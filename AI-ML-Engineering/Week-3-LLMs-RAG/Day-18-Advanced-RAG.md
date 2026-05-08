# Day 18: Advanced RAG Techniques

## Learning Objectives
- Implement query rewriting and expansion strategies
- Use HyDE and multi-query retrieval patterns
- Apply re-ranking with cross-encoders
- Build hybrid search (dense + sparse)
- Design parent-child and hierarchical chunking
- Implement Self-RAG and knowledge graph augmented RAG

---

## 1. Query Rewriting & Expansion

```python
from openai import OpenAI
client = OpenAI()

# Problem: User queries are often vague or poorly worded
# "how to fix that error" → Retrieve nothing useful

# Solution 1: Query Rewriting (clarify intent)
def rewrite_query(original_query: str) -> str:
    """Rewrite query to be more specific and searchable."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Rewrite the user's query to be more specific and detailed for document retrieval. Return only the rewritten query."},
            {"role": "user", "content": original_query}
        ],
        temperature=0,
    )
    return response.choices[0].message.content

# "fix auth error" → "How to resolve authentication error in user login system"

# Solution 2: Multi-Query (generate multiple perspectives)
def multi_query_expansion(query: str, n: int = 3) -> list[str]:
    """Generate multiple versions of a query for broader retrieval."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"Generate {n} different versions of the given query for document search. Each version should approach the topic from a different angle. Return one per line."},
            {"role": "user", "content": query}
        ],
        temperature=0.7,
    )
    queries = response.choices[0].message.content.strip().split("\n")
    return [q.strip() for q in queries if q.strip()]

# "RAG performance" →
# ["How to improve retrieval accuracy in RAG systems",
#  "Optimizing response quality for retrieval-augmented generation",
#  "RAG evaluation metrics and benchmarks"]

# Solution 3: Step-back Prompting (abstract the query)
def step_back_query(query: str) -> str:
    """Generate a more general query to find background context."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Given a specific question, generate a broader step-back question that would help find useful background context. Return only the question."},
            {"role": "user", "content": query}
        ],
    )
    return response.choices[0].message.content

# "Why does my Flask app crash with 500 error on /api/users?" 
# → "How does Flask handle request routing and error responses?"
```

---

## 2. HyDE (Hypothetical Document Embeddings)

```python
# Problem: Query embeddings are in "question space" but docs are in "answer space"
# "What causes memory leaks?" ≠ embedding of "Memory leaks occur when..."
# Solution: Generate a hypothetical answer, embed THAT instead

def hyde_retrieval(query: str, retriever, embedder):
    """
    HyDE: Generate hypothetical document, use its embedding for retrieval.
    Often retrieves better results than embedding the query directly.
    """
    # Step 1: Generate hypothetical answer (doesn't need to be accurate)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Write a short passage that would answer the following question. Don't worry about accuracy, just write a plausible-sounding answer."},
            {"role": "user", "content": query}
        ],
    )
    hypothetical_doc = response.choices[0].message.content
    
    # Step 2: Embed the hypothetical document (not the query!)
    hyde_embedding = embedder.encode(hypothetical_doc)
    
    # Step 3: Search with hypothetical doc embedding
    results = retriever.search(hyde_embedding, top_k=5)
    return results

# Why HyDE works:
# - Hypothetical answer is in same "embedding space" as real docs
# - Even inaccurate answers share vocabulary/structure with real answers
# - Query "What is ACID?" → hypothetical: "ACID stands for Atomicity, Consistency..."
#   → matches real doc about database transactions better than bare query
```

---

## 3. Re-Ranking with Cross-Encoders

```python
# Problem: Bi-encoder (embedding) retrieval is fast but imprecise
# Solution: Retrieve many (top-50), then re-rank with a cross-encoder (top-5)

# Bi-encoder: query and doc embedded independently → fast but less accurate
# Cross-encoder: query + doc processed together → slow but very accurate

from sentence_transformers import CrossEncoder

# Load cross-encoder for re-ranking
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def retrieve_and_rerank(query: str, retriever, top_k: int = 5, initial_k: int = 50):
    """Two-stage retrieval: broad bi-encoder search → precise cross-encoder re-ranking."""
    
    # Stage 1: Fast retrieval (bi-encoder)
    candidates = retriever.retrieve(query, top_k=initial_k)
    
    # Stage 2: Re-rank with cross-encoder (slower but more accurate)
    pairs = [(query, doc.page_content) for doc in candidates]
    scores = reranker.predict(pairs)
    
    # Sort by re-ranker score
    scored_docs = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [doc for doc, score in scored_docs[:top_k]]

# Re-ranking typically improves precision by 10-30%
# Cost: ~100ms for 50 candidates (acceptable for most applications)

# Cohere re-ranker (API-based, high quality)
import cohere
co = cohere.Client("your-api-key")

def cohere_rerank(query: str, documents: list[str], top_k: int = 5):
    results = co.rerank(
        query=query,
        documents=documents,
        top_n=top_k,
        model="rerank-english-v3.0",
    )
    return [(r.index, r.relevance_score) for r in results.results]
```

---

## 4. Hybrid Search (Dense + Sparse)

