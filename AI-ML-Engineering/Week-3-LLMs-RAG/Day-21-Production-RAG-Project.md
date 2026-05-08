# Day 21: Project — Production RAG System

## Learning Objectives
- Build a complete production-grade RAG system end-to-end
- Implement multi-document ingestion with chunking comparison
- Add hybrid search with re-ranking
- Evaluate with RAGAS metrics
- Add streaming responses and conversation memory
- Deploy with FastAPI + Qdrant

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Production RAG System                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Ingestion Pipeline:                                         │
│  Documents → Loader → Chunker → Embedder → Qdrant           │
│                                                              │
│  Query Pipeline:                                             │
│  User Query → Rewriter → Hybrid Search → Re-ranker          │
│       → Context Builder → LLM → Streaming Response           │
│                                                              │
│  Conversation Memory:                                        │
│  Session → Chat History → Context-aware Queries              │
│                                                              │
│  Evaluation:                                                 │
│  RAGAS (faithfulness, relevancy, context precision/recall)   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Document Ingestion Pipeline

```python
import os
from pathlib import Path
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
import hashlib
import uuid

@dataclass
class Chunk:
    text: str
    metadata: dict
    chunk_id: str

class DocumentIngestion:
    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
        self.qdrant = QdrantClient(url=qdrant_url)
        self.collection_name = "production_rag"
        self._ensure_collection()
    
    def _ensure_collection(self):
        collections = [c.name for c in self.qdrant.get_collections().collections]
        if self.collection_name not in collections:
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE),
            )
    
    def load_documents(self, directory: str) -> list[dict]:
        """Load all supported files from directory."""
        docs = []
        for path in Path(directory).rglob("*"):
            if path.suffix in {".md", ".txt", ".py", ".rst"}:
                text = path.read_text(encoding="utf-8", errors="ignore")
                docs.append({"text": text, "source": str(path), "type": path.suffix})
        print(f"Loaded {len(docs)} documents")
        return docs
    
    def chunk_documents(self, docs: list[dict], strategy: str = "recursive") -> list[Chunk]:
        """Chunk documents with chosen strategy."""
        chunks = []
        
        if strategy == "recursive":
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=800, chunk_overlap=100,
                separators=["\n\n", "\n", ". ", " "]
            )
        elif strategy == "small":
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=400, chunk_overlap=50
            )
        
        for doc in docs:
            text_chunks = splitter.split_text(doc["text"])
            for i, text in enumerate(text_chunks):
                chunk_id = hashlib.md5(f"{doc['source']}_{i}".encode()).hexdigest()
                chunks.append(Chunk(
                    text=text,
                    metadata={"source": doc["source"], "type": doc["type"], "chunk_index": i},
                    chunk_id=chunk_id,
                ))
        
        print(f"Created {len(chunks)} chunks with '{strategy}' strategy")
        return chunks
    
    def embed_and_store(self, chunks: list[Chunk], batch_size: int = 128):
        """Embed chunks and store in Qdrant."""
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            texts = [c.text for c in batch]
            embeddings = self.embedder.encode(texts, show_progress_bar=False)
            
            points = [
                PointStruct(
                    id=str(uuid.uuid5(uuid.NAMESPACE_DNS, c.chunk_id)),
                    vector=emb.tolist(),
                    payload={"text": c.text, **c.metadata},
                )
                for c, emb in zip(batch, embeddings)
            ]
            self.qdrant.upsert(collection_name=self.collection_name, points=points)
        
        print(f"Stored {len(chunks)} chunks in Qdrant")
    
    def ingest(self, directory: str, strategy: str = "recursive"):
        """Full ingestion pipeline."""
        docs = self.load_documents(directory)
        chunks = self.chunk_documents(docs, strategy)
        self.embed_and_store(chunks)
        return len(chunks)
```

---

## 3. Hybrid Search with Re-Ranking

