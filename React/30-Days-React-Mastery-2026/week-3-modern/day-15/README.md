# 📅 Day 15 – TypeScript with React

## 🎯 Learning Goals
- Master TypeScript fundamentals for React
- Type components, props, and state
- Understand generics in React
- Handle events and refs with types

---

## 📚 Theory

### TypeScript Fundamentals for React

```tsx
// Basic types
let name: string = 'John';
let age: number = 30;
let isActive: boolean = true;
let items: string[] = ['a', 'b'];
let tuple: [string, number] = ['hello', 42];

// Object types
interface User {
  id: number;
  name: string;
  email?: string;        // Optional
  readonly createdAt: Date; // Immutable
}

// Union types
type Status = 'pending' | 'success' | 'error';
type ID = string | number;

// Intersection types
type AdminUser = User & { role: 'admin'; permissions: string[] };

// Type assertions
const input = document.getElementById('input') as HTMLInputElement;

// Generics
function identity<T>(arg: T): T {
  return arg;
}

// Utility types
Partial<User>       // All properties optional
Required<User>      // All properties required
Pick<User, 'id' | 'name'>  // Pick specific properties
Omit<User, 'email'>        // Omit specific properties
Record<string, number>     // Key-value object
ReturnType<typeof fn>      // Return type of function
```

### Typing React Components

```tsx
// Function component with props
interface ButtonProps {
  label: string;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
  onClick: () => void;
}

const Button: React.FC<ButtonProps> = ({ label, variant = 'primary', disabled, onClick }) => (
  <button 
    className={variant} 
    disabled={disabled} 
    onClick={onClick}
  >
    {label}
  </button>
);

// Better: Explicit return type (no React.FC)
function Button({ label, variant = 'primary', disabled, onClick }: ButtonProps): JSX.Element {
  return (
    <button className={variant} disabled={disabled} onClick={onClick}>
      {label}
    </button>
  );
}

// With children
interface CardProps {
  children: React.ReactNode;
  title: string;
}

function Card({ children, title }: CardProps) {
  return (
    <div className="card">
      <h2>{title}</h2>
      {children}
    </div>
  );
}

// Props with HTML attributes
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

function Input({ label, error, ...inputProps }: InputProps) {
  return (
    <div>
      <label>{label}</label>
      <input {...inputProps} />
      {error && <span className="error">{error}</span>}
    </div>
  );
}

// Generic components
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function List<T>({ items, renderItem }: ListProps<T>) {
  return <ul>{items.map(renderItem)}</ul>;
}

// Usage
<List<User> 
  items={users} 
  renderItem={(user) => <li key={user.id}>{user.name}</li>} 
/>
```

### Typing Hooks

```tsx
// useState
const [count, setCount] = useState<number>(0);
const [user, setUser] = useState<User | null>(null);

// Type is inferred when initial value is provided
const [name, setName] = useState(''); // string inferred

// useReducer
interface State {
  count: number;
  error: string | null;
}

type Action = 
  | { type: 'increment' }
  | { type: 'decrement' }
  | { type: 'set'; payload: number }
  | { type: 'error'; payload: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'increment':
      return { ...state, count: state.count + 1 };
    case 'decrement':
      return { ...state, count: state.count - 1 };
    case 'set':
      return { ...state, count: action.payload };
    case 'error':
      return { ...state, error: action.payload };
    default:
      return state;
  }
}

const [state, dispatch] = useReducer(reducer, { count: 0, error: null });

// useRef
const inputRef = useRef<HTMLInputElement>(null);
const countRef = useRef<number>(0); // Mutable ref

// useContext
interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

// Custom hooks
function useLocalStorage<T>(key: string, initialValue: T): [T, (value: T) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : initialValue;
  });

  const setValue = (value: T) => {
    setStoredValue(value);
    localStorage.setItem(key, JSON.stringify(value));
  };

  return [storedValue, setValue];
}
```

### Event Handling

```tsx
// Common event types
function EventExamples() {
  // Mouse events
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    console.log(e.currentTarget.name);
  };

  // Change events
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);
  };

  // Form events
  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Handle form
  };

  // Keyboard events
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      // Handle enter
    }
  };

  // Focus events
  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    console.log(e.target.value);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input onChange={handleChange} onKeyDown={handleKeyDown} onFocus={handleFocus} />
      <button onClick={handleClick}>Submit</button>
    </form>
  );
}

// Event handler types
type ClickHandler = React.MouseEventHandler<HTMLButtonElement>;
type ChangeHandler = React.ChangeEventHandler<HTMLInputElement>;
```

### Advanced Patterns

