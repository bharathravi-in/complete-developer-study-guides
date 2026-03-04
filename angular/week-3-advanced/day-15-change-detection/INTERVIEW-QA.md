# Day 15: Change Detection - Interview Questions & Answers

## Basic Level

### Q1: What is Change Detection in Angular?

**Answer:**
Change Detection is Angular's mechanism to detect changes in component data and update the DOM accordingly. When the application state changes, Angular:

1. **Detects** the change (via Zone.js or manual triggers)
2. **Compares** current and previous values
3. **Updates** the DOM only where needed

```
┌─────────────────────────────────────────────────────────────┐
│                 Change Detection Cycle                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   State Change ──► Zone.js Notifies ──► Angular Runs CD     │
│                                              │               │
│                                              ▼               │
│                                    ┌─────────────────┐      │
│                                    │ Root Component  │      │
│                                    └────────┬────────┘      │
│                                             │               │
│                              ┌──────────────┼──────────────┐│
│                              ▼              ▼              ▼│
│                         ┌───────┐     ┌───────┐     ┌───────┐
│                         │Child A│     │Child B│     │Child C│
│                         └───────┘     └───────┘     └───────┘
│                                                              │
│   Direction: Top to Bottom (unidirectional)                 │
└─────────────────────────────────────────────────────────────┘
```

---

### Q2: What is Zone.js and why does Angular use it?

**Answer:**
Zone.js is a library that creates execution contexts (zones) and patches async browser APIs.

**Why Angular uses it:**
- Automatically detects when async operations complete
- Triggers change detection without manual calls
- Patches: `setTimeout`, `setInterval`, `Promise`, `addEventListener`, `XHR`, `fetch`

```typescript
// Without Zone.js, you'd need:
setTimeout(() => {
  this.data = 'updated';
  this.cdr.detectChanges();  // Manual trigger needed
}, 1000);

// With Zone.js, Angular handles it automatically:
setTimeout(() => {
  this.data = 'updated';
  // Zone.js notifies Angular, CD runs automatically
}, 1000);
```

---

### Q3: What are the Change Detection strategies in Angular?

**Answer:**

**1. Default (CheckAlways):**
- Checks component on every CD cycle
- Checks even if inputs haven't changed
- Safe but can be slow for large apps

**2. OnPush (CheckOnce):**
- Checks only when:
  - Input reference changes
  - DOM event occurs in component
  - Async pipe receives new value
  - Manually triggered

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class OptimizedComponent {
  @Input() data!: Data;  // Only checked when reference changes
}
```

**When to use OnPush:**
- Large lists
- Frequently updating parent components
- When using immutable data patterns
- When using observables with async pipe

---

### Q4: What is the difference between markForCheck() and detectChanges()?

**Answer:**

| Method | markForCheck() | detectChanges() |
|--------|----------------|-----------------|
| When runs | Next CD cycle | Immediately |
| Scope | Marks component + ancestors | This component + children |
| Use case | OnPush with external updates | Immediate update needed |
| Synchronous | No | Yes |

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ExampleComponent {
  private cdr = inject(ChangeDetectorRef);
  data: string = '';

  // External update (WebSocket, Service)
  onExternalUpdate(value: string) {
    this.data = value;
    
    // Option 1: Mark for next cycle (preferred)
    this.cdr.markForCheck();
    
    // Option 2: Update immediately
    // this.cdr.detectChanges();
  }
}
```

**Rule of thumb:**
- Use `markForCheck()` in most cases (safer, batched)
- Use `detectChanges()` when immediate update is critical

---

## Intermediate Level

### Q5: How does OnPush change detection work with Input bindings?

**Answer:**
OnPush checks inputs by **reference equality**, not deep comparison.

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @for (item of items; track item.id) {
      <span>{{ item.name }}</span>
    }
  `
})
export class ListComponent {
  @Input() items: Item[] = [];
}

// Parent component
@Component({
  template: `<app-list [items]="items" />`
})
export class ParentComponent {
  items: Item[] = [];

  // ❌ WON'T trigger OnPush - same reference
  addItemBad() {
    this.items.push({ id: 1, name: 'New' });
    // items array reference unchanged
  }

  // ✓ WILL trigger OnPush - new reference
  addItemGood() {
    this.items = [...this.items, { id: 1, name: 'New' }];
    // New array reference
  }
}
```

---

### Q6: How do you run code outside Angular's zone?

**Answer:**
Use `NgZone.runOutsideAngular()` for operations that shouldn't trigger change detection:

