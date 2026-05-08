# Day 14: Project — End-to-End Spark Data Pipeline

## Learning Objectives
- Build a complete batch + streaming pipeline with Spark
- Implement the medallion architecture (Bronze → Silver → Gold)
- Apply SCD Type 2, data quality checks, and performance optimizations
- Deploy on a local Spark cluster with Docker

---

## 1. Project Overview

### Architecture
```
Sources                    Processing                      Serving
─────────                  ──────────                      ───────
CSV Files ─────┐
               ├──→ Bronze (raw) ──→ Silver (clean) ──→ Gold (aggregated)
Kafka Stream ──┘         ↑                ↑                    ↓
                    Delta Lake       Delta Lake            Dashboard / API
                    (append only)    (MERGE/SCD2)          (read-optimized)
```

### Requirements
- Batch: Ingest CSV sales data → Transform → Load to warehouse
- Streaming: Real-time events from Kafka → Process → Delta Lake
- Quality: Validate at each layer, quarantine bad records
- Performance: Partition, Z-Order, optimize for query patterns

---

## 2. Project Setup

```python
# project structure
# spark-pipeline/
# ├── docker-compose.yml
# ├── Makefile
# ├── src/
# │   ├── __init__.py
# │   ├── config.py
# │   ├── bronze/
# │   │   ├── ingest_batch.py
# │   │   └── ingest_stream.py
# │   ├── silver/
# │   │   ├── transform_orders.py
# │   │   └── transform_customers.py
# │   ├── gold/
# │   │   └── aggregate_metrics.py
# │   └── quality/
# │       └── checks.py
# ├── tests/
# │   └── test_transforms.py
# └── data/
#     └── sample/
```

### Docker Compose

```yaml
version: '3.8'
services:
  spark-master:
    image: bitnami/spark:3.5
    environment:
      - SPARK_MODE=master
    ports:
      - "8080:8080"  # Spark UI
      - "7077:7077"  # Master port
    volumes:
      - ./src:/app/src
      - ./data:/app/data
      - spark-warehouse:/user/hive/warehouse

  spark-worker:
    image: bitnami/spark:3.5
    environment:
      - SPARK_MODE=worker
      - SPARK_MASTER_URL=spark://spark-master:7077
    depends_on:
      - spark-master

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper

  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: analytics
      POSTGRES_USER: pipeline
      POSTGRES_PASSWORD: secure123
    ports:
      - "5432:5432"

volumes:
  spark-warehouse:
```

---

## 3. Configuration

```python
# src/config.py
from dataclasses import dataclass

@dataclass
class SparkConfig:
    app_name: str = "DataPipeline"
    master: str = "spark://spark-master:7077"
    warehouse_dir: str = "/user/hive/warehouse"
    checkpoint_dir: str = "/checkpoints"
    
    # Delta paths
    bronze_path: str = "/lake/bronze"
    silver_path: str = "/lake/silver"
    gold_path: str = "/lake/gold"
    quarantine_path: str = "/lake/quarantine"
    
    # Kafka
    kafka_bootstrap: str = "kafka:9092"
    kafka_topic: str = "events"

def get_spark_session(config: SparkConfig):
    from pyspark.sql import SparkSession
    return (
        SparkSession.builder
        .appName(config.app_name)
        .master(config.master)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", 
                "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.sql.warehouse.dir", config.warehouse_dir)
        .config("spark.sql.adaptive.enabled", "true")
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
        .getOrCreate()
    )
```

---

## 4. Bronze Layer — Raw Ingestion

### Batch Ingestion

