# Day 2 - Data Types Deep Dive

## Topics Covered
- int, float, bool
- str (immutability)
- list, tuple, set, dict
- NoneType
- Mutable vs Immutable
- Memory references
- id() and `is` vs `==`

## Data Types Summary

| Type | Mutable | Ordered | Duplicates | Example |
|------|---------|---------|------------|---------|
| int | ❌ | N/A | N/A | `42` |
| float | ❌ | N/A | N/A | `3.14` |
| bool | ❌ | N/A | N/A | `True` |
| str | ❌ | ✅ | ✅ | `"hello"` |
| list | ✅ | ✅ | ✅ | `[1, 2, 3]` |
| tuple | ❌ | ✅ | ✅ | `(1, 2, 3)` |
| set | ✅ | ❌ | ❌ | `{1, 2, 3}` |
| dict | ✅ | ✅* | Keys ❌ | `{"a": 1}` |
| NoneType | ❌ | N/A | N/A | `None` |

*dict is ordered since Python 3.7+

## Key Concepts

### `is` vs `==`
- `==` checks **value equality**
- `is` checks **identity** (same object in memory)

### id()
- Returns the memory address of an object
- Two objects with same `id()` are the same object

## Run
```bash
python practice.py
```
