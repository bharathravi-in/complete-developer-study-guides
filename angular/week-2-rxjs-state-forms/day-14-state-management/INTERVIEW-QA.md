# Day 14: State Management - Interview Questions & Answers

## Basic Level

### Q1: What is state management and why do we need it?

**Answer:**
State management is the practice of managing the data that controls the UI and behavior of an application.

**Why we need it:**
1. **Single source of truth** - One place for application data
2. **Predictable state changes** - Know exactly how/when state changes
3. **Component communication** - Share data without prop drilling
4. **Debugging** - Easier to trace state changes
5. **Testing** - Isolated state logic is easier to test

```
┌─────────────────────────────────────────────────────────────┐
│                    Without State Management                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│    ┌─────────┐         ┌─────────┐         ┌─────────┐     │
│    │ Comp A  │◄───────►│ Comp B  │◄───────►│ Comp C  │     │
│    │ (state) │         │ (state) │         │ (state) │     │
│    └────┬────┘         └────┬────┘         └────┬────┘     │
│         │                   │                   │           │
│    ┌────▼────┐         ┌────▼────┐         ┌────▼────┐     │
│    │ Comp D  │         │ Comp E  │         │ Comp F  │     │
│    │ (state) │         │ (copy?) │         │ (copy?) │     │
│    └─────────┘         └─────────┘         └─────────┘     │
│                                                              │
│    Problem: Data duplication, sync issues, debugging hard    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    With State Management                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    ┌─────────────────┐                      │
│                    │   STORE         │                      │
│                    │ (Single Source) │                      │
│                    └────────┬────────┘                      │
│              ┌──────────────┼──────────────┐                │
│              │              │              │                │
│         ┌────▼────┐    ┌────▼────┐    ┌────▼────┐          │
│         │ Comp A  │    │ Comp B  │    │ Comp C  │          │
│         └────┬────┘    └─────────┘    └─────────┘          │
│              │                                              │
│         ┌────▼────┐    ┌─────────┐    ┌─────────┐          │
│         │ Comp D  │    │ Comp E  │    │ Comp F  │          │
│         └─────────┘    └─────────┘    └─────────┘          │
│                                                              │
│    Solution: Single source, automatic sync, easy debugging   │
└─────────────────────────────────────────────────────────────┘
```

---

### Q2: What are the different state management options in Angular?

**Answer:**

| Option | Complexity | Use Case |
|--------|------------|----------|
| **Component State** | Simple | Data used by single component |
| **Service + BehaviorSubject** | Low | Small apps, simple shared state |
| **Signals** | Low-Medium | Modern Angular 17+ apps |
| **@ngrx/signals** | Medium | Signal-based with structure |
| **NgRx Store** | High | Large enterprise apps |
| **Akita** | Medium | Alternative to NgRx |
| **NGXS** | Medium | Simpler Redux-like pattern |

**Selection criteria:**
- Team size and experience
- Application complexity
- Debugging requirements
- Performance needs

---

### Q3: What is BehaviorSubject and why is it used for state management?

**Answer:**
BehaviorSubject is a special type of Subject that:
1. **Has an initial value** - Always holds a value
2. **Emits current value** - New subscribers get current value immediately
3. **Allows reading current value** - Via `.getValue()` method

```typescript
import { BehaviorSubject } from 'rxjs';

// Create with initial value
const state$ = new BehaviorSubject<number>(0);

// Subscribe immediately gets 0
state$.subscribe(value => console.log(value)); // Output: 0

// Update value
state$.next(1); // All subscribers get 1

// Get current value synchronously
console.log(state$.getValue()); // 1

// vs Regular Subject - no initial value, no current value access
const subject$ = new Subject<number>();
subject$.subscribe(val => console.log(val)); // Nothing until next()
```

**Why BehaviorSubject for state:**
- Synchronous access to current state
- New components get current state immediately
- Predictable behavior

---

## Intermediate Level

### Q4: How would you implement a simple store using BehaviorSubject?

