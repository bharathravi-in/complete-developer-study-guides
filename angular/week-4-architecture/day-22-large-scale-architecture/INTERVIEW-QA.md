# Day 22: Large-Scale Architecture - Interview Questions & Answers

## Basic Level

### Q1: How do you structure a large Angular application?

**Answer:**
Large Angular applications typically use a monorepo structure with feature-based organization:

```
workspace/
├── apps/
│   ├── main-app/           # Main application
│   └── admin-app/          # Admin application
├── libs/
│   ├── shared/
│   │   ├── ui/             # Reusable UI components
│   │   ├── utils/          # Utility functions
│   │   └── data-access/    # Shared services/API
│   └── feature/
│       ├── auth/           # Auth feature module
│       ├── products/       # Products feature
│       └── orders/         # Orders feature
└── nx.json
```

**Key Principles:**
1. **Separation of concerns** - Each library has a single responsibility
2. **Lazy loading** - Load features on demand
3. **Shared code** - Common functionality in shared libraries
4. **Clear boundaries** - Enforce dependency rules

---

### Q2: What are Smart and Dumb components?

**Answer:**

| Smart (Container) | Dumb (Presentational) |
|-------------------|----------------------|
| Knows about services | Only uses inputs/outputs |
| Manages state | Stateless |
| Contains business logic | Pure presentation |
| Connected to store | Reusable anywhere |

```typescript
// Smart Component
@Component({
  template: `
    <app-user-list 
      [users]="users()" 
      (select)="onSelect($event)" 
    />
  `
})
export class UserContainerComponent {
  private store = inject(UserStore);
  users = this.store.users;

  onSelect(user: User) {
    this.store.selectUser(user);
  }
}

// Dumb Component
@Component({
  selector: 'app-user-list',
  template: `
    @for (user of users(); track user.id) {
      <div (click)="select.emit(user)">{{ user.name }}</div>
    }
  `
})
export class UserListComponent {
  users = input.required<User[]>();
  select = output<User>();
}
```

---

### Q3: What is the Facade pattern?

**Answer:**
Facade provides a simplified interface to complex subsystems (stores, services, APIs):

```typescript
@Injectable({ providedIn: 'root' })
export class OrderFacade {
  private store = inject(OrderStore);
  private api = inject(OrderApi);
  private notification = inject(NotificationService);

  // Expose simplified state
  orders = this.store.orders;
  loading = this.store.loading;
  
  // Simplified methods
  loadOrders() {
    this.store.setLoading(true);
    this.api.getOrders().subscribe(orders => {
      this.store.setOrders(orders);
    });
  }

  createOrder(data: CreateOrderDto) {
    this.api.create(data).subscribe(order => {
      this.store.addOrder(order);
      this.notification.success('Order created');
    });
  }
}

// Component uses simple facade
@Component({...})
export class OrderListComponent {
  private facade = inject(OrderFacade);
  orders = this.facade.orders;

  ngOnInit() {
    this.facade.loadOrders();
  }
}
```

**Benefits:**
- Components don't need to know about internals
- Easier to test (mock facade)
- Centralized logic
- Cleaner components

---

## Intermediate Level

### Q4: How do you enforce module boundaries?

**Answer:**
Using Nx workspace with ESLint rules:

```json
// project.json - Tag libraries
{
  "projects": {
    "feature-orders": {
      "tags": ["scope:orders", "type:feature"]
    },
    "shared-ui": {
      "tags": ["scope:shared", "type:ui"]
    },
    "data-access-orders": {
      "tags": ["scope:orders", "type:data-access"]
    }
  }
}
```

```json
// .eslintrc.json - Define rules
{
  "rules": {
    "@nx/enforce-module-boundaries": [
      "error",
      {
        "depConstraints": [
          {
            "sourceTag": "type:feature",
            "onlyDependOnLibsWithTags": ["type:ui", "type:data-access", "type:util"]
          },
          {
            "sourceTag": "type:ui",
            "onlyDependOnLibsWithTags": ["type:ui", "type:util"]
          },
          {
            "sourceTag": "scope:orders",
            "onlyDependOnLibsWithTags": ["scope:orders", "scope:shared"]
          }
        ]
      }
    ]
  }
}
```

**This prevents:**
- UI libraries importing feature libraries
- Feature A importing Feature B's internal code
- Circular dependencies

---

### Q5: How do you organize state management at scale?

**Answer:**

**1. Feature-level stores:**
```typescript
// Each feature has its own store
// libs/feature/products/src/lib/state/product.store.ts
@Injectable()
export class ProductStore extends ComponentStore<ProductState> {
  // Feature-specific state
}

// Provided at feature level
@Component({
  providers: [ProductStore]
})
export class ProductShellComponent {}
```

**2. Global shared state:**
```typescript
// Single instance for app-wide state
@Injectable({ providedIn: 'root' })
export class AuthStore {
  user = signal<User | null>(null);
  isAuthenticated = computed(() => !!this.user());
}
```

**3. Component-local state:**
```typescript
// State for single component instance
@Component({
  providers: [FormStore]  // New instance per component
})
export class ProductFormComponent {
  private formStore = inject(FormStore);
}
```

**Best Practice:**
- Global: Auth, User preferences, Notifications
- Feature: Feature-specific domain data
- Local: Form state, UI state, temporary data

---

### Q6: How do you implement domain-driven design in Angular?

**Answer:**

**Layered Architecture:**
```
Presentation → Facade → Application → Domain → Infrastructure
```

