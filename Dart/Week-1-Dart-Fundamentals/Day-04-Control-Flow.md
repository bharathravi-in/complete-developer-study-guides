# Day 04: Control Flow

## 🎯 What You'll Learn

- How to branch execution with `if`, `else if`, and `else`
- Dart 3's pattern-matching `if` (brief intro — deep dive on Day 18)
- Classic `switch` statements: cases, `break`, `default`, and Dart's strict fall-through rules
- Dart 3 enhanced switch expressions: exhaustive matching, guard clauses (`when`), and returning values inline
- All loop forms: C-style `for`, `for-in` over iterables, `forEach`, `while`, and `do-while`
- `break` and `continue` — with and without labels — for fine-grained loop control
- Labeled loops for breaking out of nested loops in one step
- The ternary operator `condition ? a : b` for concise inline branching
- `assert` for debug-mode invariant checking

---

## 📚 Core Concepts

### `if`, `else if`, and `else`

The most fundamental branching construct in Dart works exactly as you'd expect from any C-family language. The condition must evaluate to a `bool` — Dart does **not** treat `0`, `null`, or empty strings as falsy, so you must be explicit.

```dart
int score = 72;
if (score >= 90) {
  print('A');
} else if (score >= 80) {
  print('B');
} else if (score >= 70) {
  print('C');
} else {
  print('F');
}
```

Dart 3 introduced **pattern-matching `if` statements**, letting you test a value's shape and bind variables in one step:

```dart
Object value = 42;
if (value case int n when n > 0) {
  print('Positive int: $n');
}
```

This is a brief taste — Day 18 covers patterns exhaustively.

### Ternary Operator

For simple two-branch expressions, the ternary operator keeps code concise:

```dart
String label = score >= 60 ? 'Pass' : 'Fail';
```

Avoid nesting ternaries — they hurt readability fast.

### Classic `switch` Statement

Dart's `switch` statement matches a value against a series of `case` labels. Unlike C or Java, **Dart does not allow implicit fall-through** between non-empty cases. If you want to fall through intentionally, you must use `continue` with a label pointing to the next case. Every non-empty case must end with `break`, `return`, `throw`, or `continue <label>`.

```dart
String day = 'Monday';
switch (day) {
  case 'Saturday':
  case 'Sunday':           // empty cases DO fall through — this is allowed
    print('Weekend');
    break;
  case 'Monday':
    print('Start of work week');
    break;
  default:
    print('Midweek');
}
```

The `default` clause is optional but recommended when the matched type is not exhaustively covered.

### Dart 3 Enhanced Switch Expressions

Dart 3 (released with Dart SDK 3.0) introduced **switch expressions** — a more powerful form that:

- Returns a value directly (usable anywhere an expression is expected)
- Requires **exhaustive** matching (the compiler enforces that all possible values are handled)
- Supports **guard clauses** with `when` to add extra conditions to a case
- Uses `=>` instead of `:` and omits `break`

```dart
String classify(int n) => switch (n) {
  < 0        => 'negative',
  0          => 'zero',
  int x when x.isEven => 'positive even',
  _          => 'positive odd',   // _ is the wildcard / default
};
```

Switch expressions shine when working with sealed classes and enums because the compiler can verify exhaustiveness at compile time.

### `for` Loops

Dart supports three loop styles for iteration:

**C-style `for`** — use when you need an index:
```dart
for (int i = 0; i < 5; i++) { ... }
```

**`for-in`** — use when you just need each element of an `Iterable`:
```dart
for (final item in myList) { ... }
```

**`forEach`** — a higher-order method on `Iterable`; accepts a callback:
```dart
myList.forEach((item) => print(item));
```

Prefer `for-in` over `forEach` when you need `break` or `continue` — those keywords don't work inside a `forEach` callback.

### `while` and `do-while`

`while` checks the condition **before** each iteration; `do-while` checks it **after**, guaranteeing at least one execution:

