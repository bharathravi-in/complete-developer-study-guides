# Day 6: TDD & BDD Patterns in Practice

## 📚 Topics to Cover (3-4 hours)

---

## 1. TDD – Test-Driven Development Deep Dive

### The Cycle

```
    ┌──── Write Failing Test (RED) ────┐
    │                                   │
    │    Write Minimum Code (GREEN) ◄───┘
    │           │
    │    Refactor (BLUE)
    │           │
    └───────────┘
```

### TDD Rules (Uncle Bob)
1. You may not write production code unless it makes a failing test pass
2. You may not write more of a test than is sufficient to fail
3. You may not write more production code than is sufficient to pass

### Complete TDD Example: Building a URL Shortener

```typescript
// Step 1: RED - Test basic shortening
describe('UrlShortener', () => {
  let shortener: UrlShortener;

  beforeEach(() => {
    shortener = new UrlShortener();
  });

  it('should shorten a valid URL', () => {
    const result = shortener.shorten('https://example.com/very/long/path');
    expect(result).toBeDefined();
    expect(result.length).toBeLessThan(10);
  });
});

// Step 2: GREEN - Minimal implementation
class UrlShortener {
  shorten(url: string): string {
    return 'abc123';
  }
}

// Step 3: RED - Test URL retrieval
it('should retrieve original URL', () => {
  const short = shortener.shorten('https://example.com/long');
  const original = shortener.resolve(short);
  expect(original).toBe('https://example.com/long');
});

// Step 4: GREEN
class UrlShortener {
  private store = new Map<string, string>();

  shorten(url: string): string {
    const code = Math.random().toString(36).substring(2, 8);
    this.store.set(code, url);
    return code;
  }

  resolve(code: string): string | undefined {
    return this.store.get(code);
  }
}

// Step 5: RED - Test validation
it('should throw for invalid URL', () => {
  expect(() => shortener.shorten('not-a-url')).toThrow('Invalid URL');
});

it('should throw for empty URL', () => {
  expect(() => shortener.shorten('')).toThrow('URL is required');
});

// Step 6: GREEN - Add validation
shorten(url: string): string {
  if (!url) throw new Error('URL is required');
  try { new URL(url); } catch { throw new Error('Invalid URL'); }
  // ... rest
}

// Step 7: RED - Test uniqueness
it('should generate unique codes', () => {
  const codes = new Set<string>();
  for (let i = 0; i < 1000; i++) {
    codes.add(shortener.shorten(`https://example.com/${i}`));
  }
  expect(codes.size).toBe(1000);
});

// Step 8: REFACTOR - Improve code generation
// ... and so on
```

---

## 2. BDD – Behavior-Driven Development

### BDD Principles
- Focus on **behaviors**, not **implementations**
- Write specs in **business language**
- Use **Given-When-Then** format
- Collaborate between devs, QA, and product

### Cucumber.js + Gherkin

```gherkin
# features/shopping-cart.feature
Feature: Shopping Cart
  As a customer
  I want to manage items in my cart
  So that I can purchase products

  Background:
    Given the following products exist:
      | name    | price | stock |
      | Widget  | 9.99  | 100   |
      | Gadget  | 19.99 | 50    |

  Scenario: Add item to empty cart
    Given my cart is empty
    When I add "Widget" to my cart
    Then my cart should contain 1 item
    And the cart total should be $9.99

  Scenario: Add multiple items
    Given my cart is empty
    When I add "Widget" to my cart
    And I add "Gadget" to my cart
    Then my cart should contain 2 items
    And the cart total should be $29.98

  Scenario: Remove item from cart
    Given my cart contains "Widget"
    When I remove "Widget" from my cart
    Then my cart should be empty

  Scenario Outline: Quantity limits
    Given my cart is empty
    When I add <quantity> of "<product>" to my cart
    Then I should see "<message>"

    Examples:
      | quantity | product | message                |
      | 1        | Widget  | Added to cart          |
      | 0        | Widget  | Quantity must be > 0   |
      | 101      | Widget  | Exceeds available stock|
```

### Step Definitions

```typescript
// features/step-definitions/cart.steps.ts
import { Given, When, Then } from '@cucumber/cucumber';
import { expect } from 'chai';

let cart: ShoppingCart;

Given('my cart is empty', () => {
  cart = new ShoppingCart();
});

Given('my cart contains {string}', (product: string) => {
  cart = new ShoppingCart();
  cart.add(product, 1);
});

When('I add {string} to my cart', (product: string) => {
  cart.add(product, 1);
});

When('I remove {string} from my cart', (product: string) => {
  cart.remove(product);
});

