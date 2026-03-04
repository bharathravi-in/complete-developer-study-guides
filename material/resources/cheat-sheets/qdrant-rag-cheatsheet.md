# Qdrant & RAG Cheat Sheet

## Qdrant Setup
```bash
# Run Qdrant
docker run -p 6333:6333 qdrant/qdrant

# Python client
pip install qdrant-client
```

## Qdrant Operations
```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(host="localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# Insert vectors
client.upsert(
    collection_name="documents",
    points=[
        PointStruct(
            id=1,
            vector=[0.1, 0.2, ...],  # 384 dims
            payload={"text": "chunk text", "doc_id": "abc", "page": 1}
        )
    ]
)

# Search
results = client.search(
    collection_name="documents",
    query_vector=[0.1, 0.2, ...],
    limit=5,
    score_threshold=0.7,
)

# Search with filter
from qdrant_client.models import Filter, FieldCondition, MatchValue
results = client.search(
    collection_name="documents",
    query_vector=embedding,
    query_filter=Filter(must=[
        FieldCondition(key="doc_id", match=MatchValue(value="abc"))
    ]),
    limit=5,
)

# Delete
client.delete(
    collection_name="documents",
    points_selector=[1, 2, 3],  # Point IDs
)

# Collection info
info = client.get_collection("documents")
print(info.points_count)
```

## Embedding Generation
```python
# OpenAI
from openai import OpenAI
client = OpenAI()
response = client.embeddings.create(input="text", model="text-embedding-3-small")
vector = response.data[0].embedding  # 1536 dims

# Sentence Transformers (free, local)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
vector = model.encode("text").tolist()  # 384 dims

# Batch
vectors = model.encode(["text1", "text2", "text3"]).tolist()
```

## Cosine Similarity
```python
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

## RAG Pipeline
```python
# 1. CHUNK
def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

# 2. EMBED + STORE
chunks = chunk_text(document_text)
embeddings = model.encode(chunks)
points = [
    PointStruct(id=i, vector=emb.tolist(), payload={"text": chunk, "doc_id": doc_id})
    for i, (chunk, emb) in enumerate(zip(chunks, embeddings))
]
client.upsert("documents", points)

# 3. RETRIEVE
query_embedding = model.encode(user_query).tolist()
results = client.search("documents", query_vector=query_embedding, limit=5)
context = "\n".join([r.payload["text"] for r in results])

# 4. GENERATE
prompt = f"""Answer based ONLY on the context below.

Context:
{context}

Question: {user_query}

Answer:"""

response = openai_client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    temperature=0,
)
answer = response.choices[0].message.content
```

## Key Numbers
```
Embedding Models:
  all-MiniLM-L6-v2    → 384 dims, free, fast
  text-embedding-3-small → 1536 dims, $0.02/1M tokens
  text-embedding-3-large → 3072 dims, $0.13/1M tokens

Qdrant Capacity (single node):
  1M vectors × 384 dims = ~1.5 GB RAM
  1M vectors × 1536 dims = ~6 GB RAM

Chunk Sizes:
  Small (200 words)  → precise retrieval, less context
  Medium (500 words) → balanced (RECOMMENDED)
  Large (1000 words) → more context, less precise

Overlap: 10-20% of chunk size
Top-K: 3-10 results (5 is common default)
Score threshold: 0.7+ for high quality
```
