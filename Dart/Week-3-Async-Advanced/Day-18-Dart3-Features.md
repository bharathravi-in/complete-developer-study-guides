# Day 18: Dart 3 Features

## 🎯 What You'll Learn
- Records — anonymous compound types with positional and named fields
- Patterns — destructuring, switch patterns, and pattern matching
- Guard clauses in switch expressions and case statements
- Sealed classes and exhaustiveness checking
- Class modifiers — `final`, `base`, `interface`, `sealed`, and `mixin`
- How these features improve type safety and expressiveness
- Migration considerations from Dart 2.x to Dart 3

## 📚 Core Concepts

Dart 3, released in May 2023, introduced several major language features that bring Dart closer to modern functional programming languages while maintaining its object-oriented roots. The headline features are **records** and **patterns**, which together enable powerful destructuring and pattern matching. Dart 3 also introduced **class modifiers** that give library authors fine-grained control over how their classes can be extended or implemented.

### Records

A **record** is an anonymous, immutable aggregate type. Records are defined by their field structure — two records with the same field types in the same order are the same type. Records can have positional fields, named fields, or both.

```dart
// Positional fields
(int, String) record = (42, 'answer');

// Named fields
({int x, int y}) point = (x: 10, y: 20);

// Mixed
(int, String, {bool flag}) mixed = (1, 'text', flag: true);
```

Records are useful for returning multiple values from functions without defining a custom class. They're lightweight, immutable, and have structural typing — no need to declare a type name.

### Patterns

**Patterns** are a new syntactic construct that can destructure data, match against shapes, and bind variables. Patterns appear in several contexts:
- Variable declarations: `var (x, y) = point;`
- Switch cases: `case (0, 0): print('origin');`
- If-case statements: `if (value case [int x, int y]) { ... }`
- For loops: `for (var (key, value) in entries) { ... }`

Patterns can match literals, types, records, lists, maps, and objects. They can also include guard clauses (`when` conditions) for additional filtering.

### Switch Expressions and Patterns

Dart 3 enhances `switch` with expression syntax and pattern matching. A switch expression evaluates to a value and must be exhaustive (cover all cases). Combined with patterns, this enables concise, type-safe branching.

```dart
String describe(Object obj) => switch (obj) {
  0 => 'zero',
  1 => 'one',
  int n when n < 0 => 'negative',
  int n => 'positive $n',
  String s => 'text: $s',
  _ => 'unknown',
};
```

### Guard Clauses

Guard clauses use the `when` keyword to add boolean conditions to patterns. This is more expressive than nested `if` statements and keeps related logic together.

```dart
switch (value) {
  case int n when n > 0:
    print('positive');
  case int n when n < 0:
    print('negative');
  case 0:
    print('zero');
}
```

### Sealed Classes

A **sealed class** can only be extended or implemented within the same library. This enables exhaustiveness checking in switch statements — the compiler knows all possible subtypes and can verify that every case is handled.

```dart
sealed class Shape {}
class Circle extends Shape { final double radius; Circle(this.radius); }
class Square extends Shape { final double side; Square(this.side); }

double area(Shape shape) => switch (shape) {
  Circle(radius: var r) => 3.14 * r * r,
  Square(side: var s) => s * s,
  // Compiler error if any subtype is missing
};
```

### Class Modifiers

Dart 3 introduces five class modifiers that control how classes can be used:

- **`final`**: The class cannot be extended or implemented outside its library, but can be instantiated.
- **`base`**: The class can be extended but not implemented. Subclasses must also be `base`, `final`, or `sealed`.
- **`interface`**: The class can be implemented but not extended. Used for pure contracts.
- **`sealed`**: The class can only be extended or implemented within the same library. Enables exhaustiveness checking.
- **`mixin`**: Declares a mixin (not a class). Mixins cannot be instantiated or extended, only mixed in.

These modifiers help library authors enforce API contracts and prevent misuse. For example, marking a class `final` prevents external code from creating fragile subclasses that break when the base class changes.

### Migration from Dart 2.x

