# Day 11: Spark Performance Tuning

## Learning Objectives
- Read and interpret the Spark UI effectively
- Identify and resolve common performance bottlenecks
- Master memory management, caching, and shuffle optimization
- Apply AQE and advanced tuning techniques

---

## 1. Understanding the Spark UI

### Key Tabs
- **Jobs**: One job per action. Shows timeline and stage breakdown
- **Stages**: Shows tasks, shuffle read/write, GC time, data skew
- **Storage**: Cached RDDs/DataFrames and memory usage
- **SQL**: Query plans, operator timelines, metrics per operator

### What to Look For
```
RED FLAGS in Spark UI:
├── Large shuffle write (data movement between stages)
├── Uneven task durations (data skew)
├── Spill to disk (memory pressure)
├── Many small tasks (too many partitions)
├── Few large tasks (too few partitions)
├── High GC time (>10% of task time)
└── Straggler tasks (one task much slower)
```

---

## 2. Shuffle Optimization

### Beginner: Understanding Shuffles

```python
# Operations that trigger shuffle:
# - groupBy, reduceByKey, aggregateByKey
# - join (unless broadcast)
# - repartition
# - distinct
# - sort/orderBy

# Default shuffle partitions
spark.conf.get("spark.sql.shuffle.partitions")  # Default: 200

# For small datasets, reduce shuffle partitions
spark.conf.set("spark.sql.shuffle.partitions", "50")

# Rule of thumb: 2-4x the number of cores
# Target partition size: 128MB - 256MB
```

### Intermediate: Reducing Shuffle Data

```python
# BAD: Shuffle entire dataset then filter
df.join(large_table, "key").filter(F.col("date") > "2024-01-01")

# GOOD: Filter first, reduce data before shuffle
df.filter(F.col("date") > "2024-01-01").join(large_table, "key")

# BAD: Multiple groupBy operations
df.groupBy("key").agg(F.sum("a")).join(
    df.groupBy("key").agg(F.avg("b")), "key"
)

# GOOD: Single groupBy with multiple aggregations
df.groupBy("key").agg(
    F.sum("a").alias("sum_a"),
    F.avg("b").alias("avg_b")
)

# Reduce shuffle size with selective columns
df.select("key", "amount").groupBy("key").agg(F.sum("amount"))
# vs
df.groupBy("key").agg(F.sum("amount"))  # Shuffles all columns
```

---

## 3. Handling Data Skew

### Detecting Skew

```python
# Check key distribution
df.groupBy("join_key").count().orderBy(F.desc("count")).show(20)

# In Spark UI: Look for tasks with much higher shuffle read
# One task with 10x data = skew
```

### Solving Skew

```python
# Method 1: Salting (add random prefix to skewed key)
import random

num_salts = 10

# Salt the skewed table
df_salted = df.withColumn(
    "salted_key",
    F.concat(F.col("join_key"), F.lit("_"), (F.rand() * num_salts).cast("int"))
)

# Explode the other table to match all salts
df_other_exploded = df_other.crossJoin(
    spark.range(num_salts).withColumnRenamed("id", "salt")
).withColumn(
    "salted_key",
    F.concat(F.col("join_key"), F.lit("_"), F.col("salt"))
)

# Join on salted key (distributes hot key across partitions)
result = df_salted.join(df_other_exploded, "salted_key")

# Method 2: Separate hot keys
hot_keys = ["key1", "key2"]  # Known skewed keys

df_hot = df.filter(F.col("key").isin(hot_keys))
df_cold = df.filter(~F.col("key").isin(hot_keys))

# Broadcast join for hot keys, regular join for cold
result_hot = df_hot.join(broadcast(other), "key")
result_cold = df_cold.join(other, "key")
result = result_hot.union(result_cold)

# Method 3: AQE Skew Join (Spark 3.0+)
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionFactor", "5")
spark.conf.set("spark.sql.adaptive.skewJoin.skewedPartitionThresholdInBytes", "256MB")
```

