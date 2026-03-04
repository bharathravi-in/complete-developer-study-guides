# 📅 Day 8 – Rendering Behavior

## 🎯 Learning Goals
- Understand React rendering phases
- Learn about React Fiber architecture
- Grasp Concurrent Rendering concepts
- Understand Strict Mode behavior

---

## 📚 Theory

### React Rendering Phases

```
React rendering happens in two main phases:

┌─────────────────────────────────────────────────────────────┐
│                     RENDER PHASE                             │
│  (Pure, no side effects, can be paused/aborted/restarted)   │
├─────────────────────────────────────────────────────────────┤
│  1. Component function executes                              │
│  2. Returns JSX (React elements)                             │
│  3. React builds new virtual DOM tree                        │
│  4. Diffing: Compare new tree with previous                  │
│  5. Calculate minimal changes needed                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     COMMIT PHASE                             │
│  (Side effects, synchronous, cannot be interrupted)         │
├─────────────────────────────────────────────────────────────┤
│  1. Apply DOM changes                                        │
│  2. Run useLayoutEffect callbacks                            │
│  3. Browser paints                                           │
│  4. Run useEffect callbacks                                  │
└─────────────────────────────────────────────────────────────┘
```

### Render Phase Deep Dive

```tsx
// What triggers a render:
// 1. Initial mount
// 2. State change (useState, useReducer)
// 3. Props change
// 4. Parent re-render
// 5. Context change

function Parent() {
  const [count, setCount] = useState(0);
  console.log('Parent renders');  // Runs during render phase
  
  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>
        Count: {count}
      </button>
      <Child />  {/* Re-renders when Parent re-renders! */}
    </div>
  );
}

function Child() {
  console.log('Child renders');  // Also runs when Parent re-renders
  return <div>Child</div>;
}

// Render doesn't mean DOM update!
// If virtual DOM is the same, no DOM changes happen.

// Rendering is recursive:
// Parent renders → all children render → their children render...
```

### React Fiber Architecture

```tsx
// Fiber is React's reconciliation algorithm (since React 16)

// Key concepts:

// 1. FIBER NODE
// Each component instance has a fiber node
type Fiber = {
  type: any;              // Component type (function, class, string)
  key: string | null;     // Key for lists
  stateNode: any;         // DOM node or class instance
  child: Fiber | null;    // First child fiber
  sibling: Fiber | null;  // Next sibling fiber
  return: Fiber | null;   // Parent fiber
  alternate: Fiber | null; // Previous version (for diffing)
  effectTag: number;      // What needs to happen (Update, Placement, Deletion)
  // ... more fields
};

// 2. WORK LOOP
// Fiber enables incremental rendering:
// - Work can be split into chunks
// - Work can be paused and resumed
// - Work can be aborted if no longer needed
// - Work can be reused if still valid

// 3. PRIORITY LEVELS
// Different updates have different priorities:
// - Immediate: Must happen synchronously
// - User-blocking: Discrete user interactions (clicks)
// - Normal: Data fetching, most state updates
// - Low: Analytics, prefetching
// - Idle: Non-urgent work

// 4. TWO TREES
// React maintains two fiber trees:
// - current: What's currently rendered
// - workInProgress: Being built during render

// Benefits of Fiber:
// ✅ Interruptible rendering
// ✅ Priority-based scheduling
// ✅ Better animation handling
// ✅ Concurrent features possible
```

### Concurrent Rendering

```tsx
// Concurrent Mode enables React to:
// 1. Prepare multiple versions of UI at same time
// 2. Keep current UI interactive during updates
// 3. Prioritize urgent updates over less urgent ones

// Key Concurrent Features:

// 1. useTransition - mark updates as non-urgent
import { useTransition, useState } from 'react';

function SearchResults() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Urgent: update input immediately
    setQuery(e.target.value);

    // Non-urgent: can be interrupted
    startTransition(() => {
      setResults(filterResults(e.target.value));
    });
  };

  return (
    <div>
      <input value={query} onChange={handleChange} />
      {isPending && <span>Loading...</span>}
      <ResultsList results={results} />
    </div>
  );
}

// 2. useDeferredValue - defer a value
import { useDeferredValue } from 'react';

function SearchPage({ query }: { query: string }) {
  // deferredQuery may "lag behind" query
  const deferredQuery = useDeferredValue(query);
  
  // Shows stale results while new ones are being computed
  return <SearchResults query={deferredQuery} />;
}

// 3. Suspense with concurrent features
import { Suspense } from 'react';

function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <AsyncComponent />
    </Suspense>
  );
}

// Concurrent rendering is automatic in React 18+
// when using createRoot instead of render
import { createRoot } from 'react-dom/client';
const root = createRoot(document.getElementById('root')!);
root.render(<App />);  // Concurrent mode enabled!
```

### Strict Mode

```tsx
// StrictMode helps find problems in your app

import { StrictMode } from 'react';

// In index.tsx
root.render(
  <StrictMode>
    <App />
  </StrictMode>
);

// What StrictMode does (development only):

// 1. Double-invokes render functions
function Component() {
  console.log('Render');  // Logs twice!
  return <div />;
}

// 2. Double-invokes effects
useEffect(() => {
  console.log('Setup');   // Runs twice!
  return () => {
    console.log('Cleanup'); // Runs once between setups
  };
}, []);

// Sequence: Setup → Cleanup → Setup

// Why double invocation?
// - Detect impure render functions
// - Detect missing cleanup functions
// - Detect side effects in render
// - Prepare for Concurrent features

// 3. Warns about deprecated APIs
// - Legacy context API
// - findDOMNode
// - Certain lifecycle methods

// 4. Warns about unsafe lifecycles
// - componentWillMount
// - componentWillReceiveProps
// - componentWillUpdate

// StrictMode has NO effect in production!
```

