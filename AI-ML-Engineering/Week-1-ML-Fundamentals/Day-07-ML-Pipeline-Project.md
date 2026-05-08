# Day 7: Project — End-to-End ML Pipeline

## Learning Objectives
- Build a complete ML pipeline from EDA to deployment
- Use sklearn ColumnTransformer for preprocessing
- Compare multiple algorithms and select the best
- Tune hyperparameters with Optuna
- Serialize model and create a simple serving API

---

## 1. Problem Definition & EDA

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split

# Load dataset (example: customer churn prediction)
df = pd.read_csv('customer_churn.csv')

# --- Exploratory Data Analysis ---
print(f"Shape: {df.shape}")
print(f"\nTarget distribution:\n{df['churn'].value_counts(normalize=True)}")
print(f"\nMissing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
print(f"\nData types:\n{df.dtypes.value_counts()}")

# Identify feature types
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
target = 'churn'
numeric_cols.remove(target) if target in numeric_cols else None

print(f"\nNumeric features ({len(numeric_cols)}): {numeric_cols}")
print(f"Categorical features ({len(categorical_cols)}): {categorical_cols}")

# --- Visualizations ---
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Target distribution
df[target].value_counts().plot(kind='bar', ax=axes[0, 0], title='Target Distribution')

# Numeric distributions
for i, col in enumerate(numeric_cols[:5]):
    ax = axes.flatten()[i + 1]
    df[col].hist(ax=ax, bins=30)
    ax.set_title(col)

plt.tight_layout()
plt.show()

# Correlation heatmap
plt.figure(figsize=(10, 8))
corr = df[numeric_cols + [target]].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0)
plt.title('Feature Correlations')
plt.show()

# Split data (stratified for imbalanced target)
X = df.drop(columns=[target, 'customer_id'])  # Remove ID column
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)
print(f"Train: {X_train.shape}, Test: {X_test.shape}")
```

---

## 2. Feature Engineering Pipeline

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Define feature types
numeric_features = ['tenure', 'monthly_charges', 'total_charges', 'age']
categorical_features = ['gender', 'contract_type', 'payment_method', 'internet_service']

# Numeric pipeline: impute → scale
numeric_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler()),
])

# Categorical pipeline: impute → one-hot
categorical_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False)),
])

# Combine into ColumnTransformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features),
    ],
    remainder='drop',  # Drop columns not in either list
)

# Test preprocessing
X_processed = preprocessor.fit_transform(X_train)
print(f"Processed shape: {X_processed.shape}")

# Get feature names after transformation
feature_names = (
    numeric_features + 
    list(preprocessor.named_transformers_['cat']
         .named_steps['encoder']
         .get_feature_names_out(categorical_features))
)
print(f"Feature names: {feature_names[:10]}...")
```

---

## 3. Model Selection (Compare 3+ Algorithms)

```python
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, roc_auc_score
import time

# Define models to compare
models = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'XGBoost': XGBClassifier(n_estimators=100, random_state=42, verbosity=0),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
    'KNN': KNeighborsClassifier(n_neighbors=5),
}

# Compare with cross-validation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
results = []

for name, model in models.items():
    # Create full pipeline
    pipe = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', model),
    ])
    
    start = time.time()
    scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring='roc_auc')
    elapsed = time.time() - start
    
    results.append({
        'model': name,
        'auc_mean': scores.mean(),
        'auc_std': scores.std(),
        'time_seconds': elapsed,
    })
    print(f"{name:25s} AUC: {scores.mean():.4f} ± {scores.std():.4f} ({elapsed:.1f}s)")

# Results table
results_df = pd.DataFrame(results).sort_values('auc_mean', ascending=False)
print(f"\n{'='*60}")
print(results_df.to_string(index=False))
```

---

## 4. Hyperparameter Tuning (Optuna)

