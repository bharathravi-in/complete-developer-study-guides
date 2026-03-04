# Day 9: Objects Deep Dive

## 🎯 Learning Objectives
- Master Object.create for prototype patterns
- Understand Object.freeze, seal, preventExtensions
- Learn Object.defineProperty and descriptors
- Deep vs Shallow cloning strategies

---

## 📚 Object.create()

Creates a new object with the specified prototype.

```javascript
// Basic Object.create
const personProto = {
    greet() {
        return `Hello, I'm ${this.name}`;
    },
    introduce() {
        return `${this.name}, ${this.age} years old`;
    }
};

const john = Object.create(personProto);
john.name = "John";
john.age = 30;

console.log(john.greet());      // "Hello, I'm John"
console.log(john.introduce());  // "John, 30 years old"

// Object.create with property descriptors
const jane = Object.create(personProto, {
    name: {
        value: "Jane",
        writable: true,
        enumerable: true,
        configurable: true
    },
    age: {
        value: 25,
        writable: false,  // Cannot be changed
        enumerable: true,
        configurable: false
    }
});

jane.age = 30; // Silently fails (strict mode: throws)
console.log(jane.age); // 25

// Object.create(null) - Pure dictionary
const dict = Object.create(null);
dict.key = "value";

console.log(dict.toString);        // undefined (no prototype!)
console.log("key" in dict);        // true
console.log("toString" in dict);   // false

// Useful for maps without prototype pollution
dict["__proto__"] = "safe"; // Won't affect prototype chain
console.log(dict["__proto__"]); // "safe"

// Compare with regular object
const regular = {};
regular["__proto__"] = { bad: true };
console.log(regular.bad); // true (prototype modified!)
```

---

## ❄️ Object.freeze()

Makes an object completely immutable (shallow).

```javascript
const config = {
    api: "https://api.example.com",
    timeout: 5000,
    features: {
        darkMode: true,
        notifications: false
    }
};

Object.freeze(config);

// Cannot modify
config.api = "https://other.com";
console.log(config.api); // "https://api.example.com" (unchanged)

// Cannot add
config.newProp = "value";
console.log(config.newProp); // undefined

// Cannot delete
delete config.timeout;
console.log(config.timeout); // 5000 (still exists)

// BUT nested objects are NOT frozen!
config.features.darkMode = false;
console.log(config.features.darkMode); // false (changed!)

// Deep freeze implementation
function deepFreeze(obj) {
    // Get all property names
    const propNames = Object.getOwnPropertyNames(obj);
    
    // Freeze nested objects first
    propNames.forEach(name => {
        const value = obj[name];
        if (value && typeof value === "object") {
            deepFreeze(value);
        }
    });
    
    return Object.freeze(obj);
}

const deepConfig = deepFreeze({
    api: "url",
    settings: { nested: true }
});

deepConfig.settings.nested = false;
console.log(deepConfig.settings.nested); // true (unchanged!)

// Check if frozen
console.log(Object.isFrozen(config)); // true
```

---

## 🔒 Object.seal() and Object.preventExtensions()

```javascript
// Object.seal - Can modify, but no add/delete
const user = { name: "John", age: 30 };
Object.seal(user);

user.name = "Jane";        // OK - can modify
console.log(user.name);    // "Jane"

user.email = "a@b.com";    // Fails - can't add
console.log(user.email);   // undefined

delete user.age;           // Fails - can't delete
console.log(user.age);     // 30

console.log(Object.isSealed(user)); // true

// Object.preventExtensions - No new properties, but can modify/delete
const product = { name: "Widget", price: 100 };
Object.preventExtensions(product);

product.price = 150;       // OK - can modify
console.log(product.price); // 150

delete product.price;      // OK - can delete
console.log(product.price); // undefined

product.stock = 50;        // Fails - can't add
console.log(product.stock); // undefined

console.log(Object.isExtensible(product)); // false

/*
═══════════════════════════════════════════════════════════
COMPARISON:
═══════════════════════════════════════════════════════════

Action              │ preventExtensions │  seal  │ freeze
────────────────────────────────────────────────────────────
Add properties      │       ❌          │   ❌   │   ❌
Delete properties   │       ✅          │   ❌   │   ❌
Modify values       │       ✅          │   ✅   │   ❌
Reconfigure props   │       ✅          │   ❌   │   ❌
*/
```

---

## 🔧 Object.defineProperty()

Fine-grained control over property behavior.

```javascript
const person = {};

