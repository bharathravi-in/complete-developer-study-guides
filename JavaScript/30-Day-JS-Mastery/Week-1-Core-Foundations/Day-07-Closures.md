# Day 7: Closures (VERY IMPORTANT)

## 🎯 Learning Objectives
- Understand Lexical Environment deeply
- Master Closure memory retention
- Create private variables with closures
- Avoid common mistakes in loops
- Implement practical closure patterns

---

## 📚 What is a Closure?

A **closure** is a function that has access to variables from its outer (enclosing) function's scope, even after the outer function has returned.

```javascript
function outer() {
    const message = "Hello from outer!";
    
    function inner() {
        console.log(message); // Has access to outer's variable
    }
    
    return inner;
}

const closureFn = outer();
closureFn(); // "Hello from outer!" - still has access!

/*
═══════════════════════════════════════════════════════════
WHY THIS WORKS:
═══════════════════════════════════════════════════════════

When outer() returns, normally its variables would be garbage collected.
But inner() maintains a REFERENCE to the outer scope (lexical environment).
This reference prevents garbage collection of `message`.

Visual:
┌─────────────────────────────────────────────────────────┐
│ closureFn (inner function)                               │
│    │                                                     │
│    └───► [[Environment]] ───► outer's Lexical Environment│
│                                    │                     │
│                                    └──► message: "Hello" │
└─────────────────────────────────────────────────────────┘
*/
```

---

## 🌳 Lexical Environment

Every function has a hidden `[[Environment]]` property that references the Lexical Environment where it was created.

```javascript
/*
═══════════════════════════════════════════════════════════
LEXICAL ENVIRONMENT STRUCTURE:
═══════════════════════════════════════════════════════════

Lexical Environment = {
    Environment Record: {
        // Variables and functions declared in this scope
    },
    Outer Reference: // Reference to parent lexical environment
}
*/

const globalVar = "global";

function outer() {
    const outerVar = "outer";
    
    function middle() {
        const middleVar = "middle";
        
        function inner() {
            const innerVar = "inner";
            console.log(globalVar, outerVar, middleVar, innerVar);
        }
        
        return inner;
    }
    
    return middle;
}

const middleFn = outer();
const innerFn = middleFn();
innerFn(); // "global outer middle inner"

/*
Lexical Environment Chain:

inner's LE:
├── innerVar: "inner"
└── outer → middle's LE:
            ├── middleVar: "middle"
            └── outer → outer's LE:
                        ├── outerVar: "outer"
                        └── outer → Global LE:
                                    ├── globalVar: "global"
                                    └── outer → null
*/
```

### Variable Resolution

```javascript
function createAdder(x) {
    // Lexical Environment created with x
    return function(y) {
        return x + y; // x looked up in parent LE
    };
}

const add5 = createAdder(5);  // x = 5 in closure
const add10 = createAdder(10); // x = 10 in different closure

console.log(add5(3));  // 8 (5 + 3)
console.log(add10(3)); // 13 (10 + 3)

// Each call to createAdder creates a NEW lexical environment
// with its own copy of x
```

---

## 💾 Closure Memory Retention

Closures keep variables alive as long as they're referenced.

```javascript
// Memory retention example
function createHugeArray() {
    const hugeData = new Array(1000000).fill("data");
    
    return function() {
        return hugeData.length; // Closure over hugeData
    };
}

const getLength = createHugeArray();
// hugeData is NOT garbage collected because getLength references it

// Memory-efficient version
function createHugeArrayEfficient() {
    const hugeData = new Array(1000000).fill("data");
    const length = hugeData.length; // Extract what we need
    
    return function() {
        return length; // Only closure over length, not entire array
    };
}
// hugeData CAN be garbage collected now

// Releasing closure references
let closure = function() {
    const data = { heavy: "object" };
    return function() {
        return data;
    };
}();

console.log(closure()); // { heavy: "object" }
closure = null; // Now data can be garbage collected
```

---

## 🔒 Private Variables with Closures

