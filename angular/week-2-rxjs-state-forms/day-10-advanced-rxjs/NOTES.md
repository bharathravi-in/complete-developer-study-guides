# Day 10: Advanced RxJS - Combination Operators & Multicasting

## Learning Objectives
- Master combination operators: combineLatest, forkJoin, merge, concat, zip, withLatestFrom
- Understand BehaviorSubject for state management
- Implement shareReplay and multicasting patterns
- Create custom RxJS operators

---

## 1. Combination Operators Overview

### Quick Reference Table

| Operator | Emissions | Completion | Use Case |
|----------|-----------|------------|----------|
| `combineLatest` | Latest from all when any emits | When all complete | Real-time combined state |
| `forkJoin` | Last value from each | When all complete | Parallel HTTP requests |
| `merge` | All values as they arrive | When all complete | Multiple event sources |
| `concat` | All values in sequence | When all complete | Sequential operations |
| `zip` | Paired values by index | When shortest completes | Coordinated pairs |
| `withLatestFrom` | Source + latest from others | When source completes | Main stream with context |

---

## 2. combineLatest

### Concept
Combines the latest values from multiple observables. Emits whenever ANY source emits (after all have emitted at least once).

### ASCII Marble Diagram
```
Source A:    --1-------3-------5--|
Source B:    ----2-------4---------|
             combineLatest([A, B])
Output:      ---[1,2]--[3,2]-[3,4]-[5,4]--|

Timeline:
t1: A emits 1, waiting for B
t2: B emits 2 → emit [1,2]
t3: A emits 3 → emit [3,2] (latest B is still 2)
t4: B emits 4 → emit [3,4] (latest A is still 3)
t5: A emits 5 → emit [5,4]
```

### Angular Example: Search with Filters
```typescript
import { Component, inject, DestroyRef } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { combineLatest, debounceTime, startWith } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-product-search',
  standalone: true,
  imports: [ReactiveFormsModule],
  template: `
    <input [formControl]="searchControl" placeholder="Search...">
    <select [formControl]="categoryControl">
      <option value="">All Categories</option>
      <option value="electronics">Electronics</option>
      <option value="clothing">Clothing</option>
    </select>
    <select [formControl]="sortControl">
      <option value="name">Name</option>
      <option value="price">Price</option>
    </select>
  `
})
export class ProductSearchComponent {
  private destroyRef = inject(DestroyRef);
  private productService = inject(ProductService);
  
  searchControl = new FormControl('');
  categoryControl = new FormControl('');
  sortControl = new FormControl('name');
  
  constructor() {
    // Combine all filter controls
    combineLatest([
      this.searchControl.valueChanges.pipe(startWith(''), debounceTime(300)),
      this.categoryControl.valueChanges.pipe(startWith('')),
      this.sortControl.valueChanges.pipe(startWith('name'))
    ]).pipe(
      takeUntilDestroyed(this.destroyRef)
    ).subscribe(([search, category, sort]) => {
      this.productService.loadProducts({ search, category, sort });
    });
  }
}
```

### Key Points
- **Requires initial emission from ALL sources** before first output
- Use `startWith()` to provide initial values
- Perfect for dependent UI state combinations

---

## 3. forkJoin

### Concept
Waits for ALL observables to complete, then emits a single array/object with the LAST value from each.

### ASCII Marble Diagram
```
Source A:    --1--2--3--|
Source B:    ----a----b----|
Source C:    ------x--|
             forkJoin([A, B, C])
Output:      --------------[3, b, x]|

Timeline:
- Waits until ALL complete
- Emits single value with last from each: [3, 'b', 'x']
- Then completes immediately
```

