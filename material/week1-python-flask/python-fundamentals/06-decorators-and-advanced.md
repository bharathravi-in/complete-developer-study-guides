# Day 6: Decorators, Type Hints & Advanced Python

## Why This Matters
- Flask routes use decorators (`@app.route`)
- Authentication uses decorators (`@require_auth`)
- Type hints make code maintainable (like TypeScript)
- These are essential patterns in production Python

---

## 1. Decorators

### Basic Decorator
```python
# A decorator is a function that wraps another function
# Like middleware in Express.js!

def log_call(func):
    """Logs when a function is called."""
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}...")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned: {result}")
        return result
    return wrapper

@log_call
def add(a, b):
    return a + b

# @log_call is syntactic sugar for: add = log_call(add)
add(2, 3)
# Output:
# Calling add...
# add returned: 5
```

### Decorator with Arguments
```python
from functools import wraps

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator that retries a function on failure."""
    def decorator(func):
        @wraps(func)  # Preserves function metadata
        def wrapper(*args, **kwargs):
            import time
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts - 1:
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                        time.sleep(delay)
                    else:
                        raise
        return wrapper
    return decorator

@retry(max_attempts=3, delay=0.5)
def call_api(url: str) -> dict:
    """This will automatically retry 3 times."""
    import random
    if random.random() < 0.5:
        raise ConnectionError("API down")
    return {"status": "success"}
```

### Real-World Decorators for AI Services
```python
import time
from functools import wraps

# 1. Timing decorator
def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper

# 2. Caching decorator (simple memoization)
def cache(func):
    _cache = {}
    @wraps(func)
    def wrapper(*args):
        if args in _cache:
            print(f"Cache hit for {args}")
            return _cache[args]
        result = func(*args)
        _cache[args] = result
        return result
    return wrapper

# 3. Rate limiter
def rate_limit(calls_per_second: int = 5):
    def decorator(func):
        last_called = [0.0]
        min_interval = 1.0 / calls_per_second
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 4. Authentication check (Flask-style)
def require_auth(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from flask import request, jsonify
        token = request.headers.get("Authorization")
        if not token or not verify_token(token):
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper

# 5. Input validation
def validate_json(*required_fields):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request, jsonify
            data = request.get_json()
            missing = [f for f in required_fields if f not in data]
            if missing:
                return jsonify({"error": f"Missing fields: {missing}"}), 400
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage in Flask:
# @app.route("/api/embed", methods=["POST"])
# @require_auth
# @validate_json("text")
# @timer
# def embed_text():
#     ...
```

### Async Decorators
```python
from functools import wraps
import asyncio

def async_timer(func):
    """Timer for async functions."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.2f}s")
        return result
    return wrapper

def async_retry(max_attempts: int = 3):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        raise
        return wrapper
    return decorator

@async_timer
@async_retry(max_attempts=3)
async def fetch_embedding(text: str) -> list[float]:
    # ... actual implementation
    pass
```

---

## 2. Type Hints (Like TypeScript)

### Basic Type Hints
```python
from typing import Optional, Union, Any

# Basic types
name: str = "Bharath"
age: int = 30
score: float = 95.5
is_active: bool = True

# Function type hints
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}!"

# Optional (value or None)
def find_user(id: int) -> Optional[dict]:
    """Returns user dict or None if not found."""
    if id == 1:
        return {"name": "Bharath"}
    return None

# Union (multiple types)
def process(data: Union[str, list[str]]) -> list[str]:
    if isinstance(data, str):
        return [data]
    return data

# Python 3.10+ syntax (simpler)
def process_modern(data: str | list[str]) -> list[str]:
    if isinstance(data, str):
        return [data]
    return data
```

### Complex Types
```python
from typing import (
    Dict, List, Tuple, Set, 
    Callable, Iterator, Generator,
    TypeVar, Generic
)

# Collections
def process_docs(docs: list[str]) -> dict[str, list[float]]:
    return {doc: [0.1, 0.2] for doc in docs}

# Callable (function types)
def apply_transform(
    text: str, 
    transform: Callable[[str], str]
) -> str:
    return transform(text)

# Usage
result = apply_transform("hello", lambda x: x.upper())

# TypeVar (generics like TypeScript's T)
T = TypeVar("T")

def first_item(items: list[T]) -> T:
    """Return first item, preserving type."""
    return items[0]

# TypedDict (like TypeScript interface for dicts)
from typing import TypedDict

class UserDict(TypedDict):
    name: str
    age: int
    role: str
    skills: list[str]

def create_user(data: UserDict) -> UserDict:
    return data

user: UserDict = {
    "name": "Bharath",
    "age": 30,
    "role": "AI Engineer",
    "skills": ["Python", "React"]
}
```

