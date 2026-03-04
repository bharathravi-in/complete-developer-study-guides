# 📅 Day 23 – Performance at Scale

## 🎯 Learning Goals
- Master large-scale performance optimization
- Understand virtualization techniques
- Learn code splitting strategies
- Implement performance monitoring

---

## 📚 Theory

### Virtualization for Large Lists

```tsx
// Virtual scrolling - render only visible items
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50, // Estimated row height
    overscan: 5, // Render 5 extra items for smooth scrolling
  });

  return (
    <div
      ref={parentRef}
      style={{ height: '600px', overflow: 'auto' }}
    >
      <div
        style={{
          height: `${virtualizer.getTotalSize()}px`,
          width: '100%',
          position: 'relative',
        }}
      >
        {virtualizer.getVirtualItems().map((virtualRow) => (
          <div
            key={virtualRow.key}
            style={{
              position: 'absolute',
              top: 0,
              left: 0,
              width: '100%',
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            {items[virtualRow.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}

// With react-window (simpler API)
import { FixedSizeList, VariableSizeList } from 'react-window';

function WindowedList({ items }: { items: Item[] }) {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>{items[index].name}</div>
  );

  return (
    <FixedSizeList
      height={600}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </FixedSizeList>
  );
}

// Infinite scroll with virtualization
import { useInfiniteQuery } from '@tanstack/react-query';

function InfiniteVirtualList() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage } = useInfiniteQuery({
    queryKey: ['items'],
    queryFn: ({ pageParam = 0 }) => fetchItems(pageParam),
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    initialPageParam: 0,
  });

  const allItems = data?.pages.flatMap(page => page.items) ?? [];
  const parentRef = useRef<HTMLDivElement>(null);

  const virtualizer = useVirtualizer({
    count: hasNextPage ? allItems.length + 1 : allItems.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
    overscan: 5,
  });

  useEffect(() => {
    const lastItem = virtualizer.getVirtualItems().at(-1);
    if (lastItem && lastItem.index >= allItems.length - 1 && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  }, [virtualizer.getVirtualItems(), hasNextPage, isFetchingNextPage, fetchNextPage]);

  return (
    <div ref={parentRef} style={{ height: '600px', overflow: 'auto' }}>
      {/* ... virtual list implementation */}
    </div>
  );
}
```

### Advanced Code Splitting

```tsx
// Route-based splitting (basic)
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

// Component-based splitting
const HeavyChart = lazy(() => import('./components/HeavyChart'));
const RichTextEditor = lazy(() => import('./components/RichTextEditor'));

// Named exports
const UserSettings = lazy(() =>
  import('./pages/Settings').then(module => ({ default: module.UserSettings }))
);

// Preloading on hover
function NavLink({ to, children }: NavLinkProps) {
  const preload = () => {
    if (to === '/dashboard') {
      import('./pages/Dashboard');
    }
  };

  return (
    <Link to={to} onMouseEnter={preload}>
      {children}
    </Link>
  );
}

// Prefetch with React Router
import { prefetchRouteData } from './router';

function Navigation() {
  return (
    <nav>
      <Link
        to="/dashboard"
        onMouseEnter={() => prefetchRouteData('/dashboard')}
      >
        Dashboard
      </Link>
    </nav>
  );
}

// Bundle analysis
// vite.config.ts
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    visualizer({
      open: true,
      filename: 'bundle-stats.html',
      gzipSize: true,
    }),
  ],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts', 'd3'],
          editor: ['prosemirror', 'tiptap'],
        },
      },
    },
  },
});
```

### Memory Management

```tsx
// Cleanup subscriptions and timers
function DataSubscription() {
  useEffect(() => {
    const subscription = dataSource.subscribe(handleData);
    const timer = setInterval(pollData, 1000);

    return () => {
      subscription.unsubscribe();
      clearInterval(timer);
    };
  }, []);

  return <div>...</div>;
}

// Abort fetch on unmount
function FetchComponent({ url }: { url: string }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    fetch(url, { signal: controller.signal })
      .then(res => res.json())
      .then(setData)
      .catch(err => {
        if (err.name !== 'AbortError') {
          console.error(err);
        }
      });

    return () => controller.abort();
  }, [url]);

  return <div>{JSON.stringify(data)}</div>;
}

// WeakMap for external references
const componentCache = new WeakMap<object, ComponentData>();

function CachedComponent({ data }: { data: object }) {
  if (!componentCache.has(data)) {
    componentCache.set(data, processData(data));
  }
  
  const processed = componentCache.get(data)!;
  return <div>{processed.content}</div>;
}

// Detect memory leaks
// In development, use React DevTools Profiler
// Use Chrome DevTools Memory tab for heap snapshots
```

