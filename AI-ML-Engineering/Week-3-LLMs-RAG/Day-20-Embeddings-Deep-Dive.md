# Day 20: Embeddings Deep Dive

## Learning Objectives
- Understand how embeddings are trained (contrastive learning)
- Fine-tune embedding models for domain-specific tasks
- Apply Matryoshka representations and dimensionality reduction
- Work with multi-modal embeddings
- Optimize embeddings for production (quantization, caching)
- Navigate the MTEB leaderboard

---

## 1. How Embeddings Are Trained

```python
# Embeddings are learned via contrastive learning:
# - Similar pairs should have high cosine similarity
# - Dissimilar pairs should have low cosine similarity

# Training data examples:
# Positive pair: ("What is Python?", "Python is a programming language")
# Negative pair: ("What is Python?", "The weather is sunny today")

# InfoNCE / Contrastive Loss
import torch
import torch.nn.functional as F

def contrastive_loss(query_emb, positive_emb, negative_embs, temperature=0.05):
    """
    InfoNCE loss: maximize similarity with positive, minimize with negatives.
    """
    # Cosine similarity with positive
    pos_sim = F.cosine_similarity(query_emb, positive_emb, dim=-1) / temperature
    
    # Cosine similarity with negatives
    neg_sims = F.cosine_similarity(
        query_emb.unsqueeze(1), negative_embs, dim=-1
    ) / temperature
    
    # Combine: log_softmax over [positive, negatives]
    logits = torch.cat([pos_sim.unsqueeze(-1), neg_sims], dim=-1)
    labels = torch.zeros(logits.shape[0], dtype=torch.long)  # positive is index 0
    
    return F.cross_entropy(logits, labels)

# Key training strategies:
# 1. Hard negatives: negatives that are similar but wrong (harder to distinguish)
# 2. In-batch negatives: use other batch items as negatives (efficient)
# 3. Knowledge distillation: train small model to mimic large model's embeddings
```

---

## 2. Fine-Tuning Embeddings

```python
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# When to fine-tune:
# - Domain-specific vocabulary (legal, medical, code)
# - Your retrieval task differs from general search
# - Off-the-shelf models underperform on your data

# Prepare training data (query, positive_doc, optionally negative_doc)
train_examples = [
    InputExample(texts=["kubernetes pod crash", "CrashLoopBackOff indicates the container is repeatedly failing"]),
    InputExample(texts=["how to scale deployment", "Use kubectl scale deployment --replicas=5"]),
    InputExample(texts=["nginx ingress config", "apiVersion: networking.k8s.io/v1\nkind: Ingress"]),
]

# Load base model
model = SentenceTransformer('BAAI/bge-base-en-v1.5')

# Training with MultipleNegativesRankingLoss (most common for retrieval)
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.MultipleNegativesRankingLoss(model=model)

# Fine-tune
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,
    warmup_steps=100,
    output_path="./fine-tuned-embeddings",
)

# With hard negatives (triplet: query, positive, hard_negative)
triplet_examples = [
    InputExample(texts=[
        "python memory leak",              # query
        "Use tracemalloc to find memory leaks in Python",  # positive
        "Python supports garbage collection for memory management",  # hard negative
    ]),
]
triplet_loss = losses.TripletLoss(model=model)

# Evaluate fine-tuned model
from sentence_transformers.evaluation import InformationRetrievalEvaluator

evaluator = InformationRetrievalEvaluator(
    queries={"q1": "how to debug python"},
    corpus={"d1": "Use pdb debugger", "d2": "Python is interpreted"},
    relevant_docs={"q1": {"d1"}},
)
score = evaluator(model)
print(f"NDCG@10: {score['ndcg@10']}")
```

---

## 3. Matryoshka Representations

```python
# Matryoshka embeddings: single model produces useful embeddings at MULTIPLE dimensions
# Named after Russian nesting dolls — first N dimensions are also meaningful

# Traditional: 768-dim embedding (fixed)
# Matryoshka: dims[:64] useful, dims[:128] better, dims[:768] best

# Why this matters:
# - Use 64 dims for fast initial filtering (4x less storage/compute)
# - Use full 768 dims for final re-ranking
# - Adaptive: choose precision vs speed at query time

from sentence_transformers import SentenceTransformer

# Models trained with Matryoshka loss
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5")

# Get full embedding
full_emb = model.encode("Hello world")  # 768 dims

# Truncate to smaller dimensions (still useful!)
import numpy as np

def truncate_embedding(embedding, dim):
    """Truncate Matryoshka embedding to desired dimension."""
    truncated = embedding[:dim]
    # Re-normalize after truncation
    return truncated / np.linalg.norm(truncated)

emb_64 = truncate_embedding(full_emb, 64)    # Fast, less accurate
emb_256 = truncate_embedding(full_emb, 256)  # Good balance
emb_768 = truncate_embedding(full_emb, 768)  # Full quality

# Multi-stage retrieval with Matryoshka:
# 1. Search with 64-dim embeddings (fast, broad) → top-1000
# 2. Re-score with 256-dim embeddings → top-100
# 3. Re-score with full 768-dim → top-10

# Training Matryoshka embeddings
from sentence_transformers.losses import MatryoshkaLoss, MultipleNegativesRankingLoss

base_loss = MultipleNegativesRankingLoss(model)
matryoshka_loss = MatryoshkaLoss(
    model=model,
    loss=base_loss,
    matryoshka_dims=[64, 128, 256, 512, 768],  # Train at all these dims
)
```

