# Day 06: Collections

## 🎯 What You'll Learn

- How `List<E>` works — ordered, indexed, allows duplicates — and its most useful methods
- How `Set<E>` enforces uniqueness and supports set-algebra operations (`union`, `intersection`, `difference`)
- How `Map<K, V>` stores key-value pairs and the full API for reading, writing, and iterating entries
- How the spread operator `...` (and null-aware `...?`) merges collections inline
- How collection-if and collection-for let you build collections declaratively without imperative loops
- The difference between growable and fixed-length lists (`List.filled`, `List.generate`)
- How to create unmodifiable collections with `List.unmodifiable`, `Map.unmodifiable`, and `const`
- Why type safety matters — `List<String>` vs `List<dynamic>` and the runtime implications

---

## 📚 Core Concepts

### List\<E\> — Ordered, Indexed, Allows Duplicates

A `List<E>` is Dart's equivalent of an array. Elements are stored in insertion order, accessed by zero-based index, and duplicates are allowed. You create one with a literal `[]` or with factory constructors.

```dart
var fruits = ['apple', 'banana', 'cherry']; // List<String> inferred
```

Key methods:

| Method | What it does |
|--------|-------------|
| `add(e)` | Appends one element |
| `addAll(iterable)` | Appends every element from another iterable |
| `insert(index, e)` | Inserts at a specific position |
| `remove(e)` | Removes the first occurrence of `e` |
| `removeAt(index)` | Removes the element at `index` |
| `indexOf(e)` | Returns the first index of `e`, or `-1` |
| `contains(e)` | Returns `true` if `e` is in the list |
| `length` | Number of elements |
| `isEmpty` / `isNotEmpty` | Quick emptiness checks |
| `sublist(start, end?)` | Returns a new list slice |
| `reversed` | Returns a lazy `Iterable` in reverse order |
| `sort([compare?])` | Sorts in place (mutates the list) |
| `shuffle([random?])` | Randomises order in place |

**Growable vs fixed-length lists.** By default, list literals are growable — you can `add` and `remove` freely. `List.filled(n, value)` creates a fixed-length list pre-filled with a value; you can update elements but cannot change the length. `List.generate(n, (i) => ...)` creates a growable list by calling a generator function for each index, which is handy for computed sequences.

```dart
final fixed = List<int>.filled(5, 0);       // [0, 0, 0, 0, 0], fixed length
final squares = List<int>.generate(5, (i) => i * i); // [0, 1, 4, 9, 16], growable
```

### Set\<E\> — Unordered, No Duplicates

A `Set<E>` stores unique values with no guaranteed order. Adding a duplicate is silently ignored. Use a set when membership testing is the primary operation — `contains` is O(1) for `HashSet` (the default), compared to O(n) for a list.

```dart
var colors = {'red', 'green', 'blue'}; // Set<String>
colors.add('red'); // no-op — already present
```

Set-algebra methods: `union(other)`, `intersection(other)`, `difference(other)` all return new `Set` instances without mutating the originals.

### Map\<K, V\> — Key-Value Pairs

A `Map<K, V>` associates unique keys with values. The literal syntax uses `{key: value}` pairs. Key lookup is O(1) for `HashMap` (the default).

```dart
var scores = {'Alice': 95, 'Bob': 87}; // Map<String, int>
scores['Carol'] = 72;                   // add or update via [] operator
```

Important members:

| Member | What it does |
|--------|-------------|
| `map[key]` | Returns value or `null` if absent |
| `putIfAbsent(key, () => value)` | Inserts only if key is missing |
| `update(key, (v) => newV)` | Updates an existing value |
| `remove(key)` | Removes the entry, returns the value |
| `containsKey(key)` | Membership test on keys |
| `containsValue(value)` | Membership test on values (O(n)) |
| `keys` / `values` | Lazy iterables of keys / values |
| `entries` | Iterable of `MapEntry<K, V>` objects |
| `forEach((k, v) => ...)` | Iterates all entries |

### Spread Operator `...` and Null-Aware Spread `...?`

The spread operator inserts all elements of an iterable inline inside a collection literal. This is far cleaner than calling `addAll` after construction.

```dart
final a = [1, 2, 3];
final b = [0, ...a, 4]; // [0, 1, 2, 3, 4]
```

The null-aware variant `...?` skips the spread entirely when the iterable is `null`, preventing a null-dereference error:

```dart
List<int>? extras;
final safe = [1, 2, ...?extras]; // [1, 2] — no crash
```

### Collection-if: Conditional Element Inclusion

Collection-if lets you include an element (or a spread) only when a condition is true, keeping the collection literal self-contained:

```dart
final isAdmin = true;
final menu = [
  'Home',
  'Profile',
  if (isAdmin) 'Admin Panel', // included only when isAdmin is true
];
```

An optional `else` branch is also supported: `if (cond) x else y`.

### Collection-for: Generating Elements from an Iterable

Collection-for embeds a `for-in` loop directly inside a literal, transforming or filtering another iterable without a separate variable:

```dart
final numbers = [1, 2, 3, 4, 5];
final evens = [for (final n in numbers) if (n.isEven) n]; // [2, 4]
```

You can nest collection-for and collection-if freely, and even spread inside the loop body.

### Unmodifiable Collections

To prevent mutation after construction, use the unmodifiable factory constructors or `const`:

```dart
final locked = List<int>.unmodifiable([1, 2, 3]); // throws UnsupportedError on mutation
final lockedMap = Map<String, int>.unmodifiable({'a': 1});
const constList = [10, 20, 30]; // compile-time constant, deeply immutable
```

`const` collections are canonicalised — two identical `const` literals share the same object in memory.

### Type Safety in Collections

Prefer typed collections (`List<String>`) over `List<dynamic>`. With a typed list, the compiler catches type mismatches at compile time and you get full IDE autocompletion. `List<dynamic>` defers all checks to runtime, which can cause `TypeError` surprises.

```dart
List<String> names = ['Alice', 'Bob'];
// names.add(42); // compile-time error — good!

List<dynamic> anything = ['Alice', 42]; // allowed, but risky
```

---

## 💻 Code Examples

### Example 1: List Operations — Creation, Mutation, Searching, Sorting

```dart
void main() {
  // --- Creation ---
  var fruits = <String>['banana', 'apple', 'cherry', 'apple'];
  print(fruits.length);       // 4
  print(fruits.contains('apple')); // true
  print(fruits.indexOf('cherry')); // 2

  // --- Mutation ---
  fruits.add('date');
  fruits.addAll(['elderberry', 'fig']);
  fruits.insert(0, 'avocado'); // insert at index 0
  fruits.remove('apple');      // removes first 'apple' only
  fruits.removeAt(0);          // removes 'avocado'
  print(fruits); // [banana, cherry, apple, date, elderberry, fig]

  // --- Slicing ---
  final slice = fruits.sublist(1, 4); // indices 1, 2, 3
  print(slice); // [cherry, apple, date]

  // --- Sorting ---
  final sorted = [...fruits]..sort(); // copy then sort in place
  print(sorted); // alphabetical order

  // --- Reversed (lazy iterable, not a new list) ---
  final rev = fruits.reversed.toList();
  print(rev.first); // fig

  // --- Fixed-length list ---
  final matrix = List<int>.filled(9, 0); // 3×3 grid flattened
  matrix[4] = 1; // centre cell
  print(matrix); // [0, 0, 0, 0, 1, 0, 0, 0, 0]

  // --- Generated list ---
  final cubes = List<int>.generate(5, (i) => i * i * i);
  print(cubes); // [0, 1, 8, 27, 64]
}
```

### Example 2: Set and Map Operations with Spread Operators

```dart
void main() {
  // --- Set basics ---
  var primes = <int>{2, 3, 5, 7, 11};
  primes.add(13);
  primes.add(7);          // duplicate — silently ignored
  print(primes.length);   // 6

  var odds = <int>{1, 3, 5, 7, 9, 11};

  // Set algebra — all return new sets
  print(primes.intersection(odds)); // {3, 5, 7, 11}
  print(primes.union(odds));        // {1, 2, 3, 5, 7, 9, 11, 13}
  print(primes.difference(odds));   // {2, 13} — in primes but not odds

  // --- Map basics ---
  var inventory = <String, int>{
    'apples': 10,
    'bananas': 5,
  };

  inventory['cherries'] = 20;                        // add new key
  inventory.update('apples', (v) => v + 3);          // 10 → 13
  inventory.putIfAbsent('dates', () => 7);            // adds 'dates': 7
  inventory.putIfAbsent('apples', () => 999);         // no-op — key exists

  print(inventory.containsKey('bananas'));  // true
  print(inventory.containsValue(5));        // true

  // Iterate entries
  inventory.forEach((key, value) => print('$key: $value'));

  // keys / values as iterables
  final keyList = inventory.keys.toList()..sort();
  print(keyList); // [apples, bananas, cherries, dates]

  // --- Spread operator ---
  final base = [1, 2, 3];
  final extended = [0, ...base, 4, 5]; // [0, 1, 2, 3, 4, 5]
  print(extended);

  // Null-aware spread — safe when source may be null
  List<String>? extras;
  final tags = ['dart', 'flutter', ...?extras]; // no crash
  print(tags); // [dart, flutter]

  // Spread into a Map
  final defaults = {'theme': 'light', 'lang': 'en'};
  final userPrefs = {'lang': 'fr'};
  final merged = {...defaults, ...userPrefs}; // userPrefs overrides defaults
  print(merged); // {theme: light, lang: fr}
}
```