### Performance Monitoring

```tsx
// Web Vitals
import { onCLS, onFCP, onLCP, onTTFB, onINP } from 'web-vitals';

function reportWebVitals() {
  onCLS(metric => sendToAnalytics('CLS', metric));
  onFCP(metric => sendToAnalytics('FCP', metric));
  onLCP(metric => sendToAnalytics('LCP', metric));
  onTTFB(metric => sendToAnalytics('TTFB', metric));
  onINP(metric => sendToAnalytics('INP', metric));
}

// Custom Performance Hook
function usePerformanceMonitor(componentName: string) {
  useEffect(() => {
    const startTime = performance.now();

    return () => {
      const endTime = performance.now();
      console.log(`${componentName} mounted in ${endTime - startTime}ms`);
    };
  }, [componentName]);
}

// React Profiler API
import { Profiler } from 'react';

function onRenderCallback(
  id: string,
  phase: 'mount' | 'update',
  actualDuration: number,
  baseDuration: number,
  startTime: number,
  commitTime: number,
) {
  console.log({
    id,
    phase,
    actualDuration,
    baseDuration,
  });
}

function App() {
  return (
    <Profiler id="App" onRender={onRenderCallback}>
      <Dashboard />
    </Profiler>
  );
}

// Performance budget
// Track bundle size in CI
// package.json
{
  "bundlesize": [
    {
      "path": "./dist/assets/*.js",
      "maxSize": "200 kB"
    },
    {
      "path": "./dist/assets/*.css",
      "maxSize": "50 kB"
    }
  ]
}
```

### Rendering Optimization at Scale

```tsx
// Selector pattern to prevent re-renders
const useUserName = () => useStore(state => state.user.name);
const useUserEmail = () => useStore(state => state.user.email);

// Instead of:
const { name, email } = useStore(state => state.user);

// Windowing for complex UIs
function ComplexDashboard({ widgets }: { widgets: Widget[] }) {
  const [visibleWidgets, setVisibleWidgets] = useState<Set<string>>(new Set());

  useEffect(() => {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        setVisibleWidgets(prev => {
          const next = new Set(prev);
          if (entry.isIntersecting) {
            next.add(entry.target.id);
          } else {
            next.delete(entry.target.id);
          }
          return next;
        });
      });
    });

    // Observe widgets
    return () => observer.disconnect();
  }, []);

  return (
    <div>
      {widgets.map(widget => (
        <div key={widget.id} id={widget.id}>
          {visibleWidgets.has(widget.id) ? (
            <Widget data={widget} />
          ) : (
            <WidgetPlaceholder />
          )}
        </div>
      ))}
    </div>
  );
}

// Debounce expensive operations
function SearchWithDebounce() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  const { data } = useQuery({
    queryKey: ['search', debouncedQuery],
    queryFn: () => search(debouncedQuery),
    enabled: debouncedQuery.length > 2,
  });

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
    />
  );
}
```

---

## ✅ Task: Optimize Large Data Application

Build a dashboard that:
- Renders 100,000+ rows efficiently
- Uses virtualization
- Implements proper code splitting
- Monitors performance metrics
- Handles memory properly

---

## 🎯 Interview Questions & Answers

### Q1: How do you handle rendering 100k items?
**Answer:** Use virtualization (react-virtual, react-window). Only render visible items + overscan. Implement proper key strategy. Consider pagination/infinite scroll for better UX. Avoid complex computations during render.

### Q2: What are Web Vitals and why do they matter?
**Answer:** Core metrics: LCP (loading), INP (interactivity), CLS (visual stability). Google uses them for SEO ranking. They measure real user experience. Tools: web-vitals library, Lighthouse, Chrome DevTools.

### Q3: How do you find and fix memory leaks?
**Answer:** Use Chrome DevTools Memory tab, take heap snapshots, compare over time. Common causes: uncleared timers/subscriptions, closures holding references, event listeners not removed. Always cleanup in useEffect return.

---

## ✅ Completion Checklist

- [ ] Implement virtualization
- [ ] Master code splitting
- [ ] Understand memory management
- [ ] Set up performance monitoring
- [ ] Built optimized large-scale app

---

**Previous:** [Day 22 - Architecture](../day-22/README.md)  
**Next:** [Day 24 - Accessibility](../day-24/README.md)
