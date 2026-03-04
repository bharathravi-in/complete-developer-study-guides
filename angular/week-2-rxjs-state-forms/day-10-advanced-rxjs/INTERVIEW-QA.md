# Day 10: Advanced RxJS - Interview Questions & Answers

## Question 1: combineLatest vs forkJoin - When to Use Each?

### Question
What are the differences between `combineLatest` and `forkJoin`? When would you use each?

### Answer

**Key Differences:**

| Aspect | combineLatest | forkJoin |
|--------|---------------|----------|
| Emissions | Multiple (every time any source emits) | Single (one array when all complete) |
| Timing | After all sources emit at least once | Only after all sources complete |
| Values | Latest from each source | Last value from each source |
| Use Case | Reactive, ongoing streams | One-time parallel operations |

**combineLatest:**
```typescript
// Reactive UI - emits on every change
combineLatest([
  this.searchControl.valueChanges.pipe(startWith('')),
  this.filterControl.valueChanges.pipe(startWith('all')),
  this.sortControl.valueChanges.pipe(startWith('date'))
]).subscribe(([search, filter, sort]) => {
  // Called every time any control changes
  this.applyFilters(search, filter, sort);
});
```

**forkJoin:**
```typescript
// Parallel HTTP - single result when all complete
forkJoin({
  user: this.userService.getUser(id),
  orders: this.orderService.getOrders(id),
  preferences: this.prefService.getPreferences(id)
}).subscribe(({ user, orders, preferences }) => {
  // Called once when ALL requests complete
  this.initializeDashboard(user, orders, preferences);
});
```

**Decision Guide:**
- Use `combineLatest` for ongoing reactive streams (form controls, state observables)
- Use `forkJoin` for one-time parallel operations (HTTP requests, file reads)
- `forkJoin` with infinite streams (interval, WebSocket) = **never emits**
- `combineLatest` needs initial values or `startWith()` for immediate emission

---

## Question 2: Why might forkJoin never emit?

### Question
You wrote this code but it never emits any value. What's wrong?

```typescript
forkJoin([
  this.http.get('/api/data'),
  interval(1000)
]).subscribe(data => console.log(data));
```

### Answer

**Problem:** `forkJoin` waits for ALL observables to complete. `interval(1000)` is an infinite stream that **never completes**, so `forkJoin` will never emit.

**Solutions:**

```typescript
// Solution 1: Take a finite number of values
forkJoin([
  this.http.get('/api/data'),
  interval(1000).pipe(take(5)) // Complete after 5 emissions
]).subscribe();

// Solution 2: Use combineLatest if you need ongoing emissions
combineLatest([
  this.http.get('/api/data').pipe(shareReplay(1)),
  interval(1000)
]).subscribe();

// Solution 3: Add timeout for safety
forkJoin([
  this.http.get('/api/data').pipe(timeout(5000)),
  someStream$.pipe(take(1))
]).subscribe();
```

**Common Infinite Streams to Watch:**
- `interval()`, `timer()` without count
- `fromEvent()` (click, scroll, etc.)
- `Subject`, `BehaviorSubject` (unless explicitly completed)
- WebSocket connections

---

## Question 3: merge vs concat - Execution Order

### Question
Explain the difference between `merge` and `concat`. Given these observables, what will each output?

```typescript
const a$ = of(1, 2).pipe(delay(100));
const b$ = of('a', 'b');
```

### Answer

**merge - Parallel execution, interleaved output:**
```typescript
merge(a$, b$).subscribe(console.log);
// Output: 'a', 'b', 1, 2
// b$ emits immediately, a$ emits after 100ms
```

**concat - Sequential execution, ordered output:**
```typescript
concat(a$, b$).subscribe(console.log);
// Output: 1, 2, 'a', 'b'
// Waits for a$ to complete, then subscribes to b$
```

