# Day 14: Error Handling & Debugging

## 🎯 Learning Objectives
- Master try/catch/finally
- Create custom error classes
- Learn debugging with DevTools
- Understand memory profiling
- Handle async errors properly

---

## 🚨 Error Types in JavaScript

```javascript
// Built-in Error Types
try {
    // SyntaxError - Parsing error (can't be caught at runtime)
    // eval('if ('); // SyntaxError: Unexpected end of input
    
    // ReferenceError - Undeclared variable
    console.log(undeclaredVar);
    
    // TypeError - Wrong type operation
    null.foo;
    
    // RangeError - Number out of range
    new Array(-1);
    
    // URIError - Invalid URI
    decodeURI('%');
    
    // EvalError - Rarely used, related to eval()
    
} catch (error) {
    console.log(error.name);    // "ReferenceError"
    console.log(error.message); // "undeclaredVar is not defined"
    console.log(error.stack);   // Full stack trace
}

// Error constructor
const error = new Error('Something went wrong');
error.name;    // "Error"
error.message; // "Something went wrong"
error.stack;   // Stack trace
```

---

## 🛡️ try/catch/finally

```javascript
// Basic structure
try {
    // Code that might throw
    riskyOperation();
} catch (error) {
    // Handle the error
    console.error('Error:', error.message);
} finally {
    // Always runs (cleanup)
    cleanup();
}

// Execution flow examples
function example1() {
    try {
        console.log('1');
        throw new Error('Oops');
        console.log('2'); // Never runs
    } catch (e) {
        console.log('3');
    } finally {
        console.log('4');
    }
    console.log('5');
}
example1(); // Output: 1, 3, 4, 5

// Return in try/catch/finally
function example2() {
    try {
        return 'try';
    } finally {
        return 'finally'; // Overrides try's return!
    }
}
console.log(example2()); // "finally"

function example3() {
    try {
        return 'try';
    } finally {
        console.log('cleanup');
        // No return here
    }
}
console.log(example3()); // cleanup, then "try"

// Nested try/catch
function outer() {
    try {
        inner();
    } catch (e) {
        console.log('Outer catch:', e.message);
    }
}

function inner() {
    try {
        throw new Error('Inner error');
    } catch (e) {
        console.log('Inner catch:', e.message);
        throw e; // Re-throw to outer
    }
}

outer();
// "Inner catch: Inner error"
// "Outer catch: Inner error"

// Optional catch binding (ES2019+)
try {
    JSON.parse(badJson);
} catch { // No error parameter needed
    console.log('Parse failed');
}
```

---

## 🛠️ Custom Errors

```javascript
// Basic custom error
class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
        
        // Maintains proper stack trace (V8)
        if (Error.captureStackTrace) {
            Error.captureStackTrace(this, ValidationError);
        }
    }
}

// Custom error with additional properties
class HttpError extends Error {
    constructor(statusCode, message) {
        super(message);
        this.name = 'HttpError';
        this.statusCode = statusCode;
    }
    
    get isClientError() {
        return this.statusCode >= 400 && this.statusCode < 500;
    }
    
    get isServerError() {
        return this.statusCode >= 500;
    }
}

// Usage
function validateUser(user) {
    if (!user.name) {
        throw new ValidationError('Name is required');
    }
    if (!user.email) {
        throw new ValidationError('Email is required');
    }
}

try {
    validateUser({});
} catch (error) {
    if (error instanceof ValidationError) {
        console.log('Validation failed:', error.message);
    } else {
        throw error; // Re-throw unexpected errors
    }
}

// Error hierarchy
class AppError extends Error {
    constructor(message, code) {
        super(message);
        this.name = this.constructor.name;
        this.code = code;
    }
}

class DatabaseError extends AppError {
    constructor(message, query) {
        super(message, 'DB_ERROR');
        this.query = query;
    }
}

class NotFoundError extends AppError {
    constructor(resource) {
        super(`${resource} not found`, 'NOT_FOUND');
        this.resource = resource;
    }
}

// Aggregate Error (ES2021)
const errors = [
    new Error('Error 1'),
    new Error('Error 2'),
    new Error('Error 3')
];

const aggregateError = new AggregateError(errors, 'Multiple errors occurred');
console.log(aggregateError.errors); // Array of all errors

// Often used with Promise.any()
try {
    await Promise.any([failingPromise1, failingPromise2]);
} catch (e) {
    if (e instanceof AggregateError) {
        e.errors.forEach(err => console.log(err.message));
    }
}
```

---

## 🔄 Async Error Handling

