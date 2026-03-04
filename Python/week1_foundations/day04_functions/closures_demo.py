#!/usr/bin/env python3
"""
Closures Deep Dive

Demonstrating advanced closure patterns and real-world use cases.
"""

from typing import Callable, Any
from functools import wraps
import time


def section(title: str):
    print(f"\n{'=' * 50}")
    print(title)
    print("=" * 50)


# ============================================
# 1. BASIC CLOSURE MECHANICS
# ============================================
section("1. BASIC CLOSURE MECHANICS")


def outer_function(msg: str):
    """Demonstrates closure capturing outer variable"""
    
    def inner_function():
        # 'msg' is captured from outer scope
        print(f"Message: {msg}")
    
    return inner_function


# The inner function "remembers" msg even after outer_function returns
hello = outer_function("Hello!")
world = outer_function("World!")

hello()  # Prints: Message: Hello!
world()  # Prints: Message: World!

# Inspect closure cells
print(f"\nClosure cells: {hello.__closure__}")
print(f"Captured value: {hello.__closure__[0].cell_contents}")


# ============================================
# 2. NONLOCAL KEYWORD
# ============================================
section("2. NONLOCAL KEYWORD")


def make_accumulator(start: int = 0) -> Callable[[int], int]:
    """
    Create an accumulator that maintains state.
    Uses 'nonlocal' to modify outer scope variable.
    """
    total = start
    
    def add(value: int) -> int:
        nonlocal total  # Required to modify outer variable
        total += value
        return total
    
    return add


acc = make_accumulator(100)
print(f"Start: 100")
print(f"Add 10: {acc(10)}")  # 110
print(f"Add 25: {acc(25)}")  # 135
print(f"Add -5: {acc(-5)}")  # 130


# ============================================
# 3. CLOSURE-BASED DECORATORS
# ============================================
section("3. CLOSURE-BASED DECORATORS")


def timer(func: Callable) -> Callable:
    """Decorator using closure to wrap function"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"  {func.__name__} took {(end-start)*1000:.2f}ms")
        return result
    return wrapper


def retry(max_attempts: int = 3):
    """Parameterized decorator using nested closure"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"  Attempt {attempt} failed: {e}")
                    if attempt == max_attempts:
                        raise
        return wrapper
    return decorator


@timer
def slow_function():
    time.sleep(0.1)
    return "done"


result = slow_function()

# Retry example
attempt_count = 0

@retry(max_attempts=3)
def flaky_function():
    global attempt_count
    attempt_count += 1
    if attempt_count < 3:
        raise ValueError("Not yet!")
    return "Success!"


print(f"\nRetry result: {flaky_function()}")


# ============================================
# 4. CLOSURE FOR CONFIGURATION
# ============================================
section("4. CLOSURE FOR CONFIGURATION")


def create_logger(prefix: str, debug: bool = False):
    """Create a configured logger function"""
    
    def log(message: str, level: str = "INFO"):
        if level == "DEBUG" and not debug:
            return
        print(f"[{prefix}] [{level}] {message}")
    
    return log


# Create different loggers
app_logger = create_logger("APP", debug=True)
db_logger = create_logger("DATABASE", debug=False)

app_logger("Starting application")
app_logger("Debug info", "DEBUG")  # Will print
db_logger("Connection established")
db_logger("Query details", "DEBUG")  # Won't print (debug=False)


# ============================================
# 5. CLOSURE FOR CACHING (MEMOIZATION)
# ============================================
section("5. CLOSURE FOR CACHING")


def memoize(func: Callable) -> Callable:
    """Create a memoized version of a function using closure"""
    cache = {}  # Captured by closure
    
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
            print(f"  Computing {func.__name__}{args}")
        else:
            print(f"  Cache hit for {func.__name__}{args}")
        return cache[args]
    
    # Expose cache for inspection
    wrapper.cache = cache
    wrapper.clear_cache = lambda: cache.clear()
    
    return wrapper


@memoize
def expensive_computation(n: int) -> int:
    """Simulate expensive computation"""
    return n ** 2


print(f"Result: {expensive_computation(5)}")
print(f"Result: {expensive_computation(5)}")  # Cache hit
print(f"Result: {expensive_computation(10)}")
print(f"Cache contents: {expensive_computation.cache}")


# ============================================
# 6. CLOSURE FOR PARTIAL APPLICATION
# ============================================
section("6. CLOSURE FOR PARTIAL APPLICATION")


def partial(func: Callable, *fixed_args, **fixed_kwargs) -> Callable:
    """
    Custom partial function implementation using closure.
    Similar to functools.partial.
    """
    def wrapper(*args, **kwargs):
        final_kwargs = {**fixed_kwargs, **kwargs}
        return func(*fixed_args, *args, **final_kwargs)
    return wrapper


def power(base: int, exponent: int) -> int:
    return base ** exponent


square = partial(power, exponent=2)
cube = partial(power, exponent=3)

print(f"square(5): {square(5)}")
print(f"cube(3): {cube(3)}")


# ============================================
# 7. CLOSURE PITFALLS
# ============================================
section("7. CLOSURE PITFALLS")

# Common mistake: Loop variable capture
print("\n❌ Wrong way (all closures share same variable):")
funcs_wrong = []
for i in range(3):
    funcs_wrong.append(lambda: i)  # All capture same 'i'

for f in funcs_wrong:
    print(f"  {f()}")  # All print 2!

print("\n✅ Correct way (default argument captures value):")
funcs_correct = []
for i in range(3):
    funcs_correct.append(lambda i=i: i)  # Capture current value

for f in funcs_correct:
    print(f"  {f()}")  # Prints 0, 1, 2


# ============================================
# 8. REAL-WORLD EXAMPLE: Rate Limiter
# ============================================
section("8. REAL-WORLD: RATE LIMITER")


def rate_limiter(max_calls: int, period: float):
    """
    Decorator that limits function calls per time period.
    Uses closure to maintain call history.
    """
    calls = []  # Timestamps of recent calls
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal calls
            now = time.time()
            
            # Remove old calls outside the period
            calls = [t for t in calls if now - t < period]
            
            if len(calls) >= max_calls:
                wait_time = period - (now - calls[0])
                print(f"  Rate limited! Wait {wait_time:.2f}s")
                return None
            
            calls.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


@rate_limiter(max_calls=3, period=1.0)
def api_call(endpoint: str):
    return f"Called {endpoint}"


# Test rate limiting
for i in range(5):
    result = api_call(f"/api/v1/resource/{i}")
    if result:
        print(f"  {result}")


print("\n✅ Closures demo completed!")
