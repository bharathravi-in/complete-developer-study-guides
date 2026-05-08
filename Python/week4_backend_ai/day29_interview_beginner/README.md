# Day 29: Python Interview Questions — Beginner & Intermediate

## Learning Objectives
- Master the 30 most-asked Python interview questions
- Practice explaining concepts clearly and concisely
- Solve common coding challenges with optimal solutions
- Handle follow-up questions confidently

---

## 1. Python Fundamentals (Beginner)

**Q1: What are Python's key features?**
Interpreted, dynamically typed, garbage collected, supports multiple paradigms (OOP, functional, procedural). Indentation-based syntax. Rich standard library. "Batteries included." Extensive third-party ecosystem (PyPI).

**Q2: What's the difference between a list and a tuple?**
```python
# List: mutable, slightly more memory, slower
my_list = [1, 2, 3]
my_list[0] = 10  # OK

# Tuple: immutable, less memory, faster, hashable (can be dict key)
my_tuple = (1, 2, 3)
# my_tuple[0] = 10  # TypeError!

# When to use tuple: fixed data (coordinates, RGB), dict keys, function returns
# When to use list: dynamic collections, need to modify
```

**Q3: Explain `*args` and `**kwargs`.**
```python
def flexible(*args, **kwargs):
    """
    *args: collects positional arguments into a tuple
    **kwargs: collects keyword arguments into a dict
    """
    print(args)    # (1, 2, 3)
    print(kwargs)  # {'name': 'Alice', 'age': 30}

flexible(1, 2, 3, name="Alice", age=30)

# Unpacking
def add(a, b, c):
    return a + b + c

numbers = [1, 2, 3]
print(add(*numbers))  # 6 — unpacks list into positional args
```

**Q4: What is a dictionary comprehension?**
```python
# Create dict from transformation
squares = {x: x**2 for x in range(6)}
# {0: 0, 1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

# Filter and transform
words = ["hello", "world", "python"]
lengths = {w: len(w) for w in words if len(w) > 4}
# {'hello': 5, 'world': 5, 'python': 6}
```

**Q5: Explain the difference between `==` and `is`.**
```python
a = [1, 2, 3]
b = [1, 2, 3]
c = a

print(a == b)  # True (same value)
print(a is b)  # False (different objects in memory)
print(a is c)  # True (same object)

# Use 'is' ONLY for: None checks, singleton comparisons
if x is None:
    pass
```

---

## 2. Data Structures & Functions (Intermediate)

**Q6: How does a Python dictionary work internally?**
Hash table. Key → hash → index → bucket. Collision resolution via open addressing (probing). Average O(1) lookup. Load factor < 2/3 triggers resize. Python 3.7+: preserves insertion order. Keys must be hashable (immutable: str, int, tuple).

**Q7: What are decorators? Write one.**
```python
import functools
import time

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__}: {time.perf_counter() - start:.4f}s")
        return result
    return wrapper

@timer
def slow_function():
    time.sleep(1)
    return "done"

slow_function()  # slow_function: 1.0012s
```

**Q8: Explain generators and when to use them.**
```python
def fibonacci(limit):
    a, b = 0, 1
    while a < limit:
        yield a  # Pauses, returns value, resumes on next()
        a, b = b, a + b

# Memory-efficient: generates one value at a time
for num in fibonacci(100):
    print(num)

# Use when: large datasets, lazy evaluation, infinite sequences
# Generator expression: (x**2 for x in range(1000000))  # O(1) memory
```

**Q9: What is the GIL?**
Global Interpreter Lock — mutex that allows only one thread to execute Python bytecode at a time. Exists because CPython's memory management (reference counting) isn't thread-safe. Impact: multithreading doesn't speed up CPU-bound code. Solution: use `multiprocessing` for CPU work; threading works fine for I/O-bound tasks (GIL released during I/O).

**Q10: Explain shallow copy vs deep copy.**
```python
import copy

original = [[1, 2], [3, 4]]

shallow = copy.copy(original)     # or original[:]
deep = copy.deepcopy(original)

original[0][0] = 99
print(shallow[0][0])  # 99 — shared inner objects!
print(deep[0][0])     # 1  — fully independent copy

# Shallow: new outer container, same inner objects
# Deep: recursively copies everything (slower, more memory)
```

---

## 3. OOP & Advanced (Intermediate-Advanced)

**Q11: Explain `@classmethod`, `@staticmethod`, `@property`.**
```python
class Circle:
    pi = 3.14159
    
    def __init__(self, radius):
        self._radius = radius
    
    @property
    def radius(self):
        return self._radius
    
    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value
    
    @classmethod
    def from_diameter(cls, diameter):
        """Alternative constructor using class."""
        return cls(diameter / 2)
    
    @staticmethod
    def is_valid_radius(value):
        """Utility — no access to class or instance."""
        return isinstance(value, (int, float)) and value >= 0
```

**Q12: What is multiple inheritance and MRO?**
```python
class A:
    def method(self): print("A")

class B(A):
    def method(self): print("B")

class C(A):
    def method(self): print("C")

class D(B, C):
    pass

d = D()
d.method()  # "B" — follows MRO
print(D.__mro__)  # D → B → C → A → object (C3 Linearization)
# super() follows MRO, not parent!
```

