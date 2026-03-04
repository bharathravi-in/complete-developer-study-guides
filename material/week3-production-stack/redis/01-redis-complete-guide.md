# Redis - Complete Guide for AI Engineers

## What is Redis?
Redis = **Re**mote **Di**ctionary **S**erver — an in-memory data store.

**Think of it as:** A super-fast JavaScript `Map()` that lives outside your app, persists data, and does much more.

## Why Redis for AI?
- **Cache LLM responses** — save $$ and reduce latency
- **Rate limiting** — protect API budgets
- **Session storage** — JWT token management
- **Pub/Sub** — real-time updates
- **Queuing** — background job processing
- **TTL (Time to Live)** — auto-expire cached data

---

## 1. Setup

```bash
# Docker
docker run -d --name redis -p 6379:6379 redis:latest

# Verify
docker exec -it redis redis-cli ping
# PONG

# Python client
pip install redis
```

## 2. Basic Operations

```python
import redis
import json
from typing import Optional

# Connect
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# ========== STRINGS ==========
r.set("name", "Bharath")
r.get("name")  # "Bharath"

# With TTL (Time to Live)
r.set("session:abc123", "user_1", ex=3600)  # Expires in 1 hour
r.ttl("session:abc123")  # Remaining seconds

# Increment/Decrement (atomic!)
r.set("api_calls", 0)
r.incr("api_calls")  # 1
r.incr("api_calls")  # 2
r.decr("api_calls")  # 1

# ========== HASHES (Like Objects) ==========
r.hset("user:1", mapping={
    "name": "Bharath",
    "role": "AI Engineer",
    "api_calls": "0"
})
r.hget("user:1", "name")  # "Bharath"
r.hgetall("user:1")       # {'name': 'Bharath', 'role': 'AI Engineer', ...}
r.hincrby("user:1", "api_calls", 1)  # Atomic increment

# ========== LISTS (Queues) ==========
r.lpush("task_queue", "task1", "task2", "task3")  # Push left
r.rpop("task_queue")   # Pop right = "task1" (FIFO)
r.lrange("task_queue", 0, -1)  # Get all items
r.llen("task_queue")   # Length

# ========== SETS ==========
r.sadd("online_users", "user1", "user2", "user3")
r.sismember("online_users", "user1")  # True
r.smembers("online_users")  # {'user1', 'user2', 'user3'}
r.scard("online_users")     # 3

# ========== SORTED SETS (Leaderboard/Priority) ==========
r.zadd("search_scores", {"doc1": 0.95, "doc2": 0.87, "doc3": 0.72})
r.zrevrange("search_scores", 0, -1, withscores=True)
# [('doc1', 0.95), ('doc2', 0.87), ('doc3', 0.72)]

# ========== JSON STORAGE ==========
data = {"model": "gpt-4", "response": "AI is fascinating", "tokens": 150}
r.set("cache:query_hash", json.dumps(data), ex=3600)
cached = json.loads(r.get("cache:query_hash"))
```

---

## 3. LLM Response Caching (Most Important Use Case)

