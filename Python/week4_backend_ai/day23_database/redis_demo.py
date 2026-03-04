#!/usr/bin/env python3
"""Day 23 - Redis Caching"""

import json
from typing import Optional, Any, Callable
from datetime import timedelta
from functools import wraps
import hashlib


# ============================================
# REDIS CLIENT (Simulated for demo)
# ============================================

class FakeRedis:
    """
    Simulated Redis client for demonstration.
    In production, use: pip install redis
    
    import redis
    r = redis.Redis(host='localhost', port=6379, db=0)
    """
    
    def __init__(self):
        self._store = {}
        self._expiry = {}
    
    def set(self, key: str, value: str, ex: int = None) -> bool:
        """Set key with optional expiry in seconds."""
        self._store[key] = value
        if ex:
            self._expiry[key] = ex  # In real Redis, this triggers TTL
        return True
    
    def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        return self._store.get(key)
    
    def delete(self, key: str) -> int:
        """Delete key."""
        if key in self._store:
            del self._store[key]
            return 1
        return 0
    
    def exists(self, key: str) -> int:
        """Check if key exists."""
        return 1 if key in self._store else 0
    
    def setex(self, key: str, seconds: int, value: str) -> bool:
        """Set with expiry."""
        return self.set(key, value, ex=seconds)
    
    def incr(self, key: str) -> int:
        """Increment integer value."""
        val = int(self._store.get(key, 0)) + 1
        self._store[key] = str(val)
        return val
    
    def hset(self, name: str, key: str = None, value: str = None, mapping: dict = None) -> int:
        """Set hash field."""
        if name not in self._store:
            self._store[name] = {}
        if mapping:
            self._store[name].update(mapping)
            return len(mapping)
        self._store[name][key] = value
        return 1
    
    def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field."""
        if name in self._store:
            return self._store[name].get(key)
        return None
    
    def hgetall(self, name: str) -> dict:
        """Get all hash fields."""
        return self._store.get(name, {})
    
    def lpush(self, name: str, *values) -> int:
        """Push to list (left)."""
        if name not in self._store:
            self._store[name] = []
        for v in values:
            self._store[name].insert(0, v)
        return len(self._store[name])
    
    def lrange(self, name: str, start: int, end: int) -> list:
        """Get list range."""
        lst = self._store.get(name, [])
        return lst[start:end + 1 if end >= 0 else None]
    
    def sadd(self, name: str, *values) -> int:
        """Add to set."""
        if name not in self._store:
            self._store[name] = set()
        before = len(self._store[name])
        self._store[name].update(values)
        return len(self._store[name]) - before
    
    def smembers(self, name: str) -> set:
        """Get all set members."""
        return self._store.get(name, set())
    
    def flushdb(self) -> bool:
        """Clear all keys."""
        self._store.clear()
        self._expiry.clear()
        return True


# Create Redis instance
redis_client = FakeRedis()

# For real Redis:
# import redis
# redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


# ============================================
# CACHING UTILITIES
# ============================================

def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments."""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(expire_seconds: int = 300, prefix: str = "cache"):
    """
    Decorator for caching function results.
    
    Usage:
        @cached(expire_seconds=3600)
        def expensive_function(x, y):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = f"{prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(key, expire_seconds, json.dumps(result))
            
            return result
        return wrapper
    return decorator


# ============================================
# CACHE PATTERNS
# ============================================

class CacheManager:
    """
    Redis cache manager with common patterns.
    """
    
    def __init__(self, redis_instance, prefix: str = "app"):
        self.redis = redis_instance
        self.prefix = prefix
    
    def _key(self, key: str) -> str:
        """Add prefix to key."""
        return f"{self.prefix}:{key}"
    
    # --- String Operations ---
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """Set JSON-serializable value."""
        return self.redis.setex(
            self._key(key),
            expire,
            json.dumps(value)
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Get and deserialize value."""
        value = self.redis.get(self._key(key))
        if value:
            return json.loads(value)
        return None
    
    def delete(self, key: str) -> bool:
        """Delete key."""
        return self.redis.delete(self._key(key)) > 0
    
    # --- Cache-Aside Pattern ---
    
    def get_or_set(
        self, 
        key: str, 
        fallback: Callable, 
        expire: int = 3600
    ) -> Any:
        """
        Cache-aside pattern:
        1. Try to get from cache
        2. If miss, call fallback and cache result
        """
        value = self.get(key)
        if value is None:
            value = fallback()
            self.set(key, value, expire)
        return value
    
    # --- Rate Limiting ---
    
    def rate_limit(
        self, 
        key: str, 
        max_requests: int, 
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Rate limiting using Redis.
        Returns: (allowed, remaining)
        """
        full_key = self._key(f"rate:{key}")
        current = self.redis.incr(full_key)
        
        if current == 1:
            # First request, set expiry
            self.redis.setex(full_key, window_seconds, str(current))
        
        allowed = current <= max_requests
        remaining = max(0, max_requests - current)
        
        return allowed, remaining
    
    # --- Session Storage ---
    
    def set_session(
        self, 
        session_id: str, 
        data: dict, 
        expire: int = 3600
    ) -> bool:
        """Store session data."""
        return self.redis.setex(
            self._key(f"session:{session_id}"),
            expire,
            json.dumps(data)
        ) == True
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        value = self.redis.get(self._key(f"session:{session_id}"))
        if value:
            return json.loads(value)
        return None
    
    # --- Leaderboard (Sorted Set) ---
    
    def leaderboard_add(self, name: str, user: str, score: int):
        """Add score to leaderboard (using hash for simulation)."""
        self.redis.hset(self._key(f"lb:{name}"), user, str(score))
    
    def leaderboard_get(self, name: str) -> list:
        """Get sorted leaderboard."""
        data = self.redis.hgetall(self._key(f"lb:{name}"))
        sorted_data = sorted(
            data.items(), 
            key=lambda x: int(x[1]), 
            reverse=True
        )
        return [(user, int(score)) for user, score in sorted_data]


# Create cache manager instance
cache = CacheManager(redis_client)


# ============================================
# DEMONSTRATION
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("REDIS CACHING DEMONSTRATION")
    print("=" * 50)
    
    # --- Basic Operations ---
    print("\n--- Basic String Operations ---")
    
    redis_client.set("name", "John", ex=3600)
    print(f"Set 'name': John")
    print(f"Get 'name': {redis_client.get('name')}")
    
    redis_client.incr("counter")
    redis_client.incr("counter")
    print(f"Counter after 2 increments: {redis_client.get('counter')}")
    
    # --- Hash Operations ---
    print("\n--- Hash Operations ---")
    
    redis_client.hset("user:1", mapping={
        "name": "Alice",
        "email": "alice@example.com",
        "age": "30"
    })
    print(f"User hash: {redis_client.hgetall('user:1')}")
    print(f"User email: {redis_client.hget('user:1', 'email')}")
    
    # --- List Operations ---
    print("\n--- List Operations ---")
    
    redis_client.lpush("recent_searches", "python", "redis", "fastapi")
    print(f"Recent searches: {redis_client.lrange('recent_searches', 0, 2)}")
    
    # --- Set Operations ---
    print("\n--- Set Operations ---")
    
    redis_client.sadd("tags:post:1", "python", "backend", "tutorial")
    print(f"Post tags: {redis_client.smembers('tags:post:1')}")
    
    # --- Cache Manager ---
    print("\n--- Cache Manager ---")
    
    # Set and get
    cache.set("user:profile:1", {"id": 1, "name": "John"})
    profile = cache.get("user:profile:1")
    print(f"Cached profile: {profile}")
    
    # Cache-aside pattern
    def fetch_from_db():
        print("  → Fetching from database...")
        return {"id": 2, "name": "Jane"}
    
    # First call - cache miss
    print("First call (cache miss):")
    data = cache.get_or_set("user:2", fetch_from_db)
    print(f"  Result: {data}")
    
    # Second call - cache hit
    print("Second call (cache hit):")
    data = cache.get_or_set("user:2", fetch_from_db)
    print(f"  Result: {data}")
    
    # --- Cached Decorator ---
    print("\n--- @cached Decorator ---")
    
    call_count = 0
    
    @cached(expire_seconds=3600, prefix="demo")
    def expensive_calculation(x, y):
        global call_count
        call_count += 1
        return x + y
    
    print(f"First call: {expensive_calculation(5, 3)}, function called: {call_count}")
    print(f"Second call: {expensive_calculation(5, 3)}, function called: {call_count}")
    print(f"Different args: {expensive_calculation(5, 4)}, function called: {call_count}")
    
    # --- Rate Limiting ---
    print("\n--- Rate Limiting ---")
    
    for i in range(5):
        allowed, remaining = cache.rate_limit("api:user:1", max_requests=3, window_seconds=60)
        status = "✓ Allowed" if allowed else "✗ Blocked"
        print(f"  Request {i+1}: {status}, remaining: {remaining}")
    
    # --- Session Management ---
    print("\n--- Session Management ---")
    
    session_data = {"user_id": 123, "role": "admin"}
    cache.set_session("abc123", session_data)
    retrieved = cache.get_session("abc123")
    print(f"Session stored and retrieved: {retrieved}")
    
    # --- Leaderboard ---
    print("\n--- Leaderboard ---")
    
    cache.leaderboard_add("game", "Alice", 100)
    cache.leaderboard_add("game", "Bob", 150)
    cache.leaderboard_add("game", "Charlie", 75)
    
    print("Leaderboard:")
    for rank, (user, score) in enumerate(cache.leaderboard_get("game"), 1):
        print(f"  {rank}. {user}: {score}")
    
    print("\n" + "=" * 50)
    print("REDIS USE CASES")
    print("=" * 50)
    print("""
1. Caching: Store frequently accessed data
2. Sessions: User session storage
3. Rate Limiting: API request throttling
4. Leaderboards: Real-time rankings
5. Pub/Sub: Message broadcasting
6. Queues: Job/task queues
7. Real-time analytics: Counters & stats
""")