**Q13: How does exception handling work?**
```python
def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        return None
    except TypeError as e:
        raise ValueError(f"Invalid types: {e}") from e
    else:
        # Runs only if NO exception
        print(f"Success: {result}")
    finally:
        # ALWAYS runs (cleanup)
        print("Cleaning up")
    return result

# Custom exception
class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"{field}: {message}")
```

**Q14: What are context managers?**
```python
# Ensure resource cleanup (files, locks, connections)
class DatabaseConnection:
    def __enter__(self):
        self.conn = connect()
        return self.conn
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
        return False  # Don't suppress exceptions

# Simpler with contextlib
from contextlib import contextmanager

@contextmanager
def timer(label):
    start = time.time()
    yield
    print(f"{label}: {time.time() - start:.2f}s")
```

**Q15: Explain `async/await`.**
```python
import asyncio

async def fetch(url):
    # Non-blocking I/O
    await asyncio.sleep(1)  # Simulates network request
    return f"Data from {url}"

async def main():
    # Concurrent execution (NOT parallel — single thread)
    results = await asyncio.gather(
        fetch("url1"),
        fetch("url2"),
        fetch("url3"),
    )  # Takes ~1s, not ~3s

asyncio.run(main())
# Use for: I/O-bound concurrency (web requests, DB queries)
# NOT for: CPU-bound work (use multiprocessing instead)
```

---

## 4. Common Coding Problems

```python
# 1. Reverse a string
def reverse_string(s: str) -> str:
    return s[::-1]

# 2. Check palindrome
def is_palindrome(s: str) -> bool:
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]

# 3. FizzBuzz
def fizzbuzz(n: int) -> list[str]:
    return [
        "FizzBuzz" if i % 15 == 0
        else "Fizz" if i % 3 == 0
        else "Buzz" if i % 5 == 0
        else str(i)
        for i in range(1, n + 1)
    ]

# 4. Two Sum
def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

# 5. Find duplicates
def find_duplicates(lst: list) -> list:
    from collections import Counter
    return [item for item, count in Counter(lst).items() if count > 1]

# 6. Flatten nested list
def flatten(nested: list) -> list:
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

# 7. Anagram check
def is_anagram(s1: str, s2: str) -> bool:
    from collections import Counter
    return Counter(s1.lower()) == Counter(s2.lower())

# 8. Remove duplicates preserving order
def remove_duplicates(lst: list) -> list:
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]
```

---

## Interview Questions

### Beginner
1. **What happens when you do `a = b = []`?** Both `a` and `b` reference the SAME list object. `a.append(1)` means `b` is also `[1]`. To create independent lists: `a, b = [], []` or `a = []; b = a.copy()`. This is a reference aliasing issue — Python variables are names pointing to objects, not containers.

2. **How is memory managed in Python?** Reference counting (immediate cleanup when count=0) + garbage collector (handles circular references). Objects < 512 bytes use pymalloc (arena-based). Small integers (-5 to 256) and short strings are cached (interned). No manual malloc/free needed.

3. **What's a lambda function?** Anonymous, single-expression function: `square = lambda x: x**2`. Limited to one expression (no statements, no assignments). Use for: short callbacks, key functions (`sorted(items, key=lambda x: x.age)`). For anything complex, use a regular `def` function.

### Intermediate
4. **Explain list vs generator performance tradeoffs.** List: random access O(1), can iterate multiple times, stores all elements (O(n) memory). Generator: sequential access only, single iteration, O(1) memory. List wins for: small data, repeated access. Generator wins for: large/infinite data, pipeline processing, memory-constrained environments.

5. **What are `__slots__` and when would you use them?** `__slots__` replaces instance `__dict__` with fixed-size struct. Saves ~35% memory, faster attribute access. Trade-off: can't add new attributes dynamically. Use when: millions of instances (data points, nodes), memory-critical applications. Don't use when: few instances or need dynamic attributes.

6. **How do you handle circular imports?** Solutions: (1) Import inside function (lazy import), (2) Restructure code (extract shared code to third module), (3) Use `TYPE_CHECKING` block for type hints only. Prevention: design clear module hierarchy, avoid bidirectional dependencies, keep modules focused.

### Advanced
7. **Explain Python's descriptor protocol and how `property` uses it.** Descriptors define `__get__`, `__set__`, `__delete__`. Data descriptors (with `__set__`) override instance `__dict__`. `property` is a data descriptor that calls getter/setter functions on attribute access. Lookup order: data descriptor → instance dict → non-data descriptor → class dict.

8. **Design a connection pool in Python.** Use `queue.Queue(maxsize=N)` for thread-safety. `acquire()`: get from queue (blocks if empty). `release()`: put back. Context manager for auto-release. Health checks: validate before returning. Growth: create new if below max and queue empty. Shrink: close idle connections after timeout.

9. **What's the difference between concurrency and parallelism in Python?** Concurrency: managing multiple tasks (interleaving on one core) — asyncio, threading. Parallelism: executing multiple tasks simultaneously (multiple cores) — multiprocessing. Python's GIL limits parallelism for CPU-bound threads. Achieve both: `ProcessPoolExecutor` for CPU work, `asyncio` for I/O concurrency.

---

## Hands-On Exercise
1. Solve all 8 coding problems above without looking at solutions
2. Explain each concept in 2 minutes (practice verbal communication)
3. Write tests for each coding problem with edge cases
4. Time yourself: solve Two Sum, Valid Parentheses, and Merge Intervals in 15 min each
5. Mock interview: have someone pick 5 random questions from this file