### Example 3: Collection-if and Collection-for — Declarative Collection Building

```dart
void main() {
  // --- Collection-if ---
  final isLoggedIn = true;
  final isPremium = false;

  final navItems = [
    'Home',
    'Search',
    if (isLoggedIn) 'Profile',           // included
    if (isLoggedIn && isPremium) 'VIP',  // excluded
    if (!isLoggedIn) 'Sign In' else 'Sign Out', // else branch
  ];
  print(navItems); // [Home, Search, Profile, Sign Out]

  // --- Collection-for ---
  final words = ['hello', 'world', 'dart'];

  // Transform: uppercase each word
  final upper = [for (final w in words) w.toUpperCase()];
  print(upper); // [HELLO, WORLD, DART]

  // Filter + transform in one expression
  final longUpper = [
    for (final w in words)
      if (w.length > 4) w.toUpperCase(), // only words longer than 4 chars
  ];
  print(longUpper); // [HELLO, WORLD]

  // Nested collection-for: build a multiplication table as a flat list
  final table = [
    for (var i = 1; i <= 3; i++)
      for (var j = 1; j <= 3; j++)
        i * j,
  ];
  print(table); // [1, 2, 3, 2, 4, 6, 3, 6, 9]

  // Collection-for with spread: flatten a list of lists
  final groups = [
    [1, 2],
    [3, 4],
    [5, 6],
  ];
  final flat = [for (final g in groups) ...g]; // spread each sub-list
  print(flat); // [1, 2, 3, 4, 5, 6]

  // Build a Map with collection-for
  final wordLengths = {
    for (final w in words) w: w.length,
  };
  print(wordLengths); // {hello: 5, world: 5, dart: 4}

  // --- Unmodifiable collections ---
  final locked = List<int>.unmodifiable([10, 20, 30]);
  try {
    locked.add(40); // throws UnsupportedError at runtime
  } catch (e) {
    print('Cannot mutate: $e');
  }

  const constSet = {1, 2, 3}; // compile-time constant set
  print(constSet.contains(2)); // true
}
```

---

## ⚠️ Common Pitfalls

1. **Mutating a list while iterating it.** Calling `remove` or `add` inside a `for-in` loop over the same list throws a `ConcurrentModificationError`. Iterate a copy (`[...list]`) or collect indices to remove and process them after the loop.

2. **`reversed` returns a lazy `Iterable`, not a `List`.** `list.reversed` does not allocate a new list — it is a lazy view. If you need random access or want to pass it to something expecting a `List`, call `.toList()` on it first.

3. **`List.filled` creates a fixed-length list.** Calling `add` or `remove` on a list created with `List.filled(n, value)` throws an `UnsupportedError`. Use a list literal or `List.generate` when you need a growable list.

4. **Map `[]` operator returns a nullable value.** `map[key]` returns `T?`, not `T`, because the key might not exist. Always null-check or use `map[key]!` only when you are certain the key is present, or prefer `map.putIfAbsent` / `map.update` for safer access patterns.

5. **Set literal `{}` vs Map literal `{}`.** An empty `{}` is inferred as `Map<dynamic, dynamic>`, not a `Set`. Write `<String>{}` or `Set<String>()` to get an empty set.

---

## ❓ Interview Questions

### Q1: What is the difference between `List`, `Set`, and `Map` in Dart?

