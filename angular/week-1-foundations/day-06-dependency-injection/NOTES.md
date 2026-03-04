# Day 6: Dependency Injection (DI) in Angular

## Table of Contents
1. [What is Dependency Injection?](#what-is-dependency-injection)
2. [Hierarchical Injectors](#hierarchical-injectors)
3. [providedIn Options](#providedin-options)
4. [Singleton vs Scoped Services](#singleton-vs-scoped-services)
5. [Provider Types](#provider-types)
6. [InjectionToken](#injectiontoken)
7. [Multi Providers](#multi-providers)
8. [inject() vs Constructor Injection](#inject-vs-constructor-injection)
9. [forwardRef](#forwardref)
10. [Quick Reference Card](#quick-reference-card)

---

## What is Dependency Injection?

Dependency Injection (DI) is a design pattern where a class receives its dependencies from external sources rather than creating them itself. Angular has its own DI framework that's a core part of the framework.

### Benefits of DI
- **Loose coupling**: Classes don't need to know how to create their dependencies
- **Testability**: Easy to mock dependencies in unit tests
- **Maintainability**: Changes to dependencies don't affect consumers
- **Reusability**: Services can be shared across components

### Basic Example (Angular 22+)

```typescript
// user.service.ts
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private users = signal<User[]>([]);

  getUsers() {
    return this.users.asReadonly();
  }

  addUser(user: User) {
    this.users.update(users => [...users, user]);
  }
}

// user-list.component.ts
import { Component, inject } from '@angular/core';
import { UserService } from './user.service';

@Component({
  selector: 'app-user-list',
  standalone: true,
  template: `
    @for (user of userService.getUsers()(); track user.id) {
      <div>{{ user.name }}</div>
    }
  `
})
export class UserListComponent {
  // Modern inject() function - preferred in Angular 22+
  protected userService = inject(UserService);
}
```

---

## Hierarchical Injectors

Angular's DI system is hierarchical, meaning there are multiple injector levels that form a tree structure.

### Injector Hierarchy Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     NULL INJECTOR                                    │
│                (throws error if not found)                          │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PLATFORM INJECTOR                                 │
│         (providedIn: 'platform' services live here)                 │
│              Shared across multiple apps                            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      ROOT INJECTOR                                   │
│          (providedIn: 'root' services - singletons)                 │
│                    bootstrapApplication()                            │
└─────────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│   ROUTE INJECTOR          │   │   ROUTE INJECTOR          │
│   (lazy loaded routes)    │   │   (lazy loaded routes)    │
│   loadComponent/Children  │   │   loadComponent/Children  │
└───────────────────────────┘   └───────────────────────────┘
                │
        ┌───────┴───────┐
        ▼               ▼
┌─────────────┐   ┌─────────────┐
│  ELEMENT    │   │  ELEMENT    │
│  INJECTOR   │   │  INJECTOR   │
│ (component) │   │ (component) │
│  providers  │   │  providers  │
└─────────────┘   └─────────────┘
        │
        ▼
┌─────────────┐
│   CHILD     │
│  ELEMENT    │
│  INJECTOR   │
└─────────────┘
```

### Resolution Process

```
┌────────────────────────────────────────────────────────────┐
│                    RESOLUTION FLOW                          │
├────────────────────────────────────────────────────────────┤
│                                                             │
│   Component requests dependency                             │
│              │                                              │
│              ▼                                              │
│   ┌─────────────────────┐                                  │
│   │ Check Element       │──Found──▶ Return instance        │
│   │ Injector (self)     │                                  │
│   └─────────────────────┘                                  │
│              │ Not Found                                    │
│              ▼                                              │
│   ┌─────────────────────┐                                  │
│   │ Check Parent        │──Found──▶ Return instance        │
│   │ Element Injector    │                                  │
│   └─────────────────────┘                                  │
│              │ Not Found                                    │
│              ▼                                              │
│   ┌─────────────────────┐                                  │
│   │ Check Route         │──Found──▶ Return instance        │
│   │ Injector            │                                  │
│   └─────────────────────┘                                  │
│              │ Not Found                                    │
│              ▼                                              │
│   ┌─────────────────────┐                                  │
│   │ Check Root          │──Found──▶ Return instance        │
│   │ Injector            │                                  │
│   └─────────────────────┘                                  │
│              │ Not Found                                    │
│              ▼                                              │
│   ┌─────────────────────┐                                  │
│   │ Check Platform      │──Found──▶ Return instance        │
│   │ Injector            │                                  │
│   └─────────────────────┘                                  │
│              │ Not Found                                    │
│              ▼                                              │
│   ┌─────────────────────┐                                  │
│   │ NULL Injector       │──────────▶ Throw Error           │
│   │                     │          NullInjectorError       │
│   └─────────────────────┘                                  │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Two Injector Hierarchies

Angular actually has TWO parallel injector trees:

```
┌──────────────────────────────────────────────────────────────────┐
│                    ENVIRONMENT INJECTORS                          │
│         (Module/Route level - services & global state)           │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│   Platform Injector                                               │
│         │                                                         │
│         ▼                                                         │
│   Root Injector ◄─── providedIn: 'root'                          │
│         │                                                         │
│         ├──▶ Lazy Route Injector A                               │
│         │                                                         │
│         └──▶ Lazy Route Injector B                               │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                     ELEMENT INJECTORS                             │
│         (Component level - component-specific services)          │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│   AppComponent (Element Injector)                                │
│         │                                                         │
│         ├──▶ HeaderComponent                                     │
│         │         │                                               │
│         │         └──▶ NavComponent                              │
│         │                                                         │
│         └──▶ MainComponent                                       │
│                   │                                               │
│                   ├──▶ SidebarComponent                          │
│                   │                                               │
│                   └──▶ ContentComponent                          │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## providedIn Options

### Comparison Table

| Option | Scope | Tree-Shakable | Use Case |
|--------|-------|---------------|----------|
| `'root'` | Application-wide singleton | ✅ Yes | Most services, global state |
| `'platform'` | Shared across Angular apps | ✅ Yes | Micro-frontends, multiple apps |
| `'any'` | Per-module instance | ✅ Yes | Module-scoped state (legacy) |
| Component class | Component tree | ✅ Yes | Component-scoped services |

### Examples

#### providedIn: 'root' (Most Common)

```typescript
@Injectable({
  providedIn: 'root'  // Singleton across entire application
})
export class AuthService {
  private isAuthenticated = signal(false);
  private currentUser = signal<User | null>(null);

  login(credentials: Credentials) {
    // Single instance handles all auth
  }
}
```

#### providedIn: 'platform'

```typescript
// Useful for micro-frontends sharing state
@Injectable({
  providedIn: 'platform'  // Shared across multiple Angular apps
})
export class SharedAnalyticsService {
  trackEvent(event: AnalyticsEvent) {
    // Shared analytics across all Angular micro-apps
  }
}
```

#### providedIn: 'any' (Deprecated Pattern)

```typescript
// ⚠️ Legacy - creates instance per lazy-loaded module
// Not recommended in modern Angular
@Injectable({
  providedIn: 'any'
})
export class LegacyModuleScopedService {
  // Each lazy module gets its own instance
}
```

#### providedIn: Component (Modern Scoped Pattern)

```typescript
// Modern approach for component-scoped services
@Injectable()
export class FormStateService {
  private formData = signal<FormData>({});

  updateField(key: string, value: unknown) {
    this.formData.update(data => ({ ...data, [key]: value }));
  }
}

@Component({
  selector: 'app-user-form',
  standalone: true,
  providers: [FormStateService],  // New instance per component
  template: `...`
})
export class UserFormComponent {
  private formState = inject(FormStateService);
}
```

---

## Singleton vs Scoped Services

### Singleton Services (providedIn: 'root')

```typescript
@Injectable({ providedIn: 'root' })
export class CartService {
  private items = signal<CartItem[]>([]);
  
  readonly total = computed(() => 
    this.items().reduce((sum, item) => sum + item.price * item.quantity, 0)
  );

  addItem(item: CartItem) {
    this.items.update(items => [...items, item]);
  }
}

// Same instance everywhere
@Component({ ... })
export class HeaderComponent {
  cartService = inject(CartService);  // Instance A
}

@Component({ ... })
export class CartPageComponent {
  cartService = inject(CartService);  // Same Instance A
}
```

### Scoped Services (Component Providers)

```typescript
@Injectable()
export class FormValidationService {
  private errors = signal<Record<string, string>>({});

  setError(field: string, message: string) {
    this.errors.update(e => ({ ...e, [field]: message }));
  }

  clearErrors() {
    this.errors.set({});
  }
}

// Each form gets its own validation service
@Component({
  selector: 'app-registration-form',
  standalone: true,
  providers: [FormValidationService],  // New instance
  template: `
    <app-email-field />
    <app-password-field />
  `
})
export class RegistrationFormComponent {}

// Child components share parent's instance
@Component({
  selector: 'app-email-field',
  standalone: true,
  template: `...`
})
export class EmailFieldComponent {
  // Gets the SAME instance from parent
  validation = inject(FormValidationService);
}
```

### Visual: Singleton vs Scoped

```
SINGLETON (providedIn: 'root')
┌─────────────────────────────────────────────┐
│                 Root Injector               │
│         ┌──────────────────────┐            │
│         │   CartService        │            │
│         │   (Single Instance)  │            │
│         └──────────────────────┘            │
│                    │                        │
│     ┌──────────────┼──────────────┐        │
│     ▼              ▼              ▼        │
│  Header        ProductList      Cart       │
│  (same)         (same)         (same)      │
└─────────────────────────────────────────────┘

SCOPED (Component providers)
┌─────────────────────────────────────────────┐
│                                              │
│  ┌─────────────────────┐  ┌─────────────────┐
│  │ FormComponent A     │  │ FormComponent B │
│  │ ┌─────────────────┐ │  │ ┌─────────────┐ │
│  │ │FormValidation A │ │  │ │FormValid B  │ │
│  │ └─────────────────┘ │  │ └─────────────┘ │
│  │         │           │  │       │         │
│  │    ┌────┴────┐      │  │    ┌──┴──┐      │
│  │    ▼         ▼      │  │    ▼     ▼      │
│  │ EmailField NameField│  │  Field  Field   │
│  │  (same A)  (same A) │  │ (same B)(same B)│
│  └─────────────────────┘  └─────────────────┘
│                                              │
└─────────────────────────────────────────────┘
```

---

## Provider Types

Angular supports several ways to configure providers:

### Comparison Table

| Provider Type | Syntax | Use Case |
|--------------|--------|----------|
| `useClass` | `{ provide: AbstractService, useClass: ConcreteService }` | Implementation swapping, mocking |
| `useValue` | `{ provide: CONFIG, useValue: configObject }` | Static configuration values |
| `useFactory` | `{ provide: Service, useFactory: factoryFn, deps: [...] }` | Dynamic instantiation |
| `useExisting` | `{ provide: Alias, useExisting: RealService }` | Aliasing services |

### useClass - Implementation Swapping

```typescript
// Abstract base
abstract class DataService {
  abstract fetchData(): Observable<Data[]>;
}

// Production implementation
@Injectable()
class ApiDataService extends DataService {
  private http = inject(HttpClient);

  fetchData(): Observable<Data[]> {
    return this.http.get<Data[]>('/api/data');
  }
}

// Mock implementation for testing/development
@Injectable()
class MockDataService extends DataService {
  fetchData(): Observable<Data[]> {
    return of([
      { id: 1, name: 'Mock Item 1' },
      { id: 2, name: 'Mock Item 2' }
    ]);
  }
}

// Application config
export const appConfig: ApplicationConfig = {
  providers: [
    {
      provide: DataService,
      useClass: environment.production ? ApiDataService : MockDataService
    }
  ]
};
```

### useValue - Static Configuration

```typescript
// Define configuration interface
interface AppConfig {
  apiUrl: string;
  maxRetries: number;
  featureFlags: {
    darkMode: boolean;
    newDashboard: boolean;
  };
}

// Create injection token
const APP_CONFIG = new InjectionToken<AppConfig>('app.config');

// Production config
const productionConfig: AppConfig = {
  apiUrl: 'https://api.production.com',
  maxRetries: 3,
  featureFlags: {
    darkMode: true,
    newDashboard: false
  }
};

// Provide the value
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: APP_CONFIG, useValue: productionConfig }
  ]
};

// Consume it
@Component({ ... })
export class ApiClientComponent {
  private config = inject(APP_CONFIG);

  callApi() {
    console.log(`Calling ${this.config.apiUrl}`);
  }
}
```

### useFactory - Dynamic Instantiation

```typescript
// Factory function with dependencies
function loggerFactory(
  http: HttpClient,
  config: AppConfig
): LoggerService {
  if (config.featureFlags.remoteLogging) {
    return new RemoteLoggerService(http, config.apiUrl);
  }
  return new ConsoleLoggerService();
}

// Provide with factory
export const appConfig: ApplicationConfig = {
  providers: [
    {
      provide: LoggerService,
      useFactory: loggerFactory,
      deps: [HttpClient, APP_CONFIG]  // Factory dependencies
    }
  ]
};

// Modern approach with inject() in factory
function createLoggerService(): LoggerService {
  const http = inject(HttpClient);
  const config = inject(APP_CONFIG);
  
  return config.featureFlags.remoteLogging
    ? new RemoteLoggerService(http, config.apiUrl)
    : new ConsoleLoggerService();
}

export const appConfig: ApplicationConfig = {
  providers: [
    { provide: LoggerService, useFactory: createLoggerService }
  ]
};
```

### useExisting - Service Aliasing

```typescript
// Original service
@Injectable({ providedIn: 'root' })
class ModernLoggerService {
  log(message: string) {
    console.log(`[Modern] ${message}`);
  }
}

// Legacy interface that old code expects
abstract class LegacyLogger {
  abstract log(message: string): void;
}

// Alias LegacyLogger to use ModernLoggerService
export const appConfig: ApplicationConfig = {
  providers: [
    {
      provide: LegacyLogger,
      useExisting: ModernLoggerService  // Points to same instance
    }
  ]
};

// Both inject the SAME instance
@Component({ ... })
export class OldComponent {
  logger = inject(LegacyLogger);  // Gets ModernLoggerService
}

@Component({ ... })
export class NewComponent {
  logger = inject(ModernLoggerService);  // Same instance
}
```

---

## InjectionToken

`InjectionToken` is used to create tokens for non-class dependencies (primitives, interfaces, functions).

### Basic InjectionToken

```typescript
import { InjectionToken, inject } from '@angular/core';

// Simple token for a primitive
export const API_URL = new InjectionToken<string>('api.url');

// Token for an interface (can't use interface as token)
export interface FeatureFlags {
  darkMode: boolean;
  betaFeatures: boolean;
  analytics: boolean;
}

export const FEATURE_FLAGS = new InjectionToken<FeatureFlags>('feature.flags');

// Providing tokens
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: API_URL, useValue: 'https://api.example.com' },
    { 
      provide: FEATURE_FLAGS, 
      useValue: {
        darkMode: true,
        betaFeatures: false,
        analytics: true
      }
    }
  ]
};

// Using tokens
@Component({
  selector: 'app-feature',
  standalone: true,
  template: `
    @if (features.darkMode) {
      <app-dark-theme />
    }
  `
})
export class FeatureComponent {
  features = inject(FEATURE_FLAGS);
  apiUrl = inject(API_URL);
}
```

### InjectionToken with Factory

```typescript
// Token with built-in factory (self-providing)
export const WINDOW = new InjectionToken<Window>(
  'Window object',
  {
    providedIn: 'root',
    factory: () => {
      if (typeof window !== 'undefined') {
        return window;
      }
      throw new Error('Window is not available');
    }
  }
);

export const LOCAL_STORAGE = new InjectionToken<Storage>(
  'LocalStorage',
  {
    providedIn: 'root',
    factory: () => {
      const win = inject(WINDOW);
      return win.localStorage;
    }
  }
);

// Usage
@Injectable({ providedIn: 'root' })
export class StorageService {
  private storage = inject(LOCAL_STORAGE);

  getItem(key: string): string | null {
    return this.storage.getItem(key);
  }

  setItem(key: string, value: string): void {
    this.storage.setItem(key, value);
  }
}
```

### InjectionToken for Functions

```typescript
// Token for a validator function
type ValidatorFn = (value: string) => boolean;

export const EMAIL_VALIDATOR = new InjectionToken<ValidatorFn>(
  'email.validator',
  {
    providedIn: 'root',
    factory: () => (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
  }
);

export const PHONE_VALIDATOR = new InjectionToken<ValidatorFn>(
  'phone.validator',
  {
    providedIn: 'root',
    factory: () => (value: string) => /^\+?[\d\s-]{10,}$/.test(value)
  }
);

// Using function tokens
@Component({ ... })
export class ValidationComponent {
  emailValidator = inject(EMAIL_VALIDATOR);
  phoneValidator = inject(PHONE_VALIDATOR);

  validateEmail(email: string) {
    return this.emailValidator(email);
  }
}
```

---

## Multi Providers

Multi providers allow multiple values to be registered under the same token.

### Basic Multi Provider

```typescript
// Token for multiple validators
export const FORM_VALIDATORS = new InjectionToken<ValidatorFn[]>('form.validators');

// Individual validators
const requiredValidator: ValidatorFn = ctrl => 
  ctrl.value ? null : { required: true };

const minLengthValidator: ValidatorFn = ctrl => 
  ctrl.value?.length >= 3 ? null : { minLength: true };

const noSpacesValidator: ValidatorFn = ctrl => 
  !/\s/.test(ctrl.value || '') ? null : { noSpaces: true };

// Provide multiple validators
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: FORM_VALIDATORS, useValue: requiredValidator, multi: true },
    { provide: FORM_VALIDATORS, useValue: minLengthValidator, multi: true },
    { provide: FORM_VALIDATORS, useValue: noSpacesValidator, multi: true }
  ]
};

// Inject returns array
@Component({ ... })
export class FormComponent {
  // Returns [requiredValidator, minLengthValidator, noSpacesValidator]
  validators = inject(FORM_VALIDATORS);

  validate(control: AbstractControl) {
    return this.validators.map(v => v(control)).filter(Boolean);
  }
}
```

### Built-in Multi Token Example: HTTP_INTERCEPTORS (Legacy)

```typescript
// Legacy approach (Angular 14 and earlier)
// For reference - modern Angular uses functional interceptors

import { HTTP_INTERCEPTORS } from '@angular/common/http';

@Injectable()
class AuthInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<unknown>, next: HttpHandler) {
    const token = inject(AuthService).getToken();
    const authReq = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
    return next.handle(authReq);
  }
}

