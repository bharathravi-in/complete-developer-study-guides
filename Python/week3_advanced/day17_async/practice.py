#!/usr/bin/env python3
"""Day 17 - Async Programming Deep Dive"""

import asyncio
import time
from typing import List, Any
from contextlib import asynccontextmanager

print("=" * 50)
print("ASYNC PROGRAMMING")
print("=" * 50)


# ============================================
# 1. BASIC ASYNC/AWAIT
# ============================================
print("\n--- 1. BASIC ASYNC/AWAIT ---")


async def say_hello(name: str, delay: float) -> str:
    """Simple async function (coroutine)"""
    print(f"  Starting: {name}")
    await asyncio.sleep(delay)  # Non-blocking sleep
    print(f"  Finished: {name}")
    return f"Hello, {name}!"


async def main_basic():
    # Sequential execution
    result1 = await say_hello("Alice", 1)
    result2 = await say_hello("Bob", 1)
    print(f"  Results: {result1}, {result2}")


print("Sequential (slow):")
start = time.perf_counter()
asyncio.run(main_basic())
print(f"  Time: {time.perf_counter() - start:.2f}s")


# ============================================
# 2. CONCURRENT EXECUTION
# ============================================
print("\n--- 2. CONCURRENT EXECUTION ---")


async def main_concurrent():
    # Concurrent execution with gather
    results = await asyncio.gather(
        say_hello("Alice", 1),
        say_hello("Bob", 1),
        say_hello("Charlie", 1),
    )
    print(f"  Results: {results}")


print("Concurrent (fast):")
start = time.perf_counter()
asyncio.run(main_concurrent())
print(f"  Time: {time.perf_counter() - start:.2f}s")


# ============================================
# 3. TASKS
# ============================================
print("\n--- 3. TASKS ---")


async def main_tasks():
    # Create tasks for concurrent execution
    task1 = asyncio.create_task(say_hello("Task1", 0.5))
    task2 = asyncio.create_task(say_hello("Task2", 0.5))
    
    # Do other work while tasks run
    print("  Tasks created, doing other work...")
    await asyncio.sleep(0.2)
    print("  Other work done, waiting for tasks...")
    
    # Wait for tasks
    result1 = await task1
    result2 = await task2
    
    print(f"  Task results: {result1}, {result2}")


asyncio.run(main_tasks())


# ============================================
# 4. TIMEOUT AND CANCELLATION
# ============================================
print("\n--- 4. TIMEOUT AND CANCELLATION ---")


async def long_operation():
    print("  Long operation starting...")
    await asyncio.sleep(10)
    return "Done"


async def main_timeout():
    try:
        # Timeout after 1 second
        result = await asyncio.wait_for(long_operation(), timeout=1.0)
        print(f"  Result: {result}")
    except asyncio.TimeoutError:
        print("  Operation timed out!")


asyncio.run(main_timeout())


# Task cancellation
async def main_cancellation():
    task = asyncio.create_task(long_operation())
    
    await asyncio.sleep(0.5)
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        print("  Task was cancelled!")


asyncio.run(main_cancellation())


# ============================================
# 5. ASYNC GENERATORS
# ============================================
print("\n--- 5. ASYNC GENERATORS ---")


async def async_range(start: int, stop: int, delay: float = 0.1):
    """Async generator"""
    for i in range(start, stop):
        await asyncio.sleep(delay)
        yield i


async def main_async_gen():
    print("  Async generator values:")
    async for value in async_range(0, 5, 0.1):
        print(f"    Got: {value}")


asyncio.run(main_async_gen())


# ============================================
# 6. ASYNC CONTEXT MANAGERS
# ============================================
print("\n--- 6. ASYNC CONTEXT MANAGERS ---")


