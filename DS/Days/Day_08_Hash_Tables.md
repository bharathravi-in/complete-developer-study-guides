# 📚 DSA 30-Day Tutorial - Day 8

## Day 8: Hash Tables Deep Dive

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand hash function design
- Know collision resolution strategies
- Implement a hash table from scratch
- Solve common hashing problems

---

### 📖 What is a Hash Table?

A hash table (hash map) stores key-value pairs with O(1) average lookup, insert, and delete.

```
Key "apple" → hash("apple") = 42 → index 42 → value

┌────────────────────────────┐
│ Index │  Key    │  Value   │
├───────┼─────────┼──────────┤
│  ...  │         │          │
│  42   │ "apple" │  150     │
│  43   │ "grape" │  200     │
│  ...  │         │          │
└────────────────────────────┘
```

---

### 📖 Hash Function Design

A good hash function:
1. **Deterministic:** Same key always produces same hash
2. **Uniform distribution:** Spreads keys evenly
3. **Fast to compute**

```javascript
// Simple string hash function
function hash(key, tableSize) {
    let hashValue = 0;
    const prime = 31;  // Prime multiplier
    
    for (let i = 0; i < key.length; i++) {
        hashValue = (hashValue * prime + key.charCodeAt(i)) % tableSize;
    }
    
    return hashValue;
}

// Example
hash("apple", 1000)  // → some number 0-999
hash("apple", 1000)  // → same number (deterministic)
```

---

### 📖 Collision Resolution

When two keys hash to the same index.

#### Method 1: Chaining (Separate Chaining)
```
Index 42 → [("apple", 150)] → [("grape", 200)] → null

Each index stores a linked list of entries.
```

```javascript
class HashMapChaining {
    constructor(size = 1000) {
        this.size = size;
        this.buckets = Array.from({ length: size }, () => []);
    }
    
    _hash(key) {
        let h = 0;
        for (let char of String(key)) {
            h = (h * 31 + char.charCodeAt(0)) % this.size;
        }
        return h;
    }
    
    set(key, value) {
        const index = this._hash(key);
        const bucket = this.buckets[index];
        
        // Update if exists
        for (let item of bucket) {
            if (item[0] === key) {
                item[1] = value;
                return;
            }
        }
        
        // Add new
        bucket.push([key, value]);
    }
    
    get(key) {
        const index = this._hash(key);
        const bucket = this.buckets[index];
        
        for (let [k, v] of bucket) {
            if (k === key) return v;
        }
        return undefined;
    }
    
    delete(key) {
        const index = this._hash(key);
        const bucket = this.buckets[index];
        
        for (let i = 0; i < bucket.length; i++) {
            if (bucket[i][0] === key) {
                bucket.splice(i, 1);
                return true;
            }
        }
        return false;
    }
}
```

#### Method 2: Open Addressing (Linear Probing)
```
If index 42 is full, try 43, then 44, then 45...

┌───┬────────┬───────┐
│42 │ "apple"│ 150   │ ← First choice
├───┼────────┼───────┤
│43 │ "grape"│ 200   │ ← Collision, try next
├───┼────────┼───────┤
│44 │        │       │
└───┴────────┴───────┘
```

---

### 📖 Load Factor and Resizing

**Load Factor = n / m** (items / buckets)

When load factor > 0.7, resize the table (usually double).

```javascript
class HashMap {
    constructor() {
        this.size = 16;
        this.count = 0;
        this.buckets = Array.from({ length: this.size }, () => []);
    }
    
    set(key, value) {
        // Check load factor
        if (this.count / this.size > 0.7) {
            this._resize();
        }
        // ... rest of set logic
    }
    
    _resize() {
        const oldBuckets = this.buckets;
        this.size *= 2;
        this.count = 0;
        this.buckets = Array.from({ length: this.size }, () => []);
        
        // Rehash all entries
        for (let bucket of oldBuckets) {
            for (let [key, value] of bucket) {
                this.set(key, value);
            }
        }
    }
}
```

---

### 📖 Two Sum - HashMap Solution

```javascript
function twoSum(nums, target) {
    const map = new Map();  // value → index
    
    for (let i = 0; i < nums.length; i++) {
        const complement = target - nums[i];
        
        if (map.has(complement)) {
            return [map.get(complement), i];
        }
        
        map.set(nums[i], i);
    }
    
    return [-1, -1];
}
```

**Walkthrough:**
```
nums = [2, 7, 11, 15], target = 9

i=0: complement = 9-2 = 7, not in map
     map = {2: 0}

i=1: complement = 9-7 = 2, found at index 0!
     return [0, 1]
```

---

### 📖 Group Anagrams

```javascript
function groupAnagrams(strs) {
    const map = new Map();
    
    for (let str of strs) {
        // Sort string to create key
        const key = [...str].sort().join('');
        
        if (!map.has(key)) {
            map.set(key, []);
        }
        map.get(key).push(str);
    }
    
    return [...map.values()];
}
```

**Alternative key: Character count array**
```javascript
function getKey(str) {
    const count = new Array(26).fill(0);
    for (let char of str) {
        count[char.charCodeAt(0) - 'a'.charCodeAt(0)]++;
    }
    return count.join('#');  // "1#0#0#...#0" for "a"
}
```

---

### 📖 Longest Consecutive Sequence

Find the longest consecutive elements sequence in O(n).

```javascript
function longestConsecutive(nums) {
    const numSet = new Set(nums);
    let maxLength = 0;
    
    for (let num of numSet) {
        // Only start counting from sequence start
        if (!numSet.has(num - 1)) {
            let currentNum = num;
            let currentLength = 1;
            
            while (numSet.has(currentNum + 1)) {
                currentNum++;
                currentLength++;
            }
            
            maxLength = Math.max(maxLength, currentLength);
        }
    }
    
    return maxLength;
}
```

**Key Insight:** Only start counting from the beginning of a sequence (when num-1 doesn't exist).

```
nums = [100, 4, 200, 1, 3, 2]

Set = {100, 4, 200, 1, 3, 2}

num=100: 99 not in set, start here
         100→(101 not in set), length=1

num=4:   3 in set, skip (not start)

num=200: 199 not in set, start here
         200→(201 not in set), length=1

num=1:   0 not in set, start here
         1→2→3→4→(5 not in set), length=4 ✓

num=3:   2 in set, skip
num=2:   1 in set, skip

Answer: 4
```

---

### ✅ Day 8 Checklist
- [ ] Understand hash functions and collision resolution
- [ ] Implement hash table with chaining
- [ ] Complete: Two Sum, Group Anagrams
- [ ] Practice: Longest Consecutive Sequence

---

