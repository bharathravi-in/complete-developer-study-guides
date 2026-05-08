# Day 16: Multithreading & Multiprocessing — Concurrency in Python

## Learning Objectives
- Use `threading` for I/O-bound concurrency
- Use `multiprocessing` for CPU-bound parallelism
- Master `concurrent.futures` for clean parallel execution
- Handle synchronization with locks, queues, and events
- Choose the right concurrency model for each problem

---

## 1. Threading for I/O-Bound Work (Beginner)

```python
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor

# Basic threading
def download_page(url: str) -> int:
    """I/O-bound: network wait releases GIL."""
    response = requests.get(url, timeout=10)
    print(f"Downloaded {url}: {response.status_code}")
    return response.status_code

urls = [
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/1",
]

# Sequential: ~3 seconds
start = time.perf_counter()
for url in urls:
    download_page(url)
print(f"Sequential: {time.perf_counter() - start:.2f}s")

# Threaded: ~1 second (concurrent I/O)
start = time.perf_counter()
threads = []
for url in urls:
    t = threading.Thread(target=download_page, args=(url,))
    threads.append(t)
    t.start()
for t in threads:
    t.join()  # Wait for all to complete
print(f"Threaded: {time.perf_counter() - start:.2f}s")


# BETTER: ThreadPoolExecutor (cleaner API)
start = time.perf_counter()
with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(download_page, urls))
print(f"Pool: {time.perf_counter() - start:.2f}s")
print(results)  # [200, 200, 200]
```

### Thread Synchronization

```python
import threading
from queue import Queue

# Race condition example
counter = 0

def increment_unsafe():
    global counter
    for _ in range(100_000):
        counter += 1  # NOT atomic! Read-modify-write race

# Fix with Lock
lock = threading.Lock()
counter = 0

def increment_safe():
    global counter
    for _ in range(100_000):
        with lock:  # Only one thread at a time
            counter += 1

# Thread-safe queue for producer-consumer
def producer(queue: Queue, items: list):
    for item in items:
        queue.put(item)
        time.sleep(0.1)
    queue.put(None)  # Sentinel to signal done

def consumer(queue: Queue, name: str):
    while True:
        item = queue.get()
        if item is None:
            queue.put(None)  # Pass sentinel to next consumer
            break
        print(f"{name} processed: {item}")
        queue.task_done()

q = Queue(maxsize=10)
threading.Thread(target=producer, args=(q, range(20))).start()
threading.Thread(target=consumer, args=(q, "Worker-1")).start()
threading.Thread(target=consumer, args=(q, "Worker-2")).start()
```

---

## 2. Multiprocessing for CPU-Bound Work (Intermediate)

```python
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
import time
import math

def cpu_intensive(n: int) -> float:
    """CPU-bound: compute prime check."""
    total = 0
    for i in range(2, n):
        if all(i % j != 0 for j in range(2, int(math.sqrt(i)) + 1)):
            total += i
    return total

numbers = [100_000, 100_000, 100_000, 100_000]

# Sequential: ~8 seconds on 4 cores
start = time.perf_counter()
results = [cpu_intensive(n) for n in numbers]
print(f"Sequential: {time.perf_counter() - start:.2f}s")

# Multiprocessing: ~2 seconds (true parallelism!)
start = time.perf_counter()
with ProcessPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(cpu_intensive, numbers))
print(f"Parallel: {time.perf_counter() - start:.2f}s")


# Shared state between processes
def worker(shared_array, lock, index, value):
    with lock:
        shared_array[index] = value

if __name__ == "__main__":
    # Shared memory array
    shared_arr = mp.Array('i', 10)  # 10 integers
    lock = mp.Lock()
    
    processes = []
    for i in range(10):
        p = mp.Process(target=worker, args=(shared_arr, lock, i, i * 10))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    print(list(shared_arr))  # [0, 10, 20, 30, ...]


# Inter-process communication with Queue
def producer_process(queue: mp.Queue):
    for i in range(100):
        queue.put(f"item_{i}")
    queue.put("DONE")

def consumer_process(queue: mp.Queue, results: mp.Queue):
    while True:
        item = queue.get()
        if item == "DONE":
            break
        results.put(item.upper())
```

### Process Pool with Progress

```python
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

def process_file(filepath: str) -> dict:
    """Process a single file (CPU-bound)."""
    # Simulate work
    data = open(filepath).read()
    word_count = len(data.split())
    return {"file": filepath, "words": word_count}

files = [f"data/file_{i}.txt" for i in range(100)]

# Process with progress bar
with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
    futures = {executor.submit(process_file, f): f for f in files}
    
    results = []
    for future in tqdm(as_completed(futures), total=len(files)):
        try:
            result = future.result(timeout=30)
            results.append(result)
        except Exception as e:
            filepath = futures[future]
            print(f"Error processing {filepath}: {e}")
```

---

## 3. Advanced Patterns (Advanced)

### concurrent.futures — Unified API

```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future
from concurrent.futures import wait, FIRST_COMPLETED
import time

def resilient_parallel(tasks, worker_fn, max_workers=4, timeout=30):
    """Parallel execution with error handling and timeout."""
    results = {}
    errors = {}
    
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(worker_fn, task): task 
            for task in tasks
        }
        
        done, not_done = wait(
            future_to_task.keys(),
            timeout=timeout,
            return_when=FIRST_COMPLETED  # or ALL_COMPLETED
        )
        
        # Process completed
        for future in done:
            task = future_to_task[future]
            try:
                results[task] = future.result()
            except Exception as e:
                errors[task] = str(e)
        
        # Cancel timed-out
        for future in not_done:
            future.cancel()
            errors[future_to_task[future]] = "Timeout"
    
    return results, errors
```