```javascript
// Callback pattern
function asyncOperation(callback) {
    setTimeout(() => {
        try {
            const result = riskyOperation();
            callback(null, result);
        } catch (error) {
            callback(error, null);
        }
    }, 100);
}

// Error-first callback usage
asyncOperation((error, result) => {
    if (error) {
        console.error('Error:', error.message);
        return;
    }
    console.log('Result:', result);
});

// Promise error handling
fetchData()
    .then(data => processData(data))
    .then(result => displayResult(result))
    .catch(error => {
        // Catches errors from any previous .then()
        console.error('Error:', error.message);
    })
    .finally(() => {
        // Cleanup - always runs
        hideLoading();
    });

// Async/await error handling
async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        
        if (!response.ok) {
            throw new HttpError(response.status, 'Failed to fetch user');
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        if (error instanceof HttpError) {
            console.error('HTTP Error:', error.statusCode);
        } else if (error instanceof TypeError) {
            console.error('Network error');
        } else {
            console.error('Unexpected error:', error);
        }
        throw error; // Re-throw if needed
    }
}

// Promise.all error handling
async function fetchAllData() {
    try {
        const [users, posts, comments] = await Promise.all([
            fetchUsers(),
            fetchPosts(),
            fetchComments()
        ]);
        return { users, posts, comments };
    } catch (error) {
        // First rejection stops everything
        console.error('One request failed:', error);
    }
}

// Promise.allSettled - get all results
async function fetchAllDataSafe() {
    const results = await Promise.allSettled([
        fetchUsers(),
        fetchPosts(),
        fetchComments()
    ]);
    
    results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
            console.log(`Request ${index} succeeded:`, result.value);
        } else {
            console.log(`Request ${index} failed:`, result.reason);
        }
    });
}

// Unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection:', reason);
    // Log and exit, or handle appropriately
});

// Browser equivalent
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled rejection:', event.reason);
    event.preventDefault(); // Prevent default console error
});
```

---

## 🔍 Debugging Techniques

### Console Methods

```javascript
// Basic logging
console.log('Simple log');
console.info('Info message');
console.warn('Warning message');
console.error('Error message');

// Formatted output
console.log('User: %s, Age: %d', 'John', 30);
console.log('%c Styled text', 'color: red; font-size: 20px');

// Object inspection
const user = { name: 'John', age: 30, address: { city: 'NYC' } };
console.log(user);     // May be collapsed
console.dir(user);     // Always shows object properties
console.table([user]); // Table format

// Grouping
console.group('User Operations');
console.log('Fetching user...');
console.log('Processing data...');
console.groupEnd();

// Conditionally
console.assert(1 === 2, 'Math is broken!'); // Only logs if false

// Timing
console.time('operation');
heavyOperation();
console.timeEnd('operation'); // "operation: 123.456ms"

// Counting
function processItem() {
    console.count('processItem called');
}
processItem(); // "processItem called: 1"
processItem(); // "processItem called: 2"
console.countReset('processItem called');

// Stack trace
console.trace('Trace from here');
```

### Debugger Statement

```javascript
function complexCalculation(a, b) {
    debugger; // Pauses here if DevTools is open
    
    const intermediate = a * b;
    const result = intermediate + 10;
    
    return result;
}
```

### DevTools Features

```javascript
/*
╔══════════════════════════════════════════════════════════════════╗
║                    CHROME DEVTOOLS FEATURES                       ║
╠══════════════════════════════════════════════════════════════════╣
║ BREAKPOINTS:                                                      ║
║ - Line breakpoints (click line number)                            ║
║ - Conditional breakpoints (right-click → Add conditional)         ║
║ - DOM breakpoints (Elements → Break on...)                        ║
║ - XHR/fetch breakpoints (Sources → XHR/fetch Breakpoints)         ║
║ - Event listener breakpoints (Sources → Event Listener)            ║
║ - Exception breakpoints (pause on caught/uncaught)                ║
║                                                                   ║
║ STEPPING:                                                         ║
║ - F8: Resume                                                      ║
║ - F10: Step over                                                  ║
║ - F11: Step into                                                  ║
║ - Shift+F11: Step out                                             ║
║                                                                   ║
║ WATCH EXPRESSIONS:                                                ║
║ - Add variables to watch                                          ║
║ - See values update as you step                                   ║
║                                                                   ║
║ CALL STACK:                                                       ║
║ - See function call hierarchy                                     ║
║ - Click to jump to caller                                         ║
║                                                                   ║
║ SCOPE:                                                            ║
║ - Local, Closure, Global variables                                ║
║ - Edit values in place                                            ║
╚══════════════════════════════════════════════════════════════════╝
*/
```

---

## 💾 Memory Profiling

