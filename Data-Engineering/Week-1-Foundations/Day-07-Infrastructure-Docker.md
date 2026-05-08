# Day 7: Data Infrastructure & Docker for DE

## Learning Objectives
- Set up local data engineering infrastructure with Docker
- Understand containerization for data pipelines
- Build reproducible environments for DE workflows
- Practice infrastructure-as-code patterns

---

## 1. Docker Fundamentals for Data Engineers

### Why Docker for DE?
- Reproducible environments (same on laptop, CI, prod)
- Isolate dependencies (Spark version, Python packages)
- Quick provisioning of databases, message queues, tools
- Local development mirrors production

### Beginner: Running Data Services

```bash
# Start PostgreSQL for warehouse development
docker run -d \
  --name postgres-warehouse \
  -e POSTGRES_DB=warehouse \
  -e POSTGRES_USER=de_user \
  -e POSTGRES_PASSWORD=secure_pass \
  -p 5432:5432 \
  -v pgdata:/var/lib/postgresql/data \
  postgres:16

# Start MinIO (S3-compatible object storage)
docker run -d \
  --name minio \
  -e MINIO_ROOT_USER=admin \
  -e MINIO_ROOT_PASSWORD=password123 \
  -p 9000:9000 \
  -p 9001:9001 \
  -v minio-data:/data \
  minio/minio server /data --console-address ":9001"

# Start Apache Kafka
docker run -d \
  --name kafka \
  -e KAFKA_BROKER_ID=1 \
  -e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=PLAINTEXT:PLAINTEXT \
  -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
  -p 9092:9092 \
  confluentinc/cp-kafka:7.5.0
```

### Intermediate: Docker Compose for Full Stack

```yaml
# docker-compose.yml - Local DE Environment
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: warehouse
      POSTGRES_USER: de_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U de_user"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio-data:/data

  # Apache Airflow
  airflow-webserver:
    image: apache/airflow:2.8.0-python3.11
    command: webserver
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://de_user:${DB_PASSWORD}@postgres/airflow
      AIRFLOW__CORE__FERNET_KEY: ${FERNET_KEY}
    ports:
      - "8080:8080"
    volumes:
      - ./dags:/opt/airflow/dags
      - ./plugins:/opt/airflow/plugins
    depends_on:
      postgres:
        condition: service_healthy

  # Jupyter for development
  jupyter:
    image: jupyter/pyspark-notebook:latest
    ports:
      - "8888:8888"
    volumes:
      - ./notebooks:/home/jovyan/work
    environment:
      JUPYTER_ENABLE_LAB: "yes"

volumes:
  pgdata:
  minio-data:
```

### Advanced: Custom Pipeline Container

```dockerfile
# Dockerfile for data pipeline
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy pipeline code
COPY src/ /app/src/
COPY config/ /app/config/

WORKDIR /app

# Run pipeline
ENTRYPOINT ["python", "-m", "src.pipeline"]
```

```txt
# requirements.txt
pandas==2.1.4
polars==0.20.3
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
boto3==1.34.0
great-expectations==0.18.8
pyarrow==14.0.2
requests==2.31.0
```

---

## 2. Data Lake Setup with MinIO

```python
import boto3
from botocore.client import Config

def setup_data_lake():
    """Set up MinIO buckets mimicking S3 data lake structure."""
    s3 = boto3.client(
        's3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='admin',
        aws_secret_access_key='password123',
        config=Config(signature_version='s3v4')
    )
    
    # Create lake layers
    buckets = ['bronze', 'silver', 'gold']
    for bucket in buckets:
        try:
            s3.create_bucket(Bucket=bucket)
            print(f"Created bucket: {bucket}")
        except s3.exceptions.BucketAlreadyOwnedByYou:
            print(f"Bucket {bucket} already exists")
    
    return s3

def write_to_lake(s3, layer: str, table: str, df, partition_col: str = None):
    """Write DataFrame to data lake with optional partitioning."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    from io import BytesIO
    
    if partition_col:
        # Partition by date
        for partition_value, partition_df in df.groupby(df[partition_col].dt.date):
            key = f"{table}/{partition_col}={partition_value}/data.parquet"
            buffer = BytesIO()
            partition_df.to_parquet(buffer, index=False)
            buffer.seek(0)
            s3.put_object(Bucket=layer, Key=key, Body=buffer.getvalue())
    else:
        key = f"{table}/data.parquet"
        buffer = BytesIO()
        df.to_parquet(buffer, index=False)
        buffer.seek(0)
        s3.put_object(Bucket=layer, Key=key, Body=buffer.getvalue())
```

---

## 3. Makefile for DE Workflows

```makefile
# Makefile for data engineering project
.PHONY: up down test lint pipeline

# Start all infrastructure
up:
	docker compose up -d
	@echo "Waiting for services..."
	@sleep 10
	@echo "Services ready!"

# Stop all infrastructure
down:
	docker compose down

# Run data quality tests
test:
	python -m pytest tests/ -v

# Lint pipeline code
lint:
	ruff check src/
	mypy src/

# Run the full pipeline
pipeline:
	python -m src.pipeline --config config/production.yaml

# Initialize database schemas
init-db:
	docker exec -i postgres-warehouse psql -U de_user -d warehouse < sql/schema.sql

# Generate sample data for development
seed:
	python scripts/generate_sample_data.py --rows 100000

# View pipeline logs
logs:
	docker compose logs -f airflow-webserver

# Clean up everything
clean:
	docker compose down -v
	rm -rf data/tmp/*
```

