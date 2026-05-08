# Day 09: Inheritance, Abstract Classes & Interfaces

## 🎯 What You'll Learn

- How single inheritance works in Dart with `extends` and how to call `super` constructors
- Method overriding with `@override` and calling `super.method()` to extend parent behavior
- Abstract classes — declaring them with `abstract class`, defining abstract methods, and why they cannot be instantiated
- Implicit interfaces — how every Dart class automatically defines an interface
- The `implements` keyword and the obligation to implement every member of an interface
- The key differences between `extends` and `implements` (and when to choose each)
- Type checking with `is` and safe casting with `as`
- The `covariant` keyword for narrowing parameter types in overrides
- Polymorphism in Dart and how it enables flexible, extensible designs
- A brief comparison of abstract class vs interface vs mixin to set up Day 10

---

## 📚 Core Concepts

### `extends` — Single Inheritance

Dart supports **single inheritance**: a class can extend exactly one other class using the `extends` keyword. The subclass inherits all non-private instance variables and methods from the superclass. Private members (names starting with `_`) are not inherited across library boundaries.

```dart
class Animal {
  final String name;
  Animal(this.name);
  void breathe() => print('$name breathes');
}

class Dog extends Animal {
  Dog(super.name); // super-parameter shorthand (Dart 2.17+)
}
```

When a subclass declares a constructor, it must initialize the superclass. The idiomatic way in Dart 2.17+ is the **super-parameter** shorthand (`super.name`), which forwards the parameter directly to the matching superclass constructor. For older-style code you use an initializer list: `Dog(String name) : super(name)`.

If the superclass has a **named constructor**, the subclass must call it explicitly:

```dart
class Animal {
  final String name;
  Animal.named(this.name);
}

class Cat extends Animal {
  Cat(String name) : super.named(name);
}
```

### Method Overriding with `@override`

A subclass can replace a superclass method by declaring a method with the same name and compatible signature. Annotate it with `@override` — the analyzer will report an error if no matching member exists in the supertype, turning silent typos into compile-time failures.

```dart
class Animal {
  void speak() => print('...');
}

class Dog extends Animal {
  @override
  void speak() => print('Woof!');
}
```

To **extend** rather than replace the parent behavior, call `super.method()` inside the override:

```dart
class LoggingDog extends Dog {
  @override
  void speak() {
    print('[LOG] Dog is about to speak');
    super.speak(); // delegates to Dog.speak()
  }
}
```

### Abstract Classes

An **abstract class** is declared with the `abstract` keyword. It serves as a blueprint that cannot be instantiated directly — you must subclass it and provide concrete implementations of any abstract methods.

An **abstract method** has no body; it ends with a semicolon. Concrete subclasses are required to implement every abstract method, or they must themselves be declared abstract.

```dart
abstract class Shape {
  double get area;          // abstract getter — no body
  double get perimeter;     // abstract getter — no body
  void describe() {         // concrete method — subclasses inherit this
    print('I am a ${runtimeType} with area ${area.toStringAsFixed(2)}');
  }
}
```

Abstract classes can have constructors, concrete methods, and fields — they are not limited to pure declarations. This makes them more powerful than a bare interface when you want to share implementation alongside the contract.

### Implicit Interfaces — Every Class Is an Interface

In Dart, **every class implicitly defines an interface** consisting of all its public instance members (methods, getters, setters, and fields). You do not need a separate `interface` keyword to declare one. This is called an **implicit interface**.

This design means any class can be used as a type contract without the author having to anticipate it. The interface of a class is the set of public members that callers can rely on.

### `implements` — Implementing an Interface

Use `implements` to declare that a class satisfies the contract of another class (or multiple classes). When you `implement` a class, you must provide a concrete implementation of **every** public member — you inherit nothing. This is the critical difference from `extends`.

```dart
class Printable {
  void printInfo() => print('Printable');
}

class Report implements Printable {
  @override
  void printInfo() => print('Report details'); // must implement — nothing is inherited
}
```

A class can implement multiple interfaces, separated by commas:

```dart
class FancyReport implements Printable, Serializable { ... }
```

### `extends` vs `implements` — The Core Distinction

| | `extends` | `implements` |
|---|---|---|
| Inherits implementation | ✅ Yes | ❌ No |
| Inherits fields | ✅ Yes | ❌ No (must redeclare) |
| Max supertypes | 1 | Unlimited |
| Must override abstract members | ✅ Yes | ✅ Yes (all members) |
| Use when | Sharing code + IS-A relationship | Satisfying a contract only |