```python
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
import numpy as np

class HybridSearchEngine:
    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.qdrant = QdrantClient(url=qdrant_url)
        self.collection_name = "production_rag"
        self._build_bm25_index()
    
    def _build_bm25_index(self):
        """Build BM25 index from stored documents."""
        # Scroll all documents from Qdrant
        all_points = []
        offset = None
        while True:
            results, offset = self.qdrant.scroll(
                collection_name=self.collection_name, limit=1000, offset=offset
            )
            all_points.extend(results)
            if offset is None:
                break
        
        self.documents = [(p.id, p.payload["text"], p.payload) for p in all_points]
        tokenized = [doc[1].lower().split() for doc in self.documents]
        self.bm25 = BM25Okapi(tokenized)
    
    def dense_search(self, query: str, top_k: int = 50) -> list[tuple]:
        """Vector similarity search."""
        query_emb = self.embedder.encode(query)
        results = self.qdrant.search(
            collection_name=self.collection_name,
            query_vector=query_emb.tolist(),
            limit=top_k,
        )
        return [(r.payload["text"], r.score, r.payload) for r in results]
    
    def sparse_search(self, query: str, top_k: int = 50) -> list[tuple]:
        """BM25 keyword search."""
        scores = self.bm25.get_scores(query.lower().split())
        top_indices = np.argsort(scores)[-top_k:][::-1]
        return [
            (self.documents[i][1], scores[i], self.documents[i][2])
            for i in top_indices if scores[i] > 0
        ]
    
    def hybrid_search(self, query: str, top_k: int = 10, alpha: float = 0.7):
        """Combine dense + sparse with RRF, then re-rank."""
        dense_results = self.dense_search(query, top_k=50)
        sparse_results = self.sparse_search(query, top_k=50)
        
        # Reciprocal Rank Fusion
        scores = {}
        k = 60
        for rank, (text, _, meta) in enumerate(dense_results):
            key = text[:100]  # Use text prefix as key
            scores[key] = scores.get(key, {"score": 0, "text": text, "meta": meta})
            scores[key]["score"] += alpha / (k + rank + 1)
        
        for rank, (text, _, meta) in enumerate(sparse_results):
            key = text[:100]
            scores[key] = scores.get(key, {"score": 0, "text": text, "meta": meta})
            scores[key]["score"] += (1 - alpha) / (k + rank + 1)
        
        # Get top candidates
        candidates = sorted(scores.values(), key=lambda x: x["score"], reverse=True)[:30]
        
        # Re-rank with cross-encoder
        pairs = [(query, c["text"]) for c in candidates]
        rerank_scores = self.reranker.predict(pairs)
        
        reranked = sorted(
            zip(candidates, rerank_scores), key=lambda x: x[1], reverse=True
        )
        return [(c["text"], score, c["meta"]) for c, score in reranked[:top_k]]
```

---

## 4. Generation with Streaming & Memory

```python
from openai import OpenAI
from collections import deque

class ConversationRAG:
    def __init__(self, search_engine: HybridSearchEngine):
        self.search = search_engine
        self.client = OpenAI()
        self.sessions: dict[str, deque] = {}  # session_id → chat history
        self.max_history = 10
    
    def _get_history(self, session_id: str) -> list[dict]:
        if session_id not in self.sessions:
            self.sessions[session_id] = deque(maxlen=self.max_history)
        return list(self.sessions[session_id])
    
    def _add_to_history(self, session_id: str, role: str, content: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = deque(maxlen=self.max_history)
        self.sessions[session_id].append({"role": role, "content": content})
    
    def _rewrite_with_context(self, query: str, history: list[dict]) -> str:
        """Rewrite query using conversation context (resolve pronouns, etc.)."""
        if not history:
            return query
        
        history_text = "\n".join(f"{m['role']}: {m['content']}" for m in history[-4:])
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Rewrite the user's query to be self-contained, resolving any pronouns or references from chat history. Return only the rewritten query."},
                {"role": "user", "content": f"Chat history:\n{history_text}\n\nLatest query: {query}"}
            ],
            temperature=0,
        )
        return response.choices[0].message.content
    
    def query_stream(self, question: str, session_id: str = "default"):
        """Full RAG pipeline with streaming response."""
        # Get history and rewrite query
        history = self._get_history(session_id)
        rewritten_query = self._rewrite_with_context(question, history)
        
        # Retrieve relevant documents
        results = self.search.hybrid_search(rewritten_query, top_k=5)
        context = "\n\n---\n\n".join(f"[Source: {r[2].get('source', 'unknown')}]\n{r[0]}" for r in results)
        
        # Build messages
        messages = [
            {"role": "system", "content": """You are a helpful assistant that answers questions based on the provided context.

Rules:
- Answer ONLY from the provided context
- If context doesn't contain the answer, say so clearly
- Cite sources when possible [Source: filename]
- Be concise and accurate"""},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
        
        # Stream response
        stream = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0,
            stream=True,
        )
        
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content
                full_response += token
                yield token
        
        # Save to history
        self._add_to_history(session_id, "user", question)
        self._add_to_history(session_id, "assistant", full_response)
```

