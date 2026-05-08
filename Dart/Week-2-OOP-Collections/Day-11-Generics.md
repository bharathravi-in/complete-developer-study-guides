# Day 11: Generics

## 🎯 What You'll Learn

- What generics are and why they eliminate the need for `dynamic` casts
- How to declare and use generic classes with a type parameter `<T>`
- How to write generic methods that infer their type parameter from arguments
- How bounded type parameters (`T extends SomeType`) constrain what types are allowed
- What "reified generics" means and how Dart preserves type information at runtime
- The difference between `List<dynamic>`, `List<Object>`, and `List<String>`
- How covariance works in Dart's generic collections and where it can cause runtime errors
- How to use multiple type parameters (e.g., `Map<K, V>`)

---

## 📚 Core Concepts

### Why Generics?

Without generics, a reusable data structure must either accept `dynamic` (losing type safety) or be duplicated for every type it needs to support. Generics solve this by letting you write code that is **parameterized by a type** — the type is specified by the caller, and the compiler enforces it throughout.

```dart
// Without generics — unsafe, requires a cast to use the value
class Box {
  dynamic value;
  Box(this.value);
}

// With generics — type-safe, no cast needed
class Box<T> {
  T value;
  Box(this.value);
}

final Box<String> nameBox = Box('Alice');
final String name = nameBox.value; // no cast — T is String
```

The type parameter `T` is a placeholder that is replaced with a concrete type when the class is used. By convention, single-letter uppercase names are used: `T` (type), `E` (element), `K` (key), `V` (value), `R` (return type).

### Generic Classes

A generic class declares one or more type parameters in angle brackets after the class name. All methods and fields in the class can use those type parameters as if they were real types:

```dart
class Pair<A, B> {
  final A first;
  final B second;

  const Pair(this.first, this.second);

  Pair<B, A> swap() => Pair(second, first); // returns a new Pair with types swapped

  @override
  String toString() => '($first, $second)';
}

final p = Pair<String, int>('age', 30);
print(p);        // (age, 30)
print(p.swap()); // (30, age)
```

Dart can often **infer** the type arguments from the constructor arguments, so `Pair('age', 30)` works without explicitly writing `Pair<String, int>`.

### Generic Methods

A method can declare its own type parameter, independent of the class's type parameter. This is useful for utility functions that work on any type:

```dart
T first<T>(List<T> list) {
  if (list.isEmpty) throw StateError('List is empty');
  return list.first; // returns T, not dynamic
}

final String s = first(['a', 'b', 'c']); // T inferred as String
final int n = first([1, 2, 3]);           // T inferred as int
```

### Bounded Type Parameters

A **bounded type parameter** uses `extends` to restrict which types are allowed. This lets the generic code call methods that are guaranteed to exist on the bounded type:

```dart
// T must be Comparable<T> — guarantees T has a compareTo() method
T max<T extends Comparable<T>>(T a, T b) => a.compareTo(b) >= 0 ? a : b;

print(max(3, 7));       // 7 — int implements Comparable<int>
print(max('apple', 'banana')); // banana — String implements Comparable<String>
// max(Point(1,2), Point(3,4)); // compile error — Point doesn't implement Comparable
```

Without the bound, calling `a.compareTo(b)` would be a compile error because `T` could be anything. The bound `T extends Comparable<T>` tells the compiler that `T` is guaranteed to have `compareTo`.

### Reified Generics

In many languages (notably Java), generic type information is **erased** at runtime — a `List<String>` and a `List<int>` are both just `List` at runtime. Dart takes a different approach: **generics are reified**, meaning type information is preserved at runtime.

This means you can use `is` to check the generic type of a collection at runtime:

```dart
final items = <String>['a', 'b', 'c'];
print(items is List<String>); // true
print(items is List<int>);    // false — type info is preserved at runtime
print(items is List<Object>); // true — String is a subtype of Object
```

Reified generics make Dart's type system more predictable and eliminate an entire class of bugs that plague Java's type-erasure model.

### `List<dynamic>` vs `List<Object>` vs `List<String>`

These three types are often confused:

