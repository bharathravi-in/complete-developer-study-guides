# Day 16: Airflow Advanced — Dynamic DAGs, TaskFlow & Production

## Learning Objectives
- Build dynamic DAGs from configuration
- Master the TaskFlow API (@task decorator)
- Implement testing, monitoring, and deployment patterns
- Handle complex scheduling and dependencies

---

## 1. TaskFlow API (Modern Airflow)

```python
from airflow.decorators import dag, task
from airflow.models import Variable
from datetime import datetime, timedelta
import json

@dag(
    schedule="0 6 * * *",  # Daily at 6 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        "email_on_failure": True,
    },
    tags=["production", "etl"],
)
def sales_pipeline():
    """Sales ETL pipeline using TaskFlow API."""
    
    @task()
    def extract(source: str) -> dict:
        """Extract data from source system."""
        import pandas as pd
        df = pd.read_csv(source)
        return {"records": len(df), "path": source}
    
    @task()
    def validate(extract_result: dict) -> dict:
        """Validate extracted data quality."""
        if extract_result["records"] == 0:
            raise ValueError("No records extracted!")
        return extract_result
    
    @task()
    def transform(validated: dict) -> str:
        """Transform and write to staging."""
        import pandas as pd
        df = pd.read_csv(validated["path"])
        df["amount"] = df["quantity"] * df["unit_price"]
        output_path = "/data/staging/sales_transformed.parquet"
        df.to_parquet(output_path)
        return output_path
    
    @task()
    def load(file_path: str):
        """Load to data warehouse."""
        from sqlalchemy import create_engine
        import pandas as pd
        engine = create_engine(Variable.get("warehouse_conn"))
        df = pd.read_parquet(file_path)
        df.to_sql("fact_sales", engine, if_exists="append", index=False)
    
    # DAG flow defined by function calls
    extracted = extract("/data/raw/sales.csv")
    validated = validate(extracted)
    transformed = transform(validated)
    load(transformed)

sales_pipeline()
```

---

## 2. Dynamic DAGs

### From Configuration

```python
# dags/dynamic_pipeline.py
import yaml
from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
from datetime import datetime

# Load pipeline configs
with open("/opt/airflow/config/pipelines.yaml") as f:
    pipelines = yaml.safe_load(f)

def create_pipeline_dag(pipeline_config):
    """Factory function to create DAG from config."""
    
    @dag(
        dag_id=f"pipeline_{pipeline_config['name']}",
        schedule=pipeline_config.get("schedule", "@daily"),
        start_date=datetime(2024, 1, 1),
        catchup=False,
        tags=pipeline_config.get("tags", []),
    )
    def pipeline():
        @task()
        def extract():
            source = pipeline_config["source"]
            # Extract based on source type
            if source["type"] == "postgres":
                return extract_postgres(source)
            elif source["type"] == "api":
                return extract_api(source)
            elif source["type"] == "s3":
                return extract_s3(source)
        
        @task()
        def transform(data):
            for t in pipeline_config.get("transforms", []):
                data = apply_transform(data, t)
            return data
        
        @task()
        def load(data):
            target = pipeline_config["target"]
            load_to_target(data, target)
        
        raw = extract()
        transformed = transform(raw)
        load(transformed)
    
    return pipeline()

# Generate DAGs dynamically
for config in pipelines:
    globals()[f"pipeline_{config['name']}"] = create_pipeline_dag(config)
```

```yaml
# config/pipelines.yaml
- name: customer_sync
  schedule: "*/30 * * * *"
  source:
    type: postgres
    connection: source_db
    table: customers
    incremental_key: updated_at
  transforms:
    - type: deduplicate
      key: customer_id
    - type: standardize
      columns: [email, phone]
  target:
    type: delta
    path: /lake/silver/customers
  tags: [customers, sync]

- name: event_processing
  schedule: "@hourly"
  source:
    type: s3
    bucket: raw-events
    prefix: events/
  transforms:
    - type: flatten_json
    - type: add_timestamp
  target:
    type: delta
    path: /lake/bronze/events
  tags: [events, bronze]
```

### Dynamic Task Mapping (Airflow 2.3+)

```python
@dag(schedule="@daily", start_date=datetime(2024, 1, 1))
def parallel_etl():
    
    @task()
    def get_tables() -> list[str]:
        """Get list of tables to process."""
        return ["orders", "customers", "products", "inventory"]
    
    @task()
    def process_table(table_name: str) -> dict:
        """Process each table in parallel."""
        # This runs as separate task instances
        record_count = run_etl(table_name)
        return {"table": table_name, "records": record_count}
    
    @task()
    def summarize(results: list[dict]):
        """Combine all results."""
        total = sum(r["records"] for r in results)
        print(f"Processed {total} total records across {len(results)} tables")
    
    tables = get_tables()
    results = process_table.expand(table_name=tables)  # Dynamic fan-out
    summarize(results)

parallel_etl()
```

