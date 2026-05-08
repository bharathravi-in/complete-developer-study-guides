# Day 30: Python Interview Questions — Advanced & System Design

## Learning Objectives
- Master advanced Python internals questions
- Practice system design with Python components
- Solve hard coding challenges optimally
- Handle deep-dive follow-ups from senior interviewers

---

## 1. Python Internals & Advanced Concepts

**Q1: How does Python's garbage collector handle circular references?**
```python
import gc

# Reference counting handles most objects (refcount=0 → free)
# But circular references have refcount > 0 forever!

class Node:
    def __init__(self):
        self.ref = None

a = Node()
b = Node()
a.ref = b
b.ref = a  # Circular! Refcount never reaches 0

del a, b
# GC uses generational collection:
# - 3 generations (0, 1, 2) — young objects die fast
# - Detects cycles by tracing reachable objects
# - Unreachable cycles are collected
gc.collect()  # Forces collection

# Prevent: use weakref for back-references
import weakref
class Tree:
    def __init__(self, parent=None):
        self.children = []
        self.parent = weakref.ref(parent) if parent else None
```

**Q2: Explain metaclasses and give a use case.**
```python
# Metaclass: the class of a class (default is 'type')
# type(MyClass) → <class 'type'>

class ValidatedMeta(type):
    """Metaclass that ensures all methods have docstrings."""
    def __new__(mcs, name, bases, namespace):
        for key, value in namespace.items():
            if callable(value) and not key.startswith('_'):
                if not value.__doc__:
                    raise TypeError(f"Method '{key}' in {name} must have a docstring")
        return super().__new__(mcs, name, bases, namespace)

class APIHandler(metaclass=ValidatedMeta):
    def get(self):
        """Handle GET request."""
        pass
    
    # def post(self):  # TypeError! Missing docstring
    #     pass

# Real use cases: Django models, SQLAlchemy, ABC, enum
# Prefer __init_subclass__ for simpler cases (Python 3.6+)
```

**Q3: How does Python's import system work?**
```python
# 1. Check sys.modules cache (already imported? return cached)
# 2. Find the module (sys.path, finders)
# 3. Load the module (loaders)
# 4. Execute module code (top-level statements run)
# 5. Cache in sys.modules

import sys
# sys.path: list of directories to search
# sys.modules: dict of already-imported modules

# Import hooks for custom loading
class CustomFinder:
    def find_module(self, name, path=None):
        if name == "virtual_module":
            return CustomLoader()

# Circular imports: module partially loaded → AttributeError
# Fix: import inside function, or restructure
```

**Q4: Explain descriptors and the attribute lookup chain.**
```python
# Attribute lookup order:
# 1. Data descriptor on class (has __set__)
# 2. Instance __dict__
# 3. Non-data descriptor on class (only __get__)
# 4. Class __dict__
# 5. __getattr__ (fallback)

class Validated:
    """Data descriptor with __get__ and __set__."""
    def __set_name__(self, owner, name):
        self.name = f"_{name}"
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.name, None)
    
    def __set__(self, obj, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"Must be non-negative integer")
        setattr(obj, self.name, value)

class Product:
    price = Validated()   # Data descriptor
    quantity = Validated()
    
    def __init__(self, price, quantity):
        self.price = price      # Calls Validated.__set__
        self.quantity = quantity
```

**Q5: How would you implement `__slots__` from scratch (conceptually)?**
```python
# __slots__ replaces per-instance __dict__ with fixed-size struct
# Conceptually: class stores attribute names, instance stores values in array

# Without slots: each instance has a dict (~104 bytes overhead)
# With slots: instance has array of pointers (much smaller)

class Optimized:
    __slots__ = ('x', 'y', 'z')
    # No __dict__ created!
    # Can't add arbitrary attributes
    # ~40% less memory per instance
    # Slightly faster attribute access (direct offset vs dict lookup)

# Trade-offs:
# - Can't use __dict__-dependent features (vars(), **vars(obj))
# - Multiple inheritance with conflicting slots fails
# - Must redeclare in subclasses
```

---

## 2. Concurrency & Performance

