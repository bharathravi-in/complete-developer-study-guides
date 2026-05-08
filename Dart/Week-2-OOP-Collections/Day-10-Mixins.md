# Day 10: Mixins

## 🎯 What You'll Learn

- What a mixin is and how it differs from a class, abstract class, and interface
- How to declare a mixin with the `mixin` keyword and apply it with `with`
- How the `on` constraint restricts which classes a mixin can be applied to
- How to compose multiple mixins and understand linearization order
- How Dart resolves method conflicts when multiple mixins define the same method
- The difference between `mixin`, `mixin class`, and `abstract class` in Dart 3
- Practical patterns for using mixins to share behavior across unrelated hierarchies
- Limitations of mixins — no generative constructors, no `new MixinName()`

---

## 📚 Core Concepts

### What Is a Mixin?

A **mixin** is a way to reuse a class's code in multiple class hierarchies without using inheritance. Where `extends` gives you one parent and `implements` gives you a contract with no code, `with` gives you **code reuse without a parent–child relationship**. You can think of a mixin as a bundle of methods and fields that gets "mixed into" a class.

Dart uses the `mixin` keyword (introduced in Dart 2.1) to declare a pure mixin — a construct that can only be used with `with`, cannot be instantiated directly, and cannot have generative constructors. Before Dart 2.1, regular classes were used as mixins, which caused ambiguity; the dedicated `mixin` keyword makes intent explicit.

```dart
mixin Flyable {
  void fly() => print('$runtimeType is flying');
}

class Bird with Flyable {}
class Airplane with Flyable {}
```

Both `Bird` and `Airplane` gain `fly()` without sharing a common ancestor beyond `Object`. This is the core value proposition: **horizontal code reuse** across otherwise unrelated hierarchies.

### Declaring a Mixin

A mixin declaration looks like a class declaration but uses the `mixin` keyword:

```dart
mixin Swimmable {
  double _waterSpeed = 0; // instance variable — allowed in mixins

  void swim(double speed) {
    _waterSpeed = speed;
    print('$runtimeType swims at ${_waterSpeed}m/s');
  }

  double get waterSpeed => _waterSpeed;
}
```

Mixins **can** have instance variables and concrete methods. They **cannot** have generative constructors (constructors that create instances), because a mixin is never instantiated on its own. Dart 3 introduced `mixin class` for the rare case where you need both mixin and class behavior, but pure `mixin` is the idiomatic choice.

### Applying a Mixin with `with`

Apply one or more mixins using the `with` keyword after the class name (and after `extends` if present):

```dart
class Duck extends Animal with Flyable, Swimmable {
  Duck(super.name);
}
```

The order matters: mixins are listed left to right, and the rightmost mixin is "closest" to the class in the linearization chain (explained below).

### The `on` Constraint

The `on` keyword restricts which classes a mixin can be applied to. A mixin declared with `on SomeClass` can only be used by classes that extend or implement `SomeClass`. This is useful when a mixin needs to call methods that are guaranteed to exist on the target class:

```dart
abstract class Animal {
  String get name;
  void breathe();
}

mixin Logging on Animal {
  // Can safely call name and breathe() because the on constraint
  // guarantees this mixin is only applied to Animal subclasses.
  void logAction(String action) {
    print('[${DateTime.now()}] $name: $action');
    breathe(); // safe — Animal guarantees this method exists
  }
}

class Dog extends Animal with Logging {
  @override
  final String name;
  Dog(this.name);

  @override
  void breathe() => print('$name breathes');
}
```

Without the `on` constraint, calling `name` or `breathe()` inside the mixin would be a compile error because the mixin has no guarantee those members exist. The `on` constraint is the mechanism that makes this safe.

### Mixin Composition and Linearization Order

When multiple mixins are applied, Dart uses **C3 linearization** (the same algorithm used by Python) to build a linear method resolution order (MRO). The rule is: the class itself is checked first, then mixins are checked right to left, then the superclass chain.

For `class C extends A with M1, M2`:

```
C → M2 → M1 → A → Object
```

This means if both `M1` and `M2` define a method `foo()`, the version from `M2` wins (it is closer to `C` in the chain). There is no ambiguity — Dart always picks the rightmost mixin's implementation.

### Mixin vs Abstract Class vs Interface

| Feature | `mixin` | `abstract class` | Interface (`implements`) |
|---|---|---|---|
| Keyword | `mixin` / `with` | `abstract class` / `extends` | any class / `implements` |
| Shares implementation | ✅ Yes | ✅ Yes | ❌ No |
| Can have constructor | ❌ No | ✅ Yes | ✅ Yes |
| Multiple use | ✅ Yes | ❌ One only | ✅ Yes |
| `on` constraint | ✅ Yes | ❌ N/A | ❌ N/A |
| Instantiable | ❌ No | ❌ No | ✅ (as class) |

Choose a **mixin** when you want to share behavior across classes that don't share a common ancestor and you don't need a constructor. Choose an **abstract class** when you want to share both code and a constructor-based initialization contract. Choose an **interface** when you only need a type contract with no shared code.

### Dart 3: `mixin class`

Dart 3 introduced `mixin class` — a declaration that can be used both as a mixin (with `with`) and as a regular class (with `extends` or standalone). It must satisfy the constraints of both: no `on` clause, and it must extend `Object` directly. This is a niche feature; prefer plain `mixin` for pure mixin use cases.

---

## 💻 Code Examples

### Example 1: Basic Mixin Declaration and `with` Usage

```dart
// ── Simple mixins with no constraints ─────────────────────────────────────

mixin Printable {
  // Mixins can define concrete methods
  void printInfo() => print('${runtimeType}: ${toString()}');
}

mixin Serializable {
  // Mixins can define abstract-like methods by relying on toString()
  // or by declaring abstract members (which forces the applying class to implement them)
  Map<String, dynamic> toJson();

  String toJsonString() {
    // Calls toJson() — the applying class must provide this
    return toJson().entries.map((e) => '"${e.key}": "${e.value}"').join(', ');
  }
}

// ── A class that applies both mixins ──────────────────────────────────────
class User with Printable, Serializable {
  final String name;
  final String email;

  User(this.name, this.email);

  // Must implement toJson() because Serializable declares it as abstract-like
  // (it calls toJson() but doesn't define it — the mixin relies on the class)
  @override
  Map<String, dynamic> toJson() => {'name': name, 'email': email};

  @override
  String toString() => 'User($name, $email)';
}

class Product with Printable, Serializable {
  final String id;
  final double price;

  Product(this.id, this.price);

  @override
  Map<String, dynamic> toJson() => {'id': id, 'price': price.toString()};

  @override
  String toString() => 'Product($id, \$$price)';
}

void main() {
  final user = User('Alice', 'alice@example.com');
  final product = Product('P001', 29.99);

  user.printInfo();    // User: User(Alice, alice@example.com)
  product.printInfo(); // Product: Product(P001, $29.99)

  print(user.toJsonString());    // "name": "Alice", "email": "alice@example.com"
  print(product.toJsonString()); // "id": "P001", "price": "29.99"

  // Both User and Product are Printable — polymorphic usage
  final List<Printable> items = [user, product];
  for (final item in items) {
    item.printInfo();
  }
}
```

### Example 2: `on` Constraint — Mixin That Requires a Specific Superclass

