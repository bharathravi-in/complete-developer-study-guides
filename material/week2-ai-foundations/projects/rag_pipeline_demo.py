#!/usr/bin/env python3
"""
Week 2 Project: Complete RAG Pipeline Demo

This is a self-contained RAG demo you can run locally.
Uses sentence-transformers (free, no API key needed) for embeddings
and a simple in-memory vector store.

Setup:
    pip install sentence-transformers numpy

Run:
    python rag_pipeline_demo.py
"""

import hashlib
import json
import re
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


# ============================================================
# 1. DOCUMENT LOADER & CHUNKER
# ============================================================

@dataclass
class Chunk:
    id: str
    text: str
    source: str
    index: int
    embedding: Optional[list[float]] = None


class RecursiveChunker:
    """Split text using recursive strategy: paragraph → sentence → word."""

    def __init__(self, chunk_size: int = 200, overlap: int = 30):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, source: str = "unknown") -> list[Chunk]:
        # Try paragraph split first
        paragraphs = text.split('\n\n')
        chunks: list[str] = []

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            words = para.split()
            if len(words) <= self.chunk_size:
                chunks.append(para)
            else:
                # Fall back to sentence split
                sentences = re.split(r'(?<=[.!?])\s+', para)
                current: list[str] = []
                current_size = 0
                for sent in sentences:
                    wc = len(sent.split())
                    if current_size + wc > self.chunk_size and current:
                        chunks.append(' '.join(current))
                        overlap_sents = current[-1:] if self.overlap > 0 else []
                        current = overlap_sents
                        current_size = sum(len(s.split()) for s in current)
                    current.append(sent)
                    current_size += wc
                if current:
                    chunks.append(' '.join(current))

        return [
            Chunk(
                id=hashlib.md5(f"{source}:{i}:{c[:50]}".encode()).hexdigest()[:12],
                text=c,
                source=source,
                index=i,
            )
            for i, c in enumerate(chunks)
        ]


# ============================================================
# 2. IN-MEMORY VECTOR STORE (No Qdrant needed for demo)
# ============================================================

class SimpleVectorStore:
    """In-memory vector store using numpy cosine similarity."""

    def __init__(self):
        self._chunks: list[Chunk] = []
        self._vectors: list[np.ndarray] = []

    def add(self, chunks: list[Chunk], vectors: list[np.ndarray]) -> None:
        self._chunks.extend(chunks)
        self._vectors.extend(vectors)
        print(f"  Stored {len(chunks)} chunks (total: {len(self._chunks)})")

    def search(self, query_vector: np.ndarray, top_k: int = 5, threshold: float = 0.3) -> list[tuple[Chunk, float]]:
        if not self._vectors:
            return []

        matrix = np.array(self._vectors)
        query = query_vector.reshape(1, -1)

        # Cosine similarity
        dot_products = np.dot(matrix, query.T).flatten()
        norms = np.linalg.norm(matrix, axis=1) * np.linalg.norm(query)
        norms = np.where(norms == 0, 1e-10, norms)
        similarities = dot_products / norms

        # Get top-k above threshold
        indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in indices:
            score = float(similarities[idx])
            if score >= threshold:
                results.append((self._chunks[idx], score))

        return results

    @property
    def count(self) -> int:
        return len(self._chunks)


# ============================================================
# 3. EMBEDDING SERVICE (using sentence-transformers)
# ============================================================

