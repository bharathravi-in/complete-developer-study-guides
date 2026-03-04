# Advanced Python — Design Patterns, Metaclasses & Performance

> Topics NOT covered in days 1-6 that come up in senior interviews.

---

## 1. Design Patterns in Python

### Singleton (Thread-safe)
```python
import threading

class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-check
                    cls._instance = super().__new__(cls)
        return cls._instance

# Usage
s1 = Singleton()
s2 = Singleton()
assert s1 is s2  # True — same instance

# Simpler: module-level singleton (Pythonic way)
# config.py
class _Config:
    def __init__(self):
        self.db_url = "postgresql://..."
config = _Config()  # Module-level = singleton
```

### Factory Pattern
```python
from abc import ABC, abstractmethod

class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> list[float]: ...

class OpenAIEmbedding(EmbeddingProvider):
    def embed(self, text: str) -> list[float]:
        # Call OpenAI API
        return [0.1] * 1536

class LocalEmbedding(EmbeddingProvider):
    def embed(self, text: str) -> list[float]:
        # Use sentence-transformers
        return [0.1] * 384

class EmbeddingFactory:
    _providers = {
        "openai": OpenAIEmbedding,
        "local": LocalEmbedding,
    }

    @classmethod
    def create(cls, provider: str) -> EmbeddingProvider:
        if provider not in cls._providers:
            raise ValueError(f"Unknown provider: {provider}")
        return cls._providers[provider]()

# Usage
embedder = EmbeddingFactory.create("openai")
vector = embedder.embed("hello world")
```

### Strategy Pattern
```python
from typing import Protocol

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
        # ... group sentences into chunks ...
        return sentences

# The pipeline doesn't care which strategy
def process_document(text: str, strategy: ChunkStrategy, size: int = 500) -> list[str]:
    return strategy.chunk(text, size)

# Swap strategies at runtime
chunks = process_document(text, FixedChunker(), 200)
chunks = process_document(text, SentenceChunker(), 200)
```

### Repository Pattern
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class User:
    id: str
    email: str
    name: str

class UserRepository(ABC):
    @abstractmethod
    def get(self, id: str) -> User | None: ...
    @abstractmethod
    def save(self, user: User) -> None: ...
    @abstractmethod
    def delete(self, id: str) -> None: ...

class PostgresUserRepo(UserRepository):
    def __init__(self, db):
        self.db = db
    def get(self, id: str) -> User | None:
        row = self.db.query("SELECT * FROM users WHERE id = %s", id)
        return User(**row) if row else None
    def save(self, user: User) -> None:
        self.db.execute("INSERT INTO users ...", user)
    def delete(self, id: str) -> None:
        self.db.execute("DELETE FROM users WHERE id = %s", id)

class InMemoryUserRepo(UserRepository):
    """For testing — no DB needed."""
    def __init__(self):
        self._store: dict[str, User] = {}
    def get(self, id: str) -> User | None:
        return self._store.get(id)
    def save(self, user: User) -> None:
        self._store[user.id] = user
    def delete(self, id: str) -> None:
        self._store.pop(id, None)
```

### Dependency Injection
```python
class RAGService:
    """Dependencies are injected, not created internally."""
    def __init__(
        self,
        embedder: EmbeddingProvider,
        vector_db: VectorDBProvider,
        llm: LLMProvider,
        cache: CacheProvider,
    ):
        self.embedder = embedder
        self.vector_db = vector_db
        self.llm = llm
        self.cache = cache

# Production
rag = RAGService(
    embedder=OpenAIEmbedding(),
    vector_db=QdrantProvider(),
    llm=OpenAILLM(),
    cache=RedisCache(),
)

# Testing — swap with mocks
rag = RAGService(
    embedder=MockEmbedding(),
    vector_db=InMemoryVectorDB(),
    llm=MockLLM(),
    cache=InMemoryCache(),
)
```

---

## 2. Metaclasses & Descriptors

### Metaclasses (How classes are created)
```python
class ValidatedMeta(type):
    """Metaclass that enforces all methods have type hints."""
    def __new__(mcs, name, bases, namespace):
        import inspect
        for attr_name, attr_value in namespace.items():
            if callable(attr_value) and not attr_name.startswith('_'):
                sig = inspect.signature(attr_value)
                for param_name, param in sig.parameters.items():
                    if param_name == 'self':
                        continue
                    if param.annotation is inspect.Parameter.empty:
                        raise TypeError(
                            f"{name}.{attr_name}: parameter '{param_name}' missing type hint"
                        )
        return super().__new__(mcs, name, bases, namespace)

