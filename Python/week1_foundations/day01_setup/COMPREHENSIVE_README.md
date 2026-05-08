# Day 1 - Python Setup & Basics

## Table of Contents
- [Overview](#overview)
- [Python Installation](#python-installation)
- [Virtual Environments](#virtual-environments)
- [Python Basics](#python-basics)
- [Best Practices](#best-practices)
- [Interview Preparation](#interview-preparation)
- [Practice Exercises](#practice-exercises)

---

## Overview

Python is a high-level, interpreted, dynamically-typed programming language known for its readability and versatility. This day covers essential setup and foundational concepts needed to start your Python journey.

---

## Python Installation

### Check Current Installation

```bash
# Check if Python is installed
python --version  # or python3 --version

# Check pip (package manager)
pip --version  # or pip3 --version

# Find Python location
which python3  # Linux/Mac
where python   # Windows
```

### Installing Python

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS:**
```bash
# Using Homebrew
brew install python3

# Or download from python.org
```

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- Check "Add Python to PATH" during installation
- Verify with `python --version` in CMD

### Multiple Python Versions

```bash
# Using pyenv (recommended for managing multiple versions)
curl https://pyenv.run | bash

# Install specific Python version
pyenv install 3.11.5
pyenv install 3.12.0

# Set global version
pyenv global 3.11.5

# Set local version for a project
pyenv local 3.12.0
```

---

## Virtual Environments

Virtual environments isolate project dependencies, preventing conflicts between different projects.

### Why Use Virtual Environments?

 **Isolation**: Each project has its own dependencies
- **Reproducibility**: Easy to recreate exact environment
- **No Permission Issues**: Install packages without sudo
- **Multiple Python Versions**: Different projects can use different Python versions

### venv (Built-in)

```bash
# Create virtual environment
python3 -m venv myenv

# Activate
# Linux/macOS:
source myenv/bin/activate

# Windows:
myenv\Scripts\activate

# Deactivate
deactivate

# Delete virtual environment
rm -rf myenv  # Linux/macOS
rmdir /s myenv  # Windows
```

### virtualenv (Third-party)

```bash
# Install
pip install virtualenv

# Create environment
virtualenv myenv

# Create with specific Python version
virtualenv --python=/usr/bin/python3.11 myenv
```

### pipenv (Modern Approach)

```bash
# Install pipenv
pip install pipenv

# Create environment and install packages
pipenv install requests numpy

# Activate environment
pipenv shell

# Run script without activating
pipenv run python script.py

# Install from Pipfile
pipenv install

# Install dev dependencies
pipenv install --dev pytest
```

### conda (Anaconda/Miniconda)

```bash
# Create environment
conda create --name myenv python=3.11

# Activate
conda activate myenv

# Deactivate
conda deactivate

# List environments
conda env list

# Remove environment
conda remove --name myenv --all
```

### poetry (Dependency Management)

```bash
# Install poetry
curl -sSL https://install.python-poetry.org | python3 -

# Initialize new project
poetry new my-project

# Install dependencies
poetry install

# Add package
poetry add requests

# Run script
poetry run python script.py
```

---

## Python Basics

### Running Python

```bash
# 1. Interactive REPL (Read-Eval-Print Loop)
python3
>>> print("Hello, World!")
>>> 2 + 2
>>> exit()

# 2. Run a script
python3 script.py

# 3. Run as module
python3 -m module_name

# 4. One-liner
python3 -c "print('Hello')"

# 5. Interactive mode after script
python3 -i script.py
```

### Variables and Naming Conventions

```python
# Variables (no declaration needed, dynamically typed)
name = "Alice"
age = 30
is_student = False
score = 95.5

# Multiple assignment
x, y, z = 1, 2, 3
a = b = c = 0

# Swap variables
a, b = b, a

# Naming Conventions (PEP 8)
# ✅ GOOD
user_name = "Alice"           # snake_case for variables
MAX_SIZE = 100                # UPPER_SNAKE_CASE for constants
UserProfile = None            # PascalCase for classes
_internal_var = 42            # _ prefix for internal use
__private_var = 10            # __ prefix for name mangling

# ❌ BAD
userName = "Bob"              # camelCase (JS style)
MAXSIZE = 100                 # Missing underscore
user-name = "Charlie"         # Hyphens not allowed
2nd_place = "Silver"          # Can't start with digit
```

### Python Keywords

Keywords are reserved words that cannot be used as variable names.

```python
import keyword

# List all keywords
print(keyword.kwlist)
# ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
#  'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
#  'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
#  'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
#  'try', 'while', 'with', 'yield']

# Check if a string is a keyword
print(keyword.iskeyword('for'))   # True
print(keyword.iskeyword('name'))  # False
```

### Basic Input/Output

```python
# Output
print("Hello, World!")
print("Name:", name, "Age:", age)  # Multiple values
print(f"Name: {name}, Age: {age}")  # f-string (Python 3.6+)
print("Line 1\nLine 2")  # Newline
print("One", "Two", "Three", sep=" | ")  # Custom separator

# Input (always returns string)
name = input("Enter your name: ")
age = int(input("Enter your age: "))  # Convert to int
price = float(input("Enter price: "))  # Convert to float
```

### Comments

```python
# Single-line comment

"""
Multi-line comment or docstring
Can span multiple lines
"""

def function():
    """
    Docstring for function documentation
    Shows up in help() and documentation tools
    """
    pass
```

### Type Checking

```python
# Check type
x = 42
print(type(x))  # <class 'int'>

# Check if instance of type
print(isinstance(x, int))  # True
print(isinstance(x, (int, float)))  # True (multiple types)

# Convert types
x = "42"
y = int(x)      # String to int
z = float(x)    # String to float
s = str(42)     # Int to string
```

---

## Best Practices

### 1. PEP 8 Style Guide

```python
# ✅ GOOD: Consistent formatting
def calculate_total(items, tax_rate=0.1):
    """Calculate total price including tax."""
    subtotal = sum(item['price'] for item in items)
    tax = subtotal * tax_rate
    return subtotal + tax

# ❌ BAD: Inconsistent formatting
def calculate_total(items,tax_rate=0.1):
    subtotal=sum(item['price']for item in items)
    return subtotal+subtotal*tax_rate

# Imports
# ✅ GOOD: Organized imports
import os
import sys

import numpy as np
import pandas as pd

from mypackage import mymodule

# ❌ BAD: Random order
from mypackage import mymodule
import sys
import numpy as np
import os
```

### 2. Virtual Environment Workflow

```bash
# Standard project workflow
mkdir my_project
cd my_project

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install requests flask pytest

# Save dependencies
pip freeze > requirements.txt

# Install from requirements.txt (on another machine)
pip install -r requirements.txt
```

### 3. requirements.txt Best Practices

```txt
# Pinned versions (reproducible)
requests==2.31.0
flask==3.0.0

# Minimum version
numpy>=1.24.0

# Version range
pandas>=1.5.0,<2.0.0

# Development dependencies
pytest>=7.0.0  # dev

# Comments
# Data processing
pandas==2.0.0
numpy==1.24.0

# Web framework
flask==3.0.0
```

### 4. Project Structure

```
my_project/
├── venv/                 # Virtual environment (don't commit)
├── src/                  # Source code
│   ├── __init__.py
│   ├── main.py
│   └── utils.py
├── tests/                # Tests
│   ├── __init__.py
│   └── test_main.py
├── docs/                 # Documentation
├── .gitignore           # Git ignore file
├── README.md            # Project description
├── requirements.txt     # Dependencies
└── setup.py            # Package configuration
```

### 5. .gitignore for Python

```gitignore
# Virtual environments
venv/
env/
ENV/
.venv/

# Python cache
__pycache__/
*.py[cod]
*$py.class
*.so

# Distribution
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment variables
.env

# OS
.DS_Store
Thumbs.db
```

---

## Interview Preparation

### Q1: What is Python? What are its key features?

**Answer:**
Python is a high-level, interpreted, dynamically-typed programming language.

**Key Features:**
- **Easy to learn**: Simple, readable syntax
- **Interpreted**: No compilation needed
- **Dynamically typed**: Type checking at runtime
- **Object-oriented**: Supports OOP paradigms
- **Large standard library**: "Batteries included"
- **Cross-platform**: Runs on Windows, Linux, macOS
- **Versatile**: Web, data science, AI, automation, etc.

---

### Q2: What is the difference between Python 2 and Python 3?

**Answer:**
Python 2 reached end-of-life on January 1, 2020. Key differences:

| Feature | Python 2 | Python 3 |
|---------|----------|----------|
| Print | `print "Hello"` | `print("Hello")` |
| Division | `5/2 = 2` (int) | `5/2 = 2.5` (float) |
| Unicode | ASCII default | Unicode default |
| range() | Returns list | Returns iterator |
| input() | eval(input()) | Safe string input |

**Always use Python 3** for new projects.

---

### Q3: What is PEP 8?

**Answer:**
PEP 8 is the Python Enhancement Proposal that defines the style guide for Python code.

**Key Rules:**
- Use 4 spaces for indentation (not tabs)
- Max line length: 79 characters
- Use `snake_case` for variables and functions
- Use `PascalCase` for classes
- Two blank lines between top-level functions/classes
- One blank line between methods

```python
# Check code against PEP 8
pip install pycodestyle
pycodestyle myfile.py

# Auto-format code
pip install black
black myfile.py
```

---

### Q4: What is a virtual environment and why is it important?

**Answer:**
A virtual environment is an isolated Python environment with its own:
- Python interpreter
- Installed packages
- Scripts

**Why Important:**
```python
# Without virtual environment
# Project A needs requests 2.25.0
# Project B needs requests 2.31.0
# ❌ CONFLICT - only one version can be installed globally

# With virtual environments
# ✅ Project A (venv_a): requests 2.25.0
# ✅ Project B (venv_b): requests 2.31.0
```

Benefits:
1. Dependency isolation
2. No permission issues
3. Reproducible environments
4. Clean system Python
5. Easy cleanup (delete folder)

---

### Q5: What are Python's naming conventions?

**Answer:**
```python
# Variables and functions: snake_case
user_name = "Alice"
def calculate_total():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_CONNECTIONS = 100
API_KEY = "abc123"

# Classes: PascalCase
class UserProfile:
    pass

# Modules: lowercase, underscores if needed
import mymodule
import data_processor

# Private: _single_leading_underscore
_internal_function()
_private_variable = 42

# Name mangling: __double_leading_underscore
class MyClass:
    def __init__(self):
        self.__private = 10  # Becomes _MyClass__private
```

---

### Q6: Coding Problem - CLI Calculator

**Question:** Build a command-line calculator that:
1. Takes two numbers and an operator as input
2. Supports +, -, *, /, //, %, **
3. Handles division by zero
4. Allows continuous calculations or quit

**Solution:**
```python
def calculate(num1, operator, num2):
    """Perform calculation based on operator"""
    operations = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b if b != 0 else "Error: Division by zero",
        '//': lambda a, b: a // b if b != 0 else "Error: Division by zero",
        '%': lambda a, b: a % b if b != 0 else "Error: Division by zero",
        '**': lambda a, b: a ** b
    }
    
    if operator in operations:
        return operations[operator](num1, num2)
    else:
        return "Error: Invalid operator"

def main():
    """Main calculator loop"""
    print("=== CLI Calculator ===")
    print("Operators: +, -, *, /, //, %, **")
    print("Type 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("Enter calculation (e.g., 5 + 3) or 'quit': ")
            
            if user_input.lower() == 'quit':
                print("Goodbye!")
                break
            
            # Parse input
            parts = user_input.split()
            if len(parts) != 3:
                print("Error: Use format 'number operator number'")
                continue
            
            num1 = float(parts[0])
            operator = parts[1]
            num2 = float(parts[2])
            
            result = calculate(num1, operator, num2)
            print(f"Result: {result}\n")
            
        except ValueError:
            print("Error: Invalid number format\n")
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
```

---

### Q7: What is the difference between `is` and `==`?

**Answer:**
- `==` checks **value equality** (content)
- `is` checks **identity** (same object in memory)

```python
# Small integers are cached (interned)
a = 256
b = 256
print(a == b)  # True (same value)
print(a is b)  # True (same object due to caching)

# Large integers are not cached
x = 1000
y = 1000
print(x == y)  # True (same value)
print(x is y)  # False (different objects)

# Lists
list1 = [1, 2, 3]
list2 = [1, 2, 3]
list3 = list1

print(list1 == list2)  # True (same content)
print(list1 is list2)  # False (different objects)
print(list1 is list3)  # True (same object)

# Use 'is' for None, True, False (singletons)
if value is None:  # ✅ Correct
    pass
if value == None:  # ❌ Works but not idiomatic
    pass
```

---

### Q8: Explain Python's memory management

**Answer:**
Python uses:
1. **Reference Counting**: Each object has a reference count
2. **Garbage Collection**: Detects and cleans circular references
3. **Memory Pools**: Optimize small object allocation

```python
import sys

# Reference counting
a = [1, 2, 3]
print(sys.getrefcount(a))  # 2 (a + getrefcount argument)

b = a  # Increase ref count
print(sys.getrefcount(a))  # 3

del b  # Decrease ref count
print(sys.getrefcount(a))  # 2

# Circular reference (garbage collector needed)
class Node:
    def __init__(self):
        self.ref = None

node1 = Node()
node2 = Node()
node1.ref = node2
node2.ref = node1  # Circular reference

del node1, node2  # Ref count doesn't reach 0
# Garbage collector will clean this up
```

---

## Practice Exercises

### Exercise 1: Environment Setup Checklist
Complete these tasks:
1. Install Python 3.10+
2. Create a virtual environment
3. Install `requests`, `numpy`, `pytest`
4. Generate `requirements.txt`
5. Create a `.gitignore` file

### Exercise 2: Enhanced CLI Calculator
Extend the calculator to:
- Support parentheses: `(5 + 3) * 2`
- Store calculation history
- Support variables: `x = 10; y = 5; x + y`

<details>
<summary>Solution Hint</summary>

```python
# Use eval() carefully or implement a parser
def safe_eval(expression):
    """Safely evaluate mathematical expressions"""
    allowed_chars = set("0123456789+-*/().% ")
    if not all(c in allowed_chars for c in expression):
        return "Error: Invalid characters"
    
    try:
        result = eval(expression)
        return result
    except Exception as e:
        return f"Error: {e}"

# History
history = []

while True:
    expr = input(">>> ")
    if expr == "quit":
        break
    if expr == "history":
        for h in history:
            print(h)
        continue
    
    result = safe_eval(expr)
    print(result)
    history.append(f"{expr} = {result}")
```
</details>

---

## Practice Task

Build a comprehensive CLI Calculator that:
1. Takes user input for two numbers
2. Supports +, -, *, /, //, %, **
3. Handles invalid input gracefully
4. Allows continuous calculation until 'quit'
5. **Bonus**: Add memory functions (M+, M-, MR, MC)
6. **Bonus**: Save calculation history to file

## Run
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

# Run practice scripts
python practice.py
python cli_calculator.py

# Deactivate when done
deactivate
```

## Additional Resources

- [Official Python Tutorial](https://docs.python.org/3/tutorial/)
- [PEP 8 Style Guide](https://pep8.org/)
- [Real Python - Virtual Environments](https://realpython.com/python-virtual-environments-a-primer/)
- [Python Package Index (PyPI)](https://pypi.org/)

---

## Key Takeaways

1. ✅ Always use virtual environments for projects
2. ✅ Follow PEP 8 naming conventions
3. ✅ Use `python3` and `pip3` to avoid version conflicts
4. ✅ Keep `requirements.txt` updated
5. ✅ Use `is` for None/True/False, `==` for value comparisons
6. ✅ Python is dynamically typed but supports type hints
7. ✅ REPL is great for experimentation
8. ✅ Never commit virtual environments to version control
