# Day 14: Testing Node.js Applications

## 🎯 Learning Objectives
- Write unit, integration, and e2e tests for Node.js APIs
- Master Jest and Supertest for testing
- Understand mocking, stubbing, and test doubles
- Implement test coverage and CI integration

---

## 📚 Testing Fundamentals

### Test Pyramid

```
        /  E2E Tests  \          ← Few, slow, expensive
       / Integration    \        ← Moderate amount
      /   Unit Tests     \       ← Many, fast, cheap
     ──────────────────────
```

### Jest Setup

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node',
  coverageDirectory: 'coverage',
  collectCoverageFrom: ['src/**/*.js', '!src/**/*.test.js'],
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 }
  },
  setupFilesAfterFramework: ['./tests/setup.js'],
  testMatch: ['**/*.test.js', '**/*.spec.js']
};

// tests/setup.js
beforeAll(async () => {
  // Connect to test database
  await connectTestDB();
});

afterAll(async () => {
  await disconnectTestDB();
});

afterEach(async () => {
  // Clean up test data
  await clearDatabase();
});
```

---

## 🧪 Unit Testing

```javascript
// services/userService.js
class UserService {
  constructor(userRepository, emailService) {
    this.userRepository = userRepository;
    this.emailService = emailService;
  }
  
  async createUser(data) {
    const existing = await this.userRepository.findByEmail(data.email);
    if (existing) throw new ConflictError('Email already registered');
    
    const user = await this.userRepository.create(data);
    await this.emailService.sendWelcome(user.email, user.name);
    return user;
  }
}

// services/userService.test.js
const { UserService } = require('./userService');
const { ConflictError } = require('../utils/errors');

describe('UserService', () => {
  let userService;
  let mockUserRepo;
  let mockEmailService;
  
  beforeEach(() => {
    mockUserRepo = {
      findByEmail: jest.fn(),
      create: jest.fn(),
    };
    mockEmailService = {
      sendWelcome: jest.fn().mockResolvedValue(true),
    };
    userService = new UserService(mockUserRepo, mockEmailService);
  });
  
  describe('createUser', () => {
    const userData = { name: 'Alice', email: 'alice@example.com', password: 'secret123' };
    
    it('should create a user successfully', async () => {
      mockUserRepo.findByEmail.mockResolvedValue(null);
      mockUserRepo.create.mockResolvedValue({ id: '1', ...userData });
      
      const result = await userService.createUser(userData);
      
      expect(result).toMatchObject({ id: '1', name: 'Alice' });
      expect(mockUserRepo.create).toHaveBeenCalledWith(userData);
      expect(mockEmailService.sendWelcome).toHaveBeenCalledWith('alice@example.com', 'Alice');
    });
    
    it('should throw ConflictError if email exists', async () => {
      mockUserRepo.findByEmail.mockResolvedValue({ id: '1', email: 'alice@example.com' });
      
      await expect(userService.createUser(userData)).rejects.toThrow(ConflictError);
      expect(mockUserRepo.create).not.toHaveBeenCalled();
      expect(mockEmailService.sendWelcome).not.toHaveBeenCalled();
    });
    
    it('should propagate errors from repository', async () => {
      mockUserRepo.findByEmail.mockResolvedValue(null);
      mockUserRepo.create.mockRejectedValue(new Error('DB connection lost'));
      
      await expect(userService.createUser(userData)).rejects.toThrow('DB connection lost');
    });
  });
});
```

---

## 🔗 Integration Testing with Supertest

```javascript
const request = require('supertest');
const app = require('../src/app'); // Express app (without .listen())
const { connectDB, disconnectDB, clearDB } = require('./helpers/db');

describe('Users API', () => {
  let authToken;
  
  beforeAll(async () => {
    await connectDB();
    // Create test user and get token
    const res = await request(app)
      .post('/api/auth/register')
      .send({ name: 'Test Admin', email: 'admin@test.com', password: 'password123', role: 'admin' });
    authToken = res.body.accessToken;
  });
  
  afterAll(async () => {
    await disconnectDB();
  });
  
  afterEach(async () => {
    await clearDB(['users']); // Clear specific collections
  });
  
  describe('POST /api/users', () => {
    it('should create a user with valid data', async () => {
      const res = await request(app)
        .post('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ name: 'Alice', email: 'alice@example.com', password: 'password123' });
      
      expect(res.status).toBe(201);
      expect(res.body.data).toMatchObject({
        name: 'Alice',
        email: 'alice@example.com'
      });
      expect(res.body.data).not.toHaveProperty('password');
      expect(res.headers.location).toMatch(/\/api\/users\/.+/);
    });
    
    it('should return 400 for invalid email', async () => {
      const res = await request(app)
        .post('/api/users')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ name: 'Alice', email: 'not-an-email', password: 'password123' });
      
      expect(res.status).toBe(400);
      expect(res.body.error.code).toBe('VALIDATION_ERROR');
    });
    
    it('should return 401 without auth token', async () => {
      const res = await request(app)
        .post('/api/users')
        .send({ name: 'Alice', email: 'alice@example.com', password: 'password123' });
      
      expect(res.status).toBe(401);
    });
    
    it('should return 409 for duplicate email', async () => {
      const userData = { name: 'Alice', email: 'alice@example.com', password: 'password123' };
      
      await request(app).post('/api/users').set('Authorization', `Bearer ${authToken}`).send(userData);
      const res = await request(app).post('/api/users').set('Authorization', `Bearer ${authToken}`).send(userData);
      
      expect(res.status).toBe(409);
    });
  });
  
  describe('GET /api/users', () => {
    it('should return paginated users', async () => {
      // Seed test data
      for (let i = 0; i < 25; i++) {
        await request(app)
          .post('/api/users')
          .set('Authorization', `Bearer ${authToken}`)
          .send({ name: `User ${i}`, email: `user${i}@test.com`, password: 'pass123' });
      }
      
      const res = await request(app)
        .get('/api/users?page=1&limit=10')
        .set('Authorization', `Bearer ${authToken}`);
      
      expect(res.status).toBe(200);
      expect(res.body.data).toHaveLength(10);
      expect(res.body.pagination).toMatchObject({
        page: 1,
        limit: 10,
        total: 25,
        hasNext: true
      });
    });
  });
});
```

---

## 🎭 Mocking Patterns

```javascript
// Mock external services
jest.mock('../services/emailService', () => ({
  sendWelcome: jest.fn().mockResolvedValue(true),
  sendPasswordReset: jest.fn().mockResolvedValue(true),
}));

