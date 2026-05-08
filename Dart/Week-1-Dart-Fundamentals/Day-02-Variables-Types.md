# Day 02: Variables & Types

## 🎯 What You'll Learn

- The difference between `var`, `final`, and `const` and when to use each
- How Dart's type inference works and when to prefer explicit annotations
- All of Dart's built-in types: `int`, `double`, `num`, `String`, `bool`, `dynamic`, `Object`
- Collection types at a glance: `List`, `Map`, `Set`, `Symbol`, `Runes`
- String features: interpolation, raw strings, multi-line strings, and common methods
- Type conversion between numeric and string types
- The `late` keyword for deferred initialization of non-nullable variables
- How `dynamic` and `Object` differ and why that matters for type safety

---

## 📚 Core Concepts

### Variable Declarations: `var`, `final`, and `const`

Dart gives you three ways to declare a variable, and choosing the right one communicates intent clearly to both the compiler and your teammates.

**`var`** declares a variable whose type is inferred from the initializer. Once the type is inferred, it is fixed — you cannot later assign a value of a different type. The variable itself is reassignable.

```dart
var name = 'Alice'; // inferred as String
name = 'Bob';       // fine — same type
// name = 42;       // compile error — int is not String
```

**`final`** declares a variable that can be assigned exactly once. The assignment happens at runtime, so the value can come from a function call, a constructor, or any runtime expression. After the first assignment the variable is immutable.

```dart
final now = DateTime.now(); // assigned once at runtime
// now = DateTime.now();    // compile error — final variable
```

**`const`** declares a compile-time constant. The value must be fully known at compile time — no function calls, no `DateTime.now()`, no user input. `const` values are deeply immutable and are canonicalized by the compiler (two identical `const` objects share the same memory location).

```dart
const pi = 3.14159;
const appName = 'MyApp';
```

Use `const` whenever the value is truly fixed at compile time (magic numbers, string literals, configuration). Use `final` for values computed once at runtime. Use `var` (or an explicit type) for mutable variables.

### Explicit Type Annotations vs Type Inference

Dart supports both styles. Type inference keeps code concise; explicit annotations add clarity in public APIs and complex expressions.

```dart
var score = 100;          // inferred: int
int score2 = 100;         // explicit: int — identical at runtime
String greeting = 'Hi';   // explicit annotation
```

Prefer explicit annotations for function signatures, class fields, and anywhere the inferred type might surprise a reader. Inside function bodies, `var` is idiomatic when the type is obvious from the right-hand side.

### Built-in Numeric Types: `int`, `double`, and `num`

`int` represents whole numbers (64-bit on native, arbitrary precision on the web). `double` represents 64-bit IEEE 754 floating-point numbers. `num` is the abstract supertype of both — use it when a function should accept either integers or doubles.

```dart
int age = 30;
double price = 9.99;
num quantity = 3;     // can hold int or double
quantity = 3.5;       // still valid
```

### `String`

Dart strings are sequences of UTF-16 code units. You can use single or double quotes interchangeably. String interpolation uses `$variable` or `${expression}`. Raw strings (prefixed with `r`) treat backslashes literally. Multi-line strings use triple quotes (`'''` or `"""`).

```dart
var s1 = 'hello';
var s2 = "world";
var path = r'C:\Users\dart'; // raw string — backslash is literal
var poem = '''
  Roses are red,
  Violets are blue.
''';
var msg = 'Hello, $s1! 2 + 2 = ${2 + 2}';
```

### `bool`

`bool` has exactly two values: `true` and `false`. Dart does not perform implicit boolean conversions — `if (1)` is a compile error, unlike JavaScript.

### `dynamic`

`dynamic` opts out of Dart's static type system entirely. Any operation on a `dynamic` value is allowed at compile time; errors surface only at runtime. Use it sparingly — it defeats the purpose of Dart's sound type system and makes refactoring harder.

```dart
dynamic anything = 42;
anything = 'now a string'; // no compile error
anything.nonExistentMethod(); // compiles fine, crashes at runtime
```

