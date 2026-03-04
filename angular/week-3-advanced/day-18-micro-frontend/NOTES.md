# Day 18: Micro Frontends with Angular

## Overview

Micro Frontends extend microservices architecture to the frontend, allowing independent teams to develop, deploy, and scale their applications independently.

---

## Micro Frontend Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Micro Frontend Architecture                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                         Shell/Host App                           │   │
│   │  ┌──────────────────────────────────────────────────────────┐   │   │
│   │  │                    Navigation / Layout                     │   │   │
│   │  └──────────────────────────────────────────────────────────┘   │   │
│   │                                                                  │   │
│   │  ┌────────────┐  ┌────────────┐  ┌────────────┐                │   │
│   │  │  Remote 1  │  │  Remote 2  │  │  Remote 3  │                │   │
│   │  │  (Team A)  │  │  (Team B)  │  │  (Team C)  │                │   │
│   │  │            │  │            │  │            │                │   │
│   │  │ Products   │  │   Cart     │  │  Checkout  │                │   │
│   │  │ Feature    │  │  Feature   │  │  Feature   │                │   │
│   │  └────────────┘  └────────────┘  └────────────┘                │   │
│   │                                                                  │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│   Each Remote:                                                           │
│   • Independent codebase                                                 │
│   • Independent deployments                                              │
│   • Own CI/CD pipeline                                                   │
│   • Own tech stack (potentially)                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Module Federation

Module Federation is a Webpack 5 feature that enables sharing code between applications at runtime.

### Setup with Native Federation

```bash
# Install Native Federation
npm install @angular-architects/native-federation -D

# Initialize host (shell) application
ng add @angular-architects/native-federation --project shell --type host

# Initialize remote application
ng add @angular-architects/native-federation --project products --type remote
```

### Host Application Configuration

```typescript
// shell/federation.config.js
const { withNativeFederation, shareAll } = require('@angular-architects/native-federation/config');

module.exports = withNativeFederation({
  name: 'shell',
  
  remotes: {
    'products': 'http://localhost:4201/remoteEntry.json',
    'cart': 'http://localhost:4202/remoteEntry.json',
  },

  shared: {
    ...shareAll({
      singleton: true,
      strictVersion: true,
      requiredVersion: 'auto'
    }),
  },

  skip: [
    'rxjs/ajax',
    'rxjs/fetch',
    'rxjs/testing',
    'rxjs/webSocket',
  ]
});
```

### Remote Application Configuration

```typescript
// products/federation.config.js
const { withNativeFederation, shareAll } = require('@angular-architects/native-federation/config');

module.exports = withNativeFederation({
  name: 'products',
  
  exposes: {
    './ProductsModule': './src/app/products/products.routes.ts',
    './ProductListComponent': './src/app/products/product-list.component.ts',
  },

  shared: {
    ...shareAll({
      singleton: true,
      strictVersion: true,
      requiredVersion: 'auto'
    }),
  },

  skip: [
    'rxjs/ajax',
    'rxjs/fetch',
    'rxjs/testing',
    'rxjs/webSocket',
  ]
});
```

---

## Loading Remote Modules

### Dynamic Route Loading

```typescript
// shell/src/app/app.routes.ts
import { loadRemoteModule } from '@angular-architects/native-federation';

export const routes: Routes = [
  {
    path: '',
    component: HomeComponent
  },
  {
    path: 'products',
    loadChildren: () => loadRemoteModule({
      remoteName: 'products',
      exposedModule: './ProductsModule'
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

### Dynamic Remote Configuration

```typescript
// For environments where remote URLs change
// shell/src/app/app.config.ts
import { initFederation } from '@angular-architects/native-federation';

export async function initializeApp(): Promise<ApplicationConfig> {
  // Load remote configuration from server
  const remoteConfig = await fetch('/api/federation-config').then(r => r.json());
  
  await initFederation({
    products: remoteConfig.productsUrl,
    cart: remoteConfig.cartUrl,
    checkout: remoteConfig.checkoutUrl
  });

  return {
    providers: [
      // ... other providers
    ]
  };
}
```

---

## Shared State Between Micro Frontends

### Using Custom Events

```typescript
// Shared event types
interface CartUpdateEvent {
  type: 'CART_UPDATE';
  payload: { itemCount: number };
}

