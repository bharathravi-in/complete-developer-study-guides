# Day 26: Real-Time Architectures

## Learning Objectives
- Compare Lambda, Kappa, and streaming-first architectures
- Implement event sourcing and CQRS for data systems
- Understand stream-table duality
- Choose the right architecture for your use case

---

## 1. Lambda Architecture

```
                    ┌─────────────────────┐
                    │    Batch Layer      │  (Recomputes all, high accuracy)
                    │  Spark/EMR/dbt      │
     Source ───┬───→│  Full recomputation │──→ Batch Views
               │    └─────────────────────┘         │
               │                                     ├──→ Serving Layer (merge)
               │    ┌─────────────────────┐         │
               └───→│    Speed Layer      │──→ Real-time Views
                    │  Kafka Streams/Flink │  (Approx, low latency)
                    └─────────────────────┘
```

### Implementation

```python
# Batch layer: Full recomputation (runs hourly/daily)
def batch_layer():
    """Recompute all metrics from scratch — source of truth."""
    df = spark.read.format("delta").load("/lake/silver/events")
    
    daily_metrics = (
        df.groupBy(F.to_date("event_time").alias("date"), "region")
        .agg(
            F.count("*").alias("total_events"),
            F.sum("amount").alias("total_revenue"),
            F.countDistinct("user_id").alias("unique_users"),
        )
    )
    
    daily_metrics.write.format("delta").mode("overwrite").save("/lake/gold/daily_metrics")

# Speed layer: Real-time approximation
def speed_layer():
    """Process only recent events for low-latency views."""
    stream = (
        spark.readStream.format("kafka")
        .option("subscribe", "events")
        .load()
    )
    
    real_time_metrics = (
        stream
        .withWatermark("event_time", "5 minutes")
        .groupBy(F.window("event_time", "1 hour"), "region")
        .agg(F.count("*").alias("events"), F.sum("amount").alias("revenue"))
    )
    
    real_time_metrics.writeStream.format("delta").outputMode("update") \
        .save("/lake/gold/realtime_metrics")

# Serving layer: Merge batch + speed
def serve_query(date, region):
    """Query merges batch (accurate) with speed (recent)."""
    batch_result = query_batch_view(date, region)
    speed_result = query_speed_view(date, region)  # Only for current period
    
    # Speed layer covers gap since last batch run
    if is_current_period(date):
        return merge_results(batch_result, speed_result)
    return batch_result
```

### Pros/Cons
- ✅ High accuracy (batch recomputes everything)
- ✅ Low latency (speed layer for recent data)
- ❌ Complex (maintain two code paths)
- ❌ Consistency issues (batch and speed may disagree)

---

## 2. Kappa Architecture

```
     Source ──→ Kafka (immutable log) ──→ Stream Processing ──→ Serving
                                              │
                                              └─→ Reprocess from beginning if logic changes
```

### Implementation

```python
# Single streaming pipeline — no batch layer
def kappa_pipeline():
    """Process everything as a stream. Reprocess = replay from beginning."""
    
    # Read from Kafka (retains events for replay)
    events = (
        spark.readStream.format("kafka")
        .option("subscribe", "events")
        .option("startingOffsets", "earliest")  # Can replay from beginning
        .load()
    )
    
    # Single processing logic (same code for real-time and backfill)
    processed = (
        events
        .select(F.from_json(F.col("value").cast("string"), schema).alias("data"))
        .select("data.*")
        .withWatermark("event_time", "10 minutes")
        .groupBy(F.window("event_time", "1 hour"), "region")
        .agg(
            F.count("*").alias("event_count"),
            F.sum("amount").alias("total_revenue"),
            F.approx_count_distinct("user_id").alias("approx_unique_users"),
        )
    )
    
    # Write to serving layer
    processed.writeStream \
        .format("delta") \
        .outputMode("update") \
        .option("checkpointLocation", "/checkpoints/kappa/metrics") \
        .start("/lake/gold/metrics")

# Reprocessing: Deploy new version, consume from beginning
# 1. Deploy new consumer with fresh consumer group
# 2. Process from earliest offset
# 3. Once caught up, switch serving layer to new output
# 4. Decommission old consumer
```

### Pros/Cons
- ✅ Simple (one code path)
- ✅ True real-time
- ✅ Easy to evolve logic (replay)
- ❌ Requires high Kafka retention (expensive for large volumes)
- ❌ Reprocessing takes time for large history
- ❌ Some computations hard in streaming (ML training, complex joins)

