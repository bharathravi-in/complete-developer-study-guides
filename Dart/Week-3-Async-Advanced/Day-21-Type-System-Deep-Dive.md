# Day 21: Type System Deep Dive

## 🎯 What You'll Learn
- The `typedef` keyword for type aliases and function types
- Function types and first-class functions
- The `covariant` keyword and variance in generics
- Difference between `dynamic`, `Object`, and `Object?`
- Type promotion and flow analysis
- Sound null safety internals and the type hierarchy
- Reified generics and runtime type information
- When to use `as`, `is`, and type inference

## 📚 Core Concepts

Dart has a **sound type system** — the compiler guarantees that a value's runtime type matches its static type. This enables powerful optimizations and catches bugs at compile time. Understanding Dart's type system deeply helps you write safer, more expressive code and debug type errors effectively.

### typedef — Type Aliases

`typedef` creates an alias for a type, making complex types more readable and reusable. It's most commonly used for function types but works for any type.

```dart
// Function type alias
typedef IntOperation = int Function(int a, int b);

// Use the alias
IntOperation add = (a, b) => a + b;
IntOperation multiply = (a, b) => a * b;

// Generic type alias
typedef JsonMap = Map<String, dynamic>;

// Function type with generics
typedef Mapper<T, R> = R Function(T input);
```

Before Dart 2, `typedef` only worked for function types. Modern Dart allows aliasing any type, including classes and generics.

### Function Types

Functions are first-class objects in Dart — they have types and can be assigned to variables, passed as arguments, and returned from functions. Function types specify parameter types and return type.

```dart
// Function type: (int, int) -> int
int Function(int, int) operation;

// Named parameters in function types
void Function({required String name, int age}) greet;

// Optional positional parameters
String Function(String, [int?]) format;
```

Function types are structural — two functions with the same signature are the same type, regardless of their names.

### covariant — Overriding with Subtypes

By default, Dart enforces **contravariance** for method parameters — an overriding method cannot narrow parameter types. The `covariant` keyword allows you to override a method with a more specific parameter type, but this is checked at runtime, not compile time.

```dart
class Animal {
  void chase(Animal other) {}
}

class Cat extends Animal {
  // covariant allows narrowing the parameter type
  @override
  void chase(covariant Cat other) {
    // Can call Cat-specific methods on other
  }
}
```

Use `covariant` sparingly — it weakens type safety by deferring checks to runtime.

### dynamic vs Object vs Object?

These three types represent "any value" but with different semantics:

- **`dynamic`**: Disables static type checking. Any operation is allowed at compile time, but may fail at runtime. Use only when you truly don't know the type (e.g., JSON parsing).
- **`Object`**: The root of the non-nullable type hierarchy. Every non-nullable type is a subtype of `Object`. You can't call arbitrary methods without casting.
- **`Object?`**: The root of the entire type hierarchy, including nullable types. Every type (nullable or not) is a subtype of `Object?`.

```dart
dynamic d = 'text';
d.anyMethod(); // Compiles, may fail at runtime

Object o = 'text';
// o.anyMethod(); // Compile error — Object doesn't have anyMethod
print(o.toString()); // OK — toString() is on Object

Object? maybeNull = null; // OK
// maybeNull.toString(); // Compile error — might be null
```

Prefer `Object` or `Object?` over `dynamic` for better type safety.

### Type Promotion and Flow Analysis

Dart's flow analysis tracks the types of variables through control flow and **promotes** them to more specific types when safe. This eliminates unnecessary casts.

```dart
void process(Object obj) {
  if (obj is String) {
    // obj is promoted to String here
    print(obj.length); // No cast needed
  }

  String? nullable = 'text';
  if (nullable != null) {
    // nullable is promoted to String (non-nullable)
    print(nullable.length); // No ! needed
  }
}
```

Type promotion works with `is` checks, null checks, and even `&&` / `||` operators. It's one of Dart's most powerful type system features.

### Sound Null Safety Internals

Dart's null safety is **sound** — the compiler guarantees that non-nullable variables never contain `null`. The type hierarchy has two branches:

- **Non-nullable types**: `int`, `String`, `Object`, etc. — cannot be `null`
- **Nullable types**: `int?`, `String?`, `Object?`, etc. — can be `null`

`Null` is a subtype of all nullable types but not of non-nullable types. This is enforced at compile time, with runtime checks only for `dynamic` and interop boundaries.

### Reified Generics

Unlike Java (which uses type erasure), Dart's generics are **reified** — type information is available at runtime. You can check the type of a generic collection or use `is` with generic types.

```dart
void check<T>(List<T> list) {
  print(list is List<int>); // true if T is int
  print(T); // prints the actual type
}

check<int>([1, 2, 3]); // true, int
check<String>(['a']); // false, String
```

This enables powerful runtime type checks and reflection, but also means generic types affect runtime behavior and performance.

### Type Inference

Dart infers types from context when you use `var`, `final`, or omit type annotations. The inference is **local** — it looks at the initializer, not how the variable is used later.

```dart
var x = 42; // inferred as int
final list = [1, 2, 3]; // inferred as List<int>
final map = {'key': 'value'}; // inferred as Map<String, String>

// Inference from function return type
int getValue() => 42;
var y = getValue(); // y is int
```

Inference makes code concise without sacrificing type safety. Use explicit types when inference is unclear or when you want to document intent.

### Type Casts and Checks

- **`is`**: Type check — returns `bool`, enables type promotion
- **`as`**: Type cast — throws if the cast fails
- **`is!`**: Negated type check

```dart
Object obj = 'text';

if (obj is String) {
  print(obj.length); // obj promoted to String
}

String str = obj as String; // throws if obj is not String

if (obj is! int) {
  print('Not an int');
}
```

Prefer `is` with type promotion over `as` casts — it's safer and more idiomatic.


## 💻 Code Examples

### Example 1: typedef for function types and type aliases

```dart
// Function type aliases
typedef BinaryOperation = int Function(int a, int b);
typedef Predicate<T> = bool Function(T value);
typedef Mapper<T, R> = R Function(T input);

// Use function type aliases
BinaryOperation add = (a, b) => a + b;
BinaryOperation multiply = (a, b) => a * b;

Predicate<int> isEven = (n) => n % 2 == 0;
Predicate<String> isEmpty = (s) => s.isEmpty;

Mapper<int, String> intToString = (n) => n.toString();
Mapper<String, int> stringLength = (s) => s.length;

// Type alias for complex types
typedef JsonMap = Map<String, dynamic>;
typedef UserList = List<Map<String, dynamic>>;

void main() {
  print('5 + 3 = ${add(5, 3)}');           // 5 + 3 = 8
  print('5 * 3 = ${multiply(5, 3)}');     // 5 * 3 = 15
  print('Is 4 even? ${isEven(4)}');       // Is 4 even? true
  print('Length of "hello": ${stringLength("hello")}'); // Length of "hello": 5

  JsonMap user = {'name': 'Alice', 'age': 30};
  print('User: $user'); // User: {name: Alice, age: 30}
}
```

### Example 2: Function types and first-class functions

```dart
// Function that takes a function as parameter
int applyOperation(int a, int b, int Function(int, int) operation) {
  return operation(a, b);
}

// Function that returns a function
int Function(int) makeMultiplier(int factor) {
  return (int x) => x * factor;
}

// Function with named parameters
void greet({
  required String Function(String) formatter,
  required String name,
}) {
  print(formatter(name));
}

void main() {
  // Pass functions as arguments
  print(applyOperation(10, 5, (a, b) => a + b)); // 15
  print(applyOperation(10, 5, (a, b) => a - b)); // 5
  print(applyOperation(10, 5, (a, b) => a * b)); // 50

  // Store returned function
  final double = makeMultiplier(2);
  final triple = makeMultiplier(3);

  print('double(5) = ${double(5)}'); // double(5) = 10
  print('triple(5) = ${triple(5)}'); // triple(5) = 15

  // Pass function to named parameter
  greet(
    formatter: (name) => 'Hello, $name!',
    name: 'Alice',
  ); // Hello, Alice!
}
```

