# Day 17: Async Programming — asyncio, Coroutines & Event Loop

## Learning Objectives
- Understand the event loop and cooperative multitasking
- Master `async/await` syntax and coroutines
- Use `asyncio` for concurrent I/O operations
- Implement async patterns: gather, semaphore, queue, streaming
- Build production async applications (web clients, servers)

---

## 1. Async Fundamentals (Beginner)

```python
import asyncio
import time

# A coroutine — defined with async def
async def greet(name: str, delay: float) -> str:
    """Async function: can await other coroutines."""
    print(f"Starting greet({name})")
    await asyncio.sleep(delay)  # Non-blocking sleep
    print(f"Done greet({name})")
    return f"Hello, {name}!"

# Running async code
async def main():
    # Sequential (one after another): 3 seconds total
    result1 = await greet("Alice", 1)
    result2 = await greet("Bob", 2)
    print(result1, result2)

asyncio.run(main())

# Concurrent (both at same time): 2 seconds total!
async def main_concurrent():
    # gather runs coroutines concurrently
    results = await asyncio.gather(
        greet("Alice", 1),
        greet("Bob", 2),
        greet("Charlie", 1.5),
    )
    print(results)  # ["Hello, Alice!", "Hello, Bob!", "Hello, Charlie!"]

asyncio.run(main_concurrent())
```

### How the Event Loop Works

```python
"""
Event Loop — single-threaded cooperative multitasking:

1. Coroutine runs until it hits `await`
2. At `await`, control returns to event loop
3. Event loop checks: any I/O ready? Any timers expired?
4. Resumes the coroutine whose I/O completed
5. Repeat

Key insight: NO preemption. Coroutines voluntarily yield via await.
If a coroutine does CPU work without awaiting → blocks everything!
"""

# BAD: Blocking the event loop
async def bad_cpu_work():
    # This blocks ALL other coroutines!
    result = sum(i**2 for i in range(10_000_000))
    return result

# GOOD: Run CPU-bound work in thread pool
async def good_cpu_work():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, cpu_intensive_function)
    return result
```

---

## 2. Practical Async Patterns (Intermediate)

```python
import asyncio
import aiohttp  # pip install aiohttp

# Concurrent HTTP requests
async def fetch_url(session: aiohttp.ClientSession, url: str) -> dict:
    async with session.get(url) as response:
        return {"url": url, "status": response.status, "size": len(await response.text())}

async def fetch_all(urls: list[str]) -> list[dict]:
    """Fetch multiple URLs concurrently."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

# 100 URLs in ~1 second (vs ~100s sequential)
urls = [f"https://httpbin.org/get?id={i}" for i in range(100)]
results = asyncio.run(fetch_all(urls))


# Semaphore — limit concurrency (don't overwhelm servers)
async def fetch_with_limit(urls: list[str], max_concurrent: int = 10):
    """Limit to N concurrent requests."""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def limited_fetch(session, url):
        async with semaphore:  # Only N coroutines enter at a time
            async with session.get(url) as resp:
                return await resp.json()
    
    async with aiohttp.ClientSession() as session:
        tasks = [limited_fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)


# Timeout handling
async def fetch_with_timeout(url: str, timeout: float = 5.0):
    try:
        async with asyncio.timeout(timeout):  # Python 3.11+
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    return await resp.json()
    except asyncio.TimeoutError:
        return {"error": f"Timeout after {timeout}s", "url": url}
```

### Async Generators & Iterators

```python
# Async generator — yield values asynchronously
async def fetch_pages(base_url: str, max_pages: int = 10):
    """Async generator: fetch paginated API."""
    async with aiohttp.ClientSession() as session:
        for page in range(1, max_pages + 1):
            url = f"{base_url}?page={page}"
            async with session.get(url) as resp:
                data = await resp.json()
                if not data["results"]:
                    break
                yield data["results"]

# Consume with async for
async def process_all_pages():
    async for page_data in fetch_pages("https://api.example.com/items"):
        for item in page_data:
            await process_item(item)


# Async context manager
class AsyncDatabasePool:
    def __init__(self, url: str, max_connections: int = 10):
        self.url = url
        self.max_connections = max_connections
        self._pool = None
    
    async def __aenter__(self):
        self._pool = await create_pool(self.url, self.max_connections)
        return self._pool
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._pool.close()

async def query_db():
    async with AsyncDatabasePool("postgres://localhost/db") as pool:
        result = await pool.fetch("SELECT * FROM users")
        return result
```

---

## 3. Advanced Async Patterns (Advanced)

### Producer-Consumer with asyncio.Queue

```python
import asyncio
from dataclasses import dataclass

@dataclass
class Task:
    id: int
    url: str

async def producer(queue: asyncio.Queue, tasks: list[Task]):
    """Produce tasks into queue."""
    for task in tasks:
        await queue.put(task)
    # Signal completion
    await queue.put(None)

async def consumer(queue: asyncio.Queue, name: str, results: list):
    """Consume and process tasks."""
    while True:
        task = await queue.get()
        if task is None:
            await queue.put(None)  # Propagate sentinel
            break
        
        result = await process_task(task)
        results.append(result)
        queue.task_done()
        print(f"{name} completed task {task.id}")

async def run_pipeline(tasks: list[Task], num_workers: int = 5):
    queue = asyncio.Queue(maxsize=100)  # Backpressure
    results = []
    
    # Start producer and consumers concurrently
    producer_task = asyncio.create_task(producer(queue, tasks))
    consumers = [
        asyncio.create_task(consumer(queue, f"worker-{i}", results))
        for i in range(num_workers)
    ]
    
    await producer_task
    await asyncio.gather(*consumers)
    return results
```

