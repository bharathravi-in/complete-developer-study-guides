# Day 13: Delta Lake & Lakehouse Architecture

## Learning Objectives
- Understand Delta Lake ACID transactions on data lakes
- Implement time travel, schema evolution, and MERGE operations
- Build Bronze-Silver-Gold lakehouse layers
- Compare Delta Lake vs Iceberg vs Hudi

---

## 1. Delta Lake Fundamentals

### What is Delta Lake?
- Open-source storage layer on top of data lake (S3, ADLS, GCS)
- ACID transactions on Parquet files
- Schema enforcement and evolution
- Time travel (versioning)
- Unified batch + streaming

### Beginner: Basic Operations

```python
from pyspark.sql import SparkSession, functions as F
from delta import *

spark = (
    SparkSession.builder
    .appName("DeltaLake")
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    .getOrCreate()
)

# Write Delta table
df = spark.read.parquet("data/sales/")
df.write.format("delta").mode("overwrite").save("/lake/bronze/sales")

# Read Delta table
sales = spark.read.format("delta").load("/lake/bronze/sales")

# Or use table name
df.write.format("delta").saveAsTable("bronze.sales")
sales = spark.table("bronze.sales")

# Append data
new_data.write.format("delta").mode("append").save("/lake/bronze/sales")
```

---

## 2. Time Travel

```python
from delta.tables import DeltaTable

# Read specific version
df_v0 = spark.read.format("delta").option("versionAsOf", 0).load("/lake/bronze/sales")
df_v5 = spark.read.format("delta").option("versionAsOf", 5).load("/lake/bronze/sales")

# Read at specific timestamp
df_yesterday = (
    spark.read.format("delta")
    .option("timestampAsOf", "2024-01-15 10:00:00")
    .load("/lake/bronze/sales")
)

# View history
delta_table = DeltaTable.forPath(spark, "/lake/bronze/sales")
delta_table.history().show(truncate=False)
# Shows: version, timestamp, operation, operationParameters, userName

# Restore to previous version
delta_table.restoreToVersion(3)
# or
delta_table.restoreToTimestamp("2024-01-15")

# SQL syntax
spark.sql("SELECT * FROM delta.`/lake/bronze/sales` VERSION AS OF 5")
spark.sql("DESCRIBE HISTORY delta.`/lake/bronze/sales`")
```

---

## 3. MERGE (Upserts)

### Basic Upsert

```python
from delta.tables import DeltaTable

# Target: existing table
target = DeltaTable.forPath(spark, "/lake/silver/customers")

# Source: new/updated records
source = spark.read.parquet("data/customer_updates/")

# MERGE: Update existing, insert new
(
    target.alias("t")
    .merge(source.alias("s"), "t.customer_id = s.customer_id")
    .whenMatchedUpdate(set={
        "name": "s.name",
        "email": "s.email",
        "updated_at": "s.updated_at",
    })
    .whenNotMatchedInsertAll()
    .execute()
)
```

### Advanced: SCD Type 2 (Slowly Changing Dimensions)

```python
# SCD Type 2: Keep full history with effective dates
target = DeltaTable.forPath(spark, "/lake/silver/customers_scd2")
updates = spark.read.parquet("data/customer_changes/")

# Step 1: Find changed records
changes = (
    updates.alias("u")
    .join(target.toDF().alias("t"), "customer_id")
    .filter("t.is_current = true AND (t.name != u.name OR t.email != u.email)")
)

# Step 2: Expire old records and insert new versions
staged_updates = (
    changes.selectExpr(
        "NULL as merge_key",  # Force insert (no match)
        "u.customer_id", "u.name", "u.email",
        "u.effective_date", "NULL as end_date", "true as is_current"
    )
    .union(
        changes.selectExpr(
            "u.customer_id as merge_key",  # Match existing
            "u.customer_id", "t.name", "t.email",
            "t.effective_date", "u.effective_date as end_date", "false as is_current"
        )
    )
)

(
    target.alias("t")
    .merge(staged_updates.alias("s"), "t.customer_id = s.merge_key AND t.is_current = true")
    .whenMatchedUpdate(set={
        "is_current": "false",
        "end_date": "s.end_date"
    })
    .whenNotMatchedInsertAll()
    .execute()
)
```

### Conditional MERGE

