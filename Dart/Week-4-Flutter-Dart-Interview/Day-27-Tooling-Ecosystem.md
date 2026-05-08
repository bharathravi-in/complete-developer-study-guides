# Day 27: Tooling & Ecosystem

## 🎯 What You'll Learn
- `pubspec.yaml` structure and dependency management
- `pub` package manager: `pub get`, `pub upgrade`, `pub outdated`
- Linting with `analysis_options.yaml` and recommended rule sets
- `dart fix` for automated code migrations and fixes
- `dart format` for consistent code style
- `dart doc` for generating API documentation
- Dart DevTools for debugging and profiling
- Popular packages: `http`, `dio`, `provider`, `riverpod`, `freezed`, `json_serializable`

## 📚 Core Concepts

Dart's tooling ecosystem is designed for productivity and consistency. The `dart` CLI provides commands for formatting, linting, testing, and documentation. The `pub` package manager handles dependencies. `analysis_options.yaml` enforces code quality. Together, these tools enable teams to maintain high-quality, consistent codebases.

### `pubspec.yaml` — Project Configuration

`pubspec.yaml` is the project manifest. It declares:
- Package name and version
- Dart SDK constraints
- Dependencies (runtime and dev)
- Assets (for Flutter apps)

Example:

```yaml
name: my_app
description: A sample Dart application
version: 1.0.0
publish_to: 'none' # prevents accidental publishing

environment:
  sdk: '>=3.0.0 <4.0.0'

dependencies:
  http: ^1.1.0
  provider: ^6.0.5

dev_dependencies:
  test: ^1.24.0
  mockito: ^5.4.0
  build_runner: ^2.4.0
```

**Dependency versioning**:
- `^1.2.3` — compatible with 1.2.3, allows 1.x.x (not 2.0.0)
- `>=1.2.3 <2.0.0` — explicit range
- `any` — any version (avoid in production)

### `pub` Package Manager

`pub` manages dependencies and packages:

| Command | Purpose |
|---------|---------|
| `dart pub get` / `flutter pub get` | Install dependencies from `pubspec.yaml` |
| `dart pub upgrade` | Upgrade dependencies to latest compatible versions |
| `dart pub outdated` | Show outdated dependencies |
| `dart pub add <package>` | Add a dependency to `pubspec.yaml` |
| `dart pub remove <package>` | Remove a dependency |
| `dart pub publish` | Publish a package to pub.dev |

Dependencies are cached in `~/.pub-cache` and symlinked into `.dart_tool/package_config.json`.

### Linting with `analysis_options.yaml`

`analysis_options.yaml` configures the Dart analyzer. It enforces code quality rules (lints) and customizes warnings/errors.

Example:

```yaml
include: package:lints/recommended.yaml

analyzer:
  exclude:
    - '**/*.g.dart' # exclude generated files
    - '**/*.freezed.dart'
  strong-mode:
    implicit-casts: false
    implicit-dynamic: false

linter:
  rules:
    - prefer_const_constructors
    - prefer_const_literals_to_create_immutables
    - avoid_print
    - always_declare_return_types
    - require_trailing_commas
```

**Recommended rule sets**:
- `package:lints/core.yaml` — minimal rules
- `package:lints/recommended.yaml` — balanced rules for apps
- `package:flutter_lints/flutter.yaml` — Flutter-specific rules

Enable rules that catch bugs (`avoid_null_checks_in_equality_operators`) and enforce style (`prefer_const_constructors`).

### `dart fix` — Automated Code Fixes

`dart fix` applies automated fixes for lint warnings and deprecations:

```bash
dart fix --dry-run  # preview fixes
dart fix --apply    # apply fixes
```

Use it to:
- Migrate to new APIs (e.g., `Isolate.spawn` → `Isolate.run`)
- Fix lint violations (e.g., add `const` to constructors)
- Update deprecated code

`dart fix` is safe — it only applies fixes that preserve behavior.

### `dart format` — Code Formatting

`dart format` formats code according to the Dart style guide:

```bash
dart format .              # format all files
dart format lib/main.dart  # format one file
dart format --set-exit-if-changed .  # CI mode (exit 1 if unformatted)
```

Formatting is deterministic and non-configurable (no bikeshedding). Use it in pre-commit hooks and CI pipelines to enforce consistency.

### `dart doc` — API Documentation

`dart doc` generates HTML documentation from doc comments:

```dart
/// Calculates the factorial of [n].
///
/// Throws [ArgumentError] if [n] is negative.
///
/// Example:
/// ```dart
/// print(factorial(5)); // 120
/// ```
int factorial(int n) {
  if (n < 0) throw ArgumentError('n must be non-negative');
  return n == 0 ? 1 : n * factorial(n - 1);
}
```

Run `dart doc` to generate docs in `doc/api/`. Use `///` for public APIs and `//` for internal comments.

### Dart DevTools

Dart DevTools is a suite of debugging and profiling tools:

- **Inspector**: Visualize widget tree, view properties, highlight repaints
- **Timeline**: Profile frame rendering, identify jank
- **Memory**: Track heap usage, detect leaks
- **CPU Profiler**: Identify hot functions
- **Network**: Inspect HTTP requests/responses
- **Logging**: View print statements and errors

Launch with `dart devtools` or `flutter pub global run devtools`.

### Popular Packages

| Package | Purpose |
|---------|---------|
| `http` | Simple HTTP client |
| `dio` | Advanced HTTP client with interceptors, retries |
| `provider` | State management with `InheritedWidget` |
| `riverpod` | Provider 2.0 — compile-safe, no `BuildContext` |
| `bloc` | State management with streams and BLoC pattern |
| `freezed` | Code generation for immutable classes |
| `json_serializable` | JSON serialization code generation |
| `shared_preferences` | Key-value storage |
| `sqflite` | SQLite database for Flutter |
| `path_provider` | Access device directories |

Browse packages at [pub.dev](https://pub.dev).

## 💻 Code Examples

### Example 1: `pubspec.yaml` with dependencies

```yaml
name: weather_app
description: A weather forecast application
version: 1.0.0+1
publish_to: 'none'

environment:
  sdk: '>=3.0.0 <4.0.0'
  flutter: '>=3.10.0'

dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0          # HTTP client
  provider: ^6.0.5      # State management
  intl: ^0.18.0         # Internationalization

dev_dependencies:
  flutter_test:
    sdk: flutter
  mockito: ^5.4.0       # Mocking for tests
  build_runner: ^2.4.0  # Code generation
  flutter_lints: ^2.0.0 # Linting rules
```

### Example 2: `analysis_options.yaml` with custom rules

```yaml
include: package:flutter_lints/flutter.yaml

analyzer:
  exclude:
    - '**/*.g.dart'
    - '**/*.freezed.dart'
    - 'build/**'
  
  strong-mode:
    implicit-casts: false      # disallow implicit downcasts
    implicit-dynamic: false    # disallow implicit dynamic

  errors:
    missing_required_param: error
    missing_return: error
    todo: ignore               # don't warn on TODO comments

linter:
  rules:
    # Style
    - prefer_const_constructors
    - prefer_const_literals_to_create_immutables
    - prefer_final_fields
    - prefer_final_locals
    - require_trailing_commas
    
    # Errors
    - avoid_print
    - avoid_returning_null_for_void
    - cancel_subscriptions
    - close_sinks
    
    # Documentation
    - public_member_api_docs
```

### Example 3: Using `dart fix` to apply automated fixes

```bash
# Preview fixes without applying
$ dart fix --dry-run
Computing fixes in my_app... 2.1s
  lib/main.dart:10:5 • prefer_const_constructors
  lib/main.dart:15:12 • prefer_const_constructors
  lib/utils.dart:5:3 • unnecessary_this

3 fixes found.

# Apply fixes
$ dart fix --apply
Computing fixes in my_app... 2.0s
Applying fixes... 0.5s
  lib/main.dart:10:5 • prefer_const_constructors
  lib/main.dart:15:12 • prefer_const_constructors
  lib/utils.dart:5:3 • unnecessary_this

3 fixes applied.
```

### Example 4: Documenting code with `dart doc`

```dart
/// A service for fetching weather data.
///
/// This service uses the OpenWeatherMap API to retrieve current weather
/// and forecasts for a given city.
///
/// Example:
/// ```dart
/// final service = WeatherService(apiKey: 'your_key');
/// final weather = await service.getCurrentWeather('London');
/// print('Temperature: ${weather.temperature}°C');
/// ```
class WeatherService {
  /// The API key for OpenWeatherMap.
  final String apiKey;

  /// Creates a [WeatherService] with the given [apiKey].
  WeatherService({required this.apiKey});

  /// Fetches the current weather for [city].
  ///
  /// Returns a [Weather] object with temperature, humidity, and conditions.
  /// Throws [HttpException] if the request fails.
  Future<Weather> getCurrentWeather(String city) async {
    // Implementation...
    throw UnimplementedError();
  }
}

/// Represents weather data for a location.
class Weather {
  /// Temperature in Celsius.
  final double temperature;

  /// Humidity percentage (0-100).
  final int humidity;

  /// Weather conditions (e.g., "Clear", "Cloudy").
  final String conditions;

  /// Creates a [Weather] instance.
  const Weather({
    required this.temperature,
    required this.humidity,
    required this.conditions,
  });
}
```

Run `dart doc` to generate HTML documentation.

## ⚠️ Common Pitfalls

- **Not running `pub get` after changing `pubspec.yaml`**: Dependencies aren't updated until you run `dart pub get` or `flutter pub get`.
- **Ignoring lint warnings**: Lints catch bugs and enforce best practices. Fix them, don't disable them.
- **Not using `dart format` in CI**: Unformatted code causes merge conflicts. Run `dart format --set-exit-if-changed .` in CI to enforce formatting.
- **Committing generated files**: Files like `*.g.dart` and `*.freezed.dart` should be in `.gitignore` (regenerate them with `build_runner`).
- **Not documenting public APIs**: Public classes, methods, and fields should have doc comments (`///`). Enable the `public_member_api_docs` lint.

## ❓ Interview Questions

### Q1: What is `pubspec.yaml` and what does it contain?
**Answer**: `pubspec.yaml` is the project manifest for Dart and Flutter projects. It declares the package name, version, description, Dart SDK constraints, dependencies (runtime and dev), and assets (for Flutter). Dependencies use semantic versioning with constraints like `^1.2.3` (compatible with 1.x.x) or `>=1.2.3 <2.0.0` (explicit range). When you run `dart pub get`, pub resolves dependencies, downloads packages to `~/.pub-cache`, and generates `.dart_tool/package_config.json`. Changes to `pubspec.yaml` require running `pub get` to take effect.

### Q2: What is the difference between `dart pub get` and `dart pub upgrade`?
**Answer**: `dart pub get` installs dependencies according to `pubspec.lock` (if it exists) or resolves the latest compatible versions from `pubspec.yaml` and creates `pubspec.lock`. It's deterministic — running it twice gives the same versions. `dart pub upgrade` ignores `pubspec.lock` and resolves the latest compatible versions from `pubspec.yaml`, then updates `pubspec.lock`. Use `pub get` for reproducible builds (CI, new clones) and `pub upgrade` to update dependencies to the latest versions.

### Q3: How does `analysis_options.yaml` improve code quality?
**Answer**: `analysis_options.yaml` configures the Dart analyzer to enforce code quality rules (lints). It can enable/disable specific rules, exclude files (e.g., generated code), and customize error levels. Recommended rule sets like `package:lints/recommended.yaml` catch common bugs (`avoid_null_checks_in_equality_operators`), enforce best practices (`prefer_const_constructors`), and improve readability (`require_trailing_commas`). Lints run in the IDE (real-time feedback) and CI (fail builds on violations). This prevents bugs, enforces consistency, and makes code reviews faster.

### Q4: What is `dart fix` and when should you use it?
**Answer**: `dart fix` applies automated fixes for lint warnings, deprecations, and API migrations. It analyzes your code, identifies fixable issues, and applies safe transformations that preserve behavior. Use it to migrate to new APIs (e.g., `Isolate.spawn` → `Isolate.run`), fix lint violations (e.g., add `const` to constructors), and update deprecated code. Run `dart fix --dry-run` to preview fixes, then `dart fix --apply` to apply them. It's safe and deterministic — the same code always produces the same fixes.

### Q5: Why is `dart format` non-configurable?
**Answer**: `dart format` is intentionally non-configurable to eliminate bikeshedding (endless debates about style). The Dart team chose a single, deterministic style based on research and community feedback. This ensures all Dart code looks consistent, makes code reviews focus on logic (not style), and prevents teams from wasting time configuring formatters. The trade-off is that you can't customize the style, but the benefit is zero configuration and universal consistency. Use it in pre-commit hooks and CI to enforce formatting automatically.

### Q6: What are the most important packages in the Dart ecosystem?
**Answer**: For HTTP: `http` (simple) and `dio` (advanced with interceptors). For state management: `provider` (simple, built on `InheritedWidget`), `riverpod` (compile-safe, no `BuildContext`), and `bloc` (streams and BLoC pattern). For code generation: `freezed` (immutable classes), `json_serializable` (JSON serialization), and `build_runner` (runs generators). For storage: `shared_preferences` (key-value), `sqflite` (SQLite), and `hive` (NoSQL). For utilities: `intl` (internationalization), `path` (file paths), and `collection` (advanced collections). Browse packages at pub.dev and check popularity, likes, and pub points.

## 🔑 Key Takeaways
- `pubspec.yaml` declares dependencies; `pub get` installs them
- `analysis_options.yaml` enforces code quality with lints
- `dart fix` applies automated fixes for lints and deprecations
- `dart format` enforces consistent style (non-configurable)
- `dart doc` generates HTML documentation from doc comments
- Dart DevTools provides debugging, profiling, and inspection tools
- Popular packages: `http`, `provider`, `riverpod`, `freezed`, `json_serializable`

## 🔗 Related Topics
- [Day 26: Testing in Dart](./Day-26-Testing-in-Dart.md) — `package:test`, `mockito`, `build_runner`
- [Day 01: Dart Overview & Setup](../Week-1-Dart-Fundamentals/Day-01-Dart-Overview-Setup.md) — SDK installation
- [DevOps CI/CD](../../DevOps/Week-3-CICD/Day-16-GitHub-Actions.md) — integrating Dart tools in CI
- [Day 19: Metaprogramming](../Week-3-Async-Advanced/Day-19-Metaprogramming.md) — code generation
