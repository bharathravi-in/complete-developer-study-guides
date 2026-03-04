# Day 8: ACID & Transactions

## 📚 Learning Objectives
- Understand ACID properties deeply
- Master transaction control (BEGIN, COMMIT, ROLLBACK)
- Learn savepoints
- Deep dive into isolation levels
- Master MVCC (Most Important Concept!)

---

## 1. ACID Properties

### Atomicity
All operations in a transaction succeed or all fail.

```sql
-- Either both succeed or both fail
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- If second UPDATE fails, first is rolled back
```

### Consistency
Database moves from one valid state to another valid state.

```sql
-- Constraints ensure consistency
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    balance NUMERIC(10,2) CHECK (balance >= 0)
);

-- This fails atomically (constraint violation)
BEGIN;
UPDATE accounts SET balance = balance - 5000 WHERE id = 1;  -- Fails if balance < 5000
-- Transaction rolled back, consistency maintained
```

### Isolation
Concurrent transactions don't interfere with each other.

```sql
-- Transaction A and B see consistent snapshots
-- Changes from A are invisible to B until A commits
```

### Durability
Committed data survives system failures.

```sql
-- After COMMIT, data is persisted to WAL
-- Even if server crashes, data can be recovered
```

---

## 2. Transaction Control

### Basic Transaction

```sql
-- Explicit transaction
BEGIN;
    INSERT INTO orders (customer_id, total) VALUES (1, 100);
    INSERT INTO order_items (order_id, product_id) VALUES (1, 5);
COMMIT;

-- Alternative syntax
BEGIN TRANSACTION;
    -- statements
END TRANSACTION;

-- Or
START TRANSACTION;
    -- statements
COMMIT WORK;
```

### ROLLBACK

```sql
-- Cancel all changes
BEGIN;
    DELETE FROM important_data;
    -- Oops! Cancel that!
ROLLBACK;

-- Error handling in application code
BEGIN;
    -- operation 1
    -- operation 2
    -- if error:
ROLLBACK;
    -- else:
COMMIT;
```

### Autocommit

```sql
-- By default, each statement is its own transaction
INSERT INTO logs (message) VALUES ('Test');  -- Auto-committed

-- Disable autocommit for session
SET autocommit = OFF;

-- In psql
\set AUTOCOMMIT off
```

---

## 3. Savepoints

Savepoints allow partial rollback within a transaction.

```sql
BEGIN;

INSERT INTO orders (id, customer_id) VALUES (1, 100);
SAVEPOINT order_created;

INSERT INTO order_items (order_id, product_id) VALUES (1, 999);
-- Error! Product doesn't exist

ROLLBACK TO SAVEPOINT order_created;
-- Order is still there, only order_items rolled back

INSERT INTO order_items (order_id, product_id) VALUES (1, 1);
-- This works

COMMIT;
```

### Nested Savepoints

```sql
BEGIN;
    INSERT INTO t1 VALUES (1);
    SAVEPOINT sp1;
        INSERT INTO t2 VALUES (2);
        SAVEPOINT sp2;
            INSERT INTO t3 VALUES (3);
        ROLLBACK TO sp2;    -- Undo t3, keep t1, t2
        INSERT INTO t3 VALUES (4);
    SAVEPOINT sp3;
        INSERT INTO t4 VALUES (5);
    ROLLBACK TO sp1;    -- Undo t2, t3, t4, keep only t1
COMMIT;  -- Only t1 committed
```

### Release Savepoint

```sql
BEGIN;
    SAVEPOINT sp1;
    -- work
    RELEASE SAVEPOINT sp1;  -- Savepoint no longer valid
    -- can't rollback to sp1 anymore
COMMIT;
```

---

## 4. Isolation Levels

### The Four Standard Levels

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|-------|------------|---------------------|--------------|
| Read Uncommitted | Possible | Possible | Possible |
| Read Committed | No | Possible | Possible |
| Repeatable Read | No | No | No* |
| Serializable | No | No | No |

*PostgreSQL's Repeatable Read prevents phantoms due to MVCC

### Read Phenomena Explained

