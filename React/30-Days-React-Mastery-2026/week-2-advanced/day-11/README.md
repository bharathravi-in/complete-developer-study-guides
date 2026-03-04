# 📅 Day 11 – Context API

## 🎯 Learning Goals
- Deep understanding of Context
- Performance considerations
- When NOT to use Context
- Advanced patterns

---

## 📚 Theory

### Context Fundamentals

```tsx
import { createContext, useContext, useState, ReactNode } from 'react';

// 1. Create Context with type
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | null>(null);

// 2. Create Provider
function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<'light' | 'dark'>('light');
  
  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// 3. Create custom hook
function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

// 4. Usage
function App() {
  return (
    <ThemeProvider>
      <Header />
      <MainContent />
    </ThemeProvider>
  );
}

function Header() {
  const { theme, toggleTheme } = useTheme();
  return (
    <header className={theme}>
      <button onClick={toggleTheme}>Toggle Theme</button>
    </header>
  );
}
```

### Context Performance Issues

```tsx
// ⚠️ Problem: Every context consumer re-renders on ANY value change

const AppContext = createContext<{
  user: User;
  theme: Theme;
  notifications: Notification[];
  settings: Settings;
} | null>(null);

function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  const [theme, setTheme] = useState('light');
  const [notifications, setNotifications] = useState([]);
  const [settings, setSettings] = useState({});

  // ❌ New object every render - all consumers re-render!
  const value = {
    user, setUser,
    theme, setTheme,
    notifications, setNotifications,
    settings, setSettings,
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}

// When theme changes, components using ONLY user also re-render!
```

### Optimizing Context

```tsx
// Solution 1: Split contexts by update frequency

const UserContext = createContext<UserContextType | null>(null);
const ThemeContext = createContext<ThemeContextType | null>(null);
const NotificationContext = createContext<NotificationContextType | null>(null);

function Providers({ children }: { children: ReactNode }) {
  return (
    <UserProvider>
      <ThemeProvider>
        <NotificationProvider>
          {children}
        </NotificationProvider>
      </ThemeProvider>
    </UserProvider>
  );
}

// Now theme changes only affect theme consumers!

// Solution 2: Separate state and dispatch contexts

const StateContext = createContext<State | null>(null);
const DispatchContext = createContext<Dispatch | null>(null);

function Provider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <StateContext.Provider value={state}>
      <DispatchContext.Provider value={dispatch}>
        {children}
      </DispatchContext.Provider>
    </StateContext.Provider>
  );
}

// Components that only dispatch don't re-render on state change!
function AddButton() {
  const dispatch = useContext(DispatchContext);  // Stable reference
  return <button onClick={() => dispatch({ type: 'ADD' })}>Add</button>;
}

// Solution 3: Memoize the value object

function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState('light');
  
  const value = useMemo(() => ({
    theme,
    setTheme,
  }), [theme]);  // Only creates new object when theme changes

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

// Solution 4: Use selectors (with libraries like use-context-selector)
import { createContext, useContextSelector } from 'use-context-selector';

const AppContext = createContext({ user: null, theme: 'light' });

function UserDisplay() {
  // Only re-renders when user changes
  const user = useContextSelector(AppContext, state => state.user);
  return <div>{user?.name}</div>;
}

function ThemeDisplay() {
  // Only re-renders when theme changes
  const theme = useContextSelector(AppContext, state => state.theme);
  return <div>{theme}</div>;
}
```

### When NOT to Use Context

```tsx
// ❌ DON'T use Context for:

// 1. Frequently changing values
// Example: Mouse position, scroll position
// Better: Component composition or state management library

// 2. Large amounts of data
// Example: List of thousands of items
// Better: State management library with selectors

// 3. All state management
// Context isn't optimized for frequent updates
// Better: Redux, Zustand, Jotai for complex state

// 4. Props that only go 1-2 levels deep
// Prop drilling isn't always bad
// Context adds complexity

// ✅ DO use Context for:

// 1. Theme (infrequent changes)
// 2. Locale/Language
// 3. Current user
// 4. Feature flags
// 5. UI state (modals, sidebars)
```

