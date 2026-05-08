# Day 08: Classes & Constructors

## 🎯 What You'll Learn

- How to declare classes with instance variables and methods in Dart
- The five constructor types: default, named, factory, redirecting, and `const`
- How initializer lists work and when to use them
- Getters and setters with the `get`/`set` keywords
- The `this` keyword for disambiguation and constructor shorthand
- `static` members — class-level variables and methods
- Overriding `toString()`, `==`, and `hashCode` for value equality
- The `@override` annotation and why it matters
- Cascade notation `..` for fluent method chaining

---

## 📚 Core Concepts

### Class Declaration and Instance Variables

A Dart class groups related data (fields) and behavior (methods) into a single unit. You declare a class with the `class` keyword, followed by the class name in `UpperCamelCase`. Instance variables are declared directly inside the class body — Dart automatically generates a getter for every public field and a setter for every non-`final` public field.

```dart
class Point {
  double x;
  double y;
}
```

Fields can be `final` (set once, at construction time) or `late` (initialized on first access). Dart's sound null safety means every non-nullable field must be initialized before the constructor body runs — either via an initializer list, a default value, or the `this.field` shorthand.

### Default Constructor and Initializer Lists

When you don't declare any constructor, Dart provides a no-argument default constructor. As soon as you declare your own constructor, the implicit default disappears. The most common pattern uses the `this.field` shorthand to assign parameters directly to fields:

```dart
class Point {
  final double x;
  final double y;

  // this.x and this.y assign parameters to fields before the body runs
  Point(this.x, this.y);
}
```

An **initializer list** runs between the parameter list and the constructor body. It is the right place to initialize `final` fields that require a computation, call `assert`, or delegate to a superclass constructor:

```dart
Point.fromJson(Map<String, double> json)
    : x = json['x'] ?? 0.0,   // initializer list
      y = json['y'] ?? 0.0;
```

### Named Constructors

Dart does not support constructor overloading by parameter types, but it does support **named constructors** — additional constructors with a dot-separated name. They are ideal for alternative creation patterns:

```dart
Point.origin() : x = 0.0, y = 0.0;
Point.fromList(List<double> coords) : x = coords[0], y = coords[1];
```

Named constructors make intent explicit and keep the primary constructor clean.

### Factory Constructors

A **factory constructor** uses the `factory` keyword and must return an instance of the class (or a subtype). Unlike regular constructors, it does not automatically create a new object — you control what gets returned. This makes factory constructors ideal for:

- **Caching / singleton patterns**: return an existing instance instead of creating a new one.
- **Subtype dispatch**: inspect arguments and return the appropriate subclass.
- **Complex initialization**: run async-like logic before returning (though the constructor itself must be synchronous).

```dart
factory Point.cached(double x, double y) {
  return _cache.putIfAbsent('$x,$y', () => Point._internal(x, y));
}
```

### Redirecting Constructors

A **redirecting constructor** delegates entirely to another constructor in the same class using `: this(...)`. It has no body:

```dart
Point.zero() : this(0.0, 0.0);   // redirects to Point(double, double)
```

This avoids duplicating initialization logic.

### `const` Constructors

A `const` constructor creates a **compile-time constant** object. Requirements:
1. The class must have only `final` fields.
2. The constructor body must be empty (no body at all).
3. All field initializations must be constant expressions.

When you call `const Point(1, 2)` twice, Dart returns the same canonical instance — saving memory and enabling fast `identical()` checks. Flutter uses `const` constructors extensively to avoid unnecessary widget rebuilds.

### Getters and Setters

Custom getters and setters let you expose computed properties or add validation without changing the call site:

```dart
double get distanceFromOrigin => math.sqrt(x * x + y * y);

set label(String value) {
  if (value.isEmpty) throw ArgumentError('Label cannot be empty');
  _label = value;
}
```

### The `this` Keyword

`this` refers to the current instance. You need it when a local variable or parameter shadows a field name. The `this.field` constructor shorthand is syntactic sugar that assigns the parameter to the field of the same name — it is the idiomatic Dart way to write constructors.

### `static` Members

`static` fields and methods belong to the class itself, not to any instance. They are accessed via the class name (`Point.origin`) and cannot reference `this`. Use `static` for constants, utility methods, and shared state:

```dart
static const double pi = 3.14159;
static Point lerp(Point a, Point b, double t) => Point(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t);
```

### Overriding `toString()`, `==`, and `hashCode`

