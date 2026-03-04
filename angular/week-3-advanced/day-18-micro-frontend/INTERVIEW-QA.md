# Day 18: Micro Frontends - Interview Questions & Answers

## Basic Level

### Q1: What are Micro Frontends?

**Answer:**
Micro Frontends extend microservices architecture to the frontend. Instead of a monolithic frontend application, you build multiple smaller applications that work together.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Monolith vs Micro Frontend                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Monolith:                    Micro Frontends:                       │
│  ┌────────────────┐          ┌────────┐ ┌────────┐ ┌────────┐      │
│  │                │          │Products│ │  Cart  │ │Checkout│      │
│  │  Single App    │    →     │ Team A │ │ Team B │ │ Team C │      │
│  │  Single Team   │          └────────┘ └────────┘ └────────┘      │
│  │  Single Deploy │                 ↓         ↓         ↓          │
│  │                │          ┌────────────────────────────────┐     │
│  └────────────────┘          │      Shell / Host App          │     │
│                              └────────────────────────────────┘     │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Benefits:**
1. **Independent Teams** - Teams own their domain end-to-end
2. **Independent Deployments** - Deploy without coordinating
3. **Technology Flexibility** - Different tech stacks possible
4. **Scalability** - Scale teams and apps independently
5. **Fault Isolation** - One MFE failure doesn't crash everything

**Challenges:**
1. Initial setup complexity
2. Shared state management
3. Consistent UX across MFEs
4. Bundle size with duplicated dependencies

---

### Q2: What is Module Federation?

**Answer:**
Module Federation is a Webpack 5 feature that allows JavaScript applications to dynamically load code from other applications at runtime.

**Key Concepts:**
- **Host (Shell)**: Main application that consumes remote modules
- **Remote**: Application that exposes modules to be consumed
- **Shared**: Dependencies shared between host and remotes

```typescript
// Remote configuration (exposes modules)
module.exports = withNativeFederation({
  name: 'products',
  exposes: {
    './ProductList': './src/app/products/product-list.component.ts'
  },
  shared: shareAll({ singleton: true })
});

// Host configuration (consumes remotes)
module.exports = withNativeFederation({
  name: 'shell',
  remotes: {
    'products': 'http://localhost:4201/remoteEntry.json'
  },
  shared: shareAll({ singleton: true })
});
```

---

### Q3: How do you load a remote module in Angular?

**Answer:**
Using `@angular-architects/native-federation`:

```typescript
// Dynamic route loading
import { loadRemoteModule } from '@angular-architects/native-federation';

export const routes: Routes = [
  {
    path: 'products',
    loadChildren: () => loadRemoteModule({
      remoteName: 'products',
      exposedModule: './ProductsRoutes'
    }).then(m => m.PRODUCT_ROUTES)
  },
  {
    path: 'cart',
    loadComponent: () => loadRemoteModule({
      remoteName: 'cart',
      exposedModule: './CartComponent'
    }).then(m => m.CartComponent)
  }
];
```

---

## Intermediate Level

### Q4: How do you handle shared state between micro frontends?

**Answer:**

**1. Custom Events (Simple communication):**
```typescript
// Dispatch from any MFE
window.dispatchEvent(new CustomEvent('user-logged-in', {
  detail: { userId: '123', name: 'John' }
}));

// Listen in any MFE
window.addEventListener('user-logged-in', (event: CustomEvent) => {
  this.user.set(event.detail);
});
```

**2. Shared Service (Singleton):**
```typescript
// Shared library exposed by all MFEs
@Injectable({ providedIn: 'root' })
export class GlobalStateService {
  private user$ = new BehaviorSubject<User | null>(null);
  
  getUser() { return this.user$.asObservable(); }
  setUser(user: User) { this.user$.next(user); }
}

// Works because Module Federation shares the singleton instance
```

**3. Message Bus Pattern:**
```typescript
@Injectable({ providedIn: 'root' })
export class EventBus {
  private events$ = new Subject<{type: string; payload: any}>();

  emit(type: string, payload: any) {
    this.events$.next({ type, payload });
  }

  on<T>(type: string): Observable<T> {
    return this.events$.pipe(
      filter(e => e.type === type),
      map(e => e.payload)
    );
  }
}
```

---

### Q5: How do you handle version conflicts in Module Federation?

**Answer:**
```typescript
// federation.config.js
shared: {
  '@angular/core': {
    singleton: true,        // Only one instance
    strictVersion: false,   // Allow compatible versions
    requiredVersion: '^17.0.0'  // Accept any 17.x
  },
  '@angular/common': {
    singleton: true,
    strictVersion: false,
    requiredVersion: '^17.0.0'
  },
  'rxjs': {
    singleton: true,
    strictVersion: false,
    requiredVersion: '^7.0.0'
  }
}
```

