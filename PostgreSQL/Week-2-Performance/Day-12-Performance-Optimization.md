# Day 12: Performance Optimization

## 📚 Learning Objectives
- Query rewriting techniques
- Avoid N+1 problem
- Index selection strategy
- Pagination optimization
- Connection pooling concepts

---

## 1. Query Rewriting Techniques

### Use EXISTS Instead of COUNT

```sql
-- ❌ Slow: Counts all matching rows
SELECT * FROM customers c
WHERE (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.id) > 0;

-- ✅ Fast: Stops at first match
SELECT * FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```

### Use IN Wisely

```sql
-- ❌ Slow for large lists
SELECT * FROM products WHERE id IN (1, 2, 3, ... 10000);

-- ✅ Better: Use ANY with array
SELECT * FROM products WHERE id = ANY(ARRAY[1, 2, 3, ...]);

-- ✅ Best: Join with VALUES or temp table
SELECT p.* FROM products p
JOIN (VALUES (1), (2), (3)) AS v(id) ON p.id = v.id;
```

### Avoid Functions on Indexed Columns

```sql
-- ❌ Index on created_at NOT used
SELECT * FROM orders WHERE DATE(created_at) = '2024-01-15';

-- ✅ Index IS used
SELECT * FROM orders 
WHERE created_at >= '2024-01-15' AND created_at < '2024-01-16';

-- ❌ Index on email NOT used
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

-- ✅ Create expression index or use CITEXT type
CREATE INDEX idx_email_lower ON users(LOWER(email));
```

### Use UNION ALL Instead of UNION

```sql
-- ❌ UNION removes duplicates (expensive sort)
SELECT id FROM table_a
UNION
SELECT id FROM table_b;

-- ✅ UNION ALL if duplicates OK or impossible
SELECT id FROM table_a
UNION ALL
SELECT id FROM table_b;
```

### Optimize Subqueries

```sql
-- ❌ Correlated subquery (executes per row)
SELECT *,
    (SELECT MAX(amount) FROM orders WHERE orders.customer_id = customers.id)
FROM customers;

-- ✅ Rewrite as JOIN
SELECT c.*, o.max_amount
FROM customers c
LEFT JOIN (
    SELECT customer_id, MAX(amount) AS max_amount
    FROM orders
    GROUP BY customer_id
) o ON c.id = o.customer_id;
```

---

## 2. The N+1 Problem

### What is N+1?

```
┌─────────────────────────────────────────────┐
│ Query 1: SELECT * FROM customers LIMIT 10;  │  1 query
├─────────────────────────────────────────────┤
│ Query 2: SELECT * FROM orders WHERE cust=1; │  ╮
│ Query 3: SELECT * FROM orders WHERE cust=2; │  │
│ Query 4: SELECT * FROM orders WHERE cust=3; │  │ N queries
│ ...                                         │  │
│ Query 11: SELECT * FROM orders WHERE cust=10│  ╯
└─────────────────────────────────────────────┘
Total: 11 queries for 10 customers!
```

### Solutions

```sql
-- Solution 1: JOIN
SELECT c.*, o.id as order_id, o.total
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE c.id <= 10;

-- Solution 2: Batch loading (for ORMs)
-- First query: get customer IDs
SELECT id FROM customers LIMIT 10;  -- Returns [1,2,3..10]

-- Second query: get all orders at once
SELECT * FROM orders WHERE customer_id = ANY(ARRAY[1,2,3,4,5,6,7,8,9,10]);

-- Solution 3: Array aggregation
SELECT 
    c.*,
    ARRAY_AGG(JSONB_BUILD_OBJECT('id', o.id, 'total', o.total)) AS orders
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id;
```

### ORM Patterns

```python
# Django: Use select_related / prefetch_related
customers = Customer.objects.prefetch_related('orders').all()[:10]

# SQLAlchemy: Use joinedload / subqueryload
customers = session.query(Customer)\
    .options(joinedload(Customer.orders))\
    .limit(10).all()
```

---

## 3. Index Selection Strategy

### Decision Tree

