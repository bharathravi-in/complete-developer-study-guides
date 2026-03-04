# PostgreSQL Interview Questions: Beginner Level

## 1. Basic Concepts

### Q1: What is PostgreSQL?
**Answer:** PostgreSQL is an open-source, object-relational database management system (ORDBMS) known for its reliability, extensibility, and SQL compliance. It supports both relational (SQL) and non-relational (JSON) queries.

**Key Features:**
- ACID compliant
- MVCC (Multi-Version Concurrency Control)
- Extensible (custom types, functions, operators)
- Rich indexing options
- Full-text search built-in
- JSON/JSONB support

---

### Q2: What is the difference between SQL and PostgreSQL?
**Answer:**
- **SQL** is a language standard for querying relational databases
- **PostgreSQL** is a database management system that implements SQL

PostgreSQL extends standard SQL with:
- Arrays
- JSONB data type
- Custom types and functions
- Window functions (advanced)
- Full-text search

---

### Q3: What are the different data types in PostgreSQL?
**Answer:**

| Category | Data Types |
|----------|------------|
| Numeric | INTEGER, BIGINT, DECIMAL, NUMERIC, REAL, DOUBLE PRECISION, SERIAL |
| Character | VARCHAR(n), CHAR(n), TEXT |
| Binary | BYTEA |
| Date/Time | DATE, TIME, TIMESTAMP, TIMESTAMPTZ, INTERVAL |
| Boolean | BOOLEAN |
| UUID | UUID |
| JSON | JSON, JSONB |
| Arrays | INTEGER[], TEXT[], etc. |
| Network | INET, CIDR, MACADDR |
| Geometric | POINT, LINE, POLYGON, CIRCLE |

---

### Q4: What is a Primary Key?
**Answer:** A primary key is a column (or set of columns) that uniquely identifies each row in a table.

**Properties:**
- Must be UNIQUE
- Cannot be NULL
- Only one per table
- Creates an index automatically

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL
);

-- Composite primary key
CREATE TABLE order_items (
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    PRIMARY KEY (order_id, product_id)
);
```

---

### Q5: What is a Foreign Key?
**Answer:** A foreign key is a column that creates a link between two tables by referencing the primary key of another table.

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total DECIMAL(10,2)
);

-- With explicit constraint name
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
```

**Actions:**
- `CASCADE` - Delete/update related rows
- `SET NULL` - Set to NULL
- `SET DEFAULT` - Set to default value
- `RESTRICT` - Prevent operation

---

## 2. Basic SQL Operations

### Q6: Write a query to create a table
**Answer:**
```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hire_date DATE DEFAULT CURRENT_DATE,
    salary DECIMAL(10,2) CHECK (salary > 0),
    department_id INTEGER REFERENCES departments(id),
    is_active BOOLEAN DEFAULT true
);
```

---

### Q7: What is the difference between DELETE, TRUNCATE, and DROP?
**Answer:**

| Command | Purpose | Rollback | Triggers | WHERE |
|---------|---------|----------|----------|-------|
| DELETE | Remove rows | Yes | Fires | Yes |
| TRUNCATE | Remove all rows | Yes* | No | No |
| DROP | Remove table | No | No | No |

```sql
-- DELETE: Slow, logged, can rollback
DELETE FROM users WHERE created_at < '2020-01-01';

-- TRUNCATE: Fast, resets sequences, less logging
TRUNCATE TABLE temp_data;
TRUNCATE TABLE temp_data RESTART IDENTITY;

-- DROP: Removes table completely
DROP TABLE temp_data;
DROP TABLE IF EXISTS temp_data CASCADE;
```

---

### Q8: Explain different types of JOINs
**Answer:**

```sql
-- INNER JOIN: Only matching rows
SELECT u.name, o.total
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN: All from left, matching from right
SELECT u.name, o.total
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
-- Users without orders will have NULL for order columns

-- RIGHT JOIN: All from right, matching from left
SELECT u.name, o.total
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id;

-- FULL OUTER JOIN: All rows from both
SELECT u.name, o.total
FROM users u
FULL OUTER JOIN orders o ON u.id = o.user_id;

-- CROSS JOIN: Cartesian product
SELECT * FROM colors CROSS JOIN sizes;
```

**Visual:**
```
INNER:    [  A ∩ B  ]
LEFT:     [ A (A ∩ B) ]
RIGHT:    [ (A ∩ B) B ]
FULL:     [ A (A ∩ B) B ]
```

