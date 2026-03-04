# Day 21: Functional Programming Concepts

## 🎯 Learning Objectives
- Understand FP core principles
- Master pure functions and immutability
- Learn higher-order functions
- Apply map, filter, reduce effectively
- Use function composition and pipelines

---

## 🧱 Core FP Principles

```javascript
/*
╔════════════════════════════════════════════════════════════════════╗
║                 FUNCTIONAL PROGRAMMING PILLARS                      ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  1. PURE FUNCTIONS                                                  ║
║     • Same input → Same output                                      ║
║     • No side effects                                               ║
║                                                                     ║
║  2. IMMUTABILITY                                                    ║
║     • Data never changes                                            ║
║     • Create new data instead                                       ║
║                                                                     ║
║  3. FIRST-CLASS FUNCTIONS                                           ║
║     • Functions as values                                           ║
║     • Pass/return functions                                         ║
║                                                                     ║
║  4. DECLARATIVE CODE                                                ║
║     • Describe WHAT, not HOW                                        ║
║     • Abstract away control flow                                    ║
║                                                                     ║
╚════════════════════════════════════════════════════════════════════╝
*/
```

---

## ✨ Pure Functions

A pure function always returns the same output for the same input and has no side effects.

```javascript
// ❌ Impure - depends on external state
let counter = 0;
function incrementCounter() {
    return ++counter;  // Modifies external state
}

// ✅ Pure
function increment(n) {
    return n + 1;  // No external state
}

// ❌ Impure - side effect (console.log)
function logAndReturn(x) {
    console.log(x);  // Side effect
    return x;
}

// ❌ Impure - depends on Date
function getTimestamp() {
    return Date.now();  // Different each time
}

// ❌ Impure - mutates input
function addItem(arr, item) {
    arr.push(item);  // Mutates original array
    return arr;
}

// ✅ Pure
function addItemPure(arr, item) {
    return [...arr, item];  // Returns new array
}

// ❌ Impure - mutates nested object
function updateUser(user, name) {
    user.name = name;  // Mutation
    return user;
}

// ✅ Pure
function updateUserPure(user, name) {
    return { ...user, name };  // Returns new object
}

/*
BENEFITS OF PURE FUNCTIONS:
• Testable - no setup needed
• Cacheable - memoization
• Parallelizable - no shared state
• Predictable - easier to reason about
*/

// Memoization works because of purity
function memoize(fn) {
    const cache = new Map();
    return function(...args) {
        const key = JSON.stringify(args);
        if (cache.has(key)) {
            return cache.get(key);
        }
        const result = fn(...args);
        cache.set(key, result);
        return result;
    };
}

const pureAdd = (a, b) => a + b;
const memoizedAdd = memoize(pureAdd);
memoizedAdd(1, 2); // Computed
memoizedAdd(1, 2); // Cached
```

---

## 🧊 Immutability

Never modify data in place. Always create new copies.

```javascript
// Arrays - Immutable operations
const arr = [1, 2, 3];

// ❌ Mutating methods
arr.push(4);      // Modifies arr
arr.pop();        // Modifies arr
arr.splice(1, 1); // Modifies arr
arr.sort();       // Modifies arr

// ✅ Non-mutating equivalents
const added = [...arr, 4];
const removed = arr.slice(0, -1);
const spliced = [...arr.slice(0, 1), ...arr.slice(2)];
const sorted = [...arr].sort();

// Insert at index
const insertAt = (arr, index, item) => [
    ...arr.slice(0, index),
    item,
    ...arr.slice(index)
];

// Remove at index
const removeAt = (arr, index) => [
    ...arr.slice(0, index),
    ...arr.slice(index + 1)
];

// Update at index
const updateAt = (arr, index, item) => [
    ...arr.slice(0, index),
    item,
    ...arr.slice(index + 1)
];

// Objects - Immutable operations
const user = { name: 'John', age: 30, address: { city: 'NYC' } };

// ❌ Mutating
user.name = 'Jane';
user.address.city = 'LA';

// ✅ Immutable updates
const updated = { ...user, name: 'Jane' };

// Deep update
const deepUpdated = {
    ...user,
    address: { ...user.address, city: 'LA' }
};

// Removing a property
const { age, ...withoutAge } = user;

// Conditional update
const maybeUpdate = (obj, condition, updates) =>
    condition ? { ...obj, ...updates } : obj;

// Object.freeze (shallow)
const frozen = Object.freeze({ a: 1, b: { c: 2 } });
// frozen.a = 2;      // Error in strict mode
frozen.b.c = 3;       // Works! (shallow freeze)

// Deep freeze
function deepFreeze(obj) {
    Object.keys(obj).forEach(key => {
        if (typeof obj[key] === 'object' && obj[key] !== null) {
            deepFreeze(obj[key]);
        }
    });
    return Object.freeze(obj);
}

// Immutable update helper
function updatePath(obj, path, value) {
    const keys = path.split('.');
    if (keys.length === 1) {
        return { ...obj, [keys[0]]: value };
    }
    const [first, ...rest] = keys;
    return {
        ...obj,
        [first]: updatePath(obj[first] || {}, rest.join('.'), value)
    };
}

const updated2 = updatePath(user, 'address.city', 'SF');
```