// Legacy multi provider registration
providers: [
  { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
  { provide: HTTP_INTERCEPTORS, useClass: LoggingInterceptor, multi: true }
]
```

### Modern Functional Interceptors (Angular 22+)

```typescript
import { HttpInterceptorFn, provideHttpClient, withInterceptors } from '@angular/common/http';

// Functional interceptor
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.getToken();
  
  if (token) {
    req = req.clone({
      headers: req.headers.set('Authorization', `Bearer ${token}`)
    });
  }
  
  return next(req);
};

export const loggingInterceptor: HttpInterceptorFn = (req, next) => {
  console.log(`[HTTP] ${req.method} ${req.url}`);
  return next(req).pipe(
    tap({
      next: (event) => console.log('[HTTP] Response:', event),
      error: (error) => console.error('[HTTP] Error:', error)
    })
  );
};

// Modern registration
export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([authInterceptor, loggingInterceptor])
    )
  ]
};
```

### Custom Plugin System with Multi Providers

```typescript
// Plugin interface
interface Plugin {
  name: string;
  initialize(): void;
  destroy(): void;
}

export const APP_PLUGINS = new InjectionToken<Plugin[]>('app.plugins');

// Analytics plugin
const analyticsPlugin: Plugin = {
  name: 'Analytics',
  initialize: () => console.log('Analytics initialized'),
  destroy: () => console.log('Analytics destroyed')
};

