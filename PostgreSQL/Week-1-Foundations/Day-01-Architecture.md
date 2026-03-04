# Day 1: PostgreSQL Architecture

## 📚 Learning Objectives
- Understand PostgreSQL history and ecosystem
- Learn client-server architecture
- Understand process model
- Explore data directory structure
- Navigate system catalogs

---

## 1. PostgreSQL History & Ecosystem

### Brief History
- **1986**: POSTGRES project started at UC Berkeley by Professor Michael Stonebraker
- **1996**: Renamed to PostgreSQL with SQL support
- **2024**: PostgreSQL 17 released with major performance improvements

### Why PostgreSQL?
- **ACID Compliant**: Full transaction support
- **Extensible**: Custom functions, data types, operators
- **Standards Compliant**: Most SQL-compliant open-source database
- **Mature**: 35+ years of active development
- **Enterprise Ready**: Used by Apple, Instagram, Spotify, Netflix

### Comparison with Other RDBMS

| Feature | PostgreSQL | MySQL | Oracle |
|---------|------------|-------|--------|
| MVCC | ✅ Native | ✅ InnoDB only | ✅ |
| JSON Support | ✅ JSONB | ✅ JSON | ✅ |
| Full-Text Search | ✅ Built-in | ✅ Limited | ✅ |
| Partitioning | ✅ Native | ✅ | ✅ |
| Cost | Free | Free/Paid | Paid |
| License | PostgreSQL | GPL/Commercial | Commercial |

---

## 2. Client-Server Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT APPLICATIONS                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │
│  │  psql   │  │  pgAdmin │  │  App    │  │  JDBC   │        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘        │
└───────┼────────────┼────────────┼────────────┼──────────────┘
        │            │            │            │
        └────────────┴─────┬──────┴────────────┘
                           │ TCP/IP or Unix Socket
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    POSTGRESQL SERVER                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    POSTMASTER                         │   │
│  │              (Main Server Process)                    │   │
│  └──────────────────────────────────────────────────────┘   │
│              │                     │                         │
│              ▼                     ▼                         │
│  ┌─────────────────┐    ┌─────────────────────────────┐    │
│  │ Backend Process │    │   Background Workers        │    │
│  │ (per connection)│    │ - WAL Writer                │    │
│  └─────────────────┘    │ - Background Writer         │    │
│                         │ - Checkpointer              │    │
│                         │ - Autovacuum                │    │
│                         │ - Stats Collector           │    │
│                         └─────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Connection Flow
1. Client sends connection request
2. Postmaster accepts connection
3. Postmaster forks a new backend process
4. Backend process handles all client queries
5. Connection closed → backend process terminates

---

## 3. Process Model

### Main Processes

#### Postmaster (postgres)
```bash
# View postmaster process
ps aux | grep postgres | grep -v grep
```
- **Role**: Main supervisor process
- **Listens**: For incoming connections
- **Spawns**: Backend processes for each connection
- **Manages**: Shared memory, semaphores

#### Backend Processes
- One per client connection
- Handles SQL parsing, planning, execution
- Accesses shared buffers
- Writes to WAL

#### Background Workers

| Process | Function |
|---------|----------|
| **WAL Writer** | Flushes WAL buffers to disk |
| **Background Writer** | Writes dirty buffers to disk |
| **Checkpointer** | Creates checkpoints for recovery |
| **Autovacuum Launcher** | Manages autovacuum workers |
| **Stats Collector** | Collects database statistics |
| **Logical Replication Launcher** | Manages logical replication |

```bash
# View all PostgreSQL processes
ps aux | grep postgres

# Output example:
# postgres   1234  postmaster
# postgres   1235  checkpointer
# postgres   1236  background writer
# postgres   1237  walwriter
# postgres   1238  autovacuum launcher
# postgres   1239  stats collector
```

---

## 4. Memory Architecture

```
┌────────────────────────────────────────────────────────────┐
│                    SHARED MEMORY                            │
│  ┌────────────────┐  ┌─────────────┐  ┌─────────────────┐  │
│  │ Shared Buffers │  │  WAL Buffers │  │ Commit Log      │  │
│  │ (Data Cache)   │  │              │  │ (CLOG)          │  │
│  └────────────────┘  └─────────────┘  └─────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Lock Tables & Other Structures            │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│              PROCESS LOCAL MEMORY (per backend)             │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────────┐  │
│  │  work_mem    │  │ maintenance_  │  │  temp_buffers   │  │
│  │ (sorts,hash) │  │   work_mem    │  │                 │  │
│  └──────────────┘  └───────────────┘  └─────────────────┘  │
└────────────────────────────────────────────────────────────┘
```

### Key Memory Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `shared_buffers` | 128MB | Shared memory for caching data |
| `work_mem` | 4MB | Memory for sorts, hashes (per operation) |
| `maintenance_work_mem` | 64MB | Memory for maintenance operations |
| `effective_cache_size` | 4GB | Planner's assumption of disk cache |

---

## 5. Data Directory Structure

```bash
# Find data directory
SHOW data_directory;
# or
sudo -u postgres psql -c "SHOW data_directory;"
```

### Typical Location
- **Debian/Ubuntu**: `/var/lib/postgresql/{version}/main/`
- **RHEL/CentOS**: `/var/lib/pgsql/{version}/data/`
- **macOS (Homebrew)**: `/usr/local/var/postgres/`

### Directory Breakdown