Dart 3 is a major version with breaking changes. The most significant is that **sound null safety is now mandatory** — code without null safety cannot run on Dart 3. Most Dart 2.x code with null safety runs unchanged on Dart 3, but some edge cases (like implicit downcasts) are now errors. The Dart team provides migration tools and guides to help with the transition.


## 💻 Code Examples

### Example 1: Records for multiple return values

```dart
// Return multiple values without defining a class
(String, int) parseNameAndAge(String input) {
  final parts = input.split(',');
  return (parts[0].trim(), int.parse(parts[1].trim()));
}

void main() {
  final record = parseNameAndAge('Alice, 30');

  // Access positional fields with $1, $2, etc.
  print('Name: ${record.$1}'); // Name: Alice
  print('Age: ${record.$2}');   // Age: 30

  // Destructure in variable declaration
  var (name, age) = parseNameAndAge('Bob, 25');
  print('$name is $age years old'); // Bob is 25 years old

  // Named fields for clarity
  ({String name, int age}) person = (name: 'Charlie', age: 35);
  print('${person.name} is ${person.age}'); // Charlie is 35
}
```

### Example 2: Pattern matching in switch expressions

```dart
String classifyNumber(int n) => switch (n) {
  0 => 'zero',
  1 => 'one',
  -1 => 'negative one',
  _ when n < 0 => 'negative',
  _ when n > 0 && n < 10 => 'single digit',
  _ when n >= 10 && n < 100 => 'double digit',
  _ => 'large number',
};

void main() {
  print(classifyNumber(0));    // zero
  print(classifyNumber(-5));   // negative
  print(classifyNumber(7));    // single digit
  print(classifyNumber(42));   // double digit
  print(classifyNumber(1000)); // large number
}
```

### Example 3: Destructuring lists and records

```dart
void main() {
  // List pattern matching
  final numbers = [1, 2, 3, 4, 5];

  switch (numbers) {
    case []:
      print('empty');
    case [var x]:
      print('single element: $x');
    case [var first, var second, ...]:
      print('starts with $first, $second');
  }
  // Output: starts with 1, 2

  // Record pattern matching
  final point = (x: 10, y: 20);

  switch (point) {
    case (x: 0, y: 0):
      print('origin');
    case (x: var x, y: 0):
      print('on x-axis at $x');
    case (x: 0, y: var y):
      print('on y-axis at $y');
    case (x: var x, y: var y):
      print('at ($x, $y)');
  }
  // Output: at (10, 20)

  // Destructure in for loop
  final entries = [(1, 'one'), (2, 'two'), (3, 'three')];
  for (var (num, word) in entries) {
    print('$num -> $word');
  }
  // Output:
  // 1 -> one
  // 2 -> two
  // 3 -> three
}
```

### Example 4: Sealed classes with exhaustiveness checking

```dart
sealed class Result<T> {}

class Success<T> extends Result<T> {
  final T value;
  Success(this.value);
}

class Failure<T> extends Result<T> {
  final String error;
  Failure(this.error);
}

// Compiler enforces exhaustiveness — all subtypes must be handled
String handleResult(Result<int> result) => switch (result) {
  Success(value: var v) => 'Got value: $v',
  Failure(error: var e) => 'Error: $e',
  // If we add a new subtype, this switch becomes a compile error
};

void main() {
  final success = Success(42);
  final failure = Failure<int>('Network error');

  print(handleResult(success)); // Got value: 42
  print(handleResult(failure)); // Error: Network error
}
```

### Example 5: Class modifiers in action

