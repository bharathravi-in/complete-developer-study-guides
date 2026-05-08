# Day 13: Extension Methods

## 🎯 What You'll Learn

- What extension methods are and why they were introduced in Dart 2.7
- How to declare an extension with the `extension` keyword
- How to name an extension and why naming matters for disambiguation
- How to write extensions on nullable types (`String?`, `int?`)
- How to write extensions on generic types (`List<T>`, `Iterable<T>`)
- How to resolve naming conflicts between two extensions using explicit syntax
- The limitations of extension methods — what they cannot do
- Practical use cases: adding utility methods to built-in types

---

## 📚 Core Concepts

### What Are Extension Methods?

Extension methods let you add new methods (and getters, setters, and operators) to an existing type **without modifying the original class** and without subclassing it. They are purely syntactic sugar — at the call site, `myString.toTitleCase()` looks like a regular method call, but the compiler rewrites it to a static function call behind the scenes.

They were introduced in Dart 2.7 to solve a common frustration: you cannot add methods to `String`, `int`, `List`, or any other type you don't own. Before extension methods, the only options were standalone utility functions (`toTitleCase(myString)`) or wrapper classes — both of which break the fluent, method-chaining style that Dart encourages.

```dart
// Before extension methods — awkward standalone function
String toTitleCase(String s) => s.split(' ').map((w) =>
    w[0].toUpperCase() + w.substring(1)).join(' ');

print(toTitleCase('hello world')); // Hello World

// With extension methods — reads naturally
extension StringUtils on String {
  String toTitleCase() => split(' ').map((w) =>
      w[0].toUpperCase() + w.substring(1)).join(' ');
}

print('hello world'.toTitleCase()); // Hello World
```

### Declaring an Extension

The syntax is:

```dart
extension [OptionalName] on Type {
  // methods, getters, setters, operators
}
```

The name is optional for anonymous extensions (useful in the same file), but **naming is strongly recommended** for extensions in libraries — it enables explicit disambiguation and makes the extension importable/hideable.

Inside the extension body, `this` refers to the instance of the extended type, just like inside a regular method.

### Extensions on Nullable Types

You can extend nullable types by writing `on Type?`. This is particularly useful for adding null-safe utility methods:

```dart
extension NullableStringUtils on String? {
  // this is String? — can be null
  bool get isNullOrEmpty => this == null || this!.isEmpty;
  String orDefault(String fallback) => this ?? fallback;
}

String? name;
print(name.isNullOrEmpty); // true — no null check needed at call site
print(name.orDefault('Anonymous')); // Anonymous
```

Note: an extension on `String?` also applies to non-nullable `String` values (since `String` is a subtype of `String?`). An extension on `String` does **not** apply to `String?` — you cannot call it on a nullable value without a null check.

### Extensions on Generic Types

Extensions can be generic, allowing you to add methods to `List<T>`, `Iterable<T>`, or any parameterized type:

```dart
extension ListUtils<T> on List<T> {
  // Splits the list into chunks of [size]
  List<List<T>> chunked(int size) {
    final result = <List<T>>[];
    for (var i = 0; i < length; i += size) {
      result.add(sublist(i, (i + size).clamp(0, length)));
    }
    return result;
  }
}

print([1, 2, 3, 4, 5].chunked(2)); // [[1, 2], [3, 4], [5]]
```

The type parameter `T` is inferred from the receiver — no explicit type argument is needed at the call site.

### Naming Conflicts and Disambiguation

If two extensions define a method with the same name on the same type, and both are in scope, Dart reports a compile-time ambiguity error. There are two ways to resolve it:

1. **Hide one extension** at the import site: `import 'package:foo/foo.dart' hide ExtensionA;`
2. **Use explicit extension syntax**: `ExtensionName(receiver).method()`

```dart
extension A on String {
  String shout() => toUpperCase() + '!!!';
}

extension B on String {
  String shout() => '*** ${toUpperCase()} ***';
}

// 'hello'.shout(); // compile error — ambiguous

// Explicit disambiguation:
print(A('hello').shout()); // HELLO!!!
print(B('hello').shout()); // *** HELLO ***
```

### What Extensions Cannot Do

Extensions have important limitations:

1. **No instance variables.** You cannot add new fields to a class via an extension. Extensions can only add methods, getters, setters, and operators. (Static fields are allowed but are just static members of the extension, not instance state.)
2. **No overriding existing members.** If the type already has a method with the same name, the extension method is silently ignored — the original method always wins. Extensions can only add new members, not replace existing ones.
3. **No access to private members.** An extension defined outside the library that declares the type cannot access private members (names starting with `_`).
4. **Not visible on `dynamic`.** If the static type of a variable is `dynamic`, extension methods are not resolved — only actual instance methods are called. Extensions are a compile-time feature.

### Practical Use Cases

Extensions shine for:
- Adding utility methods to `String` (parsing, formatting, validation)
- Adding convenience methods to `int` and `double` (clamping, formatting)
- Adding collection utilities to `List<T>` and `Iterable<T>` (chunking, grouping, zipping)
- Adding domain-specific helpers to third-party types you don't own
- Improving readability by enabling method chaining on types that don't natively support it

---

## 💻 Code Examples

### Example 1: Basic Extension on `String` and `int`

```dart
// ── Extension on String ────────────────────────────────────────────────────
extension StringExtensions on String {
  // Convert to title case: "hello world" → "Hello World"
  String toTitleCase() {
    if (isEmpty) return this; // handle empty string
    return split(' ')
        .map((word) => word.isEmpty
            ? word
            : word[0].toUpperCase() + word.substring(1).toLowerCase())
        .join(' ');
  }

  // Truncate with ellipsis: "Hello World" → "Hello..." (maxLength=8)
  String truncate(int maxLength, {String ellipsis = '...'}) {
    if (length <= maxLength) return this;
    return substring(0, maxLength - ellipsis.length) + ellipsis;
  }

  // Check if the string is a valid email (simplified)
  bool get isValidEmail {
    final regex = RegExp(r'^[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}$');
    return regex.hasMatch(this);
  }

  // Repeat the string n times: 'ab'.repeat(3) → 'ababab'
  String repeat(int times) => List.filled(times, this).join();

  // Count occurrences of a substring
  int countOccurrences(String pattern) {
    if (pattern.isEmpty) return 0;
    var count = 0;
    var start = 0;
    while (true) {
      final index = indexOf(pattern, start);
      if (index == -1) break;
      count++;
      start = index + pattern.length;
    }
    return count;
  }
}

// ── Extension on int ──────────────────────────────────────────────────────
extension IntExtensions on int {
  // Clamp between min and max (more readable than .clamp())
  int between(int min, int max) => clamp(min, max) as int;

  // Format as ordinal: 1 → "1st", 2 → "2nd", 3 → "3rd", 4 → "4th"
  String get ordinal {
    if (this >= 11 && this <= 13) return '${this}th'; // special cases
    return switch (this % 10) {
      1 => '${this}st',
      2 => '${this}nd',
      3 => '${this}rd',
      _ => '${this}th',
    };
  }

  // Generate a range: 5.to(8) → [5, 6, 7, 8]
  List<int> to(int end) =>
      List.generate(end - this + 1, (i) => this + i);

  // Check if the number is within a range (inclusive)
  bool inRange(int min, int max) => this >= min && this <= max;
}

void main() {
  // ── String extensions ─────────────────────────────────────────────────
  print('hello world'.toTitleCase()); // Hello World
  print('dart programming language'.toTitleCase()); // Dart Programming Language

  print('Hello, World!'.truncate(8));          // Hello...
  print('Hi'.truncate(8));                     // Hi (no truncation needed)

  print('user@example.com'.isValidEmail);      // true
  print('not-an-email'.isValidEmail);          // false

  print('ab'.repeat(3));                       // ababab
  print('banana'.countOccurrences('an'));      // 2

  // ── int extensions ────────────────────────────────────────────────────
  print(150.between(0, 100)); // 100 — clamped
  print(50.between(0, 100));  // 50 — within range

  print(1.ordinal);  // 1st
  print(2.ordinal);  // 2nd
  print(11.ordinal); // 11th (special case)
  print(21.ordinal); // 21st

  print(3.to(7)); // [3, 4, 5, 6, 7]

  print(5.inRange(1, 10)); // true
  print(15.inRange(1, 10)); // false
}
```

### Example 2: Extension on Nullable Type (`String?`), Extension on `List<T>`