```dart
// ── Base class that the mixin depends on ──────────────────────────────────
abstract class DatabaseEntity {
  int? id; // nullable — null means not yet persisted
  DateTime? createdAt;
  DateTime? updatedAt;

  // Abstract method — subclasses define their table name
  String get tableName;

  // Concrete method available to all entities
  bool get isPersisted => id != null;
}

// ── Mixin with `on` constraint ─────────────────────────────────────────────
// This mixin can ONLY be applied to classes that extend DatabaseEntity.
// The `on` constraint lets us safely call id, tableName, isPersisted, etc.
mixin AuditLog on DatabaseEntity {
  final List<String> _changeLog = [];

  // Safe to call tableName and id because DatabaseEntity guarantees them
  void recordChange(String field, dynamic oldValue, dynamic newValue) {
    final entry =
        '[${DateTime.now().toIso8601String()}] $tableName#${id ?? "NEW"}: '
        '$field changed from "$oldValue" to "$newValue"';
    _changeLog.add(entry);
    updatedAt = DateTime.now(); // can set updatedAt — it's on DatabaseEntity
  }

  List<String> get changeLog => List.unmodifiable(_changeLog);

  void printAuditLog() {
    if (_changeLog.isEmpty) {
      print('No changes recorded for ${tableName}#$id');
      return;
    }
    print('=== Audit Log for ${tableName}#$id ===');
    for (final entry in _changeLog) {
      print('  $entry');
    }
  }
}

mixin SoftDelete on DatabaseEntity {
  bool _deleted = false;
  DateTime? deletedAt;

  bool get isDeleted => _deleted;

  // Safe to call isPersisted because DatabaseEntity provides it
  void softDelete() {
    if (!isPersisted) {
      throw StateError('Cannot delete an unpersisted entity');
    }
    _deleted = true;
    deletedAt = DateTime.now();
    print('$tableName#$id soft-deleted at $deletedAt');
  }

  void restore() {
    _deleted = false;
    deletedAt = null;
    print('$tableName#$id restored');
  }
}

// ── Concrete entity applying both mixins ──────────────────────────────────
class UserEntity extends DatabaseEntity with AuditLog, SoftDelete {
  String _name;
  String _email;

  UserEntity(this._name, this._email);

  @override
  String get tableName => 'users';

  String get name => _name;
  set name(String value) {
    recordChange('name', _name, value); // from AuditLog mixin
    _name = value;
  }

  String get email => _email;
  set email(String value) {
    recordChange('email', _email, value);
    _email = value;
  }
}

void main() {
  final user = UserEntity('Bob', 'bob@example.com');
  user.id = 42;
  user.createdAt = DateTime.now();

  user.name = 'Robert';
  user.email = 'robert@example.com';

  user.printAuditLog();
  // === Audit Log for users#42 ===
  //   [2024-...] users#42: name changed from "Bob" to "Robert"
  //   [2024-...] users#42: email changed from "bob@example.com" to "robert@example.com"

  user.softDelete();
  // users#42 soft-deleted at ...

  print('Is deleted: ${user.isDeleted}'); // Is deleted: true
  user.restore();
  print('Is deleted: ${user.isDeleted}'); // Is deleted: false
}
```

### Example 3: Multiple Mixins, Linearization Order, Method Resolution

