# Day 30: Capstone Project — End-to-End Data Platform

## Learning Objectives
- Build a production-grade data platform from scratch
- Integrate all 30 days of learning into one project
- Practice design decisions, tradeoffs, and documentation
- Create a portfolio-worthy project

---

## 1. Project Overview

### Architecture

```
DATA SOURCES                    INGESTION              PROCESSING
─────────────                   ─────────              ──────────
REST API ──────────┐
(e-commerce orders) │
                    ├──→ Kafka ──→ Spark Streaming ──→ Bronze (S3/Delta)
PostgreSQL ────────┤                                        │
(CDC via Debezium)  │                                        ▼
                    │                              Spark Batch + dbt
CSV/Flat Files ────┘                              (transform + model)
(product catalog)                                         │
                                                          ▼
                                                   Silver (cleaned)
                                                          │
                                                          ▼
                                                   Gold (aggregates)
                                                          │
                                    ┌─────────────────────┼──────────────┐
                                    ▼                     ▼              ▼
                              REST API              Dashboard        ML Feature
                              (FastAPI)             (Streamlit)      Store (Redis)

ORCHESTRATION: Airflow
QUALITY: Great Expectations
MONITORING: Prometheus + Grafana
CONTAINERIZED: Docker Compose
```

---

## 2. Project Setup

```bash
# Project structure
capstone-data-platform/
├── docker-compose.yml          # All services
├── Makefile                    # Common commands
├── README.md                   # Documentation
├── .env.example               # Configuration template
│
├── infra/
│   ├── kafka/                 # Kafka + Zookeeper config
│   ├── spark/                 # Spark config
│   └── airflow/               # Airflow config, DAGs
│
├── src/
│   ├── ingestion/
│   │   ├── api_producer.py    # REST API → Kafka
│   │   ├── cdc_connector.py   # Debezium CDC config
│   │   └── file_loader.py     # CSV → S3
│   │
│   ├── processing/
│   │   ├── streaming.py       # Spark Streaming (Kafka → Bronze)
│   │   ├── batch.py           # Spark Batch (Bronze → Silver)
│   │   └── dbt_project/       # dbt models (Silver → Gold)
│   │
│   ├── quality/
│   │   ├── expectations/      # Great Expectations suites
│   │   └── monitors.py        # Custom data quality checks
│   │
│   ├── serving/
│   │   ├── api/               # FastAPI serving layer
│   │   └── dashboard/         # Streamlit dashboard
│   │
│   └── utils/
│       ├── config.py          # Configuration management
│       └── logging_setup.py   # Structured logging
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
└── docs/
    ├── architecture.md
    ├── data-model.md
    └── runbook.md
```

### Docker Compose

```yaml
version: '3.8'
services:
  # --- Infrastructure ---
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on: [zookeeper]
    ports: ["9092:9092"]
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ecommerce
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports: ["5432:5432"]
    volumes:
      - ./infra/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports: ["9000:9000", "9001:9001"]
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}

  # --- Processing ---
  spark-master:
    image: bitnami/spark:3.5
    ports: ["8080:8080", "7077:7077"]
    environment:
      SPARK_MODE: master

  spark-worker:
    image: bitnami/spark:3.5
    depends_on: [spark-master]
    environment:
      SPARK_MODE: worker
      SPARK_MASTER_URL: spark://spark-master:7077

  # --- Orchestration ---
  airflow:
    image: apache/airflow:2.8.0
    depends_on: [postgres]
    ports: ["8081:8080"]
    volumes:
      - ./infra/airflow/dags:/opt/airflow/dags
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://admin:${POSTGRES_PASSWORD}@postgres/airflow
```

---

## 3. Implementation

### Phase 1: Ingestion

