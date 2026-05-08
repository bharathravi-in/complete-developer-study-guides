# Day 14: Enums

## 🎯 What You'll Learn

- How to declare a simple enum and use `values`, `name`, and `index`
- How switch exhaustiveness checking works with enums in Dart 3
- How to declare an enhanced enum (Dart 2.17+) with fields, constructors, and methods
- How to implement interfaces on an enum
- How pattern matching works with enums using Dart 3 switch expressions
- How to look up an enum value by name with `EnumName.values.byName()`
- Common patterns: state machines, configuration flags, and command dispatch with enums
- The difference between simple enums and enhanced enums and when to use each

---

## 📚 Core Concepts

### Simple Enums

A simple enum declares a fixed set of named constants. Each constant has an `index` (zero-based position in the declaration) and a `name` (the identifier as a string):

```dart
enum Direction { north, south, east, west }

final d = Direction.north;
print(d.name);  // north
print(d.index); // 0
print(Direction.values); // [Direction.north, Direction.south, Direction.east, Direction.west]
```

Enums are types — you can use them in type annotations, switch statements, and collections. Every enum implicitly extends `Enum` and cannot be subclassed or instantiated with `new`.

### Switch Exhaustiveness

Dart 3's switch expressions and switch statements are **exhaustive** for enums — the compiler requires you to handle every case (or provide a `default`/`_` wildcard). This is a powerful safety feature: if you add a new enum value later, every switch on that enum becomes a compile error until you handle the new case.

```dart
// Switch expression — must be exhaustive (no default needed if all cases covered)
String describe(Direction d) => switch (d) {
  Direction.north => 'Going north',
  Direction.south => 'Going south',
  Direction.east  => 'Going east',
  Direction.west  => 'Going west',
  // No default needed — all 4 cases are covered
};
```

If you add `Direction.up` later, this switch becomes a compile error immediately — the compiler tells you exactly which switches need updating.

### Enhanced Enums (Dart 2.17+)

Enhanced enums allow enum constants to carry data and have methods, making them far more powerful than simple named constants. An enhanced enum can have:

- **Fields** (must be `final`)
- **Constructors** (must be `const`)
- **Methods** and **getters**
- **Implemented interfaces** (via `implements`)
- **Overridden `toString()`**

The syntax looks like a class declaration inside an `enum`:

```dart
enum Planet {
  mercury(3.303e+23, 2.4397e6),
  venus(4.869e+24, 6.0518e6),
  earth(5.976e+24, 6.37814e6);

  // Fields — must be final
  final double mass;
  final double radius;

  // Constructor — must be const
  const Planet(this.mass, this.radius);

  // Method — can use fields
  double get surfaceGravity {
    const g = 6.67430e-11;
    return g * mass / (radius * radius);
  }
}
```

Each enum constant calls the constructor with its arguments. The semicolon after the last constant is required when the enum has members.

### `values`, `name`, `index`, and `byName()`

All enums (simple and enhanced) have these built-in members:

- **`EnumType.values`**: A `List<EnumType>` of all constants in declaration order.
- **`.name`**: The constant's identifier as a `String` (e.g., `Direction.north.name == 'north'`).
- **`.index`**: The zero-based position in the declaration.
- **`EnumType.values.byName(String name)`**: Looks up a constant by its name string. Throws `ArgumentError` if not found. Useful for deserializing from JSON or user input.

```dart
final d = Direction.values.byName('east'); // Direction.east
print(d); // Direction.east
```

For safe lookup (returning null instead of throwing), use:
```dart
Direction? safeByName(String name) {
  try {
    return Direction.values.byName(name);
  } on ArgumentError {
    return null;
  }
}
```

Or with Dart 3 patterns:
```dart
Direction? safeByName(String name) =>
    Direction.values.where((d) => d.name == name).firstOrNull;
```

### Pattern Matching on Enums (Dart 3)

Dart 3 switch expressions support full pattern matching on enums, including guard clauses (`when`) and destructuring of enhanced enum fields:

```dart
// Guard clause — additional condition on a case
String classify(Direction d) => switch (d) {
  Direction.north || Direction.south => 'vertical',
  Direction.east  || Direction.west  => 'horizontal',
};

// With enhanced enums — access fields in the switch
String describePlanet(Planet p) => switch (p) {
  Planet.earth => 'Our home planet',
  Planet _ when p.surfaceGravity > 9 => 'High gravity planet',
  _ => 'Other planet',
};
```

### Enums Implementing Interfaces

Enhanced enums can implement interfaces, which is useful for polymorphic dispatch:

```dart
abstract interface class Describable {
  String get description;
}

enum Status implements Describable {
  active('Currently active'),
  inactive('Not active'),
  pending('Awaiting activation');

  @override
  final String description;
  const Status(this.description);
}

void printDescription(Describable d) => print(d.description);
printDescription(Status.active); // Currently active
```

---

## 💻 Code Examples

### Example 1: Simple Enum — `values`, `name`, `index`, Switch Exhaustiveness

```dart
// ── Simple enum declaration ────────────────────────────────────────────────
enum Weekday {
  monday,
  tuesday,
  wednesday,
  thursday,
  friday,
  saturday,
  sunday,
}

// ── Exhaustive switch expression (Dart 3) ─────────────────────────────────
// The compiler verifies all 7 cases are covered — no default needed.
bool isWeekend(Weekday day) => switch (day) {
  Weekday.saturday || Weekday.sunday => true, // OR pattern
  _ => false, // wildcard covers the remaining 5 weekdays
};

String dayType(Weekday day) => switch (day) {
  Weekday.monday ||
  Weekday.tuesday ||
  Weekday.wednesday ||
  Weekday.thursday ||
  Weekday.friday =>
    'Workday',
  Weekday.saturday => 'Saturday',
  Weekday.sunday   => 'Sunday',
  // All 7 cases covered — exhaustive, no default needed
};

void main() {
  // ── Basic properties ──────────────────────────────────────────────────
  final day = Weekday.wednesday;
  print(day.name);  // wednesday
  print(day.index); // 2 (zero-based)

  // ── Iterating all values ──────────────────────────────────────────────
  print('\nAll weekdays:');
  for (final d in Weekday.values) {
    print('  ${d.index}: ${d.name} — ${dayType(d)}');
  }

  // ── byName() — look up by string ──────────────────────────────────────
  final friday = Weekday.values.byName('friday');
  print('\nFound: $friday'); // Weekday.friday
  print('Is weekend: ${isWeekend(friday)}'); // false

  // ── Safe byName using firstOrNull (Dart 3) ────────────────────────────
  // firstOrNull is available on Iterable in Dart 3
  Weekday? safeByName(String name) =>
      Weekday.values.where((d) => d.name == name).firstOrNull;

  print(safeByName('monday'));  // Weekday.monday
  print(safeByName('holiday')); // null — no such value

  // ── Enum in a collection ──────────────────────────────────────────────
  final workdays = Weekday.values.where((d) => !isWeekend(d)).toList();
  print('\nWorkdays: ${workdays.map((d) => d.name).join(', ')}');
  // monday, tuesday, wednesday, thursday, friday

  // ── Enum comparison ───────────────────────────────────────────────────
  // Enums support == and can be used in Sets and as Map keys
  final schedule = {
    Weekday.monday: 'Team standup',
    Weekday.wednesday: 'Design review',
    Weekday.friday: 'Sprint retrospective',
  };
  print('\nSchedule for ${day.name}: ${schedule[day] ?? 'No meetings'}');
  // Schedule for wednesday: Design review
}
```

### Example 2: Enhanced Enum with Fields, Constructor, and Methods

