# Day 30: Final Revision & Cheatsheet

## 🎯 Learning Objectives
- Quick reference for all concepts
- Final review before interviews
- Key patterns to remember
- Common pitfalls to avoid

---

## 📚 JavaScript Fundamentals Cheatsheet

### Variables & Scope

```javascript
// Declaration differences
var x = 1;    // Function-scoped, hoisted, can redeclare
let y = 2;    // Block-scoped, temporal dead zone, no redeclare
const z = 3;  // Block-scoped, cannot reassign (objects are mutable)

// Hoisting
console.log(a); // undefined (var hoisted)
console.log(b); // ReferenceError (TDZ)
var a = 1;
let b = 2;

// Scope chain
function outer() {
    const x = 1;
    function inner() {
        console.log(x); // 1 (closure)
    }
}
```

### Data Types

```javascript
// Primitives (immutable, passed by value)
typeof 'string'     // 'string'
typeof 42           // 'number'
typeof true         // 'boolean'
typeof undefined    // 'undefined'
typeof Symbol()     // 'symbol'
typeof 42n          // 'bigint'
typeof null         // 'object' (bug!)

// Reference types (mutable, passed by reference)
typeof {}           // 'object'
typeof []           // 'object'
typeof function(){} // 'function'

// Type checking
Array.isArray([])           // true
obj instanceof Constructor  // prototype check
Object.prototype.toString.call([]) // '[object Array]'
```

### Type Coercion

```javascript
// Falsy values
false, 0, -0, '', null, undefined, NaN

// Common coercions
'' + 1               // '1'
'5' - 3              // 2
+'42'                // 42
!!'string'           // true
[] + []              // ''
[] + {}              // '[object Object]'
{} + []              // 0 (in console)

// Equality
null == undefined    // true
null === undefined   // false
NaN === NaN          // false (use Number.isNaN)
```

---

## 🔧 Functions

```javascript
// Function types
function named() {}           // Declaration (hoisted)
const expr = function() {};   // Expression
const arrow = () => {};       // Arrow (no this, arguments)

// Parameters
function fn(a, b = 2, ...rest) {}  // Default, rest
fn(1, undefined, 3, 4);            // a=1, b=2, rest=[3,4]

// IIFE
(function() { /* private scope */ })();
(() => { /* arrow IIFE */ })();
```

### `this` Keyword

```javascript
// Rules (in order of precedence)
// 1. new - this = new object
// 2. explicit - call/apply/bind
// 3. implicit - object method
// 4. default - global/undefined (strict)

const obj = {
    name: 'obj',
    regular() { return this.name; },    // 'obj'
    arrow: () => this.name              // undefined (lexical)
};

// Binding
fn.call(obj, arg1, arg2);
fn.apply(obj, [arg1, arg2]);
const bound = fn.bind(obj);
```

### Closures

```javascript
function createCounter() {
    let count = 0;
    return {
        increment: () => ++count,
        getCount: () => count
    };
}

// Common pattern: private variables
const counter = createCounter();
counter.increment(); // 1
counter.getCount();  // 1
// count is private, not accessible directly
```

---

## 🔗 Prototypes & Classes

```javascript
// Prototype chain
const arr = [1, 2, 3];
// arr → Array.prototype → Object.prototype → null

// ES6 Classes (syntactic sugar)
class Animal {
    static count = 0;
    #privateField = 'private';
    
    constructor(name) {
        this.name = name;
        Animal.count++;
    }
    
    speak() {
        return `${this.name} makes a sound`;
    }
}

class Dog extends Animal {
    constructor(name, breed) {
        super(name);
        this.breed = breed;
    }
    
    speak() {
        return `${this.name} barks`;
    }
}

// Check inheritance
dog instanceof Dog      // true
dog instanceof Animal   // true
Dog.prototype.isPrototypeOf(dog) // true
```

---

## ⚡ Async JavaScript

### Event Loop

```
┌─────────────────────────────────────────────────────┐
│ Call Stack (sync) → Microtasks → Macrotasks        │
│                                                     │
│ Microtasks: Promise.then, queueMicrotask, MutationObserver
│ Macrotasks: setTimeout, setInterval, I/O, UI       │
└─────────────────────────────────────────────────────┘
```

```javascript
console.log('1');              // 1. Sync
setTimeout(() => console.log('2'), 0);  // 4. Macrotask
Promise.resolve().then(() => console.log('3')); // 3. Microtask
console.log('4');              // 2. Sync
// Output: 1, 4, 3, 2
```

### Promises

```javascript
// Creating
const promise = new Promise((resolve, reject) => {
    if (success) resolve(value);
    else reject(error);
});

// Chaining
promise
    .then(result => transform(result))
    .catch(error => handle(error))
    .finally(() => cleanup());

// Combinators
Promise.all([p1, p2])      // All succeed or first fail
Promise.race([p1, p2])     // First to settle
Promise.allSettled([p1, p2]) // All settle, with status
Promise.any([p1, p2])      // First success

// Async/await
async function fn() {
    try {
        const result = await promise;
    } catch (error) {
        // handle error
    }
}
```

---

## 📦 Objects & Arrays

### Object Methods

```javascript
// Creation
Object.create(proto)
Object.assign(target, ...sources)
{ ...spread }

// Properties
Object.keys(obj)         // enumerable keys
Object.values(obj)       // enumerable values
Object.entries(obj)      // [key, value] pairs
Object.fromEntries(entries)

// Descriptors
Object.defineProperty(obj, 'key', {
    value, writable, enumerable, configurable,
    get, set
});

// Protection
Object.freeze(obj)       // No changes
Object.seal(obj)         // No add/delete
Object.preventExtensions(obj) // No add
```