### `Object` and `Object?`

`Object` is the root of Dart's non-nullable type hierarchy. Every non-nullable Dart type is a subtype of `Object`. Because it is non-nullable, you cannot assign `null` to an `Object` variable. `Object?` (with the `?`) extends the hierarchy to include `null`.

The key difference from `dynamic`: `Object` still enforces static type checking. You can only call methods defined on `Object` itself (like `toString()`, `hashCode`, `==`) without a cast.

```dart
Object value = 'hello';
// value.length; // compile error — Object has no .length
(value as String).length; // OK after explicit cast
```

### Type Conversion

Dart does not implicitly convert between types. Use explicit conversion methods:

```dart
int n = int.parse('42');
double d = double.parse('3.14');
String s = 42.toString();
int truncated = 3.9.toInt();   // 3 — truncates, does not round
double asDouble = 5.toDouble(); // 5.0
```

### The `late` Keyword

`late` defers the initialization of a non-nullable variable. The variable must be assigned before it is first read, or a `LateInitializationError` is thrown at runtime. Common use cases: fields initialized in a method rather than the constructor, and circular references.

```dart
late String description; // not yet initialized
description = 'Assigned later'; // must happen before first read
print(description); // safe
```

### Collection Types at a Glance

Dart has three core collection types built into the language:

- **`List<E>`** — ordered, indexed, allows duplicates. Literal: `[1, 2, 3]`.
- **`Set<E>`** — unordered, no duplicates. Literal: `{1, 2, 3}`.
- **`Map<K, V>`** — key-value pairs. Literal: `{'a': 1, 'b': 2}`.

`Symbol` represents an operator or identifier in Dart source code (used in reflection). `Runes` expose the Unicode code points of a string. Both are rarely needed in everyday code but are part of the type system.

---

## 💻 Code Examples

### Example 1: `var`, `final`, and `const` with Type Inference

```dart
void main() {
  // var — type inferred as String, reassignable
  var city = 'London';
  city = 'Paris'; // OK
  // city = 42;   // compile error: int is not String

  // final — assigned once at runtime
  final launchTime = DateTime.now(); // runtime value
  // launchTime = DateTime.now();    // compile error

  // const — compile-time constant, deeply immutable
  const double taxRate = 0.2;
  const List<String> weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
  // weekdays.add('Sat'); // compile error: unmodifiable list

  // Explicit type annotation — identical runtime behaviour to var
  String country = 'Germany';
  int population = 84_000_000; // underscores improve readability

  print('$city, $country — pop: $population');
  print('Tax rate: $taxRate');
  print('Weekdays: $weekdays');
  print('Launched at: $launchTime');
}
```

### Example 2: Built-in Types, `is` Checks, and `runtimeType`

```dart
void main() {
  // Numeric types
  int age = 28;
  double height = 1.75;
  num score = 95; // num accepts both int and double
  score = 95.5;   // still valid

  // String
  String name = 'Dart';
  bool isAwesome = true;

  // dynamic — type checking deferred to runtime
  dynamic flexible = 'hello';
  flexible = 100; // no compile error

  // Object — root non-nullable type
  Object obj = 42;
  // obj.isEven; // compile error — Object has no .isEven

  // Collections
  List<int> primes = [2, 3, 5, 7, 11];
  Set<String> tags = {'dart', 'flutter', 'mobile'};
  Map<String, int> scores = {'Alice': 90, 'Bob': 85};

  // Symbol and Runes (rarely used directly)
  Symbol sym = #mySymbol;
  Runes runes = Runes('\u{1F600}'); // 😀

  // Runtime type inspection
  print(age.runtimeType);       // int
  print(height.runtimeType);    // double
  print(name.runtimeType);      // String
  print(flexible.runtimeType);  // int (after reassignment)

  // 'is' operator for type checking
  print(age is int);            // true
  print(score is num);          // true
  print(score is double);       // true (score holds 95.5)
  print(obj is Object);         // true
  print(null is Object);        // false — Object is non-nullable
  print(null is Object?);       // true

  // Type conversion
  String parsed = 42.toString();
  int fromString = int.parse('123');
  double asDouble = 7.toDouble();
  int truncated = 3.99.toInt(); // 3, not 4

  print('$parsed, $fromString, $asDouble, $truncated');
}
```

