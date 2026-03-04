# Day 17: High Availability (HA)

## 📚 Learning Objectives
- Understand HA concepts and patterns
- Configure Patroni for automatic failover
- Set up PgBouncer for connection pooling
- Design HA architectures

---

## 1. HA Fundamentals

### Why High Availability?

```
Single Server Problem:
┌──────────────┐
│   Primary    │ ← Single Point of Failure!
│  PostgreSQL  │
└──────────────┘
      ↓
   Server Dies
      ↓
  💀 Downtime!

HA Solution:
┌──────────────┐     ┌──────────────┐
│   Primary    │────▶│   Replica    │
│  PostgreSQL  │ WAL │  PostgreSQL  │
└──────────────┘     └──────────────┘
      ↓                    ↓
   Server Dies        Auto-Promote!
      ↓                    ↓
  ✓ No Downtime     New Primary!
```

### HA Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| **RTO** | Recovery Time Objective - Max downtime | < 30 seconds |
| **RPO** | Recovery Point Objective - Max data loss | 0 (synchronous) |
| **Availability** | Uptime percentage | 99.99% = 52.6 min/year |

---

## 2. Streaming Replication HA

### Basic Setup

```
┌─────────────────────────────────────────────────────────────┐
│                        Load Balancer                         │
│                    (HAProxy/pgpool-II)                      │
└───────────────────────────┬─────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ Primary  │─────▶│ Replica1 │      │ Replica2 │
    │          │ WAL  │  (sync)  │      │ (async)  │
    └──────────┘      └──────────┘      └──────────┘
```

### Synchronous Replication

```sql
-- On Primary (postgresql.conf)
synchronous_standby_names = 'FIRST 1 (replica1, replica2)'

-- Modes:
-- FIRST N (list): At least N replicas must ACK
synchronous_standby_names = 'FIRST 2 (r1, r2, r3)'

-- ANY N (list): Any N from list
synchronous_standby_names = 'ANY 1 (r1, r2)'

-- Check sync status
SELECT application_name, sync_state, sent_lsn, replay_lsn
FROM pg_stat_replication;

-- sync_state: async, sync, potential, quorum
```

---

## 3. Patroni: Automatic Failover

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Distributed Consensus                     │
│              (etcd / Consul / ZooKeeper)                    │
└───────────────────────────┬─────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │ Patroni  │      │ Patroni  │      │ Patroni  │
    │    +     │      │    +     │      │    +     │
    │  PG1     │      │  PG2     │      │  PG3     │
    │(Leader)  │      │(Replica) │      │(Replica) │
    └──────────┘      └──────────┘      └──────────┘
```

### Patroni Configuration

```yaml
# /etc/patroni/patroni.yml
scope: my-cluster
namespace: /db/
name: node1

restapi:
  listen: 0.0.0.0:8008
  connect_address: node1:8008

etcd:
  hosts: etcd1:2379,etcd2:2379,etcd3:2379

bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576  # 1MB
    postgresql:
      use_pg_rewind: true
      parameters:
        max_connections: 200
        shared_buffers: 2GB
        
  initdb:
    - encoding: UTF8
    - data-checksums

postgresql:
  listen: 0.0.0.0:5432
  connect_address: node1:5432
  data_dir: /var/lib/postgresql/data
  authentication:
    replication:
      username: replicator
      password: secret
    superuser:
      username: postgres
      password: secret
```

### Patroni Operations

```bash
# Check cluster status
patronictl -c /etc/patroni/patroni.yml list

# Output:
# +--------+--------+----------------+--------+---------+----+-----------+
# | Member | Host   | Role           | State  | TL      | Lag| Tags      |
# +--------+--------+----------------+--------+---------+----+-----------+
# | node1  | node1  | Leader         | running| 5       |    |           |
# | node2  | node2  | Sync Standby   | running| 5       | 0  |           |
# | node3  | node3  | Replica        | running| 5       | 0  |           |
# +--------+--------+----------------+--------+---------+----+-----------+

# Manual switchover (planned)
patronictl switchover --master node1 --candidate node2 --scheduled now

# Failover (force)
patronictl failover my-cluster

