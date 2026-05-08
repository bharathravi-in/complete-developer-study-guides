# Day 22: AWS Data Engineering Stack

## Learning Objectives
- Master core AWS data services (S3, Glue, Athena, Kinesis, EMR)
- Design data lake architectures on AWS
- Implement governance with Lake Formation
- Optimize cost and performance

---

## 1. Amazon S3 — Storage Foundation

```python
import boto3
from datetime import datetime

s3 = boto3.client('s3')

# Create bucket with lifecycle
s3.create_bucket(Bucket='datalake-prod', CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})

# Lifecycle rules (cost optimization)
s3.put_bucket_lifecycle_configuration(
    Bucket='datalake-prod',
    LifecycleConfiguration={
        'Rules': [
            {
                'ID': 'bronze-to-glacier',
                'Filter': {'Prefix': 'bronze/'},
                'Status': 'Enabled',
                'Transitions': [
                    {'Days': 30, 'StorageClass': 'STANDARD_IA'},
                    {'Days': 90, 'StorageClass': 'GLACIER'},
                ],
                'Expiration': {'Days': 365},
            },
            {
                'ID': 'keep-gold-hot',
                'Filter': {'Prefix': 'gold/'},
                'Status': 'Enabled',
                'Transitions': [
                    {'Days': 90, 'StorageClass': 'STANDARD_IA'},
                ],
            },
        ]
    }
)

# Optimal partitioning for queries
# s3://datalake-prod/silver/events/year=2024/month=01/day=15/hour=10/data.parquet
def write_partitioned(df, table_name, partition_cols=['year', 'month', 'day']):
    """Write DataFrame partitioned to S3."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    
    table = pa.Table.from_pandas(df)
    pq.write_to_dataset(
        table,
        root_path=f's3://datalake-prod/silver/{table_name}/',
        partition_cols=partition_cols,
        compression='snappy',
    )
```

### Storage Classes
| Class | Use Case | Cost (GB/mo) | Retrieval |
|-------|----------|--------------|-----------|
| Standard | Hot data, frequent access | $0.023 | Immediate |
| Standard-IA | Infrequent access (>30 days) | $0.0125 | Immediate |
| Glacier Instant | Archive with instant access | $0.004 | Immediate |
| Glacier Flexible | Archive, hours retrieval | $0.0036 | 3-12 hours |
| Glacier Deep | Cold archive | $0.00099 | 12-48 hours |

---

## 2. AWS Glue — ETL & Catalog

```python
# Glue ETL Job (PySpark)
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'source_path', 'target_path'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read from Glue Data Catalog
dynamic_frame = glueContext.create_dynamic_frame.from_catalog(
    database="raw_db",
    table_name="orders",
    transformation_ctx="source"
)

# Transform
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as F

df = dynamic_frame.toDF()
df_transformed = (
    df.filter(F.col("order_id").isNotNull())
    .withColumn("total", F.col("quantity") * F.col("price"))
    .withColumn("order_date", F.to_date("order_date"))
)

# Write to S3 in Parquet format
output = DynamicFrame.fromDF(df_transformed, glueContext, "output")
glueContext.write_dynamic_frame.from_options(
    frame=output,
    connection_type="s3",
    connection_options={
        "path": args['target_path'],
        "partitionKeys": ["year", "month"]
    },
    format="parquet",
    format_options={"compression": "snappy"},
)

job.commit()
```

### Glue Crawler (Auto-discover Schema)
```python
import boto3

glue = boto3.client('glue')

# Create crawler to discover schema from S3
glue.create_crawler(
    Name='silver-orders-crawler',
    Role='GlueServiceRole',
    DatabaseName='silver_db',
    Targets={
        'S3Targets': [
            {'Path': 's3://datalake-prod/silver/orders/', 'Exclusions': ['_tmp/**']},
        ]
    },
    SchemaChangePolicy={
        'UpdateBehavior': 'UPDATE_IN_DATABASE',
        'DeleteBehavior': 'LOG',
    },
    Schedule='cron(0 */6 * * ? *)',  # Every 6 hours
    Configuration='{"Version":1.0,"CrawlerOutput":{"Partitions":{"AddOrUpdateBehavior":"InheritFromTable"}}}'
)

# Run crawler
glue.start_crawler(Name='silver-orders-crawler')
```

