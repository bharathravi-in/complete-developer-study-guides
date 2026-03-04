#!/usr/bin/env python3
"""Day 7 - Modules & Packages Practice"""

import sys
import os

print("=" * 50)
print("MODULES & PACKAGES")
print("=" * 50)

# ============================================
# 1. IMPORT STATEMENTS
# ============================================
print("\n--- 1. IMPORT STATEMENTS ---")

# Standard import
import math
print(f"math.pi: {math.pi}")
print(f"math.sqrt(16): {math.sqrt(16)}")

# From import
from datetime import datetime, timedelta
now = datetime.now()
print(f"Current time: {now}")
print(f"Tomorrow: {now + timedelta(days=1)}")

# Import with alias
import json as j
data = j.dumps({"key": "value"})
print(f"JSON: {data}")

# Import specific items with alias
from collections import Counter as C
counts = C([1, 1, 2, 3, 3, 3])
print(f"Counter: {counts}")


# ============================================
# 2. MODULE INFORMATION
# ============================================
print("\n--- 2. MODULE INFORMATION ---")

print(f"Module name: {__name__}")
print(f"Module file: {__file__}")
print(f"Module doc: {__doc__[:50]}...")

# Module search path
print(f"\nPython path ({len(sys.path)} entries):")
for i, path in enumerate(sys.path[:5]):
    print(f"  {i}. {path}")
print("  ...")


# ============================================
# 3. __name__ == "__main__"
# ============================================
print("\n--- 3. __name__ == '__main__' ---")

def main():
    """Main function that runs when script is executed directly"""
    print("  This runs only when executed directly, not when imported")


# This pattern allows module to be both importable and executable
if __name__ == "__main__":
    # This block runs only when script is run directly
    print(f"  __name__ is: {__name__}")
    main()


# ============================================
# 4. IMPORTING YOUR OWN MODULES
# ============================================
print("\n--- 4. CUSTOM MODULES ---")

# Create a simple module dynamically
module_code = '''
"""A simple math utilities module"""

PI = 3.14159

def add(a, b):
    """Add two numbers"""
    return a + b

def multiply(a, b):
    """Multiply two numbers"""
    return a * b

class Calculator:
    """Simple calculator class"""
    def __init__(self, initial=0):
        self.value = initial
    
    def add(self, x):
        self.value += x
        return self
    
    def result(self):
        return self.value
'''

# Write module to temp file and import it
import tempfile
import importlib.util

with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    f.write(module_code)
    temp_module_path = f.name

# Load module dynamically
spec = importlib.util.spec_from_file_location("mymath", temp_module_path)
mymath = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mymath)

print(f"  mymath.PI: {mymath.PI}")
print(f"  mymath.add(2, 3): {mymath.add(2, 3)}")
print(f"  Calculator: {mymath.Calculator(10).add(5).add(3).result()}")

# Cleanup
os.unlink(temp_module_path)


# ============================================
# 5. EXPLORING MODULES
# ============================================
print("\n--- 5. EXPLORING MODULES ---")

# List module contents
print("Math module contents (first 10):")
math_contents = [x for x in dir(math) if not x.startswith('_')]
for item in math_contents[:10]:
    obj = getattr(math, item)
    obj_type = type(obj).__name__
    print(f"  {item:15} ({obj_type})")

# Get help
print(f"\nmath.factorial docstring: {math.factorial.__doc__}")


# ============================================
# 6. PACKAGE STRUCTURE
# ============================================
print("\n--- 6. PACKAGE STRUCTURE ---")

package_structure = """
mypackage/
├── __init__.py          # Package initialization
├── core/
│   ├── __init__.py
│   ├── utils.py
│   └── config.py
├── api/
│   ├── __init__.py
│   └── handlers.py
└── tests/
    ├── __init__.py
    └── test_core.py
"""

print(package_structure)

# __init__.py example
init_example = '''
# mypackage/__init__.py
"""MyPackage - A sample package"""

__version__ = "1.0.0"
__author__ = "Developer"

# Control what's exported with 'from package import *'
__all__ = ['core', 'api', 'VERSION']

VERSION = __version__

# Configure package-level imports
from .core import utils
from .core.config import Config
'''

print("Example __init__.py:")
print(init_example)


# ============================================
# 7. STANDARD LIBRARY HIGHLIGHTS
# ============================================
print("\n--- 7. STANDARD LIBRARY HIGHLIGHTS ---")

useful_modules = {
    "collections": "Counter, defaultdict, deque, namedtuple",
    "itertools": "product, permutations, combinations, chain",
    "functools": "lru_cache, partial, reduce, wraps",
    "pathlib": "Modern path handling (Path)",
    "dataclasses": "Data class decorator",
    "typing": "Type hints support",
    "json": "JSON encoding/decoding",
    "re": "Regular expressions",
    "datetime": "Date and time handling",
    "logging": "Logging framework",
    "unittest": "Unit testing framework",
    "argparse": "Command-line argument parsing",
    "os": "Operating system interface",
    "sys": "System-specific parameters",
    "subprocess": "Process management",
    "threading": "Thread-based parallelism",
    "asyncio": "Async I/O",
}

for module, description in useful_modules.items():
    print(f"  {module:15} - {description}")


# ============================================
# 8. PIP AND PACKAGE MANAGEMENT
# ============================================
print("\n--- 8. PIP COMMANDS ---")

pip_commands = """
Common pip commands:
  pip install package         # Install package
  pip install package==1.0    # Install specific version
  pip install -r requirements.txt  # Install from file
  pip uninstall package       # Remove package
  pip list                    # List installed packages
  pip freeze                  # List with versions
  pip show package            # Package details
  pip search keyword          # Search PyPI
  
Modern alternatives:
  uv pip install package      # Faster pip alternative
  poetry add package          # Poetry package manager
  pipenv install package      # Pipenv environment
"""

print(pip_commands)


# ============================================
# 9. RELATIVE VS ABSOLUTE IMPORTS
# ============================================
print("\n--- 9. RELATIVE VS ABSOLUTE IMPORTS ---")

imports_example = """
# Absolute imports (preferred)
from mypackage.core import utils
from mypackage.core.config import Config

# Relative imports (within package)
from . import utils          # Same directory
from .. import other_module  # Parent directory
from ..api import handlers   # Sibling package
"""

print(imports_example)


print("\n✅ Day 7 completed!")
print("\n📌 Now build the CLI TODO App in cli_todo_app/ directory!")
