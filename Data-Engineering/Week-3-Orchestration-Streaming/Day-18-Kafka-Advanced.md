# Day 18: Kafka Advanced — Streams, Connect & Production

## Learning Objectives
- Implement stream processing with Kafka Streams/ksqlDB
- Configure Kafka Connect for source and sink connectors
- Manage schema evolution with Schema Registry
- Tune Kafka for production workloads

---

## 1. Kafka Connect

### Source Connectors (Database → Kafka)

```json
{
  "name": "postgres-source-customers",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "replication_user",
    "database.password": "${secrets:postgres:password}",
    "database.dbname": "production",
    "database.server.name": "prod",
    "table.include.list": "public.customers,public.orders",
    "plugin.name": "pgoutput",
    "slot.name": "debezium_slot",
    "publication.name": "dbz_publication",
    "transforms": "route",
    "transforms.route.type": "org.apache.kafka.connect.transforms.RegexRouter",
    "transforms.route.regex": "prod.public.(.*)",
    "transforms.route.replacement": "cdc.$1",
    "snapshot.mode": "initial",
    "tombstones.on.delete": "true"
  }
}
```

### Sink Connectors (Kafka → Target)

```json
{
  "name": "s3-sink-events",
  "config": {
    "connector.class": "io.confluent.connect.s3.S3SinkConnector",
    "tasks.max": "4",
    "topics": "events",
    "s3.bucket.name": "datalake-bronze",
    "s3.region": "us-east-1",
    "flush.size": "10000",
    "rotate.interval.ms": "3600000",
    "storage.class": "io.confluent.connect.s3.storage.S3Storage",
    "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
    "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
    "path.format": "'year'=YYYY/'month'=MM/'day'=dd/'hour'=HH",
    "locale": "en-US",
    "timezone": "UTC",
    "partition.duration.ms": "3600000",
    "schema.compatibility": "BACKWARD"
  }
}
```

### Managing Connectors via REST API

```bash
# List connectors
curl http://localhost:8083/connectors

# Create connector
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d @postgres-source.json

# Check status
curl http://localhost:8083/connectors/postgres-source-customers/status

# Restart failed task
curl -X POST http://localhost:8083/connectors/postgres-source-customers/tasks/0/restart

# Pause/Resume
curl -X PUT http://localhost:8083/connectors/postgres-source-customers/pause
curl -X PUT http://localhost:8083/connectors/postgres-source-customers/resume

# Delete
curl -X DELETE http://localhost:8083/connectors/postgres-source-customers
```

---

## 2. Schema Registry

```python
# Schema Registry ensures producers and consumers agree on message format
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from confluent_kafka import SerializingProducer, DeserializingConsumer

# Schema Registry client
schema_registry = SchemaRegistryClient({"url": "http://localhost:8081"})

# Define Avro schema
order_schema_str = """
{
  "type": "record",
  "name": "Order",
  "namespace": "com.company.events",
  "fields": [
    {"name": "order_id", "type": "string"},
    {"name": "customer_id", "type": "string"},
    {"name": "amount", "type": "double"},
    {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
    {"name": "status", "type": {"type": "enum", "name": "Status", 
                                  "symbols": ["PENDING", "COMPLETED", "CANCELLED"]}},
    {"name": "metadata", "type": ["null", {"type": "map", "values": "string"}], "default": null}
  ]
}
"""

# Producer with schema validation
avro_serializer = AvroSerializer(schema_registry, order_schema_str)

producer = SerializingProducer({
    "bootstrap.servers": "localhost:9092",
    "key.serializer": lambda k, ctx: k.encode("utf-8"),
    "value.serializer": avro_serializer,
})

# Produce with schema
producer.produce(
    topic="orders",
    key="ORD-001",
    value={
        "order_id": "ORD-001",
        "customer_id": "CUST-123",
        "amount": 99.99,
        "timestamp": 1706745600000,
        "status": "COMPLETED",
        "metadata": {"source": "web"},
    }
)
producer.flush()
```

### Schema Evolution Rules

```python
# Compatibility modes:
# BACKWARD: New schema can read old data (add optional fields, remove fields)
# FORWARD: Old schema can read new data (remove optional fields, add fields)
# FULL: Both backward and forward compatible
# NONE: No compatibility checking

# Set compatibility for a subject
import requests
requests.put(
    "http://localhost:8081/config/orders-value",
    json={"compatibility": "BACKWARD"}
)

# Check compatibility before registering new schema
response = requests.post(
    "http://localhost:8081/compatibility/subjects/orders-value/versions/latest",
    json={"schema": new_schema_str}
)
# {"is_compatible": true}

# BACKWARD compatible changes:
# ✅ Add field with default value
# ✅ Remove field (consumers ignore unknown fields)
# ❌ Remove field without default (old consumers fail)
# ❌ Change field type (int → string)
# ❌ Rename field
```

