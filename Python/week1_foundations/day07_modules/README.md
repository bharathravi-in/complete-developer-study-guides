# Day 7 - Modules & Packages

## Topics Covered
- import statements
- from ... import
- `__name__ == "__main__"`
- Creating modules
- Package structure
- pip

## Module vs Package
- **Module**: Single Python file (.py)
- **Package**: Directory with `__init__.py`

## Import Styles
```python
import math                    # Full import
from math import sqrt          # Specific import
from math import sqrt as s     # With alias
from math import *             # Import all (avoid!)
```

## Package Structure
```
mypackage/
├── __init__.py
├── module1.py
├── module2.py
└── subpackage/
    ├── __init__.py
    └── module3.py
```

## Practice Project
Build a CLI TODO App with:
- Add, list, complete, delete tasks
- Persistent storage (JSON)
- Modular structure

## Run
```bash
python practice.py
cd cli_todo_app && python -m todo
```
