# Day 05: Functions

## 🎯 What You'll Learn

- How to declare functions with explicit return types, named parameters, positional parameters, and default values
- The difference between required positional parameters, optional positional parameters (`[]`), and named parameters (`{}`)
- How to mark named parameters as required with the `required` keyword
- Arrow function syntax (`=>`) for concise single-expression bodies
- First-class functions — storing functions in variables, passing them as arguments, and returning them from other functions
- Anonymous functions (lambdas) and how closures capture variables from their enclosing scope
- Higher-order functions on collections: `map`, `where`, `reduce`, `fold`, and `sort`
- `typedef` for creating reusable function-type aliases
- Recursive functions and the `Function` type

---

## 📚 Core Concepts

### Function Declaration Syntax

Every Dart function has four parts: a **return type**, a **name**, a **parameter list**, and a **body**. The return type comes first and can be any type, including `void` (no return value) or `Future<T>` for async functions. If you omit the return type, Dart infers it, but being explicit is idiomatic and helps the analyzer catch bugs.

```dart
int add(int a, int b) {
  return a + b;
}
```

### Positional Parameters

Positional parameters are the default. They are matched by position when the function is called. They can be **required** (no brackets) or **optional** (wrapped in `[]`). Optional positional parameters must come after required ones and can have default values.

```dart
// 'base' is required; 'exponent' is optional with a default of 2
double power(double base, [int exponent = 2]) {
  return base * exponent; // simplified for illustration
}
power(3.0);       // exponent defaults to 2
power(3.0, 3);    // exponent is 3
```

Optional positional parameters without a default value are nullable (`int? exponent`), so you must handle the `null` case inside the function.

### Named Parameters

Named parameters are declared inside curly braces `{}`. They are called by name at the call site, which makes call sites self-documenting and argument order irrelevant. By default, named parameters are **optional** — callers can omit them. To make a named parameter **required**, annotate it with the `required` keyword.

```dart
void createUser({required String name, int age = 0, String? email}) {
  // 'name' must be provided; 'age' defaults to 0; 'email' is optional nullable
}
createUser(name: 'Alice');
createUser(name: 'Bob', age: 30, email: 'bob@example.com');
```

Named parameters are the idiomatic choice for functions with more than two or three parameters, especially in Flutter widget constructors.

### Default Parameter Values

Both optional positional and optional named parameters can have default values. The default must be a **compile-time constant** — a literal, a `const` constructor call, or a `const` variable. If no default is provided, the parameter's type must be nullable and it defaults to `null`.

```dart
String greet(String name, {String greeting = 'Hello'}) => '$greeting, $name!';
greet('Alice');                    // Hello, Alice!
greet('Bob', greeting: 'Hi');     // Hi, Bob!
```

### Arrow Functions

When a function body is a single expression, you can replace `{ return expr; }` with `=> expr`. This is called an **arrow function** (or fat-arrow syntax). It is purely syntactic sugar — there is no behavioral difference.

```dart
int square(int n) => n * n;
bool isEven(int n) => n % 2 == 0;
```

Arrow functions are especially common as callbacks passed to higher-order methods like `map` and `where`.

### First-Class Functions

In Dart, functions are **first-class citizens** — they are objects of type `Function` and can be:

- Assigned to variables
- Passed as arguments to other functions
- Returned from functions
- Stored in collections

```dart
int Function(int, int) operation = add;  // store a function in a typed variable
operation(3, 4);                         // 7
```

This enables powerful patterns like callbacks, strategy objects, and functional pipelines.

### Anonymous Functions (Lambdas)

An anonymous function (also called a lambda or function literal) is a function without a name. You define it inline, typically to pass as an argument. The syntax is identical to a named function but without the name:

```dart
final double = (int n) => n * 2;          // arrow form
final cube   = (int n) { return n * n * n; }; // block form
```

Anonymous functions are the bread and butter of collection operations and event callbacks.

### Closures — Capturing Variables from Enclosing Scope

