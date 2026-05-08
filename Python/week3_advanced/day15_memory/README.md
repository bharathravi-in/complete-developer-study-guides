# Day 15: Python Memory Model — GC, GIL & Optimization

## Learning Objectives
- Understand Python's memory allocation (stack vs heap)
- Master reference counting and garbage collection cycles
- Explain the GIL and its implications for performance
- Profile and optimize memory usage in real applications
- Detect and fix memory leaks

---

## 1. Memory Allocation & Reference Counting (Beginner)

```python
import sys

# Everything in Python is an object on the heap
x = 42
print(sys.getrefcount(x))  # Reference count (usually high for small ints — cached!)

# Reference counting in action
a = [1, 2, 3]            # refcount = 1
b = a                    # refcount = 2 (b references same object)
c = [a, a]              # refcount = 4 (c has 2 refs to a)
print(sys.getrefcount(a))  # 5 (includes the getrefcount arg)

del b                    # refcount decreases
print(sys.getrefcount(a))  # 4

# When refcount → 0, memory is freed immediately
del a, c  # Object [1,2,3] is freed (if no other refs)

# id() shows memory address
x = "hello"
y = "hello"
print(id(x) == id(y))  # True! String interning (small strings reused)

# Small integer cache (-5 to 256)
a = 100
b = 100
print(a is b)  # True (same object — cached)

a = 1000
b = 1000
print(a is b)  # False (different objects — not cached)
```

### Memory Layout

```python
import sys

# Object sizes
print(sys.getsizeof(0))          # 28 bytes (int)
print(sys.getsizeof(""))         # 49 bytes (empty string)
print(sys.getsizeof([]))         # 56 bytes (empty list)
print(sys.getsizeof({}))         # 64 bytes (empty dict)
print(sys.getsizeof(object()))   # 16 bytes

# Lists over-allocate for amortized O(1) append
lst = []
for i in range(10):
    print(f"len={len(lst)}, size={sys.getsizeof(lst)} bytes")
    lst.append(i)
# Size grows in chunks: 56, 88, 88, 88, 88, 120, 120, 120, 120, 184...
```

---

## 2. Garbage Collection & Circular References (Intermediate)

```python
import gc
import weakref

# Circular reference — refcount NEVER reaches 0!
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
    def __del__(self):
        print(f"Node({self.value}) deleted")

# Create circular reference
a = Node(1)
b = Node(2)
a.next = b
b.next = a  # Circular!

del a, b
# Refcounts are still > 0! Only GC can clean this.
gc.collect()  # Forces garbage collection — "Node(1) deleted", "Node(2) deleted"


# Weak references — don't prevent garbage collection
class Cache:
    """Cache that doesn't prevent objects from being collected."""
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()
    
    def get(self, key):
        return self._cache.get(key)
    
    def set(self, key, value):
        self._cache[key] = value

cache = Cache()
obj = Node(42)
cache.set("key", obj)
print(cache.get("key"))  # Node(42)
del obj
gc.collect()
print(cache.get("key"))  # None (object was collected!)


# GC statistics and tuning
print(gc.get_stats())       # Collection stats per generation
print(gc.get_threshold())   # (700, 10, 10) — when collections trigger
gc.set_threshold(1000, 15, 15)  # Less frequent collection (more memory, less CPU)

# Disable GC for performance-critical sections
gc.disable()
# ... allocate many objects ...
gc.enable()
gc.collect()
```

### Memory Profiling

```python
# pip install memory-profiler
from memory_profiler import profile

@profile
def memory_intensive():
    """Profiler shows line-by-line memory usage."""
    data = [i ** 2 for i in range(1_000_000)]  # +7.6 MiB
    filtered = [x for x in data if x % 2 == 0]  # +3.8 MiB
    del data                                      # -7.6 MiB
    return filtered

# Run: python -m memory_profiler script.py

# tracemalloc — built-in memory tracing
import tracemalloc

tracemalloc.start()

# ... your code ...
data = {i: str(i) * 100 for i in range(100_000)}

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
for stat in top_stats[:5]:
    print(stat)
```

---

## 3. GIL & Performance Implications (Advanced)

```python
import threading
import multiprocessing
import time

# GIL: Only ONE thread runs Python bytecode at a time
# Impact: CPU-bound multithreading gives NO speedup

def cpu_bound(n):
    """CPU-intensive work."""
    total = 0
    for i in range(n):
        total += i * i
    return total

# Single-threaded
start = time.perf_counter()
cpu_bound(10_000_000)
cpu_bound(10_000_000)
print(f"Sequential: {time.perf_counter() - start:.2f}s")

# Multi-threaded (NO speedup due to GIL!)
start = time.perf_counter()
t1 = threading.Thread(target=cpu_bound, args=(10_000_000,))
t2 = threading.Thread(target=cpu_bound, args=(10_000_000,))
t1.start(); t2.start()
t1.join(); t2.join()
print(f"Threaded: {time.perf_counter() - start:.2f}s")  # Same or slower!

# Multi-process (BYPASSES GIL — true parallelism!)
start = time.perf_counter()
with multiprocessing.Pool(2) as pool:
    pool.map(cpu_bound, [10_000_000, 10_000_000])
print(f"Multiprocess: {time.perf_counter() - start:.2f}s")  # ~2x faster!


# GIL is RELEASED during I/O — threading works for I/O-bound!
import requests

def fetch_url(url):
    """I/O-bound — GIL released during network wait."""
    return requests.get(url).status_code

urls = ["https://httpbin.org/delay/1"] * 5

# Sequential: ~5 seconds
# Threaded: ~1 second (GIL released during I/O wait)
```

