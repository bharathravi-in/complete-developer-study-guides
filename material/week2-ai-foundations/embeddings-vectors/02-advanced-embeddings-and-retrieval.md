# Advanced Embeddings & Vector Search — Reranking, Hybrid Search & Multi-Modal

> Deep dive into the retrieval layer — where 80% of RAG quality is determined.

---

## 1. Embedding Models Comparison

```
Model                       Dims    Speed     Quality   Cost
─────────────────────────────────────────────────────────────
OpenAI text-embedding-3-large 3072  Fast      Best      $0.13/M tokens
OpenAI text-embedding-3-small 1536  Fastest   Good      $0.02/M tokens
Cohere embed-v3               1024  Fast      Excellent $0.10/M tokens
sentence-transformers (local)  384  Medium    Good      Free
BGE M3 (local)                1024  Slow      Excellent Free
Nomic embed (local + API)      768  Medium    Very Good Free/Cheap

WHICH TO CHOOSE:
  Personal projects → sentence-transformers (free)
  Production, budget → text-embedding-3-small ($0.02/M)
  Production, quality → text-embedding-3-large ($0.13/M)
  Privacy-sensitive → BGE M3 (run locally)
```

### Embedding Best Practices
```python
# 1. Normalize embeddings for cosine similarity
import numpy as np

def normalize(vector: list[float]) -> list[float]:
    arr = np.array(vector)
    return (arr / np.linalg.norm(arr)).tolist()

# 2. Use instruction-prefixed embeddings (newer models)
# For OpenAI text-embedding-3, no prefix needed
# For many open-source models:
query_embedding = model.encode("query: What is Python?")        # Search query
doc_embedding = model.encode("passage: Python is a language...")  # Document

# 3. Batch embeddings (don't embed one at a time)
texts = ["chunk 1", "chunk 2", "chunk 3"]
embeddings = model.encode(texts, batch_size=32)  # Much faster

# 4. Matryoshka embeddings (OpenAI text-embedding-3)
# You can truncate to smaller dimensions for faster search
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
    model="text-embedding-3-large",
    input="Hello world",
    dimensions=256,  # Truncate from 3072 → 256 (12x less storage, ~5% quality drop)
)
```

---

## 2. Reranking (Cross-Encoder)

### Why Reranking?
```
Bi-encoder (embedding search):
  - Fast: O(1) with vector index
  - But: Query and document are encoded separately
  - Medium quality

Cross-encoder (reranker):
  - Slow: Processes query + document together
  - But: Captures fine-grained interactions
  - High quality

Best: Use bi-encoder for initial retrieval (top 20)
       → then cross-encoder to rerank (pick top 5)
```

### Implementation
```python
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)
    
    def rerank(
        self, query: str, chunks: list[dict], top_k: int = 5
    ) -> list[dict]:
        """Rerank chunks using cross-encoder."""
        
        # Create query-chunk pairs
        pairs = [(query, chunk["text"]) for chunk in chunks]
        
        # Score with cross-encoder
        scores = self.model.predict(pairs)
        
        # Combine scores with chunks
        for chunk, score in zip(chunks, scores):
            chunk["rerank_score"] = float(score)
        
        # Sort by rerank score
        reranked = sorted(chunks, key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]

# Usage in RAG pipeline
class EnhancedRAGPipeline:
    def __init__(self, embedder, vector_db, reranker, llm):
        self.embedder = embedder
        self.vector_db = vector_db
        self.reranker = reranker
        self.llm = llm
    
    def query(self, question: str) -> dict:
        # Step 1: Embed and retrieve top 20
        vector = self.embedder.embed(question)
        candidates = self.vector_db.search(vector, top_k=20)
        
        # Step 2: Rerank to top 5
        reranked = self.reranker.rerank(question, candidates, top_k=5)
        
        # Step 3: Generate with top 5
        context = "\n\n".join([c["text"] for c in reranked])
        answer = self.llm.generate(question, context)
        
        return {
            "answer": answer,
            "sources": reranked,
        }
```

---

## 3. Hybrid Search (Dense + Sparse)

