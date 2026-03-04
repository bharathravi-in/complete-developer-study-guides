# Day 19: Partitioning

## 📚 Learning Objectives
- Understand partitioning benefits
- Implement range, list, and hash partitioning
- Manage partitions effectively
- Optimize queries on partitioned tables

---

## 1. Why Partitioning?

### Benefits

```
Without Partitioning:
┌─────────────────────────────────────┐
│        orders (100M rows)           │
│  Scan entire table for date range   │
│  VACUUM locks entire table          │
│  Indexes become huge                │
└─────────────────────────────────────┘

With Partitioning:
┌──────────┬──────────┬──────────┬──────────┐
│ orders   │ orders   │ orders   │ orders   │
│ 2023_q1  │ 2023_q2  │ 2023_q3  │ 2023_q4  │
│ (25M)    │ (25M)    │ (25M)    │ (25M)    │
└──────────┴──────────┴──────────┴──────────┘
     ↓
Query Jan 2023? → Scan only Q1 partition!
Drop old data? → DROP PARTITION (instant!)
```

### When to Partition

| Good Use Cases | Bad Use Cases |
|----------------|---------------|
| Time-series data | Small tables |
| Multi-tenant | Random access patterns |
| Data lifecycle management | Need cross-partition queries |
| Large tables (100M+ rows) | Simple CRUD apps |

---

## 2. Range Partitioning

### Create Range Partitioned Table

```sql
-- Parent table (no data stored here)
CREATE TABLE orders (
    id BIGSERIAL,
    order_date TIMESTAMPTZ NOT NULL,
    customer_id INTEGER,
    total_amount DECIMAL(10,2),
    status VARCHAR(20)
) PARTITION BY RANGE (order_date);

-- Create partitions
CREATE TABLE orders_2023_q1 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');

CREATE TABLE orders_2023_q2 PARTITION OF orders
    FOR VALUES FROM ('2023-04-01') TO ('2023-07-01');

CREATE TABLE orders_2023_q3 PARTITION OF orders
    FOR VALUES FROM ('2023-07-01') TO ('2023-10-01');

CREATE TABLE orders_2023_q4 PARTITION OF orders
    FOR VALUES FROM ('2023-10-01') TO ('2024-01-01');

-- Default partition (catches anything that doesn't match)
CREATE TABLE orders_default PARTITION OF orders
    DEFAULT;
```

### Automatic Monthly Partitions

```sql
-- Function to create monthly partitions
CREATE OR REPLACE FUNCTION create_monthly_partition(
    parent_table TEXT,
    partition_date DATE
) RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    start_date DATE;
    end_date DATE;
BEGIN
    start_date := date_trunc('month', partition_date);
    end_date := start_date + INTERVAL '1 month';
    partition_name := parent_table || '_' || to_char(start_date, 'YYYY_MM');
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I
         FOR VALUES FROM (%L) TO (%L)',
        partition_name, parent_table, start_date, end_date
    );
END;
$$ LANGUAGE plpgsql;

-- Create next 12 months
DO $$
BEGIN
    FOR i IN 0..11 LOOP
        PERFORM create_monthly_partition(
            'orders',
            CURRENT_DATE + (i || ' months')::INTERVAL
        );
    END LOOP;
END $$;
```

---

## 3. List Partitioning

### By Category

```sql
CREATE TABLE products (
    id SERIAL,
    name VARCHAR(100),
    category VARCHAR(50) NOT NULL,
    price DECIMAL(10,2)
) PARTITION BY LIST (category);

CREATE TABLE products_electronics PARTITION OF products
    FOR VALUES IN ('electronics', 'computers', 'phones');

CREATE TABLE products_clothing PARTITION OF products
    FOR VALUES IN ('clothing', 'shoes', 'accessories');

CREATE TABLE products_other PARTITION OF products
    DEFAULT;
```

### Multi-Tenant

```sql
CREATE TABLE tenant_data (
    id SERIAL,
    tenant_id INTEGER NOT NULL,
    data JSONB
) PARTITION BY LIST (tenant_id);

-- One partition per tenant
CREATE TABLE tenant_data_1 PARTITION OF tenant_data FOR VALUES IN (1);
CREATE TABLE tenant_data_2 PARTITION OF tenant_data FOR VALUES IN (2);
CREATE TABLE tenant_data_3 PARTITION OF tenant_data FOR VALUES IN (3);
```

---

## 4. Hash Partitioning

### Even Distribution

```sql
-- Good for: Even load distribution when no natural partition key
CREATE TABLE events (
    id UUID DEFAULT gen_random_uuid(),
    event_type VARCHAR(50),
    payload JSONB,
    created_at TIMESTAMPTZ
) PARTITION BY HASH (id);

-- Create 8 partitions
CREATE TABLE events_p0 PARTITION OF events FOR VALUES WITH (MODULUS 8, REMAINDER 0);
CREATE TABLE events_p1 PARTITION OF events FOR VALUES WITH (MODULUS 8, REMAINDER 1);
CREATE TABLE events_p2 PARTITION OF events FOR VALUES WITH (MODULUS 8, REMAINDER 2);
CREATE TABLE events_p3 PARTITION OF events FOR VALUES WITH (MODULUS 8, REMAINDER 3);
CREATE TABLE events_p4 PARTITION OF events FOR VALUES WITH (MODULUS 8, REMAINDER 4);
CREATE TABLE events_p5 PARTITION OF events FOR VALUES WITH (MODULUS 8, REMAINDER 5);
CREATE TABLE events_p6 PARTITION OF events FOR VALUES WITH (MODULUS 8, REMAINDER 6);
CREATE TABLE events_p7 PARTITION OF events FOR VALUES WITH (MODULUS 8, REMAINDER 7);
```