// Performance plugin
const performancePlugin: Plugin = {
  name: 'Performance',
  initialize: () => console.log('Performance monitoring started'),
  destroy: () => console.log('Performance monitoring stopped')
};

// Register plugins
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: APP_PLUGINS, useValue: analyticsPlugin, multi: true },
    { provide: APP_PLUGINS, useValue: performancePlugin, multi: true }
  ]
};

// Plugin manager
@Injectable({ providedIn: 'root' })
export class PluginManager {
  private plugins = inject(APP_PLUGINS);

  initializeAll() {
    this.plugins.forEach(plugin => {
      console.log(`Initializing ${plugin.name}...`);
      plugin.initialize();
    });
  }

  destroyAll() {
    this.plugins.forEach(plugin => plugin.destroy());
  }
}
```

---

## inject() vs Constructor Injection

### Comparison Table

| Feature | `inject()` Function | Constructor Injection |
|---------|--------------------|-----------------------|
| Syntax | `service = inject(Service)` | `constructor(private service: Service)` |
| Location | Field initializer, constructor, factory | Constructor only |
| Inheritance | Easier (no super() issues) | Requires calling super() |
| Tree-shaking | Slightly better | Standard |
| TypeScript | Works with strict mode | Works with strict mode |
| Testing | Both mockable | Both mockable |
| Angular Version | 14+ (stable in 15+) | All versions |

### inject() Function (Modern - Recommended)

```typescript
import { Component, inject, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-modern',
  standalone: true,
  template: `
    <h1>{{ user()?.name }}</h1>
  `
})
export class ModernComponent {
  // Direct field injection - clean and readable
  private userService = inject(UserService);
  private authService = inject(AuthService);
  private router = inject(Router);
  private destroyRef = inject(DestroyRef);

