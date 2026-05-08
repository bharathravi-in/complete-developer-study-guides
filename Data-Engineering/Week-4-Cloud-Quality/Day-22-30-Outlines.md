# Week 4: Cloud, Quality & Interview — Day Outlines

## Day 22: AWS Data Stack
- S3 (storage tiers, lifecycle policies, partitioning)
- AWS Glue (ETL jobs, crawlers, Data Catalog)
- Athena (serverless SQL on S3, Parquet optimization)
- Redshift Spectrum (query S3 from Redshift)
- Kinesis (Data Streams, Firehose, Analytics)
- EMR (managed Spark/Hadoop clusters)
- Step Functions (orchestration alternative)
- Lake Formation (governance, permissions)

## Day 23: GCP Data Stack
- BigQuery (serverless, slots, streaming inserts, ML)
- Cloud Dataflow (Apache Beam, batch + stream)
- Pub/Sub (messaging, exactly-once)
- Cloud Composer (managed Airflow)
- Dataproc (managed Spark)
- Cloud Storage (GCS, lifecycle, transfer)
- Looker / Data Studio (BI layer)

## Day 24: Data Quality & Observability
- Data quality dimensions (completeness, accuracy, freshness, consistency)
- Great Expectations (expectations, checkpoints, data docs)
- dbt tests (schema, custom, relationships)
- Monte Carlo (automated anomaly detection)
- Data SLAs and SLOs
- Alerting and incident response
- Building a quality dashboard

## Day 25: Data Governance & Cataloging
- Data lineage (column-level, end-to-end)
- Metadata management (DataHub, OpenMetadata, Amundsen)
- Data classification (PII, sensitive, public)
- Access control (RBAC, ABAC, row-level security)
- Compliance (GDPR, CCPA, HIPAA)
- Data mesh principles (domain ownership, data as product)
- Data contracts between teams

## Day 26: Real-Time Architectures
- Lambda Architecture (batch + speed layers)
- Kappa Architecture (stream-only)
- Streaming-first design
- Materialized views for real-time aggregation
- Event sourcing + CQRS for data systems
- Stream-table duality (Kafka as source of truth)
- Choosing batch vs stream vs hybrid

## Day 27: Performance & Cost Optimization
- File format optimization (Parquet, compression codecs)
- Partition pruning and predicate pushdown
- Columnar storage best practices
- Query optimization (warehouse-specific)
- Cost monitoring and budgets
- Right-sizing compute resources
- Reserved vs on-demand pricing
- Data lifecycle management (hot/warm/cold)

## Day 28: System Design for Data Engineering
- Design: Uber real-time surge pricing pipeline
- Design: Netflix viewing analytics platform
- Design: Twitter trending topics
- Design: E-commerce recommendation data pipeline
- Design: Financial transaction processing
- Framework: Requirements → Data flow → Storage → Processing → Serving

## Day 29: Interview Prep
- Top 50 questions review (see Interview-Prep/)
- SQL coding challenges (LeetCode SQL)
- System design practice (whiteboard)
- Take-home project patterns
- Behavioral questions for DE roles
- Salary negotiation for DE positions

## Day 30: Capstone Project
- Full data platform implementation
- Sources: REST API + PostgreSQL CDC + CSV uploads
- Ingestion: Kafka (streaming) + Airflow (batch)
- Storage: S3/MinIO (data lake) + PostgreSQL (warehouse)
- Transformation: dbt models (bronze → silver → gold)
- Quality: Great Expectations + dbt tests
- Serving: REST API + Dashboard
- Documentation: Architecture diagram + runbook