### Array Methods

```javascript
// Mutating
push(), pop(), shift(), unshift()
splice(start, deleteCount, ...items)
sort(), reverse(), fill()

// Non-mutating
slice(start, end)
concat(...arrays)
map(fn), filter(fn), reduce(fn, init)
find(fn), findIndex(fn)
some(fn), every(fn)
flat(depth), flatMap(fn)
```

---

## 🎨 ES6+ Features Quick Reference

```javascript
// Destructuring
const { a, b: renamed, c = default } = obj;
const [first, , third, ...rest] = arr;

// Spread/Rest
const newArr = [...arr1, ...arr2];
const newObj = { ...obj1, ...obj2 };
function fn(...args) {} // Rest

// Template literals
`Hello ${name}, result: ${1 + 1}`;
tag`literal ${expression}`;

// Optional chaining & Nullish coalescing
obj?.nested?.prop
arr?.[index]
fn?.()
value ?? defaultValue  // Only null/undefined

// Modules
export const x = 1;
export default fn;
import { x } from './module';
import * as module from './module';
```

---

## 🔄 Common Patterns

### Debounce & Throttle

```javascript
// Debounce: Wait until calm
function debounce(fn, delay) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

// Throttle: Max once per interval
function throttle(fn, interval) {
    let lastTime = 0;
    return function(...args) {
        const now = Date.now();
        if (now - lastTime >= interval) {
            lastTime = now;
            fn.apply(this, args);
        }
    };
}
```

### Memoization

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

### Currying

```javascript
function curry(fn) {
    return function curried(...args) {
        if (args.length >= fn.length) {
            return fn.apply(this, args);
        }
        return function(...more) {
            return curried.apply(this, [...args, ...more]);
        };
    };
}
```

### Deep Clone

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

---

## ⚠️ Common Pitfalls

```javascript
// 1. Floating point
0.1 + 0.2 === 0.3           // false!
Math.abs(0.1 + 0.2 - 0.3) < 0.0001 // true

// 2. typeof null
typeof null === 'object'     // true (bug)
obj !== null && typeof obj === 'object' // proper check

// 3. Array comparison
[1, 2] === [1, 2]           // false (different references)
JSON.stringify(a) === JSON.stringify(b) // works for simple cases

// 4. this in callbacks
obj.method.call(otherObj);  // this = otherObj
element.addEventListener('click', obj.method); // this = element
element.addEventListener('click', () => obj.method()); // works

// 5. Async in loops
// Wrong - all iterations share same i
for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100); // 3, 3, 3
}
// Right - use let or closure
for (let i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100); // 0, 1, 2
}

// 6. Object default parameters
function fn(obj = {}) { }  // Creates new object each time
const DEFAULT = {};
function fn(obj = DEFAULT) { } // Shares same object (careful!)

// 7. Array from split
'hello'.split('');          // ['h', 'e', 'l', 'l', 'o']
[...'hello'];               // Same, but handles emoji better
```

---

## 📋 Interview Quick Tips

```
╔════════════════════════════════════════════════════════════════════╗
║                    QUICK INTERVIEW TIPS                             ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  APPROACH:                                                          ║
║  1. Listen carefully, ask clarifying questions                      ║
║  2. Think out loud as you work                                      ║
║  3. Start with brute force, then optimize                          ║
║  4. Test with examples and edge cases                               ║
║  5. Discuss time/space complexity                                   ║
║                                                                     ║
║  KEY TOPICS TO MASTER:                                              ║
║  □ Closures and scope                                               ║
║  □ this keyword behavior                                            ║
║  □ Prototypes and inheritance                                       ║
║  □ Event loop and async                                             ║
║  □ Higher-order functions                                           ║
║  □ ES6+ features                                                    ║
║                                                                     ║
║  COMMON IMPLEMENTATIONS:                                            ║
║  □ bind, call, apply                                                ║
║  □ Promise.all, Promise.race                                        ║
║  □ debounce, throttle                                               ║
║  □ deep clone, deep equal                                           ║
║  □ EventEmitter                                                     ║
║  □ memoize, curry                                                   ║
║                                                                     ║
║  RED FLAGS TO AVOID:                                                ║
║  □ Silent when stuck (keep talking!)                                ║
║  □ Not asking questions                                             ║
║  □ Not testing code                                                 ║
║  □ Ignoring edge cases                                              ║
║  □ Overcomplicating solutions                                       ║
║                                                                     ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## 🎉 Congratulations!

You've completed the 30-Day JavaScript Mastery Plan! 

### What You've Learned:

**Week 1 - Core Foundations:**
- JS Engine & Runtime
- Variables, Scope, Hoisting
- Data Types & Memory
- Type Coercion & Equality
- Functions (declarations, expressions, arrow)
- `this` keyword
- Closures

**Week 2 - Intermediate:**
- Prototypes & Inheritance
- Objects & Arrays Deep Dive
- Event Loop
- Promises & Async/Await
- Modules
- Error Handling

**Week 3 - Advanced:**
- Currying & Composition
- Debounce & Throttle
- DOM & Events
- Design Patterns
- Memory Management
- Proxy, Reflect, Generators
- Functional Programming

**Week 4 - Interview Prep:**
- Polyfills & Implementations
- Output Prediction
- System Design
- Node.js Internals
- Security
- Testing
- Mini Project
- Mock Interviews

---

## ✅ Day 30 Checklist

- [ ] Review all cheatsheet sections
- [ ] Practice implementing key functions
- [ ] Review common pitfalls
- [ ] Do a final mock interview
- [ ] Get a good night's sleep!

**You're ready for your JavaScript interviews. Good luck! 🚀**
