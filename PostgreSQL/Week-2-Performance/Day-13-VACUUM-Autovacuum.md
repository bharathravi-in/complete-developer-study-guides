# Day 13: VACUUM & Autovacuum

## 📚 Learning Objectives
- Understand why VACUUM is necessary
- Learn about table bloat
- Master VACUUM, ANALYZE, FREEZE
- Configure autovacuum optimally

---

## 1. Why VACUUM?

### MVCC Creates Dead Rows

```
Transaction 100: INSERT INTO t VALUES (1, 'Alice');
│
├─ Row: xmin=100, xmax=NULL, data='Alice' (LIVE)
│
Transaction 105: UPDATE t SET data='Bob' WHERE id=1;
│
├─ Row: xmin=100, xmax=105, data='Alice' (DEAD)
├─ Row: xmin=105, xmax=NULL, data='Bob'  (LIVE)
│
Transaction 110: DELETE FROM t WHERE id=1;
│
├─ Row: xmin=100, xmax=105, data='Alice' (DEAD)
├─ Row: xmin=105, xmax=110, data='Bob'  (DEAD)
│
└─ Without VACUUM, dead rows accumulate forever!
```

### VACUUM Functions

1. **Reclaim space** from dead rows
2. **Update visibility map** for index-only scans
3. **Update free space map** for new inserts
4. **Prevent transaction ID wraparound**

---

## 2. Table Bloat

### What is Bloat?

```
Live rows:     ████████████░░░░░░░░░░░░  40%
Dead rows:     ░░░░░░░░░░░░████████████  40%
Free space:    ░░░░░░░░░░░░░░░░░░░░████  20%
              |-------- Table Size --------|

Table is 100GB but only 40GB is live data = 60% bloated!
```

### Detecting Bloat

```sql
-- Quick check: Dead tuple ratio
SELECT 
    schemaname || '.' || relname AS table,
    n_live_tup,
    n_dead_tup,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;

-- More accurate: Size vs estimated live data
SELECT 
    schemaname || '.' || relname AS table,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    pg_size_pretty(pg_relation_size(relid)) AS table_size,
    n_live_tup,
    CASE WHEN n_live_tup > 0 
        THEN pg_size_pretty((pg_relation_size(relid) / n_live_tup)::bigint)
        ELSE 'N/A' 
    END AS avg_row_size
FROM pg_stat_user_tables
WHERE n_live_tup > 1000
ORDER BY pg_total_relation_size(relid) DESC;

-- Use pgstattuple for accurate measurement
CREATE EXTENSION pgstattuple;

SELECT * FROM pgstattuple('large_table');
-- tuple_percent: % of space used by tuples
-- dead_tuple_percent: % of space used by dead tuples
-- free_percent: % of free space
```

---

## 3. VACUUM Types

### Regular VACUUM

```sql
-- Vacuum specific table
VACUUM users;

-- Vacuum with verbose output
VACUUM VERBOSE users;

-- Vacuum entire database
VACUUM;

-- Vacuum and analyze (update statistics)
VACUUM ANALYZE users;
```

Effects:
- Marks dead rows as reusable
- **Does NOT return space to OS**
- Non-blocking (can run with queries)

### VACUUM FULL

```sql
-- Rewrites entire table
VACUUM FULL users;

-- ⚠️ Requires ACCESS EXCLUSIVE lock!
-- ⚠️ Doubles space needed temporarily
-- ⚠️ Very slow on large tables
```

Effects:
- Rewrites table without dead rows
- **Returns space to OS**
- Blocks all access to table

### When to Use What?

| Scenario | Action |
|----------|--------|
| Regular maintenance | VACUUM (automatic) |
| After bulk DELETE | VACUUM ANALYZE |
| Severe bloat (>50%) | VACUUM FULL (downtime) |
| Prevent that bloat | pg_repack (online) |

---

## 4. ANALYZE

Updates statistics for query planner.

