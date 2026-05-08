# Day 28: Mock Interview

## 🎯 What You'll Learn
- 10 scenario-based Dart/Flutter interview problems
- Full solutions with Dart 3.x syntax
- Time and space complexity analysis
- Follow-up discussion points for each problem
- Common interview patterns: parsing, state management, async coordination, data structures
- How to approach whiteboard coding in Dart interviews

## 📚 Core Concepts

This day simulates a real Dart/Flutter interview with 10 problems covering the full spectrum of topics from this 4-week plan. Each problem includes:
- A realistic scenario
- A complete solution with annotations
- Complexity analysis
- Follow-up questions an interviewer might ask

Treat this as a practice interview — time yourself (30-45 minutes per problem) and try to solve each before reading the solution.

---

## 💻 Problem 1: Implement a Type-Safe Event Bus

**Scenario**: You're building a Flutter app with multiple screens that need to communicate without tight coupling. Implement a type-safe event bus using Dart's `Stream` and generics.

**Requirements**:
- Support multiple event types
- Type-safe: `on<EventType>()` should only receive events of that type
- Allow multiple listeners per event type
- Provide a way to unsubscribe

**Solution**:

```dart
import 'dart:async';

/// A type-safe event bus using streams and generics.
class EventBus {
  // Map of event types to their stream controllers
  final Map<Type, StreamController<dynamic>> _controllers = {};

  /// Publishes an event of type [T].
  void fire<T>(T event) {
    final controller = _controllers[T];
    if (controller != null) {
      controller.add(event);
    }
  }

  /// Subscribes to events of type [T].
  /// Returns a [StreamSubscription] that must be canceled when done.
  StreamSubscription<T> on<T>(void Function(T event) handler) {
    // Get or create a controller for this event type
    final controller = _controllers.putIfAbsent(
      T,
      () => StreamController<T>.broadcast(),
    ) as StreamController<T>;

    return controller.stream.listen(handler);
  }

  /// Closes all stream controllers.
  void dispose() {
    for (final controller in _controllers.values) {
      controller.close();
    }
    _controllers.clear();
  }
}

// Example usage
class UserLoggedIn {
  final String username;
  UserLoggedIn(this.username);
}

class MessageReceived {
  final String message;
  MessageReceived(this.message);
}

void main() async {
  final bus = EventBus();

  // Subscribe to UserLoggedIn events
  final sub1 = bus.on<UserLoggedIn>((event) {
    print('User logged in: ${event.username}');
  });

  // Subscribe to MessageReceived events
  final sub2 = bus.on<MessageReceived>((event) {
    print('Message: ${event.message}');
  });

  // Fire events
  bus.fire(UserLoggedIn('Alice'));
  bus.fire(MessageReceived('Hello!'));
  bus.fire(UserLoggedIn('Bob'));

  await Future.delayed(const Duration(milliseconds: 100));

  // Cleanup
  sub1.cancel();
  sub2.cancel();
  bus.dispose();
}
```

**Complexity**:
- Time: O(1) for `fire()` and `on()` (hash map lookup)
- Space: O(N) where N is the number of event types

**Follow-up Questions**:
1. How would you prevent memory leaks if listeners forget to unsubscribe?
   - Use weak references or automatic cleanup when widgets dispose
2. How would you add event filtering (e.g., only fire to listeners that match a predicate)?
   - Add a `where()` method that wraps the stream with `stream.where(predicate)`
3. How would you make this work across isolates?
   - Use `SendPort`/`ReceivePort` for inter-isolate communication

---

## 💻 Problem 2: Implement a Retry Mechanism for Async Operations

**Scenario**: You're calling an unreliable API that sometimes fails. Implement a `retry()` function that retries an async operation with exponential backoff.

**Requirements**:
- Retry up to `maxAttempts` times
- Use exponential backoff: wait 1s, 2s, 4s, 8s, etc.
- Rethrow the last exception if all attempts fail

**Solution**:

```dart
import 'dart:async';

/// Retries [operation] up to [maxAttempts] times with exponential backoff.
/// Throws the last exception if all attempts fail.
Future<T> retry<T>(
  Future<T> Function() operation, {
  int maxAttempts = 3,
  Duration initialDelay = const Duration(seconds: 1),
}) async {
  int attempt = 0;
  Duration delay = initialDelay;

  while (true) {
    attempt++;
    try {
      return await operation();
    } catch (e) {
      if (attempt >= maxAttempts) {
        rethrow; // all attempts failed
      }
      print('Attempt $attempt failed: $e. Retrying in ${delay.inSeconds}s...');
      await Future.delayed(delay);
      delay *= 2; // exponential backoff
    }
  }
}

// Example usage
Future<String> unreliableApi() async {
  // Simulate 70% failure rate
  if (DateTime.now().millisecondsSinceEpoch % 10 < 7) {
    throw Exception('API error');
  }
  return 'Success!';
}

void main() async {
  try {
    final result = await retry(
      unreliableApi,
      maxAttempts: 5,
      initialDelay: const Duration(milliseconds: 500),
    );
    print('Result: $result');
  } catch (e) {
    print('All attempts failed: $e');
  }
}
```

**Complexity**:
- Time: O(maxAttempts) in the worst case
- Space: O(1)

**Follow-up Questions**:
1. How would you add jitter to prevent thundering herd?
   - Add random variation: `delay * (0.5 + Random().nextDouble())`
2. How would you make the backoff configurable (linear, exponential, custom)?
   - Accept a `Duration Function(int attempt)` parameter
3. How would you add a timeout per attempt?
   - Wrap `operation()` with `Future.timeout()`

---

## 💻 Problem 3: Implement a Simple JSON Parser

**Scenario**: Implement a minimal JSON parser that converts a JSON string to Dart objects (`Map`, `List`, `String`, `num`, `bool`, `null`).

