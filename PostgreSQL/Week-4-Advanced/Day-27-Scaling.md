# Day 27: Scaling PostgreSQL

## 📚 Learning Objectives
- Understand scaling strategies
- Implement read replicas
- Design sharding patterns
- Use Citus for distributed PostgreSQL

---

## 1. Scaling Fundamentals

### Vertical vs Horizontal Scaling

```
Vertical Scaling (Scale Up):
┌─────────────────┐
│   PostgreSQL    │
│  ▲ More CPU     │
│  ▲ More RAM     │
│  ▲ Faster SSD   │
└─────────────────┘
Pros: Simple, no code changes
Cons: Hardware limits, single point of failure

Horizontal Scaling (Scale Out):
┌──────────┐ ┌──────────┐ ┌──────────┐
│  Shard 1 │ │  Shard 2 │ │  Shard 3 │
└──────────┘ └──────────┘ └──────────┘
Pros: Near-infinite scale, fault tolerance
Cons: Complex, application changes needed
```

### When to Scale

| Symptom | Possible Solution |
|---------|------------------|
| CPU saturated | Vertical scale, read replicas |
| Memory exhausted | Vertical scale, connection pooling |
| Disk I/O bottleneck | SSD upgrade, read replicas |
| Connection limits | PgBouncer, connection pooling |
| Write bottleneck | Sharding |
| Data too large | Partitioning, sharding |

---

## 2. Read Scaling (Replicas)

### Architecture

```
                    ┌─────────────────┐
                    │   Application   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  Load Balancer  │
                    └────────┬────────┘
          ┌──────────────────┼──────────────────┐
          │                  │                  │
   ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
   │   Primary   │───▶│   Replica1  │    │   Replica2  │
   │  (Writes)   │WAL │   (Reads)   │    │   (Reads)   │
   └─────────────┘    └─────────────┘    └─────────────┘
```

### Application-Level Read/Write Split

```python
# Python example
import psycopg2

class DatabaseRouter:
    def __init__(self):
        self.primary = psycopg2.connect(host="primary.db", dbname="mydb")
        self.replicas = [
            psycopg2.connect(host="replica1.db", dbname="mydb"),
            psycopg2.connect(host="replica2.db", dbname="mydb"),
        ]
        self.replica_idx = 0
    
    def get_write_connection(self):
        return self.primary
    
    def get_read_connection(self):
        # Round-robin
        conn = self.replicas[self.replica_idx]
        self.replica_idx = (self.replica_idx + 1) % len(self.replicas)
        return conn
    
    def execute_read(self, query, params=None):
        conn = self.get_read_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    
    def execute_write(self, query, params=None):
        conn = self.get_write_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
```

### Handling Replication Lag

```python
# Read-your-writes consistency
class SmartRouter:
    def __init__(self):
        self.last_write_lsn = None
        
    def write(self, query, params):
        conn = self.primary
        with conn.cursor() as cur:
            cur.execute(query, params)
            cur.execute("SELECT pg_current_wal_lsn()")
            self.last_write_lsn = cur.fetchone()[0]
        conn.commit()
    
    def read(self, query, params, need_latest=False):
        if need_latest and self.last_write_lsn:
            # Check replica has caught up
            for replica in self.replicas:
                with replica.cursor() as cur:
                    cur.execute("SELECT pg_last_wal_replay_lsn()")
                    replica_lsn = cur.fetchone()[0]
                    if replica_lsn >= self.last_write_lsn:
                        return self.execute_on(replica, query, params)
            # Fallback to primary
            return self.execute_on(self.primary, query, params)
        return self.execute_read(query, params)
```

---

## 3. Sharding Strategies

### Application-Level Sharding

```python
# Shard by user_id
def get_shard(user_id, num_shards=4):
    return user_id % num_shards

class ShardedDatabase:
    def __init__(self):
        self.shards = {
            0: psycopg2.connect(host="shard0.db", dbname="mydb"),
            1: psycopg2.connect(host="shard1.db", dbname="mydb"),
            2: psycopg2.connect(host="shard2.db", dbname="mydb"),
            3: psycopg2.connect(host="shard3.db", dbname="mydb"),
        }
    
    def get_user(self, user_id):
        shard_id = get_shard(user_id)
        conn = self.shards[shard_id]
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            return cur.fetchone()
    
    def get_all_users(self):
        # Fan-out query to all shards
        results = []
        for conn in self.shards.values():
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users")
                results.extend(cur.fetchall())
        return results
```

### Shard Key Selection

```
Good Shard Keys:
✓ user_id - Natural isolation for user data
✓ tenant_id - Multi-tenant SaaS
✓ region_id - Geographic isolation
✓ timestamp (range) - Time-series data

Bad Shard Keys:
✗ Auto-increment ID - Hotspot on latest shard
✗ Boolean fields - Only 2 shards
✗ Low cardinality - Uneven distribution

Considerations:
- Query patterns (avoid cross-shard queries)
- Data distribution (even across shards)
- Growth pattern (easy to add shards)
```

### Rebalancing Shards

```sql
-- Consistent hashing approach
-- Add new shard by only moving portion of data

-- Before: 3 shards (0, 1, 2)
-- id % 3: 0->shard0, 1->shard1, 2->shard2

-- After: 4 shards (0, 1, 2, 3)
-- Need to redistribute ~25% of data

-- Better: Use hash ring (consistent hashing)
-- Virtual nodes per physical shard
-- Adding shard only moves data from neighbors
```

