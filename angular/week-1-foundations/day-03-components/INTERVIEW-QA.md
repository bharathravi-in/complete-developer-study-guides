# Day 3: Interview Q&A – Components Deep Dive

## Q1: Explain the Angular component lifecycle hooks in order.

**Answer:**
Angular components go through lifecycle stages from creation to destruction:

1. **constructor()** - Class instantiation, DI only
2. **ngOnChanges()** - Called when @Input() changes (before ngOnInit)
3. **ngOnInit()** - Component initialization, fetch data
4. **ngDoCheck()** - Custom change detection (every CD cycle)
5. **ngAfterContentInit()** - After ng-content projected (once)
6. **ngAfterContentChecked()** - After projected content checked
7. **ngAfterViewInit()** - After view children initialized (once)
8. **ngAfterViewChecked()** - After view children checked
9. **ngOnDestroy()** - Cleanup before destruction

**Interview Tip:** Mention that `ngOnInit` is for data fetching, `ngAfterViewInit` for ViewChild access, and `ngOnDestroy` for cleanup (unsubscribe, clear timers).

---

## Q2: What is the difference between constructor and ngOnInit?

**Answer:**

| constructor | ngOnInit |
|-------------|----------|
| TypeScript class feature | Angular lifecycle hook |
| Called during instantiation | Called after inputs are set |
| @Input values NOT available | @Input values available |
| Use for DI only | Use for initialization logic |
| Runs before Angular | Part of Angular lifecycle |

```typescript
@Component({ ... })
export class MyComponent implements OnInit {
  @Input() userId!: string;
  
  constructor(private userService: UserService) {
    // ✅ DI works
    // ❌ this.userId is undefined here
  }
  
  ngOnInit(): void {
    // ✅ this.userId is available
    this.userService.getUser(this.userId);
  }
}
```

---

## Q3: How does Angular's change detection work?

**Answer:**
Change detection is Angular's mechanism to synchronize the component model with the DOM.

**Process:**
1. **Trigger** - Async event occurs (click, HTTP, timer)
2. **Zone.js** - Intercepts and notifies Angular
3. **ApplicationRef.tick()** - Starts CD cycle
4. **Top-down check** - From root to leaf components
5. **DOM update** - Updates changed bindings

**Strategies:**
- **Default** - Checks component on every CD cycle
- **OnPush** - Checks only when inputs change, events fire, or async pipe emits

```typescript
// OnPush for performance
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})
```

---

## Q4: What is OnPush strategy and when does it trigger change detection?

**Answer:**
OnPush is a performance optimization that limits when change detection runs.

**OnPush triggers CD when:**
1. @Input() **reference** changes (not mutation)
2. Event handler in the component fires
3. Async pipe receives new value
4. `markForCheck()` is called manually
5. Signal value changes

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ListComponent {
  @Input() items: Item[] = [];
  
  // ❌ Won't work - same reference
  addWrong(item: Item): void {
    this.items.push(item);
  }
  
  // ✅ Works - new reference
  addCorrect(item: Item): void {
    this.items = [...this.items, item];
  }
}
```

**Best practices with OnPush:**
- Use immutable data
- Use async pipe
- Use signals
- Avoid method calls in templates

---

## Q5: What are Signals in Angular? How do they compare to BehaviorSubject?

**Answer:**
Signals are Angular's reactive primitive for fine-grained state management (Angular 16+).

**Types:**
1. **Writable Signal** - `signal(value)` - basic state
2. **Computed Signal** - `computed(() => ...)` - derived state
3. **Effect** - `effect(() => ...)` - side effects

```typescript
// Signal
count = signal(0);
doubled = computed(() => this.count() * 2);

// Update
this.count.set(5);
this.count.update(c => c + 1);