---

## 4. Multi-Modal Embeddings

```python
# Embed text AND images into same vector space
# Enables: text→image search, image→text search, cross-modal retrieval

# CLIP (OpenAI) — text + image in same space
from transformers import CLIPModel, CLIPProcessor
from PIL import Image

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Encode text
text_inputs = processor(text=["a photo of a cat", "a photo of a dog"], 
                        return_tensors="pt", padding=True)
text_embs = model.get_text_features(**text_inputs)

# Encode image
image = Image.open("cat.jpg")
image_inputs = processor(images=image, return_tensors="pt")
image_emb = model.get_image_features(**image_inputs)

# Cross-modal similarity
import torch.nn.functional as F
similarity = F.cosine_similarity(text_embs, image_emb)
# "a photo of a cat" will have higher similarity with cat.jpg

# Multi-modal RAG: index images and text together
# Query with text → retrieve relevant images or text chunks
# Query with image → find similar images or related text descriptions

# Newer models: SigLIP, BLIP-2, Nomic Embed Vision
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("nomic-ai/nomic-embed-vision-v1.5")
# Embeds images into same space as nomic text model
```

---

## 5. Production Optimization

```python
import numpy as np

# 1. Quantization — reduce memory & speed up search
def quantize_embeddings(embeddings: np.ndarray, method="int8"):
    """Quantize float32 embeddings to reduce memory."""
    if method == "int8":
        # Scale to [-128, 127] range
        max_val = np.abs(embeddings).max(axis=1, keepdims=True)
        scale = 127.0 / (max_val + 1e-8)
        quantized = np.round(embeddings * scale).astype(np.int8)
        return quantized, scale
    elif method == "binary":
        # Binary: 32x compression (each dim → 1 bit)
        return (embeddings > 0).astype(np.uint8)
    
# Memory comparison (1M documents, 768 dims):
# float32: 1M × 768 × 4 bytes = 3.07 GB
# int8:    1M × 768 × 1 byte  = 768 MB (4x smaller)
# binary:  1M × 768 / 8 bytes = 96 MB  (32x smaller)

# 2. Embedding cache
from functools import lru_cache
import hashlib

class EmbeddingCache:
    def __init__(self, embedder, cache_size=10000):
        self.embedder = embedder
        self.cache = {}
    
    def encode(self, text: str) -> np.ndarray:
        key = hashlib.md5(text.encode()).hexdigest()
        if key not in self.cache:
            self.cache[key] = self.embedder.encode(text)
        return self.cache[key]

# 3. Batch encoding for efficiency
def batch_encode(texts: list[str], model, batch_size=256):
    """Encode large number of texts in batches."""
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        embeddings = model.encode(batch, show_progress_bar=True)
        all_embeddings.append(embeddings)
    return np.vstack(all_embeddings)

# 4. Approximate Nearest Neighbor (ANN) indexing
import faiss

# Build HNSW index (fast, good recall)
dim = 768
index = faiss.IndexHNSWFlat(dim, 32)  # 32 = num connections
index.hnsw.efConstruction = 200  # Higher = better index, slower build
index.add(embeddings)  # Add all document embeddings

# Search
index.hnsw.efSearch = 64  # Higher = better recall, slower search
distances, indices = index.search(query_embedding.reshape(1, -1), k=10)

# IVF index (for very large datasets)
nlist = 1000  # Number of clusters
quantizer = faiss.IndexFlatIP(dim)
index = faiss.IndexIVFFlat(quantizer, dim, nlist)
index.train(embeddings)  # Must train first
index.add(embeddings)
index.nprobe = 10  # Search 10 clusters (speed vs recall trade-off)
```

---

## 6. MTEB Leaderboard & Model Selection

