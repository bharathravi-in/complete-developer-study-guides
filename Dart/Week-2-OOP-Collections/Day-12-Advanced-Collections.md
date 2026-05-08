# Day 12: Advanced Collections

## 🎯 What You'll Learn

- The difference between `Iterable` and `Iterator` and how they relate
- How to implement a custom `Iterable` and `Iterator` from scratch
- What lazy evaluation means in Dart's `Iterable` API and why it matters for performance
- How to chain `where`, `map`, `expand`, `takeWhile`, and `skipWhile` lazily
- The difference between `fold` and `reduce` and when to use each
- How `any`, `every`, `firstWhere`, `lastWhere`, and `singleWhere` work
- The `groupBy` pattern using `Map` and `fold`
- Types from `dart:collection`: `LinkedHashMap`, `SplayTreeMap`, `Queue`, `DoubleLinkedQueue`

---

## 📚 Core Concepts

### `Iterable` vs `Iterator`

These two interfaces work together but serve different roles:

- **`Iterable<E>`** represents a sequence of elements that can be iterated. It is the high-level abstraction — it has methods like `map`, `where`, `fold`, `toList`, etc. A `List`, `Set`, and `Map.keys` are all `Iterable`.
- **`Iterator<E>`** is the low-level cursor that does the actual traversal. It has two members: `bool moveNext()` (advances the cursor and returns `true` if there is a next element) and `E get current` (returns the current element after `moveNext()` has been called).

The relationship: `Iterable` has a factory method `Iterator<E> get iterator` that creates a fresh `Iterator` each time it is called. A `for-in` loop is syntactic sugar for calling `iterator`, then repeatedly calling `moveNext()` and reading `current`.

```dart
// What a for-in loop desugars to:
final iterable = [1, 2, 3];
final it = iterable.iterator;
while (it.moveNext()) {
  print(it.current); // 1, 2, 3
}
```

### Lazy Evaluation

Most `Iterable` methods in Dart are **lazy** — they return a new `Iterable` that describes a transformation but does not execute it until elements are actually consumed. No computation happens until you call `toList()`, `toSet()`, iterate with `for-in`, or call a terminal operation like `fold` or `length`.

This is important for performance: chaining `where`, `map`, and `take` on a million-element list does not create intermediate lists. Each element flows through the entire chain one at a time.

```dart
final result = [1, 2, 3, 4, 5, 6]
    .where((n) => n.isEven)   // lazy — no list created yet
    .map((n) => n * 10)       // lazy — still no list
    .take(2);                 // lazy — still no list

// Only NOW does computation happen:
print(result.toList()); // [20, 40]
```

Contrast this with `toList()` in the middle of a chain, which forces evaluation and creates an intermediate list — avoid this unless you need to reuse the intermediate result.

### `where` and `takeWhile` / `skipWhile`

- **`where(predicate)`**: Filters elements, keeping only those for which the predicate returns `true`. Evaluates every element.
- **`takeWhile(predicate)`**: Returns elements from the start of the sequence as long as the predicate is `true`. Stops at the first `false` — does not evaluate the rest.
- **`skipWhile(predicate)`**: Skips elements from the start as long as the predicate is `true`. Returns everything from the first `false` onward.

```dart
final nums = [2, 4, 6, 1, 8, 10];
print(nums.where((n) => n.isEven).toList());      // [2, 4, 6, 8, 10] — all evens
print(nums.takeWhile((n) => n.isEven).toList());  // [2, 4, 6] — stops at 1
print(nums.skipWhile((n) => n.isEven).toList());  // [1, 8, 10] — skips until 1
```

### `map` and `expand`

- **`map(transform)`**: Transforms each element using a function, producing a new `Iterable` of the same length.
- **`expand(toIterable)`**: Maps each element to an `Iterable` and flattens the results (equivalent to `flatMap` in other languages). Useful for one-to-many transformations.

```dart
final words = ['hello world', 'foo bar'];
final chars = words.expand((s) => s.split(' ')).toList();
print(chars); // [hello, world, foo, bar]
```

### `fold` vs `reduce`

Both accumulate a sequence into a single value, but they differ in how they handle the initial value:

- **`fold(initialValue, combine)`**: Takes an explicit initial value. Works on empty iterables (returns the initial value). The accumulator type can differ from the element type.
- **`reduce(combine)`**: Uses the first element as the initial accumulator. Throws `StateError` on an empty iterable. The accumulator must be the same type as the elements.

