# Day 27: JavaScript Testing

## 🎯 Learning Objectives
- Master Jest testing framework
- Understand unit vs integration testing
- Learn mocking and spying
- Practice TDD patterns
- Understand code coverage

---

## 🧪 Testing Fundamentals

### Testing Types

```
┌─────────────────────────────────────────────────────────────────┐
│                    TESTING PYRAMID                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                     △                                            │
│                    /E\                                           │
│                   /2E\        E2E Tests (Cypress, Playwright)   │
│                  /────\       Few, slow, expensive               │
│                 /      \                                         │
│                / INTEG  \     Integration Tests                  │
│               /──────────\    Medium amount                      │
│              /            \                                      │
│             /    UNIT      \  Unit Tests                         │
│            /────────────────\ Many, fast, cheap                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🃏 Jest Basics

### Setup

```bash
npm install --save-dev jest
```

```json
// package.json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}
```

### Basic Test Structure

```javascript
// math.js
function add(a, b) {
    return a + b;
}

function multiply(a, b) {
    return a * b;
}

module.exports = { add, multiply };

// math.test.js
const { add, multiply } = require('./math');

describe('Math functions', () => {
    describe('add', () => {
        test('adds two positive numbers', () => {
            expect(add(1, 2)).toBe(3);
        });

        test('adds negative numbers', () => {
            expect(add(-1, -2)).toBe(-3);
        });

        it('handles zero', () => { // 'it' is alias for 'test'
            expect(add(5, 0)).toBe(5);
        });
    });

    describe('multiply', () => {
        test('multiplies two numbers', () => {
            expect(multiply(3, 4)).toBe(12);
        });
    });
});
```

---

## 📝 Jest Matchers

```javascript
// EQUALITY MATCHERS
test('equality matchers', () => {
    // Exact equality
    expect(2 + 2).toBe(4);
    
    // Object equality (deep)
    expect({ a: 1, b: 2 }).toEqual({ a: 1, b: 2 });
    
    // Strict equality with objects
    const obj = { a: 1 };
    expect(obj).toBe(obj);  // Same reference
    expect({ a: 1 }).not.toBe({ a: 1 }); // Different references
});

// TRUTHINESS
test('truthiness', () => {
    expect(null).toBeNull();
    expect(undefined).toBeUndefined();
    expect(true).toBeDefined();
    expect(true).toBeTruthy();
    expect(false).toBeFalsy();
    expect(0).toBeFalsy();
    expect('').toBeFalsy();
});

// NUMBERS
test('numbers', () => {
    expect(2 + 2).toBeGreaterThan(3);
    expect(2 + 2).toBeGreaterThanOrEqual(4);
    expect(2 + 2).toBeLessThan(5);
    expect(2 + 2).toBeLessThanOrEqual(4);
    
    // Floating point
    expect(0.1 + 0.2).toBeCloseTo(0.3); // Handles floating point
});

// STRINGS
test('strings', () => {
    expect('Hello World').toMatch(/World/);
    expect('Hello World').toContain('World');
    expect('Hello World').toHaveLength(11);
});

// ARRAYS AND ITERABLES
test('arrays', () => {
    const arr = ['apple', 'banana', 'cherry'];
    
    expect(arr).toContain('banana');
    expect(arr).toHaveLength(3);
    expect(arr).toEqual(expect.arrayContaining(['banana', 'apple']));
    
    // Objects in arrays
    const users = [{ name: 'Alice' }, { name: 'Bob' }];
    expect(users).toContainEqual({ name: 'Alice' });
});

// OBJECTS
test('objects', () => {
    const obj = { a: 1, b: 2, c: 3 };
    
    expect(obj).toHaveProperty('a');
    expect(obj).toHaveProperty('a', 1);
    expect(obj).toMatchObject({ a: 1, b: 2 });
    expect(obj).toEqual(expect.objectContaining({ a: 1 }));
});

// EXCEPTIONS
test('exceptions', () => {
    function throwError() {
        throw new Error('Something went wrong');
    }
    
    expect(throwError).toThrow();
    expect(throwError).toThrow(Error);
    expect(throwError).toThrow('Something went wrong');
    expect(throwError).toThrow(/wrong/);
});

