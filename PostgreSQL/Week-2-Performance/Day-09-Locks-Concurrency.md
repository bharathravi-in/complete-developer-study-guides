# Day 9: Locks & Concurrency

## 📚 Learning Objectives
- Understand PostgreSQL locking mechanisms
- Master row-level and table-level locks
- Handle deadlocks properly
- Use SELECT FOR UPDATE
- Learn advisory locks

---

## 1. Lock Types Overview

### Lock Levels

```
Least Restrictive ←──────────────────────────→ Most Restrictive

ACCESS SHARE → ROW SHARE → ROW EXCLUSIVE → SHARE UPDATE EXCLUSIVE 
→ SHARE → SHARE ROW EXCLUSIVE → EXCLUSIVE → ACCESS EXCLUSIVE
```

### Lock Compatibility Matrix

| Requested \ Held | AS | RS | RE | SUE | S | SRE | E | AE |
|------------------|----|----|----|----|---|-----|---|-----|
| ACCESS SHARE | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |
| ROW SHARE | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ |
| ROW EXCL | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| SHARE UPDATE EXCL | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |
| SHARE | ✓ | ✓ | ✗ | ✗ | ✓ | ✗ | ✗ | ✗ |
| SHARE ROW EXCL | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| EXCLUSIVE | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| ACCESS EXCL | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

---

## 2. Table-Level Locks

### Automatic Locks by Statement

| Statement | Lock Acquired |
|-----------|--------------|
| SELECT | ACCESS SHARE |
| SELECT FOR UPDATE/SHARE | ROW SHARE |
| UPDATE, DELETE, INSERT | ROW EXCLUSIVE |
| CREATE INDEX CONCURRENTLY | SHARE UPDATE EXCLUSIVE |
| VACUUM, ANALYZE | SHARE UPDATE EXCLUSIVE |
| CREATE INDEX | SHARE |
| CREATE TRIGGER | SHARE ROW EXCLUSIVE |
| ALTER TABLE, DROP TABLE | ACCESS EXCLUSIVE |
| TRUNCATE | ACCESS EXCLUSIVE |

### Explicit Table Locks

```sql
-- Lock table explicitly
BEGIN;
LOCK TABLE accounts IN ACCESS EXCLUSIVE MODE;
-- No one can read or write until we commit
UPDATE accounts SET balance = balance * 1.05;
COMMIT;

-- Lock with NOWAIT
BEGIN;
LOCK TABLE accounts IN SHARE MODE NOWAIT;
-- Fails immediately if lock not available
```

### Lock Modes Explained

```sql
-- ACCESS SHARE: Reading, allows concurrent reads
SELECT * FROM accounts;

-- ROW EXCLUSIVE: Writing, blocks DDL
UPDATE accounts SET balance = 100 WHERE id = 1;

-- SHARE: Read lock, blocks writes
BEGIN;
LOCK TABLE accounts IN SHARE MODE;
SELECT * FROM accounts;  -- Consistent read
-- No updates allowed by others
COMMIT;

-- ACCESS EXCLUSIVE: Full lock
BEGIN;
LOCK TABLE accounts IN ACCESS EXCLUSIVE MODE;
ALTER TABLE accounts ADD COLUMN notes TEXT;
COMMIT;
```

---

## 3. Row-Level Locks

### MVCC and Row Locks

PostgreSQL uses MVCC primarily, but row locks exist for:
- SELECT FOR UPDATE
- UPDATE/DELETE operations

```sql
-- View row locks
SELECT 
    locktype,
    relation::regclass,
    tuple,
    pid,
    mode,
    granted
FROM pg_locks
WHERE locktype = 'tuple';
```

### Lock Modes on Rows

| Mode | UPDATE | NO KEY UPDATE | SHARE | KEY SHARE |
|------|--------|---------------|-------|-----------|
| FOR UPDATE | ✗ | ✗ | ✗ | ✗ |
| FOR NO KEY UPDATE | ✗ | ✗ | ✗ | ✓ |
| FOR SHARE | ✗ | ✗ | ✓ | ✓ |
| FOR KEY SHARE | ✗ | ✓ | ✓ | ✓ |

---

## 4. SELECT FOR UPDATE

### Basic Usage

```sql
-- Lock rows for update
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- Row locked - other transactions wait
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- Lock multiple rows
BEGIN;
SELECT * FROM inventory 
WHERE product_id IN (1, 2, 3) 
FOR UPDATE;
-- All matching rows locked
-- Process inventory
COMMIT;
```

### FOR UPDATE Options

