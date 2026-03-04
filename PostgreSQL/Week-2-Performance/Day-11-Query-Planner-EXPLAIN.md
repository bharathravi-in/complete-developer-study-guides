# Day 11: Query Planner & EXPLAIN

## 📚 Learning Objectives
- Master EXPLAIN and EXPLAIN ANALYZE
- Understand all scan types
- Read and interpret execution plans
- Identify performance bottlenecks

---

## 1. How the Query Planner Works

### Planning Phases

```
SQL Query
    ↓
┌─────────────────┐
│    Parser       │ → Syntax check, create parse tree
├─────────────────┤
│    Analyzer     │ → Semantic check, resolve names
├─────────────────┤
│    Rewriter     │ → Apply rules (views, etc.)
├─────────────────┤
│    Planner      │ → Generate execution plans, choose best
├─────────────────┤
│    Executor     │ → Execute chosen plan
└─────────────────┘
    ↓
Result
```

### Cost-Based Optimization

```sql
-- Planner estimates costs based on:
-- 1. Table statistics (pg_statistic)
-- 2. Index availability
-- 3. Configuration parameters
-- 4. Cost constants (seq_page_cost, random_page_cost, etc.)

SHOW seq_page_cost;      -- Default: 1.0
SHOW random_page_cost;   -- Default: 4.0 (SSD: set to 1.1)
SHOW cpu_tuple_cost;     -- Default: 0.01
SHOW cpu_index_tuple_cost; -- Default: 0.005
```

---

## 2. EXPLAIN Basics

### EXPLAIN vs EXPLAIN ANALYZE

```sql
-- EXPLAIN: Shows estimated plan (doesn't run query)
EXPLAIN SELECT * FROM users WHERE id = 1;

-- EXPLAIN ANALYZE: Shows actual execution (runs query!)
EXPLAIN ANALYZE SELECT * FROM users WHERE id = 1;

-- ⚠️ Warning: EXPLAIN ANALYZE executes the query
-- Use with caution on INSERT/UPDATE/DELETE
BEGIN;
EXPLAIN ANALYZE UPDATE users SET name = 'Test' WHERE id = 1;
ROLLBACK;  -- Undo the change
```

### EXPLAIN Options

```sql
-- All options
EXPLAIN (
    ANALYZE true,        -- Run query
    VERBOSE true,        -- Show column names
    COSTS true,          -- Show costs (default)
    BUFFERS true,        -- Show buffer usage
    TIMING true,         -- Show timing (default with ANALYZE)
    FORMAT json          -- Output format: text, xml, json, yaml
)
SELECT * FROM users WHERE id = 1;

-- Common combinations
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
EXPLAIN (FORMAT json) SELECT ...;
```

---

## 3. Reading EXPLAIN Output

### Basic Structure

```
                          QUERY PLAN
─────────────────────────────────────────────────────────────────
 Seq Scan on users  (cost=0.00..35.50 rows=10 width=244)
                     └── startup..total  estimated  row size
```

### Cost Breakdown

```
cost=0.00..35.50
     │       │
     │       └── Total cost to return all rows
     └── Startup cost (before first row)

rows=10    → Estimated rows to return
width=244  → Average row size in bytes
```

### With ANALYZE

```
Seq Scan on users  (cost=0.00..35.50 rows=10 width=244)
                    (actual time=0.012..0.015 rows=10 loops=1)
                     └── startup..total  actual   iterations
```

---

## 4. Scan Types

### Sequential Scan (Seq Scan)

```sql
EXPLAIN ANALYZE SELECT * FROM users;

-- Output:
Seq Scan on users  (cost=0.00..35.50 rows=2000 width=244)
  (actual time=0.008..0.352 rows=2000 loops=1)

-- Reads entire table, row by row
-- Used when:
-- - No suitable index
-- - Table is small
-- - Query returns most rows
```

### Index Scan

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE id = 100;

-- Output:
Index Scan using users_pkey on users  (cost=0.29..8.30 rows=1 width=244)
  Index Cond: (id = 100)
  (actual time=0.015..0.016 rows=1 loops=1)

-- Reads index, then fetches rows from table
-- Used for selective queries
```

### Index Only Scan

```sql
-- Index covers all needed columns
CREATE INDEX idx_covering ON users(id, email);

EXPLAIN ANALYZE SELECT id, email FROM users WHERE id = 100;

-- Output:
Index Only Scan using idx_covering on users  (cost=0.29..4.30 rows=1 width=40)
  Index Cond: (id = 100)
  Heap Fetches: 0   ← No table access needed!
  (actual time=0.012..0.012 rows=1 loops=1)
```

### Bitmap Index Scan

```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE status = 'pending' AND total > 1000;

