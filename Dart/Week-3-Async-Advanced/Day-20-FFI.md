# Day 20: FFI (Foreign Function Interface)

## 🎯 What You'll Learn
- What FFI is and when to use it
- The `dart:ffi` library and its core types
- Working with `Pointer`, `Struct`, and native memory
- Calling C functions from Dart
- Memory management and preventing leaks
- Using `@Native` annotation for simplified FFI (Dart 3.1+)
- Performance considerations and safety concerns

## 📚 Core Concepts

**FFI (Foreign Function Interface)** allows Dart code to call functions written in C and other languages that follow the C calling convention. This enables Dart to interoperate with native libraries, access platform-specific APIs, and perform operations that require native performance. FFI is commonly used in Flutter plugins to bridge Dart and platform code (iOS/Android/Windows/macOS/Linux).

### Why Use FFI?

Use FFI when you need to:
- Call existing C/C++ libraries (image processing, cryptography, databases)
- Access platform-specific APIs not exposed through Dart
- Achieve native performance for CPU-intensive operations
- Reuse legacy native code in a Dart application
- Build Flutter plugins that wrap native SDKs

FFI is lower-level and more dangerous than pure Dart — you're responsible for memory management, and mistakes can cause crashes or security vulnerabilities. Use it only when necessary.

### dart:ffi Core Types

The `dart:ffi` library provides types for interacting with native code:

- **`Pointer<T>`**: A pointer to native memory. `Pointer<Int32>` points to a 32-bit integer, `Pointer<Utf8>` points to a null-terminated UTF-8 string.
- **`Struct`**: Base class for defining C structs in Dart. Fields are annotated with native types.
- **`NativeFunction<T>`**: Represents a C function pointer. Used with `DynamicLibrary.lookup` to find functions.
- **`DynamicLibrary`**: Represents a loaded native library (`.so`, `.dylib`, `.dll`). Use `DynamicLibrary.open()` to load a library.
- **Native types**: `Int8`, `Int16`, `Int32`, `Int64`, `Uint8`, `Uint16`, `Uint32`, `Uint64`, `Float`, `Double`, `Void`, `Pointer`, etc.

### Loading a Native Library

Use `DynamicLibrary.open(path)` to load a shared library. The path is platform-specific (`.so` on Linux/Android, `.dylib` on macOS/iOS, `.dll` on Windows). For Flutter plugins, use `DynamicLibrary.process()` or `DynamicLibrary.executable()` to access symbols from the current process.

```dart
import 'dart:ffi';
import 'dart:io';

final DynamicLibrary nativeLib = Platform.isAndroid
    ? DynamicLibrary.open('libnative.so')
    : DynamicLibrary.process();
```

### Calling C Functions

To call a C function:
1. Define a Dart typedef matching the C function signature using native types
2. Look up the function in the loaded library with `lookup<NativeFunction<T>>()`
3. Convert it to a Dart function with `.asFunction<T>()`

```dart
// C function: int add(int a, int b);

// 1. Define native signature
typedef AddNative = Int32 Function(Int32 a, Int32 b);

// 2. Define Dart signature
typedef AddDart = int Function(int a, int b);

// 3. Look up and convert
final add = nativeLib
    .lookup<NativeFunction<AddNative>>('add')
    .asFunction<AddDart>();

// 4. Call like a normal Dart function
print(add(2, 3)); // 5
```

### Working with Pointers and Memory

Pointers in Dart FFI are raw memory addresses. You allocate memory with `malloc.allocate<T>(count)` (from `package:ffi`) and must manually free it with `malloc.free(pointer)` to prevent leaks. Always use `try/finally` or `using` to ensure cleanup.

```dart
import 'package:ffi/ffi.dart';

final pointer = malloc.allocate<Int32>(1); // allocate 4 bytes
try {
  pointer.value = 42; // write to memory
  print(pointer.value); // read from memory
} finally {
  malloc.free(pointer); // always free!
}
```

### Structs

