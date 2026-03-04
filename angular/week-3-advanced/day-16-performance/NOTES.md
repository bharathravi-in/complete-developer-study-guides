# Day 16: Performance Optimization in Angular

## Overview

Performance optimization in Angular involves reducing initial load time, improving runtime performance, and optimizing change detection.

---

## Performance Metrics

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Core Web Vitals                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  LCP (Largest Contentful Paint)     Target: < 2.5s                  │
│  └── How long until main content is visible                         │
│                                                                      │
│  FID (First Input Delay)            Target: < 100ms                 │
│  └── Time from user input to browser response                       │
│                                                                      │
│  CLS (Cumulative Layout Shift)      Target: < 0.1                   │
│  └── Visual stability (elements not jumping around)                 │
│                                                                      │
│  INP (Interaction to Next Paint)    Target: < 200ms                 │
│  └── Responsiveness throughout the session                          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Lazy Loading

### Route-Based Lazy Loading

```typescript
// app.routes.ts
export const routes: Routes = [
  { 
    path: '', 
    component: HomeComponent 
  },
  {
    path: 'admin',
    loadComponent: () => import('./admin/admin.component')
      .then(m => m.AdminComponent)
  },
  {
    path: 'products',
    loadChildren: () => import('./products/products.routes')
      .then(m => m.PRODUCT_ROUTES)
  }
];

// products/products.routes.ts
export const PRODUCT_ROUTES: Routes = [
  { path: '', component: ProductListComponent },
  { path: ':id', component: ProductDetailComponent }
];
```

### Preloading Strategies

```typescript
// app.config.ts
import { provideRouter, withPreloading, PreloadAllModules } from '@angular/router';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      withPreloading(PreloadAllModules)  // Preload after initial load
    )
  ]
};

// Custom preloading strategy
@Injectable({ providedIn: 'root' })
export class SelectivePreloadStrategy implements PreloadingStrategy {
  preload(route: Route, load: () => Observable<any>): Observable<any> {
    // Only preload routes marked with data.preload = true
    return route.data?.['preload'] ? load() : of(null);
  }
}

// Route with preload flag
{
  path: 'frequently-used',
  loadComponent: () => import('./frequent.component'),
  data: { preload: true }
}
```

### Component-Level Lazy Loading

```typescript
@Component({
  template: `
    @defer (on viewport) {
      <app-heavy-chart [data]="chartData" />
    } @placeholder {
      <div class="skeleton">Loading chart...</div>
    } @loading (minimum 500ms) {
      <app-spinner />
    } @error {
      <p>Failed to load chart</p>
    }
  `
})
export class DashboardComponent {
  chartData = signal<ChartData[]>([]);
}
```

### @defer Triggers

```typescript
// Trigger when element enters viewport
@defer (on viewport) { ... }

// Trigger on user interaction
@defer (on interaction) { ... }

// Trigger on hover
@defer (on hover) { ... }

// Trigger when idle (browser idle callback)
@defer (on idle) { ... }

// Trigger immediately (background load)
@defer (on immediate) { ... }

// Trigger after specific delay
@defer (on timer(2000ms)) { ... }

// Trigger based on condition
@defer (when isReady) { ... }

// Multiple conditions
@defer (on viewport; when shouldLoad) { ... }

// Prefetch for faster loading
@defer (on viewport; prefetch on idle) { ... }
```

---

## 2. OnPush Change Detection

```typescript
@Component({
  selector: 'app-user-card',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="card">
      <h3>{{ user().name }}</h3>
      <p>{{ user().email }}</p>
    </div>
  `
})
export class UserCardComponent {
  @Input({ required: true }) user!: Signal<User>;
}

// Parent component
@Component({
  template: `
    @for (user of users(); track user.id) {
      <app-user-card [user]="user" />
    }
  `
})
export class UserListComponent {
  users = signal<User[]>([]);
  
  updateUser(id: string, name: string) {
    // Create new reference for OnPush
    this.users.update(users =>
      users.map(u => u.id === id ? { ...u, name } : u)
    );
  }
}
```

---

## 3. TrackBy Function

```typescript
@Component({
  template: `
    <!-- Angular 17+ syntax with track -->
    @for (item of items(); track item.id) {
      <app-item [item]="item" />
    }

    <!-- Legacy syntax with ngFor -->
    <app-item 
      *ngFor="let item of items; trackBy: trackById" 
      [item]="item"
    />
  `
})
export class ListComponent {
  items = signal<Item[]>([]);

  // Legacy trackBy function
  trackById(index: number, item: Item): number {
    return item.id;
  }
}
```

**Why trackBy matters:**
```
Without trackBy:                 With trackBy:
─────────────────                ─────────────
items = [a, b, c]               items = [a, b, c]
items = [a, b, c, d]            items = [a, b, c, d]

