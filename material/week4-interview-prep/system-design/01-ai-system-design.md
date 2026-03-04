# AI System Design - Complete Guide

## How to Answer System Design Questions

### Framework (5-Step)
1. **Clarify Requirements** (2 min)
2. **High-Level Architecture** (5 min)
3. **Deep Dive into Components** (15 min)
4. **Scaling & Performance** (5 min)
5. **Trade-offs & Monitoring** (3 min)

---

## Design 1: AI Chat System (Like ChatGPT)

### Requirements
- Users send messages, get AI responses
- Conversation history maintained
- Streaming responses
- Rate limiting
- Multi-model support (GPT-4, Claude, etc.)

### Architecture
```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  React Web  │────▶│  API Gateway │────▶│  Flask API   │
│  Flutter App│     │  (Nginx/ALB) │     │  (Gunicorn)  │
└─────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                    ┌────────────────────────────┼────────────────────┐
                    │                            │                    │
              ┌─────▼─────┐            ┌─────────▼──────┐    ┌──────▼──────┐
              │   Redis   │            │  PostgreSQL    │    │ LLM Gateway │
              │  - Cache  │            │  - Users       │    │ - OpenAI    │
              │  - Rate   │            │  - Chats       │    │ - Claude    │
              │  - Sessions│           │  - Messages    │    │ - Llama     │
              └───────────┘            └────────────────┘    └─────────────┘
```

### Key Decisions
```
1. Streaming: Use Server-Sent Events (SSE) for streaming responses
   - NOT WebSocket (SSE is simpler for one-way streaming)
   - Frontend: EventSource API
   - Backend: Flask response generator

2. Rate Limiting: Redis sliding window
   - 30 requests/minute for free tier
   - 100 requests/minute for paid

3. Conversation History:
   - Store in PostgreSQL
   - Send last N messages as context
   - Summarize old messages to save tokens

4. Multi-Model:
   - Abstract LLM layer (Strategy pattern)
   - Route based on user preference
   - Fallback to cheaper model on errors
```

### Streaming Implementation
```python
from flask import Flask, Response, stream_with_context
import json

@app.route("/api/chat/stream", methods=["POST"])
def chat_stream():
    data = request.get_json()
    
    def generate():
        stream = openai_client.chat.completions.create(
            model="gpt-4",
            messages=data["messages"],
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield f"data: {json.dumps({'token': delta.content})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
```

---

## Design 2: Scalable RAG System

### Requirements
- Upload documents (PDF, TXT, CSV)
- Chunk and embed documents
- Semantic search
- Generate answers with citations
- Handle 10K+ documents, 100+ concurrent users

### Architecture
```
┌──────────────┐
│  React Admin │
│  Dashboard   │
└──────┬───────┘
       │
┌──────▼───────┐     ┌──────────────┐     ┌───────────────┐
│  Flask API   │────▶│  Redis Cache │     │  Celery       │
│  Gateway     │     │  - LLM cache │     │  Workers      │
└──────┬───────┘     │  - Rate limit│     │  - Chunk      │
       │             └──────────────┘     │  - Embed      │
       │                                  │  - Index      │
       ├─────────────────┐                └───────┬───────┘
       │                 │                        │
┌──────▼──────┐  ┌──────▼──────┐         ┌──────▼──────┐
│  Qdrant     │  │ PostgreSQL  │         │  S3/MinIO   │
│  Vectors    │  │  Metadata   │         │  Document   │
│  Embeddings │  │  Users      │         │  Storage    │
└─────────────┘  └─────────────┘         └─────────────┘
```

### Indexing Pipeline (Background)
```
Upload Document
    │
    ▼
Celery Worker picks up job
    │
    ▼
Extract Text (PDF → text)
    │
    ▼
Clean & Normalize
    │
    ▼
Chunk (recursive, 500 words, 50 overlap)
    │
    ▼
Generate Embeddings (batch, max 100/request)
    │
    ▼
Store in Qdrant (with metadata)
    │
    ▼
Update PostgreSQL (doc status = "indexed")
    │
    ▼
Notify user (WebSocket/email)
```

### Query Pipeline
```
User Query
    │
    ▼
Check Redis Cache (hash of query)
    │ (cache miss)
    ▼
Generate Query Embedding
    │
    ▼
Search Qdrant (top_k=10, with filters)
    │
    ▼
Re-rank results (optional)
    │
    ▼
Build Prompt (context + question)
    │
    ▼
Call LLM (with streaming)
    │
    ▼
Cache response in Redis (TTL=1hr)
    │
    ▼
Return to user (with sources)
```

