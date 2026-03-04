# Advanced System Design — Event-Driven Architecture, CQRS, MLOps & Cost Optimization

> Topics beyond the basic system design guide that come up in senior/staff interviews.

---

## 1. Event-Driven Architecture for AI Systems

### Why Event-Driven?
```
Traditional (Request/Response):
  Client → API → Process Document → Embed → Store → Respond
  Problem: Client waits 30+ seconds for large documents

Event-Driven:
  Client → API → "Document Uploaded" event → Respond immediately (202)
  Worker picks up event → Process → Embed → Store
  Client polls status or gets SSE notification
```

### Architecture Diagram
```
┌──────────┐     ┌──────────┐     ┌───────────────┐
│  Client   │────▶│  API     │────▶│  Redis Stream  │
│  (Flutter)│◀────│  (Flask) │     │  (Event Bus)   │
└──────────┘ SSE └──────────┘     └───────┬────────┘
                                          │
                     ┌────────────────────┤
                     ▼                    ▼
              ┌─────────────┐    ┌──────────────┐
              │ Doc Worker   │    │ Embed Worker  │
              │ (Extract +   │    │ (Vectorize +  │
              │  Chunk)      │    │  Store)       │
              └──────┬──────┘    └──────┬────────┘
                     │                   │
                     ▼                   ▼
              ┌─────────────┐    ┌──────────────┐
              │  PostgreSQL  │    │   Qdrant      │
              └─────────────┘    └──────────────┘
```

### Event Schema
```python
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    DOCUMENT_UPLOADED = "document.uploaded"
    DOCUMENT_PROCESSED = "document.processed"
    DOCUMENT_EMBEDDED = "document.embedded"
    DOCUMENT_FAILED = "document.failed"
    CHAT_MESSAGE_SENT = "chat.message.sent"
    CHAT_RESPONSE_GENERATED = "chat.response.generated"

class Event(BaseModel):
    id: str
    type: EventType
    timestamp: datetime
    tenant_id: str
    user_id: str
    data: dict
    metadata: dict = {}

# Example events
upload_event = Event(
    id="evt_abc123",
    type=EventType.DOCUMENT_UPLOADED,
    timestamp=datetime.utcnow(),
    tenant_id="t_1",
    user_id="u_1",
    data={"doc_id": "d_1", "filename": "report.pdf", "size_bytes": 152000},
)
```

---

## 2. CQRS (Command Query Responsibility Segregation)

### When to Use CQRS
```
Standard CRUD: Read and write same database tables
  → Fine for simple apps

CQRS: Separate read model from write model
  → When reads and writes have very different patterns
  → When you need to optimize reads independently

For AI Platform:
  WRITE: Upload document → Process → Embed → Store in Qdrant + Postgres
  READ:  Search → Vector similarity in Qdrant → Metadata from Redis cache
  These are completely different data flows → CQRS fits well
```

### Implementation
```python
# Commands (Write side)
class UploadDocumentCommand:
    def __init__(self, file, user_id: str, tenant_id: str):
        self.file = file
        self.user_id = user_id
        self.tenant_id = tenant_id

class CommandHandler:
    def handle_upload(self, cmd: UploadDocumentCommand):
        # 1. Save to storage
        doc = save_file(cmd.file)
        # 2. Store metadata in Postgres
        db.session.add(Document(id=doc.id, user_id=cmd.user_id, ...))
        db.session.commit()
        # 3. Emit event for async processing
        event_bus.publish(Event(type="document.uploaded", data={"doc_id": doc.id}))
        return doc.id

# Queries (Read side) — optimized for fast retrieval
class SearchQuery:
    def __init__(self, question: str, tenant_id: str, top_k: int = 5):
        self.question = question
        self.tenant_id = tenant_id
        self.top_k = top_k

class QueryHandler:
    def handle_search(self, query: SearchQuery):
        # 1. Check cache
        cached = cache.get(f"search:{hash(query.question)}")
        if cached:
            return cached
        
        # 2. Embed question
        vector = embedder.embed(query.question)
        
        # 3. Search Qdrant (read-optimized store)
        results = qdrant.search(
            vector=vector,
            filter={"tenant_id": query.tenant_id},
            limit=query.top_k,
        )
        
        # 4. Cache results
        cache.set(f"search:{hash(query.question)}", results, ttl=300)
        return results
```

---

## 3. Saga Pattern (Distributed Transactions)

### Problem: Multi-Step Operations That Can Fail
```
Upload Flow:
  1. Save file to S3         ✅
  2. Create DB record        ✅
  3. Extract text             ✅
  4. Generate embeddings      ❌ FAILED (API error)
  5. Store in Qdrant          ⏭️ Never reached

Now what? File is saved but embeddings don't exist.
User sees "processing" forever.
```

