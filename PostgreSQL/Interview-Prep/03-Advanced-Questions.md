# PostgreSQL Interview Questions: Advanced Level

## 1. Internals & Architecture

### Q1: Explain PostgreSQL's process architecture
**Answer:**

```
                          ┌─────────────────────────────┐
                          │        Postmaster           │
                          │   (Parent process, PID 1)   │
                          └──────────────┬──────────────┘
                                         │
        ┌────────────────┬───────────────┼───────────────┬────────────────┐
        ▼                ▼               ▼               ▼                ▼
 ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────┐
 │   Backend    │ │  Background  │ │  WAL Writer  │ │  Checkpointer│ │Autovacuum│
 │   Process    │ │   Writer     │ │              │ │              │ │ Launcher │
 │ (per conn)   │ │              │ │              │ │              │ │          │
 └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────┘

Shared Memory:
┌─────────────────────────────────────────────────────────────────┐
│  shared_buffers  │  WAL buffers  │  Lock tables  │  CLOG      │
└─────────────────────────────────────────────────────────────────┘
```

**Key Processes:**
- **Postmaster**: Accepts connections, forks backends
- **Backend**: One per client connection, executes queries
- **Background Writer**: Writes dirty buffers to disk
- **WAL Writer**: Flushes WAL to disk
- **Checkpointer**: Periodic checkpoints
- **Autovacuum Launcher**: Spawns autovacuum workers
- **Stats Collector**: Collects statistics

---

### Q2: How does PostgreSQL handle buffer management?
**Answer:**

```sql
-- Buffer pool in shared_buffers
-- Uses clock-sweep algorithm for eviction

-- Check buffer cache status
CREATE EXTENSION pg_buffercache;

SELECT 
    c.relname,
    COUNT(*) AS buffers,
    pg_size_pretty(COUNT(*) * 8192) AS size
FROM pg_buffercache b
JOIN pg_class c ON b.relfilenode = c.relfilenode
WHERE c.relname IS NOT NULL
GROUP BY c.relname
ORDER BY buffers DESC
LIMIT 10;

-- Buffer hit ratio
SELECT 
    blks_hit::float / (blks_hit + blks_read) AS cache_hit_ratio
FROM pg_stat_database
WHERE datname = current_database();
-- Target: > 99%
```

**Ring Buffer Strategy:**
- Bulk operations (large SEQ SCAN) use ring buffer
- Prevents cache pollution
- Controlled by effective_io_concurrency

---

### Q3: Explain WAL (Write-Ahead Logging)
**Answer:**

```
Transaction Flow:
1. Execute SQL
2. Modify pages in shared_buffers (dirty pages)
3. Write WAL record to WAL buffer
4. On COMMIT: Flush WAL to disk (fsync)
5. Return success to client
6. Later: Background writer flushes dirty pages

Why WAL-first?
- Sequential writes (fast)
- Small records (just changes)
- Can reconstruct data pages from WAL
```

**WAL Configuration:**
```sql
wal_level = replica        -- minimal, replica, logical
max_wal_size = 4GB         -- Checkpoint triggered
min_wal_size = 1GB         -- Retain at least this
wal_compression = on       -- Compress WAL
full_page_writes = on      -- Full page on first modify after checkpoint
```

**WAL Internals:**
```sql
-- Current WAL position
SELECT pg_current_wal_lsn();

-- WAL file info
SELECT * FROM pg_ls_waldir() ORDER BY modification DESC LIMIT 5;

-- WAL statistics
SELECT * FROM pg_stat_wal;
```

---

### Q4: How does MVCC handle visibility?
**Answer:**

```
Row Header:
┌─────────────────────────────────────────────────┐
│ xmin (create TXN) │ xmax (delete TXN) │ ctid    │
└─────────────────────────────────────────────────┘

Visibility Rules (simplified):
Row is visible if:
  xmin is committed AND xmin < snapshot_xid
  AND (xmax is 0 OR xmax is aborted OR xmax >= snapshot_xid)

Example:
TXN 100: INSERT row (xmin=100, xmax=0)
TXN 101: Take snapshot (sees xid 100-101)
TXN 102: UPDATE row (old: xmax=102, new: xmin=102)

TXN 101 sees: old row (xmax=102 > snapshot, so invisible)
TXN 103 sees: new row (xmin=102 committed)
```

