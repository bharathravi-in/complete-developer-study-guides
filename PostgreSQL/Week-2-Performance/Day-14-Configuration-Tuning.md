# Day 14: Configuration Tuning

## 📚 Learning Objectives
- Tune memory settings optimally
- Configure WAL for performance
- Optimize connection settings
- Understand checkpoint tuning
- Create configuration for different workloads

---

## 1. Configuration Overview

### Configuration Levels

```sql
-- 1. postgresql.conf (permanent, requires reload/restart)
-- 2. ALTER SYSTEM (stored in postgresql.auto.conf)
-- 3. Database level
ALTER DATABASE mydb SET work_mem = '256MB';

-- 4. User level
ALTER USER analyst SET work_mem = '512MB';

-- 5. Session level
SET work_mem = '128MB';

-- 6. Transaction level
SET LOCAL work_mem = '256MB';

-- View current value and source
SELECT name, setting, source FROM pg_settings WHERE name = 'work_mem';
```

### Apply Configuration Changes

```sql
-- Check if restart required
SELECT name, pending_restart FROM pg_settings WHERE pending_restart;

-- Reload configuration
SELECT pg_reload_conf();

-- From command line
pg_ctl reload -D /var/lib/postgresql/data

-- Some settings require restart
-- e.g., shared_buffers, max_connections
```

---

## 2. Memory Configuration

### Memory Architecture Recap

```
┌──────────────────────────────────────────────────────────┐
│                    System RAM (128 GB)                    │
├──────────────────────────────────────────────────────────┤
│  OS Cache    │ shared_buffers │ PostgreSQL Processes      │
│  (50-60%)    │   (25%)        │ (work_mem per operation)  │
│   ~70 GB     │   ~32 GB       │ ~20 GB total              │
└──────────────────────────────────────────────────────────┘
```

### shared_buffers

PostgreSQL's main buffer cache.

```sql
SHOW shared_buffers;  -- Default: 128MB

-- Recommendation:
-- Dedicated server: 25% of RAM
-- Shared server: 15% of RAM
-- Maximum useful: ~8GB (diminishing returns after)

-- postgresql.conf
shared_buffers = 32GB  -- For 128GB RAM server

-- Check buffer cache hit ratio
SELECT 
    SUM(blks_hit) * 100.0 / SUM(blks_hit + blks_read) AS hit_ratio
FROM pg_stat_database;
-- Aim for > 99%
```

### effective_cache_size

Planner's estimate of total cache (shared_buffers + OS cache).

```sql
SHOW effective_cache_size;  -- Default: 4GB

-- Set to ~75% of total RAM
effective_cache_size = 96GB  -- For 128GB RAM

-- This doesn't allocate memory!
-- Just helps planner choose index vs seq scan
```

### work_mem

Memory for sorts, hashes, etc. **Per operation!**

```sql
SHOW work_mem;  -- Default: 4MB

-- Be careful: Complex query might use multiple work_mem allocations
-- Query with 10 joins + sorts = potentially 10 × work_mem

-- Conservative formula:
-- work_mem = (RAM - shared_buffers) / (max_connections × 3)

-- For 128GB RAM, 100 connections, 32GB shared_buffers:
-- (128 - 32) / (100 × 3) = 320MB (generous)
-- Set conservatively: work_mem = 64MB

-- For analytics workloads, set higher per-session:
SET work_mem = '512MB';  -- For heavy report

-- Check if work_mem exceeded
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM large_table ORDER BY column;
-- Look for: Sort Method: external merge  Disk: 10240kB
-- This means work_mem was exceeded!
```

### maintenance_work_mem

Memory for maintenance operations (VACUUM, CREATE INDEX, etc.).

```sql
SHOW maintenance_work_mem;  -- Default: 64MB

-- Can be much higher - only one maintenance op at a time
-- Set to 1-2GB for faster maintenance
maintenance_work_mem = 2GB

-- For large table reindex or vacuum
SET maintenance_work_mem = '4GB';
VACUUM FULL large_table;
```

### temp_buffers

Memory for temporary tables per session.

