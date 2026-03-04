# Day 1: JavaScript Engine & Runtime

## 🎯 Learning Objectives
- Understand what JavaScript is at its core
- Learn how JS engines work (V8)
- Master Call Stack and Heap concepts
- Understand Compilation vs Interpretation
- Deep dive into Execution Context

---

## 📚 What is JavaScript?

JavaScript is a **high-level, interpreted, single-threaded, dynamic language** with:
- First-class functions
- Prototype-based object orientation
- Event-driven, non-blocking I/O model

```javascript
// JavaScript runs in different environments
// Browser: window object is the global context
console.log(typeof window); // "object" (in browser)

// Node.js: global object is the global context
console.log(typeof global); // "object" (in Node.js)
```

### Key Characteristics:
1. **Single-threaded**: One call stack, one thing at a time
2. **Non-blocking**: Uses callbacks, promises, async/await
3. **Dynamic typing**: Types determined at runtime
4. **JIT compiled**: Modern engines compile JS to machine code

---

## 🔧 JavaScript Engine (V8)

### What is V8?
V8 is Google's open-source high-performance JavaScript and WebAssembly engine, written in C++.

```
┌─────────────────────────────────────────────────────────────┐
│                        V8 ENGINE                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐  │
│  │   Parser    │───▶│     AST     │───▶│   Interpreter   │  │
│  │             │    │             │    │   (Ignition)    │  │
│  └─────────────┘    └─────────────┘    └────────┬────────┘  │
│                                                  │           │
│                                                  ▼           │
│                                         ┌───────────────┐   │
│                                         │   Bytecode    │   │
│                                         └───────┬───────┘   │
│                                                  │           │
│                                                  ▼           │
│                                         ┌───────────────┐   │
│                                         │   Compiler    │   │
│                                         │ (TurboFan)    │   │
│                                         └───────┬───────┘   │
│                                                  │           │
│                                                  ▼           │
│                                         ┌───────────────┐   │
│                                         │ Machine Code  │   │
│                                         └───────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### V8 Components:

1. **Parser**: Converts JS code to AST (Abstract Syntax Tree)
2. **Ignition**: Interpreter that generates bytecode
3. **TurboFan**: Optimizing compiler for hot code
4. **Garbage Collector (Orinoco)**: Memory management

```javascript
// Example: How V8 optimizes this code
function add(a, b) {
    return a + b;
}

// Called many times with numbers - V8 optimizes for numbers
for (let i = 0; i < 10000; i++) {
    add(i, i + 1); // V8 marks this as "hot" and optimizes
}

// But if you suddenly do this:
add("hello", "world"); // De-optimization occurs!
```

---

## 📦 Call Stack

The **Call Stack** is a LIFO (Last In, First Out) data structure that tracks function execution.

```javascript
function first() {
    console.log("First function");
    second();
    console.log("First function ending");
}

function second() {
    console.log("Second function");
    third();
    console.log("Second function ending");
}

function third() {
    console.log("Third function");
}

first();

/*
Call Stack Evolution:
═══════════════════════════════════════════════════════════

Step 1:     Step 2:     Step 3:     Step 4:     Step 5:
┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐
│       │   │       │   │third()│   │       │   │       │
│       │   │second │   │second │   │second │   │       │
│first()│   │first()│   │first()│   │first()│   │first()│
└───────┘   └───────┘   └───────┘   └───────┘   └───────┘

Output:
- "First function"
- "Second function"
- "Third function"
- "Second function ending"
- "First function ending"
*/
```

### Stack Overflow Example:
```javascript
function infiniteLoop() {
    infiniteLoop(); // RangeError: Maximum call stack size exceeded
}

// Each browser has different stack limits
// Chrome: ~10,000-16,000 frames
// Firefox: ~50,000+ frames
```

---

## 🗄️ Heap Memory

The **Heap** is an unstructured memory region where objects are stored.

```javascript
// Primitives are stored in Stack
let a = 10;        // Stack
let b = "hello";   // Stack (reference to string pool)

// Objects are stored in Heap
let obj = {        // Reference in Stack, Object in Heap
    name: "John",
    age: 30
};

let arr = [1, 2, 3]; // Reference in Stack, Array in Heap

/*
Memory Layout:
═══════════════════════════════════════════════════════════

   STACK                          HEAP
┌──────────────┐            ┌──────────────────┐
│ a = 10       │            │                  │
│ b = "hello"  │            │  ┌────────────┐  │
│ obj = 0x001  │───────────▶│  │{name:"John"│  │
│ arr = 0x002  │───────┐    │  │ age: 30}   │  │
└──────────────┘       │    │  └────────────┘  │
                       │    │                  │
                       │    │  ┌────────────┐  │
                       └───▶│  │ [1, 2, 3]  │  │
                            │  └────────────┘  │
                            └──────────────────┘
*/
```

---

## ⚙️ Compilation vs Interpretation

### Traditional Interpretation:
```
Source Code ──▶ Line-by-line execution ──▶ Result
                (slow, reads code each time)
```

### Traditional Compilation:
```
Source Code ──▶ Compiler ──▶ Machine Code ──▶ Execution
                (fast execution, but compile step needed)
