#!/usr/bin/env python3
"""Day 30 - Python Interview Questions (Advanced Level)"""

print("=" * 60)
print("PYTHON INTERVIEW QUESTIONS - ADVANCED")
print("=" * 60)


# ============================================
# SECTION 1: PYTHON INTERNALS
# ============================================
print("\n" + "=" * 60)
print("SECTION 1: PYTHON INTERNALS")
print("=" * 60)

print("""
Q1: How does Python's memory management work?
─────────────────────────────────────────────
A: - Private heap for all objects and data structures
   - Memory manager handles allocation
   - Reference counting: Each object tracks how many references point to it
   - Garbage collector: Handles circular references (generational GC)
   - Small integers (-5 to 256) and interned strings are cached

Q2: What is the GIL (Global Interpreter Lock)?
──────────────────────────────────────────────
A: - Mutex that allows only one thread to execute Python bytecode at a time
   - Exists in CPython (reference implementation)
   - Simplifies memory management (no race conditions for ref counting)
   - Impact: CPU-bound threads don't run in parallel
   - Workarounds: multiprocessing, asyncio, C extensions, PyPy

Q3: Explain Python's garbage collection
───────────────────────────────────────
A: Two mechanisms:
   1. Reference Counting (primary):
      - Each object has a counter
      - When counter reaches 0, memory is freed
      - Can't handle circular references
   
   2. Generational GC (cyclic garbage):
      - 3 generations (0, 1, 2)
      - Younger objects collected more frequently
      - Objects that survive move to older generation
""")

# Demo: Reference counting
import sys
print("\nDemo: Reference counting")
a = [1, 2, 3]
print(f"sys.getrefcount(a) = {sys.getrefcount(a)}")  # +1 for getrefcount param
b = a
print(f"After b=a: sys.getrefcount(a) = {sys.getrefcount(a)}")
del b
print(f"After del b: sys.getrefcount(a) = {sys.getrefcount(a)}")

print("""
Q4: What are descriptors?
─────────────────────────
A: Objects that define __get__, __set__, or __delete__
   - Data descriptors: define both __get__ and __set__
   - Non-data descriptors: only __get__
   - Used by: property, classmethod, staticmethod
""")

# Demo: Descriptor
class Validator:
    def __init__(self, min_value):
        self.min_value = min_value
        self.name = None
    
    def __set_name__(self, owner, name):
        self.name = name
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__.get(self.name)
    
    def __set__(self, obj, value):
        if value < self.min_value:
            raise ValueError(f"{self.name} must be >= {self.min_value}")
        obj.__dict__[self.name] = value

class Product:
    price = Validator(0)

print("\nDemo: Descriptor")
p = Product()
p.price = 10
print(f"p.price = {p.price}")
try:
    p.price = -5
except ValueError as e:
    print(f"Setting negative price: {e}")


# ============================================
# SECTION 2: ADVANCED OOP
# ============================================
print("\n" + "=" * 60)
print("SECTION 2: ADVANCED OOP")
print("=" * 60)

print("""
Q5: Explain Python's Method Resolution Order (MRO)
──────────────────────────────────────────────────
A: - Order in which Python searches for methods in class hierarchy
   - Uses C3 Linearization algorithm
   - Ensures:
     1. Subclass checked before parents
     2. Order of parents preserved
     3. Each class appears only once
   - Access via: Class.__mro__ or Class.mro()
""")

# Demo: MRO
class A:
    def method(self): return "A"

class B(A):
    def method(self): return "B"

class C(A):
    def method(self): return "C"

class D(B, C):
    pass

print("\nDemo: MRO")
print(f"D.__mro__ = {[c.__name__ for c in D.__mro__]}")
print(f"D().method() = '{D().method()}'")

print("""
Q6: What are metaclasses?
─────────────────────────
A: - Classes of classes (type is the default metaclass)
   - Control class creation and behavior
   - Use cases: ORMs, registries, validation, singletons
""")

# Demo: Metaclass
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Database(metaclass=SingletonMeta):
    def __init__(self):
        self.connection = "Connected"

