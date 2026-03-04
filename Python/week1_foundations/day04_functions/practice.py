#!/usr/bin/env python3
"""Day 4 - Functions Deep Dive"""

from typing import Callable, Any
import functools

print("=" * 50)
print("FUNCTIONS DEEP DIVE")
print("=" * 50)

# ============================================
# 1. BASIC FUNCTIONS
# ============================================
print("\n--- 1. BASIC FUNCTIONS ---")


def greet(name: str) -> str:
    """Simple function with type hints"""
    return f"Hello, {name}!"


print(greet("Python"))
print(f"Function docstring: {greet.__doc__}")
print(f"Function name: {greet.__name__}")


# ============================================
# 2. DEFAULT PARAMETERS
# ============================================
print("\n--- 2. DEFAULT PARAMETERS ---")


def create_user(name: str, age: int = 0, active: bool = True) -> dict:
    """Function with default parameters"""
    return {"name": name, "age": age, "active": active}


print(create_user("Alice"))
print(create_user("Bob", 25))
print(create_user("Charlie", 30, False))

# ⚠️ DANGER: Mutable default arguments


def bad_append(item, lst=[]):  # DON'T DO THIS!
    lst.append(item)
    return lst


print("\nMutable default danger:")
print(f"  First call: {bad_append(1)}")
print(f"  Second call: {bad_append(2)}")  # [1, 2] - Bug!


def good_append(item, lst=None):  # Correct way
    if lst is None:
        lst = []
    lst.append(item)
    return lst


print(f"  Fixed first: {good_append(1)}")
print(f"  Fixed second: {good_append(2)}")  # [2] - Correct!


# ============================================
# 3. *ARGS AND **KWARGS
# ============================================
print("\n--- 3. *ARGS AND **KWARGS ---")


def flexible_func(*args, **kwargs):
    """Function accepting any arguments"""
    print(f"  args (tuple): {args}")
    print(f"  kwargs (dict): {kwargs}")


flexible_func(1, 2, 3, name="Python", version=3.12)


def calculate_total(*prices, tax_rate: float = 0.1, discount: float = 0):
    """Real-world example with *args and keyword-only args"""
    subtotal = sum(prices)
    tax = subtotal * tax_rate
    total = subtotal + tax - discount
    return round(total, 2)


print(f"\nTotal: ${calculate_total(100, 200, 50, tax_rate=0.08, discount=25)}")


# Unpacking with * and **
def add_three(a, b, c):
    return a + b + c


numbers = [1, 2, 3]
print(f"Unpacking list: {add_three(*numbers)}")

kwargs = {"a": 1, "b": 2, "c": 3}
print(f"Unpacking dict: {add_three(**kwargs)}")


# ============================================
# 4. LAMBDA FUNCTIONS
# ============================================
print("\n--- 4. LAMBDA FUNCTIONS ---")

# Basic lambda
square = lambda x: x ** 2
print(f"Lambda square(5): {square(5)}")

# Lambda with multiple args
add = lambda a, b: a + b
print(f"Lambda add(3, 4): {add(3, 4)}")

# Lambda in sorting
users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35},
]

sorted_users = sorted(users, key=lambda u: u["age"])
print(f"\nSorted by age: {[u['name'] for u in sorted_users]}")

# Lambda with map, filter, reduce
numbers = [1, 2, 3, 4, 5]
print(f"\nmap (square): {list(map(lambda x: x**2, numbers))}")
print(f"filter (even): {list(filter(lambda x: x % 2 == 0, numbers))}")

from functools import reduce
print(f"reduce (sum): {reduce(lambda a, b: a + b, numbers)}")


# ============================================
# 5. RECURSION
# ============================================
print("\n--- 5. RECURSION ---")


def factorial(n: int) -> int:
    """Classic recursive factorial"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)


print(f"factorial(5): {factorial(5)}")


def fibonacci(n: int) -> int:
    """Naive recursive fibonacci (exponential time)"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# Memoized version
