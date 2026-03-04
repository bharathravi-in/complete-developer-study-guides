# 📅 Day 10 – Error Handling

## 🎯 Learning Goals
- Implement Error Boundaries
- Create fallback UIs
- Combine Suspense with Error Boundaries
- Handle async errors

---

## 📚 Theory

### Error Boundaries

```tsx
// Error boundaries are class components that catch JavaScript errors
// in their child component tree during rendering.

import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  // Update state when an error occurs
  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  // Log error information
  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.props.onError?.(error, errorInfo);
    
    // Log to error tracking service
    // logErrorToService(error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-fallback">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
            Try again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary 
      fallback={<ErrorPage />}
      onError={(error) => logToService(error)}
    >
      <MyComponent />
    </ErrorBoundary>
  );
}
```

### Error Boundaries DO NOT catch:

```tsx
// 1. Event handlers
function Button() {
  const handleClick = () => {
    throw new Error('Click error');  // NOT caught by boundary
  };
  return <button onClick={handleClick}>Click</button>;
}

// Solution: try/catch in event handler
function Button() {
  const handleClick = () => {
    try {
      throw new Error('Click error');
    } catch (error) {
      setError(error);  // Handle in component state
    }
  };
  return <button onClick={handleClick}>Click</button>;
}

// 2. Async code
function AsyncComponent() {
  useEffect(() => {
    fetch('/api/data').catch(error => {
      throw error;  // NOT caught by boundary
    });
  }, []);
}

// Solution: Handle async errors with state
function AsyncComponent() {
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetch('/api/data')
      .then(res => res.json())
      .catch(error => setError(error));
  }, []);

  if (error) throw error;  // NOW caught by boundary!
}

// 3. Server-side rendering errors

// 4. Errors in the error boundary itself
```

### Reusable Error Boundary Hook Pattern

```tsx
// Create a hook for throwing errors (triggers error boundary)
function useErrorHandler() {
  const [error, setError] = useState<Error | null>(null);
  
  if (error) {
    throw error;  // Caught by nearest error boundary
  }
  
  const handleError = useCallback((error: Error) => {
    setError(error);
  }, []);
  
  const resetError = useCallback(() => {
    setError(null);
  }, []);
  
  return { handleError, resetError };
}

// Usage
function DataFetcher() {
  const { handleError } = useErrorHandler();
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch('/api/data')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch');
        return res.json();
      })
      .then(setData)
      .catch(handleError);  // Throws to error boundary
  }, [handleError]);

  return <div>{data}</div>;
}
```

### Fallback UI Patterns

```tsx
// 1. Simple message
<ErrorBoundary fallback={<p>Something went wrong</p>}>

// 2. Detailed error with retry
function ErrorFallback({ 
  error, 
  resetErrorBoundary 
}: { 
  error: Error; 
  resetErrorBoundary: () => void;
}) {
  return (
    <div className="error-fallback">
      <h2>Oops! Something went wrong</h2>
      <pre>{error.message}</pre>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

// 3. Different fallbacks for different sections
function App() {
  return (
    <div>
      <ErrorBoundary fallback={<HeaderError />}>
        <Header />
      </ErrorBoundary>
      
      <ErrorBoundary fallback={<SidebarError />}>
        <Sidebar />
      </ErrorBoundary>
      
      <ErrorBoundary fallback={<MainError />}>
        <MainContent />
      </ErrorBoundary>
    </div>
  );
}

// 4. Full page error with navigation
function FullPageError({ error }: { error: Error }) {
  return (
    <div className="error-page">
      <h1>Something went wrong</h1>
      <p>{error.message}</p>
      <div className="actions">
        <button onClick={() => window.location.reload()}>
          Refresh Page
        </button>
        <a href="/">Go Home</a>
        <a href="mailto:support@example.com">Contact Support</a>
      </div>
    </div>
  );
}
```

### Suspense + Error Boundary

