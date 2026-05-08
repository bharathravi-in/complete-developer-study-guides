# Day 4: Data Modeling — Data Vault & 3NF

## Overview
Data Vault 2.0 is the modern approach for enterprise data warehouses needing auditability, flexibility, and historization. Understanding when to use 3NF vs Star vs Data Vault is key.

---

## 1. Third Normal Form (3NF) in Data Warehousing

### When 3NF Makes Sense
- **Inmon approach**: Build a normalized Enterprise Data Warehouse (EDW), then create star schema data marts
- Reduces redundancy, ensures consistency
- Better for complex, evolving schemas

### 3NF Rules Refresher
1. **1NF**: No repeating groups, atomic values
2. **2NF**: No partial dependencies (every non-key depends on the whole key)
3. **3NF**: No transitive dependencies (non-key → non-key)

```sql
-- 3NF Example: Orders broken into proper tables
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
);

CREATE TABLE addresses (
    address_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers,
    street TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    address_type TEXT  -- 'billing', 'shipping'
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers,
    shipping_address_id INT REFERENCES addresses,
    order_date TIMESTAMPTZ,
    status TEXT
);

CREATE TABLE order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders,
    product_id INT REFERENCES products,
    quantity INT,
    unit_price DECIMAL(10,2)
);
```

---

## 2. Data Vault 2.0

### Core Philosophy
- **Business keys are eternal** — they don't change
- **Separate structure from context** — relationships vs attributes
- **Everything is historized** — full audit trail
- **Load everything, sort out later** — no filtering during load

### Components

```
┌──────────┐     ┌──────────────┐     ┌──────────┐
│   HUB    │────▶│    LINK      │◀────│   HUB    │
│(Business │     │(Relationship)│     │(Business │
│  Entity) │     └──────┬───────┘     │  Entity) │
└────┬─────┘            │             └────┬─────┘
     │                  │                  │
┌────▼─────┐     ┌──────▼───────┐   ┌────▼─────┐
│ SATELLITE│     │  SATELLITE   │   │ SATELLITE│
│(Attributes│    │(Link context)│   │(Attributes│
│ over time)│    └──────────────┘   │ over time)│
└──────────┘                        └──────────┘
```

### Hubs — Business Keys
```sql
-- Hubs store unique business identifiers
CREATE TABLE hub_customer (
    hub_customer_hk BYTEA PRIMARY KEY,     -- Hash key (MD5/SHA of BK)
    customer_bk TEXT NOT NULL,              -- Business key
    load_date TIMESTAMPTZ NOT NULL,
    record_source TEXT NOT NULL             -- Where it came from
);

CREATE TABLE hub_product (
    hub_product_hk BYTEA PRIMARY KEY,
    product_bk TEXT NOT NULL,
    load_date TIMESTAMPTZ NOT NULL,
    record_source TEXT NOT NULL
);
```

### Links — Relationships
```sql
-- Links store relationships between hubs
CREATE TABLE link_order (
    link_order_hk BYTEA PRIMARY KEY,       -- Hash of all parent HKs
    hub_customer_hk BYTEA NOT NULL REFERENCES hub_customer,
    hub_product_hk BYTEA NOT NULL REFERENCES hub_product,
    order_bk TEXT,                          -- Degenerate business key
    load_date TIMESTAMPTZ NOT NULL,
    record_source TEXT NOT NULL
);
```

### Satellites — Attributes (with History)
```sql
-- Satellites store descriptive attributes with full history
CREATE TABLE sat_customer_details (
    hub_customer_hk BYTEA NOT NULL REFERENCES hub_customer,
    load_date TIMESTAMPTZ NOT NULL,
    load_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    record_source TEXT NOT NULL,
    hash_diff BYTEA NOT NULL,              -- Hash of all attributes (change detection)
    -- Actual attributes
    customer_name TEXT,
    email TEXT,
    phone TEXT,
    tier TEXT,
    PRIMARY KEY (hub_customer_hk, load_date)
);

CREATE TABLE sat_order_details (
    link_order_hk BYTEA NOT NULL REFERENCES link_order,
    load_date TIMESTAMPTZ NOT NULL,
    load_end_date TIMESTAMPTZ DEFAULT '9999-12-31',
    record_source TEXT NOT NULL,
    hash_diff BYTEA NOT NULL,
    quantity INT,
    unit_price DECIMAL(10,2),
    discount DECIMAL(10,2),
    status TEXT,
    PRIMARY KEY (link_order_hk, load_date)
);
```

---

## 3. Data Vault Loading Patterns

### Hash Key Generation
```python
import hashlib

def generate_hash_key(*business_keys):
    """Generate consistent hash key from business keys"""
    concat = '||'.join(str(bk).strip().upper() for bk in business_keys)
    return hashlib.md5(concat.encode()).hexdigest()

# Hub hash = hash of single business key
customer_hk = generate_hash_key('CUST-001')

# Link hash = hash of ALL parent hub keys combined
order_hk = generate_hash_key('CUST-001', 'PROD-ABC', 'ORD-12345')

# Satellite hash_diff = hash of all attributes (change detection)
hash_diff = generate_hash_key('John Doe', 'john@email.com', 'gold')
```