---

## 3. Amazon Athena — Serverless SQL

```sql
-- Create external table pointing to S3
CREATE EXTERNAL TABLE silver_db.orders (
    order_id STRING,
    customer_id STRING,
    amount DOUBLE,
    status STRING
)
PARTITIONED BY (year INT, month INT, day INT)
STORED AS PARQUET
LOCATION 's3://datalake-prod/silver/orders/'
TBLPROPERTIES ('parquet.compression'='SNAPPY');

-- Load partitions
MSCK REPAIR TABLE silver_db.orders;

-- Query with partition pruning ($5/TB scanned)
SELECT 
    customer_id,
    SUM(amount) AS total_spent,
    COUNT(*) AS order_count
FROM silver_db.orders
WHERE year = 2024 AND month = 1  -- Partition pruning!
  AND status = 'COMPLETED'
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 100;

-- CTAS (Create Table As Select) for optimization
CREATE TABLE gold_db.daily_revenue
WITH (
    format = 'PARQUET',
    parquet_compression = 'SNAPPY',
    partitioned_by = ARRAY['year', 'month'],
    external_location = 's3://datalake-prod/gold/daily_revenue/'
) AS
SELECT 
    date,
    region,
    SUM(amount) AS revenue,
    year, month
FROM silver_db.orders
GROUP BY date, region, year, month;
```

---

## 4. Amazon Kinesis — Real-Time

```python
import boto3
import json
from datetime import datetime

# Kinesis Data Streams — real-time ingestion
kinesis = boto3.client('kinesis')

# Produce events
def send_event(stream_name: str, event: dict):
    kinesis.put_record(
        StreamName=stream_name,
        Data=json.dumps(event).encode('utf-8'),
        PartitionKey=event['user_id'],  # Determines shard
    )

# Batch produce (more efficient)
def send_batch(stream_name: str, events: list[dict]):
    records = [
        {
            'Data': json.dumps(e).encode('utf-8'),
            'PartitionKey': e['user_id'],
        }
        for e in events
    ]
    kinesis.put_records(StreamName=stream_name, Records=records)

# Kinesis Data Firehose — zero-code delivery to S3/Redshift
firehose = boto3.client('firehose')
firehose.create_delivery_stream(
    DeliveryStreamName='events-to-s3',
    S3DestinationConfiguration={
        'RoleARN': 'arn:aws:iam::123456789:role/FirehoseRole',
        'BucketARN': 'arn:aws:s3:::datalake-prod',
        'Prefix': 'bronze/events/year=!{timestamp:yyyy}/month=!{timestamp:MM}/day=!{timestamp:dd}/',
        'ErrorOutputPrefix': 'errors/events/',
        'BufferingHints': {'SizeInMBs': 128, 'IntervalInSeconds': 300},
        'CompressionFormat': 'GZIP',
    },
)
```

---

## 5. AWS EMR — Managed Spark

```python
import boto3

emr = boto3.client('emr')

# Launch EMR cluster
cluster = emr.run_job_flow(
    Name='data-pipeline-cluster',
    ReleaseLabel='emr-7.0.0',
    Applications=[
        {'Name': 'Spark'},
        {'Name': 'Hive'},
        {'Name': 'Delta'},
    ],
    Instances={
        'MasterInstanceType': 'm5.2xlarge',
        'SlaveInstanceType': 'r5.4xlarge',
        'InstanceCount': 5,
        'KeepJobFlowAliveWhenNoSteps': False,
        'Ec2SubnetId': 'subnet-xxx',
    },
    Steps=[{
        'Name': 'Spark ETL',
        'ActionOnFailure': 'TERMINATE_CLUSTER',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                'spark-submit',
                '--deploy-mode', 'cluster',
                '--conf', 'spark.sql.extensions=io.delta.sql.DeltaSparkSessionExtension',
                's3://scripts/etl_job.py',
                '--date', '2024-01-15',
            ],
        },
    }],
    Configurations=[{
        'Classification': 'spark-defaults',
        'Properties': {
            'spark.sql.adaptive.enabled': 'true',
            'spark.dynamicAllocation.enabled': 'true',
        },
    }],
    LogUri='s3://logs/emr/',
    ServiceRole='EMR_DefaultRole',
    JobFlowRole='EMR_EC2_DefaultRole',
)
```