```sql
SHOW temp_buffers;  -- Default: 8MB

-- Increase if using many temp tables
temp_buffers = 64MB
```

---

## 3. WAL Configuration

### wal_buffers

Buffer for WAL before writing to disk.

```sql
SHOW wal_buffers;  -- Default: -1 (auto: 3% of shared_buffers)

-- Usually auto is fine
-- For very high write workloads: 64MB-256MB
wal_buffers = 64MB
```

### min_wal_size / max_wal_size

```sql
SHOW min_wal_size;  -- Default: 80MB
SHOW max_wal_size;  -- Default: 1GB

-- For write-heavy workloads, increase:
min_wal_size = 1GB
max_wal_size = 4GB

-- Prevents excessive checkpoint frequency
```

### checkpoint_completion_target

Spread checkpoint I/O over time.

```sql
SHOW checkpoint_completion_target;  -- Default: 0.9

-- Aim to complete checkpoint in 90% of checkpoint_timeout
checkpoint_completion_target = 0.9  -- Good default
checkpoint_timeout = 15min          -- Increase from 5min
```

### synchronous_commit

Trade durability for performance.

```sql
SHOW synchronous_commit;  -- Default: on

-- Options:
-- on:           Full durability (safest)
-- remote_write: Durable on primary, written to replica
-- remote_apply: Durable and visible on replica
-- local:        Durable on primary only
-- off:          May lose up to wal_writer_delay commits

-- For non-critical logging tables:
SET LOCAL synchronous_commit = 'off';
INSERT INTO logs (...) VALUES (...);
-- Slightly faster, may lose last few ms of commits on crash
```

---

## 4. Connection Settings

### max_connections

```sql
SHOW max_connections;  -- Default: 100

-- Each connection uses ~10MB RAM
-- 100 connections = 1GB RAM just for connections

-- Use connection pooling to reduce needed connections
-- Direct connections: 100-200
-- With PgBouncer: 20-50 actual PostgreSQL connections

max_connections = 200  -- Reasonable for most apps
```

### Connection-Related Memory

```sql
-- Total memory per connection includes:
-- - Stack space (~1MB)
-- - work_mem (per operation)
-- - temp_buffers
-- - Other session state

-- Example: 200 connections, each might use:
-- 1MB (base) + 64MB (work_mem) + 8MB (temp) = 73MB potential per connection
-- Total: 200 × 73MB = 14.6GB potential (worst case)
```

---

## 5. Query Planner Settings

### random_page_cost

Cost of random I/O vs sequential.

```sql
SHOW random_page_cost;  -- Default: 4.0

-- For SSD: Lower value (random ≈ sequential)
random_page_cost = 1.1

-- For HDD: Keep default or higher
random_page_cost = 4.0
```

### cpu_tuple_cost / cpu_index_tuple_cost

```sql
SHOW cpu_tuple_cost;        -- Default: 0.01
SHOW cpu_index_tuple_cost;  -- Default: 0.005

-- Usually no need to change
```

### effective_io_concurrency

Concurrent I/O operations for bitmap heap scans.

```sql
SHOW effective_io_concurrency;  -- Default: 1

-- For SSD: Higher value (many concurrent reads)
effective_io_concurrency = 200

-- For HDD: Lower value
effective_io_concurrency = 2
```

### parallel_tuple_cost / parallel_setup_cost

Control parallel query usage.

```sql
SHOW max_parallel_workers_per_gather;  -- Default: 2
SHOW max_parallel_workers;              -- Default: 8
SHOW max_worker_processes;              -- Default: 8

-- For OLAP workloads: Increase parallelism
max_parallel_workers_per_gather = 4
max_parallel_workers = 8

-- Reduce parallel query overhead estimates for more parallel queries
parallel_tuple_cost = 0.01   -- Default: 0.1
parallel_setup_cost = 100    -- Default: 1000
```

---

## 6. Logging Configuration

### Essential Logging

