# Day 28: System Design for Data Engineering

## Learning Objectives
- Apply a structured framework for data system design interviews
- Design end-to-end data platforms for real-world companies
- Handle scale, fault tolerance, and evolving requirements
- Communicate tradeoffs clearly

---

## 1. System Design Framework

```
Step 1: REQUIREMENTS (5 min)
├── Functional: What does the system do?
├── Non-functional: Scale, latency, consistency, availability
├── Data characteristics: Volume, velocity, variety
└── Constraints: Budget, team size, existing tech

Step 2: HIGH-LEVEL DESIGN (10 min)
├── Data flow: Source → Ingestion → Processing → Storage → Serving
├── Components: What goes where
└── Key interfaces between components

Step 3: DEEP DIVE (15 min)
├── Core challenges: What makes this hard?
├── Data model: Schema, partitioning, indexing
├── Processing: Batch vs stream, transformations
└── Storage: Hot/warm/cold, formats

Step 4: TRADEOFFS & SCALING (5 min)
├── Bottlenecks and mitigation
├── Failure modes and recovery
├── Cost vs performance decisions
└── Future evolution
```

---

## 2. Design: Uber Surge Pricing Pipeline

### Requirements
- Real-time supply/demand per geohash (100m² cells)
- 50M rides/day, 5M drivers sending location every 5 seconds
- Surge multiplier calculated every 30 seconds per zone
- Historical analytics for pricing team

### Architecture

```
Driver GPS (5s intervals)           Rider Requests
    │                                    │
    ▼                                    ▼
┌────────────────────────────────────────────────────┐
│              Kafka (geo-partitioned)                 │
│  Topics: driver-locations, ride-requests             │
└─────────────┬──────────────────────┬───────────────┘
              │                      │
              ▼                      ▼
┌──────────────────────┐   ┌──────────────────────┐
│  Flink: Driver       │   │  Flink: Demand       │
│  Aggregation         │   │  Aggregation         │
│  (count per geohash  │   │  (requests per       │
│   per 30s window)    │   │   geohash per 30s)   │
└──────────┬───────────┘   └──────────┬───────────┘
           │                           │
           ▼                           ▼
┌─────────────────────────────────────────────────────┐
│     Flink: Surge Calculator                          │
│     surge = demand / supply × base_multiplier        │
│     + smoothing (prevent rapid fluctuations)         │
│     + caps (max 5x)                                  │
└──────────────────────┬──────────────────────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
    ┌──────────────────┐  ┌──────────────────┐
    │  Redis Cluster   │  │  Kafka → S3      │
    │  (current surge  │  │  (historical     │
    │   per geohash)   │  │   for analytics) │
    └──────────────────┘  └──────────────────┘
              │                      │
              ▼                      ▼
    Pricing Service             Spark Batch
    (query Redis for            (daily aggregates,
     ride pricing)              ML model training)
```

### Key Design Decisions

```python
# Geohash partitioning for locality
import geohash2

def partition_key(lat: float, lon: float, precision: int = 6) -> str:
    """Geohash precision 6 ≈ 1.2km × 600m cell."""
    return geohash2.encode(lat, lon, precision)

# Flink windowed aggregation (pseudocode)
"""
driver_supply = driver_locations
    .keyBy(event -> geohash(event.lat, event.lon, 6))
    .window(TumblingEventTimeWindows.of(Time.seconds(30)))
    .aggregate(CountFunction())

ride_demand = ride_requests
    .keyBy(event -> geohash(event.pickup_lat, event.pickup_lon, 6))
    .window(TumblingEventTimeWindows.of(Time.seconds(30)))
    .aggregate(CountFunction())

# Join supply and demand
surge = driver_supply.connect(ride_demand)
    .keyBy(s -> s.geohash, d -> d.geohash)
    .process(SurgeCalculator())
"""

# Surge calculation with smoothing
def calculate_surge(supply: int, demand: int, prev_surge: float) -> float:
    if supply == 0:
        raw_surge = 5.0  # Cap
    else:
        raw_surge = min(demand / max(supply, 1), 5.0)
    
    # Exponential smoothing (prevent sudden jumps)
    alpha = 0.3
    smoothed = alpha * raw_surge + (1 - alpha) * prev_surge
    
    # Round to nearest 0.1
    return round(max(1.0, smoothed), 1)
```