print("\nDemo: Singleton Metaclass")
db1 = Database()
db2 = Database()
print(f"db1 is db2: {db1 is db2}")

print("""
Q7: What's the difference between __new__ and __init__?
───────────────────────────────────────────────────────
A: __new__: Creates the instance (receives class, returns instance)
   __init__: Initializes the instance (receives instance, returns None)
   
   Use __new__ for:
   - Immutable types (can't modify in __init__)
   - Singletons
   - Caching instances
""")


# ============================================
# SECTION 3: CONCURRENCY
# ============================================
print("\n" + "=" * 60)
print("SECTION 3: CONCURRENCY")
print("=" * 60)

print("""
Q8: Threading vs Multiprocessing vs Asyncio?
────────────────────────────────────────────
A: Threading (concurrent, same memory):
   - Multiple threads, shared memory
   - GIL limits CPU parallelism
   - Good for: I/O-bound with shared state
   
   Multiprocessing (parallel, separate memory):
   - Multiple processes, separate memory
   - True parallelism (bypasses GIL)
   - Good for: CPU-bound tasks
   - Higher memory overhead
   
   Asyncio (concurrent, single thread):
   - Single thread, event loop
   - Cooperative multitasking (await)
   - Good for: Many I/O-bound tasks
   - Lower overhead than threading

Q9: What is a race condition?
─────────────────────────────
A: When outcome depends on timing of thread execution
   Solution: Locks, semaphores, atomic operations
""")

import threading
import time

print("\nDemo: Race Condition")
counter = 0

def increment():
    global counter
    for _ in range(100000):
        counter += 1

threads = [threading.Thread(target=increment) for _ in range(2)]
for t in threads: t.start()
for t in threads: t.join()
print(f"Expected: 200000, Got: {counter} (race condition!)")

# With lock
counter = 0
lock = threading.Lock()

def safe_increment():
    global counter
    for _ in range(100000):
        with lock:
            counter += 1

threads = [threading.Thread(target=safe_increment) for _ in range(2)]
for t in threads: t.start()
for t in threads: t.join()
print(f"With lock: {counter}")

print("""
Q10: Explain async/await
────────────────────────
A: - async def: Defines coroutine function
   - await: Suspends execution until awaitable completes
   - Event loop: Manages coroutine execution
   - Benefits: Efficient I/O, no context switching overhead
""")


# ============================================
# SECTION 4: DESIGN PATTERNS
# ============================================
print("\n" + "=" * 60)
print("SECTION 4: DESIGN PATTERNS")
print("=" * 60)

print("""
Q11: Explain SOLID principles
─────────────────────────────
A: S - Single Responsibility: One class, one purpose
   O - Open/Closed: Open for extension, closed for modification
   L - Liskov Substitution: Subtypes must be substitutable
   I - Interface Segregation: Many specific interfaces > one general
   D - Dependency Inversion: Depend on abstractions, not concretions

Q12: Common Python design patterns?
───────────────────────────────────
A: Creational:
   - Singleton (one instance)
   - Factory (create objects without specifying class)
   - Builder (step-by-step construction)
   
   Structural:
   - Decorator (add behavior dynamically)
   - Adapter (convert interface)
   - Facade (simplified interface)
   
   Behavioral:
   - Observer (pub/sub)
   - Strategy (interchangeable algorithms)
   - Command (encapsulate requests)
""")

# Demo: Factory Pattern
print("\nDemo: Factory Pattern")
class Animal:
    def speak(self): pass

class Dog(Animal):
    def speak(self): return "Woof!"

class Cat(Animal):
    def speak(self): return "Meow!"

def animal_factory(animal_type):
    animals = {"dog": Dog, "cat": Cat}
    return animals.get(animal_type.lower(), Animal)()

dog = animal_factory("dog")
print(f"animal_factory('dog').speak() = '{dog.speak()}'")

# Demo: Strategy Pattern
print("\nDemo: Strategy Pattern")
from abc import ABC, abstractmethod

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount): pass

class CreditCard(PaymentStrategy):
    def pay(self, amount): return f"Paid ${amount} with credit card"