### Thread Pool for Web Scraping

```python
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from queue import Queue
import requests

@dataclass
class CrawlResult:
    url: str
    status: int
    content_length: int
    error: str | None = None

class WebCrawler:
    """Thread-pool based concurrent web crawler."""
    
    def __init__(self, max_workers: int = 10, timeout: int = 10):
        self.max_workers = max_workers
        self.timeout = timeout
        self.results: list[CrawlResult] = []
        self._lock = threading.Lock()
    
    def _fetch(self, url: str) -> CrawlResult:
        try:
            resp = requests.get(url, timeout=self.timeout)
            return CrawlResult(url, resp.status_code, len(resp.content))
        except Exception as e:
            return CrawlResult(url, 0, 0, error=str(e))
    
    def crawl(self, urls: list[str]) -> list[CrawlResult]:
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            results = list(executor.map(self._fetch, urls))
        return results

# Usage
crawler = WebCrawler(max_workers=20)
results = crawler.crawl(["https://example.com"] * 50)
successful = [r for r in results if r.status == 200]
```

### Choosing the Right Model

```python
"""
Decision Guide:
┌─────────────────────────────────────────────────┐
│ Is the task I/O-bound or CPU-bound?             │
├─────────────────┬───────────────────────────────┤
│ I/O-bound       │ CPU-bound                     │
│ (network, disk) │ (computation, data processing)│
├─────────────────┼───────────────────────────────┤
│ asyncio (best)  │ multiprocessing               │
│ threading       │ ProcessPoolExecutor           │
│ ThreadPoolExec  │ C extensions (numpy, etc.)    │
└─────────────────┴───────────────────────────────┘

Key rules:
1. I/O-bound → threading or asyncio (GIL released during I/O)
2. CPU-bound → multiprocessing (separate processes, bypasses GIL)
3. Need shared state → threading with locks (or multiprocessing.Manager)
4. Simple parallelism → concurrent.futures (unified API)
5. Many connections → asyncio (thousands of concurrent connections)
6. Quick parallel map → ProcessPoolExecutor.map()
"""
```

---

## Interview Questions

### Beginner
1. **What's the difference between a thread and a process?** Threads share the same memory space (lightweight, fast communication, but need locks for shared data). Processes have separate memory (heavyweight, need IPC, but truly parallel). In Python: threads can't run CPU code in parallel (GIL), processes can. Threads for I/O concurrency, processes for CPU parallelism.

2. **Why doesn't multithreading speed up CPU-bound Python code?** The GIL (Global Interpreter Lock) allows only one thread to execute Python bytecode at a time. For CPU-bound work, threads take turns on one core instead of running on multiple cores simultaneously. Solution: use `multiprocessing` (separate processes with separate GILs) or C extensions that release the GIL.

3. **What is `concurrent.futures` and why use it?** A high-level API providing `ThreadPoolExecutor` and `ProcessPoolExecutor` with identical interfaces. Benefits: simple `.map()` and `.submit()`, automatic thread/process management, `as_completed()` for results as they arrive, context manager for cleanup. Switch between threading and multiprocessing by changing one class name.

### Intermediate
4. **Explain race conditions and how to prevent them.** A race condition occurs when multiple threads read-modify-write shared data simultaneously, causing inconsistent state. Prevention: `threading.Lock` (mutual exclusion), `Queue` (thread-safe data transfer), atomic operations, immutable data. Best practice: minimize shared mutable state; use message passing (queues) over shared memory.

5. **When would you use `asyncio` vs `threading` for I/O-bound work?** asyncio: single-threaded, event loop, great for thousands of concurrent connections (web servers, chat). Threading: simpler mental model, works with blocking libraries, good for moderate concurrency (10-100 threads). asyncio is more efficient (no thread overhead) but requires `async/await` throughout. Threading works with existing synchronous code.

6. **How do you share data between processes?** Options: `multiprocessing.Queue` (message passing, preferred), `multiprocessing.Manager()` (shared objects, slow due to IPC), `multiprocessing.Value/Array` (shared memory, fast but limited types), `multiprocessing.shared_memory` (Python 3.8+, efficient for large data). Prefer message passing (queues) over shared state.

### Advanced
7. **Design a parallel data processing pipeline with backpressure.** Producer → bounded Queue(maxsize=N) → worker pool → output Queue → consumer. Bounded queues provide backpressure: producer blocks when queue full (slow consumer → slow producer). Worker pool: ProcessPoolExecutor for CPU-bound stages. Monitor: queue sizes indicate bottlenecks. Scale: add workers to bottleneck stage.

8. **How would you implement a thread pool from scratch?** Worker threads loop: pull tasks from a Queue, execute them, put results in output Queue. Manager tracks: idle workers, pending tasks, completed tasks. Shutdown: put sentinel values (None) for each worker. Dynamic sizing: start min workers, add when queue grows, reap idle workers after timeout.

9. **Compare Python's concurrency with other languages. What are the tradeoffs?** Python's GIL makes single-threaded code faster (no locking overhead) but limits CPU parallelism. Go: goroutines (lightweight, true parallelism). Java: real threads with true parallelism. Rust: fearless concurrency (compile-time safety). Python compensates with: multiprocessing, async I/O, C extensions (NumPy releases GIL), and simplicity for typical I/O-heavy workloads.

---

## Hands-On Exercise
1. Build a concurrent file downloader using ThreadPoolExecutor
2. Implement a parallel number cruncher with ProcessPoolExecutor
3. Create a producer-consumer pipeline with bounded queues
4. Write a thread-safe counter class with Lock
5. Profile and compare: sequential vs threaded vs multiprocess for your workload
