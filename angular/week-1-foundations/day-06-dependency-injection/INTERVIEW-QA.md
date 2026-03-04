# Day 6: Dependency Injection - Interview Questions & Answers

## Table of Contents
1. [Basic Questions (1-4)](#basic-questions)
2. [Intermediate Questions (5-8)](#intermediate-questions)
3. [Advanced Questions (9-12)](#advanced-questions)
4. [Scenario-Based Questions (13-15)](#scenario-based-questions)
5. [Interview Tips](#interview-tips)

---

## Basic Questions

### Question 1: What is Dependency Injection and why does Angular use it?

**Answer:**

Dependency Injection (DI) is a design pattern where a class receives its dependencies from an external source rather than creating them internally. Angular has a built-in DI framework that's fundamental to how the framework works.

```typescript
// ❌ Without DI - tight coupling
class UserComponent {
  private userService: UserService;
  
  constructor() {
    // Component creates its own dependency
    this.userService = new UserService(new HttpClient(), new CacheService());
  }
}

// ✅ With DI - loose coupling
@Component({
  selector: 'app-user',
  standalone: true,
  template: `...`
})
class UserComponent {
  // Angular injects the dependency
  private userService = inject(UserService);
}
```

**Why Angular uses DI:**

| Benefit | Explanation |
|---------|-------------|
| **Testability** | Easy to mock dependencies in unit tests |
| **Loose Coupling** | Components don't know how dependencies are created |
| **Maintainability** | Change implementations without modifying consumers |
| **Reusability** | Share service instances across components |
| **Configurability** | Swap implementations based on environment |

**Interview Tip:** Mention that DI is one of Angular's core concepts and enables features like lazy loading and tree-shaking of unused services.

---

### Question 2: Explain the difference between `providedIn: 'root'` and component-level providers.

**Answer:**

```typescript
// providedIn: 'root' - Application-wide singleton
@Injectable({
  providedIn: 'root'
})
class AuthService {
  private user = signal<User | null>(null);
  
  // Same instance shared everywhere
  getCurrentUser() {
    return this.user.asReadonly();
  }
}

// Component-level providers - Scoped instances
@Injectable()
class FormStateService {
  private formData = signal<Record<string, unknown>>({});
}

@Component({
  selector: 'app-user-form',
  standalone: true,
  providers: [FormStateService],  // Each component instance gets new service
  template: `...`
})
class UserFormComponent {
  formState = inject(FormStateService);
}
```

**Visual Comparison:**

```
providedIn: 'root'                    Component providers
┌─────────────────────┐               ┌─────────────────────┐
│    Root Injector    │               │                     │
│  ┌───────────────┐  │               │  Form A             │
│  │ AuthService   │  │               │  ┌───────────────┐  │
│  │ (singleton)   │  │               │  │FormStateService│  │
│  └───────────────┘  │               │  │  (instance 1)  │  │
│         │          │               │  └───────────────┘  │
│    ┌────┴────┐     │               │                     │
│    ▼         ▼     │               │  Form B             │
│  Comp A   Comp B   │               │  ┌───────────────┐  │
│  (same)   (same)   │               │  │FormStateService│  │
│                     │               │  │  (instance 2)  │  │
└─────────────────────┘               │  └───────────────┘  │
                                       └─────────────────────┘
```

| Aspect | `providedIn: 'root'` | Component Providers |
|--------|---------------------|---------------------|
| Scope | Application singleton | Per component instance |
| Tree-shaking | ✅ Automatic | ✅ If not used |
| Use case | Global state, auth, HTTP | Form state, local data |
| Memory | One instance | Instance per component |

---

### Question 3: What is the `inject()` function and how does it differ from constructor injection?

**Answer:**

```typescript
// Modern approach: inject() function (Angular 14+)
@Component({
  selector: 'app-modern',
  standalone: true,
  template: `{{ data() }}`
})
class ModernComponent {
  // Field-level injection - clean and readable
  private dataService = inject(DataService);
  private router = inject(Router);
  private destroyRef = inject(DestroyRef);
  
  data = this.dataService.getData();
  
  constructor() {
    // inject() also works in constructor
    const logger = inject(LoggerService);
  }
}

// Legacy approach: Constructor injection
@Component({
  selector: 'app-legacy',
  standalone: true,
  template: `...`
})
class LegacyComponent {
  constructor(
    private dataService: DataService,
    private router: Router,
    @Optional() private analytics: AnalyticsService | null
  ) {}
}
```

**Key Differences:**

| Feature | `inject()` | Constructor Injection |
|---------|-----------|----------------------|
| Location | Field, constructor, factory | Constructor only |
| Inheritance | Cleaner (no super calls needed) | Requires super() with all deps |
| Optional deps | `inject(S, { optional: true })` | `@Optional()` decorator |
| Code style | More functional | More traditional OOP |
| Angular version | 14+ | All versions |

**Inheritance Example:**

```typescript
// inject() makes inheritance easy
class BaseComponent {
  protected logger = inject(LoggerService);
}

@Component({ ... })
class ChildComponent extends BaseComponent {
  private userService = inject(UserService);
  // No super() needed, logger is available
}
```

**Interview Tip:** Emphasize that `inject()` is the modern preferred approach in Angular 15+ and makes the code more functional and easier to refactor.

---

### Question 4: What is an InjectionToken and when would you use it?

**Answer:**

`InjectionToken` creates a unique token for dependency injection when you can't use a class as the token (primitives, interfaces, functions).

```typescript
import { InjectionToken, inject } from '@angular/core';

// Problem: Can't use interface as DI token
interface AppConfig {
  apiUrl: string;
  timeout: number;
}

// Solution: Create an InjectionToken
export const APP_CONFIG = new InjectionToken<AppConfig>('app.config');

// Token with built-in factory (self-providing)
export const WINDOW = new InjectionToken<Window>('window', {
  providedIn: 'root',
  factory: () => window
});

export const DOCUMENT = new InjectionToken<Document>('document', {
  providedIn: 'root',
  factory: () => inject(WINDOW).document
});

// Providing the token
export const appConfig: ApplicationConfig = {
  providers: [
    {
      provide: APP_CONFIG,
      useValue: {
        apiUrl: 'https://api.example.com',
        timeout: 5000
      }
    }
  ]
};

// Using the token
@Injectable({ providedIn: 'root' })
class ApiService {
  private config = inject(APP_CONFIG);
  private document = inject(DOCUMENT);
  
  getApiUrl() {
    return this.config.apiUrl;
  }
}
```

**Common Use Cases:**

```
┌────────────────────────────────────────────────────────────┐
│              InjectionToken Use Cases                       │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Configuration Objects                                   │
│     const CONFIG = new InjectionToken<Config>('config')    │
│                                                             │
│  2. Browser APIs                                           │
│     const STORAGE = new InjectionToken<Storage>('storage') │
│                                                             │
│  3. Function tokens                                        │
│     const VALIDATOR = new InjectionToken<ValidatorFn>(...) │
│                                                             │
│  4. Third-party libraries                                  │
│     const STRIPE = new InjectionToken<Stripe>('stripe')    │
│                                                             │
│  5. Environment-specific values                            │
│     const API_URL = new InjectionToken<string>('api.url')  │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

---

## Intermediate Questions

### Question 5: Explain Angular's hierarchical injector system and how dependency resolution works.

**Answer:**

Angular has two parallel injector hierarchies that form a tree structure:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENVIRONMENT INJECTORS                             │
│            (Platform → Root → Route Injectors)                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    NULL INJECTOR                             │   │
│   │              (throws NullInjectorError)                      │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              ▲                                       │
│                              │                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                  PLATFORM INJECTOR                           │   │
│   │             providedIn: 'platform'                           │   │
│   │        (shared across multiple Angular apps)                 │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              ▲                                       │
│                              │                                       │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    ROOT INJECTOR                             │   │
│   │               providedIn: 'root'                             │   │
│   │            (application singletons)                          │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              ▲                                       │
│              ┌───────────────┴───────────────┐                      │
│              │                               │                      │
│   ┌──────────────────────┐    ┌──────────────────────┐             │
│   │   LAZY ROUTE A       │    │    LAZY ROUTE B      │             │
│   │   Route Injector     │    │    Route Injector    │             │
│   └──────────────────────┘    └──────────────────────┘             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     ELEMENT INJECTORS                                │
│               (Component Hierarchy)                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                    AppComponent                              │   │
│   │                 (Element Injector)                           │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                              │                                       │
│              ┌───────────────┼───────────────┐                      │
│              ▼               ▼               ▼                      │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│   │   Header     │  │    Main      │  │   Footer     │             │
│   │  (Element)   │  │  (Element)   │  │  (Element)   │             │
│   └──────────────┘  └──────────────┘  └──────────────┘             │
│                              │                                       │
│                      ┌───────┴───────┐                              │
│                      ▼               ▼                              │
│               ┌──────────┐    ┌──────────┐                          │
│               │ Sidebar  │    │ Content  │                          │
│               └──────────┘    └──────────┘                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Resolution Process:**

```typescript
@Component({
  selector: 'app-child',
  standalone: true,
  providers: [LocalService],
  template: `...`
})
class ChildComponent {
  // Resolution order for each inject():
  
  // 1. Check element injector (self)
  local = inject(LocalService);  // Found in component providers
  
  // 2. Walk up element injector tree, then environment injectors
  global = inject(GlobalService);  // Found in root injector
  
  // 3. Use options to modify resolution
  parentOnly = inject(SomeService, { skipSelf: true });  // Skip self
  selfOnly = inject(SomeService, { self: true });  // Only check self
  optional = inject(SomeService, { optional: true });  // Return null if not found
}
```

**Resolution Algorithm:**

```
Request Service X
       │
       ▼
┌──────────────────┐
│ Check Element    │──Found──▶ Return Instance
│ Injector (self)  │
└──────────────────┘
       │ Not Found
       ▼
┌──────────────────┐
│ Check Parent     │──Found──▶ Return Instance
│ Element Injector │
└──────────────────┘
       │ Not Found
       ▼
  ... continue up element tree ...
       │ Not Found
       ▼
┌──────────────────┐
│ Check Route      │──Found──▶ Return Instance
│ Injector         │
└──────────────────┘
       │ Not Found
       ▼
┌──────────────────┐
│ Check Root       │──Found──▶ Return Instance
│ Injector         │
└──────────────────┘
       │ Not Found
       ▼
┌──────────────────┐
│ Check Platform   │──Found──▶ Return Instance
│ Injector         │
└──────────────────┘
       │ Not Found
       ▼
┌──────────────────┐
│ NULL Injector    │──────────▶ Throw NullInjectorError
└──────────────────┘
```

---

### Question 6: What are the different provider types (useClass, useValue, useFactory, useExisting)?

**Answer:**

```typescript
// 1. useClass - Provide a different class implementation
abstract class StorageService {
  abstract get(key: string): string | null;
  abstract set(key: string, value: string): void;
}

@Injectable()
class LocalStorageService extends StorageService {
  get(key: string) { return localStorage.getItem(key); }
  set(key: string, value: string) { localStorage.setItem(key, value); }
}

@Injectable()
class SessionStorageService extends StorageService {
  get(key: string) { return sessionStorage.getItem(key); }
  set(key: string, value: string) { sessionStorage.setItem(key, value); }
}

providers: [
  {
    provide: StorageService,
    useClass: environment.persistData ? LocalStorageService : SessionStorageService
  }
]

// 2. useValue - Provide a static value
const config = {
  apiUrl: 'https://api.example.com',
  maxRetries: 3,
  features: { darkMode: true }
};

providers: [
  { provide: APP_CONFIG, useValue: config },
  { provide: IS_PRODUCTION, useValue: true },
  { provide: VERSION, useValue: '1.2.3' }
]

// 3. useFactory - Dynamic creation with dependencies
providers: [
  {
    provide: LoggerService,
    useFactory: () => {
      const config = inject(APP_CONFIG);
      const http = inject(HttpClient);
      
      if (config.features.remoteLogging) {
        return new RemoteLoggerService(http, config.apiUrl);
      }
      return new ConsoleLoggerService();
    }
  }
]

// 4. useExisting - Create an alias to another provider
@Injectable({ providedIn: 'root' })
class NewAuthService {
  login() { /* new implementation */ }
}

abstract class LegacyAuthService {
  abstract login(): void;
}

providers: [
  // LegacyAuthService points to same instance as NewAuthService
  { provide: LegacyAuthService, useExisting: NewAuthService }
]
```

**Summary Table:**

| Provider Type | When to Use | Example |
|--------------|-------------|---------|
| `useClass` | Swap implementations | Mock services, A/B testing |
| `useValue` | Static configuration | API URLs, feature flags |
| `useFactory` | Dynamic/conditional creation | Environment-based services |
| `useExisting` | Alias services | Legacy compatibility |

---

### Question 7: What are multi providers and when would you use them?

**Answer:**

Multi providers allow multiple values to be registered under the same token, returning an array when injected.

```typescript
// Define the token
export const VALIDATORS = new InjectionToken<ValidatorFn[]>('validators');

// Validator functions
const required: ValidatorFn = (ctrl) => 
  ctrl.value ? null : { required: true };

const minLength: ValidatorFn = (ctrl) => 
  (ctrl.value?.length ?? 0) >= 3 ? null : { minLength: 3 };

const noWhitespace: ValidatorFn = (ctrl) => 
  /\s/.test(ctrl.value ?? '') ? { whitespace: true } : null;

// Register multiple values with multi: true
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: VALIDATORS, useValue: required, multi: true },
    { provide: VALIDATORS, useValue: minLength, multi: true },
    { provide: VALIDATORS, useValue: noWhitespace, multi: true }
  ]
};

// Inject returns an array
@Component({ ... })
class FormComponent {
  private validators = inject(VALIDATORS);
  // validators = [required, minLength, noWhitespace]
  
  validate(control: AbstractControl) {
    return this.validators
      .map(v => v(control))
      .filter(Boolean);
  }
}
```

**Practical Example: Plugin System**

```typescript
interface Plugin {
  name: string;
  initialize(): Promise<void>;
}

const APP_PLUGINS = new InjectionToken<Plugin[]>('plugins');

// Core plugin (always included)
const corePlugin: Plugin = {
  name: 'Core',
  initialize: async () => console.log('Core initialized')
};

// Analytics plugin (feature module)
const analyticsPlugin: Plugin = {
  name: 'Analytics',
  initialize: async () => console.log('Analytics tracking started')
};

// Register in app config
providers: [
  { provide: APP_PLUGINS, useValue: corePlugin, multi: true },
  { provide: APP_PLUGINS, useValue: analyticsPlugin, multi: true }
]

// Feature module can add more plugins
// In a lazy-loaded route:
providers: [
  { provide: APP_PLUGINS, useValue: featurePlugin, multi: true }
]

// Plugin manager initializes all
@Injectable({ providedIn: 'root' })
class PluginManager {
  plugins = inject(APP_PLUGINS);

  async initializeAll() {
    for (const plugin of this.plugins) {
      await plugin.initialize();
    }
  }
}
```

**Built-in Multi Tokens:**

```typescript
// Modern way: Functional interceptors (not multi providers)
export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([authInterceptor, loggingInterceptor])
    )
  ]
};