```dart
// ── Extension on nullable String ──────────────────────────────────────────
extension NullableStringExtensions on String? {
  // Safe check — works even when this is null
  bool get isNullOrEmpty => this == null || this!.isEmpty;
  bool get isNullOrBlank => this == null || this!.trim().isEmpty;

  // Return this if non-null and non-empty, otherwise return the fallback
  String orDefault(String fallback) {
    if (isNullOrEmpty) return fallback;
    return this!; // safe — we checked above
  }

  // Safe trim — returns null if this is null
  String? get trimmed => this?.trim();
}

// ── Generic extension on List<T> ──────────────────────────────────────────
extension ListExtensions<T> on List<T> {
  // Split into chunks of [size] — useful for pagination, batching
  List<List<T>> chunked(int size) {
    if (size <= 0) throw ArgumentError('size must be positive');
    final result = <List<T>>[];
    for (var i = 0; i < length; i += size) {
      // clamp ensures we don't go past the end of the list
      result.add(sublist(i, (i + size).clamp(0, length)));
    }
    return result;
  }

  // Returns a new list with duplicates removed, preserving order
  List<T> distinct() {
    final seen = <T>{};
    return where(seen.add).toList(); // Set.add returns false for duplicates
  }

  // Zip two lists together into a list of pairs
  List<(T, S)> zip<S>(List<S> other) {
    final len = length < other.length ? length : other.length;
    return List.generate(len, (i) => (this[i], other[i]));
  }

  // Returns the element at [index] or [defaultValue] if out of bounds
  T getOrElse(int index, T defaultValue) {
    if (index < 0 || index >= length) return defaultValue;
    return this[index];
  }

  // Rotate the list left by [n] positions: [1,2,3,4,5].rotateLeft(2) → [3,4,5,1,2]
  List<T> rotateLeft(int n) {
    if (isEmpty) return [];
    final offset = n % length; // handle n > length
    return [...sublist(offset), ...sublist(0, offset)];
  }
}

void main() {
  // ── Nullable String extensions ────────────────────────────────────────
  String? name;
  print(name.isNullOrEmpty);       // true
  print(name.orDefault('Guest'));  // Guest

  name = '  ';
  print(name.isNullOrBlank);       // true
  print(name.trimmed);             // '' (empty string after trim)

  name = 'Alice';
  print(name.isNullOrEmpty);       // false
  print(name.orDefault('Guest'));  // Alice

  // ── List<T> extensions ────────────────────────────────────────────────
  final numbers = [1, 2, 3, 4, 5, 6, 7];
  print(numbers.chunked(3)); // [[1, 2, 3], [4, 5, 6], [7]]
  print(numbers.chunked(2)); // [[1, 2], [3, 4], [5, 6], [7]]

  final withDupes = [1, 2, 2, 3, 1, 4, 3];
  print(withDupes.distinct()); // [1, 2, 3, 4]

  final letters = ['a', 'b', 'c'];
  final zipped = letters.zip([1, 2, 3]);
  print(zipped); // [(a, 1), (b, 2), (c, 3)]

  print(numbers.getOrElse(2, -1));  // 3 — valid index
  print(numbers.getOrElse(99, -1)); // -1 — out of bounds

  print([1, 2, 3, 4, 5].rotateLeft(2)); // [3, 4, 5, 1, 2]
  print([1, 2, 3, 4, 5].rotateLeft(7)); // [3, 4, 5, 1, 2] — 7 % 5 = 2
}
```

### Example 3: Named Extensions, Disambiguation with `ExtensionName.method()`, Extension on `Iterable`

