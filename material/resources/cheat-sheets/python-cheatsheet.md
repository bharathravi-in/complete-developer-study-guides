# Python Cheat Sheet — For JS/TS Developers

## Variables & Types
```python
# JS: const, let, var → Python: just assign
name = "Bharath"              # str
age = 28                      # int
score = 9.5                   # float
active = True                 # bool (capital T/F)
items = [1, 2, 3]             # list (like Array)
info = {"key": "value"}       # dict (like Object)
unique = {1, 2, 3}            # set
coords = (10, 20)             # tuple (immutable list)
nothing = None                # None (like null)
```

## Strings
```python
f"Hello {name}"               # f-string (like template literal)
"hello".upper()               # "HELLO"
"a,b,c".split(",")            # ["a", "b", "c"]
",".join(["a", "b"])          # "a,b"
"hello"[1:3]                  # "el" (slice)
len("hello")                  # 5
"lo" in "hello"               # True
```

## Lists
```python
nums = [1, 2, 3, 4, 5]
nums.append(6)                # push
nums.pop()                    # pop
nums[0]                       # first
nums[-1]                      # last
nums[1:3]                     # [2, 3] slice
len(nums)                     # length
sorted(nums, reverse=True)    # sort copy
nums.sort()                   # sort in-place
[x*2 for x in nums]           # map
[x for x in nums if x > 2]   # filter
```

## Dicts
```python
d = {"name": "Bharath", "age": 28}
d["name"]                     # "Bharath"
d.get("email", "N/A")         # safe get with default
d.keys()                      # dict_keys
d.values()                    # dict_values
d.items()                     # key-value pairs
{**d, "role": "ai"}           # spread/merge
```

## Control Flow
```python
# if/elif/else (no braces, use indentation)
if x > 0:
    print("positive")
elif x == 0:
    print("zero")
else:
    print("negative")

# for loop
for item in items:
    print(item)

for i, item in enumerate(items):  # index + item
    print(i, item)

for key, val in d.items():    # iterate dict
    print(key, val)

# while
while condition:
    do_something()

# ternary
result = "yes" if x > 0 else "no"
```

## Functions
```python
def greet(name: str, greeting: str = "Hello") -> str:
    return f"{greeting}, {name}"

# Lambda (arrow function)
double = lambda x: x * 2

# *args, **kwargs (rest params)
def log(*args, **kwargs):
    print(args, kwargs)
```

## Classes
```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    role: str = "user"

user = User("Bharath", "b@test.com")

# Regular class
class Service:
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def call(self) -> str:
        return "result"
```

## Error Handling
```python
try:
    result = risky_operation()
except ValueError as e:
    print(f"Value error: {e}")
except Exception as e:
    print(f"Error: {e}")
finally:
    cleanup()

# Raise (throw)
raise ValueError("Invalid input")
```

## File I/O
```python
# Read
with open("file.txt") as f:
    content = f.read()

# Write
with open("out.txt", "w") as f:
    f.write("hello")

# JSON
import json
data = json.loads(json_string)
json_string = json.dumps(data, indent=2)
```

## Async
```python
import asyncio

async def fetch(url: str) -> str:
    # async operation
    return "data"

# Run multiple
results = await asyncio.gather(fetch(url1), fetch(url2))

# Run async function
asyncio.run(main())
```

## Common Imports
```python
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime
import json, os, logging
from collections import defaultdict, Counter
```

## One-Liners
```python
# Swap
a, b = b, a

# Flatten
flat = [x for sub in nested for x in sub]

# Count items
from collections import Counter
counts = Counter(items)

# Unique (preserve order)
unique = list(dict.fromkeys(items))

# Check any/all
any(x > 0 for x in nums)     # True if any positive
all(x > 0 for x in nums)     # True if all positive
```
