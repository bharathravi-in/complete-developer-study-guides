# Day 28: PostgreSQL System Design Patterns

## 📚 Learning Objectives
- Design database schemas for common systems
- Apply PostgreSQL-specific patterns
- Handle scale and performance challenges
- Make architectural tradeoffs

---

## 1. E-Commerce Platform

### Schema Design

```sql
-- Core entities
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE products (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL,
    inventory_count INTEGER DEFAULT 0,
    category_id INTEGER REFERENCES categories(id),
    attributes JSONB DEFAULT '{}',
    search_vector TSVECTOR,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Orders (partitioned by date)
CREATE TABLE orders (
    id UUID DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending',
    total_amount NUMERIC(12, 2) NOT NULL,
    shipping_address JSONB,
    ordered_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (id, ordered_at)
) PARTITION BY RANGE (ordered_at);

-- Create monthly partitions
CREATE TABLE orders_y2024m01 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE order_items (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    order_id UUID NOT NULL,
    order_date TIMESTAMPTZ NOT NULL,
    product_id UUID NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10, 2) NOT NULL,
    FOREIGN KEY (order_id, order_date) REFERENCES orders(id, ordered_at)
);
```

### Inventory Management (Atomic Updates)

```sql
-- Reserve inventory (prevents overselling)
WITH reserved AS (
    UPDATE products
    SET inventory_count = inventory_count - $2
    WHERE id = $1 
    AND inventory_count >= $2  -- Check availability
    RETURNING id
)
INSERT INTO reservations (product_id, quantity, expires_at)
SELECT id, $2, now() + INTERVAL '15 minutes'
FROM reserved
RETURNING id;

-- If no rows returned, product unavailable

-- Release expired reservations (scheduled job)
WITH released AS (
    DELETE FROM reservations
    WHERE expires_at < now()
    RETURNING product_id, quantity
)
UPDATE products p
SET inventory_count = p.inventory_count + r.quantity
FROM released r
WHERE p.id = r.product_id;
```

### Product Search

```sql
-- Full-text search with facets
WITH matched_products AS (
    SELECT 
        p.*,
        ts_rank(search_vector, query) AS rank
    FROM products p,
         websearch_to_tsquery('english', $1) AS query
    WHERE search_vector @@ query
    AND is_active = true
    AND ($2::int IS NULL OR category_id = $2)
    AND price BETWEEN $3 AND $4
),
facets AS (
    SELECT 
        c.name AS category,
        COUNT(*) AS count
    FROM matched_products mp
    JOIN categories c ON mp.category_id = c.id
    GROUP BY c.name
)
SELECT 
    (SELECT json_agg(row_to_json(facets)) FROM facets) AS facets,
    (SELECT json_agg(row_to_json(mp)) 
     FROM (SELECT * FROM matched_products ORDER BY rank DESC LIMIT 20) mp
    ) AS products;
```

---

## 2. Social Media Feed

### Schema

```sql
CREATE TABLE posts (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    content TEXT,
    media_urls TEXT[],
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE follows (
    follower_id UUID REFERENCES users(id),
    followed_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (follower_id, followed_id)
);

CREATE INDEX idx_follows_followed ON follows(followed_id);

-- Materialized feed (fan-out on write)
CREATE TABLE feed_items (
    user_id UUID NOT NULL,
    post_id BIGINT NOT NULL REFERENCES posts(id),
    created_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (user_id, post_id)
);

CREATE INDEX idx_feed_user_time ON feed_items(user_id, created_at DESC);
```

### Fan-Out on Write

```sql
-- When user posts, add to all followers' feeds
CREATE OR REPLACE FUNCTION fan_out_post()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO feed_items (user_id, post_id, created_at)
    SELECT follower_id, NEW.id, NEW.created_at
    FROM follows
    WHERE followed_id = NEW.user_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_post_insert
    AFTER INSERT ON posts
    FOR EACH ROW
    EXECUTE FUNCTION fan_out_post();
```

### Fan-Out on Read (for celebrities)

