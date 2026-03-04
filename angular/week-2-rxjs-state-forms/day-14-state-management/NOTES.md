# Day 14: State Management in Angular

## Overview

State management handles how data flows through your application. Angular offers multiple approaches from simple to complex.

---

## State Management Options

```
┌─────────────────────────────────────────────────────────────────────┐
│                   State Management Spectrum                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Simple ◄─────────────────────────────────────────────────► Complex │
│                                                                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │Component │  │ Service  │  │ Signals  │  │  NgRx    │  │ NgRx + ││
│  │  State   │  │ + BehSub │  │  Store   │  │  Store   │  │ Effects││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘│
│                                                                      │
│  1-2 comps     Small apps    Medium apps   Large apps   Enterprise  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 1. Component State (Local)

For state used by a single component:

```typescript
@Component({
  selector: 'app-counter',
  template: `
    <p>Count: {{ count }}</p>
    <button (click)="increment()">+</button>
  `
})
export class CounterComponent {
  count = 0;
  
  increment() {
    this.count++;
  }
}
```

---

## 2. Service + BehaviorSubject Pattern

Most common pattern for small-medium apps:

```typescript
// services/user-state.service.ts
import { Injectable, inject } from '@angular/core';
import { BehaviorSubject, Observable, map } from 'rxjs';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

interface UserState {
  currentUser: User | null;
  users: User[];
  loading: boolean;
  error: string | null;
}

const initialState: UserState = {
  currentUser: null,
  users: [],
  loading: false,
  error: null
};

@Injectable({ providedIn: 'root' })
export class UserStateService {
  private state$ = new BehaviorSubject<UserState>(initialState);
  
  // Selectors - expose readonly observables
  readonly currentUser$ = this.state$.pipe(
    map(state => state.currentUser)
  );
  
  readonly users$ = this.state$.pipe(
    map(state => state.users)
  );
  
  readonly loading$ = this.state$.pipe(
    map(state => state.loading)
  );
  
  readonly error$ = this.state$.pipe(
    map(state => state.error)
  );
  
  readonly isAuthenticated$ = this.currentUser$.pipe(
    map(user => !!user)
  );

  // Actions - methods to update state
  setLoading(loading: boolean): void {
    this.updateState({ loading });
  }

  setCurrentUser(user: User | null): void {
    this.updateState({ currentUser: user, error: null });
  }

  setUsers(users: User[]): void {
    this.updateState({ users, loading: false });
  }

  addUser(user: User): void {
    const current = this.state$.getValue();
    this.updateState({ 
      users: [...current.users, user] 
    });
  }

  updateUser(id: string, updates: Partial<User>): void {
    const current = this.state$.getValue();
    const users = current.users.map(u => 
      u.id === id ? { ...u, ...updates } : u
    );
    this.updateState({ users });
  }

  removeUser(id: string): void {
    const current = this.state$.getValue();
    const users = current.users.filter(u => u.id !== id);
    this.updateState({ users });
  }

  setError(error: string): void {
    this.updateState({ error, loading: false });
  }

  reset(): void {
    this.state$.next(initialState);
  }

  // Private helper
  private updateState(partial: Partial<UserState>): void {
    const current = this.state$.getValue();
    this.state$.next({ ...current, ...partial });
  }
}
```

### Using the State Service

```typescript
// components/user-list.component.ts
@Component({
  selector: 'app-user-list',
  template: `
    @if (loading$ | async) {
      <app-spinner></app-spinner>
    }
    
    @if (error$ | async; as error) {
      <div class="error">{{ error }}</div>
    }
    
    @for (user of users$ | async; track user.id) {
      <app-user-card 
        [user]="user"
        (delete)="onDelete($event)"
      />
    }
  `
})
export class UserListComponent implements OnInit {
  private userState = inject(UserStateService);
  private userApi = inject(UserApiService);

  users$ = this.userState.users$;
  loading$ = this.userState.loading$;
  error$ = this.userState.error$;

  ngOnInit() {
    this.loadUsers();
  }

  loadUsers() {
    this.userState.setLoading(true);
    
    this.userApi.getUsers().subscribe({
      next: users => this.userState.setUsers(users),
      error: err => this.userState.setError(err.message)
    });
  }

