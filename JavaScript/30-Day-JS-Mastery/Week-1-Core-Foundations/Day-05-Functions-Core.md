# Day 5: Functions (Core)

## 🎯 Learning Objectives
- Master Function Declaration vs Expression
- Deep understanding of Arrow Functions
- Learn IIFE patterns
- Understand arguments object
- Master Rest & Spread operators
- Learn Default Parameters
- Understand First-class and Higher-order Functions

---

## 📚 Function Declaration vs Expression

### Function Declaration
- **Hoisted** completely (can call before definition)
- Creates a named function

```javascript
// Function Declaration
sayHello(); // Works! (hoisted)

function sayHello() {
    console.log("Hello!");
}

// Characteristics:
// 1. Hoisted to top of scope
// 2. Has a name property
// 3. Creates a function in current scope
console.log(sayHello.name); // "sayHello"
```

### Function Expression
- **NOT hoisted** (only variable declaration is hoisted)
- Can be named or anonymous

```javascript
// Anonymous Function Expression
// sayBye(); // TypeError: sayBye is not a function

var sayBye = function() {
    console.log("Bye!");
};

sayBye(); // Works after definition

// Named Function Expression
var factorial = function fact(n) {
    if (n <= 1) return 1;
    return n * fact(n - 1); // Can use 'fact' inside
};

console.log(factorial(5)); // 120
// console.log(fact(5)); // ReferenceError (fact not in scope)
console.log(factorial.name); // "fact"

// let/const Function Expression
const greet = function(name) {
    return `Hello, ${name}!`;
};
```

### Key Differences

```javascript
/*
═══════════════════════════════════════════════════════════
FUNCTION DECLARATION vs FUNCTION EXPRESSION
═══════════════════════════════════════════════════════════

Aspect              │ Declaration         │ Expression
─────────────────────────────────────────────────────────────
Hoisting            │ Fully hoisted       │ Variable hoisted only
Call before define  │ ✅ Yes              │ ❌ No
Named/Anonymous     │ Always named        │ Can be either
Use in conditionals │ Behavior varies     │ Reliable
As callback         │ Both work           │ More common
*/

// Conditional function (unreliable with declaration)
if (true) {
    function test() { return "if"; }
} else {
    function test() { return "else"; }
}
// Result varies by JavaScript engine!

// Conditional function (reliable with expression)
let test;
if (true) {
    test = function() { return "if"; };
} else {
    test = function() { return "else"; };
}
console.log(test()); // "if" (reliable)
```

---

## ➡️ Arrow Functions

Arrow functions have shorter syntax and lexical `this` binding.

```javascript
// Basic Syntax
const add = (a, b) => a + b;

// With single parameter (parens optional)
const double = x => x * 2;

// With no parameters
const greet = () => "Hello!";

// With multiple statements (need braces and return)
const multiply = (a, b) => {
    const result = a * b;
    return result;
};

// Returning objects (wrap in parentheses)
const createUser = (name, age) => ({ name, age });
console.log(createUser("John", 30)); // { name: "John", age: 30 }

// Arrow functions in array methods
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
const evens = numbers.filter(n => n % 2 === 0);
const sum = numbers.reduce((acc, n) => acc + n, 0);
```

### Arrow Functions vs Regular Functions

```javascript
// 1. No `this` binding (lexical this)
const obj = {
    name: "Object",
    regularMethod: function() {
        console.log(this.name); // "Object"
        
        setTimeout(function() {
            console.log(this.name); // undefined (lost this)
        }, 100);
        
        setTimeout(() => {
            console.log(this.name); // "Object" (lexical this)
        }, 100);
    },
    arrowMethod: () => {
        console.log(this.name); // undefined (inherits from parent scope)
    }
};

// 2. No `arguments` object
function regular() {
    console.log(arguments); // [Arguments] { '0': 1, '1': 2 }
}
regular(1, 2);

const arrow = () => {
    // console.log(arguments); // ReferenceError!
};

// Use rest parameters instead
const arrowWithArgs = (...args) => {
    console.log(args); // [1, 2]
};
arrowWithArgs(1, 2);

// 3. Cannot be used as constructors
function Person(name) {
    this.name = name;
}
const person = new Person("John"); // OK

const PersonArrow = (name) => {
    this.name = name;
};
// const person2 = new PersonArrow("Jane"); // TypeError!

// 4. No prototype property
console.log(Person.prototype);      // Person {}
console.log(PersonArrow.prototype); // undefined

// 5. Cannot use yield (not generators)
function* generator() {
    yield 1;
}
// const genArrow = *() => { yield 1; }; // SyntaxError!

/*
═══════════════════════════════════════════════════════════
WHEN TO USE ARROW FUNCTIONS:
═══════════════════════════════════════════════════════════

✅ Use Arrow Functions:
- Callbacks in array methods (map, filter, reduce)
- Short functions
- When you need lexical `this`
- Promise chains
- Event handlers needing parent `this`

❌ Avoid Arrow Functions:
- Object methods (need `this`)
- Constructors
- Event handlers needing event target `this`
- Functions using arguments object
- Functions needing dynamic `this`
*/
```

