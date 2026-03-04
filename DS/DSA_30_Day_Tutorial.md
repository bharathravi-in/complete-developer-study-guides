# 📚 30-Day DSA Complete Tutorial Guide

> **A comprehensive learning guide with concepts, visualizations, and implementations**  
> **Target:** Senior Engineers preparing for FAANG interviews  
> **Language:** JavaScript/Node.js

---

# 🗓️ WEEK 1: Foundations & Array Mastery

---

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

## Day 2: Two Pointer Pattern

### 🎯 Learning Objectives
By the end of this day, you will:
- Master the two pointer technique
- Know when to use two pointers vs other approaches
- Implement 4 different two pointer patterns

---

### 📖 What is the Two Pointer Technique?

Two pointers is a technique where we use two variables to traverse a data structure (usually an array) simultaneously.

#### When to Use Two Pointers?
```
✓ Sorted arrays (searching for pairs)
✓ Removing duplicates in-place
✓ Reversing arrays/strings
✓ Finding palindromes
✓ Merging sorted arrays
✓ Linked list cycle detection
```

---

### 📖 Pattern 1: Opposite Direction (Converging)

Two pointers start at opposite ends and move toward each other.

```
Array: [1, 3, 5, 7, 9, 11]
        ↑              ↑
       left          right
       
Move closer based on condition until left >= right
```

#### Example: Two Sum II (Sorted Array)

**Problem:** Find two numbers that add up to target in a sorted array.

```javascript
function twoSumSorted(numbers, target) {
    let left = 0;
    let right = numbers.length - 1;
    
    while (left < right) {
        const sum = numbers[left] + numbers[right];
        
        if (sum === target) {
            return [left + 1, right + 1];  // 1-indexed
        } else if (sum < target) {
            // Need larger sum → move left pointer right
            left++;
        } else {
            // Need smaller sum → move right pointer left
            right--;
        }
    }
    
    return [-1, -1];  // No solution found
}
```

**Walkthrough:**
```
numbers = [2, 7, 11, 15], target = 9

Step 1: left=0, right=3
        [2, 7, 11, 15]
         ↑          ↑
        sum = 2 + 15 = 17 > 9 → right--

Step 2: left=0, right=2
        [2, 7, 11, 15]
         ↑      ↑
        sum = 2 + 11 = 13 > 9 → right--

Step 3: left=0, right=1
        [2, 7, 11, 15]
         ↑  ↑
        sum = 2 + 7 = 9 = target ✓
        
Return [1, 2] (1-indexed)
```

#### Why It Works
- Array is sorted
- If sum > target, we need smaller numbers → move right pointer left
- If sum < target, we need larger numbers → move left pointer right
- We never skip a valid pair because we explore all possibilities

---

### 📖 Pattern 2: Same Direction (Slow/Fast)

Both pointers move in the same direction at different speeds.

```
Array: [0, 1, 0, 3, 12]
        ↑
      slow
        ↑
       fast
       
Fast scans, slow marks position for valid elements
```

#### Example: Move Zeroes

**Problem:** Move all 0's to the end while maintaining order of non-zero elements.

```javascript
function moveZeroes(nums) {
    let slow = 0;  // Position for next non-zero
    
    // Fast pointer scans entire array
    for (let fast = 0; fast < nums.length; fast++) {
        if (nums[fast] !== 0) {
            // Swap non-zero to slow position
            [nums[slow], nums[fast]] = [nums[fast], nums[slow]];
            slow++;
        }
    }
    
    return nums;
}
```

**Walkthrough:**
```
nums = [0, 1, 0, 3, 12]

Initial: slow=0, fast=0
         [0, 1, 0, 3, 12]
          ↑
         s,f
         nums[0]=0, skip

fast=1:  [0, 1, 0, 3, 12]
          ↑  ↑
          s  f
         nums[1]=1≠0, swap nums[0]↔nums[1]
         [1, 0, 0, 3, 12], slow=1

fast=2:  [1, 0, 0, 3, 12]
             ↑  ↑
             s  f
         nums[2]=0, skip

fast=3:  [1, 0, 0, 3, 12]
             ↑     ↑
             s     f
         nums[3]=3≠0, swap nums[1]↔nums[3]
         [1, 3, 0, 0, 12], slow=2

fast=4:  [1, 3, 0, 0, 12]
                ↑      ↑
                s      f
         nums[4]=12≠0, swap nums[2]↔nums[4]
         [1, 3, 12, 0, 0], slow=3

Final: [1, 3, 12, 0, 0] ✓
```

---

### 📖 Pattern 3: Remove Duplicates (In-Place)

Keep only unique elements in sorted array.

```javascript
function removeDuplicates(nums) {
    if (nums.length === 0) return 0;
    
    let slow = 0;  // Last unique element position
    
    for (let fast = 1; fast < nums.length; fast++) {
        if (nums[fast] !== nums[slow]) {
            slow++;
            nums[slow] = nums[fast];
        }
    }
    
    return slow + 1;  // Length of unique elements
}
```

**Walkthrough:**
```
nums = [1, 1, 2, 2, 3]

Initial: slow=0
         [1, 1, 2, 2, 3]
          ↑

fast=1:  nums[1]=1 === nums[0]=1, skip
fast=2:  nums[2]=2 !== nums[0]=1
         slow++, nums[1]=2
         [1, 2, 2, 2, 3]
             ↑
fast=3:  nums[3]=2 === nums[1]=2, skip
fast=4:  nums[4]=3 !== nums[1]=2
         slow++, nums[2]=3
         [1, 2, 3, 2, 3]
                ↑

Return slow+1 = 3 (first 3 elements are unique)
```

---

### 📖 Pattern 4: Container With Most Water

Finding the maximum area between vertical lines.

```javascript
function maxArea(height) {
    let left = 0;
    let right = height.length - 1;
    let maxWater = 0;
    
    while (left < right) {
        // Width × minimum height
        const width = right - left;
        const minHeight = Math.min(height[left], height[right]);
        const area = width * minHeight;
        
        maxWater = Math.max(maxWater, area);
        
        // Move the shorter line (it's limiting our area)
        if (height[left] < height[right]) {
            left++;
        } else {
            right--;
        }
    }
    
    return maxWater;
}
```

**Visual Explanation:**
```
height = [1, 8, 6, 2, 5, 4, 8, 3, 7]

    8 |    █              █
    7 |    █              █     █
    6 |    █  █           █     █
    5 |    █  █     █     █     █
    4 |    █  █     █  █  █     █
    3 |    █  █     █  █  █  █  █
    2 |    █  █  █  █  █  █  █  █
    1 | █  █  █  █  █  █  █  █  █
      └─────────────────────────────
        0  1  2  3  4  5  6  7  8
        ↑                       ↑
       left                   right
       
Area = min(1,7) × (8-0) = 1 × 8 = 8
Move left (shorter)

Continue until left >= right
Best: left=1, right=8, area = min(8,7) × 7 = 49
```

---

### 📖 Pattern 5: 3Sum (Combining Patterns)

Find all unique triplets that sum to zero.

```javascript
function threeSum(nums) {
    nums.sort((a, b) => a - b);  // Sort first!
    const result = [];
    
    for (let i = 0; i < nums.length - 2; i++) {
        // Skip duplicates for i
        if (i > 0 && nums[i] === nums[i - 1]) continue;
        
        // Two pointer for remaining two numbers
        let left = i + 1;
        let right = nums.length - 1;
        const target = -nums[i];  // Need left + right = -nums[i]
        
        while (left < right) {
            const sum = nums[left] + nums[right];
            
            if (sum === target) {
                result.push([nums[i], nums[left], nums[right]]);
                
                // Skip duplicates
                while (left < right && nums[left] === nums[left + 1]) left++;
                while (left < right && nums[right] === nums[right - 1]) right--;
                
                left++;
                right--;
            } else if (sum < target) {
                left++;
            } else {
                right--;
            }
        }
    }
    
    return result;
}
```

---

### 📖 Two Pointer Decision Guide

```
┌────────────────────────────────────────────────────────────────┐
│                    Is array SORTED?                            │
│                           │                                    │
│                    ┌──────┴──────┐                             │
│                   YES            NO                            │
│                    │              │                            │
│         ┌──────────┴────────┐    │                             │
│     Searching for          In-place   → Sort first OR         │
│     pairs/triplets?        modification?  use HashMap          │
│           │                     │                              │
│    Use OPPOSITE          Use SAME                              │
│    direction             direction                             │
│    (left, right)         (slow, fast)                          │
└────────────────────────────────────────────────────────────────┘
```

---

### 💻 Practice Problems

| Problem | Pattern | Key Insight |
|---------|---------|-------------|
| Two Sum II | Opposite | Sort enables binary decisions |
| 3Sum | Opposite + Loop | Fix one, two-pointer rest |
| Container With Most Water | Opposite | Move shorter line |
| Remove Duplicates | Same Direction | Slow marks valid position |
| Move Zeroes | Same Direction | Swap non-zeros forward |
| Valid Palindrome | Opposite | Compare from both ends |

---

### ✅ Day 2 Checklist
- [ ] Understand opposite direction pattern
- [ ] Understand same direction pattern
- [ ] Know when to use each pattern
- [ ] Complete: Two Sum II, Container With Most Water, 3Sum
- [ ] Practice: Remove Duplicates, Move Zeroes

---

## Day 3: Sliding Window Pattern

### 🎯 Learning Objectives
By the end of this day, you will:
- Master fixed and variable size sliding windows
- Know how to maintain window state
- Solve substring/subarray optimization problems

---

### 📖 What is the Sliding Window Technique?

The sliding window technique maintains a "window" that slides through an array/string to find a contiguous subarray/substring meeting certain criteria.

#### When to Use Sliding Window?
```
✓ "Contiguous subarray/substring" in the problem
✓ "Maximum/minimum sum of k elements"
✓ "Longest substring with condition"
✓ "Smallest window containing..."
✓ Looking for a range that satisfies a condition
```

---

### 📖 Type 1: Fixed Size Window

Window size is given (k elements).

```
Array: [1, 3, 2, 6, -1, 4, 1, 8, 2], k=3

Window 1: [1, 3, 2] → sum = 6
           ~~~~~~~~
Window 2: [3, 2, 6] → sum = 11
              ~~~~~~~~
Window 3: [2, 6, -1] → sum = 7
                 ~~~~~~~~
...slide until end
```

#### Example: Maximum Sum of K Consecutive Elements

```javascript
function maxSumSubarray(arr, k) {
    if (arr.length < k) return null;
    
    // Calculate sum of first window
    let windowSum = 0;
    for (let i = 0; i < k; i++) {
        windowSum += arr[i];
    }
    
    let maxSum = windowSum;
    
    // Slide the window
    for (let i = k; i < arr.length; i++) {
        // Add new element, remove old element
        windowSum = windowSum + arr[i] - arr[i - k];
        maxSum = Math.max(maxSum, windowSum);
    }
    
    return maxSum;
}
```

**Why O(n) and not O(n×k)?**
```
Naive: Recalculate sum for each window → O(n × k)
Smart: Add new element, subtract old element → O(n)

Window [1,3,2] sum = 6
Slide: subtract 1, add 6
Window [3,2,6] sum = 6 - 1 + 6 = 11
```

---

### 📖 Type 2: Variable Size Window (Expand + Contract)

Window size varies based on condition. This is the more common pattern.

```
General Template:

left   right
  ↓     ↓
  [a, b, c, d, e, f, g]
      window
      
1. Expand: Move right pointer to include more elements
2. Contract: Move left pointer when window becomes invalid
3. Update result when window is valid
```

#### Template Code

```javascript
function slidingWindowTemplate(s) {
    let left = 0;
    let result = 0;  // or Infinity for minimum problems
    const windowState = {};  // Track window contents
    
    for (let right = 0; right < s.length; right++) {
        // 1. EXPAND: Add s[right] to window
        // Update windowState with s[right]
        
        // 2. CONTRACT: While window is invalid
        while (/* window is invalid */) {
            // Remove s[left] from window
            // Update windowState
            left++;
        }
        
        // 3. UPDATE: Window is now valid
        result = Math.max(result, right - left + 1);
    }
    
    return result;
}
```

---

### 📖 Example: Longest Substring Without Repeating Characters

**Problem:** Find the length of the longest substring without repeating characters.

```javascript
function lengthOfLongestSubstring(s) {
    const charIndex = new Map();  // char → last seen index
    let left = 0;
    let maxLength = 0;
    
    for (let right = 0; right < s.length; right++) {
        const char = s[right];
        
        // If char seen before AND within current window
        if (charIndex.has(char) && charIndex.get(char) >= left) {
            // Move left past the duplicate
            left = charIndex.get(char) + 1;
        }
        
        // Update last seen index
        charIndex.set(char, right);
        
        // Update max length
        maxLength = Math.max(maxLength, right - left + 1);
    }
    
    return maxLength;
}
```

**Walkthrough:**
```
s = "abcabcbb"

right=0, char='a': window="a", left=0, max=1
         charIndex: {a:0}
         
right=1, char='b': window="ab", left=0, max=2
         charIndex: {a:0, b:1}
         
right=2, char='c': window="abc", left=0, max=3
         charIndex: {a:0, b:1, c:2}
         
right=3, char='a': 'a' at index 0 >= left(0)!
         Move left = 0 + 1 = 1
         window="bca", max=3
         charIndex: {a:3, b:1, c:2}
         
right=4, char='b': 'b' at index 1 >= left(1)!
         Move left = 1 + 1 = 2
         window="cab", max=3
         charIndex: {a:3, b:4, c:2}
         
right=5, char='c': 'c' at index 2 >= left(2)!
         Move left = 2 + 1 = 3
         window="abc", max=3
         charIndex: {a:3, b:4, c:5}
         
right=6, char='b': 'b' at index 4 >= left(3)!
         Move left = 4 + 1 = 5
         window="cb", max=3
         
right=7, char='b': 'b' at index 6 >= left(5)!
         Move left = 6 + 1 = 7
         window="b", max=3

Answer: 3
```

---

### 📖 Example: Minimum Window Substring

**Problem:** Find the minimum window in S that contains all characters of T.

```javascript
function minWindow(s, t) {
    if (t.length > s.length) return "";
    
    // Count characters needed from t
    const need = new Map();
    for (let char of t) {
        need.set(char, (need.get(char) || 0) + 1);
    }
    
    let have = 0;           // Characters we have in correct count
    const required = need.size;  // Unique chars we need
    const window = new Map();
    
    let left = 0;
    let minLen = Infinity;
    let minStart = 0;
    
    for (let right = 0; right < s.length; right++) {
        // EXPAND: Add character
        const char = s[right];
        window.set(char, (window.get(char) || 0) + 1);
        
        // Check if this character satisfies requirement
        if (need.has(char) && window.get(char) === need.get(char)) {
            have++;
        }
        
        // CONTRACT: Try to minimize window
        while (have === required) {
            // Update result
            if (right - left + 1 < minLen) {
                minLen = right - left + 1;
                minStart = left;
            }
            
            // Remove left character
            const leftChar = s[left];
            window.set(leftChar, window.get(leftChar) - 1);
            
            if (need.has(leftChar) && window.get(leftChar) < need.get(leftChar)) {
                have--;
            }
            
            left++;
        }
    }
    
    return minLen === Infinity ? "" : s.substring(minStart, minStart + minLen);
}
```