class PayPal(PaymentStrategy):
    def pay(self, amount): return f"Paid ${amount} with PayPal"

class Order:
    def __init__(self, strategy: PaymentStrategy):
        self.strategy = strategy
    
    def checkout(self, amount):
        return self.strategy.pay(amount)

order = Order(PayPal())
print(f"order.checkout(100) = '{order.checkout(100)}'")


# ============================================
# SECTION 5: PERFORMANCE
# ============================================
print("\n" + "=" * 60)
print("SECTION 5: PERFORMANCE")
print("=" * 60)

print("""
Q13: How do you profile Python code?
────────────────────────────────────
A: Time profiling:
   - timeit: Quick timing
   - cProfile: Function call profiling
   - line_profiler: Line-by-line
   
   Memory profiling:
   - memory_profiler: Line-by-line memory
   - tracemalloc: Memory allocation tracking
   - sys.getsizeof(): Object size

Q14: Common Python optimizations?
─────────────────────────────────
A: - Use built-in functions (map, filter, sorted)
   - List comprehensions over loops
   - Generator expressions for large data
   - Local variables are faster than global
   - Use slots for memory-efficient classes
   - Use sets for membership testing
   - Cache with functools.lru_cache
""")

# Demo: __slots__
print("\nDemo: __slots__ memory savings")
import sys

class RegularClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SlottedClass:
    __slots__ = ['x', 'y']
    def __init__(self, x, y):
        self.x = x
        self.y = y

regular = RegularClass(1, 2)
slotted = SlottedClass(1, 2)
print(f"Regular: has __dict__: {hasattr(regular, '__dict__')}")
print(f"Slotted: has __dict__: {hasattr(slotted, '__dict__')}")

# Demo: lru_cache
print("\nDemo: lru_cache")
from functools import lru_cache

@lru_cache(maxsize=128)
def fib(n):
    if n < 2:
        return n
    return fib(n-1) + fib(n-2)

import time
start = time.time()
result = fib(35)
print(f"fib(35) = {result}, time: {time.time()-start:.4f}s (cached)")


# ============================================
# SECTION 6: ADVANCED TOPICS
# ============================================
print("\n" + "=" * 60)
print("SECTION 6: ADVANCED TOPICS")
print("=" * 60)

print("""
Q15: What are context managers?
───────────────────────────────
A: Objects that implement __enter__ and __exit__
   - Ensure cleanup (file closing, lock releasing)
   - Use 'with' statement
   - Can use contextlib.contextmanager decorator
""")

from contextlib import contextmanager

@contextmanager
def timer():
    start = time.time()
    yield
    print(f"Elapsed: {time.time() - start:.4f}s")

print("\nDemo: Context Manager")
with timer():
    sum(range(1000000))

print("""
Q16: Explain Python's iteration protocol
────────────────────────────────────────
A: Iterator protocol:
   - __iter__(): Returns iterator object
   - __next__(): Returns next value or raises StopIteration
   
   Iterable: Has __iter__() that returns iterator
   Iterator: Has both __iter__() and __next__()
   Generator: Function with yield (creates iterator)
""")

# Demo: Custom iterator
print("\nDemo: Custom Iterator")
class CountDown:
    def __init__(self, start):
        self.start = start
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.start <= 0:
            raise StopIteration
        self.start -= 1
        return self.start + 1

print("CountDown(5):", list(CountDown(5)))

print("""
Q17: What are coroutines vs generators?
───────────────────────────────────────
A: Generators (yield):
   - Produce values (yield sends data out)
   - Can receive via send()
   - Single-way communication primarily
   
   Coroutines (async/await):
   - Await other coroutines
   - Designed for async I/O
   - Native support in asyncio
""")


# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 60)
print("KEY ADVANCED TOPICS")
print("=" * 60)
print("""
1. GIL and its implications
2. Memory management & garbage collection
3. Metaclasses and descriptors
4. MRO and multiple inheritance
5. Threading vs multiprocessing vs asyncio
6. Design patterns in Python
7. Performance optimization techniques
8. Context managers and protocols
9. Decorators (class and function)
10. Type hints and generics
""")
