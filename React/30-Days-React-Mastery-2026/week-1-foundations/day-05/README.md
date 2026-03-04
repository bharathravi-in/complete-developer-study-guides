# 📅 Day 5 – useEffect Mastery

## 🎯 Learning Goals
- Master dependency array
- Understand cleanup functions
- Avoid infinite loops
- Learn data fetching patterns
- Prevent memory leaks

---

## 📚 Theory

### useEffect Fundamentals

```tsx
import { useEffect } from 'react';

// useEffect signature
useEffect(
  () => {
    // Effect code (side effects)
    
    return () => {
      // Cleanup code (optional)
    };
  },
  [/* dependencies */]
);

// Three dependency patterns:

// 1. No dependency array - runs after EVERY render
useEffect(() => {
  console.log('Runs after every render');
});

// 2. Empty dependency array - runs ONCE after mount
useEffect(() => {
  console.log('Runs once on mount');
  return () => console.log('Runs on unmount');
}, []);

// 3. With dependencies - runs when dependencies change
useEffect(() => {
  console.log('Runs when count changes');
}, [count]);
```

### Dependency Array Deep Dive

```tsx
// Rules for dependencies:
// 1. Include ALL values from component scope used inside effect
// 2. Functions, objects, arrays are compared by reference
// 3. Primitives are compared by value

function Example({ userId }: { userId: string }) {
  const [user, setUser] = useState(null);
  
  // ✅ userId in deps - effect runs when userId changes
  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);
  
  // ❌ Missing dependency - ESLint will warn
  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, []);  // userId should be in deps!
  
  // Object/Array dependencies - be careful!
  const options = { page: 1 };  // New object every render!
  
  useEffect(() => {
    fetchData(options);
  }, [options]);  // ❌ Runs every render - options is new each time
  
  // ✅ Solution 1: Move object inside effect
  useEffect(() => {
    const options = { page: 1 };
    fetchData(options);
  }, []);
  
  // ✅ Solution 2: useMemo for stable reference
  const options = useMemo(() => ({ page: 1 }), []);
  
  // ✅ Solution 3: Depend on primitive values
  const page = 1;
  useEffect(() => {
    fetchData({ page });
  }, [page]);
}

// Function dependencies
function Example({ onSuccess }: { onSuccess: () => void }) {
  // ❌ onSuccess changes every render if parent doesn't memoize
  useEffect(() => {
    onSuccess();
  }, [onSuccess]);
  
  // ✅ Parent should memoize callback
  // const handleSuccess = useCallback(() => { ... }, []);
}
```

### Cleanup Function

```tsx
// Cleanup runs:
// 1. Before the effect runs again (when deps change)
// 2. When component unmounts

// Pattern 1: Event listeners
useEffect(() => {
  const handleResize = () => setWidth(window.innerWidth);
  window.addEventListener('resize', handleResize);
  
  return () => {
    window.removeEventListener('resize', handleResize);
  };
}, []);

// Pattern 2: Subscriptions
useEffect(() => {
  const subscription = dataSource.subscribe(handleChange);
  
  return () => {
    subscription.unsubscribe();
  };
}, [dataSource]);

// Pattern 3: Timers
useEffect(() => {
  const intervalId = setInterval(() => {
    setCount(c => c + 1);
  }, 1000);
  
  return () => clearInterval(intervalId);
}, []);

// Pattern 4: Abort controllers for fetch
useEffect(() => {
  const abortController = new AbortController();
  
  fetch('/api/data', { signal: abortController.signal })
    .then(res => res.json())
    .then(setData)
    .catch(err => {
      if (err.name !== 'AbortError') {
        setError(err);
      }
    });
  
  return () => abortController.abort();
}, []);

// Pattern 5: Boolean flag for async operations
useEffect(() => {
  let isCancelled = false;
  
  async function fetchData() {
    const result = await fetch('/api/data');
    const data = await result.json();
    
    if (!isCancelled) {
      setData(data);  // Only update if not cancelled
    }
  }
  
  fetchData();
  
  return () => {
    isCancelled = true;
  };
}, []);
```

### Avoiding Infinite Loops

