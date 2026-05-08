# Day 19: Metaprogramming

## 🎯 What You'll Learn
- What metaprogramming is and why it's useful in Dart
- Creating and using custom annotations
- Overview of `dart:mirrors` for runtime reflection
- Code generation with `build_runner` and `source_gen`
- The `@pragma` annotation for compiler hints
- When to use metaprogramming vs alternatives
- Performance and tree-shaking implications

## 📚 Core Concepts

**Metaprogramming** is writing code that manipulates or generates other code. In Dart, metaprogramming takes three main forms: **annotations** (metadata attached to declarations), **reflection** (inspecting and modifying code at runtime), and **code generation** (creating source files at build time). Each approach has different trade-offs in terms of performance, tree-shaking, and complexity.

### Annotations

Annotations are metadata attached to classes, methods, fields, or parameters using the `@` syntax. Dart has built-in annotations like `@override`, `@deprecated`, and `@pragma`, but you can also define custom annotations. Annotations themselves don't do anything — they're markers that tools, frameworks, or reflection code can read and act upon.

```dart
class MyAnnotation {
  final String description;
  const MyAnnotation(this.description);
}

@MyAnnotation('This is a special class')
class MyClass {}
```

Annotations must be compile-time constants. They're commonly used for:
- Marking code for code generators (e.g., `@JsonSerializable()` in `json_serializable`)
- Providing hints to the compiler (e.g., `@pragma('vm:entry-point')`)
- Documenting intent (e.g., `@visibleForTesting`)

### dart:mirrors — Runtime Reflection

The `dart:mirrors` library provides runtime reflection — the ability to inspect and invoke code dynamically. You can list a class's methods, read field values, call functions by name, and more. However, `dart:mirrors` has significant downsides:

- **Not supported in Flutter or web**: Reflection breaks tree-shaking and increases bundle size, so it's disabled in production Flutter and dart2js.
- **Performance overhead**: Reflection is slow compared to direct calls.
- **Breaks static analysis**: The compiler can't optimize or verify reflected code.

For these reasons, `dart:mirrors` is rarely used in modern Dart. It's mainly for server-side tools, test frameworks, or legacy code.

```dart
import 'dart:mirrors';

void main() {
  final mirror = reflectClass(MyClass);
  print(mirror.declarations.keys); // List of method/field names
}
```

### Code Generation with build_runner

The modern approach to metaprogramming in Dart is **code generation** at build time. Tools like `build_runner` and `source_gen` read your source code, find annotations, and generate new `.g.dart` files with boilerplate code. This approach:

- Works in Flutter and web (generated code is normal Dart)
- Has zero runtime overhead (generated code is compiled like any other code)
- Preserves tree-shaking and static analysis
- Requires a build step (`dart run build_runner build`)

Popular packages like `json_serializable`, `freezed`, and `retrofit` use code generation. You annotate your classes, run the generator, and it creates serialization, immutability, or API client code for you.

### How Code Generation Works

1. You write a class with an annotation: `@JsonSerializable() class User { ... }`
2. You run `dart run build_runner build`
3. A generator reads your source code using the `analyzer` package
4. The generator finds classes with `@JsonSerializable()`
5. The generator writes a `user.g.dart` file with `_$UserFromJson` and `_$UserToJson` functions
6. You import the generated file and use the functions

This pattern eliminates boilerplate while keeping the benefits of static typing and tree-shaking.

### @pragma Annotation

The `@pragma` annotation provides hints to the Dart compiler and VM. It's used for low-level optimizations and interop with native code. Common pragmas:

- `@pragma('vm:entry-point')` — prevents tree-shaking of a function/class used by native code
- `@pragma('vm:prefer-inline')` — suggests inlining a function
- `@pragma('dart2js:noInline')` — prevents inlining in dart2js
- `@pragma('vm:external-name', 'nativeName')` — maps a Dart function to a native symbol

Most developers never use `@pragma` directly — it's for framework authors and performance-critical code.

### When to Use Metaprogramming

