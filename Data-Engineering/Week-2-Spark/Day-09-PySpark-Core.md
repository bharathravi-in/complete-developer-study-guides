# Day 9: PySpark Core — RDDs, DataFrames & Partitioning

## Learning Objectives
- Master PySpark DataFrame operations for large-scale data processing
- Understand RDDs vs DataFrames tradeoffs
- Implement partitioning strategies for optimal performance
- Read/write various data formats efficiently

---

## 1. PySpark Session Setup

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *

# Create SparkSession
spark = (
    SparkSession.builder
    .appName("DataEngineering")
    .master("local[*]")  # Use all cores
    .config("spark.sql.adaptive.enabled", "true")  # AQE
    .config("spark.sql.shuffle.partitions", "200")
    .config("spark.driver.memory", "4g")
    .config("spark.executor.memory", "4g")
    .getOrCreate()
)

# Set log level
spark.sparkContext.setLogLevel("WARN")
```

---

## 2. RDD Fundamentals

### Beginner: Basic RDD Operations

```python
# Create RDD from list
rdd = spark.sparkContext.parallelize([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], numSlices=4)

# Transformations (lazy - build DAG)
squared = rdd.map(lambda x: x ** 2)
evens = rdd.filter(lambda x: x % 2 == 0)
pairs = rdd.map(lambda x: (x % 3, x))  # Key-value pairs

# Actions (trigger execution)
print(squared.collect())       # [1, 4, 9, 16, ...]
print(evens.count())           # 5
print(rdd.reduce(lambda a, b: a + b))  # 55

# Word count - classic MapReduce
text_rdd = spark.sparkContext.textFile("data/book.txt")
word_counts = (
    text_rdd
    .flatMap(lambda line: line.split())
    .map(lambda word: (word.lower(), 1))
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda x: x[1], ascending=False)
)
```

### When to Use RDDs
- Unstructured data without schema
- Low-level transformations (custom partitioners)
- Legacy code migration
- **Always prefer DataFrames** for structured data (Catalyst optimizer)

---

## 3. DataFrame Operations

### Beginner: Creating and Basic Operations

```python
# Read CSV
df = spark.read.csv("data/sales.csv", header=True, inferSchema=True)

# Read Parquet (preferred format)
df = spark.read.parquet("data/sales/")

# Read JSON
df = spark.read.json("data/events.json")

# Basic operations
df.printSchema()
df.show(5, truncate=False)
df.describe().show()

# Select and filter
result = (
    df.select("customer_id", "amount", "date")
    .filter(F.col("amount") > 100)
    .filter(F.col("date") >= "2024-01-01")
)

# Add columns
df_enriched = df.withColumn("year", F.year("date")) \
               .withColumn("amount_usd", F.col("amount") * F.col("exchange_rate")) \
               .withColumn("is_large", F.when(F.col("amount") > 1000, True).otherwise(False))

# Drop and rename
df_clean = df.drop("internal_id") \
             .withColumnRenamed("cust_id", "customer_id")
```

### Intermediate: Aggregations and Joins

```python
# Group by with multiple aggregations
summary = (
    df.groupBy("region", "product_category")
    .agg(
        F.sum("amount").alias("total_revenue"),
        F.count("*").alias("transaction_count"),
        F.avg("amount").alias("avg_order_value"),
        F.countDistinct("customer_id").alias("unique_customers"),
        F.max("date").alias("last_order_date"),
    )
    .orderBy(F.desc("total_revenue"))
)

# Window functions
from pyspark.sql.window import Window

window_spec = Window.partitionBy("customer_id").orderBy(F.desc("date"))

df_ranked = df.withColumn("rank", F.row_number().over(window_spec))
df_latest = df_ranked.filter(F.col("rank") == 1)  # Latest order per customer

# Running totals
running_window = Window.partitionBy("customer_id").orderBy("date").rowsBetween(
    Window.unboundedPreceding, Window.currentRow
)
df_running = df.withColumn("cumulative_spend", F.sum("amount").over(running_window))

# Joins
customers = spark.read.parquet("data/customers/")
orders = spark.read.parquet("data/orders/")

# Inner join
enriched = orders.join(customers, orders.customer_id == customers.id, "inner")

# Left join with null handling
result = orders.join(
    customers, 
    orders.customer_id == customers.id, 
    "left"
).fillna({"customer_name": "Unknown"})

# Broadcast join (small table fits in memory)
from pyspark.sql.functions import broadcast
result = orders.join(broadcast(customers), "customer_id")
```

### Advanced: Complex Transformations

```python
# Explode arrays
df_with_tags = spark.createDataFrame([
    (1, ["python", "spark", "sql"]),
    (2, ["java", "kafka"]),
], ["user_id", "skills"])

df_exploded = df_with_tags.select("user_id", F.explode("skills").alias("skill"))

# Pivot tables
pivot_df = (
    df.groupBy("region")
    .pivot("quarter", ["Q1", "Q2", "Q3", "Q4"])
    .agg(F.sum("revenue"))
)

# UDFs (use sparingly - breaks Catalyst optimization)
from pyspark.sql.functions import udf, pandas_udf

@udf(returnType=StringType())
def classify_amount(amount):
    if amount > 10000: return "enterprise"
    elif amount > 1000: return "mid-market"
    else: return "smb"

# Pandas UDF (vectorized - much faster than row-level UDF)
@pandas_udf(FloatType())
def normalize(series: pd.Series) -> pd.Series:
    return (series - series.mean()) / series.std()