### Advanced Context Patterns

```tsx
// Pattern 1: Compound Components with Context
const AccordionContext = createContext<{
  openItems: string[];
  toggle: (id: string) => void;
} | null>(null);

function Accordion({ children, allowMultiple = false }) {
  const [openItems, setOpenItems] = useState<string[]>([]);

  const toggle = (id: string) => {
    setOpenItems(prev => {
      if (prev.includes(id)) {
        return prev.filter(i => i !== id);
      }
      return allowMultiple ? [...prev, id] : [id];
    });
  };

  return (
    <AccordionContext.Provider value={{ openItems, toggle }}>
      <div className="accordion">{children}</div>
    </AccordionContext.Provider>
  );
}

Accordion.Item = function AccordionItem({ 
  id, 
  title, 
  children 
}: { 
  id: string; 
  title: string; 
  children: ReactNode 
}) {
  const context = useContext(AccordionContext);
  if (!context) throw new Error('Must be inside Accordion');
  
  const isOpen = context.openItems.includes(id);

  return (
    <div className="accordion-item">
      <button onClick={() => context.toggle(id)}>
        {title} {isOpen ? '▼' : '▶'}
      </button>
      {isOpen && <div className="content">{children}</div>}
    </div>
  );
};

// Usage
<Accordion allowMultiple>
  <Accordion.Item id="1" title="Section 1">Content 1</Accordion.Item>
  <Accordion.Item id="2" title="Section 2">Content 2</Accordion.Item>
</Accordion>

// Pattern 2: Context with Reducer
interface State {
  items: Item[];
  loading: boolean;
  error: string | null;
}

type Action =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: Item[] }
  | { type: 'FETCH_ERROR'; payload: string }
  | { type: 'ADD_ITEM'; payload: Item };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true, error: null };
    case 'FETCH_SUCCESS':
      return { ...state, loading: false, items: action.payload };
    case 'FETCH_ERROR':
      return { ...state, loading: false, error: action.payload };
    case 'ADD_ITEM':
      return { ...state, items: [...state.items, action.payload] };
    default:
      return state;
  }
}

const ItemsContext = createContext<{
  state: State;
  dispatch: React.Dispatch<Action>;
} | null>(null);
```

---

## 🎯 Interview Questions & Answers

### Q1: What is Context API?
**Answer:** Context provides a way to pass data through the component tree without having to pass props manually at every level.

Components: `createContext`, `Provider`, `useContext`

```tsx
const Context = createContext(defaultValue);

<Context.Provider value={value}>
  {children}
</Context.Provider>

const value = useContext(Context);
```

### Q2: Context vs Redux - when to use each?
**Answer:**

| Context | Redux |
|---------|-------|
| Built-in, no extra deps | External library |
| Simple state sharing | Complex state logic |
| Infrequent updates | Frequent updates |
| No devtools | Great devtools |
| No middleware | Middleware support |
| Re-renders all consumers | Optimized selectors |

**Use Context for:** Theme, user, locale, feature flags
**Use Redux for:** Complex app state, frequent updates, need for devtools

### Q3: Why does Context cause performance issues?
**Answer:** When context value changes, ALL consuming components re-render, even if they only use part of the value.

```tsx
// If theme changes, UserComponent re-renders too!
const value = { user, theme };
<Context.Provider value={value}>

// Solution: Split contexts
<UserContext.Provider value={user}>
<ThemeContext.Provider value={theme}>
```

### Q4: How to optimize Context performance?
**Answer:**
1. **Split contexts** by update frequency
2. **Memoize value** with useMemo
3. **Separate state/dispatch** contexts
4. **Use selectors** (use-context-selector library)
5. **Lift content up** - pass components as children

---

## ✅ Completion Checklist

- [ ] Understand Context creation and usage
- [ ] Know performance implications
- [ ] Know when NOT to use Context
- [ ] Can implement advanced patterns
- [ ] Can answer all interview questions

---

**Previous:** [Day 10 - Error Handling](../day-10/README.md)  
**Next:** [Day 12 - State Management](../day-12/README.md)
