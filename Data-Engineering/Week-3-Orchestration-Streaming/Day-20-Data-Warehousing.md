# Day 20: Data Warehousing — Snowflake, BigQuery & Redshift

## Learning Objectives
- Understand cloud data warehouse architectures
- Master Snowflake, BigQuery, and Redshift concepts
- Optimize for performance and cost
- Choose the right warehouse for your use case

---

## 1. Snowflake Architecture

### Key Concepts
```
┌─────────────────────────────────────────┐
│          Cloud Services Layer            │  ← Metadata, auth, optimizer
├─────────────────────────────────────────┤
│     Virtual Warehouses (Compute)        │  ← Independent, scalable
├─────────────────────────────────────────┤
│     Centralized Storage (S3/Azure/GCS)  │  ← Micro-partitions, columnar
└─────────────────────────────────────────┘
```

### Snowflake SQL

```sql
-- Create warehouse (compute)
CREATE WAREHOUSE etl_wh
    WAREHOUSE_SIZE = 'LARGE'
    AUTO_SUSPEND = 300          -- Suspend after 5 min idle
    AUTO_RESUME = TRUE
    MIN_CLUSTER_COUNT = 1
    MAX_CLUSTER_COUNT = 4       -- Multi-cluster scaling
    SCALING_POLICY = 'STANDARD';

-- Create database & schema
CREATE DATABASE analytics;
CREATE SCHEMA analytics.marts;

-- Create table with clustering
CREATE TABLE analytics.marts.fct_orders (
    order_id STRING NOT NULL,
    customer_id STRING,
    order_date DATE,
    amount DECIMAL(12,2),
    region STRING
)
CLUSTER BY (order_date, region);  -- Micro-partition pruning

-- Time travel (90 days on Enterprise)
SELECT * FROM fct_orders AT (TIMESTAMP => '2024-01-15 10:00:00');
SELECT * FROM fct_orders AT (OFFSET => -3600);  -- 1 hour ago
SELECT * FROM fct_orders BEFORE (STATEMENT => '<query_id>');

-- Clone (zero-copy, instant)
CREATE TABLE fct_orders_backup CLONE fct_orders;
CREATE DATABASE analytics_dev CLONE analytics;  -- Entire DB clone!

-- Streams (CDC on Snowflake tables)
CREATE STREAM orders_changes ON TABLE raw.orders;
-- Captures INSERT, UPDATE, DELETE changes
SELECT * FROM orders_changes;  -- METADATA$ACTION, METADATA$ISUPDATE, METADATA$ROW_ID

-- Tasks (scheduling)
CREATE TASK transform_orders
    WAREHOUSE = etl_wh
    SCHEDULE = 'USING CRON 0 * * * * UTC'
AS
    MERGE INTO marts.fct_orders t
    USING (SELECT * FROM orders_changes) s
    ON t.order_id = s.order_id
    WHEN MATCHED THEN UPDATE SET ...
    WHEN NOT MATCHED THEN INSERT ...;

ALTER TASK transform_orders RESUME;

-- Dynamic tables (declarative pipelines)
CREATE DYNAMIC TABLE marts.fct_daily_revenue
    TARGET_LAG = '1 hour'
    WAREHOUSE = etl_wh
AS
    SELECT order_date, region, SUM(amount) AS revenue
    FROM marts.fct_orders
    GROUP BY order_date, region;
```

---

## 2. Google BigQuery

### Key Concepts
- **Serverless**: No infrastructure to manage
- **Slots**: Units of compute (auto-scaled or reserved)
- **Storage**: Columnar, auto-compressed, Capacitor format
- **Pricing**: On-demand ($5/TB scanned) or flat-rate (slots)

```sql
-- Create dataset (equivalent to schema)
CREATE SCHEMA `project.analytics`;

-- Create partitioned + clustered table
CREATE TABLE `project.analytics.fct_orders` (
    order_id STRING NOT NULL,
    customer_id STRING,
    order_date DATE,
    amount NUMERIC,
    region STRING
)
PARTITION BY order_date           -- Partition by date (reduces scan)
CLUSTER BY region, customer_id    -- Cluster for filter performance
OPTIONS (
    partition_expiration_days = 365,  -- Auto-delete old partitions
    require_partition_filter = TRUE   -- Force date filter in queries
);

-- Query with partition pruning (only scans needed partitions)
SELECT region, SUM(amount) AS revenue
FROM `project.analytics.fct_orders`
WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31'  -- Required!
GROUP BY region;

-- Materialized views (auto-refreshed)
CREATE MATERIALIZED VIEW `project.analytics.mv_daily_revenue` AS
    SELECT order_date, region, SUM(amount) AS revenue, COUNT(*) AS orders
    FROM `project.analytics.fct_orders`
    GROUP BY order_date, region;

-- BigQuery ML (ML in SQL!)
CREATE MODEL `project.analytics.customer_churn_model`
OPTIONS (
    model_type = 'LOGISTIC_REG',
    input_label_cols = ['churned']
) AS
SELECT * FROM `project.analytics.customer_features`;

-- Predict
SELECT * FROM ML.PREDICT(MODEL `project.analytics.customer_churn_model`,
    (SELECT * FROM `project.analytics.new_customers`));

-- Scheduled queries
CREATE SCHEDULED QUERY daily_aggregation
    SCHEDULE = 'every 24 hours'
    OPTIONS (destination_table = 'analytics.daily_summary')
AS SELECT ...;

-- Streaming inserts
-- Via API: tabledata.insertAll (for real-time, costs more)
-- Via Storage Write API (preferred, exactly-once)
```