```python
import redis
import hashlib
import json
import time
from typing import Optional
from dataclasses import dataclass

@dataclass
class CachedResponse:
    content: str
    model: str
    cached: bool
    cache_key: str
    latency_ms: float

class LLMCache:
    """Cache LLM responses to save money and reduce latency."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        default_ttl: int = 3600,  # 1 hour
        prefix: str = "llm_cache:"
    ):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = default_ttl
        self.prefix = prefix
    
    def _make_key(self, model: str, prompt: str, temperature: float) -> str:
        """Create a unique cache key from the request parameters."""
        # Only cache deterministic responses (temperature=0)
        content = f"{model}:{prompt}:{temperature}"
        hash_val = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"{self.prefix}{hash_val}"
    
    def get(self, model: str, prompt: str, temperature: float = 0.0) -> Optional[str]:
        """Get cached response."""
        if temperature > 0:
            return None  # Don't cache non-deterministic responses
        
        key = self._make_key(model, prompt, temperature)
        cached = self.redis.get(key)
        
        if cached:
            data = json.loads(cached)
            self.redis.hincrby(f"{self.prefix}stats", "hits", 1)
            return data["content"]
        
        self.redis.hincrby(f"{self.prefix}stats", "misses", 1)
        return None
    
    def set(
        self, 
        model: str, 
        prompt: str, 
        response: str, 
        temperature: float = 0.0,
        ttl: Optional[int] = None
    ) -> None:
        """Cache a response."""
        if temperature > 0:
            return  # Don't cache non-deterministic responses
        
        key = self._make_key(model, prompt, temperature)
        data = {
            "content": response,
            "model": model,
            "cached_at": time.time(),
        }
        self.redis.set(key, json.dumps(data), ex=ttl or self.default_ttl)
    
    def get_stats(self) -> dict:
        """Get cache hit/miss statistics."""
        stats = self.redis.hgetall(f"{self.prefix}stats")
        hits = int(stats.get("hits", 0))
        misses = int(stats.get("misses", 0))
        total = hits + misses
        return {
            "hits": hits,
            "misses": misses,
            "total": total,
            "hit_rate": f"{hits / total * 100:.1f}%" if total > 0 else "0%"
        }
    
    def clear(self) -> int:
        """Clear all cached responses."""
        keys = self.redis.keys(f"{self.prefix}*")
        if keys:
            return self.redis.delete(*keys)
        return 0


# Usage with OpenAI
from openai import OpenAI

class CachedLLMService:
    """LLM service with Redis caching."""
    
    def __init__(self, api_key: str, redis_url: str = "redis://localhost:6379"):
        self.client = OpenAI(api_key=api_key)
        self.cache = LLMCache(redis_url=redis_url)
    
    def generate(self, prompt: str, model: str = "gpt-4", temperature: float = 0.0) -> CachedResponse:
        start = time.time()
        
        # Check cache first
        cached = self.cache.get(model, prompt, temperature)
        if cached:
            return CachedResponse(
                content=cached,
                model=model,
                cached=True,
                cache_key=self.cache._make_key(model, prompt, temperature),
                latency_ms=(time.time() - start) * 1000,
            )
        
        # Call LLM
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        content = response.choices[0].message.content
        
        # Cache the response
        self.cache.set(model, prompt, content, temperature)
        
        return CachedResponse(
            content=content,
            model=model,
            cached=False,
            cache_key=self.cache._make_key(model, prompt, temperature),
            latency_ms=(time.time() - start) * 1000,
        )
```

---

## 4. Rate Limiting

```python
import redis
import time

class RateLimiter:
    """Token bucket rate limiter using Redis."""
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        max_requests: int = 10,
        window_seconds: int = 60,
    ):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, identifier: str) -> tuple[bool, dict]:
        """Check if a request is allowed.
        
        Returns: (is_allowed, info_dict)
        """
        key = f"rate_limit:{identifier}"
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        pipe = self.redis.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        # Count remaining entries
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(current_time): current_time})
        # Set expiry
        pipe.expire(key, self.window_seconds)
        
        results = pipe.execute()
        request_count = results[1]
        
        info = {
            "remaining": max(0, self.max_requests - request_count - 1),
            "limit": self.max_requests,
            "reset": current_time + self.window_seconds,
        }
        
        return request_count < self.max_requests, info


# Flask middleware
from flask import Flask, request, jsonify
from functools import wraps

limiter = RateLimiter(max_requests=30, window_seconds=60)

def rate_limit_middleware(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Use IP or API key as identifier
        identifier = request.headers.get("X-API-Key", request.remote_addr)
        allowed, info = limiter.is_allowed(identifier)
        
        if not allowed:
            return jsonify({
                "error": "Rate limit exceeded",
                "retry_after": info["reset"] - int(time.time()),
            }), 429
        
        response = f(*args, **kwargs)
        # Add rate limit headers
        if hasattr(response, 'headers'):
            response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
            response.headers["X-RateLimit-Limit"] = str(info["limit"])
        return response
    
    return wrapper

# Usage
@app.route("/api/query")
@rate_limit_middleware
def handle_query():
    return jsonify({"answer": "..."})
```

---

## 5. Session Management

```python
import redis
import json
import uuid
from datetime import datetime

class SessionManager:
    """Manage user sessions with Redis."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379", ttl: int = 86400):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.ttl = ttl
        self.prefix = "session:"
    
    def create_session(self, user_id: int, data: dict = None) -> str:
        session_id = str(uuid.uuid4())
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            **(data or {})
        }
        self.redis.set(
            f"{self.prefix}{session_id}",
            json.dumps(session_data),
            ex=self.ttl
        )
        return session_id
    
    def get_session(self, session_id: str) -> dict | None:
        data = self.redis.get(f"{self.prefix}{session_id}")
        return json.loads(data) if data else None
    
    def delete_session(self, session_id: str):
        self.redis.delete(f"{self.prefix}{session_id}")
    
    def extend_session(self, session_id: str):
        self.redis.expire(f"{self.prefix}{session_id}", self.ttl)
```