**Answer:**
```typescript
interface AppState {
  user: User | null;
  theme: 'light' | 'dark';
  notifications: Notification[];
}

@Injectable({ providedIn: 'root' })
export class AppStore {
  private state$ = new BehaviorSubject<AppState>({
    user: null,
    theme: 'light',
    notifications: []
  });

  // Selectors
  readonly user$ = this.state$.pipe(map(s => s.user), distinctUntilChanged());
  readonly theme$ = this.state$.pipe(map(s => s.theme), distinctUntilChanged());
  readonly notifications$ = this.state$.pipe(map(s => s.notifications));
  readonly isLoggedIn$ = this.user$.pipe(map(user => !!user));

  // Computed selector
  readonly unreadCount$ = this.notifications$.pipe(
    map(notifications => notifications.filter(n => !n.read).length)
  );

  // Snapshot of current state
  get snapshot(): AppState {
    return this.state$.getValue();
  }

  // Actions
  setUser(user: User | null): void {
    this.patch({ user });
  }

  setTheme(theme: 'light' | 'dark'): void {
    this.patch({ theme });
    localStorage.setItem('theme', theme);
  }

  addNotification(notification: Notification): void {
    this.patch({
      notifications: [...this.snapshot.notifications, notification]
    });
  }

  markAsRead(id: string): void {
    this.patch({
      notifications: this.snapshot.notifications.map(n =>
        n.id === id ? { ...n, read: true } : n
      )
    });
  }

  // Helper: immutable update
  private patch(partial: Partial<AppState>): void {
    this.state$.next({ ...this.snapshot, ...partial });
  }
}
```

---

### Q5: Explain NgRx and its core concepts.

**Answer:**
NgRx is a state management library based on Redux pattern with RxJS.

**Core concepts:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                          NgRx Data Flow                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌───────────┐     dispatch      ┌───────────┐                     │
│   │ Component │──────────────────►│  Actions  │                     │
│   └───────────┘                   └─────┬─────┘                     │
│         ▲                               │                            │
│         │                               │                            │
│    select/                              ▼                            │
│    subscribe                      ┌───────────┐    ┌──────────────┐ │
│         │                         │  Reducer  │    │   Effects    │ │
│         │                         │ (pure fn) │    │ (side efx)   │ │
│         │                         └─────┬─────┘    └──────┬───────┘ │
│         │                               │                 │          │
│         │                               ▼                 │          │
│         │                         ┌───────────┐           │          │
│         └─────────────────────────│   Store   │◄──────────┘          │
│                                   └───────────┘                      │
│                                         ▲                            │
│                                         │                            │
│                                   ┌─────┴─────┐                      │
│                                   │ Selectors │                      │
│                                   │ (memoized)│                      │
│                                   └───────────┘                      │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**1. Store** - Single immutable state tree
```typescript
interface AppState {
  users: UserState;
  products: ProductState;
}
```

**2. Actions** - Events describing state changes
```typescript
export const loadUsers = createAction('[User] Load');
export const loadUsersSuccess = createAction(
  '[User] Load Success',
  props<{ users: User[] }>()
);
```

**3. Reducers** - Pure functions that take state + action, return new state
```typescript
export const userReducer = createReducer(
  initialState,
  on(loadUsersSuccess, (state, { users }) => ({
    ...state,
    users,
    loading: false
  }))
);
```

**4. Selectors** - Functions to derive/compute state
```typescript
export const selectUsers = createSelector(
  selectUserState,
  state => state.users
);
```

**5. Effects** - Handle side effects (API calls, etc.)
```typescript
loadUsers$ = createEffect(() =>
  this.actions$.pipe(
    ofType(loadUsers),
    mergeMap(() => this.api.getUsers().pipe(
      map(users => loadUsersSuccess({ users }))
    ))
  )
);
```

---

### Q6: What are the advantages of using Signals for state management?

**Answer:**

**Advantages of Signals (Angular 17+):**