---

## 4. Memory Management & Caching

### Memory Architecture
```
Executor Memory Layout:
├── Reserved Memory (300MB fixed)
├── User Memory (40% of remaining) — your data structures, UDF objects
└── Unified Memory (60% of remaining)
    ├── Storage Memory (cached data, broadcasts)
    └── Execution Memory (shuffles, joins, sorts, aggregations)
    (These can borrow from each other dynamically)
```

### Caching Strategy

```python
# Cache when:
# 1. DataFrame is reused multiple times
# 2. Expensive computation (joins, aggregations)
# 3. Interactive exploration

# Storage levels
from pyspark import StorageLevel

df.cache()  # Same as MEMORY_AND_DISK
df.persist(StorageLevel.MEMORY_ONLY)       # Fastest, may lose partitions
df.persist(StorageLevel.MEMORY_AND_DISK)   # Spill to disk if needed (default)
df.persist(StorageLevel.DISK_ONLY)         # Large datasets, memory pressure
df.persist(StorageLevel.MEMORY_ONLY_SER)   # Serialized (less memory, more CPU)

# IMPORTANT: cache is lazy, trigger with action
df_cached = df.filter(F.col("active")).cache()
df_cached.count()  # Now actually cached

# Use cached DF multiple times
summary1 = df_cached.groupBy("region").agg(F.sum("amount"))
summary2 = df_cached.groupBy("product").agg(F.avg("amount"))

# Unpersist when done
df_cached.unpersist()

# Check what's cached
spark.catalog.isCached("my_table")
```

### When NOT to Cache
```python
# Don't cache if:
# - Used only once (adds overhead)
# - Data is small and fast to recompute
# - Memory is constrained
# - Data changes frequently

# Instead, consider checkpointing for very long DAGs
df.checkpoint()  # Breaks lineage, saves to reliable storage
```

---

## 5. Adaptive Query Execution (AQE)

```python
# AQE optimizes at runtime based on actual data statistics
spark.conf.set("spark.sql.adaptive.enabled", "true")  # Default in Spark 3.2+

# Feature 1: Coalesce Post-Shuffle Partitions
# Merges small partitions after shuffle
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.advisoryPartitionSizeInBytes", "128MB")

# Feature 2: Switch Join Strategy at Runtime
# Converts sort-merge join to broadcast if table is small after filter
spark.conf.set("spark.sql.adaptive.localShuffleReader.enabled", "true")

# Feature 3: Skew Join Optimization
# Splits skewed partitions into smaller ones
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")

# AQE means you don't need to manually tune shuffle.partitions as much
# It will auto-coalesce small partitions
```

---

## 6. Join Optimization

```python
# Join strategies (ordered by preference):
# 1. Broadcast Hash Join (one side < threshold)
# 2. Shuffle Hash Join (one side fits in memory)
# 3. Sort Merge Join (default for large-large joins)
# 4. Cartesian/Cross Join (avoid!)

# Force broadcast
from pyspark.sql.functions import broadcast
result = big_df.join(broadcast(small_df), "key")

# Broadcast threshold (default 10MB)
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "50MB")  # Increase
spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "-1")    # Disable auto-broadcast

# Bucketing for repeated joins on same key
(
    df.write
    .bucketBy(32, "customer_id")
    .sortBy("customer_id")
    .saveAsTable("orders_bucketed")
)
# Subsequent joins on customer_id avoid shuffle!
orders = spark.table("orders_bucketed")
customers = spark.table("customers_bucketed")  # Also bucketed by 32 on customer_id
result = orders.join(customers, "customer_id")  # No shuffle!

# Hint system
df1.join(df2.hint("merge"), "key")       # Force sort-merge
df1.join(df2.hint("shuffle_hash"), "key")  # Force shuffle-hash
```

---

## 7. Advanced Tuning Parameters