Use metaprogramming when:
- You have repetitive boilerplate that follows a pattern (serialization, routing, dependency injection)
- You need to enforce conventions across a large codebase (linting, code generation)
- You're building a framework or library that needs to inspect user code

Avoid metaprogramming when:
- Simple functions or classes would suffice
- The complexity of the metaprogramming tooling exceeds the complexity of the problem
- You need runtime flexibility (consider dependency injection or strategy patterns instead)

### Alternatives to Metaprogramming

Before reaching for metaprogramming, consider:
- **Generics and higher-order functions** for reusable logic
- **Mixins and extension methods** for adding behavior to existing types
- **Dependency injection** for runtime flexibility without reflection
- **Code snippets and templates** for one-time boilerplate

Metaprogramming is powerful but adds complexity. Use it when the benefits clearly outweigh the costs.


## 💻 Code Examples

### Example 1: Custom annotations

```dart
// Define a custom annotation class
class Route {
  final String path;
  final String method;

  const Route(this.path, {this.method = 'GET'});
}

class Deprecated {
  final String message;
  const Deprecated(this.message);
}

// Use annotations on classes and methods
@Route('/api/users')
class UserController {
  @Route('/api/users/:id', method: 'GET')
  String getUser(String id) => 'User $id';

  @Route('/api/users', method: 'POST')
  @Deprecated('Use createUserV2 instead')
  String createUser(String name) => 'Created $name';
}

void main() {
  // Annotations are metadata — they don't execute code by themselves
  // Tools or reflection code can read them at build time or runtime
  final controller = UserController();
  print(controller.getUser('123')); // User 123
}
```

### Example 2: dart:mirrors reflection (server-side only)

```dart
import 'dart:mirrors';

class Person {
  String name;
  int age;

  Person(this.name, this.age);

  void greet() => print('Hello, I am $name');
}

void main() {
  final person = Person('Alice', 30);

  // Reflect on the instance
  final instanceMirror = reflect(person);

  // Get class mirror
  final classMirror = instanceMirror.type;

  print('Class name: ${MirrorSystem.getName(classMirror.simpleName)}');
  // Class name: Person

  // List all instance members
  print('Methods and fields:');
  classMirror.declarations.forEach((symbol, declaration) {
    print('  ${MirrorSystem.getName(symbol)}');
  });
  // Output includes: name, age, greet, etc.

  // Invoke method by name
  instanceMirror.invoke(Symbol('greet'), []);
  // Hello, I am Alice

  // Get field value
  final nameMirror = instanceMirror.getField(Symbol('name'));
  print('Name via reflection: ${nameMirror.reflectee}');
  // Name via reflection: Alice

  // Set field value
  instanceMirror.setField(Symbol('age'), 31);
  print('New age: ${person.age}'); // New age: 31
}

// NOTE: This code only works in Dart VM (server-side).
// It will NOT work in Flutter or dart2js (web).
```

### Example 3: Code generation setup (conceptual)

```dart
// 1. Define an annotation in your package
class JsonSerializable {
  const JsonSerializable();
}

// 2. Annotate your model class
@JsonSerializable()
class User {
  final String name;
  final int age;

  User(this.name, this.age);

  // Reference generated code (created by build_runner)
  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}

// 3. Run: dart run build_runner build
// This generates user.g.dart with _$UserFromJson and _$UserToJson

// 4. Import the generated file
// part 'user.g.dart';

void main() {
  final json = {'name': 'Alice', 'age': 30};
  final user = User.fromJson(json);
  print('${user.name} is ${user.age}'); // Alice is 30

  final backToJson = user.toJson();
  print(backToJson); // {name: Alice, age: 30}
}

// NOTE: This is a simplified example. Real code generation requires:
// - Adding build_runner and source_gen to dev_dependencies
// - Writing a generator class that extends GeneratorForAnnotation
// - Configuring build.yaml
```

### Example 4: @pragma for compiler hints