A **closure** is a function that captures (closes over) variables from its surrounding lexical scope. The function retains a reference to those variables even after the outer scope has finished executing. This is how Dart implements stateful callbacks and factory patterns.

```dart
Function makeCounter() {
  int count = 0;                  // 'count' lives in makeCounter's scope
  return () {
    count++;                      // the returned function captures 'count'
    return count;
  };
}

final counter = makeCounter();
counter(); // 1
counter(); // 2  — 'count' persists between calls
```

Each call to `makeCounter()` creates an independent `count` variable, so two counters don't share state.

### Higher-Order Functions

A **higher-order function** is any function that takes another function as an argument or returns one. Dart's `Iterable` API is built around higher-order functions:

| Method | What it does |
|--------|-------------|
| `map(f)` | Transforms each element by applying `f`, returns a lazy `Iterable` |
| `where(f)` | Filters elements where `f` returns `true` |
| `reduce(f)` | Combines elements left-to-right using `f`; list must be non-empty |
| `fold(init, f)` | Like `reduce` but starts with an initial value; works on empty lists |
| `sort(compare)` | Sorts a `List` in-place using a comparator function |

These methods accept arrow functions or named functions interchangeably, making collection pipelines concise and readable.

### `typedef` — Function Type Aliases

`typedef` creates a named alias for a function type. This improves readability, enables reuse, and makes complex function signatures manageable.

```dart
typedef Predicate<T> = bool Function(T value);
typedef Transformer<T, R> = R Function(T input);
```

Once defined, you use the alias as a type annotation anywhere you'd use the full function type. `typedef` is especially valuable when the same function signature appears in multiple places — changing the signature in one place updates all usages.

### Recursive Functions

A function that calls itself is **recursive**. Dart supports recursion fully. Every recursive function needs a **base case** that stops the recursion and a **recursive case** that moves toward the base case.

```dart
int factorial(int n) {
  if (n <= 1) return 1;       // base case
  return n * factorial(n - 1); // recursive case
}
```

For deep recursion, be mindful of stack overflow. Dart does not perform tail-call optimization, so iterative solutions are preferable for very large inputs.

### The `Function` Type

`Function` is the top type for all function objects in Dart. You can use it when you want to accept any callable without specifying its signature. For type-safe code, prefer a specific function type or `typedef` over the bare `Function` type.

```dart
void execute(Function callback) => callback();
```

---

## 💻 Code Examples

### Example 1: All Parameter Types

```dart
// Dart 3.x — sound null safety

// Required positional + optional positional + named required + named optional
String formatMessage(
  String sender,                  // required positional
  String text, [                  // required positional (last before optional block)
  int? priority,                  // optional positional — nullable, no default
]) {
  final p = priority != null ? ' [P$priority]' : '';
  return '$sender: $text$p';
}

// Named parameters: 'to' is required, 'subject' has a default, 'cc' is optional nullable
String composeEmail({
  required String to,
  String subject = '(no subject)',
  String? cc,
}) {
  final ccLine = cc != null ? '\nCC: $cc' : '';
  return 'To: $to\nSubject: $subject$ccLine';
}

void main() {
  // --- Optional positional ---
  print(formatMessage('Alice', 'Hello'));          // Alice: Hello
  print(formatMessage('Bob', 'Urgent!', 1));       // Bob: Urgent! [P1]

  // --- Named parameters ---
  // 'to' is required; 'subject' and 'cc' are optional
  print(composeEmail(to: 'alice@example.com'));
  // To: alice@example.com
  // Subject: (no subject)

  print(composeEmail(
    to: 'bob@example.com',
    subject: 'Meeting',
    cc: 'carol@example.com',
  ));
  // To: bob@example.com
  // Subject: Meeting
  // CC: carol@example.com

  // --- Arrow function ---
  // Single-expression body; identical behavior to a block body with 'return'
  int double_(int n) => n * 2;
  print(double_(7)); // 14

  // --- Default values must be compile-time constants ---
  String tag(String text, {String wrapper = 'div'}) => '<$wrapper>$text</$wrapper>';
  print(tag('Hello'));              // <div>Hello</div>
  print(tag('Hello', wrapper: 'p')); // <p>Hello</p>
}
```

