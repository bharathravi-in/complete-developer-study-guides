# Testing AI Applications — Patterns & Best Practices

> How to test systems where outputs are probabilistic, not deterministic.

---

## The Challenge: AI is Non-Deterministic

**Traditional Testing:**
```python
def test_add():
    assert add(2, 3) == 5  # Always true
```

**AI Testing:**
```python
def test_llm_answer():
    answer = llm.generate("What is Python?")
    assert answer == "Python is a programming language"  # ❌ FAILS
    # Actual output: "Python is a versatile, high-level programming language..."
```

**The problem**: AI outputs vary. Testing requires **different strategies**.

---

## 1. Testing RAG Retrieval

### Test Strategy: Semantic similarity, not exact match

```python
import pytest
from sentence_transformers import SentenceTransformer, util

@pytest.fixture
def similarity_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def test_retrieval_returns_relevant_chunks(rag_pipeline, similarity_model):
    """Test that retrieved chunks are semantically relevant."""
    # Index test documents
    rag_pipeline.index_documents([
        {"id": "1", "text": "Python is a programming language used for AI"},
        {"id": "2", "text": "React is a JavaScript library for building UIs"},
        {"id": "3", "text": "Machine learning uses algorithms to learn from data"},
    ])
    
    # Query
    results = rag_pipeline.retrieve("Tell me about programming languages for AI")
    
    # Assertions
    assert len(results) > 0, "Should return at least one result"
    
    # Check that top result is semantically relevant
    query_embedding = similarity_model.encode("programming languages for AI")
    top_chunk_embedding = similarity_model.encode(results[0]['text'])
    similarity = util.cos_sim(query_embedding, top_chunk_embedding).item()
    
    assert similarity > 0.5, f"Top result should be relevant (similarity: {similarity})"
    
    # Check that irrelevant docs are ranked lower
    top_ids = [r['id'] for r in results[:2]]
    assert "2" not in top_ids, "React doc should not be in top results"


def test_retrieval_respects_filters(rag_pipeline):
    """Test metadata filtering works."""
    rag_pipeline.index_documents([
        {"id": "1", "text": "...", "category": "python"},
        {"id": "2", "text": "...", "category": "javascript"},
    ])
    
    results = rag_pipeline.retrieve("programming", filter={"category": "python"})
    
    assert all(r['category'] == "python" for r in results)


def test_retrieval_scores_are_consistent(rag_pipeline):
    """Test that same query returns similar scores."""
    rag_pipeline.index_documents([...])
    
    results1 = rag_pipeline.retrieve("What is AI?")
    results2 = rag_pipeline.retrieve("What is AI?")
    
    # Scores should be identical for same query (deterministic retrieval)
    assert results1[0]['score'] == pytest.approx(results2[0]['score'], abs=0.01)
```

---

## 2. Testing LLM Generation

### Strategy 1: Use a Judge LLM

```python
def llm_judge(question: str, answer: str, ground_truth: str) -> float:
    """Use an LLM to judge if the answer is correct."""
    prompt = f"""You are evaluating an AI assistant's answer.

Question: {question}
Expected answer: {ground_truth}
Actual answer: {answer}

Rate the answer from 0.0 to 1.0 based on:
- Correctness (does it answer the question?)
- Completeness (covers all key points?)
- Factual accuracy (no hallucinations?)

Return only a number between 0.0 and 1.0."""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    
    return float(response.choices[0].message.content.strip())


def test_llm_answer_quality():
    """Test LLM generates high-quality answers."""
    test_cases = [
        {
            "question": "What is the GIL in Python?",
            "ground_truth": "The Global Interpreter Lock allows only one thread to execute Python bytecode at a time",
        },
        {
            "question": "How does RAG work?",
            "ground_truth": "RAG retrieves relevant documents and uses them as context for LLM generation",
        },
    ]
    
    for case in test_cases:
        answer = rag_pipeline.generate(case["question"])
        score = llm_judge(case["question"], answer, case["ground_truth"])
        assert score >= 0.7, f"Answer quality too low: {score}\nAnswer: {answer}"
```

### Strategy 2: Assert on Properties