```python
# src/bronze/ingest_batch.py
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import *
from datetime import datetime

class BronzeBatchIngestor:
    def __init__(self, spark: SparkSession, config):
        self.spark = spark
        self.config = config
    
    def ingest_orders(self, source_path: str):
        """Ingest raw orders CSV to Bronze Delta table."""
        schema = StructType([
            StructField("order_id", StringType()),
            StructField("customer_id", StringType()),
            StructField("product_id", StringType()),
            StructField("quantity", IntegerType()),
            StructField("unit_price", DoubleType()),
            StructField("order_date", StringType()),
            StructField("status", StringType()),
            StructField("region", StringType()),
        ])
        
        df = (
            self.spark.read
            .schema(schema)
            .option("header", True)
            .option("mode", "PERMISSIVE")  # Keep malformed rows
            .option("columnNameOfCorruptRecord", "_corrupt_record")
            .csv(source_path)
        )
        
        # Add ingestion metadata
        df_with_metadata = df.withColumns({
            "_ingested_at": F.current_timestamp(),
            "_source_file": F.input_file_name(),
            "_batch_id": F.lit(datetime.utcnow().strftime("%Y%m%d_%H%M%S")),
        })
        
        # Write to Bronze (append-only, no transformations)
        df_with_metadata.write \
            .format("delta") \
            .mode("append") \
            .partitionBy("_batch_id") \
            .save(f"{self.config.bronze_path}/orders")
        
        return df_with_metadata.count()
    
    def ingest_customers(self, source_path: str):
        """Ingest customer master data."""
        df = self.spark.read.option("header", True).csv(source_path)
        
        df_with_metadata = df.withColumns({
            "_ingested_at": F.current_timestamp(),
            "_source_file": F.input_file_name(),
        })
        
        df_with_metadata.write \
            .format("delta") \
            .mode("overwrite") \
            .save(f"{self.config.bronze_path}/customers")
```

### Stream Ingestion

```python
# src/bronze/ingest_stream.py
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import *

class BronzeStreamIngestor:
    def __init__(self, spark: SparkSession, config):
        self.spark = spark
        self.config = config
    
    def start_event_stream(self):
        """Ingest real-time events from Kafka to Bronze."""
        event_schema = StructType([
            StructField("event_id", StringType()),
            StructField("user_id", StringType()),
            StructField("event_type", StringType()),
            StructField("page", StringType()),
            StructField("timestamp", StringType()),
            StructField("properties", MapType(StringType(), StringType())),
        ])
        
        kafka_df = (
            self.spark.readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", self.config.kafka_bootstrap)
            .option("subscribe", self.config.kafka_topic)
            .option("startingOffsets", "latest")
            .load()
        )
        
        events = (
            kafka_df
            .select(
                F.col("key").cast("string").alias("kafka_key"),
                F.from_json(F.col("value").cast("string"), event_schema).alias("data"),
                F.col("timestamp").alias("kafka_timestamp"),
                F.col("partition").alias("kafka_partition"),
                F.col("offset").alias("kafka_offset"),
            )
            .select("kafka_key", "data.*", "kafka_timestamp", "kafka_partition", "kafka_offset")
            .withColumn("_ingested_at", F.current_timestamp())
        )
        
        query = (
            events.writeStream
            .format("delta")
            .outputMode("append")
            .option("checkpointLocation", f"{self.config.checkpoint_dir}/bronze_events")
            .trigger(processingTime="30 seconds")
            .start(f"{self.config.bronze_path}/events")
        )
        
        return query
```

---

## 5. Silver Layer — Clean & Transform