  onDelete(userId: string) {
    this.userApi.deleteUser(userId).subscribe({
      next: () => this.userState.removeUser(userId),
      error: err => this.userState.setError(err.message)
    });
  }
}
```

---

## 3. Signals Store (Angular 17+)

Modern approach using Angular Signals:

```typescript
// services/todo-store.service.ts
import { Injectable, computed, signal } from '@angular/core';

interface Todo {
  id: number;
  title: string;
  completed: boolean;
}

@Injectable({ providedIn: 'root' })
export class TodoStore {
  // State as signals
  private readonly _todos = signal<Todo[]>([]);
  private readonly _loading = signal(false);
  private readonly _filter = signal<'all' | 'active' | 'completed'>('all');

  // Computed selectors
  readonly todos = this._todos.asReadonly();
  readonly loading = this._loading.asReadonly();
  readonly filter = this._filter.asReadonly();

  readonly filteredTodos = computed(() => {
    const todos = this._todos();
    const filter = this._filter();

    switch (filter) {
      case 'active':
        return todos.filter(t => !t.completed);
      case 'completed':
        return todos.filter(t => t.completed);
      default:
        return todos;
    }
  });

  readonly stats = computed(() => {
    const todos = this._todos();
    return {
      total: todos.length,
      completed: todos.filter(t => t.completed).length,
      active: todos.filter(t => !t.completed).length
    };
  });

  // Actions
  setTodos(todos: Todo[]): void {
    this._todos.set(todos);
  }

  addTodo(title: string): void {
    const newTodo: Todo = {
      id: Date.now(),
      title,
      completed: false
    };
    this._todos.update(todos => [...todos, newTodo]);
  }

  toggleTodo(id: number): void {
    this._todos.update(todos =>
      todos.map(t => t.id === id ? { ...t, completed: !t.completed } : t)
    );
  }

  removeTodo(id: number): void {
    this._todos.update(todos => todos.filter(t => t.id !== id));
  }

  setFilter(filter: 'all' | 'active' | 'completed'): void {
    this._filter.set(filter);
  }

  setLoading(loading: boolean): void {
    this._loading.set(loading);
  }

  clearCompleted(): void {
    this._todos.update(todos => todos.filter(t => !t.completed));
  }
}
```

### Using Signals Store

```typescript
@Component({
  selector: 'app-todo-list',
  template: `
    <div class="stats">
      Total: {{ stats().total }} | 
      Active: {{ stats().active }} | 
      Completed: {{ stats().completed }}
    </div>

    <div class="filters">
      <button (click)="store.setFilter('all')">All</button>
      <button (click)="store.setFilter('active')">Active</button>
      <button (click)="store.setFilter('completed')">Completed</button>
    </div>

    @for (todo of filteredTodos(); track todo.id) {
      <div class="todo-item">
        <input 
          type="checkbox" 
          [checked]="todo.completed"
          (change)="store.toggleTodo(todo.id)"
        >
        <span [class.completed]="todo.completed">{{ todo.title }}</span>
        <button (click)="store.removeTodo(todo.id)">Delete</button>
      </div>
    }

    <button (click)="store.clearCompleted()">Clear Completed</button>
  `
})
export class TodoListComponent {
  protected store = inject(TodoStore);
  
  // Expose computed signals to template
  filteredTodos = this.store.filteredTodos;
  stats = this.store.stats;
}
```

---

## 4. @ngrx/signals (Official Signals Store)

NgRx team's signal-based state management:

```typescript
// npm install @ngrx/signals

import { signalStore, withState, withMethods, withComputed, patchState } from '@ngrx/signals';
import { computed } from '@angular/core';

interface ProductState {
  products: Product[];
  loading: boolean;
  selectedId: number | null;
}

const initialState: ProductState = {
  products: [],
  loading: false,
  selectedId: null
};

export const ProductStore = signalStore(
  { providedIn: 'root' },
  
  // Define state
  withState(initialState),
  
  // Define computed values
  withComputed(({ products, selectedId }) => ({
    selectedProduct: computed(() => 
      products().find(p => p.id === selectedId())
    ),
    productCount: computed(() => products().length)
  })),
  
  // Define methods
  withMethods((store) => ({
    setProducts(products: Product[]) {
      patchState(store, { products, loading: false });
    },
    
    addProduct(product: Product) {
      patchState(store, { 
        products: [...store.products(), product] 
      });
    },
    
    selectProduct(id: number) {
      patchState(store, { selectedId: id });
    },
    
    setLoading(loading: boolean) {
      patchState(store, { loading });
    }
  }))
);