```sql
-- Hybrid approach: Fan-out on write for regular users
-- Fan-out on read for high-follower users

CREATE OR REPLACE FUNCTION get_feed(p_user_id UUID, p_limit INT DEFAULT 20)
RETURNS TABLE (post_id BIGINT, created_at TIMESTAMPTZ) AS $$
BEGIN
    RETURN QUERY
    -- Pre-computed feed items
    SELECT fi.post_id, fi.created_at
    FROM feed_items fi
    WHERE fi.user_id = p_user_id
    
    UNION
    
    -- Celebrity posts (fan-out on read)
    SELECT p.id, p.created_at
    FROM posts p
    JOIN follows f ON p.user_id = f.followed_id
    JOIN users u ON p.user_id = u.id
    WHERE f.follower_id = p_user_id
    AND u.follower_count > 10000  -- Celebrity threshold
    
    ORDER BY created_at DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
```

---

## 3. Real-Time Analytics

### Time-Series Schema

```sql
-- Raw events (append-only)
CREATE TABLE events (
    id BIGSERIAL,
    event_type VARCHAR(50) NOT NULL,
    properties JSONB,
    user_id UUID,
    session_id UUID,
    occurred_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);

-- BRIN index for time-series (very compact)
CREATE INDEX idx_events_time ON events USING BRIN (occurred_at);

-- Aggregate tables (materialized hourly/daily)
CREATE TABLE event_stats_hourly (
    hour TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    count BIGINT,
    unique_users BIGINT,
    properties_agg JSONB,
    PRIMARY KEY (hour, event_type)
);
```

### Continuous Aggregation

```sql
-- Materialized view for real-time stats
CREATE MATERIALIZED VIEW event_stats_live AS
SELECT 
    date_trunc('hour', occurred_at) AS hour,
    event_type,
    COUNT(*) AS count,
    COUNT(DISTINCT user_id) AS unique_users
FROM events
WHERE occurred_at >= now() - INTERVAL '24 hours'
GROUP BY 1, 2;

CREATE UNIQUE INDEX ON event_stats_live (hour, event_type);

-- Refresh periodically
CREATE OR REPLACE PROCEDURE refresh_event_stats()
LANGUAGE plpgsql AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY event_stats_live;
END;
$$;

-- Schedule with pg_cron
SELECT cron.schedule('refresh-stats', '*/5 * * * *', 
    'CALL refresh_event_stats()');
```

### Approximate Counts with HyperLogLog

```sql
CREATE EXTENSION hll;

CREATE TABLE daily_uniques (
    day DATE PRIMARY KEY,
    users HLL
);

-- Add user to HyperLogLog
INSERT INTO daily_uniques (day, users)
VALUES (CURRENT_DATE, hll_add(hll_empty(), hll_hash_text($1)))
ON CONFLICT (day) DO UPDATE
SET users = hll_union(daily_uniques.users, EXCLUDED.users);

-- Get approximate unique count
SELECT hll_cardinality(users) AS unique_users
FROM daily_uniques
WHERE day = CURRENT_DATE;

-- Union across days
SELECT hll_cardinality(hll_union_agg(users)) AS weekly_uniques
FROM daily_uniques
WHERE day >= CURRENT_DATE - 7;
```

---

## 4. Multi-Tenant SaaS

### Schema Isolation Patterns

```sql
-- Option 1: Shared table with tenant_id
CREATE TABLE customers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(200),
    email VARCHAR(255),
    UNIQUE (tenant_id, email)
);

CREATE INDEX idx_customers_tenant ON customers(tenant_id);

-- Row-Level Security
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON customers
    USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- Set tenant context
SET app.tenant_id = '123e4567-e89b-12d3-a456-426614174000';
SELECT * FROM customers;  -- Only sees tenant's data
```

```sql
-- Option 2: Schema per tenant
CREATE SCHEMA tenant_abc123;

CREATE TABLE tenant_abc123.customers (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(200),
    email VARCHAR(255) UNIQUE
);

-- Set search_path per tenant
SET search_path = tenant_abc123, public;
SELECT * FROM customers;  -- Uses tenant's schema
```

### Tenant Data Isolation Comparison

| Approach | Isolation | Complexity | Scale | Backup |
|----------|-----------|------------|-------|--------|
| Shared + RLS | Logical | Low | High | Complex |
| Schema per tenant | Strong | Medium | Medium | Per-schema |
| Database per tenant | Strongest | High | Low | Simple |

