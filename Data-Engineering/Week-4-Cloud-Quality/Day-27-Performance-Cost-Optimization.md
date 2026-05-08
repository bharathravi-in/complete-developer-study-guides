# Day 27: Performance & Cost Optimization

## Learning Objectives
- Optimize file formats, compression, and storage layout
- Master partition pruning and predicate pushdown
- Implement cost monitoring and budgeting
- Right-size compute resources

---

## 1. File Format Optimization

### Format Comparison

| Format | Type | Compression | Splittable | Best For |
|--------|------|-------------|------------|----------|
| Parquet | Columnar | Snappy/Zstd/Gzip | ✅ | Analytics, data lake |
| ORC | Columnar | Zlib/Snappy | ✅ | Hive ecosystem |
| Avro | Row-based | Deflate/Snappy | ✅ | Streaming, schema evolution |
| CSV | Row-based | Gzip | ❌ (if compressed) | Exchange, human-readable |
| JSON | Row-based | Gzip | ❌ (if compressed) | APIs, semi-structured |
| Delta/Iceberg | Columnar+ | Snappy/Zstd | ✅ | ACID, time travel |

### Parquet Optimization

```python
import pyarrow as pa
import pyarrow.parquet as pq

# Write optimized Parquet
table = pa.Table.from_pandas(df)

pq.write_table(
    table,
    'data.parquet',
    compression='zstd',           # Best compression ratio
    # compression='snappy',       # Fastest decompression
    row_group_size=128 * 1024 * 1024,  # 128MB row groups
    use_dictionary=True,          # Dictionary encoding for low-cardinality
    write_statistics=True,        # Min/max stats for predicate pushdown
)

# Read with column pruning (only read needed columns)
table = pq.read_table('data.parquet', columns=['user_id', 'amount'])

# Read with predicate pushdown (skip row groups)
table = pq.read_table(
    'data.parquet',
    filters=[
        ('date', '>=', '2024-01-01'),
        ('region', '=', 'US'),
    ]
)

# Compression comparison
# | Codec  | Ratio | Write Speed | Read Speed | Use Case |
# |--------|-------|-------------|------------|----------|
# | None   | 1.0x  | Fastest     | Fastest    | Temp/cache |
# | Snappy | 2-4x  | Fast        | Fast       | Default (balanced) |
# | Zstd   | 3-6x  | Medium      | Fast       | Storage-optimized |
# | Gzip   | 3-5x  | Slow        | Medium     | Archive, max compat |
# | LZ4    | 2-3x  | Fastest     | Fastest    | Speed-critical |
```

### Optimal File Sizes

```python
# TARGET: 128MB - 1GB per file
# Too small: overhead per file (metadata, listing), bad parallelism
# Too large: slow to process single file, memory pressure

# In Spark
df.coalesce(10).write.parquet("output/")  # Reduce file count

# Calculate optimal file count
data_size_gb = 50
target_file_size_mb = 256
optimal_files = (data_size_gb * 1024) / target_file_size_mb  # ~200 files

# Compaction (fix small file problem)
spark.read.parquet("input/many_small_files/") \
    .repartition(200) \
    .write.mode("overwrite") \
    .parquet("output/compacted/")

# Delta Lake auto-compaction
spark.sql("""
    ALTER TABLE events SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true',
        'delta.targetFileSize' = '268435456'  -- 256MB
    )
""")
```

---

## 2. Partition Strategy

```python
# GOOD: Partition on date (queries always filter by date)
df.write.partitionBy("year", "month", "day").parquet("output/events/")
# Result: output/events/year=2024/month=01/day=15/part-00000.parquet

# BAD: Over-partition (high cardinality → millions of tiny files)
# df.write.partitionBy("user_id").parquet("output/")  # Don't do this!

# Rule of thumb:
# - Partition on columns in WHERE clause
# - Each partition should have 128MB+ of data
# - Max ~10,000 partitions per table
# - Low-cardinality columns only (date, region, status)

# Hive-style partitioning
# Query: SELECT * FROM events WHERE date = '2024-01-15'
# Without partition: scans ALL files
# With date partition: scans only /date=2024-01-15/ directory

# BigQuery partition + cluster
"""
CREATE TABLE events
PARTITION BY DATE(event_time)  -- Partition (reduces scan)
CLUSTER BY region, event_type  -- Cluster (sort within partition)
"""

# Snowflake clustering
"""
ALTER TABLE events CLUSTER BY (event_date, region)
"""
```

---

## 3. Query Optimization

