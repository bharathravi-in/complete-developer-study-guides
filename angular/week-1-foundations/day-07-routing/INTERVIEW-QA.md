# Day 7: Angular Routing - Interview Questions & Answers

## Table of Contents
1. [Router Fundamentals](#1-router-fundamentals)
2. [Lazy Loading](#2-lazy-loading)
3. [Route Guards](#3-route-guards)
4. [Route Parameters](#4-route-parameters)
5. [Child & Auxiliary Routes](#5-child--auxiliary-routes)
6. [Preloading Strategies](#6-preloading-strategies)
7. [Router Events](#7-router-events)
8. [Resolvers](#8-resolvers)
9. [withComponentInputBinding](#9-withcomponentinputbinding)
10. [canMatch vs canActivate](#10-canmatch-vs-canactivate)
11. [Router Configuration](#11-router-configuration)
12. [Navigation & URL Handling](#12-navigation--url-handling)
13. [Route Animations](#13-route-animations)
14. [Performance & Best Practices](#14-performance--best-practices)

---

## 1. Router Fundamentals

### Q1: Explain the Angular Router architecture and how navigation works internally.

**Answer:**

The Angular Router follows a sophisticated pipeline for handling navigation:

```
┌─────────────────────────────────────────────────────────────────┐
│                 ROUTER NAVIGATION PIPELINE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. PARSE URL                                                   │
│      └─── Break URL into segments, query params, fragment       │
│                                                                  │
│   2. APPLY REDIRECTS                                             │
│      └─── Process any redirectTo configurations                 │
│                                                                  │
│   3. RECOGNIZE ROUTES                                            │
│      └─── Match URL segments to route configurations            │
│                                                                  │
│   4. GUARD CHECKS                                                │
│      └─── canMatch → canActivateChild → canActivate             │
│                                                                  │
│   5. RESOLVE DATA                                                │
│      └─── Execute resolvers, wait for data                      │
│                                                                  │
│   6. ACTIVATE ROUTES                                             │
│      └─── Create component instances, update outlets            │
│                                                                  │
│   7. MANAGE NAVIGATION STATE                                     │
│      └─── Update browser URL, history state                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Components:**

```typescript
// Core router components
import { Router, ActivatedRoute, RouterOutlet, RouterLink } from '@angular/router';

// Router - Service for programmatic navigation
router.navigate(['/users', userId]);

// ActivatedRoute - Access to current route information
activatedRoute.paramMap.subscribe(params => {
  const id = params.get('id');
});

// RouterOutlet - Placeholder for routed components
<router-outlet></router-outlet>

// RouterLink - Template-based navigation
<a [routerLink]="['/users']">Users</a>
```

**Interview Tip:** Mention that the router uses Observables extensively and that navigation is asynchronous. Understanding the navigation lifecycle events helps in debugging routing issues.

---

## 2. Lazy Loading

### Q2: What is the difference between `loadComponent` and `loadChildren`? When would you use each?

**Answer:**

```
┌─────────────────────────────────────────────────────────────────┐
│          loadComponent vs loadChildren                           │
├────────────────────┬────────────────────────────────────────────┤
│   loadComponent    │   loadChildren                              │
├────────────────────┼────────────────────────────────────────────┤
│ Loads a single     │ Loads a set of routes (child               │
│ standalone         │ routes configuration)                      │
│ component          │                                            │
├────────────────────┼────────────────────────────────────────────┤
│ Simpler syntax     │ More flexible for complex                  │
│ for leaf routes    │ feature areas                              │
├────────────────────┼────────────────────────────────────────────┤
│ Component-level    │ Can lazy load multiple                     │
│ code splitting     │ components together                        │
├────────────────────┼────────────────────────────────────────────┤
│ Angular 14+        │ Available since Angular 2                  │
└────────────────────┴────────────────────────────────────────────┘
```

**loadComponent Example:**

```typescript
// Lazy loads a single standalone component
export const routes: Routes = [
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard.component')
      .then(m => m.DashboardComponent)
  },
  {
    path: 'profile',
    loadComponent: () => import('./profile/profile.component')
      .then(c => c.ProfileComponent)
  }
];
```

**loadChildren Example:**

```typescript
// app.routes.ts - Lazy loads child routes
export const routes: Routes = [
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.routes')
      .then(m => m.ADMIN_ROUTES)
  }
];

// admin/admin.routes.ts
export const ADMIN_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./admin-layout.component')
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

**When to use:**

- **loadComponent**: Simple routes, single components, no child routing needed
- **loadChildren**: Feature modules with multiple related routes, shared layout components

**Interview Tip:** Emphasize that in Angular 22+, standalone components with `loadComponent` are preferred for simpler code organization. `loadChildren` is still valuable for larger features with multiple routes.

---

## 3. Route Guards

### Q3: Explain all route guards and their execution order. How do you implement a functional guard?

**Answer:**

**Guard Execution Order:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    GUARD EXECUTION ORDER                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Navigation Request                                             │
│         │                                                        │
│         ▼                                                        │
│   ┌───────────────┐                                              │
│   │   canMatch    │  ◄── Runs FIRST, BEFORE lazy loading        │
│   │               │      Determines if route can match           │
│   └───────┬───────┘                                              │
│           │                                                      │
│           ▼  (Lazy loading happens here if needed)               │
│                                                                  │
│   ┌───────────────┐                                              │
│   │ canActivate   │  ◄── Protects child routes collectively     │
│   │    Child      │                                              │
│   └───────┬───────┘                                              │
│           │                                                      │
│           ▼                                                      │
│   ┌───────────────┐                                              │
│   │  canActivate  │  ◄── Protects specific route                │
│   │               │                                              │
│   └───────┬───────┘                                              │
│           │                                                      │
│           ▼                                                      │
│   ┌───────────────┐                                              │
│   │   resolve     │  ◄── Pre-fetches data                       │
│   │               │                                              │
│   └───────┬───────┘                                              │
│           │                                                      │
│           ▼                                                      │
│       Component                                                  │
│       Activated                                                  │
│           │                                                      │
│           ▼                                                      │
│   ┌───────────────┐                                              │
│   │ canDeactivate │  ◄── Runs when LEAVING                      │
│   │               │      (e.g., unsaved changes)                │
│   └───────────────┘                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Functional Guard Implementations (Angular 22+):**

```typescript
// auth.guard.ts - canActivate
import { inject } from '@angular/core';
import { Router, CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.isAuthenticated()) {
    return true;
  }

  // Store intended URL for redirect after login
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url }
  });
};

// admin.guard.ts - canMatch (runs before lazy loading)
import { CanMatchFn } from '@angular/router';

export const adminGuard: CanMatchFn = (route, segments) => {
  const authService = inject(AuthService);

  // If user is not admin, route won't even match
  // Router will try the next route configuration
  if (authService.hasRole('admin')) {
    return true;
  }

  // Return false to try next matching route
  // Return UrlTree to redirect
  return inject(Router).createUrlTree(['/unauthorized']);
};

// unsaved-changes.guard.ts - canDeactivate
export interface CanDeactivateComponent {
  canDeactivate(): boolean | Observable<boolean>;
}

export const unsavedChangesGuard: CanDeactivateFn<CanDeactivateComponent> = (
  component,
  currentRoute,
  currentState,
  nextState
) => {
  return component.canDeactivate?.() ?? true;
};
```

**Route Configuration:**

```typescript
export const routes: Routes = [
  {
    path: 'admin',
    canMatch: [adminGuard],  // Runs first
    loadChildren: () => import('./admin/admin.routes'),
    canActivateChild: [adminChildGuard]  // Protects all children
  },
  {
    path: 'profile/edit',
    loadComponent: () => import('./edit-profile.component'),
    canActivate: [authGuard],
    canDeactivate: [unsavedChangesGuard]
  }
];
```

**Interview Tip:** Emphasize the difference between `canMatch` and `canActivate` - `canMatch` is unique because it runs before lazy loading, making it perfect for role-based route protection where you don't want to load unnecessary code.

---

## 4. Route Parameters

### Q4: What are the different types of route parameters in Angular? How do you access them?

**Answer:**

```
┌─────────────────────────────────────────────────────────────────┐
│              URL: /products/123;view=grid?sort=price#specs      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  /products/123     ;view=grid      ?sort=price       #specs     │
│  ├──────────┘      ├─────────┘     ├──────────┘      ├─────┘    │
│  │                 │               │                 │          │
│  Path Param        Matrix Param   Query Param       Fragment    │
│  (required)        (route-local)  (global)          (anchor)    │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  Param Type    │ Survives     │ Scope      │ Use Case           │
│  ───────────── │ Navigation?  │ ────────── │ ─────────────────  │
│  Path (:id)    │ No           │ Single     │ Resource ID        │
│  Matrix (;k=v) │ No           │ Route-only │ View state         │
│  Query (?k=v)  │ Configurable │ Global     │ Filters, sorting   │
│  Fragment (#)  │ No           │ Page       │ Scroll to section  │
└─────────────────────────────────────────────────────────────────┘
```

**Accessing Parameters (Multiple Methods):**

```typescript
// product-detail.component.ts
import { Component, inject, input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs/operators';

@Component({
  standalone: true,
  template: `
    <h1>Product {{ productId() }}</h1>
    <p>Sort: {{ sort() }}</p>
  `
})
export class ProductDetailComponent {
  private route = inject(ActivatedRoute);

  // Method 1: Component Input Binding (requires withComponentInputBinding())
  // Automatically binds route params, query params, and resolved data
  productId = input<string>();  // From path :productId
  sort = input<string>();       // From query ?sort=

  // Method 2: ActivatedRoute with signals
  productIdSignal = toSignal(
    this.route.paramMap.pipe(map(params => params.get('productId')))
  );

  // Method 3: Snapshot (static, doesn't react to changes)
  productIdSnapshot = this.route.snapshot.paramMap.get('productId');

  // Method 4: Observable subscription (traditional)
  constructor() {
    this.route.paramMap.subscribe(params => {
      console.log('Product ID:', params.get('productId'));
    });

    this.route.queryParamMap.subscribe(params => {
      console.log('Sort:', params.get('sort'));
    });
  }
}
```

**Setting Parameters:**

```typescript
// Template-based navigation
<a [routerLink]="['/products', productId]"
   [queryParams]="{ sort: 'price', page: 1 }"
   [queryParamsHandling]="'merge'"
   [fragment]="'reviews'">
  View Product
</a>

// Programmatic navigation
this.router.navigate(['/products', this.productId], {
  queryParams: { sort: 'price', filter: 'active' },
  queryParamsHandling: 'merge',  // 'preserve' | 'merge' | ''
  fragment: 'reviews'
});

// Matrix parameters
this.router.navigate(['/products', { category: 'electronics' }, productId]);
// Results in: /products;category=electronics/123
```

**Interview Tip:** Mention that `paramMap` and `queryParamMap` are preferred over `params` and `queryParams` because they provide a `get()` method that handles missing params gracefully (returns null instead of undefined).

---

## 5. Child & Auxiliary Routes

### Q5: Explain child routes and auxiliary routes. When would you use auxiliary routes?

**Answer:**

**Child Routes:**

```typescript
// Nested routes for hierarchical UI
export const routes: Routes = [
  {
    path: 'products',
    loadComponent: () => import('./products-shell.component'),
    children: [
      {
        path: '',  // /products
        loadComponent: () => import('./product-list.component')
      },
      {
        path: ':id',  // /products/123
        loadComponent: () => import('./product-detail.component'),
        children: [
          { path: '', redirectTo: 'overview', pathMatch: 'full' },
          { path: 'overview', loadComponent: () => import('./overview.component') },
          { path: 'specs', loadComponent: () => import('./specs.component') },
          { path: 'reviews', loadComponent: () => import('./reviews.component') }
        ]
      }
    ]
  }
];
```

```
┌─────────────────────────────────────────────────────────────────┐
│              CHILD ROUTES - URL: /products/123/reviews          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  AppComponent                                            │   │
│   │  ┌─────────────────────────────────────────────────────┐│   │
│   │  │  <router-outlet>                                    ││   │
│   │  │  ┌───────────────────────────────────────────────┐  ││   │
│   │  │  │  ProductsShellComponent                       │  ││   │
│   │  │  │  - Navigation sidebar                         │  ││   │
│   │  │  │  ┌─────────────────────────────────────────┐  │  ││   │
│   │  │  │  │  <router-outlet>                        │  │  ││   │
│   │  │  │  │  ┌───────────────────────────────────┐  │  │  ││   │
│   │  │  │  │  │  ProductDetailComponent           │  │  │  ││   │
│   │  │  │  │  │  - Product header, tabs           │  │  │  ││   │
│   │  │  │  │  │  ┌─────────────────────────────┐  │  │  │  ││   │
│   │  │  │  │  │  │  <router-outlet>            │  │  │  │  ││   │
│   │  │  │  │  │  │  ┌───────────────────────┐  │  │  │  │  ││   │
│   │  │  │  │  │  │  │  ReviewsComponent     │  │  │  │  │  ││   │
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

**Auxiliary Routes (Named Outlets):**

```typescript
// Routes with named outlets
export const routes: Routes = [
  { path: 'dashboard', loadComponent: () => import('./dashboard.component') },
  {
    path: 'chat',
    loadComponent: () => import('./chat.component'),
    outlet: 'sidebar'  // Named outlet
  },
  {
    path: 'notifications',
    loadComponent: () => import('./notifications.component'),
    outlet: 'sidebar'
  },
  {
    path: 'quick-help',
    loadComponent: () => import('./help-modal.component'),
    outlet: 'modal'
  }
];
```

```typescript
// app.component.ts
@Component({
  template: `
    <div class="layout">
      <main>
        <router-outlet></router-outlet>  <!-- Primary outlet -->
      </main>

      <aside class="sidebar">
        <router-outlet name="sidebar"></router-outlet>  <!-- Named outlet -->
      </aside>

      <div class="modal-container">
        <router-outlet name="modal"></router-outlet>  <!-- Another named outlet -->
      </div>
    </div>
  `
})
export class AppComponent {}
```

**Navigating to Auxiliary Routes:**

```typescript
// URL: /dashboard(sidebar:chat//modal:quick-help)

// Template
<a [routerLink]="['/dashboard', { outlets: { sidebar: ['chat'] } }]">
  Open Chat
</a>

// Open multiple outlets
<a [routerLink]="['/dashboard', { outlets: { sidebar: ['chat'], modal: ['quick-help'] } }]">
  Open Chat & Help
</a>

// Close auxiliary route
<a [routerLink]="[{ outlets: { sidebar: null } }]">Close Sidebar</a>

// Programmatic
this.router.navigate([
  '/dashboard',
  { outlets: { sidebar: ['notifications'], modal: null } }
]);
```

**When to Use Auxiliary Routes:**

| Use Case | Example |
|----------|---------|
| Side panels | Chat, notifications panel |
| Modals/dialogs | Help dialogs with bookmarkable URLs |
| Split views | Email app (list + detail) |
| Persistent UI | Player controls, mini-cart |

**Interview Tip:** Auxiliary routes are less common but powerful for complex UIs. Mention that they allow independent navigation of multiple components while maintaining a single URL that represents the full application state.

---

## 6. Preloading Strategies

### Q6: What are preloading strategies and how do you implement a custom one?

**Answer:**

**Preloading Strategies Comparison:**

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PRELOADING STRATEGIES                                 │
├─────────────────────┬──────────────────────────────────────────────────┤
│  No Preloading      │  Load modules only when navigating              │
│  (Default)          │  Slowest subsequent navigation                  │
│                     │  Least initial bandwidth                        │
├─────────────────────┼──────────────────────────────────────────────────┤
│  PreloadAllModules  │  Preload all lazy modules after app loads       │
│                     │  Fastest subsequent navigation                  │
│                     │  Highest bandwidth usage                        │
├─────────────────────┼──────────────────────────────────────────────────┤
│  Custom Strategy    │  Selective preloading based on:                 │
│                     │  - Route data flags                             │
│                     │  - User role/behavior                           │
│                     │  - Network conditions                           │
│                     │  Best balance                                   │
└─────────────────────┴──────────────────────────────────────────────────┘
```

**Configuration:**

```typescript
// app.config.ts
import { provideRouter, withPreloading, PreloadAllModules } from '@angular/router';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      withPreloading(PreloadAllModules)  // or custom strategy
    )
  ]
};
```

**Custom Preloading Strategy:**

```typescript
// strategies/selective-preloading.strategy.ts
import { Injectable } from '@angular/core';
import { PreloadingStrategy, Route } from '@angular/router';
import { Observable, of, timer } from 'rxjs';
import { mergeMap } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class SelectivePreloadingStrategy implements PreloadingStrategy {
  preloadedModules: string[] = [];

  preload(route: Route, loadFn: () => Observable<any>): Observable<any> {
    // Check if route has preload flag
    if (route.data?.['preload'] === true) {
      const delay = route.data?.['preloadDelay'] || 0;

      return timer(delay).pipe(
        mergeMap(() => {
          console.log(`Preloading: ${route.path}`);
          this.preloadedModules.push(route.path!);
          return loadFn();
        })
      );
    }

    return of(null);  // Don't preload
  }
}

// Network-aware preloading
@Injectable({ providedIn: 'root' })
export class NetworkAwarePreloadingStrategy implements PreloadingStrategy {
  preload(route: Route, loadFn: () => Observable<any>): Observable<any> {
    // Check connection quality
    const connection = (navigator as any).connection;

    if (connection) {
      // Don't preload on slow connections or data saver mode
      if (connection.saveData ||
          connection.effectiveType === '2g' ||
          connection.effectiveType === 'slow-2g') {
        return of(null);
      }
    }

    // Only preload routes marked for preloading
    if (route.data?.['preload']) {
      return loadFn();
    }

    return of(null);
  }
}
```

**Route Configuration with Preload Data:**

```typescript
export const routes: Routes = [
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard.component'),
    data: { preload: true }  // Will preload immediately
  },
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.routes'),
    data: { preload: false }  // Won't preload (admin-only)
  },
  {
    path: 'reports',
    loadComponent: () => import('./reports.component'),
    data: { preload: true, preloadDelay: 5000 }  // Preload after 5s
  }
];
```

**Interview Tip:** Mention that preloading happens in the background after the initial application loads. For mobile-first apps, network-aware preloading is important to avoid wasting user bandwidth on slow connections.

---

## 7. Router Events

### Q7: What router events are available and how would you use them for a loading indicator?

**Answer:**

**Router Events Timeline:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROUTER EVENTS SEQUENCE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   NavigationStart         ─── Show loading indicator            │
│         │                                                        │
│         ▼                                                        │
│   RouteConfigLoadStart    ─── Lazy loading begins               │
│         │                                                        │
│         ▼                                                        │
│   RouteConfigLoadEnd      ─── Lazy loading complete             │
│         │                                                        │
│         ▼                                                        │
│   RoutesRecognized        ─── Routes matched                    │
│         │                                                        │
│         ▼                                                        │
│   GuardsCheckStart        ─── Guards begin                      │
│         │                                                        │
│         ▼                                                        │
│   ChildActivationStart    ─── Per child route                   │
│         │                                                        │
│         ▼                                                        │
│   ActivationStart         ─── Per route                         │
│         │                                                        │
│         ▼                                                        │
│   ActivationEnd                                                  │
│         │                                                        │
│         ▼                                                        │
│   ChildActivationEnd                                             │
│         │                                                        │
│         ▼                                                        │
│   GuardsCheckEnd          ─── Guards complete                   │
│         │                                                        │
│         ▼                                                        │
│   ResolveStart            ─── Resolvers begin                   │
│         │                                                        │
│         ▼                                                        │
│   ResolveEnd              ─── Resolvers complete                │
│         │                                                        │
│         ▼                                                        │
│   NavigationEnd           ─── Hide loading, track analytics     │
│                                                                  │
│   (or NavigationCancel / NavigationError)                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Loading Indicator Implementation:**

```typescript
// services/loading.service.ts
import { Injectable, signal, inject } from '@angular/core';
import { Router, NavigationStart, NavigationEnd,
         NavigationCancel, NavigationError } from '@angular/router';
import { filter } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class LoadingService {
  private router = inject(Router);
  
  isLoading = signal(false);

  constructor() {
    this.router.events.pipe(
      filter(event =>
        event instanceof NavigationStart ||
        event instanceof NavigationEnd ||
        event instanceof NavigationCancel ||
        event instanceof NavigationError
      )
    ).subscribe(event => {
      this.isLoading.set(event instanceof NavigationStart);
    });
  }
}

// components/loading-bar.component.ts
@Component({
  selector: 'app-loading-bar',
  standalone: true,
  template: `
    @if (loadingService.isLoading()) {
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
      z-index: 9999;
    }
    .progress {
      height: 100%;
      background: linear-gradient(90deg, #4285f4, #34a853);
      animation: loading 2s ease-in-out infinite;
    }
    @keyframes loading {
      0% { width: 0; }
      50% { width: 70%; }
      100% { width: 100%; }
    }
  `]
})
export class LoadingBarComponent {
  loadingService = inject(LoadingService);
}
```

**Analytics with Router Events:**

```typescript
// services/analytics.service.ts
@Injectable({ providedIn: 'root' })
export class AnalyticsService {
  private router = inject(Router);

  init() {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      // Track page view
      this.trackPageView(event.urlAfterRedirects);
    });
  }

  private trackPageView(url: string) {
    // Google Analytics, etc.
    console.log('Page view:', url);
  }
}
```

**Interview Tip:** Router events are Observables, so they integrate well with RxJS. Mention that `NavigationCancel` and `NavigationError` must also be handled to properly hide loading indicators even when navigation fails.

---

## 8. Resolvers

### Q8: What are resolvers and how do they differ from fetching data in ngOnInit?

**Answer:**

```
┌─────────────────────────────────────────────────────────────────┐
│              RESOLVER vs ngOnInit DATA FETCHING                  │
├────────────────────────┬────────────────────────────────────────┤
│       Resolver         │         ngOnInit                       │
├────────────────────────┼────────────────────────────────────────┤
│ Data loaded BEFORE     │ Component renders FIRST,               │
│ component renders      │ then data loads                        │
├────────────────────────┼────────────────────────────────────────┤
│ Component guaranteed   │ Must handle loading states             │
│ to have data           │ in component                           │
├────────────────────────┼────────────────────────────────────────┤
│ Navigation waits       │ Navigation completes                   │
│ for data               │ immediately                            │
├────────────────────────┼────────────────────────────────────────┤
│ Loading indicator at   │ Loading indicator in                   │
│ router level           │ each component                         │
├────────────────────────┼────────────────────────────────────────┤
│ Can block navigation   │ Always navigates                       │
│ on error               │ (handle error in component)            │
└────────────────────────┴────────────────────────────────────────┘
```

**Resolver Implementation:**

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
      console.error('Failed to load product:', error);
      router.navigate(['/products']);  // Redirect on error
      return EMPTY;  // Cancel navigation
    })
  );
};

// Multiple resolvers
export const productReviewsResolver: ResolveFn<Review[]> = (route) => {
  const productService = inject(ProductService);
  const productId = route.paramMap.get('id')!;
  return productService.getReviews(productId);
};
```

**Route Configuration:**

```typescript
export const routes: Routes = [
  {
    path: 'products/:id',
    loadComponent: () => import('./product-detail.component'),
    resolve: {
      product: productResolver,
      reviews: productReviewsResolver
    },
    title: productTitleResolver  // Dynamic page title
  }
];
```

**Accessing Resolved Data:**

```typescript
// product-detail.component.ts
@Component({
  standalone: true,
  template: `
    <!-- Data guaranteed to exist -->
    <h1>{{ product()?.name }}</h1>
    
    @for (review of reviews(); track review.id) {
      <app-review [review]="review"></app-review>
    }
  `
})
export class ProductDetailComponent {
  // Method 1: Component input binding (requires withComponentInputBinding())
  product = input<Product>();
  reviews = input<Review[]>();

  // Method 2: ActivatedRoute
  private route = inject(ActivatedRoute);
  
  productFromRoute = toSignal(
    this.route.data.pipe(map(data => data['product']))
  );
}
```

**When to Use Resolvers:**

| Use Resolvers When | Use ngOnInit When |
|-------------------|-------------------|
| Data is critical for the view | Data can load progressively |
| Want to prevent partial renders | Want faster perceived navigation |
| Single source of loading UI | Component-specific loading states |
| Data errors should block nav | Graceful error handling in component |

**Interview Tip:** Mention that resolvers run in parallel. If one resolver returns EMPTY or errors, navigation is cancelled. Consider whether blocking navigation is desired - sometimes showing a skeleton UI with ngOnInit loading is better UX.

---

## 9. withComponentInputBinding

### Q9: Explain withComponentInputBinding() and its advantages over traditional parameter access.

**Answer:**

**Traditional vs Input Binding:**

```typescript
// app.config.ts - Enable feature
import { provideRouter, withComponentInputBinding } from '@angular/router';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      withComponentInputBinding()  // Enable the feature
    )
  ]
};
```

```
┌─────────────────────────────────────────────────────────────────┐
│           TRADITIONAL vs INPUT BINDING                           │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│   URL: /users/123/posts/456?sort=date                           │
│   Route: users/:userId/posts/:postId                            │
│   Resolve: { author: authorResolver }                           │
│   Data: { breadcrumb: 'Post' }                                  │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│   TRADITIONAL (ActivatedRoute)                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   @Component(...)                                                │
│   export class PostComponent {                                   │
│     private route = inject(ActivatedRoute);                      │
│                                                                  │
│     userId$ = this.route.paramMap.pipe(                          │
│       map(p => p.get('userId'))                                  │
│     );                                                           │
│     postId$ = this.route.paramMap.pipe(                          │
│       map(p => p.get('postId'))                                  │
│     );                                                           │
│     sort$ = this.route.queryParamMap.pipe(                       │
│       map(p => p.get('sort'))                                    │
│     );                                                           │
│     author$ = this.route.data.pipe(                              │
│       map(d => d['author'])                                      │
│     );                                                           │
│   }                                                              │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│   WITH INPUT BINDING (Cleaner!)                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   @Component(...)                                                │
│   export class PostComponent {                                   │
│     // Path parameters                                           │
│     userId = input<string>();                                    │
│     postId = input<string>();                                    │
│                                                                  │
│     // Query parameters                                          │
│     sort = input<string>();                                      │
│                                                                  │
│     // Resolved data                                             │
│     author = input<User>();                                      │
│                                                                  │
│     // Static route data                                         │
│     breadcrumb = input<string>();                                │
│   }                                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Priority Resolution:**

When multiple sources have the same key name:

```
1. Static route data     (highest priority)
2. Path parameters
3. Resolved data
4. Query parameters
5. Matrix parameters     (lowest priority)
```

**Advanced Example with Transforms:**

```typescript
@Component({
  standalone: true,
  template: `
    <h1>User {{ userId() }}, Post {{ postId() }}</h1>
    <p>Page: {{ page() }}, Featured Only: {{ featuredOnly() }}</p>
    <p>Author: {{ author()?.name }}</p>
  `
})
export class PostComponent {
  // Required path parameter
  userId = input.required<string>();
  postId = input.required<string>();

  // Query parameter with default
  sort = input<string>('date');

  // Query parameter with transform (string to number)
  page = input(1, {
    transform: (value: string | number) =>
      typeof value === 'string' ? parseInt(value, 10) : value
  });

  // Boolean query parameter transform
  featuredOnly = input(false, {
    transform: (value: string | boolean) =>
      typeof value === 'string' ? value === 'true' : value
  });

  // Resolved data
  author = input<User>();

  // Computed values using signals
  fullRoute = computed(() =>
    `/users/${this.userId()}/posts/${this.postId()}`
  );
}
```

**Advantages of Input Binding:**

| Advantage | Description |
|-----------|-------------|
| Less boilerplate | No ActivatedRoute injection, no pipe chains |
| Signals-friendly | Works naturally with input() signals |
| Type-safe | TypeScript knows input types |
| Testable | Easy to provide inputs in tests |
| Reactive | Inputs update when params change |
| Unified API | Same pattern for all param types |

**Interview Tip:** This feature was introduced in Angular 16 and represents the modern way to handle route parameters. It dramatically simplifies components and makes them more testable since you can pass inputs directly in tests without mocking ActivatedRoute.

---

## 10. canMatch vs canActivate

### Q10: What is the difference between canMatch and canActivate guards? When would you use canMatch?

**Answer:**

```
┌─────────────────────────────────────────────────────────────────┐
│              canMatch vs canActivate                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  canMatch                        canActivate                     │
│  ────────                        ────────────                    │
│                                                                  │
│  • Runs BEFORE lazy loading      • Runs AFTER lazy loading      │
│  • Affects route matching        • Only blocks activation       │
│  • false = try next route        • false/UrlTree = redirect     │
│  • No access to route data       • Full route access            │
│  • Best for role-based routing   • Best for auth checks         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Visual Execution Order:**

```
                       Navigation to /admin/dashboard

                                │
                                ▼
           ┌─────────────────────────────────────────┐
           │           Route Matching                 │
           │  /admin → canMatch: [adminGuard]        │
           └──────────────────┬──────────────────────┘
                              │
                 ┌────────────┴────────────┐
                 │ canMatch runs           │
                 │ (BEFORE lazy loading)   │
                 └────────────┬────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
          ✓ true                          ✗ false
              │                               │
              ▼                               ▼
    ┌─────────────────────┐         ┌─────────────────────┐
    │  Lazy load chunk    │         │  Route doesn't match │
    │  loadChildren()     │         │  Try next route      │
    └─────────┬───────────┘         │  definition          │
              │                      └─────────────────────┘
              ▼
    ┌─────────────────────┐
    │  canActivate runs   │
    │  (AFTER loading)    │
    └─────────┬───────────┘
              │
              ▼
        Component rendered
```

**canMatch Guard Implementation:**

```typescript
// guards/admin-match.guard.ts
import { inject } from '@angular/core';
import { CanMatchFn, Route, UrlSegment, Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const adminMatchGuard: CanMatchFn = (
  route: Route,
  segments: UrlSegment[]
) => {
  const authService = inject(AuthService);
  const router = inject(Router);

  if (authService.hasRole('admin')) {
    return true;  // Route matches, proceed
  }

  // Option 1: Route doesn't match, router will try next route
  return false;

  // Option 2: Redirect to another route
  // return router.createUrlTree(['/unauthorized']);
};
```

**Practical Use Case: Feature Flags / A/B Testing**

```typescript
// Feature flag routing
export const routes: Routes = [
  // New dashboard (for users with feature enabled)
  {
    path: 'dashboard',
    canMatch: [featureFlagGuard('new-dashboard')],
    loadComponent: () => import('./dashboard-v2/dashboard.component')
  },
  // Old dashboard (fallback)
  {
    path: 'dashboard',
    loadComponent: () => import('./dashboard/dashboard.component')
  }
];

// Feature flag guard
export const featureFlagGuard = (flag: string): CanMatchFn => {
  return () => {
    const featureService = inject(FeatureService);
    return featureService.isEnabled(flag);
  };
};
```

**Role-Based Routing:**

```typescript
export const routes: Routes = [
  // Admin sees admin dashboard
  {
    path: 'home',
    canMatch: [roleMatchGuard('admin')],
    loadComponent: () => import('./admin-home/admin-home.component')
  },
  // Manager sees manager dashboard
  {
    path: 'home',
    canMatch: [roleMatchGuard('manager')],
    loadComponent: () => import('./manager-home/manager-home.component')
  },
  // Regular users see standard dashboard
  {
    path: 'home',
    loadComponent: () => import('./user-home/user-home.component')
  }
];

export const roleMatchGuard = (role: string): CanMatchFn => {
  return () => {
    const authService = inject(AuthService);
    return authService.hasRole(role);
  };
};
```

**Interview Tip:** `canMatch` is crucial for optimizing bundle sizes - if a user doesn't have access to admin, why download the admin module? Also mention its usefulness for A/B testing and feature flags where different users see different components for the same route.

---

## 11. Router Configuration

### Q11: Explain the router configuration options available with provideRouter().

**Answer:**

```typescript
// app.config.ts - Complete router configuration
import {
  provideRouter,
  withComponentInputBinding,
  withPreloading,
  withDebugTracing,
  withRouterConfig,
  withHashLocation,
  withInMemoryScrolling,
  withNavigationErrorHandler,
  withViewTransitions,
  PreloadAllModules
} from '@angular/router';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,

      // Bind route params to component inputs
      withComponentInputBinding(),

      // Preload lazy-loaded routes
      withPreloading(PreloadAllModules),

      // Console log all router events (development only)
      withDebugTracing(),

      // Router behavior configuration
      withRouterConfig({
        // How child routes inherit params from parents
        paramsInheritanceStrategy: 'always', // 'emptyOnly' | 'always'

        // Behavior when navigating to same URL
        onSameUrlNavigation: 'reload', // 'ignore' | 'reload'

        // When to update browser URL
        urlUpdateStrategy: 'eager', // 'deferred' | 'eager'

        // How cancelled navigation updates URL
        canceledNavigationResolution: 'computed' // 'replace' | 'computed'
      }),

      // Use hash-based URLs (#/path)
      // withHashLocation(),

      // Scroll behavior
      withInMemoryScrolling({
        scrollPositionRestoration: 'enabled', // 'disabled' | 'enabled' | 'top'
        anchorScrolling: 'enabled'            // Enable #fragment scrolling
      }),

      // Global error handler
      withNavigationErrorHandler((error) => {
        console.error('Navigation failed:', error);
        inject(Router).navigate(['/error']);
      }),

      // Enable View Transitions API (Chrome 111+)
      withViewTransitions({
        skipInitialTransition: true,
        onViewTransitionCreated: (info) => {
          console.log('Transition:', info.from, '->', info.to);
        }
      })
    )
  ]
};
```

**Configuration Options Explained:**

```
┌────────────────────────────────────────────────────────────────────────┐
│                 ROUTER CONFIGURATION OPTIONS                            │
├─────────────────────────────┬──────────────────────────────────────────┤
│  paramsInheritanceStrategy  │                                          │
│  ─────────────────────────  │                                          │
│  'emptyOnly' (default)      │  Child inherits params only if it has   │
│                             │  empty path                              │
│  'always'                   │  Child always inherits parent params    │
├─────────────────────────────┼──────────────────────────────────────────┤
│  onSameUrlNavigation        │                                          │
│  ────────────────────       │                                          │
│  'ignore' (default)         │  Don't trigger navigation for same URL  │
│  'reload'                   │  Re-run guards and resolvers            │
├─────────────────────────────┼──────────────────────────────────────────┤
│  urlUpdateStrategy          │                                          │
│  ─────────────────          │                                          │
│  'deferred' (default)       │  Update URL after navigation completes  │
│  'eager'                    │  Update URL immediately                 │
├─────────────────────────────┼──────────────────────────────────────────┤
│  scrollPositionRestoration  │                                          │
│  ────────────────────────   │                                          │
│  'disabled' (default)       │  No scroll management                   │
│  'enabled'                  │  Restore previous position on back      │
│  'top'                      │  Always scroll to top                   │
└─────────────────────────────┴──────────────────────────────────────────┘
```

**View Transitions (Angular 17+):**

```typescript
// Enables smooth page transitions using View Transitions API
withViewTransitions({
  skipInitialTransition: true,  // Don't animate first load
  onViewTransitionCreated: ({ transition, from, to }) => {
    // Customize transition based on routes
    if (to?.url.includes('detail')) {
      // Custom entry animation for detail pages
    }
  }
})
```

**Interview Tip:** Know when to use each option. `paramsInheritanceStrategy: 'always'` is often needed for deeply nested routes. `onSameUrlNavigation: 'reload'` is essential for refresh buttons on the same page.

---

## 12. Navigation & URL Handling

### Q12: What are the different ways to navigate in Angular and when would you use each?

**Answer:**

```
┌─────────────────────────────────────────────────────────────────┐
│                 NAVIGATION METHODS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. RouterLink Directive (Template)                             │
│      - Declarative, accessibility-friendly                       │
│      - Best for static navigation                                │
│                                                                  │
│   2. router.navigate() (Programmatic)                            │
│      - Dynamic navigation with conditions                        │
│      - Array-based path                                          │
│                                                                  │
│   3. router.navigateByUrl() (Programmatic)                       │
│      - Absolute URL string                                       │
│      - Used with URL trees                                       │
│                                                                  │
│   4. router.createUrlTree() (URL Building)                       │
│      - Create URL without navigating                             │
│      - Used in guards for redirects                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**RouterLink Directive:**

```typescript
@Component({
  template: `
    <!-- Basic -->
    <a routerLink="/products">Products</a>

    <!-- With path parameters -->
    <a [routerLink]="['/products', product.id]">{{ product.name }}</a>

    <!-- With query parameters -->
    <a [routerLink]="['/products']"
       [queryParams]="{ category: 'electronics', sort: 'price' }"
       [queryParamsHandling]="'merge'"
       [fragment]="'top'"
       [preserveFragment]="false"
       [skipLocationChange]="false"
       [replaceUrl]="false"
       [state]="{ from: 'catalog' }">
      Electronics
    </a>

    <!-- Active state styling -->
    <a routerLink="/products"
       routerLinkActive="active-link"
       [routerLinkActiveOptions]="{ exact: true }"
       #rla="routerLinkActive">
      Products {{ rla.isActive ? '(current)' : '' }}
    </a>

    <!-- Auxiliary routes -->
    <a [routerLink]="['/products', { outlets: { sidebar: ['filters'] } }]">
      Show Filters
    </a>
  `
})
export class NavigationComponent {}
```

**Programmatic Navigation:**

```typescript
@Component({...})
export class ProductListComponent {
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  // Navigate with path array
  navigateToProduct(id: string) {
    this.router.navigate(['/products', id]);
  }

  // With query parameters
  applyFilters(filters: Record<string, string>) {
    this.router.navigate(['/products'], {
      queryParams: filters,
      queryParamsHandling: 'merge'
    });
  }

  // Relative navigation
  navigateToReviews(productId: string) {
    this.router.navigate(['reviews'], {
      relativeTo: this.route  // Navigate relative to current route
    });
  }

  // With navigation extras
  navigateWithOptions() {
    this.router.navigate(['/checkout'], {
      queryParams: { step: 'payment' },
      queryParamsHandling: 'merge',  // 'preserve' | 'merge' | ''
      fragment: 'summary',
      skipLocationChange: false,     // Don't update URL
      replaceUrl: true,              // Replace history entry
      state: {                       // History state (hidden)
        orderId: '12345',
        returnUrl: '/products'
      }
    });
  }

  // Using navigateByUrl for absolute paths
  navigateAbsolute() {
    this.router.navigateByUrl('/products/123?sort=price#reviews');
  }

  // Creating URL trees (useful in guards)
  createRedirectUrl() {
    const urlTree = this.router.createUrlTree(
      ['/login'],
      { queryParams: { returnUrl: this.router.url } }
    );

    // Can be returned from guards
    return urlTree;
  }
}
```

**Accessing Navigation State:**

```typescript
// Passed state is available in receiving component
@Component({...})
export class CheckoutComponent {
  private router = inject(Router);

  constructor() {
    // Access state from navigation
    const navigation = this.router.getCurrentNavigation();
    const state = navigation?.extras?.state;
    console.log('Order ID:', state?.['orderId']);
  }

  // Or via Location
  private location = inject(Location);

  ngOnInit() {
    const state = this.location.getState() as any;
    console.log('State:', state);
  }
}
```

**queryParamsHandling Options:**

| Option | Behavior |
|--------|----------|
| `''` (default) | Replace all query params |
| `'merge'` | Merge new params with existing |
| `'preserve'` | Keep existing, ignore new |

**Interview Tip:** Mention that `routerLink` is preferred for accessibility (proper href, keyboard navigation) and SEO. Programmatic navigation is for conditional logic after user actions.

---

## 13. Route Animations

### Q13: How do you implement route animations in Angular?

**Answer:**

**Setup:**

```typescript
// app.config.ts
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withViewTransitions()),
    provideAnimationsAsync()  // Enable animations
  ]
};
```

**Animation Definitions:**

```typescript
// animations/route.animations.ts
import {
  trigger, transition, style, animate,
  query, group, animateChild
} from '@angular/animations';

// Fade animation
export const fadeAnimation = trigger('routeAnimations', [
  transition('* <=> *', [
    // Set up positioning
    query(':enter, :leave', [
      style({
        position: 'absolute',
        width: '100%',
        opacity: 0
      })
    ], { optional: true }),

    // Leave animation
    query(':leave', [
      style({ opacity: 1 }),
      animate('200ms ease-out', style({ opacity: 0 }))
    ], { optional: true }),

    // Enter animation
    query(':enter', [
      style({ opacity: 0 }),
      animate('300ms ease-in', style({ opacity: 1 }))
    ], { optional: true })
  ])
]);

// Slide animation based on route data
export const slideAnimation = trigger('routeAnimations', [
  // Slide left when going deeper
  transition('home => products, products => detail', [
    query(':enter, :leave', [
      style({
        position: 'absolute',
        width: '100%'
      })
    ], { optional: true }),

    group([
      query(':leave', [
        animate('300ms ease-out',
          style({ transform: 'translateX(-100%)' }))
      ], { optional: true }),
      query(':enter', [
        style({ transform: 'translateX(100%)' }),
        animate('300ms ease-out',
          style({ transform: 'translateX(0)' }))
      ], { optional: true })
    ])
  ]),

  // Slide right when going back
  transition('detail => products, products => home', [
    query(':enter, :leave', [
      style({
        position: 'absolute',
        width: '100%'
      })
    ], { optional: true }),

    group([
      query(':leave', [
        animate('300ms ease-out',
          style({ transform: 'translateX(100%)' }))
      ], { optional: true }),
      query(':enter', [
        style({ transform: 'translateX(-100%)' }),
        animate('300ms ease-out',
          style({ transform: 'translateX(0)' }))
      ], { optional: true })
    ])
  ])
]);
```

**Route Configuration with Animation Data:**

```typescript
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
  },
  {
    path: 'products/:id',
    loadComponent: () => import('./detail.component'),
    data: { animation: 'detail' }
  }
];
```

**Using Animations:**

```typescript
// app.component.ts
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { slideAnimation } from './animations/route.animations';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  template: `
    <main [@routeAnimations]="getAnimationData()">
      <router-outlet #outlet="outlet"></router-outlet>
    </main>
  `,
  animations: [slideAnimation]
})
export class AppComponent {
  outlet!: RouterOutlet;

  getAnimationData() {
    return this.outlet?.activatedRouteData?.['animation'];
  }
}
```

**View Transitions API (Modern Alternative):**

```typescript
// Angular 17+ - CSS-based transitions
// app.config.ts
provideRouter(
  routes,
  withViewTransitions({
    skipInitialTransition: true
  })
)

// In CSS
::view-transition-old(root) {
  animation: fade-out 0.25s ease-in-out;
}

::view-transition-new(root) {
  animation: fade-in 0.25s ease-in-out;
}

@keyframes fade-out {
  from { opacity: 1; }
  to { opacity: 0; }
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

**Interview Tip:** Mention that View Transitions API is the modern approach (Angular 17+) as it's more performant and uses CSS animations. Traditional Angular animations offer more control but have performance overhead.

---

## 14. Performance & Best Practices

### Q14: What are best practices for optimizing Angular Router performance?

**Answer:**

```
┌─────────────────────────────────────────────────────────────────┐
│              ROUTER PERFORMANCE BEST PRACTICES                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. LAZY LOADING                                                 │
│     • Load feature areas on demand                               │
│     • Reduces initial bundle size                                │
│     • Use loadComponent for standalone components                │
│                                                                  │
│  2. PRELOADING STRATEGY                                          │
│     • PreloadAllModules for fast apps                           │
│     • Custom strategy for large apps                            │
│     • Consider network conditions                                │
│                                                                  │
│  3. GUARD OPTIMIZATION                                           │
│     • Use canMatch before lazy loading                          │
│     • Cache permission checks                                    │
│     • Avoid heavy computations in guards                        │
│                                                                  │
│  4. RESOLVER CONSIDERATIONS                                      │
│     • Keep resolvers lightweight                                 │
│     • Consider loading data in component instead                │
│     • Use EMPTY to cancel navigation on errors                  │
│                                                                  │
│  5. ROUTE STRUCTURE                                              │
│     • Avoid deep nesting (>3 levels)                            │
│     • Use shared modules strategically                          │
│     • Keep route configuration flat when possible               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Lazy Loading Structure:**

```typescript
// Optimal lazy loading setup
export const routes: Routes = [
  // Eagerly load critical routes
  {
    path: '',
    loadComponent: () => import('./home/home.component')
      .then(m => m.HomeComponent),
    data: { preload: true }
  },

  // Lazy load features
  {
    path: 'admin',
    canMatch: [adminGuard],  // Don't load if not admin
    loadChildren: () => import('./admin/admin.routes')
      .then(m => m.ADMIN_ROUTES)
  },

  // Wildcard should be last
  {
    path: '**',
    loadComponent: () => import('./not-found/not-found.component')
  }
];
```

**Efficient Guard Pattern:**

```typescript
// Cache expensive checks
@Injectable({ providedIn: 'root' })
export class PermissionCache {
  private cache = new Map<string, boolean>();

  check(permission: string): Observable<boolean> {
    if (this.cache.has(permission)) {
      return of(this.cache.get(permission)!);
    }

    return this.api.checkPermission(permission).pipe(
      tap(result => this.cache.set(permission, result))
    );
  }
}

export const permissionGuard: CanActivateFn = (route) => {
  const cache = inject(PermissionCache);
  const permission = route.data['permission'];
  return cache.check(permission);
};
```

**Route Tracking for Analytics:**

```typescript
// Efficient, non-blocking tracking
@Injectable({ providedIn: 'root' })
export class AnalyticsService {
  private router = inject(Router);

  init() {
    this.router.events.pipe(
      filter((e): e is NavigationEnd => e instanceof NavigationEnd),
      // Debounce rapid navigation
      debounceTime(100)
    ).subscribe(event => {
      // Fire and forget - don't block
      queueMicrotask(() => {
        this.trackPageView(event.urlAfterRedirects);
      });
    });
  }

  private trackPageView(url: string) {
    // Analytics implementation
  }
}
```

**Bundle Analysis:**

```bash
# Analyze bundle sizes
ng build --stats-json
npx webpack-bundle-analyzer dist/*/stats.json

# Lazy chunks should be reasonably sized
# Aim for < 100KB per lazy chunk
```

**Interview Tip:** Performance optimization is about trade-offs. Lazy loading reduces initial load but adds network requests later. Preloading improves navigation but uses bandwidth. The best strategy depends on the app's usage patterns and target audience.

---

## Summary Table

| Topic | Key Points |
|-------|------------|
| **Router Architecture** | Parse → Match → Guards → Resolve → Activate |
| **loadComponent vs loadChildren** | Single component vs route set |
| **Guards Order** | canMatch → canActivateChild → canActivate → resolve → canDeactivate |
| **Parameter Types** | Path (:id), Query (?), Matrix (;), Fragment (#) |
| **canMatch** | Runs before lazy loading, affects route matching |
| **withComponentInputBinding** | Binds params to component inputs automatically |
| **Preloading** | NoPreloading, PreloadAllModules, Custom |
| **Router Events** | NavigationStart → ... → NavigationEnd |
| **Resolvers** | Pre-fetch data, blocks navigation |
| **Auxiliary Routes** | Named outlets for parallel content |

---

## Interview Tips

1. **Know the guard execution order** - This is commonly asked and trips up many candidates

2. **Understand canMatch vs canActivate** - canMatch running before lazy loading is a key optimization

3. **Explain trade-offs** - Resolvers vs ngOnInit, preloading strategies, lazy loading

4. **Modern patterns** - Use functional guards, withComponentInputBinding, standalone components

5. **Real-world scenarios** - Be ready to discuss auth flows, role-based routing, protected routes

6. **Performance awareness** - Bundle splitting, preloading strategies, guard optimization

7. **Debug skills** - Know how to use withDebugTracing() and router events for troubleshooting
