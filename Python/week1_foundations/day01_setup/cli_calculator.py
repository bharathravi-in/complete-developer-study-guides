#!/usr/bin/env python3
"""
Day 1 Practice Project: CLI Calculator
A command-line calculator supporting basic arithmetic operations.
"""


def calculate(num1: float, operator: str, num2: float) -> float | str:
    """Perform arithmetic operation on two numbers."""
    operations = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b if b != 0 else "Error: Division by zero",
        '//': lambda a, b: a // b if b != 0 else "Error: Division by zero",
        '%': lambda a, b: a % b if b != 0 else "Error: Modulo by zero",
        '**': lambda a, b: a ** b,
    }
    
    if operator not in operations:
        return f"Error: Unknown operator '{operator}'"
    
    return operations[operator](num1, num2)


def get_number(prompt: str) -> float | None:
    """Get a valid number from user input."""
    try:
        return float(input(prompt))
    except ValueError:
        print("❌ Invalid number. Please enter a valid number.")
        return None


def display_menu():
    """Display calculator menu."""
    print("\n" + "=" * 40)
    print("🧮 CLI CALCULATOR")
    print("=" * 40)
    print("Supported operators: +  -  *  /  //  %  **")
    print("Type 'quit' or 'q' to exit")
    print("Type 'clear' to start fresh")
    print("=" * 40)


def main():
    """Main calculator loop."""
    display_menu()
    result = None
    
    while True:
        print()
        
        # Get first number (or use previous result)
        if result is not None:
            use_prev = input(f"Use previous result ({result})? [y/n]: ").lower()
            if use_prev == 'y':
                num1 = result
            else:
                num1 = get_number("Enter first number: ")
                if num1 is None:
                    continue
        else:
            user_input = input("Enter first number (or 'quit'): ")
            if user_input.lower() in ('quit', 'q'):
                print("\n👋 Goodbye!")
                break
            if user_input.lower() == 'clear':
                result = None
                display_menu()
                continue
            try:
                num1 = float(user_input)
            except ValueError:
                print("❌ Invalid number.")
                continue
        
        # Get operator
        operator = input("Enter operator (+, -, *, /, //, %, **): ").strip()
        if operator.lower() in ('quit', 'q'):
            print("\n👋 Goodbye!")
            break
        
        # Get second number
        num2 = get_number("Enter second number: ")
        if num2 is None:
            continue
        
        # Calculate and display result
        result = calculate(num1, operator, num2)
        
        if isinstance(result, str) and result.startswith("Error"):
            print(f"\n❌ {result}")
            result = None
        else:
            print(f"\n✅ {num1} {operator} {num2} = {result}")


if __name__ == "__main__":
    main()
