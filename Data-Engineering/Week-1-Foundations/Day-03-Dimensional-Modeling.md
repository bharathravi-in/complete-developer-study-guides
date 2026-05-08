# Day 3: Data Modeling — Dimensional (Kimball)

## Overview
Dimensional modeling is the foundation of analytics data warehousing. Learn to design star schemas that are intuitive to query and performant at scale.

---

## 1. Why Dimensional Modeling?

### OLTP vs OLAP
| Aspect | OLTP (Transactional) | OLAP (Analytical) |
|--------|---------------------|-------------------|
| Purpose | Run the business | Analyze the business |
| Queries | Simple, row-level | Complex, aggregations |
| Schema | Highly normalized (3NF) | Denormalized (star/snowflake) |
| Users | Applications | Analysts, Data Scientists |
| Optimize for | Write speed | Read speed |

### Kimball's 4-Step Process
1. **Select the business process** (e.g., orders, page views)
2. **Declare the grain** (what does one row represent?)
3. **Identify the dimensions** (who, what, where, when, how)
4. **Identify the facts** (measurable numeric values)

---

## 2. Star Schema

```
        ┌──────────────┐
        │  dim_date    │
        └──────┬───────┘
               │
┌──────────┐   │   ┌──────────────┐
│dim_product├───┼───┤ fact_sales   │
└──────────┘   │   └───┬──────────┘
               │       │
        ┌──────┴───┐   │   ┌──────────┐
        │dim_store │   └───┤dim_customer│
        └──────────┘       └──────────┘
```

### Fact Tables
- Contain **measurements/metrics** (revenue, quantity, duration)
- Have **foreign keys** to dimension tables
- Usually the largest tables (billions of rows)
- Grain is critical: "one row per order line item"

```sql
CREATE TABLE fact_sales (
    sale_key BIGINT PRIMARY KEY,
    -- Foreign keys (dimensions)
    date_key INT REFERENCES dim_date(date_key),
    product_key INT REFERENCES dim_product(product_key),
    customer_key INT REFERENCES dim_customer(customer_key),
    store_key INT REFERENCES dim_store(store_key),
    -- Degenerate dimension (no separate table needed)
    order_number TEXT,
    -- Facts (measures)
    quantity INT,
    unit_price DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    net_revenue DECIMAL(10,2),
    cost DECIMAL(10,2),
    profit DECIMAL(10,2)
);
```

### Types of Facts
| Type | Description | Example |
|------|-------------|---------|
| Additive | Can SUM across all dimensions | Revenue, quantity |
| Semi-additive | Can SUM across some dimensions | Account balance (not across time) |
| Non-additive | Cannot SUM at all | Ratios, percentages |

### Dimension Tables
- Contain **descriptive attributes** (name, category, address)
- Usually wide (many columns) but short (thousands to millions of rows)
- Support filtering and grouping

```sql
CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,       -- Surrogate key
    product_id TEXT NOT NULL,              -- Natural/business key
    product_name TEXT,
    category TEXT,
    subcategory TEXT,
    brand TEXT,
    supplier TEXT,
    unit_cost DECIMAL(10,2),
    is_active BOOLEAN,
    -- SCD Type 2 tracking
    valid_from DATE,
    valid_to DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE
);

CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,             -- YYYYMMDD format
    full_date DATE NOT NULL,
    year INT,
    quarter INT,
    month INT,
    month_name TEXT,
    week_of_year INT,
    day_of_week INT,
    day_name TEXT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    fiscal_year INT,
    fiscal_quarter INT
);
```

---

## 3. Snowflake Schema

Star schema but with normalized dimensions (dimension tables have their own sub-dimensions).

```
dim_product → dim_category → dim_department
```

```sql
-- Snowflaked: category is separate
CREATE TABLE dim_category (
    category_key SERIAL PRIMARY KEY,
    category_name TEXT,
    department TEXT
);

CREATE TABLE dim_product (
    product_key SERIAL PRIMARY KEY,
    product_name TEXT,
    category_key INT REFERENCES dim_category(category_key),
    brand TEXT
);
```

### Star vs Snowflake
| Aspect | Star | Snowflake |
|--------|------|-----------|
| Query complexity | Simpler (fewer joins) | More joins |
| Storage | More redundancy | Less redundancy |
| Query performance | Generally faster | More joins = slower |
| ETL complexity | Simpler loads | More complex |
| **Recommendation** | **Preferred for analytics** | Use sparingly |

---

## 4. Slowly Changing Dimensions (SCDs)

How to handle dimension attributes that change over time.

### SCD Type 0 — Retain Original
Never update. Keep the value as it was when first loaded.

