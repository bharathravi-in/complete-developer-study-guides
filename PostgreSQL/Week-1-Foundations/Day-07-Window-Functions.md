# Day 7: Window Functions (Interview Favorite)

## 📚 Learning Objectives
- Master ROW_NUMBER, RANK, DENSE_RANK
- Learn LEAD, LAG for row comparison
- Understand PARTITION BY
- Practice aggregate window functions
- Master frame clauses

---

## 1. Window Functions Overview

### What Are Window Functions?

Window functions perform calculations across a set of rows related to the current row, without collapsing rows like GROUP BY.

```sql
-- GROUP BY collapses rows
SELECT department_id, AVG(salary) 
FROM employees 
GROUP BY department_id;
-- Result: One row per department

-- Window function preserves rows
SELECT 
    name, 
    department_id, 
    salary,
    AVG(salary) OVER (PARTITION BY department_id) AS dept_avg
FROM employees;
-- Result: All employee rows with their department average
```

### Syntax Structure

```sql
function_name(arguments) OVER (
    [PARTITION BY partition_expression]
    [ORDER BY sort_expression]
    [frame_clause]
)
```

---

## 2. ROW_NUMBER()

Assigns unique sequential numbers to rows.

```sql
-- Sequential numbers for all rows
SELECT 
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS rank,
    name, 
    salary
FROM employees;

-- Reset numbering per partition
SELECT 
    ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS dept_rank,
    name, 
    department_id,
    salary
FROM employees;
```

### Use Case: Top N per Group

```sql
-- Top 3 earners per department
SELECT * FROM (
    SELECT 
        ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rn,
        name,
        department_id,
        salary
    FROM employees
) ranked
WHERE rn <= 3;

-- Alternative with LATERAL
SELECT d.name AS department, e.*
FROM departments d
CROSS JOIN LATERAL (
    SELECT name, salary
    FROM employees
    WHERE department_id = d.id
    ORDER BY salary DESC
    LIMIT 3
) e;
```

### Use Case: Pagination

```sql
-- Page 3 (rows 21-30)
WITH numbered AS (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY created_at DESC) AS rn,
        *
    FROM products
)
SELECT * FROM numbered WHERE rn BETWEEN 21 AND 30;
```

### Use Case: Deduplication

```sql
-- Keep only the latest record per email
DELETE FROM users
WHERE id IN (
    SELECT id FROM (
        SELECT 
            id,
            ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at DESC) AS rn
        FROM users
    ) t
    WHERE rn > 1
);

-- Select deduplicated data
SELECT * FROM (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at DESC) AS rn
    FROM users
) t
WHERE rn = 1;
```

---

## 3. RANK() and DENSE_RANK()

### Difference Between Them

```
salary: 100, 100, 90, 80

ROW_NUMBER(): 1, 2, 3, 4  (no ties)
RANK():       1, 1, 3, 4  (skip after tie)
DENSE_RANK(): 1, 1, 2, 3  (no skip)
```

```sql
SELECT 
    name,
    salary,
    ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num,
    RANK() OVER (ORDER BY salary DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rank
FROM employees;
```

### Use Case: Competition Ranking

```sql
-- Leaderboard with ties
SELECT 
    player_name,
    score,
    RANK() OVER (ORDER BY score DESC) AS position
FROM game_scores;

-- Percentile ranking
SELECT 
    name,
    salary,
    PERCENT_RANK() OVER (ORDER BY salary) AS percentile,
    CUME_DIST() OVER (ORDER BY salary) AS cumulative_dist
FROM employees;
```

### Use Case: Find Records at Specific Rank

```sql
-- Get 2nd highest salary (handles ties)
SELECT DISTINCT salary
FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) AS dr
    FROM employees
) t
WHERE dr = 2;

-- Top 10% performers
SELECT * FROM (
    SELECT 
        *,
        NTILE(10) OVER (ORDER BY performance_score DESC) AS decile
    FROM employees
) t
WHERE decile = 1;
```

---

## 4. NTILE()

Divides rows into N buckets.

