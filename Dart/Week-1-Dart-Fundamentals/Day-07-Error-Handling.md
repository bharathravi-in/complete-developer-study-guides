# Day 07: Error Handling

## 🎯 What You'll Learn

- The difference between `Error` and `Exception` in Dart and when to use each
- How to use `try/catch/finally` to handle exceptions gracefully
- How to use `on` clauses to catch specific exception types
- How to `throw` any non-null object and create custom exceptions
- How to use `rethrow` to re-throw the current exception up the call stack
- How to capture and inspect `StackTrace` objects for debugging
- How to handle errors in async code with `await`, `Future.catchError`, and `onError`

---

## 📚 Core Concepts

### `Error` vs `Exception` — The Dart Convention

Dart draws a clear line between two categories of throwable objects:

**`Error`** represents a programmer mistake — something that should never happen in correct code. Examples include accessing a list out of bounds (`RangeError`), passing a bad argument (`ArgumentError`), or calling a method on an object in an invalid state (`StateError`). Errors signal bugs; you generally should not catch them in production code because catching them hides the underlying defect. Let them propagate and crash loudly so you can fix the root cause.

**`Exception`** represents an expected failure — something that can go wrong at runtime even in correct code. Parsing a malformed string (`FormatException`), a network timeout, or a missing file are all exceptions. These are conditions you anticipate and handle gracefully.

Both `Error` and `Exception` are interfaces (not classes you extend directly, though you can). Any non-null object can be thrown in Dart — even a plain `String` — but the convention is to throw objects that implement `Exception` for recoverable situations and let `Error` subclasses propagate for bugs.

### Built-in Types

Common built-in exceptions and errors you'll encounter:

| Type | Category | When it occurs |
|------|----------|----------------|
| `FormatException` | Exception | Parsing fails (e.g., `int.parse('abc')`) |
| `RangeError` | Error | Index out of bounds, value out of range |
| `ArgumentError` | Error | Invalid argument passed to a function |
| `StateError` | Error | Object used in an invalid state |
| `UnsupportedError` | Error | Operation not supported by this object |
| `NullThrownError` | Error | `null` was thrown (rare in null-safe code) |

### `try / catch / finally` — Basic Structure

The fundamental error-handling construct:

```dart
try {
  // code that might throw
} on SpecificType catch (e, s) {
  // handle SpecificType; e = exception, s = stack trace
} catch (e, s) {
  // catch anything else
} finally {
  // always runs — whether an exception was thrown, caught, or not
}
```

The `on` clause filters by type. You can chain multiple `on` clauses to handle different exception types differently. The `catch(e)` form captures the thrown object; `catch(e, s)` also captures the `StackTrace`. The `finally` block always executes — even if a `return` statement is hit inside `try` or `catch`.

### `throw` — Throwing Objects

You can throw any non-null object:

```dart
throw FormatException('Invalid input: $input');
throw ArgumentError.notNull('userId');
throw 'something went wrong'; // valid but unconventional
```

Prefer throwing objects that implement `Exception` for recoverable errors, or `Error` subclasses for programmer mistakes.

### Custom Exceptions

Implement the `Exception` interface to create domain-specific exceptions with structured data:

```dart
class ValidationException implements Exception {
  final String field;
  final String message;
  const ValidationException(this.field, this.message);

  @override
  String toString() => 'ValidationException: $field — $message';
}
```

### `rethrow` — Re-throwing the Current Exception

Inside a `catch` block, `rethrow` re-throws the caught exception without creating a new stack frame, preserving the original stack trace. This is useful when you want to log or inspect an exception but still let it propagate:

```dart
try {
  riskyOperation();
} catch (e, s) {
  logger.error('Operation failed', e, s);
  rethrow; // propagates original exception + stack trace
}
```

Note: `rethrow` is different from `throw e` — `throw e` resets the stack trace to the current location.

### Stack Traces