-- Output:
Bitmap Heap Scan on orders  (cost=8.58..32.36 rows=50 width=244)
  Recheck Cond: ((status = 'pending') AND (total > 1000))
  -> BitmapAnd
       -> Bitmap Index Scan on idx_status  (cost=0.00..4.18 rows=200 width=0)
             Index Cond: (status = 'pending')
       -> Bitmap Index Scan on idx_total  (cost=0.00..4.35 rows=150 width=0)
             Index Cond: (total > 1000)

-- Two-phase:
-- 1. Build bitmap of matching row locations
-- 2. Scan heap in physical order
-- Efficient for OR conditions and low-selectivity
```

### TID Scan

```sql
-- Direct access by row location
EXPLAIN ANALYZE SELECT * FROM users WHERE ctid = '(0,1)';

-- Output:
Tid Scan on users  (cost=0.00..4.01 rows=1 width=244)
  TID Cond: (ctid = '(0,1)'::tid)
```

---

## 5. Join Methods

### Nested Loop

```sql
EXPLAIN ANALYZE
SELECT u.*, o.total
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.id = 100;

-- Output:
Nested Loop  (cost=0.58..16.62 rows=3 width=268)
  -> Index Scan using users_pkey on users u  (cost=0.29..8.30 rows=1 width=244)
       Index Cond: (id = 100)
  -> Index Scan using idx_orders_user on orders o  (cost=0.29..8.30 rows=3 width=24)
       Index Cond: (user_id = 100)

-- For each row in outer table, scan inner table
-- Good for: small outer table, indexed inner table
```

### Hash Join

```sql
EXPLAIN ANALYZE
SELECT u.name, SUM(o.total)
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.name;

-- Output:
Hash Join  (cost=60.00..100.00 rows=1000 width=268)
  Hash Cond: (o.user_id = u.id)
  -> Seq Scan on orders o  (cost=0.00..30.00 rows=1000 width=24)
  -> Hash  (cost=35.00..35.00 rows=2000 width=244)
       -> Seq Scan on users u  (cost=0.00..35.00 rows=2000 width=244)

-- Build hash table from smaller table
-- Probe with larger table
-- Good for: larger tables, no indexes
```

### Merge Join

```sql
EXPLAIN ANALYZE
SELECT u.*, o.*
FROM users u
JOIN orders o ON u.id = o.user_id
ORDER BY u.id;

-- Output:
Merge Join  (cost=150.00..200.00 rows=1000 width=268)
  Merge Cond: (u.id = o.user_id)
  -> Index Scan using users_pkey on users u  (cost=0.29..80.00 rows=2000 width=244)
  -> Sort  (cost=70.00..72.50 rows=1000 width=24)
       Sort Key: o.user_id
       -> Seq Scan on orders o  (cost=0.00..30.00 rows=1000 width=24)

-- Both inputs must be sorted
-- Good for: already sorted data, large datasets
```

---

## 6. Other Operations

### Sort

```sql
EXPLAIN ANALYZE SELECT * FROM users ORDER BY email;

-- Output:
Sort  (cost=150.00..155.00 rows=2000 width=244)
  Sort Key: email
  Sort Method: quicksort  Memory: 256kB
  -> Seq Scan on users  (cost=0.00..35.00 rows=2000 width=244)

-- Memory sorts are fast
-- Disk sorts are slow (increase work_mem if needed)
Sort Method: external merge  Disk: 10240kB  ← Bad!
```

### Hash Aggregate

```sql
EXPLAIN ANALYZE
SELECT status, COUNT(*) FROM orders GROUP BY status;

-- Output:
HashAggregate  (cost=45.00..47.50 rows=5 width=16)
  Group Key: status
  -> Seq Scan on orders  (cost=0.00..30.00 rows=1000 width=8)
```

### Group Aggregate

```sql
-- When data is already sorted
EXPLAIN ANALYZE
SELECT user_id, COUNT(*) FROM orders GROUP BY user_id ORDER BY user_id;

-- Output:
GroupAggregate  (cost=70.00..95.00 rows=500 width=12)
  Group Key: user_id
  -> Sort  (cost=70.00..72.50 rows=1000 width=4)
```

---

## 7. BUFFERS Option

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM users WHERE id = 100;

-- Output:
Index Scan using users_pkey on users  (cost=0.29..8.30 rows=1 width=244)
  Index Cond: (id = 100)
  Buffers: shared hit=3 read=1
           │         │    │
           │         │    └── Pages read from disk
           │         └── Pages found in cache
           └── shared buffer pool

-- Ideal: All hits, no reads
-- Problem: Many reads = cold cache or large working set
```

### Buffer Types

```
shared hit    → Found in shared buffers (fast)
shared read   → Read from OS cache or disk
shared dirtied → Modified pages
shared written → Written during query
local hit/read → Temporary tables
temp read/written → Temp files (work_mem exceeded)
```

---

## 8. Common Issues & Solutions

### Issue: Seq Scan When Index Exists