### Example 3: covariant for parameter type narrowing

```dart
class Animal {
  String name;
  Animal(this.name);

  void chase(Animal other) {
    print('$name chases ${other.name}');
  }
}

class Cat extends Animal {
  Cat(super.name);

  // covariant allows narrowing the parameter type
  @override
  void chase(covariant Cat other) {
    print('$name (cat) chases ${other.name} (cat)');
    meow(); // Can call Cat-specific methods
  }

  void meow() => print('$name says meow');
}

class Dog extends Animal {
  Dog(super.name);
}

void main() {
  final cat1 = Cat('Whiskers');
  final cat2 = Cat('Mittens');
  final dog = Dog('Rex');

  cat1.chase(cat2); // $name (cat) chases Mittens (cat)

  // Runtime error — covariant weakens type safety
  Animal animal = cat1;
  // animal.chase(dog); // Throws TypeError at runtime!
}
```

### Example 4: dynamic vs Object vs Object?

```dart
void main() {
  // dynamic — no static type checking
  dynamic d = 'text';
  d = 42; // OK — can change type
  d.anyMethod(); // Compiles, but throws at runtime
  print(d.length); // Runtime error — int has no length

  // Object — root of non-nullable types
  Object o = 'text';
  // o = null; // Compile error — Object is non-nullable
  print(o.toString()); // OK — toString() is on Object
  // print(o.length); // Compile error — Object has no length
  if (o is String) {
    print(o.length); // OK — type promotion to String
  }

  // Object? — root of all types (nullable and non-nullable)
  Object? maybeNull = null; // OK
  maybeNull = 'text'; // OK
  maybeNull = 42; // OK
  // print(maybeNull.toString()); // Compile error — might be null
  if (maybeNull != null) {
    print(maybeNull.toString()); // OK — promoted to Object
  }

  // Prefer Object/Object? over dynamic for type safety
  Object value = 'text';
  if (value is String) {
    print('String of length ${value.length}');
  } else if (value is int) {
    print('Integer: $value');
  }
}
```

### Example 5: Type promotion and flow analysis

```dart
void processValue(Object? value) {
  // Type promotion with is check
  if (value is String) {
    // value promoted to String
    print('String of length ${value.length}');
    print('Uppercase: ${value.toUpperCase()}');
  } else if (value is int) {
    // value promoted to int
    print('Integer: ${value.abs()}');
  }

  // Type promotion with null check
  String? nullable = 'hello';
  if (nullable != null) {
    // nullable promoted to String (non-nullable)
    print('Length: ${nullable.length}'); // No ! needed
  }

  // Type promotion with && operator
  if (value != null && value is String) {
    // value promoted to String (non-nullable)
    print('Non-null string: ${value.toUpperCase()}');
  }

  // Type promotion doesn't work across function calls
  String? text = 'test';
  if (text != null) {
    // text is promoted here
    someFunction();
    // text is no longer promoted — might have been modified
    // print(text.length); // Compile error
    print(text!.length); // Need ! or another null check
  }
}

void someFunction() {
  // Could modify external state
}

void main() {
  processValue('Dart');
  processValue(42);
  processValue(null);
}
// Output:
// String of length 4
// Uppercase: DART
// Integer: 42
```

### Example 6: Reified generics and runtime type information

