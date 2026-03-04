# Day 15: Change Detection Deep Dive

## Overview

Change detection is Angular's mechanism to synchronize component state with the DOM.

---

## How Change Detection Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Change Detection Flow                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   User Action / Async Event                                          │
│           │                                                          │
│           ▼                                                          │
│   ┌───────────────┐                                                 │
│   │   Zone.js     │  ◄── Patches async APIs (setTimeout, Promise)   │
│   │   Detects     │                                                 │
│   └───────┬───────┘                                                 │
│           │                                                          │
│           ▼                                                          │
│   ┌───────────────┐                                                 │
│   │   Angular     │                                                 │
│   │   Notified    │                                                 │
│   └───────┬───────┘                                                 │
│           │                                                          │
│           ▼                                                          │
│   ┌───────────────────────────────────────────────────┐             │
│   │           Change Detection Cycle                   │             │
│   │                                                    │             │
│   │   Root Component                                   │             │
│   │        │                                           │             │
│   │        ├──► Check bindings                        │             │
│   │        │                                           │             │
│   │        ▼                                           │             │
│   │   Child Components (recursively)                   │             │
│   │        │                                           │             │
│   │        ├──► Check bindings                        │             │
│   │        ├──► Update DOM if needed                  │             │
│   │        │                                           │             │
│   └───────────────────────────────────────────────────┘             │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Zone.js

Zone.js is a library that patches async APIs to notify Angular when async operations complete.

### What Zone.js Patches

```typescript
// Zone.js patches these and more:
setTimeout(), setInterval()
Promise.then()
addEventListener()
XMLHttpRequest
fetch()
requestAnimationFrame()
```

### How Zone.js Works

```typescript
// Without Zone.js, Angular wouldn't know about this:
setTimeout(() => {
  this.data = 'updated';  // Angular needs to detect this change
}, 1000);

// Zone.js wraps setTimeout:
// Original: window.setTimeout
// Patched:  Zone.current.wrap(window.setTimeout)

// When the callback runs, Zone.js notifies Angular
// Angular then runs change detection
```

---

## Change Detection Strategies

### Default Strategy

```typescript
@Component({
  selector: 'app-default',
  changeDetection: ChangeDetectionStrategy.Default,
  template: `<p>{{ data }}</p>`
})
export class DefaultComponent {
  data = 'initial';
}
```

**Behavior:**
- Runs on EVERY change detection cycle
- Checks ALL bindings in template
- Can be expensive with complex components

### OnPush Strategy

```typescript
@Component({
  selector: 'app-on-push',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <p>{{ user.name }}</p>
    <p>{{ data$ | async }}</p>
  `
})
export class OnPushComponent {
  @Input() user!: User;
  data$ = this.dataService.data$;
}
```

**OnPush triggers change detection when:**
1. **@Input reference changes** (not mutations)
2. **DOM events** from the component or children
3. **Async pipe** emits new value
4. **Manually triggered** via ChangeDetectorRef

```
┌─────────────────────────────────────────────────────────────────────┐
│                  OnPush vs Default Comparison                        │
├─────────────────┬─────────────────────┬─────────────────────────────┤
│ Trigger         │ Default             │ OnPush                      │
├─────────────────┼─────────────────────┼─────────────────────────────┤
│ Any CD cycle    │ ✓ Checks            │ ✗ Skipped                   │
│ Input change    │ ✓ Checks            │ ✓ Checks (reference only)   │
│ DOM event       │ ✓ Checks            │ ✓ Checks                    │
│ async pipe      │ ✓ Checks            │ ✓ Checks                    │
│ setTimeout      │ ✓ Checks            │ ✗ Skipped                   │
│ Manual mark     │ N/A                 │ ✓ Checks                    │
└─────────────────┴─────────────────────┴─────────────────────────────┘
```

---

## ChangeDetectorRef Methods

```typescript
import { Component, ChangeDetectorRef, ChangeDetectionStrategy, inject } from '@angular/core';

