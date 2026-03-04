# Qdrant Vector Database - Complete Guide

## What is Qdrant?

Qdrant = A vector database optimized for storing and searching embeddings.

**Why not just use PostgreSQL?**
- PostgreSQL: great for structured data, terrible for similarity search
- Qdrant: optimized for finding nearest vectors (semantic search)
- A 1M document search that takes 10 seconds in PostgreSQL takes 10ms in Qdrant

---

## 1. Setup

```bash
# Docker (recommended)
docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant

# Or with persistent storage
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant

# Python client
pip install qdrant-client
```

## 2. Core Concepts

```
Collection = Table (in SQL terms)
    ├── Points = Rows
    │   ├── ID (unique identifier)
    │   ├── Vector (embedding - list of floats)
    │   └── Payload (metadata - like JSON fields)
    └── Index (for fast search)
```

| SQL Concept | Qdrant Equivalent |
|------------|-------------------|
| Table | Collection |
| Row | Point |
| Column | Payload field |
| Primary Key | Point ID |
| SELECT WHERE | Filtering |
| ORDER BY similarity | Search |

---

## 3. Basic Operations

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue, Range,
    UpdateStatus
)

# Connect
client = QdrantClient(host="localhost", port=6333)
# Or in-memory (for testing)
# client = QdrantClient(":memory:")

# ========== CREATE COLLECTION ==========
client.recreate_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=384,           # Must match your embedding dimensions!
        distance=Distance.COSINE  # COSINE, DOT, EUCLID
    )
)

# ========== INSERT POINTS ==========
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

documents = [
    {"text": "Python is a programming language", "category": "tech", "source": "wiki"},
    {"text": "Machine learning uses algorithms", "category": "ai", "source": "textbook"},
    {"text": "Flask is a web framework", "category": "tech", "source": "docs"},
    {"text": "RAG combines retrieval and generation", "category": "ai", "source": "paper"},
    {"text": "Redis is a caching system", "category": "tech", "source": "docs"},
]

# Generate embeddings
texts = [doc["text"] for doc in documents]
embeddings = model.encode(texts).tolist()

# Create points
points = [
    PointStruct(
        id=i,
        vector=embedding,
        payload=doc  # Any JSON-serializable data
    )
    for i, (embedding, doc) in enumerate(zip(embeddings, documents))
]

# Upsert (insert or update)
client.upsert(
    collection_name="documents",
    points=points
)
print(f"Inserted {len(points)} points")

# ========== SEARCH ==========
query = "How do neural networks learn?"
query_embedding = model.encode(query).tolist()

results = client.search(
    collection_name="documents",
    query_vector=query_embedding,
    limit=3  # Top 3 results
)

for result in results:
    print(f"Score: {result.score:.4f} | {result.payload['text']}")

# ========== SEARCH WITH FILTERS ==========
results = client.search(
    collection_name="documents",
    query_vector=query_embedding,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="category",
                match=MatchValue(value="ai")
            )
        ]
    ),
    limit=3
)

# ========== GET POINT BY ID ==========
point = client.retrieve(
    collection_name="documents",
    ids=[0, 1],
    with_payload=True,
    with_vectors=False  # Don't return large vectors
)

# ========== UPDATE PAYLOAD ==========
client.set_payload(
    collection_name="documents",
    payload={"updated": True, "version": 2},
    points=[0]  # Point IDs to update
)

# ========== DELETE POINTS ==========
client.delete(
    collection_name="documents",
    points_selector=[0, 1]  # Delete by IDs
)

# ========== COLLECTION INFO ==========
info = client.get_collection("documents")
print(f"Points: {info.points_count}")
print(f"Vectors: {info.vectors_count}")
```

---

## 4. Advanced Filtering

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue, Range, MatchAny

# Exact match
filter_exact = Filter(
    must=[
        FieldCondition(key="category", match=MatchValue(value="ai"))
    ]
)

# Multiple values (IN clause)
filter_in = Filter(
    must=[
        FieldCondition(key="category", match=MatchAny(any=["ai", "tech"]))
    ]
)

# Range filter
filter_range = Filter(
    must=[
        FieldCondition(key="score", range=Range(gte=0.5, lte=1.0))
    ]
)

# NOT filter
filter_not = Filter(
    must_not=[
        FieldCondition(key="source", match=MatchValue(value="wiki"))
    ]
)

# Combined (AND + OR)
filter_combined = Filter(
    must=[
        FieldCondition(key="category", match=MatchValue(value="ai")),
    ],
    should=[  # OR conditions
        FieldCondition(key="source", match=MatchValue(value="paper")),
        FieldCondition(key="source", match=MatchValue(value="textbook")),
    ]
)

# Use in search
results = client.search(
    collection_name="documents",
    query_vector=query_embedding,
    query_filter=filter_combined,
    limit=5
)
```

---

## 5. Indexing for Performance

```python
# Create payload indexes for fast filtering
client.create_payload_index(
    collection_name="documents",
    field_name="category",
    field_schema="keyword"  # keyword, integer, float, geo, datetime
)

client.create_payload_index(
    collection_name="documents",
    field_name="source",
    field_schema="keyword"
)

client.create_payload_index(
    collection_name="documents",
    field_name="created_at",
    field_schema="datetime"
)
```

---

## 6. Production Qdrant Service

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue,
    UpdateStatus
)
from sentence_transformers import SentenceTransformer
from dataclasses import dataclass
from typing import Optional
import logging
import uuid

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    id: str
    text: str
    score: float
    metadata: dict