---

## 🔁 IIFE (Immediately Invoked Function Expression)

```javascript
// Classic IIFE syntax
(function() {
    console.log("I run immediately!");
})();

// With parameters
(function(name) {
    console.log(`Hello, ${name}!`);
})("World");

// Arrow IIFE
(() => {
    console.log("Arrow IIFE!");
})();

// Named IIFE (for debugging)
(function myIIFE() {
    console.log("Named IIFE");
})();

// Async IIFE
(async function() {
    const data = await fetchSomething();
    console.log(data);
})();

// Async Arrow IIFE
(async () => {
    const data = await fetchSomething();
    console.log(data);
})();

// IIFE Use Cases:

// 1. Module Pattern (ES5 era)
const counter = (function() {
    let count = 0; // Private variable
    
    return {
        increment: function() { return ++count; },
        decrement: function() { return --count; },
        getCount: function() { return count; }
    };
})();

console.log(counter.getCount()); // 0
counter.increment();
console.log(counter.getCount()); // 1

// 2. Avoid global pollution
(function() {
    var privateVar = "I'm not global!";
    // ... code
})();
// console.log(privateVar); // ReferenceError

// 3. Fix loop variable (before let)
for (var i = 0; i < 3; i++) {
    (function(j) {
        setTimeout(() => console.log(j), 100);
    })(i);
}
// Output: 0, 1, 2 (not 3, 3, 3)

// 4. Initialization code
const config = (function() {
    const env = process.env.NODE_ENV || 'development';
    const baseUrl = env === 'production' 
        ? 'https://api.example.com' 
        : 'http://localhost:3000';
    
    return Object.freeze({ env, baseUrl });
})();
```

---

## 📝 Arguments Object

```javascript
// arguments is an array-like object
function showArgs() {
    console.log(arguments);        // [Arguments] { '0': 1, '1': 2, '2': 3 }
    console.log(arguments.length); // 3
    console.log(arguments[0]);     // 1
    
    // arguments is NOT a real array
    // arguments.map(x => x); // TypeError!
    
    // Convert to array
    const argsArray = Array.from(arguments);
    const argsArray2 = [...arguments];
    const argsArray3 = Array.prototype.slice.call(arguments);
    
    console.log(argsArray.map(x => x * 2)); // [2, 4, 6]
}

showArgs(1, 2, 3);

// arguments.callee (deprecated, avoid!)
function factorial(n) {
    if (n <= 1) return 1;
    // return n * arguments.callee(n - 1); // Works but deprecated
    return n * factorial(n - 1); // Use function name instead
}

// arguments in strict mode
function strictArgs(a, b) {
    "use strict";
    arguments[0] = 100;
    console.log(a); // Still original value (in strict mode)
}

function nonStrictArgs(a, b) {
    arguments[0] = 100;
    console.log(a); // 100 (modified!)
}

// Arrow functions don't have arguments
const arrow = () => {
    // console.log(arguments); // ReferenceError
};

// But can access parent's arguments
function outer() {
    const inner = () => {
        console.log(arguments); // outer's arguments
    };
    inner();
}
outer(1, 2, 3); // [Arguments] { '0': 1, '1': 2, '2': 3 }
```

---

## 🔄 Rest & Spread Operators

### Rest Parameters (...args)
Collects remaining arguments into an array.