---

### Q9: What is the difference between WHERE and HAVING?
**Answer:**

- **WHERE**: Filters rows BEFORE grouping
- **HAVING**: Filters groups AFTER aggregation

```sql
-- WHERE: Filter individual rows
SELECT department, COUNT(*)
FROM employees
WHERE salary > 50000      -- Filter rows first
GROUP BY department;

-- HAVING: Filter groups
SELECT department, AVG(salary) as avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 60000;  -- Filter after grouping

-- Combined
SELECT department, COUNT(*) as count
FROM employees
WHERE is_active = true        -- Filter rows
GROUP BY department
HAVING COUNT(*) > 5;          -- Filter groups
```

---

### Q10: What is NULL in PostgreSQL?
**Answer:** NULL represents an unknown or missing value. It is not the same as zero, empty string, or false.

```sql
-- NULL comparisons
SELECT * FROM users WHERE email = NULL;      -- Wrong!
SELECT * FROM users WHERE email IS NULL;     -- Correct

-- NULL in expressions
SELECT 5 + NULL;     -- NULL
SELECT NULL = NULL;  -- NULL (not true!)

-- COALESCE: First non-NULL value
SELECT COALESCE(phone, email, 'No contact') AS contact FROM users;

-- NULLIF: Returns NULL if equal
SELECT NULLIF(discount, 0) AS discount FROM products;

-- IS DISTINCT FROM: NULL-safe comparison
SELECT * FROM users WHERE email IS DISTINCT FROM 'test@example.com';
```

---

## 3. Indexes and Constraints

### Q11: What is an Index?
**Answer:** An index is a data structure that improves query performance by allowing the database to find rows without scanning the entire table.

```sql
-- Create index
CREATE INDEX idx_users_email ON users(email);

-- Unique index
CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Multi-column index
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date);

-- Partial index (subset of rows)
CREATE INDEX idx_active_users ON users(email) WHERE is_active = true;

-- Check if index is used
EXPLAIN SELECT * FROM users WHERE email = 'test@example.com';
```

**Types:** B-tree (default), Hash, GIN, GiST, BRIN

---

### Q12: What are Constraints?
**Answer:** Constraints enforce rules on data in a table.

```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,                          -- Primary Key
    sku VARCHAR(50) UNIQUE NOT NULL,                -- Unique + Not Null
    name VARCHAR(200) NOT NULL,                     -- Not Null
    price DECIMAL(10,2) CHECK (price > 0),          -- Check
    category_id INT REFERENCES categories(id),      -- Foreign Key
    status VARCHAR(20) DEFAULT 'active'             -- Default
);

-- Add constraint to existing table
ALTER TABLE products ADD CONSTRAINT positive_stock CHECK (stock >= 0);
```

---

### Q13: What is the difference between UNIQUE and PRIMARY KEY?
**Answer:**

| Feature | PRIMARY KEY | UNIQUE |
|---------|-------------|--------|
| NULL allowed | No | Yes (one NULL) |
| Per table | One only | Multiple allowed |
| Creates index | Yes | Yes |
| Identifies row | Yes | No |

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,        -- Only one
    email VARCHAR(255) UNIQUE,    -- Can have multiple UNIQUE
    phone VARCHAR(20) UNIQUE      -- Another UNIQUE constraint
);
```

---

## 4. Basic Functions

### Q14: Common Aggregate Functions
**Answer:**
```sql
-- COUNT
SELECT COUNT(*) FROM users;                    -- All rows
SELECT COUNT(email) FROM users;                -- Non-NULL emails
SELECT COUNT(DISTINCT department) FROM users;  -- Distinct values

-- SUM, AVG, MIN, MAX
SELECT 
    SUM(amount) AS total,
    AVG(amount) AS average,
    MIN(amount) AS minimum,
    MAX(amount) AS maximum
FROM orders;

-- STRING_AGG
SELECT department, STRING_AGG(name, ', ')
FROM employees
GROUP BY department;

-- ARRAY_AGG
SELECT department, ARRAY_AGG(name)
FROM employees
GROUP BY department;
```

---

### Q15: Common String Functions
**Answer:**
```sql
-- Length
SELECT LENGTH('Hello');              -- 5
SELECT CHAR_LENGTH('Hello');         -- 5

