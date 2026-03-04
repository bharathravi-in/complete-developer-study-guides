# Day 23: Output Prediction Questions

## 🎯 Learning Objectives
- Predict JavaScript output accurately
- Understand tricky JS behaviors
- Recognize common interview patterns
- Debug logical errors

---

## 🔄 Hoisting & Scope

### Question 1
```javascript
console.log(a);
var a = 5;
console.log(a);

// Output:
// undefined
// 5

// Why: var is hoisted, but not the assignment
```

### Question 2
```javascript
console.log(a);
let a = 5;

// Output:
// ReferenceError: Cannot access 'a' before initialization

// Why: let has TDZ (Temporal Dead Zone)
```

### Question 3
```javascript
var a = 1;
function foo() {
    console.log(a);
    var a = 2;
    console.log(a);
}
foo();

// Output:
// undefined
// 2

// Why: Local 'a' shadows global 'a', but hoisted
```

### Question 4
```javascript
function foo() {
    console.log(a);
}
var a = 1;
foo();

// Output:
// 1

// Why: By the time foo() is called, a is already assigned
```

### Question 5
```javascript
for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 0);
}

// Output:
// 3
// 3
// 3

// Why: var has function scope, all callbacks share same i
```

### Question 6
```javascript
for (let i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 0);
}

// Output:
// 0
// 1
// 2

// Why: let has block scope, each iteration has its own i
```

---

## 🎯 this Keyword

### Question 7
```javascript
const obj = {
    name: 'John',
    greet: function() {
        console.log(this.name);
    }
};

obj.greet();
const fn = obj.greet;
fn();

// Output:
// John
// undefined (or throws in strict mode)

// Why: Method vs function call - this changes
```

### Question 8
```javascript
const obj = {
    name: 'John',
    greet: () => {
        console.log(this.name);
    }
};

obj.greet();

// Output:
// undefined

// Why: Arrow functions don't have their own this
```

### Question 9
```javascript
const obj = {
    name: 'John',
    greet() {
        const inner = function() {
            console.log(this.name);
        };
        inner();
    }
};

obj.greet();

// Output:
// undefined

// Why: inner() is called as regular function
```

### Question 10
```javascript
const obj = {
    name: 'John',
    greet() {
        const inner = () => {
            console.log(this.name);
        };
        inner();
    }
};

obj.greet();

// Output:
// John

// Why: Arrow function preserves this from greet()
```

### Question 11
```javascript
function Person(name) {
    this.name = name;
    return { name: 'Jane' };
}

const p = new Person('John');
console.log(p.name);

// Output:
// Jane

// Why: Returning an object overrides the new instance
```

---

## 🔐 Closures

### Question 12
```javascript
function outer() {
    var x = 10;
    return function inner() {
        console.log(x);
    };
}

const fn = outer();
fn();

// Output:
// 10

// Why: Closure retains access to outer's scope
```

### Question 13
```javascript
function createFunctions() {
    var result = [];
    for (var i = 0; i < 3; i++) {
        result.push(function() {
            console.log(i);
        });
    }
    return result;
}

const fns = createFunctions();
fns[0]();
fns[1]();
fns[2]();

// Output:
// 3
// 3
// 3

// Why: All functions share the same i (var hoisting)
```

### Question 14
```javascript
function createFunctions() {
    var result = [];
    for (var i = 0; i < 3; i++) {
        (function(j) {
            result.push(function() {
                console.log(j);
            });
        })(i);
    }
    return result;
}

const fns = createFunctions();
fns[0]();
fns[1]();
fns[2]();

// Output:
// 0
// 1
// 2

// Why: IIFE creates new scope for each iteration
```

---

## ⚖️ Type Coercion

### Question 15
```javascript
console.log([] + []);
console.log([] + {});
console.log({} + []);

// Output:
// ""
// "[object Object]"
// "[object Object]" (or 0 in some contexts)

// Why: Arrays/Objects convert to strings for +
```

### Question 16
```javascript
console.log(1 + '2');
console.log('1' - 2);
console.log('1' + 2 + 3);
console.log(1 + 2 + '3');

// Output:
// "12"
// -1
// "123"
// "33"

// Why: + with string concatenates, - converts to number
```

