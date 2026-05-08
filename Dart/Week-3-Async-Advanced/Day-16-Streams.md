# Day 16: Streams

## 🎯 What You'll Learn
- What a `Stream` is and how it differs from `Future`
- Creating streams with `StreamController` and `async*` generators
- Listening to streams with `StreamSubscription` and `await for`
- Single-subscription vs broadcast streams
- Transforming streams with `map`, `where`, `expand`, and `StreamTransformer`
- Error handling in streams and the `onError` callback
- Closing streams and managing subscriptions to prevent memory leaks

## 📚 Core Concepts

A `Stream<T>` is a sequence of asynchronous events delivered over time. While a `Future` represents a single value that arrives later, a `Stream` represents zero or more values that arrive at different times. Streams are the foundation of reactive programming in Dart and are used extensively in Flutter for handling user input, network responses, and state changes.

### Stream vs Future

A `Future` completes once with either a value or an error, then it's done. A `Stream` can emit multiple values over time, then optionally complete or error. Think of a `Future` as a single HTTP request and a `Stream` as a WebSocket connection that pushes data continuously.

```dart
Future<int> fetchOnce() async => 42;        // one value
Stream<int> countStream() async* {          // many values
  for (int i = 0; i < 5; i++) {
    yield i;
  }
}
```

### StreamController

`StreamController<T>` is the most common way to create a stream programmatically. It has a `sink` for adding events and a `stream` for listening to them. You add events with `sink.add(value)`, errors with `sink.addError(error)`, and signal completion with `sink.close()`.

```dart
final controller = StreamController<String>();
controller.stream.listen((data) => print(data));
controller.sink.add('Hello');
controller.sink.add('World');
controller.sink.close();
```

By default, `StreamController` creates a single-subscription stream — only one listener is allowed. If you need multiple listeners, create a broadcast stream with `StreamController.broadcast()`.

### Single-Subscription vs Broadcast Streams

A **single-subscription stream** allows only one listener and starts producing events when the listener subscribes. This is appropriate for reading a file or making an HTTP request — operations that should happen once.

A **broadcast stream** allows multiple listeners and produces events regardless of whether anyone is listening. This is appropriate for UI events like button clicks or global state changes that many widgets might observe.

```dart
// Single-subscription — only one listener allowed
final single = StreamController<int>();
single.stream.listen((x) => print('A: $x'));
// single.stream.listen((x) => print('B: $x')); // ERROR: already listened

// Broadcast — multiple listeners allowed
final broadcast = StreamController<int>.broadcast();
broadcast.stream.listen((x) => print('A: $x'));
broadcast.stream.listen((x) => print('B: $x')); // OK
```

### async* and yield

The `async*` keyword marks a function as an asynchronous generator that returns a `Stream`. Inside an `async*` function, `yield` emits a value to the stream, and `yield*` emits all values from another stream. This is the most readable way to create streams with complex logic.

```dart
Stream<int> fibonacci(int n) async* {
  int a = 0, b = 1;
  for (int i = 0; i < n; i++) {
    yield a;
    final next = a + b;
    a = b;
    b = next;
  }
}
```

### Listening to Streams

You can listen to a stream in two ways:

1. **`stream.listen()`** — callback-based, returns a `StreamSubscription` that you can pause, resume, or cancel.
2. **`await for`** — loop-based, blocks until the stream completes or errors. Only works inside `async` functions.

```dart
// Callback style
final subscription = stream.listen(
  (data) => print(data),
  onError: (e) => print('Error: $e'),
  onDone: () => print('Done'),
);

// Loop style
await for (final value in stream) {
  print(value);
}
```

### Stream Transformations

Streams support functional transformations like `map`, `where`, `expand`, `take`, `skip`, and more. These return new streams, enabling chaining. For complex transformations, use `StreamTransformer<S, T>`, which converts a `Stream<S>` into a `Stream<T>`.

```dart
final numbers = Stream.fromIterable([1, 2, 3, 4, 5]);
final doubled = numbers.map((x) => x * 2);
final evens = doubled.where((x) => x % 2 == 0);
```

### Error Handling

Errors in streams propagate to listeners. You can catch them with the `onError` callback in `listen()` or with `try/catch` around `await for`. If an error is not handled, it becomes an unhandled async error. Unlike futures, a stream can emit multiple errors over its lifetime.

### Closing Streams and Memory Leaks

Always close `StreamController` instances when done to free resources. Always cancel `StreamSubscription` instances when you no longer need events — in Flutter, this typically happens in `dispose()`. Failing to cancel subscriptions causes memory leaks because the listener keeps a reference to your widget or object.


## 💻 Code Examples

### Example 1: StreamController basics

