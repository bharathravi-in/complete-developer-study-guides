# 📅 Day 13 – Routing

## 🎯 Learning Goals
- Master React Router v6+
- Implement nested routes
- Create protected routes
- Implement lazy routes

---

## 📚 Theory

### React Router v6+ Basics

```tsx
import { 
  BrowserRouter, 
  Routes, 
  Route, 
  Link, 
  NavLink,
  useNavigate,
  useParams,
  useSearchParams,
  useLocation,
  Outlet
} from 'react-router-dom';

// Basic Setup
function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
        <NavLink 
          to="/contact"
          className={({ isActive }) => isActive ? 'active' : ''}
        >
          Contact
        </NavLink>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/contact" element={<Contact />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}

// Hooks
function UserProfile() {
  // URL params: /users/:id
  const { id } = useParams<{ id: string }>();
  
  // Query params: /search?q=react
  const [searchParams, setSearchParams] = useSearchParams();
  const query = searchParams.get('q');
  
  // Programmatic navigation
  const navigate = useNavigate();
  const goBack = () => navigate(-1);
  const goToHome = () => navigate('/');
  const goWithState = () => navigate('/profile', { state: { from: 'home' } });
  
  // Location info
  const location = useLocation();
  // { pathname, search, hash, state, key }
  
  return <div>User {id}</div>;
}
```

### Nested Routes

```tsx
// Parent route with Outlet
function Dashboard() {
  return (
    <div className="dashboard">
      <nav>
        <Link to="overview">Overview</Link>
        <Link to="settings">Settings</Link>
        <Link to="analytics">Analytics</Link>
      </nav>
      
      {/* Child routes render here */}
      <Outlet />
    </div>
  );
}

// Route configuration
function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      
      {/* Nested routes */}
      <Route path="/dashboard" element={<Dashboard />}>
        <Route index element={<DashboardOverview />} />
        <Route path="settings" element={<DashboardSettings />} />
        <Route path="analytics" element={<DashboardAnalytics />} />
      </Route>

      {/* Dynamic nested routes */}
      <Route path="/users" element={<UsersLayout />}>
        <Route index element={<UsersList />} />
        <Route path=":userId" element={<UserProfile />}>
          <Route index element={<UserOverview />} />
          <Route path="posts" element={<UserPosts />} />
          <Route path="settings" element={<UserSettings />} />
        </Route>
      </Route>
    </Routes>
  );
}

// Relative links in nested routes
function UserProfile() {
  return (
    <div>
      {/* These are relative to current route */}
      <Link to="posts">Posts</Link>  {/* /users/:id/posts */}
      <Link to="settings">Settings</Link>  {/* /users/:id/settings */}
      <Link to="..">Back to Users</Link>  {/* /users */}
      <Outlet />
    </div>
  );
}
```

### Protected Routes

```tsx
import { Navigate, useLocation } from 'react-router-dom';

// Auth context
interface AuthContextType {
  user: User | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}

// Protected Route component
function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    // Redirect to login, save intended destination
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}

// Role-based protection
function RequireRole({ 
  children, 
  allowedRoles 
}: { 
  children: ReactNode; 
  allowedRoles: string[] 
}) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
}

// Usage
function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        
        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Role-based routes */}
        <Route
          path="/admin"
          element={
            <RequireRole allowedRoles={['admin']}>
              <AdminPanel />
            </RequireRole>
          }
        />
      </Routes>
    </AuthProvider>
  );
}

// Login with redirect back
function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const from = location.state?.from?.pathname || '/';

  const handleSubmit = async (credentials: Credentials) => {
    await login(credentials);
    navigate(from, { replace: true });
  };

  return <LoginForm onSubmit={handleSubmit} />;
}
```

### Lazy Routes

```tsx
import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';

// Lazy load route components
const Home = lazy(() => import('./pages/Home'));
const About = lazy(() => import('./pages/About'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

// Loading component
function PageLoader() {
  return (
    <div className="page-loader">
      <Spinner />
      <p>Loading...</p>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/dashboard/*" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

// Preload on hover
function Navigation() {
  const preloadDashboard = () => {
    import('./pages/Dashboard');
  };

  return (
    <nav>
      <Link to="/">Home</Link>
      <Link 
        to="/dashboard" 
        onMouseEnter={preloadDashboard}
      >
        Dashboard
      </Link>
    </nav>
  );
}

// Route object configuration with lazy
const routes = [
  {
    path: '/',
    element: <Home />,
  },
  {
    path: '/dashboard',
    element: <Dashboard />,
    children: [
      { index: true, element: <DashboardHome /> },
      { path: 'analytics', element: <Analytics /> },
    ],
  },
];

function App() {
  return useRoutes(routes);
}
```

### Advanced Patterns

```tsx
// Search params management
function ProductList() {
  const [searchParams, setSearchParams] = useSearchParams();
  
  const filters = {
    category: searchParams.get('category') || 'all',
    sort: searchParams.get('sort') || 'newest',
    page: Number(searchParams.get('page')) || 1,
  };

  const updateFilters = (updates: Partial<typeof filters>) => {
    setSearchParams(prev => {
      Object.entries(updates).forEach(([key, value]) => {
        if (value) {
          prev.set(key, String(value));
        } else {
          prev.delete(key);
        }
      });
      return prev;
    });
  };

  return (
    <div>
      <select 
        value={filters.category}
        onChange={e => updateFilters({ category: e.target.value })}
      >
        <option value="all">All</option>
        <option value="electronics">Electronics</option>
      </select>
      
      <Pagination
        page={filters.page}
        onPageChange={page => updateFilters({ page })}
      />
    </div>
  );
}

// Route loaders (React Router 6.4+)
import { createBrowserRouter, RouterProvider } from 'react-router-dom';

const router = createBrowserRouter([
  {
    path: '/users/:id',
    element: <UserProfile />,
    loader: async ({ params }) => {
      const response = await fetch(`/api/users/${params.id}`);
      return response.json();
    },
    errorElement: <ErrorPage />,
  },
]);

function UserProfile() {
  const user = useLoaderData();  // Data from loader
  return <div>{user.name}</div>;
}

function App() {
  return <RouterProvider router={router} />;
}
```

---

## 🎯 Interview Questions & Answers

### Q1: How does React Router work?
**Answer:** React Router uses the browser's History API to manage navigation without page reloads. It:

1. Listens for URL changes
2. Matches current URL against route patterns
3. Renders matching route's component
4. Provides navigation utilities (Link, navigate)

### Q2: What's new in React Router v6?
**Answer:**
- `Routes` instead of `Switch`
- `element` prop instead of `component`
- Relative routes and links
- No exact prop needed
- `useNavigate` instead of `useHistory`
- `Outlet` for nested routes
- Route configuration objects
- Built-in data loading (v6.4+)

### Q3: Protected routes pattern?
**Answer:**
```tsx
function ProtectedRoute({ children }) {
  const { user } = useAuth();
  const location = useLocation();
  
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  return children;
}
```

---

## ✅ Completion Checklist

- [ ] Master React Router v6 basics
- [ ] Implement nested routes with Outlet
- [ ] Create protected routes
- [ ] Implement lazy loading routes
- [ ] Can answer all interview questions

---

**Previous:** [Day 12 - State Management](../day-12/README.md)  
**Next:** [Day 14 - Testing](../day-14/README.md)