---

## 6. Pub/Sub (Real-time Updates)

```python
import redis
import json
import threading

class EventBus:
    """Simple pub/sub event bus using Redis."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.pubsub = self.redis.pubsub()
    
    def publish(self, channel: str, data: dict):
        """Publish an event."""
        self.redis.publish(channel, json.dumps(data))
    
    def subscribe(self, channel: str, callback):
        """Subscribe to a channel with a callback."""
        self.pubsub.subscribe(**{channel: lambda msg: callback(json.loads(msg["data"]))})
        thread = self.pubsub.run_in_thread(sleep_time=0.01)
        return thread


# Usage:
# Publisher (e.g., when document is indexed)
bus = EventBus()
bus.publish("document_indexed", {
    "document_id": "doc_123",
    "chunks": 15,
    "timestamp": "2024-01-01T12:00:00"
})

# Subscriber (e.g., notification service)
def on_document_indexed(data):
    print(f"New document indexed: {data['document_id']} with {data['chunks']} chunks")

bus.subscribe("document_indexed", on_document_indexed)
```

---

## 7. Background Job Queue

```python
import redis
import json
import time
import uuid
from dataclasses import dataclass
from typing import Callable
from enum import Enum

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SimpleQueue:
    """Simple job queue using Redis lists."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url, decode_responses=True)
    
    def enqueue(self, queue_name: str, job_data: dict) -> str:
        """Add a job to the queue."""
        job_id = str(uuid.uuid4())[:8]
        job = {
            "id": job_id,
            "data": job_data,
            "status": JobStatus.PENDING.value,
            "created_at": time.time(),
        }
        self.redis.lpush(f"queue:{queue_name}", json.dumps(job))
        self.redis.hset(f"job:{job_id}", mapping={
            "status": JobStatus.PENDING.value,
            "queue": queue_name,
        })
        return job_id
    
    def dequeue(self, queue_name: str, timeout: int = 5) -> dict | None:
        """Get next job from queue (blocking)."""
        result = self.redis.brpop(f"queue:{queue_name}", timeout=timeout)
        if result:
            _, job_json = result
            job = json.loads(job_json)
            self.redis.hset(f"job:{job['id']}", "status", JobStatus.PROCESSING.value)
            return job
        return None
    
    def complete(self, job_id: str, result: dict = None):
        """Mark job as completed."""
        self.redis.hset(f"job:{job_id}", mapping={
            "status": JobStatus.COMPLETED.value,
            "result": json.dumps(result or {}),
            "completed_at": str(time.time()),
        })
    
    def get_status(self, job_id: str) -> dict:
        return self.redis.hgetall(f"job:{job_id}")


# Usage:
queue = SimpleQueue()

# Producer: Submit embedding job
job_id = queue.enqueue("embeddings", {
    "document_id": "doc_123",
    "text": "Process this document for embeddings"
})
print(f"Job submitted: {job_id}")

# Worker: Process jobs
def worker(queue_name: str):
    q = SimpleQueue()
    while True:
        job = q.dequeue(queue_name)
        if job:
            print(f"Processing job: {job['id']}")
            # ... do the actual work ...
            time.sleep(2)  # Simulate work
            q.complete(job['id'], {"embeddings": [0.1, 0.2, 0.3]})
            print(f"Completed job: {job['id']}")
```

---

## Exercises

### Exercise 1: Build an Embedding Cache
```python
# Build a cache specifically for embeddings:
# 1. Cache key = hash of text
# 2. Store embedding as JSON
# 3. Track cache hit rate
# 4. Support batch get/set
# 5. Auto-expire after 7 days
# TODO: Implement
```

### Exercise 2: Build a Usage Tracker
```python
# Track API usage per user using Redis:
# 1. Count API calls per user per day
# 2. Track token usage
# 3. Track cost
# 4. Alert when daily limit exceeded
# 5. Generate daily reports
# TODO: Implement
```

---

## Key Takeaways
1. Redis is **in-memory** = microsecond latency
2. **Cache LLM responses** to save 90%+ on API costs
3. **Rate limiting** protects your API budget
4. **TTL** auto-expires data (no cleanup needed)
5. **Pub/Sub** for real-time features
6. **Lists** for simple job queues
7. **Sorted Sets** for rankings and scores
8. Always use **connection pooling** in production
