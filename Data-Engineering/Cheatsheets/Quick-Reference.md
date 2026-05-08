# Data Engineering Cheatsheet

## Quick Reference Commands

### Spark
```python
# Read
df = spark.read.parquet("s3://bucket/path/")
df = spark.read.option("header", True).csv("data.csv")
df = spark.read.format("delta").load("delta_path")

# Transformations
df.filter(col("age") > 25)
df.select("name", "age")
df.withColumn("new_col", col("price") * 1.1)
df.groupBy("category").agg(sum("amount"), count("*"))
df.join(other, "key_col", "left")
df.join(broadcast(small_df), "key_col")  # Broadcast join

# Write
df.write.mode("overwrite").parquet("output/")
df.write.partitionBy("date").format("delta").save("delta_path")
df.coalesce(1).write.csv("single_file/")  # Single output file
```

### Airflow
```python
# DAG Template
with DAG('my_dag', schedule_interval='0 6 * * *', start_date=datetime(2024,1,1), catchup=False):
    task = PythonOperator(task_id='task', python_callable=func)

# Template variables: {{ ds }}, {{ ds_nodash }}, {{ execution_date }}
# CLI: airflow dags trigger my_dag
#      airflow tasks test my_dag my_task 2024-01-01
#      airflow dags backfill my_dag -s 2024-01-01 -e 2024-01-31
```

### Kafka (Python)
```python
# Producer
producer = Producer({'bootstrap.servers': 'localhost:9092', 'acks': 'all'})
producer.produce('topic', key=b'key', value=b'value', callback=callback)
producer.flush()

# Consumer
consumer = Consumer({'bootstrap.servers': 'localhost:9092', 'group.id': 'grp', 'auto.offset.reset': 'earliest'})
consumer.subscribe(['topic'])
msg = consumer.poll(1.0)
consumer.commit()
```

### dbt
```bash
dbt init my_project
dbt run                    # Run all models
dbt run --select model_name  # Run specific model
dbt test                   # Run all tests
dbt docs generate && dbt docs serve  # Documentation
```

## SQL Patterns for DE

```sql
-- Deduplication
SELECT * FROM (SELECT *, ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) rn FROM t) WHERE rn = 1;

-- Running total
SELECT *, SUM(amount) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING) FROM orders;

-- Gap fill (with date series)
SELECT d.date, COALESCE(m.value, 0) FROM date_series d LEFT JOIN metrics m ON d.date = m.date;

-- Pivot
SELECT user_id,
  COUNT(*) FILTER (WHERE event = 'view') AS views,
  COUNT(*) FILTER (WHERE event = 'click') AS clicks
FROM events GROUP BY user_id;
```

## File Formats Comparison
| Format | Columnar | Compression | Schema | Use Case |
|--------|----------|-------------|--------|----------|
| Parquet | Yes | Excellent | Embedded | Analytics, data lake |
| ORC | Yes | Excellent | Embedded | Hive ecosystem |
| Avro | No (row) | Good | Embedded | Streaming, Kafka |
| JSON | No | None | None | APIs, logs |
| CSV | No | None | None | Simple exchange |
| Delta | Yes (Parquet) | Excellent | + ACID | Lakehouse |

## Key Architecture Patterns
```
Medallion:   Bronze (raw) → Silver (clean) → Gold (business)
Lambda:      Batch layer + Speed layer + Serving layer
Kappa:       Stream-only (Kafka as source of truth)
CDC:         Source WAL → Debezium → Kafka → Target
```