  // Signals can use injected services
  user = this.userService.currentUser;

  constructor() {
    // inject() can also be used in constructor
    const logger = inject(LoggerService);
    logger.log('Component created');

    // Setup subscriptions with automatic cleanup
    this.authService.authState$
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(state => {
        if (!state.authenticated) {
          this.router.navigate(['/login']);
        }
      });
  }
}
```

### Constructor Injection (Legacy - Still Valid)

```typescript
import { Component } from '@angular/core';

@Component({
  selector: 'app-legacy',
  standalone: true,
  template: `...`
})
export class LegacyComponent {
  constructor(
    private userService: UserService,
    private authService: AuthService,
    private router: Router
  ) {
    // All dependencies declared in constructor
  }
}
```

### Inheritance: inject() is Cleaner

```typescript
// With inject() - No super() headaches
class BaseComponent {
  protected logger = inject(LoggerService);
  protected router = inject(Router);
}

@Component({ ... })
class ChildComponent extends BaseComponent {
  // No need to call super() or redeclare dependencies
  private userService = inject(UserService);

  ngOnInit() {
    this.logger.log('Child initialized');  // Works!
  }
}

// With constructor injection - Must handle inheritance
class BaseComponentLegacy {
  constructor(
    protected logger: LoggerService,
    protected router: Router
  ) {}
}