// APP_INITIALIZER - Run code at app startup
providers: [
  {
    provide: APP_INITIALIZER,
    useFactory: () => {
      const config = inject(ConfigService);
      return () => config.load();  // Returns Promise
    },
    multi: true
  },
  {
    provide: APP_INITIALIZER,
    useFactory: () => {
      const auth = inject(AuthService);
      return () => auth.checkSession();
    },
    multi: true
  }
]
```

---

### Question 8: How do you handle optional dependencies in Angular?

**Answer:**

```typescript
@Component({
  selector: 'app-feature',
  standalone: true,
  template: `
    @if (hasAnalytics) {
      <div>Analytics enabled</div>
    }
  `
})
class FeatureComponent {
  // Modern: inject() with optional flag
  private analytics = inject(AnalyticsService, { optional: true });
  
  // With default value
  private config = inject(APP_CONFIG, { optional: true }) ?? {
    apiUrl: 'http://localhost:3000',
    timeout: 5000
  };
  
  // Computed flag for template
  hasAnalytics = !!this.analytics;
  
  trackEvent(event: string) {
    // Null-safe calls
    this.analytics?.trackEvent(event);
  }
}

// Legacy: @Optional() decorator
@Component({ ... })
class LegacyComponent {
  constructor(
    @Optional() private analytics: AnalyticsService | null,
    @Optional() @Inject(APP_CONFIG) private config: AppConfig | null
  ) {}
}
```

**Combining Resolution Modifiers:**

```typescript
@Component({
  selector: 'app-child',
  standalone: true,
  providers: [ChildService],
  template: `...`
})
class ChildComponent {
  // Self: Only look in this component's injector
  childService = inject(ChildService, { self: true });
  
