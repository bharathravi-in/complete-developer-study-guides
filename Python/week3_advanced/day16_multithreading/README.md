# Day 16 - Multithreading & Multiprocessing

## Topics Covered
- threading module
- multiprocessing module
- Thread vs Process
- When to use what?

## Quick Guide
| Use Case | Solution |
|----------|----------|
| I/O-bound (network, file) | Threading / Asyncio |
| CPU-bound (computation) | Multiprocessing |
| Shared state needed | Threading with locks |
| Independent tasks | Multiprocessing |

## Key Concepts
- Threads share memory space
- Processes have separate memory
- GIL limits threading for CPU-bound tasks
- Use `concurrent.futures` for simpler API

## Run
```bash
python practice.py
```
