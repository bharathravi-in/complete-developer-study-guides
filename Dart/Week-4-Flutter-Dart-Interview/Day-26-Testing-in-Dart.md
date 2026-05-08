# Day 26: Testing in Dart

## 🎯 What You'll Learn
- `package:test` — Dart's official testing framework
- Writing unit tests for functions, classes, and business logic
- Mocking dependencies with `package:mockito` and code generation
- Widget tests overview (Flutter-specific)
- Test-driven development (TDD) workflow
- Test organization: `group`, `setUp`, `tearDown`
- Async testing with `expectAsync` and `expectLater`

## 📚 Core Concepts

Testing is essential for maintaining code quality, catching regressions, and enabling refactoring with confidence. Dart provides `package:test` for unit and integration tests, and Flutter adds `flutter_test` for widget tests. This day covers unit testing in Dart — the foundation for all testing strategies.

### `package:test` — The Testing Framework

`package:test` is Dart's official testing framework. It provides:
- `test()` — defines a single test case
- `group()` — organizes related tests
- `expect()` — asserts expected values
- `setUp()` / `tearDown()` — runs before/after each test
- `setUpAll()` / `tearDownAll()` — runs once before/after all tests in a group

Basic structure:

```dart
import 'package:test/test.dart';

void main() {
  test('addition works', () {
    expect(2 + 2, equals(4));
  });
}
```

Run tests with `dart test` or `flutter test`.

### Writing Unit Tests

Unit tests verify individual functions, methods, or classes in isolation. They should be:
- **Fast**: Run in milliseconds
- **Isolated**: No dependencies on external systems (databases, networks)
- **Repeatable**: Same result every time
- **Self-validating**: Pass or fail automatically (no manual inspection)

Example:

```dart
class Calculator {
  int add(int a, int b) => a + b;
  int divide(int a, int b) {
    if (b == 0) throw ArgumentError('Cannot divide by zero');
    return a ~/ b;
  }
}

void main() {
  group('Calculator', () {
    late Calculator calc;

    setUp(() {
      calc = Calculator(); // runs before each test
    });

    test('add returns sum', () {
      expect(calc.add(2, 3), equals(5));
    });

    test('divide throws on zero', () {
      expect(() => calc.divide(10, 0), throwsArgumentError);
    });
  });
}
```

### Matchers — Flexible Assertions

`expect()` uses matchers to define expected values. Common matchers:

| Matcher | Meaning |
|---------|---------|
| `equals(value)` | Deep equality |
| `same(value)` | Identity (`identical`) |
| `isTrue`, `isFalse` | Boolean checks |
| `isNull`, `isNotNull` | Null checks |
| `greaterThan(n)`, `lessThan(n)` | Numeric comparisons |
| `contains(item)` | Collection membership |
| `throwsA(matcher)` | Exception matching |
| `completion(matcher)` | Future completion |

You can combine matchers with `allOf`, `anyOf`, and `isNot`.

### Mocking with `package:mockito`

Mocking replaces real dependencies with test doubles, allowing you to:
- Test in isolation (no database, no network)
- Control behavior (return specific values, throw errors)
- Verify interactions (was a method called? with what arguments?)

`package:mockito` uses code generation to create mocks:

```dart
// user_repository.dart
abstract class UserRepository {
  Future<User> getUser(int id);
}

// user_service_test.dart
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:test/test.dart';

@GenerateMocks([UserRepository])
import 'user_service_test.mocks.dart';

void main() {
  test('UserService fetches user', () async {
    final mockRepo = MockUserRepository();
    when(mockRepo.getUser(1)).thenAnswer((_) async => User(id: 1, name: 'Alice'));

    final service = UserService(mockRepo);
    final user = await service.fetchUser(1);

    expect(user.name, equals('Alice'));
    verify(mockRepo.getUser(1)).called(1);
  });
}
```

Run `dart run build_runner build` to generate `*.mocks.dart` files.

### Test Organization

Use `group()` to organize related tests:

```dart
void main() {
  group('String', () {
    test('split returns list', () {
      expect('a,b,c'.split(','), equals(['a', 'b', 'c']));
    });

    test('trim removes whitespace', () {
      expect('  hello  '.trim(), equals('hello'));
    });
  });

  group('List', () {
    test('add increases length', () {
      final list = [1, 2];
      list.add(3);
      expect(list.length, equals(3));
    });
  });
}
```

Use `setUp()` and `tearDown()` for common initialization and cleanup:

```dart
group('Database', () {
  late Database db;

  setUp(() {
    db = Database.inMemory(); // runs before each test
  });

  tearDown(() {
    db.close(); // runs after each test
  });

  test('insert adds row', () {
    db.insert('users', {'name': 'Alice'});
    expect(db.count('users'), equals(1));
  });
});
```

### Async Testing

Use `async` and `await` in tests just like regular code:

```dart
test('fetchData returns data', () async {
  final data = await fetchData();
  expect(data, isNotEmpty);
});
```

For streams, use `expectLater` with `emitsInOrder`:

