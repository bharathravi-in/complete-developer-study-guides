# 📅 Day 22 – Architecture Patterns

## 🎯 Learning Goals
- Master scalable architecture patterns
- Understand feature-based architecture
- Learn clean architecture principles
- Apply SOLID principles to React

---

## 📚 Theory

### Feature-Based Architecture

```
✅ Feature-Based (Recommended)

src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── index.ts
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   └── useLogin.ts
│   │   ├── services/
│   │   │   └── authApi.ts
│   │   ├── store/
│   │   │   └── authSlice.ts
│   │   ├── types/
│   │   │   └── auth.types.ts
│   │   ├── utils/
│   │   │   └── validators.ts
│   │   └── index.ts          # Public API
│   │
│   ├── products/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── index.ts
│   │
│   └── cart/
│       ├── components/
│       ├── hooks/
│       └── index.ts
│
├── shared/
│   ├── components/           # Shared UI components
│   │   ├── Button/
│   │   ├── Input/
│   │   └── Modal/
│   ├── hooks/                # Shared hooks
│   ├── utils/                # Shared utilities
│   └── types/                # Shared types
│
├── app/                      # App-level concerns
│   ├── providers/
│   ├── router/
│   └── store/
│
└── main.tsx

Benefits:
✅ Co-located code (easier to understand)
✅ Clear boundaries between features
✅ Easy to delete/move features
✅ Team ownership clarity
✅ Scales with team size
```

### Clean Architecture in React

```tsx
// Layers: UI → Application → Domain → Infrastructure

// 1. Domain Layer (Business logic - no React)
// src/features/orders/domain/Order.ts
export interface Order {
  id: string;
  items: OrderItem[];
  status: OrderStatus;
  total: number;
  createdAt: Date;
}

export type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered';

export function calculateOrderTotal(items: OrderItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

export function canCancelOrder(order: Order): boolean {
  return order.status === 'pending';
}

// 2. Application Layer (Use cases)
// src/features/orders/application/createOrder.ts
import { Order, calculateOrderTotal } from '../domain/Order';
import { OrderRepository } from '../infrastructure/OrderRepository';

export class CreateOrderUseCase {
  constructor(private orderRepo: OrderRepository) {}

  async execute(items: OrderItem[], userId: string): Promise<Order> {
    const total = calculateOrderTotal(items);
    
    const order: Order = {
      id: crypto.randomUUID(),
      items,
      status: 'pending',
      total,
      createdAt: new Date(),
    };

    await this.orderRepo.save(order);
    return order;
  }
}

// 3. Infrastructure Layer (External services)
// src/features/orders/infrastructure/OrderRepository.ts
import { Order } from '../domain/Order';
import { api } from '@/shared/api';

export interface OrderRepository {
  save(order: Order): Promise<void>;
  findById(id: string): Promise<Order | null>;
  findByUser(userId: string): Promise<Order[]>;
}

export class ApiOrderRepository implements OrderRepository {
  async save(order: Order): Promise<void> {
    await api.post('/orders', order);
  }

  async findById(id: string): Promise<Order | null> {
    const { data } = await api.get(`/orders/${id}`);
    return data;
  }

  async findByUser(userId: string): Promise<Order[]> {
    const { data } = await api.get(`/users/${userId}/orders`);
    return data;
  }
}

// 4. UI Layer (React components)
// src/features/orders/components/CreateOrderButton.tsx
import { useCreateOrder } from '../hooks/useCreateOrder';

export function CreateOrderButton({ items }: { items: OrderItem[] }) {
  const { mutate, isPending } = useCreateOrder();

  return (
    <button onClick={() => mutate(items)} disabled={isPending}>
      {isPending ? 'Creating...' : 'Place Order'}
    </button>
  );
}
```

### SOLID Principles in React

```tsx
// S - Single Responsibility
// ❌ Bad: Component does too much
function UserProfile() {
  // Fetches data, handles auth, renders UI, manages form
}

// ✅ Good: Separated concerns
function UserProfile({ user }: { user: User }) {
  return <div>{user.name}</div>; // Only renders
}

function useUserProfile(id: string) {
  return useQuery(['user', id], () => fetchUser(id)); // Only fetches
}

// O - Open/Closed (extend, don't modify)
// ✅ Extensible via props
interface ButtonProps {
  variant: 'primary' | 'secondary';
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

// L - Liskov Substitution (components can be swapped)
interface InputProps {
  value: string;
  onChange: (value: string) => void;
}

// Any input can be used: TextInput, Select, DatePicker
function Form({ InputComponent }: { InputComponent: React.FC<InputProps> }) {
  const [value, setValue] = useState('');
  return <InputComponent value={value} onChange={setValue} />;
}

// I - Interface Segregation
// ❌ Bad: Too many required props
interface UserCardProps {
  user: User;
  posts: Post[];
  followers: User[];
  settings: Settings;
  analytics: Analytics;
}

// ✅ Good: Minimal interface
interface UserCardProps {
  name: string;
  avatar: string;
}

// D - Dependency Inversion
// ✅ Depend on abstractions (hooks, context)
function OrderList() {
  // Uses hook abstraction, not direct API call
  const { orders } = useOrders();
  return <List items={orders} />;
}
```