By default, `toString()` returns something like `Instance of 'Point'`, and `==` uses reference equality. Override them to get meaningful output and value-based equality:

- `toString()` — return a human-readable string.
- `==` — return `true` when two objects represent the same value. Always check `identical` first (fast path), then type, then fields.
- `hashCode` — must be consistent with `==`: if `a == b` then `a.hashCode == b.hashCode`. Use `Object.hash()` (Dart 2.14+) to combine field hashes safely.

The `@override` annotation is not required by the compiler, but it is strongly recommended — it causes a compile error if the method you think you're overriding doesn't actually exist in the superclass, catching typos early.

### Cascade Notation `..`

The cascade operator `..` lets you call multiple methods or set multiple properties on the same object without repeating the variable name:

```dart
final p = Point(1, 2)
  ..scale(2)
  ..translate(dx: 5, dy: 3);
```

The expression evaluates to the original object, not the return value of the last method call. Use `?..` for null-safe cascades.

---

## 💻 Code Examples

### Example 1: Default Constructor, Named Constructor, Initializer List, Getters/Setters

```dart
import 'dart:math' as math;

class Circle {
  // final fields — must be set before the constructor body
  final double radius;
  String _label; // backing field for the label setter

  // Default constructor with this.field shorthand + initializer list
  Circle(this.radius, {String label = 'circle'}) : _label = label {
    // Constructor body runs after the initializer list
    if (radius < 0) throw ArgumentError('Radius must be non-negative');
  }

  // Named constructor — creates a unit circle
  Circle.unit() : this(1.0, label: 'unit circle'); // redirecting

  // Named constructor with initializer list — parses a map
  Circle.fromMap(Map<String, dynamic> map)
      : radius = (map['radius'] as num).toDouble(),
        _label = map['label'] as String? ?? 'circle';

  // Getter — computed property, no backing field needed
  double get area => math.pi * radius * radius;
  double get circumference => 2 * math.pi * radius;

  // Getter/setter pair for the label field
  String get label => _label;
  set label(String value) {
    if (value.trim().isEmpty) throw ArgumentError('Label cannot be empty');
    _label = value.trim();
  }

  @override
  String toString() => 'Circle(radius: $radius, label: $_label)';
}

void main() {
  final c1 = Circle(5.0, label: 'big circle');
  print(c1.area.toStringAsFixed(2));   // 78.54
  print(c1.circumference.toStringAsFixed(2)); // 31.42

  c1.label = 'updated';
  print(c1.label); // updated

  final c2 = Circle.unit();
  print(c2); // Circle(radius: 1.0, label: unit circle)

  final c3 = Circle.fromMap({'radius': 3, 'label': 'medium'});
  print(c3.radius); // 3.0
}
```

### Example 2: Factory Constructor (Singleton / Caching) and `const` Constructor

```dart
// ── Singleton via factory constructor ──────────────────────────────────────
class AppConfig {
  final String apiBaseUrl;
  final int timeoutSeconds;

  // Private named constructor — only callable from within this class
  AppConfig._internal({
    required this.apiBaseUrl,
    required this.timeoutSeconds,
  });

  // The single cached instance
  static AppConfig? _instance;

  // Factory constructor returns the cached instance on subsequent calls
  factory AppConfig({
    String apiBaseUrl = 'https://api.example.com',
    int timeoutSeconds = 30,
  }) {
    // Create once, reuse forever
    _instance ??= AppConfig._internal(
      apiBaseUrl: apiBaseUrl,
      timeoutSeconds: timeoutSeconds,
    );
    return _instance!;
  }
}

// ── const constructor ───────────────────────────────────────────────────────
class ImmutablePoint {
  final double x;
  final double y;

  // const constructor: all fields are final, no constructor body
  const ImmutablePoint(this.x, this.y);

  // Named const constructor
  const ImmutablePoint.origin() : x = 0.0, y = 0.0;
}

void main() {
  // Singleton: both variables point to the same object
  final cfg1 = AppConfig();
  final cfg2 = AppConfig(apiBaseUrl: 'https://other.com'); // ignored after first call
  print(identical(cfg1, cfg2)); // true

  // const objects with the same arguments are canonicalized — same instance
  const p1 = ImmutablePoint(1.0, 2.0);
  const p2 = ImmutablePoint(1.0, 2.0);
  print(identical(p1, p2)); // true  ← compile-time constant canonicalization

  // Non-const call creates a new instance each time
  final p3 = ImmutablePoint(1.0, 2.0);
  final p4 = ImmutablePoint(1.0, 2.0);
  print(identical(p3, p4)); // false ← different heap objects
}
```

