# Day 21: Connection Pooling (PgBouncer Deep Dive)

## 📚 Learning Objectives
- Understand why connection pooling matters
- Master PgBouncer configuration
- Compare pooling modes
- Implement connection pooling in applications

---

## 1. Why Connection Pooling?

### The Problem

```
Without Pooling:
┌─────────────┐     ┌─────────────┐
│   App       │───1000 connections──▶│ PostgreSQL  │
│ (1000 users)│                      │(1000 backends)│
└─────────────┘                      └─────────────┘
                                           ↓
                                     Memory: 10GB+
                                     Context switches: High
                                     Performance: Poor

Each PostgreSQL connection:
- ~10MB RAM per connection
- fork() overhead
- Process context switching
```

### The Solution

```
With Pooling:
┌─────────────┐     ┌───────────┐     ┌─────────────┐
│   App       │────▶│ PgBouncer │────▶│ PostgreSQL  │
│(1000 users) │     │ (Pooler)  │     │ (50 backends)│
└─────────────┘     └───────────┘     └─────────────┘
     1000              Multiplexes          50
   connections         connections      connections
                                            ↓
                                     Memory: 500MB
                                     Performance: Great
```

---

## 2. PgBouncer Configuration

### Basic Setup

```ini
# /etc/pgbouncer/pgbouncer.ini

;; Database connections
[databases]
; dbname = connection string
mydb = host=localhost port=5432 dbname=mydb
; With specific user
analytics = host=db.example.com dbname=analytics user=analyst

; Wildcard (any database)
* = host=localhost port=5432

;; PgBouncer settings
[pgbouncer]
; Admin interface
listen_addr = 0.0.0.0
listen_port = 6432
admin_users = pgbouncer_admin
stats_users = pgbouncer_stats

; Authentication
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

; Pooling mode
pool_mode = transaction

; Connection limits
max_client_conn = 1000
default_pool_size = 25
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3

; Timeouts
server_idle_timeout = 600
client_idle_timeout = 0
client_login_timeout = 60
query_timeout = 0
query_wait_timeout = 120

; Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1

; TLS (optional)
;client_tls_sslmode = require
;client_tls_cert_file = /path/to/client.crt
;client_tls_key_file = /path/to/client.key
```

### User Authentication

```bash
# /etc/pgbouncer/userlist.txt
"myuser" "plain_password"
"myuser" "md5" + md5(password + username)

# Generate MD5 hash
echo -n "passwordmyuser" | md5sum
# Output: abc123... (prefix with "md5")

# Or use auth_query for dynamic lookup
# In pgbouncer.ini:
auth_query = SELECT usename, passwd FROM pg_shadow WHERE usename=$1
```

---

## 3. Pool Modes

### Session Pooling

```
┌──────────────────────────────────────────────────────────┐
│                    SESSION MODE                           │
├──────────────────────────────────────────────────────────┤
│ Client connects → Gets dedicated server connection       │
│ Holds connection until client disconnects                │
│                                                          │
│ Client 1 ──────────────────────────▶ Server Conn 1      │
│ Client 2 ──────────────────────────▶ Server Conn 2      │
│                                                          │
│ + Supports ALL PostgreSQL features                       │
│ + LISTEN/NOTIFY, Prepared statements, Session variables  │
│ - Poor multiplexing (1:1)                               │
└──────────────────────────────────────────────────────────┘

pool_mode = session
```

### Transaction Pooling

```
┌──────────────────────────────────────────────────────────┐
│                   TRANSACTION MODE                        │
├──────────────────────────────────────────────────────────┤
│ Client gets connection only during transaction           │
│ Connection returned to pool after COMMIT/ROLLBACK        │
│                                                          │
│ Client 1 ─TX1─▶ Server 1 ─(return)                      │
│           └TX2─▶ Server 2 ─(return)                      │
│ Client 2 ─TX3─▶ Server 1 ─(returned to pool)            │
│                                                          │
│ + Great multiplexing                                     │
│ - No session features (prepared statements, SET, etc.)   │
│ - LISTEN/NOTIFY won't work                              │
└──────────────────────────────────────────────────────────┘

pool_mode = transaction
```

### Statement Pooling

```
┌──────────────────────────────────────────────────────────┐
│                    STATEMENT MODE                         │
├──────────────────────────────────────────────────────────┤
│ Connection returned after EVERY statement                │
│ Forces autocommit (no multi-statement transactions)      │
│                                                          │
│ Client 1 ─SELECT─▶ Server 1 ─(return)                   │
│          ─UPDATE─▶ Server 2 ─(return)                   │
│                                                          │
│ + Maximum multiplexing                                   │
│ - Very restrictive                                       │
│ - Best for simple read-heavy workloads                  │
└──────────────────────────────────────────────────────────┘

pool_mode = statement
```

### Mode Comparison

| Feature | Session | Transaction | Statement |
|---------|---------|-------------|-----------|
| Multiplexing | Poor (1:1) | Good | Best |
| `SET` commands | ✓ | ✗ | ✗ |
| Prepared statements | ✓ | ✗* | ✗ |
| `LISTEN/NOTIFY` | ✓ | ✗ | ✗ |
| Multi-statement TX | ✓ | ✓ | ✗ |
| Cursors | ✓ | ✗ | ✗ |
| Temp tables | ✓ | ✓ | ✗ |

*Protocol-level prepared statements work in transaction mode