```tsx
// ❌ Infinite loop: setting state without deps
useEffect(() => {
  setCount(count + 1);  // Changes count → runs effect → changes count...
});

// ❌ Infinite loop: object in deps
useEffect(() => {
  setData({ value: 1 });  // New object each time
}, [data]);  // data changed → runs effect → new data...

// ✅ Fixed: use functional update
useEffect(() => {
  setCount(c => c + 1);
}, []);  // Run once

// ✅ Fixed: compare values, not references
useEffect(() => {
  if (data.value !== 1) {
    setData({ value: 1 });
  }
}, [data.value]);

// ❌ Infinite loop: function in deps
function Example() {
  const getData = () => fetch('/api');  // New function every render
  
  useEffect(() => {
    getData();
  }, [getData]);  // Infinite loop!
}

// ✅ Fixed: useCallback
function Example() {
  const getData = useCallback(() => fetch('/api'), []);
  
  useEffect(() => {
    getData();
  }, [getData]);
}

// ✅ Fixed: move function inside effect
function Example() {
  useEffect(() => {
    const getData = () => fetch('/api');
    getData();
  }, []);
}
```

### Data Fetching Pattern

```tsx
interface FetchState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

function useFetch<T>(url: string): FetchState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const abortController = new AbortController();
    
    async function fetchData() {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetch(url, { 
          signal: abortController.signal 
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const json = await response.json();
        setData(json);
      } catch (err) {
        if (err instanceof Error && err.name !== 'AbortError') {
          setError(err);
        }
      } finally {
        setLoading(false);
      }
    }

    fetchData();

    return () => abortController.abort();
  }, [url]);

  return { data, loading, error };
}

// Usage
function UserProfile({ userId }: { userId: string }) {
  const { data: user, loading, error } = useFetch<User>(`/api/users/${userId}`);

  if (loading) return <Spinner />;
  if (error) return <Error message={error.message} />;
  if (!user) return <NotFound />;

  return <UserCard user={user} />;
}
```

### Memory Leaks

```tsx
// Memory leak: setting state after unmount
function BadComponent() {
  const [data, setData] = useState(null);

  useEffect(() => {
    // ❌ If component unmounts before fetch completes,
    // setData will be called on unmounted component
    fetch('/api/data')
      .then(res => res.json())
      .then(data => setData(data));  // Memory leak warning!
  }, []);

  return <div>{data}</div>;
}

// ✅ Fixed with cleanup flag
function GoodComponent() {
  const [data, setData] = useState(null);

  useEffect(() => {
    let isSubscribed = true;

    fetch('/api/data')
      .then(res => res.json())
      .then(data => {
        if (isSubscribed) {
          setData(data);
        }
      });

    return () => {
      isSubscribed = false;
    };
  }, []);

  return <div>{data}</div>;
}

// ✅ Fixed with AbortController
function BetterComponent() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const controller = new AbortController();

    fetch('/api/data', { signal: controller.signal })
      .then(res => res.json())
      .then(setData)
      .catch(err => {
        if (err.name !== 'AbortError') {
          console.error(err);
        }
      });

    return () => controller.abort();
  }, []);

  return <div>{data}</div>;
}
```

---

## ✅ Tasks

### Task 1: Fetch API Data

Create `src/components/DataFetching/PostsList.tsx`:

```tsx
import { useState, useEffect } from 'react';

interface Post {
  id: number;
  title: string;
  body: string;
  userId: number;
}

interface FetchState {
  posts: Post[];
  loading: boolean;
  error: string | null;
}

export function PostsList() {
  const [state, setState] = useState<FetchState>({
    posts: [],
    loading: true,
    error: null,
  });
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');

  // Fetch posts when page changes
  useEffect(() => {
    const controller = new AbortController();
    
    async function fetchPosts() {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      try {
        const response = await fetch(
          `https://jsonplaceholder.typicode.com/posts?_page=${page}&_limit=10`,
          { signal: controller.signal }
        );
        
        if (!response.ok) {
          throw new Error('Failed to fetch posts');
        }
        
        const data = await response.json();
        setState(prev => ({ ...prev, posts: data, loading: false }));
      } catch (err) {
        if (err instanceof Error && err.name !== 'AbortError') {
          setState(prev => ({ 
            ...prev, 
            error: err.message, 
            loading: false 
          }));
        }
      }
    }

    fetchPosts();

    return () => controller.abort();
  }, [page]);

  // Filter posts based on search
  const filteredPosts = state.posts.filter(post =>
    post.title.toLowerCase().includes(search.toLowerCase())
  );

  if (state.loading) {
    return <div className="loading">Loading posts...</div>;
  }

  if (state.error) {
    return (
      <div className="error">
        <p>Error: {state.error}</p>
        <button onClick={() => setPage(page)}>Retry</button>
      </div>
    );
  }

  return (
    <div className="posts-list">
      <h2>Posts (Page {page})</h2>
      
      <input
        type="text"
        placeholder="Search posts..."
        value={search}
        onChange={e => setSearch(e.target.value)}
        className="search-input"
      />

      <div className="posts">
        {filteredPosts.length === 0 ? (
          <p>No posts found</p>
        ) : (
          filteredPosts.map(post => (
            <article key={post.id} className="post-card">
              <h3>{post.title}</h3>
              <p>{post.body}</p>
            </article>
          ))
        )}
      </div>

      <div className="pagination">
        <button 
          onClick={() => setPage(p => Math.max(1, p - 1))}
          disabled={page === 1}
        >
          Previous
        </button>
        <span>Page {page}</span>
        <button onClick={() => setPage(p => p + 1)}>
          Next
        </button>
      </div>
    </div>
  );
}
```

### Task 2: Add Cleanup Demo

Create `src/components/DataFetching/CleanupDemo.tsx`:

```tsx
import { useState, useEffect } from 'react';