```python
# Executor configuration
spark.conf.set("spark.executor.memory", "8g")
spark.conf.set("spark.executor.cores", "4")
spark.conf.set("spark.executor.instances", "10")

# Memory fraction tuning
spark.conf.set("spark.memory.fraction", "0.6")           # Unified memory
spark.conf.set("spark.memory.storageFraction", "0.5")    # Storage vs execution

# Shuffle configuration
spark.conf.set("spark.sql.shuffle.partitions", "200")
spark.conf.set("spark.shuffle.compress", "true")
spark.conf.set("spark.shuffle.spill.compress", "true")

# Serialization
spark.conf.set("spark.serializer", "org.apache.spark.serializer.KryoSerializer")

# Garbage Collection
spark.conf.set("spark.executor.extraJavaOptions", "-XX:+UseG1GC")

# Network
spark.conf.set("spark.network.timeout", "800s")

# Speculation (re-launch slow tasks)
spark.conf.set("spark.speculation", "true")
spark.conf.set("spark.speculation.quantile", "0.9")
```

---

## 8. Troubleshooting Checklist

```markdown
## Performance Debugging Flow:

1. Check explain() plan
   - Are filters pushed down?
   - Which join strategy is chosen?
   - Any full table scans?

2. Check Spark UI Stages
   - Which stage is slowest?
   - Shuffle data size (reduce with early filtering)
   - Spill to disk? (increase memory or reduce data)

3. Check Task Distribution
   - Even distribution? → Good
   - Skewed? → Salt keys or AQE
   - Too many small tasks? → Coalesce
   - Too few large tasks? → Repartition

4. Check Memory
   - GC time > 10%? → Increase memory or reduce cached data
   - OOM errors? → Reduce partition size, increase executor memory

5. Check I/O
   - Reading full Parquet or partition-pruned?
   - File sizes optimal (128MB-1GB)?
   - Too many small files? → Compact
```

---

## Interview Questions

### Beginner
1. **What is a shuffle in Spark?** Data redistribution across partitions/executors. Triggered by wide operations (groupBy, join, repartition). Expensive due to network + disk I/O.
2. **What does caching do?** Stores computed DataFrame in memory/disk for reuse. Avoids recomputation. Must be triggered by an action.
3. **How many partitions should you have?** Rule of thumb: 2-4x available cores. Target 128MB-256MB per partition.

### Intermediate
4. **How does AQE improve performance?** Runtime optimization: coalesces small shuffle partitions, converts joins to broadcast if data is small after filters, handles skew by splitting large partitions.
5. **Explain the difference between persist and checkpoint.** Persist: keeps lineage (can recompute), in-memory/disk cache. Checkpoint: breaks lineage, saves to reliable storage (HDFS). Use checkpoint for very long DAGs to avoid stack overflow on driver.
6. **What causes OOM in Spark?** Common causes: single large partition (skew), collecting too much to driver, caching more than available memory, UDF memory leaks, too many columns in shuffle.

### Advanced
7. **Design a tuning strategy for a job running 3x slower than expected.** Check Spark UI → identify bottleneck stage → check for skew (salt or AQE) → verify partition sizes (repartition/coalesce) → ensure filters pushed down → check if broadcast possible → verify no disk spill → tune memory fraction.
8. **Explain when sort-merge join is better than broadcast hash join.** When both tables are large (neither fits in executor memory). Sort-merge handles large-large joins with predictable memory (O(partition) not O(table)). It requires both sides sorted on join key.
9. **How do you optimize a Spark job that reads 100TB of data daily?** Partition by date for pruning, Z-order on query columns, use Delta Lake for skip indexing, broadcast dimension tables, AQE for runtime optimization, cache hot dimensions, right-size executors (more cores → less executor overhead).

---

## Hands-On Exercise
1. Create a dataset with intentional skew (one key has 100x more records)
2. Run a join, observe skew in Spark UI (uneven task times)
3. Fix with salting, measure improvement
4. Enable AQE, compare automatic skew handling
5. Benchmark: cached vs uncached with multiple downstream queries
6. Use explain() to verify predicate pushdown and join strategies
