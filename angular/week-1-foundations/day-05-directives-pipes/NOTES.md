# Day 5: Directives & Pipes

## Table of Contents
1. [Directive Types](#1-directive-types)
2. [Custom Directives](#2-custom-directives)
3. [Built-in Pipes](#3-built-in-pipes)
4. [Pure vs Impure Pipes](#4-pure-vs-impure-pipes)
5. [Custom Pipes](#5-custom-pipes)
6. [Async Pipe](#6-async-pipe)

---

## 1. Directive Types

Angular has three types of directives:

```
┌─────────────────────────────────────────────────────────────┐
│                    DIRECTIVE TYPES                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Component Directives                                     │
│     - Directives with a template                            │
│     - @Component decorator                                   │
│                                                              │
│  2. Structural Directives                                    │
│     - Change DOM structure                                   │
│     - *ngIf, *ngFor, *ngSwitch                              │
│     - Prefix: * (asterisk)                                   │
│                                                              │
│  3. Attribute Directives                                     │
│     - Change appearance/behavior                             │
│     - ngClass, ngStyle, custom                              │
│     - No prefix                                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Custom Directives

### Attribute Directive

```typescript
import { 
  Directive, 
  ElementRef, 
  HostListener, 
  HostBinding,
  Input, 
  Output,
  EventEmitter,
  OnInit,
  inject 
} from '@angular/core';

// Basic highlight directive
@Directive({
  selector: '[appHighlight]',
  standalone: true
})
export class HighlightDirective implements OnInit {
  private el = inject(ElementRef);
  
  @Input() appHighlight = 'yellow';
  @Input() defaultColor = '';
  
  @HostBinding('style.backgroundColor') bgColor = '';
  
  ngOnInit(): void {
    this.bgColor = this.defaultColor || this.appHighlight;
  }
  
  @HostListener('mouseenter')
  onMouseEnter(): void {
    this.bgColor = this.appHighlight;
  }
  
  @HostListener('mouseleave')
  onMouseLeave(): void {
    this.bgColor = this.defaultColor;
  }
}
```

### Directive with Events

```typescript
@Directive({
  selector: '[appClickTracker]',
  standalone: true
})
export class ClickTrackerDirective {
  private el = inject(ElementRef);
  private clickCount = 0;
  
  @Output() clickCountChange = new EventEmitter<number>();
  @Output() doubleClicked = new EventEmitter<void>();
  
  private lastClickTime = 0;
  
  @HostListener('click', ['$event'])
  onClick(event: MouseEvent): void {
    this.clickCount++;
    this.clickCountChange.emit(this.clickCount);
    
    const now = Date.now();
    if (now - this.lastClickTime < 300) {
      this.doubleClicked.emit();
    }
    this.lastClickTime = now;
  }
  
  @HostListener('document:keydown.escape')
  onEscape(): void {
    this.clickCount = 0;
    this.clickCountChange.emit(this.clickCount);
  }
}
```

### Structural Directive

```typescript
import { 
  Directive, 
  Input, 
  TemplateRef, 
  ViewContainerRef,
  inject,
  OnChanges,
  SimpleChanges
} from '@angular/core';

// Custom *appUnless directive (opposite of *ngIf)
@Directive({
  selector: '[appUnless]',
  standalone: true
})
export class UnlessDirective implements OnChanges {
  private templateRef = inject(TemplateRef<any>);
  private viewContainer = inject(ViewContainerRef);
  
  @Input() appUnless = false;
  
  private hasView = false;
  
  ngOnChanges(changes: SimpleChanges): void {
    if ('appUnless' in changes) {
      this.updateView();
    }
  }
  
  private updateView(): void {
    if (!this.appUnless && !this.hasView) {
      this.viewContainer.createEmbeddedView(this.templateRef);
      this.hasView = true;
    } else if (this.appUnless && this.hasView) {
      this.viewContainer.clear();
      this.hasView = false;
    }
  }
}

// Usage
// <p *appUnless="isHidden">Shown when isHidden is false</p>
```

### Repeat Directive

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
      this.viewContainer.createEmbeddedView(this.templateRef, {
        $implicit: i,
        index: i,
        first: i === 0,
        last: i === count - 1
      });
    }
  }
}

// Usage
// <div *appRepeat="5; let i">Item {{ i }}</div>
```

---

## 3. Built-in Pipes

### Text Pipes

```html
<!-- uppercase / lowercase -->
<p>{{ 'hello' | uppercase }}</p>  <!-- HELLO -->
<p>{{ 'HELLO' | lowercase }}</p>  <!-- hello -->

<!-- titlecase -->
<p>{{ 'hello world' | titlecase }}</p>  <!-- Hello World -->

<!-- slice -->
<p>{{ 'Angular' | slice:0:3 }}</p>  <!-- Ang -->
<p>{{ 'Angular' | slice:3 }}</p>    <!-- ular -->
```

### Number Pipes

```html
<!-- number: 'minInt.minFrac-maxFrac' -->
<p>{{ 3.14159 | number:'1.2-4' }}</p>  <!-- 3.1416 -->
<p>{{ 1234.5 | number:'1.0-0' }}</p>   <!-- 1,235 -->

<!-- currency -->
<p>{{ 99.99 | currency }}</p>              <!-- $99.99 -->
<p>{{ 99.99 | currency:'EUR' }}</p>        <!-- €99.99 -->
<p>{{ 99.99 | currency:'INR':'symbol' }}</p> <!-- ₹99.99 -->

<!-- percent -->
<p>{{ 0.85 | percent }}</p>          <!-- 85% -->
<p>{{ 0.8567 | percent:'1.2-2' }}</p> <!-- 85.67% -->
```

### Date Pipe

```html
<!-- Basic formats -->
<p>{{ today | date }}</p>              <!-- Mar 15, 2024 -->
<p>{{ today | date:'short' }}</p>      <!-- 3/15/24, 10:30 AM -->
<p>{{ today | date:'medium' }}</p>     <!-- Mar 15, 2024, 10:30:00 AM -->
<p>{{ today | date:'long' }}</p>       <!-- March 15, 2024, 10:30:00 AM GMT -->
<p>{{ today | date:'full' }}</p>       <!-- Friday, March 15, 2024 -->

<!-- Custom formats -->
<p>{{ today | date:'yyyy-MM-dd' }}</p>      <!-- 2024-03-15 -->
<p>{{ today | date:'dd/MM/yyyy' }}</p>      <!-- 15/03/2024 -->
<p>{{ today | date:'EEEE, MMM d, y' }}</p>  <!-- Friday, Mar 15, 2024 -->
<p>{{ today | date:'HH:mm:ss' }}</p>        <!-- 14:30:00 -->
<p>{{ today | date:'h:mm a' }}</p>          <!-- 2:30 PM -->

<!-- With timezone -->
<p>{{ today | date:'short':'UTC' }}</p>
<p>{{ today | date:'short':'+0530' }}</p>
```

### JSON Pipe

```html
<!-- Useful for debugging -->
<pre>{{ user | json }}</pre>
<!-- Output: 
{
  "name": "John",
  "age": 30
}
-->
```

### KeyValue Pipe

```html
<!-- Iterate over objects -->
@for (item of obj | keyvalue; track item.key) {
  <p>{{ item.key }}: {{ item.value }}</p>
}

<!-- With Map -->
@for (item of myMap | keyvalue; track item.key) {
  <p>{{ item.key }} = {{ item.value }}</p>
}
```

---

## 4. Pure vs Impure Pipes

### Pure Pipes (Default)

```typescript
@Pipe({
  name: 'filter',
  standalone: true,
  pure: true  // Default
})
export class FilterPipe implements PipeTransform {
  transform(items: any[], criteria: string): any[] {
    console.log('Pure pipe called');
    return items.filter(item => item.includes(criteria));
  }
}
```

**Characteristics:**
- Called only when input reference changes
- Angular caches results
- Better performance
- Won't detect mutations

### Impure Pipes

```typescript
@Pipe({
  name: 'filterImpure',
  standalone: true,
  pure: false  // Impure
})
export class FilterImpurePipe implements PipeTransform {
  transform(items: any[], criteria: string): any[] {
    console.log('Impure pipe called - runs on every CD');
    return items.filter(item => item.includes(criteria));
  }
}
```

**Characteristics:**
- Called on every change detection
- Detects array mutations
- Can impact performance
- Use sparingly

### Comparison

| Pure (default) | Impure |
|----------------|--------|
| Runs when input ref changes | Runs every CD cycle |
| Cached results | No caching |
| Better performance | Can be slow |
| Won't detect mutations | Detects all changes |

---

## 5. Custom Pipes

### Basic Transform Pipe

```typescript
import { Pipe, PipeTransform } from '@angular/core';

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

// Usage: {{ text | truncate:100:'...' }}
```

### File Size Pipe

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

### Time Ago Pipe

```typescript
@Pipe({
  name: 'timeAgo',
  standalone: true
})
export class TimeAgoPipe implements PipeTransform {
  transform(value: Date | string): string {
    const date = new Date(value);
    const now = new Date();
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    const intervals: [number, string][] = [
      [31536000, 'year'],
      [2592000, 'month'],
      [86400, 'day'],
      [3600, 'hour'],
      [60, 'minute'],
      [1, 'second']
    ];
    
    for (const [secondsInUnit, unit] of intervals) {
      const interval = Math.floor(seconds / secondsInUnit);
      if (interval >= 1) {
        return interval === 1 
          ? `1 ${unit} ago` 
          : `${interval} ${unit}s ago`;
      }
    }
    
    return 'just now';
  }
}

// Usage: {{ createdAt | timeAgo }}  → "2 hours ago"
```

### Filter Pipe

```typescript
@Pipe({
  name: 'filter',
  standalone: true
})
export class FilterPipe implements PipeTransform {
  transform<T>(items: T[], field: keyof T, value: any): T[] {
    if (!items || !field) return items;
    return items.filter(item => item[field] === value);
  }
}

// Usage: {{ users | filter:'status':'active' }}
```

### Sort Pipe

```typescript
@Pipe({
  name: 'sort',
  standalone: true
})
export class SortPipe implements PipeTransform {
  transform<T>(items: T[], field: keyof T, order: 'asc' | 'desc' = 'asc'): T[] {
    if (!items || !field) return items;
    
    return [...items].sort((a, b) => {
      const aVal = a[field];
      const bVal = b[field];
      
      if (aVal < bVal) return order === 'asc' ? -1 : 1;
      if (aVal > bVal) return order === 'asc' ? 1 : -1;
      return 0;
    });
  }
}

// Usage: {{ items | sort:'name':'desc' }}
```

---

## 6. Async Pipe

The async pipe handles Observable and Promise subscriptions automatically.

### Basic Usage

```typescript
@Component({
  standalone: true,
  imports: [AsyncPipe],
  template: `
    <!-- Observable -->
    @if (user$ | async; as user) {
      <p>{{ user.name }}</p>
    }
    
    <!-- Alternative syntax -->
    <p>{{ (user$ | async)?.name }}</p>
    
    <!-- With loading state -->
    @if (data$ | async; as data) {
      <div>{{ data | json }}</div>
    } @else {
      <p>Loading...</p>
    }
    
    <!-- Multiple subscriptions (creates multiple subs!) -->
    <p>{{ (user$ | async)?.name }}</p>
    <p>{{ (user$ | async)?.email }}</p>  <!-- ❌ Two subscriptions -->
    
    <!-- Better: Single subscription -->
    @if (user$ | async; as user) {
      <p>{{ user.name }}</p>
      <p>{{ user.email }}</p>  <!-- ✅ One subscription -->
    }
  `
})
export class UserComponent {
  user$ = inject(UserService).getUser();
}
```

### With Error Handling

```typescript
@Component({
  template: `
    @if (data$ | async; as data) {
      <div>{{ data.name }}</div>
    } @else if (error) {
      <p class="error">{{ error }}</p>
    } @else {
      <p>Loading...</p>
    }
  `
})
export class DataComponent implements OnInit {
  data$!: Observable<Data>;
  error: string | null = null;
  
  ngOnInit(): void {
    this.data$ = this.dataService.getData().pipe(
      catchError(err => {
        this.error = err.message;
        return EMPTY;
      })
    );
  }
}
```

### Async Pipe Benefits

1. **Automatic subscription** - No manual subscribe
2. **Automatic unsubscription** - No memory leaks
3. **Works with OnPush** - Triggers change detection
4. **Cleaner code** - No ngOnInit subscriptions

```typescript
// ❌ Manual subscription (needs cleanup)
@Component({...})
export class BadComponent implements OnInit, OnDestroy {
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

// ✅ Async pipe (automatic cleanup)
@Component({
  template: `
    @if (user$ | async; as user) {
      {{ user.name }}
    }
  `
})
export class GoodComponent {
  user$ = inject(UserService).getUser();
}
```

---

## Summary

| Concept | Key Points |
|---------|------------|
| Directive Types | Component, Structural (*), Attribute |
| Custom Directive | @Directive, HostListener, HostBinding |
| Structural | TemplateRef, ViewContainerRef |
| Pure Pipe | Default, cached, better performance |
| Impure Pipe | Every CD, detects mutations |
| Async Pipe | Auto subscribe/unsubscribe |

---

## Next Steps
- Create a custom structural directive
- Build a search filter pipe
- Practice using async pipe with HTTP requests
