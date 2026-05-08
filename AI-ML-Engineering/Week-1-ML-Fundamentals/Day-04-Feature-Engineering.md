# Day 4: Feature Engineering

## Learning Objectives
- Transform numeric, categorical, text, and temporal features
- Handle missing values with appropriate strategies
- Select features using filter, wrapper, and embedded methods
- Understand feature store concepts for production ML

---

## 1. Numeric Feature Engineering

```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import (
    StandardScaler, MinMaxScaler, RobustScaler,
    PowerTransformer, PolynomialFeatures, KBinsDiscretizer
)

# --- Scaling ---
# StandardScaler: mean=0, std=1 (use for linear models, SVM, NN)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

# MinMaxScaler: [0, 1] range (use for NN, distance-based models)
X_minmax = MinMaxScaler().fit_transform(X_train)

# RobustScaler: uses median/IQR (robust to outliers)
X_robust = RobustScaler().fit_transform(X_train)

# --- Log Transform (fix right-skewed distributions) ---
df['income_log'] = np.log1p(df['income'])  # log(1+x) handles zeros
df['price_log'] = np.log(df['price'] + 1)

# PowerTransformer: Box-Cox (positive values) or Yeo-Johnson (any values)
pt = PowerTransformer(method='yeo-johnson')
X_normalized = pt.fit_transform(X_train)

# --- Binning (discretization) ---
# Convert continuous to categorical (captures non-linear effects)
binner = KBinsDiscretizer(n_bins=5, encode='ordinal', strategy='quantile')
df['age_bin'] = binner.fit_transform(df[['age']])

# Custom bins with business meaning
df['age_group'] = pd.cut(df['age'], bins=[0, 18, 35, 55, 100],
                          labels=['young', 'adult', 'middle', 'senior'])

# --- Polynomial Features (capture interactions) ---
poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
X_poly = poly.fit_transform(X_train[:, :3])  # Only on few features (explosion!)
# Creates: x1, x2, x3, x1*x2, x1*x3, x2*x3

# --- Domain-specific transforms ---
df['bmi'] = df['weight_kg'] / (df['height_m'] ** 2)
df['price_per_sqft'] = df['price'] / df['sqft']
df['ratio_income_debt'] = df['income'] / (df['debt'] + 1)
```

---

## 2. Categorical Feature Engineering

```python
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, LabelEncoder
import category_encoders as ce

# --- One-Hot Encoding (nominal categories, low cardinality) ---
# Best for: tree models and linear models with <20 categories
ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
X_encoded = ohe.fit_transform(df[['color', 'city']])

# Pandas (quick):
df_encoded = pd.get_dummies(df, columns=['color'], drop_first=True)

# --- Ordinal Encoding (ordered categories) ---
# Best for: tree models (can exploit ordering)
ordinal = OrdinalEncoder(categories=[['low', 'medium', 'high']])
df['risk_encoded'] = ordinal.fit_transform(df[['risk_level']])

# --- Target Encoding (high cardinality, supervised) ---
# Replace category with mean of target for that category
# Risk: data leakage! Must use fold-based encoding
target_enc = ce.TargetEncoder(cols=['zip_code', 'city'], smoothing=10)
X_target = target_enc.fit_transform(X_train, y_train)
X_test_target = target_enc.transform(X_test)

# Manual target encoding with smoothing (to prevent overfitting on rare categories)
def target_encode(df, col, target, smoothing=10):
    global_mean = df[target].mean()
    agg = df.groupby(col)[target].agg(['mean', 'count'])
    smooth = (agg['count'] * agg['mean'] + smoothing * global_mean) / (agg['count'] + smoothing)
    return df[col].map(smooth)

# --- Frequency Encoding ---
# Replace category with its count/frequency
freq_map = df['city'].value_counts(normalize=True).to_dict()
df['city_freq'] = df['city'].map(freq_map)

# --- Binary Encoding (high cardinality, memory efficient) ---
binary_enc = ce.BinaryEncoder(cols=['zip_code'])
X_binary = binary_enc.fit_transform(df)

# Decision guide:
# | Method          | Cardinality | Model Type      | Leakage Risk |
# |-----------------|-------------|-----------------|--------------|
# | One-Hot         | Low (<20)   | Any             | None         |
# | Ordinal         | Low-Med     | Trees           | None         |
# | Target          | High        | Any             | HIGH (use CV)|
# | Frequency       | High        | Trees           | Low          |
# | Binary          | High        | Any             | None         |
```

---

## 3. Text Feature Engineering

