# 📅 Day 7 – Mini Project: Advanced Todo App

## 🎯 Learning Goals
Apply everything from Week 1 to build a complete Todo application with:
- Filtering and search
- Local storage persistence
- Custom hooks
- Reusable components
- TypeScript

---

## 🏗️ Project Overview

### Features
1. **CRUD Operations** - Create, read, update, delete todos
2. **Filtering** - All, Active, Completed
3. **Search** - Real-time search with debounce
4. **Local Storage** - Persistence across sessions
5. **Categories** - Organize todos by category
6. **Due Dates** - Set and display due dates
7. **Priority Levels** - High, Medium, Low

### Project Structure
```
src/
├── components/
│   ├── TodoApp/
│   │   ├── TodoApp.tsx
│   │   ├── TodoApp.css
│   │   └── index.ts
│   ├── TodoInput/
│   │   ├── TodoInput.tsx
│   │   └── index.ts
│   ├── TodoList/
│   │   ├── TodoList.tsx
│   │   ├── TodoItem.tsx
│   │   └── index.ts
│   ├── TodoFilters/
│   │   ├── TodoFilters.tsx
│   │   └── index.ts
│   └── ui/
│       ├── Button.tsx
│       ├── Input.tsx
│       ├── Select.tsx
│       └── Badge.tsx
├── hooks/
│   ├── useLocalStorage.ts
│   ├── useDebounce.ts
│   └── useTodos.ts
├── types/
│   └── todo.ts
├── utils/
│   └── todoUtils.ts
└── App.tsx
```

---

## 💻 Implementation

### Step 1: Types

Create `src/types/todo.ts`:

```tsx
export type Priority = 'low' | 'medium' | 'high';
export type FilterStatus = 'all' | 'active' | 'completed';

export interface Todo {
  id: string;
  text: string;
  completed: boolean;
  category: string;
  priority: Priority;
  dueDate: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface TodoFilters {
  status: FilterStatus;
  category: string;
  priority: Priority | 'all';
  search: string;
}
```

### Step 2: Custom Hooks

Create `src/hooks/useLocalStorage.ts`:

```tsx
import { useState, useEffect, useCallback } from 'react';

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T | ((prev: T) => T)) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((prev: T) => T)) => {
    try {
      setStoredValue(prev => {
        const valueToStore = value instanceof Function ? value(prev) : value;
        localStorage.setItem(key, JSON.stringify(valueToStore));
        return valueToStore;
      });
    } catch (error) {
      console.error('useLocalStorage error:', error);
    }
  }, [key]);

  return [storedValue, setValue];
}
```

Create `src/hooks/useDebounce.ts`:

```tsx
import { useState, useEffect } from 'react';

export function useDebounce<T>(value: T, delay: number = 300): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
```

Create `src/hooks/useTodos.ts`:

```tsx
import { useCallback, useMemo } from 'react';
import { useLocalStorage } from './useLocalStorage';
import { useDebounce } from './useDebounce';
import { Todo, TodoFilters, Priority } from '../types/todo';

const generateId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;

const initialFilters: TodoFilters = {
  status: 'all',
  category: 'all',
  priority: 'all',
  search: '',
};

export function useTodos() {
  const [todos, setTodos] = useLocalStorage<Todo[]>('todos', []);
  const [filters, setFilters] = useLocalStorage<TodoFilters>('todoFilters', initialFilters);
  
  const debouncedSearch = useDebounce(filters.search, 300);

  // Add todo
  const addTodo = useCallback((
    text: string,
    category: string = 'general',
    priority: Priority = 'medium',
    dueDate: string | null = null
  ) => {
    const now = new Date().toISOString();
    const newTodo: Todo = {
      id: generateId(),
      text: text.trim(),
      completed: false,
      category,
      priority,
      dueDate,
      createdAt: now,
      updatedAt: now,
    };
    
    setTodos(prev => [newTodo, ...prev]);
  }, [setTodos]);

  // Toggle todo
  const toggleTodo = useCallback((id: string) => {
    setTodos(prev => prev.map(todo =>
      todo.id === id
        ? { ...todo, completed: !todo.completed, updatedAt: new Date().toISOString() }
        : todo
    ));
  }, [setTodos]);

  // Update todo
  const updateTodo = useCallback((id: string, updates: Partial<Todo>) => {
    setTodos(prev => prev.map(todo =>
      todo.id === id
        ? { ...todo, ...updates, updatedAt: new Date().toISOString() }
        : todo
    ));
  }, [setTodos]);

  // Delete todo
  const deleteTodo = useCallback((id: string) => {
    setTodos(prev => prev.filter(todo => todo.id !== id));
  }, [setTodos]);

  // Clear completed
  const clearCompleted = useCallback(() => {
    setTodos(prev => prev.filter(todo => !todo.completed));
  }, [setTodos]);

  // Update filters
  const updateFilters = useCallback((newFilters: Partial<TodoFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  }, [setFilters]);

  // Reset filters
  const resetFilters = useCallback(() => {
    setFilters(initialFilters);
  }, [setFilters]);

  // Filtered todos
  const filteredTodos = useMemo(() => {
    return todos.filter(todo => {
      // Status filter
      if (filters.status === 'active' && todo.completed) return false;
      if (filters.status === 'completed' && !todo.completed) return false;

      // Category filter
      if (filters.category !== 'all' && todo.category !== filters.category) return false;

      // Priority filter
      if (filters.priority !== 'all' && todo.priority !== filters.priority) return false;

      // Search filter (debounced)
      if (debouncedSearch) {
        const searchLower = debouncedSearch.toLowerCase();
        if (!todo.text.toLowerCase().includes(searchLower)) return false;
      }

      return true;
    });
  }, [todos, filters.status, filters.category, filters.priority, debouncedSearch]);

  // Stats
  const stats = useMemo(() => ({
    total: todos.length,
    active: todos.filter(t => !t.completed).length,
    completed: todos.filter(t => t.completed).length,
    filtered: filteredTodos.length,
  }), [todos, filteredTodos]);

  // Categories
  const categories = useMemo(() => {
    const cats = new Set(todos.map(t => t.category));
    return ['all', ...Array.from(cats)];
  }, [todos]);

  return {
    todos: filteredTodos,
    allTodos: todos,
    filters,
    stats,
    categories,
    addTodo,
    toggleTodo,
    updateTodo,
    deleteTodo,
    clearCompleted,
    updateFilters,
    resetFilters,
  };
}
```

### Step 3: UI Components

Create `src/components/ui/Button.tsx`:

```tsx
import { ButtonHTMLAttributes, ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  children: ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  children,
  className = '',
  ...props
}: ButtonProps) {
  const baseStyles = 'rounded font-medium transition-colors focus:outline-none focus:ring-2';
  
  const variantStyles = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600 focus:ring-blue-300',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300 focus:ring-gray-300',
    danger: 'bg-red-500 text-white hover:bg-red-600 focus:ring-red-300',
    ghost: 'bg-transparent hover:bg-gray-100 focus:ring-gray-300',
  };

  const sizeStyles = {
    sm: 'px-2 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
  };

  return (
    <button
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
```

Create `src/components/ui/Badge.tsx`:

```tsx
import { ReactNode } from 'react';
import { Priority } from '../../types/todo';

interface BadgeProps {
  children: ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger';
}

export function Badge({ children, variant = 'default' }: BadgeProps) {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
  };

  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${variants[variant]}`}>
      {children}
    </span>
  );
}

export function PriorityBadge({ priority }: { priority: Priority }) {
  const variants: Record<Priority, 'danger' | 'warning' | 'default'> = {
    high: 'danger',
    medium: 'warning',
    low: 'default',
  };

  return <Badge variant={variants[priority]}>{priority}</Badge>;
}
```

### Step 4: Todo Components

Create `src/components/TodoInput/TodoInput.tsx`:

```tsx
import { useState, FormEvent } from 'react';
import { Button } from '../ui/Button';
import { Priority } from '../../types/todo';

