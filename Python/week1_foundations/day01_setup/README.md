# Day 1 - Python Setup & Basics

## Topics Covered
- Python installation
- Virtual environments (venv, pipenv)
- Running scripts
- Python REPL
- Variables & naming conventions
- Keywords

## Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Deactivate
deactivate
```

## Python Keywords
```python
import keyword
print(keyword.kwlist)
```

## Naming Conventions
- **Variables**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Classes**: `PascalCase`
- **Private**: `_single_leading_underscore`
- **Magic/Dunder**: `__double_underscore__`

## Practice Task
Build a CLI Calculator that:
1. Takes user input for two numbers
2. Supports +, -, *, /, //, %, **
3. Handles invalid input gracefully
4. Allows continuous calculation until 'quit'

## Run
```bash
python practice.py
python cli_calculator.py
```
