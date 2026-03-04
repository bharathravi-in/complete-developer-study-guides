# Redis Cheat Sheet

## CLI Commands
```bash
redis-cli                    # Connect
redis-cli ping               # Check connection
redis-cli INFO               # Server info
redis-cli MONITOR            # Watch all commands
```

## Strings (Cache)
```bash
SET key "value"              # Set
SET key "value" EX 3600      # Set with TTL (1 hour)
GET key                      # Get
DEL key                      # Delete
EXISTS key                   # Check exists
TTL key                      # Time remaining
INCR counter                 # Increment
```

## Hashes (Objects)
```bash
HSET user:1 name "Bharath" role "admin"
HGET user:1 name             # "Bharath"
HGETALL user:1               # All fields
HDEL user:1 role             # Delete field
```

## Lists (Queues)
```bash
LPUSH queue "job1"           # Push left
RPUSH queue "job2"           # Push right
LPOP queue                   # Pop left
RPOP queue                   # Pop right
LLEN queue                   # Length
LRANGE queue 0 -1            # Get all
```

## Sets
```bash
SADD tags "python" "ai"      # Add
SMEMBERS tags                 # All members
SISMEMBER tags "ai"           # Check membership
SCARD tags                    # Count
```

## Sorted Sets (Rate Limiting)
```bash
ZADD leaderboard 100 "user1"  # Add with score
ZRANGE leaderboard 0 -1 WITHSCORES  # Get all
ZRANGEBYSCORE leaderboard 0 100     # By score range
ZREM leaderboard "user1"             # Remove
```

## Python redis Client
```python
import redis

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

# Basic operations
r.set("key", "value", ex=3600)    # Set with TTL
r.get("key")                       # Get
r.delete("key")                    # Delete
r.exists("key")                    # Check

# Hash
r.hset("user:1", mapping={"name": "Bharath", "role": "admin"})
r.hgetall("user:1")

# Pipeline (batch)
pipe = r.pipeline()
pipe.set("a", 1)
pipe.set("b", 2)
pipe.execute()                     # Execute all at once
```

## LLM Cache Pattern
```python
import hashlib, json

def get_cached(prompt, model="gpt-4"):
    key = f"llm:{hashlib.sha256(f'{model}:{prompt}'.encode()).hexdigest()}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)  # Cache HIT
    
    response = call_llm(prompt, model)
    r.set(key, json.dumps(response), ex=3600)
    return response
```

## Rate Limiter Pattern
```python
import time

def is_rate_limited(user_id, limit=30, window=60):
    key = f"ratelimit:{user_id}"
    now = time.time()
    
    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, now - window)  # Remove old
    pipe.zadd(key, {str(now): now})               # Add current
    pipe.zcard(key)                                # Count
    pipe.expire(key, window)                       # Auto-cleanup
    _, _, count, _ = pipe.execute()
    
    return count > limit
```
