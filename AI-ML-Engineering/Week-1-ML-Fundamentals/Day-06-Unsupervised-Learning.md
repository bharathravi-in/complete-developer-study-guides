# Day 6: Unsupervised Learning

## Learning Objectives
- Apply K-Means, DBSCAN, and hierarchical clustering
- Reduce dimensionality with PCA, t-SNE, and UMAP
- Detect anomalies using Isolation Forest and LOF
- Choose the right unsupervised method for the problem

---

## 1. K-Means Clustering

### Algorithm
1. Initialize K centroids randomly
2. Assign each point to nearest centroid
3. Recompute centroids as mean of assigned points
4. Repeat until convergence

```python
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# Always scale before clustering (distance-based)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# K-Means
kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
labels = kmeans.fit_predict(X_scaled)

print(f"Inertia (within-cluster sum of squares): {kmeans.inertia_:.2f}")
print(f"Silhouette Score: {silhouette_score(X_scaled, labels):.4f}")  # [-1, 1], higher = better

# --- Elbow Method: Find optimal K ---
inertias = []
silhouettes = []
K_range = range(2, 15)

for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)
    silhouettes.append(silhouette_score(X_scaled, km.labels_))

# Plot elbow (look for "bend")
import matplotlib.pyplot as plt
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
ax1.plot(K_range, inertias, 'bo-')
ax1.set_xlabel('K'); ax1.set_ylabel('Inertia'); ax1.set_title('Elbow Method')

ax2.plot(K_range, silhouettes, 'ro-')
ax2.set_xlabel('K'); ax2.set_ylabel('Silhouette Score'); ax2.set_title('Silhouette Score')
plt.show()

# K-Means limitations:
# ❌ Assumes spherical clusters
# ❌ Must specify K in advance
# ❌ Sensitive to initialization (use n_init=10+)
# ❌ Sensitive to outliers
# ❌ Fails on non-convex shapes
```

---

## 2. DBSCAN (Density-Based)

```python
from sklearn.cluster import DBSCAN

# DBSCAN: Density-Based Spatial Clustering
# Finds clusters of arbitrary shape, handles noise
dbscan = DBSCAN(
    eps=0.5,            # Maximum distance between neighbors
    min_samples=5,      # Minimum points to form a dense region
    metric='euclidean',
)
labels = dbscan.fit_predict(X_scaled)

n_clusters = len(set(labels) - {-1})  # -1 = noise
n_noise = (labels == -1).sum()
print(f"Clusters: {n_clusters}, Noise points: {n_noise}")

if n_clusters > 1:
    # Silhouette only on non-noise points
    mask = labels != -1
    print(f"Silhouette: {silhouette_score(X_scaled[mask], labels[mask]):.4f}")

# --- Finding optimal eps ---
from sklearn.neighbors import NearestNeighbors

nn = NearestNeighbors(n_neighbors=5)
nn.fit(X_scaled)
distances, _ = nn.kneighbors(X_scaled)
distances = np.sort(distances[:, -1])  # Sort 5th-nearest-neighbor distances

plt.plot(distances)
plt.xlabel('Points (sorted)')
plt.ylabel('5-NN Distance')
plt.title('K-distance graph (elbow = good eps)')
plt.show()

# DBSCAN advantages:
# ✅ No need to specify K
# ✅ Handles arbitrary shapes
# ✅ Identifies outliers as noise
# ✅ Robust to outliers
# ❌ Sensitive to eps and min_samples
# ❌ Struggles with varying densities
```

---

## 3. Hierarchical Clustering

```python
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt

# Compute linkage matrix
Z = linkage(X_scaled, method='ward')  # ward, complete, average, single

# Plot dendrogram (visualize hierarchy)
plt.figure(figsize=(12, 6))
dendrogram(Z, truncate_mode='lastp', p=20)
plt.xlabel('Cluster')
plt.ylabel('Distance')
plt.title('Dendrogram (cut at desired height to get K clusters)')
plt.show()

# Agglomerative clustering
agg = AgglomerativeClustering(
    n_clusters=5,
    linkage='ward',      # 'ward', 'complete', 'average', 'single'
)
labels = agg.fit_predict(X_scaled)
print(f"Silhouette: {silhouette_score(X_scaled, labels):.4f}")

# Linkage methods:
# ward: minimize within-cluster variance (tends to find spherical clusters)
# complete: maximum distance between clusters (tight clusters)
# average: mean distance between clusters (balanced)
# single: minimum distance (can find elongated shapes, sensitive to noise)

# Advantages:
# ✅ Dendrogram provides visual interpretation
# ✅ No need to predefine K (cut dendrogram at any level)
# ✅ Works with any distance metric
# ❌ O(n³) time, O(n²) memory — not for large data
```

---

## 4. PCA (Principal Component Analysis)