---

## 🔝 Higher-Order Functions

Functions that take or return other functions.

```javascript
// Function as argument
function map(arr, fn) {
    const result = [];
    for (let i = 0; i < arr.length; i++) {
        result.push(fn(arr[i], i, arr));
    }
    return result;
}

// Function as return value
function multiplier(factor) {
    return function(number) {
        return number * factor;
    };
}

const double = multiplier(2);
const triple = multiplier(3);

// Common HOFs
const numbers = [1, 2, 3, 4, 5];

// map - transform each element
numbers.map(x => x * 2);           // [2, 4, 6, 8, 10]

// filter - keep elements that pass test
numbers.filter(x => x % 2 === 0);  // [2, 4]

// reduce - accumulate into single value
numbers.reduce((acc, x) => acc + x, 0);  // 15

// find - first matching element
numbers.find(x => x > 3);          // 4

// some - any element passes test
numbers.some(x => x > 4);          // true

// every - all elements pass test
numbers.every(x => x > 0);         // true

// Custom HOFs
const filter = (predicate) => (arr) =>
    arr.filter(predicate);

const isEven = x => x % 2 === 0;
const filterEven = filter(isEven);
filterEven([1, 2, 3, 4]); // [2, 4]

// Function enhancement
function withLogging(fn) {
    return function(...args) {
        console.log(`Calling ${fn.name} with:`, args);
        const result = fn(...args);
        console.log(`Result:`, result);
        return result;
    };
}

const add = (a, b) => a + b;
const loggedAdd = withLogging(add);
loggedAdd(2, 3); // Logs: Calling add with [2, 3], Result: 5

// Timing decorator
function withTiming(fn) {
    return function(...args) {
        const start = performance.now();
        const result = fn(...args);
        const end = performance.now();
        console.log(`${fn.name} took ${end - start}ms`);
        return result;
    };
}
```

---

## 🔄 Map, Filter, Reduce Mastery

### Map - Transform

```javascript
const users = [
    { name: 'John', age: 25 },
    { name: 'Jane', age: 30 },
    { name: 'Bob', age: 35 }
];

// Extract property
users.map(u => u.name);           // ['John', 'Jane', 'Bob']

// Transform objects
users.map(u => ({
    ...u,
    isAdult: u.age >= 18
}));

// Index access
['a', 'b', 'c'].map((char, i) => `${i}: ${char}`);
// ['0: a', '1: b', '2: c']

// flatMap - map then flatten one level
const sentences = ['Hello world', 'Foo bar'];
sentences.flatMap(s => s.split(' ')); // ['Hello', 'world', 'Foo', 'bar']
```

### Filter - Select

```javascript
// Simple predicate
numbers.filter(x => x > 3);         // [4, 5]

// Complex condition
users.filter(u => u.age >= 30 && u.name.startsWith('J'));

// Remove falsy
[0, 1, false, 2, '', 3, null].filter(Boolean); // [1, 2, 3]

// Unique values
const unique = arr => [...new Set(arr)];
// Or with filter:
const unique2 = arr => arr.filter((v, i, a) => a.indexOf(v) === i);

// Partition (split by condition)
const partition = (arr, predicate) => [
    arr.filter(predicate),
    arr.filter(x => !predicate(x))
];

const [evens, odds] = partition([1, 2, 3, 4], x => x % 2 === 0);
```

### Reduce - Accumulate

```javascript
// Sum
[1, 2, 3, 4].reduce((sum, n) => sum + n, 0); // 10

// Max
[1, 5, 3, 2].reduce((max, n) => n > max ? n : max, -Infinity); // 5

// Group by
const groupBy = (arr, keyFn) =>
    arr.reduce((groups, item) => {
        const key = keyFn(item);
        groups[key] = groups[key] || [];
        groups[key].push(item);
        return groups;
    }, {});

const byAge = groupBy(users, u => u.age >= 30 ? 'senior' : 'junior');

// Count occurrences
const countBy = arr =>
    arr.reduce((counts, item) => {
        counts[item] = (counts[item] || 0) + 1;
        return counts;
    }, {});

countBy(['a', 'b', 'a', 'c', 'a']); // { a: 3, b: 1, c: 1 }

// Object from entries
const pairs = [['a', 1], ['b', 2], ['c', 3]];
pairs.reduce((obj, [key, val]) => ({ ...obj, [key]: val }), {});
// { a: 1, b: 2, c: 3 }

// Flatten
const nested = [[1, 2], [3, 4], [5]];
nested.reduce((flat, arr) => [...flat, ...arr], []); // [1, 2, 3, 4, 5]
// Or: nested.flat(1)

// Pipeline (reduce over functions)
const pipe = (...fns) => x => fns.reduce((v, f) => f(v), x);

// Implement map with reduce
const mapWithReduce = (arr, fn) =>
    arr.reduce((result, item, i) => [...result, fn(item, i)], []);

// Implement filter with reduce
const filterWithReduce = (arr, fn) =>
    arr.reduce((result, item) => fn(item) ? [...result, item] : result, []);
```

