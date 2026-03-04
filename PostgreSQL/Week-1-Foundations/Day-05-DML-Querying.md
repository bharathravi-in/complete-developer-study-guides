# Day 5: DML + Querying

## 📚 Learning Objectives
- Master SELECT statement and all clauses
- Deep dive into filtering with WHERE
- Understand GROUP BY and HAVING
- Learn ORDER BY and pagination

---

## 1. INSERT Statement

### Basic Insert

```sql
-- Single row
INSERT INTO employees (name, email, salary) 
VALUES ('John Doe', 'john@example.com', 50000);

-- Multi-row insert
INSERT INTO employees (name, email, salary) VALUES
    ('Jane Smith', 'jane@example.com', 55000),
    ('Bob Wilson', 'bob@example.com', 48000),
    ('Alice Brown', 'alice@example.com', 62000);

-- Default values
INSERT INTO employees (name, email) 
VALUES ('Tim Cook', 'tim@example.com');  -- salary = default

INSERT INTO employees DEFAULT VALUES;  -- All defaults
```

### Insert with Returning

```sql
-- Get inserted data
INSERT INTO employees (name, email, salary)
VALUES ('New Employee', 'new@example.com', 50000)
RETURNING id, created_at;

-- Get all columns
INSERT INTO employees (name, email)
VALUES ('Another One', 'another@example.com')
RETURNING *;
```

### Insert from Query

```sql
-- Copy from another table
INSERT INTO employees_backup 
SELECT * FROM employees WHERE status = 'active';

-- Insert with transformation
INSERT INTO archived_orders (order_id, customer_name, total)
SELECT o.id, c.name, o.total
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'completed';
```

### Upsert (ON CONFLICT)

```sql
-- Insert or update
INSERT INTO products (sku, name, price)
VALUES ('SKU001', 'Widget', 29.99)
ON CONFLICT (sku) 
DO UPDATE SET 
    name = EXCLUDED.name,
    price = EXCLUDED.price,
    updated_at = NOW();

-- Insert or ignore
INSERT INTO user_visits (user_id, visited_at)
VALUES (123, NOW())
ON CONFLICT (user_id) DO NOTHING;

-- Conflict on constraint name
INSERT INTO products (sku, name)
VALUES ('SKU001', 'Widget')
ON CONFLICT ON CONSTRAINT uq_products_sku 
DO UPDATE SET name = EXCLUDED.name;

-- With WHERE clause
INSERT INTO products (sku, name, price)
VALUES ('SKU001', 'Widget', 29.99)
ON CONFLICT (sku) 
DO UPDATE SET price = EXCLUDED.price
WHERE products.price < EXCLUDED.price;  -- Only update if new price is higher
```

---

## 2. UPDATE Statement

### Basic Update

```sql
-- Single column
UPDATE employees SET salary = 55000 WHERE id = 1;

-- Multiple columns
UPDATE employees 
SET 
    salary = 60000,
    title = 'Senior Developer',
    updated_at = NOW()
WHERE id = 1;

-- Update with expression
UPDATE products SET price = price * 1.10;  -- 10% increase

-- Update with subquery
UPDATE employees 
SET department_id = (
    SELECT id FROM departments WHERE name = 'Engineering'
)
WHERE name = 'John Doe';
```

### Update with FROM

```sql
-- Update using JOIN
UPDATE orders o
SET status = 'vip_order'
FROM customers c
WHERE o.customer_id = c.id
AND c.tier = 'vip';

-- Complex update with multiple tables
UPDATE inventory i
SET quantity = i.quantity - oi.quantity
FROM order_items oi
JOIN orders o ON oi.order_id = o.id
WHERE i.product_id = oi.product_id
AND o.id = 12345;
```

### Update with Returning

```sql
UPDATE employees 
SET salary = salary * 1.10
WHERE department_id = 1
RETURNING id, name, salary AS new_salary;
```

---

## 3. DELETE Statement

### Basic Delete

```sql
-- Delete specific rows
DELETE FROM employees WHERE id = 1;

-- Delete with multiple conditions
DELETE FROM orders 
WHERE status = 'cancelled' 
AND created_at < NOW() - INTERVAL '1 year';

-- Delete all (use TRUNCATE for large tables)
DELETE FROM temp_data;
```

### Delete with USING

```sql
-- Delete with JOIN
DELETE FROM order_items oi
USING orders o
WHERE oi.order_id = o.id
AND o.status = 'cancelled';

-- Delete with subquery
DELETE FROM users
WHERE id IN (
    SELECT user_id 
    FROM user_sessions 
    WHERE last_activity < NOW() - INTERVAL '2 years'
);
```

### Delete with Returning

```sql
-- Get deleted rows
DELETE FROM expired_sessions 
WHERE expires_at < NOW()
RETURNING user_id, token;
```

