# Day 25: Data Governance & Cataloging

## Learning Objectives
- Implement data lineage and metadata management
- Set up data catalogs (DataHub, OpenMetadata)
- Apply compliance frameworks (GDPR, CCPA)
- Design data mesh and data contracts

---

## 1. Data Lineage

### Column-Level Lineage

```python
# Track how each column is derived
from dataclasses import dataclass, field

@dataclass
class ColumnLineage:
    target_table: str
    target_column: str
    source_table: str
    source_column: str
    transformation: str  # e.g., "SUM", "CAST", "JOIN"

# Example lineage for gold.daily_revenue.total_revenue
lineage = [
    ColumnLineage("gold.daily_revenue", "total_revenue", "silver.orders", "amount", "SUM"),
    ColumnLineage("silver.orders", "amount", "bronze.raw_orders", "order_total", "CAST(DECIMAL)"),
    ColumnLineage("bronze.raw_orders", "order_total", "source.oltp.orders", "total", "COPY"),
]

# OpenLineage integration (standard for lineage)
from openlineage.client import OpenLineageClient
from openlineage.client.run import Run, RunEvent, RunState
from openlineage.client.facet import SqlJobFacet, ColumnLineageDatasetFacet

client = OpenLineageClient(url="http://marquez:5000")

# Emit lineage event
run_event = RunEvent(
    eventType=RunState.COMPLETE,
    job={"namespace": "dbt", "name": "fct_daily_revenue"},
    run=Run(runId="abc-123"),
    inputs=[
        {"namespace": "warehouse", "name": "silver.orders",
         "facets": {"columnLineage": ColumnLineageDatasetFacet(...)}}
    ],
    outputs=[
        {"namespace": "warehouse", "name": "gold.daily_revenue"}
    ],
)
client.emit(run_event)
```

---

## 2. Data Catalog with DataHub

```python
# DataHub - metadata platform
from datahub.emitter.mce_builder import make_dataset_urn
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    DatasetPropertiesClass,
    SchemaMetadataClass,
    SchemaFieldClass,
    TagAssociationClass,
    GlossaryTermAssociationClass,
)

emitter = DatahubRestEmitter("http://datahub:8080")

# Register a dataset with metadata
dataset_urn = make_dataset_urn("postgres", "warehouse.analytics.fct_orders")

# Add properties
properties = DatasetPropertiesClass(
    name="Fact Orders",
    description="All completed orders with customer and product enrichment",
    customProperties={
        "owner": "data-engineering@company.com",
        "sla": "2 hours",
        "pii": "false",
        "tier": "gold",
        "refresh_frequency": "hourly",
    },
)

# Add schema
schema = SchemaMetadataClass(
    schemaName="fct_orders",
    fields=[
        SchemaFieldClass(
            fieldPath="order_id",
            type={"type": {"com.linkedin.schema.StringType": {}}},
            description="Unique order identifier",
            nullable=False,
            globalTags=TagAssociationClass(tags=[make_tag_urn("primary-key")]),
        ),
        SchemaFieldClass(
            fieldPath="customer_email",
            type={"type": {"com.linkedin.schema.StringType": {}}},
            description="Customer email address",
            globalTags=TagAssociationClass(tags=[make_tag_urn("pii")]),
            glossaryTerms=GlossaryTermAssociationClass(
                terms=[make_glossary_term_urn("PersonalData")]
            ),
        ),
    ],
)

emitter.emit_mce(dataset_urn, properties)
emitter.emit_mce(dataset_urn, schema)
```

---

## 3. Data Classification & PII