**CLOG (Commit Log):**
```sql
-- Transaction status stored in pg_xact/
-- 2 bits per transaction: in-progress, committed, aborted, sub-committed

-- Check transaction status
SELECT txid_current();
SELECT txid_status(12345);
```

---

### Q5: Explain the query execution pipeline
**Answer:**

```
SQL Query
    ↓
┌────────────────┐
│     Parser     │  → Parse tree
└────────────────┘
    ↓
┌────────────────┐
│    Analyzer    │  → Query tree (with resolved names, types)
└────────────────┘
    ↓
┌────────────────┐
│    Rewriter    │  → Apply rules, expand views
└────────────────┘
    ↓
┌────────────────┐
│    Planner     │  → Generate execution plan
│   (Optimizer)  │     - Estimate costs
└────────────────┘     - Choose join order
    ↓                  - Select access methods
┌────────────────┐
│    Executor    │  → Execute plan nodes
└────────────────┘     - Fetch tuples
    ↓                  - Apply projections
   Result
```

**Plan Cache:**
```sql
-- Prepared statements cache plans
PREPARE find_user AS SELECT * FROM users WHERE id = $1;
EXECUTE find_user(123);

-- View cached plans
SELECT * FROM pg_prepared_statements;

-- Generic vs custom plans
-- First 5 executions: custom plan
-- After: generic plan if similar cost
```

---

## 2. Advanced Performance

### Q6: How do you diagnose and fix a performance regression?
**Answer:**

**Step 1: Gather Information**
```sql
-- Current activity
SELECT pid, query, state, wait_event_type, wait_event,
       now() - query_start AS duration
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- Recent slow queries (pg_stat_statements)
SELECT 
    calls,
    total_exec_time / calls AS avg_ms,
    query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Compare plan with expected
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT ...;
```

**Step 2: Common Causes**
```sql
-- Stale statistics
ANALYZE problematic_table;

-- Plan cache bloat (wrong generic plan)
DISCARD PLANS;

-- Index not being used
-- Check pg_stat_user_indexes for idx_scan = 0

-- Bloated table
SELECT n_dead_tup, last_vacuum FROM pg_stat_user_tables;
```

**Step 3: Force Plan (emergency)**
```sql
SET enable_seqscan = off;  -- Force index use
SET enable_hashjoin = off; -- Force nested loop
```

---

### Q7: Explain join algorithms in PostgreSQL
**Answer:**

**Nested Loop:**
```
For each row in outer:
    For each row in inner:
        If join condition matches:
            Output combined row

Best for:
- Small outer table
- Inner has index on join column
- Limited rows needed (LIMIT)
```

**Hash Join:**
```
1. Build hash table from inner (smaller) table
2. Scan outer table
3. Probe hash table for matches

Best for:
- Large tables
- No useful indexes
- Equality joins only
```

**Merge Join:**
```
1. Sort both tables on join column
2. Merge sorted lists

Best for:
- Pre-sorted data (index)
- Large tables
- Good for inequality joins too
```

```sql
-- Control join methods
SET enable_nestloop = on;
SET enable_hashjoin = on;
SET enable_mergejoin = on;

-- Join cost parameters
SET random_page_cost = 1.1;  -- SSD
SET effective_cache_size = '24GB';
```

---

### Q8: How do you handle N+1 query problem?
**Answer:**

**Problem:**
```python
# N+1 queries
users = db.query("SELECT * FROM users")
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")
# 1 query for users + N queries for orders
```

**Solutions:**

```sql
-- Solution 1: JOINs
SELECT u.*, o.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- Solution 2: Subquery with array aggregation
SELECT 
    u.*,
    (SELECT json_agg(o.*) FROM orders o WHERE o.user_id = u.id) AS orders
FROM users u;

-- Solution 3: Batch loading (application-side)
SELECT * FROM orders WHERE user_id = ANY($1);  -- $1 = array of user IDs
```