**Walkthrough:**
```
s = "ADOBECODEBANC", t = "ABC"

need = {A:1, B:1, C:1}, required = 3

Expand until have = 3:
"ADOBEC" → have=3 (has A, B, C)
  Contract: "DOBEC" → have=2 (lost A)

Continue:
"DOBECODEBA" → have=3
  Contract: "ECODEBA" → have=3
  Contract: "CODEBA" → have=3
  Contract: "ODEBA" → have=2 (no C)

"ODEBANC" → have=3
  Contract: "DEBANC" → have=3
  Contract: "EBANC" → have=3
  Contract: "BANC" → have=3 ← minimum! length 4
  Contract: "ANC" → have=2 (no B)

Answer: "BANC"
```

---

### 📖 Sliding Window Patterns Summary

| Problem Type | Window Size | Contract When |
|--------------|-------------|---------------|
| Max sum of k elements | Fixed (k) | Always after adding |
| Longest with ≤ k distinct | Variable | > k distinct chars |
| Longest without repeats | Variable | Duplicate found |
| Minimum containing all | Variable | All required chars found |
| Longest with same chars (with k flips) | Variable | > k different chars |

---

### 📖 Common Pitfalls

1. **Off-by-one errors:** Window length is `right - left + 1`
2. **Forgetting to update state:** Always update after moving either pointer
3. **Contract vs Expand order:** Usually expand first, then contract
4. **Initial window:** Some problems need initial k-size window first

---

### 💻 Practice Problems

| Problem | Type | Key Insight |
|---------|------|-------------|
| Maximum Average Subarray | Fixed | Sum / k |
| Longest Substring Without Repeating | Variable | HashMap for last index |
| Minimum Window Substring | Variable | Two hashmaps (need vs have) |
| Permutation in String | Fixed | Frequency comparison |
| Longest Repeating Character Replacement | Variable | max char count + k ≥ window |

---

### ✅ Day 3 Checklist
- [ ] Understand fixed vs variable sliding window
- [ ] Master the expand → contract → update pattern
- [ ] Complete: Longest Substring Without Repeating
- [ ] Complete: Minimum Window Substring
- [ ] Practice: Maximum Average Subarray, Permutation in String

---

## Day 4: Binary Search Mastery

### 🎯 Learning Objectives
By the end of this day, you will:
- Implement binary search correctly every time
- Know all 3 binary search templates
- Apply binary search to non-obvious problems

---

### 📖 What is Binary Search?

Binary search is a divide-and-conquer algorithm that finds a target in a **sorted** array by repeatedly halving the search space.

```
Sorted Array: [1, 3, 5, 7, 9, 11, 13, 15, 17]
Target: 11

Step 1: mid = 9
        [1, 3, 5, 7, 9, 11, 13, 15, 17]
                    ↑
        11 > 9, search right half

Step 2: mid = 13
        [11, 13, 15, 17]
              ↑
        11 < 13, search left half

Step 3: mid = 11
        [11]
         ↑
        11 = 11, FOUND!

Comparisons: 3 (vs 6 for linear search)
```

**Complexity:**
- Time: O(log n) - halving each step
- Space: O(1) iterative, O(log n) recursive

---

### 📖 Template 1: Basic Binary Search

Find exact match or return -1.

```javascript
function binarySearch(arr, target) {
    let left = 0;
    let right = arr.length - 1;
    
    while (left <= right) {  // Note: <= not <
        const mid = left + Math.floor((right - left) / 2);  // Avoid overflow
        
        if (arr[mid] === target) {
            return mid;           // Found!
        } else if (arr[mid] < target) {
            left = mid + 1;       // Search right half
        } else {
            right = mid - 1;      // Search left half
        }
    }
    
    return -1;  // Not found
}
```

**Why `left + (right - left) / 2` instead of `(left + right) / 2`?**
```
If left = 2,000,000,000 and right = 2,000,000,000
(left + right) = 4,000,000,000 → INTEGER OVERFLOW!
left + (right - left) / 2 = 2,000,000,000 + 0 = safe
```

---

### 📖 Template 2: Find First/Last Position

Find the FIRST position where condition is true.

```javascript
// Find first position where arr[i] >= target (lower bound)
function findFirst(arr, target) {
    let left = 0;
    let right = arr.length;  // Note: right = length, not length-1
    
    while (left < right) {   // Note: < not <=
        const mid = left + Math.floor((right - left) / 2);
        
        if (arr[mid] < target) {
            left = mid + 1;   // mid is too small
        } else {
            right = mid;      // mid might be answer, keep it
        }
    }
    
    return left;  // First position where arr[i] >= target
}

// Find last position where arr[i] <= target (upper bound - 1)
function findLast(arr, target) {
    let left = 0;
    let right = arr.length;
    
    while (left < right) {
        const mid = left + Math.floor((right - left) / 2);
        
        if (arr[mid] <= target) {
            left = mid + 1;   // mid might be answer, but check right
        } else {
            right = mid;
        }
    }
    
    return left - 1;  // Last position where arr[i] <= target
}
```

**Visualization:**
```
arr = [1, 2, 2, 2, 3, 4], target = 2

findFirst (first 2):
  left=0, right=6
  mid=3: arr[3]=2 >= 2, right=3
  mid=1: arr[1]=2 >= 2, right=1
  mid=0: arr[0]=1 < 2, left=1
  left=right=1, return 1 ✓

findLast (last 2):
  left=0, right=6
  mid=3: arr[3]=2 <= 2, left=4
  mid=5: arr[5]=4 > 2, right=5
  mid=4: arr[4]=3 > 2, right=4
  left=right=4, return 4-1=3 ✓
```

---

### 📖 Template 3: Binary Search on Answer

When you don't search in an array, but search for the optimal VALUE.

**Used for:**
- Minimize the maximum
- Maximize the minimum
- Find smallest/largest value satisfying condition

```javascript
function binarySearchOnAnswer(condition, minVal, maxVal) {
    let left = minVal;
    let right = maxVal;
    
    while (left < right) {
        const mid = left + Math.floor((right - left) / 2);
        
        if (condition(mid)) {
            right = mid;      // mid works, try smaller
        } else {
            left = mid + 1;   // mid doesn't work, try larger
        }
    }
    
    return left;
}
```

#### Example: Capacity to Ship Packages

**Problem:** Ship packages within D days with minimum capacity.

```javascript
function shipWithinDays(weights, days) {
    // Minimum capacity = heaviest package
    // Maximum capacity = sum of all packages
    let left = Math.max(...weights);
    let right = weights.reduce((a, b) => a + b);
    
    function canShip(capacity) {
        let daysNeeded = 1;
        let currentLoad = 0;
        
        for (let weight of weights) {
            if (currentLoad + weight > capacity) {
                daysNeeded++;
                currentLoad = 0;
            }
            currentLoad += weight;
        }
        
        return daysNeeded <= days;
    }
    
    while (left < right) {
        const mid = left + Math.floor((right - left) / 2);
        
        if (canShip(mid)) {
            right = mid;      // mid capacity works, try smaller
        } else {
            left = mid + 1;   // mid capacity too small
        }
    }
    
    return left;
}
```

---

### 📖 Search in Rotated Sorted Array

Array was sorted but then rotated at some pivot.

```
Original: [0, 1, 2, 3, 4, 5, 6, 7]
Rotated:  [4, 5, 6, 7, 0, 1, 2, 3]
                    ↑ pivot
```

**Key Insight:** One half is ALWAYS sorted!

```javascript
function searchRotated(nums, target) {
    let left = 0;
    let right = nums.length - 1;
    
    while (left <= right) {
        const mid = left + Math.floor((right - left) / 2);
        
        if (nums[mid] === target) return mid;
        
        // Determine which half is sorted
        if (nums[left] <= nums[mid]) {
            // LEFT half is sorted
            if (nums[left] <= target && target < nums[mid]) {
                // Target in left sorted half
                right = mid - 1;
            } else {
                // Target in right half
                left = mid + 1;
            }
        } else {
            // RIGHT half is sorted
            if (nums[mid] < target && target <= nums[right]) {
                // Target in right sorted half
                left = mid + 1;
            } else {
                // Target in left half
                right = mid - 1;
            }
        }
    }
    
    return -1;
}
```

**Walkthrough:**
```
nums = [4, 5, 6, 7, 0, 1, 2], target = 0

Step 1: left=0, right=6, mid=3
        [4, 5, 6, 7, 0, 1, 2]
         ↑        ↑        ↑
        left     mid     right
        
        nums[3]=7 ≠ 0
        nums[0]=4 <= nums[3]=7 → Left half sorted
        Is 0 in [4,7)? No (0 < 4)
        Search right: left = 4

Step 2: left=4, right=6, mid=5
        [4, 5, 6, 7, 0, 1, 2]
                     ↑  ↑  ↑
                    left mid right
        
        nums[5]=1 ≠ 0
        nums[4]=0 <= nums[5]=1 → Left half sorted
        Is 0 in [0,1)? Yes!
        Search left: right = 4

Step 3: left=4, right=4, mid=4
        nums[4]=0 = target ✓

Return 4
```

---

### 📖 Binary Search Template Decision Guide

```
┌───────────────────────────────────────────────────────────────┐
│                What are you searching for?                    │
├───────────────────┬───────────────────┬───────────────────────┤
│ Exact value       │ First/Last pos    │ Optimal value         │
│ (Template 1)      │ (Template 2)      │ (Template 3)          │
├───────────────────┼───────────────────┼───────────────────────┤
│ while(left<=right)│ while(left<right) │ while(left<right)     │
│ return mid        │ return left       │ return left           │
│ right = len-1     │ right = len       │ right = maxVal        │
└───────────────────┴───────────────────┴───────────────────────┘
```

---

### 💻 Practice Problems

| Problem | Template | Key Insight |
|---------|----------|-------------|
| Binary Search | 1 | Basic implementation |
| Search Insert Position | 2 | Find first >= target |
| Find First and Last Position | 2 | findFirst + findLast |
| Search in Rotated Array | 1 | One half always sorted |
| Find Minimum in Rotated | 2 | Search for break point |
| Capacity to Ship | 3 | Binary search on answer |
| Koko Eating Bananas | 3 | Binary search on speed |

---

### ✅ Day 4 Checklist
- [ ] Master all 3 binary search templates
- [ ] Understand rotated array binary search
- [ ] Complete: Binary Search, Search in Rotated Array
- [ ] Complete: Find First and Last Position
- [ ] Practice: Capacity to Ship Packages

---

## Day 5: Prefix Sum & Matrix Techniques

### 🎯 Learning Objectives
By the end of this day, you will:
- Build and use 1D/2D prefix sums
- Apply Kadane's algorithm for maximum subarray
- Traverse matrices in spiral and diagonal patterns

---

### 📖 What is Prefix Sum?

Prefix sum (cumulative sum) allows us to find the sum of any subarray in O(1) time after O(n) preprocessing.

```
Array:      [1,  2,  3,  4,  5]
Prefix Sum: [0, 1, 3, 6, 10, 15]
             ↑
            dummy 0 makes calculation easier

Sum of arr[i..j] = prefix[j+1] - prefix[i]
Sum of arr[1..3] = prefix[4] - prefix[1] = 10 - 1 = 9
                 = 2 + 3 + 4 = 9 ✓
```

#### Building Prefix Sum Array

```javascript
function buildPrefixSum(arr) {
    const prefix = [0];  // Start with 0
    for (let num of arr) {
        prefix.push(prefix[prefix.length - 1] + num);
    }
    return prefix;
}

// Range sum query
function rangeSum(prefix, left, right) {
    return prefix[right + 1] - prefix[left];
}
```

---

### 📖 Subarray Sum Equals K

**Problem:** Find the number of subarrays that sum to k.

**Naive:** O(n²) - check all subarrays
**Optimized:** O(n) - prefix sum + hashmap

```javascript
function subarraySum(nums, k) {
    const prefixCount = new Map([[0, 1]]);  // prefix sum 0 occurs once
    let sum = 0;
    let count = 0;
    
    for (let num of nums) {
        sum += num;  // Running prefix sum
        
        // If (sum - k) exists as a previous prefix sum,
        // then subarray between them sums to k
        if (prefixCount.has(sum - k)) {
            count += prefixCount.get(sum - k);
        }
        
        prefixCount.set(sum, (prefixCount.get(sum) || 0) + 1);
    }
    
    return count;
}
```

**Visualization:**
```
nums = [1, 2, 3], k = 3

Index:    0    1    2
nums:    [1,   2,   3]
prefix:   0    1    3    6

At index 0: sum=1, looking for sum-k=1-3=-2, not found
At index 1: sum=3, looking for sum-k=3-3=0, found! count=1
            (subarray [1,2] sums to 3)
At index 2: sum=6, looking for sum-k=6-3=3, found! count=2
            (subarray [3] sums to 3)

Answer: 2 subarrays ([1,2] and [3])
```

---

### 📖 2D Prefix Sum (Range Sum Matrix)

For querying sum of any rectangle in O(1).

```
Original Matrix:           2D Prefix Sum:
┌───┬───┬───┬───┐         ┌───┬───┬───┬───┬───┐
│ 3 │ 0 │ 1 │ 4 │         │ 0 │ 0 │ 0 │ 0 │ 0 │
├───┼───┼───┼───┤         ├───┼───┼───┼───┼───┤
│ 5 │ 6 │ 3 │ 2 │    →    │ 0 │ 3 │ 3 │ 4 │ 8 │
├───┼───┼───┼───┤         ├───┼───┼───┼───┼───┤
│ 1 │ 2 │ 0 │ 1 │         │ 0 │ 8 │14 │18 │24 │
└───┴───┴───┴───┘         ├───┼───┼───┼───┼───┤
                          │ 0 │ 9 │17 │21 │28 │
                          └───┴───┴───┴───┴───┘

prefix[i][j] = sum of all elements in rectangle (0,0) to (i-1,j-1)
```

```javascript
class NumMatrix {
    constructor(matrix) {
        const m = matrix.length;
        const n = matrix[0].length;
        
        // Build prefix sum with padding
        this.prefix = Array.from({ length: m + 1 }, () => 
            new Array(n + 1).fill(0)
        );
        
        for (let i = 1; i <= m; i++) {
            for (let j = 1; j <= n; j++) {
                this.prefix[i][j] = matrix[i-1][j-1] 
                                  + this.prefix[i-1][j] 
                                  + this.prefix[i][j-1] 
                                  - this.prefix[i-1][j-1];
            }
        }
    }
    
    sumRegion(row1, col1, row2, col2) {
        // Inclusion-exclusion principle
        return this.prefix[row2+1][col2+1] 
             - this.prefix[row1][col2+1] 
             - this.prefix[row2+1][col1] 
             + this.prefix[row1][col1];
    }
}
```

**Inclusion-Exclusion Visualization:**
```
Query: sum of rectangle (r1,c1) to (r2,c2)

┌─────────────────┐
│ A      │   B    │
│        │        │
├────────┼────────┤
│ C      │ ██D██  │ ← We want D
│        │ ██████ │
└────────┴────────┘

D = (A+B+C+D) - (A+B) - (A+C) + A
  = prefix[r2+1][c2+1] - prefix[r1][c2+1] - prefix[r2+1][c1] + prefix[r1][c1]
```

