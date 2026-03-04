# Day 24: PL/pgSQL (Stored Procedures & Functions)

## 📚 Learning Objectives
- Write PL/pgSQL functions and procedures
- Master control flow and error handling
- Use cursors and dynamic SQL
- Implement triggers effectively

---

## 1. Functions vs Procedures

### Functions

```sql
-- Functions return values
CREATE OR REPLACE FUNCTION add_numbers(a INTEGER, b INTEGER)
RETURNS INTEGER AS $$
BEGIN
    RETURN a + b;
END;
$$ LANGUAGE plpgsql;

-- Call function
SELECT add_numbers(5, 3);  -- 8

-- Function in queries
SELECT name, add_numbers(quantity, 10) FROM products;
```

### Procedures

```sql
-- Procedures don't return values (PostgreSQL 11+)
-- Can use COMMIT/ROLLBACK
CREATE OR REPLACE PROCEDURE transfer_funds(
    from_account INTEGER,
    to_account INTEGER,
    amount NUMERIC
)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE accounts SET balance = balance - amount 
    WHERE id = from_account;
    
    UPDATE accounts SET balance = balance + amount 
    WHERE id = to_account;
    
    COMMIT;  -- Can commit within procedure!
END;
$$;

-- Call procedure
CALL transfer_funds(1, 2, 100.00);
```

---

## 2. PL/pgSQL Syntax

### Variables and Types

```sql
CREATE OR REPLACE FUNCTION example_variables()
RETURNS VOID AS $$
DECLARE
    -- Basic types
    counter INTEGER := 0;
    name TEXT;
    price NUMERIC(10,2) DEFAULT 0.00;
    is_active BOOLEAN := true;
    
    -- From table column
    user_email users.email%TYPE;
    
    -- Row type
    user_record users%ROWTYPE;
    
    -- Record (generic row)
    dynamic_row RECORD;
    
    -- Array
    ids INTEGER[] := ARRAY[1, 2, 3];
    
    -- Constant
    TAX_RATE CONSTANT NUMERIC := 0.08;
BEGIN
    -- Assignment
    counter := counter + 1;
    
    -- SELECT INTO
    SELECT email INTO user_email FROM users WHERE id = 1;
    
    -- Row
    SELECT * INTO user_record FROM users WHERE id = 1;
    RAISE NOTICE 'Email: %', user_record.email;
END;
$$ LANGUAGE plpgsql;
```

### Control Flow

```sql
CREATE OR REPLACE FUNCTION control_examples(val INTEGER)
RETURNS TEXT AS $$
DECLARE
    result TEXT;
BEGIN
    -- IF-THEN-ELSIF-ELSE
    IF val < 0 THEN
        result := 'negative';
    ELSIF val = 0 THEN
        result := 'zero';
    ELSE
        result := 'positive';
    END IF;
    
    -- CASE expression
    result := CASE val
        WHEN 1 THEN 'one'
        WHEN 2 THEN 'two'
        ELSE 'other'
    END;
    
    -- CASE with conditions
    result := CASE
        WHEN val < 10 THEN 'small'
        WHEN val < 100 THEN 'medium'
        ELSE 'large'
    END;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;
```

### Loops

```sql
CREATE OR REPLACE FUNCTION loop_examples()
RETURNS VOID AS $$
DECLARE
    i INTEGER;
    rec RECORD;
BEGIN
    -- Basic loop
    i := 0;
    LOOP
        i := i + 1;
        EXIT WHEN i >= 10;
    END LOOP;
    
    -- WHILE loop
    WHILE i < 20 LOOP
        i := i + 1;
    END LOOP;
    
    -- FOR loop (range)
    FOR i IN 1..10 LOOP
        RAISE NOTICE 'i = %', i;
    END LOOP;
    
    -- FOR loop (reverse)
    FOR i IN REVERSE 10..1 LOOP
        RAISE NOTICE 'i = %', i;
    END LOOP;
    
    -- FOR loop (query results)
    FOR rec IN SELECT * FROM users LIMIT 10 LOOP
        RAISE NOTICE 'User: %', rec.name;
    END LOOP;
    
    -- FOREACH (array)
    DECLARE
        arr INTEGER[] := ARRAY[1, 2, 3];
        elem INTEGER;
    BEGIN
        FOREACH elem IN ARRAY arr LOOP
            RAISE NOTICE 'Element: %', elem;
        END LOOP;
    END;
END;
$$ LANGUAGE plpgsql;
```

