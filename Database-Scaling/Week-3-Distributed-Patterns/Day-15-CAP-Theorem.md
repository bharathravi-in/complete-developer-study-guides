# Day 15: CAP Theorem & Consistency Models

## CAP Theorem

In a **distributed data store**, you can only guarantee **2 of 3** properties:

```
         C (Consistency)
        / \
       /   \
      /     \
     P ───── A
(Partition  (Availability)
 Tolerance)
```

### The Three Properties

| Property | Meaning |
|----------|---------|
| **Consistency** | Every read receives the most recent write (linearizability) |
| **Availability** | Every request receives a response (not an error) |
| **Partition Tolerance** | System continues operating despite network partitions |

### The Reality: Pick CP or AP

Since network partitions **will happen** in any distributed system, P is non-negotiable. So the real choice is:

| Type | During Partition | Examples |
|------|-----------------|----------|
| **CP** | Sacrifice availability — return errors rather than stale data | PostgreSQL, MongoDB (default), HBase, Redis Cluster |
| **AP** | Sacrifice consistency — return potentially stale data | Cassandra, DynamoDB, CouchDB, Riak |

### PACELC Extension

What happens when there is **no partition**?

```
If Partition → Choose C or A
Else         → Choose Latency or Consistency

PA/EL: Prioritize availability & latency (DynamoDB, Cassandra)
PC/EC: Prioritize consistency always (PostgreSQL, traditional RDBMS)
PA/EC: Available during partition, consistent otherwise (Cosmos DB default)
PC/EL: Consistent during partition, low latency otherwise (rare)
```

## Consistency Models (From Strongest to Weakest)

### 1. Linearizability (Strongest)

Every operation appears to execute instantaneously at some point between invocation and completion. All clients see the same order.

```
Timeline:  [---Write x=1---]    [---Read---]
                              → Must return 1

Real-world: Single-leader with synchronous replication
Cost: Very high latency
Use: Distributed locks, leader election
```

### 2. Sequential Consistency

All operations appear in SOME total order, consistent with the program order of each client. Different from linearizability — the "instant" constraint is relaxed.

### 3. Causal Consistency

Operations that are causally related are seen in the same order by all nodes. Concurrent (unrelated) operations may be seen in different orders.

```
Client A: Write("comment", "Nice post!")     → timestamp T1
Client B: ReadComment() at T1, then Write("reply", "Thanks!")  → timestamp T2

Causal: ALL nodes see comment before reply (causally related)
But: Unrelated writes can appear in any order
```

### 4. Read-Your-Writes (Session Consistency)

A client always sees their own writes. Other clients may see stale data.

```
Client A: Write x=5 → Read x → MUST see x=5
Client B: Read x → MAY see x=5 or old value
```

### 5. Eventual Consistency (Weakest)

If no new writes occur, eventually all replicas converge to the same value.

```
Write x=5 → Replica1: x=5, Replica2: x=3 (stale) → Eventually: all x=5
"Eventually" = could be milliseconds to minutes
```

## Tunable Consistency (DynamoDB / Cassandra)

```
N = Number of replicas
W = Write quorum (nodes that must ACK a write)
R = Read quorum (nodes that must respond to a read)

Strong consistency:  W + R > N
Eventual consistency: W + R ≤ N

Example with N=3:
  W=3, R=1: Strong read, but writes block if 1 node down
  W=2, R=2: Balanced (strong if W+R > N)
  W=1, R=1: Fastest, but eventual consistency
```

## Conflict Resolution Strategies

### Last-Write-Wins (LWW)

```
Node A: SET x = "apple"  at T=100
Node B: SET x = "banana" at T=101
Merge:  x = "banana" (highest timestamp wins)

Problem: Clock skew → data loss
         T=100 might actually be AFTER T=101
```

### Vector Clocks

```
Node A's version: {A:2, B:1}
Node B's version: {A:1, B:3}

Neither dominates → CONFLICT → Application must resolve
```

### CRDTs (Conflict-Free Replicated Data Types)

Data structures that merge automatically without conflicts:

```
G-Counter (Grow-only counter):
  Node A: {A: 5, B: 0}
  Node B: {A: 3, B: 7}
  Merge:  {A: 5, B: 7} → Total: 12 (max per node)

OR-Set (Observed-Remove Set):
  Allows both add and remove without conflicts
  
LWW-Register:
  Last write wins based on timestamp
```

## Distributed Transactions

### Two-Phase Commit (2PC)

```
Phase 1 (Prepare):
  Coordinator → Participants: "Can you commit?"
  Participants → Coordinator: "Yes" / "No"

Phase 2 (Commit/Abort):
  If all "Yes" → Coordinator: "COMMIT"
  If any "No"  → Coordinator: "ABORT"
```

**Problem**: Coordinator is SPOF. If coordinator crashes after Phase 1, participants are stuck.

### Saga Pattern (Better for Microservices)

```
Choreography (event-driven):
  Order Created → Payment Charged → Inventory Reserved → Shipping Started
  If Payment fails → Compensating: Cancel Order

Orchestration (central coordinator):
  Saga Orchestrator:
    1. Create Order → success
    2. Charge Payment → success
    3. Reserve Inventory → FAIL
    4. Compensate: Refund Payment
    5. Compensate: Cancel Order
```

## Practical Consistency Decision Guide

```
Use Strong Consistency (CP):
✅ Financial transactions (bank transfers)
✅ Inventory management (prevent overselling)
✅ User authentication (password changes)
✅ Distributed locks

Use Eventual Consistency (AP):
✅ Social media feeds (posts, likes, comments)
✅ Analytics / metrics
✅ Shopping cart (low-stakes temporary state)
✅ DNS propagation
✅ Email delivery

Use Causal Consistency:
✅ Messaging / chat (message order matters)
✅ Comment threads (replies follow comments)
✅ Collaborative editing
```

## Key Takeaways

1. **CAP: Choose CP or AP** — partitions are inevitable, P is mandatory
2. **Eventual consistency is a spectrum** — from milliseconds to minutes
3. **Tunable consistency** (W+R>N) lets you choose per-query
4. **CRDTs** solve conflicts without coordination — excellent for AP systems
5. **Saga pattern** replaces distributed transactions in microservices
6. **Strong consistency is expensive** — only use where business requires it
