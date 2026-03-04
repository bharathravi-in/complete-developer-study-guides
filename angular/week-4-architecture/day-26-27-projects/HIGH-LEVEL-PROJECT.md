# Days 28-29: High-Level Project - E-Commerce Platform

## Project Overview

Build an enterprise-level E-Commerce application demonstrating:
- Micro Frontend Architecture
- Advanced State Management (NgRx Signals)
- Real-time features (WebSockets)
- Performance optimization
- Scalable folder structure
- AI integration

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────┐
│                      E-Commerce Platform                              │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │
│  │   Shell     │  │   Catalog   │  │    Cart     │  │   Checkout  │  │
│  │   (Host)    │  │  (Remote)   │  │  (Remote)   │  │  (Remote)   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  │
│         │                │                │                │          │
│  ┌──────┴────────────────┴────────────────┴────────────────┴──────┐  │
│  │                     Shared Libraries                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │  │
│  │  │  UI Lib  │  │ Auth Lib │  │ API Lib  │  │ State Lib│       │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │  │
│  └────────────────────────────────────────────────────────────────┘  │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Nx Workspace Setup

```bash
# Create Nx workspace
npx create-nx-workspace@latest ecommerce --preset=angular-standalone

# Navigate to workspace
cd ecommerce

# Generate shared libraries
nx g @nx/angular:library ui --directory=libs/shared
nx g @nx/angular:library auth --directory=libs/shared
nx g @nx/angular:library api --directory=libs/shared
nx g @nx/angular:library state --directory=libs/shared

# Generate applications
nx g @nx/angular:application shell
nx g @nx/angular:application catalog
nx g @nx/angular:application cart
nx g @nx/angular:application checkout
```

---

## Project Structure

```
ecommerce/
├── apps/
│   ├── shell/                    # Host application
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── layout/
│   │   │   │   ├── app.config.ts
│   │   │   │   └── app.routes.ts
│   │   │   └── main.ts
│   │   └── module-federation.config.ts
│   ├── catalog/                  # Product catalog MFE
│   │   ├── src/
│   │   │   ├── app/
│   │   │   │   ├── products/
│   │   │   │   ├── categories/
│   │   │   │   └── search/
│   │   └── module-federation.config.ts
│   ├── cart/                     # Shopping cart MFE
│   │   └── src/app/
│   │       ├── cart-items/
│   │       └── cart-summary/
│   └── checkout/                 # Checkout MFE
│       └── src/app/
│           ├── shipping/
│           ├── payment/
│           └── confirmation/
├── libs/
│   └── shared/
│       ├── ui/                   # Shared UI components
│       │   ├── button/
│       │   ├── card/
│       │   ├── modal/
│       │   └── form-controls/
│       ├── auth/                 # Authentication
│       │   ├── services/
│       │   ├── guards/
│       │   └── interceptors/
│       ├── api/                  # API services
│       │   ├── product.api.ts
│       │   ├── cart.api.ts
│       │   └── order.api.ts
│       └── state/                # Global state
│           ├── auth.store.ts
│           ├── cart.store.ts
│           └── user.store.ts
└── nx.json
```

---

## Shell Application (Host)

### Module Federation Config

```typescript
// apps/shell/module-federation.config.ts
import { ModuleFederationConfig } from '@nx/webpack';

const config: ModuleFederationConfig = {
  name: 'shell',
  remotes: ['catalog', 'cart', 'checkout']
};

export default config;
```

### Shell Routes

```typescript
// apps/shell/src/app/app.routes.ts
export const routes: Routes = [
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  {
    path: 'home',
    loadComponent: () => import('./home/home.component')
  },
  {
    path: 'products',
    loadRemoteModule({
      type: 'module',
      remoteEntry: 'http://localhost:4201/remoteEntry.js',
      exposedModule: './Routes'
    }).then(m => m.CATALOG_ROUTES)
  },
  {
    path: 'cart',
    loadRemoteModule({
      type: 'module',
      remoteEntry: 'http://localhost:4202/remoteEntry.js',
      exposedModule: './Routes'
    }).then(m => m.CART_ROUTES),
    canActivate: [authGuard]
  },
  {
    path: 'checkout',
    loadRemoteModule({
      type: 'module',
      remoteEntry: 'http://localhost:4203/remoteEntry.js',
      exposedModule: './Routes'
    }).then(m => m.CHECKOUT_ROUTES),
    canActivate: [authGuard]
  }
];
```