---

## 3. Return Types

### Return Single Value

```sql
CREATE FUNCTION get_user_count()
RETURNS INTEGER AS $$
BEGIN
    RETURN (SELECT COUNT(*) FROM users);
END;
$$ LANGUAGE plpgsql;
```

### Return Table/Set

```sql
-- RETURNS TABLE
CREATE FUNCTION get_active_users()
RETURNS TABLE (
    user_id INTEGER,
    user_name TEXT,
    user_email TEXT
) AS $$
BEGIN
    RETURN QUERY
        SELECT id, name, email
        FROM users
        WHERE is_active = true;
END;
$$ LANGUAGE plpgsql;

-- Usage
SELECT * FROM get_active_users();

-- RETURNS SETOF
CREATE FUNCTION get_users_by_role(role_name TEXT)
RETURNS SETOF users AS $$
BEGIN
    RETURN QUERY
        SELECT * FROM users WHERE role = role_name;
END;
$$ LANGUAGE plpgsql;

-- Return next (streaming)
CREATE FUNCTION generate_series_custom(start_val INT, end_val INT)
RETURNS SETOF INTEGER AS $$
DECLARE
    i INTEGER;
BEGIN
    FOR i IN start_val..end_val LOOP
        RETURN NEXT i;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

### Return Composite Type

```sql
CREATE TYPE user_stats AS (
    total_users INTEGER,
    active_users INTEGER,
    inactive_users INTEGER
);

CREATE FUNCTION get_user_stats()
RETURNS user_stats AS $$
DECLARE
    stats user_stats;
BEGIN
    SELECT COUNT(*) INTO stats.total_users FROM users;
    SELECT COUNT(*) INTO stats.active_users FROM users WHERE is_active;
    stats.inactive_users := stats.total_users - stats.active_users;
    RETURN stats;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM get_user_stats();
-- total_users | active_users | inactive_users
--         100 |           85 |             15
```

---

## 4. Error Handling

### Exception Handling

```sql
CREATE OR REPLACE FUNCTION safe_divide(a NUMERIC, b NUMERIC)
RETURNS NUMERIC AS $$
BEGIN
    RETURN a / b;
EXCEPTION
    WHEN division_by_zero THEN
        RAISE NOTICE 'Division by zero, returning NULL';
        RETURN NULL;
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: % - %', SQLSTATE, SQLERRM;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Common exception names:
-- division_by_zero
-- unique_violation
-- foreign_key_violation
-- not_null_violation
-- check_violation
-- no_data_found
-- too_many_rows
```

### RAISE Statements

```sql
CREATE FUNCTION validate_age(age INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    IF age IS NULL THEN
        RAISE EXCEPTION 'Age cannot be NULL';
    END IF;
    
    IF age < 0 THEN
        RAISE EXCEPTION 'Age cannot be negative: %', age
            USING HINT = 'Age must be a positive integer',
                  ERRCODE = 'check_violation';
    END IF;
    
    IF age < 18 THEN
        RAISE WARNING 'User is a minor: age = %', age;
    END IF;
    
    RAISE NOTICE 'Age validated: %', age;
    RAISE DEBUG 'Debug info here';
    
    RETURN true;
END;
$$ LANGUAGE plpgsql;
```

### Transaction Control (Procedures)

```sql
CREATE OR REPLACE PROCEDURE batch_insert_users(batch_size INTEGER)
LANGUAGE plpgsql AS $$
DECLARE
    i INTEGER := 0;
BEGIN
    FOR i IN 1..1000 LOOP
        INSERT INTO users (name) VALUES ('User ' || i);
        
        -- Commit every batch_size rows
        IF i % batch_size = 0 THEN
            COMMIT;
            RAISE NOTICE 'Committed % rows', i;
        END IF;
    END LOOP;
    COMMIT;
END;
$$;
```

---

## 5. Cursors

### Explicit Cursors

```sql
CREATE OR REPLACE FUNCTION process_large_table()
RETURNS VOID AS $$
DECLARE
    user_cursor CURSOR FOR SELECT * FROM users;
    user_record users%ROWTYPE;
BEGIN
    OPEN user_cursor;
    
    LOOP
        FETCH user_cursor INTO user_record;
        EXIT WHEN NOT FOUND;
        
        -- Process each row
        RAISE NOTICE 'Processing user: %', user_record.name;
    END LOOP;
    
    CLOSE user_cursor;
END;
$$ LANGUAGE plpgsql;

-- Cursor with parameters
DECLARE
    user_cursor CURSOR (min_age INTEGER) FOR
        SELECT * FROM users WHERE age >= min_age;
BEGIN
    OPEN user_cursor(18);
    -- ...
END;
```

### Refcursor (Return Cursor)

```sql
CREATE FUNCTION get_user_cursor()
RETURNS refcursor AS $$
DECLARE
    ref refcursor;
BEGIN
    OPEN ref FOR SELECT * FROM users;
    RETURN ref;
END;
$$ LANGUAGE plpgsql;

-- Use in transaction
BEGIN;
SELECT get_user_cursor();  -- Returns cursor name
FETCH 10 FROM "<unnamed cursor 1>";
COMMIT;
```

---

## 6. Dynamic SQL

### EXECUTE

```sql
CREATE OR REPLACE FUNCTION dynamic_query(table_name TEXT, column_name TEXT)
RETURNS SETOF RECORD AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT %I FROM %I LIMIT 10',
        column_name, table_name
    );
