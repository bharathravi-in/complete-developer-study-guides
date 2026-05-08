# Dart Interview Questions — Senior / Staff Level

## Section 1: Language Fundamentals

### Q1: What is the difference between `var`, `final`, and `const` in Dart?
**Difficulty**: Beginner  
**Answer**: `var` declares a mutable variable with type inference; the type is determined at compile time but the value can change. `final` declares a variable that can only be assigned once; it's initialized at runtime and cannot be reassigned. `const` declares a compile-time constant; the value must be known at compile time and is deeply immutable. Use `const` for values that never change (like configuration), `final` for runtime-computed values that shouldn't change (like a timestamp), and `var` for mutable state.

### Q2: Explain Dart's type system. Is Dart statically or dynamically typed?
**Difficulty**: Intermediate  
**Answer**: Dart is a statically typed language with strong type inference and optional dynamic typing. The type system is sound, meaning that if the static type checker says a value has type `T`, at runtime it's guaranteed to be `T`. Dart supports type inference through `var`, explicit type annotations, and the `dynamic` type for opting out of static checking. The analyzer performs static analysis at compile time, while runtime type checks ensure soundness during execution.

### Q3: What is the difference between `dynamic` and `Object?` in Dart?
**Difficulty**: Intermediate  
**Answer**: `dynamic` disables static type checking entirely; any member access is allowed at compile time but may fail at runtime. `Object?` is the top type in Dart's type hierarchy (nullable version of `Object`); it requires explicit type checks or casts before accessing members. Use `Object?` when you want type safety with runtime checks, and avoid `dynamic` unless interfacing with untyped APIs. `Object?` catches errors at compile time through flow analysis, while `dynamic` defers all checks to runtime.

### Q4: How does Dart's type inference work?
**Difficulty**: Intermediate  
**Answer**: Dart uses local type inference based on the initializer expression. When you declare `var x = 5;`, the compiler infers `int` from the literal. For functions, return types are inferred from return statements, and parameter types from usage context. Dart does not perform global type inference across function boundaries; function signatures must be explicit or inferred locally. The analyzer uses flow analysis to track type promotion within control flow, narrowing types based on null checks and type tests.

### Q5: What are the built-in types in Dart?
**Difficulty**: Beginner  
**Answer**: Dart's built-in types include: `int` and `double` (both subtypes of `num`), `String`, `bool`, `List<T>`, `Set<T>`, `Map<K, V>`, `Runes` (Unicode code points), `Symbol`, `Null`, and `Record` (Dart 3+). All types in Dart are objects; there are no primitive types. Numbers, strings, and booleans are immutable. Collections can be mutable or immutable depending on how they're created (literal vs `const` constructor).


## Section 2: OOP & Mixins

### Q6: Explain the difference between abstract classes and implicit interfaces in Dart.
**Difficulty**: Intermediate  
**Answer**: Abstract classes can contain both abstract methods (no implementation) and concrete methods with implementations, and are extended using `extends`. Every class in Dart implicitly defines an interface that can be implemented using `implements`, requiring the implementing class to provide all method implementations. Abstract classes support single inheritance and can have constructors, while interfaces (via `implements`) support multiple implementation and cannot have constructors. Use abstract classes for shared implementation and interfaces for contracts without implementation.

### Q7: How do mixins work in Dart? What are the constraints?
**Difficulty**: Advanced  
**Answer**: Mixins are reusable class members that can be added to classes using `with`. A mixin is declared with the `mixin` keyword and can specify `on` constraints to require a specific superclass. Mixins are applied linearly; `class C extends A with B, C` means C's methods override B's, which override A's. Mixins cannot have constructors, cannot be instantiated directly, and cannot use `extends`. They solve the diamond problem through linearization, making method resolution deterministic. Use mixins for horizontal composition of behavior across unrelated class hierarchies.

### Q8: What are factory constructors and when would you use them?
**Difficulty**: Intermediate  
**Answer**: Factory constructors use the `factory` keyword and can return an existing instance from a cache, return a subtype, or perform complex initialization logic before returning an instance. Unlike generative constructors, factory constructors don't automatically initialize instance variables and don't have access to `this` until an instance is created. Common use cases include implementing the singleton pattern, returning cached instances for immutable objects, and returning different subtypes based on constructor arguments. Factory constructors are essential for object pooling and controlling instance creation.

### Q9: Explain the difference between `extends`, `implements`, and `with`.
**Difficulty**: Beginner  
**Answer**: `extends` creates a subclass that inherits implementation from a single superclass, supporting method overriding and `super` calls. `implements` declares that a class fulfills a contract by implementing all methods of one or more interfaces, without inheriting any implementation. `with` applies one or more mixins to add reusable behavior without using inheritance. A class can extend one class, implement multiple interfaces, and use multiple mixins: `class C extends A with B, C implements D, E`. This provides flexible composition while maintaining single inheritance.

