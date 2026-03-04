# Day 1-2: Angular Architecture Basics

## Table of Contents
1. [What is Angular?](#1-what-is-angular)
2. [SPA vs MPA](#2-spa-vs-mpa)
3. [Angular CLI](#3-angular-cli)
4. [Project Structure](#4-project-structure)
5. [Bootstrapping Process](#5-bootstrapping-process)
6. [Standalone Components vs NgModules](#6-standalone-components-vs-ngmodules)

---

## 1. What is Angular?

Angular is a **TypeScript-based, open-source web application framework** developed by Google. It's a complete rewrite of AngularJS (Angular 1.x) and is designed for building dynamic, single-page applications (SPAs).

### Key Features of Angular 22:
- **Standalone Components** (default since Angular 17)
- **Signals** for reactive state management
- **Zoneless Change Detection** (experimental)
- **Control Flow Syntax** (@if, @for, @switch)
- **Deferrable Views** (@defer)
- **Improved SSR & Hydration**
- **Built-in Image Optimization**

### Angular vs Other Frameworks

| Feature | Angular | React | Vue |
|---------|---------|-------|-----|
| Type | Full Framework | Library | Framework |
| Language | TypeScript | JavaScript/JSX | JavaScript |
| Data Binding | Two-way | One-way | Two-way |
| State Management | Built-in (Signals) | External (Redux) | Vuex/Pinia |
| Learning Curve | Steep | Moderate | Easy |
| Best For | Enterprise Apps | Flexible Projects | Progressive Enhancement |

---

## 2. SPA vs MPA

### Single Page Application (SPA)

A web application that loads a single HTML page and dynamically updates content without full page reloads.

```
┌─────────────────────────────────────────────────────────────┐
│                         BROWSER                              │
├─────────────────────────────────────────────────────────────┤
│  Initial Load: index.html + app.js (Angular bundle)         │
│                                                              │
│  User Navigation:                                            │
│  ┌──────────┐    AJAX/Fetch    ┌──────────┐                 │
│  │  /home   │ ───────────────► │  Server  │ ──► JSON Data   │
│  └──────────┘   (No reload)    └──────────┘                 │
│                                                              │
│  Angular Router handles URL changes client-side              │
└─────────────────────────────────────────────────────────────┘
```

**Advantages:**
- Fast navigation (no full page reload)
- Better user experience
- Reduced server load
- Offline capability with Service Workers

**Disadvantages:**
- Initial load time is higher
- SEO challenges (mitigated by SSR)
- JavaScript dependency

### Multi Page Application (MPA)

Traditional web apps where each page request loads a new HTML document from the server.

```
┌─────────────────────────────────────────────────────────────┐
│                         BROWSER                              │
├─────────────────────────────────────────────────────────────┤
│  Page Request: /home                                         │
│  ┌──────────┐    Full Request   ┌──────────┐                │
│  │  /home   │ ───────────────► │  Server  │ ──► home.html   │
│  └──────────┘                   └──────────┘                 │
│                                                              │
│  Page Request: /about                                        │
│  ┌──────────┐    Full Request   ┌──────────┐                │
│  │  /about  │ ───────────────► │  Server  │ ──► about.html  │
│  └──────────┘   (Full reload)   └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### Interview Tip 💡
> "I choose SPA when the application requires rich interactivity, complex state management, and desktop-like user experience. MPA is preferred for content-heavy sites with SEO requirements, or when JavaScript dependency is a concern."

---

## 3. Angular CLI

The Angular CLI is a command-line interface tool for initializing, developing, scaffolding, and maintaining Angular applications.

### Installation

```bash
# Install Angular CLI globally
npm install -g @angular/cli

# Check version
ng version

# Create new project (Angular 22 defaults to standalone)
ng new my-app

# Create with specific options
ng new my-app --routing --style=scss --standalone
```

### Essential Commands

```bash
# Development
ng serve                    # Start dev server (http://localhost:4200)
ng serve --port 4300        # Custom port
ng serve --open             # Opens browser automatically

# Generate components, services, etc.
ng generate component home             # or ng g c home
ng generate service data              # or ng g s data
ng generate directive highlight       # or ng g d highlight
ng generate pipe format              # or ng g p format
ng generate guard auth               # or ng g g auth
ng generate interceptor auth         # or ng g interceptor auth

# Build
ng build                    # Development build
ng build --configuration=production  # Production build (optimized)

# Testing
ng test                     # Unit tests with Karma
ng e2e                      # End-to-end tests

# Linting & Analysis
ng lint                     # Lint code
ng analytics                # Configure analytics
```

### Angular CLI Configuration (angular.json)

```json
{
  "$schema": "./node_modules/@angular/cli/lib/config/schema.json",
  "version": 1,
  "newProjectRoot": "projects",
  "projects": {
    "my-app": {
      "projectType": "application",
      "root": "",
      "sourceRoot": "src",
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:application",
          "options": {
            "outputPath": "dist/my-app",
            "index": "src/index.html",
            "browser": "src/main.ts",
            "polyfills": ["zone.js"],
            "tsConfig": "tsconfig.app.json",
            "assets": ["src/favicon.ico", "src/assets"],
            "styles": ["src/styles.scss"],
            "scripts": []
          },
          "configurations": {
            "production": {
              "budgets": [
                {
                  "type": "initial",
                  "maximumWarning": "500kb",
                  "maximumError": "1mb"
                }
              ],
              "outputHashing": "all"
            },
            "development": {
              "optimization": false,
              "extractLicenses": false,
              "sourceMap": true
            }
          }
        }
      }
    }
  }
}
```

---

## 4. Project Structure

### Angular 22 Standalone Project Structure

```
my-app/
├── node_modules/           # Dependencies
├── src/
│   ├── app/
│   │   ├── components/     # Reusable components
│   │   │   └── header/
│   │   │       ├── header.component.ts
│   │   │       ├── header.component.html
│   │   │       ├── header.component.scss
│   │   │       └── header.component.spec.ts
│   │   │
│   │   ├── pages/          # Route-level components
│   │   │   ├── home/
│   │   │   └── about/
│   │   │
│   │   ├── services/       # Business logic & data
│   │   │   └── data.service.ts
│   │   │
│   │   ├── guards/         # Route guards
│   │   │   └── auth.guard.ts
│   │   │
│   │   ├── interceptors/   # HTTP interceptors
│   │   │   └── auth.interceptor.ts
│   │   │
│   │   ├── models/         # TypeScript interfaces
│   │   │   └── user.model.ts
│   │   │
│   │   ├── pipes/          # Custom pipes
│   │   │   └── format.pipe.ts
│   │   │
│   │   ├── directives/     # Custom directives
│   │   │   └── highlight.directive.ts
│   │   │
│   │   ├── app.component.ts
│   │   ├── app.component.html
│   │   ├── app.component.scss
│   │   ├── app.config.ts   # Application configuration
│   │   └── app.routes.ts   # Route definitions
│   │
│   ├── assets/             # Static files (images, fonts)
│   ├── environments/       # Environment configs
│   │   ├── environment.ts
│   │   └── environment.prod.ts
│   │
│   ├── index.html          # Main HTML file
│   ├── main.ts             # Entry point
│   └── styles.scss         # Global styles
│
├── angular.json            # CLI configuration
├── package.json            # Dependencies & scripts
├── tsconfig.json           # TypeScript config
└── README.md
```

### Feature-Based Structure (Enterprise)

```
src/app/
├── core/                    # Singleton services, guards
│   ├── services/
│   │   ├── auth.service.ts
│   │   └── api.service.ts
│   ├── guards/
│   ├── interceptors/
│   └── core.config.ts
│
├── shared/                  # Reusable components, pipes, directives
│   ├── components/
│   │   ├── button/
│   │   └── modal/
│   ├── pipes/
│   ├── directives/
│   └── shared.module.ts    # If using NgModules
│
├── features/               # Feature modules (lazy loaded)
│   ├── users/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── users.routes.ts
│   │
│   ├── products/
│   └── orders/
│
├── app.component.ts
├── app.config.ts
└── app.routes.ts
```

---

## 5. Bootstrapping Process

Understanding how Angular starts is crucial for interviews. Here's the complete flow:

### Angular 22 Bootstrapping (Standalone)

```
┌──────────────────────────────────────────────────────────────────┐
│                    Angular Bootstrapping Flow                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. index.html loads                                              │
│        │                                                          │
│        ▼                                                          │
│  2. Browser loads main.ts (entry point)                           │
│        │                                                          │
│        ▼                                                          │
│  3. bootstrapApplication() is called                              │
│        │                                                          │
│        ▼                                                          │
│  4. ApplicationConfig loads providers                             │
│        │                                                          │
│        ▼                                                          │
│  5. Angular creates the root injector                             │
│        │                                                          │
│        ▼                                                          │
│  6. Root component (AppComponent) is instantiated                 │
│        │                                                          │
│        ▼                                                          │
│  7. Component tree is rendered                                    │
│        │                                                          │
│        ▼                                                          │
│  8. Change detection runs                                         │
│        │                                                          │
│        ▼                                                          │
│  9. Application is ready                                          │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### main.ts (Entry Point)

```typescript
// main.ts - Angular 22 Standalone Bootstrapping
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { appConfig } from './app/app.config';

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
```

### app.config.ts (Application Configuration)

```typescript
// app.config.ts
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

import { routes } from './app.routes';
import { authInterceptor } from './interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    // Zone.js change detection (default)
    provideZoneChangeDetection({ eventCoalescing: true }),
    
    // Router with component input binding
    provideRouter(routes, withComponentInputBinding()),
    
    // HTTP client with interceptors
    provideHttpClient(withInterceptors([authInterceptor])),
    
    // Animations
    provideAnimationsAsync()
  ]
};
```

### app.routes.ts (Routes Configuration)

```typescript
// app.routes.ts
import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'home',
    pathMatch: 'full'
  },
  {
    path: 'home',
    loadComponent: () => import('./pages/home/home.component')
      .then(m => m.HomeComponent)
  },
  {
    path: 'users',
    loadChildren: () => import('./features/users/users.routes')
      .then(m => m.USERS_ROUTES)
  },
  {
    path: '**',
    loadComponent: () => import('./pages/not-found/not-found.component')
      .then(m => m.NotFoundComponent)
  }
];
```

### index.html

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>MyApp</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/x-icon" href="favicon.ico">
</head>
<body>
  <!-- Root component selector -->
  <app-root></app-root>
</body>
</html>
```

### Interview Deep Dive: What happens internally?

1. **Browser requests `index.html`**
2. **Scripts load** - Webpack bundles are loaded
3. **`main.ts` executes** - Entry point runs
4. **`bootstrapApplication()` called** with root component and config
5. **Platform created** - `PlatformRef` initializes Angular runtime
6. **Application created** - `ApplicationRef` manages the app
7. **Root injector created** - Dependency injection tree starts
8. **Root component instantiated** - `AppComponent` created
9. **Component compiled** - Template parsed, metadata processed
10. **View created** - DOM nodes generated
11. **Change detection** - Initial check runs
12. **Application stable** - Ready for user interaction

---

## 6. Standalone Components vs NgModules

### Evolution Timeline

```
Angular 2-13:     NgModules (required)
Angular 14:       Standalone (opt-in)
Angular 17+:      Standalone (default)
Angular 22:       Standalone (recommended, NgModules still supported)
```

### NgModule Approach (Legacy)

```typescript
// app.module.ts
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { ReactiveFormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { HeaderComponent } from './components/header.component';
import { UserService } from './services/user.service';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    ReactiveFormsModule
  ],
  providers: [UserService],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

### Standalone Approach (Modern - Angular 22)

```typescript
// app.component.ts
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './components/header.component';

@Component({
  selector: 'app-root',
  standalone: true,  // Note: Default true in Angular 22
  imports: [RouterOutlet, HeaderComponent],
  template: `
    <app-header />
    <router-outlet />
  `
})
export class AppComponent { }
```

```typescript
// header.component.ts
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  template: `
    <header>
      <h1>My App</h1>
      <nav>
        <a routerLink="/home">Home</a>
        <a routerLink="/about">About</a>
      </nav>
    </header>
  `
})
export class HeaderComponent { }
```

### Comparison Table

| Aspect | NgModules | Standalone |
|--------|-----------|------------|
| Complexity | Higher (more boilerplate) | Lower (simpler) |
| Tree-shaking | Less efficient | Better (direct imports) |
| Lazy Loading | Module-level | Component-level |
| Migration | N/A | Can be gradual |
| Learning Curve | Higher | Lower |
| Dependency Declaration | In module | In component |

### Migrating from NgModules to Standalone

```bash
# Angular CLI migration schematic
ng generate @angular/core:standalone
```

### When to Use Each

**Use Standalone (Recommended):**
- New projects (Angular 17+)
- Micro frontends
- Better tree-shaking needed
- Component-level lazy loading

**Use NgModules:**
- Large existing codebases
- Team familiarity
- Complex shared module patterns
- Library development (sometimes)

---

## Summary

| Concept | Key Points |
|---------|------------|
| Angular | TypeScript framework, full-featured, enterprise-ready |
| SPA | Single load, client-side routing, better UX |
| CLI | Scaffolding, building, testing, deployment |
| Structure | Feature-based for enterprise, flat for small apps |
| Bootstrap | main.ts → bootstrapApplication() → AppComponent |
| Standalone | Modern default, simpler, better tree-shaking |

---

## Next Steps
- Proceed to Day 3: Components Deep Dive
- Practice creating a new Angular project
- Explore the generated project structure