---

## 4. SELECT Statement

### Basic Select

```sql
-- All columns
SELECT * FROM employees;

-- Specific columns
SELECT name, email, salary FROM employees;

-- With aliases
SELECT 
    first_name AS "First Name",
    last_name AS "Last Name",
    salary * 12 AS annual_salary
FROM employees;

-- Distinct values
SELECT DISTINCT department_id FROM employees;
SELECT DISTINCT ON (department_id) * FROM employees ORDER BY department_id, salary DESC;
```

### Column Expressions

```sql
-- String concatenation
SELECT first_name || ' ' || last_name AS full_name FROM employees;

-- Math operations
SELECT name, price, quantity, price * quantity AS total FROM order_items;

-- CASE expression
SELECT 
    name,
    salary,
    CASE 
        WHEN salary < 40000 THEN 'Entry'
        WHEN salary < 70000 THEN 'Mid'
        WHEN salary < 100000 THEN 'Senior'
        ELSE 'Executive'
    END AS level
FROM employees;

-- COALESCE (first non-null)
SELECT name, COALESCE(phone, email, 'No Contact') AS contact FROM users;

-- NULLIF (returns NULL if equal)
SELECT name, NULLIF(status, 'unknown') AS status FROM items;
```

---

## 5. WHERE Clause

### Comparison Operators

```sql
-- Basic comparisons
SELECT * FROM employees WHERE salary > 50000;
SELECT * FROM employees WHERE salary >= 50000;
SELECT * FROM employees WHERE salary < 50000;
SELECT * FROM employees WHERE salary <= 50000;
SELECT * FROM employees WHERE salary = 50000;
SELECT * FROM employees WHERE salary != 50000;
SELECT * FROM employees WHERE salary <> 50000;  -- Same as !=
```

### Logical Operators

```sql
-- AND
SELECT * FROM employees 
WHERE department_id = 1 AND salary > 50000;

-- OR
SELECT * FROM employees 
WHERE department_id = 1 OR department_id = 2;

-- NOT
SELECT * FROM employees WHERE NOT status = 'inactive';

-- Combining
SELECT * FROM employees 
WHERE (department_id = 1 OR department_id = 2)
AND salary > 50000
AND status != 'inactive';
```

### Range and Set Operators

```sql
-- BETWEEN (inclusive)
SELECT * FROM orders WHERE total BETWEEN 100 AND 500;
SELECT * FROM orders WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31';

-- IN
SELECT * FROM employees WHERE department_id IN (1, 2, 3);
SELECT * FROM products WHERE category IN ('Electronics', 'Books', 'Clothing');

-- NOT IN (⚠️ Beware of NULLs!)
SELECT * FROM employees WHERE department_id NOT IN (1, 2, 3);
-- If subquery contains NULL, NOT IN returns no rows!

-- EXISTS (preferred over IN for subqueries)
SELECT * FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);
```

### NULL Handling

```sql
-- IS NULL
SELECT * FROM employees WHERE phone IS NULL;

-- IS NOT NULL  
SELECT * FROM employees WHERE phone IS NOT NULL;

-- ⚠️ Wrong way (never equals NULL)
SELECT * FROM employees WHERE phone = NULL;  -- Returns nothing!

-- COALESCE for default
SELECT name, COALESCE(phone, 'N/A') FROM employees;

-- IS DISTINCT FROM (NULL-safe comparison)
SELECT * FROM t1, t2 
WHERE t1.col IS DISTINCT FROM t2.col;
```

### Pattern Matching

```sql
-- LIKE (case-sensitive)
SELECT * FROM users WHERE email LIKE '%@gmail.com';
SELECT * FROM users WHERE name LIKE 'John%';      -- Starts with
SELECT * FROM users WHERE name LIKE '%son';       -- Ends with
SELECT * FROM users WHERE name LIKE '%oh%';       -- Contains
SELECT * FROM users WHERE code LIKE 'A_B';        -- A, any char, B

-- ILIKE (case-insensitive PostgreSQL)
SELECT * FROM users WHERE name ILIKE '%john%';

-- SIMILAR TO (SQL regex)
SELECT * FROM users WHERE name SIMILAR TO '(John|Jane)%';

-- Regular expressions (~)
SELECT * FROM users WHERE email ~ '^[a-z]+@';           -- Case-sensitive
SELECT * FROM users WHERE email ~* '^[a-z]+@';          -- Case-insensitive
SELECT * FROM users WHERE email !~ 'gmail\.com$';       -- Does not match
```

---

## 6. GROUP BY

### Basic Grouping