Choose `extends` when the subclass genuinely IS-A version of the parent and benefits from inherited code. Choose `implements` when you only care about the contract — for example, when you want two unrelated classes to be interchangeable through a common type.

### `is` and `as` — Type Checking and Casting

The `is` operator tests whether an object is an instance of a given type at runtime. It also triggers **type promotion** — inside the `if` block, the variable is automatically treated as the narrower type:

```dart
void describe(Object obj) {
  if (obj is String) {
    print(obj.toUpperCase()); // obj is promoted to String here
  }
}
```

The `as` operator performs an **explicit cast**. If the object is not actually of that type, it throws a `TypeError` at runtime. Use it only when you are certain of the type — prefer `is` + promotion for safe code:

```dart
final Animal a = Dog('Rex');
final Dog d = a as Dog; // safe here, but throws if a is not a Dog
```

### The `covariant` Keyword

Dart's type system normally requires that overridden method parameters be the same type or a supertype (contravariance). The `covariant` keyword relaxes this rule, allowing a subclass to narrow a parameter type to a subtype. This is useful in hierarchies where each level works with a more specific type:

```dart
class Animal {
  void eat(covariant Animal food) { ... }
}

class Dog extends Animal {
  @override
  void eat(Dog food) { ... } // narrowed to Dog — allowed because of covariant
}
```

Use `covariant` sparingly — it trades compile-time safety for flexibility and can cause runtime `TypeError` if the wrong type is passed through a supertype reference.

### Polymorphism in Dart

Polymorphism means a supertype reference can hold any subtype instance, and the correct method is dispatched at runtime. Dart uses **single dispatch** — the method called depends on the runtime type of the receiver:

```dart
List<Shape> shapes = [Circle(5), Rectangle(3, 4)];
for (final s in shapes) {
  s.describe(); // calls Circle.describe or Rectangle.describe at runtime
}
```

This is the foundation of extensible design: code that works with `Shape` automatically works with any future subclass.

### Abstract Class vs Interface vs Mixin — Brief Comparison

| | Abstract Class | Implicit Interface | Mixin |
|---|---|---|---|
| Keyword | `abstract class` | any `class` | `mixin` |
| Used with | `extends` | `implements` | `with` |
| Shares implementation | ✅ Yes | ❌ No | ✅ Yes |
| Can have constructor | ✅ Yes | ✅ Yes | ❌ No |
| Multiple use | ❌ One only | ✅ Many | ✅ Many |

Use an **abstract class** when you want to share code and enforce a contract. Use an **interface** (`implements`) when you only need the contract and want to allow unrelated classes to satisfy it. Use a **mixin** when you want to share behavior across classes that don't share a common ancestor. Day 10 covers mixins in depth.

---

## 💻 Code Examples

### Example 1: `extends`, `super` Constructor, Method Override with `@override`

```dart
// ── Base class ─────────────────────────────────────────────────────────────
class Vehicle {
  final String make;
  final String model;
  int _speed = 0; // private backing field

  Vehicle(this.make, this.model);

  // Named constructor — subclasses can forward to this
  Vehicle.withSpeed(this.make, this.model, int initialSpeed)
      : _speed = initialSpeed;

  int get speed => _speed;

  void accelerate(int amount) {
    _speed += amount;
    print('$make $model accelerates to $_speed km/h');
  }

  void brake(int amount) {
    _speed = (_speed - amount).clamp(0, double.maxFinite.toInt());
    print('$make $model slows to $_speed km/h');
  }

  @override
  String toString() => '$make $model @ $_speed km/h';
}

// ── Subclass using super-parameter shorthand (Dart 2.17+) ──────────────────
class ElectricVehicle extends Vehicle {
  final int batteryCapacityKwh;

  // super.make and super.model forward to Vehicle(this.make, this.model)
  ElectricVehicle(super.make, super.model, this.batteryCapacityKwh);

  // Override accelerate to add regenerative braking note
  @override
  void accelerate(int amount) {
    super.accelerate(amount); // call parent implementation first
    print('  ↳ drawing from ${batteryCapacityKwh}kWh battery');
  }

  // New method specific to EVs
  void chargeTo(int percent) =>
      print('$make $model charging to $percent%');
}

// ── Further subclass ───────────────────────────────────────────────────────
class SportsCar extends Vehicle {
  final int horsepower;

  SportsCar(super.make, super.model, this.horsepower);

  @override
  void accelerate(int amount) {
    // Sports cars accelerate faster — multiply the amount
    super.accelerate(amount * 2);
    print('  ↳ $horsepower HP engine roars');
  }
}

void main() {
  final ev = ElectricVehicle('Tesla', 'Model 3', 75);
  ev.accelerate(30);
  // Tesla Model 3 accelerates to 30 km/h
  //   ↳ drawing from 75kWh battery

  final sc = SportsCar('Ferrari', '488', 660);
  sc.accelerate(50);
  // Ferrari 488 accelerates to 100 km/h  (50 * 2)
  //   ↳ 660 HP engine roars

  print(ev); // Tesla Model 3 @ 30 km/h
}
```

