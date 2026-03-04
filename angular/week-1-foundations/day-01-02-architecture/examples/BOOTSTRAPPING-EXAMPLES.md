# Angular 22 Bootstrapping Examples

This document contains comprehensive examples of Angular bootstrapping, configuration, and core patterns.

---

## 1. main.ts - Application Entry Point

```typescript
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';

// Modern standalone bootstrapping
bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
```

---

## 2. app.config.ts - Application Configuration

```typescript
import { 
  ApplicationConfig, 
  provideZoneChangeDetection,
  provideExperimentalZonelessChangeDetection,
  isDevMode
} from '@angular/core';
import { 
  provideRouter, 
  withComponentInputBinding,
  withPreloading,
  PreloadAllModules,
  withHashLocation,
  withInMemoryScrolling
} from '@angular/router';
import { 
  provideHttpClient, 
  withInterceptors,
  withFetch
} from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { provideServiceWorker } from '@angular/service-worker';

import { routes } from './app.routes';
import { authInterceptor } from './interceptors/auth.interceptor';
import { errorInterceptor } from './interceptors/error.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    // Option 1: Zone.js change detection (default)
    provideZoneChangeDetection({ eventCoalescing: true }),
    
    // Option 2: Zoneless (experimental) - uncomment to use
    // provideExperimentalZonelessChangeDetection(),
    
    // Router configuration
    provideRouter(
      routes,
      withComponentInputBinding(),           // Bind route params to @Input
      withPreloading(PreloadAllModules),     // Preload lazy modules
      withInMemoryScrolling({
        scrollPositionRestoration: 'enabled',
        anchorScrolling: 'enabled'
      })
    ),
    
    // HTTP client with interceptors
    provideHttpClient(
      withFetch(),                           // Use native fetch API
      withInterceptors([
        authInterceptor,
        errorInterceptor
      ])
    ),
    
    // Animations
    provideAnimationsAsync(),
    
    // Service Worker for PWA (production only)
    provideServiceWorker('ngsw-worker.js', {
      enabled: !isDevMode(),
      registrationStrategy: 'registerWhenStable:30000'
    })
  ]
};
```

---

## 3. app.routes.ts - Route Configuration

```typescript
import { Routes } from '@angular/router';
import { authGuard } from './guards/auth.guard';
import { userResolver } from './resolvers/user.resolver';

export const routes: Routes = [
  // Redirect root to home
  {
    path: '',
    redirectTo: 'home',
    pathMatch: 'full'
  },
  
  // Eagerly loaded component
  {
    path: 'home',
    loadComponent: () => import('./pages/home/home.component')
      .then(m => m.HomeComponent),
    title: 'Home'
  },
  
  // Protected route with guard
  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard/dashboard.component')
      .then(m => m.DashboardComponent),
    canActivate: [authGuard],
    title: 'Dashboard'
  },
  
  // Route with resolver
  {
    path: 'user/:id',
    loadComponent: () => import('./pages/user/user.component')
      .then(m => m.UserComponent),
    resolve: { user: userResolver },
    title: 'User Profile'
  },
  
  // Lazy loaded feature routes
  {
    path: 'products',
    loadChildren: () => import('./features/products/products.routes')
      .then(m => m.PRODUCTS_ROUTES),
    canMatch: [authGuard]
  },
  
  // Wildcard - 404
  {
    path: '**',
    loadComponent: () => import('./pages/not-found/not-found.component')
      .then(m => m.NotFoundComponent),
    title: 'Page Not Found'
  }
];
```

---

## 4. app.component.ts - Root Component

```typescript
import { Component, inject } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { AsyncPipe } from '@angular/common';
import { HeaderComponent } from './components/header/header.component';
import { FooterComponent } from './components/footer/footer.component';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    AsyncPipe,
    HeaderComponent,
    FooterComponent
  ],
  template: `
    <div class="app-container">
      <app-header />
      
      <main class="main-content">
        <router-outlet />
      </main>
      
      <app-footer />
    </div>
  `,
  styles: [`
    .app-container {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    
    .main-content {
      flex: 1;
      padding: 1rem;
    }
  `]
})
export class AppComponent {
  private authService = inject(AuthService);
  
  title = 'My Angular App';
}
```

---

## 5. Standalone Component Examples

### header.component.ts

```typescript
import { Component, signal, computed, inject } from '@angular/core';
import { RouterLink, RouterLinkActive, Router } from '@angular/router';
import { NgIf, AsyncPipe } from '@angular/common';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, NgIf, AsyncPipe],
  template: `
    <header class="header">
      <div class="logo">
        <a routerLink="/">MyApp</a>
      </div>
      
      <nav class="nav">
        <a routerLink="/home" routerLinkActive="active">Home</a>
        <a routerLink="/products" routerLinkActive="active">Products</a>
        
        @if (isLoggedIn()) {
          <a routerLink="/dashboard" routerLinkActive="active">Dashboard</a>
          <button (click)="logout()">Logout ({{ username() }})</button>
        } @else {
          <a routerLink="/login" routerLinkActive="active">Login</a>
        }
      </nav>
    </header>
  `,
  styles: [`
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1rem;
      background: #333;
      color: white;
    }
    
    .nav a {
      color: white;
      margin: 0 1rem;
      text-decoration: none;
    }
    
    .nav a.active {
      font-weight: bold;
      border-bottom: 2px solid #fff;
    }
    
    button {
      background: #ff4444;
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      cursor: pointer;
    }
  `]
})
export class HeaderComponent {
  private authService = inject(AuthService);
  private router = inject(Router);
  
  // Using Signals
  isLoggedIn = this.authService.isLoggedIn;
  username = this.authService.username;
  
  logout(): void {
    this.authService.logout();
    this.router.navigate(['/home']);
  }
}
```

