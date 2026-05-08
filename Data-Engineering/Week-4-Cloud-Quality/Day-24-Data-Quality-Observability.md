# Day 24: Data Quality & Observability

## Learning Objectives
- Define and measure data quality dimensions
- Implement automated quality checks with Great Expectations
- Build data observability with alerting and SLAs
- Design quality-first data pipelines

---

## 1. Data Quality Dimensions

| Dimension | Definition | Example Check |
|-----------|-----------|---------------|
| **Completeness** | No missing values | NULL rate < 1% |
| **Accuracy** | Values are correct | Amounts match source |
| **Freshness** | Data is up-to-date | Max timestamp within 1 hour |
| **Consistency** | No contradictions | Status + date agree |
| **Uniqueness** | No duplicates | Primary keys are unique |
| **Validity** | Values in expected range | Age between 0-150 |

---

## 2. Great Expectations

```python
import great_expectations as gx

# Initialize context
context = gx.get_context()

# Connect to data source
datasource = context.sources.add_pandas("my_datasource")
data_asset = datasource.add_dataframe_asset("orders")

# Build expectations
batch = data_asset.build_batch_request(dataframe=df)
validator = context.get_validator(batch_request=batch)

# Completeness
validator.expect_column_values_to_not_be_null("order_id")
validator.expect_column_values_to_not_be_null("amount", mostly=0.99)

# Validity
validator.expect_column_values_to_be_between("amount", min_value=0, max_value=1000000)
validator.expect_column_values_to_be_in_set("status", ["PENDING", "COMPLETED", "CANCELLED"])
validator.expect_column_values_to_match_regex("email", r"^[\w.-]+@[\w.-]+\.\w+$")

# Uniqueness
validator.expect_column_values_to_be_unique("order_id")
validator.expect_compound_columns_to_be_unique(["customer_id", "order_date", "product_id"])

# Freshness
validator.expect_column_max_to_be_between(
    "created_at",
    min_value=(datetime.now() - timedelta(hours=2)).isoformat(),
    max_value=datetime.now().isoformat(),
)

# Distribution
validator.expect_column_mean_to_be_between("amount", min_value=50, max_value=500)
validator.expect_column_stdev_to_be_between("amount", min_value=10, max_value=200)

# Volume
validator.expect_table_row_count_to_be_between(min_value=1000, max_value=100000)

# Save expectation suite
validator.save_expectation_suite()
```

### Checkpoints (Automated Validation)

```python
# Create checkpoint for pipeline integration
checkpoint = context.add_or_update_checkpoint(
    name="orders_quality_checkpoint",
    validations=[
        {
            "batch_request": batch_request,
            "expectation_suite_name": "orders_suite",
        }
    ],
    action_list=[
        {"name": "store_validation_result", "action": {"class_name": "StoreValidationResultAction"}},
        {"name": "update_data_docs", "action": {"class_name": "UpdateDataDocsAction"}},
        {
            "name": "send_slack_notification",
            "action": {
                "class_name": "SlackNotificationAction",
                "slack_webhook": "${SLACK_WEBHOOK}",
                "notify_on": "failure",
            },
        },
    ],
)

# Run checkpoint (in pipeline)
result = checkpoint.run()
if not result.success:
    raise DataQualityError(f"Quality checks failed: {result.statistics}")
```

---

## 3. Data Quality Framework (Custom)

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Any
from datetime import datetime, timedelta
import pandas as pd

class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class QualityRule:
    name: str
    description: str
    check_fn: Callable[[pd.DataFrame], tuple[bool, dict]]
    severity: Severity
    tags: list[str] = field(default_factory=list)

@dataclass
class QualityResult:
    rule_name: str
    passed: bool
    severity: Severity
    details: dict
    timestamp: datetime = field(default_factory=datetime.utcnow)

class DataQualityEngine:
    def __init__(self):
        self.rules: list[QualityRule] = []
        self.results: list[QualityResult] = []
    
    def add_rule(self, rule: QualityRule):
        self.rules.append(rule)
    
    def run(self, df: pd.DataFrame) -> list[QualityResult]:
        self.results = []
        for rule in self.rules:
            try:
                passed, details = rule.check_fn(df)
                result = QualityResult(
                    rule_name=rule.name,
                    passed=passed,
                    severity=rule.severity,
                    details=details,
                )
            except Exception as e:
                result = QualityResult(
                    rule_name=rule.name,
                    passed=False,
                    severity=Severity.CRITICAL,
                    details={"error": str(e)},
                )
            self.results.append(result)
        return self.results
    
    def has_failures(self, min_severity: Severity = Severity.ERROR) -> bool:
        severity_order = {Severity.INFO: 0, Severity.WARNING: 1, Severity.ERROR: 2, Severity.CRITICAL: 3}
        return any(
            not r.passed and severity_order[r.severity] >= severity_order[min_severity]
            for r in self.results
        )