```python
# src/ingestion/api_producer.py
"""Simulate e-commerce API events → Kafka."""
import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8'),
)

PRODUCTS = [f"PROD-{i:04d}" for i in range(1, 101)]
REGIONS = ['US-East', 'US-West', 'EU-West', 'APAC']

def generate_order_event() -> dict:
    return {
        "event_id": f"evt-{random.randint(100000, 999999)}",
        "event_type": random.choice(["order_placed", "order_shipped", "order_delivered"]),
        "order_id": f"ORD-{random.randint(10000, 99999)}",
        "customer_id": f"CUST-{random.randint(1, 10000)}",
        "product_id": random.choice(PRODUCTS),
        "quantity": random.randint(1, 5),
        "amount": round(random.uniform(9.99, 499.99), 2),
        "region": random.choice(REGIONS),
        "timestamp": datetime.utcnow().isoformat(),
    }

def run_producer(events_per_second: int = 10):
    """Produce events to Kafka at specified rate."""
    print(f"Producing {events_per_second} events/sec to 'orders' topic...")
    while True:
        event = generate_order_event()
        producer.send(
            topic='orders',
            key=event['customer_id'],
            value=event,
        )
        time.sleep(1.0 / events_per_second)

if __name__ == '__main__':
    run_producer()
```

### Phase 2: Stream Processing (Kafka → Bronze)

```python
# src/processing/streaming.py
"""Spark Structured Streaming: Kafka → Delta Lake Bronze."""
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

spark = SparkSession.builder \
    .appName("OrdersStreaming") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .getOrCreate()

schema = StructType([
    StructField("event_id", StringType()),
    StructField("event_type", StringType()),
    StructField("order_id", StringType()),
    StructField("customer_id", StringType()),
    StructField("product_id", StringType()),
    StructField("quantity", IntegerType()),
    StructField("amount", DoubleType()),
    StructField("region", StringType()),
    StructField("timestamp", StringType()),
])

# Read from Kafka
raw_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:29092")
    .option("subscribe", "orders")
    .option("startingOffsets", "earliest")
    .load()
)

# Parse and add metadata
bronze_stream = (
    raw_stream
    .select(
        F.from_json(F.col("value").cast("string"), schema).alias("data"),
        F.col("topic"),
        F.col("partition"),
        F.col("offset"),
        F.col("timestamp").alias("kafka_timestamp"),
    )
    .select(
        "data.*",
        "topic",
        "partition",
        "offset",
        "kafka_timestamp",
        F.current_timestamp().alias("ingested_at"),
    )
)

# Write to Delta Lake Bronze
query = (
    bronze_stream.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "s3a://lakehouse/checkpoints/orders_bronze")
    .partitionBy("region")
    .start("s3a://lakehouse/bronze/orders")
)

query.awaitTermination()
```

### Phase 3: Batch Processing (Bronze → Silver → Gold)

```python
# src/processing/batch.py
"""Spark Batch: Bronze → Silver (clean) → Gold (aggregates)."""
from pyspark.sql import SparkSession, functions as F

spark = SparkSession.builder.appName("OrdersBatch").getOrCreate()

# --- Bronze → Silver ---
def bronze_to_silver():
    """Clean, deduplicate, validate."""
    bronze = spark.read.format("delta").load("s3a://lakehouse/bronze/orders")
    
    silver = (
        bronze
        # Deduplicate
        .dropDuplicates(["event_id"])
        # Cast types
        .withColumn("event_timestamp", F.to_timestamp("timestamp"))
        .withColumn("event_date", F.to_date("event_timestamp"))
        # Validate
        .filter(F.col("amount") > 0)
        .filter(F.col("quantity") > 0)
        .filter(F.col("customer_id").isNotNull())
        # Add derived columns
        .withColumn("total_amount", F.col("amount") * F.col("quantity"))
        # Drop raw columns
        .drop("timestamp", "topic", "partition", "offset")
    )
    
    silver.write.format("delta") \
        .mode("overwrite") \
        .partitionBy("event_date", "region") \
        .save("s3a://lakehouse/silver/orders")

# --- Silver → Gold ---
def silver_to_gold():
    """Business aggregates."""
    silver = spark.read.format("delta").load("s3a://lakehouse/silver/orders")
    
    # Daily revenue by region
    daily_revenue = (
        silver
        .filter(F.col("event_type") == "order_placed")
        .groupBy("event_date", "region")
        .agg(
            F.count("order_id").alias("total_orders"),
            F.sum("total_amount").alias("total_revenue"),
            F.avg("total_amount").alias("avg_order_value"),
            F.countDistinct("customer_id").alias("unique_customers"),
        )
    )
    
    daily_revenue.write.format("delta") \
        .mode("overwrite") \
        .save("s3a://lakehouse/gold/daily_revenue")
    
    # Top products
    top_products = (
        silver
        .filter(F.col("event_type") == "order_placed")
        .groupBy("product_id")
        .agg(
            F.sum("quantity").alias("total_sold"),
            F.sum("total_amount").alias("total_revenue"),
            F.countDistinct("customer_id").alias("unique_buyers"),
        )
        .orderBy(F.desc("total_revenue"))
    )
    
    top_products.write.format("delta") \
        .mode("overwrite") \
        .save("s3a://lakehouse/gold/top_products")

if __name__ == '__main__':
    bronze_to_silver()
    silver_to_gold()
```

