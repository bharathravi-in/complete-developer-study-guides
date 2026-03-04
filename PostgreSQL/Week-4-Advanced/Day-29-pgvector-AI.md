# Day 29: pgvector & AI Integration

## 📚 Learning Objectives
- Understand vector embeddings
- Master pgvector extension
- Build semantic search systems
- Implement RAG (Retrieval-Augmented Generation)

---

## 1. Vector Embeddings Fundamentals

### What are Embeddings?

```
Text: "PostgreSQL is a powerful database"
          ↓
     Embedding Model (OpenAI, Sentence Transformers)
          ↓
Vector: [0.02, -0.15, 0.89, ..., 0.34]  (1536 dimensions for ada-002)

Semantically similar text → Similar vectors
"MySQL is a database system" → [0.03, -0.12, 0.85, ..., 0.31]

Vector distance measures similarity:
- Cosine similarity (most common)
- Euclidean distance
- Inner product
```

### Use Cases

```
Semantic Search:
  User: "good restaurants nearby"
  Match: "best dining spots in the area" (different words, same meaning)

Recommendation:
  User likes A, B, C → Find items with similar vectors

RAG (ChatGPT + Your Data):
  1. User asks question
  2. Find relevant documents by vector similarity
  3. Send documents + question to LLM
  4. LLM generates answer using your data
```

---

## 2. pgvector Setup

### Installation

```bash
# Ubuntu/Debian
sudo apt install postgresql-16-pgvector

# From source
cd /tmp
git clone --branch v0.6.0 https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

```sql
-- Enable extension
CREATE EXTENSION vector;
```

### Basic Operations

```sql
-- Create table with vector column
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(1536)  -- OpenAI ada-002 dimension
);

-- Insert vector
INSERT INTO documents (content, embedding) VALUES
('PostgreSQL is great', '[0.1, 0.2, 0.3, ...]'::vector);

-- Vector from array
INSERT INTO documents (content, embedding) VALUES
('Another document', ARRAY[0.1, 0.2, 0.3, ...]::vector(1536));
```

---

## 3. Vector Distance Operators

### Similarity Measures

```sql
-- L2 distance (Euclidean) - smaller = more similar
SELECT * FROM documents
ORDER BY embedding <-> '[0.1, 0.2, ...]'::vector
LIMIT 5;

-- Inner product (negative) - smaller = more similar
SELECT * FROM documents
ORDER BY embedding <#> '[0.1, 0.2, ...]'::vector
LIMIT 5;

-- Cosine distance - smaller = more similar (0 = identical)
SELECT * FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;

-- Cosine similarity (1 - cosine distance)
SELECT 
    content,
    1 - (embedding <=> '[0.1, 0.2, ...]'::vector) AS similarity
FROM documents
ORDER BY similarity DESC
LIMIT 5;
```

### Distance Functions

```sql
-- L2 distance
SELECT l2_distance(embedding, '[0.1, ...]'::vector) FROM documents;

-- Inner product
SELECT inner_product(embedding, '[0.1, ...]'::vector) FROM documents;

-- Cosine distance  
SELECT cosine_distance(embedding, '[0.1, ...]'::vector) FROM documents;

-- Vector dimensions
SELECT vector_dims(embedding) FROM documents LIMIT 1;

-- Vector norm
SELECT vector_norm(embedding) FROM documents LIMIT 1;
```

---

## 4. Indexing Vectors

### IVFFlat Index

```sql
-- IVFFlat: Inverted File with Flat compression
-- Good balance of speed and recall

-- Create index
CREATE INDEX ON documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);  -- Number of clusters

-- Index operators:
-- vector_l2_ops      - L2 distance (<->)
-- vector_ip_ops      - Inner product (<#>)
-- vector_cosine_ops  - Cosine distance (<=>)

-- Tuning: lists ≈ sqrt(rows) for small datasets
-- lists ≈ rows/1000 for large datasets

-- Set probes for query (higher = better recall, slower)
SET ivfflat.probes = 10;  -- Default is 1
```

### HNSW Index

```sql
-- HNSW: Hierarchical Navigable Small World
-- Better recall, more memory, slower build

CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- m: Max connections per node (default 16)
-- ef_construction: Build-time search scope (default 64)

-- Query-time parameter
SET hnsw.ef_search = 40;  -- Higher = better recall
```

### Index Comparison

| Feature | IVFFlat | HNSW |
|---------|---------|------|
| Build speed | Fast | Slow |
| Query speed | Fast | Faster |
| Recall | Good | Better |
| Memory | Low | High |
| Updates | Requires rebuild | Supports updates |

---

## 5. Generating Embeddings

### Python with OpenAI

```python
import psycopg2
import openai
from openai import OpenAI

client = OpenAI(api_key="your-key")

def get_embedding(text: str) -> list[float]:
    """Generate embedding using OpenAI ada-002"""
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

# Store document with embedding
def store_document(content: str):
    embedding = get_embedding(content)
    
    conn = psycopg2.connect("dbname=mydb")
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
            (content, embedding)
        )
    conn.commit()

# Semantic search
def search(query: str, limit: int = 5):
    query_embedding = get_embedding(query)
    
    conn = psycopg2.connect("dbname=mydb")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT content, 1 - (embedding <=> %s::vector) AS similarity
            FROM documents
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, query_embedding, limit))
        
        return cur.fetchall()
