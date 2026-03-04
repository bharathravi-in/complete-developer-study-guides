# Day 8-9: RxJS Core - Interview Questions & Answers

## Table of Contents
1. [Fundamentals](#fundamentals)
2. [Subjects](#subjects)
3. [Operators](#operators)
4. [Error Handling & Memory Management](#error-handling--memory-management)
5. [Practical Scenarios](#practical-scenarios)
6. [Advanced Concepts](#advanced-concepts)
7. [Interview Tips](#interview-tips)

---

## Fundamentals

### Q1: What is the difference between Observable and Promise?

**Answer:**

| Aspect | Observable | Promise |
|--------|------------|---------|
| **Execution** | Lazy - executes only on subscribe | Eager - executes immediately on creation |
| **Values** | Multiple values over time (stream) | Single value |
| **Cancellation** | Can cancel via `unsubscribe()` | Not natively cancelable |
| **Operators** | Rich library (map, filter, switchMap, etc.) | Limited (then, catch, finally) |
| **Sync/Async** | Can be synchronous or asynchronous | Always asynchronous |

**Code Example:**

```typescript
// Promise - Executes immediately
const promise = new Promise(resolve => {
  console.log('Promise: Executing NOW');
  resolve('done');
});
// "Promise: Executing NOW" - logs immediately even without .then()

// Observable - Executes only on subscribe
const observable = new Observable(subscriber => {
  console.log('Observable: Executing NOW');
  subscriber.next('done');
  subscriber.complete();
});
// Nothing logged yet...
observable.subscribe(); // "Observable: Executing NOW" - logs now
```

**Key Points to Mention:**
- Observables can emit 0, 1, or multiple values; Promises resolve once
- Observable subscription returns a `Subscription` object for cleanup
- Observables support operators for transformation, filtering, combination
- You can convert between them using `from()` (Promise→Observable) and `firstValueFrom()`/`lastValueFrom()` (Observable→Promise)

---

### Q2: Explain the difference between cold and hot observables with examples.

**Answer:**

**Cold Observable:**
- Creates a new data producer for each subscriber
- Each subscriber gets independent execution
- Examples: `of()`, `from()`, `interval()`, HTTP requests

**Hot Observable:**
- Shares the same data producer among all subscribers
- Late subscribers miss earlier emissions
- Examples: `Subject`, `fromEvent()`, WebSocket connections

```typescript
// COLD: Each subscriber gets fresh random number
const cold$ = defer(() => of(Math.random()));
cold$.subscribe(v => console.log('A:', v)); // A: 0.123
cold$.subscribe(v => console.log('B:', v)); // B: 0.789 (different!)

// HOT: All subscribers share the same source
const hot$ = new Subject<number>();
hot$.subscribe(v => console.log('A:', v));
hot$.next(1); // A: 1
hot$.subscribe(v => console.log('B:', v));
hot$.next(2); // A: 2, B: 2 (B missed 1)
```

**Converting Cold to Hot:**
```typescript
// share() multicasts to all subscribers
const shared$ = interval(1000).pipe(share());

// shareReplay(1) - also replays last value to new subscribers
const cached$ = this.http.get('/api/data').pipe(shareReplay(1));
```

**Interview Tip:** Use a marble diagram to illustrate:
```
Cold (interval):
SubA: ─0─1─2─3─4─
SubB:     ─0─1─2─3─4─  (own counter)

Hot (Subject):
emit:    ─1───2───3───4─
SubA:    ─1───2───3───4─
SubB:        └───2───3───4─  (missed 1)
```

---

### Q3: What happens if you don't unsubscribe from an Observable?

**Answer:**

**Potential Problems:**
1. **Memory Leaks**: Subscription holds references preventing garbage collection
2. **Unintended Side Effects**: Callbacks continue executing on destroyed components
3. **Performance Degradation**: Multiple active subscriptions consume resources
4. **Application Errors**: Accessing destroyed component properties

```typescript
// PROBLEM: Memory leak
@Component({...})
export class LeakyComponent implements OnInit {
  ngOnInit() {
    // This keeps running forever, even after component destroyed!
    interval(1000).subscribe(v => {
      this.counter = v; // Error: accessing destroyed component
    });
  }
}

// SOLUTION: Proper cleanup
@Component({...})
export class SafeComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  
  ngOnInit() {
    interval(1000).pipe(
      takeUntil(this.destroy$)
    ).subscribe(v => this.counter = v);
  }
  
  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

**Observables That Auto-Complete (usually safe):**
- HTTP requests (`HttpClient.get()`)
- `of()`, `from()` with finite data
- `take()`, `first()` operators

**Observables That Never Complete (must unsubscribe):**
- `interval()`, `timer()` (without take)
- `fromEvent()`
- `Subject` emissions
- Router events
- Form valueChanges

---

## Subjects

### Q4: Compare all Subject types and when to use each.

**Answer:**

| Subject Type | Initial Value | Replay | Emit Timing | Use Case |
|--------------|---------------|--------|-------------|----------|
| `Subject` | No | None | On `next()` | Events, actions, no replay needed |
| `BehaviorSubject` | Required | Last 1 | On `next()` + immediate | State, always has current value |
| `ReplaySubject` | No | Configurable (n) | On `next()` + replay | Cache, late subscriber catch-up |
| `AsyncSubject` | No | Last 1 | Only on `complete()` | Final result only |

```typescript
// Subject - Fire and forget events
const clicks$ = new Subject<MouseEvent>();
clicks$.next(event); // Only current subscribers receive

// BehaviorSubject - Current state
const user$ = new BehaviorSubject<User | null>(null);
user$.getValue(); // Synchronous access to current value
user$.subscribe(u => ...); // Immediately receives current value

// ReplaySubject - Message history
const messages$ = new ReplaySubject<Message>(10); // Keep last 10
// New subscriber gets last 10 messages immediately

// AsyncSubject - Computation result
const result$ = new AsyncSubject<number>();
result$.next(1); // Nothing emitted
result$.next(2); // Nothing emitted
result$.complete(); // NOW emits 2 to all subscribers
```

**When to Choose:**
- Need current value sync? → `BehaviorSubject`
- Need replay for late subscribers? → `ReplaySubject`
- Only care about final result? → `AsyncSubject`
- Simple event bus? → `Subject`

---

### Q5: What is the difference between Subject and BehaviorSubject? When would you use each?

**Answer:**

**Key Differences:**

| Aspect | Subject | BehaviorSubject |
|--------|---------|-----------------|
| Initial Value | Not required | Required |
| New Subscriber | Gets nothing until next `next()` | Immediately gets current value |
| Sync Value Access | Not possible | `getValue()` or `.value` |
| Typical Use | Events, actions | State management |

**Use Subject When:**
- Emitting events/actions that don't need replay
- Click handlers, form submissions
- No meaningful "current value" exists

**Use BehaviorSubject When:**
- Managing state that always has a value
- New subscribers need immediate access to current state
- Need synchronous value access

```typescript
// Subject for actions - no initial state makes sense
@Injectable({ providedIn: 'root' })
export class ActionService {
  private actionSubject = new Subject<Action>();
  action$ = this.actionSubject.asObservable();
  
  dispatch(action: Action) {
    this.actionSubject.next(action);
  }
}

// BehaviorSubject for state - always has a value
@Injectable({ providedIn: 'root' })
export class AuthService {
  private userSubject = new BehaviorSubject<User | null>(null);
  user$ = this.userSubject.asObservable();
  
  get currentUser(): User | null {
    return this.userSubject.getValue(); // Sync access
  }
  
  login(user: User) {
    this.userSubject.next(user);
  }
  
  logout() {
    this.userSubject.next(null);
  }
}
```

**Interview Tip:** Mention that `BehaviorSubject` is commonly used in Angular services for state because components subscribing in `ngOnInit` immediately receive the current value.

---

## Operators

### Q6: Explain the difference between switchMap, mergeMap, concatMap, and exhaustMap.

**Answer:**

This is one of the most common RxJS interview questions. All four operators flatten inner observables but handle concurrency differently.

```
Given: outer$ emits A, then B while A's inner is still running

switchMap:  B cancels A's inner, starts B's inner
mergeMap:   Both run concurrently
concatMap:  B's inner queued, runs after A's completes
exhaustMap: B is completely ignored while A's inner runs
```

**Visual Comparison:**
```
outer$:     ──A──────B──────C──|
              │       │       │
              └──1─2──│       │
                  X cancel    │
                      └──1─2──│
                          X cancel
                              └──1─2─3─|

switchMap:  ────1─────1────1─2─3─|  (cancel previous)
mergeMap:   ────1─2───1─2──1─2─3─|  (all parallel)
concatMap:  ────1─2───1─2──1─2─3─|  (sequential queue)
exhaustMap: ────1─2────────1─2─3─|  (ignore B)
```

**When to Use Each:**

| Operator | Behavior | Use Case |
|----------|----------|----------|
| `switchMap` | Cancel previous | Search autocomplete, navigation |
| `mergeMap` | Run parallel | Batch operations, when order doesn't matter |
| `concatMap` | Run sequential | Transactions, ordered operations |
| `exhaustMap` | Ignore new | Prevent double-submit, refresh button |

**Code Examples:**

```typescript
// switchMap - Type-ahead search (cancel previous search)
this.searchInput.valueChanges.pipe(
  debounceTime(300),
  switchMap(term => this.searchService.search(term))
).subscribe(results => this.results = results);

// mergeMap - Load all items in parallel
from(itemIds).pipe(
  mergeMap(id => this.http.get(`/api/items/${id}`))
).subscribe(item => this.items.push(item));

// concatMap - Sequential file uploads
from(files).pipe(
  concatMap(file => this.uploadService.upload(file))
).subscribe(result => console.log('Uploaded:', result));

// exhaustMap - Form submission (ignore clicks while saving)
this.submitButton.clicks$.pipe(
  exhaustMap(() => this.http.post('/api/save', this.form.value))
).subscribe(response => this.showSuccess());
```

**Interview Tip:** Draw a marble diagram and walk through what happens when a second value arrives while the first inner observable is still running.

---

### Q7: What is debounceTime vs throttleTime? When would you use each?

**Answer:**

| Aspect | debounceTime | throttleTime |
|--------|--------------|--------------|
| **Behavior** | Wait for silence | Emit first, then wait |
| **Emits** | After no input for duration | First value, then ignores for duration |
| **Use Case** | Search input, resize | Scroll, mouse move, button clicks |

**Marble Diagram:**
```
Input:          ──a─b─c─d─e─────f─g──|
                              ↑
                         (500ms gap)

debounceTime(200ms):
result:         ──────────e─────────g─|
                (emits after silence)

throttleTime(200ms):
result:         ──a─────────────f────|
                (emits first, ignores for 200ms)
```

**Code Examples:**

```typescript
// debounceTime - Search input (wait for user to stop typing)
this.searchInput.valueChanges.pipe(
  debounceTime(300), // Wait 300ms after last keystroke
  distinctUntilChanged(),
  switchMap(term => this.search(term))
).subscribe(results => this.results = results);

// throttleTime - Scroll handler (limit frequency)
fromEvent(window, 'scroll').pipe(
  throttleTime(100) // Max once per 100ms
).subscribe(() => this.handleScroll());

// throttleTime - Rapid button clicks
fromEvent(button, 'click').pipe(
  throttleTime(1000) // Ignore clicks for 1s after first
).subscribe(() => this.performAction());
```

**Decision Guide:**
- User typing → `debounceTime` (wait until they pause)
- Scroll/resize/mousemove → `throttleTime` (limit frequency)
- Search suggestions → `debounceTime`
- Infinite scroll → `throttleTime`

---

### Q8: Explain the takeUntil pattern and takeUntilDestroyed.

**Answer:**

**takeUntil Pattern (Pre-Angular 16):**

```typescript
@Component({...})
export class MyComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  
  ngOnInit() {
    // All subscriptions auto-cleanup
    this.dataService.data$.pipe(
      takeUntil(this.destroy$)
    ).subscribe(data => this.data = data);
    
    interval(1000).pipe(
      takeUntil(this.destroy$)
    ).subscribe(v => this.tick(v));
  }
  
  ngOnDestroy() {
    this.destroy$.next();    // Trigger completion
    this.destroy$.complete(); // Clean up subject
  }
}
```

**takeUntilDestroyed (Angular 16+):**

```typescript
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { DestroyRef, inject } from '@angular/core';

@Component({...})
export class ModernComponent {
  private destroyRef = inject(DestroyRef);
  
  ngOnInit() {
    // Method 1: Inject DestroyRef
    this.dataService.data$.pipe(
      takeUntilDestroyed(this.destroyRef)
    ).subscribe(data => this.data = data);
  }
}

// Even cleaner - in constructor (auto-injects DestroyRef)
@Component({...})
export class CleanerComponent {
  constructor() {
    interval(1000).pipe(
      takeUntilDestroyed() // No argument needed in constructor
    ).subscribe(v => this.tick(v));
  }
}
```

**Comparison:**

| Aspect | takeUntil | takeUntilDestroyed |
|--------|-----------|-------------------|
| Angular Version | All | 16+ |
| Requires Subject | Yes | No |
| Requires OnDestroy | Yes | No |
| Constructor Usage | Works | Auto-injects |
| Outside Constructor | Works | Needs DestroyRef |

**Interview Tip:** Always mention that `takeUntilDestroyed()` without arguments only works in injection context (constructor, field initializer).

---

## Error Handling & Memory Management

### Q9: How do you handle errors in RxJS streams?

**Answer:**

**Key Operators:**

```typescript
import { catchError, retry, EMPTY, throwError, of } from 'rxjs';

// 1. catchError - Handle and recover
this.http.get('/api/data').pipe(
  catchError(error => {
    console.error('Error:', error);
    return of(defaultData); // Return fallback
  })
).subscribe(data => this.data = data);

// 2. Return EMPTY to silently complete
this.http.get('/api/optional').pipe(
  catchError(() => EMPTY) // Complete without value
).subscribe();

// 3. Rethrow with context
this.http.get('/api/user').pipe(
  catchError(err => throwError(() => 
    new Error(`Failed to load user: ${err.message}`)
  ))
).subscribe({ error: e => this.handleError(e) });

// 4. Different handling per error type
this.http.get('/api/data').pipe(
  catchError(err => {
    if (err.status === 404) return of(null);
    if (err.status === 401) {
      this.router.navigate(['/login']);
      return EMPTY;
    }
    return throwError(() => err);
  })
).subscribe();
```

**Retry Strategies:**

```typescript
// Simple retry
this.http.get('/api/flaky').pipe(
  retry(3) // Retry up to 3 times
).subscribe();

// Retry with delay (RxJS 7+)
this.http.get('/api/data').pipe(
  retry({
    count: 3,
    delay: 1000 // 1 second between retries
  })
).subscribe();

// Exponential backoff
this.http.get('/api/data').pipe(
  retry({
    count: 4,
    delay: (error, retryCount) => 
      timer(Math.pow(2, retryCount) * 1000) // 2s, 4s, 8s, 16s
  })
).subscribe();
```

**Complete Pattern:**

```typescript
this.http.get('/api/data').pipe(
  tap(() => this.loading = true),
  retry({ count: 3, delay: 1000 }),
  catchError(err => {
    this.errorService.report(err);
    return of(fallbackData);
  }),
  finalize(() => this.loading = false) // Always runs
).subscribe(data => this.data = data);
```

---

### Q10: What is the finalize operator and when do you use it?

**Answer:**

`finalize()` executes a callback when the observable completes, errors, OR is unsubscribed. It's perfect for cleanup that must always happen.

```typescript
import { finalize } from 'rxjs/operators';

// Use Case 1: Loading indicator
loadData() {
  this.loading = true;
  
  this.http.get('/api/data').pipe(
    finalize(() => this.loading = false) // Always resets
  ).subscribe({
    next: data => this.data = data,
    error: err => this.showError(err)
  });
}

// Use Case 2: Resource cleanup
this.webSocket.connect().pipe(
  finalize(() => {
    console.log('Cleaning up connection');
    this.webSocket.close();
  })
).subscribe();

// Use Case 3: Analytics tracking
performAction() {
  const startTime = Date.now();
  
  this.actionService.execute().pipe(
    finalize(() => {
      this.analytics.track('action_duration', Date.now() - startTime);
    })
  ).subscribe();
}
```

**When finalize runs:**
- Observable completes normally ✓
- Observable errors ✓
- Subscription is unsubscribed ✓

**Interview Tip:** Compare with `tap` - `tap` runs for each value, `finalize` runs once at the end.

---

### Q11: How do you prevent memory leaks in Angular with RxJS?

**Answer:**

**Strategies (from most to least recommended):**

**1. AsyncPipe (Best for templates)**
```typescript
@Component({
  template: `
    <div *ngIf="data$ | async as data">{{ data.name }}</div>
  `
})
export class MyComponent {
  data$ = this.dataService.getData();
  // No manual subscription management!
}
```

**2. takeUntilDestroyed (Angular 16+)**
```typescript
@Component({...})
export class ModernComponent {
  constructor() {
    interval(1000).pipe(
      takeUntilDestroyed()
    ).subscribe();
  }
}
```

**3. takeUntil Pattern**
```typescript
private destroy$ = new Subject<void>();

ngOnInit() {
  source$.pipe(takeUntil(this.destroy$)).subscribe();
}

ngOnDestroy() {
  this.destroy$.next();
  this.destroy$.complete();
}
```

**4. Manual Subscription Management**
```typescript
private subscription = new Subscription();

ngOnInit() {
  this.subscription.add(source1$.subscribe());
  this.subscription.add(source2$.subscribe());
}

ngOnDestroy() {
  this.subscription.unsubscribe();
}
```

**Red Flags (Memory Leak Sources):**
- `interval()` without `take()` or cleanup
- `fromEvent()` without cleanup
- Route params/query params subscriptions
- Form valueChanges without cleanup
- WebSocket connections

**Interview Tip:** Mention that HTTP requests (`HttpClient`) auto-complete after response, so they usually don't need cleanup (but cancellation via `takeUntil` can still be useful).

---

## Practical Scenarios

### Q12: How would you implement a search-as-you-type feature with RxJS?

**Answer:**

```typescript
@Component({
  template: `
    <input [formControl]="searchControl" placeholder="Search...">
    <ul>
      <li *ngFor="let result of results">{{ result.name }}</li>
    </ul>
    <div *ngIf="loading">Loading...</div>
  `
})
export class SearchComponent implements OnInit {
  searchControl = new FormControl('');
  results: SearchResult[] = [];
  loading = false;
  
  private destroyRef = inject(DestroyRef);
  private searchService = inject(SearchService);
  
  ngOnInit() {
    this.searchControl.valueChanges.pipe(
      debounceTime(300),           // Wait for typing pause
      distinctUntilChanged(),       // Ignore if same value
      tap(() => this.loading = true),
      switchMap(term => {           // Cancel previous request
        if (!term || term.length < 2) {
          return of([]);            // Min length requirement
        }
        return this.searchService.search(term).pipe(
          catchError(() => of([]))  // Handle error gracefully
        );
      }),
      tap(() => this.loading = false),
      takeUntilDestroyed(this.destroyRef)
    ).subscribe(results => this.results = results);
  }
}
```

**Key Points:**
- `debounceTime(300)` - Wait for user to stop typing
- `distinctUntilChanged()` - Don't search if term hasn't changed
- `switchMap` - Cancel previous HTTP request when new term arrives
- `catchError` - Handle API errors gracefully
- `takeUntilDestroyed` - Cleanup on component destroy

---

### Q13: How would you implement polling with RxJS?

**Answer:**

```typescript
@Component({...})
export class DashboardComponent implements OnInit {
  status$: Observable<Status>;
  private destroyRef = inject(DestroyRef);
  
  ngOnInit() {
    // Basic polling every 5 seconds
    this.status$ = interval(5000).pipe(
      startWith(0), // Emit immediately on subscribe
      switchMap(() => this.http.get<Status>('/api/status')),
      retry(3),
      catchError(err => {
        console.error('Polling error:', err);
        return EMPTY;
      }),
      takeUntilDestroyed(this.destroyRef)
    );
  }
}

// Advanced: Polling with pause/resume
@Component({...})
export class AdvancedPollingComponent {
  private polling$ = new BehaviorSubject<boolean>(true);
  
  status$ = this.polling$.pipe(
    switchMap(isPolling => 
      isPolling ? interval(5000).pipe(startWith(0)) : EMPTY
    ),
    switchMap(() => this.http.get<Status>('/api/status')),
    shareReplay(1)
  );
  
  pausePolling() { this.polling$.next(false); }
  resumePolling() { this.polling$.next(true); }
}
```

**Key Points:**
- `interval(5000)` - Poll every 5 seconds
- `startWith(0)` - Load immediately, don't wait 5s
- `switchMap` - Cancel pending request if new interval fires
- `shareReplay(1)` - Share result with multiple subscribers

---

### Q14: How do you implement a form auto-save feature?

**Answer:**

```typescript
@Component({...})
export class AutoSaveFormComponent implements OnInit {
  form = new FormGroup({
    title: new FormControl(''),
    content: new FormControl('')
  });
  
  saveStatus$ = new BehaviorSubject<'saved' | 'saving' | 'error'>('saved');
  
  private destroyRef = inject(DestroyRef);
  
  ngOnInit() {
    this.form.valueChanges.pipe(
      debounceTime(1000),           // Wait 1s after changes
      distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
      tap(() => this.saveStatus$.next('saving')),
      switchMap(value => 
        this.http.post('/api/draft', value).pipe(
          map(() => 'saved' as const),
          catchError(() => of('error' as const))
        )
      ),
      takeUntilDestroyed(this.destroyRef)
    ).subscribe(status => this.saveStatus$.next(status));
  }
}
```

**Template:**
```html
<form [formGroup]="form">
  <input formControlName="title">
  <textarea formControlName="content"></textarea>
  
  <span [ngSwitch]="saveStatus$ | async">
    <span *ngSwitchCase="'saving'">Saving...</span>
    <span *ngSwitchCase="'saved'">All changes saved</span>
    <span *ngSwitchCase="'error'">Save failed</span>
  </span>
</form>
```

---

### Q15: How would you handle multiple concurrent HTTP requests?

**Answer:**

**Scenario 1: Wait for All (forkJoin)**
```typescript
// All requests must complete
forkJoin({
  users: this.http.get<User[]>('/api/users'),
  products: this.http.get<Product[]>('/api/products'),
  orders: this.http.get<Order[]>('/api/orders')
}).subscribe(({ users, products, orders }) => {
  this.users = users;
  this.products = products;
  this.orders = orders;
});
```

**Scenario 2: Combine Latest Values (combineLatest)**
```typescript
// React to latest from each, after all emit at least once
combineLatest([
  this.user$,
  this.settings$,
  this.permissions$
]).pipe(
  map(([user, settings, permissions]) => ({
    displayName: user.name,
    theme: settings.theme,
    canEdit: permissions.includes('edit')
  }))
).subscribe(viewModel => this.vm = viewModel);
```

**Scenario 3: Parallel with Concurrency Limit (mergeMap)**
```typescript
// Process 100 items, max 5 concurrent requests
from(itemIds).pipe(
  mergeMap(
    id => this.http.get(`/api/items/${id}`),
    5 // Concurrency limit
  )
).subscribe(item => this.items.push(item));
```

**Scenario 4: Load in Sequence (concatMap)**
```typescript
// Load in order, one at a time
from(['config', 'user', 'data']).pipe(
  concatMap(endpoint => this.http.get(`/api/${endpoint}`))
).subscribe(response => console.log('Loaded:', response));
```

**Comparison:**
| Method | Use Case |
|--------|----------|
| `forkJoin` | Wait for all to complete, get all results together |
| `combineLatest` | React to changes, need latest from multiple streams |
| `mergeMap` | Parallel execution with optional concurrency limit |
| `concatMap` | Sequential execution, order matters |

---

## Advanced Concepts

### Q16: What is the difference between share() and shareReplay()?

**Answer:**

| Aspect | share() | shareReplay(n) |
|--------|---------|----------------|
| **Multicasting** | Yes | Yes |
| **Replay** | No | Yes, last n values |
| **Late Subscribers** | Miss previous emissions | Get replayed values |
| **RefCount** | Yes (auto connect/disconnect) | Configurable |

```typescript
// share() - No replay
const shared$ = interval(1000).pipe(
  take(5),
  share()
);

shared$.subscribe(v => console.log('A:', v)); // A: 0, 1, 2, 3, 4
setTimeout(() => {
  shared$.subscribe(v => console.log('B:', v)); // B: 2, 3, 4 (missed 0, 1)
}, 2500);

// shareReplay(1) - Replay last value
const cached$ = this.http.get('/api/config').pipe(
  shareReplay(1)
);

cached$.subscribe(v => console.log('A:', v)); // A: {config}
setTimeout(() => {
  cached$.subscribe(v => console.log('B:', v)); // B: {config} (instant!)
}, 5000);
```

**Common Use Cases:**
- HTTP caching: `shareReplay(1)`
- Live data (no replay needed): `share()`
- Expensive computations: `shareReplay(1)`

---

### Q17: Explain higher-order observables and why flattening is needed.

**Answer:**

A **higher-order observable** is an Observable that emits other Observables (`Observable<Observable<T>>`).

```typescript
// Without flattening
const outer$ = of(1, 2, 3);
const higherOrder$ = outer$.pipe(
  map(n => of(n * 10)) // Returns Observable<Observable<number>>
);

higherOrder$.subscribe(inner$ => {
  // inner$ is an Observable, not a value!
  inner$.subscribe(value => console.log(value));
});
// Nested subscriptions - ugly and error-prone!

// With flattening (switchMap/mergeMap/etc.)
const flattened$ = outer$.pipe(
  switchMap(n => of(n * 10)) // Returns Observable<number>
);

flattened$.subscribe(value => console.log(value));
// 10, 20, 30 - much cleaner!
```

**Why Flattening Matters:**
1. Avoids nested subscription hell
2. Provides automatic subscription management
3. Different strategies for different use cases (switchMap, mergeMap, etc.)
4. Better error handling propagation

---

### Q18: How does the async pipe help with memory management?

**Answer:**

The `async` pipe automatically:
1. Subscribes when the view initializes
2. Unsubscribes when the view is destroyed
3. Triggers change detection on new values

```typescript
// WITHOUT async pipe (manual subscription)
@Component({
  template: `<div>{{ data?.name }}</div>`
})
export class ManualComponent implements OnInit, OnDestroy {
  data: Data | null = null;
  private subscription?: Subscription;
  
  ngOnInit() {
    this.subscription = this.dataService.getData()
      .subscribe(d => this.data = d);
  }
  
  ngOnDestroy() {
    this.subscription?.unsubscribe(); // Must remember!
  }
}

// WITH async pipe (automatic)
@Component({
  template: `<div>{{ (data$ | async)?.name }}</div>`
})
export class AsyncPipeComponent {
  data$ = this.dataService.getData();
  // No ngOnDestroy needed!
}
```

**Best Practices:**
```html
<!-- Use 'as' syntax for multiple usages -->
<ng-container *ngIf="user$ | async as user">
  <h1>{{ user.name }}</h1>
  <p>{{ user.email }}</p>
</ng-container>

<!-- Multiple observables -->
<ng-container *ngIf="{ 
  user: user$ | async, 
  settings: settings$ | async 
} as vm">
  <div>{{ vm.user?.name }} - {{ vm.settings?.theme }}</div>
</ng-container>
```

---

### Q19: What's the difference between tap and map operators?

**Answer:**

| Aspect | tap | map |
|--------|-----|-----|
| **Purpose** | Side effects | Transform values |
| **Return Value** | Ignored (returns original) | Becomes new emitted value |
| **Changes Stream** | No | Yes |
| **Use Case** | Logging, state updates | Data transformation |

```typescript
of(1, 2, 3).pipe(
  tap(x => console.log('Before:', x)),  // Side effect only
  map(x => x * 10),                      // Transform value
  tap(x => console.log('After:', x))    // Side effect only
).subscribe(x => console.log('Final:', x));

// Output:
// Before: 1
// After: 10
// Final: 10
// Before: 2
// After: 20
// Final: 20
// Before: 3
// After: 30
// Final: 30
```

**Common tap Uses:**
```typescript
this.http.get('/api/data').pipe(
  tap(() => this.loading = false),     // Update loading state
  tap(data => console.log('Received:', data)), // Logging
  tap(data => localStorage.setItem('cache', JSON.stringify(data))) // Cache
)
```

---

### Q20: How do you test RxJS code in Angular?

**Answer:**

```typescript
import { TestScheduler } from 'rxjs/testing';
import { debounceTime, map } from 'rxjs/operators';

describe('RxJS Testing', () => {
  let scheduler: TestScheduler;
  
  beforeEach(() => {
    scheduler = new TestScheduler((actual, expected) => {
      expect(actual).toEqual(expected);
    });
  });
  
  // Marble testing
  it('should debounce values', () => {
    scheduler.run(({ cold, expectObservable }) => {
      const source$ = cold('--a--b--c---|');
      const expected =     '-----a--b---(c|)';
      
      const result$ = source$.pipe(debounceTime(2));
      
      expectObservable(result$).toBe(expected);
    });
  });
  
  // Testing with fakeAsync
  it('should filter and map', fakeAsync(() => {
    const results: number[] = [];
    
    of(1, 2, 3, 4, 5).pipe(
      filter(n => n % 2 === 0),
      map(n => n * 10)
    ).subscribe(v => results.push(v));
    
    tick();
    expect(results).toEqual([20, 40]);
  }));
  
  // Testing services with mock
  it('should handle HTTP with switchMap', fakeAsync(() => {
    const httpSpy = jasmine.createSpyObj('HttpClient', ['get']);
    httpSpy.get.and.returnValue(of({ data: 'test' }));
    
    const service = new MyService(httpSpy);
    let result: any;
    
    service.search('query').subscribe(r => result = r);
    tick(300); // debounceTime
    
    expect(result).toEqual({ data: 'test' });
  }));
});
```

---

## Interview Tips

### Common Mistakes to Avoid

1. **Forgetting to unsubscribe**
   - Always use `takeUntilDestroyed`, `takeUntil`, or `async` pipe

2. **Using mergeMap when switchMap is needed**
   - Search autocomplete should use `switchMap` to cancel previous requests

3. **Not handling errors**
   - Always have `catchError` in production code

4. **Nested subscriptions**
   - Use flattening operators instead

5. **Subscribing in subscribe**
   ```typescript
   // BAD
   source$.subscribe(id => {
     this.http.get(`/api/${id}`).subscribe(data => {...});
   });
   
   // GOOD
   source$.pipe(
     switchMap(id => this.http.get(`/api/${id}`))
   ).subscribe(data => {...});
   ```

### Key Points to Remember

1. **Observable vs Promise**: Lazy vs eager, multiple vs single, cancelable
2. **Cold vs Hot**: New execution vs shared execution
3. **Subject Types**: Know when to use each (BehaviorSubject for state)
4. **Flattening Operators**: switchMap (cancel), mergeMap (parallel), concatMap (queue), exhaustMap (ignore)
5. **Cleanup**: `takeUntilDestroyed` (16+), `takeUntil`, `async` pipe
6. **Error Handling**: `catchError`, `retry`, `finalize`

### Questions to Ask

When discussing RxJS in interviews, be prepared to:
1. Draw marble diagrams
2. Explain operator choices for specific scenarios
3. Discuss memory leak prevention
4. Compare different approaches (pros/cons)

---

## Quick Reference: Operator Selection

```
Need to transform each value?              → map
Need to flatten inner observables?
  └─ Cancel previous?                      → switchMap
  └─ Run in parallel?                      → mergeMap
  └─ Run sequentially?                     → concatMap
  └─ Ignore while busy?                    → exhaustMap
Need to filter values?
  └─ By condition?                         → filter
  └─ First n values?                       → take
  └─ Until signal?                         → takeUntil
  └─ Skip duplicates?                      → distinctUntilChanged
Need to delay/rate limit?
  └─ Wait for silence?                     → debounceTime
  └─ Limit frequency?                      → throttleTime
Need to handle errors?
  └─ Recover with fallback?                → catchError
  └─ Retry automatically?                  → retry
Need side effects?
  └─ Logging/state updates?                → tap
  └─ Cleanup on completion?                → finalize
Need to combine streams?
  └─ Wait for all to complete?             → forkJoin
  └─ Latest from each?                     → combineLatest
  └─ Merge into one?                       → merge
```