---

### 📖 Kadane's Algorithm - Maximum Subarray

Find the contiguous subarray with maximum sum.

**Key Insight:** At each position, decide whether to:
1. Extend the previous subarray
2. Start a new subarray from current element

```javascript
function maxSubArray(nums) {
    let maxSum = nums[0];
    let currentSum = nums[0];
    
    for (let i = 1; i < nums.length; i++) {
        // Either extend previous subarray or start new one
        currentSum = Math.max(nums[i], currentSum + nums[i]);
        maxSum = Math.max(maxSum, currentSum);
    }
    
    return maxSum;
}
```

**Walkthrough:**
```
nums = [-2, 1, -3, 4, -1, 2, 1, -5, 4]

i=0: currentSum=-2, maxSum=-2
i=1: currentSum=max(1, -2+1)=max(1,-1)=1, maxSum=1
i=2: currentSum=max(-3, 1-3)=max(-3,-2)=-2, maxSum=1
i=3: currentSum=max(4, -2+4)=max(4,2)=4, maxSum=4
i=4: currentSum=max(-1, 4-1)=max(-1,3)=3, maxSum=4
i=5: currentSum=max(2, 3+2)=max(2,5)=5, maxSum=5
i=6: currentSum=max(1, 5+1)=max(1,6)=6, maxSum=6
i=7: currentSum=max(-5, 6-5)=max(-5,1)=1, maxSum=6
i=8: currentSum=max(4, 1+4)=max(4,5)=5, maxSum=6

Answer: 6 (subarray [4,-1,2,1])
```

---

### 📖 Product of Array Except Self

Calculate product of all elements except self without using division.

```javascript
function productExceptSelf(nums) {
    const n = nums.length;
    const result = new Array(n).fill(1);
    
    // Left pass: result[i] = product of all elements to the left
    let leftProduct = 1;
    for (let i = 0; i < n; i++) {
        result[i] = leftProduct;
        leftProduct *= nums[i];
    }
    
    // Right pass: result[i] *= product of all elements to the right
    let rightProduct = 1;
    for (let i = n - 1; i >= 0; i--) {
        result[i] *= rightProduct;
        rightProduct *= nums[i];
    }
    
    return result;
}
```

**Visualization:**
```
nums = [1, 2, 3, 4]

Left pass:
  result = [1, 1, 2, 6]
           [-, 1, 1×2, 1×2×3]
           
Right pass:
  result = [24, 12, 8, 6]
           [1×24, 1×12, 2×4, 6×1]
           [2×3×4, 1×3×4, 1×2×4, 1×2×3]
```

---

### 📖 Spiral Matrix Traversal

```javascript
function spiralOrder(matrix) {
    const result = [];
    if (!matrix.length) return result;
    
    let top = 0, bottom = matrix.length - 1;
    let left = 0, right = matrix[0].length - 1;
    
    while (top <= bottom && left <= right) {
        // Go right
        for (let col = left; col <= right; col++) {
            result.push(matrix[top][col]);
        }
        top++;
        
        // Go down
        for (let row = top; row <= bottom; row++) {
            result.push(matrix[row][right]);
        }
        right--;
        
        // Go left (if there's still a row)
        if (top <= bottom) {
            for (let col = right; col >= left; col--) {
                result.push(matrix[bottom][col]);
            }
            bottom--;
        }
        
        // Go up (if there's still a column)
        if (left <= right) {
            for (let row = bottom; row >= top; row--) {
                result.push(matrix[row][left]);
            }
            left++;
        }
    }
    
    return result;
}
```

**Visualization:**
```
┌───┬───┬───┐
│ 1→│ 2→│ 3 │
├───┼───┼───┤
│ 8 │ 9 │ 4↓│
├───┼───┼───┤
│←7 │←6 │ 5 │
└───┴───┴───┘

Order: 1→2→3→4→5→6→7→8→9
```

---

### ✅ Day 5 Checklist
- [ ] Build and query 1D prefix sums
- [ ] Understand 2D prefix sum with inclusion-exclusion
- [ ] Master Kadane's algorithm
- [ ] Complete: Range Sum Query, Maximum Subarray
- [ ] Practice: Subarray Sum Equals K, Spiral Matrix

---

## Day 6: Linked Lists

### 🎯 Learning Objectives
By the end of this day, you will:
- Implement singly and doubly linked lists
- Master the fast/slow pointer technique
- Reverse linked lists iteratively and recursively
- Solve merge and intersection problems

---

### 📖 Linked List Basics

```javascript
// Node definition
class ListNode {
    constructor(val) {
        this.val = val;
        this.next = null;
    }
}

// Creating a linked list: 1 → 2 → 3
const head = new ListNode(1);
head.next = new ListNode(2);
head.next.next = new ListNode(3);
```

```
Visual:  [1] → [2] → [3] → null
         head
```

#### Traversal
```javascript
function printList(head) {
    let current = head;
    while (current !== null) {
        console.log(current.val);
        current = current.next;
    }
}
```

---

### 📖 Dummy Head Technique

A dummy/sentinel node simplifies edge cases (empty list, head changes).

```javascript
function insertAtBeginning(head, val) {
    const dummy = new ListNode(0);
    dummy.next = head;
    
    const newNode = new ListNode(val);
    newNode.next = dummy.next;
    dummy.next = newNode;
    
    return dummy.next;  // New head
}
```

---

### 📖 Fast & Slow Pointer (Floyd's Cycle Detection)

**Pattern:** Slow moves 1 step, fast moves 2 steps.

#### Detect Cycle
```javascript
function hasCycle(head) {
    let slow = head;
    let fast = head;
    
    while (fast !== null && fast.next !== null) {
        slow = slow.next;        // 1 step
        fast = fast.next.next;   // 2 steps
        
        if (slow === fast) {
            return true;  // Cycle detected!
        }
    }
    
    return false;  // No cycle
}
```

**Visualization:**
```
No cycle: 1 → 2 → 3 → null
          s→  s→  s
          f→→ f→→ (f=null, stop)

Cycle: 1 → 2 → 3 → 4
       ↑         ↓
       └─── 6 ← 5
       
Step 1: slow=1, fast=1
Step 2: slow=2, fast=3
Step 3: slow=3, fast=5
Step 4: slow=4, fast=3
Step 5: slow=5, fast=5 ← MEET!
```

#### Find Cycle Start
```javascript
function detectCycle(head) {
    let slow = head;
    let fast = head;
    
    // Phase 1: Detect cycle
    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
        
        if (slow === fast) {
            // Phase 2: Find start
            slow = head;
            while (slow !== fast) {
                slow = slow.next;
                fast = fast.next;  // Both move 1 step now
            }
            return slow;  // Cycle start
        }
    }
    
    return null;
}
```

**Why does this work?**
```
Let:
- L = distance from head to cycle start
- C = cycle length
- X = distance from cycle start to meeting point

When they meet:
- Slow traveled: L + X
- Fast traveled: L + X + nC (n complete cycles)

Since fast travels 2x slow:
2(L + X) = L + X + nC
L + X = nC
L = nC - X = (n-1)C + (C - X)

So if we reset one pointer to head and move both at same speed,
they'll meet at cycle start after L steps!
```

#### Find Middle of List
```javascript
function findMiddle(head) {
    let slow = head;
    let fast = head;
    
    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
    }
    
    return slow;  // Middle node
}
```

---

### 📖 Reverse Linked List

#### Iterative (O(1) space)
```javascript
function reverseList(head) {
    let prev = null;
    let curr = head;
    
    while (curr !== null) {
        const next = curr.next;  // Save next
        curr.next = prev;        // Reverse pointer
        prev = curr;             // Move prev forward
        curr = next;             // Move curr forward
    }
    
    return prev;  // New head
}
```

**Visualization:**
```
Initial: null   1 → 2 → 3 → null
         prev  curr

Step 1:  null ← 1   2 → 3 → null
               prev curr

Step 2:  null ← 1 ← 2   3 → null
                   prev curr

Step 3:  null ← 1 ← 2 ← 3   null
                       prev curr

Return prev = 3
```

#### Recursive
```javascript
function reverseListRecursive(head) {
    // Base case: empty or single node
    if (head === null || head.next === null) {
        return head;
    }
    
    // Recursively reverse rest of list
    const newHead = reverseListRecursive(head.next);
    
    // Reverse current connection
    head.next.next = head;
    head.next = null;
    
    return newHead;
}
```

---

### 📖 Merge Two Sorted Lists

```javascript
function mergeTwoLists(l1, l2) {
    const dummy = new ListNode(0);
    let current = dummy;
    
    while (l1 !== null && l2 !== null) {
        if (l1.val <= l2.val) {
            current.next = l1;
            l1 = l1.next;
        } else {
            current.next = l2;
            l2 = l2.next;
        }
        current = current.next;
    }
    
    // Attach remaining nodes
    current.next = l1 !== null ? l1 : l2;
    
    return dummy.next;
}
```

---

### 📖 Reverse Nodes in K-Group

```javascript
function reverseKGroup(head, k) {
    const dummy = new ListNode(0);
    dummy.next = head;
    
    let groupPrev = dummy;
    
    while (true) {
        // Check if k nodes exist
        let kthNode = getKthNode(groupPrev, k);
        if (kthNode === null) break;
        
        let groupNext = kthNode.next;
        
        // Reverse the group
        let prev = kthNode.next;
        let curr = groupPrev.next;
        
        while (curr !== groupNext) {
            const next = curr.next;
            curr.next = prev;
            prev = curr;
            curr = next;
        }
        
        // Connect with previous part
        const tmp = groupPrev.next;
        groupPrev.next = kthNode;
        groupPrev = tmp;
    }
    
    return dummy.next;
}

function getKthNode(curr, k) {
    while (curr !== null && k > 0) {
        curr = curr.next;
        k--;
    }
    return curr;
}
```

---

### ✅ Day 6 Checklist
- [ ] Implement linked list from scratch
- [ ] Master fast/slow pointer technique
- [ ] Reverse list iteratively and recursively
- [ ] Complete: Reverse Linked List, Merge Two Sorted Lists
- [ ] Practice: Linked List Cycle II, Reverse K-Group

---

## Day 7: Stacks & Queues

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand stack (LIFO) and queue (FIFO) operations
- Master the monotonic stack pattern
- Implement special stacks (min stack)
- Solve expression evaluation problems

---

### 📖 Stack Basics (LIFO - Last In, First Out)

```
Push 1, Push 2, Push 3:

   │ 3 │ ← top
   ├───┤
   │ 2 │
   ├───┤
   │ 1 │
   └───┘

Pop → returns 3
Pop → returns 2
```

```javascript
// JavaScript array as stack
const stack = [];
stack.push(1);     // [1]
stack.push(2);     // [1, 2]
stack.pop();       // returns 2, stack = [1]
stack[stack.length - 1];  // peek: 1
```

---

### 📖 Queue Basics (FIFO - First In, First Out)

```
Enqueue 1, Enqueue 2, Enqueue 3:

   ┌───┬───┬───┐
   │ 1 │ 2 │ 3 │
   └───┴───┴───┘
    ↑           ↑
  front        back

Dequeue → returns 1
```

```javascript
// JavaScript array as queue (not optimal, use for small sizes)
const queue = [];
queue.push(1);     // [1]
queue.push(2);     // [1, 2]
queue.shift();     // returns 1, queue = [2]
```

---

### 📖 Monotonic Stack Pattern

A monotonic stack maintains elements in strictly increasing or decreasing order.

**Used for:**
- Next greater/smaller element
- Previous greater/smaller element
- Histogram problems
- Temperature problems

#### Next Greater Element

```javascript
function nextGreaterElement(nums) {
    const result = new Array(nums.length).fill(-1);
    const stack = [];  // Stack of indices
    
    for (let i = 0; i < nums.length; i++) {
        // Pop elements smaller than current
        while (stack.length > 0 && nums[stack[stack.length - 1]] < nums[i]) {
            const idx = stack.pop();
            result[idx] = nums[i];  // Current is next greater for popped element
        }
        stack.push(i);
    }
    
    return result;
}
```

**Walkthrough:**
```
nums = [2, 1, 2, 4, 3]

i=0: stack=[], push 0
     stack=[0] (nums[0]=2)

i=1: nums[1]=1 < nums[0]=2, push 1
     stack=[0,1]

i=2: nums[2]=2 > nums[1]=1, pop 1
     result[1]=2
     nums[2]=2 = nums[0]=2, push 2
     stack=[0,2]

i=3: nums[3]=4 > nums[2]=2, pop 2, result[2]=4
     nums[3]=4 > nums[0]=2, pop 0, result[0]=4
     push 3
     stack=[3]

i=4: nums[4]=3 < nums[3]=4, push 4
     stack=[3,4]

result = [4, 2, 4, -1, -1]
```

#### Largest Rectangle in Histogram

```javascript
function largestRectangleArea(heights) {
    const stack = [];  // Stack of indices
    let maxArea = 0;
    
    for (let i = 0; i <= heights.length; i++) {
        // Use 0 as sentinel for last iteration
        const h = i === heights.length ? 0 : heights[i];
        
        while (stack.length > 0 && heights[stack[stack.length - 1]] > h) {
            const height = heights[stack.pop()];
            const width = stack.length === 0 ? i : i - stack[stack.length - 1] - 1;
            maxArea = Math.max(maxArea, height * width);
        }
        
        stack.push(i);
    }
    
    return maxArea;
}
```

**Visualization:**
```
heights = [2, 1, 5, 6, 2, 3]

    6 |       █
    5 |     █ █
    4 |     █ █
    3 |     █ █     █
    2 | █   █ █ █   █
    1 | █ █ █ █ █ █
    0 └─────────────────
      0 1 2 3 4 5

Largest rectangle: height=5, width=2 (indices 2-3), area=10
```

---

### 📖 Min Stack

Stack that supports push, pop, top, and getMin in O(1).

```javascript
class MinStack {
    constructor() {
        this.stack = [];
        this.minStack = [];  // Parallel stack tracking minimums
    }
    
    push(val) {
        this.stack.push(val);
        
        // Push to minStack if empty or val <= current min
        if (this.minStack.length === 0 || val <= this.minStack[this.minStack.length - 1]) {
            this.minStack.push(val);
        }
    }
    
    pop() {
        const val = this.stack.pop();
        
        // Pop from minStack if it's the minimum
        if (val === this.minStack[this.minStack.length - 1]) {
            this.minStack.pop();
        }
        
        return val;
    }
    
    top() {
        return this.stack[this.stack.length - 1];
    }
    
    getMin() {
        return this.minStack[this.minStack.length - 1];
    }
}
```

---

### 📖 Valid Parentheses

```javascript
function isValid(s) {
    const stack = [];
    const pairs = {
        ')': '(',
        '}': '{',
        ']': '['
    };
    
    for (let char of s) {
        if (char in pairs) {
            // Closing bracket
            if (stack.length === 0 || stack.pop() !== pairs[char]) {
                return false;
            }
        } else {
            // Opening bracket
            stack.push(char);
        }
    }
    
    return stack.length === 0;
}
```

---