### Example 3: `static` Members, `toString`/`==`/`hashCode` Override, Cascade Notation

```dart
import 'dart:math' as math;

class Vector2 {
  final double x;
  final double y;

  const Vector2(this.x, this.y);

  // ── static members ────────────────────────────────────────────────────────
  static const Vector2 zero = Vector2(0, 0);   // class-level constant
  static const Vector2 unitX = Vector2(1, 0);
  static const Vector2 unitY = Vector2(0, 1);

  // Static utility method — no access to `this`
  static double dot(Vector2 a, Vector2 b) => a.x * b.x + a.y * b.y;

  // ── instance methods ──────────────────────────────────────────────────────
  double get magnitude => math.sqrt(x * x + y * y);

  Vector2 operator +(Vector2 other) => Vector2(x + other.x, y + other.y);
  Vector2 operator *(double scalar) => Vector2(x * scalar, y * scalar);

  Vector2 normalized() {
    final m = magnitude;
    if (m == 0) throw StateError('Cannot normalize a zero vector');
    return Vector2(x / m, y / m);
  }

  // ── toString ──────────────────────────────────────────────────────────────
  @override
  String toString() => 'Vector2($x, $y)';

  // ── == and hashCode ───────────────────────────────────────────────────────
  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;   // fast path: same reference
    if (other is! Vector2) return false;        // type check
    return x == other.x && y == other.y;        // field comparison
  }

  // Object.hash combines multiple field hashes safely (Dart 2.14+)
  @override
  int get hashCode => Object.hash(x, y);
}

// ── Mutable builder that demonstrates cascade notation ─────────────────────
class PathBuilder {
  final List<Vector2> _points = [];

  PathBuilder moveTo(double x, double y) {
    _points.add(Vector2(x, y));
    return this; // return self to allow chaining
  }

  PathBuilder lineTo(double x, double y) {
    _points.add(Vector2(x, y));
    return this;
  }

  List<Vector2> build() => List.unmodifiable(_points);
}

void main() {
  // static members accessed via class name
  print(Vector2.zero);          // Vector2(0.0, 0.0)
  print(Vector2.dot(Vector2.unitX, Vector2.unitY)); // 0.0

  // == and hashCode
  final v1 = Vector2(3, 4);
  final v2 = Vector2(3, 4);
  print(v1 == v2);              // true  ← value equality
  print(v1.hashCode == v2.hashCode); // true

  // Cascade notation: call multiple methods on the same PathBuilder instance
  // The expression evaluates to the PathBuilder, not the return of lineTo
  final path = PathBuilder()
    ..moveTo(0, 0)
    ..lineTo(1, 0)
    ..lineTo(1, 1)
    ..lineTo(0, 1);

  print(path.build()); // [Vector2(0.0, 0.0), Vector2(1.0, 0.0), ...]
}
```

---

## ⚠️ Common Pitfalls

1. **Forgetting that declaring any constructor removes the implicit default constructor.** If you add a named constructor like `Point.origin()` but still need `Point()`, you must declare it explicitly — otherwise callers get a compile error.

2. **Using a factory constructor when you need `super` initialization.** Factory constructors cannot use initializer lists or call `super(...)`. If your class extends another and needs to pass arguments up the chain, use a regular constructor with an initializer list instead.

3. **Inconsistent `==` and `hashCode`.** If you override `==` without overriding `hashCode` (or vice versa), objects that compare equal will have different hash codes, breaking `Set` membership and `Map` key lookups in subtle, hard-to-debug ways. Always override both together.

4. **Mutating `static` state carelessly.** A mutable `static` field is effectively global state — it persists across all instances and test runs. Prefer `static const` or `static final` for constants, and be deliberate about mutable statics (e.g., singletons).

5. **Cascade `..` vs method chaining.** The cascade operator returns the *receiver*, not the return value of the last call. If a method returns a different object (e.g., a transformed copy), use regular chaining (`a.transform().scale()`) instead of cascades, or you'll silently discard the return value.

---

## ❓ Interview Questions

### Q1: What is the difference between a factory constructor and a regular constructor in Dart?

**Answer:** A regular constructor always creates a new instance of the class and can use initializer lists and `super()` calls. A factory constructor uses the `factory` keyword and must explicitly return an instance — it can return a cached object, a subtype instance, or the result of any synchronous computation. Because it controls what gets returned, a factory constructor is the idiomatic way to implement singletons, object pools, and subtype dispatch. The trade-off is that factory constructors cannot be `const` and cannot use initializer lists or call `super` directly.