---

## 5. Event Sourcing

### Event Store

```sql
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    aggregate_type VARCHAR(50) NOT NULL,
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    version INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (aggregate_type, aggregate_id, version)
);

CREATE INDEX idx_events_aggregate 
    ON events(aggregate_type, aggregate_id, version);

-- Append event (optimistic locking)
INSERT INTO events (aggregate_type, aggregate_id, event_type, event_data, version)
VALUES ($1, $2, $3, $4, 
    (SELECT COALESCE(MAX(version), 0) + 1 
     FROM events 
     WHERE aggregate_type = $1 AND aggregate_id = $2)
);
-- Fails on concurrent modification (UNIQUE violation)
```

### Projections

```sql
-- Order projection (materialized view from events)
CREATE TABLE order_projections (
    id UUID PRIMARY KEY,
    user_id UUID,
    status VARCHAR(20),
    total_amount NUMERIC(12, 2),
    item_count INTEGER,
    updated_at TIMESTAMPTZ
);

-- Update projection on new events
CREATE OR REPLACE FUNCTION update_order_projection()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.aggregate_type = 'Order' THEN
        INSERT INTO order_projections (id, user_id, status, total_amount, item_count, updated_at)
        VALUES (
            NEW.aggregate_id,
            (NEW.event_data->>'user_id')::uuid,
            NEW.event_data->>'status',
            (NEW.event_data->>'total')::numeric,
            (NEW.event_data->>'item_count')::int,
            NEW.created_at
        )
        ON CONFLICT (id) DO UPDATE SET
            status = COALESCE(EXCLUDED.status, order_projections.status),
            total_amount = COALESCE(EXCLUDED.total_amount, order_projections.total_amount),
            item_count = COALESCE(EXCLUDED.item_count, order_projections.item_count),
            updated_at = EXCLUDED.updated_at;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

## 6. Job Queue (SKIP LOCKED)

```sql
CREATE TABLE job_queue (
    id BIGSERIAL PRIMARY KEY,
    job_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    scheduled_at TIMESTAMPTZ DEFAULT now(),
    locked_at TIMESTAMPTZ,
    locked_by VARCHAR(100),
    completed_at TIMESTAMPTZ,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_jobs_pending ON job_queue(priority DESC, scheduled_at)
    WHERE status = 'pending';

-- Acquire job (concurrent-safe)
WITH acquired AS (
    SELECT id FROM job_queue
    WHERE status = 'pending'
    AND scheduled_at <= now()
    ORDER BY priority DESC, scheduled_at
    LIMIT 1
    FOR UPDATE SKIP LOCKED
)
UPDATE job_queue
SET status = 'processing',
    locked_at = now(),
    locked_by = $1,
    attempts = attempts + 1
WHERE id = (SELECT id FROM acquired)
RETURNING *;

-- Complete job
UPDATE job_queue
SET status = 'completed', completed_at = now()
WHERE id = $1;

-- Fail job (retry or permanent failure)
UPDATE job_queue
SET 
    status = CASE 
        WHEN attempts >= max_attempts THEN 'failed'
        ELSE 'pending'
    END,
    error = $2,
    locked_at = NULL,
    locked_by = NULL,
    scheduled_at = CASE
        WHEN attempts < max_attempts 
        THEN now() + (INTERVAL '1 minute' * attempts)  -- Exponential backoff
        ELSE scheduled_at
    END
WHERE id = $1;
```

---

## 📝 Key Takeaways

1. **Partition time-series data** - Essential for scale
2. **JSONB for flexible schemas** - Product attributes, event data
3. **RLS for multi-tenancy** - Database-enforced isolation
4. **SKIP LOCKED for queues** - Concurrent-safe job processing
5. **Materialized views for analytics** - Pre-computed aggregates

---

## ✅ Day 28 Checklist

- [ ] Design e-commerce schema with partitioning
- [ ] Implement feed with fan-out patterns
- [ ] Create time-series analytics tables
- [ ] Set up multi-tenant RLS
- [ ] Build event sourcing store
- [ ] Implement job queue with SKIP LOCKED