**Q6: Design a producer-consumer system with backpressure.**
```python
import asyncio
from typing import AsyncGenerator

class Pipeline:
    def __init__(self, buffer_size: int = 100):
        self.queue = asyncio.Queue(maxsize=buffer_size)  # Backpressure!
        self._running = True
    
    async def produce(self, items: AsyncGenerator):
        async for item in items:
            await self.queue.put(item)  # Blocks if queue full
        await self.queue.put(None)  # Sentinel
    
    async def consume(self, worker_id: int):
        while True:
            item = await self.queue.get()
            if item is None:
                await self.queue.put(None)  # Propagate
                break
            await self.process(item, worker_id)
            self.queue.task_done()
    
    async def process(self, item, worker_id):
        await asyncio.sleep(0.01)  # Simulate work
        print(f"Worker-{worker_id}: {item}")
    
    async def run(self, source, num_workers: int = 5):
        producer = asyncio.create_task(self.produce(source))
        consumers = [
            asyncio.create_task(self.consume(i))
            for i in range(num_workers)
        ]
        await asyncio.gather(producer, *consumers)
```

**Q7: Implement a thread-safe LRU cache.**
```python
import threading
from collections import OrderedDict

class ThreadSafeLRU:
    def __init__(self, maxsize: int = 128):
        self.maxsize = maxsize
        self.cache = OrderedDict()
        self.lock = threading.Lock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key):
        with self.lock:
            if key in self.cache:
                self.hits += 1
                self.cache.move_to_end(key)
                return self.cache[key]
            self.misses += 1
            return None
    
    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                self.cache[key] = value
            else:
                if len(self.cache) >= self.maxsize:
                    self.cache.popitem(last=False)  # Remove LRU
                self.cache[key] = value
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0
```

---

## 3. System Design Questions

**Q8: Design a URL shortener in Python.**
```python
import hashlib
import string
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ShortURL:
    short_code: str
    original_url: str
    created_at: datetime
    click_count: int = 0

class URLShortener:
    BASE62 = string.ascii_letters + string.digits
    
    def __init__(self):
        self._url_map: dict[str, ShortURL] = {}
        self._reverse_map: dict[str, str] = {}
        self._counter = 0
    
    def shorten(self, url: str) -> str:
        # Check if already shortened
        if url in self._reverse_map:
            return self._reverse_map[url]
        
        # Generate short code (base62 encoding of counter)
        self._counter += 1
        code = self._encode(self._counter)
        
        entry = ShortURL(code, url, datetime.now())
        self._url_map[code] = entry
        self._reverse_map[url] = code
        return code
    
    def resolve(self, code: str) -> str | None:
        entry = self._url_map.get(code)
        if entry:
            entry.click_count += 1
            return entry.original_url
        return None
    
    def _encode(self, num: int) -> str:
        if num == 0:
            return self.BASE62[0]
        result = []
        while num:
            result.append(self.BASE62[num % 62])
            num //= 62
        return ''.join(reversed(result))

# Scale considerations:
# - Use Redis for fast lookups
# - Distributed counter (Snowflake ID)
# - Cache popular URLs
# - Analytics: track clicks, referrers, geography
```

**Q9: Design a rate limiter.**
```python
import time
from collections import defaultdict
from threading import Lock

class SlidingWindowRateLimiter:
    """Sliding window counter rate limiter."""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: dict[str, list[float]] = defaultdict(list)
        self.lock = Lock()
    
    def allow_request(self, client_id: str) -> bool:
        with self.lock:
            now = time.time()
            window_start = now - self.window
            
            # Remove expired timestamps
            self.requests[client_id] = [
                ts for ts in self.requests[client_id]
                if ts > window_start
            ]
            
            if len(self.requests[client_id]) < self.max_requests:
                self.requests[client_id].append(now)
                return True
            return False
    
    def remaining(self, client_id: str) -> int:
        now = time.time()
        window_start = now - self.window
        current = len([ts for ts in self.requests[client_id] if ts > window_start])
        return max(0, self.max_requests - current)

# Token bucket alternative:
class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate          # Tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()
        self.lock = Lock()
    
    def allow(self) -> bool:
        with self.lock:
            now = time.time()
            self.tokens = min(
                self.capacity,
                self.tokens + (now - self.last_refill) * self.rate
            )
            self.last_refill = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False
```

---

## 4. Hard Coding Challenges

