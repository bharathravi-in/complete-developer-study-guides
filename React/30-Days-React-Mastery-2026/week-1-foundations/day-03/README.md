# 📅 Day 3 – Components Deep Dive

## 🎯 Learning Goals
- Master Functional Components
- Understand Props deeply
- Identify and solve Props Drilling
- Learn Component Composition patterns
- Use Default Props effectively
- Master Children pattern

---

## 📚 Theory

### Functional Components

```tsx
// Basic Functional Component
function Greeting({ name }: { name: string }) {
  return <h1>Hello, {name}!</h1>;
}

// Arrow Function Component
const Greeting = ({ name }: { name: string }) => {
  return <h1>Hello, {name}!</h1>;
};

// With implicit return
const Greeting = ({ name }: { name: string }) => <h1>Hello, {name}!</h1>;

// Component with multiple props
interface UserCardProps {
  name: string;
  email: string;
  avatar?: string;
  isOnline?: boolean;
}

function UserCard({ name, email, avatar, isOnline = false }: UserCardProps) {
  return (
    <div className="user-card">
      {avatar && <img src={avatar} alt={name} />}
      <h3>{name}</h3>
      <p>{email}</p>
      {isOnline && <span className="status online">Online</span>}
    </div>
  );
}
```

### Props Deep Dive

```tsx
// Props are read-only - NEVER mutate!
function BadComponent({ user }: { user: User }) {
  user.name = 'Modified';  // ❌ NEVER do this!
  return <div>{user.name}</div>;
}

// Destructuring with renaming
interface Props {
  item: { id: string; name: string };
  onClick: (id: string) => void;
}

function ListItem({ item: { id, name }, onClick: handleClick }: Props) {
  return <li onClick={() => handleClick(id)}>{name}</li>;
}

// Rest props pattern
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
  isLoading?: boolean;
}

function Button({ variant = 'primary', isLoading, children, ...rest }: ButtonProps) {
  return (
    <button 
      className={`btn btn-${variant}`} 
      disabled={isLoading}
      {...rest}
    >
      {isLoading ? 'Loading...' : children}
    </button>
  );
}

// Usage - all native button props work
<Button onClick={handleClick} type="submit" variant="primary">Submit</Button>
```

### Props Drilling Problem

```tsx
// ❌ Props Drilling - passing props through many layers
function App() {
  const [user, setUser] = useState({ name: 'John' });
  return <Layout user={user} />;
}

function Layout({ user }: { user: User }) {
  return (
    <div>
      <Header user={user} />  {/* Header doesn't use user */}
      <Main user={user} />
    </div>
  );
}

function Header({ user }: { user: User }) {
  return (
    <header>
      <Nav user={user} />  {/* Nav doesn't use user */}
    </header>
  );
}

function Nav({ user }: { user: User }) {
  return (
    <nav>
      <UserMenu user={user} />  {/* Finally used here! */}
    </nav>
  );
}

// Solutions to Props Drilling:
// 1. Component Composition (below)
// 2. Context API (Day 11)
// 3. State Management (Day 12)
```

### Component Composition

