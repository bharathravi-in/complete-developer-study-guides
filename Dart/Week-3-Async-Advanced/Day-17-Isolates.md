# Day 17: Isolates

## 🎯 What You'll Learn
- What isolates are and how they differ from threads
- The Dart concurrency model and why isolates don't share memory
- Creating isolates with `Isolate.spawn` and `Isolate.run`
- Communicating between isolates using `SendPort` and `ReceivePort`
- When to use isolates vs async/await
- Isolate lifecycle management and error handling
- Performance considerations and isolate overhead

## 📚 Core Concepts

Dart is single-threaded by default, using an event loop to handle asynchronous operations without blocking. However, CPU-intensive work (like parsing large JSON, image processing, or cryptography) can block the event loop and freeze the UI. **Isolates** are Dart's solution for true parallelism — they run code on separate threads with independent memory heaps.

### Isolates vs Threads

Unlike threads in languages like Java or C++, Dart isolates do not share memory. Each isolate has its own heap, and there is no shared state or need for locks. This eliminates entire classes of concurrency bugs (race conditions, deadlocks) but requires explicit message passing for communication. Think of isolates as separate Dart programs that communicate via messages.

### The Dart Concurrency Model

Every Dart program starts with a main isolate. When you create a new isolate, Dart spawns a new thread (or uses a thread pool) and runs a separate event loop on it. The two isolates communicate by sending messages through ports. Messages are copied (or transferred for large data like `TransferableTypedData`) between isolates, never shared.

This model is similar to Web Workers in JavaScript or actors in Erlang. It trades the complexity of shared-memory concurrency for the simplicity of message passing.

### Isolate.run (Dart 2.19+)

`Isolate.run<T>(computation)` is the simplest way to offload work to an isolate. It spawns a new isolate, runs the provided function, waits for the result, and then shuts down the isolate automatically. This is perfect for one-off CPU-intensive tasks.

```dart
final result = await Isolate.run(() {
  // Heavy computation runs on a separate isolate
  return expensiveCalculation();
});
```

The function passed to `Isolate.run` must be a top-level function or a static method — it cannot be a closure that captures variables from the surrounding scope, because those variables live in a different isolate's memory.

### Isolate.spawn

For long-lived isolates or more complex communication patterns, use `Isolate.spawn(entryPoint, message)`. This spawns a new isolate and calls the `entryPoint` function with the provided `message`. The entry point receives the message and can set up bidirectional communication using ports.

```dart
void isolateEntryPoint(SendPort sendPort) {
  // This runs in the new isolate
  sendPort.send('Hello from isolate');
}

void main() async {
  final receivePort = ReceivePort();
  await Isolate.spawn(isolateEntryPoint, receivePort.sendPort);
  print(await receivePort.first); // Hello from isolate
}
```

### SendPort and ReceivePort

`ReceivePort` is a stream of messages sent from other isolates. Calling `receivePort.sendPort` gives you a `SendPort` that can be sent to other isolates (via `Isolate.spawn` or through another message). The other isolate uses `sendPort.send(message)` to send messages back.

This is the only way isolates communicate. You cannot pass functions, closures, or objects with methods — only primitive types, lists, maps, and a few special types like `SendPort` and `TransferableTypedData`.

### When to Use Isolates

Use isolates for CPU-bound work that takes more than a few milliseconds and would block the UI:
- Parsing large JSON or XML documents
- Image processing (resizing, filtering, encoding)
- Cryptographic operations (hashing, encryption)
- Complex computations (physics simulations, data analysis)

Do NOT use isolates for I/O-bound work (network requests, file reads) — `async/await` handles those efficiently without isolate overhead. Spawning an isolate has a cost (memory, startup time), so only use them when the work justifies it.

### Isolate Lifecycle and Error Handling

Isolates created with `Isolate.spawn` run until their entry point function completes or until you explicitly kill them with `isolate.kill()`. If an isolate throws an unhandled exception, it terminates, and you can catch the error by listening to the isolate's error stream.

```dart
final isolate = await Isolate.spawn(entryPoint, message);
isolate.addErrorListener(receivePort.sendPort);
```

