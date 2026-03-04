# Day 9: System Design Core Concepts

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. Consistency Models
- [ ] Understand different consistency levels
- [ ] Know when to choose each

#### Strong Consistency

```
                    ┌─────────────────┐
    Write ─────────►│    Primary      │
                    │   (Leader)      │
                    └────────┬────────┘
                             │
                   Wait for ALL replicas
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │  Replica 1   │ │  Replica 2   │ │  Replica 3   │
     │   ✓ Ack     │ │   ✓ Ack     │ │   ✓ Ack     │
     └──────────────┘ └──────────────┘ └──────────────┘
                             │
                             ▼
    Write confirmed only after ALL replicas acknowledge
```

**Characteristics:**
- Every read returns the most recent write
- Higher latency
- Lower availability during partitions

---

#### Eventual Consistency

```
                    ┌─────────────────┐
    Write ─────────►│    Primary      │◄─── Immediate ACK
                    │   (Leader)      │
                    └────────┬────────┘
                             │
               Async replication (eventually)
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │  Replica 1   │ │  Replica 2   │ │  Replica 3   │
     │  (Stale)     │ │ (Up-to-date) │ │  (Stale)     │
     └──────────────┘ └──────────────┘ └──────────────┘
     
    Read may return stale data temporarily
```

**Characteristics:**
- Lower latency
- Higher availability
- Temporary inconsistency

---

#### Consistency Spectrum

```
Strong ◄─────────────────────────────────────────────► Eventual

Linearizable  Sequential  Causal  Read-your-writes  Eventual
     │            │          │           │             │
     └────────────┴──────────┴───────────┴─────────────┘
           Higher Consistency      Higher Availability
           Higher Latency          Lower Latency
```

| Level | Description | Example |
|-------|-------------|---------|
| **Linearizable** | Strongest, all ops appear atomic | Banking |
| **Sequential** | Ops appear in some total order | Social media posts |
| **Causal** | Cause-effect relationships preserved | Comments |
| **Read-your-writes** | User sees their own writes | Profile updates |
| **Eventual** | All replicas converge eventually | DNS, caches |

---

### 2. ACID vs BASE
- [ ] Understand both models
- [ ] Know when to use each

#### ACID (Traditional Databases)

```
┌─────────────────────────────────────────────────────────────────┐
│  ACID Transaction                                                │
│                                                                 │
│  BEGIN TRANSACTION                                              │
│    ├── Operation 1: Debit $100 from Account A                  │
│    ├── Operation 2: Credit $100 to Account B                   │
│    └── COMMIT (All or Nothing)                                 │
│                                                                 │
│  A - Atomicity:    All operations succeed or all fail         │
│  C - Consistency:  Database moves from valid to valid state   │
│  I - Isolation:    Concurrent transactions don't interfere    │
│  D - Durability:   Committed changes survive failures         │
└─────────────────────────────────────────────────────────────────┘
```

#### BASE (Distributed Systems)

```
┌─────────────────────────────────────────────────────────────────┐
│  BASE Model                                                      │
│                                                                 │
│  BA - Basically Available:                                      │
│       System guarantees availability (may serve stale data)    │
│                                                                 │
│  S  - Soft State:                                               │
│       State may change over time without input                 │
│                                                                 │
│  E  - Eventually Consistent:                                    │
│       System will become consistent given enough time          │
└─────────────────────────────────────────────────────────────────┘
```

#### Comparison

| Property | ACID | BASE |
|----------|------|------|
| Focus | Consistency | Availability |
| Scaling | Vertical | Horizontal |
| Performance | Lower | Higher |
| Complexity | Lower | Higher |
| Use Case | Financial, critical | Social, analytics |

---

### 3. Consistency Patterns
- [ ] Learn practical patterns

#### Two-Phase Commit (2PC)

```
                    ┌─────────────────┐
                    │   Coordinator   │
                    └────────┬────────┘
                             │
      Phase 1: Prepare       │
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    ┌─────────┐         ┌─────────┐         ┌─────────┐
    │ Node A  │         │ Node B  │         │ Node C  │
    │ Vote:YES│         │ Vote:YES│         │ Vote:YES│
    └────┬────┘         └────┬────┘         └────┬────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
      Phase 2: Commit        │
                             ▼
                    ┌─────────────────┐
                    │   COMMIT ALL    │
                    └─────────────────┘
```

