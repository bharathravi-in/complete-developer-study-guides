# Day 25: CTEs & Recursive Queries

## 📚 Learning Objectives
- Master Common Table Expressions (CTEs)
- Implement recursive queries
- Understand CTE optimization
- Apply CTEs to real-world problems

---

## 1. CTE Basics

### What is a CTE?

```sql
-- CTE = Named temporary result set
-- Improves readability and reusability

-- Syntax
WITH cte_name AS (
    SELECT ...
)
SELECT * FROM cte_name;

-- Multiple CTEs
WITH 
    cte1 AS (SELECT ...),
    cte2 AS (SELECT ... FROM cte1),
    cte3 AS (SELECT ... FROM cte2)
SELECT * FROM cte3;
```

### Basic Examples

```sql
-- Simple CTE
WITH active_users AS (
    SELECT * FROM users WHERE is_active = true
)
SELECT name, email FROM active_users;

-- Multiple CTEs
WITH 
    orders_2024 AS (
        SELECT * FROM orders 
        WHERE EXTRACT(YEAR FROM order_date) = 2024
    ),
    customer_totals AS (
        SELECT 
            customer_id,
            SUM(total_amount) AS total_spent
        FROM orders_2024
        GROUP BY customer_id
    )
SELECT 
    c.name,
    ct.total_spent
FROM customers c
JOIN customer_totals ct ON c.id = ct.customer_id
ORDER BY ct.total_spent DESC;
```

### CTE vs Subquery

```sql
-- Subquery (repeated, harder to read)
SELECT * FROM orders
WHERE customer_id IN (
    SELECT id FROM customers WHERE country = 'US'
)
AND total_amount > (
    SELECT AVG(total_amount) 
    FROM orders
    WHERE customer_id IN (
        SELECT id FROM customers WHERE country = 'US'
    )
);

-- CTE (cleaner, reusable)
WITH 
    us_customers AS (
        SELECT id FROM customers WHERE country = 'US'
    ),
    us_orders AS (
        SELECT * FROM orders
        WHERE customer_id IN (SELECT id FROM us_customers)
    ),
    avg_order AS (
        SELECT AVG(total_amount) AS avg_amount FROM us_orders
    )
SELECT * FROM us_orders
WHERE total_amount > (SELECT avg_amount FROM avg_order);
```

---

## 2. CTE Modifiers

### MATERIALIZED vs NOT MATERIALIZED

```sql
-- MATERIALIZED: Force CTE to be evaluated once (cached)
WITH users_cte AS MATERIALIZED (
    SELECT * FROM users WHERE is_active = true
)
SELECT * FROM users_cte WHERE age > 30
UNION ALL  
SELECT * FROM users_cte WHERE country = 'US';
-- CTE evaluated ONCE, result reused

-- NOT MATERIALIZED: Inline as subquery (default in PG 12+)
WITH users_cte AS NOT MATERIALIZED (
    SELECT * FROM users WHERE is_active = true
)
SELECT * FROM users_cte WHERE age > 30;
-- CTE merged into main query, optimizer can use indexes
```

### When to Use MATERIALIZED

```sql
-- ✓ Use MATERIALIZED when:
-- - CTE is referenced multiple times
-- - CTE result is expensive and stable
-- - You need optimization barrier

WITH expensive_calc AS MATERIALIZED (
    SELECT customer_id, 
           calculate_score(customer_id) AS score  -- expensive function
    FROM customers
)
SELECT * FROM expensive_calc WHERE score > 80
UNION ALL
SELECT * FROM expensive_calc WHERE score BETWEEN 50 AND 80;

-- ✓ Use NOT MATERIALIZED when:
-- - CTE is referenced once
-- - Want indexes on base tables used
-- - Default behavior is fine
```

---

## 3. Writeable CTEs

### INSERT/UPDATE/DELETE in CTEs

```sql
-- Move data between tables
WITH deleted_orders AS (
    DELETE FROM orders
    WHERE order_date < '2020-01-01'
    RETURNING *
)
INSERT INTO archived_orders
SELECT * FROM deleted_orders;

-- Update and select affected rows
WITH updated AS (
    UPDATE products
    SET price = price * 1.1
    WHERE category = 'electronics'
    RETURNING id, name, price AS new_price
)
SELECT * FROM updated;

-- Cascade operations
WITH 
    order_ids AS (
        SELECT id FROM orders WHERE customer_id = 123
    ),
    deleted_items AS (
        DELETE FROM order_items
        WHERE order_id IN (SELECT id FROM order_ids)
        RETURNING *
    ),
    deleted_orders AS (
        DELETE FROM orders
        WHERE id IN (SELECT id FROM order_ids)
        RETURNING *
    )
SELECT 
    (SELECT COUNT(*) FROM deleted_orders) AS orders_deleted,
    (SELECT COUNT(*) FROM deleted_items) AS items_deleted;
```

