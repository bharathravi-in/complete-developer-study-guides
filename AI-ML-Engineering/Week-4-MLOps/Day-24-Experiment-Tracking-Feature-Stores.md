# Day 24: Experiment Tracking & Feature Stores

## Learning Objectives
- Use MLflow for experiment tracking, model registry, and artifacts
- Understand Weights & Biases for dashboards and sweeps
- Design feature stores for online/offline serving
- Ensure point-in-time correctness to avoid data leakage

---

## 1. MLflow Deep Dive

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

# Set tracking URI (local or remote)
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("fraud-detection-v2")

# Train with experiment tracking
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

with mlflow.start_run(run_name="rf-baseline"):
    # Log parameters
    params = {"n_estimators": 100, "max_depth": 10, "min_samples_split": 5}
    mlflow.log_params(params)
    
    # Train model
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)
    
    # Log metrics
    y_pred = model.predict(X_test)
    mlflow.log_metric("accuracy", accuracy_score(y_test, y_pred))
    mlflow.log_metric("f1", f1_score(y_test, y_pred))
    mlflow.log_metric("train_samples", len(X_train))
    
    # Log model
    mlflow.sklearn.log_model(model, "model")
    
    # Log artifacts (plots, data samples, configs)
    import matplotlib.pyplot as plt
    plt.figure()
    # ... create confusion matrix plot
    plt.savefig("confusion_matrix.png")
    mlflow.log_artifact("confusion_matrix.png")
    
    # Log dataset info
    mlflow.log_param("dataset_version", "v2.3")
    mlflow.log_param("features_used", str(feature_names))

# Model Registry: version and stage models
from mlflow.tracking import MlflowClient
client = MlflowClient()

# Register model
model_uri = f"runs:/{run_id}/model"
mlflow.register_model(model_uri, "fraud-detector")

# Transition to production
client.transition_model_version_stage(
    name="fraud-detector",
    version=3,
    stage="Production",
)

# Load production model for serving
model = mlflow.pyfunc.load_model("models:/fraud-detector/Production")
predictions = model.predict(new_data)
```

---

## 2. Weights & Biases

```python
import wandb

# Initialize project
wandb.init(
    project="fraud-detection",
    name="rf-tuning-v2",
    config={
        "n_estimators": 100,
        "max_depth": 10,
        "learning_rate": 0.01,
    }
)

# Log metrics during training
for epoch in range(100):
    train_loss = train_one_epoch()
    val_loss = evaluate()
    wandb.log({
        "train_loss": train_loss,
        "val_loss": val_loss,
        "epoch": epoch,
    })

# Log media (images, tables, plots)
wandb.log({"confusion_matrix": wandb.plot.confusion_matrix(
    y_true=y_test, preds=y_pred, class_names=["legit", "fraud"]
)})

# Hyperparameter sweeps
sweep_config = {
    "method": "bayes",  # bayesian optimization
    "metric": {"name": "val_f1", "goal": "maximize"},
    "parameters": {
        "n_estimators": {"values": [50, 100, 200, 500]},
        "max_depth": {"min": 3, "max": 20},
        "learning_rate": {"min": 0.001, "max": 0.1, "distribution": "log_uniform_values"},
    }
}

sweep_id = wandb.sweep(sweep_config, project="fraud-detection")

def train_sweep():
    wandb.init()
    config = wandb.config
    model = train_model(config)
    wandb.log({"val_f1": evaluate(model)})

wandb.agent(sweep_id, function=train_sweep, count=50)

wandb.finish()

# Comparison: MLflow vs W&B
# | Feature          | MLflow          | W&B             |
# |-----------------|-----------------|-----------------|
# | Open source     | Yes             | Partially       |
# | Self-hosted     | Yes             | Yes (enterprise)|
# | UI quality      | Good            | Excellent       |
# | Sweeps          | Manual          | Built-in        |
# | Model registry  | Built-in        | Via artifacts   |
# | Cost            | Free            | Free tier + paid|
# | Collaboration   | Basic           | Strong          |
```

---

## 3. Feature Stores

```python
# Feature Store: centralized repository for ML features
# Solves: feature reuse, online/offline consistency, point-in-time correctness

# Feast (open source feature store)
from feast import FeatureStore, Entity, FeatureView, Field
from feast.types import Float32, Int64
from feast.infra.offline_stores.file_source import FileSource

# Define entities (what features are about)
customer = Entity(name="customer_id", join_keys=["customer_id"])

