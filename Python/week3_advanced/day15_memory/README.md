# Day 15 - Python Memory Model

## Topics Covered
- Stack vs Heap
- Garbage Collection
- Reference Counting
- Global Interpreter Lock (GIL)

## Key Concepts

### Memory Allocation
- **Stack**: Local variables, function calls (small, fast)
- **Heap**: Objects, data structures (managed by GC)

### Reference Counting
- Every object has a reference count
- When count reaches 0, memory is freed
- Circular references handled by GC

### GIL (Global Interpreter Lock)
- Only one thread executes Python bytecode at a time
- Affects CPU-bound tasks
- I/O-bound tasks can still benefit from threading

## Interview Questions
- What is the GIL and why does it exist?
- How does Python manage memory?
- What causes memory leaks in Python?

## Run
```bash
python practice.py
```
