# Day 5: Interview Q&A – Directives & Pipes

## Q1: What is the difference between structural and attribute directives?

**Answer:**
Angular has three types of directives: components, structural directives, and attribute directives.

| Structural Directives | Attribute Directives |
|-----------------------|----------------------|
| Modify DOM structure (add/remove elements) | Modify appearance or behavior |
| Prefixed with asterisk `*` | No special prefix |
| Create/destroy DOM elements | Work on existing elements |
| Examples: `*ngIf`, `*ngFor`, `*ngSwitch` | Examples: `ngClass`, `ngStyle`, custom |
| Use `TemplateRef` and `ViewContainerRef` | Use `ElementRef` and `Renderer2` |
| Only one per element | Multiple allowed per element |

```html
<!-- Structural directive - adds/removes element from DOM -->
<div *ngIf="isVisible">This may or may not exist in DOM</div>

<!-- Attribute directive - changes appearance -->
<div [ngClass]="{'active': isActive}">Always in DOM</div>
<div [ngStyle]="{'color': textColor}">Changes style</div>

<!-- Structural directive desugaring -->
<ng-template [ngIf]="isVisible">
  <div>This is what Angular actually creates</div>
</ng-template>
```

**Interview Tip:** Mention that the asterisk `*` is syntactic sugar - Angular internally transforms `*ngIf` into an `<ng-template>` element.

---

## Q2: How do you create a custom attribute directive?

**Answer:**
Custom attribute directives are created using the `@Directive` decorator with `ElementRef` for DOM access.

```typescript
import { 
  Directive, 
  ElementRef, 
  Input, 
  OnInit,
  inject 
} from '@angular/core';

@Directive({
  selector: '[appHighlight]',
  standalone: true
})
export class HighlightDirective implements OnInit {
  private el = inject(ElementRef);
  
  @Input() appHighlight = 'yellow';  // Same name as selector
  @Input() defaultColor = 'transparent';
  
  ngOnInit(): void {
    this.el.nativeElement.style.backgroundColor = this.appHighlight;
  }
}
```

**Usage:**
```html
<p appHighlight>Uses default yellow</p>
<p [appHighlight]="'lightblue'">Uses lightblue</p>
<p appHighlight="pink" defaultColor="white">Uses pink</p>
```

**Creating a structural directive:**
```typescript
import { 
  Directive, 
  Input, 
  TemplateRef, 
  ViewContainerRef,
  inject 
} from '@angular/core';

@Directive({
  selector: '[appUnless]',
  standalone: true
})
export class UnlessDirective {
  private templateRef = inject(TemplateRef<any>);
  private viewContainer = inject(ViewContainerRef);
  private hasView = false;
  
  @Input() set appUnless(condition: boolean) {
    if (!condition && !this.hasView) {
      this.viewContainer.createEmbeddedView(this.templateRef);
      this.hasView = true;
    } else if (condition && this.hasView) {
      this.viewContainer.clear();
      this.hasView = false;
    }
  }
}

// Usage: <p *appUnless="isHidden">Shown when isHidden is false</p>
```

---

## Q3: What are @HostListener and @HostBinding? When do you use them?

**Answer:**
`@HostListener` and `@HostBinding` are decorators used in directives to interact with the host element.

| @HostListener | @HostBinding |
|---------------|--------------|
| Listens to host element events | Binds to host element properties |
| Replaces `addEventListener` | Replaces property assignment |
| Takes event name and optional args | Takes property name |
| Executes method on event | Syncs class property to host |

```typescript
@Directive({
  selector: '[appInteractive]',
  standalone: true
})
export class InteractiveDirective {
  // HostBinding - binds class property to host property
  @HostBinding('class.active') isActive = false;
  @HostBinding('style.cursor') cursor = 'pointer';
  @HostBinding('attr.aria-pressed') get ariaPressed() {
    return this.isActive;
  }
  
  // HostListener - listens to host events
  @HostListener('mouseenter')
  onMouseEnter(): void {
    this.isActive = true;
  }
  
  @HostListener('mouseleave')
  onMouseLeave(): void {
    this.isActive = false;
  }
  
  // With event object
  @HostListener('click', ['$event'])
  onClick(event: MouseEvent): void {
    console.log('Clicked at:', event.clientX, event.clientY);
  }
  
  // Listen to document/window events
  @HostListener('document:keydown.escape')
  onEscape(): void {
    this.isActive = false;
  }
  
  @HostListener('window:resize', ['$event.target.innerWidth'])
  onResize(width: number): void {
    console.log('Window width:', width);
  }
}
```