### Phase 4: dbt Models

```sql
-- src/processing/dbt_project/models/gold/customer_lifetime_value.sql
{{ config(materialized='table', partition_by='signup_month') }}

WITH customer_orders AS (
    SELECT
        customer_id,
        MIN(event_date) AS first_order_date,
        MAX(event_date) AS last_order_date,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(total_amount) AS total_spent,
        AVG(total_amount) AS avg_order_value,
        DATEDIFF(MAX(event_date), MIN(event_date)) AS customer_lifespan_days
    FROM {{ ref('silver_orders') }}
    WHERE event_type = 'order_placed'
    GROUP BY customer_id
)

SELECT
    customer_id,
    first_order_date,
    last_order_date,
    total_orders,
    total_spent,
    avg_order_value,
    customer_lifespan_days,
    DATE_TRUNC('month', first_order_date) AS signup_month,
    -- CLV segments
    CASE
        WHEN total_spent > 1000 AND total_orders > 10 THEN 'VIP'
        WHEN total_spent > 500 OR total_orders > 5 THEN 'Regular'
        WHEN total_orders = 1 THEN 'One-time'
        ELSE 'Casual'
    END AS customer_segment
FROM customer_orders
```

### Phase 5: Data Quality

```python
# src/quality/monitors.py
"""Data quality checks using Great Expectations patterns."""
from dataclasses import dataclass

@dataclass
class QualityCheck:
    name: str
    passed: bool
    details: str

def run_quality_checks(spark, table_path: str) -> list[QualityCheck]:
    """Run quality checks on a Delta table."""
    df = spark.read.format("delta").load(table_path)
    results = []
    
    # 1. Row count check
    count = df.count()
    results.append(QualityCheck(
        name="row_count",
        passed=count > 0,
        details=f"Row count: {count}",
    ))
    
    # 2. Null checks
    for col in ['event_id', 'customer_id', 'amount']:
        null_count = df.filter(F.col(col).isNull()).count()
        results.append(QualityCheck(
            name=f"null_check_{col}",
            passed=null_count == 0,
            details=f"{col}: {null_count} nulls",
        ))
    
    # 3. Freshness check
    max_timestamp = df.agg(F.max("ingested_at")).collect()[0][0]
    from datetime import datetime, timedelta
    is_fresh = (datetime.utcnow() - max_timestamp) < timedelta(hours=2)
    results.append(QualityCheck(
        name="freshness",
        passed=is_fresh,
        details=f"Latest record: {max_timestamp}",
    ))
    
    # 4. Uniqueness check
    total = df.count()
    unique = df.select("event_id").distinct().count()
    results.append(QualityCheck(
        name="uniqueness_event_id",
        passed=total == unique,
        details=f"Total: {total}, Unique: {unique}, Dupes: {total - unique}",
    ))
    
    return results
```

### Phase 6: Serving Layer

```python
# src/serving/api/main.py
"""FastAPI serving layer for Gold data."""
from fastapi import FastAPI, Query
from datetime import date

app = FastAPI(title="E-Commerce Analytics API")

@app.get("/metrics/daily-revenue")
async def get_daily_revenue(
    start_date: date = Query(...),
    end_date: date = Query(...),
    region: str = Query(None),
):
    """Get daily revenue metrics."""
    # In production: query from Delta Lake or pre-cached in Redis
    query = f"""
        SELECT * FROM gold.daily_revenue
        WHERE event_date BETWEEN '{start_date}' AND '{end_date}'
    """
    if region:
        query += f" AND region = '{region}'"
    
    # Execute and return
    results = execute_query(query)
    return {"data": results, "count": len(results)}

@app.get("/metrics/top-products")
async def get_top_products(limit: int = Query(10, le=100)):
    """Get top products by revenue."""
    results = execute_query(f"""
        SELECT * FROM gold.top_products
        ORDER BY total_revenue DESC
        LIMIT {limit}
    """)
    return {"data": results}

@app.get("/health")
async def health_check():
    """Pipeline health status."""
    return {
        "status": "healthy",
        "last_batch_run": get_last_batch_timestamp(),
        "streaming_lag": get_kafka_consumer_lag(),
    }
```