class MyService(metaclass=ValidatedMeta):
    def process(self, text: str) -> str:  # OK — has type hints
        return text.upper()

# class BadService(metaclass=ValidatedMeta):
#     def process(self, text):  # FAILS — missing type hint
#         return text.upper()
```

### Descriptors (Property-like behavior)
```python
class Validated:
    """Descriptor that validates values on assignment."""
    def __init__(self, min_val=None, max_val=None):
        self.min_val = min_val
        self.max_val = max_val

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, obj, value):
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f"{self.name} must be >= {self.min_val}")
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f"{self.name} must be <= {self.max_val}")
        obj.__dict__[self.name] = value

    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name)

class ChunkConfig:
    chunk_size = Validated(min_val=50, max_val=2000)
    overlap = Validated(min_val=0, max_val=500)

    def __init__(self, chunk_size: int, overlap: int):
        self.chunk_size = chunk_size  # Triggers __set__
        self.overlap = overlap

config = ChunkConfig(500, 50)  # OK
# config = ChunkConfig(10, 50)  # ValueError: chunk_size must be >= 50
```

---

## 3. Performance Optimization

### Profiling
```python
# cProfile — find bottlenecks
import cProfile
cProfile.run('my_function()', sort='cumulative')

# line_profiler — line-by-line timing
# pip install line_profiler
# @profile  # Add decorator
# kernprof -l -v script.py

# Memory profiling
# pip install memory_profiler
# @profile
# python -m memory_profiler script.py

# timeit — quick benchmarks
import timeit
timeit.timeit('"-".join(str(n) for n in range(100))', number=10000)
```

### Slots (Memory optimization)
```python
class RegularChunk:
    def __init__(self, text, score):
        self.text = text
        self.score = score
# Each instance has a __dict__ → ~200+ bytes overhead

class SlottedChunk:
    __slots__ = ('text', 'score')
    def __init__(self, text, score):
        self.text = text
        self.score = score
# No __dict__ → ~50% less memory per instance
# For 1M chunks: saves ~100MB+ RAM
```

### Generator Pipelines (Memory-efficient processing)
```python
from pathlib import Path
from typing import Iterator

def read_documents(directory: Path) -> Iterator[str]:
    """Lazy — reads one file at a time."""
    for path in directory.rglob("*.txt"):
        yield path.read_text()

def clean_texts(texts: Iterator[str]) -> Iterator[str]:
    """Process without loading all into memory."""
    for text in texts:
        yield text.strip().lower()

def chunk_texts(texts: Iterator[str], size: int = 500) -> Iterator[list[str]]:
    """Chunk each text."""
    for text in texts:
        words = text.split()
        yield [' '.join(words[i:i+size]) for i in range(0, len(words), size)]

# Pipeline — processes ONE document at a time
# Works for millions of documents without running out of memory
docs = read_documents(Path("./documents"))
cleaned = clean_texts(docs)
chunks = chunk_texts(cleaned)

for doc_chunks in chunks:
    for chunk in doc_chunks:
        embed_and_store(chunk)
```

### LRU Cache (Built-in memoization)
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_embedding(text: str) -> tuple[float, ...]:
    """Cache embeddings — tuple because lists aren't hashable."""
    vector = embedding_model.encode(text)
    return tuple(vector)

# Check cache stats
print(get_embedding.cache_info())
# CacheInfo(hits=450, misses=550, maxsize=1000, currsize=550)
```