---

## 3. Design: Netflix Analytics Platform

### Requirements
- 250M subscribers, 1B+ hours streamed/month
- Track: plays, pauses, seeks, quality changes, buffering
- Real-time: viewing now, trending, system health
- Batch: recommendations, A/B tests, content valuation

### Architecture

```
Devices (TV, Mobile, Web)
    │ (events via HTTP/gRPC)
    ▼
┌──────────────────────────────────┐
│  Gateway (validate, enrich)       │
│  + Schema Registry               │
└──────────────┬───────────────────┘
               ▼
┌──────────────────────────────────┐
│        Kafka Cluster              │
│  Topics: playback-events,         │
│          quality-events,          │
│          user-interactions        │
│  (Partitioned by user_id)         │
│  Retention: 7 days                │
└──────┬───────────────┬───────────┘
       │               │
       ▼               ▼
┌──────────────┐  ┌──────────────────────────┐
│ Flink        │  │ Spark Structured Streaming│
│ (real-time)  │  │ (near-real-time)          │
│ - Viewing    │  │ - User sessions           │
│   now count  │  │ - Engagement metrics      │
│ - Trending   │  │ - Quality aggregates      │
│ - Anomalies  │  └─────────────┬────────────┘
└──────┬───────┘                │
       │                        ▼
       ▼               ┌──────────────────────┐
┌──────────────┐       │  S3 Data Lake         │
│ Elasticsearch│       │  Bronze: raw events   │
│ (real-time   │       │  Silver: cleaned,     │
│  dashboards) │       │         sessionized   │
│              │       │  Gold: aggregates     │
└──────────────┘       └─────────────┬────────┘
                                     │
                                     ▼
                       ┌──────────────────────────┐
                       │ Spark Batch (daily)       │
                       │ - Recommendation models  │
                       │ - Content valuation      │
                       │ - A/B test analysis      │
                       └─────────────┬────────────┘
                                     │
                                     ▼
                       ┌──────────────────────────┐
                       │ Serving: Druid/Presto    │
                       │ (interactive analytics)  │
                       └──────────────────────────┘
```

### Session Construction

```python
# Sessionize viewing events
def build_sessions(events_df):
    """Group events into viewing sessions (30-min inactivity gap)."""
    from pyspark.sql import functions as F, Window
    
    w = Window.partitionBy("user_id", "content_id").orderBy("event_time")
    
    sessionized = (
        events_df
        .withColumn("prev_time", F.lag("event_time").over(w))
        .withColumn("gap_minutes", 
            (F.col("event_time").cast("long") - F.col("prev_time").cast("long")) / 60
        )
        .withColumn("new_session", F.when(F.col("gap_minutes") > 30, 1).otherwise(0))
        .withColumn("session_id", F.sum("new_session").over(w))
    )
    
    # Aggregate per session
    sessions = (
        sessionized
        .groupBy("user_id", "content_id", "session_id")
        .agg(
            F.min("event_time").alias("session_start"),
            F.max("event_time").alias("session_end"),
            F.count("*").alias("event_count"),
            F.sum(F.when(F.col("event_type") == "play", F.col("duration_ms"))).alias("watch_time_ms"),
            F.sum(F.when(F.col("event_type") == "buffer", 1)).alias("buffer_count"),
            F.max("quality").alias("max_quality"),
        )
    )
    
    return sessions
```

---

## 4. Design: Twitter/X Trending Topics

### Requirements
- 500M tweets/day, detect trending topics within 5 minutes
- Regional and global trends
- Filter spam/bots, personalize trends
- Historical: what trended when, engagement curves

### Architecture

```
Tweets (API)
    │
    ▼
Kafka → Flink (stream processing)
    │
    ├── Extract entities: hashtags, phrases, named entities (NER)
    │
    ├── Count per entity per time window (5-min tumbling)
    │
    ├── Compare to baseline (last 24h rolling average)
    │   Trend score = (current_count - baseline) / std_dev
    │
    ├── Filter: spam detection, bot filtering
    │
    └── Rank: Top-N per region + global
         │
         ▼
    Redis (current trends, TTL=10min)
         │
         ▼
    Trending API (serves mobile/web)
```

