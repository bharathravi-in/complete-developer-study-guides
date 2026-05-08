# Day 6: Data Pipelines with Python

## Learning Objectives
- Build production-grade data pipelines in Python
- Master key libraries: pandas, polars, SQLAlchemy, requests
- Implement error handling, logging, and retry patterns
- Understand pipeline orchestration basics

---

## 1. Pipeline Architecture Patterns

### Beginner: Simple Extract-Load Script

```python
import pandas as pd
import sqlalchemy
from datetime import datetime

def extract_from_csv(file_path: str) -> pd.DataFrame:
    """Extract data from CSV with basic validation."""
    df = pd.read_csv(file_path)
    print(f"Extracted {len(df)} rows from {file_path}")
    return df

def load_to_database(df: pd.DataFrame, table_name: str, engine):
    """Load DataFrame to PostgreSQL."""
    df.to_sql(table_name, engine, if_exists='append', index=False)
    print(f"Loaded {len(df)} rows to {table_name}")

# Usage
engine = sqlalchemy.create_engine('postgresql://user:pass@localhost/warehouse')
data = extract_from_csv('sales_2024.csv')
load_to_database(data, 'raw_sales', engine)
```

### Intermediate: Pipeline with Transformations

```python
import pandas as pd
import logging
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PipelineConfig:
    source_path: str
    target_table: str
    batch_size: int = 10000
    date_column: str = 'created_at'

class DataPipeline:
    def __init__(self, config: PipelineConfig, engine):
        self.config = config
        self.engine = engine
        self.metrics = {'extracted': 0, 'transformed': 0, 'loaded': 0, 'errors': 0}
    
    def extract(self) -> pd.DataFrame:
        """Extract with chunking for large files."""
        chunks = []
        for chunk in pd.read_csv(self.config.source_path, chunksize=self.config.batch_size):
            chunks.append(chunk)
        df = pd.concat(chunks, ignore_index=True)
        self.metrics['extracted'] = len(df)
        logger.info(f"Extracted {len(df)} rows")
        return df
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply business transformations."""
        # Remove duplicates
        initial_count = len(df)
        df = df.drop_duplicates()
        
        # Parse dates
        df[self.config.date_column] = pd.to_datetime(
            df[self.config.date_column], errors='coerce'
        )
        
        # Remove rows with null dates
        df = df.dropna(subset=[self.config.date_column])
        
        # Add metadata columns
        df['_loaded_at'] = datetime.utcnow()
        df['_source_file'] = self.config.source_path
        
        self.metrics['transformed'] = len(df)
        logger.info(f"Transformed: {initial_count} → {len(df)} rows")
        return df
    
    def load(self, df: pd.DataFrame):
        """Load with batch processing."""
        for i in range(0, len(df), self.config.batch_size):
            batch = df.iloc[i:i + self.config.batch_size]
            batch.to_sql(
                self.config.target_table, 
                self.engine, 
                if_exists='append', 
                index=False,
                method='multi'
            )
        self.metrics['loaded'] = len(df)
        logger.info(f"Loaded {len(df)} rows to {self.config.target_table}")
    
    def run(self):
        """Execute full pipeline."""
        try:
            df = self.extract()
            df = self.transform(df)
            self.load(df)
            logger.info(f"Pipeline complete: {self.metrics}")
        except Exception as e:
            self.metrics['errors'] += 1
            logger.error(f"Pipeline failed: {e}")
            raise
```

### Advanced: Production Pipeline with Retry & Monitoring

```python
import time
import functools
from typing import Callable, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

def retry(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator for retry with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            attempts = 0
            current_delay = delay
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempts}/{max_attempts}): {e}"
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator

class ProductionPipeline:
    """Pipeline with retry, dead-letter queue, and parallel processing."""
    
    def __init__(self, config: PipelineConfig, engine):
        self.config = config
        self.engine = engine
        self.dead_letter_queue = []
    
    @retry(max_attempts=3, delay=2.0)
    def extract_from_api(self, url: str, params: dict) -> dict:
        """Extract from REST API with retry."""
        import requests
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    
    def extract_parallel(self, urls: list[str]) -> list[dict]:
        """Extract from multiple sources in parallel."""
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(self.extract_from_api, url, {}): url 
                for url in urls
            }
            for future in as_completed(futures):
                url = futures[future]
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.error(f"Failed to extract from {url}: {e}")
                    self.dead_letter_queue.append({'url': url, 'error': str(e)})
        return results
    
    def validate(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Separate valid and invalid records."""
        # Define validation rules
        valid_mask = (
            df['amount'].notna() & 
            (df['amount'] > 0) & 
            df['customer_id'].notna()
        )
        valid_df = df[valid_mask].copy()
        invalid_df = df[~valid_mask].copy()
        
        if len(invalid_df) > 0:
            logger.warning(f"{len(invalid_df)} invalid records sent to dead letter queue")
            self.dead_letter_queue.extend(invalid_df.to_dict('records'))
        
        return valid_df, invalid_df
    
    @retry(max_attempts=3)
    def load_batch(self, batch: pd.DataFrame, table: str):
        """Load a single batch with retry."""
        batch.to_sql(table, self.engine, if_exists='append', index=False, method='multi')
```

