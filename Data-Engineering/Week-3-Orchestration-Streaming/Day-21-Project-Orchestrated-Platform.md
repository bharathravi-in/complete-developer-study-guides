# Day 21: Project — Orchestrated Data Platform

## Learning Objectives
- Build a complete orchestrated data platform
- Integrate Kafka, Airflow, dbt, and a data warehouse
- Implement end-to-end monitoring and alerting
- Practice production deployment patterns

---

## 1. Architecture

```
┌──────────────┐    ┌───────────┐    ┌──────────┐    ┌────────────┐
│ PostgreSQL   │───→│  Debezium │───→│  Kafka   │───→│ Spark      │
│ (OLTP)       │    │  (CDC)    │    │          │    │ Streaming  │
└──────────────┘    └───────────┘    └──────────┘    └─────┬──────┘
                                                           │
┌──────────────┐    ┌───────────┐                          ▼
│ REST APIs    │───→│  Airflow  │───→ Bronze (Delta Lake)
│ (Batch)      │    │  (Batch)  │         │
└──────────────┘    └───────────┘         ▼
                                    ┌───────────┐    ┌────────────┐
┌──────────────┐                    │    dbt    │───→│   Gold     │
│ CSV Files    │───→ Airflow ──────→│ (Transforms)   │ (Warehouse)│
│ (Upload)     │                    └───────────┘    └─────┬──────┘
└──────────────┘                                           │
                                                           ▼
                                                    ┌────────────┐
                                                    │ Dashboard  │
                                                    │ + API      │
                                                    └────────────┘
```

---

## 2. Infrastructure (Docker Compose)

```yaml
version: '3.8'

services:
  # Source database
  source-postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: ecommerce
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${SOURCE_DB_PASS}
    ports:
      - "5433:5432"
    volumes:
      - ./init/source-schema.sql:/docker-entrypoint-initdb.d/01-schema.sql
      - ./init/source-data.sql:/docker-entrypoint-initdb.d/02-data.sql
    command: >
      postgres -c wal_level=logical
               -c max_replication_slots=4
               -c max_wal_senders=4

  # Warehouse
  warehouse-postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: warehouse
      POSTGRES_USER: analyst
      POSTGRES_PASSWORD: ${WAREHOUSE_DB_PASS}
    ports:
      - "5434:5432"

  # Kafka + Zookeeper
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on: [zookeeper]
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  # Schema Registry
  schema-registry:
    image: confluentinc/cp-schema-registry:7.5.0
    depends_on: [kafka]
    ports:
      - "8081:8081"
    environment:
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka:29092

  # Kafka Connect (Debezium)
  kafka-connect:
    image: debezium/connect:2.4
    depends_on: [kafka, source-postgres]
    ports:
      - "8083:8083"
    environment:
      BOOTSTRAP_SERVERS: kafka:29092
      GROUP_ID: connect-cluster
      CONFIG_STORAGE_TOPIC: connect-configs
      OFFSET_STORAGE_TOPIC: connect-offsets
      STATUS_STORAGE_TOPIC: connect-status

  # Airflow
  airflow:
    image: apache/airflow:2.8.0-python3.11
    depends_on: [warehouse-postgres, kafka]
    ports:
      - "8080:8080"
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/plugins:/opt/airflow/plugins
      - ./dbt_project:/opt/airflow/dbt
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@warehouse-postgres/airflow

  # MinIO (S3-compatible data lake)
  minio:
    image: minio/minio
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: ${MINIO_PASS}
    command: server /data --console-address ":9001"

volumes:
  source-pgdata:
  warehouse-pgdata:
  minio-data:
```

---

## 3. Airflow DAGs

### Master Orchestration DAG

