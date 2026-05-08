# Day 11: Generators & Iterators — Lazy Evaluation & Memory Efficiency

## Learning Objectives
- Understand the iterator protocol (`__iter__`, `__next__`)
- Master generator functions with `yield`
- Use generator expressions for memory-efficient pipelines
- Apply `send()`, `throw()`, `close()` for coroutine patterns
- Build real-world data processing pipelines with generators

---

## 1. Iterator Protocol (Beginner)

```python
# Every for-loop uses the iterator protocol under the hood
class CountUp:
    """Custom iterator that counts from start to end."""
    
    def __init__(self, start: int, end: int):
        self.current = start
        self.end = end
    
    def __iter__(self):
        """Return self as the iterator."""
        return self
    
    def __next__(self):
        """Return next value or raise StopIteration."""
        if self.current > self.end:
            raise StopIteration
        value = self.current
        self.current += 1
        return value

# Usage
for num in CountUp(1, 5):
    print(num)  # 1, 2, 3, 4, 5

# What for-loop actually does:
counter = CountUp(1, 3)
iterator = iter(counter)  # Calls __iter__()
print(next(iterator))     # 1 - Calls __next__()
print(next(iterator))     # 2
print(next(iterator))     # 3
# next(iterator)          # StopIteration!
```

### Generator Functions — Simpler Way

```python
def count_up(start: int, end: int):
    """Generator function - much simpler than iterator class!"""
    current = start
    while current <= end:
        yield current  # Pauses here, returns value
        current += 1   # Resumes here on next call

# Usage is identical
for num in count_up(1, 5):
    print(num)

# Memory comparison
import sys

# List: ALL values in memory at once
big_list = [x**2 for x in range(1_000_000)]
print(sys.getsizeof(big_list))  # ~8.4 MB

# Generator: ONE value at a time
big_gen = (x**2 for x in range(1_000_000))
print(sys.getsizeof(big_gen))   # ~200 bytes!
```

---

## 2. Practical Generator Patterns (Intermediate)

```python
from typing import Generator, Iterator
from pathlib import Path

# Reading large files line by line (memory-efficient)
def read_large_file(filepath: str) -> Generator[str, None, None]:
    """Process files larger than RAM."""
    with open(filepath) as f:
        for line in f:
            yield line.strip()

# Chaining generators (pipeline pattern)
def parse_csv_lines(lines: Iterator[str]) -> Generator[dict, None, None]:
    """Parse CSV lines into dicts."""
    header = next(lines).split(",")
    for line in lines:
        values = line.split(",")
        yield dict(zip(header, values))

def filter_active(records: Iterator[dict]) -> Generator[dict, None, None]:
    """Filter only active records."""
    for record in records:
        if record.get("status") == "active":
            yield record

def transform_amounts(records: Iterator[dict]) -> Generator[dict, None, None]:
    """Convert amount strings to float."""
    for record in records:
        record["amount"] = float(record.get("amount", 0))
        yield record

# Pipeline: read → parse → filter → transform (ZERO intermediate lists!)
lines = read_large_file("transactions.csv")
records = parse_csv_lines(lines)
active = filter_active(records)
transformed = transform_amounts(active)

# Only processes ONE record at a time through entire pipeline
for record in transformed:
    process(record)


# Infinite generators
def fibonacci() -> Generator[int, None, None]:
    """Infinite Fibonacci sequence."""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

# Take first N from infinite generator
from itertools import islice
first_10 = list(islice(fibonacci(), 10))
print(first_10)  # [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


# Generator with cleanup (try/finally)
def database_cursor(query: str):
    """Generator that ensures connection cleanup."""
    conn = connect_to_db()
    try:
        cursor = conn.execute(query)
        for row in cursor:
            yield row
    finally:
        conn.close()  # ALWAYS runs, even if generator abandoned
```

### `yield from` — Delegating to Sub-generators

```python
def flatten(nested_list):
    """Recursively flatten nested lists."""
    for item in nested_list:
        if isinstance(item, list):
            yield from flatten(item)  # Delegate to sub-generator
        else:
            yield item

data = [1, [2, 3, [4, 5]], [6, [7, 8]]]
print(list(flatten(data)))  # [1, 2, 3, 4, 5, 6, 7, 8]


def chain(*iterables):
    """Like itertools.chain."""
    for iterable in iterables:
        yield from iterable

result = list(chain([1, 2], [3, 4], [5, 6]))
print(result)  # [1, 2, 3, 4, 5, 6]
```

---

## 3. Advanced Generator Patterns (Advanced)

### send(), throw(), close() — Coroutine-style

```python
def running_average():
    """Generator that accepts values via send() and yields running avg."""
    total = 0
    count = 0
    average = None
    
    while True:
        value = yield average  # Receive value, yield current average
        if value is None:
            break
        total += value
        count += 1
        average = total / count

# Usage
avg = running_average()
next(avg)              # Prime the generator (advance to first yield)
print(avg.send(10))    # 10.0
print(avg.send(20))    # 15.0
print(avg.send(30))    # 20.0
avg.close()            # Cleanup


def supervised_worker():
    """Generator that handles errors via throw()."""
    while True:
        try:
            task = yield "ready"
            print(f"Processing: {task}")
            yield f"completed: {task}"
        except ValueError as e:
            yield f"error: {e}"
        except GeneratorExit:
            print("Worker shutting down")
            return

worker = supervised_worker()
next(worker)                    # "ready"
worker.send("task_1")          # "completed: task_1"
next(worker)                    # "ready"
worker.throw(ValueError, "bad input")  # "error: bad input"
worker.close()                 # "Worker shutting down"
```

