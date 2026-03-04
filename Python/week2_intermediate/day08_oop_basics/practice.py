#!/usr/bin/env python3
"""Day 8 - Object-Oriented Programming Basics"""

from dataclasses import dataclass
from typing import List, Optional

print("=" * 50)
print("OOP BASICS")
print("=" * 50)

# ============================================
# 1. BASIC CLASS
# ============================================
print("\n--- 1. BASIC CLASS ---")


class Dog:
    """A simple Dog class"""
    
    # Class variable (shared by all instances)
    species = "Canis familiaris"
    count = 0
    
    def __init__(self, name: str, age: int):
        """Initialize instance"""
        # Instance variables (unique to each instance)
        self.name = name
        self.age = age
        Dog.count += 1
    
    def bark(self) -> str:
        """Instance method"""
        return f"{self.name} says Woof!"
    
    def description(self) -> str:
        return f"{self.name} is {self.age} years old"


# Create instances
dog1 = Dog("Buddy", 3)
dog2 = Dog("Max", 5)

print(f"Dog 1: {dog1.description()}")
print(f"Dog 2: {dog2.description()}")
print(f"Species (class var): {Dog.species}")
print(f"Total dogs: {Dog.count}")


# ============================================
# 2. CLASS VS INSTANCE VARIABLES
# ============================================
print("\n--- 2. CLASS VS INSTANCE VARIABLES ---")


class Counter:
    total = 0  # Class variable
    
    def __init__(self):
        Counter.total += 1
        self.count = 0  # Instance variable
    
    def increment(self):
        self.count += 1


c1 = Counter()
c2 = Counter()

c1.increment()
c1.increment()
c2.increment()

print(f"c1.count (instance): {c1.count}")
print(f"c2.count (instance): {c2.count}")
print(f"Counter.total (class): {Counter.total}")


# ============================================
# 3. INSTANCE, CLASS, AND STATIC METHODS
# ============================================
print("\n--- 3. METHOD TYPES ---")


class Pizza:
    """Demonstrates different method types"""
    
    def __init__(self, ingredients: List[str]):
        self.ingredients = ingredients
    
    # Instance method - accesses instance via self
    def describe(self) -> str:
        return f"Pizza with {', '.join(self.ingredients)}"
    
    # Class method - accesses class via cls
    @classmethod
    def margherita(cls) -> "Pizza":
        """Factory method to create Margherita"""
        return cls(["mozzarella", "tomatoes", "basil"])
    
    @classmethod
    def pepperoni(cls) -> "Pizza":
        """Factory method to create Pepperoni"""
        return cls(["mozzarella", "pepperoni"])
    
    # Static method - no access to instance or class
    @staticmethod
    def calculate_area(radius: float) -> float:
        """Calculate pizza area"""
        import math
        return math.pi * radius ** 2


# Using different method types
custom = Pizza(["cheese", "mushrooms", "olives"])
print(f"Custom: {custom.describe()}")

margh = Pizza.margherita()  # Factory method
print(f"Margherita: {margh.describe()}")

area = Pizza.calculate_area(10)  # Static method
print(f"Area (r=10): {area:.2f}")


# ============================================
# 4. DUNDER METHODS (MAGIC METHODS)
# ============================================
print("\n--- 4. DUNDER METHODS ---")


class Vector:
    """2D Vector with dunder methods"""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Vector({self.x}, {self.y})"
    
    def __str__(self) -> str:
        """User-friendly representation"""
        return f"({self.x}, {self.y})"
    
    def __eq__(self, other) -> bool:
        """Equality comparison"""
        if not isinstance(other, Vector):
            return NotImplemented
        return self.x == other.x and self.y == other.y
    
    def __hash__(self) -> int:
        """Make hashable for dict keys"""
        return hash((self.x, self.y))
    
    def __add__(self, other) -> "Vector":
        """Add two vectors"""
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other) -> "Vector":
        """Subtract vectors"""
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> "Vector":
        """Scalar multiplication"""
        return Vector(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar: float) -> "Vector":
        """Right multiplication (scalar * vector)"""
        return self.__mul__(scalar)
    
    def __abs__(self) -> float:
        """Vector magnitude"""
        return (self.x ** 2 + self.y ** 2) ** 0.5
    
    def __bool__(self) -> bool:
        """Truth value (non-zero vector)"""
        return self.x != 0 or self.y != 0
    
    def __len__(self) -> int:
        """Number of dimensions"""
        return 2
    
    def __getitem__(self, index: int) -> float:
        """Index access"""
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        raise IndexError("Vector index out of range")
    
    def __iter__(self):
        """Make iterable"""
        yield self.x
        yield self.y