df_classified = df.withColumn("segment", classify_amount("amount"))
df_normalized = df.withColumn("amount_normalized", normalize("amount"))

# Handling nested JSON
nested_df = spark.read.json("data/events.json")
flat_df = nested_df.select(
    "event_id",
    F.col("user.name").alias("user_name"),
    F.col("user.email").alias("user_email"),
    F.col("metadata.timestamp").alias("event_time"),
    F.explode("items").alias("item")
).select(
    "*",
    F.col("item.product_id").alias("product_id"),
    F.col("item.quantity").alias("quantity"),
)
```

---

## 4. Partitioning Strategies

```python
# Check current partitions
print(f"Partitions: {df.rdd.getNumPartitions()}")

# Repartition (full shuffle - expensive but even distribution)
df_repartitioned = df.repartition(100)  # By count
df_repartitioned = df.repartition("date")  # By column (hash partitioning)
df_repartitioned = df.repartition(50, "region", "date")  # By columns with count

# Coalesce (reduce partitions without full shuffle - cheaper)
df_coalesced = df.coalesce(10)  # Only for reducing partitions

# When to use each:
# repartition: increase partitions, need even distribution, before join on key
# coalesce: reduce partitions (e.g., before writing fewer files)

# Partition-aware writing
df.write.partitionBy("year", "month").parquet("output/sales/")
# Creates: output/sales/year=2024/month=01/part-00000.parquet

# Bucketing (pre-sort for faster joins)
df.write.bucketBy(32, "customer_id").sortBy("date").saveAsTable("bucketed_orders")
```

---

## 5. Reading & Writing Data Formats

```python
# === PARQUET (preferred) ===
# Columnar, compressed, schema-embedded
df.write.mode("overwrite").parquet("output/data.parquet")
df = spark.read.parquet("output/data.parquet")

# === DELTA LAKE ===
df.write.format("delta").mode("overwrite").save("output/delta_table")
df = spark.read.format("delta").load("output/delta_table")

# === CSV ===
df.write.option("header", True).csv("output/data.csv")
df = spark.read.option("header", True).option("inferSchema", True).csv("input/*.csv")

# === JSON ===
df.write.json("output/data.json")

# === Explicit Schema (always use in production) ===
schema = StructType([
    StructField("id", LongType(), nullable=False),
    StructField("name", StringType(), nullable=True),
    StructField("amount", DoubleType(), nullable=True),
    StructField("date", DateType(), nullable=True),
    StructField("metadata", StructType([
        StructField("source", StringType()),
        StructField("version", IntegerType()),
    ])),
])

df = spark.read.schema(schema).json("input/events/")

# === Write optimization ===
# Control file sizes
df.coalesce(10).write.parquet("output/")  # 10 files
df.repartition(1).write.parquet("output/")  # Single file (small data only)

# Compression
df.write.option("compression", "snappy").parquet("output/")  # Default, fast
df.write.option("compression", "zstd").parquet("output/")    # Better ratio
```

---

## 6. Performance Tips

```python
# 1. Always use DataFrames over RDDs
# 2. Use built-in functions (F.xxx) over UDFs
# 3. Filter early (predicate pushdown)
# 4. Use broadcast for small tables (<10MB)
# 5. Avoid collect() on large data
# 6. Cache intermediate results if reused

df_cached = df.filter(F.col("active") == True).cache()
df_cached.count()  # Trigger cache

# 7. Use explain() to understand query plan
df.explain(mode="extended")

# 8. Monitor with Spark UI (localhost:4040)
```

---

## Interview Questions

### Beginner
1. **What's the difference between RDD and DataFrame?** DataFrame has schema, uses Catalyst optimizer, supports SQL. RDD is low-level, unstructured, no optimization. Always prefer DataFrame.
2. **What's the difference between transformation and action?** Transformations are lazy (map, filter, select) - build a DAG. Actions trigger execution (count, collect, write).
3. **What is lazy evaluation?** Spark doesn't execute transformations immediately. It builds an execution plan (DAG) and optimizes it before running. Triggered only by actions.

### Intermediate
4. **When would you use repartition vs coalesce?** Repartition for increasing partitions or redistributing evenly (full shuffle). Coalesce only for reducing partitions (no shuffle, may be uneven).
5. **Why avoid UDFs? When are they necessary?** UDFs break Catalyst optimization, serialize data to Python. Use when no built-in function exists. Prefer Pandas UDFs (vectorized) over row-level UDFs.
6. **How does broadcast join work?** Small table is serialized and sent to all executors. Avoids shuffle of the large table. Use when one side is <10MB (configurable).

### Advanced
7. **Explain partition pruning and predicate pushdown.** Partition pruning: skip reading partitions not matching filter. Predicate pushdown: push filters to storage layer (Parquet reads only needed row groups). Both reduce I/O dramatically.
8. **How do you handle data skew in Spark joins?** Salting (add random prefix to skewed key), AQE skew join optimization, broadcast if one side is small, separate processing for hot keys.
9. **Design a partitioning strategy for a 10TB event table.** Partition by date (year/month/day) for time-range queries. Within partitions, target 128MB-1GB files. Use Z-ordering on frequently filtered columns. Consider bucketing on join keys.

---

## Hands-On Exercise
1. Read a large CSV (generate 1M+ rows) with explicit schema
2. Perform transformations: filter, aggregate, window functions
3. Join with a dimension table using broadcast
4. Write partitioned Parquet output
5. Compare execution plans with explain()
6. Experiment with different partition counts and measure performance