```dart
final nums = [1, 2, 3, 4, 5];

// fold — accumulator starts at 0, can be a different type
final sum = nums.fold(0, (acc, n) => acc + n); // 15
final product = nums.fold(1, (acc, n) => acc * n); // 120

// fold to build a different type — count even numbers
final evenCount = nums.fold(0, (acc, n) => n.isEven ? acc + 1 : acc); // 2

// reduce — first element is the initial accumulator
final max = nums.reduce((a, b) => a > b ? a : b); // 5
// [].reduce(...) throws StateError — use fold with an identity value instead
```

### `any`, `every`, `firstWhere`, `lastWhere`

These are **terminal operations** — they consume the iterable and return a non-iterable result:

- **`any(predicate)`**: Returns `true` if at least one element satisfies the predicate. Short-circuits on the first match.
- **`every(predicate)`**: Returns `true` if all elements satisfy the predicate. Short-circuits on the first failure.
- **`firstWhere(predicate, {orElse})`**: Returns the first matching element, or calls `orElse` if none found (throws if `orElse` is not provided).
- **`lastWhere(predicate, {orElse})`**: Returns the last matching element.
- **`singleWhere(predicate, {orElse})`**: Returns the single matching element; throws if zero or more than one match.

### `dart:collection` Types

The `dart:collection` library provides specialized collection types beyond the core `List`, `Set`, and `Map`:

- **`LinkedHashMap<K, V>`**: A `Map` that preserves insertion order (the default `Map` literal in Dart is already a `LinkedHashMap`).
- **`SplayTreeMap<K, V>`**: A self-balancing BST map that keeps keys in sorted order. Useful when you need sorted iteration.
- **`HashMap<K, V>`**: An unordered hash map with O(1) average operations. Slightly faster than `LinkedHashMap` when order doesn't matter.
- **`Queue<E>`** / **`DoubleLinkedQueue<E>`**: A double-ended queue supporting O(1) add/remove at both ends. Use instead of `List` when you need efficient front-insertion.
- **`UnmodifiableListView<E>`** / **`UnmodifiableMapView<K, V>`**: Read-only wrappers around existing collections.

---

## 💻 Code Examples

### Example 1: Custom `Iterable` and `Iterator` Implementation

```dart
// ── Custom Iterator: generates a Fibonacci sequence up to a limit ──────────
class FibonacciIterator implements Iterator<int> {
  final int limit; // stop when value exceeds this
  int _current = 0;
  int _next = 1;
  bool _started = false;

  FibonacciIterator(this.limit);

  @override
  int get current => _current; // returns the current value

  @override
  bool moveNext() {
    if (!_started) {
      // First call: position at the first element (0)
      _started = true;
      return _current <= limit;
    }
    // Advance: compute next Fibonacci number
    final newNext = _current + _next;
    _current = _next;
    _next = newNext;
    return _current <= limit; // false when we exceed the limit
  }
}

// ── Custom Iterable: wraps FibonacciIterator ──────────────────────────────
class FibonacciSequence extends Iterable<int> {
  final int limit;
  const FibonacciSequence(this.limit);

  // Iterable requires only this one method — everything else is derived
  @override
  Iterator<int> get iterator => FibonacciIterator(limit);
}

void main() {
  final fibs = FibonacciSequence(100);

  // for-in works because FibonacciSequence is Iterable
  print('Fibonacci up to 100:');
  for (final n in fibs) {
    process(n); // prints each number
  }

  // All Iterable methods work automatically — they use the iterator internally
  print('\nEven Fibonacci numbers: ${fibs.where((n) => n.isEven).toList()}');
  // [0, 2, 8, 34]

  print('Sum: ${fibs.fold(0, (a, b) => a + b)}');
  // 0+1+1+2+3+5+8+13+21+34+55+89 = 232

  print('Any > 50: ${fibs.any((n) => n > 50)}'); // true
  print('All < 200: ${fibs.every((n) => n < 200)}'); // true (limit is 100)

  // Each call to fibs.iterator creates a FRESH iterator — safe to iterate multiple times
  print('Count: ${fibs.length}'); // 12
}

void process(int n) => print('  $n');
```