```sql
-- Count per department
SELECT department_id, COUNT(*) AS employee_count
FROM employees
GROUP BY department_id;

-- Multiple columns
SELECT department_id, status, COUNT(*)
FROM employees
GROUP BY department_id, status;

-- With expressions
SELECT 
    DATE_TRUNC('month', order_date) AS month,
    COUNT(*) AS orders,
    SUM(total) AS revenue
FROM orders
GROUP BY DATE_TRUNC('month', order_date);
```

### Aggregate Functions

```sql
SELECT 
    department_id,
    COUNT(*) AS total,
    COUNT(phone) AS with_phone,        -- Counts non-null values
    SUM(salary) AS total_salary,
    AVG(salary) AS avg_salary,
    MIN(salary) AS min_salary,
    MAX(salary) AS max_salary,
    ROUND(AVG(salary), 2) AS avg_rounded
FROM employees
GROUP BY department_id;

-- String aggregation
SELECT 
    department_id,
    STRING_AGG(name, ', ' ORDER BY name) AS employees
FROM employees
GROUP BY department_id;

-- Array aggregation
SELECT 
    department_id,
    ARRAY_AGG(name ORDER BY hire_date) AS employees
FROM employees
GROUP BY department_id;

-- JSON aggregation
SELECT 
    department_id,
    JSONB_AGG(JSONB_BUILD_OBJECT('name', name, 'salary', salary)) AS employees
FROM employees
GROUP BY department_id;
```

### GROUPING SETS, ROLLUP, CUBE

```sql
-- GROUPING SETS (multiple groupings in one query)
SELECT region, product, SUM(sales)
FROM sales_data
GROUP BY GROUPING SETS (
    (region, product),  -- Group by both
    (region),           -- Subtotal by region
    (product),          -- Subtotal by product
    ()                  -- Grand total
);

-- ROLLUP (hierarchical aggregation)
SELECT region, country, city, SUM(sales)
FROM sales_data
GROUP BY ROLLUP (region, country, city);
-- Produces: (region, country, city), (region, country), (region), ()

-- CUBE (all combinations)
SELECT region, product, SUM(sales)
FROM sales_data
GROUP BY CUBE (region, product);
-- Produces: (region, product), (region), (product), ()
```

---

## 7. HAVING Clause

HAVING filters groups (after GROUP BY), while WHERE filters rows (before GROUP BY).

```sql
-- Filter groups by aggregate
SELECT department_id, AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id
HAVING AVG(salary) > 50000;

-- Multiple conditions
SELECT department_id, COUNT(*) AS count, AVG(salary)
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 5 AND AVG(salary) BETWEEN 40000 AND 80000;

-- With WHERE and HAVING
SELECT department_id, AVG(salary) AS avg_salary
FROM employees
WHERE status = 'active'              -- Filter rows first
GROUP BY department_id
HAVING AVG(salary) > 50000;          -- Then filter groups
```

### WHERE vs HAVING

```sql
-- ✅ WHERE for row filtering (more efficient)
SELECT department_id, COUNT(*)
FROM employees
WHERE hire_date > '2020-01-01'
GROUP BY department_id;

-- ✅ HAVING for aggregate filtering
SELECT department_id, COUNT(*)
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 10;

-- ❌ Don't use HAVING for non-aggregate conditions
SELECT department_id, COUNT(*)
FROM employees
GROUP BY department_id
HAVING department_id IN (1, 2, 3);  -- Use WHERE instead!
```

---

## 8. ORDER BY

### Basic Ordering

```sql
-- Ascending (default)
SELECT * FROM employees ORDER BY salary;
SELECT * FROM employees ORDER BY salary ASC;

-- Descending
SELECT * FROM employees ORDER BY salary DESC;

-- Multiple columns
SELECT * FROM employees ORDER BY department_id, salary DESC;

-- By position
SELECT name, salary FROM employees ORDER BY 2 DESC;  -- Order by 2nd column

-- By alias
SELECT first_name || ' ' || last_name AS full_name
FROM employees
ORDER BY full_name;
```

### NULL Handling in ORDER

```sql
-- NULLS FIRST (default for DESC)
SELECT * FROM employees ORDER BY phone NULLS FIRST;

-- NULLS LAST (default for ASC)
SELECT * FROM employees ORDER BY phone NULLS LAST;

-- Custom NULL handling
SELECT * FROM employees 
ORDER BY phone DESC NULLS LAST;
```

### Expression Ordering

```sql
-- Order by expression
SELECT * FROM products ORDER BY price * quantity DESC;

-- Order by CASE
SELECT * FROM tasks
ORDER BY 
    CASE priority
        WHEN 'high' THEN 1
        WHEN 'medium' THEN 2
        WHEN 'low' THEN 3
    END;
```

---

## 9. LIMIT and OFFSET (Pagination)

### Basic Pagination

