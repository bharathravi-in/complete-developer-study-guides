# Day 29: Interview Preparation

## Learning Objectives
- Practice SQL interview challenges (beginner to advanced)
- Walk through system design interviews with data engineering focus
- Prepare behavioral answers using STAR framework
- Understand take-home assignment patterns

---

## 1. SQL Interview Challenges

### Level 1: Fundamentals

```sql
-- Q1: Find top 3 departments by average salary
SELECT department, AVG(salary) as avg_salary
FROM employees
GROUP BY department
ORDER BY avg_salary DESC
LIMIT 3;

-- Q2: Find employees earning more than their manager
SELECT e.name as employee, e.salary, m.name as manager, m.salary as manager_salary
FROM employees e
JOIN employees m ON e.manager_id = m.id
WHERE e.salary > m.salary;

-- Q3: Find duplicate emails
SELECT email, COUNT(*) as cnt
FROM users
GROUP BY email
HAVING COUNT(*) > 1;

-- Q4: Second highest salary (handle ties)
SELECT DISTINCT salary
FROM employees
ORDER BY salary DESC
LIMIT 1 OFFSET 1;

-- Better: using DENSE_RANK
SELECT salary FROM (
    SELECT salary, DENSE_RANK() OVER (ORDER BY salary DESC) as rnk
    FROM employees
) ranked
WHERE rnk = 2;
```

### Level 2: Intermediate

```sql
-- Q5: Running total of orders per customer
SELECT 
    customer_id,
    order_date,
    amount,
    SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date) as running_total
FROM orders;

-- Q6: Find gaps in consecutive dates (missing days)
WITH date_series AS (
    SELECT 
        log_date,
        LAG(log_date) OVER (ORDER BY log_date) as prev_date
    FROM daily_logs
)
SELECT 
    prev_date as gap_start,
    log_date as gap_end,
    log_date - prev_date - 1 as days_missing
FROM date_series
WHERE log_date - prev_date > 1;

-- Q7: Pivot: Monthly revenue by product category
SELECT
    product_category,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 1 THEN revenue END) as jan,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 2 THEN revenue END) as feb,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 3 THEN revenue END) as mar
FROM orders
WHERE EXTRACT(YEAR FROM order_date) = 2024
GROUP BY product_category;

-- Q8: Retention: Users active in month 1 and month 2
WITH month1_users AS (
    SELECT DISTINCT user_id
    FROM events
    WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31'
),
month2_users AS (
    SELECT DISTINCT user_id
    FROM events
    WHERE event_date BETWEEN '2024-02-01' AND '2024-02-29'
)
SELECT 
    COUNT(m2.user_id)::FLOAT / COUNT(m1.user_id) as retention_rate
FROM month1_users m1
LEFT JOIN month2_users m2 ON m1.user_id = m2.user_id;
```

### Level 3: Advanced

