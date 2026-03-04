# Angular Interview Flashcards

## Core Concepts

### Card 1: Standalone Components
**Q: What are standalone components?**

A: Components that declare their own dependencies via `imports` array instead of belonging to an NgModule.
```typescript
@Component({
  standalone: true,
  imports: [CommonModule, FormsModule]
})
```
**Benefits:** Simpler mental model, better tree-shaking, easier lazy loading.

---

### Card 2: Change Detection
**Q: What triggers change detection in Angular?**

A: 1) DOM events (click, input)
   2) HTTP responses
   3) Timers (setTimeout, setInterval)
   4) Async operations via Zone.js
   
**OnPush:** Only when input reference changes, events fire, or async pipe emits.

---

### Card 3: OnPush Strategy
**Q: When does OnPush component update?**

A: 
- Input reference changes (not mutations)
- Event fired in component/child
- Async pipe receives value
- `markForCheck()` called manually
- Signal value changes

---

### Card 4: Signals
**Q: What are Angular Signals?**

A: Reactive primitives for state management:
```typescript
count = signal(0);       // Create
count();                 // Read
count.set(5);           // Write
computed(() => count() * 2);  // Derived
effect(() => {...});    // Side effects
```

---

### Card 5: @defer Blocks
**Q: What does @defer do?**

A: Lazy loads template sections based on triggers:
```html
@defer (on viewport) {
  <heavy-component />
} @placeholder { ... }
```
**Triggers:** viewport, idle, interaction, hover, timer, when condition

---

## RxJS

### Card 6: switchMap vs mergeMap
**Q: When to use switchMap vs mergeMap?**

A:
- **switchMap:** Cancels previous, uses latest → Search/autocomplete
- **mergeMap:** All concurrent → Parallel downloads
- **concatMap:** Sequential queue → Ordered operations

---

### Card 7: Memory Leaks
**Q: How to prevent RxJS memory leaks?**

A:
```typescript
// Best (Angular 16+)
takeUntilDestroyed(this.destroyRef)

// Async pipe (auto-unsubscribe)
{{ data$ | async }}

// Manual
private destroy$ = new Subject();
ngOnDestroy() { this.destroy$.next(); }
```

---

### Card 8: Subject Types
**Q: Difference between Subject, BehaviorSubject, ReplaySubject?**

A:
- **Subject:** No initial value, no replay
- **BehaviorSubject:** Has current value, replays 1
- **ReplaySubject:** Configurable buffer size
- **AsyncSubject:** Emits last value on complete

---

## Dependency Injection

### Card 9: providedIn
**Q: What does providedIn: 'root' do?**

A: Creates a singleton service at the root injector level. Tree-shakable if not used.
```typescript
@Injectable({ providedIn: 'root' })
```
Other options: `'platform'`, `'any'`, specific NgModule

---

### Card 10: inject() Function
**Q: What is the inject() function?**

A: Modern way to inject dependencies (Angular 14+):
```typescript
class MyComponent {
  private service = inject(MyService);
  private router = inject(Router);
}
```
Must be called in constructor or field initializer.

---

## Routing

### Card 11: Functional Guards
**Q: How do you write a functional guard?**

A:
```typescript
export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  return auth.isLoggedIn() || inject(Router).createUrlTree(['/login']);
};
```

---

### Card 12: Lazy Loading
**Q: How to lazy load a route?**

A:
```typescript
{
  path: 'admin',
  loadComponent: () => import('./admin/admin.component'),
  // Or for routes:
  loadChildren: () => import('./admin/admin.routes')
}
```

---

## Forms

### Card 13: Reactive vs Template Forms
**Q: When to use Reactive vs Template-driven forms?**

A:
- **Reactive:** Complex forms, dynamic fields, heavy validation, unit testing
- **Template-driven:** Simple forms, two-way binding, minimal validation

---

### Card 14: Custom Validators
**Q: How to create a custom validator?**

A:
```typescript
function noSpaces(control: AbstractControl): ValidationErrors | null {
  return control.value?.includes(' ') ? { noSpaces: true } : null;
}

// Usage
name: ['', [Validators.required, noSpaces]]
```

---

## Performance

### Card 15: trackBy
**Q: Why use track in @for loops?**

A: Helps Angular identify items for efficient DOM updates:
```html
@for (item of items; track item.id) {
  <div>{{ item.name }}</div>
}
```
Without track, entire list re-renders on changes.

---

### Card 16: Virtual Scrolling
**Q: When to use virtual scrolling?**