```python
import optuna
from sklearn.model_selection import cross_val_score

# Tune the best model (e.g., XGBoost)
def objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 500),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 1e-4, 10, log=True),
        'reg_lambda': trial.suggest_float('reg_lambda', 1e-4, 10, log=True),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
    }
    
    model = XGBClassifier(**params, random_state=42, verbosity=0, n_jobs=-1)
    
    pipe = Pipeline([
        ('preprocessor', preprocessor),
        ('classifier', model),
    ])
    
    scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring='roc_auc')
    return scores.mean()

# Run optimization
study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=100, show_progress_bar=True)

print(f"\nBest AUC: {study.best_value:.4f}")
print(f"Best params: {study.best_params}")

# Feature importance from best trial
best_params = study.best_params
best_model = XGBClassifier(**best_params, random_state=42, verbosity=0)
final_pipe = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', best_model),
])
final_pipe.fit(X_train, y_train)
```

---

## 5. Final Evaluation

```python
from sklearn.metrics import (
    classification_report, roc_auc_score, roc_curve,
    precision_recall_curve, confusion_matrix, ConfusionMatrixDisplay
)

# Predict on test set
y_pred = final_pipe.predict(X_test)
y_proba = final_pipe.predict_proba(X_test)[:, 1]

# Classification report
print("Classification Report:")
print(classification_report(y_test, y_pred))
print(f"AUC-ROC: {roc_auc_score(y_test, y_proba):.4f}")

# Confusion matrix
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

ConfusionMatrixDisplay.from_predictions(y_test, y_pred, ax=axes[0])
axes[0].set_title('Confusion Matrix')

# ROC Curve
fpr, tpr, _ = roc_curve(y_test, y_proba)
axes[1].plot(fpr, tpr, label=f'AUC={roc_auc_score(y_test, y_proba):.3f}')
axes[1].plot([0, 1], [0, 1], 'k--')
axes[1].set_xlabel('FPR'); axes[1].set_ylabel('TPR')
axes[1].set_title('ROC Curve'); axes[1].legend()

# Precision-Recall Curve
prec, rec, _ = precision_recall_curve(y_test, y_proba)
axes[2].plot(rec, prec)
axes[2].set_xlabel('Recall'); axes[2].set_ylabel('Precision')
axes[2].set_title('Precision-Recall Curve')

plt.tight_layout()
plt.show()

# Feature importance
importances = final_pipe.named_steps['classifier'].feature_importances_
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': importances,
}).sort_values('importance', ascending=False).head(15)

plt.figure(figsize=(10, 6))
plt.barh(importance_df['feature'], importance_df['importance'])
plt.xlabel('Importance')
plt.title('Top 15 Feature Importances')
plt.gca().invert_yaxis()
plt.show()
```

---

## 6. Model Serialization & Simple API

```python
import joblib
from pathlib import Path

# --- Save model ---
model_dir = Path('models')
model_dir.mkdir(exist_ok=True)

joblib.dump(final_pipe, model_dir / 'churn_model_v1.pkl')
print(f"Model saved: {model_dir / 'churn_model_v1.pkl'}")

# --- Load and verify ---
loaded_model = joblib.load(model_dir / 'churn_model_v1.pkl')
test_pred = loaded_model.predict_proba(X_test[:5])[:, 1]
print(f"Verification predictions: {test_pred}")

# --- Simple FastAPI serving ---
# api.py
"""
from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI()
model = joblib.load('models/churn_model_v1.pkl')

class CustomerFeatures(BaseModel):
    tenure: float
    monthly_charges: float
    total_charges: float
    age: float
    gender: str
    contract_type: str
    payment_method: str
    internet_service: str

@app.post('/predict')
def predict_churn(features: CustomerFeatures):
    df = pd.DataFrame([features.model_dump()])
    proba = model.predict_proba(df)[0, 1]
    return {
        'churn_probability': round(float(proba), 4),
        'prediction': 'churn' if proba > 0.5 else 'stay',
        'confidence': round(float(max(proba, 1-proba)), 4),
    }

@app.get('/health')
def health():
    return {'status': 'healthy', 'model_version': 'v1'}
"""

# Run with: uvicorn api:app --reload
# Test with: curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
#   -d '{"tenure": 24, "monthly_charges": 65.5, ...}'
```

---

## 7. Project Report Template

