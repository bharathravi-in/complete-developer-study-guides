# Day 10: Indexing Deep Dive

## 📚 Learning Objectives
- Understand all PostgreSQL index types
- Master B-Tree, GIN, GiST, BRIN indexes
- Learn partial and expression indexes
- Choose the right index for each scenario

---

## 1. Index Fundamentals

### What is an Index?

An index is a data structure that improves query speed by providing quick lookups.

```
Without Index: Full table scan O(n)
┌───────────────────────────────────┐
│ Scan every row to find matches   │
└───────────────────────────────────┘

With B-Tree Index: O(log n)
            [50]
           /    \
        [25]    [75]
        /  \    /  \
      [10][30][60][90]
```

### Creating Indexes

```sql
-- Basic index
CREATE INDEX idx_users_email ON users(email);

-- Unique index
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- Multi-column index
CREATE INDEX idx_orders_cust_date ON orders(customer_id, order_date);

-- Index with specific opclass
CREATE INDEX idx_name_pattern ON users(name varchar_pattern_ops);

-- Index on tablespace
CREATE INDEX idx_large ON large_table(col) TABLESPACE fast_ssd;
```

### Index Maintenance

```sql
-- View indexes
\di                          -- In psql
SELECT * FROM pg_indexes WHERE tablename = 'users';

-- Index size
SELECT pg_size_pretty(pg_relation_size('idx_users_email'));

-- Rebuild index
REINDEX INDEX idx_users_email;
REINDEX TABLE users;
REINDEX DATABASE mydb;

-- Drop index
DROP INDEX idx_users_email;
DROP INDEX CONCURRENTLY idx_users_email;  -- Non-blocking
```

---

## 2. B-Tree Index (Default)

### When to Use
- Equality comparisons (=)
- Range queries (<, >, <=, >=, BETWEEN)
- Sorting (ORDER BY)
- NULL checks (IS NULL, IS NOT NULL)
- LIKE with prefix pattern ('abc%')

### Examples

```sql
-- Default creates B-Tree
CREATE INDEX idx_salary ON employees(salary);

-- These queries use the index:
SELECT * FROM employees WHERE salary = 50000;
SELECT * FROM employees WHERE salary > 50000;
SELECT * FROM employees WHERE salary BETWEEN 40000 AND 60000;
SELECT * FROM employees ORDER BY salary;
SELECT * FROM employees WHERE salary IS NOT NULL;
```

### Multi-Column B-Tree

```sql
-- Index on (a, b, c)
CREATE INDEX idx_abc ON t(a, b, c);

-- Uses index:
WHERE a = 1
WHERE a = 1 AND b = 2
WHERE a = 1 AND b = 2 AND c = 3
WHERE a = 1 AND b > 2

-- Does NOT use index efficiently:
WHERE b = 2               -- Missing leftmost column
WHERE a = 1 AND c = 3     -- Gap in columns
WHERE b = 2 AND c = 3     -- Missing leftmost column
```

### Index-Only Scans

```sql
-- Index contains all needed columns
CREATE INDEX idx_covering ON orders(customer_id, order_date, total);

-- This can be index-only (no table access needed):
SELECT order_date, total 
FROM orders 
WHERE customer_id = 1;

-- INCLUDE for non-searchable columns (PG 11+)
CREATE INDEX idx_customer ON orders(customer_id) 
INCLUDE (order_date, total);
```

---

## 3. Hash Index

### When to Use
- Only equality comparisons (=)
- Not useful for range queries
- Smaller than B-Tree for equality-only workloads
- Now WAL-logged (safe since PostgreSQL 10)

```sql
CREATE INDEX idx_hash_email ON users USING HASH (email);

-- Uses hash index:
SELECT * FROM users WHERE email = 'test@example.com';

-- Does NOT use hash index:
SELECT * FROM users WHERE email LIKE 'test%';
SELECT * FROM users WHERE email > 'a';
```

---

## 4. GIN Index (Generalized Inverted Index)

### When to Use
- Full-text search
- JSONB containment (@>, ?, ?|, ?&)
- Array containment (@>, &&, <@)
- Trigram similarity (pg_trgm)

### Array Operations

```sql
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    tags TEXT[]
);

CREATE INDEX idx_posts_tags ON posts USING GIN (tags);

-- Uses GIN index:
SELECT * FROM posts WHERE tags @> ARRAY['postgresql'];  -- Contains
SELECT * FROM posts WHERE tags && ARRAY['sql', 'nosql']; -- Overlaps
SELECT * FROM posts WHERE 'database' = ANY(tags);        -- Has element
```

### JSONB Operations

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    data JSONB
);

-- Index entire JSONB
CREATE INDEX idx_products_data ON products USING GIN (data);

