# Day 2: Variables & Scope

## 🎯 Learning Objectives
- Deep understanding of var, let, const
- Master Temporal Dead Zone (TDZ)
- Understand Hoisting completely
- Learn Scope Chain mechanism
- Understand Block Scope vs Function Scope

---

## 📚 var vs let vs const (Deep Dive)

### Comparison Table

| Feature | var | let | const |
|---------|-----|-----|-------|
| Scope | Function | Block | Block |
| Hoisting | Yes (undefined) | Yes (TDZ) | Yes (TDZ) |
| Re-declaration | ✅ Allowed | ❌ Error | ❌ Error |
| Re-assignment | ✅ Allowed | ✅ Allowed | ❌ Error |
| Global Object | ✅ Added | ❌ Not added | ❌ Not added |
| TDZ | ❌ No | ✅ Yes | ✅ Yes |

### 1. var (Function Scoped)

```javascript
// var is FUNCTION scoped, not block scoped
function testVar() {
    if (true) {
        var x = 10;
    }
    console.log(x); // 10 - accessible outside if block!
}

testVar();

// var in global scope attaches to window object
var globalVar = "I'm global";
console.log(window.globalVar); // "I'm global" (in browser)

// var can be re-declared
var name = "John";
var name = "Jane"; // No error!
console.log(name); // "Jane"

// var hoisting - initialized with undefined
console.log(hoisted); // undefined
var hoisted = "value";
```

### 2. let (Block Scoped)

```javascript
// let is BLOCK scoped
function testLet() {
    if (true) {
        let y = 20;
        console.log(y); // 20
    }
    console.log(y); // ReferenceError: y is not defined
}

// let does NOT attach to global object
let globalLet = "not on window";
console.log(window.globalLet); // undefined

// let cannot be re-declared in same scope
let city = "NYC";
let city = "LA"; // SyntaxError: Identifier 'city' has already been declared

// But can be re-declared in different scope
let city = "NYC";
if (true) {
    let city = "LA"; // Different scope, OK
    console.log(city); // "LA"
}
console.log(city); // "NYC"

// let can be reassigned
let counter = 1;
counter = 2; // OK
```

### 3. const (Block Scoped, Immutable Binding)

```javascript
// const MUST be initialized at declaration
const PI; // SyntaxError: Missing initializer in const declaration
const PI = 3.14159; // OK

// const cannot be reassigned
const MAX = 100;
MAX = 200; // TypeError: Assignment to constant variable

// BUT const objects can be mutated!
const user = { name: "John" };
user.name = "Jane"; // OK - mutating property
user.age = 30;      // OK - adding property
console.log(user);  // { name: "Jane", age: 30 }

user = {};          // TypeError - can't reassign reference

// Same with arrays
const arr = [1, 2, 3];
arr.push(4);        // OK
arr[0] = 10;        // OK
arr = [5, 6];       // TypeError

// To make truly immutable objects
const frozen = Object.freeze({ name: "John" });
frozen.name = "Jane"; // Silently fails (or throws in strict mode)
console.log(frozen.name); // "John"
```

---

## ⏰ Temporal Dead Zone (TDZ)

The **TDZ** is the period between entering a scope and the variable being declared, where accessing the variable throws a ReferenceError.

```javascript
/*
═══════════════════════════════════════════════════════════
TEMPORAL DEAD ZONE VISUALIZATION:
═══════════════════════════════════════════════════════════

{   // Block starts - TDZ for 'x' begins
    │
    │  ← TDZ ZONE (accessing x here throws ReferenceError)
    │
    │  console.log(x); // ReferenceError!
    │
    │  ← TDZ ZONE
    │
    let x = 10;  ← TDZ ends, x is initialized
    │
    console.log(x); // 10 - OK
}
*/

// TDZ Example 1: Basic
{
    // TDZ starts
    console.log(myLet); // ReferenceError: Cannot access 'myLet' before initialization
    let myLet = "Hello";
    // TDZ ends after this line
}

// TDZ Example 2: Function in TDZ
{
    const func = () => console.log(secret); // Function defined
    // TDZ for 'secret' still active
    func(); // ReferenceError when called (not when defined!)
    let secret = 42;
}

// TDZ Example 3: Default parameters
function example(a = b, b = 1) {
    console.log(a, b);
}
example(); // ReferenceError: Cannot access 'b' before initialization

// Fixed version
function exampleFixed(b = 1, a = b) {
    console.log(a, b);
}
exampleFixed(); // 1 1

// TDZ Example 4: typeof
console.log(typeof undeclared); // "undefined" - no error
console.log(typeof letVariable); // ReferenceError!
let letVariable = 10;
```

### Why TDZ Exists?

1. **Catches errors early**: Accessing uninitialized variables is usually a bug
2. **Consistent behavior**: const needs TDZ (must be initialized), let follows same rules
3. **Prevents hoisting confusion**: Makes code more predictable

---

## 🏗️ Hoisting (Complete Understanding)

**Hoisting** is JavaScript's behavior of moving declarations to the top of their scope during compilation.

### How Different Declarations are Hoisted:

```javascript
/*
═══════════════════════════════════════════════════════════
HOISTING BEHAVIOR:
═══════════════════════════════════════════════════════════

Declaration Type    │ Hoisted? │ Initial Value │ Accessible Before?
─────────────────────────────────────────────────────────────
var                 │   Yes    │  undefined    │    Yes (undefined)
let                 │   Yes    │  <TDZ>        │    No (ReferenceError)
const               │   Yes    │  <TDZ>        │    No (ReferenceError)
function decl.      │   Yes    │  Full fn      │    Yes (callable)
function expr.      │   Var*   │  undefined    │    No (TypeError)
class               │   Yes    │  <TDZ>        │    No (ReferenceError)
*/

// 1. var hoisting
console.log(a); // undefined
var a = 5;
// Interpreted as:
// var a;
// console.log(a);
// a = 5;

// 2. let/const hoisting (into TDZ)
console.log(b); // ReferenceError
let b = 10;

// 3. Function declaration hoisting (FULLY hoisted)
sayHello(); // "Hello!" - works!
function sayHello() {
    console.log("Hello!");
}

// 4. Function expression hoisting (only var is hoisted)
sayBye(); // TypeError: sayBye is not a function
var sayBye = function() {
    console.log("Bye!");
};
// Interpreted as:
// var sayBye; // undefined
// sayBye(); // calling undefined as function = TypeError
// sayBye = function() {...};

// 5. Arrow function hoisting (same as function expression)
greet(); // TypeError: greet is not a function
var greet = () => console.log("Hi!");

// 6. Class hoisting (into TDZ)
const p = new Person(); // ReferenceError
class Person {}
```

### Hoisting Priority

```javascript
// When both function and var have same name
console.log(foo); // [Function: foo]
var foo = "variable";
function foo() {
    return "function";
}
console.log(foo); // "variable"

// Why? Functions are hoisted ABOVE variables
// Interpreted as:
// function foo() { return "function"; }  // Hoisted first
// var foo; // Ignored because foo already exists
// console.log(foo); // function
// foo = "variable";
// console.log(foo); // "variable"
```

---

## 🔗 Scope Chain

The **Scope Chain** is the mechanism by which JavaScript looks up variable values.

```javascript
/*
═══════════════════════════════════════════════════════════
SCOPE CHAIN VISUALIZATION:
═══════════════════════════════════════════════════════════

Global Scope
    │
    ├── globalVar = "global"
    │
    └── outer() 
            │
            ├── outerVar = "outer"
            │
            └── inner()
                    │
                    └── innerVar = "inner"

Lookup for variable in inner():
inner's scope → outer's scope → global scope → ReferenceError

*/

var globalVar = "global";

function outer() {
    var outerVar = "outer";
    
    function inner() {
        var innerVar = "inner";
        
        // Scope chain lookup
        console.log(innerVar);  // Found in inner's scope
        console.log(outerVar);  // Found in outer's scope
        console.log(globalVar); // Found in global scope
        console.log(unknown);   // ReferenceError: not found anywhere
    }
    
    inner();
}

outer();

// Scope chain is determined at function DEFINITION, not execution (Lexical Scope)
var x = 10;

function foo() {
    console.log(x); // 10, not 20
}

function bar() {
    var x = 20;
    foo(); // foo's scope chain was set when it was defined
}

bar(); // Output: 10
```

### Lexical Scope vs Dynamic Scope

```javascript
// JavaScript uses LEXICAL (static) scoping
// Scope is determined by where code is WRITTEN, not where it's CALLED

var name = "Global";

function outer() {
    var name = "Outer";
    
    function inner() {
        console.log(name); // Looks up based on where inner is defined
    }
    
    return inner;
}

var innerFunc = outer();
var name = "Changed Global";
innerFunc(); // "Outer" - lexical scope, not "Changed Global"
```

---

## 📦 Block Scope

Block scope is created by `{ }` and applies to `let` and `const`.

```javascript
// Block scope examples
{
    let blockLet = "I'm block scoped";
    const blockConst = "Me too";
    var blockVar = "I'm function/global scoped";
}

console.log(blockVar);   // Works - var ignores block scope
console.log(blockLet);   // ReferenceError
console.log(blockConst); // ReferenceError

// Block scope in loops
for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100);
}
// Output: 3, 3, 3 (var is shared across all iterations)

for (let j = 0; j < 3; j++) {
    setTimeout(() => console.log(j), 100);
}
// Output: 0, 1, 2 (let creates new binding each iteration)

// Block scope in if/switch
if (true) {
    let ifScoped = "only here";
}
console.log(ifScoped); // ReferenceError

switch (true) {
    case true:
        let switchScoped = "only in switch block";
        break;
}
console.log(switchScoped); // ReferenceError
```

---

## 🌍 Global Object

