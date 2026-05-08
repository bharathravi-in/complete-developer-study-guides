# Day 2 - Data Types Deep Dive

## Table of Contents
- [Overview](#overview)
- [Numeric Types](#numeric-types)
- [String Type](#string-type)
- [Collection Types](#collection-types)
- [Mutable vs Immutable](#mutable-vs-immutable)
- [Memory and Identity](#memory-and-identity)
- [Best Practices](#best-practices)
- [Interview Preparation](#interview-preparation)
- [Practice Exercises](#practice-exercises)

---

## Overview

Python has several built-in data types for representing different kinds of information. Understanding these types and their properties (mutable vs immutable, ordered vs unordered) is crucial for writing efficient Python code.

---

## Numeric Types

### Integer (int)

Integers have unlimited precision in Python 3.

```python
# Integer literals
x = 42
y = -17
z = 0

# Large integers (no overflow)
big = 123456789012345678901234567890
print(big ** 2)  # Works fine!

# Binary, Octal, Hex
binary = 0b1010      # 10 in decimal
octal = 0o12         # 10 in decimal
hex_num = 0xA        # 10 in decimal

# Underscores for readability (Python 3.6+)
million = 1_000_000
print(million)  # 1000000
```

### Float

Double-precision floating-point numbers (64-bit).

```python
# Float literals
pi = 3.14159
scientific = 1.5e-4  # 0.00015
negative = -2.5

# Precision issues
print(0.1 + 0.2)  # 0.30000000000000004 (!)

# Use decimal for precise calculations
from decimal import Decimal
x = Decimal('0.1')
y = Decimal('0.2')
print(x + y)  # Decimal('0.3')

# Infinity and NaN
inf = float('inf')
neg_inf = float('-inf')
not_a_number = float('nan')

import math
print(math.isinf(inf))    # True
print(math.isnan(not_a_number))  # True
```

### Boolean (bool)

Subclass of int where `True = 1` and `False = 0`.

```python
# Boolean literals
is_active = True
is_deleted = False

# Boolean as int
print(True + True)   # 2
print(False * 10)    # 0

# Truthy and Falsy values
# Falsy: False, None, 0, 0.0, '', [], {}, set()
# Everything else is Truthy

if []:  # Empty list is False
    print("Won't print")

if [1, 2]:  # Non-empty list is True
    print("Will print")

# Boolean operations
print(True and False)  # False
print(True or False)   # True
print(not True)        # False

# Short-circuit evaluation
def expensive_function():
    print("Called!")
    return True

# expensive_function() won't be called
result = False and expensive_function()
```

### Complex Numbers

```python
# Complex literals
z = 3 + 4j
z2 = complex(3, 4)

# Operations
print(z.real)      # 3.0
print(z.imag)      # 4.0
print(abs(z))      # 5.0 (magnitude)
print(z.conjugate())  # (3-4j)

# Complex arithmetic
z3 = (1 + 2j) + (3 + 4j)
print(z3)  # (4+6j)
```

---

## String Type

Strings are **immutable** sequences of Unicode characters.

### String Creation

```python
# String literals
single = 'Hello'
double = "World"
triple = '''Multi
line
string'''

# Raw strings (escape sequences ignored)
path = r'C:\Users\name\file.txt'

# f-strings (Python 3.6+)
name = "Alice"
age = 30
print(f"{name} is {age} years old")
print(f"{name.upper()}")  # Can include expressions
print(f"{2 + 2 = }")      # Prints: 2 + 2 = 4 (Python 3.8+)

# Format method
print("{}  is {} years old".format(name, age))
print("{1} {0}".format("World", "Hello"))  # Hello World
```

### String Operations

```python
s = "Python Programming"

# Indexing
print(s[0])     # 'P'
print(s[-1])    # 'g' (last character)

# Slicing
print(s[0:6])   # 'Python'
print(s[:6])    # 'Python' (same)
print(s[7:])    # 'Programming'
print(s[::2])   # 'Pto rgamn' (every 2nd char)
print(s[::-1])  # 'gnimmargorP nohtyP' (reverse)

# Length
print(len(s))   # 18

# Concatenation
greeting = "Hello" + " " + "World"

# Repetition
print("Ha" * 3)  # "HaHaHa"

# Membership
print("Python" in s)      # True
print("Java" not in s)    # True
```

### String Methods

```python
s = "  Python Programming  "

# Case conversion
print(s.lower())       # '  python programming  '
print(s.upper())       # ' PYTHON PROGRAMMING  '
print(s.title())       # '  Python Programming  '
print(s.capitalize())  # '  python programming  '
print(s.swapcase())    # '  pYTHON pROGRAMMING  '

# Whitespace
print(s.strip())       # 'Python Programming' (both ends)
print(s.lstrip())      # 'Python Programming  ' (left)
print(s.rstrip())      # '  Python Programming' (right)

# Search
print(s.find('Prog'))     # 9 (index, or -1 if not found)
print(s.index('Prog'))    # 9 (index, or raises ValueError)
print(s.count('n'))       # 2
print(s.startswith(' P')) # True
print(s.endswith('g '))   # True

# Split and Join
words = "apple,banana,cherry".split(',')
print(words)  # ['apple', 'banana', 'cherry']

joined = " | ".join(words)
print(joined)  # 'apple | banana | cherry'

# Replace
print("hello world".replace('world', 'Python'))  # 'hello Python'

# Check type
print("123".isdigit())      # True
print("abc".is alpha())      # True
print("abc123".isalnum())   # True
print("   ".isspace())      # True
```

### String Immutability

```python
s = "Hello"

# ❌ Cannot modify string
# s[0] = 'h'  # TypeError: 'str' object does not support item assignment

# ✅ Must create new string
s = 'h' + s[1:]  # 'hello'

# Performance note: String concatenation in loop is slow
# ❌ SLOW
result = ""
for i in range(1000):
    result += str(i)  # Creates new string each time!

# ✅ FAST
result = "".join(str(i) for i in range(1000))
```

---

## Collection Types

### List -  Mutable, Ordered, Allows Duplicates

```python
# List creation
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", 3.14, True, [1, 2]]
empty = []
range_list = list(range(5))  # [0, 1, 2, 3, 4]

# Indexing and slicing (same as strings)
print(fruits[0])      # 'apple'
print(fruits[-1])     # 'cherry'
print(fruits[1:3])    # ['banana', 'cherry']

# Modification (mutable!)
fruits[0] = "apricot"
fruits[1:3] = ["blueberry", "coconut"]

# Methods
fruits.append("date")           # Add to end
fruits.insert(0, "avocado")     # Insert at index
fruits.extend(["elderberry"])   # Add multiple
fruits.remove("banana")         # Remove first occurrence
popped = fruits.pop()           # Remove and return last
popped_index = fruits.pop(0)    # Remove and return at index
fruits.clear()                  # Remove all

# Sorting
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
numbers.sort()                  # In-place sort
print(numbers)                  # [1, 1, 2, 3, 4, 5, 6, 9]

sorted_nums = sorted([3, 1, 4], reverse=True)  # Returns new sorted list

# List comprehension
squares = [x**2 for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
matrix = [[i*j for j in range(3)] for i in range(3)]
```

### Tuple - Immutable, Ordered, Allows Duplicates

```python
# Tuple creation
coordinates = (10, 20)
colors = ("red", "green", "blue")
single_item = (42,)  # Comma required for single item!
empty = ()
tuple_from_list = tuple([1, 2, 3])

# Unpacking
x, y = coordinates
print(x, y)  # 10 20

# Swapping
a, b = 10, 20
a, b = b, a  # Swap using tuple packing/unpacking

# Extended unpacking (Python 3+)
first, *middle, last = [1, 2, 3, 4, 5]
print(first)   # 1
print(middle)  # [2, 3, 4]
print(last)    # 5

# Tuples are immutable
# coordinates[0] = 15  # TypeError!

# But can contain mutable objects
t = ([1, 2], [3, 4])
t[0].append(3)  # Modifies the list inside tuple
print(t)  # ([1, 2, 3], [3, 4])

# Named tuples
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])
p = Point(10, 20)
print(p.x, p.y)  # 10 20
print(p[0], p[1])  # 10 20 (still indexed like tuple)
```

### Set - Mutable, Unordered, No Duplicates

```python
# Set creation
fruits = {"apple", "banana", "cherry"}
numbers = {1, 2, 3, 4, 5}
empty_set = set()  # {} creates empty dict, not set!

# Duplicates removed automatically
nums = {1, 2, 2, 3, 3, 3}
print(nums)  # {1, 2, 3}

# Methods
fruits.add("date")
fruits.remove("banana")      # Raises KeyError if not found
fruits.discard("orange")     # No error if not found
popped = fruits.pop()        # Remove and return arbitrary element
fruits.clear()

# Set operations
a = {1, 2, 3, 4, 5}
b = {4, 5, 6, 7, 8}

print(a | b)  # Union: {1, 2, 3, 4, 5, 6, 7, 8}
print(a & b)  # Intersection: {4, 5}
print(a - b)  # Difference: {1, 2, 3}
print(a ^ b)  # Symmetric difference: {1, 2, 3, 6, 7, 8}

# Method alternatives
print(a.union(b))
print(a.intersection(b))
print(a.difference(b))
print(a.symmetric_difference(b))

# Subset and superset
print({1, 2}.issubset({1, 2, 3}))      # True
print({1, 2, 3}.issuperset({1, 2}))    # True

# Frozenset (immutable set)
fs = frozenset([1, 2, 3])
# fs.add(4)  # AttributeError - immutable!
```

### Dictionary - Mutable, Ordered (Python 3.7+), Keys Unique

```python
# Dictionary creation
person = {"name": "Alice", "age": 30, "city": "NYC"}
empty_dict = {}
dict_from_tuples = dict([("a", 1), ("b", 2)])
dict_comprehension = {x: x**2 for x in range(5)}

# Access
print(person["name"])          # 'Alice'
print(person.get("age"))       # 30
print(person.get("country", "USA"))  # 'USA' (default if key missing)

# Modification
person["age"] = 31             # Update
person["country"] = "USA"      # Add new key
del person["city"]             # Delete key
popped = person.pop("age")     # Remove and  return
person.clear()                 # Remove all

# Methods
person = {"name": "Alice", "age": 30}
print(person.keys())           # dict_keys(['name', 'age'])
print(person.values())         # dict_values(['Alice', 30])
print(person.items())          # dict_items([('name', 'Alice'), ('age', 30)])

# Iteration
for key in person:
    print(key, person[key])

for key, value in person.items():
    print(f"{key}: {value}")

# Merging dictionaries
dict1 = {"a": 1, "b": 2}
dict2 = {"c": 3, "d": 4}

# Python 3.5+
merged = {**dict1, **dict2}

# Python 3.9+
merged = dict1 | dict2

# setdefault
counts = {}
counts.setdefault("apple", 0)
counts["apple"] += 1

# defaultdict (never raises KeyError)
from collections import defaultdict
counts = defaultdict(int)  # Default value: 0
counts["apple"] += 1  # No KeyError!

# Counter (counts hashable objects)
from collections import Counter
words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
counter = Counter(words)
print(counter)  # Counter({'apple': 3, 'banana': 2, 'cherry': 1})
print(counter.most_common(2))  # [('apple', 3), ('banana', 2)]
```

---

## Mutable vs Immutable

### Immutable Types
- int, float, bool, str, tuple, frozenset
- **Cannot be changed after creation**
- Modifications create new objects

```python
# String is immutable
s = "hello"
print(id(s))  # Memory address
s = s.upper()  # Creates NEW string
print(id(s))  # Different address!

# Tuple is immutable
t = (1, 2, 3)
# t[0] = 10  # TypeError!
```

### Mutable Types
- list, dict, set
- **Can be modified in-place**
- Modifications keep same object

```python
# List is mutable
lst = [1, 2, 3]
print(id(lst))  # Memory address
lst.append(4)   # Modifies SAME object
print(id(lst))  # Same address!
```

### Implications

```python
# Immutable - safe to share
x = 100
y = x
y = 200  # Creates new int, x unchanged
print(x)  # 100

# Mutable - be careful!
list1 = [1, 2, 3]
list2 = list1  # Both reference SAME list
list2.append(4)
print(list1)  # [1, 2, 3, 4] - list1 also changed!

# To copy mutable objects
list3 = list1.copy()  # Shallow copy
list4 = list1[:]      # Shallow copy
import copy
list5 = copy.deepcopy(list1)  # Deep copy (nested structures)
```

---

## Memory and Identity

### `id()` Function

Returns the memory address (identity) of an object.

```python
x = 1000
y = 1000
print(id(x))  # e.g., 140234567890
print(id(y))  # Different address

# Small integers are cached (-5 to 256)
a = 100
b = 100
print(id(a) == id(b))  # True (same object!)

# Strings may be interned
s1 = "hello"
s2 = "hello"
print(s1 is s2)  # May be True (string interning)
```

### `is` vs `==`

```python
# == compares VALUES
# is compares IDENTITIES (memory addresses)

list1 = [1, 2, 3]
list2 = [1, 2, 3]
list3 = list1

print(list1 == list2)  # True (same content)
print(list1 is list2)  # False (different objects)
print(list1 is list3)  # True (same object)

# Always use 'is' with None, True, False (singletons)
if value is None:  # ✅ Correct
    pass

if value == None:  # ❌ Works but not idiomatic
    pass
```

###NoneType

```python
# None is a singleton (only one None object)
x = None
y = None
print(x is y)  # True (same object)

# Common use: default parameter
def function(value=None):
    if value is None:
        value = []  # Create new list
    value.append(1)
    return value

# Check for None
if value is None:
    print("No value")

if not value:  # Careful! 0, False, '', [], {} are also falsy
    print("Falsy value")
```

---

## Best Practices

### 1. Choose the Right Data Structure

```python
# ✅ Use list for ordered collection that may change
shopping_list = ["milk", "bread", "eggs"]

# ✅ Use tuple for fixed collection
coordinates = (latitude, longitude)

# ✅ Use set for unique items, fast membership testing
unique_users = {"alice", "bob", "charlie"}

# ✅ Use dict for key-value mappings
user_ages = {"alice": 30, "bob": 25}
```

### 2. Be Aware of Mutability

```python
# ❌ Mutable default argument
def add_item(item, items=[]):  # WRONG!
    items.append(item)
    return items

# ✅ Use None as default
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

### 3. Use Comprehensions

```python
# ✅ List comprehension (concise and fast)
squares = [x**2 for x in range(10)]

# ❌ Loopbuilding (verbose)
squares = []
for x in range(10):
    squares.append(x**2)
```

### 4. String Concatenation

```python
# ❌ Slow for many concatenations
result = ""
for i in range(10000):
    result += str(i)

# ✅ Fast
result = "".join(str(i) for i in range(10000))

# ✅ f-strings for formatting
name = "Alice"
age = 30
message = f"{name} is {age} years old"
```

---

## Interview Preparation

### Q1: What is the difference between list and tuple?

**Answer:**

| Feature | List | Tuple |
|---------|------|-------|
| Mutability | Mutable | Immutable |
| Syntax | `[1, 2, 3]` | `(1, 2, 3)` |
| Performance | Slower | Faster |
| Use case | Dynamic data | Fixed data |
| Methods | Many (append, etc.) | Few (count, index) |

**When to use:**
- **List**: Shopping cart items, todo list
- **Tuple**: Coordinates, RGB colors, database records

---

### Q2: Explain mutable vs immutable types with examples

**Answer:**
```python
# Immutable (int, str, tuple)
x = 10
id_before = id(x)
x += 1  # Creates new object
id_after = id(x)
print(id_before == id_after)  # False

# Mutable (list, dict, set)
lst = [1, 2, 3]
id_before = id(lst)
lst.append(4)  # Modifies same object
id_after = id(lst)
print(id_before == id_after)  # True
```

**Implications:**
- Immutable objects are safe to use as dict keys
- Mutable objects can lead to unexpected behavior if shared

---

### Q3: What are truthy and falsy values in Python?

**Answer:**

**Falsy values:**
```python
False, None, 0, 0.0, 0j, '', [], (), {}, set(), frozenset()
```

**Everything else is truthy:**
```python
True, 1, "hello", [1], {'a': 1}, {1, 2}
```

**Usage:**
```python
if my_list:  # Check if non-empty
    process(my_list)

if user_name:  # Check if not empty string
    welcome(user_name)
```

---

### Q4: Coding Problem - Find duplicates in a list

**Question:** Write a function to find all duplicate elements in a list.

**Solution:**
```python
def find_duplicates(lst):
    """Return list of duplicate elements"""
    seen = set()
    duplicates = set()
    
    for item in lst:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    
    return list(duplicates)

# Test
numbers = [1, 2, 3, 2, 4, 5, 1, 6]
print(find_duplicates(numbers))  # [1, 2]

# Alternative using Counter
from collections import Counter
def find_duplicates_v2(lst):
    counts = Counter(lst)
    return [item for item, count in counts.items() if count > 1]
```

---

### Q5: Coding Problem - Merge two dictionaries

**Question:** Merge two dictionaries, with values from the second dict taking precedence.

**Solution:**
```python
def merge_dicts(dict1, dict2):
    """Merge two dictionaries"""
    # Method 1: Using unpacking (Python 3.5+)
    return {**dict1, **dict2}

# Method 2: Using | operator (Python 3.9+)
def merge_dicts_v2(dict1, dict2):
    return dict1 | dict2

# Method 3: Using update
def merge_dicts_v3(dict1, dict2):
    result = dict1.copy()
    result.update(dict2)
    return result

# Test
d1 = {"a": 1, "b": 2}
d2 = {"b": 3, "c": 4}
print(merge_dicts(d1, d2))  # {'a': 1, 'b': 3, 'c': 4}
```

---

### Q6: Coding Problem - Two Sum (LeetCode classic)

**Question:** Given a list of integers and a target sum, return indices of two numbers that add up to the target.

**Solution:**
```python
def two_sum(nums, target):
    """
    Find two numbers that add up to target.
    Return their indices.
    
    Time: O(n), Space: O(n)
    """
    seen = {}  # value -> index
    
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    
    return []  # No solution

# Test
nums = [2, 7, 11, 15]
target = 9
print(two_sum(nums, target))  # [0, 1] (2 + 7 = 9)
```

---

### Q7: What is the time complexity of common operations?

**Answer:**

| Operation | List | Tuple | Set | Dict |
|-----------|------|-------|-----|------|
| Access by index | O(1) | O(1) | N/A | N/A |
| Search | O(n) | O(n) | O(1) | O(1) |
| Insert/Delete end | O(1) | N/A | O(1) | O(1) |
| Insert/Delete begin | O(n) | N/A | O(1) | O(1) |
| Memory | More | Less | More | More |

---

## Practice Exercises

### Exercise 1: Data Type Summary
Create examples demonstrating all data types with their key characteristics.

### Exercise 2: String Manipulation
Write functions to:
- Reverse words in a sentence
- Check if a string is a palindrome
- Count vowels and consonants

<details>
<summary>Solutions</summary>

```python
def reverse_words(sentence):
    return ' '.join(sentence.split()[::-1])

def is_palindrome(s):
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]

def count_vowels_consonants(s):
    vowels = set('aeiouAEIOU')
    v_count = sum(1 for c in s if c in vowels)
    c_count = sum(1 for c in s if c.isalpha() and c not in vowels)
    return v_count, c_count
```
</details>

---

## Run
```bash
python practice.py
```

## Key Takeaways

1. ✅ Choose mutable types (list, dict, set) for dynamic data
2. ✅ Choose immutable types (tuple, frozenset) for fixed data
3. ✅ Use `is` for identity, `==` for equality
4. ✅ Sets and dicts provide O(1) lookup
5. ✅ Lists preserve order and allow duplicates
6. ✅ Strings are immutable; use f-strings for formatting
7. ✅ Be careful with mutable default arguments
8. ✅ Use `None` instead of empty mutable defaults