  // SkipSelf: Skip this injector, look in parent
  parentService = inject(ParentService, { skipSelf: true });
  
  // Optional + SkipSelf: Get from parent or null
  maybeParent = inject(ParentService, { 
    skipSelf: true, 
    optional: true 
  });
  
  // Host: Stop at the host component boundary
  hostService = inject(HostService, { host: true });
}
```

**Resolution Modifier Summary:**

```
┌────────────────────────────────────────────────────────────┐
│                Resolution Modifiers                         │
├───────────┬────────────────────────────────────────────────┤
│ Modifier  │ Behavior                                        │
├───────────┼────────────────────────────────────────────────┤
│ (none)    │ Walk up entire injector tree                   │
│ self      │ Only check current injector                    │
│ skipSelf  │ Skip current, start from parent                │
│ host      │ Stop at host component boundary                │
│ optional  │ Return null instead of throwing error          │
└───────────┴────────────────────────────────────────────────┘
```

---

## Advanced Questions

### Question 9: Explain forwardRef and when you need to use it.

**Answer:**

`forwardRef` allows referencing a class that hasn't been defined yet, solving circular dependency issues.

```typescript
// Problem: Circular reference
// File A depends on B, B depends on A

// ❌ Without forwardRef - Error!
@Injectable({ providedIn: 'root' })
class ParentService {
  child = inject(ChildService);  // Error: ChildService not defined yet
}