```javascript
// In browsers
console.log(this);    // Window object
console.log(window);  // Window object
console.log(self);    // Window object

// In Node.js
console.log(this);    // {} (empty object in module)
console.log(global);  // Global object

// globalThis (ES2020) - works everywhere
console.log(globalThis); // Window (browser) or global (Node.js)

// var attaches to global object
var varGlobal = "attached";
console.log(globalThis.varGlobal); // "attached"

// let/const do NOT attach
let letGlobal = "not attached";
const constGlobal = "not attached";
console.log(globalThis.letGlobal);   // undefined
console.log(globalThis.constGlobal); // undefined

// Function declarations also attach
function globalFunc() {}
console.log(globalThis.globalFunc); // [Function: globalFunc]
```

---

## ❓ Interview Questions & Answers

### Q1: What is the difference between var, let, and const?

**Answer**:
- **var**: Function-scoped, hoisted with undefined, can be re-declared, attaches to global object
- **let**: Block-scoped, hoisted into TDZ, cannot be re-declared in same scope, can be reassigned
- **const**: Block-scoped, hoisted into TDZ, cannot be re-declared or reassigned (but objects can be mutated)

### Q2: What is TDZ (Temporal Dead Zone)?

**Answer**: TDZ is the period between entering a scope and the actual declaration of a let/const variable. During TDZ, accessing the variable throws a ReferenceError. It exists to catch errors early and ensure const variables are properly initialized.

```javascript
{
    // TDZ starts
    console.log(x); // ReferenceError
    let x = 5; // TDZ ends
}
```

### Q3: Why is var dangerous in production apps?

**Answer**:
1. **Function scope**: Variables leak out of blocks (if, for, etc.)
2. **Hoisting to undefined**: Silent bugs when accessing before declaration
3. **Re-declaration allowed**: Can accidentally overwrite variables
4. **Global object pollution**: Creates properties on window/global
5. **Loop variable sharing**: Classic closure bug in async operations

```javascript
// Dangerous var behavior
for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100);
}
// Prints: 3, 3, 3 - not 0, 1, 2 as expected

// var leaks
if (true) {
    var leaked = "oops";
}
console.log(leaked); // "oops" - leaked out of block!
```

### Q4: Explain hoisting with examples

**Answer**:
```javascript
// What you write:
console.log(a);
sayHi();
var a = 10;
function sayHi() {
    console.log("Hi!");
}

// How JS interprets it:
function sayHi() {      // Functions hoisted first, fully
    console.log("Hi!");
}
var a;                  // var hoisted, initialized to undefined
console.log(a);         // undefined
sayHi();                // "Hi!"
a = 10;                 // Assignment stays in place
```

### Q5: What is scope chain?

**Answer**: The scope chain is a list of all variable objects that the current execution context has access to. When looking up a variable, JS starts from the innermost scope and moves outward until found or ReferenceError.

```javascript
var a = 1;
function outer() {
    var b = 2;
    function inner() {
        var c = 3;
        // Scope chain: inner → outer → global
        console.log(a + b + c); // Can access all three
    }
    inner();
}
outer();
```

---

## 🔬 Practice Problems

```javascript
// Problem 1: What's the output?
var x = 1;
function foo() {
    console.log(x);
    var x = 2;
}
foo();
// Answer: undefined (local x is hoisted, shadows global x)

// Problem 2: What's the output?
let y = 1;
{
    console.log(y);
    let y = 2;
}
// Answer: ReferenceError (TDZ - let y hoisted in block, but in TDZ)

// Problem 3: What's the output?
for (var i = 0; i < 3; i++) {
    setTimeout(function() {
        console.log(i);
    }, 1000);
}
// Answer: 3, 3, 3 after 1 second (var is shared)

// Problem 4: Fix Problem 3 using IIFE
for (var i = 0; i < 3; i++) {
    (function(j) {
        setTimeout(function() {
            console.log(j);
        }, 1000);
    })(i);
}
// Answer: 0, 1, 2 (IIFE captures each value)

// Problem 5: Fix Problem 3 using let
for (let i = 0; i < 3; i++) {
    setTimeout(function() {
        console.log(i);
    }, 1000);
}
// Answer: 0, 1, 2 (let creates new binding per iteration)

// Problem 6: What's the output?
const obj = { a: 1 };
obj.b = 2;
console.log(obj);
obj = { c: 3 };
// Answer: { a: 1, b: 2 }, then TypeError

// Problem 7: What's the output?
console.log(typeof foo);
console.log(typeof bar);
var foo = function() {};
function bar() {}
// Answer: "undefined", "function"

// Problem 8: What's the output?
var a = 1;
function outer() {
    var a = 2;
    function inner() {
        console.log(a);
    }
    return inner;
}
var innerFn = outer();
a = 3;
innerFn();
// Answer: 2 (lexical scope - inner was defined inside outer)
```

---

## ✅ Day 2 Checklist

- [ ] Understand var (function scope, hoisting, re-declaration)
- [ ] Understand let (block scope, TDZ, no re-declaration)
- [ ] Understand const (block scope, TDZ, immutable binding)
- [ ] Master Temporal Dead Zone concept
- [ ] Understand hoisting for all declaration types
- [ ] Learn scope chain lookup mechanism
- [ ] Understand block scope vs function scope
- [ ] Know how global object works
- [ ] Complete all practice problems
- [ ] Practice explaining TDZ in interview style
