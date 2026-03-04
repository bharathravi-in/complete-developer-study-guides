# Day 1-2: Interview Q&A – Angular Architecture Basics

## Q1: What is Angular and how does it differ from AngularJS?

**Answer:**
Angular is a TypeScript-based front-end framework developed by Google for building single-page applications. It's a complete rewrite of AngularJS with significant differences:

| Aspect | AngularJS (1.x) | Angular (2+) |
|--------|-----------------|--------------|
| Language | JavaScript | TypeScript |
| Architecture | MVC | Component-based |
| Data Binding | Two-way (scope) | One-way default, Two-way optional |
| Mobile Support | Limited | Built-in |
| Dependency Injection | String-based | Class-based |
| Performance | $digest cycle issues | Change detection optimized |

**Interview Tip:** Mention that Angular provides better performance through Ahead-of-Time (AOT) compilation, tree-shaking, and optimized change detection.

---

## Q2: Explain SPA vs MPA. When would you choose each?

**Answer:**
**SPA (Single Page Application):**
- Loads once, updates dynamically
- Client-side routing
- Better user experience with no page reloads
- Examples: Gmail, Google Maps

**MPA (Multi Page Application):**
- Each action loads a new page from server
- Server-side routing
- Traditional web architecture
- Better initial SEO

**When to choose:**
- **SPA:** Complex interactions, dashboard apps, when rich UX is priority
- **MPA:** Content-heavy sites, SEO-critical sites, when JavaScript dependency is a concern

---

## Q3: What is the Angular CLI and what are its key features?

**Answer:**
Angular CLI is a command-line interface for Angular development that provides:

1. **Project scaffolding:** `ng new app-name`
2. **Code generation:** `ng generate component/service/guard`
3. **Development server:** `ng serve` with hot reload
4. **Building:** `ng build` with optimization
5. **Testing:** `ng test` (unit), `ng e2e` (integration)
6. **Linting:** `ng lint`
7. **Updates:** `ng update` for dependency management

**Key configurations in angular.json:**
- Build options, budgets, assets
- Environment configurations
- Project structure settings

---

## Q4: Describe the Angular project structure. How would you organize a large-scale application?

**Answer:**
**Standard Structure:**
```
src/
├── app/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Route-level components
│   ├── services/       # Business logic
│   ├── guards/         # Route protection
│   ├── interceptors/   # HTTP middleware
│   ├── models/         # TypeScript interfaces
│   ├── pipes/          # Data transformation
│   ├── directives/     # DOM manipulation
│   ├── app.config.ts   # App configuration
│   └── app.routes.ts   # Routing
```

**Enterprise Feature-Based Structure:**
```
src/app/
├── core/              # Singletons (auth, API services)
├── shared/            # Reusable components, pipes, directives
├── features/          # Feature modules (lazy loaded)
│   ├── users/
│   ├── products/
│   └── orders/
```

**Key principles:**
- Core module for singleton services
- Shared module for reusable components
- Feature modules for business domains
- Lazy loading for performance

---

## Q5: Explain the Angular bootstrapping process. What happens when an Angular app starts?

**Answer:**
The bootstrapping process in Angular 22 (Standalone):

1. **Browser loads `index.html`**
2. **Main bundle loads and executes `main.ts`**
3. **`bootstrapApplication()` is called** with root component and config
4. **Platform is created** - Angular runtime initializes
5. **Application configuration loads** - Providers from `app.config.ts`
6. **Root injector created** - DI tree starts
7. **Root component instantiated** - `AppComponent` created
8. **Template compiled** - DOM nodes generated
9. **Change detection runs** - Initial UI update
10. **Application is stable** - Ready for interaction

```typescript
// main.ts
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';

bootstrapApplication(AppComponent, appConfig)
  .catch(err => console.error(err));
```

---

## Q6: What are Standalone Components? How do they differ from NgModules?

**Answer:**
**Standalone Components** (Angular 14+, default in Angular 17+):
- Self-contained components with their own imports
- No NgModule required
- Better tree-shaking
- Component-level lazy loading
- Simpler architecture

```typescript
@Component({
  selector: 'app-user',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `<h1>User Component</h1>`
})
export class UserComponent { }
```

**NgModules** (Traditional):
- Container for related components, directives, pipes
- Declare dependencies at module level
- Required in Angular 2-13

**Key Differences:**
| Aspect | Standalone | NgModules |
|--------|------------|-----------|
| Imports | Per component | Per module |
| Tree-shaking | Better | Less efficient |
| Lazy Loading | Component-level | Module-level |
| Boilerplate | Less | More |

---