```tsx
// ✅ Solution 1: Composition - pass components as props
function App() {
  const [user, setUser] = useState({ name: 'John' });
  
  return (
    <Layout
      header={<Header userMenu={<UserMenu user={user} />} />}
      content={<Main />}
    />
  );
}

function Layout({ header, content }: { header: ReactNode; content: ReactNode }) {
  return (
    <div>
      {header}
      {content}
    </div>
  );
}

function Header({ userMenu }: { userMenu: ReactNode }) {
  return (
    <header>
      <nav>{userMenu}</nav>
    </header>
  );
}

// ✅ Solution 2: Children pattern
function Card({ children }: { children: ReactNode }) {
  return <div className="card">{children}</div>;
}

function App() {
  return (
    <Card>
      <h2>Title</h2>
      <p>Content goes here</p>
    </Card>
  );
}

// ✅ Solution 3: Compound Components
function Tabs({ children, defaultTab }: { children: ReactNode; defaultTab: string }) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tabs">{children}</div>
    </TabsContext.Provider>
  );
}

Tabs.List = function TabsList({ children }: { children: ReactNode }) {
  return <div className="tabs-list">{children}</div>;
};

Tabs.Tab = function Tab({ id, children }: { id: string; children: ReactNode }) {
  const { activeTab, setActiveTab } = useContext(TabsContext);
  return (
    <button 
      className={activeTab === id ? 'active' : ''} 
      onClick={() => setActiveTab(id)}
    >
      {children}
    </button>
  );
};

Tabs.Panel = function TabsPanel({ id, children }: { id: string; children: ReactNode }) {
  const { activeTab } = useContext(TabsContext);
  if (activeTab !== id) return null;
  return <div className="tabs-panel">{children}</div>;
};

// Usage
<Tabs defaultTab="tab1">
  <Tabs.List>
    <Tabs.Tab id="tab1">Tab 1</Tabs.Tab>
    <Tabs.Tab id="tab2">Tab 2</Tabs.Tab>
  </Tabs.List>
  <Tabs.Panel id="tab1">Content 1</Tabs.Panel>
  <Tabs.Panel id="tab2">Content 2</Tabs.Panel>
</Tabs>
```

### Default Props

```tsx
// Method 1: Default parameters (recommended)
interface GreetingProps {
  name?: string;
  greeting?: string;
}

function Greeting({ name = 'Guest', greeting = 'Hello' }: GreetingProps) {
  return <h1>{greeting}, {name}!</h1>;
}

// Method 2: Default values with destructuring
function Button({ 
  variant = 'primary', 
  size = 'medium',
  disabled = false,
  children 
}: ButtonProps) {
  return <button className={`btn-${variant} btn-${size}`}>{children}</button>;
}

// Method 3: Satisfies pattern for complex defaults
const defaultConfig = {
  theme: 'light',
  language: 'en',
  notifications: true,
} satisfies Partial<Config>;

function Settings({ config = defaultConfig }: { config?: Config }) {
  const finalConfig = { ...defaultConfig, ...config };
  // ...
}
```

### Children Pattern

```tsx
import { ReactNode, Children, isValidElement, cloneElement } from 'react';

// Basic children usage
interface CardProps {
  children: ReactNode;
}

function Card({ children }: CardProps) {
  return <div className="card">{children}</div>;
}

// Children with specific types
interface ListProps {
  children: ReactNode;  // ReactNode accepts anything renderable
}

// Render props pattern (children as function)
interface MouseTrackerProps {
  children: (position: { x: number; y: number }) => ReactNode;
}

function MouseTracker({ children }: MouseTrackerProps) {
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent) => {
    setPosition({ x: e.clientX, y: e.clientY });
  };

  return (
    <div onMouseMove={handleMouseMove} style={{ height: '100vh' }}>
      {children(position)}
    </div>
  );
}

// Usage
<MouseTracker>
  {({ x, y }) => <p>Mouse position: {x}, {y}</p>}
</MouseTracker>

// Manipulating children
function List({ children }: { children: ReactNode }) {
  return (
    <ul>
      {Children.map(children, (child, index) => {
        if (isValidElement(child)) {
          return cloneElement(child, { index });
        }
        return child;
      })}
    </ul>
  );
}

// Multiple children slots
interface LayoutProps {
  header: ReactNode;
  sidebar: ReactNode;
  children: ReactNode;  // Main content
  footer?: ReactNode;
}

function Layout({ header, sidebar, children, footer }: LayoutProps) {
  return (
    <div className="layout">
      <header>{header}</header>
      <aside>{sidebar}</aside>
      <main>{children}</main>
      {footer && <footer>{footer}</footer>}
    </div>
  );
}
```

---

## ✅ Tasks

### Task 1: Reusable Card Component

Create `src/components/Card/Card.tsx`:

