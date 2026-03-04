# Day 16: Backup & Recovery

## 📚 Learning Objectives
- Master pg_dump and pg_restore
- Understand base backups
- Implement Point-in-Time Recovery (PITR)
- Design backup strategies

---

## 1. Logical Backups (pg_dump)

### Basic pg_dump

```bash
# Dump single database (custom format - recommended)
pg_dump -Fc -f backup.dump mydb

# SQL format (human-readable)
pg_dump -Fp -f backup.sql mydb

# Directory format (parallel backup)
pg_dump -Fd -j 4 -f backup_dir/ mydb

# Compressed SQL
pg_dump mydb | gzip > backup.sql.gz
```

### pg_dump Options

```bash
# Schema only (no data)
pg_dump -s -f schema.sql mydb

# Data only
pg_dump -a -f data.sql mydb

# Specific tables
pg_dump -t users -t orders mydb > tables.sql

# Exclude tables
pg_dump --exclude-table='*_log' mydb > backup.sql

# Specific schema
pg_dump -n public mydb > public_schema.sql
```

### pg_dumpall

```bash
# Backup entire cluster (all databases, roles, etc.)
pg_dumpall -f full_cluster.sql

# Globals only (roles, tablespaces)
pg_dumpall -g -f globals.sql
```

---

## 2. Restore with pg_restore

### Basic Restore

```bash
# Create target database first
createdb newdb

# Restore from custom format
pg_restore -d newdb backup.dump

# Restore with parallelism
pg_restore -j 4 -d newdb backup.dump

# SQL format (use psql)
psql -d newdb -f backup.sql
```

### Restore Options

```bash
# List contents without restoring
pg_restore -l backup.dump

# Selective restore (only specific items)
pg_restore -l backup.dump > list.txt
# Edit list.txt to comment out unwanted items
pg_restore -L list.txt -d newdb backup.dump

# Schema only
pg_restore -s -d newdb backup.dump

# Data only
pg_restore -a -d newdb backup.dump

# Single table
pg_restore -t users -d newdb backup.dump

# Clean before restore
pg_restore -c -d newdb backup.dump
```

---

## 3. Physical Backups (Base Backup)

### Using pg_basebackup

```bash
# Basic backup
pg_basebackup -D /backup/base -Fp -Xs -P

# With compression
pg_basebackup -D /backup/base -Ft -z -P

# Options:
# -D: Target directory
# -Fp: Plain format
# -Ft: Tar format
# -Xs: Stream WAL during backup
# -z: Compress
# -P: Progress reporting
# -c: Checkpoint mode (fast/spread)
# -R: Write recovery configuration
```

### Why Physical Backup?

| Feature | pg_dump | pg_basebackup |
|---------|---------|---------------|
| Speed | Slow | Fast |
| PITR | No | Yes |
| Size | Smaller | Larger |
| Cross-platform | Yes | No |
| Partial restore | Yes | No |

---

## 4. Point-in-Time Recovery (PITR)

### Architecture

```
┌─────────┐     ┌────────────────┐     ┌───────────┐
│  Base   │  +  │  Archived WAL  │  =  │ Any Point │
│ Backup  │     │  Segments      │     │ in Time   │
└─────────┘     └────────────────┘     └───────────┘

Base Backup (Day 1)
    │
    ├── WAL 000001 (Day 1-2)
    ├── WAL 000002 (Day 2-3)
    ├── WAL 000003 (Day 3-4)  ← Recover to here!
    └── WAL 000004 (Day 4-5)
```

### Configure WAL Archiving

```sql
-- postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archive/%f'

-- Or with compression
archive_command = 'gzip < %p > /archive/%f.gz'

-- Test archive_command
archive_command = 'test ! -f /archive/%f && cp %p /archive/%f'
```

### Take Base Backup

```bash
# Start continuous archiving first!
# Then take base backup
pg_basebackup -D /backup/base -Ft -z -P -Xs
```

### Perform PITR

```bash
# 1. Stop PostgreSQL
systemctl stop postgresql

# 2. Clear data directory
rm -rf /var/lib/postgresql/data/*

# 3. Restore base backup
tar -xzf /backup/base/base.tar.gz -C /var/lib/postgresql/data

# 4. Configure recovery
cat > /var/lib/postgresql/data/postgresql.auto.conf << EOF
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2024-01-15 14:30:00'
recovery_target_action = 'promote'
EOF

# 5. Create recovery signal
touch /var/lib/postgresql/data/recovery.signal

# 6. Start PostgreSQL
systemctl start postgresql

# 7. PostgreSQL replays WAL until target time
# Then promotes to regular operation
```

### Recovery Targets

```sql
-- Recover to specific time
recovery_target_time = '2024-01-15 14:30:00'

-- Recover to transaction ID
recovery_target_xid = '12345'

-- Recover to named restore point
SELECT pg_create_restore_point('before_migration');
recovery_target_name = 'before_migration'

-- Recover to end of WAL
recovery_target = 'immediate'

-- What to do after recovery
recovery_target_action = 'pause'    -- Stay in recovery
recovery_target_action = 'promote'  -- Become primary
recovery_target_action = 'shutdown' -- Stop server

-- Include or exclude target
recovery_target_inclusive = false   -- Stop just before target
```

---

## 5. Backup Strategies

### Full + Incremental

```
Sunday: Full Base Backup
Monday-Saturday: Archive WAL only

Recovery: Restore Sunday's base + replay WAL

Pros: Less storage, fast daily backups
Cons: Longer recovery time
```

### Continuous Archiving

```bash
# Always-on WAL archiving
# Base backups weekly
# Can recover to any point

# Automation script
#!/bin/bash
pg_basebackup -D /backup/base_$(date +%Y%m%d) -Ft -z -P
# Keep last 4 weekly backups
find /backup -name "base_*" -mtime +28 -delete
```

### pgBackRest (Recommended)

```bash
# Install pgbackrest
apt install pgbackrest

# Configure /etc/pgbackrest/pgbackrest.conf
[global]
repo1-path=/backup/pgbackrest
repo1-retention-full=4

[mydb]
pg1-path=/var/lib/postgresql/data

# Create backup
pgbackrest backup --stanza=mydb --type=full

# Incremental backup
pgbackrest backup --stanza=mydb --type=incr

# Restore
pgbackrest restore --stanza=mydb --target-time="2024-01-15 14:30:00"
```

---

## 6. Backup Monitoring

```sql
-- View last successful backup
SELECT pg_stat_get_backend_activity(pg_backend_pid());

-- Check archive status
SELECT * FROM pg_stat_archiver;

-- Files waiting to be archived
SELECT COUNT(*) FROM pg_ls_dir('pg_wal') WHERE name ~ '^[0-9A-F]{24}$';
```

---

## 📝 Key Takeaways

1. **pg_dump for logical backups** - Human-readable, cross-version
2. **pg_basebackup for PITR** - Byte-level, requires WAL
3. **Always archive WAL** - Essential for point-in-time recovery
4. **Test your restores** - Backup is useless if restore fails
5. **Automate with pgBackRest** - Enterprise-grade backup tool

---

## ✅ Day 16 Checklist

- [ ] Practice pg_dump/pg_restore
- [ ] Configure WAL archiving
- [ ] Take base backup
- [ ] Set up PITR
- [ ] Test recovery procedure
- [ ] Document backup schedule