```dart
void checkType<T>(List<T> list) {
  print('Type parameter T: $T');
  print('Runtime type of list: ${list.runtimeType}');

  // Reified generics — type info available at runtime
  if (list is List<int>) {
    print('List of integers');
  } else if (list is List<String>) {
    print('List of strings');
  }

  // Can check individual elements
  for (var item in list) {
    print('  Item: $item (${item.runtimeType})');
  }
}

class Box<T> {
  final T value;
  Box(this.value);

  // Can use T at runtime
  bool isTypeOf<R>() => T == R;

  void printType() {
    print('Box contains type: $T');
  }
}

void main() {
  checkType<int>([1, 2, 3]);
  print('---');
  checkType<String>(['a', 'b', 'c']);
  print('---');

  final intBox = Box<int>(42);
  intBox.printType(); // Box contains type: int
  print('Is int? ${intBox.isTypeOf<int>()}'); // Is int? true
  print('Is String? ${intBox.isTypeOf<String>()}'); // Is String? false
}
// Output:
// Type parameter T: int
// Runtime type of list: List<int>
// List of integers
//   Item: 1 (int)
//   Item: 2 (int)
//   Item: 3 (int)
// ---
// Type parameter T: String
// Runtime type of list: List<String>
// List of strings
//   Item: a (String)
//   Item: b (String)
//   Item: c (String)
// ---
// Box contains type: int
// Is int? true
// Is String? false
```

### Example 7: Type inference in action

```dart
void main() {
  // Inferred from initializer
  var x = 42; // int
  var text = 'hello'; // String
  var list = [1, 2, 3]; // List<int>
  var map = {'key': 'value'}; // Map<String, String>

  // Inferred from function return type
  int getValue() => 42;
  var y = getValue(); // int

  // Inferred from context
  List<int> numbers = [1, 2, 3];
  numbers.add(4); // OK
  // numbers.add('text'); // Compile error

  // Generic type inference
  final result = [1, 2, 3].map((x) => x * 2); // Iterable<int>
  final doubled = result.toList(); // List<int>

  // Inference with function parameters
  void process(int Function(int) fn) {
    print(fn(5));
  }

  process((x) => x * 2); // Parameter x inferred as int

  // Explicit types when inference is unclear
  var mixed = []; // List<dynamic> — unclear intent
  List<int> explicitList = []; // Better — clear intent

  print('x: $x (${x.runtimeType})');
  print('text: $text (${text.runtimeType})');
  print('list: $list (${list.runtimeType})');
  print('doubled: $doubled (${doubled.runtimeType})');
}
```

## ⚠️ Common Pitfalls

- **Overusing dynamic**: `dynamic` disables type checking and should be used sparingly. Prefer `Object` or `Object?` for better type safety.
- **Forgetting type promotion limits**: Type promotion doesn't work across function calls or when variables might be modified. Use local variables or explicit null checks.
- **Misusing covariant**: `covariant` weakens type safety by deferring checks to runtime. Use it only when necessary and document the runtime contract.
- **Confusing Object and Object?**: `Object` is non-nullable; `Object?` is nullable. Using the wrong one causes compile errors or unexpected null values.
- **Unnecessary type casts**: Prefer `is` checks with type promotion over `as` casts. Casts throw at runtime if they fail; type checks are safer.
- **Ignoring reified generics**: Unlike Java, Dart's generics are available at runtime. You can use `is` with generic types, but be aware of performance implications.

## ❓ Interview Questions

### Q1: What is the difference between dynamic, Object, and Object? in Dart?
**Answer**: `dynamic` disables static type checking — any operation is allowed at compile time but may fail at runtime. Use it only when you truly don't know the type. `Object` is the root of the non-nullable type hierarchy — every non-nullable type is a subtype of `Object`, but you can't call arbitrary methods without casting. `Object?` is the root of the entire type hierarchy, including nullable types — every type is a subtype of `Object?`. Prefer `Object` or `Object?` over `dynamic` for better type safety and IDE support.

### Q2: What is type promotion and how does it work?
**Answer**: Type promotion is when Dart's flow analysis automatically narrows a variable's type based on control flow. For example, after an `if (x is String)` check, `x` is promoted to `String` within that block, eliminating the need for casts. Type promotion also works with null checks: after `if (x != null)`, a nullable variable is promoted to non-nullable. Promotion is local and doesn't work across function calls or when variables might be modified. It's one of Dart's most powerful type system features, making code safer and more concise.

### Q3: What are reified generics and how do they differ from Java's type erasure?
**Answer**: Reified generics means type information is available at runtime. In Dart, you can check `list is List<int>` or print the type parameter `T` inside a generic function. Java uses type erasure — generic type information is removed at runtime, so you can't distinguish `List<Integer>` from `List<String>` at runtime. Dart's reified generics enable powerful runtime type checks and reflection but also mean generic types affect runtime behavior and performance. This is a key difference from Java and enables features like type-safe collections.