```markdown
# Customer Churn Prediction — Project Report

## 1. Problem Statement
Predict customer churn (binary classification) to enable proactive retention.
Business goal: Identify at-risk customers 30 days before churn.

## 2. Data Summary
- Records: 7,043 customers
- Features: 20 (13 numeric, 7 categorical)
- Target: 26.5% churn rate (imbalanced)
- Missing values: 2.5% in total_charges (imputed with median)

## 3. Feature Engineering
- Computed: tenure_months / monthly_charges ratio
- Encoded: one-hot for categoricals
- Scaled: StandardScaler for numerics

## 4. Model Comparison
| Model | AUC-ROC (CV) | Training Time |
|-------|--------------|---------------|
| XGBoost | 0.847 ± 0.012 | 3.2s |
| Random Forest | 0.831 ± 0.015 | 2.1s |
| Logistic Reg | 0.809 ± 0.010 | 0.3s |

## 5. Best Model: Tuned XGBoost
- Test AUC-ROC: 0.852
- Precision: 0.72, Recall: 0.68, F1: 0.70 (at threshold 0.5)
- Optimal threshold (cost-based): 0.35 → Recall: 0.82

## 6. Key Insights
- Top predictors: contract_type, tenure, monthly_charges
- Month-to-month contracts have 3x churn rate vs 2-year
- Customers with tenure < 12 months are highest risk

## 7. Deployment
- Model serialized with joblib (size: 2.3MB)
- FastAPI endpoint for real-time scoring
- Batch scoring via Airflow DAG (daily)

## 8. Next Steps
- A/B test retention offers based on predictions
- Add behavioral features (login frequency, support tickets)
- Monitor model drift monthly
```

---

## Interview Questions

### Beginner
1. **Walk me through your ML project end-to-end.** EDA → define features → split data (stratified) → preprocess (ColumnTransformer) → compare models (CV) → tune best model (Optuna) → evaluate on test set → serialize → serve via API.
2. **Why split into train/test before preprocessing?** Prevent data leakage. If you fit scaler on full data, test statistics leak into training. Always: fit on train, transform both train and test.
3. **How do you handle categorical variables in sklearn?** ColumnTransformer with OneHotEncoder for categoricals and StandardScaler for numerics. `handle_unknown='ignore'` for unseen categories at test time.

### Intermediate
4. **How do you select the best model?** Compare multiple algorithms using cross-validation (same folds). Primary metric aligned with business goal (AUC for ranking, F1 for balance). Consider: speed, interpretability, complexity. Statistical test for significance.
5. **Why use a Pipeline vs separate steps?** Prevents leakage (preprocessing fit only on train fold during CV). Reproducible (one object contains everything). Easy to serialize and deploy. Easy to swap components.
6. **How do you know if your model is overfitting?** Train score >> test score. Gap increases with model complexity. Fix: regularization, reduce complexity, more data, early stopping, cross-validation for reliable estimate.

### Advanced
7. **How do you take an ML model to production?** Serialize (joblib/pickle) → API (FastAPI/Flask) → containerize (Docker) → deploy (Kubernetes/Lambda) → monitor (drift detection, performance) → retrain schedule. Also: A/B testing, feature store, CI/CD for models.
8. **How do you handle model updates in production?** Shadow mode (new model runs alongside, compare) → canary deployment (small traffic %) → full rollout. Rollback plan. Version models. Track performance metrics. Automated retraining with guardrails.
9. **Design an ML system for a real-time recommendation engine.** Offline: train model daily on interaction data. Feature store: batch (user profiles) + real-time (recent clicks). Serving: pre-compute top-N per user (Redis), or real-time inference for personalization. Evaluate: offline (NDCG) + online (A/B on CTR).

---

## Hands-On Exercise
1. Complete EDA on a real dataset (visualize distributions, correlations, missing data)
2. Build ColumnTransformer pipeline handling numeric + categorical features
3. Compare 5+ models with cross-validation, create results table
4. Tune best model with Optuna (50+ trials)
5. Evaluate final model: metrics, curves, confusion matrix
6. Serialize model and create a working FastAPI endpoint
7. Write a 1-page project report summarizing findings