```javascript
// Rest: Collects arguments into array
function sum(...numbers) {
    return numbers.reduce((total, n) => total + n, 0);
}

console.log(sum(1, 2, 3, 4, 5)); // 15

// Rest must be last parameter
function greet(greeting, ...names) {
    return names.map(name => `${greeting}, ${name}!`);
}

console.log(greet("Hello", "John", "Jane")); // ["Hello, John!", "Hello, Jane!"]

// Rest vs arguments
function compare(...args) {
    console.log(args);            // Real array
    console.log(Array.isArray(args)); // true
    console.log(arguments);       // Array-like object
}

// Destructuring with rest
const [first, second, ...rest] = [1, 2, 3, 4, 5];
console.log(first);  // 1
console.log(second); // 2
console.log(rest);   // [3, 4, 5]

const { name, ...otherProps } = { name: "John", age: 30, city: "NYC" };
console.log(name);       // "John"
console.log(otherProps); // { age: 30, city: "NYC" }
```

### Spread Operator (...)
Expands an iterable into individual elements.

```javascript
// Spread in function calls
const numbers = [1, 2, 3];
console.log(Math.max(...numbers)); // 3

// Spread in array literals
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];
const combined = [...arr1, ...arr2]; // [1, 2, 3, 4, 5, 6]

// Copy array (shallow)
const original = [1, 2, { a: 3 }];
const copy = [...original];
copy[0] = 100;
console.log(original[0]); // 1 (unchanged)
copy[2].a = 300;
console.log(original[2].a); // 300 (shallow copy issue!)

// Spread in object literals
const user = { name: "John", age: 30 };
const userWithRole = { ...user, role: "admin" };
console.log(userWithRole); // { name: "John", age: 30, role: "admin" }

// Merging objects (later properties override)
const defaults = { theme: "light", lang: "en" };
const userPrefs = { theme: "dark" };
const settings = { ...defaults, ...userPrefs };
console.log(settings); // { theme: "dark", lang: "en" }

// Spread with strings
const chars = [..."Hello"];
console.log(chars); // ["H", "e", "l", "l", "o"]

// Spread to convert iterables
const set = new Set([1, 2, 3]);
const arrFromSet = [...set];
console.log(arrFromSet); // [1, 2, 3]
```

---

## 📐 Default Parameters

```javascript
// Default parameter values
function greet(name = "Guest", greeting = "Hello") {
    return `${greeting}, ${name}!`;
}

console.log(greet());              // "Hello, Guest!"
console.log(greet("John"));        // "Hello, John!"
console.log(greet("Jane", "Hi"));  // "Hi, Jane!"

// undefined triggers default, null doesn't
console.log(greet(undefined, "Hey")); // "Hey, Guest!"
console.log(greet(null, "Hey"));      // "Hey, null!"

// Using expressions as defaults
function getDefaultName() {
    return "Anonymous";
}

function greet2(name = getDefaultName()) {
    return `Hello, ${name}!`;
}

// Using previous parameters
function createUser(name, role = "user", greeting = `Welcome, ${name}!`) {
    return { name, role, greeting };
}

console.log(createUser("John")); 
// { name: "John", role: "user", greeting: "Welcome, John!" }

// Default with destructuring
function processUser({ name = "Guest", age = 0 } = {}) {
    console.log(name, age);
}

processUser({ name: "John" });  // "John" 0
processUser({});                // "Guest" 0
processUser();                  // "Guest" 0 (default object)

// Required parameters pattern
const required = () => { throw new Error("Parameter required!"); };

function myFunc(a = required(), b = required()) {
    return a + b;
}

// myFunc(); // Error: Parameter required!
console.log(myFunc(1, 2)); // 3
```

---

## 🌟 First-Class Functions

Functions in JavaScript are "first-class citizens" - they can be:

```javascript
// 1. Assigned to variables
const sayHello = function() {
    return "Hello!";
};

// 2. Stored in data structures
const functions = [
    function() { return 1; },
    function() { return 2; },
    function() { return 3; }
];
console.log(functions[0]()); // 1

// 3. Passed as arguments
function callTwice(fn) {
    fn();
    fn();
}
callTwice(() => console.log("Called!"));

// 4. Returned from other functions
function createMultiplier(factor) {
    return function(number) {
        return number * factor;
    };
}
const double = createMultiplier(2);
console.log(double(5)); // 10

// 5. Have properties
function myFunc() {}
myFunc.version = "1.0.0";
console.log(myFunc.version); // "1.0.0"

// 6. Compared with ===
const fn1 = () => {};
const fn2 = fn1;
const fn3 = () => {};

console.log(fn1 === fn2); // true (same reference)
console.log(fn1 === fn3); // false (different functions)
```

---

## 🔺 Higher-Order Functions

Functions that take functions as arguments or return functions.