---

## 5. Multi-Level Partitioning

```sql
-- First level: Range by date
CREATE TABLE sales (
    id BIGSERIAL,
    sale_date DATE NOT NULL,
    region VARCHAR(20) NOT NULL,
    amount DECIMAL(10,2)
) PARTITION BY RANGE (sale_date);

-- Second level: List by region
CREATE TABLE sales_2024 PARTITION OF sales
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01')
    PARTITION BY LIST (region);

CREATE TABLE sales_2024_us PARTITION OF sales_2024
    FOR VALUES IN ('US', 'CA');

CREATE TABLE sales_2024_eu PARTITION OF sales_2024
    FOR VALUES IN ('UK', 'DE', 'FR');

CREATE TABLE sales_2024_asia PARTITION OF sales_2024
    FOR VALUES IN ('JP', 'CN', 'IN');
```

---

## 6. Partition Management

### Add/Remove Partitions

```sql
-- Add new partition
CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

-- Detach partition (keeps data)
ALTER TABLE orders DETACH PARTITION orders_2023_q1;

-- Now it's a regular table - can archive, drop, etc.
-- Archive to cold storage...
DROP TABLE orders_2023_q1;

-- Reattach a table as partition
ALTER TABLE orders ATTACH PARTITION orders_2023_q1
    FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');
```

### Move Data Between Partitions

```sql
-- If data was inserted into wrong partition (or default)
-- First, create correct partition
CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- Move data from default
WITH moved AS (
    DELETE FROM orders_default
    WHERE order_date >= '2024-04-01' AND order_date < '2024-07-01'
    RETURNING *
)
INSERT INTO orders_2024_q2 SELECT * FROM moved;
```

---

## 7. Indexes on Partitioned Tables

```sql
-- Index on parent applies to all partitions
CREATE INDEX idx_orders_customer ON orders (customer_id);
-- Creates: idx_orders_2023_q1_customer, idx_orders_2023_q2_customer, etc.

-- Unique constraints require partition key
CREATE UNIQUE INDEX idx_orders_id ON orders (id, order_date);
-- id alone won't work!

-- Index on specific partition only
CREATE INDEX idx_orders_2023_q1_status 
    ON orders_2023_q1 (status);
```

### Primary Key Considerations

```sql
-- Partition key must be part of primary key
CREATE TABLE orders (
    id BIGSERIAL,
    order_date TIMESTAMPTZ NOT NULL,
    customer_id INTEGER,
    PRIMARY KEY (id, order_date)  -- Include partition key!
) PARTITION BY RANGE (order_date);
```

---

## 8. Query Optimization

### Partition Pruning

```sql
-- PostgreSQL automatically prunes partitions
EXPLAIN SELECT * FROM orders 
WHERE order_date = '2023-06-15';

--                                 QUERY PLAN
-- ---------------------------------------------------------------------------
-- Append  (cost=0.00..21.75 rows=5 width=36)
--   ->  Seq Scan on orders_2023_q2 orders_1  (cost=0.00..21.75 rows=5 width=36)
--         Filter: (order_date = '2023-06-15'::date)
-- Only scans Q2 partition!
```

### Enable Runtime Pruning

```sql
-- Enabled by default (PG11+)
SET enable_partition_pruning = on;

-- Works with parameters too
PREPARE find_orders (date) AS
    SELECT * FROM orders WHERE order_date = $1;

EXECUTE find_orders('2023-06-15');
-- Still prunes at runtime!
```

### JOINs with Partitioned Tables

```sql
-- Partition-wise joins
SET enable_partitionwise_join = on;

-- Join happens at partition level
SELECT o.*, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.order_date BETWEEN '2023-04-01' AND '2023-06-30';
```

---

## 9. Maintenance

### View Partitions

```sql
-- List all partitions
SELECT 
    parent.relname AS parent,
    child.relname AS partition,
    pg_get_expr(child.relpartbound, child.oid) AS bounds
FROM pg_inherits
JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
JOIN pg_class child ON pg_inherits.inhrelid = child.oid
WHERE parent.relname = 'orders';

-- Partition sizes
SELECT 
    child.relname AS partition,
    pg_size_pretty(pg_relation_size(child.oid)) AS size,
    pg_stat_get_live_tuples(child.oid) AS rows
FROM pg_inherits
JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
JOIN pg_class child ON pg_inherits.inhrelid = child.oid
WHERE parent.relname = 'orders';
```

### VACUUM on Partitions

```sql
-- VACUUM specific partition
VACUUM ANALYZE orders_2023_q4;

-- VACUUM all partitions
VACUUM ANALYZE orders;

-- Autovacuum works per-partition
-- Old partitions rarely vacuumed (no changes)
```

---

## 📝 Key Takeaways

1. **Range for time-series** - Natural fit for date-based data
2. **List for categories** - Good for tenants, regions
3. **Hash for even distribution** - When no natural key exists
4. **Partition key in PK** - Required for unique constraints
5. **Partition pruning is automatic** - Huge performance boost

---

## ✅ Day 19 Checklist

- [ ] Create range partitioned table
- [ ] Create list partitioned table
- [ ] Implement multi-level partitioning
- [ ] Add indexes to partitioned tables
- [ ] Practice partition management
- [ ] Verify partition pruning with EXPLAIN
