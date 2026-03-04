# Day 15: Currying, Partial Application & Composition

## 🎯 Learning Objectives
- Understand currying and its applications
- Master partial application
- Learn function composition
- Implement these patterns from scratch

---

## 🍛 Currying

Currying transforms a function with multiple arguments into a sequence of functions, each taking a single argument.

```javascript
// Non-curried
function add(a, b, c) {
    return a + b + c;
}
add(1, 2, 3); // 6

// Curried
function curriedAdd(a) {
    return function(b) {
        return function(c) {
            return a + b + c;
        };
    };
}
curriedAdd(1)(2)(3); // 6

// Arrow function syntax
const curriedAddArrow = a => b => c => a + b + c;
curriedAddArrow(1)(2)(3); // 6

// Partial application via currying
const add1 = curriedAdd(1);      // Remembers a=1
const add1and2 = add1(2);        // Remembers a=1, b=2
const result = add1and2(3);      // Returns 6

/*
VISUALIZATION:
             curriedAdd(1)
                   │
                   ▼
        ┌─────────────────────┐
        │  a = 1 (closed)     │
        │  return function(b) │
        └─────────────────────┘
                   │
                   ▼ (2)
        ┌─────────────────────┐
        │  a = 1, b = 2       │
        │  return function(c) │
        └─────────────────────┘
                   │
                   ▼ (3)
        ┌─────────────────────┐
        │  return 1 + 2 + 3   │
        │  = 6                │
        └─────────────────────┘
*/
```

### Generic Curry Function

```javascript
// Simple curry (fixed arity)
function curry(fn) {
    return function curried(...args) {
        if (args.length >= fn.length) {
            return fn.apply(this, args);
        } else {
            return function(...moreArgs) {
                return curried.apply(this, args.concat(moreArgs));
            };
        }
    };
}

// Usage
const sum = (a, b, c) => a + b + c;
const curriedSum = curry(sum);

curriedSum(1)(2)(3);      // 6
curriedSum(1, 2)(3);      // 6
curriedSum(1)(2, 3);      // 6
curriedSum(1, 2, 3);      // 6

// Advanced curry with placeholder support
const _ = Symbol('placeholder');

function curryWithPlaceholder(fn) {
    return function curried(...args) {
        // Check if all args are provided (no placeholders)
        const complete = args.length >= fn.length &&
            !args.slice(0, fn.length).includes(_);
        
        if (complete) {
            return fn.apply(this, args);
        }
        
        return function(...newArgs) {
            // Replace placeholders with new args
            const mergedArgs = args.map(arg => 
                arg === _ && newArgs.length ? newArgs.shift() : arg
            );
            return curried.apply(this, mergedArgs.concat(newArgs));
        };
    };
}

const greet = (greeting, name, punctuation) => 
    `${greeting}, ${name}${punctuation}`;

const curriedGreet = curryWithPlaceholder(greet);

// Skip arguments with placeholder
const greetWithName = curriedGreet(_, 'John', _);
greetWithName('Hello', '!'); // "Hello, John!"
```

### Practical Currying Examples

```javascript
// 1. Event handling
const handleEvent = eventType => element => callback => {
    element.addEventListener(eventType, callback);
    return () => element.removeEventListener(eventType, callback);
};

const onClick = handleEvent('click');
const onButtonClick = onClick(button);
const cleanup = onButtonClick(e => console.log('Clicked!'));

// 2. API requests
const request = method => url => data => {
    return fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
};

const post = request('POST');
const postToUsers = post('/api/users');
postToUsers({ name: 'John' });

// 3. Logging with levels
const log = level => timestamp => message => 
    console.log(`[${level}] ${timestamp}: ${message}`);

const error = log('ERROR');
const errorNow = error(new Date().toISOString());
errorNow('Something went wrong!');

// 4. Validation
const validate = predicate => errorMsg => value => 
    predicate(value) ? { valid: true, value } : { valid: false, error: errorMsg };

const isNonEmpty = validate(s => s.length > 0)('Field is required');
const isEmail = validate(s => s.includes('@'))('Invalid email');

isNonEmpty('test');    // { valid: true, value: 'test' }
isNonEmpty('');        // { valid: false, error: 'Field is required' }
```