```

### Local Embeddings (Sentence Transformers)

```python
from sentence_transformers import SentenceTransformer

# Load model (runs locally)
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions

def get_local_embedding(text: str) -> list[float]:
    embedding = model.encode(text)
    return embedding.tolist()

# Table with smaller dimension
# CREATE TABLE documents (
#     id SERIAL PRIMARY KEY,
#     content TEXT,
#     embedding VECTOR(384)
# );
```

---

## 6. RAG Implementation

### Schema for RAG

```sql
CREATE TABLE knowledge_base (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100),        -- File name, URL, etc.
    chunk_index INTEGER,        -- Position in source
    content TEXT NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ON knowledge_base 
USING hnsw (embedding vector_cosine_ops);

CREATE INDEX ON knowledge_base (source);
```

### Document Chunking

```python
def chunk_document(text: str, chunk_size: int = 500, overlap: int = 50):
    """Split document into overlapping chunks"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind('.')
            if last_period > chunk_size * 0.5:
                chunk = chunk[:last_period + 1]
                end = start + last_period + 1
        
        chunks.append({
            'content': chunk.strip(),
            'start_index': start,
            'end_index': end
        })
        
        start = end - overlap
    
    return chunks

def ingest_document(source: str, content: str):
    """Process and store document chunks"""
    chunks = chunk_document(content)
    
    conn = psycopg2.connect("dbname=mydb")
    with conn.cursor() as cur:
        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk['content'])
            cur.execute("""
                INSERT INTO knowledge_base 
                (source, chunk_index, content, embedding, metadata)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                source, 
                i, 
                chunk['content'],
                embedding,
                json.dumps({'start': chunk['start_index'], 'end': chunk['end_index']})
            ))
    conn.commit()
```

### RAG Query

```python
def rag_query(question: str, k: int = 5):
    """Retrieve relevant context and generate answer"""
    
    # 1. Get question embedding
    query_embedding = get_embedding(question)
    
    # 2. Find relevant chunks
    conn = psycopg2.connect("dbname=mydb")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT content, source, 
                   1 - (embedding <=> %s::vector) AS similarity
            FROM knowledge_base
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, query_embedding, k))
        
        results = cur.fetchall()
    
    # 3. Build context
    context = "\n\n".join([
        f"[Source: {r[1]}]\n{r[0]}" 
        for r in results
    ])
    
    # 4. Generate answer with LLM
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": """Answer based on the provided context. 
             If the context doesn't contain relevant information, say so."""},
            {"role": "user", "content": f"""Context:\n{context}\n\nQuestion: {question}"""}
        ]
    )
    
    return {
        'answer': response.choices[0].message.content,
        'sources': [r[1] for r in results],
        'similarities': [r[2] for r in results]
    }
```

---

## 7. Advanced Patterns

### Hybrid Search (Vector + Full-Text)

```sql
-- Combine semantic and keyword search
WITH semantic_results AS (
    SELECT id, content, 
           1 - (embedding <=> $1::vector) AS semantic_score
    FROM knowledge_base
    ORDER BY embedding <=> $1::vector
    LIMIT 20
),
keyword_results AS (
    SELECT id, content,
           ts_rank(to_tsvector('english', content), 
                   websearch_to_tsquery('english', $2)) AS keyword_score
    FROM knowledge_base
    WHERE to_tsvector('english', content) @@ websearch_to_tsquery('english', $2)
    LIMIT 20
)
SELECT 
    COALESCE(s.id, k.id) AS id,
    COALESCE(s.content, k.content) AS content,
    COALESCE(s.semantic_score, 0) * 0.7 + 
    COALESCE(k.keyword_score, 0) * 0.3 AS combined_score
FROM semantic_results s
FULL OUTER JOIN keyword_results k ON s.id = k.id
ORDER BY combined_score DESC
LIMIT 10;
```

### Metadata Filtering

```sql
-- Pre-filter before vector search
SELECT content, 1 - (embedding <=> $1::vector) AS similarity
FROM knowledge_base
WHERE metadata->>'category' = 'technical'
AND created_at > now() - INTERVAL '30 days'
ORDER BY embedding <=> $1::vector
LIMIT 5;

-- Create partial index for common filters
CREATE INDEX ON knowledge_base USING hnsw (embedding vector_cosine_ops)
WHERE metadata->>'category' = 'technical';
```

### Batch Operations

```python
# Batch insert for efficiency
def batch_store(documents: list[dict]):
    embeddings = model.encode([d['content'] for d in documents])
    
    with conn.cursor() as cur:
        args = [(d['content'], e.tolist()) for d, e in zip(documents, embeddings)]
        cur.executemany(
            "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
            args
        )
    conn.commit()
```

---

## 📝 Key Takeaways

1. **pgvector enables AI in PostgreSQL** - Native vector operations
2. **HNSW for production** - Best recall, supports updates
3. **Chunk documents properly** - 500-1000 tokens, with overlap
4. **Hybrid search improves results** - Combine vector + keyword
5. **RAG grounds LLMs** - Prevents hallucination with your data

---

## ✅ Day 29 Checklist

- [ ] Install pgvector extension
- [ ] Create table with vector column
- [ ] Generate embeddings (OpenAI or local)
- [ ] Implement semantic search
- [ ] Create HNSW index
- [ ] Build RAG pipeline
- [ ] Try hybrid search
