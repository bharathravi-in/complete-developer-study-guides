# Day 30: Mock Interview & Final Review

## 📚 Objectives
- Review all key concepts
- Practice interview questions
- System design scenarios
- Final assessment

---

## 1. Quick Concept Review

### Architecture
- PostgreSQL uses process-per-connection model
- Shared memory: shared_buffers, WAL buffers
- Key processes: Postmaster, Background Writer, WAL Writer, Autovacuum

### ACID & Transactions
- MVCC enables non-blocking reads
- Isolation levels: Read Committed (default), Repeatable Read, Serializable
- Transaction IDs wrap at 2 billion (need VACUUM)

### Indexing
- B-tree: Default, equality and range
- GIN: Arrays, JSONB, Full-text
- GiST: Geometric, Full-text, ranges
- BRIN: Time-series, sorted data (compact)

### Performance
- EXPLAIN ANALYZE for query plans
- Look for Seq Scan on large tables
- shared_buffers = 25% RAM
- effective_cache_size = 75% RAM

### Locking
- Row-level: FOR UPDATE, FOR SHARE
- Table-level: ACCESS SHARE through ACCESS EXCLUSIVE
- Advisory locks for application-level locking

### Replication
- Streaming: Physical, real-time
- Logical: Table-level, cross-version
- Synchronous for zero data loss

---

## 2. Common Interview Questions

### Junior Level

**Q: What is the difference between DELETE and TRUNCATE?**
```sql
-- DELETE: Row-level, can have WHERE, triggers fire, logged
DELETE FROM users WHERE active = false;

-- TRUNCATE: Releases storage, no WHERE, no triggers, faster
TRUNCATE TABLE temp_data;
```

**Q: What is a primary key vs unique constraint?**
```sql
-- Primary Key: Unique + NOT NULL + only one per table
CREATE TABLE users (
    id SERIAL PRIMARY KEY
);

-- Unique: Allows one NULL, multiple per table
CREATE TABLE users (
    email VARCHAR(255) UNIQUE,
    ssn VARCHAR(11) UNIQUE
);
```

**Q: Explain JOIN types**
```sql
-- INNER: Only matching rows
-- LEFT: All from left + matching right
-- RIGHT: All from right + matching left
-- FULL: All rows, NULL where no match
-- CROSS: Cartesian product
```

---

### Mid Level

**Q: How does MVCC work?**
```
Every row has xmin (created by TX) and xmax (deleted by TX)
When you UPDATE, PostgreSQL:
1. Marks old row dead (set xmax)
2. Inserts new row (new xmin)

Readers see snapshot - rows where:
- xmin committed before snapshot
- xmax not set or not committed

No read locks needed!
```

**Q: How do you optimize a slow query?**
```sql
-- 1. Run EXPLAIN ANALYZE
EXPLAIN ANALYZE SELECT ...;

-- 2. Look for:
-- - Sequential scans on large tables
-- - High actual vs estimated rows
-- - Sort/Hash operations on disk

-- 3. Solutions:
-- - Add appropriate index
-- - Update statistics: ANALYZE table
-- - Rewrite query (avoid functions in WHERE)
-- - Check for missing JOINs
```

**Q: Explain PostgreSQL isolation levels**
```
Read Committed (default):
- See committed data at statement start
- May see different data in same transaction

Repeatable Read:
- See snapshot at transaction start
- Serialization errors on conflicts

Serializable:
- Full isolation, as if sequential
- Most serialization errors
```

**Q: What causes table bloat?**
```
Dead tuples from UPDATE/DELETE not vacuumed
Causes:
- Autovacuum not keeping up
- Long-running transactions holding back vacuum
- Disabled autovacuum

Solution:
- Manual VACUUM FULL (locks table)
- pg_repack (online rebuild)
- Fix autovacuum settings
```

---

### Senior Level

**Q: Design a high-availability PostgreSQL setup**
```
Architecture:
┌─────────────┐
│  HAProxy    │ ←── Health checks
└─────┬───────┘
      │
┌─────┼─────┬─────────────┐
│     │     │             │
▼     ▼     ▼             ▼
PG1   PG2   PG3         etcd
(P)   (S)   (S)       (consensus)
│     │     │
└──Patroni──┘

Components:
- Patroni: Automatic failover management
- etcd/Consul: Leader election, distributed consensus
- HAProxy: Connection routing via health checks
- Streaming replication: Data sync

RTO: ~10-30 seconds
RPO: 0 with synchronous_commit
```

**Q: How would you handle a 100TB database?**
```
Strategy:
1. Partitioning
   - Range by date (time-series)
   - Hash for even distribution
   
2. Tablespaces
   - Hot data on SSD
   - Cold data on HDD
   
3. Archiving
   - Move old partitions to archive
   - DROP PARTITION for cleanup

4. Read replicas
   - Scale reads horizontally
   
5. Consider sharding (Citus)
   - If single node can't handle writes
```

**Q: Explain VACUUM and why it's critical**
```
VACUUM does:
1. Reclaims dead tuples (marks reusable)
2. Updates visibility map
3. Updates free space map
4. Freezes old transactions (XID wraparound prevention)

XID Wraparound:
- 32-bit transaction IDs
- Wraps at 2 billion
- Without freezing, "future" transactions become "past"
- Data appears to vanish!

autovacuum_freeze_max_age = 200M default
```

