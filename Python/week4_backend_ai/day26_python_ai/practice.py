#!/usr/bin/env python3
"""Day 26 - NumPy, Pandas & AI Practice"""

print("=" * 50)
print("PYTHON FOR AI - PRACTICE")
print("=" * 50)


# ============================================
# 1. DATA PIPELINE CONCEPT
# ============================================
print("\n--- 1. Data Pipeline ---")

DATA_PIPELINE = """
Typical AI/ML Data Pipeline:
───────────────────────────────────────────────────

1. Data Collection
   └─ APIs, databases, files, web scraping

2. Data Cleaning (Pandas)
   ├─ Handle missing values
   ├─ Remove duplicates
   ├─ Fix data types
   └─ Normalize text

3. Feature Engineering (NumPy/Pandas)
   ├─ Create new features
   ├─ Encode categorical variables
   ├─ Scale numerical features
   └─ Generate embeddings

4. Model Integration (OpenAI/HuggingFace)
   ├─ Text classification
   ├─ Sentiment analysis
   ├─ Text generation
   └─ Embeddings & similarity

5. Serving (FastAPI)
   └─ REST API endpoints
"""
print(DATA_PIPELINE)


# ============================================
# 2. SIMPLE DATA PROCESSING EXAMPLE
# ============================================
print("\n--- 2. Data Processing Example ---")

# Simulate without requiring actual imports
class MockDataFrame:
    """Demonstrates Pandas-like operations conceptually."""
    
    def __init__(self, data):
        self.data = data
        self.columns = list(data.keys()) if data else []
    
    def head(self, n=5):
        return {k: v[:n] for k, v in self.data.items()}
    
    def describe(self):
        result = {}
        for col, values in self.data.items():
            if all(isinstance(v, (int, float)) for v in values):
                result[col] = {
                    'count': len(values),
                    'mean': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }
        return result
    
    def filter(self, condition_func):
        indices = [i for i, _ in enumerate(list(self.data.values())[0]) 
                   if condition_func(i)]
        return {k: [v[i] for i in indices] for k, v in self.data.items()}


# Create sample data
data = {
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'age': [25, 30, 35, 28, 32],
    'score': [85.5, 90.0, 78.5, 92.0, 88.5]
}

df = MockDataFrame(data)
print(f"Data columns: {df.columns}")
print(f"Head: {df.head(3)}")
print(f"Stats: {df.describe()}")


# ============================================
# 3. EMBEDDING SIMILARITY CONCEPT
# ============================================
print("\n--- 3. Embedding Similarity ---")

def cosine_similarity(a, b):
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(x ** 2 for x in b) ** 0.5
    return dot_product / (norm_a * norm_b)


# Simulated embeddings (normally 1536 dimensions from OpenAI)
embedding_python = [0.1, 0.8, 0.3, 0.9, 0.2]
embedding_java = [0.2, 0.7, 0.4, 0.8, 0.3]
embedding_cooking = [0.9, 0.1, 0.8, 0.1, 0.7]

print("Cosine Similarities:")
print(f"  Python vs Java: {cosine_similarity(embedding_python, embedding_java):.4f}")
print(f"  Python vs Cooking: {cosine_similarity(embedding_python, embedding_cooking):.4f}")
print("  (Higher = more similar)")


# ============================================
# 4. TEXT PREPROCESSING
# ============================================
print("\n--- 4. Text Preprocessing ---")

import re
from collections import Counter


def preprocess_text(text):
    """Basic text preprocessing."""
    # Lowercase
    text = text.lower()
    # Remove special characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Tokenize
    tokens = text.split()
    # Remove common stopwords
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for'}
    tokens = [t for t in tokens if t not in stopwords]
    return tokens


def get_word_frequency(texts):
    """Get word frequency from list of texts."""
    all_tokens = []
    for text in texts:
        all_tokens.extend(preprocess_text(text))
    return Counter(all_tokens).most_common(10)


