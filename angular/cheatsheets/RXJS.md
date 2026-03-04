# RxJS Cheatsheet

## Creation Operators

```typescript
import { of, from, interval, timer, fromEvent, EMPTY, throwError } from 'rxjs';

// of - emit values in sequence
of(1, 2, 3);                    // 1, 2, 3

// from - convert array/iterable/promise
from([1, 2, 3]);                // 1, 2, 3
from(fetchPromise);             // value from promise

// interval - emit incrementing numbers
interval(1000);                 // 0, 1, 2... every second

// timer - delay then emit, or with interval
timer(2000);                    // emit 0 after 2s
timer(2000, 1000);              // emit 0 after 2s, then 1,2,3... every 1s

// fromEvent - DOM events
fromEvent(button, 'click');
fromEvent(document, 'keydown');

// EMPTY - completes immediately
EMPTY;

// throwError - emits error
throwError(() => new Error('Failed'));
```

## Transformation Operators

```typescript
import { map, switchMap, mergeMap, concatMap, exhaustMap, scan } from 'rxjs/operators';

// map - transform values
source$.pipe(map(x => x * 2));

// switchMap - cancel previous, use latest
search$.pipe(
  switchMap(term => api.search(term))  // Good for: search, autocomplete
);

// mergeMap - all concurrent
files$.pipe(
  mergeMap(file => upload(file), 3)    // Good for: parallel requests
);                                      // 3 = max concurrent

// concatMap - one at a time, in order
actions$.pipe(
  concatMap(action => saveAction(action))  // Good for: ordered sequences
);

// exhaustMap - ignore while busy
click$.pipe(
  exhaustMap(() => api.submit())       // Good for: prevent double submit
);

// scan - accumulate values (like reduce)
clicks$.pipe(
  scan((count, _) => count + 1, 0)     // Running count
);
```

## Filtering Operators

```typescript
import { 
  filter, take, first, last, skip, 
  distinctUntilChanged, debounceTime, throttleTime, 
  takeUntil, takeWhile 
} from 'rxjs/operators';

// filter
source$.pipe(filter(x => x > 5));

// take - emit first n
source$.pipe(take(3));           // First 3 only

// first / last
source$.pipe(first());           // First value, then complete
source$.pipe(last());            // Last value before complete

// skip
source$.pipe(skip(2));           // Skip first 2

// distinctUntilChanged
source$.pipe(distinctUntilChanged());
source$.pipe(distinctUntilChanged((a, b) => a.id === b.id));

// debounceTime - wait for pause
input$.pipe(debounceTime(300));   // Wait 300ms of silence

// throttleTime - emit, then ignore for duration
resize$.pipe(throttleTime(100));  // Max once per 100ms

// takeUntil - complete when other emits
source$.pipe(takeUntil(destroy$));

// takeWhile - complete when condition false
source$.pipe(takeWhile(x => x < 10));
```

## Combination Operators

```typescript
import { combineLatest, forkJoin, merge, concat, zip, withLatestFrom } from 'rxjs';

// combineLatest - latest from each when any emit
combineLatest([user$, settings$]).pipe(
  map(([user, settings]) => ({ user, settings }))
);

// forkJoin - wait for all to complete
forkJoin({
  user: api.getUser(id),
  orders: api.getOrders(id)
});

// merge - concurrent emissions
merge(click$, keypress$);

// concat - sequential subscriptions
concat(preload$, mainData$);

// zip - pair by index
zip([letters$, numbers$]);  // [a,1], [b,2], [c,3]

// withLatestFrom - combine with latest from another
clicks$.pipe(
  withLatestFrom(currentUser$),
  map(([click, user]) => ({ click, user }))
);
```

## Error Handling