**ASCII Marble Diagram:**
```
a$:      ---(1,2)|
b$:      (a,b)|

merge:   (a,b)---(1,2)|  // Parallel
concat:  ---(1,2)(a,b)|  // Sequential
```

**Use Cases:**

| Operator | Use When |
|----------|----------|
| `merge` | Multiple event sources (clicks, keys, touch) |
| `merge` | Race conditions needed |
| `merge` | Real-time data from multiple sources |
| `concat` | Order matters (validate → save → notify) |
| `concat` | Rate-limited APIs (one request at a time) |
| `concat` | Sequential file uploads |

```typescript
// merge: Multiple user interaction types
merge(
  fromEvent(el, 'click'),
  fromEvent(el, 'touchstart'),
  fromEvent(el, 'keydown')
).pipe(take(1)).subscribe(() => {
  this.showTooltip();
});

// concat: Sequential save operations
concat(
  this.validate(),
  this.save(),
  this.notify()
).subscribe();
```

---

## Question 4: shareReplay Memory Leak

### Question
What's the potential issue with this service code? How would you fix it?

```typescript
@Injectable({ providedIn: 'root' })
export class DataService {
  readonly data$ = this.http.get('/api/data').pipe(
    shareReplay(1)
  );
}
```

### Answer

**Issue:** `shareReplay(1)` defaults to `refCount: false`, meaning:
- The HTTP subscription stays active even when all subscribers disconnect
- Cached data persists forever (could become stale)
- Memory never released

**Solutions:**

```typescript
// Solution 1: Use refCount: true
@Injectable({ providedIn: 'root' })
export class DataService {
  readonly data$ = this.http.get('/api/data').pipe(
    shareReplay({ bufferSize: 1, refCount: true })
  );
  // Re-fetches when new subscriber arrives after all unsubscribed
}

// Solution 2: Implement cache invalidation
@Injectable({ providedIn: 'root' })
export class DataService {
  private cache$: Observable<Data> | null = null;
  
  getData(): Observable<Data> {
    if (!this.cache$) {
      this.cache$ = this.http.get<Data>('/api/data').pipe(
        shareReplay({ bufferSize: 1, refCount: false })
      );
    }
    return this.cache$;
  }
  
  invalidateCache(): void {
    this.cache$ = null;
  }
}

// Solution 3: Time-based cache with share()
@Injectable({ providedIn: 'root' })
export class DataService {
  readonly data$ = this.http.get('/api/data').pipe(
    share({
      connector: () => new ReplaySubject(1),
      resetOnRefCountZero: () => timer(60000) // 60s cache
    })
  );
}
```

**refCount Comparison:**

| `refCount: false` | `refCount: true` |
|-------------------|------------------|
| Subscription persists | Unsubscribes when count hits 0 |
| Good for app-wide config | Good for component-scoped data |
| Manual invalidation needed | Auto re-fetch on new subscription |
| Potential memory leak | Potential unnecessary re-fetches |

---

## Question 5: Creating a Custom Debounced Input Operator

### Question
Create a custom RxJS operator for search input that:
1. Trims whitespace
2. Ignores inputs shorter than 3 characters
3. Debounces by 300ms
4. Only emits distinct values

### Answer

```typescript
import { MonoTypeOperatorFunction, pipe } from 'rxjs';
import { 
  map, 
  filter, 
  debounceTime, 
  distinctUntilChanged 
} from 'rxjs/operators';

interface SearchInputConfig {
  minLength?: number;
  debounceMs?: number;
}

function searchInput(config: SearchInputConfig = {}): MonoTypeOperatorFunction<string> {
  const { minLength = 3, debounceMs = 300 } = config;
  
  return pipe(
    map(value => value?.trim() ?? ''),
    debounceTime(debounceMs),
    filter(value => value.length === 0 || value.length >= minLength),
    distinctUntilChanged()
  );
}

// Usage
@Component({
  template: `<input [formControl]="searchControl">`
})
export class SearchComponent {
  searchControl = new FormControl('');
  
  constructor() {
    this.searchControl.valueChanges.pipe(
      searchInput({ minLength: 2, debounceMs: 400 })
    ).subscribe(query => {
      if (query) {
        this.search(query);
      } else {
        this.clearResults();
      }
    });
  }
}
```