---

## 2. Polars for High-Performance Pipelines

```python
import polars as pl

# Polars is 10-100x faster than pandas for large datasets
def polars_pipeline(source: str, target: str):
    """High-performance pipeline using Polars."""
    
    # Lazy evaluation - builds query plan, executes optimally
    df = (
        pl.scan_csv(source)
        .filter(pl.col('amount') > 0)
        .with_columns([
            pl.col('created_at').str.to_datetime(),
            pl.col('amount').cast(pl.Float64),
            pl.lit(datetime.utcnow()).alias('_loaded_at'),
        ])
        .group_by('customer_id')
        .agg([
            pl.col('amount').sum().alias('total_amount'),
            pl.col('amount').count().alias('transaction_count'),
            pl.col('created_at').max().alias('last_transaction'),
        ])
        .sort('total_amount', descending=True)
        .collect()  # Execute the plan
    )
    
    # Write to Parquet (efficient columnar format)
    df.write_parquet(target)
    return df

# Streaming for files larger than memory
def polars_streaming(source: str):
    """Process files larger than RAM."""
    result = (
        pl.scan_csv(source)
        .filter(pl.col('status') == 'completed')
        .group_by('region')
        .agg(pl.col('revenue').sum())
        .collect(streaming=True)  # Process in chunks
    )
    return result
```

---

## 3. API Data Extraction Patterns

```python
import requests
from typing import Generator
import time

class APIExtractor:
    """Production API extractor with pagination, rate limiting."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        self.rate_limit_remaining = 100
    
    def paginate(self, endpoint: str, page_size: int = 100) -> Generator:
        """Yield pages of results with cursor-based pagination."""
        cursor = None
        while True:
            params = {'limit': page_size}
            if cursor:
                params['cursor'] = cursor
            
            response = self._make_request(endpoint, params)
            data = response.json()
            
            yield data['results']
            
            cursor = data.get('next_cursor')
            if not cursor:
                break
    
    def _make_request(self, endpoint: str, params: dict) -> requests.Response:
        """Make request with rate limit handling."""
        if self.rate_limit_remaining < 5:
            time.sleep(60)  # Wait for rate limit reset
        
        response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
        
        self.rate_limit_remaining = int(
            response.headers.get('X-RateLimit-Remaining', 100)
        )
        
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 60))
            time.sleep(retry_after)
            return self._make_request(endpoint, params)
        
        response.raise_for_status()
        return response
    
    def extract_all(self, endpoint: str) -> pd.DataFrame:
        """Extract all pages into a DataFrame."""
        all_records = []
        for page in self.paginate(endpoint):
            all_records.extend(page)
        return pd.DataFrame(all_records)
```

---

## 4. Database CDC (Change Data Capture) with Python

```python
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta

class IncrementalExtractor:
    """Extract only changed records since last run."""
    
    def __init__(self, connection_string: str):
        self.conn = psycopg2.connect(connection_string)
    
    def get_last_watermark(self, pipeline_name: str) -> datetime:
        """Get the last successful extraction timestamp."""
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT max_watermark FROM pipeline_state WHERE name = %s",
                (pipeline_name,)
            )
            result = cur.fetchone()
            return result[0] if result else datetime(2020, 1, 1)
    
    def extract_incremental(self, table: str, watermark_col: str, 
                           pipeline_name: str) -> pd.DataFrame:
        """Extract records modified since last run."""
        last_watermark = self.get_last_watermark(pipeline_name)
        
        query = f"""
            SELECT * FROM {table}
            WHERE {watermark_col} > %s
            ORDER BY {watermark_col}
        """
        
        df = pd.read_sql(query, self.conn, params=[last_watermark])
        
        if len(df) > 0:
            new_watermark = df[watermark_col].max()
            self._update_watermark(pipeline_name, new_watermark)
        
        return df
    
    def _update_watermark(self, pipeline_name: str, watermark: datetime):
        """Update watermark after successful extraction."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pipeline_state (name, max_watermark, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (name) DO UPDATE SET 
                    max_watermark = EXCLUDED.max_watermark,
                    updated_at = NOW()
            """, (pipeline_name, watermark))
            self.conn.commit()
```

---

## 5. Data Validation Framework

