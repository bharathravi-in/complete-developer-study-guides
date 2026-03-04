# Day 4: Templates & Data Binding

## Table of Contents
1. [Interpolation](#1-interpolation)
2. [Property Binding](#2-property-binding)
3. [Event Binding](#3-event-binding)
4. [Two-Way Binding](#4-two-way-binding)
5. [Structural Directives](#5-structural-directives)
6. [Attribute Directives](#6-attribute-directives)
7. [Control Flow (Angular 17+)](#7-control-flow-angular-17)

---

## 1. Interpolation

Interpolation embeds expressions into text content using `{{ }}`.

```html
<!-- Basic interpolation -->
<h1>{{ title }}</h1>
<p>Hello, {{ user.name }}!</p>

<!-- Expressions -->
<p>Total: {{ price * quantity }}</p>
<p>Full Name: {{ firstName + ' ' + lastName }}</p>

<!-- Method calls (use sparingly - runs every CD) -->
<p>{{ getFormattedDate() }}</p>

<!-- Ternary operator -->
<p>Status: {{ isActive ? 'Active' : 'Inactive' }}</p>

<!-- Safe navigation operator -->
<p>{{ user?.address?.city }}</p>

<!-- Pipes -->
<p>{{ price | currency:'USD' }}</p>
<p>{{ date | date:'fullDate' }}</p>
<p>{{ name | uppercase }}</p>
```

### What CAN'T be used in interpolation:
- Assignments: `{{ x = 5 }}`
- `new` keyword: `{{ new Date() }}`
- Chaining with `;`: `{{ a; b }}`
- Increment/decrement: `{{ i++ }}`

---

## 2. Property Binding

Property binding sets element/directive/component properties using `[property]`.

```html
<!-- DOM property binding -->
<img [src]="imageUrl" [alt]="imageDescription">
<button [disabled]="isDisabled">Submit</button>
<div [hidden]="!isVisible">Content</div>

<!-- Component property binding -->
<app-user [user]="selectedUser" [showAvatar]="true"></app-user>

<!-- Attribute binding (when no DOM property exists) -->
<td [attr.colspan]="columnSpan">Data</td>
<div [attr.aria-label]="description">Accessible</div>
<svg>
  <circle [attr.cx]="x" [attr.cy]="y" [attr.r]="radius"></circle>
</svg>

<!-- Class binding -->
<div [class.active]="isActive">Single class</div>
<div [class]="classString">String: 'class1 class2'</div>
<div [class]="classArray">Array: ['class1', 'class2']</div>
<div [class]="classObject">Object: {class1: true, class2: false}</div>

<!-- Style binding -->
<div [style.width.px]="width">Sized</div>
<div [style.background-color]="bgColor">Colored</div>
<div [style]="styleObject">Object: {width: '100px', color: 'red'}</div>
```

### Property vs Attribute

```html
<!-- Property (DOM property) -->
<input [value]="name">

<!-- Attribute (HTML attribute) -->
<input [attr.value]="name">

<!-- Key difference: -->
<!-- Property: Updates DOM property (what JavaScript sees) -->
<!-- Attribute: Sets HTML attribute (initial value only) -->
```

---

## 3. Event Binding

Event binding responds to user actions using `(event)`.

```typescript
@Component({
  template: `
    <!-- Basic events -->
    <button (click)="onClick()">Click Me</button>
    <input (input)="onInput($event)" (blur)="onBlur()">
    <form (submit)="onSubmit($event)">...</form>
    
    <!-- $event object -->
    <input (keyup)="onKey($event)">
    <input (keyup.enter)="onEnter()">  <!-- Key filter -->
    <input (keyup.escape)="onEscape()">
    
    <!-- Mouse events -->
    <div 
      (mouseenter)="onMouseEnter()"
      (mouseleave)="onMouseLeave()"
      (mousemove)="onMouseMove($event)">
      Hover me
    </div>
    
    <!-- Keyboard modifiers -->
    <input (keydown.control.a)="selectAll()">
    <input (keydown.shift.enter)="submitForm()">
    
    <!-- Custom component events -->
    <app-child (notify)="onNotify($event)"></app-child>
  `
})
export class EventDemoComponent {
  onClick(): void {
    console.log('Clicked!');
  }
  
  onInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    console.log(input.value);
  }
  
  onKey(event: KeyboardEvent): void {
    console.log(event.key);
  }
  
  onSubmit(event: Event): void {
    event.preventDefault();
    // Handle form submission
  }
}
```

### Template Statements

```html
<!-- Multiple statements -->
<button (click)="count = count + 1; logCount()">Increment</button>

<!-- Inline expression -->
<button (click)="showDetails = !showDetails">Toggle</button>

<!-- Pass data -->
<li *ngFor="let item of items">
  <button (click)="selectItem(item)">{{ item.name }}</button>
</li>
```

---

## 4. Two-Way Binding

Two-way binding syncs data between component and template using `[()]`.

```typescript
import { FormsModule } from '@angular/forms';

@Component({
  standalone: true,
  imports: [FormsModule],
  template: `
    <!-- ngModel for form elements -->
    <input [(ngModel)]="name" placeholder="Name">
    <p>Hello, {{ name }}!</p>
    
    <!-- Equivalent to: -->
    <input [ngModel]="name" (ngModelChange)="name = $event">
    
    <!-- Select -->
    <select [(ngModel)]="selectedCountry">
      <option *ngFor="let c of countries" [value]="c.code">
        {{ c.name }}
      </option>
    </select>
    
    <!-- Checkbox -->
    <input type="checkbox" [(ngModel)]="isSubscribed">
    <label>Subscribe to newsletter</label>
    
    <!-- Radio buttons -->
    <input type="radio" [(ngModel)]="gender" value="male"> Male
    <input type="radio" [(ngModel)]="gender" value="female"> Female
    
    <!-- Textarea -->
    <textarea [(ngModel)]="message"></textarea>
  `
})
export class TwoWayComponent {
  name = '';
  selectedCountry = 'US';
  isSubscribed = false;
  gender = '';
  message = '';
  countries = [
    { code: 'US', name: 'United States' },
    { code: 'UK', name: 'United Kingdom' }
  ];
}
```

### Custom Two-Way Binding

```typescript
// Child component
@Component({
  selector: 'app-slider',
  template: `
    <input 
      type="range" 
      [min]="min" 
      [max]="max" 
      [value]="value"
      (input)="onSlide($event)">
  `
})
export class SliderComponent {
  @Input() value = 0;
  @Input() min = 0;
  @Input() max = 100;
  @Output() valueChange = new EventEmitter<number>();
  
  onSlide(event: Event): void {
    const val = +(event.target as HTMLInputElement).value;
    this.valueChange.emit(val);
  }
}

// Parent usage
@Component({
  template: `
    <app-slider [(value)]="volume"></app-slider>
    <p>Volume: {{ volume }}</p>
  `
})
export class ParentComponent {
  volume = 50;
}
```

---

## 5. Structural Directives

Structural directives change DOM structure with `*prefix`.

### *ngIf

```html
<!-- Basic ngIf -->
<div *ngIf="isVisible">Shown when true</div>

<!-- With else -->
<div *ngIf="user; else noUser">
  Welcome, {{ user.name }}!
</div>
<ng-template #noUser>
  <p>Please log in.</p>
</ng-template>

<!-- With then and else -->
<div *ngIf="condition; then thenBlock; else elseBlock"></div>
<ng-template #thenBlock>Then content</ng-template>
<ng-template #elseBlock>Else content</ng-template>

<!-- Store value in variable -->
<div *ngIf="users$ | async as users">
  <div *ngFor="let user of users">{{ user.name }}</div>
</div>
```

### *ngFor

```html
<!-- Basic loop -->
<ul>
  <li *ngFor="let item of items">{{ item.name }}</li>
</ul>

<!-- With index and other variables -->
<div *ngFor="let item of items; 
             let i = index; 
             let first = first;
             let last = last;
             let even = even;
             let odd = odd">
  <p [class.highlight]="first">
    {{ i + 1 }}. {{ item.name }}
  </p>
</div>

<!-- With trackBy (IMPORTANT for performance) -->
<div *ngFor="let item of items; trackBy: trackById">
  {{ item.name }}
</div>
```

```typescript
// Component
trackById(index: number, item: Item): number {
  return item.id;
}
```

### *ngSwitch

```html
<div [ngSwitch]="userRole">
  <p *ngSwitchCase="'admin'">Admin Dashboard</p>
  <p *ngSwitchCase="'editor'">Editor Panel</p>
  <p *ngSwitchCase="'viewer'">View Mode</p>
  <p *ngSwitchDefault>Guest Access</p>
</div>
```

### ng-container (No Extra DOM Element)

```html
<!-- ng-container doesn't render to DOM -->
<ng-container *ngIf="user">
  <span>{{ user.name }}</span>
  <span>{{ user.email }}</span>
</ng-container>

<!-- Useful for multiple structural directives -->
<ng-container *ngFor="let item of items">
  <ng-container *ngIf="item.active">
    <div>{{ item.name }}</div>
  </ng-container>
</ng-container>
```

---

## 6. Attribute Directives

Attribute directives change appearance or behavior of elements.

### Built-in Attribute Directives

```html
<!-- ngClass -->
<div [ngClass]="'class1 class2'">String</div>
<div [ngClass]="['class1', 'class2']">Array</div>
<div [ngClass]="{ active: isActive, disabled: isDisabled }">Object</div>

<!-- ngStyle -->
<div [ngStyle]="{ 'color': textColor, 'font-size.px': fontSize }">
  Styled text
</div>

<!-- Combining with conditions -->
<div 
  [ngClass]="{ 
    'success': status === 'success',
    'error': status === 'error',
    'warning': status === 'warning'
  }"
  [ngStyle]="{
    'border-color': status === 'error' ? 'red' : 'green'
  }">
  Status: {{ status }}
</div>
```

### Custom Attribute Directive

```typescript
import { Directive, ElementRef, HostListener, Input, inject } from '@angular/core';

@Directive({
  selector: '[appHighlight]',
  standalone: true
})
export class HighlightDirective {
  private el = inject(ElementRef);
  
  @Input() appHighlight = 'yellow';  // Default color
  @Input() highlightTextColor = 'black';
  
  @HostListener('mouseenter')
  onMouseEnter(): void {
    this.highlight(this.appHighlight, this.highlightTextColor);
  }
  
  @HostListener('mouseleave')
  onMouseLeave(): void {
    this.highlight('', '');
  }
  
  private highlight(bgColor: string, textColor: string): void {
    this.el.nativeElement.style.backgroundColor = bgColor;
    this.el.nativeElement.style.color = textColor;
  }
}

// Usage
@Component({
  imports: [HighlightDirective],
  template: `
    <p appHighlight>Yellow highlight (default)</p>
    <p [appHighlight]="'lightblue'" highlightTextColor="white">
      Blue highlight
    </p>
  `
})
```

---

## 7. Control Flow (Angular 17+)

New built-in control flow syntax (replaces structural directives).

### @if

```html
<!-- Basic @if -->
@if (isLoggedIn) {
  <p>Welcome, {{ user.name }}!</p>
}

<!-- @if with @else -->
@if (user) {
  <p>Hello, {{ user.name }}</p>
} @else {
  <p>Please log in</p>
}

<!-- @if with @else if -->
@if (status === 'loading') {
  <p>Loading...</p>
} @else if (status === 'error') {
  <p>Error occurred</p>
} @else {
  <p>Data loaded</p>
}
```

### @for

```html
<!-- Basic @for -->
@for (item of items; track item.id) {
  <div>{{ item.name }}</div>
}

<!-- With index and other variables -->
@for (item of items; track item.id; let idx = $index, first = $first, last = $last) {
  <div [class.first]="first" [class.last]="last">
    {{ idx + 1 }}. {{ item.name }}
  </div>
}

<!-- @empty block -->
@for (item of items; track item.id) {
  <div>{{ item.name }}</div>
} @empty {
  <p>No items found</p>
}

<!-- Available variables in @for -->
<!-- $index, $first, $last, $even, $odd, $count -->
```

### @switch

```html
@switch (userRole) {
  @case ('admin') {
    <app-admin-dashboard />
  }
  @case ('editor') {
    <app-editor-panel />
  }
  @case ('viewer') {
    <app-viewer-mode />
  }
  @default {
    <app-guest-access />
  }
}
```

### @defer (Lazy Loading)

```html
<!-- Basic defer -->
@defer {
  <app-heavy-component />
}

<!-- With loading and error states -->
@defer {
  <app-heavy-component />
} @loading {
  <p>Loading component...</p>
} @error {
  <p>Failed to load</p>
} @placeholder {
  <p>Placeholder content</p>
}

<!-- With conditions -->
@defer (on viewport) {
  <app-lazy-component />
}

@defer (on interaction) {
  <app-lazy-component />
}

@defer (on idle) {
  <app-lazy-component />
}

@defer (on timer(2s)) {
  <app-lazy-component />
}

@defer (when isReady) {
  <app-lazy-component />
}

<!-- With minimum time (prevents flash) -->
@defer {
  <app-component />
} @loading (minimum 500ms) {
  <spinner />
}
```

---

## Comparison: Old vs New Syntax

| Old (Directives) | New (Control Flow) |
|------------------|-------------------|
| `*ngIf="cond"` | `@if (cond) { }` |
| `*ngIf="cond; else temp"` | `@if (cond) { } @else { }` |
| `*ngFor="let i of items"` | `@for (i of items; track i.id) { }` |
| `[ngSwitch]` | `@switch (val) { }` |
| No equivalent | `@defer { }` |

### Why New Syntax?

1. **Better performance** - Optimized compilation
2. **Simpler** - No need for ng-container
3. **Built-in** - No imports needed
4. **Type-safe** - Better type checking
5. **@defer** - Native lazy loading

---

## Summary

| Binding Type | Syntax | Direction |
|--------------|--------|-----------|
| Interpolation | `{{ value }}` | Component → DOM |
| Property | `[property]="value"` | Component → DOM |
| Event | `(event)="handler()"` | DOM → Component |
| Two-way | `[(ngModel)]="value"` | Both ways |
| Class | `[class.name]="cond"` | Component → DOM |
| Style | `[style.prop]="value"` | Component → DOM |
| Attribute | `[attr.name]="value"` | Component → DOM |

---

## Next Steps
- Practice control flow syntax with different conditions
- Create custom attribute directives
- Build forms with two-way binding
