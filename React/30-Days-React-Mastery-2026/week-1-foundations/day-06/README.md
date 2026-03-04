# 📅 Day 6 – Hooks Deep Dive

## 🎯 Learning Goals
- Master useRef
- Understand useMemo
- Learn useCallback
- Explore useReducer
- Build Custom Hooks

---

## 📚 Theory

### useRef

```tsx
import { useRef, useEffect } from 'react';

// Two main uses for useRef:

// 1. DOM References
function TextInput() {
  const inputRef = useRef<HTMLInputElement>(null);

  const focusInput = () => {
    inputRef.current?.focus();
  };

  return (
    <>
      <input ref={inputRef} type="text" />
      <button onClick={focusInput}>Focus Input</button>
    </>
  );
}

// 2. Mutable value that persists across renders (no re-render on change)
function Timer() {
  const intervalRef = useRef<number | null>(null);
  const [count, setCount] = useState(0);

  const startTimer = () => {
    if (intervalRef.current) return;  // Prevent multiple intervals
    
    intervalRef.current = window.setInterval(() => {
      setCount(c => c + 1);
    }, 1000);
  };

  const stopTimer = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  useEffect(() => {
    return () => stopTimer();  // Cleanup on unmount
  }, []);

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={startTimer}>Start</button>
      <button onClick={stopTimer}>Stop</button>
    </div>
  );
}

// Tracking previous value
function usePrevious<T>(value: T): T | undefined {
  const ref = useRef<T>();
  
  useEffect(() => {
    ref.current = value;
  }, [value]);
  
  return ref.current;
}

// Usage
function Example({ count }: { count: number }) {
  const prevCount = usePrevious(count);
  
  return (
    <p>
      Current: {count}, Previous: {prevCount}
    </p>
  );
}

// Ref vs State comparison
// useRef:
// - Changes don't trigger re-render
// - Value persists across renders
// - Synchronous access via .current
// - Good for: DOM refs, timers, previous values, mutable values

// useState:
// - Changes trigger re-render
// - Value persists across renders
// - Asynchronous updates
// - Good for: UI state, data that affects render
```

### useMemo

```tsx
import { useMemo, useState } from 'react';

// Memoize expensive computations
function ExpensiveComponent({ items, filter }: { items: Item[]; filter: string }) {
  // ❌ Runs on every render
  const filteredItems = items.filter(item => 
    item.name.toLowerCase().includes(filter.toLowerCase())
  );

  // ✅ Only recalculates when items or filter changes
  const filteredItems = useMemo(() => 
    items.filter(item => 
      item.name.toLowerCase().includes(filter.toLowerCase())
    ),
    [items, filter]
  );

  return (
    <ul>
      {filteredItems.map(item => <li key={item.id}>{item.name}</li>)}
    </ul>
  );
}

// Memoize object/array references
function Parent() {
  const [count, setCount] = useState(0);
  
  // ❌ New object every render - causes Child to re-render
  const config = { theme: 'dark', size: 'large' };
  
  // ✅ Stable reference - Child won't re-render unnecessarily
  const config = useMemo(() => ({ 
    theme: 'dark', 
    size: 'large' 
  }), []);

  return (
    <>
      <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>
      <MemoizedChild config={config} />
    </>
  );
}

// When to use useMemo:
// 1. Expensive calculations
// 2. Referential equality for props (with memo)
// 3. Dependencies for other hooks

// When NOT to use useMemo:
// 1. Simple calculations
// 2. Values that change every render anyway
// 3. Premature optimization

// Example: Complex data transformation
interface User {
  id: string;
  name: string;
  department: string;
  salary: number;
}

function EmployeeDashboard({ employees }: { employees: User[] }) {
  const stats = useMemo(() => {
    console.log('Computing stats...');
    
    const byDepartment = employees.reduce((acc, emp) => {
      acc[emp.department] = (acc[emp.department] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const totalSalary = employees.reduce((sum, emp) => sum + emp.salary, 0);
    const avgSalary = totalSalary / employees.length;
    
    return { byDepartment, totalSalary, avgSalary };
  }, [employees]);

  return <StatsDisplay stats={stats} />;
}
```

### useCallback

