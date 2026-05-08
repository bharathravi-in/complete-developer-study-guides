# Day 2: Advanced SQL for Data Engineers

## Overview
SQL is the lingua franca of data engineering. Master these patterns and you'll handle 80% of transformation work.

---

## 1. Window Functions

Window functions operate on a set of rows related to the current row WITHOUT collapsing them (unlike GROUP BY).

### Syntax
```sql
function_name() OVER (
    [PARTITION BY column(s)]
    [ORDER BY column(s)]
    [ROWS/RANGE frame_spec]
)
```

### ROW_NUMBER, RANK, DENSE_RANK
```sql
-- Deduplicate: Keep latest record per user
WITH ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY user_id 
            ORDER BY updated_at DESC
        ) AS rn
    FROM raw_users
)
SELECT * FROM ranked WHERE rn = 1;

-- Rank products by revenue within category
SELECT 
    category,
    product_name,
    revenue,
    RANK() OVER (PARTITION BY category ORDER BY revenue DESC) as rank,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY revenue DESC) as dense_rank
FROM products;
```

### LAG / LEAD — Access Previous/Next Rows
```sql
-- Calculate day-over-day change
SELECT 
    event_date,
    daily_revenue,
    LAG(daily_revenue) OVER (ORDER BY event_date) AS prev_day_revenue,
    daily_revenue - LAG(daily_revenue) OVER (ORDER BY event_date) AS day_over_day_change,
    ROUND(
        (daily_revenue - LAG(daily_revenue) OVER (ORDER BY event_date)) 
        / LAG(daily_revenue) OVER (ORDER BY event_date) * 100, 2
    ) AS pct_change
FROM daily_metrics;
```

### Running Totals & Moving Averages
```sql
-- Running total
SELECT 
    order_date,
    amount,
    SUM(amount) OVER (ORDER BY order_date) AS running_total,
    -- 7-day moving average
    AVG(amount) OVER (
        ORDER BY order_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d
FROM orders;
```

### NTILE — Bucketing
```sql
-- Divide customers into quartiles by spend
SELECT 
    customer_id,
    total_spend,
    NTILE(4) OVER (ORDER BY total_spend) AS spend_quartile
FROM customer_metrics;
```

---

## 2. Common Table Expressions (CTEs)

### Basic CTEs
```sql
-- Readable, composable queries
WITH 
active_users AS (
    SELECT user_id, MAX(event_date) AS last_active
    FROM events
    WHERE event_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
),
user_orders AS (
    SELECT user_id, COUNT(*) AS order_count, SUM(amount) AS total_spent
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY user_id
)
SELECT 
    au.user_id,
    au.last_active,
    COALESCE(uo.order_count, 0) AS orders_30d,
    COALESCE(uo.total_spent, 0) AS spend_30d
FROM active_users au
LEFT JOIN user_orders uo ON au.user_id = uo.user_id;
```

### Recursive CTEs — Hierarchies & Sequences
```sql
-- Generate date series (useful for filling gaps)
WITH RECURSIVE date_series AS (
    SELECT DATE '2024-01-01' AS dt
    UNION ALL
    SELECT dt + INTERVAL '1 day'
    FROM date_series
    WHERE dt < DATE '2024-12-31'
)
SELECT dt FROM date_series;

-- Organizational hierarchy
WITH RECURSIVE org_tree AS (
    -- Base: top-level managers
    SELECT id, name, manager_id, 1 AS level, ARRAY[name] AS path
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive: each employee under their manager
    SELECT e.id, e.name, e.manager_id, ot.level + 1, ot.path || e.name
    FROM employees e
    JOIN org_tree ot ON e.manager_id = ot.id
)
SELECT * FROM org_tree ORDER BY path;
```

---

## 3. LATERAL Joins

LATERAL allows a subquery to reference columns from preceding tables (like a correlated subquery, but in FROM).

```sql
-- Top 3 orders per customer (more efficient than window + filter)
SELECT c.customer_id, c.name, top_orders.*
FROM customers c
CROSS JOIN LATERAL (
    SELECT order_id, amount, order_date
    FROM orders o
    WHERE o.customer_id = c.customer_id
    ORDER BY amount DESC
    LIMIT 3
) AS top_orders;

-- Unnest JSON arrays with context
SELECT 
    e.event_id,
    e.user_id,
    item.*
FROM events e
CROSS JOIN LATERAL jsonb_array_elements(e.payload->'items') AS item;
```

---

## 4. Advanced Aggregation

