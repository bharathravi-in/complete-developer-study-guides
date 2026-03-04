# Day 10: Database Architecture

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. SQL vs NoSQL
- [ ] Understand differences
- [ ] Know when to use each

#### SQL Databases

```
┌─────────────────────────────────────────────────────────────────┐
│  Relational Database (SQL)                                       │
│                                                                 │
│  Users Table           Orders Table                             │
│  ┌──────┬───────┐     ┌──────┬─────────┬────────┐              │
│  │ id   │ name  │     │ id   │ user_id │ total  │              │
│  ├──────┼───────┤     ├──────┼─────────┼────────┤              │
│  │ 1    │ John  │◄────│ 101  │    1    │ $50.00 │              │
│  │ 2    │ Jane  │     │ 102  │    2    │ $75.00 │              │
│  └──────┴───────┘     └──────┴─────────┴────────┘              │
│                                                                 │
│  Features: ACID, Joins, Schema enforcement                     │
└─────────────────────────────────────────────────────────────────┘
```

**Examples:** PostgreSQL, MySQL, Oracle, SQL Server

**Use When:**
- Complex queries and joins needed
- Strong consistency required
- Data integrity is critical
- Structured, predictable data

---

#### NoSQL Databases

```
┌─────────────────────────────────────────────────────────────────┐
│  Document Database (MongoDB)                                     │
│                                                                 │
│  {                                                              │
│    "_id": "user_1",                                             │
│    "name": "John",                                              │
│    "orders": [                                                  │
│      { "id": "101", "total": 50.00 },                          │
│      { "id": "103", "total": 25.00 }                           │
│    ],                                                           │
│    "preferences": {                                             │
│      "theme": "dark",                                           │
│      "notifications": true                                      │
│    }                                                            │
│  }                                                              │
│                                                                 │
│  Features: Flexible schema, horizontal scaling, denormalized   │
└─────────────────────────────────────────────────────────────────┘
```

**Types of NoSQL:**

| Type | Examples | Use Case |
|------|----------|----------|
| **Document** | MongoDB, CouchDB | Flexible schema, nested data |
| **Key-Value** | Redis, DynamoDB | Simple lookups, caching |
| **Column-Family** | Cassandra, HBase | Write-heavy, time series |
| **Graph** | Neo4j, Neptune | Relationships, social networks |

#### Comparison

| Aspect | SQL | NoSQL |
|--------|-----|-------|
| Schema | Fixed | Flexible |
| Scaling | Vertical | Horizontal |
| Joins | Native | Manual/Limited |
| ACID | Full | Partial/None |
| Best For | Complex queries | Simple queries at scale |

---

### 2. Read Replicas
- [ ] Understand replication
- [ ] Know replication lag

```
┌─────────────────────────────────────────────────────────────────────┐
│  Read Replica Architecture                                           │
│                                                                     │
│                        ┌─────────────────┐                         │
│     Writes ──────────► │    Primary      │                         │
│                        │   (Master)      │                         │
│                        └────────┬────────┘                         │
│                                 │                                   │
│                        Async Replication                           │
│                                 │                                   │
│          ┌──────────────────────┼──────────────────────┐           │
│          │                      │                      │           │
│          ▼                      ▼                      ▼           │
│   ┌──────────────┐       ┌──────────────┐       ┌──────────────┐   │
│   │   Replica 1  │       │   Replica 2  │       │   Replica 3  │   │
│   │   (Read)     │       │   (Read)     │       │   (Read)     │   │
│   └──────────────┘       └──────────────┘       └──────────────┘   │
│          ▲                      ▲                      ▲           │
│          │                      │                      │           │
│          └──────────────────────┼──────────────────────┘           │
│                                 │                                   │
│     Reads ◄─────────────────────┘                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- Scale read traffic
- Geographic distribution
- Failover capability

**Challenges:**
- Replication lag
- Eventual consistency
- Read-after-write issues

---

### 3. Indexing
- [ ] Understand index types
- [ ] Know indexing strategies

```
Without Index:                    With Index:
┌──────────────────────┐         ┌──────────────────────┐
│ Full Table Scan      │         │ Index Lookup         │
│                      │         │                      │
│ O(n) - Check every   │         │ O(log n) - B-Tree    │
│ row                  │         │ lookup               │
│                      │         │                      │
│ SELECT * FROM users  │         │ SELECT * FROM users  │
│ WHERE email = 'x'    │         │ WHERE email = 'x'    │
│                      │         │                      │
│ Time: 100ms          │         │ Time: 1ms            │
└──────────────────────┘         └──────────────────────┘
```

**Index Types:**

| Type | Description | Use Case |
|------|-------------|----------|
| **B-Tree** | Balanced tree, default | Equality, range queries |
| **Hash** | Hash table | Equality only |
| **GIN** | Generalized Inverted | Full-text, arrays |
| **GiST** | Generalized Search Tree | Geometric, full-text |
| **Composite** | Multiple columns | Multi-column queries |
| **Partial** | Subset of rows | Filtered queries |

**Indexing Best Practices:**
```sql
-- Good: Composite index matching query pattern
CREATE INDEX idx_user_status_date ON orders(user_id, status, created_at);
-- Query: SELECT * FROM orders WHERE user_id = 1 AND status = 'active' ORDER BY created_at