`StackTrace` is a Dart type representing the call stack at the point an exception was thrown. You capture it as the second parameter in `catch(e, s)`. You can also capture the current stack trace at any point using `StackTrace.current`:

```dart
final trace = StackTrace.current; // snapshot of the call stack right now
```

Stack traces are invaluable for debugging — always log them alongside exceptions in production error handlers.

### Error Handling in Async Code

With `async/await`, `try/catch` works exactly the same as synchronous code — the `await` expression unwraps the `Future` and re-throws any error:

```dart
Future<void> fetchData() async {
  try {
    final result = await httpClient.get(url);
    process(result);
  } on FormatException catch (e) {
    print('Bad response format: $e');
  } catch (e, s) {
    print('Unexpected error: $e\n$s');
  }
}
```

You can also use the `Future` API directly with `.catchError()` and `.onError()`, though `async/await` with `try/catch` is generally more readable. `Future.catchError` takes a callback and an optional `test` predicate to filter which errors it handles.

---

## 💻 Code Examples

### Example 1: `try / catch / on / finally` with Multiple Exception Types

```dart
import 'dart:convert';

/// Parses a JSON string and extracts the 'age' field as an integer.
/// Demonstrates chained `on` clauses and `finally`.
int parseAge(String jsonString) {
  try {
    final map = jsonDecode(jsonString) as Map<String, dynamic>;
    final raw = map['age'];

    if (raw == null) {
      // Throw a domain-specific error for missing required field
      throw ArgumentError.value(jsonString, 'jsonString', "'age' field is missing");
    }

    // int.parse throws FormatException if the value isn't a valid integer string
    return int.parse(raw.toString());
  } on FormatException catch (e) {
    // Recoverable: bad format — return a sentinel value
    print('Format error: ${e.message}');
    return -1;
  } on ArgumentError catch (e) {
    // Programmer mistake: missing required field
    print('Argument error: $e');
    return -1;
  } catch (e, s) {
    // Catch-all for anything unexpected; log the stack trace
    print('Unexpected error: $e');
    print('Stack trace:\n$s');
    return -1;
  } finally {
    // Runs regardless of outcome — good for cleanup (closing files, releasing locks)
    print('parseAge() completed for input: $jsonString');
  }
}

void main() {
  print(parseAge('{"age": "30"}')); // 30
  print(parseAge('{"age": "abc"}')); // FormatException → -1
  print(parseAge('{"name": "Alice"}')); // ArgumentError → -1
}
```

### Example 2: Custom Exceptions with Fields and Messages

```dart
/// A custom exception for HTTP-related failures.
/// Implements [Exception] so it's treated as a recoverable error.
class HttpException implements Exception {
  final int statusCode;
  final String reason;
  final Uri? url;

  const HttpException({
    required this.statusCode,
    required this.reason,
    this.url,
  });

  @override
  String toString() =>
      'HttpException($statusCode): $reason${url != null ? ' — $url' : ''}';
}

/// A more specific subclass for 404 responses.
class NotFoundException extends HttpException {
  const NotFoundException(Uri url)
      : super(statusCode: 404, reason: 'Not Found', url: url);
}

/// Simulates an HTTP fetch that may fail.
String fetchResource(String path) {
  if (path.isEmpty) {
    // ArgumentError is an Error (programmer mistake), not an Exception
    throw ArgumentError.value(path, 'path', 'Path must not be empty');
  }
  if (path == '/missing') {
    throw NotFoundException(Uri.parse('https://api.example.com$path'));
  }
  if (path == '/error') {
    throw const HttpException(statusCode: 500, reason: 'Internal Server Error');
  }
  return 'Response body for $path';
}

void main() {
  final paths = ['/home', '/missing', '/error'];

  for (final path in paths) {
    try {
      final body = fetchResource(path);
      print('Success: $body');
    } on NotFoundException catch (e) {
      // Handle 404 specifically — maybe redirect or show a fallback
      print('Resource not found: ${e.url}');
    } on HttpException catch (e) {
      // Handle all other HTTP errors
      print('HTTP error ${e.statusCode}: ${e.reason}');
    }
    // ArgumentError (programmer mistake) is intentionally not caught here —
    // let it propagate so the bug is visible during development.
  }
}
```

