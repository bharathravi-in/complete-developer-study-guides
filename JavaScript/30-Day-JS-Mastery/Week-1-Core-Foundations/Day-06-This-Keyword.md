# Day 6: `this` Keyword (Most Asked Topic)

## 🎯 Learning Objectives
- Master `this` in all contexts
- Understand call(), apply(), bind()
- Differentiate arrow vs regular function `this`
- Implement your own bind()

---

## 📚 Understanding `this`

`this` is a keyword that refers to the current execution context. Its value depends on **HOW** a function is called, not where it's defined.

```
╔═══════════════════════════════════════════════════════════════════╗
║                    `this` BINDING RULES                            ║
╠═══════════════════════════════════════════════════════════════════╣
║  Priority (highest to lowest):                                     ║
║                                                                    ║
║  1. new Binding      →  this = newly created object               ║
║  2. Explicit Binding →  this = specified object (call/apply/bind) ║
║  3. Implicit Binding →  this = object before the dot              ║
║  4. Default Binding  →  this = global/undefined (strict mode)     ║
║                                                                    ║
║  Special: Arrow functions → this = lexical (inherited from parent)║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 🌍 `this` in Global Scope

```javascript
// In Browser (non-strict mode)
console.log(this);              // Window object
console.log(this === window);   // true

// In Browser (strict mode)
"use strict";
console.log(this);              // Window (at global level, still Window)

// In Node.js (module scope)
console.log(this);              // {} (empty object - module exports)
console.log(this === module.exports); // true

// In Node.js (global scope - not in module)
console.log(globalThis);        // global object

// globalThis (ES2020) - universal way
console.log(globalThis);        // Window (browser) or global (Node.js)
```

---

## 📦 `this` in Functions

### Default Binding (Standalone Function Call)

```javascript
// Non-strict mode
function showThis() {
    console.log(this);
}
showThis(); // Window (browser) or global (Node.js)

// Strict mode
"use strict";
function showThisStrict() {
    console.log(this);
}
showThisStrict(); // undefined

// Even when called from within another function
function outer() {
    function inner() {
        console.log(this);
    }
    inner(); // undefined (strict) or global (non-strict)
}

outer();

// Assigned to variable - still default binding
const obj = {
    method: function() {
        console.log(this);
    }
};

const fn = obj.method;
fn(); // undefined (strict) or global (non-strict) - NOT obj!
```

---

## 🎯 `this` in Objects (Implicit Binding)

```javascript
// Implicit binding - `this` is the object BEFORE the dot
const user = {
    name: "John",
    greet: function() {
        console.log(`Hello, I'm ${this.name}`);
    }
};

user.greet(); // "Hello, I'm John" - this = user

// Nested objects - only immediate object matters
const company = {
    name: "TechCorp",
    department: {
        name: "Engineering",
        announce: function() {
            console.log(`Department: ${this.name}`);
        }
    }
};

company.department.announce(); // "Department: Engineering" - this = department

// Common mistake: Losing `this`
const greetFn = user.greet;
greetFn(); // "Hello, I'm undefined" - lost implicit binding!

// Solution 1: bind
const boundGreet = user.greet.bind(user);
boundGreet(); // "Hello, I'm John"

// Solution 2: wrapper function
const wrappedGreet = () => user.greet();
wrappedGreet(); // "Hello, I'm John"

// Method shorthand (ES6+)
const person = {
    name: "Jane",
    greet() {
        console.log(`Hi, I'm ${this.name}`);
    }
};
person.greet(); // "Hi, I'm Jane"
```

---

## ➡️ `this` in Arrow Functions

Arrow functions don't have their own `this` - they inherit from enclosing scope.

```javascript
// Arrow function inherits this from parent
const obj = {
    name: "MyObject",
    regularMethod: function() {
        console.log("Regular:", this.name); // "MyObject"
        
        const arrowFn = () => {
            console.log("Arrow:", this.name); // "MyObject" (inherited)
        };
        arrowFn();
    },
    arrowMethod: () => {
        console.log("Arrow method:", this.name); // undefined (inherits global this)
    }
};

obj.regularMethod();
obj.arrowMethod();

// Common use case: callbacks
const counter = {
    count: 0,
    increment: function() {
        // Problem with regular function
        setTimeout(function() {
            this.count++; // `this` is global/undefined, not counter!
            console.log(this.count); // NaN or error
        }, 100);
        
        // Solution with arrow function
        setTimeout(() => {
            this.count++; // `this` is counter (inherited)
            console.log(this.count); // 1
        }, 100);
    }
};

// Arrow functions in classes
class MyClass {
    name = "MyClass";
    
