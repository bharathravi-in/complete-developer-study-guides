# Day 9: OOP Advanced — Inheritance, Polymorphism & Abstract Classes

## Learning Objectives
- Master single, multiple, and mixin inheritance patterns
- Understand MRO and `super()` in complex hierarchies
- Implement polymorphism and duck typing
- Use abstract base classes (ABC) for interface contracts
- Apply SOLID principles in Python OOP

---

## 1. Inheritance Patterns (Beginner)

```python
class Animal:
    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species
    
    def speak(self) -> str:
        return f"{self.name} makes a sound"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name!r})"


class Dog(Animal):
    def __init__(self, name: str, breed: str):
        super().__init__(name, species="Canis familiaris")
        self.breed = breed
    
    def speak(self) -> str:  # Override
        return f"{self.name} barks!"
    
    def fetch(self, item: str) -> str:
        return f"{self.name} fetches the {item}"


class Cat(Animal):
    def __init__(self, name: str, indoor: bool = True):
        super().__init__(name, species="Felis catus")
        self.indoor = indoor
    
    def speak(self) -> str:
        return f"{self.name} meows!"


# Polymorphism in action
animals: list[Animal] = [Dog("Rex", "Labrador"), Cat("Whiskers"), Dog("Buddy", "Poodle")]
for animal in animals:
    print(animal.speak())  # Each calls its own version
```

### Encapsulation

```python
class BankAccount:
    def __init__(self, owner: str, balance: float):
        self.owner = owner           # Public
        self._balance = balance      # Protected (convention)
        self.__pin = "1234"          # Name-mangled → _BankAccount__pin
    
    @property
    def balance(self) -> float:
        return self._balance
    
    def _validate_amount(self, amount: float) -> bool:
        """Protected method - for internal/subclass use."""
        return amount > 0
    
    def withdraw(self, amount: float, pin: str) -> float:
        if pin != self.__pin:
            raise PermissionError("Invalid PIN")
        if not self._validate_amount(amount):
            raise ValueError("Invalid amount")
        if amount > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount
        return self._balance

# Name mangling access (not truly private!)
acc = BankAccount("Alice", 1000)
# acc.__pin  # AttributeError
# acc._BankAccount__pin  # Works but DON'T do this!
```

---

## 2. Multiple Inheritance & Mixins (Intermediate)

```python
# Mixin pattern - adds behavior without being a standalone class
class SerializableMixin:
    """Mixin: adds JSON serialization to any class."""
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), default=str)

class LoggableMixin:
    """Mixin: adds logging capability."""
    def log(self, message: str):
        print(f"[{self.__class__.__name__}] {message}")

class TimestampMixin:
    """Mixin: adds created_at timestamp."""
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from datetime import datetime
        self.created_at = datetime.now()


# Combining mixins
class User(SerializableMixin, LoggableMixin, TimestampMixin):
    def __init__(self, name: str, email: str):
        super().__init__()
        self.name = name
        self.email = email

user = User("Alice", "alice@example.com")
print(user.to_json())   # {"name": "Alice", "email": "alice@example.com", "created_at": "..."}
user.log("User created")  # [User] User created
```

### MRO — Method Resolution Order

```python
class A:
    def method(self):
        print("A.method")
        super().method()  # Calls next in MRO!

class B(A):
    def method(self):
        print("B.method")
        super().method()

class C(A):
    def method(self):
        print("C.method")
        super().method()

class D(B, C):
    def method(self):
        print("D.method")
        super().method()

# MRO: D → B → C → A → object
print(D.__mro__)
# D.method → B.method → C.method → A.method

d = D()
d.method()
# Output: D.method, B.method, C.method, A.method
# super() follows MRO, NOT parent class!
```

---

## 3. Abstract Base Classes & Protocols (Advanced)

```python
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

# ABC approach - explicit contract
class Shape(ABC):
    """Abstract base class - cannot be instantiated directly."""
    
    @abstractmethod
    def area(self) -> float:
        """Subclasses MUST implement this."""
        ...
    
    @abstractmethod
    def perimeter(self) -> float:
        ...
    
    def describe(self) -> str:
        """Concrete method - inherited by subclasses."""
        return f"{self.__class__.__name__}: area={self.area():.2f}, perimeter={self.perimeter():.2f}"


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius
    
    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2
    
    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.radius


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    
    def area(self) -> float:
        return self.width * self.height
    
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


# shape = Shape()  # TypeError: Can't instantiate abstract class
circle = Circle(5)
print(circle.describe())  # Circle: area=78.54, perimeter=31.42


# Protocol approach (structural typing / duck typing formalized)
@runtime_checkable
class Drawable(Protocol):
    """Any class with draw() method satisfies this protocol."""
    def draw(self) -> None: ...

class Canvas:
    def draw(self) -> None:
        print("Drawing canvas")

# No inheritance needed!
canvas = Canvas()
print(isinstance(canvas, Drawable))  # True (structural check)
```

### SOLID Principles in Python