```dart
// final class — cannot be extended or implemented outside this library
final class ImmutableConfig {
  final String apiKey;
  final int timeout;

  const ImmutableConfig(this.apiKey, this.timeout);
}

// base class — can be extended but not implemented
base class Vehicle {
  void move() => print('moving');
}

// Must use 'base', 'final', or 'sealed' when extending a base class
final class Car extends Vehicle {
  @override
  void move() => print('driving');
}

// interface class — can be implemented but not extended
interface class Drawable {
  void draw();
}

// OK to implement
class Circle implements Drawable {
  @override
  void draw() => print('drawing circle');
}

// sealed class — only extendable within same library
sealed class PaymentMethod {}
class CreditCard extends PaymentMethod {}
class PayPal extends PaymentMethod {}
class BankTransfer extends PaymentMethod {}

String processPayment(PaymentMethod method) => switch (method) {
  CreditCard() => 'Processing credit card',
  PayPal() => 'Processing PayPal',
  BankTransfer() => 'Processing bank transfer',
  // Exhaustive — compiler knows all subtypes
};

void main() {
  final config = ImmutableConfig('secret', 5000);
  print('Timeout: ${config.timeout}');

  final car = Car();
  car.move(); // driving

  final circle = Circle();
  circle.draw(); // drawing circle

  final payment = CreditCard();
  print(processPayment(payment)); // Processing credit card
}
```

### Example 6: Guard clauses and if-case statements

```dart
void main() {
  final data = [1, 2, 3];

  // if-case statement — pattern matching in if
  if (data case [var first, ...]) {
    print('First element: $first'); // First element: 1
  }

  // Guard clauses in switch
  for (var i = -2; i <= 2; i++) {
    final result = switch (i) {
      0 => 'zero',
      int n when n > 0 => 'positive $n',
      int n when n < 0 => 'negative $n',
      _ => 'unknown',
    };
    print('$i: $result');
  }
  // Output:
  // -2: negative -2
  // -1: negative -1
  // 0: zero
  // 1: positive 1
  // 2: positive 2

  // Complex guard with multiple conditions
  final user = (name: 'Alice', age: 17, isAdmin: false);

  final access = switch (user) {
    (age: >= 18, isAdmin: true) => 'full admin access',
    (age: >= 18, isAdmin: false) => 'standard access',
    (age: < 18, isAdmin: true) => 'junior admin access',
    (age: < 18, isAdmin: false) => 'restricted access',
  };

  print(access); // restricted access
}
```

## ⚠️ Common Pitfalls

- **Forgetting exhaustiveness in sealed classes**: When switching on a sealed class, you must handle all subtypes. Adding a new subtype breaks existing switches — this is intentional and helps catch bugs, but can be surprising during refactoring.
- **Confusing record field access**: Positional fields use `$1`, `$2`, etc., not `[0]`, `[1]`. Named fields use dot notation. Mixing them up causes compile errors.
- **Overusing patterns**: Patterns are powerful but can reduce readability if overused. Simple cases are often clearer with traditional `if/else` or property access.
- **Misunderstanding class modifiers**: `final` prevents extension, `base` prevents implementation, `interface` prevents extension. Choosing the wrong modifier can make your API too restrictive or too permissive.
- **Breaking changes in Dart 3**: Code without null safety won't run. Some implicit downcasts that worked in Dart 2 are now errors. Always test thoroughly when migrating.

## ❓ Interview Questions

### Q1: What are records and how do they differ from classes?
**Answer**: Records are anonymous, immutable aggregate types defined by their field structure. Unlike classes, records don't have a declared type name — two records with the same field types in the same order are the same type (structural typing). Records are lightweight and perfect for returning multiple values from functions without defining a custom class. Classes have nominal typing (type identity based on name), can be mutable, and support methods and inheritance. Use records for simple data grouping and classes for complex behavior and identity.

### Q2: What is the purpose of sealed classes?
**Answer**: Sealed classes restrict subtyping to the same library, enabling exhaustiveness checking in switch statements. The compiler knows all possible subtypes and can verify that every case is handled, catching bugs at compile time. This is especially useful for modeling algebraic data types like `Result<T>` (Success or Failure) or state machines where you want to ensure all states are handled. If you add a new subtype, all existing switches become compile errors, forcing you to update them.

### Q3: Explain the difference between final, base, and interface class modifiers.
**Answer**: `final` prevents a class from being extended or implemented outside its library — it's a closed type that can only be instantiated. `base` allows extension but not implementation, ensuring subclasses inherit the base implementation rather than providing their own. Subclasses of `base` classes must also be `base`, `final`, or `sealed`. `interface` allows implementation but not extension — it's a pure contract with no inherited behavior. These modifiers give library authors control over how their classes are used and prevent fragile subclassing.