### Example 2: Abstract Class with Abstract Methods and Concrete Subclasses

```dart
import 'dart:math' as math;

// ── Abstract base class ────────────────────────────────────────────────────
abstract class Shape {
  final String color;

  // Abstract classes CAN have constructors — used by subclasses via super()
  const Shape({this.color = 'black'});

  // Abstract getters — no body, subclasses MUST implement
  double get area;
  double get perimeter;

  // Concrete method — shared by all subclasses, no override needed
  void describe() {
    print(
      '${runtimeType}($color): '
      'area=${area.toStringAsFixed(2)}, '
      'perimeter=${perimeter.toStringAsFixed(2)}',
    );
  }

  // Abstract method — subclasses decide how to scale themselves
  Shape scale(double factor);
}

// ── Concrete subclass 1 ────────────────────────────────────────────────────
class Circle extends Shape {
  final double radius;

  const Circle(this.radius, {super.color});

  @override
  double get area => math.pi * radius * radius;

  @override
  double get perimeter => 2 * math.pi * radius;

  @override
  Circle scale(double factor) => Circle(radius * factor, color: color);

  @override
  String toString() => 'Circle(r=$radius, color=$color)';
}

// ── Concrete subclass 2 ────────────────────────────────────────────────────
class Rectangle extends Shape {
  final double width;
  final double height;

  const Rectangle(this.width, this.height, {super.color});

  @override
  double get area => width * height;

  @override
  double get perimeter => 2 * (width + height);

  @override
  Rectangle scale(double factor) =>
      Rectangle(width * factor, height * factor, color: color);

  @override
  String toString() => 'Rectangle(${width}x$height, color=$color)';
}

// ── Concrete subclass 3 ────────────────────────────────────────────────────
class Triangle extends Shape {
  final double a; // side lengths
  final double b;
  final double c;

  const Triangle(this.a, this.b, this.c, {super.color});

  @override
  double get perimeter => a + b + c;

  @override
  double get area {
    // Heron's formula
    final s = perimeter / 2;
    return math.sqrt(s * (s - a) * (s - b) * (s - c));
  }

  @override
  Triangle scale(double factor) =>
      Triangle(a * factor, b * factor, c * factor, color: color);
}

void main() {
  // Cannot instantiate an abstract class:
  // final s = Shape(); // ← compile error: Abstract classes can't be instantiated

  final shapes = <Shape>[
    Circle(5, color: 'red'),
    Rectangle(4, 6, color: 'blue'),
    Triangle(3, 4, 5, color: 'green'),
  ];

  for (final shape in shapes) {
    shape.describe();
  }
  // Circle(red): area=78.54, perimeter=31.42
  // Rectangle(blue): area=24.00, perimeter=20.00
  // Triangle(green): area=6.00, perimeter=12.00

  // Polymorphic scale — each subclass returns its own concrete type
  final scaled = shapes.map((s) => s.scale(2)).toList();
  for (final s in scaled) {
    print(s);
  }
}
```

### Example 3: Implicit Interfaces with `implements`, `is`/`as` Operators, and Polymorphism

