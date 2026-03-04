# Day 2: OOP & Classes in Python

## Why OOP Matters for AI Engineering
- Flask uses classes (Blueprints, Models)
- SQLAlchemy models are classes
- Custom exception classes
- Service layers in clean architecture
- LangChain uses class-based chains

---

## 1. Classes Basics

```python
# JS equivalent:
# class User {
#   constructor(name, age) {
#     this.name = name;
#     this.age = age;
#   }
# }

class User:
    """A user in the system."""
    
    # Class variable (shared across all instances, like static in JS)
    platform = "AI Platform"
    
    def __init__(self, name: str, age: int):
        """Constructor (like constructor() in JS)."""
        # Instance variables (like this.x in JS)
        self.name = name
        self.age = age
        self._email = None  # "private" by convention (single underscore)
        self.__secret = "hidden"  # Name mangling (double underscore)
    
    def greet(self) -> str:
        """Instance method (self = this in JS)."""
        return f"Hi, I'm {self.name}, age {self.age}"
    
    def __str__(self) -> str:
        """String representation (like toString() in JS)."""
        return f"User({self.name}, {self.age})"
    
    def __repr__(self) -> str:
        """Developer representation (for debugging)."""
        return f"User(name='{self.name}', age={self.age})"


# Creating instances
user = User("Bharath", 30)
print(user.greet())       # Hi, I'm Bharath, age 30
print(user.platform)      # AI Platform
print(str(user))          # User(Bharath, 30)
```

## 2. Properties (Getters/Setters)

```python
class User:
    def __init__(self, name: str, email: str):
        self.name = name
        self._email = email  # "protected"
    
    @property
    def email(self) -> str:
        """Getter - access like an attribute, not a method."""
        return self._email
    
    @email.setter
    def email(self, value: str) -> None:
        """Setter with validation."""
        if "@" not in value:
            raise ValueError("Invalid email")
        self._email = value
    
    @property
    def display_name(self) -> str:
        """Computed property (like a getter in JS)."""
        return f"{self.name} <{self._email}>"


user = User("Bharath", "bharath@example.com")
print(user.email)           # bharath@example.com (calls getter)
user.email = "new@email.com"  # calls setter
print(user.display_name)    # Bharath <new@email.com>
```

## 3. Inheritance

```python
class BaseModel:
    """Base class for all models."""
    
    def __init__(self, id: int):
        self.id = id
        self.created_at = "2024-01-01"
    
    def to_dict(self) -> dict:
        return {"id": self.id, "created_at": self.created_at}


class User(BaseModel):
    """User inherits from BaseModel."""
    
    def __init__(self, id: int, name: str, role: str):
        super().__init__(id)  # Call parent constructor
        self.name = name
        self.role = role
    
    def to_dict(self) -> dict:
        """Override parent method."""
        base = super().to_dict()  # Get parent's dict
        base.update({"name": self.name, "role": self.role})
        return base


class AdminUser(User):
    """Multi-level inheritance."""
    
    def __init__(self, id: int, name: str, permissions: list):
        super().__init__(id, name, role="admin")
        self.permissions = permissions
    
    def has_permission(self, perm: str) -> bool:
        return perm in self.permissions


# Usage
admin = AdminUser(1, "Bharath", ["read", "write", "delete"])
print(admin.to_dict())
# {'id': 1, 'created_at': '2024-01-01', 'name': 'Bharath', 'role': 'admin'}
print(admin.has_permission("write"))  # True
print(isinstance(admin, User))       # True
print(isinstance(admin, BaseModel))  # True
```

## 4. Abstract Classes (Like Interfaces in TypeScript)

```python
from abc import ABC, abstractmethod

class EmbeddingProvider(ABC):
    """Abstract base class - cannot be instantiated directly.
    Like an interface in TypeScript.
    """
    
    @abstractmethod
    def generate_embedding(self, text: str) -> list[float]:
        """Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    def get_dimension(self) -> int:
        """Concrete method - shared by all subclasses."""
        return 1536


class OpenAIEmbedding(EmbeddingProvider):
    """Concrete implementation."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def generate_embedding(self, text: str) -> list[float]:
        # Would call OpenAI API
        return [0.1, 0.2, 0.3]  # simplified
    
    def get_model_name(self) -> str:
        return "text-embedding-ada-002"


class LocalEmbedding(EmbeddingProvider):
    """Another implementation."""
    
    def generate_embedding(self, text: str) -> list[float]:
        # Would use local model
        return [0.4, 0.5, 0.6]
    
    def get_model_name(self) -> str:
        return "all-MiniLM-L6-v2"


# Can't do this:
# provider = EmbeddingProvider()  # TypeError!

# Must use concrete class:
provider = OpenAIEmbedding("sk-xxx")
embedding = provider.generate_embedding("Hello world")
```

## 5. Class Methods & Static Methods

```python
class Document:
    _count = 0  # Class variable
    
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content
        Document._count += 1
    
    def summary(self) -> str:
        """Instance method - needs self (the instance)."""
        return f"{self.title}: {self.content[:50]}..."
    
    @classmethod
    def from_dict(cls, data: dict) -> "Document":
        """Class method - factory pattern.
        cls = the class itself (not an instance).
        Like a static factory method in Java/TS.
        """
        return cls(data["title"], data["content"])
    
    @classmethod
    def get_count(cls) -> int:
        """Access class-level data."""
        return cls._count
    
    @staticmethod
    def is_valid_title(title: str) -> bool:
        """Static method - no access to instance or class.
        Just a utility function namespaced to the class.
        """
        return len(title) > 0 and len(title) <= 200


# Usage
doc = Document("AI Guide", "This is a comprehensive guide to AI...")
doc2 = Document.from_dict({"title": "RAG", "content": "RAG stands for..."})
print(Document.get_count())          # 2
print(Document.is_valid_title(""))   # False
```