---

## 3. Amazon Redshift

### Key Concepts
- **Nodes**: Leader (query planning) + Compute (data processing)
- **Distribution**: How data is spread across nodes
- **Sort Keys**: How data is ordered on disk (for range scans)

```sql
-- Create table with distribution and sort keys
CREATE TABLE analytics.fct_orders (
    order_id VARCHAR(36) NOT NULL ENCODE zstd,
    customer_id VARCHAR(36) ENCODE zstd,
    order_date DATE ENCODE delta,
    amount DECIMAL(12,2) ENCODE az64,
    region VARCHAR(20) ENCODE bytedict
)
DISTKEY(customer_id)          -- Distribute by join key (co-locates data)
SORTKEY(order_date, region)   -- Compound sort key (for range queries)
;

-- Distribution styles:
-- DISTKEY(col): Hash by column (good for frequent joins on that column)
-- DISTSTYLE EVEN: Round-robin (good when no dominant join key)
-- DISTSTYLE ALL: Copy entire table to all nodes (for small dimension tables)
-- DISTSTYLE AUTO: Redshift decides (recommended for new tables)

-- Sort key strategies:
-- COMPOUND: col1, col2, col3 (prefix-based, like compound index)
-- INTERLEAVED: col1, col2 (equal weight, flexible but slower loading)
-- AUTO: Redshift chooses

-- Redshift Spectrum (query S3 directly)
CREATE EXTERNAL SCHEMA spectrum_schema
FROM DATA CATALOG
DATABASE 'datalake'
IAM_ROLE 'arn:aws:iam::123456789:role/RedshiftSpectrumRole'
REGION 'us-east-1';

-- Query S3 data (Parquet)
SELECT * FROM spectrum_schema.raw_events
WHERE event_date = '2024-01-15';

-- COPY command (bulk load from S3)
COPY analytics.fct_orders
FROM 's3://datalake/silver/orders/'
IAM_ROLE 'arn:aws:iam::123456789:role/RedshiftLoadRole'
FORMAT AS PARQUET;

-- UNLOAD (export to S3)
UNLOAD ('SELECT * FROM analytics.fct_orders WHERE order_date >= ''2024-01-01''')
TO 's3://exports/orders/'
IAM_ROLE 'arn:aws:iam::123456789:role/RedshiftUnloadRole'
FORMAT AS PARQUET
PARTITION BY (region);

-- Analyze & Vacuum
ANALYZE analytics.fct_orders;           -- Update statistics
VACUUM FULL analytics.fct_orders;       -- Reclaim space, re-sort
VACUUM DELETE ONLY analytics.fct_orders; -- Just reclaim deleted rows
```

---

## 4. Performance Optimization

### Snowflake

```sql
-- Query profiling
SELECT * FROM TABLE(INFORMATION_SCHEMA.QUERY_HISTORY())
WHERE EXECUTION_STATUS = 'SUCCESS'
ORDER BY TOTAL_ELAPSED_TIME DESC
LIMIT 20;

-- Check clustering effectiveness
SELECT SYSTEM$CLUSTERING_INFORMATION('fct_orders', '(order_date, region)');

-- Result caching (24 hours, free)
-- Same query + same data = instant result from cache
ALTER SESSION SET USE_CACHED_RESULT = TRUE;

-- Optimization tips:
-- 1. Choose right warehouse size (bigger = more parallelism)
-- 2. Cluster on filter/join columns
-- 3. Use COPY for bulk loads (not INSERT)
-- 4. Avoid SELECT * (column pruning)
-- 5. Use LIMIT for exploration
```

### BigQuery