### Shell Layout

```typescript
// apps/shell/src/app/layout/layout.component.ts
@Component({
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, FooterComponent, SidenavComponent],
  template: `
    <app-header 
      [user]="authStore.user()"
      [cartCount]="cartStore.itemCount()"
      (logout)="authStore.logout()"
      (toggleMenu)="sidenavOpen.set(!sidenavOpen())" />

    <mat-sidenav-container>
      <mat-sidenav [opened]="sidenavOpen()" mode="side">
        <app-sidenav [categories]="categoryStore.categories()" />
      </mat-sidenav>

      <mat-sidenav-content>
        <main>
          <router-outlet />
        </main>
        <app-footer />
      </mat-sidenav-content>
    </mat-sidenav-container>

    @if (notification()) {
      <app-notification [message]="notification()" />
    }
  `
})
export class LayoutComponent {
  authStore = inject(AuthStore);
  cartStore = inject(CartStore);
  categoryStore = inject(CategoryStore);
  notification = inject(NotificationService).message;
  
  sidenavOpen = signal(true);
}
```

---

## Product Catalog MFE

### Product Store (NgRx Signals)

```typescript
// apps/catalog/src/app/stores/product.store.ts
type ProductState = {
  products: Product[];
  selectedProduct: Product | null;
  categories: Category[];
  filters: ProductFilters;
  pagination: Pagination;
  loading: boolean;
  error: string | null;
};

const initialState: ProductState = {
  products: [],
  selectedProduct: null,
  categories: [],
  filters: { category: null, priceRange: [0, 1000], search: '' },
  pagination: { page: 1, pageSize: 20, total: 0 },
  loading: false,
  error: null
};

export const ProductStore = signalStore(
  { providedIn: 'root' },
  withState(initialState),
  withComputed((store) => ({
    filteredProducts: computed(() => {
      let products = store.products();
      const filters = store.filters();
      
      if (filters.category) {
        products = products.filter(p => p.categoryId === filters.category);
      }
      if (filters.search) {
        products = products.filter(p => 
          p.name.toLowerCase().includes(filters.search.toLowerCase())
        );
      }
      products = products.filter(p => 
        p.price >= filters.priceRange[0] && p.price <= filters.priceRange[1]
      );
      
      return products;
    }),
    totalPages: computed(() => 
      Math.ceil(store.pagination().total / store.pagination().pageSize)
    ),
    hasProducts: computed(() => store.products().length > 0)
  })),
  withMethods((store, api = inject(ProductApiService)) => ({
    async loadProducts(params?: ProductQueryParams) {
      patchState(store, { loading: true, error: null });
      
      try {
        const response = await firstValueFrom(api.getProducts(params));
        patchState(store, {
          products: response.data,
          pagination: response.meta,
          loading: false
        });
      } catch (error) {
        patchState(store, { error: 'Failed to load products', loading: false });
      }
    },
    async loadProductById(id: string) {
      patchState(store, { loading: true });
      
      try {
        const product = await firstValueFrom(api.getProductById(id));
        patchState(store, { selectedProduct: product, loading: false });
      } catch (error) {
        patchState(store, { error: 'Product not found', loading: false });
      }
    },
    setFilters(filters: Partial<ProductFilters>) {
      patchState(store, { filters: { ...store.filters(), ...filters } });
    },
    setPage(page: number) {
      patchState(store, { pagination: { ...store.pagination(), page } });
    }
  })),
  withHooks({
    onInit(store) {
      store.loadProducts();
    }
  })
);
```

### Product List Component