### Example 3: String Operations — Interpolation, Raw Strings, Multi-line, Common Methods

```dart
void main() {
  // Basic interpolation
  String firstName = 'Ada';
  String lastName = 'Lovelace';
  print('Full name: $firstName $lastName');
  print('Name length: ${firstName.length + lastName.length}');

  // Single vs double quotes — interchangeable
  var s1 = 'It\'s a beautiful day'; // escaped apostrophe
  var s2 = "It's a beautiful day";  // no escape needed with double quotes
  print(s1 == s2); // true

  // Raw strings — backslashes are literal
  var windowsPath = r'C:\Users\Ada\Documents';
  var regexPattern = r'\d+\.\d+'; // no need to double-escape
  print(windowsPath);
  print(regexPattern);

  // Multi-line strings
  var haiku = '''
Autumn moonlight—
a worm digs silently
into the chestnut.
  ''';
  print(haiku);

  // Common String methods
  var text = '  Hello, Dart!  ';
  print(text.trim());                    // 'Hello, Dart!'
  print(text.trim().toLowerCase());      // 'hello, dart!'
  print(text.trim().toUpperCase());      // 'HELLO, DART!'
  print(text.trim().contains('Dart'));   // true
  print(text.trim().replaceAll('Dart', 'World')); // 'Hello, World!'
  print(text.trim().split(', '));        // [Hello, Dart!]
  print('Dart'.padLeft(8));             // '    Dart'
  print('42'.padLeft(5, '0'));          // '00042'

  // String concatenation — prefer interpolation over +
  var greeting = 'Hello' + ', ' + 'world!'; // works but verbose
  var betterGreeting = 'Hello, ${'world'}!'; // idiomatic

  // Checking content
  print('flutter'.startsWith('flu')); // true
  print('flutter'.endsWith('ter'));   // true
  print('flutter'.indexOf('tt'));     // 2
  print('flutter'.substring(2, 5));   // 'utt'
}
```

---

## ⚠️ Common Pitfalls

- **Confusing `const` and `final`**: `final` allows runtime values (`DateTime.now()`, constructor arguments); `const` requires compile-time constants. Trying to use a runtime value with `const` is a compile error.

- **Using `dynamic` too broadly**: `dynamic` silences the type checker, so typos in method names and wrong argument types become runtime crashes instead of compile errors. Prefer `Object?` when you genuinely need to accept any value — it still enforces that you check the type before calling type-specific methods.

- **Forgetting that `int` and `double` don't auto-convert**: `double result = 5 / 2;` gives `2.5` (Dart's `/` always returns `double`), but `int result = 5 / 2;` is a compile error. Use `~/` for integer division: `5 ~/ 2 == 2`.

- **`late` without initialization**: Declaring `late String name;` and reading `name` before assigning it throws `LateInitializationError` at runtime — there is no compile-time safety net once you use `late`.

- **Empty set literal `{}` is a `Map`, not a `Set`**: `var s = {};` infers `Map<dynamic, dynamic>`. To create an empty `Set`, write `var s = <String>{}` or `Set<String> s = {}`.

---

## ❓ Interview Questions

### Q1: What is the difference between `var`, `final`, and `const` in Dart?

**Answer**: `var` declares a type-inferred, mutable variable — the type is locked at inference time but the value can be reassigned. `final` declares a variable that can be assigned exactly once; the assignment happens at runtime, so the value can be the result of a function call or constructor. `const` declares a compile-time constant whose value must be fully known before the program runs; `const` objects are deeply immutable and canonicalized by the compiler, meaning two identical `const` literals share the same object in memory. The practical rule: reach for `const` first, fall back to `final` if the value is only known at runtime, and use `var` (or an explicit type) only when the variable genuinely needs to change.