---

## 6. Lake Formation — Governance

```python
# Grant fine-grained permissions
lakeformation = boto3.client('lakeformation')

# Grant database access to analyst role
lakeformation.grant_permissions(
    Principal={'DataLakePrincipalIdentifier': 'arn:aws:iam::123456789:role/AnalystRole'},
    Resource={
        'Table': {
            'DatabaseName': 'gold_db',
            'Name': 'daily_revenue',
        }
    },
    Permissions=['SELECT'],
    PermissionsWithGrantOption=[],
)

# Column-level security (hide PII)
lakeformation.grant_permissions(
    Principal={'DataLakePrincipalIdentifier': 'arn:aws:iam::123456789:role/JuniorAnalyst'},
    Resource={
        'TableWithColumns': {
            'DatabaseName': 'silver_db',
            'Name': 'customers',
            'ColumnNames': ['customer_id', 'name', 'region'],  # Only these columns
            'ColumnWildcard': None,  # Exclude: email, phone, address (PII)
        }
    },
    Permissions=['SELECT'],
)

# Row-level security
lakeformation.create_data_cells_filter(
    TableData={
        'DatabaseName': 'silver_db',
        'TableName': 'orders',
        'Name': 'us-only-filter',
        'RowFilter': {'FilterExpression': "region = 'US'"},
        'ColumnNames': [],
        'ColumnWildcard': {},
    }
)
```

---

## Interview Questions

### Beginner
1. **What is AWS Glue?** Managed ETL service with Data Catalog (schema discovery), crawlers (auto-detect), and Spark-based jobs. Serverless — pay per DPU-hour.
2. **When to use Athena vs Redshift?** Athena: ad-hoc queries, infrequent access, pay-per-query. Redshift: frequent queries, complex joins, predictable workload, need sub-second latency.
3. **What is Kinesis Firehose vs Data Streams?** Firehose: fully managed delivery to S3/Redshift (no code, buffered). Data Streams: custom processing with Lambda/applications (more control, lower latency).

### Intermediate
4. **How do you optimize Athena query costs?** Partition data (reduce scan), use columnar formats (Parquet/ORC), compress data, use CTAS for denormalized tables, avoid SELECT *, set workgroup limits.
5. **Explain Glue job bookmarks.** Track what data has been processed. On subsequent runs, only process new files/rows. Prevents reprocessing. Reset bookmark to reprocess everything.
6. **How does Lake Formation differ from IAM for data access?** IAM is coarse-grained (bucket/prefix level). Lake Formation adds column-level, row-level, and tag-based access control. Centralized governance across Athena, Glue, EMR.

### Advanced
7. **Design a cost-optimized data lake on AWS for 100TB.** S3 lifecycle (hot→IA→Glacier), Glue for ETL (spot instances), Athena for ad-hoc (partition pruning), Redshift for dashboards, reserved capacity. Monitor with Cost Explorer, set budgets.
8. **How do you handle exactly-once processing with Kinesis?** Kinesis has at-least-once delivery. For exactly-once: use DynamoDB for checkpoint tracking, idempotent writes (upsert), or use Kinesis + Lambda with deduplication window.
9. **Architect a real-time + batch pipeline on AWS.** Kinesis → Lambda (real-time alerts) + Firehose → S3 (bronze). Glue jobs (batch transform to silver/gold). Step Functions orchestration. Athena + QuickSight for analytics. Lake Formation for governance.

---

## Hands-On Exercise
1. Set up S3 bucket with lifecycle policies
2. Create Glue crawler to discover schema from Parquet files
3. Write and run a Glue ETL job
4. Query data with Athena (compare costs with different formats)
5. Set up Kinesis Firehose delivery to S3
6. Configure Lake Formation permissions (column-level)
