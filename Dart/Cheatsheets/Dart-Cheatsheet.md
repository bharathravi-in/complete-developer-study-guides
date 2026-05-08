# Dart Cheatsheet

Quick reference for Dart 3.x syntax and patterns. Organized by the 4-week learning plan.

---

## Week 1: Dart Fundamentals

### Variables & Types

```dart
// Variable declarations
var name = 'Alice';           // type inferred as String
final now = DateTime.now();   // assigned once at runtime
const pi = 3.14159;           // compile-time constant

// Explicit types
int age = 30;
double price = 9.99;
num quantity = 3;             // accepts int or double
String greeting = 'Hi';
bool isActive = true;
dynamic flexible = 'any';     // opts out of type checking
Object obj = 42;              // root non-nullable type
Object? nullable = null;      // root nullable type

// Type conversion
int n = int.parse('42');
double d = double.parse('3.14');
String s = 42.toString();
int truncated = 3.9.toInt();  // 3
```

### Null Safety

```dart
// Nullable vs non-nullable
String name = 'Alice';        // cannot be null
String? nickname;             // can be null (defaults to null)

// Null-aware operators
String display = nickname ?? 'Anonymous';     // if-null
int? len = nickname?.length;                  // safe access
nickname ??= 'Guest';                         // assign if null
String? first = items?[0];                    // safe index
buffer?..write('a')..write('b');              // safe cascade

// Null assertion (risky!)
String definite = nickname!;  // throws if null

// late keyword
late String description;      // deferred initialization
late final cache = buildCache(); // lazy initialization
```

### Control Flow

```dart
// if/else
if (score >= 90) {
  print('A');
} else if (score >= 80) {
  print('B');
} else {
  print('C');
}

// Ternary
String grade = score >= 60 ? 'Pass' : 'Fail';

// switch (Dart 3 enhanced)
String result = switch (status) {
  'active' => 'Running',
  'paused' => 'Waiting',
  _ => 'Unknown'
};

// Pattern matching in switch
var point = (x: 1, y: 2);
switch (point) {
  case (x: 0, y: 0):
    print('Origin');
  case (x: var px, y: var py) when px == py:
    print('Diagonal');
  default:
    print('Other');
}

// Loops
for (var i = 0; i < 5; i++) { }
for (var item in list) { }
while (condition) { }
do { } while (condition);
```

### Functions

```dart
// Basic function
String greet(String name) {
  return 'Hello, $name';
}

// Arrow function
String greet(String name) => 'Hello, $name';

// Optional positional parameters
int sum(int a, [int b = 0, int c = 0]) => a + b + c;

// Named parameters
void configure({required String host, int port = 80}) { }
configure(host: 'localhost', port: 8080);

// First-class functions
Function multiply = (int a, int b) => a * b;
int apply(int x, int Function(int) fn) => fn(x);

// Closures
Function makeAdder(int addBy) {
  return (int i) => i + addBy;
}
var add2 = makeAdder(2);
print(add2(3)); // 5
```

### Collections

```dart
// List
var numbers = [1, 2, 3];
List<String> names = ['Alice', 'Bob'];
numbers.add(4);
numbers.remove(2);
print(numbers[0]);
print(numbers.length);

// Set
var tags = {'dart', 'flutter'};
Set<int> primes = {2, 3, 5, 7};
tags.add('mobile');
print(tags.contains('dart')); // true

// Map
var scores = {'Alice': 90, 'Bob': 85};
Map<String, int> ages = {'Alice': 30};
scores['Charlie'] = 88;
print(scores['Alice']);

// Spread operator
var all = [...numbers, 4, 5];
var merged = {...tags, 'web'};

// Collection-if
var nav = ['Home', if (isLoggedIn) 'Profile'];

// Collection-for
var doubled = [for (var n in numbers) n * 2];
```

### Error Handling

```dart
// try/catch/finally
try {
  var result = riskyOperation();
} on FormatException catch (e) {
  print('Format error: $e');
} on Exception catch (e, stackTrace) {
  print('Error: $e');
  print(stackTrace);
} catch (e) {
  print('Unknown: $e');
} finally {
  cleanup();
}

// throw
throw FormatException('Invalid input');
throw ArgumentError.value(value, 'value', 'Must be positive');

// Custom exception
class NetworkException implements Exception {
  final String message;
  NetworkException(this.message);
  @override
  String toString() => 'NetworkException: $message';
}
```

---

## Week 2: OOP & Collections

### Classes & Constructors