### Phase 7: Airflow DAG

```python
# infra/airflow/dags/daily_pipeline.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-engineering',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
}

with DAG(
    'daily_ecommerce_pipeline',
    default_args=default_args,
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['ecommerce', 'production'],
) as dag:
    
    bronze_to_silver = SparkSubmitOperator(
        task_id='bronze_to_silver',
        application='/opt/spark/jobs/batch.py',
        name='bronze_to_silver',
        conf={'spark.sql.shuffle.partitions': '200'},
    )
    
    quality_check = PythonOperator(
        task_id='quality_check_silver',
        python_callable=run_silver_quality_checks,
    )
    
    silver_to_gold = SparkSubmitOperator(
        task_id='silver_to_gold',
        application='/opt/spark/jobs/batch.py',
        name='silver_to_gold',
    )
    
    quality_check_gold = PythonOperator(
        task_id='quality_check_gold',
        python_callable=run_gold_quality_checks,
    )
    
    refresh_cache = PythonOperator(
        task_id='refresh_redis_cache',
        python_callable=refresh_serving_cache,
    )
    
    # DAG dependencies
    bronze_to_silver >> quality_check >> silver_to_gold >> quality_check_gold >> refresh_cache
```

---

## 4. Testing Strategy

```python
# tests/unit/test_transforms.py
import pytest
from pyspark.sql import SparkSession
from src.processing.batch import bronze_to_silver

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[*]").getOrCreate()

def test_deduplication(spark):
    """Duplicate events should be removed."""
    data = [
        ("evt-1", "order_placed", "ORD-1", 100.0),
        ("evt-1", "order_placed", "ORD-1", 100.0),  # Duplicate
        ("evt-2", "order_placed", "ORD-2", 200.0),
    ]
    df = spark.createDataFrame(data, ["event_id", "event_type", "order_id", "amount"])
    result = df.dropDuplicates(["event_id"])
    assert result.count() == 2

def test_negative_amounts_filtered(spark):
    """Negative amounts should be filtered out."""
    data = [
        ("evt-1", 100.0),
        ("evt-2", -50.0),   # Should be removed
        ("evt-3", 0.0),     # Should be removed (amount > 0)
    ]
    df = spark.createDataFrame(data, ["event_id", "amount"])
    result = df.filter(df.amount > 0)
    assert result.count() == 1

def test_total_amount_calculation(spark):
    """Total amount = price × quantity."""
    from pyspark.sql import functions as F
    data = [("evt-1", 25.0, 3)]
    df = spark.createDataFrame(data, ["event_id", "amount", "quantity"])
    result = df.withColumn("total", F.col("amount") * F.col("quantity"))
    assert result.collect()[0]["total"] == 75.0
```

---

## 5. Documentation

```markdown
# README.md

## E-Commerce Data Platform

End-to-end data platform processing e-commerce events through 
streaming and batch pipelines into analytics-ready datasets.

### Architecture Decision Records

| Decision | Choice | Reason |
|----------|--------|--------|
| Message Broker | Kafka | Durability, replay, high throughput |
| Processing | Spark | Unified batch + stream, Delta Lake |
| Storage | Delta Lake on S3 | ACID, time travel, schema evolution |
| Orchestration | Airflow | Industry standard, DAG visualization |
| Serving | FastAPI + Redis | Low latency, caching |

### Running Locally

```bash
# Start all services
docker-compose up -d

# Initialize (create topics, tables)
make init

# Start streaming pipeline
make stream

# Run batch pipeline
make batch

# Run quality checks
make quality

