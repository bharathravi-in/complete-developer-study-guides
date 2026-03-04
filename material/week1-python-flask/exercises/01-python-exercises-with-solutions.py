#!/usr/bin/env python3
"""
Week 1 Exercises with Solutions — Python Fundamentals
Run: python 01-python-exercises-with-solutions.py
"""

# ============================================================
# EXERCISE 1: Data Structures & Comprehensions
# ============================================================

def exercise_1_word_frequency(text: str) -> dict[str, int]:
    """Count word frequency in a text string. Return top 5 words.
    
    Example:
        >>> exercise_1_word_frequency("the cat sat on the mat the cat")
        {'the': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1}
    """
    from collections import Counter
    words = text.lower().split()
    counts = Counter(words)
    return dict(counts.most_common(5))


def exercise_2_flatten_nested(nested: list) -> list:
    """Flatten a deeply nested list using recursion.
    
    Example:
        >>> exercise_2_flatten_nested([1, [2, [3, 4]], [5, 6]])
        [1, 2, 3, 4, 5, 6]
    """
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(exercise_2_flatten_nested(item))
        else:
            result.append(item)
    return result


def exercise_3_matrix_operations():
    """Create a 3x3 matrix and perform operations using list comprehensions."""
    # Create
    matrix = [[i * 3 + j + 1 for j in range(3)] for i in range(3)]
    # [[1, 2, 3], [4, 5, 6], [7, 8, 9]]

    # Transpose
    transposed = [[row[i] for row in matrix] for i in range(3)]
    # [[1, 4, 7], [2, 5, 8], [3, 6, 9]]

    # Flatten
    flat = [val for row in matrix for val in row]
    # [1, 2, 3, 4, 5, 6, 7, 8, 9]

    # Sum diagonals
    main_diagonal = sum(matrix[i][i] for i in range(3))  # 15
    anti_diagonal = sum(matrix[i][2-i] for i in range(3))  # 15

    return {
        "matrix": matrix,
        "transposed": transposed,
        "flat": flat,
        "main_diagonal": main_diagonal,
        "anti_diagonal": anti_diagonal,
    }


# ============================================================
# EXERCISE 2: OOP & Design Patterns
# ============================================================

from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Protocol


# Strategy Pattern — different chunking strategies
class ChunkStrategy(Protocol):
    def chunk(self, text: str, size: int) -> list[str]: ...


class FixedChunker:
    def chunk(self, text: str, size: int) -> list[str]:
        words = text.split()
        return [' '.join(words[i:i+size]) for i in range(0, len(words), size)]


class SentenceChunker:
    def chunk(self, text: str, size: int) -> list[str]:
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks, current, count = [], [], 0
        for s in sentences:
            wc = len(s.split())
            if count + wc > size and current:
                chunks.append(' '.join(current))
                current, count = [], 0
            current.append(s)
            count += wc
        if current:
            chunks.append(' '.join(current))
        return chunks


@dataclass
class Document:
    title: str
    content: str
    tags: list[str] = field(default_factory=list)

    @property
    def word_count(self) -> int:
        return len(self.content.split())

    def chunk(self, strategy: ChunkStrategy, size: int = 100) -> list[str]:
        return strategy.chunk(self.content, size)


# Observer Pattern — notify on document events
class DocumentObserver(ABC):
    @abstractmethod
    def on_event(self, event: str, doc: Document) -> None: ...


class LoggingObserver(DocumentObserver):
    def __init__(self):
        self.events: list[str] = []

    def on_event(self, event: str, doc: Document) -> None:
        msg = f"[{event}] {doc.title}"
        self.events.append(msg)
        print(msg)


class DocumentManager:
    def __init__(self):
        self._documents: dict[str, Document] = {}
        self._observers: list[DocumentObserver] = []

    def add_observer(self, observer: DocumentObserver) -> None:
        self._observers.append(observer)

    def _notify(self, event: str, doc: Document) -> None:
        for obs in self._observers:
            obs.on_event(event, doc)

    def add(self, doc: Document) -> None:
        self._documents[doc.title] = doc
        self._notify("ADDED", doc)

    def remove(self, title: str) -> None:
        if title in self._documents:
            doc = self._documents.pop(title)
            self._notify("REMOVED", doc)

    def search(self, keyword: str) -> list[Document]:
        return [
            d for d in self._documents.values()
            if keyword.lower() in d.content.lower()
        ]


# ============================================================
# EXERCISE 3: Async & Concurrency
# ============================================================

import asyncio


