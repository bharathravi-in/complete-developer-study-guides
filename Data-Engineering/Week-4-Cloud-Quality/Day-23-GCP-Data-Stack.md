# Day 23: GCP Data Engineering Stack

## Learning Objectives
- Master BigQuery for analytics and ML
- Build streaming pipelines with Dataflow (Apache Beam)
- Use Pub/Sub for messaging and Cloud Composer for orchestration
- Design data architectures on GCP

---

## 1. BigQuery Deep Dive

```sql
-- Partitioned + Clustered table (best practice)
CREATE TABLE `project.analytics.events`
(
    event_id STRING NOT NULL,
    user_id STRING,
    event_type STRING,
    properties JSON,
    amount NUMERIC,
    event_time TIMESTAMP,
    region STRING
)
PARTITION BY DATE(event_time)
CLUSTER BY region, event_type
OPTIONS (
    partition_expiration_days = 365,
    require_partition_filter = TRUE,
    description = 'User events partitioned by day, clustered by region and type'
);

-- Streaming insert (real-time)
-- Via API or client library (see Python below)

-- Scheduled query
CREATE SCHEDULED QUERY `daily_aggregation`
OPTIONS (schedule = 'every 24 hours', destination_table = 'analytics.daily_summary')
AS
SELECT
    DATE(event_time) AS event_date,
    region,
    event_type,
    COUNT(*) AS event_count,
    SUM(amount) AS total_amount,
    COUNT(DISTINCT user_id) AS unique_users
FROM `project.analytics.events`
WHERE DATE(event_time) = CURRENT_DATE() - 1
GROUP BY 1, 2, 3;

-- Materialized view (auto-refreshed, auto-used by optimizer)
CREATE MATERIALIZED VIEW `project.analytics.mv_hourly_events` AS
SELECT
    TIMESTAMP_TRUNC(event_time, HOUR) AS hour,
    region,
    COUNT(*) AS events,
    SUM(amount) AS revenue
FROM `project.analytics.events`
GROUP BY 1, 2;

-- BigQuery ML
CREATE OR REPLACE MODEL `project.analytics.churn_model`
OPTIONS (
    model_type = 'BOOSTED_TREE_CLASSIFIER',
    input_label_cols = ['churned'],
    data_split_method = 'AUTO_SPLIT',
    max_iterations = 50
) AS
SELECT
    user_id,
    total_orders,
    avg_order_value,
    days_since_last_order,
    churned
FROM `project.analytics.customer_features`;

-- Predict
SELECT * FROM ML.PREDICT(
    MODEL `project.analytics.churn_model`,
    (SELECT * FROM `project.analytics.new_customers`)
);
```

### BigQuery Python Client

```python
from google.cloud import bigquery
import pandas as pd

client = bigquery.Client(project='my-project')

# Query
query = """
    SELECT region, SUM(amount) as revenue
    FROM `project.analytics.events`
    WHERE DATE(event_time) = @date
    GROUP BY region
"""
job_config = bigquery.QueryJobConfig(
    query_parameters=[
        bigquery.ScalarQueryParameter("date", "DATE", "2024-01-15"),
    ]
)
df = client.query(query, job_config=job_config).to_dataframe()

# Load data
table_ref = client.dataset('analytics').table('events')
job_config = bigquery.LoadJobConfig(
    source_format=bigquery.SourceFormat.PARQUET,
    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
)
load_job = client.load_table_from_uri(
    'gs://datalake/silver/events/*.parquet',
    table_ref,
    job_config=job_config,
)
load_job.result()  # Wait for completion

# Streaming insert
rows = [
    {"event_id": "e1", "user_id": "u1", "amount": 99.99, "event_time": "2024-01-15T10:00:00"},
    {"event_id": "e2", "user_id": "u2", "amount": 49.99, "event_time": "2024-01-15T10:01:00"},
]
errors = client.insert_rows_json(table_ref, rows)
if errors:
    print(f"Insert errors: {errors}")
```

---

## 2. Cloud Dataflow (Apache Beam)

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, GoogleCloudOptions
from apache_beam.io.gcp.bigquery import WriteToBigQuery
import json

# Pipeline options
options = PipelineOptions([
    '--runner=DataflowRunner',
    '--project=my-project',
    '--region=us-central1',
    '--temp_location=gs://temp-bucket/tmp/',
    '--staging_location=gs://temp-bucket/staging/',
    '--machine_type=n1-standard-4',
    '--num_workers=4',
    '--max_num_workers=20',
    '--autoscaling_algorithm=THROUGHPUT_BASED',
])