```dart
// ── Two extensions that define the same method name ───────────────────────
// This simulates a conflict that can arise when importing multiple packages.

extension MarkdownFormatter on String {
  // Format as a Markdown bold string
  String get bold => '**$this**';

  // Format as a Markdown code span
  String get code => '`$this`';
}

extension HtmlFormatter on String {
  // Format as an HTML bold tag
  String get bold => '<b>$this</b>';

  // Format as an HTML code tag
  String get code => '<code>$this</code>';
}

// ── Extension on Iterable<T> — works for List, Set, any Iterable ──────────
extension IterableExtensions<T> on Iterable<T> {
  // Returns the element at [index], or null if out of bounds
  T? elementAtOrNull(int index) {
    if (index < 0) return null;
    var i = 0;
    for (final element in this) {
      if (i == index) return element;
      i++;
    }
    return null;
  }

  // Groups elements by a key function — returns Map<K, List<T>>
  Map<K, List<T>> groupBy<K>(K Function(T) keyOf) {
    final result = <K, List<T>>{};
    for (final element in this) {
      (result[keyOf(element)] ??= []).add(element);
    }
    return result;
  }

  // Returns true if the iterable has exactly [count] elements
  bool hasExactly(int count) {
    var n = 0;
    for (final _ in this) {
      n++;
      if (n > count) return false; // short-circuit — no need to count all
    }
    return n == count;
  }

  // Interleave with a separator element: [1,2,3].intersperse(0) → [1,0,2,0,3]
  Iterable<T> intersperse(T separator) sync* {
    var first = true;
    for (final element in this) {
      if (!first) yield separator;
      yield element;
      first = false;
    }
  }
}

void main() {
  // ── Disambiguation: both MarkdownFormatter and HtmlFormatter define bold ──
  const text = 'Dart';

  // 'text.bold' would be ambiguous if both extensions are in scope.
  // Use explicit extension syntax to choose:
  print(MarkdownFormatter(text).bold); // **Dart**
  print(HtmlFormatter(text).bold);     // <b>Dart</b>
  print(MarkdownFormatter(text).code); // `Dart`
  print(HtmlFormatter(text).code);     // <code>Dart</code>

  // ── Iterable extensions ───────────────────────────────────────────────
  final words = ['apple', 'banana', 'avocado', 'blueberry', 'cherry'];

  // elementAtOrNull — safe index access on any Iterable
  print(words.elementAtOrNull(2));  // avocado
  print(words.elementAtOrNull(99)); // null

  // groupBy — group by first letter
  final byLetter = words.groupBy((w) => w[0]);
  print(byLetter);
  // {a: [apple, avocado], b: [banana, blueberry], c: [cherry]}

  // hasExactly — efficient count check
  print(words.hasExactly(5)); // true
  print(words.hasExactly(3)); // false

  // intersperse — works on any Iterable, including lazy ones
  final nums = [1, 2, 3, 4];
  print(nums.intersperse(0).toList()); // [1, 0, 2, 0, 3, 0, 4]

  // Works on Set too — Iterable extension applies to all Iterables
  final letters = {'a', 'b', 'c'};
  print(letters.groupBy((l) => l == 'a' ? 'vowel' : 'consonant'));
  // {vowel: [a], consonant: [b, c]}
}
```

---

## ⚠️ Common Pitfalls

1. **Trying to add instance variables via an extension.** Extensions cannot add new instance state to a class. `extension Foo on Bar { int count = 0; }` is a compile error. If you need to associate state with an existing type, use a wrapper class, a `Map<Bar, int>` external store, or an `Expando<int>`.

2. **Expecting an extension method to override an existing method.** If the type already has a method with the same name, the extension method is silently ignored — the original always wins. This is by design (extensions cannot break existing code), but it means you cannot use extensions to "patch" a method you dislike. If you need to change behavior, subclass or wrap the type.

3. **Extension methods not working on `dynamic` variables.** Extensions are resolved at compile time based on the static type. If a variable is typed as `dynamic`, extension methods are not available — only actual instance methods are dispatched. Always use a specific static type to benefit from extensions.

4. **Forgetting that an extension on `String` does not apply to `String?`.** An extension on `String` cannot be called on a nullable `String?` without a null check. If you want the method to work on nullable values, declare the extension on `String?` explicitly. Conversely, an extension on `String?` also applies to non-nullable `String` values.

5. **Name collisions between extensions from different packages.** When two imported libraries both define an extension with the same method name on the same type, you get a compile-time ambiguity error. Resolve it by hiding one extension at the import site (`import 'package:foo/foo.dart' hide ExtensionA`) or by using explicit extension syntax (`ExtensionA(value).method()`).

---

## ❓ Interview Questions

### Q1: What are extension methods in Dart and why were they introduced?