### Example 3: `rethrow`, Stack Traces, and Async Error Handling

```dart
import 'dart:async';

/// Simulates an async operation that may fail.
Future<String> loadConfig(String path) async {
  await Future.delayed(const Duration(milliseconds: 10)); // simulate I/O
  if (path.endsWith('.bad')) {
    throw FormatException('Invalid config format', path);
  }
  if (path.isEmpty) {
    throw ArgumentError.value(path, 'path', 'Path must not be empty');
  }
  return '{"debug": true}';
}

/// Wraps [loadConfig] with logging. Uses [rethrow] to preserve the original
/// stack trace while still recording the error.
Future<String> loadConfigWithLogging(String path) async {
  try {
    return await loadConfig(path);
  } catch (e, s) {
    // Log the error and original stack trace before re-throwing
    print('[LOG] loadConfig failed: $e');
    print('[LOG] Original stack trace:\n$s');
    rethrow; // re-throws the SAME exception with the SAME stack trace
  }
}

/// Top-level handler that decides how to respond to each error type.
Future<void> bootstrap(String configPath) async {
  try {
    final config = await loadConfigWithLogging(configPath);
    print('Config loaded: $config');
  } on FormatException catch (e) {
    print('Bad config file at "${e.source}": ${e.message}');
  } on ArgumentError {
    print('Invalid path provided — check your configuration.');
  }
  // Other errors propagate to the caller (or the top-level error zone)
}

/// Demonstrates Future.catchError as an alternative to try/catch.
Future<void> futureApiStyle() async {
  await loadConfig('config.bad')
      .then((config) => print('Loaded: $config'))
      .catchError(
        (Object e) => print('Caught via catchError: $e'),
        // The optional `test` predicate filters which errors this handler catches
        test: (e) => e is FormatException,
      );

  // StackTrace.current — capture the call stack at any point
  final trace = StackTrace.current;
  print('Current stack trace captured (first line): ${trace.toString().split('\n').first}');
}

void main() async {
  await bootstrap('app.json');   // success
  await bootstrap('app.bad');    // FormatException
  await bootstrap('');           // ArgumentError
  await futureApiStyle();        // Future.catchError demo
}
```

---

## ⚠️ Common Pitfalls

- **Catching `Error` subclasses in production** — `RangeError`, `ArgumentError`, and similar errors indicate bugs in your code. Catching them silently hides the defect. Let them crash during development so you can fix the root cause; only catch `Exception` types for expected failures.

- **Using `throw e` instead of `rethrow`** — When you want to re-throw inside a `catch` block, always use `rethrow`. Writing `throw e` creates a new throw point, which resets the stack trace and makes debugging much harder because you lose the original call site.

- **Ignoring the stack trace parameter** — `catch(e)` is convenient but drops the stack trace. In any non-trivial error handler, use `catch(e, s)` and log `s` alongside `e`. Without the stack trace, diagnosing production errors is significantly harder.

- **Empty `catch` blocks** — Swallowing exceptions silently (`catch (e) { }`) is one of the most dangerous patterns in any language. At minimum, log the error. Prefer letting unexpected exceptions propagate rather than hiding them.

- **Forgetting that `finally` can suppress exceptions** — If a `finally` block itself throws, the original exception is lost. Keep `finally` blocks simple and free of operations that can throw.

---

## ❓ Interview Questions

### Q1: What is the difference between `Error` and `Exception` in Dart?