### Trending Detection Algorithm

```python
from collections import defaultdict
import math

class TrendingDetector:
    """Detect trending topics using statistical anomaly detection."""
    
    def __init__(self, window_minutes: int = 5, baseline_hours: int = 24):
        self.window_minutes = window_minutes
        self.baseline_hours = baseline_hours
        self.current_counts = defaultdict(int)   # topic → count this window
        self.baseline_stats = {}                   # topic → (mean, std)
    
    def process_event(self, topic: str):
        self.current_counts[topic] += 1
    
    def compute_trends(self) -> list[dict]:
        """Compute trend scores at end of each window."""
        trends = []
        for topic, count in self.current_counts.items():
            baseline = self.baseline_stats.get(topic, {"mean": 10, "std": 5})
            mean, std = baseline["mean"], max(baseline["std"], 1)
            
            # Z-score: how many standard deviations above normal
            z_score = (count - mean) / std
            
            # Velocity: rate of change (acceleration matters)
            # Higher weight for topics that are accelerating
            
            if z_score > 3.0:  # Significant spike
                trends.append({
                    "topic": topic,
                    "score": z_score,
                    "count": count,
                    "baseline_mean": mean,
                })
        
        # Sort by score, return top N
        trends.sort(key=lambda x: x["score"], reverse=True)
        return trends[:50]
    
    def update_baseline(self, historical_counts: dict):
        """Update baseline from last 24h (runs periodically)."""
        for topic, counts_per_window in historical_counts.items():
            mean = sum(counts_per_window) / len(counts_per_window)
            variance = sum((c - mean) ** 2 for c in counts_per_window) / len(counts_per_window)
            self.baseline_stats[topic] = {"mean": mean, "std": math.sqrt(variance)}
```

---

## 5. Design: E-Commerce Recommendation Pipeline

### Architecture

```
User Activity              Product Catalog           Order History
(clicks, views,            (features, categories)    (purchases, returns)
 search, cart)
    │                           │                         │
    └───────────────────────────┼─────────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Feature Store        │
                    │   - User features      │
                    │   - Item features      │
                    │   - Interaction feats   │
                    └─────────┬─────────────┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
         ┌──────────┐  ┌──────────┐  ┌──────────┐
         │Candidate │  │ Ranking  │  │ Real-time│
         │Generation│  │  Model   │  │ Features │
         │(ALS/ANN) │  │(XGBoost) │  │(Flink)   │
         └────┬─────┘  └────┬─────┘  └────┬─────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
                             ▼
                    ┌───────────────────────┐
                    │  Re-ranking Layer      │
                    │  (diversity, business  │
                    │   rules, freshness)    │
                    └───────────┬───────────┘
                                │
                                ▼
                    Personalized Recommendations
                    (cached in Redis, TTL=1hr)
```

### Feature Engineering

```python
# Batch features (computed daily)
user_features = (
    orders_df
    .groupBy("user_id")
    .agg(
        F.count("*").alias("total_orders"),
        F.avg("order_value").alias("avg_order_value"),
        F.max("order_date").alias("last_order_date"),
        F.countDistinct("category").alias("category_diversity"),
        F.collect_set("category").alias("preferred_categories"),
    )
)

# Real-time features (Flink/Spark Streaming)
# Last 30 min: categories viewed, items in cart, search queries
realtime_features = (
    activity_stream
    .withWatermark("event_time", "5 minutes")
    .groupBy("user_id", F.window("event_time", "30 minutes"))
    .agg(
        F.collect_list("category_viewed").alias("recent_categories"),
        F.count(F.when(F.col("event") == "add_to_cart", 1)).alias("cart_additions"),
        F.collect_list("search_query").alias("recent_searches"),
    )
)
```

---

## 6. Design: Financial Transaction Pipeline

### Requirements
- Process 100K transactions/second
- Fraud detection within 100ms
- Regulatory compliance (7-year retention, audit trail)
- Exactly-once processing guarantee

### Architecture