Define C structs in Dart by extending `Struct` and annotating fields with native types. Dart generates the memory layout to match the C struct.

```dart
class Point extends Struct {
  @Int32()
  external int x;

  @Int32()
  external int y;
}

final pointer = malloc.allocate<Point>(sizeOf<Point>());
final point = pointer.ref;
point.x = 10;
point.y = 20;
malloc.free(pointer);
```

### Strings and UTF-8

C strings are null-terminated byte arrays. Use `Pointer<Utf8>` and the `package:ffi` helpers `toNativeUtf8()` and `toDartString()` to convert between Dart strings and C strings.

```dart
import 'package:ffi/ffi.dart';

// Dart to C
final cString = 'Hello'.toNativeUtf8();
try {
  // pass cString to C function
} finally {
  malloc.free(cString); // free the allocated memory
}

// C to Dart
final dartString = cStringPointer.toDartString();
```

### @Native Annotation (Dart 3.1+)

Dart 3.1 introduced the `@Native` annotation to simplify FFI. Instead of manually looking up functions, you declare them as `external` and annotate with `@Native`. The Dart compiler generates the lookup code.

```dart
@Native<Int32 Function(Int32, Int32)>(symbol: 'add')
external int add(int a, int b);

// No need for lookup or asFunction — just call it
print(add(2, 3)); // 5
```

This is cleaner and less error-prone than manual lookup, but requires Dart 3.1+.

### Memory Management and Safety

FFI is unsafe — Dart's memory safety guarantees don't apply to native code. Common pitfalls:
- **Memory leaks**: Forgetting to free allocated memory
- **Use-after-free**: Accessing freed memory
- **Buffer overflows**: Writing past the end of allocated memory
- **Null pointer dereferences**: Accessing `nullptr`

Always use `try/finally` for cleanup, validate pointer arguments, and test thoroughly. Consider using `Finalizer` (Dart 2.17+) to automatically free memory when Dart objects are garbage collected.


## 💻 Code Examples

### Example 1: Loading a library and calling a simple function

```dart
import 'dart:ffi';
import 'dart:io';

// C code (compiled to libnative.so / libnative.dylib / native.dll):
// int multiply(int a, int b) {
//   return a * b;
// }

// Load the native library
final DynamicLibrary nativeLib = Platform.isLinux
    ? DynamicLibrary.open('libnative.so')
    : Platform.isMacOS
        ? DynamicLibrary.open('libnative.dylib')
        : DynamicLibrary.open('native.dll');

// Define native function signature
typedef MultiplyNative = Int32 Function(Int32 a, Int32 b);

// Define Dart function signature
typedef MultiplyDart = int Function(int a, int b);

// Look up the function and convert to Dart callable
final multiply = nativeLib
    .lookup<NativeFunction<MultiplyNative>>('multiply')
    .asFunction<MultiplyDart>();

void main() {
  print('5 * 7 = ${multiply(5, 7)}'); // 5 * 7 = 35
}
```

### Example 2: Working with pointers and memory allocation

```dart
import 'dart:ffi';
import 'package:ffi/ffi.dart';

void main() {
  // Allocate memory for a single Int32
  final pointer = malloc.allocate<Int32>(sizeOf<Int32>());

  try {
    // Write to the pointer
    pointer.value = 42;
    print('Value: ${pointer.value}'); // Value: 42

    // Modify the value
    pointer.value = pointer.value * 2;
    print('Doubled: ${pointer.value}'); // Doubled: 84

    // Allocate an array of 5 integers
    final array = malloc.allocate<Int32>(sizeOf<Int32>() * 5);
    try {
      // Write to array elements
      for (int i = 0; i < 5; i++) {
        array[i] = i * 10;
      }

      // Read from array
      print('Array: ${[for (int i = 0; i < 5; i++) array[i]]}');
      // Array: [0, 10, 20, 30, 40]
    } finally {
      malloc.free(array);
    }
  } finally {
    // Always free allocated memory
    malloc.free(pointer);
  }
}
```

### Example 3: Defining and using structs