@Injectable({ providedIn: 'root' })
class ChildService {
  parent = inject(ParentService);
}

// ✅ With forwardRef - Works!
import { forwardRef, inject, Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
class ParentService {
  private child = inject(forwardRef(() => ChildService));
  
  getChildData() {
    return this.child.getData();
  }
}

@Injectable({ providedIn: 'root' })
class ChildService {
  private parent = inject(forwardRef(() => ParentService));
  
  getData() {
    return 'data from child';
  }
}
```

**Common Use Cases:**

```typescript
// 1. Content queries for components defined later
@Component({
  selector: 'app-tabs',
  standalone: true,
  template: `<ng-content></ng-content>`
})
class TabsComponent {
  @ContentChildren(forwardRef(() => TabComponent))
  tabs!: QueryList<TabComponent>;
}

@Component({
  selector: 'app-tab',
  standalone: true,
  template: `<ng-content></ng-content>`
})
class TabComponent {
  parent = inject(TabsComponent);  // OK - TabsComponent defined above
}

// 2. Self-referential tree structures
@Injectable()
class TreeNode {
  constructor(
    public value: string,
    @Optional() @SkipSelf() 
    public parent: TreeNode | null
  ) {}
}

// 3. Provider with forward reference
providers: [
  {
    provide: SOME_TOKEN,
    useFactory: () => inject(forwardRef(() => ServiceDefinedBelow))
  }
]
```

**When NOT to Use forwardRef:**

```
┌─────────────────────────────────────────────────────────────┐
│            forwardRef - Design Smell Warning                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Circular dependencies often indicate design problems.      │
│  Consider refactoring:                                      │
│                                                             │
│  Before (circular):                                         │
│       A ──────▶ B                                          │
│       ▲         │                                          │
│       └─────────┘                                          │
│                                                             │
│  After (extracted shared logic):                           │
│       A ──────▶ C ◀────── B                               │
│                                                             │
│  Or use events/observables for communication:              │
│       A ──events──▶ EventBus ◀──subscribes── B            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

### Question 10: How does tree-shaking work with Angular's DI system?

**Answer:**

Tree-shaking removes unused code from the final bundle. Angular's DI supports tree-shaking through `providedIn` and proper provider registration.

```typescript
// ✅ Tree-shakable: providedIn: 'root'
@Injectable({
  providedIn: 'root'
})
class TreeShakableService {
  // If no component injects this, it's removed from bundle
}

// ❌ Not tree-shakable: Module providers array
@NgModule({
  providers: [NotTreeShakableService]  // Always included
})
class SomeModule {}

// ✅ Tree-shakable: InjectionToken with factory
const FEATURE_SERVICE = new InjectionToken<FeatureService>('feature', {
  providedIn: 'root',
  factory: () => new FeatureService(inject(HttpClient))
});
```

**How It Works:**

```
┌─────────────────────────────────────────────────────────────┐
│                  Tree-Shaking Flow                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Build Time Analysis:                                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 1. Bundler scans all import statements              │    │
│  │ 2. Tracks which classes are actually used           │    │
│  │ 3. providedIn creates a reference FROM the service   │    │
│  │    TO the injector (not the other way)              │    │
│  │ 4. If service is never imported/injected, it's dead │    │
│  │    code and gets removed                             │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  providedIn: 'root' (Tree-Shakable)                         │
│  ┌──────────────────┐                                       │
│  │ Service          │──reference──▶ Root Injector           │
│  │ (defines where   │              (doesn't reference        │
│  │  it's provided)  │               the service)             │
│  └──────────────────┘                                       │
│         │                                                    │
│         ▼                                                    │
│  If no component imports → REMOVED from bundle              │
│                                                              │
│  Module providers[] (NOT Tree-Shakable)                     │
│  ┌──────────────────┐                                       │
│  │ NgModule         │──reference──▶ Service                 │
│  │ providers: [Svc] │              (always imported)        │
│  └──────────────────┘                                       │
│         │                                                    │
│         ▼                                                    │
│  Module is used → Service always INCLUDED                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Best Practices for Tree-Shaking:**

```typescript
// 1. Always use providedIn for services
@Injectable({ providedIn: 'root' })
class MyService {}

// 2. Use InjectionToken with factory for values
const MY_CONFIG = new InjectionToken('config', {
  providedIn: 'root',
  factory: () => ({ apiUrl: '/api' })
});

// 3. Lazy load feature modules
const routes: Routes = [
  {
    path: 'admin',
    loadComponent: () => import('./admin/admin.component')
      .then(m => m.AdminComponent),
    providers: [
      // These services only loaded with admin route
      AdminService
    ]
  }
];

// 4. Avoid importing services you don't use
// ❌ Bad: import { UnusedService } from './unused.service';
// ✅ Good: Only import what you inject
```

---

### Question 11: How do you test services with dependencies using Angular's DI?

**Answer:**

```typescript
// Service to test
@Injectable({ providedIn: 'root' })
class UserService {
  private http = inject(HttpClient);
  private config = inject(APP_CONFIG);

  getUser(id: string): Observable<User> {
    return this.http.get<User>(`${this.config.apiUrl}/users/${id}`);
  }
}

// Test file: user.service.spec.ts
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';

describe('UserService', () => {
  let service: UserService;
  let httpMock: HttpTestingController;

  const mockConfig = {
    apiUrl: 'https://test-api.com'
  };

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        UserService,
        { provide: APP_CONFIG, useValue: mockConfig }
      ]
    });

    service = TestBed.inject(UserService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();  // Ensure no outstanding requests
  });

  it('should fetch user by id', () => {
    const mockUser: User = { id: '123', name: 'Test User' };

    service.getUser('123').subscribe(user => {
      expect(user).toEqual(mockUser);
    });

    const req = httpMock.expectOne('https://test-api.com/users/123');
    expect(req.request.method).toBe('GET');
    req.flush(mockUser);
  });
});
```

**Testing with Mock Services:**

```typescript
// Abstract service (for clean mocking)
abstract class DataService {
  abstract getData(): Observable<Data[]>;
}