**ORM Solutions:**
```python
# SQLAlchemy eager loading
users = session.query(User).options(joinedload(User.orders)).all()

# Django prefetch_related
users = User.objects.prefetch_related('orders')
```

---

### Q9: Explain parallel query execution
**Answer:**

```sql
-- Enable parallel queries
SET max_parallel_workers_per_gather = 4;
SET parallel_tuple_cost = 0.01;
SET parallel_setup_cost = 1000;


-- Parallel-safe operations:
-- Sequential scans, index scans, aggregates, joins

EXPLAIN ANALYZE
SELECT COUNT(*) FROM large_table WHERE condition;

-- Output shows:
-- Gather (actual workers: 4)
--   Workers Planned: 4
--   Workers Launched: 4
--   -> Parallel Seq Scan on large_table
```

**Limitations:**
- Not all operations parallel-safe
- Cursors disable parallelism
- Within transaction with writes
- Subtransactions

```sql
-- Force parallel
ALTER TABLE large_table SET (parallel_workers = 8);

SET force_parallel_mode = on;  -- Testing only
```

---

## 3. High Availability & Disaster Recovery

### Q10: Design a zero-downtime failover system
**Answer:**

```
┌─────────────────────────────────────────────────────────────────┐
│                         Load Balancer                           │
│                       (HAProxy + VIP)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ Patroni │          │ Patroni │          │ Patroni │
   │   +     │──WAL──▶  │   +     │──WAL──▶  │   +     │
   │  PG1    │          │  PG2    │          │  PG3    │
   │(Leader) │          │(Sync)   │          │(Async)  │
   └────┬────┘          └─────────┘          └─────────┘
        │
        ▼
   ┌─────────┐
   │  etcd   │ (Distributed consensus)
   │ cluster │
   └─────────┘

Failover Process (automatic):
1. Leader fails (health check timeout)
2. Patroni releases DCS leader key
3. Sync replica has latest data
4. Sync replica acquires leader key
5. Patroni promotes to primary
6. HAProxy health checks detect new primary
7. Traffic routes to new primary
8. Old primary (if recovers) joins as replica

RTO: ~10-30 seconds
RPO: 0 (synchronous)
```

---

### Q11: How do you handle split-brain?
**Answer:**

**Prevention:**
```yaml
# Patroni configuration
bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    postgresql:
      parameters:
        # Fencing: Old primary can't accept writes
        synchronous_commit: on
        synchronous_standby_names: '*'

# When old primary recovers:
# 1. Can't reach DCS → Can't confirm leadership
# 2. Demotes self to replica
# 3. Uses pg_rewind if diverged
```

**Network Partition Handling:**
```
Scenario: Network splits cluster

Partition A: Primary + 1 replica + 2 etcd nodes
Partition B: 1 replica + 1 etcd node

Partition A: Has quorum, continues operation
Partition B: No quorum, replica stays read-only

When healed: B rejoins, replicates from A
```

---

### Q12: Explain point-in-time recovery (PITR)
**Answer:**

```bash
# Architecture
Base Backup (Sunday) + WAL Archive (Mon-Sat) = Any Point Recovery

# 1. Configure WAL archiving
# postgresql.conf
archive_mode = on
archive_command = 'cp %p /archive/%f'

# 2. Take base backup
pg_basebackup -D /backup -Ft -z -P -Xs

# 3. Recovery
# Stop PostgreSQL
# Clear data directory
# Restore base backup
tar -xzf base.tar.gz -C /var/lib/postgresql/data

# 4. Configure recovery
# postgresql.auto.conf
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2024-01-15 14:30:00'
recovery_target_action = 'promote'

# 5. Create recovery signal
touch /var/lib/postgresql/data/recovery.signal

# 6. Start PostgreSQL
# Replays WAL up to target time
```

