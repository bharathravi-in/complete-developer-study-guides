# Day 22: Large-Scale Angular Architecture

## Overview

Building large Angular applications requires careful architectural decisions to ensure maintainability, scalability, and team productivity.

---

## Monorepo Structure with Nx

```
my-org/
├── apps/
│   ├── web-app/                    # Main web application
│   ├── admin-app/                  # Admin dashboard
│   └── mobile-app/                 # Ionic/Capacitor app
├── libs/
│   ├── shared/
│   │   ├── ui/                     # Shared UI components
│   │   ├── data-access/            # Shared API services
│   │   ├── utils/                  # Utility functions
│   │   └── models/                 # TypeScript interfaces
│   ├── feature/
│   │   ├── auth/                   # Authentication feature
│   │   ├── users/                  # User management
│   │   └── products/               # Products feature
│   └── domain/
│       ├── user/                   # User domain logic
│       └── product/                # Product domain logic
├── tools/
├── nx.json
└── workspace.json
```

### Library Types

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Library Classification                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Feature Libraries:                                                  │
│  └── Smart components, feature-specific logic                        │
│  └── Example: libs/feature/dashboard                                 │
│                                                                      │
│  UI Libraries:                                                       │
│  └── Presentational/dumb components                                  │
│  └── Example: libs/shared/ui                                         │
│                                                                      │
│  Data-Access Libraries:                                              │
│  └── Services, state management, API calls                           │
│  └── Example: libs/shared/data-access                                │
│                                                                      │
│  Utility Libraries:                                                  │
│  └── Pure functions, helpers, pipes                                  │
│  └── Example: libs/shared/utils                                      │
│                                                                      │
│  Domain Libraries:                                                   │
│  └── Domain logic, business rules                                    │
│  └── Example: libs/domain/orders                                     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Feature Module Architecture

### Smart vs Dumb Components

```typescript
// Smart Component (Container) - knows about state and services
@Component({
  selector: 'app-user-list-container',
  template: `
    <app-user-list
      [users]="users()"
      [loading]="loading()"
      (userSelected)="onUserSelect($event)"
      (deleteUser)="onDeleteUser($event)"
    />
  `
})
export class UserListContainerComponent {
  private store = inject(UserStore);
  
  users = this.store.users;
  loading = this.store.loading;

  onUserSelect(user: User) {
    this.store.selectUser(user);
  }

  onDeleteUser(userId: string) {
    this.store.deleteUser(userId);
  }
}

// Dumb Component (Presentational) - only deals with inputs/outputs
@Component({
  selector: 'app-user-list',
  template: `
    @if (loading()) {
      <app-skeleton type="list" />
    } @else {
      @for (user of users(); track user.id) {
        <app-user-card
          [user]="user"
          (click)="userSelected.emit(user)"
          (delete)="deleteUser.emit(user.id)"
        />
      }
    }
  `
})
export class UserListComponent {
  users = input.required<User[]>();
  loading = input(false);
  userSelected = output<User>();
  deleteUser = output<string>();
}
```

### Feature Module Structure

```
libs/feature/products/
├── src/
│   ├── lib/
│   │   ├── containers/
│   │   │   ├── product-list-container/
│   │   │   └── product-detail-container/
│   │   ├── components/
│   │   │   ├── product-card/
│   │   │   ├── product-form/
│   │   │   └── product-filters/
│   │   ├── services/
│   │   │   └── product.facade.ts
│   │   ├── state/
│   │   │   ├── product.store.ts
│   │   │   └── product.selectors.ts
│   │   ├── models/
│   │   │   └── product.model.ts
│   │   └── products.routes.ts
│   ├── index.ts
│   └── public-api.ts
└── project.json
```

---

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Layered Architecture                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    PRESENTATION LAYER                          │  │
│  │  Components │ Templates │ Directives │ Pipes                   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      FACADE LAYER                              │  │
│  │  Facade Services │ View Models │ Component State               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    APPLICATION LAYER                           │  │
│  │  Use Cases │ Application Services │ DTOs                       │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      DOMAIN LAYER                              │  │
│  │  Entities │ Value Objects │ Domain Services │ Business Rules   │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                   INFRASTRUCTURE LAYER                         │  │
│  │  API Services │ Storage │ External Services │ Adapters         │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Implementation

```typescript
// Domain Layer - Business entities and rules
// libs/domain/order/src/lib/order.entity.ts
export class Order {
  constructor(
    public readonly id: string,
    public readonly items: OrderItem[],
    public readonly status: OrderStatus,
    public readonly customerId: string,
    public readonly createdAt: Date
  ) {}

  get total(): number {
    return this.items.reduce((sum, item) => sum + item.subtotal, 0);
  }

  canBeCancelled(): boolean {
    return this.status === 'pending' || this.status === 'confirmed';
  }
}

// Application Layer - Use cases
// libs/feature/orders/src/lib/services/order.use-cases.ts
@Injectable({ providedIn: 'root' })
export class OrderUseCases {
  private orderRepo = inject(OrderRepository);
  private notificationService = inject(NotificationService);

  createOrder(items: OrderItem[], customerId: string): Observable<Order> {
    const order = new Order(
      generateId(),
      items,
      'pending',
      customerId,
      new Date()
    );

    return this.orderRepo.save(order).pipe(
      tap(savedOrder => {
        this.notificationService.notify('Order created', savedOrder.id);
      })
    );
  }

  cancelOrder(orderId: string): Observable<Order> {
    return this.orderRepo.findById(orderId).pipe(
      tap(order => {
        if (!order.canBeCancelled()) {
          throw new Error('Order cannot be cancelled');
        }
      }),
      switchMap(order => this.orderRepo.updateStatus(order.id, 'cancelled'))
    );
  }
}

// Facade Layer - Simplified interface for components
// libs/feature/orders/src/lib/services/order.facade.ts
@Injectable({ providedIn: 'root' })
export class OrderFacade {
  private store = inject(OrderStore);
  private useCases = inject(OrderUseCases);

  // Expose state as signals
  orders = this.store.orders;
  selectedOrder = this.store.selectedOrder;
  loading = this.store.loading;
  error = this.store.error;

  loadOrders() {
    this.store.setLoading(true);
    this.useCases.getOrders().subscribe({
      next: orders => this.store.setOrders(orders),
      error: err => this.store.setError(err.message)
    });
  }

  createOrder(items: OrderItem[]) {
    return this.useCases.createOrder(items, this.getCurrentUserId());
  }

  cancelOrder(orderId: string) {
    return this.useCases.cancelOrder(orderId);
  }
}
```