### Question 17
```javascript
console.log(true + true);
console.log(true + false);
console.log(false + false);

// Output:
// 2
// 1
// 0

// Why: Booleans convert to 1/0 for arithmetic
```

### Question 18
```javascript
console.log(null == undefined);
console.log(null === undefined);
console.log(null == 0);
console.log(null > 0);
console.log(null >= 0);

// Output:
// true
// false
// false
// false
// true

// Why: null loosely equals undefined, comparison converts to 0
```

### Question 19
```javascript
console.log([] == false);
console.log([] == ![]);
console.log('' == false);
console.log('' == 0);

// Output:
// true
// true
// true
// true

// Why: Complex coercion rules - ToPrimitive then ToNumber
```

### Question 20
```javascript
console.log(typeof null);
console.log(typeof undefined);
console.log(typeof NaN);
console.log(typeof function(){});

// Output:
// "object"
// "undefined"
// "number"
// "function"

// Why: typeof null is a famous JS bug, NaN is a number
```

---

## 📦 Objects & Arrays

### Question 21
```javascript
const a = { x: 1 };
const b = { x: 1 };
console.log(a == b);
console.log(a === b);

const c = a;
console.log(a === c);

// Output:
// false
// false
// true

// Why: Objects compared by reference, not value
```

### Question 22
```javascript
const arr = [1, 2, 3];
arr[10] = 10;
console.log(arr.length);
console.log(arr[5]);

// Output:
// 11
// undefined

// Why: Array has "holes" (sparse array)
```

### Question 23
```javascript
const arr = [1, 2, 3];
arr.length = 1;
console.log(arr);

// Output:
// [1]

// Why: Setting length truncates the array
```

### Question 24
```javascript
const a = [1, 2, 3];
const b = a;
b.push(4);
console.log(a);
console.log(b);

// Output:
// [1, 2, 3, 4]
// [1, 2, 3, 4]

// Why: Both reference the same array
```

### Question 25
```javascript
const obj = { a: 1 };
Object.freeze(obj);
obj.a = 2;
obj.b = 3;
console.log(obj);

// Output:
// { a: 1 }

// Why: Frozen objects can't be modified
```

---

## ⏱️ Event Loop & Async

### Question 26
```javascript
console.log('start');
setTimeout(() => console.log('timeout'), 0);
Promise.resolve().then(() => console.log('promise'));
console.log('end');

// Output:
// start
// end
// promise
// timeout

// Why: Microtasks (Promise) run before macrotasks (setTimeout)
```

### Question 27
```javascript
console.log('1');
setTimeout(() => console.log('2'), 0);
Promise.resolve()
    .then(() => console.log('3'))
    .then(() => console.log('4'));
console.log('5');

// Output:
// 1
// 5
// 3
// 4
// 2

// Why: Sync first, then all microtasks, then macrotasks
```

### Question 28
```javascript
async function async1() {
    console.log('async1 start');
    await async2();
    console.log('async1 end');
}

async function async2() {
    console.log('async2');
}

console.log('script start');
setTimeout(() => console.log('setTimeout'), 0);
async1();
new Promise((resolve) => {
    console.log('promise1');
    resolve();
}).then(() => console.log('promise2'));
console.log('script end');

// Output:
// script start
// async1 start
// async2
// promise1
// script end
// async1 end
// promise2
// setTimeout
```

### Question 29
```javascript
setTimeout(() => console.log('1'), 0);
setImmediate(() => console.log('2'));
Promise.resolve().then(() => console.log('3'));
process.nextTick(() => console.log('4'));

// Output (in Node.js):
// 4
// 3
// 1 or 2 (order uncertain between setTimeout and setImmediate)
// 2 or 1

// Why: nextTick > microtasks > macrotasks
```

### Question 30
```javascript
const promise = new Promise((resolve, reject) => {
    console.log(1);
    resolve();
    console.log(2);
    reject();
});

promise
    .then(() => console.log(3))
    .catch(() => console.log(4));

console.log(5);

// Output:
// 1
// 2
// 5
// 3

// Why: Promise executor runs sync, once resolved stays resolved
```

---

## 🔗 Prototypes & Classes

