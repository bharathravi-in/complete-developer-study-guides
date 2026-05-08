# Day 4 - Functions

## Table of Contents
- [Overview](#overview)
- [Function Basics](#function-basics)
- [Parameters and Arguments](#parameters-and-arguments)
- [Advanced Function Concepts](#advanced-function-concepts)
- [Best Practices](#best-practices)
- [Interview Preparation](#interview-preparation)
- [Practice Exercises](#practice-exercises)

---

## Overview

Functions are reusable blocks of code that perform specific tasks. They are fundamental to writing clean, maintainable, and DRY (Don't Repeat Yourself) code. Python functions are first-class objects, meaning they can be assigned to variables, passed as arguments, and returned from other functions.

---

## Function Basics

### Defining Functions

```python
def function_name(parameters):
    """Docstring explaining what the function does"""
    # Function body
    return value
```

**Example:**
```python
def greet(name):
    """Return a personalized greeting"""
    return f"Hello, {name}!"

result = greet("Alice")
print(result)  # Output: Hello, Alice!
```

### Return Types

Python functions can return:
- **Single value**: `return 42`
- **Multiple values** (as tuple): `return x, y, z`
- **None** (implicit if no return statement)
- **Any data type**: int, str, list, dict, function, object, etc.

```python
def calculate(a, b):
    """Return multiple calculation results"""
    return a + b, a - b, a * b, a / b

add, sub, mul, div = calculate(10, 5)
print(f"Add: {add}, Sub: {sub}, Mul: {mul}, Div: {div}")
# Output: Add: 15, Sub: 5, Mul: 50, Div: 2.0
```

### Type Hints (Python 3.5+)

```python
def add_numbers(a: int, b: int) -> int:
    """Add two integers and return the result"""
    return a + b

def get_user_info(user_id: int) -> dict[str, str]:
    """Return user information as a dictionary"""
    return {"id": str(user_id), "name": "John"}
```

---

## Parameters and Arguments

### Positional Arguments

Arguments must be passed in the same order as parameters are defined.

```python
def introduce(name, age, city):
    return f"{name} is {age} years old and lives in {city}"

print(introduce("Bob", 25, "NYC"))  # Must follow order
```

### Default Parameters

Provide default values for parameters. They must come after non-default parameters.

```python
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"

print(greet("Alice"))              # Output: Hello, Alice!
print(greet("Bob", "Hi"))          # Output: Hi, Bob!
```

**⚠️ Common Pitfall: Mutable Default Arguments**

```python
# ❌ WRONG - Mutable default argument
def add_item(item, my_list=[]):
    my_list.append(item)
    return my_list

print(add_item(1))  # [1]
print(add_item(2))  # [1, 2] - NOT what you expect!

# ✅ CORRECT
def add_item(item, my_list=None):
    if my_list is None:
        my_list = []
    my_list.append(item)
    return my_list

print(add_item(1))  # [1]
print(add_item(2))  # [2] - Correct!
```

### Keyword Arguments

Pass arguments by parameter name, allowing any order.

```python
def book_ticket(name, destination, seat_class="Economy", meal="Veg"):
    return f"{name} -> {destination} | {seat_class} | {meal}"

# Keyword arguments (order doesn't matter)
print(book_ticket(destination="Paris", name="Alice"))
print(book_ticket("Bob", "Tokyo", meal="Non-Veg", seat_class="Business"))
```

### *args (Variable Positional Arguments)

Capture any number of positional arguments as a **tuple**.

```python
def sum_all(*args):
    """Sum all numbers passed as arguments"""
    total = 0
    for num in args:
        total += num
    return total

print(sum_all(1, 2, 3))           # Output: 6
print(sum_all(10, 20, 30, 40))    # Output: 100

# More concise with built-in sum()
def sum_all(*args):
    return sum(args)
```

**Example: Flexible String Formatter**
```python
def format_output(template, *args):
    """Format a template string with variable arguments"""
    return template.format(*args)

result = format_output("Name: {}, Age: {}, City: {}", "Alice", 30, "NYC")
print(result)  # Output: Name: Alice, Age: 30, City: NYC
```

### **kwargs (Variable Keyword Arguments)

Capture any number of keyword arguments as a **dictionary**.

```python
def print_user_info(**kwargs):
    """Print all user information"""
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_user_info(name="Alice", age=30, city="NYC", job="Engineer")
# Output:
# name: Alice
# age: 30
# city: NYC
# job: Engineer
```

### Combining All Parameter Types

**Order matters:** `def func(pos, pos_default=val, *args, kw_only, kw_default=val, **kwargs)`

```python
def complex_function(required, default="default", *args, kw_only, kw_default="kw_def", **kwargs):
    print(f"Required: {required}")
    print(f"Default: {default}")
    print(f"Args: {args}")
    print(f"Keyword-only: {kw_only}")
    print(f"Keyword-default: {kw_default}")
    print(f"Kwargs: {kwargs}")

complex_function(
    "must_provide",           # required
    "changed_default",        # default
    1, 2, 3,                  # *args
    kw_only="must_provide_kw", # keyword-only (after *args)
    extra1="value1",          # **kwargs
    extra2="value2"
)
```

---

## Advanced Function Concepts

### Lambda Functions

Anonymous, single-expression functions. Syntax: `lambda arguments: expression`

```python
# Traditional function
def square(x):
    return x ** 2

# Lambda equivalent
square = lambda x: x ** 2

print(square(5))  # Output: 25

# Common use cases
numbers = [1, 2, 3, 4, 5]

# With map()
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# With filter()
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4]

# With sorted()
users = [("Alice", 30), ("Bob", 25), ("Charlie", 35)]
sorted_by_age = sorted(users, key=lambda x: x[1])
print(sorted_by_age)  # [('Bob', 25), ('Alice', 30), ('Charlie', 35)]
```

**When to use lambdas:**
- Short, simple operations
- One-time use (callbacks, key functions)
- Functional programming constructs (map, filter, reduce)

**When NOT to use lambdas:**
- Complex logic (use named functions)
- Need for docstrings or type hints
- Reusable code (named functions are more readable)

### Recursion

A function that calls itself. Must have a **base case** to prevent infinite recursion.

```python
def factorial(n):
    """Calculate factorial using recursion"""
    # Base case
    if n == 0 or n == 1:
        return 1
    # Recursive case
    return n * factorial(n - 1)

print(factorial(5))  # Output: 120 (5 * 4 * 3 * 2 * 1)

# Fibonacci sequence
def fibonacci(n):
    """Return nth Fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print([fibonacci(i) for i in range(10)])
# Output: [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

**⚠️ Recursion Limits:**
Python has a default recursion limit (usually 1000). Use `sys.setrecursionlimit()` if needed, but consider iterative solutions for deep recursion.

```python
import sys
print(sys.getrecursionlimit())  # Default: 1000
sys.setrecursionlimit(2000)     # Increase if needed
```

**Tail Recursion Optimization:**
Python doesn't optimize tail recursion, so deep recursion can cause stack overflow.

```python
# Iterative alternative for factorial (better for large n)
def factorial_iterative(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
```

### Closures

A closure is a function that **remembers values from its enclosing scope**, even after the outer function has finished executing.

```python
def make_multiplier(factor):
    """Return a function that multiplies by factor"""
    def multiplier(x):
        return x * factor  # 'factor' is remembered from outer scope
    return multiplier

times_3 = make_multiplier(3)
times_5 = make_multiplier(5)

print(times_3(10))  # Output: 30
print(times_5(10))  # Output: 50

# Check closure variables
print(times_3.__closure__)
print(times_3.__closure__[0].cell_contents)  # Output: 3
```

**Real-world Example: Counter**
```python
def make_counter():
    """Create a counter with increment, decrement, and reset"""
    count = 0  # Enclosed variable
    
    def increment():
        nonlocal count  # Modify enclosed variable
        count += 1
        return count
    
    def decrement():
        nonlocal count
        count -= 1
        return count
    
    def reset():
        nonlocal count
        count = 0
        return count
    
    def get_count():
        return count
    
    return increment, decrement, reset, get_count

inc, dec, reset, get = make_counter()
print(inc())    # 1
print(inc())    # 2
print(dec())    # 1
print(reset())  # 0
print(get())    # 0
```

### First-Class Functions

Functions are **first-class objects** in Python. They can be:
1. Assigned to variables
2. Passed as arguments to other functions
3. Returned from functions
4. Stored in data structures

```python
# 1. Assign to variable
def greet():
    return "Hello!"

say_hello = greet
print(say_hello())  # Output: Hello!

# 2. Pass as argument (Higher-order function)
def apply_operation(func, x, y):
    """Apply a function to two arguments"""
    return func(x, y)

def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

print(apply_operation(add, 5, 3))       # Output: 8
print(apply_operation(multiply, 5, 3))  # Output: 15

# 3. Return from function
def get_operation(op_type):
    """Return the appropriate operation function"""
    if op_type == "add":
        return lambda x, y: x + y
    elif op_type == "multiply":
        return lambda x, y: x * y
    else:
        return lambda x, y: None

operation = get_operation("add")
print(operation(10, 5))  # Output: 15

# 4. Store in data structures
operations = {
    "add": lambda x, y: x + y,
    "subtract": lambda x, y: x - y,
    "multiply": lambda x, y: x * y,
    "divide": lambda x, y: x / y if y != 0 else None
}

print(operations["multiply"](4, 5))  # Output: 20
```

### Decorators Preview

While we'll cover decorators in detail later, they rely on first-class functions:

```python
def uppercase_decorator(func):
    """Decorator that converts function output to uppercase"""
    def wrapper():
        result = func()
        return result.upper()
    return wrapper

@uppercase_decorator
def greet():
    return "hello, world!"

print(greet())  # Output: HELLO, WORLD!
```

---

## Best Practices

### 1. Function Design Principles

```python
# ✅ DO: Single Responsibility - One function, one purpose
def calculate_total_price(items):
    return sum(item['price'] for item in items)

def apply_discount(total, discount_percent):
    return total * (1 - discount_percent / 100)

# ❌ DON'T: Multiple responsibilities
def calculate_and_print_price(items, discount):
    total = sum(item['price'] for item in items)
    discounted = total * (1 - discount / 100)
    print(f"Total: ${discounted}")  # Mixing calculation and I/O
    return discounted
```

### 2. Use Docstrings

```python
def calculate_bmi(weight_kg, height_m):
    """
    Calculate Body Mass Index (BMI).
    
    Args:
        weight_kg (float): Weight in kilograms
        height_m (float): Height in meters
    
    Returns:
        float: BMI value rounded to 2 decimal places
    
    Raises:
        ValueError: If weight or height is not positive
    
    Example:
        >>> calculate_bmi(70, 1.75)
        22.86
    """
    if weight_kg <= 0 or height_m <= 0:
        raise ValueError("Weight and height must be positive")
    return round(weight_kg / (height_m ** 2), 2)
```

### 3. Avoid Side Effects

```python
# ❌ AVOID: Function with side effects (modifies external state)
total = 0
def add_to_total(value):
    global total
    total += value

# ✅ PREFER: Pure function (no side effects)
def add_values(current_total, value):
    return current_total + value

total = add_values(total, 10)
```

### 4. Keep Functions Short

Aim for functions that fit on one screen (~20-30 lines max). If longer, break into smaller functions.

### 5. Use Type Hints for Clarity

```python
from typing import List, Dict, Optional, Tuple

def process_users(
    users: List[Dict[str, str]], 
    filter_active: bool = True
) -> List[str]:
    """Extract names of active users"""
    return [u['name'] for u in users if not filter_active or u.get('active')]
```

---

## Interview Preparation

### Common Interview Questions

#### Q1: What's the difference between arguments and parameters?

**Answer:**
- **Parameters** are variables in the function definition
- **Arguments** are actual values passed when calling the function

```python
def greet(name):  # 'name' is a parameter
    print(f"Hello, {name}")

greet("Alice")  # "Alice" is an argument
```

---

#### Q2: Explain *args and **kwargs with an example

**Answer:**
- `*args` collects extra positional arguments into a tuple
- `**kwargs` collects extra keyword arguments into a dictionary

```python
def example_function(required, *args, **kwargs):
    print(f"Required: {required}")
    print(f"Args (tuple): {args}")
    print(f"Kwargs (dict): {kwargs}")

example_function(1, 2, 3, 4, key1="value1", key2="value2")
# Output:
# Required: 1
# Args (tuple): (2, 3, 4)
# Kwargs (dict): {'key1': 'value1', 'key2': 'value2'}
```

---

#### Q3: What is a closure? Provide an example.

**Answer:**
A closure is a function that retains access to variables from its enclosing scope even after the outer function has finished.

```python
def outer(x):
    def inner(y):
        return x + y  # 'inner' closes over 'x'
    return inner

add_5 = outer(5)
print(add_5(10))  # Output: 15
print(add_5(20))  # Output: 25
```

---

#### Q4: What's the difference between map(), filter(), and reduce()?

**Answer:**
- **map()**: Apply a function to all items → `[f(x) for x in iterable]`
- **filter()**: Keep items that pass a test → `[x for x in iterable if condition(x)]`
- **reduce()**: Accumulate items to a single value

```python
from functools import reduce

numbers = [1, 2, 3, 4, 5]

# map: apply function to each
squared = list(map(lambda x: x**2, numbers))
print(squared)  # [1, 4, 9, 16, 25]

# filter: keep only items matching condition
evens = list(filter(lambda x: x % 2 == 0, numbers))
print(evens)  # [2, 4]

# reduce: accumulate to single value
product = reduce(lambda x, y: x * y, numbers)
print(product)  # 120 (1*2*3*4*5)
```

---

#### Q5: Coding Problem - Implement a function decorator that caches results

**Question:** Write a memoization decorator that caches function results.

**Solution:**
```python
def memoize(func):
    """Cache function results for given arguments"""
    cache = {}
    
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    
    return wrapper

@memoize
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Much faster with memoization
print(fibonacci(50))  # Completes instantly
```

---

#### Q6: Coding Problem - Flatten a nested list recursively

**Question:** Write a recursive function to flatten a nested list of arbitrary depth.

**Solution:**
```python
def flatten(nested_list):
    """
    Flatten a nested list recursively.
    
    Args:
        nested_list: A list that may contain nested lists
    
    Returns:
        A flat list containing all elements
    
    Example:
        >>> flatten([1, [2, 3, [4, 5]], 6, [7, [8, 9]]])
        [1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten(item))  # Recursive call
        else:
            result.append(item)
    return result

# Test
nested = [1, [2, 3, [4, 5]], 6, [7, [8, 9]]]
print(flatten(nested))  # [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

**Iterative solution:**
```python
def flatten_iterative(nested_list):
    """Flatten using a stack (iterative)"""
    stack = [nested_list]
    result = []
    
    while stack:
        current = stack.pop()
        if isinstance(current, list):
            stack.extend(reversed(current))  # Maintain order
        else:
            result.append(current)
    
    return result
```

---

#### Q7: Coding Problem - Function composition

**Question:** Implement a `compose` function that composes multiple functions.

**Solution:**
```python
from functools import reduce

def compose(*functions):
    """
    Compose multiple functions into a single function.
    Functions are applied right to left.
    
    Example:
        >>> f = compose(str.upper, lambda x: x + "!", lambda x: "Hello " + x)
        >>> f("world")
        'HELLO WORLD!'
    """
    def composed_function(x):
        return reduce(lambda acc, func: func(acc), reversed(functions), x)
    return composed_function

# Usage
add_exclamation = lambda x: x + "!"
greet = lambda x: "Hello " + x
shout = str.upper

greet_and_shout = compose(shout, add_exclamation, greet)
print(greet_and_shout("world"))  # Output: HELLO WORLD!
```

---

#### Q8: What happens with mutable default arguments?

**Answer:** Mutable defaults are evaluated once at function definition, not per call.

```python
# Problem
def append_to(element, target=[]):
    target.append(element)
    return target

print(append_to(1))  # [1]
print(append_to(2))  # [1, 2] - Unexpected!

# Solution
def append_to(element, target=None):
    if target is None:
        target = []
    target.append(element)
    return target

print(append_to(1))  # [1]
print(append_to(2))  # [2] - Correct!
```

---

#### Q9: Coding Problem - Curry function

**Question:** Implement a curry function that converts `f(a, b, c)` to `f(a)(b)(c)`.

**Solution:**
```python
def curry(func):
    """
    Convert a function that takes multiple arguments
    into a sequence of functions that each take a single argument.
    """
    def curried(*args):
        if len(args) >= func.__code__.co_argcount:
            return func(*args)
        return lambda *more_args: curried(*(args + more_args))
    return curried

# Example
def add_three(a, b, c):
    return a + b + c

curried_add = curry(add_three)

# Can call in different ways
print(curried_add(1)(2)(3))       # 6
print(curried_add(1, 2)(3))       # 6
print(curried_add(1)(2, 3))       # 6
print(curried_add(1, 2, 3))       # 6
```

---

#### Q10: Coding Problem - Function retry mechanism

**Question:** Create a decorator that retries a function on failure.

```python
import time
from functools import wraps

def retry(max_attempts=3, delay=1):
    """
    Retry decorator that attempts to call a function multiple times
    if it raises an exception.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay in seconds between retries
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts >= max_attempts:
                        raise
                    print(f"Attempt {attempts} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator

# Usage
@retry(max_attempts=3, delay=2)
def unstable_function():
    import random
    if random.random() < 0.7:
        raise ConnectionError("Network error")
    return "Success!"

# Will retry up to 3 times
result = unstable_function()
print(result)
```

---

## Practice Exercises

### Exercise 1: Basic Functions
Write a function `is_palindrome(s)` that returns `True` if string `s` is a palindrome (ignoring case and spaces).

<details>
<summary>Solution</summary>

```python
def is_palindrome(s):
    """Check if a string is a palindrome"""
    # Remove spaces and convert to lowercase
    cleaned = s.replace(" ", "").lower()
    return cleaned == cleaned[::-1]

# Test
print(is_palindrome("racecar"))      # True
print(is_palindrome("A man a plan a canal Panama"))  # True
print(is_palindrome("hello"))        # False
```
</details>

---

### Exercise 2: Variable Arguments
Create a function `calculate_stats(*numbers)` that returns a dictionary with `min`, `max`, `mean`, and `median` of the numbers.

<details>
<summary>Solution</summary>

```python
def calculate_stats(*numbers):
    """Calculate statistics for a sequence of numbers"""
    if not numbers:
        return None
    
    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    
    # Calculate median
    if n % 2 == 0:
        median = (sorted_nums[n//2 - 1] + sorted_nums[n//2]) / 2
    else:
        median = sorted_nums[n//2]
    
    return {
        'min': min(numbers),
        'max': max(numbers),
        'mean': sum(numbers) / len(numbers),
        'median': median,
        'count': n
    }

# Test
print(calculate_stats(1, 2, 3, 4, 5))
# {'min': 1, 'max': 5, 'mean': 3.0, 'median': 3, 'count': 5}
```
</details>

---

### Exercise 3: Closures
Create a `make_bank_account(initial_balance)` function that returns three functions: `deposit(amount)`, `withdraw(amount)`, and `get_balance()`.

<details>
<summary>Solution</summary>

```python
def make_bank_account(initial_balance=0):
    """Create a bank account with closure-based state"""
    balance = initial_balance
    
    def deposit(amount):
        nonlocal balance
        if amount > 0:
            balance += amount
            return f"Deposited ${amount}. New balance: ${balance}"
        return "Invalid amount"
    
    def withdraw(amount):
        nonlocal balance
        if 0 < amount <= balance:
            balance -= amount
            return f"Withdrew ${amount}. New balance: ${balance}"
        return "Insufficient funds or invalid amount"
    
    def get_balance():
        return f"Current balance: ${balance}"
    
    return deposit, withdraw, get_balance

# Usage
deposit, withdraw, get_balance = make_bank_account(100)
print(get_balance())    # Current balance: $100
print(deposit(50))      # Deposited $50. New balance: $150
print(withdraw(30))     # Withdrew $30. New balance: $120
print(get_balance())    # Current balance: $120
```
</details>

---

### Exercise 4: Recursion
Write a recursive function `sum_nested_list(lst)` that sums all numbers in a nested list (can contain integers and lists).

<details>
<summary>Solution</summary>

```python
def sum_nested_list(lst):
    """
    Sum all integers in a nested list structure.
    
    Example:
        >>> sum_nested_list([1, [2, 3], [[4], 5]])
        15
    """
    total = 0
    for item in lst:
        if isinstance(item, list):
            total += sum_nested_list(item)  # Recursive call
        else:
            total += item
    return total

# Test
nested = [1, [2, 3], [[4], 5], [[[6]]]]
print(sum_nested_list(nested))  # 21
```
</details>

---

### Exercise 5: Higher-Order Functions
Create a `filter_map(predicate, transform, iterable)` function that combines filter and map operations.

<details>
<summary>Solution</summary>

```python
def filter_map(predicate, transform, iterable):
    """
    Filter items by predicate, then apply transform.
    
    Args:
        predicate: Function that returns True/False
        transform: Function to apply to filtered items
        iterable: Input sequence
    
    Returns:
        List of transformed items that passed the filter
    """
    return [transform(item) for item in iterable if predicate(item)]

# Alternative using map and filter
def filter_map_alt(predicate, transform, iterable):
    return list(map(transform, filter(predicate, iterable)))

# Test
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
result = filter_map(
    lambda x: x % 2 == 0,  # Keep only evens
    lambda x: x ** 2,       # Square them
    numbers
)
print(result)  # [4, 16, 36, 64, 100]
```
</details>

---

## Run

```bash
# Practice basic functions
python practice.py

# Explore closures
python closures_demo.py
```

## Additional Resources

- [Python Official Docs - Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
- [PEP 3102 - Keyword-Only Arguments](https://www.python.org/dev/peps/pep-3102/)
- [Real Python - Closures](https://realpython.com/inner-functions-what-are-they-good-for/)
- [Functional Programming in Python](https://docs.python.org/3/howto/functional.html)

---

## Key Takeaways

1. ✅ Functions are first-class objects in Python
2. ✅ Use `*args` for variable positional args, `**kwargs` for variable keyword args
3. ✅ Avoid mutable default arguments (use `None` instead)
4. ✅ Closures capture and remember their enclosing scope
5. ✅ Recursion needs a base case to prevent infinite loops
6. ✅ Lambda functions are useful for short, one-time operations
7. ✅ Type hints improve code readability and enable better tooling
8. ✅ Keep functions focused on a single responsibility
