# Day 8 - Object-Oriented Programming Basics

## Topics Covered
- Classes
- `__init__` constructor
- Instance vs class variables
- Methods (instance, class, static)
- Dunder/magic methods

## Key Concepts

### Class vs Instance Variables
```python
class Dog:
    species = "Canis familiaris"  # Class variable
    
    def __init__(self, name):
        self.name = name  # Instance variable
```

### Method Types
- **Instance method**: `def method(self)` - access instance
- **Class method**: `@classmethod def method(cls)` - access class
- **Static method**: `@staticmethod def method()` - no access

### Common Dunder Methods
| Method | Purpose |
|--------|---------|
| `__init__` | Constructor |
| `__str__` | String representation (user) |
| `__repr__` | String representation (dev) |
| `__eq__` | Equality comparison |
| `__hash__` | Hash for dict keys |
| `__len__` | Length |
| `__getitem__` | Index access |

## Run
```bash
python practice.py
```