---

## 3. ksqlDB — SQL on Streams

```sql
-- Create a STREAM from Kafka topic
CREATE STREAM orders_raw (
    order_id VARCHAR KEY,
    customer_id VARCHAR,
    amount DOUBLE,
    status VARCHAR,
    order_time TIMESTAMP
) WITH (
    KAFKA_TOPIC = 'orders',
    VALUE_FORMAT = 'AVRO',
    TIMESTAMP = 'order_time'
);

-- Real-time filtering
CREATE STREAM high_value_orders AS
    SELECT * FROM orders_raw
    WHERE amount > 1000;

-- Windowed aggregation (tumbling window)
CREATE TABLE orders_per_minute AS
    SELECT
        customer_id,
        COUNT(*) AS order_count,
        SUM(amount) AS total_amount,
        WINDOWSTART AS window_start,
        WINDOWEND AS window_end
    FROM orders_raw
    WINDOW TUMBLING (SIZE 1 MINUTE)
    GROUP BY customer_id;

-- Stream-Table join (enrich events with static data)
CREATE TABLE customers (
    customer_id VARCHAR PRIMARY KEY,
    name VARCHAR,
    tier VARCHAR
) WITH (
    KAFKA_TOPIC = 'customers',
    VALUE_FORMAT = 'AVRO'
);

CREATE STREAM enriched_orders AS
    SELECT 
        o.order_id,
        o.customer_id,
        c.name AS customer_name,
        c.tier AS customer_tier,
        o.amount
    FROM orders_raw o
    LEFT JOIN customers c ON o.customer_id = c.customer_id;

-- Detect anomalies (more than 10 orders in 5 minutes)
CREATE TABLE suspicious_activity AS
    SELECT
        customer_id,
        COUNT(*) AS order_count,
        SUM(amount) AS total_amount
    FROM orders_raw
    WINDOW HOPPING (SIZE 5 MINUTES, ADVANCE BY 1 MINUTE)
    GROUP BY customer_id
    HAVING COUNT(*) > 10;
```

---

## 4. Exactly-Once Processing

```python
from confluent_kafka import Producer, Consumer

# Idempotent Producer (exactly-once within single partition)
producer = Producer({
    "bootstrap.servers": "localhost:9092",
    "enable.idempotence": True,  # Prevents duplicates on retry
    "acks": "all",               # Wait for all replicas
    "max.in.flight.requests.per.connection": 5,  # Allows reordering prevention
})

# Transactional Producer (exactly-once across partitions/topics)
producer = Producer({
    "bootstrap.servers": "localhost:9092",
    "transactional.id": "my-app-producer-1",
})
producer.init_transactions()

try:
    producer.begin_transaction()
    producer.produce("topic-a", key="k1", value="v1")
    producer.produce("topic-b", key="k2", value="v2")
    producer.commit_transaction()
except Exception as e:
    producer.abort_transaction()
    raise

# Consumer with exactly-once (read-process-write pattern)
consumer = Consumer({
    "bootstrap.servers": "localhost:9092",
    "group.id": "my-group",
    "enable.auto.commit": False,  # Manual commit
    "isolation.level": "read_committed",  # Only read committed transactions
})

# Process-commit pattern
consumer.subscribe(["orders"])
while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue
    
    # Process message
    process(msg.value())
    
    # Commit offset AFTER successful processing
    consumer.commit(asynchronous=False)
```

---

## 5. Production Tuning

### Producer Tuning

```python
producer_config = {
    "bootstrap.servers": "broker1:9092,broker2:9092,broker3:9092",
    
    # Durability
    "acks": "all",               # Wait for all ISR replicas
    "enable.idempotence": True,  # No duplicates
    
    # Throughput
    "batch.size": 65536,         # 64KB batches
    "linger.ms": 20,             # Wait 20ms for batch to fill
    "compression.type": "lz4",   # Fast compression
    
    # Reliability
    "retries": 2147483647,       # Infinite retries (with timeout)
    "delivery.timeout.ms": 120000,  # 2 min total delivery timeout
    "request.timeout.ms": 30000,
    
    # Memory
    "buffer.memory": 67108864,   # 64MB buffer
}
```

### Consumer Tuning

