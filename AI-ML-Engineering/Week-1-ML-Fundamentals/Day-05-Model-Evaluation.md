# Day 5: Model Evaluation

## Learning Objectives
- Master classification metrics (precision, recall, F1, AUC)
- Understand regression metrics (MSE, RMSE, MAE, R²)
- Tune thresholds for business requirements
- Apply calibration and statistical model comparison

---

## 1. Classification Metrics

### Confusion Matrix

```
                    Predicted
                 Positive  Negative
Actual Positive    TP        FN
Actual Negative    FP        TN

Accuracy  = (TP + TN) / (TP + TN + FP + FN)
Precision = TP / (TP + FP)     → "Of predicted positive, how many correct?"
Recall    = TP / (TP + FN)     → "Of actual positive, how many found?"
F1        = 2 × (P × R) / (P + R)  → Harmonic mean of P and R
```

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score,
    precision_recall_curve, roc_curve, average_precision_score
)
import matplotlib.pyplot as plt
import numpy as np

# Basic metrics
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

print(classification_report(y_test, y_pred))
print(f"Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
print(f"Precision: {precision_score(y_test, y_pred):.4f}")
print(f"Recall:    {recall_score(y_test, y_pred):.4f}")
print(f"F1 Score:  {f1_score(y_test, y_pred):.4f}")
print(f"AUC-ROC:   {roc_auc_score(y_test, y_proba):.4f}")
print(f"AUC-PR:    {average_precision_score(y_test, y_proba):.4f}")
```

### When to Use Which Metric

```python
# FRAUD DETECTION (1% positive):
# → Recall is critical (don't miss fraud!)
# → Precision matters for cost (investigating false positives is expensive)
# → Use F1 or F-beta with beta=2 (weight recall 2x more)
from sklearn.metrics import fbeta_score
f2 = fbeta_score(y_test, y_pred, beta=2)  # Weights recall higher

# SPAM FILTER:
# → Precision is critical (don't put real emails in spam!)
# → Some spam getting through is OK
# → Use F-beta with beta=0.5 (weight precision more)

# MEDICAL SCREENING:
# → Recall near 100% (can't miss disease)
# → Accept lower precision (further testing is OK)

# RECOMMENDATION:
# → Precision@K (are top-K results relevant?)
# → MAP, NDCG for ranked results

# IMBALANCED DATA:
# → Accuracy is MISLEADING (99% accuracy by predicting majority class)
# → Use AUC-PR (precision-recall curve) instead of AUC-ROC
# → Or F1 score
```

### ROC and Precision-Recall Curves

```python
# ROC Curve (True Positive Rate vs False Positive Rate)
fpr, tpr, thresholds_roc = roc_curve(y_test, y_proba)
auc_roc = roc_auc_score(y_test, y_proba)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

ax1.plot(fpr, tpr, label=f'ROC (AUC={auc_roc:.3f})')
ax1.plot([0, 1], [0, 1], 'k--', label='Random')
ax1.set_xlabel('False Positive Rate')
ax1.set_ylabel('True Positive Rate')
ax1.set_title('ROC Curve')
ax1.legend()

# Precision-Recall Curve (better for imbalanced data)
precision_curve, recall_curve, thresholds_pr = precision_recall_curve(y_test, y_proba)
ap = average_precision_score(y_test, y_proba)

ax2.plot(recall_curve, precision_curve, label=f'PR (AP={ap:.3f})')
ax2.set_xlabel('Recall')
ax2.set_ylabel('Precision')
ax2.set_title('Precision-Recall Curve')
ax2.legend()
plt.tight_layout()
plt.show()

# When to use which curve:
# AUC-ROC: balanced classes, comparing models
# AUC-PR: imbalanced classes (more informative when positive class is rare)
```

---

## 2. Regression Metrics

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

y_pred = model.predict(X_test)

# Mean Squared Error (penalizes large errors)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)  # Same units as target

# Mean Absolute Error (robust to outliers)
mae = mean_absolute_error(y_test, y_pred)

# Mean Absolute Percentage Error (relative error)
mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100

# R² Score (proportion of variance explained)
r2 = r2_score(y_test, y_pred)  # 1.0 = perfect, 0.0 = mean baseline, <0 = worse than mean

print(f"RMSE: {rmse:.4f}")
print(f"MAE:  {mae:.4f}")
print(f"MAPE: {mape:.2f}%")
print(f"R²:   {r2:.4f}")

# Metric selection guide:
# | Metric | Interpretation                | Use When                      |
# |--------|-------------------------------|-------------------------------|
# | MSE    | Avg squared error             | Penalize large errors         |
# | RMSE   | Sqrt of MSE (same units)      | Standard reporting            |
# | MAE    | Avg absolute error            | Robust to outliers            |
# | MAPE   | Percentage error              | Compare across scales         |
# | R²     | Variance explained (0-1)      | Relative performance          |
```

---

## 3. Threshold Tuning

```python
# Default threshold = 0.5, but often not optimal for business

# Method 1: Optimize F1
from sklearn.metrics import f1_score

thresholds = np.arange(0.1, 0.9, 0.01)
f1_scores = [f1_score(y_test, (y_proba >= t).astype(int)) for t in thresholds]
best_threshold = thresholds[np.argmax(f1_scores)]
print(f"Best threshold (F1): {best_threshold:.2f}, F1={max(f1_scores):.4f}")

# Method 2: Business-driven threshold
# Example: Fraud detection
# Cost of missing fraud (FN): $10,000
# Cost of investigating (FP): $100
# Optimize: minimize total cost

def business_cost(threshold, y_true, y_proba, cost_fn=10000, cost_fp=100):
    y_pred = (y_proba >= threshold).astype(int)
    fn = ((y_true == 1) & (y_pred == 0)).sum()
    fp = ((y_true == 0) & (y_pred == 1)).sum()
    return fn * cost_fn + fp * cost_fp

costs = [business_cost(t, y_test, y_proba) for t in thresholds]
optimal_threshold = thresholds[np.argmin(costs)]
print(f"Optimal threshold (cost): {optimal_threshold:.2f}")

# Method 3: Target specific recall (e.g., catch 95% of fraud)
target_recall = 0.95
recalls = [recall_score(y_test, (y_proba >= t).astype(int)) for t in thresholds]
valid_thresholds = [t for t, r in zip(thresholds, recalls) if r >= target_recall]
# Pick highest threshold that achieves target recall (best precision)
best = max(valid_thresholds) if valid_thresholds else 0.5
print(f"Threshold for 95% recall: {best:.2f}")
```

---

## 4. Model Calibration

```python
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
import matplotlib.pyplot as plt

# Check calibration: is predicted probability accurate?
# If model says "70% chance of positive", is it actually positive 70% of the time?
prob_true, prob_pred = calibration_curve(y_test, y_proba, n_bins=10)

plt.figure(figsize=(8, 6))
plt.plot(prob_pred, prob_true, marker='o', label='Model')
plt.plot([0, 1], [0, 1], 'k--', label='Perfectly calibrated')
plt.xlabel('Mean Predicted Probability')
plt.ylabel('Fraction of Positives')
plt.title('Calibration Curve')
plt.legend()
plt.show()

# Fix calibration: Platt Scaling or Isotonic Regression
calibrated_model = CalibratedClassifierCV(model, method='sigmoid', cv=5)  # Platt
# calibrated_model = CalibratedClassifierCV(model, method='isotonic', cv=5)  # Non-parametric
calibrated_model.fit(X_train, y_train)
y_proba_calibrated = calibrated_model.predict_proba(X_test)[:, 1]

# When calibration matters:
# - Medical: "there's a 30% chance of disease" must be accurate
# - Ranking: if combining scores from multiple models
# - Decision-making: threshold depends on correct probabilities
# When it doesn't matter: pure ranking/sorting (AUC won't change)
```

---

## 5. Cross-Validation Strategies

```python
from sklearn.model_selection import (
    KFold, StratifiedKFold, TimeSeriesSplit, 
    cross_val_score, cross_validate
)

# Standard K-Fold (5 or 10 folds)
cv = KFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy')
print(f"CV Accuracy: {scores.mean():.4f} ± {scores.std():.4f}")

# Stratified K-Fold (maintains class distribution — use for classification)
cv_strat = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=cv_strat, scoring='f1')

# Time Series Split (respects temporal order — use for time data)
cv_time = TimeSeriesSplit(n_splits=5)
scores = cross_val_score(model, X, y, cv=cv_time, scoring='neg_mean_squared_error')
# Train: [1,2,3] Test: [4]
# Train: [1,2,3,4] Test: [5]
# Train: [1,2,3,4,5] Test: [6]  ... expanding window

# Multiple metrics at once
results = cross_validate(
    model, X, y, cv=cv_strat,
    scoring=['accuracy', 'precision', 'recall', 'f1', 'roc_auc'],
    return_train_score=True,
)
for metric in ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']:
    train_score = results[f'train_{metric}'].mean()
    test_score = results[f'test_{metric}'].mean()
    print(f"{metric:12s} Train: {train_score:.4f}  Test: {test_score:.4f}  "
          f"Gap: {train_score - test_score:.4f}")
```

---

## 6. Statistical Model Comparison

```python
from scipy import stats

# Paired t-test: Are two models significantly different?
def compare_models(model_a, model_b, X, y, cv=10):
    """Statistical test: is model A significantly better than model B?"""
    cv = StratifiedKFold(n_splits=cv, shuffle=True, random_state=42)
    
    scores_a = cross_val_score(model_a, X, y, cv=cv, scoring='accuracy')
    scores_b = cross_val_score(model_b, X, y, cv=cv, scoring='accuracy')
    
    # Paired t-test (same folds)
    t_stat, p_value = stats.ttest_rel(scores_a, scores_b)
    
    print(f"Model A: {scores_a.mean():.4f} ± {scores_a.std():.4f}")
    print(f"Model B: {scores_b.mean():.4f} ± {scores_b.std():.4f}")
    print(f"t-stat: {t_stat:.4f}, p-value: {p_value:.4f}")
    
    if p_value < 0.05:
        winner = "A" if t_stat > 0 else "B"
        print(f"Model {winner} is significantly better (p < 0.05)")
    else:
        print("No significant difference (p >= 0.05)")
    
    return scores_a, scores_b

# McNemar's test (for classification — compares actual predictions)
from statsmodels.stats.contingency_tables import mcnemar

def mcnemar_test(y_true, y_pred_a, y_pred_b):
    """Are the errors of two classifiers significantly different?"""
    # Contingency table
    correct_a = (y_pred_a == y_true)
    correct_b = (y_pred_b == y_true)
    
    # b: A correct, B wrong | c: A wrong, B correct
    b = ((correct_a) & (~correct_b)).sum()
    c = ((~correct_a) & (correct_b)).sum()
    
    table = [[0, b], [c, 0]]  # Simplified
    result = mcnemar(table, exact=True)
    return result.pvalue
```

---

## Interview Questions

### Beginner
1. **When is accuracy a bad metric?** Imbalanced classes. If 99% negative, predicting all negative gives 99% accuracy but catches 0% of positives. Use precision/recall/F1/AUC-PR instead.
2. **Precision vs Recall: explain the tradeoff.** Higher threshold → higher precision (fewer FP) but lower recall (more FN). Lower threshold → higher recall (catch more positives) but lower precision (more false alarms). F1 balances both.
3. **What does AUC-ROC represent?** Probability that a randomly chosen positive example is ranked higher than a randomly chosen negative example. 0.5 = random, 1.0 = perfect. Threshold-independent measure of discriminative ability.

### Intermediate
4. **AUC-ROC vs AUC-PR: when to use each?** AUC-ROC can be misleading with imbalanced data (high TNR inflates the score). AUC-PR focuses only on the positive class. Use AUC-PR when positive class is rare and you care about finding positives.
5. **How do you choose between MSE and MAE for regression?** MSE penalizes large errors quadratically (sensitive to outliers, good when big errors are especially bad). MAE treats all errors linearly (robust to outliers, more interpretable). Use RMSE for same-unit comparison.
6. **What is model calibration and why does it matter?** Calibrated model: predicted probability matches actual frequency. Matters for: medical decisions, combining multiple models, threshold-based decisions. Fix with Platt scaling (logistic on outputs) or isotonic regression.

### Advanced
7. **How do you evaluate a model in production vs offline?** Offline: CV metrics on held-out data. Online: A/B testing (actual business metric). Gaps happen: data distribution shift, feature freshness, system effects. Shadow deployment → canary → full rollout.
8. **Design an evaluation strategy for a ranking system.** Offline: NDCG, MAP, MRR (measure rank quality). Online: click-through rate, conversion rate, time-to-find. Position bias correction. Interleaving experiments. User satisfaction surveys.
9. **How do you handle evaluation with delayed labels?** Examples: loan default (known in 6 months), ad conversion (known in 30 days). Solutions: proxy labels (early signals), time-based splits (train on older data), partial labels, progressive evaluation as ground truth arrives.

---

## Hands-On Exercise
1. Train a model, compute all classification metrics, interpret confusion matrix
2. Plot ROC and PR curves, explain what each point represents
3. Tune threshold for a business scenario (fraud: minimize total cost)
4. Compare 3 models using cross-validation and statistical tests
5. Check calibration, apply Platt scaling, verify improvement
6. Create an evaluation report: metrics table, curves, threshold recommendation