- **`List<String>`**: Only `String` values. Fully type-safe. The compiler rejects any attempt to add a non-`String`.
- **`List<Object>`**: Any non-nullable value (since every non-nullable type is a subtype of `Object`). Adding a `String` or `int` is fine, but retrieving an element gives you `Object` — you need a cast or `is` check to use it as a specific type.
- **`List<dynamic>`**: Opts out of type checking entirely. You can add anything and retrieve anything without a cast, but you lose all static type safety. Errors appear at runtime instead of compile time.

```dart
List<String> strings = ['a', 'b'];
// strings.add(1); // compile error

List<Object> objects = ['a', 1, true]; // fine — all are Object
final first = objects.first; // type is Object — need cast to use as String

List<dynamic> dynamics = ['a', 1, true]; // fine
final d = dynamics.first; // type is dynamic — no compile-time checks
```

### Covariance in Generic Collections

Dart's built-in collections (`List`, `Set`, `Map`) are **covariant** — a `List<String>` is a subtype of `List<Object>`. This is convenient but can cause runtime errors:

```dart
List<String> strings = ['hello'];
List<Object> objects = strings; // allowed — covariant assignment

// This compiles but throws at runtime:
// objects.add(42); // UnsupportedError: Cannot add to a fixed-length list
// (or CastError if the list is growable)
```

The runtime check catches the violation, but it means covariant collections are not fully statically safe. For read-only access, covariance is safe and useful. For mutable collections, be careful when assigning a `List<Subtype>` to a `List<Supertype>` variable.

---

## 💻 Code Examples

### Example 1: Generic Class (`Stack<T>`) and Generic Method

```dart
// ── Generic Stack implementation ───────────────────────────────────────────
class Stack<T> {
  // Internal storage — List<T> ensures type safety throughout
  final List<T> _items = [];

  // Push an item onto the stack
  void push(T item) => _items.add(item);

  // Pop the top item — throws if empty
  T pop() {
    if (isEmpty) throw StateError('Stack is empty');
    return _items.removeLast();
  }

  // Peek at the top item without removing it
  T get peek {
    if (isEmpty) throw StateError('Stack is empty');
    return _items.last;
  }

  bool get isEmpty => _items.isEmpty;
  int get size => _items.length;

  // Returns an unmodifiable view — callers cannot mutate internal state
  List<T> get items => List.unmodifiable(_items);

  @override
  String toString() => 'Stack<$T>($_items)';
}

// ── Generic method — works on any Stack<T> ────────────────────────────────
// Transfers all items from [source] to [destination], reversing order.
void transferAll<T>(Stack<T> source, Stack<T> destination) {
  while (!source.isEmpty) {
    destination.push(source.pop());
  }
}

// ── Generic function with return type inference ────────────────────────────
// Returns the element at [index] or [defaultValue] if out of bounds.
T getOrDefault<T>(List<T> list, int index, T defaultValue) {
  if (index < 0 || index >= list.length) return defaultValue;
  return list[index];
}

void main() {
  // ── String stack ──────────────────────────────────────────────────────
  final Stack<String> history = Stack();
  history.push('page1');
  history.push('page2');
  history.push('page3');

  print(history);       // Stack<String>([page1, page2, page3])
  print(history.peek);  // page3
  print(history.pop()); // page3
  print(history.size);  // 2

  // ── Integer stack ─────────────────────────────────────────────────────
  final Stack<int> numbers = Stack();
  numbers.push(10);
  numbers.push(20);
  numbers.push(30);

  final Stack<int> reversed = Stack();
  transferAll(numbers, reversed); // transfers and reverses
  print(reversed); // Stack<int>([30, 20, 10])

  // ── Generic method with type inference ───────────────────────────────
  final colors = ['red', 'green', 'blue'];
  print(getOrDefault(colors, 1, 'unknown')); // green
  print(getOrDefault(colors, 9, 'unknown')); // unknown — index out of bounds

  // ── Type safety demonstration ─────────────────────────────────────────
  // history.push(42); // compile error: int is not a String
  // numbers.push('hello'); // compile error: String is not an int
}
```

