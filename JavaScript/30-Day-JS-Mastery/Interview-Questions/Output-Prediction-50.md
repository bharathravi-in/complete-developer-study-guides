# JavaScript Output Prediction Questions - 50 Tricky Questions

Master these tricky output prediction questions to ace your JavaScript interviews!

---

## How to Use This Document

1. Try to predict the output BEFORE looking at the answer
2. Understand WHY the output is what it is
3. Review the concept if you got it wrong
4. Practice explaining your reasoning out loud

---

## 🔄 Hoisting & Scope

### Q1: Variable Hoisting
```javascript
console.log(a);
console.log(b);
var a = 1;
let b = 2;
```

<details>
<summary>Answer</summary>

```
undefined
ReferenceError: Cannot access 'b' before initialization
```
**Explanation:** `var` is hoisted with value `undefined`. `let` is hoisted but in Temporal Dead Zone.
</details>

---

### Q2: Function vs Variable Hoisting
```javascript
console.log(foo);
var foo = 'hello';
function foo() {
    return 'function';
}
console.log(foo);
```

<details>
<summary>Answer</summary>

```
[Function: foo]
hello
```
**Explanation:** Function declarations are hoisted completely (above var). After execution, foo is reassigned to 'hello'.
</details>

---

### Q3: Hoisting in Conditions
```javascript
function test() {
    console.log(x);
    if (false) {
        var x = 1;
    }
    console.log(x);
}
test();
```

<details>
<summary>Answer</summary>

```
undefined
undefined
```
**Explanation:** `var` is function-scoped, not block-scoped. Declaration is hoisted even though the block never executes.
</details>

---

### Q4: Let in Loops
```javascript
for (let i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 0);
}
```

<details>
<summary>Answer</summary>

```
0
1
2
```
**Explanation:** `let` creates a new binding for each loop iteration, so each closure captures its own `i`.
</details>

---

### Q5: Var in Loops
```javascript
for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 0);
}
```

<details>
<summary>Answer</summary>

```
3
3
3
```
**Explanation:** `var` is function-scoped. All closures share the same `i`, which is 3 after the loop ends.
</details>

---

## 🎯 this Keyword

### Q6: this in Object Method
```javascript
const obj = {
    name: 'Object',
    getName: function() {
        return this.name;
    },
    getNameArrow: () => {
        return this.name;
    }
};

console.log(obj.getName());
console.log(obj.getNameArrow());
```

<details>
<summary>Answer</summary>

```
Object
undefined
```
**Explanation:** Regular function's `this` is the calling object. Arrow function's `this` is lexical (from enclosing scope, likely global).
</details>

---

### Q7: Extracted Method
```javascript
const obj = {
    name: 'Object',
    greet() {
        console.log(`Hello, ${this.name}`);
    }
};

obj.greet();
const greet = obj.greet;
greet();
```

<details>
<summary>Answer</summary>

```
Hello, Object
Hello, undefined
```
**Explanation:** When method is extracted, `this` binding is lost. In non-strict mode, `this` becomes global object.
</details>

---

### Q8: this in Nested Functions
```javascript
const obj = {
    name: 'Object',
    outer() {
        console.log(this.name);
        function inner() {
            console.log(this.name);
        }
        inner();
    }
};
obj.outer();
```

<details>
<summary>Answer</summary>

```
Object
undefined
```
**Explanation:** Nested regular function loses `this` binding. Use arrow function or `const self = this` to fix.
</details>

---

### Q9: this with call/apply
```javascript
function greet() {
    console.log(`Hello, ${this.name}`);
}

const person = { name: 'Alice' };

greet.call(person);
greet.apply(person);
```

<details>
<summary>Answer</summary>

```
Hello, Alice
Hello, Alice
```
**Explanation:** Both `call` and `apply` explicitly set `this` to the provided object.
</details>

---

### Q10: this in Constructor
```javascript
function Person(name) {
    this.name = name;
    return { name: 'Overridden' };
}

const p = new Person('Alice');
console.log(p.name);
```

<details>
<summary>Answer</summary>