```dart
// Prevent tree-shaking for a function called from native code
@pragma('vm:entry-point')
void callableFromNative() {
  print('Called from native code');
}

// Suggest inlining for performance
@pragma('vm:prefer-inline')
int add(int a, int b) => a + b;

// Prevent inlining in dart2js
@pragma('dart2js:noInline')
void debugLog(String message) {
  print('[DEBUG] $message');
}

// Map Dart function to native symbol (used with dart:ffi)
@pragma('vm:external-name', 'native_compute')
external int compute(int x);

void main() {
  // These pragmas affect compilation, not runtime behavior
  print(add(2, 3)); // 5
  debugLog('Application started');
}
```

### Example 5: Annotation-based validation (conceptual)

```dart
// Custom annotations for validation
class Required {
  const Required();
}

class MinLength {
  final int length;
  const MinLength(this.length);
}

class Email {
  const Email();
}

// Annotated model
class UserForm {
  @Required()
  @MinLength(3)
  String? username;

  @Required()
  @Email()
  String? email;

  @MinLength(8)
  String? password;

  UserForm({this.username, this.email, this.password});
}

// Validation logic (would use reflection or code generation in real code)
List<String> validate(UserForm form) {
  final errors = <String>[];

  // In real code, this would use reflection or generated code
  // to read annotations and validate fields automatically

  if (form.username == null || form.username!.isEmpty) {
    errors.add('Username is required');
  } else if (form.username!.length < 3) {
    errors.add('Username must be at least 3 characters');
  }

  if (form.email == null || form.email!.isEmpty) {
    errors.add('Email is required');
  } else if (!form.email!.contains('@')) {
    errors.add('Email must be valid');
  }

  if (form.password != null && form.password!.length < 8) {
    errors.add('Password must be at least 8 characters');
  }

  return errors;
}

void main() {
  final form = UserForm(username: 'ab', email: 'invalid', password: '123');
  final errors = validate(form);

  if (errors.isNotEmpty) {
    print('Validation errors:');
    errors.forEach(print);
  }
}
// Output:
// Validation errors:
// Username must be at least 3 characters
// Email must be valid
// Password must be at least 8 characters
```

## ⚠️ Common Pitfalls

- **Using dart:mirrors in Flutter**: Reflection doesn't work in Flutter or dart2js because it breaks tree-shaking. Always use code generation instead for production code.
- **Forgetting to run build_runner**: After changing annotated classes, you must run `dart run build_runner build` to regenerate code. Forgetting this causes "undefined name" errors.
- **Overusing metaprogramming**: Metaprogramming adds complexity and build-time overhead. Use it only when the boilerplate reduction justifies the cost.
- **Non-const annotations**: Annotations must be compile-time constants. Using `new` or non-const constructors in annotations causes compile errors.
- **Ignoring generated files**: Generated `.g.dart` files should be committed to version control (for libraries) or gitignored (for apps). Check your package's conventions.
- **Circular dependencies in generators**: If your generator depends on generated code from another generator, you may hit circular dependency issues. Structure your code to avoid this.

## ❓ Interview Questions

### Q1: What is metaprogramming and what are the main approaches in Dart?
**Answer**: Metaprogramming is writing code that manipulates or generates other code. Dart supports three main approaches: annotations (metadata attached to declarations), runtime reflection with `dart:mirrors` (inspecting code at runtime), and code generation with `build_runner` (creating source files at build time). Annotations are lightweight markers; reflection is powerful but breaks tree-shaking and doesn't work in Flutter; code generation is the modern approach that works everywhere and has zero runtime overhead.

### Q2: Why is dart:mirrors not recommended for Flutter applications?
**Answer**: `dart:mirrors` provides runtime reflection, which breaks tree-shaking — the process of removing unused code from the final bundle. Reflection requires keeping all code and metadata in the binary, dramatically increasing app size. Flutter and dart2js disable `dart:mirrors` for this reason. Additionally, reflection has performance overhead and prevents static analysis optimizations. The modern alternative is code generation with `build_runner`, which generates normal Dart code at build time and preserves all optimizations.