```sql
-- Q9: Sessionize events (30-min inactivity gap = new session)
WITH lagged AS (
    SELECT 
        user_id,
        event_time,
        LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time) as prev_time
    FROM events
),
flagged AS (
    SELECT *,
        CASE WHEN EXTRACT(EPOCH FROM event_time - prev_time) > 1800 
             OR prev_time IS NULL 
             THEN 1 ELSE 0 END as new_session
    FROM lagged
)
SELECT 
    user_id,
    event_time,
    SUM(new_session) OVER (PARTITION BY user_id ORDER BY event_time) as session_id
FROM flagged;

-- Q10: Funnel analysis (conversion through steps)
WITH step1 AS (
    SELECT DISTINCT user_id FROM events WHERE event = 'page_view'
),
step2 AS (
    SELECT DISTINCT user_id FROM events WHERE event = 'add_to_cart'
),
step3 AS (
    SELECT DISTINCT user_id FROM events WHERE event = 'checkout'
),
step4 AS (
    SELECT DISTINCT user_id FROM events WHERE event = 'purchase'
)
SELECT
    (SELECT COUNT(*) FROM step1) as page_views,
    (SELECT COUNT(*) FROM step1 s1 JOIN step2 s2 ON s1.user_id = s2.user_id) as add_to_cart,
    (SELECT COUNT(*) FROM step1 s1 JOIN step2 s2 ON s1.user_id = s2.user_id 
     JOIN step3 s3 ON s2.user_id = s3.user_id) as checkout,
    (SELECT COUNT(*) FROM step1 s1 JOIN step2 s2 ON s1.user_id = s2.user_id 
     JOIN step3 s3 ON s2.user_id = s3.user_id 
     JOIN step4 s4 ON s3.user_id = s4.user_id) as purchase;

-- Q11: Median calculation without PERCENTILE function
SELECT AVG(salary) as median_salary
FROM (
    SELECT salary, 
           ROW_NUMBER() OVER (ORDER BY salary) as rn,
           COUNT(*) OVER () as total
    FROM employees
) t
WHERE rn IN (FLOOR((total + 1) / 2.0), CEIL((total + 1) / 2.0));

-- Q12: Recursive CTE: Organization hierarchy
WITH RECURSIVE org_tree AS (
    -- Base: CEO (no manager)
    SELECT id, name, manager_id, 1 as level, name::text as path
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive: all reports
    SELECT e.id, e.name, e.manager_id, t.level + 1, t.path || ' > ' || e.name
    FROM employees e
    JOIN org_tree t ON e.manager_id = t.id
)
SELECT * FROM org_tree ORDER BY path;
```

---

## 2. System Design Practice

### Framework Responses

```
Interviewer: "Design a data pipeline for a ride-sharing company."

STEP 1 - REQUIREMENTS (ask clarifying questions):
"Before I design, let me understand:
- What data? GPS pings, ride events, payments?
- Scale: How many rides/day? Drivers sending location how often?
- Latency: Real-time pricing? Or batch analytics only?
- What downstream consumers? ML models, dashboards, APIs?"

STEP 2 - HIGH LEVEL:
"Here's my approach:
- Ingestion: Kafka (high throughput, ordered per partition)
- Processing: Flink for real-time (pricing, ETA), Spark for batch (analytics)
- Storage: S3 + Delta Lake (time travel, ACID)
- Serving: Redis (real-time), Presto/Trino (interactive analytics)

Let me draw the data flow..."

STEP 3 - DEEP DIVE:
"The hardest part is real-time pricing with 5M drivers.
Here's how I'd handle it:
- Partition Kafka by geohash (locality)
- Flink windowed aggregation (30s tumbling windows)
- Supply/demand ratio per zone → surge multiplier
- Store in Redis → pricing service queries

For the batch side:
- Kafka → S3 (raw) → Spark → Silver/Gold layers
- dbt for business transformations
- Airflow orchestration"

STEP 4 - TRADEOFFS:
"Key tradeoffs:
- Kafka retention: 7d vs longer (cost vs replayability)  
- Exactly-once: needed for payments, not for GPS analytics
- Consistency: eventual OK for analytics, strong for payments
- Scaling: Flink scales with Kafka partitions"
```

### Common System Design Topics

| Topic | Key Components | Main Challenge |
|-------|---------------|----------------|
| Real-time analytics dashboard | Kafka → Flink → Druid/Redis | Low-latency aggregation at scale |
| Data lake architecture | S3 + Delta + Spark + Airflow | Governance, data quality, performance |
| Event-driven pipeline | Kafka → processors → stores | Exactly-once, ordering, schema evolution |
| ML feature store | Batch features + streaming features | Consistency between training and serving |
| Log analytics platform | Fluentd → Kafka → Elasticsearch | Volume (TB/day), retention vs cost |
| CDC pipeline | Debezium → Kafka → target | Schema changes, ordering, consistency |

---

## 3. Behavioral Questions (STAR Framework)

```
S - Situation: Context
T - Task: What you needed to do
A - Action: What you did (focus here)
R - Result: Measurable outcome
```

### Common Questions & Answer Patterns