**Answer:** Extension methods, introduced in Dart 2.7, allow developers to add new methods, getters, setters, and operators to existing types without modifying the original class or subclassing it. They were introduced to solve the problem of adding utility methods to types you don't own — like `String`, `int`, or third-party classes — in a way that reads naturally as a method call rather than a standalone function. Before extension methods, the only options were utility functions (`toTitleCase(str)`) or wrapper classes, both of which break the fluent, method-chaining style that Dart encourages. Extensions are purely a compile-time feature: the compiler rewrites `str.toTitleCase()` to a static function call, so there is no runtime overhead.

### Q2: How do you resolve a naming conflict between two extensions?

**Answer:** When two extensions in scope define a method with the same name on the same type, Dart reports a compile-time ambiguity error. There are two resolution strategies. First, you can hide one of the conflicting extensions at the import site using `import 'package:foo/foo.dart' hide ConflictingExtension`, which removes it from scope entirely. Second, you can use explicit extension invocation syntax: `ExtensionName(receiver).methodName()` — this bypasses the ambiguity by explicitly naming which extension to use. The explicit syntax is also useful when you want to call an extension method that is shadowed by an instance method of the same name (though in that case, the instance method always wins and the extension cannot override it).

### Q3: Can you add instance variables to a class via an extension?

**Answer:** No — extensions cannot add instance variables (fields) to a class. Extensions can only add methods, getters, setters, and operators. Attempting to declare an instance variable in an extension body is a compile error. This limitation exists because adding instance variables would change the memory layout of the class, which is not possible without modifying the class itself. Static variables are allowed in extensions, but they are just static members of the extension type, not per-instance state. If you need to associate per-instance state with an existing type, the alternatives are: a wrapper/decorator class, an `Expando<T>` (a weak-reference map from object to value), or an external `Map<OriginalType, StateType>`.

### Q4: How do extensions on nullable types work?

**Answer:** An extension declared `on Type?` applies to both nullable and non-nullable values of that type, because `Type` is a subtype of `Type?`. Inside the extension body, `this` has type `Type?`, so you must null-check before calling non-nullable methods. Conversely, an extension declared `on Type` (non-nullable) does not apply to `Type?` values — you cannot call it on a nullable variable without a null check or the `?.` operator. Extensions on nullable types are useful for adding null-safe utility methods like `isNullOrEmpty` or `orDefault` that handle the null case gracefully, eliminating the need for null checks at every call site.

### Q5: What are the limitations of extension methods in Dart?

**Answer:** Extension methods have several important limitations. First, they cannot add instance variables — only methods, getters, setters, and operators. Second, they cannot override existing instance methods — if the type already has a method with the same name, the instance method always wins and the extension is silently ignored. Third, they cannot access private members of the extended type (names starting with `_`) unless the extension is defined in the same library. Fourth, they are not resolved on `dynamic` — if the static type is `dynamic`, only actual instance methods are dispatched. Fifth, naming conflicts between two extensions in scope cause a compile-time error that must be resolved by hiding one extension or using explicit invocation syntax.

---

## 🔑 Key Takeaways

- Extension methods add methods/getters/operators to existing types without modifying or subclassing them — purely a compile-time feature.
- Name extensions for disambiguation and to make them importable/hideable.
- Extensions on `Type?` apply to both nullable and non-nullable values; extensions on `Type` do not apply to `Type?`.
- Generic extensions (`extension Foo<T> on List<T>`) work on any parameterized type with the type argument inferred from the receiver.
- Resolve naming conflicts by hiding an extension at import or using explicit `ExtensionName(receiver).method()` syntax.
- Extensions cannot add instance variables, cannot override existing methods, and are invisible on `dynamic` variables.
- Best use cases: utility methods on `String`/`int`/`double`, collection helpers on `List<T>`/`Iterable<T>`, domain helpers on third-party types.

---

## 🔗 Related Topics

- **Previous:** [Day 12 — Advanced Collections](./Day-12-Advanced-Collections.md)
- **Next:** [Day 14 — Enums](./Day-14-Enums.md)
- **Day 05:** [Functions](../Week-1-Dart-Fundamentals/Day-05-Functions.md) — extension methods are syntactic sugar over static functions
- **Day 11:** [Generics](./Day-11-Generics.md) — generic extensions use the same type parameter syntax
- **Dart Cheatsheet:** [Extension method syntax quick reference](../Cheatsheets/Dart-Cheatsheet.md)
