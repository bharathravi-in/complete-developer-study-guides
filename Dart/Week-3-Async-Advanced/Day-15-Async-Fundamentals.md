# Day 15: Async Fundamentals

## 🎯 What You'll Learn
- What a `Future` is and how it models deferred computation
- Writing `async` functions and using `await` to unwrap futures
- Chaining with `.then()`, `.catchError()`, and `.whenComplete()`
- Running futures concurrently with `Future.wait` and `Future.any`
- How errors propagate through async chains
- The difference between synchronous exceptions and async errors
- Using `Future.value`, `Future.error`, and `Future.delayed`

## 📚 Core Concepts

Dart's concurrency model is single-threaded but non-blocking. Instead of spawning threads for I/O, Dart uses an **event loop** that processes a queue of microtasks and macrotasks. A `Future<T>` is a handle to a value that will be available at some point — either a result of type `T` or an error.

### The Event Loop

When Dart starts, it runs `main()` synchronously. Any `async` work is scheduled on the event loop. The loop drains the **microtask queue** first (e.g., `Future.microtask`, `scheduleMicrotask`), then picks the next event from the **event queue** (I/O, timers, `Future.delayed`). This means microtasks always run before the next event, which matters for ordering guarantees.

### `Future<T>` States

A `Future` is in one of three states:
1. **Uncompleted** — the async operation is still running.
2. **Completed with a value** — the operation succeeded; `.then()` callbacks fire.
3. **Completed with an error** — the operation failed; `.catchError()` callbacks fire.

Once completed, a `Future` never changes state. You can attach multiple `.then()` listeners, but each gets its own chain.

### `async` / `await`

Marking a function `async` makes it return a `Future` automatically. Inside an `async` function, `await` suspends execution until the awaited `Future` completes, then resumes with the unwrapped value. This makes async code read like synchronous code while remaining non-blocking.

```dart
Future<String> fetchUser() async {
  await Future.delayed(Duration(seconds: 1)); // simulate I/O
  return 'Alice';
}
```

The return type is `Future<String>` even though the function body returns a plain `String` — the `async` keyword wraps it automatically.

### Error Propagation

Errors in `async` functions propagate as rejected futures. An uncaught `throw` inside an `async` function completes the returned `Future` with that error. You can catch it with `try/catch` inside the `async` function, or with `.catchError()` on the returned `Future`.

If you `await` a future that completed with an error and don't catch it, the error is re-thrown at the `await` site — exactly like a synchronous exception.

### `Future.wait` vs `Future.any`

`Future.wait(List<Future>)` runs all futures concurrently and waits for **all** to complete. If any future errors, `Future.wait` completes with that error (but all futures still run). Use `eagerError: false` to collect all errors.

`Future.any(List<Future>)` completes as soon as the **first** future completes (with value or error). The other futures continue running but their results are ignored.

### `.then()` / `.catchError()` / `.whenComplete()`

These are the callback-style API for futures, predating `async/await`. They return new `Future` objects, enabling chaining. `.whenComplete()` is like `finally` — it runs regardless of success or error but does not receive the value.

```dart
fetchUser()
  .then((name) => print('Hello $name'))
  .catchError((e) => print('Error: $e'))
  .whenComplete(() => print('Done'));
```

Prefer `async/await` for readability; use `.then()` chains when you need to compose futures without `async` context (e.g., in constructors or synchronous code paths).

### `Future.value` and `Future.error`

`Future.value(x)` creates an already-completed future. `Future.error(e)` creates an already-failed future. Both are useful for testing and for returning early from functions that are typed to return a `Future`.

## 💻 Code Examples

### Example 1: Basic async/await

