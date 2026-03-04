# RAG (Retrieval-Augmented Generation) - Complete Guide

## What is RAG?

RAG = Instead of asking an LLM to answer from memory, we RETRIEVE relevant documents first, then send them as context to the LLM.

```
Without RAG:
  User Question → LLM → Answer (might hallucinate)

With RAG:
  User Question → Search Vector DB → Get Relevant Docs → Send Docs + Question to LLM → Accurate Answer
```

**This is THE core skill for an AI Engineer.**

---

## The RAG Pipeline

```
┌──────────────────── INDEXING PHASE ────────────────────┐
│                                                         │
│  Documents → Chunk → Embed → Store in Vector DB         │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌──────────────────── QUERY PHASE ──────────────────────┐
│                                                        │
│  Query → Embed → Search Vector DB → Get Top-K Chunks   │
│    → Build Prompt (context + question)                  │
│    → Send to LLM → Generate Answer                     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 1. Document Loading

```python
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import json

@dataclass
class Document:
    """A document to be indexed."""
    id: str
    content: str
    metadata: dict = field(default_factory=dict)
    source: str = ""

class DocumentLoader:
    """Load documents from various sources."""
    
    @staticmethod
    def load_text(filepath: str) -> Document:
        path = Path(filepath)
        content = path.read_text(encoding='utf-8')
        return Document(
            id=path.stem,
            content=content,
            metadata={"type": "text", "filename": path.name},
            source=str(path)
        )
    
    @staticmethod
    def load_json(filepath: str) -> list[Document]:
        with open(filepath) as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return [
                Document(
                    id=f"doc_{i}",
                    content=item.get("content", item.get("text", str(item))),
                    metadata=item.get("metadata", {}),
                    source=filepath
                )
                for i, item in enumerate(data)
            ]
        return [Document(id="doc_0", content=json.dumps(data), source=filepath)]
    
    @staticmethod
    def load_directory(dir_path: str, extensions: list = None) -> list[Document]:
        if extensions is None:
            extensions = ['.txt', '.md', '.json']
        
        documents = []
        for path in Path(dir_path).rglob('*'):
            if path.is_file() and path.suffix in extensions:
                try:
                    content = path.read_text(encoding='utf-8')
                    documents.append(Document(
                        id=path.stem,
                        content=content,
                        metadata={
                            "filename": path.name,
                            "extension": path.suffix,
                            "directory": str(path.parent),
                        },
                        source=str(path)
                    ))
                except Exception as e:
                    print(f"Error loading {path}: {e}")
        
        return documents
```

---

## 2. Text Chunking (Critical Component)

**Interview Question: "What chunking strategy would you use?"**

```python
import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class Chunk:
    """A chunk of text from a document."""
    id: str
    text: str
    document_id: str
    chunk_index: int
    metadata: dict

class TextChunker:
    """Multiple chunking strategies."""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        strategy: str = "recursive"  # fixed, sentence, recursive, semantic
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.strategy = strategy
    
    def chunk_document(self, document: Document) -> list[Chunk]:
        """Chunk a document using the configured strategy."""
        if self.strategy == "fixed":
            texts = self._fixed_chunks(document.content)
        elif self.strategy == "sentence":
            texts = self._sentence_chunks(document.content)
        elif self.strategy == "recursive":
            texts = self._recursive_chunks(document.content)
        else:
            texts = self._fixed_chunks(document.content)
        
        return [
            Chunk(
                id=f"{document.id}_chunk_{i}",
                text=text,
                document_id=document.id,
                chunk_index=i,
                metadata={
                    **document.metadata,
                    "source": document.source,
                    "chunk_strategy": self.strategy,
                }
            )
            for i, text in enumerate(texts)
            if text.strip()  # Skip empty chunks
        ]
    
    def _fixed_chunks(self, text: str) -> list[str]:
        """Simple fixed-size word-based chunking."""
        words = text.split()
        chunks = []
        start = 0
        
        while start < len(words):
            end = start + self.chunk_size
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            start += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def _sentence_chunks(self, text: str) -> list[str]:
        """Chunk by sentences, respecting size limit."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_size = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            if current_size + sentence_words > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                # Overlap: keep last N words
                overlap_text = ' '.join(current_chunk)
                overlap_words = overlap_text.split()[-self.chunk_overlap:]
                current_chunk = overlap_words
                current_size = len(current_chunk)
            
            current_chunk.append(sentence)
            current_size += sentence_words
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    def _recursive_chunks(self, text: str) -> list[str]:
        """Recursive character text splitter (like LangChain).
        Tries to split on natural boundaries.
        """
        separators = ["\n\n", "\n", ". ", " ", ""]
        
        def _split(text: str, sep_idx: int = 0) -> list[str]:
            if len(text.split()) <= self.chunk_size:
                return [text]
            
            if sep_idx >= len(separators):
                return [text]
            
            sep = separators[sep_idx]
            if not sep:
                # Last resort: split by words
                words = text.split()
                return [' '.join(words[i:i+self.chunk_size]) 
                        for i in range(0, len(words), self.chunk_size - self.chunk_overlap)]
            
            parts = text.split(sep)
            chunks = []
            current = ""
            
            for part in parts:
                test = current + sep + part if current else part
                if len(test.split()) > self.chunk_size:
                    if current:
                        # Current chunk is big enough, save it
                        if len(current.split()) > self.chunk_size:
                            # Still too big, recurse with next separator
                            chunks.extend(_split(current, sep_idx + 1))
                        else:
                            chunks.append(current)
                    current = part
                else:
                    current = test
            
            if current:
                if len(current.split()) > self.chunk_size:
                    chunks.extend(_split(current, sep_idx + 1))
                else:
                    chunks.append(current)
            
            return chunks
        
        return _split(text)


# Usage comparison
text = """Machine learning is a method of data analysis that automates analytical model building.
It is a branch of artificial intelligence based on the idea that systems can learn from data.
They can identify patterns and make decisions with minimal human intervention.

