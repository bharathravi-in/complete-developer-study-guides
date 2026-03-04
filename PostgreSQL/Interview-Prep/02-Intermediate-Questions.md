# PostgreSQL Interview Questions: Intermediate Level

## 1. Transactions & ACID

### Q1: Explain ACID properties
**Answer:**

| Property | Description | PostgreSQL Implementation |
|----------|-------------|--------------------------|
| **Atomicity** | All or nothing | Transaction log (WAL) |
| **Consistency** | Valid state transitions | Constraints, triggers |
| **Isolation** | Concurrent transactions isolated | MVCC |
| **Durability** | Committed data persists | WAL + fsync |

```sql
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;  -- Both succeed or both fail (Atomicity)
```

---

### Q2: What is MVCC?
**Answer:** Multi-Version Concurrency Control allows concurrent reads without blocking writes.

**How it works:**
```
Every row has hidden columns:
- xmin: Transaction ID that created the row
- xmax: Transaction ID that deleted/updated the row

When you UPDATE:
1. Old row marked dead (xmax set)
2. New row created (new xmin)

Readers see snapshot:
- Rows where xmin committed before snapshot
- Rows where xmax not set or not committed
```

**Benefits:**
- Readers don't block writers
- Writers don't block readers
- No read locks needed

**Downside:**
- Dead tuples accumulate (need VACUUM)

---

### Q3: Explain isolation levels in PostgreSQL
**Answer:**

```sql
-- Read Committed (default)
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- Each statement sees latest committed data
-- Same query might return different results

-- Repeatable Read
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- Sees snapshot from transaction start
-- Serialization error on write conflicts

-- Serializable
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- Full isolation, as if sequential execution
-- Most serialization errors
```

**Phenomena:**

| Level | Dirty Read | Non-Repeatable Read | Phantom Read | Serialization Anomaly |
|-------|------------|---------------------|--------------|----------------------|
| Read Committed | No | Yes | Yes | Yes |
| Repeatable Read | No | No | No | Yes |
| Serializable | No | No | No | No |

---

### Q4: What are savepoints?
**Answer:** Savepoints allow partial rollback within a transaction.

```sql
BEGIN;
    INSERT INTO orders (id, total) VALUES (1, 100);
    SAVEPOINT sp1;
    
    INSERT INTO order_items (order_id, product_id) VALUES (1, 999);
    -- Error: product doesn't exist
    
    ROLLBACK TO sp1;  -- Undo only to savepoint
    
    INSERT INTO order_items (order_id, product_id) VALUES (1, 1);
    
COMMIT;  -- Order with valid item committed
```

---

## 2. Performance & Optimization

### Q5: How do you optimize a slow query?
**Answer:**

**Step 1: Analyze with EXPLAIN**
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) 
SELECT * FROM orders WHERE user_id = 123;
```

**Step 2: Look for problems**
- `Seq Scan` on large table → Need index
- High `actual rows` vs `estimated` → Statistics outdated
- `Sort` or `Hash` with disk → Increase work_mem
- Nested Loop with many iterations → Consider JOIN rewrite

**Step 3: Solutions**
```sql
-- Add index
CREATE INDEX idx_orders_user ON orders(user_id);

-- Update statistics
ANALYZE orders;

-- Rewrite query
-- Bad: Function in WHERE
WHERE EXTRACT(YEAR FROM created_at) = 2024
-- Good: Range comparison
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01'
```

---

### Q6: Explain different index types
**Answer:**

| Index Type | Best For | Example |
|------------|----------|---------|
| B-tree | Equality, Range, Sorting | `WHERE id = 1`, `ORDER BY name` |
| Hash | Equality only | `WHERE hash_col = 'value'` |
| GIN | Arrays, JSONB, Full-text | `WHERE tags @> '{sql}'` |
| GiST | Geometric, Range, Full-text | `WHERE point <@ box` |
| BRIN | Large sorted tables (time-series) | `WHERE timestamp > '2024-01-01'` |

```sql
-- B-tree (default)
CREATE INDEX idx_users_email ON users(email);

-- GIN for JSONB
CREATE INDEX idx_products_attrs ON products USING GIN(attributes);

-- GiST for full-text
CREATE INDEX idx_articles_fts ON articles USING GiST(search_vector);

-- BRIN for time-series (very compact)
CREATE INDEX idx_events_time ON events USING BRIN(created_at);
```

---

### Q7: What is a partial index?
**Answer:** An index on a subset of rows, filtered by a WHERE clause.

```sql
-- Only index active users (smaller, faster)
CREATE INDEX idx_active_users ON users(email) WHERE is_active = true;

-- Query uses partial index
SELECT * FROM users WHERE email = 'test@example.com' AND is_active = true;