### Example 2: Lazy Evaluation Chain — `where`, `map`, `expand`, `takeWhile`, `skipWhile`

```dart
void main() {
  // ── Lazy chain — no intermediate lists created ─────────────────────────
  final numbers = List.generate(1000000, (i) => i + 1); // 1 to 1,000,000

  // This chain processes elements one at a time — no 1M-element intermediate lists
  final result = numbers
      .where((n) => n % 3 == 0)       // keep multiples of 3 (lazy)
      .map((n) => n * n)               // square them (lazy)
      .takeWhile((n) => n < 10000)     // stop when squared value >= 10000 (lazy)
      .toList();                        // NOW evaluate — only processes ~33 elements

  print('Squares of multiples of 3 less than 10000:');
  print(result); // [9, 36, 81, 144, 225, 324, 441, 576, 729, 900, ...]

  // ── expand (flatMap) — one-to-many transformation ─────────────────────
  final sentences = [
    'the quick brown fox',
    'jumps over the lazy dog',
  ];

  // Split each sentence into words, then filter short words
  final longWords = sentences
      .expand((s) => s.split(' '))     // flatten: each sentence → list of words
      .where((w) => w.length > 3)      // keep words longer than 3 chars
      .map((w) => w.toUpperCase())     // uppercase
      .toList();

  print('\nLong words: $longWords');
  // [QUICK, BROWN, JUMPS, OVER, LAZY]

  // ── skipWhile and takeWhile on a sorted sequence ───────────────────────
  final sorted = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

  // Skip the leading small numbers, take the middle range
  final middle = sorted
      .skipWhile((n) => n < 4)         // skip 1, 2, 3
      .takeWhile((n) => n <= 7)        // take 4, 5, 6, 7
      .toList();

  print('\nMiddle range: $middle'); // [4, 5, 6, 7]

  // ── Demonstrating laziness: the transform is NOT called until consumed ──
  var callCount = 0;
  final lazy = [1, 2, 3, 4, 5]
      .map((n) {
        callCount++; // count how many times map's function is called
        return n * 2;
      })
      .where((n) => n > 4); // still lazy — nothing evaluated yet

  print('\nBefore consuming: callCount = $callCount'); // 0

  final first = lazy.first; // consume ONE element — evaluates until first match
  print('After first: callCount = $callCount, first = $first');
  // callCount = 3 (evaluated 1→2, 2→4, 3→6; 6>4 so stops)
  // first = 6
}
```

### Example 3: `fold` vs `reduce`, `any`/`every`/`firstWhere`/`lastWhere`, `groupBy` Pattern

