# 🚀 30-Day Flutter Quick Reference Guide

Complete summary of all topics with code examples for rapid revision.

---

## 📅 Week 1: Foundations

### Day 1-2: Dart Basics
```dart
// Variables
String name = 'Flutter';
int? nullableInt;
late String lateInit;
final constant = 'compile time';
const pi = 3.14;

// Functions
String greet(String name, {int? age}) => 'Hello $name';

// Classes with OOP
class Person {
  String name;
  Person(this.name);
  void speak() => print('Hi, $name');
}

// Async/Await
Future<String> fetchData() async {
  await Future.delayed(Duration(seconds: 1));
  return 'Data';
}

// Streams
Stream<int> counter() async* {
  for (int i = 0; i < 5; i++) {
    await Future.delayed(Duration(seconds: 1));
    yield i;
  }
}

// Event Loop Order: Sync → Microtasks → Event Queue
```

### Day 3-4: Architecture
```dart
// Widget → Element → RenderObject

// StatelessWidget (Immutable)
class MyWidget extends StatelessWidget {
  @override
  Widget build(BuildContext context) => Text('Hello');
}

// StatefulWidget (Mutable)
class Counter extends StatefulWidget {
  @override
  _CounterState createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  int count = 0;
  
  @override
  void initState() { super.initState(); }
  
  @override
  Widget build(BuildContext context) {
    return Text('$count');
  }
  
  @override
  void dispose() { super.dispose(); }
}

// BuildContext - handle to widget location
Theme.of(context)
MediaQuery.of(context).size
Navigator.of(context).push(...)
```

### Day 5-6: Layouts
```dart
// Container
Container(
  width: 100,
  height: 100,
  padding: EdgeInsets.all(16),
  margin: EdgeInsets.symmetric(horizontal: 20, vertical: 10),
  decoration: BoxDecoration(
    color: Colors.blue,
    borderRadius: BorderRadius.circular(10),
    boxShadow: [BoxShadow(color: Colors.black26, blurRadius: 5)],
  ),
  child: Text('Box'),
)

// Row/Column
Row(
  mainAxisAlignment: MainAxisAlignment.spaceBetween,
  crossAxisAlignment: CrossAxisAlignment.center,
  children: [Widget1(), Widget2()],
)

// Stack (Overlapping)
Stack(
  children: [
    Container(color: Colors.blue),
    Positioned(top: 10, left: 10, child: Text('Overlay')),
  ],
)

// Expanded/Flexible
Row(
  children: [
    Expanded(flex: 2, child: Container(color: Colors.red)),
    Expanded(flex: 1, child: Container(color: Colors.blue)),
  ],
)

// Responsive
final size = MediaQuery.of(context).size;
Container(width: size.width * 0.8) // 80% of screen
```

### Day 7: Navigation
```dart
// Push
Navigator.push(
  context,
  MaterialPageRoute(builder: (context) => SecondScreen()),
);

// Pop
Navigator.pop(context);

// Named Routes
MaterialApp(
  routes: {
    '/': (context) => HomeScreen(),
    '/details': (context) => DetailsScreen(),
  },
);

Navigator.pushNamed(context, '/details');

// Pass Data
Navigator.pushNamed(
  context,
  '/details',
  arguments: {'id': '123', 'name': 'Flutter'},
);

// Return Data
final result = await Navigator.push(...);

// Replace
Navigator.pushReplacement(context, MaterialPageRoute(...));

// Clear Stack
Navigator.pushAndRemoveUntil(
  context,
  MaterialPageRoute(builder: (context) => HomeScreen()),
  (route) => false,
);
```

---

## 📅 Week 2: Intermediate

### Day 8-9: State Management
```dart
// setState
setState(() { counter++; });

// InheritedWidget
class MyData extends InheritedWidget {
  final int data;
  
  MyData({required this.data, required Widget child}) : super(child: child);
  
  static MyData? of(BuildContext context) {
    return context.dependOnInheritedWidgetOfExactType<MyData>();
  }
  
  @override
  bool updateShouldNotify(MyData old) => data != old.data;
}

// Provider
class Counter with ChangeNotifier {
  int _count = 0;
  int get count => _count;
  
  void increment() {
    _count++;
    notifyListeners();
  }
}

// Setup
ChangeNotifierProvider(
  create: (context) => Counter(),
  child: MyApp(),
)

// Usage
Consumer<Counter>(
  builder: (context, counter, child) => Text('${counter.count}'),
)

context.read<Counter>().increment(); // No rebuild
context.watch<Counter>().count; // Rebuilds on change

// Selector (Optimized)
Selector<Model, int>(
  selector: (context, model) => model.count,
  builder: (context, count, child) => Text('$count'),
)
```

