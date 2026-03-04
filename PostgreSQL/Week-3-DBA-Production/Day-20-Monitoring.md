# Day 20: Monitoring

## 📚 Learning Objectives
- Master PostgreSQL system views (pg_stat_*)
- Use pg_stat_statements for query analysis
- Implement Prometheus/Grafana monitoring
- Create alerting rules

---

## 1. Key System Views

### Connection Monitoring

```sql
-- Active connections
SELECT 
    datname,
    usename,
    application_name,
    client_addr,
    state,
    query,
    wait_event_type,
    wait_event,
    now() - query_start AS query_duration
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- Connection counts by state
SELECT 
    state, 
    COUNT(*) 
FROM pg_stat_activity 
GROUP BY state;

-- Connections by database
SELECT 
    datname,
    COUNT(*) as connections,
    MAX(CASE WHEN state = 'active' THEN 1 ELSE 0 END) as active
FROM pg_stat_activity
GROUP BY datname;
```

### Database Statistics

```sql
-- Database-level stats
SELECT 
    datname,
    numbackends AS connections,
    xact_commit AS commits,
    xact_rollback AS rollbacks,
    blks_read,
    blks_hit,
    ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) 
        AS cache_hit_ratio,
    tup_returned,
    tup_fetched,
    tup_inserted,
    tup_updated,
    tup_deleted,
    conflicts,
    deadlocks,
    temp_files,
    temp_bytes,
    stats_reset
FROM pg_stat_database
WHERE datname = current_database();
```

### Table Statistics

```sql
-- Table I/O stats
SELECT 
    schemaname,
    relname AS table_name,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins AS inserts,
    n_tup_upd AS updates,
    n_tup_del AS deletes,
    n_live_tup AS live_rows,
    n_dead_tup AS dead_rows,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) 
        AS dead_ratio,
    last_vacuum,
    last_autovacuum,
    last_analyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;

-- Tables needing indexes (too many seq scans)
SELECT 
    relname,
    seq_scan,
    seq_tup_read,
    idx_scan,
    CASE WHEN seq_scan > 0 
         THEN seq_tup_read / seq_scan 
         ELSE 0 
    END AS avg_seq_tup
FROM pg_stat_user_tables
WHERE seq_scan > 100
ORDER BY seq_tup_read DESC;
```

### Index Statistics

```sql
-- Index usage
SELECT 
    schemaname,
    relname AS table_name,
    indexrelname AS index_name,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan;

-- Unused indexes (candidates for removal)
SELECT 
    schemaname || '.' || relname AS table,
    indexrelname AS index,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND schemaname NOT IN ('pg_catalog', 'pg_toast')
ORDER BY pg_relation_size(indexrelid) DESC;

-- Duplicate indexes
SELECT 
    a.indrelid::regclass AS table_name,
    a.indexrelid::regclass AS index1,
    b.indexrelid::regclass AS index2,
    pg_size_pretty(pg_relation_size(a.indexrelid)) AS size1
FROM pg_index a
JOIN pg_index b ON a.indrelid = b.indrelid 
    AND a.indexrelid < b.indexrelid
WHERE a.indkey = b.indkey;
```

---

## 2. pg_stat_statements

### Enable Extension

```sql
-- Add to postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all

-- Create extension
CREATE EXTENSION pg_stat_statements;
```

### Query Analysis

```sql
-- Top queries by total time
SELECT 
    LEFT(query, 80) AS query,
    calls,
    ROUND(total_exec_time::numeric, 2) AS total_time_ms,
    ROUND(mean_exec_time::numeric, 2) AS avg_time_ms,
    ROUND(min_exec_time::numeric, 2) AS min_time_ms,
    ROUND(max_exec_time::numeric, 2) AS max_time_ms,
    rows,
    ROUND(100.0 * shared_blks_hit / 
        NULLIF(shared_blks_hit + shared_blks_read, 0), 2) AS hit_ratio
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Most called queries
SELECT 
    LEFT(query, 80) AS query,
    calls,
    ROUND(mean_exec_time::numeric, 2) AS avg_time_ms
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 20;

-- Queries with most I/O
SELECT 
    LEFT(query, 80) AS query,
    calls,
    shared_blks_read + shared_blks_written AS total_io_blocks,
    ROUND(mean_exec_time::numeric, 2) AS avg_time_ms
FROM pg_stat_statements
ORDER BY (shared_blks_read + shared_blks_written) DESC
LIMIT 20;

-- Reset stats
SELECT pg_stat_statements_reset();
```

---

## 3. Lock Monitoring

```sql
-- Current locks
SELECT 
    pg_locks.pid,
    pg_stat_activity.usename,
    pg_stat_activity.query,
    pg_locks.mode,
    pg_locks.granted,
    pg_class.relname
FROM pg_locks
JOIN pg_stat_activity ON pg_locks.pid = pg_stat_activity.pid
LEFT JOIN pg_class ON pg_locks.relation = pg_class.oid
WHERE pg_stat_activity.query NOT LIKE '%pg_locks%';

-- Blocking queries
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_query,
    blocking_activity.query AS blocking_query
FROM pg_locks blocked_locks
JOIN pg_stat_activity blocked_activity ON blocked_locks.pid = blocked_activity.pid
JOIN pg_locks blocking_locks ON blocked_locks.locktype = blocking_locks.locktype
    AND blocked_locks.relation = blocking_locks.relation
    AND blocked_locks.pid != blocking_locks.pid
JOIN pg_stat_activity blocking_activity ON blocking_locks.pid = blocking_activity.pid
WHERE NOT blocked_locks.granted;
```