```python
# Complex merge with conditions
(
    target.alias("t")
    .merge(source.alias("s"), "t.id = s.id")
    .whenMatchedUpdate(
        condition="s.updated_at > t.updated_at",  # Only if newer
        set={"name": "s.name", "amount": "s.amount", "updated_at": "s.updated_at"}
    )
    .whenMatchedDelete(condition="s.is_deleted = true")  # Soft delete
    .whenNotMatchedInsert(
        condition="s.is_deleted = false",  # Don't insert deleted
        values={"id": "s.id", "name": "s.name", "amount": "s.amount"}
    )
    .execute()
)
```

---

## 4. Schema Evolution

```python
# Schema enforcement (default): rejects writes with different schema
# This will FAIL:
new_data_with_extra_col.write.format("delta").mode("append").save("/lake/table")

# Enable schema evolution: adds new columns
new_data_with_extra_col.write \
    .format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("/lake/table")

# Overwrite schema entirely
different_schema_data.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .save("/lake/table")

# Add column with ALTER TABLE
spark.sql("ALTER TABLE bronze.events ADD COLUMNS (new_col STRING AFTER existing_col)")

# Change column type (must be compatible)
spark.sql("ALTER TABLE bronze.events CHANGE COLUMN amount amount DOUBLE")
```

---

## 5. OPTIMIZE & Z-ORDER

```python
# Problem: Many small files from streaming or frequent appends
# Solution: OPTIMIZE compacts small files into larger ones

# Compact files (target ~1GB per file)
delta_table = DeltaTable.forPath(spark, "/lake/silver/events")
delta_table.optimize().executeCompaction()

# Z-ORDER: Co-locate related data for faster queries
# Puts records with same values close together in files
delta_table.optimize().executeZOrderBy("customer_id", "date")

# SQL syntax
spark.sql("OPTIMIZE silver.events ZORDER BY (customer_id, date)")

# When to Z-ORDER:
# - Columns frequently used in WHERE clauses
# - Columns used in JOIN conditions
# - High cardinality columns (customer_id, not gender)
# - Maximum 3-4 columns (effectiveness decreases)

# Auto-optimize (for streaming tables)
spark.sql("""
    ALTER TABLE silver.events 
    SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
""")
```

---

## 6. Change Data Feed (CDC)

```python
# Enable Change Data Feed on table
spark.sql("""
    ALTER TABLE silver.customers 
    SET TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true')
""")

# Read changes between versions
changes = (
    spark.read.format("delta")
    .option("readChangeFeed", "true")
    .option("startingVersion", 5)
    .option("endingVersion", 10)
    .table("silver.customers")
)

# Change types: insert, update_preimage, update_postimage, delete
changes.select("customer_id", "_change_type", "_commit_version", "_commit_timestamp").show()

# Stream changes (CDC pipeline)
cdc_stream = (
    spark.readStream.format("delta")
    .option("readChangeFeed", "true")
    .option("startingVersion", "latest")
    .table("silver.customers")
)

# Process CDC events
def handle_cdc(batch_df, batch_id):
    inserts = batch_df.filter("_change_type = 'insert'")
    updates = batch_df.filter("_change_type = 'update_postimage'")
    deletes = batch_df.filter("_change_type = 'delete'")
    # Apply to downstream systems...

cdc_stream.writeStream.foreachBatch(handle_cdc).start()
```

---

## 7. VACUUM (Cleanup Old Versions)

```python
# Remove old files no longer referenced by any version
# Default retention: 7 days (don't go below this in production)

delta_table = DeltaTable.forPath(spark, "/lake/silver/events")
delta_table.vacuum(168)  # Keep files for 168 hours (7 days)

# SQL
spark.sql("VACUUM silver.events RETAIN 168 HOURS")

# WARNING: After VACUUM, time travel before retention period is impossible
# Set retention based on your recovery requirements

# Check what would be deleted (dry run)
delta_table.vacuum(168, retentionCheckEnabled=False)  # Dangerous: allows < 7 days
```

---

## 8. Lakehouse Architecture Layers