```python
import re
from enum import Enum
from typing import Optional

class DataClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"  # PII, financial, health

class PIIDetector:
    """Detect PII columns by name patterns and content sampling."""
    
    PII_PATTERNS = {
        "email": r"(email|e_mail|email_address)",
        "phone": r"(phone|mobile|tel|telephone)",
        "ssn": r"(ssn|social_security|sin)",
        "name": r"(first_name|last_name|full_name|customer_name)",
        "address": r"(address|street|city|zip|postal)",
        "ip": r"(ip_address|ip_addr|client_ip)",
        "credit_card": r"(card_number|cc_number|credit_card)",
        "dob": r"(date_of_birth|dob|birth_date)",
    }
    
    def classify_column(self, column_name: str, sample_values: list) -> Optional[str]:
        """Classify a column as PII or not."""
        col_lower = column_name.lower()
        
        # Check column name patterns
        for pii_type, pattern in self.PII_PATTERNS.items():
            if re.search(pattern, col_lower):
                return pii_type
        
        # Check content patterns
        if sample_values:
            email_pattern = r'^[\w.-]+@[\w.-]+\.\w+$'
            if sum(1 for v in sample_values if re.match(email_pattern, str(v))) > len(sample_values) * 0.5:
                return "email"
        
        return None
    
    def scan_table(self, df, table_name: str) -> dict:
        """Scan all columns in a table for PII."""
        findings = {}
        for col in df.columns:
            sample = df[col].dropna().head(100).tolist()
            pii_type = self.classify_column(col, sample)
            if pii_type:
                findings[col] = {
                    "pii_type": pii_type,
                    "classification": DataClassification.RESTRICTED.value,
                    "action": "mask_or_encrypt",
                }
        return findings
```

---

## 4. Access Control

```python
# Row-Level Security (RLS) example in PostgreSQL
"""
-- Create policy: US team only sees US data
CREATE POLICY us_data_only ON orders
    FOR SELECT
    TO us_analysts
    USING (region = 'US');

-- Column-Level Security via Views
CREATE VIEW orders_masked AS
SELECT
    order_id,
    CASE WHEN current_user IN ('admin', 'data_engineer')
         THEN customer_email
         ELSE '***@' || split_part(customer_email, '@', 2)
    END AS customer_email,
    amount,
    order_date
FROM orders;

-- Dynamic data masking
CREATE MASKING POLICY mask_email AS (val STRING)
RETURNS STRING ->
    CASE
        WHEN CURRENT_ROLE() IN ('ADMIN', 'DATA_ENGINEER') THEN val
        ELSE REGEXP_REPLACE(val, '.+@', '***@')
    END;
"""

# RBAC Implementation
from dataclasses import dataclass

@dataclass
class AccessPolicy:
    role: str
    tables: list[str]
    columns: list[str]  # Empty = all columns
    row_filter: str     # SQL WHERE clause
    operations: list[str]  # SELECT, INSERT, UPDATE, DELETE

POLICIES = [
    AccessPolicy(
        role="analyst",
        tables=["gold.*"],
        columns=[],  # All columns in gold
        row_filter="",  # No row filter
        operations=["SELECT"],
    ),
    AccessPolicy(
        role="regional_analyst_us",
        tables=["silver.orders", "gold.daily_revenue"],
        columns=["order_id", "amount", "status", "region"],  # No PII columns
        row_filter="region = 'US'",
        operations=["SELECT"],
    ),
    AccessPolicy(
        role="data_engineer",
        tables=["*"],
        columns=[],
        row_filter="",
        operations=["SELECT", "INSERT", "UPDATE", "DELETE"],
    ),
]
```

---

## 5. Compliance (GDPR/CCPA)

```python
class ComplianceManager:
    """Handle data subject rights (GDPR Article 15-22)."""
    
    def right_to_access(self, user_id: str) -> dict:
        """Article 15: Provide all data held about a user."""
        data = {}
        for table in self._get_tables_with_user_data():
            records = self._query(f"SELECT * FROM {table} WHERE user_id = %s", user_id)
            if records:
                data[table] = records
        return data
    
    def right_to_erasure(self, user_id: str) -> dict:
        """Article 17: Delete all user data (right to be forgotten)."""
        deleted = {}
        for table in self._get_tables_with_user_data():
            count = self._execute(f"DELETE FROM {table} WHERE user_id = %s", user_id)
            deleted[table] = count
        
        # Also remove from backups/archives (harder - schedule for next backup cycle)
        self._schedule_backup_purge(user_id)
        
        # Log the erasure for audit
        self._audit_log("erasure", user_id, deleted)
        return deleted
    
    def right_to_portability(self, user_id: str) -> bytes:
        """Article 20: Export data in machine-readable format."""
        data = self.right_to_access(user_id)
        return json.dumps(data, default=str).encode('utf-8')
    
    def data_retention_sweep(self):
        """Enforce retention policies - delete expired data."""
        retention_policies = {
            "raw_events": 90,       # 90 days
            "user_sessions": 365,   # 1 year
            "transaction_logs": 730, # 2 years (legal requirement)
        }
        for table, days in retention_policies.items():
            self._execute(
                f"DELETE FROM {table} WHERE created_at < NOW() - INTERVAL '{days} days'"
            )
```