# Define feature view (how to compute features)
customer_features = FeatureView(
    name="customer_features",
    entities=[customer],
    schema=[
        Field(name="total_purchases", dtype=Int64),
        Field(name="avg_order_value", dtype=Float32),
        Field(name="days_since_last_order", dtype=Int64),
        Field(name="lifetime_value", dtype=Float32),
    ],
    source=FileSource(path="data/customer_features.parquet", timestamp_field="event_timestamp"),
    ttl=timedelta(days=1),  # How fresh features must be
)

# Apply to feature store
# feast apply (CLI command)

# --- Offline Feature Retrieval (for training) ---
store = FeatureStore(repo_path="./feature_repo")

# Get historical features (point-in-time correct)
training_data = store.get_historical_features(
    entity_df=entity_df,  # DataFrame with customer_id + event_timestamp
    features=[
        "customer_features:total_purchases",
        "customer_features:avg_order_value",
        "customer_features:lifetime_value",
    ],
).to_df()

# --- Online Feature Retrieval (for serving) ---
# Materialize features to online store (Redis, DynamoDB)
# feast materialize-incremental $(date +%Y-%m-%dT%H:%M:%S)

online_features = store.get_online_features(
    features=[
        "customer_features:total_purchases",
        "customer_features:avg_order_value",
    ],
    entity_rows=[{"customer_id": 12345}],
).to_dict()
# Returns: {"customer_id": [12345], "total_purchases": [47], "avg_order_value": [89.5]}
```

---

## 4. Online vs Offline Feature Serving

```python
# Offline Store: Historical features for training
# - Storage: Data warehouse (BigQuery, Snowflake), Parquet, Delta Lake
# - Access pattern: Batch reads, large scans
# - Latency: Seconds to minutes (acceptable for training)
# - Point-in-time: Join features as they were AT training time

# Online Store: Real-time features for inference
# - Storage: Redis, DynamoDB, Bigtable
# - Access pattern: Key-value lookup by entity ID
# - Latency: <10ms (required for serving)
# - Freshness: Must be up-to-date

# Architecture:
# Batch pipeline → Offline Store (training)
#                ↓ materialization
#              Online Store (serving)
#
# Streaming pipeline → Online Store (real-time features)

# Example: Fraud detection features
# Offline (training): avg_transaction_amount_30d, num_transactions_7d (computed daily)
# Online (serving): same features, pre-computed and stored in Redis
# Real-time (streaming): transactions_last_5min, velocity_score (computed per event)

class FeatureService:
    """Unified feature access for training and serving."""
    
    def __init__(self, feast_store):
        self.store = feast_store
    
    def get_training_features(self, entity_df, feature_list):
        """Get point-in-time correct features for training."""
        return self.store.get_historical_features(
            entity_df=entity_df,
            features=feature_list,
        ).to_df()
    
    def get_serving_features(self, entity_ids: list[dict], feature_list):
        """Get latest features for real-time inference."""
        return self.store.get_online_features(
            features=feature_list,
            entity_rows=entity_ids,
        ).to_dict()
```

---

## 5. Point-in-Time Correctness

```python
# CRITICAL: Avoid data leakage in feature engineering
# Problem: Using future information to predict past events

# Example: Predicting if customer will churn THIS month
# Wrong: Use features computed from THIS month's data (includes outcome period)
# Right: Use features computed from LAST month's data only

# Point-in-time join:
# For each training example at time T, join features as they were AT time T
# (not current values, which include future information)

import pandas as pd

# Bad: simple join (uses latest feature values → data leakage!)
# training_df.merge(features_df, on="customer_id")  # WRONG!

# Good: point-in-time join
def point_in_time_join(
    entity_df: pd.DataFrame,    # columns: customer_id, event_timestamp
    feature_df: pd.DataFrame,   # columns: customer_id, feature_timestamp, features...
) -> pd.DataFrame:
    """Join features as-of entity timestamp (no future data)."""
    
    # Sort both by timestamp
    entity_df = entity_df.sort_values("event_timestamp")
    feature_df = feature_df.sort_values("feature_timestamp")
    
    # For each entity row, find latest feature BEFORE event_timestamp
    result = pd.merge_asof(
        entity_df,
        feature_df,
        left_on="event_timestamp",
        right_on="feature_timestamp",
        by="customer_id",
        direction="backward",  # Only look backwards in time
    )
    return result

# Feast handles this automatically in get_historical_features()
# This is one of the main reasons to use a feature store