```dart
import 'dart:async';

void main() async {
  // Create a single-subscription stream controller
  final controller = StreamController<int>();

  // Listen to the stream before adding events
  controller.stream.listen(
    (data) => print('Received: $data'),
    onError: (e) => print('Error: $e'),
    onDone: () => print('Stream closed'),
  );

  // Add events to the stream
  controller.sink.add(1);
  controller.sink.add(2);
  controller.sink.add(3);

  // Add an error
  controller.sink.addError('Something went wrong');

  // Close the stream — triggers onDone callback
  await controller.close();
}
// Output:
// Received: 1
// Received: 2
// Received: 3
// Error: Something went wrong
// Stream closed
```

### Example 2: async* generator and await for

```dart
import 'dart:async';

// async* function returns a Stream<int>
Stream<int> countDown(int from) async* {
  for (int i = from; i >= 0; i--) {
    await Future.delayed(const Duration(milliseconds: 100));
    yield i; // emit value to the stream
  }
}

void main() async {
  print('Countdown starting...');

  // await for consumes the stream until it completes
  await for (final count in countDown(5)) {
    print(count);
  }

  print('Liftoff!');
}
// Output (with 100ms delays):
// Countdown starting...
// 5
// 4
// 3
// 2
// 1
// 0
// Liftoff!
```

### Example 3: Broadcast stream with multiple listeners

```dart
import 'dart:async';

void main() async {
  // Broadcast stream allows multiple listeners
  final controller = StreamController<String>.broadcast();

  // First listener
  controller.stream.listen((msg) => print('Listener A: $msg'));

  // Second listener
  controller.stream.listen((msg) => print('Listener B: $msg'));

  // Both listeners receive all events
  controller.sink.add('Hello');
  controller.sink.add('World');

  await Future.delayed(const Duration(milliseconds: 10));
  await controller.close();
}
// Output:
// Listener A: Hello
// Listener B: Hello
// Listener A: World
// Listener B: World
```

### Example 4: Stream transformations and chaining

```dart
import 'dart:async';

void main() async {
  // Create a stream of numbers 1 through 10
  final numbers = Stream<int>.periodic(
    const Duration(milliseconds: 50),
    (count) => count + 1,
  ).take(10);

  // Chain transformations: filter evens, square them, convert to strings
  final transformed = numbers
      .where((n) => n % 2 == 0)           // keep only even numbers
      .map((n) => n * n)                  // square each number
      .map((n) => 'Square: $n');          // format as string

  // Consume the transformed stream
  await for (final result in transformed) {
    print(result);
  }
}
// Output:
// Square: 4
// Square: 16
// Square: 36
// Square: 64
// Square: 100
```

### Example 5: StreamTransformer for custom transformations

```dart
import 'dart:async';

// Custom transformer that batches events into lists of size n
class BatchTransformer<T> extends StreamTransformerBase<T, List<T>> {
  final int batchSize;

  BatchTransformer(this.batchSize);

  @override
  Stream<List<T>> bind(Stream<T> stream) async* {
    final batch = <T>[];
    await for (final item in stream) {
      batch.add(item);
      if (batch.length == batchSize) {
        yield List.from(batch); // emit a copy of the batch
        batch.clear();
      }
    }
    // Emit remaining items if any
    if (batch.isNotEmpty) {
      yield batch;
    }
  }
}

void main() async {
  final numbers = Stream.fromIterable([1, 2, 3, 4, 5, 6, 7, 8, 9]);

  // Transform stream into batches of 3
  final batched = numbers.transform(BatchTransformer<int>(3));

  await for (final batch in batched) {
    print(batch);
  }
}
// Output:
// [1, 2, 3]
// [4, 5, 6]
// [7, 8, 9]
```

## ⚠️ Common Pitfalls

- **Forgetting to cancel subscriptions**: In Flutter, always cancel `StreamSubscription` in `dispose()` to prevent memory leaks. A subscription keeps a reference to your listener callback, which may reference your widget.
- **Listening to a single-subscription stream twice**: Attempting to call `.listen()` twice on a single-subscription stream throws a `StateError`. Use `asBroadcastStream()` to convert it if you need multiple listeners.
- **Not closing StreamController**: An unclosed `StreamController` leaks memory. Always call `controller.close()` when done, typically in a `dispose()` method or `finally` block.
- **Ignoring errors**: Streams can emit errors at any time. If you don't provide an `onError` callback or wrap `await for` in `try/catch`, unhandled errors crash your app.
- **Using await for in UI code**: `await for` blocks until the stream completes. In Flutter, use `StreamBuilder` instead to reactively rebuild widgets as events arrive without blocking.
- **Modifying a stream while iterating**: Adding events to a `StreamController` from within its own listener can cause infinite loops or unexpected behavior. Use a separate controller or queue events for later.

## ❓ Interview Questions