### SCD Type 1 — Overwrite
```sql
-- Simply update the row (lose history)
UPDATE dim_customer 
SET tier = 'gold', email = 'new@email.com'
WHERE customer_id = 'C123';
```

### SCD Type 2 — Add New Row (Most Common in DE)
```sql
-- Close current record
UPDATE dim_customer 
SET valid_to = CURRENT_DATE - 1, is_current = FALSE
WHERE customer_id = 'C123' AND is_current = TRUE;

-- Insert new version
INSERT INTO dim_customer 
    (customer_id, name, tier, valid_from, valid_to, is_current)
VALUES 
    ('C123', 'John Doe', 'gold', CURRENT_DATE, '9999-12-31', TRUE);
```

### SCD Type 3 — Add Column
```sql
-- Track only previous + current
ALTER TABLE dim_customer ADD COLUMN previous_tier TEXT;

UPDATE dim_customer 
SET previous_tier = tier, tier = 'gold'
WHERE customer_id = 'C123';
```

### SCD Type 6 (Hybrid: 1+2+3)
Combines Type 2 rows with Type 3 current-value columns.

---

## 5. Fact Table Types

### Transaction Facts
- One row per event/transaction
- Most common, finest grain
- Example: `fact_orders` (one row per order line)

### Periodic Snapshot Facts
- One row per entity per time period
- Example: `fact_account_daily` (account balance each day)

```sql
CREATE TABLE fact_inventory_daily (
    date_key INT,
    product_key INT,
    store_key INT,
    quantity_on_hand INT,      -- Semi-additive
    quantity_sold INT,         -- Additive
    days_of_supply DECIMAL    -- Non-additive
);
```

### Accumulating Snapshot Facts
- One row per entity lifetime (updated as milestones occur)
- Example: Order lifecycle tracking

```sql
CREATE TABLE fact_order_lifecycle (
    order_key INT PRIMARY KEY,
    customer_key INT,
    order_date_key INT,
    ship_date_key INT,         -- Updated when shipped
    delivery_date_key INT,     -- Updated when delivered
    return_date_key INT,       -- Updated if returned
    order_amount DECIMAL,
    shipping_cost DECIMAL,
    days_to_ship INT,
    days_to_deliver INT
);
```

### Factless Fact Tables
- No numeric measures, only keys
- Record events/coverage

```sql
-- Student attendance (the fact IS the attendance)
CREATE TABLE fact_attendance (
    date_key INT,
    student_key INT,
    class_key INT,
    PRIMARY KEY (date_key, student_key, class_key)
);
```

---

## 6. Advanced Patterns

### Junk Dimensions
Combine low-cardinality flags into one dimension to avoid cluttering the fact table.

```sql
-- Instead of 5 boolean columns in fact table:
CREATE TABLE dim_order_flags (
    flag_key SERIAL PRIMARY KEY,
    is_online BOOLEAN,
    is_gift BOOLEAN,
    is_first_order BOOLEAN,
    payment_type TEXT,      -- 'credit', 'debit', 'cash'
    delivery_type TEXT      -- 'standard', 'express', 'same_day'
);
-- Only ~50-100 unique combinations
```

### Role-Playing Dimensions
Same dimension used multiple times in a fact table.

```sql
-- dim_date used for order_date, ship_date, delivery_date
SELECT 
    f.*,
    od.full_date AS order_date,
    sd.full_date AS ship_date,
    dd.full_date AS delivery_date
FROM fact_orders f
JOIN dim_date od ON f.order_date_key = od.date_key
JOIN dim_date sd ON f.ship_date_key = sd.date_key
JOIN dim_date dd ON f.delivery_date_key = dd.date_key;
```

### Conformed Dimensions
Shared dimensions used across multiple fact tables (enables cross-process analysis).

```sql
-- dim_customer used by fact_sales, fact_support_tickets, fact_web_sessions
-- Same customer_key everywhere = join across business processes
```

---

## 7. Design Exercise

Design a star schema for an **e-commerce platform**:

**Business process**: Order fulfillment  
**Grain**: One row per order line item  

**Dimensions to consider**:
- Customer (name, segment, geography, registration date)
- Product (name, category, brand, supplier)
- Date (order date, ship date)
- Store/Channel (online, mobile, in-store)
- Promotion (discount type, campaign)

**Facts to measure**:
- Quantity, unit price, discount, net revenue
- Shipping cost, tax amount
- Days to fulfill

---

## Key Takeaways
- Always declare the **grain** first — everything flows from it
- Star schema > snowflake for analytical workloads
- SCD Type 2 preserves history (critical for accurate reporting)
- Use surrogate keys (not natural keys) in dimensions
- Conformed dimensions enable enterprise-wide analytics

## Tomorrow
**Day 4**: Data Vault & Third Normal Form — alternative modeling approaches for flexibility and auditability.
