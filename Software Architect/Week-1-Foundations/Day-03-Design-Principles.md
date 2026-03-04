# Day 3: Design Principles (Deep Dive)

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. SOLID Principles
- [ ] Master all five SOLID principles
- [ ] Understand how to apply in real projects

#### S - Single Responsibility Principle (SRP)
> A class should have only one reason to change.

```typescript
// ❌ Bad - Multiple responsibilities
class UserService {
  createUser(user: User) { /* ... */ }
  sendEmail(user: User) { /* ... */ }
  generateReport(user: User) { /* ... */ }
}

// ✅ Good - Single responsibility
class UserService {
  createUser(user: User) { /* ... */ }
}

class EmailService {
  sendEmail(user: User) { /* ... */ }
}

class ReportService {
  generateReport(user: User) { /* ... */ }
}
```

#### O - Open/Closed Principle (OCP)
> Software entities should be open for extension but closed for modification.

```typescript
// ❌ Bad - Modifying existing code
class PaymentProcessor {
  process(payment: Payment) {
    if (payment.type === 'credit') { /* ... */ }
    else if (payment.type === 'debit') { /* ... */ }
    else if (payment.type === 'crypto') { /* ... */ }  // Added later
  }
}

// ✅ Good - Open for extension
interface PaymentStrategy {
  process(payment: Payment): void;
}

class CreditPayment implements PaymentStrategy { /* ... */ }
class DebitPayment implements PaymentStrategy { /* ... */ }
class CryptoPayment implements PaymentStrategy { /* ... */ }  // Easy to add
```

#### L - Liskov Substitution Principle (LSP)
> Objects of a superclass should be replaceable with objects of a subclass.

```typescript
// ❌ Bad - Violates LSP
class Rectangle {
  setWidth(w: number) { this.width = w; }
  setHeight(h: number) { this.height = h; }
}

class Square extends Rectangle {
  setWidth(w: number) { this.width = this.height = w; }  // Breaks expectation
  setHeight(h: number) { this.width = this.height = h; } // Breaks expectation
}

// ✅ Good - Proper abstraction
interface Shape {
  getArea(): number;
}

class Rectangle implements Shape { /* ... */ }
class Square implements Shape { /* ... */ }
```

#### I - Interface Segregation Principle (ISP)
> Many client-specific interfaces are better than one general-purpose interface.

```typescript
// ❌ Bad - Fat interface
interface Worker {
  work(): void;
  eat(): void;
  sleep(): void;
}

// Robot can't eat or sleep!
class Robot implements Worker {
  work() { /* ... */ }
  eat() { throw new Error(''); }  // Forced implementation
  sleep() { throw new Error(''); }
}

// ✅ Good - Segregated interfaces
interface Workable { work(): void; }
interface Eatable { eat(): void; }
interface Sleepable { sleep(): void; }

class Human implements Workable, Eatable, Sleepable { /* ... */ }
class Robot implements Workable { /* ... */ }
```

#### D - Dependency Inversion Principle (DIP)
> Depend on abstractions, not concretions.

```typescript
// ❌ Bad - Direct dependency
class OrderService {
  private mysqlDB = new MySQLDatabase();  // Concrete dependency
  
  save(order: Order) {
    this.mysqlDB.save(order);
  }
}

// ✅ Good - Dependency inversion
interface Database {
  save(entity: any): void;
}

class OrderService {
  constructor(private db: Database) {}  // Abstraction
  
  save(order: Order) {
    this.db.save(order);
  }
}
```

---

### 2. DRY - Don't Repeat Yourself
- [ ] Understand DRY principle
- [ ] Know when NOT to apply DRY

> Every piece of knowledge must have a single, unambiguous representation.

**When NOT to apply DRY:**
- When abstractions lead to wrong couplings
- When contexts are different (coincidental duplication)
- When it reduces readability

---

### 3. KISS - Keep It Simple, Stupid
- [ ] Understand simplicity in design

> Most systems work best if they are kept simple rather than made complicated.

