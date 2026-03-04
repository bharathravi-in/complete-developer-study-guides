# Day 16: Performance - Interview Questions & Answers

## Basic Level

### Q1: What are the main areas of Angular performance optimization?

**Answer:**

```
┌─────────────────────────────────────────────────────────────────────┐
│               Performance Optimization Categories                    │
├──────────────────────┬──────────────────────────────────────────────┤
│ Category             │ Techniques                                    │
├──────────────────────┼──────────────────────────────────────────────┤
│ Initial Load         │ Lazy loading, code splitting, preloading     │
│                      │ @defer, bundle optimization                   │
├──────────────────────┼──────────────────────────────────────────────┤
│ Runtime              │ OnPush, trackBy, virtual scrolling           │
│                      │ memoization, signals                          │
├──────────────────────┼──────────────────────────────────────────────┤
│ Bundle Size          │ Tree shaking, direct imports                  │
│                      │ avoid barrel misuse                           │
├──────────────────────┼──────────────────────────────────────────────┤
│ Memory               │ Unsubscribe, async pipe                       │
│                      │ proper cleanup                                │
├──────────────────────┼──────────────────────────────────────────────┤
│ Rendering            │ Image optimization, lazy images               │
│                      │ CSS containment                               │
└──────────────────────┴──────────────────────────────────────────────┘
```

---

### Q2: What is lazy loading and how do you implement it?

**Answer:**
Lazy loading defers loading of modules/components until they're needed, reducing initial bundle size.

```typescript
// Route-based lazy loading
export const routes: Routes = [
  { path: '', component: HomeComponent },  // Eager
  { 
    path: 'admin',
    loadComponent: () => import('./admin/admin.component')
      .then(m => m.AdminComponent)  // Lazy
  },
  {
    path: 'products',
    loadChildren: () => import('./products/products.routes')
      .then(m => m.PRODUCT_ROUTES)  // Lazy routes
  }
];

// Component-level with @defer
@Component({
  template: `
    @defer (on viewport) {
      <app-heavy-component />
    } @placeholder {
      <div>Loading...</div>
    }
  `
})
export class PageComponent {}
```

**Benefits:**
- Smaller initial bundle
- Faster first load
- Load only what's needed

---

### Q3: What is trackBy and why is it important?

**Answer:**
`trackBy` helps Angular identify which items in a list have changed, preventing unnecessary DOM recreation.

```typescript
// Without trackBy: Angular recreates ALL items when list changes
@Component({
  template: `
    <div *ngFor="let item of items">{{ item.name }}</div>
  `
})

// With trackBy: Angular only updates changed items
@Component({
  template: `
    <!-- Modern syntax -->
    @for (item of items; track item.id) {
      <div>{{ item.name }}</div>
    }
    
    <!-- Legacy syntax -->
    <div *ngFor="let item of items; trackBy: trackById">
      {{ item.name }}
    </div>
  `
})
export class ListComponent {
  trackById(index: number, item: Item): number {
    return item.id;
  }
}
```

**Performance impact:**
```
List: [A, B, C] → [A, B, C, D]

Without trackBy:
  - Destroy A, B, C DOM elements
  - Create A, B, C, D DOM elements
  - Total: 7 DOM operations

With trackBy (tracking by id):
  - Keep A, B, C DOM elements
  - Create D DOM element
  - Total: 1 DOM operation
```

---

### Q4: How does OnPush strategy improve performance?

**Answer:**
OnPush skips change detection for a component unless specific conditions are met:

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<p>{{ data }}</p>`
})
export class OptimizedComponent {
  @Input() data!: string;
}
```

**OnPush triggers CD when:**
1. Input reference changes
2. DOM event originates in component
3. Async pipe emits
4. Manually triggered (markForCheck/detectChanges)

**Performance benefit:**
```
App with 100 components using Default:
- Every async event checks ALL 100 components

App with 100 components using OnPush:
- Only affected components are checked
- Could check just 1-5 components
```

---

## Intermediate Level

### Q5: Explain the @defer feature and its triggers.

**Answer:**
`@defer` delays rendering of template blocks until certain conditions are met.

```typescript
@Component({
  template: `
    <!-- Load when element enters viewport -->
    @defer (on viewport) {
      <app-chart />
    }

    <!-- Load on user interaction -->
    @defer (on interaction) {
      <app-comments />
    } @placeholder {
      <button>Load Comments</button>
    }

    <!-- Load after delay -->
    @defer (on timer(3000ms)) {
      <app-recommendations />
    }

    <!-- Prefetch for faster loading -->
    @defer (on viewport; prefetch on idle) {
      <app-related-products />
    }

    <!-- Multiple conditions -->
    @defer (when isLoggedIn; on viewport) {
      <app-personalized-content />
    } @loading (minimum 200ms) {
      <app-skeleton />
    } @error {
      <p>Failed to load</p>
    }
  `
})
```

