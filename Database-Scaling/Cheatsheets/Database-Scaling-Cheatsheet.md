# Database Scaling Cheatsheet — Quick Reference

## Replication Types
```
Single-Leader:  1 Primary (R+W) → N Replicas (R only)
Multi-Leader:   N Primaries (R+W) ↔ sync between them
Leaderless:     All nodes R+W, quorum reads/writes
```

## Replication Methods
```
WAL Shipping:     Physical byte-level (PostgreSQL) — version-coupled
Logical (Row):    INSERT/UPDATE/DELETE events — version-independent
Statement:        SQL statements replayed — non-deterministic issues
```

## Sync vs Async
```
Synchronous:     Write → Replica ACK → Response (safe, slow)
Asynchronous:    Write → Response → Replica later (fast, risky)
Semi-Sync:       1 sync replica + N async (practical)
```

## Sharding Strategies
```
Range:         key ranges per shard (hot spots risk)
Hash:          hash(key) % N (even, but reorganize on resize)
Consistent:    Hash ring, ~1/N keys move on add/remove
Directory:     Lookup table maps key→shard (flexible, SPOF)
Geo:           Region-based (data sovereignty)
```

## Shard Key Rules
```
✅ High cardinality    ❌ Low cardinality (country)
✅ Even distribution   ❌ Monotonically increasing
✅ In most queries     ❌ Rarely queried field
✅ Immutable           ❌ Frequently changing
```

## CAP Theorem
```
CP: Consistency + Partition Tolerance (PostgreSQL, MongoDB)
AP: Availability + Partition Tolerance (Cassandra, DynamoDB)

Network partitions are inevitable → P is mandatory → Choose C or A
```

## Quorum Formula
```
N = total replicas
W = write quorum
R = read quorum

Strong: W + R > N
Fast:   W=1, R=1 (eventual consistency)
```

## Consistency Models (Strong → Weak)
```
Linearizable    → Every read returns latest write
Sequential      → Total order respecting per-client order
Causal          → Causally related ops in order
Read-your-writes → See your own writes
Eventual        → Converges eventually, no ordering guarantee
```

## Conflict Resolution
```
LWW:           Last-Write-Wins by timestamp (data loss risk)
Vector Clocks: Detect conflicts, app resolves
CRDTs:         Auto-merge without conflicts (G-Counter, OR-Set)
```

## Distributed Transactions
```
2PC:   Prepare → Commit/Abort (coordinator SPOF)
Saga:  Local txns + compensating actions
       Choreography: Event-driven
       Orchestration: Central coordinator
```

## PostgreSQL Scaling Path
```
1. Indexing & query optimization
2. Connection pooling (PgBouncer)
3. Read replicas (streaming replication)
4. Table partitioning (range/list/hash)
5. Citus/PG sharding extension
6. If still not enough → dedicated sharding
```

## Caching Patterns
```
Cache-Aside:       App reads cache → miss → read DB → update cache
Write-Through:     App writes cache + DB simultaneously
Write-Behind:      App writes cache → async write to DB
Read-Through:      Cache reads from DB on miss (transparent)
```

## Failover Checklist
```
☐ Heartbeat monitoring (timeout: 10-30s)
☐ Automated replica promotion
☐ Fencing mechanism (prevent split-brain)
☐ DNS/service discovery update
☐ Connection pool refresh
☐ Application retry with backoff
☐ Data consistency verification post-failover
```

## Key Numbers
```
Single PostgreSQL:  ~5K TPS writes, ~50K TPS reads
Redis:              ~100K ops/sec (single thread)
Network partition:  Happens ~1-5x/year in cloud
Replication lag:    Async: ms to seconds; Sync: 0 (at cost of latency)
Failover time:      Automated: 10-30s; Manual: minutes to hours
```