A: For large lists (100+ items). Only renders visible items:
```html
<cdk-virtual-scroll-viewport itemSize="50">
  <div *cdkVirtualFor="let item of items">{{ item }}</div>
</cdk-virtual-scroll-viewport>
```

---

## Testing

### Card 17: TestBed
**Q: What is TestBed used for?**

A: Creates a testing module for Angular components/services:
```typescript
await TestBed.configureTestingModule({
  imports: [MyComponent],
  providers: [{ provide: MyService, useValue: mockService }]
}).compileComponents();
```

---

### Card 18: fakeAsync
**Q: What is fakeAsync used for?**

A: Testing async code synchronously:
```typescript
it('should debounce', fakeAsync(() => {
  component.search('test');
  tick(300);  // Advance time
  expect(component.results()).toBeTruthy();
}));
```

---

## Architecture

### Card 19: Smart vs Dumb Components
**Q: What are smart and dumb components?**

A:
- **Smart (Container):** Handles logic, injects services, manages state
- **Dumb (Presentational):** Pure UI, inputs/outputs only, OnPush strategy

---

### Card 20: Facade Pattern
**Q: What is the Facade pattern?**

A: Simplifies component access to complex state/services:
```typescript
@Injectable()
class UserFacade {
  users$ = this.store.users$;
  loadUsers() { this.store.dispatch(loadUsers()); }
}
```
Components use Facade, not direct store access.

---

## HTTP

### Card 21: Interceptors
**Q: What are HTTP interceptors?**

A: Middleware for HTTP requests/responses:
```typescript
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = inject(AuthService).token();
  if (token) {
    req = req.clone({ setHeaders: { Authorization: `Bearer ${token}` }});
  }
  return next(req);
};
```

---

### Card 22: Error Handling
**Q: How to handle HTTP errors globally?**

A: Use an error interceptor:
```typescript
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    catchError(error => {
      if (error.status === 401) inject(Router).navigate(['/login']);
      return throwError(() => error);
    })
  );
};
```

---

## State Management

### Card 23: Signal Store
**Q: What is NgRx Signal Store?**

A: Reactive state management using signals:
```typescript
export const CounterStore = signalStore(
  withState({ count: 0 }),
  withComputed(({ count }) => ({
    doubled: computed(() => count() * 2)
  })),
  withMethods((store) => ({
    increment() { patchState(store, { count: store.count() + 1 }); }
  }))
);
```

---

### Card 24: ComponentStore
**Q: What is ComponentStore?**

A: Lightweight state management for feature/component level:
```typescript
@Injectable()
class TodoStore extends ComponentStore<TodoState> {
  todos = this.selectSignal(state => state.todos);
  
  readonly loadTodos = this.effect(trigger$ => trigger$.pipe(
    switchMap(() => this.api.getTodos()),
    tap(todos => this.patchState({ todos }))
  ));
}
```

---

## SSR

### Card 25: Hydration
**Q: What is Angular hydration?**

A: Process of attaching event listeners to server-rendered HTML without re-rendering:
```typescript
provideClientHydration(withEventReplay())
```
**Benefits:** Faster interactivity, preserved DOM state, better user experience.

---

## Security

### Card 26: XSS Prevention
**Q: How does Angular prevent XSS?**

A: 
- Auto-sanitizes interpolation `{{ }}`
- Sanitizes innerHTML, style, URL bindings
- Use `DomSanitizer` for trusted content:
```typescript
this.sanitizer.bypassSecurityTrustHtml(html)
```

---

## Modern Features

### Card 27: input() function
**Q: What is the input() function?**

A: Signal-based input declaration (Angular 17+):
```typescript
title = input<string>();           // Optional
id = input.required<number>();     // Required
count = input(0);                  // With default
```

---

### Card 28: output() function
**Q: What is the output() function?**

A: Signal-based output declaration:
```typescript
clicked = output<void>();
selected = output<Item>();

// Emit
this.clicked.emit();
this.selected.emit(item);
```

---

### Card 29: model()
**Q: What is the model() function?**

A: Two-way binding with signals:
```typescript
value = model('');  // In component

// Usage
<my-input [(value)]="name" />
```

---

### Card 30: Control Flow
**Q: What is the new control flow syntax?**

A: Built-in template syntax (Angular 17+):
```html
@if (condition) { ... } @else { ... }
@for (item of items; track item.id) { ... }
@switch (value) { @case ('a') { ... } }
@defer (on viewport) { ... }
```
