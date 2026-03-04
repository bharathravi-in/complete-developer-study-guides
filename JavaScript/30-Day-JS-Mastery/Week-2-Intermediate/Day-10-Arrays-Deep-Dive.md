# Day 10: Arrays Deep Dive

## 🎯 Learning Objectives
- Master map, filter, reduce
- Understand some, every, flat
- Learn sort internals
- Implement array methods manually

---

## 📚 Array Transformation Methods

### map()
Creates a new array by calling a function on every element.

```javascript
const numbers = [1, 2, 3, 4, 5];

// Basic map
const doubled = numbers.map(n => n * 2);
console.log(doubled); // [2, 4, 6, 8, 10]

// map with index
const indexed = numbers.map((n, i) => `${i}: ${n}`);
console.log(indexed); // ["0: 1", "1: 2", "2: 3", "3: 4", "4: 5"]

// map with array reference
const percentages = numbers.map((n, i, arr) => 
    ((n / arr.reduce((a, b) => a + b)) * 100).toFixed(1) + "%"
);

// Transforming objects
const users = [
    { name: "John", age: 30 },
    { name: "Jane", age: 25 }
];

const names = users.map(user => user.name);
console.log(names); // ["John", "Jane"]

// ⚠️ map gotchas
console.log(["1", "2", "3"].map(parseInt));
// [1, NaN, NaN] - parseInt receives (value, index) as (value, radix)

// Fix:
console.log(["1", "2", "3"].map(n => parseInt(n)));
// [1, 2, 3]
```

### filter()
Creates a new array with elements that pass the test.

```javascript
const numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

// Basic filter
const evens = numbers.filter(n => n % 2 === 0);
console.log(evens); // [2, 4, 6, 8, 10]

// Filter with objects
const users = [
    { name: "John", age: 30, active: true },
    { name: "Jane", age: 25, active: false },
    { name: "Bob", age: 35, active: true }
];

const activeUsers = users.filter(user => user.active);
const adults = users.filter(user => user.age >= 30);

// Filter unique values
const arr = [1, 2, 2, 3, 3, 3, 4];
const unique = arr.filter((value, index, self) => 
    self.indexOf(value) === index
);
console.log(unique); // [1, 2, 3, 4]

// Better: Use Set
const uniqueSet = [...new Set(arr)];

// Remove falsy values
const mixed = [0, 1, false, 2, "", 3, null, undefined, NaN];
const truthy = mixed.filter(Boolean);
console.log(truthy); // [1, 2, 3]
```

### reduce()
Reduces array to a single value.

```javascript
// Basic sum
const numbers = [1, 2, 3, 4, 5];
const sum = numbers.reduce((acc, curr) => acc + curr, 0);
console.log(sum); // 15

// Without initial value (first element becomes initial)
const product = numbers.reduce((acc, curr) => acc * curr);
console.log(product); // 120

// Find max
const max = numbers.reduce((a, b) => a > b ? a : b);
console.log(max); // 5

// Count occurrences
const fruits = ["apple", "banana", "apple", "orange", "banana", "apple"];
const count = fruits.reduce((acc, fruit) => {
    acc[fruit] = (acc[fruit] || 0) + 1;
    return acc;
}, {});
console.log(count); // { apple: 3, banana: 2, orange: 1 }

// Flatten array
const nested = [[1, 2], [3, 4], [5, 6]];
const flat = nested.reduce((acc, curr) => [...acc, ...curr], []);
console.log(flat); // [1, 2, 3, 4, 5, 6]

// Group by property
const people = [
    { name: "John", age: 30 },
    { name: "Jane", age: 25 },
    { name: "Bob", age: 30 }
];

const grouped = people.reduce((acc, person) => {
    const key = person.age;
    (acc[key] = acc[key] || []).push(person);
    return acc;
}, {});
console.log(grouped);
// { 25: [{name: "Jane", ...}], 30: [{name: "John", ...}, {name: "Bob", ...}] }

// Pipeline with reduce
const pipeline = [
    x => x * 2,
    x => x + 10,
    x => x / 2
];

const result = pipeline.reduce((acc, fn) => fn(acc), 5);
console.log(result); // ((5 * 2) + 10) / 2 = 10

// reduceRight (right to left)
const letters = ["a", "b", "c", "d"];
const reversed = letters.reduceRight((acc, letter) => acc + letter, "");
console.log(reversed); // "dcba"
```

---

## 🔍 Array Testing Methods

### some() and every()

```javascript
const numbers = [1, 2, 3, 4, 5];

// some - returns true if ANY element passes
console.log(numbers.some(n => n > 3));   // true
console.log(numbers.some(n => n > 10));  // false

// every - returns true if ALL elements pass
console.log(numbers.every(n => n > 0));  // true
console.log(numbers.every(n => n > 3));  // false

// Short-circuit behavior
const largeArray = new Array(1000000).fill(0);
largeArray[0] = 1;

// some stops at first true
console.time("some");
largeArray.some(n => n === 1); // Stops immediately
console.timeEnd("some"); // ~0ms

// every stops at first false
console.time("every");
largeArray.every(n => n === 0); // Stops immediately (first element)
console.timeEnd("every"); // ~0ms

// Practical examples
const users = [
    { name: "John", verified: true },
    { name: "Jane", verified: false }
];

const hasUnverified = users.some(u => !u.verified);
const allVerified = users.every(u => u.verified);
```