END;
$$ LANGUAGE plpgsql;

-- Execute with parameters
CREATE FUNCTION get_user_by_column(col_name TEXT, col_value TEXT)
RETURNS SETOF users AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT * FROM users WHERE %I = $1',
        col_name
    ) USING col_value;
END;
$$ LANGUAGE plpgsql;
```

### Format Function

```sql
-- %s - string (no quoting)
-- %I - identifier (quoted if needed)
-- %L - literal (quoted + escaped)

SELECT format('SELECT * FROM %I WHERE name = %L', 'users', 'O''Brien');
-- Result: SELECT * FROM users WHERE name = 'O''Brien'

-- Positional
SELECT format('%1$s %2$s %1$s', 'A', 'B');
-- Result: A B A
```

---

## 7. Triggers

### Row-Level Trigger

```sql
-- Audit log trigger
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT,
    operation TEXT,
    old_data JSONB,
    new_data JSONB,
    changed_at TIMESTAMPTZ DEFAULT now(),
    changed_by TEXT DEFAULT current_user
);

CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (table_name, operation, old_data)
        VALUES (TG_TABLE_NAME, 'DELETE', to_jsonb(OLD));
        RETURN OLD;
        
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (table_name, operation, old_data, new_data)
        VALUES (TG_TABLE_NAME, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
        
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (table_name, operation, new_data)
        VALUES (TG_TABLE_NAME, 'INSERT', to_jsonb(NEW));
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
CREATE TRIGGER users_audit
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW
    EXECUTE FUNCTION audit_trigger();
```

### Statement-Level Trigger

```sql
CREATE OR REPLACE FUNCTION notify_changes()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('table_changes', TG_TABLE_NAME);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER notify_users_changes
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH STATEMENT
    EXECUTE FUNCTION notify_changes();
```

### Trigger Variables

```
TG_NAME        - Trigger name
TG_WHEN        - BEFORE, AFTER, INSTEAD OF
TG_OP          - INSERT, UPDATE, DELETE, TRUNCATE
TG_TABLE_NAME  - Table name
TG_TABLE_SCHEMA - Schema name
NEW            - New row (INSERT/UPDATE)
OLD            - Old row (UPDATE/DELETE)
TG_NARGS       - Number of arguments
TG_ARGV        - Arguments array
```

---

## 📝 Key Takeaways

1. **Functions return values** - Procedures can commit
2. **RETURNS TABLE for sets** - Queryable results
3. **Use EXCEPTION blocks** - Graceful error handling
4. **format() for dynamic SQL** - Safe identifier quoting
5. **Triggers for automation** - Audit, validation, derived data

---

## ✅ Day 24 Checklist

- [ ] Create functions with various return types
- [ ] Write procedure with transaction control
- [ ] Implement error handling
- [ ] Use cursors for large datasets
- [ ] Write dynamic SQL safely
- [ ] Create audit trigger