### Example 2: Bounded Type Parameters — `T extends Comparable<T>`, Sorting

```dart
import 'dart:math' show Random;

// ── Bounded generic function ───────────────────────────────────────────────
// T must implement Comparable<T>, guaranteeing compareTo() exists.
T clamp<T extends Comparable<T>>(T value, T min, T max) {
  if (value.compareTo(min) < 0) return min; // value < min
  if (value.compareTo(max) > 0) return max; // value > max
  return value;
}

// ── Generic class with a bound ────────────────────────────────────────────
// A sorted list that maintains ascending order on every insert.
class SortedList<T extends Comparable<T>> {
  final List<T> _data = [];

  void add(T item) {
    // Binary search for the insertion point
    int lo = 0, hi = _data.length;
    while (lo < hi) {
      final mid = (lo + hi) ~/ 2;
      if (_data[mid].compareTo(item) <= 0) {
        lo = mid + 1;
      } else {
        hi = mid;
      }
    }
    _data.insert(lo, item); // insert at sorted position
  }

  T get min => _data.first; // always the smallest — list is sorted
  T get max => _data.last;  // always the largest

  // Returns items in the range [from, to] inclusive
  List<T> range(T from, T to) => _data
      .where((item) =>
          item.compareTo(from) >= 0 && item.compareTo(to) <= 0)
      .toList();

  @override
  String toString() => 'SortedList($_data)';
}

// ── Custom class implementing Comparable ──────────────────────────────────
class Temperature implements Comparable<Temperature> {
  final double celsius;
  const Temperature(this.celsius);

  @override
  int compareTo(Temperature other) => celsius.compareTo(other.celsius);

  @override
  String toString() => '${celsius}°C';
}

void main() {
  // ── clamp with int ────────────────────────────────────────────────────
  print(clamp(5, 1, 10));   // 5 — within range
  print(clamp(-3, 1, 10));  // 1 — below min
  print(clamp(15, 1, 10));  // 10 — above max

  // ── clamp with String ─────────────────────────────────────────────────
  print(clamp('m', 'a', 'z')); // m
  print(clamp('A', 'a', 'z')); // a — 'A' < 'a' in Unicode ordering

  // ── SortedList<int> ───────────────────────────────────────────────────
  final sorted = SortedList<int>();
  final rng = Random(42);
  for (var i = 0; i < 8; i++) {
    sorted.add(rng.nextInt(100));
  }
  print(sorted); // SortedList([...sorted numbers...])
  print('min: ${sorted.min}, max: ${sorted.max}');

  // ── SortedList<String> ────────────────────────────────────────────────
  final words = SortedList<String>();
  ['banana', 'apple', 'cherry', 'date'].forEach(words.add);
  print(words); // SortedList([apple, banana, cherry, date])
  print(words.range('b', 'c')); // [banana, cherry]

  // ── SortedList<Temperature> — custom Comparable ───────────────────────
  final temps = SortedList<Temperature>();
  [Temperature(100), Temperature(-10), Temperature(37), Temperature(0)]
      .forEach(temps.add);
  print(temps); // SortedList([-10°C, 0°C, 37°C, 100°C])
}
```

### Example 3: Reified Generics — `is List<String>` at Runtime, Covariance