### Error Handling & Retry

```python
import asyncio
from typing import TypeVar, Callable, Awaitable
import random

T = TypeVar('T')

async def retry_async(
    coro_factory: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
) -> T:
    """Retry an async operation with exponential backoff + jitter."""
    for attempt in range(max_retries):
        try:
            return await coro_factory()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay + jitter:.1f}s")
            await asyncio.sleep(delay + jitter)

# Usage
result = await retry_async(
    lambda: fetch_url(session, "https://flaky-api.com/data"),
    max_retries=5,
    base_delay=2.0,
)
```

### Structured Concurrency with TaskGroup (Python 3.11+)

```python
async def process_batch(items: list[str]) -> list[dict]:
    """Process items with structured concurrency."""
    results = []
    
    async with asyncio.TaskGroup() as tg:
        # All tasks are awaited, exceptions propagate cleanly
        tasks = [tg.create_task(process_item(item)) for item in items]
    
    # Only reaches here if ALL tasks succeeded
    return [task.result() for task in tasks]

# If any task raises, ALL others are cancelled and the exception propagates
# This prevents orphan tasks (unlike gather with return_exceptions=True)
```

---

## Interview Questions

### Beginner
1. **What is `async/await` and how does it differ from threading?** `async/await` is cooperative multitasking: coroutines voluntarily yield control at `await` points. Single-threaded, no race conditions, no locks needed. Threading: preemptive (OS decides when to switch), needs locks for shared data. Async is more efficient for I/O (no thread overhead), but can't help with CPU-bound work.

2. **What is the event loop?** The event loop is the core of asyncio — it manages and schedules coroutines. It runs in a single thread, continuously checking: which coroutines are ready to resume (I/O completed, timer expired)? It multiplexes many concurrent operations on one thread. Like a restaurant waiter handling many tables vs one waiter per table (threading).

3. **When should you use asyncio vs threading?** Asyncio: many concurrent connections (1000s), network servers, web scraping, API clients. Threading: moderate concurrency (10-100), using blocking libraries without async versions, simpler code. Asyncio is more scalable (1 coroutine = ~1KB vs 1 thread = ~1MB), but requires async-compatible libraries.

### Intermediate
4. **What happens if you block the event loop?** Everything stops! Since asyncio is single-threaded, blocking code (CPU work, `time.sleep()`, synchronous I/O) halts ALL coroutines. Fix: use `await asyncio.sleep()` not `time.sleep()`, run blocking code in executor (`loop.run_in_executor()`), use async libraries (aiohttp, asyncpg, aiofiles).

5. **Explain `asyncio.gather()` vs `asyncio.TaskGroup`.** `gather()`: runs coroutines concurrently, returns all results. With `return_exceptions=True`, captures errors without cancelling others. `TaskGroup` (3.11+): structured concurrency — if any task fails, ALL others are cancelled. Prevents orphan tasks. TaskGroup is safer for production (no leaked tasks), gather is more flexible.

6. **How do you limit concurrency in asyncio?** `asyncio.Semaphore(N)`: allows only N coroutines to enter the critical section simultaneously. Pattern: `async with semaphore: await operation()`. Also: bounded `asyncio.Queue(maxsize=N)` for backpressure. These prevent overwhelming external services or exhausting resources.

### Advanced
7. **Design an async web scraper that handles rate limiting, retries, and errors.** Components: (1) URL queue (asyncio.Queue with backpressure), (2) Worker pool (N consumer coroutines), (3) Rate limiter (semaphore + delay between requests), (4) Retry with exponential backoff, (5) Error classification (transient vs permanent), (6) Result aggregation. Use aiohttp with connection pooling, respect robots.txt.

8. **How does asyncio integrate with synchronous/blocking code?** `loop.run_in_executor(None, sync_fn)`: runs blocking code in ThreadPoolExecutor without blocking event loop. For CPU-bound: use ProcessPoolExecutor. `asyncio.to_thread(fn)` (3.9+): simpler API for thread offloading. Going the other direction: `asyncio.run()` from sync code, or `loop.run_until_complete()`.

9. **Compare asyncio event loop implementations (uvloop, etc.) and performance considerations.** uvloop (Cython wrapper around libuv): 2-4x faster than default asyncio loop. Production tips: use uvloop, set appropriate connection pool sizes, profile with `asyncio.get_event_loop().slow_callback_duration`, avoid creating too many tasks (memory), use `TaskGroup` for structured cleanup. Monitor: pending tasks count, callback execution time.

---

## Hands-On Exercise
1. Fetch 50 URLs concurrently with aiohttp and measure vs sequential requests
2. Implement a rate-limited API client (max 10 requests/second)
3. Build a producer-consumer pipeline with asyncio.Queue
4. Create an async retry decorator with exponential backoff
5. Write an async web server that handles 1000 concurrent connections
