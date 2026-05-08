# Day 24: Design Patterns

## 🎯 What You'll Learn
- Singleton pattern for global state and services
- Factory pattern for object creation and polymorphism
- Builder pattern for complex object construction
- Observer pattern (already seen in `ChangeNotifier`)
- Command pattern for undo/redo and action queuing
- Repository pattern for data access abstraction
- Dart-idiomatic implementations using named constructors, mixins, and extensions

## 📚 Core Concepts

Design patterns are reusable solutions to common software design problems. Dart's language features — named constructors, factory constructors, mixins, extension methods, and first-class functions — enable elegant implementations of classic patterns. This day covers the patterns most relevant to Flutter and Dart development, with idiomatic code examples.

### Singleton Pattern

The Singleton pattern ensures a class has only one instance and provides a global access point to it. In Dart, the idiomatic way to implement a singleton is with a private constructor and a static instance:

```dart
class Logger {
  static final Logger _instance = Logger._internal();
  factory Logger() => _instance;
  Logger._internal();

  void log(String message) => print('[LOG] $message');
}
```

The `factory` constructor returns the same `_instance` every time. This is thread-safe in Dart because static field initialization is lazy and happens once.

**Use cases**: Logging, configuration, database connections, HTTP clients.

**Caution**: Singletons are global mutable state — they make testing harder and create hidden dependencies. Prefer dependency injection when possible.

### Factory Pattern

The Factory pattern uses a method to create objects, allowing subclasses or logic to decide which concrete class to instantiate. Dart's `factory` constructors are perfect for this:

```dart
abstract class Shape {
  void draw();

  factory Shape(String type) {
    switch (type) {
      case 'circle':
        return Circle();
      case 'square':
        return Square();
      default:
        throw ArgumentError('Unknown shape: $type');
    }
  }
}

class Circle implements Shape {
  @override
  void draw() => print('Drawing a circle');
}

class Square implements Shape {
  @override
  void draw() => print('Drawing a square');
}
```

The `factory Shape(type)` constructor returns different concrete types based on the input. This decouples client code from concrete classes.

**Use cases**: Parsing (e.g., `JsonCodec.decoder`), platform-specific implementations, plugin systems.

### Builder Pattern

The Builder pattern constructs complex objects step-by-step. In Dart, you can use method chaining with a fluent API:

```dart
class HttpRequest {
  String? _url;
  Map<String, String> _headers = {};
  String? _body;

  HttpRequest url(String url) {
    _url = url;
    return this;
  }

  HttpRequest header(String key, String value) {
    _headers[key] = value;
    return this;
  }

  HttpRequest body(String body) {
    _body = body;
    return this;
  }

  Future<String> send() async {
    if (_url == null) throw StateError('URL not set');
    // Simulate HTTP request
    return 'Response from $_url';
  }
}

// Usage:
final response = await HttpRequest()
    .url('https://api.example.com')
    .header('Authorization', 'Bearer token')
    .body('{"key": "value"}')
    .send();
```

Each method returns `this`, enabling chaining. This is more readable than a constructor with many optional parameters.

**Use cases**: HTTP clients, query builders, UI component configuration.

### Observer Pattern

The Observer pattern defines a one-to-many dependency: when one object changes state, all dependents are notified. Dart's `ChangeNotifier` (from Flutter) is a built-in implementation:

```dart
class Stock extends ChangeNotifier {
  double _price = 100.0;
  double get price => _price;

  void updatePrice(double newPrice) {
    _price = newPrice;
    notifyListeners(); // notifies all observers
  }
}
```

Observers register with `addListener(callback)` and are notified when `notifyListeners()` is called. This is the foundation of Flutter's reactive state management.

**Use cases**: State management, event systems, MVC/MVVM architectures.

### Command Pattern

The Command pattern encapsulates a request as an object, allowing you to parameterize clients with different requests, queue requests, and support undo/redo. In Dart, use classes with an `execute()` method:

```dart
abstract class Command {
  void execute();
  void undo();
}

class IncrementCommand implements Command {
  final Counter counter;
  IncrementCommand(this.counter);

  @override
  void execute() => counter.increment();

  @override
  void undo() => counter.decrement();
}

class Counter {
  int value = 0;
  void increment() => value++;
  void decrement() => value--;
}

class CommandHistory {
  final List<Command> _history = [];

  void execute(Command command) {
    command.execute();
    _history.add(command);
  }

  void undo() {
    if (_history.isNotEmpty) {
      _history.removeLast().undo();
    }
  }
}
```

This enables undo/redo, macro recording, and transactional operations.

**Use cases**: Text editors, drawing apps, transactional systems, event sourcing.

### Repository Pattern

The Repository pattern abstracts data access, providing a collection-like interface to the domain layer. It decouples business logic from data sources (database, network, cache):

