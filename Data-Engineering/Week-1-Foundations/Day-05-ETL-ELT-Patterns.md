# Day 5: ETL vs ELT Patterns

## Overview
Understanding data movement patterns — Extract-Transform-Load vs Extract-Load-Transform, Change Data Capture, and building idempotent pipelines.

---

## 1. ETL vs ELT

### ETL (Traditional)
```
Source → [Extract] → Staging → [Transform] → [Load] → Warehouse
                         ↑
              Transform happens OUTSIDE warehouse
              (Spark, Python, Informatica)
```

### ELT (Modern)
```
Source → [Extract] → [Load Raw] → Warehouse → [Transform in-place]
                                       ↑
                          Transform happens INSIDE warehouse
                          (SQL, dbt, stored procs)
```

### When to Use Each
| Use ETL When | Use ELT When |
|---|---|
| Warehouse compute is expensive | Warehouse has elastic compute (Snowflake, BQ) |
| Complex transformations (ML, NLP) | SQL-expressible transformations |
| Data reduction before load (filter 90%) | Load everything, transform later |
| Sensitive data must not enter warehouse raw | Warehouse handles masking |
| Legacy systems (Informatica, SSIS) | Modern cloud stack |

---

## 2. Change Data Capture (CDC)

### What is CDC?
Capture only the changes (INSERT, UPDATE, DELETE) from source systems instead of full loads.

### CDC Methods

#### 1. Timestamp-Based (Pull)
```python
# Simple but misses deletes
last_extracted = get_watermark('customers')  # e.g., '2024-03-15 10:30:00'

new_records = db.query("""
    SELECT * FROM customers 
    WHERE updated_at > :last_extracted
""", last_extracted=last_extracted)

load_to_staging(new_records)
update_watermark('customers', max(new_records['updated_at']))
```

**Pros**: Simple, no source changes needed  
**Cons**: Misses deletes, requires updated_at column, clock skew issues

#### 2. Log-Based (Push) — Preferred
```
PostgreSQL WAL / MySQL Binlog → Debezium → Kafka → Target
```

```json
// Debezium CDC event
{
  "op": "u",  // c=create, u=update, d=delete
  "before": {"id": 1, "name": "John", "tier": "silver"},
  "after":  {"id": 1, "name": "John", "tier": "gold"},
  "source": {
    "version": "2.4.0",
    "connector": "postgresql",
    "ts_ms": 1710500000000,
    "table": "customers",
    "lsn": 123456789
  }
}
```

**Pros**: Captures all changes including deletes, minimal source impact, real-time  
**Cons**: Complex setup, schema changes need handling

#### 3. Trigger-Based
```sql
-- Audit table populated by trigger
CREATE TABLE customer_changes (
    change_id SERIAL PRIMARY KEY,
    operation TEXT,  -- INSERT, UPDATE, DELETE
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    old_data JSONB,
    new_data JSONB
);

CREATE OR REPLACE FUNCTION track_customer_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO customer_changes (operation, old_data, new_data)
    VALUES (TG_OP, to_jsonb(OLD), to_jsonb(NEW));
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Pros**: Guaranteed capture  
**Cons**: Performance impact on source, tight coupling

---

## 3. Idempotent Pipeline Patterns

### Why Idempotency Matters
Running the same pipeline twice should produce the same result. Critical for:
- Retry after failures
- Backfill historical data
- Testing and debugging

### Pattern 1: DELETE + INSERT (Partition Replace)
```python
def load_daily_data(date: str, data: pd.DataFrame, engine):
    """Idempotent: safe to re-run for any date"""
    with engine.begin() as conn:
        # Delete existing data for this partition
        conn.execute(
            text("DELETE FROM fact_events WHERE event_date = :dt"),
            {"dt": date}
        )
        # Insert fresh data
        data.to_sql('fact_events', conn, if_exists='append', index=False)
```

### Pattern 2: MERGE / UPSERT
```sql
-- PostgreSQL: INSERT ON CONFLICT
INSERT INTO dim_customer (customer_id, name, email, tier, updated_at)
VALUES ('C123', 'John', 'john@email.com', 'gold', NOW())
ON CONFLICT (customer_id) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    tier = EXCLUDED.tier,
    updated_at = EXCLUDED.updated_at;

-- Snowflake/BigQuery: MERGE
MERGE INTO target_table t
USING staging_table s ON t.id = s.id
WHEN MATCHED AND s.hash_diff != t.hash_diff THEN
    UPDATE SET t.name = s.name, t.email = s.email, t.updated_at = s.updated_at
WHEN NOT MATCHED THEN
    INSERT (id, name, email, updated_at) 
    VALUES (s.id, s.name, s.email, s.updated_at);
```

### Pattern 3: Append-Only with Deduplication
```sql
-- Load all data (including duplicates), deduplicate at read time
CREATE VIEW fact_events_deduped AS
SELECT * FROM (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY load_timestamp DESC) AS rn
    FROM fact_events_raw
) WHERE rn = 1;
```

---

## 4. Incremental Loading Strategies

### Full Load (Snapshot)
```python
# Replace entire table — simplest but expensive for large tables
def full_load(source_query, target_table, engine):
    data = extract(source_query)
    data.to_sql(target_table, engine, if_exists='replace', index=False)
```

### Incremental by Watermark
```python
def incremental_load(source_table, target_table, engine):
    # Get high watermark from target
    watermark = engine.execute(
        f"SELECT COALESCE(MAX(updated_at), '1970-01-01') FROM {target_table}"
    ).scalar()
    
    # Extract only new/changed records
    new_data = extract(f"""
        SELECT * FROM {source_table} 
        WHERE updated_at > '{watermark}'
    """)
    
    if len(new_data) > 0:
        # Upsert into target
        upsert(new_data, target_table, key_columns=['id'], engine=engine)
        print(f"Loaded {len(new_data)} incremental records")