**Requirements**:
- Support objects, arrays, strings, numbers, booleans, null
- Throw `FormatException` on invalid JSON
- No external dependencies (don't use `dart:convert`)

**Solution** (simplified — production parsers are more complex):

```dart
class JsonParser {
  String _input = '';
  int _pos = 0;

  dynamic parse(String input) {
    _input = input.trim();
    _pos = 0;
    final result = _parseValue();
    _skipWhitespace();
    if (_pos < _input.length) {
      throw FormatException('Unexpected characters after JSON');
    }
    return result;
  }

  dynamic _parseValue() {
    _skipWhitespace();
    if (_pos >= _input.length) throw FormatException('Unexpected end of input');

    final char = _input[_pos];
    if (char == '{') return _parseObject();
    if (char == '[') return _parseArray();
    if (char == '"') return _parseString();
    if (char == 't' || char == 'f') return _parseBoolean();
    if (char == 'n') return _parseNull();
    if (char == '-' || (char.codeUnitAt(0) >= 48 && char.codeUnitAt(0) <= 57)) {
      return _parseNumber();
    }
    throw FormatException('Unexpected character: $char');
  }

  Map<String, dynamic> _parseObject() {
    _expect('{');
    final map = <String, dynamic>{};
    _skipWhitespace();

    if (_peek() == '}') {
      _pos++;
      return map;
    }

    while (true) {
      _skipWhitespace();
      final key = _parseString();
      _skipWhitespace();
      _expect(':');
      final value = _parseValue();
      map[key] = value;

      _skipWhitespace();
      if (_peek() == '}') {
        _pos++;
        break;
      }
      _expect(',');
    }
    return map;
  }

  List<dynamic> _parseArray() {
    _expect('[');
    final list = <dynamic>[];
    _skipWhitespace();

    if (_peek() == ']') {
      _pos++;
      return list;
    }

    while (true) {
      list.add(_parseValue());
      _skipWhitespace();
      if (_peek() == ']') {
        _pos++;
        break;
      }
      _expect(',');
    }
    return list;
  }

  String _parseString() {
    _expect('"');
    final start = _pos;
    while (_pos < _input.length && _input[_pos] != '"') {
      if (_input[_pos] == '\\') _pos++; // skip escaped char
      _pos++;
    }
    final str = _input.substring(start, _pos);
    _expect('"');
    return str;
  }

  num _parseNumber() {
    final start = _pos;
    if (_peek() == '-') _pos++;
    while (_pos < _input.length && '0123456789.'.contains(_input[_pos])) {
      _pos++;
    }
    final str = _input.substring(start, _pos);
    return num.parse(str);
  }

  bool _parseBoolean() {
    if (_input.substring(_pos, _pos + 4) == 'true') {
      _pos += 4;
      return true;
    }
    if (_input.substring(_pos, _pos + 5) == 'false') {
      _pos += 5;
      return false;
    }
    throw FormatException('Invalid boolean');
  }

  Null _parseNull() {
    if (_input.substring(_pos, _pos + 4) == 'null') {
      _pos += 4;
      return null;
    }
    throw FormatException('Invalid null');
  }

  void _expect(String char) {
    if (_pos >= _input.length || _input[_pos] != char) {
      throw FormatException('Expected "$char" at position $_pos');
    }
    _pos++;
  }

  String _peek() => _pos < _input.length ? _input[_pos] : '';

  void _skipWhitespace() {
    while (_pos < _input.length && ' \t\n\r'.contains(_input[_pos])) {
      _pos++;
    }
  }
}

void main() {
  final parser = JsonParser();
  print(parser.parse('{"name": "Alice", "age": 30, "active": true}'));
  print(parser.parse('[1, 2, 3, null, "hello"]'));
}
```

**Complexity**:
- Time: O(N) where N is the length of the input string
- Space: O(D) where D is the depth of nesting (recursion stack)

**Follow-up Questions**:
1. How would you handle escape sequences in strings (`\n`, `\t`, `\"`)?
   - Add a lookup table for escape codes and process them in `_parseString()`
2. How would you improve error messages (show line/column)?
   - Track line and column numbers as you parse
3. How would you make this streaming (parse as data arrives)?
   - Use a state machine instead of recursion

---

## 💻 Problem 4: Implement a Debounce Function

**Scenario**: You have a search box that triggers an API call on every keystroke. Implement a `debounce()` function that delays execution until the user stops typing.

**Requirements**:
- Delay execution by `duration` after the last call
- Cancel previous pending calls when a new call arrives
- Return a function with the same signature as the input

**Solution**:

```dart
import 'dart:async';

/// Returns a debounced version of [function] that delays execution by [duration].
void Function() debounce(void Function() function, Duration duration) {
  Timer? timer;

  return () {
    timer?.cancel(); // cancel previous timer
    timer = Timer(duration, function); // start new timer
  };
}

// Generic version for functions with arguments
void Function(T) debounceGeneric<T>(
  void Function(T) function,
  Duration duration,
) {
  Timer? timer;

  return (T arg) {
    timer?.cancel();
    timer = Timer(duration, () => function(arg));
  };
}

// Example usage
void main() async {
  final search = debounceGeneric<String>(
    (query) => print('Searching for: $query'),
    const Duration(milliseconds: 500),
  );

  // Simulate rapid typing
  search('a');
  await Future.delayed(const Duration(milliseconds: 100));
  search('ap');
  await Future.delayed(const Duration(milliseconds: 100));
  search('app');
  await Future.delayed(const Duration(milliseconds: 100));
  search('appl');
  await Future.delayed(const Duration(milliseconds: 100));
  search('apple');

  // Only the last call executes after 500ms
  await Future.delayed(const Duration(milliseconds: 600));
}
```

**Complexity**:
- Time: O(1) per call
- Space: O(1)

**Follow-up Questions**:
1. How would you implement `throttle()` (execute at most once per interval)?
   - Track the last execution time and skip calls within the interval
2. How would you make this work with async functions?
   - Return `Future<void> Function()` and await the function
3. How would you add a "leading" option (execute immediately on first call)?
   - Check if `timer` is null and execute immediately if so

---

## 💻 Problem 5: Implement a Simple State Machine

**Scenario**: You're building a traffic light controller. Implement a state machine with states `Red`, `Yellow`, `Green` and transitions triggered by a timer.

**Requirements**:
- Define states and transitions
- Trigger transitions automatically after a delay
- Allow external code to observe state changes

**Solution**:

```dart
import 'dart:async';

enum TrafficLightState { red, yellow, green }

class TrafficLight {
  TrafficLightState _state = TrafficLightState.red;
  Timer? _timer;

  final _controller = StreamController<TrafficLightState>.broadcast();
  Stream<TrafficLightState> get stateChanges => _controller.stream;

  TrafficLightState get state => _state;

  void start() {
    _scheduleNextTransition();
  }

  void stop() {
    _timer?.cancel();
  }

  void dispose() {
    stop();
    _controller.close();
  }

  void _scheduleNextTransition() {
    final (nextState, delay) = _getNextStateAndDelay();
    _timer = Timer(delay, () {
      _state = nextState;
      _controller.add(_state);
      print('State changed to: $_state');
      _scheduleNextTransition();
    });
  }

  (TrafficLightState, Duration) _getNextStateAndDelay() {
    return switch (_state) {
      TrafficLightState.red => (TrafficLightState.green, const Duration(seconds: 5)),
      TrafficLightState.green => (TrafficLightState.yellow, const Duration(seconds: 4)),
      TrafficLightState.yellow => (TrafficLightState.red, const Duration(seconds: 1)),
    };
  }
}

void main() async {
  final light = TrafficLight();

  light.stateChanges.listen((state) {
    print('Observer: Light is now $state');
  });

  light.start();

  await Future.delayed(const Duration(seconds: 12));
  light.dispose();
}
```

**Complexity**:
- Time: O(1) per transition
- Space: O(1)

**Follow-up Questions**:
1. How would you add entry/exit actions for each state?
   - Add `onEnter` and `onExit` callbacks to each state
2. How would you make transitions conditional (e.g., skip yellow if emergency)?
   - Add a `bool Function(TrafficLightState)` guard to each transition
3. How would you persist state across app restarts?
   - Save `_state` to `SharedPreferences` and restore in constructor

---

## 💻 Problem 6: Implement a LRU Cache

**Scenario**: Implement a Least Recently Used (LRU) cache with O(1) get and put operations.

**Requirements**:
- `get(key)` returns the value or null if not found
- `put(key, value)` inserts or updates the value
- When capacity is exceeded, evict the least recently used item
- Both operations must be O(1)

**Solution**:

```dart
class LRUCache<K, V> {
  final int capacity;
  final Map<K, _Node<K, V>> _cache = {};
  _Node<K, V>? _head; // most recently used
  _Node<K, V>? _tail; // least recently used

  LRUCache(this.capacity);

  V? get(K key) {
    final node = _cache[key];
    if (node == null) return null;

    // Move to front (most recently used)
    _remove(node);
    _addToFront(node);
    return node.value;
  }

  void put(K key, V value) {
    final existing = _cache[key];
    if (existing != null) {
      // Update existing node
      existing.value = value;
      _remove(existing);
      _addToFront(existing);
    } else {
      // Add new node
      final node = _Node(key, value);
      _cache[key] = node;
      _addToFront(node);

      // Evict LRU if over capacity
      if (_cache.length > capacity) {
        final lru = _tail!;
        _remove(lru);
        _cache.remove(lru.key);
      }
    }
  }

  void _addToFront(_Node<K, V> node) {
    node.next = _head;
    node.prev = null;
    if (_head != null) _head!.prev = node;
    _head = node;
    _tail ??= node;
  }

  void _remove(_Node<K, V> node) {
    if (node.prev != null) {
      node.prev!.next = node.next;
    } else {
      _head = node.next;
    }

    if (node.next != null) {
      node.next!.prev = node.prev;
    } else {
      _tail = node.prev;
    }
  }
}

class _Node<K, V> {
  final K key;
  V value;
  _Node<K, V>? prev;
  _Node<K, V>? next;
  _Node(this.key, this.value);
}

void main() {
  final cache = LRUCache<int, String>(3);
  cache.put(1, 'one');
  cache.put(2, 'two');
  cache.put(3, 'three');
  print(cache.get(1)); // 'one'
  cache.put(4, 'four'); // evicts key 2
  print(cache.get(2)); // null
  print(cache.get(3)); // 'three'
}
```

**Complexity**:
- Time: O(1) for both `get()` and `put()`
- Space: O(capacity)

**Follow-up Questions**:
1. How would you make this thread-safe?
   - Add a `Lock` or use `synchronized` (not built into Dart — use `package:synchronized`)
2. How would you add TTL (time-to-live) for entries?
   - Store expiration time in each node and check it in `get()`
3. How would you implement LFU (Least Frequently Used) instead?
   - Track access count per node and evict the node with the lowest count

---

## 💻 Problem 7-10: Quick-Fire Problems

### Problem 7: Flatten a Nested List

```dart
List<T> flatten<T>(List<dynamic> nested) {
  final result = <T>[];
  for (final item in nested) {
    if (item is List) {
      result.addAll(flatten<T>(item));
    } else {
      result.add(item as T);
    }
  }
  return result;
}

void main() {
  print(flatten<int>([1, [2, [3, 4], 5], 6])); // [1, 2, 3, 4, 5, 6]
}
```

**Complexity**: O(N) time, O(D) space (D = max depth)

---

### Problem 8: Implement `groupBy`

```dart
Map<K, List<T>> groupBy<T, K>(Iterable<T> items, K Function(T) keySelector) {
  final map = <K, List<T>>{};
  for (final item in items) {
    final key = keySelector(item);
    map.putIfAbsent(key, () => []).add(item);
  }
  return map;
}

void main() {
  final words = ['apple', 'banana', 'apricot', 'blueberry'];
  final grouped = groupBy(words, (word) => word[0]);
  print(grouped); // {a: [apple, apricot], b: [banana, blueberry]}
}
```

**Complexity**: O(N) time, O(N) space

---

### Problem 9: Implement `zip`

```dart
List<(T1, T2)> zip<T1, T2>(List<T1> list1, List<T2> list2) {
  final length = list1.length < list2.length ? list1.length : list2.length;
  return List.generate(length, (i) => (list1[i], list2[i]));
}

void main() {
  print(zip([1, 2, 3], ['a', 'b', 'c'])); // [(1, a), (2, b), (3, c)]
}
```

**Complexity**: O(min(N, M)) time and space

---

### Problem 10: Implement `memoize`

```dart
R Function(A) memoize<A, R>(R Function(A) function) {
  final cache = <A, R>{};
  return (A arg) => cache.putIfAbsent(arg, () => function(arg));
}

void main() {
  int fib(int n) => n <= 1 ? n : fib(n - 1) + fib(n - 2);
  final memoizedFib = memoize(fib);

  print(memoizedFib(40)); // Fast due to memoization
}
```

**Complexity**: O(1) time per call (after first), O(N) space

---

## 🔑 Key Takeaways
- Event bus: Use `StreamController.broadcast()` for type-safe pub/sub
- Retry with backoff: Exponential delay prevents overwhelming servers
- JSON parsing: Recursive descent parser with state tracking
- Debounce: Cancel previous timers to delay execution
- State machine: Use enums, switch expressions, and streams for transitions
- LRU cache: Doubly-linked list + hash map for O(1) operations
- Functional utilities: `flatten`, `groupBy`, `zip`, `memoize` are common interview questions

## 🔗 Related Topics
- [Day 16: Streams](../Week-3-Async-Advanced/Day-16-Streams.md) — `StreamController`, `broadcast()`
- [Day 15: Async Fundamentals](../Week-3-Async-Advanced/Day-15-Async-Fundamentals.md) — `Future`, `Timer`
- [Day 11: Generics](../Week-2-OOP-Collections/Day-11-Generics.md) — type-safe collections
- [DS Algorithms](../../DS/Days/Day_01_Complexity_Analysis.md) — time/space complexity
- [DS Mock Interviews](../../DS/Days/Day_29_Mock_Interview_1.md) — more practice problems