@Component({
  selector: 'app-manual-cd',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <p>Count: {{ count }}</p>
    <button (click)="increment()">Increment</button>
  `
})
export class ManualCdComponent {
  private cdr = inject(ChangeDetectorRef);
  count = 0;

  increment() {
    this.count++;
    // With OnPush, we need to tell Angular to check this component
  }

  // External update (WebSocket, setInterval, etc.)
  externalUpdate(value: number) {
    this.count = value;
    // Option 1: Mark for check in next cycle
    this.cdr.markForCheck();
    
    // Option 2: Run detection immediately
    // this.cdr.detectChanges();
  }

  // Detach from change detection (advanced optimization)
  detachExample() {
    this.cdr.detach();  // Component won't be checked
    
    // Later, reattach
    this.cdr.reattach();
  }
}
```

### Method Comparison

```
┌────────────────────┬─────────────────────────────────────────────────┐
│ Method             │ Description                                      │
├────────────────────┼─────────────────────────────────────────────────┤
│ markForCheck()     │ Marks component and ancestors for check.        │
│                    │ Runs in next CD cycle. Use with OnPush.         │
├────────────────────┼─────────────────────────────────────────────────┤
│ detectChanges()    │ Runs CD immediately for this component and      │
│                    │ its children. Synchronous.                      │
├────────────────────┼─────────────────────────────────────────────────┤
│ detach()           │ Removes component from CD tree. Component       │
│                    │ won't be checked until reattached.              │
├────────────────────┼─────────────────────────────────────────────────┤
│ reattach()         │ Re-adds component to CD tree.                   │
├────────────────────┼─────────────────────────────────────────────────┤
│ checkNoChanges()   │ Development only. Throws if bindings changed.   │
│                    │ Used to detect ExpressionChangedAfterCheck.     │
└────────────────────┴─────────────────────────────────────────────────┘
```

---

## Common Patterns

### Pattern 1: OnPush with Immutable Data

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @for (item of items; track item.id) {
      <app-item [item]="item" />
    }
  `
})
export class ListComponent {
  @Input() items: Item[] = [];

  // Parent must pass NEW array reference for OnPush to detect
  // items = [...items, newItem];  ✓
  // items.push(newItem);          ✗ Won't detect
}
```

### Pattern 2: OnPush with Observables

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    @if (user$ | async; as user) {
      <h1>{{ user.name }}</h1>
      <p>{{ user.email }}</p>
    }
  `
})
export class UserProfileComponent {
  user$ = this.userService.currentUser$;
  // async pipe automatically triggers markForCheck()
}
```

### Pattern 3: OnPush with Signals

```typescript
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <h1>{{ user().name }}</h1>
    <p>Count: {{ count() }}</p>
  `
})
export class SignalComponent {
  user = signal({ name: 'John' });
  count = signal(0);
  
  // Signals automatically integrate with CD
  // No markForCheck needed
  increment() {
    this.count.update(c => c + 1);
    // Angular knows to check this component
  }
}
```

### Pattern 4: Detached Change Detection

```typescript
@Component({
  template: `<canvas #canvas></canvas>`
})
export class CanvasComponent implements OnInit, OnDestroy {
  @ViewChild('canvas') canvas!: ElementRef<HTMLCanvasElement>;
  
  private cdr = inject(ChangeDetectorRef);
  private animationId!: number;

  ngOnInit() {
    // Detach since we're doing custom rendering
    this.cdr.detach();
    this.animate();
  }

  private animate() {
    this.draw();
    this.animationId = requestAnimationFrame(() => this.animate());
  }

  private draw() {
    const ctx = this.canvas.nativeElement.getContext('2d');
    // Direct DOM manipulation, no Angular bindings
  }

  ngOnDestroy() {
    cancelAnimationFrame(this.animationId);
  }
}
```

---

## NgZone

NgZone allows you to control when Angular runs change detection.

```typescript
import { Component, NgZone, inject } from '@angular/core';

@Component({...})
export class ZoneComponent {
  private ngZone = inject(NgZone);

  // Run OUTSIDE Angular zone (no CD triggered)
  runHeavyComputation() {
    this.ngZone.runOutsideAngular(() => {
      // This won't trigger change detection
      for (let i = 0; i < 1000000; i++) {
        // heavy work
      }
      
      // When done, run back inside Angular zone
      this.ngZone.run(() => {
        this.result = 'done';
        // This triggers change detection
      });
    });
  }

