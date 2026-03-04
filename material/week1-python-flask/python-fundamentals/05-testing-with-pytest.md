# Day 5: Testing with pytest

## Why Testing Matters for AI Engineers
- Validate AI pipeline outputs
- Test API endpoints
- Ensure embedding quality
- Regression testing for prompt changes
- CI/CD pipelines require tests

---

## 1. pytest Basics

```bash
# Install
pip install pytest pytest-asyncio pytest-cov
```

### First Test
```python
# test_basics.py

def add(a: int, b: int) -> int:
    return a + b

def test_add():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_add_strings():
    """Should handle string concatenation."""
    assert add("hello", " world") == "hello world"

# Run: pytest test_basics.py -v
```

### Test Organization
```
project/
├── src/
│   ├── services/
│   │   ├── embedding_service.py
│   │   └── llm_service.py
│   └── models/
│       └── document.py
├── tests/
│   ├── conftest.py           # Shared fixtures
│   ├── test_embedding.py
│   ├── test_llm.py
│   └── test_document.py
└── pytest.ini
```

### pytest.ini
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow
    integration: marks integration tests
```

## 2. Assertions

```python
# Basic assertions
def test_assertions():
    # Equality
    assert 1 + 1 == 2
    assert "hello" != "world"
    
    # Truthiness
    assert True
    assert not False
    assert [] == []
    assert not []  # empty list is falsy
    
    # Containment
    assert "hello" in "hello world"
    assert 3 in [1, 2, 3]
    assert "key" in {"key": "value"}
    
    # Type checking
    assert isinstance(42, int)
    assert isinstance("hello", str)
    
    # Approximate (for floats)
    from pytest import approx
    assert 0.1 + 0.2 == approx(0.3)
    assert [0.1, 0.2] == approx([0.1, 0.2], abs=1e-6)
    
    # None
    assert None is None
    result = some_function()
    assert result is not None

# Exception testing
import pytest

def test_raises_error():
    with pytest.raises(ValueError) as exc_info:
        raise ValueError("Invalid input")
    
    assert "Invalid input" in str(exc_info.value)

def test_raises_specific():
    with pytest.raises(ZeroDivisionError):
        1 / 0
```

## 3. Fixtures (Test Setup/Teardown)

```python
# conftest.py - shared fixtures

import pytest
from dataclasses import dataclass

@dataclass
class Document:
    id: int
    title: str
    content: str
    embedding: list[float] = None

@pytest.fixture
def sample_document():
    """Provides a sample document for tests."""
    return Document(
        id=1,
        title="AI Introduction",
        content="Artificial Intelligence is the simulation of human intelligence.",
        embedding=[0.1, 0.2, 0.3]
    )

@pytest.fixture
def sample_documents():
    """Provides multiple documents."""
    return [
        Document(1, "AI Basics", "What is AI?"),
        Document(2, "ML Intro", "Machine learning overview"),
        Document(3, "RAG Guide", "How RAG works"),
    ]

@pytest.fixture
def mock_config():
    """Provides test configuration."""
    return {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
        "api_key": "test-key-123"
    }

# Fixture with setup AND teardown
@pytest.fixture
def temp_directory(tmp_path):
    """Create a temporary directory with test files."""
    # Setup
    (tmp_path / "doc1.txt").write_text("Hello World")
    (tmp_path / "doc2.txt").write_text("AI is great")
    
    yield tmp_path  # This is what the test receives
    
    # Teardown (cleanup) - happens after test
    # tmp_path is auto-cleaned by pytest

# Fixture with scope
@pytest.fixture(scope="module")
def expensive_resource():
    """Created once per module, not per test."""
    print("Setting up expensive resource...")
    resource = {"connection": "established"}
    yield resource
    print("Tearing down expensive resource...")
```

### Using Fixtures
```python
# test_document.py

def test_document_has_title(sample_document):
    assert sample_document.title == "AI Introduction"

def test_document_has_embedding(sample_document):
    assert sample_document.embedding is not None
    assert len(sample_document.embedding) == 3

def test_multiple_documents(sample_documents):
    assert len(sample_documents) == 3
    titles = [d.title for d in sample_documents]
    assert "AI Basics" in titles

def test_with_config(mock_config):
    assert mock_config["model"] == "gpt-4"
    assert mock_config["temperature"] == 0.7
```

## 4. Parametrized Tests

```python
import pytest

# Test the same function with many inputs
@pytest.mark.parametrize("input_text,expected_chunks", [
    ("Hello world", 1),
    ("A" * 1000, 2),  # Should split into 2 chunks
    ("", 0),           # Empty string
    ("Short text", 1),
])
def test_chunking(input_text, expected_chunks):
    chunks = chunk_text(input_text, chunk_size=500)
    assert len(chunks) == expected_chunks

# Multiple parameters
@pytest.mark.parametrize("model,temperature,expected", [
    ("gpt-4", 0.0, "deterministic"),
    ("gpt-4", 1.0, "creative"),
    ("gpt-3.5-turbo", 0.5, "balanced"),
])
def test_model_config(model, temperature, expected):
    config = create_config(model, temperature)
    assert config["mode"] == expected
