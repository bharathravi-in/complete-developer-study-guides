# Day 13 - Type Hints & Static Typing

## Topics Covered
- typing module
- Optional, Union
- TypedDict
- dataclasses
- Pydantic

## Why Type Hints?
1. Better IDE support (autocomplete, error detection)
2. Self-documenting code
3. Catch bugs before runtime
4. Enable static type checking (mypy)

## Common Types
```python
from typing import List, Dict, Optional, Union, Callable

def func(
    items: List[int],
    config: Dict[str, Any],
    callback: Optional[Callable[[int], str]] = None
) -> Union[str, None]:
    pass
```

## Run
```bash
python practice.py
python pydantic_demo.py
```
