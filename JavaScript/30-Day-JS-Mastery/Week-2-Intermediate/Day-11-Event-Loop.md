# Day 11: Event Loop (CRITICAL)

## 🎯 Learning Objectives
- Understand the Call Stack
- Learn about Web APIs
- Master Microtask vs Macrotask queues
- Predict async code execution order

---

## 📚 JavaScript Runtime Architecture

```
╔═══════════════════════════════════════════════════════════════════════╗
║                        JAVASCRIPT RUNTIME                              ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  ┌─────────────────────────────────────────────────────────────────┐  ║
║  │                       CALL STACK                                 │  ║
║  │  (Executes JavaScript code synchronously, one at a time)        │  ║
║  └─────────────────────────────────────────────────────────────────┘  ║
║                           │                                            ║
║                           ▼                                            ║
║  ┌─────────────────────────────────────────────────────────────────┐  ║
║  │                       WEB APIs                                   │  ║
║  │  setTimeout, fetch, DOM events, etc.                            │  ║
║  │  (Handled by browser, not JavaScript engine)                    │  ║
║  └─────────────────────────────────────────────────────────────────┘  ║
║                           │                                            ║
║            ┌──────────────┴──────────────┐                            ║
║            ▼                              ▼                            ║
║  ┌─────────────────────┐    ┌─────────────────────┐                   ║
║  │   MICROTASK QUEUE   │    │   MACROTASK QUEUE   │                   ║
║  │  (High priority)    │    │  (Normal priority)  │                   ║
║  │                     │    │                     │                   ║
║  │  • Promise.then     │    │  • setTimeout       │                   ║
║  │  • queueMicrotask   │    │  • setInterval      │                   ║
║  │  • MutationObserver │    │  • setImmediate     │                   ║
║  │  • process.nextTick │    │  • I/O callbacks    │                   ║
║  │                     │    │  • UI rendering     │                   ║
║  └─────────────────────┘    └─────────────────────┘                   ║
║            │                              │                            ║
║            └──────────────┬───────────────┘                            ║
║                           │                                            ║
║                           ▼                                            ║
║  ┌─────────────────────────────────────────────────────────────────┐  ║
║  │                      EVENT LOOP                                  │  ║
║  │  (Continuously checks if call stack is empty, then processes    │  ║
║  │   ALL microtasks, then ONE macrotask, repeat)                   │  ║
║  └─────────────────────────────────────────────────────────────────┘  ║
║                                                                        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

---

## 📦 Call Stack

The **Call Stack** is a LIFO data structure that tracks function execution.

```javascript
function multiply(a, b) {
    return a * b;
}

function square(n) {
    return multiply(n, n);
}

function printSquare(n) {
    const result = square(n);
    console.log(result);
}

printSquare(4);

/*
CALL STACK EVOLUTION:
═══════════════════════════════════════════════════════════

Step 1:           Step 2:           Step 3:           Step 4:
                                    ┌─────────┐
                  ┌─────────┐       │multiply │       ┌─────────┐
┌─────────────┐   │ square  │       │ square  │       │ square  │
│printSquare  │   │printSqr │       │printSqr │       │printSqr │
└─────────────┘   └─────────┘       └─────────┘       └─────────┘

Step 5:           Step 6:           Step 7:
                  ┌─────────┐
┌─────────────┐   │ console │
│printSquare  │   │printSqr │       (empty)
└─────────────┘   └─────────┘

Output: 16
*/
```

---

## 🌐 Web APIs

Web APIs are browser-provided features that run outside the JavaScript engine.

```javascript
// setTimeout - Timer API
console.log("Start");

setTimeout(() => {
    console.log("Timeout callback");
}, 0);

console.log("End");

// Output: "Start", "End", "Timeout callback"

/*
WHY? Even with 0ms delay:
1. "Start" - executed immediately
2. setTimeout callback → sent to Web API
3. Web API starts timer (0ms)
4. "End" - executed immediately  
5. Timer completes → callback to Macrotask Queue
6. Call stack empty → Event Loop moves callback to stack
7. "Timeout callback" - executed
*/

// fetch - Network API
fetch('/api/data')
    .then(response => response.json())
    .then(data => console.log(data));

// DOM Events
document.addEventListener('click', () => {
    console.log('Clicked!');
});
```

---

## ⚡ Microtask vs Macrotask Queue

### Microtasks (High Priority)
- `Promise.then()`, `.catch()`, `.finally()`
- `queueMicrotask()`
- `MutationObserver`
- `process.nextTick()` (Node.js)

### Macrotasks (Normal Priority)
- `setTimeout()`, `setInterval()`
- `setImmediate()` (Node.js)
- I/O operations
- UI rendering
- `requestAnimationFrame()`

```javascript
console.log("1. Script start");

setTimeout(() => {
    console.log("2. setTimeout");
}, 0);