interface TodoInputProps {
  onAdd: (text: string, category: string, priority: Priority, dueDate: string | null) => void;
  categories: string[];
}

export function TodoInput({ onAdd, categories }: TodoInputProps) {
  const [text, setText] = useState('');
  const [category, setCategory] = useState('general');
  const [priority, setPriority] = useState<Priority>('medium');
  const [dueDate, setDueDate] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;

    onAdd(text, category, priority, dueDate || null);
    setText('');
    setDueDate('');
  };

  return (
    <form onSubmit={handleSubmit} className="todo-input">
      <div className="flex gap-2">
        <input
          type="text"
          value={text}
          onChange={e => setText(e.target.value)}
          placeholder="What needs to be done?"
          className="flex-1 px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-300"
        />
        <Button type="submit">Add</Button>
        <Button 
          type="button" 
          variant="ghost"
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          {showAdvanced ? '−' : '+'}
        </Button>
      </div>

      {showAdvanced && (
        <div className="mt-2 flex gap-2 flex-wrap">
          <select
            value={category}
            onChange={e => setCategory(e.target.value)}
            className="px-3 py-1 border rounded"
          >
            {categories.filter(c => c !== 'all').map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
            <option value="work">work</option>
            <option value="personal">personal</option>
            <option value="shopping">shopping</option>
          </select>

          <select
            value={priority}
            onChange={e => setPriority(e.target.value as Priority)}
            className="px-3 py-1 border rounded"
          >
            <option value="low">Low Priority</option>
            <option value="medium">Medium Priority</option>
            <option value="high">High Priority</option>
          </select>

          <input
            type="date"
            value={dueDate}
            onChange={e => setDueDate(e.target.value)}
            className="px-3 py-1 border rounded"
          />
        </div>
      )}
    </form>
  );
}
```

Create `src/components/TodoFilters/TodoFilters.tsx`:

```tsx
import { TodoFilters as Filters, FilterStatus, Priority } from '../../types/todo';
import { Button } from '../ui/Button';

interface TodoFiltersProps {
  filters: Filters;
  categories: string[];
  stats: {
    total: number;
    active: number;
    completed: number;
    filtered: number;
  };
  onUpdateFilters: (filters: Partial<Filters>) => void;
  onResetFilters: () => void;
  onClearCompleted: () => void;
}