```sql
-- Divide into quartiles
SELECT 
    name,
    salary,
    NTILE(4) OVER (ORDER BY salary) AS quartile
FROM employees;

-- Segment customers by spend
SELECT 
    name,
    total_purchases,
    CASE NTILE(5) OVER (ORDER BY total_purchases DESC)
        WHEN 1 THEN 'Premium'
        WHEN 2 THEN 'Gold'
        WHEN 3 THEN 'Silver'
        WHEN 4 THEN 'Bronze'
        ELSE 'Basic'
    END AS tier
FROM customers;
```

---

## 5. LEAD() and LAG()

Access data from other rows without self-join.

### LAG() - Previous Row

```sql
-- Compare with previous row
SELECT 
    order_date,
    total,
    LAG(total) OVER (ORDER BY order_date) AS prev_total,
    total - LAG(total) OVER (ORDER BY order_date) AS change
FROM orders;

-- With default value
SELECT 
    order_date,
    total,
    LAG(total, 1, 0) OVER (ORDER BY order_date) AS prev_total
FROM orders;

-- Look back multiple rows
SELECT 
    month,
    revenue,
    LAG(revenue, 3) OVER (ORDER BY month) AS same_month_last_quarter
FROM monthly_sales;
```

### LEAD() - Next Row

```sql
-- Calculate time to next event
SELECT 
    event_name,
    event_time,
    LEAD(event_time) OVER (ORDER BY event_time) AS next_event,
    LEAD(event_time) OVER (ORDER BY event_time) - event_time AS gap
FROM events;

-- Find gaps in sequence
SELECT * FROM (
    SELECT 
        id,
        LEAD(id) OVER (ORDER BY id) AS next_id
    FROM items
) t
WHERE next_id - id > 1;  -- Gap found
```

### Use Case: Month-over-Month Growth

```sql
SELECT 
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_month,
    ROUND(
        (revenue - LAG(revenue) OVER (ORDER BY month)) / 
        LAG(revenue) OVER (ORDER BY month) * 100, 
        2
    ) AS mom_growth_pct
FROM monthly_sales;
```

### Use Case: Session Analysis

```sql
-- Group events into sessions (30 min gap = new session)
SELECT 
    user_id,
    event_time,
    CASE 
        WHEN event_time - LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) 
             > INTERVAL '30 minutes'
        THEN 1 ELSE 0 
    END AS new_session
FROM user_events;

-- Actually assign session IDs
WITH session_starts AS (
    SELECT 
        *,
        CASE 
            WHEN event_time - LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) 
                 > INTERVAL '30 minutes'
            OR LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) IS NULL
            THEN 1 ELSE 0 
        END AS is_session_start
    FROM user_events
)
SELECT 
    *,
    SUM(is_session_start) OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
FROM session_starts;
```

---

## 6. FIRST_VALUE() and LAST_VALUE()

```sql
-- First and last in partition
SELECT 
    name,
    department_id,
    salary,
    FIRST_VALUE(name) OVER (PARTITION BY department_id ORDER BY salary DESC) AS top_earner,
    LAST_VALUE(name) OVER (
        PARTITION BY department_id 
        ORDER BY salary DESC
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS lowest_earner
FROM employees;

-- NTH_VALUE
SELECT 
    name,
    salary,
    NTH_VALUE(name, 2) OVER (ORDER BY salary DESC) AS second_highest
FROM employees;
```

---

## 7. Aggregate Window Functions

```sql
-- Running aggregates
SELECT 
    order_date,
    total,
    SUM(total) OVER (ORDER BY order_date) AS running_total,
    AVG(total) OVER (ORDER BY order_date) AS running_avg,
    COUNT(*) OVER (ORDER BY order_date) AS running_count,
    MIN(total) OVER (ORDER BY order_date) AS running_min,
    MAX(total) OVER (ORDER BY order_date) AS running_max
FROM orders;

-- Partition aggregates (no running calculation)
SELECT 
    name,
    department_id,
    salary,
    SUM(salary) OVER (PARTITION BY department_id) AS dept_total,
    AVG(salary) OVER (PARTITION BY department_id) AS dept_avg,
    salary / SUM(salary) OVER (PARTITION BY department_id) * 100 AS pct_of_dept
FROM employees;

-- Difference from average
SELECT 
    name,
    salary,
    salary - AVG(salary) OVER () AS diff_from_avg,
    salary - AVG(salary) OVER (PARTITION BY department_id) AS diff_from_dept_avg
FROM employees;
```