```python
"""
Transaction → API Gateway → Kafka (exactly-once) 
    │
    ├── Flink (real-time fraud detection)
    │   ├── Rule-based: velocity checks, amount limits
    │   ├── ML model: fraud probability score
    │   └── Output: approve/reject/review
    │
    ├── Flink (compliance)
    │   ├── AML pattern detection
    │   ├── Sanctions screening
    │   └── Report generation
    │
    └── S3 (immutable audit log)
        ├── Raw transactions (7-year retention)
        ├── Parquet (for analytics)
        └── Delta Lake (ACID, time travel)

Key Design Decisions:
- Kafka with exactly-once semantics (idempotent producers + transactional consumers)
- Flink for <100ms processing with checkpointing
- Event sourcing: all state changes as immutable events
- Encryption at rest + in transit + field-level for PII
- Separate clusters for PCI compliance zone
"""

# Fraud detection rules (Flink pseudocode)
class FraudDetector:
    def evaluate(self, transaction, user_history) -> str:
        score = 0.0
        
        # Rule 1: Velocity (>5 transactions in 1 minute)
        recent_count = user_history.count_last_minutes(1)
        if recent_count > 5:
            score += 0.3
        
        # Rule 2: Amount anomaly (3x user's average)
        if transaction.amount > user_history.avg_amount * 3:
            score += 0.25
        
        # Rule 3: New location
        if transaction.location not in user_history.known_locations:
            score += 0.2
        
        # Rule 4: ML model score
        ml_score = self.ml_model.predict(transaction.features)
        score += ml_score * 0.5
        
        if score > 0.8:
            return "REJECT"
        elif score > 0.5:
            return "REVIEW"
        return "APPROVE"
```

---

## Interview Questions

### Beginner
1. **Walk me through your system design approach.** Requirements (5 min) → High-level design (10 min) → Deep dive on core challenge (15 min) → Tradeoffs and scaling (5 min). Always clarify requirements before designing.
2. **How do you estimate scale?** Back-of-envelope: users × events/user/day = events/day. Divide by 86,400 for events/sec. Data volume: events × avg_size. Storage: volume × retention × replication.
3. **Batch vs streaming: when to choose?** Batch: latency acceptable (minutes-hours), complex logic, full dataset operations. Streaming: low latency needed (seconds), event-driven, continuous output.

### Intermediate
4. **Design a real-time leaderboard for a gaming platform.** Kafka for game events → Flink for score aggregation → Redis Sorted Sets for leaderboard (ZADD, ZREVRANGE). Challenge: millions of players, need top-100 globally + friend rankings. Solution: sharded Redis, approximate counts, cache friend lists.
5. **How do you handle late-arriving data?** Watermarks (allowed lateness), append-only with later compaction, separate late-data pipeline that updates existing aggregates, Delta Lake MERGE for corrections.
6. **Design a data pipeline for a startup vs enterprise.** Startup: simple stack (Fivetran → BigQuery → dbt → Looker), managed services, minimize ops. Enterprise: Kafka + Spark + Airflow + Delta Lake, multiple environments, governance, RBAC, compliance.

### Advanced
7. **Design a pipeline handling 1M events/second with exactly-once guarantees.** Kafka (partitioned, idempotent producers, transactional consumers) → Flink (checkpointing, exactly-once sinks) → Delta Lake (idempotent writes). End-to-end exactly-once requires: dedup at source (event_id), transactional processing, idempotent sinks.
8. **Your pipeline has 2-hour SLA. It's taking 3 hours. How do you fix it?** Diagnose: Spark UI (which stage slow?), data skew?, shuffle?, small files? Quick fixes: increase parallelism, fix skew (salting), partition pruning. Medium: change join strategy, cache intermediate. Long: redesign (incremental vs full, better partitioning).
9. **Design a multi-region active-active data platform.** Each region: full pipeline (ingest → process → serve). Cross-region: Kafka MirrorMaker for replication. Conflict resolution: last-writer-wins or CRDT. Global aggregations: async consolidation. Challenges: consistency (CAP theorem), cost of replication.

---

## Hands-On Exercise
1. Pick a system design problem and practice the 4-step framework
2. Estimate scale for: "Design analytics for a food delivery app with 10M users"
3. Draw architecture for: "Real-time inventory tracking for 1000 warehouses"
4. Identify tradeoffs for: "100ms latency requirement vs exactly-once processing"
5. Practice explaining decisions aloud (communicate like an interview)
