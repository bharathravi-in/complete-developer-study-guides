# Day 30: Capstone & Interview

## Learning Objectives
- Build a complete ML system: data → training → serving → monitoring
- Integrate MLflow experiment tracking
- Containerize with Docker
- Create monitoring dashboard
- Practice explaining system design decisions

---

## 1. Capstone Project: End-to-End ML System

```
Project: Customer Churn Prediction System

Components:
1. Data Pipeline: Load, validate, feature engineer
2. Training: Experiment with models, track with MLflow
3. Serving: FastAPI endpoint with Docker
4. Monitoring: Drift detection + performance tracking
5. CI/CD: Automated retraining trigger
```

---

## 2. Data Pipeline

```python
# src/data_pipeline.py
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from datetime import datetime

class DataPipeline:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.reference_stats = {}
    
    def load_and_validate(self) -> pd.DataFrame:
        df = pd.read_csv(self.data_path)
        
        # Validation
        assert df.shape[0] > 100, "Too few samples"
        assert "target" in df.columns, "Missing target column"
        null_pct = df.isnull().sum().sum() / df.size
        assert null_pct < 0.05, f"Too many nulls: {null_pct:.1%}"
        
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features for churn prediction."""
        features = pd.DataFrame()
        
        features["tenure_months"] = df["tenure"]
        features["monthly_charges"] = df["monthly_charges"]
        features["total_charges"] = df["total_charges"]
        features["contract_type"] = df["contract"].map(
            {"Month-to-month": 0, "One year": 1, "Two year": 2}
        )
        features["num_services"] = df[["phone", "internet", "streaming"]].sum(axis=1)
        features["charge_per_month_ratio"] = df["total_charges"] / (df["tenure"] + 1)
        features["has_support"] = df["tech_support"].astype(int)
        
        return features
    
    def prepare(self) -> tuple:
        df = self.load_and_validate()
        X = self.engineer_features(df)
        y = df["target"]
        
        # Save reference statistics for monitoring
        self.reference_stats = {col: X[col].describe().to_dict() for col in X.columns}
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
        return X_train, X_test, y_train, y_test
```

---

## 3. Training with MLflow

```python
# src/train.py
import mlflow
import mlflow.sklearn
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
import json

class Trainer:
    def __init__(self, experiment_name: str = "churn-prediction"):
        mlflow.set_experiment(experiment_name)
    
    def train_and_log(self, X_train, X_test, y_train, y_test, model_type: str = "gbt"):
        with mlflow.start_run(run_name=f"{model_type}-{datetime.now().strftime('%Y%m%d')}"):
            # Select model
            if model_type == "gbt":
                params = {"n_estimators": 200, "max_depth": 5, "learning_rate": 0.1}
                model = GradientBoostingClassifier(**params)
            elif model_type == "logistic":
                params = {"C": 1.0, "max_iter": 1000}
                model = LogisticRegression(**params)
            
            # Log params
            mlflow.log_params(params)
            mlflow.log_param("model_type", model_type)
            mlflow.log_param("train_size", len(X_train))
            
            # Train
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1]
            
            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "f1": f1_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred),
                "recall": recall_score(y_test, y_pred),
                "roc_auc": roc_auc_score(y_test, y_prob),
            }
            mlflow.log_metrics(metrics)
            
            # Log model
            mlflow.sklearn.log_model(model, "model")
            
            # Log metrics as artifact
            with open("metrics.json", "w") as f:
                json.dump(metrics, f, indent=2)
            mlflow.log_artifact("metrics.json")
            
            print(f"Model: {model_type} | F1: {metrics['f1']:.4f} | AUC: {metrics['roc_auc']:.4f}")
            return model, metrics

# Run experiments
trainer = Trainer()
pipeline = DataPipeline("data/churn.csv")
X_train, X_test, y_train, y_test = pipeline.prepare()

# Compare models
gbt_model, gbt_metrics = trainer.train_and_log(X_train, X_test, y_train, y_test, "gbt")
lr_model, lr_metrics = trainer.train_and_log(X_train, X_test, y_train, y_test, "logistic")

# Register best model
best_model = gbt_model if gbt_metrics["f1"] > lr_metrics["f1"] else lr_model
mlflow.sklearn.log_model(best_model, "best_model", registered_model_name="churn-predictor")
```

---

## 4. Docker Containerized Serving

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY models/ models/

EXPOSE 8000

