# Day 19: Memory Management & Garbage Collection

## 🎯 Learning Objectives
- Understand JavaScript memory model
- Learn garbage collection algorithms
- Identify memory leaks
- Master WeakMap and WeakSet
- Profile memory with DevTools

---

## 🧠 Memory Lifecycle

```javascript
/*
╔════════════════════════════════════════════════════════════════════╗
║                     MEMORY LIFECYCLE                                ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║   1. ALLOCATE ───────► 2. USE ───────► 3. RELEASE                  ║
║                                                                     ║
║   • Variable declaration   • Read/Write      • Garbage Collection   ║
║   • Object creation        • Function calls  • Automatic            ║
║   • Function definition    • Calculations    • When unreachable     ║
║                                                                     ║
╚════════════════════════════════════════════════════════════════════╝

MEMORY STRUCTURE:

┌─────────────────────────────────────────────────────────────────┐
│                          STACK                                   │
│  • Primitives (stored by value)                                  │
│  • References (pointers to heap)                                 │
│  • Function call frames                                          │
│  • Fixed size, fast access                                       │
│  • LIFO (Last In, First Out)                                     │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          HEAP                                    │
│  • Objects                                                       │
│  • Arrays                                                        │
│  • Functions                                                     │
│  • Dynamic size, slower access                                   │
│  • Managed by Garbage Collector                                  │
└─────────────────────────────────────────────────────────────────┘
*/

// Stack allocation (primitives)
let a = 10;        // Stored directly on stack
let b = "hello";   // Stored on stack
let c = true;      // Stored on stack

// Heap allocation (objects)
let obj = { x: 1 }; // Reference on stack, object on heap
let arr = [1, 2, 3]; // Reference on stack, array on heap
let fn = () => {};   // Reference on stack, function on heap

/*
STACK           HEAP
┌─────────┐    ┌─────────────────────┐
│ a: 10   │    │  obj: { x: 1 }      │
│ b:hello │    │  arr: [1, 2, 3]     │
│ c: true │    │  fn: () => {}       │
│ obj: ───│───►│                     │
│ arr: ───│───►│                     │
│ fn:  ───│───►│                     │
└─────────┘    └─────────────────────┘
*/
```

---

## ♻️ Garbage Collection

### Mark and Sweep Algorithm

```javascript
/*
MARK AND SWEEP (Primary GC Algorithm):

1. START from "roots" (global, local variables, etc.)
2. MARK all reachable objects
3. SWEEP (delete) unmarked objects

ROOTS:
• Global object (window/global)
• Currently executing function's local variables
• Variables in the call stack
• Closures

EXAMPLE:
*/

let user = { name: 'John' };  // ✓ Reachable from root

user = null;  // Object becomes unreachable
              // GC will collect { name: 'John' }

/*
BEFORE:
  root (user) ──► { name: 'John' }

AFTER user = null:
  root (user) ──► null
                  { name: 'John' }  ← Unreachable, will be collected
*/

// Circular references are handled correctly
function circularExample() {
    let objA = {};
    let objB = {};
    
    objA.ref = objB;
    objB.ref = objA;
    
    // Both objects reference each other
    // But when function ends, no root references them
    // GC can collect both
}

circularExample();
// objA and objB are collected despite circular refs
```

### Generational Garbage Collection

```javascript
/*
V8 ENGINE GC STRATEGY:

YOUNG GENERATION (Nursery):
┌─────────────────────────────────────────────┐
│  Most objects die young                      │
│  Small, fast collection (Minor GC)           │
│  Uses Scavenge algorithm                     │
│  Objects that survive move to Old Gen        │
└─────────────────────────────────────────────┘

OLD GENERATION:
┌─────────────────────────────────────────────┐
│  Long-lived objects                          │
│  Less frequent collection (Major GC)         │
│  Uses Mark-Sweep & Mark-Compact              │
│  More expensive, but runs less often         │
└─────────────────────────────────────────────┘

GC TRIGGERS:
• Memory allocation when near limit
• Idle time (opportunistic)
• Explicit gc() call (Node with --expose-gc)
*/

// Force GC in Node.js (for testing only!)
// node --expose-gc script.js
if (global.gc) {
    global.gc();
}
```

---

## 🔒 Memory Leaks

### Common Leak Patterns

