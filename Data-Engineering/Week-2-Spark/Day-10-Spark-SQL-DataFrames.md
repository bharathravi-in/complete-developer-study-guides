# Day 10: Spark SQL & Advanced DataFrames

## Learning Objectives
- Master Spark SQL syntax and Catalog API
- Understand Catalyst Optimizer internals
- Write efficient UDFs and Pandas UDFs
- Handle complex data types (arrays, maps, structs)

---

## 1. Spark SQL Fundamentals

```python
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("SparkSQL").getOrCreate()

# Register DataFrame as SQL view
df = spark.read.parquet("data/orders/")
df.createOrReplaceTempView("orders")

# Query with SQL
result = spark.sql("""
    SELECT 
        customer_id,
        COUNT(*) as order_count,
        SUM(amount) as total_spent,
        AVG(amount) as avg_order,
        MAX(order_date) as last_order
    FROM orders
    WHERE status = 'completed'
      AND order_date >= '2024-01-01'
    GROUP BY customer_id
    HAVING COUNT(*) > 5
    ORDER BY total_spent DESC
    LIMIT 100
""")

# Create permanent table in Spark catalog
df.write.saveAsTable("warehouse.orders")  # Persisted to warehouse

# Show available tables
spark.catalog.listTables("default")
spark.catalog.listColumns("orders")
```

### CTEs and Subqueries

```python
result = spark.sql("""
    WITH monthly_revenue AS (
        SELECT 
            DATE_TRUNC('month', order_date) as month,
            region,
            SUM(amount) as revenue
        FROM orders
        GROUP BY 1, 2
    ),
    ranked AS (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY month ORDER BY revenue DESC) as rank,
            LAG(revenue) OVER (PARTITION BY region ORDER BY month) as prev_month_revenue
        FROM monthly_revenue
    )
    SELECT *,
        ROUND((revenue - prev_month_revenue) / prev_month_revenue * 100, 2) as mom_growth_pct
    FROM ranked
    WHERE rank <= 5
""")
```

---

## 2. Catalyst Optimizer

```python
# View the execution plan
df_result = (
    df.filter(F.col("amount") > 100)
    .join(customers, "customer_id")
    .groupBy("region")
    .agg(F.sum("amount"))
)

# Simple plan
df_result.explain()

# Extended plan (Parsed → Analyzed → Optimized → Physical)
df_result.explain(mode="extended")

# Formatted plan (easier to read)
df_result.explain(mode="formatted")

# Cost-based plan
df_result.explain(mode="cost")
```

### How Catalyst Works
1. **Parsing**: SQL/DataFrame → Unresolved Logical Plan
2. **Analysis**: Resolve columns, tables → Resolved Logical Plan
3. **Optimization**: Apply rules (predicate pushdown, constant folding, column pruning)
4. **Physical Planning**: Choose join strategy, scan method → Physical Plan
5. **Code Generation**: Whole-stage code gen → JVM bytecode

### Key Optimizations
```python
# Predicate Pushdown (filter pushed to data source)
df.filter(F.col("date") == "2024-01-01")  # Only reads matching partitions

# Column Pruning (only read needed columns)
df.select("id", "amount")  # Won't read other columns from Parquet

# Constant Folding
df.filter(F.lit(1) + F.lit(1) > F.col("x"))  # Optimized to 2 > x

# Join Reordering (with CBO enabled)
spark.conf.set("spark.sql.cbo.enabled", "true")
spark.conf.set("spark.sql.cbo.joinReorder.enabled", "true")
```

---

## 3. User-Defined Functions (UDFs)

### Basic UDF (Row-level, slow)

```python
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType, ArrayType, StructType, StructField

# Simple UDF
@udf(returnType=StringType())
def extract_domain(email: str) -> str:
    if email and '@' in email:
        return email.split('@')[1]
    return None

df.withColumn("email_domain", extract_domain("email"))

# UDF returning complex type
@udf(returnType=ArrayType(StringType()))
def parse_tags(tags_str: str):
    if tags_str:
        return [t.strip() for t in tags_str.split(',')]
    return []

# Register for SQL use
spark.udf.register("extract_domain", extract_domain)
spark.sql("SELECT extract_domain(email) FROM users")
```