---

## 3. Task Groups & Organization

```python
from airflow.decorators import dag, task, task_group
from airflow.utils.task_group import TaskGroup

@dag(schedule="@daily", start_date=datetime(2024, 1, 1))
def organized_pipeline():
    
    @task_group(group_id="extract")
    def extract_sources():
        @task()
        def extract_orders():
            return "orders_data"
        
        @task()
        def extract_customers():
            return "customers_data"
        
        @task()
        def extract_products():
            return "products_data"
        
        return extract_orders(), extract_customers(), extract_products()
    
    @task_group(group_id="transform")
    def transform_data(orders, customers, products):
        @task()
        def join_and_enrich(orders, customers):
            return "enriched_data"
        
        @task()
        def aggregate(enriched):
            return "aggregated_data"
        
        enriched = join_and_enrich(orders, customers)
        return aggregate(enriched)
    
    @task_group(group_id="load")
    def load_targets(data):
        @task()
        def load_warehouse(data):
            pass
        
        @task()
        def load_cache(data):
            pass
        
        load_warehouse(data)
        load_cache(data)
    
    sources = extract_sources()
    transformed = transform_data(*sources)
    load_targets(transformed)

organized_pipeline()
```

---

## 4. Sensors & Triggers

```python
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.external_task import ExternalTaskSensor
from airflow.sensors.sql import SqlSensor
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

@dag(schedule="@daily", start_date=datetime(2024, 1, 1))
def sensor_pipeline():
    
    # Wait for file to appear
    wait_for_file = FileSensor(
        task_id="wait_for_data",
        filepath="/data/incoming/{{ ds }}/sales.csv",
        poke_interval=60,  # Check every 60 seconds
        timeout=3600,      # Give up after 1 hour
        mode="reschedule", # Free up worker slot while waiting
    )
    
    # Wait for upstream DAG to complete
    wait_for_upstream = ExternalTaskSensor(
        task_id="wait_for_ingestion",
        external_dag_id="data_ingestion",
        external_task_id="complete",
        execution_delta=timedelta(hours=1),
    )
    
    # Wait for data in database
    wait_for_records = SqlSensor(
        task_id="wait_for_records",
        conn_id="warehouse",
        sql="SELECT COUNT(*) FROM staging.orders WHERE date = '{{ ds }}'",
        success=lambda count: count > 0,
        poke_interval=120,
    )
    
    # Wait for S3 object
    wait_for_s3 = S3KeySensor(
        task_id="wait_for_s3",
        bucket_key="raw/events/{{ ds }}/_SUCCESS",
        bucket_name="datalake",
        aws_conn_id="aws_default",
    )
    
    @task()
    def process():
        pass
    
    [wait_for_file, wait_for_upstream] >> wait_for_records >> process()
```

---

## 5. Custom Operators & Hooks

```python
# plugins/operators/spark_delta_operator.py
from airflow.models import BaseOperator
from airflow.providers.apache.spark.hooks.spark_submit import SparkSubmitHook

class SparkDeltaOperator(BaseOperator):
    """Custom operator to run Spark Delta Lake jobs."""
    
    template_fields = ["source_path", "target_path", "execution_date"]
    
    def __init__(
        self,
        source_path: str,
        target_path: str,
        transform_type: str,
        execution_date: str = "{{ ds }}",
        spark_conn_id: str = "spark_default",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.source_path = source_path
        self.target_path = target_path
        self.transform_type = transform_type
        self.execution_date = execution_date
        self.spark_conn_id = spark_conn_id
    
    def execute(self, context):
        hook = SparkSubmitHook(
            conn_id=self.spark_conn_id,
            application="/opt/airflow/spark_jobs/delta_transform.py",
            application_args=[
                "--source", self.source_path,
                "--target", self.target_path,
                "--transform", self.transform_type,
                "--date", self.execution_date,
            ],
            conf={
                "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
            },
        )
        hook.submit()
```

---

## 6. Testing DAGs

