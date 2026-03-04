# Day 20: Proxy, Reflect, Generators & Iterators

## 🎯 Learning Objectives
- Master Proxy traps
- Understand Reflect API
- Create custom iterators
- Use generators effectively
- Implement async iterators

---

## 🎭 Proxy

Proxy creates a wrapper that intercepts operations on an object.

```javascript
/*
╔════════════════════════════════════════════════════════════════════╗
║                        PROXY CONCEPT                                ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║   Operation  ───────►  Proxy  ───────►  Target                     ║
║                          │                                          ║
║                      Handler                                        ║
║                     (traps)                                         ║
║                                                                     ║
║   const proxy = new Proxy(target, handler)                          ║
║                                                                     ║
╚════════════════════════════════════════════════════════════════════╝
*/

// Basic Proxy
const target = {
    name: 'John',
    age: 30
};

const handler = {
    get(target, property) {
        console.log(`Getting ${property}`);
        return target[property];
    },
    set(target, property, value) {
        console.log(`Setting ${property} to ${value}`);
        target[property] = value;
        return true; // Must return true for success
    }
};

const proxy = new Proxy(target, handler);

proxy.name;        // Log: Getting name, Returns: 'John'
proxy.age = 31;    // Log: Setting age to 31
```

### All Proxy Traps

```javascript
const handler = {
    // Property access: obj.prop, obj['prop']
    get(target, property, receiver) {
        return Reflect.get(target, property, receiver);
    },
    
    // Property assignment: obj.prop = value
    set(target, property, value, receiver) {
        return Reflect.set(target, property, value, receiver);
    },
    
    // 'prop' in obj
    has(target, property) {
        return Reflect.has(target, property);
    },
    
    // delete obj.prop
    deleteProperty(target, property) {
        return Reflect.deleteProperty(target, property);
    },
    
    // Object.keys(), for...in, etc.
    ownKeys(target) {
        return Reflect.ownKeys(target);
    },
    
    // Object.getOwnPropertyDescriptor()
    getOwnPropertyDescriptor(target, property) {
        return Reflect.getOwnPropertyDescriptor(target, property);
    },
    
    // Object.defineProperty()
    defineProperty(target, property, descriptor) {
        return Reflect.defineProperty(target, property, descriptor);
    },
    
    // Object.getPrototypeOf()
    getPrototypeOf(target) {
        return Reflect.getPrototypeOf(target);
    },
    
    // Object.setPrototypeOf()
    setPrototypeOf(target, prototype) {
        return Reflect.setPrototypeOf(target, prototype);
    },
    
    // Object.isExtensible()
    isExtensible(target) {
        return Reflect.isExtensible(target);
    },
    
    // Object.preventExtensions()
    preventExtensions(target) {
        return Reflect.preventExtensions(target);
    },
    
    // new proxy() - when target is a constructor
    construct(target, args) {
        return Reflect.construct(target, args);
    },
    
    // proxy() - when target is a function
    apply(target, thisArg, args) {
        return Reflect.apply(target, thisArg, args);
    }
};
```

### Practical Proxy Examples

```javascript
// 1. Validation
function createValidated(schema) {
    return function(obj) {
        return new Proxy(obj, {
            set(target, property, value) {
                if (property in schema) {
                    const validator = schema[property];
                    if (!validator(value)) {
                        throw new Error(`Invalid value for ${property}: ${value}`);
                    }
                }
                target[property] = value;
                return true;
            }
        });
    };
}

const schema = {
    age: (v) => typeof v === 'number' && v >= 0 && v <= 150,
    email: (v) => typeof v === 'string' && v.includes('@'),
    name: (v) => typeof v === 'string' && v.length > 0
};

const createUser = createValidated(schema);
const user = createUser({});

user.age = 25;          // OK
user.email = 'a@b.com'; // OK
// user.age = -5;       // Error: Invalid value for age

// 2. Default values
function withDefaults(defaults) {
    return new Proxy({}, {
        get(target, property) {
            return property in target ? target[property] : defaults[property];
        }
    });
}

const config = withDefaults({
    port: 3000,
    host: 'localhost',
    debug: false
});

console.log(config.port);      // 3000
console.log(config.host);      // 'localhost'
config.port = 8080;
console.log(config.port);      // 8080

// 3. Observable / Reactive
function observable(obj, callback) {
    return new Proxy(obj, {
        set(target, property, value) {
            const oldValue = target[property];
            target[property] = value;
            callback(property, value, oldValue);
            return true;
        }
    });
}

const state = observable({ count: 0 }, (prop, newVal, oldVal) => {
    console.log(`${prop} changed: ${oldVal} → ${newVal}`);
    updateUI();
});

state.count++;  // count changed: 0 → 1

// 4. Private properties
const privateHandler = {
    get(target, property) {
        if (property.startsWith('_')) {
            throw new Error(`Cannot access private property: ${property}`);
        }
        return target[property];
    },
    set(target, property, value) {
        if (property.startsWith('_')) {
            throw new Error(`Cannot set private property: ${property}`);
        }
        target[property] = value;
        return true;
    },
    ownKeys(target) {
        return Object.keys(target).filter(key => !key.startsWith('_'));
    }
};

const person = new Proxy({
    name: 'John',
    _secret: 'hidden'
}, privateHandler);

console.log(person.name);    // 'John'
// console.log(person._secret); // Error!
console.log(Object.keys(person)); // ['name']

// 5. Array negative indexing
const negativeArray = (arr) => new Proxy(arr, {
    get(target, property) {
        let index = Number(property);
        if (Number.isInteger(index) && index < 0) {
            index = target.length + index;
        }
        return target[index];
    }
});

const arr = negativeArray([1, 2, 3, 4, 5]);
console.log(arr[-1]); // 5
console.log(arr[-2]); // 4
```