### Angular Example: Dashboard Data Loading
```typescript
import { Component, OnInit, inject, signal } from '@angular/core';
import { forkJoin, catchError, of } from 'rxjs';

interface DashboardData {
  user: User;
  stats: Stats;
  notifications: Notification[];
  recentOrders: Order[];
}

@Component({
  selector: 'app-dashboard',
  template: `
    @if (loading()) {
      <app-loading-spinner />
    } @else if (error()) {
      <app-error-message [message]="error()" />
    } @else {
      <app-user-profile [user]="data()?.user" />
      <app-stats-card [stats]="data()?.stats" />
      <app-notifications [items]="data()?.notifications" />
      <app-recent-orders [orders]="data()?.recentOrders" />
    }
  `
})
export class DashboardComponent implements OnInit {
  private userService = inject(UserService);
  private statsService = inject(StatsService);
  private notificationService = inject(NotificationService);
  private orderService = inject(OrderService);
  
  loading = signal(true);
  error = signal<string | null>(null);
  data = signal<DashboardData | null>(null);
  
  ngOnInit() {
    // All requests run in parallel, wait for all to complete
    forkJoin({
      user: this.userService.getCurrentUser(),
      stats: this.statsService.getStats(),
      notifications: this.notificationService.getRecent().pipe(
        catchError(() => of([])) // Graceful degradation
      ),
      recentOrders: this.orderService.getRecent(5)
    }).subscribe({
      next: (result) => {
        this.data.set(result);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set('Failed to load dashboard');
        this.loading.set(false);
      }
    });
  }
}
```

### ⚠️ Warning: forkJoin Pitfalls
```typescript
// ❌ DANGER: If any observable errors, entire forkJoin fails
forkJoin([obs1$, obs2$, obs3$]); // One error = all fail

// ✅ Handle errors individually
forkJoin([
  obs1$.pipe(catchError(err => of(null))),
  obs2$.pipe(catchError(err => of([]))),
  obs3$.pipe(catchError(err => of(defaultValue)))
]);

// ❌ DANGER: Never-completing observables
forkJoin([of(1), interval(1000)]); // Never emits! interval never completes

// ✅ Take finite values from infinite streams
forkJoin([of(1), interval(1000).pipe(take(3))]);
```

---

## 4. merge

### Concept
Combines multiple observables into one, emitting values from ALL sources as they arrive (interleaved).

### ASCII Marble Diagram
```
Source A:    --1-----3-----5--|
Source B:    ----2-----4--------|
             merge(A, B)
Output:      --1-2---3-4---5----|

Timeline: Values arrive in actual emission order
- All sources are subscribed simultaneously
- Order depends on when each source emits
```

### Angular Example: Multiple Event Sources
```typescript
import { Component, ElementRef, ViewChild, AfterViewInit, inject, DestroyRef } from '@angular/core';
import { fromEvent, merge, throttleTime } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-scroll-tracker',
  template: `
    <div #scrollContainer class="scroll-area">
      <div class="content">Scrollable content...</div>
    </div>
  `
})
export class ScrollTrackerComponent implements AfterViewInit {
  @ViewChild('scrollContainer') container!: ElementRef;
  
  private destroyRef = inject(DestroyRef);
  private analyticsService = inject(AnalyticsService);
  
  ngAfterViewInit() {
    const windowScroll$ = fromEvent(window, 'scroll');
    const containerScroll$ = fromEvent(this.container.nativeElement, 'scroll');
    const touchMove$ = fromEvent(this.container.nativeElement, 'touchmove');
    
    // Merge all scroll-related events into single stream
    merge(windowScroll$, containerScroll$, touchMove$).pipe(
      throttleTime(200),
      takeUntilDestroyed(this.destroyRef)
    ).subscribe(event => {
      this.analyticsService.trackScroll(event);
    });
  }
}
```

### Real-World: WebSocket Reconnection
```typescript
@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private socket$ = webSocket<Message>('wss://api.example.com/ws');
  
  // Merge real messages with local optimistic updates
  messages$ = merge(
    this.socket$.pipe(
      retry({ count: 3, delay: 1000 })
    ),
    this.localUpdates$ // Optimistic UI updates
  );
}
```

---

## 5. concat

### Concept
Subscribes to observables sequentially—waits for each to complete before subscribing to the next.

### ASCII Marble Diagram
```
Source A:    --1--2--|
Source B:    --a--b--c--|
             concat(A, B)
Output:      --1--2----a--b--c--|

Timeline:
- Subscribe to A first
- Wait for A to complete
- Then subscribe to B
- Emit B's values
```

### Angular Example: Sequential File Upload
```typescript
import { Injectable, inject } from '@angular/core';
import { concat, from, Observable } from 'rxjs';
import { concatMap, tap, finalize } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class FileUploadService {
  private http = inject(HttpClient);
  
  // Upload files one at a time (preserve order, respect rate limits)
  uploadFilesSequentially(files: File[]): Observable<UploadResult> {
    return from(files).pipe(
      concatMap((file, index) => 
        this.uploadSingleFile(file).pipe(
          tap(result => console.log(`File ${index + 1} uploaded`))
        )
      )
    );
  }
  
  // Alternative: Using concat directly
  uploadWithProgress(files: File[]): Observable<UploadProgress> {
    const uploads$ = files.map(file => this.uploadSingleFile(file));
    
    return concat(...uploads$).pipe(
      finalize(() => console.log('All uploads complete'))
    );
  }
  
  private uploadSingleFile(file: File): Observable<UploadResult> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<UploadResult>('/api/upload', formData);
  }
}
```

