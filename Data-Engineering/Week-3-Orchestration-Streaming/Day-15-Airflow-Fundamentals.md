# Day 15: Apache Airflow Fundamentals

## Overview
Apache Airflow is the industry-standard workflow orchestrator. Learn to build, schedule, and monitor data pipelines as code.

---

## 1. What is Airflow?

A platform to **author, schedule, and monitor** workflows as Directed Acyclic Graphs (DAGs) of tasks.

### Key Concepts
| Concept | Description |
|---------|-------------|
| **DAG** | Directed Acyclic Graph — defines workflow structure and dependencies |
| **Task** | A single unit of work (an operator instance) |
| **Operator** | Template for a task (PythonOperator, BashOperator, etc.) |
| **Sensor** | Waits for an external condition to be met |
| **XCom** | Cross-communication between tasks (small data) |
| **Connection** | Credentials for external systems |
| **Variable** | Key-value config stored in Airflow |
| **Pool** | Limit concurrency for resource-constrained operations |

### Architecture
```
┌─────────────┐     ┌────────────┐     ┌────────────┐
│  Scheduler  │────▶│  Metadata  │◀────│  Webserver │
│ (triggers   │     │  Database  │     │  (UI)      │
│  DAG runs)  │     │(PostgreSQL)│     └────────────┘
└──────┬──────┘     └────────────┘
       │
       ▼
┌──────────────┐
│   Executor   │
│ (runs tasks) │
│  ┌────────┐  │
│  │Worker 1│  │   Executors: LocalExecutor, CeleryExecutor,
│  │Worker 2│  │              KubernetesExecutor
│  │Worker N│  │
│  └────────┘  │
└──────────────┘
```

---

## 2. Your First DAG

```python
"""
DAG: Daily ETL Pipeline
Schedule: Every day at 6 AM UTC
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

# Default arguments applied to all tasks
default_args = {
    'owner': 'data-engineering',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['alerts@company.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=1),
}

# DAG definition
with DAG(
    dag_id='daily_etl_pipeline',
    default_args=default_args,
    description='Extract, transform, and load daily data',
    schedule_interval='0 6 * * *',      # Cron: 6 AM daily
    start_date=datetime(2024, 1, 1),
    catchup=False,                       # Don't backfill
    tags=['etl', 'production'],
    max_active_runs=1,                   # Only one run at a time
) as dag:

    # Task 1: Extract
    def extract_data(**context):
        """Extract data from source API"""
        execution_date = context['ds']  # YYYY-MM-DD string
        print(f"Extracting data for {execution_date}")
        # Your extraction logic here
        records = fetch_from_api(date=execution_date)
        return len(records)  # Returned value goes to XCom

    extract = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
    )

    # Task 2: Validate
    validate = BashOperator(
        task_id='validate_data',
        bash_command='python /opt/scripts/validate.py --date {{ ds }}',
    )

    # Task 3: Transform (SQL)
    transform = PostgresOperator(
        task_id='transform_data',
        postgres_conn_id='warehouse',
        sql='sql/transform_daily.sql',
        params={'run_date': '{{ ds }}'},
    )

    # Task 4: Load
    def load_to_warehouse(**context):
        """Load transformed data to final tables"""
        ti = context['ti']
        record_count = ti.xcom_pull(task_ids='extract_data')
        print(f"Loading {record_count} records")

    load = PythonOperator(
        task_id='load_to_warehouse',
        python_callable=load_to_warehouse,
    )

    # Task 5: Quality check
    quality_check = PostgresOperator(
        task_id='quality_check',
        postgres_conn_id='warehouse',
        sql="""
            SELECT CASE 
                WHEN COUNT(*) = 0 THEN RAISE('No data loaded!')
                ELSE 'OK'
            END
            FROM fact_daily WHERE event_date = '{{ ds }}'
        """,
    )

    # Define dependencies
    extract >> validate >> transform >> load >> quality_check
```

---

## 3. Operators Deep Dive

### PythonOperator
```python
from airflow.operators.python import PythonOperator, BranchPythonOperator

def process_data(execution_date, **kwargs):
    """Access context variables"""
    print(f"Processing: {execution_date}")
    print(f"DAG Run ID: {kwargs['run_id']}")
    print(f"Task Instance: {kwargs['ti']}")
    
task = PythonOperator(
    task_id='process',
    python_callable=process_data,
    op_kwargs={'custom_param': 'value'},  # Extra keyword args
    provide_context=True,                  # Deprecated in 2.x (automatic)
)
```

### BranchPythonOperator
```python
def choose_branch(**context):
    """Route to different tasks based on conditions"""
    day_of_week = context['execution_date'].weekday()
    if day_of_week == 6:  # Sunday
        return 'full_refresh'
    return 'incremental_load'

branch = BranchPythonOperator(
    task_id='choose_strategy',
    python_callable=choose_branch,
)

# full_refresh and incremental_load are downstream tasks
branch >> [full_refresh, incremental_load]
```

