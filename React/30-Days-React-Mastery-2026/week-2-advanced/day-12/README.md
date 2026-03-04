# 📅 Day 12 – State Management (Industry Level)

## 🎯 Learning Goals
- Master Redux Toolkit
- Learn Zustand
- Explore Jotai
- Understand MobX basics
- Compare all solutions

---

## 📚 Theory

### Redux Toolkit (RTK)

```tsx
// Modern Redux with Redux Toolkit

// 1. Create a slice (combines reducer + actions)
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface CounterState {
  value: number;
  status: 'idle' | 'loading' | 'failed';
}

const initialState: CounterState = {
  value: 0,
  status: 'idle',
};

const counterSlice = createSlice({
  name: 'counter',
  initialState,
  reducers: {
    increment: (state) => {
      state.value += 1;  // Immer allows "mutation"
    },
    decrement: (state) => {
      state.value -= 1;
    },
    incrementByAmount: (state, action: PayloadAction<number>) => {
      state.value += action.payload;
    },
  },
});

export const { increment, decrement, incrementByAmount } = counterSlice.actions;
export default counterSlice.reducer;

// 2. Configure store
import { configureStore } from '@reduxjs/toolkit';

export const store = configureStore({
  reducer: {
    counter: counterSlice.reducer,
    // Add more reducers here
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// 3. Typed hooks
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

// 4. Provide store
import { Provider } from 'react-redux';

function App() {
  return (
    <Provider store={store}>
      <Counter />
    </Provider>
  );
}

// 5. Use in components
function Counter() {
  const count = useAppSelector((state) => state.counter.value);
  const dispatch = useAppDispatch();

  return (
    <div>
      <span>{count}</span>
      <button onClick={() => dispatch(increment())}>+</button>
      <button onClick={() => dispatch(decrement())}>-</button>
    </div>
  );
}

// Async actions with createAsyncThunk
import { createAsyncThunk } from '@reduxjs/toolkit';

export const fetchUser = createAsyncThunk(
  'user/fetchById',
  async (userId: string) => {
    const response = await fetch(`/api/users/${userId}`);
    return response.json();
  }
);

const userSlice = createSlice({
  name: 'user',
  initialState: { user: null, loading: false, error: null },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchUser.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchUser.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(fetchUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});
```

### Zustand

```tsx
// Zustand - minimal, hook-based state management
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

// 1. Create store
interface BearStore {
  bears: number;
  increase: () => void;
  decrease: () => void;
  reset: () => void;
}

const useBearStore = create<BearStore>((set) => ({
  bears: 0,
  increase: () => set((state) => ({ bears: state.bears + 1 })),
  decrease: () => set((state) => ({ bears: state.bears - 1 })),
  reset: () => set({ bears: 0 }),
}));

// 2. Use in components (no provider needed!)
function BearCounter() {
  const bears = useBearStore((state) => state.bears);
  const increase = useBearStore((state) => state.increase);
  
  return (
    <div>
      <span>{bears} bears</span>
      <button onClick={increase}>Add bear</button>
    </div>
  );
}

// 3. With middleware (devtools + persistence)
const useStore = create<StoreState>()(
  devtools(
    persist(
      (set) => ({
        count: 0,
        increment: () => set((state) => ({ count: state.count + 1 })),
      }),
      { name: 'my-storage' }  // localStorage key
    )
  )
);

// 4. Async actions
interface TodoStore {
  todos: Todo[];
  loading: boolean;
  fetchTodos: () => Promise<void>;
  addTodo: (text: string) => void;
}

const useTodoStore = create<TodoStore>((set, get) => ({
  todos: [],
  loading: false,
  
  fetchTodos: async () => {
    set({ loading: true });
    const response = await fetch('/api/todos');
    const todos = await response.json();
    set({ todos, loading: false });
  },

  addTodo: (text) => {
    const newTodo = { id: Date.now(), text, completed: false };
    set((state) => ({ todos: [...state.todos, newTodo] }));
  },
}));

// 5. Computed values / selectors
const useTotalBears = () => useBearStore((state) => state.bears * 2);

// 6. Slices pattern for large stores
interface UserSlice {
  user: User | null;
  setUser: (user: User) => void;
}

interface CartSlice {
  items: CartItem[];
  addItem: (item: CartItem) => void;
}

const createUserSlice = (set: any): UserSlice => ({
  user: null,
  setUser: (user) => set({ user }),
});

const createCartSlice = (set: any): CartSlice => ({
  items: [],
  addItem: (item) => set((state: any) => ({ items: [...state.items, item] })),
});

const useBoundStore = create<UserSlice & CartSlice>()((...a) => ({
  ...createUserSlice(...a),
  ...createCartSlice(...a),
}));
```

### Jotai