### Concurrent Batch Processing
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def batch_embed(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """Process embeddings in batches with concurrency control."""
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent API calls
    results = []

    async def embed_batch(batch: list[str]) -> list[list[float]]:
        async with semaphore:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                return await loop.run_in_executor(
                    pool, lambda: model.encode(batch).tolist()
                )

    batches = [texts[i:i+batch_size] for i in range(0, len(texts), batch_size)]
    tasks = [embed_batch(batch) for batch in batches]
    batch_results = await asyncio.gather(*tasks)

    for batch_result in batch_results:
        results.extend(batch_result)
    return results
```

---

## 4. Advanced Type Hints

### TypeVar & Generics
```python
from typing import TypeVar, Generic, TypedDict

T = TypeVar('T')

class Result(Generic[T]):
    """Generic result type — like Result<T> in TypeScript."""
    def __init__(self, data: T | None = None, error: str | None = None):
        self.data = data
        self.error = error
        self.ok = error is None

    @classmethod
    def success(cls, data: T) -> 'Result[T]':
        return cls(data=data)

    @classmethod
    def failure(cls, error: str) -> 'Result[T]':
        return cls(error=error)

# Typed results
user_result: Result[User] = Result.success(User(id="1", name="Bharath"))
chunk_result: Result[list[Chunk]] = Result.failure("Embedding failed")
```

### TypedDict (Typed dictionaries)
```python
from typing import TypedDict, NotRequired

class RAGResponse(TypedDict):
    question: str
    answer: str
    sources: list[dict]
    confidence: float
    cached: NotRequired[bool]  # Optional key

def query(q: str) -> RAGResponse:
    return {
        "question": q,
        "answer": "Python is...",
        "sources": [{"text": "...", "score": 0.9}],
        "confidence": 0.95,
    }
```

### Protocols (Structural typing — like TS interfaces)
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Embeddable(Protocol):
    def to_text(self) -> str: ...

class Document:
    def __init__(self, content: str):
        self.content = content
    def to_text(self) -> str:
        return self.content

class ChatMessage:
    def __init__(self, role: str, text: str):
        self.role = role
        self.text = text
    def to_text(self) -> str:
        return f"{self.role}: {self.text}"

def embed_item(item: Embeddable) -> list[float]:
    """Works with any object that has to_text()."""
    text = item.to_text()
    return model.encode(text).tolist()

# Both work — no inheritance needed (duck typing with type safety)
embed_item(Document("hello"))
embed_item(ChatMessage("user", "hello"))
isinstance(Document("hi"), Embeddable)  # True at runtime
```

---

## 5. Context Managers (Advanced)

### Async Context Managers
```python
class AsyncDBConnection:
    async def __aenter__(self):
        self.conn = await create_connection()
        return self.conn

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.conn.close()

async def query():
    async with AsyncDBConnection() as conn:
        result = await conn.fetch("SELECT * FROM users")
```

### Nested Context Manager
```python
from contextlib import contextmanager
import time

@contextmanager
def timed_operation(name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"⏱️  {name}: {elapsed:.3f}s")

@contextmanager
def error_boundary(operation: str):
    try:
        yield
    except Exception as e:
        print(f"❌ {operation} failed: {e}")

# Compose
with timed_operation("RAG query"):
    with error_boundary("embedding"):
        vector = embed(query)
    with error_boundary("search"):
        results = search(vector)
    with error_boundary("generation"):
        answer = generate(query, results)
```

---

## 6. Python Internals (Interview Gold)

### How `import` Works
```
1. Check sys.modules cache
2. Find the module (sys.path)
3. Load and compile to bytecode (.pyc)
4. Execute module code
5. Cache in sys.modules

Key: Module code runs ONCE on first import.
     Subsequent imports return cached module.
     This is why module-level singletons work.
```

### How Garbage Collection Works
```
Reference Counting (primary):
  - Every object has a reference count
  - When count reaches 0, object is freed
  - Immediate cleanup for most objects

Generational GC (secondary):
  - Handles circular references
  - 3 generations: gen0 (new), gen1, gen2 (old)
  - gen0 collected frequently, gen2 rarely
  - Objects that survive collection move to next gen

For AI: NumPy arrays use C memory management
  - Not tracked by Python GC
  - Must be explicitly freed or rely on __del__
  - Use gc.collect() if memory pressure
```

### Dunder Methods Cheat Sheet
```python
class AIResponse:
    def __init__(self, text, score): ...       # Constructor
    def __repr__(self): ...                     # Debug string
    def __str__(self): ...                      # User string
    def __len__(self): ...                      # len(obj)
    def __bool__(self): ...                     # if obj:
    def __eq__(self, other): ...                # obj == other
    def __lt__(self, other): ...                # obj < other (enables sorting)
    def __hash__(self): ...                     # hash(obj) (for sets/dicts)
    def __getitem__(self, key): ...             # obj[key]
    def __iter__(self): ...                     # for x in obj:
    def __contains__(self, item): ...           # item in obj
    def __call__(self, *args): ...              # obj()
    def __enter__(self): ...                    # with obj:
    def __exit__(self, *args): ...              # end of with block
    def __add__(self, other): ...               # obj + other
```

---

## Key Takeaways
1. **Design patterns** in Python are simpler than Java — use Protocols, not interfaces
2. **Metaclasses** are rarely needed — use decorators and descriptors instead
3. **Performance**: Profile first, optimize second. Use generators for large data.
4. **Type hints**: Use TypeVar, Generic, Protocol for production code
5. **Memory**: `__slots__` for data-heavy classes, generators for pipelines
6. **Internals**: Understand GIL, GC, imports — they come up in senior interviews