---

## 🧩 Partial Application

Partial application fixes some arguments of a function, producing a function with fewer arguments.

```javascript
// Using bind
function multiply(a, b, c) {
    return a * b * c;
}

const multiplyBy2 = multiply.bind(null, 2);
multiplyBy2(3, 4); // 24 (2 * 3 * 4)

const multiplyBy2And3 = multiply.bind(null, 2, 3);
multiplyBy2And3(4); // 24

// Custom partial function
function partial(fn, ...presetArgs) {
    return function(...laterArgs) {
        return fn(...presetArgs, ...laterArgs);
    };
}

const double = partial(multiply, 2, 1);
double(5); // 10 (2 * 1 * 5)

// Partial with placeholder (apply from right)
function partialRight(fn, ...presetArgs) {
    return function(...laterArgs) {
        return fn(...laterArgs, ...presetArgs);
    };
}

const greet = (greeting, name) => `${greeting}, ${name}!`;
const greetJohn = partialRight(greet, 'John');
greetJohn('Hello'); // "Hello, John!"

// Real-world example: setTimeout
const delay = partial(setTimeout);
const delayOneSecond = partial(setTimeout, _, 1000);

// Using partial for map/filter/reduce
const map = (fn, array) => array.map(fn);
const filter = (fn, array) => array.filter(fn);

const double = x => x * 2;
const isEven = x => x % 2 === 0;

const doubleAll = partial(map, double);
const filterEven = partial(filter, isEven);

doubleAll([1, 2, 3]);    // [2, 4, 6]
filterEven([1, 2, 3, 4]); // [2, 4]
```

### Currying vs Partial Application

```javascript
/*
╔════════════════════════════════════════════════════════════════════╗
║             CURRYING vs PARTIAL APPLICATION                         ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  CURRYING:                                                          ║
║  - Transforms f(a, b, c) → f(a)(b)(c)                               ║
║  - Always produces unary functions                                  ║
║  - Automatically provides all intermediate functions                ║
║                                                                     ║
║  PARTIAL APPLICATION:                                               ║
║  - Fixes some arguments: f(a, b, c) → g(c) where a, b are fixed    ║
║  - Can fix any number of arguments                                  ║
║  - One-step transformation                                          ║
║                                                                     ║
╚════════════════════════════════════════════════════════════════════╝

f(a, b, c) = a + b + c

Currying:
curry(f)(1)       → f(b)(c) = 1 + b + c
curry(f)(1)(2)    → f(c) = 1 + 2 + c
curry(f)(1)(2)(3) → 6

Partial:
partial(f, 1)        → f(b, c) = 1 + b + c
partial(f, 1)(2, 3)  → 6
*/
```

---

## 🔗 Function Composition

Composition combines simple functions to build complex ones.

```javascript
// Basic composition: f(g(x))
const compose = (f, g) => x => f(g(x));

const addOne = x => x + 1;
const double = x => x * 2;

const addOneThenDouble = compose(double, addOne);
addOneThenDouble(5); // 12: double(addOne(5)) = double(6) = 12

// Multi-function compose (right to left)
const composeMulti = (...fns) => 
    fns.reduce((f, g) => (...args) => f(g(...args)));

// OR more readable:
const composeMulti2 = (...fns) => x => 
    fns.reduceRight((acc, fn) => fn(acc), x);

const addOne = x => x + 1;
const double = x => x * 2;
const square = x => x * x;

const composed = composeMulti(square, double, addOne);
composed(3); // 64: square(double(addOne(3))) = square(double(4)) = square(8) = 64

// Pipe (left to right) - more intuitive
const pipe = (...fns) => x => 
    fns.reduce((acc, fn) => fn(acc), x);

const piped = pipe(addOne, double, square);
piped(3); // 64: Same result, different order

// Async composition
const pipeAsync = (...fns) => x =>
    fns.reduce(async (acc, fn) => fn(await acc), x);

const fetchUser = async id => ({ id, name: 'John' });
const addPosts = async user => ({ ...user, posts: [] });
const addStats = async user => ({ ...user, stats: { views: 100 } });

const getUserWithEverything = pipeAsync(fetchUser, addPosts, addStats);
await getUserWithEverything(1);
// { id: 1, name: 'John', posts: [], stats: { views: 100 } }
```