**Key Pattern:** Use `pipe()` function to compose existing operators rather than creating from scratch. This is:
- More maintainable
- Less error-prone
- Better type inference
- Easier to test

---

## Question 6: withLatestFrom vs combineLatest

### Question
What's the difference between these two approaches? When would you prefer each?

```typescript
// Approach A
click$.pipe(
  withLatestFrom(state$)
).subscribe(([click, state]) => {});

// Approach B
combineLatest([click$, state$])
  .subscribe(([click, state]) => {});
```

### Answer

**Key Difference: Which stream triggers emissions**

| Operator | Triggers On | Other Streams |
|----------|-------------|---------------|
| `withLatestFrom` | Source only (`click$`) | Provide context values |
| `combineLatest` | Any stream | All are equal |

**Approach A (withLatestFrom):**
```
click$: ----x---------x------|
state$: --A----B--C----------|
output: ----[x,A]-----[x,C]--|

- Emits ONLY when click$ emits
- state$ changes alone don't trigger emissions
```

**Approach B (combineLatest):**
```
click$: ----x---------x------|
state$: --A----B--C----------|
output: ----[x,A]-[x,B][x,C]-[x,C]|

- Emits when EITHER stream emits
- Would need additional filtering for click-only behavior
```

**Use Cases:**

```typescript
// withLatestFrom: Action + context
submitButton$.pipe(
  withLatestFrom(formValue$, userPermissions$),
  filter(([_, form, perms]) => perms.canSubmit),
  exhaustMap(([_, form]) => this.api.submit(form))
);

// combineLatest: Reactive derived state
combineLatest([
  selectedProduct$,
  quantity$,
  discountCode$
]).pipe(
  map(([product, qty, discount]) => 
    calculateTotal(product, qty, discount)
  )
);
```

**Rule of thumb:**
- User action + current state → `withLatestFrom`
- Derived state from multiple sources → `combineLatest`

---

## Question 7: BehaviorSubject vs ReplaySubject vs Subject

### Question
Explain the differences between Subject, BehaviorSubject, and ReplaySubject. When would you use each?

### Answer

**Comparison Table:**

| Feature | Subject | BehaviorSubject | ReplaySubject |
|---------|---------|-----------------|---------------|
| Initial value | No | **Required** | No |
| New subscriber receives | Nothing | Current value | Last N values |
| Sync value access | No | **Yes** (`.getValue()`) | No |
| Memory usage | Low | Low | Can grow |

**ASCII Marble Diagrams:**

```
Subject:
              --1--2--3--|
Subscriber A: --1--2--3--|  (subscribes at start)
Subscriber B:       --3--|  (subscribes after 2, misses 1,2)

BehaviorSubject(0):
              --1--2--3--|
Subscriber A: 0-1--2--3--|  (gets initial 0 immediately)
Subscriber B:      (2)3--|  (gets current value 2 immediately)

ReplaySubject(2):
              --1--2--3--|
Subscriber A: --1--2--3--|  (subscribes at start)
Subscriber B:      (1,2)3|  (replays last 2: 1, 2)
```

**When to Use:**

```typescript
// Subject: Event bus, no history needed
private action$ = new Subject<Action>();
dispatch(action: Action) {
  this.action$.next(action);
}

// BehaviorSubject: State management, need current value
private state$ = new BehaviorSubject<AppState>(initialState);
getSnapshot(): AppState {
  return this.state$.getValue(); // Sync access
}

// ReplaySubject: Late subscribers need history
private chatHistory$ = new ReplaySubject<Message>(50); // Keep last 50
// New users joining chat get recent history
```