### concat vs merge Comparison
```
merge:  Parallel execution, interleaved results
        --1-a-2-b-3-c--|
        
concat: Sequential execution, ordered results
        --1--2--3--a--b--c--|
```

---

## 6. zip

### Concept
Pairs values by index position—waits for ALL sources to emit their nth value, then emits combined array.

### ASCII Marble Diagram
```
Source A:    --1-----2-------3--|
Source B:    ----a-------b-------c--|
             zip(A, B)
Output:      ----[1,a]---[2,b]---[3,c]--|

Pairing by index:
- Index 0: (1, a) → [1, a]
- Index 1: (2, b) → [2, b]  
- Index 2: (3, c) → [3, c]
```

### Angular Example: Coordinated Animation
```typescript
import { Component } from '@angular/core';
import { zip, interval, of } from 'rxjs';
import { take, map } from 'rxjs/operators';

@Component({
  selector: 'app-animated-list',
  template: `
    @for (item of animatedItems; track item.id) {
      <div class="item" [class.visible]="item.visible">
        {{ item.name }}
      </div>
    }
  `
})
export class AnimatedListComponent {
  items = ['Apple', 'Banana', 'Cherry', 'Date'];
  animatedItems: Array<{ id: number; name: string; visible: boolean }> = [];
  
  startAnimation() {
    // Pair items with staggered timing
    zip(
      of(...this.items),              // Items to show
      interval(200)                    // Stagger interval
    ).pipe(
      map(([name, index]) => ({ id: index, name, visible: true }))
    ).subscribe(item => {
      this.animatedItems.push(item);
    });
  }
}
```

### When to Use zip
```typescript
// ✅ Good: Coordinated requests where you need paired results
zip(
  this.userService.getUser(id),
  this.permissionService.getPermissions(id)
).subscribe(([user, permissions]) => {
  // Both relate to same user, paired by request order
});

// ❌ Avoid: When sources emit at very different rates
zip(
  interval(100),   // Fast
  interval(5000)   // Slow - creates memory buildup
);
```

---

## 7. withLatestFrom

### Concept  
When the SOURCE observable emits, combine with the LATEST value from other observables. Other observables don't trigger emissions.

### ASCII Marble Diagram
```
Source:      ----1-------2-------3---|
Other:       --a-----b-----c---------|
             source.pipe(withLatestFrom(other))
Output:      ----[1,a]---[2,b]---[3,c]|

Key difference from combineLatest:
- Only Source triggers emissions
- Other stream provides "context" values
```

### Angular Example: Form Submit with Current Filters
```typescript
import { Component, inject, DestroyRef } from '@angular/core';
import { Subject, BehaviorSubject } from 'rxjs';
import { withLatestFrom, exhaustMap } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-search-form',
  template: `
    <input #searchInput>
    <button (click)="search$.next(searchInput.value)">Search</button>
    
    <div class="filters">
      <label>
        <input type="checkbox" (change)="toggleFilter('active')"> Active Only
      </label>
      <select (change)="sortBy$.next($any($event.target).value)">
        <option value="date">Date</option>
        <option value="name">Name</option>
      </select>
    </div>
  `
})
export class SearchFormComponent {
  private destroyRef = inject(DestroyRef);
  private searchService = inject(SearchService);
  
  search$ = new Subject<string>();
  filters$ = new BehaviorSubject<Set<string>>(new Set());
  sortBy$ = new BehaviorSubject<string>('date');
  
  constructor() {
    // Search button triggers, filters are just "context"
    this.search$.pipe(
      withLatestFrom(this.filters$, this.sortBy$),
      exhaustMap(([query, filters, sortBy]) => 
        this.searchService.search({ query, filters: [...filters], sortBy })
      ),
      takeUntilDestroyed(this.destroyRef)
    ).subscribe(results => {
      // Handle results
    });
  }
  
  toggleFilter(filter: string) {
    const current = this.filters$.value;
    if (current.has(filter)) {
      current.delete(filter);
    } else {
      current.add(filter);
    }
    this.filters$.next(new Set(current));
  }
}
```