```typescript
// apps/catalog/src/app/products/product-list.component.ts
@Component({
  standalone: true,
  imports: [ProductCardComponent, ProductFiltersComponent, PaginatorComponent],
  template: `
    <div class="product-list">
      <aside class="filters">
        <app-product-filters 
          [filters]="store.filters()"
          [categories]="store.categories()"
          (filtersChange)="store.setFilters($event)" />
      </aside>

      <main class="products">
        @if (store.loading()) {
          <div class="skeleton-grid">
            @for (i of [1,2,3,4,5,6]; track i) {
              <div class="skeleton-card"></div>
            }
          </div>
        } @else if (store.filteredProducts().length === 0) {
          <div class="empty-state">
            <mat-icon>inventory_2</mat-icon>
            <h3>No products found</h3>
            <p>Try adjusting your filters</p>
          </div>
        } @else {
          <div class="product-grid">
            @for (product of store.filteredProducts(); track product.id) {
              @defer (on viewport) {
                <app-product-card 
                  [product]="product"
                  (addToCart)="addToCart($event)"
                  (viewDetails)="viewDetails($event)" />
              } @placeholder {
                <div class="skeleton-card"></div>
              }
            }
          </div>
        }

        <app-paginator 
          [page]="store.pagination().page"
          [total]="store.pagination().total"
          [pageSize]="store.pagination().pageSize"
          (pageChange)="store.setPage($event)" />
      </main>
    </div>
  `
})
export default class ProductListComponent {
  store = inject(ProductStore);
  cartStore = inject(CartStore);
  router = inject(Router);

  addToCart(product: Product) {
    this.cartStore.addItem(product, 1);
  }

  viewDetails(product: Product) {
    this.router.navigate(['/products', product.id]);
  }
}
```

### Product Detail with AI Recommendations

```typescript
// apps/catalog/src/app/products/product-detail.component.ts
@Component({
  standalone: true,
  template: `
    @if (store.loading()) {
      <app-product-detail-skeleton />
    } @else if (store.selectedProduct(); as product) {
      <div class="product-detail">
        <div class="gallery">
          <app-image-gallery [images]="product.images" />
        </div>

        <div class="info">
          <h1>{{ product.name }}</h1>
          <div class="rating">
            <app-star-rating [rating]="product.rating" />
            <span>({{ product.reviewCount }} reviews)</span>
          </div>
          
          <p class="price">{{ product.price | currency }}</p>
          
          <p class="description">{{ product.description }}</p>

          <div class="actions">
            <app-quantity-selector [(quantity)]="quantity" />
            <button mat-raised-button color="primary" (click)="addToCart()">
              <mat-icon>shopping_cart</mat-icon>
              Add to Cart
            </button>
            <button mat-icon-button (click)="toggleWishlist()">
              <mat-icon>{{ isWishlisted() ? 'favorite' : 'favorite_border' }}</mat-icon>
            </button>
          </div>
        </div>
      </div>

      <section class="reviews">
        <h2>Customer Reviews</h2>
        <app-review-list [productId]="product.id" />
      </section>

      <section class="recommendations">
        <h2>You Might Also Like</h2>
        @if (loadingRecommendations()) {
          <app-product-carousel-skeleton />
        } @else {
          <app-product-carousel [products]="recommendations()" />
        }
      </section>

      <section class="ai-assistant">
        <h2>Ask About This Product</h2>
        <app-product-ai-chat [product]="product" />
      </section>
    }
  `
})
export default class ProductDetailComponent implements OnInit {
  store = inject(ProductStore);
  cartStore = inject(CartStore);
  wishlistStore = inject(WishlistStore);
  recommendationService = inject(RecommendationService);
  route = inject(ActivatedRoute);

  quantity = signal(1);
  recommendations = signal<Product[]>([]);
  loadingRecommendations = signal(true);

  isWishlisted = computed(() => 
    this.wishlistStore.isWishlisted(this.store.selectedProduct()?.id)
  );

  ngOnInit() {
    const productId = this.route.snapshot.params['id'];
    this.store.loadProductById(productId);
    this.loadRecommendations(productId);
  }

  addToCart() {
    const product = this.store.selectedProduct();
    if (product) {
      this.cartStore.addItem(product, this.quantity());
    }
  }

  toggleWishlist() {
    const product = this.store.selectedProduct();
    if (product) {
      if (this.isWishlisted()) {
        this.wishlistStore.removeItem(product.id);
      } else {
        this.wishlistStore.addItem(product);
      }
    }
  }

  private loadRecommendations(productId: string) {
    this.recommendationService.getRecommendations(productId).subscribe({
      next: products => {
        this.recommendations.set(products);
        this.loadingRecommendations.set(false);
      }
    });
  }
}
```

