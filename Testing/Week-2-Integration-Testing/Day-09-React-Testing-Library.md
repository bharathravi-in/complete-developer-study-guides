# Day 9: React Testing Library – Component Testing

## 📚 Topics to Cover (3-4 hours)

---

## 1. React Testing Library Philosophy

> "The more your tests resemble the way your software is used, the more confidence they can give you."

### Core Principles
- Test **behavior**, not implementation
- Query by **accessibility roles** (what users see)
- Avoid testing internal state
- Fire real events, not synthetic ones

---

## 2. Setup

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

```typescript
// jest.setup.ts
import '@testing-library/jest-dom';
```

---

## 3. Queries (Priority Order)

```typescript
import { render, screen } from '@testing-library/react';

// 1. getByRole (BEST - accessibility-first)
screen.getByRole('button', { name: /submit/i });
screen.getByRole('heading', { level: 1 });
screen.getByRole('textbox', { name: /email/i });
screen.getByRole('checkbox');
screen.getByRole('link', { name: /home/i });

// 2. getByLabelText (forms)
screen.getByLabelText(/email address/i);

// 3. getByPlaceholderText
screen.getByPlaceholderText(/enter your name/i);

// 4. getByText (non-interactive elements)
screen.getByText(/welcome back/i);
screen.getByText((content, element) => {
  return element.tagName === 'SPAN' && content.startsWith('Hello');
});

// 5. getByDisplayValue (current form values)
screen.getByDisplayValue('current@email.com');

// 6. getByAltText (images)
screen.getByAltText(/company logo/i);

// 7. getByTestId (last resort)
screen.getByTestId('custom-element');

// Query variants:
// getBy*    → throws if not found (synchronous)
// queryBy*  → returns null if not found (synchronous)
// findBy*   → returns promise, waits for element (async)
// getAllBy* → returns array, throws if empty
```

---

## 4. User Interactions

```typescript
import userEvent from '@testing-library/user-event';

describe('LoginForm', () => {
  it('should submit with valid credentials', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn();
    
    render(<LoginForm onSubmit={onSubmit} />);

    // Type in inputs
    await user.type(screen.getByLabelText(/email/i), 'john@test.com');
    await user.type(screen.getByLabelText(/password/i), 'Password123!');

    // Click submit
    await user.click(screen.getByRole('button', { name: /log in/i }));

    expect(onSubmit).toHaveBeenCalledWith({
      email: 'john@test.com',
      password: 'Password123!',
    });
  });

  it('should show validation errors', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={jest.fn()} />);

    // Submit without filling
    await user.click(screen.getByRole('button', { name: /log in/i }));

    expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    expect(screen.getByText(/password is required/i)).toBeInTheDocument();
  });
});

// More interactions
await user.clear(input);
await user.selectOptions(select, ['option1']);
await user.upload(fileInput, file);
await user.hover(element);
await user.keyboard('{Enter}');
await user.tab();
await user.dblClick(element);
```

---

## 5. Testing Async Components

```typescript
import { render, screen, waitFor, waitForElementToBeRemoved } from '@testing-library/react';

describe('UserList', () => {
  it('should show loading then users', async () => {
    render(<UserList />);

    // Loading state
    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    // Wait for data
    const users = await screen.findAllByRole('listitem');
    expect(users).toHaveLength(3);

    // Loading should be gone
    expect(screen.queryByText(/loading/i)).not.toBeInTheDocument();
  });

  it('should show error on failure', async () => {
    server.use(
      rest.get('/api/users', (req, res, ctx) => res(ctx.status(500)))
    );

    render(<UserList />);

    await waitFor(() => {
      expect(screen.getByText(/error loading users/i)).toBeInTheDocument();
    });
  });

  it('should remove loading spinner', async () => {
    render(<UserList />);
    await waitForElementToBeRemoved(() => screen.queryByText(/loading/i));
  });
});
```

---

## 6. Testing Hooks