### combineLatest vs withLatestFrom
```typescript
// combineLatest: Either stream triggers emission
combineLatest([click$, position$])
// User moves mouse → emission
// User clicks → emission

// withLatestFrom: Only source triggers emission
click$.pipe(withLatestFrom(position$))
// User moves mouse → NO emission
// User clicks → emission with current position
```

---

## 8. BehaviorSubject for State Management

### Concept
A Subject that requires an initial value and emits the current value to new subscribers.

### ASCII Marble Diagram
```
BehaviorSubject(0):

        [Initial: 0]
             |
Subscriber A subscribes → immediately receives 0
             |
             --1---2---
                   |
Subscriber B subscribes → immediately receives 2
                   |
             ------3---4---|
```

### Angular Example: Simple State Store
```typescript
import { Injectable, computed, signal } from '@angular/core';
import { BehaviorSubject, Observable, distinctUntilChanged, map } from 'rxjs';

// Type-safe state interface
interface AppState {
  user: User | null;
  theme: 'light' | 'dark';
  notifications: Notification[];
  isLoading: boolean;
}

const initialState: AppState = {
  user: null,
  theme: 'light',
  notifications: [],
  isLoading: false
};

@Injectable({ providedIn: 'root' })
export class StateService {
  private state$ = new BehaviorSubject<AppState>(initialState);
  
  // Public read-only stream
  readonly state: Observable<AppState> = this.state$.asObservable();
  
  // Selectors - derived state with memoization
  readonly user$ = this.select(state => state.user);
  readonly theme$ = this.select(state => state.theme);
  readonly notifications$ = this.select(state => state.notifications);
  readonly unreadCount$ = this.select(
    state => state.notifications.filter(n => !n.read).length
  );
  
  // Generic selector factory
  select<T>(selector: (state: AppState) => T): Observable<T> {
    return this.state$.pipe(
      map(selector),
      distinctUntilChanged()
    );
  }
  
  // Get current snapshot (synchronous)
  getSnapshot(): AppState {
    return this.state$.getValue();
  }
  
  // State update methods
  setUser(user: User | null): void {
    this.updateState({ user });
  }
  
  setTheme(theme: 'light' | 'dark'): void {
    this.updateState({ theme });
  }
  
  addNotification(notification: Notification): void {
    const current = this.getSnapshot();
    this.updateState({
      notifications: [...current.notifications, notification]
    });
  }
  
  markNotificationRead(id: string): void {
    const current = this.getSnapshot();
    this.updateState({
      notifications: current.notifications.map(n =>
        n.id === id ? { ...n, read: true } : n
      )
    });
  }
  
  setLoading(isLoading: boolean): void {
    this.updateState({ isLoading });
  }
  
  // Immutable state update
  private updateState(partial: Partial<AppState>): void {
    const current = this.state$.getValue();
    this.state$.next({ ...current, ...partial });
  }
  
  // Reset to initial state
  reset(): void {
    this.state$.next(initialState);
  }
}
```

### Usage in Components
```typescript
@Component({
  selector: 'app-header',
  template: `
    <nav>
      <span>{{ (user$ | async)?.name }}</span>
      <button (click)="toggleTheme()">
        {{ theme$ | async }}
      </button>
      <span class="badge">{{ unreadCount$ | async }}</span>
    </nav>
  `
})
export class HeaderComponent {
  private stateService = inject(StateService);
  
  user$ = this.stateService.user$;
  theme$ = this.stateService.theme$;
  unreadCount$ = this.stateService.unreadCount$;
  
  toggleTheme() {
    const current = this.stateService.getSnapshot().theme;
    this.stateService.setTheme(current === 'light' ? 'dark' : 'light');
  }
}
```

---

## 9. shareReplay - Caching & Multicasting

### Concept
Share a single subscription among multiple subscribers AND replay the last N emissions to new subscribers.

### ASCII Marble Diagram
```
Without shareReplay:
source$: HTTP GET /api/data
Subscriber A: ----HTTP call----data-|
Subscriber B: ----HTTP call----data-|
(2 HTTP calls!)

With shareReplay(1):
source$.pipe(shareReplay(1))
Subscriber A: ----HTTP call----data-|
Subscriber B: ------------------data-| (from cache)
(1 HTTP call!)
```