```python
# BRONZE: Raw ingestion (schema-on-read, all data, no transformation)
raw_events = spark.readStream.format("kafka").load()
raw_events.writeStream.format("delta").save("/lake/bronze/events")

# SILVER: Cleaned, validated, typed (business entities)
bronze = spark.readStream.format("delta").load("/lake/bronze/events")
silver = (
    bronze
    .select(F.from_json("value", schema).alias("data"))
    .select("data.*")
    .filter(F.col("event_id").isNotNull())
    .dropDuplicates(["event_id"])
    .withColumn("processed_at", F.current_timestamp())
)
silver.writeStream.format("delta").save("/lake/silver/events")

# GOLD: Aggregated, business-ready (dimensions, facts, metrics)
silver_events = spark.read.format("delta").load("/lake/silver/events")
gold_daily_metrics = (
    silver_events
    .groupBy(F.to_date("event_time").alias("date"), "region")
    .agg(
        F.count("*").alias("total_events"),
        F.countDistinct("user_id").alias("unique_users"),
        F.sum("revenue").alias("total_revenue"),
    )
)
gold_daily_metrics.write.format("delta").mode("overwrite").save("/lake/gold/daily_metrics")
```

---

## 9. Delta Lake vs Iceberg vs Hudi

| Feature | Delta Lake | Apache Iceberg | Apache Hudi |
|---------|-----------|----------------|-------------|
| **Backed by** | Databricks | Apple/Netflix | Uber |
| **ACID** | ✅ | ✅ | ✅ |
| **Time Travel** | ✅ | ✅ | Limited |
| **Schema Evolution** | ✅ | ✅ (best) | ✅ |
| **Partition Evolution** | ❌ (must rewrite) | ✅ (hidden partitioning) | ❌ |
| **Ecosystem** | Spark-centric | Multi-engine (Spark, Trino, Flink) | Spark, Flink |
| **MERGE performance** | Good | Good | Best (MOR tables) |
| **Streaming** | Best (native Spark) | Good | Good |
| **Governance** | Unity Catalog | Nessie/Polaris | Limited |
| **Best for** | Databricks shops | Multi-engine, Trino | Uber-style CDC |

---

## Interview Questions

### Beginner
1. **What is Delta Lake?** Open-source storage layer adding ACID transactions, time travel, and schema enforcement to data lake files (Parquet). Enables reliable data lakes.
2. **What's the difference between Delta Lake and Parquet?** Parquet is a file format. Delta Lake adds transaction log (_delta_log), enabling versioning, ACID, rollback, and schema enforcement on top of Parquet files.
3. **What are Bronze, Silver, and Gold layers?** Medallion architecture: Bronze = raw data as-is, Silver = cleaned/deduplicated/typed, Gold = aggregated/business-ready for consumption.

### Intermediate
4. **How does MERGE work in Delta Lake?** Matches source and target rows on a condition. For matches: update or delete. For non-matches: insert. All in a single atomic transaction.
5. **Explain Z-ORDER and when to use it.** Z-ordering co-locates data with similar column values in the same files. Enables data skipping (file-level min/max stats). Use on columns in WHERE clauses. Best for 2-3 high-cardinality columns.
6. **What's the purpose of VACUUM?** Removes old Parquet files no longer referenced by the transaction log. Reclaims storage. After VACUUM, time travel to versions before retention is impossible.

### Advanced
7. **How do you implement CDC from OLTP to lakehouse?** Source: Debezium captures WAL changes → Kafka → Spark Streaming reads → Delta Lake MERGE (insert new, update changed, mark deleted). Use Change Data Feed for downstream propagation.
8. **Design a schema evolution strategy for a production Delta Lake.** Additive changes (new columns) use mergeSchema. Breaking changes: create new table version, backfill, validate, switch consumers. Never drop columns without deprecation period. Track schema versions in metadata.
9. **Compare Delta Lake vs Iceberg for a multi-engine environment.** Iceberg wins: hidden partitioning (no partition by errors), partition evolution, multi-engine (Trino, Flink, Spark). Delta wins: Spark integration, streaming, Databricks ecosystem, simpler to start.

---

## Hands-On Exercise
1. Create a Delta table, perform inserts, updates, deletes
2. Use time travel to query previous versions
3. Implement MERGE for upserts (update if exists, insert if new)
4. Build SCD Type 2 with MERGE
5. Enable Change Data Feed, read changes downstream
6. OPTIMIZE with Z-ORDER, measure query performance improvement
7. Build a Bronze → Silver → Gold pipeline with quality checks at each layer