### 📖 Daily Temperatures

Find days until warmer temperature.

```javascript
function dailyTemperatures(temperatures) {
    const result = new Array(temperatures.length).fill(0);
    const stack = [];  // Stack of indices
    
    for (let i = 0; i < temperatures.length; i++) {
        while (stack.length > 0 && temperatures[i] > temperatures[stack[stack.length - 1]]) {
            const idx = stack.pop();
            result[idx] = i - idx;  // Days until warmer
        }
        stack.push(i);
    }
    
    return result;
}
```

---

### ✅ Day 7 Checklist
- [ ] Understand stack and queue operations
- [ ] Master monotonic stack pattern
- [ ] Complete: Valid Parentheses, Daily Temperatures
- [ ] Complete: Min Stack, Largest Rectangle in Histogram
- [ ] Practice: Basic Calculator II

---

# End of Week 1

**Week 1 Summary:**
- Day 1: Complexity Analysis
- Day 2: Two Pointer Pattern
- Day 3: Sliding Window Pattern
- Day 4: Binary Search
- Day 5: Prefix Sum & Matrix
- Day 6: Linked Lists
- Day 7: Stacks & Queues

---

# 🗓️ WEEK 2: Core Data Structures

---

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

## Day 9: String Algorithms

### 🎯 Learning Objectives
By the end of this day, you will:
- Implement KMP pattern matching
- Understand Z-algorithm
- Know when to use which string algorithm

---

### 📖 Why String Algorithms Matter?

**Naive string search:** O(n × m)
```javascript
function naiveSearch(text, pattern) {
    for (let i = 0; i <= text.length - pattern.length; i++) {
        let match = true;
        for (let j = 0; j < pattern.length; j++) {
            if (text[i + j] !== pattern[j]) {
                match = false;
                break;
            }
        }
        if (match) return i;
    }
    return -1;
}
```

**KMP/Z-algorithm:** O(n + m)

---

### 📖 KMP Algorithm (Knuth-Morris-Pratt)

KMP avoids re-comparing characters by using a **failure function (LPS array)**.

#### What is LPS (Longest Proper Prefix Suffix)?

LPS[i] = length of longest proper prefix of pattern[0..i] that is also a suffix.

```
Pattern: "ABABC"

Index:   0   1   2   3   4
Char:    A   B   A   B   C
LPS:     0   0   1   2   0

Explanation:
LPS[0] = 0 (single char, no proper prefix)
LPS[1] = 0 ("AB" - no match)
LPS[2] = 1 ("ABA" - "A" is both prefix and suffix)
LPS[3] = 2 ("ABAB" - "AB" is both prefix and suffix)
LPS[4] = 0 ("ABABC" - no match)
```

#### Building LPS Array

```javascript
function buildLPS(pattern) {
    const lps = [0];       // LPS[0] is always 0
    let len = 0;           // Length of previous longest prefix suffix
    let i = 1;
    
    while (i < pattern.length) {
        if (pattern[i] === pattern[len]) {
            len++;
            lps.push(len);
            i++;
        } else if (len > 0) {
            // Try shorter prefix
            len = lps[len - 1];
        } else {
            lps.push(0);
            i++;
        }
    }
    
    return lps;
}
```

#### KMP Search

```javascript
function kmpSearch(text, pattern) {
    const lps = buildLPS(pattern);
    const results = [];
    
    let i = 0;  // Index for text
    let j = 0;  // Index for pattern
    
    while (i < text.length) {
        if (text[i] === pattern[j]) {
            i++;
            j++;
            
            if (j === pattern.length) {
                results.push(i - j);  // Found match!
                j = lps[j - 1];       // Continue searching
            }
        } else if (j > 0) {
            // Mismatch: use LPS to skip
            j = lps[j - 1];
        } else {
            i++;
        }
    }
    
    return results;
}
```

**Visual Walkthrough:**
```
Text:    "ABABDABABC"
Pattern: "ABABC"
LPS:     [0, 0, 1, 2, 0]

i=0, j=0: A=A ✓, i=1, j=1
i=1, j=1: B=B ✓, i=2, j=2
i=2, j=2: A=A ✓, i=3, j=3
i=3, j=3: B=B ✓, i=4, j=4
i=4, j=4: D≠C ✗
          j = lps[3] = 2 (skip to position 2)
          
i=4, j=2: D≠A ✗
          j = lps[1] = 0
          
i=4, j=0: D≠A ✗, j=0, so i++

i=5, j=0: A=A ✓, i=6, j=1
... continues until match at index 5
```

**Why it works:**
When mismatch at position j, LPS tells us the longest prefix that's also a suffix. We don't need to re-compare that part!

---

### 📖 Z-Algorithm

Z[i] = length of longest substring starting at i that matches a prefix of the string.

```
String: "aabxaab"

Index:   0   1   2   3   4   5   6
Char:    a   a   b   x   a   a   b
Z:       -   1   0   0   3   1   0

Z[4] = 3 because "aab" (starting at 4) matches prefix "aab"
```

```javascript
function zFunction(s) {
    const n = s.length;
    const z = new Array(n).fill(0);
    let l = 0, r = 0;  // [l, r] is the rightmost matched segment
    
    for (let i = 1; i < n; i++) {
        if (i < r) {
            // We're inside a known matching segment
            z[i] = Math.min(r - i, z[i - l]);
        }
        
        // Try to extend
        while (i + z[i] < n && s[z[i]] === s[i + z[i]]) {
            z[i]++;
        }
        
        // Update rightmost segment
        if (i + z[i] > r) {
            l = i;
            r = i + z[i];
        }
    }
    
    return z;
}

// Pattern matching using Z
function zSearch(text, pattern) {
    const combined = pattern + '$' + text;
    const z = zFunction(combined);
    const results = [];
    
    for (let i = pattern.length + 1; i < combined.length; i++) {
        if (z[i] === pattern.length) {
            results.push(i - pattern.length - 1);
        }
    }
    
    return results;
}
```

---

### 📖 When to Use Which Algorithm?

| Algorithm | Use Case | Time | Space |
|-----------|----------|------|-------|
| KMP | Single pattern search | O(n+m) | O(m) |
| Z-Algorithm | Pattern search, longest palindromic prefix | O(n+m) | O(n+m) |
| Rabin-Karp | Multiple pattern search, plagiarism detection | O(n+m) avg | O(1) |
| Trie | Dictionary matching, autocomplete | O(m) per query | O(alphabet × total chars) |

---

### ✅ Day 9 Checklist
- [ ] Understand LPS array construction
- [ ] Implement KMP search
- [ ] Understand Z-algorithm
- [ ] Practice: Implement strStr, Repeated Substring Pattern

---

## Day 10: Binary Trees Fundamentals

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand tree terminology
- Implement all tree traversals (recursive & iterative)
- Solve common tree problems

---

### 📖 Tree Terminology

```
        1          ← Root
       / \
      2   3        ← Level 1 (depth 1)
     / \   \
    4   5   6      ← Leaves (no children)
    
Terminology:
- Root: Node with no parent (1)
- Leaf: Node with no children (4, 5, 6)
- Parent of 4: 2
- Children of 2: 4, 5
- Siblings of 5: 4
- Height: Longest path from root to leaf (2)
- Depth of node 5: Distance from root (2)
```

```javascript
class TreeNode {
    constructor(val) {
        this.val = val;
        this.left = null;
        this.right = null;
    }
}
```

---

### 📖 Tree Traversals

#### Inorder (Left → Root → Right)
```
    1
   / \
  2   3
 / \
4   5

Inorder: 4, 2, 5, 1, 3
```

```javascript
// Recursive
function inorderRecursive(root, result = []) {
    if (root === null) return result;
    
    inorderRecursive(root.left, result);
    result.push(root.val);
    inorderRecursive(root.right, result);
    
    return result;
}

// Iterative (using stack)
function inorderIterative(root) {
    const result = [];
    const stack = [];
    let current = root;
    
    while (current !== null || stack.length > 0) {
        // Go to leftmost node
        while (current !== null) {
            stack.push(current);
            current = current.left;
        }
        
        // Process node
        current = stack.pop();
        result.push(current.val);
        
        // Go to right subtree
        current = current.right;
    }
    
    return result;
}
```

#### Preorder (Root → Left → Right)
```javascript
// Recursive
function preorderRecursive(root, result = []) {
    if (root === null) return result;
    
    result.push(root.val);
    preorderRecursive(root.left, result);
    preorderRecursive(root.right, result);
    
    return result;
}

// Iterative
function preorderIterative(root) {
    if (!root) return [];
    
    const result = [];
    const stack = [root];
    
    while (stack.length > 0) {
        const node = stack.pop();
        result.push(node.val);
        
        // Push right first (so left is processed first)
        if (node.right) stack.push(node.right);
        if (node.left) stack.push(node.left);
    }
    
    return result;
}
```

#### Postorder (Left → Right → Root)
```javascript
// Recursive
function postorderRecursive(root, result = []) {
    if (root === null) return result;
    
    postorderRecursive(root.left, result);
    postorderRecursive(root.right, result);
    result.push(root.val);
    
    return result;
}

// Iterative (reverse of modified preorder)
function postorderIterative(root) {
    if (!root) return [];
    
    const result = [];
    const stack = [root];
    
    while (stack.length > 0) {
        const node = stack.pop();
        result.unshift(node.val);  // Add to front
        
        if (node.left) stack.push(node.left);
        if (node.right) stack.push(node.right);
    }
    
    return result;
}
```

#### Level Order (BFS)
```javascript
function levelOrder(root) {
    if (!root) return [];
    
    const result = [];
    const queue = [root];
    
    while (queue.length > 0) {
        const levelSize = queue.length;
        const currentLevel = [];
        
        for (let i = 0; i < levelSize; i++) {
            const node = queue.shift();
            currentLevel.push(node.val);
            
            if (node.left) queue.push(node.left);
            if (node.right) queue.push(node.right);
        }
        
        result.push(currentLevel);
    }
    
    return result;
}
```

---

### 📖 Common Tree Problems

#### Maximum Depth
```javascript
function maxDepth(root) {
    if (root === null) return 0;
    
    return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
}
```

#### Same Tree
```javascript
function isSameTree(p, q) {
    if (p === null && q === null) return true;
    if (p === null || q === null) return false;
    
    return p.val === q.val 
        && isSameTree(p.left, q.left) 
        && isSameTree(p.right, q.right);
}
```

#### Invert Binary Tree
```javascript
function invertTree(root) {
    if (root === null) return null;
    
    // Swap children
    [root.left, root.right] = [root.right, root.left];
    
    invertTree(root.left);
    invertTree(root.right);
    
    return root;
}
```

#### Diameter of Binary Tree
```javascript
function diameterOfBinaryTree(root) {
    let diameter = 0;
    
    function height(node) {
        if (node === null) return 0;
        
        const leftHeight = height(node.left);
        const rightHeight = height(node.right);
        
        // Update diameter (path through this node)
        diameter = Math.max(diameter, leftHeight + rightHeight);
        
        return 1 + Math.max(leftHeight, rightHeight);
    }
    
    height(root);
    return diameter;
}
```

---

### ✅ Day 10 Checklist
- [ ] Understand tree terminology
- [ ] Implement all 4 traversals (recursive & iterative)
- [ ] Complete: Max Depth, Same Tree, Invert Tree
- [ ] Practice: Diameter, Level Order Traversal

---

## Day 11: Binary Search Trees (BST)

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand BST properties
- Validate BST
- Implement BST operations
- Solve BST-specific problems

---

### 📖 BST Property

For every node:
- All values in left subtree < node's value
- All values in right subtree > node's value

```
Valid BST:          Invalid BST:
      8                   8
     / \                 / \
    3   10              3   10
   / \    \            / \    \
  1   6    14         1   6    4  ← 4 < 8, should be in left
     / \                 / \
    4   7               4   7
```

---

### 📖 BST Search, Insert, Delete

#### Search
```javascript
function searchBST(root, val) {
    if (root === null || root.val === val) return root;
    
    if (val < root.val) {
        return searchBST(root.left, val);
    } else {
        return searchBST(root.right, val);
    }
}
// Time: O(h) where h = height, O(log n) for balanced
```

#### Insert
```javascript
function insertIntoBST(root, val) {
    if (root === null) return new TreeNode(val);
    
    if (val < root.val) {
        root.left = insertIntoBST(root.left, val);
    } else {
        root.right = insertIntoBST(root.right, val);
    }
    
    return root;
}
```

---

### 📖 Validate Binary Search Tree

```javascript
function isValidBST(root, min = -Infinity, max = Infinity) {
    if (root === null) return true;
    
    // Check current node's value
    if (root.val <= min || root.val >= max) {
        return false;
    }
    
    // Recursively validate subtrees with updated bounds
    return isValidBST(root.left, min, root.val) 
        && isValidBST(root.right, root.val, max);
}
```

**Key Insight:** Pass down valid range for each subtree.

```
        5
       / \
      3   7
     / \
    1   4

Check 5: range (-∞, +∞) ✓
Check 3: range (-∞, 5) ✓
Check 7: range (5, +∞) ✓
Check 1: range (-∞, 3) ✓
Check 4: range (3, 5) ✓
```

---

### 📖 Kth Smallest Element in BST

**Key Insight:** Inorder traversal of BST gives sorted order!

```javascript
function kthSmallest(root, k) {
    const stack = [];
    let current = root;
    
    while (current !== null || stack.length > 0) {
        while (current !== null) {
            stack.push(current);
            current = current.left;
        }
        
        current = stack.pop();
        k--;
        
        if (k === 0) return current.val;
        
        current = current.right;
    }
    
    return -1;  // k is larger than tree size
}
```

---

### 📖 Lowest Common Ancestor in BST

```javascript
function lowestCommonAncestorBST(root, p, q) {
    while (root !== null) {
        if (p.val < root.val && q.val < root.val) {
            // Both in left subtree
            root = root.left;
        } else if (p.val > root.val && q.val > root.val) {
            // Both in right subtree
            root = root.right;
        } else {
            // Split point - this is LCA
            return root;
        }
    }
    
    return null;
}
```

---

### ✅ Day 11 Checklist
- [ ] Understand BST property
- [ ] Implement search, insert operations
- [ ] Complete: Validate BST, Kth Smallest
- [ ] Practice: LCA of BST, Convert Sorted Array to BST

---

## Day 12: Advanced Trees

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand balanced trees (AVL)
- Serialize and deserialize trees
- Solve path sum problems

---

### 📖 AVL Tree Concepts

AVL is a self-balancing BST where heights of left and right subtrees differ by at most 1.

**Balance Factor = height(left) - height(right)**
- Must be -1, 0, or 1 for every node

#### Rotations

**Right Rotation (LL Imbalance):**
```
    z                y
   / \             /   \
  y   T4   →      x     z
 / \             / \   / \
x   T3          T1 T2 T3 T4
```

**Left Rotation (RR Imbalance):**
```
  z                    y
 / \                 /   \
T1  y     →         z     x
   / \             / \   / \
  T2  x           T1 T2 T3 T4
```

---

### 📖 Serialize and Deserialize Binary Tree

Convert tree to string and back.

