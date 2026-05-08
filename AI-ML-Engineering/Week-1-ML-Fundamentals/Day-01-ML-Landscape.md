# Day 1: Machine Learning Landscape & Workflow

## Overview
Understanding the ML ecosystem, types of learning, and the systematic workflow for building ML systems.

---

## 1. What is Machine Learning?

> "A computer program learns from experience E with respect to task T and performance measure P, if its performance at T improves with E." — Tom Mitchell

### ML vs Traditional Programming
```
Traditional: Input + Rules → Output
ML:          Input + Output → Rules (learned from data)
```

---

## 2. Types of Machine Learning

### Supervised Learning
- **Given**: Labeled data (input → known output)
- **Goal**: Learn mapping function f(x) → y
- **Types**:
  - Classification: Predict categories (spam/not spam, disease/healthy)
  - Regression: Predict continuous values (price, temperature)

```python
from sklearn.ensemble import RandomForestClassifier

# Training data has labels
X_train = [[age, income, score], ...]   # Features
y_train = [0, 1, 1, 0, ...]            # Labels (approved/denied)

model = RandomForestClassifier()
model.fit(X_train, y_train)             # Learn the pattern
prediction = model.predict([[35, 75000, 720]])  # Predict new
```

### Unsupervised Learning
- **Given**: Unlabeled data
- **Goal**: Find hidden patterns/structure
- **Types**:
  - Clustering: Group similar items (customer segments)
  - Dimensionality reduction: Compress features (PCA)
  - Anomaly detection: Find outliers (fraud)

### Self-Supervised Learning
- **Given**: Unlabeled data, but create labels from data itself
- **Example**: Masked language modeling (BERT), next-token prediction (GPT)
- Foundation of modern LLMs

### Reinforcement Learning
- **Given**: Environment with rewards/penalties
- **Goal**: Learn policy to maximize cumulative reward
- **Examples**: Game playing, robotics, RLHF for LLMs

---

## 3. The ML Workflow

```
┌────────┐   ┌────────────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐
│Problem │──▶│   Data      │──▶│ Feature  │──▶│  Model   │──▶│  Deploy │
│Define  │   │Collection & │   │Engineer- │   │Training &│   │& Monitor│
│        │   │Exploration  │   │  ing     │   │Evaluation│   │         │
└────────┘   └────────────┘   └──────────┘   └──────────┘   └─────────┘
     │                                              │               │
     └──────────────────── Iterate ─────────────────┘               │
                                                                    │
                           ← Monitor & Retrain ─────────────────────┘
```

### Step 1: Problem Definition
```python
# Key questions:
# - What are we predicting? (target variable)
# - What does success look like? (metric)
# - What data is available?
# - What's the baseline? (simple heuristic)
# - What are the constraints? (latency, fairness, interpretability)

problem = {
    'task': 'Predict customer churn (binary classification)',
    'metric': 'F1 score (balance precision and recall)',
    'baseline': 'Predict most common class → 75% accuracy',
    'target_performance': 'F1 > 0.80',
    'latency_requirement': '< 100ms per prediction',
}
```

### Step 2: Data Collection & Exploration
```python
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load and explore
df = pd.read_csv('customer_data.csv')

# Basic EDA
print(f"Shape: {df.shape}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nTarget distribution:\n{df['churned'].value_counts(normalize=True)}")
print(f"\nMissing values:\n{df.isnull().sum()}")
print(f"\nNumeric summary:\n{df.describe()}")

# Visualize
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
sns.histplot(df['tenure'], ax=axes[0,0])
sns.boxplot(x='churned', y='monthly_charges', data=df, ax=axes[0,1])
sns.heatmap(df.corr(), annot=True, ax=axes[1,0])
sns.countplot(x='churned', data=df, ax=axes[1,1])
plt.tight_layout()
```

### Step 3: Data Splitting
```python
from sklearn.model_selection import train_test_split

# CRITICAL: Split BEFORE any preprocessing
X = df.drop('churned', axis=1)
y = df['churned']

# 60% train, 20% validation, 20% test
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.4, random_state=42, stratify=y)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

print(f"Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")
```

---

## 4. Bias-Variance Trade-off

```
Total Error = Bias² + Variance + Irreducible Noise

High Bias (Underfitting):
├── Model too simple
├── Misses patterns in data
├── High error on BOTH train and val
└── Fix: More features, complex model, less regularization

High Variance (Overfitting):
├── Model too complex
├── Memorizes training data (including noise)
├── Low train error, HIGH val error
└── Fix: More data, regularization, simpler model, dropout
```