```dart
int count = 0;
while (count < 3) {
  print(count++);
}

int attempts = 0;
do {
  attempts++;
} while (attempts < 3);
```

### `break` and `continue`

- `break` exits the nearest enclosing loop or `switch` immediately.
- `continue` skips the rest of the current iteration and jumps to the next one.

Both work in `for`, `for-in`, `while`, and `do-while` loops.

### Labeled Loops

When you have nested loops and need to `break` or `continue` an **outer** loop from inside an inner one, attach a label to the outer loop:

```dart
outer:
for (int i = 0; i < 3; i++) {
  for (int j = 0; j < 3; j++) {
    if (j == 1) continue outer;  // skip rest of inner, advance outer
    if (i == 2) break outer;     // exit both loops entirely
    print('$i,$j');
  }
}
```

Labels are rarely needed in everyday code, but they're the clean alternative to boolean flags when escaping nested loops.

### `assert`

`assert(condition, [message])` throws an `AssertionError` if `condition` is `false` — but **only in debug mode**. In production (compiled with `dart compile` or Flutter release builds), all `assert` calls are stripped out entirely. Use them to document and enforce invariants during development:

```dart
int divide(int a, int b) {
  assert(b != 0, 'Divisor must not be zero');
  return a ~/ b;
}
```

---

## 💻 Code Examples

### Example 1: `if/else`, Ternary, and `assert`

```dart
void main() {
  // --- if / else if / else ---
  int temperature = 22;

  if (temperature < 0) {
    print('Freezing');
  } else if (temperature < 15) {
    print('Cold');
  } else if (temperature < 25) {
    print('Comfortable');   // this branch runs
  } else {
    print('Hot');
  }

  // --- Ternary operator ---
  // Concise two-branch expression; avoid nesting
  String weather = temperature > 30 ? 'Hot' : 'Not hot';
  print(weather); // Not hot

  // --- assert (active only in debug mode) ---
  // Throws AssertionError in debug mode if condition is false;
  // completely removed in release/production builds.
  int age = 25;
  assert(age >= 0, 'Age cannot be negative');
  print('Age is valid: $age');

  // --- Dart 3 pattern-matching if (brief intro) ---
  Object value = -7;
  if (value case int n when n < 0) {
    // 'case int n' checks the type AND binds the value to n
    print('Negative integer: $n'); // prints: Negative integer: -7
  }
}
```

### Example 2: Classic `switch` Statement vs Dart 3 Switch Expression

```dart
// Dart 3.x — sound null safety

// --- Classic switch statement ---
String describeDay(String day) {
  switch (day) {
    case 'Saturday':
    case 'Sunday':
      // Two empty cases share one body — this fall-through IS allowed
      return 'Weekend';
    case 'Monday':
      return 'Start of work week';
    case 'Friday':
      return 'Almost there!';
    default:
      return 'Midweek';
  }
}

// --- Dart 3 switch expression ---
// Returns a value directly; exhaustiveness is checked at compile time.
// Guard clauses (when) add extra conditions beyond the pattern.
String classifyNumber(int n) => switch (n) {
  0          => 'zero',
  < 0        => 'negative',                        // relational pattern
  int x when x % 2 == 0 => 'positive even',        // guard clause
  _          => 'positive odd',                    // wildcard (default)
};

// --- Switch expression on an enum (exhaustive by default) ---
enum TrafficLight { red, yellow, green }

String action(TrafficLight light) => switch (light) {
  TrafficLight.red    => 'Stop',
  TrafficLight.yellow => 'Caution',
  TrafficLight.green  => 'Go',
  // No default needed — compiler verifies all enum values are covered
};

void main() {
  print(describeDay('Saturday'));   // Weekend
  print(describeDay('Wednesday'));  // Midweek

  print(classifyNumber(0));   // zero
  print(classifyNumber(-3));  // negative
  print(classifyNumber(4));   // positive even
  print(classifyNumber(7));   // positive odd

  print(action(TrafficLight.red));   // Stop
  print(action(TrafficLight.green)); // Go
}
```

