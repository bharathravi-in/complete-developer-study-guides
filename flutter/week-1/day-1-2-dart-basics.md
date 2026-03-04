# Day 1-2: Setup & Dart Basics

## 📋 Topics Covered
- Flutter SDK Installation
- Flutter CLI Commands
- Dart Fundamentals
- Async Programming
- Event Loop

---

## 🔧 Part 1: Flutter Setup

### Installation Steps

```bash
# Linux Setup
sudo snap install flutter --classic

# Verify installation
flutter doctor

# Check Flutter version
flutter --version

# Create your first project
flutter create my_first_app
cd my_first_app
flutter run
```

### Essential Flutter CLI Commands

```bash
# Create new project
flutter create app_name

# Run app
flutter run

# Build APK
flutter build apk

# Build for iOS
flutter build ios

# Analyze code
flutter analyze

# Run tests
flutter test

# Clean build
flutter clean

# Get dependencies
flutter pub get

# Upgrade dependencies
flutter pub upgrade

# Check for outdated packages
flutter pub outdated
```

---

## 📘 Part 2: Dart Basics

### 1. Variables & Data Types

```dart
void main() {
  // Variables
  String name = 'Flutter';
  int age = 5;
  double price = 99.99;
  bool isAwesome = true;
  
  // Type inference
  var language = 'Dart'; // inferred as String
  var year = 2024; // inferred as int
  
  // Final and const
  final String city = 'New York'; // Runtime constant
  const double pi = 3.14159; // Compile-time constant
  
  // Late keyword (null safety)
  late String description;
  description = 'Initialized later';
  
  // Nullable types
  String? nullableString; // Can be null
  int? nullableInt = null;
  
  // Non-nullable with default
  String message = nullableString ?? 'Default message';
  
  print('Name: $name, Age: $age, Price: \$$price');
  print('Is Awesome: $isAwesome');
  print('Late: $description');
  print('Message: $message');
}
```

### 2. Collections

```dart
void main() {
  // List
  List<String> fruits = ['Apple', 'Banana', 'Orange'];
  var numbers = [1, 2, 3, 4, 5];
  
  // List operations
  fruits.add('Mango');
  fruits.remove('Banana');
  print('Fruits: $fruits');
  print('First fruit: ${fruits.first}');
  print('Last fruit: ${fruits.last}');
  print('Length: ${fruits.length}');
  
  // Set (unique values)
  Set<int> uniqueNumbers = {1, 2, 3, 4, 5, 1, 2}; // Duplicates removed
  print('Unique numbers: $uniqueNumbers');
  
  // Map (key-value pairs)
  Map<String, int> ages = {
    'Alice': 25,
    'Bob': 30,
    'Charlie': 35,
  };
  
  ages['David'] = 28;
  print('Ages: $ages');
  print('Alice age: ${ages['Alice']}');
  
  // Iterating
  for (var fruit in fruits) {
    print('Fruit: $fruit');
  }
  
  ages.forEach((name, age) {
    print('$name is $age years old');
  });
}
```

### 3. Functions

```dart
// Basic function
String greet(String name) {
  return 'Hello, $name!';
}

// Arrow function (single expression)
String greetShort(String name) => 'Hello, $name!';

// Optional positional parameters
String sayHello(String name, [String? title]) {
  if (title != null) {
    return 'Hello, $title $name';
  }
  return 'Hello, $name';
}

// Named parameters
String introduce({required String name, required int age, String? hobby}) {
  String intro = 'I am $name, $age years old';
  if (hobby != null) {
    intro += ' and I like $hobby';
  }
  return intro;
}

// Default parameter values
String welcome({String name = 'Guest', String time = 'day'}) {
  return 'Good $time, $name!';
}

// Higher-order functions
void executeOperation(int a, int b, Function(int, int) operation) {
  print('Result: ${operation(a, b)}');
}

void main() {
  print(greet('Flutter'));
  print(sayHello('John', 'Mr.'));
  print(introduce(name: 'Alice', age: 25, hobby: 'coding'));
  print(welcome());
  print(welcome(name: 'Bob'));
  
  // Anonymous function
  executeOperation(5, 3, (a, b) => a + b);
  executeOperation(10, 2, (a, b) => a * b);
}
```

### 4. Object-Oriented Programming