// Real implementation
@Injectable({ providedIn: 'root' })
class ApiDataService extends DataService {
  private http = inject(HttpClient);
  
  getData(): Observable<Data[]> {
    return this.http.get<Data[]>('/api/data');
  }
}

// Mock for testing
class MockDataService extends DataService {
  getData(): Observable<Data[]> {
    return of([{ id: 1, name: 'Mock' }]);
  }
}

// Component test
describe('DataComponent', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [DataComponent],
      providers: [
        { provide: DataService, useClass: MockDataService }
      ]
    });
  });

  it('should display data', () => {
    const fixture = TestBed.createComponent(DataComponent);
    fixture.detectChanges();
    
    expect(fixture.nativeElement.textContent).toContain('Mock');
  });
});
```

**Testing with Jasmine Spies:**

```typescript
describe('Component with spied service', () => {
  let authServiceSpy: jasmine.SpyObj<AuthService>;

  beforeEach(() => {
    // Create spy object
    authServiceSpy = jasmine.createSpyObj('AuthService', [
      'login', 
      'logout', 
      'isAuthenticated'
    ]);
    
    // Configure return values
    authServiceSpy.isAuthenticated.and.returnValue(true);
    authServiceSpy.login.and.returnValue(of({ success: true }));

    TestBed.configureTestingModule({
      imports: [ProtectedComponent],
      providers: [
        { provide: AuthService, useValue: authServiceSpy }
      ]
    });
  });

  it('should call login on submit', () => {
    const fixture = TestBed.createComponent(ProtectedComponent);
    const component = fixture.componentInstance;
    
    component.onLoginSubmit({ email: 'test@test.com', password: 'pwd' });
    
    expect(authServiceSpy.login).toHaveBeenCalledWith({
      email: 'test@test.com',
      password: 'pwd'
    });
  });
});
```

---

### Question 12: Explain the difference between module injectors and element injectors.

**Answer:**

Angular has two parallel injector hierarchies:

```
┌─────────────────────────────────────────────────────────────────────┐
│                ENVIRONMENT INJECTORS (Module/Route)                  │
│     Services registered with providedIn or route providers          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   Platform Injector                                                  │
│         │                                                            │
│         ▼                                                            │
│   Root Injector ◄─── @Injectable({ providedIn: 'root' })            │
│   (bootstrapApplication providers)                                   │
│         │                                                            │
│         ├───────────────┬───────────────┐                           │
│         ▼               ▼               ▼                           │
│   Lazy Route A    Lazy Route B    Lazy Route C                      │
│   (route providers) (route providers) (route providers)             │
│                                                                      │
│   Characteristics:                                                   │
│   • Singleton within scope                                          │
│   • Shared across all components in scope                           │
│   • Survives component destruction                                  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                   ELEMENT INJECTORS (Component)                      │
│           Services registered in component providers                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   AppComponent (element injector)                                   │
│         │                                                            │
│         ├─────────────────┬─────────────────┐                       │
│         ▼                 ▼                 ▼                       │
│   HeaderComponent    MainComponent    FooterComponent               │
│         │                 │                                         │
│         │           ┌─────┴─────┐                                   │
│         │           ▼           ▼                                   │
│         │     SidebarComp   ContentComp                             │
│         │                       │                                   │
│         │                 ┌─────┴─────┐                             │
│         ▼                 ▼           ▼                             │
│   NavComponent      CardComp     ListComp                           │
│                                                                      │
│   Characteristics:                                                   │
│   • New instance per component with providers: []                   │
│   • Destroyed with component                                        │
│   • Child components share parent's instance                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Practical Examples:**