```
                    ┌─────────────────┐
                    │  Your Query     │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
      ┌─────────┐      ┌──────────┐     ┌─────────┐
      │Equality │      │  Range   │     │  Text   │
      │  (=)    │      │ (<,>,BW) │     │ Search  │
      └────┬────┘      └────┬─────┘     └────┬────┘
           │                │                 │
      ┌────┴────┐     ┌────┴────┐       ┌────┴────┐
      │ B-Tree  │     │ B-Tree  │       │  GIN +  │
      │ or Hash │     │         │       │ pg_trgm │
      └─────────┘     └─────────┘       └─────────┘
```

### Index Selection Rules

```sql
-- Rule 1: Index columns in WHERE clauses
SELECT * FROM orders WHERE customer_id = 1;
-- Need: idx_orders_customer_id

-- Rule 2: Index columns in JOIN conditions
SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id;
-- Need: idx_orders_customer_id

-- Rule 3: Index columns in ORDER BY (if no WHERE)
SELECT * FROM orders ORDER BY created_at DESC LIMIT 10;
-- Need: idx_orders_created_at_desc

-- Rule 4: Consider covering indexes
CREATE INDEX idx_orders_covering ON orders(customer_id) 
INCLUDE (total, status);

-- Rule 5: Partial indexes for filtered queries
CREATE INDEX idx_active_orders ON orders(created_at) 
WHERE status = 'active';
```

### Composite Index Guidelines

```sql
-- Put equality columns before range columns
-- Query: WHERE status = 'active' AND created_at > '2024-01-01'
CREATE INDEX idx_composite ON orders(status, created_at);

-- Put high-cardinality columns first for index-only scans
CREATE INDEX idx_user_status ON users(user_id, status);

-- Match index order to common sort orders
CREATE INDEX idx_orders_desc ON orders(customer_id, created_at DESC);
```

---

## 4. Pagination Optimization

### Offset Pagination (Simple but Slow)

```sql
-- Page 1
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 0;

-- Page 100
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 1980;
-- ⚠️ Must scan 2000 rows!
```

### Keyset Pagination (Cursor-Based)

```sql
-- Page 1
SELECT * FROM products ORDER BY id LIMIT 20;
-- Last id was 20

-- Page 2 (using cursor)
SELECT * FROM products WHERE id > 20 ORDER BY id LIMIT 20;
-- Uses index efficiently!

-- For multiple sort columns
SELECT * FROM products 
WHERE (created_at, id) > ('2024-01-15', 100)
ORDER BY created_at, id
LIMIT 20;
```

### Implementing Cursor Pagination

```sql
-- Create cursor token (encode last row values)
-- Token: base64(json({"created_at": "2024-01-15", "id": 100}))

-- Next page query
SELECT * FROM products 
WHERE (created_at, id) > ($1, $2)  -- Decode from cursor
ORDER BY created_at, id
LIMIT $3;

-- Previous page query
SELECT * FROM (
    SELECT * FROM products 
    WHERE (created_at, id) < ($1, $2)
    ORDER BY created_at DESC, id DESC
    LIMIT $3
) sub
ORDER BY created_at, id;
```

### Window Function Pagination

```sql
-- Get page with total count
SELECT *,
    COUNT(*) OVER() AS total_count
FROM products
WHERE category = 'Electronics'
ORDER BY id
LIMIT 20 OFFSET 0;
```

---

## 5. Connection Pooling

### Why Pool Connections?

```
Without pooling:
┌─────────┐     ┌─────────────┐
│ Request │────→│ New Conn    │ (expensive!)
└─────────┘     │ to Postgres │
                └─────────────┘

With pooling:
┌─────────┐     ┌──────────┐     ┌─────────────┐
│ Request │────→│ Get Conn │────→│ Reuse Conn  │
└─────────┘     │ from Pool│     │ to Postgres │
                └──────────┘     └─────────────┘
```

### Connection Cost

- Fork process: ~100ms
- Memory: ~10MB per connection
- File descriptors
- Lock contention

### PgBouncer Configuration

```ini
; pgbouncer.ini
[databases]
mydb = host=localhost dbname=mydb

[pgbouncer]
listen_addr = *
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
min_pool_size = 5
reserve_pool_size = 5
```

