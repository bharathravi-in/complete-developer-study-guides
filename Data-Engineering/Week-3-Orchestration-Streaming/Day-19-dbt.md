# Day 19: dbt (Data Build Tool)

## Learning Objectives
- Master dbt project structure and workflows
- Implement materializations (view, table, incremental, ephemeral)
- Write tests, documentation, and macros
- Build a complete dbt transformation layer

---

## 1. dbt Fundamentals

### Project Structure

```
dbt_project/
├── dbt_project.yml          # Project configuration
├── profiles.yml             # Connection configuration (not in git)
├── models/
│   ├── staging/             # 1:1 with source tables (rename, type cast)
│   │   ├── _staging.yml     # Schema + tests
│   │   ├── stg_orders.sql
│   │   └── stg_customers.sql
│   ├── intermediate/        # Business logic joins
│   │   └── int_orders_enriched.sql
│   └── marts/               # Final business entities
│       ├── _marts.yml
│       ├── fct_orders.sql   # Fact tables
│       └── dim_customers.sql # Dimension tables
├── tests/                   # Custom data tests
├── macros/                  # Reusable SQL/Jinja
├── seeds/                   # CSV lookup tables
├── snapshots/               # SCD Type 2
└── analyses/                # Ad-hoc queries (not materialized)
```

### dbt_project.yml

```yaml
name: 'analytics'
version: '1.0.0'
config-version: 2

profile: 'warehouse'

model-paths: ["models"]
test-paths: ["tests"]
macro-paths: ["macros"]
seed-paths: ["seeds"]
snapshot-paths: ["snapshots"]

models:
  analytics:
    staging:
      +materialized: view
      +schema: staging
    intermediate:
      +materialized: ephemeral
    marts:
      +materialized: table
      +schema: analytics
```

---

## 2. Models

### Staging Models (Source Abstraction)

```sql
-- models/staging/stg_orders.sql
WITH source AS (
    SELECT * FROM {{ source('raw', 'orders') }}
),

renamed AS (
    SELECT
        order_id,
        customer_id,
        product_id,
        CAST(quantity AS INTEGER) AS quantity,
        CAST(unit_price AS NUMERIC(10,2)) AS unit_price,
        CAST(order_date AS DATE) AS order_date,
        UPPER(TRIM(status)) AS status,
        UPPER(TRIM(region)) AS region,
        _loaded_at AS ingested_at
    FROM source
    WHERE order_id IS NOT NULL  -- Remove invalid records
)

SELECT * FROM renamed
```

### Intermediate Models

```sql
-- models/intermediate/int_orders_enriched.sql
WITH orders AS (
    SELECT * FROM {{ ref('stg_orders') }}
),

customers AS (
    SELECT * FROM {{ ref('stg_customers') }}
),

products AS (
    SELECT * FROM {{ ref('stg_products') }}
)

SELECT
    o.order_id,
    o.customer_id,
    c.customer_name,
    c.customer_segment,
    o.product_id,
    p.product_name,
    p.category,
    o.quantity,
    o.unit_price,
    o.quantity * o.unit_price AS total_amount,
    o.order_date,
    o.status,
    o.region
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
LEFT JOIN products p ON o.product_id = p.product_id
```

### Mart Models (Business Layer)

```sql
-- models/marts/fct_orders.sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge',
        partition_by={'field': 'order_date', 'data_type': 'date', 'granularity': 'month'},
    )
}}

WITH enriched_orders AS (
    SELECT * FROM {{ ref('int_orders_enriched') }}
    {% if is_incremental() %}
    WHERE order_date > (SELECT MAX(order_date) FROM {{ this }})
    {% endif %}
)

SELECT
    order_id,
    customer_id,
    customer_name,
    product_id,
    product_name,
    category,
    quantity,
    unit_price,
    total_amount,
    order_date,
    status,
    region,
    CURRENT_TIMESTAMP AS _dbt_updated_at
FROM enriched_orders
```

---

## 3. Materializations

```sql
-- VIEW: Virtual table, always fresh, no storage cost
-- Use for: staging models, simple transforms
{{ config(materialized='view') }}

-- TABLE: Physical table, rebuilt on every run
-- Use for: small-medium tables, full refresh needed
{{ config(materialized='table') }}

-- INCREMENTAL: Only process new/changed rows
-- Use for: large tables, append-heavy data, fact tables
{{ config(materialized='incremental', unique_key='id') }}
SELECT * FROM {{ ref('stg_events') }}
{% if is_incremental() %}
WHERE event_time > (SELECT MAX(event_time) FROM {{ this }})
{% endif %}

-- EPHEMERAL: Not materialized, inlined as CTE
-- Use for: intermediate logic, avoid creating database objects
{{ config(materialized='ephemeral') }}
```