```dart
import 'dart:ffi';
import 'package:ffi/ffi.dart';

// Define a C struct in Dart
class Rectangle extends Struct {
  @Int32()
  external int width;

  @Int32()
  external int height;

  // Helper method (not part of C struct)
  int get area => width * height;
}

// C function: int calculate_area(Rectangle* rect);
typedef CalculateAreaNative = Int32 Function(Pointer<Rectangle> rect);
typedef CalculateAreaDart = int Function(Pointer<Rectangle> rect);

void main() {
  // Allocate memory for the struct
  final pointer = malloc.allocate<Rectangle>(sizeOf<Rectangle>());

  try {
    // Access the struct through .ref
    final rect = pointer.ref;
    rect.width = 10;
    rect.height = 20;

    print('Width: ${rect.width}');   // Width: 10
    print('Height: ${rect.height}'); // Height: 20
    print('Area: ${rect.area}');     // Area: 200

    // If we had a native function, we'd call it like:
    // final calculateArea = nativeLib
    //     .lookup<NativeFunction<CalculateAreaNative>>('calculate_area')
    //     .asFunction<CalculateAreaDart>();
    // print('Native area: ${calculateArea(pointer)}');
  } finally {
    malloc.free(pointer);
  }
}
```

### Example 4: Working with C strings

```dart
import 'dart:ffi';
import 'package:ffi/ffi.dart';

// C function: void print_string(const char* str);
typedef PrintStringNative = Void Function(Pointer<Utf8> str);
typedef PrintStringDart = void Function(Pointer<Utf8> str);

// C function: const char* get_greeting();
typedef GetGreetingNative = Pointer<Utf8> Function();
typedef GetGreetingDart = Pointer<Utf8> Function();

void main() {
  // Convert Dart string to C string
  final dartString = 'Hello from Dart!';
  final cString = dartString.toNativeUtf8();

  try {
    // Pass to C function (if we had one)
    // printString(cString);

    // Manually read the C string back
    print('C string: ${cString.toDartString()}');
    // C string: Hello from Dart!
  } finally {
    // Always free the allocated C string
    malloc.free(cString);
  }

  // Simulate receiving a C string from native code
  final nativeGreeting = 'Hello from C!'.toNativeUtf8();
  try {
    // Convert C string to Dart string
    final dartGreeting = nativeGreeting.toDartString();
    print('Dart string: $dartGreeting');
    // Dart string: Hello from C!
  } finally {
    malloc.free(nativeGreeting);
  }
}
```

### Example 5: Using @Native annotation (Dart 3.1+)

```dart
import 'dart:ffi';
import 'dart:io';

// Load the native library
final DynamicLibrary nativeLib = Platform.isLinux
    ? DynamicLibrary.open('libnative.so')
    : DynamicLibrary.process();

// Simplified FFI with @Native annotation
@Native<Int32 Function(Int32, Int32)>(symbol: 'add', isLeaf: true)
external int add(int a, int b);

@Native<Double Function(Double)>(symbol: 'sqrt')
external double sqrt(double x);

// For functions with custom library
@Native<Void Function(Pointer<Utf8>)>(symbol: 'log_message')
external void logMessage(Pointer<Utf8> message);

void main() {
  // Call native functions directly — no manual lookup needed
  print('2 + 3 = ${add(2, 3)}');       // 2 + 3 = 5
  print('sqrt(16) = ${sqrt(16.0)}');   // sqrt(16) = 4.0

  // Note: @Native requires Dart 3.1+ and proper library configuration
}
```

### Example 6: Memory management with Finalizer

