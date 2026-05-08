# Data Engineering — Interview Prep

## Top 50 Interview Questions

### SQL & Data Modeling (Questions 1-10)

**1. Explain the difference between Star Schema and Snowflake Schema.**
- Star: Denormalized dimensions directly connected to fact table. Fewer joins, faster queries.
- Snowflake: Normalized dimensions with sub-dimensions. Less redundancy, more joins.
- Prefer Star for analytics workloads.

**2. What is a Slowly Changing Dimension? Explain SCD Types.**
- SCD 0: Never update (retain original)
- SCD 1: Overwrite (lose history)
- SCD 2: Add new row with valid_from/valid_to (preserve history) — most common
- SCD 3: Add previous_value column (limited history)

**3. What is the grain of a fact table?**
The grain defines what a single row represents (e.g., "one order line item per day"). Must be declared before designing the fact table. Getting grain wrong = broken analytics.

**4. Write a query to find the second-highest salary in each department.**
```sql
WITH ranked AS (
    SELECT *, DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rn
    FROM employees
)
SELECT * FROM ranked WHERE rn = 2;
```

**5. Explain window functions vs GROUP BY.**
- GROUP BY collapses rows into groups (1 output row per group)
- Window functions compute over a "window" without collapsing (original rows preserved)

**6. What is data lineage?**
The complete lifecycle of data — where it comes from, how it transforms, where it goes. Critical for debugging, compliance, and impact analysis.

**7. Explain normalization vs denormalization trade-offs.**
- Normalization: Reduces redundancy, ensures consistency, slower reads (more joins)
- Denormalization: Faster reads, redundancy, potential inconsistency
- OLTP → normalize; OLAP → denormalize

**8. What is a surrogate key vs natural key?**
- Natural: Business-meaningful (email, SSN) — can change!
- Surrogate: System-generated (auto-increment, UUID) — stable, used in DWH dimensions

**9. Explain the CAP theorem.**
- Consistency: All nodes see same data
- Availability: Every request gets a response
- Partition tolerance: System works despite network splits
- Choose 2 of 3 (in practice: CP or AP during partition)

**10. Design a fact table for ride-sharing (like Uber).**
Grain: One ride per row. Dimensions: driver, rider, location_pickup, location_dropoff, date, payment_method. Facts: distance, duration, fare, surge_multiplier, tip_amount.

---

### Spark & Big Data (Questions 11-20)

**11. Explain Spark's lazy evaluation.**
Transformations build a DAG but don't execute. Actions (count, show, write) trigger execution. Benefits: Catalyst optimizer can reorganize the entire DAG for efficiency.

**12. What is a shuffle in Spark?**
Redistribution of data across partitions. Triggered by groupBy, join, repartition, distinct. Expensive (network + disk I/O). Minimize with broadcast joins, pre-partitioning.

**13. When would you use broadcast join?**
When one side of the join is small enough to fit in executor memory (< 10MB default). Eliminates shuffle for the small table. Set: `spark.sql.autoBroadcastJoinThreshold`.

**14. Explain Spark's memory management.**
Unified Memory = Storage + Execution. Storage: cached DataFrames. Execution: shuffles, sorts, aggregations. They can borrow from each other. OOM = increase executor memory or reduce partition size.

**15. What is data skew and how do you fix it?**
When some partitions have much more data than others. Fixes: salt the key, use Adaptive Query Execution (AQE), repartition, custom partitioner, or filter hot keys separately.

**16. Compare Spark batch vs Structured Streaming.**
Same API (DataFrames). Batch: reads finite data. Streaming: reads infinite data with triggers (micro-batch or continuous). Watermarks handle late data.

**17. Explain Delta Lake's benefits over plain Parquet.**
ACID transactions, time travel (version history), schema enforcement/evolution, MERGE/UPSERT support, optimistic concurrency, small file compaction (OPTIMIZE).

**18. How to tune a slow Spark job?**
1. Check Spark UI (stages, tasks, shuffle read/write)
2. Look for skew (one task much slower)
3. Check for shuffle (reduce with broadcast)
4. Adjust partition count (spark.sql.shuffle.partitions)
5. Cache intermediate results if reused
6. Enable AQE

**19. RDD vs DataFrame vs Dataset.**
- RDD: Low-level, no optimization, type-safe (Scala)
- DataFrame: Optimized (Catalyst), schema-aware, no type safety
- Dataset: Optimized + type-safe (Scala/Java only)
- Use DataFrame/SQL in PySpark always.

**20. Explain Spark's execution plan (explain output).**
Physical Plan → Stages → Tasks. Key things: scan type (FileScan vs InMemory), join strategy (BroadcastHash vs SortMerge), exchange (shuffle), and filter pushdown.

---

### Kafka & Streaming (Questions 21-30)

**21. Explain Kafka's architecture.**
Brokers store data in topics. Topics split into partitions. Producers write to partitions (by key hash). Consumer groups read with one consumer per partition max. Replication for fault tolerance.

