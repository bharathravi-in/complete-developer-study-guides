# Day 1: Python Syntax & Data Structures

## Why Python for an AI Engineer?
- Primary language for ML/AI ecosystem
- Rich libraries (NumPy, Pandas, LangChain, OpenAI SDK)
- Simple syntax = fast prototyping
- Massive community for AI/ML

---

## Python vs JavaScript (Quick Comparison for You)

| Feature | JavaScript | Python |
|---------|-----------|--------|
| Variables | `let x = 5` | `x = 5` |
| Constants | `const x = 5` | `X = 5` (convention) |
| Print | `console.log()` | `print()` |
| String format | `` `Hello ${name}` `` | `f"Hello {name}"` |
| Arrays/Lists | `[1, 2, 3]` | `[1, 2, 3]` |
| Objects/Dicts | `{key: value}` | `{key: value}` |
| Null | `null / undefined` | `None` |
| Boolean | `true / false` | `True / False` |
| Arrow func | `(x) => x + 1` | `lambda x: x + 1` |
| For loop | `for (let i of arr)` | `for i in arr:` |
| Import | `import x from 'y'` | `from y import x` |
| Async | `async/await` | `async/await` |
| Package mgr | `npm` | `pip` |
| **Indentation** | Optional (braces) | **Required (no braces!)** |

---

## 1. Variables & Types

```python
# Python uses dynamic typing (like JS)
name = "Bharath"          # str
age = 30                   # int
salary = 150000.50         # float
is_engineer = True         # bool
skills = None              # NoneType

# Type checking
print(type(name))    # <class 'str'>
print(type(age))     # <class 'int'>

# Type hints (like TypeScript!) - IMPORTANT for AI codebases
name: str = "Bharath"
age: int = 30
salary: float = 150000.50
is_active: bool = True
```

## 2. Strings

```python
# String operations
name = "Bharath"
print(name.upper())        # BHARATH
print(name.lower())        # bharath
print(name[0])             # B (indexing)
print(name[1:4])           # har (slicing)
print(len(name))           # 7

# f-strings (like template literals in JS)
role = "AI Engineer"
print(f"Hello, I'm {name}, a {role}")

# Multi-line strings (used A LOT in prompts)
prompt = """
You are a helpful assistant.
Answer the following question:
{question}
"""

# String methods you'll use constantly
text = "  Hello World  "
text.strip()               # "Hello World" (like .trim())
text.split(" ")            # ['', '', 'Hello', 'World', '', '']
"hello".replace("l", "r")  # "herro"
"hello world".title()      # "Hello World"
",".join(["a", "b", "c"])  # "a,b,c"
```

## 3. Numbers

```python
# Integer operations
x = 10
y = 3
print(x + y)    # 13
print(x - y)    # 7
print(x * y)    # 30
print(x / y)    # 3.3333... (float division)
print(x // y)   # 3 (integer division) ← NEW for you
print(x % y)    # 1 (modulo)
print(x ** y)   # 1000 (power) ← JS uses Math.pow()

# Useful built-ins
abs(-5)          # 5
round(3.7)       # 4
round(3.14159, 2)  # 3.14
min(1, 2, 3)     # 1
max(1, 2, 3)     # 3
```

## 4. Lists (Like Arrays in JS)

```python
# Creating lists
fruits = ["apple", "banana", "cherry"]
numbers = [1, 2, 3, 4, 5]
mixed = [1, "hello", True, 3.14]  # mixed types allowed

# Accessing
print(fruits[0])    # apple
print(fruits[-1])   # cherry (negative indexing!)
print(fruits[1:3])  # ['banana', 'cherry'] (slicing)

# Modifying
fruits.append("mango")        # Add to end (like .push())
fruits.insert(1, "grape")     # Insert at index
fruits.remove("banana")       # Remove by value
popped = fruits.pop()         # Remove & return last
fruits.extend(["kiwi", "fig"])  # Add multiple (like .concat())

# List operations
numbers = [3, 1, 4, 1, 5, 9]
numbers.sort()                # [1, 1, 3, 4, 5, 9] (in-place)
sorted_nums = sorted(numbers) # Returns new sorted list
numbers.reverse()             # Reverse in-place
len(numbers)                  # 6
5 in numbers                  # True (like .includes())
numbers.count(1)              # 2
numbers.index(4)              # Find index of value

# ⭐ List Comprehensions (PYTHON SUPERPOWER - use constantly!)
# JS: numbers.map(x => x * 2)
doubled = [x * 2 for x in numbers]

# JS: numbers.filter(x => x > 3)
big_nums = [x for x in numbers if x > 3]

# JS: numbers.filter(x => x > 2).map(x => x * 2)
result = [x * 2 for x in numbers if x > 2]

# Nested comprehension
matrix = [[1, 2], [3, 4], [5, 6]]
flat = [num for row in matrix for num in row]  # [1, 2, 3, 4, 5, 6]
```

## 5. Tuples (Immutable Lists)

```python
# Tuples = immutable lists (can't change after creation)
point = (10, 20)
rgb = (255, 128, 0)

# Accessing (same as lists)
print(point[0])   # 10

# Unpacking (very Pythonic!)
x, y = point      # x=10, y=20

# When to use tuples?
# - Return multiple values from functions
# - Dictionary keys (lists can't be keys)
# - When data shouldn't change

def get_user():
    return "Bharath", 30, "AI Engineer"  # Returns tuple

name, age, role = get_user()  # Unpack
```

## 6. Dictionaries (Like Objects in JS)