**Modern alternative using `host` metadata:**
```typescript
@Directive({
  selector: '[appHighlight]',
  standalone: true,
  host: {
    '(mouseenter)': 'onEnter()',
    '(mouseleave)': 'onLeave()',
    '[class.highlighted]': 'isHighlighted',
    '[style.backgroundColor]': 'bgColor'
  }
})
export class HighlightDirective {
  isHighlighted = false;
  bgColor = 'transparent';
  
  onEnter(): void {
    this.bgColor = 'yellow';
    this.isHighlighted = true;
  }
  
  onLeave(): void {
    this.bgColor = 'transparent';
    this.isHighlighted = false;
  }
}
```

**Interview Tip:** Mention that `@HostListener` automatically handles cleanup - no need to manually remove event listeners.

---

## Q4: What are pipes in Angular and why use them?

**Answer:**
Pipes are template transformation functions that format data for display without modifying the underlying data.

**Why use pipes:**
1. **Separation of concerns** - Keep formatting logic out of components
2. **Reusability** - Use same transformation across multiple templates
3. **Readability** - Cleaner template syntax
4. **Performance** - Pure pipes are memoized

```typescript
// Without pipes - logic in component
@Component({
  template: `<p>{{ formattedPrice }}</p>`
})
export class BadComponent {
  price = 99.99;
  get formattedPrice() {
    return '$' + this.price.toFixed(2);
  }
}

// With pipes - clean template
@Component({
  template: `<p>{{ price | currency }}</p>`
})
export class GoodComponent {
  price = 99.99;
}
```

**Pipe chaining:**
```html
<!-- Multiple pipes applied left to right -->
<p>{{ birthday | date:'fullDate' | uppercase }}</p>
<!-- Output: FRIDAY, MARCH 15, 2024 -->

<!-- With parameters -->
<p>{{ amount | currency:'EUR':'symbol':'1.2-2' }}</p>
```

**Pipe syntax:**
```
{{ value | pipeName:arg1:arg2 }}
```

---

## Q5: What is the difference between pure and impure pipes?

**Answer:**
Pure and impure pipes differ in when Angular executes the pipe's `transform` method.

| Pure Pipe (default) | Impure Pipe |
|---------------------|-------------|
| `pure: true` (default) | `pure: false` |
| Called only when input **reference** changes | Called on **every** change detection cycle |
| Results are cached/memoized | No caching |
| Better performance | Can impact performance |
| Does NOT detect object/array mutations | Detects mutations |
| Use for primitive values, immutable data | Use for mutable data, real-time filtering |

```typescript
// Pure Pipe - Default behavior
@Pipe({
  name: 'filter',
  standalone: true,
  pure: true  // Default - can be omitted
})
export class FilterPipe implements PipeTransform {
  transform(items: string[], search: string): string[] {
    console.log('Pure pipe called');  // Called only on reference change
    return items.filter(item => item.includes(search));
  }
}

// Impure Pipe
@Pipe({
  name: 'filterImpure',
  standalone: true,
  pure: false
})
export class FilterImpurePipe implements PipeTransform {
  transform(items: string[], search: string): string[] {
    console.log('Impure pipe called');  // Called EVERY CD cycle
    return items.filter(item => item.includes(search));
  }
}
```

**Demonstrating the difference:**
```typescript
@Component({
  template: `
    <input [(ngModel)]="search">
    <ul>
      @for (item of items | filter:search; track item) {
        <li>{{ item }}</li>
      }
    </ul>
    <button (click)="addItem()">Add Item</button>
  `
})
export class DemoComponent {
  items = ['Apple', 'Banana', 'Cherry'];
  search = '';
  
  addItem(): void {
    // Pure pipe WON'T detect this mutation
    this.items.push('Date');
    
    // Pure pipe WILL detect this (new reference)
    // this.items = [...this.items, 'Date'];
  }
}
```

