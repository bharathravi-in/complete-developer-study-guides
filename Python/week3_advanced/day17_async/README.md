# Day 17 - Async Programming

## Topics Covered
- async/await syntax
- asyncio module
- Event loop
- Async context managers
- Practical async patterns

## Key Concepts

### Coroutine
```python
async def fetch_data():
    await some_io_operation()
    return data
```

### Running Async Code
```python
import asyncio

# Python 3.7+
asyncio.run(main())

# Or with event loop
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

### When to Use Async
- Many concurrent I/O operations
- Network requests
- Database queries
- File I/O

## Run
```bash
python practice.py
python async_api_caller.py
```
