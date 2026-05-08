# Day 10: Decorators — Functions, Classes & Advanced Patterns

## Learning Objectives
- Understand decorator syntax and the underlying pattern
- Build decorators with and without arguments
- Use `functools.wraps` to preserve function metadata
- Create class-based decorators and decorator factories
- Apply decorators for real-world concerns (caching, auth, validation)

---

## 1. Decorator Fundamentals (Beginner)

```python
import functools
import time

# A decorator is a function that takes a function and returns a modified function
def timer(func):
    """Measure execution time of a function."""
    @functools.wraps(func)  # Preserves __name__, __doc__, etc.
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__}() took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_function(n):
    """Sum numbers the slow way."""
    return sum(range(n))

# @timer is syntactic sugar for: slow_function = timer(slow_function)
result = slow_function(1_000_000)
print(slow_function.__name__)  # "slow_function" (thanks to @wraps)
print(slow_function.__doc__)   # "Sum numbers the slow way."


# Without @wraps, metadata would show "wrapper" instead!
def bad_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
# bad_decorator(fn).__name__ → "wrapper" (BAD!)
```

### Simple Practical Decorators

```python
def debug(func):
    """Print function call details."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result
    return wrapper

def retry(max_attempts: int = 3):
    """Retry a function on exception."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    print(f"Attempt {attempt} failed: {e}. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
        return wrapper
    return decorator

@debug
@retry(max_attempts=3)
def fetch_data(url: str) -> dict:
    """Fetch data from API."""
    import random
    if random.random() < 0.5:
        raise ConnectionError("Network timeout")
    return {"data": "success"}
```

---

## 2. Decorators with Arguments (Intermediate)

```python
# Pattern: decorator factory → decorator → wrapper
def rate_limit(calls: int, period: float):
    """Limit function calls to N per period seconds."""
    def decorator(func):
        call_times = []
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove expired call records
            call_times[:] = [t for t in call_times if now - t < period]
            
            if len(call_times) >= calls:
                wait = period - (now - call_times[0])
                raise RuntimeError(f"Rate limited. Try again in {wait:.1f}s")
            
            call_times.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(calls=5, period=60)
def api_call(endpoint: str):
    return f"Called {endpoint}"


# Decorator that works with AND without arguments
def cache(func=None, *, maxsize=128, ttl=300):
    """Flexible decorator: @cache or @cache(maxsize=64)."""
    def decorator(fn):
        _cache = {}
        
        @functools.wraps(fn)
        def wrapper(*args):
            if args in _cache:
                value, timestamp = _cache[args]
                if time.time() - timestamp < ttl:
                    return value
            result = fn(*args)
            _cache[args] = (result, time.time())
            # Evict if over size
            if len(_cache) > maxsize:
                oldest = min(_cache, key=lambda k: _cache[k][1])
                del _cache[oldest]
            return result
        
        wrapper.cache_clear = lambda: _cache.clear()
        return wrapper
    
    if func is not None:
        return decorator(func)  # Called as @cache without parens
    return decorator  # Called as @cache(maxsize=64)

@cache(maxsize=64, ttl=60)
def expensive_computation(n: int) -> int:
    time.sleep(1)
    return n ** 2
```

### Stacking Decorators

```python
# Decorators apply bottom-up (closest to function first)
@timer          # 3rd: wraps the auth-checked, validated function
@require_auth   # 2nd: wraps the validated function
@validate_input # 1st: wraps the original function
def process(data):
    ...

# Equivalent to:
# process = timer(require_auth(validate_input(process)))
```

---

## 3. Class-Based Decorators (Advanced)

```python
class Memoize:
    """Class-based decorator with cache statistics."""
    
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.cache = {}
        self.hits = 0
        self.misses = 0
    
    def __call__(self, *args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        result = self.func(*args, **kwargs)
        self.cache[key] = result
        return result
    
    def __get__(self, obj, objtype=None):
        """Support instance methods (descriptor protocol)."""
        if obj is None:
            return self
        return functools.partial(self.__call__, obj)
    
    @property
    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total if total else 0
        }

@Memoize
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

fibonacci(100)
print(fibonacci.stats)  # {'hits': 98, 'misses': 101, 'hit_rate': 0.49}


# Class decorator (decorates a class, not a function)
def singleton(cls):
    """Ensure only one instance of a class exists."""
    instances = {}
    
    @functools.wraps(cls, updated=[])
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class DatabaseConnection:
    def __init__(self, url: str):
        self.url = url
        print(f"Connecting to {url}")

# Only creates one instance
db1 = DatabaseConnection("postgres://localhost/db")
db2 = DatabaseConnection("postgres://localhost/other")
assert db1 is db2  # Same object!
```