**"Tell me about a time you dealt with data quality issues."**
```
S: Production dashboard showing wrong revenue numbers. Off by 15%.
T: Find root cause, fix, and prevent recurrence.
A: 1) Added data quality checks (Great Expectations) at each layer
   2) Traced issue to timezone conversion bug in ETL
   3) Backfilled corrected data using Delta Lake time travel
   4) Implemented automated alerts for anomalies (>5% deviation)
R: Zero data quality incidents in 6 months. Trust in data restored.
   Team adopted quality-first approach.
```

**"Describe a pipeline that failed in production."**
```
S: Nightly batch job started failing. SLA breach at 6 AM.
T: Restore pipeline within SLA, prevent recurrence.
A: 1) Immediate: checked Airflow logs, found OOM error
   2) Root cause: upstream sent 10x normal data volume (marketing campaign)
   3) Fix: increased executor memory, added dynamic allocation
   4) Prevention: added data volume monitoring, auto-scaling, alerting
   5) Wrote runbook for on-call team
R: Pipeline recovered in 45 minutes. Auto-scaling prevented 
   3 similar incidents in following month.
```

**"How do you handle disagreements with stakeholders?"**
```
S: Product team wanted real-time dashboard. Eng team said batch was sufficient.
T: Find right solution balancing needs and effort.
A: 1) Gathered requirements: what decisions need real-time? (only 2 of 10 metrics)
   2) Proposed hybrid: batch for 8 metrics, streaming for 2 critical ones
   3) Built POC showing streaming was 5x more complex and expensive
   4) Got alignment: streaming only for alerting, batch for exploration
R: Delivered 4 weeks faster. Product team happy with tiered approach.
   Established decision framework for future batch-vs-stream choices.
```

---

## 4. Take-Home Assignment Patterns

### Common Format
```
You receive: Dataset (CSV/JSON) + requirements document
Deliverable: Code + documentation + (optional) presentation

Time: 4-8 hours (respect this!)
```

### Example: Data Pipeline Take-Home

```python
"""
Assignment: Build a data pipeline for e-commerce order data.
Requirements:
1. Ingest CSV files (orders, products, customers)
2. Clean and validate data
3. Build dimensional model (star schema)
4. Create aggregated metrics
5. Document assumptions and decisions
"""

# Winning approach structure:
# /
# ├── README.md          (Setup, architecture, decisions, tradeoffs)
# ├── src/
# │   ├── ingest.py      (Load raw data)
# │   ├── validate.py    (Data quality checks)
# │   ├── transform.py   (Business logic, dimensional model)
# │   └── metrics.py     (Final aggregates)
# ├── tests/             (Unit + integration tests)
# ├── data/              (Sample data or instructions)
# ├── docs/              (Architecture diagram, data model)
# └── Makefile/docker-compose.yml (Easy to run)

# Key differentiators:
# 1. Clean code (PEP 8, type hints, docstrings)
# 2. Tests (at least 5-10 meaningful tests)
# 3. Error handling (what if data is missing/malformed?)
# 4. Documentation (explain WHY, not just HOW)
# 5. Easy to run (docker-compose up or make run)

# Example validation:
from dataclasses import dataclass

@dataclass 
class ValidationResult:
    passed: bool
    checks_run: int
    failures: list[str]

def validate_orders(df) -> ValidationResult:
    failures = []
    
    # Not null checks
    for col in ['order_id', 'customer_id', 'order_date', 'amount']:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            failures.append(f"{col}: {null_count} null values")
    
    # Range checks
    negative_amounts = (df['amount'] < 0).sum()
    if negative_amounts > 0:
        failures.append(f"amount: {negative_amounts} negative values")
    
    # Uniqueness
    dup_orders = df['order_id'].duplicated().sum()
    if dup_orders > 0:
        failures.append(f"order_id: {dup_orders} duplicates")
    
    return ValidationResult(
        passed=len(failures) == 0,
        checks_run=6,
        failures=failures,
    )
```

---

## 5. Technical Deep-Dive Questions

### Kafka
- How do you guarantee ordering? (Partition key)
- Consumer lag growing — how do you fix? (Add consumers, increase partitions, optimize processing)
- How does exactly-once work? (Idempotent producer + transactional consumer)