# Batch pipeline
with beam.Pipeline(options=options) as p:
    (
        p
        | 'Read' >> beam.io.ReadFromText('gs://datalake/raw/events/*.json')
        | 'Parse' >> beam.Map(json.loads)
        | 'Filter' >> beam.Filter(lambda x: x.get('amount', 0) > 0)
        | 'Transform' >> beam.Map(lambda x: {
            'event_id': x['event_id'],
            'user_id': x['user_id'],
            'amount': float(x['amount']),
            'event_date': x['timestamp'][:10],
            'region': x.get('region', 'unknown').upper(),
        })
        | 'Write' >> WriteToBigQuery(
            'project:analytics.events',
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
        )
    )

# Streaming pipeline (Pub/Sub → BigQuery)
with beam.Pipeline(options=options) as p:
    (
        p
        | 'Read PubSub' >> beam.io.ReadFromPubSub(topic='projects/my-project/topics/events')
        | 'Parse JSON' >> beam.Map(json.loads)
        | 'Add Timestamp' >> beam.Map(lambda x: beam.window.TimestampedValue(
            x, x['timestamp']
        ))
        | 'Window' >> beam.WindowInto(beam.window.FixedWindows(300))  # 5-min windows
        | 'Aggregate' >> beam.CombinePerKey(sum)
        | 'Write BQ' >> WriteToBigQuery('project:analytics.windowed_events')
    )
```

---

## 3. Cloud Pub/Sub

```python
from google.cloud import pubsub_v1
import json

# Publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path('my-project', 'events')

def publish_event(event: dict):
    data = json.dumps(event).encode('utf-8')
    future = publisher.publish(
        topic_path,
        data,
        event_type=event['type'],  # Attribute for filtering
        region=event['region'],
    )
    return future.result()

# Subscriber with filtering
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path('my-project', 'events-us-sub')

# Create subscription with filter
subscriber.create_subscription(
    request={
        'name': subscription_path,
        'topic': topic_path,
        'filter': 'attributes.region = "US"',  # Only US events
        'ack_deadline_seconds': 60,
        'retry_policy': {
            'minimum_backoff': {'seconds': 10},
            'maximum_backoff': {'seconds': 600},
        },
    }
)

# Pull messages
def callback(message):
    event = json.loads(message.data.decode('utf-8'))
    process_event(event)
    message.ack()

streaming_pull = subscriber.subscribe(subscription_path, callback=callback)
streaming_pull.result()  # Block
```

---

## 4. Cloud Composer (Managed Airflow)

```python
# DAG for GCP data pipeline
from airflow.decorators import dag, task
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryInsertJobOperator,
    BigQueryCheckOperator,
)
from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from datetime import datetime

@dag(schedule="@daily", start_date=datetime(2024, 1, 1), catchup=False)
def gcp_data_pipeline():
    
    # Wait for data in GCS
    wait_for_data = GCSObjectExistenceSensor(
        task_id='wait_for_data',
        bucket='datalake-raw',
        object=f'events/{{{{ ds }}}}/data.parquet',
        timeout=7200,
    )
    
    # Run Dataflow job
    process_data = DataflowStartFlexTemplateOperator(
        task_id='process_events',
        body={
            'launchParameter': {
                'containerSpecGcsPath': 'gs://templates/event-processor',
                'jobName': f'event-processing-{{{{ ds_nodash }}}}',
                'parameters': {
                    'input': f'gs://datalake-raw/events/{{{{ ds }}}}/',
                    'output': 'project:analytics.events',
                },
            }
        },
        location='us-central1',
    )
    
    # Run BigQuery transformation
    transform = BigQueryInsertJobOperator(
        task_id='transform_events',
        configuration={
            'query': {
                'query': """
                    INSERT INTO `project.analytics.daily_summary`
                    SELECT DATE(event_time) as date, region, COUNT(*) as events
                    FROM `project.analytics.events`
                    WHERE DATE(event_time) = '{{ ds }}'
                    GROUP BY 1, 2
                """,
                'useLegacySql': False,
            }
        },
    )
    
    # Quality check
    quality_check = BigQueryCheckOperator(
        task_id='quality_check',
        sql=f"SELECT COUNT(*) > 0 FROM `project.analytics.daily_summary` WHERE date = '{{{{ ds }}}}'",
        use_legacy_sql=False,
    )
    
    wait_for_data >> process_data >> transform >> quality_check

gcp_data_pipeline()
```

---

## 5. GCS & Dataproc

```python
from google.cloud import storage, dataproc_v1

