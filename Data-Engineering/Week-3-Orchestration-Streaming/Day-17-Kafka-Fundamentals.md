# Day 17: Apache Kafka Fundamentals

## Overview
Kafka is the backbone of real-time data infrastructure. Learn distributed messaging, event streaming, and building reliable data pipelines.

---

## 1. What is Kafka?

A **distributed event streaming platform** for high-throughput, fault-tolerant, real-time data pipelines.

### Use Cases
- Real-time analytics (clickstreams, metrics)
- Event sourcing & CQRS
- Log aggregation
- CDC (Change Data Capture) transport
- Microservice communication
- Stream processing (with Kafka Streams / Flink)

---

## 2. Core Concepts

```
Producer → Topic (Partitions) → Consumer Group
                  │
         ┌───────┼───────┐
         ▼       ▼       ▼
    Partition 0  P1      P2
    [msg0,msg3] [msg1]  [msg2,msg4]
         │       │       │
    Consumer A  Con B   Con C   (Consumer Group: "analytics")
```

### Topics & Partitions
```
Topic: "user-events" (3 partitions)
┌─────────────────────────────────┐
│ Partition 0: [0][1][2][3][4]... │  ← Ordered within partition
│ Partition 1: [0][1][2]...       │  ← Messages distributed by key
│ Partition 2: [0][1][2][3]...    │  ← Each partition = 1 consumer max
└─────────────────────────────────┘
```

| Concept | Description |
|---------|-------------|
| **Topic** | Named feed/category of messages |
| **Partition** | Ordered, immutable sequence of messages within a topic |
| **Offset** | Unique sequential ID of a message within a partition |
| **Key** | Determines which partition a message goes to (hash-based) |
| **Consumer Group** | Set of consumers sharing work on a topic |
| **Broker** | Kafka server instance |
| **Replication** | Copies of partitions across brokers for fault tolerance |

---

## 3. Producers

```python
from confluent_kafka import Producer
import json

# Configuration
config = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'my-producer',
    'acks': 'all',                    # Wait for all replicas
    'retries': 3,
    'enable.idempotence': True,       # Exactly-once semantics
    'compression.type': 'snappy',     # Compress messages
    'linger.ms': 5,                   # Batch messages for 5ms
    'batch.size': 16384,              # Max batch size in bytes
}

producer = Producer(config)

# Delivery callback
def delivery_report(err, msg):
    if err:
        print(f"Delivery failed: {err}")
    else:
        print(f"Delivered to {msg.topic()}[{msg.partition()}] @ offset {msg.offset()}")

# Produce messages
def produce_event(user_id: str, event_type: str, data: dict):
    event = {
        'user_id': user_id,
        'event_type': event_type,
        'timestamp': datetime.utcnow().isoformat(),
        'data': data
    }
    
    producer.produce(
        topic='user-events',
        key=user_id.encode('utf-8'),      # Partition by user_id
        value=json.dumps(event).encode('utf-8'),
        callback=delivery_report
    )
    producer.poll(0)  # Trigger callbacks

# Flush remaining messages before exit
producer.flush()
```

### Partitioning Strategy
```python
# Default: hash(key) % num_partitions
# Same key → same partition → ordered per key

# Custom partitioner
def custom_partitioner(key, all_partitions, available_partitions):
    """Route high-priority events to partition 0"""
    if key and b'priority:high' in key:
        return 0
    return hash(key) % len(all_partitions)
```

---

## 4. Consumers

```python
from confluent_kafka import Consumer, KafkaError

config = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'analytics-service',
    'auto.offset.reset': 'earliest',     # Start from beginning if no offset
    'enable.auto.commit': False,         # Manual commit for at-least-once
    'max.poll.interval.ms': 300000,      # Max time between polls
    'session.timeout.ms': 45000,         # Consumer heartbeat timeout
}

consumer = Consumer(config)
consumer.subscribe(['user-events'])

try:
    while True:
        msg = consumer.poll(timeout=1.0)
        
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            raise KafkaError(msg.error())
        
        # Process message
        event = json.loads(msg.value().decode('utf-8'))
        process_event(event)
        
        # Manual commit after successful processing (at-least-once)
        consumer.commit(asynchronous=False)
        
except KeyboardInterrupt:
    pass
finally:
    consumer.close()
```

### Consumer Group Rebalancing
```
Topic: user-events (6 partitions)

Consumer Group: "analytics" (3 consumers)
├── Consumer A → Partitions [0, 1]
├── Consumer B → Partitions [2, 3]
└── Consumer C → Partitions [4, 5]

If Consumer C dies:
├── Consumer A → Partitions [0, 1, 4]   ← Rebalanced
└── Consumer B → Partitions [2, 3, 5]   ← Rebalanced
```

---

## 5. Delivery Guarantees

| Guarantee | How | Trade-off |
|-----------|-----|-----------|
| **At-most-once** | Auto-commit before processing | May lose messages |
| **At-least-once** | Commit after processing | May have duplicates |
| **Exactly-once** | Idempotent producer + transactions | Higher latency |