### Loading Rules
```sql
-- Hub: INSERT only if business key doesn't exist
INSERT INTO hub_customer (hub_customer_hk, customer_bk, load_date, record_source)
SELECT hash_key, business_key, NOW(), 'crm_system'
FROM staging_customers
WHERE hash_key NOT IN (SELECT hub_customer_hk FROM hub_customer);

-- Satellite: INSERT only if attributes changed (hash_diff differs)
INSERT INTO sat_customer_details 
SELECT s.hub_customer_hk, NOW(), '9999-12-31', 'crm_system', s.hash_diff,
       s.name, s.email, s.phone, s.tier
FROM staging_customers s
LEFT JOIN (
    SELECT * FROM sat_customer_details WHERE load_end_date = '9999-12-31'
) current_sat ON s.hub_customer_hk = current_sat.hub_customer_hk
WHERE current_sat.hash_diff IS NULL           -- New record
   OR current_sat.hash_diff != s.hash_diff;   -- Changed record
```

---

## 4. Business Vault & Information Mart

### Business Vault (Derived)
```sql
-- Point-in-Time (PIT) table: simplify satellite joins
CREATE TABLE pit_customer AS
SELECT 
    h.hub_customer_hk,
    snap_date,
    -- Find the satellite record valid at snap_date
    (SELECT MAX(load_date) FROM sat_customer_details s 
     WHERE s.hub_customer_hk = h.hub_customer_hk 
     AND s.load_date <= snap_date) AS sat_details_load_date,
    (SELECT MAX(load_date) FROM sat_customer_metrics s 
     WHERE s.hub_customer_hk = h.hub_customer_hk 
     AND s.load_date <= snap_date) AS sat_metrics_load_date
FROM hub_customer h
CROSS JOIN generate_series('2024-01-01'::date, CURRENT_DATE, '1 day') AS snap_date;
```

### Information Mart (Star Schema from Vault)
```sql
-- Build dimensional model FROM Data Vault for reporting
CREATE VIEW dim_customer_current AS
SELECT 
    h.hub_customer_hk,
    h.customer_bk AS customer_id,
    s.customer_name,
    s.email,
    s.tier
FROM hub_customer h
JOIN sat_customer_details s 
    ON h.hub_customer_hk = s.hub_customer_hk
    AND s.load_end_date = '9999-12-31';  -- Current only
```

---

## 5. Comparison: When to Use What

| Criteria | Star Schema | 3NF (Inmon) | Data Vault |
|----------|-------------|-------------|------------|
| **Best for** | Reporting/BI | Enterprise consistency | Agile, auditable DWH |
| **Flexibility** | Low (redesign to add) | Medium | High (additive) |
| **History** | SCD in dimensions | SCD in dimensions | Built-in everywhere |
| **Load complexity** | Medium | High | Rules-based (automatable) |
| **Query performance** | Excellent | Needs marts | Needs marts |
| **Auditability** | Low | Medium | Full lineage |
| **Schema changes** | Painful | Painful | Easy (add satellite) |
| **Team size** | Small | Large | Medium-Large |
| **Tool support** | Excellent | Good | Growing (dbt-vault) |

### Decision Framework
```
Need fast reporting with simple queries?        → Star Schema
Need full audit trail + multiple sources?       → Data Vault → Star Marts
Need enterprise-wide consistency (Inmon)?       → 3NF EDW → Star Marts
Agile team, frequent schema changes?            → Data Vault
Regulatory compliance (finance, healthcare)?    → Data Vault
Small team, single data source?                 → Star Schema directly
```

---

## 6. Data Vault with dbt

```sql
-- dbt model: hub_customer.sql (using dbt-vault package)
{{ config(materialized='incremental') }}

{%- set source_model = 'stg_crm_customers' -%}
{%- set src_pk = 'customer_hk' -%}
{%- set src_nk = 'customer_id' -%}
{%- set src_ldts = 'load_date' -%}
{%- set src_source = 'record_source' -%}

{{ dbtvault.hub(
    src_pk=src_pk,
    src_nk=src_nk,
    src_ldts=src_ldts,
    src_source=src_source,
    source_model=source_model
) }}
```

---

## 7. Practice Exercise

Design a Data Vault model for an **online marketplace** with:
- Customers who buy products
- Sellers who list products  
- Orders connecting buyers, sellers, and products
- Reviews (customer reviews a product)

Identify:
1. All Hubs (business entities)
2. All Links (relationships)
3. Key Satellites (what attributes change over time?)

---

## Key Takeaways
- Data Vault separates business keys (Hubs), relationships (Links), and context (Satellites)
- Everything is historized automatically — full audit trail
- Hash keys enable parallel, independent loading
- Data Vault is the staging/raw vault; Star Schema serves reporting
- Use dbt-vault to automate Data Vault pattern generation
- Choose your modeling approach based on team size, compliance needs, and query patterns

## Tomorrow
**Day 5**: ETL vs ELT Patterns — Change Data Capture, idempotency, and building reliable data pipelines.
