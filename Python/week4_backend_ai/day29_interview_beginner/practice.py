#!/usr/bin/env python3
"""Day 29 - Python Interview Questions (Beginner Level)"""

print("=" * 60)
print("PYTHON INTERVIEW QUESTIONS - BEGINNER")
print("=" * 60)


# ============================================
# SECTION 1: PYTHON BASICS
# ============================================
print("\n" + "=" * 60)
print("SECTION 1: PYTHON BASICS")
print("=" * 60)

print("""
Q1: What are Python's key features?
─────────────────────────────────
A: - Interpreted language (no compilation)
   - Dynamically typed
   - High-level, readable syntax
   - Object-oriented and functional
   - Large standard library
   - Garbage collected
   - Cross-platform

Q2: What's the difference between Python 2 and 3?
─────────────────────────────────────────────────
A: - print is a function in Python 3: print()
   - Integer division: 5/2 = 2.5 (Py3) vs 2 (Py2)
   - Unicode strings by default in Python 3
   - range() returns iterator in Python 3
   - Python 2 reached end-of-life in 2020

Q3: What is PEP 8?
──────────────────
A: Python Enhancement Proposal 8 - the style guide for Python code.
   Key rules:
   - 4 spaces for indentation
   - Max line length: 79 characters
   - snake_case for functions/variables
   - CamelCase for classes
   - UPPER_CASE for constants

Q4: What are Python's built-in data types?
──────────────────────────────────────────
A: Numeric: int, float, complex
   Sequence: str, list, tuple, range
   Mapping: dict
   Set: set, frozenset
   Boolean: bool
   Binary: bytes, bytearray
   None: NoneType
""")


# ============================================
# SECTION 2: DATA TYPES & VARIABLES
# ============================================
print("\n" + "=" * 60)
print("SECTION 2: DATA TYPES & VARIABLES")
print("=" * 60)

print("""
Q5: What's the difference between mutable and immutable?
────────────────────────────────────────────────────────
A: Mutable: Can be changed after creation
   - list, dict, set, bytearray
   
   Immutable: Cannot be changed after creation
   - int, float, str, tuple, frozenset
""")

# Demo
print("Demo: Mutable vs Immutable")
a = [1, 2, 3]
b = a
b.append(4)
print(f"List (mutable): a={a}, b={b}  # Both changed!")

x = "hello"
y = x
y = y + " world"
print(f"String (immutable): x='{x}', y='{y}'  # Original unchanged")

print("""
Q6: What's the difference between == and is?
────────────────────────────────────────────
A: == compares values (equality)
   is compares identity (same object in memory)
""")

# Demo
a = [1, 2, 3]
b = [1, 2, 3]
c = a
print(f"\na=[1,2,3], b=[1,2,3], c=a")
print(f"a == b: {a == b}")  # True (same values)
print(f"a is b: {a is b}")  # False (different objects)
print(f"a is c: {a is c}")  # True (same object)

print("""
Q7: What are *args and **kwargs?
────────────────────────────────
A: *args: Variable positional arguments (tuple)
   **kwargs: Variable keyword arguments (dict)
""")

def demo_func(*args, **kwargs):
    print(f"args: {args}")
    print(f"kwargs: {kwargs}")

print("\ndemo_func(1, 2, 3, name='Python', version=3)")
demo_func(1, 2, 3, name='Python', version=3)


# ============================================
# SECTION 3: DATA STRUCTURES
# ============================================
print("\n" + "=" * 60)
print("SECTION 3: DATA STRUCTURES")
print("=" * 60)

print("""
Q8: List vs Tuple vs Set vs Dict?
─────────────────────────────────
A: List []: Ordered, mutable, allows duplicates, indexed
   Tuple (): Ordered, immutable, allows duplicates, indexed
   Set {}: Unordered, mutable, NO duplicates, not indexed
   Dict {k:v}: Ordered (3.7+), mutable, unique keys

Q9: What's a list comprehension?
────────────────────────────────
A: Concise way to create lists:
   [expression for item in iterable if condition]
""")

# Demo
squares = [x**2 for x in range(5)]
evens = [x for x in range(10) if x % 2 == 0]
print(f"Squares: {squares}")
print(f"Evens: {evens}")

print("""
Q10: How do you remove duplicates from a list?
──────────────────────────────────────────────
A: Use set() - but loses order
   Use dict.fromkeys() - preserves order
""")

# Demo
nums = [1, 2, 2, 3, 3, 3, 4]
unique1 = list(set(nums))
unique2 = list(dict.fromkeys(nums))
print(f"Original: {nums}")
print(f"set(): {unique1}")
print(f"dict.fromkeys(): {unique2}")


# ============================================
# SECTION 4: FUNCTIONS
# ============================================
print("\n" + "=" * 60)
print("SECTION 4: FUNCTIONS")
print("=" * 60)

print("""
Q11: What's a lambda function?
──────────────────────────────
A: Anonymous, single-expression function:
   lambda arguments: expression
""")