```sql
-- Check if statistics are current
ANALYZE users;

-- Check if index is valid
SELECT * FROM pg_indexes WHERE tablename = 'users';

-- Force index hint (testing only!)
SET enable_seqscan = off;
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
SET enable_seqscan = on;

-- Possible causes:
-- 1. Outdated statistics (run ANALYZE)
-- 2. Low selectivity (query returns too many rows)
-- 3. Small table (seq scan is faster)
```

### Issue: Inaccurate Row Estimates

```sql
-- Bad estimate example:
Index Scan on users  (cost=0.29..8.30 rows=1 width=244)
                      (actual time=0.015..5.000 rows=10000 loops=1)
                                           └── Huge mismatch!

-- Solutions:
-- 1. Update statistics
ANALYZE users;

-- 2. Increase statistics target
ALTER TABLE users ALTER COLUMN email SET STATISTICS 1000;
ANALYZE users;

-- 3. Create extended statistics for correlated columns
CREATE STATISTICS stat_name (dependencies) ON col1, col2 FROM table;
```

### Issue: Hash/Sort to Disk

```sql
-- Memory exceeded:
Sort Method: external merge  Disk: 10240kB

-- Solutions:
SET work_mem = '256MB';  -- Increase memory
-- Or optimize query to process fewer rows
```

---

## 9. Using EXPLAIN for Optimization

### Workflow

1. **Get baseline**
   ```sql
   EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
   ```

2. **Identify bottleneck**
   - Look for highest cost nodes
   - Check actual vs estimated rows
   - Look for disk sorts/spills

3. **Try optimization**
   - Add/modify indexes
   - Rewrite query
   - Adjust parameters

4. **Verify improvement**
   ```sql
   EXPLAIN (ANALYZE, BUFFERS) SELECT ...;
   ```

### Example Optimization

```sql
-- Original query
EXPLAIN ANALYZE
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id, u.name
ORDER BY order_count DESC
LIMIT 10;

-- Analyze the plan:
-- 1. Is created_at indexed?
-- 2. Is user_id in orders indexed?
-- 3. Are row estimates accurate?

-- Add missing indexes
CREATE INDEX idx_users_created ON users(created_at);
CREATE INDEX idx_orders_user ON orders(user_id);

-- Re-run and compare
EXPLAIN ANALYZE ...;
```

---

## 10. Plan Visualization Tools

```sql
-- JSON output for tools
EXPLAIN (FORMAT json) SELECT ...;

-- Tools:
-- - explain.depesz.com (paste text output)
-- - explain.dalibo.com (paste JSON)
-- - pgAdmin built-in visualizer
-- - DataGrip explain plan
```

---

## 🔬 Hands-On Practice

```sql
-- Setup
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255),
    region VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE purchases (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    amount NUMERIC(10,2),
    purchased_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert data
INSERT INTO customers (name, email, region)
SELECT 
    'Customer ' || i,
    'customer' || i || '@example.com',
    (ARRAY['North', 'South', 'East', 'West'])[1 + (i % 4)]
FROM generate_series(1, 10000) i;

INSERT INTO purchases (customer_id, amount, purchased_at)
SELECT 
    1 + (random() * 9999)::int,
    random() * 1000,
    NOW() - (random() * 365 || ' days')::interval
FROM generate_series(1, 100000) i;

ANALYZE customers;
ANALYZE purchases;

-- Practice queries
-- 1. Compare seq scan vs index scan
EXPLAIN ANALYZE SELECT * FROM customers WHERE id = 5000;
EXPLAIN ANALYZE SELECT * FROM customers WHERE region = 'North';

-- 2. Add index and compare
CREATE INDEX idx_region ON customers(region);
EXPLAIN ANALYZE SELECT * FROM customers WHERE region = 'North';

-- 3. Analyze joins
EXPLAIN (ANALYZE, BUFFERS)
SELECT c.name, SUM(p.amount) as total
FROM customers c
JOIN purchases p ON c.id = p.customer_id
WHERE c.region = 'North'
GROUP BY c.id, c.name
ORDER BY total DESC
LIMIT 10;
```

---

## 📝 Key Takeaways

1. **EXPLAIN shows the plan, ANALYZE runs it** - Be careful with writes
2. **Compare estimated vs actual rows** - Big gaps = statistics problem
3. **Buffers show I/O patterns** - Hits = good, reads = potentially slow
4. **Seq scan isn't always bad** - Small tables, non-selective queries
5. **work_mem affects sorts** - Increase to avoid disk spills
6. **Nested loops need indexes** - On the inner table

---

## ✅ Day 11 Checklist

- [ ] Run EXPLAIN on various queries
- [ ] Understand each scan type
- [ ] Identify join methods
- [ ] Use BUFFERS to analyze I/O
- [ ] Optimize a slow query
- [ ] Practice reading complex plans