```dart
import 'dart:collection' show SplayTreeMap;

// ── Sample data ────────────────────────────────────────────────────────────
class Transaction {
  final String category;
  final double amount;
  final DateTime date;

  const Transaction(this.category, this.amount, this.date);

  @override
  String toString() => 'Transaction($category, \$$amount)';
}

// ── groupBy helper — groups elements by a key function ────────────────────
// Returns a Map<K, List<T>> where each key maps to a list of matching elements.
Map<K, List<T>> groupBy<T, K>(Iterable<T> items, K Function(T) keyOf) {
  return items.fold(
    <K, List<T>>{}, // initial accumulator: empty map
    (map, item) {
      final key = keyOf(item);
      // getOrPut pattern: create the list if the key doesn't exist yet
      (map[key] ??= []).add(item);
      return map;
    },
  );
}

void main() {
  final transactions = [
    Transaction('food', 12.50, DateTime(2024, 1, 5)),
    Transaction('transport', 3.20, DateTime(2024, 1, 6)),
    Transaction('food', 8.75, DateTime(2024, 1, 7)),
    Transaction('entertainment', 25.00, DateTime(2024, 1, 8)),
    Transaction('transport', 4.50, DateTime(2024, 1, 9)),
    Transaction('food', 15.00, DateTime(2024, 1, 10)),
  ];

  final amounts = transactions.map((t) => t.amount).toList();

  // ── fold — safe on empty, can change accumulator type ─────────────────
  final total = amounts.fold(0.0, (sum, a) => sum + a);
  print('Total: \$${total.toStringAsFixed(2)}'); // Total: $68.95

  // fold to build a summary string — accumulator type differs from element type
  final summary = transactions.fold(
    StringBuffer(),
    (buf, t) => buf..write('${t.category}:\$${t.amount} '),
  ).toString().trim();
  print('Summary: $summary');

  // ── reduce — uses first element as initial value ───────────────────────
  final maxAmount = amounts.reduce((a, b) => a > b ? a : b);
  final minAmount = amounts.reduce((a, b) => a < b ? a : b);
  print('Max: \$$maxAmount, Min: \$$minAmount'); // Max: $25.0, Min: $3.2

  // ── any / every ───────────────────────────────────────────────────────
  print('Any > \$20: ${amounts.any((a) => a > 20)}');     // true
  print('All > \$1:  ${amounts.every((a) => a > 1)}');    // true
  print('All > \$10: ${amounts.every((a) => a > 10)}');   // false

  // ── firstWhere / lastWhere ────────────────────────────────────────────
  final firstFood = transactions.firstWhere(
    (t) => t.category == 'food',
    orElse: () => throw StateError('No food transactions'),
  );
  print('First food: $firstFood'); // Transaction(food, $12.5)

  final lastFood = transactions.lastWhere((t) => t.category == 'food');
  print('Last food: $lastFood'); // Transaction(food, $15.0)

  // orElse returns a default when no match is found
  final luxury = transactions.firstWhere(
    (t) => t.amount > 100,
    orElse: () => Transaction('none', 0, DateTime.now()),
  );
  print('Luxury: $luxury'); // Transaction(none, $0.0)

  // ── groupBy pattern ───────────────────────────────────────────────────
  final byCategory = groupBy(transactions, (t) => t.category);

  // Use SplayTreeMap to iterate categories in sorted order
  final sorted = SplayTreeMap<String, List<Transaction>>.from(byCategory);

  print('\nSpending by category:');
  for (final entry in sorted.entries) {
    final categoryTotal =
        entry.value.fold(0.0, (sum, t) => sum + t.amount);
    print('  ${entry.key}: \$${categoryTotal.toStringAsFixed(2)} '
        '(${entry.value.length} transactions)');
  }
  // entertainment: $25.00 (1 transactions)
  // food: $36.25 (3 transactions)
  // transport: $7.70 (2 transactions)
}
```

---

## ⚠️ Common Pitfalls

1. **Calling `toList()` in the middle of a chain and creating unnecessary intermediate lists.** `list.where(...).toList().map(...)` forces evaluation after `where`, creating a full intermediate list. Remove the intermediate `toList()` to keep the chain lazy: `list.where(...).map(...)`.

2. **Using `reduce` on a potentially empty iterable.** `[].reduce((a, b) => a + b)` throws `StateError: No element`. Always use `fold` with an identity value when the iterable might be empty, or guard with an `isEmpty` check first.

3. **Assuming `length` is O(1) on a lazy `Iterable`.** Calling `.length` on a lazy `Iterable` (not a `List`) iterates the entire sequence to count elements — it is O(n). If you need the length of a lazy chain, call `toList().length` once and cache the result, or restructure to avoid needing the length.

4. **Mutating a collection while iterating it.** Modifying a `List` (adding or removing elements) while iterating it with `for-in` throws a `ConcurrentModificationError`. Collect the elements to modify first (e.g., with `where(...).toList()`), then apply the modifications.

5. **Confusing `where` with `takeWhile`.** `where` evaluates every element and keeps all matches. `takeWhile` stops at the first non-match — elements after the first `false` are never evaluated, even if they would match. On an unsorted list, `takeWhile` will miss matches that come after a non-matching element.

---

## ❓ Interview Questions

### Q1: What is the difference between `Iterable` and `Iterator` in Dart?

**Answer:** `Iterable<E>` is the high-level abstraction representing a sequence of elements — it provides the rich API (`map`, `where`, `fold`, `toList`, etc.) and has a single required method: `Iterator<E> get iterator`. `Iterator<E>` is the low-level cursor that performs the actual traversal — it has `bool moveNext()` (advance and return whether there is a next element) and `E get current` (the current element). The relationship is that `Iterable` creates a fresh `Iterator` each time `iterator` is called, allowing multiple independent traversals. A `for-in` loop desugars to calling `iterator`, then looping with `moveNext()` and reading `current`. You implement `Iterable` when creating custom sequences; you rarely implement `Iterator` directly unless you need custom traversal logic.

