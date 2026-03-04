# Day 2: Jest Deep Dive – The Complete Guide

## 📚 Topics to Cover (3-4 hours)

---

## 1. Jest Overview

Jest is Facebook's zero-config testing framework for JavaScript/TypeScript. It's the default for React and widely used with Node.js projects.

### Installation & Setup

```bash
# NPM
npm install --save-dev jest @types/jest ts-jest

# package.json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

### jest.config.js

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node', // or 'jsdom' for browser
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
  collectCoverageFrom: ['src/**/*.ts', '!src/**/*.d.ts'],
  coverageThreshold: {
    global: { branches: 80, functions: 80, lines: 80, statements: 80 }
  },
  setupFilesAfterSetup: ['./jest.setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1'
  }
};
```

---

## 2. Matchers – Complete Reference

### Common Matchers

```javascript
// Exact equality
expect(2 + 2).toBe(4);
expect({ name: 'John' }).toEqual({ name: 'John' }); // deep equality

// Truthiness
expect(null).toBeNull();
expect(undefined).toBeUndefined();
expect(value).toBeDefined();
expect(value).toBeTruthy();
expect(value).toBeFalsy();

// Numbers
expect(value).toBeGreaterThan(3);
expect(value).toBeGreaterThanOrEqual(3.5);
expect(value).toBeLessThan(5);
expect(0.1 + 0.2).toBeCloseTo(0.3); // floating point

// Strings
expect('team').toMatch(/T/i);
expect('Christoph').toMatch(/stop/);

// Arrays & Iterables
expect(['Alice', 'Bob', 'Eve']).toContain('Bob');
expect(new Set([1, 2, 3])).toContain(2);

// Objects
expect(obj).toHaveProperty('name');
expect(obj).toHaveProperty('address.city', 'NYC');
expect(obj).toMatchObject({ name: 'John' }); // partial match

// Exceptions
expect(() => compileCode()).toThrow();
expect(() => compileCode()).toThrow(Error);
expect(() => compileCode()).toThrow('compile error');
expect(() => compileCode()).toThrow(/error/);
```

### Asymmetric Matchers

```javascript
expect(callback).toHaveBeenCalledWith(
  expect.objectContaining({ name: 'John' }),
  expect.any(Number),
  expect.arrayContaining([1, 2]),
  expect.stringMatching(/hello/i),
  expect.anything() // matches everything except null/undefined
);
```

---

## 3. Mocking – Complete Guide

### Function Mocks

```javascript
// Basic mock function
const mockFn = jest.fn();
mockFn('hello');
expect(mockFn).toHaveBeenCalledWith('hello');
expect(mockFn).toHaveBeenCalledTimes(1);

// Return values
const mockFn = jest.fn()
  .mockReturnValueOnce(10)
  .mockReturnValueOnce('x')
  .mockReturnValue(true);

console.log(mockFn(), mockFn(), mockFn()); // 10, 'x', true

// Async mock
const asyncMock = jest.fn()
  .mockResolvedValue('default')
  .mockResolvedValueOnce('first call')
  .mockRejectedValueOnce(new Error('fail'));

// Implementation mock
const mockFn = jest.fn((a, b) => a + b);
```

### Module Mocks

```javascript
// Auto-mock entire module
jest.mock('./userService');
import { getUser } from './userService';

// Manual mock with implementation
jest.mock('./userService', () => ({
  getUser: jest.fn().mockResolvedValue({ id: 1, name: 'John' }),
  createUser: jest.fn().mockResolvedValue({ id: 2 }),
}));

// Partial mock (keep some real implementations)
jest.mock('./utils', () => ({
  ...jest.requireActual('./utils'),
  formatDate: jest.fn().mockReturnValue('2026-01-01'),
}));
```

### Spying

```javascript
const video = {
  play() { return true; },
  pause() { return false; }
};

// Spy on method
const playSpy = jest.spyOn(video, 'play');
video.play();
expect(playSpy).toHaveBeenCalled();

// Spy and mock implementation
jest.spyOn(video, 'play').mockImplementation(() => 'mocked');

// Spy on module method
import * as mathUtils from './math';
jest.spyOn(mathUtils, 'add').mockReturnValue(42);

// Restore original
playSpy.mockRestore();
```

### Timer Mocks

```javascript
jest.useFakeTimers();

function delayedGreeting(callback) {
  setTimeout(() => callback('Hello!'), 1000);
}

it('should call callback after 1 second', () => {
  const cb = jest.fn();
  delayedGreeting(cb);
  
  expect(cb).not.toHaveBeenCalled();
  jest.advanceTimersByTime(1000);
  expect(cb).toHaveBeenCalledWith('Hello!');
});

// Run all timers
jest.runAllTimers();

// Run only pending timers
jest.runOnlyPendingTimers();

// Clear all timers
jest.clearAllTimers();
jest.useRealTimers();
```