### Upsert Pattern

```sql
-- Insert or update with CTE
WITH new_data (id, name, value) AS (
    VALUES (1, 'Product A', 100),
           (2, 'Product B', 200)
),
updated AS (
    UPDATE products p
    SET name = nd.name, value = nd.value
    FROM new_data nd
    WHERE p.id = nd.id
    RETURNING p.id
)
INSERT INTO products (id, name, value)
SELECT id, name, value FROM new_data
WHERE id NOT IN (SELECT id FROM updated);
```

---

## 4. Recursive CTEs

### Basic Syntax

```sql
WITH RECURSIVE cte_name AS (
    -- Base case (non-recursive term)
    SELECT ...
    
    UNION [ALL]
    
    -- Recursive case (references cte_name)
    SELECT ... FROM cte_name WHERE ...
)
SELECT * FROM cte_name;
```

### Simple Counter

```sql
-- Generate numbers 1-10
WITH RECURSIVE counter AS (
    -- Base case
    SELECT 1 AS n
    
    UNION ALL
    
    -- Recursive case
    SELECT n + 1 FROM counter WHERE n < 10
)
SELECT * FROM counter;
-- Result: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
```

### Hierarchical Data (Tree)

```sql
-- Employee hierarchy
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    manager_id INTEGER REFERENCES employees(id)
);

INSERT INTO employees (id, name, manager_id) VALUES
(1, 'CEO', NULL),
(2, 'CTO', 1),
(3, 'CFO', 1),
(4, 'Dev Lead', 2),
(5, 'Dev 1', 4),
(6, 'Dev 2', 4),
(7, 'Finance Manager', 3);

-- Get all subordinates of CTO (id=2)
WITH RECURSIVE subordinates AS (
    -- Base: Start with CTO
    SELECT id, name, manager_id, 0 AS level
    FROM employees
    WHERE id = 2
    
    UNION ALL
    
    -- Recursive: Find employees managed by current level
    SELECT e.id, e.name, e.manager_id, s.level + 1
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.id
)
SELECT 
    REPEAT('  ', level) || name AS hierarchy,
    level
FROM subordinates;

-- Result:
-- hierarchy          | level
-- CTO                | 0
--   Dev Lead         | 1
--     Dev 1          | 2
--     Dev 2          | 2
```

### Path Tracking

```sql
-- Track full path from root
WITH RECURSIVE org_tree AS (
    SELECT 
        id, 
        name, 
        manager_id,
        ARRAY[name] AS path,
        1 AS depth
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    SELECT 
        e.id,
        e.name,
        e.manager_id,
        ot.path || e.name,
        ot.depth + 1
    FROM employees e
    JOIN org_tree ot ON e.manager_id = ot.id
)
SELECT 
    id,
    name,
    array_to_string(path, ' > ') AS full_path
FROM org_tree;

-- Result:
-- id | name            | full_path
--  1 | CEO             | CEO
--  2 | CTO             | CEO > CTO
--  4 | Dev Lead        | CEO > CTO > Dev Lead
--  5 | Dev 1           | CEO > CTO > Dev Lead > Dev 1
```

### Cycle Detection

```sql
-- Prevent infinite loops with CYCLE clause (PG 14+)
WITH RECURSIVE subordinates AS (
    SELECT id, name, manager_id
    FROM employees
    WHERE id = 1
    
    UNION ALL
    
    SELECT e.id, e.name, e.manager_id
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.id
) CYCLE id SET is_cycle USING path
SELECT * FROM subordinates WHERE NOT is_cycle;

-- Pre-PG14 cycle detection
WITH RECURSIVE subordinates AS (
    SELECT 
        id, name, manager_id,
        ARRAY[id] AS visited,
        false AS has_cycle
    FROM employees
    WHERE id = 1
    
    UNION ALL
    
    SELECT 
        e.id, e.name, e.manager_id,
        s.visited || e.id,
        e.id = ANY(s.visited)
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.id
    WHERE NOT s.has_cycle
)
SELECT * FROM subordinates WHERE NOT has_cycle;
```