// Timer with cleanup
function Timer() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    console.log('Timer mounted - starting interval');
    
    const intervalId = setInterval(() => {
      setSeconds(s => s + 1);
    }, 1000);
    
    return () => {
      console.log('Timer cleanup - clearing interval');
      clearInterval(intervalId);
    };
  }, []);

  return <div>Timer: {seconds}s</div>;
}

// Window resize listener with cleanup
function WindowSize() {
  const [size, setSize] = useState({
    width: window.innerWidth,
    height: window.innerHeight,
  });

  useEffect(() => {
    console.log('WindowSize mounted - adding listener');
    
    const handleResize = () => {
      setSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);
    
    return () => {
      console.log('WindowSize cleanup - removing listener');
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <div>
      Window: {size.width} x {size.height}
    </div>
  );
}

// Async operation with cleanup
function AsyncFetch({ userId }: { userId: number }) {
  const [user, setUser] = useState<{ name: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log(`Fetching user ${userId}`);
    let isCancelled = false;
    const controller = new AbortController();

    async function fetchUser() {
      setLoading(true);
      
      try {
        // Simulate slow API
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        const res = await fetch(
          `https://jsonplaceholder.typicode.com/users/${userId}`,
          { signal: controller.signal }
        );
        const data = await res.json();
        
        if (!isCancelled) {
          console.log(`Setting user ${userId}:`, data.name);
          setUser(data);
        } else {
          console.log(`Fetch for user ${userId} was cancelled`);
        }
      } catch (err) {
        if (!isCancelled && (err as Error).name !== 'AbortError') {
          console.error('Fetch error:', err);
        }
      } finally {
        if (!isCancelled) {
          setLoading(false);
        }
      }
    }

    fetchUser();

    return () => {
      console.log(`Cleanup for user ${userId}`);
      isCancelled = true;
      controller.abort();
    };
  }, [userId]);

  if (loading) return <div>Loading user {userId}...</div>;
  return <div>User: {user?.name}</div>;
}

// Demo component to toggle children
export function CleanupDemo() {
  const [showTimer, setShowTimer] = useState(true);
  const [showWindowSize, setShowWindowSize] = useState(true);
  const [userId, setUserId] = useState(1);

  return (
    <div className="cleanup-demo">
      <h2>Cleanup Demo (Watch Console)</h2>
      
      <section>
        <h3>Timer (Interval Cleanup)</h3>
        <button onClick={() => setShowTimer(!showTimer)}>
          {showTimer ? 'Unmount Timer' : 'Mount Timer'}
        </button>
        {showTimer && <Timer />}
      </section>

      <section>
        <h3>Window Size (Event Listener Cleanup)</h3>
        <button onClick={() => setShowWindowSize(!showWindowSize)}>
          {showWindowSize ? 'Unmount' : 'Mount'}
        </button>
        {showWindowSize && <WindowSize />}
      </section>

      <section>
        <h3>Async Fetch (AbortController Cleanup)</h3>
        <p>Quickly change user ID to see cancelled requests</p>
        <div className="user-buttons">
          {[1, 2, 3, 4, 5].map(id => (
            <button 
              key={id} 
              onClick={() => setUserId(id)}
              className={userId === id ? 'active' : ''}
            >
              User {id}
            </button>
          ))}
        </div>
        <AsyncFetch userId={userId} />
      </section>
    </div>
  );
}
```

---

## 🎯 Interview Questions & Answers

### Q1: Why does useEffect run twice in StrictMode?
**Answer:** In development mode with StrictMode, React intentionally double-invokes effects to help find bugs:

```tsx
// StrictMode causes:
// 1. Mount → effect runs
// 2. Unmount → cleanup runs
// 3. Mount → effect runs again

// This helps detect:
// - Missing cleanup functions
// - Side effects that aren't idempotent
// - State that depends on mounting once

// Your effect should work correctly even if it runs twice:
useEffect(() => {
  const controller = new AbortController();
  fetch(url, { signal: controller.signal })
    .then(/* ... */);
  
  return () => controller.abort();  // Cleanup handles double-invoke
}, [url]);
```

This only happens in development. Production builds run effects once.

### Q2: Difference between useEffect and useLayoutEffect?
**Answer:**

| useEffect | useLayoutEffect |
|-----------|----------------|
| Runs asynchronously after paint | Runs synchronously before paint |
| Non-blocking | Blocking |
| For most side effects | For DOM measurements/mutations |
| Better performance | Can cause visual delays |

```tsx
// useEffect: runs after browser paints
useEffect(() => {
  // User sees initial render, then effect runs
  // Good for: data fetching, subscriptions, analytics
}, []);

// useLayoutEffect: runs before browser paints
useLayoutEffect(() => {
  // Blocks painting until complete
  // Good for: measuring DOM, synchronous visual updates
  const height = ref.current.getBoundingClientRect().height;
  setHeight(height);  // Update before user sees anything
}, []);

// When to use useLayoutEffect:
// 1. Measuring DOM elements
// 2. Preventing flicker (tooltip positioning)
// 3. Synchronously updating DOM
```

### Q3: How to handle race conditions in useEffect?
**Answer:** Race conditions occur when multiple async operations complete out of order:

```tsx
// ❌ Race condition
useEffect(() => {
  fetch(`/api/users/${id}`)
    .then(res => res.json())
    .then(setUser);  // Old request might complete after new one!
}, [id]);

// ✅ Solution 1: Ignore stale results
useEffect(() => {
  let isStale = false;
  
  fetch(`/api/users/${id}`)
    .then(res => res.json())
    .then(data => {
      if (!isStale) setUser(data);
    });
    
  return () => { isStale = true; };
}, [id]);

// ✅ Solution 2: AbortController (cancels request)
useEffect(() => {
  const controller = new AbortController();
  
  fetch(`/api/users/${id}`, { signal: controller.signal })
    .then(res => res.json())
    .then(setUser);
    
  return () => controller.abort();
}, [id]);

// ✅ Solution 3: Use TanStack Query (best practice)
const { data: user } = useQuery({
  queryKey: ['user', id],
  queryFn: () => fetchUser(id),
});
```

### Q4: What happens if you don't add dependencies?
**Answer:**

```tsx
// No deps array: runs after EVERY render
useEffect(() => {
  console.log('Runs after every render');
  // ⚠️ Can cause performance issues
  // ⚠️ May loop infinitely if setting state
});

// Empty deps: runs once on mount
useEffect(() => {
  console.log('Runs once on mount');
}, []);

// Missing deps: bug - stale closure
function Example({ id }) {
  useEffect(() => {
    fetchData(id);  // ❌ Uses stale id!
  }, []);  // ESLint warns: missing 'id' in deps
}
```

### Q5: How do I run useEffect only on update?
**Answer:**

```tsx
// Using a ref to track first render
function Example({ value }) {
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;  // Skip first render
    }
    
    // This only runs on updates
    console.log('Value updated:', value);
  }, [value]);
}

// Custom hook for update-only effect
function useUpdateEffect(effect: () => void, deps: any[]) {
  const isFirstRender = useRef(true);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    return effect();
  }, deps);
}

// Usage
useUpdateEffect(() => {
  console.log('Only runs on updates');
}, [value]);
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

- [ ] Understand all dependency array patterns
- [ ] Know how to write cleanup functions
- [ ] Can identify and fix infinite loops
- [ ] Know the data fetching pattern
- [ ] Understand memory leak prevention
- [ ] Built posts list with fetch
- [ ] Built cleanup demo
- [ ] Can answer all interview questions

---

**Previous:** [Day 4 - State & Lifecycle](../day-04/README.md)  
**Next:** [Day 6 - Hooks Deep Dive](../day-06/README.md)
