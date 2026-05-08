# Implementation Plan: Dart 4-Week Learning Plan

## Overview

Create a complete 28-day Dart learning curriculum as a set of Markdown files under a top-level `Dart/` directory, mirroring the structure of the existing JavaScript, DS, API-Design, Database-Scaling, and DevOps plans in this workspace. The plan covers Dart fundamentals through advanced topics, with cross-references to other workspace plans.

## Tasks

- [x] 1. Create Dart/ folder structure and scaffold all files
  - Create `Dart/` at workspace root with all four week folders: `Week-1-Dart-Fundamentals/`, `Week-2-OOP-Collections/`, `Week-3-Async-Advanced/`, `Week-4-Flutter-Dart-Interview/`
  - Create `Dart/Cheatsheets/` and `Dart/Interview-Prep/` directories
  - Create empty placeholder files for all 28 day files, README.md, Dart-Cheatsheet.md, and Dart-Interview-Questions.md so the full tree is visible before content is filled in
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 2. Create Dart/README.md
  - Write title and one-paragraph description of the plan's goals
  - Add week-by-week summary table (week name, focus area, days covered)
  - Add full 28-day progress tracker table with topic names and `⬜` checkbox status indicators
  - Add relative Markdown links to every day file, the Cheatsheet, and the Interview Prep file
  - Add "How to Use" section with recommended daily routine (read → code → practice → review)
  - Add "Key Topics by Priority" section with Beginner / Intermediate / Advanced tiers
  - Add cross-reference section linking to related workspace plans (JavaScript, DS, API-Design, Database-Scaling, DevOps)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3. Create Week 1 day files (Days 01–07) — Dart Fundamentals
  - [x] 3.1 Create `Week-1-Dart-Fundamentals/Day-01-Dart-Overview-Setup.md`
    - Topic: Dart overview, SDK setup, `dart` CLI, DartPad, `main()` entry point
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As, Common Pitfalls, Key Takeaways, Related Topics
    - Cross-ref: `../../JavaScript/30-Day-JS-Mastery/README.md` (parallel JS plan)
    - _Requirements: 3.1 (Day 01), 3.2, 3.3, 3.4, 7.1–7.8_

  - [x] 3.2 Create `Week-1-Dart-Fundamentals/Day-02-Variables-Types.md`
    - Topic: `var`, `final`, `const`, type inference, built-in types (`int`, `double`, `String`, `bool`, `dynamic`, `Object`)
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As
    - _Requirements: 3.1 (Day 02), 3.2, 3.3, 3.4, 7.1–7.8_

  - [x] 3.3 Create `Week-1-Dart-Fundamentals/Day-03-Null-Safety.md`
    - Topic: Nullable types (`?`), non-nullable, `late`, `!` operator, null-aware operators (`??`, `?.`, `??=`)
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As, Common Pitfalls
    - _Requirements: 3.1 (Day 03), 3.2, 3.3, 3.4, 7.1–7.8, 10.2_

  - [x] 3.4 Create `Week-1-Dart-Fundamentals/Day-04-Control-Flow.md`
    - Topic: `if/else`, `switch` (including Dart 3 enhanced switch expressions), `for`, `while`, `do-while`, `break`, `continue`
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As
    - _Requirements: 3.1 (Day 04), 3.2, 3.3, 3.4, 7.1–7.8_

  - [x] 3.5 Create `Week-1-Dart-Fundamentals/Day-05-Functions.md`
    - Topic: Named/positional/optional parameters, default values, arrow functions, first-class functions, closures
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As
    - Cross-ref: `../../JavaScript/30-Day-JS-Mastery/Week-1-Core-Foundations/Day-07-Closures.md`
    - _Requirements: 3.1 (Day 05), 3.2, 3.3, 3.4, 7.1–7.8_

  - [x] 3.6 Create `Week-1-Dart-Fundamentals/Day-06-Collections.md`
    - Topic: `List`, `Set`, `Map`, spread operators, collection-if, collection-for, common collection methods
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As
    - Cross-ref: `../../DS/Days/Day_01_Complexity_Analysis.md`
    - _Requirements: 3.1 (Day 06), 3.2, 3.3, 3.4, 7.1–7.8_

  - [x] 3.7 Create `Week-1-Dart-Fundamentals/Day-07-Error-Handling.md`
    - Topic: `try/catch/finally`, `throw`, custom exceptions, `on` clauses, stack traces
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As, Common Pitfalls
    - _Requirements: 3.1 (Day 07), 3.2, 3.3, 3.4, 7.1–7.8_

