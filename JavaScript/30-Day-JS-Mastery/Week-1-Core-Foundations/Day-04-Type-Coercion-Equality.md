# Day 4: Type Coercion & Equality

## 🎯 Learning Objectives
- Deep understanding of == vs ===
- Master the Abstract Equality Algorithm
- Understand isNaN vs Number.isNaN
- Learn Object.is and SameValueZero
- Predict coercion behavior accurately

---

## 📚 == vs === (Equality Operators)

### Strict Equality (===)
No type coercion - compares both value AND type.

```javascript
// Same type, same value
console.log(5 === 5);           // true
console.log("hello" === "hello"); // true

// Different types - always false
console.log(5 === "5");         // false
console.log(0 === false);       // false
console.log(null === undefined); // false

// Object comparison (reference)
const obj1 = { a: 1 };
const obj2 = { a: 1 };
const obj3 = obj1;

console.log(obj1 === obj2);     // false (different references)
console.log(obj1 === obj3);     // true (same reference)

// Special cases
console.log(NaN === NaN);       // false (NaN is not equal to itself!)
console.log(+0 === -0);         // true (different, but === says equal)
```

### Loose Equality (==)
Performs type coercion before comparison.

```javascript
// Type coercion in action
console.log(5 == "5");          // true (string coerced to number)
console.log(0 == false);        // true (boolean coerced to number)
console.log(null == undefined); // true (special case)
console.log("" == 0);           // true (empty string → 0)

// Arrays and objects
console.log([1] == 1);          // true ([1] → "1" → 1)
console.log([1,2] == "1,2");    // true ([1,2] → "1,2")
console.log({} == "[object Object]"); // true ({} → "[object Object]")

// null and undefined special behavior
console.log(null == 0);         // false (null only == null or undefined)
console.log(undefined == 0);    // false
console.log(null == false);     // false
```

---

## 🔢 Abstract Equality Algorithm

The `==` operator follows the ECMAScript Abstract Equality Comparison Algorithm:

```
╔═══════════════════════════════════════════════════════════════════╗
║        ABSTRACT EQUALITY ALGORITHM (x == y)                        ║
╠═══════════════════════════════════════════════════════════════════╣
║                                                                    ║
║  1. If Type(x) === Type(y):                                       ║
║     → Return x === y                                              ║
║                                                                    ║
║  2. If x is null and y is undefined (or vice versa):              ║
║     → Return true                                                  ║
║                                                                    ║
║  3. If one is Number and other is String:                         ║
║     → Convert String to Number, then compare                      ║
║                                                                    ║
║  4. If one is Boolean:                                            ║
║     → Convert Boolean to Number (true→1, false→0)                 ║
║     → Then compare                                                 ║
║                                                                    ║
║  5. If one is Object and other is primitive:                      ║
║     → Convert Object using ToPrimitive (valueOf, toString)        ║
║     → Then compare                                                 ║
║                                                                    ║
║  6. Otherwise:                                                     ║
║     → Return false                                                 ║
║                                                                    ║
╚═══════════════════════════════════════════════════════════════════╝
```

### Algorithm Examples

```javascript
// Example 1: "5" == 5
// Step 3: Convert "5" to Number → 5
// Then: 5 === 5 → true

// Example 2: true == 1
// Step 4: Convert true to Number → 1
// Then: 1 === 1 → true

// Example 3: true == "1"
// Step 4: Convert true to Number → 1
// Now: 1 == "1"
// Step 3: Convert "1" to Number → 1
// Then: 1 === 1 → true

// Example 4: [] == false
// Step 4: Convert false to Number → 0
// Now: [] == 0
// Step 5: Convert [] to primitive → "" (empty string)
// Now: "" == 0
// Step 3: Convert "" to Number → 0
// Then: 0 === 0 → true

// Example 5: [1] == true
// Step 4: Convert true to Number → 1
// Now: [1] == 1
// Step 5: Convert [1] to primitive → "1"
// Now: "1" == 1
// Step 3: Convert "1" to Number → 1
// Then: 1 === 1 → true

// Example 6: {} == "[object Object]"
// Step 5: Convert {} to primitive
// ({}).valueOf() → {} (not primitive, try toString)
// ({}).toString() → "[object Object]"
// Now: "[object Object]" == "[object Object]"
// Step 1: Same type, compare → true
```