**Common Pitfall:**
```typescript
// ❌ Anti-pattern: Using getValue() in reactive chains
this.state$.pipe(
  map(state => {
    const other = this.other$.getValue(); // Breaks reactivity!
    return combine(state, other);
  })
);

// ✅ Correct: Use operators
combineLatest([this.state$, this.other$]).pipe(
  map(([state, other]) => combine(state, other))
);
```

---

## Question 8: Implementing a Cache with TTL

### Question
Implement a caching service with Time To Live (TTL) using RxJS operators.

### Answer

```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, share, timer, ReplaySubject, EMPTY } from 'rxjs';
import { tap, switchMap, catchError, takeUntil } from 'rxjs/operators';

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

@Injectable({ providedIn: 'root' })
export class CachingService {
  private http = inject(HttpClient);
  private cache = new Map<string, CacheEntry<unknown>>();
  private inFlight = new Map<string, Observable<unknown>>();
  
  get<T>(url: string, ttlMs: number = 60000): Observable<T> {
    // Check memory cache
    const cached = this.cache.get(url) as CacheEntry<T> | undefined;
    if (cached && Date.now() - cached.timestamp < ttlMs) {
      return of(cached.data);
    }
    
    // Check if request already in flight (deduplication)
    if (this.inFlight.has(url)) {
      return this.inFlight.get(url) as Observable<T>;
    }
    
    // Make new request
    const request$ = this.http.get<T>(url).pipe(
      tap(data => {
        this.cache.set(url, { data, timestamp: Date.now() });
        this.inFlight.delete(url);
      }),
      catchError(err => {
        this.inFlight.delete(url);
        throw err;
      }),
      share() // Share among concurrent subscribers
    );
    
    this.inFlight.set(url, request$);
    return request$;
  }
  
  invalidate(url: string): void {
    this.cache.delete(url);
  }
  
  invalidateAll(): void {
    this.cache.clear();
  }
}

// Advanced: Auto-expiring cache with share()
@Injectable({ providedIn: 'root' })
export class AutoExpiringCache {
  private http = inject(HttpClient);
  
  // Cache that auto-invalidates after TTL
  getCached<T>(url: string, ttlMs: number = 60000): Observable<T> {
    return this.http.get<T>(url).pipe(
      share({
        connector: () => new ReplaySubject<T>(1),
        resetOnComplete: false,
        resetOnError: true,
        resetOnRefCountZero: () => timer(ttlMs)
      })
    );
  }
}
```

**Usage:**
```typescript
@Component({...})
export class ProductComponent {
  private cache = inject(CachingService);
  
  product$ = this.cache.get<Product>(
    `/api/products/${this.id}`,
    5 * 60 * 1000 // 5 minute TTL
  );
}
```

---

## Question 9: Error Handling in forkJoin

### Question
If one of the observables in forkJoin errors, what happens? How do you handle partial failures?

### Answer

**Default Behavior:** If ANY observable errors, the entire `forkJoin` fails.

```typescript
// ❌ One error kills everything
forkJoin({
  users: this.http.get('/api/users'),     // Success
  posts: this.http.get('/api/posts'),     // ERROR!
  comments: this.http.get('/api/comments') // Never reached
}).subscribe({
  next: data => console.log(data),  // Never called
  error: err => console.log('All failed!') // Called
});
```

**Solution: Handle errors individually**