# Define rules
engine = DataQualityEngine()

engine.add_rule(QualityRule(
    name="no_null_order_ids",
    description="Order ID must never be null",
    check_fn=lambda df: (
        df['order_id'].notna().all(),
        {"null_count": int(df['order_id'].isna().sum())}
    ),
    severity=Severity.CRITICAL,
    tags=["completeness"],
))

engine.add_rule(QualityRule(
    name="amount_in_range",
    description="Order amounts should be between 0 and 100000",
    check_fn=lambda df: (
        ((df['amount'] >= 0) & (df['amount'] <= 100000)).all(),
        {
            "out_of_range": int(((df['amount'] < 0) | (df['amount'] > 100000)).sum()),
            "min": float(df['amount'].min()),
            "max": float(df['amount'].max()),
        }
    ),
    severity=Severity.ERROR,
    tags=["validity"],
))

engine.add_rule(QualityRule(
    name="freshness_check",
    description="Most recent record should be within 2 hours",
    check_fn=lambda df: (
        (datetime.utcnow() - pd.to_datetime(df['created_at']).max()).total_seconds() < 7200,
        {"max_timestamp": str(pd.to_datetime(df['created_at']).max())}
    ),
    severity=Severity.ERROR,
    tags=["freshness"],
))

engine.add_rule(QualityRule(
    name="volume_anomaly",
    description="Row count should be within 50% of expected",
    check_fn=lambda df: (
        5000 <= len(df) <= 50000,
        {"actual_count": len(df), "expected_range": "5000-50000"}
    ),
    severity=Severity.WARNING,
    tags=["volume"],
))

# Run and check
results = engine.run(df)
if engine.has_failures():
    # Send alert, quarantine data, block pipeline
    send_alert(results)
```

---

## 4. Data SLAs & SLOs

```python
@dataclass
class DataSLA:
    table_name: str
    freshness_hours: float      # Max hours since last update
    completeness_pct: float     # Min % non-null for key columns
    accuracy_threshold: float   # Min accuracy score
    volume_tolerance_pct: float # Max % deviation from expected volume
    
    def check_freshness(self, max_timestamp: datetime) -> bool:
        age_hours = (datetime.utcnow() - max_timestamp).total_seconds() / 3600
        return age_hours <= self.freshness_hours
    
    def check_volume(self, actual: int, expected: int) -> bool:
        if expected == 0:
            return actual == 0
        deviation = abs(actual - expected) / expected
        return deviation <= self.volume_tolerance_pct / 100

# Define SLAs per table
SLAS = {
    "fct_orders": DataSLA(
        table_name="fct_orders",
        freshness_hours=2,
        completeness_pct=99.9,
        accuracy_threshold=0.99,
        volume_tolerance_pct=30,
    ),
    "dim_customers": DataSLA(
        table_name="dim_customers",
        freshness_hours=24,
        completeness_pct=95,
        accuracy_threshold=0.95,
        volume_tolerance_pct=10,
    ),
}

# SLA monitoring job
def check_all_slas():
    violations = []
    for table, sla in SLAS.items():
        # Check freshness
        max_ts = get_max_timestamp(table)
        if not sla.check_freshness(max_ts):
            violations.append(f"{table}: stale ({max_ts})")
        
        # Check volume
        actual_count = get_row_count(table, today=True)
        expected_count = get_historical_avg(table, lookback_days=7)
        if not sla.check_volume(actual_count, expected_count):
            violations.append(f"{table}: volume anomaly ({actual_count} vs expected {expected_count})")
    
    if violations:
        alert_oncall(violations)
    return violations
```

---

## 5. Anomaly Detection

```python
import numpy as np
from scipy import stats