---

## 5. FastAPI Deployment

```python
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Production RAG API")

# Initialize components
ingestion = DocumentIngestion()
search_engine = HybridSearchEngine()
rag = ConversationRAG(search_engine)

class QueryRequest(BaseModel):
    question: str
    session_id: str = "default"
    top_k: int = 5

class IngestRequest(BaseModel):
    directory: str
    strategy: str = "recursive"

@app.post("/ingest")
async def ingest_documents(request: IngestRequest):
    """Ingest documents from a directory."""
    num_chunks = ingestion.ingest(request.directory, request.strategy)
    # Rebuild BM25 index after ingestion
    search_engine._build_bm25_index()
    return {"status": "success", "chunks_created": num_chunks}

@app.post("/query")
async def query(request: QueryRequest):
    """Query with full RAG pipeline (non-streaming)."""
    response_text = ""
    for token in rag.query_stream(request.question, request.session_id):
        response_text += token
    return {"answer": response_text, "session_id": request.session_id}

@app.post("/query/stream")
async def query_stream(request: QueryRequest):
    """Query with streaming response."""
    def generate():
        for token in rag.query_stream(request.question, request.session_id):
            yield token
    
    return StreamingResponse(generate(), media_type="text/plain")

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 6. RAGAS Evaluation

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness, answer_relevancy, 
    context_precision, context_recall
)
from datasets import Dataset

class RAGEvaluator:
    def __init__(self, rag_system: ConversationRAG):
        self.rag = rag_system
    
    def create_test_set(self) -> list[dict]:
        """Define test questions with ground truth."""
        return [
            {
                "question": "What is the refund policy?",
                "ground_truth": "Full refund within 30 days of purchase for unused items.",
            },
            {
                "question": "How do I reset my password?",
                "ground_truth": "Go to Settings > Security > Reset Password, enter email for verification link.",
            },
            # Add 10+ test cases for reliable evaluation
        ]
    
    def run_evaluation(self) -> dict:
        """Run full RAGAS evaluation."""
        test_set = self.create_test_set()
        
        questions, answers, contexts, ground_truths = [], [], [], []
        
        for test in test_set:
            # Get RAG answer
            response = ""
            for token in self.rag.query_stream(test["question"]):
                response += token
            
            # Get retrieved contexts
            results = self.rag.search.hybrid_search(test["question"], top_k=5)
            retrieved_contexts = [r[0] for r in results]
            
            questions.append(test["question"])
            answers.append(response)
            contexts.append(retrieved_contexts)
            ground_truths.append(test["ground_truth"])
        
        # Build RAGAS dataset
        dataset = Dataset.from_dict({
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        })
        
        # Evaluate
        results = evaluate(
            dataset,
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        )
        
        print(f"Faithfulness:      {results['faithfulness']:.3f}")
        print(f"Answer Relevancy:  {results['answer_relevancy']:.3f}")
        print(f"Context Precision: {results['context_precision']:.3f}")
        print(f"Context Recall:    {results['context_recall']:.3f}")
        return results

# Chunking comparison experiment
def compare_chunking_strategies(directory: str):
    """Compare different chunking strategies on same test set."""
    strategies = ["recursive", "small"]
    results = {}
    
    for strategy in strategies:
        ingestion.ingest(directory, strategy=strategy)
        search_engine._build_bm25_index()
        evaluator = RAGEvaluator(rag)
        results[strategy] = evaluator.run_evaluation()
    
    # Print comparison
    for strategy, metrics in results.items():
        print(f"\n{strategy}:")
        for metric, score in metrics.items():
            print(f"  {metric}: {score:.3f}")
```

---

## 7. Production Checklist

