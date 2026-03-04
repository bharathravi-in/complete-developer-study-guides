# 📅 Day 2 – JSX & Rendering

## 🎯 Learning Goals
- Understand JSX internals and Babel transformation
- Master expressions in JSX
- Learn conditional rendering patterns
- Handle lists and keys properly
- Use Fragments effectively

---

## 📚 Theory

### JSX Internals (Babel Transform)

JSX is syntactic sugar for `React.createElement()` calls. Babel transforms JSX at build time.

```jsx
// What you write (JSX)
const element = (
  <div className="container">
    <h1>Hello, {name}</h1>
    <Button onClick={handleClick}>Click me</Button>
  </div>
);

// What Babel outputs (React 17+ JSX Transform)
import { jsx as _jsx, jsxs as _jsxs } from 'react/jsx-runtime';

const element = _jsxs('div', {
  className: 'container',
  children: [
    _jsx('h1', { children: ['Hello, ', name] }),
    _jsx(Button, { onClick: handleClick, children: 'Click me' }),
  ],
});

// Old transform (before React 17)
const element = React.createElement(
  'div',
  { className: 'container' },
  React.createElement('h1', null, 'Hello, ', name),
  React.createElement(Button, { onClick: handleClick }, 'Click me')
);
```

**Key Points:**
- JSX elements become function calls
- Props become an object
- Children are passed as additional arguments or `children` prop
- React 17+ has automatic JSX runtime (no import needed)

### Expressions in JSX

```tsx
// Variables
const name = 'React';
<h1>Hello, {name}</h1>

// Function calls
<p>Current time: {new Date().toLocaleTimeString()}</p>

// Ternary operators
<p>{isLoggedIn ? 'Welcome back!' : 'Please log in'}</p>

// Logical operators
<div>{isLoading && <Spinner />}</div>

// Array methods
<ul>{items.map(item => <li key={item.id}>{item.name}</li>)}</ul>

// Template literals
<p className={`status ${isActive ? 'active' : 'inactive'}`}>Status</p>

// Object properties
<User name={user.name} email={user.email} />

// Computed properties
<div style={{ backgroundColor: color }}>{content}</div>
```

**What you CANNOT do:**
```tsx
// ❌ Statements (if, for, while)
<div>{if (condition) { return 'yes' }}</div>

// ❌ Object literals (without wrapping)
<div>{object}</div>  // Objects are not valid React children

// ✅ Convert to expressions
<div>{condition ? 'yes' : 'no'}</div>
<div>{JSON.stringify(object)}</div>
```

### Conditional Rendering

```tsx
// 1. Ternary Operator - for either/or
function Greeting({ isLoggedIn }: { isLoggedIn: boolean }) {
  return (
    <div>
      {isLoggedIn ? <UserGreeting /> : <GuestGreeting />}
    </div>
  );
}

// 2. Logical AND (&&) - for show/hide
function Mailbox({ unreadMessages }: { unreadMessages: string[] }) {
  return (
    <div>
      <h1>Inbox</h1>
      {unreadMessages.length > 0 && (
        <p>You have {unreadMessages.length} unread messages.</p>
      )}
    </div>
  );
}

// ⚠️ Gotcha with && and 0
// This will render "0" instead of nothing!
{count && <Results />}  // If count is 0, renders "0"

// ✅ Fix: explicit boolean conversion
{count > 0 && <Results />}
{!!count && <Results />}
{Boolean(count) && <Results />}

// 3. Early return pattern
function UserProfile({ user }: { user: User | null }) {
  if (!user) {
    return <div>Please log in</div>;
  }
  
  return <div>Welcome, {user.name}</div>;
}

// 4. Switch-like with object lookup
const statusComponents = {
  loading: <Spinner />,
  error: <ErrorMessage />,
  success: <SuccessMessage />,
  idle: null,
};

function StatusDisplay({ status }: { status: keyof typeof statusComponents }) {
  return <div>{statusComponents[status]}</div>;
}

// 5. Immediately Invoked Function Expression (IIFE)
function ComplexCondition({ status }: { status: string }) {
  return (
    <div>
      {(() => {
        switch (status) {
          case 'loading': return <Spinner />;
          case 'error': return <Error />;
          case 'success': return <Success />;
          default: return null;
        }
      })()}
    </div>
  );
}
```

### Lists & Keys