### Q10: What are named constructors and why are they useful?
**Difficulty**: Beginner  
**Answer**: Named constructors provide multiple ways to create instances with descriptive names, like `DateTime.now()` or `List.filled(10, 0)`. They improve code readability by making the construction intent explicit and allow different initialization logic for different use cases. Named constructors are declared as `ClassName.constructorName()` and can delegate to other constructors using `: this()` or `: super()`. They're particularly useful for factory patterns, deserialization (like `User.fromJson()`), and providing convenient shortcuts for common initialization patterns.


## Section 3: Null Safety

### Q11: How does Dart's sound null safety work?
**Difficulty**: Intermediate  
**Answer**: Dart's null safety is sound, meaning the type system guarantees that non-nullable types can never contain null at runtime. Types are non-nullable by default; you must explicitly add `?` to make them nullable. The compiler uses flow analysis to track when nullable variables have been checked for null, promoting them to non-nullable in safe contexts. This eliminates null reference errors at compile time rather than runtime. Sound null safety requires all dependencies to be null-safe and uses strict mode by default in Dart 2.12+.

### Q12: What is the `late` keyword and when should you use it?
**Difficulty**: Intermediate  
**Answer**: `late` declares a non-nullable variable that will be initialized later, deferring initialization until first use. It's useful for expensive initialization that should be lazy, for variables that can't be initialized in the constructor, and for top-level or static variables. The runtime throws an error if you access a `late` variable before initialization. Use `late` for circular dependencies, lazy initialization patterns, and when you're certain a variable will be initialized before use but the compiler can't prove it. Avoid overusing `late` as it bypasses compile-time safety.

### Q13: Explain the null-aware operators: `??`, `?.`, `??=`, and `!`.
**Difficulty**: Beginner  
**Answer**: `??` is the null-coalescing operator that returns the left operand if non-null, otherwise the right: `value ?? defaultValue`. `?.` is the null-aware access operator that returns null if the receiver is null: `user?.name`. `??=` assigns only if the variable is null: `name ??= 'Unknown'`. `!` is the null assertion operator that casts nullable to non-nullable, throwing if null: `nullableValue!`. Use these operators to write concise null-handling code, but avoid overusing `!` as it reintroduces runtime null errors.

### Q14: What is type promotion and how does it work with null safety?
**Difficulty**: Advanced  
**Answer**: Type promotion is when the analyzer narrows a variable's type based on control flow analysis. After a null check like `if (x != null)`, the variable `x` is promoted from `T?` to `T` within that scope. Promotion also works with type tests: `if (x is String)` promotes `x` to `String`. Promotion is flow-sensitive and respects control flow including early returns, breaks, and continues. However, promotion doesn't work for fields or getters (which could change between checks), only for local variables and parameters. This enables writing null-safe code without excessive casting.

### Q15: What are the common pitfalls with null safety?
**Difficulty**: Intermediate  
**Answer**: Common pitfalls include: overusing `!` which reintroduces runtime errors; forgetting that fields don't promote (use local variables instead); not understanding that `late` variables can still throw at runtime; mixing nullable and non-nullable types incorrectly in generics; and assuming `dynamic` is null-safe (it's not). Another pitfall is not initializing non-nullable fields in all constructor paths, which causes compile errors. Understanding flow analysis limitations is crucial; for example, closures capture variables but don't preserve promotion, and promotion is lost after potential reassignment.


## Section 4: Async & Streams

### Q16: Explain the difference between `Future` and `Stream`.
**Difficulty**: Beginner  
**Answer**: A `Future` represents a single asynchronous value that will be available in the future; it completes once with either a value or an error. A `Stream` represents a sequence of asynchronous values over time; it can emit zero, one, or many values and can be listened to multiple times (broadcast streams). Use `Future` for one-time async operations like HTTP requests or file reads, and `Stream` for continuous data like user input events, WebSocket messages, or real-time updates. Futures are consumed with `await` or `.then()`, while Streams are consumed with `await for` or `.listen()`.

### Q17: What is the difference between `async` and `async*`?
**Difficulty**: Intermediate  
**Answer**: `async` marks a function that returns a `Future` and allows using `await` inside; it returns a single value asynchronously. `async*` marks a generator function that returns a `Stream` and allows using `yield` to emit multiple values over time. An `async` function completes when it reaches the end or a return statement, while an `async*` function continues emitting values until it completes or the stream is cancelled. Use `async` for single async operations and `async*` for generating sequences of async values, like paginated API calls or real-time data feeds.

### Q18: How do you handle errors in async code?
**Difficulty**: Intermediate  
**Answer**: For `Future`-based code, use `try-catch` with `await`, or `.catchError()` with `.then()` chains. Errors propagate through the Future chain until caught. For `Stream`-based code, provide an `onError` callback to `.listen()`, or use `.handleError()` to transform errors in the stream pipeline. Uncaught async errors can be caught globally with `runZonedGuarded()`. Always handle errors explicitly; unhandled Future errors are reported but don't crash the app, while unhandled Stream errors cancel the subscription. Use `Future.wait()` with `eagerError: true` to fail fast when processing multiple Futures.