```dart
abstract class UserRepository {
  Future<User> getUser(int id);
  Future<void> saveUser(User user);
}

class ApiUserRepository implements UserRepository {
  final HttpClient _client;
  ApiUserRepository(this._client);

  @override
  Future<User> getUser(int id) async {
    final response = await _client.get('/users/$id');
    return User.fromJson(response);
  }

  @override
  Future<void> saveUser(User user) async {
    await _client.post('/users', body: user.toJson());
  }
}

class CachedUserRepository implements UserRepository {
  final UserRepository _remote;
  final Map<int, User> _cache = {};

  CachedUserRepository(this._remote);

  @override
  Future<User> getUser(int id) async {
    if (_cache.containsKey(id)) return _cache[id]!;
    final user = await _remote.getUser(id);
    _cache[id] = user;
    return user;
  }

  @override
  Future<void> saveUser(User user) async {
    await _remote.saveUser(user);
    _cache[user.id] = user;
  }
}
```

The domain layer depends on `UserRepository`, not on concrete implementations. This enables testing with mock repositories and swapping data sources without changing business logic.

**Use cases**: Data access layers, clean architecture, testable code.

### Dart-Specific Idioms

Dart's language features enable concise pattern implementations:

- **Named constructors**: `DateTime.now()`, `List.filled(10, 0)` — factory methods without a separate factory class
- **Factory constructors**: Return different types or cached instances
- **Mixins**: Share behavior across unrelated classes (e.g., `with ChangeNotifier`)
- **Extension methods**: Add methods to existing types without inheritance
- **First-class functions**: Pass behavior as parameters (strategy pattern without classes)

## 💻 Code Examples

### Example 1: Singleton with lazy initialization

```dart
/// Thread-safe singleton with lazy initialization.
class DatabaseConnection {
  static DatabaseConnection? _instance;
  final String connectionString;

  // Private constructor
  DatabaseConnection._internal(this.connectionString);

  // Factory constructor returns the singleton instance
  factory DatabaseConnection(String connectionString) {
    _instance ??= DatabaseConnection._internal(connectionString);
    return _instance!;
  }

  void query(String sql) {
    print('Executing: $sql on $connectionString');
  }
}

void main() {
  final db1 = DatabaseConnection('localhost:5432');
  final db2 = DatabaseConnection('localhost:5432');
  print(identical(db1, db2)); // true — same instance
}
```

### Example 2: Factory pattern with named constructors

```dart
abstract class Animal {
  void speak();

  // Factory constructor delegates to concrete types
  factory Animal.fromType(String type) {
    switch (type) {
      case 'dog':
        return Dog();
      case 'cat':
        return Cat();
      default:
        throw ArgumentError('Unknown animal type: $type');
    }
  }
}

class Dog implements Animal {
  @override
  void speak() => print('Woof!');
}

class Cat implements Animal {
  @override
  void speak() => print('Meow!');
}

void main() {
  final animals = ['dog', 'cat', 'dog']
      .map((type) => Animal.fromType(type))
      .toList();

  for (final animal in animals) {
    animal.speak(); // Woof! Meow! Woof!
  }
}
```

### Example 3: Builder pattern with method chaining

```dart
class QueryBuilder {
  String? _table;
  final List<String> _columns = [];
  String? _where;
  int? _limit;

  QueryBuilder select(List<String> columns) {
    _columns.addAll(columns);
    return this;
  }

  QueryBuilder from(String table) {
    _table = table;
    return this;
  }

  QueryBuilder where(String condition) {
    _where = condition;
    return this;
  }

  QueryBuilder limit(int count) {
    _limit = count;
    return this;
  }

  String build() {
    if (_table == null) throw StateError('Table not specified');
    final cols = _columns.isEmpty ? '*' : _columns.join(', ');
    var sql = 'SELECT $cols FROM $_table';
    if (_where != null) sql += ' WHERE $_where';
    if (_limit != null) sql += ' LIMIT $_limit';
    return sql;
  }
}

void main() {
  final query = QueryBuilder()
      .select(['id', 'name'])
      .from('users')
      .where('age > 18')
      .limit(10)
      .build();

  print(query); // SELECT id, name FROM users WHERE age > 18 LIMIT 10
}
```

### Example 4: Command pattern with undo/redo

```dart
abstract class Command {
  void execute();
  void undo();
}

class TextEditor {
  String content = '';

  void insert(String text) => content += text;
  void delete(int count) => content = content.substring(0, content.length - count);
}

class InsertCommand implements Command {
  final TextEditor editor;
  final String text;

  InsertCommand(this.editor, this.text);

  @override
  void execute() => editor.insert(text);

  @override
  void undo() => editor.delete(text.length);
}

class CommandManager {
  final List<Command> _history = [];
  int _currentIndex = -1;

  void execute(Command command) {
    // Discard redo history when a new command is executed
    _history.removeRange(_currentIndex + 1, _history.length);
    command.execute();
    _history.add(command);
    _currentIndex++;
  }

  void undo() {
    if (_currentIndex >= 0) {
      _history[_currentIndex].undo();
      _currentIndex--;
    }
  }

  void redo() {
    if (_currentIndex < _history.length - 1) {
      _currentIndex++;
      _history[_currentIndex].execute();
    }
  }
}

void main() {
  final editor = TextEditor();
  final manager = CommandManager();

  manager.execute(InsertCommand(editor, 'Hello '));
  manager.execute(InsertCommand(editor, 'World'));
  print(editor.content); // Hello World

  manager.undo();
  print(editor.content); // Hello 

  manager.redo();
  print(editor.content); // Hello World
}
```