**Recovery Targets:**
```sql
recovery_target_time = '2024-01-15 14:30:00'
recovery_target_xid = '12345678'
recovery_target_name = 'before_migration'  -- Named restore point
recovery_target_lsn = '0/12345678'
recovery_target = 'immediate'  -- As soon as consistent
```

---

## 4. Scaling & Distribution

### Q13: How would you scale writes beyond single node?
**Answer:**

**Option 1: Application Sharding**
```python
def get_shard(user_id: int, num_shards: int = 4) -> int:
    return user_id % num_shards

shards = {
    0: psycopg2.connect(host='shard0'),
    1: psycopg2.connect(host='shard1'),
    2: psycopg2.connect(host='shard2'),
    3: psycopg2.connect(host='shard3'),
}

def insert_order(user_id: int, order_data: dict):
    shard = shards[get_shard(user_id)]
    with shard.cursor() as cur:
        cur.execute("INSERT INTO orders ...", order_data)
```

**Option 2: Citus (Distributed PostgreSQL)**
```sql
-- Distribute tables
SELECT create_distributed_table('orders', 'user_id');
SELECT create_distributed_table('order_items', 'order_id',
    colocate_with => 'orders');

-- Queries automatically routed
INSERT INTO orders (user_id, ...) VALUES (123, ...);
SELECT * FROM orders WHERE user_id = 123;  -- Single shard
SELECT user_id, SUM(total) FROM orders GROUP BY user_id;  -- All shards
```

**Option 3: Partitioning + Read Replicas**
```sql
-- For append-heavy workloads (time-series)
CREATE TABLE events (...) PARTITION BY RANGE (created_at);

-- Each partition on different tablespace/disk
CREATE TABLE events_2024_01 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01')
    TABLESPACE fast_ssd;
```

---

### Q14: Explain consistent hashing for sharding
**Answer:**

```
Traditional Hashing:
shard = hash(key) % num_shards
Problem: Adding shard requires rehashing everything

Consistent Hashing:
Hash ring (0 to 2^32)
Each shard owns a range
Adding shard: Only neighbors rehash

    0
    │
 ┌──┴───┐
 │Shard1│ (0 - 1B)
 └──┬───┘
    │
 ┌──┴───┐
 │Shard2│ (1B - 2B)
 └──┬───┘
    │
 ┌──┴───┐
 │Shard3│ (2B - 4B)
 └──────┘

Add Shard4 at 3B:
Only Shard3 moves data (3B - 4B → Shard4)

Virtual Nodes:
Each physical shard → multiple points on ring
Better distribution, easier rebalancing
```

---

### Q15: How do you handle cross-shard queries?
**Answer:**

```sql
-- Avoid if possible: Use colocated tables
SELECT o.*, oi.*
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
WHERE o.user_id = 123;
-- Both tables sharded by user_id → Single shard query

-- When unavoidable: Scatter-gather
SELECT user_id, COUNT(*) 
FROM orders 
GROUP BY user_id;
-- Query all shards → Aggregate results

-- Cross-shard transactions
-- Use 2PC (two-phase commit)
BEGIN;
    -- Prepare on all shards
    PREPARE TRANSACTION 'tx1' ON shard1;
    PREPARE TRANSACTION 'tx1' ON shard2;
    -- If all succeed:
    COMMIT PREPARED 'tx1' ON shard1;
    COMMIT PREPARED 'tx1' ON shard2;
    -- If any fail:
    ROLLBACK PREPARED 'tx1' ON all;
```

---

## 5. Security

### Q16: Implement row-level security for multi-tenancy
**Answer:**

```sql
-- Table with tenant_id
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    content TEXT,
    created_by INTEGER
);

-- Enable RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents FORCE ROW LEVEL SECURITY;  -- For table owner too

-- Tenant isolation policy
CREATE POLICY tenant_isolation ON documents
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::int)
    WITH CHECK (tenant_id = current_setting('app.tenant_id')::int);

-- Application sets context
SET app.tenant_id = '42';
SELECT * FROM documents;  -- Only sees tenant 42

-- Multiple policies (OR logic)
CREATE POLICY admin_access ON documents
    FOR ALL
    TO admin_role
    USING (true);

-- Bypass RLS
ALTER USER service_account BYPASSRLS;
```