# Common leakage patterns:
# 1. Target leakage: feature derived from target variable
# 2. Temporal leakage: using future data for past predictions
# 3. Group leakage: train/test split doesn't respect time
```

---

## 6. Feature Engineering Pipelines

```python
# Automated feature computation pipeline

from datetime import datetime, timedelta

class FeaturePipeline:
    """Compute features on schedule, write to feature store."""
    
    def __init__(self, db_connection, feature_store):
        self.db = db_connection
        self.store = feature_store
    
    def compute_customer_features(self, as_of_date: datetime) -> pd.DataFrame:
        """Compute customer features as of a specific date."""
        query = f"""
        SELECT 
            customer_id,
            COUNT(*) as total_purchases,
            AVG(amount) as avg_order_value,
            DATEDIFF('{as_of_date}', MAX(order_date)) as days_since_last_order,
            SUM(amount) as lifetime_value,
            STDDEV(amount) as order_value_stddev,
            COUNT(DISTINCT product_category) as categories_purchased
        FROM orders
        WHERE order_date < '{as_of_date}'
        GROUP BY customer_id
        """
        features_df = pd.read_sql(query, self.db)
        features_df["feature_timestamp"] = as_of_date
        return features_df
    
    def run_daily(self):
        """Daily feature computation job (run by Airflow/cron)."""
        today = datetime.now()
        features = self.compute_customer_features(today)
        
        # Write to offline store
        self.store.write_to_offline(features)
        
        # Materialize to online store (latest values)
        self.store.materialize(end_date=today)
        
        print(f"Computed features for {len(features)} customers as of {today}")

# Airflow DAG for scheduled feature computation:
# @daily
# compute_features >> validate_features >> materialize_to_online >> notify
```

---

## Interview Questions

### Beginner
1. **Why use experiment tracking?** Track hyperparameters, metrics, and artifacts across training runs. Compare experiments systematically. Reproduce results (know exact config that produced a model). Collaborate (share results). Audit trail for compliance.
2. **What is a feature store?** Centralized repository for ML features. Stores feature definitions and values. Serves features for both training (offline, batch) and inference (online, real-time). Ensures consistency: same feature logic for training and serving.
3. **What is MLflow's model registry?** Centralized model versioning and lifecycle management. Stages: None → Staging → Production → Archived. Track which model version is in production. Provides model loading by name+stage. Enables controlled deployments.

### Intermediate
4. **Explain point-in-time correctness.** When creating training data, features must reflect what was known at prediction time. Use `merge_asof` (backward direction) to join features from before the event timestamp. Prevents data leakage from using future information. Feature stores handle this automatically.
5. **How do online and offline feature stores differ?** Offline: data warehouse (Parquet, BigQuery), batch access, seconds latency, for training. Online: key-value store (Redis, DynamoDB), point lookups by entity ID, <10ms latency, for serving. Materialization syncs offline→online. Both must return same values for same entity+time.
6. **When would you choose W&B over MLflow?** W&B: better UI/visualizations, built-in hyperparameter sweeps, stronger collaboration, hosted (no infrastructure). MLflow: fully open source, self-hosted (data stays internal), model registry built-in, works with any ML framework. Use W&B for research/experimentation, MLflow for production deployments.

### Advanced
7. **Design a feature store for a ride-sharing platform.** Entities: driver, rider, trip. Offline features (daily batch): driver_avg_rating, rider_total_trips, driver_acceptance_rate. Real-time features (streaming): driver_trips_last_hour, surge_multiplier, driver_distance_to_pickup. Architecture: Spark batch → BigQuery (offline) → Redis (online). Kafka + Flink → Redis (streaming features).
8. **How do you handle feature drift?** Monitor feature distributions over time (KL divergence, PSI). Alert when distributions shift significantly. Investigate: is it data quality issue or genuine change? If genuine: retrain model on recent data. Feature store provides centralized monitoring point.
9. **Design a reproducible ML experiment system.** Version everything: code (Git), data (DVC), features (feature store), environment (Docker), config (YAML). MLflow tracks: params, metrics, artifacts, git hash, environment. Pipeline: git checkout + dvc pull + docker run → exact reproduction. Automated testing: reproduce top experiments nightly.

---

## Hands-On Exercise
1. Set up MLflow tracking server, log 3 experiments with different params
2. Register best model in MLflow Model Registry, transition to Production
3. Set up W&B, run hyperparameter sweep (10 configs)
4. Implement a simple feature store with Feast (3 features, online + offline)
5. Demonstrate point-in-time join vs naive join (show leakage effect)
6. Build a daily feature computation pipeline (mock Airflow)