// Effect
effect(() => console.log(this.count()));
```

**Signals vs BehaviorSubject:**

| Signals | BehaviorSubject |
|---------|-----------------|
| `count()` to read | `.value` or subscribe |
| No manual unsubscribe | Requires cleanup |
| Built-in computed | Needs operators |
| Fine-grained CD | Full CD cycle |
| Template-friendly | Needs async pipe |

---

## Q6: What is the difference between @ViewChild and @ContentChild?

**Answer:**

| @ViewChild | @ContentChild |
|------------|---------------|
| Queries own template | Queries projected content |
| Available in ngAfterViewInit | Available in ngAfterContentInit |
| Elements inside component | Elements in `<ng-content>` |

```typescript
// Component template
@Component({
  template: `
    <input #myInput />           <!-- ViewChild -->
    <ng-content></ng-content>    <!-- ContentChild queries here -->
  `
})
export class CardComponent {
  @ViewChild('myInput') input!: ElementRef;
  @ContentChild('header') header!: ElementRef;
}

// Parent
@Component({
  template: `
    <app-card>
      <h1 #header>Title</h1>   <!-- ContentChild target -->
    </app-card>
  `
})
```

---

## Q7: How do you prevent memory leaks in Angular components?

**Answer:**
Memory leaks occur when subscriptions, timers, or event listeners aren't cleaned up.

**Solutions:**

1. **takeUntil pattern:**
```typescript
private destroy$ = new Subject<void>();

ngOnInit(): void {
  this.service.getData()
    .pipe(takeUntil(this.destroy$))
    .subscribe();
}

ngOnDestroy(): void {
  this.destroy$.next();
  this.destroy$.complete();
}
```

2. **takeUntilDestroyed (Angular 16+):**
```typescript
data$ = inject(DataService).getData()
  .pipe(takeUntilDestroyed());
```

3. **Async pipe:**
```html
<!-- Automatically unsubscribes -->
<div *ngIf="data$ | async as data">{{ data }}</div>
```

4. **Clear timers:**
```typescript
private timer?: ReturnType<typeof setTimeout>;

ngOnInit(): void {
  this.timer = setTimeout(() => {}, 1000);
}

ngOnDestroy(): void {
  if (this.timer) clearTimeout(this.timer);
}
```

5. **Remove event listeners:**
```typescript
private listener = (e: Event) => this.handle(e);

ngOnInit(): void {
  window.addEventListener('resize', this.listener);
}

ngOnDestroy(): void {
  window.removeEventListener('resize', this.listener);
}
```

---

## Q8: What is ViewEncapsulation and what are its types?

**Answer:**
ViewEncapsulation determines how CSS styles are scoped to components.

**Types:**

1. **Emulated (default):**
   - Adds unique attributes to elements
   - Scopes CSS to component
   - `_ngcontent-xxx` attributes

2. **None:**
   - No encapsulation
   - Styles are global
   - Can affect entire application

3. **ShadowDom:**
   - Uses native Shadow DOM
   - True isolation
   - Limited browser support

```typescript
@Component({
  encapsulation: ViewEncapsulation.Emulated  // Default
  // encapsulation: ViewEncapsulation.None
  // encapsulation: ViewEncapsulation.ShadowDom
})
```

---

## Q9: What are Input transforms in Angular?

**Answer:**
Input transforms convert input values automatically (Angular 16+).

```typescript
import { booleanAttribute, numberAttribute } from '@angular/core';

@Component({ ... })
export class ButtonComponent {
  // Transform string "true"/"false" to boolean
  @Input({ transform: booleanAttribute }) disabled = false;
  
  // Transform string to number
  @Input({ transform: numberAttribute }) count = 0;
  
  // Custom transform
  @Input({ transform: (value: string) => value.toUpperCase() }) 
  label = '';
}
```

Usage:
```html
<!-- These string values are transformed -->
<app-button disabled="true" count="5" label="hello" />
```

---

## Q10: How do you implement two-way binding in Angular?

**Answer:**
Two-way binding uses the "banana in a box" syntax `[()]`.

**Built-in ngModel:**
```html
<input [(ngModel)]="name" />
```

**Custom two-way binding:**
```typescript
@Component({
  selector: 'app-counter'
})
export class CounterComponent {
  // Convention: property + propertyChange
  @Input() value = 0;
  @Output() valueChange = new EventEmitter<number>();
  