### Q4: What is the covariant keyword and when should you use it?
**Answer**: `covariant` allows you to override a method with a more specific parameter type than the base class. By default, Dart enforces contravariance for parameters — overriding methods cannot narrow parameter types. `covariant` weakens this guarantee by deferring the check to runtime. Use it when you need to specialize a method for a subclass but be aware that it can cause runtime type errors if the wrong type is passed. Document the runtime contract clearly and use sparingly — it trades compile-time safety for flexibility.

### Q5: What is typedef and what are its use cases?
**Answer**: `typedef` creates an alias for a type, making complex types more readable and reusable. It's most commonly used for function types: `typedef Predicate<T> = bool Function(T);` makes code cleaner than repeating `bool Function(T)` everywhere. Modern Dart also allows aliasing any type, including classes and generics: `typedef JsonMap = Map<String, dynamic>;`. Use `typedef` to document intent, reduce repetition, and make complex type signatures more manageable. It's purely a compile-time alias — the underlying type is unchanged.

### Q6: How does Dart's sound null safety work internally?
**Answer**: Dart's null safety is sound — the compiler guarantees that non-nullable variables never contain `null`. The type hierarchy has two branches: non-nullable types (`int`, `String`, `Object`) and nullable types (`int?`, `String?`, `Object?`). `Null` is a subtype of all nullable types but not of non-nullable types. This is enforced at compile time through flow analysis and type promotion. Runtime checks only occur at interop boundaries (like `dynamic` or FFI) where static guarantees can't be made. Sound null safety eliminates null reference errors at compile time, making Dart code safer.

### Q7: What is the difference between is and as in Dart?
**Answer**: `is` is a type check that returns a boolean and enables type promotion — after `if (x is String)`, `x` is promoted to `String` within that block. `as` is a type cast that throws a `TypeError` if the cast fails — `x as String` asserts that `x` is a `String` and throws otherwise. Prefer `is` with type promotion over `as` casts because it's safer (no runtime exceptions) and more idiomatic. Use `as` only when you're certain of the type and want to fail fast if you're wrong, or when type promotion doesn't apply.

### Q8: How does type inference work in Dart?
**Answer**: Dart infers types from context when you use `var`, `final`, or omit type annotations. Inference is local — it looks at the initializer, not how the variable is used later. For example, `var x = 42;` infers `int` from the literal. Inference also works with function return types, generic type parameters, and collection literals. The inference is sound — the inferred type is guaranteed to be correct. Use explicit types when inference is unclear or when you want to document intent. Inference makes code concise without sacrificing type safety.



## 🔑 Key Takeaways
- `typedef` creates type aliases for function types and complex types, improving readability
- Functions are first-class objects with structural typing based on signature
- `covariant` allows parameter type narrowing but weakens type safety with runtime checks
- `dynamic` disables type checking; prefer `Object` or `Object?` for better safety
- Type promotion automatically narrows types based on flow analysis (`is` checks, null checks)
- Dart's null safety is sound — non-nullable types are guaranteed to never be `null`
- Generics are reified — type information is available at runtime, unlike Java's type erasure
- Prefer `is` with type promotion over `as` casts for safer, more idiomatic code

## 🔗 Related Topics
- [Day 03: Null Safety](../Week-1-Dart-Fundamentals/Day-03-Null-Safety.md) — foundation of sound null safety
- [Day 05: Functions](../Week-1-Dart-Fundamentals/Day-05-Functions.md) — function types and first-class functions
- [Day 11: Generics](../Week-2-OOP-Collections/Day-11-Generics.md) — generic types and bounded type parameters
- [Day 18: Dart 3 Features](./Day-18-Dart3-Features.md) — patterns and type matching
- [JavaScript TypeScript](../../JavaScript/30-Day-JS-Mastery/Week-3-Advanced/Day-20-TypeScript.md) — compare type systems
