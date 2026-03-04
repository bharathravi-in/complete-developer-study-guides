# 📅 Day 4 – State & Lifecycle

## 🎯 Learning Goals
- Master useState hook
- Understand state batching
- Learn functional updates
- Know what triggers re-renders
- Understand component lifecycle in React 19

---

## 📚 Theory

### useState Deep Dive

```tsx
import { useState } from 'react';

// Basic usage
const [count, setCount] = useState(0);

// With type inference
const [user, setUser] = useState({ name: 'John', age: 30 });

// With explicit type
const [items, setItems] = useState<string[]>([]);

// With union type
const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');

// Lazy initialization (for expensive computations)
const [data, setData] = useState(() => {
  // This only runs once on initial render
  return expensiveComputation();
});

// Object state
const [form, setForm] = useState({
  name: '',
  email: '',
  age: 0,
});

// Update single field (must spread previous state!)
setForm(prev => ({ ...prev, name: 'Jane' }));

// ❌ WRONG: Mutating state directly
form.name = 'Jane';  // This won't trigger re-render!
setForm(form);       // Same reference, React won't update

// ✅ CORRECT: Create new object
setForm({ ...form, name: 'Jane' });
```

### State Batching

React 18+ automatically batches state updates for better performance.

```tsx
function Counter() {
  const [count, setCount] = useState(0);
  const [flag, setFlag] = useState(false);

  function handleClick() {
    // React 18+: These are batched - only ONE re-render!
    setCount(c => c + 1);
    setFlag(f => !f);
    // Component re-renders once with both updates
  }

  // Even in async code (new in React 18)
  async function handleAsync() {
    await fetch('/api/data');
    // Still batched in React 18+!
    setCount(c => c + 1);
    setFlag(f => !f);
  }

  // To opt-out of batching (rare cases)
  import { flushSync } from 'react-dom';
  
  function handleUrgent() {
    flushSync(() => {
      setCount(c => c + 1);
    });
    // DOM is updated here
    
    flushSync(() => {
      setFlag(f => !f);
    });
    // DOM is updated here
  }
}
```

### Functional Updates

```tsx
// ❌ Problem with direct updates
function Counter() {
  const [count, setCount] = useState(0);

  function handleClick() {
    // Multiple rapid clicks - only increments by 1!
    setCount(count + 1);  // Uses stale count
    setCount(count + 1);  // Same stale count
    setCount(count + 1);  // Same stale count
  }

  // ✅ Solution: Functional updates
  function handleClickCorrect() {
    setCount(c => c + 1);  // c = 0, returns 1
    setCount(c => c + 1);  // c = 1, returns 2
    setCount(c => c + 1);  // c = 2, returns 3
    // Final count: 3
  }
}

// When to use functional updates:
// 1. New state depends on previous state
// 2. State updates in callbacks/event handlers
// 3. Multiple updates to same state
// 4. Updates in async code

// Examples
setItems(prev => [...prev, newItem]);           // Add to array
setItems(prev => prev.filter(i => i.id !== id)); // Remove from array
setItems(prev => prev.map(i => i.id === id ? {...i, done: true} : i)); // Update in array
setCount(prev => Math.max(0, prev - 1));        // Ensure non-negative
```

### Re-render Triggers

```tsx
// What CAUSES re-render:
// 1. State change
// 2. Props change
// 3. Parent re-render
// 4. Context change

function Parent() {
  const [count, setCount] = useState(0);
  
  return (
    <div>
      <button onClick={() => setCount(c => c + 1)}>
        Increment
      </button>
      {/* Child re-renders when Parent re-renders! */}
      <Child name="John" />
    </div>
  );
}

// Even though Child's props don't change, it re-renders
function Child({ name }: { name: string }) {
  console.log('Child rendered');  // Logs on every parent update!
  return <div>{name}</div>;
}

// Solution: React.memo (Day 9 - Performance)
const MemoizedChild = React.memo(Child);

// What does NOT cause re-render:
// 1. Mutating state directly (wrong way)
// 2. Changing let/const variables
// 3. Changing refs
```

### Component Lifecycle (React 19)

```tsx
// Class component lifecycle (legacy - for reference)
// constructor → render → componentDidMount
// props/state change → render → componentDidUpdate
// unmount → componentWillUnmount

// Functional component "lifecycle" with hooks
function LifecycleDemo({ id }: { id: string }) {
  const [data, setData] = useState(null);

  // "componentDidMount" - runs once after initial render
  useEffect(() => {
    console.log('Component mounted');
    
    // "componentWillUnmount" - cleanup function
    return () => {
      console.log('Component will unmount');
    };
  }, []);  // Empty deps = mount/unmount only

  // "componentDidUpdate" - runs on every id change
  useEffect(() => {
    console.log('ID changed to:', id);
    fetchData(id).then(setData);
    
    return () => {
      // Cleanup before next effect or unmount
      console.log('Cleaning up for ID:', id);
    };
  }, [id]);  // Runs when id changes

  // Render phase
  console.log('Rendering...');
  
  return <div>{data}</div>;
}

// React 19 lifecycle phases:
// 1. Render Phase (pure, no side effects)
//    - Component function executes
//    - Returns JSX
//    - May be paused/aborted/restarted (Concurrent)
//
// 2. Commit Phase (side effects allowed)
//    - DOM updates
//    - useLayoutEffect runs
//    - useEffect runs
//
// 3. Cleanup Phase
//    - Previous useEffect cleanups run
//    - Runs before new effects or unmount
```