→ Re-render ALL items           → Only render new item 'd'
```

---

## 4. Virtual Scrolling

```typescript
import { ScrollingModule } from '@angular/cdk/scrolling';

@Component({
  selector: 'app-virtual-list',
  standalone: true,
  imports: [ScrollingModule],
  template: `
    <cdk-virtual-scroll-viewport 
      itemSize="50" 
      class="viewport"
      minBufferPx="200"
      maxBufferPx="400"
    >
      <div 
        *cdkVirtualFor="let item of items; trackBy: trackById"
        class="item"
      >
        {{ item.name }}
      </div>
    </cdk-virtual-scroll-viewport>
  `,
  styles: [`
    .viewport {
      height: 400px;
      width: 100%;
    }
    .item {
      height: 50px;
    }
  `]
})
export class VirtualListComponent {
  items: Item[] = Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    name: `Item ${i}`
  }));

  trackById(index: number, item: Item): number {
    return item.id;
  }
}
```

### Dynamic Item Size

```typescript
@Component({
  template: `
    <cdk-virtual-scroll-viewport
      [itemSize]="50"
      autosize
    >
      <div *cdkVirtualFor="let item of items">
        <!-- Variable height content -->
      </div>
    </cdk-virtual-scroll-viewport>
  `
})
export class DynamicHeightListComponent {}
```

---

## 5. Bundle Optimization

### Tree Shaking

```typescript
// ❌ BAD - imports entire lodash
import _ from 'lodash';
_.debounce(fn, 300);

// ✓ GOOD - imports only debounce
import debounce from 'lodash/debounce';
debounce(fn, 300);

// ✓ BETTER - use RxJS (already in Angular)
import { debounceTime } from 'rxjs/operators';
```

### Avoid Barrel File Issues

```typescript
// ❌ BAD - barrel file exports everything
// shared/index.ts
export * from './component-a';
export * from './component-b';
export * from './heavy-library';  // Always bundled!

// Usage pulls in everything
import { ComponentA } from './shared';

// ✓ GOOD - direct imports
import { ComponentA } from './shared/component-a';
```

### Analyze Bundle Size

```bash
# Build with stats
ng build --stats-json

# Analyze with webpack-bundle-analyzer
npx webpack-bundle-analyzer dist/*/stats.json

# Or use source-map-explorer
npm install source-map-explorer
ng build --source-map
npx source-map-explorer dist/**/main.*.js
```

---

## 6. Image Optimization

### NgOptimizedImage

```typescript
import { NgOptimizedImage } from '@angular/common';

@Component({
  standalone: true,
  imports: [NgOptimizedImage],
  template: `
    <!-- Automatically optimizes image loading -->
    <img
      ngSrc="hero.jpg"
      width="800"
      height="600"
      priority
      placeholder="data:image/svg+xml;base64,..."
    />

    <!-- Responsive image -->
    <img
      ngSrc="product.jpg"
      fill
      sizes="(max-width: 768px) 100vw, 50vw"
      [loaderParams]="{ quality: 80 }"
    />
  `
})
export class HeroComponent {}
```

### Image Loader Configuration

```typescript
// app.config.ts
import { provideImgixLoader, provideCloudinaryLoader } from '@angular/common';

export const appConfig: ApplicationConfig = {
  providers: [
    // For Imgix
    provideImgixLoader('https://my-site.imgix.net/'),
    
    // Or for Cloudinary
    provideCloudinaryLoader('https://res.cloudinary.com/my-account/')
  ]
};
```

---

## 7. Memory Leak Prevention

### Unsubscribe Patterns

```typescript
@Component({...})
export class LeakFreeComponent implements OnDestroy {
  private destroy$ = new Subject<void>();

  ngOnInit() {
    // Pattern 1: takeUntilDestroyed (Angular 16+)
    this.service.data$
      .pipe(takeUntilDestroyed())
      .subscribe(data => this.handleData(data));

    // Pattern 2: takeUntil with subject
    this.service.other$
      .pipe(takeUntil(this.destroy$))
      .subscribe(data => this.handleOther(data));
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}

// Pattern 3: Async pipe (preferred)
@Component({
  template: `
    @if (data$ | async; as data) {
      {{ data | json }}
    }
  `
})
export class AsyncComponent {
  data$ = this.service.data$;
  // Auto-unsubscribes!
}

// Pattern 4: DestroyRef (Angular 16+)
@Component({...})
export class ModernComponent {
  private destroyRef = inject(DestroyRef);

