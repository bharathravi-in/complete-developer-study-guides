#!/usr/bin/env python3
"""Day 9 - OOP Advanced Concepts"""

from abc import ABC, abstractmethod
from typing import List

print("=" * 50)
print("OOP ADVANCED")
print("=" * 50)

# ============================================
# 1. INHERITANCE
# ============================================
print("\n--- 1. INHERITANCE ---")


class Animal:
    """Base class for animals"""
    
    def __init__(self, name: str):
        self.name = name
    
    def speak(self) -> str:
        return "Some sound"
    
    def describe(self) -> str:
        return f"I am {self.name}"


class Dog(Animal):
    """Dog inherits from Animal"""
    
    def __init__(self, name: str, breed: str):
        super().__init__(name)  # Call parent constructor
        self.breed = breed
    
    def speak(self) -> str:
        return "Woof!"
    
    def fetch(self) -> str:
        return f"{self.name} fetches the ball!"


class Cat(Animal):
    """Cat inherits from Animal"""
    
    def speak(self) -> str:
        return "Meow!"
    
    def purr(self) -> str:
        return f"{self.name} purrs contentedly"


dog = Dog("Buddy", "Golden Retriever")
cat = Cat("Whiskers")

print(f"Dog: {dog.describe()}, says {dog.speak()}")
print(f"Cat: {cat.describe()}, says {cat.speak()}")
print(f"Dog breed: {dog.breed}")
print(f"Dog fetch: {dog.fetch()}")


# ============================================
# 2. MULTIPLE INHERITANCE
# ============================================
print("\n--- 2. MULTIPLE INHERITANCE ---")


class Flyable:
    def fly(self) -> str:
        return f"{self.name} is flying!"


class Swimmable:
    def swim(self) -> str:
        return f"{self.name} is swimming!"


class Walkable:
    def walk(self) -> str:
        return f"{self.name} is walking!"


class Duck(Animal, Flyable, Swimmable, Walkable):
    """Duck can do everything!"""
    
    def speak(self) -> str:
        return "Quack!"


class Penguin(Animal, Swimmable, Walkable):
    """Penguin can swim and walk but not fly"""
    
    def speak(self) -> str:
        return "Squawk!"


duck = Duck("Donald")
penguin = Penguin("Pingu")

print(f"\nDuck: {duck.speak()}, {duck.fly()}, {duck.swim()}")
print(f"Penguin: {penguin.speak()}, {penguin.swim()}, {penguin.walk()}")


# ============================================
# 3. METHOD RESOLUTION ORDER (MRO)
# ============================================
print("\n--- 3. METHOD RESOLUTION ORDER (MRO) ---")


class A:
    def method(self):
        return "A"


class B(A):
    def method(self):
        return "B"


class C(A):
    def method(self):
        return "C"


class D(B, C):
    pass


class E(C, B):
    pass


print(f"D.mro(): {[cls.__name__ for cls in D.mro()]}")
print(f"E.mro(): {[cls.__name__ for cls in E.mro()]}")
print(f"D().method(): {D().method()}")  # Returns B
print(f"E().method(): {E().method()}")  # Returns C

# Super with MRO
class Base:
    def __init__(self):
        print("    Base.__init__")


class Mixin1(Base):
    def __init__(self):
        print("    Mixin1.__init__")
        super().__init__()


class Mixin2(Base):
    def __init__(self):
        print("    Mixin2.__init__")
        super().__init__()


class Child(Mixin1, Mixin2):
    def __init__(self):
        print("    Child.__init__")
        super().__init__()


print("\nCreating Child() - MRO chain:")
child = Child()
print(f"  MRO: {[c.__name__ for c in Child.mro()]}")


# ============================================
# 4. ENCAPSULATION
# ============================================
print("\n--- 4. ENCAPSULATION ---")


class BankAccount:
    """Demonstrates encapsulation"""
    
    def __init__(self, owner: str, balance: float = 0):
        self.owner = owner          # Public
        self._balance = balance     # Protected (convention)
        self.__pin = "1234"         # Private (name mangled)
    
    @property
    def balance(self) -> float:
        """Read-only access to balance"""
        return self._balance
    
    def deposit(self, amount: float):
        if amount > 0:
            self._balance += amount
    
    def withdraw(self, amount: float, pin: str) -> bool:
        if pin != self.__pin:
            print("  Invalid PIN!")
            return False
        if amount > self._balance:
            print("  Insufficient funds!")
            return False
        self._balance -= amount
        return True
    
    def _internal_method(self):
        """Protected method - for internal use"""
        pass