```dart
import 'dart:math' show pi;

// ── Enhanced enum: HTTP status codes ──────────────────────────────────────
enum HttpStatus {
  // Each constant calls the const constructor with its arguments
  ok(200, 'OK'),
  created(201, 'Created'),
  noContent(204, 'No Content'),
  badRequest(400, 'Bad Request'),
  unauthorized(401, 'Unauthorized'),
  forbidden(403, 'Forbidden'),
  notFound(404, 'Not Found'),
  internalServerError(500, 'Internal Server Error'),
  serviceUnavailable(503, 'Service Unavailable');

  // Fields — must be final in enhanced enums
  final int code;
  final String message;

  // Constructor — must be const
  const HttpStatus(this.code, this.message);

  // Computed getter — derived from fields
  bool get isSuccess => code >= 200 && code < 300;
  bool get isClientError => code >= 400 && code < 500;
  bool get isServerError => code >= 500 && code < 600;

  // Method — can use fields and other methods
  String toResponseLine() => 'HTTP/1.1 $code $message';

  // Static factory — look up by code number
  static HttpStatus? fromCode(int code) =>
      HttpStatus.values.where((s) => s.code == code).firstOrNull;

  @override
  String toString() => '$code $message';
}

// ── Enhanced enum implementing an interface ────────────────────────────────
abstract interface class Measurable {
  double get area;
  double get perimeter;
}

enum RegularPolygon implements Measurable {
  triangle(3),
  square(4),
  pentagon(5),
  hexagon(6),
  octagon(8);

  final int sides;
  const RegularPolygon(this.sides);

  // Compute area of a regular polygon with unit side length
  @override
  double get area {
    final s = 1.0; // unit side length
    return (sides * s * s) / (4 * (pi / sides).tan());
  }

  // Perimeter of a regular polygon with unit side length
  @override
  double get perimeter => sides * 1.0;
}

// Extension on double for tan (not in dart:math)
extension on double {
  double tan() => (this * pi / 180).sin() / (this * pi / 180).cos();
  double sin() {
    // Use dart:math indirectly via the formula
    // (simplified — in real code, import dart:math and use math.tan)
    return _sin(this);
  }
  double cos() => _cos(this);
}

double _sin(double x) {
  // Taylor series approximation (for demo purposes)
  // In production, use dart:math's sin/cos
  var result = 0.0;
  for (var n = 0; n < 10; n++) {
    final sign = n.isEven ? 1 : -1;
    result += sign * _pow(x, 2 * n + 1) / _factorial(2 * n + 1);
  }
  return result;
}

double _cos(double x) {
  var result = 0.0;
  for (var n = 0; n < 10; n++) {
    final sign = n.isEven ? 1 : -1;
    result += sign * _pow(x, 2 * n) / _factorial(2 * n);
  }
  return result;
}

double _pow(double base, int exp) =>
    exp == 0 ? 1.0 : base * _pow(base, exp - 1);

double _factorial(int n) => n <= 1 ? 1.0 : n * _factorial(n - 1);

void main() {
  // ── HttpStatus enhanced enum ──────────────────────────────────────────
  final status = HttpStatus.notFound;
  print(status);                    // 404 Not Found
  print(status.toResponseLine());   // HTTP/1.1 404 Not Found
  print(status.isClientError);      // true
  print(status.isSuccess);          // false

  // Static factory lookup
  final found = HttpStatus.fromCode(200);
  print(found);                     // 200 OK
  print(found?.isSuccess);          // true

  final unknown = HttpStatus.fromCode(999);
  print(unknown);                   // null

  print('\nAll success statuses:');
  for (final s in HttpStatus.values.where((s) => s.isSuccess)) {
    print('  ${s.toResponseLine()}');
  }
  // HTTP/1.1 200 OK
  // HTTP/1.1 201 Created
  // HTTP/1.1 204 No Content

  // ── RegularPolygon enum implementing Measurable ───────────────────────
  print('\nRegular polygons (unit side):');
  for (final polygon in RegularPolygon.values) {
    print('  ${polygon.name}: sides=${polygon.sides}, '
        'perimeter=${polygon.perimeter.toStringAsFixed(2)}');
  }
}
```

### Example 3: Pattern Matching on Enums with Dart 3 Switch Expressions, `byName()`

