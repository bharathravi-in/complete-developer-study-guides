# Day 4: Interview Q&A – Templates & Data Binding

## Q1: What are the different types of data binding in Angular?

**Answer:**
Angular supports four types of data binding:

1. **Interpolation** `{{ }}` - Component → Template (one-way)
   ```html
   <p>{{ userName }}</p>
   ```

2. **Property Binding** `[]` - Component → Template (one-way)
   ```html
   <img [src]="imageUrl">
   <button [disabled]="isDisabled">
   ```

3. **Event Binding** `()` - Template → Component (one-way)
   ```html
   <button (click)="handleClick()">
   ```

4. **Two-way Binding** `[()]` - Both directions
   ```html
   <input [(ngModel)]="name">
   ```

---

## Q2: What is the difference between Property Binding and Attribute Binding?

**Answer:**

| Property Binding | Attribute Binding |
|------------------|-------------------|
| Sets DOM property | Sets HTML attribute |
| `[property]="value"` | `[attr.attribute]="value"` |
| For standard DOM properties | For non-standard attributes |
| Updates dynamically | Initial value only |

```html
<!-- Property binding -->
<input [value]="name">
<button [disabled]="isDisabled">

<!-- Attribute binding (when no DOM property exists) -->
<td [attr.colspan]="span">
<div [attr.aria-label]="label">
<svg [attr.width]="w">
```

**Use attribute binding for:**
- ARIA attributes
- SVG attributes
- Custom data attributes
- `colspan`, `rowspan`

---

## Q3: What is trackBy and why is it important?

**Answer:**
`trackBy` is a function that tells Angular how to identify items in an `*ngFor` loop.

**Without trackBy:**
- Angular tracks items by object identity
- Full DOM re-render when array reference changes
- Poor performance with large lists

**With trackBy:**
- Angular tracks by unique identifier
- Only changed items are re-rendered
- Significant performance improvement

```typescript
// Component
items = [
  { id: 1, name: 'Item 1' },
  { id: 2, name: 'Item 2' }
];

trackById(index: number, item: Item): number {
  return item.id;
}
```

```html
<!-- Template -->
<div *ngFor="let item of items; trackBy: trackById">
  {{ item.name }}
</div>

<!-- New syntax (Angular 17+) -->
@for (item of items; track item.id) {
  <div>{{ item.name }}</div>
}
```

---

## Q4: What is ng-container and when should you use it?

**Answer:**
`ng-container` is a grouping element that doesn't render to the DOM.

**Use cases:**

1. **Multiple structural directives:**
```html
<!-- ❌ Can't have two structural directives on one element -->
<div *ngIf="condition" *ngFor="let item of items">

<!-- ✅ Use ng-container -->
<ng-container *ngFor="let item of items">
  <div *ngIf="item.active">{{ item.name }}</div>
</ng-container>
```

2. **Conditional content without wrapper:**
```html
<!-- ❌ Adds extra span to DOM -->
<span *ngIf="condition">{{ text }}</span>

<!-- ✅ No extra element -->
<ng-container *ngIf="condition">{{ text }}</ng-container>
```

3. **Template outlet:**
```html
<ng-container *ngTemplateOutlet="template"></ng-container>
```

---

## Q5: Explain the difference between *ngIf and [hidden].

**Answer:**

| *ngIf | [hidden] |
|-------|----------|
| Removes from DOM | Hides with CSS |
| Destroys component | Component stays alive |
| No memory usage | Memory still used |
| Triggers lifecycle | No lifecycle changes |
| Performance (large) | Performance (toggle frequent) |

```html
<!-- *ngIf - Removes from DOM -->
<div *ngIf="isVisible">Content</div>

<!-- [hidden] - CSS display: none -->
<div [hidden]="!isVisible">Content</div>
```

**Choose *ngIf when:**
- Heavy components (free resources)
- Security (hide sensitive data)
- Complex initialization needed

**Choose [hidden] when:**
- Frequent toggling
- Preserve component state
- Quick show/hide animations

---

## Q6: What is the new control flow syntax in Angular 17+?

**Answer:**
Angular 17 introduced built-in control flow syntax:

**@if (replaces *ngIf):**
```html
@if (user) {
  <p>Hello {{ user.name }}</p>
} @else if (guest) {
  <p>Hello Guest</p>
} @else {
  <p>Please log in</p>
}
```

**@for (replaces *ngFor):**
```html
@for (item of items; track item.id) {
  <div>{{ item.name }}</div>
} @empty {
  <p>No items found</p>
}
```

**@switch (replaces ngSwitch):**
```html
@switch (status) {
  @case ('loading') { <p>Loading...</p> }
  @case ('error') { <p>Error!</p> }
  @default { <p>Ready</p> }
}
```