### Example 2: First-Class Functions, Anonymous Functions, and Closures

```dart
// Dart 3.x — sound null safety

// --- First-class functions: store in a variable ---
int add(int a, int b) => a + b;
int subtract(int a, int b) => a - b;

// A function that accepts another function as an argument (higher-order)
int applyOperation(int x, int y, int Function(int, int) op) => op(x, y);

// --- Closure factory: each call creates an independent captured variable ---
// Returns a function that remembers its own 'step' and 'count'
Function makeCounter({int step = 1}) {
  int count = 0;                    // captured by the returned closure
  return () {
    count += step;                  // 'count' and 'step' are both captured
    return count;
  };
}

// --- Closure capturing a loop variable ---
// Demonstrates that each closure captures its own copy of the loop variable
List<Function> makeAdders(List<int> values) {
  return [
    for (final v in values) (int x) => x + v,
    // Each iteration creates a new 'v' binding — no shared-variable bug
  ];
}

void main() {
  // --- Functions as values ---
  int Function(int, int) op = add;
  print(op(10, 3));   // 13

  op = subtract;      // reassign to a different function
  print(op(10, 3));   // 7

  // --- Passing functions as arguments ---
  print(applyOperation(10, 3, add));       // 13
  print(applyOperation(10, 3, subtract));  // 7

  // --- Anonymous function (lambda) passed inline ---
  print(applyOperation(10, 3, (a, b) => a * b)); // 30

  // --- Closures with independent state ---
  final counterBy1 = makeCounter();
  final counterBy5 = makeCounter(step: 5);

  print(counterBy1()); // 1
  print(counterBy1()); // 2
  print(counterBy5()); // 5  — independent from counterBy1
  print(counterBy5()); // 10

  // --- Closures capturing loop variables correctly ---
  final adders = makeAdders([1, 2, 3]);
  print(adders[0](10)); // 11  (10 + 1)
  print(adders[1](10)); // 12  (10 + 2)
  print(adders[2](10)); // 13  (10 + 3)

  // --- Returning a function from a function ---
  // 'multiplier' returns a closure that remembers 'factor'
  int Function(int) multiplier(int factor) => (int n) => n * factor;

  final triple = multiplier(3);
  final quadruple = multiplier(4);
  print(triple(7));    // 21
  print(quadruple(7)); // 28
}
```

### Example 3: Higher-Order Functions with Collections and `typedef`