Always clean up isolates when done to free resources. `Isolate.run` handles this automatically, but with `Isolate.spawn` you must call `isolate.kill()` or let the entry point function return.

### Performance Considerations

Spawning an isolate takes 1–2 milliseconds and allocates several megabytes of memory for the new heap. Sending messages between isolates involves copying data, which can be expensive for large objects. For very large data (like typed arrays), use `TransferableTypedData` to transfer ownership instead of copying.

If you need to run many short tasks, consider using an isolate pool (spawn a few isolates and reuse them) rather than spawning a new isolate for each task.


## 💻 Code Examples

### Example 1: Isolate.run for simple offloading

```dart
import 'dart:isolate';

// Top-level function — required for Isolate.run
int fibonacci(int n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

void main() async {
  print('Computing fibonacci(40) on isolate...');

  final stopwatch = Stopwatch()..start();

  // Offload CPU-intensive work to a separate isolate
  final result = await Isolate.run(() => fibonacci(40));

  stopwatch.stop();
  print('Result: $result');
  print('Time: ${stopwatch.elapsedMilliseconds}ms');
  // Isolate automatically shuts down after returning result
}
// Output (times vary by hardware):
// Computing fibonacci(40) on isolate...
// Result: 102334155
// Time: ~800ms
```

### Example 2: Isolate.spawn with bidirectional communication

```dart
import 'dart:isolate';

// Entry point for the worker isolate
void workerIsolate(SendPort mainSendPort) async {
  // Create a ReceivePort to receive messages from main isolate
  final workerReceivePort = ReceivePort();

  // Send our SendPort back to main isolate
  mainSendPort.send(workerReceivePort.sendPort);

  // Listen for messages from main isolate
  await for (final message in workerReceivePort) {
    if (message == 'shutdown') {
      workerReceivePort.close();
      break;
    }

    // Process message and send result back
    final result = message * 2;
    mainSendPort.send(result);
  }
}

void main() async {
  // Create ReceivePort to receive messages from worker
  final mainReceivePort = ReceivePort();

  // Spawn worker isolate, passing our SendPort
  await Isolate.spawn(workerIsolate, mainReceivePort.sendPort);

  // Get worker's SendPort from first message
  final workerSendPort = await mainReceivePort.first as SendPort;

  // Create new ReceivePort for ongoing communication
  final responsePort = ReceivePort();
  mainReceivePort.close();

  // Send work to isolate
  workerSendPort.send(5);
  workerSendPort.send(10);
  workerSendPort.send(15);

  // Receive results (this is simplified — production code needs better coordination)
  print('Results: ${await responsePort.take(3).toList()}');

  // Shutdown worker
  workerSendPort.send('shutdown');
}
```

### Example 3: Parsing JSON in an isolate

```dart
import 'dart:convert';
import 'dart:isolate';

// Top-level function to parse JSON
List<Map<String, dynamic>> parseJsonList(String jsonString) {
  final decoded = jsonDecode(jsonString) as List;
  return decoded.cast<Map<String, dynamic>>();
}

void main() async {
  // Simulate large JSON response
  final largeJson = jsonEncode(
    List.generate(10000, (i) => {'id': i, 'name': 'Item $i'}),
  );

  print('Parsing ${largeJson.length} characters of JSON...');

  final stopwatch = Stopwatch()..start();

  // Parse on isolate to avoid blocking UI
  final result = await Isolate.run(() => parseJsonList(largeJson));

  stopwatch.stop();
  print('Parsed ${result.length} items in ${stopwatch.elapsedMilliseconds}ms');
  print('First item: ${result.first}');
}
// Output:
// Parsing 488895 characters of JSON...
// Parsed 10000 items in ~50ms
// First item: {id: 0, name: Item 0}
```

### Example 4: Error handling in isolates