```
$PGDATA/
├── base/                    # Database files
│   ├── 1/                   # template1 database
│   ├── 13067/               # template0 database
│   └── 16384/               # User databases (OID)
├── global/                  # Cluster-wide tables
│   ├── pg_control           # Control file
│   └── pg_database          # Database catalog
├── pg_wal/                  # Write-Ahead Logs
│   └── 000000010000000000000001
├── pg_xact/                 # Transaction commit status (CLOG)
├── pg_multixact/            # Multitransaction status
├── pg_subtrans/             # Subtransaction status
├── pg_twophase/             # Two-phase commit state
├── pg_stat/                 # Statistics files
├── pg_stat_tmp/             # Temporary statistics
├── pg_replslot/             # Replication slots
├── pg_tblspc/               # Tablespace symlinks
├── pg_logical/              # Logical replication
├── pg_commit_ts/            # Commit timestamps
├── pg_notify/               # LISTEN/NOTIFY data
├── pg_serial/               # Serializable transaction info
├── pg_snapshots/            # Exported snapshots
├── pg_dynshmem/             # Dynamic shared memory
├── postgresql.conf          # Main configuration
├── postgresql.auto.conf     # Auto-generated config
├── pg_hba.conf              # Host-based authentication
├── pg_ident.conf            # Ident authentication mapping
├── PG_VERSION               # PostgreSQL version
├── postmaster.opts          # Command line options
└── postmaster.pid           # PID file
```

---

## 6. Configuration Files

### pg_hba.conf (Host-Based Authentication)

```bash
# Location
SHOW hba_file;
```

```conf
# TYPE  DATABASE    USER        ADDRESS         METHOD

# Local connections
local   all         postgres                    peer
local   all         all                         peer

# IPv4 local connections
host    all         all         127.0.0.1/32    scram-sha-256

# IPv6 local connections
host    all         all         ::1/128         scram-sha-256

# Allow remote connections (example)
host    all         all         192.168.1.0/24  scram-sha-256
```

#### Authentication Methods
| Method | Description |
|--------|-------------|
| `trust` | No password required (dangerous!) |
| `peer` | OS username must match DB username |
| `scram-sha-256` | Secure password authentication |
| `md5` | MD5 password (legacy) |
| `reject` | Reject connection |
| `cert` | SSL client certificate |

### postgresql.conf (Main Configuration)

```bash
# Location
SHOW config_file;
```

Key Settings:
```conf
# Connection Settings
listen_addresses = 'localhost'      # or '*' for all interfaces
port = 5432
max_connections = 100

# Memory
shared_buffers = 256MB              # 25% of RAM for dedicated server
work_mem = 4MB
maintenance_work_mem = 64MB
effective_cache_size = 4GB          # 75% of RAM

# WAL
wal_level = replica
max_wal_size = 1GB
min_wal_size = 80MB

# Logging
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_statement = 'ddl'               # none, ddl, mod, all
```

---

## 7. System Catalogs

System catalogs store metadata about database objects.

### Important Catalogs

```sql
-- List all databases
SELECT datname, datdba, encoding 
FROM pg_database;

-- List all tables in current database
SELECT schemaname, tablename, tableowner 
FROM pg_tables 
WHERE schemaname NOT IN ('pg_catalog', 'information_schema');

-- List all schemas
SELECT nspname, nspowner 
FROM pg_namespace;

-- List all users/roles
SELECT rolname, rolsuper, rolinherit, rolcreaterole, rolcreatedb 
FROM pg_roles;

-- Table sizes
SELECT 
    relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

### pg_catalog vs information_schema

| Feature | pg_catalog | information_schema |
|---------|------------|-------------------|
| PostgreSQL Specific | ✅ Yes | ❌ No |
| SQL Standard | ❌ No | ✅ Yes |
| Performance | Faster | Slower (views) |
| Portability | Low | High |

---

## 🔬 Hands-On Practice

### Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

### First Connection

```bash
# Connect as postgres superuser
sudo -u postgres psql

# Basic commands
\l              -- List databases
\du             -- List roles
\c dbname       -- Connect to database
\dt             -- List tables
\d tablename    -- Describe table
\q              -- Quit
```

### Explore System

```sql
-- Check PostgreSQL version
SELECT version();

-- View current configuration
SHOW ALL;

-- View specific setting
SHOW shared_buffers;
SHOW data_directory;

-- View active connections
SELECT * FROM pg_stat_activity;

-- View background processes
SELECT pid, wait_event_type, wait_event, state, query 
FROM pg_stat_activity 
WHERE backend_type != 'client backend';
```

---

## 📝 Key Takeaways

1. **PostgreSQL is process-based** - Each connection gets its own backend process
2. **Shared memory is critical** - Used for buffer cache, WAL buffers, locks
3. **Data directory contains everything** - Databases, WAL, configs
4. **pg_hba.conf controls access** - Who can connect and how
5. **System catalogs are queryable** - Metadata is stored in regular tables

---

## 📚 Further Reading

- [PostgreSQL Architecture](https://www.postgresql.org/docs/current/runtime.html)
- [Database File Layout](https://www.postgresql.org/docs/current/storage-file-layout.html)
- [The Internals of PostgreSQL](https://www.interdb.jp/pg/)

---

## ✅ Day 1 Checklist

- [ ] Install PostgreSQL
- [ ] Connect using psql
- [ ] Explore data directory
- [ ] Read pg_hba.conf
- [ ] Read postgresql.conf
- [ ] Query system catalogs
- [ ] Understand process model