    // Regular method
    regularMethod() {
        console.log(this.name);
    }
    
    // Arrow function as class field
    arrowMethod = () => {
        console.log(this.name);
    }
}

const instance = new MyClass();
const regular = instance.regularMethod;
const arrow = instance.arrowMethod;

// regular(); // Error - lost this
arrow(); // "MyClass" - arrow preserves this!

/*
═══════════════════════════════════════════════════════════
WHEN TO USE ARROW vs REGULAR FUNCTIONS:
═══════════════════════════════════════════════════════════

Arrow Function (lexical this):
✅ Callbacks in setTimeout, setInterval
✅ Array methods (map, filter, reduce)
✅ Promise handlers (.then, .catch)
✅ When you need to preserve parent `this`

Regular Function (dynamic this):
✅ Object methods that need `this`
✅ Constructor functions
✅ Event handlers that need element as `this`
✅ Methods using arguments object
*/
```

---

## 📞 call() Method

`call()` invokes a function with a specific `this` value and arguments.

```javascript
// Syntax: fn.call(thisArg, arg1, arg2, ...)

function greet(greeting, punctuation) {
    console.log(`${greeting}, ${this.name}${punctuation}`);
}

const person = { name: "John" };

greet.call(person, "Hello", "!"); // "Hello, John!"

// Borrowing methods
const arrayLike = { 0: "a", 1: "b", 2: "c", length: 3 };
const arr = Array.prototype.slice.call(arrayLike);
console.log(arr); // ["a", "b", "c"]

// Getting true type
const getType = Object.prototype.toString;
console.log(getType.call([]));        // "[object Array]"
console.log(getType.call(null));      // "[object Null]"
console.log(getType.call(undefined)); // "[object Undefined]"

// Method chaining with call
const person1 = { name: "Alice" };
const person2 = { name: "Bob" };

function introduce() {
    return `I'm ${this.name}`;
}

console.log(introduce.call(person1)); // "I'm Alice"
console.log(introduce.call(person2)); // "I'm Bob"

// call with null/undefined
function showThis() {
    console.log(this);
}

showThis.call(null);      // global (non-strict) or null (strict)
showThis.call(undefined); // global (non-strict) or undefined (strict)
```

---

## 📲 apply() Method

`apply()` is like `call()` but takes arguments as an array.

```javascript
// Syntax: fn.apply(thisArg, [argsArray])

function introduce(greeting, age) {
    console.log(`${greeting}, I'm ${this.name}, ${age} years old`);
}

const person = { name: "Jane" };

introduce.apply(person, ["Hi", 25]); // "Hi, I'm Jane, 25 years old"

// Useful for functions that take individual arguments
const numbers = [5, 6, 2, 3, 7];

// Before ES6 spread
const max = Math.max.apply(null, numbers);
console.log(max); // 7

// With ES6 spread (preferred now)
const max2 = Math.max(...numbers);

// Merging arrays
const arr1 = [1, 2, 3];
const arr2 = [4, 5, 6];

// Before ES6
Array.prototype.push.apply(arr1, arr2);
console.log(arr1); // [1, 2, 3, 4, 5, 6]

// With ES6 spread (preferred)
arr1.push(...arr2);

/*
═══════════════════════════════════════════════════════════
call() vs apply():
═══════════════════════════════════════════════════════════

call()  → Arguments passed individually
apply() → Arguments passed as array

Mnemonic:
- Call = Comma separated arguments
- Apply = Array of arguments
*/
```

---

## 🔗 bind() Method

`bind()` creates a new function with `this` permanently bound.

```javascript
// Syntax: fn.bind(thisArg, arg1, arg2, ...)

function greet(greeting) {
    console.log(`${greeting}, ${this.name}!`);
}

const person = { name: "John" };

const boundGreet = greet.bind(person);
boundGreet("Hello"); // "Hello, John!"

// bind doesn't invoke the function - it returns a new function
const anotherBound = greet.bind(person, "Hi");
anotherBound(); // "Hi, John!" - greeting already bound

// Partial application with bind
function multiply(a, b) {
    return a * b;
}

const double = multiply.bind(null, 2);
console.log(double(5)); // 10
console.log(double(10)); // 20

// bind is permanent - can't be overridden
const obj1 = { name: "Obj1" };
const obj2 = { name: "Obj2" };

const bound = greet.bind(obj1);
bound.call(obj2, "Hey"); // "Hey, Obj1!" - still bound to obj1

// Common use: event handlers
class Button {
    constructor(label) {
        this.label = label;
    }
    
    handleClick() {
        console.log(`Button ${this.label} clicked`);
    }
}