```
Overridden
```
**Explanation:** When constructor returns an object, that object is returned instead of `this`.
</details>

---

## 🔒 Closures

### Q11: Basic Closure
```javascript
function outer() {
    let count = 0;
    return function inner() {
        count++;
        console.log(count);
    };
}

const counter1 = outer();
const counter2 = outer();
counter1();
counter1();
counter2();
```

<details>
<summary>Answer</summary>

```
1
2
1
```
**Explanation:** Each call to `outer()` creates a new closure with its own `count`. counter1 and counter2 are independent.
</details>

---

### Q12: Closure with setTimeout
```javascript
function createFunctions() {
    const arr = [];
    for (var i = 0; i < 3; i++) {
        arr.push(function() {
            console.log(i);
        });
    }
    return arr;
}

const functions = createFunctions();
functions[0]();
functions[1]();
functions[2]();
```

<details>
<summary>Answer</summary>

```
3
3
3
```
**Explanation:** All functions share the same `i` (var is function-scoped). By the time they execute, `i` is 3.
</details>

---

### Q13: Closure with IIFE
```javascript
for (var i = 0; i < 3; i++) {
    (function(j) {
        setTimeout(() => console.log(j), 0);
    })(i);
}
```

<details>
<summary>Answer</summary>

```
0
1
2
```
**Explanation:** IIFE creates a new scope for each iteration, capturing the current value of `i` as `j`.
</details>

---

## 🔀 Type Coercion

### Q14: String Concatenation
```javascript
console.log(1 + '2' + '3');
console.log(1 + 2 + '3');
console.log('1' + 2 + 3);
```

<details>
<summary>Answer</summary>

```
123
33
123
```
**Explanation:** + with string converts to string. Operations are left-to-right.
</details>

---

### Q15: Boolean Coercion
```javascript
console.log([] == false);
console.log([] == ![]);
console.log(!![] == true);
```

<details>
<summary>Answer</summary>

```
true
true
true
```
**Explanation:** 
- [] → '' → 0, false → 0, so true
- ![] → false → 0, [] → 0, so true  
- !![] → true (arrays are truthy)
</details>

---

### Q16: Equality Coercion
```javascript
console.log(null == undefined);
console.log(null === undefined);
console.log(NaN === NaN);
```

<details>
<summary>Answer</summary>

```
true
false
false
```
**Explanation:** null and undefined equal only each other with ==. NaN is not equal to anything, including itself.
</details>

---

### Q17: Plus Operator
```javascript
console.log(+'42');
console.log(+[]);
console.log(+[1]);
console.log(+[1, 2]);
```

<details>
<summary>Answer</summary>

```
42
0
1
NaN
```
**Explanation:** Unary + converts to number. [] → '' → 0. [1] → '1' → 1. [1,2] → '1,2' → NaN.
</details>

---

### Q18: String Coercion
```javascript
console.log('b' + 'a' + + 'a' + 'a');
```

<details>
<summary>Answer</summary>

```
baNaNa
```
**Explanation:** + 'a' is unary plus trying to convert 'a' to number → NaN. Then concatenation continues.
</details>

---

## 📦 Objects & Arrays

### Q19: Object Key Conversion
```javascript
const a = {};
const b = { key: 'b' };
const c = { key: 'c' };

a[b] = 123;
a[c] = 456;

console.log(a[b]);
```

<details>
<summary>Answer</summary>

```
456
```
**Explanation:** Objects as keys are converted to string '[object Object]'. Both b and c become the same key.
</details>

---

### Q20: Array Methods
```javascript
const arr = [1, 2, 3];
arr[10] = 11;
console.log(arr.length);
console.log(arr.filter(x => x === undefined).length);
```

<details>
<summary>Answer</summary>

```
11
0
```
**Explanation:** Length is 11 (sparse array). filter/map skip empty slots (not undefined, just empty).
</details>

---

### Q21: Array Reference
```javascript
const a = [1, 2, 3];
const b = a;
b.push(4);
console.log(a);
console.log(a === b);
```

<details>
<summary>Answer</summary>