```dart
// ── Reified generics: type info is preserved at runtime ───────────────────

void inspectType(Object obj) {
  // In Java, these checks would all be true (type erasure).
  // In Dart, they correctly reflect the actual type argument.
  print('Value: $obj');
  print('  is List<String>: ${obj is List<String>}');
  print('  is List<int>:    ${obj is List<int>}');
  print('  is List<Object>: ${obj is List<Object>}');
  print('  is List<dynamic>:${obj is List<dynamic>}');
  print('  runtimeType:     ${obj.runtimeType}');
}

// ── Covariance: List<String> is a subtype of List<Object> ─────────────────
void demonstrateCovariance() {
  final List<String> strings = ['hello', 'world'];

  // Covariant assignment — allowed because List<String> <: List<Object>
  final List<Object> objects = strings;

  // Reading is safe — every String is an Object
  print(objects.first); // hello

  // Writing is DANGEROUS — the runtime catches it
  try {
    objects.add(42); // runtime error: type 'int' is not a subtype of type 'String'
  } catch (e) {
    print('Caught: $e');
  }

  // Safe pattern: use List<Object> from the start if you need mixed types
  final List<Object> mixed = ['hello', 42, true];
  print(mixed); // [hello, 42, true]
}

// ── whereType<T>() — filter by type using reified generics ────────────────
void filterByType() {
  final List<Object> mixed = [1, 'two', 3, 'four', 5.0, true];

  // whereType<T>() uses reified generics to filter at runtime
  final ints = mixed.whereType<int>().toList();
  final strings = mixed.whereType<String>().toList();

  print('Ints: $ints');       // Ints: [1, 3]
  print('Strings: $strings'); // Strings: [two, four]
}

// ── Generic result type — common pattern in Dart ──────────────────────────
sealed class Result<T> {
  const Result();
}

class Success<T> extends Result<T> {
  final T value;
  const Success(this.value);
  @override String toString() => 'Success($value)';
}

class Failure<T> extends Result<T> {
  final String error;
  const Failure(this.error);
  @override String toString() => 'Failure($error)';
}

Result<int> parseInt(String input) {
  final n = int.tryParse(input);
  return n != null ? Success(n) : Failure('Not a number: $input');
}

void main() {
  // ── Reified generics ──────────────────────────────────────────────────
  inspectType(<String>['a', 'b']);
  print('---');
  inspectType(<int>[1, 2, 3]);

  print('---');
  demonstrateCovariance();

  print('---');
  filterByType();

  print('---');
  // ── Result<T> pattern ─────────────────────────────────────────────────
  final results = ['42', 'hello', '100'].map(parseInt).toList();
  for (final result in results) {
    // Pattern matching on sealed Result<T>
    switch (result) {
      case Success(:final value):
        print('Parsed: $value');
      case Failure(:final error):
        print('Error: $error');
    }
  }
  // Parsed: 42
  // Error: Not a number: hello
  // Parsed: 100
}
```

---

## ⚠️ Common Pitfalls

1. **Using `dynamic` instead of a type parameter and losing compile-time safety.** `List<dynamic>` accepts anything and returns `dynamic`, so errors appear at runtime. If you find yourself writing `(myList[0] as String)`, that's a sign you should be using generics instead.

2. **Forgetting that covariant collections can throw at runtime.** Assigning `List<String>` to `List<Object>` compiles fine, but adding a non-`String` to the `List<Object>` reference throws at runtime. If you need a truly mixed list, declare it as `List<Object>` from the start.

3. **Confusing `T extends SomeClass` (bound) with `T implements SomeClass`.** In generic bounds, `extends` is used for both class and interface constraints — there is no `implements` in a type parameter bound. `T extends Comparable<T>` means T must implement the `Comparable<T>` interface, even though `Comparable` is an abstract class.

4. **Expecting type inference to work across assignment boundaries.** Dart infers type arguments from constructor arguments, but not always from the assigned variable's type. `final Stack s = Stack()` gives you `Stack<dynamic>`, not `Stack<String>`, even if you later only push strings. Always specify the type argument when the inference context is ambiguous: `final Stack<String> s = Stack()`.

5. **Using raw types (no type argument) and getting `dynamic` behavior.** Writing `Stack()` without a type argument gives `Stack<dynamic>`. This is valid Dart but defeats the purpose of generics. Always provide explicit type arguments or ensure the context provides enough information for inference.

---

## ❓ Interview Questions

### Q1: What are generics in Dart and why are they useful?

**Answer:** Generics allow you to write classes, methods, and functions that are parameterized by a type, specified by the caller at use-site. They eliminate the need for `dynamic` casts by letting the compiler enforce type correctness throughout the generic code. For example, `Stack<String>` guarantees that only strings can be pushed and that `pop()` returns a `String` — no cast needed. Generics improve code reuse (one `Stack<T>` works for any type), improve readability (the type parameter documents intent), and catch type errors at compile time rather than runtime.