CMD ["uvicorn", "src.serve:app", "--host", "0.0.0.0", "--port", "8000"]
```

```python
# src/serve.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import numpy as np
import time

app = FastAPI(title="Churn Prediction API")
model = None

@app.on_event("startup")
def load():
    global model
    model = joblib.load("models/churn_model.pkl")

class PredictionRequest(BaseModel):
    tenure_months: float
    monthly_charges: float
    total_charges: float
    contract_type: int
    num_services: int
    charge_per_month_ratio: float
    has_support: int

class PredictionResponse(BaseModel):
    churn_probability: float
    will_churn: bool
    latency_ms: float

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    start = time.time()
    
    features = np.array([[
        request.tenure_months, request.monthly_charges,
        request.total_charges, request.contract_type,
        request.num_services, request.charge_per_month_ratio,
        request.has_support,
    ]])
    
    probability = model.predict_proba(features)[0][1]
    
    return PredictionResponse(
        churn_probability=round(float(probability), 4),
        will_churn=probability > 0.5,
        latency_ms=round((time.time() - start) * 1000, 2),
    )

@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}
```

```bash
# Build and run
docker build -t churn-predictor .
docker run -p 8000:8000 churn-predictor

# Test
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"tenure_months": 12, "monthly_charges": 70, "total_charges": 840, "contract_type": 0, "num_services": 3, "charge_per_month_ratio": 70, "has_support": 0}'
```

---

## 5. Monitoring Dashboard

```python
# src/monitor.py
from scipy import stats
import numpy as np
import json
from datetime import datetime

class ProductionMonitor:
    def __init__(self, reference_path: str = "data/reference_stats.json"):
        with open(reference_path) as f:
            self.reference = json.load(f)
        self.predictions_log = []
    
    def log_prediction(self, features: dict, prediction: float):
        self.predictions_log.append({
            "timestamp": datetime.now().isoformat(),
            "features": features,
            "prediction": prediction,
        })
    
    def check_drift(self, recent_data: dict[str, list]) -> dict:
        """Check all features for drift."""
        results = {}
        for feature, values in recent_data.items():
            ref_mean = self.reference[feature]["mean"]
            ref_std = self.reference[feature]["std"]
            
            current_mean = np.mean(values)
            z_score = abs(current_mean - ref_mean) / (ref_std + 1e-8)
            
            results[feature] = {
                "reference_mean": ref_mean,
                "current_mean": current_mean,
                "z_score": round(z_score, 2),
                "drift_detected": z_score > 3,
            }
        return results
    
    def prediction_distribution_check(self) -> dict:
        """Check if prediction distribution has shifted."""
        recent_preds = [p["prediction"] for p in self.predictions_log[-1000:]]
        
        return {
            "mean_prediction": np.mean(recent_preds),
            "std_prediction": np.std(recent_preds),
            "churn_rate": np.mean([p > 0.5 for p in recent_preds]),
            "high_confidence_rate": np.mean([p > 0.9 or p < 0.1 for p in recent_preds]),
        }
    
    def generate_report(self, recent_data: dict) -> dict:
        drift = self.check_drift(recent_data)
        pred_dist = self.prediction_distribution_check()
        
        drifted = [f for f, r in drift.items() if r["drift_detected"]]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_predictions": len(self.predictions_log),
            "drift_summary": {
                "features_checked": len(drift),
                "features_drifted": len(drifted),
                "drifted_features": drifted,
            },
            "prediction_distribution": pred_dist,
            "action_needed": len(drifted) > 2 or pred_dist["churn_rate"] > 0.4,
        }
```

---

## 6. System Design Document

```markdown
# Churn Prediction System — Design Document

## Overview
Predict customer churn to enable proactive retention interventions.

## Architecture
```
Data Source → Data Pipeline → Feature Store → Training (MLflow)
                                    ↓
User Request → API (FastAPI) → Model → Response
                                    ↓
                            Monitoring → Alerts → Retraining
```

## Key Decisions & Justifications

### Why GBT over Deep Learning?
- Tabular data: GBT typically outperforms neural nets
- Interpretable: feature importances for business stakeholders  
- Fast inference: <5ms per prediction
- Small dataset: 10K rows insufficient for deep learning

### Why FastAPI over batch predictions?
- Real-time: predict at point of customer interaction
- Integration: support team sees risk score during call
- Freshness: uses latest features (not stale daily batch)

### Why Docker over serverless?
- Cold start: serverless adds 2-5s latency (unacceptable)
- Model size: 50MB model loads once at container start
- Predictable latency: consistent <10ms inference