Deep learning is a subset of machine learning. It uses neural networks with many layers.
These deep neural networks attempt to simulate the behavior of the human brain.
They allow machines to learn from large amounts of data.

Natural language processing is another branch of AI. It deals with the interaction between
computers and humans through natural language. The ultimate goal is to read, understand,
and generate human languages in a valuable way."""

# Try different strategies
for strategy in ["fixed", "sentence", "recursive"]:
    chunker = TextChunker(chunk_size=50, chunk_overlap=10, strategy=strategy)
    doc = Document(id="test", content=text)
    chunks = chunker.chunk_document(doc)
    print(f"\n{strategy}: {len(chunks)} chunks")
    for c in chunks:
        print(f"  [{c.chunk_index}] {c.text[:80]}...")
```

---

## 3. Complete RAG Pipeline

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dataclasses import dataclass
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)

@dataclass
class RAGResponse:
    """Response from RAG pipeline."""
    answer: str
    sources: list[dict]
    query: str
    model: str
    context_chunks: int

class RAGPipeline:
    """Complete RAG pipeline: Index → Retrieve → Generate."""
    
    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        collection_name: str = "rag_documents",
        embedding_model: str = "all-MiniLM-L6-v2",
        llm_api_key: Optional[str] = None,
        llm_model: str = "gpt-4",
    ):
        # Vector DB
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.collection_name = collection_name
        
        # Embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        self.dimensions = self.embedding_model.get_sentence_embedding_dimension()
        
        # LLM
        self.llm_client = OpenAI(api_key=llm_api_key) if llm_api_key else None
        self.llm_model = llm_model
        
        # Chunker
        self.chunker = TextChunker(chunk_size=200, chunk_overlap=30, strategy="recursive")
    
    def setup(self):
        """Initialize the collection."""
        collections = [c.name for c in self.client.get_collections().collections]
        
        if self.collection_name not in collections:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.dimensions,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"Created collection: {self.collection_name}")
    
    # ==================== INDEXING PHASE ====================
    
    def index_document(self, document: Document) -> int:
        """Index a single document (chunk → embed → store)."""
        chunks = self.chunker.chunk_document(document)
        return self._store_chunks(chunks)
    
    def index_documents(self, documents: list[Document]) -> int:
        """Index multiple documents."""
        all_chunks = []
        for doc in documents:
            chunks = self.chunker.chunk_document(doc)
            all_chunks.extend(chunks)
        
        return self._store_chunks(all_chunks)
    
    def _store_chunks(self, chunks: list[Chunk], batch_size: int = 100) -> int:
        """Generate embeddings and store chunks in Qdrant."""
        total = 0
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c.text for c in batch]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # Create points
            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "text": chunk.text,
                        "document_id": chunk.document_id,
                        "chunk_index": chunk.chunk_index,
                        **chunk.metadata,
                    }
                )
                for chunk, embedding in zip(batch, embeddings)
            ]
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            total += len(points)
            logger.info(f"Stored {len(points)} chunks (total: {total})")
        
        return total
    
    # ==================== RETRIEVAL PHASE ====================
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
        category: Optional[str] = None,
    ) -> list[dict]:
        """Retrieve relevant chunks for a query."""
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Build filter
        filter_conditions = []
        if category:
            filter_conditions.append(
                FieldCondition(key="category", match=MatchValue(value=category))
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
            {
                "text": r.payload.get("text", ""),
                "score": r.score,
                "document_id": r.payload.get("document_id", ""),
                "chunk_index": r.payload.get("chunk_index", 0),
                "metadata": {k: v for k, v in r.payload.items() 
                           if k not in ("text",)},
            }
            for r in results
        ]
    
    # ==================== GENERATION PHASE ====================
    
    def generate(
        self,
        query: str,
        context_chunks: list[dict],
        temperature: float = 0.0,
    ) -> str:
        """Generate answer using LLM with retrieved context."""
        if not self.llm_client:
            # Fallback: return context without LLM
            return "\n\n".join([c["text"] for c in context_chunks])
        
        # Build context
        context = "\n\n---\n\n".join([
            f"[Source: {c['document_id']}, Chunk {c['chunk_index']}]\n{c['text']}"
            for c in context_chunks
        ])
        
        # Build prompt
        prompt = f"""Answer the question based ONLY on the following context.