```dart
// ── Two unrelated classes that each define an implicit interface ───────────

class Logger {
  final String tag;
  Logger(this.tag);

  void log(String message) => print('[$tag] $message');
  void warn(String message) => print('[$tag] ⚠ $message');
}

class Serializable {
  Map<String, dynamic> toJson() => {};
  String toJsonString() => toJson().toString();
}

// ── A class that implements BOTH interfaces ────────────────────────────────
// It inherits NOTHING — must provide its own implementation of every member.
class AuditRecord implements Logger, Serializable {
  final String _tag;
  final String event;
  final DateTime timestamp;

  AuditRecord(this.event, {String tag = 'AUDIT'})
      : _tag = tag,
        timestamp = DateTime.now();

  // ── Logger interface ─────────────────────────────────────────────────────
  @override
  String get tag => _tag;

  @override
  void log(String message) => print('[$_tag][${timestamp.toIso8601String()}] $message');

  @override
  void warn(String message) => print('[$_tag] ⚠ $message');

  // ── Serializable interface ───────────────────────────────────────────────
  @override
  Map<String, dynamic> toJson() => {
        'event': event,
        'timestamp': timestamp.toIso8601String(),
        'tag': _tag,
      };

  @override
  String toJsonString() => toJson().entries
      .map((e) => '"${e.key}":"${e.value}"')
      .join(', ');
}

// ── Polymorphism via interface types ──────────────────────────────────────
void processLogger(Logger logger) {
  // Works with ANY object that implements Logger — Logger, AuditRecord, etc.
  logger.log('Processing started');
  logger.warn('Low memory');
}

void main() {
  final record = AuditRecord('user_login', tag: 'AUTH');

  // AuditRecord satisfies both Logger and Serializable
  processLogger(record); // polymorphic call — AuditRecord.log is dispatched

  print(record.toJsonString());

  // ── is operator — type checking + type promotion ──────────────────────
  final Object obj = record;

  if (obj is Logger) {
    // Inside this block, obj is promoted to Logger — no cast needed
    obj.log('Type check passed');
  }

  if (obj is AuditRecord) {
    // Promoted to AuditRecord — can access AuditRecord-specific members
    print('Event: ${obj.event}');
  }

  // ── as operator — explicit cast ───────────────────────────────────────
  // Use only when you are certain of the runtime type
  final Logger loggerRef = record;
  final AuditRecord downcast = loggerRef as AuditRecord; // safe here
  print('Downcast event: ${downcast.event}');

  // Unsafe cast — throws TypeError at runtime:
  // final Logger plain = Logger('X');
  // final AuditRecord bad = plain as AuditRecord; // ← TypeError

  // ── is! — negative type check ─────────────────────────────────────────
  final items = <Object>[record, Logger('SYS'), 42, 'hello'];
  for (final item in items) {
    if (item is! Logger) {
      print('Not a logger: $item');
    }
  }
  // Not a logger: 42
  // Not a logger: hello

  // ── covariant example ─────────────────────────────────────────────────
  // See the covariant section in Core Concepts for a full explanation.
}
```

---

## ⚠️ Common Pitfalls

1. **Confusing `extends` with `implements` and wondering why nothing is inherited.** When you use `implements`, you get the contract but zero implementation. Every method, getter, and field must be redeclared. A common mistake is writing `class Dog implements Animal` and then being surprised that `Dog` doesn't have `Animal`'s methods. Use `extends` when you want to inherit code; use `implements` when you only need the type contract.

2. **Trying to instantiate an abstract class directly.** `abstract class Shape` cannot be used with `new Shape()` or `Shape()` — the compiler rejects it. Abstract classes exist solely to be subclassed. If you need a default instance, provide a factory constructor that returns a concrete subtype.

3. **Forgetting `@override` and silently creating a new method instead of overriding.** If you misspell a method name (e.g., `tostring()` instead of `toString()`), Dart creates a brand-new method without warning. Adding `@override` turns this into a compile error: "The method 'tostring' isn't defined in a superclass." Always annotate intentional overrides.

4. **Using `as` without checking `is` first.** An unsafe `as` cast throws a `TypeError` at runtime if the object is not of the expected type. Prefer the `is` check + type promotion pattern, which is both safer and more idiomatic. Reserve `as` for situations where you have external guarantees about the type (e.g., after a `whereType<T>()` filter).

5. **Overusing `covariant` without understanding the runtime risk.** Marking a parameter `covariant` tells the compiler to trust you, but Dart still inserts a runtime type check. If a caller passes the wrong subtype through a supertype reference, you get a `TypeError` at runtime rather than a compile error. Use `covariant` only in tightly controlled hierarchies where the narrowed type is always guaranteed.

---

## ❓ Interview Questions

### Q1: What is the difference between `extends` and `implements` in Dart?

**Answer:** `extends` establishes a true inheritance relationship — the subclass inherits all non-private instance members (fields, methods, getters, setters) from the superclass and can override them selectively. Only one class can be extended. `implements` establishes a contract relationship — the implementing class must provide its own concrete implementation of every public member of the interface, inheriting nothing. Multiple interfaces can be implemented simultaneously. Choose `extends` when the subclass IS-A version of the parent and benefits from shared code; choose `implements` when you only need two unrelated classes to be interchangeable through a common type, without sharing implementation.