**Available triggers:**
| Trigger | Description |
|---------|-------------|
| on viewport | Element enters visible area |
| on interaction | Click, focus, or other interaction |
| on hover | Mouse hovers over placeholder |
| on idle | Browser is idle |
| on immediate | Load in background immediately |
| on timer(Xms) | After specified delay |
| when condition | When expression becomes truthy |

---

### Q6: How do you implement virtual scrolling?

**Answer:**
Virtual scrolling renders only visible items, crucial for large lists.

```typescript
import { ScrollingModule } from '@angular/cdk/scrolling';

@Component({
  standalone: true,
  imports: [ScrollingModule],
  template: `
    <cdk-virtual-scroll-viewport 
      itemSize="50"
      class="viewport"
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
    .viewport { height: 500px; }
    .item { height: 50px; }
  `]
})
export class VirtualListComponent {
  // 10,000 items but only ~15 rendered at a time
  items = Array.from({ length: 10000 }, (_, i) => ({
    id: i,
    name: `Item ${i}`
  }));

  trackById = (i: number, item: any) => item.id;
}
```

**Performance comparison:**
```
Regular list with 10,000 items:
- 10,000 DOM elements
- Slow scroll, high memory

Virtual scroll with 10,000 items:
- ~20 DOM elements (visible + buffer)
- Smooth scroll, low memory
```

---

### Q7: How do you optimize bundle size?

**Answer:**

**1. Direct imports (avoid barrels):**
```typescript
// ❌ BAD - pulls in everything
import { Component } from './shared';

// ✓ GOOD - only what's needed
import { Component } from './shared/component';
```

**2. Tree-shakeable imports:**
```typescript
// ❌ BAD - entire lodash
import _ from 'lodash';

// ✓ GOOD - only used function
import debounce from 'lodash-es/debounce';
```

**3. Analyze bundle:**
```bash
# Generate stats
ng build --stats-json

# Analyze
npx webpack-bundle-analyzer dist/stats.json
```

**4. Use standalone components:**
```typescript
// Smaller than NgModules, better tree shaking
@Component({
  standalone: true,
  imports: [OnlyWhatYouNeed]
})
```

**5. Lazy load routes:**
```typescript
{
  path: 'admin',
  loadComponent: () => import('./admin.component')
}
```

---

### Q8: How do you prevent memory leaks in Angular?

**Answer:**

**1. takeUntilDestroyed (Angular 16+):**
```typescript
@Component({...})
export class ModernComponent {
  constructor() {
    this.service.data$
      .pipe(takeUntilDestroyed())
      .subscribe(data => this.handle(data));
  }
}
```

**2. Async pipe (auto-unsubscribes):**
```typescript
@Component({
  template: `{{ data$ | async }}`
})
export class SafeComponent {
  data$ = this.service.data$;
}
```

**3. Manual cleanup with Subject:**
```typescript
@Component({...})
export class ManualComponent implements OnDestroy {
  private destroy$ = new Subject<void>();

  ngOnInit() {
    this.service.data$
      .pipe(takeUntil(this.destroy$))
      .subscribe();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

**4. DestroyRef (Angular 16+):**
```typescript
@Component({...})
export class RefComponent {
  private destroyRef = inject(DestroyRef);

  ngOnInit() {
    const sub = this.service.data$.subscribe();
    this.destroyRef.onDestroy(() => sub.unsubscribe());
  }
}
```

---

## Advanced Level

### Q9: How would you optimize a dashboard with real-time data?

**Answer:**

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="dashboard">
      @for (widget of widgets; track widget.id) {
        @defer (on viewport) {
          <app-widget 
            [data]="widget.data$ | async"
            [config]="widget.config"
          />
        } @placeholder {
          <app-widget-skeleton />
        }
      }
    </div>
  `
})
export class DashboardComponent {
  // Use signals for config
  widgets = signal<Widget[]>([]);
  
  private ngZone = inject(NgZone);
  private cdr = inject(ChangeDetectorRef);

  connectRealtime() {
    // Handle high-frequency updates outside zone
    this.ngZone.runOutsideAngular(() => {
      const ws = new WebSocket('wss://api/realtime');
      
      let buffer: Update[] = [];
      let scheduled = false;
      
      ws.onmessage = (event) => {
        buffer.push(JSON.parse(event.data));
        
        // Batch updates at 60fps
        if (!scheduled) {
          scheduled = true;
          requestAnimationFrame(() => {
            this.ngZone.run(() => {
              this.applyUpdates(buffer);
              buffer = [];
              scheduled = false;
            });
          });
        }
      };
    });
  }
}
```

**Key optimizations:**
1. OnPush change detection
2. @defer for viewport-based loading
3. Outside zone for WebSocket
4. Batch updates with requestAnimationFrame
5. trackBy for list items

---

### Q10: How do you measure and monitor Angular performance?

**Answer:**

**1. Angular DevTools:**
- Profile change detection cycles
- Inspect component tree
- View execution time

**2. Chrome DevTools Performance:**
```typescript
// Manual performance marks
performance.mark('render-start');
// ... render logic
performance.mark('render-end');
performance.measure('render', 'render-start', 'render-end');
```

**3. Custom performance tracking:**
```typescript
@Injectable({ providedIn: 'root' })
export class PerformanceService {
  measureRender(componentName: string) {
    const startMark = `${componentName}-start`;
    const endMark = `${componentName}-end`;
    
    return {
      start: () => performance.mark(startMark),
      end: () => {
        performance.mark(endMark);
        const measure = performance.measure(
          componentName, startMark, endMark
        );
        console.log(`${componentName}: ${measure.duration}ms`);
        
        // Send to analytics if too slow
        if (measure.duration > 100) {
          this.reportSlowRender(componentName, measure.duration);
        }
      }
    };
  }
}
```

**4. Web Vitals monitoring:**
```typescript
import { onLCP, onFID, onCLS } from 'web-vitals';

