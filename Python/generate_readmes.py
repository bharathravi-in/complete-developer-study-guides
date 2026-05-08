#!/usr/bin/env python3
"""
Generate comprehensive README files for Python learning materials
"""

import os

# Template for comprehensive README structure
README_TEMPLATE = """# Day {day_num} - {title}

## Table of Contents
- [Overview](#overview)
{toc_sections}
- [Best Practices](#best-practices)
- [Interview Preparation](#interview-preparation)
- [Practice Exercises](#practice-exercises)

---

## Overview

{overview_content}

---

{main_content}

---

## Best Practices

{best_practices}

---

## Interview Preparation

{interview_questions}

---

## Practice Exercises

{practice_exercises}

---

## Run
```bash
python practice.py
```

## Additional Resources

{resources}

---

## Key Takeaways

{key_takeaways}
"""

# Day-specific content configuration
CONTENT_CONFIG = {
    "day03_controlflow": {
        "title": "Control Flow",
        "overview": """Control flow structures determine the order in which code executes. Python provides several control flow statements including conditionals (if-elif-else), loops (for, while), and control statements (break, continue, pass). Understanding these is essential for writing logic and handling different scenarios in your programs.""",
        "sections": ["Conditional Statements", "Loops", "Loop Control", "Pattern Matching"],
        "key_takeaways": [
            "Use if-elif-else for conditional logic",
            "for loops iterate over sequences, while loops continue until condition is False",
            "break exits loop, continue skips to next iteration",
            "match-case provides pattern matching (Python 3.10+)",
            "Truthy/Falsy values: False, None, 0, '', [], {}, set() are falsy",
            "List comprehensions are faster than loops for creating lists",
            "Loop else clause runs only if loop completes without break",
            "Use enumerate() for index and value in loops"
        ]
    },
    "day05_datastructures": {
        "title": "Data Structures in Python",
        "overview": """Master Python's built-in data structures and their operations. Learn list methods, dictionary operations, set theory, tuple unpacking, and comprehensions. Understanding when and how to use each data structure efficiently is crucial for writing performant Python code.""",
        "sections": ["List Operations", "Dictionary Methods", "Set Operations", "Comprehensions"],
        "key_takeaways": [
            "Lists are versatile ordered collections (append, extend, insert, etc.)",
            "Dicts provide O(1) lookup with key-value pairs",
            "Sets offer fast membership testing and mathematical operations",
            "Comprehensions are more Pythonic than traditional loops",
            "Use setdefault() and defaultdict for safe dictionary access",
            "Counter is perfect for counting hashable objects",
            "Deque provides O(1) operations at both ends",
            "Choose the right data structure for the task"
        ]
    },
    "day06_errorhandling": {
        "title": "Error Handling & Exceptions",
        "overview": """Learn to handle errors gracefully using Python's exception handling mechanism. Understand try-except-finally blocks, raising exceptions, creating custom exceptions, and following best practices for error handling. Proper error handling makes your code robust and user-friendly.""",
        "sections": ["Exception Basics", "Try-Except-Finally", "Raising Exceptions", "Custom Exceptions"],
        "key_takeaways": [
            "Always catch specific exceptions, not bare except:",
            "Use finally for cleanup (file closing, connection closing)",
            "else clause runs only if no exception occurred",
            "Create custom exceptions for domain-specific errors",
            "Use raise to re-raise exceptions or raise new ones",
            "Context managers (with statement) handle cleanup automatically",
            "Never catch SystemExit or KeyboardInterrupt",
            "Log exceptions instead of silently catching them"
        ]
    },
    "day07_modules": {
        "title": "Modules & Packages",
        "overview": """Learn to organize code into reusable modules and packages. Understand import statements, package structure, __init__.py files, and relative/absolute imports. Mastering modules and packages is essential for building maintainable, scalable Python applications.""",
        "sections": ["Import Statements", "Creating Modules", "Package Structure", "Best Practices"],
        "key_takeaways": [
            "Module = single .py file, Package = directory with __init__.py",
            "Use 'if __name__ == \"__main__\":' for executable scripts",
            "Absolute imports are clearer than relative imports",
            "Avoid circular imports by restructuring code",
            "Use __all__ to control 'from module import *'",
            "Virtual environments isolate project dependencies",
            "requirements.txt tracks project dependencies",
            "Organize code into logical modules for maintainability"
        ]
    },
}