```python
# airflow/dags/master_pipeline.py
from airflow.decorators import dag, task, task_group
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

@dag(
    schedule="0 */2 * * *",  # Every 2 hours
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["master", "production"],
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
)
def master_pipeline():
    """Master orchestration: Extract → Load → Transform → Quality → Serve."""
    
    @task_group(group_id="extract")
    def extract_sources():
        @task()
        def extract_api_orders():
            """Pull orders from REST API."""
            import requests
            import pandas as pd
            
            response = requests.get(
                "http://api-service/orders",
                params={"since": "{{ prev_execution_date }}"},
                timeout=60,
            )
            response.raise_for_status()
            
            df = pd.DataFrame(response.json()["orders"])
            df.to_parquet("/data/bronze/api_orders/{{ ds }}.parquet")
            return len(df)
        
        @task()
        def extract_csv_uploads():
            """Process uploaded CSV files."""
            import glob
            import pandas as pd
            
            files = glob.glob("/data/incoming/*.csv")
            total = 0
            for f in files:
                df = pd.read_csv(f)
                df.to_parquet(f"/data/bronze/uploads/{f.stem}_{{{{ ds }}}}.parquet")
                total += len(df)
            return total
        
        return extract_api_orders(), extract_csv_uploads()
    
    @task_group(group_id="transform")
    def run_dbt():
        """Run dbt transformations."""
        
        dbt_deps = BashOperator(
            task_id="dbt_deps",
            bash_command="cd /opt/airflow/dbt && dbt deps",
        )
        
        dbt_run = BashOperator(
            task_id="dbt_run",
            bash_command="cd /opt/airflow/dbt && dbt run --select tag:hourly",
        )
        
        dbt_test = BashOperator(
            task_id="dbt_test",
            bash_command="cd /opt/airflow/dbt && dbt test --select tag:hourly",
        )
        
        dbt_deps >> dbt_run >> dbt_test
    
    @task_group(group_id="quality")
    def quality_checks():
        @task()
        def check_row_counts():
            """Verify expected row counts."""
            from sqlalchemy import create_engine, text
            engine = create_engine("postgresql://analyst:pass@warehouse:5432/warehouse")
            with engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT COUNT(*) FROM marts.fct_orders WHERE order_date = :date"
                ), {"date": "{{ ds }}"})
                count = result.scalar()
                if count < 100:  # Minimum expected
                    raise ValueError(f"Only {count} orders for {{ ds }}")
        
        @task()
        def check_freshness():
            """Verify data freshness."""
            from sqlalchemy import create_engine, text
            engine = create_engine("postgresql://analyst:pass@warehouse:5432/warehouse")
            with engine.connect() as conn:
                result = conn.execute(text(
                    "SELECT MAX(order_date) FROM marts.fct_orders"
                ))
                max_date = result.scalar()
                # Alert if data is more than 1 day stale
        
        check_row_counts()
        check_freshness()
    
    @task()
    def notify_completion():
        """Send completion notification."""
        # Slack/email notification
        pass
    
    # DAG flow
    extract_sources() >> run_dbt() >> quality_checks() >> notify_completion()

master_pipeline()
```

---

## 4. dbt Transformation Layer

```sql
-- dbt_project/models/staging/stg_orders.sql
WITH raw_orders AS (
    SELECT * FROM {{ source('bronze', 'orders') }}
)

SELECT
    order_id,
    customer_id,
    product_id,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(amount AS DECIMAL(12,2)) AS amount,
    CAST(order_date AS DATE) AS order_date,
    UPPER(TRIM(status)) AS status,
    UPPER(TRIM(region)) AS region,
    _ingested_at
FROM raw_orders
WHERE order_id IS NOT NULL

-- dbt_project/models/marts/fct_daily_revenue.sql
{{ config(
    materialized='incremental',
    unique_key=['order_date', 'region'],
    incremental_strategy='merge'
) }}

SELECT
    order_date,
    region,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(amount) AS total_revenue,
    AVG(amount) AS avg_order_value,
    CURRENT_TIMESTAMP AS _computed_at
FROM {{ ref('stg_orders') }}
WHERE status = 'COMPLETED'
{% if is_incremental() %}
    AND order_date > (SELECT MAX(order_date) - INTERVAL '2 days' FROM {{ this }})
{% endif %}
GROUP BY order_date, region
```

---

## 5. Monitoring Dashboard

