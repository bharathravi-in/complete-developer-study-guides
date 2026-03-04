# CLI Commands Cheatsheet

## Project Creation

```bash
# Create new project
ng new my-app
ng new my-app --standalone --routing --style=scss

# Create with specific options
ng new my-app --routing              # Add routing
ng new my-app --style=scss          # Use SCSS
ng new my-app --prefix=app          # Component prefix
ng new my-app --strict              # Strict mode
ng new my-app --skip-tests          # No test files
ng new my-app --skip-git            # No git init
ng new my-app --package-manager=npm # Specify package manager

# Create workspace without app
ng new my-workspace --create-application=false
```

## Generate Commands

```bash
# Component
ng g c components/button
ng g c features/user/user-list --standalone
ng g c shared/card --skip-tests
ng g c header --inline-template --inline-style  # -t -s
ng g c modal --change-detection=OnPush

# Service
ng g s services/user
ng g s core/auth --skip-tests

# Directive
ng g d directives/highlight
ng g d directives/focus --standalone

# Pipe
ng g p pipes/truncate
ng g p pipes/currency --standalone

# Guard
ng g guard guards/auth
ng g guard guards/auth --functional  # Function-based

# Interceptor
ng g interceptor interceptors/auth

# Interface/Model
ng g interface models/user
ng g class models/user

# Enum
ng g enum enums/status

# Module (if not using standalone)
ng g m features/user --routing

# Library (in workspace)
ng g lib shared-ui

# Resolver
ng g resolver resolvers/user

# Environment
ng g environments
```

### Generate Options

```bash
--dry-run, -d          # Preview changes without creating files
--skip-tests           # Don't create test file
--standalone           # Create standalone component
--flat                 # Don't create folder
--export               # Export from module
--inline-template, -t  # Template in .ts file
--inline-style, -s     # Styles in .ts file
--prefix               # Custom selector prefix
--change-detection     # OnPush or Default
--view-encapsulation   # None, Emulated, ShadowDom
```

## Serve & Build

```bash
# Development server
ng serve
ng serve --port 4300
ng serve --open                    # Open browser
ng serve --host 0.0.0.0           # External access
ng serve --proxy-config proxy.conf.json
ng serve --ssl                     # HTTPS

# Build
ng build
ng build --configuration=production  # Or just ng build
ng build --configuration=development
ng build --watch                   # Watch mode
ng build --source-map             # Include source maps
ng build --stats-json             # Generate stats.json
ng build --output-hashing=none    # Disable hash in filenames

# Analyze bundle
ng build --stats-json
npx webpack-bundle-analyzer dist/my-app/stats.json
```

## Testing

```bash
# Unit tests
ng test
ng test --watch=false             # Single run
ng test --code-coverage           # With coverage
ng test --browsers=ChromeHeadless # Headless
ng test --include=**/user*.spec.ts  # Specific files
ng test --karma-config=karma.conf.js

# E2E tests
ng e2e
ng e2e --configuration=production
```

## Linting & Formatting

```bash
# Lint
ng lint
ng lint --fix                     # Auto-fix issues

# Add eslint (if not present)
ng add @angular-eslint/schematics
```

## Add Libraries

```bash
# Angular Material
ng add @angular/material

# PWA support
ng add @angular/pwa

# SSR
ng add @angular/ssr

# Nx
npx nx@latest init

# Third-party
ng add @ngrx/store
ng add @ngrx/effects
ng add @ngrx/signals
```

## Update

```bash
# Check for updates
ng update

# Update Angular
ng update @angular/core @angular/cli

# Update specific package
ng update @angular/material

# Update with migrate
ng update @angular/core --migrate-only --from=15 --to=16
```

## Configuration

```bash
# Global CLI settings
ng config cli.packageManager npm
ng config cli.analytics false

# Project settings
ng config projects.my-app.architect.build.options.sourceMap true

# View config
ng config
```

## Environment Commands

```bash
# Generate environments
ng g environments

# Creates:
# - src/environments/environment.ts
# - src/environments/environment.development.ts

# Build for specific environment
ng build --configuration=production
ng build --configuration=development
```

## Cache

```bash
# Clear Angular cache
ng cache clean

# Disable cache
ng cache disable

# Enable cache
ng cache enable

# Cache info
ng cache info
```

## CI/CD Commands

```bash
# Production build
ng build --configuration=production

# Run tests once (CI)
ng test --watch=false --browsers=ChromeHeadless --code-coverage

# Lint
ng lint

# Combined CI script
npm run build && npm run test:ci && npm run lint
```

## Workspace Commands (Nx)

```bash
# Create Nx workspace
npx create-nx-workspace@latest my-org --preset=angular-standalone

# Generate app
nx g @nx/angular:application admin

# Generate library
nx g @nx/angular:library ui --directory=libs/shared

# Run multiple projects
nx run-many --target=build --all
nx run-many --target=test --projects=app1,lib1

# Affected commands
nx affected:build
nx affected:test
nx affected:lint

# Dependency graph
nx graph
```

## Useful Scripts (package.json)

```json
{
  "scripts": {
    "start": "ng serve",
    "build": "ng build",
    "build:prod": "ng build --configuration=production",
    "test": "ng test",
    "test:ci": "ng test --watch=false --browsers=ChromeHeadless --code-coverage",
    "test:coverage": "ng test --code-coverage",
    "lint": "ng lint",
    "lint:fix": "ng lint --fix",
    "analyze": "ng build --stats-json && npx webpack-bundle-analyzer dist/my-app/stats.json",
    "e2e": "ng e2e"
  }
}
```

## Shorthand Commands

| Full | Short |
|------|-------|
| `ng generate component` | `ng g c` |
| `ng generate service` | `ng g s` |
| `ng generate directive` | `ng g d` |
| `ng generate pipe` | `ng g p` |
| `ng generate guard` | `ng g guard` |
| `ng generate module` | `ng g m` |
| `ng generate interface` | `ng g i` |
| `ng generate class` | `ng g cl` |
| `ng generate enum` | `ng g e` |
| `--dry-run` | `-d` |
| `--inline-template` | `-t` |
| `--inline-style` | `-s` |