### Sensors
```python
from airflow.sensors.filesystem import FileSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.sensors.external_task import ExternalTaskSensor

# Wait for file to appear
wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/data/incoming/{{ ds }}/data.csv',
    poke_interval=60,        # Check every 60 seconds
    timeout=3600,            # Fail after 1 hour
    mode='reschedule',       # Free up worker while waiting
)

# Wait for S3 object
wait_for_s3 = S3KeySensor(
    task_id='wait_for_s3',
    bucket_name='data-lake',
    bucket_key='raw/events/dt={{ ds }}/data.parquet',
    aws_conn_id='aws_default',
    mode='reschedule',
)

# Wait for another DAG to complete
wait_for_upstream = ExternalTaskSensor(
    task_id='wait_for_upstream',
    external_dag_id='upstream_dag',
    external_task_id='final_task',
    execution_delta=timedelta(hours=0),
)
```

---

## 4. Templating (Jinja)

Airflow uses Jinja2 templates for dynamic values:

```python
# Available template variables
"""
{{ ds }}                  → '2024-03-15'  (execution date, YYYY-MM-DD)
{{ ds_nodash }}           → '20240315'
{{ ts }}                  → '2024-03-15T06:00:00+00:00'
{{ execution_date }}      → datetime object
{{ prev_ds }}             → previous execution date
{{ next_ds }}             → next execution date
{{ dag_run.conf }}        → trigger conf (manual triggers)
{{ params.my_param }}     → DAG params
{{ var.value.my_var }}    → Airflow Variable
{{ conn.my_conn.host }}   → Connection details
"""

# SQL template file (sql/transform_daily.sql)
"""
DELETE FROM fact_events WHERE event_date = '{{ ds }}';

INSERT INTO fact_events
SELECT * FROM staging_events
WHERE event_date = '{{ ds }}'
AND processed = FALSE;
"""
```

---

## 5. XComs — Cross-Task Communication

```python
# Push XCom (implicit: return value)
def extract(**context):
    data = fetch_data()
    return {'record_count': len(data), 'file_path': '/tmp/data.parquet'}

# Push XCom (explicit)
def extract_explicit(**context):
    ti = context['ti']
    ti.xcom_push(key='schema_version', value='v2')

# Pull XCom
def transform(**context):
    ti = context['ti']
    
    # Pull return value (key='return_value' by default)
    extract_result = ti.xcom_pull(task_ids='extract')
    record_count = extract_result['record_count']
    
    # Pull specific key
    schema = ti.xcom_pull(task_ids='extract', key='schema_version')

# XCom in templates
load = BashOperator(
    task_id='load',
    bash_command='load_data.sh {{ ti.xcom_pull(task_ids="extract")["file_path"] }}',
)
```

**Warning**: XComs are stored in the metadata DB. Keep them small (< 48KB). For large data, pass file paths or references.

---

## 6. Connections & Variables

### Connections (UI or CLI)
```bash
# Add via CLI
airflow connections add 'warehouse' \
    --conn-type postgres \
    --conn-host localhost \
    --conn-port 5432 \
    --conn-login admin \
    --conn-password secret \
    --conn-schema analytics

# Use in code
from airflow.hooks.postgres_hook import PostgresHook

hook = PostgresHook(postgres_conn_id='warehouse')
df = hook.get_pandas_df("SELECT * FROM table LIMIT 10")
records = hook.get_records("SELECT count(*) FROM table")
hook.run("INSERT INTO table VALUES (%s, %s)", parameters=('a', 'b'))
```

### Variables
```python
from airflow.models import Variable

# Set (UI, CLI, or code)
Variable.set('env', 'production')
Variable.set('config', {'key': 'value'}, serialize_json=True)

# Get
env = Variable.get('env')
config = Variable.get('config', deserialize_json=True)

# In templates (no DB hit per task — use this way)
# {{ var.value.env }}
# {{ var.json.config.key }}
```

---

## 7. Best Practices

### DAG Design
```python
# ✅ DO: Use task groups for organization
from airflow.utils.task_group import TaskGroup

with DAG(...) as dag:
    with TaskGroup('extract') as extract_group:
        extract_users = PythonOperator(...)
        extract_orders = PythonOperator(...)
    
    with TaskGroup('transform') as transform_group:
        transform_users = PythonOperator(...)
        transform_orders = PythonOperator(...)
    
    extract_group >> transform_group

# ✅ DO: Make tasks idempotent
# ✅ DO: Use execution_date for processing (not current time)
# ✅ DO: Keep tasks atomic (one logical operation)
# ❌ DON'T: Pass large data via XCom
# ❌ DON'T: Use top-level code that runs on import
# ❌ DON'T: Hardcode dates — use {{ ds }}
```

### File Structure
```
dags/
├── daily_etl.py
├── weekly_reports.py
├── sql/
│   ├── transform_daily.sql
│   └── quality_checks.sql
├── utils/
│   ├── __init__.py
│   └── helpers.py
└── config/
    └── pipeline_config.yaml
```

---

## 8. Running Airflow Locally

```bash
# Docker Compose (recommended)
curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.8.0/docker-compose.yaml'

# Initialize
docker compose up airflow-init

# Start all services
docker compose up -d

# Access UI: http://localhost:8080 (airflow/airflow)
```

---

## Key Takeaways
- DAGs = Python code defining workflow dependencies
- Operators are task templates (Python, SQL, Bash, Sensor)
- Use Jinja templates for dynamic dates and parameters
- XComs for small cross-task data; file paths for large data
- Always use `{{ ds }}` for date-based processing (not `datetime.now()`)
- Make every task idempotent and atomic

## Tomorrow
**Day 16**: Airflow Advanced — Dynamic DAGs, custom operators, testing strategies, and production patterns.