### Production Decorator Patterns

```python
def validate(**validators):
    """Decorator that validates function arguments by name."""
    def decorator(func):
        import inspect
        sig = inspect.signature(func)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            for param_name, validator_fn in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not validator_fn(value):
                        raise ValueError(
                            f"Validation failed for '{param_name}': {value!r}"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate(
    age=lambda x: 0 <= x <= 150,
    name=lambda x: isinstance(x, str) and len(x) > 0,
    email=lambda x: "@" in x
)
def register_user(name: str, age: int, email: str):
    return {"name": name, "age": age, "email": email}

# register_user("", 25, "a@b.com")  # ValueError: Validation failed for 'name'
```

---

## Interview Questions

### Beginner
1. **What is a decorator and what problem does it solve?** A decorator is a function that wraps another function to add behavior (logging, timing, auth) without modifying its code. It implements the Open/Closed principle: extend behavior without changing source. Syntax: `@decorator` above function definition, equivalent to `func = decorator(func)`.

2. **Why is `functools.wraps` important?** Without `@wraps`, the decorated function loses its `__name__`, `__doc__`, `__module__`, and `__qualname__`. This breaks introspection, help(), debugging, and documentation tools. `@wraps(func)` copies these attributes to the wrapper, making the decoration transparent.

3. **What's the difference between `@decorator` and `@decorator()`?** `@decorator` passes the function directly to `decorator(func)`. `@decorator()` calls `decorator()` first (a factory), then passes the function to the returned inner decorator. The factory pattern is needed when the decorator accepts configuration arguments like `@retry(max_attempts=3)`.

### Intermediate
4. **How do you write a decorator that works both with and without arguments?** Check if the first argument is a callable. Pattern: `def deco(func=None, *, option=default)`. If `func` is provided (no-args call), apply directly. If `func` is None (called with args), return the inner decorator. This allows both `@deco` and `@deco(option=value)`.

5. **Explain decorator stacking order.** Decorators apply bottom-up: the closest to the function wraps first. `@A @B @C def f` means `f = A(B(C(f)))`. Execution flows top-down through wrappers: A's pre-code → B's pre-code → C's pre-code → f() → C's post → B's post → A's post. Order matters for auth/validation chains.

6. **When would you use a class-based decorator vs function-based?** Class-based when: you need to maintain state across calls (cache stats, call counts), want a clean OOP interface (methods for introspection), or need the descriptor protocol for method decoration. Function-based for: simple wrappers, stateless transformations, most common cases.

### Advanced
7. **How do you make a decorator work on both functions and methods?** The challenge: methods pass `self` as first arg. Solution 1: use `*args, **kwargs` (works for both). Solution 2: implement `__get__` on a class-based decorator (descriptor protocol) to handle bound methods. The descriptor approach lets you access the instance if needed.

8. **Implement a decorator that adds circuit-breaker behavior.** Track consecutive failures. After N failures, "open" the circuit (raise immediately without calling function). After a timeout, allow one "probe" call. If probe succeeds, close circuit. State: failure_count, last_failure_time, circuit_state (closed/open/half-open). Use a class decorator for clean state management.

9. **What are the performance implications of decorators?** Each decorator adds a function call layer (stack frame + argument packing). For hot loops, this overhead matters. Mitigations: use `functools.lru_cache` (C-implemented), `__slots__` on class decorators, avoid deep stacking on performance-critical paths. Profile before optimizing.

---

## Hands-On Exercise
1. Build a `@timer` decorator and apply it to recursive vs iterative fibonacci
2. Create `@retry(max_attempts=3, backoff=2)` with exponential backoff
3. Implement `@cache(maxsize=128, ttl=60)` with TTL expiration
4. Write `@validate_types` that checks argument types match annotations
5. Build a `@rate_limit(10, 60)` that allows 10 calls per 60 seconds
