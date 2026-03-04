# 🧠 Flutter Interview Questions & Answers

Complete guide to ace your Flutter interviews at any level.

## Table of Contents
- [Beginner Level (0-1 year)](#beginner-level)
- [Intermediate Level (1-2 years)](#intermediate-level)
- [Advanced Level (2-4 years)](#advanced-level)
- [Senior/Architect Level (4+ years)](#seniorarchitect-level)

---

## Beginner Level

### 1. What is Flutter?

**Answer:**
Flutter is an open-source UI framework developed by Google for building natively compiled applications for mobile, web, and desktop from a single codebase. It uses Dart programming language and provides:
- Hot reload for fast development
- Rich widget library
- Native performance
- Expressive and flexible UI

### 2. Difference between Stateless and Stateful widgets?

**Answer:**

**StatelessWidget:**
- Immutable (doesn't change)
- No internal state
- Rebuilds only when parent rebuilds
- Example: Text, Icon, Image

```dart
class MyStatelessWidget extends StatelessWidget {
  final String title;
  
  const MyStatelessWidget({required this.title});
  
  @override
  Widget build(BuildContext context) {
    return Text(title);
  }
}
```

**StatefulWidget:**
- Mutable (can change over time)
- Has internal state
- Can rebuild itself using `setState()`
- Example: Checkbox, TextField, Counter

```dart
class MyStatefulWidget extends StatefulWidget {
  @override
  _MyStatefulWidgetState createState() => _MyStatefulWidgetState();
}

class _MyStatefulWidgetState extends State<MyStatefulWidget> {
  int counter = 0;
  
  @override
  Widget build(BuildContext context) {
    return Text('$counter');
  }
}
```

### 3. What is Hot Reload?

**Answer:**
Hot reload is a feature that:
- Injects updated source code into the running Dart VM
- Rebuilds the widget tree
- Preserves app state
- Happens in <1 second
- Works with stateful widgets

**Hot Reload vs Hot Restart:**
- Hot Reload: Preserves state
- Hot Restart: Resets state and restarts app

### 4. What is BuildContext?

**Answer:**
BuildContext is a handle to the location of a widget in the widget tree. It's actually the Element object itself.

**Uses:**
```dart
// 1. Access theme
Theme.of(context).primaryColor

// 2. Get screen size
MediaQuery.of(context).size.width

// 3. Navigate
Navigator.of(context).push(...)

// 4. Show snackbar
ScaffoldMessenger.of(context).showSnackBar(...)

// 5. Access InheritedWidget
Provider.of<MyModel>(context)
```

### 5. What is the Widget Tree?

**Answer:**
The widget tree is a hierarchical structure of widgets that describes your UI. Flutter uses three trees:

1. **Widget Tree** (Configuration)
   - Immutable
   - Describes what UI should look like
   - Cheap to create

2. **Element Tree** (Lifecycle)
   - Mutable
   - Manages widget lifecycle
   - Links widget to RenderObject

3. **RenderObject Tree** (Rendering)
   - Handles layout, painting
   - Expensive to create
   - Cached and reused

```
Widget Tree        Element Tree         RenderObject Tree
  Container    →    Element          →    RenderBox
    └─Text      →    └─Element       →      └─RenderParagraph
```

### 6. Explain Null Safety in Dart

**Answer:**
Null safety prevents null reference errors at compile time.

```dart
// Nullable type
String? name; // Can be null
name = null; // OK

// Non-nullable type
String title; // Cannot be null
// title = null; // Error!

// Operators
String? nullableStr;

// Null-aware operator
String result = nullableStr ?? 'default';

// Null-assertion operator (use carefully!)
String certain = nullableStr!; // Throws if null

// Null-aware access
int? length = nullableStr?.length;

// Late initialization
late String description;
description = 'Initialized later';
```

### 7. What is async and await?

**Answer:**
`async` and `await` make asynchronous code easier to read and write.

```dart
// Future - represents eventual completion/failure
Future<String> fetchData() async {
  await Future.delayed(Duration(seconds: 2));
  return 'Data loaded';
}

// Using await
void loadData() async {
  print('Loading...');
  String data = await fetchData(); // Waits here
  print(data);
}

// Error handling
Future<void> fetchUser() async {
  try {
    final user = await getUserFromAPI();
    print(user);
  } catch (e) {
    print('Error: $e');
  } finally {
    print('Done');
  }
}
```

### 8. Difference between Future and Stream?

**Answer:**

**Future:**
- Single async value
- Completes once
- Use `async/await`

```dart
Future<int> getNumber() async {
  await Future.delayed(Duration(seconds: 1));
  return 42;
}

void main() async {
  int num = await getNumber();
  print(num); // 42
}
```

**Stream:**
- Multiple async values over time
- Can emit many values
- Use `async*` and `yield`

```dart
Stream<int> countStream() async* {
  for (int i = 1; i <= 5; i++) {
    await Future.delayed(Duration(seconds: 1));
    yield i; // Emit value
  }
}

void main() async {
  await for (int num in countStream()) {
    print(num); // 1, 2, 3, 4, 5
  }
}
```

### 9. Difference between Row and Column?

**Answer:**

**Row** - Horizontal layout (main axis is horizontal)
```dart
Row(
  mainAxisAlignment: MainAxisAlignment.spaceAround,
  crossAxisAlignment: CrossAxisAlignment.center,
  children: [
    Text('A'),
    Text('B'),
    Text('C'),
  ],
)
```

**Column** - Vertical layout (main axis is vertical)
```dart
Column(
  mainAxisAlignment: MainAxisAlignment.center,
  crossAxisAlignment: CrossAxisAlignment.start,
  children: [
    Text('A'),
    Text('B'),
    Text('C'),
  ],
)
```

**Main Axis:** Direction of Row/Column
**Cross Axis:** Perpendicular to main axis

### 10. What is the purpose of `const` keyword?

**Answer:**
`const` creates compile-time constants, improving performance:

```dart
// Creates new widget every build
Widget build(BuildContext context) {
  return Container(
    child: Text('Hello'),
  );
}

// Reuses same widget (better performance)
Widget build(BuildContext context) {
  return const Container(
    child: Text('Hello'),
  );
}

// Flutter doesn't rebuild const widgets
// They're cached and reused
```

**Benefits:**
- Reduced memory usage
- Faster rebuilds
- Better performance

---

## Intermediate Level

### 11. Explain the Flutter rendering pipeline

**Answer:**
Flutter rendering happens in these stages:

```
1. Widget → Configuration
2. Element → Lifecycle management
3. RenderObject → Layout & Paint
4. Layer → Compositing
5. Engine → Skia draws to screen
```

**Detailed Flow:**
```dart
// 1. Build Phase
Widget build() → Creates widget tree

// 2. Layout Phase
performLayout() → Calculates sizes and positions
Constraints go down (parent to child)
Sizes go up (child to parent)

// 3. Paint Phase
paint() → Draws to canvas

// 4. Composite Phase
Layer tree → Sent to engine

// 5. Raster Phase
Skia → Renders to GPU
```

**Frame Budget:** 16.67ms for 60fps, 8.33ms for 120fps

### 12. What causes unnecessary rebuilds and how to avoid them?

**Answer:**

**Causes:**
```dart
// 1. setState rebuilds entire widget
class MyWidget extends StatefulWidget {
  @override
  _MyWidgetState createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget> {
  int counter = 0;
  
  @override
  Widget build(BuildContext context) {
    // This rebuilds EVERYTHING when counter changes
    return Column(
      children: [
        ExpensiveWidget(), // Rebuilds unnecessarily!
        Text('$counter'),
      ],
    );
  }
}
```

**Solutions:**

**1. Extract StatefulWidget:**
```dart
class MyWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ExpensiveWidget(), // Not rebuilt
        CounterWidget(), // Only this rebuilds
      ],
    );
  }
}

class CounterWidget extends StatefulWidget {
  // setState only rebuilds this widget
}
```

**2. Use const constructors:**
```dart
const ExpensiveWidget(), // Never rebuilt
```

**3. Use ValueListenableBuilder:**
```dart
final counter = ValueNotifier<int>(0);

ValueListenableBuilder<int>(
  valueListenable: counter,
  builder: (context, value, child) {
    return Text('$value'); // Only this rebuilds
  },
)
```

**4. Use Selector with Provider:**
```dart
Selector<MyModel, int>(
  selector: (context, model) => model.count,
  builder: (context, count, child) {
    return Text('$count'); // Only rebuilds when count changes
  },
)
```

### 13. Why is setState not scalable?

**Answer:**

**Problems with setState:**

```dart
class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  // ❌ Issues:
  // 1. State scattered across many widgets
  int counter = 0;
  String username = '';
  bool isLoggedIn = false;
  List<Product> cart = [];
  
  // 2. Hard to share state
  // Need to pass through widget tree via constructors
  
  // 3. Business logic mixed with UI
  void addToCart(Product product) {
    setState(() {
      cart.add(product);
      // Complex logic here...
    });
  }
  
  // 4. Testing is difficult
  // Can't test business logic separately
  
  @override
  Widget build(BuildContext context) {
    // Everything rebuilds on any setState
  }
}
```

**Better Solution - Use Provider/Bloc:**
```dart
// Separate model
class CartModel extends ChangeNotifier {
  List<Product> _cart = [];
  
  List<Product> get items => [..._cart];
  
  void addProduct(Product product) {
    _cart.add(product);
    notifyListeners();
  }
}

// UI
class MyWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Consumer<CartModel>(
      builder: (context, cart, child) {
        return Text('${cart.items.length}');
      },
    );
  }
}
```

### 14. Compare Provider, Bloc, Riverpod

**Answer:**

### **Provider**
**Pros:**
- Simple to learn
- Good for small to medium apps
- Built on InheritedWidget
- Good documentation

**Cons:**
- Can get messy in large apps
- BuildContext dependency

```dart
// Setup
ChangeNotifierProvider(
  create: (context) => Counter(),
  child: MyApp(),
)

// Use
Consumer<Counter>(
  builder: (context, counter, child) {
    return Text('${counter.value}');
  },
)
```

### **Bloc (Business Logic Component)**
**Pros:**
- Clear separation of concerns
- Testable
- Predictable state changes
- Great for large apps
- Stream-based

**Cons:**
- Steeper learning curve
- More boilerplate code
- Overkill for simple apps

```dart
// Event
class IncrementEvent extends CounterEvent {}

// State
class CounterState {
  final int count;
  CounterState(this.count);
}

// Bloc
class CounterBloc extends Bloc<CounterEvent, CounterState> {
  CounterBloc() : super(CounterState(0)) {
    on<IncrementEvent>((event, emit) {
      emit(CounterState(state.count + 1));
    });
  }
}

// UI
BlocBuilder<CounterBloc, CounterState>(
  builder: (context, state) {
    return Text('${state.count}');
  },
)
```

### **Riverpod**
**Pros:**
- No BuildContext needed
- Compile-time safety
- Easier testing
- Better than Provider
- Can use anywhere

**Cons:**
- Different from Provider
- Newer (less resources)

```dart
// Provider
final counterProvider = StateProvider<int>((ref) => 0);

// UI
Consumer(
  builder: (context, ref, child) {
    final count = ref.watch(counterProvider);
    return Text('$count');
  },
)

// Anywhere (no BuildContext!)
ref.read(counterProvider.notifier).state++;
```

**When to use:**
- **Provider:** Small to medium apps, simple state
- **Bloc:** Large apps, complex business logic, team development
- **Riverpod:** Modern alternative to Provider, any app size

### 15. Explain Clean Architecture in Flutter

**Answer:**

Clean Architecture separates concerns into layers:

```
┌─────────────────────────────┐
│   Presentation Layer        │  ← UI (Widgets, Pages)
│   - Widgets                 │
│   - Pages                   │
│   - Bloc/Provider           │
├─────────────────────────────┤
│   Domain Layer              │  ← Business Logic
│   - Entities                │
│   - Use Cases               │
│   - Repository Interface    │
├─────────────────────────────┤
│   Data Layer                │  ← Data Sources
│   - Repository Impl         │
│   - Data Sources (API/DB)   │
│   - Models                  │
└─────────────────────────────┘
```

**Example:**

```dart
// DOMAIN LAYER
// Entity
class User {
  final String id;
  final String name;
  final String email;
  
  User({required this.id, required this.name, required this.email});
}

// Repository Interface
abstract class UserRepository {
  Future<User> getUser(String id);
  Future<void> saveUser(User user);
}

// Use Case
class GetUser {
  final UserRepository repository;
  
  GetUser(this.repository);
  
  Future<User> call(String id) {
    return repository.getUser(id);
  }
}

// DATA LAYER
// Model (extends Entity)
class UserModel extends User {
  UserModel({
    required String id,
    required String name,
    required String email,
  }) : super(id: id, name: name, email: email);
  
  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'],
      name: json['name'],
      email: json['email'],
    );
  }
  
  Map<String, dynamic> toJson() {
    return {'id': id, 'name': name, 'email': email};
  }
}

// Data Source
class UserRemoteDataSource {
  Future<UserModel> getUser(String id) async {
    final response = await http.get('/users/$id');
    return UserModel.fromJson(json.decode(response.body));
  }
}

// Repository Implementation
class UserRepositoryImpl implements UserRepository {
  final UserRemoteDataSource remoteDataSource;
  
  UserRepositoryImpl(this.remoteDataSource);
  
  @override
  Future<User> getUser(String id) async {
    return await remoteDataSource.getUser(id);
  }
  
  @override
  Future<void> saveUser(User user) async {
    // Implementation
  }
}

// PRESENTATION LAYER
// State
class UserState {}
class UserLoading extends UserState {}
class UserLoaded extends UserState {
  final User user;
  UserLoaded(this.user);
}
class UserError extends UserState {
  final String message;
  UserError(this.message);
}

// Bloc
class UserBloc extends Bloc<UserEvent, UserState> {
  final GetUser getUser;
  
  UserBloc({required this.getUser}) : super(UserState()) {
    on<LoadUser>((event, emit) async {
      emit(UserLoading());
      try {
        final user = await getUser(event.userId);
        emit(UserLoaded(user));
      } catch (e) {
        emit(UserError(e.toString()));
      }
    });
  }
}

// Widget
class UserPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return BlocBuilder<UserBloc, UserState>(
      builder: (context, state) {
        if (state is UserLoading) {
          return CircularProgressIndicator();
        } else if (state is UserLoaded) {
          return Text(state.user.name);
        } else if (state is UserError) {
          return Text(state.message);
        }
        return Container();
      },
    );
  }
}

// Dependency Injection
final getIt = GetIt.instance;

void setupDependencies() {
  // Data
  getIt.registerLazySingleton(() => UserRemoteDataSource());
  getIt.registerLazySingleton<UserRepository>(
    () => UserRepositoryImpl(getIt()),
  );
  
  // Domain
  getIt.registerLazySingleton(() => GetUser(getIt()));
  
  // Presentation
  getIt.registerFactory(() => UserBloc(getUser: getIt()));
}
```

**Benefits:**
- Testable (can test each layer independently)
- Maintainable (clear separation)
- Scalable (easy to add features)
- Independent of frameworks
- Independent of UI
- Independent of database

### 16. How does ListView.builder work?

**Answer:**

**Regular ListView:**
```dart
// ❌ Creates ALL widgets at once
ListView(
  children: List.generate(10000, (i) => ListTile(title: Text('Item $i'))),
)
// Memory: High (10000 widgets in memory)
```

**ListView.builder:**
```dart
// ✅ Creates widgets on-demand (lazy loading)
ListView.builder(
  itemCount: 10000,
  itemBuilder: (context, index) {
    print('Building item $index'); // Only called for visible items
    return ListTile(title: Text('Item $index'));
  },
)
// Memory: Low (only visible widgets + few extras)
```

**How it works:**
1. Calculates visible viewport
2. Builds only visible items + buffer
3. Recycles widgets as you scroll
4. Much better performance for large lists

**When to use:**
- **ListView.builder:** Dynamic lists, large data
- **ListView:** Small, known number of items
- **ListView.separated:** Lists with dividers
- **ListView.custom:** Custom scrolling behavior

### 17. Explain Keys in Flutter

**Answer:**

Keys help Flutter identify which widgets have changed, been added, or removed.

**Types of Keys:**

**1. ValueKey - Based on value**
```dart
ValueKey<int>(item.id)
// Use when item has unique value
```

**2. ObjectKey - Based on object**
```dart
ObjectKey(item)
// Use when objects are unique
```

**3. UniqueKey - Always unique**
```dart
UniqueKey()
// Generates unique key each time
```

**4. GlobalKey - Access widget state**
```dart
final key = GlobalKey<FormState>();
Form(key: key)
// Later: key.currentState?.validate()
```

**When keys are needed:**

**Without Key (BUG!):**
```dart
class Item extends StatefulWidget {
  final String title;
  Item(this.title);
  
  @override
  _ItemState createState() => _ItemState();
}

class _ItemState extends State<Item> {
  bool checked = false;
  
  @override
  Widget build(BuildContext context) {
    return CheckboxListTile(
      title: Text(widget.title),
      value: checked,
      onChanged: (val) => setState(() => checked = val!),
    );
  }
}

List<Item> items = [
  Item('Item 1'),
  Item('Item 2'),
  Item('Item 3'),
];

// If you remove first item:
items.removeAt(0);
// Bug: Wrong checkboxes stay checked!
```

**With Key (FIXED!):**
```dart
List<Item> items = [
  Item('Item 1', key: ValueKey('1')),
  Item('Item 2', key: ValueKey('2')),
  Item('Item 3', key: ValueKey('3')),
];

// Now Flutter correctly identifies widgets
items.removeAt(0);
// Works correctly!
```

**Rule:** Use keys when reordering/adding/removing stateful widgets

---

## Advanced Level

### 18. Explain event loop in Dart

**Answer:**

Dart is single-threaded with an event loop:

```
┌─────────────────┐
│  Call Stack     │  ← Synchronous code
└─────────────────┘
         ↓
┌─────────────────┐
│ Microtask Queue │  ← scheduleMicrotask, Future.microtask
└─────────────────┘
         ↓
┌─────────────────┐
│  Event Queue    │  ← Future, Timer, I/O
└─────────────────┘
```

**Execution Order:**
```dart
void main() {
  print('1. Sync'); // First
  
  Future(() => print('4. Future')); // Event queue
  
  scheduleMicrotask(() => print('3. Microtask')); // Microtask queue
  
  print('2. Sync'); // Second
  
  // Output:
  // 1. Sync
  // 2. Sync
  // 3. Microtask   ← Microtasks run before event queue
  // 4. Future
}
```

**Detailed Example:**
```dart
void main() async {
  print('A'); // 1st (sync)
  
  Future(() => print('B')); // 5th (event queue)
  
  Future.microtask(() => print('C')); // 3rd (microtask queue)
  
  scheduleMicrotask(() => print('D')); // 4th (microtask queue)
  
  print('E'); // 2nd (sync)
  
  await Future(() => print('F')); // 6th (event queue, awaited)
  
  print('G'); // 7th (sync after await)
  
  // Output: A, E, C, D, B, F, G
}
```

**Priority:**
1. Synchronous code (Call Stack)
2. Microtasks (High priority)
3. Events (Lower priority)

**Interview Tip:** Microtasks have higher priority than Futures!

### 19. What is isolate in Dart?

**Answer:**

Isolates are Dart's version of threads, but with isolated memory:

**Key Points:**
- Dart is single-threaded per isolate
- Isolates don't share memory
- Communication via message passing (SendPort/ReceivePort)
- Used for CPU-intensive tasks

**Example:**
```dart
import 'dart:isolate';

// Expensive computation
int fibonacci(int n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

// Run in isolate
Future<int> computeInIsolate(int n) async {
  final receivePort = ReceivePort();
  
  await Isolate.spawn(_isolateEntry, receivePort.sendPort);
  
  final sendPort = await receivePort.first as SendPort;
  
  final responsePort = ReceivePort();
  sendPort.send([n, responsePort.sendPort]);
  
  return await responsePort.first as int;
}

void _isolateEntry(SendPort sendPort) {
  final port = ReceivePort();
  sendPort.send(port.sendPort);
  
  port.listen((message) {
    final n = message[0] as int;
    final replyPort = message[1] as SendPort;
    
    final result = fibonacci(n);
    replyPort.send(result);
  });
}

// Flutter's compute() simplifies this:
Future<int> computeFibonacci(int n) {
  return compute(fibonacci, n);
}

// Usage
void main() async {
  print('Start');
  final result = await computeFibonacci(40);
  print('Result: $result');
  print('Done');
  
  // UI stays responsive while computing!
}
```

**When to use:**
- JSON parsing (large data)
- Image processing
- Encryption/Decryption
- Complex calculations

**Don't use for:**
- Simple operations (overhead not worth it)
- Operations needing UI access

### 20. How to reduce frame drops?

**Answer:**

**1. Use const constructors:**
```dart
const Text('Hello') // Cached, never rebuilt
```

**2. Use ListView.builder for long lists:**
```dart
ListView.builder( // Lazy loading
  itemCount: items.length,
  itemBuilder: (context, index) => ItemWidget(items[index]),
)
```

**3. Avoid expensive operations in build():**
```dart
// ❌ Bad
@override
Widget build(BuildContext context) {
  final data = expensiveComputation(); // Runs every build!
  return Text(data);
}

// ✅ Good
@override
void initState() {
  super.initState();
  _data = expensiveComputation(); // Runs once
}

@override
Widget build(BuildContext context) {
  return Text(_data);
}
```

**4. Use RepaintBoundary:**
```dart
// Prevents child from repainting when parent repaints
RepaintBoundary(
  child: ComplexWidget(), // Cached
)
```

**5. Optimize image loading:**
```dart
// Resize images
Image.network(
  url,
  cacheWidth: 400, // Don't load full resolution
  cacheHeight: 300,
)

// Use cached_network_image
CachedNetworkImage(
  imageUrl: url,
  placeholder: (context, url) => CircularProgressIndicator(),
)
```

**6. Profile with DevTools:**
```bash
flutter run --profile
# Open DevTools
# Check Performance tab
# Look for janky frames (>16ms)
```

**7. Use Selector instead of Consumer:**
```dart
// Rebuilds only when count changes
Selector<Model, int>(
  selector: (context, model) => model.count,
  builder: (context, count, child) => Text('$count'),
)
```

**8. Avoid Opacity widget:**
```dart
// ❌ Expensive
Opacity(opacity: 0.5, child: Widget())

// ✅ Better
Container(
  color: Colors.black.withOpacity(0.5),
  child: Widget(),
)
```

### 21. How does Flutter handle memory leaks?

**Answer:**

**Common Causes:**

**1. Not disposing controllers:**
```dart
// ❌ Memory leak
class MyWidget extends StatefulWidget {
  @override
  _MyWidgetState createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget> {
  final TextEditingController _controller = TextEditingController();
  
  @override
  Widget build(BuildContext context) {
    return TextField(controller: _controller);
  }
  // Missing dispose()! Memory leak!
}

// ✅ Fixed
class _MyWidgetState extends State<MyWidget> {
  final TextEditingController _controller = TextEditingController();
  
  @override
  void dispose() {
    _controller.dispose(); // Clean up
    super.dispose();
  }
  
  @override
  Widget build(BuildContext context) {
    return TextField(controller: _controller);
  }
}
```

**2. Not cancelling streams:**
```dart
// ❌ Memory leak
class _MyWidgetState extends State<MyWidget> {
  StreamSubscription? _subscription;
  
  @override
  void initState() {
    super.initState();
    _subscription = stream.listen((data) {
      // Handle data
    });
  }
  // Missing cancel()! Memory leak!
}

// ✅ Fixed
@override
void dispose() {
  _subscription?.cancel(); // Cancel subscription
  super.dispose();
}
```

**3. Not removing listeners:**
```dart
// ❌ Memory leak
class _MyWidgetState extends State<MyWidget> {
  @override
  void initState() {
    super.initState();
    someNotifier.addListener(_listener);
  }
  
  void _listener() { }
  // Missing removeListener()!
}

// ✅ Fixed
@override
void dispose() {
  someNotifier.removeListener(_listener);
  super.dispose();
}
```

**Debug memory leaks:**
```dart
// Use DevTools Memory tab
// 1. Take snapshot
// 2. Perform action
// 3. Take another snapshot
// 4. Compare - look for growing objects

// Also check for:
// - Dispose not called
// - Streams not cancelled
// - Timers not cancelled
// - AnimationControllers not disposed
```

---

## Senior/Architect Level

### 22. How would you structure a large-scale Flutter app?

**Answer:**

**Feature-based architecture:**

```
lib/
├── core/
│   ├── constants/
│   ├── themes/
│   ├── utils/
│   ├── error/
│   └── network/
├── features/
│   ├── authentication/
│   │   ├── data/
│   │   │   ├── datasources/
│   │   │   ├── models/
│   │   │   └── repositories/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   ├── repositories/
│   │   │   └── usecases/
│   │   └── presentation/
│   │       ├── bloc/
│   │       ├── pages/
│   │       └── widgets/
│   ├── home/
│   │   ├── data/
│   │   ├── domain/
│   │   └── presentation/
│   └── profile/
│       ├── data/
│       ├── domain/
│       └── presentation/
└── main.dart
```

**Key Principles:**
1. **Clean Architecture** - Separation of concerns
2. **Feature Modules** - Independent, reusable
3. **Dependency Injection** - get_it or injectable
4. **Code Generation** - freezed, json_serializable
5. **Testing** - Unit, widget, integration tests
6. **CI/CD** - Automated builds and deployment
7. **Error Handling** - Centralized error management
8. **Logging** - Structured logging (logger package)

### 23. How would you handle multiple environments?

**Answer:**

**1. Flavor-based approach:**

```dart
// Define flavors
enum Flavor { dev, staging, production }

class FlavorConfig {
  final Flavor flavor;
  final String apiUrl;
  final String appName;
  
  static FlavorConfig? _instance;
  
  FlavorConfig({
    required this.flavor,
    required this.apiUrl,
    required this.appName,
  });
  
  static FlavorConfig get instance => _instance!;
  
  static void initialize({
    required Flavor flavor,
    required String apiUrl,
    required String appName,
  }) {
    _instance = FlavorConfig(
      flavor: flavor,
      apiUrl: apiUrl,
      appName: appName,
    );
  }
}

// main_dev.dart
void main() {
  FlavorConfig.initialize(
    flavor: Flavor.dev,
    apiUrl: 'https://dev-api.example.com',
    appName: 'MyApp DEV',
  );
  runApp(MyApp());
}

// main_prod.dart
void main() {
  FlavorConfig.initialize(
    flavor: Flavor.production,
    apiUrl: 'https://api.example.com',
    appName: 'MyApp',
  );
  runApp(MyApp());
}

// Usage
final apiUrl = FlavorConfig.instance.apiUrl;
```

**2. Build commands:**
```bash
# Android
flutter build apk --flavor dev -t lib/main_dev.dart
flutter build apk --flavor prod -t lib/main_prod.dart

# iOS
flutter build ios --flavor dev -t lib/main_dev.dart
flutter build ios --flavor prod -t lib/main_prod.dart
```

**3. Native configuration:**

**Android** (android/app/build.gradle):
```gradle
flavorDimensions "app"
productFlavors {
    dev {
        dimension "app"
        applicationIdSuffix ".dev"
        resValue "string", "app_name", "MyApp DEV"
    }
    prod {
        dimension "app"
        resValue "string", "app_name", "MyApp"
    }
}
```

**iOS** (Create schemes in Xcode for each flavor)

### 24. How would you handle offline-first architecture?

**Answer:**

```dart
// Repository pattern with cache
class UserRepository {
  final RemoteDataSource remoteDataSource;
  final LocalDataSource localDataSource;
  final NetworkInfo networkInfo;
  
  UserRepository({
    required this.remoteDataSource,
    required this.localDataSource,
    required this.networkInfo,
  });
  
  Future<User> getUser(String id) async {
    if (await networkInfo.isConnected) {
      try {
        // Fetch from API
        final user = await remoteDataSource.getUser(id);
        // Cache locally
        await localDataSource.cacheUser(user);
        return user;
      } catch (e) {
        // Fallback to cache
        return await localDataSource.getUser(id);
      }
    } else {
      // No internet, use cache
      return await localDataSource.getUser(id);
    }
  }
  
  Future<void> saveUser(User user) async {
    // Save locally first
    await localDataSource.saveUser(user);
    
    if (await networkInfo.isConnected) {
      // Sync with server
      try {
        await remoteDataSource.saveUser(user);
      } catch (e) {
        // Queue for later sync
        await localDataSource.queueForSync(user);
      }
    } else {
      // Queue for later sync
      await localDataSource.queueForSync(user);
    }
  }
  
  // Sync queued items when online
  Future<void> syncPendingChanges() async {
    if (!await networkInfo.isConnected) return;
    
    final pendingItems = await localDataSource.getPendingSync();
    for (final item in pendingItems) {
      try {
        await remoteDataSource.saveUser(item);
        await localDataSource.removefromSyncQueue(item);
      } catch (e) {
        // Handle sync error
      }
    }
  }
}

// Network info
class NetworkInfo {
  final Connectivity connectivity;
  
  Future<bool> get isConnected async {
    final result = await connectivity.checkConnectivity();
    return result != ConnectivityResult.none;
  }
}
```

### 25. How to reduce app size?

**Answer:**

**1. Enable code shrinking:**
```gradle
// android/app/build.gradle
buildTypes {
    release {
        shrinkResources true
        minifyEnabled true
    }
}
```

**2. Use app bundles:**
```bash
flutter build appbundle # Android (reduces size by 50%+)
```

**3. Remove unused resources:**
```dart
// Use --split-debug-info and --obfuscate
flutter build apk --release \
  --split-debug-info=build/app/outputs/symbols \
  --obfuscate
```

**4. Optimize images:**
```yaml
# Use WebP format
# Compress images before adding
# Use vector graphics (SVG) when possible
```

**5. Lazy load features:**
```dart
// Deferred imports
import 'package:big_feature/big_feature.dart' deferred as big_feature;

// Load when needed
await big_feature.loadLibrary();
big_feature.showFeature();
```

**6. Analyze size:**
```bash
flutter build apk --analyze-size
# Shows what's taking space
```

---

## 📌 Key Interview Tips

1. **Understand fundamentals deeply** - Don't just memorize
2. **Practice coding** - Build real projects
3. **Explain clearly** - Use diagrams when possible
4. **Know trade-offs** - Every solution has pros/cons
5. **Ask clarifying questions** - Show you think before coding
6. **Test your code** - Mention testing approach
7. **Performance matters** - Always consider optimization
8. **Stay updated** - Follow Flutter updates

---

## 🎯 Common Follow-up Questions

**"How would you implement [feature]?"**
- Ask about requirements
- Discuss architecture
- Mention state management
- Consider error handling
- Think about testing

**"What's the best way to..."**
- There's rarely ONE best way
- Discuss trade-offs
- Mention alternatives
- Consider app size/complexity

**"Have you used [package/pattern]?"**
- Be honest if you haven't
- Show willingness to learn
- Relate to similar experience
- Mention quick learning ability

---

## 📚 Resources for Deep Dive

- [Official Flutter Docs](https://flutter.dev/docs)
- [Dart Language Tour](https://dart.dev/guides/language/language-tour)
- [Flutter Architecture Samples](https://github.com/brianegan/flutter_architecture_samples)
- [Riverpod Documentation](https://riverpod.dev)
- [Bloc Library](https://bloclibrary.dev)

---

**Good luck with your interviews! 🚀**
