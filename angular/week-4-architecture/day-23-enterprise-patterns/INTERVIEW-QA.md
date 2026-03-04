# Day 23: Enterprise Patterns - Interview Questions & Answers

## Basic Level

### Q1: What is the Repository pattern?

**Answer:**
Repository abstracts data access, providing a clean API for business logic:

```typescript
// Abstract interface
abstract class UserRepository {
  abstract findAll(): Observable<User[]>;
  abstract findById(id: string): Observable<User>;
  abstract save(user: User): Observable<User>;
  abstract delete(id: string): Observable<void>;
}

// HTTP implementation
@Injectable()
class HttpUserRepository extends UserRepository {
  private http = inject(HttpClient);
  
  findAll(): Observable<User[]> {
    return this.http.get<User[]>('/api/users');
  }
  
  findById(id: string): Observable<User> {
    return this.http.get<User>(`/api/users/${id}`);
  }
  
  save(user: User): Observable<User> {
    return this.http.post<User>('/api/users', user);
  }
  
  delete(id: string): Observable<void> {
    return this.http.delete<void>(`/api/users/${id}`);
  }
}

// Provider setup
providers: [
  { provide: UserRepository, useClass: HttpUserRepository }
]
```

**Benefits:**
- Business logic doesn't know about HTTP/database
- Easy to mock for testing
- Can swap implementations (HTTP, localStorage, mock)

---

### Q2: What is CQRS?

**Answer:**
**Command Query Responsibility Segregation** separates read and write operations:

```typescript
// COMMAND (Write) - CreateUserCommand
@Injectable()
class CreateUserHandler {
  private repo = inject(UserRepository);

  execute(name: string, email: string): Observable<User> {
    const user = new User(generateId(), name, email);
    return this.repo.save(user);
  }
}

// QUERY (Read) - GetUsersQuery
@Injectable()
class GetUsersHandler {
  private readRepo = inject(UserReadRepository);

  execute(page: number, size: number): Observable<User[]> {
    return this.readRepo.findPaginated(page, size);
  }
}

// Facade combines both
@Injectable()
class UserFacade {
  private createHandler = inject(CreateUserHandler);
  private getUsersHandler = inject(GetUsersHandler);

  // Command
  createUser(name: string, email: string) {
    return this.createHandler.execute(name, email);
  }

  // Query
  getUsers(page: number, size: number) {
    return this.getUsersHandler.execute(page, size);
  }
}
```

**Benefits:**
- Optimize reads and writes separately
- Scale read/write sides independently
- Different models for reading vs writing

---

### Q3: What is the Strategy pattern?

**Answer:**
Strategy defines interchangeable algorithms:

```typescript
// Strategy interface
interface PaymentStrategy {
  pay(amount: number): Observable<PaymentResult>;
}

// Concrete strategies
@Injectable()
class CreditCardPayment implements PaymentStrategy {
  pay(amount: number): Observable<PaymentResult> {
    return this.http.post('/api/payments/credit', { amount });
  }
}

@Injectable()
class PayPalPayment implements PaymentStrategy {
  pay(amount: number): Observable<PaymentResult> {
    return this.http.post('/api/payments/paypal', { amount });
  }
}

// Context
@Injectable()
class PaymentService {
  private strategies = new Map<string, PaymentStrategy>();

  constructor(creditCard: CreditCardPayment, paypal: PayPalPayment) {
    this.strategies.set('credit', creditCard);
    this.strategies.set('paypal', paypal);
  }

  processPayment(method: string, amount: number): Observable<PaymentResult> {
    const strategy = this.strategies.get(method);
    if (!strategy) throw new Error('Unknown payment method');
    return strategy.pay(amount);
  }
}
```

---

## Intermediate Level

### Q4: Explain the Specification pattern

**Answer:**
Specification encapsulates business rules that can be combined:

```typescript
// Base specification
interface Specification<T> {
  isSatisfiedBy(item: T): boolean;
  and(other: Specification<T>): Specification<T>;
  or(other: Specification<T>): Specification<T>;
}

// Product specifications
class InStockSpec implements Specification<Product> {
  isSatisfiedBy(product: Product): boolean {
    return product.stock > 0;
  }
  
  and(other: Specification<Product>): Specification<Product> {
    return new AndSpec(this, other);
  }
  
  or(other: Specification<Product>): Specification<Product> {
    return new OrSpec(this, other);
  }
}

class PriceRangeSpec implements Specification<Product> {
  constructor(private min: number, private max: number) {}
  
  isSatisfiedBy(product: Product): boolean {
    return product.price >= this.min && product.price <= this.max;
  }
  // ... and/or methods
}

class CategorySpec implements Specification<Product> {
  constructor(private category: string) {}
  
  isSatisfiedBy(product: Product): boolean {
    return product.category === this.category;
  }
  // ... and/or methods
}

// Usage - composable business rules
const affordableElectronicsInStock = new InStockSpec()
  .and(new PriceRangeSpec(0, 500))
  .and(new CategorySpec('electronics'));

const filtered = products.filter(p => affordableElectronicsInStock.isSatisfiedBy(p));
```

**Benefits:**
- Reusable business rules
- Composable with and/or
- Self-documenting code

---

### Q5: How do you implement Event-Driven Architecture?

**Answer:**
```typescript
// Event definitions
interface DomainEvent {
  timestamp: Date;
  type: string;
}

class OrderPlacedEvent implements DomainEvent {
  type = 'OrderPlaced';
  timestamp = new Date();
  
  constructor(public orderId: string, public total: number) {}
}

// Event Bus
@Injectable({ providedIn: 'root' })
class EventBus {
  private events$ = new Subject<DomainEvent>();

  publish(event: DomainEvent): void {
    this.events$.next(event);
  }

  on<T extends DomainEvent>(eventType: string): Observable<T> {
    return this.events$.pipe(
      filter(event => event.type === eventType)
    ) as Observable<T>;
  }
}

// Publisher
@Injectable()
class OrderService {
  private eventBus = inject(EventBus);
  
  placeOrder(items: OrderItem[]): Observable<Order> {
    return this.orderRepo.save(order).pipe(
      tap(savedOrder => {
        this.eventBus.publish(new OrderPlacedEvent(savedOrder.id, savedOrder.total));
      })
    );
  }
}

// Subscriber
@Injectable({ providedIn: 'root' })
class InventoryHandler {
  private eventBus = inject(EventBus);
  
  constructor() {
    this.eventBus.on<OrderPlacedEvent>('OrderPlaced').subscribe(event => {
      this.updateInventory(event.orderId);
    });
  }
}
```

---

### Q6: What is the Unit of Work pattern?

**Answer:**
Unit of Work tracks changes and commits them as a transaction:

```typescript
@Injectable()
class UnitOfWork {
  private newEntities: any[] = [];
  private dirtyEntities: any[] = [];
  private deletedEntities: any[] = [];

  registerNew(entity: any): void {
    this.newEntities.push(entity);
  }

  registerDirty(entity: any): void {
    if (!this.newEntities.includes(entity)) {
      this.dirtyEntities.push(entity);
    }
  }

  registerDeleted(entity: any): void {
    this.newEntities = this.newEntities.filter(e => e !== entity);
    this.dirtyEntities = this.dirtyEntities.filter(e => e !== entity);
    this.deletedEntities.push(entity);
  }

  commit(): Observable<void> {
    // Persist all changes atomically
    const operations = [
      ...this.newEntities.map(e => this.repo.create(e)),
      ...this.dirtyEntities.map(e => this.repo.update(e)),
      ...this.deletedEntities.map(e => this.repo.delete(e))
    ];

    return forkJoin(operations).pipe(
      map(() => this.clear())
    );
  }

  rollback(): void {
    this.clear();
  }

  private clear(): void {
    this.newEntities = [];
    this.dirtyEntities = [];
    this.deletedEntities = [];
  }
}

// Usage
@Injectable()
class OrderProcessingService {
  private uow = inject(UnitOfWork);

  processOrder(order: Order): Observable<void> {
    this.uow.registerNew(order);
    
    order.items.forEach(item => {
      const inventory = this.getInventory(item.productId);
      inventory.reduce(item.quantity);
      this.uow.registerDirty(inventory);
    });

    return this.uow.commit();  // All or nothing
  }
}
```

---

## Advanced Level

### Q7: How do you implement Domain-Driven Design in Angular?

**Answer:**

