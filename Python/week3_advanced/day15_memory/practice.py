#!/usr/bin/env python3
"""Day 15 - Python Memory Model Deep Dive"""

import sys
import gc
import weakref
import ctypes
from typing import Any

print("=" * 50)
print("PYTHON MEMORY MODEL")
print("=" * 50)

# ============================================
# 1. OBJECT IDENTITY AND REFERENCE
# ============================================
print("\n--- 1. OBJECT IDENTITY ---")

a = [1, 2, 3]
b = a  # Reference, not copy
c = [1, 2, 3]  # New object

print(f"a = {a}, id = {id(a)}")
print(f"b = {b}, id = {id(b)}")
print(f"c = {c}, id = {id(c)}")

print(f"\na is b: {a is b}")  # True - same object
print(f"a is c: {a is c}")  # False - different objects
print(f"a == c: {a == c}")  # True - same value


# ============================================
# 2. REFERENCE COUNTING
# ============================================
print("\n--- 2. REFERENCE COUNTING ---")


def get_ref_count(obj_id: int) -> int:
    """Get reference count of object by id"""
    return ctypes.c_long.from_address(obj_id).value


x = [1, 2, 3]
x_id = id(x)

print(f"Initial ref count: {sys.getrefcount(x)}")  # +1 for function arg
print(f"Actual ref count: {get_ref_count(x_id)}")

y = x  # Add reference
print(f"After y = x: {get_ref_count(x_id)}")

z = x  # Add another
print(f"After z = x: {get_ref_count(x_id)}")

del y  # Remove reference
print(f"After del y: {get_ref_count(x_id)}")

del z
print(f"After del z: {get_ref_count(x_id)}")


# ============================================
# 3. SMALL INTEGER CACHING
# ============================================
print("\n--- 3. INTEGER CACHING ---")

# Python caches small integers (-5 to 256)
a = 256
b = 256
print(f"256 is 256: {a is b}")  # True

a = 257
b = 257
print(f"257 is 257: {a is b}")  # Usually False (different objects)

# String interning
s1 = "hello"
s2 = "hello"
print(f"'hello' is 'hello': {s1 is s2}")  # True (interned)

s1 = "hello world!"
s2 = "hello world!"
print(f"'hello world!' is 'hello world!': {s1 is s2}")  # May vary


# ============================================
# 4. GARBAGE COLLECTION
# ============================================
print("\n--- 4. GARBAGE COLLECTION ---")

print(f"GC enabled: {gc.isenabled()}")
print(f"GC thresholds: {gc.get_threshold()}")
print(f"GC counts: {gc.get_count()}")

# Circular reference example
class Node:
    def __init__(self, name):
        self.name = name
        self.ref = None
    def __del__(self):
        print(f"  __del__ called for {self.name}")


print("\nCreating circular reference:")
a = Node("A")
b = Node("B")
a.ref = b
b.ref = a  # Circular reference

del a
del b

print("After del, objects still exist due to circular ref")
print(f"Collecting garbage...")
collected = gc.collect()
print(f"Collected {collected} objects")


# ============================================
# 5. WEAK REFERENCES
# ============================================
print("\n--- 5. WEAK REFERENCES ---")

class MyObject:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"MyObject({self.name})"


obj = MyObject("test")
weak_ref = weakref.ref(obj)

print(f"Object: {obj}")
print(f"Weak ref: {weak_ref}")
print(f"Weak ref(): {weak_ref()}")

del obj
print(f"After del obj, weak_ref(): {weak_ref()}")  # None

# WeakValueDictionary
cache = weakref.WeakValueDictionary()
obj = MyObject("cached")
cache["key"] = obj

print(f"\nCache: {dict(cache)}")
del obj
gc.collect()
print(f"After del: {dict(cache)}")  # Empty


# ============================================
# 6. MEMORY SIZE OF OBJECTS
# ============================================
print("\n--- 6. OBJECT SIZES ---")

objects = [
    ("int 0", 0),
    ("int 1", 1),
    ("float", 1.0),
    ("str ''", ""),
    ("str 'a'", "a"),
    ("str 'hello'", "hello"),
    ("list []", []),
    ("list [1,2,3]", [1, 2, 3]),
    ("dict {}", {}),
    ("dict {1:1}", {1: 1}),
    ("set()", set()),
    ("tuple ()", ()),
    ("None", None),
    ("class instance", type("C", (), {})()),
]

print(f"{'Object':<20} {'Size (bytes)':>12}")
print("-" * 35)
for name, obj in objects:
    size = sys.getsizeof(obj)
    print(f"{name:<20} {size:>12}")


# ============================================
# 7. MEMORY PROFILING
# ============================================
print("\n--- 7. MEMORY PROFILING ---")

print("""
Memory profiling tools:

1. sys.getsizeof() - Size of single object
2. tracemalloc - Track memory allocations
3. memory_profiler - Line-by-line memory usage
4. objgraph - Object reference graphs

Example with tracemalloc:
""")

import tracemalloc

tracemalloc.start()

# Allocate memory
data = [i ** 2 for i in range(10000)]

current, peak = tracemalloc.get_traced_memory()
print(f"Current memory: {current / 1024:.2f} KB")
print(f"Peak memory: {peak / 1024:.2f} KB")

tracemalloc.stop()
del data


# ============================================
# 8. THE GIL (GLOBAL INTERPRETER LOCK)
# ============================================
print("\n--- 8. THE GIL ---")

print("""
What is the GIL?
- Mutex that protects access to Python objects
- Only one thread executes Python bytecode at a time
- Part of CPython implementation

Why does it exist?
- Simplifies memory management (reference counting)
- Makes C extensions easier to write
- Prevents race conditions in interpreter

Impact:
- CPU-bound tasks: Limited parallelism (use multiprocessing)
- I/O-bound tasks: Threads still useful (GIL released during I/O)

Workarounds:
1. Use multiprocessing for CPU-bound work
2. Use asyncio for I/O-bound work
3. Use C extensions that release GIL (numpy, etc.)
4. Use alternative interpreters (PyPy, Jython)
""")

# Demonstrate GIL impact
import threading
import time

def cpu_bound(n: int) -> int:
    """CPU-bound task"""
    count = 0
    for i in range(n):
        count += i
    return count


def benchmark_sequential():
    start = time.perf_counter()
    cpu_bound(10_000_000)
    cpu_bound(10_000_000)
    return time.perf_counter() - start


def benchmark_threaded():
    start = time.perf_counter()
    t1 = threading.Thread(target=cpu_bound, args=(10_000_000,))
    t2 = threading.Thread(target=cpu_bound, args=(10_000_000,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    return time.perf_counter() - start


seq_time = benchmark_sequential()
thread_time = benchmark_threaded()

print(f"Sequential: {seq_time:.2f}s")
print(f"Threaded: {thread_time:.2f}s")
print(f"Speedup: {seq_time/thread_time:.2f}x (should be ~1 due to GIL)")


# ============================================
# 9. MEMORY LEAKS
# ============================================
print("\n--- 9. COMMON MEMORY LEAKS ---")

print("""
Common causes of memory leaks:

1. Circular References (handled by GC, but slower)
2. Global variables accumulating data
3. Caches without eviction
4. Closures capturing large objects
5. __del__ preventing garbage collection
6. C extensions not releasing memory

Best practices:
- Use weak references for caches
- Clear large objects when done
- Use context managers
- Profile memory usage regularly
- Be careful with global state
""")


print("\n✅ Day 15 completed!")
