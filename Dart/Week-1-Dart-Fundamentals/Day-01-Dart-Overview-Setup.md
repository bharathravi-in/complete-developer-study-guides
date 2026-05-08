# Day 01: Dart Overview & Setup

## 🎯 What You'll Learn

- What Dart is, its history, and why Google created it
- Dart's core characteristics: strongly typed, null-safe, AOT + JIT compiled, garbage collected
- Where Dart runs: Flutter, web (dart2js), server-side, and CLI
- How to install the Dart SDK and understand its directory layout
- The `dart` CLI and its key sub-commands (`run`, `compile`, `pub`, `analyze`, `format`)
- Using DartPad for instant, browser-based Dart experimentation
- The `main()` function as the mandatory entry point and how to accept command-line arguments
- Dart file structure: imports, top-level declarations, and the `main()` function

---

## 📚 Core Concepts

### What Is Dart?

Dart is a general-purpose, object-oriented programming language developed by Google. It was first unveiled at the GOTO conference in October 2011, with Lars Bak and Kasper Lund as its primary designers. Google created Dart to address perceived shortcomings in JavaScript for large-scale web applications — they wanted a language that was structured, performant, and easy to tool. Over time, Dart's scope expanded well beyond the browser, and today it is best known as the language that powers the Flutter UI framework.

Dart reached a major milestone with Dart 2.0 (2018), which introduced a sound static type system. Dart 2.12 (2021) added sound null safety, eliminating an entire class of null-reference bugs at compile time. Dart 3.0 (2023) built on that foundation with records, patterns, sealed classes, and class modifiers — features that bring Dart closer to modern functional and algebraic type systems.

### Key Characteristics

**Strongly typed with type inference.** Every value in Dart has a type. You can annotate types explicitly (`String name = 'Alice'`) or let the compiler infer them (`var name = 'Alice'`). The `dynamic` type opts out of static checking when you genuinely need it, but idiomatic Dart avoids it.

**Sound null safety.** Since Dart 2.12, the type system distinguishes between nullable (`String?`) and non-nullable (`String`) types. The compiler guarantees that a non-nullable variable can never hold `null` at runtime — no more `NullPointerException` surprises. The `late` keyword defers initialization of a non-nullable variable to its first use, and the `!` operator asserts non-nullability when you know better than the compiler.

**AOT and JIT compilation.** Dart supports two compilation modes. Just-In-Time (JIT) compilation is used during development: the Dart VM compiles code on the fly, enabling hot reload and fast iteration. Ahead-Of-Time (AOT) compilation is used for production: the compiler produces native machine code (or JavaScript for the web), resulting in fast startup times and predictable performance. Flutter uses JIT in debug mode and AOT in release mode.

**Garbage collected.** Dart manages memory automatically. The runtime uses a generational garbage collector, which is efficient for the short-lived objects typical in UI frameworks. You do not manually allocate or free memory (except when using `dart:ffi` to interop with C code).

**Single-threaded with isolates.** Dart code runs in a single thread by default. True parallelism is achieved through isolates — independent workers that share no memory and communicate via message passing. This design eliminates data races without requiring locks.

### Where Dart Runs

- **Flutter**: The primary use case. Dart compiles to native ARM/x64 code for iOS, Android, macOS, Windows, and Linux, and to JavaScript/WebAssembly for the web.
- **Web (dart2js / DDC)**: The `dart compile js` command transpiles Dart to optimized JavaScript. The Dart Development Compiler (DDC) produces modular JS for faster development builds.
- **Server-side / CLI**: Dart runs on the server via the Dart VM. You can build HTTP servers (using `package:shelf`), command-line tools, and scripts. `dart compile exe` produces a self-contained native executable.
- **Embedded / IoT**: Dart's small AOT footprint makes it viable for resource-constrained environments.

### Installing the Dart SDK