## ⚠️ Common Pitfalls

- **Overusing Singleton**: Singletons are global mutable state — they make testing hard and create hidden dependencies. Prefer dependency injection (passing instances via constructors) when possible.
- **Forgetting to dispose Observers**: When using `ChangeNotifier`, always call `removeListener()` or `dispose()` to avoid memory leaks.
- **Builder pattern without validation**: Builders should validate required fields in the `build()` method and throw `StateError` if the object is incomplete.
- **Command pattern without undo logic**: If you implement `execute()` but not `undo()`, you lose the main benefit of the pattern. Always implement both.
- **Repository pattern leaking implementation details**: The repository interface should use domain types, not database-specific types (e.g., return `User`, not `Map<String, dynamic>`).

## ❓ Interview Questions

### Q1: What is the Singleton pattern and how do you implement it in Dart?
**Answer**: The Singleton pattern ensures a class has only one instance and provides a global access point to it. In Dart, the idiomatic implementation uses a private named constructor and a `factory` constructor that returns a static instance. The factory constructor is called every time you write `ClassName()`, but it returns the same cached instance. This is thread-safe because Dart's static field initialization is lazy and happens once. Singletons are useful for logging, configuration, and shared resources, but they create global mutable state and make testing harder, so prefer dependency injection when possible.

### Q2: What is the difference between a factory constructor and a named constructor in Dart?
**Answer**: A named constructor is a way to provide multiple constructors with descriptive names (e.g., `DateTime.now()`, `List.filled(10, 0)`). It always creates a new instance of the class. A `factory` constructor can return an existing instance, a subclass instance, or even a cached object — it doesn't have to create a new instance. Factory constructors are used for the Singleton pattern, object pooling, and returning different types based on parameters. Named constructors are for convenience and clarity; factory constructors are for controlling object creation.

### Q3: Explain the Builder pattern and when you would use it.
**Answer**: The Builder pattern constructs complex objects step-by-step using a fluent API with method chaining. Each method sets a property and returns `this`, allowing calls to be chained. The final `build()` method validates required fields and returns the constructed object. Use the Builder pattern when an object has many optional parameters (to avoid constructors with 10+ parameters), when construction requires multiple steps, or when you want to enforce validation before the object is created. Examples include HTTP request builders, query builders, and UI component configuration.

### Q4: What is the Repository pattern and why is it useful?
**Answer**: The Repository pattern abstracts data access behind a collection-like interface, decoupling business logic from data sources (database, network, cache). The domain layer depends on a `Repository` interface, not on concrete implementations. This enables testing with mock repositories, swapping data sources without changing business logic, and adding caching or logging layers transparently. For example, a `UserRepository` interface might have `getUser(id)` and `saveUser(user)` methods, with implementations for API, local database, and in-memory cache. The pattern is central to clean architecture and testable code.

### Q5: How does the Command pattern enable undo/redo functionality?
**Answer**: The Command pattern encapsulates each action as an object with `execute()` and `undo()` methods. A `CommandManager` maintains a history stack of executed commands. When the user performs an action, the manager calls `execute()` and pushes the command onto the stack. To undo, the manager pops the last command and calls `undo()`. To redo, it re-executes the command. This works because each command knows how to reverse itself. The pattern also enables macro recording (replaying a sequence of commands), transactional operations, and event sourcing.

### Q6: What are the trade-offs of using the Singleton pattern?
**Answer**: Singletons provide global access to a single instance, which is convenient for shared resources like loggers or configuration. However, they create global mutable state, which makes code harder to test (you can't easily mock or reset the singleton between tests), harder to reason about (any code can modify the singleton), and harder to parallelize (singletons are shared across isolates in Dart). Singletons also hide dependencies — a class that uses a singleton doesn't declare that dependency in its constructor, making the dependency graph opaque. Prefer dependency injection (passing instances via constructors) when possible, and reserve singletons for truly global, immutable resources.

## 🔑 Key Takeaways
- Singleton: one instance, global access — use `factory` constructor and static field
- Factory: control object creation — use `factory` constructor to return different types
- Builder: step-by-step construction with method chaining — validate in `build()`
- Observer: one-to-many notification — `ChangeNotifier` is Dart's built-in implementation
- Command: encapsulate actions as objects — enables undo/redo and macro recording
- Repository: abstract data access — decouples business logic from data sources
- Dart idioms: named constructors, factory constructors, mixins, extensions, first-class functions

## 🔗 Related Topics
- [Day 08: Classes & Constructors](../Week-2-OOP-Collections/Day-08-Classes-Constructors.md) — factory constructors
- [Day 23: State Management Patterns](./Day-23-State-Management-Patterns.md) — `ChangeNotifier` (Observer pattern)
- [JavaScript Design Patterns](../../JavaScript/30-Day-JS-Mastery/Week-3-Advanced/Day-18-Design-Patterns.md) — cross-language comparison
- [Day 26: Testing in Dart](./Day-26-Testing-in-Dart.md) — mocking repositories
