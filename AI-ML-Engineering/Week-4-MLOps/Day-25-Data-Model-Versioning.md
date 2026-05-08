# Day 25: Data & Model Versioning

## Learning Objectives
- Use DVC for data and pipeline versioning
- Implement Git + DVC workflows for ML projects
- Version models and datasets effectively
- Achieve full reproducibility (code + data + environment)
- Manage artifacts with remote storage

---

## 1. DVC (Data Version Control)

```bash
# DVC: Git for data. Track large files without storing them in Git.
# Git tracks metadata (.dvc files), DVC tracks actual data in remote storage.

# Initialize DVC in a Git repo
pip install dvc[s3]  # Install with S3 support
git init
dvc init

# Track a large dataset
dvc add data/training_data.parquet
# Creates: data/training_data.parquet.dvc (metadata, tracked by Git)
# Creates: .gitignore entry (actual data NOT in Git)

git add data/training_data.parquet.dvc data/.gitignore
git commit -m "Track training data v1"

# Configure remote storage (S3, GCS, Azure, local)
dvc remote add -d myremote s3://my-bucket/dvc-storage
dvc push  # Upload data to remote

# When someone clones the repo:
git clone <repo-url>
dvc pull  # Downloads data from remote storage

# Version data: just modify and re-add
# (update training_data.parquet with new data)
dvc add data/training_data.parquet
git add data/training_data.parquet.dvc
git commit -m "Training data v2: added January 2025 data"
dvc push

# Switch between data versions:
git checkout v1.0  # Checkout old code
dvc checkout       # Downloads corresponding data version
```

---

## 2. DVC Pipelines

```yaml
# dvc.yaml — Define reproducible ML pipeline stages
stages:
  preprocess:
    cmd: python src/preprocess.py
    deps:
      - src/preprocess.py
      - data/raw/
    outs:
      - data/processed/train.parquet
      - data/processed/test.parquet
    params:
      - preprocess.test_size
      - preprocess.random_state

  train:
    cmd: python src/train.py
    deps:
      - src/train.py
      - data/processed/train.parquet
    outs:
      - models/model.pkl
    params:
      - train.n_estimators
      - train.max_depth
      - train.learning_rate
    metrics:
      - metrics/train_metrics.json:
          cache: false

  evaluate:
    cmd: python src/evaluate.py
    deps:
      - src/evaluate.py
      - models/model.pkl
      - data/processed/test.parquet
    metrics:
      - metrics/eval_metrics.json:
          cache: false
    plots:
      - metrics/confusion_matrix.csv:
          x: predicted
          y: actual
```

```yaml
# params.yaml — Centralized parameters
preprocess:
  test_size: 0.2
  random_state: 42

train:
  n_estimators: 100
  max_depth: 10
  learning_rate: 0.01
```

```bash
# Run the full pipeline
dvc repro

# Only re-runs stages whose dependencies changed
# If only train params changed → skips preprocess, runs train + evaluate

# Compare metrics across experiments
dvc metrics show
dvc metrics diff  # Compare current vs previous commit

# Compare parameters
dvc params diff

# Visualize pipeline DAG
dvc dag
```

---

## 3. Git + DVC Workflow

```bash
# Typical ML development workflow:

# 1. Create feature branch
git checkout -b experiment/larger-model

# 2. Modify parameters
# Edit params.yaml: train.n_estimators: 100 → 500

# 3. Run pipeline
dvc repro

# 4. Check results
dvc metrics show
# metrics/eval_metrics.json:
#   accuracy: 0.94
#   f1_score: 0.91

# 5. Compare with main branch
dvc metrics diff main
# Path                      Metric    Old     New     Change
# metrics/eval_metrics.json accuracy  0.92    0.94    0.02

# 6. Commit and push
git add dvc.lock params.yaml metrics/
git commit -m "Experiment: larger model (n=500), +2% accuracy"
dvc push  # Push data/model artifacts

# 7. Merge if improved
git checkout main
git merge experiment/larger-model

# Key: Git manages code + params + metrics, DVC manages data + models
```

---

## 4. Model Versioning Strategies