Visit [dart.dev/get-dart](https://dart.dev/get-dart) for platform-specific instructions. The recommended approach on macOS is Homebrew (`brew install dart`); on Windows, the Chocolatey package manager (`choco install dart-sdk`); on Linux, the official apt repository.

After installation, the SDK lives in a directory like `/usr/lib/dart` (Linux) or `/opt/homebrew/opt/dart` (macOS). Key subdirectories:

| Directory | Contents |
|-----------|----------|
| `bin/`    | Executables: `dart`, `dartaotruntime`, `dartdoc` |
| `lib/`    | Core libraries: `dart:core`, `dart:async`, `dart:io`, `dart:math`, etc. |
| `include/`| C headers for `dart:ffi` |

Verify your installation: `dart --version` should print something like `Dart SDK version: 3.x.x`.

### The `dart` CLI

The `dart` command is the single entry point for all Dart tooling:

| Sub-command | Purpose |
|-------------|---------|
| `dart run <file.dart>` | Run a Dart program with the JIT VM |
| `dart compile exe <file.dart>` | Compile to a self-contained native executable |
| `dart compile js <file.dart>` | Compile to optimized JavaScript |
| `dart pub get` | Fetch dependencies listed in `pubspec.yaml` |
| `dart pub add <package>` | Add a package dependency |
| `dart analyze` | Run the static analyzer (reports errors and warnings) |
| `dart format <file.dart>` | Auto-format code to the official Dart style |
| `dart fix --apply` | Apply automated code fixes suggested by the analyzer |
| `dart doc` | Generate HTML API documentation |
| `dart test` | Run the test suite (requires `package:test`) |

### DartPad

[DartPad](https://dartpad.dev) is an official, browser-based Dart editor maintained by the Dart team. It requires no installation and supports the full Dart 3.x language, including Flutter widget previews. It is ideal for quickly testing a snippet, sharing a reproducible example, or following along with documentation. DartPad auto-formats code, shows analyzer hints inline, and lets you switch between Dart and Flutter modes.

### The `main()` Function

Every Dart program must have a top-level `main()` function — it is the entry point the runtime calls when the program starts. Two signatures are valid:

```dart
void main() { ... }                        // no command-line arguments
void main(List<String> args) { ... }       // receives CLI arguments as a list
```

`main()` may also return `Future<void>` when the program's top-level logic is asynchronous (covered on Day 15).

### Dart File Structure

A typical Dart source file follows this order:

1. **Library directive** (optional): `library my_library;`
2. **Import directives**: `import 'dart:math';` / `import 'package:http/http.dart';`
3. **Part directives** (optional, for multi-file libraries)
4. **Top-level declarations**: constants, type aliases, functions, classes
5. **`main()` function** (in the entry-point file)

Dart uses `import` (not `require` or `#include`). The `dart:` prefix refers to SDK libraries; `package:` refers to pub packages; a bare path string refers to a local file.

---

## 💻 Code Examples

### Example 1: Minimal "Hello, Dart!" Program

```dart
// Every Dart program starts execution at main().
// void means main() does not return a value.
void main() {
  // print() writes to stdout followed by a newline.
  print('Hello, Dart!');
}
```

**Run it:**
```
dart run hello.dart
# Output: Hello, Dart!
```

This is the smallest valid Dart program. Notice there are no semicolons at the end of the file, no class wrapper required, and no `public static void` boilerplate — `main()` is simply a top-level function.

---

### Example 2: `main()` with Command-Line Arguments

```dart
// List<String> is a typed list of strings — Dart's equivalent of String[] in Java.
void main(List<String> args) {
  // args.isEmpty is true when no arguments are passed.
  if (args.isEmpty) {
    print('Usage: dart run greet.dart <name>');
    return; // exit early
  }

  // args[0] accesses the first argument (zero-indexed).
  final String name = args[0];

  // String interpolation: $variable or ${expression} inside a string literal.
  print('Hello, $name! Welcome to Dart.');
}
```

**Run it:**
```
dart run greet.dart Alice
# Output: Hello, Alice! Welcome to Dart.

dart run greet.dart
# Output: Usage: dart run greet.dart <name>
```

`final` declares a variable that is assigned once and never reassigned. The type annotation `String` is optional here because Dart can infer it from `args[0]`, but explicit annotations improve readability.

---

### Example 3: Imports, Variables, and a Function Call

```dart
// Import the dart:math SDK library to access math constants and functions.
import 'dart:math';

// A top-level constant — SCREAMING_SNAKE_CASE by convention.
// const values are compile-time constants; they cannot change.
const double PI_APPROX = 3.14159;

// A top-level function that computes the area of a circle.
// The return type (double) is declared before the function name.
double circleArea(double radius) {
  // pi is a constant defined in dart:math (more precise than PI_APPROX).
  return pi * radius * radius;
}

void main() {
  // var lets Dart infer the type; radius is inferred as double.
  var radius = 5.0;

  // Call the top-level function and store the result.
  double area = circleArea(radius);

  // toStringAsFixed(2) formats the double to 2 decimal places.
  print('Radius: $radius');
  print('Area: ${area.toStringAsFixed(2)}');

  // sqrt() is also from dart:math — computes the square root.
  print('Square root of area: ${sqrt(area).toStringAsFixed(4)}');
}
```

**Run it:**
```
dart run circle.dart
# Output:
# Radius: 5.0
# Area: 78.54
# Square root of area: 8.8623
```

This example shows the three-part structure of a real Dart file: an import at the top, a top-level declaration (`circleArea`), and `main()` at the bottom. The `dart:math` library is part of the SDK — no `pubspec.yaml` entry needed.

---

## ⚠️ Common Pitfalls

**1. Forgetting that `main()` is mandatory.**
Unlike some scripting languages, Dart will not execute a file that lacks a `main()` function. Running `dart run myfile.dart` on a file without `main()` produces: `Error: No 'main' method found.` Every entry-point file needs one.

**2. Confusing `var`, `final`, and `const`.**
- `var` — type-inferred, reassignable variable.
- `final` — assigned once at runtime; the reference cannot change after first assignment.
- `const` — compile-time constant; the value must be known before the program runs.

A common mistake is using `var` when `final` is more appropriate (making intent unclear) or trying to use `const` with a value computed at runtime (which causes a compile error).

**3. Using `print()` for structured output in production.**
`print()` is fine for learning and debugging, but in production Dart/Flutter code you should use a proper logging package (e.g., `package:logging`) or, in Flutter, `debugPrint()`. `print()` is synchronous and can block the event loop on large outputs.

**4. Assuming Dart files need a class wrapper.**
Developers coming from Java or C# often wrap everything in a class. In Dart, top-level functions, variables, and constants are perfectly idiomatic. `main()` does not need to be inside a class.

**5. Mixing up `dart:` and `package:` imports.**
`dart:core` is automatically imported — you never need to write `import 'dart:core'`. Other SDK libraries (`dart:math`, `dart:io`, `dart:async`) must be imported explicitly. Third-party packages use the `package:` prefix and must be listed in `pubspec.yaml` before importing.

---

## ❓ Interview Questions

### Q1: What is Dart and what are its primary use cases?

**Answer:** Dart is a strongly typed, object-oriented, garbage-collected programming language developed by Google and first released in 2011. Its primary use case today is Flutter — Google's cross-platform UI framework — where Dart compiles to native machine code for mobile, desktop, and web targets. Beyond Flutter, Dart is used for server-side development (HTTP servers, CLI tools) via the Dart VM, and for web applications via the `dart2js` compiler that transpiles Dart to optimized JavaScript. The language's combination of fast development iteration (JIT hot reload) and high-performance production builds (AOT native code) makes it particularly well-suited for UI-heavy applications.

---

### Q2: What is the difference between AOT and JIT compilation in Dart?

**Answer:** Just-In-Time (JIT) compilation compiles Dart code to machine code at runtime, as the program executes. This enables Flutter's hot reload feature — the VM can swap in new code without restarting the app — and produces faster development cycles. However, JIT has a warm-up cost: the first time a code path runs, it must be compiled, which can cause initial latency. Ahead-Of-Time (AOT) compilation happens before the program runs: the `dart compile exe` or Flutter release build pipeline translates Dart to native machine code (or JavaScript) at build time. AOT-compiled programs start faster and have more predictable performance because there is no runtime compilation overhead, but they lose the ability to dynamically load or hot-reload code. Flutter uses JIT in debug mode and AOT in profile/release mode.

---

### Q3: How does Dart's null safety differ from languages like Java or JavaScript?

**Answer:** In Java and JavaScript, any reference type can be `null` by default, and null-reference errors are only caught at runtime (a `NullPointerException` in Java, a `TypeError` in JavaScript). Dart's sound null safety, introduced in Dart 2.12, makes nullability part of the static type system: a variable of type `String` can never be `null`, while `String?` explicitly allows `null`. The compiler enforces this at compile time — you cannot pass a `String?` where a `String` is expected without first checking for null or using the `!` assertion operator. This is "sound" because the guarantee holds throughout the entire program, including across library boundaries, unlike Java's `@NonNull` annotations which are advisory and not enforced by the compiler.

---

### Q4: What is the role of the `main()` function in Dart?

**Answer:** `main()` is the mandatory entry point of every Dart program. When you run `dart run file.dart` or execute a compiled Dart binary, the runtime locates the top-level `main()` function and calls it first. It accepts an optional `List<String> args` parameter that receives command-line arguments passed to the program. `main()` can be synchronous (`void main()`) or asynchronous (`Future<void> main() async`) — the latter is common when the program's startup logic involves I/O or other async operations. Without a `main()` function, the Dart runtime will refuse to execute the file.

---

### Q5: What are the key differences between `dart run`, `dart compile exe`, and `dart compile js`?

**Answer:** `dart run <file.dart>` executes the program immediately using the JIT Dart VM — no compilation step is visible to the user, and the program can use `dart:mirrors` and other VM-only features. It is the standard command during development. `dart compile exe <file.dart>` performs AOT compilation and produces a self-contained native executable for the current platform (e.g., an ELF binary on Linux, a `.exe` on Windows). The output file has no dependency on the Dart SDK and starts faster than JIT, making it suitable for distributing CLI tools. `dart compile js <file.dart>` transpiles Dart to optimized JavaScript, targeting web browsers or Node.js. The output is a `.js` file that can be included in an HTML page; it does not produce native code and cannot use `dart:io` or other VM-only libraries. Each compilation target has different library restrictions: `dart:io` is available for native targets but not for JS, while `dart:html` is available for JS but not for native.

---

## 🔑 Key Takeaways

- Dart is a strongly typed, null-safe, garbage-collected language created by Google in 2011, now primarily used with Flutter.
- Dart supports both JIT (fast development iteration, hot reload) and AOT (fast startup, production performance) compilation.
- Sound null safety, introduced in Dart 2.12, eliminates null-reference errors at compile time by making nullability an explicit part of the type system.
- The `dart` CLI is the single tool for running, compiling, formatting, analyzing, and managing dependencies in Dart projects.
- Every Dart program requires a top-level `main()` function as its entry point; it optionally accepts `List<String> args` for command-line arguments.
- DartPad (dartpad.dev) provides instant, zero-install Dart experimentation in the browser.
- Dart files are structured as: imports → top-level declarations → `main()`; no class wrapper is required for top-level code.

---

## 🔗 Related Topics

- [Day 02: Variables & Types](../Week-1-Dart-Fundamentals/Day-02-Variables-Types.md) — next day: `var`, `final`, `const`, and Dart's built-in types
- [Day 03: Null Safety](../Week-1-Dart-Fundamentals/Day-03-Null-Safety.md) — deep dive into `?`, `late`, `!`, and null-aware operators
- [Day 27: Tooling & Ecosystem](../Week-4-Flutter-Dart-Interview/Day-27-Tooling-Ecosystem.md) — `pubspec.yaml`, linting, `dart fix`, and `dart doc`
- [JavaScript 30-Day Plan README](../../JavaScript/30-Day-JS-Mastery/README.md) — parallel JS learning plan for cross-language comparison
- [Dart Cheatsheet](../Cheatsheets/Dart-Cheatsheet.md) — quick-reference syntax for the entire plan