```typescript
// Environment Injector: Global auth state
@Injectable({ providedIn: 'root' })
class AuthService {
  private isAuthenticated = signal(false);
  // One instance for entire app
}

// Element Injector: Form state per instance
@Injectable()
class FormStateService {
  private data = signal({});
  // New instance per form component
}

@Component({
  selector: 'app-user-form',
  standalone: true,
  providers: [FormStateService],  // Element injector
  template: `
    <app-name-field />
    <app-email-field />
  `
})
class UserFormComponent {
  formState = inject(FormStateService);
}

// Child gets SAME instance from parent's element injector
@Component({
  selector: 'app-name-field',
  standalone: true,
  template: `...`
})
class NameFieldComponent {
  // Same FormStateService as parent
  formState = inject(FormStateService);
}
```

**Resolution Order:**

```typescript
@Component({
  selector: 'app-child',
  standalone: true,
  providers: [LocalService],
  template: `...`
})
class ChildComponent {
  // 1. Check ChildComponent's element injector (FOUND - LocalService)
  local = inject(LocalService);
  
  // 2. Walk up element injectors (not found in any)
  // 3. Check route injector (if lazy loaded)
  // 4. Check root injector (FOUND - AuthService)
  auth = inject(AuthService);
  
  // 5. Check platform injector
  // 6. Null injector (throws if not found)
}
```

---

## Scenario-Based Questions

### Question 13: How would you implement a service that needs different instances for different feature areas but the same instance within each area?

**Answer:**

Use route-level providers with lazy loading:

```typescript
// Shared service interface
@Injectable()
class FeatureStateService {
  private state = signal<Record<string, unknown>>({});
  
  setState(key: string, value: unknown) {
    this.state.update(s => ({ ...s, [key]: value }));
  }
  
  getState() {
    return this.state.asReadonly();
  }
  
  clear() {
    this.state.set({});
  }
}

// Routes configuration
const routes: Routes = [
  {
    path: 'users',
    loadComponent: () => import('./users/users.component'),
    providers: [FeatureStateService],  // Instance A for user feature
    children: [
      { path: '', component: UserListComponent },
      { path: ':id', component: UserDetailComponent }
    ]
  },
  {
    path: 'products',
    loadComponent: () => import('./products/products.component'),
    providers: [FeatureStateService],  // Instance B for product feature
    children: [
      { path: '', component: ProductListComponent },
      { path: ':id', component: ProductDetailComponent }
    ]
  }
];
```

