# Day 26: CI/CD for ML

## Learning Objectives
- Understand ML CI/CD vs traditional software CI/CD
- Implement testing for ML code (unit, data, model tests)
- Build GitHub Actions workflows for ML pipelines
- Design automated retraining and model validation gates
- Implement continuous training (CT) pipelines

---

## 1. ML CI/CD vs Traditional CI/CD

```
Traditional Software CI/CD:
Code Change → Build → Test → Deploy

ML CI/CD (adds data + model dimensions):
Code Change ─┐
Data Change ──┼─→ Build → Test Code → Test Data → Train → Validate Model → Deploy
Config Change ┘

Key differences:
- Triggered by code, data, OR config changes
- Testing includes data validation + model quality checks
- "Build" includes training (expensive, GPU)
- Deployment requires model validation gates
- Rollback is more complex (model + code + data)
```

---

## 2. Testing ML Code

```python
# tests/test_preprocessing.py
import pytest
import pandas as pd
import numpy as np
from src.preprocess import clean_data, encode_features, split_data

# --- Unit Tests (code correctness) ---
class TestPreprocessing:
    def test_clean_data_removes_nulls(self):
        df = pd.DataFrame({"a": [1, None, 3], "b": [4, 5, None]})
        result = clean_data(df)
        assert result.isnull().sum().sum() == 0
    
    def test_encode_features_correct_shape(self):
        df = pd.DataFrame({"category": ["a", "b", "a"], "value": [1, 2, 3]})
        encoded = encode_features(df)
        assert encoded.shape[1] >= 2  # At least original columns
    
    def test_split_preserves_size(self):
        df = pd.DataFrame({"x": range(100), "y": range(100)})
        train, test = split_data(df, test_size=0.2)
        assert len(train) == 80
        assert len(test) == 20

# --- Data Tests (data quality) ---
class TestDataQuality:
    @pytest.fixture
    def training_data(self):
        return pd.read_parquet("data/processed/train.parquet")
    
    def test_no_nulls_in_features(self, training_data):
        assert training_data.isnull().sum().sum() == 0
    
    def test_target_distribution(self, training_data):
        """Target should not be too imbalanced."""
        ratio = training_data["target"].value_counts(normalize=True).min()
        assert ratio > 0.05, f"Target too imbalanced: minority class = {ratio:.2%}"
    
    def test_feature_ranges(self, training_data):
        """Features should be within expected ranges."""
        assert training_data["age"].between(0, 120).all()
        assert training_data["amount"].ge(0).all()
    
    def test_no_data_leakage(self, training_data):
        """Ensure no future data in training."""
        assert (training_data["event_date"] < "2025-01-01").all()
    
    def test_schema_unchanged(self, training_data):
        expected_columns = ["feature_1", "feature_2", "target"]
        assert all(col in training_data.columns for col in expected_columns)

# --- Model Tests (model quality) ---
class TestModel:
    @pytest.fixture
    def model_and_data(self):
        import joblib
        model = joblib.load("models/model.pkl")
        test_data = pd.read_parquet("data/processed/test.parquet")
        return model, test_data
    
    def test_model_accuracy_threshold(self, model_and_data):
        model, data = model_and_data
        X = data.drop("target", axis=1)
        y = data["target"]
        accuracy = model.score(X, y)
        assert accuracy > 0.85, f"Model accuracy {accuracy:.3f} below threshold 0.85"
    
    def test_model_no_prediction_bias(self, model_and_data):
        model, data = model_and_data
        X = data.drop("target", axis=1)
        preds = model.predict(X)
        pred_ratio = preds.mean()
        actual_ratio = data["target"].mean()
        assert abs(pred_ratio - actual_ratio) < 0.1, "Prediction bias detected"
    
    def test_model_latency(self, model_and_data):
        """Single prediction should be fast."""
        import time
        model, data = model_and_data
        X_single = data.drop("target", axis=1).iloc[:1]
        
        start = time.time()
        for _ in range(100):
            model.predict(X_single)
        avg_latency_ms = (time.time() - start) / 100 * 1000
        
        assert avg_latency_ms < 50, f"Latency {avg_latency_ms:.1f}ms exceeds 50ms threshold"
```

---