```dart
import 'dart:async';

// Simulates a network call that takes 500ms
Future<String> fetchGreeting(String name) async {
  await Future.delayed(const Duration(milliseconds: 500));
  if (name.isEmpty) throw ArgumentError('Name cannot be empty');
  return 'Hello, $name!';
}

void main() async {
  // await suspends main() until fetchGreeting completes
  final greeting = await fetchGreeting('Dart');
  print(greeting); // Hello, Dart!

  // Error handling with try/catch — same syntax as synchronous code
  try {
    await fetchGreeting('');
  } on ArgumentError catch (e) {
    print('Caught: $e'); // Caught: Invalid argument(s): Name cannot be empty
  }
}
```

### Example 2: .then() / .catchError() chaining

```dart
Future<int> divide(int a, int b) async {
  if (b == 0) throw UnsupportedError('Division by zero');
  return a ~/ b; // integer division
}

void main() {
  divide(10, 2)
      .then((result) {
        print('Result: $result'); // Result: 5
        return result * 2; // return value becomes next future's value
      })
      .then((doubled) => print('Doubled: $doubled')) // Doubled: 10
      .catchError(
        (Object e) => print('Error: $e'),
        test: (e) => e is UnsupportedError, // only catch this type
      )
      .whenComplete(() => print('Chain complete'));
}
```

### Example 3: Future.wait — concurrent execution

```dart
Future<String> fetchA() async {
  await Future.delayed(const Duration(milliseconds: 300));
  return 'A';
}

Future<String> fetchB() async {
  await Future.delayed(const Duration(milliseconds: 200));
  return 'B';
}

Future<String> fetchC() async {
  await Future.delayed(const Duration(milliseconds: 100));
  return 'C';
}

void main() async {
  final stopwatch = Stopwatch()..start();

  // All three run concurrently — total time ≈ 300ms, not 600ms
  final results = await Future.wait([fetchA(), fetchB(), fetchC()]);
  print(results); // [A, B, C] — order matches input, not completion order

  stopwatch.stop();
  print('Elapsed: ${stopwatch.elapsedMilliseconds}ms'); // ~300ms
}
```

### Example 4: Future.any and error propagation

```dart
Future<String> slowSource() async {
  await Future.delayed(const Duration(seconds: 2));
  return 'slow result';
}

Future<String> fastSource() async {
  await Future.delayed(const Duration(milliseconds: 100));
  return 'fast result';
}

Future<String> failingSource() async {
  await Future.delayed(const Duration(milliseconds: 50));
  throw StateError('Source unavailable');
}

void main() async {
  // Future.any — first to complete wins
  final winner = await Future.any([slowSource(), fastSource()]);
  print(winner); // fast result

  // If the fastest future errors, Future.any propagates that error
  try {
    await Future.any([failingSource(), slowSource()]);
  } on StateError catch (e) {
    print('Any failed: $e'); // Any failed: Bad state: Source unavailable
  }

  // Future.wait with eagerError: false collects all errors
  final futures = [
    Future<int>.value(1),
    Future<int>.error('oops'),
    Future<int>.value(3),
  ];
  try {
    await Future.wait(futures, eagerError: false);
  } catch (e) {
    print('wait error: $e'); // wait error: oops
  }
}
```

## ⚠️ Common Pitfalls

- **Forgetting `await`**: Calling an `async` function without `await` returns a `Future` immediately. The code continues before the async work finishes, leading to race conditions or stale data.
- **Mixing `async/await` and `.then()` carelessly**: Returning a `Future` from inside `.then()` flattens it automatically, but returning a value from inside `await` does not — they behave differently. Stick to one style per function.
- **Unhandled future errors**: A `Future` that completes with an error and has no error handler will trigger an unhandled exception. In Flutter this crashes the app. Always attach `.catchError()` or wrap `await` in `try/catch`.
- **`Future.wait` partial failure**: By default, `Future.wait` throws on the first error but all futures still run. If you need all results (including errors), use `Future.wait(..., eagerError: false)` and handle errors individually.
- **`async` in constructors**: Dart constructors cannot be `async`. Use a static factory method or a `FutureBuilder` in Flutter instead.