export function TodoFilters({
  filters,
  categories,
  stats,
  onUpdateFilters,
  onResetFilters,
  onClearCompleted,
}: TodoFiltersProps) {
  const statusOptions: { value: FilterStatus; label: string; count?: number }[] = [
    { value: 'all', label: 'All', count: stats.total },
    { value: 'active', label: 'Active', count: stats.active },
    { value: 'completed', label: 'Completed', count: stats.completed },
  ];

  return (
    <div className="todo-filters space-y-4">
      {/* Search */}
      <input
        type="text"
        value={filters.search}
        onChange={e => onUpdateFilters({ search: e.target.value })}
        placeholder="Search todos..."
        className="w-full px-4 py-2 border rounded"
      />

      {/* Status Filter */}
      <div className="flex gap-2">
        {statusOptions.map(option => (
          <Button
            key={option.value}
            variant={filters.status === option.value ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => onUpdateFilters({ status: option.value })}
          >
            {option.label} ({option.count})
          </Button>
        ))}
      </div>

      {/* Category & Priority Filters */}
      <div className="flex gap-2">
        <select
          value={filters.category}
          onChange={e => onUpdateFilters({ category: e.target.value })}
          className="px-3 py-1 border rounded"
        >
          {categories.map(cat => (
            <option key={cat} value={cat}>
              {cat === 'all' ? 'All Categories' : cat}
            </option>
          ))}
        </select>

        <select
          value={filters.priority}
          onChange={e => onUpdateFilters({ priority: e.target.value as Priority | 'all' })}
          className="px-3 py-1 border rounded"
        >
          <option value="all">All Priorities</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {/* Actions */}
      <div className="flex gap-2 justify-between">
        <span className="text-gray-500">
          {stats.filtered} of {stats.total} shown
        </span>
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={onResetFilters}>
            Reset Filters
          </Button>
          {stats.completed > 0 && (
            <Button variant="danger" size="sm" onClick={onClearCompleted}>
              Clear Completed
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
```

Create `src/components/TodoList/TodoItem.tsx`:

```tsx
import { useState, memo } from 'react';
import { Todo, Priority } from '../../types/todo';
import { Button } from '../ui/Button';
import { PriorityBadge } from '../ui/Badge';

interface TodoItemProps {
  todo: Todo;
  onToggle: (id: string) => void;
  onUpdate: (id: string, updates: Partial<Todo>) => void;
  onDelete: (id: string) => void;
}

export const TodoItem = memo(function TodoItem({
  todo,
  onToggle,
  onUpdate,
  onDelete,
}: TodoItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(todo.text);

  const handleSave = () => {
    if (editText.trim()) {
      onUpdate(todo.id, { text: editText.trim() });
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSave();
    if (e.key === 'Escape') {
      setEditText(todo.text);
      setIsEditing(false);
    }
  };

  const isOverdue = todo.dueDate && new Date(todo.dueDate) < new Date() && !todo.completed;

  return (
    <li className={`todo-item p-4 border rounded mb-2 ${todo.completed ? 'opacity-50' : ''} ${isOverdue ? 'border-red-300 bg-red-50' : ''}`}>
      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={() => onToggle(todo.id)}
          className="w-5 h-5"
        />

        <div className="flex-1">
          {isEditing ? (
            <input
              type="text"
              value={editText}
              onChange={e => setEditText(e.target.value)}
              onBlur={handleSave}
              onKeyDown={handleKeyDown}
              className="w-full px-2 py-1 border rounded"
              autoFocus
            />
          ) : (
            <span
              className={`cursor-pointer ${todo.completed ? 'line-through text-gray-400' : ''}`}
              onDoubleClick={() => setIsEditing(true)}
            >
              {todo.text}
            </span>
          )}

          <div className="flex gap-2 mt-1 text-xs text-gray-500">
            <span className="bg-gray-100 px-2 py-0.5 rounded">{todo.category}</span>
            <PriorityBadge priority={todo.priority} />
            {todo.dueDate && (
              <span className={isOverdue ? 'text-red-500 font-medium' : ''}>
                Due: {new Date(todo.dueDate).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>

        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsEditing(true)}
          >
            ✏️
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onDelete(todo.id)}
          >
            🗑️
          </Button>
        </div>
      </div>
    </li>
  );
});
```

Create `src/components/TodoList/TodoList.tsx`:

```tsx
import { Todo } from '../../types/todo';
import { TodoItem } from './TodoItem';

interface TodoListProps {
  todos: Todo[];
  onToggle: (id: string) => void;
  onUpdate: (id: string, updates: Partial<Todo>) => void;
  onDelete: (id: string) => void;
}

export function TodoList({ todos, onToggle, onUpdate, onDelete }: TodoListProps) {
  if (todos.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-4xl mb-2">📝</p>
        <p>No todos found</p>
        <p className="text-sm">Add a todo or adjust your filters</p>
      </div>
    );
  }

  return (
    <ul className="todo-list">
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onUpdate={onUpdate}
          onDelete={onDelete}
        />
      ))}
    </ul>
  );
}
```

### Step 5: Main App Component

Create `src/components/TodoApp/TodoApp.tsx`:

```tsx
import { useTodos } from '../../hooks/useTodos';
import { TodoInput } from '../TodoInput/TodoInput';
import { TodoFilters } from '../TodoFilters/TodoFilters';
import { TodoList } from '../TodoList/TodoList';
import './TodoApp.css';

export function TodoApp() {
  const {
    todos,
    filters,
    stats,
    categories,
    addTodo,
    toggleTodo,
    updateTodo,
    deleteTodo,
    clearCompleted,
    updateFilters,
    resetFilters,
  } = useTodos();

  return (
    <div className="todo-app max-w-2xl mx-auto p-6">
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-gray-800">📋 Todo App</h1>
        <p className="text-gray-500">Week 1 React Mastery Project</p>
      </header>

      <section className="mb-6">
        <TodoInput onAdd={addTodo} categories={categories} />
      </section>

      <section className="mb-6">
        <TodoFilters
          filters={filters}
          categories={categories}
          stats={stats}
          onUpdateFilters={updateFilters}
          onResetFilters={resetFilters}
          onClearCompleted={clearCompleted}
        />
      </section>

      <section>
        <TodoList
          todos={todos}
          onToggle={toggleTodo}
          onUpdate={updateTodo}
          onDelete={deleteTodo}
        />
      </section>

      <footer className="mt-8 text-center text-gray-400 text-sm">
        <p>Double-click to edit a todo</p>
        <p>Data is saved to localStorage</p>
      </footer>
    </div>
  );
}
```

Create `src/components/TodoApp/TodoApp.css`:

```css
.todo-app {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.todo-app > * {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.todo-app header {
  background: transparent;
  box-shadow: none;
  color: white;
}

.todo-app header h1 {
  color: white;
}

.todo-app header p {
  color: rgba(255, 255, 255, 0.8);
}

.todo-app footer {
  background: transparent;
  box-shadow: none;
  color: rgba(255, 255, 255, 0.7);
}
```

Update `src/App.tsx`:

```tsx
import { TodoApp } from './components/TodoApp/TodoApp';

function App() {
  return <TodoApp />;
}

export default App;
```

---

## ✅ Completion Checklist

### Features
- [ ] Add new todos
- [ ] Mark todos as complete
- [ ] Delete todos
- [ ] Edit todos (double-click)
- [ ] Filter by status
- [ ] Filter by category
- [ ] Filter by priority
- [ ] Search with debounce
- [ ] Persist to localStorage
- [ ] Clear completed todos
- [ ] Show todo count stats
- [ ] Due date functionality
- [ ] Overdue highlighting

### Code Quality
- [ ] TypeScript types defined
- [ ] Custom hooks extracted
- [ ] Components are reusable
- [ ] Memoization where needed
- [ ] Props properly typed
- [ ] Clean folder structure

### Concepts Applied
- [ ] useState for component state
- [ ] useEffect (in hooks)
- [ ] useCallback for stable callbacks
- [ ] useMemo for computed values
- [ ] useRef (if needed)
- [ ] Custom hooks
- [ ] Component composition
- [ ] Conditional rendering
- [ ] List rendering with keys
- [ ] Form handling
- [ ] Event handling

---

## 🎯 Challenges (Optional)

1. **Drag and Drop** - Reorder todos by dragging
2. **Undo/Redo** - Add history functionality
3. **Export/Import** - JSON export and import
4. **Subtasks** - Nested todos
5. **Tags** - Multiple tags per todo
6. **Dark Mode** - Theme toggle
7. **Animations** - Add transitions
8. **Keyboard Shortcuts** - Quick actions

---

## 📝 Reflection

What I learned this week:
```

_______________________________________________

_______________________________________________

_______________________________________________
```

Challenges I faced:
```

_______________________________________________

_______________________________________________

_______________________________________________
```

---

**Previous:** [Day 6 - Hooks Deep Dive](../day-06/README.md)  
**Next:** [Week 2 - Day 8 - Rendering Behavior](../../week-2-advanced/day-08/README.md)

---

## 🎉 Week 1 Complete!

Congratulations! You've completed Week 1 of the React Mastery Plan. You now have a solid understanding of:

- React fundamentals and Virtual DOM
- JSX and rendering
- Component patterns and composition
- State management with hooks
- Side effects with useEffect
- Advanced hooks (useMemo, useCallback, useReducer)
- Custom hooks
- Building a complete application

**Next week:** Advanced React & Performance!
