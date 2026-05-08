# Day 8: Object-Oriented Programming Basics

## Learning Objectives
- Understand classes, objects, and the OOP paradigm in Python
- Master instance vs class variables and their scoping rules
- Implement all method types (instance, class, static)
- Use dunder/magic methods to customize object behavior
- Apply OOP to real-world modeling problems

---

## 1. Classes & Objects (Beginner)

### What is OOP?
Object-Oriented Programming organizes code around **objects** (data + behavior) rather than functions + logic. Python is multi-paradigm but OOP is core to its design.

### Defining a Class

```python
class BankAccount:
    """A simple bank account model."""
    
    # Class variable - shared across ALL instances
    bank_name = "Python National Bank"
    _total_accounts = 0
    
    def __init__(self, owner: str, balance: float = 0.0):
        """Constructor - called when creating an instance."""
        # Instance variables - unique to each object
        self.owner = owner
        self.balance = balance
        self._transaction_history = []
        BankAccount._total_accounts += 1
    
    def deposit(self, amount: float) -> float:
        """Instance method - operates on self."""
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self._transaction_history.append(f"+{amount}")
        return self.balance
    
    def withdraw(self, amount: float) -> float:
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self._transaction_history.append(f"-{amount}")
        return self.balance
    
    @classmethod
    def get_total_accounts(cls) -> int:
        """Class method - operates on the class itself."""
        return cls._total_accounts
    
    @classmethod
    def from_string(cls, account_str: str):
        """Alternative constructor using classmethod."""
        owner, balance = account_str.split(":")
        return cls(owner, float(balance))
    
    @staticmethod
    def validate_amount(amount) -> bool:
        """Static method - no access to instance or class."""
        return isinstance(amount, (int, float)) and amount > 0


# Usage
account = BankAccount("Alice", 1000)
account.deposit(500)
account.withdraw(200)
print(account.balance)  # 1300

# Alternative constructor
acc2 = BankAccount.from_string("Bob:2500")
print(BankAccount.get_total_accounts())  # 2
```

### Instance vs Class Variables

```python
class Employee:
    # Class variable - shared
    company = "TechCorp"
    raise_percentage = 0.05
    all_employees = []
    
    def __init__(self, name: str, salary: float):
        # Instance variables - unique per object
        self.name = name
        self.salary = salary
        Employee.all_employees.append(self)
    
    def apply_raise(self):
        # Uses class variable via self (allows override in subclass)
        self.salary *= (1 + self.raise_percentage)

# GOTCHA: Mutable class variables
class Team:
    members = []  # SHARED across all instances! Bug!
    
    def __init__(self, name):
        self.name = name
        # self.members.append(name)  # Modifies class variable!

# CORRECT approach:
class Team:
    def __init__(self, name):
        self.name = name
        self.members = []  # Instance variable - unique per object
```

---

## 2. Method Types & Properties (Intermediate)

```python
class Temperature:
    """Demonstrates properties and method types."""
    
    def __init__(self, celsius: float = 0):
        self._celsius = celsius  # Convention: _ means "private"
    
    @property
    def celsius(self) -> float:
        """Getter - access like attribute."""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value: float):
        """Setter with validation."""
        if value < -273.15:
            raise ValueError("Temperature below absolute zero!")
        self._celsius = value
    
    @property
    def fahrenheit(self) -> float:
        """Computed property."""
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value: float):
        self.celsius = (value - 32) * 5/9


temp = Temperature(100)
print(temp.fahrenheit)  # 212.0
temp.fahrenheit = 32
print(temp.celsius)     # 0.0
# temp.celsius = -300   # ValueError!
```

### Slots for Memory Optimization

```python
class Point:
    """Regular class - uses __dict__ (flexible but memory-heavy)."""
    def __init__(self, x, y):
        self.x = x
        self.y = y

class OptimizedPoint:
    """Slotted class - fixed attributes, ~40% less memory."""
    __slots__ = ('x', 'y')
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

# Can't add arbitrary attributes to slotted class:
p = OptimizedPoint(1, 2)
# p.z = 3  # AttributeError!

import sys
regular = Point(1, 2)
optimized = OptimizedPoint(1, 2)
print(sys.getsizeof(regular.__dict__))  # ~104 bytes
# OptimizedPoint has no __dict__ at all
```

---

## 3. Dunder/Magic Methods (Advanced)

```python
class Vector:
    """Full implementation showing operator overloading."""
    
    def __init__(self, *components):
        self._components = tuple(components)
    
    # String representations
    def __repr__(self) -> str:
        return f"Vector({', '.join(map(str, self._components))})"
    
    def __str__(self) -> str:
        return f"({', '.join(map(str, self._components))})"
    
    # Comparison
    def __eq__(self, other) -> bool:
        return self._components == other._components
    
    def __hash__(self) -> int:
        return hash(self._components)
    
    # Arithmetic operators
    def __add__(self, other):
        if len(self) != len(other):
            raise ValueError("Vectors must be same length")
        return Vector(*(a + b for a, b in zip(self._components, other._components)))
    
    def __mul__(self, scalar):
        return Vector(*(c * scalar for c in self._components))
    
    def __rmul__(self, scalar):
        """Handles: 3 * vector (reverse multiplication)."""
        return self.__mul__(scalar)
    
    # Container protocol
    def __len__(self) -> int:
        return len(self._components)
    
    def __getitem__(self, index):
        return self._components[index]
    
    def __iter__(self):
        return iter(self._components)
    
    # Numeric
    def __abs__(self) -> float:
        return sum(c ** 2 for c in self._components) ** 0.5
    
    def __bool__(self) -> bool:
        return any(self._components)
    
    # Context manager protocol
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass


v1 = Vector(1, 2, 3)
v2 = Vector(4, 5, 6)
print(v1 + v2)       # (5, 7, 9)
print(3 * v1)        # (3, 6, 9)
print(abs(v1))       # 3.7416...
print(len(v1))       # 3
print(v1[0])         # 1
```

