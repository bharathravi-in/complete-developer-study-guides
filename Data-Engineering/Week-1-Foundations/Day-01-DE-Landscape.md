# Day 1: Data Engineering Landscape

## Overview
Understanding what Data Engineers do, the modern data stack, and how it all fits together.

---

## 1. What is Data Engineering?

Data Engineering is the practice of designing, building, and maintaining systems that collect, store, and transform data for analysis and decision-making.

### DE vs Related Roles
| Role | Focus |
|------|-------|
| Data Engineer | Pipelines, infrastructure, data quality |
| Data Scientist | Statistical modeling, ML experiments |
| AI Engineer | LLM applications, model deployment |
| Analytics Engineer | dbt, semantic layer, business logic |
| ML Engineer | Model training at scale, MLOps |

---

## 2. The Modern Data Stack

```
Sources → Ingestion → Storage → Transformation → Serving → Consumption
   ↓          ↓          ↓            ↓              ↓          ↓
APIs      Fivetran    Data Lake     dbt          Data Mart   Dashboards
DBs       Kafka       Warehouse    Spark         APIs        ML Models
Files     Airbyte     Lakehouse    Python        Metrics     Reports
Events    CDC         Object Store               Reverse ETL
```

### Key Components
1. **Ingestion**: Kafka, Fivetran, Airbyte, custom connectors
2. **Storage**: S3/GCS (data lake), Snowflake/BigQuery (warehouse), Delta Lake (lakehouse)
3. **Transformation**: dbt, Spark, Python scripts
4. **Orchestration**: Airflow, Dagster, Prefect
5. **Quality**: Great Expectations, dbt tests, Monte Carlo
6. **Serving**: APIs, reverse ETL, semantic layers

---

## 3. Batch vs Streaming

### Batch Processing
- Process data in chunks at scheduled intervals
- Higher latency (minutes to hours), lower complexity
- Tools: Spark batch, Airflow, dbt
- Use cases: Daily reports, ML training, historical analysis

### Stream Processing  
- Process data as it arrives (real-time or near-real-time)
- Low latency (milliseconds to seconds), higher complexity
- Tools: Kafka, Flink, Spark Streaming
- Use cases: Fraud detection, real-time recommendations, monitoring

### When to Choose What
```
Latency needed < 1 second  → Stream processing
Latency needed < 1 hour    → Micro-batch or stream
Latency needed > 1 hour    → Batch
Complex joins/aggregations  → Batch (simpler)
Event-driven actions        → Stream
```

---

## 4. Data Pipeline Patterns

### ETL (Extract → Transform → Load)
```python
# Traditional: Transform BEFORE loading
raw_data = extract_from_source()        # Extract
clean_data = transform(raw_data)         # Transform
load_to_warehouse(clean_data)            # Load
```
- Transform happens outside the warehouse
- Good when: compute is cheaper outside, strict schema needed

### ELT (Extract → Load → Transform)
```python
# Modern: Load raw, transform IN warehouse
raw_data = extract_from_source()         # Extract
load_raw_to_warehouse(raw_data)          # Load (raw)
transform_in_warehouse()                  # Transform (SQL/dbt)
```
- Leverage warehouse compute power
- Good when: warehouse is powerful (Snowflake, BigQuery), schema evolves

### CDC (Change Data Capture)
```
Source DB → WAL/Binlog → Kafka → Target
         (only changes)
```
- Capture only INSERT/UPDATE/DELETE events
- Tools: Debezium, AWS DMS, Fivetran
- Minimal source impact, near-real-time sync

---

## 5. Data Architecture Patterns

### Data Warehouse
- Structured, schema-on-write
- SQL-first, optimized for analytics
- Examples: Snowflake, BigQuery, Redshift

### Data Lake
- Raw data, schema-on-read
- Store anything (structured, semi-structured, unstructured)
- Examples: S3 + Athena, HDFS, ADLS

### Data Lakehouse
- Best of both: raw storage + ACID + SQL
- Open formats with warehouse features
- Examples: Delta Lake, Apache Iceberg, Apache Hudi

### Data Mesh
- Domain-oriented, decentralized ownership
- Data as a product, federated governance
- Organizational pattern, not a technology

---

## 6. Key Principles for Data Engineers

### Idempotency
```python
# BAD: Running twice creates duplicates
def load_data(records):
    db.insert(records)

# GOOD: Running twice produces same result
def load_data(records, run_date):
    db.delete_where(date=run_date)  # Clear first
    db.insert(records)              # Then insert
```

### Schema Evolution
- Backward compatible: new readers can read old data
- Forward compatible: old readers can read new data
- Use formats that support evolution: Avro, Parquet + Delta Lake

### Data Contracts
```yaml
# Define expectations between producer and consumer
schema:
  fields:
    - name: user_id
      type: string
      required: true
    - name: event_timestamp
      type: timestamp
      required: true
  sla:
    freshness: 1h
    completeness: 99.9%
```

---

## 7. Hands-On: Your First Data Pipeline

```python
"""
Simple ETL pipeline: CSV → Clean → PostgreSQL
"""
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

def extract(file_path: str) -> pd.DataFrame:
    """Extract data from source"""
    df = pd.read_csv(file_path)
    print(f"Extracted {len(df)} rows")
    return df

def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform data"""
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Handle nulls
    df = df.dropna(subset=['user_id', 'event_type'])
    
    # Add metadata
    df['processed_at'] = datetime.utcnow()
    df['source'] = 'csv_import'
    
    print(f"Transformed: {len(df)} rows remaining")
    return df

def load(df: pd.DataFrame, table_name: str, engine):
    """Load data to warehouse (idempotent)"""
    # Truncate-and-load pattern
    df.to_sql(
        table_name,
        engine,
        if_exists='replace',
        index=False,
        method='multi'
    )
    print(f"Loaded {len(df)} rows to {table_name}")

def run_pipeline():
    """Orchestrate the ETL"""
    engine = create_engine('postgresql://user:pass@localhost:5432/warehouse')
    
    # ETL
    raw = extract('data/events.csv')
    clean = transform(raw)
    load(clean, 'stg_events', engine)
    
    print("Pipeline completed successfully!")

if __name__ == '__main__':
    run_pipeline()
```

---

## 8. Mini-Project: Pipeline Health Dashboard

Create a simple pipeline that:
1. Reads a CSV file with mock event data
2. Validates data quality (nulls, duplicates, schema)
3. Generates a quality report
4. Loads clean data to a SQLite/PostgreSQL table

**Bonus**: Add logging, timing metrics, and error handling.

---

## Key Takeaways
- Data Engineering = building reliable data pipelines at scale
- Modern stack: ELT > ETL, Lakehouse > pure lake/warehouse
- Idempotency and data contracts are non-negotiable
- Choose batch vs streaming based on latency requirements
- The landscape is vast — focus on fundamentals first

---

## Resources
- [Fundamentals of Data Engineering (Joe Reis)](https://www.oreilly.com/library/view/fundamentals-of-data/9781098108298/)
- [The Data Engineering Cookbook](https://github.com/andkret/Cookbook)
- [Modern Data Stack glossary](https://www.moderndatastack.xyz/)

## Tomorrow
**Day 2**: Advanced SQL for Data Engineering — Window functions, CTEs, LATERAL joins, and query optimization patterns every DE must know.