```python
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# PCA: Find directions of maximum variance
pca = PCA(n_components=0.95)  # Keep 95% of variance
X_pca = pca.fit_transform(X_scaled)

print(f"Original dimensions: {X_scaled.shape[1]}")
print(f"Reduced dimensions: {X_pca.shape[1]}")
print(f"Explained variance ratios: {pca.explained_variance_ratio_[:5]}")
print(f"Total variance explained: {pca.explained_variance_ratio_.sum():.4f}")

# Scree plot (how many components to keep?)
pca_full = PCA().fit(X_scaled)
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.bar(range(1, len(pca_full.explained_variance_ratio_) + 1), 
        pca_full.explained_variance_ratio_[:20])
plt.xlabel('Component')
plt.ylabel('Variance Explained')
plt.title('Scree Plot')

plt.subplot(1, 2, 2)
plt.plot(np.cumsum(pca_full.explained_variance_ratio_))
plt.xlabel('Components')
plt.ylabel('Cumulative Variance')
plt.axhline(y=0.95, color='r', linestyle='--', label='95%')
plt.legend()
plt.show()

# PCA for visualization (2D)
pca_2d = PCA(n_components=2)
X_2d = pca_2d.fit_transform(X_scaled)
plt.scatter(X_2d[:, 0], X_2d[:, 1], c=labels, cmap='viridis', alpha=0.5)
plt.xlabel(f'PC1 ({pca_2d.explained_variance_ratio_[0]:.1%})')
plt.ylabel(f'PC2 ({pca_2d.explained_variance_ratio_[1]:.1%})')
plt.title('PCA 2D Projection')
plt.show()

# When to use PCA:
# ✅ Reduce dimensions for visualization
# ✅ Speed up downstream ML (fewer features)
# ✅ Reduce multicollinearity
# ✅ Noise reduction (small components are often noise)
# ❌ Loses interpretability (components are combinations)
# ❌ Assumes linear relationships
```

---

## 5. t-SNE and UMAP (Non-Linear Visualization)

```python
from sklearn.manifold import TSNE

# t-SNE: Non-linear dimensionality reduction for VISUALIZATION
# Preserves local structure (nearby points stay nearby)
tsne = TSNE(
    n_components=2,
    perplexity=30,       # Balance between local and global (try 5-50)
    learning_rate='auto',
    n_iter=1000,
    random_state=42,
)
X_tsne = tsne.fit_transform(X_scaled)

plt.scatter(X_tsne[:, 0], X_tsne[:, 1], c=labels, cmap='viridis', alpha=0.5, s=10)
plt.title('t-SNE Visualization')
plt.show()

# UMAP: Faster, preserves more global structure than t-SNE
import umap

reducer = umap.UMAP(
    n_components=2,
    n_neighbors=15,     # Size of local neighborhood (larger = more global)
    min_dist=0.1,       # Minimum distance between points in output
    metric='euclidean',
    random_state=42,
)
X_umap = reducer.fit_transform(X_scaled)

plt.scatter(X_umap[:, 0], X_umap[:, 1], c=labels, cmap='viridis', alpha=0.5, s=10)
plt.title('UMAP Visualization')
plt.show()

# Comparison:
# | Method | Speed    | Global Structure | Reproducible | Use For        |
# |--------|----------|-----------------|--------------|----------------|
# | PCA    | Fast     | Yes             | Yes          | Linear, fast   |
# | t-SNE  | Slow     | Poor            | No (random)  | Visualization  |
# | UMAP   | Fast     | Better          | Yes (seeded) | Viz + features |

# IMPORTANT: t-SNE/UMAP are for VISUALIZATION only
# - Distances between clusters are NOT meaningful
# - Don't use for downstream ML or inference about cluster sizes
# - Different perplexity/n_neighbors gives different pictures
```

---

## 6. Anomaly Detection

```python
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM

# --- Isolation Forest ---
# Idea: Anomalies are easier to isolate (fewer splits needed)
iso_forest = IsolationForest(
    n_estimators=100,
    contamination=0.05,  # Expected fraction of anomalies
    random_state=42,
)
anomaly_labels = iso_forest.fit_predict(X_scaled)  # -1 = anomaly, 1 = normal
anomaly_scores = iso_forest.score_samples(X_scaled)  # Lower = more anomalous

n_anomalies = (anomaly_labels == -1).sum()
print(f"Detected anomalies: {n_anomalies} ({n_anomalies/len(X)*100:.1f}%)")

# --- Local Outlier Factor (LOF) ---
# Idea: Compare local density to neighbors' density
lof = LocalOutlierFactor(
    n_neighbors=20,
    contamination=0.05,
)
lof_labels = lof.fit_predict(X_scaled)  # -1 = anomaly
lof_scores = -lof.negative_outlier_factor_  # Higher = more anomalous

# --- One-Class SVM ---
# Idea: Learn boundary around normal data
oc_svm = OneClassSVM(kernel='rbf', nu=0.05)  # nu ≈ contamination
svm_labels = oc_svm.fit_predict(X_scaled)

# --- Statistical approach: Z-score ---
def zscore_anomalies(X, threshold=3.0):
    """Flag points with any feature >3 std from mean."""
    z_scores = np.abs((X - X.mean(axis=0)) / X.std(axis=0))
    is_anomaly = (z_scores > threshold).any(axis=1)
    return is_anomaly

# --- Choosing anomaly detection method ---
# | Method          | Best For                      | Scales To      |
# |-----------------|-------------------------------|----------------|
# | Isolation Forest| General purpose, high-dim     | Large datasets |
# | LOF             | Local anomalies, varied density| Medium datasets|
# | One-Class SVM   | When boundary shape matters   | Small-medium   |
# | Z-score         | Simple, univariate            | Any size       |
# | Autoencoder     | Complex patterns, sequences   | Large datasets |
```