**Problems with 2PC:**
- Blocking if coordinator fails
- Poor availability
- Not partition tolerant

---

#### Saga Pattern (Preferred for Microservices)

```
Choreography Saga:
┌─────────┐  OrderCreated  ┌─────────┐  PaymentDone  ┌─────────┐
│  Order  │ ─────────────► │ Payment │ ────────────► │  Ship   │
│ Service │                │ Service │               │ Service │
└────┬────┘                └────┬────┘               └─────────┘
     │                          │
     │    PaymentFailed         │
     │◄─────────────────────────┘
     │
     ▼
  Cancel Order (Compensating Transaction)
```

---

### 4. Sharding (Partitioning)
- [ ] Understand sharding strategies
- [ ] Know challenges and solutions

```
                    ┌─────────────────────────┐
                    │      Shard Router       │
                    │   (Determines shard)    │
                    └───────────┬─────────────┘
                                │
           ┌────────────────────┼────────────────────┐
           │                    │                    │
           ▼                    ▼                    ▼
    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
    │   Shard 1    │     │   Shard 2    │     │   Shard 3    │
    │  (0-1000)    │     │ (1001-2000)  │     │ (2001-3000)  │
    └──────────────┘     └──────────────┘     └──────────────┘
```

#### Sharding Strategies

| Strategy | Description | Pros/Cons |
|----------|-------------|-----------|
| **Range** | Based on key ranges | Easy to implement, hotspots |
| **Hash** | Hash of key | Even distribution, no range queries |
| **Directory** | Lookup table | Flexible, single point of failure |
| **Geographic** | By location | Data locality, complex |

#### Consistent Hashing

```
                        ┌──────────────────────┐
                        │   Hash Ring          │
                        │                      │
                        │        N1            │
                        │      /    \          │
                        │     /      \         │
                        │   N4        N2       │
                        │     \      /         │
                        │      \    /          │
                        │        N3            │
                        │                      │
                        └──────────────────────┘

When N2 is removed, only data between N1 and N2 moves to N3
(Minimal redistribution!)
```

---

### 5. Partitioning
- [ ] Understand data partitioning
- [ ] Know horizontal vs vertical

#### Horizontal Partitioning (Sharding)

```
Original Table:                 After Horizontal Partitioning:
┌─────────────────────┐         ┌──────────────┐  ┌──────────────┐
│ id │ name   │ city  │         │ Partition 1  │  │ Partition 2  │
├────┼────────┼───────┤         │ (id 1-1000)  │  │ (id 1001+)   │
│ 1  │ John   │ NYC   │         ├──────────────┤  ├──────────────┤
│ 2  │ Jane   │ LA    │   ──►   │ 1│John│NYC   │  │1001│Bob│CHI  │
│... │ ...    │ ...   │         │ 2│Jane│LA    │  │1002│Sue│MIA  │
│1001│ Bob    │ CHI   │         └──────────────┘  └──────────────┘
│1002│ Sue    │ MIA   │
└─────────────────────┘
```

#### Vertical Partitioning

```
Original Table:                 After Vertical Partitioning:
┌─────────────────────────────┐ ┌──────────────┐  ┌──────────────┐
│ id │ name │ email  │ bio    │ │ Core Table   │  │ Extended     │
├────┼──────┼────────┼────────┤ ├──────────────┤  ├──────────────┤
│ 1  │ John │ j@x.co │ Long...│ │ 1│John│j@x.co│  │ 1 │Long bio..│
│ 2  │ Jane │ a@y.co │ Long...│ │ 2│Jane│a@y.co│  │ 2 │Long bio..│
└─────────────────────────────┘ └──────────────┘  └──────────────┘
                                (Frequently used)  (Rarely used)
```

---

## 🎯 Practice Task

### Design Data Strategy

**Instructions:**
1. Given a user database with 100M users
2. Design sharding strategy
3. Handle cross-shard queries
4. Plan for growth

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] Designing Data-Intensive Applications - Ch. 5, 6
- [ ] [Consistency Models](https://jepsen.io/consistency)
- [ ] [Database Partitioning](https://docs.aws.amazon.com/prescriptive-guidance/latest/modernization-data-persistence/data-partitioning-sharding.html)

---

## ✅ Completion Checklist

- [ ] Understood consistency models
- [ ] Know ACID vs BASE
- [ ] Mastered sharding strategies
- [ ] Understand partitioning approaches
- [ ] Know consistent hashing

**Date Completed:** _____________