```typescript
@Component({...})
export class PerformanceComponent {
  private ngZone = inject(NgZone);

  initAnimation() {
    // Run outside zone - no CD triggered for each frame
    this.ngZone.runOutsideAngular(() => {
      const animate = () => {
        // Update canvas, do calculations
        this.updateCanvas();
        requestAnimationFrame(animate);
      };
      animate();
    });
  }

  initThirdPartyLib() {
    this.ngZone.runOutsideAngular(() => {
      // Library callbacks won't trigger CD
      thirdPartyLib.init({
        onUpdate: (data: any) => {
          // Only enter zone when UI needs update
          if (this.needsUIUpdate(data)) {
            this.ngZone.run(() => {
              this.displayData = data;
            });
          }
        }
      });
    });
  }
}
```

**Use cases:**
- Canvas animations
- Third-party libraries with many callbacks
- Heavy computations
- Polling that doesn't always need UI update

---

### Q7: Explain the ExpressionChangedAfterItHasBeenCheckedError.

**Answer:**
This error occurs (in dev mode) when a binding value changes during or after change detection ran.

**Why it exists:**
- Angular enforces unidirectional data flow
- Prevents infinite change detection loops
- Ensures predictable rendering

**Common causes and fixes:**

```typescript
// Cause 1: Getter returns different value each time
// ❌ BAD
get timestamp() {
  return Date.now();  // Different every check
}
// ✓ FIX: Cache the value
timestamp = Date.now();

// Cause 2: Changing state in lifecycle hooks
// ❌ BAD
ngAfterViewInit() {
  this.showContent = true;  // Changes during CD
}
// ✓ FIX: Defer to next cycle
ngAfterViewInit() {
  setTimeout(() => this.showContent = true);
  // Or use signals
  queueMicrotask(() => this.showContent.set(true));
}

// Cause 3: Service updating parent from child
// ❌ BAD - Child changes parent state during CD
@Component({ template: `<child (init)="onChildInit()">` })
class Parent {
  showMore = false;
  onChildInit() {
    this.showMore = true;  // Error!
  }
}
// ✓ FIX: Defer the change
onChildInit() {
  Promise.resolve().then(() => this.showMore = true);
}
```

---

### Q8: How do signals affect change detection?

**Answer:**
Signals provide fine-grained reactivity that integrates seamlessly with change detection:

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <p>Name: {{ user().name }}</p>
    <p>Count: {{ count() }}</p>
    <p>Double: {{ doubleCount() }}</p>
  `
})
export class SignalComponent {
  // Writable signals
  user = signal({ name: 'John' });
  count = signal(0);
  
  // Computed signal (derived state)
  doubleCount = computed(() => this.count() * 2);

  updateCount() {
    this.count.set(10);
    // Angular automatically schedules check
    // No markForCheck() needed
  }

  updateUser() {
    this.user.update(u => ({ ...u, name: 'Jane' }));
    // Triggers CD automatically
  }
}
```

**Benefits of signals:**
1. No `markForCheck()` needed
2. Fine-grained updates (only affected bindings)
3. Works with OnPush out of the box
4. Prepared for zoneless Angular

---

## Advanced Level

### Q9: How would you implement manual change detection for a real-time dashboard?

**Answer:**
For high-frequency updates, detach from CD and manually control updates:

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <div class="metrics">
      @for (metric of metrics; track metric.id) {
        <div class="metric">
          <span>{{ metric.name }}</span>
          <span>{{ metric.value }}</span>
        </div>
      }
    </div>
  `
})
export class DashboardComponent implements OnInit, OnDestroy {
  private cdr = inject(ChangeDetectorRef);
  private ngZone = inject(NgZone);
  private metricsService = inject(MetricsService);
  
  metrics: Metric[] = [];
  private buffer: Metric[] = [];
  private updateInterval: any;

  ngOnInit() {
    // Detach from automatic CD
    this.cdr.detach();

    // Subscribe to real-time updates outside zone
    this.ngZone.runOutsideAngular(() => {
      this.metricsService.stream$.subscribe(metric => {
        this.buffer.push(metric);
      });

      // Batch updates at 60fps
      this.updateInterval = setInterval(() => {
        if (this.buffer.length > 0) {
          this.metrics = [...this.buffer];
          this.buffer = [];
          this.cdr.detectChanges();  // Manual update
        }
      }, 16);  // ~60fps
    });
  }

  ngOnDestroy() {
    clearInterval(this.updateInterval);
    this.cdr.reattach();
  }
}
```

---

### Q10: How does change detection work with async pipe?

**Answer:**
The async pipe automatically:
1. Subscribes to Observable/Promise
2. Calls `markForCheck()` when new value emits
3. Unsubscribes on component destroy