-- Only index non-null values
CREATE INDEX idx_users_phone ON users(phone) WHERE phone IS NOT NULL;
```

**Benefits:**
- Smaller index size
- Faster updates
- Better cache utilization

---

### Q8: What is an expression index?
**Answer:** An index on the result of an expression or function.

```sql
-- Index on lowercase email
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- Query uses expression index
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

-- Index on JSONB path
CREATE INDEX idx_products_brand ON products((attributes->>'brand'));

SELECT * FROM products WHERE attributes->>'brand' = 'Apple';

-- Index on date part
CREATE INDEX idx_orders_year ON orders(EXTRACT(YEAR FROM created_at));
```

---

### Q9: Explain query planner statistics
**Answer:**

```sql
-- View table statistics
SELECT 
    relname,
    reltuples AS estimated_rows,
    relpages AS pages
FROM pg_class 
WHERE relname = 'users';

-- View column statistics
SELECT 
    attname,
    null_frac,
    n_distinct,
    most_common_vals,
    histogram_bounds
FROM pg_stats 
WHERE tablename = 'users';

-- Update statistics
ANALYZE users;

-- More detailed statistics
ALTER TABLE users ALTER COLUMN status SET STATISTICS 1000;
ANALYZE users;
```

**Why statistics matter:**
- Planner estimates row counts
- Chooses between Seq Scan vs Index Scan
- Decides JOIN order and method
- Bad estimates → Bad plans

---

## 3. Locking & Concurrency

### Q10: Explain lock types in PostgreSQL
**Answer:**

**Row-Level Locks:**
```sql
-- FOR UPDATE: Exclusive, blocks other FOR UPDATE
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;

-- FOR SHARE: Shared, allows other FOR SHARE
SELECT * FROM accounts WHERE id = 1 FOR SHARE;

-- FOR NO KEY UPDATE: Like FOR UPDATE but allows foreign key checks
SELECT * FROM accounts WHERE id = 1 FOR NO KEY UPDATE;

-- SKIP LOCKED: Skip locked rows (for job queues)
SELECT * FROM jobs WHERE status = 'pending' 
FOR UPDATE SKIP LOCKED LIMIT 1;
```

**Table-Level Locks:**

| Lock Mode | Conflicts With |
|-----------|----------------|
| ACCESS SHARE | ACCESS EXCLUSIVE |
| ROW SHARE | EXCLUSIVE, ACCESS EXCLUSIVE |
| ROW EXCLUSIVE | SHARE, SHARE ROW EXCLUSIVE, EXCLUSIVE, ACCESS EXCLUSIVE |
| ACCESS EXCLUSIVE | Everything |

---

### Q11: How do you detect and resolve deadlocks?
**Answer:**

**Detection:**
```sql
-- View current locks
SELECT 
    pg_locks.pid,
    pg_stat_activity.query,
    pg_locks.mode,
    pg_locks.granted
FROM pg_locks
JOIN pg_stat_activity ON pg_locks.pid = pg_stat_activity.pid
WHERE NOT pg_locks.granted;

-- View blocking queries
SELECT 
    blocked.pid AS blocked_pid,
    blocked.query AS blocked_query,
    blocking.pid AS blocking_pid,
    blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks blocked_locks ON blocked.pid = blocked_locks.pid
JOIN pg_locks blocking_locks ON blocked_locks.locktype = blocking_locks.locktype
    AND blocked_locks.relation = blocking_locks.relation
    AND blocked_locks.pid != blocking_locks.pid
JOIN pg_stat_activity blocking ON blocking_locks.pid = blocking.pid
WHERE NOT blocked_locks.granted;
```

**Prevention:**
```sql
-- Lock timeout
SET lock_timeout = '5s';

-- Statement timeout
SET statement_timeout = '30s';

-- Consistent lock ordering
-- Always lock tables/rows in same order

-- Use NOWAIT
SELECT * FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;
-- Fails immediately if locked
```

---

### Q12: What are advisory locks?
**Answer:** Application-level locks not tied to database objects.

```sql
-- Session-level lock
SELECT pg_advisory_lock(12345);  -- Acquire
-- ... do work ...
SELECT pg_advisory_unlock(12345);  -- Release

-- Transaction-level lock (auto-released on commit)
SELECT pg_advisory_xact_lock(12345);

-- Try without waiting
SELECT pg_try_advisory_lock(12345);  -- Returns true/false

-- Two-key lock (e.g., for resource type + ID)
SELECT pg_advisory_lock(1, 42);  -- Lock type 1, resource 42
```

**Use cases:**
- Prevent duplicate job execution
- Coordinate external processes
- Rate limiting

---

## 4. VACUUM & Maintenance

### Q13: What is VACUUM and why is it needed?
**Answer:**

**Why needed:**
1. **Dead tuples** from UPDATE/DELETE accumulate
2. **Transaction ID wraparound** prevention (XID is 32-bit)
3. **Statistics** update for query planner

**Types:**
```sql
-- Regular VACUUM: Marks space reusable, doesn't shrink
VACUUM users;