**@defer (NEW - lazy loading):**
```html
@defer (on viewport) {
  <app-heavy-component />
} @loading {
  <spinner />
}
```

**Benefits:**
- Better performance
- No imports needed
- Built-in @empty/@loading
- Better type checking

---

## Q7: What is @defer and how does it work?

**Answer:**
`@defer` is Angular 17's built-in lazy loading for template content.

**Triggers:**
- `on viewport` - When visible in viewport
- `on interaction` - On user interaction (click, focus)
- `on idle` - When browser is idle
- `on timer(Xms)` - After specified time
- `when condition` - When condition is true

```html
@defer (on viewport) {
  <app-chart />
} @loading (minimum 500ms) {
  <p>Loading chart...</p>
} @error {
  <p>Failed to load</p>
} @placeholder {
  <p>Chart will appear here</p>
}
```

**Prefetching:**
```html
@defer (on interaction; prefetch on idle) {
  <app-heavy-component />
}
```

---

## Q8: How do you create a custom attribute directive?

**Answer:**

```typescript
import { Directive, ElementRef, HostListener, Input, inject } from '@angular/core';

@Directive({
  selector: '[appTooltip]',
  standalone: true
})
export class TooltipDirective {
  private el = inject(ElementRef);
  private tooltipEl: HTMLElement | null = null;
  
  @Input() appTooltip = '';
  @Input() tooltipPosition = 'top';
  
  @HostListener('mouseenter')
  onMouseEnter(): void {
    this.showTooltip();
  }
  
  @HostListener('mouseleave')
  onMouseLeave(): void {
    this.hideTooltip();
  }
  
  private showTooltip(): void {
    this.tooltipEl = document.createElement('div');
    this.tooltipEl.textContent = this.appTooltip;
    this.tooltipEl.className = `tooltip tooltip-${this.tooltipPosition}`;
    document.body.appendChild(this.tooltipEl);
    // Position tooltip...
  }
  
  private hideTooltip(): void {
    this.tooltipEl?.remove();
  }
}
```

```html
<button [appTooltip]="'Click to save'" tooltipPosition="bottom">
  Save
</button>
```

---

## Q9: What is the $event object in event binding?

**Answer:**
`$event` is the native DOM event or custom event payload.

```typescript
@Component({
  template: `
    <!-- DOM events - $event is native Event -->
    <input (input)="onInput($event)">
    <button (click)="onClick($event)">
    
    <!-- Custom events - $event is emitted value -->
    <app-child (notify)="onNotify($event)"></app-child>
  `
})
export class DemoComponent {
  onInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    console.log(input.value);
  }
  
  onClick(event: MouseEvent): void {
    console.log(event.clientX, event.clientY);
    event.preventDefault();
  }
  
  onNotify(data: NotifyPayload): void {
    console.log(data);
  }
}
```

**Keyboard events with filters:**
```html
<input (keyup.enter)="onEnter()">
<input (keydown.control.s)="onSave()">
<input (keyup.escape)="onCancel()">
```

---

## Q10: How does ngModel work internally?

**Answer:**
`ngModel` combines property binding and event binding:

```html
<!-- Two-way binding -->
<input [(ngModel)]="name">

<!-- Desugared form -->
<input [ngModel]="name" (ngModelChange)="name = $event">
```

**Internal mechanism:**
1. `ngModel` directive listens to input events
2. On input, emits `ngModelChange` with new value
3. Property binding updates when model changes
4. Supports forms validation via `ControlValueAccessor`

**Requirements:**
```typescript
import { FormsModule } from '@angular/forms';

@Component({
  imports: [FormsModule]  // Required for ngModel
})
```

**Custom two-way binding pattern:**
```typescript
// Convention: property + propertyChange
@Input() value = '';
@Output() valueChange = new EventEmitter<string>();
```

---

## Quick Reference Card

| Topic | Syntax | Use Case |
|-------|--------|----------|
| Interpolation | `{{ expr }}` | Display values |
| Property | `[prop]="val"` | Set DOM properties |
| Attribute | `[attr.x]="val"` | Set HTML attributes |
| Event | `(event)="fn()"` | Handle user actions |
| Two-way | `[(ngModel)]="val"` | Form inputs |
| Class | `[class.x]="cond"` | Conditional classes |
| Style | `[style.x]="val"` | Dynamic styles |
| trackBy | `trackBy: fn` | Optimize lists |
| ng-container | `<ng-container>` | No DOM wrapper |
| @if | `@if (cond) { }` | Conditional rendering |
| @for | `@for (i of items; track i.id)` | Iteration |
| @defer | `@defer { }` | Lazy loading |