  // Common use: Third-party libraries
  initThirdPartyLib() {
    this.ngZone.runOutsideAngular(() => {
      // Initialize library that uses many timers/events
      // Won't trigger CD for every callback
      someLib.init({
        onUpdate: (data: any) => {
          // Only enter Angular zone when needed
          if (data.needsUIUpdate) {
            this.ngZone.run(() => {
              this.data = data;
            });
          }
        }
      });
    });
  }
}
```

---

## Zoneless Angular (Experimental)

Angular 18+ supports running without Zone.js:

```typescript
// main.ts
import { bootstrapApplication } from '@angular/platform-browser';
import { provideExperimentalZonelessChangeDetection } from '@angular/core';

bootstrapApplication(AppComponent, {
  providers: [
    provideExperimentalZonelessChangeDetection()
  ]
});
```

**Requirements for Zoneless:**
- Use Signals for reactive state
- Use `async` pipe or `toSignal()` for observables
- Manually call `markForCheck()` when needed

```typescript
// Zoneless component with signals
@Component({
  selector: 'app-zoneless',
  template: `
    <p>Count: {{ count() }}</p>
    <button (click)="increment()">+</button>
  `
})
export class ZonelessComponent {
  count = signal(0);

  increment() {
    this.count.update(c => c + 1);
    // Signals notify Angular scheduler automatically
  }
}
```

---

## ExpressionChangedAfterItHasBeenCheckedError

This error occurs when a binding changes during change detection (in development mode).

### Common Causes and Solutions

```typescript
// ❌ BAD: Changing value in getter
get calculatedValue() {
  return Math.random();  // Different each time
}

// ✓ GOOD: Cache the value
private _cachedValue = Math.random();
get calculatedValue() {
  return this._cachedValue;
}

// ❌ BAD: Changing value in ngAfterViewInit
ngAfterViewInit() {
  this.title = 'Updated';  // Error!
}

// ✓ GOOD: Use setTimeout or signal
ngAfterViewInit() {
  setTimeout(() => this.title = 'Updated');
  // Or with signals:
  // this.title.set('Updated');
}

// ❌ BAD: Child modifying parent state
@Component({
  template: `<child (ready)="onChildReady()"></child>`
})
class ParentComponent {
  showContent = false;
  
  onChildReady() {
    this.showContent = true;  // Error if during CD
  }
}

// ✓ GOOD: Defer the update
onChildReady() {
  Promise.resolve().then(() => this.showContent = true);
}
```

---

## Performance Tips

### 1. Use OnPush Everywhere

```typescript
// Set as default in angular.json
{
  "schematics": {
    "@schematics/angular:component": {
      "changeDetection": "OnPush"
    }
  }
}
```

### 2. Use trackBy in loops

```typescript
@Component({
  template: `
    @for (item of items; track item.id) {
      <app-item [item]="item" />
    }
  `
})
export class ListComponent {
  // trackBy prevents re-rendering unchanged items
}
```

### 3. Avoid Complex Expressions in Templates

```typescript
// ❌ BAD
<div>{{ calculateComplexValue() }}</div>

// ✓ GOOD
<div>{{ complexValue }}</div>

// In component:
complexValue = computed(() => this.calculateComplexValue());
```

### 4. Use Pipes for Transformations

```typescript
// ❌ BAD: Transform in template
<div>{{ items.filter(i => i.active).length }}</div>

// ✓ GOOD: Use pure pipe (memoized)
<div>{{ items | activeCount }}</div>
```

---

## Summary

| Concept | Description |
|---------|-------------|
| Zone.js | Patches async APIs, notifies Angular |
| Default CD | Checks all components every cycle |
| OnPush | Checks only when inputs/events/async pipe |
| markForCheck() | Schedule check for next cycle |
| detectChanges() | Run check immediately |
| detach()/reattach() | Remove/add from CD tree |
| runOutsideAngular() | Execute without triggering CD |
| Signals | Automatic fine-grained reactivity |