### Incremental Strategies

```sql
-- MERGE (default for most warehouses): Upsert based on unique_key
{{ config(
    materialized='incremental',
    unique_key='event_id',
    incremental_strategy='merge'
) }}

-- APPEND: Just insert new rows (fastest, no dedup)
{{ config(
    materialized='incremental',
    incremental_strategy='append'
) }}

-- DELETE+INSERT: Delete matching records, insert new (Redshift)
{{ config(
    materialized='incremental',
    unique_key='event_id',
    incremental_strategy='delete+insert'
) }}

-- INSERT_OVERWRITE: Replace entire partitions (BigQuery, Spark)
{{ config(
    materialized='incremental',
    incremental_strategy='insert_overwrite',
    partition_by={'field': 'event_date', 'data_type': 'date'}
) }}
```

---

## 4. Testing

### Schema Tests (YAML)

```yaml
# models/marts/_marts.yml
version: 2

models:
  - name: fct_orders
    description: "Order fact table with enriched customer and product data"
    columns:
      - name: order_id
        description: "Primary key"
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
      - name: total_amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000000
      - name: status
        tests:
          - accepted_values:
              values: ['PENDING', 'COMPLETED', 'CANCELLED', 'REFUNDED']
      - name: order_date
        tests:
          - not_null
          - dbt_utils.not_null_proportion:
              at_least: 0.99
```

### Custom Tests

```sql
-- tests/assert_no_orphan_orders.sql
-- Custom test: all orders have valid customers
SELECT
    o.order_id,
    o.customer_id
FROM {{ ref('fct_orders') }} o
LEFT JOIN {{ ref('dim_customers') }} c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL
-- If this returns any rows, the test FAILS

-- tests/assert_revenue_not_negative.sql
SELECT
    order_date,
    SUM(total_amount) AS daily_revenue
FROM {{ ref('fct_orders') }}
GROUP BY order_date
HAVING SUM(total_amount) < 0
```

### Generic Tests (Reusable)

```sql
-- tests/generic/test_is_positive.sql
{% test is_positive(model, column_name) %}
    SELECT *
    FROM {{ model }}
    WHERE {{ column_name }} < 0
{% endtest %}
```

```yaml
# Usage in YAML
columns:
  - name: quantity
    tests:
      - is_positive
```

---

## 5. Macros & Jinja

```sql
-- macros/generate_surrogate_key.sql
{% macro generate_surrogate_key(field_list) %}
    {{ dbt_utils.generate_surrogate_key(field_list) }}
{% endmacro %}

-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name, precision=2) %}
    ROUND(CAST({{ column_name }} AS NUMERIC) / 100, {{ precision }})
{% endmacro %}

-- macros/date_spine.sql
{% macro get_date_range(start_date, end_date) %}
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="'" ~ start_date ~ "'",
        end_date="'" ~ end_date ~ "'"
    ) }}
{% endmacro %}

-- macros/incremental_filter.sql
{% macro incremental_filter(timestamp_col, lookback_hours=6) %}
    {% if is_incremental() %}
        WHERE {{ timestamp_col }} > (
            SELECT DATEADD(hour, -{{ lookback_hours }}, MAX({{ timestamp_col }}))
            FROM {{ this }}
        )
    {% endif %}
{% endmacro %}
```

### Using Macros in Models

```sql
-- models/marts/fct_orders.sql
SELECT
    {{ generate_surrogate_key(['order_id', 'order_date']) }} AS order_sk,
    order_id,
    {{ cents_to_dollars('amount_cents') }} AS amount_dollars,
    order_date
FROM {{ ref('stg_orders') }}
{{ incremental_filter('order_date') }}
```

---

## 6. Sources & Documentation

### Sources

```yaml
# models/staging/_sources.yml
version: 2

sources:
  - name: raw
    database: production
    schema: public
    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}
    loaded_at_field: _loaded_at
    tables:
      - name: orders
        description: "Raw orders from OLTP system"
        columns:
          - name: order_id
            tests:
              - not_null
      - name: customers
      - name: products
```

### Documentation