### Spark
- Explain narrow vs wide transformations. (Narrow: map, filter — no shuffle. Wide: groupBy, join — shuffle)
- How do you handle data skew? (Salting, broadcast join, adaptive query execution)
- What's the difference between cache and persist? (cache = persist(MEMORY_AND_DISK))

### Airflow
- DAG stuck — how do you debug? (Check scheduler logs, task instance state, clear and retry, check resources)
- How do you handle backfills? (airflow backfill with date range, idempotent tasks)
- Dynamic DAGs: pros and cons? (Pro: flexible. Con: hard to debug, parse time issues)

### Data Modeling
- Star vs snowflake schema? (Star: denormalized dims, faster queries. Snowflake: normalized dims, less storage)
- SCD Type 2 implementation? (Add effective_date, end_date, is_current columns)
- When to denormalize? (Query performance critical, write frequency low, storage cheap)

---

## 6. Mock Interview Scorecard

```
SCORING (1-5 per area):

Communication:
□ Clarifies requirements before jumping in
□ Explains reasoning, not just answers
□ Handles follow-ups gracefully
□ Acknowledges unknowns honestly

Technical Depth:
□ Correct fundamentals
□ Understands tradeoffs
□ Aware of edge cases
□ Production-aware (monitoring, failure modes)

System Design:
□ Structured approach
□ Appropriate scale estimation
□ Sound component choices
□ Identifies bottlenecks

Coding:
□ Clean, readable code
□ Handles edge cases
□ Good time complexity
□ Tests / validation

Cultural Fit:
□ Collaborative approach
□ Ownership mentality
□ Learns from mistakes
□ Data-driven decisions
```

---

## Interview Questions

### Beginner
1. **What's the difference between INNER JOIN and LEFT JOIN?** INNER: only matching rows. LEFT: all rows from left table + matching rows from right (NULL if no match). Use LEFT for "all users, even those without orders."
2. **Explain ETL vs ELT.** ETL: Extract, Transform, Load (transform before loading, traditional). ELT: Extract, Load, Transform (load raw, transform in warehouse — modern approach with cheap compute). ELT preferred when warehouse is powerful.
3. **What is data normalization?** Reduce redundancy by splitting into related tables (1NF, 2NF, 3NF). Pros: less storage, no update anomalies. Cons: more joins. Denormalize for read-heavy analytics.

### Intermediate
4. **How would you debug a slow query?** EXPLAIN ANALYZE (see execution plan), check: sequential scans (add index?), large sorts (add ORDER BY index?), nested loops on large tables (use hash join?), missing partition pruning.
5. **Design a data quality framework.** Layers: schema validation (input) → null/range checks (bronze→silver) → business rules (silver→gold) → cross-table consistency. Tools: Great Expectations, dbt tests, custom monitors. Alert on degradation.
6. **Explain exactly-once semantics.** At-most-once: may lose messages. At-least-once: may duplicate. Exactly-once: each message processed exactly once. Implementation: idempotent writes (dedup by ID) + transactional processing + checkpointing.

### Advanced
7. **You inherit a legacy pipeline. How do you modernize it?** Assess: document current state, identify pain points, measure (cost, latency, failures). Plan: prioritize by impact. Execute incrementally: add tests first, then migrate component by component, dual-run old+new, validate outputs match, cut over.
8. **How do you handle a pipeline that must process data from 50 different sources?** Standardize ingestion framework (configuration-driven, not code-per-source). Schema registry for contracts. Common landing zone pattern. Monitoring per source. Isolate failures (one source failing shouldn't block others).
9. **Design on-call for a data platform team.** Runbooks for common issues, tiered alerting (P1: SLA breach, P2: degradation, P3: warning), rotation with escalation. Post-mortems for P1s. Reduce toil: automate common fixes, self-healing pipelines, noise reduction in alerts.

---

## Hands-On Exercise
1. Solve 5 SQL problems from LeetCode (Easy → Medium → Hard)
2. Practice system design: set 35-min timer, design "real-time fraud detection"
3. Write STAR responses for 3 behavioral questions
4. Build a take-home assignment in 4 hours (find a practice dataset)
5. Do a mock interview with a peer (or record yourself)