### Concept
```
Dense search (embeddings):       Good for semantic similarity
Sparse search (BM25/keywords):   Good for exact terms, names, codes

Example where sparse wins:
  Query: "error code ERR-4012"
  Dense: Finds "error handling" documents (wrong!)
  Sparse: Finds exact "ERR-4012" match (correct!)

Example where dense wins:
  Query: "how to fix memory problems"
  Dense: Finds "RAM optimization techniques" (correct!)
  Sparse: Only finds docs with exact word "memory problems"

Hybrid: Combine both for best results!
```

### Implementation
```python
import math
from collections import Counter

class BM25:
    """Simple BM25 implementation for sparse retrieval."""
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_freqs: Counter = Counter()
        self.doc_lens: list[int] = []
        self.avg_dl: float = 0
        self.corpus_size: int = 0
        self.index: dict[str, list[tuple[int, int]]] = {}  # term → [(doc_id, freq)]
    
    def index_documents(self, documents: list[str]):
        """Build BM25 index."""
        self.corpus_size = len(documents)
        
        for doc_id, doc in enumerate(documents):
            tokens = doc.lower().split()
            self.doc_lens.append(len(tokens))
            
            term_freq = Counter(tokens)
            for term, freq in term_freq.items():
                self.doc_freqs[term] += 1
                self.index.setdefault(term, []).append((doc_id, freq))
        
        self.avg_dl = sum(self.doc_lens) / self.corpus_size if self.corpus_size else 0
    
    def search(self, query: str, top_k: int = 10) -> list[tuple[int, float]]:
        """Search with BM25 scoring."""
        tokens = query.lower().split()
        scores: dict[int, float] = {}
        
        for term in tokens:
            if term not in self.index:
                continue
            
            df = self.doc_freqs[term]
            idf = math.log((self.corpus_size - df + 0.5) / (df + 0.5) + 1)
            
            for doc_id, tf in self.index[term]:
                dl = self.doc_lens[doc_id]
                score = idf * (tf * (self.k1 + 1)) / (
                    tf + self.k1 * (1 - self.b + self.b * dl / self.avg_dl)
                )
                scores[doc_id] = scores.get(doc_id, 0) + score
        
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:top_k]


class HybridSearch:
    """Combine dense (embedding) and sparse (BM25) search."""
    
    def __init__(
        self,
        embedder,
        vector_db,
        bm25: BM25,
        dense_weight: float = 0.7,
        sparse_weight: float = 0.3,
    ):
        self.embedder = embedder
        self.vector_db = vector_db
        self.bm25 = bm25
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
    
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        # Dense search
        vector = self.embedder.embed(query)
        dense_results = self.vector_db.search(vector, top_k=top_k * 2)
        
        # Sparse search (BM25)
        sparse_results = self.bm25.search(query, top_k=top_k * 2)
        
        # Reciprocal Rank Fusion (RRF)
        scores: dict[str, float] = {}
        
        for rank, (chunk_id, _) in enumerate(dense_results):
            rrf = 1 / (60 + rank)  # RRF constant = 60
            scores[chunk_id] = scores.get(chunk_id, 0) + self.dense_weight * rrf
        
        for rank, (doc_id, _) in enumerate(sparse_results):
            rrf = 1 / (60 + rank)
            chunk_id = str(doc_id)
            scores[chunk_id] = scores.get(chunk_id, 0) + self.sparse_weight * rrf
        
        # Sort by combined score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [{"id": cid, "score": score} for cid, score in ranked[:top_k]]
```

---

## 4. Chunking Strategies Deep Dive

### Comparison
```
Strategy              Best For                    Size
─────────────────────────────────────────────────────────
Fixed size            General text, logs           500 chars
Recursive character   Most documents               500-1000 chars
Sentence-based        Academic papers, precise Q&A  3-5 sentences
Semantic chunking     Mixed-topic documents         Variable
Parent-child          Hierarchical docs (manuals)   Parent: 2000, Child: 200
```