```python
# src/silver/transform_orders.py
from pyspark.sql import SparkSession, functions as F
from delta.tables import DeltaTable

class SilverOrdersTransformer:
    def __init__(self, spark: SparkSession, config):
        self.spark = spark
        self.config = config
    
    def transform(self):
        """Transform Bronze orders to Silver (cleaned, typed, deduplicated)."""
        bronze_orders = self.spark.read.format("delta").load(
            f"{self.config.bronze_path}/orders"
        )
        
        # Clean and type
        silver_orders = (
            bronze_orders
            # Remove corrupt records
            .filter(F.col("order_id").isNotNull())
            # Type conversions
            .withColumn("order_date", F.to_date("order_date", "yyyy-MM-dd"))
            .withColumn("quantity", F.col("quantity").cast("integer"))
            .withColumn("unit_price", F.col("unit_price").cast("double"))
            # Business logic
            .withColumn("total_amount", F.col("quantity") * F.col("unit_price"))
            .withColumn("order_year", F.year("order_date"))
            .withColumn("order_month", F.month("order_date"))
            # Standardize
            .withColumn("status", F.upper(F.trim("status")))
            .withColumn("region", F.upper(F.trim("region")))
            # Deduplication
            .dropDuplicates(["order_id"])
            # Add processing metadata
            .withColumn("_processed_at", F.current_timestamp())
            # Select final columns
            .select(
                "order_id", "customer_id", "product_id",
                "quantity", "unit_price", "total_amount",
                "order_date", "order_year", "order_month",
                "status", "region", "_processed_at"
            )
        )
        
        # Quality check before writing
        quality_results = self._validate(silver_orders)
        if quality_results["critical_failures"] > 0:
            raise ValueError(f"Quality check failed: {quality_results}")
        
        # Write Silver (MERGE for idempotency)
        silver_path = f"{self.config.silver_path}/orders"
        if DeltaTable.isDeltaTable(self.spark, silver_path):
            target = DeltaTable.forPath(self.spark, silver_path)
            (
                target.alias("t")
                .merge(silver_orders.alias("s"), "t.order_id = s.order_id")
                .whenMatchedUpdateAll(condition="s._processed_at > t._processed_at")
                .whenNotMatchedInsertAll()
                .execute()
            )
        else:
            silver_orders.write \
                .format("delta") \
                .partitionBy("order_year", "order_month") \
                .save(silver_path)
        
        return silver_orders.count()
    
    def _validate(self, df) -> dict:
        """Data quality checks."""
        total = df.count()
        null_ids = df.filter(F.col("order_id").isNull()).count()
        negative_amounts = df.filter(F.col("total_amount") < 0).count()
        future_dates = df.filter(F.col("order_date") > F.current_date()).count()
        
        return {
            "total_records": total,
            "null_ids": null_ids,
            "negative_amounts": negative_amounts,
            "future_dates": future_dates,
            "critical_failures": null_ids,  # Null IDs are critical
        }
```

### SCD Type 2 for Customers

```python
# src/silver/transform_customers.py
class SilverCustomersTransformer:
    def __init__(self, spark, config):
        self.spark = spark
        self.config = config
    
    def transform_scd2(self):
        """Apply SCD Type 2 for customer dimension."""
        bronze_customers = self.spark.read.format("delta").load(
            f"{self.config.bronze_path}/customers"
        )
        
        silver_path = f"{self.config.silver_path}/customers"
        
        if not DeltaTable.isDeltaTable(self.spark, silver_path):
            # Initial load
            initial = bronze_customers.withColumns({
                "effective_from": F.current_date(),
                "effective_to": F.lit("9999-12-31").cast("date"),
                "is_current": F.lit(True),
            })
            initial.write.format("delta").save(silver_path)
            return
        
        target = DeltaTable.forPath(self.spark, silver_path)
        
        # Find changes
        current_records = target.toDF().filter("is_current = true")
        
        changes = (
            bronze_customers.alias("new")
            .join(current_records.alias("curr"), "customer_id")
            .filter("""
                new.name != curr.name OR 
                new.email != curr.email OR 
                new.address != curr.address
            """)
        )
        
        if changes.count() == 0:
            return
        
        # Expire old + insert new version
        staged = (
            # New current record
            changes.selectExpr(
                "NULL as merge_key",
                "new.customer_id", "new.name", "new.email", "new.address",
                "current_date() as effective_from",
                "cast('9999-12-31' as date) as effective_to",
                "true as is_current"
            )
            .union(
                # Expire existing
                changes.selectExpr(
                    "new.customer_id as merge_key",
                    "curr.customer_id", "curr.name", "curr.email", "curr.address",
                    "curr.effective_from",
                    "date_sub(current_date(), 1) as effective_to",
                    "false as is_current"
                )
            )
        )
        
        (
            target.alias("t")
            .merge(staged.alias("s"), "t.customer_id = s.merge_key AND t.is_current = true")
            .whenMatchedUpdate(set={
                "is_current": "s.is_current",
                "effective_to": "s.effective_to"
            })
            .whenNotMatchedInsertAll()
            .execute()
        )
```