---

## 4. Replication Monitoring

```sql
-- Primary: Check replica status
SELECT 
    client_addr,
    application_name,
    state,
    sync_state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) / 1024 / 1024 AS lag_mb
FROM pg_stat_replication;

-- Replica: Check own lag
SELECT 
    pg_last_wal_receive_lsn() AS received_lsn,
    pg_last_wal_replay_lsn() AS replayed_lsn,
    pg_wal_lsn_diff(
        pg_last_wal_receive_lsn(), 
        pg_last_wal_replay_lsn()
    ) AS replay_lag_bytes,
    now() - pg_last_xact_replay_timestamp() AS replay_delay;

-- WAL archiving status
SELECT * FROM pg_stat_archiver;

-- Replication slots
SELECT 
    slot_name,
    slot_type,
    active,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS retained_bytes
FROM pg_replication_slots;
```

---

## 5. Prometheus/Grafana Setup

### postgres_exporter Configuration

```yaml
# docker-compose.yml
services:
  postgres_exporter:
    image: prometheuscommunity/postgres-exporter
    environment:
      DATA_SOURCE_URI: "postgres:5432/mydb?sslmode=disable"
      DATA_SOURCE_USER: "monitor"
      DATA_SOURCE_PASS: "password"
    ports:
      - "9187:9187"
```

### Key Metrics

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres_exporter:9187']

# Essential metrics to monitor:
# pg_stat_database_tup_* - Row operations
# pg_stat_database_blks_* - Block I/O
# pg_stat_database_deadlocks - Deadlock count
# pg_stat_user_tables_* - Table statistics
# pg_replication_lag - Replica delay
# pg_up - Database availability
```

### Grafana Dashboard

```sql
-- Custom queries for Grafana

-- Active connections gauge
SELECT COUNT(*) FROM pg_stat_activity WHERE state = 'active';

-- Cache hit ratio
SELECT 
    ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2)
FROM pg_stat_database 
WHERE datname = current_database();

-- Transactions per second (rate over time)
SELECT 
    xact_commit + xact_rollback AS total_xact
FROM pg_stat_database 
WHERE datname = current_database();

-- Replication lag seconds
SELECT 
    EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()));
```

---

## 6. Alerting Rules

### Prometheus Alerts

```yaml
# alerts.yml
groups:
  - name: postgresql
    rules:
      # Database down
      - alert: PostgreSQLDown
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is down"
          
      # Too many connections
      - alert: PostgreSQLHighConnections
        expr: pg_stat_database_numbackends / pg_settings_max_connections > 0.8
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL connection usage > 80%"
          
      # Replication lag
      - alert: PostgreSQLReplicationLag
        expr: pg_replication_lag > 300
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL replication lag > 5 minutes"
          
      # Low cache hit ratio
      - alert: PostgreSQLLowCacheHitRatio
        expr: pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read) < 0.95
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL cache hit ratio < 95%"
          
      # Deadlocks
      - alert: PostgreSQLDeadlocks
        expr: rate(pg_stat_database_deadlocks[5m]) > 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL deadlocks detected"
```

---

## 7. Custom Monitoring Functions

```sql
-- Create monitoring schema
CREATE SCHEMA monitoring;

-- Health check function
CREATE OR REPLACE FUNCTION monitoring.health_check()
RETURNS TABLE (
    metric TEXT,
    value TEXT,
    status TEXT
) AS $$
BEGIN
    -- Connection usage
    RETURN QUERY
    SELECT 
        'connection_usage'::TEXT,
        (100.0 * COUNT(*) / current_setting('max_connections')::int)::TEXT,
        CASE 
            WHEN 100.0 * COUNT(*) / current_setting('max_connections')::int > 80 
            THEN 'WARNING' 
            ELSE 'OK' 
        END
    FROM pg_stat_activity;
    
    -- Cache hit ratio
    RETURN QUERY
    SELECT 
        'cache_hit_ratio'::TEXT,
        ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2)::TEXT,
        CASE 
            WHEN 100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0) < 95 
            THEN 'WARNING' 
            ELSE 'OK' 
        END
    FROM pg_stat_database WHERE datname = current_database();
    
    -- Long running queries
    RETURN QUERY
    SELECT 
        'long_queries'::TEXT,
        COUNT(*)::TEXT,
        CASE WHEN COUNT(*) > 0 THEN 'WARNING' ELSE 'OK' END
    FROM pg_stat_activity
    WHERE state = 'active' 
    AND now() - query_start > INTERVAL '5 minutes';
    
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT * FROM monitoring.health_check();
```

---

## 📝 Key Takeaways

1. **pg_stat_* views are goldmine** - All runtime stats
2. **pg_stat_statements for slow queries** - Must-have extension
3. **Monitor cache hit ratio** - Should be > 95%
4. **Watch replication lag** - Critical for HA
5. **Automate alerting** - Prometheus + Grafana

---

## ✅ Day 20 Checklist

- [ ] Query pg_stat_activity for connections
- [ ] Enable and use pg_stat_statements
- [ ] Monitor table/index statistics
- [ ] Check replication lag
- [ ] Set up Prometheus exporter
- [ ] Create Grafana dashboard
- [ ] Configure alerting rules