### Q2: What is an implicit interface in Dart?

**Answer:** In Dart, every class automatically defines an implicit interface consisting of all its public instance members — methods, getters, setters, and fields. There is no separate `interface` keyword; the interface is derived from the class declaration itself. This means any class can be used as a type contract via `implements`, even if the original author never intended it to be used that way. For example, `class Logger { void log(String msg) {} }` implicitly defines an interface with a `log` method, and any class can `implement Logger` as long as it provides a concrete `log` implementation. This design gives Dart great flexibility for dependency injection and testing.

### Q3: What is the difference between an abstract class and an interface in Dart?

**Answer:** An abstract class (declared with `abstract class`) can contain both abstract members (no body) and concrete members (with implementation), and it can have constructors and fields. Subclasses use `extends` and inherit the concrete members. An interface in Dart is the implicit contract defined by any class; it is consumed via `implements`, which requires the implementing class to provide its own implementation of every member — nothing is inherited. The practical difference: use an abstract class when you want to share code and enforce a contract simultaneously (e.g., a `Shape` base with a shared `describe()` method); use `implements` when you only need the contract and want to allow unrelated classes to satisfy it without inheriting any behavior. Dart 3 also introduced the `interface class` modifier to explicitly mark a class as interface-only (cannot be extended, only implemented).

### Q4: How does method overriding work in Dart and what role does `@override` play?

**Answer:** Method overriding occurs when a subclass declares a method with the same name and a compatible signature as a method in its superclass. At runtime, Dart dispatches the call to the most-derived implementation — this is single dispatch polymorphism. The `@override` annotation is not required by the compiler, but it is strongly recommended: if the annotated method does not actually match any member in the supertype, the analyzer reports a compile-time error, catching typos and signature mismatches early. Inside an override, you can call `super.methodName()` to invoke the parent's implementation and extend rather than replace it. The overriding method's parameter types must be the same as or supertypes of the original (contravariance), unless the `covariant` keyword is used to allow narrowing.

### Q5: What is the `covariant` keyword and when would you use it?

**Answer:** `covariant` is a keyword placed on a method parameter (in either the superclass declaration or the override) to tell Dart's type system that subclasses are allowed to narrow the parameter type to a subtype. Normally, Dart enforces that overridden parameters must be the same type or a supertype (to preserve Liskov substitution), but `covariant` relaxes this rule. A typical use case is a hierarchy where each level works with a more specific type — for example, `Animal.eat(covariant Animal food)` allows `Dog.eat(Dog food)` to override it with a narrower type. The trade-off is that the compile-time safety guarantee is weakened: Dart inserts a runtime type check, and passing the wrong subtype through a supertype reference throws a `TypeError` at runtime. Use `covariant` sparingly and only in tightly controlled hierarchies.

---

## 🔑 Key Takeaways

- Dart supports single inheritance via `extends`; the subclass inherits all non-private members and can call `super` to access the parent's constructor or methods.
- `@override` is not mandatory but is strongly recommended — it turns silent typos into compile errors and documents intent clearly.
- Abstract classes cannot be instantiated; they define a contract (abstract members) and optionally share implementation (concrete members).
- Every Dart class implicitly defines an interface; `implements` lets any class satisfy that contract without inheriting any code.
- `extends` inherits implementation; `implements` only inherits the contract — you must implement every member yourself.
- `is` checks type at runtime and promotes the variable inside the branch; `as` performs an explicit cast that throws `TypeError` if wrong.
- `covariant` allows parameter type narrowing in overrides at the cost of a runtime check — use it sparingly.
- Polymorphism in Dart is achieved through single dispatch: the runtime type of the receiver determines which method is called.
- For sharing behavior across unrelated class hierarchies, prefer mixins (Day 10) over deep inheritance chains.

---

## 🔗 Related Topics

- **Previous:** [Day 08 — Classes & Constructors](./Day-08-Classes-Constructors.md)
- **Next:** [Day 10 — Mixins](./Day-10-Mixins.md) — composing behavior across hierarchies without inheritance
- **Day 18:** [Dart 3 Features — Sealed Classes & Class Modifiers](../Week-3-Async-Advanced/Day-18-Dart3-Features.md) — `sealed`, `final`, `base`, and `interface` class modifiers
- **Dart Cheatsheet:** [Inheritance & Interface syntax quick reference](../Cheatsheets/Dart-Cheatsheet.md)