## 6. Dataclasses (Modern Python - Use This!)

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class User:
    """Dataclass = auto-generates __init__, __repr__, __eq__.
    Like a TypeScript interface but with implementations.
    """
    name: str
    email: str
    age: int
    role: str = "engineer"  # Default value
    skills: list[str] = field(default_factory=list)  # Mutable default
    id: Optional[int] = None
    
    def is_senior(self) -> bool:
        return self.age > 30 or len(self.skills) > 5


# Auto-generated constructor!
user = User(name="Bharath", email="b@test.com", age=30)
print(user)
# User(name='Bharath', email='b@test.com', age=30, role='engineer', skills=[], id=None)

# Auto-generated equality!
user2 = User(name="Bharath", email="b@test.com", age=30)
print(user == user2)  # True


@dataclass
class EmbeddingResult:
    """Perfect for AI data structures."""
    text: str
    embedding: list[float]
    model: str
    dimensions: int
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)  # Immutable!
class Config:
    """Frozen dataclass = immutable after creation."""
    model_name: str
    temperature: float
    max_tokens: int
    
# config = Config("gpt-4", 0.7, 4096)
# config.temperature = 0.5  # FrozenInstanceError!
```

## 7. Protocols (Duck Typing - Very Pythonic)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Searchable(Protocol):
    """Like a TypeScript interface - structural typing.
    Any class with these methods is considered 'Searchable'.
    No explicit inheritance needed!
    """
    def search(self, query: str) -> list[dict]: ...
    def index(self, document: dict) -> bool: ...


class QdrantSearch:
    """Implements Searchable without inheriting."""
    
    def search(self, query: str) -> list[dict]:
        return [{"text": "result", "score": 0.95}]
    
    def index(self, document: dict) -> bool:
        return True


class ElasticSearch:
    """Also implements Searchable."""
    
    def search(self, query: str) -> list[dict]:
        return [{"text": "elastic result", "score": 0.88}]
    
    def index(self, document: dict) -> bool:
        return True


def perform_search(engine: Searchable, query: str) -> list[dict]:
    """Works with any 'Searchable' object."""
    return engine.search(query)

# Both work!
qdrant = QdrantSearch()
elastic = ElasticSearch()
print(isinstance(qdrant, Searchable))  # True (structural check)
perform_search(qdrant, "AI")
perform_search(elastic, "AI")
```

## 8. Mixins Pattern

```python
class TimestampMixin:
    """Add timestamp behavior to any class."""
    
    def set_timestamps(self):
        from datetime import datetime
        now = datetime.utcnow().isoformat()
        if not hasattr(self, "created_at"):
            self.created_at = now
        self.updated_at = now


class SerializableMixin:
    """Add serialization to any class."""
    
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() 
                if not k.startswith("_")}
    
    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict())


class User(TimestampMixin, SerializableMixin):
    """User with timestamp and serialization capabilities."""
    
    def __init__(self, name: str, email: str):
        self.name = name
        self.email = email
        self.set_timestamps()


user = User("Bharath", "b@test.com")
print(user.to_dict())
# {'name': 'Bharath', 'email': 'b@test.com', 'created_at': '...', 'updated_at': '...'}
print(user.to_json())
```

## 9. Enums

```python
from enum import Enum, auto

class UserRole(Enum):
    """Like TypeScript enum."""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class Status(Enum):
    PENDING = auto()   # 1
    ACTIVE = auto()    # 2
    INACTIVE = auto()  # 3

# Usage
role = UserRole.ADMIN
print(role.value)        # "admin"
print(role.name)         # "ADMIN"
print(role == UserRole.ADMIN)  # True

# In pattern matching (Python 3.10+)
match role:
    case UserRole.ADMIN:
        print("Full access")
    case UserRole.EDITOR:
        print("Edit access")
    case UserRole.VIEWER:
        print("Read only")
```

---

## Exercises

### Exercise 1: Build an Embedding Service Class Hierarchy
```python
# Create:
# 1. Abstract class `BaseEmbeddingService` with:
#    - abstract method: embed(text: str) -> list[float]
#    - abstract method: embed_batch(texts: list[str]) -> list[list[float]]
#    - concrete method: similarity(vec1, vec2) -> float (cosine similarity)
#
# 2. `MockEmbeddingService(BaseEmbeddingService)` that returns random vectors
# 3. `CachedEmbeddingService` that wraps another service and caches results

# TODO: Implement
```

### Exercise 2: Build a Document Model with Dataclasses
```python
# Create dataclasses for:
# 1. Document (id, title, content, metadata, chunks)
# 2. Chunk (id, text, embedding, document_id)
# 3. SearchResult (chunk, score, metadata)
# 
# Add methods:
# - Document.chunk_text(chunk_size=500) -> list[Chunk]
# - SearchResult.is_relevant(threshold=0.7) -> bool

# TODO: Implement
```

### Exercise 3: Build a Plugin System
```python
# Create a plugin system where:
# 1. Base class `Plugin` with abstract method `execute(data: dict) -> dict`
# 2. `PluginManager` class that:
#    - Registers plugins
#    - Executes plugins in order
#    - Handles plugin errors gracefully
# 3. Create 3 sample plugins: LoggingPlugin, ValidationPlugin, TransformPlugin

# TODO: Implement
```

---

## Key Takeaways for Day 2
1. `self` = `this` in JavaScript
2. `__init__` = constructor
3. Use **@dataclass** for data-holding classes (most AI data structures)
4. Use **ABC** for interfaces/contracts
5. **@property** for computed values and validation
6. **@classmethod** for factory methods
7. **Protocols** for duck typing (structural typing like TS)
8. **No access modifiers** — use `_single_underscore` convention for private