## Q7: What is the `app.config.ts` file and what does it contain?

**Answer:**
`app.config.ts` is the application configuration file in standalone Angular apps. It contains providers and feature configurations.

```typescript
export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes, withComponentInputBinding()),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimationsAsync()
  ]
};
```

**Common providers:**
- `provideRouter()` - Routing configuration
- `provideHttpClient()` - HTTP client with interceptors
- `provideAnimationsAsync()` - Angular animations
- `provideZoneChangeDetection()` - Zone.js configuration

---

## Q8: How does Angular's dependency injection work at the application level?

**Answer:**
Angular creates a **hierarchical injector tree**:

1. **Platform Injector** - Shared across all apps
2. **Root Injector** - Created by `bootstrapApplication()`
3. **Component Injectors** - Created per component

**Provider registration:**
```typescript
// In app.config.ts (root level)
providers: [
  { provide: UserService, useClass: UserService }
]

// In component (component level)
@Component({
  providers: [UserService]  // New instance per component
})
```

**providedIn options:**
```typescript
@Injectable({
  providedIn: 'root'  // Singleton, tree-shakable
})
export class UserService { }
```

---

## Q9: What is the purpose of `provideRouter()` and its options?

**Answer:**
`provideRouter()` configures the Angular Router in standalone apps.

```typescript
provideRouter(
  routes,
  withComponentInputBinding(),     // Bind route params to inputs
  withPreloading(PreloadAllModules), // Preloading strategy
  withRouterConfig({
    onSameUrlNavigation: 'reload'
  }),
  withHashLocation(),              // Hash-based routing
  withInMemoryScrolling({
    scrollPositionRestoration: 'enabled'
  })
)
```

**Common features:**
- `withComponentInputBinding()` - Route params as @Input()
- `withPreloading()` - Lazy load strategies
- `withHashLocation()` - Hash URLs for older servers
- `withInMemoryScrolling()` - Scroll position management

---

## Q10: What are the benefits of using standalone components over NgModules?

**Answer:**

1. **Reduced Boilerplate**
   - No need for NgModule declarations
   - Direct imports in component

2. **Better Tree-Shaking**
   - Unused components are removed
   - Smaller bundle sizes

3. **Simpler Mental Model**
   - Dependencies declared where used
   - Easier to understand

4. **Component-Level Lazy Loading**
   ```typescript
   loadComponent: () => import('./user.component')
     .then(m => m.UserComponent)
   ```

5. **Easier Testing**
   - Less setup required
   - Direct component testing

6. **Gradual Migration**
   - Can mix with NgModules
   - No all-or-nothing approach

---

## Q11: How would you migrate an existing NgModule-based app to standalone?

**Answer:**

**Step 1: Use Angular schematic**
```bash
ng generate @angular/core:standalone
```

**Step 2: Manual migration steps:**

1. Mark components as standalone:
```typescript
@Component({
  standalone: true,
  imports: [CommonModule, ...],
  ...
})
```

2. Move imports from module to component

3. Update bootstrapping:
```typescript
// Before (NgModule)
platformBrowserDynamic().bootstrapModule(AppModule);

// After (Standalone)
bootstrapApplication(AppComponent, appConfig);
```

4. Convert routes to use `loadComponent` instead of `loadChildren`

**Migration Strategy:**
- Start with leaf components
- Work up to shared components
- Finally migrate root component
- Keep NgModules where complex patterns exist

---

## Q12: Explain the role of Zone.js in Angular bootstrapping.

**Answer:**
**Zone.js** is a library that patches async APIs to enable automatic change detection.

**How it works:**
1. Zone.js patches browser APIs (setTimeout, Promise, events)
2. When async operation completes, Zone notifies Angular
3. Angular runs change detection

**Bootstrapping with Zone.js:**
```typescript
// Default
provideZoneChangeDetection({ eventCoalescing: true })

// Event coalescing groups multiple events into single CD cycle
```

**Zoneless (Experimental in Angular 22):**
```typescript
provideExperimentalZonelessChangeDetection()
```

**Interview Tip:** Mention that Signals + Zoneless is the future direction for Angular, providing better performance and explicit change management.

---

## Quick Reference Card

| Topic | Key Point |
|-------|-----------|
| Angular | TypeScript framework, component-based |
| SPA | Single HTML load, client-side routing |
| CLI | Scaffolding & build tool |
| Structure | Feature-based for enterprise |
| Bootstrapping | main.ts → bootstrapApplication() |
| Standalone | Modern default, better tree-shaking |
| NgModules | Legacy, still supported |
| Zone.js | Async tracking for change detection |