@Component({ ... })
class ChildComponentLegacy extends BaseComponentLegacy {
  constructor(
    logger: LoggerService,
    router: Router,
    private userService: UserService
  ) {
    super(logger, router);  // Must call super with all deps
  }
}
```

### inject() in Factory Functions

```typescript
// inject() works in factory functions during DI context
function createDataService(): DataService {
  const http = inject(HttpClient);
  const config = inject(APP_CONFIG);
  const cache = inject(CacheService);

  return new OptimizedDataService(http, config, cache);
}

export const appConfig: ApplicationConfig = {
  providers: [
    { provide: DataService, useFactory: createDataService }
  ]
};
```

### Optional Dependencies

```typescript
@Component({ ... })
export class FlexibleComponent {
  // Modern: inject() with optional
  private analytics = inject(AnalyticsService, { optional: true });

  // Modern: inject() with default value
  private config = inject(APP_CONFIG, { optional: true }) ?? defaultConfig;

  // Legacy: @Optional() decorator
  constructor(
    @Optional() private legacyAnalytics: AnalyticsService | null
  ) {}

  trackEvent(event: string) {
    // Null-safe access for optional dependencies
    this.analytics?.track(event);
  }
}
```

### Self, SkipSelf, Host with inject()

```typescript
@Component({
  selector: 'app-child',
  standalone: true,
  providers: [LoggerService],  // Local provider
  template: `...`
})
export class ChildComponent {
  // Only look in this component's injector
  private localLogger = inject(LoggerService, { self: true });