class AsyncDatabase:
    """Async context manager example"""
    
    def __init__(self, name: str):
        self.name = name
    
    async def __aenter__(self):
        print(f"  Connecting to {self.name}...")
        await asyncio.sleep(0.2)
        print(f"  Connected!")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print(f"  Disconnecting from {self.name}...")
        await asyncio.sleep(0.1)
        print(f"  Disconnected!")
        return False
    
    async def query(self, sql: str) -> list:
        await asyncio.sleep(0.1)
        return [{"data": f"Result for: {sql}"}]


async def main_context():
    async with AsyncDatabase("users_db") as db:
        result = await db.query("SELECT * FROM users")
        print(f"  Query result: {result}")


asyncio.run(main_context())


# Using asynccontextmanager decorator
@asynccontextmanager
async def async_timer(name: str):
    start = time.perf_counter()
    print(f"  Starting {name}")
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"  {name} took {elapsed:.2f}s")


async def main_timer():
    async with async_timer("operation"):
        await asyncio.sleep(0.5)


asyncio.run(main_timer())


# ============================================
# 7. SEMAPHORES (RATE LIMITING)
# ============================================
print("\n--- 7. SEMAPHORES ---")


async def fetch_with_semaphore(semaphore: asyncio.Semaphore, url: str) -> str:
    async with semaphore:
        print(f"  Fetching: {url}")
        await asyncio.sleep(0.5)  # Simulate network request
        return f"Data from {url}"


async def main_semaphore():
    # Limit to 2 concurrent requests
    semaphore = asyncio.Semaphore(2)
    
    urls = [f"http://example.com/{i}" for i in range(5)]
    
    tasks = [fetch_with_semaphore(semaphore, url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    print(f"  Got {len(results)} results")


start = time.perf_counter()
asyncio.run(main_semaphore())
print(f"  Time with semaphore(2): {time.perf_counter() - start:.2f}s")


# ============================================
# 8. QUEUES
# ============================================
print("\n--- 8. ASYNC QUEUES ---")


async def producer(queue: asyncio.Queue, n: int):
    for i in range(n):
        await asyncio.sleep(0.1)
        await queue.put(i)
        print(f"  Produced: {i}")
    await queue.put(None)  # Sentinel


async def consumer(queue: asyncio.Queue, name: str):
    while True:
        item = await queue.get()
        if item is None:
            queue.task_done()
            break
        print(f"  {name} consumed: {item}")
        await asyncio.sleep(0.2)
        queue.task_done()


async def main_queue():
    queue = asyncio.Queue(maxsize=3)
    
    await asyncio.gather(
        producer(queue, 5),
        consumer(queue, "Consumer1"),
    )


asyncio.run(main_queue())


# ============================================
# 9. ERROR HANDLING
# ============================================
print("\n--- 9. ERROR HANDLING ---")


async def may_fail(fail: bool):
    await asyncio.sleep(0.1)
    if fail:
        raise ValueError("Operation failed!")
    return "Success"


async def main_errors():
    # gather with return_exceptions
    results = await asyncio.gather(
        may_fail(False),
        may_fail(True),
        may_fail(False),
        return_exceptions=True
    )
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"  Task {i}: Error - {result}")
        else:
            print(f"  Task {i}: {result}")


asyncio.run(main_errors())


# ============================================
# 10. BEST PRACTICES
# ============================================
print("\n--- 10. BEST PRACTICES ---")

print("""
Async Best Practices:

1. Use asyncio.run() to run main coroutine
2. Use asyncio.gather() for concurrent tasks
3. Use asyncio.create_task() for background tasks
4. Always await coroutines (don't forget!)
5. Use asyncio.wait_for() for timeouts
6. Use Semaphores to limit concurrency
7. Use async context managers for resources
8. Handle exceptions in gather with return_exceptions=True
9. Don't block the event loop with sync code
10. Use run_in_executor() for blocking I/O

Common mistakes:
❌ Forgetting to await a coroutine
❌ Running blocking code in async function
❌ Not handling cancellation properly
❌ Creating too many concurrent tasks

For CPU-bound tasks, use:
- concurrent.futures.ProcessPoolExecutor
- loop.run_in_executor(executor, func, *args)
""")


print("\n✅ Day 17 completed!")