```

### JIT (Just-In-Time) Compilation - Used by V8:
```
Source Code ──▶ Parse ──▶ Bytecode ──▶ Execute
                              │
                              ▼ (Hot code detected)
                         Optimize ──▶ Machine Code
                              │
                              ▼ (Type changed)
                         De-optimize ──▶ Back to Bytecode
```

```javascript
// JIT Optimization Example
function calculate(x) {
    return x * 2 + 1;
}

// First few calls - interpreted
calculate(5);  // Interpreted
calculate(10); // Interpreted

// After many calls - JIT compiled
for (let i = 0; i < 10000; i++) {
    calculate(i); // Eventually compiled to machine code
}

// V8 Optimization Tiers:
// 1. Ignition (Interpreter) - Quick start
// 2. Sparkplug - Baseline compiler (fast)
// 3. Maglev - Mid-tier optimizer
// 4. TurboFan - Full optimizer (slowest to compile, fastest to run)
```

---

## 🏗️ Execution Context

An **Execution Context** is the environment in which JavaScript code is evaluated and executed.

### Types of Execution Context:

1. **Global Execution Context (GEC)**: Created when script starts
2. **Function Execution Context (FEC)**: Created for each function call
3. **Eval Execution Context**: Created inside eval() (avoid using)

### Execution Context Phases:

```javascript
var name = "John";

function greet() {
    var message = "Hello";
    console.log(message + " " + name);
}

greet();

/*
═══════════════════════════════════════════════════════════
PHASE 1: CREATION PHASE (Memory Allocation)
═══════════════════════════════════════════════════════════

Global Execution Context:
┌────────────────────────────────────────────────────────┐
│ Variable Object (VO):                                   │
│   name: undefined                                       │
│   greet: function reference                             │
│                                                         │
│ Scope Chain: [Global VO]                                │
│ this: window (browser) / global (Node.js)               │
└────────────────────────────────────────────────────────┘

═══════════════════════════════════════════════════════════
PHASE 2: EXECUTION PHASE
═══════════════════════════════════════════════════════════

Global Execution Context:
┌────────────────────────────────────────────────────────┐
│ Variable Object (VO):                                   │
│   name: "John"        ← Assigned                        │
│   greet: function reference                             │
└────────────────────────────────────────────────────────┘

When greet() is called, new FEC is created:
┌────────────────────────────────────────────────────────┐
│ Function Execution Context (greet):                     │
│                                                         │
│ Variable Object (VO):                                   │
│   message: undefined → "Hello"                          │
│   arguments: {}                                         │
│                                                         │
│ Scope Chain: [greet VO, Global VO]                     │
│ this: window (non-strict) / undefined (strict)         │
└────────────────────────────────────────────────────────┘
*/
```

### Execution Context Stack (Call Stack):

```javascript
var a = 10;

function outer() {
    var b = 20;
    
    function inner() {
        var c = 30;
        console.log(a + b + c); // 60
    }
    
    inner();
}

outer();

/*
Execution Context Stack Evolution:
═══════════════════════════════════════════════════════════

Step 1:         Step 2:         Step 3:         Step 4:
                                ┌─────────┐     
                ┌─────────┐     │ inner() │     ┌─────────┐
┌─────────┐     │ outer() │     │ outer() │     │ outer() │
│ Global  │     │ Global  │     │ Global  │     │ Global  │
└─────────┘     └─────────┘     └─────────┘     └─────────┘

Step 5:
┌─────────┐
│ Global  │ ← Finally, Global is also popped
└─────────┘
*/
```

---

## 📝 Task: Explain console.log(a); var a = 10;

```javascript
console.log(a); // Output: undefined
var a = 10;
console.log(a); // Output: 10