**Interview Tip:** Always prefer pure pipes. If you need impure behavior, consider using immutable data patterns instead.

---

## Q6: How does the async pipe work and what are its benefits?

**Answer:**
The `async` pipe subscribes to an Observable or Promise and automatically returns the emitted value.

**How it works:**
1. Subscribes to Observable/Promise when component initializes
2. Returns emitted values to the template
3. Marks component for change detection on new values
4. **Automatically unsubscribes** when component is destroyed

```typescript
@Component({
  standalone: true,
  imports: [AsyncPipe],
  template: `
    <!-- Basic usage -->
    @if (user$ | async; as user) {
      <h1>Welcome, {{ user.name }}</h1>
      <p>Email: {{ user.email }}</p>
    } @else {
      <p>Loading user...</p>
    }
  `
})
export class UserComponent {
  user$ = inject(UserService).getUser();
}
```

**Benefits:**

| Benefit | Description |
|---------|-------------|
| Auto unsubscribe | No memory leaks, no `ngOnDestroy` cleanup |
| Works with OnPush | Triggers change detection automatically |
| Cleaner code | No manual subscribe/unsubscribe |
| Null safety | Returns `null` until first emission |

**Comparison - Manual vs Async Pipe:**
```typescript
// ❌ Manual subscription - requires cleanup
@Component({...})
export class ManualComponent implements OnInit, OnDestroy {
  user: User | null = null;
  private destroy$ = new Subject<void>();
  
  ngOnInit(): void {
    this.userService.getUser()
      .pipe(takeUntil(this.destroy$))
      .subscribe(user => this.user = user);
  }
  
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}

// ✅ Async pipe - automatic cleanup
@Component({
  template: `@if (user$ | async; as user) { {{ user.name }} }`
})
export class AsyncComponent {
  user$ = inject(UserService).getUser();
}
```

**Avoiding multiple subscriptions:**
```html
<!-- ❌ Bad - creates 3 subscriptions -->
<p>{{ (user$ | async)?.name }}</p>
<p>{{ (user$ | async)?.email }}</p>
<p>{{ (user$ | async)?.role }}</p>

<!-- ✅ Good - single subscription -->
@if (user$ | async; as user) {
  <p>{{ user.name }}</p>
  <p>{{ user.email }}</p>
  <p>{{ user.role }}</p>
}
```

---

## Q7: How do you create a custom pipe?

**Answer:**
Custom pipes are created using the `@Pipe` decorator and implementing the `PipeTransform` interface.

```typescript
import { Pipe, PipeTransform } from '@angular/core';

// Basic pipe
@Pipe({
  name: 'truncate',
  standalone: true
})
export class TruncatePipe implements PipeTransform {
  transform(value: string, limit = 50, ellipsis = '...'): string {
    if (!value) return '';
    if (value.length <= limit) return value;
    return value.substring(0, limit) + ellipsis;
  }
}

// Usage: {{ longText | truncate:20:'...' }}
```

**File size pipe:**
```typescript
@Pipe({
  name: 'fileSize',
  standalone: true
})
export class FileSizePipe implements PipeTransform {
  private units = ['B', 'KB', 'MB', 'GB', 'TB'];
  
  transform(bytes: number, precision = 2): string {
    if (bytes === 0) return '0 B';
    
    const unitIndex = Math.floor(Math.log(bytes) / Math.log(1024));
    const size = bytes / Math.pow(1024, unitIndex);
    
    return `${size.toFixed(precision)} ${this.units[unitIndex]}`;
  }
}

// Usage: {{ 1536000 | fileSize }}  → "1.46 MB"
```

**Time ago pipe:**
```typescript
@Pipe({
  name: 'timeAgo',
  standalone: true
})
export class TimeAgoPipe implements PipeTransform {
  transform(value: Date | string): string {
    const date = new Date(value);
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    
    const intervals: [number, string][] = [
      [31536000, 'year'],
      [2592000, 'month'],
      [86400, 'day'],
      [3600, 'hour'],
      [60, 'minute']
    ];
    
    for (const [secondsInUnit, unit] of intervals) {
      const interval = Math.floor(seconds / secondsInUnit);
      if (interval >= 1) {
        return interval === 1 ? `1 ${unit} ago` : `${interval} ${unit}s ago`;
      }
    }
    return 'just now';
  }
}

// Usage: {{ createdAt | timeAgo }}  → "2 hours ago"
```

