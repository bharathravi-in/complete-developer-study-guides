# Production Architecture Patterns for AI Systems

## 1. Clean Architecture for AI Apps

### Layer Diagram
```
┌─────────────────────────────────────────┐
│           ROUTES / CONTROLLERS          │  ← HTTP layer (Flask routes)
│         Thin: parse input, return JSON  │
├─────────────────────────────────────────┤
│             SERVICE LAYER               │  ← Business logic
│         RAGService, LLMService,         │
│         EmbeddingService, CacheService  │
├─────────────────────────────────────────┤
│           REPOSITORY LAYER              │  ← Data access
│         PostgreSQL, Qdrant, Redis,      │
│         OpenAI API, S3                  │
├─────────────────────────────────────────┤
│             DOMAIN MODELS               │  ← Dataclasses, Pydantic
│         Document, Chunk, User, Chat     │
└─────────────────────────────────────────┘
```

### Rules
1. Routes NEVER call database/Qdrant directly — always through services
2. Services contain business logic and orchestrate repositories
3. Repositories handle data access and external API calls
4. Models are plain data structures — no logic

### Flask Implementation
```python
# routes/chat.py — THIN controller
@bp.route("/chat", methods=["POST"])
@require_auth
def chat():
    data = ChatRequest(**request.get_json())
    result = rag_service.query(data.question, data.chat_id)
    return jsonify(ChatResponse.from_result(result).dict())

# services/rag_service.py — BUSINESS LOGIC
class RAGService:
    def __init__(self, embedding_svc, vector_svc, llm_svc, cache_svc):
        self.embedding_svc = embedding_svc
        self.vector_svc = vector_svc
        self.llm_svc = llm_svc
        self.cache_svc = cache_svc

    def query(self, question: str, chat_id: str) -> RAGResult:
        # Check cache
        cached = self.cache_svc.get(question)
        if cached:
            return cached

        # Embed → Search → Generate
        embedding = self.embedding_svc.embed_one(question)
        chunks = self.vector_svc.search(embedding, top_k=5)
        answer = self.llm_svc.generate(question, chunks)

        result = RAGResult(question=question, answer=answer, sources=chunks)
        self.cache_svc.set(question, result, ttl=3600)
        return result
```

---

## 2. Error Handling Strategy

### Error Hierarchy
```python
class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, status_code: int = 500, error_code: str = "INTERNAL"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code

class ValidationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR")

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        super().__init__(f"{resource} '{id}' not found", status_code=404, error_code="NOT_FOUND")

class RateLimitError(AppError):
    def __init__(self):
        super().__init__("Rate limit exceeded", status_code=429, error_code="RATE_LIMITED")

class LLMError(AppError):
    def __init__(self, provider: str, message: str):
        super().__init__(f"LLM provider '{provider}' error: {message}", status_code=502, error_code="LLM_ERROR")
```

### Global Error Handler
```python
@app.errorhandler(AppError)
def handle_app_error(e: AppError):
    return jsonify({
        "error": e.error_code,
        "message": e.message,
    }), e.status_code

@app.errorhandler(Exception)
def handle_unexpected_error(e: Exception):
    logger.exception("Unexpected error")
    return jsonify({
        "error": "INTERNAL",
        "message": "An unexpected error occurred",
    }), 500
```

---

## 3. Circuit Breaker Pattern

```python
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"       # Normal — requests pass through
    OPEN = "open"           # Failing — requests blocked
    HALF_OPEN = "half_open" # Testing — allow one request

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = 0.0

    def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise LLMError("circuit_breaker", "Service unavailable (circuit open)")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
openai_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)

def call_llm(prompt: str) -> str:
    return openai_breaker.call(openai_client.chat.completions.create, ...)
```

---

## 4. Background Job Processing