```typescript
import { signal, computed, effect } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class CartStore {
  // 1. Simple, readable syntax
  private items = signal<CartItem[]>([]);
  private discount = signal(0);

  // 2. Computed values - automatically tracked
  total = computed(() => {
    const subtotal = this.items().reduce((sum, i) => sum + i.price, 0);
    return subtotal * (1 - this.discount());
  });

  // 3. No subscriptions to manage - no memory leaks
  // 4. Synchronous reads - no async pipe needed in template
  // 5. Fine-grained reactivity - only affected components update
}
```

**Comparison:**

| Feature | BehaviorSubject | Signals |
|---------|-----------------|---------|
| Syntax | More verbose | Cleaner |
| Subscription mgmt | Manual | Automatic |
| Change detection | Zone-based | Granular |
| Derived state | `pipe(map())` | `computed()` |
| Side effects | `subscribe()` | `effect()` |
| Template usage | `async` pipe | Direct call |
| Memory leaks | Possible | Unlikely |

---

### Q7: How do you handle component state vs application state?

**Answer:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    State Categories                                  │
├─────────────────┬───────────────────────────────────────────────────┤
│ Type            │ Examples                       │ Storage          │
├─────────────────┼────────────────────────────────┼──────────────────┤
│ UI State        │ Modal open, form dirty,        │ Component        │
│ (Component)     │ dropdown expanded              │                  │
├─────────────────┼────────────────────────────────┼──────────────────┤
│ Feature State   │ Todo list, product filters,    │ Service/Signals  │
│                 │ search results                 │                  │
├─────────────────┼────────────────────────────────┼──────────────────┤
│ App State       │ Current user, theme,           │ Global Store     │
│                 │ permissions                    │                  │
├─────────────────┼────────────────────────────────┼──────────────────┤
│ Server State    │ API responses, cached data     │ Service + Cache  │
│                 │                                │                  │
├─────────────────┼────────────────────────────────┼──────────────────┤
│ URL State       │ Route params, query strings    │ Router           │
│                 │                                │                  │
└─────────────────┴────────────────────────────────┴──────────────────┘
```

**Guidelines:**
```typescript
// Component state - stays in component
@Component({...})
export class DropdownComponent {
  isOpen = false;  // UI state
  
  toggle() { this.isOpen = !this.isOpen; }
}

// Feature state - in dedicated service/store
@Injectable({ providedIn: 'root' })
export class TodoStore {
  private todos = signal<Todo[]>([]);
  // Shared across components in feature
}

// App state - global store
@Injectable({ providedIn: 'root' })
export class AppStore {
  private user = signal<User | null>(null);
  // Available everywhere
}
```

---

## Advanced Level

### Q8: How would you implement optimistic updates?

**Answer:**
Optimistic updates show changes immediately before server confirmation, rolling back on error:

```typescript
@Injectable({ providedIn: 'root' })
export class TodoStore {
  private todos = signal<Todo[]>([]);
  private http = inject(HttpClient);

  async toggleTodo(id: string) {
    const previousState = this.todos();
    
    // 1. Optimistically update UI
    this.todos.update(todos =>
      todos.map(t => t.id === id ? { ...t, completed: !t.completed } : t)
    );

    try {
      // 2. Make API call
      const todo = previousState.find(t => t.id === id)!;
      await firstValueFrom(
        this.http.patch(`/api/todos/${id}`, { completed: !todo.completed })
      );
    } catch (error) {
      // 3. Rollback on error
      this.todos.set(previousState);
      this.notifyError('Failed to update todo');
    }
  }

  async deleteTodo(id: string) {
    const previousState = this.todos();
    
    // Optimistic delete
    this.todos.update(todos => todos.filter(t => t.id !== id));

    try {
      await firstValueFrom(this.http.delete(`/api/todos/${id}`));
    } catch (error) {
      // Rollback
      this.todos.set(previousState);
      this.notifyError('Failed to delete todo');
    }
  }
}
```

**NgRx approach with Effects:**
```typescript
// Actions
export const deleteTodo = createAction('[Todo] Delete', props<{ id: string }>());
export const deleteTodoSuccess = createAction('[Todo] Delete Success', props<{ id: string }>());
export const deleteTodoFailed = createAction('[Todo] Delete Failed', props<{ id: string; previousTodos: Todo[] }>());

