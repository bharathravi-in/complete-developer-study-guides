# Day 3: Data Types & Memory

## 🎯 Learning Objectives
- Understand Primitive vs Reference types
- Master Stack vs Heap memory allocation
- Deep dive into typeof operator
- Understand null vs undefined
- Learn Symbol and BigInt

---

## 📚 Primitive vs Reference Types

### Primitive Types (7 types)
Stored directly in **Stack** memory - immutable values.

```javascript
// 7 Primitive Types
const str = "Hello";           // String
const num = 42;                // Number
const bool = true;             // Boolean
const undef = undefined;       // Undefined
const nul = null;              // Null
const sym = Symbol("id");      // Symbol (ES6)
const bigInt = 9007199254740991n; // BigInt (ES2020)

// Primitives are IMMUTABLE
let name = "John";
name[0] = "K";      // Silently fails
console.log(name);  // "John" - unchanged

// When you "change" a primitive, you create a new value
let a = 10;
let b = a;      // b gets a COPY of the value
b = 20;
console.log(a); // 10 (unchanged)
console.log(b); // 20
```

### Reference Types
Stored in **Heap** memory - variable holds a reference/pointer.

```javascript
// Reference Types
const obj = { name: "John" };  // Object
const arr = [1, 2, 3];         // Array (special object)
const func = function() {};     // Function
const date = new Date();       // Date
const regex = /pattern/;       // RegExp
const map = new Map();         // Map
const set = new Set();         // Set

// References point to the SAME object
let person1 = { name: "John" };
let person2 = person1;  // person2 points to SAME object
person2.name = "Jane";
console.log(person1.name); // "Jane" - both changed!

// Arrays work the same way
let arr1 = [1, 2, 3];
let arr2 = arr1;
arr2.push(4);
console.log(arr1); // [1, 2, 3, 4] - both changed!
```

---

## 🗄️ Stack vs Heap Memory

```
╔═══════════════════════════════════════════════════════════════════╗
║                    MEMORY ARCHITECTURE                             ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                    ║
║   STACK (Fast, LIFO)              HEAP (Dynamic, Slower)          ║
║   ──────────────────              ──────────────────────          ║
║   │ Primitives       │            │                    │          ║
║   │ References       │───────────▶│  { name: "John" }  │          ║
║   │                  │            │  [1, 2, 3]         │          ║
║   │                  │            │  function() {}     │          ║
║   └──────────────────┘            └────────────────────┘          ║
║                                                                    ║
║   Characteristics:                Characteristics:                 ║
║   • Fixed size                    • Dynamic size                   ║
║   • Automatic cleanup             • Garbage collected              ║
║   • Fast access                   • Slower access                  ║
║   • LIFO order                    • No specific order              ║
║                                                                    ║
╚═══════════════════════════════════════════════════════════════════╝
```

### Memory Visualization

```javascript
// Example Code
let a = 10;
let b = "hello";
let c = { x: 1, y: 2 };
let d = c;
let e = [1, 2, 3];

/*
═══════════════════════════════════════════════════════════
MEMORY LAYOUT:
═══════════════════════════════════════════════════════════

STACK                              HEAP
┌─────────────────────┐           ┌─────────────────────────┐
│ a    │    10        │           │                         │
├──────┼──────────────┤           │  ┌─────────────────┐    │
│ b    │   "hello"    │           │  │ { x: 1, y: 2 } │◄───┼──┐
├──────┼──────────────┤           │  └─────────────────┘    │  │
│ c    │   0x001 ─────┼───────────┼─────────────────────────┼──┘
├──────┼──────────────┤           │                         │
│ d    │   0x001 ─────┼───────────┼─────────────────────────┼──┘
├──────┼──────────────┤           │                         │  (same ref)
│ e    │   0x002 ─────┼───────────┼──▶ ┌─────────────┐     │
└──────┴──────────────┘           │    │ [1, 2, 3]   │     │
                                  │    └─────────────┘     │
                                  └─────────────────────────┘
*/
```

### Pass by Value vs Pass by Reference

```javascript
// Primitives: Pass by VALUE (copy)
function modifyPrimitive(x) {
    x = 100;
    console.log("Inside:", x); // 100
}

let num = 50;
modifyPrimitive(num);
console.log("Outside:", num); // 50 (unchanged)

// Objects: Pass by REFERENCE (pointer copy)
function modifyObject(obj) {
    obj.name = "Modified";
    console.log("Inside:", obj); // { name: "Modified" }
}

let person = { name: "Original" };
modifyObject(person);
console.log("Outside:", person); // { name: "Modified" } (changed!)

// BUT reassigning doesn't affect original
function reassignObject(obj) {
    obj = { name: "New Object" };
    console.log("Inside:", obj); // { name: "New Object" }
}

let person2 = { name: "Original" };
reassignObject(person2);
console.log("Outside:", person2); // { name: "Original" } (unchanged)
// Why? Because we reassigned the LOCAL reference, not the original
```