  // Skip this component, look in parent
  private parentLogger = inject(LoggerService, { skipSelf: true });

  // Stop at host component's injector
  private hostLogger = inject(LoggerService, { host: true });

  // Combination: skip self, but make it optional
  private maybeParentLogger = inject(LoggerService, { 
    skipSelf: true, 
    optional: true 
  });
}
```

---

## forwardRef

`forwardRef` solves circular dependency issues when a class references another class that hasn't been defined yet.

### Problem: Circular Dependencies

```typescript
// ❌ Error: Cannot access 'ChildService' before initialization

@Injectable({ providedIn: 'root' })
class ParentService {
  constructor(private child: ChildService) {}  // Error!
}

@Injectable({ providedIn: 'root' })
class ChildService {
  constructor(private parent: ParentService) {}
}
```

### Solution: forwardRef

```typescript
import { forwardRef, Injectable, inject } from '@angular/core';

@Injectable({ providedIn: 'root' })
class ParentService {
  // Using inject() with forwardRef
  private child = inject(forwardRef(() => ChildService));

  getChildData() {
    return this.child.getData();
  }
}

@Injectable({ providedIn: 'root' })
class ChildService {
  private parent = inject(forwardRef(() => ParentService));

  getData() {
    return 'child data';
  }
}
```

### forwardRef with Providers

```typescript
// When providing a service that references itself
export const appConfig: ApplicationConfig = {
  providers: [
    {
      provide: TreeNodeService,
      useFactory: () => {
        const parent = inject(
          forwardRef(() => TreeNodeService), 
          { optional: true, skipSelf: true }
        );
        return new TreeNodeService(parent);
      }
    }
  ]
};
```

### forwardRef with ContentChild/ViewChild

```typescript
@Component({
  selector: 'app-parent',
  standalone: true,
  template: `
    <ng-content></ng-content>
  `
})
export class ParentComponent {
  // Reference a child component type defined later
  @ContentChildren(forwardRef(() => ChildItemComponent))
  children!: QueryList<ChildItemComponent>;
}