# Reinitialize failed node
patronictl reinit my-cluster node1

# Pause/Resume auto-failover
patronictl pause my-cluster
patronictl resume my-cluster

# Edit dynamic config
patronictl edit-config my-cluster
```

---

## 4. HAProxy Load Balancing

### Configuration

```haproxy
# /etc/haproxy/haproxy.cfg
global
    maxconn 1000

defaults
    mode tcp
    timeout connect 10s
    timeout client 30m
    timeout server 30m

# Write endpoint (primary only)
listen postgresql-write
    bind *:5432
    option httpchk GET /primary
    http-check expect status 200
    default-server inter 3s fall 3 rise 2
    server node1 node1:5432 check port 8008
    server node2 node2:5432 check port 8008
    server node3 node3:5432 check port 8008

# Read endpoint (all replicas)
listen postgresql-read
    bind *:5433
    balance roundrobin
    option httpchk GET /replica
    http-check expect status 200
    default-server inter 3s fall 3 rise 2
    server node1 node1:5432 check port 8008
    server node2 node2:5432 check port 8008
    server node3 node3:5432 check port 8008

# Stats page
listen stats
    bind *:7000
    mode http
    stats enable
    stats uri /
```

### Application Connection

```python
# Connect via HAProxy
import psycopg2

# For writes
write_conn = psycopg2.connect(
    host="haproxy.example.com",
    port=5432,          # Write port
    database="mydb"
)

# For reads
read_conn = psycopg2.connect(
    host="haproxy.example.com", 
    port=5433,          # Read port
    database="mydb"
)
```

---

## 5. Failover Scenarios

### Automatic Failover Flow

```
1. Primary Fails
       ↓
2. Patroni detects (health check)
       ↓
3. Patroni releases leader key (etcd)
       ↓
4. Remaining nodes race for leader key
       ↓
5. Node with least lag wins
       ↓
6. Winner promotes to primary
       ↓
7. Other replicas follow new primary
       ↓
8. HAProxy health checks detect change
       ↓
9. Traffic routes to new primary

Timeline: ~10-30 seconds
```

### Split-Brain Prevention

```yaml
# Patroni prevents split-brain using:
# 1. Distributed consensus (etcd quorum)
# 2. Leader key with TTL
# 3. Fencing - old primary demotes itself

# postgresql.conf safety
primary_conninfo = 'host=...'
primary_slot_name = 'slot_name'
# If can't reach primary, demote
recovery_target_timeline = 'latest'
```

---

## 6. PgBouncer Setup

### Configuration

```ini
# /etc/pgbouncer/pgbouncer.ini
[databases]
mydb = host=haproxy.example.com port=5432 dbname=mydb

[pgbouncer]
listen_addr = *
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 5
reserve_pool_size = 5
server_idle_timeout = 600
```

### Full HA Architecture

```
                    ┌─────────────────┐
                    │   Application   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    PgBouncer    │
                    │  (Pool Conns)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     HAProxy     │
                    │ (Health Check)  │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐      ┌─────▼─────┐      ┌─────▼─────┐
    │  Patroni  │      │  Patroni  │      │  Patroni  │
    │     +     │      │     +     │      │     +     │
    │  PG Node1 │──────│  PG Node2 │──────│  PG Node3 │
    │ (Primary) │ WAL  │ (Replica) │ WAL  │ (Replica) │
    └───────────┘      └───────────┘      └───────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                    ┌────────▼────────┐
                    │      etcd       │
                    │   (Consensus)   │
                    └─────────────────┘
```

---

## 📝 Key Takeaways

1. **Use distributed consensus** - etcd/Consul for leader election
2. **Patroni automates failover** - Handles promotion, replication
3. **HAProxy routes traffic** - Health checks determine primary
4. **PgBouncer pools connections** - Reduces connection overhead
5. **Synchronous for RPO=0** - Trade latency for durability

---

## ✅ Day 17 Checklist

- [ ] Set up multi-node streaming replication
- [ ] Configure Patroni cluster
- [ ] Practice manual switchover
- [ ] Test automatic failover
- [ ] Configure HAProxy load balancing
- [ ] Understand split-brain prevention