```typescript
// Source code insight:
@Pipe({ pure: false })  // Impure pipe - runs every CD cycle
export class AsyncPipe implements OnDestroy {
  private cdr: ChangeDetectorRef;
  
  transform(obj: Observable<any>) {
    // Subscribe if not already
    this.subscription = obj.subscribe(value => {
      this.latestValue = value;
      this.cdr.markForCheck();  // Trigger CD
    });
    return this.latestValue;
  }
}
```

**Best practice with OnPush:**
```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <!-- Option 1: Multiple async pipes (multiple subscriptions) -->
    @if ((user$ | async)?.isAdmin) {
      <admin-panel [user]="user$ | async" />
    }

    <!-- Option 2: Single subscription with as (preferred) -->
    @if (user$ | async; as user) {
      @if (user.isAdmin) {
        <admin-panel [user]="user" />
      }
    }
  `
})
export class DashboardComponent {
  user$ = this.userService.currentUser$;
}
```

---

### Q11: Explain zoneless Angular and when to use it.

**Answer:**
Zoneless Angular runs without Zone.js, relying on signals for reactivity:

```typescript
// Bootstrap without Zone.js
bootstrapApplication(AppComponent, {
  providers: [
    provideExperimentalZonelessChangeDetection()
  ]
});
```

**Requirements:**
1. Use Signals for reactive state
2. Use async pipe or toSignal() for observables
3. Explicit markForCheck() for edge cases

```typescript
@Component({
  template: `
    <p>{{ count() }}</p>
    <p>{{ data() }}</p>
    <button (click)="increment()">+</button>
  `
})
export class ZonelessComponent {
  count = signal(0);
  
  // Convert observable to signal
  data = toSignal(this.dataService.data$, { initialValue: null });

  increment() {
    this.count.update(c => c + 1);
    // Signal notifies scheduler - no Zone.js needed
  }
}
```

**Benefits:**
- Smaller bundle size (no Zone.js ~100KB)
- Better performance (no monkey-patching)
- More predictable behavior
- Better debugging

**When to use:**
- New Angular 18+ projects
- Performance-critical apps
- When team understands signals well

---

### Q12: How would you optimize a component rendering 10,000 items?

**Answer:**

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <cdk-virtual-scroll-viewport itemSize="50" class="viewport">
      <div *cdkVirtualFor="let item of items; trackBy: trackById">
        {{ item.name }}
      </div>
    </cdk-virtual-scroll-viewport>
  `
})
export class LargeListComponent {
  @Input() items: Item[] = [];

  trackById(index: number, item: Item): number {
    return item.id;
  }
}
```

**Optimization strategies:**

1. **Virtual scrolling** - Only render visible items
2. **OnPush** - Skip unchanged components
3. **trackBy** - Prevent unnecessary re-renders
4. **Memoization** - Cache computed values

```typescript
// Additional optimizations
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class OptimizedListComponent {
  // Use signals for items
  items = signal<Item[]>([]);
  
  // Computed filtered list (memoized)
  filteredItems = computed(() => 
    this.items().filter(i => i.active)
  );

  // trackBy function
  trackById = (index: number, item: Item) => item.id;
}
```

---

## Scenario Questions

### Q13: Component not updating after service call - debug approach?

**Answer:**
Debugging checklist:

```typescript
// 1. Check if using OnPush
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush  // ← This?
})

// 2. Check subscription
ngOnInit() {
  this.service.getData().subscribe(data => {
    console.log('Data received:', data);  // Is this logging?
    this.data = data;
    // If OnPush, need markForCheck()
    this.cdr.markForCheck();
  });
}

// 3. Better approach - use async pipe
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (data$ | async; as data) {
      {{ data | json }}
    }
  `
})
export class Component {
  data$ = this.service.getData();
  // async pipe handles markForCheck automatically
}

// 4. Check if code runs outside zone
this.ngZone.runOutsideAngular(() => {
  // This won't trigger CD
});
// Fix: Use ngZone.run() when updating state
```

---

## Quick Reference

```
Change Detection Methods:
─────────────────────────
markForCheck()    → Schedule check (next cycle)
detectChanges()   → Check immediately
detach()          → Remove from CD tree
reattach()        → Add back to CD tree
checkNoChanges()  → Debug mode verification

OnPush Triggers:
────────────────
✓ Input reference change
✓ DOM event in component
✓ async pipe emission
✓ markForCheck()
✓ detectChanges()
✗ Property mutation
✗ setTimeout/setInterval
✗ Service subscription (without markForCheck)

NgZone Methods:
───────────────
runOutsideAngular() → No CD trigger
run()               → Enter Angular zone
onStable            → After CD completes
onUnstable          → Before CD starts
```
