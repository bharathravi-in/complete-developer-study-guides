# Day 3: Tree-Based Models

## Learning Objectives
- Understand decision tree splitting criteria (entropy, Gini)
- Master Random Forest (bagging + feature randomness)
- Implement XGBoost/LightGBM gradient boosting
- Extract and interpret feature importance
- Tune hyperparameters effectively

---

## 1. Decision Trees

### Splitting Criteria

**Gini Impurity** (used by CART, sklearn default):
$$Gini(S) = 1 - \sum_{i=1}^{C} p_i^2$$

**Entropy / Information Gain** (used by ID3, C4.5):
$$Entropy(S) = -\sum_{i=1}^{C} p_i \log_2(p_i)$$
$$InformationGain = Entropy(parent) - \sum \frac{|child|}{|parent|} Entropy(child)$$

```python
import numpy as np
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Load data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train decision tree
dt = DecisionTreeClassifier(
    criterion='gini',       # 'gini' or 'entropy'
    max_depth=4,            # Limit depth to prevent overfitting
    min_samples_split=5,    # Minimum samples to split a node
    min_samples_leaf=2,     # Minimum samples in leaf
    random_state=42,
)
dt.fit(X_train, y_train)
print(f"Accuracy: {dt.score(X_test, y_test):.4f}")

# Visualize the tree
print(export_text(dt, feature_names=load_iris().feature_names))

# How a tree makes predictions:
# 1. Start at root node
# 2. Check condition (e.g., petal_length <= 2.45)
# 3. Go left (True) or right (False)
# 4. Repeat until leaf node
# 5. Leaf gives prediction (majority class or mean value)
```

### Why Trees Overfit

```python
# Unrestricted tree = memorizes training data
dt_overfit = DecisionTreeClassifier(max_depth=None, min_samples_leaf=1)
dt_overfit.fit(X_train, y_train)
print(f"Train: {dt_overfit.score(X_train, y_train):.4f}")  # ~1.0 (memorized)
print(f"Test:  {dt_overfit.score(X_test, y_test):.4f}")    # Lower (overfitting)

# Solution: Restrict tree OR use ensembles
```

---

## 2. Random Forest (Bagging)

### How It Works
1. Create N bootstrapped samples (sample with replacement)
2. Train a decision tree on each sample
3. At each split, consider only √n_features (randomness)
4. Final prediction = majority vote (classification) or average (regression)

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification

# Generate complex dataset
X, y = make_classification(n_samples=10000, n_features=20, n_informative=10,
                            n_redundant=5, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Random Forest
rf = RandomForestClassifier(
    n_estimators=100,        # Number of trees
    max_depth=10,            # Max depth per tree
    max_features='sqrt',     # Features considered per split
    min_samples_leaf=5,
    n_jobs=-1,               # Parallel training
    random_state=42,
    oob_score=True,          # Out-of-bag estimate (free validation)
)
rf.fit(X_train, y_train)

print(f"Train accuracy: {rf.score(X_train, y_train):.4f}")
print(f"Test accuracy:  {rf.score(X_test, y_test):.4f}")
print(f"OOB score:      {rf.oob_score_:.4f}")

# Random Forest advantages:
# ✅ Reduces variance (averaging many trees)
# ✅ Handles non-linear relationships
# ✅ Robust to outliers
# ✅ Provides feature importance
# ✅ Parallelizable
# ❌ Not as strong as boosting for structured data
# ❌ Large memory footprint
```

---

## 3. Gradient Boosting (XGBoost / LightGBM)

### How Boosting Works
1. Train a weak learner (shallow tree) on the data
2. Compute residuals (errors)
3. Train next tree to predict the residuals
4. Add prediction (with learning rate) to ensemble
5. Repeat

```python
import xgboost as xgb
import lightgbm as lgb

# XGBoost
xgb_model = xgb.XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,      # Shrinkage (smaller = more trees needed but better)
    subsample=0.8,          # Row sampling per tree
    colsample_bytree=0.8,  # Feature sampling per tree
    reg_alpha=0.1,          # L1 regularization
    reg_lambda=1.0,         # L2 regularization
    eval_metric='logloss',
    random_state=42,
    n_jobs=-1,
)
xgb_model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False,
)
print(f"XGBoost accuracy: {xgb_model.score(X_test, y_test):.4f}")