const btn = new Button("Submit");
// document.addEventListener("click", btn.handleClick); // `this` would be document
document.addEventListener("click", btn.handleClick.bind(btn)); // `this` is btn

// Alternative: arrow function in class
class Button2 {
    constructor(label) {
        this.label = label;
    }
    
    handleClick = () => {
        console.log(`Button ${this.label} clicked`);
    }
}

const btn2 = new Button2("Submit");
document.addEventListener("click", btn2.handleClick); // Works without bind!
```

---

## 🏗️ new Binding

When using `new`, `this` refers to the newly created object.

```javascript
function Person(name, age) {
    // this = {} (empty object created by new)
    this.name = name;
    this.age = age;
    // return this; (implicit)
}

const john = new Person("John", 30);
console.log(john.name); // "John"

// What `new` does internally:
function simulateNew(Constructor, ...args) {
    // 1. Create new object
    const obj = {};
    
    // 2. Set prototype
    Object.setPrototypeOf(obj, Constructor.prototype);
    
    // 3. Call constructor with `this` = obj
    const result = Constructor.apply(obj, args);
    
    // 4. Return obj (unless constructor returns an object)
    return result instanceof Object ? result : obj;
}

// Constructor returning object overrides `this`
function ReturnObject(name) {
    this.name = name;
    return { differentProperty: "returned" };
}

const instance = new ReturnObject("John");
console.log(instance.name);              // undefined
console.log(instance.differentProperty); // "returned"

// new binding has highest priority
function showThis() {
    console.log(this);
}

const boundShow = showThis.bind({ bound: true });
boundShow();      // { bound: true }
new boundShow();  // showThis {} (new wins over bind)
```

---

## 💡 Implement Your Own bind()

```javascript
// Simple implementation
Function.prototype.myBind = function(context, ...boundArgs) {
    const fn = this;
    
    return function(...args) {
        return fn.apply(context, [...boundArgs, ...args]);
    };
};

// Test
function greet(greeting, punctuation) {
    return `${greeting}, ${this.name}${punctuation}`;
}

const person = { name: "John" };
const myBoundGreet = greet.myBind(person, "Hello");
console.log(myBoundGreet("!")); // "Hello, John!"

// Advanced implementation (handles new)
Function.prototype.myBindAdvanced = function(context, ...boundArgs) {
    const fn = this;
    
    const boundFunction = function(...args) {
        // Check if called with new
        const isNew = this instanceof boundFunction;
        
        return fn.apply(
            isNew ? this : context,
            [...boundArgs, ...args]
        );
    };
    
    // Preserve prototype for new
    if (fn.prototype) {
        boundFunction.prototype = Object.create(fn.prototype);
    }
    
    return boundFunction;
};

// Test with new
function Animal(name) {
    this.name = name;
}

const BoundAnimal = Animal.myBindAdvanced({ ignored: true });
const cat = new BoundAnimal("Whiskers");
console.log(cat.name); // "Whiskers" (new binding works)
```

---

## ❓ Interview Questions

### Q1: What's the difference between arrow and regular function?

```javascript
/*
1. `this` binding:
   - Regular: Dynamic (depends on how called)
   - Arrow: Lexical (inherited from parent)

2. `arguments` object:
   - Regular: Has own arguments
   - Arrow: No arguments (use rest params)

3. `new` keyword:
   - Regular: Can be used as constructor
   - Arrow: Cannot be used with new

4. `prototype`:
   - Regular: Has prototype property
   - Arrow: No prototype

5. Implicit return:
   - Regular: Need explicit return
   - Arrow: Can have implicit return
*/

// Example demonstrating all differences
function Regular(name) {
    this.name = name;
    console.log(arguments);
}

const Arrow = (name) => {
    // this.name = name; // Can't use in constructor context
    // console.log(arguments); // ReferenceError
};

console.log(Regular.prototype); // Regular {}
console.log(Arrow.prototype);   // undefined

new Regular("John"); // Works
// new Arrow("Jane"); // TypeError: Arrow is not a constructor
```

### Q2: Predict the output

```javascript
const obj = {
    name: "Object",
    getName: function() {
        return this.name;
    },
    getNameArrow: () => {
        return this.name;
    }
};

console.log(obj.getName());      // ?  - "Object"
console.log(obj.getNameArrow()); // ?  - undefined (global this)

const getNameFn = obj.getName;
console.log(getNameFn());        // ?  - undefined (lost this)
```

### Q3: Fix this code

```javascript
// Problem
const person = {
    name: "Alice",
    friends: ["Bob", "Charlie"],
    printFriends: function() {
        this.friends.forEach(function(friend) {
            console.log(`${this.name} knows ${friend}`);
        });
    }
};

