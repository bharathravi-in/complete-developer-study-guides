# DSA Handbook for Senior Engineers
## A Comprehensive 30-Day Master Plan

---

**Author:** Bharath R  
**Target Audience:** Senior Engineers (8+ Years Experience)  
**Focus:** System Design, AI Engineering, FAANG Interviews  
**Version:** 1.0

---

## Table of Contents

1. [Introduction: Why DSA at Senior Level](#introduction)
2. [Week 1: Foundations with Advanced Thinking](#week-1)
3. [Week 2: Core Structures](#week-2)
4. [Week 3: Graphs & Advanced Algorithms](#week-3)
5. [Week 4: Senior-Level Engineering DSA](#week-4)
6. [Advanced Interview Question Bank](#question-bank)
7. [How to Answer at Senior Level](#answering-strategy)
8. [Mini-Systems to Build](#mini-systems)
9. [Quick Reference Patterns](#patterns)

---

<a name="introduction"></a>
## Chapter 1: Introduction — Why DSA Matters at Senior Level

### The Senior Engineer Reality

At 8+ years of experience, DSA isn't about reversing strings. It's about:

| Area | Why It Matters |
|------|----------------|
| **System Design** | Efficient data modeling, choosing right structures |
| **Backend (Node.js APIs)** | Caching strategies, indexing, message queuing |
| **AI Systems** | Graph traversal, embeddings indexing, vector search |
| **Performance Optimization** | O(1) vs O(n²) tradeoffs in production |
| **High-level Interviews** | Architecture + Deep coding rounds |
| **Technical Leadership** | Making correct scalability decisions |

### What You WON'T Be Asked
- "Reverse a string"
- "Find the largest number in array"
- "Check if palindrome"

### What You WILL Be Asked
- "Design a rate limiter for 1M requests/second"
- "Implement LRU cache with O(1) operations"
- "Design scalable autocomplete for 100M queries"
- "Optimize search across petabytes of data"

---

<a name="week-1"></a>
## Chapter 2: Week 1 — Foundations with Advanced Thinking

### Day 1-2: Time & Space Complexity (Deep Level)

#### Core Concepts

##### 1. Amortized Complexity
- **Definition:** Average time per operation over a sequence of operations
- **Example:** Dynamic array (ArrayList/Vector)
  - Single insertion: O(n) when resize needed
  - Amortized: O(1) because resize happens rarely

```javascript
// Dynamic array amortized analysis
class DynamicArray {
    constructor() {
        this.data = new Array(1);
        this.size = 0;
        this.capacity = 1;
    }
    
    push(element) {
        if (this.size === this.capacity) {
            this.resize(2 * this.capacity);  // O(n) - but rare
        }
        this.data[this.size++] = element;    // O(1) - common
    }
    
    resize(newCapacity) {
        const newData = new Array(newCapacity);
        for (let i = 0; i < this.size; i++) {
            newData[i] = this.data[i];
        }
        this.data = newData;
        this.capacity = newCapacity;
    }
}
// After n insertions: total work = n + n/2 + n/4 + ... ≈ 2n
// Amortized per operation: O(1)
```

##### 2. Worst vs Average Case Analysis

| Algorithm | Average Case | Worst Case | When Worst Happens |
|-----------|--------------|------------|-------------------|
| QuickSort | O(n log n) | O(n²) | Already sorted, bad pivot |
| HashMap lookup | O(1) | O(n) | All keys hash to same bucket |
| Binary Search Tree | O(log n) | O(n) | Skewed tree (sorted insertion) |

##### 3. Master Theorem
For recurrences of form: `T(n) = aT(n/b) + f(n)`

```
Case 1: f(n) = O(n^(log_b(a) - ε)) → T(n) = Θ(n^log_b(a))
Case 2: f(n) = Θ(n^log_b(a)) → T(n) = Θ(n^log_b(a) * log n)
Case 3: f(n) = Ω(n^(log_b(a) + ε)) → T(n) = Θ(f(n))
```

**Common Examples:**
- Merge Sort: T(n) = 2T(n/2) + n → O(n log n)
- Binary Search: T(n) = T(n/2) + 1 → O(log n)
- Strassen's: T(n) = 7T(n/2) + n² → O(n^2.81)

##### 4. Big O vs Theta vs Omega

| Notation | Meaning | Usage |
|----------|---------|-------|
| O(n) | Upper bound (at most) | Worst case guarantee |
| Ω(n) | Lower bound (at least) | Best case / lower limit |
| Θ(n) | Tight bound (exactly) | Precise characterization |

##### 5. Space-Time Tradeoffs

```javascript
// Example: Two Sum Problem

// Approach 1: O(n²) time, O(1) space
function twoSumBruteForce(nums, target) {
    for (let i = 0; i < nums.length; i++) {
        for (let j = i + 1; j < nums.length; j++) {
            if (nums[i] + nums[j] === target) return [i, j];
        }
    }
    return [];
}

// Approach 2: O(n) time, O(n) space
function twoSumOptimal(nums, target) {
    const map = new Map();
    for (let i = 0; i < nums.length; i++) {
        const complement = target - nums[i];
        if (map.has(complement)) return [map.get(complement), i];
        map.set(nums[i], i);
    }
    return [];
}
```

#### Interview Questions — Day 1-2

1. **Q: Why is QuickSort average O(n log n) but worst O(n²)?**
   - Average: Random pivot splits array roughly in half each time
   - Worst: Pivot is always smallest/largest (already sorted array)
   - Solution: Randomized pivot, median-of-three

2. **Q: Why is HashMap average O(1) but worst O(n)?**
   - Average: Good hash function distributes keys evenly
   - Worst: All keys collide → linked list traversal
   - Modern fix: Java 8+ uses trees for buckets > 8 elements

3. **Q: When does Merge Sort outperform QuickSort?**
   - Linked lists (no random access penalty)
   - External sorting (large files)
   - Stability required
   - Guaranteed O(n log n) needed

---

### Day 3-4: Arrays & Strings (Advanced Patterns)

#### Pattern 1: Two Pointer Technique

```javascript
// Template: Opposite ends moving inward
function twoPointerOpposite(arr) {
    let left = 0, right = arr.length - 1;
    while (left < right) {
        // Process based on condition
        if (condition) left++;
        else right--;
    }
}

// Template: Same direction (fast/slow)
function twoPointerSameDirection(arr) {
    let slow = 0;
    for (let fast = 0; fast < arr.length; fast++) {
        if (condition) {
            arr[slow] = arr[fast];
            slow++;
        }
    }
    return slow;
}
```

**Example: Container With Most Water**
```javascript
function maxArea(height) {
    let left = 0, right = height.length - 1;
    let maxWater = 0;
    
    while (left < right) {
        const width = right - left;
        const h = Math.min(height[left], height[right]);
        maxWater = Math.max(maxWater, width * h);
        
        // Move the shorter side (greedy)
        if (height[left] < height[right]) left++;
        else right--;
    }
    return maxWater;
}
// Time: O(n), Space: O(1)
```

#### Pattern 2: Sliding Window

```javascript
// Template: Fixed size window
function fixedWindow(arr, k) {
    let windowSum = 0;
    // Build first window
    for (let i = 0; i < k; i++) windowSum += arr[i];
    
    let result = windowSum;
    // Slide window
    for (let i = k; i < arr.length; i++) {
        windowSum += arr[i] - arr[i - k];
        result = Math.max(result, windowSum);
    }
    return result;
}

// Template: Variable size window
function variableWindow(s) {
    const charCount = new Map();
    let left = 0, result = 0;
    
    for (let right = 0; right < s.length; right++) {
        // Expand window
        charCount.set(s[right], (charCount.get(s[right]) || 0) + 1);
        
        // Shrink window while invalid
        while (/* window is invalid */) {
            charCount.set(s[left], charCount.get(s[left]) - 1);
            if (charCount.get(s[left]) === 0) charCount.delete(s[left]);
            left++;
        }
        
        // Update result
        result = Math.max(result, right - left + 1);
    }
    return result;
}
```

**Example: Longest Substring Without Repeating Characters**
```javascript
function lengthOfLongestSubstring(s) {
    const charIndex = new Map();
    let left = 0, maxLen = 0;
    
    for (let right = 0; right < s.length; right++) {
        if (charIndex.has(s[right]) && charIndex.get(s[right]) >= left) {
            left = charIndex.get(s[right]) + 1;
        }
        charIndex.set(s[right], right);
        maxLen = Math.max(maxLen, right - left + 1);
    }
    return maxLen;
}
// Time: O(n), Space: O(min(m, n)) where m = charset size
```

#### Pattern 3: Prefix Sum

```javascript
// Build prefix sum array
function buildPrefixSum(arr) {
    const prefix = [0];
    for (let num of arr) {
        prefix.push(prefix[prefix.length - 1] + num);
    }
    return prefix;
}

// Range sum query: sum(i, j) = prefix[j+1] - prefix[i]
function rangeSum(prefix, i, j) {
    return prefix[j + 1] - prefix[i];
}
```

**Example: Subarray Sum Equals K**
```javascript
function subarraySum(nums, k) {
    const prefixCount = new Map([[0, 1]]);
    let sum = 0, count = 0;
    
    for (let num of nums) {
        sum += num;
        // If (sum - k) exists, we found subarrays ending here
        if (prefixCount.has(sum - k)) {
            count += prefixCount.get(sum - k);
        }
        prefixCount.set(sum, (prefixCount.get(sum) || 0) + 1);
    }
    return count;
}
// Time: O(n), Space: O(n)
```

#### Pattern 4: Kadane's Algorithm

```javascript
function maxSubArray(nums) {
    let maxSum = nums[0];
    let currentSum = nums[0];
    
    for (let i = 1; i < nums.length; i++) {
        // Either extend current subarray or start new
        currentSum = Math.max(nums[i], currentSum + nums[i]);
        maxSum = Math.max(maxSum, currentSum);
    }
    return maxSum;
}
// Time: O(n), Space: O(1)

// Variation: Track indices
function maxSubArrayWithIndices(nums) {
    let maxSum = nums[0], currentSum = nums[0];
    let start = 0, end = 0, tempStart = 0;
    
    for (let i = 1; i < nums.length; i++) {
        if (nums[i] > currentSum + nums[i]) {
            currentSum = nums[i];
            tempStart = i;
        } else {
            currentSum += nums[i];
        }
        
        if (currentSum > maxSum) {
            maxSum = currentSum;
            start = tempStart;
            end = i;
        }
    }
    return { maxSum, start, end };
}
```

#### Pattern 5: Matrix Manipulation

```javascript
// Spiral Matrix Traversal
function spiralOrder(matrix) {
    if (!matrix.length) return [];
    
    const result = [];
    let top = 0, bottom = matrix.length - 1;
    let left = 0, right = matrix[0].length - 1;
    
    while (top <= bottom && left <= right) {
        // Traverse right
        for (let col = left; col <= right; col++) {
            result.push(matrix[top][col]);
        }
        top++;
        
        // Traverse down
        for (let row = top; row <= bottom; row++) {
            result.push(matrix[row][right]);
        }
        right--;
        
        // Traverse left (if rows remaining)
        if (top <= bottom) {
            for (let col = right; col >= left; col--) {
                result.push(matrix[bottom][col]);
            }
            bottom--;
        }
        
        // Traverse up (if columns remaining)
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

#### Trapping Rain Water (Classic Hard Problem)

```javascript
function trap(height) {
    if (height.length < 3) return 0;
    
    let left = 0, right = height.length - 1;
    let leftMax = 0, rightMax = 0;
    let water = 0;
    
    while (left < right) {
        if (height[left] < height[right]) {
            if (height[left] >= leftMax) {
                leftMax = height[left];
            } else {
                water += leftMax - height[left];
            }
            left++;
        } else {
            if (height[right] >= rightMax) {
                rightMax = height[right];
            } else {
                water += rightMax - height[right];
            }
            right--;
        }
    }
    return water;
}
// Time: O(n), Space: O(1)
```

---

### Day 5-6: Linked Lists (Real-world Applications)

#### Fast & Slow Pointer (Floyd's Cycle Detection)

```javascript
class ListNode {
    constructor(val, next = null) {
        this.val = val;
        this.next = next;
    }
}

// Detect cycle
function hasCycle(head) {
    let slow = head, fast = head;
    while (fast && fast.next) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow === fast) return true;
    }
    return false;
}

// Find cycle start
function detectCycle(head) {
    let slow = head, fast = head;
    
    while (fast && fast.next) {
        slow = slow.next;
        fast = fast.next.next;
        
        if (slow === fast) {
            // Move one pointer to head
            slow = head;
            while (slow !== fast) {
                slow = slow.next;
                fast = fast.next;
            }
            return slow;  // Start of cycle
        }
    }
    return null;
}

// Find middle of list
function findMiddle(head) {
    let slow = head, fast = head;
    while (fast && fast.next) {
        slow = slow.next;
        fast = fast.next.next;
    }
    return slow;
}
```

#### Reverse Linked List Variations

```javascript
// Iterative reversal
function reverseList(head) {
    let prev = null, curr = head;
    while (curr) {
        const next = curr.next;
        curr.next = prev;
        prev = curr;
        curr = next;
    }
    return prev;
}

// Reverse in K groups
function reverseKGroup(head, k) {
    // Check if k nodes exist
    let count = 0, curr = head;
    while (curr && count < k) {
        curr = curr.next;
        count++;
    }
    
    if (count < k) return head;  // Not enough nodes
    
    // Reverse k nodes
    let prev = null;
    curr = head;
    for (let i = 0; i < k; i++) {
        const next = curr.next;
        curr.next = prev;
        prev = curr;
        curr = next;
    }
    
    // Recursively reverse rest and connect
    head.next = reverseKGroup(curr, k);
    return prev;
}
```

#### Merge K Sorted Lists (Heap Approach)

```javascript
class MinHeap {
    constructor() {
        this.heap = [];
    }
    
    push(node) {
        this.heap.push(node);
        this.bubbleUp(this.heap.length - 1);
    }
    
    pop() {
        if (this.heap.length === 0) return null;
        if (this.heap.length === 1) return this.heap.pop();
        
        const min = this.heap[0];
        this.heap[0] = this.heap.pop();
        this.bubbleDown(0);
        return min;
    }
    
    bubbleUp(index) {
        while (index > 0) {
            const parent = Math.floor((index - 1) / 2);
            if (this.heap[parent].val <= this.heap[index].val) break;
            [this.heap[parent], this.heap[index]] = [this.heap[index], this.heap[parent]];
            index = parent;
        }
    }
    
    bubbleDown(index) {
        const length = this.heap.length;
        while (true) {
            let smallest = index;
            const left = 2 * index + 1;
            const right = 2 * index + 2;
            
            if (left < length && this.heap[left].val < this.heap[smallest].val) {
                smallest = left;
            }
            if (right < length && this.heap[right].val < this.heap[smallest].val) {
                smallest = right;
            }
            if (smallest === index) break;
            
            [this.heap[smallest], this.heap[index]] = [this.heap[index], this.heap[smallest]];
            index = smallest;
        }
    }
    
    isEmpty() {
        return this.heap.length === 0;
    }
}

function mergeKLists(lists) {
    const heap = new MinHeap();
    
    // Add first node from each list
    for (let list of lists) {
        if (list) heap.push(list);
    }
    
    const dummy = new ListNode(0);
    let curr = dummy;
    
    while (!heap.isEmpty()) {
        const node = heap.pop();
        curr.next = node;
        curr = curr.next;
        
        if (node.next) heap.push(node.next);
    }
    
    return dummy.next;
}
// Time: O(N log k) where N = total nodes, k = number of lists
```

#### LRU Cache Foundation

```javascript
class LRUCache {
    constructor(capacity) {
        this.capacity = capacity;
        this.cache = new Map();
        
        // Doubly linked list for O(1) removal
        this.head = { key: null, val: null, prev: null, next: null };
        this.tail = { key: null, val: null, prev: null, next: null };
        this.head.next = this.tail;
        this.tail.prev = this.head;
    }
    
    _remove(node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }
    
    _addToFront(node) {
        node.next = this.head.next;
        node.prev = this.head;
        this.head.next.prev = node;
        this.head.next = node;
    }
    
    get(key) {
        if (!this.cache.has(key)) return -1;
        
        const node = this.cache.get(key);
        this._remove(node);
        this._addToFront(node);
        return node.val;
    }
    
    put(key, value) {
        if (this.cache.has(key)) {
            const node = this.cache.get(key);
            node.val = value;
            this._remove(node);
            this._addToFront(node);
        } else {
            const newNode = { key, val: value, prev: null, next: null };
            this.cache.set(key, newNode);
            this._addToFront(newNode);
            
            if (this.cache.size > this.capacity) {
                const lru = this.tail.prev;
                this._remove(lru);
                this.cache.delete(lru.key);
            }
        }
    }
}
// All operations: O(1)
```

---

### Day 7: Stack & Queue

#### Monotonic Stack Pattern

```javascript
// Next Greater Element
function nextGreaterElements(nums) {
    const n = nums.length;
    const result = new Array(n).fill(-1);
    const stack = [];  // Store indices
    
    for (let i = 0; i < n; i++) {
        while (stack.length && nums[stack[stack.length - 1]] < nums[i]) {
            const idx = stack.pop();
            result[idx] = nums[i];
        }
        stack.push(i);
    }
    return result;
}

// Largest Rectangle in Histogram
function largestRectangleArea(heights) {
    const stack = [];  // Store indices
    let maxArea = 0;
    
    for (let i = 0; i <= heights.length; i++) {
        const h = i === heights.length ? 0 : heights[i];
        
        while (stack.length && heights[stack[stack.length - 1]] > h) {
            const height = heights[stack.pop()];
            const width = stack.length ? i - stack[stack.length - 1] - 1 : i;
            maxArea = Math.max(maxArea, height * width);
        }
        stack.push(i);
    }
    return maxArea;
}
// Time: O(n), Space: O(n)
```

#### Min Stack

```javascript
class MinStack {
    constructor() {
        this.stack = [];
        this.minStack = [];
    }
    
    push(val) {
        this.stack.push(val);
        const min = this.minStack.length === 0 
            ? val 
            : Math.min(val, this.minStack[this.minStack.length - 1]);
        this.minStack.push(min);
    }
    
    pop() {
        this.stack.pop();
        this.minStack.pop();
    }
    
    top() {
        return this.stack[this.stack.length - 1];
    }
    
    getMin() {
        return this.minStack[this.minStack.length - 1];
    }
}
// All operations: O(1)
```

#### Queue Using Two Stacks

```javascript
class MyQueue {
    constructor() {
        this.stackIn = [];
        this.stackOut = [];
    }
    
    push(x) {
        this.stackIn.push(x);
    }
    
    pop() {
        this._transfer();
        return this.stackOut.pop();
    }
    
    peek() {
        this._transfer();
        return this.stackOut[this.stackOut.length - 1];
    }
    
    empty() {
        return this.stackIn.length === 0 && this.stackOut.length === 0;
    }
    
    _transfer() {
        if (this.stackOut.length === 0) {
            while (this.stackIn.length) {
                this.stackOut.push(this.stackIn.pop());
            }
        }
    }
}
// Amortized O(1) for all operations
```

#### Rate Limiter Using Sliding Window

```javascript
class RateLimiter {
    constructor(maxRequests, windowSizeMs) {
        this.maxRequests = maxRequests;
        this.windowSize = windowSizeMs;
        this.requests = new Map();  // userId -> deque of timestamps
    }
    
    isAllowed(userId) {
        const now = Date.now();
        const windowStart = now - this.windowSize;
        
        if (!this.requests.has(userId)) {
            this.requests.set(userId, []);
        }
        
        const userRequests = this.requests.get(userId);
        
        // Remove expired timestamps
        while (userRequests.length && userRequests[0] < windowStart) {
            userRequests.shift();
        }
        
        if (userRequests.length < this.maxRequests) {
            userRequests.push(now);
            return true;
        }
        return false;
    }
}
// Time: O(1) amortized, Space: O(n) where n = active users
```

---

### Day 7.5: Binary Search Patterns (Critical)

#### Binary Search Templates

```javascript
// Template 1: Find exact value
function binarySearch(arr, target) {
    let left = 0, right = arr.length - 1;
    while (left <= right) {
        const mid = left + Math.floor((right - left) / 2);
        if (arr[mid] === target) return mid;
        else if (arr[mid] < target) left = mid + 1;
        else right = mid - 1;
    }
    return -1;
}

// Template 2: Find leftmost (first) occurrence
function findFirst(arr, target) {
    let left = 0, right = arr.length;
    while (left < right) {
        const mid = left + Math.floor((right - left) / 2);
        if (arr[mid] < target) left = mid + 1;
        else right = mid;
    }
    return left; // First position where arr[i] >= target
}

// Template 3: Find rightmost (last) occurrence
function findLast(arr, target) {
    let left = 0, right = arr.length;
    while (left < right) {
        const mid = left + Math.floor((right - left) / 2);
        if (arr[mid] <= target) left = mid + 1;
        else right = mid;
    }
    return left - 1; // Last position where arr[i] <= target
}

// Search in Rotated Sorted Array
function searchRotated(nums, target) {
    let left = 0, right = nums.length - 1;
    
    while (left <= right) {
        const mid = left + Math.floor((right - left) / 2);
        if (nums[mid] === target) return mid;
        
        // Determine which half is sorted
        if (nums[left] <= nums[mid]) {
            // Left half is sorted
            if (nums[left] <= target && target < nums[mid]) {
                right = mid - 1;
            } else {
                left = mid + 1;
            }
        } else {
            // Right half is sorted
            if (nums[mid] < target && target <= nums[right]) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
    }
    return -1;
}

// Binary Search on Answer (Min/Max problems)
function minCapacityToShip(weights, days) {
    let left = Math.max(...weights);
    let right = weights.reduce((a, b) => a + b);
    
    function canShip(capacity) {
        let daysNeeded = 1, currentLoad = 0;
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
        if (canShip(mid)) right = mid;
        else left = mid + 1;
    }
    return left;
}

// Find Minimum in Rotated Sorted Array
function findMin(nums) {
    let left = 0, right = nums.length - 1;
    
    while (left < right) {
        const mid = left + Math.floor((right - left) / 2);
        if (nums[mid] > nums[right]) {
            left = mid + 1;
        } else {
            right = mid;
        }
    }
    return nums[left];
}
```

---

<a name="week-2"></a>
## Chapter 3: Week 2 — Core Structures

### Day 8-9: Hashing (Critical Knowledge)

#### Hash Function Design

```javascript
// Simple string hash
function hashString(str, tableSize) {
    let hash = 0;
    const prime = 31;
    
    for (let i = 0; i < str.length; i++) {
        hash = (hash * prime + str.charCodeAt(i)) % tableSize;
    }
    return hash;
}

// Rolling hash (Rabin-Karp)
class RollingHash {
    constructor(base = 26, mod = 1e9 + 7) {
        this.base = base;
        this.mod = mod;
    }
    
    compute(str) {
        let hash = 0;
        for (let char of str) {
            hash = (hash * this.base + char.charCodeAt(0)) % this.mod;
        }
        return hash;
    }
    
    roll(oldHash, oldChar, newChar, length) {
        // Remove old char, add new char
        const basePow = this.powerMod(this.base, length - 1, this.mod);
        let hash = (oldHash - oldChar.charCodeAt(0) * basePow % this.mod + this.mod) % this.mod;
        hash = (hash * this.base + newChar.charCodeAt(0)) % this.mod;
        return hash;
    }
    
    powerMod(base, exp, mod) {
        let result = 1;
        base %= mod;
        while (exp > 0) {
            if (exp & 1) result = result * base % mod;
            base = base * base % mod;
            exp >>= 1;
        }
        return result;
    }
}
```

#### Collision Resolution Strategies

```javascript
// Chaining (Separate Chaining)
class HashMapChaining {
    constructor(size = 1000) {
        this.size = size;
        this.buckets = Array.from({ length: size }, () => []);
    }
    
    hash(key) {
        let h = 0;
        for (let char of String(key)) {
            h = (h * 31 + char.charCodeAt(0)) % this.size;
        }
        return h;
    }
    
    set(key, value) {
        const index = this.hash(key);
        const bucket = this.buckets[index];
        
        for (let item of bucket) {
            if (item[0] === key) {
                item[1] = value;
                return;
            }
        }
        bucket.push([key, value]);
    }
    
    get(key) {
        const index = this.hash(key);
        for (let [k, v] of this.buckets[index]) {
            if (k === key) return v;
        }
        return undefined;
    }
}

// Open Addressing (Linear Probing)
class HashMapOpenAddressing {
    constructor(size = 1000) {
        this.size = size;
        this.keys = new Array(size).fill(null);
        this.values = new Array(size).fill(null);
        this.deleted = new Array(size).fill(false);
        this.count = 0;
    }
    
    hash(key) {
        let h = 0;
        for (let char of String(key)) {
            h = (h * 31 + char.charCodeAt(0)) % this.size;
        }
        return h;
    }
    
    set(key, value) {
        if (this.count >= this.size * 0.7) this._resize();
        
        let index = this.hash(key);
        while (this.keys[index] !== null && this.keys[index] !== key) {
            index = (index + 1) % this.size;
        }
        
        if (this.keys[index] === null) this.count++;
        this.keys[index] = key;
        this.values[index] = value;
        this.deleted[index] = false;
    }
    
    get(key) {
        let index = this.hash(key);
        let start = index;
        
        while (this.keys[index] !== null || this.deleted[index]) {
            if (this.keys[index] === key && !this.deleted[index]) {
                return this.values[index];
            }
            index = (index + 1) % this.size;
            if (index === start) break;
        }
        return undefined;
    }
    
    _resize() {
        const oldKeys = this.keys;
        const oldValues = this.values;
        
        this.size *= 2;
        this.keys = new Array(this.size).fill(null);
        this.values = new Array(this.size).fill(null);
        this.deleted = new Array(this.size).fill(false);
        this.count = 0;
        
        for (let i = 0; i < oldKeys.length; i++) {
            if (oldKeys[i] !== null) {
                this.set(oldKeys[i], oldValues[i]);
            }
        }
    }
}
```

#### Consistent Hashing (Distributed Systems)

```javascript
class ConsistentHash {
    constructor(nodes = [], replicas = 100) {
        this.replicas = replicas;
        this.ring = new Map();  // hash -> node
        this.sortedKeys = [];
        
        for (let node of nodes) {
            this.addNode(node);
        }
    }
    
    hash(key) {
        // Simple hash for demo - use MD5/SHA in production
        let h = 0;
        for (let char of String(key)) {
            h = ((h << 5) - h + char.charCodeAt(0)) | 0;
        }
        return Math.abs(h);
    }
    
    addNode(node) {
        for (let i = 0; i < this.replicas; i++) {
            const virtualKey = this.hash(`${node}:${i}`);
            this.ring.set(virtualKey, node);
            this.sortedKeys.push(virtualKey);
        }
        this.sortedKeys.sort((a, b) => a - b);
    }
    
    removeNode(node) {
        for (let i = 0; i < this.replicas; i++) {
            const virtualKey = this.hash(`${node}:${i}`);
            this.ring.delete(virtualKey);
            this.sortedKeys = this.sortedKeys.filter(k => k !== virtualKey);
        }
    }
    
    getNode(key) {
        if (this.sortedKeys.length === 0) return null;
        
        const hash = this.hash(key);
        
        // Binary search for first key >= hash
        let left = 0, right = this.sortedKeys.length;
        while (left < right) {
            const mid = (left + right) >> 1;
            if (this.sortedKeys[mid] < hash) left = mid + 1;
            else right = mid;
        }
        
        // Wrap around to first key if we exceed all keys
        const index = left === this.sortedKeys.length ? 0 : left;
        return this.ring.get(this.sortedKeys[index]);
    }
}

// Usage
const ch = new ConsistentHash(['server1', 'server2', 'server3']);
console.log(ch.getNode('user:123'));  // Returns responsible server
```

#### Key Interview Problems

```javascript
// Longest Consecutive Sequence O(n)
function longestConsecutive(nums) {
    const numSet = new Set(nums);
    let maxLength = 0;
    
    for (let num of numSet) {
        // Only start counting from sequence start
        if (!numSet.has(num - 1)) {
            let length = 1;
            while (numSet.has(num + length)) {
                length++;
            }
            maxLength = Math.max(maxLength, length);
        }
    }
    return maxLength;
}

// Group Anagrams
function groupAnagrams(strs) {
    const map = new Map();
    
    for (let str of strs) {
        // Use sorted string as key
        const key = [...str].sort().join('');
        if (!map.has(key)) map.set(key, []);
        map.get(key).push(str);
    }
    
    return [...map.values()];
}
// Time: O(n * k log k) where k = max string length
```

---

### Day 10-12: Trees (Most Important Topic)

#### Binary Tree Traversals (Iterative)

```javascript
// Inorder (Left, Root, Right)
function inorderIterative(root) {
    const result = [], stack = [];
    let curr = root;
    
    while (curr || stack.length) {
        while (curr) {
            stack.push(curr);
            curr = curr.left;
        }
        curr = stack.pop();
        result.push(curr.val);
        curr = curr.right;
    }
    return result;
}

// Preorder (Root, Left, Right)
function preorderIterative(root) {
    if (!root) return [];
    const result = [], stack = [root];
    
    while (stack.length) {
        const node = stack.pop();
        result.push(node.val);
        if (node.right) stack.push(node.right);
        if (node.left) stack.push(node.left);
    }
    return result;
}

// Postorder (Left, Right, Root)
function postorderIterative(root) {
    if (!root) return [];
    const result = [], stack = [root];
    
    while (stack.length) {
        const node = stack.pop();
        result.unshift(node.val);  // Add to front
        if (node.left) stack.push(node.left);
        if (node.right) stack.push(node.right);
    }
    return result;
}

// Level Order (BFS)
function levelOrder(root) {
    if (!root) return [];
    const result = [], queue = [root];
    
    while (queue.length) {
        const levelSize = queue.length;
        const level = [];
        
        for (let i = 0; i < levelSize; i++) {
            const node = queue.shift();
            level.push(node.val);
            if (node.left) queue.push(node.left);
            if (node.right) queue.push(node.right);
        }
        result.push(level);
    }
    return result;
}
```

#### BST Operations

```javascript
// Validate BST
function isValidBST(root, min = -Infinity, max = Infinity) {
    if (!root) return true;
    if (root.val <= min || root.val >= max) return false;
    return isValidBST(root.left, min, root.val) && 
           isValidBST(root.right, root.val, max);
}

// Kth Smallest in BST
function kthSmallest(root, k) {
    const stack = [];
    let curr = root;
    
    while (curr || stack.length) {
        while (curr) {
            stack.push(curr);
            curr = curr.left;
        }
        curr = stack.pop();
        k--;
        if (k === 0) return curr.val;
        curr = curr.right;
    }
}

// Lowest Common Ancestor
function lowestCommonAncestor(root, p, q) {
    if (!root || root === p || root === q) return root;
    
    const left = lowestCommonAncestor(root.left, p, q);
    const right = lowestCommonAncestor(root.right, p, q);
    
    if (left && right) return root;
    return left || right;
}

// Diameter of Binary Tree
function diameterOfBinaryTree(root) {
    let diameter = 0;
    
    function height(node) {
        if (!node) return 0;
        const left = height(node.left);
        const right = height(node.right);
        diameter = Math.max(diameter, left + right);
        return 1 + Math.max(left, right);
    }
    
    height(root);
    return diameter;
}
```

#### Tree Serialization/Deserialization

```javascript
class Codec {
    serialize(root) {
        if (!root) return 'null';
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

#### Balanced Tree Concepts

```javascript
// AVL Tree Node
class AVLNode {
    constructor(val) {
        this.val = val;
        this.left = null;
        this.right = null;
        this.height = 1;
    }
}

class AVLTree {
    getHeight(node) {
        return node ? node.height : 0;
    }
    
    getBalance(node) {
        return node ? this.getHeight(node.left) - this.getHeight(node.right) : 0;
    }
    
    updateHeight(node) {
        node.height = 1 + Math.max(this.getHeight(node.left), this.getHeight(node.right));
    }
    
    rotateRight(y) {
        const x = y.left;
        const T2 = x.right;
        
        x.right = y;
        y.left = T2;
        
        this.updateHeight(y);
        this.updateHeight(x);
        
        return x;
    }
    
    rotateLeft(x) {
        const y = x.right;
        const T2 = y.left;
        
        y.left = x;
        x.right = T2;
        
        this.updateHeight(x);
        this.updateHeight(y);
        
        return y;
    }
    
    insert(node, val) {
        if (!node) return new AVLNode(val);
        
        if (val < node.val) {
            node.left = this.insert(node.left, val);
        } else if (val > node.val) {
            node.right = this.insert(node.right, val);
        } else {
            return node;  // Duplicates not allowed
        }
        
        this.updateHeight(node);
        
        const balance = this.getBalance(node);
        
        // Left Left Case
        if (balance > 1 && val < node.left.val) {
            return this.rotateRight(node);
        }
        
        // Right Right Case
        if (balance < -1 && val > node.right.val) {
            return this.rotateLeft(node);
        }
        
        // Left Right Case
        if (balance > 1 && val > node.left.val) {
            node.left = this.rotateLeft(node.left);
            return this.rotateRight(node);
        }
        
        // Right Left Case
        if (balance < -1 && val < node.right.val) {
            node.right = this.rotateRight(node.right);
            return this.rotateLeft(node);
        }
        
        return node;
    }
}
```

---

### Day 13-14: Heaps / Priority Queue

#### Binary Heap Implementation

```javascript
class MinHeap {
    constructor() {
        this.heap = [];
    }
    
    parent(i) { return Math.floor((i - 1) / 2); }
    leftChild(i) { return 2 * i + 1; }
    rightChild(i) { return 2 * i + 2; }
    
    swap(i, j) {
        [this.heap[i], this.heap[j]] = [this.heap[j], this.heap[i]];
    }
    
    push(val) {
        this.heap.push(val);
        this.bubbleUp(this.heap.length - 1);
    }
    
    pop() {
        if (this.heap.length === 0) return null;
        if (this.heap.length === 1) return this.heap.pop();
        
        const min = this.heap[0];
        this.heap[0] = this.heap.pop();
        this.bubbleDown(0);
        return min;
    }
    
    peek() {
        return this.heap[0];
    }
    
    bubbleUp(index) {
        while (index > 0 && this.heap[this.parent(index)] > this.heap[index]) {
            this.swap(index, this.parent(index));
            index = this.parent(index);
        }
    }
    
    bubbleDown(index) {
        let smallest = index;
        const left = this.leftChild(index);
        const right = this.rightChild(index);
        
        if (left < this.heap.length && this.heap[left] < this.heap[smallest]) {
            smallest = left;
        }
        if (right < this.heap.length && this.heap[right] < this.heap[smallest]) {
            smallest = right;
        }
        
        if (smallest !== index) {
            this.swap(index, smallest);
            this.bubbleDown(smallest);
        }
    }
    
    size() {
        return this.heap.length;
    }
}
```

#### Top K Elements Pattern

```javascript
// Top K Frequent Elements
function topKFrequent(nums, k) {
    // Count frequencies
    const freq = new Map();
    for (let num of nums) {
        freq.set(num, (freq.get(num) || 0) + 1);
    }
    
    // Min heap of size k (stores [num, freq])
    const heap = new MinHeapCustom((a, b) => a[1] - b[1]);
    
    for (let [num, count] of freq) {
        heap.push([num, count]);
        if (heap.size() > k) heap.pop();
    }
    
    return heap.heap.map(item => item[0]);
}

// Kth Largest Element
function findKthLargest(nums, k) {
    const minHeap = new MinHeap();
    
    for (let num of nums) {
        minHeap.push(num);
        if (minHeap.size() > k) minHeap.pop();
    }
    
    return minHeap.peek();
}
// Time: O(n log k), Space: O(k)
```

#### Median from Data Stream

```javascript
class MedianFinder {
    constructor() {
        this.maxHeap = new MaxHeap();  // Lower half
        this.minHeap = new MinHeap();  // Upper half
    }
    
    addNum(num) {
        // Add to max heap first
        this.maxHeap.push(num);
        
        // Balance: max of lower half should be <= min of upper half
        this.minHeap.push(this.maxHeap.pop());
        
        // Maintain size: maxHeap can have at most 1 more element
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
// addNum: O(log n), findMedian: O(1)
```

---

### Day 14.5: Bit Manipulation (Critical for Interviews)

#### Essential Bit Operations

```javascript
// Basic Operations
const getBit = (n, i) => (n >> i) & 1;           // Get bit at position i
const setBit = (n, i) => n | (1 << i);           // Set bit at position i to 1
const clearBit = (n, i) => n & ~(1 << i);        // Clear bit at position i
const toggleBit = (n, i) => n ^ (1 << i);        // Toggle bit at position i
const lowestSetBit = n => n & (-n);              // Get lowest set bit
const clearLowestSetBit = n => n & (n - 1);      // Clear lowest set bit

// Power of Two Check
const isPowerOfTwo = n => n > 0 && (n & (n - 1)) === 0;

// Count Set Bits (Brian Kernighan's Algorithm)
function countSetBits(n) {
    let count = 0;
    while (n) {
        n &= (n - 1);  // Clear lowest set bit
        count++;
    }
    return count;
}
// Time: O(number of set bits)

// Single Number (XOR property: a ^ a = 0, a ^ 0 = a)
function singleNumber(nums) {
    return nums.reduce((xor, num) => xor ^ num, 0);
}

// Single Number III (Two numbers appear once)
function singleNumberIII(nums) {
    // XOR all numbers to get a ^ b
    let xor = nums.reduce((x, n) => x ^ n, 0);
    
    // Find rightmost set bit (differs between a and b)
    const rightmostBit = xor & (-xor);
    
    // Partition numbers by this bit
    let a = 0, b = 0;
    for (let num of nums) {
        if (num & rightmostBit) a ^= num;
        else b ^= num;
    }
    return [a, b];
}

// Reverse Bits
function reverseBits(n) {
    let result = 0;
    for (let i = 0; i < 32; i++) {
        result = (result << 1) | (n & 1);
        n >>>= 1;
    }
    return result >>> 0;  // Convert to unsigned
}

// Add Two Numbers Without Arithmetic Operators
function getSum(a, b) {
    while (b !== 0) {
        const carry = (a & b) << 1;
        a = a ^ b;
        b = carry;
    }
    return a;
}

// Generate Subsets Using Bit Masking
function subsetsWithBitmask(nums) {
    const n = nums.length;
    const result = [];
    
    // Iterate through all 2^n possible subsets
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

// Missing Number (XOR with indices)
function missingNumber(nums) {
    let xor = nums.length;
    for (let i = 0; i < nums.length; i++) {
        xor ^= i ^ nums[i];
    }
    return xor;
}

// Counting Bits for All Numbers 0 to n
function countBitsArray(n) {
    const dp = new Array(n + 1).fill(0);
    for (let i = 1; i <= n; i++) {
        dp[i] = dp[i >> 1] + (i & 1);
    }
    return dp;
}
// Time: O(n), Space: O(n)
```

#### Bit Manipulation Tricks Table

| Operation | Code | Description |
|-----------|------|-------------|
| Check if odd | `n & 1` | Returns 1 if odd |
| Multiply by 2 | `n << 1` | Left shift |
| Divide by 2 | `n >> 1` | Right shift |
| Swap bits | `a ^= b; b ^= a; a ^= b;` | XOR swap |
| Check power of 2 | `n && !(n & (n-1))` | True if power of 2 |
| Turn off rightmost 1 | `n & (n-1)` | Clears lowest set bit |
| Isolate rightmost 1 | `n & (-n)` | Gets lowest set bit |
| Right propagate rightmost 1 | `n \| (n-1)` | Sets all bits after rightmost 1 |

---

### Day 14.6: String Algorithms (KMP & Z-Algorithm)

#### KMP (Knuth-Morris-Pratt) Algorithm

```javascript
// Build Longest Proper Prefix which is also Suffix (LPS) array
function buildLPS(pattern) {
    const lps = [0];
    let len = 0;
    let i = 1;
    
    while (i < pattern.length) {
        if (pattern[i] === pattern[len]) {
            len++;
            lps.push(len);
            i++;
        } else if (len > 0) {
            len = lps[len - 1];  // Backtrack
        } else {
            lps.push(0);
            i++;
        }
    }
    return lps;
}

// KMP Search - O(n + m)
function kmpSearch(text, pattern) {
    const lps = buildLPS(pattern);
    const result = [];
    let i = 0;  // index for text
    let j = 0;  // index for pattern
    
    while (i < text.length) {
        if (text[i] === pattern[j]) {
            i++;
            j++;
            
            if (j === pattern.length) {
                result.push(i - j);  // Found match at index i - j
                j = lps[j - 1];      // Continue searching
            }
        } else if (j > 0) {
            j = lps[j - 1];  // Use LPS to avoid re-matching
        } else {
            i++;
        }
    }
    return result;
}
// Time: O(n + m), Space: O(m)

// Example: Find "ABABC" in "ABABDABACDABABCABAB"
// LPS for "ABABC" = [0, 0, 1, 2, 0]
```

#### Z-Algorithm

```javascript
// Z-Array: z[i] = length of longest substring starting at i that matches prefix
function zFunction(s) {
    const n = s.length;
    const z = new Array(n).fill(0);
    let l = 0, r = 0;  // [l, r] is the rightmost matching segment
    
    for (let i = 1; i < n; i++) {
        if (i < r) {
            // We're inside a known matching segment
            z[i] = Math.min(r - i, z[i - l]);
        }
        
        // Try to extend the match
        while (i + z[i] < n && s[z[i]] === s[i + z[i]]) {
            z[i]++;
        }
        
        // Update the rightmost segment if necessary
        if (i + z[i] > r) {
            l = i;
            r = i + z[i];
        }
    }
    return z;
}

// Pattern matching using Z-algorithm
function zSearch(text, pattern) {
    const combined = pattern + '$' + text;  // '$' is separator
    const z = zFunction(combined);
    const result = [];
    
    for (let i = pattern.length + 1; i < combined.length; i++) {
        if (z[i] === pattern.length) {
            result.push(i - pattern.length - 1);
        }
    }
    return result;
}
// Time: O(n + m), Space: O(n + m)
```

#### Longest Palindromic Substring (Manacher's Algorithm)

```javascript
function manacher(s) {
    // Transform string: "abc" -> "^#a#b#c#$"
    const t = '^#' + s.split('').join('#') + '#$';
    const n = t.length;
    const p = new Array(n).fill(0);  // Palindrome radii
    let c = 0, r = 0;  // Center and right boundary
    
    for (let i = 1; i < n - 1; i++) {
        if (i < r) {
            p[i] = Math.min(r - i, p[2 * c - i]);
        }
        
        // Expand around center i
        while (t[i + p[i] + 1] === t[i - p[i] - 1]) {
            p[i]++;
        }
        
        // Update center and boundary
        if (i + p[i] > r) {
            c = i;
            r = i + p[i];
        }
    }
    
    // Find the maximum palindrome
    const maxLen = Math.max(...p);
    const centerIndex = p.indexOf(maxLen);
    const start = (centerIndex - maxLen) / 2;
    
    return s.substring(start, start + maxLen);
}
// Time: O(n), Space: O(n)
```

---

<a name="week-3"></a>
## Chapter 4: Week 3 — Graphs & Advanced Algorithms

### Day 15-17: Graph Theory

#### Graph Representations

```javascript
// Adjacency List (Most Common)
class Graph {
    constructor(directed = false) {
        this.adjList = new Map();
        this.directed = directed;
    }
    
    addVertex(v) {
        if (!this.adjList.has(v)) {
            this.adjList.set(v, []);
        }
    }
    
    addEdge(u, v, weight = 1) {
        this.addVertex(u);
        this.addVertex(v);
        this.adjList.get(u).push({ node: v, weight });
        if (!this.directed) {
            this.adjList.get(v).push({ node: u, weight });
        }
    }
}

// Adjacency Matrix (Dense graphs)
class GraphMatrix {
    constructor(n) {
        this.n = n;
        this.matrix = Array.from({ length: n }, () => 
            Array(n).fill(0)
        );
    }
    
    addEdge(u, v, weight = 1) {
        this.matrix[u][v] = weight;
        this.matrix[v][u] = weight;  // Remove for directed
    }
}
```

#### BFS and DFS Templates

```javascript
// BFS Template
function bfs(graph, start) {
    const visited = new Set([start]);
    const queue = [start];
    const result = [];
    
    while (queue.length) {
        const node = queue.shift();
        result.push(node);
        
        for (let neighbor of graph.get(node) || []) {
            if (!visited.has(neighbor)) {
                visited.add(neighbor);
                queue.push(neighbor);
            }
        }
    }
    return result;
}

// DFS Template (Iterative)
function dfs(graph, start) {
    const visited = new Set();
    const stack = [start];
    const result = [];
    
    while (stack.length) {
        const node = stack.pop();
        if (visited.has(node)) continue;
        
        visited.add(node);
        result.push(node);
        
        for (let neighbor of graph.get(node) || []) {
            if (!visited.has(neighbor)) {
                stack.push(neighbor);
            }
        }
    }
    return result;
}

// DFS Template (Recursive)
function dfsRecursive(graph, node, visited = new Set(), result = []) {
    if (visited.has(node)) return result;
    
    visited.add(node);
    result.push(node);
    
    for (let neighbor of graph.get(node) || []) {
        dfsRecursive(graph, neighbor, visited, result);
    }
    return result;
}
```

#### Topological Sort

```javascript
// Kahn's Algorithm (BFS)
function topologicalSortKahn(numCourses, prerequisites) {
    const graph = new Map();
    const inDegree = new Array(numCourses).fill(0);
    
    // Build graph
    for (let [course, prereq] of prerequisites) {
        if (!graph.has(prereq)) graph.set(prereq, []);
        graph.get(prereq).push(course);
        inDegree[course]++;
    }
    
    // Start with nodes having no dependencies
    const queue = [];
    for (let i = 0; i < numCourses; i++) {
        if (inDegree[i] === 0) queue.push(i);
    }
    
    const result = [];
    while (queue.length) {
        const node = queue.shift();
        result.push(node);
        
        for (let neighbor of graph.get(node) || []) {
            inDegree[neighbor]--;
            if (inDegree[neighbor] === 0) {
                queue.push(neighbor);
            }
        }
    }
    
    // Check for cycle
    return result.length === numCourses ? result : [];
}

// DFS Approach
function topologicalSortDFS(numCourses, prerequisites) {
    const graph = new Map();
    for (let [course, prereq] of prerequisites) {
        if (!graph.has(prereq)) graph.set(prereq, []);
        graph.get(prereq).push(course);
    }
    
    const visited = new Set();
    const visiting = new Set();  // For cycle detection
    const result = [];
    
    function dfs(node) {
        if (visiting.has(node)) return false;  // Cycle
        if (visited.has(node)) return true;
        
        visiting.add(node);
        for (let neighbor of graph.get(node) || []) {
            if (!dfs(neighbor)) return false;
        }
        visiting.delete(node);
        visited.add(node);
        result.unshift(node);  // Add to front
        return true;
    }
    
    for (let i = 0; i < numCourses; i++) {
        if (!dfs(i)) return [];
    }
    return result;
}
```

#### Shortest Path Algorithms

```javascript
// Dijkstra's Algorithm
function dijkstra(graph, start) {
    const distances = new Map();
    const visited = new Set();
    const pq = new MinHeapCustom((a, b) => a[1] - b[1]);
    
    // Initialize
    for (let node of graph.keys()) {
        distances.set(node, Infinity);
    }
    distances.set(start, 0);
    pq.push([start, 0]);
    
    while (pq.size() > 0) {
        const [node, dist] = pq.pop();
        
        if (visited.has(node)) continue;
        visited.add(node);
        
        for (let { node: neighbor, weight } of graph.get(node) || []) {
            const newDist = dist + weight;
            if (newDist < distances.get(neighbor)) {
                distances.set(neighbor, newDist);
                pq.push([neighbor, newDist]);
            }
        }
    }
    
    return distances;
}

// Bellman-Ford (Handles negative weights)
function bellmanFord(n, edges, start) {
    const distances = new Array(n).fill(Infinity);
    distances[start] = 0;
    
    // Relax all edges n-1 times
    for (let i = 0; i < n - 1; i++) {
        for (let [u, v, weight] of edges) {
            if (distances[u] !== Infinity && 
                distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight;
            }
        }
    }
    
    // Check for negative cycles
    for (let [u, v, weight] of edges) {
        if (distances[u] !== Infinity && 
            distances[u] + weight < distances[v]) {
            return null;  // Negative cycle exists
        }
    }
    
    return distances;
}

// Floyd-Warshall (All pairs shortest path)
function floydWarshall(graph) {
    const n = graph.length;
    const dist = graph.map(row => [...row]);
    
    for (let k = 0; k < n; k++) {
        for (let i = 0; i < n; i++) {
            for (let j = 0; j < n; j++) {
                if (dist[i][k] + dist[k][j] < dist[i][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j];
                }
            }
        }
    }
    
    return dist;
}
// Time: O(V³)
```

#### Union Find (Disjoint Set)

```javascript
class UnionFind {
    constructor(n) {
        this.parent = Array.from({ length: n }, (_, i) => i);
        this.rank = new Array(n).fill(0);
        this.count = n;  // Number of components
    }
    
    find(x) {
        if (this.parent[x] !== x) {
            this.parent[x] = this.find(this.parent[x]);  // Path compression
        }
        return this.parent[x];
    }
    
    union(x, y) {
        const rootX = this.find(x);
        const rootY = this.find(y);
        
        if (rootX === rootY) return false;
        
        // Union by rank
        if (this.rank[rootX] < this.rank[rootY]) {
            this.parent[rootX] = rootY;
        } else if (this.rank[rootX] > this.rank[rootY]) {
            this.parent[rootY] = rootX;
        } else {
            this.parent[rootY] = rootX;
            this.rank[rootX]++;
        }
        
        this.count--;
        return true;
    }
    
    connected(x, y) {
        return this.find(x) === this.find(y);
    }
}

// Number of Islands using Union Find
function numIslands(grid) {
    if (!grid.length) return 0;
    
    const m = grid.length, n = grid[0].length;
    const uf = new UnionFind(m * n);
    let islands = 0;
    
    const getIndex = (i, j) => i * n + j;
    
    for (let i = 0; i < m; i++) {
        for (let j = 0; j < n; j++) {
            if (grid[i][j] === '1') {
                islands++;
                // Union with right and down neighbors
                if (j + 1 < n && grid[i][j + 1] === '1') {
                    if (uf.union(getIndex(i, j), getIndex(i, j + 1))) {
                        islands--;
                    }
                }
                if (i + 1 < m && grid[i + 1][j] === '1') {
                    if (uf.union(getIndex(i, j), getIndex(i + 1, j))) {
                        islands--;
                    }
                }
            }
        }
    }
    
    return islands;
}
```

---

### Day 17.5: Minimum Spanning Tree Algorithms

#### Kruskal's Algorithm (Union-Find Based)

```javascript
function kruskalMST(n, edges) {
    // Sort edges by weight
    edges.sort((a, b) => a[2] - b[2]);
    
    const uf = new UnionFind(n);
    const mstEdges = [];
    let totalCost = 0;
    
    for (const [u, v, weight] of edges) {
        if (uf.union(u, v)) {
            mstEdges.push([u, v, weight]);
            totalCost += weight;
            
            // MST has exactly n-1 edges
            if (mstEdges.length === n - 1) break;
        }
    }
    
    // Check if MST exists (graph is connected)
    if (mstEdges.length < n - 1) return null;
    
    return { edges: mstEdges, cost: totalCost };
}
// Time: O(E log E) for sorting
```

#### Prim's Algorithm (Heap Based)

```javascript
function primMST(n, adjList) {
    const visited = new Set();
    const mstEdges = [];
    let totalCost = 0;
    
    // Min heap: [weight, from, to]
    const pq = new MinHeap((a, b) => a[0] - b[0]);
    
    // Start from node 0
    visited.add(0);
    for (const [neighbor, weight] of adjList[0] || []) {
        pq.push([weight, 0, neighbor]);
    }
    
    while (pq.size() > 0 && visited.size < n) {
        const [weight, from, to] = pq.pop();
        
        if (visited.has(to)) continue;
        
        visited.add(to);
        mstEdges.push([from, to, weight]);
        totalCost += weight;
        
        // Add all edges from the new vertex
        for (const [neighbor, edgeWeight] of adjList[to] || []) {
            if (!visited.has(neighbor)) {
                pq.push([edgeWeight, to, neighbor]);
            }
        }
    }
    
    return visited.size === n 
        ? { edges: mstEdges, cost: totalCost }
        : null;  // Graph not connected
}
// Time: O(E log V)
```

#### Min Cost to Connect All Points (MST Application)

```javascript
function minCostConnectPoints(points) {
    const n = points.length;
    const dist = (i, j) => 
        Math.abs(points[i][0] - points[j][0]) + 
        Math.abs(points[i][1] - points[j][1]);
    
    // Prim's algorithm
    const visited = new Set([0]);
    const pq = new MinHeap();
    
    // Add all edges from point 0
    for (let i = 1; i < n; i++) {
        pq.push([dist(0, i), i]);
    }
    
    let totalCost = 0;
    
    while (visited.size < n && pq.size() > 0) {
        const [cost, node] = pq.pop();
        
        if (visited.has(node)) continue;
        
        visited.add(node);
        totalCost += cost;
        
        for (let i = 0; i < n; i++) {
            if (!visited.has(i)) {
                pq.push([dist(node, i), i]);
            }
        }
    }
    
    return totalCost;
}
```

#### MST Algorithm Selection Guide

```
| Algorithm | Best For | Time Complexity |
|-----------|----------|-----------------|
| Kruskal's | Sparse graphs (E << V²) | O(E log E) |
| Prim's    | Dense graphs (E ≈ V²), when starting point matters | O(E log V) |
```

---

### Day 18-19: Dynamic Programming

#### DP Patterns and Templates

```javascript
// 1D DP Template
function dp1D(n) {
    const dp = new Array(n + 1).fill(0);
    dp[0] = /* base case */;
    
    for (let i = 1; i <= n; i++) {
        dp[i] = /* transition from previous states */;
    }
    return dp[n];
}

// 2D DP Template
function dp2D(m, n) {
    const dp = Array.from({ length: m + 1 }, () => 
        new Array(n + 1).fill(0)
    );
    
    // Base cases
    for (let i = 0; i <= m; i++) dp[i][0] = /* base */;
    for (let j = 0; j <= n; j++) dp[0][j] = /* base */;
    
    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            dp[i][j] = /* transition */;
        }
    }
    return dp[m][n];
}
```

#### Classic DP Problems

```javascript
// Coin Change
function coinChange(coins, amount) {
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
// Time: O(amount * coins), Space: O(amount)

// 0/1 Knapsack
function knapsack(weights, values, capacity) {
    const n = weights.length;
    const dp = Array.from({ length: n + 1 }, () => 
        new Array(capacity + 1).fill(0)
    );
    
    for (let i = 1; i <= n; i++) {
        for (let w = 0; w <= capacity; w++) {
            // Don't take item i
            dp[i][w] = dp[i - 1][w];
            
            // Take item i (if possible)
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

// Space Optimized Knapsack
function knapsackOptimized(weights, values, capacity) {
    const dp = new Array(capacity + 1).fill(0);
    
    for (let i = 0; i < weights.length; i++) {
        // Traverse backwards to avoid using same item twice
        for (let w = capacity; w >= weights[i]; w--) {
            dp[w] = Math.max(dp[w], dp[w - weights[i]] + values[i]);
        }
    }
    
    return dp[capacity];
}

// Longest Increasing Subsequence
function lengthOfLIS(nums) {
    // O(n²) DP
    const dp = new Array(nums.length).fill(1);
    let maxLen = 1;
    
    for (let i = 1; i < nums.length; i++) {
        for (let j = 0; j < i; j++) {
            if (nums[j] < nums[i]) {
                dp[i] = Math.max(dp[i], dp[j] + 1);
            }
        }
        maxLen = Math.max(maxLen, dp[i]);
    }
    return maxLen;
}

// O(n log n) Binary Search Approach
function lengthOfLISOptimized(nums) {
    const tails = [];
    
    for (let num of nums) {
        let left = 0, right = tails.length;
        while (left < right) {
            const mid = (left + right) >> 1;
            if (tails[mid] < num) left = mid + 1;
            else right = mid;
        }
        
        if (left === tails.length) tails.push(num);
        else tails[left] = num;
    }
    
    return tails.length;
}

// Edit Distance
function minDistance(word1, word2) {
    const m = word1.length, n = word2.length;
    const dp = Array.from({ length: m + 1 }, () => 
        new Array(n + 1).fill(0)
    );
    
    // Base cases
    for (let i = 0; i <= m; i++) dp[i][0] = i;
    for (let j = 0; j <= n; j++) dp[0][j] = j;
    
    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            if (word1[i - 1] === word2[j - 1]) {
                dp[i][j] = dp[i - 1][j - 1];
            } else {
                dp[i][j] = 1 + Math.min(
                    dp[i - 1][j],     // Delete
                    dp[i][j - 1],     // Insert
                    dp[i - 1][j - 1]  // Replace
                );
            }
        }
    }
    
    return dp[m][n];
}

// Longest Palindromic Substring
function longestPalindrome(s) {
    const n = s.length;
    let start = 0, maxLen = 1;
    
    // Expand around center
    function expandAroundCenter(left, right) {
        while (left >= 0 && right < n && s[left] === s[right]) {
            if (right - left + 1 > maxLen) {
                start = left;
                maxLen = right - left + 1;
            }
            left--;
            right++;
        }
    }
    
    for (let i = 0; i < n; i++) {
        expandAroundCenter(i, i);     // Odd length
        expandAroundCenter(i, i + 1); // Even length
    }
    
    return s.substring(start, start + maxLen);
}
// Time: O(n²), Space: O(1)
```

---

### Day 20-21: Greedy & Backtracking

#### Greedy Patterns

```javascript
// Activity Selection
function activitySelection(activities) {
    // Sort by end time
    activities.sort((a, b) => a.end - b.end);
    
    const selected = [activities[0]];
    let lastEnd = activities[0].end;
    
    for (let i = 1; i < activities.length; i++) {
        if (activities[i].start >= lastEnd) {
            selected.push(activities[i]);
            lastEnd = activities[i].end;
        }
    }
    
    return selected;
}

// Jump Game
function canJump(nums) {
    let maxReach = 0;
    
    for (let i = 0; i < nums.length; i++) {
        if (i > maxReach) return false;
        maxReach = Math.max(maxReach, i + nums[i]);
        if (maxReach >= nums.length - 1) return true;
    }
    
    return maxReach >= nums.length - 1;
}
```

#### Backtracking Templates

```javascript
// General Backtracking Template
function backtrack(candidates, path, result, start) {
    if (/* goal condition */) {
        result.push([...path]);
        return;
    }
    
    for (let i = start; i < candidates.length; i++) {
        // Skip duplicates / pruning
        if (/* skip condition */) continue;
        
        path.push(candidates[i]);          // Make choice
        backtrack(candidates, path, result, i + 1);  // Recurse
        path.pop();                         // Undo choice
    }
}

// Subsets
function subsets(nums) {
    const result = [];
    
    function backtrack(start, path) {
        result.push([...path]);
        
        for (let i = start; i < nums.length; i++) {
            path.push(nums[i]);
            backtrack(i + 1, path);
            path.pop();
        }
    }
    
    backtrack(0, []);
    return result;
}

// Permutations
function permute(nums) {
    const result = [];
    const used = new Array(nums.length).fill(false);
    
    function backtrack(path) {
        if (path.length === nums.length) {
            result.push([...path]);
            return;
        }
        
        for (let i = 0; i < nums.length; i++) {
            if (used[i]) continue;
            
            used[i] = true;
            path.push(nums[i]);
            backtrack(path);
            path.pop();
            used[i] = false;
        }
    }
    
    backtrack([]);
    return result;
}

// N-Queens
function solveNQueens(n) {
    const result = [];
    const board = Array.from({ length: n }, () => '.'.repeat(n));
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
            
            cols.add(col);
            diag1.add(row - col);
            diag2.add(row + col);
            board[row] = board[row].substring(0, col) + 'Q' + board[row].substring(col + 1);
            
            backtrack(row + 1);
            
            cols.delete(col);
            diag1.delete(row - col);
            diag2.delete(row + col);
            board[row] = board[row].substring(0, col) + '.' + board[row].substring(col + 1);
        }
    }
    
    backtrack(0);
    return result;
}
```

---

<a name="week-4"></a>
## Chapter 5: Week 4 — Senior-Level Engineering DSA

### Day 22-23: Tries & Advanced Trees

#### Trie Implementation

```javascript
class TrieNode {
    constructor() {
        this.children = new Map();
        this.isEnd = false;
        this.count = 0;  // For prefix count
    }
}

class Trie {
    constructor() {
        this.root = new TrieNode();
    }
    
    insert(word) {
        let node = this.root;
        for (let char of word) {
            if (!node.children.has(char)) {
                node.children.set(char, new TrieNode());
            }
            node = node.children.get(char);
            node.count++;
        }
        node.isEnd = true;
    }
    
    search(word) {
        let node = this.root;
        for (let char of word) {
            if (!node.children.has(char)) return false;
            node = node.children.get(char);
        }
        return node.isEnd;
    }
    
    startsWith(prefix) {
        let node = this.root;
        for (let char of prefix) {
            if (!node.children.has(char)) return false;
            node = node.children.get(char);
        }
        return true;
    }
    
    // Get all words with prefix
    getWordsWithPrefix(prefix) {
        let node = this.root;
        for (let char of prefix) {
            if (!node.children.has(char)) return [];
            node = node.children.get(char);
        }
        
        const words = [];
        this._collectWords(node, prefix, words);
        return words;
    }
    
    _collectWords(node, prefix, words) {
        if (node.isEnd) words.push(prefix);
        
        for (let [char, child] of node.children) {
            this._collectWords(child, prefix + char, words);
        }
    }
}
```

#### Autocomplete System

```javascript
class AutocompleteSystem {
    constructor(sentences, times) {
        this.trie = new Trie();
        this.sentenceFreq = new Map();
        this.currentInput = '';
        
        for (let i = 0; i < sentences.length; i++) {
            this.sentenceFreq.set(sentences[i], times[i]);
            this.trie.insert(sentences[i]);
        }
    }
    
    input(c) {
        if (c === '#') {
            // End of input, save sentence
            this.sentenceFreq.set(
                this.currentInput, 
                (this.sentenceFreq.get(this.currentInput) || 0) + 1
            );
            this.trie.insert(this.currentInput);
            this.currentInput = '';
            return [];
        }
        
        this.currentInput += c;
        
        // Get all sentences with current prefix
        const candidates = this.trie.getWordsWithPrefix(this.currentInput);
        
        // Sort by frequency (desc), then alphabetically
        candidates.sort((a, b) => {
            const freqDiff = this.sentenceFreq.get(b) - this.sentenceFreq.get(a);
            return freqDiff !== 0 ? freqDiff : a.localeCompare(b);
        });
        
        return candidates.slice(0, 3);  // Top 3 suggestions
    }
}
```

#### Segment Tree

```javascript
class SegmentTree {
    constructor(arr) {
        this.n = arr.length;
        this.tree = new Array(4 * this.n).fill(0);
        this.build(arr, 0, 0, this.n - 1);
    }
    
    build(arr, node, start, end) {
        if (start === end) {
            this.tree[node] = arr[start];
            return;
        }
        
        const mid = (start + end) >> 1;
        const leftChild = 2 * node + 1;
        const rightChild = 2 * node + 2;
        
        this.build(arr, leftChild, start, mid);
        this.build(arr, rightChild, mid + 1, end);
        
        this.tree[node] = this.tree[leftChild] + this.tree[rightChild];
    }
    
    update(index, value, node = 0, start = 0, end = this.n - 1) {
        if (start === end) {
            this.tree[node] = value;
            return;
        }
        
        const mid = (start + end) >> 1;
        const leftChild = 2 * node + 1;
        const rightChild = 2 * node + 2;
        
        if (index <= mid) {
            this.update(index, value, leftChild, start, mid);
        } else {
            this.update(index, value, rightChild, mid + 1, end);
        }
        
        this.tree[node] = this.tree[leftChild] + this.tree[rightChild];
    }
    
    query(l, r, node = 0, start = 0, end = this.n - 1) {
        if (r < start || l > end) return 0;  // Out of range
        
        if (l <= start && end <= r) return this.tree[node];  // Fully in range
        
        const mid = (start + end) >> 1;
        const leftChild = 2 * node + 1;
        const rightChild = 2 * node + 2;
        
        return this.query(l, r, leftChild, start, mid) + 
               this.query(l, r, rightChild, mid + 1, end);
    }
}
// Build: O(n), Update: O(log n), Query: O(log n)
```

---

### Day 24-25: Advanced Data Structures

#### LFU Cache

```javascript
class LFUCache {
    constructor(capacity) {
        this.capacity = capacity;
        this.minFreq = 0;
        this.cache = new Map();           // key -> {value, freq}
        this.freqMap = new Map();         // freq -> Set of keys (insertion order)
    }
    
    _updateFreq(key) {
        const { value, freq } = this.cache.get(key);
        
        // Remove from current frequency list
        this.freqMap.get(freq).delete(key);
        if (this.freqMap.get(freq).size === 0) {
            this.freqMap.delete(freq);
            if (this.minFreq === freq) this.minFreq++;
        }
        
        // Add to new frequency list
        const newFreq = freq + 1;
        this.cache.set(key, { value, freq: newFreq });
        if (!this.freqMap.has(newFreq)) {
            this.freqMap.set(newFreq, new Set());
        }
        this.freqMap.get(newFreq).add(key);
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
            return;
        }
        
        if (this.cache.size >= this.capacity) {
            // Evict LFU key
            const keysWithMinFreq = this.freqMap.get(this.minFreq);
            const keyToEvict = keysWithMinFreq.values().next().value;
            keysWithMinFreq.delete(keyToEvict);
            if (keysWithMinFreq.size === 0) {
                this.freqMap.delete(this.minFreq);
            }
            this.cache.delete(keyToEvict);
        }
        
        // Add new key
        this.cache.set(key, { value, freq: 1 });
        if (!this.freqMap.has(1)) {
            this.freqMap.set(1, new Set());
        }
        this.freqMap.get(1).add(key);
        this.minFreq = 1;
    }
}
// All operations: O(1)
```

#### Bloom Filter

```javascript
class BloomFilter {
    constructor(size = 1000, numHashes = 3) {
        this.size = size;
        this.numHashes = numHashes;
        this.bits = new Array(size).fill(false);
    }
    
    // Multiple hash functions using double hashing
    _hash(item, i) {
        const str = String(item);
        let h1 = 0, h2 = 0;
        
        for (let j = 0; j < str.length; j++) {
            h1 = (h1 * 31 + str.charCodeAt(j)) % this.size;
            h2 = (h2 * 37 + str.charCodeAt(j)) % this.size;
        }
        
        return (Math.abs(h1 + i * h2)) % this.size;
    }
    
    add(item) {
        for (let i = 0; i < this.numHashes; i++) {
            this.bits[this._hash(item, i)] = true;
        }
    }
    
    mightContain(item) {
        for (let i = 0; i < this.numHashes; i++) {
            if (!this.bits[this._hash(item, i)]) {
                return false;  // Definitely not in set
            }
        }
        return true;  // Probably in set (may be false positive)
    }
    
    // False positive rate ≈ (1 - e^(-kn/m))^k
    // k = number of hash functions
    // n = number of items
    // m = size of bit array
}
```

#### Skip List

```javascript
class SkipListNode {
    constructor(val, level) {
        this.val = val;
        this.forward = new Array(level + 1).fill(null);
    }
}

class SkipList {
    constructor(maxLevel = 16, p = 0.5) {
        this.maxLevel = maxLevel;
        this.p = p;
        this.level = 0;
        this.head = new SkipListNode(-Infinity, maxLevel);
    }
    
    randomLevel() {
        let level = 0;
        while (Math.random() < this.p && level < this.maxLevel) {
            level++;
        }
        return level;
    }
    
    search(target) {
        let curr = this.head;
        
        for (let i = this.level; i >= 0; i--) {
            while (curr.forward[i] && curr.forward[i].val < target) {
                curr = curr.forward[i];
            }
        }
        
        curr = curr.forward[0];
        return curr && curr.val === target;
    }
    
    add(num) {
        const update = new Array(this.maxLevel + 1).fill(null);
        let curr = this.head;
        
        for (let i = this.level; i >= 0; i--) {
            while (curr.forward[i] && curr.forward[i].val < num) {
                curr = curr.forward[i];
            }
            update[i] = curr;
        }
        
        const newLevel = this.randomLevel();
        if (newLevel > this.level) {
            for (let i = this.level + 1; i <= newLevel; i++) {
                update[i] = this.head;
            }
            this.level = newLevel;
        }
        
        const newNode = new SkipListNode(num, newLevel);
        for (let i = 0; i <= newLevel; i++) {
            newNode.forward[i] = update[i].forward[i];
            update[i].forward[i] = newNode;
        }
    }
    
    erase(num) {
        const update = new Array(this.maxLevel + 1).fill(null);
        let curr = this.head;
        
        for (let i = this.level; i >= 0; i--) {
            while (curr.forward[i] && curr.forward[i].val < num) {
                curr = curr.forward[i];
            }
            update[i] = curr;
        }
        
        curr = curr.forward[0];
        if (!curr || curr.val !== num) return false;
        
        for (let i = 0; i <= this.level; i++) {
            if (update[i].forward[i] !== curr) break;
            update[i].forward[i] = curr.forward[i];
        }
        
        while (this.level > 0 && !this.head.forward[this.level]) {
            this.level--;
        }
        
        return true;
    }
}
// Average: O(log n) for search, insert, delete
```

---

### Day 25.5: Math & Number Theory (Critical for Interviews)

#### GCD and LCM

```javascript
// Euclidean Algorithm for GCD
function gcd(a, b) {
    while (b !== 0) {
        [a, b] = [b, a % b];
    }
    return a;
}

// Extended Euclidean Algorithm
// Returns [gcd, x, y] where a*x + b*y = gcd(a, b)
function extendedGcd(a, b) {
    if (b === 0) return [a, 1, 0];
    
    const [g, x, y] = extendedGcd(b, a % b);
    return [g, y, x - Math.floor(a / b) * y];
}

// LCM
const lcm = (a, b) => (a * b) / gcd(a, b);

// GCD of array
const gcdArray = arr => arr.reduce((acc, val) => gcd(acc, val));
```

#### Prime Numbers

```javascript
// Check if Prime
function isPrime(n) {
    if (n < 2) return false;
    if (n === 2) return true;
    if (n % 2 === 0) return false;
    
    for (let i = 3; i * i <= n; i += 2) {
        if (n % i === 0) return false;
    }
    return true;
}
// Time: O(√n)

// Sieve of Eratosthenes
function sieveOfEratosthenes(n) {
    const isPrime = new Array(n + 1).fill(true);
    isPrime[0] = isPrime[1] = false;
    
    for (let i = 2; i * i <= n; i++) {
        if (isPrime[i]) {
            for (let j = i * i; j <= n; j += i) {
                isPrime[j] = false;
            }
        }
    }
    
    // Return list of primes
    const primes = [];
    for (let i = 2; i <= n; i++) {
        if (isPrime[i]) primes.push(i);
    }
    return primes;
}
// Time: O(n log log n), Space: O(n)

// Prime Factorization
function primeFactors(n) {
    const factors = [];
    
    // Check for 2
    while (n % 2 === 0) {
        factors.push(2);
        n /= 2;
    }
    
    // Check odd numbers
    for (let i = 3; i * i <= n; i += 2) {
        while (n % i === 0) {
            factors.push(i);
            n /= i;
        }
    }
    
    // If n is still > 1, it's a prime factor
    if (n > 1) factors.push(n);
    
    return factors;
}
```

#### Modular Arithmetic

```javascript
// Modular Exponentiation (a^n mod m)
function modPow(a, n, mod) {
    let result = 1n;
    a = BigInt(a) % BigInt(mod);
    n = BigInt(n);
    mod = BigInt(mod);
    
    while (n > 0n) {
        if (n & 1n) {
            result = (result * a) % mod;
        }
        n >>= 1n;
        a = (a * a) % mod;
    }
    return Number(result);
}

// Modular Inverse using Fermat's Little Theorem
// Only works when mod is prime
function modInverse(a, mod) {
    return modPow(a, mod - 2, mod);
}

// Modular Division
function modDivide(a, b, mod) {
    return (a * modInverse(b, mod)) % mod;
}

// Safe modular operations
const MOD = 1e9 + 7;
const modAdd = (a, b) => ((a % MOD) + (b % MOD)) % MOD;
const modSub = (a, b) => ((a % MOD) - (b % MOD) + MOD) % MOD;
const modMul = (a, b) => ((a % MOD) * (b % MOD)) % MOD;
```

#### Combinatorics

```javascript
// nCr with mod (Pascal's Triangle approach)
function nCrPascal(n, r, mod = 1e9 + 7) {
    const C = Array.from({ length: n + 1 }, () => new Array(r + 1).fill(0));
    
    for (let i = 0; i <= n; i++) {
        C[i][0] = 1;
        for (let j = 1; j <= Math.min(i, r); j++) {
            C[i][j] = (C[i - 1][j - 1] + C[i - 1][j]) % mod;
        }
    }
    return C[n][r];
}

// nCr using factorial and inverse (for large n)
function nCrFactorial(n, r, mod = 1e9 + 7) {
    if (r > n) return 0;
    if (r === 0 || r === n) return 1;
    
    // Precompute factorials
    const fact = [1];
    for (let i = 1; i <= n; i++) {
        fact[i] = (fact[i - 1] * i) % mod;
    }
    
    const invFact = n => modPow(n, mod - 2, mod);
    
    return (fact[n] * invFact(fact[r]) % mod) * invFact(fact[n - r]) % mod;
}

// Generate all permutations count
const permutations = (n, r) => {
    let result = 1;
    for (let i = 0; i < r; i++) {
        result *= (n - i);
    }
    return result;
};
```

#### Common Math Interview Problems

```javascript
// Integer Square Root (Binary Search)
function mySqrt(x) {
    if (x < 2) return x;
    
    let left = 1, right = Math.floor(x / 2);
    while (left <= right) {
        const mid = left + Math.floor((right - left) / 2);
        if (mid === x / mid) return mid;
        else if (mid < x / mid) left = mid + 1;
        else right = mid - 1;
    }
    return right;
}

// Power of Three
function isPowerOfThree(n) {
    if (n < 1) return false;
    while (n % 3 === 0) {
        n /= 3;
    }
    return n === 1;
}

// Count Trailing Zeros in Factorial
function trailingZeroes(n) {
    let count = 0;
    while (n >= 5) {
        n = Math.floor(n / 5);
        count += n;
    }
    return count;
}
// Trailing zeros = number of 5s in prime factorization

// Happy Number
function isHappy(n) {
    const seen = new Set();
    
    while (n !== 1 && !seen.has(n)) {
        seen.add(n);
        n = sumOfSquares(n);
    }
    return n === 1;
    
    function sumOfSquares(num) {
        let sum = 0;
        while (num > 0) {
            const digit = num % 10;
            sum += digit * digit;
            num = Math.floor(num / 10);
        }
        return sum;
    }
}

// Ugly Number II (Using Min Heap or DP)
function nthUglyNumber(n) {
    const dp = [1];
    let i2 = 0, i3 = 0, i5 = 0;
    
    while (dp.length < n) {
        const next2 = dp[i2] * 2;
        const next3 = dp[i3] * 3;
        const next5 = dp[i5] * 5;
        
        const next = Math.min(next2, next3, next5);
        dp.push(next);
        
        if (next === next2) i2++;
        if (next === next3) i3++;
        if (next === next5) i5++;
    }
    
    return dp[n - 1];
}
```

---

### Day 26-27: Concurrency Structures (Node.js)

#### Rate Limiter (Token Bucket)

```javascript
class TokenBucketRateLimiter {
    constructor(capacity, refillRate) {
        this.capacity = capacity;       // Max tokens
        this.refillRate = refillRate;   // Tokens per second
        this.tokens = capacity;
        this.lastRefill = Date.now();
    }
    
    _refill() {
        const now = Date.now();
        const elapsed = (now - this.lastRefill) / 1000;
        const tokensToAdd = elapsed * this.refillRate;
        this.tokens = Math.min(this.capacity, this.tokens + tokensToAdd);
        this.lastRefill = now;
    }
    
    async acquire(tokens = 1) {
        this._refill();
        
        if (this.tokens >= tokens) {
            this.tokens -= tokens;
            return true;
        }
        return false;
    }
}

// Sliding Window Rate Limiter (Redis-like)
class SlidingWindowRateLimiter {
    constructor(windowMs, maxRequests) {
        this.windowMs = windowMs;
        this.maxRequests = maxRequests;
        this.requests = new Map();  // userId -> [timestamps]
    }
    
    isAllowed(userId) {
        const now = Date.now();
        const windowStart = now - this.windowMs;
        
        if (!this.requests.has(userId)) {
            this.requests.set(userId, []);
        }
        
        const userRequests = this.requests.get(userId);
        
        // Remove old requests outside window
        while (userRequests.length && userRequests[0] < windowStart) {
            userRequests.shift();
        }
        
        if (userRequests.length < this.maxRequests) {
            userRequests.push(now);
            return true;
        }
        
        return false;
    }
}
```

#### Async Queue (Producer-Consumer)

```javascript
class AsyncQueue {
    constructor(concurrency = 1) {
        this.concurrency = concurrency;
        this.running = 0;
        this.queue = [];
    }
    
    async push(task) {
        return new Promise((resolve, reject) => {
            this.queue.push({ task, resolve, reject });
            this._process();
        });
    }
    
    async _process() {
        if (this.running >= this.concurrency || this.queue.length === 0) {
            return;
        }
        
        const { task, resolve, reject } = this.queue.shift();
        this.running++;
        
        try {
            const result = await task();
            resolve(result);
        } catch (error) {
            reject(error);
        } finally {
            this.running--;
            this._process();
        }
    }
}

// Usage
const queue = new AsyncQueue(2);

async function processRequest(id) {
    return queue.push(async () => {
        // Simulate async work
        await new Promise(r => setTimeout(r, 1000));
        return `Processed ${id}`;
    });
}
```

#### Semaphore for Resource Limiting

```javascript
class Semaphore {
    constructor(permits) {
        this.permits = permits;
        this.queue = [];
    }
    
    async acquire() {
        if (this.permits > 0) {
            this.permits--;
            return;
        }
        
        // Wait for permit
        return new Promise(resolve => {
            this.queue.push(resolve);
        });
    }
    
    release() {
        if (this.queue.length > 0) {
            const resolve = this.queue.shift();
            resolve();
        } else {
            this.permits++;
        }
    }
    
    async withPermit(fn) {
        await this.acquire();
        try {
            return await fn();
        } finally {
            this.release();
        }
    }
}

// Database connection pool example
const dbSemaphore = new Semaphore(10);  // Max 10 connections

async function queryDatabase(sql) {
    return dbSemaphore.withPermit(async () => {
        // Execute database query
        const connection = await pool.getConnection();
        try {
            return await connection.query(sql);
        } finally {
            connection.release();
        }
    });
}
```

---

<a name="question-bank"></a>
## Chapter 6: Advanced Interview Question Bank

### Elite-Level Problems by Category

#### Arrays (Hard)
1. **Maximum Rectangle in Histogram** (LeetCode 84)
2. **Median of Two Sorted Arrays** (LeetCode 4)
3. **First Missing Positive** (LeetCode 41)
4. **Trapping Rain Water** (LeetCode 42)

#### Trees (Hard)
1. **Serialize and Deserialize Binary Tree** (LeetCode 297)
2. **Recover Binary Search Tree** (LeetCode 99)
3. **Binary Tree Maximum Path Sum** (LeetCode 124)

#### Graphs (Hard)
1. **Alien Dictionary** (LeetCode 269)
2. **Network Delay Time** (LeetCode 743)
3. **Critical Connections** (LeetCode 1192)
4. **Word Ladder II** (LeetCode 126)

#### Dynamic Programming (Hard)
1. **Regular Expression Matching** (LeetCode 10)
2. **Word Break II** (LeetCode 140)
3. **Burst Balloons** (LeetCode 312)
4. **Edit Distance** (LeetCode 72)

#### Design Problems
1. **LRU Cache** (LeetCode 146)
2. **LFU Cache** (LeetCode 460)
3. **Design Search Autocomplete** (LeetCode 642)
4. **Design Twitter** (LeetCode 355)

---

<a name="answering-strategy"></a>
## Chapter 7: How to Answer at Senior Level

### The STAR-T Framework for Coding

```
S - State the problem clearly
T - Think out loud (brute force first)
A - Analyze complexity and tradeoffs
R - Refine to optimal solution
T - Test with edge cases
```

### Sample Answer Structure

**Problem:** Design an LRU Cache

**Your Response:**

1. **Clarify Requirements**
   - "What operations need to be O(1)? Get and Put?"
   - "Is there a capacity limit?"
   - "Thread-safety needed?"

2. **State Brute Force**
   - "I could use an array and search linearly - O(n) get, O(n) put"

3. **Optimize**
   - "For O(1) access, I need a HashMap"
   - "For O(1) ordering, I need a Doubly Linked List"
   - "Combining: HashMap for O(1) lookup, DLL for O(1) removal/insertion"

4. **Code**
   - Write clean, modular code
   - Use meaningful variable names

5. **Analyze**
   - Time: O(1) for both operations
   - Space: O(capacity)

6. **Edge Cases**
   - Empty cache
   - Capacity = 0
   - Update existing key
   - Access order after update

---

<a name="mini-systems"></a>
## Chapter 8: Mini-Systems to Build

### 1. Rate Limiter (Node.js/Express)

```javascript
// Complete implementation with multiple strategies
const express = require('express');
const app = express();

// In-memory store (use Redis in production)
class RateLimiter {
    // ... (use implementation from Day 26-27)
}

const limiter = new SlidingWindowRateLimiter(60000, 100);

app.use((req, res, next) => {
    const userId = req.ip;
    if (limiter.isAllowed(userId)) {
        next();
    } else {
        res.status(429).json({ error: 'Rate limit exceeded' });
    }
});
```

### 2. In-Memory Database

```javascript
class InMemoryDB {
    constructor() {
        this.data = new Map();
        this.indexes = new Map();  // fieldName -> Map<value, Set<id>>
        this.transactions = [];
    }
    
    set(key, value) {
        const current = this.transactions.length > 0 
            ? this.transactions[this.transactions.length - 1] 
            : this.data;
        current.set(key, value);
    }
    
    get(key) {
        // Check transactions in reverse order
        for (let i = this.transactions.length - 1; i >= 0; i--) {
            if (this.transactions[i].has(key)) {
                return this.transactions[i].get(key);
            }
        }
        return this.data.get(key);
    }
    
    begin() {
        this.transactions.push(new Map());
    }
    
    commit() {
        if (this.transactions.length === 0) throw new Error('No transaction');
        const tx = this.transactions.pop();
        const target = this.transactions.length > 0 
            ? this.transactions[this.transactions.length - 1] 
            : this.data;
        
        for (let [key, value] of tx) {
            target.set(key, value);
        }
    }
    
    rollback() {
        if (this.transactions.length === 0) throw new Error('No transaction');
        this.transactions.pop();
    }
}
```

### 3. Graph-Based Recommendation Engine

```javascript
class RecommendationEngine {
    constructor() {
        this.userItems = new Map();  // userId -> Set of itemIds
        this.itemUsers = new Map();  // itemId -> Set of userIds
    }
    
    addInteraction(userId, itemId) {
        if (!this.userItems.has(userId)) {
            this.userItems.set(userId, new Set());
        }
        if (!this.itemUsers.has(itemId)) {
            this.itemUsers.set(itemId, new Set());
        }
        
        this.userItems.get(userId).add(itemId);
        this.itemUsers.get(itemId).add(userId);
    }
    
    getCollaborativeRecommendations(userId, limit = 10) {
        const userItems = this.userItems.get(userId) || new Set();
        const scores = new Map();  // itemId -> score
        
        // Find similar users (users who liked same items)
        for (let itemId of userItems) {
            for (let otherUserId of this.itemUsers.get(itemId) || []) {
                if (otherUserId === userId) continue;
                
                // Score items that similar users liked
                for (let otherItem of this.userItems.get(otherUserId) || []) {
                    if (!userItems.has(otherItem)) {
                        scores.set(otherItem, (scores.get(otherItem) || 0) + 1);
                    }
                }
            }
        }
        
        // Sort by score and return top items
        return [...scores.entries()]
            .sort((a, b) => b[1] - a[1])
            .slice(0, limit)
            .map(([itemId]) => itemId);
    }
}
```

---

<a name="patterns"></a>
## Chapter 9: Quick Reference — Essential Patterns

### Pattern Cheat Sheet

| Pattern | When to Use | Template |
|---------|-------------|----------|
| **Two Pointer** | Sorted arrays, finding pairs | `left = 0, right = n-1` |
| **Sliding Window** | Contiguous subarray/substring | `for right in range; while invalid: left++` |
| **Binary Search** | Sorted array, min/max problems | `while left < right: mid = (l+r)/2` |
| **BFS** | Shortest path, level-order | `queue`, process level by level |
| **DFS** | Path finding, tree traversal | `stack` or recursion |
| **Backtracking** | Permutations, combinations | `choose → explore → unchoose` |
| **DP** | Optimal substructure, overlapping | `dp[i] = f(dp[i-1], ...)` |
| **Monotonic Stack** | Next greater/smaller element | `while stack and condition: pop` |
| **Union Find** | Graph connectivity, components | `find with path compression, union by rank` |
| **Heap** | Top-K, median, scheduling | `heappush/heappop` |
| **Trie** | Prefix matching, autocomplete | `node.children[char]` |

### Complexity Quick Reference

| Operation | Array | Linked List | Hash Table | BST | Heap |
|-----------|-------|-------------|------------|-----|------|
| Access | O(1) | O(n) | N/A | O(log n) | N/A |
| Search | O(n) | O(n) | O(1)* | O(log n) | O(n) |
| Insert | O(n) | O(1) | O(1)* | O(log n) | O(log n) |
| Delete | O(n) | O(1) | O(1)* | O(log n) | O(log n) |

*Average case

---

## Final Notes

### Success Formula

1. **Understand deeply** - Don't memorize, understand why each approach works
2. **Practice consistently** - 2-3 problems daily > 20 problems in one day
3. **Simulate interviews** - Time yourself, explain out loud
4. **Build systems** - Apply DSA to real mini-projects
5. **Review patterns** - Before interviews, review this handbook

### Recommended Daily Schedule

- **Morning (30 min):** Review 1 pattern from handbook
- **Afternoon (1 hour):** Solve 2-3 problems of that pattern
- **Evening (30 min):** Review solutions, note key insights

---

*This handbook is designed for senior engineers preparing for technical interviews at top companies. Master these concepts, and you'll be ready for any coding challenge.*

**Version:** 1.0  
**Last Updated:** February 2026