```typescript
import { catchError, retry, retryWhen, finalize } from 'rxjs/operators';
import { throwError, timer } from 'rxjs';

// catchError
api.getData().pipe(
  catchError(err => {
    console.error(err);
    return of([]);           // Return fallback
    // or: return throwError(() => err);  // Re-throw
  })
);

// retry - simple retry
api.getData().pipe(retry(3));    // Retry 3 times

// retry with config (RxJS 7+)
api.getData().pipe(
  retry({
    count: 3,
    delay: (error, retryCount) => {
      if (error.status === 404) {
        return throwError(() => error);  // Don't retry 404
      }
      return timer(retryCount * 1000);   // Exponential backoff
    }
  })
);

// finalize - always runs
api.getData().pipe(
  finalize(() => this.loading = false)
);
```

## Utility Operators

```typescript
import { tap, delay, timeout, startWith, share, shareReplay } from 'rxjs/operators';

// tap - side effects without changing stream
source$.pipe(
  tap(val => console.log('Value:', val)),
  tap({ 
    next: v => console.log(v),
    error: e => console.error(e),
    complete: () => console.log('Done')
  })
);

// delay
source$.pipe(delay(1000));

// timeout
api.getData().pipe(timeout(5000));  // Error if no emit in 5s

// startWith
data$.pipe(startWith([]));  // Emit [] first

// share - multicast (hot)
source$.pipe(share());

// shareReplay - multicast with replay
config$.pipe(shareReplay(1));  // Cache last value
```

## Subjects

```typescript
import { Subject, BehaviorSubject, ReplaySubject, AsyncSubject } from 'rxjs';

// Subject - no initial value
const subject = new Subject<string>();
subject.subscribe(v => console.log(v));
subject.next('Hello');

// BehaviorSubject - has current value
const behavior = new BehaviorSubject<number>(0);
console.log(behavior.getValue());  // Get current
behavior.next(1);

// ReplaySubject - replays n values
const replay = new ReplaySubject<string>(3);  // Buffer last 3
replay.next('a');
replay.next('b');
replay.subscribe(v => console.log(v));  // Gets a, b

// AsyncSubject - only last value on complete
const async = new AsyncSubject<string>();
async.next('a');
async.next('b');
async.complete();  // Subscriber gets 'b'
```

## Common Angular Patterns

```typescript
// Cleanup in component
@Component({...})
export class MyComponent {
  destroyRef = inject(DestroyRef);
  
  ngOnInit() {
    this.service.data$.pipe(
      takeUntilDestroyed(this.destroyRef)
    ).subscribe();
  }
}

// HTTP with error handling
getUsers(): Observable<User[]> {
  return this.http.get<User[]>('/api/users').pipe(
    retry(2),
    catchError(err => {
      this.notification.error('Failed to load users');
      return of([]);
    })
  );
}

// Search with debounce
this.searchControl.valueChanges.pipe(
  debounceTime(300),
  distinctUntilChanged(),
  filter(term => term.length > 2),
  switchMap(term => this.searchService.search(term))
).subscribe(results => this.results = results);

// Polling
interval(30000).pipe(
  startWith(0),
  switchMap(() => this.api.getStatus()),
  takeUntilDestroyed(this.destroyRef)
).subscribe();

// Combine latest state
combineLatest({
  users: this.userService.users$,
  filter: this.filterControl.valueChanges.pipe(startWith(''))
}).pipe(
  map(({ users, filter }) => 
    users.filter(u => u.name.includes(filter))
  )
);
```

## Operator Decision Tree

```
Need to transform value?
  ├── Simple transform → map
  └── To Observable → 
        ├── Cancel previous? → switchMap (search)
        ├── All parallel? → mergeMap (bulk operations)
        ├── Sequential? → concatMap (ordered writes)
        └── Ignore while busy? → exhaustMap (submit button)

Need to filter?
  ├── By condition → filter
  ├── First n values → take
  ├── Prevent duplicates → distinctUntilChanged
  ├── Wait for pause → debounceTime
  └── Rate limit → throttleTime

Need to combine?
  ├── Latest from all → combineLatest
  ├── Wait for all complete → forkJoin
  ├── Mix multiple streams → merge
  └── Pair by index → zip

Need error handling?
  ├── Provide fallback → catchError
  ├── Retry → retry
  └── Cleanup → finalize
```