---

## 6. Gold Layer — Business Aggregations

```python
# src/gold/aggregate_metrics.py
class GoldMetricsBuilder:
    def __init__(self, spark, config):
        self.spark = spark
        self.config = config
    
    def build_daily_sales(self):
        """Gold layer: Daily sales metrics."""
        orders = self.spark.read.format("delta").load(f"{self.config.silver_path}/orders")
        customers = self.spark.read.format("delta").load(f"{self.config.silver_path}/customers")
        
        # Join and aggregate
        daily_sales = (
            orders
            .filter(F.col("status") == "COMPLETED")
            .join(
                customers.filter("is_current = true"),
                "customer_id",
                "left"
            )
            .groupBy(
                F.col("order_date").alias("date"),
                "region"
            )
            .agg(
                F.count("order_id").alias("total_orders"),
                F.sum("total_amount").alias("total_revenue"),
                F.avg("total_amount").alias("avg_order_value"),
                F.countDistinct("customer_id").alias("unique_customers"),
                F.sum(F.when(F.col("is_current").isNull(), 1).otherwise(0)).alias("unknown_customers"),
            )
            .withColumn("_computed_at", F.current_timestamp())
        )
        
        # Write Gold (overwrite partitions for recomputation)
        daily_sales.write \
            .format("delta") \
            .mode("overwrite") \
            .option("replaceWhere", f"date >= '{self._get_start_date()}'") \
            .save(f"{self.config.gold_path}/daily_sales")
    
    def build_customer_lifetime(self):
        """Gold: Customer lifetime value metrics."""
        orders = self.spark.read.format("delta").load(f"{self.config.silver_path}/orders")
        
        from pyspark.sql.window import Window
        
        customer_ltv = (
            orders
            .filter(F.col("status") == "COMPLETED")
            .groupBy("customer_id")
            .agg(
                F.sum("total_amount").alias("lifetime_revenue"),
                F.count("order_id").alias("total_orders"),
                F.avg("total_amount").alias("avg_order_value"),
                F.min("order_date").alias("first_order_date"),
                F.max("order_date").alias("last_order_date"),
                F.datediff(F.max("order_date"), F.min("order_date")).alias("customer_tenure_days"),
            )
            .withColumn("segment", 
                F.when(F.col("lifetime_revenue") > 10000, "enterprise")
                .when(F.col("lifetime_revenue") > 1000, "mid-market")
                .otherwise("smb")
            )
        )
        
        customer_ltv.write \
            .format("delta") \
            .mode("overwrite") \
            .save(f"{self.config.gold_path}/customer_ltv")
    
    def _get_start_date(self):
        """Recompute last 7 days."""
        from datetime import datetime, timedelta
        return (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
```

---

## 7. Quality Checks

```python
# src/quality/checks.py
from dataclasses import dataclass
from typing import Callable
from pyspark.sql import DataFrame, functions as F

@dataclass
class QualityCheck:
    name: str
    query: Callable[[DataFrame], int]  # Returns count of failures
    threshold: float  # Max allowed failure rate

class QualityGate:
    def __init__(self, checks: list[QualityCheck]):
        self.checks = checks
    
    def run(self, df: DataFrame) -> dict:
        total = df.count()
        results = {}
        all_passed = True
        
        for check in self.checks:
            failures = check.query(df)
            failure_rate = failures / total if total > 0 else 0
            passed = failure_rate <= check.threshold
            
            results[check.name] = {
                "failures": failures,
                "failure_rate": round(failure_rate, 4),
                "threshold": check.threshold,
                "passed": passed,
            }
            
            if not passed:
                all_passed = False
        
        results["_overall_passed"] = all_passed
        return results

# Usage
gate = QualityGate([
    QualityCheck("no_null_ids", lambda df: df.filter(F.col("order_id").isNull()).count(), 0.0),
    QualityCheck("valid_amounts", lambda df: df.filter(F.col("total_amount") <= 0).count(), 0.01),
    QualityCheck("no_future_dates", lambda df: df.filter(F.col("order_date") > F.current_date()).count(), 0.0),
    QualityCheck("known_regions", lambda df: df.filter(~F.col("region").isin(["US", "EU", "APAC"])).count(), 0.05),
])
```

