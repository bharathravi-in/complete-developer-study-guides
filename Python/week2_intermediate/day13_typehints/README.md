# Day 13: Type Hints & Static Typing — mypy, Pydantic & Generics

## Learning Objectives
- Master Python's type annotation system
- Use `typing` module for complex types (generics, protocols, overloads)
- Validate data with Pydantic models
- Configure and use mypy for static type checking
- Apply typing best practices in production code

---

## 1. Type Annotations Basics (Beginner)

```python
# Python 3.10+ syntax (no imports needed for basic types)
def greet(name: str, times: int = 1) -> str:
    return (f"Hello, {name}! " * times).strip()

# Variable annotations
age: int = 25
names: list[str] = ["Alice", "Bob"]
config: dict[str, int] = {"timeout": 30, "retries": 3}
coordinates: tuple[float, float] = (51.5, -0.1)

# Optional (can be None)
from typing import Optional
def find_user(user_id: int) -> Optional[dict]:
    """Returns user dict or None if not found."""
    # Python 3.10+: can write  dict | None  instead
    ...

# Union types
def process(value: int | str | float) -> str:
    return str(value)

# Collections (Python 3.9+ built-in generics)
def summarize(items: list[dict[str, int]]) -> dict[str, float]:
    totals: dict[str, float] = {}
    for item in items:
        for key, val in item.items():
            totals[key] = totals.get(key, 0) + val
    return totals
```

### Type Aliases & Callables

```python
from typing import Callable, TypeAlias

# Type aliases for complex types
JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None
UserID: TypeAlias = int
Handler: TypeAlias = Callable[[str, int], bool]

# Callable types
def apply_operation(
    values: list[int],
    operation: Callable[[int], int]  # Takes int, returns int
) -> list[int]:
    return [operation(v) for v in values]

doubled = apply_operation([1, 2, 3], lambda x: x * 2)  # [2, 4, 6]

# Functions with callbacks
def fetch_data(
    url: str,
    on_success: Callable[[dict], None],
    on_error: Callable[[Exception], None] = lambda e: None
) -> None:
    ...
```

---

## 2. Advanced Typing (Intermediate)

```python
from typing import TypeVar, Generic, Protocol, overload, Literal, TypeGuard
from dataclasses import dataclass

# Generics — type-safe containers
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []
    
    def push(self, item: T) -> None:
        self._items.append(item)
    
    def pop(self) -> T:
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()
    
    def peek(self) -> T:
        return self._items[-1]

# Type checker knows what's in the stack
int_stack: Stack[int] = Stack()
int_stack.push(42)
value: int = int_stack.pop()  # mypy knows this is int
# int_stack.push("hello")    # mypy error!


# Bounded TypeVar
from typing import SupportsFloat
Numeric = TypeVar('Numeric', bound=SupportsFloat)

def average(values: list[Numeric]) -> float:
    return sum(float(v) for v in values) / len(values)


# Protocol (structural typing)
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> dict: ...
    def from_dict(cls, data: dict) -> 'Serializable': ...

# Any class with to_dict/from_dict methods satisfies this
class User:
    def to_dict(self) -> dict:
        return {"name": self.name}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        return cls(data["name"])

def save(obj: Serializable) -> None:
    data = obj.to_dict()  # Type-safe!


# Overloaded functions
@overload
def parse(value: str) -> dict: ...
@overload
def parse(value: bytes) -> str: ...
@overload
def parse(value: int) -> float: ...

def parse(value: str | bytes | int) -> dict | str | float:
    if isinstance(value, str):
        return json.loads(value)
    elif isinstance(value, bytes):
        return value.decode()
    return float(value)


# Literal types
def set_mode(mode: Literal["read", "write", "append"]) -> None:
    ...

# TypeGuard — narrowing types
def is_string_list(val: list) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)
```

---

## 3. Pydantic & Data Validation (Advanced)

```python
from pydantic import BaseModel, Field, validator, field_validator
from pydantic import EmailStr, HttpUrl, ConfigDict
from datetime import datetime
from typing import Annotated

class Address(BaseModel):
    street: str
    city: str
    country: str = "US"
    zip_code: str = Field(pattern=r'^\d{5}(-\d{4})?$')

class User(BaseModel):
    """Pydantic model with validation."""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: Annotated[int, Field(ge=0, le=150)]
    role: Literal["admin", "user", "moderator"] = "user"
    address: Address | None = None
    tags: list[str] = Field(default_factory=list, max_length=10)
    created_at: datetime = Field(default_factory=datetime.now)
    
    @field_validator('name')
    @classmethod
    def name_must_be_titlecase(cls, v: str) -> str:
        return v.strip().title()

# Automatic validation on creation
user = User(name="alice smith", email="alice@example.com", age=30)
print(user.name)  # "Alice Smith" (validated + transformed)
print(user.model_dump_json(indent=2))

# Validation errors are detailed
try:
    User(name="", email="not-an-email", age=200)
except ValidationError as e:
    print(e.errors())
    # [{'type': 'string_too_short', 'loc': ('name',), ...},
    #  {'type': 'value_error', 'loc': ('email',), ...},
    #  {'type': 'less_than_equal', 'loc': ('age',), ...}]


# Pydantic for API request/response
class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)  # ORM mode
```

