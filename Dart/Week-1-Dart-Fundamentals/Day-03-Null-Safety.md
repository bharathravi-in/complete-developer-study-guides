# Day 03: Null Safety

## 🎯 What You'll Learn

- What sound null safety is and why Dart adopted it
- The difference between non-nullable types (default) and nullable types (`?`)
- How to use the null assertion operator (`!`) and when it is risky
- All null-aware operators: `??`, `?.`, `??=`, `?..`, `?[]`
- The `late` keyword for deferred and lazy initialization
- How Dart's type promotion automatically narrows nullable types after null checks
- Null safety in function parameters and return types
- A brief overview of migrating pre-null-safety code

---

## 📚 Core Concepts

### What Is Sound Null Safety?

Null safety is a language feature that eliminates an entire class of runtime errors — the infamous "null reference" crash — by moving null checks to compile time. Before null safety, any variable of any type could silently hold `null`, and the compiler had no way to warn you. The result was runtime `NullPointerException`-style crashes that were hard to trace.

Dart's null safety is described as *sound* because the guarantee is enforced end-to-end by the type system. If the compiler says a variable is non-nullable, it is *provably* non-null at runtime — no hidden escape hatches. This is stronger than, say, TypeScript's `strictNullChecks`, which can be bypassed with `any`, or Kotlin's `!!` operator used carelessly. In Dart, the only way to get a null dereference at runtime is to explicitly use the `!` operator on a value that turns out to be null.

### Non-Nullable vs Nullable Types

By default, every type in Dart is **non-nullable**. `String name` cannot hold `null` — the compiler rejects any assignment of `null` to it. To allow null, you append `?` to the type: `String? name`. This single character is the entire opt-in mechanism.

```dart
String name = 'Alice';   // non-nullable — can never be null
String? nickname;        // nullable — defaults to null
```

The `?` annotation propagates through the type system. A `List<String>` is a non-nullable list of non-nullable strings. A `List<String?>` is a non-nullable list that may contain null elements. A `List<String>?` is a nullable list (the list itself may be null). A `List<String?>?` allows both.

### The `!` Null Assertion Operator

The `!` operator tells the compiler "I know this is not null right now — trust me." It converts a `T?` to `T`. If you are wrong and the value is actually null at runtime, Dart throws a `Null check operator used on a null value` error immediately.

Use `!` only when you have external knowledge that the compiler cannot infer — for example, after checking a flag set elsewhere, or when interoperating with legacy APIs. Prefer null-aware operators or explicit null checks whenever possible.

### Null-Aware Operators

Dart provides a rich set of operators for working with nullable values without verbose `if (x != null)` guards:

- **`??` (if-null / null-coalescing)**: Returns the left operand if it is non-null, otherwise evaluates and returns the right operand. `String display = nickname ?? 'Anonymous';`
- **`?.` (null-safe member access)**: Accesses a property or calls a method only if the receiver is non-null; otherwise the entire expression evaluates to `null`. `int? len = nickname?.length;`
- **`??=` (null-aware assignment)**: Assigns the right-hand value to the variable only if the variable is currently null. `nickname ??= 'Guest';`
- **`?..` (null-aware cascade)**: Chains method calls on an object only if it is non-null. `buffer?..write('hello')..write(' world');`
- **`?[]` (null-aware index)**: Accesses a list or map element only if the collection is non-null. `String? first = items?[0];`

### The `late` Keyword

`late` has two distinct uses:

1. **Deferred initialization**: You declare a non-nullable variable without an initializer, promising the compiler you will assign it before it is first read. If you read it before assigning, Dart throws a `LateInitializationError` at runtime. This is useful for fields initialized in `setUp()` in tests, or in `initState()` in Flutter widgets.

2. **Lazy initialization**: `late final String heavyValue = expensiveComputation();` — the initializer runs exactly once, the first time the variable is accessed. Subsequent reads return the cached value. This is a clean alternative to nullable fields used purely to defer work.