---

## 🪞 Reflect

Reflect provides methods for interceptable JavaScript operations (same as Proxy traps).

```javascript
// Benefits of Reflect:
// 1. Returns boolean for success/failure
// 2. Consistent with Proxy trap signatures
// 3. Better error handling than Object methods

// Property operations
const obj = { name: 'John', age: 30 };

Reflect.get(obj, 'name');                    // 'John'
Reflect.set(obj, 'name', 'Jane');            // true
Reflect.has(obj, 'name');                    // true
Reflect.deleteProperty(obj, 'age');          // true
Reflect.ownKeys(obj);                        // ['name']

// Define property
Reflect.defineProperty(obj, 'id', {
    value: 1,
    writable: false
});

// Property descriptor
Reflect.getOwnPropertyDescriptor(obj, 'name');

// Prototype
Reflect.getPrototypeOf(obj);                 // Object.prototype
Reflect.setPrototypeOf(obj, null);           // true

// Function operations
function greet(greeting) {
    return `${greeting}, ${this.name}!`;
}

Reflect.apply(greet, { name: 'John' }, ['Hello']); // 'Hello, John!'

// Constructor
class Person {
    constructor(name) {
        this.name = name;
    }
}

const person = Reflect.construct(Person, ['John']);

// Prevent extensions
Reflect.preventExtensions(obj);
Reflect.isExtensible(obj); // false

// Proper Proxy with Reflect (recommended pattern)
const proxy = new Proxy(target, {
    get(target, property, receiver) {
        console.log(`Accessing ${property}`);
        // Use Reflect to maintain proper behavior
        return Reflect.get(target, property, receiver);
    },
    set(target, property, value, receiver) {
        console.log(`Setting ${property}`);
        // Reflect.set returns boolean for validation
        return Reflect.set(target, property, value, receiver);
    }
});
```

---

## 🔄 Iterators

An iterator is an object with a `next()` method that returns `{ value, done }`.

```javascript
// Built-in iterables
const arr = [1, 2, 3];
const iterator = arr[Symbol.iterator]();

iterator.next(); // { value: 1, done: false }
iterator.next(); // { value: 2, done: false }
iterator.next(); // { value: 3, done: false }
iterator.next(); // { value: undefined, done: true }

// Custom iterator
const range = {
    from: 1,
    to: 5,
    
    [Symbol.iterator]() {
        let current = this.from;
        const last = this.to;
        
        return {
            next() {
                if (current <= last) {
                    return { value: current++, done: false };
                }
                return { done: true };
            }
        };
    }
};

for (const num of range) {
    console.log(num); // 1, 2, 3, 4, 5
}

console.log([...range]); // [1, 2, 3, 4, 5]

// Iterator class
class Counter {
    constructor(start, end, step = 1) {
        this.start = start;
        this.end = end;
        this.step = step;
    }
    
    [Symbol.iterator]() {
        let current = this.start;
        const { end, step } = this;
        
        return {
            next() {
                if (current <= end) {
                    const value = current;
                    current += step;
                    return { value, done: false };
                }
                return { done: true };
            },
            
            return() {
                // Called when iteration is stopped early
                console.log('Iterator closed');
                return { done: true };
            }
        };
    }
}

const counter = new Counter(0, 10, 2);
for (const n of counter) {
    console.log(n); // 0, 2, 4, 6, 8, 10
}

// String iterator
const str = 'Hello';
for (const char of str) {
    console.log(char); // H, e, l, l, o
}

// Map and Set iterators
const map = new Map([['a', 1], ['b', 2]]);
for (const [key, value] of map) {
    console.log(key, value);
}

const set = new Set([1, 2, 3]);
for (const value of set) {
    console.log(value);
}
```

---

## ⚡ Generators

Generators are functions that can be paused and resumed.

