# Day 23: Enterprise Patterns

## Overview

Enterprise patterns help build maintainable, scalable applications with clear separation of concerns and testable code.

---

## Repository Pattern

Abstracts data access, allowing business logic to remain independent of data sources.

```typescript
// Abstract repository interface
export abstract class UserRepository {
  abstract findAll(): Observable<User[]>;
  abstract findById(id: string): Observable<User>;
  abstract save(user: User): Observable<User>;
  abstract delete(id: string): Observable<void>;
}

// HTTP implementation
@Injectable()
export class HttpUserRepository extends UserRepository {
  private http = inject(HttpClient);
  private apiUrl = '/api/users';

  findAll(): Observable<User[]> {
    return this.http.get<UserDto[]>(this.apiUrl).pipe(
      map(dtos => dtos.map(dto => this.toDomain(dto)))
    );
  }

  findById(id: string): Observable<User> {
    return this.http.get<UserDto>(`${this.apiUrl}/${id}`).pipe(
      map(dto => this.toDomain(dto))
    );
  }

  save(user: User): Observable<User> {
    const dto = this.toDto(user);
    return user.id
      ? this.http.put<UserDto>(`${this.apiUrl}/${user.id}`, dto).pipe(map(this.toDomain))
      : this.http.post<UserDto>(this.apiUrl, dto).pipe(map(this.toDomain));
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }

  private toDomain(dto: UserDto): User {
    return new User(dto.id, dto.name, dto.email, dto.role);
  }

  private toDto(user: User): UserDto {
    return { id: user.id, name: user.name, email: user.email, role: user.role };
  }
}

// Mock implementation for testing
@Injectable()
export class MockUserRepository extends UserRepository {
  private users = signal<User[]>([
    new User('1', 'John', 'john@example.com', 'admin'),
    new User('2', 'Jane', 'jane@example.com', 'user')
  ]);

  findAll(): Observable<User[]> {
    return of(this.users());
  }

  findById(id: string): Observable<User> {
    const user = this.users().find(u => u.id === id);
    return user ? of(user) : throwError(() => new Error('Not found'));
  }

  save(user: User): Observable<User> {
    this.users.update(users => [...users, user]);
    return of(user);
  }

  delete(id: string): Observable<void> {
    this.users.update(users => users.filter(u => u.id !== id));
    return of(void 0);
  }
}

// Provider configuration
export const appConfig: ApplicationConfig = {
  providers: [
    {
      provide: UserRepository,
      useClass: environment.production ? HttpUserRepository : MockUserRepository
    }
  ]
};
```

---

## Unit of Work Pattern

Tracks changes to entities and persists them as a single transaction.

```typescript
interface UnitOfWork {
  registerNew<T>(entity: T, repository: Repository<T>): void;
  registerDirty<T>(entity: T, repository: Repository<T>): void;
  registerDeleted<T>(entity: T, repository: Repository<T>): void;
  commit(): Observable<void>;
  rollback(): void;
}

@Injectable()
export class EntityUnitOfWork implements UnitOfWork {
  private newEntities: Map<any, Repository<any>> = new Map();
  private dirtyEntities: Map<any, Repository<any>> = new Map();
  private deletedEntities: Map<any, Repository<any>> = new Map();

  registerNew<T>(entity: T, repository: Repository<T>): void {
    this.newEntities.set(entity, repository);
  }

  registerDirty<T>(entity: T, repository: Repository<T>): void {
    if (!this.newEntities.has(entity)) {
      this.dirtyEntities.set(entity, repository);
    }
  }

  registerDeleted<T>(entity: T, repository: Repository<T>): void {
    if (this.newEntities.has(entity)) {
      this.newEntities.delete(entity);
      return;
    }
    this.dirtyEntities.delete(entity);
    this.deletedEntities.set(entity, repository);
  }

  commit(): Observable<void> {
    const operations: Observable<any>[] = [];

    this.newEntities.forEach((repo, entity) => {
      operations.push(repo.save(entity));
    });

    this.dirtyEntities.forEach((repo, entity) => {
      operations.push(repo.save(entity));
    });

    this.deletedEntities.forEach((repo, entity) => {
      operations.push(repo.delete(entity.id));
    });

    return forkJoin(operations).pipe(
      map(() => {
        this.clear();
      })
    );
  }

  rollback(): void {
    this.clear();
  }

  private clear(): void {
    this.newEntities.clear();
    this.dirtyEntities.clear();
    this.deletedEntities.clear();
  }
}

// Usage
@Injectable()
export class OrderService {
  private orderRepo = inject(OrderRepository);
  private inventoryRepo = inject(InventoryRepository);
  private unitOfWork = inject(EntityUnitOfWork);

  processOrder(order: Order): Observable<void> {
    // Create order
    this.unitOfWork.registerNew(order, this.orderRepo);

    // Update inventory for each item
    order.items.forEach(item => {
      const inventory = this.getInventory(item.productId);
      inventory.quantity -= item.quantity;
      this.unitOfWork.registerDirty(inventory, this.inventoryRepo);
    });

    // Commit all changes atomically
    return this.unitOfWork.commit();
  }
}
```