### Q19: What is the difference between single-subscription and broadcast streams?
**Difficulty**: Advanced  
**Answer**: Single-subscription streams allow only one listener and start producing events when listened to; they're the default stream type. Broadcast streams allow multiple listeners and produce events regardless of listeners; they're created with `Stream.asBroadcastStream()` or `StreamController.broadcast()`. Single-subscription streams are for one-time sequences like file reads, while broadcast streams are for events like button clicks. Broadcast streams don't buffer events for late listeners; listeners only receive events emitted after they subscribe. Converting to broadcast is expensive; prefer creating broadcast streams directly when needed.

### Q20: Explain `Future.wait()`, `Future.any()`, and `Future.forEach()`.
**Difficulty**: Intermediate  
**Answer**: `Future.wait()` takes a list of Futures and returns a Future that completes when all input Futures complete, with a list of results in order. It fails immediately if any Future fails (unless `eagerError: false`). `Future.any()` completes with the first Future to complete successfully, ignoring others. `Future.forEach()` executes an async function for each element sequentially, waiting for each to complete before starting the next. Use `wait()` for parallel operations that all must succeed, `any()` for racing multiple sources, and `forEach()` for sequential processing with async operations.

### Q21: What are `StreamTransformer` and `StreamController`?
**Difficulty**: Advanced  
**Answer**: `StreamController` creates and manages a stream, providing methods to add events (`add()`), errors (`addError()`), and close the stream (`close()`). It's the primary way to create custom streams. `StreamTransformer` modifies stream events as they flow through, transforming, filtering, or aggregating them. Built-in transformers include `map()`, `where()`, `expand()`, and `asyncMap()`. Create custom transformers with `StreamTransformer.fromHandlers()` for complex event processing. Controllers manage stream lifecycle, while transformers enable composable stream pipelines for data processing.


## Section 5: Isolates & Concurrency

### Q22: How does Dart's concurrency model differ from traditional threading?
**Difficulty**: Advanced  
**Answer**: Dart uses isolates instead of shared-memory threads; each isolate has its own memory heap and event loop, preventing race conditions and eliminating the need for locks. Isolates communicate through message passing using ports, sending only immutable data or transferable objects. This model is safer than threading but requires explicit serialization for communication. The main isolate handles UI and most app logic, while compute-intensive tasks run in background isolates. Unlike threads, isolates don't share state, making concurrent programming simpler but requiring different patterns for data sharing.

### Q23: When should you use isolates vs async/await?
**Difficulty**: Intermediate  
**Answer**: Use `async/await` for I/O-bound operations like network requests, file access, or database queries, where the operation waits for external resources. Use isolates for CPU-bound operations like JSON parsing of large payloads, image processing, encryption, or complex computations that would block the event loop. Isolates add overhead for message passing, so only use them when a task takes more than ~16ms (one frame at 60fps). For Flutter, use `compute()` as a convenient wrapper for simple isolate tasks, or `Isolate.run()` for more control.

### Q24: Explain `Isolate.spawn()` vs `Isolate.run()`.
**Difficulty**: Advanced  
**Answer**: `Isolate.spawn()` creates a long-lived isolate that requires manual setup of `SendPort`/`ReceivePort` for bidirectional communication and explicit cleanup. It's suitable for persistent background workers that handle multiple tasks. `Isolate.run()` (Dart 2.19+) is a simpler API for one-off computations; it spawns an isolate, runs a function, returns the result, and automatically cleans up. `Isolate.run()` handles serialization and communication internally, making it ideal for simple CPU-intensive tasks. Use `spawn()` for long-lived workers and `run()` for one-time computations.

### Q25: What are the limitations of isolate communication?
**Difficulty**: Advanced  
**Answer**: Isolates can only send messages that are primitives, collections of primitives, or objects that implement `SendPort`. Complex objects must be serialized (typically to JSON) before sending, which adds overhead. Large data transfers are expensive; consider using `TransferableTypedData` for efficient transfer of byte buffers. Isolates cannot share memory, so you can't pass references or closures that capture variables. Communication is asynchronous, requiring careful coordination. For Flutter, UI objects like `Widget` or `BuildContext` cannot be sent to isolates, limiting their use for UI-related tasks.

### Q26: How do you handle errors in isolates?
**Difficulty**: Intermediate  
**Answer**: For `Isolate.run()`, errors are propagated as Future errors and can be caught with try-catch. For `Isolate.spawn()`, set up error handling with `isolate.addErrorListener()` or pass an error port to the spawned isolate. Uncaught errors in isolates don't crash the main isolate but terminate the worker isolate. Always implement error handling in isolate entry points and communicate errors back to the main isolate through messages. Use `onError` and `onExit` parameters in `Isolate.spawn()` for robust error handling and cleanup. Consider wrapping isolate logic in try-catch and sending error messages explicitly.


## Section 6: Generics & Type System

### Q27: How do bounded type parameters work in Dart?
**Difficulty**: Intermediate  
**Answer**: Bounded type parameters use `extends` to constrain generic types to subtypes of a specific class or interface: `class Box<T extends Comparable<T>>`. This allows calling methods defined on the bound within the generic class. Dart supports single bounds only; you can't specify multiple bounds like `T extends A & B`. Bounded generics enable type-safe APIs that require specific capabilities from type arguments. The bound is checked at compile time, ensuring type safety. Use bounds when your generic code needs to call specific methods on the type parameter.

