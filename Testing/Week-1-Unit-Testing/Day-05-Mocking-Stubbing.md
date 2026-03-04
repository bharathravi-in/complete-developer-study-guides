# Day 5: Mocking & Stubbing – Advanced Patterns

## 📚 Topics to Cover (3-4 hours)

---

## 1. Why Mock?

### The Dependency Problem

```
┌─────────────┐     ┌─────────────┐     ┌──────────┐
│  Your Code  │ ──→ │  Database   │ ──→ │  Network  │
└─────────────┘     └─────────────┘     └──────────┘
       │                                       │
       └──→ ┌─────────────┐     ┌─────────────┘
            │  File System │     │  External API
            └─────────────┘     └─────────────┘
```

**Mock when:**
- External services (APIs, databases, file system)
- Non-deterministic code (random, Date, timers)
- Slow operations (network, heavy computation)
- Side effects (emails, payments, logging)

**Don't mock:**
- Pure functions
- Simple utility code
- Data structures
- Value objects

---

## 2. JavaScript/TypeScript Mocking Patterns

### Dependency Injection Pattern (Best Practice)

```typescript
// Production code - accepts dependencies
class OrderService {
  constructor(
    private paymentGateway: PaymentGateway,
    private emailService: EmailService,
    private orderRepo: OrderRepository
  ) {}

  async placeOrder(order: Order): Promise<OrderResult> {
    const payment = await this.paymentGateway.charge(order.total);
    if (!payment.success) throw new Error('Payment failed');
    
    const saved = await this.orderRepo.save({ ...order, paymentId: payment.id });
    await this.emailService.sendConfirmation(order.email, saved.id);
    
    return { orderId: saved.id, status: 'confirmed' };
  }
}

// Test - inject mocks
describe('OrderService.placeOrder', () => {
  let service: OrderService;
  let mockPayment: jest.Mocked<PaymentGateway>;
  let mockEmail: jest.Mocked<EmailService>;
  let mockRepo: jest.Mocked<OrderRepository>;

  beforeEach(() => {
    mockPayment = {
      charge: jest.fn().mockResolvedValue({ success: true, id: 'pay_123' }),
    } as any;
    mockEmail = {
      sendConfirmation: jest.fn().mockResolvedValue(true),
    } as any;
    mockRepo = {
      save: jest.fn().mockResolvedValue({ id: 'ord_456', paymentId: 'pay_123' }),
    } as any;

    service = new OrderService(mockPayment, mockEmail, mockRepo);
  });

  it('should process order successfully', async () => {
    const order = { email: 'user@test.com', total: 99.99, items: [] };
    const result = await service.placeOrder(order);

    expect(result.status).toBe('confirmed');
    expect(mockPayment.charge).toHaveBeenCalledWith(99.99);
    expect(mockRepo.save).toHaveBeenCalledWith(
      expect.objectContaining({ paymentId: 'pay_123' })
    );
    expect(mockEmail.sendConfirmation).toHaveBeenCalledWith('user@test.com', 'ord_456');
  });

  it('should throw when payment fails', async () => {
    mockPayment.charge.mockResolvedValue({ success: false, id: null });
    
    await expect(service.placeOrder({ total: 10 } as any))
      .rejects.toThrow('Payment failed');
    
    expect(mockRepo.save).not.toHaveBeenCalled();
    expect(mockEmail.sendConfirmation).not.toHaveBeenCalled();
  });
});
```

### Module Mocking

```typescript
// Mock entire module
jest.mock('../services/analytics', () => ({
  trackEvent: jest.fn(),
  trackPageView: jest.fn(),
  identify: jest.fn(),
}));

// Mock with factory (resets each test)
jest.mock('../config', () => ({
  getConfig: jest.fn(() => ({
    apiUrl: 'http://test-api.com',
    timeout: 5000,
  })),
}));

// Dynamic mock per test
import { getConfig } from '../config';
const mockGetConfig = getConfig as jest.Mock;

it('should use custom timeout', () => {
  mockGetConfig.mockReturnValue({ timeout: 10000 });
  // test with 10s timeout
});
```

---

## 3. Python Mocking Patterns

### patch Decorator & Context Manager

```python
from unittest.mock import patch, MagicMock, PropertyMock, call

# Decorator style
@patch('myapp.services.requests.get')
@patch('myapp.services.db.save')
def test_fetch_and_save(mock_save, mock_get):
    # Note: decorators are applied bottom-up, so args are inner-first
    mock_get.return_value.json.return_value = {"data": [1, 2, 3]}
    mock_get.return_value.status_code = 200
    mock_save.return_value = True
    
    result = fetch_and_save_data()
    
    mock_get.assert_called_once_with("https://api.example.com/data")
    mock_save.assert_called_once_with([1, 2, 3])
    assert result is True

# Context manager style
def test_with_context():
    with patch('myapp.services.cache.get') as mock_cache:
        mock_cache.return_value = None  # Cache miss
        result = get_user_with_cache(1)
        mock_cache.assert_called_with('user:1')

# patch.object for specific instance
def test_instance_method():
    user_service = UserService()
    with patch.object(user_service, 'validate', return_value=True):
        result = user_service.create_user({"name": "John"})
        assert result is not None
```

### MagicMock & Spec