```python
def test_llm_answer_properties(rag_pipeline):
    """Test properties of the answer, not exact content."""
    answer = rag_pipeline.generate("What is Python?")
    
    # Property 1: Should be a reasonable length (not empty, not a novel)
    assert 50 < len(answer) < 500, f"Answer length unexpected: {len(answer)}"
    
    # Property 2: Should mention key terms
    assert any(term in answer.lower() for term in ["python", "language", "programming"])
    
    # Property 3: Should not contain certain patterns (hallucination indicators)
    assert "I don't know" not in answer.lower()
    assert "as an AI" not in answer.lower()  # Avoid generic AI disclaimers
    
    # Property 4: Should cite sources (RAG-specific)
    assert "[Source:" in answer or "According to" in answer


def test_llm_follows_instructions(rag_pipeline):
    """Test that LLM respects system prompt instructions."""
    answer = rag_pipeline.generate(
        "What is quantum computing?",
        system_prompt="Answer in exactly 2 sentences."
    )
    
    # Count sentences (rough heuristic)
    sentence_count = answer.count('.') + answer.count('!') + answer.count('?')
    assert 2 <= sentence_count <= 3, f"Should be 2 sentences, got {sentence_count}"
```

---

## 3. Mocking External APIs

### Mock OpenAI API

```python
from unittest.mock import Mock, patch
import pytest

@pytest.fixture
def mock_openai_embeddings(monkeypatch):
    """Mock OpenAI embeddings API."""
    mock_response = Mock()
    mock_response.data = [Mock(embedding=[0.1] * 1536)]
    
    with patch('openai.Embeddings.create', return_value=mock_response):
        yield


@pytest.fixture
def mock_openai_chat(monkeypatch):
    """Mock OpenAI chat completions API."""
    mock_response = Mock()
    mock_response.choices = [
        Mock(message=Mock(content="This is a test response"))
    ]
    mock_response.usage = Mock(total_tokens=100, prompt_tokens=50, completion_tokens=50)
    
    with patch('openai.ChatCompletion.create', return_value=mock_response):
        yield


def test_rag_pipeline_without_api_calls(mock_openai_embeddings, mock_openai_chat):
    """Test RAG pipeline with mocked LLM calls (no API costs)."""
    rag = RAGPipeline()
    rag.index_document("Python is a programming language")
    
    answer = rag.generate("What is Python?")
    
    assert answer == "This is a test response"  # Our mocked response
```

### VCR.py for Recording API Responses

```python
# pip install vcrpy pytest-vcr

import vcr
import pytest

@pytest.fixture(scope="module")
def vcr_config():
    """Configure VCR to hide API keys."""
    return {
        "filter_headers": [("authorization", "DUMMY")],
        "filter_post_data_parameters": [("api_key", "DUMMY")],
    }

@vcr.use_cassette('tests/fixtures/vcr_cassettes/test_embedding.yaml')
def test_embedding_service_real_api():
    """First run: records real API response. Subsequent runs: replays from file."""
    service = EmbeddingService()
    vector = service.embed("test text")
    
    assert len(vector) == 1536
    assert all(isinstance(v, float) for v in vector)

# After first run, this test uses zero API calls!
```

---

## 4. Integration Testing RAG End-to-End

```python
@pytest.mark.integration
def test_rag_pipeline_end_to_end():
    """Full integration test of the RAG pipeline."""
    # Setup
    rag = RAGPipeline()
    rag.setup()  # Initialize Qdrant collection
    
    # Index documents
    documents = [
        Document(id="1", content="Python is a high-level programming language."),
        Document(id="2", content="Flask is a web framework for Python."),
        Document(id="3", content="RAG stands for Retrieval-Augmented Generation."),
    ]
    rag.index_documents(documents)
    
    # Query
    response = rag.query("What is Flask?")
    
    # Assertions
    assert response["answer"] is not None
    assert "flask" in response["answer"].lower()
    assert "python" in response["answer"].lower()  # Should mention Python too
    assert len(response["sources"]) > 0
    assert response["sources"][0]["document"] == "2"  # Flask doc should be top source
    
    # Cleanup
    rag.teardown()


@pytest.mark.integration
@pytest.mark.slow
def test_rag_handles_large_documents():
    """Test chunking and retrieval on large documents."""
    rag = RAGPipeline()
    rag.setup()
    
    # Create a large document
    large_text = "Python is versatile. " * 1000  # 20K chars
    rag.index_document(Document(id="large", content=large_text))
    
    # Should chunk into multiple pieces
    results = rag.retrieve("Python")
    assert len(results) >= 5  # Should have created multiple chunks
    
    rag.teardown()
```