---

## 🔍 typeof Operator

```javascript
// typeof returns a string indicating the type
console.log(typeof "hello");      // "string"
console.log(typeof 42);           // "number"
console.log(typeof 42n);          // "bigint"
console.log(typeof true);         // "boolean"
console.log(typeof undefined);    // "undefined"
console.log(typeof Symbol());     // "symbol"
console.log(typeof function(){}); // "function"
console.log(typeof {});           // "object"
console.log(typeof []);           // "object" (arrays are objects!)

// ⚠️ THE FAMOUS BUG
console.log(typeof null);         // "object" (historical bug!)

// Checking for null properly
let value = null;
console.log(value === null);      // true

// Checking for arrays
console.log(Array.isArray([]));   // true
console.log(Array.isArray({}));   // false

// typeof with undeclared variables
console.log(typeof nonExistent);  // "undefined" (no error!)

// typeof on classes
class MyClass {}
console.log(typeof MyClass);      // "function"

// More accurate type checking
function getType(value) {
    return Object.prototype.toString.call(value);
}

console.log(getType("hello"));    // "[object String]"
console.log(getType(42));         // "[object Number]"
console.log(getType(null));       // "[object Null]"
console.log(getType([]));         // "[object Array]"
console.log(getType({}));         // "[object Object]"
console.log(getType(new Date())); // "[object Date]"
console.log(getType(/regex/));    // "[object RegExp]"
```

---

## ❓ null vs undefined

```javascript
// undefined: "Nothing has been assigned"
let a;
console.log(a); // undefined

// null: "Intentionally empty"
let b = null;
console.log(b); // null

// Key differences
console.log(typeof undefined); // "undefined"
console.log(typeof null);      // "object" (bug)

console.log(undefined == null);  // true (loose equality)
console.log(undefined === null); // false (strict equality)

// Number conversion
console.log(Number(undefined)); // NaN
console.log(Number(null));      // 0

// Default parameters
function greet(name = "Guest") {
    console.log("Hello, " + name);
}
greet(undefined); // "Hello, Guest" (default applied)
greet(null);      // "Hello, null" (null is a value!)

// Where undefined appears naturally
let obj = {};
console.log(obj.nonExistent); // undefined

function noReturn() {}
console.log(noReturn());      // undefined

let arr = [1, , 3]; // sparse array
console.log(arr[1]); // undefined

// Where to use null
let element = document.getElementById("nonexistent");
console.log(element); // null (intentionally no element)

// Clearing references
let data = { heavy: "data" };
data = null; // Eligible for garbage collection

// Nullish coalescing (??)
let value1 = null ?? "default";     // "default"
let value2 = undefined ?? "default"; // "default"
let value3 = 0 ?? "default";        // 0 (only null/undefined)
let value4 = "" ?? "default";       // "" (only null/undefined)

// Optional chaining (?.)
let user = null;
console.log(user?.name);        // undefined (no error)
console.log(user?.getName?.());  // undefined (no error)
```

---

## 🔣 Symbol

**Symbol** is a primitive type for unique identifiers (ES6).

```javascript
// Creating Symbols
const sym1 = Symbol();
const sym2 = Symbol();
console.log(sym1 === sym2); // false (always unique!)

// Symbols with descriptions (for debugging)
const sym3 = Symbol("mySymbol");
console.log(sym3.description); // "mySymbol"

// Symbols are NOT converted to strings
const sym = Symbol("test");
// console.log("Symbol: " + sym); // TypeError!
console.log("Symbol: " + sym.toString()); // "Symbol: Symbol(test)"
console.log(`Symbol: ${sym.description}`); // "Symbol: test"

// Use Case 1: Unique object keys
const ID = Symbol("id");
const user = {
    name: "John",
    [ID]: 12345
};

console.log(user[ID]); // 12345
console.log(user.ID);  // undefined (not the same!)

// Symbols are NOT enumerable
console.log(Object.keys(user));              // ["name"]
console.log(Object.getOwnPropertyNames(user)); // ["name"]
console.log(Object.getOwnPropertySymbols(user)); // [Symbol(id)]

// Use Case 2: Prevent name collisions
const library1 = {
    [Symbol("version")]: "1.0.0"
};

const library2 = {
    [Symbol("version")]: "2.0.0"
};

// Both can be merged without collision
const merged = { ...library1, ...library2 };

// Use Case 3: Well-known Symbols
// Symbol.iterator - makes object iterable
const myIterable = {
    data: [1, 2, 3],
    [Symbol.iterator]() {
        let index = 0;
        return {
            next: () => ({
                value: this.data[index],
                done: index++ >= this.data.length
            })
        };
    }
};

for (const item of myIterable) {
    console.log(item); // 1, 2, 3
}

// Symbol.for() - Global symbol registry
const globalSym1 = Symbol.for("shared");
const globalSym2 = Symbol.for("shared");
console.log(globalSym1 === globalSym2); // true (same symbol!)

// Symbol.keyFor() - Get key from global registry
console.log(Symbol.keyFor(globalSym1)); // "shared"
console.log(Symbol.keyFor(Symbol("local"))); // undefined
```

