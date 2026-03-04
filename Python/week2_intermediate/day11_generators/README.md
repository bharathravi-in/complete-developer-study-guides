# Day 11 - Generators & Iterators

## Topics Covered
- yield statement
- Generator expressions
- iter() and next()
- Lazy evaluation
- Generator methods (send, throw, close)

## Key Concepts

### Generator vs List
```python
# List - all values in memory
squares_list = [x**2 for x in range(1000000)]

# Generator - values generated on demand
squares_gen = (x**2 for x in range(1000000))
```

### Memory Efficiency
- Generators are memory-efficient for large datasets
- Values computed lazily (on-demand)
- Can only iterate once

## Run
```bash
python practice.py
```