---

## 5. Testing Embeddings

### Test Semantic Properties

```python
def test_similar_texts_have_similar_embeddings(embedding_service):
    """Semantically similar texts should have high cosine similarity."""
    emb1 = embedding_service.embed("machine learning is great")
    emb2 = embedding_service.embed("ML is awesome")
    emb3 = embedding_service.embed("cooking recipes for dinner")
    
    sim_related = cosine_similarity(emb1, emb2)
    sim_unrelated = cosine_similarity(emb1, emb3)
    
    assert sim_related > 0.7, f"Related similarity too low: {sim_related}"
    assert sim_related > sim_unrelated, "Related should be more similar than unrelated"


def test_embedding_dimensions(embedding_service):
    """Embeddings should have expected dimensions."""
    vector = embedding_service.embed("test")
    
    assert len(vector) == 384  # or 1536 for OpenAI
    assert all(isinstance(v, float) for v in vector)
    assert all(-1 <= v <= 1 for v in vector)  # Normalized embeddings


def test_embedding_caching(embedding_service):
    """Embeddings should be cached for same input."""
    text = "test text for caching"
    
    import time
    
    start = time.time()
    emb1 = embedding_service.embed(text)
    first_time = time.time() - start
    
    start = time.time()
    emb2 = embedding_service.embed(text)  # Should hit cache
    second_time = time.time() - start
    
    assert emb1 == emb2
    assert second_time < first_time / 10, "Cache should be much faster"
```

---

## 6. Performance & Load Testing

```python
import asyncio
import time
import pytest

@pytest.mark.performance
def test_embedding_batch_performance(embedding_service):
    """Batch embedding should be faster than individual calls."""
    texts = ["test text"] * 100
    
    # Individual calls
    start = time.time()
    for text in texts:
        embedding_service.embed(text)
    individual_time = time.time() - start
    
    # Batch call
    start = time.time()
    embedding_service.embed_batch(texts)
    batch_time = time.time() - start
    
    assert batch_time < individual_time / 5, "Batch should be much faster"


@pytest.mark.performance
async def test_rag_concurrent_queries(rag_pipeline):
    """Test RAG pipeline handles concurrent queries."""
    queries = [
        "What is Python?",
        "Explain Flask framework",
        "How does RAG work?",
    ] * 10  # 30 queries
    
    start = time.time()
    tasks = [rag_pipeline.query_async(q) for q in queries]
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    
    assert all(r["answer"] for r in results)
    assert elapsed < 20, f"30 queries took {elapsed}s (should be <20s with concurrency)"


@pytest.mark.load
def test_rag_under_load(rag_pipeline):
    """Test system behavior under sustained load."""
    queries_per_second = 10
    duration_seconds = 30
    
    errors = []
    latencies = []
    
    for i in range(queries_per_second * duration_seconds):
        try:
            start = time.time()
            rag_pipeline.query("test query")
            latency = time.time() - start
            latencies.append(latency)
        except Exception as e:
            errors.append(str(e))
        
        time.sleep(1 / queries_per_second)
    
    # Assertions
    error_rate = len(errors) / len(latencies)
    p95_latency = sorted(latencies)[int(0.95 * len(latencies))]
    
    assert error_rate < 0.01, f"Error rate too high: {error_rate*100}%"
    assert p95_latency < 2.0, f"P95 latency too high: {p95_latency}s"
```

---

## 7. Testing Chunking Strategies

