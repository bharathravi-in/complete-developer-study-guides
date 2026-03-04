#!/usr/bin/env python3
"""Day 16 - Multithreading & Multiprocessing"""

import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time
import queue
import os

print("=" * 50)
print("MULTITHREADING & MULTIPROCESSING")
print("=" * 50)

# ============================================
# 1. BASIC THREADING
# ============================================
print("\n--- 1. BASIC THREADING ---")


def worker(name: str, delay: float):
    """Simple worker function"""
    print(f"  {name} starting")
    time.sleep(delay)
    print(f"  {name} finished")


# Create and start threads
threads = []
for i in range(3):
    t = threading.Thread(target=worker, args=(f"Thread-{i}", 0.5))
    threads.append(t)
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()

print("All threads completed")


# ============================================
# 2. THREADING WITH CLASS
# ============================================
print("\n--- 2. THREAD CLASS ---")


class WorkerThread(threading.Thread):
    def __init__(self, task_id: int):
        super().__init__()
        self.task_id = task_id
        self.result = None
    
    def run(self):
        """Override run method"""
        print(f"  Task {self.task_id} starting (thread: {self.name})")
        time.sleep(0.3)
        self.result = self.task_id ** 2
        print(f"  Task {self.task_id} completed")


threads = [WorkerThread(i) for i in range(3)]
for t in threads:
    t.start()
for t in threads:
    t.join()

results = [t.result for t in threads]
print(f"Results: {results}")


# ============================================
# 3. THREAD SYNCHRONIZATION
# ============================================
print("\n--- 3. THREAD SYNCHRONIZATION ---")

# Without lock (race condition)
counter_unsafe = 0


def increment_unsafe():
    global counter_unsafe
    for _ in range(100000):
        counter_unsafe += 1


# With lock (thread-safe)
counter_safe = 0
lock = threading.Lock()


def increment_safe():
    global counter_safe
    for _ in range(100000):
        with lock:
            counter_safe += 1


# Test unsafe
threads = [threading.Thread(target=increment_unsafe) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"Unsafe counter (expected 500000): {counter_unsafe}")

# Test safe
threads = [threading.Thread(target=increment_safe) for _ in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print(f"Safe counter (expected 500000): {counter_safe}")


# ============================================
# 4. THREAD-SAFE QUEUE
# ============================================
print("\n--- 4. THREAD-SAFE QUEUE ---")

task_queue = queue.Queue()
results_queue = queue.Queue()


def producer():
    for i in range(5):
        task_queue.put(i)
        print(f"  Produced: {i}")
        time.sleep(0.1)
    task_queue.put(None)  # Sentinel


def consumer():
    while True:
        item = task_queue.get()
        if item is None:
            break
        result = item ** 2
        results_queue.put(result)
        print(f"  Consumed: {item} -> {result}")
        task_queue.task_done()


producer_thread = threading.Thread(target=producer)
consumer_thread = threading.Thread(target=consumer)

producer_thread.start()
consumer_thread.start()

producer_thread.join()
consumer_thread.join()


# ============================================
# 5. MULTIPROCESSING BASICS
# ============================================
print("\n--- 5. MULTIPROCESSING ---")


def cpu_intensive(n: int) -> int:
    """CPU-bound task"""
    total = 0
    for i in range(n):
        total += i ** 2
    return total


# Single process timing
start = time.perf_counter()
results = [cpu_intensive(1000000) for _ in range(4)]
single_time = time.perf_counter() - start
print(f"Single process: {single_time:.2f}s")

# Multiprocessing timing
if __name__ == "__main__":
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(cpu_intensive, [1000000] * 4))
    multi_time = time.perf_counter() - start
    print(f"Multiprocessing: {multi_time:.2f}s")
    print(f"Speedup: {single_time/multi_time:.2f}x")


# ============================================
# 6. CONCURRENT.FUTURES
# ============================================
print("\n--- 6. CONCURRENT.FUTURES ---")


def fetch_url(url: str) -> str:
    """Simulate fetching URL"""
    time.sleep(0.5)  # Simulate network delay
    return f"Content from {url}"


urls = [f"http://example.com/page{i}" for i in range(5)]

# ThreadPoolExecutor for I/O-bound tasks
print("\nThreadPoolExecutor:")
start = time.perf_counter()
with ThreadPoolExecutor(max_workers=5) as executor:
    # Submit all tasks
    futures = [executor.submit(fetch_url, url) for url in urls]
    
    # Get results as they complete
    for future in futures:
        result = future.result()
        print(f"  Got: {result[:30]}...")

print(f"Time: {time.perf_counter() - start:.2f}s")


# Map vs Submit
print("\nUsing executor.map():")
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(fetch_url, urls[:3]))
    for r in results:
        print(f"  {r[:30]}...")


# ============================================
# 7. PROCESS COMMUNICATION
# ============================================
print("\n--- 7. PROCESS COMMUNICATION ---")


def worker_with_queue(input_q, output_q):
    """Worker that uses queues for communication"""
    while True:
        item = input_q.get()
        if item is None:
            break
        result = item ** 2
        output_q.put((item, result))


if __name__ == "__main__":
    input_queue = multiprocessing.Queue()
    output_queue = multiprocessing.Queue()
    
    # Start worker process
    p = multiprocessing.Process(
        target=worker_with_queue,
        args=(input_queue, output_queue)
    )
    p.start()
    
    # Send tasks
    for i in range(5):
        input_queue.put(i)
    input_queue.put(None)  # Signal to stop
    
    # Get results
    p.join()
    while not output_queue.empty():
        item, result = output_queue.get()
        print(f"  {item}² = {result}")


# ============================================
# 8. SHARED STATE
# ============================================
print("\n--- 8. SHARED STATE ---")


def increment_shared(counter, lock, n):
    """Increment shared counter"""
    for _ in range(n):
        with lock:
            counter.value += 1


if __name__ == "__main__":
    # Shared memory
    shared_counter = multiprocessing.Value('i', 0)
    shared_lock = multiprocessing.Lock()
    
    processes = [
        multiprocessing.Process(
            target=increment_shared,
            args=(shared_counter, shared_lock, 10000)
        )
        for _ in range(4)
    ]
    
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    
    print(f"Shared counter: {shared_counter.value} (expected: 40000)")


# ============================================
# 9. COMPARISON
# ============================================
print("\n--- 9. THREADING VS MULTIPROCESSING ---")

print("""
Threading:
  ✓ Lightweight (less memory)
  ✓ Fast to create
  ✓ Shared memory
  ✗ Limited by GIL for CPU-bound
  ✓ Good for I/O-bound tasks

Multiprocessing:
  ✓ True parallelism
  ✓ Not limited by GIL
  ✗ Higher memory usage
  ✗ Slower to create
  ✓ Good for CPU-bound tasks

AsyncIO:
  ✓ Single-threaded concurrency
  ✓ Excellent for I/O-bound
  ✓ Low overhead
  ✗ Requires async/await syntax
  ✗ Not for CPU-bound tasks

Decision tree:
  CPU-bound? → Multiprocessing
  I/O-bound + many connections? → AsyncIO
  I/O-bound + simple? → Threading
  Need shared state? → Threading with locks
""")


print("\n✅ Day 16 completed!")