---

## 4. Citus (Distributed PostgreSQL)

### Architecture

```
┌─────────────────────────────────────────────┐
│              Coordinator Node               │
│  (Accepts queries, plans distribution)      │
└──────────────────────┬──────────────────────┘
                       │
     ┌─────────────────┼─────────────────┐
     │                 │                 │
┌────▼────┐      ┌─────▼─────┐     ┌─────▼─────┐
│ Worker1 │      │  Worker2  │     │  Worker3  │
│ Shards  │      │  Shards   │     │  Shards   │
│ 1,4,7   │      │  2,5,8    │     │  3,6,9    │
└─────────┘      └───────────┘     └───────────┘
```

### Setup Citus

```sql
-- On coordinator
CREATE EXTENSION citus;

-- Add worker nodes
SELECT citus_add_node('worker1', 5432);
SELECT citus_add_node('worker2', 5432);
SELECT citus_add_node('worker3', 5432);

-- View cluster
SELECT * FROM citus_get_active_worker_nodes();
```

### Distributed Tables

```sql
-- Create table (on coordinator)
CREATE TABLE events (
    id BIGSERIAL,
    user_id INTEGER NOT NULL,
    event_type TEXT,
    payload JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Distribute table by user_id
SELECT create_distributed_table('events', 'user_id');

-- Inserts automatically routed to correct shard
INSERT INTO events (user_id, event_type, payload)
VALUES (123, 'click', '{"page": "/home"}');

-- Query routed to single shard (efficient)
SELECT * FROM events WHERE user_id = 123;

-- Query all shards (fan-out)
SELECT event_type, COUNT(*) FROM events GROUP BY event_type;
```

### Reference Tables

```sql
-- Small tables replicated to all workers
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    name TEXT,
    code CHAR(2)
);

SELECT create_reference_table('countries');

-- JOINs with reference tables are local (fast)
SELECT e.*, c.name AS country
FROM events e
JOIN countries c ON e.payload->>'country_id' = c.id::text
WHERE e.user_id = 123;
```

### Colocation

```sql
-- Colocate tables that are frequently joined
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total NUMERIC
);

SELECT create_distributed_table('users', 'id');
SELECT create_distributed_table('orders', 'user_id', 
    colocate_with => 'users');

-- JOIN stays on same shard - no network
SELECT u.name, SUM(o.total)
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.id = 123
GROUP BY u.name;
```

---

## 5. Foreign Data Wrappers (FDW)

### postgres_fdw

```sql
-- Connect to remote PostgreSQL
CREATE EXTENSION postgres_fdw;

CREATE SERVER remote_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'remote.db', dbname 'mydb');

CREATE USER MAPPING FOR current_user
SERVER remote_server
OPTIONS (user 'remote_user', password 'secret');

-- Import tables
IMPORT FOREIGN SCHEMA public
FROM SERVER remote_server
INTO local_schema;

-- Or create specific foreign table
CREATE FOREIGN TABLE remote_users (
    id INTEGER,
    name TEXT,
    email TEXT
) SERVER remote_server
OPTIONS (table_name 'users');

-- Query as if local
SELECT * FROM remote_users WHERE id = 123;

-- JOIN local and remote tables
SELECT l.*, r.email
FROM local_orders l
JOIN remote_users r ON l.user_id = r.id;
```

---

## 6. Scaling Patterns Summary

### Pattern Selection Guide

```
┌──────────────────────────────────────────────────────────────┐
│                    Scaling Decision Tree                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Read-heavy?                                                 │
│      │                                                       │
│      ├─Yes─▶ Add Read Replicas                              │
│      │                                                       │
│  Write-heavy?                                                │
│      │                                                       │
│      ├─Yes─▶ Vertical Scale (bigger server)                 │
│      │       └──If still not enough──▶ Sharding             │
│      │                                                       │
│  Data too large for single node?                            │
│      │                                                       │
│      ├─Yes─▶ Partitioning (single node)                     │
│      │       └──If still too large──▶ Sharding              │
│      │                                                       │
│  Need global distribution?                                   │
│      │                                                       │
│      └─Yes─▶ Citus / CockroachDB / Spanner                  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Cost-Benefit Analysis

| Approach | Complexity | Write Scale | Read Scale | Data Size |
|----------|------------|-------------|------------|-----------|
| Vertical | Low | Medium | Medium | Medium |
| Read Replicas | Low | No | High | No |
| Partitioning | Medium | Some | Some | Medium |
| App Sharding | High | High | High | High |
| Citus | Medium | High | High | High |

---

## 📝 Key Takeaways

1. **Start simple** - Vertical scaling, read replicas
2. **Partition before sharding** - Less complex
3. **Shard key is critical** - Determines query efficiency
4. **Citus simplifies sharding** - Transparent distribution
5. **Consider cloud solutions** - AWS Aurora, Azure Hyperscale

---

## ✅ Day 27 Checklist

- [ ] Set up read replicas
- [ ] Implement read/write split in application
- [ ] Design sharding strategy
- [ ] Try Citus distributed tables
- [ ] Use postgres_fdw for federation
- [ ] Understand when to use each approach