```python
# MagicMock with spec ensures only real methods can be called
mock_user = MagicMock(spec=User)
mock_user.name = "John"
mock_user.save.return_value = True

# This would raise AttributeError because User has no 'fly' method
# mock_user.fly()  # AttributeError!

# Property mocking
with patch.object(type(instance), 'property_name', new_callable=PropertyMock) as mock_prop:
    mock_prop.return_value = "mocked value"
    assert instance.property_name == "mocked value"

# Call tracking
mock = MagicMock()
mock(1, key='value')
mock(2, key='other')

mock.assert_any_call(1, key='value')
assert mock.call_count == 2
assert mock.call_args_list == [
    call(1, key='value'),
    call(2, key='other'),
]
```

---

## 4. Angular Mocking Patterns

### Service Mocking with SpyObj

```typescript
describe('ProductComponent', () => {
  let component: ProductComponent;
  let fixture: ComponentFixture<ProductComponent>;
  let productService: jasmine.SpyObj<ProductService>;
  let router: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    productService = jasmine.createSpyObj('ProductService', 
      ['getProducts', 'deleteProduct'],
      { products$: new BehaviorSubject([]) }  // properties
    );
    router = jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      declarations: [ProductComponent],
      providers: [
        { provide: ProductService, useValue: productService },
        { provide: Router, useValue: router }
      ]
    }).compileComponents();
  });

  it('should navigate on delete', async () => {
    productService.deleteProduct.and.returnValue(of(true));
    
    component.delete('prod_1');
    
    expect(productService.deleteProduct).toHaveBeenCalledWith('prod_1');
    expect(router.navigate).toHaveBeenCalledWith(['/products']);
  });
});
```

### HTTP Mock with HttpTestingController

```typescript
it('should retry failed requests', () => {
  service.getDataWithRetry().subscribe(data => {
    expect(data).toEqual({ result: 'success' });
  });

  // First request fails
  const req1 = httpMock.expectOne('/api/data');
  req1.flush('Error', { status: 500, statusText: 'Server Error' });

  // Retry succeeds
  const req2 = httpMock.expectOne('/api/data');
  req2.flush({ result: 'success' });

  httpMock.verify();
});
```

---

## 5. React Testing Library – Component Mocking

```jsx
// Mock child component
jest.mock('./ChildComponent', () => {
  return function MockChild(props) {
    return <div data-testid="mock-child">{props.title}</div>;
  };
});

// Mock hooks
jest.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    user: { id: 1, name: 'John' },
    isAuthenticated: true,
    login: jest.fn(),
    logout: jest.fn(),
  }),
}));

// Mock context
const mockContext = {
  theme: 'dark',
  toggleTheme: jest.fn(),
};

render(
  <ThemeContext.Provider value={mockContext}>
    <ThemedComponent />
  </ThemeContext.Provider>
);
```

---

## 6. Advanced Mocking Patterns

### Fake Implementations

```typescript
// In-memory database fake
class FakeUserRepository implements UserRepository {
  private users: Map<string, User> = new Map();

  async findById(id: string): Promise<User | null> {
    return this.users.get(id) || null;
  }

  async save(user: User): Promise<User> {
    this.users.set(user.id, user);
    return user;
  }

  async delete(id: string): Promise<boolean> {
    return this.users.delete(id);
  }

  // Test helper
  seed(users: User[]) {
    users.forEach(u => this.users.set(u.id, u));
  }
}
```

### Network Mocking (MSW - Mock Service Worker)

```typescript
import { setupServer } from 'msw/node';
import { rest } from 'msw';

const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(ctx.json([{ id: 1, name: 'John' }]));
  }),
  rest.post('/api/users', (req, res, ctx) => {
    return res(ctx.status(201), ctx.json({ id: 2, ...req.body }));
  }),
  rest.get('/api/users/:id', (req, res, ctx) => {
    if (req.params.id === '404') {
      return res(ctx.status(404));
    }
    return res(ctx.json({ id: req.params.id, name: 'John' }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// Override for specific test
it('should handle server error', async () => {
  server.use(
    rest.get('/api/users', (req, res, ctx) => {
      return res(ctx.status(500));
    })
  );
  // Test error handling...
});
```

---

## 🎯 Interview Questions

### Q1: What's the difference between mocks, stubs, fakes, and spies?
**A:** **Stub**: Returns canned data, no verification. **Mock**: Pre-programmed with expectations, verifies interactions. **Spy**: Wraps real implementation, records calls. **Fake**: Working simplified implementation (e.g., in-memory DB). In practice, modern frameworks blur these lines.

### Q2: What is "over-mocking" and why is it bad?
**A:** Over-mocking means mocking too many dependencies, making tests pass even when real code is broken. Tests become coupled to implementation, not behavior. They pass even when logic changes, creating false confidence. Prefer integration tests with minimal mocking.

### Q3: Explain the "Don't mock what you don't own" principle
**A:** Don't mock third-party libraries directly. Instead, create your own wrapper/adapter and mock that. This isolates your code from library changes and makes mocks reflect your domain language.

---

## 📝 Practice Exercises

1. Implement a full mock of a payment service with success/failure/timeout scenarios
2. Create a fake in-memory repository and test CRUD operations against it
3. Use MSW to mock a complete REST API and test a React component
4. Mock a WebSocket connection and test real-time updates