// NEGATION
test('negation', () => {
    expect(1).not.toBe(2);
    expect([1, 2]).not.toContain(3);
});
```

---

## 🎭 Mocking

### Mock Functions

```javascript
// BASIC MOCK
test('mock function', () => {
    const mockFn = jest.fn();
    
    mockFn('hello');
    mockFn('world');
    
    expect(mockFn).toHaveBeenCalled();
    expect(mockFn).toHaveBeenCalledTimes(2);
    expect(mockFn).toHaveBeenCalledWith('hello');
    expect(mockFn).toHaveBeenLastCalledWith('world');
    
    // All calls
    expect(mockFn.mock.calls).toEqual([['hello'], ['world']]);
});

// MOCK RETURN VALUES
test('mock return values', () => {
    const mockFn = jest.fn();
    
    mockFn
        .mockReturnValue(10)           // Default return
        .mockReturnValueOnce(1)        // First call
        .mockReturnValueOnce(2);       // Second call
    
    expect(mockFn()).toBe(1);  // First call
    expect(mockFn()).toBe(2);  // Second call
    expect(mockFn()).toBe(10); // Subsequent calls
});

// MOCK IMPLEMENTATION
test('mock implementation', () => {
    const mockFn = jest.fn(x => x * 2);
    
    expect(mockFn(5)).toBe(10);
    
    mockFn.mockImplementation(x => x + 1);
    expect(mockFn(5)).toBe(6);
    
    mockFn.mockImplementationOnce(x => x * 10);
    expect(mockFn(5)).toBe(50);
    expect(mockFn(5)).toBe(6);  // Back to previous implementation
});

// MOCK PROMISES
test('mock async functions', async () => {
    const mockFn = jest.fn();
    
    mockFn
        .mockResolvedValue('default')
        .mockResolvedValueOnce('first')
        .mockRejectedValueOnce(new Error('failed'));
    
    await expect(mockFn()).resolves.toBe('first');
    await expect(mockFn()).rejects.toThrow('failed');
    await expect(mockFn()).resolves.toBe('default');
});
```

### Mocking Modules

```javascript
// api.js
const axios = require('axios');

async function fetchUser(id) {
    const response = await axios.get(`/users/${id}`);
    return response.data;
}

module.exports = { fetchUser };

// api.test.js
const axios = require('axios');
const { fetchUser } = require('./api');

// Mock entire module
jest.mock('axios');

test('fetches user', async () => {
    const user = { id: 1, name: 'John' };
    axios.get.mockResolvedValue({ data: user });
    
    const result = await fetchUser(1);
    
    expect(result).toEqual(user);
    expect(axios.get).toHaveBeenCalledWith('/users/1');
});

// PARTIAL MOCK
jest.mock('./utils', () => ({
    ...jest.requireActual('./utils'), // Keep original implementation
    specificFunction: jest.fn()        // Mock only this
}));

// MANUAL MOCKS
// __mocks__/axios.js
module.exports = {
    get: jest.fn(),
    post: jest.fn(),
    create: jest.fn(() => ({
        get: jest.fn(),
        post: jest.fn()
    }))
};
```

### Spying

```javascript
const calculator = {
    add(a, b) {
        return a + b;
    },
    multiply(a, b) {
        return a * b;
    }
};

test('spy on method', () => {
    const addSpy = jest.spyOn(calculator, 'add');
    
    const result = calculator.add(2, 3);
    
    expect(result).toBe(5);  // Original implementation called
    expect(addSpy).toHaveBeenCalledWith(2, 3);
    
    addSpy.mockRestore(); // Restore original
});

test('spy and mock implementation', () => {
    const addSpy = jest.spyOn(calculator, 'add')
        .mockImplementation(() => 100);
    
    expect(calculator.add(2, 3)).toBe(100);
    
    addSpy.mockRestore();
});
```

---

## ⏰ Testing Async Code

```javascript
// CALLBACKS
function fetchData(callback) {
    setTimeout(() => callback('data'), 100);
}

test('callback', done => {
    fetchData(data => {
        expect(data).toBe('data');
        done(); // Signal completion
    });
});

// PROMISES
function fetchDataPromise() {
    return new Promise(resolve => {
        setTimeout(() => resolve('data'), 100);
    });
}

test('promise with return', () => {
    return fetchDataPromise().then(data => {
        expect(data).toBe('data');
    });
});

test('promise with resolves', () => {
    return expect(fetchDataPromise()).resolves.toBe('data');
});

test('promise rejection', () => {
    const rejectPromise = () => Promise.reject(new Error('fail'));
    return expect(rejectPromise()).rejects.toThrow('fail');
});

// ASYNC/AWAIT
test('async/await', async () => {
    const data = await fetchDataPromise();
    expect(data).toBe('data');
});

