# Day 27: Model Monitoring

## Learning Objectives
- Detect data drift (KL divergence, PSI, KS test)
- Monitor concept drift and model performance degradation
- Use monitoring tools (Evidently AI, WhyLabs, NannyML)
- Configure alerts and automated retraining triggers
- Implement shadow mode deployment

---

## 1. Data Drift Detection

```python
import numpy as np
from scipy import stats

# Data drift: input feature distributions change over time
# Training distribution ≠ Production distribution → model may fail

# Method 1: Population Stability Index (PSI)
def calculate_psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """
    PSI measures how much a distribution has shifted.
    PSI < 0.1: No significant drift
    PSI 0.1-0.25: Moderate drift (investigate)
    PSI > 0.25: Significant drift (action needed)
    """
    # Bin the expected distribution
    breakpoints = np.percentile(expected, np.linspace(0, 100, bins + 1))
    breakpoints[0], breakpoints[-1] = -np.inf, np.inf
    
    expected_counts = np.histogram(expected, bins=breakpoints)[0] / len(expected)
    actual_counts = np.histogram(actual, bins=breakpoints)[0] / len(actual)
    
    # Avoid division by zero
    expected_counts = np.clip(expected_counts, 1e-6, None)
    actual_counts = np.clip(actual_counts, 1e-6, None)
    
    psi = np.sum((actual_counts - expected_counts) * np.log(actual_counts / expected_counts))
    return psi

# Method 2: Kolmogorov-Smirnov Test
def ks_drift_test(reference: np.ndarray, current: np.ndarray, threshold: float = 0.05):
    """KS test: are two samples from the same distribution?"""
    statistic, p_value = stats.ks_2samp(reference, current)
    is_drift = p_value < threshold
    return {"statistic": statistic, "p_value": p_value, "drift_detected": is_drift}

# Method 3: KL Divergence
def kl_divergence(p: np.ndarray, q: np.ndarray, bins: int = 50) -> float:
    """KL divergence between two distributions."""
    p_hist = np.histogram(p, bins=bins, density=True)[0] + 1e-8
    q_hist = np.histogram(q, bins=bins, density=True)[0] + 1e-8
    return stats.entropy(p_hist, q_hist)

# Monitor all features
class DriftMonitor:
    def __init__(self, reference_data: dict[str, np.ndarray]):
        self.reference = reference_data
    
    def check_drift(self, current_data: dict[str, np.ndarray]) -> dict:
        results = {}
        for feature, ref_values in self.reference.items():
            curr_values = current_data.get(feature, np.array([]))
            if len(curr_values) == 0:
                continue
            
            psi = calculate_psi(ref_values, curr_values)
            ks = ks_drift_test(ref_values, curr_values)
            
            results[feature] = {
                "psi": round(psi, 4),
                "ks_statistic": round(ks["statistic"], 4),
                "drift_detected": psi > 0.25 or ks["drift_detected"],
            }
        return results
```

---

## 2. Concept Drift & Performance Monitoring

```python
# Concept drift: relationship between features and target changes
# Feature distributions may be stable, but model accuracy drops
# Example: customer behavior changes due to economic shift

from datetime import datetime, timedelta

class PerformanceMonitor:
    def __init__(self, alert_threshold: float = 0.05):
        self.baseline_metrics = {}
        self.alert_threshold = alert_threshold  # Max allowed degradation
        self.history = []
    
    def set_baseline(self, metrics: dict):
        """Set baseline from training evaluation."""
        self.baseline_metrics = metrics
    
    def log_metrics(self, metrics: dict, timestamp: datetime = None):
        """Log production metrics."""
        timestamp = timestamp or datetime.now()
        self.history.append({"timestamp": timestamp, **metrics})
    
    def check_degradation(self, current_metrics: dict) -> dict:
        """Compare current performance to baseline."""
        alerts = []
        for metric, baseline_value in self.baseline_metrics.items():
            current_value = current_metrics.get(metric)
            if current_value is None:
                continue
            
            degradation = baseline_value - current_value
            if degradation > self.alert_threshold:
                alerts.append({
                    "metric": metric,
                    "baseline": baseline_value,
                    "current": current_value,
                    "degradation": degradation,
                    "severity": "critical" if degradation > 2 * self.alert_threshold else "warning",
                })
        
        return {"alerts": alerts, "action_needed": len(alerts) > 0}
    
    def detect_trend(self, window_days: int = 7) -> dict:
        """Detect gradual performance decline (concept drift)."""
        cutoff = datetime.now() - timedelta(days=window_days)
        recent = [h for h in self.history if h["timestamp"] > cutoff]
        
        if len(recent) < 3:
            return {"trend": "insufficient_data"}
        
        # Check if accuracy is trending down
        accuracies = [h.get("accuracy", 0) for h in recent]
        slope = np.polyfit(range(len(accuracies)), accuracies, 1)[0]
        
        if slope < -0.001:  # Declining trend
            return {"trend": "declining", "slope": slope, "action": "investigate"}
        return {"trend": "stable", "slope": slope}
```