class VectorDBService:
    """Production-ready Qdrant service."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection_name: str = "documents",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = collection_name
        self.model = SentenceTransformer(embedding_model)
        self.dimensions = self.model.get_sentence_embedding_dimension()
    
    def create_collection(self, recreate: bool = False):
        """Create or recreate the collection."""
        collections = [c.name for c in self.client.get_collections().collections]
        
        if self.collection_name in collections:
            if recreate:
                self.client.delete_collection(self.collection_name)
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                return
        
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=VectorParams(
                size=self.dimensions,
                distance=Distance.COSINE
            )
        )
        
        # Create indexes
        self.client.create_payload_index(
            self.collection_name, "category", "keyword"
        )
        self.client.create_payload_index(
            self.collection_name, "source", "keyword"
        )
        
        logger.info(f"Created collection: {self.collection_name}")
    
    def add_documents(
        self,
        texts: list[str],
        metadata: Optional[list[dict]] = None,
        batch_size: int = 100,
    ) -> int:
        """Add documents to the collection."""
        if metadata is None:
            metadata = [{}] * len(texts)
        
        total_added = 0
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_meta = metadata[i:i + batch_size]
            
            # Generate embeddings
            embeddings = self.model.encode(batch_texts).tolist()
            
            # Create points
            points = []
            for j, (text, embedding, meta) in enumerate(
                zip(batch_texts, embeddings, batch_meta)
            ):
                point_id = str(uuid.uuid4())
                payload = {
                    "text": text,
                    "char_count": len(text),
                    "word_count": len(text.split()),
                    **meta
                }
                points.append(PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload
                ))
            
            # Upsert batch
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            total_added += len(points)
            logger.info(f"Added batch {i//batch_size + 1}: {len(points)} documents")
        
        return total_added
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0,
        category: Optional[str] = None,
        source: Optional[str] = None,
    ) -> list[SearchResult]:
        """Search for similar documents."""
        # Generate query embedding
        query_embedding = self.model.encode(query).tolist()
        
        # Build filter
        filter_conditions = []
        if category:
            filter_conditions.append(
                FieldCondition(key="category", match=MatchValue(value=category))
            )
        if source:
            filter_conditions.append(
                FieldCondition(key="source", match=MatchValue(value=source))
            )
        
        query_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=query_filter,
            limit=top_k,
            score_threshold=score_threshold,
        )
        
        return [
            SearchResult(
                id=str(r.id),
                text=r.payload.get("text", ""),
                score=r.score,
                metadata={k: v for k, v in r.payload.items() if k != "text"}
            )
            for r in results
        ]
    
    def delete_documents(self, ids: list[str]):
        """Delete documents by ID."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=ids
        )
    
    def get_stats(self) -> dict:
        """Get collection statistics."""
        info = self.client.get_collection(self.collection_name)
        return {
            "collection": self.collection_name,
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "status": info.status,
            "dimensions": self.dimensions,
        }


# Usage
db = VectorDBService()
db.create_collection(recreate=True)

# Add documents
texts = [
    "Machine learning is a subset of artificial intelligence",
    "Deep learning uses neural networks with many layers",
    "Natural language processing handles human language",
    "Computer vision processes and analyzes images",
    "Reinforcement learning learns through trial and error",
]
metadata = [
    {"category": "ai", "source": "textbook"},
    {"category": "ai", "source": "paper"},
    {"category": "ai", "source": "textbook"},
    {"category": "ai", "source": "paper"},
    {"category": "ai", "source": "textbook"},
]

db.add_documents(texts, metadata)

# Search
results = db.search("How do machines learn from data?", top_k=3)
for r in results:
    print(f"Score: {r.score:.4f} | {r.text}")

# Filter search
results = db.search("neural networks", category="ai", source="paper")
```

---

## 7. Qdrant vs Other Vector DBs

| Feature | Qdrant | Pinecone | Weaviate | ChromaDB |
|---------|--------|----------|----------|----------|
| Self-hosted | ✅ | ❌ (cloud only) | ✅ | ✅ |
| Cloud | ✅ | ✅ | ✅ | ✅ |
| Filtering | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Performance | Fast | Fast | Medium | Slow |
| Free tier | Unlimited | Limited | Unlimited | Unlimited |
| Python SDK | Great | Great | Good | Great |
| Best for | Production | Quick start | GraphQL fans | Prototyping |

---

## Exercises

### Exercise 1: Build a Document Search System
```python
# Build a system that:
# 1. Reads .txt files from a directory
# 2. Chunks them into 500-word segments
# 3. Stores chunks in Qdrant with file metadata
# 4. Provides search API with category filtering
# 5. Returns results with source file info

# TODO: Implement
```

### Exercise 2: Build a Similar Items Recommender
```python
# Given an e-commerce product catalog:
# 1. Store products with embeddings from descriptions
# 2. Given a product ID, find similar products
# 3. Filter by category and price range
# 4. Exclude the query product from results

# TODO: Implement
```

---

## Key Takeaways
1. **Qdrant** = optimized for vector similarity search
2. **Collection** = table, **Point** = row with vector + payload
3. Always **batch** inserts for performance
4. Use **payload indexes** for filter fields
5. **COSINE** distance is standard for text embeddings
6. Score threshold helps filter low-quality results
7. Self-hosted = free and fast
