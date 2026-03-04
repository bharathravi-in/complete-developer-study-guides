# DSA for AI Engineers
## Mapping Data Structures & Algorithms to AI/ML Systems

---

## Why DSA Matters for AI Engineers

AI engineering isn't just about training models. It's about:
- **Efficient inference** at scale
- **Data pipelines** that process billions of records
- **Vector search** across millions of embeddings
- **Real-time systems** with strict latency requirements
- **Resource optimization** in cloud environments

This guide maps traditional DSA concepts to real AI engineering challenges.

---

## Table of Contents

1. [Core DSA → AI Applications](#core-mapping)
2. [Vector Search & Embeddings](#vector-search)
3. [Graph Algorithms in AI](#graphs-in-ai)
4. [Efficient Data Structures for ML](#ml-structures)
5. [Interview Focus Areas](#interview-focus)
6. [Practical Projects](#projects)

---

<a name="core-mapping"></a>
## 1. Core DSA → AI Applications

### Quick Reference Matrix

| DSA Concept | AI/ML Application | Why It Matters |
|-------------|-------------------|----------------|
| **Arrays/Matrices** | Tensor operations | NumPy/PyTorch foundations |
| **Hashing** | Feature hashing, deduplication | Handle high-cardinality features |
| **Trees** | Decision trees, KD-trees, R-trees | Model structure, spatial search |
| **Heaps** | Beam search, top-K predictions | Efficient decoding in NLP |
| **Graphs** | Knowledge graphs, GNNs | Relationship modeling |
| **Tries** | Tokenizers, autocomplete | NLP preprocessing |
| **DP** | Sequence alignment, Viterbi | Traditional NLP, HMMs |
| **Bloom Filters** | Duplicate detection, caching | Data processing at scale |

---

### Detailed Mappings

#### Arrays & Matrices → Tensor Operations

**AI Context:** All deep learning is tensor manipulation.

```python
import numpy as np

# Matrix multiplication - foundation of neural networks
def linear_layer(X, W, b):
    """
    X: (batch_size, in_features)
    W: (in_features, out_features)
    b: (out_features,)
    """
    return X @ W + b  # O(batch * in * out)

# Attention mechanism (Transformer core)
def scaled_dot_product_attention(Q, K, V):
    """
    Q, K, V: (batch, seq_len, d_model)
    Time: O(seq_len² * d_model)
    Space: O(seq_len²) for attention matrix
    """
    d_k = K.shape[-1]
    scores = Q @ K.transpose(-2, -1) / np.sqrt(d_k)
    attention_weights = softmax(scores, axis=-1)
    return attention_weights @ V

# This is why O(n²) matters - seq_len=4096 means 16M operations per layer!
```

**Interview Question:**
> "How would you optimize attention for long sequences?"

**Answer:**
- **Sparse Attention:** Only attend to local windows + global tokens
- **Linear Attention:** Approximate softmax with kernel methods → O(n)
- **Flash Attention:** Optimize memory access patterns, not algorithm

---

#### Hashing → Feature Engineering

**AI Context:** Handle categorical features with millions of unique values.

```python
class FeatureHasher:
    """
    Hash trick: Convert high-cardinality features to fixed-size vectors
    Used in: Online learning, NLP, recommendation systems
    """
    def __init__(self, n_features=2**20):
        self.n_features = n_features
    
    def hash_feature(self, feature_name, value):
        """Hash (feature_name, value) pair to index"""
        key = f"{feature_name}:{value}"
        # Use double hashing for sign (reduces collision impact)
        index = hash(key) % self.n_features
        sign = 1 if hash(key + "_sign") % 2 == 0 else -1
        return index, sign
    
    def transform(self, features_dict):
        """Transform dict of features to sparse vector"""
        result = np.zeros(self.n_features)
        for name, value in features_dict.items():
            if isinstance(value, list):
                for v in value:
                    idx, sign = self.hash_feature(name, v)
                    result[idx] += sign
            else:
                idx, sign = self.hash_feature(name, value)
                result[idx] += sign * value
        return result

# Example: User features for recommendation
features = {
    "user_id": "U123456",  # Millions of users
    "viewed_products": ["P1", "P2", "P3"],  # Variable length
    "age": 25,
    "country": "US"
}
hashed = FeatureHasher(n_features=10000).transform(features)
# Now fixed 10K dimensional vector, regardless of cardinality
```

**Interview Question:**
> "How do you handle a feature with 100M unique values in an ML model?"

**Answer:**
1. **Feature Hashing:** Fixed-size representation, slight collision risk
2. **Embedding Tables:** Learnable representations (if memory allows)
3. **Frequency Bucketing:** Group rare values
4. **Target Encoding:** Replace with statistics

---

#### Trees → Model Architectures & Search

**AI Context:** Trees appear in models, search, and organization.

```python
# KD-Tree for efficient nearest neighbor search
class KDTree:
    """
    Used in: k-NN classification, similarity search, clustering
    Build: O(n log n)
    Query: O(log n) average, O(n) worst case
    """
    def __init__(self, points, depth=0):
        if not points:
            self.node = None
            return
        
        k = len(points[0])  # Dimensions
        axis = depth % k
        
        points.sort(key=lambda x: x[axis])
        median = len(points) // 2
        
        self.node = points[median]
        self.axis = axis
        self.left = KDTree(points[:median], depth + 1)
        self.right = KDTree(points[median + 1:], depth + 1)
    
    def nearest(self, target, best=None, best_dist=float('inf')):
        if self.node is None:
            return best, best_dist
        
        dist = self._distance(self.node, target)
        if dist < best_dist:
            best = self.node
            best_dist = dist
        
        # Determine which subtree to search first
        diff = target[self.axis] - self.node[self.axis]
        first = self.left if diff < 0 else self.right
        second = self.right if diff < 0 else self.left
        
        best, best_dist = first.nearest(target, best, best_dist)
        
        # Check if we need to search the other subtree
        if abs(diff) < best_dist:
            best, best_dist = second.nearest(target, best, best_dist)
        
        return best, best_dist
    
    def _distance(self, a, b):
        return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5

# Decision Tree splitting (foundation of XGBoost, Random Forest)
def find_best_split(X, y, feature_idx):
    """
    Find best split point for a feature
    Used in: CART, XGBoost, LightGBM
    """
    feature_values = X[:, feature_idx]
    sorted_indices = np.argsort(feature_values)
    
    best_gain = 0
    best_threshold = None
    
    for i in range(1, len(sorted_indices)):
        threshold = (feature_values[sorted_indices[i-1]] + 
                     feature_values[sorted_indices[i]]) / 2
        
        left_mask = feature_values <= threshold
        right_mask = ~left_mask
        
        gain = information_gain(y, y[left_mask], y[right_mask])
        
        if gain > best_gain:
            best_gain = gain
            best_threshold = threshold
    
    return best_threshold, best_gain
```

---

#### Heaps → Beam Search & Top-K

**AI Context:** Generating text with language models.

```python
import heapq

class BeamSearchDecoder:
    """
    Beam search for sequence generation (GPT, BERT, etc.)
    Maintains top-k hypotheses at each step
    """
    def __init__(self, model, beam_width=5, max_length=50):
        self.model = model
        self.beam_width = beam_width
        self.max_length = max_length
    
    def decode(self, input_ids):
        """
        Generate sequence using beam search
        Time: O(max_length * beam_width * vocab_size)
        """
        # Initialize with start token
        # Each beam: (neg_log_prob, sequence)
        beams = [(0.0, input_ids.copy())]
        
        for _ in range(self.max_length):
            candidates = []
            
            for log_prob, sequence in beams:
                if sequence[-1] == self.model.eos_token:
                    candidates.append((log_prob, sequence))
                    continue
                
                # Get next token probabilities
                next_probs = self.model.predict_next(sequence)
                
                # Get top-k next tokens (heap operation)
                top_k = heapq.nlargest(
                    self.beam_width, 
                    enumerate(next_probs),
                    key=lambda x: x[1]
                )
                
                for token_id, prob in top_k:
                    new_seq = sequence + [token_id]
                    new_log_prob = log_prob - np.log(prob + 1e-10)
                    candidates.append((new_log_prob, new_seq))
            
            # Keep top beam_width candidates
            beams = heapq.nsmallest(self.beam_width, candidates, key=lambda x: x[0])
            
            # Check if all beams ended
            if all(seq[-1] == self.model.eos_token for _, seq in beams):
                break
        
        return min(beams, key=lambda x: x[0])[1]

# Top-K sampling (alternative to beam search)
def top_k_sampling(logits, k=50, temperature=1.0):
    """
    Sample from top-k tokens with temperature
    More diverse than beam search
    """
    scaled_logits = logits / temperature
    
    # Get top-k indices using heap
    top_k_indices = heapq.nlargest(k, range(len(logits)), key=lambda i: logits[i])
    
    # Zero out non-top-k
    mask = np.full(len(logits), -float('inf'))
    mask[top_k_indices] = scaled_logits[top_k_indices]
    
    probs = softmax(mask)
    return np.random.choice(len(probs), p=probs)
```

---

<a name="vector-search"></a>
## 2. Vector Search & Embeddings

### The Core Problem

Modern AI generates embeddings (dense vectors) for everything:
- Text → 768-4096 dimensional vectors
- Images → 512-2048 dimensional vectors  
- Users/Products → 64-256 dimensional vectors

**Challenge:** Find similar vectors among millions/billions efficiently.

### Approximate Nearest Neighbor (ANN) Algorithms

#### Locality Sensitive Hashing (LSH)

```python
import numpy as np
from collections import defaultdict

class LSH:
    """
    Locality Sensitive Hashing for cosine similarity
    Key idea: Similar vectors hash to same bucket with high probability
    
    Time: O(d * num_hashes) per query
    Space: O(n * num_hashes)
    """
    def __init__(self, dim, num_hashes=10, num_tables=5):
        self.num_hashes = num_hashes
        self.num_tables = num_tables
        self.dim = dim
        
        # Random hyperplanes for hashing
        self.hyperplanes = [
            np.random.randn(num_hashes, dim) 
            for _ in range(num_tables)
        ]
        
        # Hash tables
        self.tables = [defaultdict(list) for _ in range(num_tables)]
        self.vectors = {}
    
    def _hash(self, vector, table_idx):
        """Hash vector to bucket using random hyperplanes"""
        projections = self.hyperplanes[table_idx] @ vector
        return tuple((projections > 0).astype(int))
    
    def add(self, vector_id, vector):
        """Add vector to all hash tables"""
        self.vectors[vector_id] = vector
        vector = vector / np.linalg.norm(vector)  # Normalize
        
        for i in range(self.num_tables):
            bucket = self._hash(vector, i)
            self.tables[i][bucket].append(vector_id)
    
    def query(self, vector, k=10):
        """Find approximate k nearest neighbors"""
        vector = vector / np.linalg.norm(vector)
        candidates = set()
        
        # Collect candidates from all tables
        for i in range(self.num_tables):
            bucket = self._hash(vector, i)
            candidates.update(self.tables[i][bucket])
        
        # Compute exact distances for candidates
        if not candidates:
            return []
        
        distances = []
        for cand_id in candidates:
            dist = 1 - np.dot(vector, self.vectors[cand_id] / 
                             np.linalg.norm(self.vectors[cand_id]))
            distances.append((dist, cand_id))
        
        distances.sort()
        return distances[:k]

# Usage for image similarity
# lsh = LSH(dim=512, num_hashes=15, num_tables=10)
# for img_id, embedding in image_embeddings:
#     lsh.add(img_id, embedding)
# similar = lsh.query(new_image_embedding, k=5)
```

#### HNSW (Hierarchical Navigable Small World)

```python
import heapq
import random

class HNSWNode:
    def __init__(self, vector_id, vector, level):
        self.id = vector_id
        self.vector = vector
        self.level = level
        self.neighbors = [set() for _ in range(level + 1)]

class HNSW:
    """
    State-of-the-art ANN algorithm
    Used by: Pinecone, Weaviate, Milvus, FAISS
    
    Build: O(n * log n)
    Query: O(log n) with high recall
    """
    def __init__(self, dim, M=16, ef_construction=200, max_level=16):
        self.dim = dim
        self.M = M  # Max connections per layer
        self.M_max0 = 2 * M  # Max connections at layer 0
        self.ef_construction = ef_construction
        self.max_level = max_level
        self.ml = 1 / np.log(M)
        
        self.entry_point = None
        self.nodes = {}
    
    def _random_level(self):
        """Generate random level for new node"""
        level = 0
        while random.random() < self.ml and level < self.max_level:
            level += 1
        return level
    
    def _distance(self, a, b):
        """Euclidean distance"""
        return np.linalg.norm(a - b)
    
    def _search_layer(self, query, entry_points, ef, layer):
        """Search single layer, return ef nearest neighbors"""
        visited = set(ep.id for ep in entry_points)
        candidates = []
        results = []
        
        for ep in entry_points:
            dist = self._distance(query, ep.vector)
            heapq.heappush(candidates, (dist, ep))
            heapq.heappush(results, (-dist, ep))
        
        while candidates:
            dist_c, current = heapq.heappop(candidates)
            dist_f = -results[0][0] if results else float('inf')
            
            if dist_c > dist_f:
                break
            
            for neighbor_id in current.neighbors[layer]:
                if neighbor_id in visited:
                    continue
                visited.add(neighbor_id)
                
                neighbor = self.nodes[neighbor_id]
                dist = self._distance(query, neighbor.vector)
                
                if len(results) < ef or dist < -results[0][0]:
                    heapq.heappush(candidates, (dist, neighbor))
                    heapq.heappush(results, (-dist, neighbor))
                    if len(results) > ef:
                        heapq.heappop(results)
        
        return [node for _, node in results]
    
    def insert(self, vector_id, vector):
        """Insert new vector"""
        level = self._random_level()
        node = HNSWNode(vector_id, vector, level)
        self.nodes[vector_id] = node
        
        if self.entry_point is None:
            self.entry_point = node
            return
        
        current = self.entry_point
        
        # Traverse from top to node's level
        for lc in range(self.entry_point.level, level, -1):
            current = self._search_layer(vector, [current], 1, lc)[0]
        
        # Insert at each level
        for lc in range(min(level, self.entry_point.level), -1, -1):
            neighbors = self._search_layer(
                vector, [current], self.ef_construction, lc
            )
            
            M = self.M_max0 if lc == 0 else self.M
            selected = self._select_neighbors(vector, neighbors, M)
            
            for neighbor in selected:
                node.neighbors[lc].add(neighbor.id)
                neighbor.neighbors[lc].add(vector_id)
                
                # Prune if too many connections
                if len(neighbor.neighbors[lc]) > M:
                    neighbor.neighbors[lc] = self._prune_connections(
                        neighbor, lc, M
                    )
            
            current = neighbors[0] if neighbors else current
        
        if level > self.entry_point.level:
            self.entry_point = node
    
    def _select_neighbors(self, query, candidates, M):
        """Select M best neighbors (simple strategy)"""
        candidates.sort(key=lambda n: self._distance(query, n.vector))
        return candidates[:M]
    
    def _prune_connections(self, node, layer, M):
        """Prune connections to keep only M best"""
        neighbors = list(node.neighbors[layer])
        neighbors.sort(key=lambda nid: self._distance(
            node.vector, self.nodes[nid].vector
        ))
        return set(neighbors[:M])
    
    def search(self, query, k=10, ef=50):
        """Find k nearest neighbors"""
        if self.entry_point is None:
            return []
        
        current = self.entry_point
        
        # Traverse from top to layer 0
        for lc in range(self.entry_point.level, 0, -1):
            current = self._search_layer(query, [current], 1, lc)[0]
        
        # Search layer 0 with higher ef
        candidates = self._search_layer(query, [current], ef, 0)
        
        # Return top k
        candidates.sort(key=lambda n: self._distance(query, n.vector))
        return [(n.id, self._distance(query, n.vector)) for n in candidates[:k]]
```

### Product Quantization for Memory Efficiency

```python
class ProductQuantizer:
    """
    Compress vectors for memory-efficient similarity search
    Used by: FAISS, ScaNN
    
    Compression: 384-dim float32 (1536 bytes) → 24 bytes (64x reduction)
    """
    def __init__(self, dim, n_subvectors=8, n_clusters=256):
        self.dim = dim
        self.n_subvectors = n_subvectors
        self.n_clusters = n_clusters
        self.subvector_dim = dim // n_subvectors
        
        self.codebooks = None  # (n_subvectors, n_clusters, subvector_dim)
    
    def train(self, vectors):
        """Train quantizer on sample vectors"""
        self.codebooks = np.zeros((
            self.n_subvectors, 
            self.n_clusters, 
            self.subvector_dim
        ))
        
        for i in range(self.n_subvectors):
            start = i * self.subvector_dim
            end = start + self.subvector_dim
            subvectors = vectors[:, start:end]
            
            # K-means clustering
            self.codebooks[i] = self._kmeans(subvectors, self.n_clusters)
    
    def _kmeans(self, vectors, k, max_iter=20):
        """Simple k-means for training"""
        centroids = vectors[np.random.choice(len(vectors), k, replace=False)]
        
        for _ in range(max_iter):
            # Assign to nearest centroid
            dists = np.linalg.norm(
                vectors[:, np.newaxis] - centroids, axis=2
            )
            assignments = np.argmin(dists, axis=1)
            
            # Update centroids
            for i in range(k):
                mask = assignments == i
                if np.any(mask):
                    centroids[i] = vectors[mask].mean(axis=0)
        
        return centroids
    
    def encode(self, vectors):
        """Encode vectors to compact codes"""
        codes = np.zeros((len(vectors), self.n_subvectors), dtype=np.uint8)
        
        for i in range(self.n_subvectors):
            start = i * self.subvector_dim
            end = start + self.subvector_dim
            subvectors = vectors[:, start:end]
            
            # Find nearest centroid
            dists = np.linalg.norm(
                subvectors[:, np.newaxis] - self.codebooks[i], axis=2
            )
            codes[:, i] = np.argmin(dists, axis=1)
        
        return codes
    
    def compute_distance_table(self, query):
        """Precompute distances from query to all centroids"""
        table = np.zeros((self.n_subvectors, self.n_clusters))
        
        for i in range(self.n_subvectors):
            start = i * self.subvector_dim
            end = start + self.subvector_dim
            query_sub = query[start:end]
            
            table[i] = np.linalg.norm(
                query_sub - self.codebooks[i], axis=1
            ) ** 2
        
        return table
    
    def search(self, query, codes, k=10):
        """Asymmetric distance computation (ADC)"""
        table = self.compute_distance_table(query)
        
        # Compute distances using lookup table
        distances = np.zeros(len(codes))
        for i in range(self.n_subvectors):
            distances += table[i, codes[:, i]]
        
        # Find top k
        top_k = np.argpartition(distances, k)[:k]
        top_k = top_k[np.argsort(distances[top_k])]
        
        return [(idx, np.sqrt(distances[idx])) for idx in top_k]
```

---

<a name="graphs-in-ai"></a>
## 3. Graph Algorithms in AI

### Knowledge Graphs

```python
class KnowledgeGraph:
    """
    Store and query entity relationships
    Used in: RAG systems, entity linking, question answering
    """
    def __init__(self):
        self.entities = {}  # entity_id -> properties
        self.relations = defaultdict(list)  # (head, relation) -> [tails]
        self.reverse = defaultdict(list)  # (tail, relation) -> [heads]
    
    def add_entity(self, entity_id, properties):
        self.entities[entity_id] = properties
    
    def add_relation(self, head, relation, tail):
        self.relations[(head, relation)].append(tail)
        self.reverse[(tail, relation)].append(head)
    
    def query(self, head=None, relation=None, tail=None):
        """
        Triple pattern matching
        (?, relation, tail) - find all heads
        (head, relation, ?) - find all tails
        """
        if head and relation and not tail:
            return self.relations.get((head, relation), [])
        elif tail and relation and not head:
            return self.reverse.get((tail, relation), [])
        elif head and tail:
            # Check if relation exists
            return [r for (h, r), tails in self.relations.items() 
                    if h == head and tail in tails]
    
    def multi_hop_query(self, start, path):
        """
        Multi-hop reasoning
        path = [('works_at', True), ('located_in', True)]
        True = forward, False = backward
        """
        current = {start}
        
        for relation, forward in path:
            next_set = set()
            for entity in current:
                if forward:
                    next_set.update(self.relations.get((entity, relation), []))
                else:
                    next_set.update(self.reverse.get((entity, relation), []))
            current = next_set
        
        return current
    
    def shortest_path(self, start, end, max_hops=3):
        """BFS to find shortest relation path"""
        from collections import deque
        
        queue = deque([(start, [])])
        visited = {start}
        
        while queue:
            entity, path = queue.popleft()
            
            if len(path) >= max_hops:
                continue
            
            # Try all outgoing relations
            for (head, relation), tails in self.relations.items():
                if head != entity:
                    continue
                for tail in tails:
                    if tail == end:
                        return path + [(relation, tail)]
                    if tail not in visited:
                        visited.add(tail)
                        queue.append((tail, path + [(relation, tail)]))
        
        return None  # No path found

# Example: Question answering with knowledge graph
kg = KnowledgeGraph()
kg.add_entity("Elon_Musk", {"type": "person", "born": 1971})
kg.add_entity("Tesla", {"type": "company", "founded": 2003})
kg.add_entity("SpaceX", {"type": "company", "founded": 2002})

kg.add_relation("Elon_Musk", "CEO_of", "Tesla")
kg.add_relation("Elon_Musk", "founder_of", "SpaceX")
kg.add_relation("Tesla", "industry", "Automotive")

# Query: "What companies did Elon Musk found?"
print(kg.query(head="Elon_Musk", relation="founder_of"))
# ['SpaceX']
```

### Graph Neural Networks Foundation

```python
import numpy as np

class SimpleGCN:
    """
    Simple Graph Convolutional Network layer
    Used in: Node classification, link prediction, recommendation
    
    Key insight: Aggregate neighbor features
    """
    def __init__(self, in_features, out_features):
        self.W = np.random.randn(in_features, out_features) * 0.01
    
    def forward(self, X, A):
        """
        X: Node features (n_nodes, in_features)
        A: Adjacency matrix (n_nodes, n_nodes)
        Returns: (n_nodes, out_features)
        """
        # Add self-loops
        A_hat = A + np.eye(A.shape[0])
        
        # Degree normalization
        D = np.diag(A_hat.sum(axis=1) ** -0.5)
        A_norm = D @ A_hat @ D
        
        # Message passing: aggregate neighbor features
        H = A_norm @ X @ self.W
        
        return self.relu(H)
    
    def relu(self, x):
        return np.maximum(0, x)

class GraphSAGE:
    """
    GraphSAGE: Inductive learning on graphs
    Key: Sample neighbors instead of using all
    """
    def __init__(self, in_features, out_features, n_samples=10):
        self.W = np.random.randn(2 * in_features, out_features) * 0.01
        self.n_samples = n_samples
    
    def sample_neighbors(self, node, adj_list, n):
        """Sample n neighbors uniformly"""
        neighbors = adj_list[node]
        if len(neighbors) <= n:
            return neighbors
        return np.random.choice(neighbors, n, replace=False)
    
    def forward(self, X, adj_list, nodes):
        """
        Compute embeddings for specified nodes
        """
        embeddings = []
        
        for node in nodes:
            # Sample and aggregate neighbor features
            neighbors = self.sample_neighbors(node, adj_list, self.n_samples)
            
            if len(neighbors) > 0:
                neighbor_feats = X[neighbors].mean(axis=0)
            else:
                neighbor_feats = np.zeros(X.shape[1])
            
            # Concatenate self and neighbor features
            combined = np.concatenate([X[node], neighbor_feats])
            embedding = self.relu(combined @ self.W)
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def relu(self, x):
        return np.maximum(0, x)
```

### PageRank & Recommendation

```python
def pagerank(adj_matrix, damping=0.85, max_iter=100, tol=1e-6):
    """
    PageRank algorithm
    Used in: Search ranking, importance scoring, recommendations
    
    Time: O(iter * edges)
    """
    n = adj_matrix.shape[0]
    
    # Normalize adjacency matrix
    out_degree = adj_matrix.sum(axis=1, keepdims=True)
    out_degree[out_degree == 0] = 1
    P = adj_matrix / out_degree
    
    # Initialize uniform
    rank = np.ones(n) / n
    
    for _ in range(max_iter):
        new_rank = (1 - damping) / n + damping * (P.T @ rank)
        
        if np.linalg.norm(new_rank - rank) < tol:
            break
        rank = new_rank
    
    return rank

def personalized_pagerank(adj_matrix, personalization, damping=0.85):
    """
    Personalized PageRank for recommendations
    personalization: preference vector (e.g., one-hot for user's liked items)
    """
    n = adj_matrix.shape[0]
    
    out_degree = adj_matrix.sum(axis=1, keepdims=True)
    out_degree[out_degree == 0] = 1
    P = adj_matrix / out_degree
    
    rank = personalization.copy()
    
    for _ in range(100):
        rank = (1 - damping) * personalization + damping * (P.T @ rank)
    
    return rank
```

---

<a name="ml-structures"></a>
## 4. Efficient Data Structures for ML

### Bloom Filters for Data Processing

```python
class BloomFilter:
    """
    Probabilistic set membership
    Used in: Deduplication, caching, seen URL tracking
    
    Space efficient: 10 bits per element for 1% false positive
    """
    def __init__(self, expected_elements, false_positive_rate=0.01):
        # Calculate optimal size and hash count
        self.size = self._optimal_size(expected_elements, false_positive_rate)
        self.hash_count = self._optimal_hash_count(self.size, expected_elements)
        self.bit_array = [False] * self.size
    
    def _optimal_size(self, n, p):
        """m = -(n * ln(p)) / (ln(2)^2)"""
        return int(-n * np.log(p) / (np.log(2) ** 2))
    
    def _optimal_hash_count(self, m, n):
        """k = (m / n) * ln(2)"""
        return max(1, int((m / n) * np.log(2)))
    
    def _hashes(self, item):
        """Generate k hash values using double hashing"""
        h1 = hash(item)
        h2 = hash(str(item) + "_salt")
        for i in range(self.hash_count):
            yield (h1 + i * h2) % self.size
    
    def add(self, item):
        for idx in self._hashes(item):
            self.bit_array[idx] = True
    
    def __contains__(self, item):
        return all(self.bit_array[idx] for idx in self._hashes(item))

# Usage: Dedup training data
class DataDeduplicator:
    def __init__(self, expected_docs=10_000_000):
        self.seen = BloomFilter(expected_docs, 0.001)
        self.exact_check = set()  # For borderline cases
    
    def is_duplicate(self, doc_hash):
        if doc_hash not in self.seen:
            self.seen.add(doc_hash)
            return False
        
        # Bloom filter says maybe - do exact check
        if doc_hash in self.exact_check:
            return True
        
        self.exact_check.add(doc_hash)
        return False
```

### Count-Min Sketch for Frequency Estimation

```python
class CountMinSketch:
    """
    Probabilistic frequency counting
    Used in: Heavy hitters, frequency estimation, rate limiting
    
    Space: O(log(1/δ) * 1/ε) for error ε with probability 1-δ
    """
    def __init__(self, width=1000, depth=7):
        self.width = width
        self.depth = depth
        self.table = np.zeros((depth, width), dtype=np.int64)
        self.hash_seeds = [random.randint(0, 2**32) for _ in range(depth)]
    
    def _hash(self, item, seed):
        return (hash(item) ^ seed) % self.width
    
    def add(self, item, count=1):
        for i in range(self.depth):
            j = self._hash(item, self.hash_seeds[i])
            self.table[i, j] += count
    
    def query(self, item):
        """Return minimum count (best estimate)"""
        return min(
            self.table[i, self._hash(item, self.hash_seeds[i])]
            for i in range(self.depth)
        )

# Usage: Track token frequencies in streaming data
class StreamingTokenCounter:
    def __init__(self):
        self.sketch = CountMinSketch(width=10000, depth=7)
        self.total = 0
    
    def process_batch(self, tokens):
        for token in tokens:
            self.sketch.add(token)
            self.total += 1
    
    def get_frequency(self, token):
        return self.sketch.query(token) / self.total
```

### MinHash for Document Similarity

```python
class MinHash:
    """
    Estimate Jaccard similarity of sets
    Used in: Near-duplicate detection, document clustering
    
    Jaccard(A, B) ≈ (# matching minhash values) / (# total)
    """
    def __init__(self, num_hashes=100):
        self.num_hashes = num_hashes
        self.hash_coeffs = [
            (random.randint(1, 2**32), random.randint(0, 2**32))
            for _ in range(num_hashes)
        ]
        self.prime = 2**61 - 1
    
    def _hash(self, value, a, b):
        return ((a * hash(value) + b) % self.prime)
    
    def signature(self, items):
        """Compute MinHash signature for a set of items"""
        sig = [float('inf')] * self.num_hashes
        
        for item in items:
            for i, (a, b) in enumerate(self.hash_coeffs):
                h = self._hash(item, a, b)
                sig[i] = min(sig[i], h)
        
        return sig
    
    def similarity(self, sig1, sig2):
        """Estimate Jaccard similarity from signatures"""
        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / self.num_hashes

# LSH with MinHash for finding similar documents
class MinHashLSH:
    def __init__(self, num_hashes=100, bands=20):
        self.minhash = MinHash(num_hashes)
        self.bands = bands
        self.rows_per_band = num_hashes // bands
        self.buckets = [defaultdict(list) for _ in range(bands)]
    
    def add(self, doc_id, items):
        sig = self.minhash.signature(items)
        
        for band in range(self.bands):
            start = band * self.rows_per_band
            end = start + self.rows_per_band
            band_hash = hash(tuple(sig[start:end]))
            self.buckets[band][band_hash].append((doc_id, sig))
    
    def query(self, items, threshold=0.5):
        """Find documents with similarity above threshold"""
        sig = self.minhash.signature(items)
        candidates = set()
        
        for band in range(self.bands):
            start = band * self.rows_per_band
            end = start + self.rows_per_band
            band_hash = hash(tuple(sig[start:end]))
            
            for doc_id, doc_sig in self.buckets[band].get(band_hash, []):
                candidates.add((doc_id, tuple(doc_sig)))
        
        # Verify candidates
        results = []
        for doc_id, doc_sig in candidates:
            sim = self.minhash.similarity(sig, list(doc_sig))
            if sim >= threshold:
                results.append((doc_id, sim))
        
        return sorted(results, key=lambda x: -x[1])
```

---

<a name="interview-focus"></a>
## 5. Interview Focus Areas for AI Engineers

### Must-Know Problems

| Problem Type | Example | AI Application |
|--------------|---------|----------------|
| **Top-K** | Kth Largest Element | Beam search, ranking |
| **Priority Queue** | Merge K Sorted Lists | Model ensemble |
| **Graph Traversal** | Number of Islands | Component detection |
| **Topological Sort** | Course Schedule | DAG execution (Airflow) |
| **Prefix Matching** | Implement Trie | Tokenization |
| **Interval Merging** | Merge Intervals | Batch scheduling |
| **Sliding Window** | Max Subarray | Feature engineering |
| **Binary Search** | Search in Rotated Array | Hyperparameter tuning |

### Common AI Interview Questions

#### 1. Design a Similar Image Search System

**Expected Discussion Points:**
- Feature extraction (CNN embeddings)
- Vector database choice (Pinecone, Milvus, FAISS)
- ANN algorithm selection (HNSW vs IVF)
- Trade-offs: recall vs latency vs memory


#### 2. Design a Real-time Recommendation System

**Expected Discussion Points:**
- Two-tower model architecture
- Feature store design
- Caching strategy (what to pre-compute)
- Serving latency optimization

#### 3. Map-Reduce for Distributed Training

```python
def distributed_sgd_step(data_shards, model_params, learning_rate):
    """
    Conceptual distributed SGD
    Interview: Explain communication patterns
    """
    # Map: Compute gradients on each shard
    gradients = []
    for shard in data_shards:
        grad = compute_gradient(shard, model_params)
        gradients.append(grad)
    
    # Reduce: Average gradients
    avg_gradient = sum(gradients) / len(gradients)
    
    # Update parameters
    new_params = model_params - learning_rate * avg_gradient
    return new_params

# Key discussion points:
# 1. All-reduce vs parameter server
# 2. Gradient compression
# 3. Asynchronous vs synchronous
# 4. Ring all-reduce topology
```

### Complexity Questions for AI

1. **"What's the time complexity of self-attention?"**
   - Answer: O(n² * d) where n = sequence length, d = dimension
   - Follow-up: How to reduce? → Sparse attention, linear attention

2. **"How does batch size affect training time?"**
   - Compute: O(batch_size * model_ops) per step
   - Steps per epoch: O(dataset_size / batch_size)
   - Total: Balance between parallelism and convergence

3. **"Memory complexity of storing embeddings?"**
   - Raw: O(n * d * sizeof(float32))
   - Quantized: O(n * d / 4) with INT8
   - Product quantized: O(n * num_subvectors)

---

<a name="projects"></a>
## 6. Practical Projects

### Project 1: Semantic Search Engine

```python
class SemanticSearchEngine:
    """
    Complete semantic search implementation
    Skills: Embeddings, ANN, caching, API design
    """
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2'):
        self.encoder = SentenceTransformer(model_name)
        self.index = HNSWIndex(dim=384)
        self.documents = {}
        self.cache = LRUCache(capacity=10000)
    
    def index_documents(self, documents):
        """Batch index documents"""
        embeddings = self.encoder.encode(
            [doc['text'] for doc in documents],
            batch_size=32,
            show_progress_bar=True
        )
        
        for doc, emb in zip(documents, embeddings):
            doc_id = doc['id']
            self.documents[doc_id] = doc
            self.index.add(doc_id, emb)
    
    def search(self, query, k=10):
        """Search with caching"""
        cache_key = hash(query)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        query_emb = self.encoder.encode([query])[0]
        results = self.index.search(query_emb, k=k)
        
        enriched = [
            {
                'id': doc_id,
                'score': score,
                'document': self.documents[doc_id]
            }
            for doc_id, score in results
        ]
        
        self.cache[cache_key] = enriched
        return enriched
```

### Project 2: RAG Pipeline with Knowledge Graph

```python
class RAGPipeline:
    """
    Retrieval-Augmented Generation with KG
    Skills: Vector search, graph traversal, prompt engineering
    """
    def __init__(self, vector_db, knowledge_graph, llm):
        self.vector_db = vector_db
        self.kg = knowledge_graph
        self.llm = llm
    
    def retrieve(self, query, k=5):
        """Hybrid retrieval: vector + KG"""
        # Vector retrieval
        vector_results = self.vector_db.search(query, k=k)
        
        # Entity linking
        entities = self.extract_entities(query)
        
        # KG traversal
        kg_context = []
        for entity in entities:
            relations = self.kg.get_relations(entity, max_hops=2)
            kg_context.extend(relations)
        
        return vector_results, kg_context
    
    def generate(self, query):
        """Full RAG generation"""
        vector_context, kg_context = self.retrieve(query)
        
        prompt = self.build_prompt(query, vector_context, kg_context)
        response = self.llm.generate(prompt)
        
        return response
    
    def build_prompt(self, query, vector_context, kg_context):
        context_str = "\n".join([
            f"- {doc['text']}" for doc in vector_context
        ])
        
        kg_str = "\n".join([
            f"- {head} {rel} {tail}" 
            for head, rel, tail in kg_context
        ])
        
        return f"""Answer the question using the following context.

Documents:
{context_str}

Knowledge Graph Facts:
{kg_str}

Question: {query}

Answer:"""
```

### Project 3: Feature Store with Real-time Updates

```python
class FeatureStore:
    """
    Real-time feature store for ML serving
    Skills: Caching, streaming, data structures
    """
    def __init__(self):
        self.online_store = {}  # Redis-like in-memory
        self.feature_views = {}
        self.ttl_heap = []  # Min-heap for expiration
    
    def register_feature_view(self, name, schema, ttl_seconds):
        self.feature_views[name] = {
            'schema': schema,
            'ttl': ttl_seconds
        }
    
    def write_features(self, feature_view, entity_key, features):
        """Write features with TTL"""
        key = f"{feature_view}:{entity_key}"
        expires_at = time.time() + self.feature_views[feature_view]['ttl']
        
        self.online_store[key] = {
            'features': features,
            'expires_at': expires_at
        }
        
        heapq.heappush(self.ttl_heap, (expires_at, key))
    
    def get_features(self, feature_view, entity_key):
        """Read features"""
        self._cleanup_expired()
        
        key = f"{feature_view}:{entity_key}"
        data = self.online_store.get(key)
        
        if data is None or time.time() > data['expires_at']:
            return None
        
        return data['features']
    
    def get_features_batch(self, requests):
        """Batch feature retrieval"""
        results = []
        for feature_view, entity_key in requests:
            results.append(self.get_features(feature_view, entity_key))
        return results
    
    def _cleanup_expired(self):
        """Lazy expiration cleanup"""
        now = time.time()
        while self.ttl_heap and self.ttl_heap[0][0] < now:
            _, key = heapq.heappop(self.ttl_heap)
            if key in self.online_store:
                if self.online_store[key]['expires_at'] < now:
                    del self.online_store[key]
```

---

## Quick Reference Card

### DSA ↔ AI Cheat Sheet

```
Array Operations     → Tensor manipulation
Hashing             → Feature hashing, dedup
Trees               → Decision trees, KD-trees
Heaps               → Top-K, beam search
Graphs              → Knowledge graphs, GNNs
Tries               → Tokenizers
DP                  → Sequence models (CTC, Viterbi)
Bloom Filters       → Training data dedup
LSH                 → Approximate similarity
Union-Find          → Clustering
Topological Sort    → DAG execution
```

### Complexity Targets for AI Systems

| Operation | Target | Why |
|-----------|--------|-----|
| Embedding lookup | O(1) | Real-time serving |
| ANN search | O(log n) | Large vector DBs |
| Feature retrieval | O(1) | Low-latency inference |
| Batch inference | O(batch * model) | GPU efficiency |
| Training step | O(data * params) | Distributed scaling |

---

*This guide bridges traditional DSA with modern AI engineering. Master these concepts to excel in AI/ML interviews and build production AI systems.*

*Last Updated: February 2026*