---

## 6. Data Mesh & Data Contracts

```yaml
# data_contract.yml - Agreement between producer and consumer
apiVersion: v1
kind: DataContract
metadata:
  name: orders-contract
  version: 2.1.0
  owner: commerce-team@company.com
  domain: commerce

schema:
  type: object
  properties:
    order_id:
      type: string
      format: uuid
      description: "Unique order identifier"
      pii: false
    customer_id:
      type: string
      description: "Customer reference"
      pii: true
    amount:
      type: number
      minimum: 0
      maximum: 1000000
    status:
      type: string
      enum: [PENDING, COMPLETED, CANCELLED]
    order_date:
      type: string
      format: date

quality:
  freshness:
    max_age_hours: 2
  completeness:
    order_id: 100%
    amount: 99.9%
  volume:
    min_daily_records: 1000
    max_daily_records: 100000

sla:
  availability: 99.9%
  latency_p99_ms: 500

consumers:
  - team: analytics
    purpose: "Daily revenue reporting"
  - team: ml-platform
    purpose: "Recommendation model training"
```

```python
# Validate data against contract
import yaml
from jsonschema import validate

def validate_against_contract(df, contract_path: str) -> dict:
    with open(contract_path) as f:
        contract = yaml.safe_load(f)
    
    violations = []
    
    # Schema validation
    for col, spec in contract['schema']['properties'].items():
        if col not in df.columns:
            violations.append(f"Missing column: {col}")
            continue
        if spec.get('type') == 'number' and 'minimum' in spec:
            bad = df[df[col] < spec['minimum']]
            if len(bad) > 0:
                violations.append(f"{col}: {len(bad)} below minimum {spec['minimum']}")
    
    # Quality validation
    quality = contract.get('quality', {})
    if 'freshness' in quality:
        # Check max age
        pass
    
    return {"valid": len(violations) == 0, "violations": violations}
```

---

## Interview Questions

### Beginner
1. **What is data governance?** Framework of policies, processes, and standards for managing data assets. Covers quality, security, compliance, cataloging, and lineage. Enables trust in data.
2. **What is data lineage?** Visual/metadata tracking of how data flows from source to destination. Shows transformations at table and column level. Critical for debugging, compliance, impact analysis.
3. **What is PII?** Personally Identifiable Information — data that can identify an individual (name, email, SSN, phone). Must be protected, masked, or encrypted per regulations.

### Intermediate
4. **How do you implement GDPR right to erasure in a data lake?** Track user_id across all tables (lineage/catalog), delete from operational tables, mark in immutable stores (tombstones), schedule backup purges, audit log all actions, verify completeness.
5. **Explain the difference between RBAC and ABAC.** RBAC: permissions based on role (analyst, engineer). ABAC: permissions based on attributes (department=finance AND location=US AND classification=internal). ABAC is more flexible but complex.
6. **What is a data contract?** Formal agreement between data producer and consumer on schema, quality SLAs, freshness, and semantics. Enforced via CI/CD. Prevents breaking downstream systems.

### Advanced
7. **Design a data mesh architecture.** Domain-oriented ownership (each team owns their data products), self-serve platform (standardized tools, catalog, quality), federated governance (global policies, local implementation), data as product (SLAs, docs, discoverability).
8. **How do you implement column-level lineage at scale?** Parse SQL with sqlglue/sqllineage for automated extraction, integrate with dbt (ref-based lineage), emit OpenLineage events from pipelines, store in graph database (Neo4j) or catalog (DataHub), visualize with lineage explorer.
9. **Design a compliance automation system for multi-regulation.** Unified PII detection (automated scanning), tag-based policies (PII→mask, HIPAA→encrypt), consent management integration, automated DSR (Data Subject Request) fulfillment, retention policies per regulation, audit trail, regular compliance reports.

---

## Hands-On Exercise
1. Set up DataHub or OpenMetadata locally (Docker)
2. Register datasets with schema and ownership
3. Implement PII detection scanning
4. Create RBAC policies with row/column-level security
5. Write a data contract YAML and validation script
6. Implement right-to-erasure across multiple tables