-- Uses index:
SELECT * FROM products WHERE data @> '{"brand": "Apple"}';
SELECT * FROM products WHERE data ? 'price';
SELECT * FROM products WHERE data ?| ARRAY['color', 'size'];

-- Index specific path (smaller, faster)
CREATE INDEX idx_products_brand ON products USING GIN ((data->'brand'));
```

### Full-Text Search

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    title TEXT,
    body TEXT,
    tsv TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('english', title || ' ' || body)
    ) STORED
);

CREATE INDEX idx_articles_tsv ON articles USING GIN (tsv);

-- Full-text search:
SELECT * FROM articles 
WHERE tsv @@ to_tsquery('english', 'postgresql & performance');
```

### Trigram for LIKE/ILIKE

```sql
CREATE EXTENSION pg_trgm;

CREATE INDEX idx_name_trgm ON users USING GIN (name gin_trgm_ops);

-- Now LIKE/ILIKE can use index:
SELECT * FROM users WHERE name LIKE '%john%';
SELECT * FROM users WHERE name ILIKE '%SMITH%';
```

---

## 5. GiST Index (Generalized Search Tree)

### When to Use
- Geometric data (PostGIS)
- Range types
- Full-text search (alternative to GIN)
- Nearest-neighbor searches

### Range Types

```sql
CREATE TABLE reservations (
    id SERIAL PRIMARY KEY,
    room_id INT,
    during DATERANGE
);

CREATE INDEX idx_reservations_during ON reservations USING GIST (during);

-- Uses GiST:
SELECT * FROM reservations WHERE during && '[2024-01-01, 2024-01-15)';

-- Exclude constraint (prevent overlaps)
ALTER TABLE reservations ADD CONSTRAINT no_overlap
EXCLUDE USING GIST (room_id WITH =, during WITH &&);
```

### Geometric Data

```sql
CREATE EXTENSION postgis;

CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    geom GEOMETRY(Point, 4326)
);

CREATE INDEX idx_locations_geom ON locations USING GIST (geom);

-- Spatial queries:
SELECT * FROM locations 
WHERE ST_DWithin(geom, ST_MakePoint(-122.4, 37.8)::geography, 1000);
```

### KNN (K-Nearest Neighbors)

```sql
-- Find 10 nearest neighbors
SELECT * FROM locations
ORDER BY geom <-> ST_MakePoint(-122.4, 37.8)
LIMIT 10;
```

---

## 6. BRIN Index (Block Range Index)

### When to Use
- Very large tables
- Naturally ordered data (time-series, incrementing IDs)
- Much smaller than B-Tree
- Good for range queries on physical order

```sql
-- Perfect for time-series data
CREATE TABLE sensor_data (
    id BIGSERIAL,
    sensor_id INT,
    reading NUMERIC,
    recorded_at TIMESTAMPTZ DEFAULT NOW()
);

-- BRIN index (very small!)
CREATE INDEX idx_sensor_time ON sensor_data USING BRIN (recorded_at);

-- Uses BRIN:
SELECT * FROM sensor_data 
WHERE recorded_at BETWEEN '2024-01-01' AND '2024-01-02';
```

### BRIN vs B-Tree Size

```sql
-- Compare sizes on 100M row table
-- B-Tree:  ~2 GB
-- BRIN:    ~100 KB

-- Check actual sizes
SELECT 
    indexrelname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE relname = 'sensor_data';
```

### BRIN Parameters

```sql
-- pages_per_range: How many pages per BRIN entry
-- Smaller = more accurate but larger index
CREATE INDEX idx_brin ON large_table USING BRIN (col)
WITH (pages_per_range = 32);  -- Default: 128
```

---

## 7. Partial Index

Index only a subset of rows.

```sql
-- Only index active users
CREATE INDEX idx_active_users ON users(email) 
WHERE status = 'active';

-- Query must match WHERE clause to use index:
SELECT * FROM users WHERE email = 'test@example.com' AND status = 'active';

-- Partial unique constraint
CREATE UNIQUE INDEX idx_unique_active_email ON users(email)
WHERE status = 'active';
-- Allows duplicate emails for inactive users
```

### Use Cases

```sql
-- Index only recent orders
CREATE INDEX idx_recent_orders ON orders(customer_id)
WHERE order_date > '2024-01-01';

-- Index only non-null values
CREATE INDEX idx_phone ON users(phone) WHERE phone IS NOT NULL;

-- Index only specific status
CREATE INDEX idx_pending_orders ON orders(created_at)
WHERE status = 'pending';
```

---

## 8. Expression Index

Index on computed values.

```sql
-- Case-insensitive search
CREATE INDEX idx_email_lower ON users(LOWER(email));

-- Query must use same expression:
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

-- Date extraction
CREATE INDEX idx_order_year ON orders(EXTRACT(YEAR FROM order_date));

-- Query:
SELECT * FROM orders WHERE EXTRACT(YEAR FROM order_date) = 2024;

-- JSON field
CREATE INDEX idx_data_name ON products((data->>'name'));

-- Query:
SELECT * FROM products WHERE data->>'name' = 'Widget';
```