**Guidelines:**
- Avoid over-engineering
- Choose boring technology when possible
- Write readable code over clever code

---

### 4. YAGNI - You Aren't Gonna Need It
- [ ] Understand when to defer decisions

> Don't implement something until it's necessary.

**Benefits:**
- Reduces complexity
- Faster delivery
- Less code to maintain

---

### 5. GRASP Principles
- [ ] Learn General Responsibility Assignment Software Patterns

| Principle | Description |
|-----------|-------------|
| **Information Expert** | Assign responsibility to the class with the most info |
| **Creator** | B creates A if B contains, aggregates, or uses A |
| **Controller** | Assign responsibility of system events to a non-UI class |
| **Low Coupling** | Minimize dependencies between classes |
| **High Cohesion** | Keep related responsibilities together |
| **Polymorphism** | Use polymorphism for type-based variations |
| **Pure Fabrication** | Create artificial classes for cohesion |
| **Indirection** | Assign responsibility to intermediate object |
| **Protected Variations** | Wrap unstable code behind stable interfaces |

---

### 6. Separation of Concerns (SoC)
- [ ] Understand modular design

> Divide program into distinct sections, each addressing a separate concern.

```
┌─────────────────────────────────────────────────────┐
│                   Application                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐    │
│  │    UI      │  │  Business  │  │    Data    │    │
│  │  Concern   │  │   Logic    │  │   Access   │    │
│  └────────────┘  └────────────┘  └────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## 📘 Advanced Principles

### High Cohesion vs Low Coupling

```
High Cohesion (Good)          Low Cohesion (Bad)
┌─────────────────┐           ┌─────────────────┐
│ User Module     │           │ Utils Module    │
│ - createUser    │           │ - createUser    │
│ - updateUser    │           │ - sendEmail     │
│ - deleteUser    │           │ - formatDate    │
│ - getUser       │           │ - calculateTax  │
└─────────────────┘           └─────────────────┘

Low Coupling (Good)           High Coupling (Bad)
┌─────┐    ┌─────┐            ┌─────┐◄──►┌─────┐
│  A  │───►│  B  │            │  A  │◄──►│  B  │
└─────┘    └─────┘            └──┬──┘    └──┬──┘
     via interface                  ▲        ▲
                                   └─────┬───┘
                                         ▼
                                      ┌─────┐
                                      │  C  │
                                      └─────┘
```

### Composition Over Inheritance

```typescript
// ❌ Inheritance - Tight coupling
class Dog extends Animal {
  bark() { /* ... */ }
}

// ✅ Composition - Flexible
class Dog {
  constructor(
    private movement: WalkBehavior,
    private sound: BarkBehavior
  ) {}
  
  move() { this.movement.walk(); }
  makeSound() { this.sound.bark(); }
}
```

**Why Composition?**
- More flexible
- Avoids inheritance hierarchies
- Easy to change behavior at runtime
- Better testability

---

## 🎯 Practice Task

### Apply SOLID to Your Code

**Instructions:**
1. Take an existing service class
2. Identify SOLID violations
3. Refactor to follow SOLID
4. Document before/after

**Template:**

```markdown
## Class: [ClassName]

### Before Refactoring
[Code snippet showing violations]

### Violations Identified
- [ ] SRP: [Description]
- [ ] OCP: [Description]
- [ ] LSP: [Description]
- [ ] ISP: [Description]
- [ ] DIP: [Description]

### After Refactoring
[Refactored code]

### Benefits Achieved
1. [Benefit 1]
2. [Benefit 2]
```

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] Clean Code - Robert C. Martin
- [ ] Head First Design Patterns
- [ ] [SOLID Principles Examples](https://solidprinciples.com/)

---

## ✅ Completion Checklist

- [ ] Mastered SOLID principles with examples
- [ ] Understood DRY, KISS, YAGNI
- [ ] Learned GRASP principles
- [ ] Know cohesion vs coupling
- [ ] Understand composition over inheritance
- [ ] Completed practice task

**Date Completed:** _____________