```dart
import 'dart:isolate';

void faultyIsolate(SendPort sendPort) {
  // Simulate some work, then throw an error
  Future.delayed(const Duration(milliseconds: 100), () {
    throw StateError('Something went wrong in isolate');
  });
}

void main() async {
  final receivePort = ReceivePort();
  final errorPort = ReceivePort();

  // Spawn isolate with error listener
  final isolate = await Isolate.spawn(
    faultyIsolate,
    receivePort.sendPort,
    onError: errorPort.sendPort,
  );

  // Listen for errors
  errorPort.listen((errorData) {
    print('Isolate error: ${errorData[0]}');
    print('Stack trace: ${errorData[1]}');
    isolate.kill();
    receivePort.close();
    errorPort.close();
  });

  // Wait a bit to let error occur
  await Future.delayed(const Duration(milliseconds: 200));
}
// Output:
// Isolate error: Bad state: Something went wrong in isolate
// Stack trace: [stack trace details]
```

### Example 5: Isolate pool for multiple tasks

```dart
import 'dart:isolate';
import 'dart:async';

class IsolatePool {
  final int size;
  final List<SendPort> _workers = [];
  final List<ReceivePort> _ports = [];

  IsolatePool(this.size);

  Future<void> init() async {
    for (int i = 0; i < size; i++) {
      final receivePort = ReceivePort();
      await Isolate.spawn(_workerEntryPoint, receivePort.sendPort);
      final sendPort = await receivePort.first as SendPort;
      _workers.add(sendPort);
      _ports.add(receivePort);
    }
  }

  static void _workerEntryPoint(SendPort mainSendPort) {
    final workerPort = ReceivePort();
    mainSendPort.send(workerPort.sendPort);

    workerPort.listen((message) {
      final data = message as List;
      final replyPort = data[0] as SendPort;
      final task = data[1] as int;

      // Simulate work
      final result = task * task;
      replyPort.send(result);
    });
  }

  Future<int> compute(int value) async {
    // Round-robin worker selection
    final workerIndex = value % size;
    final worker = _workers[workerIndex];

    final responsePort = ReceivePort();
    worker.send([responsePort.sendPort, value]);

    return await responsePort.first as int;
  }

  void dispose() {
    for (final port in _ports) {
      port.close();
    }
  }
}

void main() async {
  final pool = IsolatePool(3);
  await pool.init();

  print('Computing squares using isolate pool...');

  final results = await Future.wait([
    pool.compute(5),
    pool.compute(10),
    pool.compute(15),
    pool.compute(20),
  ]);

  print('Results: $results');
  pool.dispose();
}
// Output:
// Computing squares using isolate pool...
// Results: [25, 100, 225, 400]
```

## ⚠️ Common Pitfalls

- **Passing closures to Isolate.spawn**: The entry point must be a top-level function or static method. Closures capture variables from the surrounding scope, which don't exist in the new isolate's memory. Use message passing to send data instead.
- **Overusing isolates for I/O**: Isolates are for CPU-bound work. Network requests and file I/O are already non-blocking with `async/await` — using isolates adds overhead without benefit.
- **Forgetting to kill long-lived isolates**: Isolates created with `Isolate.spawn` run until explicitly killed or until their entry point returns. Always call `isolate.kill()` when done to free resources.
- **Sending non-copyable objects**: You can only send primitive types, collections, and special types like `SendPort`. Attempting to send functions, closures, or objects with methods throws a runtime error.
- **Ignoring isolate startup cost**: Spawning an isolate takes 1–2ms and allocates several MB. For tasks under 10ms, the overhead exceeds the benefit. Profile before optimizing with isolates.
- **Not handling isolate errors**: Unhandled exceptions in isolates terminate the isolate silently unless you attach an error listener with `onError` or `addErrorListener`.

## ❓ Interview Questions

### Q1: What is the difference between isolates and threads?
**Answer**: Isolates are Dart's concurrency primitive, similar to threads but with a critical difference: isolates do not share memory. Each isolate has its own heap and cannot access variables from other isolates. This eliminates race conditions and deadlocks but requires explicit message passing for communication. Threads in languages like Java or C++ share memory and require locks for synchronization. Dart's model trades the complexity of shared-memory concurrency for the simplicity and safety of isolated memory spaces.

### Q2: When should you use isolates instead of async/await?
**Answer**: Use isolates for CPU-bound work that takes more than a few milliseconds and would block the event loop, such as parsing large JSON, image processing, or complex computations. Use `async/await` for I/O-bound work like network requests or file reads, which are already non-blocking and don't benefit from isolates. The rule of thumb: if the work is waiting for external resources, use `async/await`; if the work is computing intensively, use isolates.