### Day 10-11: Forms
```dart
// Form with Validation
final _formKey = GlobalKey<FormState>();

Form(
  key: _formKey,
  child: Column(
    children: [
      TextFormField(
        decoration: InputDecoration(labelText: 'Email'),
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Please enter email';
          }
          if (!value.contains('@')) {
            return 'Invalid email';
          }
          return null;
        },
      ),
      ElevatedButton(
        onPressed: () {
          if (_formKey.currentState!.validate()) {
            // Process data
          }
        },
        child: Text('Submit'),
      ),
    ],
  ),
)

// TextEditingController
final controller = TextEditingController();

TextField(controller: controller)

// Get value
String text = controller.text;

// Dispose
@override
void dispose() {
  controller.dispose();
  super.dispose();
}

// FocusNode
final focusNode = FocusNode();

TextField(focusNode: focusNode)
focusNode.requestFocus(); // Focus field
```

### Day 12-13: Networking
```dart
// HTTP GET
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<List<User>> fetchUsers() async {
  final response = await http.get(
    Uri.parse('https://api.example.com/users'),
  );
  
  if (response.statusCode == 200) {
    final List data = json.decode(response.body);
    return data.map((json) => User.fromJson(json)).toList();
  } else {
    throw Exception('Failed to load');
  }
}

// POST
Future<User> createUser(String name) async {
  final response = await http.post(
    Uri.parse('https://api.example.com/users'),
    headers: {'Content-Type': 'application/json'},
    body: json.encode({'name': name}),
  );
  
  return User.fromJson(json.decode(response.body));
}

// Model
class User {
  final int id;
  final String name;
  
  User({required this.id, required this.name});
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(id: json['id'], name: json['name']);
  }
  
  Map<String, dynamic> toJson() {
    return {'id': id, 'name': name};
  }
}

// FutureBuilder
FutureBuilder<List<User>>(
  future: fetchUsers(),
  builder: (context, snapshot) {
    if (snapshot.connectionState == ConnectionState.waiting) {
      return CircularProgressIndicator();
    } else if (snapshot.hasError) {
      return Text('Error: ${snapshot.error}');
    } else if (snapshot.hasData) {
      return ListView.builder(
        itemCount: snapshot.data!.length,
        itemBuilder: (context, index) {
          return ListTile(title: Text(snapshot.data![index].name));
        },
      );
    }
    return Container();
  },
)

// StreamBuilder
StreamBuilder<User>(
  stream: userStream,
  builder: (context, snapshot) {
    if (snapshot.hasData) {
      return Text(snapshot.data!.name);
    }
    return CircularProgressIndicator();
  },
)
```

### Day 14: Local Storage
```dart
// SharedPreferences (Key-Value)
import 'package:shared_preferences/shared_preferences.dart';

// Save
final prefs = await SharedPreferences.getInstance();
await prefs.setString('name', 'Flutter');
await prefs.setInt('age', 5);
await prefs.setBool('isLoggedIn', true);

// Read
String? name = prefs.getString('name');
int? age = prefs.getInt('age');
bool? isLoggedIn = prefs.getBool('isLoggedIn');

// Delete
await prefs.remove('name');
await prefs.clear(); // Clear all

// SQLite (Structured Data)
import 'package:sqflite/sqflite.dart';

final database = openDatabase(
  'my_database.db',
  version: 1,
  onCreate: (db, version) {
    return db.execute(
      'CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, age INTEGER)',
    );
  },
);

// Insert
await db.insert('users', {'name': 'John', 'age': 25});

// Query
List<Map<String, dynamic>> users = await db.query('users');

// Update
await db.update('users', {'age': 26}, where: 'id = ?', whereArgs: [1]);

// Delete
await db.delete('users', where: 'id = ?', whereArgs: [1]);

// Hive (NoSQL)
import 'package:hive/hive.dart';

// Initialize
await Hive.initFlutter();

// Open box
var box = await Hive.openBox('myBox');

// Save
box.put('name', 'Flutter');

// Read
String name = box.get('name');

// Delete
box.delete('name');

// Close
await box.close();
```