---

## 4. Async Testing

```javascript
// Promises
it('should fetch data', () => {
  return fetchData().then(data => {
    expect(data).toBe('peanut butter');
  });
});

// Async/Await (preferred)
it('should fetch data', async () => {
  const data = await fetchData();
  expect(data).toBe('peanut butter');
});

// Reject
it('should fail with error', async () => {
  await expect(fetchBadData()).rejects.toThrow('network error');
});

// Resolve
it('should resolve with data', async () => {
  await expect(fetchData()).resolves.toBe('peanut butter');
});
```

---

## 5. Setup & Teardown

```javascript
describe('Database tests', () => {
  // Run once before all tests in this describe
  beforeAll(async () => {
    await db.connect();
  });

  // Run before each test
  beforeEach(async () => {
    await db.clear();
    await db.seed();
  });

  // Run after each test
  afterEach(() => {
    jest.clearAllMocks();
  });

  // Run once after all tests
  afterAll(async () => {
    await db.disconnect();
  });

  it('should create user', async () => {
    const user = await createUser({ name: 'John' });
    expect(user.id).toBeDefined();
  });
});
```

---

## 6. Snapshot Testing

```javascript
// Basic snapshot
it('should render correctly', () => {
  const tree = renderer.create(<Button label="Click me" />).toJSON();
  expect(tree).toMatchSnapshot();
});

// Inline snapshot
it('should format user', () => {
  expect(formatUser({ name: 'John', age: 30 })).toMatchInlineSnapshot(`
    "John (30 years old)"
  `);
});

// Update snapshots: jest --updateSnapshot or press 'u' in watch mode
```

---

## 7. Custom Matchers

```javascript
expect.extend({
  toBeWithinRange(received, floor, ceiling) {
    const pass = received >= floor && received <= ceiling;
    return {
      pass,
      message: () =>
        `expected ${received} ${pass ? 'not ' : ''}to be within range ${floor} - ${ceiling}`,
    };
  },
});

it('should be within range', () => {
  expect(100).toBeWithinRange(90, 110);
  expect(101).not.toBeWithinRange(0, 100);
});
```

---

## 8. Testing Patterns for Real-World Code

### Testing HTTP Calls

```javascript
import axios from 'axios';
jest.mock('axios');

describe('UserAPI', () => {
  it('should fetch users', async () => {
    const users = [{ id: 1, name: 'John' }];
    (axios.get as jest.Mock).mockResolvedValue({ data: users });

    const result = await UserAPI.getAll();
    
    expect(axios.get).toHaveBeenCalledWith('/api/users');
    expect(result).toEqual(users);
  });

  it('should handle error', async () => {
    (axios.get as jest.Mock).mockRejectedValue(new Error('Network Error'));

    await expect(UserAPI.getAll()).rejects.toThrow('Network Error');
  });
});
```

### Testing Event Emitters

```javascript
describe('EventBus', () => {
  it('should emit and handle events', () => {
    const bus = new EventBus();
    const handler = jest.fn();

    bus.on('user:created', handler);
    bus.emit('user:created', { id: 1, name: 'John' });

    expect(handler).toHaveBeenCalledWith({ id: 1, name: 'John' });
  });
});
```

---

## 🎯 Interview Questions

### Q1: How does Jest handle module mocking under the hood?
**A:** Jest hoists `jest.mock()` calls to the top of the file (babel transform). It replaces the module's exports with mock implementations. The module registry is manipulated so all imports get the mocked version. `jest.requireActual()` bypasses this for partial mocks.

### Q2: Explain the difference between `jest.fn()` and `jest.spyOn()`
**A:** `jest.fn()` creates a new empty mock function. `jest.spyOn()` wraps an existing method, letting you track calls while optionally keeping the original implementation. `spyOn` can be restored with `.mockRestore()`.

### Q3: How do you test code with setTimeout/setInterval?
**A:** Use `jest.useFakeTimers()` to control time flow. Then `jest.advanceTimersByTime(ms)` to fast-forward, or `jest.runAllTimers()` to execute all pending timers instantly. Always call `jest.useRealTimers()` in cleanup.

### Q4: What's the difference between `toBe` and `toEqual`?
**A:** `toBe` uses `Object.is()` for strict reference equality. `toEqual` recursively checks every property for deep equality. Use `toBe` for primitives and same-reference checks, `toEqual` for objects/arrays.

---

## 📝 Practice Exercises

1. Create a mock for `fetch` API and test a data-fetching service
2. Write timer tests for a debounce function
3. Test an Express middleware with mocked request/response objects
4. Create snapshot tests for a utility that formats complex objects

---

## 📖 Resources
- [Jest Official Docs](https://jestjs.io/docs/getting-started)
- [Jest Mock Functions](https://jestjs.io/docs/mock-functions)
- [Testing Async Code](https://jestjs.io/docs/asynchronous)
