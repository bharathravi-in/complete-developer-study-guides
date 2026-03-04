#!/usr/bin/env python3
"""Day 13 - Type Hints & Static Typing"""

from typing import (
    List, Dict, Set, Tuple, Optional, Union, Any, Callable,
    TypeVar, Generic, Literal, Final, TypedDict, Protocol,
    Iterable, Iterator, Sequence, Mapping, ClassVar
)
from dataclasses import dataclass, field
from abc import abstractmethod

print("=" * 50)
print("TYPE HINTS & STATIC TYPING")
print("=" * 50)

# ============================================
# 1. BASIC TYPE HINTS
# ============================================
print("\n--- 1. BASIC TYPE HINTS ---")


def greet(name: str) -> str:
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    return a + b


def process_items(items: list[int]) -> list[int]:  # Python 3.9+
    return [x * 2 for x in items]


# Variable annotations
name: str = "Python"
age: int = 30
prices: list[float] = [9.99, 19.99, 29.99]
config: dict[str, any] = {"debug": True}

print(f"greet('World'): {greet('World')}")
print(f"add(1, 2): {add(1, 2)}")


# ============================================
# 2. OPTIONAL AND UNION
# ============================================
print("\n--- 2. OPTIONAL AND UNION ---")


def find_user(user_id: int) -> Optional[str]:
    """Return user name or None if not found"""
    users = {1: "Alice", 2: "Bob"}
    return users.get(user_id)


def parse_input(value: Union[str, int]) -> str:
    """Accept either string or int"""
    return str(value)


# Python 3.10+ syntax
def parse_input_new(value: str | int | None) -> str:
    """Using | operator (Python 3.10+)"""
    return str(value) if value else ""


print(f"find_user(1): {find_user(1)}")
print(f"find_user(99): {find_user(99)}")
print(f"parse_input(42): {parse_input(42)}")


# ============================================
# 3. CALLABLE
# ============================================
print("\n--- 3. CALLABLE ---")


def apply_operation(
    x: int,
    operation: Callable[[int], int]
) -> int:
    """Apply a function to x"""
    return operation(x)


def square(n: int) -> int:
    return n ** 2


# Callable with multiple args
Comparator = Callable[[int, int], bool]


def sort_with_comparator(items: list[int], compare: Comparator) -> list[int]:
    # Simplified example
    return sorted(items, key=lambda x: x)


result = apply_operation(5, square)
print(f"apply_operation(5, square): {result}")


# ============================================
# 4. GENERICS
# ============================================
print("\n--- 4. GENERICS ---")

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


def first(items: list[T]) -> T | None:
    """Get first item of any type"""
    return items[0] if items else None


def merge_dicts(d1: dict[K, V], d2: dict[K, V]) -> dict[K, V]:
    """Merge two dicts of same type"""
    return {**d1, **d2}


# Generic class
class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        return self._items.pop()
    
    def __repr__(self) -> str:
        return f"Stack({self._items})"


int_stack: Stack[int] = Stack()
int_stack.push(1)
int_stack.push(2)
print(f"Stack[int]: {int_stack}")
print(f"pop(): {int_stack.pop()}")


# ============================================
# 5. TYPEDDICT
# ============================================
print("\n--- 5. TYPEDDICT ---")


class UserDict(TypedDict):
    """Typed dictionary for user data"""
    name: str
    age: int
    email: str


class PartialUser(TypedDict, total=False):
    """All keys are optional"""
    name: str
    age: int


def create_user(data: UserDict) -> str:
    return f"User: {data['name']}, {data['age']}"


user: UserDict = {"name": "Alice", "age": 30, "email": "alice@test.com"}
print(f"UserDict: {create_user(user)}")


# ============================================
# 6. LITERAL AND FINAL
# ============================================
print("\n--- 6. LITERAL AND FINAL ---")


def set_status(status: Literal["active", "inactive", "pending"]) -> None:
    """Only accept specific string values"""
    print(f"Status set to: {status}")


set_status("active")
# set_status("unknown")  # Type error!


# Final - constant values
MAX_CONNECTIONS: Final = 100
API_VERSION: Final[str] = "v1"

print(f"MAX_CONNECTIONS: {MAX_CONNECTIONS}")


# ============================================
# 7. PROTOCOLS (STRUCTURAL SUBTYPING)
# ============================================
print("\n--- 7. PROTOCOLS ---")


class Drawable(Protocol):
    """Protocol defining drawable objects"""
    def draw(self) -> str: ...


class Circle:
    def draw(self) -> str:
        return "Drawing circle"


class Square:
    def draw(self) -> str:
        return "Drawing square"


def render(shape: Drawable) -> None:
    """Works with any object that has draw() method"""
    print(f"  {shape.draw()}")


# No inheritance needed - structural typing
print("Protocol example:")
render(Circle())
render(Square())


# ============================================
# 8. DATACLASSES WITH TYPES
# ============================================
print("\n--- 8. DATACLASSES ---")


@dataclass
class Point:
    x: float
    y: float
    label: str = "origin"


@dataclass
class Rectangle:
    top_left: Point
    bottom_right: Point
    
    @property
    def width(self) -> float:
        return self.bottom_right.x - self.top_left.x
    
    @property
    def height(self) -> float:
        return self.bottom_right.y - self.top_left.y


@dataclass
class Config:
    """Dataclass with advanced features"""
    name: str
    values: list[int] = field(default_factory=list)
    _cache: dict = field(default_factory=dict, repr=False)
    version: ClassVar[str] = "1.0"  # Class variable


p1 = Point(0, 0)
p2 = Point(10, 10)
rect = Rectangle(p1, p2)
print(f"Point: {p1}")
print(f"Rectangle width: {rect.width}")


# ============================================
# 9. TYPE ALIASES
# ============================================
print("\n--- 9. TYPE ALIASES ---")

# Simple alias
UserId = int
Coordinates = tuple[float, float]

# Complex alias
JSON = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
Handler = Callable[[str, dict[str, Any]], Optional[str]]


def process_coordinates(coords: Coordinates) -> float:
    x, y = coords
    return (x ** 2 + y ** 2) ** 0.5


print(f"Distance from origin: {process_coordinates((3.0, 4.0))}")


# ============================================
# 10. TYPE CHECKING WITH MYPY
# ============================================
print("\n--- 10. MYPY COMMANDS ---")

print("""
Running type checks:
  mypy script.py           # Check single file
  mypy src/                # Check directory
  mypy --strict script.py  # Strict mode
  
Configuration (pyproject.toml):
  [tool.mypy]
  python_version = "3.12"
  strict = true
  ignore_missing_imports = true

Common mypy flags:
  --ignore-missing-imports    Ignore missing type stubs
  --disallow-untyped-defs     Require type hints
  --no-implicit-optional      Don't assume Optional
""")


# ============================================
# 11. OVERLOAD
# ============================================
print("\n--- 11. OVERLOAD ---")

from typing import overload


class Calculator:
    @overload
    def add(self, x: int, y: int) -> int: ...
    
    @overload
    def add(self, x: float, y: float) -> float: ...
    
    @overload
    def add(self, x: str, y: str) -> str: ...
    
    def add(self, x, y):
        return x + y


calc = Calculator()
print(f"int + int: {calc.add(1, 2)}")
print(f"str + str: {calc.add('Hello, ', 'World')}")


print("\n✅ Day 13 completed!")