### Component Patterns

```tsx
// Compound Components
function Tabs({ children, defaultTab }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      {children}
    </TabsContext.Provider>
  );
}

Tabs.List = function TabList({ children }: { children: React.ReactNode }) {
  return <div role="tablist">{children}</div>;
};

Tabs.Tab = function Tab({ id, children }: TabProps) {
  const { activeTab, setActiveTab } = useTabsContext();
  return (
    <button 
      role="tab" 
      aria-selected={activeTab === id}
      onClick={() => setActiveTab(id)}
    >
      {children}
    </button>
  );
};

Tabs.Panel = function TabPanel({ id, children }: TabPanelProps) {
  const { activeTab } = useTabsContext();
  if (activeTab !== id) return null;
  return <div role="tabpanel">{children}</div>;
};

// Usage
<Tabs defaultTab="profile">
  <Tabs.List>
    <Tabs.Tab id="profile">Profile</Tabs.Tab>
    <Tabs.Tab id="settings">Settings</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel id="profile">Profile content</Tabs.Panel>
  <Tabs.Panel id="settings">Settings content</Tabs.Panel>
</Tabs>

// Render Props
function DataFetcher<T>({ 
  url, 
  children 
}: { 
  url: string; 
  children: (data: T | null, loading: boolean) => React.ReactNode;
}) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(setData)
      .finally(() => setLoading(false));
  }, [url]);

  return <>{children(data, loading)}</>;
}

// HOC (Higher Order Component)
function withAuth<P>(Component: React.ComponentType<P>) {
  return function AuthenticatedComponent(props: P) {
    const { user, loading } = useAuth();
    
    if (loading) return <Loading />;
    if (!user) return <Redirect to="/login" />;
    
    return <Component {...props} />;
  };
}

const ProtectedDashboard = withAuth(Dashboard);
```

---

## ✅ Task: Design Feature Architecture

```tsx
// Design architecture for an e-commerce platform

src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── hooks/
│   │   │   └── useAuth.ts
│   │   ├── context/
│   │   │   └── AuthContext.tsx
│   │   └── index.ts
│   │
│   ├── products/
│   │   ├── components/
│   │   │   ├── ProductCard.tsx
│   │   │   ├── ProductList.tsx
│   │   │   └── ProductDetails.tsx
│   │   ├── hooks/
│   │   │   ├── useProducts.ts
│   │   │   └── useProduct.ts
│   │   ├── services/
│   │   │   └── productsApi.ts
│   │   └── index.ts
│   │
│   ├── cart/
│   │   ├── components/
│   │   │   ├── CartItem.tsx
│   │   │   └── CartSummary.tsx
│   │   ├── hooks/
│   │   │   └── useCart.ts
│   │   ├── store/
│   │   │   └── cartSlice.ts
│   │   └── index.ts
│   │
│   └── checkout/
│       ├── components/
│       ├── hooks/
│       └── index.ts
│
├── shared/
│   ├── components/
│   │   ├── Button/
│   │   ├── Input/
│   │   └── Layout/
│   ├── hooks/
│   │   ├── useDebounce.ts
│   │   └── useLocalStorage.ts
│   └── utils/
│       ├── formatters.ts
│       └── validators.ts
│
└── app/
    ├── App.tsx
    ├── routes.tsx
    └── store.ts
```

---

## 🎯 Interview Questions & Answers

### Q1: Feature-based vs layer-based architecture?
**Answer:** Feature-based groups by functionality (auth, products), layer-based by type (components, hooks). Feature-based scales better with teams, provides clearer boundaries, easier to delete/move features. Prefer feature-based for large apps.

### Q2: How do you share code between features?
**Answer:** Create `shared/` folder for truly shared code (UI components, utilities). Use public API pattern (`index.ts`) to control what's exposed from each feature. Avoid deep imports between features.

### Q3: When to create a new feature vs add to existing?
**Answer:** New feature when: different domain, different team ownership, could be extracted as library, requires different deployment cadence. Add to existing when: closely related functionality, shared data model.

---

## ✅ Completion Checklist

- [ ] Understand feature-based architecture
- [ ] Know clean architecture principles
- [ ] Can apply SOLID to React
- [ ] Master component patterns
- [ ] Designed feature architecture

---

**Previous:** [Day 21 - Micro Frontend](../../week-3-modern/day-21/README.md)  
**Next:** [Day 23 - Performance at Scale](../day-23/README.md)