### Practical Composition Examples

```javascript
// 1. Data transformation pipeline
const users = [
    { name: 'John', age: 25, active: true },
    { name: 'Jane', age: 30, active: false },
    { name: 'Bob', age: 35, active: true }
];

const getActiveUsers = users => users.filter(u => u.active);
const sortByAge = users => [...users].sort((a, b) => a.age - b.age);
const getNames = users => users.map(u => u.name);
const toUpperCase = arr => arr.map(s => s.toUpperCase());

const processUsers = pipe(
    getActiveUsers,
    sortByAge,
    getNames,
    toUpperCase
);

processUsers(users); // ['JOHN', 'BOB']

// 2. String processing
const trim = s => s.trim();
const toLowerCase = s => s.toLowerCase();
const replaceSpaces = s => s.replace(/\s+/g, '-');
const removeSpecial = s => s.replace(/[^a-z0-9-]/g, '');

const slugify = pipe(trim, toLowerCase, replaceSpaces, removeSpecial);

slugify('  Hello World! @#$  '); // "hello-world"

// 3. Validation composition
const required = value => 
    value ? { valid: true, value } : { valid: false, error: 'Required' };

const minLength = min => result =>
    result.valid && result.value.length < min
        ? { valid: false, error: `Min ${min} chars` }
        : result;

const maxLength = max => result =>
    result.valid && result.value.length > max
        ? { valid: false, error: `Max ${max} chars` }
        : result;

const validateUsername = pipe(
    required,
    minLength(3),
    maxLength(20)
);

validateUsername('Jo');     // { valid: false, error: 'Min 3 chars' }
validateUsername('John');   // { valid: true, value: 'John' }

// 4. Point-free style
const prop = key => obj => obj[key];
const map = fn => arr => arr.map(fn);
const filter = fn => arr => arr.filter(fn);

const getActiveEmails = pipe(
    filter(prop('active')),
    map(prop('email'))
);

const users2 = [
    { email: 'a@test.com', active: true },
    { email: 'b@test.com', active: false },
    { email: 'c@test.com', active: true }
];

getActiveEmails(users2); // ['a@test.com', 'c@test.com']
```

---

## 🔬 Interview Problems

```javascript
// Problem 1: Implement curry
function curry(fn) {
    return function curried(...args) {
        if (args.length >= fn.length) {
            return fn.apply(this, args);
        }
        return (...more) => curried(...args, ...more);
    };
}

// Problem 2: Implement compose
const compose = (...fns) => x => fns.reduceRight((v, f) => f(v), x);

// Problem 3: Implement pipe
const pipe = (...fns) => x => fns.reduce((v, f) => f(v), x);

// Problem 4: Create a memoized curry
function memoizedCurry(fn) {
    const cache = new Map();
    
    return function curried(...args) {
        const key = JSON.stringify(args);
        
        if (cache.has(key)) {
            return cache.get(key);
        }
        
        if (args.length >= fn.length) {
            const result = fn.apply(this, args);
            cache.set(key, result);
            return result;
        }
        
        return (...more) => curried(...args, ...more);
    };
}

// Problem 5: Infinite currying
// sum(1)(2)(3)() => 6
function sum(a) {
    return function(b) {
        if (b === undefined) return a;
        return sum(a + b);
    };
}

console.log(sum(1)(2)(3)(4)()); // 10

// Alternative with valueOf
function sum2(a) {
    function inner(b) {
        return sum2(a + b);
    }
    inner.valueOf = () => a;
    return inner;
}

console.log(+sum2(1)(2)(3)(4)); // 10 (using unary +)
```

---

## ✅ Day 15 Checklist

- [ ] Understand currying concept
- [ ] Implement generic curry function
- [ ] Know the difference between currying and partial application
- [ ] Implement partial and partialRight
- [ ] Understand function composition
- [ ] Implement compose and pipe
- [ ] Use composition for data pipelines
- [ ] Apply currying in real scenarios
- [ ] Complete interview problems
- [ ] Practice point-free style