# GCS operations
gcs = storage.Client()
bucket = gcs.bucket('datalake-prod')

# Upload with metadata
blob = bucket.blob('bronze/events/2024/01/15/data.parquet')
blob.upload_from_filename('local_data.parquet')
blob.metadata = {'source': 'api', 'pipeline': 'v2'}
blob.patch()

# Dataproc (managed Spark)
dataproc = dataproc_v1.ClusterControllerClient()

# Create cluster
cluster_config = {
    'project_id': 'my-project',
    'cluster_name': 'etl-cluster',
    'config': {
        'master_config': {'num_instances': 1, 'machine_type_uri': 'n1-standard-8'},
        'worker_config': {'num_instances': 4, 'machine_type_uri': 'n1-standard-4'},
        'software_config': {
            'image_version': '2.1-debian11',
            'properties': {
                'spark:spark.sql.adaptive.enabled': 'true',
                'dataproc:dataproc.allow.zero.workers': 'true',
            },
        },
        'lifecycle_config': {
            'idle_delete_ttl': {'seconds': 1800},  # Auto-delete after 30min idle
        },
    },
}

operation = dataproc.create_cluster(
    request={'project_id': 'my-project', 'region': 'us-central1', 'cluster': cluster_config}
)
operation.result()  # Wait for cluster creation

# Submit Spark job
job_client = dataproc_v1.JobControllerClient()
job = {
    'placement': {'cluster_name': 'etl-cluster'},
    'pyspark_job': {
        'main_python_file_uri': 'gs://scripts/transform.py',
        'args': ['--date', '2024-01-15'],
        'properties': {'spark.sql.shuffle.partitions': '100'},
    },
}
job_client.submit_job(project_id='my-project', region='us-central1', job=job)
```

---

## Interview Questions

### Beginner
1. **What is BigQuery and how is it different from traditional warehouses?** Serverless, no infrastructure management, auto-scales. Columnar storage (Capacitor format). Pay per TB scanned (on-demand) or per slot (flat-rate). Integrated ML.
2. **What is Pub/Sub?** Fully managed messaging service. Pub/Sub decouples publishers from subscribers. At-least-once delivery, message ordering per key, exactly-once with Dataflow.
3. **When to use Dataflow vs Dataproc?** Dataflow: serverless, auto-scaling, unified batch+stream (Beam). Dataproc: managed Spark/Hadoop, lift-and-shift existing jobs, more control over cluster.

### Intermediate
4. **How do you optimize BigQuery costs?** Partition + cluster tables, avoid SELECT *, use cached results, set require_partition_filter, monitor with INFORMATION_SCHEMA, use flat-rate for predictable workloads, archive to long-term storage.
5. **Explain BigQuery slots.** Slots are units of computational capacity. On-demand: up to 2000 slots shared pool. Flat-rate: reserved slots guaranteed. More slots = faster queries (parallelism). Monitor slot utilization to right-size.
6. **How does Dataflow autoscaling work?** Based on backlog (streaming) or data volume (batch). Adds workers when backlog grows, removes when caught up. Configurable min/max workers. Horizontal scaling up to max_num_workers.

### Advanced
7. **Design a real-time analytics pipeline on GCP.** Pub/Sub (ingestion) → Dataflow streaming (processing, windowing) → BigQuery (storage + analytics). Cloud Composer orchestrates batch transforms. Looker Studio for dashboards. Monitoring with Cloud Monitoring.
8. **How do you handle exactly-once in Pub/Sub + Dataflow?** Pub/Sub guarantees at-least-once. Dataflow provides exactly-once via: deterministic record IDs, checkpointing, idempotent writes to BigQuery (via Storage Write API in COMMITTED mode).
9. **Compare GCP data stack to AWS.** BigQuery ≈ Athena+Redshift (but serverless, integrated ML). Pub/Sub ≈ Kinesis/SQS. Dataflow ≈ Glue/EMR (but Beam-based, unified). Composer ≈ MWAA. GCS ≈ S3. GCP advantage: simplicity, BigQuery ML. AWS advantage: more services, larger ecosystem.

---

## Hands-On Exercise
1. Create BigQuery dataset with partitioned + clustered table
2. Build Dataflow pipeline (batch: GCS → BigQuery)
3. Set up Pub/Sub topic + subscription with filtering
4. Create Cloud Composer DAG orchestrating BQ + Dataflow
5. Run BigQuery ML model (classification or forecasting)
6. Compare query costs with and without partitioning