```python
# Strategy 1: DVC-based (simple, file-level)
# Each model is a file tracked by DVC
# Version via Git commits/tags
# dvc add models/fraud_detector.pkl
# git tag model-v2.1

# Strategy 2: MLflow Model Registry (recommended for production)
import mlflow

# Log model during training
with mlflow.start_run():
    mlflow.sklearn.log_model(model, "model", registered_model_name="fraud-detector")
    # Automatically creates new version

# Promote to production
client = mlflow.MlflowClient()
client.transition_model_version_stage("fraud-detector", version=5, stage="Production")

# Strategy 3: Custom versioning with metadata
import json
from datetime import datetime

def save_model_with_metadata(model, path: str, metrics: dict, params: dict):
    """Save model with full provenance metadata."""
    import joblib
    
    # Save model
    joblib.dump(model, f"{path}/model.pkl")
    
    # Save metadata
    metadata = {
        "version": "2.1.0",
        "created_at": datetime.now().isoformat(),
        "git_hash": get_git_hash(),
        "data_version": get_dvc_data_hash(),
        "metrics": metrics,
        "parameters": params,
        "python_version": sys.version,
        "dependencies": get_pip_freeze(),
    }
    
    with open(f"{path}/metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

# Strategy 4: Semantic versioning for models
# MAJOR.MINOR.PATCH
# MAJOR: breaking changes (different features, incompatible API)
# MINOR: improved accuracy, new capability (backward compatible)
# PATCH: bug fixes, retraining on same architecture
```

---

## 5. Dataset Versioning

```python
# Option 1: DVC (file-based, works with any format)
# dvc add data/dataset_v3.parquet
# Simple but limited metadata

# Option 2: Delta Lake (versioned data lake, time travel)
from delta import DeltaTable
import pyspark.sql.functions as F

# Write with versioning (automatic)
df.write.format("delta").mode("append").save("/data/features")

# Time travel: read data as it was at a specific version/timestamp
df_v2 = spark.read.format("delta").option("versionAsOf", 2).load("/data/features")
df_yesterday = spark.read.format("delta").option("timestampAsOf", "2025-01-15").load("/data/features")

# See history
delta_table = DeltaTable.forPath(spark, "/data/features")
delta_table.history().show()

# Option 3: LakeFS (Git-like branching for data lakes)
# Branch data, experiment, merge back
# lakectl branch create lakefs://repo/experiment-1 -s lakefs://repo/main
# Perfect for: "what if I add this data?" experiments

# Option 4: Hugging Face Datasets (for public/shared datasets)
from datasets import load_dataset
ds = load_dataset("my-org/my-dataset", revision="v2.0")
```

---

## 6. Reproducibility: Code + Data + Environment

```dockerfile
# Full reproducibility requires versioning ALL of:
# 1. Code (Git) 
# 2. Data (DVC)
# 3. Environment (Docker)
# 4. Configuration (params.yaml in Git)

# Dockerfile for ML environment
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Python dependencies (pinned versions!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY src/ src/
COPY params.yaml .
COPY dvc.yaml .
COPY dvc.lock .

# Pull data and run
# CMD ["dvc", "repro"]
```

```txt
# requirements.txt — PIN ALL VERSIONS
scikit-learn==1.4.0
pandas==2.2.0
numpy==1.26.3
mlflow==2.10.0
dvc[s3]==3.40.0
```

```bash
# Reproduce ANY past experiment:
git checkout <commit-hash>     # Get exact code + params + DVC metadata
docker build -t ml-exp .       # Get exact environment
docker run ml-exp dvc repro    # Run with exact data (pulled by DVC)

# Result: byte-for-byte identical output (if random seeds set)
```

---

## 7. Artifact Management