// Shell application - listen for events
@Component({...})
export class ShellComponent {
  cartCount = signal(0);

  constructor() {
    window.addEventListener('mfe-cart-update', (event: CustomEvent) => {
      this.cartCount.set(event.detail.itemCount);
    });
  }
}

// Cart remote - dispatch events
@Injectable({ providedIn: 'root' })
export class CartService {
  private items = signal<CartItem[]>([]);

  addItem(item: CartItem) {
    this.items.update(items => [...items, item]);
    this.dispatchCartUpdate();
  }

  private dispatchCartUpdate() {
    window.dispatchEvent(new CustomEvent('mfe-cart-update', {
      detail: { itemCount: this.items().length }
    }));
  }
}
```

### Using Shared Service

```typescript
// Shared library package
// libs/shared-state/src/lib/shared-state.service.ts
@Injectable({ providedIn: 'root' })
export class SharedStateService {
  private state$ = new BehaviorSubject<GlobalState>({
    user: null,
    permissions: [],
    theme: 'light'
  });

  readonly user$ = this.state$.pipe(map(s => s.user));
  readonly theme$ = this.state$.pipe(map(s => s.theme));

  setUser(user: User | null) {
    this.updateState({ user });
  }

  setTheme(theme: 'light' | 'dark') {
    this.updateState({ theme });
  }

  private updateState(partial: Partial<GlobalState>) {
    this.state$.next({ ...this.state$.getValue(), ...partial });
  }
}

// Both host and remotes use the same shared service
// The service instance is shared via Module Federation
```

---

## Communication Patterns

### 1. Props/Inputs (Parent to Child)

```typescript
// Shell passes data to remote component
@Component({
  template: `
    <products-list 
      [category]="selectedCategory()"
      (productSelected)="onProductSelect($event)"
    />
  `
})
export class ShellComponent {
  selectedCategory = signal('electronics');

  onProductSelect(product: Product) {
    this.router.navigate(['/product', product.id]);
  }
}
```

### 2. Custom Events (Child to Parent)

```typescript
// Remote dispatches events
@Component({
  selector: 'products-list',
  template: `...`
})
export class ProductListComponent {
  @Output() productSelected = new EventEmitter<Product>();

  selectProduct(product: Product) {
    this.productSelected.emit(product);
    
    // Also dispatch global event for other remotes
    window.dispatchEvent(new CustomEvent('product-selected', {
      detail: product
    }));
  }
}
```

### 3. Shared Observables

```typescript
// Shared message bus
@Injectable({ providedIn: 'root' })
export class MessageBus {
  private messages$ = new Subject<Message>();

  send(message: Message) {
    this.messages$.next(message);
  }

  on<T>(type: string): Observable<T> {
    return this.messages$.pipe(
      filter(m => m.type === type),
      map(m => m.payload as T)
    );
  }
}

// Usage in any micro frontend
@Component({...})
export class SomeComponent {
  private messageBus = inject(MessageBus);

  ngOnInit() {
    this.messageBus.on<Product>('PRODUCT_ADDED_TO_CART')
      .subscribe(product => {
        this.showNotification(`${product.name} added to cart`);
      });
  }

  addToCart(product: Product) {
    this.messageBus.send({
      type: 'PRODUCT_ADDED_TO_CART',
      payload: product
    });
  }
}
```

---

## Version Conflict Handling

### Singleton Shared Dependencies

```typescript
// federation.config.js
module.exports = withNativeFederation({
  shared: {
    '@angular/core': {
      singleton: true,
      strictVersion: false,  // Allow minor version differences
      requiredVersion: '^17.0.0'
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
    },
    // Shared libraries
    '@myorg/ui-components': {
      singleton: true,
      strictVersion: true,
      requiredVersion: '^2.0.0'
    }
  }
});
```

### Version Negotiation

```typescript
// When versions conflict, Module Federation can:
// 1. Use highest version satisfying all requirements
// 2. Load separate versions (if singleton: false)
// 3. Fail (if strictVersion: true and incompatible)