---

## 9. Index Selection Strategy

### Guidelines

| Query Pattern | Index Type |
|--------------|------------|
| Equality (=) | B-Tree or Hash |
| Range (<, >, BETWEEN) | B-Tree |
| Sorting (ORDER BY) | B-Tree |
| Pattern (LIKE 'abc%') | B-Tree with opclass |
| Pattern (LIKE '%abc%') | GIN + pg_trgm |
| JSONB containment | GIN |
| Array operations | GIN |
| Full-text search | GIN (faster) or GiST (smaller) |
| Spatial data | GiST |
| Time-series (ordered) | BRIN |
| Range overlap | GiST |

### Multi-Column Index Order

```sql
-- Put high-cardinality columns first
-- Put equality conditions before ranges

-- For: WHERE status = 'active' AND created_at > '2024-01-01'
CREATE INDEX idx_status_date ON orders(status, created_at);

-- For: WHERE customer_id = 1 ORDER BY created_at DESC
CREATE INDEX idx_cust_date ON orders(customer_id, created_at DESC);
```

---

## 10. Index Monitoring

```sql
-- Index usage statistics
SELECT 
    relname AS table_name,
    indexrelname AS index_name,
    idx_scan AS times_used,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
ORDER BY idx_scan;

-- Find unused indexes
SELECT 
    schemaname || '.' || relname AS table,
    indexrelname AS index,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size,
    idx_scan AS scans
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Index bloat estimation
SELECT 
    current_database(), 
    schemaname, 
    tablename, 
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    ROUND(100 * pg_relation_size(indexrelid) / 
        NULLIF(pg_relation_size(relid), 0)) AS index_ratio
FROM pg_stat_user_indexes;
```

---

## 11. CREATE INDEX CONCURRENTLY

```sql
-- Normal CREATE INDEX locks the table for writes
CREATE INDEX idx_slow ON large_table(column);  -- Blocks inserts/updates

-- CONCURRENTLY doesn't block (but slower to build)
CREATE INDEX CONCURRENTLY idx_fast ON large_table(column);

-- Important notes:
-- 1. Cannot run in a transaction
-- 2. Takes longer to build
-- 3. May fail and leave invalid index
-- 4. Check for invalid indexes:

SELECT * FROM pg_indexes 
WHERE indexdef LIKE '%INVALID%';

-- Drop invalid index and retry
DROP INDEX CONCURRENTLY idx_failed;
CREATE INDEX CONCURRENTLY idx_retry ON t(col);
```

---

## 🔬 Practical Exercises

```sql
-- Setup
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    category VARCHAR(100),
    price NUMERIC(10,2),
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert test data
INSERT INTO products (name, category, price, tags, metadata)
SELECT 
    'Product ' || i,
    (ARRAY['Electronics', 'Books', 'Clothing', 'Home'])[1 + (i % 4)],
    random() * 1000,
    ARRAY['tag' || (i % 10), 'tag' || ((i + 5) % 10)],
    jsonb_build_object('brand', 'Brand' || (i % 50), 'rating', random() * 5)
FROM generate_series(1, 100000) i;

-- Analyze the table
ANALYZE products;

-- Create and test indexes
CREATE INDEX idx_category ON products(category);
CREATE INDEX idx_tags ON products USING GIN(tags);
CREATE INDEX idx_metadata ON products USING GIN(metadata);
CREATE INDEX idx_price ON products(price) WHERE price > 500;

-- Test queries with EXPLAIN
EXPLAIN ANALYZE SELECT * FROM products WHERE category = 'Books';
EXPLAIN ANALYZE SELECT * FROM products WHERE tags @> ARRAY['tag5'];
EXPLAIN ANALYZE SELECT * FROM products WHERE metadata @> '{"brand": "Brand10"}';
EXPLAIN ANALYZE SELECT * FROM products WHERE price > 500 ORDER BY price LIMIT 10;
```

---

## 📝 Key Takeaways

1. **B-Tree is the default** - Works for most cases
2. **GIN for containment** - Arrays, JSONB, full-text
3. **GiST for geometry** - Spatial and range types
4. **BRIN for ordered data** - Time-series, very large tables
5. **Partial indexes save space** - Index only what you query
6. **Expression indexes for functions** - Match query exactly
7. **Use CONCURRENTLY in production** - Avoid blocking

---

## ✅ Day 10 Checklist

- [ ] Create B-Tree indexes (single and multi-column)
- [ ] Try GIN indexes with JSONB
- [ ] Test BRIN on time-series data
- [ ] Use partial indexes effectively
- [ ] Analyze index usage statistics
- [ ] Practice CREATE INDEX CONCURRENTLY
