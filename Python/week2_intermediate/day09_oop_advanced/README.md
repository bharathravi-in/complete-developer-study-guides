# Day 9 - OOP Advanced

## Topics Covered
- Inheritance
- Multiple inheritance
- Method Resolution Order (MRO)
- Encapsulation
- Polymorphism
- Abstraction

## Key Concepts

### Inheritance
```python
class Animal:
    pass

class Dog(Animal):  # Single inheritance
    pass

class Pet(Animal, Domestic):  # Multiple inheritance
    pass
```

### MRO (Method Resolution Order)
- Python uses C3 Linearization
- Check with `ClassName.__mro__` or `ClassName.mro()`

### Encapsulation Convention
- `public` - accessible everywhere
- `_protected` - convention for internal use
- `__private` - name mangled to `_ClassName__private`

## Run
```bash
python practice.py
```