```dart
test('stream emits values', () {
  final stream = Stream.fromIterable([1, 2, 3]);
  expectLater(stream, emitsInOrder([1, 2, 3]));
});
```

### Test-Driven Development (TDD)

TDD is a workflow where you write tests before implementation:

1. **Red**: Write a failing test for the next feature
2. **Green**: Write the minimal code to make the test pass
3. **Refactor**: Improve the code while keeping tests green

Benefits:
- Forces you to think about API design before implementation
- Ensures every feature has tests
- Provides fast feedback on correctness

Example TDD cycle:

```dart
// 1. Red: Write failing test
test('User.fromJson parses JSON', () {
  final json = {'id': 1, 'name': 'Alice'};
  final user = User.fromJson(json);
  expect(user.id, equals(1));
  expect(user.name, equals('Alice'));
});

// 2. Green: Implement minimal code
class User {
  final int id;
  final String name;
  User({required this.id, required this.name});

  factory User.fromJson(Map<String, dynamic> json) {
    return User(id: json['id'], name: json['name']);
  }
}

// 3. Refactor: Improve (e.g., add validation, null safety)
```

### Widget Tests (Flutter-Specific)

Widget tests verify UI behavior. They use `flutter_test` and `testWidgets`:

```dart
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('Counter increments', (tester) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('0'), findsOneWidget);

    await tester.tap(find.byIcon(Icons.add));
    await tester.pump();

    expect(find.text('1'), findsOneWidget);
  });
}
```

Widget tests are slower than unit tests but faster than integration tests.

## 💻 Code Examples

### Example 1: Basic unit tests with `package:test`

```dart
import 'package:test/test.dart';

int factorial(int n) {
  if (n < 0) throw ArgumentError('n must be non-negative');
  if (n == 0) return 1;
  return n * factorial(n - 1);
}

void main() {
  group('factorial', () {
    test('returns 1 for 0', () {
      expect(factorial(0), equals(1));
    });

    test('returns correct value for positive n', () {
      expect(factorial(5), equals(120));
      expect(factorial(3), equals(6));
    });

    test('throws for negative n', () {
      expect(() => factorial(-1), throwsArgumentError);
    });
  });
}
```

### Example 2: Mocking with `package:mockito`

```dart
// http_client.dart
abstract class HttpClient {
  Future<String> get(String url);
}

// weather_service.dart
class WeatherService {
  final HttpClient client;
  WeatherService(this.client);

  Future<String> getWeather(String city) async {
    final response = await client.get('https://api.weather.com/$city');
    return response;
  }
}

// weather_service_test.dart
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';
import 'package:test/test.dart';

@GenerateMocks([HttpClient])
import 'weather_service_test.mocks.dart';

void main() {
  group('WeatherService', () {
    late MockHttpClient mockClient;
    late WeatherService service;

    setUp(() {
      mockClient = MockHttpClient();
      service = WeatherService(mockClient);
    });

    test('getWeather returns response', () async {
      // Arrange: set up mock behavior
      when(mockClient.get(any))
          .thenAnswer((_) async => 'Sunny, 25°C');

      // Act: call the method under test
      final weather = await service.getWeather('London');

      // Assert: verify result and interactions
      expect(weather, equals('Sunny, 25°C'));
      verify(mockClient.get('https://api.weather.com/London')).called(1);
    });

    test('getWeather throws on error', () async {
      when(mockClient.get(any)).thenThrow(Exception('Network error'));

      expect(
        () => service.getWeather('London'),
        throwsException,
      );
    });
  });
}
```

### Example 3: Testing async code with streams

```dart
import 'dart:async';
import 'package:test/test.dart';

Stream<int> countStream(int max) async* {
  for (int i = 1; i <= max; i++) {
    await Future.delayed(const Duration(milliseconds: 10));
    yield i;
  }
}

void main() {
  group('countStream', () {
    test('emits values in order', () {
      final stream = countStream(3);
      expectLater(stream, emitsInOrder([1, 2, 3]));
    });

    test('emits correct count', () async {
      final values = await countStream(5).toList();
      expect(values.length, equals(5));
      expect(values.last, equals(5));
    });

    test('completes after last value', () {
      final stream = countStream(2);
      expectLater(stream, emitsInOrder([1, 2, emitsDone]));
    });
  });
}
```

### Example 4: TDD workflow example

```dart
import 'package:test/test.dart';

// Step 1: Write failing test (RED)
void main() {
  group('EmailValidator', () {
    test('validates correct email', () {
      expect(EmailValidator.isValid('user@example.com'), isTrue);
    });

    test('rejects email without @', () {
      expect(EmailValidator.isValid('userexample.com'), isFalse);
    });

    test('rejects email without domain', () {
      expect(EmailValidator.isValid('user@'), isFalse);
    });
  });
}

// Step 2: Implement minimal code (GREEN)
class EmailValidator {
  static bool isValid(String email) {
    if (!email.contains('@')) return false;
    final parts = email.split('@');
    if (parts.length != 2) return false;
    if (parts[1].isEmpty) return false;
    return true;
  }
}

// Step 3: Refactor (improve while keeping tests green)
class EmailValidatorRefactored {
  static final _emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');

  static bool isValid(String email) {
    return _emailRegex.hasMatch(email);
  }
}
```