```javascript
class Codec {
    serialize(root) {
        if (root === null) return 'null';
        
        return `${root.val},${this.serialize(root.left)},${this.serialize(root.right)}`;
    }
    
    deserialize(data) {
        const values = data.split(',');
        let index = 0;
        
        function build() {
            if (values[index] === 'null') {
                index++;
                return null;
            }
            
            const node = new TreeNode(parseInt(values[index++]));
            node.left = build();
            node.right = build();
            return node;
        }
        
        return build();
    }
}
```

**Example:**
```
Tree:       Serialized:
    1       "1,2,null,null,3,4,null,null,5,null,null"
   / \
  2   3
     / \
    4   5
```

---

### 📖 Binary Tree Maximum Path Sum

```javascript
function maxPathSum(root) {
    let maxSum = -Infinity;
    
    function maxGain(node) {
        if (node === null) return 0;
        
        // Max gain from left and right (ignore negative)
        const leftGain = Math.max(0, maxGain(node.left));
        const rightGain = Math.max(0, maxGain(node.right));
        
        // Path through this node
        const pathSum = node.val + leftGain + rightGain;
        maxSum = Math.max(maxSum, pathSum);
        
        // Return max gain for parent (can only use one branch)
        return node.val + Math.max(leftGain, rightGain);
    }
    
    maxGain(root);
    return maxSum;
}
```

---

### 📖 Construct Tree from Traversals

**From Preorder and Inorder:**
```javascript
function buildTree(preorder, inorder) {
    const inorderMap = new Map();
    for (let i = 0; i < inorder.length; i++) {
        inorderMap.set(inorder[i], i);
    }
    
    let preorderIdx = 0;
    
    function build(left, right) {
        if (left > right) return null;
        
        const rootVal = preorder[preorderIdx++];
        const root = new TreeNode(rootVal);
        
        const mid = inorderMap.get(rootVal);
        
        root.left = build(left, mid - 1);
        root.right = build(mid + 1, right);
        
        return root;
    }
    
    return build(0, inorder.length - 1);
}
```

---

### ✅ Day 12 Checklist
- [ ] Understand AVL rotations conceptually
- [ ] Implement serialize/deserialize
- [ ] Complete: Max Path Sum, Construct from Traversals
- [ ] Practice: Flatten to Linked List

---

## Day 13: Heaps & Priority Queues

### 🎯 Learning Objectives
By the end of this day, you will:
- Implement binary heap
- Understand heap operations
- Solve Top-K and median problems

---

### 📖 What is a Heap?

A heap is a complete binary tree where:
- **Min Heap:** Parent ≤ children (smallest at root)
- **Max Heap:** Parent ≥ children (largest at root)

```
Min Heap:          Max Heap:
     1                  9
    / \                / \
   3   2              7   8
  / \                / \
 7   4              3   6
```

**Array Representation:**
```
Index:  0  1  2  3  4
Values: 1  3  2  7  4

For index i:
- Parent: Math.floor((i - 1) / 2)
- Left child: 2 * i + 1
- Right child: 2 * i + 2
```

---

### 📖 Heap Implementation

```javascript
class MinHeap {
    constructor() {
        this.heap = [];
    }
    
    // Helper functions
    parent(i) { return Math.floor((i - 1) / 2); }
    leftChild(i) { return 2 * i + 1; }
    rightChild(i) { return 2 * i + 2; }
    
    swap(i, j) {
        [this.heap[i], this.heap[j]] = [this.heap[j], this.heap[i]];
    }
    
    // O(log n)
    push(val) {
        this.heap.push(val);
        this._bubbleUp(this.heap.length - 1);
    }
    
    _bubbleUp(index) {
        while (index > 0 && this.heap[this.parent(index)] > this.heap[index]) {
            this.swap(index, this.parent(index));
            index = this.parent(index);
        }
    }
    
    // O(log n)
    pop() {
        if (this.heap.length === 0) return null;
        if (this.heap.length === 1) return this.heap.pop();
        
        const min = this.heap[0];
        this.heap[0] = this.heap.pop();
        this._bubbleDown(0);
        return min;
    }
    
    _bubbleDown(index) {
        while (true) {
            let smallest = index;
            const left = this.leftChild(index);
            const right = this.rightChild(index);
            
            if (left < this.heap.length && this.heap[left] < this.heap[smallest]) {
                smallest = left;
            }
            if (right < this.heap.length && this.heap[right] < this.heap[smallest]) {
                smallest = right;
            }
            
            if (smallest === index) break;
            
            this.swap(index, smallest);
            index = smallest;
        }
    }
    
    peek() {
        return this.heap[0];
    }
    
    size() {
        return this.heap.length;
    }
}
```

---

### 📖 Top K Frequent Elements

```javascript
function topKFrequent(nums, k) {
    // Count frequencies
    const freq = new Map();
    for (let num of nums) {
        freq.set(num, (freq.get(num) || 0) + 1);
    }
    
    // Use min heap of size k
    const minHeap = new MinHeap();  // [frequency, num]
    
    for (let [num, count] of freq) {
        minHeap.push([count, num]);
        
        if (minHeap.size() > k) {
            minHeap.pop();  // Remove smallest frequency
        }
    }
    
    return minHeap.heap.map(item => item[1]);
}
```

---

### 📖 Find Median from Data Stream

Use two heaps: max heap for lower half, min heap for upper half.

```javascript
class MedianFinder {
    constructor() {
        this.maxHeap = new MaxHeap();  // Lower half
        this.minHeap = new MinHeap();  // Upper half
    }
    
    addNum(num) {
        // Add to max heap first
        this.maxHeap.push(num);
        
        // Balance: move largest from maxHeap to minHeap
        this.minHeap.push(this.maxHeap.pop());
        
        // Keep maxHeap same size or one larger
        if (this.minHeap.size() > this.maxHeap.size()) {
            this.maxHeap.push(this.minHeap.pop());
        }
    }
    
    findMedian() {
        if (this.maxHeap.size() > this.minHeap.size()) {
            return this.maxHeap.peek();
        }
        return (this.maxHeap.peek() + this.minHeap.peek()) / 2;
    }
}
```

**Visual:**
```
Numbers: [2, 3, 4]

After 2:  maxHeap=[2], minHeap=[]
          median = 2

After 3:  maxHeap=[2], minHeap=[3]
          median = (2+3)/2 = 2.5

After 4:  maxHeap=[3,2], minHeap=[4]
          median = 3
```

---

### ✅ Day 13 Checklist
- [ ] Implement min heap from scratch
- [ ] Understand heap operations and complexity
- [ ] Complete: Kth Largest, Top K Frequent
- [ ] Practice: Find Median from Data Stream

---

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

## Day 15: Graph Fundamentals

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand graph terminology
- Implement adjacency list and matrix
- Know when to use which representation

---

### 📖 Graph Terminology

```
     A -------- B
     |  \      /|
     |   \    / |
     |    \  /  |
     |     \/   |
     |     /\   |
     |    /  \  |
     D--------C |
      \        /
       \------/

Vertices (Nodes): A, B, C, D
Edges: A-B, A-C, A-D, B-C, C-D, B-C
Degree of vertex: Number of edges connected (A has degree 3)
Path: Sequence of vertices (A→B→C)
Cycle: Path that starts and ends at same vertex
Connected: Path exists between all vertex pairs
```

**Directed vs Undirected:**
```
Undirected:  A --- B    (can go both ways)
Directed:    A --→ B    (one way only)
```

**Weighted vs Unweighted:**
```
Unweighted:  A --- B
Weighted:    A -5- B    (edge has weight 5)
```

---

### 📖 Graph Representations

#### 1. Adjacency List (Preferred for sparse graphs)

```javascript
// Using Map
const graph = new Map([
    ['A', ['B', 'C', 'D']],
    ['B', ['A', 'C']],
    ['C', ['A', 'B', 'D']],
    ['D', ['A', 'C']]
]);

// Using Object
const graph = {
    'A': ['B', 'C', 'D'],
    'B': ['A', 'C'],
    'C': ['A', 'B', 'D'],
    'D': ['A', 'C']
};

// For weighted graph: store [neighbor, weight]
const weightedGraph = {
    'A': [['B', 5], ['C', 3]],
    'B': [['A', 5], ['C', 2]],
    'C': [['A', 3], ['B', 2]]
};
```

**Space:** O(V + E)

#### 2. Adjacency Matrix

```javascript
//     A  B  C  D
// A [ 0, 1, 1, 1 ]
// B [ 1, 0, 1, 0 ]
// C [ 1, 1, 0, 1 ]
// D [ 1, 0, 1, 0 ]

const matrix = [
    [0, 1, 1, 1],
    [1, 0, 1, 0],
    [1, 1, 0, 1],
    [1, 0, 1, 0]
];

// Check if A-B connected: matrix[0][1] === 1
```

**Space:** O(V²)

---

### 📖 Building Graph from Edges

```javascript
function buildGraph(n, edges, directed = false) {
    const graph = new Map();
    
    // Initialize all vertices
    for (let i = 0; i < n; i++) {
        graph.set(i, []);
    }
    
    // Add edges
    for (let [u, v] of edges) {
        graph.get(u).push(v);
        if (!directed) {
            graph.get(v).push(u);
        }
    }
    
    return graph;
}

// Example: edges = [[0,1], [0,2], [1,2]]
// Undirected: {0: [1,2], 1: [0,2], 2: [0,1]}
```

---

### 📖 When to Use Which?

| Aspect | Adjacency List | Adjacency Matrix |
|--------|----------------|------------------|
| Space | O(V + E) | O(V²) |
| Check edge exists | O(degree) | O(1) |
| Find all neighbors | O(degree) | O(V) |
| Best for | Sparse graphs | Dense graphs |
| Examples | Social networks, Roads | Complete graphs |

---

### ✅ Day 15 Checklist
- [ ] Understand graph terminology
- [ ] Implement both representations
- [ ] Build graph from edge list
- [ ] Know when to use which representation

---

## Day 16: BFS (Breadth-First Search)

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand BFS traversal
- Use BFS for shortest path (unweighted)
- Solve level-based problems

---

### 📖 BFS Template

BFS explores level by level using a **queue**.

```javascript
function bfs(graph, start) {
    const visited = new Set([start]);
    const queue = [start];
    
    while (queue.length > 0) {
        const node = queue.shift();
        console.log(node);  // Process node
        
        for (let neighbor of graph.get(node) || []) {
            if (!visited.has(neighbor)) {
                visited.add(neighbor);
                queue.push(neighbor);
            }
        }
    }
}
```

**BFS Visualization:**
```
Graph:       BFS from A:
  A          Level 0: A
 /|\         Level 1: B, C, D
B C D        Level 2: E, F
|   |
E   F

Queue trace:
[A] → process A, add B,C,D
[B,C,D] → process B, add E
[C,D,E] → process C
[D,E] → process D, add F
[E,F] → process E
[F] → process F
```

---

### 📖 Shortest Path (Unweighted Graph)

```javascript
function shortestPath(graph, start, end) {
    const visited = new Set([start]);
    const queue = [[start, 0]];  // [node, distance]
    
    while (queue.length > 0) {
        const [node, dist] = queue.shift();
        
        if (node === end) return dist;
        
        for (let neighbor of graph.get(node) || []) {
            if (!visited.has(neighbor)) {
                visited.add(neighbor);
                queue.push([neighbor, dist + 1]);
            }
        }
    }
    
    return -1;  // No path
}
```

---

### 📖 Number of Islands

```javascript
function numIslands(grid) {
    if (!grid.length) return 0;
    
    const rows = grid.length;
    const cols = grid[0].length;
    let islands = 0;
    
    function bfs(r, c) {
        const queue = [[r, c]];
        grid[r][c] = '0';  // Mark visited
        
        const directions = [[0, 1], [0, -1], [1, 0], [-1, 0]];
        
        while (queue.length > 0) {
            const [row, col] = queue.shift();
            
            for (let [dr, dc] of directions) {
                const newR = row + dr;
                const newC = col + dc;
                
                if (newR >= 0 && newR < rows && 
                    newC >= 0 && newC < cols && 
                    grid[newR][newC] === '1') {
                    grid[newR][newC] = '0';
                    queue.push([newR, newC]);
                }
            }
        }
    }
    
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (grid[r][c] === '1') {
                bfs(r, c);
                islands++;
            }
        }
    }
    
    return islands;
}
```

---

### 📖 Rotting Oranges (Multi-source BFS)

```javascript
function orangesRotting(grid) {
    const rows = grid.length;
    const cols = grid[0].length;
    const queue = [];
    let freshCount = 0;
    
    // Find all rotten oranges and count fresh
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (grid[r][c] === 2) queue.push([r, c, 0]);
            else if (grid[r][c] === 1) freshCount++;
        }
    }
    
    if (freshCount === 0) return 0;
    
    const directions = [[0, 1], [0, -1], [1, 0], [-1, 0]];
    let minutes = 0;
    
    while (queue.length > 0) {
        const [r, c, time] = queue.shift();
        
        for (let [dr, dc] of directions) {
            const newR = r + dr;
            const newC = c + dc;
            
            if (newR >= 0 && newR < rows && 
                newC >= 0 && newC < cols && 
                grid[newR][newC] === 1) {
                grid[newR][newC] = 2;
                freshCount--;
                minutes = time + 1;
                queue.push([newR, newC, time + 1]);
            }
        }
    }
    
    return freshCount === 0 ? minutes : -1;
}
```

---

### ✅ Day 16 Checklist
- [ ] Implement BFS template
- [ ] Find shortest path in unweighted graph
- [ ] Complete: Number of Islands, Rotting Oranges
- [ ] Practice: Word Ladder, Open the Lock

---

## Day 17: DFS (Depth-First Search)

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand DFS traversal (recursive & iterative)
- Use DFS for path finding and cycle detection
- Recognize DFS vs BFS use cases

---

### 📖 DFS Templates

#### Recursive DFS
```javascript
function dfsRecursive(graph, node, visited = new Set()) {
    if (visited.has(node)) return;
    
    visited.add(node);
    console.log(node);  // Process node
    
    for (let neighbor of graph.get(node) || []) {
        dfsRecursive(graph, neighbor, visited);
    }
}
```

#### Iterative DFS (using stack)
```javascript
function dfsIterative(graph, start) {
    const visited = new Set();
    const stack = [start];
    
    while (stack.length > 0) {
        const node = stack.pop();
        
        if (visited.has(node)) continue;
        visited.add(node);
        console.log(node);  // Process node
        
        for (let neighbor of graph.get(node) || []) {
            if (!visited.has(neighbor)) {
                stack.push(neighbor);
            }
        }
    }
}
```

---

### 📖 DFS on Grid

```javascript
function dfsGrid(grid, row, col, visited) {
    const rows = grid.length;
    const cols = grid[0].length;
    
    // Boundary and visited check
    if (row < 0 || row >= rows || col < 0 || col >= cols) return;
    if (visited.has(`${row},${col}`)) return;
    if (grid[row][col] === 0) return;  // Not valid cell
    
    visited.add(`${row},${col}`);
    
    // Explore 4 directions
    dfsGrid(grid, row + 1, col, visited);  // Down
    dfsGrid(grid, row - 1, col, visited);  // Up
    dfsGrid(grid, row, col + 1, visited);  // Right
    dfsGrid(grid, row, col - 1, visited);  // Left
}
```