```dart
class Point {
  final double x, y;
  
  Point(this.x, this.y);                    // Default constructor
  Point.origin() : x = 0, y = 0;            // Named constructor
  Point.zero() : this(0, 0);                // Redirecting
  const Point.immutable(this.x, this.y);    // const constructor
  
  factory Point.fromJson(Map<String, dynamic> json) {
    return Point(json['x'], json['y']);     // Factory constructor
  }
  
  double get magnitude => sqrt(x * x + y * y);  // Getter
  Point translate(double dx, double dy) => Point(x + dx, y + dy);
  
  static const Point origin = Point.immutable(0, 0);  // Static
  
  @override
  String toString() => 'Point($x, $y)';
  
  @override
  bool operator ==(Object other) =>
    identical(this, other) || other is Point && x == other.x && y == other.y;
  
  @override
  int get hashCode => Object.hash(x, y);
}

// Cascade notation
var p = Point(1, 2)..translate(5, 3)..toString();
```

### Inheritance & Interfaces

```dart
// Inheritance
class Animal {
  final String name;
  Animal(this.name);
  void makeSound() => print('...');
}

class Dog extends Animal {
  Dog(String name) : super(name);
  
  @override
  void makeSound() => print('Woof!');
}

// Abstract class
abstract class Shape {
  double get area;
  double get perimeter;
}

class Circle extends Shape {
  final double radius;
  Circle(this.radius);
  
  @override
  double get area => pi * radius * radius;
  
  @override
  double get perimeter => 2 * pi * radius;
}

// Implicit interface (every class is an interface)
class Printable {
  void print() => /* ... */;
}

class Document implements Printable {
  @override
  void print() => /* ... */;
}
```

### Mixins

```dart
// Define a mixin
mixin Flyable {
  void fly() => print('Flying');
}

mixin Swimmable {
  void swim() => print('Swimming');
}

// Use mixins with 'with'
class Duck extends Animal with Flyable, Swimmable {
  Duck(String name) : super(name);
}

// Mixin with 'on' constraint
mixin Debuggable on Object {
  void debug() => print(toString());
}

class MyClass with Debuggable { }
```

### Generics

```dart
// Generic class
class Box<T> {
  final T value;
  Box(this.value);
}

var intBox = Box<int>(42);
var strBox = Box('hello');

// Generic method
T first<T>(List<T> items) => items[0];

// Bounded type parameter
class Cache<T extends Comparable<T>> {
  T? _max;
  void add(T item) {
    if (_max == null || item.compareTo(_max!) > 0) {
      _max = item;
    }
  }
}

// Multiple type parameters
class Pair<K, V> {
  final K key;
  final V value;
  Pair(this.key, this.value);
}
```

### Extension Methods

```dart
// Define extension
extension StringExtensions on String {
  bool get isBlank => trim().isEmpty;
  String capitalize() => 
    isEmpty ? this : '${this[0].toUpperCase()}${substring(1)}';
}

// Use extension
print('  '.isBlank);           // true
print('hello'.capitalize());   // Hello

// Extension on nullable type
extension NullableStringExt on String? {
  String get orEmpty => this ?? '';
}

String? name;
print(name.orEmpty);  // ''
```

### Enums

```dart
// Simple enum
enum Status { pending, active, completed }

var status = Status.active;
print(status.name);  // 'active'

// Enhanced enum (Dart 2.17+)
enum HttpMethod {
  get(verb: 'GET'),
  post(verb: 'POST'),
  put(verb: 'PUT'),
  delete(verb: 'DELETE');
  
  const HttpMethod({required this.verb});
  final String verb;
  
  bool get isSafe => this == HttpMethod.get;
}

print(HttpMethod.post.verb);    // POST
print(HttpMethod.get.isSafe);   // true

// Pattern matching on enums
String describe(Status s) => switch (s) {
  Status.pending => 'Waiting',
  Status.active => 'Running',
  Status.completed => 'Done'
};
```

### Advanced Collections

```dart
// Iterable methods
var numbers = [1, 2, 3, 4, 5];

numbers.where((n) => n.isEven);           // [2, 4]
numbers.map((n) => n * 2);                // [2, 4, 6, 8, 10]
numbers.fold(0, (sum, n) => sum + n);     // 15
numbers.expand((n) => [n, n]);            // [1, 1, 2, 2, ...]
numbers.takeWhile((n) => n < 4);          // [1, 2, 3]
numbers.skipWhile((n) => n < 3);          // [3, 4, 5]

// Method chaining
var result = numbers
  .where((n) => n > 2)
  .map((n) => n * 2)
  .toList();  // [6, 8, 10]

// any, every, contains
numbers.any((n) => n > 3);      // true
numbers.every((n) => n > 0);    // true
numbers.contains(3);            // true

// firstWhere, lastWhere, singleWhere
numbers.firstWhere((n) => n > 3);  // 4
numbers.lastWhere((n) => n < 3);   // 2
```

