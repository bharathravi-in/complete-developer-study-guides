# 📚 DSA 30-Day Tutorial - Day 1

## Day 1: Complexity Analysis & Big O Mastery

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand Big O, Ω, and Θ notation
- Analyze time and space complexity of any algorithm
- Recognize common complexity patterns
- Apply amortized analysis

---

### 📖 What is Algorithm Complexity?

**Algorithm complexity** measures how the runtime or space requirements of an algorithm grow as input size increases.

#### Why Does It Matter?
```
Input Size     O(n)        O(n²)       O(2^n)
─────────────────────────────────────────────
10             10 ops      100 ops      1,024 ops
100            100 ops     10,000 ops   1.27 × 10³⁰ ops
1,000          1,000 ops   1,000,000    Impossible!
```

> **Interview Insight:** FAANG interviewers expect you to state complexity BEFORE coding and optimize BEFORE they ask.

---

### 📖 Big O Notation (Upper Bound)

Big O describes the **worst-case** scenario - the maximum time an algorithm could take.

#### Common Complexity Classes (Fastest to Slowest)

```
┌─────────────┬─────────────────────────────────────────────────────┐
│ Complexity  │ Description & Example                               │
├─────────────┼─────────────────────────────────────────────────────┤
│ O(1)        │ Constant - Array access, hash lookup                │
│ O(log n)    │ Logarithmic - Binary search                         │
│ O(n)        │ Linear - Single loop through array                  │
│ O(n log n)  │ Linearithmic - Merge sort, heap sort                │
│ O(n²)       │ Quadratic - Nested loops, bubble sort               │
│ O(n³)       │ Cubic - Triple nested loops                         │
│ O(2^n)      │ Exponential - Recursive Fibonacci, subsets          │
│ O(n!)       │ Factorial - Generating all permutations             │
└─────────────┴─────────────────────────────────────────────────────┘
```

#### Visual Growth Comparison
```
Time
  │
  │                                          ╱ O(n!)
  │                                       ╱
  │                                    ╱    
  │                                 ╱        O(2^n)
  │                              ╱
  │                           ╱
  │                   ╱──────                O(n²)
  │              ╱───
  │         ╱───                             O(n log n)
  │     ╱───
  │ ╱───────────────────────────────────     O(n)
  │╱─────────────────────────────────────    O(log n)
  │══════════════════════════════════════    O(1)
  └──────────────────────────────────────── Input Size (n)
```

---

### 📖 Analyzing Code Complexity

#### Rule 1: Drop Constants
```javascript
function example(arr) {
    for (let i = 0; i < arr.length; i++) { }    // O(n)
    for (let i = 0; i < arr.length; i++) { }    // O(n)
    for (let i = 0; i < arr.length; i++) { }    // O(n)
}
// Total: O(3n) → O(n) (drop the constant 3)
```

#### Rule 2: Drop Lower Order Terms
```javascript
function example(arr) {
    for (let i = 0; i < arr.length; i++) {          // O(n)
        for (let j = 0; j < arr.length; j++) { }    // O(n)
    }
    for (let i = 0; i < arr.length; i++) { }        // O(n)
}
// Total: O(n²) + O(n) → O(n²) (n² dominates n)
```

#### Rule 3: Different Inputs = Different Variables
```javascript
function example(arr1, arr2) {
    for (let i = 0; i < arr1.length; i++) { }       // O(a)
    for (let j = 0; j < arr2.length; j++) { }       // O(b)
}
// Total: O(a + b), NOT O(n)!
```

#### Rule 4: Nested Loops Multiply
```javascript
function example(arr1, arr2) {
    for (let i = 0; i < arr1.length; i++) {         // O(a)
        for (let j = 0; j < arr2.length; j++) { }   // O(b)
    }
}
// Total: O(a × b)
```

---

### 📖 Space Complexity

Space complexity measures the **extra memory** an algorithm uses (excluding input).

```javascript
// O(1) Space - Constant extra space
function findMax(arr) {
    let max = arr[0];  // Just one variable
    for (let num of arr) {
        if (num > max) max = num;
    }
    return max;
}

// O(n) Space - Linear extra space
function copyArray(arr) {
    const copy = [];   // New array grows with input
    for (let num of arr) {
        copy.push(num);
    }
    return copy;
}

// O(n) Space - Recursion stack
function factorial(n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);  // n stack frames
}
```

---

### 📖 Amortized Analysis

**Amortized analysis** averages the cost over a sequence of operations.

#### Example: Dynamic Array (ArrayList)

```javascript
class DynamicArray {
    constructor() {
        this.data = new Array(1);
        this.size = 0;
        this.capacity = 1;
    }
    
    push(element) {
        if (this.size === this.capacity) {
            this._resize();  // Expensive: O(n)
        }
        this.data[this.size] = element;  // Cheap: O(1)
        this.size++;
    }
    
    _resize() {
        this.capacity *= 2;  // Double the size
        const newData = new Array(this.capacity);
        for (let i = 0; i < this.size; i++) {
            newData[i] = this.data[i];
        }
        this.data = newData;
    }
}
```

**Analysis:**
```
Push sequence: 1, 2, 3, 4, 5, 6, 7, 8, 9 (n=9 inserts)

Insert 1: copy 0 elements (capacity 1→2)
Insert 2: copy 1 element  (capacity 2→4)
Insert 3: no resize
Insert 4: copy 3 elements (capacity 4→8)
Insert 5-8: no resize
Insert 9: copy 8 elements (capacity 8→16)

Total copies: 0 + 1 + 3 + 8 = 12
For n insertions: ~2n copies total
Average per insertion: 2n/n = O(1) amortized
```

---

### 📖 Common Complexity Patterns to Recognize

| Pattern | Complexity | Code Signature |
|---------|------------|----------------|
| Simple loop | O(n) | `for (let i = 0; i < n; i++)` |
| Nested loops | O(n²) | `for i { for j { } }` |
| Loop dividing by 2 | O(log n) | `while (n > 0) { n /= 2; }` |
| Two pointers | O(n) | `while (left < right)` |
| Sorting then scan | O(n log n) | `arr.sort(); for...` |
| Recursion × 2 calls | O(2^n) | `f(n-1) + f(n-1)` |

---

### 💻 Practice Exercises

**Exercise 1:** What's the complexity?
```javascript
function mystery1(n) {
    for (let i = 1; i < n; i *= 2) {
        console.log(i);
    }
}
// Answer: O(log n) - i doubles each iteration
```

**Exercise 2:** What's the complexity?
```javascript
function mystery2(n) {
    for (let i = 0; i < n; i++) {
        for (let j = i; j < n; j++) {
            console.log(i, j);
        }
    }
}
// Answer: O(n²) - Inner loop runs n + (n-1) + (n-2) + ... + 1 = n(n+1)/2
```

**Exercise 3:** What's the complexity?
```javascript
function mystery3(arr) {
    const seen = new Set();
    for (let num of arr) {
        if (seen.has(num)) return true;
        seen.add(num);
    }
    return false;
}
// Answer: O(n) time, O(n) space
```

---

### ✅ Day 1 Checklist
- [ ] Understand Big O, Ω, Θ notation
- [ ] Memorize common complexity classes
- [ ] Practice analyzing 5+ code snippets
- [ ] Understand amortized analysis
- [ ] Complete LeetCode #217 (Contains Duplicate)

---

