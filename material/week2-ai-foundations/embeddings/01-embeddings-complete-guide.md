# Embeddings - Complete Guide

## What are Embeddings?

Embeddings convert text into numerical vectors (arrays of numbers) that capture semantic meaning.

```
"Machine learning is great" → [0.023, -0.156, 0.891, ..., 0.045]  (1536 numbers)
"ML is awesome"             → [0.019, -0.148, 0.887, ..., 0.041]  (very similar!)
"Cooking pasta tonight"     → [0.891, 0.234, -0.567, ..., 0.789]  (very different!)
```

**Why this matters:**
- Similar meaning → similar vectors → similar numbers
- We can mathematically compare meanings
- This enables semantic search (not just keyword matching)

---

## 1. How Embeddings Work

```
Text Input → Tokenize → Neural Network → Dense Vector → [float, float, ..., float]
```

### Key Properties:
| Property | Value | 
|----------|-------|
| Dimensions | 768 (small) to 3072 (large) |
| OpenAI ada-002 | 1536 dimensions |
| OpenAI text-embedding-3-small | 1536 dimensions |
| OpenAI text-embedding-3-large | 3072 dimensions |
| Sentence-BERT (free) | 384-768 dimensions |
| Each value | Float between -1 and 1 |

---

## 2. Generating Embeddings

### Using OpenAI
```python
from openai import OpenAI

client = OpenAI(api_key="sk-your-key")

def get_embedding(text: str, model: str = "text-embedding-3-small") -> list[float]:
    """Generate embedding for a single text."""
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def get_embeddings_batch(texts: list[str], model: str = "text-embedding-3-small") -> list[list[float]]:
    """Generate embeddings for multiple texts (batch)."""
    response = client.embeddings.create(
        input=texts,
        model=model
    )
    return [item.embedding for item in response.data]

# Usage
embedding = get_embedding("What is machine learning?")
print(f"Dimensions: {len(embedding)}")  # 1536
print(f"First 5 values: {embedding[:5]}")
```

### Using Free Local Models (sentence-transformers)
```python
# pip install sentence-transformers

from sentence_transformers import SentenceTransformer

# Free, runs locally, no API key needed!
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions

# Single text
embedding = model.encode("What is machine learning?")
print(f"Dimensions: {len(embedding)}")  # 384

# Batch (much faster)
texts = [
    "Machine learning is a subset of AI",
    "Deep learning uses neural networks",
    "Python is a programming language",
]
embeddings = model.encode(texts)
print(f"Shape: {embeddings.shape}")  # (3, 384)
```

---

## 3. Cosine Similarity (The Core Math)

**Interview Question: "What is cosine similarity and how does it work?"**

Cosine similarity measures the angle between two vectors:
- **1.0** = identical direction (same meaning)
- **0.0** = completely unrelated
- **-1.0** = opposite meaning

$$\text{cosine\_similarity}(A, B) = \frac{A \cdot B}{\|A\| \times \|B\|}$$

```python
import numpy as np

def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    a = np.array(vec1)
    b = np.array(vec2)
    
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)

# Without numpy (pure Python)
def cosine_similarity_pure(vec1: list[float], vec2: list[float]) -> float:
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a ** 2 for a in vec1) ** 0.5
    norm2 = sum(b ** 2 for b in vec2) ** 0.5
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return dot_product / (norm1 * norm2)


# Demo
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

texts = {
    "query": "How does machine learning work?",
    "similar": "ML algorithms learn patterns from data",
    "related": "Artificial intelligence is transforming industries",
    "unrelated": "I love cooking Italian pasta"
}

embeddings = {k: model.encode(v) for k, v in texts.items()}

print("Similarity scores:")
print(f"  Query vs Similar:   {cosine_similarity(embeddings['query'], embeddings['similar']):.4f}")
print(f"  Query vs Related:   {cosine_similarity(embeddings['query'], embeddings['related']):.4f}")
print(f"  Query vs Unrelated: {cosine_similarity(embeddings['query'], embeddings['unrelated']):.4f}")

# Expected output:
# Query vs Similar:   0.7823
# Query vs Related:   0.5412
# Query vs Unrelated: 0.0891
```

