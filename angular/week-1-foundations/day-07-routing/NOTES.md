# Day 7: Angular Routing - Comprehensive Guide

## Table of Contents
1. [Router Fundamentals](#router-fundamentals)
2. [RouterModule Configuration](#routermodule-configuration)
3. [Route Parameters](#route-parameters)
4. [Lazy Loading](#lazy-loading)
5. [Route Guards](#route-guards)
6. [Route Resolvers](#route-resolvers)
7. [Child & Auxiliary Routes](#child--auxiliary-routes)
8. [Preloading Strategies](#preloading-strategies)
9. [Router Events](#router-events)
10. [Route Animations](#route-animations)
11. [Component Input Binding](#component-input-binding)
12. [Quick Reference Card](#quick-reference-card)

---

## Router Fundamentals

### What is Angular Router?

The Angular Router is a powerful navigation library that enables navigation between views, URL manipulation, and lazy loading of feature modules.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANGULAR ROUTER ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Browser URL: /products/123?sort=price#details                 │
│        │                                                         │
│        ▼                                                         │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    Router Service                        │   │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐  │   │
│   │  │ URL Parser  │  │   Route     │  │     Route       │  │   │
│   │  │             │──▶│  Matcher    │──▶│   Recognizer   │  │   │
│   │  └─────────────┘  └─────────────┘  └─────────────────┘  │   │
│   └─────────────────────────────────────────────────────────┘   │
│        │                                                         │
│        ▼                                                         │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    Guards Pipeline                       │   │
│   │  canMatch → canActivateChild → canActivate → resolve     │   │
│   └─────────────────────────────────────────────────────────┘   │
│        │                                                         │
│        ▼                                                         │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    Component Activation                  │   │
│   │  <router-outlet> renders matched component               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Core Router Components

| Component | Purpose |
|-----------|---------|
| `Router` | Navigation service, provides `navigate()`, `navigateByUrl()` |
| `ActivatedRoute` | Access to route parameters, data, query params |
| `RouterLink` | Directive for template-based navigation |
| `RouterOutlet` | Placeholder where routed components render |
| `Routes` | Type for route configuration array |

---

## RouterModule Configuration

### Standalone Application Setup (Angular 22+)

```typescript
// app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideRouter, withComponentInputBinding, withPreloading, PreloadAllModules } from '@angular/router';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      withComponentInputBinding(),           // Enable route params as inputs
      withPreloading(PreloadAllModules),     // Preloading strategy
      withRouterConfig({
        paramsInheritanceStrategy: 'always', // Inherit params from parent
        onSameUrlNavigation: 'reload'        // Handle same URL navigation
      })
    )
  ]
};
```

### Basic Routes Configuration

```typescript
// app.routes.ts
import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full'
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard.component')
      .then(m => m.DashboardComponent),
    title: 'Dashboard'  // Document title
  },
  {
    path: 'products',
    loadComponent: () => import('./products/products.component')
      .then(m => m.ProductsComponent)
  },
  {
    path: '**',  // Wildcard - catches unmatched routes
    loadComponent: () => import('./not-found/not-found.component')
      .then(m => m.NotFoundComponent)
  }
];
```

### Route Configuration Options

```typescript
interface Route {
  path?: string;                    // URL path segment
  pathMatch?: 'full' | 'prefix';    // Matching strategy
  component?: Type<any>;            // Eagerly loaded component
  loadComponent?: () => Promise<Type<any>>;  // Lazy load standalone
  loadChildren?: () => Promise<Routes>;       // Lazy load routes
  redirectTo?: string;              // Redirect target
  outlet?: string;                  // Named outlet
  canActivate?: CanActivateFn[];    // Guard functions
  canActivateChild?: CanActivateChildFn[];
  canDeactivate?: CanDeactivateFn[];
  canMatch?: CanMatchFn[];
  resolve?: { [key: string]: ResolveFn<any> };
  data?: { [key: string]: any };    // Static data
  title?: string | ResolveFn<string>;  // Page title
  children?: Routes;                // Child routes
}
```

---

## Route Parameters

### Types of Route Parameters

```
┌─────────────────────────────────────────────────────────────────┐
│                 ROUTE PARAMETER TYPES                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  URL: /products/123;color=red?sort=price&order=asc#reviews      │
│       ├────────┘ ├─────────┘ ├────────────────────┘├───────┘    │
│       │          │           │                     │             │
│       │          │           │                     └─ Fragment   │
│       │          │           └─ Query Parameters                 │
│       │          └─ Matrix Parameters                            │
│       └─ Path Parameters                                         │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Parameter Type  │  Scope       │  Use Case                      │
│  ─────────────── │ ──────────── │ ────────────────────────────── │
│  Path (:id)      │  Required    │  Resource identification       │
│  Matrix (;key)   │  Optional    │  Filter/view state per route   │
│  Query (?key)    │  Global      │  Sorting, pagination, filters  │
│  Fragment (#)    │  Page anchor │  Scroll to section             │
└─────────────────────────────────────────────────────────────────┘
```

### Path Parameters

```typescript
// Route configuration
{
  path: 'products/:productId',
  loadComponent: () => import('./product-detail/product-detail.component')
    .then(m => m.ProductDetailComponent)
}

// product-detail.component.ts
import { Component, inject, input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-product-detail',
  standalone: true,
  template: `
    <h1>Product ID: {{ productId() }}</h1>
    <!-- Or using activated route -->
    <h2>Via Route: {{ productIdFromRoute() }}</h2>
  `
})
export class ProductDetailComponent {
  // New way: Component input binding (requires withComponentInputBinding())
  productId = input<string>();

  // Traditional way: ActivatedRoute
  private route = inject(ActivatedRoute);

  productIdFromRoute = toSignal(
    this.route.paramMap.pipe(
      map(params => params.get('productId'))
    )
  );
}
```

### Query Parameters

```typescript
// Navigation with query params
import { Component, inject } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  standalone: true,
  template: `
    <!-- Template navigation -->
    <a [routerLink]="['/products']"
       [queryParams]="{ sort: 'price', order: 'asc' }"
       [queryParamsHandling]="'merge'">
      Sort by Price
    </a>

    <!-- Fragment navigation -->
    <a [routerLink]="['/products', 123]"
       [fragment]="'reviews'">
      View Reviews
    </a>
  `
})
export class ProductListComponent {
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  // Programmatic navigation
  navigateWithQuery() {
    this.router.navigate(['/products'], {
      queryParams: {
        page: 1,
        sort: 'name',
        filter: ['active', 'featured']  // Array params
      },
      queryParamsHandling: 'merge'  // 'preserve' | 'merge' | ''
    });
  }

  // Reading query params as signals
  queryParams = toSignal(this.route.queryParamMap);

  // With component input binding
  sort = input<string>();
  page = input<number>();
}
```

### Matrix Parameters

```typescript
// Matrix parameters are route-specific
// URL: /products;category=electronics/123;color=red

{
  path: 'products',
  loadComponent: () => import('./products.component'),
  children: [
    {
      path: ':id',
      loadComponent: () => import('./product-detail.component')
    }
  ]
}

// Navigation with matrix params
this.router.navigate([
  '/products', { category: 'electronics' },
  '123', { color: 'red', size: 'large' }
]);

// Template syntax
<a [routerLink]="['/products', { category: 'electronics' }, productId, { color: selectedColor }]">
  View Product
</a>
```

---

## Lazy Loading

### Lazy Loading with loadComponent

```typescript
// Lazy loading standalone components
export const routes: Routes = [
  {
    path: 'admin',
    loadComponent: () => import('./admin/admin.component')
      .then(m => m.AdminComponent),
    canActivate: [authGuard]
  },
  {
    path: 'profile',
    loadComponent: () => import('./profile/profile.component')
      .then(c => c.ProfileComponent)
  }
];
```

### Lazy Loading with loadChildren

```typescript
// Lazy loading child routes
export const routes: Routes = [
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.routes')
      .then(m => m.ADMIN_ROUTES),
    canMatch: [adminGuard]
  }
];

// admin/admin.routes.ts
import { Routes } from '@angular/router';

export const ADMIN_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./admin-layout/admin-layout.component')
      .then(m => m.AdminLayoutComponent),
    children: [
      {
        path: 'users',
        loadComponent: () => import('./users/users.component')
          .then(m => m.UsersComponent)
      },
      {
        path: 'settings',
        loadComponent: () => import('./settings/settings.component')
          .then(m => m.SettingsComponent)
      }
    ]
  }
];
```

### Lazy Loading Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    LAZY LOADING FLOW                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   User navigates to /admin                                       │
│          │                                                       │
│          ▼                                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Router checks canMatch guards                           │   │
│   │  (runs BEFORE lazy loading)                              │   │
│   └─────────────────────────────────────────────────────────┘   │
│          │ ✓ Pass                                                │
│          ▼                                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  loadChildren/loadComponent triggered                    │   │
│   │  Network request for chunk file                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│          │ Chunk loaded                                          │
│          ▼                                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  canActivate guards run                                  │   │
│   │  Resolvers execute                                       │   │
│   └─────────────────────────────────────────────────────────┘   │
│          │ ✓ All pass                                            │
│          ▼                                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Component instantiated and rendered                     │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Route Guards

### Guard Types Comparison

```
┌────────────────────────────────────────────────────────────────────────┐
│                         ROUTE GUARDS PIPELINE                           │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   Navigation Request                                                    │
│         │                                                               │
│         ▼                                                               │
│   ┌───────────────┐                                                     │
│   │   canMatch    │ ◄─── Runs FIRST, before lazy loading               │
│   │               │      Can prevent route from matching                │
│   └───────┬───────┘      Useful for A/B testing, feature flags         │
│           │ ✓                                                           │
│           ▼                                                             │
│   ┌───────────────┐                                                     │
│   │ canActivate   │ ◄─── Auth check, permission validation             │
│   │  Child        │      Protects ALL child routes                     │
│   └───────┬───────┘                                                     │
│           │ ✓                                                           │
│           ▼                                                             │
│   ┌───────────────┐                                                     │
│   │  canActivate  │ ◄─── Auth check for specific route                 │
│   │               │      Most commonly used guard                      │
│   └───────┬───────┘                                                     │
│           │ ✓                                                           │
│           ▼                                                             │
│   ┌───────────────┐                                                     │
│   │   resolve     │ ◄─── Pre-fetch data before activation              │
│   │               │      Component waits for data                      │
│   └───────┬───────┘                                                     │
│           │ ✓                                                           │
│           ▼                                                             │
│   ┌───────────────┐                                                     │
│   │ canDeactivate │ ◄─── Runs when LEAVING route                       │
│   │               │      Unsaved changes warning                       │
│   └───────┬───────┘                                                     │
│           │ ✓                                                           │
│           ▼                                                             │
│       Navigation                                                        │
│       Complete                                                          │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
```

### Functional Guards (Modern Approach)

```typescript
// guards/auth.guard.ts
import { inject } from '@angular/core';
import { Router, CanActivateFn, CanMatchFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

// canActivate - Protects route activation
export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  // Redirect to login with return URL
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url }
  });
};

// canMatch - Runs before lazy loading (Angular 15+)
export const adminGuard: CanMatchFn = (route, segments) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.hasRole('admin')) {
    return true;
  }

  // Return false = route doesn't match, try next route
  // Return UrlTree = redirect
  return router.createUrlTree(['/unauthorized']);
};

// canActivateChild - Protects all children
export const parentGuard: CanActivateChildFn = (childRoute, state) => {
  const authService = inject(AuthService);
  return authService.canAccessSection(childRoute.data['section']);
};
```

### canDeactivate Guard

```typescript
// guards/unsaved-changes.guard.ts
import { CanDeactivateFn } from '@angular/router';
import { inject } from '@angular/core';

// Interface for components with unsaved changes
export interface HasUnsavedChanges {
  hasUnsavedChanges(): boolean;
}

export const unsavedChangesGuard: CanDeactivateFn<HasUnsavedChanges> = (
  component,
  currentRoute,
  currentState,
  nextState
) => {
  if (component.hasUnsavedChanges()) {
    return window.confirm(
      'You have unsaved changes. Do you really want to leave?'
    );
  }
  return true;
};

// Usage in component
@Component({
  standalone: true,
  template: `
    <form [formGroup]="form">
      <input formControlName="name">
      <button (click)="save()">Save</button>
    </form>
  `
})
export class EditFormComponent implements HasUnsavedChanges {
  form = inject(FormBuilder).group({
    name: ['']
  });

  private saved = false;

  hasUnsavedChanges(): boolean {
    return this.form.dirty && !this.saved;
  }

  save() {
    // Save logic
    this.saved = true;
  }
}

// Route configuration
{
  path: 'edit/:id',
  loadComponent: () => import('./edit-form.component'),
  canDeactivate: [unsavedChangesGuard]
}
```

### Async Guards with Observables

```typescript
// guards/permission.guard.ts
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { PermissionService } from '../services/permission.service';
import { map, take, catchError } from 'rxjs/operators';
import { of } from 'rxjs';

export const permissionGuard: CanActivateFn = (route, state) => {
  const permissionService = inject(PermissionService);
  const router = inject(Router);
  const requiredPermission = route.data['permission'];

  return permissionService.checkPermission(requiredPermission).pipe(
    take(1),
    map(hasPermission => {
      if (hasPermission) {
        return true;
      }
      return router.createUrlTree(['/access-denied']);
    }),
    catchError(() => of(router.createUrlTree(['/error'])))
  );
};

// Route with permission
{
  path: 'admin/users',
  loadComponent: () => import('./users.component'),
  canActivate: [authGuard, permissionGuard],
  data: { permission: 'users:manage' }
}
```

---

## Route Resolvers

### Functional Resolvers

```typescript
// resolvers/product.resolver.ts
import { inject } from '@angular/core';
import { ResolveFn, Router } from '@angular/router';
import { ProductService } from '../services/product.service';
import { Product } from '../models/product.model';
import { catchError, EMPTY } from 'rxjs';

export const productResolver: ResolveFn<Product> = (route, state) => {
  const productService = inject(ProductService);
  const router = inject(Router);
  const productId = route.paramMap.get('id')!;

  return productService.getProduct(productId).pipe(
    catchError(error => {
      console.error('Error loading product:', error);
      router.navigate(['/products']);
      return EMPTY;  // Cancels navigation
    })
  );
};

// Title resolver
export const productTitleResolver: ResolveFn<string> = (route, state) => {
  const productService = inject(ProductService);
  const productId = route.paramMap.get('id')!;

  return productService.getProduct(productId).pipe(
    map(product => `${product.name} - Product Details`)
  );
};

// Route configuration
{
  path: 'products/:id',
  loadComponent: () => import('./product-detail.component'),
  resolve: {
    product: productResolver
  },
  title: productTitleResolver  // Dynamic page title
}

// product-detail.component.ts
@Component({
  standalone: true,
  template: `
    <h1>{{ product()?.name }}</h1>
    <p>{{ product()?.description }}</p>
  `
})
export class ProductDetailComponent {
  // With component input binding
  product = input<Product>();

  // Or traditional way
  private route = inject(ActivatedRoute);
  productFromRoute = toSignal(
    this.route.data.pipe(map(data => data['product']))
  );
}
```

### Resolver Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    RESOLVER EXECUTION FLOW                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Navigation to /products/123                                    │
│          │                                                       │
│          ▼                                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Guards Pass                                             │   │
│   └─────────────────────────────────────────────────────────┘   │
│          │                                                       │
│          ▼                                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Resolvers Execute (in parallel)                         │   │
│   │                                                          │   │
│   │   productResolver ─────┐                                 │   │
│   │   reviewsResolver ─────┼──► Promise.all / forkJoin       │   │
│   │   relatedResolver ─────┘                                 │   │
│   │                                                          │   │
│   │   ⏳ Component NOT rendered yet                          │   │
│   │   ⏳ Loading indicator can be shown                      │   │
│   └─────────────────────────────────────────────────────────┘   │
│          │                                                       │
│          ▼                                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  All Resolvers Complete                                  │   │
│   │                                                          │   │
│   │  route.data = {                                          │   │
│   │    product: { id: 123, name: '...' },                    │   │
│   │    reviews: [...],                                       │   │
│   │    related: [...]                                        │   │
│   │  }                                                       │   │
│   └─────────────────────────────────────────────────────────┘   │
│          │                                                       │
│          ▼                                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Component Rendered with Data                            │   │
│   │  Data available via ActivatedRoute or input()            │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Child & Auxiliary Routes

### Child Routes Configuration

```typescript
// app.routes.ts
export const routes: Routes = [
  {
    path: 'products',
    loadComponent: () => import('./products/products-layout.component')
      .then(m => m.ProductsLayoutComponent),
    children: [
      {
        path: '',  // /products
        loadComponent: () => import('./products/product-list.component')
          .then(m => m.ProductListComponent)
      },
      {
        path: ':id',  // /products/123
        loadComponent: () => import('./products/product-detail.component')
          .then(m => m.ProductDetailComponent),
        children: [
          {
            path: '',  // /products/123 (default)
            redirectTo: 'overview',
            pathMatch: 'full'
          },
          {
            path: 'overview',  // /products/123/overview
            loadComponent: () => import('./products/product-overview.component')
          },
          {
            path: 'specs',  // /products/123/specs
            loadComponent: () => import('./products/product-specs.component')
          },
          {
            path: 'reviews',  // /products/123/reviews
            loadComponent: () => import('./products/product-reviews.component')
          }
        ]
      }
    ]
  }
];
```

### Child Routes Visual

```
┌─────────────────────────────────────────────────────────────────┐
│                    NESTED ROUTES STRUCTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   URL: /products/123/reviews                                     │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  AppComponent                                            │   │
│   │  ┌─────────────────────────────────────────────────────┐│   │
│   │  │  <router-outlet>                                    ││   │
│   │  │  ┌───────────────────────────────────────────────┐  ││   │
│   │  │  │  ProductsLayoutComponent  (path: 'products')  │  ││   │
│   │  │  │  ┌─────────────────────────────────────────┐  │  ││   │
│   │  │  │  │  <router-outlet>                        │  │  ││   │
│   │  │  │  │  ┌───────────────────────────────────┐  │  │  ││   │
│   │  │  │  │  │  ProductDetailComponent (:id)     │  │  │  ││   │
│   │  │  │  │  │  ┌─────────────────────────────┐  │  │  │  ││   │
│   │  │  │  │  │  │  <router-outlet>            │  │  │  │  ││   │
│   │  │  │  │  │  │  ┌───────────────────────┐  │  │  │  │  ││   │
│   │  │  │  │  │  │  │ ProductReviewsComponent│  │  │  │  │  ││   │
│   │  │  │  │  │  │  │ (path: 'reviews')     │  │  │  │  │  ││   │
│   │  │  │  │  │  │  └───────────────────────┘  │  │  │  │  ││   │
│   │  │  │  │  │  └─────────────────────────────┘  │  │  │  ││   │
│   │  │  │  │  └───────────────────────────────────┘  │  │  ││   │
│   │  │  │  └─────────────────────────────────────────┘  │  ││   │
│   │  │  └───────────────────────────────────────────────┘  ││   │
│   │  └─────────────────────────────────────────────────────┘│   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Auxiliary Routes (Named Outlets)

```typescript
// Route configuration with named outlets
export const routes: Routes = [
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard.component')
  },
  {
    path: 'chat',
    loadComponent: () => import('./chat/chat.component'),
    outlet: 'sidebar'  // Named outlet
  },
  {
    path: 'notifications',
    loadComponent: () => import('./notifications/notifications.component'),
    outlet: 'sidebar'
  },
  {
    path: 'help',
    loadComponent: () => import('./help/help-popup.component'),
    outlet: 'popup'
  }
];

// app.component.ts
@Component({
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <div class="main-content">
      <router-outlet></router-outlet>
    </div>

    <aside class="sidebar">
      <router-outlet name="sidebar"></router-outlet>
    </aside>

    <div class="popup-container">
      <router-outlet name="popup"></router-outlet>
    </div>
  `
})
export class AppComponent {}
```

### Navigating to Auxiliary Routes

```typescript
// URL: /dashboard(sidebar:chat//popup:help)

// Template navigation
<a [routerLink]="[{ outlets: { sidebar: ['chat'] } }]">Open Chat</a>

<a [routerLink]="['/dashboard', { outlets: { sidebar: ['chat'], popup: ['help'] } }]">
  Open Dashboard with Chat and Help
</a>

// Close auxiliary route
<a [routerLink]="[{ outlets: { sidebar: null, popup: null } }]">Close Panels</a>

// Programmatic navigation
this.router.navigate([
  '/dashboard',
  { outlets: { sidebar: ['notifications'], popup: null } }
]);
```

---

## Preloading Strategies

### Built-in Strategies

```typescript
// app.config.ts
import {
  provideRouter,
  withPreloading,
  PreloadAllModules,
  NoPreloading
} from '@angular/router';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      // Option 1: No preloading (default)
      // withPreloading(NoPreloading)

      // Option 2: Preload all lazy routes
      withPreloading(PreloadAllModules)
    )
  ]
};
```

### Custom Preloading Strategy

```typescript
// strategies/selective-preloading.strategy.ts
import { Injectable } from '@angular/core';
import { PreloadingStrategy, Route } from '@angular/router';
import { Observable, of, timer } from 'rxjs';
import { mergeMap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class SelectivePreloadingStrategy implements PreloadingStrategy {
  preloadedRoutes: string[] = [];

  preload(route: Route, load: () => Observable<any>): Observable<any> {
    // Check if route should be preloaded
    if (route.data?.['preload'] === true) {
      // Optional delay to prioritize initial load
      const delay = route.data?.['preloadDelay'] || 0;

      return timer(delay).pipe(
        mergeMap(() => {
          console.log(`Preloading: ${route.path}`);
          this.preloadedRoutes.push(route.path!);
          return load();
        })
      );
    }

    return of(null);  // Don't preload
  }
}

// Route configuration
export const routes: Routes = [
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard.component'),
    data: { preload: true }  // Will be preloaded
  },
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.routes'),
    data: { preload: false }  // Won't be preloaded
  },
  {
    path: 'reports',
    loadComponent: () => import('./reports.component'),
    data: { preload: true, preloadDelay: 3000 }  // Delayed preload
  }
];

// app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      withPreloading(SelectivePreloadingStrategy)
    )
  ]
};
```

### Network-Aware Preloading

```typescript
// strategies/network-aware-preloading.strategy.ts
import { Injectable, inject } from '@angular/core';
import { PreloadingStrategy, Route } from '@angular/router';
import { Observable, of, EMPTY } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class NetworkAwarePreloadingStrategy implements PreloadingStrategy {

  preload(route: Route, load: () => Observable<any>): Observable<any> {
    // Check network conditions (Navigator API)
    const connection = (navigator as any).connection;

    if (connection) {
      // Don't preload on slow connections
      if (connection.saveData) {
        return of(null);
      }

      if (connection.effectiveType === '2g' || connection.effectiveType === 'slow-2g') {
        return of(null);
      }
    }

    // Only preload if marked for preloading
    if (route.data?.['preload']) {
      return load();
    }

    return of(null);
  }
}
```

### Preloading Strategy Comparison

```
┌─────────────────────────────────────────────────────────────────┐
│              PRELOADING STRATEGIES COMPARISON                    │
├──────────────────┬──────────────────────────────────────────────┤
│  Strategy        │  Behavior                                    │
├──────────────────┼──────────────────────────────────────────────┤
│  NoPreloading    │  Default. Load only when navigating.         │
│                  │  Minimal initial bandwidth.                  │
├──────────────────┼──────────────────────────────────────────────┤
│  PreloadAll      │  Load all lazy routes after initial load.    │
│  Modules         │  Fast subsequent navigation.                 │
│                  │  Higher bandwidth usage.                     │
├──────────────────┼──────────────────────────────────────────────┤
│  Selective       │  Preload only routes marked with             │
│  Preloading      │  data: { preload: true }.                    │
│                  │  Balanced approach.                          │
├──────────────────┼──────────────────────────────────────────────┤
│  Network-Aware   │  Adapts to connection quality.               │
│                  │  Best for mobile users.                      │
├──────────────────┼──────────────────────────────────────────────┤
│  On-Demand       │  Preload based on user behavior              │
│  (QuickLink)     │  (hover, viewport visibility).               │
└──────────────────┴──────────────────────────────────────────────┘
```

---

## Router Events

### Available Router Events

```typescript
// services/router-events.service.ts
import { Injectable, inject } from '@angular/core';
import { Router, Event, NavigationStart, NavigationEnd,
         NavigationCancel, NavigationError, GuardsCheckStart,
         GuardsCheckEnd, ResolveStart, ResolveEnd,
         RouteConfigLoadStart, RouteConfigLoadEnd } from '@angular/router';
import { filter, tap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class RouterEventsService {
  private router = inject(Router);

  init() {
    this.router.events.pipe(
      tap(event => this.logEvent(event))
    ).subscribe();
  }

  private logEvent(event: Event) {
    if (event instanceof NavigationStart) {
      console.log('Navigation started:', event.url);
      // Show loading indicator
    }
    else if (event instanceof RouteConfigLoadStart) {
      console.log('Lazy loading started:', event.route.path);
    }
    else if (event instanceof RouteConfigLoadEnd) {
      console.log('Lazy loading complete:', event.route.path);
    }
    else if (event instanceof GuardsCheckStart) {
      console.log('Guards check started');
    }
    else if (event instanceof GuardsCheckEnd) {
      console.log('Guards check complete:', event.shouldActivate);
    }
    else if (event instanceof ResolveStart) {
      console.log('Resolvers started');
    }
    else if (event instanceof ResolveEnd) {
      console.log('Resolvers complete');
    }
    else if (event instanceof NavigationEnd) {
      console.log('Navigation complete:', event.urlAfterRedirects);
      // Hide loading indicator, track analytics
    }
    else if (event instanceof NavigationCancel) {
      console.log('Navigation cancelled:', event.reason);
    }
    else if (event instanceof NavigationError) {
      console.error('Navigation error:', event.error);
    }
  }
}
```

### Router Events Timeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROUTER EVENTS TIMELINE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  NavigationStart                                                 │
│       │                                                          │
│       ▼                                                          │
│  RouteConfigLoadStart  ─── (if lazy loaded route)               │
│       │                                                          │
│       ▼                                                          │
│  RouteConfigLoadEnd                                              │
│       │                                                          │
│       ▼                                                          │
│  RoutesRecognized                                                │
│       │                                                          │
│       ▼                                                          │
│  GuardsCheckStart                                                │
│       │                                                          │
│       ├──▶ ChildActivationStart                                  │
│       │         │                                                │
│       │         ▼                                                │
│       │    ActivationStart                                       │
│       │         │                                                │
│       │         ▼                                                │
│       │    ActivationEnd                                         │
│       │         │                                                │
│       │         ▼                                                │
│       │    ChildActivationEnd                                    │
│       │                                                          │
│       ▼                                                          │
│  GuardsCheckEnd                                                  │
│       │                                                          │
│       ▼                                                          │
│  ResolveStart                                                    │
│       │                                                          │
│       ▼                                                          │
│  ResolveEnd                                                      │
│       │                                                          │
│       ▼                                                          │
│  NavigationEnd  ─────────────────────────────────────────────── │
│         │                                                        │
│         └──▶  (or NavigationCancel / NavigationError)           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Practical Loading Indicator

```typescript
// components/loading-indicator.component.ts
import { Component, inject } from '@angular/core';
import { Router, NavigationStart, NavigationEnd,
         NavigationCancel, NavigationError } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { filter, map, merge } from 'rxjs';

@Component({
  selector: 'app-loading-indicator',
  standalone: true,
  template: `
    @if (isLoading()) {
      <div class="loading-bar">
        <div class="progress"></div>
      </div>
    }
  `,
  styles: [`
    .loading-bar {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 3px;
      background: rgba(0,0,0,0.1);
    }
    .progress {
      height: 100%;
      background: #4285f4;
      animation: loading 2s ease-in-out infinite;
    }
    @keyframes loading {
      0% { width: 0; }
      50% { width: 70%; }
      100% { width: 100%; }
    }
  `]
})
export class LoadingIndicatorComponent {
  private router = inject(Router);

  private start$ = this.router.events.pipe(
    filter(e => e instanceof NavigationStart),
    map(() => true)
  );

  private end$ = this.router.events.pipe(
    filter(e =>
      e instanceof NavigationEnd ||
      e instanceof NavigationCancel ||
      e instanceof NavigationError
    ),
    map(() => false)
  );

  isLoading = toSignal(
    merge(this.start$, this.end$),
    { initialValue: false }
  );
}
```

---

## Route Animations

### Setting Up Route Animations

```typescript
// app.config.ts
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideAnimationsAsync()  // Enable animations
  ]
};
```

### Route Animation Definitions

```typescript
// animations/route.animations.ts
import {
  trigger, transition, style, animate, query, group
} from '@angular/animations';

export const routeAnimations = trigger('routeAnimations', [
  // Fade animation
  transition('* <=> *', [
    style({ position: 'relative' }),
    query(':enter, :leave', [
      style({
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%'
      })
    ], { optional: true }),
    query(':enter', [
      style({ opacity: 0 })
    ], { optional: true }),
    group([
      query(':leave', [
        animate('200ms ease-out', style({ opacity: 0 }))
      ], { optional: true }),
      query(':enter', [
        animate('300ms ease-out', style({ opacity: 1 }))
      ], { optional: true })
    ])
  ])
]);

// Slide animation
export const slideAnimation = trigger('slideAnimation', [
  transition('home => products', [
    query(':enter, :leave', style({ position: 'fixed', width: '100%' }), { optional: true }),
    group([
      query(':enter', [
        style({ transform: 'translateX(100%)' }),
        animate('0.5s ease-in-out', style({ transform: 'translateX(0%)' }))
      ], { optional: true }),
      query(':leave', [
        style({ transform: 'translateX(0%)' }),
        animate('0.5s ease-in-out', style({ transform: 'translateX(-100%)' }))
      ], { optional: true })
    ])
  ]),
  transition('products => home', [
    query(':enter, :leave', style({ position: 'fixed', width: '100%' }), { optional: true }),
    group([
      query(':enter', [
        style({ transform: 'translateX(-100%)' }),
        animate('0.5s ease-in-out', style({ transform: 'translateX(0%)' }))
      ], { optional: true }),
      query(':leave', [
        style({ transform: 'translateX(0%)' }),
        animate('0.5s ease-in-out', style({ transform: 'translateX(100%)' }))
      ], { optional: true })
    ])
  ])
]);
```

### Using Route Animations

```typescript
// app.component.ts
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { routeAnimations } from './animations/route.animations';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <main [@routeAnimations]="getRouteAnimationData()">
      <router-outlet #outlet="outlet"></router-outlet>
    </main>
  `,
  animations: [routeAnimations]
})
export class AppComponent {
  getRouteAnimationData() {
    // Returns animation state from route data
    return this.outlet?.activatedRouteData?.['animation'];
  }
}

// Route configuration with animation data
export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./home.component'),
    data: { animation: 'home' }
  },
  {
    path: 'products',
    loadComponent: () => import('./products.component'),
    data: { animation: 'products' }
  }
];
```

---

## Component Input Binding

### withComponentInputBinding() Feature

Angular 16+ allows route parameters to be bound directly to component inputs.

```typescript
// app.config.ts
import { provideRouter, withComponentInputBinding } from '@angular/router';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      withComponentInputBinding()  // Enable input binding
    )
  ]
};
```

### Using Input Binding

```typescript
// Route: /products/123?sort=price&featured=true#details
// Route config: { path: 'products/:id', ... }

@Component({
  standalone: true,
  template: `
    <h1>Product: {{ id() }}</h1>
    <p>Sort: {{ sort() }}</p>
    <p>Featured: {{ featured() }}</p>
    <p>Resolved Data: {{ product()?.name }}</p>
  `
})
export class ProductDetailComponent {
  // Path parameter (:id)
  id = input<string>();

  // Query parameters (?sort=price)
  sort = input<string>();

  // Query parameter with transform
  featured = input(false, {
    transform: (value: string) => value === 'true'
  });

  // Resolved data (from resolver)
  product = input<Product>();

  // Static route data
  // data: { permissions: ['read', 'write'] }
  permissions = input<string[]>();
}
```

### Input Binding Priority

```
┌─────────────────────────────────────────────────────────────────┐
│              INPUT BINDING RESOLUTION ORDER                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  When multiple sources have the same key, priority is:          │
│                                                                  │
│   1. Route data (static)          data: { id: 'static' }        │
│   2. Path parameters              :id in path                   │
│   3. Resolved data               resolve: { id: resolver }      │
│   4. Query parameters            ?id=value                      │
│   5. Matrix parameters           ;id=value                      │
│                                                                  │
│  ─────────────────────────────────────────────────────────────  │
│                                                                  │
│  @Input() binding works with:                                    │
│                                                                  │
│  • input() signal function (recommended)                        │
│  • @Input() decorator                                            │
│  • Both are populated automatically                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Complete Example

```typescript
// app.routes.ts
export const routes: Routes = [
  {
    path: 'users/:userId/posts/:postId',
    loadComponent: () => import('./post-detail.component'),
    resolve: {
      post: postResolver,
      comments: commentsResolver
    },
    data: {
      breadcrumb: 'Post Details',
      permissions: ['read']
    }
  }
];

// post-detail.component.ts
@Component({
  standalone: true,
  template: `
    <nav>{{ breadcrumb() }}</nav>

    <article>
      <h1>{{ post()?.title }}</h1>
      <p>User: {{ userId() }}, Post: {{ postId() }}</p>

      @if (showComments()) {
        <section>
          <h2>Comments ({{ comments()?.length }})</h2>
          @for (comment of comments(); track comment.id) {
            <div>{{ comment.text }}</div>
          }
        </section>
      }
    </article>
  `
})
export class PostDetailComponent {
  // Path parameters
  userId = input.required<string>();
  postId = input.required<string>();

  // Resolved data
  post = input<Post>();
  comments = input<Comment[]>();

  // Static route data
  breadcrumb = input<string>();
  permissions = input<string[]>();

  // Query parameter
  showComments = input(true, {
    transform: (v: string | boolean) =>
      typeof v === 'string' ? v !== 'false' : v
  });
}
```

---

## Quick Reference Card

### Router Provider Configuration

```typescript
provideRouter(
  routes,
  withComponentInputBinding(),           // Bind route params to inputs
  withPreloading(PreloadAllModules),     // Preloading strategy
  withDebugTracing(),                    // Debug logging
  withRouterConfig({
    paramsInheritanceStrategy: 'always', // 'emptyOnly' | 'always'
    onSameUrlNavigation: 'reload',       // 'ignore' | 'reload'
    urlUpdateStrategy: 'eager',          // 'deferred' | 'eager'
    canceledNavigationResolution: 'computed' // 'replace' | 'computed'
  }),
  withHashLocation(),                    // Use hash-based routing
  withInMemoryScrolling({
    scrollPositionRestoration: 'enabled', // 'disabled' | 'enabled' | 'top'
    anchorScrolling: 'enabled'
  }),
  withNavigationErrorHandler(err => {
    console.error('Navigation error:', err);
  }),
  withViewTransitions()                  // Enable View Transitions API
);
```

### Navigation Methods

```typescript
// Router service methods
router.navigate(['/path', param], {
  queryParams: { key: 'value' },
  queryParamsHandling: 'merge',  // 'preserve' | 'merge' | ''
  fragment: 'section',
  relativeTo: activatedRoute,
  skipLocationChange: false,
  replaceUrl: false,
  state: { data: 'custom' }      // History state
});

router.navigateByUrl('/absolute/path');
router.navigateByUrl(router.createUrlTree(['/path']));

// Get current URL
router.url;                      // Current URL string
router.getCurrentNavigation();   // Current navigation info
```

### RouterLink Directive

```html
<!-- Basic -->
<a routerLink="/products">Products</a>
<a [routerLink]="['/products', productId]">Product</a>

<!-- With params -->
<a [routerLink]="['/products']"
   [queryParams]="{ sort: 'price' }"
   [queryParamsHandling]="'merge'"
   [fragment]="'reviews'"
   [preserveFragment]="true"
   [skipLocationChange]="false"
   [replaceUrl]="false"
   [state]="{ from: 'list' }">
  View
</a>

<!-- Active state -->
<a routerLink="/products"
   routerLinkActive="active"
   [routerLinkActiveOptions]="{ exact: true }">
  Products
</a>
```

### Guard Function Signatures

```typescript
type CanActivateFn = (
  route: ActivatedRouteSnapshot,
  state: RouterStateSnapshot
) => Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree;

type CanActivateChildFn = (
  childRoute: ActivatedRouteSnapshot,
  state: RouterStateSnapshot
) => Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree;

type CanDeactivateFn<T> = (
  component: T,
  currentRoute: ActivatedRouteSnapshot,
  currentState: RouterStateSnapshot,
  nextState: RouterStateSnapshot
) => Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree;

type CanMatchFn = (
  route: Route,
  segments: UrlSegment[]
) => Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree;

type ResolveFn<T> = (
  route: ActivatedRouteSnapshot,
  state: RouterStateSnapshot
) => Observable<T> | Promise<T> | T;
```

### ActivatedRoute Properties

```typescript
// ActivatedRoute observables
route.params           // Observable<Params>
route.paramMap         // Observable<ParamMap>
route.queryParams      // Observable<Params>
route.queryParamMap    // Observable<ParamMap>
route.fragment         // Observable<string | null>
route.data             // Observable<Data>
route.url              // Observable<UrlSegment[]>
route.outlet           // string
route.component        // Type<any> | null
route.routeConfig      // Route | null

// Snapshot (current values)
route.snapshot.params
route.snapshot.paramMap.get('id')
route.snapshot.queryParams
route.snapshot.data
```

### Common Route Patterns

```typescript
// Redirect
{ path: '', redirectTo: '/home', pathMatch: 'full' }

// Wildcard (404)
{ path: '**', component: NotFoundComponent }

// Path with parameter
{ path: 'users/:id', component: UserComponent }

// Optional parameter via child routes
{
  path: 'products',
  children: [
    { path: '', component: ProductListComponent },
    { path: ':id', component: ProductDetailComponent }
  ]
}

// Multiple params
{ path: 'users/:userId/posts/:postId', component: PostComponent }

// Empty path with children (layout pattern)
{
  path: '',
  component: LayoutComponent,
  children: [
    { path: 'dashboard', component: DashboardComponent },
    { path: 'settings', component: SettingsComponent }
  ]
}
```

---

## Key Takeaways

1. **Use standalone components** with `loadComponent` for cleaner lazy loading
2. **Use functional guards** instead of class-based guards (modern approach)
3. **Enable `withComponentInputBinding()`** to simplify parameter handling
4. **Use appropriate preloading strategy** based on app needs and user network
5. **canMatch** runs before lazy loading - use for feature flags/A/B testing
6. **Router events** are powerful for loading states and analytics
7. **Path parameters** for required route identification, **query params** for optional/global state
8. **Resolvers** guarantee data before component renders - but can slow navigation
9. **Child routes** for nested UI, **auxiliary routes** for parallel content
10. **Route animations** require explicit setup but enhance UX significantly

---

## Further Reading

- [Angular Router Documentation](https://angular.io/guide/router)
- [Lazy Loading Feature Modules](https://angular.io/guide/lazy-loading-ngmodules)
- [Route Guards](https://angular.io/guide/router#milestone-5-route-guards)
- [Router Events](https://angular.io/api/router/RouterEvent)