### Example 3: All Loop Types with `break`, `continue`, and Labels

```dart
void main() {
  // --- C-style for loop ---
  print('C-style for:');
  for (int i = 0; i < 5; i++) {
    if (i == 3) break;       // exits loop when i reaches 3
    print(i);                // prints 0, 1, 2
  }

  // --- for-in loop over an Iterable ---
  print('\nfor-in:');
  final fruits = ['apple', 'banana', 'cherry', 'date'];
  for (final fruit in fruits) {
    if (fruit == 'cherry') continue;  // skip 'cherry', keep going
    print(fruit);                     // apple, banana, date
  }

  // --- forEach (higher-order method) ---
  // Note: break/continue do NOT work inside forEach callbacks
  print('\nforEach:');
  fruits.forEach((f) => print(f.toUpperCase()));

  // --- while loop ---
  print('\nwhile:');
  int n = 1;
  while (n <= 16) {
    n *= 2;   // doubles each iteration: 2, 4, 8, 16, 32 — stops when > 16
  }
  print(n); // 32

  // --- do-while loop ---
  // Body always executes at least once before condition is checked
  print('\ndo-while:');
  int attempts = 0;
  do {
    attempts++;
    print('Attempt $attempts');
  } while (attempts < 3); // prints Attempt 1, 2, 3

  // --- Labeled loops ---
  // 'outer' label lets us target the outer loop from inside the inner one
  print('\nLabeled loops:');
  outer:
  for (int row = 0; row < 4; row++) {
    for (int col = 0; col < 4; col++) {
      if (col == 2) continue outer;  // skip columns 2+ for every row
      if (row == 3) break outer;     // stop everything when row reaches 3
      print('($row, $col)');
      // Prints: (0,0) (0,1) (1,0) (1,1) (2,0) (2,1)
    }
  }
}
```

---

## ⚠️ Common Pitfalls

- **Implicit fall-through in `switch`**: Dart forbids it in non-empty cases. If you write two consecutive non-empty cases without a `break`/`return`/`throw`, the analyzer reports a compile-time error. Use empty cases (no body) for intentional fall-through, or use `continue <label>` for explicit jumps.

- **`break`/`continue` inside `forEach`**: These keywords only work in actual loop constructs (`for`, `while`, `do-while`). Inside a `forEach` callback they refer to the anonymous function, not the loop — the compiler will reject them. Switch to a `for-in` loop if you need early exit.

- **Non-exhaustive switch expressions**: Unlike switch statements, switch expressions must cover every possible value. Forgetting a case (or omitting the wildcard `_`) is a **compile-time error**, not a runtime one. This is a feature — it prevents silent bugs — but it can surprise developers coming from switch statements.

- **`assert` is debug-only**: A common mistake is relying on `assert` for input validation in production code. In release builds, `assert` calls are completely removed, so any side effects inside the condition (rare but possible) will also disappear. Use explicit `if`/`throw` for production guards.

- **Condition must be `bool`**: Dart does not coerce values to `bool`. Writing `if (someString)` or `if (someList)` is a compile-time error. You must write `if (someString.isNotEmpty)` or `if (someList.isNotEmpty)` explicitly.

---

## ❓ Interview Questions

### Q1: How does Dart's `switch` statement handle fall-through compared to C/Java?

**Answer**: In C and Java, execution falls through from one `case` to the next unless you explicitly write `break`. Dart takes the opposite stance: **implicit fall-through between non-empty cases is a compile-time error**. Each non-empty case must end with `break`, `return`, `throw`, or `continue <label>`. The only permitted fall-through is between consecutive *empty* cases (cases with no body), which is a common pattern for grouping multiple values under one handler. This design eliminates an entire class of bugs where a developer forgets a `break` and execution silently continues into the wrong case.