```dart
// ── State machine using enhanced enum ─────────────────────────────────────
enum OrderStatus {
  pending('Order placed, awaiting payment'),
  paid('Payment confirmed'),
  processing('Being prepared'),
  shipped('On the way'),
  delivered('Successfully delivered'),
  cancelled('Order cancelled'),
  refunded('Refund processed');

  final String description;
  const OrderStatus(this.description);

  // Returns the valid next statuses from this state
  List<OrderStatus> get nextStatuses => switch (this) {
    OrderStatus.pending    => [OrderStatus.paid, OrderStatus.cancelled],
    OrderStatus.paid       => [OrderStatus.processing, OrderStatus.cancelled],
    OrderStatus.processing => [OrderStatus.shipped],
    OrderStatus.shipped    => [OrderStatus.delivered],
    OrderStatus.delivered  => [OrderStatus.refunded],
    OrderStatus.cancelled  => [],  // terminal state
    OrderStatus.refunded   => [],  // terminal state
  };

  bool get isTerminal => nextStatuses.isEmpty;

  // Can this status transition to [next]?
  bool canTransitionTo(OrderStatus next) => nextStatuses.contains(next);
}

// ── Pattern matching with guard clauses ───────────────────────────────────
String classifyStatus(OrderStatus status) => switch (status) {
  // OR pattern — multiple cases with the same result
  OrderStatus.cancelled || OrderStatus.refunded => '❌ Closed',
  OrderStatus.delivered => '✅ Complete',
  // Guard clause — additional condition
  OrderStatus _ when status.isTerminal => '🔒 Terminal',
  _ => '⏳ In Progress',
};

// ── Deserializing from JSON/API using byName() ────────────────────────────
OrderStatus? parseStatus(String raw) {
  try {
    // byName() throws ArgumentError if the name doesn't match
    return OrderStatus.values.byName(raw);
  } on ArgumentError {
    return null; // unknown status from API
  }
}

// ── Enum-based command dispatch ────────────────────────────────────────────
enum Command { start, stop, pause, resume, reset }

typedef CommandHandler = void Function();

class CommandDispatcher {
  final Map<Command, CommandHandler> _handlers;

  CommandDispatcher(this._handlers);

  void dispatch(Command cmd) {
    final handler = _handlers[cmd];
    if (handler == null) {
      print('No handler registered for ${cmd.name}');
      return;
    }
    handler();
  }
}

void main() {
  // ── State machine transitions ─────────────────────────────────────────
  var order = OrderStatus.pending;
  print('Initial: ${order.name} — ${order.description}');

  void tryTransition(OrderStatus next) {
    if (order.canTransitionTo(next)) {
      print('  ✓ ${order.name} → ${next.name}');
      order = next;
    } else {
      print('  ✗ Cannot go from ${order.name} to ${next.name}');
    }
  }

  tryTransition(OrderStatus.paid);       // ✓ pending → paid
  tryTransition(OrderStatus.shipped);    // ✗ Cannot skip processing
  tryTransition(OrderStatus.processing); // ✓ paid → processing
  tryTransition(OrderStatus.shipped);    // ✓ processing → shipped
  tryTransition(OrderStatus.delivered);  // ✓ shipped → delivered

  print('\nFinal status: ${classifyStatus(order)}'); // ✅ Complete

  // ── Pattern matching classification ──────────────────────────────────
  print('\nStatus classifications:');
  for (final s in OrderStatus.values) {
    print('  ${s.name}: ${classifyStatus(s)}');
  }

  // ── byName() deserialization ──────────────────────────────────────────
  print('\nParsing from API:');
  final apiResponses = ['shipped', 'UNKNOWN', 'delivered', 'pending'];
  for (final raw in apiResponses) {
    final status = parseStatus(raw);
    print('  "$raw" → ${status?.name ?? 'null (unknown)'}');
  }
  // "shipped" → shipped
  // "UNKNOWN" → null (unknown)  — byName is case-sensitive
  // "delivered" → delivered
  // "pending" → pending

  // ── Command dispatch ──────────────────────────────────────────────────
  print('\nCommand dispatch:');
  final dispatcher = CommandDispatcher({
    Command.start:  () => print('  Starting...'),
    Command.stop:   () => print('  Stopping...'),
    Command.pause:  () => print('  Pausing...'),
    Command.resume: () => print('  Resuming...'),
    // Command.reset intentionally not registered
  });

  for (final cmd in Command.values) {
    dispatcher.dispatch(cmd);
  }
  // Starting...
  // Stopping...
  // Pausing...
  // Resuming...
  // No handler registered for reset
}
```

---

## ⚠️ Common Pitfalls

1. **`byName()` is case-sensitive and throws on no match.** `Direction.values.byName('North')` throws `ArgumentError` because the name is `'north'` (lowercase). Always match the exact identifier spelling, and wrap in a try-catch or use a `where`/`firstOrNull` pattern for safe lookup from untrusted input.

2. **Forgetting the semicolon after the last constant in an enhanced enum.** When an enhanced enum has fields, constructors, or methods, the list of constants must end with a semicolon before the member declarations. `enum Foo { a, b }` is fine for simple enums, but `enum Foo { a, b final int x; const Foo(this.x); }` is a syntax error — it must be `enum Foo { a(1), b(2); final int x; const Foo(this.x); }`.

3. **Assuming `index` is stable across code changes.** The `index` of an enum constant is its zero-based position in the declaration. If you add a new constant before existing ones, all subsequent indices shift. Never persist `index` values to a database or API — use `name` instead, which is stable as long as you don't rename the constant.

4. **Trying to use a non-const expression in an enhanced enum constructor.** Enhanced enum constructors must be `const`, which means all field initializers must be compile-time constants. You cannot call `DateTime.now()` or `Random()` in an enum constructor. If you need runtime-computed values, use a method or getter instead of a field.

5. **Not handling all enum cases in a switch and relying on a `default` that silently ignores new values.** Using `default:` in a switch on an enum means the compiler won't warn you when you add a new enum value. Prefer exhaustive switches (covering all cases explicitly) so that adding a new value causes a compile error at every switch site, forcing you to handle it.

---

## ❓ Interview Questions

### Q1: What is the difference between a simple enum and an enhanced enum in Dart?

