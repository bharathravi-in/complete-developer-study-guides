# 📅 Day 14 – Testing

## 🎯 Learning Goals
- Master Jest fundamentals
- Learn React Testing Library
- Understand Vitest
- Get started with Cypress

---

## 📚 Theory

### Jest Basics

```tsx
// Jest is a testing framework

// Basic test structure
describe('Calculator', () => {
  // Setup before each test
  beforeEach(() => {
    // Reset state
  });

  // Cleanup after each test
  afterEach(() => {
    // Cleanup
  });

  test('adds two numbers', () => {
    expect(add(1, 2)).toBe(3);
  });

  it('subtracts two numbers', () => {
    expect(subtract(5, 2)).toBe(3);
  });
});

// Common matchers
expect(value).toBe(3);              // Exact equality
expect(value).toEqual({ a: 1 });    // Deep equality
expect(value).toBeTruthy();         // Truthy
expect(value).toBeFalsy();          // Falsy
expect(value).toBeNull();           // null
expect(value).toBeUndefined();      // undefined
expect(value).toBeDefined();        // not undefined
expect(value).toContain('item');    // Array/string contains
expect(value).toHaveLength(3);      // Length
expect(fn).toThrow();               // Throws error
expect(fn).toHaveBeenCalled();      // Function was called
expect(fn).toHaveBeenCalledWith(1); // Called with args

// Async tests
test('async operation', async () => {
  const data = await fetchData();
  expect(data).toBeDefined();
});

test('promise resolves', () => {
  return expect(fetchData()).resolves.toEqual({ id: 1 });
});

// Mocking
const mockFn = jest.fn();
mockFn.mockReturnValue(42);
mockFn.mockResolvedValue({ data: [] });
mockFn.mockImplementation((x) => x * 2);

// Mock modules
jest.mock('./api', () => ({
  fetchUser: jest.fn().mockResolvedValue({ id: 1, name: 'John' }),
}));
```

### React Testing Library (RTL)

```tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Basic rendering
test('renders welcome message', () => {
  render(<Welcome name="John" />);
  
  // Query elements
  expect(screen.getByText('Hello, John!')).toBeInTheDocument();
});

// Query methods priority (prefer accessible queries):
// 1. getByRole - most accessible
// 2. getByLabelText - form fields
// 3. getByPlaceholderText
// 4. getByText - non-interactive
// 5. getByDisplayValue - form values
// 6. getByAltText - images
// 7. getByTitle
// 8. getByTestId - last resort

// Query variants:
// getBy - throws if not found (synchronous)
// queryBy - returns null if not found (synchronous)
// findBy - returns promise, waits for element (async)
// getAllBy, queryAllBy, findAllBy - multiple elements

// Example queries
screen.getByRole('button', { name: /submit/i });
screen.getByLabelText('Email');
screen.getByPlaceholderText('Enter your name');
screen.getByText(/welcome/i);
screen.getByTestId('custom-element');

// User interactions with userEvent (preferred over fireEvent)
test('form submission', async () => {
  const user = userEvent.setup();
  const handleSubmit = jest.fn();
  
  render(<LoginForm onSubmit={handleSubmit} />);
  
  // Type in inputs
  await user.type(screen.getByLabelText('Email'), 'test@example.com');
  await user.type(screen.getByLabelText('Password'), 'password123');
  
  // Click button
  await user.click(screen.getByRole('button', { name: /submit/i }));
  
  expect(handleSubmit).toHaveBeenCalledWith({
    email: 'test@example.com',
    password: 'password123',
  });
});

// Async operations
test('loads and displays data', async () => {
  render(<UserProfile userId="1" />);
  
  // Wait for loading to finish
  expect(screen.getByText('Loading...')).toBeInTheDocument();
  
  // Wait for data to appear
  await waitFor(() => {
    expect(screen.getByText('John Doe')).toBeInTheDocument();
  });
  
  // Or use findBy (combines getBy + waitFor)
  expect(await screen.findByText('John Doe')).toBeInTheDocument();
});

// Testing with context/providers
const customRender = (ui: ReactElement, options?: RenderOptions) => {
  const AllProviders = ({ children }: { children: ReactNode }) => (
    <ThemeProvider>
      <AuthProvider>
        {children}
      </AuthProvider>
    </ThemeProvider>
  );
  
  return render(ui, { wrapper: AllProviders, ...options });
};

test('with providers', () => {
  customRender(<MyComponent />);
  // ...
});
```

### Testing Patterns

```tsx
// Testing hooks
import { renderHook, act } from '@testing-library/react';

test('useCounter hook', () => {
  const { result } = renderHook(() => useCounter(0));
  
  expect(result.current.count).toBe(0);
  
  act(() => {
    result.current.increment();
  });
  
  expect(result.current.count).toBe(1);
});

// Testing with router
import { MemoryRouter } from 'react-router-dom';

test('navigates on click', async () => {
  const user = userEvent.setup();
  
  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>
  );
  
  await user.click(screen.getByRole('link', { name: /about/i }));
  
  expect(screen.getByText('About Page')).toBeInTheDocument();
});

// Testing with Redux
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';

function renderWithRedux(
  ui: ReactElement,
  { preloadedState = {}, store = configureStore({ reducer, preloadedState }) } = {}
) {
  return {
    ...render(<Provider store={store}>{ui}</Provider>),
    store,
  };
}

test('displays count from store', () => {
  renderWithRedux(<Counter />, {
    preloadedState: { counter: { value: 10 } },
  });
  
  expect(screen.getByText('Count: 10')).toBeInTheDocument();
});

// Mocking API calls
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/users/:id', (req, res, ctx) => {
    return res(ctx.json({ id: req.params.id, name: 'John' }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

test('fetches user data', async () => {
  render(<UserProfile userId="1" />);
  
  expect(await screen.findByText('John')).toBeInTheDocument();
});
```

