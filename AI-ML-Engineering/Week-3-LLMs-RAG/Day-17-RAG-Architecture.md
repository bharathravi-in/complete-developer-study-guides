# Day 17: RAG Architecture

## Learning Objectives
- Understand RAG concept and when to use it
- Implement document loading and chunking strategies
- Use embedding models and vector databases
- Build end-to-end RAG pipeline
- Evaluate RAG system quality

---

## 1. RAG Concept

```
Problem: LLMs have knowledge cutoffs and hallucinate on specific facts.
Solution: Retrieve relevant documents, then generate answers grounded in them.

Query → Embed → Vector Search → Top-K Documents → LLM (with context) → Answer

Without RAG: "What's our refund policy?" → LLM guesses (hallucination risk)
With RAG: "What's our refund policy?" → Retrieves policy doc → LLM quotes it accurately
```

### When to Use RAG

```
USE RAG:
✅ Private/proprietary knowledge (company docs, code)
✅ Frequently updated information
✅ Need citations/sources
✅ Domain-specific (medical, legal, technical)
✅ Large knowledge base (too big for context window)

DON'T USE RAG:
❌ General knowledge (model already knows)
❌ Simple tasks (classification, translation)
❌ Creative writing
❌ When fine-tuning is more appropriate (consistent behavior)
```

---

## 2. Document Loading & Chunking

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader

# --- Document Loading ---
# PDF
pdf_loader = PyPDFLoader("technical_manual.pdf")
pdf_docs = pdf_loader.load()

# Directory of files
dir_loader = DirectoryLoader("./docs/", glob="**/*.md")
all_docs = dir_loader.load()

# --- Chunking Strategies ---

# 1. Fixed-size chunking (simple but may cut mid-sentence)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # Characters per chunk
    chunk_overlap=50,     # Overlap between chunks (prevents info loss at boundaries)
    separators=["\n\n", "\n", ". ", " "],  # Try to split at natural boundaries
)
chunks = splitter.split_documents(all_docs)
print(f"Created {len(chunks)} chunks from {len(all_docs)} documents")

# 2. Semantic chunking (split at topic boundaries)
from langchain_experimental.text_splitter import SemanticChunker
from langchain.embeddings import OpenAIEmbeddings

semantic_splitter = SemanticChunker(
    OpenAIEmbeddings(),
    breakpoint_threshold_type="percentile",  # Split where embeddings diverge
)
semantic_chunks = semantic_splitter.split_documents(all_docs)

# 3. Markdown header-based splitting (preserves structure)
from langchain.text_splitter import MarkdownHeaderTextSplitter
headers_to_split = [("#", "h1"), ("##", "h2"), ("###", "h3")]
md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split)
md_chunks = md_splitter.split_text(markdown_text)

# Chunking guidelines:
# | Chunk Size | Best For                    | Tradeoff                |
# |------------|-----------------------------|-----------------------  |
# | 200-500    | Precise retrieval, Q&A      | May miss context        |
# | 500-1000   | General RAG (default)       | Good balance            |
# | 1000-2000  | Summarization, broad context| Less precise retrieval  |
# Overlap: 10-20% of chunk size
```

---

## 3. Embeddings

```python
# Embeddings: Convert text → dense vector capturing meaning
# Similar texts → similar vectors (cosine similarity)

from sentence_transformers import SentenceTransformer
from openai import OpenAI

# Option 1: Local (free, private, fast)
model = SentenceTransformer('all-MiniLM-L6-v2')  # 384 dimensions
embeddings = model.encode(["Hello world", "Hi there"])
# Shape: (2, 384)

# Better local model:
model = SentenceTransformer('BAAI/bge-large-en-v1.5')  # 1024 dims, top quality

# Option 2: OpenAI API (good quality, easy)
client = OpenAI()
response = client.embeddings.create(
    model="text-embedding-3-small",  # 1536 dims, cheaper
    # model="text-embedding-3-large",  # 3072 dims, better quality
    input=["Hello world", "Hi there"],
)
embeddings = [e.embedding for e in response.data]