### Q2: What are the requirements for a `const` constructor in Dart?

**Answer:** For a constructor to be `const`, three conditions must hold: (1) every instance field in the class must be declared `final`; (2) the constructor must have an empty body (no `{}` block at all, or an empty one); and (3) all field initializations in the initializer list must be constant expressions — no runtime computations, no calls to non-`const` functions. When these conditions are met, calling `const MyClass(args)` with the same arguments always returns the identical canonical instance, which Dart caches at compile time. This is especially valuable in Flutter, where `const` widgets are skipped during the rebuild phase.

### Q3: What is an initializer list in Dart and when would you use it?

**Answer:** An initializer list is the comma-separated list of assignments that appears between the constructor's parameter list and its body, introduced by a colon (`:`). It runs before the constructor body and before the superclass constructor body. You use it when you need to initialize `final` fields that require a computation (e.g., `radius = value.abs()`), when you need to call `assert` to validate parameters at construction time, or when you need to call a specific `super` constructor. It is also the only place where you can initialize `final` fields that cannot be set via the `this.field` shorthand.

### Q4: How do you correctly override `==` and `hashCode` in Dart?

**Answer:** Override the `==` operator as `bool operator ==(Object other)` — the parameter type must be `Object`, not the class type, to match the superclass signature. Inside, first check `identical(this, other)` as a fast path, then verify `other is YourClass`, then compare all relevant fields. Override `hashCode` as a getter that combines the same fields using `Object.hash(field1, field2, ...)` (Dart 2.14+) or `Object.hashAll([...])` for a variable number of fields. The contract is: if `a == b` then `a.hashCode == b.hashCode`. Violating this breaks `Set` and `Map` behavior. Always annotate both overrides with `@override`.

### Q5: What is the difference between instance methods and static methods?

**Answer:** Instance methods are called on an object and have implicit access to `this`, so they can read and modify instance fields. Static methods are declared with the `static` keyword, belong to the class itself rather than any instance, and have no access to `this` or instance fields. You call static methods via the class name (`MyClass.doSomething()`), not on an instance. Use static methods for utility functions that are logically related to the class but don't need instance state — for example, `Vector2.dot(a, b)` or `DateTime.now()`. Overusing static methods can make code harder to test and mock, so prefer instance methods when the behavior depends on object state.

### Q6 (Bonus): What is the purpose of the `@override` annotation?

**Answer:** `@override` is a metadata annotation that signals to the compiler and readers that the annotated method is intentionally overriding a member from a superclass or interface. While Dart does not require it, omitting it means a typo in the method name (e.g., `tostring()` instead of `toString()`) silently creates a new method rather than overriding the intended one. With `@override`, the analyzer reports an error if no matching member exists in the supertype, catching bugs at compile time. It also serves as documentation — any reader immediately knows the method is part of a contract defined higher in the hierarchy.

---

## 🔑 Key Takeaways

- Dart has five constructor types: default, named, factory, redirecting, and `const` — each solves a different problem.
- Initializer lists run before the constructor body and are the only place to initialize `final` fields via computation.
- Factory constructors control what instance is returned, enabling singletons, caching, and subtype dispatch.
- `const` constructors require all-`final` fields and constant initializers; they enable compile-time canonicalization.
- Always override `==` and `hashCode` together, using `Object.hash()` to combine fields.
- `static` members belong to the class, not instances — use them for constants and stateless utilities.
- The cascade operator `..` chains calls on the same receiver; it returns the receiver, not the last method's return value.
- `@override` is not mandatory but is strongly recommended — it turns silent typos into compile errors.

---

## 🔗 Related Topics

- **Previous:** [Day 07 — Error Handling](../Week-1-Dart-Fundamentals/Day-07-Error-Handling.md)
- **Next:** [Day 09 — Inheritance, Abstract Classes & Interfaces](./Day-09-Inheritance-Abstract-Interfaces.md)
- **Day 10:** [Mixins](./Day-10-Mixins.md) — composing behavior across class hierarchies without inheritance
- **Dart Cheatsheet:** [Class & Constructor syntax quick reference](../Cheatsheets/Dart-Cheatsheet.md)
- **Cross-plan:** [JavaScript Classes & Prototypes](../../JavaScript/30-Day-JS-Mastery/Week-1-Core-Foundations/Day-05-Objects-Prototypes.md) — compare OOP models between Dart and JS