v1 = Vector(3, 4)
v2 = Vector(1, 2)

print(f"v1 = {v1}")
print(f"v2 = {v2}")
print(f"v1 + v2 = {v1 + v2}")
print(f"v1 - v2 = {v1 - v2}")
print(f"v1 * 2 = {v1 * 2}")
print(f"2 * v1 = {2 * v1}")
print(f"|v1| = {abs(v1)}")
print(f"v1 == Vector(3, 4): {v1 == Vector(3, 4)}")
print(f"v1[0], v1[1] = {v1[0]}, {v1[1]}")
print(f"list(v1) = {list(v1)}")
print(f"bool(Vector(0, 0)) = {bool(Vector(0, 0))}")


# ============================================
# 5. PROPERTY DECORATOR
# ============================================
print("\n--- 5. PROPERTY DECORATOR ---")


class Circle:
    """Circle with computed properties"""
    
    def __init__(self, radius: float):
        self._radius = radius
    
    @property
    def radius(self) -> float:
        """Getter for radius"""
        return self._radius
    
    @radius.setter
    def radius(self, value: float):
        """Setter with validation"""
        if value <= 0:
            raise ValueError("Radius must be positive")
        self._radius = value
    
    @property
    def diameter(self) -> float:
        """Computed property"""
        return self._radius * 2
    
    @property
    def area(self) -> float:
        """Computed property"""
        import math
        return math.pi * self._radius ** 2


circle = Circle(5)
print(f"Radius: {circle.radius}")
print(f"Diameter: {circle.diameter}")
print(f"Area: {circle.area:.2f}")

circle.radius = 10
print(f"New radius: {circle.radius}")


# ============================================
# 6. DATACLASSES
# ============================================
print("\n--- 6. DATACLASSES ---")


@dataclass
class Point:
    """A point in 2D space using dataclass"""
    x: float
    y: float
    label: str = "origin"
    
    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@dataclass(frozen=True)
class ImmutablePoint:
    """Immutable point (can be used as dict key)"""
    x: float
    y: float


p1 = Point(0, 0, "origin")
p2 = Point(3, 4, "destination")

print(f"p1: {p1}")
print(f"p2: {p2}")
print(f"Distance: {p1.distance_to(p2)}")
print(f"p1 == Point(0, 0, 'origin'): {p1 == Point(0, 0, 'origin')}")

# Frozen dataclass
ip = ImmutablePoint(1, 2)
print(f"\nImmutable: {ip}")
# ip.x = 5  # This would raise FrozenInstanceError


# ============================================
# 7. SLOTS
# ============================================
print("\n--- 7. __SLOTS__ ---")


class RegularClass:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class SlottedClass:
    __slots__ = ['x', 'y']
    
    def __init__(self, x, y):
        self.x = x
        self.y = y


import sys

regular = RegularClass(1, 2)
slotted = SlottedClass(1, 2)

print(f"Regular has __dict__: {hasattr(regular, '__dict__')}")
print(f"Slotted has __dict__: {hasattr(slotted, '__dict__')}")
print(f"Regular __dict__: {regular.__dict__}")

# Can add dynamic attributes to regular
regular.z = 3
print(f"Added z to regular: {regular.z}")

# Cannot add to slotted
try:
    slotted.z = 3
except AttributeError as e:
    print(f"Cannot add z to slotted: {e}")


print("\n✅ Day 8 completed!")