test('async/await with expect', async () => {
    await expect(fetchDataPromise()).resolves.toBe('data');
});
```

---

## ⏲️ Timers

```javascript
// Code using timers
function delayedCallback(callback) {
    setTimeout(callback, 1000);
}

function debounce(fn, delay) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => fn.apply(this, args), delay);
    };
}

// FAKE TIMERS
describe('timer tests', () => {
    beforeEach(() => {
        jest.useFakeTimers();
    });

    afterEach(() => {
        jest.useRealTimers();
    });

    test('advances timers', () => {
        const callback = jest.fn();
        delayedCallback(callback);
        
        expect(callback).not.toHaveBeenCalled();
        
        jest.advanceTimersByTime(1000);
        
        expect(callback).toHaveBeenCalled();
    });

    test('run all timers', () => {
        const callback = jest.fn();
        delayedCallback(callback);
        
        jest.runAllTimers();
        
        expect(callback).toHaveBeenCalled();
    });

    test('debounce', () => {
        const fn = jest.fn();
        const debouncedFn = debounce(fn, 500);
        
        debouncedFn();
        debouncedFn();
        debouncedFn();
        
        expect(fn).not.toHaveBeenCalled();
        
        jest.advanceTimersByTime(500);
        
        expect(fn).toHaveBeenCalledTimes(1);
    });
});
```

---

## 🔧 Setup and Teardown

```javascript
describe('Database tests', () => {
    let db;

    // Runs once before all tests in this describe block
    beforeAll(async () => {
        db = await connectDatabase();
    });

    // Runs once after all tests
    afterAll(async () => {
        await db.close();
    });

    // Runs before each test
    beforeEach(async () => {
        await db.clear();
        await db.seed();
    });

    // Runs after each test
    afterEach(() => {
        jest.clearAllMocks();
    });

    test('test 1', () => {/* ... */});
    test('test 2', () => {/* ... */});
});

// SCOPING
describe('outer', () => {
    beforeAll(() => console.log('1 - beforeAll outer'));
    afterAll(() => console.log('1 - afterAll outer'));
    beforeEach(() => console.log('1 - beforeEach outer'));
    afterEach(() => console.log('1 - afterEach outer'));

    test('outer test', () => console.log('1 - test'));

    describe('inner', () => {
        beforeAll(() => console.log('2 - beforeAll inner'));
        afterAll(() => console.log('2 - afterAll inner'));
        beforeEach(() => console.log('2 - beforeEach inner'));
        afterEach(() => console.log('2 - afterEach inner'));

        test('inner test', () => console.log('2 - test'));
    });
});

/*
Output:
1 - beforeAll outer
1 - beforeEach outer
1 - test
1 - afterEach outer
2 - beforeAll inner
1 - beforeEach outer
2 - beforeEach inner
2 - test
2 - afterEach inner
1 - afterEach outer
2 - afterAll inner
1 - afterAll outer
*/
```

---

## 📊 Test Patterns

### Test-Driven Development (TDD)

```javascript
/*
TDD CYCLE:
1. RED - Write failing test
2. GREEN - Write minimal code to pass
3. REFACTOR - Improve code, keep tests passing
*/

// 1. RED - Write test first
test('Stack push adds element to top', () => {
    const stack = new Stack();
    stack.push(1);
    expect(stack.peek()).toBe(1);
});

// 2. GREEN - Minimal implementation
class Stack {
    constructor() {
        this.items = [];
    }
    push(item) {
        this.items.push(item);
    }
    peek() {
        return this.items[this.items.length - 1];
    }
}

// 3. Continue TDD cycle for more features
test('Stack pop removes and returns top element', () => {
    const stack = new Stack();
    stack.push(1);
    stack.push(2);
    expect(stack.pop()).toBe(2);
    expect(stack.peek()).toBe(1);
});
```

### Parameterized Tests

```javascript
// test.each
describe('add function', () => {
    test.each([
        [1, 1, 2],
        [1, 2, 3],
        [2, 2, 4],
        [-1, 1, 0],
    ])('add(%i, %i) returns %i', (a, b, expected) => {
        expect(add(a, b)).toBe(expected);
    });
});

// With objects
describe('user validation', () => {
    test.each([
        { input: { name: '' }, expected: false, desc: 'empty name' },
        { input: { name: 'ab' }, expected: false, desc: 'name too short' },
        { input: { name: 'valid' }, expected: true, desc: 'valid name' },
    ])('$desc', ({ input, expected }) => {
        expect(isValidUser(input)).toBe(expected);
    });
});

