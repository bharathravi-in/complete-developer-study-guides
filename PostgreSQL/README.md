# 🚀 PostgreSQL 30-Day Mastery Plan

> **DBA + Backend + Performance Engineering**

A comprehensive learning path to becoming a PostgreSQL expert, covering foundations through advanced system design.

## 📋 Course Overview

| Week | Focus Area | Days |
|------|------------|------|
| 1 | Foundations + SQL Mastery | Days 1-7 |
| 2 | Transactions, Indexing & Performance | Days 8-14 |
| 3 | DBA + Production + Scaling | Days 15-21 |
| 4 | Advanced PostgreSQL (Senior/AI/System Design) | Days 22-30 |

## 📁 Directory Structure

```
PostgreSQL/
├── README.md                    # This file
├── Week-1-Foundations/          # SQL basics & architecture
├── Week-2-Performance/          # Transactions, indexing, optimization
├── Week-3-DBA-Production/       # Replication, backup, HA, security
├── Week-4-Advanced/             # JSONB, FTS, extensions, system design
├── Interview-Prep/              # Interview questions & case studies
└── Practice-SQL/                # SQL exercises & solutions
```

## 📅 WEEK 1 – Foundations + SQL Mastery

| Day | Topic | Key Concepts |
|-----|-------|--------------|
| 1 | PostgreSQL Architecture | Client-server, processes, data directory |
| 2 | Database & Schema | Tablespaces, catalogs, search_path |
| 3 | Data Types | JSON/JSONB, UUID, Arrays, ENUM |
| 4 | DDL Commands | Constraints, DEFERRABLE |
| 5 | DML + Querying | SELECT, WHERE, GROUP BY, HAVING |
| 6 | Joins & Advanced Querying | All joins, subqueries, EXISTS vs IN |
| 7 | Window Functions | ROW_NUMBER, RANK, LEAD/LAG |

## 📅 WEEK 2 – Transactions, Indexing & Performance

| Day | Topic | Key Concepts |
|-----|-------|--------------|
| 8 | ACID & Transactions | MVCC, isolation levels, savepoints |
| 9 | Locks & Concurrency | Deadlocks, FOR UPDATE, advisory locks |
| 10 | Indexing Deep Dive | B-Tree, GIN, GiST, BRIN, partial indexes |
| 11 | Query Planner | EXPLAIN ANALYZE, scan types, cost |
| 12 | Performance Optimization | N+1, pagination, connection pooling |
| 13 | VACUUM & Autovacuum | Bloat, analyze, freeze |
| 14 | Configuration Tuning | Memory settings, WAL buffers |

## 📅 WEEK 3 – DBA + Production + Scaling

| Day | Topic | Key Concepts |
|-----|-------|--------------|
| 15 | WAL & Replication | Streaming, logical replication |
| 16 | Backup & Recovery | pg_dump, PITR, base backups |
| 17 | High Availability | Patroni, PgBouncer, failover |
| 18 | Security | Roles, RLS, SSL, pg_hba.conf |
| 19 | Partitioning | Range, list, hash, pruning |
| 20 | Monitoring | pg_stat_*, Prometheus, slow queries |
| 21 | Connection Pooling | PgBouncer modes |

## 📅 WEEK 4 – Advanced PostgreSQL

| Day | Topic | Key Concepts |
|-----|-------|--------------|
| 22 | JSONB & NoSQL | JSONB operators, indexing |
| 23 | Full Text Search | tsvector, tsquery, GIN |
| 24 | PL/pgSQL | Functions, procedures, triggers |
| 25 | CTE & Recursive Queries | WITH, tree traversal |
| 26 | Extensions | pgcrypto, PostGIS, pg_trgm |
| 27 | Scaling Strategy | Sharding, Citus, TimescaleDB |
| 28 | System Design | Multi-tenant, payments, e-commerce |
| 29 | PostgreSQL for AI | pgvector, embeddings, similarity search |
| 30 | Mock Interview + Revision | Practice problems, MVCC deep dive |

## 🎯 Career Targets

After completing this course, you'll be ready for:
- ✅ Senior Backend Engineer
- ✅ Database Engineer
- ✅ PostgreSQL DBA
- ✅ AI Backend Engineer
- ✅ System Design roles

## 📚 Additional Resources

- [Official PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostgreSQL Wiki](https://wiki.postgresql.org/)
- [Explain.depesz.com](https://explain.depesz.com/) - EXPLAIN visualizer
- [PgTune](https://pgtune.leopard.in.ua/) - Configuration calculator

## 🏁 Getting Started

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt install postgresql postgresql-contrib

# Connect to PostgreSQL
sudo -u postgres psql

# Check version
SELECT version();
```

---

**Happy Learning! 🐘**