@Component({
  selector: 'app-child-item',
  standalone: true,
  template: `<span>Child</span>`
})
export class ChildItemComponent {
  parent = inject(ParentComponent);
}
```

### When to Use forwardRef

```
┌─────────────────────────────────────────────────────────────┐
│                  When to Use forwardRef                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ USE when:                                                │
│     • Two services have circular dependencies                │
│     • A service references a class defined later in file     │
│     • A directive queries components defined below it        │
│     • Self-referential tree structures                       │
│                                                              │
│  ❌ AVOID when possible:                                     │
│     • Circular dependencies often indicate design issues     │
│     • Consider refactoring to break the cycle               │
│     • Extract shared logic to a third service                │
│                                                              │
│  🔄 Alternative: Refactor to break cycles                    │
│                                                              │
│     Before:   A → B → A (circular)                          │
│                                                              │
│     After:    A → C ← B (shared dependency)                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference Card

### Provider Syntax Cheatsheet

```typescript
// 1. Class provider (shorthand)
providers: [MyService]
// Equivalent to:
providers: [{ provide: MyService, useClass: MyService }]

// 2. useClass - Different implementation
providers: [{ provide: AbstractService, useClass: ConcreteService }]

// 3. useValue - Static value
providers: [{ provide: CONFIG_TOKEN, useValue: { api: 'https://...' } }]

// 4. useFactory - Dynamic creation
providers: [{
  provide: MyService,
  useFactory: () => {
    const dep = inject(OtherService);
    return new MyService(dep);
  }
}]

// 5. useExisting - Alias
providers: [{ provide: OldService, useExisting: NewService }]

// 6. Multi provider
providers: [
  { provide: VALIDATORS, useValue: validator1, multi: true },
  { provide: VALIDATORS, useValue: validator2, multi: true }
]
```

