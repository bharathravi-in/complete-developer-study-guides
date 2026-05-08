# Day 25: Performance Optimization

## 🎯 What You'll Learn
- `const` constructors and compile-time constants for zero-cost widgets
- Avoiding unnecessary rebuilds with `RepaintBoundary` and widget keys
- `compute()` for offloading heavy work to isolates
- Profiling with Dart DevTools: timeline, memory, CPU profiler
- Memory leak prevention: disposing controllers, canceling subscriptions
- Lazy loading and pagination strategies
- Build method optimization: splitting widgets, caching expensive computations

## 📚 Core Concepts

Flutter's reactive framework rebuilds widgets frequently — on every `setState`, parent rebuild, or theme change. Writing performant Flutter apps requires understanding when rebuilds happen, how to minimize their cost, and how to profile and fix performance issues. This day covers the essential optimization techniques and tools.

### `const` Constructors — Zero-Cost Widgets

A `const` widget is created at compile time and cached. Flutter can skip rebuilding `const` widgets entirely because they're guaranteed to be identical across rebuilds. This is one of the most impactful optimizations:

```dart
// Without const: new Text object created on every rebuild
Text('Hello')

// With const: same object reused across rebuilds
const Text('Hello')
```

Rules for `const` constructors:
- All fields must be `final`
- All field values must be compile-time constants
- The constructor must be marked `const`

Enable the `prefer_const_constructors` and `prefer_const_literals` lint rules to catch missed opportunities.

### Avoiding Unnecessary Rebuilds

Flutter's reconciliation algorithm compares old and new widget trees and updates only what changed. However, if a parent rebuilds, all descendants rebuild by default — even if their configuration didn't change. Strategies to avoid this:

1. **Split widgets**: Extract subtrees into separate `StatelessWidget` or `StatefulWidget` classes. Only the widget that calls `setState` rebuilds.

2. **Use `const` constructors**: `const` widgets are never rebuilt.

3. **Use `RepaintBoundary`**: Isolates a subtree from parent repaints. Useful for complex widgets that don't change often (e.g., a static header).

4. **Use `ValueKey` or `ObjectKey`**: Helps Flutter match widgets across rebuilds, preserving state.

5. **Avoid anonymous functions in `build`**: `onPressed: () => doSomething()` creates a new closure on every rebuild. Extract it to a method or use a tear-off: `onPressed: doSomething`.

### `compute()` — Offloading Work to Isolates

Dart is single-threaded per isolate. Heavy computations (JSON parsing, image processing, cryptography) block the UI thread, causing jank. `compute()` runs a function in a separate isolate:

```dart
import 'package:flutter/foundation.dart';

List<int> expensiveComputation(List<int> data) {
  // Simulate heavy work
  return data.map((x) => x * x).toList();
}

Future<void> processData() async {
  final data = List.generate(1000000, (i) => i);
  // Runs in a separate isolate — UI stays responsive
  final result = await compute(expensiveComputation, data);
  print('Result: ${result.length}');
}
```

`compute()` serializes the argument and result using `SendPort`/`ReceivePort`, so they must be simple types (primitives, lists, maps) or implement `Sendable`. For more complex cases, use `Isolate.run` (Dart 2.19+).

### Profiling with Dart DevTools

Dart DevTools is a suite of performance and debugging tools:

- **Timeline (Performance)**: Shows frame rendering times, identifies jank (frames >16ms), and highlights expensive operations.
- **Memory**: Tracks heap usage, identifies memory leaks, and shows object allocation.
- **CPU Profiler**: Shows which functions consume the most CPU time.
- **Widget Inspector**: Visualizes the widget tree, shows rebuild counts, and highlights unnecessary rebuilds.

**How to use**:
1. Run your app in profile mode: `flutter run --profile`
2. Open DevTools: `flutter pub global activate devtools && devtools`
3. Record a timeline, interact with your app, and analyze the results

Look for:
- Frames >16ms (60 FPS) or >8ms (120 FPS)
- Expensive `build()` methods
- Large widget trees (>1000 widgets)
- Memory growth over time (leaks)

### Memory Leak Prevention

Common sources of memory leaks in Flutter:

1. **Not disposing controllers**: `TextEditingController`, `AnimationController`, `ScrollController`, `TabController` must be disposed in `State.dispose()`.

2. **Not canceling stream subscriptions**: `StreamSubscription` must be canceled in `dispose()`.

3. **Not removing listeners**: `ChangeNotifier.addListener()` must be paired with `removeListener()`.

4. **Holding references to `BuildContext` after disposal**: Never store `BuildContext` in a field or use it after `async` gaps without checking `mounted`.

5. **Static fields holding widgets or state**: Static fields are never garbage collected.

**Fix**: Always dispose resources in `State.dispose()`:

```dart
@override
void dispose() {
  _controller.dispose();
  _subscription.cancel();
  _notifier.removeListener(_listener);
  super.dispose();
}
```

### Lazy Loading and Pagination

Loading large datasets all at once causes memory spikes and slow initial load. Use lazy loading:

- **`ListView.builder`**: Builds items on-demand as they scroll into view.
- **`GridView.builder`**: Same for grids.
- **Pagination**: Load data in chunks (e.g., 20 items at a time) as the user scrolls.

```dart
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) {
    // Only called for visible items
    return ListTile(title: Text(items[index]));
  },
)
```

### Build Method Optimization

The `build()` method is called frequently. Keep it fast:

1. **Avoid expensive computations**: Move them to `initState`, `didChangeDependencies`, or cache the result.
2. **Split large widgets**: Extract subtrees into separate widgets so only the changed part rebuilds.
3. **Use `const` everywhere**: `const Text('Hello')`, `const SizedBox(height: 10)`.
4. **Avoid deep nesting**: Deeply nested widgets are harder to optimize and debug.

## 💻 Code Examples

### Example 1: `const` constructors for performance

```dart
import 'package:flutter/material.dart';

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      home: HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _counter = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        // const widgets are never rebuilt
        title: const Text('Performance Demo'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // This Text rebuilds on every setState
            Text('Counter: $_counter'),
            // This Text is const — never rebuilds
            const Text('This text never rebuilds'),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () => setState(() => _counter++),
              child: const Text('Increment'),
            ),
          ],
        ),
      ),
    );
  }
}
```

### Example 2: Splitting widgets to avoid unnecessary rebuilds

```dart
import 'package:flutter/material.dart';

class CounterScreen extends StatefulWidget {
  const CounterScreen({super.key});

  @override
  State<CounterScreen> createState() => _CounterScreenState();
}

class _CounterScreenState extends State<CounterScreen> {
  int _counter = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Split Widgets')),
      body: Column(
        children: [
          // Only this widget rebuilds when _counter changes
          CounterDisplay(counter: _counter),
          // This widget never rebuilds (it's const)
          const ExpensiveWidget(),
          ElevatedButton(
            onPressed: () => setState(() => _counter++),
            child: const Text('Increment'),
          ),
        ],
      ),
    );
  }
}

class CounterDisplay extends StatelessWidget {
  final int counter;
  const CounterDisplay({required this.counter, super.key});

  @override
  Widget build(BuildContext context) {
    print('CounterDisplay rebuilt'); // only prints when counter changes
    return Text('Counter: $counter');
  }
}

class ExpensiveWidget extends StatelessWidget {
  const ExpensiveWidget({super.key});

  @override
  Widget build(BuildContext context) {
    print('ExpensiveWidget rebuilt'); // never prints after initial build
    // Simulate expensive rendering
    return Container(
      height: 200,
      color: Colors.blue,
      child: const Center(child: Text('Expensive Widget')),
    );
  }
}
```

### Example 3: Using `compute()` for heavy work

```dart
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

// Top-level function (required for compute)
List<int> heavyComputation(List<int> data) {
  // Simulate expensive work
  return data.map((x) => x * x).toList();
}

class ComputeDemo extends StatefulWidget {
  const ComputeDemo({super.key});

  @override
  State<ComputeDemo> createState() => _ComputeDemoState();
}

class _ComputeDemoState extends State<ComputeDemo> {
  String _status = 'Ready';

  Future<void> _runComputation() async {
    setState(() => _status = 'Computing...');

    final data = List.generate(10000000, (i) => i);

    // Runs in a separate isolate — UI stays responsive
    final result = await compute(heavyComputation, data);

    setState(() => _status = 'Done! Result length: ${result.length}');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('compute() Demo')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(_status),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _runComputation,
              child: const Text('Run Heavy Computation'),
            ),
          ],
        ),
      ),
    );
  }
}
```

### Example 4: Disposing resources to prevent memory leaks

```dart
import 'dart:async';
import 'package:flutter/material.dart';

class ResourceManagementDemo extends StatefulWidget {
  const ResourceManagementDemo({super.key});

  @override
  State<ResourceManagementDemo> createState() => _ResourceManagementDemoState();
}

class _ResourceManagementDemoState extends State<ResourceManagementDemo> {
  late TextEditingController _controller;
  late StreamSubscription<int> _subscription;
  Timer? _timer;

  @override
  void initState() {
    super.initState();

    // Create resources
    _controller = TextEditingController();

    _subscription = Stream.periodic(const Duration(seconds: 1), (i) => i)
        .listen((count) => print('Tick: $count'));

    _timer = Timer.periodic(const Duration(seconds: 2), (timer) {
      print('Timer tick');
    });
  }

  @override
  void dispose() {
    // CRITICAL: Dispose all resources to prevent memory leaks
    _controller.dispose();
    _subscription.cancel();
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Resource Management')),
      body: TextField(controller: _controller),
    );
  }
}
```

## ⚠️ Common Pitfalls

- **Forgetting `const` on widgets**: Missing `const` causes unnecessary object creation. Enable `prefer_const_constructors` lint.
- **Creating expensive objects in `build`**: `build()` is called frequently. Move expensive computations to `initState` or cache results.
- **Not disposing controllers**: `TextEditingController`, `AnimationController`, etc. must be disposed to avoid memory leaks.
- **Using `compute()` for small tasks**: `compute()` has overhead (isolate creation, serialization). Only use it for tasks >100ms.
- **Profiling in debug mode**: Debug mode is 10x slower than release mode. Always profile in `--profile` mode.
- **Ignoring DevTools warnings**: DevTools highlights expensive builds and memory leaks — don't ignore them.