- [x] 4. Create Week 2 day files (Days 08–14) — OOP and Collections
  - [x] 4.1 Create `Week-2-OOP-Collections/Day-08-Classes-Constructors.md`
    - Topic: Constructors (default, named, factory, redirecting, const), instance variables, methods, `this`
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As
    - _Requirements: 4.1 (Day 08), 4.2, 4.3, 4.4, 7.1–7.8_

  - [x] 4.2 Create `Week-2-OOP-Collections/Day-09-Inheritance-Abstract-Interfaces.md`
    - Topic: `extends`, `super`, method overriding, `@override`, abstract classes, implicit interfaces
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As
    - _Requirements: 4.1 (Day 09), 4.2, 4.3, 4.4, 7.1–7.8_

  - [x] 4.3 Create `Week-2-OOP-Collections/Day-10-Mixins.md`
    - Topic: `mixin`, `with`, `on` constraints, mixin composition patterns
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As, Common Pitfalls
    - _Requirements: 4.1 (Day 10), 4.2, 4.3, 4.4, 7.1–7.8_

  - [x] 4.4 Create `Week-2-OOP-Collections/Day-11-Generics.md`
    - Topic: Generic classes, generic methods, bounded type parameters, covariance, reified generics
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As
    - _Requirements: 4.1 (Day 11), 4.2, 4.3, 4.4, 7.1–7.8_

  - [x] 4.5 Create `Week-2-OOP-Collections/Day-12-Advanced-Collections.md`
    - Topic: `Iterable`, `Iterator`, lazy evaluation, `where`, `map`, `fold`, `expand`, `takeWhile`, `skipWhile`, chaining
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As
    - Cross-ref: `../../DS/Days/Day_02_Two_Pointer.md`
    - _Requirements: 4.1 (Day 12), 4.2, 4.3, 4.4, 7.1–7.8_

  - [x] 4.6 Create `Week-2-OOP-Collections/Day-13-Extension-Methods.md`
    - Topic: Defining extensions, naming conflicts, extension on nullable types, practical use cases
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As
    - _Requirements: 4.1 (Day 13), 4.2, 4.3, 4.4, 7.1–7.8_

  - [x] 4.7 Create `Week-2-OOP-Collections/Day-14-Enums.md`
    - Topic: Simple enums, enhanced enums (Dart 2.17+) with fields and methods, pattern matching on enums
    - Include ≥300-word Core Concepts, ≥3 annotated code examples, ≥5 interview Q&As
    - _Requirements: 4.1 (Day 14), 4.2, 4.3, 4.4, 7.1–7.8_

- [x] 5. Checkpoint — Verify Week 1 and Week 2 structure
  - Confirm all 14 day files exist with correct filenames and day numbering (Day-01 through Day-14)
  - Confirm each file has all required sections: What You'll Learn, Core Concepts, Code Examples, Interview Questions, Key Takeaways, Related Topics
  - Ensure all code blocks use Dart 3.x syntax and sound null safety
  - Ensure all cross-reference links use the correct `../../PlanName/...` relative path pattern
  - Ask the user if any adjustments are needed before proceeding to Week 3.

