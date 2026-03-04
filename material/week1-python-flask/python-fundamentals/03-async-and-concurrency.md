# Day 3: Async & Concurrency in Python

## Why This Matters for AI Engineering
- API calls to LLMs are slow (2-10 seconds)
- Embedding generation for many documents
- Multiple vector DB queries
- Parallel processing of chunks
- Background task processing

---

## Python Concurrency Model vs JavaScript

| Feature | JavaScript | Python |
|---------|-----------|--------|
| Model | Single-threaded, event loop | GIL (Global Interpreter Lock) |
| Async | Built-in async/await | asyncio library |
| Threads | Web Workers | threading module |
| Parallel | Worker threads | multiprocessing |
| Default | Everything is async | Everything is sync |

### What is the GIL?
**Interview Question Alert!**

The GIL (Global Interpreter Lock) prevents multiple threads from executing Python bytecode simultaneously. This means:
- CPU-bound tasks: Use `multiprocessing` (separate processes)
- I/O-bound tasks: Use `asyncio` or `threading` (both work fine!)
- AI API calls are I/O-bound → `asyncio` is perfect

---

## 1. Async/Await Basics

```python
import asyncio

# JS:
# async function fetchData() {
#   const response = await fetch(url);
#   return response.json();
# }

# Python:
async def fetch_data() -> dict:
    """Async function (coroutine)."""
    await asyncio.sleep(1)  # Simulate API call
    return {"status": "success", "data": "AI response"}

# Running async code
async def main():
    result = await fetch_data()
    print(result)

# Entry point
asyncio.run(main())
```

## 2. Running Multiple Async Tasks

```python
import asyncio
import time

async def call_llm(prompt: str) -> str:
    """Simulate LLM API call (2 second delay)."""
    print(f"Calling LLM with: {prompt[:30]}...")
    await asyncio.sleep(2)  # Simulate network delay
    return f"Response to: {prompt}"

async def generate_embedding(text: str) -> list[float]:
    """Simulate embedding generation."""
    print(f"Generating embedding for: {text[:30]}...")
    await asyncio.sleep(1)
    return [0.1, 0.2, 0.3]

# ❌ Sequential (slow): 6 seconds
async def sequential():
    start = time.time()
    r1 = await call_llm("What is AI?")
    r2 = await call_llm("What is ML?")
    r3 = await call_llm("What is DL?")
    print(f"Sequential: {time.time() - start:.1f}s")

# ✅ Parallel (fast): 2 seconds
async def parallel():
    start = time.time()
    results = await asyncio.gather(
        call_llm("What is AI?"),
        call_llm("What is ML?"),
        call_llm("What is DL?"),
    )
    print(f"Parallel: {time.time() - start:.1f}s")
    return results

# ✅ Parallel with error handling
async def parallel_safe():
    results = await asyncio.gather(
        call_llm("What is AI?"),
        call_llm("What is ML?"),
        call_llm("What is DL?"),
        return_exceptions=True  # Don't fail all if one fails
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"Error: {r}")
        else:
            print(f"Success: {r}")

asyncio.run(parallel())
```

## 3. Async Context Managers

```python
import asyncio
from contextlib import asynccontextmanager

# Async context manager (like async with in JS)
class AsyncDBConnection:
    """Simulated async database connection."""
    
    async def __aenter__(self):
        """Called on entering 'async with'."""
        print("Connecting to DB...")
        await asyncio.sleep(0.5)
        self.connected = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Called on exiting 'async with'."""
        print("Closing DB connection...")
        self.connected = False
    
    async def query(self, sql: str) -> list:
        return [{"id": 1, "name": "test"}]

# Usage
async def main():
    async with AsyncDBConnection() as db:
        results = await db.query("SELECT * FROM users")
        print(results)
    # Connection auto-closed here

# Simpler way with decorator
@asynccontextmanager
async def get_redis_client():
    """Async context manager using decorator."""
    print("Connecting to Redis...")
    client = {"host": "localhost", "port": 6379}  # Simplified
    try:
        yield client
    finally:
        print("Closing Redis connection...")

async def main2():
    async with get_redis_client() as redis:
        print(f"Using Redis at {redis['host']}")
```