### find() and findIndex()

```javascript
const users = [
    { id: 1, name: "John" },
    { id: 2, name: "Jane" },
    { id: 3, name: "Bob" }
];

// find - returns first matching element
const jane = users.find(u => u.name === "Jane");
console.log(jane); // { id: 2, name: "Jane" }

// findIndex - returns index of first match
const janeIndex = users.findIndex(u => u.name === "Jane");
console.log(janeIndex); // 1

// Not found
const notFound = users.find(u => u.name === "Alice");
console.log(notFound); // undefined

const notFoundIndex = users.findIndex(u => u.name === "Alice");
console.log(notFoundIndex); // -1

// findLast / findLastIndex (ES2023)
const numbers = [1, 2, 3, 2, 1];
const lastTwo = numbers.findLast(n => n === 2);
console.log(lastTwo); // 2 (the second one at index 3)

const lastTwoIndex = numbers.findLastIndex(n => n === 2);
console.log(lastTwoIndex); // 3
```

---

## 📊 Array Flattening

### flat() and flatMap()

```javascript
// flat - flattens nested arrays
const nested = [1, [2, 3], [4, [5, 6]]];

console.log(nested.flat());    // [1, 2, 3, 4, [5, 6]] (depth 1)
console.log(nested.flat(2));   // [1, 2, 3, 4, 5, 6] (depth 2)
console.log(nested.flat(Infinity)); // [1, 2, 3, 4, 5, 6] (any depth)

// Remove empty slots
const sparse = [1, , 3, , 5];
console.log(sparse.flat()); // [1, 3, 5]

// flatMap - map + flat(1)
const sentences = ["Hello world", "How are you"];

// With map: nested arrays
const words1 = sentences.map(s => s.split(" "));
console.log(words1); // [["Hello", "world"], ["How", "are", "you"]]

// With flatMap: flattened
const words2 = sentences.flatMap(s => s.split(" "));
console.log(words2); // ["Hello", "world", "How", "are", "you"]

// flatMap use case: filtering and mapping
const users = [
    { name: "John", emails: ["john@a.com", "john@b.com"] },
    { name: "Jane", emails: ["jane@a.com"] }
];

const allEmails = users.flatMap(u => u.emails);
console.log(allEmails); // ["john@a.com", "john@b.com", "jane@a.com"]
```

---

## 🔄 Array Sorting

### sort() internals

```javascript
// Default sort (converts to strings!)
const numbers = [10, 2, 5, 1, 9];
console.log(numbers.sort()); // [1, 10, 2, 5, 9] - WRONG!

// Proper numeric sort
console.log(numbers.sort((a, b) => a - b)); // [1, 2, 5, 9, 10]

// Descending
console.log(numbers.sort((a, b) => b - a)); // [10, 9, 5, 2, 1]

// Compare function return value:
// - Negative: a comes before b
// - Zero: keep original order
// - Positive: b comes before a

// String sort (case-insensitive)
const names = ["John", "jane", "Bob", "alice"];
console.log(names.sort((a, b) => 
    a.toLowerCase().localeCompare(b.toLowerCase())
));
// ["alice", "Bob", "jane", "John"]

// Object sort
const users = [
    { name: "John", age: 30 },
    { name: "Jane", age: 25 },
    { name: "Bob", age: 35 }
];

// Sort by age
users.sort((a, b) => a.age - b.age);

// Sort by name
users.sort((a, b) => a.name.localeCompare(b.name));

// ⚠️ sort() mutates the original array!
const original = [3, 1, 2];
const sorted = original.sort();
console.log(original); // [1, 2, 3] - mutated!
console.log(original === sorted); // true - same reference

// Non-mutating sort with toSorted() (ES2023)
const nums = [3, 1, 2];
const sortedNums = nums.toSorted((a, b) => a - b);
console.log(nums);       // [3, 1, 2] - unchanged
console.log(sortedNums); // [1, 2, 3] - new array

// Stable sort (guaranteed since ES2019)
// Elements with equal sort values keep original order
const items = [
    { name: "a", value: 1 },
    { name: "b", value: 1 },
    { name: "c", value: 2 }
];
items.sort((a, b) => a.value - b.value);
// a and b stay in original order relative to each other
```

---

## 📝 Implement Array Methods Manually

### Custom map()

```javascript
Array.prototype.myMap = function(callback, thisArg) {
    if (typeof callback !== "function") {
        throw new TypeError(callback + " is not a function");
    }
    
    const result = [];
    for (let i = 0; i < this.length; i++) {
        if (i in this) { // Handle sparse arrays
            result[i] = callback.call(thisArg, this[i], i, this);
        }
    }
    return result;
};

// Test
console.log([1, 2, 3].myMap(x => x * 2)); // [2, 4, 6]
```

### Custom filter()