-- VACUUM FULL: Reclaims space, rewrites table (locks!)
VACUUM FULL users;

-- VACUUM ANALYZE: Also updates statistics
VACUUM ANALYZE users;

-- VACUUM VERBOSE: Show progress
VACUUM VERBOSE users;
```

**XID Wraparound:**
```
Transaction IDs: 32-bit counter (wraps at ~2 billion)
Without VACUUM FREEZE:
- Old committed transactions appear "in the future"
- Data seems to disappear!

autovacuum_freeze_max_age = 200000000 (default)
```

---

### Q14: How do you tune autovacuum?
**Answer:**

```sql
-- Global settings (postgresql.conf)
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 1min

-- Thresholds
autovacuum_vacuum_threshold = 50       -- Min dead tuples
autovacuum_vacuum_scale_factor = 0.2   -- 20% of table

-- Triggers when: dead_tuples > threshold + scale_factor * table_size

-- Per-table tuning (for hot tables)
ALTER TABLE events SET (
    autovacuum_vacuum_threshold = 1000,
    autovacuum_vacuum_scale_factor = 0.01
);

-- Monitor autovacuum
SELECT 
    relname,
    n_dead_tup,
    last_vacuum,
    last_autovacuum,
    autovacuum_count
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

---

### Q15: What is table bloat and how do you fix it?
**Answer:**

**Causes:**
- High UPDATE/DELETE activity
- Long-running transactions holding back VACUUM
- Autovacuum not keeping up

**Detection:**
```sql
-- Check dead tuple ratio
SELECT 
    relname,
    n_live_tup,
    n_dead_tup,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
ORDER BY dead_pct DESC;

-- Estimate bloat with pgstattuple
CREATE EXTENSION pgstattuple;
SELECT * FROM pgstattuple('users');
```

**Solutions:**
```sql
-- VACUUM FULL (locks table - offline)
VACUUM FULL users;

-- pg_repack (online rebuild)
pg_repack -t users mydb

-- CLUSTER on index (locks table)
CLUSTER users USING idx_users_pkey;
```

---

## 5. Replication

### Q16: Explain streaming replication
**Answer:**

```
Primary                          Replica
┌─────────┐   WAL Stream   ┌─────────┐
│   PG    │───────────────▶│   PG    │
│ (R/W)   │                │  (R/O)  │
└─────────┘                └─────────┘

1. Primary writes to WAL
2. WAL sender process streams to replica
3. Replica applies WAL records
```

**Setup Primary:**
```sql
-- postgresql.conf
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10

-- pg_hba.conf
host replication replicator replica_ip/32 scram-sha-256
```

**Setup Replica:**
```bash
pg_basebackup -h primary -U replicator -D /data -Fp -Xs -P
```

**Check Status:**
```sql
-- On primary
SELECT * FROM pg_stat_replication;

-- On replica
SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();
```

---

### Q17: What is the difference between physical and logical replication?
**Answer:**

| Feature | Physical (Streaming) | Logical |
|---------|---------------------|---------|
| Data | Byte-level WAL | Row-level changes |
| Version | Same major version | Cross-version OK |
| Granularity | Entire cluster | Per-table |
| Replica writes | Read-only | Can write |
| Indexes | Replicated | Built locally |
| Use case | HA, read scaling | Migration, ETL |

```sql
-- Logical replication setup
-- Publisher
CREATE PUBLICATION my_pub FOR TABLE users, orders;

-- Subscriber
CREATE SUBSCRIPTION my_sub
CONNECTION 'host=primary dbname=mydb'
PUBLICATION my_pub;
```

---

### Q18: What is synchronous replication?
**Answer:** Primary waits for replica acknowledgment before committing.

```sql
-- postgresql.conf on primary
synchronous_standby_names = 'FIRST 1 (replica1, replica2)'

-- Modes:
synchronous_commit = off        -- No wait (fastest, risk of data loss)
synchronous_commit = local      -- Wait for local WAL (default)
synchronous_commit = remote_write  -- Wait for replica to receive
synchronous_commit = on         -- Wait for replica to flush
synchronous_commit = remote_apply  -- Wait for replica to apply

-- Per-transaction override
SET LOCAL synchronous_commit = off;
INSERT INTO logs (...);  -- Performance over durability
```

**Trade-off:** Zero data loss vs. latency

---

## 6. JSON/JSONB

### Q19: Explain JSON vs JSONB
**Answer:**

