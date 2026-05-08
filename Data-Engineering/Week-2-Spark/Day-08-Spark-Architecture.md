# Day 8: Apache Spark Architecture

## Overview
Apache Spark is the de facto standard for big data processing. Understanding its architecture is essential for writing efficient pipelines.

---

## 1. What is Spark?

A **distributed computing engine** for processing large datasets across clusters. Key features:
- In-memory processing (10-100x faster than Hadoop MapReduce)
- Unified engine: batch, streaming, SQL, ML, graph
- Lazy evaluation with DAG optimization
- Fault-tolerant via lineage

---

## 2. Architecture

```
┌─────────────────────────────────────────────┐
│                 DRIVER                        │
│  ┌─────────────────────────────────────┐    │
│  │  SparkContext / SparkSession         │    │
│  │  ├── DAG Scheduler                   │    │
│  │  ├── Task Scheduler                  │    │
│  │  └── Block Manager                   │    │
│  └─────────────────────────────────────┘    │
└─────────────────────┬───────────────────────┘
                      │ (sends tasks)
          ┌───────────┼───────────┐
          ▼           ▼           ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  EXECUTOR 1  │ │  EXECUTOR 2  │ │  EXECUTOR 3  │
│  ┌────────┐  │ │  ┌────────┐  │ │  ┌────────┐  │
│  │ Task 1 │  │ │  │ Task 3 │  │ │  │ Task 5 │  │
│  │ Task 2 │  │ │  │ Task 4 │  │ │  │ Task 6 │  │
│  └────────┘  │ │  └────────┘  │ │  └────────┘  │
│  [Cache]     │ │  [Cache]     │ │  [Cache]     │
└──────────────┘ └──────────────┘ └──────────────┘
     Worker 1        Worker 2        Worker 3
```

### Components
| Component | Role |
|-----------|------|
| **Driver** | Orchestrates the application, creates SparkSession, builds DAG |
| **Cluster Manager** | Allocates resources (YARN, Kubernetes, Standalone, Mesos) |
| **Executor** | JVM process on worker node, runs tasks, caches data |
| **Task** | Smallest unit of work, processes one partition |
| **Partition** | Chunk of data processed by one task |

---

## 3. Execution Model

### Lazy Evaluation
```python
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("demo").getOrCreate()

# Nothing executes yet — just builds a plan
df = spark.read.parquet("s3://data/events/")       # Lazy
filtered = df.filter(df.event_type == "purchase")   # Lazy
grouped = filtered.groupBy("user_id").count()       # Lazy

# NOW it executes (action triggers computation)
grouped.show()  # Action!
grouped.write.parquet("s3://output/")  # Action!
```

### Transformations vs Actions
| Transformations (Lazy) | Actions (Trigger Execution) |
|---|---|
| `filter()`, `select()`, `groupBy()` | `show()`, `count()`, `collect()` |
| `join()`, `withColumn()`, `agg()` | `write()`, `save()`, `take()` |
| `map()`, `flatMap()`, `distinct()` | `foreach()`, `reduce()` |

### DAG (Directed Acyclic Graph)
```
read.parquet → filter → groupBy → count → write
     ↓            ↓         ↓        ↓
  [Stage 1: No shuffle]  [Stage 2: Shuffle]
```

- Spark builds a DAG of transformations
- Optimizer (Catalyst) restructures for efficiency
- DAG is split into **stages** at shuffle boundaries
- Each stage has **tasks** (one per partition)

---

## 4. Shuffles — The Performance Killer

A **shuffle** redistributes data across partitions (network I/O):

```python
# Operations that cause shuffles:
df.groupBy("user_id").count()      # Shuffle: group by key
df.join(other_df, "user_id")       # Shuffle: both sides repartitioned
df.repartition(100)                # Shuffle: explicit repartition
df.distinct()                      # Shuffle: check all partitions
df.orderBy("amount")               # Shuffle: global sort
```

### Minimizing Shuffles
```python
# BAD: Multiple shuffles
result = (df
    .groupBy("user_id").agg(sum("amount"))
    .join(users_df, "user_id")      # Another shuffle!
    .orderBy("total")               # Another shuffle!
)

# BETTER: Broadcast small table (no shuffle for join)
from pyspark.sql.functions import broadcast

result = (df
    .join(broadcast(users_df), "user_id")  # No shuffle!
    .groupBy("user_id").agg(sum("amount"))
)
```

---

## 5. Memory Management