-- Avoid over-indexing (slows writes)
-- Index columns in WHERE, JOIN, ORDER BY
-- Consider column cardinality
```

---

### 4. Caching Layers
- [ ] Understand caching strategies
- [ ] Know cache patterns

```
┌─────────────────────────────────────────────────────────────────────┐
│  Multi-Layer Caching                                                 │
│                                                                     │
│   Client                                                            │
│      │                                                              │
│      ▼                                                              │
│   ┌──────────────┐                                                  │
│   │  Browser     │  Layer 1: Client-side cache                     │
│   │  Cache       │                                                  │
│   └──────┬───────┘                                                  │
│          │                                                          │
│   ┌──────▼───────┐                                                  │
│   │     CDN      │  Layer 2: Edge caching                          │
│   │   (Static)   │                                                  │
│   └──────┬───────┘                                                  │
│          │                                                          │
│   ┌──────▼───────┐                                                  │
│   │  API Gateway │  Layer 3: API response caching                  │
│   │    Cache     │                                                  │
│   └──────┬───────┘                                                  │
│          │                                                          │
│   ┌──────▼───────┐                                                  │
│   │    Redis     │  Layer 4: Application cache                     │
│   │  (In-Memory) │                                                  │
│   └──────┬───────┘                                                  │
│          │                                                          │
│   ┌──────▼───────┐                                                  │
│   │   Database   │  Layer 5: DB query cache                        │
│   │    Cache     │                                                  │
│   └──────┬───────┘                                                  │
│          │                                                          │
│   ┌──────▼───────┐                                                  │
│   │   Database   │  Source of truth                                │
│   └──────────────┘                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📘 Advanced Topics

### CQRS (Command Query Responsibility Segregation)
- [ ] Understand CQRS pattern
- [ ] Know when to use

```
┌───────────────────────────────────────────────────────────────────────┐
│  CQRS Architecture                                                     │
│                                                                       │
│          Commands (Write)              Queries (Read)                 │
│               │                             │                         │
│               ▼                             ▼                         │
│   ┌───────────────────┐         ┌───────────────────┐                │
│   │ Command Handler   │         │  Query Handler    │                │
│   │ (Validation,      │         │  (Simple reads)   │                │
│   │  Business Logic)  │         │                   │                │
│   └─────────┬─────────┘         └─────────┬─────────┘                │
│             │                             │                          │
│             ▼                             ▼                          │
│   ┌───────────────────┐         ┌───────────────────┐                │
│   │   Write Model     │  Sync   │   Read Model      │                │
│   │   (Normalized)    │ ──────► │  (Denormalized)   │                │
│   │   PostgreSQL      │  Event  │     MongoDB       │                │
│   └───────────────────┘         └───────────────────┘                │
└───────────────────────────────────────────────────────────────────────┘
```

**Use When:**
- Read/write workloads differ significantly
- Complex read queries
- Different scaling needs

---

### Database Per Service

```
┌─────────────────────────────────────────────────────────────────────┐
│  Microservices with Database Per Service                            │
│                                                                     │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐      │
│   │  User Service │    │ Order Service │    │Product Service│      │
│   └───────┬───────┘    └───────┬───────┘    └───────┬───────┘      │
│           │                    │                    │               │
│           ▼                    ▼                    ▼               │
│   ┌───────────────┐    ┌───────────────┐    ┌───────────────┐      │
│   │  PostgreSQL   │    │     MySQL     │    │   MongoDB     │      │
│   │   (Users)     │    │   (Orders)    │    │  (Products)   │      │
│   └───────────────┘    └───────────────┘    └───────────────┘      │
│                                                                     │
│   Benefits:                                                         │
│   • Independent scaling                                             │
│   • Technology freedom                                              │
│   • Loose coupling                                                  │
│                                                                     │
│   Challenges:                                                       │
│   • Cross-service joins                                             │
│   • Distributed transactions                                        │
│   • Data consistency                                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

### Polyglot Persistence

```
┌─────────────────────────────────────────────────────────────────────┐
│  E-Commerce Platform - Polyglot Persistence                          │
│                                                                     │
│   Use Case              Database Choice         Reason              │
│   ─────────────────────────────────────────────────────────────────│
│   User accounts         PostgreSQL              ACID, relations     │
│   Product catalog       MongoDB                 Flexible schema     │
│   Shopping cart         Redis                   Speed, TTL          │
│   User sessions         Redis                   Fast lookups        │
│   Search                Elasticsearch           Full-text search    │
│   Analytics             Cassandra               Time-series writes  │
│   Recommendations       Neo4j                   Graph relationships │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Practice Task

### Design Database Architecture

**Instructions:**
1. Design database architecture for a social media platform
2. Consider: Users, Posts, Comments, Likes, Followers
3. Decide SQL vs NoSQL for each entity
4. Design indexes
5. Plan caching strategy

**Template:**

```markdown
## Social Media Database Architecture

### Data Model

#### Entities
| Entity | Database | Reason |
|--------|----------|--------|
| Users | | |
| Posts | | |
| Comments | | |
| Likes | | |
| Followers | | |

### Indexing Strategy
[Describe indexes for each table]

### Caching Strategy
[Describe what to cache and TTL]

### Scaling Plan
[How to scale each component]
```

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] Designing Data-Intensive Applications - Ch. 2, 3
- [ ] [Use The Index, Luke](https://use-the-index-luke.com/)
- [ ] [MongoDB Schema Design](https://www.mongodb.com/docs/manual/core/data-modeling-introduction/)

---

## ✅ Completion Checklist

- [ ] Understood SQL vs NoSQL trade-offs
- [ ] Know replication strategies
- [ ] Mastered indexing
- [ ] Understand caching layers
- [ ] Know CQRS pattern
- [ ] Completed practice task

**Date Completed:** _____________