```sql
-- Log slow queries
log_min_duration_statement = 1000  -- Log queries > 1 second

-- Log checkpoints (monitoring)
log_checkpoints = on

-- Log connections (security)
log_connections = on
log_disconnections = on

-- Log lock waits
log_lock_waits = on
deadlock_timeout = 1s

-- Log temporary files (work_mem issues)
log_temp_files = 0  -- Log all temp files
```

### Log Destination

```sql
-- postgresql.conf
log_destination = 'stderr'  -- Also: 'csvlog', 'syslog'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
```

---

## 7. Configuration Recipes

### OLTP (Transactional) Workload

```ini
# postgresql.conf for OLTP on 128GB RAM server

# Memory
shared_buffers = 32GB
effective_cache_size = 96GB
work_mem = 64MB
maintenance_work_mem = 2GB

# WAL
wal_buffers = 64MB
min_wal_size = 1GB
max_wal_size = 4GB
checkpoint_completion_target = 0.9
checkpoint_timeout = 15min

# Connections
max_connections = 200

# Planner (SSD)
random_page_cost = 1.1
effective_io_concurrency = 200

# Autovacuum
autovacuum_max_workers = 4
autovacuum_vacuum_cost_limit = 400
```

### OLAP (Analytical) Workload

```ini
# postgresql.conf for OLAP on 128GB RAM server

# Memory - More for complex queries
shared_buffers = 32GB
effective_cache_size = 96GB
work_mem = 512MB          # Higher for sorts/aggregates
maintenance_work_mem = 4GB
huge_pages = try

# Connections - Fewer, heavier queries
max_connections = 50

# Parallel Query
max_parallel_workers_per_gather = 8
max_parallel_workers = 16
parallel_tuple_cost = 0.01
parallel_setup_cost = 100

# Planner
random_page_cost = 1.1
effective_io_concurrency = 200
default_statistics_target = 500

# Checkpoints - Less frequent
checkpoint_timeout = 30min
max_wal_size = 8GB
```

### Mixed Workload

```ini
# Balanced configuration

shared_buffers = 32GB
effective_cache_size = 96GB
work_mem = 128MB
maintenance_work_mem = 2GB

max_connections = 150

# Moderate parallelism
max_parallel_workers_per_gather = 4
max_parallel_workers = 8

random_page_cost = 1.1
effective_io_concurrency = 200
```

---

## 8. PgTune

Use automated tuning calculators:

```bash
# Online tools
# - pgtune.leopard.in.ua
# - pgconfigurator.cybertec.at

# Provide:
# - RAM
# - CPU cores
# - Storage type (SSD/HDD)
# - Workload type (OLTP/OLAP/Web/Mixed)
# - Max connections
```

---

## 9. Monitoring Configuration Impact

```sql
-- Check buffer cache usage
SELECT 
    c.relname,
    pg_size_pretty(count(*) * 8192) AS buffered_size,
    round(100.0 * count(*) / (SELECT setting FROM pg_settings WHERE name='shared_buffers')::int, 2) AS pct_of_cache
FROM pg_buffercache b
JOIN pg_class c ON b.relfilenode = c.relfilenode
GROUP BY c.relname
ORDER BY count(*) DESC
LIMIT 20;

-- Check work_mem usage
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM large_table ORDER BY column;

-- Check checkpoint frequency
SELECT 
    checkpoints_timed,
    checkpoints_req,  -- Requested (forced) checkpoints
    checkpoint_write_time / 1000 AS write_time_sec,
    checkpoint_sync_time / 1000 AS sync_time_sec
FROM pg_stat_bgwriter;
```

---

## 📝 Key Formulas

| Setting | Formula |
|---------|---------|
| shared_buffers | 25% of RAM |
| effective_cache_size | 75% of RAM |
| work_mem | (RAM - shared_buffers) / (max_connections × 3) |
| maintenance_work_mem | 1-2 GB |
| random_page_cost | 1.1 (SSD) or 4.0 (HDD) |

---

## ✅ Day 14 Checklist

- [ ] Calculate optimal shared_buffers
- [ ] Set work_mem appropriately
- [ ] Configure for SSD (random_page_cost)
- [ ] Enable useful logging
- [ ] Test configuration changes
- [ ] Monitor impact of changes