---

## 5. Real-World Examples

### Bill of Materials (BOM)

```sql
CREATE TABLE parts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    unit_cost NUMERIC
);

CREATE TABLE assemblies (
    parent_id INTEGER REFERENCES parts(id),
    child_id INTEGER REFERENCES parts(id),
    quantity INTEGER
);

-- Calculate total cost of product
WITH RECURSIVE bom AS (
    -- Start with top-level product
    SELECT 
        p.id,
        p.name,
        p.unit_cost,
        1 AS quantity,
        p.unit_cost AS total_cost
    FROM parts p
    WHERE p.id = 1  -- Product ID
    
    UNION ALL
    
    SELECT 
        p.id,
        p.name,
        p.unit_cost,
        a.quantity * bom.quantity,
        p.unit_cost * a.quantity * bom.quantity
    FROM parts p
    JOIN assemblies a ON p.id = a.child_id
    JOIN bom ON a.parent_id = bom.id
)
SELECT 
    name,
    SUM(quantity) AS total_quantity,
    SUM(total_cost) AS total_cost
FROM bom
WHERE id NOT IN (SELECT DISTINCT parent_id FROM assemblies)  -- Only leaf parts
GROUP BY name;
```

### Graph Shortest Path

```sql
CREATE TABLE routes (
    from_city VARCHAR(50),
    to_city VARCHAR(50),
    distance INTEGER
);

-- Find shortest path from A to E
WITH RECURSIVE paths AS (
    -- Start from source
    SELECT 
        from_city,
        to_city,
        distance,
        ARRAY[from_city, to_city] AS path
    FROM routes
    WHERE from_city = 'A'
    
    UNION ALL
    
    -- Extend paths
    SELECT 
        p.from_city,
        r.to_city,
        p.distance + r.distance,
        p.path || r.to_city
    FROM paths p
    JOIN routes r ON p.to_city = r.from_city
    WHERE NOT r.to_city = ANY(p.path)  -- No cycles
)
SELECT path, distance
FROM paths
WHERE to_city = 'E'
ORDER BY distance
LIMIT 1;
```

### Date Series Generation

```sql
-- Generate date range
WITH RECURSIVE date_series AS (
    SELECT DATE '2024-01-01' AS date
    
    UNION ALL
    
    SELECT date + 1
    FROM date_series
    WHERE date < '2024-01-31'
)
SELECT date FROM date_series;

-- Fill gaps in time series
WITH RECURSIVE date_range AS (
    SELECT MIN(event_date) AS date FROM events
    UNION ALL
    SELECT date + 1 FROM date_range
    WHERE date < (SELECT MAX(event_date) FROM events)
)
SELECT 
    dr.date,
    COALESCE(COUNT(e.id), 0) AS event_count
FROM date_range dr
LEFT JOIN events e ON e.event_date = dr.date
GROUP BY dr.date
ORDER BY dr.date;
```

---

## 6. Performance Considerations

```sql
-- 1. Limit recursion depth
WITH RECURSIVE tree AS (
    SELECT id, parent_id, 1 AS depth FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.parent_id, t.depth + 1
    FROM categories c
    JOIN tree t ON c.parent_id = t.id
    WHERE t.depth < 10  -- Limit depth!
)
SELECT * FROM tree;

-- 2. Use UNION ALL when duplicates impossible
-- UNION removes duplicates = slower
-- UNION ALL keeps all = faster

-- 3. Add indexes for join columns
CREATE INDEX idx_employees_manager ON employees(manager_id);

-- 4. Consider search/limit early
WITH RECURSIVE tree AS (...)
SELECT * FROM tree
WHERE name LIKE 'Dev%'  -- Filter after recursion
LIMIT 100;              -- Limit final results
```

---

## 📝 Key Takeaways

1. **CTEs improve readability** - Named, reusable subqueries
2. **MATERIALIZED controls evaluation** - Force cache or inline
3. **Writeable CTEs for complex DML** - DELETE...INSERT patterns
4. **Recursive for hierarchies** - Trees, graphs, sequences
5. **Always prevent infinite loops** - Use depth limit or CYCLE

---

## ✅ Day 25 Checklist

- [ ] Write multi-CTE query
- [ ] Use MATERIALIZED appropriately
- [ ] Implement data migration with writeable CTE
- [ ] Create recursive hierarchy query
- [ ] Add cycle detection
- [ ] Generate date series