---

### Q17: Secure sensitive data at rest
**Answer:**

```sql
-- 1. Column-level encryption with pgcrypto
CREATE EXTENSION pgcrypto;

-- Encrypt on insert
INSERT INTO users (ssn_encrypted)
VALUES (pgp_sym_encrypt('123-45-6789', 'encryption_key'));

-- Decrypt on select
SELECT pgp_sym_decrypt(ssn_encrypted, 'encryption_key') AS ssn
FROM users;

-- 2. Hash passwords
INSERT INTO users (password_hash)
VALUES (crypt('password123', gen_salt('bf', 12)));

-- Verify password
SELECT password_hash = crypt('password123', password_hash) AS valid
FROM users WHERE email = 'user@example.com';

-- 3. Transparent Data Encryption (Enterprise)
-- AWS RDS, Azure: Encrypted storage
-- Self-hosted: LUKS full disk encryption
```

---

## 6. System Design Patterns

### Q18: Design a rate limiter using PostgreSQL
**Answer:**

```sql
-- Sliding window rate limiter
CREATE TABLE rate_limits (
    key TEXT NOT NULL,
    window_start TIMESTAMPTZ NOT NULL,
    count INTEGER DEFAULT 1,
    PRIMARY KEY (key, window_start)
);

CREATE INDEX idx_rate_limits_key_time ON rate_limits (key, window_start DESC);

-- Check and increment (atomic)
CREATE OR REPLACE FUNCTION check_rate_limit(
    p_key TEXT,
    p_limit INTEGER,
    p_window_seconds INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_count INTEGER;
    v_window_start TIMESTAMPTZ;
BEGIN
    v_window_start := date_trunc('second', now()) 
        - (EXTRACT(EPOCH FROM now())::int % p_window_seconds) * INTERVAL '1 second';
    
    -- Upsert and get count
    INSERT INTO rate_limits (key, window_start, count)
    VALUES (p_key, v_window_start, 1)
    ON CONFLICT (key, window_start) DO UPDATE
    SET count = rate_limits.count + 1
    RETURNING count INTO v_count;
    
    -- Cleanup old windows
    DELETE FROM rate_limits 
    WHERE key = p_key AND window_start < v_window_start;
    
    RETURN v_count <= p_limit;
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT check_rate_limit('user:123:api', 100, 60);  -- 100 req/min
```

---

### Q19: Design an event-driven system
**Answer:**

```sql
-- Outbox pattern for reliable event publishing
CREATE TABLE outbox (
    id BIGSERIAL PRIMARY KEY,
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    published_at TIMESTAMPTZ
);

CREATE INDEX idx_outbox_unpublished ON outbox(created_at) 
    WHERE published_at IS NULL;

-- Transaction: Update state + Insert event
BEGIN;
    UPDATE orders SET status = 'completed' WHERE id = $1;
    
    INSERT INTO outbox (aggregate_type, aggregate_id, event_type, payload)
    VALUES ('Order', $1, 'OrderCompleted', '{"order_id": ...}');
COMMIT;

-- Publisher polls outbox
WITH published AS (
    SELECT id, payload FROM outbox
    WHERE published_at IS NULL
    ORDER BY created_at
    LIMIT 100
    FOR UPDATE SKIP LOCKED
)
UPDATE outbox SET published_at = now()
WHERE id IN (SELECT id FROM published)
RETURNING *;

-- LISTEN/NOTIFY for real-time
CREATE OR REPLACE FUNCTION notify_outbox()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('outbox', NEW.id::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER outbox_notify
    AFTER INSERT ON outbox
    FOR EACH ROW EXECUTE FUNCTION notify_outbox();
```

---

### Q20: Implement a distributed lock
**Answer:**

