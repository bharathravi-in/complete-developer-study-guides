# Database Scaling Interview Questions — Senior / Staff Level

## Section 1: Replication

### Q1: Explain the difference between synchronous and asynchronous replication.
**Answer**: **Synchronous**: Primary waits for replica to confirm write before responding to client. Guarantees durability but increases latency and reduces availability (replica down = writes blocked). **Asynchronous**: Primary responds immediately, replicates in background. Lower latency but risks data loss if primary fails before replication. **Semi-synchronous** (practical choice): 1 replica synchronous for guaranteed backup, rest asynchronous.

### Q2: What is replication lag and what problems does it cause?
**Answer**: Replication lag is the delay between a write on the primary and its appearance on replicas. Three key problems:
1. **Read-your-writes**: User writes data, reads from stale replica, doesn't see their write. Fix: Route reads to primary for N seconds after write.
2. **Non-monotonic reads**: User reads fresh data from Replica A, then stale data from Replica B — appears to go back in time. Fix: Sticky sessions (pin user to one replica).
3. **Causal violations**: Reply appears before the comment it references. Fix: Logical clocks.

### Q3: Explain failover in a primary-replica setup. What can go wrong?
**Answer**: Failover promotes a replica to primary when the primary fails. Steps: (1) Detect failure via heartbeat timeout, (2) Elect most up-to-date replica, (3) Reconfigure routing.

**Pitfalls**:
- **Split-brain**: Two nodes think they're primary → data divergence. Fix: Fencing (STONITH).
- **Data loss**: Async replica missing recent writes from old primary.
- **Stale routing**: Clients still point to old primary. Fix: Service discovery update, short DNS TTL.

### Q4: Multi-leader vs single-leader replication — when would you use multi-leader?
**Answer**: Multi-leader allows writes to multiple nodes simultaneously. Use when: (1) Multi-datacenter deployment (each DC has a leader for low write latency), (2) Offline-capable apps (each device is a "leader"), (3) Collaborative editing (Google Docs). **Trade-off**: Must handle write conflicts via LWW, vector clocks, or CRDTs.

## Section 2: Sharding

### Q5: What is sharding and when should you consider it?
**Answer**: Sharding = horizontal partitioning of data across multiple database servers. Each shard holds a subset of data with the same schema.

**Shard when**: (1) Data exceeds single-server capacity (>1-5 TB), (2) Write throughput exceeds single-server capacity (>10K TPS), (3) Read replicas can't handle read load. **Exhaust first**: Indexing, query optimization, caching, read replicas, vertical scaling.

### Q6: Explain consistent hashing and why it's important for sharding.
**Answer**: Standard hashing (`hash(key) % N`) requires rehashing ALL keys when N changes. Consistent hashing uses a hash ring — keys and nodes are mapped to positions on a ring. A key belongs to the next clockwise node.

**Benefits**: When adding/removing a node, only ~1/N keys need to move (vs. ALL keys in standard hashing). **Virtual nodes** ensure even distribution — each physical node has 100-200 positions on the ring.

### Q7: How do you choose a shard key? What makes a good vs bad shard key?
**Answer**:
- **Good**: High cardinality, even distribution, included in most queries, immutable. Examples: `user_id` for user-centric apps, `tenant_id` for multi-tenant SaaS.
- **Bad**: Low cardinality (`country` — only ~200 values), monotonically increasing (`auto_increment` — creates hot shard with range sharding), frequently changing (`email`).
- **Compound keys** (`tenant_id, user_id`): Provide isolation and distribution.

### Q8: How do you handle cross-shard queries?
**Answer**: (1) **Scatter-gather**: Send query to all shards, merge results. Expensive, avoid in hot paths. (2) **Global tables**: Replicate small, rarely-changing tables (countries, config) to all shards. (3) **Denormalization**: Duplicate data across shards to avoid joins. (4) **Application-level joins**: Fetch from multiple shards and join in application code. Best strategy: **Design schema so most queries only hit one shard.**

### Q9: How do you add more shards without downtime?
**Answer**: **Consistent hashing** minimizes data movement. Alternatively: (1) **Virtual shards**: Pre-create 256+ logical shards, map to physical nodes. Adding capacity = reassign logical shards. (2) **Double-write migration**: Write to old + new shard, backfill old data, switch reads to new, stop writes to old. (3) **Ghost tables** (like pt-online-schema-change): Create new table, copy data, atomic rename.

## Section 3: CAP Theorem & Consistency

### Q10: Explain CAP theorem. Can you have all three?
**Answer**: In a distributed system: **C**onsistency (all reads return latest write), **A**vailability (every request gets a response), **P**artition tolerance (system works despite network failures). Since network partitions are inevitable, P is mandatory — you choose between **CP** (return error rather than stale data) and **AP** (return stale data rather than error). You cannot have all three during a partition. Technologies: CP = PostgreSQL, MongoDB. AP = Cassandra, DynamoDB.

### Q11: What is eventual consistency? Give real-world examples where it's acceptable.
**Answer**: If no new writes occur, all replicas eventually converge to the same value. Acceptable for: social media feeds (seeing a like 2 seconds late is fine), analytics dashboards, DNS propagation, shopping carts (low-stakes, temporary). **Not acceptable for**: bank balances, inventory counts (prevent overselling), authentication state.

### Q12: Explain the Saga pattern for distributed transactions.
**Answer**: Saga breaks a distributed transaction into local transactions with compensating actions for rollback.

- **Choreography**: Services emit events, other services react. Decoupled but hard to track.
- **Orchestration**: Central coordinator directs the workflow. Easier to reason about.

Example: Order = Create Order → Charge Payment → Reserve Inventory. If inventory fails → Compensate: Refund → Cancel Order. Unlike 2PC, there's no locking — uses eventual consistency with compensating actions.

## Section 4: System Design Scenarios

### Q13: Design the database architecture for a social media platform with 100M users.
**Answer**:
- **User data**: Shard by `user_id` (hash-based, 256 shards mapped to physical nodes)
- **Posts/Feed**: Shard by `user_id` — user's posts and feed on same shard
- **Read path**: Redis cache for hot feeds (fan-out-on-write for users with <1K followers, fan-out-on-read for celebrities)
- **Replication**: Primary + 2 async replicas per shard, semi-sync for 1 replica
- **Global data**: User search index in Elasticsearch (not sharded by user)
- **Analytics**: Stream to Kafka → data warehouse (separate from OLTP)

### Q14: How would you migrate a monolithic database to a sharded architecture?
**Answer**: (1) Choose shard key based on query patterns. (2) Implement routing layer in application. (3) Set up new shards. (4) **Double-write**: Application writes to both old DB and new shards. (5) Backfill: Copy historical data to correct shards. (6) Verify data consistency (row counts, checksums). (7) Switch reads to new shards. (8) Stop writes to old DB. (9) Decommission old DB. **Key**: Use feature flags for gradual rollout, have rollback plan.

## Rapid-Fire Summary

| Concept | One-Liner |
|---------|-----------|
| Replication | Copies of same data on multiple machines |
| Sharding | Different data subsets on different machines |
| CAP theorem | Pick 2: Consistency, Availability, Partition tolerance |
| Consistent hashing | Hash ring — only 1/N keys move when adding nodes |
| Replication lag | Delay between primary write and replica visibility |
| Failover | Promote replica to primary when primary fails |
| Split-brain | Two nodes think they're primary — catastrophic |
| Saga pattern | Distributed transactions via compensating actions |
| CRDT | Conflict-free data structures for AP systems |
| Shard key | The field determining which shard holds the data |
