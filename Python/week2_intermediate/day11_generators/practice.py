#!/usr/bin/env python3
"""Day 11 - Generators & Iterators Deep Dive"""

import sys
from typing import Generator, Iterator, Iterable

print("=" * 50)
print("GENERATORS & ITERATORS")
print("=" * 50)

# ============================================
# 1. BASIC GENERATOR
# ============================================
print("\n--- 1. BASIC GENERATOR ---")


def count_up_to(n: int) -> Generator[int, None, None]:
    """Generator that counts from 1 to n"""
    i = 1
    while i <= n:
        yield i
        i += 1


# Using the generator
counter = count_up_to(5)
print(f"Generator object: {counter}")
print(f"Type: {type(counter)}")

# Iterate with for loop
print("Values:", end=" ")
for num in count_up_to(5):
    print(num, end=" ")
print()


# ============================================
# 2. GENERATOR VS LIST - MEMORY
# ============================================
print("\n--- 2. MEMORY COMPARISON ---")


def get_squares_list(n: int) -> list:
    return [x**2 for x in range(n)]


def get_squares_gen(n: int) -> Generator[int, None, None]:
    for x in range(n):
        yield x**2


n = 1000000

# Compare memory
gen = get_squares_gen(n)
# lst = get_squares_list(n)  # Would use ~36MB

print(f"Generator size: {sys.getsizeof(gen)} bytes")
# Commenting out to avoid memory usage
# print(f"List size: {sys.getsizeof(lst)} bytes")
print(f"List of {n} ints would use: ~{n * 28 // 1024 // 1024}MB")


# ============================================
# 3. ITER() AND NEXT()
# ============================================
print("\n--- 3. ITER() AND NEXT() ---")

# Every iterable has __iter__ method
my_list = [1, 2, 3]
iterator = iter(my_list)

print(f"Iterator: {iterator}")
print(f"next(): {next(iterator)}")
print(f"next(): {next(iterator)}")
print(f"next(): {next(iterator)}")

# StopIteration when exhausted
try:
    next(iterator)
except StopIteration:
    print("StopIteration raised!")

# Default value for next()
iterator2 = iter([1])
print(f"next() with default: {next(iterator2, 'default')}")
print(f"next() with default: {next(iterator2, 'default')}")


# ============================================
# 4. CUSTOM ITERATOR
# ============================================
print("\n--- 4. CUSTOM ITERATOR ---")


class Countdown:
    """Custom iterator that counts down"""
    
    def __init__(self, start: int):
        self.current = start
    
    def __iter__(self) -> Iterator[int]:
        return self
    
    def __next__(self) -> int:
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1


print("Countdown:")
for num in Countdown(5):
    print(f"  {num}")


# ============================================
# 5. GENERATOR EXPRESSIONS
# ============================================
print("\n--- 5. GENERATOR EXPRESSIONS ---")

# List comprehension
squares_list = [x**2 for x in range(10)]
print(f"List: {squares_list}")

# Generator expression
squares_gen = (x**2 for x in range(10))
print(f"Generator: {squares_gen}")
print(f"List from generator: {list(squares_gen)}")

# With condition
even_squares = (x**2 for x in range(20) if x % 2 == 0)
print(f"Even squares: {list(even_squares)}")

# Useful for large data
total = sum(x**2 for x in range(10000))
print(f"Sum of squares (0-9999): {total}")


# ============================================
# 6. YIELD FROM
# ============================================
print("\n--- 6. YIELD FROM ---")


def flatten(nested: list) -> Generator:
    """Flatten nested list using yield from"""
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item


nested = [1, [2, 3, [4, 5]], 6, [7, [8, 9]]]
print(f"Nested: {nested}")
print(f"Flattened: {list(flatten(nested))}")


def chain(*iterables):
    """Chain multiple iterables"""
    for it in iterables:
        yield from it


result = list(chain([1, 2], [3, 4], [5, 6]))
print(f"Chained: {result}")


# ============================================
# 7. GENERATOR METHODS
# ============================================
print("\n--- 7. GENERATOR METHODS ---")


def accumulator():
    """Generator that accumulates values sent to it"""
    total = 0
    while True:
        value = yield total
        if value is not None:
            total += value


acc = accumulator()
print(f"Initialize (next): {next(acc)}")
print(f"Send 10: {acc.send(10)}")
print(f"Send 20: {acc.send(20)}")
print(f"Send 5: {acc.send(5)}")


# throw() - inject exception
def careful_gen():
    try:
        while True:
            yield "running"
    except ValueError:
        yield "caught ValueError"
    finally:
        print("  Generator cleanup")


gen = careful_gen()
print(f"\nthrow() example:")
print(f"  next(): {next(gen)}")
print(f"  throw(): {gen.throw(ValueError)}")


# close() - stop generator
gen2 = careful_gen()
next(gen2)
print("\nclose() example:")
gen2.close()  # Triggers finally block


# ============================================
# 8. INFINITE GENERATORS
# ============================================
print("\n--- 8. INFINITE GENERATORS ---")


def infinite_counter(start: int = 0):
    """Infinite counter"""
    n = start
    while True:
        yield n
        n += 1


def fibonacci():
    """Infinite Fibonacci sequence"""
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


# Take first N items from infinite generator
from itertools import islice

print(f"First 10 Fibonacci: {list(islice(fibonacci(), 10))}")
print(f"Counter from 100: {list(islice(infinite_counter(100), 5))}")


# ============================================
# 9. PRACTICAL EXAMPLES
# ============================================
print("\n--- 9. PRACTICAL EXAMPLES ---")


# File reader (memory efficient for large files)
def read_large_file(file_path: str, chunk_size: int = 1024):
    """Read file in chunks"""
    with open(file_path, 'r') as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


# Pipeline processing
def numbers():
    for i in range(10):
        yield i


def squared(nums):
    for n in nums:
        yield n ** 2


def filtered(nums, threshold):
    for n in nums:
        if n > threshold:
            yield n


# Compose pipeline
pipeline = filtered(squared(numbers()), 20)
print(f"Pipeline (numbers > 20 when squared): {list(pipeline)}")


# Coroutine pattern
def grep(pattern: str):
    """Filter lines containing pattern"""
    print(f"  Looking for: {pattern}")
    while True:
        line = yield
        if pattern in line:
            print(f"  Found: {line}")


search = grep("Python")
next(search)  # Prime the generator
search.send("Hello World")
search.send("Python is great")
search.send("I love Python")
search.send("Goodbye")


# ============================================
# 10. ITERTOOLS HIGHLIGHTS
# ============================================
print("\n--- 10. ITERTOOLS HIGHLIGHTS ---")

import itertools

# count - infinite counter
print(f"count(10, 2): {list(itertools.islice(itertools.count(10, 2), 5))}")

# cycle - infinite cycle
colors = itertools.cycle(['red', 'green', 'blue'])
print(f"cycle colors: {[next(colors) for _ in range(7)]}")

# repeat
print(f"repeat('x', 5): {list(itertools.repeat('x', 5))}")

# chain
print(f"chain: {list(itertools.chain([1,2], [3,4], [5,6]))}")

# combinations & permutations
print(f"combinations: {list(itertools.combinations('ABC', 2))}")
print(f"permutations: {list(itertools.permutations('AB', 2))}")

# groupby
data = [('A', 1), ('A', 2), ('B', 3), ('B', 4)]
for key, group in itertools.groupby(data, key=lambda x: x[0]):
    print(f"  {key}: {list(group)}")


print("\n✅ Day 11 completed!")