- [x] 6. Create Week 3 day files (Days 15–21) — Async and Advanced Dart
  - [x] 6.1 Create `Week-3-Async-Advanced/Day-15-Async-Fundamentals.md`
    - Topic: `Future`, `async/await`, `then/catchError`, `Future.wait`, `Future.any`, error propagation
    - Include ≥400-word Core Concepts, ≥4 annotated code examples, ≥6 interview Q&As, Common Pitfalls
    - Cross-ref: `../../JavaScript/30-Day-JS-Mastery/Week-2-Intermediate/Day-12-Async-JavaScript.md`
    - _Requirements: 5.1 (Day 15), 5.2, 5.3, 5.4, 7.1–7.8_

  - [x] 6.2 Create `Week-3-Async-Advanced/Day-16-Streams.md`
    - Topic: `Stream`, `StreamController`, `StreamSubscription`, broadcast streams, `async*`/`yield`, `StreamTransformer`
    - Include ≥400-word Core Concepts, ≥4 annotated code examples, ≥6 interview Q&As, Common Pitfalls
    - Cross-ref: `../../JavaScript/30-Day-JS-Mastery/Week-2-Intermediate/Day-11-Event-Loop.md`
    - _Requirements: 5.1 (Day 16), 5.2, 5.3, 5.4, 7.1–7.8_

  - [x] 6.3 Create `Week-3-Async-Advanced/Day-17-Isolates.md`
    - Topic: Dart concurrency model, `Isolate.spawn`, `SendPort`/`ReceivePort`, `Isolate.run` (Dart 2.19+), when to use isolates
    - Include ≥400-word Core Concepts, ≥4 annotated code examples, ≥6 interview Q&As, Common Pitfalls
    - _Requirements: 5.1 (Day 17), 5.2, 5.3, 5.4, 7.1–7.8, 10.5_

  - [x] 6.4 Create `Week-3-Async-Advanced/Day-18-Dart3-Features.md`
    - Topic: Records, patterns (destructuring, switch patterns, guard clauses), sealed classes, class modifiers (`final`, `base`, `interface`, `sealed`)
    - Include ≥400-word Core Concepts, ≥4 annotated code examples, ≥6 interview Q&As
    - Cross-ref: `../../DS/Days/Day_24_Backtracking.md`
    - _Requirements: 5.1 (Day 18), 5.2, 5.3, 5.4, 7.1–7.8, 10.1_

  - [x] 6.5 Create `Week-3-Async-Advanced/Day-19-Metaprogramming.md`
    - Topic: Annotations, reflection with `dart:mirrors` (overview), code generation with `build_runner`/`source_gen` concepts, `@pragma`
    - Include ≥400-word Core Concepts, ≥4 annotated code examples, ≥6 interview Q&As
    - _Requirements: 5.1 (Day 19), 5.2, 5.3, 5.4, 7.1–7.8_

  - [x] 6.6 Create `Week-3-Async-Advanced/Day-20-FFI.md`
    - Topic: `dart:ffi`, `Pointer`, `Struct`, `NativeFunction`, calling C libraries, memory management
    - Include ≥400-word Core Concepts, ≥4 annotated code examples, ≥6 interview Q&As, Common Pitfalls
    - _Requirements: 5.1 (Day 20), 5.2, 5.3, 5.4, 7.1–7.8_

  - [x] 6.7 Create `Week-3-Async-Advanced/Day-21-Type-System-Deep-Dive.md`
    - Topic: `typedef`, function types, `covariant`, `dynamic` vs `Object?`, type promotion, sound null safety internals
    - Include ≥400-word Core Concepts, ≥4 annotated code examples, ≥6 interview Q&As
    - _Requirements: 5.1 (Day 21), 5.2, 5.3, 5.4, 7.1–7.8_