---

## 3. Event Sourcing + CQRS

```python
# Event Sourcing: Store events, derive state
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class Event:
    event_id: str
    aggregate_id: str  # e.g., order_id
    event_type: str    # e.g., "OrderCreated", "OrderShipped"
    data: dict
    timestamp: datetime
    version: int

@dataclass
class OrderAggregate:
    """Derive current state by replaying events."""
    order_id: str
    status: str = "unknown"
    items: list = field(default_factory=list)
    total: float = 0.0
    
    def apply(self, event: Event):
        if event.event_type == "OrderCreated":
            self.status = "created"
            self.items = event.data["items"]
            self.total = event.data["total"]
        elif event.event_type == "OrderPaid":
            self.status = "paid"
        elif event.event_type == "OrderShipped":
            self.status = "shipped"
            self.shipping_info = event.data
        elif event.event_type == "OrderCancelled":
            self.status = "cancelled"
            self.cancellation_reason = event.data.get("reason")

# Rebuild state from events
def get_order_state(order_id: str) -> OrderAggregate:
    events = event_store.get_events(aggregate_id=order_id)
    order = OrderAggregate(order_id=order_id)
    for event in events:
        order.apply(event)
    return order

# CQRS: Separate read and write models
class CommandHandler:
    """Write side: Process commands, emit events."""
    
    def create_order(self, command: dict) -> Event:
        # Validate
        if command["total"] <= 0:
            raise ValueError("Invalid order total")
        
        # Create event
        event = Event(
            event_id=generate_id(),
            aggregate_id=command["order_id"],
            event_type="OrderCreated",
            data={"items": command["items"], "total": command["total"]},
            timestamp=datetime.utcnow(),
            version=1,
        )
        
        # Persist to event store
        event_store.append(event)
        
        # Publish to Kafka for read-side projections
        kafka_producer.send("order-events", event)
        
        return event

class QueryHandler:
    """Read side: Optimized views for queries."""
    
    def get_order_summary(self, order_id: str) -> dict:
        # Read from materialized view (pre-computed)
        return redis.hgetall(f"order:{order_id}")
    
    def get_customer_orders(self, customer_id: str) -> list:
        # Read from denormalized read model
        return postgres.query(
            "SELECT * FROM order_summaries WHERE customer_id = %s", customer_id
        )

# Projector: Build read models from events
class OrderProjector:
    """Consume events, update read models."""
    
    def handle_event(self, event: Event):
        if event.event_type == "OrderCreated":
            # Update Redis (fast lookups)
            redis.hset(f"order:{event.aggregate_id}", mapping={
                "status": "created",
                "total": event.data["total"],
            })
            # Update PostgreSQL (complex queries)
            postgres.execute(
                "INSERT INTO order_summaries (order_id, status, total) VALUES (%s, %s, %s)",
                (event.aggregate_id, "created", event.data["total"])
            )
```

---

## 4. Stream-Table Duality

```python
# A stream is a changelog of a table
# A table is a snapshot of a stream at a point in time

# Stream → Table (aggregate stream to get current state)
# Kafka topic "user-updates" (stream of changes):
# {user_id: "u1", name: "John", timestamp: T1}
# {user_id: "u1", name: "Johnny", timestamp: T2}
# 
# Materialized as table:
# user_id | name    | last_updated
# u1      | Johnny  | T2

# Table → Stream (capture changes as events)
# PostgreSQL WAL → Debezium → Kafka topic
# Every INSERT/UPDATE/DELETE becomes a stream event

# Kafka Streams: KTable (table from topic)
# ksqlDB: CREATE TABLE users AS SELECT ... (latest value per key)

# In Spark:
# Table mode (latest per key)
latest_state = (
    events_stream
    .withWatermark("event_time", "1 hour")
    .groupBy("user_id")
    .agg(
        F.last("name").alias("name"),
        F.last("email").alias("email"),
        F.max("event_time").alias("last_updated"),
    )
)

# Log-compacted topic in Kafka = materialized table
# Only keeps latest value per key, deletes old versions
```

---

## 5. Choosing the Right Architecture