```python
# Artifacts: models, datasets, plots, configs — anything produced by ML pipeline

# S3-based artifact storage (most common)
import boto3

class ArtifactStore:
    def __init__(self, bucket: str, prefix: str = "artifacts"):
        self.s3 = boto3.client("s3")
        self.bucket = bucket
        self.prefix = prefix
    
    def save(self, local_path: str, artifact_name: str, version: str):
        key = f"{self.prefix}/{artifact_name}/{version}/{os.path.basename(local_path)}"
        self.s3.upload_file(local_path, self.bucket, key)
        return f"s3://{self.bucket}/{key}"
    
    def load(self, artifact_name: str, version: str, local_path: str):
        key = f"{self.prefix}/{artifact_name}/{version}/"
        # Download all files for this artifact version
        paginator = self.s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=self.bucket, Prefix=key):
            for obj in page.get('Contents', []):
                filename = obj['Key'].split('/')[-1]
                self.s3.download_file(self.bucket, obj['Key'], f"{local_path}/{filename}")

# MLflow artifact logging (integrates with experiment tracking)
with mlflow.start_run():
    mlflow.log_artifact("model.pkl")
    mlflow.log_artifact("feature_importance.png")
    mlflow.log_artifact("config.yaml")
    # All artifacts stored together, linked to this run
```

---

## Interview Questions

### Beginner
1. **What is DVC and why use it?** Data Version Control — tracks large data files alongside Git. Git tracks small metadata files (.dvc), DVC stores actual data in remote storage (S3, GCS). Enables: data versioning, pipeline reproducibility, collaboration on ML projects. Like Git-LFS but designed for ML workflows.
2. **Why version datasets?** Track what data was used for each model. Reproduce experiments exactly. Roll back if data quality degrades. Compare model performance across data versions. Audit trail for compliance. Detect when data changes cause issues.
3. **What does reproducibility mean in ML?** Same code + same data + same environment → same results. Requires versioning all three. Also: fixed random seeds, pinned library versions, deterministic algorithms. Important for: debugging, auditing, collaboration, regulatory compliance.

### Intermediate
4. **Explain DVC pipelines and when to use them.** DVC pipelines (dvc.yaml) define stages (preprocess → train → evaluate) with explicit dependencies. `dvc repro` only reruns stages whose inputs changed. Benefits: reproducibility, caching (skip unchanged stages), dependency tracking, collaboration. Use for: any multi-step ML workflow.
5. **Compare DVC vs Delta Lake for versioning.** DVC: file-level versioning, any format, Git-integrated, better for ML pipelines. Delta Lake: row-level versioning, time-travel queries, better for data lakes and analytics. Use DVC for: model files, processed datasets. Use Delta for: feature tables, raw data with frequent updates.
6. **How do you ensure environment reproducibility?** Pin all dependency versions (requirements.txt/poetry.lock). Use Docker for system-level reproducibility. Track Python version. Store Dockerfile in Git. For GPU: pin CUDA version. Test: build container from scratch and verify identical results.

### Advanced
7. **Design a versioning system for a team of 10 ML engineers.** Git for code (feature branches, PRs). DVC for data/models (shared S3 remote). MLflow for experiment tracking and model registry. Docker for environments. Convention: semantic versioning for models, branch-per-experiment. CI: auto-run pipeline on PR, compare metrics. Model promotion: requires review + metric thresholds.
8. **How do you handle large-scale data versioning (PB-scale)?** DVC unsuitable at PB scale (file-level). Use: Delta Lake (efficient row-level versioning), LakeFS (branch entire lakes), Iceberg (table-format time-travel). Combine with partitioning: only version changed partitions. Metadata: track schema + partition changes in Git.
9. **Design a rollback strategy for ML deployments.** Keep previous N model versions deployed (shadow mode). On degradation: instant traffic switch to previous version (load balancer). Data rollback: DVC checkout + retrain or use cached model. Feature rollback: feature store maintains history. Automation: monitoring triggers → auto-rollback if metrics drop below threshold.

---

## Hands-On Exercise
1. Initialize DVC in a Git repo, track a dataset, push to local remote
2. Create a DVC pipeline (preprocess → train → evaluate), run with `dvc repro`
3. Modify parameters, re-run pipeline, compare metrics with `dvc metrics diff`
4. Create 3 data versions, switch between them with `git checkout` + `dvc checkout`
5. Build a Docker environment that reproduces a training run exactly
6. Set up MLflow model registry with 3 model versions and stage transitions