```yaml
# models/marts/_marts.yml
models:
  - name: fct_orders
    description: >
      **Order fact table** containing all completed and pending orders.
      
      Grain: one row per order.
      
      Sources: stg_orders, stg_customers, stg_products
      
      Update frequency: Incremental, runs hourly.
      
      Business rules:
      - total_amount = quantity × unit_price
      - Only includes orders from 2023 onwards
      - Cancelled orders included for analytics
```

```sql
-- models/marts/fct_orders.sql
-- Add inline documentation
{% docs order_status %}
Order status values:
- **PENDING**: Order placed, not yet fulfilled
- **COMPLETED**: Order shipped and delivered
- **CANCELLED**: Order cancelled by customer
- **REFUNDED**: Order refunded after completion
{% enddocs %}
```

---

## 7. Snapshots (SCD Type 2)

```sql
-- snapshots/snap_customers.sql
{% snapshot snap_customers %}
{{
    config(
        target_schema='snapshots',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at',
        invalidate_hard_deletes=True,
    )
}}

SELECT
    customer_id,
    name,
    email,
    segment,
    address,
    updated_at
FROM {{ source('raw', 'customers') }}

{% endsnapshot %}
```

```bash
# Run snapshots
dbt snapshot

# Result: snapshots.snap_customers with columns:
# customer_id, name, email, ..., dbt_valid_from, dbt_valid_to, dbt_scd_id
```

---

## 8. dbt Commands & Workflow

```bash
# Install dependencies
dbt deps

# Run all models
dbt run

# Run specific model and its dependencies
dbt run --select fct_orders+  # fct_orders and all downstream

# Run with full refresh (rebuild incremental from scratch)
dbt run --full-refresh --select fct_orders

# Test
dbt test                      # Run all tests
dbt test --select fct_orders  # Tests for specific model

# Generate and serve documentation
dbt docs generate
dbt docs serve

# Check source freshness
dbt source freshness

# Compile SQL (see rendered Jinja)
dbt compile --select fct_orders

# Debug connection
dbt debug

# Run models changed since last git commit
dbt run --select state:modified+ --state ./target
```

---

## Interview Questions

### Beginner
1. **What is dbt and why use it?** dbt is a SQL-first transformation tool. Manages dependencies (ref), tests data quality, documents models, handles materializations. It's the "T" in ELT.
2. **What's the difference between `ref` and `source`?** `ref('model_name')` references another dbt model (creates dependency). `source('name', 'table')` references raw tables (enables freshness checks).
3. **What are the four materializations?** View (virtual), Table (physical, full rebuild), Incremental (only new rows), Ephemeral (inlined CTE, not stored).

### Intermediate
4. **How do incremental models work?** On first run: full table build. On subsequent runs: only process rows matching the `is_incremental()` filter (usually timestamp > max existing). Uses unique_key for MERGE/dedup.
5. **How do you handle late-arriving data in dbt?** Lookback window: instead of `> MAX(timestamp)`, use `> MAX(timestamp) - interval '6 hours'`. Combined with merge strategy and unique_key for dedup.
6. **Explain the staging → intermediate → marts pattern.** Staging: 1:1 source mapping (rename, cast, clean). Intermediate: business logic, joins (ephemeral). Marts: final output (facts, dimensions). Separates concerns, improves testability.

### Advanced
7. **How do you implement data contracts with dbt?** Schema YAML with column-level tests (not_null, unique, accepted_values, relationships). Enforce with `dbt test` in CI/CD. Contract-breaking changes fail the build. Use `dbt_project_evaluator` for governance.
8. **Design a dbt project for a 100-model analytics platform.** Folder by domain (marketing/, finance/, product/), shared staging layer, intermediate for cross-domain joins, YAML per folder, custom macros for patterns, CI/CD with slim runs (`state:modified+`), exposure definitions for dashboards.
9. **How do you optimize dbt for large datasets?** Incremental with merge strategy, partition_by for pruning, cluster_by for co-location, reduce model dependencies to enable parallelism, use ephemeral for shared CTEs, Snowflake warehouse sizing per model.

---

## Hands-On Exercise
1. Initialize dbt project with warehouse connection
2. Create staging models for 3 source tables
3. Build intermediate model joining staging models
4. Create incremental fact table with merge strategy
5. Add comprehensive tests (unique, not_null, relationships, custom)
6. Write macros for repeated patterns
7. Generate documentation and review lineage graph
8. Implement SCD Type 2 with snapshots