### Type Promotion

Dart's flow analysis automatically *promotes* a nullable type to its non-nullable counterpart inside a block where the compiler can prove the value is non-null. After `if (name != null)`, the variable `name` is treated as `String` (not `String?`) for the rest of that branch. This works for local variables and parameters but not for mutable fields (because another thread or getter could change them between the check and the use).

### Null Safety in Functions

Function parameters and return types participate fully in null safety. A parameter typed `String name` requires a non-null argument at every call site. A return type of `String?` means callers must handle the possibility of null. Named parameters can be made required with the `required` keyword, or optional with a nullable type or a default value.

### Migrating Pre-Null-Safety Code

Code written before Dart 2.12 can be migrated using `dart migrate`, an interactive tool that infers where `?` annotations are needed and where `!` assertions are appropriate. The tool adds `// ignore: null_safety` comments only as a last resort. Most modern packages have already migrated; you will rarely encounter un-migrated code in new projects.

---

## 💻 Code Examples

### Example 1: Nullable vs Non-Nullable Variables, `?` Annotation, and `!` Operator

```dart
void main() {
  // Non-nullable: the compiler guarantees this is never null.
  String city = 'London';

  // Nullable: explicitly opt in to allowing null.
  String? country;

  // country is null here — safe to print because we use ?. and ??
  print(country?.toUpperCase() ?? 'UNKNOWN'); // UNKNOWN

  country = 'UK';
  print(country.toUpperCase()); // UK — no null check needed after assignment

  // Using ! when we are certain the value is non-null.
  // Dangerous if wrong — throws at runtime, not compile time.
  String? maybeCity = fetchCity(); // returns null or a String
  if (maybeCity != null) {
    // Type promotion: maybeCity is treated as String inside this block.
    print(maybeCity.length); // safe — no ! needed
  }

  // Risky use of !: only do this when you have external proof it's non-null.
  String definiteCity = maybeCity!; // throws if maybeCity is null
  print(definiteCity);
}

// Simulates a function that may return null.
String? fetchCity() => null;
```

### Example 2: All Null-Aware Operators in Practice

```dart
void main() {
  String? username;
  List<String>? tags;
  StringBuffer? buffer;

  // ?? — provide a fallback when the value is null
  String display = username ?? 'Anonymous';
  print(display); // Anonymous

  // ??= — assign only if currently null (lazy default)
  username ??= 'Guest';
  print(username); // Guest

  // ?. — safe member access; returns null instead of throwing
  int? nameLength = username?.length; // 5
  print(nameLength); // 5

  // Chaining ?. — each step short-circuits if null is encountered
  String? upper = username?.toUpperCase().substring(0, 3);
  print(upper); // GUE

  // ?[] — null-aware index operator on a nullable collection
  String? firstTag = tags?[0]; // null because tags is null
  print(firstTag); // null

  tags = ['dart', 'flutter', 'null-safety'];
  print(tags?[1]); // flutter

  // ?.. — null-aware cascade: calls methods only if receiver is non-null
  buffer?..write('hello')..write(' world'); // skipped — buffer is null
  print(buffer); // null

  buffer = StringBuffer();
  buffer?..write('hello')..write(' world'); // executed — buffer is non-null
  print(buffer); // hello world

  // Combining operators for concise null handling
  String result = username?.trim() ?? 'default';
  print(result); // Guest
}
```

### Example 3: Type Promotion — Automatic Narrowing After Null Checks