Promise.resolve()
    .then(() => console.log("3. Promise 1"))
    .then(() => console.log("4. Promise 2"));

queueMicrotask(() => {
    console.log("5. queueMicrotask");
});

console.log("6. Script end");

/*
OUTPUT:
1. Script start
6. Script end
3. Promise 1
5. queueMicrotask
4. Promise 2
2. setTimeout

EXPLANATION:
1. Synchronous code runs first (1, 6)
2. After sync code, ALL microtasks run (3, 5, 4)
3. Then ONE macrotask runs (2)
4. Repeat...
*/
```

---

## 🔄 Event Loop Algorithm

```
╔═══════════════════════════════════════════════════════════════════╗
║                    EVENT LOOP ALGORITHM                            ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                    ║
║   1. Execute all synchronous code in Call Stack                   ║
║                      │                                             ║
║                      ▼                                             ║
║   2. Is Call Stack empty?                                         ║
║          │       │                                                 ║
║         No      Yes                                                ║
║          │       │                                                 ║
║          │       ▼                                                 ║
║          │    3. Process ALL microtasks                           ║
║          │       (drain microtask queue completely)               ║
║          │       │                                                 ║
║          │       ▼                                                 ║
║          │    4. Microtask queue empty?                           ║
║          │           │       │                                     ║
║          │          No      Yes                                    ║
║          │           │       │                                     ║
║          │           ▼       ▼                                     ║
║          │    Go to step 3   5. Process ONE macrotask             ║
║          │                      (if any in queue)                  ║
║          │                      │                                  ║
║          │                      ▼                                  ║
║          └──────────────────────┼──────────────────────────────── ║
║                                 │                                  ║
║                      Go back to step 2                             ║
║                                                                    ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 🧪 Complex Examples

### Example 1: Mixed Async

```javascript
console.log("1");

setTimeout(() => console.log("2"), 0);

Promise.resolve()
    .then(() => {
        console.log("3");
        setTimeout(() => console.log("4"), 0);
    })
    .then(() => console.log("5"));

setTimeout(() => {
    console.log("6");
    Promise.resolve().then(() => console.log("7"));
}, 0);

console.log("8");

/*
OUTPUT: 1, 8, 3, 5, 2, 6, 7, 4

STEP BY STEP:
- Sync: 1, 8
- Microtasks: 3, 5
- Macrotask 1: 2 (setTimeout queued first)
- Macrotask 2: 6 → then microtask 7
- Macrotask 3: 4 (queued by promise callback)
*/
```

### Example 2: Promise in setTimeout

```javascript
setTimeout(() => {
    console.log("timeout 1");
    Promise.resolve().then(() => console.log("promise inside timeout"));
}, 0);

setTimeout(() => {
    console.log("timeout 2");
}, 0);

Promise.resolve().then(() => console.log("promise 1"));

console.log("sync");

/*
OUTPUT:
sync
promise 1
timeout 1
promise inside timeout
timeout 2

EXPLANATION:
1. sync (synchronous)
2. promise 1 (microtask after sync)
3. timeout 1 (first macrotask)
4. promise inside timeout (microtask after macrotask)
5. timeout 2 (next macrotask)
*/
```

### Example 3: Nested Microtasks

```javascript
Promise.resolve()
    .then(() => {
        console.log("1");
        return Promise.resolve()
            .then(() => console.log("2"))
            .then(() => console.log("3"));
    })
    .then(() => console.log("4"));

Promise.resolve()
    .then(() => console.log("5"))
    .then(() => console.log("6"));

/*
OUTPUT: 1, 5, 2, 6, 3, 4

EXPLANATION:
Microtask queue: [promise1.then, promise2.then]
- Execute promise1.then → logs 1, returns new promise
  Queue: [promise2.then, inner1.then]
- Execute promise2.then → logs 5
  Queue: [inner1.then, promise2.then2]
- Execute inner1.then → logs 2
  Queue: [promise2.then2, inner2.then]
- Execute promise2.then2 → logs 6
  Queue: [inner2.then, promise1.then2]
- Execute inner2.then → logs 3
  Queue: [promise1.then2]
- Execute promise1.then2 → logs 4
*/
```

---

## ⏱️ setTimeout vs Promise

```javascript
// Common interview question
console.log("start");

setTimeout(() => {
    console.log("setTimeout");
}, 0);

Promise.resolve().then(() => {
    console.log("promise");
});

console.log("end");

// OUTPUT: start, end, promise, setTimeout

// WHY? Promises (microtasks) have HIGHER priority than setTimeout (macrotasks)

// Even with a resolved promise that has delay simulation
new Promise(resolve => {
    console.log("promise executor"); // Runs synchronously!
    resolve();
}).then(() => {
    console.log("promise then");
});

setTimeout(() => console.log("setTimeout"), 0);

console.log("end");

// OUTPUT: promise executor, end, promise then, setTimeout
```