### Celery Setup
```python
# tasks.py
from celery import Celery

celery_app = Celery("tasks", broker="redis://localhost:6379/0")

@celery_app.task(bind=True, max_retries=3)
def process_document(self, doc_id: str, file_path: str):
    """Background document processing."""
    try:
        # 1. Extract text
        text = extract_text(file_path)
        update_status(doc_id, "extracting")

        # 2. Chunk
        chunks = chunker.chunk(text, source=doc_id)
        update_status(doc_id, "chunking")

        # 3. Embed (batch)
        embeddings = embedding_service.embed_batch([c.text for c in chunks])
        update_status(doc_id, "embedding")

        # 4. Store in Qdrant
        vector_service.upsert(chunks, embeddings)
        update_status(doc_id, "indexed")

    except Exception as e:
        update_status(doc_id, "error", str(e))
        raise self.retry(exc=e, countdown=60)  # Retry after 60s

# Trigger from Flask route
@bp.route("/documents/upload", methods=["POST"])
def upload_document():
    file = request.files["document"]
    doc = save_document(file)
    process_document.delay(doc.id, doc.file_path)  # Async!
    return jsonify({"id": doc.id, "status": "processing"}), 202
```

---

## 5. Observability & Monitoring

### Structured Logging
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Usage
logger = logging.getLogger("ai_platform")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# Log with context
logger.info("RAG query completed", extra={
    "extra": {
        "query": question,
        "chunks_retrieved": 5,
        "top_score": 0.87,
        "latency_ms": 234,
        "tokens_used": 1500,
        "cache_hit": False,
    }
})
```

### Health Check Endpoint
```python
@app.route("/health")
def health():
    checks = {
        "api": "ok",
        "database": check_postgres(),
        "redis": check_redis(),
        "qdrant": check_qdrant(),
    }
    status = "healthy" if all(v == "ok" for v in checks.values()) else "degraded"
    code = 200 if status == "healthy" else 503
    return jsonify({"status": status, "checks": checks}), code
```

### Metrics to Track
```
AI-Specific:
  - llm_request_duration_seconds (histogram)
  - llm_tokens_used_total (counter, by model)
  - llm_cost_dollars_total (counter)
  - rag_retrieval_score_avg (gauge)
  - cache_hit_rate (gauge)
  - embedding_generation_seconds (histogram)

Standard:
  - http_request_duration_seconds (histogram, by route)
  - http_requests_total (counter, by status code)
  - active_connections (gauge)
  - error_rate (gauge)
```

---

## 6. Security Patterns

### Input Sanitization for LLM
```python
def sanitize_llm_input(text: str) -> str:
    """Prevent prompt injection."""
    # Remove control characters
    text = ''.join(c for c in text if c.isprintable() or c in '\n\t')
    # Limit length
    text = text[:10000]
    # Escape potential injection markers
    text = text.replace("```", "'''")
    return text.strip()

def build_safe_prompt(context: str, question: str) -> list[dict]:
    """Build prompt with clear boundaries."""
    return [
        {
            "role": "system",
            "content": "You are a helpful assistant. Answer ONLY based on the provided context. "
                       "If the context doesn't contain the answer, say 'I don't know.'"
        },
        {
            "role": "user",
            "content": f"<context>\n{sanitize_llm_input(context)}\n</context>\n\n"
                       f"<question>\n{sanitize_llm_input(question)}\n</question>"
        }
    ]
```

### API Key Rotation
```python
import os
from itertools import cycle

class APIKeyRotator:
    """Rotate between multiple API keys to distribute rate limits."""
    def __init__(self):
        keys = os.environ.get("OPENAI_API_KEYS", "").split(",")
        self._keys = cycle(k.strip() for k in keys if k.strip())

    def get_key(self) -> str:
        return next(self._keys)
```

---

## 7. Database Migration Strategy

```bash
# Flask-Migrate (Alembic) workflow
flask db init                    # One-time setup
flask db migrate -m "add users"  # Auto-generate migration
flask db upgrade                 # Apply to database
flask db downgrade               # Rollback one step
flask db history                 # Show migration history
```

### Migration Best Practices
1. **Never edit** applied migrations — create new ones
2. **Always review** auto-generated migrations before applying
3. Use **transaction-safe** DDL (PostgreSQL supports this)
4. **Backup database** before migrations in production
5. Use **blue-green deployments** — migrate DB, then switch traffic

---

## Key Takeaways
1. **Clean Architecture**: Routes → Services → Repositories → Models
2. **Error Handling**: Custom exceptions with HTTP status codes
3. **Circuit Breaker**: Prevent cascade failures from LLM outages
4. **Background Jobs**: Celery for document processing
5. **Observability**: Structured JSON logs + metrics
6. **Security**: Sanitize LLM inputs, prevent prompt injection
7. **Migrations**: Alembic for database schema evolution