```javascript
// 1. ACCIDENTAL GLOBALS
function leakyFunction() {
    leakedVariable = 'oops';  // Missing var/let/const
    this.alsoLeaked = 'oops'; // 'this' is global in non-strict mode
}
// Fix: Use 'use strict' and always declare variables

// 2. FORGOTTEN TIMERS
let data = fetchHugeData();

setInterval(() => {
    // This closure holds data reference forever
    process(data);
}, 1000);

// Fix: Clear intervals when done
const intervalId = setInterval(process, 1000);
// Later:
clearInterval(intervalId);

// 3. EVENT LISTENERS
class Component {
    constructor() {
        this.data = new Array(10000).fill('x');
        this.handleClick = this.handleClick.bind(this);
        window.addEventListener('click', this.handleClick);
    }
    
    handleClick() {
        console.log('clicked');
    }
    
    // Missing: remove listener on destroy
    destroy() {
        window.removeEventListener('click', this.handleClick);
    }
}

// 4. CLOSURES HOLDING LARGE DATA
function createLeak() {
    const hugeArray = new Array(1000000).fill('x');
    
    return function() {
        // Even if we don't use hugeArray,
        // some engines keep the entire closure scope
        return 'small value';
    };
}

const leak = createLeak(); // hugeArray cannot be GC'd

// Fix: Set to null when done
function createNoLeak() {
    let hugeArray = new Array(1000000).fill('x');
    const small = hugeArray.length; // Extract what we need
    hugeArray = null; // Allow GC
    
    return function() {
        return small;
    };
}

// 5. DOM REFERENCES
let elements = {
    button: document.getElementById('button'),
    image: document.getElementById('image'),
    text: document.getElementById('text')
};

function removeButton() {
    document.body.removeChild(document.getElementById('button'));
    // elements.button still holds reference!
    // The button node can't be GC'd
}

// Fix: Clean up references
function removeButtonFixed() {
    const button = elements.button;
    document.body.removeChild(button);
    elements.button = null;
}

// 6. DETACHED DOM TREES
function createTree() {
    const root = document.createElement('div');
    
    for (let i = 0; i < 1000; i++) {
        const child = document.createElement('div');
        root.appendChild(child);
    }
    
    // Never attached to document, but we keep the reference
    return root;
}

let tree = createTree();
// tree holds 1000+ DOM nodes that aren't displayed

// Fix: Set to null when done
tree = null;

// 7. MAP/SET WITH OBJECT KEYS
const cache = new Map();

function processObject(obj) {
    if (!cache.has(obj)) {
        const result = expensiveOperation(obj);
        cache.set(obj, result);
    }
    return cache.get(obj);
}

// Objects stay in cache forever!
// Even after original reference is gone
```

---

## 🗝️ WeakMap and WeakSet

Weak references allow objects to be garbage collected.

```javascript
/*
REGULAR MAP vs WEAKMAP:

Map:                              WeakMap:
• Keys can be any value           • Keys must be objects
• Strong reference to keys        • Weak reference to keys
• Keys prevent GC                 • Keys can be GC'd
• Iterable                        • NOT iterable
• Has .size property              • No .size property
*/

// WeakMap example
const wm = new WeakMap();
let obj = { name: 'John' };

wm.set(obj, 'some data');
console.log(wm.get(obj)); // 'some data'

obj = null; // Object can be garbage collected
            // WeakMap entry is automatically removed

// Practical use: Private data
const privateData = new WeakMap();

class Person {
    constructor(name, secret) {
        this.name = name;
        privateData.set(this, { secret });
    }
    
    getSecret() {
        return privateData.get(this).secret;
    }
}

const person = new Person('John', 'likes cats');
console.log(person.name);        // 'John'
console.log(person.secret);      // undefined (private!)
console.log(person.getSecret()); // 'likes cats'

// When person is GC'd, the private data is too

// Practical use: DOM metadata
const nodeData = new WeakMap();

function setNodeData(node, data) {
    nodeData.set(node, data);
}

function getNodeData(node) {
    return nodeData.get(node);
}

const div = document.createElement('div');
setNodeData(div, { clicks: 0 });

// When div is removed from DOM and garbage collected,
// the metadata is automatically cleaned up

// WeakSet example
const ws = new WeakSet();
let obj1 = { id: 1 };
let obj2 = { id: 2 };

ws.add(obj1);
ws.add(obj2);

console.log(ws.has(obj1)); // true

obj1 = null;
// obj1 can be GC'd, and removed from WeakSet

// Practical use: Tracking visited objects
const visited = new WeakSet();

function deepClone(obj) {
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }
    
    // Prevent infinite loops with circular references
    if (visited.has(obj)) {
        return obj; // Already visited
    }
    visited.add(obj);
    
    const clone = Array.isArray(obj) ? [] : {};
    
    for (const key in obj) {
        clone[key] = deepClone(obj[key]);
    }
    
    return clone;
}

// WeakRef (ES2021)
let target = { data: 'important' };
const ref = new WeakRef(target);

// Later, to access:
const deref = ref.deref();
if (deref) {
    console.log(deref.data);
} else {
    console.log('Object has been garbage collected');
}

// FinalizationRegistry (ES2021) - cleanup callbacks
const registry = new FinalizationRegistry((heldValue) => {
    console.log(`Cleanup for: ${heldValue}`);
});

let obj3 = { name: 'test' };
registry.register(obj3, 'test object');

obj3 = null;
// Eventually logs: "Cleanup for: test object"
```

---

## 📊 Memory Profiling

### Console Methods