---

## Specification Pattern

Encapsulates business rules as reusable, composable specifications.

```typescript
// Base specification
interface Specification<T> {
  isSatisfiedBy(candidate: T): boolean;
  and(other: Specification<T>): Specification<T>;
  or(other: Specification<T>): Specification<T>;
  not(): Specification<T>;
}

abstract class CompositeSpecification<T> implements Specification<T> {
  abstract isSatisfiedBy(candidate: T): boolean;

  and(other: Specification<T>): Specification<T> {
    return new AndSpecification(this, other);
  }

  or(other: Specification<T>): Specification<T> {
    return new OrSpecification(this, other);
  }

  not(): Specification<T> {
    return new NotSpecification(this);
  }
}

class AndSpecification<T> extends CompositeSpecification<T> {
  constructor(private left: Specification<T>, private right: Specification<T>) {
    super();
  }

  isSatisfiedBy(candidate: T): boolean {
    return this.left.isSatisfiedBy(candidate) && this.right.isSatisfiedBy(candidate);
  }
}

class OrSpecification<T> extends CompositeSpecification<T> {
  constructor(private left: Specification<T>, private right: Specification<T>) {
    super();
  }

  isSatisfiedBy(candidate: T): boolean {
    return this.left.isSatisfiedBy(candidate) || this.right.isSatisfiedBy(candidate);
  }
}

class NotSpecification<T> extends CompositeSpecification<T> {
  constructor(private spec: Specification<T>) {
    super();
  }

  isSatisfiedBy(candidate: T): boolean {
    return !this.spec.isSatisfiedBy(candidate);
  }
}

// Domain specifications
class IsActiveUser extends CompositeSpecification<User> {
  isSatisfiedBy(user: User): boolean {
    return user.status === 'active';
  }
}

class HasRole extends CompositeSpecification<User> {
  constructor(private role: string) {
    super();
  }

  isSatisfiedBy(user: User): boolean {
    return user.roles.includes(this.role);
  }
}

class MinimumAge extends CompositeSpecification<User> {
  constructor(private age: number) {
    super();
  }

  isSatisfiedBy(user: User): boolean {
    return this.calculateAge(user.birthDate) >= this.age;
  }

  private calculateAge(birthDate: Date): number {
    // Age calculation logic
    return 25;
  }
}

// Usage
@Injectable()
export class UserQueryService {
  private userRepo = inject(UserRepository);

  getEligibleAdmins(): Observable<User[]> {
    const spec = new IsActiveUser()
      .and(new HasRole('admin'))
      .and(new MinimumAge(21));

    return this.userRepo.findAll().pipe(
      map(users => users.filter(user => spec.isSatisfiedBy(user)))
    );
  }
}
```

---

## CQRS Pattern

Separates read and write operations for better scalability and optimization.

```typescript
// Commands (Write operations)
interface Command {}

// Create User Command
class CreateUserCommand implements Command {
  constructor(
    public readonly name: string,
    public readonly email: string,
    public readonly role: string
  ) {}
}

// Command Handler
@Injectable()
export class CreateUserHandler {
  private userRepo = inject(UserRepository);
  private eventBus = inject(EventBus);

  execute(command: CreateUserCommand): Observable<User> {
    const user = new User(
      generateId(),
      command.name,
      command.email,
      command.role
    );

    return this.userRepo.save(user).pipe(
      tap(savedUser => {
        this.eventBus.publish(new UserCreatedEvent(savedUser.id, savedUser.name));
      })
    );
  }
}

// Queries (Read operations)
class GetUserByIdQuery {
  constructor(public readonly id: string) {}
}

class GetActiveUsersQuery {
  constructor(
    public readonly page: number = 0,
    public readonly size: number = 10
  ) {}
}

// Query Handler
@Injectable()
export class UserQueryHandler {
  private readDb = inject(UserReadRepository);  // Optimized for reads

  getById(query: GetUserByIdQuery): Observable<UserReadModel> {
    return this.readDb.findById(query.id);
  }

  getActiveUsers(query: GetActiveUsersQuery): Observable<PagedResult<UserReadModel>> {
    return this.readDb.findActive(query.page, query.size);
  }
}

// Facade to simplify usage
@Injectable({ providedIn: 'root' })
export class UserFacade {
  private createHandler = inject(CreateUserHandler);
  private queryHandler = inject(UserQueryHandler);

  // Commands
  createUser(data: CreateUserDto): Observable<User> {
    return this.createHandler.execute(
      new CreateUserCommand(data.name, data.email, data.role)
    );
  }

  // Queries
  getUserById(id: string): Observable<UserReadModel> {
    return this.queryHandler.getById(new GetUserByIdQuery(id));
  }

  getActiveUsers(page: number, size: number): Observable<PagedResult<UserReadModel>> {
    return this.queryHandler.getActiveUsers(new GetActiveUsersQuery(page, size));
  }
}
```

---

## Event-Driven Architecture