-- Case
SELECT UPPER('hello');               -- HELLO
SELECT LOWER('HELLO');               -- hello
SELECT INITCAP('hello world');       -- Hello World

-- Substring
SELECT SUBSTRING('PostgreSQL' FROM 1 FOR 4);  -- Post
SELECT LEFT('PostgreSQL', 4);                  -- Post
SELECT RIGHT('PostgreSQL', 3);                 -- SQL

-- Trim
SELECT TRIM('  hello  ');            -- 'hello'
SELECT LTRIM('  hello');             -- 'hello'
SELECT RTRIM('hello  ');             -- 'hello'

-- Concatenation
SELECT 'Hello' || ' ' || 'World';    -- Hello World
SELECT CONCAT('Hello', ' ', 'World');

-- Replace
SELECT REPLACE('Hello World', 'World', 'PostgreSQL');

-- Position
SELECT POSITION('SQL' IN 'PostgreSQL');  -- 8
```

---

### Q16: Common Date Functions
**Answer:**
```sql
-- Current date/time
SELECT CURRENT_DATE;                  -- 2024-01-15
SELECT CURRENT_TIME;                  -- 14:30:00
SELECT CURRENT_TIMESTAMP;             -- 2024-01-15 14:30:00+00
SELECT NOW();                         -- Same as CURRENT_TIMESTAMP

-- Extract parts
SELECT EXTRACT(YEAR FROM CURRENT_DATE);
SELECT EXTRACT(MONTH FROM CURRENT_DATE);
SELECT EXTRACT(DAY FROM CURRENT_DATE);

-- Date arithmetic
SELECT CURRENT_DATE + INTERVAL '7 days';
SELECT CURRENT_DATE - INTERVAL '1 month';
SELECT AGE(CURRENT_DATE, '2000-01-01');

-- Truncate
SELECT DATE_TRUNC('month', CURRENT_TIMESTAMP);  -- Start of month
SELECT DATE_TRUNC('year', CURRENT_TIMESTAMP);   -- Start of year

-- Format
SELECT TO_CHAR(CURRENT_TIMESTAMP, 'YYYY-MM-DD HH24:MI:SS');
```

---

## 5. Practice Questions

### Q17: Write a query to find the second highest salary
**Answer:**
```sql
-- Method 1: OFFSET
SELECT DISTINCT salary FROM employees
ORDER BY salary DESC
LIMIT 1 OFFSET 1;

-- Method 2: Subquery
SELECT MAX(salary) FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);

-- Method 3: DENSE_RANK
SELECT salary FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) as rank
    FROM employees
) t
WHERE rank = 2;
```

---

### Q18: Write a query to find duplicate emails
**Answer:**
```sql
SELECT email, COUNT(*)
FROM users
GROUP BY email
HAVING COUNT(*) > 1;

-- With details
SELECT * FROM users
WHERE email IN (
    SELECT email FROM users
    GROUP BY email
    HAVING COUNT(*) > 1
);
```

---

### Q19: Write a query to get the nth row
**Answer:**
```sql
-- Get 5th row
SELECT * FROM users
ORDER BY id
LIMIT 1 OFFSET 4;

-- Using ROW_NUMBER
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (ORDER BY id) as rn
    FROM users
) t
WHERE rn = 5;
```

---

### Q20: How do you add a column to an existing table?
**Answer:**
```sql
-- Add column
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Add with default
ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT false;

-- Add with constraint
ALTER TABLE users ADD COLUMN age INTEGER CHECK (age >= 0);

-- Drop column
ALTER TABLE users DROP COLUMN phone;

-- Rename column
ALTER TABLE users RENAME COLUMN phone TO phone_number;

-- Change data type
ALTER TABLE users ALTER COLUMN age TYPE SMALLINT;
```

---

## Quick Reference Card

```
CREATE TABLE     - Create new table
ALTER TABLE      - Modify table structure
DROP TABLE       - Delete table
INSERT INTO      - Add rows
UPDATE           - Modify rows
DELETE FROM      - Remove rows
SELECT           - Query data

WHERE            - Filter rows
GROUP BY         - Group rows
HAVING           - Filter groups
ORDER BY         - Sort results
LIMIT/OFFSET     - Pagination

JOIN             - Combine tables
UNION            - Combine results

CREATE INDEX     - Improve query speed
PRIMARY KEY      - Unique identifier
FOREIGN KEY      - Link tables
```