### Q28: What is covariance and contravariance in Dart?
**Difficulty**: Advanced  
**Answer**: Dart's generics are covariant by default for return types and contravariant for parameter types, following the Liskov Substitution Principle. However, Dart doesn't enforce strict variance rules; you can use the `covariant` keyword to override parameter type checking, allowing subtypes in overridden methods. This is unsound but pragmatic for certain patterns. For example, `List<Dog>` is not a subtype of `List<Animal>` to prevent adding a `Cat` to a `List<Dog>`. Dart's type system prioritizes usability over strict soundness in some cases, using runtime checks where static checks would be too restrictive.

### Q29: Explain reified generics in Dart.
**Difficulty**: Advanced  
**Answer**: Dart has reified generics, meaning type information is preserved at runtime, unlike Java's type erasure. You can check types with `is` and `as` operators: `if (list is List<String>)`. This enables runtime type checks and reflection on generic types. However, reification has limits; you can't instantiate a generic type directly (`new T()` doesn't work) without passing a factory function. Reified generics make Dart's type system more powerful and enable features like type-safe JSON deserialization. The runtime type information is available through `runtimeType`, though it's primarily for debugging.

### Q30: What are function types and typedefs in Dart?
**Difficulty**: Intermediate  
**Answer**: Function types describe the signature of a function: `int Function(String, {bool? flag})`. Typedefs create aliases for function types or any type, improving readability: `typedef Parser<T> = T Function(String)`. Dart 2.13+ allows typedefs for any type, not just functions: `typedef IntList = List<int>`. Function types are first-class; you can use them as parameter types, return types, and variable types. Typedefs are purely compile-time aliases; they don't create new types. Use typedefs to simplify complex type signatures and make callback types more readable.

### Q31: How does type promotion work with generics?
**Difficulty**: Advanced  
**Answer**: Type promotion works with generic types when the analyzer can prove the type is narrowed. For example, `if (list is List<String>)` promotes `list` from `List<dynamic>` to `List<String>`. However, promotion has limitations with generics; you can't promote a generic type parameter `T` to a more specific type without explicit casting. Promotion works for concrete generic types but not for type parameters themselves. Use type tests and casts explicitly when working with generic type parameters. The analyzer's flow analysis tracks promoted types through control flow, but generic type parameters require runtime checks.


## Section 7: Dart 3 Features

### Q32: What are records in Dart 3 and how do they differ from classes?
**Difficulty**: Intermediate  
**Answer**: Records are anonymous, immutable aggregate types that group multiple values: `(int, String)` or `({int id, String name})`. Unlike classes, records have structural typing (two records with the same field types are the same type), no methods, and built-in equality based on field values. Records support positional and named fields, and can be destructured in patterns. They're ideal for returning multiple values from functions without creating a dedicated class. Records are more lightweight than classes and enable functional programming patterns with less boilerplate.

### Q33: Explain pattern matching in Dart 3.
**Difficulty**: Advanced  
**Answer**: Pattern matching allows destructuring and testing values in a single expression. Patterns work in switch statements, switch expressions, if-case statements, and variable declarations. Types include: constant patterns (`case 42:`), variable patterns (`case var x:`), record patterns (`case (int x, String y):`), list patterns (`case [1, 2, ...]:`), map patterns, and object patterns (`case Point(x: 0, y: var y):`). Patterns can include guards (`case > 0 when x.isEven:`). Pattern matching makes code more concise and expressive, especially for algebraic data types and complex conditionals.

### Q34: What are sealed classes and when should you use them?
**Difficulty**: Advanced  
**Answer**: Sealed classes (Dart 3.0+) restrict which classes can extend or implement them to the same library, enabling exhaustive pattern matching. The compiler knows all possible subtypes and can verify that switch statements cover all cases. Sealed classes are perfect for algebraic data types and state machines where you want a closed set of variants. Unlike enums, sealed class subtypes can have different fields and methods. Use sealed classes for result types (`sealed class Result<T> { class Success<T> extends Result<T> { final T value; } class Error extends Result { final String message; } }`), ensuring compile-time exhaustiveness checking.

### Q35: Explain the new class modifiers in Dart 3: `base`, `interface`, `final`, `sealed`.
**Difficulty**: Advanced  
**Answer**: `base` prevents implementation outside the library but allows extension; use for classes that must be extended, not implemented. `interface` prevents extension but allows implementation; use for pure contracts. `final` prevents both extension and implementation outside the library; use for classes that shouldn't be subclassed. `sealed` restricts subtypes to the same library and enables exhaustive checking; use for closed type hierarchies. `mixin class` allows a class to be used as both a class and a mixin. These modifiers give library authors fine-grained control over API usage and enable better optimization and exhaustiveness checking.

### Q36: How do switch expressions differ from switch statements in Dart 3?
**Difficulty**: Intermediate  
**Answer**: Switch expressions return a value and must be exhaustive (cover all cases or have a default), while switch statements execute code and don't require exhaustiveness. Switch expressions use `=>` instead of `:` and don't need `break` statements. They're more concise for mapping values: `final color = switch (status) { Status.active => 'green', Status.inactive => 'gray' };`. Switch expressions support pattern matching and guards, making them powerful for complex conditionals. Use switch expressions for value mapping and switch statements for side effects. Switch expressions are expressions, so they can be used anywhere a value is expected.


## Section 8: Flutter-Dart Integration

### Q37: How does Dart's `const` keyword optimize Flutter performance?
**Difficulty**: Intermediate  
**Answer**: `const` constructors create compile-time constants that are canonicalized (only one instance exists for identical values), reducing memory usage and enabling Flutter to skip rebuilding widgets that haven't changed. When a widget is `const`, Flutter knows it's immutable and can reuse the same instance across rebuilds. This is crucial for performance in large widget trees. Use `const` for widgets that don't depend on runtime state, like static layouts or configuration. The Flutter framework uses `const` extensively for optimization; marking widgets `const` can significantly reduce rebuild overhead and improve frame rates.

### Q38: Explain `BuildContext` and why it's important in Flutter.
**Difficulty**: Intermediate  
**Answer**: `BuildContext` represents the location of a widget in the widget tree and provides access to ancestor widgets through methods like `findAncestorWidgetOfExactType()`. It's used for theme access (`Theme.of(context)`), navigation (`Navigator.of(context)`), and inherited widgets. Each widget has its own context, and the context is only valid while the widget is mounted. Common pitfalls include using context after async operations (when the widget might be unmounted) or using the wrong context for inherited widgets. Understanding context is essential for state management and accessing framework services.

### Q39: What is `InheritedWidget` and how does it enable state management?
**Difficulty**: Advanced  
**Answer**: `InheritedWidget` is a special widget that efficiently propagates data down the widget tree without passing it through every constructor. Descendant widgets access it with `context.dependOnInheritedWidgetOfExactType<T>()`, which registers them for rebuilds when the inherited widget changes. This is the foundation for state management solutions like Provider, Riverpod, and Theme. `InheritedWidget` uses the element tree to track dependencies and only rebuilds widgets that actually depend on the data. It's more efficient than passing data through constructors because it enables selective rebuilds and avoids prop drilling.

### Q40: How do you handle async operations in Flutter widgets?
**Difficulty**: Intermediate  
**Answer**: Use `FutureBuilder` for one-time async operations and `StreamBuilder` for continuous data streams. Both widgets rebuild automatically when data arrives, handling loading, error, and success states. For more control, use `StatefulWidget` with `async` methods in lifecycle hooks, storing results in state. Always check `mounted` before calling `setState()` after async operations to avoid errors if the widget was disposed. For complex async flows, consider state management solutions like BLoC or Riverpod. Avoid calling async operations in `build()` methods; instead, trigger them in `initState()` or event handlers.

### Q41: What are keys in Flutter and when should you use them?
**Difficulty**: Advanced  
**Answer**: Keys help Flutter identify widgets across rebuilds, preserving state when widgets move in the tree. `ValueKey` uses a value for identity, `ObjectKey` uses object identity, `UniqueKey` generates a unique key, and `GlobalKey` provides access to widget state from anywhere. Use keys when reordering lists, swapping widgets, or when Flutter incorrectly reuses state. Without keys, Flutter matches widgets by type and position, which can cause state to be associated with the wrong widget. Keys are essential for animated lists, form fields in dynamic layouts, and any scenario where widget identity matters beyond position.


## Section 9: Performance & Tooling

### Q42: How do you profile and optimize Dart/Flutter performance?
**Difficulty**: Advanced  
**Answer**: Use Dart DevTools for CPU profiling, memory analysis, and timeline inspection. Profile in release mode for accurate results; debug mode has additional overhead. Look for expensive build methods, excessive rebuilds, and memory leaks. Use `const` constructors, `RepaintBoundary` for complex widgets, and `ListView.builder()` for long lists. The timeline view shows frame rendering times; aim for 16ms per frame (60fps). Memory profiling identifies leaks and excessive allocations. Use `compute()` for CPU-intensive tasks to avoid blocking the UI thread. The performance overlay shows frame rendering times in real-time during development.

### Q43: What is tree shaking and how does it work in Dart?
**Difficulty**: Intermediate  
**Answer**: Tree shaking is dead code elimination performed by the Dart compiler during AOT compilation. It analyzes the entire program to identify unused code and removes it from the final binary, reducing app size. Tree shaking works at the function and class level; if a class or function is never called, it's excluded. This is why Dart's compiled apps are smaller than the sum of their dependencies. To maximize tree shaking, avoid reflection (which prevents optimization), use `const` constructors, and avoid dynamic calls. The `--split-debug-info` flag helps analyze what's included in the final build.

### Q44: Explain the difference between JIT and AOT compilation in Dart.
**Difficulty**: Intermediate  
**Answer**: JIT (Just-In-Time) compilation compiles code during runtime, enabling hot reload and faster development cycles but with slower startup and larger memory footprint. AOT (Ahead-Of-Time) compilation compiles code before runtime, producing optimized native code with fast startup and better performance but no hot reload. Flutter uses JIT in debug mode for hot reload and AOT in release mode for performance. Dart VM uses JIT for development and AOT for production. AOT enables tree shaking and aggressive optimizations, while JIT enables dynamic features and faster iteration.

### Q45: What are the key files in a Dart project and their purposes?
**Difficulty**: Beginner  
**Answer**: `pubspec.yaml` defines dependencies, project metadata, and assets; it's the project configuration file. `analysis_options.yaml` configures linter rules and static analysis settings. `lib/` contains the main source code; files here are importable by other packages. `test/` contains unit and widget tests. `bin/` contains executable scripts for command-line apps. `.dart_tool/` and `build/` are generated directories for build artifacts. `pubspec.lock` locks dependency versions for reproducible builds. Understanding these files is essential for project setup, dependency management, and maintaining code quality through linting.

### Q46: How do you use `dart fix` and `dart format`?
**Difficulty**: Beginner  
**Answer**: `dart fix` automatically applies fixes for linter warnings and deprecations, updating code to follow best practices and migrate to new APIs. Run `dart fix --dry-run` to preview changes before applying them. `dart format` formats code according to Dart style guidelines, ensuring consistent formatting across the codebase. It's idempotent and deterministic; formatting the same code twice produces the same result. Both tools integrate with CI/CD pipelines; use `dart format --set-exit-if-changed` to fail builds on unformatted code. These tools reduce code review friction and maintain code quality automatically.


## Section 10: Coding Challenges

### Q47: Implement a generic `Result<T>` type using sealed classes for error handling.
**Difficulty**: Advanced  
**Answer**: Here's a type-safe Result type that forces exhaustive error handling:

```dart
sealed class Result<T> {
  const Result();
}

final class Success<T> extends Result<T> {
  const Success(this.value);
  final T value;
}

final class Failure<T> extends Result<T> {
  const Failure(this.error, [this.stackTrace]);
  final Object error;
  final StackTrace? stackTrace;
}

// Extension methods for convenience
extension ResultExtensions<T> on Result<T> {
  R when<R>({
    required R Function(T value) success,
    required R Function(Object error, StackTrace? stackTrace) failure,
  }) {
    return switch (this) {
      Success(value: final v) => success(v),
      Failure(error: final e, stackTrace: final s) => failure(e, s),
    };
  }
  
  T getOrElse(T defaultValue) {
    return switch (this) {
      Success(value: final v) => v,
      Failure() => defaultValue,
    };
  }
  
  Result<R> map<R>(R Function(T) transform) {
    return switch (this) {
      Success(value: final v) => Success(transform(v)),
      Failure(error: final e, stackTrace: final s) => Failure(e, s),
    };
  }
}

// Usage example
Result<int> divide(int a, int b) {
  if (b == 0) return Failure(ArgumentError('Division by zero'));
  return Success(a ~/ b);
}

void main() {
  final result = divide(10, 2);
  final message = result.when(
    success: (value) => 'Result: $value',
    failure: (error, _) => 'Error: $error',
  );
  print(message); // Result: 5
}
```

This implementation uses Dart 3's sealed classes for exhaustive pattern matching, ensuring all cases are handled at compile time.

### Q48: Write a function that implements retry logic with exponential backoff for async operations.
**Difficulty**: Advanced  
**Answer**: Here's a robust retry implementation with configurable backoff:

```dart
Future<T> retryWithBackoff<T>(
  Future<T> Function() operation, {
  int maxAttempts = 3,
  Duration initialDelay = const Duration(seconds: 1),
  double backoffMultiplier = 2.0,
  bool Function(Object)? retryIf,
}) async {
  var attempt = 0;
  var delay = initialDelay;
  
  while (true) {
    attempt++;
    try {
      return await operation();
    } catch (e) {
      // Check if we should retry this error
      if (retryIf != null && !retryIf(e)) {
        rethrow;
      }
      
      // Check if we've exhausted attempts
      if (attempt >= maxAttempts) {
        rethrow;
      }
      
      // Wait before retrying with exponential backoff
      await Future.delayed(delay);
      delay *= backoffMultiplier;
    }
  }
}

// Usage example
Future<String> fetchData() async {
  final response = await retryWithBackoff(
    () => http.get(Uri.parse('https://api.example.com/data')),
    maxAttempts: 5,
    initialDelay: Duration(milliseconds: 500),
    retryIf: (error) => error is SocketException || error is TimeoutException,
  );
  return response.body;
}
```

This implementation handles transient failures gracefully with exponential backoff and selective retry logic.

### Q49: Implement a `StreamTransformer` that debounces events.
**Difficulty**: Advanced  
**Answer**: Here's a debounce transformer that delays events until a quiet period:

```dart
class DebounceTransformer<T> extends StreamTransformerBase<T, T> {
  DebounceTransformer(this.duration);
  
  final Duration duration;
  
  @override
  Stream<T> bind(Stream<T> stream) {
    late StreamController<T> controller;
    late StreamSubscription<T> subscription;
    Timer? debounceTimer;
    
    void onData(T data) {
      debounceTimer?.cancel();
      debounceTimer = Timer(duration, () {
        controller.add(data);
      });
    }
    
    void onError(Object error, StackTrace stackTrace) {
      debounceTimer?.cancel();
      controller.addError(error, stackTrace);
    }
    
    void onDone() {
      debounceTimer?.cancel();
      controller.close();
    }
    
    controller = StreamController<T>(
      onListen: () {
        subscription = stream.listen(
          onData,
          onError: onError,
          onDone: onDone,
        );
      },
      onPause: () => subscription.pause(),
      onResume: () => subscription.resume(),
      onCancel: () {
        debounceTimer?.cancel();
        return subscription.cancel();
      },
    );
    
    return controller.stream;
  }
}

// Extension for convenience
extension StreamDebounce<T> on Stream<T> {
  Stream<T> debounce(Duration duration) {
    return transform(DebounceTransformer<T>(duration));
  }
}

// Usage example
void main() async {
  final controller = StreamController<String>();
  
  controller.stream
      .debounce(Duration(milliseconds: 300))
      .listen((value) => print('Debounced: $value'));
  
  controller.add('a');
  controller.add('ab');
  controller.add('abc'); // Only this will be printed after 300ms
  
  await Future.delayed(Duration(seconds: 1));
  controller.close();
}
```

This transformer is useful for search inputs, preventing excessive API calls while typing.

### Q50: Write a mixin that adds caching capabilities to any class.
**Difficulty**: Intermediate  
**Answer**: Here's a reusable caching mixin with TTL support:

```dart
mixin Cacheable<K, V> {
  final _cache = <K, _CacheEntry<V>>{};
  
  Duration get cacheDuration => Duration(minutes: 5);
  
  V? getCached(K key) {
    final entry = _cache[key];
    if (entry == null) return null;
    
    if (DateTime.now().difference(entry.timestamp) > cacheDuration) {
      _cache.remove(key);
      return null;
    }
    
    return entry.value;
  }
  
  void setCached(K key, V value) {
    _cache[key] = _CacheEntry(value, DateTime.now());
  }
  
  void invalidate(K key) {
    _cache.remove(key);
  }
  
  void clearCache() {
    _cache.clear();
  }
  
  int get cacheSize => _cache.length;
}

class _CacheEntry<V> {
  _CacheEntry(this.value, this.timestamp);
  final V value;
  final DateTime timestamp;
}

// Usage example
class UserRepository with Cacheable<int, User> {
  @override
  Duration get cacheDuration => Duration(minutes: 10);
  
  Future<User> getUser(int id) async {
    // Check cache first
    final cached = getCached(id);
    if (cached != null) return cached;
    
    // Fetch from API
    final user = await _fetchUserFromApi(id);
    setCached(id, user);
    return user;
  }
  
  Future<User> _fetchUserFromApi(int id) async {
    // Simulate API call
    await Future.delayed(Duration(seconds: 1));
    return User(id, 'User $id');
  }
}

class User {
  User(this.id, this.name);
  final int id;
  final String name;
}
```

This mixin demonstrates composition over inheritance and can be applied to any class needing caching.

### Q51: Implement a custom `Iterable` that generates Fibonacci numbers lazily.
**Difficulty**: Intermediate  
**Answer**: Here's a lazy Fibonacci sequence generator:

```dart
class FibonacciSequence extends Iterable<int> {
  FibonacciSequence([this.maxCount]);
  
  final int? maxCount;
  
  @override
  Iterator<int> get iterator => _FibonacciIterator(maxCount);
}

class _FibonacciIterator implements Iterator<int> {
  _FibonacciIterator(this.maxCount);
  
  final int? maxCount;
  int _current = 0;
  int _previous = 1;
  int _index = 0;
  
  @override
  int get current => _current;
  
  @override
  bool moveNext() {
    if (maxCount != null && _index >= maxCount!) {
      return false;
    }
    
    if (_index == 0) {
      _current = 0;
    } else if (_index == 1) {
      _current = 1;
      _previous = 0;
    } else {
      final next = _current + _previous;
      _previous = _current;
      _current = next;
    }
    
    _index++;
    return true;
  }
}

// Usage examples
void main() {
  // Infinite sequence (use with take)
  print(FibonacciSequence().take(10).toList());
  // [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
  
  // Limited sequence
  print(FibonacciSequence(7).toList());
  // [0, 1, 1, 2, 3, 5, 8]
  
  // Lazy evaluation - only computes what's needed
  final firstLarge = FibonacciSequence()
      .where((n) => n > 1000)
      .first;
  print(firstLarge); // 1597
  
  // Works with all Iterable methods
  final evenFibs = FibonacciSequence(20)
      .where((n) => n.isEven)
      .toList();
  print(evenFibs); // [0, 2, 8, 34, 144, 610, 2584]
}
```

This demonstrates lazy evaluation, custom iterators, and integration with Dart's collection APIs.

### Q52: Create a function that safely parses JSON with type validation using patterns.
**Difficulty**: Advanced  
**Answer**: Here's a type-safe JSON parser using Dart 3 patterns:

```dart
sealed class JsonValue {
  const JsonValue();
  
  T? tryGet<T>() {
    return switch (this) {
      JsonString(value: final v) when T == String => v as T,
      JsonNumber(value: final v) when T == num || T == int || T == double => v as T,
      JsonBool(value: final v) when T == bool => v as T,
      JsonArray(value: final v) when T == List => v as T,
      JsonObject(value: final v) when T == Map => v as T,
      JsonNull() => null,
      _ => null,
    };
  }
}

final class JsonString extends JsonValue {
  const JsonString(this.value);
  final String value;
}

final class JsonNumber extends JsonValue {
  const JsonNumber(this.value);
  final num value;
}

final class JsonBool extends JsonValue {
  const JsonBool(this.value);
  final bool value;
}

final class JsonArray extends JsonValue {
  const JsonArray(this.value);
  final List<JsonValue> value;
}

final class JsonObject extends JsonValue {
  const JsonObject(this.value);
  final Map<String, JsonValue> value;
}

final class JsonNull extends JsonValue {
  const JsonNull();
}

// Parser function
JsonValue parseJsonValue(dynamic value) {
  return switch (value) {
    String s => JsonString(s),
    int n => JsonNumber(n),
    double n => JsonNumber(n),
    bool b => JsonBool(b),
    List list => JsonArray(list.map(parseJsonValue).toList()),
    Map<String, dynamic> map => JsonObject(
      map.map((k, v) => MapEntry(k, parseJsonValue(v))),
    ),
    null => JsonNull(),
    _ => throw ArgumentError('Invalid JSON value: $value'),
  };
}

// Usage example with safe extraction
void main() {
  final json = {
    'name': 'Alice',
    'age': 30,
    'active': true,
    'tags': ['dart', 'flutter'],
  };
  
  final parsed = parseJsonValue(json);
  
  if (parsed case JsonObject(value: final obj)) {
    final name = obj['name']?.tryGet<String>();
    final age = obj['age']?.tryGet<num>();
    final tags = obj['tags']?.tryGet<List>();
    
    print('Name: $name, Age: $age, Tags: $tags');
    // Name: Alice, Age: 30, Tags: [Instance of 'JsonString', Instance of 'JsonString']
  }
}
```

This approach provides compile-time safety and exhaustive pattern matching for JSON handling.



---

## Quick Reference Summary

| Category | Key Concepts |
|----------|-------------|
| **Language Fundamentals** | `var`/`final`/`const`, type inference, sound type system, built-in types |
| **OOP & Mixins** | Abstract classes, implicit interfaces, mixins with `on` constraints, factory constructors |
| **Null Safety** | Non-nullable by default, `?` for nullable, `late` for deferred init, null-aware operators |
| **Async & Streams** | `Future` for single values, `Stream` for sequences, `async`/`async*`, error propagation |
| **Isolates** | Message-passing concurrency, no shared memory, `Isolate.run()` for one-off tasks |
| **Generics** | Bounded type parameters, covariance, reified generics, function types and typedefs |
| **Dart 3 Features** | Records, pattern matching, sealed classes, class modifiers, switch expressions |
| **Flutter Integration** | `const` optimization, `BuildContext`, `InheritedWidget`, keys for widget identity |
| **Performance** | DevTools profiling, tree shaking, JIT vs AOT, `const` constructors |
| **Tooling** | `pubspec.yaml`, `dart fix`, `dart format`, `analysis_options.yaml` |

## Interview Preparation Tips

1. **Understand null safety deeply** — it's a core differentiator of modern Dart and comes up in most interviews
2. **Practice pattern matching** — Dart 3's patterns are powerful and show advanced language knowledge
3. **Know when to use isolates** — understanding concurrency vs async is crucial for performance discussions
4. **Master async programming** — Futures and Streams are fundamental to Dart/Flutter development
5. **Explain trade-offs** — senior interviews focus on when to use each feature, not just how
6. **Write idiomatic code** — follow Dart conventions for naming, formatting, and API design
7. **Understand Flutter integration** — even for backend Dart roles, Flutter knowledge demonstrates ecosystem expertise
8. **Practice coding challenges** — implement common patterns like Result types, retry logic, and custom iterables
9. **Know the tooling** — `dart fix`, `dart format`, and DevTools show production readiness
10. **Study the type system** — generics, covariance, and type promotion are advanced topics that distinguish senior candidates

## Additional Resources

- [Dart Language Tour](https://dart.dev/guides/language/language-tour) — Official comprehensive guide
- [Effective Dart](https://dart.dev/guides/language/effective-dart) — Style and best practices
- [Dart API Reference](https://api.dart.dev/) — Complete API documentation
- [Flutter Performance Best Practices](https://docs.flutter.dev/perf/best-practices) — Optimization techniques
- [Dart 3 Release Notes](https://dart.dev/resources/dart-3-migration) — New features and migration guide