def generate_day03_content():
    """Generate comprehensive content for Day 3 - Control Flow"""
    return """
## Conditional Statements

### if-elif-else

```python
# Basic if statement
age = 18
if age >= 18:
    print("Adult")

# if-else
temperature = 25
if temperature > 30:
    print("Hot")
else:
    print("Pleasant")

# if-elif-else (chain)
score = 85
if score >= 90:
    grade = 'A'
elif score >= 80:
    grade = 'B'
elif score >= 70:
    grade = 'C'
elif score >= 60:
    grade = 'D'
else:
    grade = 'F'

print(f"Grade: {grade}")
```

### Ternary Operator (Conditional Expression)

```python
# Syntax: value_if_true if condition else value_if_false
age = 20
status = "Adult" if age >= 18 else "Minor"

# Nested ternary (avoid for readability)
value = "positive" if x > 0 else "zero" if x == 0 else "negative"

# Better: use regular if-elif-else for complex logic
```

### Truthy and Falsy Values

```python
# Falsy values (evaluate to False)
values = [False, None, 0, 0.0, 0j, '', [], (), {}, set()]

for val in values:
    if not val:
        print(f"{repr(val)} is falsy")

# Everything else is truthy
if [1, 2]:  # Non-empty list is truthy
    print("This will print")

# Common pattern: check if collection is not empty
items = [1, 2, 3]
if items:
    print(f"Processing {len(items)} items")
else:
    print("No items to process")
```

### Match-Case (Python 3.10+)

Pattern matching for more readable complex conditionals.

```python
# Basic match-case
def http_status(status):
    match status:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500:
            return "Internal Server Error"
        case _:  # Default case
            return "Unknown Status"

# Pattern matching with conditions
def describe_point(point):
    match point:
        case (0, 0):
            return "Origin"
        case (0, y):
            return f"Y-axis at y={y}"
        case (x, 0):
            return f"X-axis at x={x}"
        case (x, y):
            return f"Point at ({x}, {y})"

# Match with classes
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def describe(obj):
    match obj:
        case Point(x=0, y=0):
            return "Origin"
        case Point(x=0, y=y):
            return f"On Y axis: {y}"
        case Point(x=x, y=0):
            return f"On X axis: {x}"
        case Point():
            return f"Point: {obj.x}, {obj.y}"
        case _:
            return "Not a point"

# Guard clauses
def categorize_number(x):
    match x:
        case n if n < 0:
            return "Negative"
        case 0:
            return "Zero"
        case n if n > 100:
            return "Large positive"
        case _:
            return "Positive"
```

---

## Loops

### for Loop

Iterate over sequences (lists, strings, ranges, etc.)

```python
# Iterate over list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Iterate over string
for char in "Python":
    print(char)

# Iterate over range
for i in range(5):  # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 10, 2):  # start, stop, step
    print(i)  # 2, 4, 6, 8

# Enumerate: get index and value
for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")

# Enumerate with custom start
for index, fruit in enumerate(fruits, start=1):
    print(f"{index}. {fruit}")

# Iterate over dictionary
person = {"name": "Alice", "age": 30, "city": "NYC"}

# Keys only (default)
for key in person:
    print(key)

# Keys explicitly
for key in person.keys():
    print(key)

# Values only
for value in person.values():
    print(value)

# Key-value pairs
for key, value in person.items():
    print(f"{key}: {value}")

# Zip: iterate over multiple sequences
names = ["Alice", "Bob", "Charlie"]
ages = [30, 25, 35]
cities = ["NYC", "LA", "Chicago"]

for name, age, city in zip(names, ages, cities):
    print(f"{name} ({age}) from {city}")

# Reverse iteration
for i in reversed(range(5)):
    print(i)  # 4, 3, 2, 1, 0

for fruit in reversed(fruits):
    print(fruit)

# Sorted iteration (doesn't modify original)
numbers = [3, 1, 4, 1, 5]
for num in sorted(numbers):
    print(num)  # 1, 1, 3, 4, 5
```

### while Loop

Continue until condition becomes False.

```python
# Basic while loop
count = 0
while count < 5:
    print(count)
    count += 1

# User input loop
while True:
    user_input = input("Enter 'quit' to exit: ")
    if user_input.lower() == 'quit':
        break
    print(f"You entered: {user_input}")

# Countdown
n = 5
while n > 0:
    print(n)
    n -= 1
print("Blast off!")

# While with else
attempts = 0
max_attempts = 3

while attempts < max_attempts:
    password = input("Enter password: ")
    if password == "secret":
        print("Access granted!")
        break
    attempts += 1
else:
    # Executes if loop completes without break
    print("Too many failed attempts. Access denied.")
```

---

## Loop Control

### break Statement

Exit loop immediately.

```python
# Find first even number
numbers = [1, 3, 5, 8, 9, 10]
for num in numbers:
    if num % 2 == 0:
        print(f"First even: {num}")
        break

# Search in nested loop
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

target = 5
found = False

for row in matrix:
    for item in row:
        if item == target:
            print(f"Found {target}")
            found = True
            break
    if found:
        break
```

### continue Statement

Skip to next iteration.

```python
# Skip negative numbers
numbers = [1, -2, 3, -4, 5]
for num in numbers:
    if num < 0:
        continue
    print(num)  # Only positive numbers

# Skip specific values
for i in range(10):
    if i == 3 or i == 7:
        continue
    print(i)
```

### pass Statement

Do nothing (placeholder).

```python
# Placeholder for future implementation
def future_function():
    pass  # TODO: implement later

# Empty loop body
for i in range(5):
    pass  # Do nothing, just loop

# Empty class
class EmptyClass:
    pass

# Conditional placeholder
if condition:
    pass  # Will implement later
else:
    handle_case()
```

### Loop else Clause

Execute code if loop completes without break.

```python
# Check if number is prime
def is_prime(n):
    if n < 2:
        return False
    
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            print(f"{n} is divisible by {i}")
            break
    else:
        # Executes only if loop completes without break
        print(f"{n} is prime")
        return True
    
    return False

is_prime(17)  # Prime
is_prime(15)  # Not prime

# Search in list
def find_item(items, target):
    for item in items:
        if item == target:
            print(f"Found: {target}")
            break
    else:
        print(f"Not found: {target}")

find_item([1, 2, 3, 4], 3)  # Found
find_item([1, 2, 3, 4], 5)  # Not found
```

---

## Best Practices

```python
# ✅ Use for loop for known iterations
for i in range(10):
    process(i)

# ❌ Don't use while for known iterations
i = 0
while i < 10:
    process(i)
    i += 1

# ✅ Use enumerate for index and value
for i, value in enumerate(my_list):
    print(f"{i}: {value}")

# ❌ Don't manually track index
i = 0
for value in my_list:
    print(f"{i}: {value}")
    i += 1

# ✅ Comprehensions for simple transformations
squares = [x**2 for x in range(10)]

# ❌ Don't use loop for simple comprehension
squares = []
for x in range(10):
    squares.append(x**2)

# ✅ Use match-case for complex conditionals (Python 3.10+)
match status_code:
    case 200:
        handle_success()
    case 404:
        handle_not_found()
    case int(x) if 500 <= x < 600:
        handle_server_error()

# ❌ Deep if-elif chains (less readable)
if status_code == 200:
    handle_success()
elif status_code == 404:
    handle_not_found()
elif 500 <= status_code < 600:
    handle_server_error()
```

---

## Interview Preparation

### Q1: FizzBuzz Problem

**Question:** Print numbers 1-100. For multiples of 3 print "Fizz", multiples of 5 print "Buzz", multiples of both print "FizzBuzz".

**Solution:**
```python
def fizzbuzz(n=100):
    for i in range(1, n + 1):
        if i % 15 == 0:  # Multiple of both 3 and 5
            print("FizzBuzz")
        elif i % 3 == 0:
            print("Fizz")
        elif i % 5 == 0:
            print("Buzz")
        else:
            print(i)

# Alternative with list
def fizzbuzz_list(n=100):
    result = []
    for i in range(1, n + 1):
        output ''
        if i % 3 == 0:
            output += "Fizz"
        if i % 5 == 0:
            output += "Buzz"
        result.append(output or i)
    return result
```

### Q2: Check if a number is prime

**Solution:**
```python
def is_prime(n):
    """Check if n is a prime number"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    
    # Check odd divisors up to sqrt(n)
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    
    return True