## 3. GitHub Actions for ML

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'params.yaml'
      - 'data/**/*.dvc'
  pull_request:
    branches: [main]
  workflow_dispatch:  # Manual trigger

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run unit tests
        run: pytest tests/test_preprocessing.py -v
      
      - name: Run data tests
        run: pytest tests/test_data_quality.py -v
        env:
          DVC_REMOTE_ACCESS_KEY: ${{ secrets.AWS_ACCESS_KEY }}

  train:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup DVC
        run: |
          pip install dvc[s3]
          dvc pull
      
      - name: Run training pipeline
        run: dvc repro
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_URI }}
      
      - name: Run model tests
        run: pytest tests/test_model.py -v
      
      - name: Upload metrics
        run: |
          echo "## Model Metrics" >> $GITHUB_STEP_SUMMARY
          cat metrics/eval_metrics.json >> $GITHUB_STEP_SUMMARY

  validate-and-deploy:
    needs: train
    runs-on: ubuntu-latest
    steps:
      - name: Check model quality gate
        run: |
          python -c "
          import json
          metrics = json.load(open('metrics/eval_metrics.json'))
          assert metrics['accuracy'] > 0.85, 'Accuracy below threshold'
          assert metrics['f1'] > 0.80, 'F1 below threshold'
          print('✅ Model passes quality gates')
          "
      
      - name: Deploy model
        if: success()
        run: |
          python src/deploy.py --model-path models/model.pkl --stage production
```

---

## 4. Automated Retraining

```python
# Triggers for automated retraining:
# 1. Schedule (weekly/monthly) — simplest
# 2. Data drift detected — performance may degrade
# 3. Performance drop — actual degradation measured
# 4. New data threshold — enough new data accumulated

# retraining_trigger.py
import json
from datetime import datetime, timedelta

class RetrainingTrigger:
    def __init__(self, config: dict):
        self.min_accuracy = config.get("min_accuracy", 0.85)
        self.max_days_since_train = config.get("max_days", 30)
        self.min_new_samples = config.get("min_new_samples", 10000)
    
    def should_retrain(self, current_metrics: dict, metadata: dict) -> tuple[bool, str]:
        # Check performance degradation
        if current_metrics["accuracy"] < self.min_accuracy:
            return True, f"Accuracy dropped to {current_metrics['accuracy']:.3f}"
        
        # Check staleness
        last_trained = datetime.fromisoformat(metadata["last_trained"])
        if datetime.now() - last_trained > timedelta(days=self.max_days_since_train):
            return True, f"Model is {(datetime.now() - last_trained).days} days old"
        
        # Check new data volume
        if metadata["new_samples_since_train"] > self.min_new_samples:
            return True, f"{metadata['new_samples_since_train']} new samples available"
        
        return False, "No retraining needed"

# GitHub Actions cron trigger for scheduled retraining:
# on:
#   schedule:
#     - cron: '0 2 * * 1'  # Every Monday at 2 AM
```

---

## 5. Model Validation Gates

```python
# Quality gates: automated checks model must pass before deployment

class ModelValidationGate:
    """Model must pass ALL checks before deployment."""
    
    def __init__(self, baseline_metrics: dict):
        self.baseline = baseline_metrics
        self.checks = []
    
    def validate(self, new_metrics: dict, model) -> tuple[bool, list[str]]:
        failures = []
        
        # 1. Absolute threshold
        if new_metrics["accuracy"] < 0.85:
            failures.append(f"Accuracy {new_metrics['accuracy']:.3f} < 0.85")
        
        # 2. No regression vs current production
        if new_metrics["accuracy"] < self.baseline["accuracy"] - 0.02:
            failures.append(f"Regression: {new_metrics['accuracy']:.3f} vs baseline {self.baseline['accuracy']:.3f}")
        
        # 3. Fairness check (performance across subgroups)
        for group, group_acc in new_metrics.get("group_accuracies", {}).items():
            if group_acc < 0.80:
                failures.append(f"Fairness: {group} accuracy = {group_acc:.3f}")
        
        # 4. Latency check
        if new_metrics.get("p95_latency_ms", 0) > 100:
            failures.append(f"Latency P95 = {new_metrics['p95_latency_ms']}ms > 100ms")
        
        # 5. Model size check
        import os
        model_size_mb = os.path.getsize("models/model.pkl") / 1e6
        if model_size_mb > 500:
            failures.append(f"Model size {model_size_mb:.0f}MB > 500MB limit")
        
        passed = len(failures) == 0
        return passed, failures

# Usage in CI/CD:
gate = ModelValidationGate(baseline_metrics={"accuracy": 0.92})
passed, failures = gate.validate(new_metrics, model)
if not passed:
    print("❌ Model FAILED validation:")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("✅ Model passed all validation gates")
