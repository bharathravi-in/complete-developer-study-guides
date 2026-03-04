# 📅 Day 9 – Performance Optimization

## 🎯 Learning Goals
- Master React.memo
- Effective use of useMemo and useCallback
- Implement lazy loading
- Understand code splitting
- Use Suspense for loading states

---

## 📚 Theory

### React.memo

```tsx
import { memo, useState } from 'react';

// React.memo prevents re-render when props haven't changed

// Without memo - re-renders every time parent renders
function ExpensiveList({ items }: { items: Item[] }) {
  console.log('ExpensiveList rendered');
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}

// With memo - only re-renders when items change
const MemoizedList = memo(function ExpensiveList({ items }: { items: Item[] }) {
  console.log('MemoizedList rendered');
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
});

// Custom comparison function
const MemoizedComponent = memo(
  function Component({ user, onClick }: Props) {
    return <div onClick={onClick}>{user.name}</div>;
  },
  // Custom areEqual function
  (prevProps, nextProps) => {
    // Return true if props are equal (skip re-render)
    // Return false if props are different (re-render)
    return (
      prevProps.user.id === nextProps.user.id &&
      prevProps.user.name === nextProps.user.name
    );
  }
);

// Common mistake: new objects/arrays break memo
function Parent() {
  const [count, setCount] = useState(0);
  
  // ❌ BAD: New array every render - memo is useless!
  const items = [1, 2, 3];
  
  // ✅ GOOD: Stable reference
  const items = useMemo(() => [1, 2, 3], []);
  
  return <MemoizedList items={items} />;
}
```

### useMemo Deep Dive

```tsx
import { useMemo, useState } from 'react';

// useMemo caches expensive calculations

function DataTable({ data, sortKey }: { data: Item[]; sortKey: string }) {
  // ❌ Runs every render
  const sortedData = data.sort((a, b) => 
    a[sortKey].localeCompare(b[sortKey])
  );

  // ✅ Only recalculates when data or sortKey changes
  const sortedData = useMemo(() => {
    console.log('Sorting data...');
    return [...data].sort((a, b) => a[sortKey].localeCompare(b[sortKey]));
  }, [data, sortKey]);

  return (
    <table>
      {sortedData.map(item => (
        <tr key={item.id}>
          <td>{item.name}</td>
        </tr>
      ))}
    </table>
  );
}

// When to use useMemo:

// 1. Expensive calculations
const expensiveResult = useMemo(() => {
  return performHeavyComputation(input);
}, [input]);

// 2. Stable object/array references for memoized children
const config = useMemo(() => ({
  theme: 'dark',
  lang: 'en',
}), []);

// 3. Derived state
const filteredItems = useMemo(() => 
  items.filter(item => item.active),
  [items]
);

// When NOT to use useMemo:

// 1. Simple operations
// ❌ Unnecessary - concat is cheap
const fullName = useMemo(() => 
  `${firstName} ${lastName}`, 
  [firstName, lastName]
);
// ✅ Just calculate directly
const fullName = `${firstName} ${lastName}`;

// 2. New reference every render anyway
// ❌ deps change every render
const result = useMemo(() => ({ count }), [count]);
```

### useCallback Deep Dive

```tsx
import { useCallback, useState, memo } from 'react';

// useCallback caches function references

// Child component that is memoized
const SearchInput = memo(function SearchInput({
  value,
  onChange,
  onSubmit,
}: {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
}) {
  console.log('SearchInput rendered');
  return (
    <div>
      <input 
        value={value} 
        onChange={e => onChange(e.target.value)} 
      />
      <button onClick={onSubmit}>Search</button>
    </div>
  );
});

function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  // ❌ New function every render - SearchInput always re-renders
  const handleChange = (value: string) => setQuery(value);
  const handleSubmit = () => search(query);

  // ✅ Stable function references - SearchInput only re-renders when needed
  const handleChange = useCallback((value: string) => {
    setQuery(value);
  }, []);

  const handleSubmit = useCallback(() => {
    search(query).then(setResults);
  }, [query]); // Recreated when query changes

  return (
    <div>
      <SearchInput 
        value={query} 
        onChange={handleChange} 
        onSubmit={handleSubmit}
      />
      <Results data={results} />
    </div>
  );
}

// Common pattern: useCallback with functional updates
function Counter() {
  const [count, setCount] = useState(0);

  // ❌ Has count in deps - recreated when count changes
  const increment = useCallback(() => {
    setCount(count + 1);
  }, [count]);

  // ✅ No deps needed - always stable
  const increment = useCallback(() => {
    setCount(c => c + 1);
  }, []);

  return <Button onClick={increment}>Count: {count}</Button>;
}
```