## ⚠️ Common Pitfalls

- **Not running `build_runner` after changing mocks**: Mockito uses code generation. Run `dart run build_runner build` after adding `@GenerateMocks`.
- **Testing implementation details**: Test behavior, not implementation. Don't test private methods or internal state.
- **Slow tests**: Unit tests should run in milliseconds. If a test is slow, it's probably an integration test (use mocks to speed it up).
- **Flaky tests**: Tests that pass/fail randomly are worse than no tests. Avoid time-dependent logic, random values, and external dependencies.
- **Not using `setUp` and `tearDown`**: Duplicating initialization code across tests makes them brittle. Use `setUp` for common setup.

## ❓ Interview Questions

### Q1: What is the difference between unit tests, widget tests, and integration tests?
**Answer**: Unit tests verify individual functions, methods, or classes in isolation. They're fast (milliseconds), use mocks for dependencies, and run with `dart test`. Widget tests verify UI behavior by rendering widgets and simulating user interactions. They're slower (seconds) but faster than integration tests, and run with `flutter test`. Integration tests verify the entire app running on a device or emulator, including backend integration. They're slowest (minutes) and most brittle. The testing pyramid recommends many unit tests, some widget tests, and few integration tests.

### Q2: How does `package:mockito` work and when should you use it?
**Answer**: Mockito uses code generation to create mock implementations of interfaces. You annotate a test file with `@GenerateMocks([ClassName])`, run `build_runner`, and Mockito generates a `MockClassName` class. You use `when()` to stub method behavior and `verify()` to assert method calls. Use mocks to test in isolation — replace databases, HTTP clients, and other dependencies with mocks so tests are fast, repeatable, and don't depend on external systems. Mocks also let you test error cases (network failures, invalid data) that are hard to reproduce with real dependencies.

### Q3: What is test-driven development (TDD) and what are its benefits?
**Answer**: TDD is a workflow where you write tests before implementation: (1) Red — write a failing test for the next feature. (2) Green — write minimal code to make the test pass. (3) Refactor — improve the code while keeping tests green. Benefits: forces you to think about API design before implementation, ensures every feature has tests, provides fast feedback on correctness, and makes refactoring safer. TDD is especially useful for complex logic (parsers, algorithms, business rules) where requirements are clear upfront.

### Q4: How do you test async code in Dart?
**Answer**: Use `async` and `await` in tests just like regular code. For `Future`s, mark the test `async` and `await` the result. For `Stream`s, use `expectLater` with matchers like `emitsInOrder`, `emits`, and `emitsDone`. For example, `expectLater(stream, emitsInOrder([1, 2, 3]))` asserts the stream emits 1, then 2, then 3. You can also convert streams to lists with `await stream.toList()` and assert on the list. Always test both success and error cases (use `throwsA` for exceptions).

### Q5: What makes a good unit test?
**Answer**: A good unit test is: (1) Fast — runs in milliseconds. (2) Isolated — no dependencies on databases, networks, or file systems (use mocks). (3) Repeatable — same result every time (no random values, no time-dependent logic). (4) Self-validating — passes or fails automatically (no manual inspection). (5) Focused — tests one thing (one assertion per test is ideal). (6) Readable — clear test name, arrange-act-assert structure. (7) Maintainable — tests behavior, not implementation details. Good tests give you confidence to refactor and catch regressions early.

### Q6: How do you organize tests with `group`, `setUp`, and `tearDown`?
**Answer**: Use `group()` to organize related tests into logical sections (e.g., one group per class or feature). Use `setUp()` to run code before each test in a group (e.g., create a fresh instance of the class under test). Use `tearDown()` to run cleanup after each test (e.g., close database connections, cancel subscriptions). Use `setUpAll()` and `tearDownAll()` for expensive setup that runs once per group (e.g., loading a large file). This reduces duplication, makes tests more maintainable, and ensures tests don't interfere with each other.

## 🔑 Key Takeaways
- `package:test` provides `test()`, `group()`, `expect()`, `setUp()`, `tearDown()`
- Unit tests are fast, isolated, repeatable, and self-validating
- Use `package:mockito` with code generation to mock dependencies
- TDD workflow: Red (failing test) → Green (minimal code) → Refactor
- Test async code with `async`/`await` and `expectLater` for streams
- Good tests focus on behavior, not implementation details
- Testing pyramid: many unit tests, some widget tests, few integration tests

## 🔗 Related Topics
- [Day 24: Design Patterns](./Day-24-Design-Patterns.md) — Repository pattern for testable code
- [Day 15: Async Fundamentals](../Week-3-Async-Advanced/Day-15-Async-Fundamentals.md) — `Future`, `async/await`
- [Day 16: Streams](../Week-3-Async-Advanced/Day-16-Streams.md) — testing streams
- [JavaScript Testing](../../JavaScript/30-Day-JS-Mastery/Week-4-Interview-Prep/Day-27-Testing.md) — cross-language comparison