### Understanding Re-renders

```tsx
// Tool to visualize re-renders
function useRenderCount(componentName: string) {
  const renderCount = useRef(0);
  renderCount.current++;
  
  useEffect(() => {
    console.log(`${componentName} rendered ${renderCount.current} times`);
  });
}

// Common re-render causes:

// 1. Parent re-renders (most common)
function Parent() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>+</button>
      <Child />  {/* Re-renders every time! */}
    </div>
  );
}

// Fix: React.memo
const MemoChild = memo(Child);

// 2. New object/array props
function Parent() {
  const style = { color: 'red' };  // New object every render!
  return <Child style={style} />;
}

// Fix: useMemo
const style = useMemo(() => ({ color: 'red' }), []);

// 3. Inline functions
function Parent() {
  return (
    <Child onClick={() => console.log('click')} />  // New function!
  );
}

// Fix: useCallback
const handleClick = useCallback(() => console.log('click'), []);

// 4. Context changes
const Context = createContext({ theme: 'light' });

function Provider({ children }) {
  const [theme, setTheme] = useState('light');
  
  // New object every render - all consumers re-render!
  const value = { theme, setTheme };
  
  return <Context.Provider value={value}>{children}</Context.Provider>;
}

// Fix: useMemo
const value = useMemo(() => ({ theme, setTheme }), [theme]);
```

---

## 🎯 Interview Questions & Answers

### Q1: Explain React Fiber Architecture
**Answer:** Fiber is React's reconciliation engine (since v16) that enables:

1. **Incremental Rendering:** Work is broken into units that can be paused, resumed, or aborted
2. **Priority Scheduling:** Different updates can have different priorities
3. **Concurrency:** Multiple versions of UI can be prepared simultaneously

Key aspects:
- Each component has a "fiber node" containing its state and relationships
- Maintains two trees: "current" (displayed) and "workInProgress" (being built)
- Uses a work loop that can yield to the browser for higher priority tasks
- Enables features like Suspense, transitions, and streaming

### Q2: What is Concurrent Rendering?
**Answer:** Concurrent rendering allows React to:

1. **Interrupt rendering** to handle more urgent updates
2. **Prepare multiple UI versions** simultaneously
3. **Keep UI responsive** during expensive updates

Tools for concurrent features:
- `useTransition`: Mark state updates as non-urgent (can be interrupted)
- `useDeferredValue`: Let a value "lag behind" during heavy updates
- `Suspense`: Show fallback while waiting for async operations

```tsx
const [isPending, startTransition] = useTransition();

// Urgent: user sees immediate feedback
setInputValue(input);

// Non-urgent: can be deferred
startTransition(() => {
  setSearchResults(filterItems(input));
});
```

### Q3: Why does StrictMode render components twice?
**Answer:** StrictMode double-invokes renders and effects in development to:

1. **Detect impure components** - Render functions should be pure
2. **Find missing cleanups** - Effects should clean up resources
3. **Catch side effects in render** - Side effects belong in useEffect
4. **Prepare for Concurrent features** - Components must handle being rendered multiple times

The sequence for effects is: Setup → Cleanup → Setup

This helps catch bugs like:
- Setting state in render
- Missing event listener cleanup
- Non-idempotent operations

### Q4: What's the difference between Render and Commit phases?
**Answer:**

| Render Phase | Commit Phase |
|--------------|--------------|
| Pure computation | Side effects |
| Creates virtual DOM | Updates real DOM |
| Can be paused/aborted | Synchronous, uninterruptible |
| No DOM access | DOM access allowed |
| May run multiple times | Runs once per update |

Render phase: Component functions execute, JSX is returned, diffing happens
Commit phase: DOM updates, useLayoutEffect runs, paint, then useEffect runs

### Q5: How to prevent unnecessary re-renders?
**Answer:**
1. **React.memo** - Memoize component
2. **useMemo** - Memoize values
3. **useCallback** - Memoize functions
4. **Split components** - Isolate updating parts
5. **Move state down** - Keep state close to where it's used
6. **Lift content up** - Pass children as props

```tsx
// Before: All children re-render on count change
function Parent() {
  const [count, setCount] = useState(0);
  return (
    <div>
      <Counter count={count} setCount={setCount} />
      <ExpensiveComponent />  {/* Re-renders unnecessarily! */}
    </div>
  );
}

// After: Isolate state
function Parent() {
  return (
    <div>
      <CounterWrapper />  {/* Has its own state */}
      <ExpensiveComponent />  {/* Never re-renders! */}
    </div>
  );
}
```

---

## 📝 Notes

```
Personal notes space:

_______________________________________________

_______________________________________________
```

---

## ✅ Completion Checklist

- [ ] Understand render vs commit phases
- [ ] Can explain React Fiber
- [ ] Know concurrent rendering features
- [ ] Understand StrictMode behavior
- [ ] Can identify re-render causes
- [ ] Can answer all interview questions

---

**Previous:** [Week 1 - Day 7](../../week-1-foundations/day-07/README.md)  
**Next:** [Day 9 - Performance Optimization](../day-09/README.md)