class EmbeddingService:
    """Generate embeddings using sentence-transformers (free, local)."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                print(f"  Loading model: {self.model_name}...")
                self._model = SentenceTransformer(self.model_name)
                print(f"  Model loaded! Dimensions: {self._model.get_sentence_embedding_dimension()}")
            except ImportError:
                print("  ⚠️  sentence-transformers not installed.")
                print("  Run: pip install sentence-transformers")
                print("  Falling back to random embeddings for demo...")
                self._model = "RANDOM"

    def embed(self, texts: list[str]) -> list[np.ndarray]:
        self._load_model()
        if self._model == "RANDOM":
            return [np.random.randn(384).astype(np.float32) for _ in texts]
        return [np.array(v) for v in self._model.encode(texts)]  # type: ignore

    def embed_one(self, text: str) -> np.ndarray:
        return self.embed([text])[0]


# ============================================================
# 4. RAG PIPELINE
# ============================================================

class RAGPipeline:
    """Complete RAG pipeline: Index → Retrieve → Generate."""

    def __init__(self, chunk_size: int = 200, overlap: int = 30):
        self.chunker = RecursiveChunker(chunk_size, overlap)
        self.embedder = EmbeddingService()
        self.store = SimpleVectorStore()

    def index_document(self, text: str, source: str = "document") -> int:
        """Chunk, embed, and store a document."""
        print(f"\n📄 Indexing: {source}")

        # Chunk
        chunks = self.chunker.chunk(text, source)
        print(f"  Created {len(chunks)} chunks")

        # Embed
        texts = [c.text for c in chunks]
        vectors = self.embedder.embed(texts)
        print(f"  Generated {len(vectors)} embeddings")

        # Store
        self.store.add(chunks, vectors)
        return len(chunks)

    def retrieve(self, query: str, top_k: int = 3) -> list[tuple[Chunk, float]]:
        """Search for relevant chunks."""
        query_vector = self.embedder.embed_one(query)
        return self.store.search(query_vector, top_k=top_k)

    def query(self, question: str, top_k: int = 3) -> dict:
        """Full RAG query: retrieve context and format answer."""
        print(f"\n🔍 Query: {question}")

        # Retrieve
        results = self.retrieve(question, top_k=top_k)

        if not results:
            return {
                "question": question,
                "answer": "No relevant information found.",
                "sources": [],
            }

        # Build context
        context_parts = []
        sources = []
        for chunk, score in results:
            context_parts.append(chunk.text)
            sources.append({
                "text": chunk.text[:100] + "..." if len(chunk.text) > 100 else chunk.text,
                "source": chunk.source,
                "score": round(score, 4),
            })

        context = "\n\n---\n\n".join(context_parts)

        # Build prompt (in production, send this to OpenAI/Claude)
        prompt = f"""Answer the question based ONLY on the context below.
If the context doesn't contain enough information, say "I don't have enough information."

Context:
{context}

Question: {question}

Answer:"""

        print(f"  Found {len(results)} relevant chunks")
        print(f"  Top score: {results[0][1]:.4f}")

        return {
            "question": question,
            "prompt": prompt,
            "context_chunks": len(results),
            "top_score": round(results[0][1], 4),
            "sources": sources,
            "note": "In production, send 'prompt' to OpenAI/Claude for the final answer",
        }


# ============================================================
# 5. DEMO
# ============================================================

SAMPLE_DOCUMENTS = {
    "python_guide": """
Python is a high-level programming language known for its readability and simplicity.
It was created by Guido van Rossum and released in 1991. Python supports multiple
programming paradigms including procedural, object-oriented, and functional programming.

Python's key features include dynamic typing, automatic memory management through garbage
collection, and a comprehensive standard library. The language uses indentation to define
code blocks instead of braces, which enforces readable code structure.

Python is widely used in web development with frameworks like Flask and Django,
data science with libraries like NumPy and Pandas, machine learning with PyTorch
and TensorFlow, and automation scripting for DevOps tasks.

The Global Interpreter Lock (GIL) in CPython allows only one thread to execute Python
bytecode at a time. This means CPU-bound multithreaded programs won't see speedup.
However, I/O-bound operations release the GIL, making asyncio effective for
network-heavy applications like API servers.

Virtual environments in Python isolate project dependencies. Tools like venv, virtualenv,
and poetry create isolated spaces where each project has its own packages without
conflicts. This is similar to how node_modules works in Node.js.
""",

    "rag_guide": """