If the context doesn't contain enough information, say "I don't have enough information to answer this."
Include source references in your answer.

Context:
{context}

Question: {query}

Answer:"""
        
        response = self.llm_client.chat.completions.create(
            model=self.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on provided context only. Always cite sources."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=1000,
        )
        
        return response.choices[0].message.content
    
    # ==================== FULL PIPELINE ====================
    
    def query(
        self,
        question: str,
        top_k: int = 5,
        category: Optional[str] = None,
    ) -> RAGResponse:
        """Full RAG pipeline: Retrieve → Generate."""
        # Step 1: Retrieve
        chunks = self.retrieve(question, top_k=top_k, category=category)
        
        if not chunks:
            return RAGResponse(
                answer="I couldn't find any relevant information.",
                sources=[],
                query=question,
                model=self.llm_model,
                context_chunks=0,
            )
        
        # Step 2: Generate
        answer = self.generate(question, chunks)
        
        # Step 3: Build response
        sources = [
            {
                "document": c["document_id"],
                "chunk": c["chunk_index"],
                "score": c["score"],
                "preview": c["text"][:100] + "...",
            }
            for c in chunks
        ]
        
        return RAGResponse(
            answer=answer,
            sources=sources,
            query=question,
            model=self.llm_model,
            context_chunks=len(chunks),
        )


# ==================== USAGE EXAMPLE ====================

# Setup
rag = RAGPipeline(
    llm_api_key="sk-your-key",  # Optional
    llm_model="gpt-4",
)
rag.setup()

# Index documents
documents = [
    Document(
        id="python_guide",
        content="""Python is a high-level programming language known for its simplicity.
        It supports object-oriented, functional, and procedural programming paradigms.
        Python has extensive libraries for AI and machine learning including TensorFlow,
        PyTorch, and scikit-learn. It uses indentation for code blocks instead of braces.""",
        metadata={"category": "programming"}
    ),
    Document(
        id="flask_guide",
        content="""Flask is a lightweight WSGI web application framework in Python.
        It is designed to make getting started quick and easy, with the ability to scale
        up to complex applications. Flask uses decorators for routing and supports
        extensions for database integration, authentication, and more.""",
        metadata={"category": "web"}
    ),
    Document(
        id="rag_guide",
        content="""RAG (Retrieval-Augmented Generation) is a technique that combines
        information retrieval with language model generation. It first retrieves relevant
        documents from a knowledge base, then uses them as context for the LLM to generate
        accurate, grounded answers. This reduces hallucination significantly.""",
        metadata={"category": "ai"}
    ),
]

indexed = rag.index_documents(documents)
print(f"Indexed {indexed} chunks")

# Query
response = rag.query("What is RAG and how does it reduce hallucination?")
print(f"\nAnswer: {response.answer}")
print(f"\nSources ({response.context_chunks}):")
for s in response.sources:
    print(f"  - {s['document']} (score: {s['score']:.3f}): {s['preview']}")
```

---

## 4. RAG Flask API

```python
from flask import Flask, request, jsonify

app = Flask(__name__)
rag = None  # Initialize on startup

@app.before_request
def init_rag():
    global rag
    if rag is None:
        rag = RAGPipeline()
        rag.setup()

@app.route("/api/documents", methods=["POST"])
def upload_document():
    """Upload and index a document."""
    data = request.get_json()
    
    doc = Document(
        id=data.get("id", str(uuid.uuid4())),
        content=data["content"],
        metadata=data.get("metadata", {}),
        source=data.get("source", "api_upload")
    )
    
    chunks_count = rag.index_document(doc)
    return jsonify({
        "message": "Document indexed",
        "chunks": chunks_count,
        "document_id": doc.id,
    }), 201

@app.route("/api/query", methods=["POST"])
def query_documents():
    """Query the RAG system."""
    data = request.get_json()
    
    response = rag.query(
        question=data["question"],
        top_k=data.get("top_k", 5),
        category=data.get("category"),
    )
    
    return jsonify({
        "answer": response.answer,
        "sources": response.sources,
        "model": response.model,
        "context_chunks": response.context_chunks,
    })

@app.route("/api/search", methods=["POST"])
def search_documents():
    """Search without LLM generation (just retrieval)."""
    data = request.get_json()
    
    results = rag.retrieve(
        query=data["query"],
        top_k=data.get("top_k", 10),
    )
    
    return jsonify({"results": results, "total": len(results)})
```

---

## 5. Advanced RAG Patterns

### Hybrid Search (Keyword + Semantic)
```python
def hybrid_search(query: str, documents: list, top_k: int = 5) -> list:
    """Combine keyword and semantic search."""
    # Semantic results
    semantic_results = rag.retrieve(query, top_k=top_k * 2)
    
    # Keyword results (simple BM25-like)
    query_words = set(query.lower().split())
    keyword_results = []
    for doc in documents:
        doc_words = set(doc["text"].lower().split())
        overlap = len(query_words & doc_words) / len(query_words) if query_words else 0
        keyword_results.append({"text": doc["text"], "score": overlap})
    
    keyword_results.sort(key=lambda x: x["score"], reverse=True)
    
    # Combine scores (Reciprocal Rank Fusion)
    combined = {}
    for rank, r in enumerate(semantic_results):
        combined[r["text"]] = combined.get(r["text"], 0) + 1 / (rank + 60)
    for rank, r in enumerate(keyword_results[:top_k * 2]):
        combined[r["text"]] = combined.get(r["text"], 0) + 1 / (rank + 60)
    
    # Sort by combined score
    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
    return [{"text": text, "score": score} for text, score in ranked[:top_k]]
```

### Multi-Query RAG
```python
def multi_query_rag(question: str, rag: RAGPipeline) -> RAGResponse:
    """Generate multiple search queries for better retrieval."""
    # Step 1: Generate alternative queries
    alt_queries_prompt = f"""Generate 3 alternative search queries for this question.
