# Day 6: Joins & Advanced Querying

## 📚 Learning Objectives
- Master all JOIN types
- Understand self-joins and cross joins
- Learn subqueries (scalar, table, correlated)
- Compare EXISTS vs IN performance

---

## 1. JOIN Fundamentals

### Visual Representation

```
Table A: employees          Table B: departments
+----+--------+--------+    +----+------------+
| id | name   | dept_id|    | id | name       |
+----+--------+--------+    +----+------------+
| 1  | John   | 1      |    | 1  | Engineering|
| 2  | Jane   | 2      |    | 2  | Sales      |
| 3  | Bob    | NULL   |    | 3  | Marketing  |
| 4  | Alice  | 1      |    +----+------------+
+----+--------+--------+

INNER JOIN: Only matching rows (John, Jane, Alice)
LEFT JOIN:  All from A, matching from B (includes Bob with NULL dept)
RIGHT JOIN: All from B, matching from A (includes Marketing with NULL employees)
FULL JOIN:  All from both (Bob + Marketing unmapped)
```

---

## 2. INNER JOIN

Returns only rows with matches in both tables.

```sql
-- Explicit INNER JOIN (preferred)
SELECT e.name, d.name AS department
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;

-- Implicit join (old style, avoid)
SELECT e.name, d.name
FROM employees e, departments d
WHERE e.department_id = d.id;

-- Multiple conditions
SELECT e.name, p.name AS project
FROM employees e
INNER JOIN employee_projects ep ON e.id = ep.employee_id
INNER JOIN projects p ON ep.project_id = p.id
WHERE p.status = 'active';

-- Join with complex condition
SELECT o.id, c.name
FROM orders o
INNER JOIN customers c 
ON o.customer_id = c.id 
AND c.status = 'active'
AND o.total > 1000;
```

### Using USING Clause

```sql
-- When column names match
SELECT e.name, d.name AS department
FROM employees e
INNER JOIN departments d USING (department_id);

-- Equivalent to
SELECT e.name, d.name AS department
FROM employees e
INNER JOIN departments d ON e.department_id = d.department_id;
```

### Natural Join (Use with Caution)

```sql
-- Joins on all matching column names (implicit)
SELECT * FROM employees NATURAL JOIN departments;
-- ⚠️ Risky: If schemas change, join conditions change silently
```

---

## 3. LEFT JOIN (LEFT OUTER JOIN)

Returns all rows from left table, with NULLs for non-matching right table.

```sql
-- All employees, even without departments
SELECT e.name, d.name AS department
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;

-- Find orphan records (no match)
SELECT e.name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id
WHERE d.id IS NULL;  -- Employees without department

-- Multiple left joins
SELECT 
    c.name AS customer,
    o.id AS order_id,
    oi.product_id
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
LEFT JOIN order_items oi ON o.id = oi.order_id;
```

### Left Join vs Inner Join Performance

```sql
-- LEFT JOIN may return more rows
-- Use INNER JOIN when you only need matches

-- Example: Get all products with their categories
SELECT p.name, c.name AS category
FROM products p
LEFT JOIN categories c ON p.category_id = c.id;

-- If all products MUST have a category, use INNER JOIN
SELECT p.name, c.name AS category
FROM products p
INNER JOIN categories c ON p.category_id = c.id;
```

---

## 4. RIGHT JOIN (RIGHT OUTER JOIN)

Returns all rows from right table, with NULLs for non-matching left table.

```sql
-- All departments, even without employees
SELECT e.name, d.name AS department
FROM employees e
RIGHT JOIN departments d ON e.department_id = d.id;

-- Same as LEFT JOIN with tables swapped
SELECT e.name, d.name AS department
FROM departments d
LEFT JOIN employees e ON d.id = e.department_id;
```

---

## 5. FULL OUTER JOIN

Returns all rows from both tables, with NULLs where no match exists.

```sql
-- All employees and all departments
SELECT e.name AS employee, d.name AS department
FROM employees e
FULL OUTER JOIN departments d ON e.department_id = d.id;

-- Find unmatched records from both sides
SELECT e.name AS employee, d.name AS department
FROM employees e
FULL OUTER JOIN departments d ON e.department_id = d.id
WHERE e.id IS NULL OR d.id IS NULL;
```

### Use Case: Data Reconciliation

```sql
-- Compare two tables
SELECT 
    COALESCE(a.id, b.id) AS id,
    a.value AS source_a,
    b.value AS source_b,
    CASE 
        WHEN a.id IS NULL THEN 'Only in B'
        WHEN b.id IS NULL THEN 'Only in A'
        WHEN a.value != b.value THEN 'Different'
        ELSE 'Match'
    END AS status
FROM table_a a
FULL OUTER JOIN table_b b ON a.id = b.id
WHERE a.id IS NULL OR b.id IS NULL OR a.value != b.value;
```

---

## 6. CROSS JOIN

Returns Cartesian product (all combinations).