### Memory Optimization Techniques

```python
import sys
from dataclasses import dataclass

# 1. __slots__ — 35-40% memory reduction
class PointDict:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointSlots:
    __slots__ = ('x', 'y')
    def __init__(self, x, y):
        self.x = x
        self.y = y

# 2. Generators instead of lists
sum(x**2 for x in range(1_000_000))  # O(1) memory
# vs
sum([x**2 for x in range(1_000_000)])  # O(n) memory

# 3. array module for homogeneous numeric data
from array import array
int_array = array('i', range(1_000_000))  # ~4 MB
int_list = list(range(1_000_000))          # ~8 MB

# 4. numpy for numeric computation
import numpy as np
np_arr = np.arange(1_000_000, dtype=np.int32)  # ~4 MB, vectorized

# 5. intern strings that repeat often
import sys
s = sys.intern("frequently_used_string")

# 6. Use tuples instead of lists for immutable data
point_tuple = (3.14, 2.71)   # 56 bytes
point_list = [3.14, 2.71]    # 88 bytes
```

---

## Interview Questions

### Beginner
1. **How does Python manage memory?** Python uses: (1) Reference counting — each object tracks how many references point to it; when count=0, memory freed immediately. (2) Generational garbage collector — handles circular references that refcounting can't detect. (3) Memory pools (pymalloc) — pre-allocates memory for small objects (<512 bytes) to reduce system calls. All managed automatically.

2. **What is the GIL and why does it exist?** The Global Interpreter Lock is a mutex that allows only one thread to execute Python bytecode at a time. It exists because: CPython's memory management (reference counting) is not thread-safe. Without GIL, every refcount operation would need its own lock (huge overhead). Trade-off: simplifies C extensions, but limits CPU parallelism.

3. **What's the difference between `is` and `==`?** `==` compares values (calls `__eq__`). `is` compares identity (same object in memory, same `id()`). Use `is` only for: `None` checks (`x is None`), singleton comparisons. Gotcha: `a = 256; b = 256; a is b` → True (integer cache), but `a = 257; b = 257; a is b` → False (different objects).

### Intermediate
4. **What causes memory leaks in Python?** (1) Circular references with `__del__` methods (GC can't collect). (2) Growing caches without bounds. (3) Global variables holding references. (4) Closures capturing large objects. (5) C extension bugs. (6) Unclosed file handles/connections. Detection: `tracemalloc`, `objgraph`, `memory_profiler`. Fix: weak references, bounded caches, explicit cleanup.

5. **When would you use `multiprocessing` vs `threading`?** Threading: I/O-bound work (network, file, database) — GIL is released during I/O waits, so threads give real concurrency. Multiprocessing: CPU-bound work (computation, data processing) — bypasses GIL with separate processes. Trade-offs: multiprocessing has higher overhead (memory per process, IPC cost) but true parallelism.

6. **How does Python's garbage collector work with generations?** Three generations (0, 1, 2): new objects start in gen-0. If they survive a collection cycle, they're promoted to gen-1, then gen-2. Higher generations collected less frequently (most objects die young). Triggered by: allocation count exceeds threshold. This generational hypothesis makes GC efficient for typical allocation patterns.

### Advanced
7. **How would you debug a memory leak in production?** (1) `tracemalloc.start()` — take snapshots, compare over time. (2) `gc.get_objects()` — count objects by type. (3) `objgraph.show_most_common_types()` — find growing types. (4) `weakref.ref()` — check if objects are collected. (5) Compare heap snapshots between requests. (6) Check for caches, globals, and event listeners that accumulate.

8. **Explain Python's memory allocator hierarchy.** Layer 0: OS (`malloc`/`mmap`). Layer 1: Raw memory allocator (wraps OS calls). Layer 2: Object allocator (pymalloc) — arena-based for small objects (<512 bytes), 256KB arenas → 4KB pools → 8-byte aligned blocks. Layer 3: Object-specific allocators (int free list, float free list). This hierarchy reduces system call overhead for frequent small allocations.

9. **Will Python 3.13+'s free-threaded mode (no-GIL) change everything?** PEP 703 introduces optional GIL-free builds. Impact: true multi-threaded parallelism for CPU-bound code. Challenges: C extensions need updates, reference counting becomes atomic (slower single-threaded), memory ordering complexity. Initially opt-in, separate build. Won't eliminate multiprocessing need (still want process isolation for stability).

---

## Hands-On Exercise
1. Create circular references and verify GC collects them with `gc.collect()`
2. Profile a script with `tracemalloc` and identify the top memory consumers
3. Compare threading vs multiprocessing for CPU-bound and I/O-bound tasks
4. Optimize a data-heavy class using `__slots__` and measure memory savings
5. Build a bounded LRU cache using `weakref.WeakValueDictionary`