```javascript
// Basic generator
function* simpleGenerator() {
    yield 1;
    yield 2;
    yield 3;
}

const gen = simpleGenerator();
gen.next(); // { value: 1, done: false }
gen.next(); // { value: 2, done: false }
gen.next(); // { value: 3, done: false }
gen.next(); // { value: undefined, done: true }

// Generators are iterable
for (const value of simpleGenerator()) {
    console.log(value); // 1, 2, 3
}

console.log([...simpleGenerator()]); // [1, 2, 3]

// Infinite generator
function* infiniteSequence() {
    let i = 0;
    while (true) {
        yield i++;
    }
}

const infinite = infiniteSequence();
infinite.next().value; // 0
infinite.next().value; // 1
// ... continues forever

// Passing values into generators
function* calculator() {
    const a = yield 'Enter first number';
    const b = yield 'Enter second number';
    return a + b;
}

const calc = calculator();
calc.next();        // { value: 'Enter first number', done: false }
calc.next(5);       // { value: 'Enter second number', done: false }
calc.next(3);       // { value: 8, done: true }

// yield* delegation
function* innerGen() {
    yield 1;
    yield 2;
}

function* outerGen() {
    yield 'start';
    yield* innerGen(); // Delegates to innerGen
    yield 'end';
}

console.log([...outerGen()]); // ['start', 1, 2, 'end']

// Generator return and throw
function* controlledGen() {
    try {
        yield 1;
        yield 2;
        yield 3;
    } finally {
        console.log('Cleanup');
    }
}

const cg = controlledGen();
cg.next();           // { value: 1, done: false }
cg.return('bye');    // Cleanup, { value: 'bye', done: true }

const cg2 = controlledGen();
cg2.next();
cg2.throw(new Error('Oops!')); // Cleanup, throws Error
```

### Practical Generator Examples

```javascript
// 1. ID generator
function* idGenerator(prefix = 'id') {
    let id = 0;
    while (true) {
        yield `${prefix}_${id++}`;
    }
}

const userIdGen = idGenerator('user');
userIdGen.next().value; // 'user_0'
userIdGen.next().value; // 'user_1'

// 2. Fibonacci sequence
function* fibonacci() {
    let [prev, curr] = [0, 1];
    while (true) {
        yield curr;
        [prev, curr] = [curr, prev + curr];
    }
}

const fib = fibonacci();
for (let i = 0; i < 10; i++) {
    console.log(fib.next().value);
}
// 1, 1, 2, 3, 5, 8, 13, 21, 34, 55

// 3. Tree traversal
function* traverseTree(node) {
    if (!node) return;
    
    yield node.value;
    yield* traverseTree(node.left);
    yield* traverseTree(node.right);
}

const tree = {
    value: 1,
    left: {
        value: 2,
        left: { value: 4 },
        right: { value: 5 }
    },
    right: {
        value: 3,
        left: { value: 6 },
        right: { value: 7 }
    }
};

console.log([...traverseTree(tree)]); // [1, 2, 4, 5, 3, 6, 7]

// 4. Pagination
function* paginate(items, pageSize) {
    for (let i = 0; i < items.length; i += pageSize) {
        yield items.slice(i, i + pageSize);
    }
}

const items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
const pages = paginate(items, 3);

pages.next().value; // [1, 2, 3]
pages.next().value; // [4, 5, 6]
pages.next().value; // [7, 8, 9]
pages.next().value; // [10]

// 5. State machine
function* trafficLight() {
    while (true) {
        yield 'green';
        yield 'yellow';
        yield 'red';
    }
}

const light = trafficLight();
for (let i = 0; i < 6; i++) {
    console.log(light.next().value);
}
// green, yellow, red, green, yellow, red
```

---

## 🌊 Async Iterators and Generators

```javascript
// Async iterator
const asyncIterable = {
    async *[Symbol.asyncIterator]() {
        for (let i = 0; i < 3; i++) {
            await new Promise(r => setTimeout(r, 1000));
            yield i;
        }
    }
};

(async () => {
    for await (const value of asyncIterable) {
        console.log(value); // 0, 1, 2 (one second apart)
    }
})();

// Async generator
async function* asyncGenerator() {
    yield await fetchData(1);
    yield await fetchData(2);
    yield await fetchData(3);
}

// Practical: Stream pagination
async function* fetchPages(url) {
    let page = 1;
    while (true) {
        const response = await fetch(`${url}?page=${page}`);
        const data = await response.json();
        
        if (data.items.length === 0) break;
        
        yield* data.items;
        page++;
    }
}

// Usage
for await (const item of fetchPages('/api/users')) {
    processItem(item);
}

// Async generator with streaming
async function* streamResponse(url) {
    const response = await fetch(url);
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        yield decoder.decode(value);
    }
}

// Process stream
for await (const chunk of streamResponse('/api/stream')) {
    console.log('Received chunk:', chunk);
}
```

---

## ✅ Day 20 Checklist

- [ ] Understand Proxy concept and traps
- [ ] Create validation proxies
- [ ] Implement reactive/observable patterns
- [ ] Use Reflect API properly
- [ ] Know when to use Reflect over Object
- [ ] Create custom iterators
- [ ] Understand Symbol.iterator
- [ ] Write generator functions
- [ ] Use yield and yield*
- [ ] Pass values into generators
- [ ] Implement async iterators
- [ ] Use async generators for streaming