```sql
-- First 10 rows
SELECT * FROM products ORDER BY id LIMIT 10;

-- Skip first 20, get next 10 (page 3 with 10 per page)
SELECT * FROM products ORDER BY id LIMIT 10 OFFSET 20;

-- Alternative syntax
SELECT * FROM products ORDER BY id FETCH FIRST 10 ROWS ONLY;
SELECT * FROM products ORDER BY id OFFSET 20 FETCH NEXT 10 ROWS ONLY;
```

### Pagination Problems

```sql
-- ⚠️ OFFSET is slow for large values
SELECT * FROM large_table ORDER BY id LIMIT 10 OFFSET 1000000;
-- PostgreSQL must scan 1,000,010 rows!

-- ✅ Better: Keyset pagination (cursor-based)
-- Page 1
SELECT * FROM products ORDER BY id LIMIT 10;

-- Next page (assuming last id was 100)
SELECT * FROM products WHERE id > 100 ORDER BY id LIMIT 10;

-- Previous page (assuming first id was 91)
SELECT * FROM products WHERE id < 91 ORDER BY id DESC LIMIT 10;
```

### Total Count with Pagination

```sql
-- Method 1: Separate count query
SELECT COUNT(*) FROM products WHERE category = 'Electronics';
SELECT * FROM products WHERE category = 'Electronics' 
ORDER BY id LIMIT 10 OFFSET 0;

-- Method 2: Window function (one query)
SELECT *, COUNT(*) OVER() AS total_count
FROM products
WHERE category = 'Electronics'
ORDER BY id
LIMIT 10 OFFSET 0;
```

---

## 🔬 Hands-On Practice

### Sample Data Setup

```sql
-- Create tables
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    department_id INT REFERENCES departments(id),
    salary NUMERIC(10,2),
    hire_date DATE DEFAULT CURRENT_DATE,
    status VARCHAR(20) DEFAULT 'active'
);

-- Insert data
INSERT INTO departments (name) VALUES 
    ('Engineering'), ('Sales'), ('Marketing'), ('HR');

INSERT INTO employees (name, email, department_id, salary, hire_date) VALUES
    ('John Doe', 'john@example.com', 1, 75000, '2020-03-15'),
    ('Jane Smith', 'jane@example.com', 1, 82000, '2019-07-20'),
    ('Bob Wilson', 'bob@example.com', 2, 65000, '2021-01-10'),
    ('Alice Brown', 'alice@example.com', 2, 71000, '2020-11-05'),
    ('Charlie Lee', 'charlie@example.com', 3, 58000, '2022-06-01'),
    ('Diana Ross', 'diana@example.com', 1, 95000, '2018-09-12'),
    ('Eve Johnson', 'eve@example.com', 4, 62000, '2021-08-22'),
    ('Frank White', 'frank@example.com', 2, 78000, '2019-12-01');
```

### Practice Queries

```sql
-- 1. Employees earning above average
SELECT * FROM employees 
WHERE salary > (SELECT AVG(salary) FROM employees);

-- 2. Department summary
SELECT 
    d.name AS department,
    COUNT(e.id) AS employees,
    COALESCE(ROUND(AVG(e.salary), 2), 0) AS avg_salary,
    COALESCE(SUM(e.salary), 0) AS total_salary
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id
GROUP BY d.id, d.name
ORDER BY total_salary DESC;

-- 3. Employees with their rank in department
SELECT 
    name,
    department_id,
    salary,
    RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_rank
FROM employees;

-- 4. Top 3 earners per department
SELECT * FROM (
    SELECT 
        name,
        department_id,
        salary,
        ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn
    FROM employees
) ranked
WHERE rn <= 3;

-- 5. Year-over-year hire comparison
SELECT 
    EXTRACT(YEAR FROM hire_date) AS year,
    COUNT(*) AS hires,
    LAG(COUNT(*)) OVER (ORDER BY EXTRACT(YEAR FROM hire_date)) AS prev_year
FROM employees
GROUP BY EXTRACT(YEAR FROM hire_date)
ORDER BY year;
```

---

## 📝 Key Takeaways

1. **Use RETURNING** - Get inserted/updated/deleted data in one query
2. **ON CONFLICT for upserts** - Elegant insert-or-update
3. **Beware NOT IN with NULLs** - Use NOT EXISTS instead
4. **HAVING vs WHERE** - WHERE filters rows, HAVING filters groups
5. **Avoid OFFSET for large pages** - Use keyset pagination
6. **DISTINCT ON** - PostgreSQL-specific powerful feature

---

## ✅ Day 5 Checklist

- [ ] Practice INSERT with RETURNING
- [ ] Master ON CONFLICT (upsert)
- [ ] Use complex WHERE conditions
- [ ] GROUP BY with multiple aggregates
- [ ] Understand WHERE vs HAVING
- [ ] Implement keyset pagination
