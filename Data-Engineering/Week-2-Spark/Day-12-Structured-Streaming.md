# Day 12: Spark Structured Streaming

## Learning Objectives
- Build real-time data pipelines with Structured Streaming
- Implement windowing, watermarks, and stateful operations
- Handle late data and exactly-once semantics
- Connect to Kafka and other streaming sources

---

## 1. Streaming Fundamentals

### Concept: Unbounded Tables
Structured Streaming treats a stream as an unbounded table. New data is appended as new rows. You write the same DataFrame/SQL queries as batch.

### Beginner: Basic Streaming

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("Streaming") \
    .config("spark.sql.streaming.checkpointLocation", "/tmp/checkpoints") \
    .getOrCreate()

# Read from file source (simulates streaming)
schema = StructType([
    StructField("timestamp", TimestampType()),
    StructField("user_id", StringType()),
    StructField("event", StringType()),
    StructField("amount", DoubleType()),
])

stream_df = (
    spark.readStream
    .schema(schema)
    .option("maxFilesPerTrigger", 1)  # Process one file at a time
    .json("data/events/")
)

# Transform (same as batch!)
processed = (
    stream_df
    .filter(F.col("amount") > 0)
    .withColumn("date", F.to_date("timestamp"))
)

# Write to console (for debugging)
query = (
    processed.writeStream
    .outputMode("append")
    .format("console")
    .option("truncate", False)
    .start()
)

query.awaitTermination()
```

### Read from Kafka

```python
# Read from Kafka topic
kafka_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "events")
    .option("startingOffsets", "latest")
    .option("failOnDataLoss", "false")
    .load()
)

# Kafka message structure: key, value, topic, partition, offset, timestamp
# Parse the value (JSON)
event_schema = StructType([
    StructField("user_id", StringType()),
    StructField("event_type", StringType()),
    StructField("amount", DoubleType()),
    StructField("event_time", TimestampType()),
])

events = (
    kafka_df
    .select(F.from_json(F.col("value").cast("string"), event_schema).alias("data"))
    .select("data.*")
)
```

---

## 2. Output Modes & Triggers

### Output Modes

```python
# APPEND: Only new rows since last trigger (default)
# Use when: no aggregations, or aggregations with watermark
query = processed.writeStream.outputMode("append").start()

# COMPLETE: Entire result table every trigger
# Use when: aggregations where you need full results
query = aggregated.writeStream.outputMode("complete").start()

# UPDATE: Only rows that changed since last trigger
# Use when: aggregations, only want changed rows
query = aggregated.writeStream.outputMode("update").start()
```

### Triggers

```python
# Default: Process as soon as previous trigger completes
query = df.writeStream.trigger(processingTime="0 seconds").start()

# Fixed interval: Process every N seconds
query = df.writeStream.trigger(processingTime="30 seconds").start()

# Once: Process all available data, then stop (useful for batch-style)
query = df.writeStream.trigger(once=True).start()

# Available-now: Process all available data in multiple batches, then stop
query = df.writeStream.trigger(availableNow=True).start()

# Continuous: Experimental low-latency mode (~1ms)
query = df.writeStream.trigger(continuous="1 second").start()
```

---

## 3. Windowing Operations

### Tumbling Windows (Non-overlapping)

```python
# Count events per 5-minute window
windowed = (
    events
    .groupBy(
        F.window("event_time", "5 minutes"),  # Tumbling window
        "event_type"
    )
    .agg(
        F.count("*").alias("event_count"),
        F.sum("amount").alias("total_amount"),
    )
)

# Output: window.start, window.end, event_type, event_count, total_amount
windowed.writeStream.outputMode("update").format("console").start()
```

### Sliding Windows (Overlapping)

```python
# 10-minute window, sliding every 5 minutes
windowed = (
    events
    .groupBy(
        F.window("event_time", "10 minutes", "5 minutes"),  # window, slide
        "region"
    )
    .agg(F.avg("amount").alias("avg_amount"))
)
```

### Session Windows (Gap-based)

```python
# Session window with 10-minute gap
from pyspark.sql.functions import session_window