```python
# tests/test_dags.py
import pytest
from airflow.models import DagBag
from datetime import datetime

@pytest.fixture
def dagbag():
    return DagBag(dag_folder="/opt/airflow/dags", include_examples=False)

class TestDAGIntegrity:
    def test_no_import_errors(self, dagbag):
        """All DAGs should import without errors."""
        assert len(dagbag.import_errors) == 0, f"Import errors: {dagbag.import_errors}"
    
    def test_dag_count(self, dagbag):
        """Expected number of DAGs are loaded."""
        assert len(dagbag.dags) >= 5
    
    def test_no_cycles(self, dagbag):
        """No circular dependencies."""
        for dag_id, dag in dagbag.dags.items():
            assert not dag.test_cycle(), f"Cycle detected in {dag_id}"
    
    def test_default_args(self, dagbag):
        """All DAGs have required default args."""
        for dag_id, dag in dagbag.dags.items():
            assert dag.default_args.get("retries", 0) >= 1
            assert "retry_delay" in dag.default_args

class TestSalesPipeline:
    def test_task_count(self, dagbag):
        dag = dagbag.get_dag("sales_pipeline")
        assert len(dag.tasks) == 4
    
    def test_task_dependencies(self, dagbag):
        dag = dagbag.get_dag("sales_pipeline")
        extract = dag.get_task("extract")
        load = dag.get_task("load")
        assert "transform" in [t.task_id for t in load.upstream_list]
    
    def test_dag_run(self, dagbag):
        """Test actual execution with test data."""
        dag = dagbag.get_dag("sales_pipeline")
        dag.test(execution_date=datetime(2024, 1, 1))
```

---

## 7. Monitoring & Alerting

```python
from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
from airflow.callbacks import on_failure_callback

def slack_alert(context):
    """Send Slack alert on task failure."""
    from airflow.providers.slack.hooks.slack_webhook import SlackWebhookHook
    
    task_instance = context.get("task_instance")
    hook = SlackWebhookHook(slack_webhook_conn_id="slack")
    hook.send(
        text=f"🚨 Task Failed!\n"
             f"DAG: {task_instance.dag_id}\n"
             f"Task: {task_instance.task_id}\n"
             f"Execution: {context['execution_date']}\n"
             f"Log: {task_instance.log_url}"
    )

@dag(
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    on_failure_callback=slack_alert,  # DAG-level callback
    sla_miss_callback=slack_alert,
)
def monitored_pipeline():
    
    @task(
        sla=timedelta(hours=2),  # Alert if task takes > 2 hours
        on_failure_callback=slack_alert,
        execution_timeout=timedelta(hours=3),  # Kill if > 3 hours
    )
    def long_running_task():
        pass
    
    long_running_task()
```

---

## Interview Questions

### Beginner
1. **What is a DAG in Airflow?** Directed Acyclic Graph — defines task dependencies. Directed (A→B), Acyclic (no loops). Tasks execute in dependency order.
2. **What's the difference between schedule_interval and timetable?** schedule_interval uses cron/timedelta. Timetables (2.2+) support complex schedules (business days, custom calendars).
3. **What is catchup in Airflow?** When enabled, Airflow backfills all missed DAG runs from start_date. Disable with `catchup=False` for pipelines that only need current data.

### Intermediate
4. **How do you handle idempotency in Airflow?** Use execution_date (logical date) in queries, overwrite partitions instead of append, use MERGE operations, make tasks rerunnable.
5. **Explain dynamic task mapping.** `.expand()` creates task instances at runtime based on output of upstream task. Enables parallel processing of unknown-length lists.
6. **When to use sensor vs trigger?** Sensors: simple polling. Triggers (2.6+, Deferrable operators): suspend task, free worker slot, resume on event. Triggers for long waits (hours).

### Advanced
7. **How do you handle DAG dependencies across teams?** ExternalTaskSensor (tight coupling), Datasets (Airflow 2.4+ — data-aware scheduling), API triggers, message queues. Prefer Datasets for loose coupling.
8. **Design Airflow deployment for 500+ DAGs.** Kubernetes executor (scale to zero), CeleryExecutor for steady load, separate scheduler from webserver, DAG serialization, external metadata DB (CloudSQL), GitSync for DAG deployment, resource pools for isolation.
9. **How do you test and deploy DAGs safely?** Unit tests (import, structure, task logic), integration tests (with test connections), staging environment, CI/CD with `dag.test()`, blue-green deployment, feature flags in Variables.

---

## Hands-On Exercise
1. Build a dynamic DAG from YAML configuration
2. Implement TaskFlow API pipeline with XCom passing
3. Add sensors (wait for file, wait for upstream DAG)
4. Write DAG tests (structure, dependencies, execution)
5. Set up alerting with failure callbacks
6. Create a custom operator for your specific use case
