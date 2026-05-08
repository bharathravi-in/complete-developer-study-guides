# Day 2: Linear Models

## Learning Objectives
- Implement linear regression from scratch using gradient descent
- Compare Normal Equation vs iterative optimization
- Understand logistic regression for classification
- Apply L1, L2, and Elastic Net regularization
- Know when linear models are the right choice

---

## 1. Linear Regression from Scratch

### The Model

$$\hat{y} = w_0 + w_1 x_1 + w_2 x_2 + \ldots + w_n x_n = \mathbf{w}^T \mathbf{x}$$

### Cost Function (MSE)

$$J(\mathbf{w}) = \frac{1}{2m} \sum_{i=1}^{m} (\hat{y}^{(i)} - y^{(i)})^2$$

### Gradient Descent

```python
import numpy as np

class LinearRegressionScratch:
    """Linear regression using gradient descent."""
    
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        self.lr = learning_rate
        self.n_iter = n_iterations
        self.weights = None
        self.bias = None
        self.losses = []
    
    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0
        
        for i in range(self.n_iter):
            # Forward pass
            y_pred = X @ self.weights + self.bias
            
            # Compute gradients
            dw = (1 / n_samples) * (X.T @ (y_pred - y))
            db = (1 / n_samples) * np.sum(y_pred - y)
            
            # Update parameters
            self.weights -= self.lr * dw
            self.bias -= self.lr * db
            
            # Track loss
            loss = np.mean((y_pred - y) ** 2)
            self.losses.append(loss)
        
        return self
    
    def predict(self, X):
        return X @ self.weights + self.bias

# Usage
from sklearn.datasets import make_regression
X, y = make_regression(n_samples=1000, n_features=5, noise=10, random_state=42)

# Normalize features (critical for gradient descent)
X = (X - X.mean(axis=0)) / X.std(axis=0)

model = LinearRegressionScratch(learning_rate=0.01, n_iterations=1000)
model.fit(X, y)
predictions = model.predict(X)
print(f"Final MSE: {np.mean((predictions - y)**2):.4f}")
```

---

## 2. Normal Equation vs Gradient Descent

### Normal Equation (Closed-Form Solution)

$$\mathbf{w} = (\mathbf{X}^T \mathbf{X})^{-1} \mathbf{X}^T \mathbf{y}$$

```python
def normal_equation(X, y):
    """Closed-form solution — no iterations needed."""
    # Add bias column
    X_b = np.column_stack([np.ones(len(X)), X])
    # Solve: w = (X^T X)^(-1) X^T y
    w = np.linalg.pinv(X_b.T @ X_b) @ X_b.T @ y
    return w

# Comparison
# | Aspect           | Normal Equation        | Gradient Descent      |
# |------------------|------------------------|------------------------|
# | Time complexity  | O(n³) (matrix inverse) | O(n²k) (k iterations) |
# | Features > 10K   | Very slow              | Works fine             |
# | Need to scale    | No                     | Yes (must normalize)   |
# | Learning rate    | Not needed             | Must tune              |
# | Works always     | No (singular matrix)   | Yes (with small lr)    |
# | Best for         | Small datasets         | Large datasets         |
```

---

## 3. Logistic Regression

### From Linear to Classification

$$\sigma(z) = \frac{1}{1 + e^{-z}}, \quad z = \mathbf{w}^T \mathbf{x}$$

$$P(y=1 | \mathbf{x}) = \sigma(\mathbf{w}^T \mathbf{x})$$

### Binary Cross-Entropy Loss

$$J(\mathbf{w}) = -\frac{1}{m} \sum_{i=1}^{m} \left[ y^{(i)} \log(\hat{y}^{(i)}) + (1-y^{(i)}) \log(1-\hat{y}^{(i)}) \right]$$

```python
class LogisticRegressionScratch:
    """Logistic regression using gradient descent."""
    
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        self.lr = learning_rate
        self.n_iter = n_iterations
    
    @staticmethod
    def sigmoid(z):
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))
    
    def fit(self, X, y):
        n_samples, n_features = X.shape
        self.weights = np.zeros(n_features)
        self.bias = 0
        
        for _ in range(self.n_iter):
            z = X @ self.weights + self.bias
            y_pred = self.sigmoid(z)
            
            # Gradients (same formula as linear, but y_pred is sigmoid output)
            dw = (1 / n_samples) * (X.T @ (y_pred - y))
            db = (1 / n_samples) * np.sum(y_pred - y)
            
            self.weights -= self.lr * dw
            self.bias -= self.lr * db
        
        return self
    
    def predict_proba(self, X):
        return self.sigmoid(X @ self.weights + self.bias)
    
    def predict(self, X, threshold=0.5):
        return (self.predict_proba(X) >= threshold).astype(int)

# Decision boundary: the line where P(y=1) = 0.5, i.e., w^T x = 0
```

---

## 4. Regularization

```python
from sklearn.linear_model import Ridge, Lasso, ElasticNet, LogisticRegression

# L2 Regularization (Ridge): Penalizes large weights
# J = MSE + λ Σ w²
# Effect: Shrinks weights toward 0, but rarely exactly 0
# When: Many features, all potentially useful, want to prevent overfitting
ridge = Ridge(alpha=1.0)  # alpha = λ
ridge.fit(X_train, y_train)

# L1 Regularization (Lasso): Penalizes absolute weights
# J = MSE + λ Σ |w|
# Effect: Drives some weights to exactly 0 (feature selection!)
# When: Many features, want automatic feature selection
lasso = Lasso(alpha=0.1)
lasso.fit(X_train, y_train)
print(f"Non-zero features: {np.sum(lasso.coef_ != 0)} / {X_train.shape[1]}")

# Elastic Net: Combination of L1 + L2
# J = MSE + λ₁ Σ |w| + λ₂ Σ w²
# When: Many correlated features (Lasso picks one randomly, Elastic Net is stable)
elastic = ElasticNet(alpha=0.1, l1_ratio=0.5)  # l1_ratio: mix of L1 vs L2
elastic.fit(X_train, y_train)

# Regularization in Logistic Regression
log_reg = LogisticRegression(
    penalty='l2',      # 'l1', 'l2', 'elasticnet', 'none'
    C=1.0,             # C = 1/λ (smaller C = more regularization)
    solver='lbfgs',    # 'liblinear' for L1
    max_iter=1000,
)
log_reg.fit(X_train, y_train)
```

