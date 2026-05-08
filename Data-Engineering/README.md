# Data Engineering — 30-Day Mastery Plan

## Goal
Go from fundamentals to production-ready Data Engineer in 30 days. Covers the modern data stack: pipelines, orchestration, streaming, warehousing, and lakehouse architecture.

## Prerequisites
- Python intermediate+ (see `../Python/`)
- PostgreSQL basics (see `../PostgreSQL/`)
- Docker basics (see `../DevOps/`)

---

## Weekly Breakdown

### Week 1: Foundations — SQL, Data Modeling & ETL (Days 1–7)
| Day | Topic | Focus |
|-----|-------|-------|
| 1 | Data Engineering Landscape | Roles, tools, batch vs streaming, modern data stack |
| 2 | Advanced SQL for DE | Window functions, CTEs, LATERAL joins, query optimization |
| 3 | Data Modeling — Dimensional | Star schema, snowflake, Kimball methodology |
| 4 | Data Modeling — Data Vault & 3NF | Hubs/Links/Satellites, when to use what |
| 5 | ETL vs ELT Patterns | Extract-Transform-Load, CDC, idempotency, SCD types |
| 6 | Python for Data Engineering | Pandas at scale, Polars, DuckDB, data validation |
| 7 | Project: Build ETL Pipeline | End-to-end pipeline with Python + PostgreSQL |

### Week 2: Apache Spark & Big Data (Days 8–14)
| Day | Topic | Focus |
|-----|-------|-------|
| 8 | Spark Architecture | Driver, executors, DAG, lazy evaluation, cluster managers |
| 9 | PySpark Core | RDDs, transformations, actions, partitioning |
| 10 | Spark SQL & DataFrames | Schema inference, Catalyst optimizer, UDFs |
| 11 | Spark Performance | Shuffles, broadcasting, caching, skew handling |
| 12 | Spark Streaming | Structured Streaming, watermarks, triggers, windowing |
| 13 | Delta Lake & Lakehouse | ACID on data lake, time travel, schema evolution, Iceberg/Hudi |
| 14 | Project: Spark Data Pipeline | Batch + streaming pipeline with Delta Lake |

### Week 3: Orchestration, Streaming & Warehousing (Days 15–21)
| Day | Topic | Focus |
|-----|-------|-------|
| 15 | Apache Airflow Fundamentals | DAGs, operators, sensors, XComs, connections |
| 16 | Airflow Advanced | Dynamic DAGs, custom operators, testing, best practices |
| 17 | Apache Kafka Fundamentals | Topics, partitions, consumer groups, offsets, exactly-once |
| 18 | Kafka Advanced | Schema Registry, Kafka Connect, KSQL, stream processing |
| 19 | dbt (Data Build Tool) | Models, tests, documentation, macros, incremental models |
| 20 | Data Warehousing | Snowflake/BigQuery/Redshift architecture, partitioning, clustering |
| 21 | Project: Orchestrated Data Platform | Airflow + Kafka + dbt end-to-end |

### Week 4: Cloud, Quality & Interview Prep (Days 22–30)
| Day | Topic | Focus |
|-----|-------|-------|
| 22 | AWS Data Stack | S3, Glue, Athena, Redshift, Kinesis, EMR |
| 23 | GCP Data Stack | BigQuery, Dataflow, Pub/Sub, Cloud Composer, Dataproc |
| 24 | Data Quality & Observability | Great Expectations, Monte Carlo, data contracts, SLAs |
| 25 | Data Governance & Cataloging | Lineage, metadata (DataHub, OpenMetadata), PII handling |
| 26 | Real-time Architectures | Lambda vs Kappa, streaming-first, materialized views |
| 27 | Performance & Cost Optimization | Partition pruning, file formats (Parquet/ORC/Avro), compression |
| 28 | System Design for DE | Design: Uber surge pricing pipeline, Netflix analytics |
| 29 | Interview Prep | Common DE interview questions, SQL challenges, take-home patterns |
| 30 | Capstone Project | Full data platform: ingest → transform → warehouse → dashboard |

---

## Key Technologies Covered
- **Languages**: Python, SQL
- **Processing**: Apache Spark, PySpark, Polars, DuckDB
- **Orchestration**: Apache Airflow, Dagster (intro)
- **Streaming**: Apache Kafka, Spark Structured Streaming
- **Storage**: PostgreSQL, Delta Lake, Apache Iceberg, Parquet
- **Warehousing**: Snowflake, BigQuery, Redshift
- **Transformation**: dbt
- **Cloud**: AWS (Glue, EMR, Kinesis), GCP (Dataflow, Composer)
- **Quality**: Great Expectations, dbt tests
- **Containers**: Docker, Docker Compose

## Study Approach
- 2–3 hours/day minimum
- Each day: Theory (30 min) → Hands-on coding (60 min) → Mini-project (30 min)
- Weekend projects tie together the week's concepts