---

## 📏 BigInt

**BigInt** handles integers larger than Number.MAX_SAFE_INTEGER (ES2020).

```javascript
// Number limitations
console.log(Number.MAX_SAFE_INTEGER); // 9007199254740991
console.log(9007199254740991 + 1);    // 9007199254740992
console.log(9007199254740991 + 2);    // 9007199254740992 (WRONG!)

// Creating BigInt
const big1 = 9007199254740991n;       // Literal with 'n' suffix
const big2 = BigInt(9007199254740991); // Constructor
const big3 = BigInt("9007199254740991"); // From string

// BigInt operations
console.log(big1 + 1n); // 9007199254740992n
console.log(big1 + 2n); // 9007199254740993n (CORRECT!)

// ⚠️ Cannot mix BigInt and Number
// console.log(big1 + 1); // TypeError!
console.log(big1 + BigInt(1)); // OK
console.log(Number(big1) + 1); // OK (but might lose precision)

// BigInt comparisons
console.log(10n > 5n);   // true
console.log(10n > 5);    // true (comparison works!)
console.log(10n === 10); // false (different types)
console.log(10n == 10);  // true (loose equality)

// BigInt division (truncates)
console.log(5n / 2n);    // 2n (not 2.5n)

// BigInt in conditionals
console.log(0n ? "truthy" : "falsy"); // "falsy"
console.log(1n ? "truthy" : "falsy"); // "truthy"

// BigInt methods
console.log(BigInt.asIntN(4, 8n));  // -8n (signed)
console.log(BigInt.asUintN(4, 8n)); // 8n (unsigned)

// Use cases for BigInt
// 1. Cryptography
// 2. High-precision timestamps
// 3. Large IDs (snowflake IDs)
// 4. Scientific calculations

// JSON doesn't support BigInt
const data = { id: 123n };
// JSON.stringify(data); // TypeError!

// Workaround
const json = JSON.stringify(data, (key, value) =>
    typeof value === 'bigint' ? value.toString() : value
);
console.log(json); // {"id":"123"}
```

---

## 📋 Shallow Copy vs Deep Copy

### Shallow Copy
Copies only the first level; nested objects share references.

```javascript
// Shallow copy methods
const original = { 
    name: "John", 
    address: { city: "NYC" } 
};

// Method 1: Spread operator
const copy1 = { ...original };

// Method 2: Object.assign
const copy2 = Object.assign({}, original);

// Method 3: Array.from (for arrays)
const arrOriginal = [1, [2, 3]];
const arrCopy = [...arrOriginal];

// Shallow copy issue
copy1.name = "Jane";        // OK - doesn't affect original
copy1.address.city = "LA";  // PROBLEM - affects original!

console.log(original.name);         // "John" (unchanged)
console.log(original.address.city); // "LA" (changed!)

/*
Visual:
═══════════════════════════════════════════════════════════

original               copy1
┌──────────────┐       ┌──────────────┐
│ name: "John" │       │ name: "Jane" │
│ address: ────┼───┐   │ address: ────┼───┐
└──────────────┘   │   └──────────────┘   │
                   │                       │
                   └───────────┬───────────┘
                               │
                               ▼
                    ┌─────────────────┐
                    │ { city: "LA" }  │  ← Shared!
                    └─────────────────┘
*/
```

### Deep Copy

Copies all levels; completely independent objects.