```yaml
# Deployment checklist for production RAG:

Infrastructure:
  - [ ] Qdrant deployed (Docker/Cloud) with persistence
  - [ ] FastAPI with gunicorn/uvicorn workers
  - [ ] Redis for session/embedding cache
  - [ ] Monitoring (Prometheus + Grafana)

Quality:
  - [ ] RAGAS evaluation ≥ 0.8 on test set
  - [ ] Chunking strategy validated
  - [ ] Re-ranker improves top-5 precision
  - [ ] Conversation context resolves pronouns correctly

Performance:
  - [ ] P95 latency < 3s (retrieval + generation)
  - [ ] Embedding cache hit rate > 60%
  - [ ] Vector DB handles expected document count
  - [ ] Streaming enabled for user experience

Safety:
  - [ ] Input validation (max query length)
  - [ ] Rate limiting per session
  - [ ] No prompt injection via documents
  - [ ] "I don't know" when context insufficient
  - [ ] Source citations for verifiability

Maintenance:
  - [ ] Incremental ingestion (add docs without rebuilding)
  - [ ] Stale document detection and removal
  - [ ] Evaluation runs on schedule (detect degradation)
  - [ ] User feedback loop (thumbs up/down → improve retrieval)
```

---

## Interview Questions

### Beginner
1. **What are the key components of a production RAG system?** Document ingestion (loading, chunking, embedding, storing), retrieval (search, filtering), generation (LLM with context), and evaluation (RAGAS metrics). Also: caching, conversation memory, streaming, monitoring.
2. **Why use streaming responses in RAG?** LLM generation takes 2-10 seconds. Without streaming, user waits with no feedback. Streaming shows tokens as generated — perceived latency drops dramatically. Implementation: SSE or WebSocket from FastAPI, yield tokens from OpenAI stream.
3. **How do you handle conversation context in RAG?** Store chat history per session. Before retrieval, rewrite user's query to be self-contained (resolve "it", "that", pronouns using history). Pass rewritten query to retrieval. Keep last N turns to avoid context overflow.

### Intermediate
4. **How do you compare chunking strategies?** Fixed test set with questions + ground truth answers. Ingest same docs with different strategies. Measure: retrieval precision (right chunks found?), RAGAS scores (good answers generated?), chunk count (affects cost/speed). Usually: recursive with 500-1000 chars + 10-20% overlap wins.
5. **Explain the two-stage retrieval + re-ranking approach.** Stage 1: Fast retrieval (bi-encoder + BM25 hybrid) returns top-50 candidates. Stage 2: Cross-encoder scores each (query, candidate) pair — more accurate but slower. Return top-5 after re-ranking. Typical improvement: 15-30% better precision vs retrieval alone.
6. **How do you evaluate RAG systems comprehensively?** Component-level: retrieval metrics (precision@K, recall@K). End-to-end: RAGAS (faithfulness, relevancy, context precision/recall). User-level: satisfaction surveys, thumbs up/down. Regression: automated test suite run on every change.

### Advanced
7. **How do you prevent prompt injection via ingested documents?** Documents might contain "Ignore previous instructions..." Mitigations: sanitize special characters, use XML/delimiter tags to clearly separate context from instructions, instruction hierarchy (system > context > user), monitor outputs for unexpected behavior, red-team test with adversarial docs.
8. **Design incremental ingestion for a constantly updating knowledge base.** Hash documents to detect changes. On update: re-chunk changed doc, delete old vectors (by source metadata), embed and insert new chunks. Rebuild BM25 index periodically. Use versioning: keep old + new during transition, atomic swap. Handle: additions, deletions, modifications.
9. **How would you scale this system to 10M documents and 1000 QPS?** Qdrant cluster (sharded, replicated). Separate read replicas for search. Embedding inference: GPU batch server. Cache: frequent queries in Redis. Load balance: multiple FastAPI instances. Async ingestion queue (Kafka/RabbitMQ). CDN for static assets. Rate limit per user.

---

## Hands-On Exercise
1. Set up Qdrant (Docker), ingest 20+ documents from a directory
2. Implement hybrid search (BM25 + dense) with cross-encoder re-ranking
3. Compare 2 chunking strategies using RAGAS metrics
4. Add conversation memory — test multi-turn queries with pronoun resolution
5. Deploy as FastAPI with streaming endpoint
6. Create evaluation test suite (10+ questions) and run RAGAS
7. Load test: measure P95 latency with 10 concurrent users