### Pandas UDF (Vectorized — 10-100x faster)

```python
from pyspark.sql.functions import pandas_udf
import pandas as pd

# Series to Series (map)
@pandas_udf(FloatType())
def zscore(series: pd.Series) -> pd.Series:
    return (series - series.mean()) / series.std()

df.withColumn("amount_zscore", zscore("amount"))

# Series to Scalar (aggregation)
@pandas_udf(FloatType())
def weighted_avg(values: pd.Series, weights: pd.Series) -> float:
    return (values * weights).sum() / weights.sum()

df.groupBy("region").agg(weighted_avg("amount", "quantity").alias("weighted_avg_amount"))

# Iterator of Series (for expensive initialization)
from typing import Iterator

@pandas_udf(StringType())
def predict_batch(iterator: Iterator[pd.Series]) -> Iterator[pd.Series]:
    # Load model once
    import joblib
    model = joblib.load("/models/classifier.pkl")
    
    for batch in iterator:
        yield pd.Series(model.predict(batch.values.reshape(-1, 1)))

df.withColumn("prediction", predict_batch("features"))

# Grouped Map (apply function to each group)
@pandas_udf(df.schema, functionType=PandasUDFType.GROUPED_MAP)
def normalize_per_group(pdf: pd.DataFrame) -> pd.DataFrame:
    pdf['amount_normalized'] = (pdf['amount'] - pdf['amount'].mean()) / pdf['amount'].std()
    return pdf

df.groupBy("region").apply(normalize_per_group)
```

---

## 4. Complex Data Types

```python
# === Arrays ===
df_with_arrays = spark.createDataFrame([
    (1, ["python", "spark", "sql"], [90, 85, 92]),
    (2, ["java", "scala"], [88, 91]),
], ["id", "skills", "scores"])

# Array operations
df_with_arrays.select(
    "id",
    F.size("skills").alias("num_skills"),
    F.array_contains("skills", "python").alias("knows_python"),
    F.element_at("skills", 1).alias("primary_skill"),  # 1-indexed
    F.array_sort("skills").alias("sorted_skills"),
    F.arrays_zip("skills", "scores").alias("skill_scores"),
    F.aggregate("scores", F.lit(0), lambda acc, x: acc + x).alias("total_score"),
).show(truncate=False)

# Explode array to rows
df_with_arrays.select("id", F.explode("skills").alias("skill")).show()

# === Maps ===
df_with_maps = spark.createDataFrame([
    (1, {"lang": "python", "level": "senior"}),
    (2, {"lang": "java", "level": "mid"}),
], ["id", "attributes"])

df_with_maps.select(
    "id",
    F.col("attributes")["lang"].alias("language"),
    F.map_keys("attributes").alias("keys"),
    F.map_values("attributes").alias("values"),
).show()

# === Structs ===
df_nested = spark.createDataFrame([
    (1, ("John", "Doe", "john@example.com")),
    (2, ("Jane", "Smith", "jane@example.com")),
], ["id", "name"])

# Access struct fields
df_nested.select("id", "name._1", "name._2").show()

# Create struct
df.select(
    F.struct("first_name", "last_name", "email").alias("user_info")
).show()
```

---

## 5. Date & Time Operations