// Define a property with full control
Object.defineProperty(person, "name", {
    value: "John",
    writable: true,      // Can change value
    enumerable: true,    // Shows in for...in
    configurable: true   // Can delete or reconfigure
});

// Getters and Setters
Object.defineProperty(person, "fullName", {
    get() {
        return `${this.firstName} ${this.lastName}`;
    },
    set(value) {
        const parts = value.split(" ");
        this.firstName = parts[0];
        this.lastName = parts[1];
    },
    enumerable: true,
    configurable: true
});

person.firstName = "John";
person.lastName = "Doe";
console.log(person.fullName);  // "John Doe"

person.fullName = "Jane Smith";
console.log(person.firstName); // "Jane"

// Non-enumerable property (hidden from for...in)
Object.defineProperty(person, "_secret", {
    value: "hidden",
    enumerable: false
});

for (let key in person) {
    console.log(key); // firstName, lastName, name, fullName (not _secret)
}

console.log(person._secret); // "hidden" (direct access works)

// Non-writable property (read-only)
Object.defineProperty(person, "id", {
    value: 12345,
    writable: false
});

person.id = 99999;
console.log(person.id); // 12345 (unchanged)

// Non-configurable (can't delete or reconfigure)
Object.defineProperty(person, "permanent", {
    value: "forever",
    configurable: false
});

delete person.permanent; // Fails
// Object.defineProperty(person, "permanent", { value: "changed" }); // TypeError
```

---

## 📋 Property Descriptors

```javascript
const obj = {
    name: "Test",
    get value() { return this._value; },
    set value(v) { this._value = v; }
};

// Get descriptor
const nameDesc = Object.getOwnPropertyDescriptor(obj, "name");
console.log(nameDesc);
/*
{
    value: "Test",
    writable: true,
    enumerable: true,
    configurable: true
}
*/

const valueDesc = Object.getOwnPropertyDescriptor(obj, "value");
console.log(valueDesc);
/*
{
    get: [Function: get value],
    set: [Function: set value],
    enumerable: true,
    configurable: true
}
*/

// Get all descriptors
const allDescs = Object.getOwnPropertyDescriptors(obj);
console.log(allDescs);

// Copy object with descriptors (preserves getters/setters)
const copy = Object.defineProperties({}, 
    Object.getOwnPropertyDescriptors(obj)
);

// Regular spread/assign doesn't preserve getters
const badCopy = { ...obj };
console.log(Object.getOwnPropertyDescriptor(badCopy, "value"));
// { value: undefined, ... } - getter was invoked, not copied!
```

---

## 📦 Shallow vs Deep Clone

### Shallow Copy Methods

```javascript
const original = {
    name: "John",
    scores: [90, 85, 88],
    address: {
        city: "NYC",
        zip: "10001"
    }
};

// Method 1: Spread operator
const spread = { ...original };

// Method 2: Object.assign
const assigned = Object.assign({}, original);

// Method 3: Object.fromEntries + Object.entries
const entries = Object.fromEntries(Object.entries(original));

// ALL are shallow - nested objects are shared
spread.scores.push(95);
console.log(original.scores); // [90, 85, 88, 95] - Modified!
```

### Deep Clone Methods

```javascript
// Method 1: structuredClone (Modern, recommended)
const original = {
    name: "John",
    date: new Date(),
    data: { nested: { deep: "value" } },
    map: new Map([["key", "value"]]),
    set: new Set([1, 2, 3])
};

const deepCopy = structuredClone(original);
deepCopy.data.nested.deep = "changed";
console.log(original.data.nested.deep); // "value" (unchanged!)

// structuredClone limitations:
// ❌ Cannot clone functions
// ❌ Cannot clone DOM nodes
// ❌ Cannot clone Error objects
// ✅ Handles circular references

// Method 2: JSON (limited)
const jsonCopy = JSON.parse(JSON.stringify(original));
// ❌ Loses: Date (becomes string), Map, Set, functions, undefined