---

## 6. Service with Signals Example

### auth.service.ts

```typescript
import { Injectable, signal, computed } from '@angular/core';

interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'user';
}

@Injectable({
  providedIn: 'root'  // Singleton, tree-shakable
})
export class AuthService {
  // Private signal for user state
  private userSignal = signal<User | null>(null);
  
  // Public computed signals (read-only)
  readonly user = this.userSignal.asReadonly();
  readonly isLoggedIn = computed(() => this.userSignal() !== null);
  readonly username = computed(() => this.userSignal()?.username ?? 'Guest');
  readonly isAdmin = computed(() => this.userSignal()?.role === 'admin');
  
  // Methods to update state
  login(user: User): void {
    this.userSignal.set(user);
    localStorage.setItem('user', JSON.stringify(user));
  }
  
  logout(): void {
    this.userSignal.set(null);
    localStorage.removeItem('user');
  }
  
  // Initialize from storage
  initFromStorage(): void {
    const stored = localStorage.getItem('user');
    if (stored) {
      this.userSignal.set(JSON.parse(stored));
    }
  }
}
```

---

## 7. HTTP Interceptor Example

### auth.interceptor.ts

```typescript
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const user = authService.user();
  
  // Skip auth header for public endpoints
  const publicUrls = ['/api/auth/login', '/api/auth/register'];
  if (publicUrls.some(url => req.url.includes(url))) {
    return next(req);
  }
  
  // Add auth token if user is logged in
  if (user) {
    const token = localStorage.getItem('token');
    if (token) {
      const authReq = req.clone({
        headers: req.headers.set('Authorization', `Bearer ${token}`)
      });
      return next(authReq);
    }
  }
  
  return next(req);
};
```

---

## 8. Route Guard Example

### auth.guard.ts

```typescript
import { inject } from '@angular/core';
import { Router, CanActivateFn, CanMatchFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (authService.isLoggedIn()) {
    return true;
  }
  
  // Redirect to login with return URL
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url }
  });
};

export const adminGuard: CanMatchFn = (route, segments) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  if (authService.isAdmin()) {
    return true;
  }
  
  return router.createUrlTree(['/unauthorized']);
};
```

---

## 9. Route Resolver Example

### user.resolver.ts

```typescript
import { inject } from '@angular/core';
import { ResolveFn } from '@angular/router';
import { UserService } from '../services/user.service';
import { User } from '../models/user.model';

export const userResolver: ResolveFn<User> = (route, state) => {
  const userService = inject(UserService);
  const userId = route.paramMap.get('id')!;
  
  return userService.getUserById(userId);
};
```

---

## 10. Feature Routes Example

### features/products/products.routes.ts

```typescript
import { Routes } from '@angular/router';

export const PRODUCTS_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () => import('./product-list/product-list.component')
      .then(m => m.ProductListComponent),
    title: 'Products'
  },
  {
    path: ':id',
    loadComponent: () => import('./product-detail/product-detail.component')
      .then(m => m.ProductDetailComponent),
    title: 'Product Details'
  },
  {
    path: 'create',
    loadComponent: () => import('./product-form/product-form.component')
      .then(m => m.ProductFormComponent),
    title: 'Create Product'
  }
];
```

---

## Key Concepts Summary

### Bootstrapping
- Modern Angular uses `bootstrapApplication()` for standalone components
- Configuration is centralized in `ApplicationConfig`
- No need for `NgModule` with standalone approach

### Providers
- **provideZoneChangeDetection**: Traditional change detection with Zone.js
- **provideExperimentalZonelessChangeDetection**: New zoneless approach (experimental)
- **provideRouter**: Router configuration with feature flags
- **provideHttpClient**: HTTP client with fetch API and interceptors
- **provideAnimationsAsync**: Lazy-loaded animations
- **provideServiceWorker**: PWA support

### Router Features
- **withComponentInputBinding()**: Bind route params directly to component @Input
- **withPreloading()**: Preload lazy-loaded modules
- **withInMemoryScrolling()**: Handle scroll position restoration
- **loadComponent()**: Lazy load standalone components
- **loadChildren()**: Lazy load feature routes

### Dependency Injection
- Use `inject()` function in component/service initialization
- `providedIn: 'root'` makes services singleton and tree-shakable

### Guards & Resolvers
- **CanActivateFn**: Functional guard for route activation
- **CanMatchFn**: Functional guard for route matching
- **ResolveFn**: Functional resolver for pre-fetching data

### Signals
- **signal()**: Create mutable signal
- **computed()**: Derive values from signals
- **asReadonly()**: Expose signal as read-only
- Automatic dependency tracking and updates