---

## 4. Application Configuration

### Python with psycopg2

```python
import psycopg2
from psycopg2 import pool

# Connect through PgBouncer
conn = psycopg2.connect(
    host="pgbouncer.example.com",
    port=6432,  # PgBouncer port
    database="mydb",
    user="myuser",
    password="secret",
    # Disable Prepared statements for transaction mode
    prepare_threshold=0
)

# Application-side pooling (on top of PgBouncer)
app_pool = pool.ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    host="pgbouncer.example.com",
    port=6432,
    database="mydb"
)

def execute_query(sql, params):
    conn = app_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            conn.commit()
            return cur.fetchall()
    finally:
        app_pool.putconn(conn)
```

### Node.js with pg

```javascript
const { Pool } = require('pg');

const pool = new Pool({
    host: 'pgbouncer.example.com',
    port: 6432,  // PgBouncer
    database: 'mydb',
    user: 'myuser',
    password: 'secret',
    // Keep application pool small when using PgBouncer
    max: 10,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
});

// Use pool for queries
async function query(text, params) {
    const client = await pool.connect();
    try {
        return await client.query(text, params);
    } finally {
        client.release();
    }
}
```

### SQLAlchemy

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Connect via PgBouncer
engine = create_engine(
    "postgresql://user:pass@pgbouncer:6432/mydb",
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Check connection health
    # For transaction pooling mode
    connect_args={
        "options": "-c statement_timeout=30000"
    },
    # Disable connection-level caching
    execution_options={
        "compiled_cache": None
    }
)

Session = sessionmaker(bind=engine)
```

---

## 5. PgBouncer Administration

### Admin Console

```bash
# Connect to admin console
psql -p 6432 -U pgbouncer_admin pgbouncer

# Show pools
SHOW POOLS;
# database | user | cl_active | cl_waiting | sv_active | sv_idle | sv_used

# Show databases
SHOW DATABASES;

# Show clients
SHOW CLIENTS;

# Show servers (backend connections)
SHOW SERVERS;

# Show stats
SHOW STATS;

# Show config
SHOW CONFIG;

# Reload configuration
RELOAD;

# Pause/resume database
PAUSE mydb;
RESUME mydb;

# Kill a connection
KILL mydb;

# Suspend (graceful pause)
SUSPEND;
```

### Monitoring Queries

```sql
-- Pool utilization
SELECT 
    database,
    user,
    cl_active + cl_waiting AS total_clients,
    sv_active + sv_idle AS total_servers,
    sv_active,
    sv_idle,
    maxwait
FROM SHOW POOLS;

-- Connection wait time
SELECT 
    database,
    total_query_time / 1000 AS query_time_sec,
    total_wait_time / 1000 AS wait_time_sec,
    avg_query_time / 1000 AS avg_query_ms
FROM SHOW STATS;
```

---

## 6. Tuning Guidelines

### Sizing the Pool

```
Rule of thumb:
optimal_pool_size = (core_count * 2) + effective_spindle_count

For SSD (8 cores):
  pool_size = 8 * 2 + 1 = 17 (round to 20)

For HDD RAID (8 cores, 4 drives):
  pool_size = 8 * 2 + 4 = 20

PgBouncer settings:
  default_pool_size = 20
  min_pool_size = 10
  reserve_pool_size = 5
```

### Configuration for Different Workloads

```ini
# Web application (many short transactions)
pool_mode = transaction
default_pool_size = 25
max_client_conn = 5000
server_idle_timeout = 60

# Analytics (long queries)
pool_mode = session
default_pool_size = 50
max_client_conn = 200
server_idle_timeout = 3600

# Mixed workload (separate pools)
[databases]
app = host=pg dbname=mydb pool_mode=transaction pool_size=25
reports = host=pg dbname=mydb pool_mode=session pool_size=10
```

---

## 7. Common Issues

### Prepared Statement Errors

```
ERROR: prepared statement "..." does not exist

Solution: Disable prepared statements or use session mode

# Python
psycopg2.connect(..., prepare_threshold=0)

# Node.js
client.query({ text: sql, values: params })  # Simple query
```

### SET Command Issues

```sql
-- This won't work in transaction mode:
SET timezone = 'UTC';
SELECT now();
-- Connection might change between statements!

-- Solution 1: Use per-query settings
SELECT now() AT TIME ZONE 'UTC';

-- Solution 2: Use connection string
[databases]
mydb = host=pg dbname=mydb options='-c timezone=UTC'
```

### Connection Storms

```ini
# Prevent connection storms
server_login_retry = 5          # Wait before reconnecting
client_login_timeout = 60       # Client connection timeout
query_wait_timeout = 120        # Max wait for server connection

# Rate limiting
max_db_connections = 50         # Per database limit
max_user_connections = 50       # Per user limit
```

---

## 📝 Key Takeaways

1. **Transaction mode for web apps** - Best multiplexing
2. **Session mode for full features** - When you need SET, LISTEN
3. **Keep pool size reasonable** - More isn't always better
4. **Disable prepared statements** - In transaction mode
5. **Monitor wait times** - Indicates pool exhaustion

---

## ✅ Day 21 Checklist

- [ ] Install and configure PgBouncer
- [ ] Test different pool modes
- [ ] Connect application via PgBouncer
- [ ] Monitor using admin console
- [ ] Configure appropriate pool sizes
- [ ] Handle prepared statement issues