```dart
// Basic class
class Person {
  // Properties
  String name;
  int age;
  
  // Constructor
  Person(this.name, this.age);
  
  // Named constructor
  Person.guest() : name = 'Guest', age = 0;
  
  // Method
  void introduce() {
    print('Hi, I am $name and I am $age years old');
  }
  
  // Getter
  String get info => '$name ($age)';
  
  // Setter
  set updateAge(int newAge) {
    if (newAge > 0) {
      age = newAge;
    }
  }
}

// Inheritance
class Employee extends Person {
  String company;
  double salary;
  
  Employee(String name, int age, this.company, this.salary) 
      : super(name, age);
  
  @override
  void introduce() {
    super.introduce();
    print('I work at $company');
  }
  
  void displaySalary() {
    print('$name earns \$$salary');
  }
}

// Abstract class
abstract class Shape {
  double getArea();
  double getPerimeter();
}

// Interface implementation
class Rectangle implements Shape {
  double width;
  double height;
  
  Rectangle(this.width, this.height);
  
  @override
  double getArea() => width * height;
  
  @override
  double getPerimeter() => 2 * (width + height);
}

// Mixin
mixin Swimming {
  void swim() {
    print('Swimming...');
  }
}

mixin Flying {
  void fly() {
    print('Flying...');
  }
}

class Duck with Swimming, Flying {
  void quack() {
    print('Quack!');
  }
}

void main() {
  var person = Person('Alice', 25);
  person.introduce();
  print(person.info);
  
  var employee = Employee('Bob', 30, 'Google', 150000);
  employee.introduce();
  employee.displaySalary();
  
  var rect = Rectangle(10, 20);
  print('Area: ${rect.getArea()}');
  print('Perimeter: ${rect.getPerimeter()}');
  
  var duck = Duck();
  duck.swim();
  duck.fly();
  duck.quack();
}
```

### 5. Null Safety

```dart
class User {
  String name;
  String? email; // Nullable
  late String id; // Late initialization
  
  User(this.name, [this.email]);
  
  void initialize() {
    id = DateTime.now().millisecondsSinceEpoch.toString();
  }
}

void processUser(User? user) {
  // Null check
  if (user != null) {
    print('User: ${user.name}');
  }
  
  // Null-aware operator
  print('Email: ${user?.email ?? 'No email'}');
  
  // Force unwrap (use carefully!)
  // print(user!.name); // Will throw if null
  
  // Null-aware cascade
  user?..name = 'Updated'
      ..email = 'new@email.com';
}

void main() {
  User user1 = User('Alice', 'alice@email.com');
  user1.initialize();
  print('User ID: ${user1.id}');
  
  User? user2;
  processUser(user2);
  
  // Null-aware assignment
  user2 ??= User('Bob');
  print('User2 name: ${user2.name}');
}
```

---

## ⚡ Part 3: Async Programming

### 1. Future Basics

```dart
import 'dart:async';

// Simple Future
Future<String> fetchUserData() {
  return Future.delayed(
    Duration(seconds: 2),
    () => 'User data loaded',
  );
}

// Future with error handling
Future<int> calculateScore() {
  return Future.delayed(
    Duration(seconds: 1),
    () {
      // Simulate error
      // throw Exception('Calculation failed');
      return 100;
    },
  );
}

// Async/Await
Future<void> loadData() async {
  print('Loading data...');
  
  try {
    String data = await fetchUserData();
    print('Data: $data');
    
    int score = await calculateScore();
    print('Score: $score');
  } catch (e) {
    print('Error: $e');
  } finally {
    print('Loading complete');
  }
}

// Multiple Futures
Future<void> loadMultipleData() async {
  print('Loading multiple data...');
  
  // Sequential (slower)
  final user = await fetchUserData();
  final score = await calculateScore();
  print('Sequential: $user, Score: $score');
  
  // Parallel (faster)
  final results = await Future.wait([
    fetchUserData(),
    calculateScore(),
  ]);
  print('Parallel results: $results');
}

void main() async {
  await loadData();
  print('---');
  await loadMultipleData();
}
```

### 2. Streams

```dart
import 'dart:async';

// Simple stream
Stream<int> countStream(int max) async* {
  for (int i = 1; i <= max; i++) {
    await Future.delayed(Duration(milliseconds: 500));
    yield i;
  }
}

// Stream controller
class ChatController {
  final StreamController<String> _messageController = 
      StreamController<String>.broadcast();
  
  Stream<String> get messages => _messageController.stream;
  
  void sendMessage(String message) {
    _messageController.add(message);
  }
  
  void dispose() {
    _messageController.close();
  }
}

// Stream transformations
void streamOperations() async {
  final numbers = Stream.fromIterable([1, 2, 3, 4, 5]);
  
  // Map
  final doubled = numbers.map((n) => n * 2);
  await for (var value in doubled) {
    print('Doubled: $value');
  }
  
  // Where (filter)
  final evenNumbers = Stream.fromIterable([1, 2, 3, 4, 5, 6])
      .where((n) => n % 2 == 0);
  print('Even numbers:');
  await for (var value in evenNumbers) {
    print(value);
  }
}

void main() async {
  // Listen to stream
  print('Counting:');
  await for (var count in countStream(5)) {
    print('Count: $count');
  }
  
  print('\n---\n');
  
  // Stream controller
  final chat = ChatController();
  
  // Subscribe to messages
  chat.messages.listen((message) {
    print('Received: $message');
  });
  
  chat.sendMessage('Hello!');
  chat.sendMessage('How are you?');
  
  await Future.delayed(Duration(seconds: 1));
  chat.dispose();
  
  print('\n---\n');
  
  // Stream operations
  await streamOperations();
}
```