---

## 8. Frame Clauses

### Frame Syntax

```sql
ROWS|RANGE|GROUPS BETWEEN frame_start AND frame_end

-- frame_start/frame_end options:
-- UNBOUNDED PRECEDING  - Start of partition
-- n PRECEDING          - n rows before current
-- CURRENT ROW          - Current row
-- n FOLLOWING          - n rows after current
-- UNBOUNDED FOLLOWING  - End of partition
```

### Examples

```sql
-- Default frame: RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
SELECT 
    date,
    amount,
    SUM(amount) OVER (ORDER BY date) AS running_sum  -- Uses default
FROM transactions;

-- Moving average (3-day)
SELECT 
    date,
    amount,
    AVG(amount) OVER (
        ORDER BY date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_3day
FROM transactions;

-- Centered moving average
SELECT 
    date,
    amount,
    AVG(amount) OVER (
        ORDER BY date 
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ) AS centered_avg
FROM transactions;

-- Sum of entire partition (all rows)
SELECT 
    date,
    amount,
    SUM(amount) OVER () AS total,
    SUM(amount) OVER (
        ORDER BY date 
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS partition_total
FROM transactions;
```

### ROWS vs RANGE vs GROUPS

```sql
-- ROWS: Physical row position
SELECT 
    date,
    amount,
    SUM(amount) OVER (ORDER BY date ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)
FROM sales;
-- If multiple rows have same date, each treated separately

-- RANGE: Logical value range
SELECT 
    date,
    amount,
    SUM(amount) OVER (ORDER BY date RANGE BETWEEN 1 PRECEDING AND CURRENT ROW)
FROM sales;
-- Includes all rows with same date value

-- GROUPS: Peer groups (PostgreSQL 11+)
SELECT 
    score,
    SUM(amount) OVER (ORDER BY score GROUPS BETWEEN 1 PRECEDING AND CURRENT ROW)
FROM results;
-- Includes previous group of peers with same score
```

---

## 9. Named Windows

```sql
-- Define window once, reuse
SELECT 
    name,
    department_id,
    salary,
    SUM(salary) OVER dept_window AS dept_total,
    AVG(salary) OVER dept_window AS dept_avg,
    RANK() OVER dept_window AS dept_rank
FROM employees
WINDOW dept_window AS (PARTITION BY department_id ORDER BY salary DESC);

-- Multiple named windows
SELECT 
    date,
    category,
    amount,
    SUM(amount) OVER by_date AS daily_total,
    SUM(amount) OVER by_category AS category_total
FROM sales
WINDOW 
    by_date AS (PARTITION BY date),
    by_category AS (PARTITION BY category);
```

---

## 10. Common Interview Problems

### Problem 1: Find Employees with Consecutive Growth

```sql
WITH salary_changes AS (
    SELECT 
        employee_id,
        year,
        salary,
        salary - LAG(salary) OVER (PARTITION BY employee_id ORDER BY year) AS change
    FROM salary_history
)
SELECT employee_id
FROM salary_changes
GROUP BY employee_id
HAVING MIN(change) > 0;  -- All changes positive
```

### Problem 2: Find Median

```sql
-- Using PERCENTILE_CONT
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) AS median
FROM employees;

-- Using window functions
SELECT AVG(salary) AS median
FROM (
    SELECT 
        salary,
        ROW_NUMBER() OVER (ORDER BY salary) AS rn,
        COUNT(*) OVER () AS cnt
    FROM employees
) t
WHERE rn IN (FLOOR((cnt + 1) / 2.0), CEIL((cnt + 1) / 2.0));
```

### Problem 3: Running Distinct Count