---

## 📅 Week 3: Advanced Concepts

### Day 15-16: Advanced State Management

**Bloc Pattern:**
```dart
// Event
abstract class CounterEvent {}
class Increment extends CounterEvent {}
class Decrement extends CounterEvent {}

// State
class CounterState {
  final int count;
  CounterState(this.count);
}

// Bloc
class CounterBloc extends Bloc<CounterEvent, CounterState> {
  CounterBloc() : super(CounterState(0)) {
    on<Increment>((event, emit) {
      emit(CounterState(state.count + 1));
    });
    
    on<Decrement>((event, emit) {
      emit(CounterState(state.count - 1));
    });
  }
}

// UI
BlocProvider(
  create: (context) => CounterBloc(),
  child: MyApp(),
)

BlocBuilder<CounterBloc, CounterState>(
  builder: (context, state) {
    return Text('${state.count}');
  },
)

context.read<CounterBloc>().add(Increment());
```

**Riverpod:**
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

// Update
ref.read(counterProvider.notifier).state++;

// No BuildContext needed!
```

**GetX:**
```dart
// Controller
class CounterController extends GetxController {
  var count = 0.obs; // Observable
  
  void increment() => count++;
}

// UI
final CounterController c = Get.put(CounterController());

Obx(() => Text('${c.count}'));

// Navigation
Get.to(NextScreen());
Get.back();
Get.snackbar('Title', 'Message');
```

### Day 17-18: Clean Architecture
```
Presentation (UI) → Domain (Business Logic) → Data (Sources)

Features/
  ├── data/
  │   ├── datasources/ (API, DB)
  │   ├── models/
  │   └── repositories/
  ├── domain/
  │   ├── entities/
  │   ├── repositories/ (interfaces)
  │   └── usecases/
  └── presentation/
      ├── bloc/
      ├── pages/
      └── widgets/

Dependency Injection with get_it:

final getIt = GetIt.instance;

getIt.registerLazySingleton<ApiClient>(() => ApiClient());
getIt.registerFactory<UserRepository>(() => UserRepositoryImpl(getIt()));

Usage:
final repo = getIt<UserRepository>();
```

### Day 19: Animations
```dart
// Implicit Animations (Easy)
AnimatedContainer(
  duration: Duration(milliseconds: 300),
  width: _width,
  height: _height,
  color: _color,
)

AnimatedOpacity(
  duration: Duration(milliseconds: 500),
  opacity: _visible ? 1.0 : 0.0,
  child: Text('Fade'),
)

// Explicit Animations (Control)
class MyWidget extends StatefulWidget {
  @override
  _MyWidgetState createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;
  
  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: Duration(seconds: 2),
      vsync: this,
    );
    
    _animation = Tween<double>(begin: 0, end: 300).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }
  
  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _animation,
      builder: (context, child) {
        return Container(
          width: _animation.value,
          height: _animation.value,
          color: Colors.blue,
        );
      },
    );
  }
  
  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

// Hero Animation
Hero(
  tag: 'imageHero',
  child: Image.network(url),
)

// On next screen with same tag, auto animation!
```

### Day 20: Performance
```dart
// 1. const constructors
const Text('Static text')

// 2. ListView.builder
ListView.builder(itemBuilder: ...)

// 3. RepaintBoundary
RepaintBoundary(child: ExpensiveWidget())

// 4. Avoid build() operations
@override
void initState() {
  _data = expensiveOp(); // Once
  super.initState();
}

// 5. Image optimization
Image.network(url, cacheWidth: 400)

// 6. Profile
flutter run --profile

// 7. DevTools
// Check for janky frames (>16ms)

// 8. Selector over Consumer
Selector<Model, int>(...)
```

### Day 21: Platform Integration
```dart
// Platform Channels
const platform = MethodChannel('com.example/channel');