```
Decision Framework:
─────────────────────

1. LATENCY REQUIREMENT:
   - Minutes-hours acceptable → Batch (dbt, Spark batch)
   - Seconds → Streaming (Kafka Streams, Flink)
   - Sub-second → Pre-computed materialized views

2. DATA VOLUME:
   - < 10GB/day → Simple batch
   - 10GB - 1TB/day → Micro-batch (Spark Structured Streaming)
   - > 1TB/day → True streaming (Kafka Streams, Flink)

3. COMPLEXITY:
   - Simple aggregations → Streaming
   - Complex ML/joins → Batch or Lambda
   - Mix → Lambda or Streaming with batch supplements

4. REPROCESSING NEEDS:
   - Frequent logic changes → Kappa (replay from Kafka)
   - Stable logic → Either
   - Need exactly-right historical → Batch recomputation

RECOMMENDED FOR MOST TEAMS:
- Start with batch (simple, debuggable)
- Add streaming for specific low-latency needs
- Use Delta Lake for unified batch+stream
- Avoid Lambda complexity unless absolutely necessary
```

---

## 6. Materialized Views for Real-Time

```sql
-- PostgreSQL: Refreshable materialized view
CREATE MATERIALIZED VIEW mv_hourly_revenue AS
SELECT
    date_trunc('hour', order_date) AS hour,
    region,
    COUNT(*) AS orders,
    SUM(amount) AS revenue
FROM orders
WHERE order_date >= NOW() - INTERVAL '7 days'
GROUP BY 1, 2;

-- Refresh (can be triggered by Airflow)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_hourly_revenue;

-- Snowflake: Dynamic tables (auto-refresh)
CREATE DYNAMIC TABLE hourly_revenue
    TARGET_LAG = '1 minute'
    WAREHOUSE = realtime_wh
AS
    SELECT date_trunc('hour', order_date) AS hour, region, SUM(amount)
    FROM orders
    GROUP BY 1, 2;

-- ClickHouse: Real-time materialized views (insert-triggered)
CREATE MATERIALIZED VIEW mv_events
ENGINE = SummingMergeTree()
ORDER BY (date, region)
AS
    SELECT
        toDate(event_time) AS date,
        region,
        count() AS events,
        sum(amount) AS revenue
    FROM events_stream
    GROUP BY date, region;
```

---

## Interview Questions

### Beginner
1. **What is Lambda Architecture?** Dual-path: batch layer (full recomputation, accurate) + speed layer (real-time, approximate). Serving layer merges both. Addresses latency vs accuracy tradeoff.
2. **What is Kappa Architecture?** Stream-only: everything processed as a stream. To reprocess, replay from beginning of Kafka log. Simpler than Lambda but requires high retention.
3. **What is event sourcing?** Store all state changes as immutable events. Current state derived by replaying events. Enables full audit trail, temporal queries, and rebuilding state differently.

### Intermediate
4. **When would you choose Lambda over Kappa?** When: some computations require full dataset (ML training, graph algorithms), very long history needed (cost of Kafka retention), team has batch expertise. Kappa better for: simpler systems, all computations streamable, rapid iteration.
5. **Explain CQRS and why it's useful for data systems.** Command Query Responsibility Segregation: separate write model (event store, normalized) from read models (denormalized, optimized per use case). Allows multiple read views from same events. Read and write scale independently.
6. **What is stream-table duality?** Every stream can be materialized as a table (aggregate/compact), every table can be expressed as a stream (changelog). Kafka topic with compaction = table. CDC from database = stream. Unified view of batch and stream.

### Advanced
7. **Design a real-time recommendation system architecture.** Events stream (Kafka) → Feature computation (Flink/Spark Streaming) → Feature store (Redis) → Model serving (pre-computed scores in Redis, or real-time inference). Batch: retrain model daily on full history. Hybrid: batch for model, stream for features.
8. **How do you handle exactly-once in an event-sourced system?** Idempotent event processing (event_id-based dedup), transactional event store writes, outbox pattern for event publishing, consumer idempotency keys, saga pattern for distributed transactions.
9. **Design a migration from batch to streaming architecture.** Phase 1: Add Kafka alongside batch (dual-write). Phase 2: Build streaming consumers, validate output matches batch. Phase 3: Switch reads to streaming output. Phase 4: Decommission batch for migrated workloads. Keep batch for historical reprocessing.

---

## Hands-On Exercise
1. Implement a simple event-sourced order system
2. Build both batch and streaming aggregations, compare results
3. Implement CQRS with separate read/write models
4. Create a materialized view that auto-refreshes
5. Design architecture for: "real-time dashboard showing last 24h metrics"
6. Benchmark latency: batch vs micro-batch vs true streaming
