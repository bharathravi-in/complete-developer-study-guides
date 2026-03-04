# Day 6 - Error Handling

## Topics Covered
- try-except
- finally
- raise
- Custom exceptions
- Exception hierarchy

## Exception Hierarchy
```
BaseException
├── SystemExit
├── KeyboardInterrupt
├── GeneratorExit
└── Exception
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   └── OverflowError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── TypeError
    ├── ValueError
    ├── AttributeError
    ├── OSError
    │   ├── FileNotFoundError
    │   └── PermissionError
    └── ... (many more)
```

## Best Practices
1. Catch specific exceptions, not bare `except:`
2. Use `else` for code that runs if no exception
3. Use `finally` for cleanup
4. Create custom exceptions for your domain
5. Always provide helpful error messages

## Run
```bash
python practice.py
python custom_exceptions.py
```