**Best Practices:**
1. **Use version ranges** (`^17.0.0` not `17.1.2`)
2. **Keep Angular versions aligned** across all MFEs
3. **Update together** for major versions
4. **Test compatibility** in staging environment

---

### Q6: How do you handle routing across micro frontends?

**Answer:**
```typescript
// Shell app owns top-level routing
// shell/src/app/app.routes.ts
export const routes: Routes = [
  { path: '', component: HomeComponent },
  
  // Each remote handles its own child routes
  {
    path: 'products',
    loadChildren: () => loadRemoteModule({
      remoteName: 'products',
      exposedModule: './ProductsRoutes'
    }).then(m => m.PRODUCT_ROUTES)
  },
  
  // Remote products defines its routes
  // /products → ProductListComponent
  // /products/:id → ProductDetailComponent
  
  { path: '**', component: NotFoundComponent }
];

// products/src/app/products.routes.ts
export const PRODUCT_ROUTES: Routes = [
  { path: '', component: ProductListComponent },
  { path: ':id', component: ProductDetailComponent }
];
```

**Cross-MFE Navigation:**
```typescript
// Navigate from products MFE to cart MFE
@Component({...})
export class ProductDetailComponent {
  private router = inject(Router);

  addToCartAndCheckout(product: Product) {
    // Dispatch event for cart MFE
    window.dispatchEvent(new CustomEvent('add-to-cart', {
      detail: product
    }));
    
    // Navigate to cart (owned by shell)
    this.router.navigate(['/cart']);
  }
}
```

---

## Advanced Level

### Q7: How do you implement authentication across micro frontends?

**Answer:**
```typescript
// Shared auth library
// libs/shared-auth/src/lib/auth.service.ts
@Injectable({ providedIn: 'root' })
export class AuthService {
  private token$ = new BehaviorSubject<string | null>(null);
  private user$ = new BehaviorSubject<User | null>(null);

  constructor() {
    // Initialize from storage
    const token = localStorage.getItem('auth_token');
    if (token) {
      this.token$.next(token);
      this.loadUser(token);
    }
  }

  login(credentials: Credentials): Observable<User> {
    return this.http.post<AuthResponse>('/api/login', credentials).pipe(
      tap(response => {
        localStorage.setItem('auth_token', response.token);
        this.token$.next(response.token);
        this.user$.next(response.user);
        
        // Notify all MFEs
        window.dispatchEvent(new CustomEvent('auth-state-changed', {
          detail: { isAuthenticated: true, user: response.user }
        }));
      }),
      map(r => r.user)
    );
  }

  logout() {
    localStorage.removeItem('auth_token');
    this.token$.next(null);
    this.user$.next(null);
    
    window.dispatchEvent(new CustomEvent('auth-state-changed', {
      detail: { isAuthenticated: false }
    }));
  }

  getToken(): string | null {
    return this.token$.getValue();
  }

  isAuthenticated$ = this.token$.pipe(map(t => !!t));
}

// HTTP Interceptor (shared)
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const token = auth.getToken();

  if (token) {
    req = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });
  }

  return next(req);
};
```

---

### Q8: How do you handle errors and fallbacks in micro frontends?

**Answer:**
```typescript
// Wrapper component for loading remotes
@Component({
  selector: 'app-remote-wrapper',
  template: `
    @switch (state()) {
      @case ('loading') {
        <app-skeleton [type]="skeletonType" />
      }
      @case ('error') {
        <div class="error-container">
          <mat-icon>error_outline</mat-icon>
          <p>{{ errorMessage() }}</p>
          <button mat-raised-button (click)="retry()">
            Retry
          </button>
        </div>
      }
      @case ('loaded') {
        <ng-container *ngComponentOutlet="component" />
      }
    }
  `
})
export class RemoteWrapperComponent implements OnInit {
  @Input() remoteName!: string;
  @Input() exposedModule!: string;
  @Input() skeletonType: 'card' | 'list' | 'form' = 'card';

  state = signal<'loading' | 'loaded' | 'error'>('loading');
  component: Type<any> | null = null;
  errorMessage = signal('');

  private retryCount = 0;
  private maxRetries = 3;

  async ngOnInit() {
    await this.loadRemote();
  }

  async loadRemote() {
    this.state.set('loading');

    try {
      const module = await loadRemoteModule({
        remoteName: this.remoteName,
        exposedModule: this.exposedModule
      });

      this.component = module[Object.keys(module)[0]];
      this.state.set('loaded');
      this.retryCount = 0;
    } catch (error) {
      this.handleError(error);
    }
  }

  private handleError(error: any) {
    console.error(`Failed to load ${this.remoteName}:`, error);
    
    if (this.retryCount < this.maxRetries) {
      // Auto-retry with exponential backoff
      const delay = Math.pow(2, this.retryCount) * 1000;
      setTimeout(() => this.loadRemote(), delay);
      this.retryCount++;
    } else {
      this.errorMessage.set('Failed to load module. Please try again.');
      this.state.set('error');
    }
  }

  retry() {
    this.retryCount = 0;
    this.loadRemote();
  }
}
```