```python
# MTEB (Massive Text Embedding Benchmark): standardized evaluation
# Evaluates across: Retrieval, Classification, Clustering, Reranking, STS, etc.

# Top models (as of 2024-2025):
# | Model                      | Dims | Size  | Best For                    |
# |----------------------------|------|-------|-----------------------------|
# | text-embedding-3-large     | 3072 | API   | High quality, any task      |
# | BAAI/bge-large-en-v1.5     | 1024 | 335M  | Best open-source (English)  |
# | nomic-ai/nomic-embed-text  | 768  | 137M  | Matryoshka, good balance    |
# | all-MiniLM-L6-v2           | 384  | 23M   | Fast prototyping, lightweight|
# | Cohere embed-v3            | 1024 | API   | Multilingual, high quality  |
# | jina-embeddings-v3         | 1024 | 570M  | Long context (8192 tokens)  |

# How to choose:
# 1. Check MTEB scores for YOUR task type (retrieval vs classification vs clustering)
# 2. Consider constraints: latency, memory, cost, privacy (local vs API)
# 3. Test on YOUR data — leaderboard scores don't always transfer
# 4. Consider max sequence length (most: 512, some: 8192)

# Evaluate on your data:
from sentence_transformers import SentenceTransformer
from sentence_transformers.evaluation import InformationRetrievalEvaluator

# Compare models on your retrieval task
models_to_test = [
    "all-MiniLM-L6-v2",
    "BAAI/bge-base-en-v1.5", 
    "nomic-ai/nomic-embed-text-v1.5",
]

for model_name in models_to_test:
    model = SentenceTransformer(model_name)
    score = evaluator(model)
    print(f"{model_name}: NDCG@10 = {score['ndcg@10']:.4f}")
```

---

## Interview Questions

### Beginner
1. **What is contrastive learning for embeddings?** Train model to produce similar vectors for related text and dissimilar vectors for unrelated text. Uses positive pairs (same meaning) and negative pairs (different meaning). Loss function pushes positives together and negatives apart in vector space.
2. **Why would you fine-tune an embedding model?** When domain-specific vocabulary matters (legal, medical, code). When off-the-shelf models don't capture domain relationships. When your retrieval task differs from general web search. Typical improvement: 5-15% on domain-specific benchmarks.
3. **What is embedding dimensionality and why does it matter?** Number of values in the embedding vector. Higher dims = more capacity to encode meaning, but more storage and compute. Trade-off: 384 dims (fast, smaller) vs 1024+ dims (higher quality). Choose based on your accuracy vs resource constraints.

### Intermediate
4. **Explain Matryoshka embeddings.** Single model trained to produce useful embeddings at multiple dimensions. First N dimensions form a valid (lower-quality) embedding. Enables adaptive retrieval: use fewer dims for fast initial search, full dims for final scoring. Trained with loss at multiple truncation points.
5. **How do you quantize embeddings for production?** Float32 → Int8 (4x compression, ~1% accuracy loss): scale to [-128,127]. Float32 → Binary (32x compression, ~5% accuracy loss): threshold at 0. Use binary for initial candidate selection, full precision for re-scoring.
6. **What is HNSW and why is it used?** Hierarchical Navigable Small World — graph-based ANN index. Nodes connected to neighbors at multiple granularity levels. Search: start at top level (coarse), navigate down (fine). Sub-millisecond search even with millions of vectors. Trade-off: memory (stores graph) vs speed.

### Advanced
7. **How would you build a multi-modal RAG system?** Use CLIP/SigLIP to embed images and text in same space. Index: embed all documents (text chunks + image descriptions + raw images). Retrieval: embed query (text or image), search unified index. Generation: pass retrieved items (text + image) to multi-modal LLM (GPT-4V, Gemini). Challenge: alignment between modalities.
8. **Design an embedding pipeline for 100M documents.** Batch processing with GPU cluster. Quantize to int8 (reduce 4x storage). Use IVF-PQ index (compressed vectors + inverted index). Shard across machines. Pre-filter by metadata before vector search. Cache frequent queries. Async indexing for new docs.
9. **When does fine-tuning hurt embedding quality?** Catastrophic forgetting: over-training on narrow domain loses general knowledge. Solution: mix domain data with general data (10-20%). Low-quality training data: noisy labels hurt more than help. Too few examples: need 1000+ quality pairs minimum. Wrong loss function for your task type.

---

## Hands-On Exercise
1. Train embeddings with contrastive loss on a small dataset (50 pairs)
2. Fine-tune `all-MiniLM-L6-v2` on domain-specific query-doc pairs
3. Implement Matryoshka truncation and measure quality at 64/128/256/768 dims
4. Build multi-modal search: embed images + text, search with text query
5. Quantize embeddings (int8, binary) and measure recall degradation
6. Benchmark 3 embedding models from MTEB on your own test set