// Reducer - optimistic update
on(deleteTodo, (state, { id }) => ({
  ...state,
  todos: state.todos.filter(t => t.id !== id)
})),

// Rollback on failure
on(deleteTodoFailed, (state, { previousTodos }) => ({
  ...state,
  todos: previousTodos
}))

// Effect
deleteTodo$ = createEffect(() =>
  this.actions$.pipe(
    ofType(deleteTodo),
    withLatestFrom(this.store.select(selectTodos)),
    mergeMap(([{ id }, previousTodos]) =>
      this.api.delete(id).pipe(
        map(() => deleteTodoSuccess({ id })),
        catchError(() => of(deleteTodoFailed({ id, previousTodos })))
      )
    )
  )
);
```

---

### Q9: How do you handle state persistence (localStorage/sessionStorage)?

**Answer:**
```typescript
// Generic state persistence utility
function persistState<T>(key: string, state$: BehaviorSubject<T>) {
  // Load on init
  const saved = localStorage.getItem(key);
  if (saved) {
    try {
      state$.next(JSON.parse(saved));
    } catch (e) {
      console.error('Failed to parse saved state');
    }
  }

  // Save on changes
  state$.pipe(
    skip(1), // Skip initial
    debounceTime(1000)
  ).subscribe(state => {
    localStorage.setItem(key, JSON.stringify(state));
  });
}

// Usage
@Injectable({ providedIn: 'root' })
export class ThemeStore {
  private state$ = new BehaviorSubject({ theme: 'light', fontSize: 14 });

  constructor() {
    persistState('theme-settings', this.state$);
  }
}

// NgRx Meta-Reducer for persistence
export function persistStateMetaReducer(reducer: ActionReducer<AppState>): ActionReducer<AppState> {
  return (state, action) => {
    // Hydrate state on init
    if (action.type === '@ngrx/store/init') {
      const saved = localStorage.getItem('appState');
      if (saved) {
        state = JSON.parse(saved);
      }
    }

    const nextState = reducer(state, action);

    // Persist specific slices
    localStorage.setItem('appState', JSON.stringify({
      user: nextState.user,
      settings: nextState.settings
    }));

    return nextState;
  };
}
```

---

### Q10: How do you handle state for real-time updates (WebSocket)?

**Answer:**
```typescript
@Injectable({ providedIn: 'root' })
export class RealtimeStore {
  private messages = signal<Message[]>([]);
  private connectionStatus = signal<'connected' | 'disconnected' | 'connecting'>('disconnected');
  
  private socket!: WebSocket;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect() {
    this.connectionStatus.set('connecting');
    this.socket = new WebSocket('wss://api.example.com/ws');

    this.socket.onopen = () => {
      this.connectionStatus.set('connected');
      this.reconnectAttempts = 0;
    };

    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleMessage(message);
    };

    this.socket.onclose = () => {
      this.connectionStatus.set('disconnected');
      this.attemptReconnect();
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error', error);
    };
  }

  private handleMessage(message: any) {
    switch (message.type) {
      case 'NEW_MESSAGE':
        this.messages.update(msgs => [...msgs, message.data]);
        break;
      case 'UPDATE_MESSAGE':
        this.messages.update(msgs =>
          msgs.map(m => m.id === message.data.id ? message.data : m)
        );
        break;
      case 'DELETE_MESSAGE':
        this.messages.update(msgs =>
          msgs.filter(m => m.id !== message.data.id)
        );
        break;
    }
  }

  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      setTimeout(() => this.connect(), delay);
    }
  }

  send(message: any) {
    if (this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }

  disconnect() {
    this.socket?.close();
  }
}
```

---

### Q11: NgRx vs Signal-based state - when to use which?

**Answer:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Decision Matrix                                       │
├────────────────────────┬────────────────────┬───────────────────────────┤
│ Factor                 │ Use Signals        │ Use NgRx                  │
├────────────────────────┼────────────────────┼───────────────────────────┤
│ Team size              │ 1-5 developers     │ 5+ developers             │
│ App complexity         │ Small-medium       │ Large enterprise          │
│ State complexity       │ Simple-moderate    │ Complex with many effects │
│ Debugging needs        │ Basic              │ Time-travel debugging     │
│ Testing requirements   │ Standard           │ Extensive, isolated       │
│ Learning curve         │ Low                │ Steep                     │
│ Boilerplate            │ Minimal            │ Significant               │
│ Side effects           │ Few                │ Many complex              │
│ Undo/redo needed       │ No                 │ Yes                       │
│ Audit trail needed     │ No                 │ Yes                       │
└────────────────────────┴────────────────────┴───────────────────────────┘
```