sample_texts = [
    "Python is a great programming language for AI.",
    "Machine learning uses Python extensively.",
    "AI and machine learning are transforming industries."
]

print("Word Frequency:")
for word, count in get_word_frequency(sample_texts):
    print(f"  {word}: {count}")


# ============================================
# 5. SIMPLE VECTOR DATABASE CONCEPT
# ============================================
print("\n--- 5. Vector Database Concept ---")


class SimpleVectorDB:
    """Simple in-memory vector database concept."""
    
    def __init__(self):
        self.vectors = []  # List of (id, text, embedding)
    
    def add(self, id, text, embedding):
        self.vectors.append((id, text, embedding))
    
    def search(self, query_embedding, top_k=3):
        """Find most similar vectors."""
        similarities = []
        for id, text, embedding in self.vectors:
            sim = cosine_similarity(query_embedding, embedding)
            similarities.append((id, text, sim))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[2], reverse=True)
        return similarities[:top_k]


# Demo
db = SimpleVectorDB()
db.add(1, "Python programming", [0.1, 0.8, 0.3, 0.9, 0.2])
db.add(2, "Data science", [0.2, 0.7, 0.5, 0.8, 0.3])
db.add(3, "Web development", [0.3, 0.6, 0.4, 0.7, 0.4])
db.add(4, "Machine learning", [0.1, 0.9, 0.4, 0.9, 0.2])

query = [0.1, 0.85, 0.35, 0.88, 0.22]  # Similar to Python/ML
print("Search results for query (similar to Python/ML):")
for id, text, sim in db.search(query):
    print(f"  {text}: {sim:.4f}")


# ============================================
# 6. RAG PIPELINE CONCEPT
# ============================================
print("\n--- 6. RAG Pipeline Concept ---")

RAG_CONCEPT = """
RAG (Retrieval-Augmented Generation) Pipeline:
──────────────────────────────────────────────────

1. Document Ingestion
   ├─ Split documents into chunks
   ├─ Generate embeddings for each chunk
   └─ Store in vector database

2. Query Processing
   ├─ Generate embedding for user query
   ├─ Search vector DB for similar chunks
   └─ Retrieve top-k relevant chunks

3. Context Building
   ├─ Combine retrieved chunks
   └─ Format as context for LLM

4. Generation
   ├─ Send context + query to LLM
   └─ Generate response based on context

5. Post-processing
   ├─ Validate response
   ├─ Add citations
   └─ Return to user

Code structure:
──────────────────────────────────────────────────
class RAGPipeline:
    def __init__(self, vector_db, llm_client):
        self.db = vector_db
        self.llm = llm_client
    
    def ingest(self, documents):
        for doc in documents:
            chunks = self.split(doc)
            for chunk in chunks:
                embedding = self.embed(chunk)
                self.db.add(chunk, embedding)
    
    def query(self, question):
        # Embed question
        query_embedding = self.embed(question)
        
        # Retrieve relevant chunks
        chunks = self.db.search(query_embedding, top_k=5)
        
        # Build context
        context = "\\n".join(chunk.text for chunk in chunks)
        
        # Generate response
        response = self.llm.generate(
            f"Context: {context}\\n\\nQuestion: {question}"
        )
        
        return response
"""
print(RAG_CONCEPT)


# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 50)
print("KEY TAKEAWAYS")
print("=" * 50)
print("""
NumPy:
  - Foundation for numerical computing
  - Vectorized operations for performance
  - Essential for ML model inputs/outputs

Pandas:
  - Data loading, cleaning, transformation
  - GroupBy for aggregations
  - Time series handling

OpenAI API:
  - Chat completions for text generation
  - Embeddings for similarity search
  - Function calling for tool use
  - Assistants for stateful conversations

Integration Patterns:
  - RAG for knowledge-based responses
  - Vector databases for semantic search
  - Streaming for real-time responses
  - Caching for cost optimization

Next Steps:
  - Try LangChain for complex chains
  - Explore HuggingFace for local models
  - Build a RAG chatbot
""")