### Generic Classes
```python
from typing import TypeVar, Generic, Optional

T = TypeVar("T")

class Repository(Generic[T]):
    """Generic repository pattern (like TypeScript generic class)."""
    
    def __init__(self):
        self._items: dict[int, T] = {}
        self._next_id: int = 1
    
    def add(self, item: T) -> int:
        id = self._next_id
        self._items[id] = item
        self._next_id += 1
        return id
    
    def get(self, id: int) -> Optional[T]:
        return self._items.get(id)
    
    def get_all(self) -> list[T]:
        return list(self._items.values())
    
    def delete(self, id: int) -> bool:
        if id in self._items:
            del self._items[id]
            return True
        return False

# Usage (type-safe!)
user_repo: Repository[UserDict] = Repository()
user_repo.add({"name": "Bharath", "age": 30, "role": "AI Eng", "skills": []})

doc_repo: Repository[str] = Repository()
doc_repo.add("Hello World")
```

---

## 3. Context Managers

```python
from contextlib import contextmanager

# Custom context manager (like try/finally pattern)
@contextmanager
def timer_context(label: str):
    """Time a block of code."""
    import time
    start = time.time()
    yield  # Code inside 'with' block runs here
    elapsed = time.time() - start
    print(f"{label}: {elapsed:.2f}s")

# Usage
with timer_context("Embedding generation"):
    # ... expensive operation
    import time
    time.sleep(1)
# Output: Embedding generation: 1.00s

# Context manager for database transactions
@contextmanager
def transaction(db):
    """Ensure database transaction is committed or rolled back."""
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
```

---

## 4. Generators (Memory-Efficient Processing)

```python
# Generator function (yields values one at a time)
def chunk_generator(text: str, chunk_size: int = 500):
    """Memory-efficient text chunking.
    Doesn't load all chunks into memory at once.
    """
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]

# Usage
large_text = "A" * 10000
for chunk in chunk_generator(large_text, chunk_size=1000):
    process_chunk(chunk)  # Only one chunk in memory at a time

# Generator expression (like list comprehension but lazy)
numbers = range(1_000_000)
squares_list = [x**2 for x in numbers]    # All in memory
squares_gen = (x**2 for x in numbers)     # Lazy, memory efficient

# Real-world: streaming large files
def read_large_file(filepath: str, chunk_size: int = 8192):
    """Read large file in chunks (for processing big documents)."""
    with open(filepath, "r") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk
```

---

## 5. Modules & Packages

```python
# Project structure:
# ai_platform/
# ├── __init__.py
# ├── config.py
# ├── services/
# │   ├── __init__.py
# │   ├── embedding.py
# │   └── llm.py
# └── models/
#     ├── __init__.py
#     └── document.py

# __init__.py - makes directory a package
# ai_platform/services/__init__.py
from .embedding import EmbeddingService
from .llm import LLMService

__all__ = ["EmbeddingService", "LLMService"]

# Importing
from ai_platform.services import EmbeddingService
from ai_platform.models.document import Document
from ai_platform.config import Settings

# Relative imports (within same package)
# In ai_platform/services/llm.py:
from .embedding import EmbeddingService  # Same directory
from ..models.document import Document   # Parent directory
from ..config import Settings            # Parent directory
```

---

## Exercises

### Exercise 1: Build Useful Decorators
```python
# Build these decorators:
# 1. @cache_with_ttl(seconds=300) - cache with expiration
# 2. @log_errors - catch and log exceptions, optionally re-raise
# 3. @validate_types - validate function argument types at runtime
# 4. @deprecated(message="Use new_func instead") - warn about deprecated functions

# TODO: Implement all 4
```

### Exercise 2: Build a Type-Safe API Response System
```python
# Using TypedDict and generics, build:
# 1. APIResponse[T] generic class with: data, status, message, errors
# 2. PaginatedResponse[T] with: items, total, page, per_page
# 3. Helper functions: success_response(), error_response(), paginated_response()

# TODO: Implement
```

---

## Key Takeaways for Day 6
1. **Decorators** = Python's middleware/wrapper pattern
2. Use `@wraps(func)` to preserve function metadata
3. **Type hints** make Python feel like TypeScript
4. Use **TypedDict** for typed dictionaries
5. **Generators** for memory-efficient processing
6. **Context managers** for resource management
7. Know the difference between `*args` and `**kwargs`