```sql
-- NOWAIT: Fail immediately if locked
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;
-- ERROR: could not obtain lock on row

-- SKIP LOCKED: Process only unlocked rows
BEGIN;
SELECT * FROM job_queue 
WHERE status = 'pending'
FOR UPDATE SKIP LOCKED
LIMIT 10;
-- Returns only unlocked rows - great for job queues!
UPDATE job_queue SET status = 'processing' WHERE ...;
COMMIT;
```

### Lock Strength Variations

```sql
-- FOR UPDATE: Strongest lock, blocks everything
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;

-- FOR NO KEY UPDATE: Allows foreign key checks
SELECT * FROM orders WHERE id = 1 FOR NO KEY UPDATE;

-- FOR SHARE: Read lock, blocks writes
SELECT * FROM products WHERE id = 1 FOR SHARE;

-- FOR KEY SHARE: Weakest, allows non-key updates
SELECT * FROM items WHERE id = 1 FOR KEY SHARE;
```

### Locking with Joins

```sql
-- Lock specific table in join
SELECT o.*, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.id = 1
FOR UPDATE OF o;  -- Only lock orders, not customers

-- Lock multiple tables
SELECT o.*, c.name
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.id = 1
FOR UPDATE OF o, c;
```

---

## 5. Deadlocks

### What is a Deadlock?

```
Transaction A:          Transaction B:
-----------            -----------
Lock row 1             Lock row 2
Wants row 2            Wants row 1
Waiting...             Waiting...
⬆️_____DEADLOCK!______⬆️
```

### Example Deadlock

```sql
-- Session A
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- (holds lock on id=1)

-- Session B (concurrently)
BEGIN;
UPDATE accounts SET balance = balance - 50 WHERE id = 2;
-- (holds lock on id=2)
UPDATE accounts SET balance = balance + 50 WHERE id = 1;
-- (waiting for lock on id=1)

-- Session A (continues)
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
-- DEADLOCK! Both waiting for each other
-- ERROR: deadlock detected
```

### Deadlock Detection

```sql
-- PostgreSQL automatically detects deadlocks
-- One transaction is aborted with error:
-- ERROR: deadlock detected
-- DETAIL: Process 1234 waits for ShareLock on transaction 5678;
--         Process 5678 waits for ShareLock on transaction 1234.

-- Check deadlock timeout setting
SHOW deadlock_timeout;  -- Default: 1s

-- View deadlock information in logs
-- Set in postgresql.conf:
-- log_lock_waits = on
-- deadlock_timeout = 1s
```

### Preventing Deadlocks

```sql
-- Strategy 1: Lock in consistent order
-- Always lock lower ID first
BEGIN;
SELECT * FROM accounts 
WHERE id IN (1, 5, 3) 
ORDER BY id
FOR UPDATE;  -- Locks 1, then 3, then 5

-- Strategy 2: Lock everything at once
BEGIN;
LOCK TABLE accounts IN SHARE ROW EXCLUSIVE MODE;
-- Now update freely
COMMIT;

-- Strategy 3: Use advisory locks
BEGIN;
SELECT pg_advisory_xact_lock(hashtext('accounts:transfer'));
-- Only one transfer at a time
COMMIT;

-- Strategy 4: Retry on deadlock
-- Application code with retry logic
```

### Handling Deadlocks in Application

```python
# Python example
import psycopg2
from psycopg2 import errors

MAX_RETRIES = 3

def transfer_with_retry(conn, from_id, to_id, amount):
    for attempt in range(MAX_RETRIES):
        try:
            with conn.cursor() as cur:
                cur.execute("BEGIN")
                
                # Lock in consistent order
                ids = sorted([from_id, to_id])
                cur.execute(
                    "SELECT * FROM accounts WHERE id = ANY(%s) ORDER BY id FOR UPDATE",
                    (ids,)
                )
                
                cur.execute(
                    "UPDATE accounts SET balance = balance - %s WHERE id = %s",
                    (amount, from_id)
                )
                cur.execute(
                    "UPDATE accounts SET balance = balance + %s WHERE id = %s",
                    (amount, to_id)
                )
                
                conn.commit()
                return True
                
        except errors.DeadlockDetected:
            conn.rollback()
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(random.uniform(0.1, 0.5))
    
    return False
```

---

## 6. Advisory Locks

Application-managed locks that don't lock database objects.

### Session-Level Advisory Locks

```sql
-- Acquire lock (waits if held by another session)
SELECT pg_advisory_lock(12345);

-- Try to acquire (returns immediately)
SELECT pg_try_advisory_lock(12345);  -- Returns true/false

-- Release lock
SELECT pg_advisory_unlock(12345);

-- Lock with two keys (namespace + id)
SELECT pg_advisory_lock(1, 100);  -- Namespace 1, ID 100
```