```python
# monitoring/metrics.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json

@dataclass
class PipelineMetrics:
    pipeline_name: str
    run_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    records_extracted: int = 0
    records_transformed: int = 0
    records_loaded: int = 0
    errors: int = 0
    
    @property
    def duration_seconds(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0
    
    def to_json(self) -> str:
        return json.dumps({
            "pipeline": self.pipeline_name,
            "run_id": self.run_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "duration_seconds": self.duration_seconds,
            "records": {
                "extracted": self.records_extracted,
                "transformed": self.records_transformed,
                "loaded": self.records_loaded,
            },
            "errors": self.errors,
        })

class PipelineMonitor:
    """Track pipeline health and send alerts."""
    
    def __init__(self):
        self.metrics: list[PipelineMetrics] = []
    
    def check_sla(self, pipeline_name: str, max_duration_minutes: int) -> bool:
        """Check if pipeline is within SLA."""
        latest = self._get_latest_run(pipeline_name)
        if latest and latest.duration_seconds > max_duration_minutes * 60:
            self._alert(f"SLA breach: {pipeline_name} took {latest.duration_seconds/60:.1f}min")
            return False
        return True
    
    def check_data_freshness(self, table: str, max_age_hours: int) -> bool:
        """Check if table data is fresh."""
        # Query max timestamp in table
        # Alert if older than threshold
        pass
    
    def check_volume_anomaly(self, table: str, date: str) -> bool:
        """Detect unusual record counts."""
        # Compare today's count vs 7-day average
        # Alert if > 2 standard deviations different
        pass
```

---

## 6. End-to-End Testing

```python
# tests/integration/test_pipeline_e2e.py
import pytest
from testcontainers.postgres import PostgresContainer
from testcontainers.kafka import KafkaContainer

@pytest.fixture(scope="session")
def postgres():
    with PostgresContainer("postgres:16") as pg:
        yield pg

@pytest.fixture(scope="session")  
def kafka():
    with KafkaContainer() as k:
        yield k

class TestEndToEnd:
    def test_full_pipeline(self, postgres, kafka):
        """Test complete pipeline flow."""
        # 1. Insert test data into source
        insert_test_orders(postgres, count=100)
        
        # 2. Run extraction
        extracted = run_extract(postgres.get_connection_url())
        assert extracted == 100
        
        # 3. Run dbt transforms
        run_dbt("run", "--select", "tag:test")
        
        # 4. Verify output
        result = query_warehouse("SELECT COUNT(*) FROM marts.fct_orders")
        assert result >= 100
        
        # 5. Verify quality
        run_dbt("test", "--select", "tag:test")
    
    def test_cdc_pipeline(self, postgres, kafka):
        """Test CDC flow: source change → Kafka → warehouse."""
        # 1. Update source record
        update_customer(postgres, "CUST-1", new_email="new@example.com")
        
        # 2. Wait for CDC event
        event = consume_with_timeout(kafka, "cdc.customers", timeout=30)
        assert event is not None
        assert event["after"]["email"] == "new@example.com"
        
        # 3. Process CDC
        process_cdc_batch()
        
        # 4. Verify warehouse updated
        customer = query_warehouse("SELECT email FROM dim_customers WHERE id = 'CUST-1'")
        assert customer == "new@example.com"
```

---

## Interview Questions

### Beginner
1. **What is data orchestration?** Coordinating the execution of data pipeline tasks in the right order, handling failures, retries, and dependencies. Tools: Airflow, Dagster, Prefect.
2. **Why separate extraction from transformation?** ELT pattern: extract raw data first (fast, reliable), then transform at leisure. Enables reprocessing, debugging, and multiple transformations from same source.

### Intermediate
3. **How do you handle pipeline failures mid-way?** Idempotent tasks (rerunnable), checkpointing, atomic writes (transactions), dead letter queues for bad records, alerting, manual retry from failed task.
4. **Design a data freshness SLA system.** Track max(timestamp) per table, compare to wall clock, alert if gap > threshold. Different SLAs per table importance. Dashboard showing freshness across all tables.

### Advanced
5. **Design a platform handling 3 data sources, 50 transforms, 10 consumers.** Modular DAGs per domain, shared staging layer, dbt for transforms with tag-based selection, quality gates between layers, data catalog for discovery, RBAC for access control, cost monitoring.
6. **How do you handle breaking schema changes in production pipelines?** Versioned schemas (Schema Registry), backward-compatible evolution, blue-green deployment for transforms, dual-write during migration, automated schema comparison in CI.

---

## Deliverables
1. Docker Compose with full infrastructure
2. CDC pipeline: PostgreSQL → Debezium → Kafka → Delta Lake
3. Batch pipeline: API/CSV → Airflow → Bronze → Silver → Gold
4. dbt project with staging, intermediate, marts layers
5. Quality gates with alerting
6. End-to-end integration tests
7. Monitoring metrics and freshness checks
8. README with architecture diagram and runbook