```tsx
// Discriminated unions for props
interface TextButtonProps {
  variant: 'text';
  onClick: () => void;
}

interface IconButtonProps {
  variant: 'icon';
  icon: React.ReactNode;
  onClick: () => void;
}

type ButtonVariantProps = TextButtonProps | IconButtonProps;

function Button(props: ButtonVariantProps) {
  if (props.variant === 'icon') {
    return <button>{props.icon}</button>;
  }
  return <button>Click me</button>;
}

// Polymorphic components
type AsProp<C extends React.ElementType> = {
  as?: C;
};

type PropsWithAs<C extends React.ElementType, Props = {}> = 
  AsProp<C> & 
  Props & 
  Omit<React.ComponentPropsWithoutRef<C>, keyof Props>;

interface BoxOwnProps {
  color?: string;
}

type BoxProps<C extends React.ElementType = 'div'> = PropsWithAs<C, BoxOwnProps>;

function Box<C extends React.ElementType = 'div'>({
  as,
  color,
  ...props
}: BoxProps<C>) {
  const Component = as || 'div';
  return <Component style={{ color }} {...props} />;
}

// Usage
<Box as="span" color="red">Text</Box>
<Box as="a" href="/home">Link</Box>

// forwardRef with types
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, ...props }, ref) => (
    <div>
      <label>{label}</label>
      <input ref={ref} {...props} />
    </div>
  )
);
```

---

## ✅ Task: Fully Typed Component

```tsx
// types/index.ts
export interface Todo {
  id: string;
  text: string;
  completed: boolean;
  createdAt: Date;
  priority: 'low' | 'medium' | 'high';
}

export type TodoFilter = 'all' | 'active' | 'completed';

// hooks/useTodos.ts
interface UseTodosReturn {
  todos: Todo[];
  addTodo: (text: string, priority: Todo['priority']) => void;
  toggleTodo: (id: string) => void;
  deleteTodo: (id: string) => void;
  filteredTodos: Todo[];
  setFilter: (filter: TodoFilter) => void;
  filter: TodoFilter;
}

export function useTodos(initialTodos: Todo[] = []): UseTodosReturn {
  const [todos, setTodos] = useState<Todo[]>(initialTodos);
  const [filter, setFilter] = useState<TodoFilter>('all');

  const addTodo = useCallback((text: string, priority: Todo['priority']) => {
    const newTodo: Todo = {
      id: crypto.randomUUID(),
      text,
      completed: false,
      createdAt: new Date(),
      priority,
    };
    setTodos(prev => [...prev, newTodo]);
  }, []);

  const toggleTodo = useCallback((id: string) => {
    setTodos(prev => 
      prev.map(t => t.id === id ? { ...t, completed: !t.completed } : t)
    );
  }, []);

  const deleteTodo = useCallback((id: string) => {
    setTodos(prev => prev.filter(t => t.id !== id));
  }, []);

  const filteredTodos = useMemo(() => {
    switch (filter) {
      case 'active':
        return todos.filter(t => !t.completed);
      case 'completed':
        return todos.filter(t => t.completed);
      default:
        return todos;
    }
  }, [todos, filter]);

  return { todos, addTodo, toggleTodo, deleteTodo, filteredTodos, setFilter, filter };
}

// components/TodoItem.tsx
interface TodoItemProps {
  todo: Todo;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
}

const TodoItem = React.memo<TodoItemProps>(({ todo, onToggle, onDelete }) => {
  return (
    <li>
      <input 
        type="checkbox" 
        checked={todo.completed} 
        onChange={() => onToggle(todo.id)} 
      />
      <span className={todo.completed ? 'completed' : ''}>{todo.text}</span>
      <span className={`priority-${todo.priority}`}>{todo.priority}</span>
      <button onClick={() => onDelete(todo.id)}>Delete</button>
    </li>
  );
});
```

---

## 🎯 Interview Questions & Answers

### Q1: Why avoid React.FC?
**Answer:** `React.FC` implicitly includes `children` (confusing), has issues with generics, and doesn't work well with defaultProps. Prefer explicit function signatures with return type `JSX.Element`.

### Q2: How do you type useState with complex objects?
**Answer:** Either provide initial value (inferred) or use generic: `useState<User | null>(null)`. For complex shapes, define interface first.

### Q3: How to type forwardRef?
**Answer:**
```tsx
const Input = React.forwardRef<HTMLInputElement, InputProps>(
  (props, ref) => <input ref={ref} {...props} />
);
```
First generic is ref type, second is props.

---

## ✅ Completion Checklist

- [ ] Understand TypeScript fundamentals
- [ ] Can type components and props
- [ ] Know how to type hooks
- [ ] Handle events with proper types
- [ ] Created fully typed component

---

**Previous:** [Day 14 - Testing](../../week-2-advanced/day-14/README.md)  
**Next:** [Day 16 - Forms](../day-16/README.md)