```sql
-- All combinations of products and colors
SELECT p.name, c.color
FROM products p
CROSS JOIN colors c;

-- Equivalent syntax
SELECT p.name, c.color
FROM products p, colors c;

-- Practical use: Generate date series
SELECT d.date, s.status
FROM generate_series('2024-01-01'::date, '2024-01-31'::date, '1 day') AS d(date)
CROSS JOIN (VALUES ('open'), ('closed')) AS s(status);
```

### Use Case: Calendar with All Products

```sql
-- Sales report with zeros for missing dates
WITH dates AS (
    SELECT generate_series(
        '2024-01-01'::date, 
        '2024-01-31'::date, 
        '1 day'
    )::date AS date
),
products AS (
    SELECT DISTINCT product_id FROM sales
)
SELECT 
    d.date,
    p.product_id,
    COALESCE(s.quantity, 0) AS quantity
FROM dates d
CROSS JOIN products p
LEFT JOIN sales s ON s.sale_date = d.date AND s.product_id = p.product_id
ORDER BY d.date, p.product_id;
```

---

## 7. SELF JOIN

Joining a table with itself.

```sql
-- Employee and their manager
SELECT 
    e.name AS employee,
    m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- Find employees in same department
SELECT 
    e1.name AS employee1,
    e2.name AS employee2,
    d.name AS department
FROM employees e1
INNER JOIN employees e2 
    ON e1.department_id = e2.department_id 
    AND e1.id < e2.id  -- Avoid duplicates and self-match
INNER JOIN departments d ON e1.department_id = d.id;

-- Hierarchical query (manager chain)
WITH RECURSIVE hierarchy AS (
    SELECT id, name, manager_id, 1 AS level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    SELECT e.id, e.name, e.manager_id, h.level + 1
    FROM employees e
    INNER JOIN hierarchy h ON e.manager_id = h.id
)
SELECT * FROM hierarchy ORDER BY level, name;
```

---

## 8. Subqueries

### Scalar Subqueries (Single Value)

```sql
-- In SELECT
SELECT 
    name,
    salary,
    (SELECT AVG(salary) FROM employees) AS avg_salary,
    salary - (SELECT AVG(salary) FROM employees) AS diff
FROM employees;

-- In WHERE
SELECT * FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);

-- In FROM
SELECT * FROM (
    SELECT department_id, AVG(salary) AS avg_sal
    FROM employees
    GROUP BY department_id
) dept_avg
WHERE avg_sal > 50000;
```

### Table Subqueries

```sql
-- IN subquery
SELECT * FROM employees
WHERE department_id IN (
    SELECT id FROM departments WHERE location = 'NYC'
);

-- NOT IN subquery (⚠️ beware of NULLs)
SELECT * FROM employees
WHERE department_id NOT IN (
    SELECT id FROM departments WHERE status = 'inactive'
    -- If any result is NULL, entire NOT IN returns false!
);

-- ANY/SOME comparison
SELECT * FROM products
WHERE price > ANY (SELECT price FROM competitor_prices);

-- ALL comparison
SELECT * FROM products
WHERE price < ALL (SELECT price FROM competitor_prices);
```

### Correlated Subqueries

Subquery references the outer query.

```sql
-- Employees earning more than department average
SELECT e1.name, e1.salary, e1.department_id
FROM employees e1
WHERE e1.salary > (
    SELECT AVG(e2.salary)
    FROM employees e2
    WHERE e2.department_id = e1.department_id  -- Correlated
);

-- Latest order per customer
SELECT c.name, o.id AS order_id, o.order_date
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
WHERE o.order_date = (
    SELECT MAX(o2.order_date)
    FROM orders o2
    WHERE o2.customer_id = c.id  -- Correlated
);
```

---

## 9. EXISTS vs IN

### EXISTS

```sql
-- Customers with at least one order
SELECT c.name
FROM customers c
WHERE EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.id
);

-- NOT EXISTS
SELECT c.name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.id
);
```

### IN

```sql
-- Same result as EXISTS above
SELECT c.name
FROM customers c
WHERE c.id IN (
    SELECT customer_id FROM orders
);

-- NOT IN (⚠️ NULL issues!)
SELECT c.name
FROM customers c
WHERE c.id NOT IN (
    SELECT customer_id FROM orders
    WHERE customer_id IS NOT NULL  -- Must filter NULLs!
);
```

### Performance Comparison

| Scenario | EXISTS | IN |
|----------|--------|-----|
| Large subquery | ✅ Better (stops early) | ❌ Evaluates all |
| Small subquery | Similar | Similar |
| Indexed columns | Both efficient | Both efficient |
| NULL handling | ✅ Safe | ⚠️ NOT IN issues |
| Readability | More explicit | More concise |

```sql
-- EXISTS is generally safer and often faster
-- Optimizer may rewrite IN to EXISTS internally

-- Recommended pattern
SELECT c.name
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);

-- Instead of
SELECT c.name  
FROM customers c
WHERE c.id IN (SELECT customer_id FROM orders);
```