### Q2: What is the difference between `dynamic` and `Object` in Dart?

**Answer**: Both can hold a value of any type, but they behave very differently under the type checker. `Object` is the root of Dart's non-nullable type hierarchy and still participates in static type checking — you can only call methods defined on `Object` (like `toString()` and `hashCode`) without a cast, so the compiler catches mistakes at compile time. `dynamic` completely opts out of static analysis; any method call or property access on a `dynamic` value is allowed at compile time and only checked at runtime, which means bugs surface as runtime exceptions rather than compile errors. Prefer `Object?` over `dynamic` when you need to accept any value — it forces you to perform an `is` check or cast before using type-specific members, keeping the code safe.

### Q3: Why does Dart have both `int` and `num`? When would you use `num`?

**Answer**: `int` and `double` are distinct types in Dart's type hierarchy, and `num` is their common abstract supertype. You use `num` when you want a function or variable to accept either integers or doubles without forcing the caller to convert. For example, a `calculateArea(num width, num height)` function works naturally with both `int` and `double` arguments. In practice, prefer the more specific `int` or `double` when you know which you need — `num` is most useful in generic utility code, mathematical libraries, or when reading values from JSON where the numeric type may vary.

### Q4: What is type inference in Dart and how does it work?

**Answer**: Type inference is the compiler's ability to deduce the static type of a variable or expression without an explicit annotation. When you write `var x = 42`, the Dart analyzer examines the right-hand side (`42`, an `int` literal) and assigns `x` the type `int` — from that point on, `x` behaves exactly as if you had written `int x = 42`. Inference also works for generic type arguments: `var names = <String>[]` infers `List<String>`, and `var map = {'a': 1}` infers `Map<String, int>`. The inferred type is fixed at the point of declaration; you cannot later assign a value of a different type to a `var` variable. Dart's inference is local (per expression/statement) and does not perform whole-program inference, which keeps compile times fast and error messages predictable.

### Q5: What is the `late` keyword and when should you use it?

**Answer**: `late` tells the Dart compiler "I promise this non-nullable variable will be initialized before it is first read — trust me." Without `late`, every non-nullable variable must be initialized at the point of declaration or in the constructor initializer list. `late` is useful in three main scenarios: (1) fields that are expensive to compute and should be lazily initialized on first access (`late final _cache = _buildCache()`), (2) fields that are initialized in a lifecycle method rather than the constructor (common in Flutter's `State.initState()`), and (3) circular references where two objects need to reference each other. The trade-off is that `late` moves the safety guarantee from compile time to runtime — if you read the variable before assigning it, you get a `LateInitializationError`.

---

## 🔑 Key Takeaways

- Use `const` for compile-time constants, `final` for runtime-assigned immutable values, and `var`/explicit type for mutable variables.
- Dart's type inference is sound and local — once a type is inferred, it cannot change.
- `num` is the supertype of `int` and `double`; use it when a function should accept either.
- `dynamic` disables static type checking entirely — prefer `Object?` when you need to accept any value safely.
- `Object` is the root of the non-nullable type hierarchy; `Object?` extends it to include `null`.
- String interpolation (`$var`, `${expr}`), raw strings (`r'...'`), and multi-line strings (`'''...'''`) are all first-class language features.
- Dart never implicitly converts between types — use `int.parse()`, `.toString()`, `.toInt()`, `.toDouble()` explicitly.
- `late` defers initialization of non-nullable variables but shifts the safety check to runtime.

---

## 🔗 Related Topics

- [Day 01: Dart Overview & Setup](./Day-01-Dart-Overview-Setup.md) — SDK installation, `dart` CLI, and the `main()` entry point
- [Day 03: Null Safety](./Day-03-Null-Safety.md) — nullable types (`?`), `late`, `!` operator, and null-aware operators
- [Dart Cheatsheet](../Cheatsheets/Dart-Cheatsheet.md) — quick-reference for all variable and type syntax
