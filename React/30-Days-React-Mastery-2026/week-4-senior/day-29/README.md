# 📅 Day 29 – Interview Questions Bank

## 🎯 Learning Goals
- Master common React interview questions
- Practice technical explanations
- Prepare for system design rounds
- Build confidence for interviews

---

## 📚 Questions by Category

### React Fundamentals

**Q1: What is the Virtual DOM and how does it work?**
```
The Virtual DOM is a lightweight JavaScript representation of the actual DOM. 
When state changes:
1. React creates a new Virtual DOM tree
2. Compares it with the previous tree (diffing)
3. Calculates the minimum changes needed
4. Batches and applies changes to the real DOM

Benefits: Performance (batch updates), Declarative programming, Cross-platform (React Native uses same reconciliation)
```

**Q2: Explain the component lifecycle in React 18+**
```
Mounting:
1. constructor (class) / initial render (function)
2. render / return JSX
3. DOM updates
4. useEffect runs (or componentDidMount)

Updating:
1. Props/state change triggers re-render
2. render / return JSX  
3. DOM updates
4. useEffect cleanup → useEffect runs

Unmounting:
1. useEffect cleanup (or componentWillUnmount)

Note: Strict Mode in dev runs effects twice to detect issues.
```

**Q3: What's the difference between controlled and uncontrolled components?**
```
Controlled: React state drives the input value
- value={state}, onChange={setState}
- React is "single source of truth"
- Use for: validation, formatting, conditional disabling

Uncontrolled: DOM manages its own state
- Use ref to read value: inputRef.current.value
- defaultValue for initial value
- Use for: simple forms, file inputs, integration with non-React code
```

---

### Hooks Deep Dive

**Q4: Why can't hooks be called conditionally?**
```
React relies on call order to track hook state. Each render must call hooks 
in the same order.

❌ Bad:
if (condition) {
  const [state, setState] = useState(); // Different order each render!
}

✅ Good:
const [state, setState] = useState();
// Use state conditionally, not the hook itself
```

**Q5: Explain useCallback vs useMemo**
```
useMemo: Memoizes a computed VALUE
const sortedList = useMemo(() => list.sort(), [list]);

useCallback: Memoizes a FUNCTION reference
const handleClick = useCallback(() => onClick(id), [id, onClick]);

Both prevent unnecessary recalculations/re-renders when dependencies haven't changed.

useCallback(fn, deps) is equivalent to useMemo(() => fn, deps)
```

**Q6: When would useRef be preferred over useState?**
```
useRef when:
- Value change shouldn't trigger re-render (counters, timers, previous values)
- Accessing DOM elements directly
- Storing mutable values across renders

useState when:
- Value change should update UI
- Value is part of render output
```

**Q7: How does useEffect handle cleanup?**
```tsx
useEffect(() => {
  const subscription = subscribe(id);
  
  return () => {
    // Cleanup runs:
    // 1. Before effect runs again (deps changed)
    // 2. When component unmounts
    subscription.unsubscribe();
  };
}, [id]);

Common cleanup: clear timers, cancel requests, remove event listeners
```

---

### State Management

**Q8: Context vs Redux vs Zustand - when to use each?**
```
Context API:
- Small apps, few consumers
- Infrequent updates (theme, auth)
- ⚠️ Re-renders all consumers on any change

Redux Toolkit:
- Large apps, complex state
- Need time-travel debugging
- Team familiar with flux pattern
- Middleware for async logic

Zustand:
- Medium apps, simple API
- No boilerplate
- Selective subscriptions (no re-render issues)
- Easy to learn
```

**Q9: How do you prevent unnecessary re-renders with Context?**
```tsx
// 1. Split contexts
const ThemeContext = createContext();
const UserContext = createContext();

// 2. Memoize provider value
const value = useMemo(() => ({ user, setUser }), [user]);

// 3. Use selectors (with use-context-selector library)
const name = useContextSelector(UserContext, (ctx) => ctx.user.name);

// 4. Split state and dispatch contexts
const StateContext = createContext();
const DispatchContext = createContext();
```

---

### Performance

**Q10: How would you optimize a slow React application?**
```
1. Identify bottleneck:
   - React DevTools Profiler
   - Chrome Performance tab
   - Lighthouse audit

2. Common fixes:
   - Virtualization for long lists (react-virtual)
   - Code splitting with lazy()
   - Memoization (memo, useMemo, useCallback)
   - Avoid inline objects/functions in render
   - Fix expensive computations

3. Network:
   - Prefetching data
   - Caching with React Query
   - Image optimization

4. Bundle:
   - Analyze with source-map-explorer
   - Tree shaking
   - Dynamic imports
```