**22. How does Kafka guarantee ordering?**
Ordering guaranteed WITHIN a partition only. Same key → same partition → ordered. No global ordering across partitions. If you need total order: use single partition (limits throughput).

**23. Explain exactly-once semantics in Kafka.**
- Idempotent producer (deduplicates at broker)
- Transactional producer (atomic writes across partitions)
- Consumer: read_committed isolation level
- Or: at-least-once + idempotent consumer (simpler, recommended)

**24. What is consumer lag?**
Difference between latest offset produced and last offset consumed. High lag = consumer can't keep up. Monitor with `kafka-consumer-groups --describe`. Fix: add consumers, optimize processing.

**25. Explain Schema Registry.**
Centralized schema storage (Avro, JSON Schema, Protobuf). Enforces compatibility between producer and consumer. Prevents breaking changes. Schemas versioned and validated.

---

### Airflow & Orchestration (Questions 26-35)

**26. What is a DAG in Airflow?**
Directed Acyclic Graph — defines tasks and their dependencies. Python code that describes WHAT to run and WHEN, not HOW (the how is in operators).

**27. Explain Airflow's execution date.**
The execution_date represents the START of the period being processed, not when the DAG actually runs. A daily DAG with execution_date=Jan 1 runs on Jan 2 and processes Jan 1 data.

**28. How to make an Airflow task idempotent?**
Use execution_date for processing windows. DELETE+INSERT pattern (replace partition). Never use `datetime.now()` — always `{{ ds }}`. Same input → same output regardless of retries.

**29. XCom vs external storage for task communication.**
XCom: small metadata (< 48KB), stored in Airflow DB. Use for: file paths, record counts, status. External (S3, GCS): large data. Never pass DataFrames via XCom.

**30. Compare Airflow executors.**
- SequentialExecutor: One task at a time (dev only)
- LocalExecutor: Parallel on single machine
- CeleryExecutor: Distributed workers via Celery
- KubernetesExecutor: One pod per task (best isolation, scaling)

---

### System Design (Questions 31-40)

**31. Design a real-time analytics pipeline for an e-commerce site.**
Events → Kafka → Spark Streaming (aggregate) → Redis (real-time dashboard) + S3 (raw) → Spark batch (daily rollup) → Data Warehouse → BI tools.

**32. Design a data pipeline for fraud detection.**
Transaction events → Kafka → Feature computation (Flink/Spark) → Feature store → ML model serving (< 100ms) → Alert/Block. Batch retraining daily with MLflow.

**33. How would you handle late-arriving data?**
1. Watermarks in streaming (grace period)
2. Incremental partition updates (re-process partition when late data arrives)
3. Lambda architecture (batch corrects streaming)
4. Append-only + dedup at query time

**34. Design a CDC pipeline from PostgreSQL to a data lake.**
PostgreSQL WAL → Debezium → Kafka → S3 sink connector (Parquet, hourly partitions) → Delta Lake merge (upserts) → dbt transforms → Data Warehouse.

**35. How do you handle schema evolution in a data lake?**
Use Delta Lake/Iceberg (schema enforcement + evolution). Add columns = backward compatible. Remove/rename = requires migration. Schema Registry for streaming. dbt handles transformation-layer evolution.

---

### Data Quality & Operations (Questions 36-50)

**36. How do you ensure data quality?**
1. Schema validation at ingestion
2. Null/completeness checks
3. Freshness monitoring (SLA)
4. Statistical tests (distribution drift)
5. dbt tests (unique, not_null, accepted_values)
6. Great Expectations for complex rules

**37. Explain data contracts.**
Agreement between producer and consumer defining: schema, SLAs (freshness, completeness), ownership, and change process. Prevents breaking downstream consumers.

**38. How do you monitor data pipelines?**
- Pipeline health: success/failure rates, duration trends
- Data quality: completeness, freshness, validity
- Infrastructure: resource usage, costs
- Tools: Airflow UI, DataDog, Monte Carlo, custom dashboards

**39. Explain backfilling.**
Re-running historical pipeline runs to process old data or fix past errors. Airflow: `airflow dags backfill -s start_date -e end_date`. Requires idempotent tasks!

**40. How do you handle PII in data pipelines?**
- Classify data (PII, sensitive, public)
- Encrypt at rest and in transit
- Tokenize/hash PII early in pipeline
- Row-level security in warehouse
- Access control + audit logging
- Comply with GDPR/CCPA (right to deletion)

---

## Common Take-Home Assignments

1. **Build an ETL pipeline** that ingests CSV, validates, transforms, loads to DB
2. **Design a data model** for a given business (e-commerce, social media)
3. **Optimize a slow SQL query** (given EXPLAIN plan, suggest improvements)
4. **Stream processing** mini-project with Kafka + Python
5. **Data quality framework** with automated checks and alerting