```tsx
import { Suspense, lazy } from 'react';

// Combine for loading + error states
const LazyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <ErrorBoundary fallback={<ErrorPage />}>
      <Suspense fallback={<LoadingSpinner />}>
        <LazyComponent />
      </Suspense>
    </ErrorBoundary>
  );
}

// Order matters!
// ErrorBoundary should wrap Suspense to catch lazy loading errors

// Data fetching with both states
function UserProfile({ userId }: { userId: string }) {
  return (
    <ErrorBoundary fallback={<UserErrorFallback />}>
      <Suspense fallback={<UserSkeleton />}>
        <UserData userId={userId} />
      </Suspense>
    </ErrorBoundary>
  );
}

// With react-error-boundary library
import { ErrorBoundary } from 'react-error-boundary';

function App() {
  return (
    <ErrorBoundary
      FallbackComponent={ErrorFallback}
      onReset={() => {
        // Reset app state
      }}
      resetKeys={[userId]}  // Reset when userId changes
    >
      <Suspense fallback={<Loading />}>
        <UserProfile />
      </Suspense>
    </ErrorBoundary>
  );
}
```

### Production Error Handling

```tsx
// Complete error boundary with logging
class ProductionErrorBoundary extends Component<Props, State> {
  state = { hasError: false, error: null, errorId: null };

  static getDerivedStateFromError(error: Error) {
    const errorId = generateErrorId();
    return { hasError: true, error, errorId };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to error tracking service (Sentry, LogRocket, etc.)
    logErrorToService({
      error,
      componentStack: errorInfo.componentStack,
      errorId: this.state.errorId,
      userId: getCurrentUserId(),
      url: window.location.href,
      timestamp: new Date().toISOString(),
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <ErrorFallback
          error={this.state.error}
          errorId={this.state.errorId}
          onRetry={() => this.setState({ hasError: false })}
        />
      );
    }
    return this.props.children;
  }
}

// Helper to generate error IDs
function generateErrorId() {
  return `err_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

// Error logging service
async function logErrorToService(errorData: ErrorLog) {
  try {
    await fetch('/api/log-error', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(errorData),
    });
  } catch (e) {
    console.error('Failed to log error:', e);
  }
}
```

---

## 🎯 Interview Questions & Answers

### Q1: What are Error Boundaries?
**Answer:** Error Boundaries are React class components that catch JavaScript errors in their child component tree, log those errors, and display a fallback UI.

Key methods:
- `static getDerivedStateFromError()`: Update state to render fallback
- `componentDidCatch()`: Log error info, side effects

They catch errors in:
- Render methods
- Lifecycle methods
- Constructors of child components

They do NOT catch:
- Event handlers
- Async code
- SSR errors
- Errors in the boundary itself

### Q2: Why can't we use hooks for Error Boundaries?
**Answer:** Error boundaries require `componentDidCatch` or `getDerivedStateFromError` lifecycle methods, which don't have hook equivalents yet.

The reason is that hooks run during the render phase, and when an error occurs, React needs to interrupt that process in a way that only class lifecycle methods currently support.

Workaround: Use libraries like `react-error-boundary` that provide a clean API:
```tsx
import { ErrorBoundary } from 'react-error-boundary';
<ErrorBoundary FallbackComponent={ErrorFallback}>
```

### Q3: How do you handle async errors with Error Boundaries?
**Answer:** Async errors don't automatically trigger error boundaries. You need to:

1. Catch the error in the async code
2. Update component state with the error
3. Throw during render

```tsx
function AsyncComponent() {
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetchData().catch(setError);
  }, []);
  
  if (error) throw error;  // Now boundary catches it
  
  return <div>Content</div>;
}
```

### Q4: Best practices for Error Boundaries?
**Answer:**
1. **Multiple boundaries** - Isolate failures to specific UI sections
2. **Granular fallbacks** - Different fallbacks for different errors
3. **Error logging** - Send errors to monitoring service
4. **User-friendly messages** - Don't show technical errors
5. **Recovery options** - Provide retry, refresh, or navigation
6. **Reset mechanism** - Allow recovering from errors

---

## 📝 Notes

```
Personal notes space:

_______________________________________________
```

---

## ✅ Completion Checklist

- [ ] Can implement Error Boundaries
- [ ] Know what errors boundaries catch/don't catch
- [ ] Can create fallback UIs
- [ ] Can combine Suspense with Error Boundaries
- [ ] Know how to handle async errors
- [ ] Can answer all interview questions

---

**Previous:** [Day 9 - Performance Optimization](../day-09/README.md)  
**Next:** [Day 11 - Context API](../day-11/README.md)
