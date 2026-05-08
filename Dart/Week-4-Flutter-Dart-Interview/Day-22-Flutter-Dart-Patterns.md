# Day 22: Flutter-Dart Patterns

## 🎯 What You'll Learn
- The Flutter widget tree and how Dart classes map to widgets
- `StatelessWidget` vs `StatefulWidget` lifecycle
- `BuildContext` — what it is and why it matters
- `InheritedWidget` internals and how it powers `Provider`
- `Key` types: `ValueKey`, `ObjectKey`, `GlobalKey`, `UniqueKey`
- `const` constructors in Flutter and their performance impact
- Widget identity, reconciliation, and the element tree

## 📚 Core Concepts

Flutter's UI is built entirely in Dart. Understanding how Dart's type system, object model, and memory management interact with Flutter's rendering pipeline is essential for writing performant Flutter apps.

### The Widget Tree

In Flutter, everything is a widget — a Dart class that describes a piece of UI. Widgets are **immutable** descriptions; Flutter's framework creates, updates, and destroys the underlying `Element` and `RenderObject` trees. The widget tree is rebuilt frequently (on every `setState` call), but Flutter's reconciliation algorithm makes this efficient by reusing elements when possible.

```
Widget Tree (Dart objects, immutable)
    ↓ creates/updates
Element Tree (mutable, long-lived, holds state)
    ↓ creates/updates
RenderObject Tree (layout, painting)
```

### `StatelessWidget` vs `StatefulWidget`

`StatelessWidget` has no mutable state — its `build` method is a pure function of its constructor arguments. Use it for UI that doesn't change after construction.

`StatefulWidget` separates the widget (immutable configuration) from its `State` (mutable). The `State` object persists across widget rebuilds as long as the widget's position in the tree doesn't change. Key lifecycle methods:
- `initState()` — called once when the State is inserted into the tree
- `didUpdateWidget(oldWidget)` — called when the parent rebuilds with a new widget configuration
- `dispose()` — called when the State is removed from the tree; cancel subscriptions here
- `setState(() {...})` — marks the widget as dirty, triggering a rebuild

### `BuildContext`

`BuildContext` is a handle to a widget's location in the element tree. It's used to:
- Look up inherited widgets: `Theme.of(context)`, `MediaQuery.of(context)`
- Navigate: `Navigator.of(context).push(...)`
- Show dialogs: `showDialog(context: context, ...)`

**Critical rule**: Never use a `BuildContext` after the widget has been disposed. In async callbacks, check `mounted` before using `context`:

```dart
Future<void> loadData() async {
  final data = await fetchData();
  if (!mounted) return; // widget may have been disposed
  setState(() => _data = data);
}
```

### `InheritedWidget` Internals

`InheritedWidget` is the low-level mechanism for propagating data down the widget tree without passing it through every constructor. When you call `MyInherited.of(context)`, Flutter walks up the element tree to find the nearest `MyInherited` ancestor and registers the current widget as a dependent. When the `InheritedWidget` rebuilds with `updateShouldNotify` returning `true`, all registered dependents are rebuilt.

`Provider`, `Riverpod`, and `InheritedNotifier` are all built on top of `InheritedWidget`.

```dart
class ThemeData extends InheritedWidget {
  final Color primaryColor;

  const ThemeData({
    required this.primaryColor,
    required super.child,
    super.key,
  });

  static ThemeData of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<ThemeData>()!;
  }

  @override
  bool updateShouldNotify(ThemeData oldWidget) {
    return primaryColor != oldWidget.primaryColor; // only rebuild if color changed
  }
}
```

### `Key` Types

Keys help Flutter identify widgets across rebuilds. Without keys, Flutter uses position in the tree to match old and new widgets. With keys, Flutter uses the key value.

