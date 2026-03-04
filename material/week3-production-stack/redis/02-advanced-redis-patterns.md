# Advanced Redis Patterns for AI Applications

> Beyond caching — Redis as a message broker, rate limiter, session store, and real-time feature store.

---

## 1. Semantic Cache for LLM Responses

```python
import json
import hashlib
import numpy as np
import redis
from datetime import timedelta

class SemanticCache:
    """Cache LLM responses by semantic similarity, not exact match."""
    
    def __init__(self, redis_url: str, similarity_threshold: float = 0.92):
        self.r = redis.Redis.from_url(redis_url, decode_responses=True)
        self.threshold = similarity_threshold
        self.ttl = timedelta(hours=24)
    
    def _hash_key(self, text: str) -> str:
        return f"sem_cache:{hashlib.sha256(text.encode()).hexdigest()[:16]}"
    
    def get(self, question: str, question_embedding: list[float]) -> dict | None:
        """Check if a semantically similar question was already answered."""
        # 1. Check exact match first (fast path)
        exact_key = self._hash_key(question.strip().lower())
        cached = self.r.get(exact_key)
        if cached:
            return json.loads(cached)
        
        # 2. Check semantic similarity against recent queries
        recent_keys = self.r.zrevrange("sem_cache:recent", 0, 100)
        for key in recent_keys:
            stored = self.r.hgetall(f"sem_cache:entry:{key}")
            if not stored:
                continue
            stored_embedding = json.loads(stored["embedding"])
            similarity = self._cosine_sim(question_embedding, stored_embedding)
            if similarity >= self.threshold:
                # Cache hit — semantically similar question
                self.r.incr(f"sem_cache:hits")
                return json.loads(stored["response"])
        
        self.r.incr(f"sem_cache:misses")
        return None
    
    def put(self, question: str, embedding: list[float], response: dict):
        """Cache a question-answer pair."""
        entry_id = self._hash_key(question)
        pipe = self.r.pipeline()
        
        # Store entry
        pipe.hset(f"sem_cache:entry:{entry_id}", mapping={
            "question": question,
            "embedding": json.dumps(embedding),
            "response": json.dumps(response),
        })
        pipe.expire(f"sem_cache:entry:{entry_id}", self.ttl)
        
        # Track in sorted set (by timestamp for recency)
        import time
        pipe.zadd("sem_cache:recent", {entry_id: time.time()})
        pipe.zremrangebyrank("sem_cache:recent", 0, -1001)  # Keep last 1000
        
        # Exact match shortcut
        exact_key = self._hash_key(question.strip().lower())
        pipe.set(exact_key, json.dumps(response), ex=self.ttl)
        
        pipe.execute()
    
    @staticmethod
    def _cosine_sim(a: list[float], b: list[float]) -> float:
        a, b = np.array(a), np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    def stats(self) -> dict:
        hits = int(self.r.get("sem_cache:hits") or 0)
        misses = int(self.r.get("sem_cache:misses") or 0)
        total = hits + misses
        return {
            "hits": hits,
            "misses": misses,
            "hit_rate": round(hits / total, 3) if total else 0,
            "entries": self.r.zcard("sem_cache:recent"),
        }
```

---

## 2. Distributed Rate Limiter (Sliding Window)

```python
class DistributedRateLimiter:
    """Production rate limiter using Redis sorted sets."""
    
    TIERS = {
        "free":    {"requests": 20,  "window": 60, "daily": 100},
        "pro":     {"requests": 100, "window": 60, "daily": 5000},
        "enterprise": {"requests": 500, "window": 60, "daily": 50000},
    }
    
    def __init__(self, redis_client):
        self.r = redis_client
    
    def check(self, user_id: str, tier: str = "free") -> tuple[bool, dict]:
        """Check if request is allowed. Returns (allowed, metadata)."""
        limits = self.TIERS.get(tier, self.TIERS["free"])
        now = time.time()
        
        pipe = self.r.pipeline()
        
        # Per-minute check (sliding window)
        minute_key = f"rl:min:{user_id}"
        pipe.zremrangebyscore(minute_key, 0, now - limits["window"])
        pipe.zadd(minute_key, {f"{now}:{uuid4().hex[:8]}": now})
        pipe.zcard(minute_key)
        pipe.expire(minute_key, limits["window"] + 1)
        
        # Daily check
        daily_key = f"rl:day:{user_id}:{time.strftime('%Y%m%d')}"
        pipe.incr(daily_key)
        pipe.expire(daily_key, 86400)
        
        results = pipe.execute()
        minute_count = results[2]
        daily_count = results[4]
        
        allowed = minute_count <= limits["requests"] and daily_count <= limits["daily"]
        
        return allowed, {
            "minute_remaining": max(0, limits["requests"] - minute_count),
            "daily_remaining": max(0, limits["daily"] - daily_count),
            "retry_after": limits["window"] if not allowed else 0,
        }
```

---

## 3. Pub/Sub for Real-Time Events

