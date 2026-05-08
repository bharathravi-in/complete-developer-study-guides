# Day 21: Design Patterns in Python — Creational, Structural & Behavioral

## Learning Objectives
- Implement essential design patterns in Pythonic style
- Know when to apply each pattern (and when NOT to)
- Use patterns for testable, maintainable code
- Understand Python-specific alternatives (protocols, first-class functions)
- Apply patterns to real-world problems

---

## 1. Creational Patterns (Beginner)

### Singleton

```python
# Pythonic singleton using module-level instance
# (in Python, a module IS a singleton)

# Method 1: Class with __new__
class DatabaseConnection:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, url: str = ""):
        if not hasattr(self, '_initialized'):
            self.url = url
            self._initialized = True

db1 = DatabaseConnection("postgres://localhost/db")
db2 = DatabaseConnection("other://url")
assert db1 is db2  # Same instance
print(db2.url)     # "postgres://localhost/db" (first call's args)


# Method 2 (Pythonic): Just use a module variable
# config.py
_settings = None

def get_settings():
    global _settings
    if _settings is None:
        _settings = load_settings_from_file()
    return _settings
```

### Factory Pattern

```python
from abc import ABC, abstractmethod

class Notification(ABC):
    @abstractmethod
    def send(self, message: str) -> bool: ...

class EmailNotification(Notification):
    def send(self, message: str) -> bool:
        print(f"📧 Email: {message}")
        return True

class SMSNotification(Notification):
    def send(self, message: str) -> bool:
        print(f"📱 SMS: {message}")
        return True

class PushNotification(Notification):
    def send(self, message: str) -> bool:
        print(f"🔔 Push: {message}")
        return True

# Factory function (Pythonic — no need for Factory class)
def create_notification(channel: str) -> Notification:
    factories = {
        "email": EmailNotification,
        "sms": SMSNotification,
        "push": PushNotification,
    }
    if channel not in factories:
        raise ValueError(f"Unknown channel: {channel}")
    return factories[channel]()

# Usage
notifier = create_notification("email")
notifier.send("Hello!")
```

### Builder Pattern

```python
from dataclasses import dataclass, field

@dataclass
class HTTPRequest:
    method: str = "GET"
    url: str = ""
    headers: dict = field(default_factory=dict)
    body: str | None = None
    timeout: int = 30
    retries: int = 0

class RequestBuilder:
    """Fluent builder for complex object construction."""
    
    def __init__(self, url: str):
        self._request = HTTPRequest(url=url)
    
    def method(self, method: str) -> 'RequestBuilder':
        self._request.method = method
        return self
    
    def header(self, key: str, value: str) -> 'RequestBuilder':
        self._request.headers[key] = value
        return self
    
    def body(self, body: str) -> 'RequestBuilder':
        self._request.body = body
        return self
    
    def timeout(self, seconds: int) -> 'RequestBuilder':
        self._request.timeout = seconds
        return self
    
    def build(self) -> HTTPRequest:
        return self._request

# Fluent API
request = (
    RequestBuilder("https://api.example.com/users")
    .method("POST")
    .header("Content-Type", "application/json")
    .header("Authorization", "Bearer token123")
    .body('{"name": "Alice"}')
    .timeout(10)
    .build()
)
```

---

## 2. Structural Patterns (Intermediate)

### Decorator Pattern (not Python decorators!)

```python
from abc import ABC, abstractmethod

class DataSource(ABC):
    @abstractmethod
    def read(self) -> str: ...
    @abstractmethod
    def write(self, data: str): ...

class FileDataSource(DataSource):
    def __init__(self, filename: str):
        self.filename = filename
    
    def read(self) -> str:
        with open(self.filename) as f:
            return f.read()
    
    def write(self, data: str):
        with open(self.filename, 'w') as f:
            f.write(data)

class EncryptionDecorator(DataSource):
    """Adds encryption to any DataSource."""
    def __init__(self, wrapped: DataSource):
        self._wrapped = wrapped
    
    def read(self) -> str:
        data = self._wrapped.read()
        return self._decrypt(data)
    
    def write(self, data: str):
        encrypted = self._encrypt(data)
        self._wrapped.write(encrypted)
    
    def _encrypt(self, data: str) -> str:
        return data[::-1]  # Simple reverse (demo)
    
    def _decrypt(self, data: str) -> str:
        return data[::-1]

class CompressionDecorator(DataSource):
    """Adds compression to any DataSource."""
    def __init__(self, wrapped: DataSource):
        self._wrapped = wrapped
    
    def read(self) -> str:
        import zlib, base64
        data = self._wrapped.read()
        return zlib.decompress(base64.b64decode(data)).decode()
    
    def write(self, data: str):
        import zlib, base64
        compressed = base64.b64encode(zlib.compress(data.encode())).decode()
        self._wrapped.write(compressed)

# Stack decorators
source = CompressionDecorator(EncryptionDecorator(FileDataSource("data.txt")))
source.write("sensitive data")  # Encrypted → Compressed → Written
```