---

## 🎯 Interview Prediction Questions

```javascript
// Question 1
async function async1() {
    console.log("async1 start");
    await async2();
    console.log("async1 end");
}

async function async2() {
    console.log("async2");
}

console.log("script start");

setTimeout(() => {
    console.log("setTimeout");
}, 0);

async1();

new Promise(resolve => {
    console.log("promise1");
    resolve();
}).then(() => {
    console.log("promise2");
});

console.log("script end");

/*
OUTPUT:
script start
async1 start
async2
promise1
script end
async1 end
promise2
setTimeout

KEY INSIGHT: 
- await pauses the function and schedules rest as microtask
- Promise executor runs synchronously
*/

// Question 2
console.log("1");

setTimeout(() => console.log("2"), 0);

Promise.resolve()
    .then(() => {
        console.log("3");
        Promise.resolve().then(() => console.log("4"));
    })
    .then(() => console.log("5"));

Promise.resolve().then(() => console.log("6"));

console.log("7");

/*
OUTPUT: 1, 7, 3, 6, 4, 5, 2

Microtask queue processing:
1. After sync: [then->3, then->6]
2. Execute then->3, adds then->4, adds then->5 after
   Queue: [then->6, then->4, then->5]
3. Execute then->6
4. Execute then->4
5. Execute then->5
6. Then macrotask: 2
*/

// Question 3
const promise = new Promise((resolve, reject) => {
    console.log(1);
    setTimeout(() => {
        console.log("timerStart");
        resolve("success");
        console.log("timerEnd");
    }, 0);
    console.log(2);
});

promise.then(res => console.log(res));

console.log(4);

/*
OUTPUT: 1, 2, 4, timerStart, timerEnd, success

KEY: resolve() doesn't stop execution, just schedules .then()
*/
```

---

## 🔬 Practice Problems

```javascript
// Problem 1: Predict output
console.log('A');
setTimeout(() => console.log('B'), 0);
Promise.resolve().then(() => console.log('C'));
Promise.resolve().then(() => setTimeout(() => console.log('D'), 0));
Promise.resolve().then(() => console.log('E'));
setTimeout(() => console.log('F'), 0);
console.log('G');

// Answer: A, G, C, E, B, F, D

// Problem 2: Predict output
setTimeout(() => console.log(1), 0);

new Promise(resolve => {
    console.log(2);
    resolve();
    console.log(3);
}).then(() => console.log(4));

console.log(5);

// Answer: 2, 3, 5, 4, 1

// Problem 3: Implement a sleep function
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function demo() {
    console.log("Start");
    await sleep(2000);
    console.log("2 seconds later");
}

// Problem 4: Process array with delay between items
async function processWithDelay(items, delay) {
    for (const item of items) {
        console.log(item);
        await new Promise(r => setTimeout(r, delay));
    }
}

// Problem 5: Implement requestIdleCallback polyfill
const requestIdleCallback = 
    window.requestIdleCallback ||
    function(cb) {
        return setTimeout(() => {
            cb({
                didTimeout: false,
                timeRemaining: () => Math.max(0, 50)
            });
        }, 1);
    };
```

---

## 📋 Event Loop Cheat Sheet

```
╔═══════════════════════════════════════════════════════════════════╗
║                    EXECUTION ORDER                                 ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  1. SYNCHRONOUS CODE (Call Stack)                                 ║
║     - All regular statements                                       ║
║     - Promise executor (new Promise(executor))                     ║
║     - async function UNTIL first await                             ║
║                                                                    ║
║  2. MICROTASKS (All of them)                                      ║
║     - Promise.then(), .catch(), .finally()                        ║
║     - queueMicrotask()                                            ║
║     - await (code after await)                                    ║
║     - MutationObserver                                            ║
║                                                                    ║
║  3. ONE MACROTASK                                                  ║
║     - setTimeout, setInterval                                      ║
║     - I/O callbacks                                                ║
║     - requestAnimationFrame (before repaint)                      ║
║                                                                    ║
║  4. RENDER (if needed)                                            ║
║                                                                    ║
║  5. GO BACK TO STEP 2                                             ║
║                                                                    ║
╚═══════════════════════════════════════════════════════════════════╝

MEMORY AIDS:
- "Micro before Macro"
- "Promises are impatient" (higher priority)
- "Timeouts wait their turn"
```

---

## ✅ Day 11 Checklist

- [ ] Understand Call Stack operation
- [ ] Know what Web APIs are
- [ ] Distinguish microtasks from macrotasks
- [ ] Master Promise executor vs .then() timing
- [ ] Understand async/await in event loop
- [ ] Predict nested promise output
- [ ] Predict mixed setTimeout/Promise output
- [ ] Know queueMicrotask usage
- [ ] Understand new Promise executor runs sync
- [ ] Complete all prediction problems