## 4. Async Iterators (Processing Streams)

```python
import asyncio

async def stream_llm_response(prompt: str):
    """Simulate streaming LLM response (like ChatGPT's streaming)."""
    words = "The quick brown fox jumps over the lazy dog".split()
    for word in words:
        await asyncio.sleep(0.1)  # Simulate token delay
        yield word + " "

# Using async for
async def main():
    full_response = ""
    async for token in stream_llm_response("Tell me a story"):
        print(token, end="", flush=True)
        full_response += token
    print(f"\n\nFull: {full_response}")

asyncio.run(main())
```

## 5. Async Queues (Producer-Consumer Pattern)

```python
import asyncio

async def document_producer(queue: asyncio.Queue, documents: list[str]):
    """Producer: Add documents to processing queue."""
    for doc in documents:
        await queue.put(doc)
        print(f"Queued: {doc[:30]}...")
    
    # Signal we're done
    await queue.put(None)

async def embedding_consumer(queue: asyncio.Queue, results: list):
    """Consumer: Process documents from queue."""
    while True:
        doc = await queue.get()
        if doc is None:
            break
        
        # Simulate embedding generation
        await asyncio.sleep(0.5)
        embedding = [0.1, 0.2, 0.3]  # Simplified
        results.append({"text": doc, "embedding": embedding})
        print(f"Processed: {doc[:30]}...")
        queue.task_done()

async def main():
    documents = [
        "Machine learning is a subset of AI",
        "Deep learning uses neural networks",
        "NLP processes human language",
        "RAG combines retrieval and generation",
    ]
    
    queue = asyncio.Queue(maxsize=10)
    results = []
    
    # Run producer and consumer concurrently
    await asyncio.gather(
        document_producer(queue, documents),
        embedding_consumer(queue, results),
    )
    
    print(f"\nProcessed {len(results)} documents")

asyncio.run(main())
```

## 6. Threading (For I/O-bound Tasks)

```python
import threading
import time
from concurrent.futures import ThreadPoolExecutor

def fetch_embedding(text: str) -> dict:
    """Synchronous function (simulating API call)."""
    time.sleep(1)  # Simulate network delay
    return {"text": text, "embedding": [0.1, 0.2]}

# Using ThreadPoolExecutor (like Promise.all for sync functions)
def process_documents_threaded(texts: list[str]) -> list[dict]:
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_embedding, texts))
    return results

# Time comparison
texts = ["doc1", "doc2", "doc3", "doc4", "doc5"]

# Sequential: ~5 seconds
start = time.time()
sequential_results = [fetch_embedding(t) for t in texts]
print(f"Sequential: {time.time() - start:.1f}s")

# Threaded: ~1 second
start = time.time()
threaded_results = process_documents_threaded(texts)
print(f"Threaded: {time.time() - start:.1f}s")

# Using submit for more control
def process_with_futures(texts: list[str]) -> list[dict]:
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_embedding, t): t for t in texts}
        results = []
        for future in futures:
            try:
                result = future.result(timeout=10)
                results.append(result)
            except Exception as e:
                print(f"Error processing {futures[future]}: {e}")
    return results
```

## 7. Multiprocessing (For CPU-bound Tasks)

```python
from multiprocessing import Pool, cpu_count
import time

def compute_similarity(args: tuple) -> float:
    """CPU-intensive computation."""
    vec1, vec2 = args
    # Cosine similarity
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a ** 2 for a in vec1) ** 0.5
    norm2 = sum(a ** 2 for a in vec2) ** 0.5
    return dot_product / (norm1 * norm2) if norm1 and norm2 else 0

def parallel_similarity():
    """Compute similarities in parallel using multiple CPU cores."""
    # Generate test data
    import random
    pairs = [
        ([random.random() for _ in range(1536)], 
         [random.random() for _ in range(1536)])
        for _ in range(100)
    ]
    
    # Use all CPU cores
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(compute_similarity, pairs)
    
    print(f"Computed {len(results)} similarities")
    print(f"Average similarity: {sum(results)/len(results):.4f}")

# parallel_similarity()
```

## 8. Real-World Pattern: Async Batch Embedding