| Feature | JSON | JSONB |
|---------|------|-------|
| Storage | Text | Binary |
| Parsing | Every read | Once on insert |
| Duplicate keys | Preserved | Last value wins |
| Key order | Preserved | Not preserved |
| Indexing | Limited | Full GIN support |
| Speed | Write faster | Read faster |

```sql
-- Always prefer JSONB
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    data JSONB
);

-- Operators
SELECT data->'name' FROM events;       -- Returns JSON
SELECT data->>'name' FROM events;      -- Returns text
SELECT data @> '{"type":"click"}';     -- Contains
SELECT data ? 'name';                  -- Key exists

-- Indexing
CREATE INDEX idx_events_data ON events USING GIN(data);
```

---

### Q20: How do you query nested JSONB?
**Answer:**

```sql
-- Sample data
INSERT INTO products (data) VALUES ('{
    "name": "Laptop",
    "specs": {
        "cpu": "i7",
        "ram": {"size": 16, "type": "DDR4"}
    },
    "tags": ["electronics", "computers"]
}');

-- Nested access
SELECT data->'specs'->'ram'->>'size' FROM products;
SELECT data #>> '{specs,ram,type}' FROM products;

-- Array access
SELECT data->'tags'->0 FROM products;  -- "electronics"

-- Query nested values
SELECT * FROM products 
WHERE data->'specs'->'ram'->>'type' = 'DDR4';

-- Containment (uses GIN index)
SELECT * FROM products 
WHERE data @> '{"specs": {"cpu": "i7"}}';

-- Array contains
SELECT * FROM products 
WHERE data->'tags' ? 'electronics';
```

---

## 7. Window Functions

### Q21: Explain window functions
**Answer:**

```sql
-- ROW_NUMBER: Unique row number
SELECT 
    name,
    department,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS rank
FROM employees;

-- RANK / DENSE_RANK: With ties
SELECT 
    name,
    salary,
    RANK() OVER (ORDER BY salary DESC) AS rank,        -- 1,2,2,4
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense  -- 1,2,2,3
FROM employees;

-- Partition by department
SELECT 
    name,
    department,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS dept_rank
FROM employees;

-- LAG/LEAD: Previous/next row
SELECT 
    date,
    revenue,
    LAG(revenue) OVER (ORDER BY date) AS prev_revenue,
    revenue - LAG(revenue) OVER (ORDER BY date) AS change
FROM daily_sales;

-- Running total
SELECT 
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) AS running_total
FROM transactions;
```

---

### Q22: What is a window frame?
**Answer:**

```sql
-- Default: RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW

-- Custom frames
SELECT 
    date,
    value,
    -- Last 7 days average
    AVG(value) OVER (
        ORDER BY date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d,
    
    -- Previous 3 + current + next 3
    AVG(value) OVER (
        ORDER BY date
        ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING
    ) AS centered_avg
FROM metrics;

-- Frame types:
-- ROWS: Physical rows
-- RANGE: Logical range of values
-- GROUPS: Groups of peers (same ORDER BY value)
```

---

## Practice Scenarios

### Scenario 1: Fix slow dashboard query
```sql
-- Problem query
SELECT 
    u.name,
    COUNT(o.id) AS order_count,
    SUM(o.total) AS total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.created_at > '2024-01-01'
GROUP BY u.id
ORDER BY total_spent DESC;

-- Analysis: EXPLAIN shows Seq Scan on orders

-- Solution 1: Add index
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at);

-- Solution 2: Partial index if mostly querying recent
CREATE INDEX idx_orders_recent ON orders(user_id, created_at) 
WHERE created_at > '2024-01-01';
```

### Scenario 2: Implement pagination efficiently
```sql
-- Bad: OFFSET (scans and discards rows)
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 10000;

-- Good: Keyset pagination
SELECT * FROM products 
WHERE id > 10000  -- Last seen ID
ORDER BY id 
LIMIT 20;

-- For complex sorting
SELECT * FROM products 
WHERE (created_at, id) > ('2024-01-15', 1000)
ORDER BY created_at, id
LIMIT 20;
```

### Scenario 3: Handle race condition
```sql
-- Problem: Two users claim same coupon
UPDATE coupons SET claimed_by = 123 WHERE id = 1 AND claimed_by IS NULL;

-- Solution: SELECT FOR UPDATE
BEGIN;
SELECT * FROM coupons WHERE id = 1 AND claimed_by IS NULL FOR UPDATE;
-- Check if row returned
UPDATE coupons SET claimed_by = 123 WHERE id = 1;
COMMIT;

-- Or: Check affected rows
UPDATE coupons SET claimed_by = 123 WHERE id = 1 AND claimed_by IS NULL;
-- If 0 rows affected, coupon was taken
```
