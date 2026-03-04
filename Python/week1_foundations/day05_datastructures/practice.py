#!/usr/bin/env python3
"""Day 5 - Data Structures Deep Dive"""

from collections import defaultdict, Counter, OrderedDict, deque, namedtuple
from typing import Any

print("=" * 50)
print("DATA STRUCTURES DEEP DIVE")
print("=" * 50)

# ============================================
# 1. LIST OPERATIONS
# ============================================
print("\n--- 1. LIST OPERATIONS ---")

lst = [1, 2, 3, 4, 5]
print(f"Original: {lst}")

# Adding elements
lst.append(6)           # Add single element
print(f"After append(6): {lst}")

lst.extend([7, 8])      # Add multiple elements
print(f"After extend([7,8]): {lst}")

lst.insert(0, 0)        # Insert at index
print(f"After insert(0, 0): {lst}")

# Removing elements
popped = lst.pop()      # Remove last
print(f"After pop(): {lst}, popped: {popped}")

lst.remove(5)           # Remove first occurrence
print(f"After remove(5): {lst}")

# Slicing
print(f"\nSlicing examples on [0,1,2,3,4,5,6,7]:")
nums = [0, 1, 2, 3, 4, 5, 6, 7]
print(f"  nums[2:5] = {nums[2:5]}")
print(f"  nums[::2] = {nums[::2]}")     # Every 2nd
print(f"  nums[::-1] = {nums[::-1]}")   # Reverse
print(f"  nums[-3:] = {nums[-3:]}")     # Last 3

# Sorting
mixed = [3, 1, 4, 1, 5, 9, 2, 6]
print(f"\nSorting {mixed}:")
print(f"  sorted(): {sorted(mixed)}")
print(f"  sorted(reverse=True): {sorted(mixed, reverse=True)}")

# Key-based sorting
words = ["banana", "apple", "Cherry", "date"]
print(f"\nSorting words: {words}")
print(f"  By length: {sorted(words, key=len)}")
print(f"  Case-insensitive: {sorted(words, key=str.lower)}")

# ============================================
# 2. DICTIONARY OPERATIONS
# ============================================
print("\n--- 2. DICTIONARY OPERATIONS ---")

person = {"name": "Alice", "age": 30, "city": "NYC"}
print(f"Original: {person}")

# Safe access with get
print(f"get('name'): {person.get('name')}")
print(f"get('salary', 0): {person.get('salary', 0)}")

# Update and merge
person.update({"job": "Engineer", "age": 31})
print(f"After update: {person}")

# Python 3.9+ merge operators
d1 = {"a": 1, "b": 2}
d2 = {"b": 3, "c": 4}
merged = d1 | d2       # New dict
print(f"\nd1 | d2: {merged}")

# setdefault
cache = {}
cache.setdefault("users", []).append("alice")
cache.setdefault("users", []).append("bob")
print(f"setdefault example: {cache}")

# Dict comprehension
squares = {x: x**2 for x in range(6)}
print(f"\nDict comprehension: {squares}")

# Filtering dict
filtered = {k: v for k, v in squares.items() if v > 10}
print(f"Filtered (v > 10): {filtered}")

# ============================================
# 3. SET OPERATIONS
# ============================================
print("\n--- 3. SET OPERATIONS ---")

a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

print(f"Set A: {a}")
print(f"Set B: {b}")
print(f"\nUnion (A | B): {a | b}")
print(f"Intersection (A & B): {a & b}")
print(f"Difference (A - B): {a - b}")
print(f"Symmetric Diff (A ^ B): {a ^ b}")
print(f"Is A subset of B: {a <= b}")
print(f"Is A superset of B: {a >= b}")

# Set comprehension
even_squares = {x**2 for x in range(10) if x % 2 == 0}
print(f"\nSet comprehension (even squares): {even_squares}")

# Practical: Remove duplicates while preserving order
items = [1, 3, 2, 1, 5, 3, 5, 1, 4]
unique_ordered = list(dict.fromkeys(items))
print(f"Unique preserving order: {unique_ordered}")

# ============================================
# 4. TUPLE UNPACKING
# ============================================
print("\n--- 4. TUPLE UNPACKING ---")