```python
# 1. Implement LRU Cache (LeetCode 146)
class LRUCache:
    def __init__(self, capacity: int):
        from collections import OrderedDict
        self.cache = OrderedDict()
        self.capacity = capacity
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

# 2. Merge Intervals
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    for start, end in intervals[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged

# 3. Find median in data stream
import heapq

class MedianFinder:
    def __init__(self):
        self.small = []  # Max-heap (negate values)
        self.large = []  # Min-heap
    
    def add_num(self, num: int):
        heapq.heappush(self.small, -num)
        heapq.heappush(self.large, -heapq.heappop(self.small))
        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))
    
    def find_median(self) -> float:
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2

# 4. Word ladder (BFS)
from collections import deque

def word_ladder(begin: str, end: str, word_list: list[str]) -> int:
    word_set = set(word_list)
    if end not in word_set:
        return 0
    
    queue = deque([(begin, 1)])
    visited = {begin}
    
    while queue:
        word, steps = queue.popleft()
        for i in range(len(word)):
            for c in 'abcdefghijklmnopqrstuvwxyz':
                next_word = word[:i] + c + word[i+1:]
                if next_word == end:
                    return steps + 1
                if next_word in word_set and next_word not in visited:
                    visited.add(next_word)
                    queue.append((next_word, steps + 1))
    return 0
```

---

## Interview Questions

### Beginner
1. **What's the difference between `deepcopy` and `copy`?** `copy.copy()`: creates new outer object, but inner objects are shared (references). `copy.deepcopy()`: recursively copies everything — fully independent clone. Use shallow for: flat structures, when sharing inner objects is OK. Use deep for: nested mutable structures where independence is required.

2. **How do you handle exceptions properly in production code?** Catch specific exceptions (not bare `except:`). Log with context. Use custom exceptions for domain errors. Don't silence errors. Use `finally` for cleanup. Reraise with `raise ... from e` to preserve traceback chain. Let unexpected errors propagate to top-level handlers.

3. **What is duck typing?** "If it walks like a duck and quacks like a duck, it's a duck." Python doesn't check types — it checks behavior. If an object has the method you call, it works regardless of its class. Formal support: `typing.Protocol` provides duck typing with type checker validation. No need for explicit interfaces.

### Intermediate
4. **Explain Python's memory allocation strategy.** Layer 1: OS malloc for large objects (>512 bytes). Layer 2: pymalloc arena allocator for small objects — 256KB arenas → 4KB pools → 8-byte aligned blocks. Layer 3: free lists for common types (int, float, tuple). Small integer cache (-5 to 256), string interning. This reduces system call overhead significantly.

5. **How would you profile and optimize a slow Python application?** (1) Measure first: `cProfile` for function-level timing, `line_profiler` for line-level. (2) Find hotspot (usually 1-2 functions). (3) Optimize: better algorithm > better code > C extension. (4) For I/O: asyncio/threading. (5) For CPU: multiprocessing, NumPy vectorization, Cython. (6) Cache: `lru_cache` for repeated computations.

6. **Design a retry mechanism with exponential backoff.**
```python
import time, random
from functools import wraps

def retry(max_retries=3, base_delay=1, max_delay=60, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    jitter = random.uniform(0, delay * 0.1)
                    time.sleep(delay + jitter)
        return wrapper
    return decorator
```

### Advanced
7. **How would you design a task queue system in Python?** Components: (1) Queue (Redis/RabbitMQ), (2) Workers (multiprocessing), (3) Scheduler (cron-like), (4) Result backend (Redis). Workers: pull tasks, execute, store results. Reliability: acknowledge after processing, retry on failure, dead-letter queue. Monitor: queue depth, worker health, processing time. Existing: Celery, RQ, Dramatiq.

8. **Explain how you'd make a Python application handle 10K concurrent connections.** Use asyncio with uvloop. Single-threaded event loop handles all connections. Non-blocking I/O throughout (aiohttp, asyncpg). Connection pooling for databases. Horizontal scale: multiple process workers behind load balancer. Key: never block the event loop (CPU work → executor). Monitor: event loop latency.

9. **What changes would removing the GIL from Python require?** (PEP 703 / Python 3.13+) Reference counting becomes atomic (overhead). Biased reference counting (fast path for single-threaded). Per-object locks for container operations. Immortal objects (True, None, small ints). Free-threaded garbage collector. C extensions need updates (Py_INCREF/DECREF semantics change). Initially opt-in separate build.

---

## Hands-On Exercise
1. Implement a thread-safe connection pool with context manager
2. Design and implement a URL shortener with click analytics
3. Build a sliding window rate limiter (test with concurrent requests)
4. Solve LRU Cache, Merge Intervals, and MedianFinder
5. 45-minute mock system design: "Design a Python task queue"