### GROUPING SETS, CUBE, ROLLUP
```sql
-- Multiple grouping levels in one query
SELECT 
    COALESCE(region, 'ALL') AS region,
    COALESCE(product_category, 'ALL') AS category,
    SUM(revenue) AS total_revenue,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM sales
GROUP BY GROUPING SETS (
    (region, product_category),  -- By region and category
    (region),                     -- By region only
    (product_category),           -- By category only
    ()                            -- Grand total
);

-- ROLLUP: hierarchical subtotals
SELECT year, quarter, month, SUM(revenue)
FROM sales
GROUP BY ROLLUP (year, quarter, month);
-- Produces: (year, quarter, month), (year, quarter), (year), ()
```

### FILTER Clause
```sql
-- Conditional aggregation (cleaner than CASE WHEN)
SELECT 
    DATE_TRUNC('month', order_date) AS month,
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_orders,
    SUM(amount) FILTER (WHERE status = 'completed') AS completed_revenue,
    COUNT(*) FILTER (WHERE status = 'refunded') AS refunded_orders
FROM orders
GROUP BY 1;
```

---

## 5. Query Optimization for DE

### EXPLAIN ANALYZE Reading
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM large_table WHERE indexed_col = 'value';

-- Key metrics to look for:
-- Planning Time: < 1ms is ideal
-- Execution Time: your actual runtime
-- Rows: estimated vs actual (big gaps = stale stats)
-- Buffers: shared hit (cache) vs read (disk)
```

### Index Strategy
```sql
-- Composite index: column order matters!
-- Put equality conditions first, range conditions last
CREATE INDEX idx_orders_lookup 
ON orders (status, customer_id, order_date DESC);

-- Partial index: only index relevant rows
CREATE INDEX idx_active_orders 
ON orders (customer_id, order_date) 
WHERE status = 'active';

-- Covering index: avoid table lookups
CREATE INDEX idx_orders_covering 
ON orders (customer_id) 
INCLUDE (amount, order_date);
```

### Partitioning for Large Tables
```sql
-- Range partition by date (most common for DE)
CREATE TABLE events (
    id BIGINT,
    event_type TEXT,
    payload JSONB,
    created_at TIMESTAMPTZ
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE events_2024_01 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE events_2024_02 PARTITION OF events
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Queries with date filter only scan relevant partitions
SELECT * FROM events 
WHERE created_at >= '2024-03-01' AND created_at < '2024-04-01';
```

---

## 6. DE-Specific SQL Patterns

### Slowly Changing Dimensions (SCD Type 2)
```sql
-- Track historical changes
CREATE TABLE dim_customer (
    surrogate_key SERIAL PRIMARY KEY,
    customer_id TEXT NOT NULL,
    name TEXT,
    email TEXT,
    tier TEXT,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_to TIMESTAMPTZ DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE
);

-- Close old record, insert new
UPDATE dim_customer 
SET valid_to = NOW(), is_current = FALSE
WHERE customer_id = 'C123' AND is_current = TRUE;

INSERT INTO dim_customer (customer_id, name, email, tier, valid_from)
VALUES ('C123', 'John', 'john@new.com', 'gold', NOW());
```

### Gap-and-Island Detection
```sql
-- Find consecutive login streaks
WITH numbered AS (
    SELECT 
        user_id,
        login_date,
        login_date - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date))::int AS grp
    FROM logins
)
SELECT 
    user_id,
    MIN(login_date) AS streak_start,
    MAX(login_date) AS streak_end,
    COUNT(*) AS streak_length
FROM numbered
GROUP BY user_id, grp
HAVING COUNT(*) >= 3;  -- Streaks of 3+ days
```

### Sessionization
```sql
-- Group events into sessions (30-min inactivity = new session)
WITH event_gaps AS (
    SELECT *,
        EXTRACT(EPOCH FROM 
            event_time - LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time)
        ) AS gap_seconds
    FROM events
),
session_starts AS (
    SELECT *,
        CASE WHEN gap_seconds > 1800 OR gap_seconds IS NULL THEN 1 ELSE 0 END AS is_new_session
    FROM event_gaps
)
SELECT *,
    SUM(is_new_session) OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
FROM session_starts;
```

---

## 7. Practice Problems

1. **Deduplication**: Given a table with duplicate records, write a query to keep only the latest version of each record.
2. **Funnel Analysis**: Calculate conversion rates through a 4-step funnel (view → cart → checkout → purchase).
3. **Retention Cohorts**: Build a monthly retention matrix showing % of users returning in month N after signup.
4. **Running Percentiles**: Calculate the running median of order amounts by day.
5. **JSON Flattening**: Unnest a nested JSON column into a flat table structure.

---

## Key Takeaways
- Window functions are your primary tool for analytics transformations
- CTEs make complex queries readable and maintainable
- LATERAL joins solve "top-N per group" elegantly
- Always check EXPLAIN ANALYZE before running on large tables
- Master SCD, sessionization, and gap-and-island patterns

## Tomorrow
**Day 3**: Dimensional Data Modeling — Star schema, snowflake schema, and Kimball methodology for building analytics-ready data warehouses.