```tsx
import { useCallback, useState, memo } from 'react';

// Memoize function references
function Parent() {
  const [count, setCount] = useState(0);

  // ❌ New function every render
  const handleClick = () => {
    console.log('Clicked');
  };

  // ✅ Same function reference (stable)
  const handleClick = useCallback(() => {
    console.log('Clicked');
  }, []);

  // With dependencies
  const handleIncrement = useCallback(() => {
    setCount(c => c + 1);  // Use functional update to avoid count dependency
  }, []);

  // When you need the current value
  const handleLog = useCallback(() => {
    console.log('Count is:', count);  // Logs correct count
  }, [count]);  // Recreated when count changes

  return (
    <>
      <p>Count: {count}</p>
      <MemoizedButton onClick={handleIncrement} label="Increment" />
    </>
  );
}

// useCallback is useful when passing to memoized children
const Button = memo(function Button({ 
  onClick, 
  label 
}: { 
  onClick: () => void; 
  label: string 
}) {
  console.log('Button rendered');
  return <button onClick={onClick}>{label}</button>;
});

// useCallback vs useMemo
// They're actually the same thing!
useCallback(fn, deps)
// is equivalent to
useMemo(() => fn, deps)

// Example: Event handlers with parameters
function TodoList({ todos, onToggle }: { 
  todos: Todo[]; 
  onToggle: (id: string) => void 
}) {
  // ❌ Creates new function for each todo
  return (
    <ul>
      {todos.map(todo => (
        <TodoItem 
          key={todo.id}
          todo={todo}
          onToggle={() => onToggle(todo.id)}  // New function!
        />
      ))}
    </ul>
  );
}

// ✅ Pass stable callback, handle id in child
const MemoizedTodoItem = memo(function TodoItem({ 
  todo, 
  onToggle 
}: { 
  todo: Todo; 
  onToggle: (id: string) => void 
}) {
  return (
    <li onClick={() => onToggle(todo.id)}>
      {todo.text}
    </li>
  );
});

function TodoList({ todos, onToggle }: Props) {
  const handleToggle = useCallback((id: string) => {
    onToggle(id);
  }, [onToggle]);

  return (
    <ul>
      {todos.map(todo => (
        <MemoizedTodoItem 
          key={todo.id}
          todo={todo}
          onToggle={handleToggle}  // Stable reference
        />
      ))}
    </ul>
  );
}
```

### useReducer

```tsx
import { useReducer, Reducer } from 'react';

// State type
interface State {
  count: number;
  step: number;
  history: number[];
}

// Action types
type Action =
  | { type: 'INCREMENT' }
  | { type: 'DECREMENT' }
  | { type: 'SET_STEP'; payload: number }
  | { type: 'RESET' }
  | { type: 'SET_COUNT'; payload: number };

// Initial state
const initialState: State = {
  count: 0,
  step: 1,
  history: [],
};

// Reducer function
function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'INCREMENT':
      return {
        ...state,
        count: state.count + state.step,
        history: [...state.history, state.count + state.step],
      };
    case 'DECREMENT':
      return {
        ...state,
        count: state.count - state.step,
        history: [...state.history, state.count - state.step],
      };
    case 'SET_STEP':
      return { ...state, step: action.payload };
    case 'SET_COUNT':
      return { ...state, count: action.payload };
    case 'RESET':
      return initialState;
    default:
      return state;
  }
}

// Component using useReducer
function Counter() {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <div>
      <p>Count: {state.count}</p>
      <p>Step: {state.step}</p>
      
      <button onClick={() => dispatch({ type: 'DECREMENT' })}>-</button>
      <button onClick={() => dispatch({ type: 'INCREMENT' })}>+</button>
      <button onClick={() => dispatch({ type: 'RESET' })}>Reset</button>
      
      <input
        type="number"
        value={state.step}
        onChange={e => dispatch({ 
          type: 'SET_STEP', 
          payload: Number(e.target.value) 
        })}
      />
      
      <h4>History</h4>
      <ul>
        {state.history.map((value, index) => (
          <li key={index}>{value}</li>
        ))}
      </ul>
    </div>
  );
}

// Lazy initialization
const [state, dispatch] = useReducer(
  reducer,
  { initialCount: 10 },  // Argument to init function
  (arg) => ({             // Init function
    count: arg.initialCount,
    step: 1,
    history: [],
  })
);

// useState vs useReducer
// useState: simple state, few updates
// useReducer: complex state, many updates, related updates
```

### Custom Hooks

```tsx
// Custom hook naming: must start with "use"

// useLocalStorage
function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = (value: T | ((prev: T) => T)) => {
    try {
      const valueToStore = value instanceof Function 
        ? value(storedValue) 
        : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error('useLocalStorage error:', error);
    }
  };

  return [storedValue, setValue];
}

// useDebounce
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// useToggle
function useToggle(initialValue = false): [boolean, () => void, (value: boolean) => void] {
  const [value, setValue] = useState(initialValue);
  
  const toggle = useCallback(() => setValue(v => !v), []);
  const setToggle = useCallback((v: boolean) => setValue(v), []);
  
  return [value, toggle, setToggle];
}

// useOnClickOutside
function useOnClickOutside(
  ref: RefObject<HTMLElement>,
  handler: (event: MouseEvent | TouchEvent) => void
) {
  useEffect(() => {
    const listener = (event: MouseEvent | TouchEvent) => {
      if (!ref.current || ref.current.contains(event.target as Node)) {
        return;
      }
      handler(event);
    };

    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
}

// useMediaQuery
function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => 
    window.matchMedia(query).matches
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    
    const handler = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, [query]);

  return matches;
}
```