session_windowed = (
    events
    .groupBy(
        session_window("event_time", "10 minutes"),
        "user_id"
    )
    .agg(
        F.count("*").alias("events_in_session"),
        F.sum("amount").alias("session_total"),
        F.first("event_type").alias("first_event"),
        F.last("event_type").alias("last_event"),
    )
)
```

---

## 4. Watermarks & Late Data

```python
# Problem: Events can arrive late (network delays, mobile offline)
# Solution: Watermarks define how long to wait for late data

# Allow up to 10 minutes of late data
events_with_watermark = (
    events
    .withWatermark("event_time", "10 minutes")
    .groupBy(
        F.window("event_time", "5 minutes"),
        "event_type"
    )
    .agg(F.count("*").alias("count"))
)

# How watermarks work:
# - Watermark = max(event_time) - threshold
# - Windows older than watermark are finalized (no more updates)
# - Late data arriving after watermark is dropped
# - Allows append mode with aggregations (finalized windows)

# Write with append mode (only finalized windows)
query = (
    events_with_watermark
    .writeStream
    .outputMode("append")  # Works because watermark finalizes windows
    .format("parquet")
    .option("path", "output/windowed_events/")
    .option("checkpointLocation", "/checkpoints/windowed/")
    .start()
)
```

### Watermark Semantics
```
Timeline:
Events: [10:00, 10:02, 10:05, 10:01, 10:08, 10:03, 10:12]
Watermark threshold: 5 minutes
Max event time seen: 10:12
Current watermark: 10:12 - 5 min = 10:07

→ Windows ending before 10:07 are finalized
→ Event at 10:01 arriving now would be DROPPED (before watermark)
→ Event at 10:08 arriving now would be ACCEPTED
```

---

## 5. Stateful Operations

### Streaming Deduplication

```python
# Deduplicate within watermark window
deduped = (
    events
    .withWatermark("event_time", "1 hour")
    .dropDuplicates(["event_id", "event_time"])
)
```

### Stream-Stream Joins

```python
# Join two streams (e.g., clicks and purchases)
clicks = spark.readStream.format("kafka").option("subscribe", "clicks").load()
purchases = spark.readStream.format("kafka").option("subscribe", "purchases").load()

# Both streams need watermarks
clicks_wm = clicks.withWatermark("click_time", "10 minutes")
purchases_wm = purchases.withWatermark("purchase_time", "10 minutes")

# Join with time constraint
attributed = clicks_wm.join(
    purchases_wm,
    F.expr("""
        clicks.user_id = purchases.user_id AND
        purchase_time >= click_time AND
        purchase_time <= click_time + interval 30 minutes
    """),
    "leftOuter"
)
```

### Stream-Static Joins

```python
# Join streaming data with static lookup table
static_products = spark.read.parquet("data/products/")  # Loaded once

enriched_events = events.join(static_products, "product_id", "left")
# Note: static table is NOT refreshed during stream
# For refreshing: use foreachBatch to re-read
```

---

## 6. Writing to Sinks

### File Sink (Data Lake)

```python
query = (
    processed.writeStream
    .format("parquet")
    .option("path", "s3://datalake/bronze/events/")
    .option("checkpointLocation", "s3://datalake/checkpoints/events/")
    .partitionBy("date")
    .trigger(processingTime="1 minute")
    .start()
)
```

### Delta Lake Sink

```python
query = (
    processed.writeStream
    .format("delta")
    .outputMode("append")
    .option("checkpointLocation", "/checkpoints/delta_events/")
    .toTable("streaming_events")
)
```

### Kafka Sink

```python
# Write back to Kafka (transformed events)
output = processed.select(
    F.col("user_id").alias("key"),
    F.to_json(F.struct("*")).alias("value")
)