```sql
-- Count distinct customers over time
SELECT 
    order_date,
    customer_id,
    COUNT(DISTINCT customer_id) OVER (ORDER BY order_date) AS running_distinct
FROM orders;
-- Note: DISTINCT doesn't work in window functions directly

-- Workaround
SELECT DISTINCT ON (order_date)
    order_date,
    (SELECT COUNT(DISTINCT customer_id) 
     FROM orders o2 
     WHERE o2.order_date <= o1.order_date) AS running_distinct
FROM orders o1
ORDER BY order_date;
```

### Problem 4: Find Islands (Consecutive Groups)

```sql
-- Group consecutive dates
WITH numbered AS (
    SELECT 
        event_date,
        event_date - (ROW_NUMBER() OVER (ORDER BY event_date))::int AS grp
    FROM events
)
SELECT 
    MIN(event_date) AS island_start,
    MAX(event_date) AS island_end,
    COUNT(*) AS days
FROM numbered
GROUP BY grp
ORDER BY island_start;
```

### Problem 5: Year-over-Year Comparison

```sql
SELECT 
    year,
    month,
    revenue,
    LAG(revenue, 12) OVER (ORDER BY year, month) AS same_month_prev_year,
    ROUND(
        (revenue - LAG(revenue, 12) OVER (ORDER BY year, month)) / 
        NULLIF(LAG(revenue, 12) OVER (ORDER BY year, month), 0) * 100,
        2
    ) AS yoy_growth
FROM monthly_revenue;
```

---

## 🔬 Hands-On Practice

```sql
-- Setup
CREATE TABLE sales_data (
    id SERIAL PRIMARY KEY,
    salesperson VARCHAR(50),
    region VARCHAR(20),
    sale_date DATE,
    amount NUMERIC(10,2)
);

INSERT INTO sales_data (salesperson, region, sale_date, amount) VALUES
    ('Alice', 'East', '2024-01-15', 1000),
    ('Bob', 'East', '2024-01-15', 1500),
    ('Alice', 'East', '2024-01-16', 800),
    ('Bob', 'East', '2024-01-16', 1200),
    ('Charlie', 'West', '2024-01-15', 2000),
    ('Diana', 'West', '2024-01-15', 1800),
    ('Charlie', 'West', '2024-01-16', 2200),
    ('Diana', 'West', '2024-01-16', 1900);

-- Practice queries
-- 1. Rank salespeople within region
SELECT 
    salesperson,
    region,
    SUM(amount) AS total_sales,
    RANK() OVER (PARTITION BY region ORDER BY SUM(amount) DESC) AS region_rank
FROM sales_data
GROUP BY salesperson, region;

-- 2. Running total by salesperson
SELECT 
    sale_date,
    salesperson,
    amount,
    SUM(amount) OVER (PARTITION BY salesperson ORDER BY sale_date) AS running_total
FROM sales_data;

-- 3. Compare to previous day
SELECT 
    sale_date,
    region,
    SUM(amount) AS daily_total,
    LAG(SUM(amount)) OVER (PARTITION BY region ORDER BY sale_date) AS prev_day,
    SUM(amount) - LAG(SUM(amount)) OVER (PARTITION BY region ORDER BY sale_date) AS change
FROM sales_data
GROUP BY sale_date, region;

-- 4. Moving average
SELECT 
    sale_date,
    amount,
    AVG(amount) OVER (
        ORDER BY sale_date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_3
FROM sales_data;
```

---

## 📝 Key Takeaways

1. **ROW_NUMBER for uniqueness** - Always unique, good for top-N
2. **RANK/DENSE_RANK for ties** - Use RANK when gaps matter
3. **LAG/LEAD for comparisons** - Avoid self-joins
4. **Frame clauses control scope** - Default is RANGE, often want ROWS
5. **Named windows for reuse** - Cleaner, more maintainable
6. **Very common in interviews** - Practice these patterns!

---

## ✅ Day 7 Checklist

- [ ] Use ROW_NUMBER for top-N per group
- [ ] Understand RANK vs DENSE_RANK
- [ ] Practice LAG for period comparisons
- [ ] Write moving average queries
- [ ] Use frame clauses correctly
- [ ] Solve gap-and-island problems