```python
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sentence_transformers import SentenceTransformer

# --- Bag of Words ---
count_vec = CountVectorizer(max_features=5000, stop_words='english')
X_bow = count_vec.fit_transform(texts)

# --- TF-IDF (Term Frequency × Inverse Document Frequency) ---
tfidf = TfidfVectorizer(
    max_features=10000,
    ngram_range=(1, 2),      # Unigrams and bigrams
    min_df=5,                # Ignore very rare words
    max_df=0.95,             # Ignore very common words
    stop_words='english',
)
X_tfidf = tfidf.fit_transform(texts)
print(f"Vocabulary size: {len(tfidf.vocabulary_)}")
print(f"Shape: {X_tfidf.shape}")

# --- Embeddings (modern approach, captures semantics) ---
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions
embeddings = model.encode(texts, show_progress_bar=True)
# embeddings.shape = (n_texts, 384)

# --- Simple text features (meta-features) ---
df['text_length'] = df['text'].str.len()
df['word_count'] = df['text'].str.split().str.len()
df['avg_word_length'] = df['text'].apply(lambda x: np.mean([len(w) for w in x.split()]))
df['uppercase_ratio'] = df['text'].apply(lambda x: sum(1 for c in x if c.isupper()) / len(x))
df['has_url'] = df['text'].str.contains(r'https?://', regex=True).astype(int)
df['exclamation_count'] = df['text'].str.count('!')
```

---

## 4. Date/Time Features

```python
# --- Component extraction ---
df['hour'] = df['timestamp'].dt.hour
df['day_of_week'] = df['timestamp'].dt.dayofweek  # 0=Monday
df['month'] = df['timestamp'].dt.month
df['quarter'] = df['timestamp'].dt.quarter
df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
df['is_month_end'] = df['timestamp'].dt.is_month_end.astype(int)

# --- Cyclical encoding (for periodic features) ---
# Hour 23 is close to hour 0, but numerically they're far apart
# Solution: sin/cos encoding
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
df['dow_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
df['dow_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)

# --- Lag features (time series) ---
df['sales_lag_1'] = df.groupby('store_id')['sales'].shift(1)
df['sales_lag_7'] = df.groupby('store_id')['sales'].shift(7)

# Rolling statistics
df['sales_rolling_7d'] = df.groupby('store_id')['sales'].transform(
    lambda x: x.rolling(7, min_periods=1).mean()
)
df['sales_rolling_7d_std'] = df.groupby('store_id')['sales'].transform(
    lambda x: x.rolling(7, min_periods=1).std()
)

# --- Time since event ---
df['days_since_last_purchase'] = (df['current_date'] - df['last_purchase_date']).dt.days
df['account_age_days'] = (df['current_date'] - df['signup_date']).dt.days
```

---

## 5. Missing Value Handling

```python
from sklearn.impute import SimpleImputer, KNNImputer, IterativeImputer

# --- Analysis: Understand the pattern ---
print(df.isnull().sum())
print(df.isnull().mean())  # Percentage missing

# Missing types:
# MCAR (Missing Completely At Random): safe to impute
# MAR (Missing At Random): depends on other features  
# MNAR (Missing Not At Random): missingness itself is informative

# --- Strategy 1: Simple imputation ---
num_imputer = SimpleImputer(strategy='median')  # 'mean', 'median', 'most_frequent'
X_imputed = num_imputer.fit_transform(X_train[numeric_cols])

cat_imputer = SimpleImputer(strategy='most_frequent')
X_cat_imputed = cat_imputer.fit_transform(X_train[cat_cols])

# --- Strategy 2: Indicator variable (missingness is informative) ---
df['income_missing'] = df['income'].isnull().astype(int)
df['income'] = df['income'].fillna(df['income'].median())

# --- Strategy 3: KNN Imputer (use similar rows) ---
knn_imp = KNNImputer(n_neighbors=5)
X_knn = knn_imp.fit_transform(X_train)

# --- Strategy 4: Iterative Imputer (MICE - multivariate) ---
iter_imp = IterativeImputer(max_iter=10, random_state=42)
X_iter = iter_imp.fit_transform(X_train)

# --- Strategy 5: Group-based imputation ---
df['income'] = df.groupby('occupation')['income'].transform(
    lambda x: x.fillna(x.median())
)

# Decision guide:
# | Missing %  | Strategy                        |
# |------------|----------------------------------|
# | <5%        | Simple imputation (median/mode)  |
# | 5-30%      | KNN or group-based imputation    |
# | 30-50%     | Add missing indicator + impute   |
# | >50%       | Consider dropping the feature    |
# | Informative| Always add missing indicator     |
```

---

## 6. Feature Selection