**Pipe with dependency injection:**
```typescript
@Pipe({
  name: 'translate',
  standalone: true
})
export class TranslatePipe implements PipeTransform {
  private translateService = inject(TranslateService);
  
  transform(key: string, params?: Record<string, string>): string {
    return this.translateService.translate(key, params);
  }
}
```

---

## Q8: When should you use impure pipes?

**Answer:**
Impure pipes should be used sparingly in specific scenarios where pure pipes don't meet requirements.

**Use impure pipes when:**

1. **Filtering/sorting mutable arrays** (when you can't use immutable patterns)
2. **Real-time data transformation** based on external state
3. **Pipes that depend on frequently changing state**

```typescript
// Use case 1: Filter pipe that needs to detect array mutations
@Pipe({
  name: 'filterByStatus',
  standalone: true,
  pure: false  // Impure because array is mutated
})
export class FilterByStatusPipe implements PipeTransform {
  transform(items: Task[], status: string): Task[] {
    if (!items || !status) return items;
    return items.filter(item => item.status === status);
  }
}

// Use case 2: Pipe depending on external service state
@Pipe({
  name: 'localizedDate',
  standalone: true,
  pure: false  // Impure because locale can change
})
export class LocalizedDatePipe implements PipeTransform {
  private localeService = inject(LocaleService);
  
  transform(value: Date): string {
    return value.toLocaleDateString(this.localeService.currentLocale);
  }
}
```

**Performance considerations:**
```typescript
// ❌ Impure pipe - runs on every CD cycle
@Pipe({ name: 'expensive', pure: false })
export class ExpensivePipe implements PipeTransform {
  transform(items: Item[]): Item[] {
    console.log('Running expensive operation...');  // Logs constantly!
    return items.sort((a, b) => a.name.localeCompare(b.name));
  }
}

// ✅ Better: Use immutable data with pure pipe
@Component({
  template: `{{ sortedItems$ | async | json }}`
})
export class BetterComponent {
  items$ = new BehaviorSubject<Item[]>([]);
  
  sortedItems$ = this.items$.pipe(
    map(items => [...items].sort((a, b) => a.name.localeCompare(b.name)))
  );
  
  addItem(item: Item): void {
    this.items$.next([...this.items$.value, item]);
  }
}
```

**Interview Tip:** The `async` pipe is actually an impure pipe - it needs to run on every CD to check for new emissions - but Angular optimizes it internally.

---

## Q9: What are the built-in Angular pipes? Provide examples.

**Answer:**
Angular provides several built-in pipes for common transformations:

**Text Pipes:**
```html
<!-- Case transformation -->
{{ 'hello world' | uppercase }}     <!-- HELLO WORLD -->
{{ 'HELLO WORLD' | lowercase }}     <!-- hello world -->
{{ 'hello world' | titlecase }}     <!-- Hello World -->

<!-- Slice -->
{{ 'Angular' | slice:0:3 }}         <!-- Ang -->
{{ 'Angular' | slice:3 }}           <!-- ular -->
```

**Number Pipes:**
```html
<!-- Number formatting: 'minInt.minFrac-maxFrac' -->
{{ 3.14159 | number:'1.2-4' }}      <!-- 3.1416 -->
{{ 1234567 | number:'1.0-0' }}      <!-- 1,234,567 -->

<!-- Currency -->
{{ 99.99 | currency }}              <!-- $99.99 -->
{{ 99.99 | currency:'EUR' }}        <!-- €99.99 -->
{{ 99.99 | currency:'GBP':'symbol':'1.0-0' }}  <!-- £100 -->

<!-- Percent -->
{{ 0.85 | percent }}                <!-- 85% -->
{{ 0.8567 | percent:'1.2-2' }}      <!-- 85.67% -->
```

**Date Pipe:**
```html
<!-- Predefined formats -->
{{ today | date:'short' }}          <!-- 3/15/24, 10:30 AM -->
{{ today | date:'medium' }}         <!-- Mar 15, 2024, 10:30:00 AM -->
{{ today | date:'long' }}           <!-- March 15, 2024 at 10:30:00 AM GMT -->
{{ today | date:'full' }}           <!-- Friday, March 15, 2024 -->

<!-- Custom formats -->
{{ today | date:'yyyy-MM-dd' }}     <!-- 2024-03-15 -->
{{ today | date:'dd/MM/yyyy' }}     <!-- 15/03/2024 -->
{{ today | date:'EEEE, MMMM d' }}   <!-- Friday, March 15 -->
{{ today | date:'HH:mm:ss' }}       <!-- 14:30:00 -->
{{ today | date:'h:mm a z' }}       <!-- 2:30 PM GMT -->
```

**Other Useful Pipes:**
```html
<!-- JSON - useful for debugging -->
<pre>{{ user | json }}</pre>

<!-- KeyValue - iterate objects/Maps -->
@for (item of obj | keyvalue; track item.key) {
  <p>{{ item.key }}: {{ item.value }}</p>
}

<!-- Async - handle Observables/Promises -->
{{ data$ | async }}

<!-- i18nSelect - select based on value -->
{{ gender | i18nSelect: {'male': 'Mr.', 'female': 'Ms.', 'other': 'Mx.'} }}

<!-- i18nPlural - pluralization -->
{{ count | i18nPlural: {'=0': 'No items', '=1': 'One item', 'other': '# items'} }}
```

**Quick Reference Table:**

| Pipe | Purpose | Example |
|------|---------|---------|
| `uppercase` | Text to uppercase | `{{ 'hi' \| uppercase }}` → HI |
| `lowercase` | Text to lowercase | `{{ 'HI' \| lowercase }}` → hi |
| `titlecase` | Capitalize words | `{{ 'hello world' \| titlecase }}` → Hello World |
| `date` | Format dates | `{{ date \| date:'short' }}` |
| `number` | Format numbers | `{{ 1234.5 \| number:'1.2-2' }}` |
| `currency` | Format currency | `{{ 99 \| currency:'USD' }}` |
| `percent` | Format percentage | `{{ 0.5 \| percent }}` → 50% |
| `json` | JSON stringify | `{{ obj \| json }}` |
| `slice` | Substring/subarray | `{{ arr \| slice:0:3 }}` |
| `async` | Unwrap Observable | `{{ obs$ \| async }}` |
| `keyvalue` | Object to array | `@for (kv of obj \| keyvalue)` |

---

## Q10: What are ng-template and ng-container? When do you use them?

**Answer:**
`ng-template` and `ng-container` are Angular structural elements that don't render to the DOM.

| ng-template | ng-container |
|-------------|--------------|
| Defines a template that's NOT rendered by default | Groups elements without adding DOM nodes |
| Used with structural directives | Useful when you can't add a wrapper element |
| Can be referenced with `TemplateRef` | Invisible grouping container |
| Holds content for lazy rendering | Works with structural directives |

**ng-template usage:**
```html
<!-- Not rendered until explicitly used -->
<ng-template #loading>
  <div class="spinner">Loading...</div>
</ng-template>

<!-- Used with *ngIf else -->
@if (data$ | async; as data) {
  <div>{{ data | json }}</div>
} @else {
  <ng-container *ngTemplateOutlet="loading"></ng-container>
}

<!-- Or with old syntax -->
<div *ngIf="data; else loading">{{ data }}</div>
<ng-template #loading>
  <p>Loading...</p>
</ng-template>
```

**ng-container usage:**
```html
<!-- Problem: Can't have multiple structural directives on one element -->
<!-- ❌ This doesn't work -->
<div *ngIf="show" *ngFor="let item of items">{{ item }}</div>

<!-- ✅ Solution: Use ng-container -->
<ng-container *ngIf="show">
  <div *ngFor="let item of items">{{ item }}</div>
</ng-container>

<!-- ng-container renders no DOM element -->
<ul>
  <ng-container *ngFor="let item of items">
    <li>{{ item.name }}</li>
    <li class="divider"></li>
  </ng-container>
</ul>
<!-- Renders as: <ul><li>A</li><li class="divider"></li>...</ul> -->
```

**Dynamic template rendering:**
```typescript
@Component({
  template: `
    <ng-container *ngTemplateOutlet="currentTemplate; context: {$implicit: data}">
    </ng-container>
    
    <ng-template #template1 let-item>
      <div class="card">{{ item.name }}</div>
    </ng-template>
    
    <ng-template #template2 let-item>
      <tr><td>{{ item.name }}</td></tr>
    </ng-template>
  `
})
export class DynamicComponent {
  @ViewChild('template1') template1!: TemplateRef<any>;
  @ViewChild('template2') template2!: TemplateRef<any>;
  
  data = { name: 'Angular' };
  isCardView = true;
  
  get currentTemplate(): TemplateRef<any> {
    return this.isCardView ? this.template1 : this.template2;
  }
}
```

**Creating reusable templates:**
```typescript
@Component({
  template: `
    <!-- Pass template as content projection -->
    <app-table [data]="items" [rowTemplate]="customRow">
    </app-table>
    
    <ng-template #customRow let-item let-index="index">
      <tr [class.even]="index % 2 === 0">
        <td>{{ index + 1 }}</td>
        <td>{{ item.name }}</td>
      </tr>
    </ng-template>
  `
})
export class ParentComponent {
  items = [{ name: 'A' }, { name: 'B' }];
}

// Table component receives template
@Component({
  selector: 'app-table',
  template: `
    <table>
      <ng-container *ngFor="let item of data; let i = index">
        <ng-container *ngTemplateOutlet="rowTemplate; context: {$implicit: item, index: i}">
        </ng-container>
      </ng-container>
    </table>
  `
})
export class TableComponent {
  @Input() data: any[] = [];
  @Input() rowTemplate!: TemplateRef<any>;
}
```

---

## Q11: How do structural directives work internally?

**Answer:**
Structural directives use `TemplateRef` and `ViewContainerRef` to manipulate the DOM.

**The asterisk (*) desugaring:**
```html
<!-- What you write -->
<div *ngIf="condition">Content</div>

<!-- What Angular creates -->
<ng-template [ngIf]="condition">
  <div>Content</div>
</ng-template>
```

**Internal mechanism:**
```typescript
@Directive({
  selector: '[appCustomIf]',
  standalone: true
})
export class CustomIfDirective {
  // TemplateRef - reference to the ng-template content
  private templateRef = inject(TemplateRef<any>);
  
  // ViewContainerRef - where to insert views
  private viewContainer = inject(ViewContainerRef);
  
  private hasView = false;
  
  @Input() set appCustomIf(condition: boolean) {
    if (condition && !this.hasView) {
      // Create embedded view from template
      this.viewContainer.createEmbeddedView(this.templateRef);
      this.hasView = true;
    } else if (!condition && this.hasView) {
      // Remove all views
      this.viewContainer.clear();
      this.hasView = false;
    }
  }
}
```

**Creating context for templates:**
```typescript
@Directive({
  selector: '[appRepeat]',
  standalone: true
})
export class RepeatDirective {
  private templateRef = inject(TemplateRef<any>);
  private viewContainer = inject(ViewContainerRef);
  
  @Input() set appRepeat(count: number) {
    this.viewContainer.clear();
    
    for (let i = 0; i < count; i++) {
      // Pass context to template
      this.viewContainer.createEmbeddedView(this.templateRef, {
        $implicit: i,      // let-variable without assignment
        index: i,          // let-index="index"
        first: i === 0,    // let-isFirst="first"
        last: i === count - 1
      });
    }
  }
}

// Usage
<div *appRepeat="5; let i; let isLast = last">
  Item {{ i }} {{ isLast ? '(last)' : '' }}
</div>
```

**Interview Tip:** Understanding the desugaring helps debug complex template issues and create custom structural directives.

---

## Q12: What is the difference between ngClass and ngStyle?

**Answer:**
Both are attribute directives for dynamic styling, but they work differently.

| ngClass | ngStyle |
|---------|---------|
| Adds/removes CSS classes | Sets inline styles |
| Works with CSS class names | Works with style properties |
| Better for predefined styles | Better for dynamic values |
| Multiple syntaxes | Object syntax |

**ngClass usage:**
```html
<!-- String syntax -->
<div [ngClass]="'active primary'">Multiple classes</div>

<!-- Array syntax -->
<div [ngClass]="['active', 'primary']">Array of classes</div>

<!-- Object syntax (most common) -->
<div [ngClass]="{
  'active': isActive,
  'disabled': isDisabled,
  'size-large': size === 'large'
}">Conditional classes</div>

<!-- Mixed -->
<div [ngClass]="['base', {'active': isActive}]">Mixed</div>
```

**ngStyle usage:**
```html
<!-- Object syntax -->
<div [ngStyle]="{
  'background-color': bgColor,
  'font-size.px': fontSize,
  'width.%': widthPercent
}">Styled div</div>

<!-- With units -->
<div [ngStyle]="{
  'margin.px': 10,
  'padding.em': 2,
  'width.%': 50
}">With units</div>
```

**Best practices:**
```html
<!-- ✅ Prefer ngClass for predefined styles -->
<button [ngClass]="{'btn-primary': isPrimary, 'btn-lg': isLarge}">

<!-- ✅ Use ngStyle for truly dynamic values -->
<div [ngStyle]="{'left.px': xPosition, 'top.px': yPosition}">
  Positioned element
</div>

<!-- ❌ Avoid ngStyle for values that could be classes -->
<div [ngStyle]="{'background-color': isActive ? 'green' : 'red'}">
<!-- ✅ Better: use class -->
<div [ngClass]="{'active': isActive, 'inactive': !isActive}">
```

---

## Q13: How do you pass data to a custom directive?

**Answer:**
Custom directives receive data through `@Input()` properties, similar to components.

```typescript
@Directive({
  selector: '[appTooltip]',
  standalone: true
})
export class TooltipDirective {
  // Primary input - same name as selector
  @Input() appTooltip = '';
  
  // Additional inputs with prefix convention
  @Input() appTooltipPosition: 'top' | 'bottom' | 'left' | 'right' = 'top';
  @Input() appTooltipDelay = 200;
  
  // Or use alias
  @Input('appTooltipClass') tooltipClass = '';
  
  @HostListener('mouseenter')
  show(): void {
    console.log(`Showing: ${this.appTooltip} at ${this.appTooltipPosition}`);
  }
}
```

**Usage:**
```html
<!-- Primary input -->
<button appTooltip="Click me!">Hover</button>

<!-- With additional inputs -->
<button 
  [appTooltip]="tooltipText"
  appTooltipPosition="bottom"
  [appTooltipDelay]="500"
  appTooltipClass="custom-tooltip">
  Hover me
</button>
```

**Input with setter for reactive behavior:**
```typescript
@Directive({
  selector: '[appHighlight]',
  standalone: true
})
export class HighlightDirective {
  private el = inject(ElementRef);
  
  @Input() set appHighlight(color: string) {
    this.el.nativeElement.style.backgroundColor = color || 'yellow';
  }
  
  @Input() set highlightOnCondition(condition: boolean) {
    this.el.nativeElement.style.display = condition ? 'block' : 'none';
  }
}
```

---

## Q14: What is the difference between Renderer2 and ElementRef for DOM manipulation?

**Answer:**
Both are used for DOM manipulation in directives, but with important differences.

| ElementRef | Renderer2 |
|------------|-----------|
| Direct DOM access | Abstraction layer |
| `nativeElement` property | Methods like `setStyle`, `addClass` |
| Security risk (XSS) | Safe - no direct DOM access |
| Platform specific | Platform agnostic (SSR compatible) |
| Simple but risky | Recommended approach |

```typescript
@Directive({
  selector: '[appSafeStyle]',
  standalone: true
})
export class SafeStyleDirective {
  private el = inject(ElementRef);
  private renderer = inject(Renderer2);
  
  // ❌ Direct DOM access - avoid in production
  unsafeApproach(): void {
    this.el.nativeElement.style.color = 'red';
    this.el.nativeElement.innerHTML = '<b>Unsafe!</b>';  // XSS risk!
  }
  
  // ✅ Renderer2 - safe and platform agnostic
  safeApproach(): void {
    // Set style
    this.renderer.setStyle(this.el.nativeElement, 'color', 'red');
    
    // Add/remove class
    this.renderer.addClass(this.el.nativeElement, 'active');
    this.renderer.removeClass(this.el.nativeElement, 'inactive');
    
    // Set attribute
    this.renderer.setAttribute(this.el.nativeElement, 'aria-label', 'Button');
    
    // Set property
    this.renderer.setProperty(this.el.nativeElement, 'disabled', true);
    
    // Create and append elements
    const span = this.renderer.createElement('span');
    const text = this.renderer.createText('Hello');
    this.renderer.appendChild(span, text);
    this.renderer.appendChild(this.el.nativeElement, span);
    
    // Listen to events
    const unlisten = this.renderer.listen(this.el.nativeElement, 'click', (event) => {
      console.log('Clicked!', event);
    });
    // Call unlisten() to remove listener
  }
}
```

**When to use each:**
```typescript
// ✅ ElementRef for reading (not modifying)
@Directive({...})
export class MeasureDirective implements AfterViewInit {
  private el = inject(ElementRef);
  
  ngAfterViewInit(): void {
    const width = this.el.nativeElement.offsetWidth;  // Reading is OK
    console.log('Element width:', width);
  }
}

// ✅ Renderer2 for modifications
@Directive({...})
export class ModifyDirective {
  private el = inject(ElementRef);
  private renderer = inject(Renderer2);
  
  @HostListener('mouseenter')
  onEnter(): void {
    this.renderer.setStyle(this.el.nativeElement, 'transform', 'scale(1.1)');
  }
}
```

**Interview Tip:** Always mention SSR (Server-Side Rendering) when discussing Renderer2 - it works in environments where there's no DOM.

---

## Quick Reference Card

| Topic | Key Points |
|-------|------------|
| **Directive Types** | Component, Structural (*), Attribute |
| **Structural Directives** | `*ngIf`, `*ngFor`, `*ngSwitch` - modify DOM structure |
| **Attribute Directives** | `ngClass`, `ngStyle`, custom - modify appearance |
| **Custom Directive** | `@Directive`, `ElementRef`, `Renderer2` |
| **@HostListener** | Listen to host element events |
| **@HostBinding** | Bind to host element properties |
| **Pure Pipe** | Default, cached, runs on reference change |
| **Impure Pipe** | `pure: false`, runs every CD cycle |
| **Async Pipe** | Auto subscribe/unsubscribe, works with OnPush |
| **Built-in Pipes** | `date`, `currency`, `number`, `json`, `async` |
| **ng-template** | Defines template, not rendered by default |
| **ng-container** | Groups elements, no DOM node |
| **TemplateRef** | Reference to ng-template content |
| **ViewContainerRef** | Container for inserting views |
| **Renderer2** | Safe DOM manipulation (SSR compatible) |

---

## Common Interview Scenarios

**Scenario 1: "Create a directive that shows a tooltip on hover"**
```typescript
@Directive({ selector: '[appTooltip]', standalone: true })
export class TooltipDirective {
  @Input() appTooltip = '';
  private renderer = inject(Renderer2);
  private el = inject(ElementRef);
  private tooltipEl: HTMLElement | null = null;
  
  @HostListener('mouseenter') show() {
    this.tooltipEl = this.renderer.createElement('div');
    this.renderer.appendChild(this.tooltipEl, this.renderer.createText(this.appTooltip));
    this.renderer.addClass(this.tooltipEl, 'tooltip');
    this.renderer.appendChild(this.el.nativeElement, this.tooltipEl);
  }
  
  @HostListener('mouseleave') hide() {
    if (this.tooltipEl) this.renderer.removeChild(this.el.nativeElement, this.tooltipEl);
  }
}
```

**Scenario 2: "Create a pipe that formats phone numbers"**
```typescript
@Pipe({ name: 'phone', standalone: true })
export class PhonePipe implements PipeTransform {
  transform(value: string): string {
    if (!value) return '';
    const cleaned = value.replace(/\D/g, '');
    const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);
    return match ? `(${match[1]}) ${match[2]}-${match[3]}` : value;
  }
}
// Usage: {{ '1234567890' | phone }}  → "(123) 456-7890"
```