// Mock modules
jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn(),
}));

// Spy on methods
const spy = jest.spyOn(console, 'error').mockImplementation();
// ... test code that logs errors
expect(spy).toHaveBeenCalledWith(expect.stringContaining('error'));
spy.mockRestore();

// Mock timers
jest.useFakeTimers();
test('debounced function', () => {
  const fn = jest.fn();
  const debounced = debounce(fn, 1000);
  debounced();
  debounced();
  debounced();
  jest.advanceTimersByTime(1000);
  expect(fn).toHaveBeenCalledTimes(1);
});

// Mock database with in-memory alternative
class MockUserRepository {
  constructor() { this.users = []; }
  async create(data) { const user = { id: Date.now().toString(), ...data }; this.users.push(user); return user; }
  async findByEmail(email) { return this.users.find(u => u.email === email); }
  async findById(id) { return this.users.find(u => u.id === id); }
}
```

---

## 📊 Test Coverage & Best Practices

```javascript
// Run with coverage
// npx jest --coverage

// Good test structure (Arrange-Act-Assert)
test('should calculate order total with discount', () => {
  // Arrange
  const items = [{ price: 100, qty: 2 }, { price: 50, qty: 1 }];
  const discount = 0.1;
  
  // Act
  const total = calculateTotal(items, discount);
  
  // Assert
  expect(total).toBe(225); // (200 + 50) * 0.9
});

// Test edge cases
describe('divide', () => {
  it('should divide correctly', () => expect(divide(10, 2)).toBe(5));
  it('should handle zero divisor', () => expect(() => divide(10, 0)).toThrow());
  it('should handle negative numbers', () => expect(divide(-10, 2)).toBe(-5));
  it('should handle floating point', () => expect(divide(1, 3)).toBeCloseTo(0.333));
});
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is the difference between unit tests and integration tests?**

Unit tests: test a single function/class in isolation, mock all dependencies, fast, many of them. Integration tests: test multiple components working together (API → controller → service → database), slower, fewer. Unit tests verify logic; integration tests verify components interact correctly.

**Q2: What is mocking and why is it used in testing?**

Mocking replaces real dependencies (database, APIs, email) with controlled implementations. Purpose: isolate the unit under test, make tests deterministic (no network calls), test error scenarios (simulate failures), speed up tests. Use `jest.fn()`, `jest.mock()`, or manual mock implementations.

**Q3: What is Supertest and when do you use it?**

Supertest is a library for testing HTTP endpoints. It creates a test server from your Express app (without actually listening on a port) and makes HTTP requests against it. Used for integration testing APIs — verify status codes, response bodies, headers, and auth without a running server.

### Intermediate

**Q4: How do you test async code and error handling?**

For resolved promises: `await expect(fn()).resolves.toBe(value)`. For rejections: `await expect(fn()).rejects.toThrow(ErrorType)`. Use try/catch in tests for more complex assertions. For callbacks: use Jest's `done` callback. Always test both success and failure paths.

**Q5: How do you set up test databases?**

Options: (1) In-memory database (MongoDB Memory Server, SQLite for Postgres). (2) Docker container with fresh DB per test suite. (3) Test schema in existing DB with cleanup. Best practice: separate test config, seed data in `beforeEach`, clean in `afterEach`, never share state between tests.

**Q6: What is test coverage and what's a good target?**

Test coverage measures what percentage of code is exercised by tests (lines, branches, functions, statements). Target 80%+ for critical paths. 100% is rarely practical or valuable. Focus on: business logic, error handling, edge cases. Don't test trivial getters/setters. Branch coverage is most meaningful.

### Advanced

**Q7: How do you test WebSocket/real-time functionality?**

Use Socket.IO client in tests to connect to test server. Test: connection auth, event emission/reception, room join/leave, broadcasting. Use `waitFor` patterns for async event assertions. Test reconnection and error scenarios. Mock timers for timeout testing. Run server on random port.

**Q8: How would you implement contract testing for microservices?**

Use Pact or similar: consumer defines expected interactions (contract), provider verifies it can fulfill them. Contracts are shared via a broker. Tests run independently in each service's CI. Catch breaking API changes before deployment. Combine with schema validation (OpenAPI) for completeness.

**Q9: Design a testing strategy for a production Node.js API with 100+ endpoints.**

Layers: (1) Unit tests for all services/utilities (fast, high coverage). (2) Integration tests for critical paths (auth, payments, core CRUD). (3) Contract tests for external APIs. (4) E2E smoke tests for deployment verification. Infrastructure: parallel test execution, test database per worker, CI pipeline with coverage gates, snapshot testing for response formats.

---

## 🛠️ Hands-on Exercise

Test a complete user management API:
1. Unit test UserService with mocked dependencies
2. Integration test all CRUD endpoints with Supertest
3. Test authentication flow (register → login → protected route)
4. Test error scenarios (validation, 404, 409, 500)
5. Achieve 90%+ test coverage
6. Set up test database with automatic cleanup