```python
# Dense retrieval: great for semantic meaning ("automobile" matches "car")
# Sparse retrieval (BM25): great for exact terms ("BMW 320i", error codes)
# Hybrid: combine both for best of both worlds

from rank_bm25 import BM25Okapi
import numpy as np

class HybridRetriever:
    def __init__(self, documents: list[str], embedder):
        self.documents = documents
        self.embedder = embedder
        
        # Dense index
        self.embeddings = embedder.encode(documents)
        
        # Sparse index (BM25)
        tokenized = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)
    
    def search(self, query: str, top_k: int = 5, alpha: float = 0.7):
        """
        Hybrid search combining dense and sparse retrieval.
        alpha: weight for dense scores (1-alpha for sparse).
        """
        # Dense scores (cosine similarity)
        query_emb = self.embedder.encode(query)
        dense_scores = np.dot(self.embeddings, query_emb) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_emb)
        )
        
        # Sparse scores (BM25)
        sparse_scores = self.bm25.get_scores(query.lower().split())
        
        # Normalize both to [0, 1]
        dense_norm = (dense_scores - dense_scores.min()) / (dense_scores.max() - dense_scores.min() + 1e-8)
        sparse_norm = (sparse_scores - sparse_scores.min()) / (sparse_scores.max() - sparse_scores.min() + 1e-8)
        
        # Combine (Reciprocal Rank Fusion is an alternative)
        combined = alpha * dense_norm + (1 - alpha) * sparse_norm
        
        top_indices = np.argsort(combined)[-top_k:][::-1]
        return [(self.documents[i], combined[i]) for i in top_indices]

# Reciprocal Rank Fusion (RRF) — rank-based combination
def rrf_combine(dense_results: list, sparse_results: list, k: int = 60):
    """Combine ranked lists using Reciprocal Rank Fusion."""
    scores = {}
    for rank, (doc_id, _) in enumerate(dense_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    for rank, (doc_id, _) in enumerate(sparse_results):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

---

## 5. Parent-Child & Hierarchical Chunking

```python
# Problem: Small chunks = precise retrieval but lose context
# Solution: Retrieve small chunks, but pass their parent (larger context) to LLM

from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

class ParentChildRetriever:
    def __init__(self, embedder):
        self.embedder = embedder
        self.child_chunks = []     # Small chunks (for retrieval)
        self.parent_chunks = []    # Large chunks (for context)
        self.child_to_parent = {}  # Mapping
    
    def ingest(self, documents: list[str]):
        # Create parent chunks (large)
        parent_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        # Create child chunks (small, for precise retrieval)
        child_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
        
        for doc in documents:
            parents = parent_splitter.split_text(doc)
            for parent_id, parent in enumerate(parents):
                self.parent_chunks.append(parent)
                children = child_splitter.split_text(parent)
                for child in children:
                    child_id = len(self.child_chunks)
                    self.child_chunks.append(child)
                    self.child_to_parent[child_id] = parent_id
        
        # Embed only child chunks
        self.child_embeddings = self.embedder.encode(self.child_chunks)
    
    def retrieve(self, query: str, top_k: int = 3):
        """Retrieve child chunks, return their parents."""
        query_emb = self.embedder.encode(query)
        similarities = np.dot(self.child_embeddings, query_emb)
        top_child_ids = np.argsort(similarities)[-top_k:][::-1]
        
        # Return unique parent chunks
        parent_ids = list(set(self.child_to_parent[cid] for cid in top_child_ids))
        return [self.parent_chunks[pid] for pid in parent_ids]

# Result: Precise retrieval (small chunks) + rich context (parent chunks)
```

---

## 6. Self-RAG (Adaptive Retrieval)

```python
# Self-RAG: Model decides WHEN to retrieve and evaluates retrieved docs

class SelfRAG:
    """
    Self-RAG flow:
    1. Given query, decide if retrieval is needed
    2. If yes, retrieve and evaluate relevance of each doc
    3. Generate answer using only relevant docs
    4. Self-evaluate: is answer supported by evidence?
    """
    
    def __init__(self, retriever, llm_client):
        self.retriever = retriever
        self.client = llm_client
    
    def needs_retrieval(self, query: str) -> bool:
        """Decide if external knowledge is needed."""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Can you answer this question confidently without looking anything up? Answer YES or NO only.\n\nQuestion: {query}"}],
            temperature=0,
        )
        return "NO" in response.choices[0].message.content.upper()
    
    def evaluate_relevance(self, query: str, doc: str) -> bool:
        """Check if a retrieved document is relevant to the query."""
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Is this document relevant to answering the question? Answer RELEVANT or IRRELEVANT.\n\nQuestion: {query}\nDocument: {doc}"}],
            temperature=0,
        )
        return "RELEVANT" in response.choices[0].message.content.upper()
    
    def query(self, question: str) -> str:
        # Step 1: Decide if retrieval needed
        if not self.needs_retrieval(question):
            return self.generate_without_context(question)
        
        # Step 2: Retrieve and filter relevant docs
        candidates = self.retriever.retrieve(question, top_k=10)
        relevant_docs = [doc for doc in candidates if self.evaluate_relevance(question, doc)]
        
        if not relevant_docs:
            return "I couldn't find relevant information to answer this question."
        
        # Step 3: Generate with relevant context only
        return self.generate_with_context(question, relevant_docs)