// Best practice: Use version ranges
shared: {
  'lodash': {
    singleton: true,
    requiredVersion: '^4.17.0'  // Any 4.x version
  }
}
```

---

## Error Handling & Fallbacks

```typescript
// Loading remote with error handling
@Component({
  template: `
    @defer (on viewport) {
      <ng-container *ngComponentOutlet="remoteComponent" />
    } @error {
      <div class="error-fallback">
        <p>Failed to load module</p>
        <button (click)="retry()">Retry</button>
      </div>
    } @loading {
      <app-skeleton />
    }
  `
})
export class LazyRemoteComponent {
  remoteComponent: Type<any> | null = null;
  error = signal<Error | null>(null);

  async loadRemote() {
    try {
      const module = await loadRemoteModule({
        remoteName: 'products',
        exposedModule: './ProductsComponent'
      });
      this.remoteComponent = module.ProductsComponent;
    } catch (err) {
      this.error.set(err as Error);
      // Log to monitoring service
      this.monitoring.logError('Remote load failed', err);
    }
  }

  retry() {
    this.error.set(null);
    this.loadRemote();
  }
}
```

---

## Deployment Strategies

### Independent Deployment

```yaml
# GitHub Actions for remote deployment
name: Deploy Products Remote

on:
  push:
    paths:
      - 'apps/products/**'
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build
        run: |
          npm ci
          npm run build:products
      
      - name: Deploy to CDN
        run: |
          aws s3 sync dist/products s3://mfe-bucket/products
          aws cloudfront create-invalidation --distribution-id ${{ secrets.CF_DIST_ID }}
```

### Environment Configuration

```typescript
// environment.prod.ts
export const environment = {
  production: true,
  federation: {
    products: 'https://cdn.example.com/products/remoteEntry.json',
    cart: 'https://cdn.example.com/cart/remoteEntry.json',
    checkout: 'https://cdn.example.com/checkout/remoteEntry.json'
  }
};

// Dynamic configuration from API
async function loadFederationConfig(): Promise<FederationConfig> {
  const response = await fetch('/api/config/federation');
  return response.json();
}
```

---

## Best Practices

### 1. Shared UI Components Library

```bash
# Create shared library
ng generate library @myorg/ui-components

# Structure
libs/
  ui-components/
    src/
      lib/
        button/
        card/
        form-field/
        index.ts
```

### 2. Consistent Styling

```scss
// Shared design tokens
// libs/styles/tokens.scss
:root {
  --color-primary: #3f51b5;
  --color-accent: #ff4081;
  --spacing-unit: 8px;
  --border-radius: 4px;
  --font-family: 'Roboto', sans-serif;
}

// Each micro frontend imports shared tokens
@import '@myorg/styles/tokens';
```

### 3. Type Sharing

```typescript
// libs/shared-types/src/lib/models.ts
export interface Product {
  id: string;
  name: string;
  price: number;
  category: string;
}

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface User {
  id: string;
  name: string;
  email: string;
  roles: string[];
}
```

---

## Architecture Patterns

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Micro Frontend Patterns                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  1. Build-time Integration                                               │
│     └── NPM packages, bundled together                                   │
│     └── Simple but requires full rebuild                                 │
│                                                                          │
│  2. Runtime Integration (Module Federation)                              │
│     └── Dynamic loading at runtime                                       │
│     └── Independent deployments                                          │
│     └── Recommended for most cases                                       │
│                                                                          │
│  3. Server-side Composition                                              │
│     └── SSR assembles fragments                                          │
│     └── Good for SEO-critical pages                                      │
│                                                                          │
│  4. Edge-side Includes (ESI)                                            │
│     └── CDN/proxy assembles fragments                                    │
│     └── Good for caching individual fragments                            │
│                                                                          │
│  5. iframe Integration                                                   │
│     └── Complete isolation                                               │
│     └── Poor UX, limited communication                                   │
│     └── Use only when necessary                                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Summary

| Concept | Description |
|---------|-------------|
| Module Federation | Webpack 5 feature for runtime code sharing |
| Host/Shell | Main application that loads remotes |
| Remote | Independently deployed micro frontend |
| Shared Dependencies | Libraries shared between host and remotes |
| Singleton | Ensure single instance of shared library |
| Native Federation | Angular-specific implementation |
| Version Strategy | How to handle dependency version conflicts |
