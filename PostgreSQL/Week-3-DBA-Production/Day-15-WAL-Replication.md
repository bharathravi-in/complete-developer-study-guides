# Day 15: WAL & Replication

## 📚 Learning Objectives
- Understand Write-Ahead Logging
- Master streaming replication
- Learn logical replication
- Configure replication setups

---

## 1. Write-Ahead Logging (WAL)

### What is WAL?

```
Write Operation Flow:
┌──────────┐    ┌──────────┐    ┌──────────┐
│ Transaction│ → │ WAL      │ → │ Data     │
│ (INSERT)  │    │ Buffer   │    │ Files    │
└──────────┘    └──────────┘    └──────────┘
                    │
                    ▼
               ┌──────────┐
               │ WAL File │  (Durability!)
               │ on Disk  │
               └──────────┘

WAL guarantees: If committed, data is in WAL
               Even if crash before data files written
```

### WAL Files

```bash
# Location
ls -la $PGDATA/pg_wal/

# Files named like: 000000010000000000000001
# Format: TimelineID + LogID + Segment

# Each segment: 16MB by default
SHOW wal_segment_size;  -- 16MB
```

### WAL Levels

```sql
SHOW wal_level;

-- minimal:  Crash recovery only (no archiving/replication)
-- replica:  Supports streaming replication + PITR
-- logical:  Supports logical replication (most info)

-- Set in postgresql.conf
wal_level = replica  -- Minimum for replication
```

### WAL Configuration

```sql
-- WAL behavior
SHOW wal_buffers;      -- Memory for WAL before flush
SHOW wal_writer_delay; -- Frequency of WAL writes

-- Sync settings
SHOW fsync;                  -- Flush WAL to disk (always on!)
SHOW synchronous_commit;     -- When to report commit
SHOW wal_sync_method;        -- How to sync (fdatasync, fsync)

-- Size management
SHOW max_wal_size;     -- Trigger checkpoint if exceeded
SHOW min_wal_size;     -- Minimum WAL to keep
```

---

## 2. Streaming Replication

### Architecture

```
┌──────────────┐         ┌──────────────┐
│   PRIMARY    │ ──WAL──→│   REPLICA    │
│  (Read/Write)│         │  (Read-Only) │
└──────────────┘         └──────────────┘
       │                        │
       ▼                        ▼
  ┌─────────┐            ┌─────────┐
  │ pg_wal/ │            │ pg_wal/ │
  └─────────┘            └─────────┘

WAL records stream continuously from primary to replica
```

### Setup Primary

```sql
-- postgresql.conf (Primary)
wal_level = replica
max_wal_senders = 10           -- Max replication connections
max_replication_slots = 10     -- Named slots for replicas
wal_keep_size = 1GB            -- Keep WAL for slow replicas

-- pg_hba.conf (Primary)
-- Allow replication connections
host replication repl_user 192.168.1.0/24 scram-sha-256

-- Create replication user
CREATE USER repl_user REPLICATION LOGIN PASSWORD 'secret';
```

### Setup Replica

```bash
# Stop PostgreSQL on replica
systemctl stop postgresql

# Clear data directory
rm -rf /var/lib/postgresql/data/*

# Base backup from primary
pg_basebackup -h primary_host -D /var/lib/postgresql/data \
    -U repl_user -P --wal-method=stream

# Or with replication slot
pg_basebackup -h primary_host -D /var/lib/postgresql/data \
    -U repl_user -P --wal-method=stream -S replica1_slot
```

```sql
-- postgresql.conf (Replica)
hot_standby = on  -- Allow read queries

-- Create standby.signal file
touch /var/lib/postgresql/data/standby.signal

-- primary_conninfo in postgresql.auto.conf
primary_conninfo = 'host=primary_host port=5432 user=repl_user password=secret'
```

### Replication Slots

Prevent WAL cleanup until replica catches up.