person.printFriends();
// Output: "undefined knows Bob", "undefined knows Charlie"

// Solution 1: Arrow function
const person1 = {
    name: "Alice",
    friends: ["Bob", "Charlie"],
    printFriends: function() {
        this.friends.forEach((friend) => {
            console.log(`${this.name} knows ${friend}`);
        });
    }
};

// Solution 2: bind
const person2 = {
    name: "Alice",
    friends: ["Bob", "Charlie"],
    printFriends: function() {
        this.friends.forEach(function(friend) {
            console.log(`${this.name} knows ${friend}`);
        }.bind(this));
    }
};

// Solution 3: Store this in variable
const person3 = {
    name: "Alice",
    friends: ["Bob", "Charlie"],
    printFriends: function() {
        const self = this;
        this.friends.forEach(function(friend) {
            console.log(`${self.name} knows ${friend}`);
        });
    }
};

// Solution 4: Use thisArg parameter
const person4 = {
    name: "Alice",
    friends: ["Bob", "Charlie"],
    printFriends: function() {
        this.friends.forEach(function(friend) {
            console.log(`${this.name} knows ${friend}`);
        }, this); // Second argument to forEach
    }
};
```

---

## 🔬 Practice Problems

```javascript
// Problem 1: What's the output?
var name = "Global";

const obj = {
    name: "Object",
    sayName: function() {
        console.log(this.name);
    },
    sayNameArrow: () => {
        console.log(this.name);
    },
    nested: {
        name: "Nested",
        sayName: function() {
            console.log(this.name);
        }
    }
};

obj.sayName();           // ?
obj.sayNameArrow();      // ?
obj.nested.sayName();    // ?
const fn = obj.sayName;
fn();                    // ?

// Answers: "Object", "Global"/undefined, "Nested", "Global"/undefined

// Problem 2: Implement call
Function.prototype.myCall = function(context, ...args) {
    context = context || globalThis;
    const fnSymbol = Symbol();
    context[fnSymbol] = this;
    const result = context[fnSymbol](...args);
    delete context[fnSymbol];
    return result;
};

// Problem 3: Implement apply
Function.prototype.myApply = function(context, args = []) {
    context = context || globalThis;
    const fnSymbol = Symbol();
    context[fnSymbol] = this;
    const result = context[fnSymbol](...args);
    delete context[fnSymbol];
    return result;
};

// Problem 4: What's logged?
const obj2 = {
    count: 0,
    increment() {
        this.count++;
    },
    incrementLater() {
        setTimeout(this.increment, 100);
    }
};

obj2.incrementLater();
setTimeout(() => console.log(obj2.count), 200); // ?
// Answer: 0 (increment's this was global, not obj2)

// Fix:
const obj3 = {
    count: 0,
    increment() {
        this.count++;
    },
    incrementLater() {
        setTimeout(() => this.increment(), 100);
    }
};
```

---

## 📋 `this` Cheat Sheet

```javascript
/*
═══════════════════════════════════════════════════════════
`this` BINDING QUICK REFERENCE:
═══════════════════════════════════════════════════════════

Context                          │ `this` value
─────────────────────────────────────────────────────────
Global scope                     │ window/global
Function (non-strict)            │ window/global
Function (strict)                │ undefined
Object method                    │ The object
Nested function in method        │ window/undefined (not object!)
Arrow function                   │ Inherits from parent
Event handler (=> fn)            │ Inherits from parent
Event handler (regular)          │ Event target element
call/apply                       │ First argument
bind                             │ Bound value (permanent)
new                              │ New object
Class method                     │ Instance
Class field (arrow)              │ Instance (always)

═══════════════════════════════════════════════════════════
PRIORITY ORDER (highest to lowest):
═══════════════════════════════════════════════════════════

1. new binding
2. explicit binding (call/apply/bind)
3. implicit binding (object.method)
4. default binding (global/undefined)

Arrow functions ignore all above - always lexical!
*/
```

---

## ✅ Day 6 Checklist

- [ ] Understand `this` in global scope
- [ ] Master default binding (standalone functions)
- [ ] Master implicit binding (object methods)
- [ ] Understand arrow function lexical `this`
- [ ] Use call() for explicit `this`
- [ ] Use apply() with array arguments
- [ ] Use bind() to create bound functions
- [ ] Understand new binding
- [ ] Know binding priority order
- [ ] Implement your own bind()
- [ ] Fix common `this` issues in callbacks
- [ ] Complete all practice problems