// describe.each
describe.each([
    { type: 'string', value: 'hello' },
    { type: 'number', value: 42 },
])('$type validation', ({ value }) => {
    test('is defined', () => {
        expect(value).toBeDefined();
    });
});
```

### Snapshot Testing

```javascript
// Component or data structure snapshots
function UserCard({ user }) {
    return {
        type: 'div',
        className: 'user-card',
        children: [
            { type: 'h2', children: user.name },
            { type: 'p', children: user.email }
        ]
    };
}

test('UserCard renders correctly', () => {
    const user = { name: 'John', email: 'john@example.com' };
    expect(UserCard({ user })).toMatchSnapshot();
});

// Inline snapshots
test('inline snapshot', () => {
    const value = { a: 1, b: 2 };
    expect(value).toMatchInlineSnapshot(`
        Object {
          "a": 1,
          "b": 2,
        }
    `);
});
```

---

## 🎯 Testing Best Practices

```javascript
// 1. ARRANGE-ACT-ASSERT (AAA)
test('user can be created', () => {
    // Arrange
    const userData = { name: 'John', email: 'john@example.com' };
    
    // Act
    const user = createUser(userData);
    
    // Assert
    expect(user.id).toBeDefined();
    expect(user.name).toBe('John');
});

// 2. ONE ASSERTION CONCEPT PER TEST
// ❌ Bad - testing multiple concepts
test('user operations', () => {
    const user = createUser({ name: 'John' });
    expect(user.name).toBe('John');
    
    updateUser(user, { name: 'Jane' });
    expect(user.name).toBe('Jane');
    
    deleteUser(user);
    expect(getUser(user.id)).toBeNull();
});

// ✅ Good - separate tests
test('creates user with name', () => {
    const user = createUser({ name: 'John' });
    expect(user.name).toBe('John');
});

test('updates user name', () => {
    const user = createUser({ name: 'John' });
    updateUser(user, { name: 'Jane' });
    expect(user.name).toBe('Jane');
});

// 3. DESCRIPTIVE NAMES
// ❌ Bad
test('test1', () => {});

// ✅ Good
test('throws error when password is less than 8 characters', () => {});

// 4. AVOID IMPLEMENTATION DETAILS
// ❌ Bad - testing implementation
test('calls internal method', () => {
    const spy = jest.spyOn(service, '_internalMethod');
    service.publicMethod();
    expect(spy).toHaveBeenCalled();
});

// ✅ Good - testing behavior
test('returns processed data', () => {
    const result = service.publicMethod();
    expect(result).toEqual(expectedOutput);
});

// 5. USE FACTORIES FOR TEST DATA
function createTestUser(overrides = {}) {
    return {
        id: 1,
        name: 'Test User',
        email: 'test@example.com',
        ...overrides
    };
}

test('greets user by name', () => {
    const user = createTestUser({ name: 'Alice' });
    expect(greet(user)).toBe('Hello, Alice!');
});
```

---

## 📈 Code Coverage

```bash
# Generate coverage report
jest --coverage

# Coverage thresholds in jest.config.js
module.exports = {
    coverageThreshold: {
        global: {
            branches: 80,
            functions: 80,
            lines: 80,
            statements: 80
        }
    },
    collectCoverageFrom: [
        'src/**/*.js',
        '!src/**/*.test.js',
        '!src/index.js'
    ]
};
```

```
┌─────────────────────────────────────────────────────────────────┐
│                    COVERAGE REPORT                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  File        | % Stmts | % Branch | % Funcs | % Lines           │
│  ──────────────────────────────────────────────────────────────  │
│  All files   |   85.71 |    66.67 |     100 |   85.71           │
│  math.js     |     100 |      100 |     100 |     100           │
│  utils.js    |      75 |       50 |     100 |      75           │
│                                                                  │
│  TYPES:                                                          │
│  • Statements - Lines of code executed                           │
│  • Branches   - if/else, ternary, && paths                      │
│  • Functions  - Functions called                                 │
│  • Lines      - Physical lines executed                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Day 27 Checklist

- [ ] Set up Jest in a project
- [ ] Understand all common matchers
- [ ] Create mock functions
- [ ] Mock modules and dependencies
- [ ] Use spies to track calls
- [ ] Test async code properly
- [ ] Use fake timers
- [ ] Implement setup/teardown
- [ ] Write parameterized tests
- [ ] Follow TDD principles
- [ ] Generate coverage reports
