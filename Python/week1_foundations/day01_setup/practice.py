#!/usr/bin/env python3
"""Day 1 - Python Basics Practice"""

# 1. Print Python version
import sys
print(f"Python version: {sys.version}")

# 2. Display all keywords
import keyword
print(f"\nPython Keywords ({len(keyword.kwlist)} total):")
print(keyword.kwlist)

# 3. Variables & Naming Conventions
# snake_case for variables
user_name = "Bharath"
user_age = 30

# UPPER_SNAKE_CASE for constants
MAX_RETRIES = 3
API_BASE_URL = "https://api.example.com"

# Variable inspection
print(f"\n--- Variable Info ---")
print(f"Variable: user_name = {user_name}")
print(f"Type: {type(user_name)}")
print(f"ID (memory address): {id(user_name)}")

# 4. Multiple assignment
a, b, c = 1, 2, 3
x = y = z = 0  # All point to same object

print(f"\na, b, c = {a}, {b}, {c}")
print(f"x = y = z = {x}")
print(f"Are x, y, z same object? {x is y is z}")

# 5. Swapping variables (Pythonic way)
a, b = b, a
print(f"\nAfter swap: a = {a}, b = {b}")

# 6. Check if name is keyword
test_names = ["if", "class", "hello", "True", "None", "my_var"]
print("\n--- Keyword Check ---")
for name in test_names:
    is_kw = keyword.iskeyword(name)
    print(f"'{name}' is keyword: {is_kw}")

# 7. Type conversions
print("\n--- Type Conversions ---")
string_num = "42"
int_num = int(string_num)
float_num = float(string_num)
print(f"String '{string_num}' -> int: {int_num}, float: {float_num}")

# 8. String formatting methods
name = "Python"
version = 3.12
print("\n--- String Formatting ---")
print(f"f-string: {name} {version}")  # Preferred
print("format(): {} {}".format(name, version))
print("%-formatting: %s %.2f" % (name, version))

if __name__ == "__main__":
    print("\n✅ Day 1 basics completed!")