**Visual:**

```
┌─────────────────────────────────────────────────────────────┐
│                      Root Injector                           │
└─────────────────────────────────────────────────────────────┘
                │                           │
        ┌───────┴───────┐           ┌───────┴───────┐
        ▼               ▼           ▼               ▼
┌─────────────────┐           ┌─────────────────┐
│ /users Route    │           │ /products Route │
│ ┌─────────────┐ │           │ ┌─────────────┐ │
│ │FeatureState │ │           │ │FeatureState │ │
│ │ Instance A  │ │           │ │ Instance B  │ │
│ └─────────────┘ │           │ └─────────────┘ │
│       │         │           │       │         │
│  ┌────┴────┐    │           │  ┌────┴────┐    │
│  ▼         ▼    │           │  ▼         ▼    │
│ List    Detail  │           │ List    Detail  │
│(same A) (same A)│           │(same B) (same B)│
└─────────────────┘           └─────────────────┘
```

---

### Question 14: How would you create a plugin system using Angular's DI?

**Answer:**

```typescript
// 1. Define plugin interface
interface AppPlugin {
  name: string;
  version: string;
  initialize(): Promise<void>;
  destroy(): void;
  isEnabled: Signal<boolean>;
}

// 2. Create injection token
const APP_PLUGINS = new InjectionToken<AppPlugin[]>('app.plugins');

// 3. Create base plugin class
abstract class BasePlugin implements AppPlugin {
  abstract name: string;
  abstract version: string;
  
  private _enabled = signal(true);
  isEnabled = this._enabled.asReadonly();
  
  abstract initialize(): Promise<void>;
  
  destroy() {
    this._enabled.set(false);
  }
  
  protected setEnabled(value: boolean) {
    this._enabled.set(value);
  }
}

// 4. Implement concrete plugins
@Injectable()
class AnalyticsPlugin extends BasePlugin {
  name = 'Analytics';
  version = '1.0.0';
  
  private http = inject(HttpClient);
  
  async initialize() {
    console.log('Analytics plugin initialized');
    // Setup tracking
  }
  
  trackEvent(event: string, data?: object) {
    if (this.isEnabled()) {
      this.http.post('/analytics', { event, data }).subscribe();
    }
  }
}

@Injectable()
class NotificationPlugin extends BasePlugin {
  name = 'Notifications';
  version = '1.0.0';
  
  async initialize() {
    const permission = await Notification.requestPermission();
    this.setEnabled(permission === 'granted');
  }
  
  show(title: string, body: string) {
    if (this.isEnabled()) {
      new Notification(title, { body });
    }
  }
}

// 5. Plugin manager service
@Injectable({ providedIn: 'root' })
class PluginManager {
  private plugins = inject(APP_PLUGINS, { optional: true }) ?? [];
  private initialized = signal(false);
  
  async initializeAll() {
    for (const plugin of this.plugins) {
      console.log(`Initializing ${plugin.name} v${plugin.version}`);
      await plugin.initialize();
    }
    this.initialized.set(true);
  }
  
  getPlugin<T extends AppPlugin>(name: string): T | undefined {
    return this.plugins.find(p => p.name === name) as T | undefined;
  }
  
  destroyAll() {
    this.plugins.forEach(p => p.destroy());
  }
}

// 6. Register plugins
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: APP_PLUGINS, useClass: AnalyticsPlugin, multi: true },
    { provide: APP_PLUGINS, useClass: NotificationPlugin, multi: true },
    // Feature modules can add more plugins
  ]
};

// 7. Use in app initializer
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: APP_PLUGINS, useClass: AnalyticsPlugin, multi: true },
    {
      provide: APP_INITIALIZER,
      useFactory: () => {
        const manager = inject(PluginManager);
        return () => manager.initializeAll();
      },
      multi: true
    }
  ]
};

// 8. Use in components
@Component({ ... })
class SomeComponent {
  private pluginManager = inject(PluginManager);
  
  onAction() {
    const analytics = this.pluginManager.getPlugin<AnalyticsPlugin>('Analytics');
    analytics?.trackEvent('button_click', { id: 'save' });
  }
}
```

---

### Question 15: How do you handle circular dependencies between services?

**Answer:**

Circular dependencies between services are a code smell but sometimes necessary. Here are strategies to handle them:

**Strategy 1: forwardRef (Quick Fix)**

```typescript
// ⚠️ Works but indicates design issues
@Injectable({ providedIn: 'root' })
class ServiceA {
  private serviceB = inject(forwardRef(() => ServiceB));
  
  methodA() {
    return this.serviceB.methodB();
  }
}

@Injectable({ providedIn: 'root' })
class ServiceB {
  private serviceA = inject(forwardRef(() => ServiceA));
  
  methodB() {
    return 'B';
  }
}
```

**Strategy 2: Extract Shared Logic (Best Practice)**