### Q2: What is lazy evaluation in Dart's Iterable API?

**Answer:** Lazy evaluation means that `Iterable` transformation methods (`map`, `where`, `expand`, `takeWhile`, `skipWhile`) return a new `Iterable` that describes the transformation but does not execute it until elements are actually consumed. No computation happens and no intermediate collections are created until you call a terminal operation like `toList()`, `toSet()`, `fold()`, `first`, or iterate with `for-in`. This is important for performance: chaining multiple transformations on a large collection processes each element through the entire chain one at a time, avoiding the creation of large intermediate lists. The trade-off is that each traversal re-executes the chain — if you need to traverse the result multiple times, call `toList()` once and cache it.

### Q3: What is the difference between `fold` and `reduce`?

**Answer:** Both accumulate a sequence into a single value, but `fold` takes an explicit initial accumulator value while `reduce` uses the first element as the initial accumulator. `fold` is safer: it works on empty iterables (returning the initial value) and allows the accumulator type to differ from the element type (e.g., folding a `List<String>` into an `int` count). `reduce` throws `StateError` on an empty iterable and requires the accumulator to be the same type as the elements. In practice, prefer `fold` for robustness — use `reduce` only when you are certain the iterable is non-empty and the accumulator type matches the element type (e.g., finding the maximum of a non-empty list of numbers).

### Q4: How does `expand` work and when would you use it?

**Answer:** `expand(toIterable)` maps each element to an `Iterable` and then flattens all the resulting iterables into a single sequence — it is equivalent to `flatMap` in Scala/Kotlin or `Array.prototype.flatMap` in JavaScript. For example, `['a b', 'c d'].expand((s) => s.split(' '))` produces `['a', 'b', 'c', 'd']`. Use `expand` for one-to-many transformations: when each input element should produce zero, one, or multiple output elements. Common use cases include flattening nested lists, splitting strings into tokens, and generating multiple derived values from each input element. Like all `Iterable` methods, `expand` is lazy.

### Q5: What is the difference between `where` and `takeWhile`?

**Answer:** `where(predicate)` evaluates every element in the sequence and keeps all elements for which the predicate returns `true`, regardless of their position. `takeWhile(predicate)` evaluates elements from the start and returns them as long as the predicate is `true` — it stops permanently at the first element that returns `false`, never evaluating subsequent elements. On a sorted sequence, `takeWhile` is efficient for extracting a prefix (e.g., all elements less than a threshold). On an unsorted sequence, `takeWhile` will miss matching elements that appear after the first non-match, while `where` would find them all. Use `where` for general filtering; use `takeWhile` (and `skipWhile`) for prefix/suffix operations on ordered sequences.

---

## 🔑 Key Takeaways

- `Iterable` is the high-level sequence abstraction; `Iterator` is the low-level cursor. Implement `Iterable` for custom sequences — all rich methods come for free.
- Most `Iterable` methods are lazy — no computation happens until elements are consumed. Avoid intermediate `toList()` calls in chains.
- `fold` is safer than `reduce`: it handles empty iterables and allows a different accumulator type.
- `where` filters all elements; `takeWhile`/`skipWhile` operate on ordered prefixes/suffixes and short-circuit.
- `expand` is `flatMap` — use it for one-to-many transformations.
- `any` and `every` short-circuit; `firstWhere`/`lastWhere` accept an `orElse` fallback.
- Use `dart:collection` types (`SplayTreeMap`, `Queue`) when you need sorted iteration or efficient front-insertion.

---

## 🔗 Related Topics

- **Previous:** [Day 11 — Generics](./Day-11-Generics.md)
- **Next:** [Day 13 — Extension Methods](./Day-13-Extension-Methods.md)
- **Day 06:** [Collections Fundamentals](../Week-1-Dart-Fundamentals/Day-06-Collections.md) — `List`, `Set`, `Map` basics
- **Day 21:** [Type System Deep Dive](../Week-3-Async-Advanced/Day-21-Type-System-Deep-Dive.md) — `Iterable` and type promotion
- **Dart Cheatsheet:** [Collections quick reference](../Cheatsheets/Dart-Cheatsheet.md)
- **Cross-plan:** [DS Day 02 — Two Pointer](../../DS/Days/Day_02_Two_Pointer.md) — algorithmic patterns that map naturally to `Iterable` chains
