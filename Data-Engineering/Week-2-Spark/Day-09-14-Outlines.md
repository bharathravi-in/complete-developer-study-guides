# Week 2: Spark — Day Outlines

## Day 9: PySpark Core
- RDD fundamentals (map, filter, reduce, flatMap)
- DataFrames vs RDDs (always prefer DataFrames)
- Partitioning strategies (hash, range, custom)
- Repartition vs coalesce
- Reading various formats (Parquet, CSV, JSON, Delta)
- Schema inference vs explicit schema

## Day 10: Spark SQL & DataFrames
- Spark SQL syntax and Catalog
- Catalyst Optimizer (logical plan → physical plan)
- UDFs (Python, Pandas UDFs for vectorized ops)
- DataFrame API vs SQL (equivalent, preference is team choice)
- Complex types (arrays, maps, structs)
- Date/time operations

## Day 11: Spark Performance Tuning
- Reading the Spark UI (Jobs, Stages, Tasks, SQL)
- Identifying bottlenecks (shuffle, skew, spill)
- Partition count tuning (rule: 2-4x cores)
- Broadcast join threshold
- Adaptive Query Execution (AQE) in Spark 3+
- Caching strategy (when to persist, storage levels)
- Bucketing for repeated joins

## Day 12: Spark Structured Streaming
- Streaming DataFrames (same API as batch)
- Triggers (processingTime, once, continuous)
- Watermarks for late data handling
- Windowing (tumbling, sliding, session)
- Output modes (append, complete, update)
- Stateful operations (aggregations, deduplication)
- Exactly-once with checkpointing

## Day 13: Delta Lake & Lakehouse
- ACID transactions on data lake
- Time travel (VERSION AS OF, TIMESTAMP AS OF)
- Schema evolution (mergeSchema, overwriteSchema)
- MERGE (upserts): INSERT/UPDATE/DELETE in one operation
- OPTIMIZE (compaction) and ZORDER (co-location)
- Change Data Feed (CDC on Delta tables)
- Vacuum (cleanup old versions)
- Comparison: Delta Lake vs Iceberg vs Hudi

## Day 14: Project — Spark Data Pipeline
- Batch pipeline: Ingest CSV → Bronze → Silver → Gold
- Streaming pipeline: Kafka → Spark Streaming → Delta
- SCD Type 2 with Delta MERGE
- Data quality checks at each layer
- Performance testing and optimization
- Deploy on local Spark cluster (Docker)