## ❓ Interview Questions

### Q1: What is the performance impact of `const` constructors in Flutter?
**Answer**: A `const` widget is created at compile time and cached. Flutter can skip rebuilding `const` widgets entirely because they're guaranteed to be identical across rebuilds — the same object is reused. This eliminates object allocation, garbage collection, and reconciliation overhead. For example, `const Text('Hello')` is never rebuilt, while `Text('Hello')` creates a new object on every parent rebuild. This is one of the most impactful optimizations in Flutter. Enable the `prefer_const_constructors` lint to catch missed opportunities.

### Q2: How does `compute()` work and when should you use it?
**Answer**: `compute()` runs a function in a separate isolate, offloading heavy work from the UI thread. It serializes the argument using `SendPort`, spawns an isolate, runs the function, and returns the result. Use it for CPU-intensive tasks that take >100ms (JSON parsing, image processing, cryptography) to keep the UI responsive. Don't use it for small tasks (<100ms) because isolate creation and serialization have overhead. For more complex cases (multiple arguments, bidirectional communication), use `Isolate.run` (Dart 2.19+) or manual `Isolate.spawn`.

### Q3: What are the most common sources of memory leaks in Flutter?
**Answer**: The most common sources are: (1) Not disposing controllers (`TextEditingController`, `AnimationController`, `ScrollController`) in `State.dispose()`. (2) Not canceling stream subscriptions (`StreamSubscription.cancel()`). (3) Not removing listeners from `ChangeNotifier` (`removeListener()`). (4) Holding references to `BuildContext` after the widget is disposed (e.g., in async callbacks without checking `mounted`). (5) Static fields holding widgets or state (static fields are never garbage collected). Always dispose resources in `State.dispose()` and use DevTools Memory tab to detect leaks.

### Q4: How do you profile a Flutter app for performance issues?
**Answer**: Run the app in profile mode (`flutter run --profile`), open Dart DevTools (`devtools`), and use the Timeline (Performance) tab. Record a timeline, interact with the app, and look for frames >16ms (60 FPS) or >8ms (120 FPS). Identify expensive `build()` methods, large widget trees, and unnecessary rebuilds. Use the CPU Profiler to find hot functions. Use the Memory tab to detect leaks (heap growth over time). Use the Widget Inspector to visualize the widget tree and see rebuild counts. Never profile in debug mode — it's 10x slower than release mode.

### Q5: What strategies can you use to avoid unnecessary widget rebuilds?
**Answer**: (1) Use `const` constructors everywhere possible — `const` widgets are never rebuilt. (2) Split large widgets into smaller `StatelessWidget` or `StatefulWidget` classes so only the changed part rebuilds. (3) Use `RepaintBoundary` to isolate subtrees from parent repaints. (4) Use `ValueKey` or `ObjectKey` to help Flutter match widgets across rebuilds. (5) Avoid creating expensive objects in `build()` — move them to `initState` or cache results. (6) Avoid anonymous functions in `build()` — they create new closures on every rebuild. (7) Use `ListView.builder` instead of `ListView` for large lists.

### Q6: What is `RepaintBoundary` and when should you use it?
**Answer**: `RepaintBoundary` creates a separate layer in the render tree, isolating a subtree from parent repaints. When a parent widget repaints (e.g., due to an animation), children inside a `RepaintBoundary` don't repaint unless they changed. Use it for complex, static widgets that don't change often (e.g., a header, a chart, a map). Don't overuse it — each `RepaintBoundary` allocates a separate layer, which has memory overhead. Use DevTools Timeline to identify expensive repaints, then add `RepaintBoundary` strategically.

## 🔑 Key Takeaways
- `const` widgets are compile-time cached and never rebuilt — use them everywhere
- Split large widgets into smaller classes to minimize rebuild scope
- Use `compute()` for CPU-intensive tasks >100ms to keep UI responsive
- Always dispose controllers, cancel subscriptions, and remove listeners in `dispose()`
- Profile in `--profile` mode with DevTools Timeline, Memory, and CPU Profiler
- Use `ListView.builder` for large lists — it builds items on-demand
- Avoid expensive computations in `build()` — move them to `initState` or cache results

## 🔗 Related Topics
- [Day 22: Flutter-Dart Patterns](./Day-22-Flutter-Dart-Patterns.md) — `const` constructors, widget lifecycle
- [Day 17: Isolates](../Week-3-Async-Advanced/Day-17-Isolates.md) — `Isolate.run`, `compute()`
- [JavaScript Memory & GC](../../JavaScript/30-Day-JS-Mastery/Week-3-Advanced/Day-19-Memory-GC.md) — cross-language comparison
- [Day 23: State Management Patterns](./Day-23-State-Management-Patterns.md) — avoiding unnecessary rebuilds