Then('my cart should contain {int} item(s)', (count: number) => {
  expect(cart.itemCount).to.equal(count);
});

Then('the cart total should be ${float}', (total: number) => {
  expect(cart.total).to.be.closeTo(total, 0.01);
});

Then('my cart should be empty', () => {
  expect(cart.isEmpty).to.be.true;
});
```

---

## 3. BDD in Jest (describe/it as BDD)

```typescript
// Jest naturally supports BDD-style
describe('ShoppingCart', () => {
  describe('when cart is empty', () => {
    it('should have zero items', () => {
      const cart = new ShoppingCart();
      expect(cart.itemCount).toBe(0);
    });

    it('should have zero total', () => {
      const cart = new ShoppingCart();
      expect(cart.total).toBe(0);
    });
  });

  describe('when adding an item', () => {
    it('should increase item count by 1', () => {
      const cart = new ShoppingCart();
      cart.add({ name: 'Widget', price: 9.99 });
      expect(cart.itemCount).toBe(1);
    });

    it('should update the total', () => {
      const cart = new ShoppingCart();
      cart.add({ name: 'Widget', price: 9.99 });
      expect(cart.total).toBeCloseTo(9.99);
    });
  });

  describe('when applying discount', () => {
    it('should reduce total by percentage', () => {
      const cart = new ShoppingCart();
      cart.add({ name: 'Widget', price: 100 });
      cart.applyDiscount(10); // 10%
      expect(cart.total).toBe(90);
    });

    it('should not allow negative discount', () => {
      const cart = new ShoppingCart();
      expect(() => cart.applyDiscount(-10)).toThrow();
    });
  });
});
```

---

## 4. TDD vs BDD Comparison

| Aspect | TDD | BDD |
|--------|-----|-----|
| Focus | Code correctness | Business behavior |
| Language | Technical | Business-readable |
| Audience | Developers | Dev + QA + Product |
| Syntax | describe/it/expect | Given/When/Then |
| Scope | Unit level | Feature level |
| Tools | Jest, Pytest, JUnit | Cucumber, SpecFlow |
| Speed | Fast (unit) | Slower (integration) |
| Maintenance | Lower | Higher (feature files) |

### When to Use What?
- **TDD**: Business logic, algorithms, utilities, services
- **BDD**: User-facing features, acceptance criteria, API contracts
- **Both**: Complex features (BDD for acceptance, TDD for implementation)

---

## 5. Outside-In TDD (London School)

```
1. Start with acceptance test (outer boundary) → RED
2. Implement outer component, mock inner dependencies
3. Write unit test for next inner component → RED
4. Implement inner component
5. Continue inward until all tests pass
```

### Example: Login Feature

```typescript
// Step 1: E2E / Acceptance test
describe('Login Feature', () => {
  it('should redirect to dashboard after successful login', async () => {
    // This drives the entire feature
    const page = await visit('/login');
    await page.fill('[data-testid="email"]', 'user@test.com');
    await page.fill('[data-testid="password"]', 'password');
    await page.click('[data-testid="submit"]');
    expect(page.url()).toContain('/dashboard');
  });
});

// Step 2: Component test (mock service)
describe('LoginComponent', () => {
  it('should call auth service on submit', () => {
    const mockAuth = { login: jest.fn().mockResolvedValue({ token: 'abc' }) };
    // ... render with mock, fill form, submit
    expect(mockAuth.login).toHaveBeenCalledWith('user@test.com', 'password');
  });
});

// Step 3: Service test (mock HTTP)
describe('AuthService', () => {
  it('should POST to /api/auth/login', async () => {
    // ... mock HTTP, test service
  });
});
```

---

## 🎯 Interview Questions

### Q1: When would you choose TDD over BDD?
**A:** TDD for internal logic (algorithms, data processing, utility functions) where the audience is developers. BDD when acceptance criteria come from product/business stakeholders and you need shared understanding in natural language.

### Q2: What are the benefits of TDD?
**A:** Forces minimal design (YAGNI), creates regression safety net, documents code behavior, faster debugging (tests pinpoint failures), encourages loose coupling via dependency injection, higher test coverage naturally.

### Q3: How do you handle legacy code without tests?
**A:** Use "characterization tests" — write tests that capture current behavior (even if buggy). Then refactor safely. Michael Feathers' approach: identify seams, break dependencies, add tests incrementally.

---

## 📝 Practice Exercises

1. Build a `Calculator` class using strict TDD (Red-Green-Refactor)
2. Write Gherkin features for a user registration flow
3. Implement Outside-In TDD for a todo list API
4. Convert existing untested code to TDD with characterization tests