**Answer:** A simple enum is a fixed set of named constants with no additional data — each constant has only its `name` (string), `index` (position), and the implicit `toString()`. An enhanced enum (introduced in Dart 2.17) allows each constant to carry data via `final` fields, initialized through a `const` constructor. Enhanced enums can also have methods, getters, and can implement interfaces. For example, a simple `enum Color { red, green, blue }` gives you named constants, while an enhanced `enum Color { red(0xFF0000), green(0x00FF00), blue(0x0000FF); final int hex; const Color(this.hex); }` lets each constant carry its hex value and expose methods that use it. Use simple enums for plain named constants; use enhanced enums when each constant needs associated data or behavior.

### Q2: How do you add methods and fields to a Dart enum?

**Answer:** In an enhanced enum (Dart 2.17+), you add fields and methods inside the enum body, after a semicolon that terminates the list of constants. Fields must be `final`, and the constructor must be `const`. Each constant in the list calls the constructor with its arguments. For example: `enum Status { active('Active'), inactive('Inactive'); final String label; const Status(this.label); String get display => '[$label]'; }`. The constants `Status.active` and `Status.inactive` each carry a `label` string and expose the `display` getter. Methods can use `this` (the enum constant itself), call other methods, and access fields — they behave like regular instance methods.

### Q3: How does Dart 3 pattern matching work with enums?

**Answer:** Dart 3 switch expressions and statements support exhaustive pattern matching on enums — the compiler verifies that all enum values are handled, eliminating the need for a `default` case when all values are covered. You can use OR patterns (`case A || B =>`) to handle multiple values with the same result, guard clauses (`case X when condition =>`) to add extra conditions, and wildcard patterns (`_ =>`) as a catch-all. Switch expressions on enums are particularly powerful because they are expressions (they return a value) and are exhaustive (the compiler catches missing cases). When you add a new enum value, every non-exhaustive switch becomes a compile error, forcing you to handle the new case explicitly.

### Q4: What is `EnumName.values.byName()` and when would you use it?

**Answer:** `EnumName.values.byName(String name)` is a method on the `List<EnumName>` returned by `values` that looks up an enum constant by its `name` string. It returns the matching constant or throws `ArgumentError` if no constant has that name. It is case-sensitive and matches the exact identifier spelling. The primary use case is deserializing enum values from external sources like JSON APIs, databases, or user input — where you receive a string and need to convert it to the corresponding enum constant. For safe lookup (returning null instead of throwing), use `values.where((e) => e.name == name).firstOrNull` or wrap `byName` in a try-catch. Never use `index` for serialization — use `name` because it is stable across reordering.

### Q5: Can a Dart enum implement an interface?

**Answer:** Yes — enhanced enums can implement interfaces using the `implements` keyword, just like classes. This is useful for polymorphic dispatch: you can pass an enum constant to a function that accepts the interface type, and the enum's method implementation will be called. For example, `enum Status implements Describable { active('Active'); final String description; const Status(this.description); }` allows `Status.active` to be used anywhere a `Describable` is expected. All constants of the enum must satisfy the interface contract — if the interface has abstract methods, the enum must implement them (either in the enum body or via the constructor-initialized fields). Enums cannot extend classes (other than the implicit `Enum` superclass), but they can implement multiple interfaces.

---

## 🔑 Key Takeaways

- Simple enums provide named constants with `name`, `index`, and `values`; enhanced enums (Dart 2.17+) add `final` fields, `const` constructors, and methods.
- Dart 3 switch expressions are exhaustive on enums — the compiler catches missing cases, making enums safe to extend.
- Use `name` (not `index`) for serialization — `index` changes when you reorder constants.
- `EnumName.values.byName(name)` deserializes from a string; it throws on no match — use `firstOrNull` or try-catch for safe lookup.
- Enhanced enums can implement interfaces, enabling polymorphic dispatch.
- Never use non-const expressions in enhanced enum constructors — all field initializers must be compile-time constants.
- Enums are ideal for state machines, configuration flags, command dispatch, and any domain concept with a fixed set of named values.

---

## 🔗 Related Topics

- **Previous:** [Day 13 — Extension Methods](./Day-13-Extension-Methods.md)
- **Next:** [Day 15 — Async Fundamentals](../Week-3-Async-Advanced/Day-15-Async-Fundamentals.md)
- **Day 04:** [Control Flow](../Week-1-Dart-Fundamentals/Day-04-Control-Flow.md) — switch statements and expressions
- **Day 18:** [Dart 3 Features](../Week-3-Async-Advanced/Day-18-Dart3-Features.md) — sealed classes, patterns, and exhaustive matching
- **Dart Cheatsheet:** [Enum syntax quick reference](../Cheatsheets/Dart-Cheatsheet.md)