# Test
print([i for i in range(30) if is_prime(i)])
# [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
```

### Q3: Find all primes up to n (Sieve of Eratosthenes)

**Solution:**
```python
def sieve_of_eratosthenes(n):
    """Find all primes up to n efficiently"""
    if n < 2:
        return []
    
    # Create boolean array, initially all True
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    
    # Start with 2
    p = 2
    while p * p <= n:
        if is_prime[p]:
            # Mark multiples as not prime
            for i in range(p * p, n + 1, p):
                is_prime[i] = False
        p += 1
    
    # Collect all primes
    return [i for i, prime in enumerate(is_prime) if prime]

print(sieve_of_eratosthenes(50))
```

### Q4: Pattern printing

**Question:** Print various patterns using loops.

**Solution:**
```python
# Right triangle
def triangle(n):
    for i in range(1, n + 1):
        print('*' * i)

# Pyramid
def pyramid(n):
    for i in range(1, n + 1):
        spaces = ' ' * (n - i)
        stars = '*' * (2 * i - 1)
        print(spaces + stars)

# Diamond
def diamond(n):
    # Upper half
    for i in range(1, n + 1):
        print(' ' * (n - i) + '*' * (2 * i - 1))
    # Lower half
    for i in range(n - 1, 0, -1):
        print(' ' * (n - i) + '*' * (2 * i - 1))

