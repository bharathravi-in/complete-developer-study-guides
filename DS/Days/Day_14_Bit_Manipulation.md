# 📚 DSA 30-Day Tutorial - Day 14

## Day 14: Bit Manipulation

### 🎯 Learning Objectives
By the end of this day, you will:
- Master bitwise operators
- Know common bit tricks
- Solve bit manipulation problems

---

### 📖 Bitwise Operators

```
AND (&):    1 & 1 = 1, else 0
OR  (|):    0 | 0 = 0, else 1
XOR (^):    same = 0, different = 1
NOT (~):    flips all bits
Left Shift (<<):   n << k = n × 2^k
Right Shift (>>):  n >> k = n ÷ 2^k
```

```javascript
// Examples
5 & 3    // 101 & 011 = 001 = 1
5 | 3    // 101 | 011 = 111 = 7
5 ^ 3    // 101 ^ 011 = 110 = 6
~5       // ...11111010 = -6 (two's complement)
5 << 1   // 101 << 1 = 1010 = 10
5 >> 1   // 101 >> 1 = 10 = 2
```

---

### 📖 Essential Bit Tricks

```javascript
// Check if number is odd
const isOdd = n => (n & 1) === 1;

// Check if power of 2
const isPowerOfTwo = n => n > 0 && (n & (n - 1)) === 0;

// Get bit at position i (0-indexed from right)
const getBit = (n, i) => (n >> i) & 1;

// Set bit at position i to 1
const setBit = (n, i) => n | (1 << i);

// Clear bit at position i (set to 0)
const clearBit = (n, i) => n & ~(1 << i);

// Toggle bit at position i
const toggleBit = (n, i) => n ^ (1 << i);

// Clear lowest set bit
const clearLowestBit = n => n & (n - 1);

// Get lowest set bit
const lowestSetBit = n => n & (-n);

// Count set bits (Brian Kernighan)
function countSetBits(n) {
    let count = 0;
    while (n) {
        n &= (n - 1);  // Clear lowest set bit
        count++;
    }
    return count;
}
```

---

### 📖 Single Number (XOR Property)

XOR properties:
- a ^ a = 0 (same numbers cancel)
- a ^ 0 = a
- a ^ b ^ a = b (order doesn't matter)

```javascript
function singleNumber(nums) {
    return nums.reduce((xor, num) => xor ^ num, 0);
}

// Example: [4, 1, 2, 1, 2]
// 4 ^ 1 ^ 2 ^ 1 ^ 2
// = 4 ^ (1 ^ 1) ^ (2 ^ 2)
// = 4 ^ 0 ^ 0
// = 4
```

---

### 📖 Generate Subsets Using Bits

Each subset corresponds to a binary number where bit i indicates whether element i is included.

```javascript
function subsets(nums) {
    const result = [];
    const n = nums.length;
    
    // 2^n possible subsets
    for (let mask = 0; mask < (1 << n); mask++) {
        const subset = [];
        for (let i = 0; i < n; i++) {
            if (mask & (1 << i)) {
                subset.push(nums[i]);
            }
        }
        result.push(subset);
    }
    
    return result;
}

// nums = [1, 2, 3]
// mask=0 (000): []
// mask=1 (001): [1]
// mask=2 (010): [2]
// mask=3 (011): [1,2]
// mask=4 (100): [3]
// mask=5 (101): [1,3]
// mask=6 (110): [2,3]
// mask=7 (111): [1,2,3]
```

---

### ✅ Day 14 Checklist
- [ ] Know all bitwise operators
- [ ] Memorize common bit tricks
- [ ] Complete: Single Number, Number of 1 Bits
- [ ] Practice: Counting Bits, Subsets with bitmask

---

# End of Week 2

**Week 2 Summary:**
- Day 8: Hash Tables
- Day 9: String Algorithms (KMP, Z)
- Day 10: Binary Trees
- Day 11: Binary Search Trees
- Day 12: Advanced Trees
- Day 13: Heaps
- Day 14: Bit Manipulation

---

# 🗓️ WEEK 3: Graphs & Dynamic Programming

---