```python
from sklearn.feature_selection import (
    SelectKBest, f_classif, mutual_info_classif,
    RFE, SequentialFeatureSelector
)
from sklearn.ensemble import RandomForestClassifier

# --- Filter Methods (fast, model-independent) ---

# ANOVA F-test (linear relationship)
selector = SelectKBest(f_classif, k=10)
X_selected = selector.fit_transform(X_train, y_train)
selected_features = np.array(feature_names)[selector.get_support()]
print(f"Selected (ANOVA): {selected_features}")

# Mutual Information (captures non-linear relationships)
mi_selector = SelectKBest(mutual_info_classif, k=10)
X_mi = mi_selector.fit_transform(X_train, y_train)

# Correlation filter (remove highly correlated features)
corr_matrix = df[numeric_cols].corr().abs()
upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
to_drop = [col for col in upper_tri.columns if any(upper_tri[col] > 0.95)]

# --- Wrapper Methods (model-dependent, slower) ---

# Recursive Feature Elimination (RFE)
rfe = RFE(RandomForestClassifier(n_estimators=50, random_state=42), 
          n_features_to_select=10, step=5)
rfe.fit(X_train, y_train)
print(f"Selected (RFE): {np.array(feature_names)[rfe.support_]}")

# --- Embedded Methods (during training) ---

# L1 regularization (Lasso) — drives weights to 0
from sklearn.linear_model import LogisticRegression
lasso = LogisticRegression(penalty='l1', C=0.1, solver='liblinear')
lasso.fit(X_train, y_train)
selected = np.array(feature_names)[lasso.coef_[0] != 0]
print(f"Selected (L1): {len(selected)} features")

# Tree-based importance threshold
from sklearn.feature_selection import SelectFromModel
selector = SelectFromModel(RandomForestClassifier(n_estimators=100, random_state=42),
                            threshold='median')
selector.fit(X_train, y_train)
X_selected = selector.transform(X_train)
```

---

## 7. Feature Store Concepts

```python
# Feature Store: Centralized repository of features for ML
# Solves: training/serving skew, feature reuse, point-in-time correctness

"""
Feature Store Architecture:
┌──────────────┐     ┌─────────────────────┐     ┌──────────────┐
│   Batch      │────→│   Feature Store      │←────│  Streaming   │
│   Pipeline   │     │   (Feast, Tecton)    │     │  Pipeline    │
└──────────────┘     │                       │     └──────────────┘
                     │  - Feature registry   │
                     │  - Offline store (S3) │
                     │  - Online store(Redis)│
                     │  - Point-in-time join │
                     └──────────┬────────────┘
                                │
                     ┌──────────┼──────────┐
                     ▼          ▼          ▼
                  Training   Serving    Monitoring
                  (batch)    (online)   (drift)
"""

# Feast example (open-source feature store)
from feast import FeatureStore, Entity, Feature, FeatureView

# Define features
store = FeatureStore(repo_path=".")

# Get training data (point-in-time correct)
training_df = store.get_historical_features(
    entity_df=entities_with_timestamps,
    features=[
        "user_features:total_orders",
        "user_features:avg_order_value", 
        "user_features:days_since_last_order",
    ],
)

# Get online features for serving (latest values)
online_features = store.get_online_features(
    features=["user_features:total_orders", "user_features:avg_order_value"],
    entity_rows=[{"user_id": "user_123"}],
)
```

---

## Interview Questions

### Beginner
1. **When do you use one-hot vs target encoding?** One-hot: low cardinality (<20 categories), no data leakage risk. Target encoding: high cardinality (zip codes, IDs), much more compact, but requires cross-validation to avoid leakage.
2. **Why scale features?** Linear models, SVM, KNN, neural networks use feature magnitude. Without scaling, features with large values dominate. Trees don't need scaling (split on threshold, not magnitude).
3. **How do you handle missing values?** First understand WHY (MCAR/MAR/MNAR). Then: simple imputation (median for numeric, mode for categorical), add missing indicator if informative, KNN/iterative for complex patterns. Never drop rows in production.

### Intermediate
4. **What is target leakage and how do you prevent it?** Target leakage: using information that wouldn't be available at prediction time. Example: encoding with target mean using test data. Prevention: compute encodings only on training data, use k-fold target encoding, respect time boundaries.
5. **Why use cyclical encoding for time features?** Hour 23 and hour 0 are 1 hour apart, but numerically 23 apart. Sin/cos encoding: sin(2π·23/24) ≈ sin(2π·0/24). Preserves circular nature. Same for day-of-week, month.
6. **Compare filter vs wrapper vs embedded feature selection.** Filter (fast, model-agnostic): statistical tests (F-test, MI). Wrapper (slow, model-specific): RFE, sequential selection. Embedded (balanced): L1 regularization, tree importance. Use filter to remove obvious noise, embedded for final selection.

### Advanced
7. **How do you handle feature engineering in a production ML system?** Feature store for consistency between training and serving. Batch features (computed daily/hourly). Real-time features (streaming). Point-in-time correctness for training. Monitoring for feature drift. Versioning features with the model.
8. **How do you prevent training/serving skew in feature engineering?** Use the same transformation code (sklearn Pipeline serialized). Feature store enforces consistency. Compute features in the same system (same library, same order). Integration tests comparing training vs serving output.
9. **When does feature engineering matter more than model choice?** Almost always for tabular data. A simple model with great features beats a complex model with poor features. Trees can learn some interactions, but explicit features help all models. Domain knowledge in features is the #1 differentiator.

---

## Hands-On Exercise
1. Transform a real dataset: scale numerics, encode categoricals, engineer dates
2. Handle missing values with 3 different strategies, compare model performance
3. Create 10 meaningful features from raw e-commerce data (domain-driven)
4. Run feature selection: compare filter, RFE, and L1 results
5. Build a complete ColumnTransformer pipeline (numeric + categorical + text)
6. Measure impact: compare model with raw features vs engineered features
