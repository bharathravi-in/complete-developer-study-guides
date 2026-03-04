#!/usr/bin/env python3
"""Day 20 - Pythonic Coding & Advanced Features"""

from functools import lru_cache, partial, reduce, wraps
from itertools import (
    chain, combinations, permutations, product,
    groupby, islice, cycle, repeat, count,
    accumulate, starmap, filterfalse, takewhile, dropwhile
)
from collections import Counter, defaultdict, namedtuple, deque, OrderedDict, ChainMap
from operator import add, mul, itemgetter, attrgetter

print("=" * 50)
print("PYTHONIC CODING")
print("=" * 50)


# ============================================
# 1. MAP, FILTER, REDUCE
# ============================================
print("\n--- 1. MAP, FILTER, REDUCE ---")

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Map - apply function to each element
squares = list(map(lambda x: x**2, numbers))
print(f"map (squares): {squares}")

# Filter - keep elements that pass test
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(f"filter (evens): {evens}")

# Reduce - combine elements to single value
total = reduce(lambda acc, x: acc + x, numbers)
print(f"reduce (sum): {total}")

product_all = reduce(mul, numbers)
print(f"reduce (product): {product_all}")

# Chaining
result = reduce(add, filter(lambda x: x % 2 == 0, map(lambda x: x**2, numbers)))
print(f"Chained (sum of squared evens): {result}")

# Pythonic alternative using comprehensions
result_pythonic = sum(x**2 for x in numbers if x % 2 == 0)
print(f"Pythonic way: {result_pythonic}")


# ============================================
# 2. FUNCTOOLS
# ============================================
print("\n--- 2. FUNCTOOLS ---")

# lru_cache - memoization
@lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(f"fibonacci(100): {fibonacci(100)}")
print(f"Cache info: {fibonacci.cache_info()}")

# partial - fix some arguments
def power(base, exponent):
    return base ** exponent

square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(f"partial square(5): {square(5)}")
print(f"partial cube(3): {cube(3)}")

# reduce with initial value
values = [1, 2, 3, 4]
result = reduce(lambda acc, x: acc * x, values, 10)  # 10 * 1 * 2 * 3 * 4
print(f"reduce with initial: {result}")


# ============================================
# 3. ITERTOOLS
# ============================================
print("\n--- 3. ITERTOOLS ---")

# chain - combine iterables
combined = list(chain([1, 2], [3, 4], [5, 6]))
print(f"chain: {combined}")

# combinations - unique combinations
combs = list(combinations('ABC', 2))
print(f"combinations('ABC', 2): {combs}")

# permutations - all orderings
perms = list(permutations('AB'))
print(f"permutations('AB'): {perms}")

# product - cartesian product
prod = list(product([1, 2], ['a', 'b']))
print(f"product: {prod}")

# groupby - group consecutive elements
data = sorted([(1, 'a'), (1, 'b'), (2, 'c'), (2, 'd')], key=itemgetter(0))
for key, group in groupby(data, key=itemgetter(0)):
    print(f"  groupby key={key}: {list(group)}")

# islice - slice iterator
print(f"islice(count(), 5): {list(islice(count(), 5))}")

# accumulate - running accumulation
acc = list(accumulate([1, 2, 3, 4, 5]))
print(f"accumulate: {acc}")

acc_mul = list(accumulate([1, 2, 3, 4, 5], mul))
print(f"accumulate (mul): {acc_mul}")

# takewhile/dropwhile
nums = [2, 4, 6, 1, 3, 5]
print(f"takewhile(<5): {list(takewhile(lambda x: x < 5, nums))}")
print(f"dropwhile(<5): {list(dropwhile(lambda x: x < 5, nums))}")


# ============================================
# 4. COLLECTIONS - COUNTER
# ============================================
print("\n--- 4. COUNTER ---")

text = "mississippi"
counter = Counter(text)
print(f"Counter: {counter}")
print(f"Most common 3: {counter.most_common(3)}")
print(f"Count of 's': {counter['s']}")

# Update counter
counter.update("sss")
print(f"After update: {counter}")

# Counter arithmetic
c1 = Counter(a=3, b=1)
c2 = Counter(a=1, b=2)
print(f"c1 + c2: {c1 + c2}")
print(f"c1 - c2: {c1 - c2}")