```javascript
// Method 1: JSON (limited - loses functions, dates, etc.)
const original = {
    name: "John",
    address: { city: "NYC" },
    date: new Date(),
    func: () => "hello",
    undef: undefined
};

const jsonCopy = JSON.parse(JSON.stringify(original));
console.log(jsonCopy);
// {
//   name: "John",
//   address: { city: "NYC" },
//   date: "2026-02-28T..." // String, not Date!
//   // func is missing!
//   // undef is missing!
// }

// Method 2: structuredClone (modern, recommended)
const original2 = {
    name: "John",
    address: { city: "NYC" },
    date: new Date(),
    arr: [1, 2, [3, 4]],
    map: new Map([["key", "value"]])
};

const deepCopy = structuredClone(original2);
deepCopy.address.city = "LA";
console.log(original2.address.city); // "NYC" (unchanged!)

// structuredClone limitations
const withFunc = {
    fn: () => "hello",  // Functions not supported
    el: document.body   // DOM nodes not supported
};
// structuredClone(withFunc); // Error!

// Method 3: Custom recursive function
function deepClone(obj, hash = new WeakMap()) {
    // Handle primitives
    if (obj === null || typeof obj !== 'object') return obj;
    
    // Handle circular references
    if (hash.has(obj)) return hash.get(obj);
    
    // Handle Date
    if (obj instanceof Date) return new Date(obj);
    
    // Handle Array
    if (Array.isArray(obj)) {
        const arrCopy = [];
        hash.set(obj, arrCopy);
        obj.forEach((item, index) => {
            arrCopy[index] = deepClone(item, hash);
        });
        return arrCopy;
    }
    
    // Handle Object
    const copy = {};
    hash.set(obj, copy);
    Object.keys(obj).forEach(key => {
        copy[key] = deepClone(obj[key], hash);
    });
    return copy;
}

// Method 4: Using lodash
// import _ from 'lodash';
// const deepCopy = _.cloneDeep(original);

// Comparison of methods
/*
═══════════════════════════════════════════════════════════
METHOD              │ FUNCTIONS │ DATE │ CIRCULAR │ SPEED
─────────────────────────────────────────────────────────
JSON.parse/stringify │    ❌     │  ❌  │    ❌    │ Fast
structuredClone     │    ❌     │  ✅  │    ✅    │ Fast
Custom recursive    │    ✅*    │  ✅  │    ✅    │ Medium
lodash.cloneDeep    │    ✅*    │  ✅  │    ✅    │ Medium
*/
```

---

## 💡 Memory Reference Examples

```javascript
// Example 1: Primitive immutability
let str = "hello";
let str2 = str;
str = "world";
console.log(str2); // "hello" (copied value)

// Example 2: Object mutation
let arr = [1, 2, 3];
let arr2 = arr;
arr.push(4);
console.log(arr2); // [1, 2, 3, 4] (same reference)

// Example 3: Breaking the reference
let obj = { a: 1 };
let obj2 = obj;
obj = { b: 2 }; // obj now points to new object
console.log(obj2); // { a: 1 } (still points to original)

// Example 4: Function parameter mutation
function addItem(array) {
    array.push("new");
    return array;
}

const myArr = ["old"];
const result = addItem(myArr);
console.log(myArr);   // ["old", "new"] (mutated!)
console.log(result);  // ["old", "new"]
console.log(myArr === result); // true (same reference)

// Example 5: Avoiding mutation
function addItemPure(array) {
    return [...array, "new"]; // Returns new array
}

const myArr2 = ["old"];
const result2 = addItemPure(myArr2);
console.log(myArr2);  // ["old"] (unchanged)
console.log(result2); // ["old", "new"]
console.log(myArr2 === result2); // false (different arrays)
```

---

## 🔬 Practice Problems

```javascript
// Problem 1: What's the output?
let a = { value: 10 };
let b = a;
let c = { value: 10 };

console.log(a === b);  // ?
console.log(a === c);  // ?
// Answer: true, false (same reference vs different objects)

// Problem 2: What's the output?
function modify(obj, num) {
    obj.x = 10;
    num = 10;
}
let myObj = { x: 1 };
let myNum = 1;
modify(myObj, myNum);
console.log(myObj.x, myNum); // ?
// Answer: 10, 1

// Problem 3: What's the output?
const arr1 = [1, 2, { a: 3 }];
const arr2 = [...arr1];
arr2[0] = 100;
arr2[2].a = 300;
console.log(arr1[0], arr1[2].a); // ?
// Answer: 1, 300

// Problem 4: What's the output?
console.log(typeof typeof 1); // ?
// Answer: "string" (typeof 1 is "number", typeof "number" is "string")

// Problem 5: What's the output?
console.log(null == undefined);  // ?
console.log(null === undefined); // ?
// Answer: true, false

// Problem 6: Create a deep copy
const nested = {
    level1: {
        level2: {
            value: "deep"
        }
    }
};
const deepCopy = structuredClone(nested);
deepCopy.level1.level2.value = "modified";
console.log(nested.level1.level2.value); // ?
// Answer: "deep" (unchanged)
```

---

## ✅ Day 3 Checklist

- [ ] Understand 7 primitive types
- [ ] Understand reference types
- [ ] Master Stack vs Heap memory model
- [ ] Know all typeof operator results (including the null bug)
- [ ] Differentiate null vs undefined
- [ ] Understand Symbol and its use cases
- [ ] Learn BigInt for large numbers
- [ ] Master shallow copy vs deep copy techniques
- [ ] Know structuredClone for deep copying
- [ ] Complete all practice problems