```javascript
// Module Pattern - Private state
const counter = (function() {
    let count = 0; // Private variable
    
    return {
        increment() {
            count++;
            return count;
        },
        decrement() {
            count--;
            return count;
        },
        getCount() {
            return count;
        }
    };
})();

console.log(counter.getCount()); // 0
counter.increment();
counter.increment();
console.log(counter.getCount()); // 2
console.log(counter.count);      // undefined (private!)

// Factory function with private state
function createBankAccount(initialBalance) {
    let balance = initialBalance; // Private
    const transactionHistory = []; // Private
    
    function logTransaction(type, amount) {
        transactionHistory.push({
            type,
            amount,
            balance,
            timestamp: new Date()
        });
    }
    
    return {
        deposit(amount) {
            if (amount > 0) {
                balance += amount;
                logTransaction("deposit", amount);
                return balance;
            }
        },
        withdraw(amount) {
            if (amount > 0 && amount <= balance) {
                balance -= amount;
                logTransaction("withdrawal", amount);
                return balance;
            }
            return "Insufficient funds";
        },
        getBalance() {
            return balance;
        },
        getHistory() {
            return [...transactionHistory]; // Return copy
        }
    };
}

const account = createBankAccount(100);
account.deposit(50);    // 150
account.withdraw(30);   // 120
console.log(account.getBalance()); // 120
console.log(account.balance);      // undefined (private!)

// Private methods
function createPerson(name) {
    // Private method
    function validateName(n) {
        return typeof n === "string" && n.length > 0;
    }
    
    return {
        getName() {
            return name;
        },
        setName(newName) {
            if (validateName(newName)) {
                name = newName;
                return true;
            }
            return false;
        }
    };
}
```

---

## ⚠️ Common Mistakes in Loops

### The Classic Loop Problem

```javascript
// PROBLEM: var is function-scoped, shared across iterations
for (var i = 0; i < 3; i++) {
    setTimeout(function() {
        console.log(i);
    }, 100);
}
// Output: 3, 3, 3 (not 0, 1, 2!)

/*
═══════════════════════════════════════════════════════════
WHY THIS HAPPENS:
═══════════════════════════════════════════════════════════

1. Loop runs: i = 0, 1, 2, then 3 (exit condition)
2. setTimeout callbacks are queued
3. After 100ms, all callbacks execute
4. All callbacks reference the SAME i variable
5. i is now 3 (loop has finished)

Timeline:
t=0ms:    i=0, queue setTimeout
t=0ms:    i=1, queue setTimeout
t=0ms:    i=2, queue setTimeout
t=0ms:    i=3, loop exits
t=100ms:  All callbacks run, i=3
*/
```

### Solutions

```javascript
// Solution 1: Use let (block scope)
for (let i = 0; i < 3; i++) {
    setTimeout(function() {
        console.log(i);
    }, 100);
}
// Output: 0, 1, 2
// Each iteration creates a NEW i in its own block scope

// Solution 2: IIFE (before ES6)
for (var i = 0; i < 3; i++) {
    (function(j) {
        setTimeout(function() {
            console.log(j);
        }, 100);
    })(i);
}
// Output: 0, 1, 2
// Each IIFE creates a new scope with its own j

// Solution 3: Create a closure explicitly
function createLogger(i) {
    return function() {
        console.log(i);
    };
}

for (var i = 0; i < 3; i++) {
    setTimeout(createLogger(i), 100);
}
// Output: 0, 1, 2

// Solution 4: Use bind
for (var i = 0; i < 3; i++) {
    setTimeout(function(j) {
        console.log(j);
    }.bind(null, i), 100);
}
// Output: 0, 1, 2

// Solution 5: Third parameter of setTimeout
for (var i = 0; i < 3; i++) {
    setTimeout(function(j) {
        console.log(j);
    }, 100, i);
}
// Output: 0, 1, 2
```

### Other Loop Mistakes

```javascript
// Problem: Adding event listeners in loop
const buttons = document.querySelectorAll("button");

// WRONG
for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", function() {
        console.log("Button " + i + " clicked"); // Always last i
    });
}

// RIGHT
for (let i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", function() {
        console.log("Button " + i + " clicked"); // Correct i
    });
}

// Or using forEach (preferred)
buttons.forEach((button, index) => {
    button.addEventListener("click", () => {
        console.log("Button " + index + " clicked");
    });
});
```

