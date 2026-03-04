# Day 1: Testing Fundamentals & Philosophy

## 📚 Topics to Cover (3-4 hours)

---

## 1. Why Testing Matters

### The Testing Pyramid

```
        /  E2E  \          ← Slow, Expensive, Fewer
       /----------\
      / Integration \      ← Medium speed, Medium count
     /----------------\
    /   Unit Tests      \  ← Fast, Cheap, Many
   /____________________\
```

### Testing Trophy (Kent C. Dodds)

```
        / E2E \
       /-------\
      /Integration\        ← Most value here
     /--------------\
    /   Unit Tests    \
   /___________________\
  /   Static Analysis    \  ← TypeScript, ESLint
 /_______________________\
```

### Key Principle
> "Write tests. Not too many. Mostly integration." — Guillermo Rauch

---

## 2. Types of Tests

### Unit Tests
- Test individual functions/methods in isolation
- Mock all external dependencies
- Fast execution (ms per test)
- High count in test suite

```javascript
// Example: Pure function unit test
function calculateDiscount(price, percentage) {
  if (price < 0 || percentage < 0) throw new Error('Invalid input');
  return price * (percentage / 100);
}

// Jest test
describe('calculateDiscount', () => {
  it('should calculate discount correctly', () => {
    expect(calculateDiscount(100, 10)).toBe(10);
  });

  it('should handle zero percentage', () => {
    expect(calculateDiscount(100, 0)).toBe(0);
  });

  it('should throw for negative price', () => {
    expect(() => calculateDiscount(-100, 10)).toThrow('Invalid input');
  });
});
```

### Integration Tests
- Test how modules work together
- May use real database connections
- Medium execution speed
- Highest ROI per test

```javascript
// Example: API integration test
describe('POST /api/users', () => {
  it('should create user and return 201', async () => {
    const response = await request(app)
      .post('/api/users')
      .send({ name: 'John', email: 'john@test.com' });
    
    expect(response.status).toBe(201);
    expect(response.body.name).toBe('John');
    
    // Verify in database
    const user = await User.findOne({ email: 'john@test.com' });
    expect(user).toBeTruthy();
  });
});
```

### E2E Tests
- Test complete user workflows
- Run in real browser environment
- Slowest execution
- Catch integration bugs

```javascript
// Cypress E2E example
describe('User Login Flow', () => {
  it('should login and redirect to dashboard', () => {
    cy.visit('/login');
    cy.get('[data-testid="email"]').type('user@test.com');
    cy.get('[data-testid="password"]').type('password123');
    cy.get('[data-testid="submit"]').click();
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid="welcome"]').should('contain', 'Welcome');
  });
});
```

---

## 3. Testing Principles (FIRST)

| Principle | Meaning |
|-----------|---------|
| **F**ast | Tests should run quickly |
| **I**ndependent | Tests shouldn't depend on each other |
| **R**epeatable | Same result every time |
| **S**elf-validating | Pass or fail, no manual checking |
| **T**imely | Written close to production code |

---

## 4. Test-Driven Development (TDD)

### Red-Green-Refactor Cycle

```
1. RED    → Write a failing test
2. GREEN  → Write minimum code to pass
3. REFACTOR → Clean up code, keep tests green
```

### TDD Example

```javascript
// Step 1: RED - Write failing test
describe('Stack', () => {
  it('should push and pop elements', () => {
    const stack = new Stack();
    stack.push(1);
    stack.push(2);
    expect(stack.pop()).toBe(2);
    expect(stack.pop()).toBe(1);
  });

  it('should throw when popping empty stack', () => {
    const stack = new Stack();
    expect(() => stack.pop()).toThrow('Stack is empty');
  });

  it('should return correct size', () => {
    const stack = new Stack();
    expect(stack.size()).toBe(0);
    stack.push(1);
    expect(stack.size()).toBe(1);
  });
});

// Step 2: GREEN - Implement
class Stack {
  #items = [];

  push(item) {
    this.#items.push(item);
  }

  pop() {
    if (this.#items.length === 0) throw new Error('Stack is empty');
    return this.#items.pop();
  }

  size() {
    return this.#items.length;
  }
}
```

---