```sql
-- Analyze single table
ANALYZE users;

-- Analyze specific columns
ANALYZE users (email, status);

-- Analyze entire database
ANALYZE;

-- Verbose output
ANALYZE VERBOSE users;
```

### Statistics Target

```sql
-- Default statistics samples
SHOW default_statistics_target;  -- Default: 100

-- Increase for columns with many distinct values
ALTER TABLE users ALTER COLUMN email SET STATISTICS 500;

-- For columns with skewed data
ALTER TABLE orders ALTER COLUMN status SET STATISTICS 1000;

-- After changing, re-analyze
ANALYZE users;

-- View current statistics
SELECT 
    attname,
    n_distinct,
    most_common_vals,
    most_common_freqs
FROM pg_stats
WHERE tablename = 'users' AND attname = 'status';
```

---

## 5. FREEZE

Prevents Transaction ID Wraparound.

### The Wraparound Problem

```
Transaction IDs are 32-bit (4 billion values)
After ~2 billion transactions, old XIDs appear "in the future"

XID:    0 ... 1B ... 2B ... 3B ... 4B (wraps to 0)
        ^                   ^
     current            "future" (can't see!)

Solution: FREEZE marks rows as "visible to all transactions"
```

### How FREEZE Works

```sql
-- Manual freeze
VACUUM FREEZE users;

-- Check freeze progress
SELECT 
    relname,
    age(relfrozenxid) AS xid_age,
    pg_size_pretty(pg_relation_size(oid)) AS size
FROM pg_class
WHERE relkind = 'r'
ORDER BY age(relfrozenxid) DESC;

-- Warning thresholds
SHOW vacuum_freeze_min_age;      -- 50M: min age before freeze
SHOW vacuum_freeze_table_age;    -- 150M: trigger aggressive vacuum
SHOW autovacuum_freeze_max_age;  -- 200M: FORCE vacuum
```

### Wraparound Warning Signs

```sql
-- Monitor XID age
SELECT 
    datname,
    age(datfrozenxid) AS db_age,
    current_setting('autovacuum_freeze_max_age')::int AS max_age,
    ROUND(100.0 * age(datfrozenxid) / 
        current_setting('autovacuum_freeze_max_age')::int, 2) AS pct_towards_wraparound
FROM pg_database
ORDER BY age(datfrozenxid) DESC;

-- Emergency: Getting close to wraparound
-- System will STOP all transactions to protect itself!
-- You'll see: "database is not accepting commands to avoid wraparound"
```

---

## 6. Autovacuum Configuration

### Default Settings

```sql
-- View current settings
SHOW autovacuum;                           -- on
SHOW autovacuum_vacuum_threshold;          -- 50 rows
SHOW autovacuum_vacuum_scale_factor;       -- 0.2 (20%)
SHOW autovacuum_analyze_threshold;         -- 50 rows
SHOW autovacuum_analyze_scale_factor;      -- 0.1 (10%)
SHOW autovacuum_max_workers;               -- 3 workers
SHOW autovacuum_naptime;                   -- 1min between checks
```

### When Does Autovacuum Run?

```
VACUUM triggered when:
  dead_tuples > vacuum_threshold + (vacuum_scale_factor × table_rows)
  
Example: 1M row table, default settings
  Trigger at: 50 + (0.2 × 1,000,000) = 200,050 dead rows

ANALYZE triggered when:
  changed_tuples > analyze_threshold + (analyze_scale_factor × table_rows)
```

### Tuning Autovacuum

```sql
-- For large tables: Lower scale factor
ALTER TABLE large_table SET (
    autovacuum_vacuum_scale_factor = 0.01,   -- 1% instead of 20%
    autovacuum_vacuum_threshold = 1000,
    autovacuum_analyze_scale_factor = 0.005,
    autovacuum_analyze_threshold = 1000
);

-- For high-write tables: More aggressive
ALTER TABLE hot_table SET (
    autovacuum_vacuum_cost_limit = 1000,     -- Less throttling
    autovacuum_vacuum_cost_delay = 10        -- Faster
);

-- Global tuning (postgresql.conf)
autovacuum_vacuum_cost_delay = 2     -- ms, default 2
autovacuum_vacuum_cost_limit = 200   -- default 200
autovacuum_max_workers = 5           -- default 3
```