// Method 3: Custom recursive function
function deepClone(obj, hash = new WeakMap()) {
    if (obj === null || typeof obj !== "object") return obj;
    if (obj instanceof Date) return new Date(obj);
    if (obj instanceof RegExp) return new RegExp(obj);
    if (hash.has(obj)) return hash.get(obj); // Circular ref
    
    const clone = Array.isArray(obj) ? [] : {};
    hash.set(obj, clone);
    
    for (let key of Reflect.ownKeys(obj)) {
        clone[key] = deepClone(obj[key], hash);
    }
    
    return clone;
}

// Method 4: lodash cloneDeep (if using lodash)
// const deepCopy = _.cloneDeep(original);
```

---

## 🔍 Object Methods Reference

```javascript
const obj = { a: 1, b: 2, c: 3 };

// Keys, values, entries
console.log(Object.keys(obj));    // ["a", "b", "c"]
console.log(Object.values(obj));  // [1, 2, 3]
console.log(Object.entries(obj)); // [["a", 1], ["b", 2], ["c", 3]]

// From entries back to object
const pairs = [["x", 10], ["y", 20]];
console.log(Object.fromEntries(pairs)); // { x: 10, y: 20 }

// Transform object
const doubled = Object.fromEntries(
    Object.entries(obj).map(([k, v]) => [k, v * 2])
);
console.log(doubled); // { a: 2, b: 4, c: 6 }

// Check properties
console.log(obj.hasOwnProperty("a"));   // true
console.log(Object.hasOwn(obj, "a"));   // true (ES2022, safer)
console.log("a" in obj);                // true (includes prototype)

// Object comparison
console.log(Object.is(NaN, NaN));       // true
console.log(Object.is(+0, -0));         // false

// Merge objects
const merged = Object.assign({}, obj, { d: 4 });
// Or: const merged = { ...obj, d: 4 };

// Prototype methods
console.log(Object.getPrototypeOf(obj)); // Object.prototype
Object.setPrototypeOf(obj, null);        // Remove prototype (careful!)
```

---

## 🔬 Practice Problems

```javascript
// Problem 1: Implement Object.assign
function myAssign(target, ...sources) {
    sources.forEach(source => {
        if (source != null) {
            for (let key of Object.keys(source)) {
                target[key] = source[key];
            }
        }
    });
    return target;
}

// Problem 2: Deep freeze implementation
function deepFreeze(obj) {
    Object.getOwnPropertyNames(obj).forEach(name => {
        const value = obj[name];
        if (value && typeof value === "object" && !Object.isFrozen(value)) {
            deepFreeze(value);
        }
    });
    return Object.freeze(obj);
}

// Problem 3: Object equality check
function deepEqual(obj1, obj2) {
    if (obj1 === obj2) return true;
    
    if (typeof obj1 !== "object" || typeof obj2 !== "object") return false;
    if (obj1 === null || obj2 === null) return false;
    
    const keys1 = Object.keys(obj1);
    const keys2 = Object.keys(obj2);
    
    if (keys1.length !== keys2.length) return false;
    
    return keys1.every(key => 
        keys2.includes(key) && deepEqual(obj1[key], obj2[key])
    );
}

// Problem 4: Create observable object
function makeObservable(target) {
    const handlers = Symbol("handlers");
    target[handlers] = [];
    
    target.observe = function(handler) {
        this[handlers].push(handler);
    };
    
    return new Proxy(target, {
        set(target, property, value, receiver) {
            let success = Reflect.set(target, property, value, receiver);
            if (success) {
                target[handlers].forEach(h => h(property, value));
            }
            return success;
        }
    });
}
```

---

## ✅ Day 9 Checklist

- [ ] Use Object.create for prototype patterns
- [ ] Understand Object.freeze (shallow freeze)
- [ ] Implement deep freeze
- [ ] Know the difference between freeze/seal/preventExtensions
- [ ] Use Object.defineProperty for property control
- [ ] Understand property descriptors
- [ ] Master shallow vs deep cloning
- [ ] Use structuredClone for deep cloning
- [ ] Know Object utility methods
- [ ] Complete practice problems