  increment(): void {
    this.value++;
    this.valueChange.emit(this.value);
  }
}
```

Usage:
```html
<app-counter [(value)]="count" />
<!-- Equivalent to: -->
<app-counter [value]="count" (valueChange)="count = $event" />
```

**With model() (Angular 17+):**
```typescript
@Component({...})
export class CounterComponent {
  value = model(0);  // Combines Input + Output
  
  increment(): void {
    this.value.update(v => v + 1);
  }
}
```

---

## Q11: What is the difference between signal() and computed()?

**Answer:**

| signal() | computed() |
|----------|------------|
| Writable (set, update) | Read-only |
| Source of truth | Derived value |
| No dependencies | Tracks dependencies automatically |
| Manual updates | Auto-recalculates when deps change |

```typescript
// Source signals
firstName = signal('John');
lastName = signal('Doe');

// Computed - automatically updates when firstName or lastName changes
fullName = computed(() => `${this.firstName()} ${this.lastName()}`);

// Usage
this.firstName.set('Jane');
console.log(this.fullName());  // "Jane Doe" - auto-updated
```

**Key points:**
- `computed()` is memoized - only recalculates when dependencies change
- Cannot set a computed signal directly
- Dependencies are tracked automatically

---

## Q12: How do you optimize component performance in Angular?

**Answer:**

1. **Use OnPush change detection:**
```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})
```

2. **Use trackBy with ngFor:**
```typescript
@Component({
  template: `
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

3. **Use Signals instead of methods in templates:**
```typescript
// ❌ Called every CD cycle
getTotal(): number { return this.items.reduce(...); }

// ✅ Memoized
total = computed(() => this.items().reduce(...));
```

4. **Lazy load components:**
```typescript
@defer {
  <app-heavy-component />
} @loading {
  <p>Loading...</p>
}
```

5. **Use pure pipes over methods:**
```typescript
// Pure pipe is memoized
<p>{{ value | transform }}</p>
```

6. **Virtual scrolling for large lists:**
```typescript
<cdk-virtual-scroll-viewport itemSize="50">
  <div *cdkVirtualFor="let item of items">{{ item }}</div>
</cdk-virtual-scroll-viewport>
```

---

## Q13: What are the static options in @ViewChild?

**Answer:**
The `static` option determines when the query resolves.

```typescript
// static: false (default)
// Available in ngAfterViewInit, supports *ngIf
@ViewChild('element') element!: ElementRef;

// static: true
// Available in ngOnInit, but element must exist (no *ngIf)
@ViewChild('element', { static: true }) element!: ElementRef;
```

**When to use:**
- `static: true` - Element always exists, need early access
- `static: false` - Element conditional (*ngIf), deferred access

---

## Q14: How do you trigger manual change detection?

**Answer:**
Use `ChangeDetectorRef` for manual control:

```typescript
@Component({ ... })
export class MyComponent {
  private cdr = inject(ChangeDetectorRef);
  
  // Mark component and ancestors for check (async)
  triggerCheck(): void {
    this.cdr.markForCheck();
  }
  
  // Run change detection immediately on this component
  detectNow(): void {
    this.cdr.detectChanges();
  }
  
  // Detach from CD tree (stop automatic checks)
  detach(): void {
    this.cdr.detach();
  }
  
  // Reattach to CD tree
  reattach(): void {
    this.cdr.reattach();
  }
}
```

**Use cases:**
- `markForCheck()` - OnPush component updated outside Angular
- `detectChanges()` - Immediate DOM update needed
- `detach()` - Performance optimization for static views

---

## Quick Reference Card

| Topic | Key Points |
|-------|------------|
| Lifecycle | constructor → ngOnInit → ngAfterViewInit → ngOnDestroy |
| Change Detection | Zone.js triggers, Default vs OnPush |
| OnPush Triggers | Input change, event, async pipe, signal, markForCheck |
| Signals | signal(), computed(), effect() |
| Memory Leaks | takeUntilDestroyed, async pipe, ngOnDestroy cleanup |
| ViewChild | Query template, ngAfterViewInit |
| ContentChild | Query ng-content, ngAfterContentInit |
| Two-way | Property + propertyChange, or model() |