```

### Incremental with Partitions
```python
def partition_load(date: str, engine):
    """Process one date partition at a time"""
    # Extract partition
    data = extract(f"SELECT * FROM source WHERE event_date = '{date}'")
    
    # Replace partition (idempotent)
    engine.execute(f"DELETE FROM target WHERE event_date = '{date}'")
    data.to_sql('target', engine, if_exists='append', index=False)
```

---

## 5. Data Pipeline Architecture Patterns

### Medallion Architecture (Bronze → Silver → Gold)
```
┌─────────┐     ┌─────────┐     ┌─────────┐
│ BRONZE  │────▶│ SILVER  │────▶│  GOLD   │
│  (Raw)  │     │(Cleaned)│     │(Business)│
└─────────┘     └─────────┘     └─────────┘

Bronze: Raw ingestion, no transformations, append-only
Silver: Deduplicated, typed, validated, joined
Gold: Business-level aggregates, ready for BI/ML
```

```python
# Bronze: Raw ingestion
def bronze_load(source_file: str):
    """Load raw data as-is with metadata"""
    raw = pd.read_json(source_file)
    raw['_source_file'] = source_file
    raw['_ingested_at'] = datetime.utcnow()
    raw['_raw_data'] = raw.to_json(orient='records')
    save_to_delta('bronze.events', raw)

# Silver: Cleaned and validated
def silver_transform():
    """Clean, deduplicate, validate, type-cast"""
    bronze = read_delta('bronze.events')
    
    silver = (bronze
        .drop_duplicates(subset=['event_id'])
        .dropna(subset=['user_id', 'event_type'])
        .assign(
            event_timestamp=lambda df: pd.to_datetime(df['event_timestamp']),
            amount=lambda df: df['amount'].astype(float)
        )
    )
    
    # Validate
    assert silver['amount'].min() >= 0, "Negative amounts found!"
    save_to_delta('silver.events', silver)

# Gold: Business aggregates
def gold_aggregate():
    """Build business-level metrics"""
    silver = read_delta('silver.events')
    
    daily_metrics = (silver
        .groupby(['event_date', 'event_type'])
        .agg(
            event_count=('event_id', 'count'),
            unique_users=('user_id', 'nunique'),
            total_amount=('amount', 'sum')
        )
        .reset_index()
    )
    save_to_delta('gold.daily_metrics', daily_metrics)
```

---

## 6. Error Handling & Recovery

### Dead Letter Queue Pattern
```python
def process_with_dlq(records: list, engine):
    """Process records, send failures to DLQ"""
    success = []
    failed = []
    
    for record in records:
        try:
            validated = validate_and_transform(record)
            success.append(validated)
        except ValidationError as e:
            failed.append({
                'record': record,
                'error': str(e),
                'failed_at': datetime.utcnow().isoformat()
            })
    
    # Load successes to target
    if success:
        load_to_target(success, engine)
    
    # Load failures to DLQ for investigation
    if failed:
        load_to_dlq(failed, engine)
        alert_on_failure_rate(len(failed), len(records))
```

### Retry with Exponential Backoff
```python
import time
from functools import wraps

def retry(max_attempts=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (ConnectionError, TimeoutError) as e:
                    if attempt == max_attempts - 1:
                        raise
                    wait = backoff_factor ** attempt
                    print(f"Attempt {attempt+1} failed, retrying in {wait}s: {e}")
                    time.sleep(wait)
        return wrapper
    return decorator

@retry(max_attempts=3)
def extract_from_api(endpoint: str):
    response = requests.get(endpoint, timeout=30)
    response.raise_for_status()
    return response.json()
```

---

## 7. Practice Project: Multi-Source ELT Pipeline

Build a pipeline that:
1. **Extracts** from 3 sources: CSV file, JSON API, PostgreSQL table
2. **Loads** raw data to a staging schema (bronze layer)
3. **Transforms** using SQL/Python to create clean silver tables
4. **Handles** duplicates, nulls, and schema mismatches
5. **Is idempotent** — safe to re-run for any date

### Starter Template
```python
from dataclasses import dataclass
from datetime import date

@dataclass
class PipelineConfig:
    run_date: date
    source_db_url: str
    target_db_url: str
    
class ELTPipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.metrics = {'extracted': 0, 'loaded': 0, 'failed': 0}
    
    def run(self):
        """Main pipeline orchestration"""
        # Extract
        csv_data = self.extract_csv('data/orders.csv')
        api_data = self.extract_api('https://api.example.com/events')
        db_data = self.extract_db('SELECT * FROM customers WHERE updated_at > :date')
        
        # Load raw (bronze)
        self.load_raw('bronze.orders', csv_data)
        self.load_raw('bronze.events', api_data)
        self.load_raw('bronze.customers', db_data)
        
        # Transform (silver)
        self.transform_silver()
        
        # Report
        print(f"Pipeline complete: {self.metrics}")
```

---

## Key Takeaways
- ELT is the modern default (leverage warehouse compute)
- CDC with log-based capture (Debezium) is the gold standard for real-time sync
- Every pipeline MUST be idempotent — retry-safe by design
- Medallion architecture (Bronze→Silver→Gold) organizes data by quality level
- Use watermarks for incremental loads, partition-replace for batch reprocessing
- Dead letter queues prevent bad records from blocking pipelines

## Tomorrow
**Day 6**: Python for Data Engineering — Pandas at scale, Polars, DuckDB, and data validation with Great Expectations.