```dart
// Dart's flow analysis promotes nullable types to non-nullable
// inside branches where null has been ruled out.

String describe(String? value) {
  // Before the check, value is String? — we cannot call .length directly.

  // --- Pattern 1: if-null guard ---
  if (value == null) {
    return 'nothing'; // early return
  }
  // After the early return, Dart knows value is non-null here.
  return 'value has ${value.length} characters'; // no ! needed
}

// --- Pattern 2: null check with else branch ---
void printUpperCase(String? text) {
  if (text != null) {
    // Inside this block, text is promoted to String.
    print(text.toUpperCase()); // safe
  } else {
    print('(null)');
  }
}

// --- Pattern 3: late for deferred initialization ---
class UserProfile {
  late String displayName; // non-nullable, but not yet assigned

  void initialize(String name) {
    displayName = name; // assigned before first read
  }

  void greet() {
    // If initialize() was never called, this throws LateInitializationError.
    print('Hello, $displayName!');
  }
}

// --- Pattern 4: late final for lazy initialization ---
class Config {
  // The initializer runs exactly once, the first time apiUrl is accessed.
  late final String apiUrl = _loadApiUrl();

  String _loadApiUrl() {
    print('Loading API URL...'); // printed only once
    return 'https://api.example.com';
  }
}

// --- Pattern 5: type promotion does NOT work on mutable fields ---
class Example {
  String? mutableField;

  void demo() {
    if (mutableField != null) {
      // ERROR (if uncommented): mutableField could be set to null
      // by another method between the check and this line.
      // print(mutableField.length); // compile error
      final local = mutableField; // copy to a local variable first
      if (local != null) {
        print(local.length); // now promotion works on the local copy
      }
    }
  }
}

void main() {
  print(describe(null));        // nothing
  print(describe('Dart'));      // value has 4 characters

  printUpperCase('hello');      // HELLO
  printUpperCase(null);         // (null)

  final profile = UserProfile();
  profile.initialize('Alice');
  profile.greet();              // Hello, Alice!

  final config = Config();
  print(config.apiUrl);         // Loading API URL... \n https://api.example.com
  print(config.apiUrl);         // https://api.example.com  (no second load)

  final ex = Example();
  ex.mutableField = 'test';
  ex.demo();                    // 4
}
```

---

## ⚠️ Common Pitfalls

1. **Overusing `!` instead of proper null handling.** The `!` operator is an escape hatch, not a solution. Every `!` is a potential runtime crash. Prefer `??`, `?.`, or an explicit `if` check. Reserve `!` for cases where you have genuine external proof the value is non-null (e.g., after a `required` field is set by a framework).

2. **Expecting type promotion on class fields.** Dart only promotes *local variables* and *parameters*, not mutable instance fields. If you check `if (myField != null)` and then access `myField.length`, the compiler still complains because `myField` could be reassigned between the check and the access. Fix: copy the field to a local variable first (`final local = myField; if (local != null) { ... }`).

3. **Confusing `late` with nullable.** A `late String name` is still non-nullable — it just defers the initialization check to runtime. If you read it before assigning, you get a `LateInitializationError`, not a null value. Use `late` when you can guarantee assignment before first read; use `String?` when the absence of a value is a valid, ongoing state.

4. **Forgetting that `??=` only assigns when null.** `x ??= value` is equivalent to `x = x ?? value`. If `x` already has a non-null value, the right-hand side is never evaluated. This is intentional but can surprise developers who expect it to always run.

5. **Null-aware operators returning `null` silently.** `?.` returns `null` when the receiver is null. If you chain `?.` calls and forget to handle the resulting `T?`, you can propagate null further than intended. Always pair `?.` with `??` or a null check at the end of the chain.

---

## ❓ Interview Questions

### Q1: What is sound null safety in Dart and how does it differ from nullable types in other languages?

**Answer**: Sound null safety means the Dart type system *provably* guarantees that a non-nullable variable can never hold null — not just at the point of declaration, but throughout the entire program, including across library boundaries. The guarantee is enforced at compile time with no runtime overhead for non-nullable types. This differs from TypeScript's `strictNullChecks`, which can be bypassed with `any` or type assertions, and from Java's `@NonNull` annotations, which are advisory and not enforced by the compiler. In Kotlin, null safety is also sound, making it the closest analogue; Dart's system is similarly rigorous but adds the `late` keyword and a richer set of null-aware operators.