---

## 4. Semantic Search

```python
import numpy as np
from sentence_transformers import SentenceTransformer

class SemanticSearchEngine:
    """Simple in-memory semantic search."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.documents: list[str] = []
        self.embeddings: np.ndarray = None
    
    def index(self, documents: list[str]):
        """Index documents by generating embeddings."""
        self.documents = documents
        self.embeddings = self.model.encode(documents)
        print(f"Indexed {len(documents)} documents")
    
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search for similar documents."""
        query_embedding = self.model.encode(query)
        
        # Calculate similarities
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "text": self.documents[idx],
                "score": float(similarities[idx]),
                "index": int(idx)
            })
        
        return results


# Usage
engine = SemanticSearchEngine()

documents = [
    "Python is a high-level programming language",
    "Machine learning uses algorithms to learn from data",
    "Flask is a lightweight web framework for Python",
    "Vector databases store and search embeddings efficiently",
    "React is a JavaScript library for building user interfaces",
    "RAG combines retrieval with language model generation",
    "Redis is an in-memory data structure store",
    "Deep learning is a subset of machine learning",
    "Docker containers package applications with dependencies",
    "PostgreSQL is a powerful relational database",
]

engine.index(documents)

# Search
results = engine.search("How do neural networks learn?", top_k=3)
for r in results:
    print(f"  Score: {r['score']:.4f} | {r['text']}")

# Expected top results:
# 1. "Machine learning uses algorithms to learn from data" (0.65+)
# 2. "Deep learning is a subset of machine learning" (0.55+)
# 3. "RAG combines retrieval with language model generation" (0.30+)
```

---

## 5. Embedding Models Comparison

| Model | Dimensions | Speed | Quality | Cost | Best For |
|-------|-----------|-------|---------|------|----------|
| `text-embedding-3-small` | 1536 | Fast | Good | $0.02/1M tokens | Production (cost-effective) |
| `text-embedding-3-large` | 3072 | Slower | Best | $0.13/1M tokens | High-accuracy needs |
| `text-embedding-ada-002` | 1536 | Fast | Good | $0.10/1M tokens | Legacy |
| `all-MiniLM-L6-v2` | 384 | Very Fast | Good | Free | Local/dev |
| `all-mpnet-base-v2` | 768 | Fast | Better | Free | Local/production |
| `BAAI/bge-large-en` | 1024 | Medium | Great | Free | Best open source |

---

## 6. Production Embedding Service