### Pool Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| Session | Connection per session | Legacy apps |
| Transaction | Connection per transaction | Most apps |
| Statement | Connection per statement | Read-heavy, simple queries |

---

## 6. Query Optimization Patterns

### Batch Operations

```sql
-- ❌ Single inserts
INSERT INTO logs (message) VALUES ('log1');
INSERT INTO logs (message) VALUES ('log2');
INSERT INTO logs (message) VALUES ('log3');

-- ✅ Batch insert
INSERT INTO logs (message) VALUES
    ('log1'),
    ('log2'),
    ('log3');

-- ✅ COPY for bulk loading
COPY logs(message) FROM '/path/to/data.csv' CSV;
```

### Conditional Updates

```sql
-- ❌ Multiple UPDATE statements
UPDATE products SET price = price * 1.1 WHERE category = 'A';
UPDATE products SET price = price * 1.2 WHERE category = 'B';

-- ✅ Single UPDATE with CASE
UPDATE products SET price = price * CASE 
    WHEN category = 'A' THEN 1.1
    WHEN category = 'B' THEN 1.2
    ELSE 1.0
END;
```

### Materialized Views for Reports

```sql
-- Create materialized view
CREATE MATERIALIZED VIEW monthly_sales AS
SELECT 
    DATE_TRUNC('month', order_date) AS month,
    category,
    SUM(total) AS revenue,
    COUNT(*) AS order_count
FROM orders
JOIN order_items USING (order_id)
GROUP BY 1, 2;

CREATE UNIQUE INDEX ON monthly_sales (month, category);

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales;
```

---

## 7. Common Anti-Patterns

### SELECT *

```sql
-- ❌ Fetches unnecessary columns
SELECT * FROM users;

-- ✅ Fetch only needed columns
SELECT id, name, email FROM users;
```

### OR in WHERE

```sql
-- ❌ May not use indexes well
SELECT * FROM orders WHERE customer_id = 1 OR status = 'pending';

-- ✅ Use UNION ALL
SELECT * FROM orders WHERE customer_id = 1
UNION ALL
SELECT * FROM orders WHERE status = 'pending' AND customer_id != 1;
```

### != or NOT IN

```sql
-- ❌ Often can't use indexes
SELECT * FROM products WHERE category != 'Electronics';

-- ✅ If few values, list them
SELECT * FROM products WHERE category IN ('Books', 'Clothing', 'Home');
```

### LIKE with Leading Wildcard

```sql
-- ❌ Can't use regular B-tree index
SELECT * FROM products WHERE name LIKE '%widget%';

-- ✅ Use trigram index
CREATE EXTENSION pg_trgm;
CREATE INDEX idx_name_trgm ON products USING GIN (name gin_trgm_ops);
```

---

## 🔬 Performance Audit Checklist

```sql
-- 1. Check for missing indexes
SELECT 
    relname AS table,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch
FROM pg_stat_user_tables
WHERE seq_scan > idx_scan
AND seq_tup_read > 10000
ORDER BY seq_tup_read DESC;

-- 2. Check for unused indexes
SELECT 
    schemaname || '.' || relname AS table,
    indexrelname AS index,
    idx_scan AS times_used,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan < 10
ORDER BY pg_relation_size(indexrelid) DESC;

-- 3. Check table bloat
SELECT 
    schemaname || '.' || relname AS table,
    n_live_tup,
    n_dead_tup,
    ROUND(100 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

---

## 📝 Key Takeaways

1. **Rewrite correlated subqueries** - JOINs are usually faster
2. **Solve N+1 with batch loading** - One query is better than N
3. **Use keyset pagination** - Offset is O(N), cursor is O(1)
4. **Index strategically** - Not too many, not too few
5. **Pool connections** - Reduce connection overhead
6. **Batch operations** - Bulk inserts/updates are faster

---

## ✅ Day 12 Checklist

- [ ] Identify and fix N+1 queries
- [ ] Implement keyset pagination
- [ ] Audit existing indexes
- [ ] Optimize slow queries
- [ ] Understand connection pooling
- [ ] Remove unnecessary SELECT *