```dart
// ── Demonstrate linearization: class C extends A with M1, M2
// Resolution order: C → M2 → M1 → A → Object ──────────────────────────────

class Logger {
  // Base class — bottom of the chain
  String describe() => 'Logger';

  void log(String msg) => print('[Logger] $msg');
}

mixin TimestampMixin on Logger {
  // M1 — applied first (leftmost), so lower priority than M2
  @override
  String describe() => 'TimestampMixin → ${super.describe()}';

  @override
  void log(String msg) {
    // super.log() calls Logger.log() because TimestampMixin is above Logger
    super.log('[${DateTime.now().millisecondsSinceEpoch}] $msg');
  }
}

mixin PrefixMixin on Logger {
  // M2 — applied second (rightmost), so HIGHER priority than M1
  String prefix = 'APP'; // instance variable in mixin

  @override
  String describe() => 'PrefixMixin → ${super.describe()}';

  @override
  void log(String msg) {
    // super.log() calls TimestampMixin.log() (next in chain)
    // because linearization is: PrefixMixin → TimestampMixin → Logger
    super.log('[$prefix] $msg');
  }
}

// ── Class applying both mixins ─────────────────────────────────────────────
// Linearization: AppLogger → PrefixMixin → TimestampMixin → Logger → Object
class AppLogger extends Logger with TimestampMixin, PrefixMixin {
  @override
  String describe() => 'AppLogger → ${super.describe()}';
}

// ── Class that overrides one mixin's behavior ──────────────────────────────
class SilentLogger extends Logger with TimestampMixin, PrefixMixin {
  @override
  void log(String msg) {
    // Completely overrides the mixin chain — nothing is printed
    // (useful for test environments)
  }

  @override
  String describe() => 'SilentLogger (suppresses output)';
}

void main() {
  final app = AppLogger();
  app.prefix = 'MYAPP';

  // Calling describe() walks the full chain:
  // AppLogger.describe → PrefixMixin.describe → TimestampMixin.describe → Logger.describe
  print(app.describe());
  // AppLogger → PrefixMixin → TimestampMixin → Logger

  // Calling log() walks the chain:
  // AppLogger inherits PrefixMixin.log (rightmost wins)
  // PrefixMixin.log calls super.log → TimestampMixin.log
  // TimestampMixin.log calls super.log → Logger.log
  app.log('Server started');
  // [Logger] [1234567890] [MYAPP] Server started
  // (innermost Logger.log prints; outer layers prepend their parts)

  print('---');

  final silent = SilentLogger();
  silent.log('This is suppressed'); // prints nothing
  print(silent.describe()); // SilentLogger (suppresses output)

  // ── Type checks ───────────────────────────────────────────────────────
  print(app is Logger);        // true — AppLogger extends Logger
  print(app is TimestampMixin); // true — mixin types are checkable
  print(app is PrefixMixin);    // true
}
```

---

## ⚠️ Common Pitfalls

1. **Applying a mixin to a class that doesn't satisfy the `on` constraint.** If a mixin declares `on Animal`, you cannot apply it to a class that doesn't extend `Animal`. The compiler will report: "The mixin 'X' can't be applied to 'Y' because 'Y' doesn't implement 'Animal'." Always check the `on` clause before applying a mixin.

2. **Assuming the leftmost mixin wins in a conflict.** Dart's linearization puts the **rightmost** mixin closest to the class, so it wins. `class C with M1, M2` means `M2`'s methods take precedence over `M1`'s. This is the opposite of what many developers expect coming from other languages.

3. **Trying to give a mixin a generative constructor.** `mixin Foo { Foo(); }` is a compile error. Mixins cannot have generative constructors because they are never instantiated directly. If you need initialization logic, use a method (e.g., `void init()`) or use `mixin class` (Dart 3) if you truly need both mixin and class behavior.

4. **Calling `super` in a mixin without an `on` constraint and expecting a specific method.** Without `on`, `super` in a mixin refers to `Object`. Calling `super.someMethod()` where `someMethod` is not on `Object` is a compile error. Use the `on` constraint to guarantee the supertype has the method you need.

5. **Confusing `mixin` with `abstract class` when you need a constructor.** If your shared behavior requires initialization (e.g., setting up a controller in a constructor), a mixin is the wrong tool — use an abstract class with a constructor instead. Mixins are for stateless or lazily-initialized shared behavior.

---

## ❓ Interview Questions

### Q1: What is a mixin in Dart and how does it differ from a class?

**Answer:** A mixin is a way to reuse code across multiple class hierarchies without inheritance. It is declared with the `mixin` keyword and applied with `with`. Unlike a class, a mixin cannot be instantiated directly and cannot have generative constructors. Unlike `extends` (which allows only one superclass), `with` allows multiple mixins to be applied simultaneously. The key distinction is that mixins provide **horizontal code reuse** — sharing behavior across classes that don't share a common ancestor — while `extends` provides **vertical code reuse** through a parent–child hierarchy. A class can use `extends`, `implements`, and `with` together, giving Dart a flexible composition model.

### Q2: What is the `on` constraint in a mixin declaration?