### Vitest

```tsx
// Vitest - Vite-native testing framework (Jest compatible API)

// vite.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/setupTests.ts',
  },
});

// Tests look the same as Jest!
import { describe, test, expect, vi } from 'vitest';

describe('Component', () => {
  test('renders correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});

// Mocking with vi instead of jest
const mockFn = vi.fn();
vi.mock('./api');
vi.spyOn(object, 'method');

// Benefits over Jest:
// - Faster (uses Vite's bundling)
// - ESM first
// - Same config as Vite
// - Compatible with Jest API
```

### Cypress Basics

```tsx
// Cypress - E2E testing

// cypress/e2e/login.cy.ts
describe('Login Flow', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('displays login form', () => {
    cy.get('input[name="email"]').should('be.visible');
    cy.get('input[name="password"]').should('be.visible');
    cy.get('button[type="submit"]').should('contain', 'Login');
  });

  it('logs in successfully', () => {
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    
    // Should redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.get('h1').should('contain', 'Welcome');
  });

  it('shows error for invalid credentials', () => {
    cy.get('input[name="email"]').type('wrong@example.com');
    cy.get('input[name="password"]').type('wrongpassword');
    cy.get('button[type="submit"]').click();
    
    cy.get('.error-message').should('contain', 'Invalid credentials');
  });
});

// Custom commands
// cypress/support/commands.ts
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.visit('/login');
  cy.get('input[name="email"]').type(email);
  cy.get('input[name="password"]').type(password);
  cy.get('button[type="submit"]').click();
});

// Usage
cy.login('test@example.com', 'password123');

// API mocking
cy.intercept('GET', '/api/users', { fixture: 'users.json' });
cy.intercept('POST', '/api/login', { statusCode: 200, body: { token: 'abc' } });
```

---

## ✅ Task: Test a Small App

```tsx
// Component to test
function TodoApp() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [input, setInput] = useState('');

  const addTodo = () => {
    if (!input.trim()) return;
    setTodos([...todos, { id: Date.now(), text: input, completed: false }]);
    setInput('');
  };

  const toggleTodo = (id: number) => {
    setTodos(todos.map(t => 
      t.id === id ? { ...t, completed: !t.completed } : t
    ));
  };

  return (
    <div>
      <h1>Todo App</h1>
      <input
        value={input}
        onChange={e => setInput(e.target.value)}
        placeholder="Add todo"
        aria-label="Todo input"
      />
      <button onClick={addTodo}>Add</button>
      <ul>
        {todos.map(todo => (
          <li 
            key={todo.id}
            onClick={() => toggleTodo(todo.id)}
            style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}
          >
            {todo.text}
          </li>
        ))}
      </ul>
    </div>
  );
}

// Tests
describe('TodoApp', () => {
  it('renders empty state', () => {
    render(<TodoApp />);
    expect(screen.getByText('Todo App')).toBeInTheDocument();
    expect(screen.getByLabelText('Todo input')).toBeInTheDocument();
  });

  it('adds a new todo', async () => {
    const user = userEvent.setup();
    render(<TodoApp />);
    
    await user.type(screen.getByLabelText('Todo input'), 'Buy milk');
    await user.click(screen.getByRole('button', { name: /add/i }));
    
    expect(screen.getByText('Buy milk')).toBeInTheDocument();
    expect(screen.getByLabelText('Todo input')).toHaveValue('');
  });

  it('does not add empty todo', async () => {
    const user = userEvent.setup();
    render(<TodoApp />);
    
    await user.click(screen.getByRole('button', { name: /add/i }));
    
    expect(screen.queryByRole('listitem')).not.toBeInTheDocument();
  });

  it('toggles todo completion', async () => {
    const user = userEvent.setup();
    render(<TodoApp />);
    
    await user.type(screen.getByLabelText('Todo input'), 'Buy milk');
    await user.click(screen.getByRole('button', { name: /add/i }));
    
    const todo = screen.getByText('Buy milk');
    await user.click(todo);
    
    expect(todo).toHaveStyle({ textDecoration: 'line-through' });
  });
});
```

---

## 🎯 Interview Questions & Answers

### Q1: What is React Testing Library's philosophy?
**Answer:** "Test behavior, not implementation." RTL encourages testing components the way users interact with them, not internal implementation details. Query by role/label (accessibility), simulate user events, assert visible outcomes.

### Q2: getBy vs queryBy vs findBy?
**Answer:**
- **getBy:** Throws if not found (synchronous)
- **queryBy:** Returns null if not found (synchronous)
- **findBy:** Awaits element (async, uses waitFor)

Use queryBy when asserting element doesn't exist.

### Q3: Unit vs Integration vs E2E tests?
**Answer:**
- **Unit:** Test single function/component in isolation
- **Integration:** Test multiple units working together
- **E2E:** Test complete user flows in real browser

Testing trophy: More integration tests, fewer unit/E2E.

---

## ✅ Completion Checklist

- [ ] Understand Jest fundamentals
- [ ] Can use React Testing Library
- [ ] Know Vitest basics
- [ ] Can write Cypress tests
- [ ] Tested a small app

---

**Previous:** [Day 13 - Routing](../day-13/README.md)  
**Next:** [Week 3 - Day 15 - TypeScript](../../week-3-modern/day-15/README.md)

---

## 🎉 Week 2 Complete!

You've mastered Advanced React concepts:
- Rendering behavior & Fiber
- Performance optimization
- Error handling
- Context API
- State management
- Routing
- Testing

**Next week:** Modern React 2026!