---

### Q9: How do you deploy micro frontends independently?

**Answer:**

**Architecture:**
```
┌─────────────────────────────────────────────────────────────────────┐
│                    Deployment Architecture                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────┐                                                       │
│   │ Shell    │  → https://app.example.com                           │
│   │ (S3/CDN) │                                                       │
│   └──────────┘                                                       │
│                                                                       │
│   ┌──────────┐  ┌──────────┐  ┌──────────┐                         │
│   │ Products │  │   Cart   │  │ Checkout │                         │
│   │ (S3/CDN) │  │ (S3/CDN) │  │ (S3/CDN) │                         │
│   └──────────┘  └──────────┘  └──────────┘                         │
│        ↓              ↓             ↓                               │
│   products.        cart.        checkout.                           │
│   example.com     example.com   example.com                         │
│                                                                      │
│   Each deployed independently with own CI/CD                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Dynamic URL Resolution:**
```typescript
// Configuration service
@Injectable({ providedIn: 'root' })
export class FederationConfigService {
  private config = signal<FederationConfig | null>(null);

  async loadConfig(): Promise<void> {
    const response = await fetch('/api/federation-config');
    const config = await response.json();
    this.config.set(config);
    
    // Initialize federation with dynamic URLs
    await initFederation({
      products: config.remotes.products,
      cart: config.remotes.cart,
      checkout: config.remotes.checkout
    });
  }

  getRemoteUrl(remoteName: string): string {
    return this.config()?.remotes[remoteName] ?? '';
  }
}

// API returns different URLs per environment
// /api/federation-config
{
  "remotes": {
    "products": "https://products.prod.example.com/remoteEntry.json",
    "cart": "https://cart.prod.example.com/remoteEntry.json",
    "checkout": "https://checkout.prod.example.com/remoteEntry.json"
  }
}
```

---

### Q10: What are the trade-offs of micro frontends?

**Answer:**

| Pros | Cons |
|------|------|
| Independent deployments | Initial setup complexity |
| Team autonomy | Duplicate dependencies possible |
| Smaller, focused codebases | Cross-MFE testing harder |
| Technology flexibility | Consistent UX challenge |
| Fault isolation | Shared state complexity |
| Scalable teams | Performance overhead possible |

**When to use Micro Frontends:**
- ✅ Large teams (10+ developers)
- ✅ Multiple business domains
- ✅ Need independent deployments
- ✅ Long-term maintainability priority

**When NOT to use:**
- ❌ Small teams (< 5 developers)
- ❌ Simple applications
- ❌ Tight deadlines (high initial investment)
- ❌ Heavy cross-feature dependencies

---

## Scenario Questions

### Q11: How would you migrate a monolith to micro frontends?

**Answer:**

**Strangler Fig Pattern:**
```
Phase 1: Identify boundaries
────────────────────────────
Monolith: [Products | Cart | Checkout | User | Admin]
                ↓
Identify: Products is most independent, start there

Phase 2: Create shell + first MFE
─────────────────────────────────
┌─────────────────────────────────┐
│ Shell                           │
│ ┌─────────────────────────────┐ │
│ │ Remaining Monolith (iframe/ │ │
│ │ or integrated build)        │ │
│ └─────────────────────────────┘ │
│ ┌───────────┐                   │
│ │ Products  │ ← New MFE        │
│ │   MFE     │                   │
│ └───────────┘                   │
└─────────────────────────────────┘

Phase 3: Incrementally extract
──────────────────────────────
Extract Cart → Extract Checkout → Extract User

Phase 4: Retire monolith
────────────────────────
All features are now MFEs
```

**Key Steps:**
1. Create shell application
2. Set up Module Federation
3. Extract least-coupled feature first
4. Share authentication/common services
5. Gradually migrate remaining features
6. Retire original monolith

---

## Quick Reference

```
Module Federation Config:
─────────────────────────
Host (Shell):
  - remotes: { name: url }      // Remote locations
  - shared: { deps }            // Shared dependencies

Remote:
  - name: 'remote-name'         // Unique identifier
  - exposes: { './Module': path }  // Exposed modules
  - shared: { deps }            // Shared dependencies

Shared Options:
───────────────
singleton: true/false    // Single instance only
strictVersion: true/false // Exact version match
requiredVersion: '^x.x.x' // Version range
eager: true/false        // Load immediately

Communication Patterns:
───────────────────────
1. Custom Events     - Simple, loosely coupled
2. Shared Services   - Type-safe, singleton
3. Message Bus       - Pub/sub pattern
4. URL/Router        - Navigation-based
```