### Storage Levels
```python
from pyspark import StorageLevel

# Cache in memory (deserialized) — fastest, most memory
df.cache()  # Same as: df.persist(StorageLevel.MEMORY_ONLY)

# Memory + Disk (spills to disk if no memory)
df.persist(StorageLevel.MEMORY_AND_DISK)

# Serialized (less memory, more CPU)
df.persist(StorageLevel.MEMORY_ONLY_SER)

# Unpersist when done
df.unpersist()
```

### Memory Regions
```
Executor Memory (e.g., 4GB)
├── Reserved: 300MB (Spark internal)
├── User Memory: 40% of remaining — Your objects, UDFs
├── Unified Memory: 60% of remaining
│   ├── Storage: Cached DataFrames/RDDs
│   └── Execution: Shuffles, joins, sorts, aggregations
│       (can borrow from Storage if needed)
```

---

## 6. Cluster Managers

### Standalone
```bash
# Start master
./sbin/start-master.sh

# Start workers
./sbin/start-worker.sh spark://master:7077

# Submit job
spark-submit --master spark://master:7077 my_job.py
```

### YARN (Hadoop)
```bash
spark-submit \
    --master yarn \
    --deploy-mode cluster \
    --num-executors 10 \
    --executor-memory 4g \
    --executor-cores 4 \
    my_job.py
```

### Kubernetes
```bash
spark-submit \
    --master k8s://https://k8s-cluster:443 \
    --deploy-mode cluster \
    --conf spark.kubernetes.container.image=my-spark:3.5 \
    --conf spark.executor.instances=5 \
    my_job.py
```

---

## 7. SparkSession — Entry Point

```python
from pyspark.sql import SparkSession

spark = (SparkSession.builder
    .appName("DataPipeline")
    .master("local[*]")              # Local mode: use all cores
    .config("spark.sql.shuffle.partitions", 200)
    .config("spark.executor.memory", "4g")
    .config("spark.sql.adaptive.enabled", "true")  # AQE
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
    .enableHiveSupport()             # Access Hive metastore
    .getOrCreate())

# Access underlying SparkContext
sc = spark.sparkContext
print(f"Spark version: {spark.version}")
print(f"App ID: {sc.applicationId}")
print(f"Default parallelism: {sc.defaultParallelism}")
```

---

## 8. Deployment Modes

| Mode | Driver Location | Use Case |
|------|----------------|----------|
| **Client** | Local machine | Interactive (notebooks, debugging) |
| **Cluster** | On a worker node | Production (driver failure doesn't affect cluster) |
| **Local** | Same JVM | Development, testing |

---

## 9. Key Configuration Parameters

```python
# Critical configs for performance
configs = {
    # Parallelism
    "spark.sql.shuffle.partitions": "200",        # Default shuffle partitions
    "spark.default.parallelism": "100",           # RDD parallelism
    
    # Memory
    "spark.executor.memory": "4g",
    "spark.driver.memory": "2g",
    "spark.memory.fraction": "0.6",               # Fraction for execution+storage
    
    # Adaptive Query Execution (Spark 3+)
    "spark.sql.adaptive.enabled": "true",
    "spark.sql.adaptive.coalescePartitions.enabled": "true",
    "spark.sql.adaptive.skewJoin.enabled": "true",
    
    # Serialization
    "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
    
    # Dynamic Allocation
    "spark.dynamicAllocation.enabled": "true",
    "spark.dynamicAllocation.minExecutors": "2",
    "spark.dynamicAllocation.maxExecutors": "20",
}
```

---

## 10. Hands-On: First Spark Job

```python
"""
Your first PySpark job: Analyze web events
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, sum as spark_sum, desc

# Initialize
spark = SparkSession.builder.appName("FirstJob").master("local[*]").getOrCreate()

# Read data
events = spark.read.parquet("data/events/")

# Check schema and stats
events.printSchema()
print(f"Total records: {events.count()}")
print(f"Partitions: {events.rdd.getNumPartitions()}")

# Transform
top_users = (events
    .filter(col("event_type") == "purchase")
    .groupBy("user_id")
    .agg(
        count("*").alias("purchase_count"),
        spark_sum("amount").alias("total_spent")
    )
    .orderBy(desc("total_spent"))
    .limit(100)
)

# Write output
top_users.write.mode("overwrite").parquet("output/top_users/")

# Check execution plan
top_users.explain(mode="extended")

spark.stop()
```

---

## Key Takeaways
- Spark uses lazy evaluation — build a DAG, then execute on action
- Shuffles are expensive (network I/O) — minimize them
- Broadcast small tables to avoid shuffle joins
- Use Adaptive Query Execution (AQE) in Spark 3+
- Understand memory management to avoid OOM errors
- Choose cluster manager based on your infra (K8s is the future)

## Tomorrow
**Day 9**: PySpark Core — RDDs, transformations, actions, and partitioning strategies.