```typescript
// ✅ Graceful degradation
forkJoin({
  users: this.http.get('/api/users').pipe(
    catchError(err => {
      console.error('Users failed:', err);
      return of([]); // Return empty array as fallback
    })
  ),
  posts: this.http.get('/api/posts').pipe(
    catchError(err => of([]))
  ),
  comments: this.http.get('/api/comments').pipe(
    catchError(err => of([]))
  )
}).subscribe({
  next: ({ users, posts, comments }) => {
    // All arrays, some may be empty
    this.render(users, posts, comments);
  }
});

// ✅ With error tracking
interface ResultWithError<T> {
  data: T | null;
  error: Error | null;
}

function wrapWithErrorHandling<T>(obs$: Observable<T>): Observable<ResultWithError<T>> {
  return obs$.pipe(
    map(data => ({ data, error: null })),
    catchError(error => of({ data: null, error }))
  );
}

forkJoin({
  users: wrapWithErrorHandling(this.http.get('/api/users')),
  posts: wrapWithErrorHandling(this.http.get('/api/posts'))
}).subscribe(({ users, posts }) => {
  if (users.error) {
    this.showError('Users', users.error);
  } else {
    this.displayUsers(users.data);
  }
  
  if (posts.error) {
    this.showError('Posts', posts.error);
  } else {
    this.displayPosts(posts.data);
  }
});
```

---

## Question 10: Hot vs Cold Observables and Multicasting

### Question
What are hot and cold observables? How does `share()` convert a cold observable to hot?

### Answer

**Cold Observable:**
- Created fresh for each subscriber
- Each subscriber gets its own independent execution
- Example: HTTP requests, `of()`, `from()`

```typescript
// Cold: Each subscription = new HTTP request
const cold$ = this.http.get('/api/data');
cold$.subscribe(); // Request 1
cold$.subscribe(); // Request 2 (separate request!)
```

**Hot Observable:**
- Shared execution among all subscribers
- Late subscribers miss earlier emissions
- Example: `fromEvent()`, Subjects, WebSockets

```typescript
// Hot: All subscribers share the same event stream
const hot$ = fromEvent(document, 'click');
// Click happens whether anyone is subscribed or not
```

**share() - Convert Cold to Hot:**

```typescript
// Without share: 3 HTTP requests
const data$ = this.http.get('/api/data');
data$.subscribe(); // Request 1
data$.subscribe(); // Request 2
data$.subscribe(); // Request 3

// With share: 1 HTTP request shared
const shared$ = this.http.get('/api/data').pipe(share());
shared$.subscribe(); // Request 1
shared$.subscribe(); // Shares result
shared$.subscribe(); // Shares result
```

**How share() Works:**

```
Cold Observable:
┌─────────────┐
│ HTTP Source │
└─────────────┘
      │
      ├──▶ Subscriber A (triggers request)
      ├──▶ Subscriber B (triggers NEW request)
      └──▶ Subscriber C (triggers NEW request)

With share():
┌─────────────┐
│ HTTP Source │
└─────────────┘
      │
┌─────────────┐
│   Subject   │ ← Single subscription to source
└─────────────┘
      │
      ├──▶ Subscriber A
      ├──▶ Subscriber B (shared result)
      └──▶ Subscriber C (shared result)
```

---

## Question 11: Custom Operator for Logging and Performance

### Question
Create a custom operator that logs the time taken between subscription and first emission.

### Answer

```typescript
import { Observable, MonoTypeOperatorFunction } from 'rxjs';
import { tap } from 'rxjs/operators';

function measureTime<T>(label: string): MonoTypeOperatorFunction<T> {
  return (source: Observable<T>): Observable<T> => {
    return new Observable(subscriber => {
      const startTime = performance.now();
      let firstEmission = true;
      
      console.log(`[${label}] Subscribed`);
      
      const subscription = source.subscribe({
        next: value => {
          if (firstEmission) {
            const elapsed = performance.now() - startTime;
            console.log(`[${label}] First emission after ${elapsed.toFixed(2)}ms`);
            firstEmission = false;
          }
          subscriber.next(value);
        },
        error: err => {
          const elapsed = performance.now() - startTime;
          console.error(`[${label}] Error after ${elapsed.toFixed(2)}ms:`, err);
          subscriber.error(err);
        },
        complete: () => {
          const elapsed = performance.now() - startTime;
          console.log(`[${label}] Completed after ${elapsed.toFixed(2)}ms`);
          subscriber.complete();
        }
      });
      
      return () => {
        const elapsed = performance.now() - startTime;
        console.log(`[${label}] Unsubscribed after ${elapsed.toFixed(2)}ms`);
        subscription.unsubscribe();
      };
    });
  };
}

// Usage
this.http.get('/api/heavy-data').pipe(
  measureTime('HeavyDataLoad')
).subscribe();

// Output:
// [HeavyDataLoad] Subscribed
// [HeavyDataLoad] First emission after 234.56ms
// [HeavyDataLoad] Completed after 234.89ms
```