# Similarity search
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

query_embedding = model.encode("How do I reset my password?")
doc_embeddings = model.encode(chunks)

# Find most similar
similarities = [cosine_similarity(query_embedding, doc_emb) for doc_emb in doc_embeddings]
top_k_indices = np.argsort(similarities)[-5:][::-1]
```

---

## 4. Vector Databases

```python
# Vector DB: Store embeddings + metadata, enable fast similarity search

# --- ChromaDB (simple, local, great for prototyping) ---
import chromadb

client = chromadb.Client()
collection = client.create_collection("docs")

# Add documents
collection.add(
    documents=[chunk.page_content for chunk in chunks],
    metadatas=[chunk.metadata for chunk in chunks],
    ids=[f"chunk_{i}" for i in range(len(chunks))],
)

# Query
results = collection.query(
    query_texts=["How do I configure authentication?"],
    n_results=5,
)
print(results['documents'][0])  # Top 5 relevant chunks

# --- Qdrant (production-grade, filtering, cloud or self-hosted) ---
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

client = QdrantClient(url="http://localhost:6333")

# Create collection
client.create_collection(
    collection_name="docs",
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# Upsert vectors
points = [
    PointStruct(
        id=i,
        vector=embedding.tolist(),
        payload={"text": chunk.page_content, "source": chunk.metadata.get("source")},
    )
    for i, (chunk, embedding) in enumerate(zip(chunks, doc_embeddings))
]
client.upsert(collection_name="docs", points=points)

# Search with metadata filter
results = client.search(
    collection_name="docs",
    query_vector=query_embedding.tolist(),
    limit=5,
    query_filter={"must": [{"key": "source", "match": {"value": "user_guide.pdf"}}]},
)

# --- Comparison ---
# | DB         | Hosting    | Filtering | Scale     | Best For          |
# |------------|-----------|-----------|-----------|-------------------|
# | ChromaDB   | Local     | Basic     | Small     | Prototyping       |
# | Qdrant     | Both      | Rich      | Large     | Production        |
# | Pinecone   | Cloud     | Rich      | Large     | Serverless prod   |
# | Weaviate   | Both      | Rich      | Large     | Multi-modal       |
# | pgvector   | Postgres  | SQL       | Medium    | Existing Postgres |
```

---

## 5. End-to-End RAG Pipeline

```python
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import chromadb

class RAGPipeline:
    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.llm_client = OpenAI()
        self.vectordb = chromadb.Client()
        self.collection = self.vectordb.create_collection("knowledge_base")
    
    def ingest(self, documents: list[str], metadatas: list[dict] = None):
        """Add documents to the knowledge base."""
        self.collection.add(
            documents=documents,
            metadatas=metadatas or [{}] * len(documents),
            ids=[f"doc_{i}" for i in range(len(documents))],
        )
    
    def retrieve(self, query: str, top_k: int = 5) -> list[str]:
        """Find relevant documents for a query."""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
        )
        return results['documents'][0]
    
    def generate(self, query: str, context_docs: list[str]) -> str:
        """Generate answer using retrieved context."""
        context = "\n\n---\n\n".join(context_docs)
        
        response = self.llm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """Answer the question based ONLY on the provided context.
If the context doesn't contain the answer, say "I don't have enough information to answer this."
Cite which part of the context you used."""},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ],
            temperature=0,
        )
        return response.choices[0].message.content
    
    def query(self, question: str, top_k: int = 5) -> str:
        """Full RAG pipeline: retrieve + generate."""
        relevant_docs = self.retrieve(question, top_k)
        answer = self.generate(question, relevant_docs)
        return answer

# Usage
rag = RAGPipeline()
rag.ingest(["Refund policy: Full refund within 30 days...", 
            "Shipping: Free for orders over $50..."])
answer = rag.query("What is the refund policy?")
print(answer)
```

---

## 6. RAG Evaluation

```python
# RAGAS Framework metrics:
# 1. Faithfulness: Is the answer grounded in retrieved context?
# 2. Answer Relevance: Does the answer address the question?
# 3. Context Precision: Are retrieved docs relevant?
# 4. Context Recall: Did we retrieve all needed info?