```sql
-- Create slot (on primary)
SELECT pg_create_physical_replication_slot('replica1_slot');

-- View slots
SELECT * FROM pg_replication_slots;

-- Drop slot (if replica removed)
SELECT pg_drop_replication_slot('replica1_slot');
```

### Monitor Replication

```sql
-- On Primary: View replicas
SELECT 
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS lag_bytes
FROM pg_stat_replication;

-- On Replica: Check recovery status
SELECT 
    pg_is_in_recovery(),
    pg_last_wal_receive_lsn(),
    pg_last_wal_replay_lsn(),
    pg_last_xact_replay_timestamp();

-- Lag in time
SELECT NOW() - pg_last_xact_replay_timestamp() AS lag;
```

---

## 3. Synchronous Replication

### Configuration

```sql
-- postgresql.conf (Primary)
synchronous_standby_names = 'replica1'  -- Wait for named standby

-- Multiple standbys (first available)
synchronous_standby_names = 'FIRST 1 (replica1, replica2)'

-- Wait for any N standbys
synchronous_standby_names = 'ANY 2 (replica1, replica2, replica3)'
```

### Synchronous Modes

```sql
-- synchronous_commit options:
-- on:           Wait for WAL flush on primary
-- remote_write: Wait for WAL write (not flush) on standby
-- remote_apply: Wait for replay on standby (visible for reads)
-- local:        Wait for local flush only
-- off:          Don't wait (fastest, least durable)

SET synchronous_commit = 'remote_apply';  -- Strongest guarantee
```

---

## 4. Logical Replication

### vs Physical Replication

| Feature | Physical | Logical |
|---------|----------|---------|
| Replicates | Entire cluster | Specific tables |
| Cross-version | No | Yes |
| Cross-platform | No | Yes |
| Read/Write replica | No | Possible |
| DDL propagation | Automatic | Manual |

### Setup Publisher

```sql
-- postgresql.conf
wal_level = logical

-- Create publication
CREATE PUBLICATION my_pub FOR TABLE users, orders;

-- Or all tables
CREATE PUBLICATION all_tables FOR ALL TABLES;

-- Add table to publication
ALTER PUBLICATION my_pub ADD TABLE products;
```

### Setup Subscriber

```sql
-- Create subscription
CREATE SUBSCRIPTION my_sub 
CONNECTION 'host=publisher port=5432 dbname=mydb user=repl_user' 
PUBLICATION my_pub;

-- View subscriptions
SELECT * FROM pg_subscription;

-- View subscription stats
SELECT * FROM pg_stat_subscription;
```

### Logical Replication Slots

```sql
-- View logical slots
SELECT * FROM pg_replication_slots WHERE slot_type = 'logical';

-- Created automatically with subscription
-- Drop when removing subscription
DROP SUBSCRIPTION my_sub;
```

---

## 5. Failover & Promotion

### Promote Replica

```bash
# Using pg_ctl
pg_ctl promote -D /var/lib/postgresql/data

# Using SQL (PG 12+)
SELECT pg_promote();
```

```sql
-- Check if promoted
SELECT pg_is_in_recovery();  -- false = now primary
```

### Timeline Changes

After promotion, timeline increments to track new history.

```
Timeline 1: Original primary
     │
     ├── Replica catches up
     │
     ▼
Timeline 2: Promoted replica (now primary)
```

---

## 📝 Key Takeaways

1. **WAL ensures durability** - Write log before data
2. **Physical replication is byte-for-byte** - Entire cluster mirrored
3. **Logical replication is selective** - Choose tables, cross-version
4. **Replication slots prevent WAL loss** - Keep WAL until consumed
5. **Synchronous = consistency over speed** - Remote_apply for read-your-writes

---

## ✅ Day 15 Checklist

- [ ] Configure WAL level for replication
- [ ] Set up physical streaming replication
- [ ] Create and monitor replication slots
- [ ] Configure logical replication
- [ ] Practice failover procedure
- [ ] Monitor replication lag
