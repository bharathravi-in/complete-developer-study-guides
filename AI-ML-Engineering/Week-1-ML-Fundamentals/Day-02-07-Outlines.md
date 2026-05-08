# Week 1: ML Fundamentals — Remaining Day Outlines

## Day 2: Linear Models
- Linear regression from scratch (gradient descent)
- Normal equation vs gradient descent
- Logistic regression (sigmoid, decision boundary)
- Regularization: L1 (Lasso), L2 (Ridge), Elastic Net
- scikit-learn implementation
- When linear models are enough (interpretable, fast)

## Day 3: Tree-Based Models
- Decision trees (entropy, Gini impurity, information gain)
- Random Forest (bagging, feature randomness)
- XGBoost/LightGBM (gradient boosting, sequential trees)
- Feature importance (built-in, permutation, SHAP)
- Hyperparameter tuning (max_depth, n_estimators, learning_rate)
- When to use trees vs linear vs neural

## Day 4: Feature Engineering
- Numeric: scaling, log transforms, binning, polynomial features
- Categorical: one-hot, ordinal, target encoding, frequency encoding
- Text: TF-IDF, count vectors, embeddings
- Date/time: components, cyclical encoding, lags
- Missing values: imputation strategies
- Feature selection: filter, wrapper, embedded methods
- Feature stores concept

## Day 5: Model Evaluation
- Classification metrics: accuracy, precision, recall, F1, AUC-ROC, AUC-PR
- Regression metrics: MSE, RMSE, MAE, MAPE, R²
- Confusion matrix deep dive
- Threshold tuning for business requirements
- Calibration (Platt scaling, isotonic)
- Statistical tests for model comparison
- When accuracy is misleading (imbalanced data)

## Day 6: Unsupervised Learning
- K-Means clustering (elbow method, silhouette score)
- DBSCAN (density-based, handles noise/irregular shapes)
- Hierarchical clustering (dendrograms)
- PCA (principal components, explained variance)
- t-SNE and UMAP (visualization)
- Anomaly detection (Isolation Forest, LOF)
- Applications: customer segmentation, outlier detection

## Day 7: Project — End-to-End ML Pipeline
- Problem definition and EDA
- Feature engineering pipeline (sklearn ColumnTransformer)
- Model selection (compare 3+ algorithms)
- Hyperparameter tuning (GridSearchCV/Optuna)
- Cross-validation and final evaluation
- Model serialization and simple API
- Write up findings (notebook format)