```python
consumer_config = {
    "bootstrap.servers": "broker1:9092,broker2:9092,broker3:9092",
    "group.id": "order-processor",
    
    # Processing
    "auto.offset.reset": "earliest",  # Start from beginning if no offset
    "enable.auto.commit": False,      # Manual commit for exactly-once
    "max.poll.records": 500,          # Records per poll
    "max.poll.interval.ms": 300000,   # 5 min max processing time
    
    # Performance
    "fetch.min.bytes": 1048576,       # 1MB min fetch
    "fetch.max.wait.ms": 500,         # Wait up to 500ms for min bytes
    
    # Session
    "session.timeout.ms": 45000,      # 45s before considered dead
    "heartbeat.interval.ms": 15000,   # Heartbeat every 15s
}
```

### Broker/Topic Configuration

```bash
# Create topic with optimal settings
kafka-topics --create \
  --topic orders \
  --partitions 12 \          # Rule: partitions >= max consumers in group
  --replication-factor 3 \   # 3 for production (tolerates 1 broker failure)
  --config retention.ms=604800000 \     # 7 days retention
  --config retention.bytes=-1 \          # No size limit
  --config cleanup.policy=delete \       # Or "compact" for tables
  --config min.insync.replicas=2 \       # 2 ISR required for acks=all
  --config segment.bytes=1073741824 \    # 1GB segments
  --config compression.type=lz4
```

---

## 6. Monitoring

```python
# Key metrics to monitor:

# Consumer Lag (most important!)
# If lag grows → consumers can't keep up
# Alert when: lag > threshold or lag growing over time

# Producer metrics:
# - record-send-rate: messages/second
# - record-send-total: total messages sent
# - request-latency-avg: avg time per request
# - batch-size-avg: average batch size (should be close to batch.size)

# Consumer metrics:
# - records-consumed-rate: messages/second
# - records-lag-max: maximum lag across partitions
# - commit-latency-avg: time to commit offsets

# Broker metrics:
# - UnderReplicatedPartitions: should be 0 (data loss risk if > 0)
# - ISRShrinkRate: ISR shrinking = broker issues
# - RequestHandlerAvgIdlePercent: < 0.3 = overloaded
# - NetworkProcessorAvgIdlePercent: < 0.3 = network bottleneck
```

```bash
# Check consumer lag
kafka-consumer-groups --bootstrap-server localhost:9092 \
  --group order-processor \
  --describe

# Output:
# GROUP          TOPIC    PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# order-processor orders  0          1000            1050            50
# order-processor orders  1          2000            2005            5
```

---

## Interview Questions

### Beginner
1. **What is Kafka Connect?** Framework for streaming data between Kafka and external systems. Source connectors pull data in, sink connectors push data out. No custom code needed.
2. **Why use Schema Registry?** Ensures producers/consumers agree on message format. Prevents breaking changes. Enables schema evolution without downtime.
3. **What's the difference between a Kafka Stream and a Table?** Stream = append-only events (insert only). Table = latest value per key (upsert). Stream-table duality: stream is changelog of table.

### Intermediate
4. **Explain exactly-once semantics in Kafka.** Idempotent producer (no duplicates per partition) + transactions (atomic multi-partition writes) + consumer read_committed (skip aborted transactions) + manual offset commit after processing.
5. **How do you choose the number of partitions?** Partitions = max parallelism. At least: max(producer throughput / partition throughput, consumers in largest group). Start with 6-12, scale later. More partitions = more memory, longer rebalance.
6. **What is consumer lag and why does it matter?** Difference between latest produced offset and consumer's committed offset. Growing lag = consumers too slow. Monitor and alert. Fix: add consumers, optimize processing, increase partitions.

### Advanced
7. **Design a CDC pipeline from PostgreSQL to data lake using Kafka.** Debezium source connector → Kafka (with Schema Registry) → Kafka Connect S3 Sink (Parquet, hourly partitions) → Delta Lake MERGE for dedup. Monitor: connector status, lag, replication slot size.
8. **How do you handle schema evolution in a production Kafka pipeline?** Use Schema Registry with BACKWARD compatibility. Only add optional fields with defaults. Test compatibility before deploying. Version topics for breaking changes. Consumer handles unknown fields gracefully.
9. **Explain how to scale Kafka consumers when processing can't keep up.** Add consumers to consumer group (up to partition count). If at limit: increase partitions (requires topic recreation or config change), optimize processing logic, use batch processing within consumer, consider async processing with local buffer.

---

## Hands-On Exercise
1. Set up Kafka Connect with Debezium (PostgreSQL → Kafka)
2. Configure Schema Registry with Avro schemas
3. Write ksqlDB queries for real-time aggregation
4. Implement exactly-once producer-consumer pattern
5. Monitor consumer lag and set up alerting
6. Handle schema evolution (add field, verify backward compatibility)