triangle(5)
pyramid(5)
diamond(5)
```

---

## Practice Exercises

### Exercise 1: Number Guessing Game
Create a guessing game where the computer picks a random number and the user has to guess it.

### Exercise 2: Print all prime numbers between 1 and 100

### Exercise 3: Multiplication table generator

<details>
<summary>Solutions</summary>

```python
# Number guessing game
import random

def guessing_game():
    number = random.randint(1, 100)
    attempts = 0
    max_attempts = 10
    
    print("Guess a number between 1 and 100!")
    
    while attempts < max_attempts:
        guess = int(input(f"Attempt {attempts + 1}/{max_attempts}: "))
        attempts += 1
        
        if guess == number:
            print(f"Correct! You won in {attempts} attempts!")
            break
        elif guess < number:
            print("Too low!")
        else:
            print("Too high!")
    else:
        print(f"Game over! The number was {number}")

# Multiplication table
def multiplication_table(n, up_to=10):
    for i in range(1, up_to + 1):
        print(f"{n} x {i} = {n * i}")
```
</details>

---

## Additional Resources

- [Python Control Flow Documentation](https://docs.python.org/3/tutorial/controlflow.html)
- [PEP 634 - Structural Pattern Matching](https://peps.python.org/pep-0634/)
- [Real Python - Conditional Statements](https://realpython.com/python-conditional-statements/)
"""

# Generate files
def main():
    base_path = "/home/bharathr/self/Learning/Study/Python/week1_foundations"
    
    # Day 3
    day03_path = os.path.join(base_path, "day03_controlflow/README.md")
    with open(day03_path, 'w') as f:
        config = CONTENT_CONFIG["day03_controlflow"]
        content = README_TEMPLATE.format(
            day_num=3,
            title=config["title"],
            toc_sections="\n".join(f"- [{s}](#{s.lower().replace(' ', '-)})" for s in config["sections"]),
            overview_content=config["overview"],
            main_content=generate_day03_content(),
            best_practices="See main content above for inline best practices.",
            interview_questions="See main content above for interview questions.",
            practice_exercises="See main content above for practice exercises.",
            resources="- [Python Documentation](https://docs.python.org/)\n- [Real Python Tutorials](https://realpython.com/)",
            key_takeaways="\n".join(f"{i+1}. ✅ {kt}" for i, kt in enumerate(config["key_takeaways"]))
        )
        f.write(content)
    
    print(f"Generated comprehensive README for Day 3")

if __name__ == "__main__":
    main()