### Monitoring Autovacuum

```sql
-- Current autovacuum activity
SELECT 
    pid,
    datname,
    relid::regclass AS table,
    phase,
    heap_blks_total,
    heap_blks_scanned,
    heap_blks_vacuumed,
    index_vacuum_count
FROM pg_stat_progress_vacuum;

-- Last vacuum times
SELECT 
    schemaname || '.' || relname AS table,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count
FROM pg_stat_user_tables
ORDER BY last_autovacuum DESC NULLS LAST;

-- Tables never vacuumed
SELECT schemaname || '.' || relname AS table
FROM pg_stat_user_tables
WHERE last_vacuum IS NULL AND last_autovacuum IS NULL;
```

---

## 7. Manual VACUUM Strategy

### Daily Operations

```sql
-- Analyze updated tables
ANALYZE users;
ANALYZE orders;

-- Check for bloated tables
SELECT 
    relname,
    n_dead_tup,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;
```

### After Bulk Operations

```sql
-- After bulk DELETE
DELETE FROM logs WHERE created_at < NOW() - INTERVAL '90 days';
VACUUM ANALYZE logs;

-- After bulk UPDATE
UPDATE products SET price = price * 1.1;
VACUUM ANALYZE products;

-- After TRUNCATE (no vacuum needed)
TRUNCATE TABLE temp_data;  -- Already reclaims space
```

### Dealing with Bloat

```sql
-- Option 1: VACUUM FULL (blocking)
BEGIN;
-- Acquire lock during off-hours
VACUUM FULL bloated_table;
COMMIT;

-- Option 2: pg_repack (non-blocking)
-- Install extension first
CREATE EXTENSION pg_repack;

-- From command line:
-- pg_repack -d mydb -t bloated_table

-- Option 3: Create new table and swap
CREATE TABLE new_table (LIKE old_table INCLUDING ALL);
INSERT INTO new_table SELECT * FROM old_table;
BEGIN;
DROP TABLE old_table;
ALTER TABLE new_table RENAME TO old_table;
COMMIT;
```

---

## 8. Troubleshooting

### Autovacuum Not Running

```sql
-- Check if enabled
SHOW autovacuum;

-- Check if blocked
SELECT * FROM pg_stat_activity 
WHERE query LIKE '%autovacuum%';

-- Check for long-running transactions blocking vacuum
SELECT 
    pid,
    now() - xact_start AS age,
    query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_start;

-- Kill blocking transaction if needed
SELECT pg_terminate_backend(pid);
```

### Autovacuum Taking Too Long

```sql
-- Check vacuum progress
SELECT * FROM pg_stat_progress_vacuum;

-- Increase resources
ALTER SYSTEM SET autovacuum_vacuum_cost_limit = 400;
ALTER SYSTEM SET autovacuum_vacuum_cost_delay = 1;
SELECT pg_reload_conf();
```

---

## 📝 Key Takeaways

1. **VACUUM is essential** - MVCC creates dead rows
2. **Autovacuum usually sufficient** - But tune for large tables
3. **VACUUM FULL is expensive** - Use pg_repack instead
4. **FREEZE prevents wraparound** - Monitor XID age
5. **ANALYZE keeps stats fresh** - Critical for query planning
6. **Monitor bloat regularly** - Catch issues early

---

## ✅ Day 13 Checklist

- [ ] Check bloat levels in tables
- [ ] Monitor autovacuum activity
- [ ] Tune autovacuum for large tables
- [ ] Understand XID wraparound
- [ ] Practice manual VACUUM operations
- [ ] Know when to use VACUUM FULL
