# Day 20: Pythonic Coding — functools, itertools & collections

## Learning Objectives
- Write idiomatic Python using standard library power tools
- Master `functools` (lru_cache, partial, reduce, singledispatch)
- Chain operations with `itertools` (combinations, groupby, islice)
- Use `collections` for specialized containers (Counter, defaultdict, deque)
- Apply functional programming patterns in Python

---

## 1. collections Module (Beginner)

```python
from collections import Counter, defaultdict, namedtuple, deque, OrderedDict

# Counter — count elements effortlessly
words = "the cat sat on the mat the cat".split()
word_counts = Counter(words)
print(word_counts.most_common(3))  # [('the', 3), ('cat', 2), ('sat', 1)]

# Counter arithmetic
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)
print(c1 + c2)  # Counter({'a': 4, 'b': 3})
print(c1 - c2)  # Counter({'a': 2})  (drops zero/negative)


# defaultdict — never get KeyError
# Group items by category
products = [("fruit", "apple"), ("veggie", "carrot"), ("fruit", "banana"), ("veggie", "pea")]
grouped = defaultdict(list)
for category, item in products:
    grouped[category].append(item)
# {'fruit': ['apple', 'banana'], 'veggie': ['carrot', 'pea']}

# Count with defaultdict
char_count = defaultdict(int)
for char in "mississippi":
    char_count[char] += 1


# deque — O(1) operations on both ends
dq = deque(maxlen=5)  # Bounded deque (auto-evicts oldest)
for i in range(10):
    dq.append(i)
print(dq)  # deque([5, 6, 7, 8, 9], maxlen=5)

dq.appendleft(0)   # O(1) prepend
dq.rotate(2)        # Rotate right by 2


# namedtuple — lightweight immutable objects
Point = namedtuple('Point', ['x', 'y'])
p = Point(3, 4)
print(p.x, p.y)     # Attribute access
x, y = p            # Unpacking works
print(p._asdict())   # {'x': 3, 'y': 4}
```

---

## 2. functools Module (Intermediate)

```python
from functools import lru_cache, partial, reduce, singledispatch, wraps, cached_property

# lru_cache — automatic memoization
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    """O(n) with cache vs O(2^n) without."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

fibonacci(100)  # Instant! Without cache: would take forever
print(fibonacci.cache_info())  # CacheInfo(hits=98, misses=101, ...)
fibonacci.cache_clear()  # Reset cache


# partial — fix some arguments
def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)
print(square(5))  # 25
print(cube(3))    # 27

# Useful for callbacks
from functools import partial
import logging
debug_log = partial(logging.log, logging.DEBUG)
error_log = partial(logging.log, logging.ERROR)


# reduce — accumulate values
from functools import reduce
from operator import mul

# Product of all numbers
numbers = [1, 2, 3, 4, 5]
product = reduce(mul, numbers)  # 120
# Equivalent: reduce(lambda acc, x: acc * x, numbers)

# Flatten nested lists
nested = [[1, 2], [3, 4], [5, 6]]
flat = reduce(lambda acc, lst: acc + lst, nested)  # [1, 2, 3, 4, 5, 6]


# singledispatch — function overloading by type
@singledispatch
def process(data):
    raise NotImplementedError(f"Cannot process {type(data)}")

@process.register(str)
def _(data: str):
    return data.upper()

@process.register(list)
def _(data: list):
    return [process(item) for item in data]

@process.register(int)
def _(data: int):
    return data * 2

print(process("hello"))   # "HELLO"
print(process(42))        # 84
print(process([1, "a"]))  # [2, "A"]


# cached_property — compute once, cache on instance
class DataAnalyzer:
    def __init__(self, data: list):
        self.data = data
    
    @cached_property
    def statistics(self) -> dict:
        """Expensive computation, cached after first access."""
        return {
            "mean": sum(self.data) / len(self.data),
            "max": max(self.data),
            "min": min(self.data),
        }
```

---

## 3. itertools Module (Advanced)

```python
import itertools
from itertools import (
    chain, islice, groupby, combinations, permutations,
    product, starmap, compress, accumulate, takewhile, dropwhile
)

# chain — flatten iterables
all_items = list(chain([1, 2], [3, 4], [5, 6]))  # [1, 2, 3, 4, 5, 6]
# chain.from_iterable for nested
nested = [[1, 2], [3, 4], [5]]
flat = list(chain.from_iterable(nested))  # [1, 2, 3, 4, 5]


# islice — slice any iterator (lazy)
from itertools import count
first_10_evens = list(islice((x for x in count() if x % 2 == 0), 10))
# [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]


# groupby — group consecutive elements (MUST be sorted by key first!)
data = [
    {"name": "Alice", "dept": "Engineering"},
    {"name": "Bob", "dept": "Engineering"},
    {"name": "Charlie", "dept": "Marketing"},
    {"name": "Diana", "dept": "Marketing"},
]
data.sort(key=lambda x: x["dept"])  # MUST sort first!
for dept, members in groupby(data, key=lambda x: x["dept"]):
    print(f"{dept}: {[m['name'] for m in members]}")
# Engineering: ['Alice', 'Bob']
# Marketing: ['Charlie', 'Diana']


# combinations & permutations
letters = "ABC"
print(list(combinations(letters, 2)))   # [('A','B'), ('A','C'), ('B','C')]
print(list(permutations(letters, 2)))   # [('A','B'), ('A','C'), ('B','A'), ('B','C'), ...]

# product — cartesian product
colors = ["red", "blue"]
sizes = ["S", "M", "L"]
variants = list(product(colors, sizes))
# [('red','S'), ('red','M'), ('red','L'), ('blue','S'), ...]


# accumulate — running totals
nums = [1, 2, 3, 4, 5]
running_sum = list(accumulate(nums))          # [1, 3, 6, 10, 15]
running_max = list(accumulate(nums, max))     # [1, 2, 3, 4, 5]
running_product = list(accumulate(nums, mul)) # [1, 2, 6, 24, 120]


# takewhile / dropwhile
sorted_nums = [2, 4, 6, 8, 1, 3, 5]
before_odd = list(takewhile(lambda x: x % 2 == 0, sorted_nums))  # [2, 4, 6, 8]
after_odd = list(dropwhile(lambda x: x % 2 == 0, sorted_nums))   # [1, 3, 5]


# Real-world: batch processing
def batched(iterable, n):
    """Batch items from an iterable (Python 3.12 has itertools.batched)."""
    it = iter(iterable)
    while True:
        batch = list(islice(it, n))
        if not batch:
            break
        yield batch

for batch in batched(range(100), 10):
    process_batch(batch)
```