class DataAnomalyDetector:
    """Statistical anomaly detection for data quality."""
    
    def __init__(self, lookback_days: int = 30, z_threshold: float = 3.0):
        self.lookback_days = lookback_days
        self.z_threshold = z_threshold
    
    def detect_volume_anomaly(self, historical_counts: list[int], current_count: int) -> dict:
        """Detect if today's volume is anomalous."""
        mean = np.mean(historical_counts)
        std = np.std(historical_counts)
        
        if std == 0:
            return {"is_anomaly": current_count != mean, "z_score": 0}
        
        z_score = (current_count - mean) / std
        is_anomaly = abs(z_score) > self.z_threshold
        
        return {
            "is_anomaly": is_anomaly,
            "z_score": round(z_score, 2),
            "current": current_count,
            "expected_mean": round(mean, 0),
            "expected_std": round(std, 0),
            "lower_bound": round(mean - self.z_threshold * std, 0),
            "upper_bound": round(mean + self.z_threshold * std, 0),
        }
    
    def detect_distribution_drift(self, baseline: pd.Series, current: pd.Series) -> dict:
        """Detect if column distribution has drifted."""
        # Kolmogorov-Smirnov test
        ks_stat, p_value = stats.ks_2samp(baseline, current)
        
        return {
            "is_drifted": p_value < 0.05,
            "ks_statistic": round(ks_stat, 4),
            "p_value": round(p_value, 4),
            "baseline_mean": round(baseline.mean(), 2),
            "current_mean": round(current.mean(), 2),
        }
    
    def detect_null_spike(self, historical_null_rates: list[float], current_null_rate: float) -> dict:
        """Detect unexpected increase in null values."""
        mean_null_rate = np.mean(historical_null_rates)
        threshold = max(mean_null_rate * 2, 0.01)  # Double historical or 1%
        
        return {
            "is_anomaly": current_null_rate > threshold,
            "current_null_rate": round(current_null_rate, 4),
            "historical_avg": round(mean_null_rate, 4),
            "threshold": round(threshold, 4),
        }
```

---

## 6. Pipeline Integration Pattern

```python
# Integrate quality checks into your pipeline
class QualityGatedPipeline:
    """Pipeline that stops if quality fails."""
    
    def __init__(self, engine: DataQualityEngine, quarantine_path: str):
        self.engine = engine
        self.quarantine_path = quarantine_path
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run pipeline with quality gates."""
        # Pre-transform quality check
        pre_results = self.engine.run(df)
        if self.engine.has_failures(Severity.CRITICAL):
            self._quarantine(df, pre_results, stage="pre_transform")
            raise DataQualityError("Critical quality issues in source data")
        
        # Transform
        transformed = self._transform(df)
        
        # Post-transform quality check (different rules)
        post_results = self.engine.run(transformed)
        if self.engine.has_failures(Severity.ERROR):
            self._quarantine(transformed, post_results, stage="post_transform")
            raise DataQualityError("Quality degraded after transformation")
        
        return transformed
    
    def _quarantine(self, df: pd.DataFrame, results: list, stage: str):
        """Send bad data to quarantine for investigation."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        path = f"{self.quarantine_path}/{stage}/{timestamp}/"
        df.to_parquet(f"{path}/data.parquet")
        # Also save quality report
        pd.DataFrame([r.__dict__ for r in results]).to_json(f"{path}/quality_report.json")
```

---

## Interview Questions

### Beginner
1. **What are the main dimensions of data quality?** Completeness, accuracy, freshness, consistency, uniqueness, validity. Different tables may prioritize different dimensions.
2. **What is Great Expectations?** Python library for data quality testing. Define "expectations" (assertions about data), run them in checkpoints, generate data docs (HTML reports).
3. **Why is data freshness important?** Stale data leads to wrong decisions. A dashboard showing yesterday's data when real-time is expected is a quality issue.

### Intermediate
4. **How do you implement quality gates in a pipeline?** Check quality after each major step (extract, transform, load). Block downstream if critical failures. Quarantine bad data for investigation. Alert data team. Allow pipeline to continue for warnings.
5. **Explain data observability vs data quality.** Quality: are values correct? (testing). Observability: can I detect and diagnose issues? (monitoring, lineage, alerting, anomaly detection). Observability helps you find quality problems faster.
6. **How do you handle data that fails quality checks?** Dead letter queue / quarantine for bad records. Route good records forward. Alert owners. Provide investigation tools (who, when, what failed). Reprocess after fix.

### Advanced
7. **Design a data quality platform for 500 tables.** Centralized metadata-driven rules (config per table), anomaly detection (statistical baselines), SLA monitoring, automated alerting (PagerDuty/Slack), quality dashboard, lineage integration, self-service rule creation for data owners.
8. **How do you balance quality strictness vs pipeline availability?** Circuit breaker pattern: block for critical issues, warn for non-critical. Different SLAs per table importance. Partial failures: load good records, quarantine bad. Time-based SLAs for resolution. Business input on quality thresholds.
9. **Explain how to detect silent data quality issues.** Statistical anomaly detection (z-score on volume, distributions), drift detection (KS test), cross-system reconciliation (source vs warehouse counts), automated profiling, trend monitoring (gradual degradation alerts).

---

## Hands-On Exercise
1. Set up Great Expectations with a sample dataset
2. Define expectations for completeness, validity, uniqueness
3. Build a custom quality engine with severity-based rules
4. Implement anomaly detection for volume and distribution
5. Create a quality dashboard (track pass/fail over time)
6. Build a pipeline with quality gates and quarantine