```tsx
import { ReactNode } from 'react';
import './Card.css';

interface CardProps {
  children: ReactNode;
  variant?: 'default' | 'outlined' | 'elevated';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  className?: string;
}

interface CardHeaderProps {
  children: ReactNode;
  action?: ReactNode;
}

interface CardBodyProps {
  children: ReactNode;
}

interface CardFooterProps {
  children: ReactNode;
  align?: 'left' | 'center' | 'right';
}

export function Card({ 
  children, 
  variant = 'default', 
  padding = 'md',
  className = ''
}: CardProps) {
  return (
    <div className={`card card-${variant} card-padding-${padding} ${className}`}>
      {children}
    </div>
  );
}

Card.Header = function CardHeader({ children, action }: CardHeaderProps) {
  return (
    <div className="card-header">
      <div className="card-header-content">{children}</div>
      {action && <div className="card-header-action">{action}</div>}
    </div>
  );
};

Card.Body = function CardBody({ children }: CardBodyProps) {
  return <div className="card-body">{children}</div>;
};

Card.Footer = function CardFooter({ children, align = 'right' }: CardFooterProps) {
  return (
    <div className={`card-footer card-footer-${align}`}>
      {children}
    </div>
  );
};

// Usage example
export function CardDemo() {
  return (
    <div className="card-demo">
      <Card variant="elevated">
        <Card.Header action={<button>...</button>}>
          <h3>Card Title</h3>
        </Card.Header>
        <Card.Body>
          <p>This is the card content. It can contain any React elements.</p>
        </Card.Body>
        <Card.Footer>
          <button>Cancel</button>
          <button>Save</button>
        </Card.Footer>
      </Card>
    </div>
  );
}
```

Create `src/components/Card/Card.css`:

```css
.card {
  border-radius: 8px;
  background: white;
}

.card-default {
  border: 1px solid #e0e0e0;
}

.card-outlined {
  border: 2px solid #1976d2;
}

.card-elevated {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.card-padding-none { padding: 0; }
.card-padding-sm { padding: 8px; }
.card-padding-md { padding: 16px; }
.card-padding-lg { padding: 24px; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid #e0e0e0;
  margin-bottom: 12px;
}

.card-body {
  flex: 1;
}

.card-footer {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #e0e0e0;
  margin-top: 12px;
}

.card-footer-left { justify-content: flex-start; }
.card-footer-center { justify-content: center; }
.card-footer-right { justify-content: flex-end; }
```

### Task 2: Layout Wrapper Component

Create `src/components/Layout/Layout.tsx`:

```tsx
import { ReactNode } from 'react';
import './Layout.css';

interface LayoutProps {
  children: ReactNode;
}

interface PageLayoutProps {
  header?: ReactNode;
  sidebar?: ReactNode;
  children: ReactNode;
  footer?: ReactNode;
  sidebarPosition?: 'left' | 'right';
}

// Simple wrapper
export function Container({ children }: LayoutProps) {
  return <div className="container">{children}</div>;
}

// Flex layouts
export function Stack({ 
  children, 
  gap = 16, 
  direction = 'column' 
}: LayoutProps & { gap?: number; direction?: 'row' | 'column' }) {
  return (
    <div 
      className="stack" 
      style={{ 
        flexDirection: direction, 
        gap: `${gap}px` 
      }}
    >
      {children}
    </div>
  );
}

// Grid layout
export function Grid({ 
  children, 
  columns = 3, 
  gap = 16 
}: LayoutProps & { columns?: number; gap?: number }) {
  return (
    <div 
      className="grid" 
      style={{ 
        gridTemplateColumns: `repeat(${columns}, 1fr)`,
        gap: `${gap}px`
      }}
    >
      {children}
    </div>
  );
}

// Full page layout
export function PageLayout({ 
  header, 
  sidebar, 
  children, 
  footer,
  sidebarPosition = 'left'
}: PageLayoutProps) {
  return (
    <div className="page-layout">
      {header && <header className="page-header">{header}</header>}
      
      <div className={`page-content sidebar-${sidebarPosition}`}>
        {sidebar && <aside className="page-sidebar">{sidebar}</aside>}
        <main className="page-main">{children}</main>
      </div>
      
      {footer && <footer className="page-footer">{footer}</footer>}
    </div>
  );
}

// Usage Demo
export function LayoutDemo() {
  return (
    <PageLayout
      header={<nav>Header Navigation</nav>}
      sidebar={
        <ul>
          <li>Dashboard</li>
          <li>Settings</li>
        </ul>
      }
      footer={<p>© 2026 My App</p>}
    >
      <Container>
        <Stack gap={24}>
          <h1>Welcome</h1>
          <Grid columns={3} gap={16}>
            <div>Card 1</div>
            <div>Card 2</div>
            <div>Card 3</div>
          </Grid>
        </Stack>
      </Container>
    </PageLayout>
  );
}
```