---

## Shopping Cart MFE

### Cart Store (Global)

```typescript
// libs/shared/state/src/lib/cart.store.ts
interface CartItem {
  product: Product;
  quantity: number;
}

interface CartState {
  items: CartItem[];
  loading: boolean;
}

export const CartStore = signalStore(
  { providedIn: 'root' },
  withState<CartState>({ items: [], loading: false }),
  withComputed((store) => ({
    itemCount: computed(() => 
      store.items().reduce((sum, item) => sum + item.quantity, 0)
    ),
    subtotal: computed(() =>
      store.items().reduce((sum, item) => sum + item.product.price * item.quantity, 0)
    ),
    tax: computed(() => store.items().reduce((sum, item) => 
      sum + item.product.price * item.quantity, 0) * 0.1
    ),
    total: computed(() => {
      const items = store.items();
      const subtotal = items.reduce((sum, i) => sum + i.product.price * i.quantity, 0);
      const tax = subtotal * 0.1;
      return subtotal + tax;
    }),
    isEmpty: computed(() => store.items().length === 0)
  })),
  withMethods((store, api = inject(CartApiService), notification = inject(NotificationService)) => ({
    addItem(product: Product, quantity: number) {
      const items = store.items();
      const existingIndex = items.findIndex(i => i.product.id === product.id);

      if (existingIndex >= 0) {
        const updated = [...items];
        updated[existingIndex] = {
          ...updated[existingIndex],
          quantity: updated[existingIndex].quantity + quantity
        };
        patchState(store, { items: updated });
      } else {
        patchState(store, { items: [...items, { product, quantity }] });
      }

      notification.success(`${product.name} added to cart`);
      this.syncCart();
    },
    updateQuantity(productId: string, quantity: number) {
      if (quantity <= 0) {
        this.removeItem(productId);
        return;
      }

      patchState(store, {
        items: store.items().map(item =>
          item.product.id === productId ? { ...item, quantity } : item
        )
      });
      this.syncCart();
    },
    removeItem(productId: string) {
      patchState(store, {
        items: store.items().filter(item => item.product.id !== productId)
      });
      this.syncCart();
    },
    clearCart() {
      patchState(store, { items: [] });
      this.syncCart();
    },
    async syncCart() {
      const items = store.items();
      await firstValueFrom(api.syncCart(items));
    },
    async loadCart() {
      patchState(store, { loading: true });
      try {
        const items = await firstValueFrom(api.getCart());
        patchState(store, { items, loading: false });
      } catch {
        patchState(store, { loading: false });
      }
    }
  }))
);
```

---

## Checkout MFE

### Multi-Step Checkout