### Pythonic Patterns

```python
# Comprehensions over map/filter
# Instead of: list(map(lambda x: x**2, filter(lambda x: x > 0, nums)))
# Write:
result = [x**2 for x in nums if x > 0]

# Dictionary comprehension
word_lengths = {word: len(word) for word in words}

# Set comprehension
unique_lengths = {len(word) for word in words}

# Walrus operator (:=) — assign in expression
# Instead of:
#   line = f.readline()
#   while line:
#       process(line)
#       line = f.readline()
# Write:
while (line := f.readline()):
    process(line)

# Unpacking
first, *middle, last = [1, 2, 3, 4, 5]  # first=1, middle=[2,3,4], last=5

# zip for parallel iteration
names = ["Alice", "Bob", "Charlie"]
scores = [95, 87, 92]
for name, score in zip(names, scores, strict=True):  # strict=True: error if different lengths
    print(f"{name}: {score}")
```

---

## Interview Questions

### Beginner
1. **What makes code "Pythonic"?** Pythonic code follows Python idioms: list comprehensions over loops, context managers for resources, EAFP over LBYL (try/except vs if-check), using built-in functions (enumerate, zip, map), unpacking, generators for lazy evaluation. It reads naturally and uses Python's features rather than translating from other languages.

2. **When would you use `defaultdict` vs regular `dict`?** `defaultdict` when: you're building collections (grouping items into lists, counting occurrences) and want to avoid checking if key exists first. Regular `dict` when: missing keys should raise errors (catching bugs), or using `dict.get(key, default)` / `dict.setdefault()` is sufficient. `defaultdict(list)` eliminates all `if key not in d: d[key] = []` patterns.

3. **What does `Counter` provide over manual counting?** `Counter` gives: `most_common(n)`, arithmetic operations (add/subtract counters), `elements()` (iterate with repeats), `total()`, and it handles the counting loop automatically. Use for: word frequency, character counting, finding top-K elements. It's the right tool when you need frequency distribution.

### Intermediate
4. **Explain `lru_cache` — how does it work and what are the gotchas?** LRU (Least Recently Used) cache stores N most recent function call results. Keyed by arguments (must be hashable!). Gotchas: (1) arguments must be hashable (no lists/dicts), (2) maxsize=None means unbounded (memory leak risk), (3) first arg `self` in methods means per-instance results aren't shared, (4) cache persists for module lifetime. Use `cache_info()` to monitor hit rate.

5. **How does `groupby` differ from SQL GROUP BY?** `itertools.groupby` only groups CONSECUTIVE identical elements — data MUST be sorted by the grouping key first! It's lazy (generator). SQL GROUP BY groups all matching records regardless of order. Common mistake: using `groupby` on unsorted data gives wrong results. Always `sorted(data, key=...)` before `groupby(data, key=...)`.

6. **What is `singledispatch` and when would you use it?** `singledispatch` provides function overloading based on the type of the first argument. Register implementations for different types. Use when: processing heterogeneous data (JSON nodes, API responses), replacing type-checking if/elif chains, building serializers/formatters. It's cleaner than `isinstance()` checks and follows the Open/Closed principle.

### Advanced
7. **Compare `functools.reduce` vs explicit loops — when is each better?** `reduce`: appropriate for well-known operations (sum, product, flatten) where the combiner is obvious. Loops: better for complex logic with early termination, multiple accumulators, or side effects. Readability rule: if you need to think hard about the lambda, use a loop. Python prefers explicit loops over clever reductions (Guido's philosophy).

8. **How would you process a 100GB file using itertools and generators?** Pipeline: `open(file)` (lazy line iterator) → `islice` for batching → `chain.from_iterable` for flattening → `filter/map` for transforming → `groupby` for aggregation → write output. Key: nothing loads fully into memory. Each element flows through the pipeline one at a time. Use `batched()` for chunk-based DB inserts.

9. **Design a memoization system that handles unhashable arguments.** Convert unhashable args to hashable: lists → tuples, dicts → frozenset of items (sorted), sets → frozensets. Create a `make_hashable()` converter. Alternative: serialize args to JSON string as cache key. For custom objects: use `id()` as key (weak refs for values). Consider TTL eviction for long-running processes.

---

## Hands-On Exercise
1. Use `Counter` to find the top 10 words in a text file
2. Implement a data pipeline using `chain`, `islice`, and `groupby`
3. Create a `@memoize` decorator that handles unhashable arguments
4. Build a frequency analysis tool combining `Counter`, `defaultdict`, and comprehensions
5. Solve: "Group anagrams" using `defaultdict` and sorted keys
