#!/usr/bin/env python3
"""Day 3 - Control Flow Practice"""

print("=" * 50)
print("CONTROL FLOW")
print("=" * 50)

# ============================================
# 1. IF-ELSE
# ============================================
print("\n--- 1. IF-ELSE ---")

age = 25

if age < 13:
    print("Child")
elif age < 20:
    print("Teenager")
elif age < 60:
    print("Adult")
else:
    print("Senior")

# Ternary operator
status = "adult" if age >= 18 else "minor"
print(f"Status: {status}")

# ============================================
# 2. TRUTHY AND FALSY
# ============================================
print("\n--- 2. TRUTHY AND FALSY ---")

falsy_values = [False, None, 0, 0.0, '', [], {}, set()]

print("Falsy values:")
for val in falsy_values:
    print(f"  bool({repr(val):10}) = {bool(val)}")

print("\nTruthy examples:")
truthy_values = [True, 1, -1, "hello", [0], {"a": 1}]
for val in truthy_values:
    print(f"  bool({repr(val):15}) = {bool(val)}")

# ============================================
# 3. NESTED CONDITIONS
# ============================================
print("\n--- 3. NESTED CONDITIONS ---")

user = {"name": "Alice", "role": "admin", "active": True}

if user.get("active"):
    if user.get("role") == "admin":
        print(f"{user['name']} has full access")
    elif user.get("role") == "editor":
        print(f"{user['name']} can edit content")
    else:
        print(f"{user['name']} has read-only access")
else:
    print("User account is inactive")

# Better: Flat is better than nested
def get_access_level(user):
    if not user.get("active"):
        return "Account inactive"
    
    role = user.get("role", "viewer")
    access_map = {
        "admin": "full access",
        "editor": "edit access",
        "viewer": "read-only access"
    }
    return access_map.get(role, "no access")

print(f"Access: {get_access_level(user)}")

# ============================================
# 4. MATCH-CASE (Python 3.10+)
# ============================================
print("\n--- 4. MATCH-CASE (Python 3.10+) ---")

def handle_command(command):
    match command.split():
        case ["quit" | "exit"]:
            return "Goodbye!"
        case ["hello", name]:
            return f"Hello, {name}!"
        case ["add", *numbers]:
            return f"Sum: {sum(map(int, numbers))}"
        case ["status", ("active" | "inactive") as status]:
            return f"Status is {status}"
        case _:
            return "Unknown command"

commands = ["quit", "hello World", "add 1 2 3 4", "status active", "foo"]
for cmd in commands:
    print(f"  '{cmd}' -> {handle_command(cmd)}")

# Pattern matching with types
def describe_point(point):
    match point:
        case (0, 0):
            return "Origin"
        case (x, 0):
            return f"On X-axis at {x}"
        case (0, y):
            return f"On Y-axis at {y}"
        case (x, y):
            return f"Point at ({x}, {y})"
        case _:
            return "Not a point"

points = [(0, 0), (5, 0), (0, 3), (4, 5)]
for p in points:
    print(f"  {p} -> {describe_point(p)}")

# ============================================
# 5. FOR LOOPS
# ============================================
print("\n--- 5. FOR LOOPS ---")

# Basic iteration
print("Basic loop:", end=" ")
for i in range(5):
    print(i, end=" ")
print()

# Enumerate
fruits = ["apple", "banana", "cherry"]
print("\nWith enumerate:")
for i, fruit in enumerate(fruits, start=1):
    print(f"  {i}. {fruit}")

# Zip
names = ["Alice", "Bob", "Charlie"]
scores = [85, 92, 78]
print("\nWith zip:")
for name, score in zip(names, scores):
    print(f"  {name}: {score}")

# Dict iteration
person = {"name": "Alice", "age": 30, "city": "NYC"}
print("\nDict iteration:")
for key, value in person.items():
    print(f"  {key}: {value}")

# ============================================
# 6. WHILE LOOPS
# ============================================
print("\n--- 6. WHILE LOOPS ---")

# Basic while
count = 0
while count < 5:
    print(f"Count: {count}")
    count += 1

# While with else
print("\nWhile with else:")
n = 5
while n > 0:
    print(n, end=" ")
    n -= 1
else:
    print("-> Loop completed normally!")

# ============================================
# 7. BREAK, CONTINUE, PASS
# ============================================
print("\n--- 7. BREAK, CONTINUE, PASS ---")

# Break
print("Break example (find first even):")
for i in [1, 3, 5, 4, 7, 8]:
    if i % 2 == 0:
        print(f"  Found even: {i}")
        break
else:
    print("  No even found")

# Continue
print("\nContinue example (skip odds):")
for i in range(10):
    if i % 2 != 0:
        continue
    print(i, end=" ")
print()

# Pass (placeholder)
class FutureImplementation:
    pass  # Placeholder for future code

def not_implemented_yet():
    pass

# ============================================
# 8. LOOP ELSE CLAUSE
# ============================================
print("\n--- 8. LOOP ELSE CLAUSE ---")

def find_prime_factor(n):
    """Find first prime factor using for-else"""
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            print(f"  {n} has factor: {i}")
            break
    else:
        print(f"  {n} is prime!")

for num in [17, 25, 37, 100]:
    find_prime_factor(num)

# ============================================
# 9. COMPREHENSIONS IN CONTROL FLOW
# ============================================
print("\n--- 9. COMPREHENSIONS ---")

# List comprehension with condition
evens = [x for x in range(20) if x % 2 == 0]
print(f"Evens: {evens}")

# With if-else
labels = ["even" if x % 2 == 0 else "odd" for x in range(5)]
print(f"Labels: {labels}")

# Nested comprehension
matrix = [[i*j for j in range(1, 4)] for i in range(1, 4)]
print(f"Matrix: {matrix}")

print("\n✅ Day 3 completed!")