```

---

## 7. Knowledge Graph + RAG

```python
# Combine structured knowledge (KG) with unstructured text (RAG)
# KG provides: relationships, entities, structured facts
# RAG provides: detailed explanations, context, nuance

class KGAugmentedRAG:
    """
    1. Extract entities from query
    2. Look up related entities in knowledge graph
    3. Use KG context + vector retrieval together
    """
    
    def __init__(self, kg_client, vector_retriever, llm_client):
        self.kg = kg_client  # Neo4j, NetworkX, etc.
        self.retriever = vector_retriever
        self.client = llm_client
    
    def extract_entities(self, query: str) -> list[str]:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Extract key entities (people, technologies, concepts) from: '{query}'. Return as comma-separated list."}],
        )
        return [e.strip() for e in response.choices[0].message.content.split(",")]
    
    def get_kg_context(self, entities: list[str]) -> str:
        """Get structured relationships from knowledge graph."""
        facts = []
        for entity in entities:
            # Query graph for related nodes
            neighbors = self.kg.get_neighbors(entity)
            for rel_type, target in neighbors:
                facts.append(f"{entity} --[{rel_type}]--> {target}")
        return "\n".join(facts)
    
    def query(self, question: str) -> str:
        # Get structured context from KG
        entities = self.extract_entities(question)
        kg_context = self.get_kg_context(entities)
        
        # Get unstructured context from vector search
        docs = self.retriever.retrieve(question, top_k=5)
        
        # Combine both for generation
        combined_context = f"Structured facts:\n{kg_context}\n\nRelevant documents:\n{'---'.join(docs)}"
        return self.generate(question, combined_context)

# When to use KG+RAG:
# - Complex relationships matter (org charts, dependencies)
# - Multi-hop reasoning ("Who manages the person who wrote module X?")
# - Need consistent, verifiable facts
```

---

## Interview Questions

### Beginner
1. **What is the difference between bi-encoder and cross-encoder?** Bi-encoder embeds query and documents independently — fast (can pre-compute doc embeddings) but less accurate. Cross-encoder processes query+document together — slow (must score each pair) but more accurate. Use bi-encoder for retrieval, cross-encoder for re-ranking.
2. **What is hybrid search?** Combining dense retrieval (embeddings, semantic) with sparse retrieval (BM25, keyword-based). Dense catches meaning ("car" → "automobile"), sparse catches exact terms (error codes, names). Combined gives better recall than either alone.
3. **Why use chunking overlap?** Information at chunk boundaries gets split. Overlap ensures that facts spanning two chunks still appear fully in at least one chunk. Typical overlap: 10-20% of chunk size. Without it, you might miss relevant context.

### Intermediate
4. **Explain HyDE and when to use it.** Generate a hypothetical answer to the query, embed that instead of the query. Works because hypothetical answers are in same embedding space as real documents. Best for: factual Q&A, technical docs. Less useful for: keyword searches, when query is already well-formed.
5. **How does parent-child retrieval work?** Create small child chunks (precise retrieval) and larger parent chunks (rich context). Index children in vector DB. On retrieval, find matching children, then return their parent chunks to the LLM. Gets precision of small chunks with context of large chunks.
6. **Compare re-ranking approaches.** Cross-encoder (local, ms-marco models): fast, free, good quality. Cohere Rerank (API): highest quality, easy to use, costs money. ColBERT (token-level interaction): balance of speed and accuracy. FlashRank (distilled): very fast, slightly lower quality.

### Advanced
7. **Design a Self-RAG system.** Four decision points: 1) Should I retrieve? (skip for simple questions), 2) Is each retrieved doc relevant? (filter noise), 3) Is my answer supported by the docs? (prevent hallucination), 4) Is the answer useful? (quality check). Each requires a critic model or LLM judge. Trade-off: more LLM calls vs better quality.
8. **How would you combine KG and RAG for a complex domain?** Build entity extraction → KG construction pipeline. Store relationships in graph DB. On query: extract entities → traverse KG for structured context → vector search for detailed docs → merge contexts. KG handles "who/what/when" relationships; RAG handles "how/why" explanations. Example: medical diagnosis (KG: drug interactions, RAG: clinical guidelines).
9. **How do you handle multi-hop questions in RAG?** Decompose complex query into sub-queries. Retrieve for each sub-query. Chain retrieval: answer sub-query 1, use that to formulate sub-query 2. Alternatively: retrieve broadly, let LLM synthesize across multiple chunks. KG traversal handles relationship chains better than flat vector search.

---

## Hands-On Exercise
1. Implement query rewriting — compare retrieval quality before/after
2. Build HyDE and measure improvement on 10 test queries
3. Add cross-encoder re-ranking to basic RAG (compare top-5 quality)
4. Implement hybrid search with BM25 + dense and tune alpha
5. Build parent-child retriever and compare with flat chunking
6. Create a Self-RAG system that decides when to retrieve
