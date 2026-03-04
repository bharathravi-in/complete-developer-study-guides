#!/usr/bin/env python3
"""Day 2 - Data Types Deep Dive"""

import sys

print("=" * 50)
print("DATA TYPES DEEP DIVE")
print("=" * 50)

# ============================================
# 1. NUMERIC TYPES
# ============================================
print("\n--- 1. NUMERIC TYPES ---")

# Integer - unlimited precision
big_int = 10 ** 100
print(f"Big int (10^100): {len(str(big_int))} digits")
print(f"Integer bit length: {(1024).bit_length()} bits")

# Float - IEEE 754 double precision
print(f"\nFloat precision issue: 0.1 + 0.2 = {0.1 + 0.2}")
print(f"Float info: {sys.float_info.dig} significant digits")

# Boolean - subclass of int
print(f"\nBool is int subclass: {issubclass(bool, int)}")
print(f"True + True = {True + True}")
print(f"True * 10 = {True * 10}")

# ============================================
# 2. STRING (IMMUTABLE)
# ============================================
print("\n--- 2. STRING (IMMUTABLE) ---")

s = "hello"
print(f"Original string: '{s}', id: {id(s)}")

# String interning for small strings
s1 = "hello"
s2 = "hello"
print(f"'hello' is 'hello': {s1 is s2}")  # True (interned)

s3 = "hello world!"
s4 = "hello world!"
print(f"'hello world!' is 'hello world!': {s3 is s4}")  # May vary

# Demonstrating immutability
try:
    s[0] = 'H'  # This will fail
except TypeError as e:
    print(f"Cannot modify string: {e}")

# Creating new string instead
s_new = 'H' + s[1:]
print(f"New string: '{s_new}' (different id: {id(s) != id(s_new)})")

# ============================================
# 3. LIST (MUTABLE)
# ============================================
print("\n--- 3. LIST (MUTABLE) ---")

lst = [1, 2, 3]
print(f"Original list: {lst}, id: {id(lst)}")

lst.append(4)
print(f"After append: {lst}, id: {id(lst)}")  # Same id!

# List aliasing danger
lst2 = lst  # Both point to same object
lst2.append(5)
print(f"lst after modifying lst2: {lst}")  # Both affected!

# Proper list copy
lst3 = lst.copy()  # or lst[:]
lst3.append(6)
print(f"lst after modifying lst3 (copy): {lst}")  # lst unchanged

# ============================================
# 4. TUPLE (IMMUTABLE)
# ============================================
print("\n--- 4. TUPLE (IMMUTABLE) ---")

t = (1, 2, 3)
print(f"Tuple: {t}")

# Single element tuple needs comma
single = (1,)  # Tuple
not_tuple = (1)  # Just int with parentheses
print(f"(1,) is tuple: {isinstance(single, tuple)}")
print(f"(1) is tuple: {isinstance(not_tuple, tuple)}")

# Tuple with mutable element
t_with_list = (1, [2, 3], 4)
t_with_list[1].append(5)  # This works!
print(f"Tuple with modified list: {t_with_list}")

# ============================================
# 5. SET (MUTABLE, NO DUPLICATES)
# ============================================
print("\n--- 5. SET (MUTABLE, NO DUPLICATES) ---")

s = {1, 2, 2, 3, 3, 3}
print(f"Set removes duplicates: {s}")

# Set operations
a = {1, 2, 3}
b = {2, 3, 4}
print(f"Union: {a | b}")
print(f"Intersection: {a & b}")
print(f"Difference: {a - b}")
print(f"Symmetric Difference: {a ^ b}")

# Frozen set (immutable)
fs = frozenset([1, 2, 3])
print(f"Frozenset: {fs}")

# ============================================
# 6. DICTIONARY (MUTABLE)
# ============================================
print("\n--- 6. DICTIONARY (MUTABLE) ---")

d = {"name": "Python", "version": 3.12}
print(f"Dict: {d}")

# Dict is ordered (Python 3.7+)
d["year"] = 2024
print(f"Order preserved: {list(d.keys())}")

# Dictionary comprehension
squares = {x: x**2 for x in range(5)}
print(f"Squares dict: {squares}")

# ============================================
# 7. NONETYPE
# ============================================
print("\n--- 7. NONETYPE ---")

x = None
print(f"None type: {type(None)}")
print(f"None is singleton: {x is None}")  # Always use 'is' for None

# ============================================
# 8. MUTABLE VS IMMUTABLE
# ============================================
print("\n--- 8. MUTABLE VS IMMUTABLE ---")

# Immutable: int, float, bool, str, tuple, frozenset
# Mutable: list, dict, set

def demonstrate_mutability(obj, name):
    print(f"\n{name}: {obj}")
    print(f"ID before: {id(obj)}")
    return id(obj)

# Immutable example
x = 10
old_id = demonstrate_mutability(x, "int")
x += 1
print(f"After x += 1: {x}, ID changed: {id(x) != old_id}")

# Mutable example
lst = [1, 2, 3]
old_id = demonstrate_mutability(lst, "list")
lst.append(4)
print(f"After append: {lst}, ID changed: {id(lst) != old_id}")

# ============================================
# 9. IS VS ==
# ============================================
print("\n--- 9. IS VS == ---")

# Small integer caching (-5 to 256)
a = 256
b = 256
print(f"256 is 256: {a is b}")  # True (cached)

a = 257
b = 257
print(f"257 is 257: {a is b}")  # May be False (not cached)

# List comparison
list1 = [1, 2, 3]
list2 = [1, 2, 3]
list3 = list1

print(f"\nlist1 == list2: {list1 == list2}")  # True (same values)
print(f"list1 is list2: {list1 is list2}")    # False (different objects)
print(f"list1 is list3: {list1 is list3}")    # True (same object)

# ============================================
# 10. MEMORY SIZE
# ============================================
print("\n--- 10. MEMORY SIZE ---")

objects = [
    ("int 0", 0),
    ("int 1", 1),
    ("float 1.0", 1.0),
    ("bool True", True),
    ("str ''", ""),
    ("str 'hello'", "hello"),
    ("list []", []),
    ("list [1,2,3]", [1, 2, 3]),
    ("tuple ()", ()),
    ("tuple (1,2,3)", (1, 2, 3)),
    ("dict {}", {}),
    ("set()", set()),
    ("None", None),
]

for name, obj in objects:
    print(f"{name:15} -> {sys.getsizeof(obj)} bytes")

print("\n✅ Day 2 completed!")