---

## 8. Testing

```python
# tests/test_transforms.py
import pytest
from pyspark.sql import SparkSession
from src.silver.transform_orders import SilverOrdersTransformer

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[2]").appName("test").getOrCreate()

@pytest.fixture
def sample_orders(spark):
    return spark.createDataFrame([
        ("ORD001", "C1", "P1", 2, 10.0, "2024-01-01", "completed", "us"),
        ("ORD002", "C2", "P2", 1, 50.0, "2024-01-02", "COMPLETED", "EU"),
        ("ORD001", "C1", "P1", 2, 10.0, "2024-01-01", "completed", "us"),  # Duplicate
        (None, "C3", "P3", 1, 20.0, "2024-01-03", "pending", "apac"),  # Null ID
    ], ["order_id", "customer_id", "product_id", "quantity", "unit_price", 
        "order_date", "status", "region"])

class TestSilverOrders:
    def test_deduplication(self, spark, sample_orders):
        # Should remove duplicate ORD001
        result = process_orders(sample_orders)
        assert result.filter(F.col("order_id") == "ORD001").count() == 1
    
    def test_removes_null_ids(self, spark, sample_orders):
        result = process_orders(sample_orders)
        assert result.filter(F.col("order_id").isNull()).count() == 0
    
    def test_standardizes_status(self, spark, sample_orders):
        result = process_orders(sample_orders)
        statuses = [row.status for row in result.select("status").collect()]
        assert all(s == s.upper() for s in statuses)
    
    def test_calculates_total_amount(self, spark, sample_orders):
        result = process_orders(sample_orders)
        ord001 = result.filter(F.col("order_id") == "ORD001").first()
        assert ord001.total_amount == 20.0  # 2 * 10.0
```

---

## Interview Questions

### Beginner
1. **What is the medallion architecture?** Three-layer pattern: Bronze (raw), Silver (cleaned), Gold (aggregated). Each layer adds quality and business value.
2. **Why use Delta Lake over plain Parquet?** ACID transactions, time travel, schema enforcement, MERGE operations, streaming support, OPTIMIZE/VACUUM.

### Intermediate
3. **How do you handle late-arriving data in batch pipelines?** Reprocess affected partitions (overwrite), or use MERGE with "newer wins" logic. Design Silver with update semantics.
4. **Explain idempotent pipeline design.** Same input produces same output regardless of how many times you run it. Use MERGE (upsert) instead of append, partition-level overwrite, deduplication.

### Advanced
5. **Design a pipeline that handles 50TB daily with SLA of 4 hours.** Partition by date/hour, parallel ingestion (multiple Spark jobs per partition), Delta Lake for ACID writes, OPTIMIZE for read performance, Z-ORDER on query columns, Gold layer pre-aggregated for dashboard queries.
6. **How do you test and validate a pipeline before promoting to production?** Unit tests (transform logic), integration tests (with real Delta tables in test env), data quality gates (counts, nulls, distributions), shadow mode (run new pipeline parallel to old, compare outputs), A/B validation.

---

## Deliverables
1. Working Docker Compose environment
2. Bronze ingestion (batch CSV + streaming Kafka)
3. Silver transformation with MERGE and SCD Type 2
4. Gold aggregation layer with business metrics
5. Quality gates at each layer transition
6. Tests covering transform logic
7. Documentation: architecture diagram and README