# Basic unpacking
point = (10, 20)
x, y = point
print(f"Basic: x={x}, y={y}")

# Extended unpacking
first, *rest = [1, 2, 3, 4, 5]
print(f"first, *rest: first={first}, rest={rest}")

*head, last = [1, 2, 3, 4, 5]
print(f"*head, last: head={head}, last={last}")

first, *middle, last = [1, 2, 3, 4, 5]
print(f"first, *middle, last: {first}, {middle}, {last}")

# Nested unpacking
data = ("Alice", (1990, 5, 15))
name, (year, month, day) = data
print(f"\nNested: {name} born {year}-{month}-{day}")

# Swap using tuple unpacking
a, b = 1, 2
a, b = b, a
print(f"Swap: a={a}, b={b}")

# ============================================
# 5. COMPREHENSIONS
# ============================================
print("\n--- 5. COMPREHENSIONS ---")

# List comprehension
squares = [x**2 for x in range(10)]
print(f"List: {squares}")

# With condition
evens = [x for x in range(20) if x % 2 == 0]
print(f"List with filter: {evens}")

# Nested list comprehension
matrix = [[i*j for j in range(1, 4)] for i in range(1, 4)]
print(f"Nested list: {matrix}")

# Flatten nested list
flat = [item for row in matrix for item in row]
print(f"Flattened: {flat}")

# Dict comprehension
word_lengths = {word: len(word) for word in ["apple", "banana", "cherry"]}
print(f"\nDict: {word_lengths}")

# Set comprehension
unique_lengths = {len(word) for word in ["apple", "banana", "cherry", "date"]}
print(f"Set: {unique_lengths}")

# Generator expression (lazy)
gen = (x**2 for x in range(1000000))
print(f"\nGenerator (lazy): {gen}")
print(f"First 5: {[next(gen) for _ in range(5)]}")

# ============================================
# 6. COLLECTIONS MODULE
# ============================================
print("\n--- 6. COLLECTIONS MODULE ---")

# Counter
words = ["apple", "banana", "apple", "cherry", "apple", "banana"]
counter = Counter(words)
print(f"Counter: {counter}")
print(f"Most common 2: {counter.most_common(2)}")

# defaultdict
dd = defaultdict(list)
for item in [("a", 1), ("b", 2), ("a", 3)]:
    dd[item[0]].append(item[1])
print(f"\ndefaultdict: {dict(dd)}")

# defaultdict with int (for counting)
word_count = defaultdict(int)
for word in "hello world hello python hello".split():
    word_count[word] += 1
print(f"Word count: {dict(word_count)}")

# deque (double-ended queue)
dq = deque([1, 2, 3], maxlen=5)
dq.append(4)
dq.appendleft(0)
print(f"\ndeque: {dq}")
dq.rotate(2)
print(f"After rotate(2): {dq}")

# namedtuple
Point = namedtuple("Point", ["x", "y"])
p = Point(10, 20)
print(f"\nnamedtuple: {p}")
print(f"Access: x={p.x}, y={p.y}")
print(f"As dict: {p._asdict()}")

# ============================================
# 7. ADVANCED PATTERNS
# ============================================
print("\n--- 7. ADVANCED PATTERNS ---")

# Group by
from itertools import groupby

data = [
    {"name": "Alice", "dept": "Sales"},
    {"name": "Bob", "dept": "IT"},
    {"name": "Charlie", "dept": "Sales"},
    {"name": "Diana", "dept": "IT"},
]

# Sort first (groupby needs sorted data)
sorted_data = sorted(data, key=lambda x: x["dept"])
grouped = {k: list(v) for k, v in groupby(sorted_data, key=lambda x: x["dept"])}
print(f"Grouped by dept:")
for dept, employees in grouped.items():
    print(f"  {dept}: {[e['name'] for e in employees]}")

# Zip with dict creation
keys = ["name", "age", "city"]
values = ["Alice", 30, "NYC"]
person = dict(zip(keys, values))
print(f"\nZip to dict: {person}")

# Enumerate with start
for i, item in enumerate(["a", "b", "c"], start=1):
    print(f"  {i}. {item}")

print("\n✅ Day 5 completed!")