```
[1, 2, 3, 4]
true
```
**Explanation:** b is a reference to the same array. Modifying b also modifies a.
</details>

---

### Q22: Spread vs Assign
```javascript
const obj = { a: 1, b: { c: 2 } };
const copy = { ...obj };
copy.a = 10;
copy.b.c = 20;

console.log(obj.a);
console.log(obj.b.c);
```

<details>
<summary>Answer</summary>

```
1
20
```
**Explanation:** Spread creates shallow copy. Primitives are copied, nested objects share references.
</details>

---

### Q23: delete Operator
```javascript
const arr = [1, 2, 3];
delete arr[1];
console.log(arr.length);
console.log(arr);
console.log(arr[1]);
```

<details>
<summary>Answer</summary>

```
3
[1, empty, 3]  // or [1, <1 empty item>, 3]
undefined
```
**Explanation:** delete removes property but doesn't reindex or change length. Creates a sparse array.
</details>

---

## ⚡ Async & Event Loop

### Q24: Event Loop Order
```javascript
console.log('1');
setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => console.log('3'));
console.log('4');
```

<details>
<summary>Answer</summary>

```
1
4
3
2
```
**Explanation:** Sync first (1, 4), then microtasks (Promise - 3), then macrotasks (setTimeout - 2).
</details>

---

### Q25: Nested Promises
```javascript
Promise.resolve()
    .then(() => {
        console.log('1');
        return Promise.resolve('2');
    })
    .then(console.log);

Promise.resolve()
    .then(() => console.log('3'))
    .then(() => console.log('4'));
```

<details>
<summary>Answer</summary>

```
1
3
4
2
```
**Explanation:** Returning a Promise from .then() requires extra microtask ticks before resolution.
</details>

---

### Q26: setTimeout Order
```javascript
setTimeout(() => console.log('1'), 0);
setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => {
    console.log('3');
    setTimeout(() => console.log('4'), 0);
});
```

<details>
<summary>Answer</summary>

```
3
1
2
4
```
**Explanation:** Microtask (3) runs first, then macrotasks in order (1, 2, then 4 which was queued later).
</details>

---

### Q27: Async/Await Order
```javascript
async function async1() {
    console.log('1');
    await async2();
    console.log('2');
}

async function async2() {
    console.log('3');
}

console.log('4');
async1();
console.log('5');
```

<details>
<summary>Answer</summary>

```
4
1
3
5
2
```
**Explanation:** await pauses async1, rest after await becomes microtask. Sync code continues.
</details>

---

### Q28: Promise Constructor
```javascript
const promise = new Promise((resolve) => {
    console.log('1');
    resolve();
    console.log('2');
});

promise.then(() => console.log('3'));
console.log('4');
```

<details>
<summary>Answer</summary>

```
1
2
4
3
```
**Explanation:** Promise executor is synchronous. resolve() doesn't stop execution. then() callback is microtask.
</details>

---

## 🔗 Prototypes

### Q29: Prototype Chain
```javascript
function Animal() {}
Animal.prototype.speak = function() {
    return 'sound';
};

function Dog() {}
Dog.prototype = Object.create(Animal.prototype);
Dog.prototype.speak = function() {
    return 'bark';
};

const dog = new Dog();
console.log(dog.speak());
console.log(dog instanceof Animal);
```

<details>
<summary>Answer</summary>

```
bark
true
```
**Explanation:** Dog's speak overwrites Animal's. instanceof checks prototype chain.
</details>

---

### Q30: Constructor Property
```javascript
function Person(name) {
    this.name = name;
}

const p1 = new Person('Alice');
const p2 = new p1.constructor('Bob');

console.log(p2.name);
console.log(p2 instanceof Person);
```

<details>
<summary>Answer</summary>

```
Bob
true
```
**Explanation:** p1.constructor references Person. Can use it to create new instances.
</details>

---

## 🧩 Advanced

### Q31: typeof quirks
```javascript
console.log(typeof typeof 1);
console.log(typeof null);
console.log(typeof undefined);
console.log(typeof NaN);
```

<details>
<summary>Answer</summary>