## ❓ Interview Questions

### Q1: What is the Dart event loop and how does it relate to `Future`?
**Answer**: Dart runs on a single thread with an event loop that processes two queues: the microtask queue and the event queue. `Future` callbacks (`.then()`, `await` continuations) are scheduled as microtasks or events depending on how the `Future` was created. The event loop drains all microtasks before picking the next event, ensuring that microtask-scheduled code runs before I/O callbacks. This model allows Dart to handle thousands of concurrent I/O operations without threads, because waiting for I/O never blocks the thread — it just schedules a callback.

### Q2: What is the difference between `async/await` and `.then()/.catchError()`?
**Answer**: Both are ways to work with `Future` values, but `async/await` is syntactic sugar that makes async code look synchronous and is generally more readable. Under the hood, the Dart compiler transforms `async/await` into a state machine that uses `.then()` and `.catchError()` internally. The key practical difference is that `try/catch` works naturally with `await`, while `.then()` chains require `.catchError()` for error handling. `async/await` also makes it easier to use loops and conditional logic with async operations.

### Q3: How does `Future.wait` differ from awaiting futures sequentially?
**Answer**: Awaiting futures sequentially (one `await` after another) runs them one at a time — the second doesn't start until the first completes. `Future.wait` starts all futures simultaneously and waits for all to finish, so the total time is roughly the duration of the slowest future rather than the sum of all durations. This is a critical performance difference for independent I/O operations like fetching multiple API endpoints. Use sequential `await` only when each operation depends on the result of the previous one.

### Q4: What happens if you `throw` inside an `async` function?
**Answer**: Throwing inside an `async` function does not propagate synchronously to the caller. Instead, the returned `Future` completes with that error. The caller must either `await` the future inside a `try/catch` block or attach a `.catchError()` handler to observe the error. If neither is done, the error becomes an unhandled future error, which in Dart CLI programs prints a warning and in Flutter triggers the `FlutterError.onError` handler.

### Q5: When would you use `Future.value()` or `Future.error()`?
**Answer**: `Future.value(x)` creates an already-completed future, useful when a function is typed to return `Future<T>` but you have the value synchronously (e.g., a cache hit). `Future.error(e)` creates an already-failed future, useful for returning early errors from async-typed functions without using `async/throw`. Both are also invaluable in tests for mocking async dependencies without real delays.

### Q6: Explain error propagation through a `.then()` chain.
**Answer**: In a `.then()` chain, if any callback throws or returns a failed future, the error skips all subsequent `.then()` callbacks and travels down the chain until it hits a `.catchError()` handler. If no handler is found, the error becomes unhandled. A `.catchError()` can optionally take a `test` parameter to only catch specific error types, letting other errors continue propagating. After a `.catchError()` handles an error, the chain resumes as a successful future with the value returned by the error handler.

## 🔑 Key Takeaways
- `Future<T>` represents a value available later; it's either pending, completed with a value, or completed with an error
- `async/await` is syntactic sugar over `.then()/.catchError()` — prefer it for readability
- `Future.wait` runs futures concurrently; sequential `await` runs them one at a time
- Errors in `async` functions complete the returned `Future` with an error — use `try/catch` around `await`
- `Future.any` resolves with the first future to complete (value or error)
- Never forget to handle errors on futures — unhandled async errors crash Flutter apps

## 🔗 Related Topics
- [Day 16: Streams](./Day-16-Streams.md) — push-based async sequences built on the same event loop
- [Day 17: Isolates](./Day-17-Isolates.md) — true parallelism when async isn't enough
- [Day 23: State Management Patterns](../Week-4-Flutter-Dart-Interview/Day-23-State-Management-Patterns.md) — `FutureBuilder` in Flutter
- [JavaScript Async/Await](../../JavaScript/30-Day-JS-Mastery/Week-2-Intermediate/Day-12-Async-JavaScript.md) — compare with JS Promises
