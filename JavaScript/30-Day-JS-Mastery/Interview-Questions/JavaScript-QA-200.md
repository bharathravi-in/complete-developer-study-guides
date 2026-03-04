# JavaScript Interview Q&A - 200+ Questions

A comprehensive collection of JavaScript interview questions organized by topic.

---

## 📚 Table of Contents

1. [Fundamentals](#fundamentals)
2. [Variables & Scope](#variables--scope)
3. [Data Types](#data-types)
4. [Functions](#functions)
5. [this Keyword](#this-keyword)
6. [Closures](#closures)
7. [Prototypes & Inheritance](#prototypes--inheritance)
8. [Objects & Arrays](#objects--arrays)
9. [Async JavaScript](#async-javascript)
10. [ES6+ Features](#es6-features)
11. [DOM & Events](#dom--events)
12. [Error Handling](#error-handling)
13. [Performance & Memory](#performance--memory)
14. [Design Patterns](#design-patterns)
15. [Node.js](#nodejs)
16. [Security](#security)

---

## Fundamentals

### Q1: What is JavaScript and how does it work?
**A:** JavaScript is a high-level, interpreted programming language. It runs on the V8 (Chrome, Node) or SpiderMonkey (Firefox) engine. The engine parses code into an AST, compiles it to bytecode or machine code (JIT compilation), and executes it.

### Q2: Explain the difference between compiled and interpreted languages.
**A:** Compiled languages (C, Java) convert entire source code to machine code before execution. Interpreted languages execute code line by line. JavaScript is technically JIT-compiled - it's interpreted first, then hot code paths are compiled for optimization.

### Q3: What is the call stack?
**A:** The call stack is a LIFO data structure that tracks function execution. When a function is called, it's pushed onto the stack. When it returns, it's popped off. Stack overflow occurs when the stack exceeds its size limit (usually from infinite recursion).

### Q4: Explain JavaScript's single-threaded nature.
**A:** JavaScript has one call stack and one memory heap. It can only execute one piece of code at a time. Async operations are handled via the event loop, callbacks, and Web APIs, not by creating new threads.

### Q5: What is "use strict"?
**A:** `"use strict"` enables strict mode, which:
- Prevents using undeclared variables
- Throws errors on assignments to non-writable properties
- Disallows duplicate parameters
- Makes `this` undefined in functions (not global)
- Prevents `with` statements

---

## Variables & Scope

### Q6: What's the difference between var, let, and const?
**A:**
- `var`: Function-scoped, hoisted with undefined, can redeclare
- `let`: Block-scoped, in TDZ until declaration, cannot redeclare
- `const`: Block-scoped, in TDZ, cannot reassign (but objects are mutable)

### Q7: What is hoisting?
**A:** Hoisting moves declarations to the top of their scope during compilation. `var` declarations are hoisted with value `undefined`. `let/const` are hoisted but remain in the Temporal Dead Zone until their declaration is executed.

### Q8: What is the Temporal Dead Zone (TDZ)?
**A:** The TDZ is the time between entering a scope and the variable declaration being executed. Accessing a `let/const` variable in its TDZ throws a ReferenceError.

```javascript
console.log(x); // ReferenceError
let x = 10;
```

### Q9: Explain lexical scope.
**A:** Lexical scope means a function's scope is determined by where it's defined, not where it's called. Inner functions can access outer function variables, forming a scope chain.

### Q10: What is block scope?
**A:** Block scope means variables declared with `let/const` are only accessible within the block `{}` where they're declared. `var` ignores block scope.

### Q11: Can you modify a const object?
**A:** Yes. `const` prevents reassignment of the variable, not mutation of the value. Object properties can be modified:
```javascript
const obj = { a: 1 };
obj.a = 2; // OK
obj = {};  // TypeError
```

### Q12: What are global variables and why should you avoid them?
**A:** Global variables are accessible everywhere. Avoid them because they:
- Cause naming conflicts
- Make code harder to maintain
- Can be accidentally modified
- Pollute global namespace
- Make testing difficult

---

## Data Types

### Q13: What are JavaScript's primitive types?
**A:** String, Number, Boolean, null, undefined, Symbol, BigInt. Primitives are immutable and compared by value.

### Q14: Why does typeof null return 'object'?
**A:** It's a historical bug from JavaScript's first implementation. Null was represented with the same type tag as objects. It wasn't fixed because it would break existing code.

### Q15: What's the difference between null and undefined?
**A:**
- `undefined`: Variable declared but not assigned, or missing property
- `null`: Intentionally empty/no value, explicitly assigned
- `typeof undefined` = 'undefined'
- `typeof null` = 'object'
- `null == undefined` is true

### Q16: What is NaN? How do you check for it?
**A:** NaN (Not a Number) results from invalid numeric operations. It's unique in that `NaN !== NaN`. Check with `Number.isNaN()` (recommended) or `isNaN()` (coerces first).

### Q17: What is Symbol? Give use cases.
**A:** Symbol is a unique, immutable primitive. Use cases:
- Unique object keys (no collisions)
- Defining private-like properties
- Well-known symbols (Symbol.iterator, Symbol.toStringTag)

### Q18: Explain type coercion with examples.
**A:**
```javascript
'5' + 3      // '53' (number to string)
'5' - 3      // 2 (string to number)
!!'hello'    // true (to boolean)
[] + []      // '' (arrays to strings)
[] == false  // true (both coerce to 0)
```

### Q19: What are truthy and falsy values?
**A:** Falsy: `false`, `0`, `-0`, `''`, `null`, `undefined`, `NaN`
Everything else is truthy (including `[]`, `{}`, `'0'`).

### Q20: How do you compare objects for equality?
**A:** `===` checks reference equality. For deep equality, use:
- `JSON.stringify()` (simple cases)
- Custom recursive function
- Libraries like Lodash `_.isEqual()`

---

## Functions

### Q21: What's the difference between function declarations and expressions?
**A:**
```javascript
// Declaration - hoisted
function greet() {}

// Expression - not hoisted
const greet = function() {};
```

### Q22: What are arrow functions and their differences?
**A:** Arrow functions:
- Shorter syntax: `() => {}`
- No own `this` (lexical binding)
- No `arguments` object
- Cannot be constructors
- Cannot be generators
- No `prototype` property

### Q23: What are higher-order functions?
**A:** Functions that take functions as arguments or return functions. Examples: `map`, `filter`, `reduce`, decorators.

### Q24: Explain rest parameters vs arguments object.
**A:**
```javascript
function fn(...rest) {}  // Real array, can use array methods
function fn() { arguments }  // Array-like, no array methods
```
Arrow functions don't have `arguments`.

### Q25: What are default parameters?
**A:**
```javascript
function fn(a, b = 2, c = b + 1) {}
fn(1);  // a=1, b=2, c=3
fn(1, undefined);  // b still defaults to 2
```

### Q26: What is a pure function?
**A:** A function that:
1. Given same inputs, always returns same output
2. Has no side effects (doesn't modify external state)

### Q27: What is function currying?
**A:** Transforming a function with multiple arguments into a sequence of functions each with a single argument:
```javascript
const add = a => b => a + b;
add(1)(2); // 3
```

### Q28: Explain the spread operator in function calls.
**A:**
```javascript
const args = [1, 2, 3];
Math.max(...args);  // Same as Math.max(1, 2, 3)
```

### Q29: What is an IIFE and why use it?
**A:** Immediately Invoked Function Expression:
```javascript
(function() { /* private scope */ })();
```
Uses: Creating private scope, avoiding global pollution, module pattern.

### Q30: What is recursion? What problems does it solve?
**A:** A function calling itself. Solves problems with recursive structure: tree traversal, factorial, Fibonacci, deep cloning.

---

## this Keyword

### Q31: Explain how 'this' works in JavaScript.
**A:** `this` depends on how a function is called:
1. `new` → new object
2. `call/apply/bind` → specified object
3. Method call (obj.fn()) → the object
4. Regular function → global or undefined (strict)

### Q32: What does 'this' refer to in an arrow function?
**A:** Arrow functions don't have their own `this`. They inherit `this` from the enclosing lexical scope (where they're defined).

### Q33: Explain call(), apply(), and bind().
**A:**
```javascript
fn.call(obj, arg1, arg2);    // Calls immediately
fn.apply(obj, [arg1, arg2]); // Calls immediately, array args
const bound = fn.bind(obj);  // Returns new function
```

### Q34: What is 'this' inside a class method?
**A:** In class methods, `this` refers to the instance when called as `instance.method()`. If passed as callback, `this` may be lost unless arrow function or bind is used.

### Q35: How do you fix 'this' in callbacks?
**A:**
```javascript
// Arrow function (lexical this)
element.addEventListener('click', () => this.method());

// Bind
element.addEventListener('click', this.method.bind(this));

// Variable
const self = this;
element.addEventListener('click', function() { self.method(); });
```

---

## Closures

### Q36: What is a closure?
**A:** A closure is a function that remembers variables from its outer scope even after the outer function has returned. The inner function "closes over" the outer variables.

### Q37: Give practical examples of closures.
**A:**
- Data privacy (private variables)
- Factory functions
- Callbacks with access to outer scope
- Memoization
- Currying

### Q38: How do closures relate to the loop problem?
**A:**
```javascript
// Problem: all callbacks share same i
for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 0); // 3, 3, 3
}

// Solution: closure with let (block scope) or IIFE
for (let i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 0); // 0, 1, 2
}
```

### Q39: Can closures cause memory leaks?
**A:** Yes, if closures hold references to large objects that could otherwise be garbage collected. To fix, set variables to null when no longer needed.

### Q40: Write a function using closure for private variables.
**A:**
```javascript
function createCounter() {
    let count = 0; // private
    return {
        increment: () => ++count,
        getCount: () => count
    };
}
```

---

## Prototypes & Inheritance

### Q41: What is the prototype chain?
**A:** Each object has an internal link to another object (its prototype). When accessing a property, JS looks up the chain until found or reaching null. Example: `arr → Array.prototype → Object.prototype → null`

### Q42: Difference between __proto__ and prototype?
**A:**
- `prototype`: Property on constructor functions, becomes `__proto__` of instances
- `__proto__`: Internal link of an object to its prototype (deprecated, use `Object.getPrototypeOf()`)

### Q43: How does 'new' operator work?
**A:**
1. Creates new empty object
2. Sets object's `__proto__` to constructor's `prototype`
3. Executes constructor with `this` = new object
4. Returns object (or returned object if constructor returns one)

### Q44: How do you create an object with no prototype?
**A:**
```javascript
const obj = Object.create(null);
obj.__proto__ // undefined
```

### Q45: Explain ES6 classes vs prototypes.
**A:** ES6 classes are syntactic sugar over prototypes. They provide cleaner syntax but work the same way underneath:
```javascript
class Dog extends Animal {
    constructor() { super(); }
}
// Equivalent to prototype-based inheritance
```

### Q46: What is Object.create()?
**A:** Creates new object with specified prototype:
```javascript
const proto = { greet() { return 'Hello'; } };
const obj = Object.create(proto);
obj.greet(); // 'Hello'
```

### Q47: How do you check if a property is own or inherited?
**A:**
```javascript
obj.hasOwnProperty('prop')       // true for own
'prop' in obj                    // true for own or inherited
Object.hasOwn(obj, 'prop')       // ES2022 - preferred
```

### Q48: What is method overriding?
**A:** When a subclass defines a method with the same name as parent, the subclass method is used. Use `super.method()` to call parent's version.

---

## Objects & Arrays

### Q49: What's the difference between shallow and deep copy?
**A:**
- Shallow: Copies only first level; nested objects share references
- Deep: Recursively copies all levels; completely independent copy

```javascript
const shallow = { ...obj };      // Shallow
const deep = JSON.parse(JSON.stringify(obj)); // Deep (with limitations)
```

### Q50: What are getter and setter properties?
**A:**
```javascript
const obj = {
    _value: 0,
    get value() { return this._value; },
    set value(v) { this._value = v > 0 ? v : 0; }
};
```

### Q51: What is Object.freeze() vs Object.seal()?
**A:**
- `freeze`: No add, delete, or modify. Truly immutable.
- `seal`: No add or delete, but can modify existing properties.

### Q52: How do you merge objects?
**A:**
```javascript
Object.assign(target, source1, source2);  // Mutates target
const merged = { ...obj1, ...obj2 };      // New object
```

### Q53: Difference between map(), forEach(), and for...of?
**A:**
- `forEach`: Executes function on each element, returns undefined
- `map`: Returns new array with transformed elements
- `for...of`: Loop statement, can use break/continue

### Q54: Explain reduce() with examples.
**A:**
```javascript
// Sum
[1, 2, 3].reduce((acc, val) => acc + val, 0); // 6

// Grouping
users.reduce((acc, user) => {
    (acc[user.role] ||= []).push(user);
    return acc;
}, {});
```

### Q55: What is array destructuring?
**A:**
```javascript
const [first, second, ...rest] = [1, 2, 3, 4];
const [a, , c] = [1, 2, 3]; // Skip elements
const [x = 0] = []; // Default value
```

### Q56: How do you remove duplicates from an array?
**A:**
```javascript
[...new Set(array)]
array.filter((item, i) => array.indexOf(item) === i)
```

### Q57: What is a sparse array?
**A:** An array with "holes" (missing elements):
```javascript
const arr = [1, , 3]; // length 3, index 1 is empty
const arr2 = new Array(3); // [empty × 3]
```
Methods like `forEach` skip holes; `for` loop doesn't.

---

## Async JavaScript

### Q58: Explain the event loop.
**A:** The event loop enables async behavior:
1. Execute call stack
2. Process all microtasks (Promise callbacks, queueMicrotask)
3. Process one macrotask (setTimeout, I/O)
4. Repeat

### Q59: What is callback hell and how to avoid it?
**A:** Nested callbacks making code hard to read:
```javascript
doA(a => {
    doB(a, b => {
        doC(b, c => {})
    })
})
```
Solutions: Promises, async/await, named functions.

### Q60: Explain Promises.
**A:** A Promise represents eventual completion/failure of async operation:
```javascript
const p = new Promise((resolve, reject) => {
    if (success) resolve(value);
    else reject(error);
});
p.then(value => {}).catch(err => {});
```

### Q61: What states can a Promise be in?
**A:** 
- Pending: Initial state
- Fulfilled: Operation succeeded
- Rejected: Operation failed
Once settled (fulfilled/rejected), state is immutable.

### Q62: Explain Promise.all vs Promise.race vs Promise.allSettled.
**A:**
- `all`: Resolves when all resolve, rejects on first rejection
- `race`: Resolves/rejects with first settled promise
- `allSettled`: Waits for all to settle, never rejects

### Q63: What is async/await?
**A:** Syntactic sugar for Promises:
```javascript
async function fn() {
    try {
        const result = await fetchData();
        return result;
    } catch (e) {
        // handle error
    }
}
```

### Q64: Can you use await in regular functions?
**A:** No, `await` can only be used inside `async` functions or at top level in modules (top-level await).

### Q65: What are microtasks vs macrotasks?
**A:**
- Microtasks: Promise.then, queueMicrotask (higher priority)
- Macrotasks: setTimeout, setInterval, I/O (lower priority)
All microtasks run before next macrotask.

### Q66: Explain process.nextTick vs setImmediate (Node.js).
**A:**
- `process.nextTick`: Runs after current operation, before event loop
- `setImmediate`: Runs in check phase of event loop

### Q67: What is a Promise executor?
**A:** The function passed to `new Promise((resolve, reject) => {})`. It runs synchronously when Promise is created.

---

## ES6+ Features

### Q68: What are template literals?
**A:** String literals with embedded expressions:
```javascript
`Hello ${name}!`
`Line 1
Line 2`
```

### Q69: Explain destructuring.
**A:**
```javascript
const { a, b: renamed, c = default } = obj;
const [first, ...rest] = array;
```

### Q70: What is the spread operator?
**A:** Expands iterables:
```javascript
const arr = [...arr1, ...arr2];
const obj = { ...obj1, ...obj2 };
fn(...args);
```

### Q71: What are Maps and Sets?
**A:**
- `Map`: Key-value pairs with any type as key, ordered, iterable
- `Set`: Unique values only, ordered, iterable

### Q72: What is WeakMap/WeakSet?
**A:** Same as Map/Set but:
- Keys must be objects
- Keys are weakly held (garbage collectable)
- Not iterable, no size property
Use for: caching without memory leaks, private data.

### Q73: What is optional chaining (?.) ?
**A:** Safely access nested properties:
```javascript
obj?.prop?.nested  // undefined if any is nullish
arr?.[0]
fn?.()
```

### Q74: What is nullish coalescing (??)?
**A:** Returns right side only if left is null/undefined:
```javascript
null ?? 'default'  // 'default'
0 ?? 'default'     // 0 (unlike ||)
'' ?? 'default'    // '' (unlike ||)
```

### Q75: What is a Proxy?
**A:** Wraps object to intercept operations:
```javascript
const proxy = new Proxy(target, {
    get(target, prop) { },
    set(target, prop, value) { }
});
```

### Q76: Explain generators.
**A:** Functions that can pause/resume:
```javascript
function* gen() {
    yield 1;
    yield 2;
}
const g = gen();
g.next(); // { value: 1, done: false }
```

### Q77: What are iterators?
**A:** Objects implementing `next()` returning `{ value, done }`. Making object iterable:
```javascript
obj[Symbol.iterator] = function* () {
    yield* Object.values(this);
};
```

---

## DOM & Events

### Q78: Explain event bubbling and capturing.
**A:**
- Capture: Event travels from window down to target
- Bubble: Event travels from target up to window
Default is bubbling. Use `addEventListener(type, handler, true)` for capture.

### Q79: What is event delegation?
**A:** Attach one listener to parent instead of many to children:
```javascript
parent.addEventListener('click', e => {
    if (e.target.matches('.child')) {
        // handle
    }
});
```
Benefits: Fewer listeners, handles dynamic elements.

### Q80: Difference between e.target and e.currentTarget?
**A:**
- `e.target`: Element that triggered event (clicked element)
- `e.currentTarget`: Element listener is attached to

### Q81: How to stop event propagation?
**A:**
- `e.stopPropagation()`: Stops bubbling/capturing
- `e.stopImmediatePropagation()`: Also stops other handlers on same element
- `e.preventDefault()`: Prevents default action (not propagation)

### Q82: What is the difference between innerHTML and textContent?
**A:**
- `innerHTML`: Gets/sets HTML, can cause XSS
- `textContent`: Gets/sets text only, escapes HTML, safer

### Q83: How to create elements efficiently?
**A:**
```javascript
// Use DocumentFragment for batch operations
const fragment = document.createDocumentFragment();
items.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item;
    fragment.appendChild(li);
});
list.appendChild(fragment); // Single reflow
```

### Q84: What are custom events?
**A:**
```javascript
const event = new CustomEvent('myEvent', { 
    detail: { data: 'value' },
    bubbles: true 
});
element.dispatchEvent(event);
element.addEventListener('myEvent', e => e.detail.data);
```

---

## Error Handling

### Q85: Explain try/catch/finally.
**A:**
```javascript
try {
    // code that might throw
} catch (error) {
    // handle error
} finally {
    // always runs (cleanup)
}
```

### Q86: What is the difference between throw and reject?
**A:**
- `throw`: Synchronous, caught by try/catch
- `reject`: Async (Promise), caught by .catch() or try/catch with await

### Q87: How do you create custom errors?
**A:**
```javascript
class ValidationError extends Error {
    constructor(message) {
        super(message);
        this.name = 'ValidationError';
    }
}
```

### Q88: What is the global error handler?
**A:**
```javascript
// Browser
window.onerror = (msg, url, line, col, error) => {};
window.addEventListener('unhandledrejection', e => {});

// Node
process.on('uncaughtException', err => {});
process.on('unhandledRejection', err => {});
```

---

## Performance & Memory

### Q89: What is garbage collection?
**A:** Automatic memory management. JS uses mark-and-sweep: marks reachable objects from roots (global, stack), sweeps unreachable objects.

### Q90: How do you prevent memory leaks?
**A:**
- Remove event listeners
- Clear intervals/timeouts
- Avoid global variables
- Be careful with closures
- Use WeakMap for derived data

### Q91: What is debouncing vs throttling?
**A:**
- Debounce: Execute once after delay since last call (search input)
- Throttle: Execute at most once per interval (scroll events)

### Q92: What are Web Workers?
**A:** Background threads for heavy computation:
```javascript
const worker = new Worker('worker.js');
worker.postMessage(data);
worker.onmessage = e => e.data;
```
No DOM access, communication via messages.

### Q93: What is lazy loading?
**A:** Loading resources on demand:
```javascript
// Dynamic import
const module = await import('./module.js');

// Images
<img loading="lazy" src="image.jpg">

// Intersection Observer for custom behavior
```

### Q94: What is memoization?
**A:** Caching function results:
```javascript
function memoize(fn) {
    const cache = new Map();
    return function(...args) {
        const key = JSON.stringify(args);
        if (!cache.has(key)) cache.set(key, fn(...args));
        return cache.get(key);
    };
}
```

---

## Design Patterns

### Q95: What is the Module pattern?
**A:** Encapsulate private state, expose public API:
```javascript
const Module = (function() {
    let private = 0;
    return {
        increment: () => ++private,
        get: () => private
    };
})();
```

### Q96: What is the Singleton pattern?
**A:** Class with only one instance:
```javascript
class Singleton {
    static instance;
    static getInstance() {
        if (!Singleton.instance) {
            Singleton.instance = new Singleton();
        }
        return Singleton.instance;
    }
}
```

### Q97: What is the Observer pattern?
**A:** Objects (observers) subscribe to subject, notified of changes:
```javascript
class Subject {
    observers = [];
    subscribe(fn) { this.observers.push(fn); }
    notify(data) { this.observers.forEach(fn => fn(data)); }
}
```

### Q98: What is the Factory pattern?
**A:** Creates objects without specifying exact class:
```javascript
function createUser(type) {
    switch(type) {
        case 'admin': return new Admin();
        case 'user': return new User();
    }
}
```

### Q99: What is dependency injection?
**A:** Providing dependencies from outside rather than creating internally:
```javascript
class UserService {
    constructor(database, logger) {
        this.db = database;
        this.logger = logger;
    }
}
```
Benefits: Testability, loose coupling.

---

## Node.js

### Q100: What is the Node.js event loop?
**A:** Similar to browser but with phases:
1. Timers (setTimeout/setInterval)
2. Pending callbacks (I/O)
3. Idle, prepare
4. Poll (I/O)
5. Check (setImmediate)
6. Close callbacks

### Q101: What are Streams in Node.js?
**A:** Handle data piece by piece:
- Readable: fs.createReadStream
- Writable: fs.createWriteStream
- Duplex: Both (sockets)
- Transform: Modify data (compression)

### Q102: CommonJS vs ES Modules?
**A:**
```javascript
// CommonJS (Node default)
const x = require('./module');
module.exports = x;

// ESM
import x from './module.js';
export default x;
```
ESM: async loading, static analysis, tree shaking.

### Q103: What is the Buffer class?
**A:** Handles binary data outside V8 heap:
```javascript
const buf = Buffer.from('hello');
const buf2 = Buffer.alloc(10);
```

### Q104: Explain cluster module.
**A:** Fork multiple worker processes to utilize multiple CPUs:
```javascript
if (cluster.isMaster) {
    for (let i = 0; i < cpus; i++) cluster.fork();
} else {
    // Worker code
}
```

---

## Security

### Q105: What is XSS and how to prevent it?
**A:** Cross-Site Scripting: injecting malicious scripts.
Prevention:
- Escape user input
- Use textContent not innerHTML
- Content Security Policy
- HTTPOnly cookies

### Q106: What is CSRF and how to prevent it?
**A:** Cross-Site Request Forgery: tricks user into unwanted actions.
Prevention:
- CSRF tokens
- SameSite cookies
- Check Origin/Referer headers

### Q107: What are secure cookie attributes?
**A:**
- `HttpOnly`: No JS access
- `Secure`: HTTPS only
- `SameSite`: Control cross-site sending
- `Path`, `Domain`: Restrict scope

### Q108: How do you validate user input?
**A:**
- Whitelist allowed values
- Use regex validation
- Sanitize HTML with libraries (DOMPurify)
- Parameterized queries for DB

---

## Quick Fire Questions

### Q109: What does `'b' + 'a' + + 'a' + 'a'` return?
**A:** "baNaNa" (+ 'a' is NaN)

### Q110: What is `[] + []`?
**A:** "" (empty string)

### Q111: What is `{} + []`?
**A:** 0 (in console, {} is empty block)

### Q112: What is `typeof typeof 1`?
**A:** "string"

### Q113: What is `[1, 2] + [3, 4]`?
**A:** "1,23,4" (string concatenation)

### Q114: Is JavaScript pass by reference or value?
**A:** Always pass by value. For objects, the value is a reference (copy of pointer).

### Q115: What is a polyfill?
**A:** Code providing modern functionality on older browsers that don't support it natively.

### Q116: Difference between Object.keys and Object.getOwnPropertyNames?
**A:**
- `keys`: Enumerable own properties only
- `getOwnPropertyNames`: All own properties (including non-enumerable)

### Q117: What is CORS?
**A:** Cross-Origin Resource Sharing. Browser security restricting cross-origin requests. Server must include Access-Control-Allow-Origin header.

### Q118: What is the difference between == null and === null?
**A:**
```javascript
x == null   // true for null OR undefined
x === null  // true for null only
```

### Q119: How to check if variable is array?
**A:** `Array.isArray(arr)` is the reliable method.

### Q120: What is event.preventDefault()?
**A:** Prevents default browser behavior (form submit, link follow) without stopping propagation.

---

## Coding Questions

### Q121: Implement Array.prototype.map
```javascript
Array.prototype.myMap = function(callback) {
    const result = [];
    for (let i = 0; i < this.length; i++) {
        if (i in this) { // Handle sparse arrays
            result[i] = callback(this[i], i, this);
        }
    }
    return result;
};
```

### Q122: Implement bind()
```javascript
Function.prototype.myBind = function(context, ...args) {
    const fn = this;
    return function(...newArgs) {
        return fn.apply(context, [...args, ...newArgs]);
    };
};
```

### Q123: Implement debounce
```javascript
function debounce(fn, delay) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}
```

### Q124: Implement throttle
```javascript
function throttle(fn, limit) {
    let lastCall = 0;
    return function(...args) {
        const now = Date.now();
        if (now - lastCall >= limit) {
            lastCall = now;
            fn.apply(this, args);
        }
    };
}
```

### Q125: Flatten nested array
```javascript
function flatten(arr) {
    return arr.reduce((flat, item) => 
        flat.concat(Array.isArray(item) ? flatten(item) : item), []);
}
```

### Q126: Deep clone object
```javascript
function deepClone(obj, seen = new WeakMap()) {
    if (obj === null || typeof obj !== 'object') return obj;
    if (seen.has(obj)) return seen.get(obj);
    
    const clone = Array.isArray(obj) ? [] : {};
    seen.set(obj, clone);
    
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            clone[key] = deepClone(obj[key], seen);
        }
    }
    return clone;
}
```

### Q127: Implement Promise.all
```javascript
function promiseAll(promises) {
    return new Promise((resolve, reject) => {
        const results = [];
        let completed = 0;
        
        promises.forEach((p, i) => {
            Promise.resolve(p).then(value => {
                results[i] = value;
                if (++completed === promises.length) resolve(results);
            }).catch(reject);
        });
        
        if (promises.length === 0) resolve([]);
    });
}
```

### Q128: Implement EventEmitter
```javascript
class EventEmitter {
    constructor() { this.events = {}; }
    
    on(event, fn) {
        (this.events[event] ||= []).push(fn);
    }
    
    off(event, fn) {
        this.events[event] = this.events[event]?.filter(f => f !== fn);
    }
    
    emit(event, ...args) {
        this.events[event]?.forEach(fn => fn(...args));
    }
}
```

### Q129: Find duplicates in array
```javascript
function findDuplicates(arr) {
    return arr.filter((item, index) => arr.indexOf(item) !== index);
}

// Or using Set
function findDuplicates(arr) {
    const seen = new Set();
    return [...new Set(arr.filter(x => seen.has(x) || !seen.add(x)))];
}
```

### Q130: Implement memoization
```javascript
function memoize(fn) {
    const cache = new Map();
    return function(...args) {
        const key = JSON.stringify(args);
        if (!cache.has(key)) {
            cache.set(key, fn.apply(this, args));
        }
        return cache.get(key);
    };
}
```

---

## Advanced Questions

### Q131-140: See Day 23 (Output Prediction)
### Q141-150: See Day 24 (System Design)
### Q151-160: See Day 25 (Node.js Internals)
### Q161-170: See Day 26 (Security)
### Q171-180: See Day 27 (Testing)

---

## Behavioral Questions

### Q181: Tell me about a challenging bug you fixed.
Use STAR method (Situation, Task, Action, Result).

### Q182: How do you stay updated with JavaScript?
TC39 proposals, MDN, newsletters, conferences.

### Q183: Describe a time you disagreed with a teammate.
Focus on collaboration and constructive resolution.

### Q184: How do you handle code reviews?
Be objective, suggest improvements, learn from feedback.

### Q185: What's your favorite ES6+ feature and why?
Personal answer showing depth of knowledge.

---

## Final Tips

1. **Understand fundamentals** thoroughly (closures, this, prototypes)
2. **Practice coding** without IDE help
3. **Think out loud** during interviews
4. **Ask clarifying questions** before coding
5. **Test your code** with edge cases
6. **Know time/space complexity** of your solutions
7. **Be honest** about what you don't know
8. **Stay calm** and communicate clearly

Good luck with your interviews! 🚀