# LightGBM (faster, handles large data)
lgb_model = lgb.LGBMClassifier(
    n_estimators=200,
    max_depth=-1,           # No limit (leaf-wise growth)
    num_leaves=31,          # Key parameter (instead of max_depth)
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=0.1,
    reg_lambda=1.0,
    random_state=42,
    n_jobs=-1,
    verbose=-1,
)
lgb_model.fit(X_train, y_train)
print(f"LightGBM accuracy: {lgb_model.score(X_test, y_test):.4f}")
```

### XGBoost vs LightGBM

| Aspect | XGBoost | LightGBM |
|--------|---------|----------|
| Tree growth | Level-wise (balanced) | Leaf-wise (deeper, faster) |
| Speed | Slower | 2-10x faster |
| Memory | Higher | Lower |
| Categorical | Manual encoding | Native support |
| Large data | Good | Better |
| Small data | Slightly better | Slightly more overfit-prone |

---

## 4. Feature Importance

```python
import pandas as pd
import shap

# Built-in importance (impurity-based)
feature_names = [f"feature_{i}" for i in range(X.shape[1])]
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': rf.feature_importances_,
}).sort_values('importance', ascending=False)
print(importance_df.head(10))

# Permutation importance (more reliable)
from sklearn.inspection import permutation_importance
perm_imp = permutation_importance(rf, X_test, y_test, n_repeats=10, random_state=42)
perm_df = pd.DataFrame({
    'feature': feature_names,
    'importance_mean': perm_imp.importances_mean,
    'importance_std': perm_imp.importances_std,
}).sort_values('importance_mean', ascending=False)
print(perm_df.head(10))

# SHAP values (gold standard for interpretability)
explainer = shap.TreeExplainer(xgb_model)
shap_values = explainer.shap_values(X_test)

# Summary plot (global feature importance + direction)
shap.summary_plot(shap_values, X_test, feature_names=feature_names)

# Single prediction explanation
shap.force_plot(explainer.expected_value, shap_values[0], X_test[0],
                feature_names=feature_names)

# Built-in importance problems:
# - Biased toward high-cardinality features
# - Can be misleading with correlated features
# Solution: Use permutation importance or SHAP
```

---

## 5. Hyperparameter Tuning

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from scipy.stats import randint, uniform
import optuna

# Method 1: Grid Search (exhaustive, good for small spaces)
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7, 10],
    'learning_rate': [0.01, 0.05, 0.1],
}
grid_search = GridSearchCV(
    xgb.XGBClassifier(random_state=42),
    param_grid, cv=5, scoring='accuracy', n_jobs=-1
)
grid_search.fit(X_train, y_train)
print(f"Best params: {grid_search.best_params_}")
print(f"Best score: {grid_search.best_score_:.4f}")

# Method 2: Random Search (better for large spaces)
param_dist = {
    'n_estimators': randint(50, 500),
    'max_depth': randint(3, 15),
    'learning_rate': uniform(0.01, 0.3),
    'subsample': uniform(0.5, 0.5),
    'colsample_bytree': uniform(0.5, 0.5),
}
random_search = RandomizedSearchCV(
    xgb.XGBClassifier(random_state=42),
    param_dist, n_iter=50, cv=5, scoring='accuracy', n_jobs=-1, random_state=42
)
random_search.fit(X_train, y_train)

# Method 3: Optuna (Bayesian optimization — best for efficiency)
def objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 50, 500),
        'max_depth': trial.suggest_int('max_depth', 3, 12),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'subsample': trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 1e-4, 10, log=True),
        'reg_lambda': trial.suggest_float('reg_lambda', 1e-4, 10, log=True),
    }
    
    model = xgb.XGBClassifier(**params, random_state=42, n_jobs=-1)
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
    return scores.mean()

study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=100)
print(f"Best params: {study.best_params}")
print(f"Best accuracy: {study.best_value:.4f}")
```