### Performance Test

```sql
-- Explain both approaches
EXPLAIN ANALYZE
SELECT c.name FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

EXPLAIN ANALYZE
SELECT c.name FROM customers c
WHERE c.id IN (SELECT customer_id FROM orders);
```

---

## 10. Lateral Joins

LATERAL allows a subquery to reference columns from preceding tables.

```sql
-- Top 3 orders per customer
SELECT c.name, recent_orders.*
FROM customers c
CROSS JOIN LATERAL (
    SELECT o.id, o.total, o.order_date
    FROM orders o
    WHERE o.customer_id = c.id
    ORDER BY o.order_date DESC
    LIMIT 3
) recent_orders;

-- Equivalent to correlated subquery but more flexible
-- Can return multiple rows and columns

-- Running total with LATERAL
SELECT 
    t.month,
    t.revenue,
    running.total AS running_total
FROM monthly_sales t
CROSS JOIN LATERAL (
    SELECT SUM(revenue) AS total
    FROM monthly_sales
    WHERE month <= t.month
) running;
```

---

## 11. Join Optimization Tips

### Index Recommendations

```sql
-- Ensure foreign keys are indexed
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);

-- Composite indexes for common joins
CREATE INDEX idx_orders_customer_date 
ON orders(customer_id, order_date DESC);
```

### Query Patterns

```sql
-- ✅ Good: Filter early
SELECT c.name, o.total
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
WHERE c.status = 'active'      -- Filter reduces rows early
AND o.order_date > '2024-01-01';

-- ❌ Less efficient: Filter late
SELECT c.name, o.total
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
WHERE UPPER(c.name) LIKE 'A%';  -- Function prevents index use

-- ✅ Better: Create expression index or filter differently
CREATE INDEX idx_customers_name_upper ON customers(UPPER(name));
```

---

## 🔬 Hands-On Practice

### Setup

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255),
    status VARCHAR(20) DEFAULT 'active'
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    order_date DATE DEFAULT CURRENT_DATE,
    total NUMERIC(10,2),
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    product_id INT,
    quantity INT,
    price NUMERIC(10,2)
);

-- Insert sample data
INSERT INTO customers (name, email) VALUES
    ('John Doe', 'john@example.com'),
    ('Jane Smith', 'jane@example.com'),
    ('Bob Wilson', 'bob@example.com'),
    ('Alice Brown', 'alice@example.com');

INSERT INTO orders (customer_id, order_date, total, status) VALUES
    (1, '2024-01-15', 150.00, 'completed'),
    (1, '2024-02-20', 250.00, 'completed'),
    (2, '2024-01-10', 75.00, 'completed'),
    (2, '2024-03-05', 320.00, 'pending'),
    (3, '2024-02-28', 180.00, 'completed');
-- Note: Customer 4 (Alice) has no orders
```

### Practice Queries

```sql
-- 1. All customers with their order counts
SELECT 
    c.name,
    COUNT(o.id) AS order_count,
    COALESCE(SUM(o.total), 0) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name
ORDER BY total_spent DESC;

-- 2. Customers without orders
SELECT c.name
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
WHERE o.id IS NULL;

-- Alternative with NOT EXISTS
SELECT c.name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
);

-- 3. Customers with above-average order total
SELECT DISTINCT c.name
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
WHERE o.total > (SELECT AVG(total) FROM orders);

-- 4. Latest order per customer
SELECT c.name, o.id, o.order_date, o.total
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
WHERE o.order_date = (
    SELECT MAX(o2.order_date)
    FROM orders o2
    WHERE o2.customer_id = c.id
);

-- Alternative with LATERAL
SELECT c.name, latest.*
FROM customers c
CROSS JOIN LATERAL (
    SELECT id, order_date, total
    FROM orders
    WHERE customer_id = c.id
    ORDER BY order_date DESC
    LIMIT 1
) latest;

-- 5. Running total of orders
SELECT 
    o.id,
    o.order_date,
    o.total,
    SUM(o.total) OVER (ORDER BY o.order_date) AS running_total
FROM orders o
ORDER BY o.order_date;
```

---

## 📝 Key Takeaways

1. **Use explicit JOIN syntax** - Clearer than comma-separated tables
2. **LEFT JOIN for optional relationships** - But use INNER when matches required
3. **Beware NOT IN with NULLs** - Use NOT EXISTS instead
4. **EXISTS stops early** - Often more efficient than IN
5. **LATERAL for row-dependent subqueries** - Powerful for top-N per group
6. **Index your foreign keys** - Essential for join performance

---

## ✅ Day 6 Checklist

- [ ] Practice all JOIN types
- [ ] Write self-join queries
- [ ] Compare EXISTS vs IN
- [ ] Use correlated subqueries
- [ ] Implement LATERAL joins
- [ ] Check EXPLAIN plans for joins