---

## 🛠️ Practical Closure Patterns

### 1. Memoization

```javascript
function memoize(fn) {
    const cache = new Map();
    
    return function(...args) {
        const key = JSON.stringify(args);
        
        if (cache.has(key)) {
            console.log("Cache hit!");
            return cache.get(key);
        }
        
        console.log("Computing...");
        const result = fn.apply(this, args);
        cache.set(key, result);
        return result;
    };
}

// Usage
const expensiveOperation = memoize((a, b) => {
    // Simulate expensive computation
    return a + b;
});

console.log(expensiveOperation(1, 2)); // Computing... 3
console.log(expensiveOperation(1, 2)); // Cache hit! 3
console.log(expensiveOperation(2, 3)); // Computing... 5
```

### 2. Currying

```javascript
function curry(fn) {
    return function curried(...args) {
        if (args.length >= fn.length) {
            return fn.apply(this, args);
        }
        return function(...moreArgs) {
            return curried.apply(this, [...args, ...moreArgs]);
        };
    };
}

// Usage
const add = (a, b, c) => a + b + c;
const curriedAdd = curry(add);

console.log(curriedAdd(1)(2)(3));    // 6
console.log(curriedAdd(1, 2)(3));    // 6
console.log(curriedAdd(1)(2, 3));    // 6
console.log(curriedAdd(1, 2, 3));    // 6
```

### 3. Once Function

```javascript
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
    return "Initialized!";
});

console.log(initialize()); // Initializing... Initialized!
console.log(initialize()); // Initialized! (no log, cached result)
```

### 4. Debounce

```javascript
function debounce(fn, delay) {
    let timeoutId;
    
    return function(...args) {
        clearTimeout(timeoutId);
        
        timeoutId = setTimeout(() => {
            fn.apply(this, args);
        }, delay);
    };
}

// Usage
const searchInput = debounce((query) => {
    console.log("Searching for:", query);
}, 300);

// Rapidly calling...
searchInput("h");
searchInput("he");
searchInput("hel");
searchInput("hell");
searchInput("hello");
// Only "Searching for: hello" is logged (after 300ms)
```

### 5. Throttle

```javascript
function throttle(fn, limit) {
    let inThrottle = false;
    
    return function(...args) {
        if (!inThrottle) {
            fn.apply(this, args);
            inThrottle = true;
            
            setTimeout(() => {
                inThrottle = false;
            }, limit);
        }
    };
}

// Usage
const handleScroll = throttle(() => {
    console.log("Scroll event at:", Date.now());
}, 1000);

// Even if scroll fires 100 times per second,
// this only runs once per second
```

### 6. Private State Iterator

```javascript
function createIterator(array) {
    let index = 0;
    
    return {
        next() {
            if (index < array.length) {
                return { value: array[index++], done: false };
            }
            return { value: undefined, done: true };
        },
        hasNext() {
            return index < array.length;
        },
        reset() {
            index = 0;
        }
    };
}

const iterator = createIterator([1, 2, 3]);
console.log(iterator.next()); // { value: 1, done: false }
console.log(iterator.next()); // { value: 2, done: false }
console.log(iterator.hasNext()); // true
console.log(iterator.next()); // { value: 3, done: false }
console.log(iterator.next()); // { value: undefined, done: true }
```

---

## 📝 Task: Create Counter Using Closure

```javascript
// Basic counter
function createCounter(initial = 0) {
    let count = initial;
    
    return {
        increment() { return ++count; },
        decrement() { return --count; },
        getValue() { return count; },
        reset() { count = initial; return count; }
    };
}

const counter = createCounter(10);
console.log(counter.increment()); // 11
console.log(counter.increment()); // 12
console.log(counter.decrement()); // 11
console.log(counter.getValue());  // 11
console.log(counter.reset());     // 10

// Advanced counter with history
function createAdvancedCounter(initial = 0) {
    let count = initial;
    const history = [initial];
    const maxHistory = 10;
    
    function addToHistory(value) {
        history.push(value);
        if (history.length > maxHistory) {
            history.shift();
        }
    }
    
    return {
        increment(step = 1) {
            count += step;
            addToHistory(count);
            return count;
        },
        decrement(step = 1) {
            count -= step;
            addToHistory(count);
            return count;
        },
        getValue() {
            return count;
        },
        getHistory() {
            return [...history];
        },
        undo() {
            if (history.length > 1) {
                history.pop();
                count = history[history.length - 1];
            }
            return count;
        }
    };
}
```

