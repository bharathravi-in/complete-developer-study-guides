# Week 3: Orchestration & Streaming — Remaining Day Outlines

## Day 16: Airflow Advanced
- Dynamic DAGs (generate tasks from config/database)
- Custom operators and hooks
- TaskFlow API (@task decorator)
- Task Groups for DAG organization
- Testing DAGs (pytest, dag.test())
- Airflow Variables and Connections management
- Deployment patterns (Helm chart, managed services)

## Day 18: Kafka Advanced
- Kafka Streams (Java/Scala) concepts
- KSQL: SQL on streams (filter, join, aggregate)
- Kafka Connect: source and sink connectors
- Schema evolution with Schema Registry
- Exactly-once processing patterns
- Production tuning (partition count, replication, retention)
- Monitoring: consumer lag, throughput, latency

## Day 19: dbt (Data Build Tool)
- dbt project structure (models, tests, macros)
- Materializations (view, table, incremental, ephemeral)
- Incremental models (merge strategy, full refresh)
- Testing (generic tests: unique, not_null, relationships, custom)
- Documentation (descriptions, docs blocks)
- Macros and Jinja templating
- dbt packages and reusable code
- dbt Cloud vs dbt Core

## Day 20: Data Warehousing
- Snowflake architecture (virtual warehouses, auto-scaling)
- BigQuery (serverless, slots, BI Engine)
- Redshift (nodes, distribution keys, sort keys)
- Partitioning and clustering strategies
- Cost optimization (auto-suspend, query optimization)
- Cross-cloud comparison (when to choose what)
- Migration patterns (on-prem → cloud)

## Day 21: Project — Orchestrated Data Platform
- Full pipeline: Kafka → Airflow orchestration → dbt transforms → Warehouse
- Multiple data sources (API, database CDC, file uploads)
- Airflow sensors waiting for data arrival
- dbt models with tests and documentation
- Data quality alerts
- End-to-end monitoring dashboard