### Choosing Regularization Strength

```python
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt

# Find best alpha using cross-validation
alphas = np.logspace(-4, 4, 50)
cv_scores = []

for alpha in alphas:
    model = Ridge(alpha=alpha)
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
    cv_scores.append(-scores.mean())

best_alpha = alphas[np.argmin(cv_scores)]
print(f"Best alpha: {best_alpha:.4f}")

# Or use built-in CV
from sklearn.linear_model import RidgeCV, LassoCV
ridge_cv = RidgeCV(alphas=alphas, cv=5)
ridge_cv.fit(X_train, y_train)
print(f"Best alpha (RidgeCV): {ridge_cv.alpha_:.4f}")
```

---

## 5. Complete scikit-learn Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score

# Load data
from sklearn.datasets import fetch_california_housing
data = fetch_california_housing()
X, y = data.data, data.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Pipeline: Scale → (Optional) Polynomial → Model
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', Ridge(alpha=1.0)),
])

# Fit and evaluate
pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
print(f"R² Score: {r2_score(y_test, y_pred):.4f}")
print(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.4f}")

# Cross-validation
cv_scores = cross_val_score(pipeline, X_train, y_train, cv=5, scoring='r2')
print(f"CV R² Mean: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# Feature importance (coefficients)
feature_importance = pd.DataFrame({
    'feature': data.feature_names,
    'coefficient': pipeline.named_steps['model'].coef_,
    'abs_coef': np.abs(pipeline.named_steps['model'].coef_),
}).sort_values('abs_coef', ascending=False)
print(feature_importance)
```

---

## 6. When Linear Models Are Enough

```
USE LINEAR MODELS WHEN:
✅ Interpretability required (coefficients have meaning)
✅ Small dataset (linear models generalize better with few samples)
✅ Features are roughly linearly related to target
✅ Fast inference needed (just dot product)
✅ Baseline model (always start here)
✅ Regulatory requirements (explainability)

USE SOMETHING ELSE WHEN:
❌ Complex non-linear relationships
❌ Feature interactions are important (unless you engineer them)
❌ Very high dimensional data with interactions
❌ Diminishing returns from feature engineering

LINEAR MODEL ADVANTAGES:
- Train in seconds (even on millions of rows)
- Inference: microseconds
- Interpretable: "feature X increases outcome by W"
- Well-understood statistical properties
- Easy to debug and explain
```

---

## Interview Questions

### Beginner
1. **What's the difference between linear and logistic regression?** Linear: predicts continuous value (y = wx+b). Logistic: predicts probability [0,1] using sigmoid (for classification). Different loss functions: MSE vs binary cross-entropy.
2. **Why do we normalize features for gradient descent?** Features on different scales cause elongated loss surface → slow convergence. After normalization, all features contribute equally, gradient steps are balanced, converges faster.
3. **What is the bias-variance tradeoff?** High bias (underfitting): model too simple, misses patterns. High variance (overfitting): model too complex, memorizes noise. Regularization adds bias to reduce variance.

### Intermediate
4. **L1 vs L2 regularization: when to use each?** L1 (Lasso): drives weights to exactly zero → automatic feature selection. Use when you suspect many features are irrelevant. L2 (Ridge): shrinks all weights, never exactly zero. Use when all features are potentially useful. Elastic Net: both — use with correlated features.
5. **Why is logistic regression called "regression" if it's classification?** It's fundamentally a regression of log-odds: log(p/(1-p)) = wx + b. The sigmoid maps this to probability. Decision boundary is linear in feature space.
6. **How do you handle multicollinearity?** Signs: unstable coefficients, high VIF. Solutions: remove correlated features, PCA, Ridge regression (L2 handles collinearity gracefully), Elastic Net.

### Advanced
7. **Derive the gradient of logistic regression loss.** Start with BCE: J = -1/m Σ[y log(σ) + (1-y)log(1-σ)]. Chain rule: ∂J/∂w = 1/m Σ(σ(wx)-y)x. Key insight: same form as linear regression gradient, but y_pred is sigmoid output.
8. **When would a linear model outperform a neural network?** Small data (NN overfits), limited compute (linear is instant), interpretability required, features already engineered, noisy data (NN memorizes noise). Linear + good feature engineering often beats lazy deep learning.
9. **How do you interpret coefficients in the presence of feature interactions?** Direct coefficient interpretation breaks down with interactions/polynomial features. Use SHAP values for reliable interpretation. For pure linear: coefficient = change in y per unit change in x, holding others constant.

---

## Hands-On Exercise
1. Implement linear regression from scratch (gradient descent + normal equation)
2. Implement logistic regression from scratch, plot decision boundary
3. Compare Ridge vs Lasso on a dataset with 100 features (which zeros out weights?)
4. Tune regularization strength using cross-validation
5. Build a complete sklearn pipeline for a real dataset (California Housing)
6. Interpret coefficients: which features matter most?