```python
from dataclasses import dataclass, field
from typing import Callable
from enum import Enum

class Severity(Enum):
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationRule:
    name: str
    check: Callable[[pd.DataFrame], pd.Series]  # Returns boolean mask
    severity: Severity = Severity.ERROR
    description: str = ""

@dataclass
class ValidationResult:
    rule_name: str
    passed: bool
    total_records: int
    failed_records: int
    severity: Severity
    sample_failures: list = field(default_factory=list)

class DataValidator:
    """Validate data quality before loading."""
    
    def __init__(self):
        self.rules: list[ValidationRule] = []
    
    def add_rule(self, rule: ValidationRule):
        self.rules.append(rule)
    
    def validate(self, df: pd.DataFrame) -> list[ValidationResult]:
        """Run all validation rules."""
        results = []
        for rule in self.rules:
            mask = rule.check(df)
            failed = (~mask).sum()
            result = ValidationResult(
                rule_name=rule.name,
                passed=failed == 0,
                total_records=len(df),
                failed_records=failed,
                severity=rule.severity,
                sample_failures=df[~mask].head(5).to_dict('records') if failed > 0 else []
            )
            results.append(result)
        return results
    
    def has_critical_failures(self, results: list[ValidationResult]) -> bool:
        return any(
            not r.passed and r.severity == Severity.CRITICAL 
            for r in results
        )

# Usage
validator = DataValidator()
validator.add_rule(ValidationRule(
    name="no_null_ids",
    check=lambda df: df['id'].notna(),
    severity=Severity.CRITICAL
))
validator.add_rule(ValidationRule(
    name="positive_amounts",
    check=lambda df: df['amount'] > 0,
    severity=Severity.ERROR
))
validator.add_rule(ValidationRule(
    name="valid_dates",
    check=lambda df: df['date'] <= pd.Timestamp.now(),
    severity=Severity.WARNING
))
```

---

## 6. Logging & Monitoring for Pipelines

```python
import logging
import json
from datetime import datetime
from contextlib import contextmanager
import time

class StructuredLogger:
    """JSON structured logging for pipeline observability."""
    
    def __init__(self, pipeline_name: str):
        self.logger = logging.getLogger(pipeline_name)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.pipeline_name = pipeline_name
    
    def log(self, event: str, **kwargs):
        msg = json.dumps({
            'timestamp': datetime.utcnow().isoformat(),
            'pipeline': self.pipeline_name,
            'event': event,
            **kwargs
        })
        self.logger.info(msg)

@contextmanager
def pipeline_step(logger: StructuredLogger, step_name: str):
    """Context manager to time and log pipeline steps."""
    logger.log('step_started', step=step_name)
    start = time.time()
    try:
        yield
        duration = time.time() - start
        logger.log('step_completed', step=step_name, duration_seconds=round(duration, 2))
    except Exception as e:
        duration = time.time() - start
        logger.log('step_failed', step=step_name, duration_seconds=round(duration, 2), error=str(e))
        raise

# Usage
logger = StructuredLogger('sales_pipeline')
with pipeline_step(logger, 'extract'):
    df = extract_data()
with pipeline_step(logger, 'transform'):
    df = transform_data(df)
with pipeline_step(logger, 'load'):
    load_data(df)
```

---

## Interview Questions

### Beginner
1. **What's the difference between ETL and ELT?** ETL transforms before loading (traditional); ELT loads raw then transforms in-place (modern, cloud warehouses handle compute).
2. **Why use chunking when reading large files?** Memory management—reading a 10GB file at once crashes; chunks process sequentially within RAM limits.
3. **What is idempotency and why does it matter?** Running a pipeline multiple times produces the same result. Critical for retry safety.

### Intermediate
4. **How do you handle schema changes in a pipeline?** Schema evolution strategies: add nullable columns, version schemas, use schema registry, alert on breaking changes.
5. **When would you use Polars over pandas?** Large datasets (>1GB), need for speed (lazy evaluation, Rust backend), parallel processing. Pandas for quick prototyping and ecosystem compatibility.
6. **Explain incremental extraction patterns.** Watermark-based (track last timestamp), CDC with logical replication, or change tracking columns (updated_at).

### Advanced
7. **Design a pipeline that handles 1M records/hour with exactly-once delivery.** Idempotent writes (upsert with natural keys), watermark tracking in transactions, dead letter queue for failures, batch-level checksums.
8. **How do you ensure data quality in production pipelines?** Multi-layer validation (source, transform, load), Great Expectations integration, alerting on anomalies, circuit breakers for bad data, quarantine patterns.
9. **Explain backpressure in data pipelines.** When downstream can't keep up with upstream. Solutions: buffering (queues), rate limiting, adaptive batch sizing, circuit breakers.

---

## Hands-On Exercise
Build a pipeline that:
1. Extracts from a REST API with pagination
2. Validates data quality (null checks, type checks, range checks)
3. Transforms (dedup, normalize, enrich)
4. Loads to PostgreSQL with upsert logic
5. Logs metrics (rows processed, duration, errors)
6. Handles failures with dead letter queue