Return only the queries, one per line.

Question: {question}"""
    
    # Get alternative queries from LLM
    alt_response = rag.llm_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": alt_queries_prompt}],
        temperature=0.7
    )
    alt_queries = alt_response.choices[0].message.content.strip().split("\n")
    
    # Step 2: Search with all queries
    all_chunks = []
    seen_texts = set()
    
    for q in [question] + alt_queries:
        results = rag.retrieve(q, top_k=3)
        for r in results:
            if r["text"] not in seen_texts:
                all_chunks.append(r)
                seen_texts.add(r["text"])
    
    # Step 3: Generate with combined context
    answer = rag.generate(question, all_chunks[:10])
    
    return RAGResponse(
        answer=answer,
        sources=[{"text": c["text"][:100], "score": c["score"]} for c in all_chunks[:10]],
        query=question,
        model=rag.llm_model,
        context_chunks=len(all_chunks[:10]),
    )
```

---

## Exercises

### Exercise 1: Build a Complete RAG System
```python
# Build a RAG system that:
# 1. Accepts PDF/TXT uploads via Flask API
# 2. Chunks with recursive strategy
# 3. Stores in Qdrant with metadata
# 4. Supports filtered search
# 5. Generates answers with source citations
# 6. Tracks usage statistics

# TODO: Implement end-to-end
```

### Exercise 2: Evaluate RAG Quality
```python
# Build an evaluation system:
# 1. Create 10 question-answer pairs manually
# 2. Run each through your RAG
# 3. Compare RAG answers vs expected answers
# 4. Calculate accuracy, relevance scores
# 5. Identify failure cases

# TODO: Implement
```

---

## Key Takeaways
1. RAG = **Retrieve** relevant docs + **Augment** prompt + **Generate** answer
2. **Chunking strategy** dramatically affects quality
3. **Recursive chunking** respects document structure
4. Use **score thresholds** to filter low-quality results
5. **Prompt engineering** for RAG: always say "answer based on context ONLY"
6. **Temperature 0** for factual RAG answers
7. **Source citations** reduce hallucination and build trust
8. **Hybrid search** (keyword + semantic) improves recall