```python
def test_chunking_respects_sentence_boundaries():
    """Chunks should not cut off mid-sentence."""
    text = "Python is great. It has many libraries. Machine learning is popular."
    chunker = RecursiveChunker(chunk_size=20, overlap=5)
    
    chunks = chunker.chunk(text)
    
    for chunk in chunks:
        # Should not start or end mid-word
        assert not chunk.text[0].islower() or chunk.text[0].isspace()
        assert chunk.text[-1] in ".!?" or chunk.text[-1].isspace()


def test_chunking_maintains_context_with_overlap():
    """Overlapping chunks should share some content."""
    text = "A B C D E F G H I J K L M N O P"
    chunker = FixedChunker(chunk_size=5, overlap=2)
    
    chunks = chunker.chunk(text)
    
    # Check overlap exists
    for i in range(len(chunks) - 1):
        chunk1_words = set(chunks[i].text.split())
        chunk2_words = set(chunks[i+1].text.split())
        overlap_words = chunk1_words & chunk2_words
        assert len(overlap_words) >= 2, "Should have at least 2 overlapping words"


def test_chunking_handles_edge_cases():
    """Test chunking on empty, small, and large texts."""
    chunker = RecursiveChunker(chunk_size=100, overlap=10)
    
    # Empty
    assert chunker.chunk("") == []
    
    # Smaller than chunk size
    chunks = chunker.chunk("Short text.")
    assert len(chunks) == 1
    assert chunks[0].text == "Short text."
    
    # Much larger
    large_text = "Word. " * 1000
    chunks = chunker.chunk(large_text)
    assert len(chunks) > 5
    assert all(len(c.text) <= 120 for c in chunks)  # With some tolerance
```

---

## 8. Test Fixtures & Utilities

```python
# conftest.py
import pytest
from your_app import create_app, db
from your_app.services import RAGPipeline, EmbeddingService

@pytest.fixture(scope="session")
def app():
    """Create app with test config."""
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def rag_pipeline(app):
    """RAG pipeline with test configuration."""
    with app.app_context():
        pipeline = RAGPipeline(
            collection_name="test_collection",
            embedding_model="all-MiniLM-L6-v2",  # Fast for testing
        )
        pipeline.setup()
        yield pipeline
        pipeline.teardown()  # Cleanup


@pytest.fixture
def sample_documents():
    """Reusable test documents."""
    return [
        {"id": "1", "text": "Python is a programming language.", "metadata": {"type": "lang"}},
        {"id": "2", "text": "Flask is a web framework.", "metadata": {"type": "framework"}},
        {"id": "3", "text": "RAG improves LLM accuracy.", "metadata": {"type": "ai"}},
    ]
```

---

## 9. Testing Prompts

```python
def test_prompt_template_renders_correctly():
    """Test that prompt templates handle all variables."""
    template = """Answer based on context: {context}
Question: {question}
Answer in {format} format."""
    
    rendered = template.format(
        context="Python is a language",
        question="What is Python?",
        format="JSON"
    )
    
    assert "Python is a language" in rendered
    assert "What is Python?" in rendered
    assert "JSON format" in rendered


def test_prompt_respects_token_limits():
    """Test that prompts don't exceed model context window."""
    import tiktoken
    
    encoder = tiktoken.encoding_for_model("gpt-4")
    
    # Build prompt
    context = "Some context. " * 1000  # Large context
    prompt = build_rag_prompt(context=context, question="What is X?")
    
    tokens = len(encoder.encode(prompt))
    
    # GPT-4 limit is 8192, leave room for response
    assert tokens < 7000, f"Prompt too long: {tokens} tokens"


def test_system_prompt_prevents_hallucination():
    """Test that system prompt instructs LLM to stay grounded."""
    system_prompt = "Answer ONLY based on the provided context."
    
    # These keywords should be in the system prompt
    assert "only" in system_prompt.lower()
    assert "context" in system_prompt.lower()
```

---

## Key Takeaways
1. **Test properties, not exact outputs** (AI is non-deterministic)
2. **Use judge LLMs** for quality evaluation
3. **Mock external APIs** to avoid costs and flakiness
4. **VCR.py** records real API responses for replay
5. **Integration tests** for end-to-end RAG pipelines
6. **Performance tests** for latency and concurrency
7. **Test semantic properties** of embeddings and retrieval
8. **Fixtures** make tests clean and reusable