### ToPrimitive Conversion

```javascript
// ToPrimitive prefers valueOf for numbers, toString for strings

const obj = {
    valueOf() {
        console.log("valueOf called");
        return 42;
    },
    toString() {
        console.log("toString called");
        return "hello";
    }
};

// When comparing with number, valueOf is tried first
console.log(obj == 42);      // true (valueOf called)
console.log(obj == "42");    // true (valueOf → 42, then 42 == "42")

// String conversion uses toString
console.log(String(obj));    // "hello" (toString called)

// Arrays use toString (valueOf returns the array itself)
const arr = [1, 2, 3];
console.log(arr.toString()); // "1,2,3"
console.log(arr == "1,2,3"); // true
```

---

## 🚫 isNaN vs Number.isNaN

### The Problem with isNaN()

```javascript
// isNaN() coerces the argument to Number first
console.log(isNaN("hello"));     // true ("hello" → NaN)
console.log(isNaN("123"));       // false ("123" → 123)
console.log(isNaN(undefined));   // true (undefined → NaN)
console.log(isNaN({}));          // true ({} → NaN)
console.log(isNaN("NaN"));       // true ("NaN" → NaN)

// These are clearly NOT NaN, but isNaN says true!
console.log(isNaN("hello"));     // true - wrong!
console.log(isNaN(undefined));   // true - misleading!
```

### Number.isNaN() - The Correct Way

```javascript
// Number.isNaN() does NOT coerce - checks if value IS NaN
console.log(Number.isNaN(NaN));         // true
console.log(Number.isNaN("hello"));     // false (string, not NaN)
console.log(Number.isNaN(undefined));   // false (undefined, not NaN)
console.log(Number.isNaN({}));          // false (object, not NaN)
console.log(Number.isNaN("NaN"));       // false (string, not NaN)

// Only actual NaN returns true
console.log(Number.isNaN(0/0));         // true
console.log(Number.isNaN(Math.sqrt(-1))); // true

// Comparison
const values = [NaN, "NaN", undefined, {}, "hello", 123];

values.forEach(v => {
    console.log(`${String(v).padEnd(12)} | isNaN: ${isNaN(v).toString().padEnd(5)} | Number.isNaN: ${Number.isNaN(v)}`);
});
/*
Output:
NaN          | isNaN: true  | Number.isNaN: true
NaN          | isNaN: true  | Number.isNaN: false
undefined    | isNaN: true  | Number.isNaN: false
[object Obj] | isNaN: true  | Number.isNaN: false
hello        | isNaN: true  | Number.isNaN: false
123          | isNaN: false | Number.isNaN: false
*/
```

### Why NaN !== NaN

```javascript
// NaN is the only value in JavaScript that is not equal to itself
console.log(NaN === NaN); // false
console.log(NaN == NaN);  // false

// This is by IEEE 754 floating-point standard design
// NaN represents "Not a Number" - an undefined/unrepresentable value
// Two undefined values cannot be said to be equal

// How to check for NaN
const value = NaN;

// Method 1: Number.isNaN (recommended)
if (Number.isNaN(value)) {
    console.log("It's NaN");
}

// Method 2: Self-inequality check (clever but not recommended)
if (value !== value) {
    console.log("It's NaN");
}

// Method 3: Object.is
if (Object.is(value, NaN)) {
    console.log("It's NaN");
}
```

---

## 🎯 Object.is

`Object.is()` performs SameValue comparison - like === but handles edge cases:

```javascript
// Object.is vs ===

// Where they're the same
console.log(Object.is(5, 5));               // true
console.log(5 === 5);                       // true

console.log(Object.is("hello", "hello"));   // true
console.log("hello" === "hello");           // true

console.log(Object.is(null, null));         // true
console.log(null === null);                 // true

// Where they DIFFER

// 1. NaN comparison
console.log(Object.is(NaN, NaN));           // true ✓
console.log(NaN === NaN);                   // false

// 2. -0 and +0 comparison
console.log(Object.is(-0, +0));             // false ✓
console.log(-0 === +0);                     // true

console.log(Object.is(0, -0));              // false ✓
console.log(0 === -0);                      // true

// Why -0 matters
console.log(1 / +0);    // Infinity
console.log(1 / -0);    // -Infinity
// They are mathematically different!

// Comparison table
/*
═══════════════════════════════════════════════════════════
              │    ==    │    ===   │  Object.is
─────────────────────────────────────────────────────────
NaN, NaN      │   false  │   false  │    true
+0, -0        │   true   │   true   │    false
5, "5"        │   true   │   false  │    false
null, undef   │   true   │   false  │    false
═══════════════════════════════════════════════════════════
*/
```

---

## 🔄 SameValueZero

`SameValueZero` is used by Map, Set, includes(), and other built-in methods:

```javascript
// SameValueZero is like Object.is, but treats -0 and +0 as equal

// Where it's used:

// 1. Array.includes()
const arr = [NaN, 0];
console.log(arr.includes(NaN));    // true (SameValueZero)
console.log(arr.indexOf(NaN));     // -1 (uses ===)

// 2. Map keys
const map = new Map();
map.set(NaN, "value");
console.log(map.get(NaN));         // "value" (found!)

map.set(-0, "negative zero");
console.log(map.get(+0));          // "negative zero" (treats as same)

// 3. Set values
const set = new Set();
set.add(NaN);
console.log(set.has(NaN));         // true

set.add(-0);
console.log(set.has(+0));          // true (treats as same)

/*
═══════════════════════════════════════════════════════════
ALGORITHM COMPARISON:
═══════════════════════════════════════════════════════════

              │ NaN === NaN │ -0 === +0 │ Type Coercion
─────────────────────────────────────────────────────────
==            │    false    │   true    │     YES
===           │    false    │   true    │     NO
Object.is     │    true     │   false   │     NO
SameValueZero │    true     │   true    │     NO
═══════════════════════════════════════════════════════════
*/
```

---

## ❓ Interview Questions & Answers

### Q1: Why is [] == false true?

```javascript
console.log([] == false); // true

// Step-by-step:
// 1. [] == false
// 2. Step 4: false → 0, now: [] == 0
// 3. Step 5: [].valueOf() = [], not primitive
//    [].toString() = "", now: "" == 0
// 4. Step 3: "" → 0, now: 0 == 0
// 5. Step 1: same type, compare: 0 === 0 → true

// More tricky ones:
console.log([] == ![]);    // true! ([] == false)
console.log([] == []);     // false (different references)
console.log({} == {});     // false (different references)
console.log({} == !{});    // false ({} == false → "[object Object]" == 0 → NaN == 0 → false)
```

### Q2: Why is NaN !== NaN?

**Answer**: NaN (Not-a-Number) represents an undefined or unrepresentable numeric value. According to IEEE 754 floating-point standard, NaN is not equal to anything, including itself, because two undefined values cannot be considered equal. Use `Number.isNaN()` or `Object.is()` to properly check for NaN.

### Q3: What's the difference between == and ===?

**Answer**:
- `===` (Strict Equality): Compares type AND value without coercion
- `==` (Loose Equality): Performs type coercion before comparison following the Abstract Equality Algorithm

Best practice: Always use `===` unless you specifically need type coercion.

### Q4: Explain type coercion rules

```javascript
// String + Number = String (concatenation)
console.log("5" + 3);      // "53"
console.log(3 + "5");      // "35"

// Other operators convert to Number
console.log("5" - 3);      // 2
console.log("5" * 3);      // 15
console.log("5" / 1);      // 5

// Boolean to Number
console.log(true + true);  // 2
console.log(true + false); // 1

// null and undefined
console.log(null + 1);     // 1 (null → 0)
console.log(undefined + 1); // NaN (undefined → NaN)

// Arrays
console.log([1] + [2]);    // "12" (array → string)
console.log(+[]);          // 0 ([] → "" → 0)
console.log(+[1]);         // 1 ([1] → "1" → 1)
console.log(+[1,2]);       // NaN ([1,2] → "1,2" → NaN)
```