```typescript
// apps/checkout/src/app/checkout.component.ts
@Component({
  standalone: true,
  imports: [MatStepperModule, ShippingFormComponent, PaymentFormComponent, ConfirmationComponent],
  template: `
    <div class="checkout-container">
      <mat-stepper linear #stepper>
        <mat-step [stepControl]="shippingForm" label="Shipping">
          <app-shipping-form 
            [form]="shippingForm"
            [savedAddresses]="addressStore.addresses()"
            (addressSelected)="selectAddress($event)" />
          <button mat-raised-button matStepperNext [disabled]="shippingForm.invalid">
            Continue to Payment
          </button>
        </mat-step>

        <mat-step [stepControl]="paymentForm" label="Payment">
          <app-payment-form 
            [form]="paymentForm"
            [savedCards]="paymentStore.savedCards()" />
          <button mat-button matStepperPrevious>Back</button>
          <button mat-raised-button matStepperNext [disabled]="paymentForm.invalid">
            Review Order
          </button>
        </mat-step>

        <mat-step label="Confirmation">
          <app-order-confirmation
            [cartItems]="cartStore.items()"
            [shippingAddress]="shippingForm.getRawValue()"
            [total]="cartStore.total()"
            [processing]="processing()"
            (placeOrder)="placeOrder()" />
        </mat-step>
      </mat-stepper>

      <aside class="order-summary">
        <app-order-summary
          [items]="cartStore.items()"
          [subtotal]="cartStore.subtotal()"
          [tax]="cartStore.tax()"
          [total]="cartStore.total()" />
      </aside>
    </div>
  `
})
export default class CheckoutComponent {
  cartStore = inject(CartStore);
  addressStore = inject(AddressStore);
  paymentStore = inject(PaymentStore);
  orderService = inject(OrderService);
  router = inject(Router);
  fb = inject(FormBuilder);

  processing = signal(false);

  shippingForm = this.fb.nonNullable.group({
    firstName: ['', Validators.required],
    lastName: ['', Validators.required],
    address: ['', Validators.required],
    city: ['', Validators.required],
    state: ['', Validators.required],
    zipCode: ['', [Validators.required, Validators.pattern(/^\d{5}$/)]],
    phone: ['', Validators.required]
  });

  paymentForm = this.fb.nonNullable.group({
    cardNumber: ['', [Validators.required, this.cardValidator]],
    expiryDate: ['', [Validators.required, this.expiryValidator]],
    cvv: ['', [Validators.required, Validators.pattern(/^\d{3,4}$/)]]
  });

  selectAddress(address: Address) {
    this.shippingForm.patchValue(address);
  }

  async placeOrder() {
    this.processing.set(true);
    
    try {
      const order = await firstValueFrom(this.orderService.createOrder({
        items: this.cartStore.items(),
        shippingAddress: this.shippingForm.getRawValue(),
        payment: this.paymentForm.getRawValue()
      }));

      this.cartStore.clearCart();
      this.router.navigate(['/order-success', order.id]);
    } catch (error) {
      // Handle error
    } finally {
      this.processing.set(false);
    }
  }

  private cardValidator(control: FormControl): ValidationErrors | null {
    const value = control.value.replace(/\s/g, '');
    return /^\d{16}$/.test(value) ? null : { invalidCard: true };
  }

  private expiryValidator(control: FormControl): ValidationErrors | null {
    return /^(0[1-9]|1[0-2])\/\d{2}$/.test(control.value) ? null : { invalidExpiry: true };
  }
}
```

---

## Real-Time Features

### WebSocket Service

```typescript
// libs/shared/api/src/lib/websocket.service.ts
@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private socket: WebSocket | null = null;
  private messages$ = new Subject<WebSocketMessage>();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect(url: string): Observable<WebSocketMessage> {
    if (this.socket) return this.messages$.asObservable();

    this.socket = new WebSocket(url);

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.messages$.next(message);
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect(url);
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return this.messages$.asObservable();
  }

  send(message: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }

  disconnect(): void {
    this.socket?.close();
    this.socket = null;
  }

  private attemptReconnect(url: string): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => this.connect(url), 2000 * this.reconnectAttempts);
    }
  }
}

// Real-time inventory updates
@Injectable({ providedIn: 'root' })
export class InventoryService {
  private ws = inject(WebSocketService);
  private productStore = inject(ProductStore);

  initialize(): void {
    this.ws.connect('wss://api.example.com/inventory').pipe(
      filter(msg => msg.type === 'INVENTORY_UPDATE')
    ).subscribe(update => {
      this.productStore.updateInventory(update.productId, update.stock);
    });
  }
}
```

---

## Running the Platform

```bash
# Start all MFEs
nx serve shell --devRemotes=catalog,cart,checkout

# Or individually
nx serve shell
nx serve catalog
nx serve cart
nx serve checkout

# Build for production
nx run-many --target=build --all --configuration=production

# Deploy
nx deploy shell
```

---

## Key Takeaways

| Pattern | Implementation |
|---------|---------------|
| Micro Frontends | Module Federation with Nx |
| State Management | NgRx Signal Store (global) |
| Real-Time | WebSocket service |
| Performance | @defer, lazy loading, virtual scroll |
| AI Integration | Product recommendations, chatbot |
| Scalability | Shared libraries, consistent patterns |
