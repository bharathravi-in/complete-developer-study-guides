# 📅 Day 21 – Micro Frontend

## 🎯 Learning Goals
- Understand Micro Frontend architecture
- Learn Module Federation
- Implement independent deployments
- Share state across micro frontends

---

## 📚 Theory

### Micro Frontend Concepts

```
🏗️ Micro Frontend Architecture

Traditional Monolith:
┌──────────────────────────────────────────┐
│              Single React App            │
│  ┌────────┐ ┌────────┐ ┌────────┐       │
│  │  Auth  │ │  Shop  │ │ Admin  │       │
│  └────────┘ └────────┘ └────────┘       │
└──────────────────────────────────────────┘

Micro Frontends:
┌─────────────────────────────────────────────────────┐
│                   Container/Shell                    │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐       │
│  │  Auth MFE │  │  Shop MFE │  │ Admin MFE │       │
│  │  (React)  │  │  (React)  │  │   (Vue)   │       │
│  │ Team Auth │  │ Team Shop │  │Team Admin │       │
│  └───────────┘  └───────────┘  └───────────┘       │
└─────────────────────────────────────────────────────┘
     ↓               ↓               ↓
   Deploy         Deploy          Deploy
 Independently  Independently  Independently

Benefits:
✅ Independent deployments
✅ Team autonomy  
✅ Technology flexibility
✅ Isolated failures
✅ Scalable teams

Challenges:
⚠️ Shared dependencies
⚠️ Consistent UX
⚠️ Communication complexity
⚠️ Performance overhead
```

### Module Federation (Webpack 5)

```tsx
// Host/Container - webpack.config.js
const ModuleFederationPlugin = require('webpack/lib/container/ModuleFederationPlugin');

module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'host',
      remotes: {
        // Remote apps to consume
        auth: 'auth@http://localhost:3001/remoteEntry.js',
        shop: 'shop@http://localhost:3002/remoteEntry.js',
        admin: 'admin@http://localhost:3003/remoteEntry.js',
      },
      shared: {
        react: { singleton: true, eager: true },
        'react-dom': { singleton: true, eager: true },
        'react-router-dom': { singleton: true },
      },
    }),
  ],
};

// Remote App (Auth) - webpack.config.js
module.exports = {
  plugins: [
    new ModuleFederationPlugin({
      name: 'auth',
      filename: 'remoteEntry.js',
      exposes: {
        './LoginForm': './src/components/LoginForm',
        './AuthProvider': './src/context/AuthProvider',
        './useAuth': './src/hooks/useAuth',
      },
      shared: {
        react: { singleton: true },
        'react-dom': { singleton: true },
      },
    }),
  ],
};

// Host app consuming remote
// src/App.tsx
import React, { Suspense, lazy } from 'react';

// Dynamic imports from remotes
const AuthLoginForm = lazy(() => import('auth/LoginForm'));
const ShopCatalog = lazy(() => import('shop/Catalog'));
const AdminDashboard = lazy(() => import('admin/Dashboard'));

function App() {
  return (
    <div>
      <nav>Navigation Shell</nav>
      
      <Suspense fallback={<div>Loading Auth...</div>}>
        <AuthLoginForm onSuccess={() => console.log('Logged in')} />
      </Suspense>
      
      <Suspense fallback={<div>Loading Shop...</div>}>
        <ShopCatalog />
      </Suspense>
    </div>
  );
}
```

### Vite Module Federation

```tsx
// vite.config.ts (Host)
import { defineConfig } from 'vite';
import federation from '@originjs/vite-plugin-federation';

export default defineConfig({
  plugins: [
    federation({
      name: 'host',
      remotes: {
        auth: 'http://localhost:3001/assets/remoteEntry.js',
        shop: 'http://localhost:3002/assets/remoteEntry.js',
      },
      shared: ['react', 'react-dom'],
    }),
  ],
  build: {
    target: 'esnext',
  },
});

// vite.config.ts (Auth Remote)
export default defineConfig({
  plugins: [
    federation({
      name: 'auth',
      filename: 'remoteEntry.js',
      exposes: {
        './LoginForm': './src/components/LoginForm.tsx',
        './useAuth': './src/hooks/useAuth.ts',
      },
      shared: ['react', 'react-dom'],
    }),
  ],
  build: {
    target: 'esnext',
  },
});
```

### Communication Patterns