### Q1: What is the difference between a Stream and a Future in Dart?
**Answer**: A `Future` represents a single asynchronous value that will be available at some point — it completes once with either a value or an error. A `Stream` represents a sequence of asynchronous events over time — it can emit zero, one, or many values, and can also emit multiple errors before eventually completing. Futures are for one-shot async operations like HTTP requests, while streams are for continuous data sources like WebSocket connections, user input events, or sensor readings.

### Q2: When would you use a broadcast stream instead of a single-subscription stream?
**Answer**: Use a broadcast stream when multiple independent listeners need to observe the same events, such as UI events (button clicks, text changes) or global state changes (authentication status, theme changes). Broadcast streams produce events regardless of whether anyone is listening, and all active listeners receive every event. Use a single-subscription stream for operations that should only happen once, like reading a file or making an HTTP request, where having multiple listeners would cause the operation to run multiple times.

### Q3: How do you prevent memory leaks when using streams in Flutter?
**Answer**: Always cancel `StreamSubscription` instances when they are no longer needed, typically in the `dispose()` method of a `StatefulWidget`. A subscription holds a reference to its listener callback, which often captures the widget instance, preventing garbage collection. Also close `StreamController` instances when done to release resources. In Flutter, prefer using `StreamBuilder` widget, which automatically manages subscriptions and cancellations for you.

### Q4: Explain the difference between `yield` and `yield*` in an async* function.
**Answer**: In an `async*` generator function, `yield` emits a single value to the stream, while `yield*` emits all values from another stream. `yield` is for producing individual events, whereas `yield*` is for delegating to or flattening another stream. For example, `yield 1` adds one event, but `yield* Stream.fromIterable([1, 2, 3])` adds three events. This is analogous to the spread operator in collections.

### Q5: How does error handling work in streams?
**Answer**: Errors in streams propagate to listeners through the `onError` callback in `stream.listen()` or can be caught with `try/catch` around `await for`. Unlike futures, a stream can emit multiple errors over its lifetime without completing. If an error is not handled, it becomes an unhandled async error. You can also use `.handleError()` to catch and transform errors in a stream pipeline, or `.transform()` with a custom transformer that catches errors and emits fallback values.

### Q6: What is the purpose of StreamTransformer and when would you use it?
**Answer**: `StreamTransformer<S, T>` converts a `Stream<S>` into a `Stream<T>`, enabling complex transformations that go beyond simple `map` or `where` operations. Use it when you need stateful transformations (like batching, debouncing, or throttling), when you need to combine multiple events into one, or when you need to inject additional events based on timing or external state. For example, a debounce transformer waits for a pause in events before emitting the last value, which is useful for search-as-you-type features.

### Q7: How do you convert a single-subscription stream to a broadcast stream?
**Answer**: Call `.asBroadcastStream()` on the single-subscription stream. This creates a new broadcast stream that listens to the original stream and forwards all events to multiple listeners. However, be aware that the original stream starts producing events as soon as the first listener subscribes to the broadcast stream, and those events are buffered until listeners are added. For better control, create a `StreamController.broadcast()` and manually forward events from the original stream.

### Q8: What happens if you add events to a StreamController after calling close()?
**Answer**: Adding events to a closed `StreamController` throws a `StateError` with the message "Cannot add event after closing". Once `close()` is called, the controller transitions to a closed state and no longer accepts new events or errors. Always check `controller.isClosed` before adding events if there's any chance the controller might have been closed, or structure your code to ensure `close()` is the last operation.



## 🔑 Key Takeaways
- `Stream<T>` represents a sequence of asynchronous events over time, unlike `Future` which is a single value
- `StreamController` creates streams programmatically; use `.broadcast()` for multiple listeners
- `async*` functions with `yield` provide a readable way to generate streams
- Always cancel `StreamSubscription` and close `StreamController` to prevent memory leaks
- Use `await for` to consume streams in async functions, or `.listen()` for callback-based handling
- Streams support functional transformations (`map`, `where`, `expand`) and custom `StreamTransformer` for complex logic
- Errors in streams can occur multiple times; always provide `onError` handlers

## 🔗 Related Topics
- [Day 15: Async Fundamentals](./Day-15-Async-Fundamentals.md) — `Future` and `async/await` foundation
- [Day 17: Isolates](./Day-17-Isolates.md) — true parallelism for CPU-intensive work
- [Day 23: State Management Patterns](../Week-4-Flutter-Dart-Interview/Day-23-State-Management-Patterns.md) — `StreamBuilder` in Flutter
- [JavaScript Event Loop](../../JavaScript/30-Day-JS-Mastery/Week-2-Intermediate/Day-11-Event-Loop.md) — compare with JS event-driven patterns
- [DS Algorithms](../../DS/Days/Day_01_Complexity_Analysis.md) — stream processing complexity