```sql
-- 1. AVOID SELECT * (columnar storage benefits from column pruning)
-- BAD:
SELECT * FROM large_table WHERE date = '2024-01-15';
-- GOOD:
SELECT user_id, amount FROM large_table WHERE date = '2024-01-15';

-- 2. PUSH FILTERS DOWN (filter early)
-- BAD:
SELECT * FROM (SELECT * FROM orders JOIN customers USING(customer_id)) WHERE region = 'US';
-- GOOD:
SELECT * FROM orders o JOIN customers c ON o.customer_id = c.customer_id WHERE o.region = 'US';

-- 3. USE APPROXIMATE FUNCTIONS (for dashboards)
-- Exact (expensive):
SELECT COUNT(DISTINCT user_id) FROM events;  -- Full scan
-- Approximate (fast, <2% error):
SELECT APPROX_COUNT_DISTINCT(user_id) FROM events;  -- HyperLogLog

-- 4. AVOID CROSS JOINS
-- BAD:
SELECT * FROM a, b WHERE a.id = b.id;
-- GOOD:
SELECT * FROM a INNER JOIN b ON a.id = b.id;

-- 5. USE WINDOW FUNCTIONS instead of self-joins
-- BAD:
SELECT a.*, (SELECT MAX(date) FROM orders b WHERE b.customer_id = a.customer_id) as last_order
FROM orders a;
-- GOOD:
SELECT *, MAX(date) OVER (PARTITION BY customer_id) AS last_order FROM orders;

-- 6. MATERIALIZED CTEs for repeated subqueries
-- Consider materializing if CTE is used 3+ times
WITH expensive_cte AS MATERIALIZED (
    SELECT customer_id, SUM(amount) as total FROM orders GROUP BY 1
)
SELECT * FROM expensive_cte WHERE total > 1000;
```

---

## 4. Cost Monitoring

```python
import boto3
from datetime import datetime, timedelta

class CostMonitor:
    """Monitor and alert on data platform costs."""
    
    def __init__(self):
        self.ce = boto3.client('ce')  # Cost Explorer
    
    def get_daily_cost(self, service: str, days: int = 7) -> list[dict]:
        """Get daily cost for a specific service."""
        end = datetime.now().strftime('%Y-%m-%d')
        start = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        response = self.ce.get_cost_and_usage(
            TimePeriod={'Start': start, 'End': end},
            Granularity='DAILY',
            Filter={
                'Dimensions': {'Key': 'SERVICE', 'Values': [service]}
            },
            Metrics=['BlendedCost'],
        )
        
        return [
            {
                'date': r['TimePeriod']['Start'],
                'cost': float(r['Total']['BlendedCost']['Amount']),
            }
            for r in response['ResultsByTime']
        ]
    
    def detect_cost_anomaly(self, service: str, threshold_pct: float = 50) -> dict:
        """Alert if cost is significantly higher than average."""
        costs = self.get_daily_cost(service, days=14)
        recent = costs[-1]['cost']
        historical_avg = sum(c['cost'] for c in costs[:-1]) / (len(costs) - 1)
        
        increase_pct = ((recent - historical_avg) / historical_avg) * 100 if historical_avg > 0 else 0
        
        return {
            'service': service,
            'today_cost': recent,
            'avg_cost': round(historical_avg, 2),
            'increase_pct': round(increase_pct, 1),
            'is_anomaly': increase_pct > threshold_pct,
        }
    
    def get_top_queries_by_cost(self) -> list:
        """Get most expensive queries (BigQuery/Athena)."""
        # BigQuery: INFORMATION_SCHEMA.JOBS
        # Athena: via API get_query_execution
        pass

# Snowflake cost monitoring
"""
-- Top expensive queries
SELECT 
    query_id,
    query_text,
    warehouse_name,
    total_elapsed_time / 1000 as seconds,
    credits_used_cloud_services
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
ORDER BY total_elapsed_time DESC
LIMIT 20;

-- Cost by warehouse
SELECT 
    warehouse_name,
    SUM(credits_used) as total_credits,
    SUM(credits_used) * 4 as estimated_cost_usd  -- $4/credit
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE start_time >= DATEADD(month, -1, CURRENT_TIMESTAMP())
GROUP BY warehouse_name
ORDER BY total_credits DESC;
"""
```

---

## 5. Right-Sizing Compute

```python
# Spark: Right-sizing executors
# Formula: Total cores = num_executors × cores_per_executor
# Memory per executor: 4-8GB per core

# Small cluster (dev/test): 2 executors × 4 cores × 16GB = 8 cores, 32GB
# Medium cluster: 10 executors × 4 cores × 16GB = 40 cores, 160GB  
# Large cluster: 50 executors × 5 cores × 20GB = 250 cores, 1TB

# Optimization steps:
# 1. Start with default, monitor Spark UI
# 2. Check: GC time (increase memory if >10%)
# 3. Check: Shuffle spill (increase memory or reduce partitions)
# 4. Check: Task time variance (data skew)
# 5. Check: Total time vs task time (overhead if many small tasks)

# Snowflake: Warehouse sizing
"""
-- Monitor query queue time (if high → scale up)
SELECT 
    warehouse_name,
    AVG(queued_overload_time) / 1000 as avg_queue_seconds,
    MAX(queued_overload_time) / 1000 as max_queue_seconds
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE start_time >= DATEADD(day, -1, CURRENT_TIMESTAMP())
GROUP BY warehouse_name
HAVING avg_queue_seconds > 5;
-- If queue > 5s consistently, increase warehouse size or add multi-cluster
"""

# Cost saving strategies:
# 1. Auto-suspend (Snowflake: 300s, auto-resume)
# 2. Spot/preemptible instances (EMR, Dataproc: 60-80% savings)
# 3. Reserved capacity (steady workloads: 30-60% savings)
# 4. Right-size (don't use XL when M suffices)
# 5. Schedule non-critical jobs in off-peak hours
# 6. Data lifecycle (archive cold data to cheap storage)
```