### Scaling Decisions
```
1. Document Processing: Background with Celery + Redis
   - Don't block the API while processing documents
   - Scale workers independently

2. Embedding Generation: Batch + Rate Limit
   - Batch size: 100 texts per API call
   - Concurrency: max 3 parallel calls
   - Use semaphore to control

3. Qdrant Scaling:
   - Single node: up to ~1M vectors
   - Cluster mode: for larger datasets
   - Quantization: reduce memory 4x (slight quality loss)

4. Caching Strategy:
   - Cache identical queries for 1 hour
   - Cache embeddings for 7 days
   - Cache chunk retrievals for 15 minutes

5. Cost Optimization:
   - Use GPT-3.5-turbo for simple queries
   - Use GPT-4 only when needed
   - Cache aggressively
   - Batch embedding calls
```

---

## Design 3: Multi-Tenant AI SaaS

### Requirements
- Multiple organizations
- Each org has own documents
- Data isolation
- Usage billing
- Admin dashboard

### Architecture
```
┌─────────────────────────────────────────────────┐
│                 API Gateway (Nginx)              │
│            - SSL, Load Balancing                 │
│            - Rate Limiting per tenant            │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│              Flask API (Gunicorn x4)             │
│         - JWT Auth + Tenant Resolution           │
│         - Request Routing                        │
└──────┬───────────────┬───────────────┬──────────┘
       │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│  Qdrant     │ │ PostgreSQL  │ │   Redis     │
│  per-tenant │ │ Shared DB   │ │   Shared    │
│  collection │ │ Row-level   │ │   Prefixed  │
│             │ │ isolation   │ │   keys      │
└─────────────┘ └─────────────┘ └─────────────┘
```

### Data Isolation Approaches
```
Option 1: Separate Qdrant Collections (RECOMMENDED)
  - tenant_acme_docs, tenant_beta_docs
  - Complete isolation
  - Easy to delete tenant data

Option 2: Shared Collection with Filters
  - All vectors in one collection
  - Filter by tenant_id in payload
  - Less overhead, requires careful filtering

Option 3: Separate Qdrant Instances
  - Full isolation
  - Most expensive
  - For enterprise/compliance needs
```

---

## Design 4: Real-Time AI Streaming System

### Requirements
- Multiple users chatting simultaneously
- Real-time token streaming
- Conversation history
- Typing indicators

### Key Components
```
WebSocket Connection Manager:
  - Track active connections per user
  - Heartbeat/ping-pong for connection health
  - Graceful reconnection

Streaming Pipeline:
  User sends message
    → WebSocket receives
    → Validate + rate limit (Redis)
    → Start LLM stream
    → Forward tokens via WebSocket
    → Save complete message to DB

Server-Sent Events (alternative):
  - Simpler than WebSocket
  - One-way (server → client)
  - Automatic reconnection
  - Works through proxies
  - RECOMMENDED for chat streaming
```

---

## System Design Quick Reference

### Capacity Estimation
```
Users: 10,000 active
Queries: 5 per user per day = 50,000/day = ~0.6 QPS
Peak: 3x = ~2 QPS

Storage (Qdrant):
  - 100K documents × 10 chunks × 384 dims × 4 bytes = ~1.5 GB vectors
  - Payload: ~500 bytes/chunk × 1M chunks = ~500 MB
  - Total: ~2 GB (fits single node easily)

LLM Costs:
  - 50K queries/day × 500 tokens avg = 25M tokens/day
  - GPT-4o: 25M × $0.015/1K = ~$375/day
  - With 50% cache hit: ~$188/day
  - GPT-3.5: 25M × $0.002/1K = ~$50/day
```

### Common Patterns
```
1. CQRS: Separate read (search) and write (indexing) paths
2. Event Sourcing: Track all changes to documents
3. Circuit Breaker: Handle LLM provider outages
4. Retry with Backoff: For transient failures
5. Queue-Based Load Leveling: Use Celery for background work
6. Cache-Aside: Check cache → miss → compute → cache → return
7. Saga Pattern: Multi-step document processing with rollback
```

---

## Key Takeaways for System Design Interviews
1. Always **clarify requirements** first
2. Start with **high-level diagram** before deep diving
3. **Address scaling** — how does it handle 10x users?
4. Discuss **trade-offs** — cost vs latency, consistency vs availability
5. **Security**: data isolation, auth, rate limiting
6. **Monitoring**: latency P99, error rates, cost tracking
7. **Caching**: the #1 optimization for AI systems
8. Know **when to use** GPT-4 vs GPT-3.5 vs local models