### Angular Example: Cached HTTP Requests
```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, shareReplay, timer, switchMap } from 'rxjs';

interface Config {
  apiUrl: string;
  features: string[];
  version: string;
}

@Injectable({ providedIn: 'root' })
export class ConfigService {
  private http = inject(HttpClient);
  
  // Cached config - shared across all subscribers
  private config$: Observable<Config> | null = null;
  
  getConfig(): Observable<Config> {
    if (!this.config$) {
      this.config$ = this.http.get<Config>('/api/config').pipe(
        shareReplay({ bufferSize: 1, refCount: false })
      );
    }
    return this.config$;
  }
  
  // Auto-refreshing cache (every 5 minutes)
  private autoRefreshConfig$ = timer(0, 5 * 60 * 1000).pipe(
    switchMap(() => this.http.get<Config>('/api/config')),
    shareReplay({ bufferSize: 1, refCount: true })
  );
  
  // Clear cache on demand
  clearCache(): void {
    this.config$ = null;
  }
}
```

### shareReplay Configuration Options

```typescript
// Option 1: Simple usage
shareReplay(1)
// Equivalent to: shareReplay({ bufferSize: 1, refCount: false })

// Option 2: With refCount
shareReplay({ bufferSize: 1, refCount: true })

// refCount: false (default)
// - Source subscription stays active even with 0 subscribers
// - Good for: App-wide config that should never re-fetch

// refCount: true  
// - Source unsubscribes when all subscribers disconnect
// - Re-subscribes (and re-fetches) when new subscriber arrives
// - Good for: Component-scoped caching
```

### Memory Leak Prevention
```typescript
// ⚠️ Potential memory leak with refCount: false
@Injectable({ providedIn: 'root' })
export class DataService {
  // This subscription NEVER ends
  data$ = this.http.get('/api/data').pipe(
    shareReplay({ bufferSize: 1, refCount: false }) // ⚠️
  );
}

// ✅ Better: Use refCount: true for component-level
@Component({...})
export class MyComponent {
  data$ = this.http.get('/api/data').pipe(
    shareReplay({ bufferSize: 1, refCount: true })
  );
}

// ✅ Or: Implement manual cache invalidation
@Injectable({ providedIn: 'root' })
export class DataService {
  private cache$ = new BehaviorSubject<Data | null>(null);
  
  getData(): Observable<Data> {
    if (!this.cache$.value) {
      this.http.get<Data>('/api/data').subscribe(data => {
        this.cache$.next(data);
      });
    }
    return this.cache$.pipe(filter(Boolean));
  }
  
  invalidateCache(): void {
    this.cache$.next(null);
  }
}
```

---

## 10. Multicasting: share, publish, refCount

### The Multicast Family

```typescript
// share() = multicast(() => new Subject()) + refCount()
// shareReplay(n) = multicast(() => new ReplaySubject(n)) + refCount()

// Modern RxJS 7+ recommendation: Use share() with config
import { share, ReplaySubject } from 'rxjs';

// Equivalent to shareReplay({ bufferSize: 1, refCount: true })
source$.pipe(
  share({
    connector: () => new ReplaySubject(1),
    resetOnError: true,
    resetOnComplete: true,
    resetOnRefCountZero: true
  })
);
```

### share() Configuration
```typescript
import { share, ReplaySubject, timer } from 'rxjs';

const data$ = this.http.get('/api/data').pipe(
  share({
    // What Subject type to use internally
    connector: () => new ReplaySubject(1),
    
    // Reset behavior options:
    resetOnError: true,      // Reset on error
    resetOnComplete: false,  // Keep cached after complete
    resetOnRefCountZero: () => timer(5000) // Keep cache for 5s after last unsubscribe
  })
);
```

### Multicasting Comparison Table

| Operator | Subject Type | RefCount | Replays to Late Subscribers |
|----------|--------------|----------|----------------------------|
| `share()` | Subject | Yes | No |
| `shareReplay(n)` | ReplaySubject(n) | No* | Yes (last n values) |
| `shareReplay({..., refCount: true})` | ReplaySubject(n) | Yes | Yes |
| `publish()` | Subject | Manual | No |
| `publishReplay(n)` | ReplaySubject(n) | Manual | Yes |
| `publishBehavior(init)` | BehaviorSubject | Manual | Yes (1 value) |

*`shareReplay(n)` uses `refCount: false` by default

### When to Use Each