# ============================================
# 5. COLLECTIONS - DEFAULTDICT
# ============================================
print("\n--- 5. DEFAULTDICT ---")

# Group items by category
items = [
    ('fruit', 'apple'),
    ('vegetable', 'carrot'),
    ('fruit', 'banana'),
    ('vegetable', 'broccoli'),
]

grouped = defaultdict(list)
for category, item in items:
    grouped[category].append(item)
print(f"defaultdict(list): {dict(grouped)}")

# Count occurrences
word_counts = defaultdict(int)
for word in "the quick brown fox jumps over the lazy dog".split():
    word_counts[word] += 1
print(f"defaultdict(int): {dict(word_counts)}")

# Nested defaultdict
nested = defaultdict(lambda: defaultdict(int))
nested['a']['x'] = 1
nested['a']['y'] = 2
nested['b']['x'] = 3
print(f"nested defaultdict: {dict(nested)}")


# ============================================
# 6. COLLECTIONS - NAMEDTUPLE
# ============================================
print("\n--- 6. NAMEDTUPLE ---")

Point = namedtuple('Point', ['x', 'y'])
p = Point(3, 4)
print(f"namedtuple: {p}")
print(f"Access: x={p.x}, y={p.y}")
print(f"Unpack: x, y = {p.x}, {p.y}")

# With defaults (Python 3.7+)
Person = namedtuple('Person', ['name', 'age', 'city'], defaults=['Unknown', 0, 'Unknown'])
print(f"With defaults: {Person('Alice')}")

# Convert to dict
print(f"As dict: {p._asdict()}")

# Replace
p2 = p._replace(x=10)
print(f"Replace: {p2}")


# ============================================
# 7. COLLECTIONS - DEQUE
# ============================================
print("\n--- 7. DEQUE ---")

dq = deque([1, 2, 3], maxlen=5)
print(f"Initial deque: {dq}")

dq.append(4)
dq.appendleft(0)
print(f"After append: {dq}")

dq.rotate(2)
print(f"After rotate(2): {dq}")

dq.rotate(-2)
print(f"After rotate(-2): {dq}")

# As a sliding window
dq = deque(maxlen=3)
for i in range(5):
    dq.append(i)
    print(f"  Window: {list(dq)}")


# ============================================
# 8. CHAINMAP
# ============================================
print("\n--- 8. CHAINMAP ---")

defaults = {'color': 'red', 'size': 'medium'}
user_prefs = {'color': 'blue'}

config = ChainMap(user_prefs, defaults)
print(f"ChainMap: {dict(config)}")
print(f"color: {config['color']}")
print(f"size: {config['size']}")


# ============================================
# 9. PYTHONIC PATTERNS
# ============================================
print("\n--- 9. PYTHONIC PATTERNS ---")

# Enumerate with start
for i, item in enumerate(['a', 'b', 'c'], start=1):
    print(f"  {i}. {item}")

# Zip for parallel iteration
names = ['Alice', 'Bob']
scores = [95, 87]
for name, score in zip(names, scores):
    print(f"  {name}: {score}")

# Dict comprehension
squares = {x: x**2 for x in range(5)}
print(f"Dict comp: {squares}")

# Conditional expression
x = 10
result = "positive" if x > 0 else "non-positive"
print(f"Conditional: {result}")

# Walrus operator (Python 3.8+)
data = [1, 2, 3, 4, 5]
if (n := len(data)) > 3:
    print(f"Walrus: Length {n} > 3")


# ============================================
# 10. OPERATOR MODULE
# ============================================
print("\n--- 10. OPERATOR MODULE ---")

# itemgetter for sorting
users = [
    {'name': 'Alice', 'age': 30},
    {'name': 'Bob', 'age': 25},
    {'name': 'Charlie', 'age': 35},
]
sorted_users = sorted(users, key=itemgetter('age'))
print(f"Sorted by age: {[u['name'] for u in sorted_users]}")

# attrgetter for objects
Point = namedtuple('Point', ['x', 'y'])
points = [Point(3, 4), Point(1, 2), Point(5, 1)]
sorted_points = sorted(points, key=attrgetter('y'))
print(f"Sorted by y: {sorted_points}")


print("\n✅ Day 20 completed!")