Components communicate through events rather than direct dependencies.

```typescript
// Event definitions
interface DomainEvent {
  readonly timestamp: Date;
  readonly aggregateId: string;
}

class OrderPlacedEvent implements DomainEvent {
  readonly timestamp = new Date();
  
  constructor(
    public readonly aggregateId: string,
    public readonly items: OrderItem[],
    public readonly total: number
  ) {}
}

class PaymentReceivedEvent implements DomainEvent {
  readonly timestamp = new Date();
  
  constructor(
    public readonly aggregateId: string,
    public readonly amount: number,
    public readonly paymentMethod: string
  ) {}
}

// Event Bus
@Injectable({ providedIn: 'root' })
export class EventBus {
  private events$ = new Subject<DomainEvent>();

  publish(event: DomainEvent): void {
    this.events$.next(event);
  }

  on<T extends DomainEvent>(eventType: new (...args: any[]) => T): Observable<T> {
    return this.events$.pipe(
      filter((event): event is T => event instanceof eventType)
    );
  }
}

// Event Handlers
@Injectable({ providedIn: 'root' })
export class OrderEventHandlers {
  private eventBus = inject(EventBus);
  private inventoryService = inject(InventoryService);
  private notificationService = inject(NotificationService);

  constructor() {
    this.registerHandlers();
  }

  private registerHandlers(): void {
    // Update inventory when order is placed
    this.eventBus.on(OrderPlacedEvent).subscribe(event => {
      event.items.forEach(item => {
        this.inventoryService.reduceStock(item.productId, item.quantity);
      });
    });

    // Send notification when payment is received
    this.eventBus.on(PaymentReceivedEvent).subscribe(event => {
      this.notificationService.sendPaymentConfirmation(event.aggregateId);
    });
  }
}

// Usage in service
@Injectable()
export class OrderService {
  private orderRepo = inject(OrderRepository);
  private eventBus = inject(EventBus);

  placeOrder(items: OrderItem[]): Observable<Order> {
    const order = Order.create(items);
    
    return this.orderRepo.save(order).pipe(
      tap(savedOrder => {
        this.eventBus.publish(new OrderPlacedEvent(
          savedOrder.id,
          savedOrder.items,
          savedOrder.total
        ));
      })
    );
  }
}
```

---

## Strategy Pattern

Defines a family of algorithms and makes them interchangeable.

```typescript
// Strategy interface
interface PricingStrategy {
  calculate(basePrice: number, context: PricingContext): number;
}

// Concrete strategies
@Injectable()
export class RegularPricing implements PricingStrategy {
  calculate(basePrice: number, context: PricingContext): number {
    return basePrice;
  }
}

@Injectable()
export class DiscountPricing implements PricingStrategy {
  calculate(basePrice: number, context: PricingContext): number {
    const discount = context.discountPercent / 100;
    return basePrice * (1 - discount);
  }
}

@Injectable()
export class VIPPricing implements PricingStrategy {
  calculate(basePrice: number, context: PricingContext): number {
    // VIP gets 20% off
    return basePrice * 0.8;
  }
}

@Injectable()
export class SeasonalPricing implements PricingStrategy {
  calculate(basePrice: number, context: PricingContext): number {
    const month = new Date().getMonth();
    // Holiday season markup
    if (month === 11 || month === 0) {
      return basePrice * 1.1;
    }
    return basePrice;
  }
}

// Strategy factory
@Injectable({ providedIn: 'root' })
export class PricingStrategyFactory {
  private strategies = new Map<string, PricingStrategy>();

  constructor(
    regular: RegularPricing,
    discount: DiscountPricing,
    vip: VIPPricing,
    seasonal: SeasonalPricing
  ) {
    this.strategies.set('regular', regular);
    this.strategies.set('discount', discount);
    this.strategies.set('vip', vip);
    this.strategies.set('seasonal', seasonal);
  }

  get(type: string): PricingStrategy {
    return this.strategies.get(type) ?? this.strategies.get('regular')!;
  }
}

// Usage
@Injectable()
export class PricingService {
  private factory = inject(PricingStrategyFactory);

  calculatePrice(product: Product, user: User): number {
    const context: PricingContext = {
      discountPercent: product.discountPercent,
      userType: user.type
    };

    const strategyType = this.determineStrategy(user);
    const strategy = this.factory.get(strategyType);
    
    return strategy.calculate(product.basePrice, context);
  }

  private determineStrategy(user: User): string {
    if (user.type === 'vip') return 'vip';
    if (user.hasActiveDiscount) return 'discount';
    return 'regular';
  }
}
```

---

## Summary

| Pattern | Purpose | Use Case |
|---------|---------|----------|
| Repository | Abstract data access | Swap data sources, testing |
| Unit of Work | Transaction management | Multi-entity operations |
| Specification | Composable business rules | Complex filtering logic |
| CQRS | Separate read/write | Complex queries, scaling |
| Event-Driven | Loose coupling | Cross-feature communication |
| Strategy | Interchangeable algorithms | Multiple business rules |