**Extended Version with Emission Count:**

```typescript
function debugStream<T>(label: string, options: { 
  logValues?: boolean; 
  logTiming?: boolean 
} = {}): MonoTypeOperatorFunction<T> {
  const { logValues = false, logTiming = true } = options;
  
  return (source: Observable<T>): Observable<T> => {
    return new Observable(subscriber => {
      const startTime = performance.now();
      let emissionCount = 0;
      
      return source.subscribe({
        next: value => {
          emissionCount++;
          if (logTiming) {
            const elapsed = performance.now() - startTime;
            console.log(`[${label}] #${emissionCount} @ ${elapsed.toFixed(0)}ms`);
          }
          if (logValues) {
            console.log(`[${label}] Value:`, value);
          }
          subscriber.next(value);
        },
        error: err => subscriber.error(err),
        complete: () => {
          console.log(`[${label}] Total emissions: ${emissionCount}`);
          subscriber.complete();
        }
      });
    });
  };
}
```

---

## Question 12: State Management Pattern with BehaviorSubject

### Question
Implement a simple, type-safe state management solution using BehaviorSubject with selectors.

### Answer

```typescript
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, distinctUntilChanged, map } from 'rxjs';

// Generic Store Base Class
abstract class Store<T> {
  private state$: BehaviorSubject<T>;
  
  protected constructor(initialState: T) {
    this.state$ = new BehaviorSubject<T>(initialState);
  }
  
  // Get current snapshot synchronously
  protected get state(): T {
    return this.state$.getValue();
  }
  
  // Select a slice of state with memoization
  protected select<R>(selector: (state: T) => R): Observable<R> {
    return this.state$.pipe(
      map(selector),
      distinctUntilChanged()
    );
  }
  
  // Update state immutably
  protected setState(newState: Partial<T>): void {
    this.state$.next({
      ...this.state,
      ...newState
    });
  }
  
  // Replace entire state
  protected resetState(newState: T): void {
    this.state$.next(newState);
  }
}

// Concrete Implementation
interface CartState {
  items: CartItem[];
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

interface CartItem {
  productId: string;
  name: string;
  price: number;
  quantity: number;
}

const initialCartState: CartState = {
  items: [],
  isLoading: false,
  error: null,
  lastUpdated: null
};

@Injectable({ providedIn: 'root' })
export class CartStore extends Store<CartState> {
  constructor() {
    super(initialCartState);
  }
  
  // Public selectors (readonly)
  readonly items$ = this.select(state => state.items);
  readonly isLoading$ = this.select(state => state.isLoading);
  readonly error$ = this.select(state => state.error);
  
  // Derived selectors
  readonly itemCount$ = this.select(
    state => state.items.reduce((sum, item) => sum + item.quantity, 0)
  );
  
  readonly total$ = this.select(
    state => state.items.reduce(
      (sum, item) => sum + item.price * item.quantity, 0
    )
  );
  
  readonly isEmpty$ = this.select(state => state.items.length === 0);
  
  // Public actions
  addItem(item: Omit<CartItem, 'quantity'>): void {
    const existing = this.state.items.find(i => i.productId === item.productId);
    
    if (existing) {
      this.updateQuantity(item.productId, existing.quantity + 1);
    } else {
      this.setState({
        items: [...this.state.items, { ...item, quantity: 1 }],
        lastUpdated: new Date()
      });
    }
  }
  
  removeItem(productId: string): void {
    this.setState({
      items: this.state.items.filter(i => i.productId !== productId),
      lastUpdated: new Date()
    });
  }
  