RAG (Retrieval-Augmented Generation) is a technique that combines information retrieval
with language model generation. Instead of relying solely on the LLM's training data,
RAG searches a knowledge base to find relevant context before generating an answer.

The RAG pipeline has three main stages: indexing, retrieval, and generation.
During indexing, documents are split into chunks, converted to embeddings, and stored
in a vector database. During retrieval, the user's query is embedded and used to search
for similar chunks. During generation, retrieved chunks are provided as context to the LLM.

Text chunking is a critical part of RAG. Common strategies include fixed-size chunking
(split every N words), sentence-based chunking (split on sentence boundaries), and
recursive chunking (try paragraph first, then sentence, then word boundaries).

Chunk size affects retrieval quality. Smaller chunks (200-300 words) give more precise
retrieval but less context per result. Larger chunks (500-1000 words) provide more context
but may include irrelevant information. An overlap of 10-20% helps maintain continuity.

Vector databases like Qdrant, Pinecone, and ChromaDB store embeddings and enable fast
similarity search using algorithms like HNSW. They support filtering by metadata,
which allows searching within specific documents or categories.

Caching is essential for production RAG systems. Cache identical queries using Redis
with a TTL of 1 hour to reduce LLM API costs by 50-80%. Use the hash of the query
as the cache key for consistent lookups.
""",

    "embeddings_guide": """
Embeddings are dense vector representations of text that capture semantic meaning.
Unlike keyword matching, embeddings understand that "machine learning" and "ML" are
related even though they share no words. This enables semantic search.

Popular embedding models include OpenAI's text-embedding-3-small (1536 dimensions),
sentence-transformers all-MiniLM-L6-v2 (384 dimensions, free and local), and
Cohere's embed-v3. The choice depends on quality needs, budget, and latency requirements.

Cosine similarity is the standard metric for comparing embeddings. It measures the
angle between two vectors, ranging from -1 (opposite) to 1 (identical). For normalized
embeddings, cosine similarity equals the dot product, making computation efficient.

Embedding dimensions represent the information capacity. Higher dimensions (1536, 3072)
capture more nuance but require more storage and computation. Lower dimensions (384)
are faster and cheaper with acceptable quality for most use cases.

Batch embedding is important for performance. Instead of embedding one text at a time,
send batches of 100 texts per API call. This reduces latency from 100 API calls to 1
and is more cost-effective for large document collections.
""",
}


def main():
    print("=" * 60)
    print("RAG Pipeline Demo")
    print("=" * 60)

    # Initialize
    rag = RAGPipeline(chunk_size=100, overlap=15)

    # Index documents
    for name, text in SAMPLE_DOCUMENTS.items():
        rag.index_document(text, source=name)

    print(f"\n📊 Total chunks in store: {rag.store.count}")

    # Run queries
    queries = [
        "What is the GIL in Python?",
        "How does RAG reduce hallucination?",
        "What chunk size should I use?",
        "How do embeddings capture meaning?",
        "What is cosine similarity?",
    ]

    print("\n" + "=" * 60)
    print("Running Queries")
    print("=" * 60)

    for q in queries:
        result = rag.query(q, top_k=3)
        print(f"\n{'─' * 50}")
        print(f"Q: {result['question']}")
        print(f"Chunks found: {result['context_chunks']}")
        print(f"Top score: {result.get('top_score', 'N/A')}")
        if result['sources']:
            for i, s in enumerate(result['sources'], 1):
                print(f"  Source {i}: [{s['source']}] (score: {s['score']})")
                print(f"           {s['text']}")

    print("\n" + "=" * 60)
    print("✅ RAG Pipeline Demo Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Replace SimpleVectorStore with Qdrant")
    print("2. Add OpenAI API call in the generation step")
    print("3. Add Redis caching for repeated queries")
    print("4. Build Flask API endpoints around this pipeline")


if __name__ == "__main__":
    main()