// Call native method
try {
  final result = await platform.invokeMethod('getBatteryLevel');
  print('Battery: $result%');
} catch (e) {
  print('Error: $e');
}

// Android (Kotlin)
// MainActivity.kt
MethodChannel(flutterEngine.dartExecutor, "com.example/channel")
  .setMethodCallHandler { call, result ->
    if (call.method == "getBatteryLevel") {
      val batteryLevel = getBatteryLevel()
      result.success(batteryLevel)
    }
  }

// iOS (Swift)  
// AppDelegate.swift
let channel = FlutterMethodChannel(
  name: "com.example/channel",
  binaryMessenger: controller.binaryMessenger
)
channel.setMethodCallHandler { (call, result) in
  if call.method == "getBatteryLevel" {
    let batteryLevel = self.getBatteryLevel()
    result(batteryLevel)
  }
}

// Permissions
import 'package:permission_handler/permission_handler.dart';

if (await Permission.camera.request().isGranted) {
  // Camera access granted
}
```

---

## 📅 Week 4: Production Skills

### Day 22: Testing
```dart
// Unit Test
test('Counter increments', () {
  final counter = Counter();
  counter.increment();
  expect(counter.value, 1);
});

// Widget Test
testWidgets('Button increments counter', (tester) async {
  await tester.pumpWidget(MyApp());
  
  expect(find.text('0'), findsOneWidget);
  
  await tester.tap(find.byIcon(Icons.add));
  await tester.pump();
  
  expect(find.text('1'), findsOneWidget);
});

// Mock
class MockUserRepository extends Mock implements UserRepository {}

test('Fetch user', () async {
  final repo = MockUserRepository();
  when(repo.getUser('1')).thenAnswer((_) async => User(id: '1', name: 'Test'));
  
  final user = await repo.getUser('1');
  expect(user.name, 'Test');
});

// Integration Test
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();
  
  testWidgets('Complete flow', (tester) async {
    app.main();
    await tester.pumpAndSettle();
    
    await tester.tap(find.text('Login'));
    await tester.pumpAndSettle();
    
    expect(find.text('Home'), findsOneWidget);
  });
}
```

### Day 23: CI/CD
```yaml
# GitHub Actions (.github/workflows/flutter.yml)
name: Flutter CI

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - uses: subosito/flutter-action@v2
      with:
        flutter-version: '3.x'
    
    - run: flutter pub get
    - run: flutter analyze
    - run: flutter test
    - run: flutter build apk --release
    
    - uses: actions/upload-artifact@v2
      with:
        name: app-release.apk
        path: build/app/outputs/flutter-apk/app-release.apk

# Fastlane (Android)
# android/fastlane/Fastfile
lane :beta do
  gradle(task: "clean assembleRelease")
  upload_to_play_store(
    track: 'beta',
    apk: '../build/app/outputs/apk/release/app-release.apk'
  )
end
```

### Day 24: Firebase
```dart
// Initialize
await Firebase.initializeApp();

// Authentication
final user = await FirebaseAuth.instance.signInWithEmailAndPassword(
  email: 'test@example.com',
  password: 'password',
);

// Firestore
FirebaseFirestore.instance.collection('users').add({
  'name': 'John',
  'age': 25,
});

Stream<QuerySnapshot> users = FirebaseFirestore.instance
    .collection('users')
    .snapshots();

// Push Notifications
FirebaseMessaging.instance.getToken().then((token) {
  print('FCM Token: $token');
});

FirebaseMessaging.onMessage.listen((RemoteMessage message) {
  print('Message: ${message.notification?.title}');
});

// Crashlytics
FirebaseCrashlytics.instance.crash(); // Test crash

try {
  // Code
} catch (e) {
  FirebaseCrashlytics.instance.recordError(e, stackTrace);
}
```

### Day 25: Security
```dart
// Obfuscation
flutter build apk --obfuscate --split-debug-info=build/symbols

// Secure Storage
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final storage = FlutterSecureStorage();

await storage.write(key: 'token', value: 'secret_token');
String? token = await storage.read(key: 'token');

// SSL Pinning
import 'package:http/io_client.dart';