---

## 4. Environment Configuration

```python
# config.py - Environment-aware configuration
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass
class DatabaseConfig:
    host: str
    port: int
    database: str
    username: str
    password: str
    
    @property
    def connection_string(self) -> str:
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

@dataclass
class StorageConfig:
    endpoint: str
    access_key: str
    secret_key: str
    bronze_bucket: str = "bronze"
    silver_bucket: str = "silver"
    gold_bucket: str = "gold"

@dataclass
class PipelineEnvironment:
    database: DatabaseConfig
    storage: StorageConfig
    environment: str  # dev, staging, prod

def load_config() -> PipelineEnvironment:
    """Load configuration from environment variables."""
    env = os.getenv('PIPELINE_ENV', 'dev')
    
    return PipelineEnvironment(
        database=DatabaseConfig(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'warehouse'),
            username=os.getenv('DB_USER', 'de_user'),
            password=os.getenv('DB_PASSWORD', 'secure_pass'),
        ),
        storage=StorageConfig(
            endpoint=os.getenv('S3_ENDPOINT', 'http://localhost:9000'),
            access_key=os.getenv('S3_ACCESS_KEY', 'admin'),
            secret_key=os.getenv('S3_SECRET_KEY', 'password123'),
        ),
        environment=env,
    )
```

---

## 5. Testing Data Pipelines

```python
# tests/test_pipeline.py
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from src.pipeline import DataPipeline, PipelineConfig

@pytest.fixture
def sample_data():
    """Create sample test data."""
    return pd.DataFrame({
        'id': [1, 2, 3, 4, 5],
        'amount': [100.0, -50.0, 200.0, None, 300.0],
        'customer_id': ['C1', 'C2', 'C3', 'C4', None],
        'created_at': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']
    })

class TestTransform:
    def test_removes_negative_amounts(self, sample_data):
        pipeline = DataPipeline(config=PipelineConfig(...), engine=None)
        result = pipeline.transform(sample_data)
        assert (result['amount'] > 0).all()
    
    def test_removes_null_customer_ids(self, sample_data):
        pipeline = DataPipeline(config=PipelineConfig(...), engine=None)
        result = pipeline.transform(sample_data)
        assert result['customer_id'].notna().all()
    
    def test_adds_metadata_columns(self, sample_data):
        pipeline = DataPipeline(config=PipelineConfig(...), engine=None)
        result = pipeline.transform(sample_data)
        assert '_loaded_at' in result.columns
        assert '_source_file' in result.columns

class TestValidation:
    def test_validator_catches_nulls(self, sample_data):
        from src.validation import DataValidator, ValidationRule, Severity
        validator = DataValidator()
        validator.add_rule(ValidationRule(
            name="no_nulls",
            check=lambda df: df['amount'].notna(),
            severity=Severity.ERROR
        ))
        results = validator.validate(sample_data)
        assert not results[0].passed
        assert results[0].failed_records == 1
```

---

## Interview Questions

### Beginner
1. **Why use Docker for data engineering?** Reproducible environments, easy setup of databases/queues, consistent dev-to-prod, isolation of dependencies.
2. **What is a data lake vs data warehouse?** Lake stores raw data in files (schema-on-read); warehouse stores structured data (schema-on-write) optimized for queries.
3. **What's the Bronze-Silver-Gold pattern?** Bronze = raw ingested data, Silver = cleaned/validated, Gold = aggregated/business-ready. Each layer adds quality.

### Intermediate
4. **How do you handle secrets in containerized pipelines?** Environment variables (not in images), Docker secrets, vault integration (HashiCorp Vault), cloud secret managers.
5. **Explain the difference between volumes and bind mounts.** Volumes are managed by Docker (persistent, portable); bind mounts link host paths (useful for development, not portable).
6. **How do you test data pipelines?** Unit tests (transform logic), integration tests (with real DB via testcontainers), data quality tests (Great Expectations), contract tests.

### Advanced
7. **Design a local development environment that mirrors production.** Docker Compose with same services, seed data generators, Makefile for workflows, environment configs per stage, testcontainers for integration tests.
8. **How do you handle data pipeline dependency management?** Pin all versions (requirements.txt), use Docker multi-stage builds, separate base/app layers for cache efficiency, vulnerability scanning.
9. **Explain blue-green deployments for data pipelines.** Run new pipeline version alongside old, validate output matches, switch over. Requires idempotent pipelines and output comparison tools.

---

## Hands-On Project
Set up a complete local DE environment:
1. Docker Compose with PostgreSQL, MinIO, Redis
2. Initialize warehouse schema (staging, production schemas)
3. Create sample data generator
4. Build a pipeline that moves data: CSV → MinIO (bronze) → PostgreSQL (silver)
5. Add Makefile for common operations
6. Write tests using pytest + testcontainers
