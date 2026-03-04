# Day 4: Design Patterns for Architects

## Status: ⬜ Not Started

---

## 📚 Learning Goals

## Creational Patterns

### 1. Factory Pattern
- [ ] Understand factory pattern
- [ ] Know when to use

```typescript
// Factory Pattern
interface Product {
  operation(): string;
}

class ConcreteProductA implements Product {
  operation(): string { return 'Product A'; }
}

class ConcreteProductB implements Product {
  operation(): string { return 'Product B'; }
}

class ProductFactory {
  createProduct(type: string): Product {
    switch (type) {
      case 'A': return new ConcreteProductA();
      case 'B': return new ConcreteProductB();
      default: throw new Error('Unknown type');
    }
  }
}

// Usage
const factory = new ProductFactory();
const product = factory.createProduct('A');
```

**Use When:**
- Object creation logic is complex
- Need runtime flexibility in object creation
- Want to decouple client from concrete classes

---

### 2. Abstract Factory Pattern
- [ ] Understand abstract factory
- [ ] Know difference from factory

```typescript
// Abstract Factory - Creates families of related objects
interface UIFactory {
  createButton(): Button;
  createCheckbox(): Checkbox;
}

class WindowsFactory implements UIFactory {
  createButton(): Button { return new WindowsButton(); }
  createCheckbox(): Checkbox { return new WindowsCheckbox(); }
}

class MacFactory implements UIFactory {
  createButton(): Button { return new MacButton(); }
  createCheckbox(): Checkbox { return new MacCheckbox(); }
}
```

**Use When:**
- Need to create families of related objects
- System should be independent of product creation
- Want to enforce using products from same family

---

### 3. Builder Pattern
- [ ] Understand builder pattern
- [ ] Know step-by-step construction

```typescript
class QueryBuilder {
  private query: string = '';
  
  select(columns: string[]): QueryBuilder {
    this.query += `SELECT ${columns.join(', ')}`;
    return this;
  }
  
  from(table: string): QueryBuilder {
    this.query += ` FROM ${table}`;
    return this;
  }
  
  where(condition: string): QueryBuilder {
    this.query += ` WHERE ${condition}`;
    return this;
  }
  
  build(): string {
    return this.query;
  }
}

// Usage
const query = new QueryBuilder()
  .select(['id', 'name'])
  .from('users')
  .where('active = true')
  .build();
```

**Use When:**
- Object needs multiple steps to construct
- Want immutable objects
- Need different representations of same construction

---

## Structural Patterns

### 4. Adapter Pattern
- [ ] Understand adapter pattern
- [ ] Know interface adaptation

```typescript
// Target interface (what client expects)
interface ModernPayment {
  processPayment(amount: number): void;
}

// Adaptee (legacy system)
class LegacyPaymentSystem {
  makePayment(dollars: number, cents: number) {
    console.log(`Paying $${dollars}.${cents}`);
  }
}

// Adapter
class PaymentAdapter implements ModernPayment {
  constructor(private legacy: LegacyPaymentSystem) {}
  
  processPayment(amount: number): void {
    const dollars = Math.floor(amount);
    const cents = Math.round((amount - dollars) * 100);
    this.legacy.makePayment(dollars, cents);
  }
}
```

**Use When:**
- Integrating legacy systems
- Using third-party libraries with different interfaces
- Creating reusable classes with incompatible interfaces

---

### 5. Facade Pattern
- [ ] Understand facade pattern
- [ ] Know simplification of complex systems

```typescript
// Complex subsystems
class VideoDecoder { decode(file: string) { /* ... */ } }
class AudioDecoder { decode(file: string) { /* ... */ } }
class VideoPlayer { play(video: any, audio: any) { /* ... */ } }

// Facade - Simplifies interface
class MediaFacade {
  private videoDecoder = new VideoDecoder();
  private audioDecoder = new AudioDecoder();
  private player = new VideoPlayer();
  
  playVideo(file: string) {
    const video = this.videoDecoder.decode(file);
    const audio = this.audioDecoder.decode(file);
    this.player.play(video, audio);
  }
}

// Usage - Simple!
const media = new MediaFacade();
media.playVideo('movie.mp4');
```

**Use When:**
- Simplifying complex subsystems
- Reducing coupling between clients and subsystems
- Creating entry points to subsystem layers

---

### 6. Proxy Pattern
- [ ] Understand proxy pattern
- [ ] Know different proxy types

```typescript
interface Image {
  display(): void;
}

class RealImage implements Image {
  constructor(private filename: string) {
    this.loadFromDisk();
  }
  
  private loadFromDisk() {
    console.log(`Loading ${this.filename}`);
  }
  
  display() {
    console.log(`Displaying ${this.filename}`);
  }
}

// Proxy - Lazy loading
class ImageProxy implements Image {
  private realImage: RealImage | null = null;
  
  constructor(private filename: string) {}
  
  display() {
    if (!this.realImage) {
      this.realImage = new RealImage(this.filename);
    }
    this.realImage.display();
  }
}
```

**Types:**
- **Virtual Proxy** - Lazy loading
- **Protection Proxy** - Access control
- **Remote Proxy** - Network requests
- **Caching Proxy** - Result caching

---

## Behavioral Patterns

### 7. Observer Pattern
- [ ] Understand observer pattern
- [ ] Know publish-subscribe mechanism

```typescript
interface Observer {
  update(data: any): void;
}

class Subject {
  private observers: Observer[] = [];
  
  subscribe(observer: Observer) {
    this.observers.push(observer);
  }
  
  unsubscribe(observer: Observer) {
    this.observers = this.observers.filter(o => o !== observer);
  }
  
  notify(data: any) {
    this.observers.forEach(o => o.update(data));
  }
}

// Usage
const subject = new Subject();
subject.subscribe({ update: (d) => console.log('Observer 1:', d) });
subject.subscribe({ update: (d) => console.log('Observer 2:', d) });
subject.notify({ event: 'data-changed' });
```