### Monitoring Strategy
- Feature drift: PSI weekly on all features
- Performance: track actual churn vs predicted (30-day delay)
- Retrain trigger: drift in >3 features OR accuracy drop >5%

### Scaling Plan
- Current: single container, 100 QPS capacity
- Next: Kubernetes, 3 replicas, auto-scale on CPU
- Future: feature store (Redis), A/B testing, model ensemble
```

---

## 7. Interview Practice

```
Common System Design Interview Questions:

1. "Walk me through your ML system"
   - Start with problem definition and business impact
   - Describe data sources and feature engineering
   - Explain model choice and why (tradeoffs)
   - Cover serving architecture and latency
   - Discuss monitoring and iteration plan

2. "What would you do differently?"
   - Always have improvement ideas ready
   - "Given more time/data, I would..."
   - Show awareness of limitations

3. "How does it handle failures?"
   - Model failure: fallback to rules/previous version
   - Data pipeline failure: stale features detection
   - Inference timeout: cached responses / degraded mode
   - Data drift: automated alerts → investigation → retrain

4. "How would you scale this 100x?"
   - Horizontal: more replicas, load balancing
   - Feature store: pre-compute, cache hot features
   - Model: distill to smaller model, quantize
   - Data: streaming pipeline for real-time features
   - Infrastructure: Kubernetes auto-scaling

5. "How do you validate this works?"
   - Offline: test set metrics (F1, AUC)
   - Shadow mode: compare with production system
   - A/B test: 5% traffic for 2 weeks
   - Business metrics: retention rate improvement
```

---

## Interview Questions

### Beginner
1. **What are the essential components of a production ML system?** Data pipeline (ingestion, validation, features), training pipeline (model selection, hyperparameter tuning, evaluation), serving (API endpoint, latency optimization), monitoring (drift detection, performance tracking), and CI/CD (automated testing, retraining).
2. **Why use Docker for ML serving?** Reproducible environment (same OS, libraries, model). Fast startup (model pre-loaded). Easy deployment (same container anywhere). Isolation (no dependency conflicts). Scalable (orchestrate with Kubernetes).
3. **What should a model health check include?** Model loaded successfully, inference works (test prediction), latency within SLA, memory usage within limits, feature store connection healthy, recent predictions look reasonable (distribution check).

### Intermediate
4. **How do you decide when to retrain?** Monitor: performance metrics (if labels available), data drift (PSI/KS on features), prediction distribution shift. Triggers: scheduled (monthly baseline), performance drop (>5% degradation), significant drift (>3 features). Always validate before deploying retrained model.
5. **Explain the end-to-end workflow from data to deployment.** Data collection → validation → feature engineering → train/eval (MLflow) → model selection → validation gates → containerize (Docker) → deploy (K8s) → monitor (drift + performance) → retrain when needed. Each step has tests and quality checks.
6. **How do you handle model rollback?** Keep previous N versions deployed (inactive). Monitor new deployment closely (first 24h). Auto-rollback: if error rate spikes or metrics drop. Manual rollback: instant traffic switch via load balancer. Blue-green deployment: switch between two environments.

### Advanced
7. **Design a complete ML platform for a 50-person ML team.** Feature store (Feast + Redis), experiment tracking (MLflow), training infra (Kubernetes + GPU nodes), model registry (MLflow), CI/CD (GitHub Actions + DVC), serving (Triton + K8s), monitoring (Evidently + Grafana). Self-service: templates for new projects, shared features, common monitoring.
8. **How do you measure business impact of ML?** A/B test: ML-enabled vs control group. Measure business KPIs: revenue, retention, engagement (not just model accuracy). Attribution: causal inference for features that affect business. Track: model metric improvement → business metric improvement correlation. Report to stakeholders in business terms.
9. **What are the biggest challenges in productionizing ML?** Data quality (garbage in → garbage out), training-serving skew (different feature computation), concept drift (world changes), debugging (why did model make that prediction?), team coordination (data eng + ML + platform), tech debt (models require ongoing maintenance unlike regular code).

---

## Hands-On Exercise
1. Build the complete capstone project (data → train → serve → monitor)
2. Track 3+ experiments in MLflow, register the best model
3. Containerize the serving endpoint, test with curl
4. Implement drift monitoring on synthetic production data
5. Write a 1-page system design document justifying your decisions
6. Practice explaining your system (2-minute walkthrough, record yourself)
7. Identify 3 failure modes and implement fallback strategies