```dart
import 'dart:ffi';
import 'package:ffi/ffi.dart';

// Wrapper class that automatically frees memory when garbage collected
class NativeBuffer {
  final Pointer<Uint8> _pointer;
  final int size;

  // Finalizer to free memory when object is garbage collected
  static final _finalizer = Finalizer<Pointer<Uint8>>((pointer) {
    print('Finalizer: freeing memory at $pointer');
    malloc.free(pointer);
  });

  NativeBuffer(this.size) : _pointer = malloc.allocate<Uint8>(size) {
    // Register this object with the finalizer
    _finalizer.attach(this, _pointer, detach: this);
  }

  Pointer<Uint8> get pointer => _pointer;

  void write(int index, int value) {
    if (index < 0 || index >= size) {
      throw RangeError('Index out of bounds');
    }
    _pointer[index] = value;
  }

  int read(int index) {
    if (index < 0 || index >= size) {
      throw RangeError('Index out of bounds');
    }
    return _pointer[index];
  }

  // Manual cleanup (optional, but good practice)
  void dispose() {
    _finalizer.detach(this);
    malloc.free(_pointer);
  }
}

void main() {
  // Create a buffer — memory will be freed automatically when GC runs
  final buffer = NativeBuffer(10);

  buffer.write(0, 42);
  buffer.write(1, 84);

  print('buffer[0] = ${buffer.read(0)}'); // buffer[0] = 42
  print('buffer[1] = ${buffer.read(1)}'); // buffer[1] = 84

  // Optionally dispose manually
  buffer.dispose();

  // If we don't call dispose(), the finalizer will free memory during GC
}
```

## ⚠️ Common Pitfalls

- **Memory leaks**: Forgetting to call `malloc.free()` on allocated pointers. Always use `try/finally` or `Finalizer` to ensure cleanup.
- **Use-after-free**: Accessing a pointer after freeing it causes crashes or undefined behavior. Set pointers to `nullptr` after freeing if you might accidentally reuse them.
- **Incorrect type sizes**: Native types have platform-specific sizes. Use `sizeOf<T>()` to get the correct size, not hardcoded values.
- **String encoding issues**: C strings are UTF-8 by default. If the native code uses a different encoding, you'll get garbled text. Always verify encoding.
- **Null pointer dereferences**: Accessing `nullptr` crashes the app. Always check `pointer.address != 0` before dereferencing.
- **Platform-specific library paths**: Library names differ by platform (`.so`, `.dylib`, `.dll`). Use `Platform.isX` checks or a build system to handle this.
- **Forgetting @pragma('vm:entry-point')**: If native code calls back into Dart, mark the Dart function with `@pragma('vm:entry-point')` to prevent tree-shaking.

## ❓ Interview Questions

### Q1: What is FFI and when should you use it in Dart?
**Answer**: FFI (Foreign Function Interface) allows Dart to call functions written in C and other languages that follow the C calling convention. Use FFI when you need to call existing native libraries (like image processing or cryptography libraries), access platform-specific APIs not exposed through Dart, achieve native performance for CPU-intensive operations, or build Flutter plugins that wrap native SDKs. FFI is lower-level and more dangerous than pure Dart — you're responsible for memory management and mistakes can cause crashes, so use it only when necessary.

### Q2: How do you call a C function from Dart using FFI?
**Answer**: First, load the native library with `DynamicLibrary.open(path)`. Then define two typedefs: one for the native function signature using native types (like `Int32`), and one for the Dart signature using Dart types (like `int`). Look up the function with `library.lookup<NativeFunction<NativeType>>('functionName')` and convert it to a Dart callable with `.asFunction<DartType>()`. Finally, call it like a normal Dart function. Dart 3.1+ simplifies this with the `@Native` annotation, which generates the lookup code automatically.

### Q3: What is the difference between Pointer<T> and T in dart:ffi?
**Answer**: `Pointer<T>` is a raw memory address pointing to a value of type `T` in native memory. It's analogous to `T*` in C. You access the value through `.value` for primitive types or `.ref` for structs. `T` itself is the Dart representation of the native type — for example, `Int32` is the native type, but you work with Dart `int` values. Pointers are used for passing data to/from native code and for manual memory management. Always free pointers allocated with `malloc.allocate()` to prevent leaks.