```python
# Creating dicts
user = {
    "name": "Bharath",
    "age": 30,
    "role": "AI Engineer",
    "skills": ["Python", "React", "Angular"]
}

# Accessing
print(user["name"])          # Bharath (raises KeyError if missing)
print(user.get("name"))      # Bharath (returns None if missing)
print(user.get("salary", 0)) # 0 (default value)

# Modifying
user["salary"] = 150000      # Add/update
del user["age"]              # Delete key
user.pop("role")             # Remove & return value

# Dict methods
user.keys()                  # dict_keys(['name', 'skills', 'salary'])
user.values()                # dict_values([...])
user.items()                 # dict_items([('name', 'Bharath'), ...])

# Iterating
for key, value in user.items():
    print(f"{key}: {value}")

# ⭐ Dictionary Comprehension
# Create dict from two lists
keys = ["name", "age", "role"]
values = ["Bharath", 30, "Engineer"]
user_dict = {k: v for k, v in zip(keys, values)}

# Transform values
prices = {"apple": 1.0, "banana": 0.5, "cherry": 2.0}
doubled_prices = {k: v * 2 for k, v in prices.items()}

# Nested dicts (very common in API responses)
response = {
    "status": "success",
    "data": {
        "user": {
            "name": "Bharath",
            "embeddings": [0.1, 0.2, 0.3]
        }
    }
}
# Access nested
name = response["data"]["user"]["name"]
```

## 7. Sets (Unique Collections)

```python
# Sets = unordered, unique elements
skills = {"Python", "React", "Angular", "Python"}  # Python appears once
print(skills)  # {'Python', 'React', 'Angular'}

# Set operations (useful for data processing)
frontend = {"React", "Angular", "Vue"}
backend = {"Python", "Flask", "Node"}
fullstack = frontend | backend      # Union
common = frontend & backend         # Intersection
only_front = frontend - backend     # Difference

# Checking membership (O(1) - very fast!)
"React" in skills  # True
```

## 8. Control Flow

```python
# If/elif/else (no braces, use indentation!)
score = 85
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "F"

# Ternary (like JS ternary)
# JS: const status = age >= 18 ? "adult" : "minor"
status = "adult" if age >= 18 else "minor"

# For loops
for fruit in fruits:
    print(fruit)

# With index (like forEach with index)
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")

# Range
for i in range(5):       # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 10, 2):  # 2, 4, 6, 8
    print(i)

# While loop
count = 0
while count < 5:
    print(count)
    count += 1

# Loop control
for i in range(10):
    if i == 3:
        continue    # Skip this iteration
    if i == 7:
        break       # Exit loop
    print(i)
```

## 9. Functions

```python
# Basic function
def greet(name: str) -> str:
    """Greet a person by name."""  # Docstring
    return f"Hello, {name}!"

# Default parameters
def create_user(name: str, role: str = "Engineer") -> dict:
    return {"name": name, "role": role}

# *args and **kwargs (very common in Python!)
def log(*args):
    """Accept any number of positional arguments."""
    for arg in args:
        print(arg)

def create_config(**kwargs):
    """Accept any number of keyword arguments."""
    return kwargs

config = create_config(host="localhost", port=5000, debug=True)
# {'host': 'localhost', 'port': 5000, 'debug': True}

# Lambda (like arrow functions)
double = lambda x: x * 2
add = lambda x, y: x + y

# Higher-order functions
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))      # [2, 4, 6, 8, 10]
evens = list(filter(lambda x: x % 2 == 0, numbers)) # [2, 4]

# But prefer list comprehensions (more Pythonic):
doubled = [x * 2 for x in numbers]
evens = [x for x in numbers if x % 2 == 0]
```

## 10. Exception Handling

```python
# Try/except (like try/catch in JS)
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
except Exception as e:
    print(f"Error: {e}")
finally:
    print("Always runs")

# Raising exceptions (like throw in JS)
def validate_age(age: int) -> None:
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age seems unrealistic")

# Custom exceptions
class APIError(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
```

---

## Exercises

### Exercise 1: Data Processing
```python
# Given this data (like an API response), extract and transform:
users = [
    {"name": "Alice", "age": 28, "skills": ["Python", "Flask"]},
    {"name": "Bob", "age": 35, "skills": ["React", "Node"]},
    {"name": "Charlie", "age": 42, "skills": ["Python", "React", "Docker"]},
]

# TODO:
# 1. Get names of users older than 30
# 2. Get all unique skills across all users
# 3. Create a dict mapping name -> number of skills
# 4. Find the user with the most skills
```

### Exercise 2: Text Processing (Relevant to AI)
```python
# Process this text (like preparing text for embeddings)
text = """
Machine learning is a subset of artificial intelligence.
It uses algorithms to learn from data.
Deep learning is a subset of machine learning.
"""

# TODO:
# 1. Split into sentences
# 2. Count word frequency
# 3. Find the longest sentence
# 4. Remove duplicate words across all sentences
```

### Exercise 3: Build a Simple Config Manager
```python
# Build a function that:
# 1. Reads environment-like config from a dict
# 2. Validates required keys exist
# 3. Returns config with defaults applied
# Think of it like managing .env files

# TODO: Implement
def load_config(config: dict, required_keys: list, defaults: dict) -> dict:
    pass
```

---

## Key Takeaways for Day 1
1. Python uses **indentation** instead of braces
2. **List comprehensions** are your new `.map()` and `.filter()`
3. **Dictionaries** are like JS objects but with string keys
4. **f-strings** are like template literals
5. **Type hints** make Python feel like TypeScript
6. **Tuples** are immutable lists (use for fixed data)
7. ***args** and ****kwargs** are Python's spread operator equivalent