// Usage
@Component({...})
export class ProductListComponent {
  store = inject(ProductStore);
  
  // Access state directly
  products = this.store.products;
  loading = this.store.loading;
  selected = this.store.selectedProduct;
}
```

---

## 5. NgRx Store (Redux Pattern)

For large enterprise applications:

```typescript
// npm install @ngrx/store @ngrx/effects @ngrx/entity

// 1. Define State
// store/cart/cart.state.ts
export interface CartItem {
  productId: number;
  name: string;
  price: number;
  quantity: number;
}

export interface CartState {
  items: CartItem[];
  loading: boolean;
  error: string | null;
}

export const initialCartState: CartState = {
  items: [],
  loading: false,
  error: null
};

// 2. Define Actions
// store/cart/cart.actions.ts
import { createActionGroup, props, emptyProps } from '@ngrx/store';

export const CartActions = createActionGroup({
  source: 'Cart',
  events: {
    'Add Item': props<{ item: CartItem }>(),
    'Remove Item': props<{ productId: number }>(),
    'Update Quantity': props<{ productId: number; quantity: number }>(),
    'Clear Cart': emptyProps(),
    'Load Cart': emptyProps(),
    'Load Cart Success': props<{ items: CartItem[] }>(),
    'Load Cart Failure': props<{ error: string }>()
  }
});

// 3. Define Reducer
// store/cart/cart.reducer.ts
import { createReducer, on } from '@ngrx/store';
import { CartActions } from './cart.actions';

export const cartReducer = createReducer(
  initialCartState,
  
  on(CartActions.addItem, (state, { item }) => ({
    ...state,
    items: addOrUpdateItem(state.items, item)
  })),
  
  on(CartActions.removeItem, (state, { productId }) => ({
    ...state,
    items: state.items.filter(i => i.productId !== productId)
  })),
  
  on(CartActions.updateQuantity, (state, { productId, quantity }) => ({
    ...state,
    items: state.items.map(i =>
      i.productId === productId ? { ...i, quantity } : i
    )
  })),
  
  on(CartActions.clearCart, (state) => ({
    ...state,
    items: []
  })),
  
  on(CartActions.loadCart, (state) => ({
    ...state,
    loading: true
  })),
  
  on(CartActions.loadCartSuccess, (state, { items }) => ({
    ...state,
    items,
    loading: false,
    error: null
  })),
  
  on(CartActions.loadCartFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error
  }))
);

function addOrUpdateItem(items: CartItem[], newItem: CartItem): CartItem[] {
  const existing = items.find(i => i.productId === newItem.productId);
  if (existing) {
    return items.map(i =>
      i.productId === newItem.productId
        ? { ...i, quantity: i.quantity + newItem.quantity }
        : i
    );
  }
  return [...items, newItem];
}

// 4. Define Selectors
// store/cart/cart.selectors.ts
import { createFeatureSelector, createSelector } from '@ngrx/store';

export const selectCartState = createFeatureSelector<CartState>('cart');

export const selectCartItems = createSelector(
  selectCartState,
  state => state.items
);

export const selectCartLoading = createSelector(
  selectCartState,
  state => state.loading
);

export const selectCartError = createSelector(
  selectCartState,
  state => state.error
);

export const selectCartTotal = createSelector(
  selectCartItems,
  items => items.reduce((total, item) => total + (item.price * item.quantity), 0)
);

export const selectCartItemCount = createSelector(
  selectCartItems,
  items => items.reduce((count, item) => count + item.quantity, 0)
);

// 5. Define Effects (Side Effects)
// store/cart/cart.effects.ts
import { Injectable, inject } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { CartApiService } from '../../services/cart-api.service';
import { CartActions } from './cart.actions';
import { catchError, map, mergeMap, of } from 'rxjs';

@Injectable()
export class CartEffects {
  private actions$ = inject(Actions);
  private cartApi = inject(CartApiService);

  loadCart$ = createEffect(() =>
    this.actions$.pipe(
      ofType(CartActions.loadCart),
      mergeMap(() =>
        this.cartApi.getCart().pipe(
          map(items => CartActions.loadCartSuccess({ items })),
          catchError(error => of(CartActions.loadCartFailure({ error: error.message })))
        )
      )
    )
  );