### mypy Configuration

```ini
# mypy.ini or pyproject.toml [tool.mypy]
[mypy]
python_version = 3.12
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

# Per-module overrides
[mypy-tests.*]
disallow_untyped_defs = false

[mypy-third_party_lib.*]
ignore_missing_imports = true
```

```bash
# Running mypy
mypy src/ --strict
mypy src/ --show-error-codes --pretty
```

---

## Interview Questions

### Beginner
1. **Are type hints enforced at runtime?** No! Python's type hints are completely ignored at runtime (except by tools like Pydantic which explicitly use them). They're for: IDE autocompletion, static analysis (mypy), documentation. You can assign a string to an `int`-annotated variable without error. They're "gradual typing" — you can add them incrementally.

2. **What's the difference between `list` and `List[int]`?** `list` (lowercase, Python 3.9+) or `List` (from typing, older) is just the type. `list[int]` specifies the element type — the list contains integers. Without the generic parameter, type checkers treat contents as `Any`. Always parameterize containers: `list[str]`, `dict[str, int]`, `tuple[int, ...]`.

3. **What is `Optional[X]` equivalent to?** `Optional[X]` equals `X | None` (Python 3.10+) or `Union[X, None]`. It means the value can be of type X OR None. Common mistake: using `Optional` for optional parameters — it's about the TYPE being nullable, not about the parameter being optional (`def f(x: int = 5)` — x is optional but NOT Optional[int]).

### Intermediate
4. **Explain `TypeVar` and generics in Python.** `TypeVar` creates a placeholder type that must be consistent within a function/class. `T = TypeVar('T')` means "some type T". In `def first(items: list[T]) -> T`, if called with `list[int]`, return type is `int`. `Generic[T]` makes classes parameterizable: `Stack[int]` vs `Stack[str]`. Bounded TypeVars constrain: `T = TypeVar('T', bound=Comparable)`.

5. **When would you use Protocol vs ABC for typing?** Protocol: structural/duck typing (any class with matching methods works, no inheritance needed). ABC: nominal typing (must explicitly inherit). Use Protocol for: third-party classes you can't modify, flexible interfaces, Pythonic duck typing with type safety. Use ABC when: you want to prevent instantiation, provide shared implementations.

6. **How does Pydantic differ from dataclasses?** Dataclasses: lightweight, no runtime validation, part of stdlib, fast. Pydantic: runtime validation, type coercion (string "42" → int 42), JSON serialization, nested model validation, custom validators. Use dataclasses for: internal data structures. Use Pydantic for: external data (APIs, config files, user input) where validation matters.

### Advanced
7. **Explain `TypeGuard` and type narrowing.** `TypeGuard[T]` in a function return type tells the type checker: "if this returns True, the argument is of type T." Used for custom type guards that narrow types in if-blocks. Example: `def is_string_list(x: list) -> TypeGuard[list[str]]`. After `if is_string_list(items):`, mypy knows `items` is `list[str]`.

8. **How do you type decorators correctly?** Use `ParamSpec` (P) and `TypeVar` (T): `P = ParamSpec('P'); T = TypeVar('T')`. Decorator: `def deco(func: Callable[P, T]) -> Callable[P, T]`. This preserves the wrapped function's exact signature. Without `ParamSpec`, decorated functions lose their parameter types in mypy.

9. **Design a type-safe event system using generics.** Use `Generic[T]` for typed events: `class Event(Generic[T]): data: T`. Handlers typed as `Callable[[T], None]`. EventBus maps event types to handlers: `dict[type[Event[Any]], list[Callable]]`. This ensures: publish `Event[UserCreated]` → only handlers expecting `UserCreated` can subscribe. Full compile-time safety with mypy.

---

## Hands-On Exercise
1. Add type annotations to an existing untyped module and run mypy strict
2. Create a generic `Repository[T]` class with CRUD operations
3. Build a Pydantic model for a complex API response with nested validation
4. Implement a typed event system using Protocol and Generic
5. Configure mypy in a project with per-module strictness levels
