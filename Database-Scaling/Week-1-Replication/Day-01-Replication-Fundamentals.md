# Day 1: Replication Fundamentals

## Why Replication?

Replication = maintaining copies of the same data on multiple machines.

### Goals
1. **High Availability**: If one node dies, others serve traffic
2. **Read Scalability**: Distribute read queries across replicas
3. **Latency Reduction**: Place replicas closer to users geographically
4. **Disaster Recovery**: Data survives hardware failures, data center outages

## Replication Topologies

### 1. Single-Leader (Primary-Replica)

```
┌──────────┐     ┌──────────┐
│  Primary  │────>│ Replica 1│ (read-only)
│  (Leader) │────>│ Replica 2│ (read-only)
│  R + W    │────>│ Replica 3│ (read-only)
└──────────┘     └──────────┘

Writes: Only to Primary
Reads:  From Primary or any Replica
```

**Pros**: Simple, no write conflicts, well-understood
**Cons**: Single point of write failure, write bottleneck

### 2. Multi-Leader (Multi-Primary)

```
┌──────────┐ ←──→ ┌──────────┐
│ Primary A │      │ Primary B │
│  R + W    │      │  R + W    │
└──────────┘      └──────────┘
     ↓                  ↓
┌──────────┐      ┌──────────┐
│ Replica A│      │ Replica B│
└──────────┘      └──────────┘
```

**Pros**: Write availability, geographic distribution
**Cons**: Conflict resolution required, complex

### 3. Leaderless (Dynamo-style)

```
┌──────┐  ┌──────┐  ┌──────┐
│Node 1│  │Node 2│  │Node 3│
│ R+W  │  │ R+W  │  │ R+W  │
└──────┘  └──────┘  └──────┘

Write: Send to all nodes (quorum: W nodes must ACK)
Read:  Read from multiple nodes (quorum: R nodes must respond)
Rule:  W + R > N (ensures overlap → at least 1 fresh read)
```

**Pros**: No single point of failure, tunable consistency
**Cons**: Complex, eventual consistency, read repair needed

## Replication Methods

### 1. Statement-Based Replication
```sql
-- Primary logs the SQL statements
INSERT INTO users (name, email) VALUES ('Bharath', 'b@e.com');
-- Replicas re-execute the same statements
```
**Problem**: Non-deterministic functions (`NOW()`, `RAND()`) produce different results.

### 2. Write-Ahead Log (WAL) Shipping
```
Primary writes to WAL → Ships WAL segments to replicas → Replicas replay WAL
```
**PostgreSQL** uses this. Very reliable, byte-level replication.
**Downside**: Coupled to storage engine version — can't replicate across versions.

### 3. Logical (Row-Based) Replication
```json
// Replication log entries
{ "table": "users", "op": "INSERT", "data": {"id": 1, "name": "Bharath"} }
{ "table": "users", "op": "UPDATE", "key": {"id": 1}, "data": {"name": "BK"} }
{ "table": "users", "op": "DELETE", "key": {"id": 1} }
```
**Pros**: Version independent, can replicate between different databases.
**PostgreSQL logical replication**, MySQL binlog (ROW format).

### 4. Trigger-Based Replication
Application-level — triggers fire on data changes and log to a replication table.
**Most flexible, least performant.** Used for custom replication logic.

## Synchronous vs Asynchronous Replication

### Synchronous
```
Client → Primary → Replica ACK → Client gets response
         (waits for replica to confirm)
```
- **Guarantees**: Replica has the data before client gets response
- **Trade-off**: Higher latency, lower availability (replica down = writes blocked)

### Asynchronous
```
Client → Primary → Client gets response
                 ↓ (async, in background)
              Replica receives data later
```
- **Guarantees**: None — replica may be behind
- **Trade-off**: Lower latency, higher availability, risk of data loss on primary failure

### Semi-Synchronous (Practical Choice)
```
1 replica: synchronous (guaranteed copy)
N replicas: asynchronous (eventual)
```
PostgreSQL: `synchronous_commit = on` with `synchronous_standby_names`

## Replication Lag

The delay between a write on the primary and the data appearing on replicas.

### Problems Caused by Lag

```
1. Read-your-writes inconsistency:
   User writes profile → reads from replica → sees old data 😱

2. Monotonic reads violation:
   User reads from Replica A (fresh) → reads from Replica B (stale) → data "goes back in time"

3. Causal ordering violation:
   User A writes comment → User B writes reply → Replica shows reply before comment
```

### Solutions

```
Read-your-writes:
  → Route reads to primary for X seconds after a write
  → Use client timestamp to check if replica is fresh enough

Monotonic reads:
  → Pin user to same replica (sticky sessions by user ID hash)

Causal consistency:
  → Use logical clocks / vector clocks to order events
```

## Failover

When the primary fails, a replica must be promoted.

### Automatic Failover Steps
1. **Detect failure**: Heartbeat timeout (e.g., 30 seconds)
2. **Elect new primary**: Most up-to-date replica
3. **Reconfigure**: Route writes to new primary, old primary becomes replica on recovery

### Failover Gotchas
```
Split-brain:  Two nodes think they're primary → data divergence
              Fix: Fencing (STONITH — Shoot The Other Node In The Head)

Data loss:    Async replica promoted → missing recent writes from old primary
              Fix: Semi-synchronous replication

Stale reads:  Client cached the old primary's address
              Fix: DNS TTL, service discovery update
```

## PostgreSQL Replication Setup (Quick Reference)

```bash
# Primary: postgresql.conf
wal_level = replica
max_wal_senders = 5
synchronous_commit = on
synchronous_standby_names = 'replica1'

# Primary: pg_hba.conf
host replication replicator replica-ip/32 md5

# Replica: Create base backup
pg_basebackup -h primary-ip -D /var/lib/postgresql/data -U replicator -P

# Replica: postgresql.conf
primary_conninfo = 'host=primary-ip user=replicator password=xxx'
```

## Key Takeaways

1. **Single-leader** is the default — simple, well-understood, handles most use cases
2. **Async replication** is the practical choice — accept eventual consistency
3. **Replication lag** causes real problems — implement read-your-writes guarantees
4. **Failover is hard** — split-brain is the biggest risk, use fencing
5. **WAL shipping** (PostgreSQL) is the most reliable replication method