  // Save to server when item added
  saveCart$ = createEffect(() =>
    this.actions$.pipe(
      ofType(CartActions.addItem, CartActions.removeItem, CartActions.updateQuantity),
      mergeMap(() =>
        this.cartApi.saveCart().pipe(
          map(() => ({ type: '[Cart] Save Success' })),
          catchError(() => of({ type: '[Cart] Save Failed' }))
        )
      )
    )
  );
}

// 6. Setup Store
// app.config.ts
import { provideStore } from '@ngrx/store';
import { provideEffects } from '@ngrx/effects';
import { cartReducer } from './store/cart/cart.reducer';
import { CartEffects } from './store/cart/cart.effects';

export const appConfig: ApplicationConfig = {
  providers: [
    provideStore({ cart: cartReducer }),
    provideEffects([CartEffects])
  ]
};

// 7. Use in Component
@Component({
  selector: 'app-cart',
  template: `
    @if (loading$ | async) {
      <app-spinner />
    }
    
    @for (item of items$ | async; track item.productId) {
      <div class="cart-item">
        {{ item.name }} - {{ item.quantity }} x {{ item.price | currency }}
        <button (click)="remove(item.productId)">Remove</button>
      </div>
    }
    
    <div class="total">Total: {{ total$ | async | currency }}</div>
  `
})
export class CartComponent implements OnInit {
  private store = inject(Store);

  items$ = this.store.select(selectCartItems);
  loading$ = this.store.select(selectCartLoading);
  total$ = this.store.select(selectCartTotal);

  ngOnInit() {
    this.store.dispatch(CartActions.loadCart());
  }

  remove(productId: number) {
    this.store.dispatch(CartActions.removeItem({ productId }));
  }
}
```

---

## State Management Decision Matrix

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    When to Use What?                                       │
├────────────────────┬────────────────────────────────────────────────────────┤
│ Criteria           │ Recommendation                                         │
├────────────────────┼────────────────────────────────────────────────────────┤
│ 1-5 components     │ Component state or parent-child communication         │
│ share same data    │                                                        │
├────────────────────┼────────────────────────────────────────────────────────┤
│ Simple app,        │ Service + BehaviorSubject                              │
│ few shared states  │                                                        │
├────────────────────┼────────────────────────────────────────────────────────┤
│ Medium app,        │ Signals Store (custom or @ngrx/signals)               │
│ Angular 17+        │                                                        │
├────────────────────┼────────────────────────────────────────────────────────┤
│ Large app,         │ NgRx Store + Effects                                   │
│ many developers    │                                                        │
├────────────────────┼────────────────────────────────────────────────────────┤
│ Complex async,     │ NgRx Effects or custom Effects with RxJS              │
│ side effects       │                                                        │
├────────────────────┼────────────────────────────────────────────────────────┤
│ Need time-travel   │ NgRx with DevTools                                     │
│ debugging          │                                                        │
└────────────────────┴────────────────────────────────────────────────────────┘
```

---

## Best Practices

### 1. Single Source of Truth
```typescript
// Bad - duplicated state
@Component({...})
class UserComponent {
  users: User[] = [];  // Duplicated from service
}

// Good - derive from store
@Component({...})
class UserComponent {
  users$ = this.userState.users$;  // Single source
}
```

### 2. Immutable Updates
```typescript
// Bad - mutating state
this.state.users.push(newUser);

// Good - immutable update
this.updateState({
  users: [...current.users, newUser]
});
```

### 3. Normalize Complex Data
```typescript
// Bad - nested data
{
  orders: [
    { id: 1, user: { id: 1, name: 'John' }, items: [...] }
  ]
}

// Good - normalized
{
  orders: { 1: { id: 1, userId: 1, itemIds: [1, 2] } },
  users: { 1: { id: 1, name: 'John' } },
  items: { 1: {...}, 2: {...} }
}
```

### 4. Use Selectors for Derived State
```typescript
// Don't compute in template
<div>{{ (items$ | async)?.filter(i => i.active).length }}</div>

// Use selector
readonly activeCount$ = this.state$.pipe(
  map(s => s.items.filter(i => i.active).length)
);
```

---

## Summary

| Pattern | Complexity | Best For |
|---------|------------|----------|
| Component State | ★☆☆ | Single component |
| Service + BehaviorSubject | ★★☆ | Small-medium apps |
| Signals Store | ★★☆ | Modern Angular apps |
| @ngrx/signals | ★★★ | Medium-large apps |
| NgRx Store | ★★★★ | Enterprise apps |