### Lazy Loading & Code Splitting

```tsx
import { lazy, Suspense, useState } from 'react';

// lazy() for code splitting components
const HeavyChart = lazy(() => import('./components/HeavyChart'));
const AdminPanel = lazy(() => import('./components/AdminPanel'));
const Settings = lazy(() => import('./pages/Settings'));

// Named exports require different syntax
const MyComponent = lazy(() => 
  import('./components/MyModule').then(module => ({
    default: module.MyComponent
  }))
);

// Usage with Suspense
function App() {
  const [showChart, setShowChart] = useState(false);

  return (
    <div>
      <button onClick={() => setShowChart(true)}>
        Show Chart
      </button>

      {showChart && (
        <Suspense fallback={<div>Loading chart...</div>}>
          <HeavyChart />
        </Suspense>
      )}
    </div>
  );
}

// Route-based code splitting
import { Routes, Route } from 'react-router-dom';

const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import('./pages/About'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Suspense>
  );
}

// Preloading on hover
const Settings = lazy(() => import('./pages/Settings'));

function Navigation() {
  const preloadSettings = () => {
    import('./pages/Settings');  // Preload on hover
  };

  return (
    <nav>
      <Link 
        to="/settings" 
        onMouseEnter={preloadSettings}
      >
        Settings
      </Link>
    </nav>
  );
}
```

### Suspense Patterns

```tsx
import { Suspense, lazy } from 'react';

// 1. Component Suspense
const LazyComponent = lazy(() => import('./LazyComponent'));

function App() {
  return (
    <Suspense fallback={<Spinner />}>
      <LazyComponent />
    </Suspense>
  );
}

// 2. Nested Suspense boundaries
function Dashboard() {
  return (
    <div>
      <Suspense fallback={<HeaderSkeleton />}>
        <Header />
      </Suspense>
      
      <div className="content">
        <Suspense fallback={<SidebarSkeleton />}>
          <Sidebar />
        </Suspense>
        
        <Suspense fallback={<MainSkeleton />}>
          <MainContent />
        </Suspense>
      </div>
    </div>
  );
}

// 3. Data fetching with Suspense (React 18+)
// Library support: TanStack Query, Relay, etc.

// With TanStack Query
import { useSuspenseQuery } from '@tanstack/react-query';

function UserProfile({ userId }: { userId: string }) {
  // This suspends until data is ready
  const { data: user } = useSuspenseQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  });

  // No loading check needed - data is guaranteed
  return <div>{user.name}</div>;
}

function App() {
  return (
    <Suspense fallback={<ProfileSkeleton />}>
      <UserProfile userId="123" />
    </Suspense>
  );
}

// 4. SuspenseList (upcoming)
import { SuspenseList } from 'react';

function Feed() {
  return (
    <SuspenseList revealOrder="forwards" tail="collapsed">
      <Suspense fallback={<PostSkeleton />}>
        <Post id={1} />
      </Suspense>
      <Suspense fallback={<PostSkeleton />}>
        <Post id={2} />
      </Suspense>
      <Suspense fallback={<PostSkeleton />}>
        <Post id={3} />
      </Suspense>
    </SuspenseList>
  );
}
```

---

## ✅ Task: Optimize a Slow Component

