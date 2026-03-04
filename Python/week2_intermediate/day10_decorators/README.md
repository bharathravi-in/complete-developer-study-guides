# Day 10 - Decorators

## Topics Covered
- Function decorators
- functools.wraps
- Class decorators
- Decorators with arguments

## Decorator Pattern
```python
@decorator
def function():
    pass

# Equivalent to:
function = decorator(function)
```

## Common Use Cases
- Logging
- Timing/profiling
- Caching
- Authentication
- Rate limiting
- Validation

## Run
```bash
python practice.py
python logging_decorator.py
```