```tsx
// 1. Props drilling (simplest)
// Host passes callbacks to remotes
<ShopCart
  user={user}
  onCheckout={(items) => handleCheckout(items)}
/>

// 2. Custom Events (decoupled)
// Remote dispatches events
// shop/src/components/Cart.tsx
function Cart() {
  const checkout = () => {
    const event = new CustomEvent('shop:checkout', {
      detail: { items: cartItems, total: 99.99 },
    });
    window.dispatchEvent(event);
  };
  
  return <button onClick={checkout}>Checkout</button>;
}

// Host listens to events
// host/src/App.tsx
useEffect(() => {
  const handleCheckout = (e: CustomEvent) => {
    console.log('Checkout:', e.detail);
  };
  
  window.addEventListener('shop:checkout', handleCheckout);
  return () => window.removeEventListener('shop:checkout', handleCheckout);
}, []);

// 3. Shared State (Zustand, Redux)
// shared/store.ts
import { create } from 'zustand';

interface SharedState {
  user: User | null;
  setUser: (user: User | null) => void;
  cart: CartItem[];
  addToCart: (item: CartItem) => void;
}

export const useSharedStore = create<SharedState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  cart: [],
  addToCart: (item) => set((state) => ({ cart: [...state.cart, item] })),
}));

// Expose from one remote, consume in others
// webpack config: shared: { './store': { singleton: true } }

// 4. Event Bus (pub/sub)
// shared/eventBus.ts
type EventCallback = (data: any) => void;

class EventBus {
  private events: Map<string, EventCallback[]> = new Map();
  
  on(event: string, callback: EventCallback) {
    if (!this.events.has(event)) {
      this.events.set(event, []);
    }
    this.events.get(event)!.push(callback);
  }
  
  off(event: string, callback: EventCallback) {
    const callbacks = this.events.get(event);
    if (callbacks) {
      this.events.set(event, callbacks.filter(cb => cb !== callback));
    }
  }
  
  emit(event: string, data?: any) {
    this.events.get(event)?.forEach(cb => cb(data));
  }
}

export const eventBus = new EventBus();

// Usage
eventBus.emit('user:login', { userId: '123' });
eventBus.on('user:login', (data) => console.log('User logged in:', data));
```

### Routing in Micro Frontends

```tsx
// Host routing
// host/src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

const AuthRoutes = lazy(() => import('auth/Routes'));
const ShopRoutes = lazy(() => import('shop/Routes'));
const AdminRoutes = lazy(() => import('admin/Routes'));

function App() {
  return (
    <BrowserRouter>
      <Shell>
        <Suspense fallback={<Loading />}>
          <Routes>
            <Route path="/auth/*" element={<AuthRoutes />} />
            <Route path="/shop/*" element={<ShopRoutes />} />
            <Route path="/admin/*" element={<AdminRoutes />} />
            <Route path="/" element={<Home />} />
          </Routes>
        </Suspense>
      </Shell>
    </BrowserRouter>
  );
}

// Remote routes (use relative paths)
// auth/src/Routes.tsx
import { Routes, Route } from 'react-router-dom';

export default function AuthRoutes() {
  return (
    <Routes>
      <Route path="login" element={<Login />} />
      <Route path="register" element={<Register />} />
      <Route path="forgot-password" element={<ForgotPassword />} />
    </Routes>
  );
}
```

### Shared UI Library

```tsx
// shared-ui package (published to npm or internal registry)
// packages/shared-ui/src/Button.tsx

export interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

export function Button({ variant, size = 'md', children, ...props }: ButtonProps) {
  return (
    <button className={`btn btn-${variant} btn-${size}`} {...props}>
      {children}
    </button>
  );
}

// Each MFE imports from shared-ui
import { Button, Input, Modal } from '@company/shared-ui';

// Version management
// Ensure all MFEs use compatible versions
// package.json
{
  "dependencies": {
    "@company/shared-ui": "^2.0.0"
  }
}
```

---

## ✅ Task: Build Micro Frontend App

```
micro-fe-demo/
├── host-shell/           # Container app
│   ├── src/
│   │   ├── App.tsx       # Main routing
│   │   └── Shell.tsx     # Layout shell
│   └── vite.config.ts
│
├── auth-mfe/             # Auth micro frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   └── RegisterForm.tsx
│   │   └── Routes.tsx
│   └── vite.config.ts
│
├── shop-mfe/             # Shop micro frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── ProductList.tsx
│   │   │   └── Cart.tsx
│   │   └── Routes.tsx
│   └── vite.config.ts
│
└── shared/               # Shared packages
    ├── ui/               # Shared components
    ├── store/            # Shared state
    └── utils/            # Shared utilities
```

---

## 🎯 Interview Questions & Answers

### Q1: When to use Micro Frontends?
**Answer:** Large teams (5+), multiple products/domains, need for independent deployments, legacy modernization. NOT for small teams or simple apps - adds complexity without benefit.

### Q2: How do you handle shared dependencies?
**Answer:** Module Federation's `shared` config with `singleton: true` ensures one version loads. Use semantic versioning. Share critical deps (React) as singletons, allow others to load multiple versions if needed.

### Q3: What are the performance concerns?
**Answer:** Multiple bundle downloads, extra runtime overhead, potential duplicate dependencies. Mitigate with: shared deps, lazy loading, proper caching, tree-shaking, server-side composition.

---

## ✅ Completion Checklist

- [ ] Understand Micro Frontend architecture
- [ ] Can configure Module Federation
- [ ] Know communication patterns
- [ ] Handle shared routing
- [ ] Built MFE application

---

**Previous:** [Day 20 - Authentication](../day-20/README.md)  
**Next:** [Week 4 - Day 22 - Architecture](../../week-4-senior/day-22/README.md)

---

## 🎉 Week 3 Complete!

You've mastered Modern React 2026:
- TypeScript integration
- Forms & validation
- API layer patterns
- React Server Components
- Next.js App Router
- Authentication & Security
- Micro Frontend architecture

**Next week:** Senior Level & Interview Mastery!