**1. Domain Entities:**
```typescript
// Rich domain model with business logic
class Order {
  constructor(
    public readonly id: string,
    private _items: OrderItem[],
    private _status: OrderStatus
  ) {}

  get items(): readonly OrderItem[] {
    return [...this._items];
  }

  get total(): number {
    return this._items.reduce((sum, item) => sum + item.subtotal, 0);
  }

  addItem(product: Product, quantity: number): void {
    if (this._status !== 'draft') {
      throw new Error('Cannot modify non-draft order');
    }
    this._items.push(new OrderItem(product, quantity));
  }

  submit(): void {
    if (this._items.length === 0) {
      throw new Error('Cannot submit empty order');
    }
    this._status = 'submitted';
  }

  canBeCancelled(): boolean {
    return ['draft', 'submitted'].includes(this._status);
  }
}
```

**2. Value Objects:**
```typescript
class Money {
  constructor(
    public readonly amount: number,
    public readonly currency: string
  ) {
    if (amount < 0) throw new Error('Amount cannot be negative');
  }

  add(other: Money): Money {
    if (this.currency !== other.currency) {
      throw new Error('Currency mismatch');
    }
    return new Money(this.amount + other.amount, this.currency);
  }

  equals(other: Money): boolean {
    return this.amount === other.amount && this.currency === other.currency;
  }
}
```

**3. Domain Services:**
```typescript
@Injectable()
class OrderDomainService {
  calculateDiscount(order: Order, customer: Customer): Money {
    let discount = 0;
    
    if (customer.isVIP) {
      discount += order.total * 0.1;
    }
    
    if (order.items.length > 10) {
      discount += order.total * 0.05;
    }

    return new Money(discount, order.currency);
  }
}
```

---

### Q8: How do you handle cross-cutting concerns with patterns?

**Answer:**

**1. Decorator Pattern for logging:**
```typescript
// Base service
@Injectable()
class ProductService {
  getProducts(): Observable<Product[]> {
    return this.http.get<Product[]>('/api/products');
  }
}

// Logging decorator
@Injectable()
class LoggingProductService extends ProductService {
  private logger = inject(LoggerService);
  private wrapped = inject(ProductService);

  override getProducts(): Observable<Product[]> {
    this.logger.log('Fetching products...');
    return this.wrapped.getProducts().pipe(
      tap(products => this.logger.log(`Fetched ${products.length} products`))
    );
  }
}
```

**2. Chain of Responsibility for validation:**
```typescript
interface ValidationHandler<T> {
  setNext(handler: ValidationHandler<T>): ValidationHandler<T>;
  validate(data: T): ValidationResult;
}

class RequiredFieldsHandler implements ValidationHandler<Order> {
  private next?: ValidationHandler<Order>;

  setNext(handler: ValidationHandler<Order>): ValidationHandler<Order> {
    this.next = handler;
    return handler;
  }

  validate(order: Order): ValidationResult {
    if (!order.customerId) {
      return { valid: false, error: 'Customer required' };
    }
    return this.next?.validate(order) ?? { valid: true };
  }
}

class StockAvailabilityHandler implements ValidationHandler<Order> {
  // Similar implementation
}

// Usage
const handler = new RequiredFieldsHandler();
handler.setNext(new StockAvailabilityHandler());

const result = handler.validate(order);
```

---

## Quick Reference

```
Enterprise Patterns:
────────────────────
Repository     - Abstract data access
Unit of Work   - Transaction management
Specification  - Composable business rules
CQRS           - Separate read/write
Strategy       - Interchangeable algorithms
Event-Driven   - Loose coupling via events
Decorator      - Add behavior dynamically
Chain of Resp. - Sequential processing

Pattern Selection:
──────────────────
Multiple data sources     → Repository
Complex transactions      → Unit of Work
Complex filtering         → Specification
Read-heavy with scaling   → CQRS
Multiple algorithms       → Strategy
Cross-feature comms       → Events
Feature toggles           → Decorator
Sequential validation     → Chain of Resp.

DDD Building Blocks:
────────────────────
Entity          - Has identity, mutable state
Value Object    - No identity, immutable
Aggregate       - Consistency boundary
Repository      - Persistence abstraction
Domain Service  - Stateless domain logic
Domain Event    - Something that happened
```