```python
from dataclasses import dataclass
from typing import Optional
import hashlib
import json
import numpy as np
import logging

logger = logging.getLogger(__name__)

@dataclass
class EmbeddingResult:
    text: str
    embedding: list[float]
    model: str
    dimensions: int
    cached: bool = False

class EmbeddingService:
    """Production embedding service with caching and batching."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        cache_enabled: bool = True,
        batch_size: int = 32,
    ):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.dimensions = self.model.get_sentence_embedding_dimension()
        self.cache: dict[str, list[float]] = {}  # Simple in-memory cache
        self.cache_enabled = cache_enabled
        self.batch_size = batch_size
        self._call_count = 0
    
    def _cache_key(self, text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()
    
    def embed(self, text: str) -> EmbeddingResult:
        """Generate embedding for a single text."""
        if self.cache_enabled:
            key = self._cache_key(text)
            if key in self.cache:
                return EmbeddingResult(
                    text=text,
                    embedding=self.cache[key],
                    model=self.model_name,
                    dimensions=self.dimensions,
                    cached=True,
                )
        
        embedding = self.model.encode(text).tolist()
        self._call_count += 1
        
        if self.cache_enabled:
            self.cache[self._cache_key(text)] = embedding
        
        return EmbeddingResult(
            text=text,
            embedding=embedding,
            model=self.model_name,
            dimensions=self.dimensions,
        )
    
    def embed_batch(self, texts: list[str]) -> list[EmbeddingResult]:
        """Generate embeddings for multiple texts efficiently."""
        results = []
        uncached_texts = []
        uncached_indices = []
        
        # Check cache first
        for i, text in enumerate(texts):
            key = self._cache_key(text)
            if self.cache_enabled and key in self.cache:
                results.append(EmbeddingResult(
                    text=text,
                    embedding=self.cache[key],
                    model=self.model_name,
                    dimensions=self.dimensions,
                    cached=True,
                ))
            else:
                results.append(None)  # Placeholder
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # Generate embeddings for uncached texts in batches
        if uncached_texts:
            for batch_start in range(0, len(uncached_texts), self.batch_size):
                batch = uncached_texts[batch_start:batch_start + self.batch_size]
                embeddings = self.model.encode(batch).tolist()
                self._call_count += 1
                
                for j, embedding in enumerate(embeddings):
                    idx = uncached_indices[batch_start + j]
                    text = uncached_texts[batch_start + j]
                    
                    if self.cache_enabled:
                        self.cache[self._cache_key(text)] = embedding
                    
                    results[idx] = EmbeddingResult(
                        text=text,
                        embedding=embedding,
                        model=self.model_name,
                        dimensions=self.dimensions,
                    )
        
        return results
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts."""
        emb1 = self.embed(text1).embedding
        emb2 = self.embed(text2).embedding
        a, b = np.array(emb1), np.array(emb2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    @property
    def stats(self) -> dict:
        return {
            "model": self.model_name,
            "dimensions": self.dimensions,
            "cache_size": len(self.cache),
            "api_calls": self._call_count,
        }


# Usage
service = EmbeddingService()

# Single embedding
result = service.embed("What is machine learning?")
print(f"Dimensions: {result.dimensions}")
print(f"Cached: {result.cached}")

# Batch embeddings
texts = ["AI is great", "ML is powerful", "Python rocks"]
results = service.embed_batch(texts)

# Similarity
sim = service.similarity("machine learning", "artificial intelligence")
print(f"Similarity: {sim:.4f}")

# Stats
print(service.stats)
```

---

## Exercises

### Exercise 1: Build a FAQ Matcher
```python
# Given a list of FAQs with questions and answers,
# build a system that:
# 1. Indexes all FAQ questions
# 2. Takes a user question
# 3. Finds the most similar FAQ
# 4. Returns the answer if similarity > threshold
# 5. Returns "I don't know" if below threshold

# FAQs:
faqs = [
    {"q": "How do I reset my password?", "a": "Go to Settings > Security > Reset Password"},
    {"q": "What payment methods do you accept?", "a": "We accept Visa, Mastercard, and PayPal"},
    {"q": "How do I contact support?", "a": "Email support@example.com or call 1-800-HELP"},
    {"q": "What is your refund policy?", "a": "Full refund within 30 days of purchase"},
    {"q": "How do I upgrade my plan?", "a": "Go to Settings > Billing > Upgrade"},
]

# TODO: Implement FAQMatcher class
```

### Exercise 2: Document Deduplication
```python
# Build a system that:
# 1. Takes a list of documents
# 2. Generates embeddings for each
# 3. Finds near-duplicate pairs (similarity > 0.9)
# 4. Returns groups of duplicates

# TODO: Implement
```

---

## Key Takeaways
1. **Embeddings** = text → numbers that capture meaning
2. **Cosine similarity** = measure how similar two texts are
3. **Semantic search** = search by meaning, not just keywords
4. Use **batch processing** for efficiency
5. **Cache embeddings** — they're expensive and deterministic
6. Choose model based on: quality need, cost, latency
7. Free models (sentence-transformers) are great for development