```sql
-- Using advisory locks
-- Session-level (held until release or disconnect)
SELECT pg_advisory_lock(hashtext('resource:order:123'));
-- ... critical section ...
SELECT pg_advisory_unlock(hashtext('resource:order:123'));

-- Transaction-level (auto-release on commit)
SELECT pg_advisory_xact_lock(hashtext('resource:order:123'));

-- With timeout using non-blocking try
CREATE OR REPLACE FUNCTION acquire_lock_with_timeout(
    p_key TEXT,
    p_timeout_ms INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_start TIMESTAMPTZ := clock_timestamp();
    v_acquired BOOLEAN := false;
BEGIN
    LOOP
        v_acquired := pg_try_advisory_lock(hashtext(p_key));
        EXIT WHEN v_acquired;
        EXIT WHEN (clock_timestamp() - v_start) > (p_timeout_ms * INTERVAL '1 ms');
        PERFORM pg_sleep(0.01);  -- 10ms backoff
    END LOOP;
    RETURN v_acquired;
END;
$$ LANGUAGE plpgsql;

-- Using table-based locks (across connections)
CREATE TABLE distributed_locks (
    lock_name TEXT PRIMARY KEY,
    holder TEXT NOT NULL,
    acquired_at TIMESTAMPTZ DEFAULT now(),
    expires_at TIMESTAMPTZ
);

-- Acquire
INSERT INTO distributed_locks (lock_name, holder, expires_at)
VALUES ('resource:123', 'worker-1', now() + INTERVAL '30 seconds')
ON CONFLICT (lock_name) DO NOTHING
RETURNING *;  -- NULL if not acquired

-- Release
DELETE FROM distributed_locks 
WHERE lock_name = 'resource:123' AND holder = 'worker-1';

-- Cleanup expired
DELETE FROM distributed_locks WHERE expires_at < now();
```

---

## Scenario-Based Questions

### Scenario 1: Database is running out of disk space
**Immediate Actions:**
```sql
-- 1. Find large tables
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC;

-- 2. Find bloated tables
SELECT relname, n_dead_tup FROM pg_stat_user_tables ORDER BY n_dead_tup DESC;

-- 3. Check WAL accumulation
SELECT COUNT(*), pg_size_pretty(SUM(size)) 
FROM pg_ls_waldir();

-- 4. Free space without downtime
-- Delete old data
DELETE FROM logs WHERE created_at < now() - INTERVAL '90 days';

-- VACUUM to reclaim (marks reusable, doesn't shrink)
VACUUM logs;

-- 5. If desperate: VACUUM FULL (locks table!)
VACUUM FULL logs;
```

### Scenario 2: Query suddenly became slow
**Investigation:**
```sql
-- 1. Check if plan changed
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;

-- 2. Compare with expected
-- Is it using expected index?
-- Are row estimates accurate?

-- 3. Check for bloat
SELECT n_dead_tup, last_analyze FROM pg_stat_user_tables WHERE relname = 'x';

-- 4. Update statistics
ANALYZE tablename;

-- 5. Look for locks
SELECT * FROM pg_locks WHERE NOT granted;

-- 6. Check for resource contention
SELECT wait_event_type, wait_event, COUNT(*) 
FROM pg_stat_activity GROUP BY 1, 2;
```

### Scenario 3: Replication lag keeps growing
**Causes & Solutions:**
```sql
-- 1. Check lag
SELECT client_addr, state, sent_lsn, replay_lsn,
       pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
FROM pg_stat_replication;

-- 2. Common causes:
-- a) Replica can't keep up (CPU/IO)
--    Solution: Upgrade replica hardware

-- b) Long-running queries on replica
SELECT pid, query, now() - query_start 
FROM pg_stat_activity WHERE state = 'active';
--    Solution: Set hot_standby_feedback = on, or cancel queries

-- c) Network issues
--    Solution: Check network, increase wal_sender_timeout

-- d) Conflicting queries blocked by recovery
SHOW hot_standby_feedback;
SHOW max_standby_streaming_delay;
--    Solution: Increase delay or enable feedback
```