### Repository Pattern

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class Repository(ABC, Generic[T]):
    """Abstract repository — separates data access from business logic."""
    
    @abstractmethod
    def get(self, id: int) -> Optional[T]: ...
    
    @abstractmethod
    def get_all(self) -> list[T]: ...
    
    @abstractmethod
    def create(self, entity: T) -> T: ...
    
    @abstractmethod
    def update(self, entity: T) -> T: ...
    
    @abstractmethod
    def delete(self, id: int) -> bool: ...

class InMemoryUserRepository(Repository['User']):
    """For testing — no real database."""
    def __init__(self):
        self._store: dict[int, 'User'] = {}
        self._next_id = 1
    
    def get(self, id: int) -> Optional['User']:
        return self._store.get(id)
    
    def get_all(self) -> list['User']:
        return list(self._store.values())
    
    def create(self, entity: 'User') -> 'User':
        entity.id = self._next_id
        self._store[self._next_id] = entity
        self._next_id += 1
        return entity
    
    def update(self, entity: 'User') -> 'User':
        self._store[entity.id] = entity
        return entity
    
    def delete(self, id: int) -> bool:
        return self._store.pop(id, None) is not None
```

---

## 3. Behavioral Patterns (Advanced)

### Strategy Pattern

```python
from typing import Protocol, Callable

# Using Protocol (most Pythonic — no inheritance needed)
class PricingStrategy(Protocol):
    def calculate(self, base_price: float) -> float: ...

class RegularPricing:
    def calculate(self, base_price: float) -> float:
        return base_price

class PremiumPricing:
    def calculate(self, base_price: float) -> float:
        return base_price * 0.8  # 20% discount

class BulkPricing:
    def __init__(self, quantity: int):
        self.quantity = quantity
    
    def calculate(self, base_price: float) -> float:
        if self.quantity > 100:
            return base_price * 0.5
        elif self.quantity > 10:
            return base_price * 0.7
        return base_price

class Order:
    def __init__(self, items: list, strategy: PricingStrategy):
        self.items = items
        self.strategy = strategy
    
    def total(self) -> float:
        base = sum(item['price'] for item in self.items)
        return self.strategy.calculate(base)

# Even simpler: just use functions as strategies
def apply_pricing(base: float, strategy: Callable[[float], float]) -> float:
    return strategy(base)

regular = lambda p: p
premium = lambda p: p * 0.8
```

### Observer Pattern

```python
from typing import Callable, Any
from collections import defaultdict

class EventBus:
    """Publish-subscribe event system."""
    
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
    
    def subscribe(self, event: str, callback: Callable) -> Callable:
        self._subscribers[event].append(callback)
        return callback  # Allows use as decorator
    
    def unsubscribe(self, event: str, callback: Callable):
        self._subscribers[event].remove(callback)
    
    def publish(self, event: str, **data):
        for callback in self._subscribers[event]:
            callback(**data)

# Usage
bus = EventBus()

@bus.subscribe("user_created")
def send_welcome_email(user_id: int, email: str, **kwargs):
    print(f"Welcome email sent to {email}")

@bus.subscribe("user_created")
def init_user_settings(user_id: int, **kwargs):
    print(f"Settings initialized for user {user_id}")

# Trigger event
bus.publish("user_created", user_id=1, email="alice@example.com")
```

### Dependency Injection

```python
from dataclasses import dataclass
from typing import Protocol

class Logger(Protocol):
    def log(self, message: str) -> None: ...

class EmailService(Protocol):
    def send(self, to: str, subject: str, body: str) -> bool: ...

# Production implementations
class FileLogger:
    def log(self, message: str):
        with open("app.log", "a") as f:
            f.write(f"{message}\n")