### Q3: How do isolates communicate with each other?
**Answer**: Isolates communicate by sending messages through `SendPort` and `ReceivePort`. A `ReceivePort` is a stream that receives messages from other isolates. Its `sendPort` property gives you a `SendPort` that can be sent to other isolates (via `Isolate.spawn` or through another message). The other isolate uses `sendPort.send(message)` to send messages back. Messages are copied between isolates — you can only send primitive types, collections, and special types like `SendPort` and `TransferableTypedData`.

### Q4: What is the difference between Isolate.run and Isolate.spawn?
**Answer**: `Isolate.run` (Dart 2.19+) is a convenience method for one-off tasks: it spawns an isolate, runs a function, waits for the result, and automatically shuts down the isolate. It's perfect for simple CPU-intensive work. `Isolate.spawn` creates a long-lived isolate that runs until explicitly killed or until its entry point returns. It requires manual setup of bidirectional communication with ports and is used for complex scenarios like worker pools or ongoing background processing.

### Q5: Why can't you pass closures to Isolate.spawn?
**Answer**: Closures capture variables from their surrounding scope, which live in the parent isolate's memory. Since isolates don't share memory, those captured variables don't exist in the new isolate. The entry point for `Isolate.spawn` must be a top-level function or static method that doesn't depend on any external state. To pass data to the isolate, send it as the message parameter to `Isolate.spawn`, which copies the data to the new isolate's memory.

### Q6: How do you handle errors in isolates?
**Answer**: For `Isolate.run`, errors propagate as exceptions to the caller — wrap the call in `try/catch`. For `Isolate.spawn`, unhandled exceptions terminate the isolate silently unless you attach an error listener. Pass a `SendPort` to the `onError` parameter of `Isolate.spawn`, or call `isolate.addErrorListener(sendPort)` after spawning. The error listener receives a list with two elements: the error object and the stack trace string. Always attach error listeners to long-lived isolates to detect and handle failures.

### Q7: What are the performance costs of using isolates?
**Answer**: Spawning an isolate takes 1–2 milliseconds and allocates several megabytes of memory for the new heap. Sending messages between isolates involves copying data, which can be expensive for large objects (though `TransferableTypedData` can transfer ownership without copying). For tasks under 10ms, the isolate overhead often exceeds the benefit. Profile your code to ensure the CPU-intensive work justifies the cost. For many short tasks, consider using an isolate pool to amortize the startup cost.

### Q8: Can you share objects between isolates?
**Answer**: No, isolates cannot share objects or memory. All communication happens through message passing, and messages are copied between isolates. You can only send primitive types (int, double, String, bool), collections (List, Map, Set), and special types like `SendPort`, `Capability`, and `TransferableTypedData`. Attempting to send functions, closures, or objects with methods throws a runtime error. For large data, use `TransferableTypedData` to transfer ownership of typed arrays without copying.



## 🔑 Key Takeaways
- Isolates provide true parallelism in Dart by running code on separate threads with independent memory
- Unlike threads, isolates do not share memory — all communication happens through message passing
- Use `Isolate.run` for simple one-off CPU-intensive tasks; use `Isolate.spawn` for long-lived workers
- Only use isolates for CPU-bound work (parsing, computation, image processing) — not for I/O
- Communication uses `SendPort` and `ReceivePort`; only primitive types and collections can be sent
- Isolate startup has overhead (1–2ms, several MB) — profile before optimizing
- Always attach error listeners to `Isolate.spawn` isolates and kill them when done

## 🔗 Related Topics
- [Day 15: Async Fundamentals](./Day-15-Async-Fundamentals.md) — when async/await is sufficient
- [Day 16: Streams](./Day-16-Streams.md) — streams work across isolates via message passing
- [Day 25: Performance Optimization](../Week-4-Flutter-Dart-Interview/Day-25-Performance-Optimization.md) — `compute()` in Flutter
- [JavaScript Web Workers](../../JavaScript/30-Day-JS-Mastery/Week-3-Advanced/Day-19-Memory-GC.md) — similar message-passing model
- [DS Complexity Analysis](../../DS/Days/Day_01_Complexity_Analysis.md) — when to parallelize algorithms