```dart
// Dart 3.x — sound null safety

// --- typedef: name a reusable function type ---
typedef Predicate<T> = bool Function(T value);
typedef Transformer<T, R> = R Function(T input);
typedef Comparator<T> = int Function(T a, T b);

// A generic filter function that uses our Predicate typedef
List<T> filter<T>(List<T> items, Predicate<T> test) =>
    items.where(test).toList();

// A generic transform function that uses our Transformer typedef
List<R> transform<T, R>(List<T> items, Transformer<T, R> convert) =>
    items.map(convert).toList();

void main() {
  final numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  final words = ['banana', 'apple', 'cherry', 'date', 'elderberry'];

  // --- map: transform each element ---
  // Returns a lazy Iterable; call .toList() to materialise it
  final squares = numbers.map((n) => n * n).toList();
  print(squares); // [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

  // --- where: filter elements ---
  final evens = numbers.where((n) => n.isEven).toList();
  print(evens); // [2, 4, 6, 8, 10]

  // --- reduce: combine left-to-right (list must be non-empty) ---
  final sum = numbers.reduce((acc, n) => acc + n);
  print(sum); // 55

  // --- fold: like reduce but with an explicit initial value ---
  // Safe on empty lists; here we build a comma-separated string
  final csv = numbers.fold<String>(
    '',
    (acc, n) => acc.isEmpty ? '$n' : '$acc,$n',
  );
  print(csv); // 1,2,3,4,5,6,7,8,9,10

  // --- sort: sorts in-place using a comparator ---
  // Comparator returns negative / zero / positive (like C's qsort)
  final sortedByLength = List<String>.from(words)
    ..sort((a, b) => a.length.compareTo(b.length));
  print(sortedByLength); // [date, apple, banana, cherry, elderberry]

  // --- Chaining higher-order methods ---
  // Get the sum of squares of even numbers
  final sumOfEvenSquares = numbers
      .where((n) => n.isEven)          // [2, 4, 6, 8, 10]
      .map((n) => n * n)               // [4, 16, 36, 64, 100]
      .fold(0, (acc, n) => acc + n);   // 220
  print(sumOfEvenSquares); // 220

  // --- Using typedef-backed functions ---
  final Predicate<int> isOdd = (n) => n % 2 != 0;
  final Transformer<String, int> wordLength = (s) => s.length;

  print(filter(numbers, isOdd));          // [1, 3, 5, 7, 9]
  print(transform(words, wordLength));    // [6, 5, 6, 4, 10]

  // --- Recursive function: factorial ---
  int factorial(int n) => n <= 1 ? 1 : n * factorial(n - 1);
  print(factorial(6)); // 720

  // --- Function stored in a Map (functions as values in a collection) ---
  final Map<String, int Function(int, int)> ops = {
    'add': (a, b) => a + b,
    'mul': (a, b) => a * b,
    'max': (a, b) => a > b ? a : b,
  };
  print(ops['add']!(10, 5)); // 15
  print(ops['mul']!(10, 5)); // 50
  print(ops['max']!(10, 5)); // 10
}
```

---

## ⚠️ Common Pitfalls

- **Mixing positional and named parameters incorrectly**: You cannot mix optional positional `[]` and named `{}` parameters in the same function signature — Dart only allows one style of optional parameters per function. If you need both required positional and optional named parameters, put the required positionals first and use `{}` for the optional ones.

- **Forgetting `required` on non-nullable named parameters**: If a named parameter has a non-nullable type and no default value, you *must* mark it `required`. Omitting `required` is a compile-time error in sound null safety. A common mistake is writing `{String name}` and expecting callers to always provide it — the analyzer will reject this because `name` could be absent.

- **Closure variable capture in classic `for` loops**: In a classic `for (int i = 0; ...)` loop, all closures created inside the loop share the *same* `i` variable. By the time the closures run, `i` has its final value. Use `for-in` (which creates a fresh binding per iteration) or capture the value explicitly with `final captured = i;` inside the loop body.

- **`reduce` on an empty list throws**: `Iterable.reduce` throws a `StateError` if the list is empty because there is no initial value to return. Use `fold` with an explicit initial value when the list might be empty.

- **Arrow functions can only hold a single expression**: `=> expr` is not a shorthand for a block — you cannot put multiple statements after `=>`. If you need more than one statement, use a block body `{ ... }`. A common mistake is writing `=> { doA(); doB(); }`, which creates an anonymous `Map` literal, not a block.

---

## ❓ Interview Questions

### Q1: What is the difference between positional and named parameters in Dart?

**Answer**: Positional parameters are matched by their position in the argument list — the first argument maps to the first parameter, the second to the second, and so on. They can be required (no brackets) or optional (wrapped in `[]`). Named parameters are declared inside `{}` and are called by name at the call site (`createUser(name: 'Alice')`), making argument order irrelevant. Named parameters are optional by default; adding the `required` keyword makes them mandatory. Named parameters are the idiomatic choice for functions with many arguments (especially Flutter widget constructors) because they make call sites self-documenting and reduce the risk of passing arguments in the wrong order.

### Q2: What is a closure in Dart and how does variable capture work?

