# Day 22: MLOps Fundamentals

## Overview
MLOps bridges the gap between ML experimentation and production. Learn to build reproducible, scalable ML systems.

---

## 1. Why MLOps?

### The ML Lifecycle
```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│  Data    │──▶│  Feature │──▶│  Model   │──▶│  Deploy  │──▶│  Monitor │
│Collection│   │Engineering│   │ Training │   │& Serve   │   │& Retrain │
└──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘
      │                              │                              │
      └──────────────────── Continuous Loop ────────────────────────┘
```

### MLOps Maturity Levels
| Level | Description | Characteristics |
|-------|-------------|-----------------|
| 0 | Manual | Notebooks, no automation, ad-hoc deployments |
| 1 | ML Pipeline | Automated training, manual deployment |
| 2 | CI/CD for ML | Automated training + deployment + monitoring |
| 3 | Full Automation | Auto-retrain on drift, A/B testing, feature stores |

---

## 2. Experiment Tracking

### Why Track Experiments?
- Reproducibility: "Which hyperparams gave that result?"
- Comparison: "Is model v2 better than v1?"
- Collaboration: "What did my teammate try?"
- Auditing: "Why did we choose this model?"

### MLflow Tracking
```python
import mlflow
import mlflow.sklearn
from sklearn.metrics import accuracy_score, f1_score

# Set tracking server
mlflow.set_tracking_uri("http://mlflow-server:5000")
mlflow.set_experiment("customer-churn-prediction")

# Start experiment run
with mlflow.start_run(run_name="xgboost-v2"):
    # Log parameters
    params = {
        "n_estimators": 200,
        "max_depth": 6,
        "learning_rate": 0.1,
        "subsample": 0.8,
    }
    mlflow.log_params(params)
    
    # Train model
    model = XGBClassifier(**params)
    model.fit(X_train, y_train)
    
    # Log metrics
    y_pred = model.predict(X_test)
    mlflow.log_metrics({
        "accuracy": accuracy_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
    })
    
    # Log model
    mlflow.sklearn.log_model(
        model, 
        "model",
        registered_model_name="churn-predictor"
    )
    
    # Log artifacts
    mlflow.log_artifact("feature_importance.png")
    mlflow.log_artifact("confusion_matrix.png")
    
    # Log dataset info
    mlflow.log_param("train_size", len(X_train))
    mlflow.log_param("test_size", len(X_test))
    mlflow.log_param("features", list(X_train.columns))
```

### Weights & Biases (Alternative)
```python
import wandb

wandb.init(project="churn-prediction", name="xgboost-v2")
wandb.config.update(params)

# Training loop with logging
for epoch in range(num_epochs):
    train_loss = train_one_epoch(model, train_loader)
    val_loss, val_acc = evaluate(model, val_loader)
    
    wandb.log({
        "train_loss": train_loss,
        "val_loss": val_loss,
        "val_accuracy": val_acc,
        "epoch": epoch
    })

wandb.finish()
```

---

## 3. Model Registry

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Register model
model_version = client.create_model_version(
    name="churn-predictor",
    source="runs:/abc123/model",
    run_id="abc123"
)

# Transition model stages
client.transition_model_version_stage(
    name="churn-predictor",
    version=model_version.version,
    stage="Staging"  # None → Staging → Production → Archived
)

# Load production model
import mlflow.pyfunc
model = mlflow.pyfunc.load_model("models:/churn-predictor/Production")
predictions = model.predict(new_data)
```

---

## 4. Reproducibility

### Data Versioning with DVC
```bash
# Initialize DVC
dvc init
git add .dvc .dvcignore

# Track large data files
dvc add data/training_data.parquet
git add data/training_data.parquet.dvc data/.gitignore

# Push data to remote storage
dvc remote add -d storage s3://my-bucket/dvc
dvc push

# Reproduce pipeline
dvc repro  # Runs stages that have changed inputs
```

### DVC Pipeline
```yaml
# dvc.yaml
stages:
  preprocess:
    cmd: python src/preprocess.py
    deps:
      - src/preprocess.py
      - data/raw/
    outs:
      - data/processed/
    params:
      - preprocess.train_ratio
      - preprocess.seed

  train:
    cmd: python src/train.py
    deps:
      - src/train.py
      - data/processed/
    outs:
      - models/model.pkl
    params:
      - train.n_estimators
      - train.max_depth
    metrics:
      - metrics.json:
          cache: false

  evaluate:
    cmd: python src/evaluate.py
    deps:
      - src/evaluate.py
      - models/model.pkl
      - data/processed/test.parquet
    metrics:
      - evaluation/metrics.json:
          cache: false
    plots:
      - evaluation/confusion_matrix.png