---

## ✅ Tasks

### Task 1: Build useDebounce Hook

Create `src/hooks/useDebounce.ts`:

```tsx
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number = 500): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(timer);
    };
  }, [value, delay]);

  return debouncedValue;
}

// Demo component
export function SearchDemo() {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 300);
  const [results, setResults] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    if (!debouncedSearch) {
      setResults([]);
      return;
    }

    setIsSearching(true);
    
    // Simulate API call
    const timer = setTimeout(() => {
      const mockResults = [
        `Result 1 for "${debouncedSearch}"`,
        `Result 2 for "${debouncedSearch}"`,
        `Result 3 for "${debouncedSearch}"`,
      ];
      setResults(mockResults);
      setIsSearching(false);
    }, 500);

    return () => clearTimeout(timer);
  }, [debouncedSearch]);

  return (
    <div className="search-demo">
      <h2>Debounced Search</h2>
      <input
        type="text"
        value={searchTerm}
        onChange={e => setSearchTerm(e.target.value)}
        placeholder="Type to search..."
      />
      
      <p>Searching for: "{debouncedSearch}"</p>
      
      {isSearching && <p>Searching...</p>}
      
      <ul>
        {results.map((result, index) => (
          <li key={index}>{result}</li>
        ))}
      </ul>
    </div>
  );
}
```

### Task 2: Build useLocalStorage Hook

Create `src/hooks/useLocalStorage.ts`:

```tsx
import { useState, useEffect, useCallback } from 'react';

type SetValue<T> = (value: T | ((prev: T) => T)) => void;

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, SetValue<T>, () => void] {
  // Get from localStorage or use initial value
  const readValue = useCallback((): T => {
    if (typeof window === 'undefined') {
      return initialValue;
    }

    try {
      const item = window.localStorage.getItem(key);
      return item ? (JSON.parse(item) as T) : initialValue;
    } catch (error) {
      console.warn(`Error reading localStorage key "${key}":`, error);
      return initialValue;
    }
  }, [initialValue, key]);

  const [storedValue, setStoredValue] = useState<T>(readValue);

  // Set value in state and localStorage
  const setValue: SetValue<T> = useCallback(
    (value) => {
      try {
        const valueToStore = value instanceof Function 
          ? value(storedValue) 
          : value;
        
        setStoredValue(valueToStore);
        
        if (typeof window !== 'undefined') {
          window.localStorage.setItem(key, JSON.stringify(valueToStore));
          window.dispatchEvent(new Event('local-storage'));
        }
      } catch (error) {
        console.warn(`Error setting localStorage key "${key}":`, error);
      }
    },
    [key, storedValue]
  );

  // Remove from localStorage
  const removeValue = useCallback(() => {
    try {
      setStoredValue(initialValue);
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem(key);
      }
    } catch (error) {
      console.warn(`Error removing localStorage key "${key}":`, error);
    }
  }, [initialValue, key]);

  // Listen for changes in other tabs/windows
  useEffect(() => {
    const handleStorageChange = (event: StorageEvent) => {
      if (event.key === key && event.newValue) {
        setStoredValue(JSON.parse(event.newValue));
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [key]);

  return [storedValue, setValue, removeValue];
}

// Demo component
interface UserPreferences {
  theme: 'light' | 'dark';
  fontSize: number;
  notifications: boolean;
}

const defaultPreferences: UserPreferences = {
  theme: 'light',
  fontSize: 16,
  notifications: true,
};

export function LocalStorageDemo() {
  const [preferences, setPreferences, clearPreferences] = 
    useLocalStorage<UserPreferences>('user-preferences', defaultPreferences);

  return (
    <div 
      className="localStorage-demo" 
      style={{ 
        backgroundColor: preferences.theme === 'dark' ? '#333' : '#fff',
        color: preferences.theme === 'dark' ? '#fff' : '#333',
        fontSize: preferences.fontSize,
      }}
    >
      <h2>useLocalStorage Demo</h2>
      
      <div className="preference">
        <label>
          Theme:
          <select
            value={preferences.theme}
            onChange={e => setPreferences(prev => ({
              ...prev,
              theme: e.target.value as 'light' | 'dark'
            }))}
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </label>
      </div>

      <div className="preference">
        <label>
          Font Size: {preferences.fontSize}px
          <input
            type="range"
            min="12"
            max="24"
            value={preferences.fontSize}
            onChange={e => setPreferences(prev => ({
              ...prev,
              fontSize: Number(e.target.value)
            }))}
          />
        </label>
      </div>

      <div className="preference">
        <label>
          <input
            type="checkbox"
            checked={preferences.notifications}
            onChange={e => setPreferences(prev => ({
              ...prev,
              notifications: e.target.checked
            }))}
          />
          Enable Notifications
        </label>
      </div>

      <button onClick={clearPreferences}>Reset to Defaults</button>
      
      <pre>
        {JSON.stringify(preferences, null, 2)}
      </pre>
      
      <p className="hint">
        Try changing preferences and refreshing the page!
      </p>
    </div>
  );
}
```