### 3. Event Loop Understanding

```dart
import 'dart:async';

void demonstrateEventLoop() {
  print('1. Synchronous');
  
  // Microtask queue (higher priority)
  scheduleMicrotask(() {
    print('3. Microtask 1');
  });
  
  scheduleMicrotask(() {
    print('4. Microtask 2');
  });
  
  // Event queue (lower priority)
  Future(() {
    print('5. Future 1');
  });
  
  Future(() {
    print('6. Future 2');
  });
  
  // Immediate
  Future.microtask(() {
    print('4.5 Immediate microtask');
  });
  
  print('2. Synchronous end');
  
  // Order of execution:
  // 1. All synchronous code
  // 2. All microtasks
  // 3. Event queue items (Futures)
}

void advancedEventLoop() async {
  print('Start');
  
  Future(() => print('Future 1'));
  
  scheduleMicrotask(() => print('Microtask 1'));
  
  await Future(() => print('Await Future'));
  
  Future(() => print('Future 2'));
  
  scheduleMicrotask(() => print('Microtask 2'));
  
  print('End');
  
  // Output order:
  // Start
  // End
  // Microtask 1
  // Future 1
  // Await Future
  // Microtask 2
  // Future 2
}

void main() async {
  print('=== Event Loop Demo ===\n');
  demonstrateEventLoop();
  
  await Future.delayed(Duration(seconds: 2));
  print('\n=== Advanced Event Loop ===\n');
  
  await advancedEventLoop();
}
```

---

## 🎯 Practice Exercises

### Exercise 1: CLI Temperature Converter
```dart
import 'dart:io';

class TemperatureConverter {
  double celsiusToFahrenheit(double celsius) => (celsius * 9/5) + 32;
  double fahrenheitToCelsius(double fahrenheit) => (fahrenheit - 32) * 5/9;
  
  void run() {
    print('Temperature Converter');
    print('1. Celsius to Fahrenheit');
    print('2. Fahrenheit to Celsius');
    stdout.write('Choose option: ');
    
    var choice = stdin.readLineSync();
    stdout.write('Enter temperature: ');
    var tempStr = stdin.readLineSync();
    var temp = double.parse(tempStr ?? '0');
    
    if (choice == '1') {
      print('${temp}°C = ${celsiusToFahrenheit(temp).toStringAsFixed(2)}°F');
    } else {
      print('${temp}°F = ${fahrenheitToCelsius(temp).toStringAsFixed(2)}°C');
    }
  }
}

void main() {
  TemperatureConverter().run();
}
```

### Exercise 2: Async Data Fetcher
```dart
import 'dart:async';
import 'dart:math';

class DataFetcher {
  Future<Map<String, dynamic>> fetchUser(int id) async {
    await Future.delayed(Duration(seconds: 1));
    return {
      'id': id,
      'name': 'User $id',
      'email': 'user$id@example.com',
    };
  }
  
  Future<List<String>> fetchPosts(int userId) async {
    await Future.delayed(Duration(seconds: 1));
    return List.generate(3, (i) => 'Post ${i + 1} by User $userId');
  }
  
  Stream<int> generateNumbers(int count) async* {
    for (int i = 0; i < count; i++) {
      await Future.delayed(Duration(milliseconds: 500));
      yield Random().nextInt(100);
    }
  }
  
  Future<void> fetchAllData() async {
    print('Fetching user...');
    final user = await fetchUser(1);
    print('User: ${user['name']}');
    
    print('Fetching posts...');
    final posts = await fetchPosts(user['id']);
    print('Posts: $posts');
  }
}

void main() async {
  final fetcher = DataFetcher();
  await fetcher.fetchAllData();
  
  print('\nGenerating random numbers:');
  await for (var num in fetcher.generateNumbers(5)) {
    print('Random: $num');
  }
}
```

---

## 📌 Key Takeaways

1. **Null Safety** is mandatory in modern Dart - use `?`, `!`, `??`, and `late` appropriately
2. **async/await** makes asynchronous code readable
3. **Futures** are for single async operations
4. **Streams** are for multiple async events
5. **Event Loop** processes microtasks before event queue
6. **OOP** in Dart supports inheritance, mixins, and interfaces

---

## 🔗 Next Steps

Continue to [Day 3-4: Flutter Architecture](./day-3-4-architecture.md)

---

## 📚 Additional Resources

- [Dart Language Tour](https://dart.dev/guides/language/language-tour)
- [Dart Async Programming](https://dart.dev/codelabs/async-await)
- [Effective Dart](https://dart.dev/guides/language/effective-dart)