```python
from pyspark.sql import functions as F

# Current timestamps
df.withColumn("now", F.current_timestamp())
df.withColumn("today", F.current_date())

# Parse dates
df.withColumn("parsed", F.to_date("date_str", "yyyy-MM-dd"))
df.withColumn("parsed_ts", F.to_timestamp("ts_str", "yyyy-MM-dd HH:mm:ss"))

# Extract components
df.select(
    F.year("date").alias("year"),
    F.month("date").alias("month"),
    F.dayofmonth("date").alias("day"),
    F.dayofweek("date").alias("dow"),  # 1=Sunday
    F.quarter("date").alias("quarter"),
    F.weekofyear("date").alias("week"),
    F.hour("timestamp").alias("hour"),
)

# Date arithmetic
df.withColumn("next_week", F.date_add("date", 7))
df.withColumn("last_month", F.add_months("date", -1))
df.withColumn("days_since", F.datediff(F.current_date(), "date"))
df.withColumn("months_between", F.months_between(F.current_date(), "date"))

# Truncate
df.withColumn("month_start", F.date_trunc("month", "date"))
df.withColumn("week_start", F.date_trunc("week", "date"))

# Format
df.withColumn("formatted", F.date_format("date", "MMM dd, yyyy"))
```

---

## 6. Spark SQL Functions Reference

```python
# String functions
F.lower("col"), F.upper("col"), F.trim("col")
F.concat("col1", F.lit("-"), "col2")
F.concat_ws(",", "col1", "col2", "col3")
F.substring("col", 1, 5)
F.regexp_extract("col", r"(\d+)", 1)
F.regexp_replace("col", r"\s+", " ")
F.split("col", ",")
F.length("col")

# Null handling
F.coalesce("col1", "col2", F.lit("default"))
F.when(F.col("x").isNull(), F.lit(0)).otherwise(F.col("x"))
F.nanvl("col", F.lit(0))  # Replace NaN

# Conditional
F.when(F.col("x") > 100, "high") \
 .when(F.col("x") > 50, "medium") \
 .otherwise("low")

# Aggregations
F.approx_count_distinct("col")  # HyperLogLog estimate
F.percentile_approx("col", [0.25, 0.5, 0.75])
F.collect_list("col")  # All values in group as array
F.collect_set("col")   # Distinct values in group

# Math
F.round("col", 2), F.ceil("col"), F.floor("col")
F.log("col"), F.exp("col"), F.pow("col", 2)
F.abs("col")
```

---

## Interview Questions

### Beginner
1. **How do you create a temporary view in Spark?** `df.createOrReplaceTempView("name")` — available only in the SparkSession. Use `createOrReplaceGlobalTempView` for cross-session.
2. **What is Spark's Catalog?** Metadata store tracking databases, tables, columns, functions. Access via `spark.catalog`.
3. **Difference between spark.sql() and DataFrame API?** Equivalent — both go through Catalyst. Choose based on team preference. SQL better for complex analytics, API better for programmatic pipelines.

### Intermediate
4. **What optimizations does Catalyst perform?** Predicate pushdown, column pruning, constant folding, join reordering (CBO), broadcast join selection, partition pruning.
5. **When should you use Pandas UDFs over regular UDFs?** Always when possible. Pandas UDFs use Arrow serialization (columnar, no per-row Python overhead). 10-100x faster. Regular UDFs only for edge cases.
6. **How does whole-stage code generation work?** Catalyst compiles the query plan into a single JVM function (like hand-written code), eliminating virtual function calls between operators.

### Advanced
7. **How do you debug a slow Spark SQL query?** Check explain() for full scans vs pushdown, look at Spark UI for shuffle sizes and skew, check if AQE is coalescing shuffle partitions, verify partition pruning works, look for UDFs breaking optimization.
8. **Explain cost-based optimization (CBO) in Spark.** Uses table statistics (row count, column stats, histograms) to choose optimal join order and strategy. Enable with `spark.sql.cbo.enabled=true`. Run ANALYZE TABLE to collect stats.
9. **How do you handle evolving schemas in production?** Schema evolution with Delta Lake (mergeSchema), use explicit schemas in readers, version control schemas, validate schema compatibility before processing.

---

## Hands-On Exercise
1. Create tables from Parquet, register as views, query with SQL
2. Write CTEs with window functions (running totals, rankings, gaps-and-islands)
3. Implement a Pandas UDF for batch prediction
4. Work with nested JSON (arrays of structs), flatten and aggregate
5. Compare explain() plans with and without optimizations disabled