---

## 7. Practical Application: Customer Segmentation

```python
# End-to-end customer segmentation pipeline
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Feature engineering for RFM segmentation
def compute_rfm(transactions_df):
    """Compute Recency, Frequency, Monetary features."""
    today = transactions_df['date'].max()
    
    rfm = transactions_df.groupby('customer_id').agg({
        'date': lambda x: (today - x.max()).days,       # Recency
        'order_id': 'count',                             # Frequency
        'amount': 'sum',                                 # Monetary
    }).rename(columns={'date': 'recency', 'order_id': 'frequency', 'amount': 'monetary'})
    
    return rfm

rfm = compute_rfm(transactions)

# Scale and cluster
scaler = StandardScaler()
rfm_scaled = scaler.fit_transform(rfm)

# Find optimal K
best_k = 4  # From elbow/silhouette analysis
kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
rfm['segment'] = kmeans.fit_predict(rfm_scaled)

# Interpret segments
segment_profile = rfm.groupby('segment').agg({
    'recency': 'mean',
    'frequency': 'mean', 
    'monetary': 'mean',
}).round(1)

segment_names = {
    0: 'Champions',        # Low recency, high frequency, high monetary
    1: 'At Risk',          # High recency, medium frequency
    2: 'New Customers',    # Low recency, low frequency
    3: 'Hibernating',      # High recency, low frequency, low monetary
}
print(segment_profile)
```

---

## Interview Questions

### Beginner
1. **How does K-Means work? What are its limitations?** 1) Initialize K centroids 2) Assign points to nearest centroid 3) Update centroids 4) Repeat. Limitations: must choose K, assumes spherical clusters, sensitive to initialization and outliers.
2. **What is the silhouette score?** Measures how similar a point is to its own cluster vs nearest cluster. Range [-1, 1]. High = well-clustered. 0 = overlapping. Negative = likely misclassified. Average across all points.
3. **PCA: what does it do and when to use?** Finds orthogonal directions (principal components) that capture maximum variance. Use for: dimensionality reduction, visualization, noise reduction, removing multicollinearity. Limitation: linear only.

### Intermediate
4. **K-Means vs DBSCAN: when to use each?** K-Means: know K, spherical clusters, large data. DBSCAN: unknown K, arbitrary shapes, need to identify noise. DBSCAN fails with varying density. K-Means fails with non-convex shapes.
5. **How do you validate clustering results without labels?** Internal metrics: silhouette score, Davies-Bouldin index, Calinski-Harabasz. Visual: t-SNE/UMAP with cluster colors. Domain: are clusters actionable/interpretable? Stability: do clusters persist across random seeds?
6. **Explain Isolation Forest for anomaly detection.** Random trees with random splits. Anomalies isolated quickly (short path from root). Normal points need more splits. Score = average path length across trees. Scales well (O(n log n)), handles high dimensions.

### Advanced
7. **How do you choose between t-SNE and UMAP?** UMAP: faster (O(n) vs O(n²)), better global structure, reproducible, can project new points. t-SNE: better local structure, more established. Both: visualization only, don't trust distances between clusters.
8. **Design a production anomaly detection system.** Data → feature engineering → multiple detectors (ensemble) → scoring → threshold → alert. Handle: concept drift (retrain periodically), cold start (rule-based initially), false positive management (feedback loop). Monitor detector performance.
9. **How do you handle the curse of dimensionality in clustering?** High dimensions: distances become meaningless. Solutions: PCA/UMAP first, then cluster. Feature selection. Use cosine similarity instead of Euclidean. Subspace clustering (cluster in different feature subsets).

---

## Hands-On Exercise
1. Apply K-Means with elbow method, find optimal K
2. Compare K-Means vs DBSCAN on the moons dataset (non-convex)
3. Apply PCA to reduce a 50-feature dataset, visualize in 2D
4. Use t-SNE and UMAP to visualize MNIST digits
5. Build an anomaly detection system (Isolation Forest + threshold tuning)
6. Customer segmentation: compute RFM features, cluster, interpret segments