```typescript
// share() - Hot observable, no replay needed
const clicks$ = fromEvent(document, 'click').pipe(share());

// shareReplay(1) - Cache HTTP responses
const config$ = http.get('/config').pipe(shareReplay(1));

// shareReplay with refCount - Component-scoped cache
const componentData$ = http.get('/data').pipe(
  shareReplay({ bufferSize: 1, refCount: true })
);

// Custom share config - Advanced caching with timeout
const cachedData$ = http.get('/data').pipe(
  share({
    connector: () => new ReplaySubject(1),
    resetOnRefCountZero: () => timer(30000) // 30s cache
  })
);
```

---

## 11. Creating Custom Operators

### Pattern 1: Using Existing Operators (Preferred)
```typescript
import { Observable, pipe, MonoTypeOperatorFunction } from 'rxjs';
import { filter, map, distinctUntilChanged, debounceTime } from 'rxjs/operators';

// Type-safe custom operator
function filterNullish<T>(): MonoTypeOperatorFunction<T> {
  return pipe(
    filter((value): value is NonNullable<T> => value != null)
  );
}

// Usage
source$.pipe(filterNullish()).subscribe(value => {
  // value is guaranteed non-null
});
```

### Pattern 2: Transforming Values
```typescript
import { OperatorFunction, pipe } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

interface ApiResponse<T> {
  data: T;
  meta: { timestamp: number };
}

// Extract data from API response
function extractData<T>(): OperatorFunction<ApiResponse<T>, T> {
  return pipe(
    map(response => response.data)
  );
}

// Usage
this.http.get<ApiResponse<User[]>>('/api/users').pipe(
  extractData()
).subscribe(users => {
  // users: User[]
});
```

### Pattern 3: Debounced Distinct Input
```typescript
import { MonoTypeOperatorFunction, pipe } from 'rxjs';
import { debounceTime, distinctUntilChanged, filter, map } from 'rxjs/operators';

function searchInput(debounceMs = 300): MonoTypeOperatorFunction<string> {
  return pipe(
    map(value => value.trim()),
    filter(value => value.length >= 2),
    debounceTime(debounceMs),
    distinctUntilChanged()
  );
}

// Usage
this.searchControl.valueChanges.pipe(
  searchInput(400)
).subscribe(query => {
  this.search(query);
});
```

### Pattern 4: Error Handling with Retry
```typescript
import { Observable, OperatorFunction, pipe, throwError, timer } from 'rxjs';
import { catchError, retry, retryWhen, delay, take, concatMap } from 'rxjs/operators';

interface RetryConfig {
  maxRetries?: number;
  delayMs?: number;
  exponentialBackoff?: boolean;
}

function retryWithBackoff<T>(config: RetryConfig = {}): MonoTypeOperatorFunction<T> {
  const { maxRetries = 3, delayMs = 1000, exponentialBackoff = true } = config;
  
  return pipe(
    retry({
      count: maxRetries,
      delay: (error, retryCount) => {
        const backoffDelay = exponentialBackoff 
          ? delayMs * Math.pow(2, retryCount - 1)
          : delayMs;
        console.log(`Retry ${retryCount} after ${backoffDelay}ms`);
        return timer(backoffDelay);
      }
    })
  );
}

// Usage
this.http.get('/api/flaky-endpoint').pipe(
  retryWithBackoff({ maxRetries: 3, delayMs: 1000, exponentialBackoff: true })
).subscribe();
```

### Pattern 5: Low-Level Custom Operator
```typescript
import { Observable, OperatorFunction } from 'rxjs';

// Log emissions with timestamp
function debug<T>(tag: string): MonoTypeOperatorFunction<T> {
  return (source: Observable<T>): Observable<T> => {
    return new Observable(subscriber => {
      console.log(`[${tag}] Subscribed at ${new Date().toISOString()}`);
      
      const subscription = source.subscribe({
        next: value => {
          console.log(`[${tag}] Next:`, value);
          subscriber.next(value);
        },
        error: err => {
          console.error(`[${tag}] Error:`, err);
          subscriber.error(err);
        },
        complete: () => {
          console.log(`[${tag}] Complete`);
          subscriber.complete();
        }
      });
      
      // Cleanup function
      return () => {
        console.log(`[${tag}] Unsubscribed at ${new Date().toISOString()}`);
        subscription.unsubscribe();
      };
    });
  };
}

// Usage
source$.pipe(
  debug('BeforeMap'),
  map(x => x * 2),
  debug('AfterMap')
).subscribe();
```