**Signals are better when:**
- Starting new Angular 17+ project
- Small-medium team
- Simpler state requirements
- Want minimal boilerplate

**NgRx is better when:**
- Large team needs consistency
- Complex async flows
- Need debugging tools
- Regulatory/audit requirements
- Undo/redo functionality needed

---

### Q12: How do you test state management code?

**Answer:**

**Testing Signal Store:**
```typescript
describe('TodoStore', () => {
  let store: TodoStore;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    store = TestBed.inject(TodoStore);
  });

  it('should add todo', () => {
    store.addTodo('Test todo');
    
    expect(store.todos().length).toBe(1);
    expect(store.todos()[0].title).toBe('Test todo');
  });

  it('should compute stats correctly', () => {
    store.addTodo('Todo 1');
    store.addTodo('Todo 2');
    store.toggleTodo(store.todos()[0].id);

    expect(store.stats().total).toBe(2);
    expect(store.stats().completed).toBe(1);
    expect(store.stats().active).toBe(1);
  });
});
```

**Testing NgRx Reducer:**
```typescript
describe('Cart Reducer', () => {
  it('should add item to cart', () => {
    const item = { productId: 1, name: 'Product', price: 10, quantity: 1 };
    const action = CartActions.addItem({ item });
    const state = cartReducer(initialCartState, action);

    expect(state.items.length).toBe(1);
    expect(state.items[0]).toEqual(item);
  });

  it('should increase quantity for existing item', () => {
    const item = { productId: 1, name: 'Product', price: 10, quantity: 1 };
    const stateWithItem = { ...initialCartState, items: [item] };
    
    const action = CartActions.addItem({ item: { ...item, quantity: 2 } });
    const state = cartReducer(stateWithItem, action);

    expect(state.items.length).toBe(1);
    expect(state.items[0].quantity).toBe(3);
  });
});
```

**Testing NgRx Effects:**
```typescript
describe('Cart Effects', () => {
  let effects: CartEffects;
  let actions$: Observable<Action>;
  let cartApi: jasmine.SpyObj<CartApiService>;

  beforeEach(() => {
    cartApi = jasmine.createSpyObj('CartApiService', ['getCart']);
    
    TestBed.configureTestingModule({
      providers: [
        CartEffects,
        provideMockActions(() => actions$),
        { provide: CartApiService, useValue: cartApi }
      ]
    });

    effects = TestBed.inject(CartEffects);
  });

  it('should load cart successfully', (done) => {
    const items = [{ productId: 1, name: 'Test', price: 10, quantity: 1 }];
    cartApi.getCart.and.returnValue(of(items));
    
    actions$ = of(CartActions.loadCart());

    effects.loadCart$.subscribe(action => {
      expect(action).toEqual(CartActions.loadCartSuccess({ items }));
      done();
    });
  });
});
```

---

## Quick Reference

```
State Management Cheat Sheet:
─────────────────────────────
BehaviorSubject:
  new BehaviorSubject(initial)
  .next(value)
  .getValue()
  .pipe(map(...))

Signals:
  signal(initial)
  set(value)
  update(fn)
  computed(() => ...)
  effect(() => ...)

NgRx:
  Actions: createAction(), createActionGroup()
  Reducer: createReducer(), on()
  Selectors: createSelector()
  Effects: createEffect(), ofType()
  
Store Methods:
  store.dispatch(action)
  store.select(selector)
```