---

## 🎯 Interview Questions & Answers

### Q1: Props vs State?
**Answer:**

| Props | State |
|-------|-------|
| Passed from parent | Managed within component |
| Read-only (immutable) | Can be updated with setter |
| Used for configuration | Used for dynamic data |
| Changes cause re-render | Changes cause re-render |
| Controlled by parent | Controlled by component |

```tsx
// Props: data passed in
function Button({ label, onClick }: { label: string; onClick: () => void }) {
  return <button onClick={onClick}>{label}</button>;
}

// State: internal data
function Counter() {
  const [count, setCount] = useState(0);  // Internal state
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

### Q2: What is component composition?
**Answer:** Component composition is the pattern of building complex UIs by combining simpler components. Instead of inheritance, React uses composition.

**Benefits:**
- Avoids prop drilling
- More flexible than inheritance
- Easier to understand and test
- Components remain independent

**Patterns:**
1. **Containment:** Using `children` prop
2. **Specialization:** Generic components with specific props
3. **Compound Components:** Related components share implicit state

```tsx
// Containment
<Card>
  <UserProfile />
</Card>

// Specialization
<Dialog type="alert" title="Warning" />
<Dialog type="confirm" title="Confirm Action" />

// Compound Components
<Select>
  <Select.Option value="1">Option 1</Select.Option>
  <Select.Option value="2">Option 2</Select.Option>
</Select>
```

### Q3: When to use children vs props?
**Answer:**

**Use children when:**
- Content is arbitrary/flexible
- Building wrapper/container components
- Content structure varies by usage

**Use props when:**
- Data has specific structure
- Need type safety
- Multiple named slots needed

```tsx
// Children: flexible content
<Card>{anyContent}</Card>

// Props: structured data
<UserCard user={user} />

// Both: hybrid approach
<Modal title="Confirm" footer={<Button>OK</Button>}>
  {content}
</Modal>
```

### Q4: How to avoid prop drilling?
**Answer:**

1. **Component Composition:** Pass components, not data
2. **Context API:** Share data without passing props
3. **State Management:** Redux, Zustand for global state
4. **Custom Hooks:** Encapsulate shared logic

```tsx
// Before: prop drilling
<App user={user}>
  <Layout user={user}>
    <Header user={user}>
      <UserMenu user={user} />

// After: composition
<App>
  <Layout header={<Header userMenu={<UserMenu user={user} />} />}>
```

### Q5: What is render props pattern?
**Answer:** A technique where a component receives a function as prop that returns React elements.

```tsx
// Render prop via children
<Mouse>
  {({ x, y }) => <Cursor x={x} y={y} />}
</Mouse>

// Render prop via named prop
<Mouse render={({ x, y }) => <Cursor x={x} y={y} />} />

// Implementation
function Mouse({ children }: { children: (pos: Position) => ReactNode }) {
  const [pos, setPos] = useState({ x: 0, y: 0 });
  // ... tracking logic
  return <div>{children(pos)}</div>;
}
```

**Modern alternative:** Custom hooks often replace render props.

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

- [ ] Understand functional component patterns
- [ ] Know how to properly type and use props
- [ ] Can identify prop drilling issues
- [ ] Understand component composition patterns
- [ ] Know different ways to set default props
- [ ] Master children pattern and its variations
- [ ] Built reusable Card component
- [ ] Built Layout wrapper components
- [ ] Can answer all interview questions

---

**Previous:** [Day 2 - JSX & Rendering](../day-02/README.md)  
**Next:** [Day 4 - State & Lifecycle](../day-04/README.md)
