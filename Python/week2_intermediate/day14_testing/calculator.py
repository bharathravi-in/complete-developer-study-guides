"""Calculator module for testing demo"""

from typing import Union, List

Number = Union[int, float]


class Calculator:
    """A simple calculator class for demonstration"""
    
    def __init__(self, precision: int = 2):
        self.precision = precision
        self.history: List[str] = []
    
    def add(self, a: Number, b: Number) -> Number:
        """Add two numbers"""
        result = a + b
        self._log(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: Number, b: Number) -> Number:
        """Subtract b from a"""
        result = a - b
        self._log(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: Number, b: Number) -> Number:
        """Multiply two numbers"""
        result = a * b
        self._log(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a: Number, b: Number) -> float:
        """Divide a by b"""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = round(a / b, self.precision)
        self._log(f"{a} / {b} = {result}")
        return result
    
    def power(self, base: Number, exponent: int) -> Number:
        """Raise base to the power of exponent"""
        result = base ** exponent
        self._log(f"{base} ^ {exponent} = {result}")
        return result
    
    def _log(self, operation: str) -> None:
        """Log operation to history"""
        self.history.append(operation)
    
    def clear_history(self) -> None:
        """Clear operation history"""
        self.history = []


class AdvancedCalculator(Calculator):
    """Extended calculator with more operations"""
    
    def sqrt(self, n: Number) -> float:
        """Calculate square root"""
        if n < 0:
            raise ValueError("Cannot calculate square root of negative number")
        import math
        result = round(math.sqrt(n), self.precision)
        self._log(f"√{n} = {result}")
        return result
    
    def factorial(self, n: int) -> int:
        """Calculate factorial"""
        if n < 0:
            raise ValueError("Factorial not defined for negative numbers")
        if not isinstance(n, int):
            raise TypeError("Factorial only defined for integers")
        
        import math
        result = math.factorial(n)
        self._log(f"{n}! = {result}")
        return result