### Q3: How does code generation with build_runner work?
**Answer**: Code generation reads your source code at build time, finds annotated classes, and generates new `.g.dart` files with boilerplate code. The process: you annotate a class (e.g., `@JsonSerializable()`), run `dart run build_runner build`, a generator uses the `analyzer` package to parse your code, finds the annotation, generates helper functions, and writes them to a `.g.dart` file. You import the generated file and use the functions. This approach works in Flutter and web, has zero runtime overhead, and preserves tree-shaking.

### Q4: What is the @pragma annotation used for?
**Answer**: `@pragma` provides low-level hints to the Dart compiler and VM for optimizations and native interop. Common uses: `@pragma('vm:entry-point')` prevents tree-shaking of code called from native, `@pragma('vm:prefer-inline')` suggests inlining for performance, `@pragma('dart2js:noInline')` prevents inlining in web compilation, and `@pragma('vm:external-name')` maps Dart functions to native symbols for FFI. Most developers never use `@pragma` directly — it's for framework authors and performance-critical code.

### Q5: When should you use metaprogramming instead of regular code?
**Answer**: Use metaprogramming when you have repetitive boilerplate that follows a clear pattern (like JSON serialization, routing, or dependency injection), when you need to enforce conventions across a large codebase, or when building a framework that inspects user code. Avoid it when simple functions or classes suffice, when the tooling complexity exceeds the problem complexity, or when you need runtime flexibility (use dependency injection or strategy patterns instead). Metaprogramming adds build-time complexity, so use it only when the benefits clearly outweigh the costs.

### Q6: What are the trade-offs between annotations and code generation?
**Answer**: Annotations are simple metadata markers that have zero runtime cost and work everywhere, but they don't do anything by themselves — you need tools or reflection to read them. Code generation reads annotations at build time and generates actual code, eliminating boilerplate while preserving performance and tree-shaking. The trade-off is that code generation requires a build step (`build_runner`), adds generated files to your project, and increases build time. Use annotations alone for documentation or linting; use code generation when you need to eliminate significant boilerplate.

### Q7: How do you create a custom annotation in Dart?
**Answer**: Define a class with a const constructor — that's it. The class can have fields to store metadata. For example: `class Route { final String path; const Route(this.path); }`. Then use it with `@Route('/api/users')` on classes or methods. Annotations must be compile-time constants, so all fields must be final and the constructor must be const. The annotation itself doesn't execute code — it's metadata that tools, generators, or reflection code can read and act upon.

### Q8: What are the performance implications of using dart:mirrors?
**Answer**: `dart:mirrors` has significant performance overhead because reflection is inherently slow — looking up methods by name, invoking them dynamically, and accessing fields through mirrors is much slower than direct calls. More critically, reflection breaks tree-shaking, forcing the compiler to keep all code and metadata in the binary, dramatically increasing app size. It also prevents many compiler optimizations like inlining and devirtualization. For these reasons, `dart:mirrors` is disabled in Flutter and dart2js. Use code generation instead for production code.



## 🔑 Key Takeaways
- Metaprogramming in Dart uses annotations, runtime reflection, or code generation
- Annotations are compile-time constant metadata markers attached to declarations
- `dart:mirrors` provides runtime reflection but doesn't work in Flutter or web
- Code generation with `build_runner` is the modern approach — works everywhere with zero runtime cost
- `@pragma` provides compiler hints for optimizations and native interop
- Use metaprogramming only when boilerplate reduction justifies the added complexity
- Always prefer code generation over reflection for production code

## 🔗 Related Topics
- [Day 08: Classes and Constructors](../Week-2-OOP-Collections/Day-08-Classes-Constructors.md) — const constructors for annotations
- [Day 20: FFI](./Day-20-FFI.md) — `@pragma` for native interop
- [Day 26: Testing in Dart](../Week-4-Flutter-Dart-Interview/Day-26-Testing-in-Dart.md) — `@visibleForTesting` annotation
- [Day 27: Tooling and Ecosystem](../Week-4-Flutter-Dart-Interview/Day-27-Tooling-Ecosystem.md) — `build_runner` workflow
- [JavaScript Decorators](../../JavaScript/30-Day-JS-Mastery/Week-3-Advanced/Day-18-Design-Patterns.md) — similar annotation concept