### Transaction-Level Advisory Locks

```sql
-- Auto-released at transaction end
BEGIN;
SELECT pg_advisory_xact_lock(12345);
-- Do work
COMMIT;  -- Lock automatically released
```

### Use Cases

```sql
-- Use Case 1: Singleton job execution
-- In each worker:
BEGIN;
IF pg_try_advisory_xact_lock(hashtext('daily_report')) THEN
    -- Only one worker runs this
    PERFORM generate_daily_report();
END IF;
COMMIT;

-- Use Case 2: Rate limiting
CREATE OR REPLACE FUNCTION api_rate_limit(user_id INT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Try to acquire lock for this user
    IF pg_try_advisory_lock(user_id) THEN
        -- Register request
        INSERT INTO api_requests (user_id) VALUES (user_id);
        
        -- Release lock after brief delay
        PERFORM pg_sleep(0.1);
        PERFORM pg_advisory_unlock(user_id);
        RETURN true;
    ELSE
        RETURN false;  -- Already processing
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Use Case 3: Distributed mutex
SELECT pg_advisory_lock(
    hashtext('resource_type'),
    hashtext('resource_id')
);
-- Critical section
SELECT pg_advisory_unlock(
    hashtext('resource_type'),
    hashtext('resource_id')
);
```

### Viewing Advisory Locks

```sql
SELECT * FROM pg_locks WHERE locktype = 'advisory';

-- Count locks held by session
SELECT COUNT(*) FROM pg_locks 
WHERE locktype = 'advisory' AND pid = pg_backend_pid();
```

---

## 7. Lock Monitoring

### View Current Locks

```sql
-- All locks
SELECT 
    l.locktype,
    l.relation::regclass AS table_name,
    l.page,
    l.tuple,
    l.virtualxid,
    l.transactionid,
    l.mode,
    l.granted,
    a.usename,
    a.query,
    a.pid
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.relation IS NOT NULL
ORDER BY l.relation;

-- Lock waits (who's blocking whom)
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_query,
    blocking_activity.query AS blocking_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity 
    ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity 
    ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

### Kill Blocking Query

```sql
-- Cancel query (graceful)
SELECT pg_cancel_backend(pid);

-- Terminate connection (forceful)
SELECT pg_terminate_backend(pid);

-- Find and kill long-running queries
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'active'
AND now() - query_start > INTERVAL '10 minutes';
```

---

## 8. Lock Timeout Settings

```sql
-- Fail if can't acquire lock within timeout
SET lock_timeout = '5s';

-- Statement level
SET LOCAL lock_timeout = '2s';

-- Or per statement
BEGIN;
SET LOCAL lock_timeout = '1s';
SELECT * FROM accounts FOR UPDATE;  -- Fails after 1s if locked
COMMIT;

-- Disable (wait forever)
SET lock_timeout = 0;
```

---

## 🔬 Hands-On: Job Queue with Locking

```sql
-- Create queue table
CREATE TABLE job_queue (
    id SERIAL PRIMARY KEY,
    payload JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    locked_by INT,
    locked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Worker function - grab next job
CREATE OR REPLACE FUNCTION grab_job(worker_id INT)
RETURNS TABLE(job_id INT, payload JSONB) AS $$
BEGIN
    RETURN QUERY
    UPDATE job_queue
    SET 
        status = 'processing',
        locked_by = worker_id,
        locked_at = NOW()
    WHERE id = (
        SELECT id FROM job_queue
        WHERE status = 'pending'
        ORDER BY created_at
        FOR UPDATE SKIP LOCKED
        LIMIT 1
    )
    RETURNING id, payload;
END;
$$ LANGUAGE plpgsql;

-- Usage
BEGIN;
SELECT * FROM grab_job(1);  -- Worker 1 gets a job
-- Process the job
UPDATE job_queue SET status = 'completed' WHERE id = ?;
COMMIT;
```

---

## 📝 Key Takeaways

1. **MVCC reduces need for locks** - Readers don't block writers
2. **SELECT FOR UPDATE for atomic updates** - Essential for race conditions
3. **SKIP LOCKED for job queues** - Non-blocking worker pattern
4. **Lock in consistent order** - Prevents deadlocks
5. **Advisory locks for custom scenarios** - Application-level coordination
6. **Monitor locks in production** - Catch blocking issues early

---

## ✅ Day 9 Checklist

- [ ] Understand lock compatibility matrix
- [ ] Practice SELECT FOR UPDATE
- [ ] Use SKIP LOCKED for queues
- [ ] Handle deadlocks in code
- [ ] Implement advisory locks
- [ ] Monitor locks with pg_locks