### Q2: What is a switch expression in Dart 3 and how does it differ from a switch statement?

**Answer**: A switch expression (introduced in Dart 3.0) is an expression form of `switch` that **returns a value** and can appear anywhere an expression is valid — in a variable initializer, a `return` statement, or even as a function argument. Unlike a switch statement, a switch expression requires **exhaustive** coverage of all possible values; the compiler enforces this at compile time, so you can't accidentally miss a case. Cases use `=>` instead of `:` and there is no `break`. Guard clauses (`when`) let you add boolean conditions on top of pattern matching. Switch expressions pair especially well with sealed classes and enums, where the compiler can statically verify that every subtype or variant is handled.

### Q3: What is the difference between `break` and `continue` in Dart loops?

**Answer**: `break` **exits the loop entirely** — execution jumps to the first statement after the loop body. `continue` **skips the remainder of the current iteration** and jumps to the loop's next cycle (the increment expression in a `for` loop, or the condition check in `while`/`do-while`). Both keywords apply to the **nearest enclosing** loop by default. If you need to target an outer loop, attach a label to that loop and write `break outerLabel` or `continue outerLabel`. Neither keyword works inside `forEach` callbacks — use a `for-in` loop instead.

### Q4: How do labeled loops work in Dart and when would you use them?

**Answer**: A label is an identifier followed by a colon placed immediately before a loop statement (e.g., `outer: for (...)`). You can then write `break outer` or `continue outer` from inside a nested loop to target that specific outer loop rather than the innermost one. This is useful when you need to exit or advance multiple levels of nesting in one step — for example, searching a 2D grid and stopping as soon as a match is found. The alternative without labels is a boolean flag variable, which is more verbose and less expressive. Labels are rarely needed in idiomatic Dart, but they're the right tool when nested loop control is genuinely required.

### Q5: What is the `assert` statement and when is it active?

**Answer**: `assert(condition, [message])` is a debug-mode invariant check. If `condition` evaluates to `false`, Dart throws an `AssertionError` with the optional `message`. Crucially, **`assert` is completely stripped out in production builds** — when you compile with `dart compile exe` or build a Flutter release app, every `assert` call disappears as if it were never written. This means `assert` is appropriate for documenting and catching programmer errors during development (e.g., "this parameter must never be null", "this list must be non-empty"), but it must **not** be used for runtime input validation or security checks that need to hold in production. For production guards, use explicit `if`/`throw` instead.

---

## 🔑 Key Takeaways

- Dart conditions must be strictly `bool` — there is no truthy/falsy coercion from other types.
- Classic `switch` forbids implicit fall-through in non-empty cases; Dart 3 switch expressions go further by requiring exhaustive coverage at compile time.
- Switch expressions return values, support guard clauses (`when`), and use `=>` syntax — they're the idiomatic choice for pattern-based branching in Dart 3.
- `for-in` is the cleanest loop for iterating over any `Iterable`; use C-style `for` when you need an index, and `forEach` only when you don't need `break`/`continue`.
- `break` and `continue` target the nearest enclosing loop by default; labels let you target outer loops explicitly without boolean flag variables.
- `assert` is a development-only tool — it is completely removed in release builds, so never rely on it for production validation logic.

---

## 🔗 Related Topics

- [Day 03: Null Safety](./Day-03-Null-Safety.md) — null-aware operators (`??`, `?.`) are a form of conditional branching worth reviewing alongside `if/else`
- [Day 05: Functions](./Day-05-Functions.md) — arrow functions and closures interact closely with loop callbacks and `forEach`
- [Day 18: Dart 3 Features](../Week-3-Async-Advanced/Day-18-Dart3-Features.md) — deep dive into patterns, sealed classes, and exhaustive switch expressions
- [Dart Cheatsheet](../Cheatsheets/Dart-Cheatsheet.md) — quick-reference syntax for all control flow constructs