```tsx
interface Item {
  id: string;
  name: string;
  completed: boolean;
}

// Basic list rendering
function ItemList({ items }: { items: Item[] }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>
          {item.name}
        </li>
      ))}
    </ul>
  );
}

// With index (only when items never reorder)
function StaticList({ items }: { items: string[] }) {
  return (
    <ul>
      {items.map((item, index) => (
        <li key={index}>{item}</li>  // OK for static lists
      ))}
    </ul>
  );
}

// Extracting list item component
function TodoItem({ item, onToggle }: { item: Item; onToggle: (id: string) => void }) {
  return (
    <li onClick={() => onToggle(item.id)}>
      <input 
        type="checkbox" 
        checked={item.completed} 
        readOnly
      />
      {item.name}
    </li>
  );
}

function TodoList({ items, onToggle }: { items: Item[]; onToggle: (id: string) => void }) {
  return (
    <ul>
      {items.map(item => (
        <TodoItem 
          key={item.id}  // Key goes on the outermost element in map
          item={item} 
          onToggle={onToggle}
        />
      ))}
    </ul>
  );
}
```

### Fragments

```tsx
import { Fragment } from 'react';

// Problem: div wrappers everywhere
function Table() {
  return (
    <table>
      <tbody>
        <tr>
          <Columns />  {/* Can't return multiple <td> with a wrapping div */}
        </tr>
      </tbody>
    </table>
  );
}

// Solution 1: Fragment long syntax (when you need key)
function Columns() {
  return (
    <Fragment>
      <td>Column 1</td>
      <td>Column 2</td>
    </Fragment>
  );
}

// Solution 2: Fragment short syntax (most common)
function Columns() {
  return (
    <>
      <td>Column 1</td>
      <td>Column 2</td>
    </>
  );
}

// With key (must use Fragment, not <>)
function Glossary({ items }: { items: { id: string; term: string; description: string }[] }) {
  return (
    <dl>
      {items.map(item => (
        <Fragment key={item.id}>
          <dt>{item.term}</dt>
          <dd>{item.description}</dd>
        </Fragment>
      ))}
    </dl>
  );
}
```

---

## ✅ Tasks

### Task 1: Todo List Rendering

Create `src/components/TodoList.tsx`:

```tsx
import { useState } from 'react';

interface Todo {
  id: string;
  text: string;
  completed: boolean;
}

const initialTodos: Todo[] = [
  { id: '1', text: 'Learn React', completed: true },
  { id: '2', text: 'Build a project', completed: false },
  { id: '3', text: 'Master JSX', completed: false },
];

export function TodoList() {
  const [todos, setTodos] = useState<Todo[]>(initialTodos);
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');

  const toggleTodo = (id: string) => {
    setTodos(todos.map(todo =>
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ));
  };

  const filteredTodos = todos.filter(todo => {
    if (filter === 'active') return !todo.completed;
    if (filter === 'completed') return todo.completed;
    return true;
  });

  return (
    <div className="todo-list">
      <h2>My Todos</h2>
      
      {/* Filter buttons */}
      <div className="filters">
        {(['all', 'active', 'completed'] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={filter === f ? 'active' : ''}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* Todo count */}
      {filteredTodos.length > 0 && (
        <p>{filteredTodos.length} item(s)</p>
      )}

      {/* Empty state */}
      {filteredTodos.length === 0 && (
        <p className="empty">No todos found</p>
      )}

      {/* Todo list */}
      <ul>
        {filteredTodos.map(todo => (
          <li
            key={todo.id}
            onClick={() => toggleTodo(todo.id)}
            className={todo.completed ? 'completed' : ''}
          >
            <input
              type="checkbox"
              checked={todo.completed}
              readOnly
            />
            <span>{todo.text}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Task 2: Conditional Component Display

Create `src/components/ConditionalDisplay.tsx`:

```tsx
import { useState } from 'react';

type Status = 'idle' | 'loading' | 'success' | 'error';

interface User {
  name: string;
  email: string;
}

// Status components
const StatusIdle = () => <p>Click the button to fetch user</p>;
const StatusLoading = () => <p className="loading">Loading...</p>;
const StatusError = ({ message }: { message: string }) => (
  <p className="error">Error: {message}</p>
);
const StatusSuccess = ({ user }: { user: User }) => (
  <div className="user-card">
    <h3>{user.name}</h3>
    <p>{user.email}</p>
  </div>
);