### Solution: Saga with Compensating Actions
```python
class DocumentUploadSaga:
    """Each step has a compensating action (undo)."""
    
    def __init__(self, doc_id: str):
        self.doc_id = doc_id
        self.completed_steps = []
    
    async def execute(self):
        steps = [
            ("save_file", self.save_file, self.delete_file),
            ("create_record", self.create_db_record, self.delete_db_record),
            ("extract_text", self.extract_text, self.clear_text),
            ("embed", self.generate_embeddings, self.delete_embeddings),
            ("index", self.store_in_qdrant, self.delete_from_qdrant),
        ]
        
        for step_name, action, compensate in steps:
            try:
                await action()
                self.completed_steps.append((step_name, compensate))
            except Exception as e:
                # Rollback completed steps in reverse order
                await self.compensate(error=e)
                raise SagaFailedError(f"Step '{step_name}' failed: {e}")
    
    async def compensate(self, error: Exception):
        """Undo all completed steps in reverse."""
        for step_name, undo in reversed(self.completed_steps):
            try:
                await undo()
                logger.info(f"Compensated step: {step_name}")
            except Exception as e:
                logger.error(f"Compensation failed for {step_name}: {e}")
                # Alert human — manual intervention needed
                alert_ops_team(self.doc_id, step_name, e)
    
    async def save_file(self):
        # Save to storage
        pass
    
    async def delete_file(self):
        # Compensating action: remove file
        pass
    
    # ... other steps and compensations
```

---

## 4. MLOps Basics

### Model Versioning
```python
# Track model versions and their performance
class ModelRegistry:
    """Simple model registry backed by Redis + file storage."""
    
    def __init__(self, redis_client, storage_path: str):
        self.r = redis_client
        self.storage = Path(storage_path)
    
    def register(self, model_name: str, version: str, metrics: dict, path: str):
        """Register a new model version."""
        self.r.hset(f"model:{model_name}:{version}", mapping={
            "path": path,
            "metrics": json.dumps(metrics),
            "registered_at": datetime.utcnow().isoformat(),
            "status": "staging",
        })
        self.r.zadd(f"model:{model_name}:versions", {version: time.time()})
    
    def promote(self, model_name: str, version: str):
        """Promote a model version to production."""
        # Demote current production
        current = self.r.get(f"model:{model_name}:production")
        if current:
            self.r.hset(f"model:{model_name}:{current.decode()}", "status", "archived")
        
        # Promote new version
        self.r.hset(f"model:{model_name}:{version}", "status", "production")
        self.r.set(f"model:{model_name}:production", version)
    
    def get_production(self, model_name: str) -> dict:
        version = self.r.get(f"model:{model_name}:production")
        if not version:
            raise ValueError(f"No production model for {model_name}")
        return self.r.hgetall(f"model:{model_name}:{version.decode()}")
```

### A/B Testing for AI
```python
class ABRouter:
    """Route users to different model versions for A/B testing."""
    
    def __init__(self, redis_client):
        self.r = redis_client
    
    def configure_test(self, test_name: str, variants: dict[str, float]):
        """Configure A/B test with traffic splits.
        
        variants: {"control": 0.8, "treatment": 0.2}
        """
        self.r.hset(f"ab:{test_name}", mapping={
            k: str(v) for k, v in variants.items()
        })
    
    def get_variant(self, test_name: str, user_id: str) -> str:
        """Deterministically assign user to variant."""
        # Hash user_id for consistent assignment
        hash_val = int(hashlib.md5(f"{test_name}:{user_id}".encode()).hexdigest(), 16)
        bucket = (hash_val % 100) / 100
        
        variants = self.r.hgetall(f"ab:{test_name}")
        cumulative = 0
        for variant, weight in sorted(variants.items()):
            cumulative += float(weight)
            if bucket < cumulative:
                return variant.decode() if isinstance(variant, bytes) else variant
        return "control"
    
    def record_metric(self, test_name: str, variant: str, metric: str, value: float):
        """Record a metric for analysis."""
        key = f"ab:{test_name}:{variant}:{metric}"
        self.r.lpush(key, value)
        self.r.expire(key, 86400 * 30)  # 30 days

# Usage
router = ABRouter(redis_client)
router.configure_test("rag_model", {"gpt-4": 0.5, "gpt-4o-mini": 0.5})

variant = router.get_variant("rag_model", user_id)
if variant == "gpt-4":
    response = query_with_gpt4(question)
else:
    response = query_with_gpt4o_mini(question)

# Record quality
router.record_metric("rag_model", variant, "user_rating", user_feedback)
router.record_metric("rag_model", variant, "latency", response_time)
```

---

## 5. Cost Optimization for AI Systems