---

## 6. Data Lifecycle Management

```python
# Tiered storage strategy
LIFECYCLE_POLICIES = {
    "bronze": {
        "hot_days": 7,        # Keep in standard storage
        "warm_days": 30,      # Move to IA
        "cold_days": 90,      # Move to Glacier
        "delete_days": 365,   # Delete after 1 year
    },
    "silver": {
        "hot_days": 30,
        "warm_days": 90,
        "cold_days": None,    # Keep indefinitely
        "delete_days": None,
    },
    "gold": {
        "hot_days": 90,
        "warm_days": 365,
        "cold_days": None,
        "delete_days": None,
    },
}

def estimate_storage_cost(data_size_tb: float, tier: str) -> dict:
    """Estimate monthly storage cost by tier."""
    costs_per_tb = {
        "standard": 23.0,    # $/TB/month
        "ia": 12.5,
        "glacier": 4.0,
        "deep_archive": 1.0,
    }
    
    policy = LIFECYCLE_POLICIES[tier]
    # Simplified: assume 20% of data in each tier
    total_cost = data_size_tb * costs_per_tb["standard"] * 0.2 + \
                 data_size_tb * costs_per_tb["ia"] * 0.3 + \
                 data_size_tb * costs_per_tb["glacier"] * 0.5
    
    return {"monthly_cost": round(total_cost, 2), "annual_cost": round(total_cost * 12, 2)}
```

---

## Interview Questions

### Beginner
1. **Why use Parquet over CSV?** Columnar (only read needed columns), compressed (2-10x smaller), schema-embedded, supports predicate pushdown (skip irrelevant data). Much faster for analytics.
2. **What is partition pruning?** Query optimizer skips reading partitions that don't match the WHERE clause. E.g., `WHERE date='2024-01-15'` only reads that day's partition, not all data.
3. **Why are small files a problem?** Each file has overhead: listing, metadata, opening/closing. 10,000 small files slower than 100 properly-sized files. Target 128MB-1GB per file.

### Intermediate
4. **How do you optimize a query that scans too much data?** Partition on filter columns, add clustering/Z-order, use columnar format, avoid SELECT *, push filters early, use approximate functions for dashboards.
5. **Explain predicate pushdown vs projection pushdown.** Predicate pushdown: push WHERE filters to storage (skip row groups/files). Projection pushdown: only read needed columns. Both reduce I/O. Parquet supports both via column statistics and columnar layout.
6. **How do you handle the small files problem in a streaming pipeline?** Trigger compaction periodically (OPTIMIZE in Delta Lake), write with appropriate trigger interval (larger batches → fewer files), auto-compact configuration, separate compaction job.

### Advanced
7. **Design a cost optimization strategy for a $50K/month data platform.** Identify top cost drivers (query cost explorer, warehouse metering). Quick wins: auto-suspend warehouses, compress data, partition for pruning. Medium: reserved pricing for steady workloads, spot for ETL. Long: data lifecycle policies, query governance, materialized views for expensive repeated queries.
8. **How do you benchmark and compare file format choices?** Test with representative data and queries. Measure: write time, file size, read time for different query patterns (full scan, point lookup, aggregation, filter). Consider: ecosystem support, evolution capabilities, ACID needs. Often Parquet+Snappy is the default.
9. **Optimize a daily pipeline that processes 10TB and costs $5K/day.** Profile: where is time/cost spent? Storage optimization (Zstd instead of uncompressed: 50% less data to read). Partition pruning (if not partitioned: 10x speedup). Reduce shuffles (fewer wide operations). Spot instances for ETL (60% savings). Cache intermediate results if reused. Incremental processing (only new data vs full recompute).

---

## Hands-On Exercise
1. Compare query performance: CSV vs Parquet vs Delta Lake
2. Benchmark compression codecs (Snappy vs Zstd vs Gzip) on real data
3. Implement partitioning and measure query speedup
4. Build a cost monitoring dashboard
5. Optimize a slow Spark job (identify and fix bottlenecks)
6. Design data lifecycle policy and estimate cost savings