### Pattern 6: Stateful Custom Operator
```typescript
import { Observable, MonoTypeOperatorFunction } from 'rxjs';

// Only emit if value changed by more than threshold
function significantChange<T extends number>(threshold: number): MonoTypeOperatorFunction<T> {
  return (source: Observable<T>): Observable<T> => {
    return new Observable(subscriber => {
      let previousValue: T | undefined;
      
      return source.subscribe({
        next: value => {
          if (previousValue === undefined || 
              Math.abs(value - previousValue) >= threshold) {
            previousValue = value;
            subscriber.next(value);
          }
        },
        error: err => subscriber.error(err),
        complete: () => subscriber.complete()
      });
    });
  };
}

// Usage: Only emit when price changes by at least 0.5
priceStream$.pipe(
  significantChange(0.5)
).subscribe(price => {
  this.updateDisplay(price);
});
```

### Pattern 7: Angular-Specific - takeUntilDestroyed Alternative
```typescript
import { inject, DestroyRef } from '@angular/core';
import { Observable, MonoTypeOperatorFunction } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { Subject } from 'rxjs';

// Custom operator for cleanup (before Angular had takeUntilDestroyed)
function untilDestroyed<T>(destroyRef: DestroyRef): MonoTypeOperatorFunction<T> {
  const destroy$ = new Subject<void>();
  
  destroyRef.onDestroy(() => {
    destroy$.next();
    destroy$.complete();
  });
  
  return (source: Observable<T>) => source.pipe(takeUntil(destroy$));
}

// But prefer the built-in:
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({...})
export class MyComponent {
  private destroyRef = inject(DestroyRef);
  
  ngOnInit() {
    interval(1000).pipe(
      takeUntilDestroyed(this.destroyRef)
    ).subscribe();
  }
}
```

---

## 12. Quick Reference Card

### Combination Operators Decision Tree

```
Need to combine streams?
│
├─ Do ALL streams need to complete first?
│   ├─ Yes, wait for all → forkJoin
│   └─ No
│
├─ Should one stream trigger emissions?
│   └─ Yes → withLatestFrom
│
├─ Need values paired by index?
│   └─ Yes → zip
│
├─ Should streams run sequentially?
│   └─ Yes → concat
│
├─ Should all values interleave?
│   └─ Yes → merge
│
└─ Need latest from all when any emits?
    └─ Yes → combineLatest
```

### Multicasting Decision Tree

```
Need to share subscription?
│
├─ Need to replay values to late subscribers?
│   ├─ Yes
│   │   ├─ Should cache persist after all unsubscribe?
│   │   │   ├─ Yes → shareReplay(n) or shareReplay({..., refCount: false})
│   │   │   └─ No → shareReplay({..., refCount: true})
│   │   │
│   │   └─ Need custom reset behavior?
│   │       └─ Use share() with connector config
│   │
│   └─ No → share()
│
└─ Need synchronous current value access?
    └─ Yes → BehaviorSubject
```

### Common Patterns Cheat Sheet

```typescript
// Parallel requests, wait for all
forkJoin({ user: user$, posts: posts$ })

// Real-time combined filters
combineLatest([filter1$, filter2$]).pipe(startWith(['', '']))

// Button click with current state
click$.pipe(withLatestFrom(state$))

// Multiple event sources
merge(keydown$, click$, touch$)

// Sequential operations
concat(validate$, save$, notify$)

// Cached HTTP
http.get('/api').pipe(shareReplay(1))

// Simple state store
private state$ = new BehaviorSubject<State>(initial);
readonly value$ = this.state$.pipe(map(s => s.value), distinctUntilChanged());
```

---

## Summary

| Topic | Key Takeaway |
|-------|--------------|
| combineLatest | Latest from all when any emits; use `startWith` for initial values |
| forkJoin | Wait for all to complete; handle individual errors |
| merge | All values interleaved; good for multiple event sources |
| concat | Sequential subscription; preserves order |
| zip | Pairs by index; beware of memory with mismatched rates |
| withLatestFrom | Source triggers, others provide context |
| BehaviorSubject | Synchronous value access, immediate emission to subscribers |
| shareReplay | Cache and replay; mind `refCount` for memory management |
| Custom operators | Prefer composing existing operators; use `pipe()` factory |

---

## Next: Day 11 - HTTP Client & Interceptors