---

### 📖 Clone Graph

```javascript
function cloneGraph(node) {
    if (!node) return null;
    
    const visited = new Map();  // original → clone
    
    function dfs(node) {
        if (visited.has(node)) return visited.get(node);
        
        const clone = new Node(node.val);
        visited.set(node, clone);
        
        for (let neighbor of node.neighbors) {
            clone.neighbors.push(dfs(neighbor));
        }
        
        return clone;
    }
    
    return dfs(node);
}
```

---

### 📖 Cycle Detection in Directed Graph

```javascript
function hasCycle(numCourses, prerequisites) {
    const graph = new Map();
    for (let i = 0; i < numCourses; i++) graph.set(i, []);
    for (let [course, prereq] of prerequisites) {
        graph.get(prereq).push(course);
    }
    
    // 0: unvisited, 1: visiting (in current path), 2: visited
    const state = new Array(numCourses).fill(0);
    
    function dfs(node) {
        if (state[node] === 1) return true;   // Cycle found
        if (state[node] === 2) return false;  // Already processed
        
        state[node] = 1;  // Mark as visiting
        
        for (let neighbor of graph.get(node)) {
            if (dfs(neighbor)) return true;
        }
        
        state[node] = 2;  // Mark as fully visited
        return false;
    }
    
    for (let i = 0; i < numCourses; i++) {
        if (dfs(i)) return true;
    }
    
    return false;
}
```

---

### 📖 BFS vs DFS

| Aspect | BFS | DFS |
|--------|-----|-----|
| Data Structure | Queue | Stack/Recursion |
| Memory | O(width of tree) | O(height of tree) |
| Shortest Path | Yes (unweighted) | No |
| Best for | Level order, shortest path | Path finding, backtracking |
| Completeness | Always finds solution | May get stuck in deep path |

---

### ✅ Day 17 Checklist
- [ ] Implement DFS (recursive & iterative)
- [ ] Understand cycle detection
- [ ] Complete: Clone Graph, Course Schedule
- [ ] Practice: Number of Provinces, Pacific Atlantic

---

## Day 18: Topological Sort & Union Find

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand topological ordering
- Implement Kahn's algorithm (BFS)
- Implement Union Find (Disjoint Set)

---

### 📖 Topological Sort

Linear ordering of vertices in DAG such that for every edge u→v, u comes before v.

```
Course prerequisites:
  0 → 1 → 3
       ↘   ↓
         2 → 4

Possible order: 0, 1, 2, 3, 4
```

#### Kahn's Algorithm (BFS approach)

```javascript
function topologicalSort(numCourses, prerequisites) {
    const graph = new Map();
    const inDegree = new Array(numCourses).fill(0);
    
    // Build graph and count in-degrees
    for (let i = 0; i < numCourses; i++) graph.set(i, []);
    for (let [course, prereq] of prerequisites) {
        graph.get(prereq).push(course);
        inDegree[course]++;
    }
    
    // Start with nodes having no prerequisites
    const queue = [];
    for (let i = 0; i < numCourses; i++) {
        if (inDegree[i] === 0) queue.push(i);
    }
    
    const result = [];
    while (queue.length > 0) {
        const node = queue.shift();
        result.push(node);
        
        for (let neighbor of graph.get(node)) {
            inDegree[neighbor]--;
            if (inDegree[neighbor] === 0) {
                queue.push(neighbor);
            }
        }
    }
    
    // If we processed all nodes, valid ordering exists
    return result.length === numCourses ? result : [];
}
```

---

### 📖 Union Find (Disjoint Set Union)

Tracks elements partitioned into disjoint sets. Supports:
- **Find:** Which set does element belong to?
- **Union:** Merge two sets

```javascript
class UnionFind {
    constructor(n) {
        this.parent = Array.from({ length: n }, (_, i) => i);
        this.rank = new Array(n).fill(0);
    }
    
    // Find with path compression
    find(x) {
        if (this.parent[x] !== x) {
            this.parent[x] = this.find(this.parent[x]);
        }
        return this.parent[x];
    }
    
    // Union by rank
    union(x, y) {
        const rootX = this.find(x);
        const rootY = this.find(y);
        
        if (rootX === rootY) return false;  // Already connected
        
        if (this.rank[rootX] < this.rank[rootY]) {
            this.parent[rootX] = rootY;
        } else if (this.rank[rootX] > this.rank[rootY]) {
            this.parent[rootY] = rootX;
        } else {
            this.parent[rootY] = rootX;
            this.rank[rootX]++;
        }
        
        return true;
    }
    
    connected(x, y) {
        return this.find(x) === this.find(y);
    }
}
```

**Visual:**
```
Initial: [0] [1] [2] [3] [4]  (each is its own set)

union(0, 1):
    0
    |
    1

union(2, 3):
    0       2
    |       |
    1       3

union(0, 2):
      0
     /|\
    1 2
      |
      3
```

---

### 📖 Number of Connected Components

```javascript
function countComponents(n, edges) {
    const uf = new UnionFind(n);
    let components = n;
    
    for (let [u, v] of edges) {
        if (uf.union(u, v)) {
            components--;
        }
    }
    
    return components;
}
```

---