account = BankAccount("Alice", 1000)
print(f"Owner: {account.owner}")
print(f"Balance: ${account.balance}")

# Can access protected (but shouldn't from outside)
print(f"_balance (protected): ${account._balance}")

# Cannot directly access private
# print(account.__pin)  # AttributeError

# Name mangling - still accessible (but don't!)
print(f"Name mangled __pin: {account._BankAccount__pin}")


# ============================================
# 5. POLYMORPHISM
# ============================================
print("\n--- 5. POLYMORPHISM ---")


class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass
    
    @abstractmethod
    def perimeter(self) -> float:
        pass


class Rectangle(Shape):
    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height
    
    def area(self) -> float:
        return self.width * self.height
    
    def perimeter(self) -> float:
        return 2 * (self.width + self.height)


class Circle(Shape):
    def __init__(self, radius: float):
        self.radius = radius
    
    def area(self) -> float:
        import math
        return math.pi * self.radius ** 2
    
    def perimeter(self) -> float:
        import math
        return 2 * math.pi * self.radius


class Triangle(Shape):
    def __init__(self, a: float, b: float, c: float):
        self.a, self.b, self.c = a, b, c
    
    def area(self) -> float:
        # Heron's formula
        s = (self.a + self.b + self.c) / 2
        return (s * (s-self.a) * (s-self.b) * (s-self.c)) ** 0.5
    
    def perimeter(self) -> float:
        return self.a + self.b + self.c


# Polymorphic function
def print_shape_info(shape: Shape):
    print(f"  {type(shape).__name__}: Area={shape.area():.2f}, Perimeter={shape.perimeter():.2f}")


shapes: List[Shape] = [
    Rectangle(4, 5),
    Circle(3),
    Triangle(3, 4, 5)
]

print("\nPolymorphic iteration:")
for shape in shapes:
    print_shape_info(shape)


# ============================================
# 6. ABSTRACT BASE CLASSES
# ============================================
print("\n--- 6. ABSTRACT BASE CLASSES ---")


class Database(ABC):
    """Abstract base for database connections"""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection"""
        pass
    
    @abstractmethod
    def execute(self, query: str) -> list:
        """Execute a query"""
        pass
    
    @abstractmethod
    def close(self):
        """Close connection"""
        pass
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, *args):
        self.close()


class PostgreSQL(Database):
    def __init__(self, host: str, port: int = 5432):
        self.host = host
        self.port = port
        self._connected = False
    
    def connect(self) -> bool:
        print(f"  Connecting to PostgreSQL at {self.host}:{self.port}")
        self._connected = True
        return True
    
    def execute(self, query: str) -> list:
        if not self._connected:
            raise RuntimeError("Not connected")
        print(f"  Executing: {query}")
        return []
    
    def close(self):
        print("  Closing PostgreSQL connection")
        self._connected = False


class MongoDB(Database):
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._connected = False
    
    def connect(self) -> bool:
        print(f"  Connecting to MongoDB")
        self._connected = True
        return True
    
    def execute(self, query: str) -> list:
        print(f"  Executing MongoDB query: {query}")
        return []
    
    def close(self):
        print("  Closing MongoDB connection")
        self._connected = False


# Can use any Database implementation
def run_query(db: Database, query: str):
    with db:
        return db.execute(query)


print("\nUsing PostgreSQL:")
pg = PostgreSQL("localhost")
run_query(pg, "SELECT * FROM users")

print("\nUsing MongoDB:")
mongo = MongoDB("mongodb://localhost")
run_query(mongo, "db.users.find()")


# ============================================
# 7. COMPOSITION VS INHERITANCE
# ============================================
print("\n--- 7. COMPOSITION VS INHERITANCE ---")


# Composition: "has-a" relationship
class Engine:
    def start(self):
        return "Engine started"
    
    def stop(self):
        return "Engine stopped"


class Car:
    """Car HAS an engine (composition)"""
    
    def __init__(self, make: str):
        self.make = make
        self.engine = Engine()  # Composition
    
    def start(self):
        return f"{self.make}: {self.engine.start()}"


car = Car("Toyota")
print(f"Composition: {car.start()}")


# Prefer composition over inheritance when:
# - You need to change behavior at runtime
# - Inheritance would create deep hierarchies
# - Relationship is "has-a" not "is-a"


print("\n✅ Day 9 completed!")