### Question 31
```javascript
function Foo() {
    this.a = 1;
}

Foo.prototype.a = 2;

const obj = new Foo();
console.log(obj.a);
delete obj.a;
console.log(obj.a);

// Output:
// 1
// 2

// Why: Instance property shadows prototype, delete reveals it
```

### Question 32
```javascript
function Parent() {
    this.name = 'parent';
}

Parent.prototype.getName = function() {
    return this.name;
};

function Child() {
    this.name = 'child';
}

Child.prototype = new Parent();

const c = new Child();
console.log(c.getName());
console.log(c.constructor.name);

// Output:
// child
// Parent

// Why: Method from prototype, but constructor not fixed
```

---

## 🎲 Tricky Problems

### Question 33
```javascript
console.log(0.1 + 0.2 === 0.3);
console.log(0.1 + 0.2);

// Output:
// false
// 0.30000000000000004

// Why: Floating point precision issues
```

### Question 34
```javascript
console.log(typeof typeof 1);

// Output:
// "string"

// Why: typeof 1 is "number", typeof "number" is "string"
```

### Question 35
```javascript
console.log(3 > 2 > 1);

// Output:
// false

// Why: (3 > 2) > 1 → true > 1 → 1 > 1 → false
```

### Question 36
```javascript
const a = {};
const b = { key: 'b' };
const c = { key: 'c' };

a[b] = 123;
a[c] = 456;

console.log(a[b]);

// Output:
// 456

// Why: Both b and c stringify to "[object Object]"
```

### Question 37
```javascript
let x = 1;
let y = x++;
let z = ++x;

console.log(x, y, z);

// Output:
// 3 1 3

// Why: x++ returns then increments, ++x increments then returns
```

### Question 38
```javascript
console.log(!!"false" == !!"true");
console.log("false" == false);

// Output:
// true
// false

// Why: Non-empty strings are truthy, but string "false" != boolean false
```

### Question 39
```javascript
const arr = [10, 12, 15, 21];
for (var i = 0; i < arr.length; i++) {
    setTimeout(function() {
        console.log('Index: ' + i + ', element: ' + arr[i]);
    }, 1000);
}

// Output (after 1 second):
// Index: 4, element: undefined
// Index: 4, element: undefined
// Index: 4, element: undefined
// Index: 4, element: undefined

// Why: var hoisting, i is 4 when callbacks run
```

### Question 40
```javascript
console.log((function(x) {
    delete x;
    return x;
})(1));

// Output:
// 1

// Why: Can't delete function parameters
```

---

## 🔮 Advanced Questions

### Question 41
```javascript
var x = 21;
var girl = function() {
    console.log(x);
    var x = 20;
};
girl();

// Output:
// undefined

// Why: Local x is hoisted, shadows global x
```

### Question 42
```javascript
console.log(1 < 2 < 3);
console.log(3 > 2 > 1);

// Output:
// true
// false

// Why: (1 < 2) < 3 → true < 3 → 1 < 3 → true
//      (3 > 2) > 1 → true > 1 → 1 > 1 → false
```

### Question 43
```javascript
[1, 2, 3].map(parseInt);

// Output:
// [1, NaN, NaN]

// Why: parseInt gets (value, index, array)
// parseInt(1, 0) → 1 (radix 0 treated as 10)
// parseInt(2, 1) → NaN (invalid radix)
// parseInt(3, 2) → NaN (3 not valid in binary)
```

### Question 44
```javascript
const person = { name: 'John' };
Object.defineProperty(person, 'age', {
    value: 30,
    writable: false
});
person.age = 40;
console.log(person.age);

// Output:
// 30

// Why: Property is not writable
```

### Question 45
```javascript
function foo() {
    return
    {
        bar: 'hello'
    };
}

console.log(foo());

// Output:
// undefined

// Why: ASI (Automatic Semicolon Insertion) after return
```

---

## ✅ Day 23 Checklist

- [ ] Understand hoisting (var vs let/const)
- [ ] Know this binding rules
- [ ] Master closure behavior
- [ ] Handle type coercion edge cases
- [ ] Know object reference vs value
- [ ] Understand event loop order
- [ ] Know microtask vs macrotask
- [ ] Handle prototype chain lookups
- [ ] Recognize ASI pitfalls
- [ ] Practice 50+ output questions