---

## Module Boundaries & Dependencies

### Enforcing Boundaries with Nx

```json
// nx.json
{
  "projects": {
    "feature-orders": {
      "tags": ["scope:orders", "type:feature"]
    },
    "ui-shared": {
      "tags": ["scope:shared", "type:ui"]
    }
  }
}
```

```json
// .eslintrc.json
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

---

## State Management at Scale

### Store per Feature

```typescript
// Feature-specific store
// libs/feature/products/src/lib/state/product.store.ts
interface ProductState {
  products: Product[];
  selectedId: string | null;
  filters: ProductFilters;
  loading: boolean;
  error: string | null;
}

const initialState: ProductState = {
  products: [],
  selectedId: null,
  filters: { category: null, priceRange: null },
  loading: false,
  error: null
};

@Injectable()
export class ProductStore extends ComponentStore<ProductState> {
  constructor() {
    super(initialState);
  }

  // Selectors
  readonly products = this.selectSignal(state => state.products);
  readonly selectedProduct = this.selectSignal(state => 
    state.products.find(p => p.id === state.selectedId)
  );
  readonly loading = this.selectSignal(state => state.loading);
  
  readonly filteredProducts = this.selectSignal(state => {
    let result = state.products;
    if (state.filters.category) {
      result = result.filter(p => p.category === state.filters.category);
    }
    return result;
  });

  // Updaters
  readonly setProducts = this.updater((state, products: Product[]) => ({
    ...state,
    products,
    loading: false
  }));

  readonly setFilters = this.updater((state, filters: ProductFilters) => ({
    ...state,
    filters
  }));

  // Effects
  readonly loadProducts = this.effect((trigger$: Observable<void>) => {
    return trigger$.pipe(
      tap(() => this.patchState({ loading: true })),
      switchMap(() => this.productService.getProducts().pipe(
        tapResponse(
          products => this.setProducts(products),
          error => this.patchState({ error: error.message, loading: false })
        )
      ))
    );
  });
}
```

### Global vs Local State

```typescript
// Global state - shared across application
// libs/shared/data-access/src/lib/auth.store.ts
@Injectable({ providedIn: 'root' })
export class GlobalAuthStore {
  private user = signal<User | null>(null);
  private token = signal<string | null>(null);

  readonly isAuthenticated = computed(() => !!this.token());
  readonly currentUser = this.user.asReadonly();
}

// Local state - component-specific
// libs/feature/products/src/lib/components/product-form.component.ts
@Component({
  providers: [ProductFormStore]  // New instance per component
})
export class ProductFormComponent {
  private store = inject(ProductFormStore);
}
```

---

## Scalable Routing

```typescript
// Root routes with lazy loading
export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./layout/layout.component'),
    children: [
      {
        path: 'dashboard',
        loadChildren: () => import('@myorg/feature-dashboard').then(m => m.DASHBOARD_ROUTES)
      },
      {
        path: 'products',
        loadChildren: () => import('@myorg/feature-products').then(m => m.PRODUCT_ROUTES),
        canMatch: [() => inject(PermissionService).hasPermission('products:read')]
      },
      {
        path: 'orders',
        loadChildren: () => import('@myorg/feature-orders').then(m => m.ORDER_ROUTES)
      }
    ]
  },
  {
    path: 'auth',
    loadChildren: () => import('@myorg/feature-auth').then(m => m.AUTH_ROUTES)
  }
];

// Feature routes
// libs/feature/products/src/lib/products.routes.ts
export const PRODUCT_ROUTES: Routes = [
  {
    path: '',
    component: ProductListContainerComponent
  },
  {
    path: 'new',
    component: ProductFormContainerComponent,
    canDeactivate: [unsavedChangesGuard]
  },
  {
    path: ':id',
    component: ProductDetailContainerComponent,
    resolve: { product: productResolver }
  },
  {
    path: ':id/edit',
    component: ProductFormContainerComponent,
    resolve: { product: productResolver }
  }
];
```

---

## Summary

| Concept | Description |
|---------|-------------|
| Monorepo | Single repository with multiple apps/libs |
| Feature Libraries | Domain-specific functionality |
| Smart/Dumb Components | Container vs presentational |
| Facade Pattern | Simplified interface to complex subsystems |
| Module Boundaries | Enforce dependency rules |
| Local vs Global State | Component vs application state |