/*
═══════════════════════════════════════════════════════════
INTERNAL WORKING - Step by Step:
═══════════════════════════════════════════════════════════

1. PARSING PHASE:
   - V8 parses entire code and creates AST
   - Identifies all variable and function declarations

2. CREATION PHASE (Hoisting):
   - Global Execution Context created
   - Memory allocated for 'a'
   - 'a' is initialized to 'undefined' (var hoisting)
   
   Variable Object: { a: undefined }

3. EXECUTION PHASE:
   Line 1: console.log(a)
   - Looks up 'a' in Variable Object
   - Finds 'a' = undefined
   - Prints: undefined

   Line 2: var a = 10
   - 'var a' already hoisted (ignored now)
   - '= 10' assignment happens
   - Updates: { a: 10 }

   Line 3: console.log(a)
   - Looks up 'a' in Variable Object
   - Finds 'a' = 10
   - Prints: 10

═══════════════════════════════════════════════════════════
WHY var IS HOISTED:
═══════════════════════════════════════════════════════════

JavaScript engine processes code in two passes:
1. First pass: Collect all declarations (hoisting)
2. Second pass: Execute code line by line

This is why var declarations are "moved" to the top mentally.
The actual code is NOT modified, but the behavior appears that way.

COMPARISON with let/const:
═══════════════════════════════════════════════════════════

console.log(b); // ReferenceError: Cannot access 'b' before initialization
let b = 20;

// let and const are hoisted but NOT initialized
// They stay in "Temporal Dead Zone" until declaration line
*/
```

---

## 🎯 Execution Context Flow Diagram

```
╔═══════════════════════════════════════════════════════════════════╗
║                    EXECUTION CONTEXT FLOW                          ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  1. Script starts                                                  ║
║     │                                                              ║
║     ▼                                                              ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │              GLOBAL EXECUTION CONTEXT                         │ ║
║  │  ┌────────────────────────────────────────────────────────┐  │ ║
║  │  │ CREATION PHASE:                                         │  │ ║
║  │  │ • Create Global Object (window/global)                  │  │ ║
║  │  │ • Create 'this' binding (→ Global Object)               │  │ ║
║  │  │ • Setup memory heap for variables/functions             │  │ ║
║  │  │ • Hoist function declarations (full function)           │  │ ║
║  │  │ • Hoist var declarations (set to undefined)             │  │ ║
║  │  └────────────────────────────────────────────────────────┘  │ ║
║  │  ┌────────────────────────────────────────────────────────┐  │ ║
║  │  │ EXECUTION PHASE:                                        │  │ ║
║  │  │ • Execute code line by line                             │  │ ║
║  │  │ • Assign values to variables                            │  │ ║
║  │  │ • Execute function calls → Create new FEC               │  │ ║
║  │  └────────────────────────────────────────────────────────┘  │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║     │                                                              ║
║     │ Function called                                              ║
║     ▼                                                              ║
║  ┌──────────────────────────────────────────────────────────────┐ ║
║  │            FUNCTION EXECUTION CONTEXT                         │ ║
║  │  ┌────────────────────────────────────────────────────────┐  │ ║
║  │  │ CREATION PHASE:                                         │  │ ║
║  │  │ • Create Arguments object                               │  │ ║
║  │  │ • Create 'this' binding (depends on call)               │  │ ║
║  │  │ • Setup local variable environment                      │  │ ║
║  │  │ • Hoist local declarations                              │  │ ║
║  │  └────────────────────────────────────────────────────────┘  │ ║
║  │  ┌────────────────────────────────────────────────────────┐  │ ║
║  │  │ EXECUTION PHASE:                                        │  │ ║
║  │  │ • Execute function body                                 │  │ ║
║  │  │ • Return value (or undefined)                           │  │ ║
║  │  │ • Pop from call stack                                   │  │ ║
║  │  └────────────────────────────────────────────────────────┘  │ ║
║  └──────────────────────────────────────────────────────────────┘ ║
║                                                                    ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 💡 Interview Questions

### Q1: What happens when JavaScript code runs?
**Answer**: JS engine creates a Global Execution Context, which has two phases:
1. **Creation Phase**: Memory is allocated, variables are hoisted (var → undefined, let/const → TDZ), functions are fully hoisted
2. **Execution Phase**: Code runs line by line, values are assigned

### Q2: Explain the difference between Call Stack and Heap
**Answer**: 
- **Call Stack**: LIFO structure for tracking function execution, stores primitive values and references
- **Heap**: Unstructured memory pool for storing objects and complex data structures

### Q3: What is JIT compilation?
**Answer**: JIT (Just-In-Time) compilation is a hybrid approach where code is initially interpreted, and frequently executed "hot" code is compiled to optimized machine code at runtime for better performance.

### Q4: What is an Execution Context?
**Answer**: An execution context is the environment where JS code is evaluated. It contains:
- Variable Object (variables, function declarations, arguments)
- Scope Chain (access to outer scopes)
- this binding

---

## 🔬 Practice Code

```javascript
// Practice 1: Predict the output
console.log(foo);
console.log(bar);
var foo = "Hello";
function bar() {
    return "World";
}

// Answer: 
// undefined (foo is hoisted but not assigned)
// [Function: bar] (functions are fully hoisted)

// Practice 2: Trace the call stack
function multiply(a, b) {
    return a * b;
}

function square(n) {
    return multiply(n, n);
}

function printSquare(n) {
    var result = square(n);
    console.log(result);
}

printSquare(5);
// Trace: Global → printSquare → square → multiply → (returns) → square → printSquare → Global

// Practice 3: Execution Context creation
var x = 1;
function a() {
    var y = 2;
    function b() {
        var z = 3;
        console.log(x + y + z); // 6
    }
    b();
}
a();

// Each function creates its own execution context
// Scope chain: b's VO → a's VO → Global VO
```

---

## 📚 Additional Resources

- [V8 Blog](https://v8.dev/blog)
- [JavaScript.info - Execution Context](https://javascript.info/execution-context)
- [MDN - Memory Management](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Memory_Management)

---

## ✅ Day 1 Checklist

- [ ] Understand what JavaScript is
- [ ] Learn V8 engine components (Parser, Ignition, TurboFan)
- [ ] Master Call Stack concept
- [ ] Understand Heap memory
- [ ] Differentiate Compilation vs Interpretation
- [ ] Understand JIT compilation
- [ ] Master Execution Context (Creation + Execution phases)
- [ ] Complete all practice problems