```typescript
// ✅ Better: Extract shared functionality

// Before (circular)
// AuthService → UserService → AuthService

// After (no cycle)
@Injectable({ providedIn: 'root' })
class UserDataService {
  // Shared user data logic
  private currentUser = signal<User | null>(null);
  
  setUser(user: User) { this.currentUser.set(user); }
  getUser() { return this.currentUser.asReadonly(); }
}

@Injectable({ providedIn: 'root' })
class AuthService {
  private userData = inject(UserDataService);
  
  login(credentials: Credentials) {
    // Auth logic, then set user
    this.userData.setUser(user);
  }
}

@Injectable({ providedIn: 'root' })
class UserService {
  private userData = inject(UserDataService);
  
  getCurrentUser() {
    return this.userData.getUser();
  }
}
```

**Strategy 3: Event-Based Communication**

```typescript
// Use events/observables to break the cycle
@Injectable({ providedIn: 'root' })
class EventBus {
  private events = new Subject<AppEvent>();
  events$ = this.events.asObservable();
  
  emit(event: AppEvent) {
    this.events.next(event);
  }
}

@Injectable({ providedIn: 'root' })
class ServiceA {
  private eventBus = inject(EventBus);
  
  doSomething() {
    // Instead of calling ServiceB directly
    this.eventBus.emit({ type: 'A_ACTION', payload: {} });
  }
}

@Injectable({ providedIn: 'root' })
class ServiceB {
  private eventBus = inject(EventBus);
  
  constructor() {
    this.eventBus.events$.pipe(
      filter(e => e.type === 'A_ACTION'),
      takeUntilDestroyed()
    ).subscribe(event => {
      this.handleAAction(event.payload);
    });
  }
}
```

**Strategy 4: Lazy Injection with Injector**

```typescript
@Injectable({ providedIn: 'root' })
class ServiceA {
  private injector = inject(Injector);
  private _serviceB?: ServiceB;
  
  private get serviceB(): ServiceB {
    if (!this._serviceB) {
      this._serviceB = this.injector.get(ServiceB);
    }
    return this._serviceB;
  }
  
  methodA() {
    // ServiceB resolved lazily when needed
    return this.serviceB.methodB();
  }
}
```

**Decision Matrix:**

```
┌──────────────────────────────────────────────────────────────┐
│           Handling Circular Dependencies                      │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Situation                    │ Recommended Approach          │
│  ────────────────────────────┼───────────────────────────────│
│  Quick prototype/fix         │ forwardRef                    │
│  Production: shared state    │ Extract to third service      │
│  Production: loose coupling  │ Event bus / Observable        │
│  Rarely needed dependency    │ Lazy injection via Injector   │
│  Genuine bidirectional need  │ Redesign architecture         │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## Interview Tips

### Key Points to Remember

```
┌──────────────────────────────────────────────────────────────┐
│                   DI Interview Tips                           │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Always mention inject() as the modern approach            │
│                                                               │
│  2. Explain the hierarchical nature of injectors              │
│                                                               │
│  3. Know when to use providedIn: 'root' vs component          │
│     providers (singleton vs scoped)                           │
│                                                               │
│  4. Understand tree-shaking implications                      │
│                                                               │
│  5. Be ready to explain useClass/useValue/useFactory/         │
│     useExisting with real-world examples                      │
│                                                               │
│  6. Know how to test services with TestBed                    │
│                                                               │
│  7. Understand forwardRef but mention it's often a code smell │
│                                                               │
│  8. Be familiar with InjectionToken for non-class deps        │
│                                                               │
│  9. Know the difference between environment and element       │
│     injectors                                                 │
│                                                               │
│  10. Be prepared to discuss multi providers for plugin systems│
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

### Common Interview Mistakes to Avoid

1. **Confusing `providedIn: 'root'` with NgModule providers** - Know that `providedIn` enables tree-shaking

2. **Not knowing `inject()` function** - This is the modern standard since Angular 14+

3. **Overusing forwardRef** - Mention it's a code smell and discuss alternatives

4. **Not understanding injector hierarchy** - Be able to draw and explain the tree

5. **Mixing up resolution modifiers** - Know `self`, `skipSelf`, `host`, and `optional`

6. **Forgetting about testing** - Always mention testability as a key DI benefit

### Quick Syntax Reference

```typescript
// Service registration
@Injectable({ providedIn: 'root' })  // ✅ Tree-shakable singleton

// Modern injection
private service = inject(MyService);
private optional = inject(MyService, { optional: true });
private parent = inject(MyService, { skipSelf: true });

// InjectionToken
const TOKEN = new InjectionToken<Type>('description');
const TOKEN_WITH_FACTORY = new InjectionToken<Type>('desc', {
  providedIn: 'root',
  factory: () => new Type()
});

// Provider types
{ provide: Token, useClass: Implementation }
{ provide: Token, useValue: staticValue }
{ provide: Token, useFactory: factoryFn }
{ provide: Token, useExisting: OtherService }
{ provide: Token, useValue: value, multi: true }
```

---

## Summary

Angular's Dependency Injection system is:
- **Hierarchical** - Platform → Root → Route → Element injectors
- **Tree-shakable** - With `providedIn` option
- **Flexible** - Multiple provider types for different use cases
- **Testable** - Easy to mock and replace dependencies
- **Modern** - `inject()` function is the preferred approach

Master these concepts and you'll demonstrate strong Angular knowledge in any interview!