**Answer:** The `on` constraint (e.g., `mixin Foo on Bar`) restricts which classes the mixin can be applied to — only classes that extend or implement `Bar` can use `with Foo`. This is useful when the mixin's implementation needs to call methods or access fields that are guaranteed to exist on the target class. Without `on`, the mixin's `super` refers to `Object`, so only `Object` members are accessible. With `on Bar`, the mixin can safely call any member of `Bar` via `super` or directly, because the constraint guarantees the applying class has those members. It is essentially a way to declare a mixin's dependencies on its host class.

### Q3: How does Dart resolve method conflicts when multiple mixins define the same method?

**Answer:** Dart uses C3 linearization to build a deterministic method resolution order (MRO). For `class C extends A with M1, M2`, the order is `C → M2 → M1 → A → Object`. The **rightmost** mixin in the `with` clause is closest to the class and therefore wins when multiple mixins define the same method. There is no ambiguity — Dart always picks the first match walking left from the class in the MRO. Each mixin can call `super.method()` to delegate to the next in the chain, enabling cooperative method composition where every mixin in the chain contributes to the final behavior.

### Q4: Can a mixin have a constructor? Can it have instance variables?

**Answer:** A pure `mixin` **cannot** have generative constructors (constructors that create instances), because mixins are never instantiated directly — they are always applied to a class. Attempting to declare `mixin Foo { Foo(); }` is a compile error. However, mixins **can** have instance variables (fields), and those fields are mixed into the applying class just like methods are. Dart 3 introduced `mixin class`, which can have constructors and be used both as a mixin and as a standalone class, but it comes with restrictions (no `on` clause, must extend `Object` directly). For most use cases, plain `mixin` with instance variables and no constructor is the right choice.

### Q5: When would you choose a mixin over an abstract class?

**Answer:** Choose a mixin when you want to share behavior across classes that don't share a common ancestor and when you don't need constructor-based initialization. Mixins excel at **cross-cutting concerns** — logging, serialization, validation, animation behavior in Flutter — that apply to many unrelated classes. Choose an abstract class when the shared behavior requires a constructor (e.g., initializing a controller or registering a listener in the constructor), when you want to enforce an IS-A relationship, or when you need to share state that must be initialized at construction time. In Flutter, mixins are heavily used for `TickerProviderStateMixin`, `AutomaticKeepAliveClientMixin`, and similar patterns that add behavior to `State` subclasses without requiring a new superclass.

---

## 🔑 Key Takeaways

- A `mixin` provides horizontal code reuse — shared behavior across unrelated class hierarchies — without inheritance.
- Apply mixins with `with`; multiple mixins are allowed and listed left to right.
- The `on` constraint restricts a mixin to classes that extend/implement a specific type, enabling safe access to that type's members.
- Dart uses C3 linearization: the rightmost mixin in `with M1, M2` wins method conflicts; `super` calls walk the chain right-to-left.
- Mixins cannot have generative constructors but can have instance variables and concrete methods.
- Use `mixin` for cross-cutting concerns (logging, serialization, animation); use `abstract class` when you need a constructor or a strict IS-A relationship.
- In Dart 3, `mixin class` allows a declaration to serve as both a mixin and a class, but plain `mixin` is preferred for pure mixin use cases.

---

## 🔗 Related Topics

- **Previous:** [Day 09 — Inheritance, Abstract Classes & Interfaces](./Day-09-Inheritance-Abstract-Interfaces.md)
- **Next:** [Day 11 — Generics](./Day-11-Generics.md)
- **Day 18:** [Dart 3 Features — Sealed Classes & Class Modifiers](../Week-3-Async-Advanced/Day-18-Dart3-Features.md) — `mixin class`, `base`, `interface`, `sealed` modifiers
- **Dart Cheatsheet:** [Mixin syntax quick reference](../Cheatsheets/Dart-Cheatsheet.md)
- **Cross-plan:** [JavaScript Prototypes & Inheritance](../../JavaScript/30-Day-JS-Mastery/Week-2-Intermediate/Day-08-Prototypes-Inheritance.md) — compare JS prototype chain with Dart mixin linearization