async def exercise_async_fetcher(urls: list[str]) -> list[dict]:
    """Simulate fetching multiple URLs concurrently with error handling."""

    async def fetch_one(url: str) -> dict:
        # Simulate network delay
        delay = len(url) % 3 * 0.1 + 0.1
        await asyncio.sleep(delay)
        if "error" in url:
            raise ConnectionError(f"Failed to fetch {url}")
        return {"url": url, "status": 200, "size": len(url) * 100}

    tasks = [fetch_one(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    processed = []
    for url, result in zip(urls, results):
        if isinstance(result, Exception):
            processed.append({"url": url, "status": "error", "error": str(result)})
        else:
            processed.append(result)
    return processed


async def exercise_rate_limited_processor(items: list[str], max_concurrent: int = 3) -> list[str]:
    """Process items with concurrency limit using semaphore."""
    semaphore = asyncio.Semaphore(max_concurrent)
    results = []

    async def process(item: str) -> str:
        async with semaphore:
            await asyncio.sleep(0.1)  # simulate work
            return item.upper()

    tasks = [process(item) for item in items]
    results = await asyncio.gather(*tasks)
    return list(results)


# ============================================================
# EXERCISE 4: Decorators
# ============================================================

import functools
import time
from typing import Callable, Any


def timer(func: Callable) -> Callable:
    """Decorator that measures execution time."""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"⏱️  {func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


def retry(max_attempts: int = 3, delay: float = 0.1):
    """Decorator that retries on failure with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts:
                        wait = delay * (2 ** (attempt - 1))
                        print(f"Retry {attempt}/{max_attempts} after {wait}s...")
                        time.sleep(wait)
            raise last_error  # type: ignore
        return wrapper
    return decorator


def cache(ttl: int = 60):
    """Decorator that caches results with TTL (in seconds)."""
    _cache: dict[str, tuple[Any, float]] = {}

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = f"{args}:{kwargs}"
            now = time.time()
            if key in _cache:
                result, cached_at = _cache[key]
                if now - cached_at < ttl:
                    print(f"  Cache HIT for {func.__name__}")
                    return result
            result = func(*args, **kwargs)
            _cache[key] = (result, now)
            print(f"  Cache MISS for {func.__name__}")
            return result
        return wrapper
    return decorator


def validate_types(**expected_types: type):
    """Decorator that validates argument types at runtime."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            for param_name, expected_type in expected_types.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not isinstance(value, expected_type):
                        raise TypeError(
                            f"Expected {param_name} to be {expected_type.__name__}, "
                            f"got {type(value).__name__}"
                        )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ============================================================
# EXERCISE 5: File Handling & Data Pipeline
# ============================================================

import csv
import json
from pathlib import Path
import tempfile


def exercise_data_pipeline():
    """Build a mini ETL: read CSV → transform → write JSON."""
    # Create sample CSV
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['name', 'role', 'experience'])
        writer.writerow(['Bharath', 'Frontend Lead', '8'])
        writer.writerow(['Alice', 'AI Engineer', '5'])
        writer.writerow(['Bob', 'Backend Dev', '3'])
        csv_path = Path(f.name)

    # Read CSV
    records = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append({
                "name": row["name"],
                "role": row["role"],
                "experience_years": int(row["experience"]),
                "seniority": "senior" if int(row["experience"]) >= 5 else "mid",
            })

    # Write JSON
    json_path = csv_path.with_suffix('.json')
    with open(json_path, 'w') as f:
        json.dump(records, f, indent=2)

    # Read back and verify
    with open(json_path) as f:
        loaded = json.load(f)

    # Cleanup
    csv_path.unlink()
    json_path.unlink()

    return loaded


# ============================================================
# EXERCISE 6: Testing Helpers (to use with pytest)
# ============================================================

@timer
@cache(ttl=10)
def expensive_computation(n: int) -> int:
    """Simulate expensive work."""
    total = 0
    for i in range(n * 1000):
        total += i
    return total


@validate_types(name=str, age=int)
def create_user(name: str, age: int) -> dict:
    return {"name": name, "age": age}


# ============================================================
# RUN ALL EXERCISES
# ============================================================

def run_all():
    print("=" * 60)
    print("EXERCISE 1: Data Structures")
    print("=" * 60)

    text = "the quick brown fox jumps over the lazy dog the fox"
    print(f"Word frequency: {exercise_1_word_frequency(text)}")
    print(f"Flatten: {exercise_2_flatten_nested([1, [2, [3, 4]], [5, [6, [7]]]])}")
    print(f"Matrix ops: {exercise_3_matrix_operations()}")

    print("\n" + "=" * 60)
    print("EXERCISE 2: OOP & Patterns")
    print("=" * 60)

    doc = Document("AI Intro", "Machine learning is a subset of artificial intelligence. It uses data to learn patterns.", ["ai", "ml"])
    print(f"Word count: {doc.word_count}")
    print(f"Fixed chunks: {doc.chunk(FixedChunker(), 5)}")
    print(f"Sentence chunks: {doc.chunk(SentenceChunker(), 8)}")

    manager = DocumentManager()
    logger = LoggingObserver()
    manager.add_observer(logger)
    manager.add(doc)
    manager.add(Document("RAG Guide", "RAG combines retrieval with generation for accurate answers."))
    results = manager.search("machine")
    print(f"Search results: {[d.title for d in results]}")
    print(f"Events logged: {logger.events}")

    print("\n" + "=" * 60)
    print("EXERCISE 3: Async")
    print("=" * 60)

    urls = ["https://api.example.com/data", "https://api.example.com/error", "https://openai.com/api"]
    results = asyncio.run(exercise_async_fetcher(urls))
    for r in results:
        print(f"  {r}")

    items = [f"item_{i}" for i in range(10)]
    processed = asyncio.run(exercise_rate_limited_processor(items, max_concurrent=3))
    print(f"Processed: {processed}")

    print("\n" + "=" * 60)
    print("EXERCISE 4: Decorators")
    print("=" * 60)

    # Timer + Cache
    print("First call (cache miss):")
    expensive_computation(100)
    print("Second call (cache hit):")
    expensive_computation(100)

    # Type validation
    print(f"\nValid: {create_user('Bharath', 28)}")
    try:
        create_user('Bharath', '28')  # type: ignore — intentional for testing
    except TypeError as e:
        print(f"Type error caught: {e}")

    print("\n" + "=" * 60)
    print("EXERCISE 5: Data Pipeline")
    print("=" * 60)

    pipeline_result = exercise_data_pipeline()
    for r in pipeline_result:
        print(f"  {r}")

    print("\n" + "=" * 60)
    print("✅ ALL EXERCISES COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    run_all()