```javascript
// Memory usage in Node.js
function logMemory() {
    const used = process.memoryUsage();
    console.log({
        rss: `${Math.round(used.rss / 1024 / 1024)} MB`,
        heapTotal: `${Math.round(used.heapTotal / 1024 / 1024)} MB`,
        heapUsed: `${Math.round(used.heapUsed / 1024 / 1024)} MB`,
        external: `${Math.round(used.external / 1024 / 1024)} MB`,
        arrayBuffers: `${Math.round(used.arrayBuffers / 1024 / 1024)} MB`
    });
}

/*
rss: Resident Set Size - total memory allocated
heapTotal: Total heap size
heapUsed: Actual memory used
external: Memory used by C++ objects bound to JS
arrayBuffers: Memory for ArrayBuffers
*/

// Browser performance.memory (Chrome only)
if (performance.memory) {
    console.log({
        usedJSHeapSize: performance.memory.usedJSHeapSize,
        totalJSHeapSize: performance.memory.totalJSHeapSize,
        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
    });
}
```

### Chrome DevTools Memory Panel

```javascript
/*
HEAP SNAPSHOT:

1. Open DevTools → Memory tab
2. Select "Heap snapshot"
3. Click "Take snapshot"

ANALYZING SNAPSHOT:
• Summary: Objects grouped by constructor
• Comparison: Diff between snapshots
• Containment: Object hierarchy
• Statistics: Memory composition

WHAT TO LOOK FOR:
• Objects with high "Retained Size"
• Growing array of objects
• Detached DOM trees
• Multiple instances that should be singletons

ALLOCATION TIMELINE:

1. Select "Allocation instrumentation on timeline"
2. Click Record
3. Perform operations
4. Stop recording

• Blue bars = memory still allocated
• Gray bars = memory that was freed
• Look for accumulating blue bars

ALLOCATION SAMPLING:

1. Select "Allocation sampling"
2. Lower overhead than timeline
3. Good for production profiling
*/
```

---

## 🛠️ Memory Optimization

```javascript
// 1. Object pooling - reuse objects instead of creating new ones
class ObjectPool {
    constructor(createFn, size = 10) {
        this.createFn = createFn;
        this.pool = [];
        
        for (let i = 0; i < size; i++) {
            this.pool.push(createFn());
        }
    }
    
    acquire() {
        return this.pool.pop() || this.createFn();
    }
    
    release(obj) {
        // Reset object state
        obj.reset?.();
        this.pool.push(obj);
    }
}

class Particle {
    constructor() {
        this.x = 0;
        this.y = 0;
        this.vx = 0;
        this.vy = 0;
    }
    
    reset() {
        this.x = this.y = this.vx = this.vy = 0;
    }
}

const particlePool = new ObjectPool(() => new Particle(), 100);

// Instead of new Particle():
const particle = particlePool.acquire();
// When done:
particlePool.release(particle);

// 2. Avoid creating objects in loops
// ❌ Bad
function processItems(items) {
    return items.map(item => ({
        id: item.id,
        processed: true
    }));
}

// ✅ Better (reuse object shape)
const resultTemplate = { id: 0, processed: true };
function processItemsOptimized(items) {
    const results = new Array(items.length);
    for (let i = 0; i < items.length; i++) {
        results[i] = { ...resultTemplate, id: items[i].id };
    }
    return results;
}

// 3. Use TypedArrays for numeric data
// ❌ Regular array
const regularArray = new Array(1000000).fill(0);

// ✅ TypedArray (much more memory efficient)
const typedArray = new Uint32Array(1000000);

// 4. Stream large data instead of loading all at once
// ❌ Load all
const allData = await fetchAllData(); // May be GBs

// ✅ Stream
async function* streamData() {
    let page = 1;
    while (true) {
        const chunk = await fetchPage(page++);
        if (!chunk.length) break;
        yield* chunk;
    }
}

for await (const item of streamData()) {
    process(item);
}

// 5. Clean up subscriptions and listeners
class SafeComponent {
    constructor() {
        this.subscriptions = [];
        this.abortController = new AbortController();
    }
    
    subscribe(emitter, event, handler) {
        emitter.on(event, handler);
        this.subscriptions.push(() => emitter.off(event, handler));
    }
    
    addDOMListener(element, event, handler) {
        element.addEventListener(event, handler, {
            signal: this.abortController.signal
        });
    }
    
    destroy() {
        // Clean up all subscriptions
        this.subscriptions.forEach(unsub => unsub());
        this.subscriptions = [];
        
        // Clean up all DOM listeners
        this.abortController.abort();
    }
}
```

---

## ✅ Day 19 Checklist

- [ ] Understand stack vs heap memory
- [ ] Know garbage collection basics
- [ ] Understand mark and sweep algorithm
- [ ] Identify common memory leak patterns
- [ ] Use WeakMap for object metadata
- [ ] Use WeakSet for object tracking
- [ ] Know WeakRef and FinalizationRegistry
- [ ] Profile memory with DevTools
- [ ] Apply memory optimization techniques
- [ ] Implement object pooling
- [ ] Use TypedArrays for numeric data
- [ ] Clean up subscriptions properly