  updateQuantity(productId: string, quantity: number): void {
    if (quantity <= 0) {
      this.removeItem(productId);
      return;
    }
    
    this.setState({
      items: this.state.items.map(item =>
        item.productId === productId
          ? { ...item, quantity }
          : item
      ),
      lastUpdated: new Date()
    });
  }
  
  clearCart(): void {
    this.resetState(initialCartState);
  }
  
  setLoading(isLoading: boolean): void {
    this.setState({ isLoading, error: null });
  }
  
  setError(error: string): void {
    this.setState({ error, isLoading: false });
  }
  
  // Sync access when needed
  getSnapshot(): Readonly<CartState> {
    return this.state;
  }
}

// Usage in Component
@Component({
  selector: 'app-cart',
  template: `
    <div class="cart">
      <h2>Cart ({{ itemCount$ | async }} items)</h2>
      
      @if (isLoading$ | async) {
        <app-spinner />
      }
      
      @if (error$ | async; as error) {
        <app-error [message]="error" />
      }
      
      @for (item of items$ | async; track item.productId) {
        <div class="cart-item">
          <span>{{ item.name }}</span>
          <span>{{ item.price | currency }}</span>
          <input 
            type="number" 
            [value]="item.quantity"
            (change)="updateQuantity(item.productId, $event)">
          <button (click)="remove(item.productId)">Remove</button>
        </div>
      }
      
      <div class="total">
        Total: {{ total$ | async | currency }}
      </div>
      
      <button (click)="cart.clearCart()">Clear Cart</button>
    </div>
  `
})
export class CartComponent {
  protected cart = inject(CartStore);
  
  items$ = this.cart.items$;
  itemCount$ = this.cart.itemCount$;
  total$ = this.cart.total$;
  isLoading$ = this.cart.isLoading$;
  error$ = this.cart.error$;
  
  updateQuantity(productId: string, event: Event): void {
    const value = +(event.target as HTMLInputElement).value;
    this.cart.updateQuantity(productId, value);
  }
  
  remove(productId: string): void {
    this.cart.removeItem(productId);
  }
}
```

---

## Quick Reference: Operator Cheat Sheet

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMBINATION OPERATORS                        │
├─────────────────┬───────────────────────────────────────────────┤
│ combineLatest   │ Latest from all when ANY emits                │
│ forkJoin        │ Last from all when ALL complete               │
│ merge           │ All values interleaved (parallel)             │
│ concat          │ All values sequential (ordered)               │
│ zip             │ Paired by index                               │
│ withLatestFrom  │ Source triggers + context from others         │
├─────────────────┴───────────────────────────────────────────────┤
│                    MULTICASTING OPERATORS                        │
├─────────────────┬───────────────────────────────────────────────┤
│ share()         │ Subject internally, refCount: true            │
│ shareReplay(n)  │ ReplaySubject, refCount: false by default     │
│ shareReplay({}) │ Configurable refCount                         │
├─────────────────┴───────────────────────────────────────────────┤
│                    SUBJECTS                                      │
├─────────────────┬───────────────────────────────────────────────┤
│ Subject         │ No initial, no replay                         │
│ BehaviorSubject │ Initial value, replays current                │
│ ReplaySubject   │ Replays last N values                         │
│ AsyncSubject    │ Emits last value on complete only             │
└─────────────────┴───────────────────────────────────────────────┘
```

---

## Common Mistakes to Avoid

1. **forkJoin with infinite streams** - Use `take()` or `first()`
2. **combineLatest without initial values** - Use `startWith()`
3. **shareReplay memory leaks** - Consider `refCount: true`
4. **Using getValue() in reactive chains** - Use operators instead
5. **Not handling individual errors in forkJoin** - Use `catchError()` per stream
6. **Creating operators from scratch** - Compose existing operators with `pipe()`
7. **Forgetting to unsubscribe** - Use `takeUntilDestroyed()`