**Q11: How does React.memo work? When should you use it?**
```tsx
const MemoizedComponent = React.memo(MyComponent);

// Only re-renders if props changed (shallow comparison)

Use when:
✅ Component renders often with same props
✅ Component is expensive to render
✅ Parent re-renders frequently

Don't use when:
❌ Props change every render anyway
❌ Component is simple/cheap
❌ Premature optimization
```

---

### Advanced Patterns

**Q12: Explain Higher-Order Components (HOC) vs Render Props vs Hooks**
```tsx
// HOC: Wraps component, adds props
const withAuth = (Component) => (props) => {
  const auth = useAuth();
  return <Component {...props} auth={auth} />;
};

// Render Props: Child is a function
<DataFetcher url="/api/data">
  {(data, loading) => <Display data={data} />}
</DataFetcher>

// Custom Hook: Preferred in modern React
const { data, loading } = useFetch('/api/data');

Hooks are preferred because:
- No wrapper hell
- Better TypeScript support
- Easier to compose
```

**Q13: What are React Server Components?**
```
Components that render ONLY on the server:
- Zero client-side JavaScript
- Direct database/file access
- Can't use hooks or browser APIs
- Default in Next.js App Router

Benefits:
- Smaller bundles
- Faster initial load
- SEO by default
- Secure (secrets stay on server)

Use 'use client' directive for Client Components when you need interactivity.
```

---

### Testing

**Q14: How do you test a component that uses hooks?**
```tsx
// Component test with Testing Library
test('increments counter', async () => {
  render(<Counter />);
  
  await userEvent.click(screen.getByRole('button'));
  
  expect(screen.getByText('Count: 1')).toBeInTheDocument();
});

// Hook test with renderHook
test('useCounter', () => {
  const { result } = renderHook(() => useCounter());
  
  act(() => result.current.increment());
  
  expect(result.current.count).toBe(1);
});

// Custom hook with context
const wrapper = ({ children }) => (
  <AuthProvider>{children}</AuthProvider>
);

renderHook(() => useAuth(), { wrapper });
```

**Q15: What is the Testing Trophy and why?**
```
        /\      E2E (few)
       /  \     - Full user flows
      /----\    Integration (most)    
     /      \   - Components working together
    /--------\  Unit (some)
   /          \ - Pure functions, utilities

Why Integration tests are most valuable:
- Test real user behavior
- High confidence
- Not brittle to implementation changes
- Good balance of speed vs coverage
```

---

### System Design

**Q16: How would you design a real-time chat application?**
```
Components:
- MessageList (virtualized for performance)
- MessageInput (with typing indicators)
- ConversationList

State:
- Messages: TanStack Query with WebSocket updates
- UI state: Zustand
- Typing indicators: Ephemeral state via WebSocket

Real-time:
- WebSocket for messages and presence
- Optimistic updates for sent messages
- Reconnection with exponential backoff

Key considerations:
- Message ordering (timestamps, sequence numbers)
- Offline support (IndexedDB queue)
- Infinite scroll with cursor pagination
```

**Q17: How do you handle authentication in a React app?**
```tsx
Architecture:
1. AuthContext provides user state globally
2. Token stored in httpOnly cookie (secure)
3. Axios interceptor handles refresh
4. Protected routes check auth

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  
  // Check auth on mount
  useEffect(() => {
    checkAuth().then(setUser);
  }, []);

  const login = async (credentials) => {
    const user = await api.login(credentials);
    setUser(user);
  };

  const logout = async () => {
    await api.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

---

### Behavioral Questions

**Q18: Tell me about a challenging React bug you solved**
```
Structure your answer:
1. Situation: What was the context/problem?
2. Task: What was your responsibility?
3. Action: What did you do specifically?
4. Result: What was the outcome?

Example:
"We had a memory leak causing performance degradation over time. 
I used Chrome DevTools to take heap snapshots, found useEffect 
wasn't cleaning up WebSocket subscriptions. Fixed by adding 
proper cleanup, added ESLint rule for useEffect dependencies, 
and documented the pattern for the team."
```

---

## ✅ Practice Strategy

1. **Daily:** Answer 5 questions aloud
2. **Code:** Implement answers, not just explain
3. **Mock:** Practice with a partner
4. **Review:** Record yourself, identify gaps

---

## ✅ Completion Checklist

- [ ] Master fundamentals questions
- [ ] Know hooks deeply
- [ ] Understand state management
- [ ] Can explain performance optimization
- [ ] Practice system design questions

---

**Previous:** [Day 28 - System Design](../day-28/README.md)  
**Next:** [Day 30 - Mock Interview](../day-30/README.md)