```python
import redis
import json
import threading

class EventBus:
    """Redis Pub/Sub for real-time events (document processed, chat updated, etc.)."""
    
    def __init__(self, redis_url: str):
        self.r = redis.Redis.from_url(redis_url)
        self.pubsub = self.r.pubsub()
        self._handlers: dict[str, list] = {}
    
    def publish(self, channel: str, event: dict):
        """Publish an event to a channel."""
        self.r.publish(channel, json.dumps(event))
    
    def subscribe(self, channel: str, handler):
        """Register a handler for a channel."""
        self._handlers.setdefault(channel, []).append(handler)
        self.pubsub.subscribe(**{channel: self._message_handler})
    
    def _message_handler(self, message):
        if message["type"] == "message":
            channel = message["channel"].decode()
            data = json.loads(message["data"])
            for handler in self._handlers.get(channel, []):
                handler(data)
    
    def listen(self):
        """Start listening (run in background thread)."""
        thread = threading.Thread(target=self.pubsub.run_in_thread, daemon=True)
        thread.start()

# Usage
bus = EventBus("redis://localhost:6379")

# Worker publishes when done
bus.publish("document_events", {
    "type": "document.processed",
    "doc_id": "abc123",
    "chunks": 42,
    "status": "indexed"
})

# API subscribes to send SSE to client
def on_document_event(event):
    if event["type"] == "document.processed":
        notify_client(event["doc_id"], event)

bus.subscribe("document_events", on_document_event)
bus.listen()
```

---

## 4. Job Queue with Redis Streams

```python
class JobQueue:
    """Redis Streams-based job queue (more reliable than Pub/Sub)."""
    
    def __init__(self, redis_client, stream: str = "jobs"):
        self.r = redis_client
        self.stream = stream
        self.group = "workers"
        
        # Create consumer group if not exists
        try:
            self.r.xgroup_create(self.stream, self.group, id="0", mkstream=True)
        except redis.ResponseError:
            pass  # Group already exists
    
    def enqueue(self, job_type: str, payload: dict) -> str:
        """Add a job to the queue. Returns job ID."""
        entry_id = self.r.xadd(self.stream, {
            "type": job_type,
            "payload": json.dumps(payload),
            "created_at": time.time(),
        })
        return entry_id
    
    def process(self, consumer_name: str, handler, batch_size: int = 10):
        """Process jobs as a consumer."""
        while True:
            # Read new messages
            entries = self.r.xreadgroup(
                self.group, consumer_name,
                {self.stream: ">"},
                count=batch_size, block=5000
            )
            
            if not entries:
                continue
            
            for stream, messages in entries:
                for msg_id, data in messages:
                    try:
                        job_type = data[b"type"].decode()
                        payload = json.loads(data[b"payload"])
                        handler(job_type, payload)
                        # Acknowledge successful processing
                        self.r.xack(self.stream, self.group, msg_id)
                    except Exception as e:
                        print(f"Job {msg_id} failed: {e}")
                        # Will be retried on next pending check

# Usage
queue = JobQueue(redis_client)

# Producer (API)
queue.enqueue("embed_document", {"doc_id": "abc123", "user_id": "u1"})

# Consumer (Worker)
def handle_job(job_type: str, payload: dict):
    if job_type == "embed_document":
        process_document(payload["doc_id"])

queue.process("worker-1", handle_job)
```

---

## 5. Redis as Session Store

```python
from flask import session
from flask_session import Session

# In create_app():
app.config["SESSION_TYPE"] = "redis"
app.config["SESSION_REDIS"] = redis.Redis.from_url("redis://localhost:6379/2")
app.config["SESSION_PERMANENT"] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=24)
app.config["SESSION_KEY_PREFIX"] = "session:"
Session(app)

# Usage — same as normal Flask sessions
@app.route("/login", methods=["POST"])
def login():
    user = authenticate(request.json)
    session["user_id"] = user.id
    session["role"] = user.role
    return jsonify({"message": "logged in"})

@app.route("/profile")
def profile():
    user_id = session.get("user_id")  # From Redis, not cookie
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify(get_user(user_id))
```

---

## 6. Redis Data Structures Cheat Sheet

```
String:  SET/GET/INCR        → Counters, simple cache, feature flags
Hash:    HSET/HGET/HGETALL   → User profiles, session data, config
List:    LPUSH/RPOP/LRANGE   → Recent items, message queues, activity feed
Set:     SADD/SMEMBERS/SINTER → Tags, unique visitors, online users
ZSet:    ZADD/ZRANGE/ZRANK   → Leaderboards, rate limiters, priority queues
Stream:  XADD/XREAD/XACK    → Event logs, reliable message queues, job processing
HyperLogLog: PFADD/PFCOUNT   → Unique count approximations (tiny memory)
Bitmap:  SETBIT/BITCOUNT     → Daily active users, feature flags per user

CHOOSING THE RIGHT ONE:
┌─────────────────────────┬──────────────────┐
│ Need                    │ Use              │
├─────────────────────────┼──────────────────┤
│ Cache LLM response      │ String + TTL     │
│ User session            │ Hash             │
│ Rate limiting           │ Sorted Set       │
│ Recent chat history     │ List (capped)    │
│ Online users in room    │ Set              │
│ Document processing Q   │ Stream           │
│ Daily unique visitors   │ HyperLogLog      │
│ Feature flags per user  │ Bitmap           │
└─────────────────────────┴──────────────────┘
```

---

## Key Takeaways
1. **Semantic cache**: Save 30-50% API costs by caching similar questions
2. **Sliding window rate limiter**: More accurate than fixed windows
3. **Pub/Sub**: For real-time notifications (fire-and-forget)
4. **Streams**: For reliable job processing (with acknowledgment)
5. **Sessions**: Redis session store scales across multiple app servers
6. **Choose the right data structure** — Redis has 8+ specialized types