---

## Week 3: Async & Advanced

### Async/Await

```dart
// async function
Future<String> fetchUser() async {
  await Future.delayed(Duration(seconds: 1));
  return 'Alice';
}

// await
void main() async {
  var user = await fetchUser();
  print(user);
}

// Error handling
try {
  var data = await fetchData();
} on NetworkException catch (e) {
  print('Network error: $e');
} catch (e) {
  print('Error: $e');
}

// .then() / .catchError()
fetchUser()
  .then((name) => print(name))
  .catchError((e) => print('Error: $e'))
  .whenComplete(() => print('Done'));

// Future.wait (concurrent)
var results = await Future.wait([
  fetchA(),
  fetchB(),
  fetchC(),
]);

// Future.any (first to complete)
var winner = await Future.any([
  slowSource(),
  fastSource(),
]);

// Create futures
Future.value(42);
Future.error(Exception('Failed'));
Future.delayed(Duration(seconds: 1), () => 'Done');
```

### Streams

```dart
// Create stream
Stream<int> countStream() async* {
  for (var i = 1; i <= 5; i++) {
    await Future.delayed(Duration(seconds: 1));
    yield i;
  }
}

// Listen to stream
await for (var value in countStream()) {
  print(value);
}

// StreamController
var controller = StreamController<String>();
controller.stream.listen((data) => print(data));
controller.add('Hello');
controller.close();

// Broadcast stream
var broadcast = controller.stream.asBroadcastStream();

// Stream transformations
stream
  .where((n) => n.isEven)
  .map((n) => n * 2)
  .listen((n) => print(n));

// StreamTransformer
var transformer = StreamTransformer<int, String>.fromHandlers(
  handleData: (value, sink) => sink.add('Value: $value'),
);
stream.transform(transformer).listen(print);
```

### Isolates

```dart
import 'dart:isolate';

// Isolate.run (Dart 2.19+)
var result = await Isolate.run(() {
  return heavyComputation();
});

// Isolate.spawn (manual)
void isolateEntry(SendPort sendPort) {
  var result = heavyComputation();
  sendPort.send(result);
}

void main() async {
  var receivePort = ReceivePort();
  await Isolate.spawn(isolateEntry, receivePort.sendPort);
  var result = await receivePort.first;
  print(result);
}
```

### Dart 3 Features

```dart
// Records
var point = (x: 1, y: 2);
print(point.x);  // 1

(int, String) record = (42, 'answer');
print(record.$1);  // 42
print(record.$2);  // answer

// Destructuring
var (x, y) = (1, 2);
var (a: first, b: second) = (a: 10, b: 20);

// Pattern matching
var shape = Circle(radius: 5);
var area = switch (shape) {
  Circle(radius: var r) => pi * r * r,
  Rectangle(width: var w, height: var h) => w * h,
  _ => 0.0
};

// Guard clauses
switch (value) {
  case int n when n > 0:
    print('Positive');
  case int n when n < 0:
    print('Negative');
  default:
    print('Zero');
}

// Sealed classes
sealed class Result {}
class Success extends Result {}
class Failure extends Result {}

String handle(Result r) => switch (r) {
  Success() => 'OK',
  Failure() => 'Error'
  // Compiler ensures all cases covered
};

// Class modifiers
final class CannotExtend {}
base class MustExtend {}
interface class MustImplement {}
```

### FFI Basics

```dart
import 'dart:ffi';
import 'dart:io';

// Load native library
final dylib = Platform.isWindows
  ? DynamicLibrary.open('native.dll')
  : DynamicLibrary.open('libnative.so');

// Define C function signature
typedef NativeAdd = Int32 Function(Int32, Int32);
typedef DartAdd = int Function(int, int);

// Lookup function
final add = dylib.lookupFunction<NativeAdd, DartAdd>('add');

// Call native function
print(add(2, 3));  // 5

// Struct
class Point extends Struct {
  @Double()
  external double x;
  
  @Double()
  external double y;
}
```

### Typedefs

```dart
// Function typedef
typedef IntOperation = int Function(int, int);

IntOperation add = (a, b) => a + b;
IntOperation multiply = (a, b) => a * b;

// Generic typedef
typedef Predicate<T> = bool Function(T);

Predicate<int> isEven = (n) => n % 2 == 0;
Predicate<String> isEmpty = (s) => s.isEmpty;

// Type alias (Dart 2.13+)
typedef Json = Map<String, dynamic>;

Json user = {'name': 'Alice', 'age': 30};
```

---

## Week 4: Flutter & Interview Prep

### Flutter Patterns