### Token Usage Tracking
```python
class CostTracker:
    """Track and optimize LLM costs per tenant."""
    
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},       # per 1K tokens
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    }
    
    def __init__(self, redis_client):
        self.r = redis_client
    
    def record(self, tenant_id: str, model: str, input_tokens: int, output_tokens: int):
        pricing = self.PRICING.get(model, self.PRICING["gpt-4o"])
        cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1000
        
        date = time.strftime("%Y-%m-%d")
        month = time.strftime("%Y-%m")
        
        pipe = self.r.pipeline()
        pipe.incrbyfloat(f"cost:{tenant_id}:{date}", cost)
        pipe.incrbyfloat(f"cost:{tenant_id}:{month}", cost)
        pipe.incr(f"tokens:{tenant_id}:{month}:input", input_tokens)
        pipe.incr(f"tokens:{tenant_id}:{month}:output", output_tokens)
        pipe.execute()
    
    def get_monthly_cost(self, tenant_id: str) -> dict:
        month = time.strftime("%Y-%m")
        return {
            "cost_usd": float(self.r.get(f"cost:{tenant_id}:{month}") or 0),
            "input_tokens": int(self.r.get(f"tokens:{tenant_id}:{month}:input") or 0),
            "output_tokens": int(self.r.get(f"tokens:{tenant_id}:{month}:output") or 0),
        }
```

### Cost Reduction Strategies
```
1. SEMANTIC CACHING (saves 30-50%)
   - Cache similar questions → same answer
   - Threshold: 0.92+ cosine similarity
   
2. MODEL ROUTING (saves 40-70%)
   - Simple questions → gpt-4o-mini ($0.15/M input)
   - Complex questions → gpt-4o ($5/M input)
   - Classify complexity first, then route
   
3. PROMPT COMPRESSION (saves 20-30%)
   - Remove redundant context
   - Use shorter system prompts
   - Compress retrieved chunks to only relevant sentences
   
4. BATCH PROCESSING (saves time, not $$)
   - Batch embedding calls (100 texts at once)
   - Process documents in parallel
   
5. CONTEXT WINDOW MANAGEMENT
   - Don't send 128K tokens when 4K is enough
   - Trim conversation history intelligently
   - Use summary of old messages
   
EXAMPLE MONTHLY SAVINGS (10K queries/day):
  Before optimization: ~$4,500/month (all GPT-4)
  After optimization:  ~$800/month (routing + caching + compression)
```

---

## 6. Observability for AI Systems

### Structured Logging
```python
import structlog
import json

logger = structlog.get_logger()

class AIObservability:
    """Track AI-specific metrics."""
    
    @staticmethod
    def log_rag_query(question, chunks, answer, latency, model, tokens):
        logger.info(
            "rag_query",
            question_length=len(question),
            chunks_retrieved=len(chunks),
            avg_chunk_score=sum(c.score for c in chunks) / len(chunks) if chunks else 0,
            answer_length=len(answer),
            latency_ms=round(latency * 1000),
            model=model,
            input_tokens=tokens["input"],
            output_tokens=tokens["output"],
        )
    
    @staticmethod
    def log_embedding(text_count, dimensions, latency, model):
        logger.info(
            "embedding_generated",
            text_count=text_count,
            dimensions=dimensions,
            latency_ms=round(latency * 1000),
            model=model,
            throughput_per_sec=round(text_count / latency) if latency > 0 else 0,
        )
```

### Health Check Endpoint
```python
@bp.route("/health")
def health():
    checks = {}
    
    # Postgres
    try:
        db.session.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {e}"
    
    # Redis
    try:
        redis_client.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {e}"
    
    # Qdrant
    try:
        qdrant_client.get_collections()
        checks["qdrant"] = "healthy"
    except Exception as e:
        checks["qdrant"] = f"unhealthy: {e}"
    
    # OpenAI (lightweight check)
    try:
        client.models.list()
        checks["openai"] = "healthy"
    except Exception as e:
        checks["openai"] = f"unhealthy: {e}"
    
    all_healthy = all(v == "healthy" for v in checks.values())
    status_code = 200 if all_healthy else 503
    
    return jsonify({
        "status": "healthy" if all_healthy else "degraded",
        "checks": checks,
        "version": app.config.get("APP_VERSION", "unknown"),
    }), status_code
```

---

## Key Takeaways
1. **Event-driven** architecture is essential for AI systems (long processing times)
2. **CQRS** separates fast reads (vector search) from slow writes (document processing)
3. **Saga pattern** handles multi-step failures gracefully
4. **A/B testing** lets you compare models objectively
5. **Cost optimization** can reduce LLM bills by 70-80%
6. **Observability** — log everything: latency, tokens, scores, costs