```typescript
import { renderHook, act } from '@testing-library/react';

describe('useCounter', () => {
  it('should initialize with default value', () => {
    const { result } = renderHook(() => useCounter(0));
    expect(result.current.count).toBe(0);
  });

  it('should increment', () => {
    const { result } = renderHook(() => useCounter(0));
    act(() => { result.current.increment(); });
    expect(result.current.count).toBe(1);
  });

  it('should accept initial value', () => {
    const { result } = renderHook(() => useCounter(10));
    expect(result.current.count).toBe(10);
  });
});

// Testing hooks with context
describe('useAuth', () => {
  const wrapper = ({ children }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  it('should provide auth state', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('should login user', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await act(async () => {
      await result.current.login('user@test.com', 'password');
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user.email).toBe('user@test.com');
  });
});
```

---

## 7. Testing with Redux/Context

```typescript
// Custom render with providers
function renderWithProviders(
  ui: React.ReactElement,
  { preloadedState = {}, store = configureStore({ reducer, preloadedState }), ...options } = {}
) {
  function Wrapper({ children }) {
    return <Provider store={store}>{children}</Provider>;
  }
  return { store, ...render(ui, { wrapper: Wrapper, ...options }) };
}

describe('ProductList with Redux', () => {
  it('should display products from store', () => {
    const preloadedState = {
      products: {
        items: [
          { id: 1, name: 'Widget', price: 9.99 },
          { id: 2, name: 'Gadget', price: 19.99 },
        ],
        loading: false,
      },
    };

    renderWithProviders(<ProductList />, { preloadedState });
    
    expect(screen.getByText('Widget')).toBeInTheDocument();
    expect(screen.getByText('Gadget')).toBeInTheDocument();
  });

  it('should dispatch addToCart action', async () => {
    const user = userEvent.setup();
    const { store } = renderWithProviders(<ProductList />, { preloadedState });

    await user.click(screen.getAllByRole('button', { name: /add to cart/i })[0]);

    const state = store.getState();
    expect(state.cart.items).toHaveLength(1);
  });
});
```

---

## 8. Common Assertions (jest-dom)

```typescript
// Visibility
expect(element).toBeVisible();
expect(element).toBeInTheDocument();
expect(element).not.toBeInTheDocument();

// Forms
expect(input).toHaveValue('hello');
expect(input).toBeRequired();
expect(input).toBeDisabled();
expect(input).toBeEnabled();
expect(input).toBeChecked();
expect(form).toBeValid();
expect(form).toBeInvalid();

// Content
expect(element).toHaveTextContent(/hello/i);
expect(element).toBeEmptyDOMElement();

// Styles & Classes
expect(element).toHaveClass('active');
expect(element).toHaveStyle({ display: 'flex' });
expect(element).toHaveAttribute('href', '/home');

// Accessibility
expect(element).toHaveAccessibleDescription('help text');
expect(element).toHaveAccessibleName('Submit');
```

---

## 🎯 Interview Questions

### Q1: Why prefer React Testing Library over Enzyme?
**A:** RTL tests behavior (what users see/do), not implementation. Enzyme encourages testing internals (state, props, instance methods) leading to brittle tests. RTL prevents you from accessing component internals, forcing better test design. RTL is now the React team's recommended approach.

### Q2: What query should you use and in what priority?
**A:** `getByRole` > `getByLabelText` > `getByPlaceholderText` > `getByText` > `getByDisplayValue` > `getByAltText` > `getByTitle` > `getByTestId`. Role-based queries align with accessibility and how users interact with the UI.

### Q3: How do you test components that fetch data?
**A:** Use MSW (Mock Service Worker) to intercept network requests at the service worker level. Then use `findBy*` queries or `waitFor` to assert async content. Avoid mocking fetch/axios directly; MSW provides more realistic testing.

---

## 📝 Practice Exercises

1. Test a todo app (add, complete, delete, filter)
2. Test a multi-step form wizard with validation
3. Test a component with React Router (navigation, params)
4. Test a dashboard with data fetching and loading states