---

## 🔗 Composition and Pipelines

```javascript
// Compose (right to left)
const compose = (...fns) => x =>
    fns.reduceRight((acc, fn) => fn(acc), x);

// Pipe (left to right)
const pipe = (...fns) => x =>
    fns.reduce((acc, fn) => fn(acc), x);

// Example pipeline
const processUser = pipe(
    user => ({ ...user, name: user.name.trim() }),
    user => ({ ...user, email: user.email.toLowerCase() }),
    user => ({ ...user, createdAt: new Date() })
);

const newUser = processUser({ name: '  John  ', email: 'JOHN@TEST.COM' });

// Point-free style
const prop = key => obj => obj[key];
const map = fn => arr => arr.map(fn);
const filter = fn => arr => arr.filter(fn);
const sort = fn => arr => [...arr].sort(fn);

const getActiveUserNames = pipe(
    filter(prop('active')),
    map(prop('name')),
    sort((a, b) => a.localeCompare(b))
);

const users2 = [
    { name: 'John', active: true },
    { name: 'Alice', active: true },
    { name: 'Bob', active: false }
];

getActiveUserNames(users2); // ['Alice', 'John']

// Async composition
const pipeAsync = (...fns) => x =>
    fns.reduce((promise, fn) => promise.then(fn), Promise.resolve(x));

const fetchUserData = pipeAsync(
    userId => fetch(`/api/users/${userId}`),
    response => response.json(),
    user => ({ ...user, fetchedAt: new Date() })
);
```

---

## 🛠️ Functional Utilities

```javascript
// Identity
const identity = x => x;

// Constant
const constant = x => () => x;

// Negate
const negate = fn => (...args) => !fn(...args);

// Once - call only once
const once = fn => {
    let called = false;
    let result;
    return (...args) => {
        if (!called) {
            called = true;
            result = fn(...args);
        }
        return result;
    };
};

// Flip - flip arguments
const flip = fn => (a, b) => fn(b, a);

// Tap - side effect without changing value
const tap = fn => x => {
    fn(x);
    return x;
};

const result = pipe(
    x => x + 1,
    tap(console.log),  // Logs intermediate value
    x => x * 2
)(5);

// Trace - debugging in pipelines
const trace = label => tap(x => console.log(label, x));

// Unary - force single argument
const unary = fn => arg => fn(arg);
['1', '2', '3'].map(unary(parseInt)); // [1, 2, 3] not [1, NaN, NaN]

// Binary
const binary = fn => (a, b) => fn(a, b);

// Complement
const complement = fn => (...args) => !fn(...args);

const isOdd = complement(isEven);

// Converge - apply multiple functions then combine
const converge = (combiner, fns) => (...args) =>
    combiner(...fns.map(fn => fn(...args)));

const average = converge(
    (sum, count) => sum / count,
    [arr => arr.reduce((a, b) => a + b, 0), arr => arr.length]
);

average([1, 2, 3, 4, 5]); // 3
```

---

## 🎯 Interview Problems

```javascript
// 1. Implement flatMap
Array.prototype.myFlatMap = function(fn) {
    return this.reduce((acc, item, i) => [...acc, ...fn(item, i, this)], []);
};

// 2. Implement groupBy
const groupBy = (arr, fn) =>
    arr.reduce((acc, item) => {
        const key = typeof fn === 'function' ? fn(item) : item[fn];
        (acc[key] = acc[key] || []).push(item);
        return acc;
    }, {});

// 3. Implement chunk
const chunk = (arr, size) =>
    arr.reduce((chunks, item, i) => {
        const chunkIndex = Math.floor(i / size);
        chunks[chunkIndex] = chunks[chunkIndex] || [];
        chunks[chunkIndex].push(item);
        return chunks;
    }, []);

// 4. Implement zip
const zip = (...arrays) =>
    arrays[0].map((_, i) => arrays.map(arr => arr[i]));

// 5. Implement difference
const difference = (a, b) => {
    const setB = new Set(b);
    return a.filter(x => !setB.has(x));
};

// 6. Implement intersection
const intersection = (a, b) => {
    const setB = new Set(b);
    return a.filter(x => setB.has(x));
};

// 7. Implement union
const union = (a, b) => [...new Set([...a, ...b])];
```

---

## ✅ Day 21 Checklist

- [ ] Understand pure functions
- [ ] Know side effects to avoid
- [ ] Practice immutable array operations
- [ ] Practice immutable object operations
- [ ] Master higher-order functions
- [ ] Use map, filter, reduce fluently
- [ ] Implement reduce-based utilities
- [ ] Apply function composition
- [ ] Write point-free style code
- [ ] Know common functional utilities
- [ ] Complete interview problems