onLCP(console.log);  // Largest Contentful Paint
onFID(console.log);  // First Input Delay
onCLS(console.log);  // Cumulative Layout Shift
```

---

### Q11: How do you optimize forms with many fields?

**Answer:**

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <form [formGroup]="form">
      <!-- Split into sections with @defer -->
      <section>
        <h3>Personal Info</h3>
        @for (field of personalFields; track field.name) {
          <app-form-field 
            [control]="form.get(field.name)"
            [config]="field"
          />
        }
      </section>

      @defer (on viewport) {
        <section>
          <h3>Additional Info</h3>
          @for (field of additionalFields; track field.name) {
            <app-form-field 
              [control]="form.get(field.name)"
              [config]="field"
            />
          }
        </section>
      }
    </form>
  `
})
export class LargeFormComponent {
  form = this.fb.group({
    // Fields...
  }, { updateOn: 'blur' });  // Validate on blur, not every keystroke
}

// Optimized form field component
@Component({
  selector: 'app-form-field',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <label>{{ config.label }}</label>
    <input [formControl]="control">
    @if (control.invalid && control.touched) {
      <span class="error">{{ getError() }}</span>
    }
  `
})
export class FormFieldComponent {
  @Input() control!: FormControl;
  @Input() config!: FieldConfig;
}
```

**Optimizations:**
1. `updateOn: 'blur'` - reduces validation frequency
2. OnPush on all form components
3. @defer for below-fold sections
4. trackBy for field iteration

---

### Q12: Explain image optimization in Angular.

**Answer:**

**Using NgOptimizedImage:**
```typescript
import { NgOptimizedImage, provideImgixLoader } from '@angular/common';

// Configure loader in app.config.ts
export const appConfig = {
  providers: [
    provideImgixLoader('https://mysite.imgix.net/')
  ]
};

@Component({
  imports: [NgOptimizedImage],
  template: `
    <!-- Priority image (LCP) -->
    <img 
      ngSrc="hero.jpg"
      width="1200"
      height="600"
      priority
    />

    <!-- Lazy loaded image -->
    <img 
      ngSrc="product.jpg"
      width="400"
      height="300"
      loading="lazy"
      placeholder="blur"
    />

    <!-- Responsive image -->
    <img
      ngSrc="banner.jpg"
      fill
      sizes="(max-width: 768px) 100vw, 50vw"
    />
  `
})
```

**Benefits of NgOptimizedImage:**
1. Automatic lazy loading
2. Priority hints for LCP images
3. Automatic srcset generation
4. Width/height enforcement (prevents CLS)
5. Preconnect hints

---

## Scenario Questions

### Q13: Application is slow after fetching 5000 records - how to fix?

**Answer:**

**Immediate fixes:**
```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <!-- Virtual scrolling for large lists -->
    <cdk-virtual-scroll-viewport itemSize="50" class="list">
      <div *cdkVirtualFor="let item of items; trackBy: trackById">
        <app-item [item]="item" />
      </div>
    </cdk-virtual-scroll-viewport>
  `
})
export class ListComponent {
  items = signal<Item[]>([]);
  trackById = (i: number, item: Item) => item.id;
}

// OnPush item component
@Component({
  selector: 'app-item',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ItemComponent {
  @Input() item!: Item;
}
```

**Backend improvements:**
- Implement pagination (50-100 items per page)
- Add server-side filtering
- Use cursor-based pagination for real-time data

**Additional optimizations:**
- Debounce search input
- Cache API responses
- Load data in chunks

---

## Quick Reference

```
Performance Optimization Checklist:
───────────────────────────────────
☐ OnPush on all components
☐ trackBy in all loops
☐ Lazy load routes
☐ @defer for heavy components
☐ Virtual scroll for long lists
☐ Unsubscribe from observables
☐ Use async pipe
☐ Direct imports (no barrels)
☐ NgOptimizedImage for images
☐ Analyze bundle size regularly
☐ Profile with Angular DevTools

Key Metrics:
────────────
LCP  < 2.5s  (Largest Contentful Paint)
FID  < 100ms (First Input Delay)
CLS  < 0.1   (Cumulative Layout Shift)
INP  < 200ms (Interaction to Next Paint)
```