SecurityContext context = SecurityContext.defaultContext;
context.setTrustedCertificatesBytes(certificate);

HttpClient httpClient = HttpClient(context: context);
IOClient ioClient = IOClient(httpClient);

// Encrypt data
import 'package:encrypt/encrypt.dart';

final key = Key.fromLength(32);
final iv = IV.fromLength(16);
final encrypter = Encrypter(AES(key));

final encrypted = encrypter.encrypt('Plain text', iv: iv);
final decrypted = encrypter.decrypt(encrypted, iv: iv);
```

### Day 26-27: Advanced Dart
```dart
// Isolates
import 'dart:isolate';

Future<int> heavyComputation(int n) {
  return compute(fibonacci, n);
}

int fibonacci(int n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

// Extension Methods
extension StringExtension on String {
  String capitalize() {
    return '${this[0].toUpperCase()}${substring(1)}';
  }
}

'flutter'.capitalize(); // Flutter

// Generics
class Stack<T> {
  final List<T> _items = [];
  
  void push(T item) => _items.add(item);
  T pop() => _items.removeLast();
  T get peek => _items.last;
}

// Functional Programming
final numbers = [1, 2, 3, 4, 5];

numbers.map((n) => n * 2); // [2, 4, 6, 8, 10]
numbers.where((n) => n % 2 == 0); // [2, 4]
numbers.reduce((a, b) => a + b); // 15
numbers.fold(0, (sum, n) => sum + n); // 15
```

---

## 🎯 Key Performance Metrics

**60 FPS = 16.67ms per frame**
- Build: < 8ms
- Layout: < 4ms
- Paint: < 4ms

**Memory:**
- Keep under 100MB for average app
- Watch for leaks (dispose controllers!)

**App Size:**
- Target: < 20MB (compressed)
- Use app bundles
- Optimize images

---

## 🔥 Most Important Patterns

```dart
// 1. Singleton
class Database {
  static final Database _instance = Database._internal();
  factory Database() => _instance;
  Database._internal();
}

// 2. Factory
abstract class Shape {
  factory Shape(String type) {
    if (type == 'circle') return Circle();
    if (type == 'square') return Square();
    throw 'Invalid type';
  }
}

// 3. Repository
abstract class UserRepository {
  Future<User> getUser(String id);
}

class UserRepositoryImpl implements UserRepository {
  final RemoteDataSource remote;
  final LocalDataSource local;
  
  @override
  Future<User> getUser(String id) async {
    try {
      return await remote.getUser(id);
    } catch (e) {
      return await local.getUser(id);
    }
  }
}

// 4. Dependency Injection
final getIt = GetIt.instance;

void setup() {
  getIt.registerSingleton<ApiService>(ApiService());
  getIt.registerFactory<UserRepo>(() => UserRepoImpl(getIt()));
}
```

---

## ⚡ Quick Commands

```bash
# Create project
flutter create my_app

# Run
flutter run
flutter run --release
flutter run --profile

# Build
flutter build apk
flutter build ios
flutter build web
flutter build appbundle

# Test
flutter test
flutter test --coverage

# Analyze
flutter analyze

# Format
flutter format .

# Dependencies
flutter pub get
flutter pub upgrade
flutter pub outdated

# Clean
flutter clean

# Doctor
flutter doctor
flutter doctor -v

# DevTools
flutter pub global activate devtools
flutter pub global run devtools
```

---

## 📚 Essential Packages

```yaml
dependencies:
  # State Management
  provider: ^6.0.5
  flutter_bloc: ^8.1.3
  riverpod: ^2.4.0
  
  # Networking
  http: ^1.1.0
  dio: ^5.3.2
  
  # Storage
  shared_preferences: ^2.2.0
  sqflite: ^2.3.0
  hive: ^2.2.3
  
  # Firebase
  firebase_core: ^2.15.1
  firebase_auth: ^4.9.0
  cloud_firestore: ^4.9.1
  
  # UI
  cached_network_image: ^3.2.3
  shimmer: ^3.0.0
  
  # Utils
  get_it: ^7.6.0
  freezed: ^2.4.1
  json_serializable: ^6.7.1
```

---

**Master these concepts and you're production-ready! 🚀**