```dart
// const constructors (performance)
const Text('Hello');
const Padding(padding: EdgeInsets.all(8.0));

// Key types
ValueKey('unique-id')
ObjectKey(myObject)
GlobalKey()

// BuildContext
Widget build(BuildContext context) {
  var theme = Theme.of(context);
  var mediaQuery = MediaQuery.of(context);
  return Container();
}

// InheritedWidget pattern
class MyInherited extends InheritedWidget {
  final int data;
  
  const MyInherited({
    required this.data,
    required Widget child,
  }) : super(child: child);
  
  static MyInherited? of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<MyInherited>();
  }
  
  @override
  bool updateShouldNotify(MyInherited old) => data != old.data;
}
```

### State Management

```dart
// ChangeNotifier
class Counter extends ChangeNotifier {
  int _count = 0;
  int get count => _count;
  
  void increment() {
    _count++;
    notifyListeners();
  }
}

// ValueNotifier
var counter = ValueNotifier<int>(0);
counter.value++;

// StreamBuilder
StreamBuilder<int>(
  stream: countStream,
  builder: (context, snapshot) {
    if (snapshot.hasData) {
      return Text('${snapshot.data}');
    }
    return CircularProgressIndicator();
  },
)

// FutureBuilder
FutureBuilder<String>(
  future: fetchUser(),
  builder: (context, snapshot) {
    if (snapshot.connectionState == ConnectionState.done) {
      return Text(snapshot.data ?? 'Error');
    }
    return CircularProgressIndicator();
  },
)
```

### Design Patterns

```dart
// Singleton
class AppConfig {
  static final AppConfig _instance = AppConfig._internal();
  factory AppConfig() => _instance;
  AppConfig._internal();
}

// Factory
abstract class Animal {
  factory Animal(String type) => switch (type) {
    'dog' => Dog(),
    'cat' => Cat(),
    _ => throw ArgumentError('Unknown type')
  };
}

// Builder
class HttpRequestBuilder {
  String? _url;
  Map<String, String> _headers = {};
  
  HttpRequestBuilder url(String url) { _url = url; return this; }
  HttpRequestBuilder header(String k, String v) { _headers[k] = v; return this; }
  HttpRequest build() => HttpRequest(_url!, _headers);
}

// Observer (via Stream)
class EventBus {
  final _controller = StreamController<Event>.broadcast();
  Stream<Event> get events => _controller.stream;
  void fire(Event event) => _controller.add(event);
}

// Repository
abstract class UserRepository {
  Future<User> getUser(String id);
  Future<void> saveUser(User user);
}
```

### Testing

```dart
import 'package:test/test.dart';

// Unit test
void main() {
  test('addition', () {
    expect(2 + 2, equals(4));
  });
  
  group('Calculator', () {
    late Calculator calc;
    
    setUp(() {
      calc = Calculator();
    });
    
    test('add', () {
      expect(calc.add(2, 3), 5);
    });
    
    test('divide by zero throws', () {
      expect(() => calc.divide(1, 0), throwsA(isA<ArgumentError>()));
    });
  });
}

// Mocking with mockito
import 'package:mockito/mockito.dart';

class MockUserRepo extends Mock implements UserRepository {}

void main() {
  test('fetch user', () async {
    var repo = MockUserRepo();
    when(repo.getUser('1')).thenAnswer((_) async => User('Alice'));
    
    var user = await repo.getUser('1');
    expect(user.name, 'Alice');
    verify(repo.getUser('1')).called(1);
  });
}
```

### Tooling Commands

```bash
# Project
dart create my_app
flutter create my_app

# Run & Test
dart run
flutter run
dart test
flutter test

# Code Quality
dart format .
dart analyze
flutter analyze
dart fix --apply

# Packages
dart pub get
dart pub upgrade
dart pub outdated

# Build
dart compile exe bin/main.dart
dart compile js web/main.dart
dart doc
```

---

## Quick Tips

- **Prefer `const`** for compile-time constants (performance in Flutter)
- **Use `final`** for runtime-assigned immutable values
- **Avoid `dynamic`** — prefer `Object?` for type safety
- **Always override `==` and `hashCode` together**
- **Use `late` sparingly** — it moves safety to runtime
- **Prefer `async/await`** over `.then()` for readability
- **Use `Future.wait`** for concurrent operations
- **Leverage extension methods** to add functionality to existing types
- **Pattern matching** (Dart 3) makes switch statements powerful
- **Sealed classes** enable exhaustive pattern matching

---

## Resources

- [Dart Language Tour](https://dart.dev/guides/language/language-tour)
- [Effective Dart](https://dart.dev/guides/language/effective-dart)
- [Dart API Reference](https://api.dart.dev)
- [Flutter Documentation](https://flutter.dev/docs)