export function ConditionalDisplay() {
  const [status, setStatus] = useState<Status>('idle');
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState<string>('');

  const fetchUser = async () => {
    setStatus('loading');
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    // Randomly succeed or fail
    if (Math.random() > 0.3) {
      setUser({ name: 'John Doe', email: 'john@example.com' });
      setStatus('success');
    } else {
      setError('Failed to fetch user');
      setStatus('error');
    }
  };

  const reset = () => {
    setStatus('idle');
    setUser(null);
    setError('');
  };

  // Render based on status
  const renderContent = () => {
    switch (status) {
      case 'idle':
        return <StatusIdle />;
      case 'loading':
        return <StatusLoading />;
      case 'error':
        return <StatusError message={error} />;
      case 'success':
        return user && <StatusSuccess user={user} />;
    }
  };

  return (
    <div className="conditional-display">
      <h2>Conditional Rendering Demo</h2>
      
      {renderContent()}
      
      <div className="actions">
        {status === 'idle' && (
          <button onClick={fetchUser}>Fetch User</button>
        )}
        {(status === 'success' || status === 'error') && (
          <button onClick={reset}>Reset</button>
        )}
      </div>
    </div>
  );
}
```

---

## 🎯 Interview Questions & Answers

### Q1: Why should key not be index?
**Answer:** Using array index as key causes problems:

1. **State Corruption:** When items reorder, React matches by position, not identity. Component state gets attached to wrong items.

```jsx
// Items: [A, B, C] with index keys [0, 1, 2]
// After removing B: [A, C] with keys [0, 1]
// React thinks: item at index 1 changed from B to C (wrong!)
```

2. **Performance:** React can't efficiently reuse DOM nodes when list changes.

3. **Animation Issues:** Enter/exit animations break because identity is lost.

**When index IS acceptable:**
- List items have no state
- List never reorders
- List never filters
- Items have no unique ID

**Best practice:** Always use unique, stable IDs from your data.

### Q2: How does JSX convert internally?
**Answer:** 

1. **Babel processes JSX** at build time
2. JSX elements become `React.createElement()` or `jsx()` calls
3. Each element becomes a plain JavaScript object

```jsx
// Input
<Button color="blue">Click</Button>

// Output (React 17+ JSX transform)
import { jsx } from 'react/jsx-runtime';
jsx(Button, { color: 'blue', children: 'Click' });

// The jsx() returns a React Element object:
{
  $$typeof: Symbol(react.element),
  type: Button,
  props: { color: 'blue', children: 'Click' },
  key: null,
  ref: null,
}
```

### Q3: What renders as nothing in React?
**Answer:** These values render nothing:
- `null`
- `undefined`
- `true` / `false` (booleans)

These render as text:
- `0` (number zero)
- `''` (empty string - technically nothing)
- `NaN`

```jsx
// All render nothing
{null}
{undefined}
{true}
{false}

// Renders "0"
{0}
{count && <Results />}  // If count is 0
```

### Q4: Fragment vs div - when to use which?
**Answer:** 
- **Fragment:** When you need to group elements without adding DOM node
- **div:** When you need a wrapper for styling, events, or refs

```jsx
// Use Fragment: no extra DOM node needed
<>
  <Header />
  <Main />
  <Footer />
</>

// Use Fragment with key: in lists returning multiple elements
{items.map(item => (
  <Fragment key={item.id}>
    <dt>{item.term}</dt>
    <dd>{item.definition}</dd>
  </Fragment>
))}

// Use div: need styling or events
<div className="card" onClick={handleClick}>
  <Header />
  <Content />
</div>
```

### Q5: How to conditionally add attributes?
**Answer:**
```tsx
// Spread with conditional object
<button
  {...(isDisabled && { disabled: true })}
  {...(ariaLabel && { 'aria-label': ariaLabel })}
>
  Click
</button>

// Ternary for single attribute
<input
  className={isError ? 'error' : undefined}
  disabled={isLoading}
/>

// undefined/null removes the attribute
<button disabled={isDisabled || undefined}>Click</button>
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

- [ ] Understand Babel JSX transformation
- [ ] Can use expressions in JSX correctly
- [ ] Know all conditional rendering patterns
- [ ] Understand why index as key is problematic
- [ ] Know when to use Fragments
- [ ] Built todo list with filtering
- [ ] Built conditional display component
- [ ] Can answer all interview questions

---

**Previous:** [Day 1 - React Fundamentals](../day-01/README.md)  
**Next:** [Day 3 - Components Deep Dive](../day-03/README.md)