---

## 🎤 Explain Closure in Interview Style

**Question**: "Can you explain what a closure is and give an example?"

**Answer**:
> "A closure is a function that remembers and can access variables from its outer scope even after the outer function has finished executing.

> In JavaScript, when a function is created, it maintains a reference to its lexical environment—the scope where it was defined. This reference persists even after the outer function returns.

> Here's a simple example:

```javascript
function createGreeter(greeting) {
    return function(name) {
        return `${greeting}, ${name}!`;
    };
}

const sayHello = createGreeter("Hello");
console.log(sayHello("John")); // "Hello, John!"
```

> Even though `createGreeter` has finished executing, the inner function still has access to `greeting` because of the closure.

> Closures are useful for data privacy, function factories, and maintaining state. For example, the Module Pattern uses closures to create private variables:

```javascript
const counter = (function() {
    let count = 0;
    return {
        increment() { return ++count; },
        getCount() { return count; }
    };
})();
```

> Here, `count` is truly private—you can only access it through the returned methods."

---

## ❓ Interview Questions

### Q1: What is a closure?
A closure is a function bundled with its lexical environment, giving it access to variables from its outer scope even after the outer function has returned.

### Q2: What are practical uses of closures?
- Data privacy (Module Pattern)
- Function factories
- Partial application / Currying
- Memoization
- Event handlers with state
- Implementing iterators

### Q3: What's the output?

```javascript
function outer() {
    var x = 10;
    
    function inner() {
        console.log(x);
    }
    
    x = 20;
    return inner;
}

outer()(); // ?
// Answer: 20 (closure references the variable, not its value)
```

### Q4: Closures and memory leaks?
Closures can cause memory leaks if they unintentionally hold references to large objects. To avoid:
- Set references to null when done
- Be mindful of what's in the closure's scope
- Remove event listeners properly

---

## 🔬 Practice Problems

```javascript
// Problem 1: What's the output?
for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 0);
}
// Answer: 3, 3, 3

// Problem 2: What's the output?
const functions = [];
for (var i = 0; i < 3; i++) {
    functions.push(() => i);
}
console.log(functions.map(fn => fn()));
// Answer: [3, 3, 3]

// Problem 3: Fix Problem 2 using closure
const functions2 = [];
for (var i = 0; i < 3; i++) {
    functions2.push(((j) => () => j)(i));
}
console.log(functions2.map(fn => fn()));
// Answer: [0, 1, 2]

// Problem 4: Create a private variable counter
function createSecureCounter() {
    let count = 0;
    const password = "secret";
    
    return {
        increment(pwd) {
            if (pwd === password) {
                return ++count;
            }
            throw new Error("Unauthorized");
        },
        getCount(pwd) {
            if (pwd === password) {
                return count;
            }
            throw new Error("Unauthorized");
        }
    };
}

// Problem 5: Implement once with closure
function once(fn) {
    let executed = false;
    let result;
    
    return function(...args) {
        if (!executed) {
            executed = true;
            result = fn.apply(this, args);
        }
        return result;
    };
}

// Problem 6: What does this log?
let count = 0;
(function() {
    if (!count) {
        let count = 1;
        console.log(count);
    }
    console.log(count);
})();
// Answer: 1, 0 (let creates new count in block scope)
```

---

## ✅ Day 7 Checklist

- [ ] Understand what a closure is
- [ ] Master lexical environment concept
- [ ] Know how closure retains memory
- [ ] Create private variables with closures
- [ ] Understand and fix loop closure problems
- [ ] Implement memoization using closures
- [ ] Implement currying using closures
- [ ] Create a counter using closure
- [ ] Explain closures clearly for interviews
- [ ] Complete all practice problems
- [ ] Understand closure memory implications