### Descriptor Protocol

```python
class Validated:
    """Descriptor that validates on assignment."""
    
    def __init__(self, validator, error_msg):
        self.validator = validator
        self.error_msg = error_msg
    
    def __set_name__(self, owner, name):
        self.storage_name = f"_{name}"
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.storage_name, None)
    
    def __set__(self, obj, value):
        if not self.validator(value):
            raise ValueError(self.error_msg)
        setattr(obj, self.storage_name, value)


class Product:
    name = Validated(lambda v: isinstance(v, str) and len(v) > 0, "Name must be non-empty string")
    price = Validated(lambda v: isinstance(v, (int, float)) and v >= 0, "Price must be non-negative")
    quantity = Validated(lambda v: isinstance(v, int) and v >= 0, "Quantity must be non-negative int")
    
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity


p = Product("Widget", 9.99, 100)
# Product("", 9.99, 100)   # ValueError: Name must be non-empty string
# Product("X", -1, 100)    # ValueError: Price must be non-negative
```

---

## 4. Dataclasses & Modern OOP

```python
from dataclasses import dataclass, field
from typing import ClassVar

@dataclass(frozen=True, slots=True)
class Coordinate:
    """Immutable, memory-efficient dataclass."""
    x: float
    y: float
    
    def distance_to(self, other: 'Coordinate') -> float:
        return ((self.x - other.x)**2 + (self.y - other.y)**2) ** 0.5

@dataclass
class Order:
    """Dataclass with defaults and factory."""
    customer: str
    items: list[str] = field(default_factory=list)
    total: float = 0.0
    _id: int = field(init=False, repr=False)
    count: ClassVar[int] = 0  # Class variable, not in __init__
    
    def __post_init__(self):
        Order.count += 1
        self._id = Order.count
    
    def add_item(self, item: str, price: float):
        self.items.append(item)
        self.total += price


# Auto-generates __init__, __repr__, __eq__, __hash__ (if frozen)
c1 = Coordinate(3, 4)
c2 = Coordinate(0, 0)
print(c1.distance_to(c2))  # 5.0
```

---

## Interview Questions

### Beginner
1. **What's the difference between a class and an instance?** A class is a blueprint/template that defines attributes and methods. An instance is a specific object created from that class. Example: `class Dog` is the blueprint; `my_dog = Dog("Rex")` is an instance. Class variables are shared; instance variables (set via `self.x`) are unique per object.

2. **Explain `self` in Python.** `self` is a reference to the current instance of the class. It's passed automatically as the first argument to instance methods. It allows access to instance attributes and other methods. Unlike `this` in Java/JS, `self` is explicit in Python (not a keyword, just convention).

3. **What's the difference between `__str__` and `__repr__`?** `__str__` is for end-users (readable, informal). `__repr__` is for developers (unambiguous, ideally `eval(repr(obj))` recreates the object). If only one is defined, `__repr__` is the fallback for `str()`. Best practice: always define `__repr__`; optionally define `__str__` for user-facing output.

### Intermediate
4. **When would you use `@classmethod` vs `@staticmethod`?** `@classmethod`: needs access to the class (alternative constructors like `from_json()`, factory methods, accessing class variables). `@staticmethod`: utility function logically grouped with the class but needs no access to class or instance (validation helpers). Rule: if it doesn't use `cls` or `self`, make it `@staticmethod`; if it needs `cls`, use `@classmethod`.

5. **Explain Python's `@property` decorator.** `@property` turns a method into a read-only attribute. Paired with `@name.setter`, it provides controlled attribute access with validation. Benefits: clean API (`obj.value` not `obj.get_value()`), computed attributes, validation on set, backward-compatible refactoring (change internal storage without changing public API).

6. **What are `__slots__` and when should you use them?** `__slots__` replaces the instance `__dict__` with a fixed-size structure. Benefits: ~35-40% memory reduction, faster attribute access. Trade-offs: can't add arbitrary attributes, can't use multiple inheritance with conflicting slots. Use when: creating millions of instances (data points, nodes) or memory-constrained environments.

### Advanced
7. **Explain the descriptor protocol.** Descriptors implement `__get__`, `__set__`, and/or `__delete__`. Data descriptors (with `__set__`) override instance `__dict__`. Non-data descriptors (only `__get__`) can be overridden by instance attributes. Used internally for: `property`, `classmethod`, `staticmethod`, `__slots__`. Use for: reusable validation, lazy loading, computed attributes across multiple classes.

8. **What is the MRO (Method Resolution Order) and how does Python resolve it?** MRO defines the order Python searches for methods in inheritance hierarchies. Uses C3 Linearization algorithm: preserves local precedence order and monotonicity. Access via `ClassName.__mro__` or `ClassName.mro()`. Important for `super()` calls in diamond inheritance.

9. **How do you make a class behave like a built-in container?** Implement the appropriate protocols: `__getitem__`/`__setitem__` (indexing), `__len__` (length), `__iter__`/`__next__` (iteration), `__contains__` (membership), `__reversed__` (reverse iteration). For full compatibility, inherit from `collections.abc.MutableMapping` or `MutableSequence` which enforces the complete protocol.

---

## Hands-On Exercise
1. Create a `Money` class with currency and amount, supporting arithmetic between same-currency instances
2. Implement a `LinkedList` class with full iterator protocol (`__iter__`, `__len__`, `__getitem__`)
3. Build a `Config` class using descriptors for type-validated settings
4. Create a `@dataclass` for a shopping cart with computed totals via `@property`