**Answer**: A closure is a function that captures variables from its enclosing lexical scope and retains access to them even after the outer scope has finished executing. In Dart, every anonymous function (and named function defined inside another function) is a closure. Variable capture is by **reference**, not by value — the closure holds a reference to the variable itself, so mutations to the variable are visible inside the closure and vice versa. This means that if multiple closures capture the same variable, they all see the same mutations. A practical consequence is the classic loop-closure bug: closures created inside a classic `for (int i = 0; ...)` loop all share the same `i` reference, so they all see `i`'s final value when invoked. Using `for-in` or capturing with `final captured = i` inside the loop body avoids this.

### Q3: What is the difference between `required` named parameters and optional named parameters?

**Answer**: An optional named parameter can be omitted by the caller — if omitted, it takes its default value (if one is provided) or `null` (if the type is nullable). A `required` named parameter *must* be provided by every caller; omitting it is a **compile-time error**. The `required` keyword was introduced as part of Dart's sound null safety system to allow named parameters with non-nullable types that have no sensible default. Before null safety, all named parameters were optional and could silently be `null`. Now, if you want a named parameter that is non-nullable and has no default, you annotate it with `required`, and the analyzer enforces that callers always supply it.

### Q4: How are functions first-class citizens in Dart?

**Answer**: In Dart, functions are objects — instances of the `Function` class — and can be used anywhere any other object can be used. Specifically, you can assign a function to a variable (`int Function(int) f = square;`), pass a function as an argument to another function (`list.sort(myComparator)`), return a function from a function (`Function makeAdder(int n) => (int x) => x + n;`), and store functions in collections (`Map<String, Function> handlers = {...}`). This enables functional programming patterns such as callbacks, strategy objects, higher-order collection operations (`map`, `where`, `fold`), and function composition. The `typedef` keyword lets you give a function type a name, making these patterns more readable and type-safe.

### Q5: What is a `typedef` in Dart and when would you use one?

**Answer**: `typedef` creates a named alias for a function type (or, since Dart 2.13, for any type). For example, `typedef Predicate<T> = bool Function(T value);` gives the name `Predicate<T>` to the function type `bool Function(T value)`. You would use `typedef` when the same function signature appears in multiple places (avoiding repetition and making a single change update all usages), when a function type is complex enough that inlining it hurts readability, or when you want to document the *intent* of a function type beyond its mechanical signature. In Flutter codebases, `typedef` is common for callback types like `typedef ValueChanged<T> = void Function(T value);`, which makes widget APIs self-documenting.

---

## 🔑 Key Takeaways

- Dart has three parameter styles: required positional, optional positional (`[]`), and named (`{}`). You cannot mix `[]` and `{}` in the same function.
- Named parameters are optional by default; use `required` to enforce that callers must supply a non-nullable named parameter.
- Arrow syntax (`=>`) is syntactic sugar for a single-expression function body — it does not change behavior, only conciseness.
- Functions are first-class objects in Dart: they can be stored in variables, passed as arguments, returned from functions, and stored in collections.
- Closures capture variables by reference from their enclosing scope; be aware of shared-variable bugs in classic `for` loops.
- Higher-order collection methods (`map`, `where`, `fold`, `reduce`, `sort`) are the idiomatic way to process collections — prefer them over manual loops for transformations and aggregations.
- `typedef` names a function type, improving readability and enabling reuse across a codebase.

---

## 🔗 Related Topics

- [Day 04: Control Flow](./Day-04-Control-Flow.md) — `forEach` and loop callbacks are where anonymous functions first appear
- [Day 06: Collections](./Day-06-Collections.md) — `List`, `Set`, and `Map` are the primary targets of higher-order functions
- [Day 12: Advanced Collections](../Week-2-OOP-Collections/Day-12-Advanced-Collections.md) — deep dive into `Iterable`, lazy evaluation, and chaining
- [JavaScript Closures — Day 07](../../JavaScript/30-Day-JS-Mastery/Week-1-Core-Foundations/Day-07-Closures.md) — closures work the same way in JS; useful for cross-language comparison
- [Dart Cheatsheet](../Cheatsheets/Dart-Cheatsheet.md) — quick-reference for all function syntax forms