from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
from datasets import Dataset

# Prepare evaluation dataset
eval_data = {
    "question": ["What is the refund policy?", "How long is shipping?"],
    "answer": ["Full refund within 30 days of purchase.", "3-5 business days."],
    "contexts": [["Refund policy: Full refund within 30 days..."], ["Shipping takes 3-5 days..."]],
    "ground_truth": ["30-day full refund policy", "3-5 business days standard shipping"],
}

dataset = Dataset.from_dict(eval_data)
results = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
)
print(results)
# {'faithfulness': 0.95, 'answer_relevancy': 0.88, 'context_precision': 0.92, ...}

# Simple evaluation without RAGAS:
def evaluate_retrieval(queries, expected_doc_ids, retriever, k=5):
    """Measure retrieval quality."""
    hits = 0
    for query, expected in zip(queries, expected_doc_ids):
        retrieved = retriever.retrieve(query, top_k=k)
        if any(exp in retrieved for exp in expected):
            hits += 1
    return hits / len(queries)  # Hit rate @ K
```

---

## Interview Questions

### Beginner
1. **What is RAG and why is it useful?** Retrieval-Augmented Generation: retrieve relevant documents from a knowledge base, then give them to the LLM as context for generation. Reduces hallucination, enables private data access, keeps knowledge up-to-date without retraining.
2. **What is a vector database?** Database optimized for storing and searching high-dimensional vectors (embeddings). Enables fast approximate nearest neighbor search. Stores vectors + metadata, supports filtering. Examples: Qdrant, Pinecone, ChromaDB.
3. **Why do we chunk documents?** Embedding models have token limits (512 typical). Smaller chunks = more precise retrieval. Large documents would dilute relevant info. Chunks should be semantically coherent units.

### Intermediate
4. **How do you choose chunk size?** Depends on use case: smaller (200-500) for precise Q&A, larger (1000-2000) for broad context. Consider: embedding model max tokens, retrieval precision vs context completeness, document structure. Add overlap (10-20%) to prevent info loss at boundaries.
5. **What's the difference between dense and sparse retrieval?** Dense: embedding-based (captures semantics, "car" matches "automobile"). Sparse: keyword-based like BM25 (exact match, "BMW 320i" matches "BMW 320i"). Hybrid (both) is best for production.
6. **How do you evaluate a RAG system?** Retrieval: precision@K, recall@K, hit rate. Generation: faithfulness (grounded in context?), relevance (answers the question?). End-to-end: user satisfaction, A/B testing. Use RAGAS framework for automated metrics.

### Advanced
7. **What are common RAG failure modes and how do you fix them?** Retrieval misses: better chunking, hybrid search, query rewriting. Retrieved but not used: improve prompt, put relevant context first. Hallucination despite context: lower temperature, add "if not in context say I don't know". Wrong interpretation: better chunk overlap, parent-child retrieval.
8. **How do you scale RAG to millions of documents?** Approximate nearest neighbor (HNSW, IVF) instead of brute force. Metadata filtering (pre-filter before vector search). Hierarchical retrieval (coarse → fine). Quantize embeddings (reduce memory). Distributed vector DB (Qdrant cloud, Pinecone).
9. **Design a RAG system for a legal document search platform.** Challenges: precise citations needed, complex queries, document structure matters. Architecture: PDF parsing with structure preservation, hierarchical chunking (section → paragraph), hybrid retrieval (BM25 for exact citations + dense for semantic), re-ranking with cross-encoder, answer with page/section citations.

---

## Hands-On Exercise
1. Build a simple RAG pipeline with ChromaDB (5 documents, test queries)
2. Compare chunking strategies: fixed-size vs recursive vs semantic
3. Evaluate retrieval quality: which embedding model finds the right chunks?
4. Add metadata filtering (source document, date, category)
5. Implement the full pipeline with LangChain or LlamaIndex
6. Evaluate with RAGAS metrics on 10+ test questions