```javascript
// 1. Functions taking function arguments
const numbers = [1, 2, 3, 4, 5];

// map - transform each element
const doubled = numbers.map(n => n * 2);
console.log(doubled); // [2, 4, 6, 8, 10]

// filter - keep elements matching predicate
const evens = numbers.filter(n => n % 2 === 0);
console.log(evens); // [2, 4]

// reduce - accumulate to single value
const sum = numbers.reduce((acc, n) => acc + n, 0);
console.log(sum); // 15

// 2. Functions returning functions
function withLogging(fn) {
    return function(...args) {
        console.log(`Calling with args: ${args}`);
        const result = fn(...args);
        console.log(`Result: ${result}`);
        return result;
    };
}

const add = (a, b) => a + b;
const loggedAdd = withLogging(add);
loggedAdd(2, 3);
// "Calling with args: 2,3"
// "Result: 5"

// 3. Creating specialized functions
function createValidator(validatorFn, errorMessage) {
    return function(value) {
        if (!validatorFn(value)) {
            throw new Error(errorMessage);
        }
        return value;
    };
}

const validateEmail = createValidator(
    email => /\S+@\S+\.\S+/.test(email),
    "Invalid email format"
);

console.log(validateEmail("test@example.com")); // "test@example.com"
// validateEmail("invalid"); // Error: Invalid email format

// 4. Function composition
const compose = (...fns) => (value) => 
    fns.reduceRight((acc, fn) => fn(acc), value);

const addOne = x => x + 1;
const double = x => x * 2;
const square = x => x * x;

const composed = compose(square, double, addOne);
console.log(composed(2)); // 36 = square(double(addOne(2))) = square(double(3)) = square(6) = 36

// 5. Partial application
function partial(fn, ...fixedArgs) {
    return function(...remainingArgs) {
        return fn(...fixedArgs, ...remainingArgs);
    };
}

const multiply = (a, b, c) => a * b * c;
const multiplyBy2 = partial(multiply, 2);
console.log(multiplyBy2(3, 4)); // 24
```

---

## 🔬 Practice Problems

```javascript
// Problem 1: Implement a function that memoizes another function
function memoize(fn) {
    const cache = new Map();
    return function(...args) {
        const key = JSON.stringify(args);
        if (cache.has(key)) {
            console.log("From cache");
            return cache.get(key);
        }
        const result = fn.apply(this, args);
        cache.set(key, result);
        return result;
    };
}

const slowAdd = (a, b) => {
    // Simulate slow operation
    return a + b;
};

const fastAdd = memoize(slowAdd);
console.log(fastAdd(1, 2)); // Calculated: 3
console.log(fastAdd(1, 2)); // From cache: 3

// Problem 2: Implement once() - function that runs only once
function once(fn) {
    let called = false;
    let result;
    return function(...args) {
        if (!called) {
            called = true;
            result = fn.apply(this, args);
        }
        return result;
    };
}

const initialize = once(() => {
    console.log("Initializing...");
    return "initialized";
});

console.log(initialize()); // "Initializing..." "initialized"
console.log(initialize()); // "initialized" (no log)

// Problem 3: Implement pipe (left-to-right composition)
const pipe = (...fns) => (value) =>
    fns.reduce((acc, fn) => fn(acc), value);

const piped = pipe(addOne, double, square);
console.log(piped(2)); // 36 = square(double(addOne(2)))

// Problem 4: What's the output?
function outer() {
    console.log(this); // ?
    const inner = () => {
        console.log(this); // ?
    };
    inner();
}

outer();      // window/global (non-strict) or undefined (strict), then same
outer.call({ name: "custom" }); // { name: "custom" }, { name: "custom" }

// Problem 5: Fix this code
const calculator = {
    value: 0,
    add: function(n) {
        this.value += n;
        return this;
    },
    multiply: function(n) {
        this.value *= n;
        return this;
    },
    getValue: function() {
        return this.value;
    }
};

// Method chaining
console.log(calculator.add(5).multiply(2).getValue()); // 10
```

---

## ✅ Day 5 Checklist

- [ ] Understand function declaration vs expression differences
- [ ] Know when to use arrow functions
- [ ] Understand lexical `this` in arrow functions
- [ ] Master IIFE patterns and use cases
- [ ] Understand arguments object limitations
- [ ] Use rest parameters effectively
- [ ] Use spread operator for arrays and objects
- [ ] Implement default parameters
- [ ] Understand first-class functions concept
- [ ] Create and use higher-order functions
- [ ] Implement function composition
- [ ] Complete all practice problems