---

## 6. When to Use What

```
DECISION GUIDE:
───────────────

Small data (<1K rows):
  → Linear models (less overfitting)
  → Decision tree with max_depth

Medium data (1K-100K rows):
  → Random Forest (robust, less tuning)
  → XGBoost/LightGBM (if you tune well)

Large data (>100K rows):
  → LightGBM (fastest)
  → XGBoost (well-tested)
  → Random Forest (if parallelism available)

Tabular/Structured data:
  → Gradient boosting wins almost always (Kaggle dominant)
  → Neural nets rarely beat boosting on tabular data

Interpretability needed:
  → Single decision tree (most interpretable)
  → Linear model + SHAP
  → Random Forest/XGBoost + SHAP

Text/Image/Sequence:
  → Neural networks (trees can't handle raw text/images)
  → Trees work on engineered features from these
```

---

## Interview Questions

### Beginner
1. **How does a decision tree decide where to split?** Tries all features and all thresholds. Picks the split that maximizes information gain (reduces impurity the most). Gini: measures misclassification probability. Entropy: measures disorder.
2. **What is bagging?** Bootstrap Aggregating: train multiple models on different random subsets (with replacement). Average predictions to reduce variance. Random Forest = bagging + random feature selection at each split.
3. **Why does Random Forest reduce overfitting compared to a single tree?** Averaging many decorrelated trees reduces variance. Each tree sees different data (bootstrap) and features (random subset). Errors of individual trees cancel out.

### Intermediate
4. **Explain gradient boosting in simple terms.** Train tree 1 → compute residuals (errors) → train tree 2 on residuals → add tree 2's prediction (scaled by learning rate) → repeat. Each tree corrects the mistakes of all previous trees.
5. **XGBoost vs Random Forest: when to use each?** XGBoost: structured/tabular data, need best accuracy, willing to tune. RF: quick baseline, less tuning required, parallel training, robust to hyperparameters. XGBoost almost always wins on benchmarks with proper tuning.
6. **What's the difference between impurity-based and permutation importance?** Impurity-based: measures split quality improvement. Biased toward high-cardinality features, affected by correlated features. Permutation: measures accuracy drop when feature is shuffled. More reliable but slower to compute.

### Advanced
7. **How does LightGBM's leaf-wise growth differ from XGBoost's level-wise?** Level-wise: grows all leaves at same level (balanced tree). Leaf-wise: grows the leaf with maximum loss reduction (potentially unbalanced but more accurate). Leaf-wise faster but may overfit on small data.
8. **How do you handle data skew/imbalance with tree models?** Options: `scale_pos_weight` (XGBoost), `class_weight='balanced'` (sklearn), SMOTE/undersampling, custom loss function (focal loss), adjusted threshold based on precision-recall curve.
9. **Explain SHAP values and their theoretical foundation.** Based on Shapley values from game theory: fair attribution of prediction to features. SHAP value = average marginal contribution of a feature across all possible coalitions. Satisfies: efficiency, symmetry, null player, additivity. TreeSHAP is O(TLD²) for trees.

---

## Hands-On Exercise
1. Train a decision tree, visualize it, understand the splits
2. Compare single tree vs Random Forest (100 trees) on same data
3. Train XGBoost and LightGBM, compare accuracy and speed
4. Extract SHAP values, create summary and force plots
5. Tune XGBoost with Optuna (100 trials)
6. Build a complete pipeline: preprocessing → tuned XGBoost → evaluation