@functools.lru_cache(maxsize=None)
def fibonacci_memo(n: int) -> int:
    """Memoized fibonacci (linear time)"""
    if n <= 1:
        return n
    return fibonacci_memo(n - 1) + fibonacci_memo(n - 2)


print(f"fibonacci(10): {fibonacci(10)}")
print(f"fibonacci_memo(100): {fibonacci_memo(100)}")


# Tail recursion (Python doesn't optimize, but good practice)
def factorial_tail(n: int, accumulator: int = 1) -> int:
    """Tail recursive factorial"""
    if n <= 1:
        return accumulator
    return factorial_tail(n - 1, n * accumulator)


print(f"factorial_tail(5): {factorial_tail(5)}")


# ============================================
# 6. FIRST-CLASS FUNCTIONS
# ============================================
print("\n--- 6. FIRST-CLASS FUNCTIONS ---")

# Functions as variables
my_func = greet
print(f"Function as variable: {my_func('World')}")

# Functions as arguments
def apply_twice(func: Callable, value: Any) -> Any:
    """Apply a function twice to a value"""
    return func(func(value))


def add_10(x: int) -> int:
    return x + 10


print(f"apply_twice(add_10, 5): {apply_twice(add_10, 5)}")

# Functions returning functions
def make_multiplier(n: int) -> Callable[[int], int]:
    """Return a function that multiplies by n"""
    def multiplier(x: int) -> int:
        return x * n
    return multiplier


triple = make_multiplier(3)
print(f"triple(7): {triple(7)}")

# Function with attributes
def counter() -> int:
    counter.count += 1
    return counter.count


counter.count = 0
print(f"counter(): {counter()}, {counter()}, {counter()}")


# ============================================
# 7. CLOSURES
# ============================================
print("\n--- 7. CLOSURES ---")


def outer(x: int) -> Callable[[], int]:
    """Outer function creates a closure"""
    def inner() -> int:
        """Inner function 'closes over' x"""
        return x * 2
    return inner


closure = outer(10)
print(f"Closure: {closure()}")
print(f"Closure's free variables: {closure.__code__.co_freevars}")


# Practical closure example
def make_counter(start: int = 0) -> Callable[[], int]:
    """Create a counter function with hidden state"""
    count = start
    
    def counter() -> int:
        nonlocal count  # Access outer variable
        count += 1
        return count
    
    return counter


my_counter = make_counter(10)
print(f"\nCounter: {my_counter()}, {my_counter()}, {my_counter()}")


# Closure with multiple functions
def bank_account(initial_balance: float) -> dict:
    """Create a bank account with encapsulated balance"""
    balance = initial_balance
    
    def deposit(amount: float) -> float:
        nonlocal balance
        balance += amount
        return balance
    
    def withdraw(amount: float) -> float | str:
        nonlocal balance
        if amount > balance:
            return "Insufficient funds"
        balance -= amount
        return balance
    
    def get_balance() -> float:
        return balance
    
    return {
        "deposit": deposit,
        "withdraw": withdraw,
        "balance": get_balance,
    }


account = bank_account(100)
print(f"\nInitial balance: ${account['balance']()}")
print(f"After deposit $50: ${account['deposit'](50)}")
print(f"After withdraw $30: ${account['withdraw'](30)}")


# ============================================
# 8. FUNCTION INTROSPECTION
# ============================================
print("\n--- 8. FUNCTION INTROSPECTION ---")

import inspect


def example_func(a: int, b: str = "default", *args, **kwargs) -> str:
    """Example function for introspection"""
    return f"{a}, {b}"


print(f"Name: {example_func.__name__}")
print(f"Doc: {example_func.__doc__}")
print(f"Annotations: {example_func.__annotations__}")
print(f"Defaults: {example_func.__defaults__}")
print(f"Signature: {inspect.signature(example_func)}")

print("\n✅ Day 4 completed!")