---

## ✅ Tasks

### Task 1: Form Handling

Create `src/components/Form/UserForm.tsx`:

```tsx
import { useState, FormEvent, ChangeEvent } from 'react';

interface FormData {
  name: string;
  email: string;
  age: string;
  role: 'developer' | 'designer' | 'manager';
  newsletter: boolean;
}

interface FormErrors {
  name?: string;
  email?: string;
  age?: string;
}

const initialFormData: FormData = {
  name: '',
  email: '',
  age: '',
  role: 'developer',
  newsletter: false,
};

export function UserForm() {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const [errors, setErrors] = useState<FormErrors>({});
  const [submitted, setSubmitted] = useState(false);

  const validate = (): boolean => {
    const newErrors: FormErrors = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Invalid email format';
    }

    if (formData.age && (isNaN(Number(formData.age)) || Number(formData.age) < 0)) {
      newErrors.age = 'Age must be a positive number';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, type } = e.target;
    const value = type === 'checkbox' 
      ? (e.target as HTMLInputElement).checked 
      : e.target.value;

    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name as keyof FormErrors]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (validate()) {
      console.log('Form submitted:', formData);
      setSubmitted(true);
    }
  };

  const handleReset = () => {
    setFormData(initialFormData);
    setErrors({});
    setSubmitted(false);
  };

  if (submitted) {
    return (
      <div className="success">
        <h3>Form Submitted Successfully!</h3>
        <pre>{JSON.stringify(formData, null, 2)}</pre>
        <button onClick={handleReset}>Submit Another</button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="user-form">
      <h2>User Registration</h2>

      <div className="form-group">
        <label htmlFor="name">Name *</label>
        <input
          type="text"
          id="name"
          name="name"
          value={formData.name}
          onChange={handleChange}
          className={errors.name ? 'error' : ''}
        />
        {errors.name && <span className="error-message">{errors.name}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="email">Email *</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          className={errors.email ? 'error' : ''}
        />
        {errors.email && <span className="error-message">{errors.email}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="age">Age</label>
        <input
          type="number"
          id="age"
          name="age"
          value={formData.age}
          onChange={handleChange}
          className={errors.age ? 'error' : ''}
        />
        {errors.age && <span className="error-message">{errors.age}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="role">Role</label>
        <select
          id="role"
          name="role"
          value={formData.role}
          onChange={handleChange}
        >
          <option value="developer">Developer</option>
          <option value="designer">Designer</option>
          <option value="manager">Manager</option>
        </select>
      </div>

      <div className="form-group checkbox">
        <input
          type="checkbox"
          id="newsletter"
          name="newsletter"
          checked={formData.newsletter}
          onChange={handleChange}
        />
        <label htmlFor="newsletter">Subscribe to newsletter</label>
      </div>

      <div className="form-actions">
        <button type="button" onClick={handleReset}>Reset</button>
        <button type="submit">Submit</button>
      </div>
    </form>
  );
}
```

### Task 2: Toggle Components

Create `src/components/Toggle/Toggle.tsx`:

```tsx
import { useState, ReactNode } from 'react';

// Simple Toggle Hook
function useToggle(initialValue = false): [boolean, () => void] {
  const [value, setValue] = useState(initialValue);
  const toggle = () => setValue(prev => !prev);
  return [value, toggle];
}

// Toggle Button Component
interface ToggleButtonProps {
  initialOn?: boolean;
  onToggle?: (isOn: boolean) => void;
  children?: ReactNode;
}

export function ToggleButton({ initialOn = false, onToggle, children }: ToggleButtonProps) {
  const [isOn, toggle] = useToggle(initialOn);

  const handleClick = () => {
    toggle();
    onToggle?.(!isOn);
  };

  return (
    <button
      onClick={handleClick}
      className={`toggle-button ${isOn ? 'on' : 'off'}`}
      aria-pressed={isOn}
    >
      {children || (isOn ? 'ON' : 'OFF')}
    </button>
  );
}

// Accordion Component
interface AccordionProps {
  title: string;
  children: ReactNode;
  defaultOpen?: boolean;
}

export function Accordion({ title, children, defaultOpen = false }: AccordionProps) {
  const [isOpen, toggle] = useToggle(defaultOpen);

  return (
    <div className="accordion">
      <button
        className="accordion-header"
        onClick={toggle}
        aria-expanded={isOpen}
      >
        <span>{title}</span>
        <span className={`arrow ${isOpen ? 'up' : 'down'}`}>▼</span>
      </button>
      {isOpen && <div className="accordion-content">{children}</div>}
    </div>
  );
}

// Modal Component
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{title}</h3>
          <button onClick={onClose} aria-label="Close">×</button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}

// Demo Component
export function ToggleDemo() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);

  return (
    <div className={`toggle-demo ${darkMode ? 'dark' : 'light'}`}>
      <h2>Toggle Components Demo</h2>

      {/* Toggle Button */}
      <section>
        <h3>Toggle Button</h3>
        <ToggleButton onToggle={setDarkMode}>
          {darkMode ? '🌙 Dark Mode' : '☀️ Light Mode'}
        </ToggleButton>
      </section>

      {/* Accordion */}
      <section>
        <h3>Accordion</h3>
        <Accordion title="What is React?" defaultOpen>
          React is a JavaScript library for building user interfaces.
        </Accordion>
        <Accordion title="What are Hooks?">
          Hooks let you use state and other React features without classes.
        </Accordion>
        <Accordion title="What is JSX?">
          JSX is a syntax extension that looks like HTML but works with JavaScript.
        </Accordion>
      </section>

      {/* Modal */}
      <section>
        <h3>Modal</h3>
        <button onClick={() => setIsModalOpen(true)}>Open Modal</button>
        <Modal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          title="Confirmation"
        >
          <p>Are you sure you want to proceed?</p>
          <div className="modal-actions">
            <button onClick={() => setIsModalOpen(false)}>Cancel</button>
            <button onClick={() => setIsModalOpen(false)}>Confirm</button>
          </div>
        </Modal>
      </section>
    </div>
  );
}
```