```

## 5. Mocking (Critical for AI Testing)

```python
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# Simple mock
def test_with_mock():
    # Create a mock that behaves like an API client
    mock_client = Mock()
    mock_client.generate.return_value = "AI response"
    
    result = mock_client.generate("What is AI?")
    assert result == "AI response"
    mock_client.generate.assert_called_once_with("What is AI?")

# Patching (replace real objects with mocks)
def test_llm_service():
    """Test LLM service without making real API calls."""
    with patch("services.llm_service.openai.ChatCompletion.create") as mock:
        mock.return_value = {
            "choices": [{"message": {"content": "AI is fascinating"}}]
        }
        
        service = LLMService()
        response = service.generate("What is AI?")
        
        assert response == "AI is fascinating"
        mock.assert_called_once()

# Mock for async functions
@pytest.mark.asyncio
async def test_async_embedding():
    mock_service = AsyncMock()
    mock_service.generate_embedding.return_value = [0.1, 0.2, 0.3]
    
    result = await mock_service.generate_embedding("test text")
    assert result == [0.1, 0.2, 0.3]

# Patching environment variables
def test_with_env_vars():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        import os
        assert os.environ["OPENAI_API_KEY"] == "test-key"
```

## 6. Testing Async Code

```python
import pytest
import asyncio

# Install: pip install pytest-asyncio

@pytest.mark.asyncio
async def test_async_function():
    result = await async_fetch_data()
    assert result is not None

@pytest.mark.asyncio
async def test_concurrent_operations():
    results = await asyncio.gather(
        async_operation_1(),
        async_operation_2(),
    )
    assert len(results) == 2

# Async fixtures
@pytest.fixture
async def async_client():
    client = await create_async_client()
    yield client
    await client.close()
```

## 7. Testing Flask APIs

```python
import pytest
from flask import Flask

# Simple Flask app for testing
def create_app():
    app = Flask(__name__)
    
    @app.route("/api/health")
    def health():
        return {"status": "healthy"}
    
    @app.route("/api/embed", methods=["POST"])
    def embed():
        data = request.get_json()
        return {"embedding": [0.1, 0.2, 0.3], "text": data["text"]}
    
    return app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"

def test_embed(client):
    response = client.post(
        "/api/embed",
        json={"text": "What is AI?"}
    )
    assert response.status_code == 200
    assert "embedding" in response.json
    assert len(response.json["embedding"]) == 3

def test_embed_missing_text(client):
    response = client.post("/api/embed", json={})
    assert response.status_code == 400
```

## 8. Test Patterns for AI Systems

```python
# Testing embedding similarity
def test_similar_texts_have_high_similarity():
    """Similar texts should produce similar embeddings."""
    embedding_service = EmbeddingService()
    
    emb1 = embedding_service.embed("machine learning is great")
    emb2 = embedding_service.embed("ML is awesome")
    emb3 = embedding_service.embed("cooking recipes for dinner")
    
    sim_related = cosine_similarity(emb1, emb2)
    sim_unrelated = cosine_similarity(emb1, emb3)
    
    assert sim_related > sim_unrelated
    assert sim_related > 0.7  # Related texts should be similar

# Testing RAG pipeline
def test_rag_retrieves_relevant_context():
    """RAG should retrieve relevant documents."""
    rag = RAGPipeline()
    rag.index_documents([
        "Python is a programming language",
        "Flask is a web framework",
        "Redis is a caching system",
    ])
    
    results = rag.retrieve("web development framework")
    assert any("Flask" in r.text for r in results)

# Testing prompt templates
def test_prompt_template():
    template = "Answer based on context: {context}\nQuestion: {question}"
    prompt = template.format(
        context="AI uses neural networks",
        question="What does AI use?"
    )
    assert "neural networks" in prompt
    assert "What does AI use?" in prompt
```

## 9. Coverage

```bash
# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Output:
# Name                   Stmts   Miss  Cover   Missing
# -----------------------------------------------------
# src/services/llm.py       45      5    89%   23-27
# src/services/embed.py     32      2    94%   18-19
# src/models/document.py    20      0   100%
# -----------------------------------------------------
# TOTAL                     97      7    93%
```

---

## Exercises

### Exercise 1: Test a Text Chunker
```python
# Given this function:
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

# Write tests for:
# 1. Empty text
# 2. Text shorter than chunk_size
# 3. Text exactly chunk_size
# 4. Long text with overlap verification
# 5. Various chunk sizes
# 6. Parametrized tests for edge cases

# TODO: Write at least 8 tests
```

### Exercise 2: Test with Mocks
```python
# Test this service without making real API calls:
class AIService:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def generate_response(self, prompt: str) -> str:
        # Would call OpenAI API
        pass
    
    def generate_embedding(self, text: str) -> list[float]:
        # Would call embedding API
        pass
    
    def search_similar(self, query: str, top_k: int = 5) -> list[dict]:
        embedding = self.generate_embedding(query)
        # Would search vector DB
        pass

# Write tests mocking all external calls
# TODO: Implement
```

---

## Key Takeaways for Day 5
1. **pytest** is the standard (not unittest)
2. **Fixtures** = reusable test setup/teardown
3. **Parametrize** = test many inputs with one function
4. **Mocking** = test without real APIs (critical for AI)
5. **Test Flask** with `app.test_client()`
6. **Coverage** target: 80%+ for core logic
7. For AI: test similarity, relevance, not exact outputs