```javascript
Array.prototype.myFilter = function(callback, thisArg) {
    if (typeof callback !== "function") {
        throw new TypeError(callback + " is not a function");
    }
    
    const result = [];
    for (let i = 0; i < this.length; i++) {
        if (i in this && callback.call(thisArg, this[i], i, this)) {
            result.push(this[i]);
        }
    }
    return result;
};

// Test
console.log([1, 2, 3, 4, 5].myFilter(x => x % 2 === 0)); // [2, 4]
```

### Custom reduce()

```javascript
Array.prototype.myReduce = function(callback, initialValue) {
    if (typeof callback !== "function") {
        throw new TypeError(callback + " is not a function");
    }
    
    let accumulator;
    let startIndex = 0;
    
    if (arguments.length >= 2) {
        accumulator = initialValue;
    } else {
        // Find first non-empty element
        while (startIndex < this.length && !(startIndex in this)) {
            startIndex++;
        }
        
        if (startIndex >= this.length) {
            throw new TypeError("Reduce of empty array with no initial value");
        }
        
        accumulator = this[startIndex];
        startIndex++;
    }
    
    for (let i = startIndex; i < this.length; i++) {
        if (i in this) {
            accumulator = callback(accumulator, this[i], i, this);
        }
    }
    
    return accumulator;
};

// Test
console.log([1, 2, 3, 4, 5].myReduce((acc, val) => acc + val, 0)); // 15
```

---

## 🔧 Other Useful Array Methods

```javascript
// includes
console.log([1, 2, 3].includes(2)); // true
console.log([1, 2, NaN].includes(NaN)); // true (uses SameValueZero)

// indexOf / lastIndexOf (use === comparison)
console.log([1, 2, 3, 2].indexOf(2));     // 1
console.log([1, 2, 3, 2].lastIndexOf(2)); // 3

// at - negative indexing
const arr = [1, 2, 3, 4, 5];
console.log(arr.at(-1));  // 5
console.log(arr.at(-2));  // 4

// fill
console.log(new Array(5).fill(0));        // [0, 0, 0, 0, 0]
console.log([1, 2, 3, 4, 5].fill(0, 2));  // [1, 2, 0, 0, 0]

// copyWithin
const arr2 = [1, 2, 3, 4, 5];
console.log(arr2.copyWithin(0, 3));       // [4, 5, 3, 4, 5]

// concat
console.log([1, 2].concat([3, 4]));       // [1, 2, 3, 4]

// slice (non-mutating)
console.log([1, 2, 3, 4, 5].slice(1, 3)); // [2, 3]

// splice (mutating)
const arr3 = [1, 2, 3, 4, 5];
arr3.splice(2, 1, "inserted");            // removes 1 at index 2, inserts
console.log(arr3);                         // [1, 2, "inserted", 4, 5]

// toSpliced (ES2023, non-mutating)
const arr4 = [1, 2, 3, 4, 5];
const spliced = arr4.toSpliced(2, 1, "new");
console.log(arr4);    // [1, 2, 3, 4, 5] - unchanged
console.log(spliced); // [1, 2, "new", 4, 5]

// with (ES2023, non-mutating replace)
const arr5 = [1, 2, 3];
const replaced = arr5.with(1, "two");
console.log(arr5);     // [1, 2, 3] - unchanged
console.log(replaced); // [1, "two", 3]

// reverse / toReversed
const arr6 = [1, 2, 3];
console.log(arr6.toReversed()); // [3, 2, 1]
console.log(arr6);              // [1, 2, 3] - unchanged
```

---

## 🔬 Practice Problems

```javascript
// Problem 1: Implement flatMap
Array.prototype.myFlatMap = function(callback) {
    return this.map(callback).flat();
};

// Problem 2: Chunk array into smaller arrays
function chunk(arr, size) {
    return arr.reduce((acc, _, i) => {
        if (i % size === 0) {
            acc.push(arr.slice(i, i + size));
        }
        return acc;
    }, []);
}
console.log(chunk([1, 2, 3, 4, 5], 2)); // [[1, 2], [3, 4], [5]]

// Problem 3: Intersection of two arrays
function intersection(arr1, arr2) {
    const set2 = new Set(arr2);
    return arr1.filter(item => set2.has(item));
}

// Problem 4: Group by
function groupBy(arr, key) {
    return arr.reduce((acc, item) => {
        const group = typeof key === "function" ? key(item) : item[key];
        (acc[group] = acc[group] || []).push(item);
        return acc;
    }, {});
}

// Problem 5: Shuffle array (Fisher-Yates)
function shuffle(arr) {
    const result = [...arr];
    for (let i = result.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [result[i], result[j]] = [result[j], result[i]];
    }
    return result;
}
```

---

## ✅ Day 10 Checklist

- [ ] Master map() with all parameters
- [ ] Master filter() for conditional filtering
- [ ] Master reduce() for accumulation
- [ ] Understand some() and every()
- [ ] Use find() and findIndex()
- [ ] Use flat() and flatMap()
- [ ] Understand sort() behavior and compare function
- [ ] Know about toSorted, toReversed, toSpliced (ES2023)
- [ ] Implement map, filter, reduce manually
- [ ] Complete practice problems