### Q4: How do you manage memory when using FFI?
**Answer**: Memory allocated with `malloc.allocate<T>()` (from `package:ffi`) must be manually freed with `malloc.free(pointer)`. Always use `try/finally` blocks to ensure cleanup even if exceptions occur. For automatic cleanup, use `Finalizer` (Dart 2.17+) to register pointers for cleanup when Dart objects are garbage collected. Never access a pointer after freeing it (use-after-free), and always validate pointer arguments to prevent null pointer dereferences. FFI bypasses Dart's memory safety, so mistakes can cause crashes or security vulnerabilities.

### Q5: What are Structs in dart:ffi and how do you define them?
**Answer**: Structs in `dart:ffi` represent C structs — compound types with multiple fields. Define a struct by extending `Struct` and annotating fields with native types like `@Int32()`, `@Double()`, etc. Fields must be `external` — Dart generates the memory layout to match the C struct. Access struct fields through a pointer's `.ref` property. For example: `final rect = pointer.ref; rect.width = 10;`. Structs are useful for passing complex data structures to/from native code. Always allocate and free struct memory manually.

### Q6: How do you work with strings in FFI?
**Answer**: C strings are null-terminated byte arrays, represented as `Pointer<Utf8>` in Dart. Convert a Dart string to a C string with `'text'.toNativeUtf8()` (from `package:ffi`), which allocates memory that you must free with `malloc.free()`. Convert a C string to Dart with `pointer.toDartString()`. Always use `try/finally` to ensure C strings are freed. Be aware of encoding — C strings are typically UTF-8, but some native APIs use other encodings. Validate encoding to avoid garbled text.

### Q7: What is the @Native annotation and how does it simplify FFI?
**Answer**: The `@Native` annotation (Dart 3.1+) simplifies FFI by eliminating manual function lookup. Instead of using `lookup<NativeFunction<T>>()` and `.asFunction<T>()`, you declare the function as `external` and annotate it with `@Native<NativeSignature>(symbol: 'functionName')`. The Dart compiler generates the lookup code automatically. This is cleaner, less error-prone, and reduces boilerplate. You can also specify `isLeaf: true` for functions that don't call back into Dart, enabling further optimizations. `@Native` requires Dart 3.1+ and proper library configuration.

### Q8: What are the safety concerns when using FFI?
**Answer**: FFI bypasses Dart's memory safety guarantees. Common dangers: memory leaks (forgetting to free allocated memory), use-after-free (accessing freed memory), buffer overflows (writing past allocated bounds), null pointer dereferences (accessing `nullptr`), and type mismatches (passing wrong types to native functions). Native code can crash the entire app without Dart's exception handling. Always validate inputs, use `try/finally` for cleanup, test thoroughly, and consider using `Finalizer` for automatic memory management. Only use FFI when necessary and isolate native code behind safe Dart APIs.



## 🔑 Key Takeaways
- FFI allows Dart to call C functions and access native libraries
- Use `DynamicLibrary.open()` to load libraries and `lookup()` to find functions
- `Pointer<T>` represents raw memory addresses; always free allocated memory with `malloc.free()`
- Structs extend `Struct` with `@NativeType()` annotated fields for C struct interop
- C strings are `Pointer<Utf8>`; use `toNativeUtf8()` and `toDartString()` for conversion
- `@Native` annotation (Dart 3.1+) simplifies FFI by generating lookup code
- FFI is unsafe — memory leaks, use-after-free, and crashes are possible; always validate and test

## 🔗 Related Topics
- [Day 17: Isolates](./Day-17-Isolates.md) — FFI can be used in isolates for parallel native work
- [Day 19: Metaprogramming](./Day-19-Metaprogramming.md) — `@pragma` for FFI entry points
- [Day 21: Type System Deep Dive](./Day-21-Type-System-Deep-Dive.md) — native types vs Dart types
- [Day 27: Tooling and Ecosystem](../Week-4-Flutter-Dart-Interview/Day-27-Tooling-Ecosystem.md) — building native libraries
- [DevOps Docker](../../DevOps/Week-1-Docker/Day-01-Docker-Fundamentals.md) — containerizing apps with native dependencies