```

---

## 6. Continuous Training (CT) Pipeline

```python
# CT: Automated end-to-end pipeline that trains and deploys without human intervention

# Architecture:
# Data arrives → Validation → Feature engineering → Training → Validation gate → Deploy

# Implemented with: Airflow, Kubeflow, Vertex AI Pipelines, or GitHub Actions

# Example Airflow DAG for CT:
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {"retries": 2, "retry_delay": timedelta(minutes=5)}

with DAG("continuous_training", schedule_interval="@weekly", 
         default_args=default_args, start_date=datetime(2025, 1, 1)):
    
    validate_data = PythonOperator(
        task_id="validate_new_data",
        python_callable=run_data_validation,
    )
    
    compute_features = PythonOperator(
        task_id="compute_features",
        python_callable=run_feature_pipeline,
    )
    
    train_model = PythonOperator(
        task_id="train_model",
        python_callable=run_training,
    )
    
    validate_model = PythonOperator(
        task_id="validate_model",
        python_callable=run_model_validation,
    )
    
    deploy = PythonOperator(
        task_id="deploy_to_production",
        python_callable=deploy_model,
    )
    
    validate_data >> compute_features >> train_model >> validate_model >> deploy
```

---

## Interview Questions

### Beginner
1. **How does ML CI/CD differ from traditional software CI/CD?** ML CI/CD triggered by code, data, OR config changes. Includes data validation and model quality testing. "Build" step includes training (expensive, needs GPU). Deployment has model validation gates (accuracy thresholds). Adds continuous training (CT) alongside CI/CD.
2. **What types of tests should ML code have?** Unit tests (code logic correctness), data tests (schema, ranges, distributions, no leakage), model tests (accuracy thresholds, latency, no bias), integration tests (pipeline end-to-end). Run unit/data tests on every PR, model tests after training.
3. **What is a model validation gate?** Automated quality checks model must pass before deployment. Examples: accuracy > threshold, no regression vs baseline, fairness across subgroups, latency within SLA. Prevents deploying bad models. Blocks deployment on failure.

### Intermediate
4. **Design a GitHub Actions workflow for an ML project.** On PR: run unit tests + data tests (fast feedback). On merge to main: pull data (DVC), run pipeline (dvc repro), run model tests, validate metrics. On pass: register model in MLflow, deploy to staging. On schedule: check for drift, trigger retraining if needed.
5. **What triggers model retraining?** Schedule (weekly/monthly), performance degradation (monitoring alerts), data drift detected (distribution shift), new labeled data available (threshold reached), manual trigger (bug fix, architecture change). Best practice: combine scheduled + performance-based triggers.
6. **How do you test for data leakage in CI?** Verify temporal ordering (training data before evaluation date). Check features don't contain target information. Validate train/test split has no ID overlap. Assert feature computation uses only past data. Run point-in-time correctness tests on feature store joins.

### Advanced
7. **Design a continuous training system for a recommendation engine.** Data: clickstream → feature pipeline (hourly batch). Training: nightly on last 30 days of data. Validation: A/B test on 5% traffic. Promotion: if engagement metrics improve. Rollback: automatic if CTR drops >10%. Infrastructure: Kubeflow on K8s, MLflow registry, feature store (Feast+Redis).
8. **How do you handle GPU training in CI/CD?** Self-hosted runners with GPU. Or: cloud GPU (spot instances) triggered by CI. Cache training artifacts (checkpoints). Short CI jobs: use pre-trained checkpoints for validation. Full training: run nightly/weekly (not per-PR). Alternative: train locally, push model artifact, CI validates only.
9. **Design IaC for ML infrastructure.** Terraform modules: training cluster (GPU instances, auto-scaling), serving cluster (K8s + Triton), feature store (Redis + S3), MLflow server, monitoring (Prometheus + Grafana). Separate environments: dev/staging/prod. State management: Terraform Cloud. Secret management: AWS Secrets Manager.

---

## Hands-On Exercise
1. Write unit tests, data tests, and model tests for a sklearn pipeline
2. Create GitHub Actions workflow: test on PR, train on merge
3. Implement model validation gates (3 checks: accuracy, regression, latency)
4. Build automated retraining trigger (performance + schedule)
5. Create full DVC pipeline + GitHub Actions CI that runs `dvc repro`
6. Implement a simple CT pipeline with mock Airflow DAG