### Generator-based Context Manager

```python
from contextlib import contextmanager
import time

@contextmanager
def timer(label: str):
    """Context manager using generator."""
    start = time.perf_counter()
    yield  # Code inside 'with' block runs here
    elapsed = time.perf_counter() - start
    print(f"{label}: {elapsed:.4f}s")

with timer("Processing"):
    sum(range(10_000_000))
# Output: Processing: 0.3421s


@contextmanager
def managed_resource(name: str):
    """Acquire/release pattern."""
    print(f"Acquiring {name}")
    resource = {"name": name, "active": True}
    try:
        yield resource
    except Exception as e:
        print(f"Error in {name}: {e}")
        raise
    finally:
        resource["active"] = False
        print(f"Released {name}")
```

### Real-World: Batched Processing Pipeline

```python
from typing import TypeVar, Iterator
T = TypeVar('T')

def batched(iterable: Iterator[T], batch_size: int) -> Generator[list[T], None, None]:
    """Yield items in batches (memory-efficient)."""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch

def process_large_dataset(filepath: str, batch_size: int = 1000):
    """Process millions of records in constant memory."""
    lines = read_large_file(filepath)
    records = parse_csv_lines(lines)
    
    for batch in batched(records, batch_size):
        # Process 1000 records at a time
        results = transform_batch(batch)
        save_to_database(results)
        print(f"Processed batch of {len(batch)} records")

# Entire file processed in ~1000-record chunks regardless of file size!
```

---

## Interview Questions

### Beginner
1. **What's the difference between a generator and a list?** A list stores ALL elements in memory simultaneously. A generator produces elements one-at-a-time on demand (lazy evaluation). Generator uses `yield` instead of `return`, maintaining state between calls. You can only iterate a generator once. Use generators for: large datasets, infinite sequences, memory-constrained processing.

2. **What does `yield` do?** `yield` pauses the function and returns a value. On next call (via `next()` or for-loop), execution resumes from where it paused. The function's local state (variables, position) is preserved between yields. A function with `yield` becomes a generator function — calling it returns a generator object without executing the body.

3. **What's a generator expression vs list comprehension?** `[x**2 for x in range(n)]` creates a list (all values, O(n) memory). `(x**2 for x in range(n))` creates a generator (lazy, O(1) memory). Use list when: you need random access, will iterate multiple times. Use generator when: processing sequentially once, large/infinite sequences.

### Intermediate
4. **Explain `yield from` and when to use it.** `yield from iterable` delegates to a sub-generator, yielding each value from it. Equivalent to `for item in iterable: yield item` but also propagates `send()` and `throw()` to the sub-generator. Use for: flattening nested generators, composing generator pipelines, recursive generators (tree traversal).

5. **How do you build a data processing pipeline with generators?** Chain generators: each takes an iterator and yields transformed items. `read() → parse() → filter() → transform() → write()`. Benefits: constant memory regardless of input size, each record flows through entire pipeline before next starts, easy to add/remove stages. This is the "Unix pipe" pattern in Python.

6. **What happens when you call `close()` on a generator?** `close()` throws `GeneratorExit` at the point where the generator is paused. If the generator catches it and yields again, `RuntimeError` is raised. Use `try/finally` in generators for cleanup (closing files, connections). Garbage collection calls `close()` automatically when generator is collected.

### Advanced
7. **Explain `send()` and how generators can be used as coroutines.** `send(value)` resumes the generator AND passes a value that becomes the result of the `yield` expression. This enables two-way communication: generator yields data out, caller sends data in. Pattern: `value = yield result`. Use for: running averages, state machines, cooperative multitasking (pre-asyncio pattern).

8. **How does `@contextmanager` use generators internally?** The decorator wraps a generator function that yields exactly once. Code before `yield` runs on `__enter__`, code after `yield` runs on `__exit__`. The yielded value becomes the `as` target. `try/finally` ensures cleanup even on exceptions. It's simpler than writing a full class with `__enter__`/`__exit__`.

9. **Compare generators to async generators. When use which?** Sync generators (`yield`): CPU-bound lazy sequences, file processing, data pipelines. Async generators (`async def` + `yield`): I/O-bound lazy sequences (streaming from network, async DB cursors). Async generators work with `async for`. Use async when the production of each item involves awaiting I/O.

---

## Hands-On Exercise
1. Implement `range()` as a generator function with start, stop, step
2. Build a log file processor: read → parse → filter by level → aggregate
3. Create an infinite prime number generator using the Sieve approach
4. Implement `batched()` and use it to process a 1GB CSV in constant memory
5. Build a coroutine-based state machine using `send()`