```
string
object
undefined
number
```
**Explanation:** typeof always returns a string. null → 'object' is a bug. NaN is still a number type.
</details>

---

### Q32: Comparison with Different Types
```javascript
console.log([] + {});
console.log({} + []);
console.log([] + []);
console.log({} + {});
```

<details>
<summary>Answer</summary>

```
[object Object]
[object Object]  // or 0 in some consoles
""
[object Object][object Object]
```
**Explanation:** Arrays become '', objects become '[object Object]'. In some consoles, {} at start is empty block.
</details>

---

### Q33: Increment Operators
```javascript
let x = 1;
console.log(x++);
console.log(++x);
console.log(x);
```

<details>
<summary>Answer</summary>

```
1
3
3
```
**Explanation:** x++ returns then increments. ++x increments then returns.
</details>

---

### Q34: Floating Point
```javascript
console.log(0.1 + 0.2);
console.log(0.1 + 0.2 === 0.3);
console.log(0.1 + 0.2 - 0.3 < 0.0001);
```

<details>
<summary>Answer</summary>

```
0.30000000000000004
false
true
```
**Explanation:** IEEE 754 floating point precision limitations. Use epsilon comparison.
</details>

---

### Q35: Map Iteration
```javascript
const map = new Map();
map.set('a', 1);
map.set('a', 2);
map.set('b', 3);

console.log(map.get('a'));
console.log(map.size);
```

<details>
<summary>Answer</summary>

```
2
2
```
**Explanation:** Second set('a') overwrites first. Size counts unique keys.
</details>

---

### Q36: Object.is vs ===
```javascript
console.log(Object.is(NaN, NaN));
console.log(Object.is(0, -0));
console.log(0 === -0);
console.log(NaN === NaN);
```

<details>
<summary>Answer</summary>

```
true
false
true
false
```
**Explanation:** Object.is is more precise: NaN equals NaN, 0 and -0 are different.
</details>

---

### Q37: Generator Function
```javascript
function* gen() {
    yield 1;
    yield 2;
    return 3;
}

const g = gen();
console.log(g.next());
console.log(g.next());
console.log(g.next());
console.log(g.next());
```

<details>
<summary>Answer</summary>

```
{ value: 1, done: false }
{ value: 2, done: false }
{ value: 3, done: true }
{ value: undefined, done: true }
```
**Explanation:** return value is final value with done: true. Subsequent calls return undefined.
</details>

---

### Q38: Symbol Properties
```javascript
const sym = Symbol('key');
const obj = {
    [sym]: 'value',
    regular: 'prop'
};

console.log(Object.keys(obj));
console.log(Object.getOwnPropertySymbols(obj));
console.log(obj[sym]);
```

<details>
<summary>Answer</summary>

```
['regular']
[Symbol(key)]
value
```
**Explanation:** Symbol properties don't appear in Object.keys(). Use getOwnPropertySymbols().
</details>

---

### Q39: Proxy Behavior
```javascript
const obj = { a: 1, b: 2 };
const proxy = new Proxy(obj, {
    get(target, prop) {
        return prop in target ? target[prop] : 'default';
    }
});

console.log(proxy.a);
console.log(proxy.c);
```

<details>
<summary>Answer</summary>

```
1
default
```
**Explanation:** Proxy intercepts property access. Returns 'default' for non-existent properties.
</details>

---

### Q40: Rest Parameters
```javascript
function test(a, ...rest, b) {
    console.log(rest);
}
test(1, 2, 3, 4);
```

<details>
<summary>Answer</summary>

```
SyntaxError: Rest parameter must be last formal parameter
```
**Explanation:** Rest parameter must be the last parameter in function definition.
</details>

---

### Q41: Default Parameters
```javascript
function test(a = 1, b = a + 1, c = c + 1) {
    console.log(a, b, c);
}
test();
```

<details>
<summary>Answer</summary>

```
ReferenceError: Cannot access 'c' before initialization
```
**Explanation:** Default parameters are evaluated left-to-right. c tries to reference itself.
</details>

---