```sql
-- Estimate query cost before running
SELECT total_bytes_processed
FROM `region-us`.INFORMATION_SCHEMA.JOBS
WHERE job_id = 'current_job';

-- Or use dry run:
-- bq query --dry_run "SELECT ..."

-- Optimization tips:
-- 1. Always filter on partition column (required if set)
-- 2. Cluster on filter columns (up to 4)
-- 3. Avoid SELECT * (columnar = only read needed columns)
-- 4. Use approximate functions (APPROX_COUNT_DISTINCT)
-- 5. Materialize repeated subqueries (WITH clause or materialized views)
-- 6. Use BI Engine for dashboard acceleration
```

---

## 5. Cost Optimization

### Snowflake Costs
```
Storage: $23-40/TB/month (compressed)
Compute: $2-4/credit (1 credit = 1 XS warehouse/hour)
  XS = 1 credit/hr, S = 2, M = 4, L = 8, XL = 16

Optimization:
- Auto-suspend (300s default)
- Right-size warehouses (monitor queue time)
- Separate warehouses for ETL vs queries
- Use Resource Monitors for budget caps
- Avoid unnecessary clustering maintenance
```

### BigQuery Costs
```
On-demand: $5/TB scanned (first 1TB free/month)
Flat-rate: $1,700/month per 100 slots
Storage: $0.02/GB/month (active), $0.01/GB (long-term >90 days)

Optimization:
- Partition + cluster (reduces bytes scanned)
- Require partition filters
- Use cached results (free)
- Avoid SELECT * 
- Use flat-rate for predictable high-volume
- Archive old partitions (auto long-term pricing)
```

---

## 6. Comparison Matrix

| Feature | Snowflake | BigQuery | Redshift |
|---------|-----------|----------|----------|
| **Architecture** | Shared disk | Serverless | Shared nothing |
| **Scaling** | Instant (virtual WH) | Auto (slots) | Resize (minutes) |
| **Pricing** | Compute + Storage | Per-TB or Flat | Per-node |
| **Semi-structured** | VARIANT (native) | STRUCT/ARRAY | Super type |
| **ML Integration** | Snowpark ML | BigQuery ML (best) | Redshift ML |
| **Streaming** | Snowpipe | Storage Write API | Kinesis Firehose |
| **Data Sharing** | Best (secure shares) | Analytics Hub | Datashare |
| **Multi-cloud** | ✅ (AWS, Azure, GCP) | GCP only | AWS only |
| **Best for** | Multi-cloud, sharing | GCP ecosystem, ML | AWS ecosystem |

---

## Interview Questions

### Beginner
1. **What's the difference between OLTP and OLAP?** OLTP: transactional (fast writes, row-oriented, normalized). OLAP: analytical (fast reads, columnar, denormalized). Warehouses are OLAP.
2. **Why are columnar databases fast for analytics?** Only read needed columns (vs all columns in row stores). Better compression (similar data together). Vectorized processing.
3. **What is partitioning in a data warehouse?** Dividing table into segments by a column (usually date). Queries filtering on partition column skip irrelevant segments.

### Intermediate
4. **Explain Snowflake's separation of storage and compute.** Storage on cloud object store (cheap, unlimited). Compute via virtual warehouses (spin up/down independently). Multiple warehouses query same data without contention.
5. **How do you choose between on-demand and flat-rate pricing in BigQuery?** On-demand: variable workload, < 100TB/month scanned. Flat-rate: predictable high volume, need guaranteed capacity. Crossover typically at ~$5K-10K/month.
6. **What are distribution keys in Redshift?** Determines which node holds each row. Choose join-key columns so joined tables are co-located (no network shuffle). Use DISTSTYLE ALL for small dimensions.

### Advanced
7. **Design a multi-tenant data warehouse for a SaaS product.** Row-level security per tenant, separate schemas or filter-based isolation, resource isolation (Snowflake: reader accounts or separate warehouses per tier), data sharing for partners, encryption per tenant.
8. **How do you migrate from Redshift to Snowflake?** Export via UNLOAD to S3 (Parquet), Snowpipe/COPY into Snowflake, recreate DDL (handle type differences), migrate stored procedures (JavaScript in Snowflake), re-point BI tools, parallel run validation.
9. **Explain Zero-Copy Cloning and its use cases.** Snowflake creates metadata-only copy (instant, no storage cost until changes). Use cases: dev environments from prod, testing migrations, creating restore points, ad-hoc analysis without affecting production.

---

## Hands-On Exercise
1. Set up free-tier Snowflake, BigQuery, and Redshift accounts
2. Create fact and dimension tables with appropriate keys/partitioning
3. Load sample data (1M+ rows) and benchmark queries
4. Compare query performance with and without clustering/partitioning
5. Implement time travel and cloning (Snowflake)
6. Cost analysis: estimate monthly cost for 10TB data, 100 queries/day