# Demo
square = lambda x: x ** 2
add = lambda a, b: a + b
print(f"lambda x: x**2 -> square(5) = {square(5)}")
print(f"lambda a,b: a+b -> add(3,4) = {add(3,4)}")

print("""
Q12: Explain map(), filter(), reduce()
──────────────────────────────────────
A: map(): Apply function to each item
   filter(): Keep items where function returns True
   reduce(): Cumulative application (from functools)
""")

# Demo
nums = [1, 2, 3, 4, 5]
mapped = list(map(lambda x: x*2, nums))
filtered = list(filter(lambda x: x > 2, nums))
from functools import reduce
reduced = reduce(lambda a, b: a + b, nums)

print(f"nums = {nums}")
print(f"map(x*2): {mapped}")
print(f"filter(x>2): {filtered}")
print(f"reduce(a+b): {reduced}")

print("""
Q13: What's the difference between global and local variables?
──────────────────────────────────────────────────────────────
A: Local: Defined inside function, only accessible there
   Global: Defined outside functions, accessible everywhere
   Use 'global' keyword to modify global var inside function
""")

# Demo
x = "global"
def demo():
    x = "local"
    print(f"Inside function: x = '{x}'")

demo()
print(f"Outside function: x = '{x}'")


# ============================================
# SECTION 5: OOP BASICS
# ============================================
print("\n" + "=" * 60)
print("SECTION 5: OOP BASICS")
print("=" * 60)

print("""
Q14: What are the four pillars of OOP?
──────────────────────────────────────
A: 1. Encapsulation: Bundling data and methods
   2. Inheritance: Creating new class from existing
   3. Polymorphism: Same interface, different behavior
   4. Abstraction: Hiding complexity, showing essentials

Q15: What's the difference between a class and an object?
─────────────────────────────────────────────────────────
A: Class: Blueprint/template (e.g., Car)
   Object: Instance of a class (e.g., my_car = Car())

Q16: What are __init__ and self?
────────────────────────────────
A: __init__: Constructor method, called when object created
   self: Reference to the current instance
""")

# Demo
class Dog:
    def __init__(self, name):
        self.name = name  # Instance attribute
    
    def bark(self):
        return f"{self.name} says woof!"

dog = Dog("Buddy")
print(f"\nclass Dog with __init__:")
print(f"dog.name = '{dog.name}'")
print(f"dog.bark() = '{dog.bark()}'")

print("""
Q17: What are class vs instance attributes?
───────────────────────────────────────────
A: Class attribute: Shared by all instances
   Instance attribute: Unique to each instance
""")

# Demo
class Counter:
    count = 0  # Class attribute
    
    def __init__(self, name):
        self.name = name  # Instance attribute
        Counter.count += 1

c1 = Counter("A")
c2 = Counter("B")
print(f"\nCounter.count (class attr): {Counter.count}")
print(f"c1.name (instance attr): '{c1.name}'")


# ============================================
# SECTION 6: COMMON QUESTIONS
# ============================================
print("\n" + "=" * 60)
print("SECTION 6: COMMON QUESTIONS")
print("=" * 60)

print("""
Q18: How do you handle exceptions?
──────────────────────────────────
A: try-except-else-finally block
   - try: Code that might raise exception
   - except: Handle specific exceptions
   - else: Runs if no exception
   - finally: Always runs (cleanup)
""")

# Demo
def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        return "Cannot divide by zero!"
    else:
        return result
    finally:
        print("Division attempted")

print(f"\ndivide(10, 2):")
print(divide(10, 2))
print(f"\ndivide(10, 0):")
print(divide(10, 0))

print("""
Q19: What's the difference between append() and extend()?
─────────────────────────────────────────────────────────
A: append(): Adds one element to end
   extend(): Adds all elements from iterable
""")

# Demo
a = [1, 2]
b = [1, 2]
a.append([3, 4])
b.extend([3, 4])
print(f"\nappend([3,4]): {a}")
print(f"extend([3,4]): {b}")

print("""
Q20: How do you copy a list?
────────────────────────────
A: Shallow copy (new list, same objects):
   - list.copy(), list[:], list(original)
   
   Deep copy (new list, new objects):
   - copy.deepcopy()
""")

import copy
original = [[1, 2], [3, 4]]
shallow = original.copy()
deep = copy.deepcopy(original)

original[0][0] = 'X'
print(f"\noriginal = [[1,2],[3,4]], then original[0][0]='X'")
print(f"Original: {original}")
print(f"Shallow copy: {shallow}")  # Also changed!
print(f"Deep copy: {deep}")  # Unchanged


# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 60)
print("KEY TAKEAWAYS")
print("=" * 60)
print("""
1. Know the difference between mutable/immutable
2. Understand == vs is
3. Master list comprehensions
4. Know *args and **kwargs
5. Understand class vs instance attributes
6. Know shallow vs deep copy
7. Be comfortable with exception handling
8. Practice coding problems!
""")