# Access services
# Airflow: http://localhost:8081
# Spark UI: http://localhost:8080
# API: http://localhost:8000/docs
# MinIO: http://localhost:9001
```

### Data Flow
1. API Producer generates events → Kafka `orders` topic
2. Spark Streaming consumes → writes to Bronze (Delta Lake)
3. Daily batch: Bronze → Silver (clean, dedupe) → Gold (aggregates)
4. Data quality gates between each layer
5. Gold data served via FastAPI + Redis cache
6. Airflow orchestrates daily batch + quality + cache refresh
```

---

## 6. Extension Ideas

```
Level Up Your Capstone:
────────────────────────

1. ADD CDC: Connect Debezium to PostgreSQL, capture changes
2. ADD ML: Train a simple model on Gold data, serve predictions
3. ADD MONITORING: Prometheus metrics + Grafana dashboard
4. ADD SCHEMA REGISTRY: Confluent Schema Registry for Avro
5. ADD GOVERNANCE: Data catalog (DataHub/OpenMetadata)
6. ADD CI/CD: GitHub Actions to test and deploy
7. ADD ALERTING: PagerDuty/Slack alerts for SLA breaches
8. DEPLOY TO CLOUD: Terraform for AWS (EMR, Glue, Redshift)
```

---

## Interview Questions

### Beginner
1. **Walk me through your capstone project.** "I built an end-to-end data platform: API events → Kafka → Spark Streaming → Delta Lake → Spark Batch → dbt → FastAPI. Used Airflow for orchestration, Great Expectations for quality. Containerized with Docker Compose."
2. **Why did you choose these technologies?** Kafka: durable, replayable. Spark: handles both batch and stream. Delta Lake: ACID on S3. Airflow: standard orchestration. These represent the modern data stack and are widely used in industry.
3. **What would you change for production?** Managed services (MSK not self-hosted Kafka), auto-scaling (EMR/Databricks), proper auth/secrets management, monitoring/alerting, CI/CD, infrastructure-as-code.

### Intermediate
4. **How does your pipeline handle failures?** Kafka provides durability (replicated). Spark checkpointing for streaming recovery. Airflow retries with exponential backoff. Delta Lake transactions (partial write = rollback). Quality gates prevent bad data propagation.
5. **How would you scale this to 100x the current volume?** Increase Kafka partitions, add Spark workers, larger executor memory, optimize partitioning/file sizes, add caching layer, consider separate clusters for batch vs streaming.
6. **Explain your data quality strategy.** Three layers: schema validation at ingestion, statistical checks at Bronze→Silver (nulls, ranges, freshness), business rule validation at Silver→Gold (referential integrity, aggregate consistency). Alerts on failures.

### Advanced
7. **Design the monitoring for this platform.** Pipeline metrics: Kafka lag, processing latency, record counts per stage. Data metrics: freshness, completeness, schema drift. Infrastructure: CPU, memory, disk. Dashboards: Grafana. Alerts: tiered (P1/P2/P3).
8. **How would you implement exactly-once end-to-end?** Kafka idempotent producer. Spark Streaming with checkpointing + Delta Lake (transactional writes). For batch: idempotent operations (MERGE with unique keys). API writes: deduplication by event_id.
9. **If you had 3 more months, what would you add?** Data catalog for discoverability, column-level lineage, cost allocation per team, self-service query layer, A/B testing framework, real-time anomaly detection, multi-region for DR.

---

## Hands-On Exercise
1. Build the complete capstone project (docker-compose up → working platform)
2. Generate 1M events, validate pipeline handles volume
3. Simulate failures (kill Kafka, crash Spark) → verify recovery
4. Add one extension (CDC, monitoring, or ML)
5. Write a 2-page architecture document explaining your decisions
6. Present your project in 10 minutes (practice for interviews)

---

## Congratulations! 🎉

You've completed the 30-Day Data Engineering curriculum. You now have:
- **Foundations**: SQL, Python, data modeling, ETL patterns
- **Spark**: Batch processing, streaming, optimization
- **Orchestration**: Airflow DAGs, scheduling, monitoring
- **Streaming**: Kafka, CDC, real-time architectures
- **Cloud**: AWS/GCP services, Delta Lake, dbt
- **Quality**: Testing, validation, monitoring
- **System Design**: Framework for interview questions
- **Portfolio**: A capstone project demonstrating all skills

Next steps: Deploy to cloud, contribute to open-source data tools, practice system design interviews.