### Semantic Chunking
```python
import numpy as np

def semantic_chunk(text: str, embedder, threshold: float = 0.5) -> list[str]:
    """Split text where semantic meaning changes significantly."""
    sentences = text.split('. ')
    
    if len(sentences) <= 1:
        return [text]
    
    # Embed each sentence
    embeddings = embedder.encode(sentences)
    
    # Calculate similarity between consecutive sentences
    chunks = []
    current_chunk = [sentences[0]]
    
    for i in range(1, len(sentences)):
        similarity = cosine_similarity(embeddings[i-1], embeddings[i])
        
        if similarity < threshold:
            # Semantic break — start new chunk
            chunks.append('. '.join(current_chunk) + '.')
            current_chunk = [sentences[i]]
        else:
            current_chunk.append(sentences[i])
    
    if current_chunk:
        chunks.append('. '.join(current_chunk) + '.')
    
    return chunks

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

### Parent-Child Chunking
```python
class ParentChildChunker:
    """Store large parent chunks for context, small child chunks for retrieval."""
    
    def chunk(self, text: str, parent_size: int = 2000, child_size: int = 200):
        words = text.split()
        parents = []
        children = []
        
        # Create parent chunks
        for i in range(0, len(words), parent_size):
            parent_text = ' '.join(words[i:i+parent_size])
            parent_id = f"parent_{i}"
            parents.append({"id": parent_id, "text": parent_text})
            
            # Create child chunks within this parent
            parent_words = parent_text.split()
            for j in range(0, len(parent_words), child_size):
                child_text = ' '.join(parent_words[j:j+child_size])
                children.append({
                    "id": f"child_{i}_{j}",
                    "parent_id": parent_id,
                    "text": child_text,
                })
        
        return parents, children
    
    def retrieve(self, query_vector, top_k: int = 3):
        """Search by child chunks, return parent chunks for context."""
        # Search using small child chunks (precise)
        child_results = vector_db.search(query_vector, collection="children", top_k=top_k * 2)
        
        # Get unique parent chunks (complete context)
        parent_ids = list(set(c["parent_id"] for c in child_results))
        parents = [get_parent(pid) for pid in parent_ids[:top_k]]
        
        return parents  # Return large context chunks to LLM
```

---

## 5. Qdrant Advanced Features

### Filtered Search
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range

client = QdrantClient(host="localhost", port=6333)

# Search with metadata filters
results = client.search(
    collection_name="documents",
    query_vector=embedding,
    limit=5,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="tenant_id",
                match=MatchValue(value="tenant_123"),
            ),
            FieldCondition(
                key="file_type",
                match=MatchValue(value="pdf"),
            ),
        ],
        should=[
            FieldCondition(
                key="created_at",
                range=Range(gte="2024-01-01"),
            ),
        ],
    ),
)
```

### Batch Upsert with Metadata
```python
from qdrant_client.models import PointStruct

def batch_upsert(chunks: list[dict], embeddings: list[list[float]]):
    """Upsert documents with rich metadata."""
    points = [
        PointStruct(
            id=chunk["id"],
            vector=embedding,
            payload={
                "text": chunk["text"],
                "source": chunk["source"],
                "page": chunk.get("page"),
                "chunk_index": chunk["index"],
                "tenant_id": chunk["tenant_id"],
                "file_type": chunk.get("file_type", "txt"),
                "created_at": chunk["created_at"],
                "word_count": len(chunk["text"].split()),
            },
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]
    
    # Batch upsert (100 at a time)
    batch_size = 100
    for i in range(0, len(points), batch_size):
        client.upsert(
            collection_name="documents",
            points=points[i:i+batch_size],
        )

# Create collection with proper config
client.create_collection(
    collection_name="documents",
    vectors_config={
        "size": 1536,          # Match embedding dimensions
        "distance": "Cosine",  # or "Dot" or "Euclid"
    },
    # Enable payload indexing for filtered search
    optimizers_config={
        "indexing_threshold": 20000,
    },
)

# Create payload indexes (faster filtered search)
client.create_payload_index(
    collection_name="documents",
    field_name="tenant_id",
    field_schema="keyword",
)
```

---

## Key Takeaways
1. **Reranking** with cross-encoders improves precision by 15-25% over embedding-only search
2. **Hybrid search** (dense + sparse) handles both semantic and keyword queries
3. **Chunking strategy** matters more than model choice for RAG quality
4. **Parent-child chunks**: Small chunks for retrieval, big chunks for context
5. **Embedding size**: Larger isn't always better — test truncated dimensions
6. **Always filter by tenant_id** in multi-tenant systems