**Answer**: In Dart, `Error` represents a programmer mistake — a condition that should never occur in correct code, such as an out-of-bounds index (`RangeError`) or an invalid argument (`ArgumentError`). `Exception` represents an expected runtime failure that correct code may still encounter, such as a network timeout or a malformed input string (`FormatException`). The convention is to catch `Exception` types and handle them gracefully, while letting `Error` types propagate so the bug is visible and can be fixed. Both are interfaces, and any non-null object can technically be thrown, but following this convention makes code intent clear.

### Q2: How does the `on` clause differ from `catch` in Dart?

**Answer**: The `on` clause filters exceptions by type — `on FormatException` only catches `FormatException` instances and its subtypes, leaving all other exceptions to propagate. The `catch` clause (without `on`) catches any thrown object regardless of type. You can combine them: `on FormatException catch (e, s)` both filters by type and binds the exception object and stack trace to variables. Using `on` clauses for specific types is preferred over a bare `catch` because it makes your intent explicit and avoids accidentally swallowing unexpected errors.

### Q3: What is `rethrow` and when should you use it?

**Answer**: `rethrow` re-throws the currently caught exception from within a `catch` block, preserving the original stack trace. You use it when you want to perform a side effect — such as logging, metrics recording, or cleanup — before letting the exception continue propagating up the call stack. The key distinction from `throw e` is that `throw e` creates a new throw point and resets the stack trace to the current location, making it harder to trace the original source of the error. Use `rethrow` any time you need to observe an exception without taking responsibility for handling it.

### Q4: How do you handle errors in async Dart code?

**Answer**: With `async/await`, you use `try/catch/finally` exactly as you would in synchronous code — `await` unwraps the `Future` and re-throws any error at the `await` expression, so the surrounding `try` block catches it. You can also use the `Future` API directly: `.catchError(handler, test: predicate)` attaches an error handler to a future chain, and `.onError<T>(handler)` is a type-safe alternative introduced in Dart 2.14. For `Stream`s, you handle errors via `stream.handleError()` or the `onError` callback in `stream.listen()`. The `async/await` style with `try/catch` is generally preferred for readability.

### Q5: What is the purpose of `finally` and when does it run?

**Answer**: The `finally` block contains code that must run regardless of whether an exception was thrown or caught — it always executes after the `try` and any `catch` blocks complete. Common uses include releasing resources (closing file handles, database connections, or network sockets), resetting state flags, or logging completion. Importantly, `finally` runs even if a `return` statement is executed inside `try` or `catch` — the return value is held, `finally` runs, and then the return completes. If `finally` itself throws, the original exception is discarded, so keep `finally` blocks simple and avoid operations that can fail.

---

## 🔑 Key Takeaways

- `Error` = programmer bug (don't catch); `Exception` = expected failure (do catch and handle)
- Use `on SpecificType catch (e, s)` to handle different exception types with different logic
- Always capture the stack trace with `catch(e, s)` in production error handlers — it's essential for debugging
- Use `rethrow` (not `throw e`) when you want to observe an exception and let it propagate; `rethrow` preserves the original stack trace
- `finally` always runs — use it for resource cleanup, not for logic that depends on whether an exception occurred
- `async/await` + `try/catch` is the idiomatic way to handle errors in async Dart; it reads like synchronous code
- Custom exceptions should implement `Exception`, carry structured data (fields), and override `toString()` for readable messages

---

## 🔗 Related Topics

- [Day 06: Collections](./Day-06-Collections.md) — understanding collection operations that can throw `RangeError` and `StateError`
- [Day 08: Classes and Constructors](../Week-2-OOP-Collections/Day-08-Classes-Constructors.md) — building the custom exception classes introduced here
- [Day 15: Async Fundamentals](../Week-3-Async-Advanced/Day-15-Async-Fundamentals.md) — deep dive into `Future`, `async/await`, and async error propagation
- [Dart Cheatsheet](../Cheatsheets/Dart-Cheatsheet.md) — quick reference for error handling syntax