```python
import asyncio
from typing import Optional

class BatchEmbeddingService:
    """Real-world pattern for batch embedding generation."""
    
    def __init__(self, batch_size: int = 10, max_concurrent: int = 3):
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def _generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Simulate API call to embedding service."""
        async with self.semaphore:  # Limit concurrent calls
            await asyncio.sleep(0.5)  # Simulate API delay
            return [[0.1 * i for _ in range(768)] for i, _ in enumerate(texts)]
    
    async def embed_documents(self, documents: list[str]) -> list[list[float]]:
        """Process documents in batches with concurrency control."""
        all_embeddings = []
        
        # Split into batches
        batches = [
            documents[i:i + self.batch_size]
            for i in range(0, len(documents), self.batch_size)
        ]
        
        # Process batches concurrently (with semaphore limiting)
        tasks = [self._generate_embeddings(batch) for batch in batches]
        batch_results = await asyncio.gather(*tasks)
        
        for batch_embeddings in batch_results:
            all_embeddings.extend(batch_embeddings)
        
        return all_embeddings


async def main():
    service = BatchEmbeddingService(batch_size=5, max_concurrent=3)
    
    documents = [f"Document {i}" for i in range(25)]
    embeddings = await service.embed_documents(documents)
    print(f"Generated {len(embeddings)} embeddings")

asyncio.run(main())
```

## 9. Async Timeout and Retry Pattern

```python
import asyncio
import random

async def unreliable_api_call(prompt: str) -> str:
    """Simulates an unreliable API that sometimes fails."""
    await asyncio.sleep(random.uniform(0.5, 3.0))
    if random.random() < 0.3:  # 30% failure rate
        raise ConnectionError("API temporarily unavailable")
    return f"Response to: {prompt}"

async def call_with_retry(
    prompt: str,
    max_retries: int = 3,
    timeout: float = 5.0,
    backoff_factor: float = 1.5
) -> str:
    """Retry pattern with exponential backoff and timeout."""
    for attempt in range(max_retries):
        try:
            result = await asyncio.wait_for(
                unreliable_api_call(prompt),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            print(f"Attempt {attempt + 1}: Timeout")
        except ConnectionError as e:
            print(f"Attempt {attempt + 1}: {e}")
        
        if attempt < max_retries - 1:
            wait_time = backoff_factor ** attempt
            print(f"Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)
    
    raise Exception(f"Failed after {max_retries} attempts")

async def main():
    try:
        result = await call_with_retry("What is AI?")
        print(f"Success: {result}")
    except Exception as e:
        print(f"Final failure: {e}")

asyncio.run(main())
```

---

## Exercises

### Exercise 1: Parallel Document Processor
```python
# Build an async document processor that:
# 1. Takes a list of document URLs (simulate with sleep)
# 2. Fetches them in parallel (max 5 concurrent)
# 3. Extracts text from each
# 4. Generates embeddings for each
# 5. Returns results with timing info

# TODO: Implement using asyncio.Semaphore and asyncio.gather
```

### Exercise 2: Async Rate Limiter
```python
# Build a rate limiter class that:
# 1. Limits API calls to N per second
# 2. Queues excess calls
# 3. Works with async functions
# 4. Provides usage statistics

# TODO: Implement
```

### Exercise 3: Producer-Consumer Pipeline
```python
# Build a 3-stage async pipeline:
# Stage 1: Read documents (producer)
# Stage 2: Chunk documents (processor)
# Stage 3: Generate embeddings (consumer)
# 
# Use asyncio.Queue between stages
# Add error handling and progress tracking

# TODO: Implement
```

---

## Key Takeaways for Day 3
1. **asyncio** = Python's event loop (like Node.js event loop)
2. **asyncio.gather()** = `Promise.all()` 
3. **Semaphore** = limit concurrent operations (crucial for API rate limits)
4. **ThreadPoolExecutor** = for running sync I/O functions in parallel
5. **multiprocessing** = for CPU-heavy work (bypasses GIL)
6. **GIL** = only matters for CPU-bound threads, not I/O
7. AI workloads are mostly I/O-bound → asyncio is your friend
8. Always use **retry + timeout** for external API calls