### Exactly-Once Semantics (EOS)
```python
# Producer side: idempotent + transactional
producer_config = {
    'bootstrap.servers': 'localhost:9092',
    'enable.idempotence': True,
    'transactional.id': 'my-transaction-id',
}

producer = Producer(producer_config)
producer.init_transactions()

try:
    producer.begin_transaction()
    
    # Produce multiple messages atomically
    producer.produce('output-topic', key=b'key1', value=b'value1')
    producer.produce('output-topic', key=b'key2', value=b'value2')
    
    # Commit consumer offsets as part of transaction
    producer.send_offsets_to_transaction(
        consumer.position(consumer.assignment()),
        consumer.consumer_group_metadata()
    )
    
    producer.commit_transaction()
except Exception as e:
    producer.abort_transaction()
    raise
```

---

## 6. Kafka Architecture Deep Dive

### Replication
```
Topic: orders (replication-factor=3)

Broker 1: P0(Leader), P1(Follower), P2(Follower)
Broker 2: P0(Follower), P1(Leader), P2(Follower)
Broker 3: P0(Follower), P1(Follower), P2(Leader)

ISR (In-Sync Replicas): Followers that are caught up
- If leader dies, ISR member becomes new leader
- acks=all means ALL ISR members acknowledged
```

### Log Compaction
```
Before compaction:
[user1:v1] [user2:v1] [user1:v2] [user3:v1] [user1:v3]

After compaction:
[user2:v1] [user3:v1] [user1:v3]  ← Only latest per key

Use case: Changelog/CDC topics, KV state
```

### Retention
```properties
# Time-based retention (default 7 days)
log.retention.hours=168

# Size-based retention
log.retention.bytes=1073741824  # 1GB per partition

# Compact (keep latest per key)
log.cleanup.policy=compact
```

---

## 7. Schema Management (Schema Registry)

```python
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer

# Schema definition (Avro)
schema_str = """
{
    "type": "record",
    "name": "UserEvent",
    "namespace": "com.company.events",
    "fields": [
        {"name": "user_id", "type": "string"},
        {"name": "event_type", "type": "string"},
        {"name": "timestamp", "type": "long", "logicalType": "timestamp-millis"},
        {"name": "amount", "type": ["null", "double"], "default": null}
    ]
}
"""

# Schema Registry client
registry_client = SchemaRegistryClient({'url': 'http://localhost:8081'})

# Serializer for producer
avro_serializer = AvroSerializer(
    registry_client, 
    schema_str,
    conf={'auto.register.schemas': True}
)

# Produce with schema validation
producer.produce(
    topic='user-events',
    key=user_id,
    value=avro_serializer(event_dict, SerializationContext('user-events', MessageField.VALUE))
)
```

### Schema Evolution Rules
| Compatibility | Allowed Changes |
|---|---|
| BACKWARD | Delete fields, add optional fields |
| FORWARD | Add fields, delete optional fields |
| FULL | Add/delete optional fields only |
| NONE | Any change (dangerous!) |

---

## 8. Kafka Connect

Pre-built connectors for common data sources/sinks:

```json
// Source connector: PostgreSQL CDC → Kafka
{
    "name": "postgres-source",
    "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "database.hostname": "postgres",
        "database.port": "5432",
        "database.user": "replication_user",
        "database.password": "${secrets:postgres:password}",
        "database.dbname": "app_db",
        "table.include.list": "public.users,public.orders",
        "topic.prefix": "cdc",
        "plugin.name": "pgoutput"
    }
}

// Sink connector: Kafka → S3 (Parquet)
{
    "name": "s3-sink",
    "config": {
        "connector.class": "io.confluent.connect.s3.S3SinkConnector",
        "topics": "user-events",
        "s3.bucket.name": "data-lake-raw",
        "s3.region": "us-east-1",
        "format.class": "io.confluent.connect.s3.format.parquet.ParquetFormat",
        "partitioner.class": "io.confluent.connect.storage.partitioner.TimeBasedPartitioner",
        "partition.duration.ms": "3600000",
        "path.format": "'year'=YYYY/'month'=MM/'day'=dd/'hour'=HH",
        "flush.size": "10000"
    }
}
```

---

## 9. Local Setup with Docker

```yaml
# docker-compose.yml
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
    ports: ["2181:2181"]

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on: [zookeeper]
    ports: ["9092:9092"]
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_NUM_PARTITIONS: 3
      KAFKA_DEFAULT_REPLICATION_FACTOR: 1

  schema-registry:
    image: confluentinc/cp-schema-registry:7.5.0
    depends_on: [kafka]
    ports: ["8081:8081"]
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka:9092
```

```bash
# Topic management
kafka-topics --create --topic user-events --partitions 6 --replication-factor 1 --bootstrap-server localhost:9092
kafka-topics --list --bootstrap-server localhost:9092
kafka-topics --describe --topic user-events --bootstrap-server localhost:9092

# Console producer/consumer (testing)
kafka-console-producer --topic user-events --bootstrap-server localhost:9092
kafka-console-consumer --topic user-events --from-beginning --group test --bootstrap-server localhost:9092
```

---

## Key Takeaways
- Kafka = distributed commit log with topics and partitions
- Partition = unit of parallelism and ordering guarantee
- Consumer groups enable horizontal scaling of consumers
- Use `acks=all` + idempotent producer for reliability
- Schema Registry enforces data contracts between services
- Kafka Connect provides no-code source/sink integrations
- Choose at-least-once + idempotent consumers for most use cases

## Tomorrow
**Day 18**: Kafka Advanced — Stream processing with KSQL, Kafka Streams patterns, and production tuning.