query = (
    output.writeStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("topic", "processed_events")
    .option("checkpointLocation", "/checkpoints/kafka_output/")
    .start()
)
```

### foreachBatch (Custom Logic)

```python
def process_batch(batch_df, batch_id):
    """Custom processing for each micro-batch."""
    # Write to multiple sinks
    batch_df.write.mode("append").parquet(f"s3://lake/events/")
    
    # Upsert to database
    batch_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://localhost/warehouse") \
        .option("dbtable", "events") \
        .mode("append") \
        .save()
    
    # Update metrics
    count = batch_df.count()
    print(f"Batch {batch_id}: processed {count} records")

query = (
    processed.writeStream
    .foreachBatch(process_batch)
    .option("checkpointLocation", "/checkpoints/multi_sink/")
    .start()
)
```

---

## 7. Exactly-Once with Checkpointing

```python
# Checkpointing guarantees exactly-once processing
# Stores: offsets read, state of operations, committed offsets

# Configuration
query = (
    stream_df.writeStream
    .format("delta")
    .option("checkpointLocation", "/reliable/storage/checkpoints/my_query/")
    .start()
)

# Checkpoint contains:
# /checkpoints/my_query/
# ├── commits/      → Which batches are complete
# ├── offsets/      → What offsets were read per batch
# ├── sources/      → Source-specific metadata
# └── state/        → Stateful operation state (aggregations, dedup)

# Recovery: If query crashes and restarts:
# 1. Reads last committed offset
# 2. Re-reads from that offset
# 3. Reprocesses (transformations are deterministic)
# 4. Commits new offset
# → No data loss, no duplicates
```

---

## Interview Questions

### Beginner
1. **What is Structured Streaming?** Spark's stream processing engine that treats streams as unbounded tables. Same DataFrame/SQL API as batch. Provides exactly-once guarantees.
2. **What are the three output modes?** Append (new rows only), Complete (full result each time), Update (only changed rows). Append with aggregations requires watermarks.
3. **What's a trigger in streaming?** Determines when to process. Processing-time (interval), Once (all available then stop), Continuous (experimental low-latency).

### Intermediate
4. **Explain watermarks and their purpose.** Watermark = max(event_time) - threshold. Tells Spark how long to wait for late data. Enables: append mode with aggregations, state cleanup, bounded memory.
5. **How does exactly-once work in Structured Streaming?** Checkpointing + idempotent sinks. Checkpoint stores offsets and state. On failure, replays from last committed offset. Sinks must handle duplicates (Delta Lake, JDBC with upserts).
6. **What's the difference between stream-stream and stream-static joins?** Stream-stream: both sides are streams, requires watermarks and time constraints. Stream-static: one side loaded once (not refreshed). Stream-stream uses state store.

### Advanced
7. **How do you handle state store growth in long-running streams?** Watermarks enable state expiry (old windows dropped). Monitor state store size in UI. Use RocksDB state store for large state. Design operations to bound state (windowed aggregations over unbounded).
8. **Design a real-time event processing system with Spark Streaming.** Kafka source → parse JSON → watermark (5 min) → window aggregation → write to Delta (for analytics) + Kafka (for alerts) using foreachBatch. Checkpoints on S3 for exactly-once.
9. **How do you upgrade a streaming query without losing state?** Compatible changes (add columns, change trigger) preserve state. Incompatible changes (change groupBy keys, window size) require state migration or fresh start. Use allowances in checkpoint compatibility.

---

## Hands-On Exercise
1. Create a streaming source from JSON files (simulate events)
2. Implement windowed aggregations (events per 5-min window)
3. Add watermark (10 min), observe late data handling
4. Write to Delta Lake with partitioning
5. Implement stream-stream join (clicks + purchases)
6. Monitor query progress with `query.status` and `query.recentProgress`