```typescript
// Domain Layer - Business entities
export class Order {
  constructor(
    public readonly items: OrderItem[],
    public readonly status: OrderStatus
  ) {}

  get total(): number {
    return this.items.reduce((sum, i) => sum + i.price * i.quantity, 0);
  }

  canBeCancelled(): boolean {
    return ['pending', 'confirmed'].includes(this.status);
  }
}

// Application Layer - Use cases
@Injectable()
export class CancelOrderUseCase {
  private orderRepo = inject(OrderRepository);

  execute(orderId: string): Observable<Order> {
    return this.orderRepo.findById(orderId).pipe(
      tap(order => {
        if (!order.canBeCancelled()) {
          throw new Error('Cannot cancel order');
        }
      }),
      switchMap(order => this.orderRepo.updateStatus(orderId, 'cancelled'))
    );
  }
}

// Infrastructure Layer - API implementation
@Injectable()
export class OrderApiRepository implements OrderRepository {
  private http = inject(HttpClient);

  findById(id: string): Observable<Order> {
    return this.http.get<OrderDto>(`/api/orders/${id}`).pipe(
      map(dto => this.toDomain(dto))
    );
  }
}
```

---

## Advanced Level

### Q7: How do you handle cross-cutting concerns?

**Answer:**

**1. HTTP Interceptors:**
```typescript
// Auth, logging, error handling
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = inject(AuthService).getToken();
  if (token) {
    req = req.clone({ setHeaders: { Authorization: `Bearer ${token}` }});
  }
  return next(req);
};
```

**2. Error Boundary Component:**
```typescript
@Component({
  selector: 'app-error-boundary',
  template: `
    @if (hasError()) {
      <app-error-fallback [error]="error()" (retry)="reset()" />
    } @else {
      <ng-content />
    }
  `
})
export class ErrorBoundaryComponent implements ErrorHandler {
  hasError = signal(false);
  error = signal<Error | null>(null);

  handleError(error: Error) {
    this.error.set(error);
    this.hasError.set(true);
  }

  reset() {
    this.hasError.set(false);
    this.error.set(null);
  }
}
```

**3. Global Services:**
```typescript
// Notification service used across features
@Injectable({ providedIn: 'root' })
export class NotificationService {
  private snackBar = inject(MatSnackBar);

  success(message: string) { /* ... */ }
  error(message: string) { /* ... */ }
}
```

---

### Q8: How do you scale routing in large applications?

**Answer:**
```typescript
// 1. Lazy load all features
export const routes: Routes = [
  {
    path: '',
    component: LayoutComponent,
    children: [
      {
        path: 'products',
        loadChildren: () => import('@org/feature-products')
          .then(m => m.PRODUCT_ROUTES)
      },
      {
        path: 'orders',
        loadChildren: () => import('@org/feature-orders')
          .then(m => m.ORDER_ROUTES),
        canMatch: [hasPermission('orders:read')]
      }
    ]
  }
];

// 2. Feature handles its own routes
// libs/feature/products/src/lib/products.routes.ts
export const PRODUCT_ROUTES: Routes = [
  { path: '', component: ProductListComponent },
  { path: 'new', component: ProductFormComponent },
  { path: ':id', component: ProductDetailComponent },
  { path: ':id/edit', component: ProductFormComponent }
];

// 3. Preload critical routes
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes,
      withPreloading(PreloadAllModules),
      // Or custom strategy
      withPreloading(CustomPreloadingStrategy)
    )
  ]
};

// 4. Custom preloading
@Injectable({ providedIn: 'root' })
export class CustomPreloadingStrategy implements PreloadingStrategy {
  preload(route: Route, load: () => Observable<any>): Observable<any> {
    if (route.data?.['preload']) {
      return load();
    }
    return of(null);
  }
}
```

---

### Q9: How do you handle configuration and environment management?

**Answer:**
```typescript
// 1. Environment files (build-time)
// environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:3000/api'
};

// 2. Runtime configuration
@Injectable({ providedIn: 'root' })
export class ConfigService {
  private config = signal<AppConfig | null>(null);

  load(): Promise<void> {
    return fetch('/assets/config.json')
      .then(r => r.json())
      .then(config => this.config.set(config));
  }

  get apiUrl(): string {
    return this.config()?.apiUrl ?? environment.apiUrl;
  }
}

// Load before app starts
export function initializeApp(config: ConfigService) {
  return () => config.load();
}

export const appConfig: ApplicationConfig = {
  providers: [
    {
      provide: APP_INITIALIZER,
      useFactory: initializeApp,
      deps: [ConfigService],
      multi: true
    }
  ]
};

// 3. Feature flags
@Injectable({ providedIn: 'root' })
export class FeatureFlags {
  private flags = signal<Record<string, boolean>>({});

  isEnabled(feature: string): boolean {
    return this.flags()[feature] ?? false;
  }
}
```

---

## Quick Reference

```
Library Types (Nx):
───────────────────
feature/     - Smart components, feature logic
ui/          - Presentational components
data-access/ - Services, state, API
util/        - Pure helper functions
domain/      - Business logic, entities

Component Types:
────────────────
Container    - Connects to store/services
Presentational - Pure inputs/outputs
Shell        - Layout, provides context

State Scopes:
─────────────
Global       - providedIn: 'root'
Feature      - Provided in feature shell
Component    - Provided in component

Architecture Layers:
────────────────────
Presentation → Facade → Application → Domain → Infrastructure

Boundary Rules:
───────────────
feature  → ui, data-access, util
ui       → ui, util (no services!)
data     → util, models
util     → (nothing else)
```