### Q2: What is the difference between `??` and `?.` operators?

**Answer**: `??` (the if-null or null-coalescing operator) operates on a *value* and provides a fallback: `a ?? b` returns `a` if it is non-null, otherwise evaluates and returns `b`. The result type is non-nullable when `b` is non-nullable. `?.` (the null-safe member access operator) operates on a *receiver* before accessing a property or calling a method: `obj?.property` returns `null` if `obj` is null, otherwise returns `obj.property`. The result type is always nullable (`T?`). They are often combined: `obj?.property ?? defaultValue` — first safely access the property, then provide a fallback if either the object or the property is null.

### Q3: When should you use the `!` operator and what are its risks?

**Answer**: Use `!` only when you have information the compiler cannot infer — for example, when a value is guaranteed non-null by an invariant enforced elsewhere in the program, or when working with APIs that return `T?` for historical reasons but are documented to never return null in a specific context. The risk is a `Null check operator used on a null value` runtime error if your assumption is wrong; unlike a compile-time error, this crash only surfaces when that code path is executed, potentially in production. Prefer explicit null checks, `??`, or `?.` wherever possible, and treat every `!` as a code smell that warrants a comment explaining why it is safe.

### Q4: What is type promotion in Dart's null safety system?

**Answer**: Type promotion is Dart's flow analysis feature that automatically narrows the type of a variable within a code block where the compiler can prove a stricter type holds. For null safety, this means that after `if (x == null) return;`, the variable `x` is treated as non-nullable for the rest of the enclosing scope. Similarly, after `if (x != null) { ... }`, `x` is non-nullable inside the braces. Promotion applies to local variables and parameters but not to mutable instance fields, because the compiler cannot rule out concurrent mutation between the check and the use. To promote a field, copy it to a local variable first.

### Q5: What is the difference between `late` and nullable (`?`) for deferred initialization?

**Answer**: A nullable variable (`String? name`) explicitly models the absence of a value as a valid, ongoing state — `null` is a meaningful value that callers must handle. A `late` variable (`late String name`) is still non-nullable; it simply defers the *initialization check* from declaration time to first-read time. The intent is "this will definitely have a value before it is used, but I cannot provide it at construction time." If a `late` variable is read before being assigned, Dart throws a `LateInitializationError` at runtime. Use `late` when you can guarantee assignment before first read (e.g., in `setUp()` or `initState()`); use `?` when the absence of a value is a legitimate state that the rest of the code needs to handle.

---

## 🔑 Key Takeaways

- Dart's null safety is *sound*: non-nullable types are provably non-null at compile time, eliminating an entire class of runtime crashes.
- Append `?` to any type to make it nullable; without `?`, the type is non-nullable by default.
- Use `??` for fallback values, `?.` for safe member access, `??=` for lazy defaults, `?..` for null-aware cascades, and `?[]` for null-aware indexing.
- The `!` operator bypasses compile-time safety — use it sparingly and only when you have external proof the value is non-null.
- `late` defers initialization to first read (non-nullable); use it for fields that cannot be initialized at construction time but are guaranteed to be set before use.
- Type promotion automatically narrows nullable locals and parameters after null checks; it does not apply to mutable class fields.
- Null safety applies to function parameters and return types — `required` enforces non-null named parameters at every call site.

---

## 🔗 Related Topics

- [Day 02: Variables and Types](./Day-02-Variables-Types.md) — understanding `var`, `final`, `const`, and built-in types that underpin null safety
- [Day 04: Control Flow](./Day-04-Control-Flow.md) — `if/else` and `switch` patterns that trigger type promotion
- [Day 21: Type System Deep Dive](../Week-3-Async-Advanced/Day-21-Type-System-Deep-Dive.md) — sound null safety internals, `dynamic` vs `Object?`, and advanced type promotion
- [Dart Cheatsheet](../Cheatsheets/Dart-Cheatsheet.md) — quick-reference for all null-aware operators and `late` syntax
