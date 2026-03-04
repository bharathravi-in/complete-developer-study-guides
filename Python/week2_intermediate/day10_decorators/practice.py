#!/usr/bin/env python3
"""Day 10 - Decorators Deep Dive"""

import time
import functools
from typing import Callable, Any

print("=" * 50)
print("DECORATORS DEEP DIVE")
print("=" * 50)

# ============================================
# 1. BASIC DECORATOR
# ============================================
print("\n--- 1. BASIC DECORATOR ---")


def simple_decorator(func: Callable) -> Callable:
    """Basic decorator that wraps a function"""
    def wrapper(*args, **kwargs):
        print(f"  Before calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"  After calling {func.__name__}")
        return result
    return wrapper


@simple_decorator
def greet(name: str) -> str:
    return f"Hello, {name}!"


result = greet("Python")
print(f"  Result: {result}")


# ============================================
# 2. FUNCTOOLS.WRAPS
# ============================================
print("\n--- 2. FUNCTOOLS.WRAPS ---")


def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


def good_decorator(func):
    @functools.wraps(func)  # Preserves function metadata
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@bad_decorator
def bad_example():
    """This is my docstring"""
    pass


@good_decorator
def good_example():
    """This is my docstring"""
    pass


print(f"Without @wraps:")
print(f"  __name__: {bad_example.__name__}")  # wrapper
print(f"  __doc__: {bad_example.__doc__}")    # None

print(f"\nWith @wraps:")
print(f"  __name__: {good_example.__name__}")  # good_example
print(f"  __doc__: {good_example.__doc__}")    # This is my docstring


# ============================================
# 3. DECORATOR WITH ARGUMENTS
# ============================================
print("\n--- 3. DECORATOR WITH ARGUMENTS ---")


def repeat(times: int):
    """Decorator that repeats function execution"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(times):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return decorator


@repeat(times=3)
def say_hello() -> str:
    return "Hello!"


print(f"@repeat(3): {say_hello()}")


# ============================================
# 4. CLASS-BASED DECORATOR
# ============================================
print("\n--- 4. CLASS-BASED DECORATOR ---")


class CountCalls:
    """Decorator class that counts function calls"""
    
    def __init__(self, func: Callable):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0
    
    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"  Call #{self.count} to {self.func.__name__}")
        return self.func(*args, **kwargs)


@CountCalls
def process():
    return "Processing..."


process()
process()
process()
print(f"Total calls: {process.count}")


# ============================================
# 5. PRACTICAL DECORATORS
# ============================================
print("\n--- 5. PRACTICAL DECORATORS ---")


# Timer decorator
def timer(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"  {func.__name__} took {(end-start)*1000:.2f}ms")
        return result
    return wrapper


@timer
def slow_function():
    time.sleep(0.1)
    return "Done"


print("Timer decorator:")
slow_function()


# Retry decorator
def retry(max_attempts: int = 3, delay: float = 0.1):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"    Attempt {attempt} failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


attempt_counter = 0

@retry(max_attempts=3, delay=0.01)
def unreliable_function():
    global attempt_counter
    attempt_counter += 1
    if attempt_counter < 3:
        raise ValueError("Not ready yet")
    return "Success!"


print("\nRetry decorator:")
result = retry(unreliable_function)
print(f"  Result: Success!")


# ============================================
# 6. STACKING DECORATORS
# ============================================
print("\n--- 6. STACKING DECORATORS ---")


def bold(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper


def italic(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return f"<i>{func(*args, **kwargs)}</i>"
    return wrapper


@bold
@italic
def format_text(text: str) -> str:
    return text


# Order: bold(italic(format_text))
print(f"Stacked: {format_text('Hello')}")


# ============================================
# 7. DECORATOR FOR METHODS
# ============================================
print("\n--- 7. METHOD DECORATORS ---")


def validate_positive(func):
    @functools.wraps(func)
    def wrapper(self, value):
        if value < 0:
            raise ValueError("Value must be positive")
        return func(self, value)
    return wrapper


class BankAccount:
    def __init__(self, balance: float = 0):
        self._balance = balance
    
    @property
    def balance(self) -> float:
        return self._balance
    
    @validate_positive
    def deposit(self, amount: float):
        self._balance += amount
        return self._balance


account = BankAccount(100)
account.deposit(50)
print(f"Balance after deposit: ${account.balance}")

try:
    account.deposit(-50)
except ValueError as e:
    print(f"Validation error: {e}")


# ============================================
# 8. CLASS DECORATORS
# ============================================
print("\n--- 8. CLASS DECORATORS ---")


def singleton(cls):
    """Make a class a singleton"""
    instances = {}
    
    @functools.wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance


@singleton
class Database:
    def __init__(self, name: str):
        self.name = name
        print(f"  Creating Database: {name}")


db1 = Database("users")
db2 = Database("orders")  # Won't create new instance

print(f"db1 is db2: {db1 is db2}")
print(f"Both have name: {db1.name}")


# Add methods to a class
def add_repr(cls):
    """Add __repr__ method to a class"""
    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{cls.__name__}({attrs})"
    
    cls.__repr__ = __repr__
    return cls


@add_repr
class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age


print(f"\nWith @add_repr: {Person('Alice', 30)}")


# ============================================
# 9. BUILTIN DECORATORS
# ============================================
print("\n--- 9. BUILTIN DECORATORS ---")

print("""
Common builtin decorators:
  @property          - Create read-only attribute
  @staticmethod      - Method without self
  @classmethod       - Method with cls
  @functools.lru_cache - Memoization
  @functools.wraps   - Preserve function metadata
  @dataclasses.dataclass - Auto-generate methods
  @abc.abstractmethod - Define abstract method
""")


# LRU Cache example
@functools.lru_cache(maxsize=128)
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


start = time.perf_counter()
result = fibonacci(100)
elapsed = time.perf_counter() - start

print(f"fibonacci(100) = {result}")
print(f"Time with cache: {elapsed*1000:.4f}ms")
print(f"Cache info: {fibonacci.cache_info()}")


print("\n✅ Day 10 completed!")
