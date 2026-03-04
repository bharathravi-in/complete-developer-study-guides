#!/usr/bin/env python3
"""Day 6 - Error Handling Deep Dive"""

import traceback
import sys

print("=" * 50)
print("ERROR HANDLING DEEP DIVE")
print("=" * 50)

# ============================================
# 1. BASIC TRY-EXCEPT
# ============================================
print("\n--- 1. BASIC TRY-EXCEPT ---")


def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("  Cannot divide by zero!")
        return None
    return result


print(f"10 / 2 = {divide(10, 2)}")
print(f"10 / 0 = {divide(10, 0)}")


# ============================================
# 2. MULTIPLE EXCEPTIONS
# ============================================
print("\n--- 2. MULTIPLE EXCEPTIONS ---")


def process_data(data, index):
    try:
        value = data[index]
        result = 100 / value
        return result
    except IndexError:
        return "Index out of range"
    except ZeroDivisionError:
        return "Cannot divide by zero"
    except TypeError:
        return "Invalid type"


data = [10, 0, 5]
print(f"Index 0: {process_data(data, 0)}")
print(f"Index 1: {process_data(data, 1)}")
print(f"Index 10: {process_data(data, 10)}")
print(f"None data: {process_data(None, 0)}")


# Catch multiple in one line
def catch_multiple():
    try:
        # Some risky operation
        x = int("abc")
    except (ValueError, TypeError) as e:
        print(f"  Caught: {type(e).__name__}: {e}")


catch_multiple()


# ============================================
# 3. ELSE AND FINALLY
# ============================================
print("\n--- 3. ELSE AND FINALLY ---")


def read_file_demo(filename):
    file = None
    try:
        file = open(filename, "r")
        content = file.read()
    except FileNotFoundError:
        print(f"  File '{filename}' not found")
        content = None
    else:
        # Runs only if no exception
        print(f"  Successfully read {len(content)} characters")
    finally:
        # Always runs
        if file:
            file.close()
            print("  File closed")
    return content


read_file_demo("nonexistent.txt")


# ============================================
# 4. RAISE EXCEPTIONS
# ============================================
print("\n--- 4. RAISE EXCEPTIONS ---")


def validate_age(age):
    if not isinstance(age, int):
        raise TypeError(f"Age must be int, got {type(age).__name__}")
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age seems unrealistic")
    return age


# Test validation
test_ages = [25, -5, 200, "thirty"]
for age in test_ages:
    try:
        result = validate_age(age)
        print(f"  Valid age: {result}")
    except (TypeError, ValueError) as e:
        print(f"  Invalid age {age!r}: {e}")


# Re-raising exceptions
def process_with_logging(value):
    try:
        return 100 / value
    except ZeroDivisionError:
        print("  Logging: Division by zero occurred")
        raise  # Re-raise the same exception


print("\nRe-raising example:")
try:
    process_with_logging(0)
except ZeroDivisionError:
    print("  Caught re-raised exception")


# ============================================
# 5. EXCEPTION CHAINING
# ============================================
print("\n--- 5. EXCEPTION CHAINING ---")


def fetch_user(user_id):
    # Simulate database error
    raise ConnectionError("Database connection failed")


def get_user_info(user_id):
    try:
        return fetch_user(user_id)
    except ConnectionError as e:
        # Chain to a different exception
        raise RuntimeError(f"Failed to get user {user_id}") from e


try:
    get_user_info(123)
except RuntimeError as e:
    print(f"  Error: {e}")
    print(f"  Caused by: {e.__cause__}")


# ============================================
# 6. EXCEPTION INFO AND TRACEBACK
# ============================================
print("\n--- 6. EXCEPTION INFO ---")


def risky_function():
    return 1 / 0


try:
    risky_function()
except Exception as e:
    exc_type, exc_value, exc_tb = sys.exc_info()
    print(f"  Type: {exc_type.__name__}")
    print(f"  Value: {exc_value}")
    print(f"  Traceback:")
    for line in traceback.format_tb(exc_tb):
        print(f"    {line.strip()}")


# ============================================
# 7. CONTEXT MANAGERS FOR CLEANUP
# ============================================
print("\n--- 7. CONTEXT MANAGERS ---")


class DatabaseConnection:
    def __init__(self, name):
        self.name = name
    
    def __enter__(self):
        print(f"  Opening connection to {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"  Closing connection to {self.name}")
        if exc_type is not None:
            print(f"  Exception occurred: {exc_val}")
        return False  # Don't suppress exception


with DatabaseConnection("users_db") as conn:
    print(f"  Working with {conn.name}")


print("\nWith exception:")
try:
    with DatabaseConnection("orders_db") as conn:
        print("  About to raise exception...")
        raise ValueError("Something went wrong")
except ValueError:
    print("  Exception handled outside context manager")


# ============================================
# 8. ASSERTIONS
# ============================================
print("\n--- 8. ASSERTIONS ---")


def calculate_discount(price, discount_percent):
    assert price >= 0, "Price must be non-negative"
    assert 0 <= discount_percent <= 100, "Discount must be 0-100"
    return price * (1 - discount_percent / 100)


print(f"  Discount: {calculate_discount(100, 20)}")

try:
    calculate_discount(-100, 20)
except AssertionError as e:
    print(f"  Assertion failed: {e}")


# ============================================
# 9. BEST PRACTICES
# ============================================
print("\n--- 9. BEST PRACTICES ---")

print("""
✅ DO:
  - Catch specific exceptions
  - Use 'else' for success-only code
  - Use 'finally' for cleanup
  - Include helpful error messages
  - Log exceptions appropriately
  - Create custom exceptions for domain errors

❌ DON'T:
  - Use bare 'except:'
  - Catch 'Exception' without good reason
  - Silently swallow exceptions
  - Use exceptions for flow control
  - Catch and ignore exceptions
""")

# Bad example
def bad_error_handling():
    try:
        # Some code
        pass
    except:  # Bad: catches EVERYTHING including KeyboardInterrupt
        pass  # Bad: silently ignores


# Good example
def good_error_handling(filename):
    try:
        with open(filename) as f:
            return f.read()
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
    except PermissionError:
        print(f"Permission denied: {filename}")
        return None


print("\n✅ Day 6 completed!")