class SMTPEmailService:
    def send(self, to: str, subject: str, body: str) -> bool:
        # Real SMTP logic
        return True

# Test implementations
class MockLogger:
    def __init__(self):
        self.messages = []
    def log(self, message: str):
        self.messages.append(message)

class MockEmailService:
    def __init__(self):
        self.sent = []
    def send(self, to: str, subject: str, body: str) -> bool:
        self.sent.append((to, subject, body))
        return True

# Service with injected dependencies
@dataclass
class UserService:
    logger: Logger
    email_service: EmailService
    
    def register(self, name: str, email: str):
        self.logger.log(f"Registering {name}")
        self.email_service.send(email, "Welcome!", f"Hi {name}")

# Production
service = UserService(logger=FileLogger(), email_service=SMTPEmailService())

# Testing — inject mocks!
mock_logger = MockLogger()
mock_email = MockEmailService()
test_service = UserService(logger=mock_logger, email_service=mock_email)
test_service.register("Alice", "alice@test.com")
assert len(mock_email.sent) == 1
```

---

## Interview Questions

### Beginner
1. **What are design patterns and why use them?** Proven, reusable solutions to common software design problems. Benefits: shared vocabulary (say "observer pattern" and everyone understands), battle-tested approaches, more maintainable/testable code. In Python, many patterns are simplified by first-class functions, duck typing, and built-in features (decorators, context managers are patterns themselves).

2. **Explain the Singleton pattern and its Python alternatives.** Singleton ensures only one instance exists. In Python: (1) module-level variable (module IS a singleton), (2) `__new__` override, (3) metaclass. Pythonic alternative: just use a module with functions and module-level state. Singletons make testing harder (global state). Prefer dependency injection for testability.

3. **What's the Factory pattern in simple terms?** Factory creates objects without specifying exact class. Caller says "give me a notification" — factory decides which type based on input. In Python: often just a function (or dict mapping) that returns the right class instance. Avoids long if/elif chains for object creation. Follows Open/Closed principle.

### Intermediate
4. **Compare Strategy pattern implementation in Python vs Java.** Java: needs interface + multiple classes. Python: just pass a function! First-class functions ARE the strategy. For stateful strategies: use any object with the right method (duck typing, no interface needed). Protocol provides optional type checking. Python makes many GoF patterns trivial.

5. **When would you use the Observer pattern vs simple callbacks?** Observer: multiple subscribers to same event, loose coupling, event bus for decoupled modules. Callbacks: single handler, tight coupling is acceptable, simpler code. Use Observer when: new handlers should be addable without modifying the publisher, or when multiple systems need to react to the same event.

6. **Explain Dependency Injection without a framework.** DI means: pass dependencies as constructor/method arguments instead of creating them internally. In Python: just pass objects in `__init__`. No framework needed! Benefits: swap implementations (real vs mock for testing), explicit dependencies (visible in constructor), follows Dependency Inversion Principle. Testing becomes trivial.

### Advanced
7. **Which GoF patterns are unnecessary in Python and why?** Iterator: built into the language (for-loops, `__iter__`). Command: just use first-class functions or lambdas. Strategy: pass functions directly. Singleton: use modules. Template Method: use default arguments or mixins. State: use dictionaries mapping states to handlers. Python's dynamism eliminates ceremony that patterns address in static languages.

8. **Design a plugin system using design patterns.** Combine: Factory (create plugins by name), Observer (plugins subscribe to events), Strategy (plugins provide alternate implementations), Registry (auto-register via `__init_subclass__`). Interface: ABC or Protocol for plugin contract. Discovery: `importlib` to load from directory. Configuration: YAML/JSON specifies which plugins to activate.

9. **How do you choose between inheritance and composition for code reuse?** Inheritance: true IS-A relationships (rare), framework requires it (ABC), need polymorphism. Composition: HAS-A relationships (most cases), want flexibility to change behavior at runtime, avoid coupling. Python-specific: mixins (multiple inheritance) bridge the gap — add behavior without deep hierarchies. Rule: compose first, inherit when necessary.

---

## Hands-On Exercise
1. Implement a notification system using Strategy + Factory patterns
2. Build an event-driven system with Observer (EventBus) pattern
3. Create a data pipeline using Builder pattern (fluent API)
4. Refactor a class with many if/elif into Strategy pattern
5. Implement Repository pattern with in-memory and SQLite backends