---

## 3. Evidently AI (Drift & Quality Reports)

```python
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, ClassificationPreset
from evidently.test_suite import TestSuite
from evidently.tests import *

# Generate data drift report
reference_data = pd.read_parquet("data/reference.parquet")  # Training data
current_data = pd.read_parquet("data/production_last_week.parquet")

# Drift report (all features)
drift_report = Report(metrics=[DataDriftPreset()])
drift_report.run(reference_data=reference_data, current_data=current_data)
drift_report.save_html("reports/drift_report.html")

# Get results as dict
drift_results = drift_report.as_dict()
n_drifted = drift_results["metrics"][0]["result"]["number_of_drifted_columns"]
print(f"Drifted features: {n_drifted}")

# Classification performance report (requires labels)
column_mapping = ColumnMapping(target="label", prediction="prediction")
perf_report = Report(metrics=[ClassificationPreset()])
perf_report.run(reference_data=reference_data, current_data=current_data,
                column_mapping=column_mapping)

# Automated tests (pass/fail for CI/CD)
test_suite = TestSuite(tests=[
    TestShareOfDriftedColumns(lt=0.3),  # Less than 30% features drifted
    TestColumnDrift("age"),             # Specific column not drifted
    TestMeanInNSigmas("amount", n=3),   # Amount mean within 3 sigma
])
test_suite.run(reference_data=reference_data, current_data=current_data)
test_results = test_suite.as_dict()
all_passed = all(t["status"] == "SUCCESS" for t in test_results["tests"])
```

---

## 4. Alert Configuration

```python
import smtplib
from dataclasses import dataclass
from enum import Enum

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class Alert:
    severity: AlertSeverity
    metric: str
    message: str
    timestamp: datetime
    value: float
    threshold: float

class AlertManager:
    def __init__(self):
        self.rules = []
        self.handlers = []
    
    def add_rule(self, metric: str, threshold: float, severity: AlertSeverity, 
                 comparison: str = "lt"):
        self.rules.append({
            "metric": metric, "threshold": threshold, 
            "severity": severity, "comparison": comparison,
        })
    
    def check(self, metrics: dict) -> list[Alert]:
        alerts = []
        for rule in self.rules:
            value = metrics.get(rule["metric"])
            if value is None:
                continue
            
            triggered = (
                (rule["comparison"] == "lt" and value < rule["threshold"]) or
                (rule["comparison"] == "gt" and value > rule["threshold"])
            )
            
            if triggered:
                alerts.append(Alert(
                    severity=rule["severity"],
                    metric=rule["metric"],
                    message=f"{rule['metric']} = {value:.4f} (threshold: {rule['threshold']})",
                    timestamp=datetime.now(),
                    value=value,
                    threshold=rule["threshold"],
                ))
        return alerts
    
    def send_alerts(self, alerts: list[Alert]):
        for alert in alerts:
            if alert.severity == AlertSeverity.CRITICAL:
                self._send_pagerduty(alert)
            elif alert.severity == AlertSeverity.WARNING:
                self._send_slack(alert)

# Configure monitoring
monitor = AlertManager()
monitor.add_rule("accuracy", threshold=0.85, severity=AlertSeverity.CRITICAL, comparison="lt")
monitor.add_rule("p95_latency_ms", threshold=200, severity=AlertSeverity.WARNING, comparison="gt")
monitor.add_rule("data_drift_score", threshold=0.25, severity=AlertSeverity.WARNING, comparison="gt")
```

---

## 5. Shadow Mode Deployment

```python
# Shadow mode: new model receives real traffic but doesn't affect users
# Compare predictions with production model in real-time

class ShadowDeployment:
    """
    Run new model in shadow (no user impact), log differences.
    If shadow model performs better over N days → promote to production.
    """
    
    def __init__(self, production_model, shadow_model):
        self.production = production_model
        self.shadow = shadow_model
        self.comparison_log = []
    
    def predict(self, features):
        """Serve production prediction, log shadow prediction."""
        # Production prediction (returned to user)
        prod_prediction = self.production.predict(features)
        
        # Shadow prediction (logged only, not returned)
        shadow_prediction = self.shadow.predict(features)
        
        self.comparison_log.append({
            "timestamp": datetime.now(),
            "production": prod_prediction,
            "shadow": shadow_prediction,
            "features_hash": hash(str(features)),
        })
        
        return prod_prediction  # Only production result goes to user
    
    def evaluate_shadow(self, actuals: list) -> dict:
        """Once labels available, compare prod vs shadow accuracy."""
        prod_correct = sum(1 for log, actual in zip(self.comparison_log, actuals)
                         if log["production"] == actual)
        shadow_correct = sum(1 for log, actual in zip(self.comparison_log, actuals)
                           if log["shadow"] == actual)
        
        n = len(actuals)
        return {
            "production_accuracy": prod_correct / n,
            "shadow_accuracy": shadow_correct / n,
            "shadow_wins": shadow_correct > prod_correct,
            "improvement": (shadow_correct - prod_correct) / n,
        }
```