  ngOnInit() {
    const sub = this.service.data$.subscribe();
    this.destroyRef.onDestroy(() => sub.unsubscribe());
  }
}
```

---

## 8. Memoization

### Pure Pipes

```typescript
// Pure pipe (default) - only recalculates when input changes
@Pipe({ name: 'filterActive', pure: true })
export class FilterActivePipe implements PipeTransform {
  transform(items: Item[]): Item[] {
    return items.filter(i => i.active);
  }
}

// Usage - efficient with OnPush
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @for (item of items | filterActive; track item.id) {
      <app-item [item]="item" />
    }
  `
})
```

### Computed Signals

```typescript
@Component({...})
export class MemoizedComponent {
  items = signal<Item[]>([]);
  searchTerm = signal('');

  // Memoized - only recalculates when dependencies change
  filteredItems = computed(() => {
    const term = this.searchTerm().toLowerCase();
    return this.items().filter(i => 
      i.name.toLowerCase().includes(term)
    );
  });

  // Derived computation - also memoized
  itemCount = computed(() => this.filteredItems().length);
}
```

---

## 9. Web Workers

```typescript
// Generate worker
// ng generate web-worker heavy-calculation

// heavy-calculation.worker.ts
addEventListener('message', ({ data }) => {
  const result = heavyCalculation(data);
  postMessage(result);
});

function heavyCalculation(input: number[]): number {
  return input.reduce((sum, n) => sum + Math.pow(n, 2), 0);
}

// Component using worker
@Component({...})
export class CalculationComponent {
  private worker: Worker;
  result = signal<number | null>(null);

  constructor() {
    if (typeof Worker !== 'undefined') {
      this.worker = new Worker(
        new URL('./heavy-calculation.worker', import.meta.url)
      );
      
      this.worker.onmessage = ({ data }) => {
        this.result.set(data);
      };
    }
  }

  calculate(data: number[]) {
    this.worker.postMessage(data);
  }
}
```

---

## 10. SSR & Hydration

```typescript
// angular.json
{
  "projects": {
    "my-app": {
      "architect": {
        "build": {
          "options": {
            "prerender": true,
            "ssr": true
          }
        }
      }
    }
  }
}

// app.config.ts
import { provideClientHydration } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration()  // Enable hydration
  ]
};
```

---

## Performance Checklist

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Performance Optimization Checklist                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Initial Load                                                        │
│  ├── ☐ Lazy load routes                                             │
│  ├── ☐ Use @defer for heavy components                              │
│  ├── ☐ Enable production mode                                       │
│  ├── ☐ Enable compression (gzip/brotli)                             │
│  ├── ☐ Use preload strategies                                       │
│  └── ☐ Optimize images with ngSrc                                   │
│                                                                      │
│  Runtime                                                             │
│  ├── ☐ Use OnPush change detection                                  │
│  ├── ☐ Use trackBy in loops                                         │
│  ├── ☐ Virtual scrolling for long lists                             │
│  ├── ☐ Use pure pipes for transformations                           │
│  ├── ☐ Memoize with computed signals                                │
│  └── ☐ Run heavy work outside NgZone                                │
│                                                                      │
│  Memory                                                              │
│  ├── ☐ Unsubscribe from observables                                 │
│  ├── ☐ Use async pipe when possible                                 │
│  ├── ☐ Clean up event listeners                                     │
│  └── ☐ Use WeakMap/WeakSet for caches                               │
│                                                                      │
│  Bundle Size                                                         │
│  ├── ☐ Direct imports (avoid barrels)                               │
│  ├── ☐ Tree-shakeable imports                                       │
│  ├── ☐ Analyze bundle regularly                                     │
│  └── ☐ Use standalone components                                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Measuring Performance

```typescript
// Component-level timing
@Component({...})
export class TimedComponent implements OnInit, AfterViewInit {
  private startTime!: number;

  ngOnInit() {
    this.startTime = performance.now();
  }

  ngAfterViewInit() {
    const renderTime = performance.now() - this.startTime;
    console.log(`Component rendered in ${renderTime}ms`);
  }
}

// Using Performance API
const measure = (name: string, fn: () => void) => {
  performance.mark(`${name}-start`);
  fn();
  performance.mark(`${name}-end`);
  performance.measure(name, `${name}-start`, `${name}-end`);
  
  const entry = performance.getEntriesByName(name)[0];
  console.log(`${name}: ${entry.duration}ms`);
};
```

---

## Summary

| Technique | Impact | Effort | When to Use |
|-----------|--------|--------|-------------|
| Lazy Loading | High | Low | Always |
| OnPush | High | Medium | Always |
| Virtual Scroll | High | Low | Long lists (100+) |
| trackBy | Medium | Low | Always in loops |
| @defer | High | Low | Heavy components |
| Pure Pipes | Medium | Low | Data transformations |
| Signals | High | Medium | New projects |
| Web Workers | High | High | Heavy computations |