```sql
-- DIRTY READ: Reading uncommitted data
-- Session A                    Session B
BEGIN;
UPDATE accounts SET balance = 0;
                                -- If dirty read allowed:
                                SELECT balance;  -- Would see 0
ROLLBACK;
                                -- But data was rolled back!

-- NON-REPEATABLE READ: Same query returns different results
-- Session A                    Session B
BEGIN;
SELECT balance FROM accounts;   
-- Returns: 1000
                                UPDATE accounts SET balance = 500;
                                COMMIT;
SELECT balance FROM accounts;   
-- Returns: 500 (different!)
COMMIT;

-- PHANTOM READ: New rows appear in repeated query
-- Session A                    Session B
BEGIN;
SELECT COUNT(*) FROM orders;
-- Returns: 100
                                INSERT INTO orders VALUES (...);
                                COMMIT;
SELECT COUNT(*) FROM orders;
-- Returns: 101 (phantom row!)
COMMIT;
```

### Setting Isolation Level

```sql
-- For current transaction
BEGIN ISOLATION LEVEL READ COMMITTED;
BEGIN ISOLATION LEVEL REPEATABLE READ;
BEGIN ISOLATION LEVEL SERIALIZABLE;

-- Or
BEGIN;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- For session
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Check current level
SHOW transaction_isolation;
```

### Read Committed (PostgreSQL Default)

```sql
-- See committed changes from other transactions
-- Each statement sees latest committed data

BEGIN ISOLATION LEVEL READ COMMITTED;

SELECT balance FROM accounts WHERE id = 1;
-- Returns: 1000

-- Another session updates and commits
-- UPDATE accounts SET balance = 500 WHERE id = 1; COMMIT;

SELECT balance FROM accounts WHERE id = 1;
-- Returns: 500 (sees the committed change)

COMMIT;
```

### Repeatable Read

```sql
-- Snapshot at transaction start
-- All queries see the same snapshot

BEGIN ISOLATION LEVEL REPEATABLE READ;

SELECT balance FROM accounts WHERE id = 1;
-- Returns: 1000

-- Another session updates and commits
-- UPDATE accounts SET balance = 500 WHERE id = 1; COMMIT;

SELECT balance FROM accounts WHERE id = 1;
-- Still returns: 1000 (snapshot isolation)

COMMIT;
```

### Serializable

```sql
-- Transactions appear to run serially
-- May cause serialization failures (must retry)

BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT SUM(balance) FROM accounts;
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
COMMIT;

-- If concurrent transaction modified balance,
-- one of them will fail with:
-- ERROR: could not serialize access due to concurrent update
```

---

## 5. MVCC (Multi-Version Concurrency Control)

### The Big Concept

Instead of locking, PostgreSQL keeps multiple versions of rows.

```
Row Versions:
+------+------+--------+--------+--------+
| xmin | xmax | id     | name   | balance|
+------+------+--------+--------+--------+
| 100  | 105  | 1      | Alice  | 1000   |  <- Old version (deleted by tx 105)
| 105  | NULL | 1      | Alice  | 1500   |  <- Current version
+------+------+--------+--------+--------+
```

### Transaction IDs (xid)

```sql
-- View current transaction ID
SELECT txid_current();

-- View row versions
SELECT xmin, xmax, * FROM accounts;
```

### How MVCC Works

```sql
-- INSERT: Creates row with xmin = current txid, xmax = null
INSERT INTO t VALUES (1);  -- xmin=100, xmax=null

-- UPDATE: Marks old row with xmax, creates new row
UPDATE t SET val = 2 WHERE id = 1;
-- Old: xmin=100, xmax=101 (marked as deleted by tx 101)
-- New: xmin=101, xmax=null

-- DELETE: Marks row with xmax
DELETE FROM t WHERE id = 1;
-- xmin=101, xmax=102 (deleted by tx 102)
```

### Visibility Rules

A row is visible if:
1. `xmin` is committed AND `xmin` < current snapshot
2. `xmax` is null OR `xmax` is not committed OR `xmax` > current snapshot

```sql
-- Transaction 100 sees:
-- - Rows with xmin committed and < 100
-- - Rows not deleted (xmax null) or deleted by uncommitted tx
```

### MVCC Benefits

1. **Readers don't block writers** - Each sees own snapshot
2. **Writers don't block readers** - Old version remains visible
3. **No read locks needed** - Better concurrency
4. **Consistent snapshots** - Time-travel queries

### MVCC Costs