- **`ValueKey<T>(value)`** — identity based on a value (e.g., `ValueKey(user.id)`)
- **`ObjectKey(object)`** — identity based on object identity (`identical`)
- **`UniqueKey()`** — always unique; forces recreation on every rebuild
- **`GlobalKey`** — unique across the entire app; allows accessing `State` from outside the widget tree (use sparingly — it's expensive)

Use keys when reordering lists, animating between positions, or preserving state when a widget moves in the tree.

### `const` Constructors

A `const` widget is created at compile time and cached. Flutter can skip rebuilding `const` widgets entirely because they're guaranteed to be identical across rebuilds. This is one of the most impactful performance optimizations in Flutter.

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

## 💻 Code Examples

### Example 1: StatefulWidget lifecycle

```dart
import 'package:flutter/material.dart';

class CounterWidget extends StatefulWidget {
  final String label;
  const CounterWidget({required this.label, super.key});

  @override
  State<CounterWidget> createState() => _CounterWidgetState();
}

class _CounterWidgetState extends State<CounterWidget> {
  int _count = 0;

  @override
  void initState() {
    super.initState();
    // Called once when inserted into tree
    print('initState: ${widget.label}');
  }

  @override
  void didUpdateWidget(CounterWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    // Called when parent rebuilds with new widget config
    if (oldWidget.label != widget.label) {
      print('Label changed: ${oldWidget.label} → ${widget.label}');
    }
  }

  @override
  void dispose() {
    // Cancel subscriptions, timers, controllers here
    print('dispose: ${widget.label}');
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('${widget.label}: $_count'),
        ElevatedButton(
          onPressed: () => setState(() => _count++), // triggers rebuild
          child: const Text('Increment'),
        ),
      ],
    );
  }
}
```

### Example 2: InheritedWidget implementation

```dart
import 'package:flutter/material.dart';

// Custom InheritedWidget for app-wide user data
class UserProvider extends InheritedWidget {
  final String username;
  final int userId;

  const UserProvider({
    required this.username,
    required this.userId,
    required super.child,
    super.key,
  });

  // Convenience accessor — registers context as dependent
  static UserProvider of(BuildContext context) {
    final provider = context.dependOnInheritedWidgetOfExactType<UserProvider>();
    assert(provider != null, 'No UserProvider found in context');
    return provider!;
  }

  @override
  bool updateShouldNotify(UserProvider oldWidget) {
    // Only rebuild dependents if data actually changed
    return username != oldWidget.username || userId != oldWidget.userId;
  }
}

// Consumer widget — rebuilds when UserProvider changes
class UserGreeting extends StatelessWidget {
  const UserGreeting({super.key});

  @override
  Widget build(BuildContext context) {
    final user = UserProvider.of(context); // registers as dependent
    return Text('Hello, ${user.username}!');
  }
}
```

### Example 3: Keys for list reordering

```dart
import 'package:flutter/material.dart';

class TodoItem extends StatefulWidget {
  final String text;
  // ValueKey ensures Flutter matches this widget by text, not position
  const TodoItem({required this.text, super.key});

  @override
  State<TodoItem> createState() => _TodoItemState();
}

class _TodoItemState extends State<TodoItem> {
  bool _checked = false;

  @override
  Widget build(BuildContext context) {
    return CheckboxListTile(
      title: Text(widget.text),
      value: _checked,
      onChanged: (v) => setState(() => _checked = v ?? false),
    );
  }
}

class TodoList extends StatefulWidget {
  const TodoList({super.key});

  @override
  State<TodoList> createState() => _TodoListState();
}

class _TodoListState extends State<TodoList> {
  var _items = ['Buy milk', 'Write code', 'Exercise'];

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ..._items.map(
          // ValueKey preserves checkbox state when list is reordered
          (item) => TodoItem(key: ValueKey(item), text: item),
        ),
        ElevatedButton(
          onPressed: () => setState(() => _items = _items.reversed.toList()),
          child: const Text('Reverse'),
        ),
      ],
    );
  }
}
```

### Example 4: const constructors and performance

```dart
import 'package:flutter/material.dart';

// All fields final + const constructor = compile-time constant widget
class StatusBadge extends StatelessWidget {
  final String label;
  final Color color;

  const StatusBadge({required this.label, required this.color, super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color,
        borderRadius: const BorderRadius.all(Radius.circular(12)),
      ),
      child: Text(
        label,
        style: const TextStyle(color: Colors.white, fontSize: 12),
      ),
    );
  }
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return const MaterialApp(
      // const here means the entire subtree is cached
      home: Scaffold(
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // These const widgets are never rebuilt
              StatusBadge(label: 'Active', color: Colors.green),
              StatusBadge(label: 'Pending', color: Colors.orange),
            ],
          ),
        ),
      ),
    );
  }
}
```

## ⚠️ Common Pitfalls

- **Using `BuildContext` after `async` gap without checking `mounted`**: After any `await`, the widget may have been disposed. Always check `if (!mounted) return` before using `context` in async methods.
- **Overusing `GlobalKey`**: `GlobalKey` is expensive — it requires a global lookup table. Use it only when you genuinely need to access `State` from outside the widget tree (e.g., form validation). Prefer `ValueKey` for list items.
- **Missing `const` on widgets**: Forgetting `const` on widgets that could be constant causes unnecessary rebuilds. Enable the `prefer_const_constructors` lint rule.
- **Calling `setState` in `initState`**: Calling `setState` before the first build completes throws an error. Use `WidgetsBinding.instance.addPostFrameCallback` if you need to update state after the first frame.
- **`InheritedWidget` and `updateShouldNotify`**: Returning `true` always from `updateShouldNotify` causes all dependents to rebuild on every change, even if the relevant data didn't change. Implement proper equality checks.

## ❓ Interview Questions

### Q1: What is the difference between the widget tree, element tree, and render tree in Flutter?
**Answer**: The widget tree is a tree of immutable Dart objects that describe the UI — it's rebuilt frequently. The element tree is a mutable, long-lived tree that Flutter maintains to track the correspondence between widgets and their state. Elements are created once and updated when the widget tree changes. The render tree contains `RenderObject` instances that handle layout and painting. Flutter's reconciliation algorithm compares old and new widget trees, updates elements in place when possible (preserving state), and only creates new render objects when necessary.

### Q2: What is `BuildContext` and why is it dangerous to use after an async gap?
**Answer**: `BuildContext` is a handle to a widget's location in the element tree. It's used to look up inherited widgets, navigate, and show dialogs. After an `async` gap (any `await`), the widget may have been removed from the tree (disposed), making the `BuildContext` invalid. Using an invalid context can cause crashes or incorrect behavior. The fix is to check `if (!mounted) return` before using `context` after any `await`. In Flutter 3.7+, the `use_build_context_synchronously` lint rule catches this automatically.

### Q3: How does `InheritedWidget` work internally?
**Answer**: When a widget calls `context.dependOnInheritedWidgetOfExactType<T>()`, Flutter walks up the element tree to find the nearest ancestor of type `T` and registers the current element as a dependent. When the `InheritedWidget` rebuilds, it calls `updateShouldNotify` — if it returns `true`, Flutter marks all registered dependents as dirty and rebuilds them. This is how `Theme.of(context)`, `MediaQuery.of(context)`, and `Provider.of(context)` work. The key insight is that only widgets that called `dependOnInheritedWidgetOfExactType` are rebuilt — not the entire subtree.

### Q4: When should you use `GlobalKey` vs `ValueKey`?
**Answer**: Use `ValueKey` (or `ObjectKey`) when you need to preserve widget state across list reordering or when Flutter needs to match widgets by identity rather than position. Use `GlobalKey` only when you need to access a widget's `State` or `RenderObject` from outside the widget tree — for example, calling `formKey.currentState!.validate()` on a `Form`. `GlobalKey` is expensive because it maintains a global registry and prevents the widget from being moved between subtrees efficiently. Prefer `ValueKey` for list items and `GlobalKey` only for form validation and similar use cases.

### Q5: What makes a constructor `const` in Flutter and why does it matter?
**Answer**: A `const` constructor requires all fields to be `final` and all field values to be compile-time constants. When you use `const` when constructing a widget, Dart creates the object at compile time and caches it — the same instance is reused across rebuilds. Flutter can skip rebuilding `const` widgets entirely because they're guaranteed to be identical. This is one of the most impactful performance optimizations: a `const Text('Hello')` is never rebuilt, while `Text('Hello')` creates a new object on every parent rebuild. Enable the `prefer_const_constructors` lint to catch missed opportunities.

### Q6: Explain the `StatefulWidget` lifecycle in detail.
**Answer**: When a `StatefulWidget` is first inserted into the tree, Flutter calls `createState()` to create the `State` object, then `initState()` for one-time initialization (subscribe to streams, initialize controllers). On every rebuild, `build()` is called to produce the widget tree. When the parent rebuilds with a new widget configuration, `didUpdateWidget(oldWidget)` is called — use this to react to configuration changes. When the widget is removed from the tree, `dispose()` is called — cancel subscriptions, dispose controllers, and release resources here. `setState(() {...})` marks the widget dirty and schedules a rebuild.

## 🔑 Key Takeaways
- Flutter has three trees: widget (immutable), element (mutable, holds state), render (layout/paint)
- `BuildContext` is a tree location handle — never use it after `async` without checking `mounted`
- `InheritedWidget` propagates data down the tree; only registered dependents rebuild
- `ValueKey` preserves state across reordering; `GlobalKey` enables cross-tree state access
- `const` widgets are compile-time cached and never rebuilt — use them everywhere possible
- `StatefulWidget` lifecycle: `initState` → `build` → `didUpdateWidget` → `dispose`

## 🔗 Related Topics
- [Day 23: State Management Patterns](./Day-23-State-Management-Patterns.md) — `ChangeNotifier`, `StreamBuilder`
- [Day 25: Performance Optimization](./Day-25-Performance-Optimization.md) — avoiding unnecessary rebuilds
- [Day 08: Classes & Constructors](../Week-2-OOP-Collections/Day-08-Classes-Constructors.md) — `const` constructors
- [API Design REST Principles](../../API-Design/Week-1-REST-Fundamentals/Day-01-REST-Principles.md) — stateless design parallels