### Q2: What is a bounded type parameter and when would you use one?

**Answer:** A bounded type parameter uses `extends` to restrict which types are allowed as the type argument: `T extends Comparable<T>` means T must implement `Comparable<T>`. This is useful when the generic code needs to call methods that are not available on all types — without a bound, the compiler only allows calling `Object` methods on `T`. You use bounds when writing algorithms that require a specific capability (e.g., sorting requires `compareTo`, arithmetic requires `num`). Multiple bounds are not directly supported in Dart, but you can work around this by creating an abstract class that extends multiple interfaces and using that as the bound.

### Q3: What does "reified generics" mean in Dart?

**Answer:** Reified generics means that type arguments are preserved at runtime, not erased. In Java, `List<String>` and `List<Integer>` are both just `List` at runtime (type erasure), so `list is List<String>` always returns `true` regardless of the actual element type. In Dart, `<String>['a'] is List<String>` returns `true` and `<String>['a'] is List<int>` returns `false` — the runtime knows the actual type argument. This makes Dart's type system more predictable, enables `whereType<T>()` to work correctly, and eliminates an entire class of bugs related to unchecked casts that are common in Java generics.

### Q4: What is the difference between `List<dynamic>` and `List<Object>`?

**Answer:** `List<Object>` accepts any non-nullable value (since every non-nullable type is a subtype of `Object`), but retrieving an element gives you `Object` — you need a cast or `is` check to use it as a specific type. The compiler still enforces that you handle the `Object` type correctly. `List<dynamic>` opts out of static type checking entirely: you can add anything, retrieve anything, and call any method on the result without a cast — but errors appear at runtime instead of compile time. `List<Object>` is the safer choice when you need a heterogeneous list; `List<dynamic>` should be avoided in production code except when interfacing with untyped external data (e.g., JSON parsing).

### Q5: How does Dart handle covariance in generic collections?

**Answer:** Dart's built-in collections (`List`, `Set`, `Map`) are covariant — `List<String>` is a subtype of `List<Object>`, so you can assign a `List<String>` to a `List<Object>` variable. This is convenient for read-only use cases (every `String` is an `Object`, so reading is safe), but it creates a soundness hole for writes: adding an `int` to a `List<Object>` that actually holds a `List<String>` throws a runtime `TypeError`. Dart catches this at runtime with a type check on every write. For truly safe covariance, use `Iterable<Object>` (read-only) instead of `List<Object>` when you only need to iterate. Custom generic classes are invariant by default — `Box<String>` is not a subtype of `Box<Object>` unless you explicitly design for it.

---

## 🔑 Key Takeaways

- Generics parameterize classes and methods by type, enabling type-safe reuse without `dynamic` casts.
- Type parameters are inferred from context when possible; specify them explicitly when inference is ambiguous.
- Bounded type parameters (`T extends X`) restrict allowed types and unlock methods guaranteed by the bound.
- Dart has **reified generics** — type arguments are preserved at runtime, enabling `is List<String>` checks.
- `List<String>` is fully type-safe; `List<Object>` accepts any non-nullable value but requires casts on retrieval; `List<dynamic>` opts out of type checking entirely.
- Dart's collections are covariant (`List<String>` is a subtype of `List<Object>`), which is convenient for reads but can throw at runtime on writes.
- Use `whereType<T>()` to filter a heterogeneous collection by type — it leverages reified generics under the hood.

---

## 🔗 Related Topics

- **Previous:** [Day 10 — Mixins](./Day-10-Mixins.md)
- **Next:** [Day 12 — Advanced Collections](./Day-12-Advanced-Collections.md)
- **Day 21:** [Type System Deep Dive](../Week-3-Async-Advanced/Day-21-Type-System-Deep-Dive.md) — `covariant`, `dynamic` vs `Object?`, type promotion
- **Day 18:** [Dart 3 Features](../Week-3-Async-Advanced/Day-18-Dart3-Features.md) — records and patterns interact with generics
- **Dart Cheatsheet:** [Generics syntax quick reference](../Cheatsheets/Dart-Cheatsheet.md)