---

## 🔬 Tricky Output Questions

```javascript
// Question 1
console.log([] + []);      // "" ([] → "", "" + "" = "")
console.log([] + {});      // "[object Object]"
console.log({} + []);      // "[object Object]" or 0 (depends on context!)
// In console, {} is parsed as empty block, so +[] = 0
// In expression, {} + [] = "[object Object]"

// Question 2
console.log(true + true + true);   // 3
console.log(true - true);          // 0
console.log(true == 1);            // true
console.log(true === 1);           // false

// Question 3
console.log((!+[]+[]+![]).length); // 9
// Step by step:
// !+[] → !0 → true
// true + [] → "true"
// "true" + ![] → "true" + false → "truefalse"
// "truefalse".length → 9

// Question 4
console.log(9999999999999999);     // 10000000000000000 (precision loss)
console.log(0.1 + 0.2 === 0.3);    // false (floating point precision)
console.log(0.1 + 0.2);            // 0.30000000000000004

// Question 5
console.log(typeof null);          // "object" (historical bug)
console.log(null instanceof Object); // false

// Question 6
console.log("2" + "2" - "2");      // 20
// "2" + "2" = "22"
// "22" - "2" = 22 - 2 = 20

// Question 7
console.log([10] == 10);           // true
console.log([10] === 10);          // false

// Question 8
console.log(Boolean([]));          // true (array exists)
console.log(Boolean({}));          // true (object exists)
console.log(Boolean(""));          // false (empty string)
console.log(Boolean(0));           // false

// Question 9
console.log(1 < 2 < 3);            // true (1 < 2 = true, true < 3 = 1 < 3 = true)
console.log(3 > 2 > 1);            // false (3 > 2 = true, true > 1 = 1 > 1 = false)

// Question 10
console.log("b" + "a" + + "a" + "a"); // "baNaNa"
// "b" + "a" = "ba"
// +"a" = NaN (unary + on "a")
// "ba" + NaN = "baNaN"
// "baNaN" + "a" = "baNaNa"
```

---

## 📋 Coercion Cheat Sheet

```javascript
/*
═══════════════════════════════════════════════════════════
TO NUMBER CONVERSION (Number() or unary +):
═══════════════════════════════════════════════════════════
undefined   → NaN
null        → 0
true        → 1
false       → 0
""          → 0
"  "        → 0 (whitespace)
"123"       → 123
"12.3"      → 12.3
"123abc"    → NaN
[]          → 0 ([] → "" → 0)
[1]         → 1 ([1] → "1" → 1)
[1,2]       → NaN
{}          → NaN
function    → NaN

═══════════════════════════════════════════════════════════
TO STRING CONVERSION (String() or + ""):
═══════════════════════════════════════════════════════════
undefined   → "undefined"
null        → "null"
true        → "true"
false       → "false"
123         → "123"
NaN         → "NaN"
[]          → ""
[1,2,3]     → "1,2,3"
{}          → "[object Object]"
function    → "function() {...}"

═══════════════════════════════════════════════════════════
TO BOOLEAN CONVERSION (Boolean() or !!):
═══════════════════════════════════════════════════════════
FALSY VALUES (convert to false):
- false
- 0 and -0
- ""
- null
- undefined
- NaN

TRUTHY (everything else):
- {} (empty object)
- [] (empty array)
- "0" (string zero)
- "false" (string false)
- function
*/
```

---

## ✅ Day 4 Checklist

- [ ] Understand == vs === completely
- [ ] Master the Abstract Equality Algorithm
- [ ] Know ToPrimitive conversion (valueOf, toString)
- [ ] Understand isNaN() limitations
- [ ] Use Number.isNaN() correctly
- [ ] Know why NaN !== NaN
- [ ] Understand Object.is() and when to use it
- [ ] Know SameValueZero algorithm
- [ ] Master type coercion rules
- [ ] Be able to predict tricky output questions