```

### Environment Pinning
```dockerfile
# Dockerfile for reproducible training
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY configs/ ./configs/

ENTRYPOINT ["python", "src/train.py"]
```

```txt
# requirements.txt (pinned versions!)
scikit-learn==1.4.0
xgboost==2.0.3
pandas==2.2.0
mlflow==2.10.0
numpy==1.26.3
```

---

## 5. Feature Stores

```python
# Feature store concept: centralized feature management
# Ensures same features used in training and serving

from feast import FeatureStore

store = FeatureStore(repo_path=".")

# Define features
"""
# feature_repo/features.py
from feast import Entity, Feature, FeatureView, FileSource
from feast.types import Float32, Int64

customer = Entity(name="customer_id", join_keys=["customer_id"])

customer_features = FeatureView(
    name="customer_features",
    entities=[customer],
    schema=[
        Feature(name="total_orders", dtype=Int64),
        Feature(name="avg_order_value", dtype=Float32),
        Feature(name="days_since_last_order", dtype=Int64),
        Feature(name="lifetime_value", dtype=Float32),
    ],
    source=BigQuerySource(
        table="project.dataset.customer_features",
        timestamp_field="event_timestamp",
    ),
    ttl=timedelta(days=1),
)
"""

# Training: Get historical features (point-in-time correct!)
training_df = store.get_historical_features(
    entity_df=entity_df,  # customer_id + event_timestamp
    features=[
        "customer_features:total_orders",
        "customer_features:avg_order_value",
        "customer_features:days_since_last_order",
    ]
).to_df()

# Serving: Get latest features (real-time)
online_features = store.get_online_features(
    features=[...],
    entity_rows=[{"customer_id": "C123"}]
).to_dict()
```

---

## 6. ML Pipeline Orchestration

```python
# Airflow DAG for ML training pipeline
from airflow import DAG
from airflow.operators.python import PythonOperator

with DAG('ml_training_pipeline', schedule_interval='@weekly') as dag:
    
    extract_features = PythonOperator(
        task_id='extract_features',
        python_callable=run_feature_engineering,
    )
    
    validate_data = PythonOperator(
        task_id='validate_data',
        python_callable=run_data_validation,
    )
    
    train_model = PythonOperator(
        task_id='train_model',
        python_callable=run_training,
    )
    
    evaluate_model = PythonOperator(
        task_id='evaluate_model',
        python_callable=run_evaluation,
    )
    
    deploy_if_better = PythonOperator(
        task_id='deploy_if_better',
        python_callable=conditional_deployment,
    )
    
    extract_features >> validate_data >> train_model >> evaluate_model >> deploy_if_better
```

---

## 7. MLOps Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline                          │
├──────────┬───────────┬────────────┬───────────┬──────────┤
│ Data     │ Feature   │ Training   │ Evaluation│ Deploy   │
│ Ingest   │ Store     │ Pipeline   │ & Registry│ & Serve  │
│          │           │            │           │          │
│ Airflow  │ Feast     │ Train +    │ MLflow    │ K8s +    │
│ Kafka    │ Tecton    │ Track      │ Evaluate  │ Seldon   │
│ Spark    │           │ MLflow/W&B │ Compare   │ BentoML  │
└──────┬───┴───────────┴──────┬─────┴───────────┴─────┬────┘
       │                      │                        │
       ▼                      ▼                        ▼
┌──────────────┐    ┌─────────────────┐    ┌───────────────┐
│ Data Lake    │    │ Model Registry   │    │ Monitoring    │
│ (S3/GCS)    │    │ (Versioned models)│    │ (Drift, perf) │
└──────────────┘    └─────────────────┘    └───────────────┘
```

---

## Key Takeaways
- MLOps = DevOps + Data Engineering + ML Engineering
- Track EVERYTHING: params, metrics, data versions, code versions
- Reproducibility requires: pinned deps + data versioning + experiment tracking
- Feature stores prevent training-serving skew
- Start at Level 1 (automated pipeline) before attempting Level 3
- Use MLflow for experiment tracking + model registry

## Tomorrow
**Day 23**: MLflow Deep Dive — Advanced tracking, model registry workflows, and custom model flavors.
