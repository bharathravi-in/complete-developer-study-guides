# Day 3 - Control Flow

## Topics Covered
- if-else
- Nested conditions
- match-case (Python 3.10+)
- Loops (for, while)
- break, continue, pass

## Key Concepts

### Truthy and Falsy Values
```python
# Falsy values
False, None, 0, 0.0, '', [], {}, set()

# Everything else is truthy
```

### Match-Case (Python 3.10+)
```python
match command:
    case "quit":
        exit()
    case "help":
        show_help()
    case _:  # Default
        print("Unknown command")
```

### Loop Else Clause
```python
for item in items:
    if found:
        break
else:
    # Runs if loop completes without break
    print("Not found")
```

## Practice Tasks
1. FizzBuzz (1-100)
2. Prime number checker
3. Number guessing game

## Run
```bash
python practice.py
python fizzbuzz.py
python prime_checker.py
```