### Q42: Destructuring Default
```javascript
const { a: x = 10, b: y = 20 } = { a: undefined, b: null };
console.log(x);
console.log(y);
```

<details>
<summary>Answer</summary>

```
10
null
```
**Explanation:** Default only applies if value is undefined. null is a value, so no default.
</details>

---

### Q43: Class Hoisting
```javascript
const p = new Person('Alice');
console.log(p.name);

class Person {
    constructor(name) {
        this.name = name;
    }
}
```

<details>
<summary>Answer</summary>

```
ReferenceError: Cannot access 'Person' before initialization
```
**Explanation:** Classes are hoisted but not initialized (TDZ like let/const).
</details>

---

### Q44: Static Methods
```javascript
class Counter {
    static count = 0;
    constructor() {
        Counter.count++;
    }
    static getCount() {
        return this.count;
    }
}

const c1 = new Counter();
const c2 = new Counter();
console.log(Counter.getCount());
console.log(c1.getCount);
```

<details>
<summary>Answer</summary>

```
2
undefined
```
**Explanation:** Static methods belong to class, not instances. Instances can't access them.
</details>

---

### Q45: Array Sort
```javascript
const arr = [10, 2, 30, 1];
arr.sort();
console.log(arr);
```

<details>
<summary>Answer</summary>

```
[1, 10, 2, 30]
```
**Explanation:** Default sort converts to strings and compares UTF-16 codes. Use sort((a,b) => a-b) for numbers.
</details>

---

### Q46: parseInt Edge Cases
```javascript
console.log(parseInt('123abc'));
console.log(parseInt('abc123'));
console.log(parseInt(0.000001));
console.log(parseInt(0.0000001));
```

<details>
<summary>Answer</summary>

```
123
NaN
0
1
```
**Explanation:** parseInt parses until invalid char. Very small numbers convert to exponential notation string.
</details>

---

### Q47: Comma Operator
```javascript
console.log((1, 2, 3));
const x = (a = 1, b = 2, a + b);
console.log(x);
```

<details>
<summary>Answer</summary>

```
3
3
```
**Explanation:** Comma operator evaluates all expressions left-to-right, returns the last value.
</details>

---

### Q48: Tagged Template
```javascript
function tag(strings, ...values) {
    console.log(strings);
    console.log(values);
}

const a = 1, b = 2;
tag`Sum: ${a} + ${b} = ${a + b}`;
```

<details>
<summary>Answer</summary>

```
['Sum: ', ' + ', ' = ', '']
[1, 2, 3]
```
**Explanation:** Tagged templates receive string parts and evaluated expressions separately.
</details>

---

### Q49: WeakMap Keys
```javascript
const wm = new WeakMap();
wm.set('key', 'value');
console.log(wm.get('key'));
```

<details>
<summary>Answer</summary>

```
TypeError: Invalid value used as weak map key
```
**Explanation:** WeakMap keys must be objects, not primitives.
</details>

---

### Q50: Arguments Object
```javascript
function test(a, b) {
    arguments[0] = 10;
    console.log(a);
}

function testStrict(a, b) {
    'use strict';
    arguments[0] = 10;
    console.log(a);
}

test(1, 2);
testStrict(1, 2);
```

<details>
<summary>Answer</summary>

```
10
1
```
**Explanation:** In non-strict mode, arguments is linked to parameters. In strict mode, they're separate.
</details>

---

## 🎯 Practice Tips

1. **Run the code** in your browser console to verify
2. **Explain WHY** not just memorize the answer
3. **Group similar questions** to understand patterns
4. **Review weak areas** repeatedly
5. **Time yourself** - interviews have time pressure

---

## Key Concepts Summary

| Concept | Key Point |
|---------|-----------|
| var vs let/const | Scope, hoisting, TDZ |
| this | Call context, arrow functions |
| Closures | Captured variables |
| == vs === | Type coercion |
| Event Loop | Microtasks before macrotasks |
| Prototypes | Inheritance chain |
| Array methods | Sparse arrays, mutation |
| Objects | Reference types, shallow copy |

Good luck with your interviews! 🚀