```javascript
// Memory Leaks - Common Patterns

// 1. Global variables
function leak1() {
    leakedVar = 'oops'; // Missing 'var/let/const'
}

// 2. Forgotten timers
function leak2() {
    setInterval(() => {
        // This runs forever, references never GC'd
        doSomething(largeData);
    }, 1000);
}

// 3. Closures holding references
function leak3() {
    const largeData = new Array(1000000).fill('x');
    
    return function() {
        // Closure keeps largeData alive
        console.log('Small function');
    };
}

const fn = leak3(); // largeData stays in memory

// 4. DOM references
function leak4() {
    const elements = [];
    
    function addElement() {
        const div = document.createElement('div');
        elements.push(div); // Keeps reference even if removed from DOM
        document.body.appendChild(div);
    }
}

// 5. Event listeners not removed
function leak5() {
    const button = document.getElementById('btn');
    
    const handler = () => {
        console.log('clicked', largeData);
    };
    
    button.addEventListener('click', handler);
    // Missing: button.removeEventListener('click', handler);
}

// Fixing memory leaks

// WeakMap/WeakSet for DOM associations
const metadata = new WeakMap();

function setMetadata(element, data) {
    metadata.set(element, data);
    // When element is removed, data can be GC'd
}

// Cleanup pattern
class Component {
    constructor() {
        this.handler = this.handleClick.bind(this);
        this.element = document.getElementById('btn');
        this.element.addEventListener('click', this.handler);
    }
    
    handleClick() {
        console.log('clicked');
    }
    
    destroy() {
        this.element.removeEventListener('click', this.handler);
        this.element = null;
    }
}

// AbortController for event cleanup
const controller = new AbortController();

element.addEventListener('click', handler, {
    signal: controller.signal
});

// Later, to remove:
controller.abort(); // Removes all listeners using this signal
```

### DevTools Memory Panel

```javascript
/*
MEMORY PROFILING IN DEVTOOLS:

1. HEAP SNAPSHOT:
   - Take snapshot before operation
   - Perform operation
   - Take snapshot after
   - Compare snapshots
   - Look for detached DOM trees

2. ALLOCATION TIMELINE:
   - Start recording
   - Perform operations
   - Stop recording
   - See when allocations happen
   - Blue bars = allocated, gray = garbage collected

3. ALLOCATION SAMPLING:
   - Lower overhead profiling
   - Good for production
   - Shows which functions allocate memory

WHAT TO LOOK FOR:
- Growing memory over time
- Objects that should be released but aren't
- Detached DOM trees
- Large arrays/objects
- Duplicate data
*/

// Manual memory measurement (Node.js)
const used = process.memoryUsage();
console.log({
    heapTotal: Math.round(used.heapTotal / 1024 / 1024) + ' MB',
    heapUsed: Math.round(used.heapUsed / 1024 / 1024) + ' MB',
    external: Math.round(used.external / 1024 / 1024) + ' MB',
});

// Performance API (Browser)
if (performance.memory) {
    console.log({
        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit,
        totalJSHeapSize: performance.memory.totalJSHeapSize,
        usedJSHeapSize: performance.memory.usedJSHeapSize
    });
}
```

---

## 🎯 Error Handling Best Practices

```javascript
// 1. Always catch specific errors
async function fetchUser(id) {
    try {
        return await api.getUser(id);
    } catch (error) {
        if (error.code === 'NOT_FOUND') {
            return null; // Expected case
        }
        throw error; // Unexpected, re-throw
    }
}

// 2. Don't swallow errors
// ❌ Bad
try {
    riskyOperation();
} catch (e) {
    // Silent fail - debugging nightmare
}

// ✅ Good
try {
    riskyOperation();
} catch (e) {
    console.error('Operation failed:', e);
    // Handle appropriately
}

// 3. Clean up resources
async function processFile(path) {
    let handle;
    try {
        handle = await fs.open(path, 'r');
        const data = await handle.readFile();
        return process(data);
    } finally {
        if (handle) {
            await handle.close();
        }
    }
}

// 4. Use Error cause (ES2022)
try {
    await fetchData();
} catch (error) {
    throw new Error('Failed to load dashboard', { cause: error });
}

// 5. Wrapper for consistent error handling
async function tryCatch(promise) {
    try {
        const data = await promise;
        return [null, data];
    } catch (error) {
        return [error, null];
    }
}

// Usage
const [error, data] = await tryCatch(fetchUser(1));
if (error) {
    console.error('Failed:', error);
} else {
    console.log('User:', data);
}

// 6. Global error handler setup
window.onerror = (message, source, lineno, colno, error) => {
    logToServer({ message, source, lineno, colno, error });
    return false; // Don't suppress default handling
};

window.addEventListener('error', (event) => {
    logToServer(event.error);
});
```

---

## ✅ Day 14 Checklist

- [ ] Know all built-in Error types
- [ ] Master try/catch/finally flow
- [ ] Create custom error classes
- [ ] Handle async errors properly
- [ ] Use Promise.allSettled for resilience
- [ ] Master console debugging methods
- [ ] Use debugger and breakpoints
- [ ] Identify common memory leak patterns
- [ ] Use DevTools for memory profiling
- [ ] Apply error handling best practices
- [ ] Understand error cause chaining
- [ ] Complete practice exercises