---

## 🎯 Interview Questions & Answers

### Q1: Why are state updates asynchronous?
**Answer:** State updates are asynchronous for several reasons:

1. **Batching:** React batches multiple state updates for performance. Processing them synchronously would cause unnecessary re-renders.

2. **Consistency:** Ensures `props` and `state` are consistent. If state updated immediately, props would still be stale.

3. **Concurrent Features:** Allows React to prioritize updates, pause rendering, and handle transitions smoothly.

```tsx
function Example() {
  const [count, setCount] = useState(0);
  
  function handleClick() {
    setCount(count + 1);
    console.log(count);  // Still 0! Update is queued, not applied yet
  }
  
  // To react to state change, use useEffect
  useEffect(() => {
    console.log('Count is now:', count);  // Runs after state update
  }, [count]);
}
```

### Q2: What causes a re-render?
**Answer:** Four things cause re-renders:

1. **State change:** Calling setState with a new value
2. **Props change:** Parent passes different props
3. **Parent re-render:** When parent re-renders, children re-render too
4. **Context change:** When context value changes

```tsx
// State change
setCount(1);  // New value → re-render

// Same value → NO re-render (React bails out)
setCount(0);  // If count is already 0

// Object state - reference must change
setUser({ ...user, name: 'New' });  // New object → re-render
setUser(user);  // Same reference → no re-render

// Parent re-render causing child re-render
function Parent() {
  const [x, setX] = useState(0);
  return <Child />;  // Child re-renders even if its props don't change!
}
```

### Q3: useState vs useReducer?
**Answer:**

| useState | useReducer |
|----------|------------|
| Simple state | Complex state logic |
| Independent values | Related state transitions |
| Few updates | Many update actions |
| Inline logic | Centralized logic |

```tsx
// useState: simple, independent state
const [name, setName] = useState('');
const [age, setAge] = useState(0);

// useReducer: complex, related state
const [state, dispatch] = useReducer(reducer, initialState);

function reducer(state, action) {
  switch (action.type) {
    case 'INCREMENT': return { ...state, count: state.count + 1 };
    case 'SET_NAME': return { ...state, name: action.payload };
    case 'RESET': return initialState;
  }
}
```

### Q4: How does state batching work?
**Answer:** React 18+ automatically batches all state updates:

```tsx
// All these cause a SINGLE re-render
function handleClick() {
  setCount(c => c + 1);
  setFlag(f => !f);
  setName('New');
}

// Even async updates are batched in React 18+
async function handleAsync() {
  await fetch('/api');
  setCount(c => c + 1);  // Batched!
  setFlag(f => !f);      // Batched!
}

// To force synchronous update (rare):
import { flushSync } from 'react-dom';
flushSync(() => setCount(c => c + 1));
```

### Q5: What is lazy initialization?
**Answer:** Lazy initialization delays expensive computations until actually needed:

```tsx
// ❌ Runs on EVERY render
const [data, setData] = useState(expensiveComputation());

// ✅ Runs only on initial render
const [data, setData] = useState(() => expensiveComputation());

// Use cases:
// 1. Reading from localStorage
const [theme, setTheme] = useState(() => {
  return localStorage.getItem('theme') || 'light';
});

// 2. Complex initial calculations
const [grid, setGrid] = useState(() => {
  return Array(100).fill(null).map((_, i) => createCell(i));
});
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

- [ ] Master useState hook patterns
- [ ] Understand state batching
- [ ] Know when to use functional updates
- [ ] Understand re-render triggers
- [ ] Know component lifecycle phases
- [ ] Built form with validation
- [ ] Built toggle components
- [ ] Can answer all interview questions

---

**Previous:** [Day 3 - Components Deep Dive](../day-03/README.md)  
**Next:** [Day 5 - useEffect Mastery](../day-05/README.md)