```python
# S - Single Responsibility
class UserRepository:
    """Only handles data persistence."""
    def save(self, user): ...
    def find(self, user_id): ...

class UserService:
    """Only handles business logic."""
    def __init__(self, repo: UserRepository):
        self.repo = repo
    def register(self, name, email): ...

# O - Open/Closed (open for extension, closed for modification)
class Discount(ABC):
    @abstractmethod
    def calculate(self, price: float) -> float: ...

class PercentDiscount(Discount):
    def __init__(self, percent: float):
        self.percent = percent
    def calculate(self, price: float) -> float:
        return price * (1 - self.percent / 100)

class FlatDiscount(Discount):
    def __init__(self, amount: float):
        self.amount = amount
    def calculate(self, price: float) -> float:
        return max(0, price - self.amount)

# L - Liskov Substitution
# Subclasses must be substitutable for their base class
# If Square extends Rectangle, setting width shouldn't break height

# I - Interface Segregation
class Readable(Protocol):
    def read(self) -> str: ...

class Writable(Protocol):
    def write(self, data: str) -> None: ...

# D - Dependency Inversion
class NotificationService:
    def __init__(self, sender: 'MessageSender'):  # Depends on abstraction
        self.sender = sender
    
    def notify(self, user, message):
        self.sender.send(user.email, message)
```

---

## 4. Composition vs Inheritance

```python
# PREFER composition over deep inheritance hierarchies

class Engine:
    def __init__(self, horsepower: int):
        self.horsepower = horsepower
        self.running = False
    
    def start(self):
        self.running = True
    
    def stop(self):
        self.running = False

class GPS:
    def navigate(self, destination: str) -> str:
        return f"Navigating to {destination}"

class Car:
    """Composition: Car HAS-A engine and GPS (not IS-A)."""
    
    def __init__(self, make: str, model: str, hp: int):
        self.make = make
        self.model = model
        self.engine = Engine(hp)  # Composition
        self.gps = GPS()          # Composition
    
    def drive(self, destination: str):
        self.engine.start()
        route = self.gps.navigate(destination)
        return f"{self.make} {self.model} driving. {route}"

# vs BAD inheritance:
# class Car(Engine, GPS, Vehicle, Registerable):  # God class!
```

---

## Interview Questions

### Beginner
1. **What is inheritance and why use it?** Inheritance allows a class to acquire attributes and methods from a parent class. Benefits: code reuse, establishes IS-A relationships, enables polymorphism. Example: `Dog(Animal)` inherits `eat()` and `sleep()` but overrides `speak()`. Caveat: prefer composition for HAS-A relationships.

2. **What's the difference between `_protected` and `__private`?** `_protected`: naming convention only, signals "internal use" but Python doesn't enforce it. `__private`: name mangling — Python renames to `_ClassName__attr`, making accidental access from subclasses harder. Neither is truly private. Use `_protected` for 99% of cases; use `__private` only to prevent name collisions in inheritance.

3. **What is polymorphism? Give an example.** Polymorphism means "many forms" — the same interface works with different types. In Python: same method name, different behavior per class. `animal.speak()` produces different output for Dog vs Cat. Python uses duck typing: "if it walks like a duck and quacks like a duck, it's a duck." No need for explicit interface declaration.

### Intermediate
4. **Explain MRO and how `super()` works with multiple inheritance.** MRO (C3 Linearization) determines method lookup order. `super()` doesn't call the parent — it calls the NEXT class in MRO. For `class D(B, C)` where B and C extend A: MRO is D→B→C→A→object. This ensures each class's method is called exactly once in diamond inheritance, avoiding duplication.

5. **When would you use an ABC vs a Protocol?** ABC (nominal typing): use when you want explicit "is-a" contracts, shared concrete methods, and prevent instantiation of incomplete classes. Protocol (structural typing): use when you want duck typing with type checker support, no inheritance required, third-party classes can satisfy it without modification. Protocol is more Pythonic; ABC is stricter.

6. **Explain the difference between composition and inheritance. When to use each?** Inheritance: IS-A relationship (Dog IS-A Animal). Composition: HAS-A relationship (Car HAS-A Engine). Prefer composition because: easier to change, avoids deep hierarchies, more flexible. Use inheritance for: true type hierarchies, polymorphism requirements, framework patterns (ABC). Rule of thumb: if unsure, use composition.

### Advanced
7. **How does Python's `__init_subclass__` work and when would you use it?** Called when a class is subclassed (on the parent). Receives the new subclass as argument. Use for: registering plugins, validating subclass structure, auto-decorating methods. It's a simpler alternative to metaclasses for most customization needs. Example: auto-register all subclasses in a registry dict.

8. **Explain metaclasses and give a practical use case.** Metaclass is the "class of a class" (default: `type`). `__new__` creates the class object, `__init__` initializes it. Use for: enforcing coding standards (all methods must have docstrings), automatic `__slots__`, ORM field registration (Django models), singleton pattern. Metaclasses should be last resort — prefer `__init_subclass__` or decorators.

9. **Design a plugin system using OOP principles.** Use ABC for the plugin interface, `__init_subclass__` for auto-registration, composition for plugin manager. Each plugin implements the contract (ABC). Manager discovers plugins via registry (populated by `__init_subclass__`). This gives: type safety (ABC), zero-config registration, loose coupling (manager depends on abstraction).

---

## Hands-On Exercise
1. Build a shape hierarchy with ABC (Circle, Rectangle, Triangle) with area/perimeter
2. Create a mixin-based system: `LoggableMixin`, `CachableMixin`, `ValidatableMixin`
3. Implement a plugin architecture using `__init_subclass__` auto-registration
4. Refactor a deep inheritance hierarchy into composition pattern