---

### 8. Strategy Pattern
- [ ] Understand strategy pattern
- [ ] Know algorithm interchangeability

```typescript
interface SortStrategy {
  sort(arr: number[]): number[];
}

class QuickSort implements SortStrategy {
  sort(arr: number[]): number[] { /* quick sort */ return arr; }
}

class MergeSort implements SortStrategy {
  sort(arr: number[]): number[] { /* merge sort */ return arr; }
}

class Sorter {
  constructor(private strategy: SortStrategy) {}
  
  setStrategy(strategy: SortStrategy) {
    this.strategy = strategy;
  }
  
  sort(arr: number[]): number[] {
    return this.strategy.sort(arr);
  }
}
```

---

### 9. Mediator Pattern
- [ ] Understand mediator pattern
- [ ] Know component decoupling

```typescript
interface Mediator {
  notify(sender: object, event: string): void;
}

class ChatMediator implements Mediator {
  private users: User[] = [];
  
  addUser(user: User) {
    this.users.push(user);
  }
  
  notify(sender: object, event: string) {
    this.users
      .filter(u => u !== sender)
      .forEach(u => u.receive(event));
  }
}

class User {
  constructor(private mediator: Mediator, private name: string) {}
  
  send(message: string) {
    console.log(`${this.name} sends: ${message}`);
    this.mediator.notify(this, message);
  }
  
  receive(message: string) {
    console.log(`${this.name} received: ${message}`);
  }
}
```

---

## Advanced Architectural Patterns

### 10. CQRS (Command Query Responsibility Segregation)
- [ ] Understand CQRS pattern
- [ ] Know when to use

```
┌─────────────────────────────────────────────────────┐
│                    Application                       │
│                                                     │
│   ┌──────────────┐          ┌──────────────┐       │
│   │   Commands   │          │   Queries    │       │
│   │   (Write)    │          │   (Read)     │       │
│   └──────┬───────┘          └──────┬───────┘       │
│          │                         │               │
│   ┌──────▼───────┐          ┌──────▼───────┐       │
│   │Write Database│          │Read Database │       │
│   │(Normalized)  │   ────►  │(Denormalized)│       │
│   └──────────────┘   Sync   └──────────────┘       │
└─────────────────────────────────────────────────────┘
```

**Use When:**
- Read and write workloads are significantly different
- Need different optimization for reads vs writes
- High scalability requirements

---

### 11. Saga Pattern
- [ ] Understand distributed transactions
- [ ] Know saga types

```
Choreography Saga:
┌────────┐   Event    ┌────────┐   Event    ┌────────┐
│Service │  ──────►   │Service │  ──────►   │Service │
│   A    │            │   B    │            │   C    │
└────────┘            └────────┘            └────────┘

Orchestration Saga:
                    ┌────────────┐
                    │Orchestrator│
                    └─────┬──────┘
              ┌───────────┼───────────┐
              ▼           ▼           ▼
         ┌────────┐  ┌────────┐  ┌────────┐
         │Service │  │Service │  │Service │
         │   A    │  │   B    │  │   C    │
         └────────┘  └────────┘  └────────┘
```

**Compensating Transactions:** Each step has a compensating action for rollback.

---

### 12. Circuit Breaker Pattern
- [ ] Understand circuit breaker
- [ ] Know states and transitions

```
         ┌───────────────────────────────────┐
         │                                   │
         │        ┌──────────┐               │
    Success       │  CLOSED  │◄──── Success  │
         │        └────┬─────┘      (below   │
         │             │            threshold)
         │        Failures                   │
         │        (threshold)                │
         │             │                     │
         │             ▼                     │
         │        ┌──────────┐               │
         └────────│   OPEN   │               │
                  └────┬─────┘               │
                       │                     │
                  Timeout                    │
                       │                     │
                       ▼                     │
                  ┌──────────┐               │
                  │HALF-OPEN │───────────────┘
                  └──────────┘
                       │
                  Failure
                       │
                       ▼
                  ┌──────────┐
                  │   OPEN   │
                  └──────────┘
```

---

### 13. Retry Pattern
- [ ] Understand retry strategies

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(delay * Math.pow(2, i)); // Exponential backoff
    }
  }
  throw new Error('Max retries exceeded');
}
```

**Strategies:**
- Fixed delay
- Exponential backoff
- Exponential backoff with jitter

---

### 14. Bulkhead Pattern
- [ ] Understand isolation

```
┌─────────────────────────────────────────────────┐
│                   Application                    │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  Thread Pool │  │  Thread Pool │            │
│  │   (API A)    │  │   (API B)    │            │
│  │   10 threads │  │   10 threads │            │
│  └──────────────┘  └──────────────┘            │
│         │                  │                    │
│         ▼                  ▼                    │
│  ┌──────────────┐  ┌──────────────┐            │
│  │   Service A  │  │   Service B  │            │
│  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────┘
```

**Isolates failures** - If Service A fails, it doesn't consume all resources.

---

## 🎯 Practice Task

### Implement Key Patterns

**Instructions:**
1. Pick 3 patterns from this list
2. Implement working examples
3. Document use cases

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] Design Patterns - Gang of Four
- [ ] Head First Design Patterns
- [ ] [Refactoring Guru](https://refactoring.guru/design-patterns)

---

## ✅ Completion Checklist

- [ ] Understood creational patterns
- [ ] Understood structural patterns
- [ ] Understood behavioral patterns
- [ ] Mastered advanced patterns (CQRS, Saga, Circuit Breaker)
- [ ] Completed practice implementations

**Date Completed:** _____________