## 5. Behavior-Driven Development (BDD)

### Gherkin Syntax

```gherkin
Feature: User Authentication
  As a registered user
  I want to log into my account
  So that I can access my dashboard

  Scenario: Successful login
    Given I am on the login page
    When I enter valid credentials
    And I click the login button
    Then I should be redirected to the dashboard
    And I should see a welcome message

  Scenario: Failed login with wrong password
    Given I am on the login page
    When I enter an invalid password
    And I click the login button
    Then I should see an error message
    And I should remain on the login page
```

---

## 6. Arrange-Act-Assert (AAA) Pattern

```javascript
describe('UserService', () => {
  it('should return user by ID', async () => {
    // Arrange
    const mockUser = { id: 1, name: 'John', email: 'john@test.com' };
    const userRepo = { findById: jest.fn().mockResolvedValue(mockUser) };
    const service = new UserService(userRepo);

    // Act
    const result = await service.getUserById(1);

    // Assert
    expect(result).toEqual(mockUser);
    expect(userRepo.findById).toHaveBeenCalledWith(1);
  });
});
```

---

## 7. Test Doubles

| Type | Purpose | Example |
|------|---------|---------|
| **Dummy** | Fill parameter lists | Empty object passed but never used |
| **Stub** | Provide canned answers | `jest.fn().mockReturnValue(42)` |
| **Spy** | Record calls for verification | `jest.spyOn(obj, 'method')` |
| **Mock** | Pre-programmed expectations | `jest.mock('./module')` |
| **Fake** | Working implementation (simplified) | In-memory database |

```javascript
// Stub
const getUser = jest.fn().mockResolvedValue({ id: 1, name: 'John' });

// Spy
const consoleSpy = jest.spyOn(console, 'log');
doSomething();
expect(consoleSpy).toHaveBeenCalledWith('expected message');

// Mock module
jest.mock('./emailService', () => ({
  sendEmail: jest.fn().mockResolvedValue(true),
}));
```

---

## 8. What Makes a Good Test?

### ✅ Good Test Characteristics
- Tests behavior, not implementation
- Has clear, descriptive name
- Tests one thing
- Is deterministic
- Is fast
- Doesn't depend on other tests

### ❌ Anti-Patterns
- Testing implementation details
- Tightly coupled to code structure
- Flaky tests (pass/fail randomly)
- Slow tests blocking CI
- Testing framework code
- Over-mocking

---

## 🎯 Interview Questions

### Q1: What is the testing pyramid? Why is it important?
**A:** The testing pyramid suggests having many unit tests (fast, cheap), fewer integration tests, and even fewer E2E tests. It optimizes for fast feedback while ensuring coverage. Modern approaches like the "testing trophy" emphasize integration tests for best ROI.

### Q2: TDD vs BDD — What's the difference?
**A:** TDD is developer-focused (test-first for code units). BDD extends TDD with business-readable specifications using Given-When-Then format. TDD = technical correctness, BDD = business behavior verification.

### Q3: When should you use mocks vs real dependencies?
**A:** Mock external services (APIs, email, payment), slow resources (network, file system), and non-deterministic code (random, time). Use real dependencies for database (use test DB), internal modules, and integration boundaries.

### Q4: How do you handle flaky tests?
**A:** Identify root causes (timing, shared state, external deps). Strategies: retry logic, deterministic test data, proper cleanup, isolated test environments, avoid sleep/timeouts in favor of polling.

### Q5: What is code coverage? What's a good target?
**A:** Code coverage measures % of code executed during tests. Types: line, branch, function, statement coverage. 80% is a good target, but 100% doesn't guarantee bug-free code. Focus on critical path coverage.

---

## 📝 Practice Exercises

1. Write unit tests for a `Calculator` class with add, subtract, multiply, divide
2. Implement a `StringValidator` using TDD (email, URL, phone validation)
3. Write tests for an async `fetchUser` function with error handling
4. Create a test suite with proper setup/teardown using beforeEach/afterEach

---

## 📖 Resources
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Testing Library Principles](https://testing-library.com/docs/)
- [Martin Fowler - Testing Pyramid](https://martinfowler.com/articles/practical-test-pyramid.html)