- [x] 7. Create Week 4 day files (Days 22–28) — Flutter-Dart and Interview Prep
  - [x] 7.1 Create `Week-4-Flutter-Dart-Interview/Day-22-Flutter-Dart-Patterns.md`
    - Topic: `Widget` lifecycle patterns, `BuildContext`, `InheritedWidget` internals, `Key` types, `const` constructors in Flutter
    - Include ≥400-word Core Concepts, ≥4 annotated code examples, ≥6 interview Q&As
    - Cross-ref: `../../API-Design/Week-1-REST-Fundamentals/Day-01-REST-Principles.md`
    - _Requirements: 6.1 (Day 22), 6.2, 6.3, 6.4, 7.1–7.8_

  - [x] 7.2 Create `Week-4-Flutter-Dart-Interview/Day-23-State-Management-Patterns.md`
    - Topic: `ChangeNotifier`, `ValueNotifier`, `StreamBuilder`, `FutureBuilder`, reactive patterns
    - Include ≥400-word Core Concepts, ≥4 annotated code examples, ≥6 interview Q&As
    - _Requirements: 6.1 (Day 23), 6.2, 6.3, 6.4, 7.1–7.8_

  - [x] 7.3 Create `Week-4-Flutter-Dart-Interview/Day-24-Design-Patterns.md`
    - Topic: Singleton, Factory, Builder, Observer, Command, Repository patterns with Dart-idiomatic implementations
    - Include ≥400-word Core Concepts, ≥4 annotated code examples, ≥6 interview Q&As
    - Cross-ref: `../../JavaScript/30-Day-JS-Mastery/Week-3-Advanced/Day-18-Design-Patterns.md`
    - _Requirements: 6.1 (Day 24), 6.2, 6.3, 6.4, 7.1–7.8_

  - [x] 7.4 Create `Week-4-Flutter-Dart-Interview/Day-25-Performance-Optimization.md`
    - Topic: `const` usage, avoiding unnecessary rebuilds, `compute()`, profiling with Dart DevTools, memory leak prevention
    - Include ≥400-word Core Concepts, ≥4 annotated code examples, ≥6 interview Q&As
    - Cross-ref: `../../JavaScript/30-Day-JS-Mastery/Week-3-Advanced/Day-19-Memory-GC.md`
    - _Requirements: 6.1 (Day 25), 6.2, 6.3, 6.4, 7.1–7.8_

  - [x] 7.5 Create `Week-4-Flutter-Dart-Interview/Day-26-Testing-in-Dart.md`
    - Topic: `package:test`, unit tests, mocking with `package:mockito`, widget tests overview, TDD workflow
    - Include ≥400-word Core Concepts, ≥4 annotated code examples, ≥6 interview Q&As
    - Cross-ref: `../../JavaScript/30-Day-JS-Mastery/Week-4-Interview-Prep/Day-27-Testing.md` (if exists, else JS testing day)
    - _Requirements: 6.1 (Day 26), 6.2, 6.3, 6.4, 7.1–7.8_

  - [x] 7.6 Create `Week-4-Flutter-Dart-Interview/Day-27-Tooling-Ecosystem.md`
    - Topic: `pubspec.yaml`, `pub` package manager, linting with `analysis_options.yaml`, `dart fix`, `dart format`, `dart doc`
    - Include ≥400-word Core Concepts, ≥4 annotated code examples, ≥6 interview Q&As
    - Cross-ref: `../../DevOps/Week-3-CICD/Day-16-GitHub-Actions.md`
    - _Requirements: 6.1 (Day 27), 6.2, 6.3, 6.4, 7.1–7.8_

  - [x] 7.7 Create `Week-4-Flutter-Dart-Interview/Day-28-Mock-Interview.md`
    - Topic: 10 scenario-based Dart/Flutter interview problems with full solutions, time-complexity analysis, and follow-up discussion points
    - Include ≥400-word intro, ≥4 annotated code solutions, ≥6 follow-up Q&As
    - Cross-ref: `../../DS/Days/Day_29_Mock_Interview_1.md` and `../../DS/Days/Day_30_Mock_Interview_2.md`
    - _Requirements: 6.1 (Day 28), 6.2, 6.3, 6.4, 7.1–7.8_

- [x] 8. Create Dart/Cheatsheets/Dart-Cheatsheet.md
  - Week 1 section: variable declarations, null safety operators, control flow, function syntax, collections, error handling
  - Week 2 section: class/constructor syntax, inheritance, mixins, generics, extension methods, enums
  - Week 3 section: async/await, streams, isolates, Dart 3 records/patterns, FFI basics, typedefs
  - Week 4 section: Flutter patterns, state management, design patterns, testing snippets, tooling commands
  - Each section uses concise code blocks with minimal prose; no section exceeds 50 lines
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 9. Create Dart/Interview-Prep/Dart-Interview-Questions.md
  - Write ≥50 questions organized into 10 categories: Language Fundamentals, OOP & Mixins, Null Safety, Async & Streams, Isolates & Concurrency, Generics & Type System, Dart 3 Features, Flutter-Dart Integration, Performance & Tooling, Coding Challenges
  - Add difficulty indicator (Beginner / Intermediate / Advanced) to every question
  - Write detailed answers of ≥3 sentences per question
  - Include ≥5 coding-challenge questions that require writing Dart code as part of the answer
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 10. Final checkpoint — Verify complete plan
  - Confirm `Dart/` directory exists with all 4 week folders, 28 day files, Cheatsheets/, Interview-Prep/, and README.md
  - Spot-check that day files use Dart 3.x syntax, sound null safety, and correct naming conventions (`lowerCamelCase`, `UpperCamelCase`, `SCREAMING_SNAKE_CASE`)
  - Verify all relative cross-reference links follow the `../../PlanName/...` pattern from within week folders
  - Verify README links use `./Week-N/Day-NN-Topic.md` relative paths
  - Ensure all 28 day files contain the 6 required sections and meet minimum word/example/Q&A counts per week
  - Ensure all code examples show a simpler version before complex ones where applicable
  - Ask the user if any content or structural adjustments are needed.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints at tasks 5 and 10 ensure incremental validation
- No property-based tests apply — this is a static documentation plan; quality is verified via structural checklists
- Cross-reference links from `Dart/Week-N/Day-NN.md` files use `../../PlanName/` prefix; links from `Dart/README.md` use `../PlanName/` prefix