### Q4: How do guard clauses improve pattern matching?
**Answer**: Guard clauses use the `when` keyword to add boolean conditions to patterns, enabling more expressive and concise branching logic. Instead of nesting `if` statements inside case blocks, you can write `case int n when n > 0:` to match positive integers. This keeps related logic together and makes the intent clearer. Guards are especially powerful in switch expressions where you need to distinguish between multiple cases of the same type based on runtime values.

### Q5: What is the difference between switch statements and switch expressions in Dart 3?
**Answer**: Switch statements execute code blocks and don't return a value — they're used for side effects. Switch expressions evaluate to a value and must be exhaustive (cover all cases). Switch expressions use `=>` syntax like arrow functions and are more concise. For example, `String result = switch (x) { 0 => 'zero', _ => 'other' };` assigns the result directly. Switch statements use traditional `case:` syntax with `break`. Use expressions when you need a value, statements when you need side effects.

### Q6: How do patterns enable destructuring in Dart?
**Answer**: Patterns can appear in variable declarations, extracting values from compound types. For example, `var (x, y) = point;` destructures a record into two variables. `var [first, ...rest] = list;` extracts the first element and remaining elements. Patterns work with records, lists, maps, and objects. This eliminates boilerplate code for accessing nested data and makes code more readable. Destructuring is especially useful in for loops: `for (var (key, value) in entries)` is cleaner than `for (var entry in entries) { var key = entry.$1; ... }`.

### Q7: What are the breaking changes in Dart 3 and how do you migrate?
**Answer**: The biggest breaking change is that sound null safety is now mandatory — code without null safety won't run. Some implicit downcasts that were warnings in Dart 2 are now errors in Dart 3. The `dart migrate` tool helps automate null safety migration. Most Dart 2.x code with null safety runs unchanged on Dart 3. Test thoroughly, especially around type casts and null checks. The Dart team provides a migration guide and the analyzer flags issues. For libraries, consider using class modifiers to future-proof your API.

### Q8: When should you use records instead of defining a class?
**Answer**: Use records for simple, temporary data grouping where you don't need methods, identity, or a named type. Records are perfect for returning multiple values from functions, representing coordinates or pairs, or passing multiple arguments as a single value. Use classes when you need behavior (methods), identity (two instances with the same values should be different objects), mutability, or when the type will be used extensively throughout your codebase and deserves a meaningful name. Records are lightweight and convenient; classes are powerful and expressive.



## 🔑 Key Takeaways
- Records are anonymous, immutable aggregate types with structural typing — perfect for multiple return values
- Patterns enable destructuring and pattern matching in variable declarations, switch cases, and loops
- Sealed classes enable exhaustiveness checking — the compiler ensures all subtypes are handled
- Guard clauses (`when`) add boolean conditions to patterns for more expressive branching
- Class modifiers (`final`, `base`, `interface`, `sealed`) give fine-grained control over inheritance
- Switch expressions evaluate to a value and must be exhaustive, unlike switch statements
- Dart 3 requires sound null safety — migration tools help transition from Dart 2.x

## 🔗 Related Topics
- [Day 03: Null Safety](../Week-1-Dart-Fundamentals/Day-03-Null-Safety.md) — foundation for Dart 3's mandatory null safety
- [Day 09: Inheritance, Abstract, Interfaces](../Week-2-OOP-Collections/Day-09-Inheritance-Abstract-Interfaces.md) — class modifiers build on these concepts
- [Day 14: Enums](../Week-2-OOP-Collections/Day-14-Enums.md) — enhanced enums use similar pattern matching
- [Day 24: Design Patterns](../Week-4-Flutter-Dart-Interview/Day-24-Design-Patterns.md) — sealed classes for algebraic data types
- [DS Backtracking](../../DS/Days/Day_24_Backtracking.md) — pattern matching for algorithm design