```python
from sklearn.model_selection import learning_curve

# Diagnose bias vs variance
train_sizes, train_scores, val_scores = learning_curve(
    model, X_train, y_train, cv=5, 
    train_sizes=[0.1, 0.3, 0.5, 0.7, 1.0]
)

# If train and val scores are both low → High bias
# If train score high but val score low → High variance
# If both converge to high score → Good fit
```

---

## 5. Cross-Validation

```python
from sklearn.model_selection import (
    KFold, StratifiedKFold, TimeSeriesSplit, cross_val_score
)

# K-Fold (standard)
kfold = KFold(n_splits=5, shuffle=True, random_state=42)

# Stratified K-Fold (preserves class distribution — use for classification)
skfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Time Series Split (respects temporal order — use for time data)
tscv = TimeSeriesSplit(n_splits=5)

# Quick evaluation
scores = cross_val_score(model, X_train, y_train, cv=skfold, scoring='f1')
print(f"F1: {scores.mean():.4f} ± {scores.std():.4f}")
```

### Why Cross-Validate?
- Single train/val split is noisy (depends on which data ends up where)
- CV gives reliable estimate of model performance
- Helps detect overfitting to a specific validation set

---

## 6. ML Pipeline with Scikit-learn

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV

# Define feature types
numeric_features = ['age', 'income', 'tenure', 'monthly_charges']
categorical_features = ['gender', 'contract_type', 'payment_method']

# Preprocessing pipelines
numeric_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

categorical_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

# Combine
preprocessor = ColumnTransformer([
    ('num', numeric_transformer, numeric_features),
    ('cat', categorical_transformer, categorical_features)
])

# Full pipeline (preprocessing + model)
pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', GradientBoostingClassifier(random_state=42))
])

# Hyperparameter search
param_grid = {
    'classifier__n_estimators': [100, 200, 500],
    'classifier__max_depth': [3, 5, 7],
    'classifier__learning_rate': [0.01, 0.1, 0.3],
}

grid_search = GridSearchCV(
    pipeline, param_grid, cv=5, scoring='f1', n_jobs=-1, verbose=1
)
grid_search.fit(X_train, y_train)

print(f"Best params: {grid_search.best_params_}")
print(f"Best CV F1: {grid_search.best_score_:.4f}")

# Evaluate on test (only once!)
test_score = grid_search.score(X_test, y_test)
print(f"Test F1: {test_score:.4f}")
```

---

## 7. Common Pitfalls

### Data Leakage
```python
# ❌ BAD: Fit scaler on ALL data (leaks test info into training)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)  # WRONG!
X_train, X_test = train_test_split(X_scaled, ...)

# ✅ GOOD: Fit only on training data
X_train, X_test = train_test_split(X, ...)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # Fit on train
X_test_scaled = scaler.transform(X_test)          # Transform only on test
```

### Target Leakage
```python
# ❌ BAD: Feature that "knows" the target
# e.g., "cancellation_date" as feature when predicting churn
# This feature only exists BECAUSE they churned!

# ✅ GOOD: Only use features available AT PREDICTION TIME
```

### Class Imbalance
```python
from sklearn.utils.class_weight import compute_class_weight
from imblearn.over_sampling import SMOTE

# Option 1: Class weights
weights = compute_class_weight('balanced', classes=[0, 1], y=y_train)
model = RandomForestClassifier(class_weight='balanced')

# Option 2: SMOTE (synthetic oversampling)
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

# Option 3: Adjust threshold
y_proba = model.predict_proba(X_val)[:, 1]
# Instead of 0.5 threshold, optimize for F1
```

---

## 8. Practice Exercises

1. Load the Titanic dataset, perform EDA, build a classification pipeline
2. Diagnose if your model suffers from bias or variance using learning curves
3. Compare 3 models (Logistic Regression, Random Forest, XGBoost) using cross-validation
4. Identify and fix a data leakage scenario

---

## Key Takeaways
- ML workflow: Define → Collect → Engineer → Train → Deploy → Monitor
- Always split data BEFORE preprocessing
- Use stratified K-fold CV for reliable evaluation
- Bias-variance trade-off guides model complexity decisions
- Pipelines prevent data leakage and ensure reproducibility
- Start simple (baseline), then iterate

## Tomorrow
**Day 2**: Linear Models — Regression, classification, gradient descent from scratch, and regularization (L1/L2).
