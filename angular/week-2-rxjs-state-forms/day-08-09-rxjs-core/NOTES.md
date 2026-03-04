# Day 8-9: RxJS Core Concepts

## Table of Contents
1. [Observable vs Promise](#observable-vs-promise)
2. [Cold vs Hot Observables](#cold-vs-hot-observables)
3. [Subject Types](#subject-types)
4. [Creation Operators](#creation-operators)
5. [Transformation Operators](#transformation-operators)
6. [Filtering Operators](#filtering-operators)
7. [Error Handling](#error-handling)
8. [Cleanup Patterns](#cleanup-patterns)
9. [Marble Diagrams Reference](#marble-diagrams-reference)
10. [Quick Reference Card](#quick-reference-card)

---

## Observable vs Promise

### Fundamental Differences

| Feature | Observable | Promise |
|---------|------------|---------|
| **Execution** | Lazy (executes on subscribe) | Eager (executes immediately) |
| **Values** | Multiple values over time | Single value |
| **Cancelable** | Yes (unsubscribe) | No (native) |
| **Operators** | Rich operator library | Limited (.then, .catch, .finally) |
| **Error Handling** | catchError, retry, retryWhen | .catch() |
| **Async/Sync** | Can be both | Always async |

### Code Comparison

```typescript
// Promise - Executes immediately
const promise = new Promise((resolve, reject) => {
  console.log('Promise executor runs immediately!');
  setTimeout(() => resolve('Promise resolved'), 1000);
});

// Observable - Executes only when subscribed
const observable = new Observable(subscriber => {
  console.log('Observable executor runs on subscribe!');
  setTimeout(() => {
    subscriber.next('Observable emitted');
    subscriber.complete();
  }, 1000);
});

// Nothing happens until we subscribe
const subscription = observable.subscribe(value => console.log(value));

// Can cancel Observable
subscription.unsubscribe(); // Stops receiving values
```

### Observable Anatomy

```typescript
import { Observable } from 'rxjs';

const myObservable = new Observable<string>(subscriber => {
  // Producer logic
  subscriber.next('First value');    // Emit value
  subscriber.next('Second value');   // Emit another value
  
  setTimeout(() => {
    subscriber.next('Async value');
    subscriber.complete();           // Signal completion
  }, 1000);
  
  // Cleanup logic (teardown)
  return () => {
    console.log('Cleanup on unsubscribe');
  };
});

// Consumer
const subscription = myObservable.subscribe({
  next: value => console.log('Received:', value),
  error: err => console.error('Error:', err),
  complete: () => console.log('Completed!')
});
```

### Converting Between Observable and Promise

```typescript
import { from, firstValueFrom, lastValueFrom } from 'rxjs';

// Promise to Observable
const fromPromise$ = from(fetch('/api/data').then(r => r.json()));

// Observable to Promise (Angular 12+)
const promise1 = firstValueFrom(myObservable$); // First emitted value
const promise2 = lastValueFrom(myObservable$);  // Last emitted value (waits for complete)

// Legacy approach
const legacyPromise = myObservable$.toPromise(); // Deprecated
```

---

## Cold vs Hot Observables

### Cold Observables

**Definition**: Each subscriber gets its own independent execution of the observable.

```
Cold Observable: Data producer created INSIDE the observable

Subscriber A: ──1──2──3──|
Subscriber B:     ──1──2──3──|  (own execution)
```

```typescript
import { Observable, interval } from 'rxjs';
import { take } from 'rxjs/operators';

// Cold Observable - each subscriber gets fresh data
const cold$ = new Observable(subscriber => {
  console.log('Cold: New execution started');
  subscriber.next(Math.random()); // Different for each subscriber
  subscriber.complete();
});

cold$.subscribe(v => console.log('Subscriber A:', v)); // e.g., 0.123
cold$.subscribe(v => console.log('Subscriber B:', v)); // e.g., 0.789 (different!)

// interval is cold - each subscriber gets own counter
const interval$ = interval(1000).pipe(take(3));
interval$.subscribe(v => console.log('A:', v)); // A: 0, A: 1, A: 2
setTimeout(() => {
  interval$.subscribe(v => console.log('B:', v)); // B: 0, B: 1, B: 2 (starts fresh)
}, 2000);
```

### Hot Observables

**Definition**: All subscribers share the same execution/data source.

```
Hot Observable: Data producer exists OUTSIDE the observable

                ──1──2──3──4──5──
Subscriber A:   ──1──2──3──4──5──
Subscriber B:        ──2──3──4──5──  (joins late, misses 1)
```

```typescript
import { Subject, fromEvent, share, shareReplay } from 'rxjs';

// Subject is inherently hot
const subject$ = new Subject<number>();
subject$.subscribe(v => console.log('A:', v));
subject$.next(1); // A: 1
subject$.subscribe(v => console.log('B:', v));
subject$.next(2); // A: 2, B: 2 (B missed 1)

// fromEvent is hot - DOM events happen regardless of subscribers
const clicks$ = fromEvent(document, 'click');

// Making cold observable hot with share()
const shared$ = interval(1000).pipe(
  take(5),
  share() // Multicasts to all subscribers
);
```

### Cold to Hot Conversion

```typescript
import { interval, share, shareReplay, connectable, Subject } from 'rxjs';
import { take } from 'rxjs/operators';

// share() - multicast, refCount (auto connect/disconnect)
const shared$ = interval(1000).pipe(take(5), share());

// shareReplay(n) - multicast + replay last n values to new subscribers
const sharedReplay$ = interval(1000).pipe(
  take(5),
  shareReplay(1) // New subscribers get last emitted value immediately
);

// connectable() - manual control over connection
const source$ = interval(1000).pipe(take(5));
const connectable$ = connectable(source$, {
  connector: () => new Subject()
});
connectable$.subscribe(v => console.log('A:', v));
connectable$.connect(); // Manually start
```

### Comparison Table

| Aspect | Cold Observable | Hot Observable |
|--------|----------------|----------------|
| **Data Producer** | Created inside observable | Exists outside observable |
| **Execution** | Per subscriber | Shared |
| **Start Time** | On subscribe | Already running |
| **Examples** | HTTP requests, interval | Subject, DOM events, WebSocket |
| **Use Case** | Independent data fetches | Real-time data, events |

---

## Subject Types

### Subject

**Behavior**: No initial value, no replay. Late subscribers miss previous emissions.

```
Subject Timeline:
emit(1)  emit(2)  SubB  emit(3)  emit(4)
   │        │       │      │        │
   ▼        ▼       │      ▼        ▼
SubA: ─1────2───────│──────3────────4──
SubB: ──────────────┴──────3────────4──  (missed 1, 2)
```

```typescript
import { Subject } from 'rxjs';

const subject = new Subject<string>();

subject.subscribe(v => console.log('A:', v));
subject.next('First');  // A: First
subject.next('Second'); // A: Second

subject.subscribe(v => console.log('B:', v)); // B gets nothing yet
subject.next('Third');  // A: Third, B: Third
```

### BehaviorSubject

**Behavior**: Requires initial value. New subscribers immediately receive current value.

```
BehaviorSubject Timeline (initial: 0):
         emit(1)  SubB  emit(2)
            │       │      │
            ▼       │      ▼
SubA: ─0────1───────│──────2──
SubB: ──────────────1──────2──  (got current value immediately)
```

```typescript
import { BehaviorSubject } from 'rxjs';

const behavior$ = new BehaviorSubject<number>(0); // Initial value required

behavior$.subscribe(v => console.log('A:', v)); // A: 0 (immediate)
behavior$.next(1); // A: 1
behavior$.next(2); // A: 2

behavior$.subscribe(v => console.log('B:', v)); // B: 2 (current value)
behavior$.next(3); // A: 3, B: 3

// Access current value synchronously
console.log('Current:', behavior$.getValue()); // Current: 3
// Or use .value property
console.log('Current:', behavior$.value); // Current: 3
```

**Use Cases**: 
- Component state
- Current user/auth state
- Selected item tracking
- Any state that always has a value

### ReplaySubject

**Behavior**: Replays specified number of previous values to new subscribers.

```
ReplaySubject(2) Timeline:
emit(1)  emit(2)  emit(3)  SubB  emit(4)
   │        │        │       │      │
   ▼        ▼        ▼       │      ▼
SubA: ─1────2────────3───────│──────4──
SubB: ───────────────────────2,3────4──  (replayed last 2)
```

```typescript
import { ReplaySubject } from 'rxjs';

// Replay last 2 values
const replay$ = new ReplaySubject<number>(2);

replay$.next(1);
replay$.next(2);
replay$.next(3);

replay$.subscribe(v => console.log('Late subscriber:', v));
// Late subscriber: 2
// Late subscriber: 3

// Time-based replay: replay values from last 500ms
const timeReplay$ = new ReplaySubject<number>(Infinity, 500);
```

**Use Cases**:
- Caching responses
- Chat history
- Undo/redo functionality
- Late subscriber catch-up

### AsyncSubject

**Behavior**: Only emits the last value, and only when complete() is called.

```
AsyncSubject Timeline:
emit(1)  emit(2)  emit(3)  complete()
   │        │        │          │
   ▼        ▼        ▼          │
SubA: ─────────────────────────3│  (only last value on complete)
SubB: ─────────────────────────3│
```

```typescript
import { AsyncSubject } from 'rxjs';

const async$ = new AsyncSubject<number>();

async$.subscribe(v => console.log('A:', v)); // Nothing yet

async$.next(1); // Nothing emitted
async$.next(2); // Nothing emitted
async$.next(3); // Nothing emitted
async$.complete(); // A: 3 (only now!)

async$.subscribe(v => console.log('B:', v)); // B: 3 (replays last value)
```

**Use Cases**:
- HTTP-like request/response
- Computation results
- When only final value matters

### Subject Types Comparison

| Subject Type | Initial Value | Replay | When Emits |
|--------------|---------------|--------|------------|
| Subject | No | None | Immediately on next() |
| BehaviorSubject | Required | Last 1 | Immediately on next() |
| ReplaySubject | No | Configurable (n) | Immediately on next() |
| AsyncSubject | No | Last 1 | Only on complete() |

```typescript
// Choosing the right Subject
class StateService {
  // BehaviorSubject for state - always has a value
  private userSubject = new BehaviorSubject<User | null>(null);
  user$ = this.userSubject.asObservable();
  
  // Subject for events/actions - no need for replay
  private actionSubject = new Subject<Action>();
  action$ = this.actionSubject.asObservable();
  
  // ReplaySubject for data that late subscribers need
  private messagesSubject = new ReplaySubject<Message>(50);
  messages$ = this.messagesSubject.asObservable();
}
```

---

## Creation Operators

### of()

Creates an observable from arguments, emits synchronously, then completes.

```
of(1, 2, 3):
──1──2──3──|
```

```typescript
import { of } from 'rxjs';

of(1, 2, 3).subscribe({
  next: v => console.log(v),
  complete: () => console.log('Done')
});
// 1, 2, 3, Done

of([1, 2, 3]).subscribe(v => console.log(v));
// [1, 2, 3] (array as single value)

// Use for mock data, default values
of({ name: 'Angular', version: 17 }).subscribe(console.log);
```

### from()

Creates observable from array, iterable, Promise, or Observable-like.

```
from([1, 2, 3]):
──1──2──3──|
```

```typescript
import { from } from 'rxjs';

// From array - emits each element
from([1, 2, 3]).subscribe(console.log);
// 1, 2, 3

// From Promise
from(fetch('/api/users')).subscribe(response => console.log(response));

// From iterable (string)
from('RxJS').subscribe(console.log);
// R, x, J, S

// From generator
function* generator() {
  yield 1;
  yield 2;
  yield 3;
}
from(generator()).subscribe(console.log);
// 1, 2, 3
```

### interval()

Emits sequential numbers at specified interval (ms).

```
interval(1000):
──0──1──2──3──4──5── ... (never completes)
  1s  1s  1s  1s
```

```typescript
import { interval } from 'rxjs';
import { take } from 'rxjs/operators';

// Emits 0, 1, 2, 3... every second
interval(1000).pipe(take(5)).subscribe(console.log);
// 0 (after 1s), 1 (after 2s), 2 (after 3s), 3        (after 4s), 4 (after 5s)

// Polling pattern
interval(5000).pipe(
  switchMap(() => this.http.get('/api/status'))
).subscribe(status => this.updateStatus(status));
```

### timer()

Emits after initial delay, then optionally at intervals.

```
timer(2000):
────────0|  (single emission after 2s, then complete)

timer(1000, 500):
──────0──1──2──3──4── ... (first after 1s, then every 500ms)
  1s   500ms
```

```typescript
import { timer } from 'rxjs';
import { take } from 'rxjs/operators';

// Single emission after delay
timer(2000).subscribe(() => console.log('2 seconds passed'));

// Delayed start + interval
timer(1000, 500).pipe(take(4)).subscribe(console.log);
// 0 (after 1s), 1 (after 1.5s), 2 (after 2s), 3 (after 2.5s)

// Delayed execution
timer(0).subscribe(() => {
  // Runs in next microtask (like setTimeout(0))
});
```

### fromEvent()

Creates observable from DOM events or EventEmitter.

```
fromEvent(button, 'click'):
──────click──────click──click──── ...
```

```typescript
import { fromEvent } from 'rxjs';
import { map, debounceTime, distinctUntilChanged } from 'rxjs/operators';

// Button clicks
const button = document.getElementById('myButton');
fromEvent(button, 'click').subscribe(event => {
  console.log('Button clicked!', event);
});

// Input with debounce (search-as-you-type)
const searchInput = document.getElementById('search');
fromEvent(searchInput, 'input').pipe(
  map((event: Event) => (event.target as HTMLInputElement).value),
  debounceTime(300),
  distinctUntilChanged()
).subscribe(searchTerm => {
  console.log('Search for:', searchTerm);
});

// Window resize
fromEvent(window, 'resize').pipe(
  debounceTime(200),
  map(() => ({ width: window.innerWidth, height: window.innerHeight }))
).subscribe(dimensions => console.log(dimensions));

// Keyboard events
fromEvent<KeyboardEvent>(document, 'keydown').pipe(
  filter(event => event.key === 'Escape')
).subscribe(() => this.closeModal());
```

### Other Useful Creation Operators

```typescript
import { 
  EMPTY, NEVER, throwError, defer, range, 
  generate, combineLatest, forkJoin, merge, concat 
} from 'rxjs';

// EMPTY - completes immediately with no values
EMPTY.subscribe({
  complete: () => console.log('Completed immediately')
});

// NEVER - never emits, never completes
NEVER.subscribe(); // Useful for testing

// throwError - immediately errors
throwError(() => new Error('Oops!')).subscribe({
  error: err => console.error(err.message)
});

// defer - creates observable lazily on subscribe
const deferred$ = defer(() => {
  console.log('Creating now!');
  return of(Date.now());
});

// range - emits range of numbers
range(1, 5).subscribe(console.log); // 1, 2, 3, 4, 5
```

---

## Transformation Operators

### map()

Transforms each emitted value.

```
source:    ──1────2────3────4──|
map(x => x * 10)
result:    ──10───20───30───40─|
```

```typescript
import { of, from } from 'rxjs';
import { map } from 'rxjs/operators';

of(1, 2, 3).pipe(
  map(x => x * 10)
).subscribe(console.log);
// 10, 20, 30

// Extract property
this.http.get<User[]>('/api/users').pipe(
  map(users => users.filter(u => u.active)),
  map(users => users.length)
).subscribe(count => console.log('Active users:', count));
```

### Higher-Order Mapping Operators (flattening)

These operators handle inner observables - they "flatten" Observable<Observable<T>> to Observable<T>.

#### switchMap

**Behavior**: Cancels previous inner observable when new source value arrives.

```
source:     ──a─────────b─────────c────|
               \         \         \
inner:          ─1─2─3─|  ─1─2─3─|  ─1─2─3─|
                    X cancel    X cancel
switchMap
result:     ────1─2─────1─2───────1─2─3─|
```

```typescript
import { fromEvent, interval } from 'rxjs';
import { switchMap, take } from 'rxjs/operators';

// Type-ahead search - cancel previous HTTP request on new input
this.searchInput.valueChanges.pipe(
  debounceTime(300),
  distinctUntilChanged(),
  switchMap(term => this.searchService.search(term)) // Previous search canceled
).subscribe(results => this.results = results);

// Click starts new timer, clicking again resets
fromEvent(button, 'click').pipe(
  switchMap(() => interval(1000).pipe(take(5)))
).subscribe(console.log);
```

**Use Cases**: Search, autocomplete, navigation, any "latest wins" scenario.

#### mergeMap

**Behavior**: Runs all inner observables concurrently, no cancellation.

```
source:     ──a─────────b─────────c────|
               \         \         \
inner:          ─1─2─3─|  ─1─2─3─|  ─1─2─3─|
mergeMap
result:     ────1─2─3─────1─2─3─────1─2─3─|
                       (all run, results interleaved)
```

```typescript
import { from } from 'rxjs';
import { mergeMap, delay } from 'rxjs/operators';

// Process all items in parallel
from([1, 2, 3]).pipe(
  mergeMap(id => this.http.get(`/api/item/${id}`))
).subscribe(item => console.log('Loaded:', item));

// With concurrency limit
from(urls).pipe(
  mergeMap(url => this.http.get(url), 3) // Max 3 concurrent requests
).subscribe(response => this.process(response));

// Save all changes in parallel
this.changes$.pipe(
  mergeMap(change => this.saveChange(change))
).subscribe();
```

**Use Cases**: Parallel execution, batch operations, when order doesn't matter.

#### concatMap

**Behavior**: Queues inner observables, runs sequentially, waits for each to complete.

```
source:     ──a─────b─────c────|
               \
inner:          ─1─2─3─|
                        \
concatMap                ─1─2─3─|
result:     ────1─2─3─────1─2─3─────1─2─3─|
                       (sequential, in order)
```

```typescript
import { from } from 'rxjs';
import { concatMap, delay } from 'rxjs/operators';

// Sequential API calls - order matters
from([1, 2, 3]).pipe(
  concatMap(id => this.http.post(`/api/process/${id}`, {}))
).subscribe(result => console.log('Processed:', result));

// Animation sequence
from(['fadeIn', 'slideUp', 'pulse']).pipe(
  concatMap(animation => this.animate(element, animation))
).subscribe();

// Transaction steps (must be in order)
this.transactionSteps$.pipe(
  concatMap(step => this.executeStep(step))
).subscribe();
```

**Use Cases**: Sequential operations, transactions, animations, when order matters.

#### exhaustMap

**Behavior**: Ignores new source values while inner observable is active.

```
source:     ──a────b────c──────d────|
               \   X(ignored)   \
inner:          ─1─2─3─|         ─1─2─3─|
exhaustMap
result:     ────1─2─3───────────1─2─3─|
```

```typescript
import { fromEvent } from 'rxjs';
import { exhaustMap } from 'rxjs/operators';

// Prevent double-submit - ignore clicks while saving
fromEvent(saveButton, 'click').pipe(
  exhaustMap(() => this.http.post('/api/save', this.formData))
).subscribe(response => {
  this.showSuccess('Saved!');
});

// Refresh button - ignore rapid clicks
this.refresh$.pipe(
  exhaustMap(() => this.loadData())
).subscribe(data => this.data = data);

// Login - ignore additional attempts while logging in
this.loginForm.submit$.pipe(
  exhaustMap(credentials => this.authService.login(credentials))
).subscribe();
```

**Use Cases**: Form submission, preventing double-clicks, rate limiting user actions.

### Comparison of Flattening Operators

```
Given: outer emits A, then B while A's inner is still running

switchMap:  ──A─────B─────|         (B cancels A's inner)
mergeMap:   ──A─────B─────|         (Both run concurrently)
concatMap:  ──A─────B─────|         (B waits for A's inner to complete)
exhaustMap: ──A─────B─────|         (B is completely ignored)
```

| Operator | Inner Running | New Value Arrives | Use Case |
|----------|--------------|-------------------|----------|
| switchMap | Cancel inner | Start new inner | Search, navigation |
| mergeMap | Keep running | Start new inner (parallel) | Parallel requests |
| concatMap | Keep running | Queue new inner | Sequential ops |
| exhaustMap | Keep running | Ignore new value | Prevent double-submit |

### Decision Tree

```
Need to flatten inner observables?
│
├── Should new value cancel previous? ──► switchMap
│
├── Should all run in parallel? ──► mergeMap
│
├── Must run sequentially? ──► concatMap
│
└── Should ignore while busy? ──► exhaustMap
```

---

## Filtering Operators

### filter()

Only emits values that pass the predicate.

```
source:    ──1──2──3──4──5──6──|
filter(x => x % 2 === 0)
result:    ─────2─────4─────6──|
```

```typescript
import { from, interval } from 'rxjs';
import { filter, take } from 'rxjs/operators';

from([1, 2, 3, 4, 5]).pipe(
  filter(n => n > 2)
).subscribe(console.log);
// 3, 4, 5

// Filter with type guard
interface Cat { meow(): void; }
interface Dog { bark(): void; }
type Pet = Cat | Dog;

const pets$: Observable<Pet> = // ...
pets$.pipe(
  filter((pet): pet is Cat => 'meow' in pet)
).subscribe(cat => cat.meow()); // TypeScript knows it's Cat
```

### take()

Takes first n values then completes.

```
source:    ──1──2──3──4──5──6──|
take(3)
result:    ──1──2──3|
```

```typescript
import { interval } from 'rxjs';
import { take } from 'rxjs/operators';

interval(1000).pipe(
  take(5)
).subscribe({
  next: v => console.log(v),
  complete: () => console.log('Took 5 values')
});
// 0, 1, 2, 3, 4, Took 5 values
```

### takeUntil()

Takes values until notifier observable emits.

```
source:    ──1──2──3──4──5──6──|
notifier:  ────────────X
takeUntil(notifier)
result:    ──1──2──3──|
```

```typescript
import { interval, Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';

// Component cleanup pattern
@Component({ /* ... */ })
export class MyComponent implements OnDestroy {
  private destroy$ = new Subject<void>();
  
  ngOnInit() {
    interval(1000).pipe(
      takeUntil(this.destroy$)
    ).subscribe(v => console.log(v));
    
    this.someService.data$.pipe(
      takeUntil(this.destroy$)
    ).subscribe(data => this.data = data);
  }
  
  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

### distinctUntilChanged()

Only emits when value is different from previous.

```
source:    ──1──1──2──2──2──3──1──|
distinctUntilChanged()
result:    ──1─────2────────3──1──|
```

```typescript
import { of, from } from 'rxjs';
import { distinctUntilChanged } from 'rxjs/operators';

from([1, 1, 2, 2, 3, 3, 1]).pipe(
  distinctUntilChanged()
).subscribe(console.log);
// 1, 2, 3, 1

// With custom comparator (for objects)
this.user$.pipe(
  distinctUntilChanged((prev, curr) => prev.id === curr.id)
).subscribe(user => console.log('User changed:', user));

// Using keySelector
this.user$.pipe(
  distinctUntilChanged((prev, curr) => prev === curr, user => user.id)
).subscribe(user => console.log('User ID changed:', user));
```

### debounceTime()

Emits value only after specified silence period.

```
source:    ──a──b──c──────d──e────|
debounceTime(200ms)
result:    ─────────c────────e────|
              (200ms silence after c and e)
```

```typescript
import { fromEvent } from 'rxjs';
import { debounceTime, map, distinctUntilChanged } from 'rxjs/operators';

// Search input - wait for user to stop typing
fromEvent(searchInput, 'input').pipe(
  map(e => (e.target as HTMLInputElement).value),
  debounceTime(300),
  distinctUntilChanged()
).subscribe(term => this.search(term));

// Window resize - wait for resize to finish
fromEvent(window, 'resize').pipe(
  debounceTime(200)
).subscribe(() => this.recalculateLayout());
```

### throttleTime()

Emits first value, then ignores for specified duration.

```
source:    ──a──b──c──d──e──f──g──|
throttleTime(200ms)
result:    ──a────────d────────g──|
              (200ms gap after each emission)
```

```typescript
import { fromEvent } from 'rxjs';
import { throttleTime } from 'rxjs/operators';

// Scroll handler - limit to once per 100ms
fromEvent(window, 'scroll').pipe(
  throttleTime(100)
).subscribe(() => this.handleScroll());

// Button clicks - prevent rapid firing
fromEvent(button, 'click').pipe(
  throttleTime(1000)
).subscribe(() => this.performAction());

// With configuration
fromEvent(document, 'mousemove').pipe(
  throttleTime(100, asyncScheduler, { leading: true, trailing: true })
).subscribe(e => this.trackMouse(e));
```

### debounceTime vs throttleTime

```
Input:     ─a─b─c─d─e─────f─g─|
                    (500ms gap)

debounceTime(200ms):
result:    ─────────e─────────g─|
           (waits for silence)

throttleTime(200ms):
result:    ─a─────d───────f───|
           (emits first, ignores rest for duration)
```

| Aspect | debounceTime | throttleTime |
|--------|--------------|--------------|
| **Emits** | After silence | First, then ignores |
| **Use Case** | Search, resize | Scroll, mouse move |
| **Behavior** | Wait for pause | Rate limit |

---

## Error Handling

### catchError()

Catches errors and returns a replacement observable.

```
source:    ──1──2──X (error)
catchError(() => of('fallback'))
result:    ──1──2──fallback──|
```

```typescript
import { of, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

// Return fallback value
this.http.get('/api/config').pipe(
  catchError(err => {
    console.error('Failed to load config:', err);
    return of(defaultConfig); // Return default
  })
).subscribe(config => this.config = config);

// Rethrow with more context
this.http.get('/api/user').pipe(
  catchError(err => {
    return throwError(() => new Error(`User fetch failed: ${err.message}`));
  })
).subscribe({
  next: user => this.user = user,
  error: err => this.showError(err.message)
});

// Different handling per error type
this.http.get('/api/data').pipe(
  catchError(err => {
    if (err.status === 404) {
      return of(null); // Not found is OK
    }
    if (err.status === 401) {
      this.router.navigate(['/login']);
      return EMPTY;
    }
    return throwError(() => err); // Rethrow other errors
  })
).subscribe(data => this.data = data);
```

### retry()

Retries the source observable on error.

```
source (fails first 2 times):
attempt 1: ──1──X (error)
attempt 2: ──1──X (error)
attempt 3: ──1──2──3──|

retry(3)
result:    ────────────1──2──3──|
```

```typescript
import { interval, throwError } from 'rxjs';
import { retry, mergeMap } from 'rxjs/operators';

// Simple retry
this.http.get('/api/flaky-endpoint').pipe(
  retry(3) // Retry up to 3 times
).subscribe(data => console.log(data));

// Retry with delay (RxJS 7+)
this.http.get('/api/data').pipe(
  retry({
    count: 3,
    delay: 1000 // Wait 1s between retries
  })
).subscribe(data => this.data = data);

// Exponential backoff retry
this.http.get('/api/data').pipe(
  retry({
    count: 3,
    delay: (error, retryCount) => timer(Math.pow(2, retryCount) * 1000)
  })
).subscribe(data => this.data = data);
```

### retryWhen() (deprecated in RxJS 7+, use retry with config)

```typescript
import { timer, throwError } from 'rxjs';
import { retryWhen, delayWhen, take, tap } from 'rxjs/operators';

// Legacy approach (still works but deprecated)
this.http.get('/api/data').pipe(
  retryWhen(errors => errors.pipe(
    tap(err => console.log('Retrying...', err)),
    delayWhen((_, i) => timer(Math.pow(2, i) * 1000)),
    take(3)
  ))
).subscribe(data => this.data = data);

// Modern approach (RxJS 7+)
this.http.get('/api/data').pipe(
  retry({
    count: 3,
    delay: (error, retryCount) => {
      console.log(`Retry ${retryCount} after error:`, error);
      return timer(Math.pow(2, retryCount) * 1000);
    }
  })
).subscribe(data => this.data = data);
```

### Complete Error Handling Pattern

```typescript
import { of, timer, throwError, EMPTY } from 'rxjs';
import { catchError, retry, finalize, tap } from 'rxjs/operators';

// Comprehensive error handling
this.http.get('/api/important-data').pipe(
  tap(() => this.loading = true),
  retry({
    count: 3,
    delay: (error, retryCount) => {
      if (error.status === 404) {
        // Don't retry 404s
        return throwError(() => error);
      }
      // Exponential backoff for other errors
      return timer(1000 * Math.pow(2, retryCount));
    }
  }),
  catchError(err => {
    this.errorService.log(err);
    
    if (err.status === 404) {
      return of(null);
    }
    if (err.status === 401) {
      this.authService.logout();
      return EMPTY;
    }
    
    this.notificationService.showError('Failed to load data');
    return throwError(() => err);
  }),
  finalize(() => {
    this.loading = false; // Always runs
  })
).subscribe({
  next: data => this.data = data,
  error: err => console.error('Unhandled error:', err)
});
```

---

## Cleanup Patterns

### The takeUntil Pattern (Pre-Angular 16)

```typescript
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { Component, OnDestroy, OnInit } from '@angular/core';

@Component({
  selector: 'app-example',
  template: `...`
})
export class ExampleComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  
  data: any;
  
  ngOnInit() {
    // All subscriptions use takeUntil
    this.dataService.getData().pipe(
      takeUntil(this.destroy$)
    ).subscribe(data => this.data = data);
    
    this.authService.user$.pipe(
      takeUntil(this.destroy$)
    ).subscribe(user => this.currentUser = user);
    
    interval(1000).pipe(
      takeUntil(this.destroy$)
    ).subscribe(tick => this.handleTick(tick));
  }
  
  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

### takeUntilDestroyed (Angular 16+)

```typescript
import { Component, OnInit, inject, DestroyRef } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { interval } from 'rxjs';

@Component({
  selector: 'app-modern',
  template: `...`
})
export class ModernComponent implements OnInit {
  private destroyRef = inject(DestroyRef);
  private dataService = inject(DataService);
  
  data: any;
  
  ngOnInit() {
    // Automatic cleanup - no ngOnDestroy needed!
    this.dataService.getData().pipe(
      takeUntilDestroyed(this.destroyRef)
    ).subscribe(data => this.data = data);
    
    interval(1000).pipe(
      takeUntilDestroyed(this.destroyRef)
    ).subscribe(tick => this.handleTick(tick));
  }
}

// Even cleaner in constructor
@Component({
  selector: 'app-cleaner',
  template: `...`
})
export class CleanerComponent {
  private dataService = inject(DataService);
  
  // Subscribe in constructor - takeUntilDestroyed auto-injects DestroyRef
  data$ = this.dataService.getData();
  
  constructor() {
    // No DestroyRef needed in constructor context
    interval(1000).pipe(
      takeUntilDestroyed() // Auto-injects from injection context
    ).subscribe(tick => this.handleTick(tick));
  }
}
```

### finalize() Operator

Executes callback when observable completes OR errors OR is unsubscribed.

```
source:    ──1──2──3──| (or error, or unsubscribe)
finalize(() => cleanup())
result:    ──1──2──3──| then cleanup() runs
```

```typescript
import { finalize, tap } from 'rxjs/operators';

// Loading indicator pattern
loadData() {
  this.loading = true;
  
  this.http.get('/api/data').pipe(
    finalize(() => {
      this.loading = false; // Always runs: success, error, or cancel
    })
  ).subscribe({
    next: data => this.data = data,
    error: err => this.handleError(err)
  });
}

// Resource cleanup
openConnection() {
  return this.websocket.connect().pipe(
    finalize(() => {
      console.log('Connection cleanup');
      this.websocket.close();
    })
  );
}

// Combined with other operators
this.dataService.stream$.pipe(
  takeUntil(this.destroy$),
  tap(data => this.process(data)),
  finalize(() => {
    console.log('Stream ended - cleanup');
    this.releaseResources();
  })
).subscribe();
```

### Subscription Management Patterns

```typescript
// Pattern 1: Single subscription variable
@Component({...})
export class SingleSubComponent implements OnDestroy {
  private subscription?: Subscription;
  
  ngOnInit() {
    this.subscription = this.data$.subscribe(...);
  }
  
  ngOnDestroy() {
    this.subscription?.unsubscribe();
  }
}

// Pattern 2: Subscription array
@Component({...})
export class MultiSubComponent implements OnDestroy {
  private subscriptions: Subscription[] = [];
  
  ngOnInit() {
    this.subscriptions.push(
      this.data1$.subscribe(...),
      this.data2$.subscribe(...)
    );
  }
  
  ngOnDestroy() {
    this.subscriptions.forEach(s => s.unsubscribe());
  }
}

// Pattern 3: Subscription.add()
@Component({...})
export class AddSubComponent implements OnDestroy {
  private subscription = new Subscription();
  
  ngOnInit() {
    this.subscription.add(this.data1$.subscribe(...));
    this.subscription.add(this.data2$.subscribe(...));
  }
  
  ngOnDestroy() {
    this.subscription.unsubscribe(); // Unsubscribes all
  }
}

// Pattern 4: AsyncPipe (recommended for templates)
@Component({
  template: `
    <div *ngIf="data$ | async as data">
      {{ data.name }}
    </div>
  `
})
export class AsyncPipeComponent {
  data$ = this.dataService.getData();
  // No manual subscription management needed!
}
```

### Best Practices Summary

| Scenario | Recommended Approach |
|----------|---------------------|
| Angular 16+ | `takeUntilDestroyed()` |
| Angular < 16 | `takeUntil(destroy$)` |
| Template binding | `async` pipe |
| Single subscription | Manual `unsubscribe()` |
| HTTP requests | Usually auto-complete, but use cleanup for cancellation |
| Loading states | `finalize()` |

---

## Marble Diagrams Reference

### Reading Marble Diagrams

```
Timeline: ────────────────────────────────────────►
                     (time flows left to right)

Symbols:
  ─     Time passing (no emission)
  a,b,c Letters/numbers represent emitted values  
  |     Completion (observable ends successfully)
  X     Error (observable ends with error)
  ^     Subscription point (for hot observables)
  !     Unsubscription point

Example:
  ──a──b──c──|
     ↑  ↑  ↑  ↑
     │  │  │  └─ Completes
     │  │  └─ Emits 'c'
     │  └─ Emits 'b'
     └─ Emits 'a'
```

### Key Operator Diagrams

```
═══════════════════════════════════════════════════════
map(x => x * 2)
═══════════════════════════════════════════════════════
source:    ──1────2────3────4──|
result:    ──2────4────6────8──|

═══════════════════════════════════════════════════════
filter(x => x > 2)
═══════════════════════════════════════════════════════
source:    ──1──2──3──4──5──|
result:    ────────3──4──5──|

═══════════════════════════════════════════════════════
take(3)
═══════════════════════════════════════════════════════
source:    ──1──2──3──4──5──6──|
result:    ──1──2──3|

═══════════════════════════════════════════════════════
switchMap (inner: ─x─y─|)
═══════════════════════════════════════════════════════
source:    ──A──────B──────C──|
              \       \       \
inner:         ─x─y─|  ─x─y─|  ─x─y─|
                  ↑ cancel ↑ cancel
result:    ────x────x────x─y─|

═══════════════════════════════════════════════════════
mergeMap (inner: ─x─y─|)
═══════════════════════════════════════════════════════
source:    ──A──────B──────C──|
              \       \       \
inner:         ─x─y─|  ─x─y─|  ─x─y─|
result:    ────x─y───x─y───x─y─|

═══════════════════════════════════════════════════════
concatMap (inner: ─x─y─|)
═══════════════════════════════════════════════════════
source:    ──A──B──C──|
              \
inner:         ─x─y─|
                     \
                      ─x─y─|
                           \
                            ─x─y─|
result:    ────x─y───x─y───x─y─|

═══════════════════════════════════════════════════════
exhaustMap (inner: ─x─y─z─|)
═══════════════════════════════════════════════════════
source:    ──A──B──C──────D──|
              \   ↓   ↓      \
inner:         ─x─y─z─|       ─x─y─z─|
              (B,C ignored)
result:    ────x─y─z─────────x─y─z─|

═══════════════════════════════════════════════════════
debounceTime(20)
═══════════════════════════════════════════════════════
source:    ──a─b─c──────d───e──|
                  ↓         ↓
result:    ─────────c──────────e|
           (20 units of silence before emit)

═══════════════════════════════════════════════════════
throttleTime(20)
═══════════════════════════════════════════════════════
source:    ──a─b─c─d─e──────f──|
              ↓             ↓
result:    ──a──────────────f──|
           (emit first, ignore for 20 units)

═══════════════════════════════════════════════════════
distinctUntilChanged()
═══════════════════════════════════════════════════════
source:    ──1──1──2──2──2──1──3──|
result:    ──1─────2────────1──3──|

═══════════════════════════════════════════════════════
takeUntil(notifier)
═══════════════════════════════════════════════════════
source:    ──1──2──3──4──5──6──|
notifier:  ──────────X
result:    ──1──2──3─|

═══════════════════════════════════════════════════════
catchError(err => of('fallback'))
═══════════════════════════════════════════════════════
source:    ──1──2──X
result:    ──1──2──fallback──|

═══════════════════════════════════════════════════════
retry(2)
═══════════════════════════════════════════════════════
source:    ──1──X  ──1──X  ──1──2──|
           attempt1 attempt2 attempt3
result:    ──────────────────1──2──|
```

---

## Quick Reference Card

### Creation Operators
```typescript
of(1, 2, 3)                    // Emit values synchronously
from([1, 2, 3])                // From array/iterable/Promise
interval(1000)                 // Emit 0, 1, 2... every 1s
timer(1000)                    // Single emit after 1s
timer(1000, 500)               // Start after 1s, then every 500ms
fromEvent(elem, 'click')       // From DOM event
EMPTY                          // Complete immediately
throwError(() => new Error())  // Error immediately
defer(() => of(...))           // Lazy creation
```

### Transformation Operators
```typescript
map(x => x * 2)                // Transform each value
switchMap(x => inner$)         // Cancel previous inner
mergeMap(x => inner$)          // Run all inners parallel
concatMap(x => inner$)         // Run inners sequentially
exhaustMap(x => inner$)        // Ignore while inner active
scan((acc, val) => acc + val)  // Accumulator (like reduce)
```

### Filtering Operators
```typescript
filter(x => x > 0)             // Filter by predicate
take(5)                        // Take first 5
takeUntil(notifier$)           // Take until notifier emits
takeWhile(x => x < 10)         // Take while condition true
skip(3)                        // Skip first 3
first()                        // First value then complete
last()                         // Last value then complete
distinctUntilChanged()         // Only emit if different
debounceTime(300)              // Wait for silence
throttleTime(300)              // Rate limit
```

### Combination Operators
```typescript
combineLatest([a$, b$])        // Latest from each
forkJoin([a$, b$])             // Wait for all to complete
merge(a$, b$)                  // Merge streams
concat(a$, b$)                 // Sequential streams
withLatestFrom(other$)         // Combine with latest
zip(a$, b$)                    // Pair by index
```

### Error Handling
```typescript
catchError(err => of(fallback)) // Handle error
retry(3)                        // Retry n times
retry({ count: 3, delay: 1000}) // Retry with delay
```

### Utility
```typescript
tap(x => console.log(x))       // Side effects (no transform)
finalize(() => cleanup())      // On complete/error/unsubscribe
delay(1000)                    // Delay emissions
timeout(5000)                  // Error if no emit in time
share()                        // Multicast (make hot)
shareReplay(1)                 // Multicast + replay
```

### Angular-Specific
```typescript
// Angular 16+ automatic cleanup
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

data$.pipe(
  takeUntilDestroyed()  // In constructor
).subscribe();

data$.pipe(
  takeUntilDestroyed(this.destroyRef)  // Outside constructor
).subscribe();
```

### Common Patterns
```typescript
// Search with debounce
searchInput.valueChanges.pipe(
  debounceTime(300),
  distinctUntilChanged(),
  switchMap(term => this.search(term))
)

// Prevent double-submit
clicks$.pipe(
  exhaustMap(() => this.save())
)

// Polling
interval(5000).pipe(
  switchMap(() => this.http.get('/api/status'))
)

// Cleanup pattern (Angular < 16)
private destroy$ = new Subject<void>();
ngOnInit() { source$.pipe(takeUntil(this.destroy$)).subscribe(); }
ngOnDestroy() { this.destroy$.next(); this.destroy$.complete(); }
```

---

## Key Takeaways

1. **Observables are lazy** - nothing happens until you subscribe
2. **Always clean up subscriptions** - use `takeUntilDestroyed`, `takeUntil`, or `async` pipe
3. **Choose the right flattening operator**:
   - `switchMap` for "latest wins" (search)
   - `mergeMap` for parallel execution
   - `concatMap` for sequential execution  
   - `exhaustMap` for ignoring while busy
4. **Use `BehaviorSubject` for state** - it always has a current value
5. **Marble diagrams help visualize** - draw them when debugging
6. **Error handling is crucial** - use `catchError` and `retry` appropriately
7. **`finalize` always runs** - perfect for cleanup and loading states