### ✅ Day 18 Checklist
- [ ] Implement topological sort (Kahn's algorithm)
- [ ] Implement Union Find with path compression
- [ ] Complete: Course Schedule II, Number of Provinces
- [ ] Practice: Redundant Connection, Accounts Merge

---

## Day 19: Shortest Path Algorithms

### 🎯 Learning Objectives
By the end of this day, you will:
- Implement Dijkstra's algorithm
- Understand Bellman-Ford for negative edges
- Know when to use each algorithm

---

### 📖 Dijkstra's Algorithm

Finds shortest path from source to all vertices. **No negative edges.**

```
       5
   A ───── B
   │ \     │
  3│  2\   │1
   │    \  │
   C ───── D
       1
```

```javascript
function dijkstra(graph, start) {
    const distances = {};
    const visited = new Set();
    
    // Initialize distances
    for (let node of graph.keys()) {
        distances[node] = Infinity;
    }
    distances[start] = 0;
    
    // Min heap: [distance, node]
    const heap = new MinHeap();
    heap.push([0, start]);
    
    while (heap.size() > 0) {
        const [dist, node] = heap.pop();
        
        if (visited.has(node)) continue;
        visited.add(node);
        
        for (let [neighbor, weight] of graph.get(node) || []) {
            const newDist = dist + weight;
            
            if (newDist < distances[neighbor]) {
                distances[neighbor] = newDist;
                heap.push([newDist, neighbor]);
            }
        }
    }
    
    return distances;
}
```

**Time:** O((V + E) log V) with min heap

---

### 📖 Network Delay Time

```javascript
function networkDelayTime(times, n, k) {
    // Build weighted graph
    const graph = new Map();
    for (let i = 1; i <= n; i++) graph.set(i, []);
    for (let [u, v, w] of times) {
        graph.get(u).push([v, w]);
    }
    
    // Dijkstra from k
    const dist = dijkstra(graph, k);
    
    // Find max distance
    let maxTime = 0;
    for (let i = 1; i <= n; i++) {
        if (dist[i] === Infinity) return -1;
        maxTime = Math.max(maxTime, dist[i]);
    }
    
    return maxTime;
}
```

---

### 📖 Bellman-Ford Algorithm

Works with negative edges. Detects negative cycles.

```javascript
function bellmanFord(n, edges, start) {
    const distances = new Array(n).fill(Infinity);
    distances[start] = 0;
    
    // Relax all edges (n-1) times
    for (let i = 0; i < n - 1; i++) {
        for (let [u, v, weight] of edges) {
            if (distances[u] !== Infinity && 
                distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight;
            }
        }
    }
    
    // Check for negative cycles (one more iteration)
    for (let [u, v, weight] of edges) {
        if (distances[u] !== Infinity && 
            distances[u] + weight < distances[v]) {
            return null;  // Negative cycle exists
        }
    }
    
    return distances;
}
```

**Time:** O(V × E)

---

### 📖 When to Use Which?

| Algorithm | Use Case | Time |
|-----------|----------|------|
| BFS | Unweighted graphs | O(V + E) |
| Dijkstra | Non-negative weights | O((V+E) log V) |
| Bellman-Ford | Negative weights allowed | O(V × E) |
| Floyd-Warshall | All pairs shortest path | O(V³) |

---

### ✅ Day 19 Checklist
- [ ] Implement Dijkstra with min heap
- [ ] Understand Bellman-Ford
- [ ] Complete: Network Delay Time
- [ ] Practice: Cheapest Flights Within K Stops

---

## Day 20: Minimum Spanning Tree

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand MST concept
- Implement Kruskal's algorithm
- Implement Prim's algorithm

---

### 📖 What is MST?

Minimum Spanning Tree connects all vertices with minimum total edge weight, using exactly V-1 edges.

```
       4      
   A ───── B
   │\     /│
  1│ 2   3 │6
   │  \ /  │
   C ───── D
       5
       
MST (weight = 1 + 2 + 3 = 6):
   A       B
   │\     /
  1│ 2   3
   │  \ /
   C     D
```

---

### 📖 Kruskal's Algorithm

1. Sort edges by weight
2. Add edges one by one (skip if creates cycle)
3. Use Union Find to detect cycles

```javascript
function kruskal(n, edges) {
    // Sort edges by weight
    edges.sort((a, b) => a[2] - b[2]);
    
    const uf = new UnionFind(n);
    const mst = [];
    let totalWeight = 0;
    
    for (let [u, v, weight] of edges) {
        // Add edge if doesn't create cycle
        if (uf.union(u, v)) {
            mst.push([u, v, weight]);
            totalWeight += weight;
            
            // MST complete when we have n-1 edges
            if (mst.length === n - 1) break;
        }
    }
    
    return { mst, totalWeight };
}
```

---

### 📖 Prim's Algorithm

Start from any vertex, always add the minimum weight edge that connects visited to unvisited.

```javascript
function prim(graph, n) {
    const visited = new Set();
    const mst = [];
    let totalWeight = 0;
    
    // Min heap: [weight, from, to]
    const heap = new MinHeap();
    heap.push([0, -1, 0]);  // Start from vertex 0
    
    while (visited.size < n && heap.size() > 0) {
        const [weight, from, to] = heap.pop();
        
        if (visited.has(to)) continue;
        visited.add(to);
        
        if (from !== -1) {
            mst.push([from, to, weight]);
            totalWeight += weight;
        }
        
        for (let [neighbor, edgeWeight] of graph.get(to) || []) {
            if (!visited.has(neighbor)) {
                heap.push([edgeWeight, to, neighbor]);
            }
        }
    }
    
    return { mst, totalWeight };
}
```

---

### 📖 Min Cost to Connect All Points

```javascript
function minCostConnectPoints(points) {
    const n = points.length;
    
    // Build complete graph with Manhattan distances
    const edges = [];
    for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
            const dist = Math.abs(points[i][0] - points[j][0]) + 
                        Math.abs(points[i][1] - points[j][1]);
            edges.push([i, j, dist]);
        }
    }
    
    // Kruskal's algorithm
    const { totalWeight } = kruskal(n, edges);
    return totalWeight;
}
```

---

### ✅ Day 20 Checklist
- [ ] Understand MST concept
- [ ] Implement Kruskal's with Union Find
- [ ] Implement Prim's with min heap
- [ ] Complete: Min Cost to Connect Points

---

## Day 21: Dynamic Programming Fundamentals

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand DP principles
- Identify overlapping subproblems
- Apply memoization and tabulation

---

### 📖 What is Dynamic Programming?

DP = **Optimal Substructure** + **Overlapping Subproblems**

- Break problem into smaller subproblems
- Store results to avoid recomputation

**Two approaches:**
1. **Top-down (Memoization):** Recursive with caching
2. **Bottom-up (Tabulation):** Iterative, build from base cases

---

### 📖 Fibonacci - DP Example

#### Naive Recursion (Exponential)
```javascript
function fibNaive(n) {
    if (n <= 1) return n;
    return fibNaive(n - 1) + fibNaive(n - 2);
}
// Time: O(2^n) - recomputes same values
```

#### Memoization (Top-down)
```javascript
function fibMemo(n, memo = {}) {
    if (n <= 1) return n;
    if (memo[n] !== undefined) return memo[n];
    
    memo[n] = fibMemo(n - 1, memo) + fibMemo(n - 2, memo);
    return memo[n];
}
// Time: O(n), Space: O(n)
```

#### Tabulation (Bottom-up)
```javascript
function fibTab(n) {
    if (n <= 1) return n;
    
    const dp = new Array(n + 1);
    dp[0] = 0;
    dp[1] = 1;
    
    for (let i = 2; i <= n; i++) {
        dp[i] = dp[i - 1] + dp[i - 2];
    }
    
    return dp[n];
}
// Time: O(n), Space: O(n)
```

#### Space Optimized
```javascript
function fibOptimized(n) {
    if (n <= 1) return n;
    
    let prev2 = 0, prev1 = 1;
    for (let i = 2; i <= n; i++) {
        const curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    
    return prev1;
}
// Time: O(n), Space: O(1)
```

---

### 📖 Climbing Stairs

```javascript
function climbStairs(n) {
    // dp[i] = ways to reach step i
    // dp[i] = dp[i-1] + dp[i-2]
    
    if (n <= 2) return n;
    
    let prev2 = 1, prev1 = 2;
    for (let i = 3; i <= n; i++) {
        const curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    
    return prev1;
}
```

---

### 📖 House Robber

```javascript
function rob(nums) {
    if (nums.length === 0) return 0;
    if (nums.length === 1) return nums[0];
    
    // dp[i] = max money robbing houses 0..i
    // dp[i] = max(dp[i-1], dp[i-2] + nums[i])
    
    let prev2 = 0, prev1 = nums[0];
    
    for (let i = 1; i < nums.length; i++) {
        const curr = Math.max(prev1, prev2 + nums[i]);
        prev2 = prev1;
        prev1 = curr;
    }
    
    return prev1;
}
```

**Walkthrough:**
```
nums = [2, 7, 9, 3, 1]

i=0: prev1 = 2         (take house 0)
i=1: curr = max(2, 0+7) = 7, prev2=2, prev1=7
i=2: curr = max(7, 2+9) = 11, prev2=7, prev1=11
i=3: curr = max(11, 7+3) = 11, prev2=11, prev1=11
i=4: curr = max(11, 11+1) = 12, prev2=11, prev1=12

Answer: 12 (houses 0, 2, 4)
```

---

### 📖 Coin Change

```javascript
function coinChange(coins, amount) {
    // dp[i] = min coins needed for amount i
    const dp = new Array(amount + 1).fill(Infinity);
    dp[0] = 0;
    
    for (let i = 1; i <= amount; i++) {
        for (let coin of coins) {
            if (coin <= i && dp[i - coin] !== Infinity) {
                dp[i] = Math.min(dp[i], dp[i - coin] + 1);
            }
        }
    }
    
    return dp[amount] === Infinity ? -1 : dp[amount];
}
```

---

### ✅ Day 21 Checklist
- [ ] Understand memoization vs tabulation
- [ ] Identify DP problems
- [ ] Complete: Climbing Stairs, House Robber
- [ ] Practice: Coin Change, Min Cost Climbing Stairs

---

# End of Week 3

**Week 3 Summary:**
- Day 15: Graph Fundamentals
- Day 16: BFS
- Day 17: DFS
- Day 18: Topological Sort & Union Find
- Day 19: Shortest Path (Dijkstra, Bellman-Ford)
- Day 20: Minimum Spanning Tree
- Day 21: DP Fundamentals

**Continue to Week 4 for: Advanced DP, Greedy, Backtracking, Tries, and System Design**

---

# 🗓️ WEEK 4: Advanced Algorithms

---

## Day 22: Advanced Dynamic Programming (2D DP)

### 🎯 Learning Objectives
By the end of this day, you will:
- Solve 2D DP problems
- Apply DP on strings
- Master common 2D DP patterns

---

### 📖 Unique Paths

Robot in m×n grid, can only move right or down. Count paths from top-left to bottom-right.

```javascript
function uniquePaths(m, n) {
    // dp[i][j] = number of paths to cell (i, j)
    const dp = Array.from({ length: m }, () => new Array(n).fill(1));
    
    // First row and column are all 1s (only one way to reach)
    
    for (let i = 1; i < m; i++) {
        for (let j = 1; j < n; j++) {
            // Can come from top or left
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1];
        }
    }
    
    return dp[m - 1][n - 1];
}
```

**Visual:**
```
3×3 grid:
[1] [1] [1]
[1] [2] [3]
[1] [3] [6] ← Answer
```

---

### 📖 Longest Common Subsequence (LCS)

```javascript
function longestCommonSubsequence(text1, text2) {
    const m = text1.length;
    const n = text2.length;
    
    // dp[i][j] = LCS of text1[0..i-1] and text2[0..j-1]
    const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
    
    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            if (text1[i - 1] === text2[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1] + 1;
            } else {
                dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
            }
        }
    }
    
    return dp[m][n];
}
```

**Recurrence:**
```
if chars match:    dp[i][j] = dp[i-1][j-1] + 1
if chars differ:   dp[i][j] = max(dp[i-1][j], dp[i][j-1])
```

**Table for "abcde" and "ace":**
```
    ""  a  c  e
""   0  0  0  0
a    0  1  1  1
b    0  1  1  1
c    0  1  2  2
d    0  1  2  2
e    0  1  2  3  ← LCS = 3
```

---

### 📖 Edit Distance

Minimum operations (insert, delete, replace) to convert word1 to word2.

```javascript
function minDistance(word1, word2) {
    const m = word1.length;
    const n = word2.length;
    
    // dp[i][j] = min operations to convert word1[0..i-1] to word2[0..j-1]
    const dp = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
    
    // Base cases
    for (let i = 0; i <= m; i++) dp[i][0] = i;  // Delete all
    for (let j = 0; j <= n; j++) dp[0][j] = j;  // Insert all
    
    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            if (word1[i - 1] === word2[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1];
            } else {
                dp[i][j] = 1 + Math.min(
                    dp[i - 1][j],      // Delete
                    dp[i][j - 1],      // Insert
                    dp[i - 1][j - 1]   // Replace
                );
            }
        }
    }
    
    return dp[m][n];
}
```

---

### 📖 0/1 Knapsack

```javascript
function knapsack(weights, values, capacity) {
    const n = weights.length;
    
    // dp[i][w] = max value using items 0..i-1 with capacity w
    const dp = Array.from({ length: n + 1 }, () => 
        new Array(capacity + 1).fill(0)
    );
    
    for (let i = 1; i <= n; i++) {
        for (let w = 1; w <= capacity; w++) {
            // Don't take item i-1
            dp[i][w] = dp[i - 1][w];
            
            // Take item i-1 (if it fits)
            if (weights[i - 1] <= w) {
                dp[i][w] = Math.max(
                    dp[i][w],
                    dp[i - 1][w - weights[i - 1]] + values[i - 1]
                );
            }
        }
    }
    
    return dp[n][capacity];
}
```

---

### ✅ Day 22 Checklist
- [ ] Solve 2D grid DP problems
- [ ] Master LCS and Edit Distance
- [ ] Complete: Unique Paths, LCS, Edit Distance
- [ ] Practice: Coin Change 2, Target Sum

---

## Day 23: Greedy Algorithms

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand greedy choice property
- Identify greedy vs DP problems
- Solve interval scheduling problems

---

### 📖 When to Use Greedy

Greedy works when:
1. **Greedy choice property:** Local optimal leads to global optimal
2. **Optimal substructure:** Optimal solution contains optimal solutions to subproblems

**Greedy fails when:** Local choice affects future options negatively (use DP instead).

---

### 📖 Activity Selection / Meeting Rooms

Maximum number of non-overlapping meetings.

```javascript
function maxMeetings(meetings) {
    // Sort by end time
    meetings.sort((a, b) => a[1] - b[1]);
    
    let count = 1;
    let lastEnd = meetings[0][1];
    
    for (let i = 1; i < meetings.length; i++) {
        if (meetings[i][0] >= lastEnd) {
            count++;
            lastEnd = meetings[i][1];
        }
    }
    
    return count;
}
```

**Why sort by end time?** Finishing early leaves more room for future meetings.

---

### 📖 Jump Game

```javascript
function canJump(nums) {
    let maxReach = 0;
    
    for (let i = 0; i < nums.length; i++) {
        if (i > maxReach) return false;  // Can't reach this position
        maxReach = Math.max(maxReach, i + nums[i]);
    }
    
    return maxReach >= nums.length - 1;
}
```

### Jump Game II (Minimum jumps)
```javascript
function jump(nums) {
    let jumps = 0;
    let currentEnd = 0;
    let farthest = 0;
    
    for (let i = 0; i < nums.length - 1; i++) {
        farthest = Math.max(farthest, i + nums[i]);
        
        if (i === currentEnd) {
            jumps++;
            currentEnd = farthest;
        }
    }
    
    return jumps;
}
```

---

### 📖 Gas Station

```javascript
function canCompleteCircuit(gas, cost) {
    let totalGas = 0, totalCost = 0;
    let tank = 0, start = 0;
    
    for (let i = 0; i < gas.length; i++) {
        totalGas += gas[i];
        totalCost += cost[i];
        tank += gas[i] - cost[i];
        
        if (tank < 0) {
            start = i + 1;  // Reset start
            tank = 0;
        }
    }
    
    return totalGas >= totalCost ? start : -1;
}
```

---

### 📖 Merge Intervals

```javascript
function merge(intervals) {
    intervals.sort((a, b) => a[0] - b[0]);
    const result = [intervals[0]];
    
    for (let i = 1; i < intervals.length; i++) {
        const last = result[result.length - 1];
        
        if (intervals[i][0] <= last[1]) {
            // Overlap - merge
            last[1] = Math.max(last[1], intervals[i][1]);
        } else {
            result.push(intervals[i]);
        }
    }
    
    return result;
}
```

---

### ✅ Day 23 Checklist
- [ ] Understand greedy choice property
- [ ] Complete: Jump Game, Gas Station
- [ ] Practice: Merge Intervals, Meeting Rooms II
- [ ] Compare greedy vs DP approaches

---

## Day 24: Backtracking

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand backtracking template
- Generate permutations and combinations
- Solve constraint satisfaction problems

---

### 📖 Backtracking Template

```javascript
function backtrack(candidates, path, result) {
    // Base case: valid solution found
    if (isValid(path)) {
        result.push([...path]);
        return;
    }
    
    for (let candidate of candidates) {
        // Check if candidate is valid choice
        if (isValidChoice(candidate)) {
            // Make choice
            path.push(candidate);
            
            // Recurse
            backtrack(remainingCandidates, path, result);
            
            // Undo choice (backtrack)
            path.pop();
        }
    }
}
```

---

### 📖 Subsets

```javascript
function subsets(nums) {
    const result = [];
    
    function backtrack(start, path) {
        result.push([...path]);  // Every path is a valid subset
        
        for (let i = start; i < nums.length; i++) {
            path.push(nums[i]);
            backtrack(i + 1, path);  // Start from i+1 to avoid duplicates
            path.pop();
        }
    }
    
    backtrack(0, []);
    return result;
}
```

**Decision tree:**
```
                    []
           /        |        \
         [1]       [2]       [3]
        / \         |
     [1,2] [1,3]  [2,3]
       |
    [1,2,3]
```

---

### 📖 Permutations

```javascript
function permute(nums) {
    const result = [];
    
    function backtrack(path, used) {
        if (path.length === nums.length) {
            result.push([...path]);
            return;
        }
        
        for (let i = 0; i < nums.length; i++) {
            if (used[i]) continue;
            
            path.push(nums[i]);
            used[i] = true;
            
            backtrack(path, used);
            
            path.pop();
            used[i] = false;
        }
    }
    
    backtrack([], new Array(nums.length).fill(false));
    return result;
}
```

---

### 📖 Combination Sum

```javascript
function combinationSum(candidates, target) {
    const result = [];
    
    function backtrack(start, path, remaining) {
        if (remaining === 0) {
            result.push([...path]);
            return;
        }
        if (remaining < 0) return;
        
        for (let i = start; i < candidates.length; i++) {
            path.push(candidates[i]);
            backtrack(i, path, remaining - candidates[i]);  // i, not i+1 (reuse allowed)
            path.pop();
        }
    }
    
    backtrack(0, [], target);
    return result;
}
```

---

### 📖 N-Queens

```javascript
function solveNQueens(n) {
    const result = [];
    const board = Array.from({ length: n }, () => '.'.repeat(n));
    
    // Track attacked columns and diagonals
    const cols = new Set();
    const diag1 = new Set();  // row - col
    const diag2 = new Set();  // row + col
    
    function backtrack(row) {
        if (row === n) {
            result.push([...board]);
            return;
        }
        
        for (let col = 0; col < n; col++) {
            if (cols.has(col) || diag1.has(row - col) || diag2.has(row + col)) {
                continue;
            }
            
            // Place queen
            board[row] = board[row].substring(0, col) + 'Q' + board[row].substring(col + 1);
            cols.add(col);
            diag1.add(row - col);
            diag2.add(row + col);
            
            backtrack(row + 1);
            
            // Remove queen
            board[row] = board[row].substring(0, col) + '.' + board[row].substring(col + 1);
            cols.delete(col);
            diag1.delete(row - col);
            diag2.delete(row + col);
        }
    }
    
    backtrack(0);
    return result;
}
```

---

### ✅ Day 24 Checklist
- [ ] Master backtracking template
- [ ] Complete: Subsets, Permutations
- [ ] Practice: Combination Sum, N-Queens
- [ ] Understand pruning strategies

---

## Day 25: Tries (Prefix Trees)

### 🎯 Learning Objectives
By the end of this day, you will:
- Implement Trie data structure
- Use Tries for prefix matching
- Build autocomplete system

---

### 📖 What is a Trie?

Tree structure for storing strings, where each node represents a character.

```
Words: ["cat", "car", "card", "dog"]

         root
        /    \
       c      d
       |      |
       a      o
      / \     |
     t   r    g*
     *   |
         d*

* = end of word
```

---

### 📖 Trie Implementation

```javascript
class TrieNode {
    constructor() {
        this.children = {};
        this.isEndOfWord = false;
    }
}

class Trie {
    constructor() {
        this.root = new TrieNode();
    }
    
    insert(word) {
        let node = this.root;
        for (let char of word) {
            if (!node.children[char]) {
                node.children[char] = new TrieNode();
            }
            node = node.children[char];
        }
        node.isEndOfWord = true;
    }
    
    search(word) {
        let node = this._findNode(word);
        return node !== null && node.isEndOfWord;
    }
    
    startsWith(prefix) {
        return this._findNode(prefix) !== null;
    }
    
    _findNode(str) {
        let node = this.root;
        for (let char of str) {
            if (!node.children[char]) {
                return null;
            }
            node = node.children[char];
        }
        return node;
    }
}
```

---

### 📖 Word Search II (Trie + Backtracking)

```javascript
function findWords(board, words) {
    const trie = new Trie();
    for (let word of words) {
        trie.insert(word);
    }
    
    const result = new Set();
    const rows = board.length, cols = board[0].length;
    
    function dfs(r, c, node, path) {
        if (r < 0 || r >= rows || c < 0 || c >= cols) return;
        
        const char = board[r][c];
        if (char === '#' || !node.children[char]) return;
        
        path += char;
        node = node.children[char];
        
        if (node.isEndOfWord) {
            result.add(path);
        }
        
        board[r][c] = '#';  // Mark visited
        
        dfs(r + 1, c, node, path);
        dfs(r - 1, c, node, path);
        dfs(r, c + 1, node, path);
        dfs(r, c - 1, node, path);
        
        board[r][c] = char;  // Restore
    }
    
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            dfs(r, c, trie.root, '');
        }
    }
    
    return [...result];
}
```

---

### 📖 Autocomplete System

```javascript
class AutocompleteSystem {
    constructor(sentences, times) {
        this.trie = new Trie();
        this.frequency = new Map();
        this.currentInput = '';
        
        for (let i = 0; i < sentences.length; i++) {
            this.trie.insert(sentences[i]);
            this.frequency.set(sentences[i], times[i]);
        }
    }
    
    input(c) {
        if (c === '#') {
            // End of sentence - store it
            this.trie.insert(this.currentInput);
            this.frequency.set(
                this.currentInput,
                (this.frequency.get(this.currentInput) || 0) + 1
            );
            this.currentInput = '';
            return [];
        }
        
        this.currentInput += c;
        return this._getSuggestions(this.currentInput);
    }
    
    _getSuggestions(prefix) {
        const matches = [];
        const node = this.trie._findNode(prefix);
        
        if (!node) return [];
        
        this._collectWords(node, prefix, matches);
        
        // Sort by frequency (desc), then alphabetically
        matches.sort((a, b) => {
            const freqDiff = this.frequency.get(b) - this.frequency.get(a);
            if (freqDiff !== 0) return freqDiff;
            return a.localeCompare(b);
        });
        
        return matches.slice(0, 3);
    }
    
    _collectWords(node, prefix, matches) {
        if (node.isEndOfWord) {
            matches.push(prefix);
        }
        for (let char in node.children) {
            this._collectWords(node.children[char], prefix + char, matches);
        }
    }
}
```

---

### ✅ Day 25 Checklist
- [ ] Implement Trie with insert, search, startsWith
- [ ] Complete: Implement Trie, Word Search II
- [ ] Practice: Design Add and Search Words
- [ ] Build autocomplete system

---

## Day 26: Segment Trees & Binary Indexed Trees

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand range query problems
- Implement Segment Tree
- Know when to use BIT vs Segment Tree

---

### 📖 Range Query Problem

Given array, answer queries like:
- Sum of elements in range [l, r]
- Minimum in range [l, r]
- Update element at index i

**Naive:** O(n) per query, O(1) update
**Prefix Sum:** O(1) query, O(n) update
**Segment Tree:** O(log n) query, O(log n) update

---

### 📖 Segment Tree Implementation

```javascript
class SegmentTree {
    constructor(nums) {
        this.n = nums.length;
        this.tree = new Array(4 * this.n).fill(0);
        this.build(nums, 0, 0, this.n - 1);
    }
    
    // Build tree recursively
    build(nums, node, start, end) {
        if (start === end) {
            this.tree[node] = nums[start];
            return;
        }
        
        const mid = Math.floor((start + end) / 2);
        const leftChild = 2 * node + 1;
        const rightChild = 2 * node + 2;
        
        this.build(nums, leftChild, start, mid);
        this.build(nums, rightChild, mid + 1, end);
        
        this.tree[node] = this.tree[leftChild] + this.tree[rightChild];
    }
    
    // Update element at index
    update(index, val, node = 0, start = 0, end = this.n - 1) {
        if (start === end) {
            this.tree[node] = val;
            return;
        }
        
        const mid = Math.floor((start + end) / 2);
        const leftChild = 2 * node + 1;
        const rightChild = 2 * node + 2;
        
        if (index <= mid) {
            this.update(index, val, leftChild, start, mid);
        } else {
            this.update(index, val, rightChild, mid + 1, end);
        }
        
        this.tree[node] = this.tree[leftChild] + this.tree[rightChild];
    }
    
    // Query range [l, r]
    query(l, r, node = 0, start = 0, end = this.n - 1) {
        // No overlap
        if (r < start || l > end) return 0;
        
        // Complete overlap
        if (l <= start && end <= r) return this.tree[node];
        
        // Partial overlap
        const mid = Math.floor((start + end) / 2);
        const leftChild = 2 * node + 1;
        const rightChild = 2 * node + 2;
        
        return this.query(l, r, leftChild, start, mid) + 
               this.query(l, r, rightChild, mid + 1, end);
    }
}
```

**Visual:**
```
Array: [1, 3, 5, 7, 9, 11]

                 [36] (0-5)
              /         \
         [9] (0-2)    [27] (3-5)
         /    \        /     \
      [4](0-1) [5]  [16](3-4) [11]
      /  \           /   \
    [1]  [3]       [7]   [9]
```

---

### 📖 Binary Indexed Tree (Fenwick Tree)

Simpler implementation for sum queries. Uses clever bit manipulation.

```javascript
class BIT {
    constructor(n) {
        this.n = n;
        this.tree = new Array(n + 1).fill(0);
    }
    
    // Update index i by adding delta
    update(i, delta) {
        i++;  // 1-indexed
        while (i <= this.n) {
            this.tree[i] += delta;
            i += i & (-i);  // Add lowest set bit
        }
    }
    
    // Prefix sum [0, i]
    prefixSum(i) {
        i++;  // 1-indexed
        let sum = 0;
        while (i > 0) {
            sum += this.tree[i];
            i -= i & (-i);  // Remove lowest set bit
        }
        return sum;
    }
    
    // Range sum [l, r]
    rangeSum(l, r) {
        return this.prefixSum(r) - (l > 0 ? this.prefixSum(l - 1) : 0);
    }
}
```

---

### 📖 Count of Smaller Numbers After Self

```javascript
function countSmaller(nums) {
    const sorted = [...new Set(nums)].sort((a, b) => a - b);
    const rank = new Map();
    sorted.forEach((val, i) => rank.set(val, i));
    
    const bit = new BIT(sorted.length);
    const result = new Array(nums.length);
    
    // Process from right to left
    for (let i = nums.length - 1; i >= 0; i--) {
        const r = rank.get(nums[i]);
        result[i] = r > 0 ? bit.prefixSum(r - 1) : 0;
        bit.update(r, 1);
    }
    
    return result;
}
```

---

### ✅ Day 26 Checklist
- [ ] Implement Segment Tree
- [ ] Implement BIT
- [ ] Complete: Range Sum Query - Mutable
- [ ] Practice: Count of Smaller Numbers After Self

---

## Day 27: Math & Number Theory

### 🎯 Learning Objectives
By the end of this day, you will:
- Master GCD, LCM, prime checking
- Understand modular arithmetic
- Solve common math problems

---

### 📖 GCD (Greatest Common Divisor)

```javascript
function gcd(a, b) {
    while (b !== 0) {
        [a, b] = [b, a % b];
    }
    return a;
}

// LCM using GCD
function lcm(a, b) {
    return (a * b) / gcd(a, b);
}

// GCD of array
function gcdArray(arr) {
    return arr.reduce((acc, num) => gcd(acc, num));
}
```

---

### 📖 Prime Numbers

```javascript
// Check if prime - O(√n)
function isPrime(n) {
    if (n < 2) return false;
    if (n === 2) return true;
    if (n % 2 === 0) return false;
    
    for (let i = 3; i * i <= n; i += 2) {
        if (n % i === 0) return false;
    }
    return true;
}

// Sieve of Eratosthenes - O(n log log n)
function sieve(n) {
    const isPrime = new Array(n + 1).fill(true);
    isPrime[0] = isPrime[1] = false;
    
    for (let i = 2; i * i <= n; i++) {
        if (isPrime[i]) {
            for (let j = i * i; j <= n; j += i) {
                isPrime[j] = false;
            }
        }
    }
    
    return isPrime.map((v, i) => v ? i : -1).filter(v => v > 0);
}
```

---

### 📖 Modular Arithmetic

For large numbers in competitive programming:

```javascript
const MOD = 1e9 + 7;

// (a + b) mod m
const modAdd = (a, b) => ((a % MOD) + (b % MOD)) % MOD;

// (a * b) mod m
const modMul = (a, b) => ((a % MOD) * (b % MOD)) % MOD;

// Fast exponentiation: a^b mod m - O(log b)
function modPow(base, exp, mod = MOD) {
    let result = 1n;
    base = BigInt(base) % BigInt(mod);
    exp = BigInt(exp);
    
    while (exp > 0n) {
        if (exp % 2n === 1n) {
            result = (result * base) % BigInt(mod);
        }
        base = (base * base) % BigInt(mod);
        exp = exp / 2n;
    }
    
    return Number(result);
}
```

---

### 📖 Factorial and Combinations

```javascript
// Factorial with memoization
function factorial(n, memo = {}) {
    if (n <= 1) return 1n;
    if (memo[n]) return memo[n];
    memo[n] = BigInt(n) * factorial(n - 1, memo);
    return memo[n];
}

// nCr = n! / (r! * (n-r)!)
function combinations(n, r) {
    if (r > n) return 0n;
    return factorial(n) / (factorial(r) * factorial(n - r));
}

// Pascal's Triangle for nCr
function pascalTriangle(n) {
    const dp = Array.from({ length: n + 1 }, () => new Array(n + 1).fill(0n));
    
    for (let i = 0; i <= n; i++) {
        dp[i][0] = 1n;
        for (let j = 1; j <= i; j++) {
            dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j];
        }
    }
    
    return dp;
}
```

---

### 📖 Power of Two/Three

```javascript
// Power of 2: Only one bit set
function isPowerOfTwo(n) {
    return n > 0 && (n & (n - 1)) === 0;
}

// Power of 3: No simple bit trick
function isPowerOfThree(n) {
    if (n <= 0) return false;
    
    // Largest power of 3 that fits in 32-bit int: 3^19 = 1162261467
    return 1162261467 % n === 0;
}
```

---

### ✅ Day 27 Checklist
- [ ] Implement GCD/LCM
- [ ] Generate primes with Sieve
- [ ] Complete: Count Primes, Power of Two
- [ ] Practice: Happy Number, Ugly Number

---

## Day 28: System Design Problems (LeetCode Style)

### 🎯 Learning Objectives
By the end of this day, you will:
- Design LRU Cache
- Design data structures for specific use cases
- Balance time/space tradeoffs

---

### 📖 LRU Cache

Least Recently Used - evict least recently accessed item when cache is full.

```javascript
class LRUCache {
    constructor(capacity) {
        this.capacity = capacity;
        this.cache = new Map();  // Map maintains insertion order
    }
    
    get(key) {
        if (!this.cache.has(key)) return -1;
        
        // Move to end (most recent)
        const value = this.cache.get(key);
        this.cache.delete(key);
        this.cache.set(key, value);
        
        return value;
    }
    
    put(key, value) {
        // If exists, delete first to update position
        if (this.cache.has(key)) {
            this.cache.delete(key);
        }
        
        this.cache.set(key, value);
        
        // Evict LRU if over capacity
        if (this.cache.size > this.capacity) {
            // Map.keys().next() gives the first (oldest) key
            const lruKey = this.cache.keys().next().value;
            this.cache.delete(lruKey);
        }
    }
}
```

**With Doubly Linked List (O(1) operations):**
```javascript
class DLLNode {
    constructor(key, val) {
        this.key = key;
        this.val = val;
        this.prev = null;
        this.next = null;
    }
}

class LRUCacheOptimal {
    constructor(capacity) {
        this.capacity = capacity;
        this.cache = new Map();  // key → node
        
        // Dummy head and tail
        this.head = new DLLNode(0, 0);
        this.tail = new DLLNode(0, 0);
        this.head.next = this.tail;
        this.tail.prev = this.head;
    }
    
    _remove(node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }
    
    _addToEnd(node) {
        node.prev = this.tail.prev;
        node.next = this.tail;
        this.tail.prev.next = node;
        this.tail.prev = node;
    }
    
    get(key) {
        if (!this.cache.has(key)) return -1;
        
        const node = this.cache.get(key);
        this._remove(node);
        this._addToEnd(node);
        
        return node.val;
    }
    
    put(key, value) {
        if (this.cache.has(key)) {
            const node = this.cache.get(key);
            node.val = value;
            this._remove(node);
            this._addToEnd(node);
        } else {
            const node = new DLLNode(key, value);
            this.cache.set(key, node);
            this._addToEnd(node);
            
            if (this.cache.size > this.capacity) {
                const lru = this.head.next;
                this._remove(lru);
                this.cache.delete(lru.key);
            }
        }
    }
}
```

---

### 📖 LFU Cache

Least Frequently Used - evict least frequently used item.

```javascript
class LFUCache {
    constructor(capacity) {
        this.capacity = capacity;
        this.cache = new Map();      // key → {value, freq}
        this.freqMap = new Map();    // freq → Set of keys (in order)
        this.minFreq = 0;
    }
    
    _updateFreq(key) {
        const { value, freq } = this.cache.get(key);
        
        // Remove from current frequency list
        this.freqMap.get(freq).delete(key);
        if (this.freqMap.get(freq).size === 0) {
            this.freqMap.delete(freq);
            if (this.minFreq === freq) this.minFreq++;
        }
        
        // Add to next frequency list
        const newFreq = freq + 1;
        if (!this.freqMap.has(newFreq)) {
            this.freqMap.set(newFreq, new Set());
        }
        this.freqMap.get(newFreq).add(key);
        
        this.cache.set(key, { value, freq: newFreq });
    }
    
    get(key) {
        if (!this.cache.has(key)) return -1;
        
        this._updateFreq(key);
        return this.cache.get(key).value;
    }
    
    put(key, value) {
        if (this.capacity === 0) return;
        
        if (this.cache.has(key)) {
            this.cache.get(key).value = value;
            this._updateFreq(key);
        } else {
            if (this.cache.size >= this.capacity) {
                // Evict LFU item
                const lfuKeys = this.freqMap.get(this.minFreq);
                const evictKey = lfuKeys.values().next().value;
                lfuKeys.delete(evictKey);
                this.cache.delete(evictKey);
            }
            
            this.cache.set(key, { value, freq: 1 });
            if (!this.freqMap.has(1)) this.freqMap.set(1, new Set());
            this.freqMap.get(1).add(key);
            this.minFreq = 1;
        }
    }
}
```

---

### 📖 Time Based Key-Value Store

```javascript
class TimeMap {
    constructor() {
        this.store = new Map();  // key → [[timestamp, value], ...]
    }
    
    set(key, value, timestamp) {
        if (!this.store.has(key)) {
            this.store.set(key, []);
        }
        this.store.get(key).push([timestamp, value]);
    }
    
    get(key, timestamp) {
        if (!this.store.has(key)) return '';
        
        const values = this.store.get(key);
        
        // Binary search for largest timestamp <= target
        let left = 0, right = values.length - 1;
        let result = '';
        
        while (left <= right) {
            const mid = Math.floor((left + right) / 2);
            if (values[mid][0] <= timestamp) {
                result = values[mid][1];
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return result;
    }
}
```

---

### ✅ Day 28 Checklist
- [ ] Implement LRU Cache
- [ ] Understand LFU Cache
- [ ] Complete: Time Based Key-Value Store
- [ ] Practice: Design Twitter, Design HashSet

---

# 🗓️ WEEK 5: Mock Interviews & Review

---

## Day 29: Mock Interview Day 1

### 🎯 Practice Session 1

Simulate a 45-minute technical interview:
- 5 min: Introduction and problem understanding
- 30 min: Coding
- 10 min: Testing and optimization

### Problems to Solve
1. **Easy (10 min):** Two Sum
2. **Medium (20 min):** LRU Cache OR Course Schedule
3. **Discussion:** Time/space complexity, alternative approaches

### Interview Tips
- Think aloud - explain your approach
- Ask clarifying questions
- Start with brute force, then optimize
- Test with examples before coding
- Handle edge cases

---

## Day 30: Mock Interview Day 2 & Final Review

### 🎯 Practice Session 2

1. **Easy (10 min):** Valid Parentheses
2. **Medium/Hard (25 min):** Word Search II OR Median of Two Sorted Arrays
3. **System Design Discussion (10 min):** Design an autocomplete system

### 📖 Final Checklist

**Week 1: Foundations**
- [ ] Big O analysis
- [ ] Two Pointer pattern
- [ ] Sliding Window pattern
- [ ] Binary Search variants
- [ ] Prefix Sum
- [ ] Linked List operations
- [ ] Stack/Queue applications

**Week 2: Core Data Structures**
- [ ] Hash Table implementation
- [ ] String algorithms (KMP)
- [ ] Binary Tree traversals
- [ ] BST operations
- [ ] Heap implementation
- [ ] Bit manipulation tricks

**Week 3: Graphs & DP**
- [ ] Graph representations
- [ ] BFS/DFS
- [ ] Topological Sort
- [ ] Union Find
- [ ] Dijkstra's algorithm
- [ ] DP fundamentals (1D and 2D)

**Week 4: Advanced**
- [ ] 2D DP (LCS, Edit Distance)
- [ ] Greedy algorithms
- [ ] Backtracking template
- [ ] Trie implementation
- [ ] Segment Tree/BIT
- [ ] System design (LRU, LFU)

### 🏁 Final Tips for Interview Day

1. **Before the interview:**
   - Review your resume projects
   - Get good sleep
   - Prepare questions for interviewer

2. **During the interview:**
   - Stay calm, breathe
   - It's okay to ask for hints
   - Partial solution is better than no solution
   - Communicate throughout

3. **After the interview:**
   - Thank the interviewer
   - Reflect on what went well/could improve
   - Don't overanalyze - move forward

---

# 🎉 Congratulations!

You've completed the 30-Day DSA Tutorial!

**Next Steps:**
1. Continue practicing 2-3 problems daily
2. Focus on your weak areas
3. Do mock interviews with friends
4. Apply to companies confidently

**Resources for Continued Learning:**
- LeetCode Premium (company-specific problems)
- NeetCode.io (video explanations)
- System Design Primer (GitHub)
- CLRS (for deep algorithmic understanding)

Good luck with your interviews! 🚀