### inject() Options

```typescript
// Basic injection
const service = inject(MyService);

// Optional (returns null if not found)
const optional = inject(MyService, { optional: true });

// Self only (don't look up the tree)
const self = inject(MyService, { self: true });

// Skip self (start from parent)
const parent = inject(MyService, { skipSelf: true });

// Host only (stop at host component)
const host = inject(MyService, { host: true });

// Combinations
const combo = inject(MyService, { skipSelf: true, optional: true });
```

### InjectionToken Patterns

```typescript
// Simple token
const TOKEN = new InjectionToken<string>('description');

// Token with factory (auto-provided)
const TOKEN = new InjectionToken<Service>('service', {
  providedIn: 'root',
  factory: () => new Service(inject(Dependency))
});

// Token for interfaces
interface Config { ... }
const CONFIG = new InjectionToken<Config>('config');
```

### Hierarchical Injection Summary

```
┌────────────────────────────────────────────────────────────┐
│                   INJECTION HIERARCHY                       │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Level          │ How to Provide        │ Scope            │
│  ───────────────┼───────────────────────┼────────────────  │
│  Platform       │ providedIn:'platform' │ Multi-app        │
│  Root           │ providedIn:'root'     │ App singleton    │
│  Route          │ Route providers       │ Lazy route       │
│  Component      │ providers: []         │ Component tree   │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Common Pitfalls

```typescript
// ❌ Forgetting providedIn (not tree-shakable)
@Injectable()  // Missing providedIn!
class MyService {}

// ✅ Always specify providedIn or provide explicitly
@Injectable({ providedIn: 'root' })
class MyService {}

// ❌ Using inject() outside injection context
class NotAService {
  service = inject(MyService);  // Error at runtime!
}

// ✅ inject() only in DI context (components, services, factories)
@Injectable({ providedIn: 'root' })
class MyOtherService {
  service = inject(MyService);  // OK!
}

// ❌ Circular dependency without forwardRef
class A {
  b = inject(B);  // Error if B defined below
}
class B {
  a = inject(A);
}

// ✅ Use forwardRef for circular deps
class A {
  b = inject(forwardRef(() => B));
}
```

---

## Best Practices Summary

1. **Prefer `inject()` over constructor injection** in new code
2. **Use `providedIn: 'root'`** for application-wide singletons
3. **Use component `providers`** for component-scoped services
4. **Use `InjectionToken`** for non-class dependencies
5. **Avoid circular dependencies** - refactor if possible
6. **Use functional interceptors** instead of class-based (Angular 15+)
7. **Leverage multi providers** for extensible plugin systems
8. **Keep services focused** - single responsibility principle
9. **Consider testability** - inject dependencies, don't create them
10. **Use `forwardRef` sparingly** - it's a code smell for design issues