1. **Table bloat** - Old versions accumulate
2. **VACUUM needed** - Clean up dead rows
3. **More disk space** - Multiple versions stored
4. **XID wraparound** - Must vacuum to prevent

---

## 6. Practical Examples

### Bank Transfer

```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    owner VARCHAR(100),
    balance NUMERIC(15,2) CHECK (balance >= 0)
);

-- Safe transfer function
CREATE OR REPLACE FUNCTION transfer(
    from_account INT,
    to_account INT,
    amount NUMERIC
) RETURNS VOID AS $$
BEGIN
    -- Deduct from source
    UPDATE accounts 
    SET balance = balance - amount 
    WHERE id = from_account;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Source account not found';
    END IF;
    
    -- Add to destination
    UPDATE accounts 
    SET balance = balance + amount 
    WHERE id = to_account;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Destination account not found';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Use in transaction
BEGIN;
SELECT transfer(1, 2, 100.00);
COMMIT;
```

### Order Processing with Savepoints

```sql
CREATE OR REPLACE FUNCTION process_order(
    p_customer_id INT,
    p_items JSONB
) RETURNS INT AS $$
DECLARE
    v_order_id INT;
    v_item JSONB;
BEGIN
    -- Create order
    INSERT INTO orders (customer_id, status)
    VALUES (p_customer_id, 'pending')
    RETURNING id INTO v_order_id;
    
    SAVEPOINT items_start;
    
    -- Process each item
    FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
    LOOP
        BEGIN
            INSERT INTO order_items (order_id, product_id, quantity)
            VALUES (
                v_order_id,
                (v_item->>'product_id')::INT,
                (v_item->>'quantity')::INT
            );
            
            -- Update inventory
            UPDATE inventory 
            SET stock = stock - (v_item->>'quantity')::INT
            WHERE product_id = (v_item->>'product_id')::INT;
            
        EXCEPTION WHEN OTHERS THEN
            -- Log failed item, continue with others
            INSERT INTO order_errors (order_id, error)
            VALUES (v_order_id, SQLERRM);
        END;
    END LOOP;
    
    -- Check if any items succeeded
    IF NOT EXISTS (SELECT 1 FROM order_items WHERE order_id = v_order_id) THEN
        ROLLBACK TO items_start;
        UPDATE orders SET status = 'failed' WHERE id = v_order_id;
    ELSE
        UPDATE orders SET status = 'confirmed' WHERE id = v_order_id;
    END IF;
    
    RETURN v_order_id;
END;
$$ LANGUAGE plpgsql;
```

### Handling Serialization Failures

```python
# Python example with retry logic
import psycopg2
from psycopg2 import errors

def execute_with_retry(conn, query, max_retries=3):
    for attempt in range(max_retries):
        try:
            with conn.cursor() as cur:
                cur.execute("BEGIN ISOLATION LEVEL SERIALIZABLE")
                cur.execute(query)
                conn.commit()
                return True
        except errors.SerializationFailure:
            conn.rollback()
            if attempt == max_retries - 1:
                raise
            time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
    return False
```

---

## 7. Transaction Monitoring

```sql
-- View active transactions
SELECT 
    pid,
    now() - xact_start AS duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY xact_start;

-- Find long-running transactions
SELECT 
    pid,
    now() - xact_start AS age,
    query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
AND now() - xact_start > INTERVAL '5 minutes';

-- View locks held by transaction
SELECT 
    l.pid,
    l.locktype,
    l.relation::regclass,
    l.mode,
    l.granted
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE a.query NOT LIKE '%pg_locks%';
```

---

## 📝 Key Takeaways

1. **ACID ensures data integrity** - Fundamental to databases
2. **PostgreSQL default is Read Committed** - Fine for most apps
3. **Use Repeatable Read for consistent reports** - Snapshot isolation
4. **Serializable for critical operations** - With retry logic
5. **MVCC enables high concurrency** - Readers don't block writers
6. **VACUUM cleans up MVCC bloat** - Critical for performance

---

## ✅ Day 8 Checklist

- [ ] Practice BEGIN/COMMIT/ROLLBACK
- [ ] Use savepoints in complex transactions
- [ ] Test different isolation levels
- [ ] Observe MVCC with xmin/xmax
- [ ] Handle serialization failures
- [ ] Monitor active transactions