```tsx
// Before Optimization - slow and inefficient
function SlowProductList({ products, category, searchTerm }: Props) {
  // Problem 1: Filtering on every render
  const filtered = products
    .filter(p => category === 'all' || p.category === category)
    .filter(p => p.name.toLowerCase().includes(searchTerm.toLowerCase()));

  // Problem 2: Sorting on every render
  const sorted = filtered.sort((a, b) => b.rating - a.rating);

  // Problem 3: Complex render for each item
  return (
    <div>
      {sorted.map(product => (
        <ProductCard
          key={product.id}
          product={product}
          // Problem 4: New function every render
          onAddToCart={() => addToCart(product.id)}
          // Problem 5: New style object every render
          style={{ border: '1px solid gray' }}
        />
      ))}
    </div>
  );
}

// After Optimization
const ProductCard = memo(function ProductCard({
  product,
  onAddToCart,
  style,
}: ProductCardProps) {
  return (
    <div style={style}>
      <h3>{product.name}</h3>
      <p>{product.price}</p>
      <button onClick={onAddToCart}>Add to Cart</button>
    </div>
  );
});

function OptimizedProductList({ products, category, searchTerm }: Props) {
  // Fix 1 & 2: Memoize filtering and sorting
  const sortedProducts = useMemo(() => {
    console.log('Filtering and sorting...');
    return products
      .filter(p => category === 'all' || p.category === category)
      .filter(p => p.name.toLowerCase().includes(searchTerm.toLowerCase()))
      .sort((a, b) => b.rating - a.rating);
  }, [products, category, searchTerm]);

  // Fix 4: Stable callback
  const handleAddToCart = useCallback((productId: string) => {
    addToCart(productId);
  }, []);

  // Fix 5: Stable style object
  const cardStyle = useMemo(() => ({
    border: '1px solid gray'
  }), []);

  return (
    <div>
      {sortedProducts.map(product => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToCart={() => handleAddToCart(product.id)}
          style={cardStyle}
        />
      ))}
    </div>
  );
}

// Even better: Pass ID and let child access data
function BetterProductList({ products, category, searchTerm }: Props) {
  const sortedProducts = useMemo(() => {
    // ... filtering and sorting
  }, [products, category, searchTerm]);

  return (
    <div>
      {sortedProducts.map(product => (
        <ProductCardById key={product.id} productId={product.id} />
      ))}
    </div>
  );
}
```

---

## 🎯 Interview Questions & Answers

### Q1: When should you use React.memo?
**Answer:** Use React.memo when:

1. Component renders often with same props
2. Render is expensive (complex calculations, many children)
3. Pure component (same props = same output)

```tsx
// Good candidates:
// - List items
// - Charts/visualizations
// - Complex forms
// - Pure display components

// Bad candidates:
// - Components that always get new props
// - Small, cheap components
// - Components that need to always update
```

### Q2: What's the difference between useMemo and useCallback?
**Answer:**
- **useMemo:** Caches a computed VALUE
- **useCallback:** Caches a FUNCTION reference

```tsx
// useMemo: returns memoized value
const filtered = useMemo(() => items.filter(x => x.active), [items]);

// useCallback: returns memoized function
const handleClick = useCallback(() => onClick(id), [onClick, id]);

// useCallback is just useMemo for functions:
useCallback(fn, deps) === useMemo(() => fn, deps)
```

### Q3: How does code splitting work?
**Answer:** Code splitting breaks your bundle into smaller chunks that load on demand:

1. **How it works:**
   - Webpack/Vite creates separate chunks at `import()` boundaries
   - Chunks load when component is first rendered
   - `lazy()` wraps dynamic import for React

2. **Benefits:**
   - Faster initial load
   - Load only what's needed
   - Better caching

3. **Best practices:**
   - Split at route level
   - Split large, rarely-used components
   - Preload on user intent (hover, scroll)

### Q4: When should you NOT use useMemo/useCallback?
**Answer:**

1. **Cheap operations** - Memoization overhead > computation cost
2. **Dependencies always change** - Cache always invalidates
3. **Primitive values** - Don't need stable references
4. **Premature optimization** - Measure first, then optimize

```tsx
// ❌ Unnecessary - string concat is cheap
const fullName = useMemo(() => `${first} ${last}`, [first, last]);

// ❌ Dependencies change every render
const data = useMemo(() => ({ count }), [count]);

// ❌ No child components need stable reference
const handleClick = useCallback(() => setCount(c => c + 1), []);
// Just use: const handleClick = () => setCount(c => c + 1);
```

### Q5: How does Suspense work?
**Answer:** Suspense lets components "wait" for something before rendering:

1. **Mechanism:** Components throw promises during render
2. **Suspense catches** the promise and shows fallback
3. **When promise resolves**, React re-renders
4. **Nesting:** Multiple boundaries for granular loading states

```tsx
// Lazy loading
const LazyComponent = lazy(() => import('./Heavy'));

// Data fetching (with library support)
function Component() {
  const data = useSuspenseQuery(...);  // Suspends until ready
  return <div>{data}</div>;  // No loading check needed
}

// Boundary
<Suspense fallback={<Spinner />}>
  <LazyComponent />
</Suspense>
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

- [ ] Understand React.memo and when to use it
- [ ] Master useMemo for expensive calculations
- [ ] Master useCallback for stable functions
- [ ] Can implement lazy loading
- [ ] Understand code splitting strategies
- [ ] Know Suspense patterns
- [ ] Can optimize slow components
- [ ] Can answer all interview questions

---

**Previous:** [Day 8 - Rendering Behavior](../day-08/README.md)  
**Next:** [Day 10 - Error Handling](../day-10/README.md)