---

## 🎯 Interview Questions & Answers

### Q1: When to use useMemo?
**Answer:** Use useMemo for:

1. **Expensive computations** that shouldn't run every render
2. **Referential equality** for props passed to memoized components
3. **Stable dependencies** for other hooks

```tsx
// 1. Expensive computation
const sortedItems = useMemo(() => 
  items.sort((a, b) => a.price - b.price),
  [items]
);

// 2. Stable object for memoized child
const config = useMemo(() => ({ theme: 'dark' }), []);
<MemoizedChild config={config} />

// 3. Stable dependency
const filtered = useMemo(() => items.filter(/*...*/), [items]);
useEffect(() => {
  // filtered is stable
}, [filtered]);
```

**Don't use useMemo for:**
- Simple operations
- Values that change every render
- Premature optimization

### Q2: Difference between useMemo & useCallback?
**Answer:**

```tsx
// useMemo: memoizes a VALUE (any computation result)
const value = useMemo(() => computeExpensiveValue(a, b), [a, b]);

// useCallback: memoizes a FUNCTION
const callback = useCallback(() => doSomething(a, b), [a, b]);

// They're equivalent!
useCallback(fn, deps) === useMemo(() => fn, deps)

// When to use which:
// useMemo → computed values, objects, arrays
// useCallback → event handlers, callbacks passed to children
```

### Q3: useRef vs useState?
**Answer:**

| useRef | useState |
|--------|----------|
| .current mutable | Immutable updates |
| No re-render on change | Re-renders on change |
| Synchronous access | Async updates |
| Persists across renders | Persists across renders |

```tsx
// useState: UI state
const [count, setCount] = useState(0);

// useRef: mutable value without re-render
const renderCount = useRef(0);
renderCount.current++;  // No re-render!

// useRef: DOM references
const inputRef = useRef<HTMLInputElement>(null);
inputRef.current?.focus();

// useRef: previous values, timers, subscriptions
const intervalId = useRef<number | null>(null);
```

### Q4: When to use useReducer over useState?
**Answer:**

```tsx
// useState: simple, independent state
const [name, setName] = useState('');
const [age, setAge] = useState(0);

// useReducer: complex state with these characteristics:
// 1. Multiple sub-values
// 2. Next state depends on previous
// 3. Complex update logic
// 4. Many different actions
// 5. Need to pass dispatch down (stable reference)

const [state, dispatch] = useReducer(reducer, initialState);

// Good for: forms, multi-step wizards, shopping carts
// dispatch is stable - good for useCallback/memoized components
```

### Q5: Rules for custom hooks?
**Answer:**

1. **Name starts with "use"** - Enables lint checks
2. **Only call hooks at top level** - Not in conditions/loops
3. **Only call from React functions** - Components or other hooks
4. **Can use other hooks** - useState, useEffect, etc.
5. **Can return anything** - Value, array, object

```tsx
// ✅ Valid custom hooks
function useCounter(initial: number) {
  const [count, setCount] = useState(initial);
  const increment = () => setCount(c => c + 1);
  return { count, increment };
}

function useWindowSize() {
  const [size, setSize] = useState({ width: 0, height: 0 });
  // ... effect to track size
  return size;
}

// ❌ Invalid - not a hook (doesn't start with use)
function getUser() {  // This is just a function
  const [user, setUser] = useState(null);  // Will error!
}
```

---

## 📝 Notes

```
Personal notes space - add your learnings here:

_______________________________________________

_______________________________________________

_______________________________________________
```

---

## ✅ Completion Checklist

- [ ] Master useRef for DOM and mutable values
- [ ] Understand useMemo for expensive computations
- [ ] Know useCallback for stable function references
- [ ] Can implement useReducer for complex state
- [ ] Understand custom hook patterns
- [ ] Built useDebounce hook
- [ ] Built useLocalStorage hook
- [ ] Can answer all interview questions

---

**Previous:** [Day 5 - useEffect Mastery](../day-05/README.md)  
**Next:** [Day 7 - Mini Project](../day-07/README.md)