**Answer:** A `List<E>` is an ordered, indexed sequence that allows duplicate elements — think of it as a resizable array. A `Set<E>` is an unordered collection of unique values; adding a duplicate is a no-op and membership testing is O(1) for the default `HashSet`. A `Map<K, V>` stores key-value pairs where each key is unique; it is the right choice when you need to look up a value by a named or computed key rather than by position. The three types serve different access patterns: positional access → `List`, membership testing → `Set`, keyed lookup → `Map`.

### Q2: How do spread operators work in Dart collections?

**Answer:** The spread operator `...` inserts every element of an iterable inline inside a collection literal, equivalent to calling `addAll` but usable at construction time. It works in `List`, `Set`, and `Map` literals — for maps, each spread must be a `Map` and later entries override earlier ones for duplicate keys. The null-aware variant `...?` silently skips the spread when the source is `null`, preventing a null-dereference error without requiring an explicit null check. Both variants are purely syntactic sugar resolved at compile time; they produce no additional runtime overhead beyond the element insertions themselves.

### Q3: What is collection-if and collection-for in Dart?

**Answer:** Collection-if and collection-for are control-flow elements that can appear directly inside collection literals (`[]`, `{}`, `<>{}`), making it possible to build collections declaratively without separate imperative loops or conditional statements. Collection-if (`if (cond) element` or `if (cond) element else other`) conditionally includes zero or one element (or a spread). Collection-for (`for (final x in iterable) expr`) generates zero or more elements by iterating another iterable. They can be nested and combined freely — for example, `[for (final x in list) if (x > 0) x]` filters a list in a single expression. This style is idiomatic Dart and is preferred over building a list with `add` calls inside a loop.

### Q4: What is the difference between a growable and a fixed-length list?

**Answer:** A growable list (the default for list literals and `List.generate`) allows `add`, `addAll`, `remove`, `removeAt`, and `insert` — its length can change at runtime. A fixed-length list, created with `List.filled(n, value)`, has a length that is set at construction and cannot be changed; calling `add` or `remove` throws an `UnsupportedError`. You can still read and write elements by index on a fixed-length list. Fixed-length lists are useful when you know the exact size upfront and want to prevent accidental resizing, or when you need a pre-allocated buffer for performance-sensitive code.

### Q5: How do you create an unmodifiable collection in Dart?

**Answer:** There are three main approaches. First, `List.unmodifiable(source)`, `Set.unmodifiable(source)`, and `Map.unmodifiable(source)` wrap an existing collection in a view that throws `UnsupportedError` on any mutation attempt — the underlying data is copied at construction time. Second, `const` collection literals (`const [1, 2, 3]`) are compile-time constants that are deeply immutable and canonicalised in memory; they cannot be mutated and are shared across all references to the same literal. Third, you can expose a collection through an `UnmodifiableListView` (from `dart:collection`) to prevent external mutation while still allowing internal mutation via the backing list. The `const` approach is the most efficient for static data; the factory constructors are appropriate for runtime-computed data that should not be mutated after creation.

---

## 🔑 Key Takeaways

- `List` = ordered + indexed + duplicates allowed; `Set` = unordered + unique; `Map` = keyed lookup.
- Spread `...` and `...?` merge collections inline at construction time — prefer them over post-construction `addAll`.
- Collection-if and collection-for replace imperative loops for building collections, producing cleaner and more readable code.
- `List.filled` is fixed-length; list literals and `List.generate` are growable — know which you need before you reach for `add`.
- Always prefer typed collections (`List<String>`) over `List<dynamic>` to catch type errors at compile time.
- `Map[key]` returns a nullable `T?` — always handle the `null` case to avoid runtime errors.
- `const` collections are compile-time constants and the most efficient form of immutability for static data.

---

## 🔗 Related Topics

- [Day 05: Functions](./Day-05-Functions.md) — closures and higher-order functions used with collection methods like `sort` and `forEach`
- [Day 07: Error Handling](./Day-07-Error-Handling.md) — handling `UnsupportedError` thrown by unmodifiable collections
- [Day 12: Advanced Collections](../Week-2-OOP-Collections/Day-12-Advanced-Collections.md) — `Iterable`, lazy evaluation, `where`, `map`, `fold`, `expand`, and chaining
- [DS — Complexity Analysis](../../DS/Days/Day_01_Complexity_Analysis.md) — understanding O(1) vs O(n) access patterns for `List`, `Set`, and `Map`
- [Dart Cheatsheet](../Cheatsheets/Dart-Cheatsheet.md) — quick-reference syntax for all collection types and operators
