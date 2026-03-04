# Day 3: Components Deep Dive

## Table of Contents
1. [Component Basics](#1-component-basics)
2. [Component Lifecycle](#2-component-lifecycle)
3. [Change Detection](#3-change-detection)
4. [Signals (Angular 16+)](#4-signals-angular-16)
5. [OnPush Strategy](#5-onpush-strategy)
6. [Input/Output](#6-inputoutput)
7. [ViewChild / ContentChild](#7-viewchild--contentchild)

---

## 1. Component Basics

A component is the fundamental building block of Angular applications. It controls a patch of screen called a view.

### Component Anatomy

```typescript
import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  // Component metadata
  selector: 'app-user-card',         // HTML tag name
  standalone: true,                   // Standalone (default in Angular 22)
  imports: [CommonModule],            // Dependencies
  templateUrl: './user-card.component.html',  // External template
  // OR inline template:
  // template: `<div>{{ user.name }}</div>`,
  styleUrls: ['./user-card.component.scss'],   // External styles
  // OR inline styles:
  // styles: [`.card { padding: 1rem; }`],
  changeDetection: ChangeDetectionStrategy.OnPush,  // Performance
  encapsulation: ViewEncapsulation.Emulated          // CSS scoping
})
export class UserCardComponent {
  @Input() user!: User;
  @Output() selected = new EventEmitter<User>();
  
  onSelect(): void {
    this.selected.emit(this.user);
  }
}
```

### View Encapsulation Modes

```typescript
import { ViewEncapsulation } from '@angular/core';

// 1. Emulated (Default) - Scoped CSS using attributes
@Component({
  encapsulation: ViewEncapsulation.Emulated
})
// Result: .card[_ngcontent-xyz] { }

// 2. None - Global CSS
@Component({
  encapsulation: ViewEncapsulation.None
})
// Result: .card { } (affects entire app)

// 3. ShadowDom - Native Shadow DOM
@Component({
  encapsulation: ViewEncapsulation.ShadowDom
})
// Result: Uses browser's Shadow DOM
```

---

## 2. Component Lifecycle

Angular components go through a series of lifecycle stages. Understanding these is crucial for interviews.

### Lifecycle Hooks Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                    COMPONENT LIFECYCLE                              │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. constructor()        → Class instantiation (no Angular yet)    │
│        ↓                                                            │
│  2. ngOnChanges()        → Input property changes (first & later)  │
│        ↓                                                            │
│  3. ngOnInit()           → Component initialization (once)          │
│        ↓                                                            │
│  4. ngDoCheck()          → Custom change detection (every CD)       │
│        ↓                                                            │
│  5. ngAfterContentInit() → After <ng-content> projected (once)      │
│        ↓                                                            │
│  6. ngAfterContentChecked() → After projected content checked       │
│        ↓                                                            │
│  7. ngAfterViewInit()    → After view children initialized (once)   │
│        ↓                                                            │
│  8. ngAfterViewChecked() → After view children checked              │
│        ↓                                                            │
│  9. ngOnDestroy()        → Cleanup before destruction               │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

### Lifecycle Implementation

```typescript
import { 
  Component, 
  OnInit, 
  OnChanges, 
  DoCheck,
  AfterContentInit, 
  AfterContentChecked,
  AfterViewInit, 
  AfterViewChecked, 
  OnDestroy,
  Input,
  SimpleChanges
} from '@angular/core';
import { Subject, takeUntil, interval } from 'rxjs';

@Component({
  selector: 'app-lifecycle-demo',
  standalone: true,
  template: `<p>{{ data }}</p>`
})
export class LifecycleDemoComponent implements 
  OnInit, OnChanges, DoCheck, 
  AfterContentInit, AfterContentChecked,
  AfterViewInit, AfterViewChecked, 
  OnDestroy {
  
  @Input() data!: string;
  
  private destroy$ = new Subject<void>();
  
  // 1. Constructor - Class instantiation
  // ❌ Don't: Fetch data, access DOM, use inputs
  // ✅ Do: Initialize simple properties, DI
  constructor() {
    console.log('1. Constructor');
    // @Input() not available yet
  }
  
  // 2. ngOnChanges - Called when @Input() properties change
  // First call: Before ngOnInit
  // Subsequent: Whenever input references change
  ngOnChanges(changes: SimpleChanges): void {
    console.log('2. ngOnChanges', changes);
    
    if (changes['data']) {
      const prev = changes['data'].previousValue;
      const curr = changes['data'].currentValue;
      const firstChange = changes['data'].firstChange;
      console.log(`Data changed: ${prev} → ${curr}`);
    }
  }
  
  // 3. ngOnInit - Component initialized
  // ✅ Do: Fetch data, set up subscriptions
  ngOnInit(): void {
    console.log('3. ngOnInit');
    
    // Common pattern: Subscribe to observables
    interval(1000)
      .pipe(takeUntil(this.destroy$))
      .subscribe(val => console.log(val));
  }
  
  // 4. ngDoCheck - Custom change detection
  // ⚠️ Runs on EVERY change detection cycle
  ngDoCheck(): void {
    console.log('4. ngDoCheck');
    // Use sparingly - can impact performance
  }
  
  // 5. ngAfterContentInit - After content projection
  ngAfterContentInit(): void {
    console.log('5. ngAfterContentInit');
    // <ng-content> has been projected
  }
  
  // 6. ngAfterContentChecked - After content checked
  ngAfterContentChecked(): void {
    console.log('6. ngAfterContentChecked');
  }
  
  // 7. ngAfterViewInit - After view initialized
  // ✅ Access @ViewChild here, not in ngOnInit
  ngAfterViewInit(): void {
    console.log('7. ngAfterViewInit');
    // ViewChild queries are available
  }
  
  // 8. ngAfterViewChecked - After view checked
  ngAfterViewChecked(): void {
    console.log('8. ngAfterViewChecked');
  }
  
  // 9. ngOnDestroy - Cleanup
  // ✅ Do: Unsubscribe, clear timers, detach listeners
  ngOnDestroy(): void {
    console.log('9. ngOnDestroy');
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

### Interview Tip: When to Use Each Hook

| Hook | Use Case |
|------|----------|
| `constructor` | Dependency injection only |
| `ngOnChanges` | React to input changes |
| `ngOnInit` | Fetch data, setup subscriptions |
| `ngDoCheck` | Custom change detection logic |
| `ngAfterContentInit` | Access projected content |
| `ngAfterViewInit` | Access ViewChild, DOM manipulation |
| `ngOnDestroy` | Cleanup: unsubscribe, clear timers |

---

## 3. Change Detection

Change detection is how Angular keeps the view in sync with the data model.

### How Change Detection Works

```
┌─────────────────────────────────────────────────────────────┐
│                   CHANGE DETECTION FLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Trigger (async event)                                       │
│        │                                                     │
│        ▼                                                     │
│  Zone.js intercepts                                          │
│        │                                                     │
│        ▼                                                     │
│  ApplicationRef.tick() called                                │
│        │                                                     │
│        ▼                                                     │
│  Root component checked                                      │
│        │                                                     │
│        ▼                                                     │
│  Child components checked (top-down)                         │
│        │                                                     │
│        ▼                                                     │
│  DOM updated if needed                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Change Detection Triggers

1. **DOM Events** - click, input, submit
2. **HTTP Requests** - XHR, fetch
3. **Timers** - setTimeout, setInterval
4. **Promises** - Promise.resolve()
5. **Observables** - When subscribed template binding emits

### Example: Understanding CD Cycles

```typescript
@Component({
  selector: 'app-counter',
  template: `
    <p>Count: {{ count }}</p>
    <p>Computed: {{ getDoubled() }}</p>  <!-- ⚠️ Called every CD -->
    <button (click)="increment()">+1</button>
  `
})
export class CounterComponent {
  count = 0;
  
  increment(): void {
    this.count++;
    // Zone.js detects click → triggers CD → view updates
  }
  
  // ⚠️ Called on EVERY change detection cycle
  getDoubled(): number {
    console.log('getDoubled called');  // Logs multiple times
    return this.count * 2;
  }
}
```

### Performance Fix: Use Signals or Getter Sparingly

```typescript
@Component({
  selector: 'app-counter',
  template: `
    <p>Count: {{ count() }}</p>
    <p>Computed: {{ doubled() }}</p>  <!-- ✅ Only recalculates when count changes -->
    <button (click)="increment()">+1</button>
  `
})
export class CounterComponent {
  count = signal(0);
  doubled = computed(() => this.count() * 2);  // ✅ Memoized
  
  increment(): void {
    this.count.update(c => c + 1);
  }
}
```

---

## 4. Signals (Angular 16+)

Signals are Angular's reactive primitive for state management, providing fine-grained reactivity.

### Signal Basics

```typescript
import { Component, signal, computed, effect } from '@angular/core';

@Component({
  selector: 'app-signals-demo',
  standalone: true,
  template: `
    <h2>Signals Demo</h2>
    
    <!-- Reading signals: call with () -->
    <p>Count: {{ count() }}</p>
    <p>Doubled: {{ doubled() }}</p>
    <p>User: {{ user().name }}</p>
    
    <button (click)="increment()">+1</button>
    <button (click)="reset()">Reset</button>
    <button (click)="updateUser()">Update User</button>
  `
})
export class SignalsDemoComponent {
  // 1. Writable Signal - Basic state
  count = signal(0);
  
  // 2. Signal with object
  user = signal({ name: 'John', age: 30 });
  
  // 3. Computed Signal - Derived state (memoized)
  doubled = computed(() => this.count() * 2);
  
  // 4. Computed with multiple dependencies
  summary = computed(() => 
    `${this.user().name} has count: ${this.count()}`
  );
  
  constructor() {
    // 5. Effect - Side effects when signals change
    effect(() => {
      console.log(`Count changed to: ${this.count()}`);
      // Automatically tracks dependencies
    });
    
    // Effect with cleanup
    effect((onCleanup) => {
      const timer = setInterval(() => console.log(this.count()), 1000);
      
      onCleanup(() => {
        clearInterval(timer);
      });
    });
  }
  
  // Signal Methods
  increment(): void {
    // set() - Replace value
    // this.count.set(this.count() + 1);
    
    // update() - Update based on current value (preferred)
    this.count.update(c => c + 1);
  }
  
  reset(): void {
    this.count.set(0);
  }
  
  updateUser(): void {
    // For objects, create new reference
    this.user.update(u => ({ ...u, age: u.age + 1 }));
    
    // Or use set
    // this.user.set({ name: 'Jane', age: 25 });
  }
}
```

### Signal Input (Angular 17+)

```typescript
import { Component, input, computed } from '@angular/core';

@Component({
  selector: 'app-user-profile',
  standalone: true,
  template: `
    <div class="profile">
      <h2>{{ fullName() }}</h2>
      <p>Age: {{ age() }}</p>
    </div>
  `
})
export class UserProfileComponent {
  // Signal-based inputs (Angular 17+)
  firstName = input.required<string>();  // Required input
  lastName = input<string>('');          // Optional with default
  age = input<number>(0);
  
  // Computed from inputs
  fullName = computed(() => `${this.firstName()} ${this.lastName()}`);
}
```

### Signal Output (Angular 17+)

```typescript
import { Component, output } from '@angular/core';

@Component({
  selector: 'app-button',
  standalone: true,
  template: `
    <button (click)="handleClick()">
      <ng-content />
    </button>
  `
})
export class ButtonComponent {
  // Signal-based output (Angular 17+)
  clicked = output<void>();
  dataEmit = output<{ id: number; name: string }>();
  
  handleClick(): void {
    this.clicked.emit();
    this.dataEmit.emit({ id: 1, name: 'Test' });
  }
}
```

### Signals vs BehaviorSubject

| Aspect | Signals | BehaviorSubject |
|--------|---------|-----------------|
| Syntax | `signal()`, `()` to read | `.value`, `.next()`, `.subscribe()` |
| Subscription | Automatic in templates | Manual, needs async pipe |
| Memory Leaks | No manual cleanup | Requires unsubscribe |
| Computed | Built-in `computed()` | Requires operators |
| Change Detection | Optimized, fine-grained | Triggers full CD |

---

## 5. OnPush Strategy

OnPush change detection strategy significantly improves performance by reducing CD cycles.

### How OnPush Works

```
┌─────────────────────────────────────────────────────────────┐
│                    DEFAULT vs ONPUSH                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DEFAULT: Checks component on EVERY CD cycle                 │
│                                                              │
│  ONPUSH: Checks component ONLY when:                         │
│    1. @Input() reference changes                             │
│    2. Event handler in the component fires                   │
│    3. Async pipe receives new value                          │
│    4. markForCheck() is called                               │
│    5. Signal value changes                                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### OnPush Implementation

```typescript
import { 
  Component, 
  ChangeDetectionStrategy, 
  ChangeDetectorRef,
  Input,
  inject
} from '@angular/core';

@Component({
  selector: 'app-user-list',
  standalone: true,
  imports: [CommonModule, AsyncPipe],
  changeDetection: ChangeDetectionStrategy.OnPush,  // ⚡ OnPush enabled
  template: `
    <div *ngFor="let user of users">
      {{ user.name }}
    </div>
    
    <!-- Async pipe works with OnPush -->
    <div *ngFor="let item of items$ | async">
      {{ item.name }}
    </div>
  `
})
export class UserListComponent {
  @Input() users: User[] = [];
  
  items$ = inject(ItemService).getItems();
  
  private cdr = inject(ChangeDetectorRef);
  
  // Manual trigger when needed
  refreshView(): void {
    // Option 1: Mark for check (schedules check)
    this.cdr.markForCheck();
    
    // Option 2: Detect changes immediately (synchronous)
    // this.cdr.detectChanges();
  }
}
```

### Common OnPush Mistakes

```typescript
// ❌ WRONG: Mutating array doesn't trigger CD in OnPush
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div *ngFor="let item of items">{{ item.name }}</div>`
})
export class BadComponent {
  @Input() items: Item[] = [];
  
  addItem(item: Item): void {
    this.items.push(item);  // ❌ Same reference, no CD triggered
  }
}

// ✅ CORRECT: Create new array reference
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div *ngFor="let item of items">{{ item.name }}</div>`
})
export class GoodComponent {
  @Input() items: Item[] = [];
  
  addItem(item: Item): void {
    this.items = [...this.items, item];  // ✅ New reference
  }
}
```

### OnPush Best Practices

1. **Use immutable data patterns**
2. **Use async pipe for observables**
3. **Use signals for state**
4. **Avoid calling methods in templates**
5. **Use `trackBy` with ngFor**

---

## 6. Input/Output

### Traditional Input/Output

```typescript
import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-product-card',
  standalone: true,
  template: `
    <div class="card">
      <h3>{{ product.name }}</h3>
      <p>{{ product.price | currency }}</p>
      <button (click)="onAddToCart()">Add to Cart</button>
    </div>
  `
})
export class ProductCardComponent {
  // Input properties
  @Input() product!: Product;
  @Input() showPrice = true;  // With default
  @Input({ required: true }) userId!: string;  // Required input
  
  // Input with transform
  @Input({ transform: booleanAttribute }) disabled = false;
  @Input({ transform: numberAttribute }) quantity = 1;
  
  // Input with alias
  @Input('productData') product!: Product;
  
  // Output events
  @Output() addToCart = new EventEmitter<Product>();
  @Output('cartUpdated') updateCart = new EventEmitter<CartItem>();
  
  onAddToCart(): void {
    this.addToCart.emit(this.product);
  }
}

// Parent component usage
@Component({
  template: `
    <app-product-card
      [product]="selectedProduct"
      [showPrice]="true"
      userId="123"
      disabled="true"
      quantity="5"
      (addToCart)="handleAddToCart($event)"
    />
  `
})
export class ParentComponent {
  selectedProduct: Product = { name: 'Laptop', price: 999 };
  
  handleAddToCart(product: Product): void {
    console.log('Adding to cart:', product);
  }
}
```

### Signal-Based Input/Output (Angular 17+)

```typescript
import { Component, input, output, computed, model } from '@angular/core';

@Component({
  selector: 'app-modern-card',
  standalone: true,
  template: `
    <div class="card">
      <h3>{{ title() }}</h3>
      <p>Count: {{ count() }}</p>
      <button (click)="increment()">+</button>
    </div>
  `
})
export class ModernCardComponent {
  // Signal inputs
  title = input.required<string>();
  description = input<string>('No description');  // With default
  
  // Computed from inputs
  summary = computed(() => `${this.title()}: ${this.description()}`);
  
  // Two-way binding with model()
  count = model(0);
  
  // Signal outputs
  clicked = output<void>();
  valueChanged = output<number>();
  
  increment(): void {
    this.count.update(c => c + 1);
    this.valueChanged.emit(this.count());
  }
}

// Parent usage
@Component({
  template: `
    <app-modern-card
      title="My Card"
      [description]="desc"
      [(count)]="counterValue"
      (valueChanged)="onValueChange($event)"
    />
  `
})
export class ParentComponent {
  desc = 'A modern card';
  counterValue = 10;
  
  onValueChange(value: number): void {
    console.log('New value:', value);
  }
}
```

### Two-Way Binding (Banana in a Box)

```typescript
// Custom two-way binding
@Component({
  selector: 'app-rating',
  standalone: true,
  template: `
    <div class="stars">
      @for (star of stars; track star) {
        <span 
          [class.filled]="star <= value"
          (click)="setValue(star)">
          ★
        </span>
      }
    </div>
  `
})
export class RatingComponent {
  @Input() value = 0;
  @Output() valueChange = new EventEmitter<number>();
  
  stars = [1, 2, 3, 4, 5];
  
  setValue(rating: number): void {
    this.value = rating;
    this.valueChange.emit(rating);
  }
}

// Usage with [(value)]
@Component({
  template: `
    <app-rating [(value)]="userRating" />
    <p>Your rating: {{ userRating }}</p>
  `
})
export class ReviewComponent {
  userRating = 3;
}
```

---

## 7. ViewChild / ContentChild

### ViewChild - Query Template Elements

```typescript
import { 
  Component, 
  ViewChild, 
  ViewChildren,
  ElementRef, 
  QueryList,
  AfterViewInit
} from '@angular/core';

@Component({
  selector: 'app-form-demo',
  standalone: true,
  template: `
    <!-- Template reference variable -->
    <input #nameInput type="text" placeholder="Name">
    <input #emailInput type="email" placeholder="Email">
    
    <!-- Child component -->
    <app-button #submitBtn>Submit</app-button>
    
    <div #container class="container">
      <p *ngFor="let item of items" #listItem>{{ item }}</p>
    </div>
  `
})
export class FormDemoComponent implements AfterViewInit {
  items = ['A', 'B', 'C'];
  
  // 1. Query native element
  @ViewChild('nameInput') 
  nameInput!: ElementRef<HTMLInputElement>;
  
  // 2. Query with static: true (available in ngOnInit)
  @ViewChild('emailInput', { static: true }) 
  emailInput!: ElementRef<HTMLInputElement>;
  
  // 3. Query child component
  @ViewChild('submitBtn') 
  submitBtn!: ButtonComponent;
  
  // 4. Query by component type
  @ViewChild(ButtonComponent) 
  button!: ButtonComponent;
  
  // 5. Query multiple elements
  @ViewChildren('listItem') 
  listItems!: QueryList<ElementRef>;
  
  // 6. Query with options
  @ViewChild('container', { read: ElementRef }) 
  container!: ElementRef;
  
  ngAfterViewInit(): void {
    // ✅ ViewChild queries are available here
    console.log(this.nameInput.nativeElement.value);
    console.log(this.listItems.length);  // 3
    
    // Listen to changes
    this.listItems.changes.subscribe((items) => {
      console.log('List updated:', items.length);
    });
  }
  
  focusName(): void {
    this.nameInput.nativeElement.focus();
  }
}
```

### ContentChild - Query Projected Content

```typescript
// Parent projects content into child
@Component({
  selector: 'app-card',
  standalone: true,
  template: `
    <div class="card">
      <div class="header">
        <ng-content select="[cardTitle]"></ng-content>
      </div>
      <div class="body">
        <ng-content></ng-content>
      </div>
      <div class="footer">
        <ng-content select="[cardFooter]"></ng-content>
      </div>
    </div>
  `
})
export class CardComponent implements AfterContentInit {
  // Query projected content
  @ContentChild('header') 
  headerContent!: ElementRef;
  
  @ContentChildren('item') 
  items!: QueryList<ElementRef>;
  
  ngAfterContentInit(): void {
    // ✅ ContentChild queries available here
    console.log(this.headerContent);
    console.log(this.items.length);
  }
}

// Usage
@Component({
  template: `
    <app-card>
      <h3 cardTitle #header>Card Title</h3>
      
      <p #item>Content item 1</p>
      <p #item>Content item 2</p>
      
      <button cardFooter>Action</button>
    </app-card>
  `
})
export class ParentComponent { }
```

### Signal-Based Queries (Angular 17+)

```typescript
import { Component, viewChild, viewChildren, contentChild, contentChildren, AfterViewInit } from '@angular/core';

@Component({
  selector: 'app-modern-queries',
  template: `
    <input #searchInput />
    <app-item *ngFor="let i of [1,2,3]" #item />
  `
})
export class ModernQueriesComponent {
  // Signal-based viewChild
  searchInput = viewChild<ElementRef>('searchInput');
  firstItem = viewChild(ItemComponent);
  
  // Required viewChild
  requiredInput = viewChild.required<ElementRef>('searchInput');
  
  // Signal-based viewChildren
  allItems = viewChildren(ItemComponent);
  
  ngAfterViewInit(): void {
    // Access as signals
    console.log(this.searchInput()?.nativeElement);
    console.log(this.allItems().length);
  }
}
```

### ViewChild vs ContentChild Summary

| Query | What it finds | Available in |
|-------|---------------|--------------|
| `@ViewChild` | Elements in component's template | `ngAfterViewInit` |
| `@ContentChild` | Elements projected via `<ng-content>` | `ngAfterContentInit` |
| `@ViewChildren` | Multiple elements in template | `ngAfterViewInit` |
| `@ContentChildren` | Multiple projected elements | `ngAfterContentInit` |

---

## Summary

| Concept | Key Points |
|---------|------------|
| Lifecycle | 9 hooks from constructor to destroy |
| Change Detection | Zone.js triggers, Default vs OnPush |
| Signals | Modern reactive state, computed, effects |
| OnPush | Check only on input/event/async/signal changes |
| Input/Output | Data flow between components |
| ViewChild | Query own template elements |
| ContentChild | Query projected content |

---

## Next Steps
- Practice creating components with all lifecycle hooks
- Implement a component with OnPush strategy
- Convert a BehaviorSubject to Signals
- Build a reusable component with Input/Output