```tsx
// Jotai - atomic state management (bottom-up approach)
import { atom, useAtom, useAtomValue, useSetAtom } from 'jotai';

// 1. Create atoms
const countAtom = atom(0);
const textAtom = atom('hello');

// 2. Derived atoms (computed)
const doubleCountAtom = atom((get) => get(countAtom) * 2);

// 3. Writable derived atoms
const uppercaseAtom = atom(
  (get) => get(textAtom).toUpperCase(),
  (get, set, newValue: string) => set(textAtom, newValue.toLowerCase())
);

// 4. Use in components
function Counter() {
  const [count, setCount] = useAtom(countAtom);
  const doubleCount = useAtomValue(doubleCountAtom);  // Read-only
  
  return (
    <div>
      <span>{count} (double: {doubleCount})</span>
      <button onClick={() => setCount(c => c + 1)}>+</button>
    </div>
  );
}

// 5. Async atoms
const userAtom = atom(async (get) => {
  const response = await fetch('/api/user');
  return response.json();
});

// With Suspense
function UserProfile() {
  const user = useAtomValue(userAtom);  // Suspends until resolved
  return <div>{user.name}</div>;
}

// 6. Atom families (parameterized atoms)
import { atomFamily } from 'jotai/utils';

const todoAtomFamily = atomFamily((id: string) =>
  atom(async () => {
    const res = await fetch(`/api/todos/${id}`);
    return res.json();
  })
);

function TodoItem({ id }: { id: string }) {
  const todo = useAtomValue(todoAtomFamily(id));
  return <div>{todo.text}</div>;
}

// 7. Persistence
import { atomWithStorage } from 'jotai/utils';

const themeAtom = atomWithStorage('theme', 'light');
```

### Comparison

```
┌─────────────────────────────────────────────────────────────────┐
│                    State Management Comparison                   │
├────────────┬──────────┬──────────┬──────────┬──────────────────┤
│ Feature    │ Redux TK │ Zustand  │ Jotai    │ Context          │
├────────────┼──────────┼──────────┼──────────┼──────────────────┤
│ Bundle Size│ ~11kb    │ ~1kb     │ ~2kb     │ 0 (built-in)     │
│ Boilerplate│ Medium   │ Minimal  │ Minimal  │ Minimal          │
│ Learning   │ Higher   │ Easy     │ Easy     │ Easy             │
│ DevTools   │ Excellent│ Good     │ Good     │ Basic            │
│ Middleware │ Yes      │ Yes      │ Limited  │ No               │
│ TypeScript │ Good     │ Excellent│ Excellent│ Good             │
│ Performance│ Good     │ Excellent│ Excellent│ Poor for freq.   │
│ Best For   │ Large    │ Medium   │ Medium   │ Simple/theme     │
└────────────┴──────────┴──────────┴──────────┴──────────────────┘

When to use what:

Redux Toolkit:
- Large enterprise applications
- Need strong conventions
- Team already knows Redux
- Need middleware (logging, analytics)
- Complex async flows

Zustand:
- Small to medium apps
- Want minimal boilerplate
- Need simple store
- Want flexibility
- Good performance critical

Jotai:
- React-centric mental model
- Need fine-grained updates
- Like atoms approach
- Using Suspense extensively
- Want bottom-up state design

Context:
- Theme, locale, auth
- Infrequent updates
- Simple needs
- Don't want dependencies
```

---

## 🎯 Interview Questions & Answers

### Q1: Why Redux over Context?
**Answer:**

1. **Performance:** Redux has optimized selectors (useSelector only re-renders when selected state changes). Context re-renders all consumers.

2. **DevTools:** Redux DevTools provide time-travel debugging, action logging, state inspection.

3. **Middleware:** Redux supports middleware for logging, async operations, and more.

4. **Predictable:** Single source of truth, actions are serializable, easy to trace state changes.

5. **Ecosystem:** RTK Query for data fetching, large ecosystem of middleware and tools.

### Q2: What is Redux middleware?
**Answer:** Middleware intercepts actions between dispatch and reducer:

```tsx
// Custom middleware
const logger = (store) => (next) => (action) => {
  console.log('dispatching', action);
  let result = next(action);
  console.log('next state', store.getState());
  return result;
};

// Common middleware:
// - redux-thunk: async actions (included in RTK)
// - redux-saga: complex async flows
// - redux-logger: logging
// - RTK Query: data fetching
```

### Q3: Zustand vs Redux?
**Answer:**

| Zustand | Redux |
|---------|-------|
| ~1kb | ~11kb |
| No provider needed | Needs Provider |
| Less boilerplate | More structure |
| Hook-based | Action/Reducer |
| Good for small-medium | Good for large apps |
| Simpler learning curve | More concepts |

### Q4: What is the flux pattern?
**Answer:** Unidirectional data flow:

```
Action → Dispatcher → Store → View → Action...

1. View triggers action
2. Dispatcher sends to store
3. Store updates state
4. View re-renders
```

Redux implements Flux with: Actions, Reducers, Store, and React-Redux bindings.

---

## ✅ Completion Checklist

- [ ] Can implement Redux Toolkit store
- [ ] Know how to use Zustand
- [ ] Understand Jotai atoms
- [ ] Know when to use which solution
- [ ] Can answer all interview questions

---

**Previous:** [Day 11 - Context API](../day-11/README.md)  
**Next:** [Day 13 - Routing](../day-13/README.md)