---

## 3. System Design Scenarios

### Scenario 1: Real-time Leaderboard

**Requirements:**
- 10M users, 1M concurrent
- Update scores in real-time
- Get user rank instantly

**Solution:**
```sql
-- Option 1: Materialized view (near real-time)
CREATE TABLE scores (
    user_id UUID PRIMARY KEY,
    score BIGINT,
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_scores_rank ON scores (score DESC);

-- Get rank
SELECT COUNT(*) + 1 AS rank
FROM scores
WHERE score > (SELECT score FROM scores WHERE user_id = $1);

-- Option 2: Redis sorted set for real-time
-- PostgreSQL as source of truth
-- Redis ZADD/ZRANK for instant ranking
```

### Scenario 2: Event Sourcing System

**Requirements:**
- Append-only event log
- Rebuild state from events
- High write throughput

**Solution:**
```sql
CREATE TABLE events (
    id BIGSERIAL,
    stream_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    data JSONB NOT NULL,
    version INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (stream_id, version)  -- Natural order
) PARTITION BY RANGE (created_at);

-- Optimistic locking
INSERT INTO events (stream_id, event_type, data, version)
SELECT $1, $2, $3, COALESCE(MAX(version), 0) + 1
FROM events WHERE stream_id = $1
-- Fails on concurrent write (version conflict)
```

### Scenario 3: Multi-tenant SaaS

**Requirements:**
- 10,000 tenants
- Complete data isolation
- Per-tenant backup/restore

**Solution:**
```sql
-- Schema per tenant approach
CREATE SCHEMA tenant_12345;
SET search_path = tenant_12345, public;

-- Or shared with RLS
CREATE TABLE data (
    id SERIAL,
    tenant_id UUID NOT NULL,
    ...
);

ALTER TABLE data ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_access ON data
    USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- Always set context
SET app.tenant_id = 'uuid-here';
```

---

## 4. Troubleshooting Scenarios

### "Database is slow"
```sql
-- Check active queries
SELECT pid, now() - query_start AS duration, query 
FROM pg_stat_activity 
WHERE state = 'active' ORDER BY duration DESC;

-- Check for locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Check for bloat
SELECT relname, n_dead_tup, last_vacuum 
FROM pg_stat_user_tables 
ORDER BY n_dead_tup DESC;

-- Check cache hit ratio
SELECT 
    sum(blks_hit) / sum(blks_hit + blks_read) AS ratio
FROM pg_stat_database;
```

### "Replication lag increasing"
```sql
-- Check on primary
SELECT 
    client_addr,
    sent_lsn - replay_lsn AS bytes_behind,
    state
FROM pg_stat_replication;

-- Possible causes:
-- 1. Replica under-provisioned
-- 2. Network issues
-- 3. Long transactions on replica
-- 4. Disk I/O on replica
```

### "Out of disk space"
```sql
-- Find largest tables
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_stat_user_tables ORDER BY pg_total_relation_size(relid) DESC;

-- Check for bloat
SELECT relname, 
       pg_size_pretty(pg_relation_size(oid)) AS size,
       pg_size_pretty(pg_relation_size(oid) - 
           (reltuples * (SELECT avg(pg_column_size(t.*)) FROM tablename t))) AS estimated_bloat
FROM pg_class WHERE relkind = 'r';

-- Solutions:
-- 1. VACUUM FULL (locks table)
-- 2. pg_repack (online)
-- 3. Archive/delete old data
```

---

## 5. Final Checklist

### Must Know ✓
- [ ] ACID properties and MVCC
- [ ] Index types and when to use each
- [ ] EXPLAIN ANALYZE interpretation
- [ ] VACUUM purpose and autovacuum tuning
- [ ] Replication types and setup
- [ ] Backup/restore procedures
- [ ] Connection pooling (PgBouncer)

### Should Know ✓
- [ ] Query optimization techniques
- [ ] Partitioning strategies
- [ ] Lock types and deadlock handling
- [ ] Monitoring with pg_stat_* views
- [ ] High availability with Patroni
- [ ] Security (RLS, SSL, pg_hba.conf)

### Nice to Know ✓
- [ ] Sharding with Citus
- [ ] pgvector for AI/ML
- [ ] Event sourcing patterns
- [ ] System design with PostgreSQL

---

## 🎯 Interview Tips

1. **Always quantify** - "I've managed X TB database with Y TPS"
2. **Explain tradeoffs** - "B-tree is good for equality but GIN better for arrays"
3. **Show depth** - Don't just name features, explain internals
4. **Relate to experience** - "When I faced this, I solved it by..."
5. **Ask clarifying questions** - Shows system design thinking

---

## 🏆 Congratulations!

You've completed the 30-day PostgreSQL mastery plan. Key areas covered:

- **Week 1**: Foundations (Architecture → Window Functions)
- **Week 2**: Performance (ACID → Configuration)
- **Week 3**: DBA (WAL → Connection Pooling)
- **Week 4**: Advanced (JSONB → AI Integration)

Next steps:
1. Practice on real datasets
2. Contribute to PostgreSQL community
3. Get certified (EDB, Crunchy Data)
4. Build projects showcasing PostgreSQL expertise