---

## 6. Full Monitoring Pipeline

```python
# End-to-end monitoring: runs on schedule (hourly/daily)

class MonitoringPipeline:
    def __init__(self, reference_data, model_name: str):
        self.drift_monitor = DriftMonitor(reference_data)
        self.perf_monitor = PerformanceMonitor()
        self.alert_manager = AlertManager()
        self.model_name = model_name
    
    def run(self, production_data: pd.DataFrame, labels: pd.Series = None):
        """Run full monitoring check."""
        results = {"timestamp": datetime.now(), "model": self.model_name}
        
        # 1. Data drift check
        feature_data = {col: production_data[col].values for col in production_data.columns}
        drift_results = self.drift_monitor.check_drift(feature_data)
        drifted_features = [f for f, r in drift_results.items() if r["drift_detected"]]
        results["drift"] = {
            "features_checked": len(drift_results),
            "features_drifted": len(drifted_features),
            "drifted_list": drifted_features,
        }
        
        # 2. Performance check (if labels available)
        if labels is not None:
            predictions = model.predict(production_data)
            accuracy = (predictions == labels).mean()
            results["performance"] = {"accuracy": accuracy}
            self.perf_monitor.log_metrics({"accuracy": accuracy})
        
        # 3. Check alerts
        metrics_for_alert = {
            "data_drift_score": len(drifted_features) / max(len(drift_results), 1),
        }
        if labels is not None:
            metrics_for_alert["accuracy"] = accuracy
        
        alerts = self.alert_manager.check(metrics_for_alert)
        if alerts:
            self.alert_manager.send_alerts(alerts)
            results["alerts"] = [a.message for a in alerts]
        
        return results
```

---

## Interview Questions

### Beginner
1. **What is data drift?** Input feature distributions change between training and production. Example: training on summer data, deploying in winter (seasonal patterns differ). Causes model to make predictions on data unlike what it saw during training. Detected with PSI, KS test, or distribution comparison.
2. **What is the difference between data drift and concept drift?** Data drift: input distribution changes (features shift). Concept drift: the relationship between features and target changes (same inputs, different correct labels). Data drift detectable without labels; concept drift requires labels (delayed feedback).
3. **What is PSI?** Population Stability Index — measures how much a distribution has shifted. Bins reference distribution, compares bin proportions. PSI < 0.1: stable. 0.1-0.25: investigate. > 0.25: significant drift. Simple, interpretable, widely used in finance/insurance.

### Intermediate
4. **How do you monitor model performance without labels?** Use proxy metrics: prediction distribution shift, confidence score distribution, feature drift as early warning. Monitor operational metrics: latency, error rate, traffic patterns. Use delayed labels when available (fraud confirmed days later). Flag uncertain predictions for human review.
5. **Explain shadow mode deployment.** New model runs alongside production on real traffic. Production model serves users; shadow model's predictions are only logged. Compare after labels arrive (days/weeks). Promote shadow if it outperforms. Zero user risk. Downsides: double compute cost, need delayed labels for comparison.
6. **How do you set up drift monitoring for a feature store?** Monitor each feature independently (PSI/KS on each). Aggregate: alert if >30% features drift. Track feature freshness (stale features = pipeline issue). Compare online vs offline feature values (consistency). Dashboard: feature health per entity type.

### Advanced
7. **Design a monitoring system for a real-time fraud detection model.** Metrics: precision, recall, false positive rate (from delayed labels). Real-time: prediction latency P95/P99, throughput, error rate. Drift: transaction amount distribution, merchant category distribution, time-of-day patterns. Alerts: precision drops >5%, latency >100ms. Auto-action: route to rule-based system if ML model unreliable.
8. **How do you handle delayed labels for monitoring?** Problem: fraud confirmed days/weeks later. Solution: buffer predictions, evaluate when labels arrive. Interim monitoring: proxy metrics (confidence, drift). Backfill evaluation: nightly job joins predictions with new labels. Alert on: proxy metric degradation (immediate) + confirmed accuracy drop (delayed).
9. **Design an automated retraining pipeline triggered by monitoring.** Monitor → detect drift/degradation → trigger retraining (Airflow/GitHub Actions) → validate new model (quality gates) → shadow deployment (compare 7 days) → auto-promote if better → update baseline. Safeguards: human approval for >5% model change, rollback if production metrics drop post-deployment, max 1 retrain per week.

---

## Hands-On Exercise
1. Implement PSI and KS test for drift detection on synthetic data
2. Create a drift monitor that checks 5 features and flags drifted ones
3. Set up Evidently AI report (drift + performance) on a dataset pair
4. Build an alert system with severity levels and mock notifications
5. Implement shadow mode: log comparison between two model versions
6. Create end-to-end monitoring pipeline that produces a JSON report
