# 📅 Complete 30-Day DSA Study Plan for Senior Engineers

> **Target:** Senior Engineers (8+ YOE) preparing for FAANG/AI companies  
> **Time Commitment:** 3-4 hours/day  
> **Language:** JavaScript/Node.js

---

## 📊 Progress Tracker

| Week | Days | Focus Area | Status |
|------|------|-----------|--------|
| Week 1 | 1-7 | Foundations & Arrays | ⬜ |
| Week 2 | 8-14 | Core Structures | ⬜ |
| Week 3 | 15-21 | Graphs & Algorithms | ⬜ |
| Week 4 | 22-28 | Senior-Level DSA | ⬜ |
| Week 5 | 29-30 | Mock Interviews | ⬜ |

---

## 🎯 Week 1: Foundations & Arrays (Days 1-7)

### Day 1: Complexity Analysis & Big O Mastery
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Big O, Big Ω, Big Θ notation
- [ ] Time vs Space complexity
- [ ] Amortized analysis
- [ ] Best/Average/Worst case analysis
- [ ] Common complexity classes: O(1), O(log n), O(n), O(n log n), O(n²), O(2^n), O(n!)

#### 📖 Key Concepts
```
O(1) < O(log n) < O(n) < O(n log n) < O(n²) < O(2^n) < O(n!)

Amortized Analysis Example:
- Dynamic array doubling: O(1) amortized insert
- Union-Find with path compression: O(α(n)) ≈ O(1)
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Contains Duplicate | Easy | [LC 217](https://leetcode.com/problems/contains-duplicate/) | ⬜ |
| 2 | Valid Anagram | Easy | [LC 242](https://leetcode.com/problems/valid-anagram/) | ⬜ |
| 3 | Two Sum | Easy | [LC 1](https://leetcode.com/problems/two-sum/) | ⬜ |

#### 📝 Implementation Task
- [ ] Implement dynamic array with O(1) amortized push
- [ ] Measure time complexities of different operations

---

### Day 2: Two Pointer Pattern
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Two pointers from opposite ends
- [ ] Two pointers from same end (fast/slow)
- [ ] When to move which pointer
- [ ] Invariant maintenance

#### 📖 Pattern Template
```javascript
// Opposite ends (sorted array)
function twoPointers(arr, target) {
    let left = 0, right = arr.length - 1;
    while (left < right) {
        const sum = arr[left] + arr[right];
        if (sum === target) return [left, right];
        else if (sum < target) left++;
        else right--;
    }
    return [-1, -1];
}

// Same direction (remove duplicates)
function removeDuplicates(arr) {
    let slow = 0;
    for (let fast = 1; fast < arr.length; fast++) {
        if (arr[fast] !== arr[slow]) {
            slow++;
            arr[slow] = arr[fast];
        }
    }
    return slow + 1;
}
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Two Sum II (Sorted Array) | Medium | [LC 167](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) | ⬜ |
| 2 | Container With Most Water | Medium | [LC 11](https://leetcode.com/problems/container-with-most-water/) | ⬜ |
| 3 | 3Sum | Medium | [LC 15](https://leetcode.com/problems/3sum/) | ⬜ |
| 4 | Trapping Rain Water | Hard | [LC 42](https://leetcode.com/problems/trapping-rain-water/) | ⬜ |
| 5 | Remove Duplicates from Sorted Array II | Medium | [LC 80](https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/) | ⬜ |

---

### Day 3: Sliding Window Pattern
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Fixed size window
- [ ] Variable size window
- [ ] Expanding and contracting window
- [ ] Window state management (hashmap, counter)

#### 📖 Pattern Template
```javascript
// Variable Size Window Template
function slidingWindow(arr, condition) {
    let left = 0;
    let windowState = {}; // track window properties
    let result = 0;
    
    for (let right = 0; right < arr.length; right++) {
        // 1. Add right element to window
        updateWindow(arr[right]);
        
        // 2. Shrink window until valid
        while (!isValid(windowState)) {
            removeFromWindow(arr[left]);
            left++;
        }
        
        // 3. Update result
        result = Math.max(result, right - left + 1);
    }
    return result;
}
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Maximum Average Subarray I | Easy | [LC 643](https://leetcode.com/problems/maximum-average-subarray-i/) | ⬜ |
| 2 | Longest Substring Without Repeating | Medium | [LC 3](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | ⬜ |
| 3 | Minimum Window Substring | Hard | [LC 76](https://leetcode.com/problems/minimum-window-substring/) | ⬜ |
| 4 | Sliding Window Maximum | Hard | [LC 239](https://leetcode.com/problems/sliding-window-maximum/) | ⬜ |
| 5 | Permutation in String | Medium | [LC 567](https://leetcode.com/problems/permutation-in-string/) | ⬜ |

---

### Day 4: Binary Search Patterns
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Classic binary search
- [ ] Search for first/last occurrence
- [ ] Search in rotated array
- [ ] Binary search on answer (min/max problems)
- [ ] Bisect left vs bisect right

#### 📖 Pattern Templates
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

// Template 3: Binary search on answer
function minCapacityToShip(weights, days) {
    let left = Math.max(...weights);
    let right = weights.reduce((a, b) => a + b);
    
    while (left < right) {
        const mid = left + Math.floor((right - left) / 2);
        if (canShip(weights, days, mid)) right = mid;
        else left = mid + 1;
    }
    return left;
}
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Binary Search | Easy | [LC 704](https://leetcode.com/problems/binary-search/) | ⬜ |
| 2 | Search in Rotated Sorted Array | Medium | [LC 33](https://leetcode.com/problems/search-in-rotated-sorted-array/) | ⬜ |
| 3 | Find Minimum in Rotated Sorted Array | Medium | [LC 153](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/) | ⬜ |
| 4 | Capacity to Ship Packages | Medium | [LC 1011](https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/) | ⬜ |
| 5 | Median of Two Sorted Arrays | Hard | [LC 4](https://leetcode.com/problems/median-of-two-sorted-arrays/) | ⬜ |
| 6 | Find First and Last Position | Medium | [LC 34](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/) | ⬜ |

---

### Day 5: Prefix Sum & Matrix Techniques
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] 1D Prefix Sum
- [ ] 2D Prefix Sum
- [ ] Difference arrays
- [ ] Kadane's algorithm
- [ ] Matrix spiral traversal

#### 📖 Key Implementations
```javascript
// 1D Prefix Sum
function buildPrefixSum(arr) {
    const prefix = [0];
    for (let num of arr) {
        prefix.push(prefix[prefix.length - 1] + num);
    }
    return prefix;
}
// Range sum [l, r] = prefix[r+1] - prefix[l]

// 2D Prefix Sum
function build2DPrefix(matrix) {
    const m = matrix.length, n = matrix[0].length;
    const prefix = Array.from({length: m + 1}, () => Array(n + 1).fill(0));
    
    for (let i = 1; i <= m; i++) {
        for (let j = 1; j <= n; j++) {
            prefix[i][j] = matrix[i-1][j-1] + prefix[i-1][j] + 
                           prefix[i][j-1] - prefix[i-1][j-1];
        }
    }
    return prefix;
}

// Kadane's Algorithm
function maxSubArray(nums) {
    let maxSum = nums[0], currentSum = nums[0];
    for (let i = 1; i < nums.length; i++) {
        currentSum = Math.max(nums[i], currentSum + nums[i]);
        maxSum = Math.max(maxSum, currentSum);
    }
    return maxSum;
}
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Range Sum Query - Immutable | Easy | [LC 303](https://leetcode.com/problems/range-sum-query-immutable/) | ⬜ |
| 2 | Range Sum Query 2D - Immutable | Medium | [LC 304](https://leetcode.com/problems/range-sum-query-2d-immutable/) | ⬜ |
| 3 | Maximum Subarray | Medium | [LC 53](https://leetcode.com/problems/maximum-subarray/) | ⬜ |
| 4 | Product of Array Except Self | Medium | [LC 238](https://leetcode.com/problems/product-of-array-except-self/) | ⬜ |
| 5 | Subarray Sum Equals K | Medium | [LC 560](https://leetcode.com/problems/subarray-sum-equals-k/) | ⬜ |
| 6 | Spiral Matrix | Medium | [LC 54](https://leetcode.com/problems/spiral-matrix/) | ⬜ |

---

### Day 6: Linked Lists
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Singly vs Doubly Linked Lists
- [ ] Fast & Slow pointer (Floyd's)
- [ ] Reversal techniques
- [ ] Merge operations
- [ ] Dummy head technique

#### 📖 Key Patterns
```javascript
// Detect Cycle (Floyd's)
function hasCycle(head) {
    let slow = head, fast = head;
    while (fast && fast.next) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow === fast) return true;
    }
    return false;
}

// Find Cycle Start
function detectCycle(head) {
    let slow = head, fast = head;
    while (fast && fast.next) {
        slow = slow.next;
        fast = fast.next.next;
        if (slow === fast) {
            slow = head;
            while (slow !== fast) {
                slow = slow.next;
                fast = fast.next;
            }
            return slow;
        }
    }
    return null;
}

// Reverse with recursion
function reverseList(head) {
    if (!head || !head.next) return head;
    const newHead = reverseList(head.next);
    head.next.next = head;
    head.next = null;
    return newHead;
}
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Reverse Linked List | Easy | [LC 206](https://leetcode.com/problems/reverse-linked-list/) | ⬜ |
| 2 | Merge Two Sorted Lists | Easy | [LC 21](https://leetcode.com/problems/merge-two-sorted-lists/) | ⬜ |
| 3 | Linked List Cycle II | Medium | [LC 142](https://leetcode.com/problems/linked-list-cycle-ii/) | ⬜ |
| 4 | Reverse Nodes in k-Group | Hard | [LC 25](https://leetcode.com/problems/reverse-nodes-in-k-group/) | ⬜ |
| 5 | Merge K Sorted Lists | Hard | [LC 23](https://leetcode.com/problems/merge-k-sorted-lists/) | ⬜ |
| 6 | Copy List with Random Pointer | Medium | [LC 138](https://leetcode.com/problems/copy-list-with-random-pointer/) | ⬜ |

---

### Day 7: Stacks & Queues
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Stack basics and applications
- [ ] Monotonic stack pattern
- [ ] Queue using stacks
- [ ] Deque (double-ended queue)
- [ ] Priority Queue basics

#### 📖 Monotonic Stack Pattern
```javascript
// Next Greater Element
function nextGreaterElement(nums) {
    const result = new Array(nums.length).fill(-1);
    const stack = []; // store indices
    
    for (let i = 0; i < nums.length; i++) {
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
    const stack = [];
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
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Valid Parentheses | Easy | [LC 20](https://leetcode.com/problems/valid-parentheses/) | ⬜ |
| 2 | Min Stack | Medium | [LC 155](https://leetcode.com/problems/min-stack/) | ⬜ |
| 3 | Daily Temperatures | Medium | [LC 739](https://leetcode.com/problems/daily-temperatures/) | ⬜ |
| 4 | Largest Rectangle in Histogram | Hard | [LC 84](https://leetcode.com/problems/largest-rectangle-in-histogram/) | ⬜ |
| 5 | Implement Queue using Stacks | Easy | [LC 232](https://leetcode.com/problems/implement-queue-using-stacks/) | ⬜ |
| 6 | Basic Calculator II | Medium | [LC 227](https://leetcode.com/problems/basic-calculator-ii/) | ⬜ |

---

## 🎯 Week 2: Core Structures (Days 8-14)

### Day 8: Hash Tables Deep Dive
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Hash function design
- [ ] Collision resolution: Chaining vs Open Addressing
- [ ] Load factor and resizing
- [ ] Rolling hash (Rabin-Karp)
- [ ] Consistent hashing

#### 📖 Key Implementations
```javascript
// Rabin-Karp Substring Search
function rabinKarp(text, pattern) {
    const base = 26, mod = 1e9 + 7;
    const m = pattern.length, n = text.length;
    
    // Compute pattern hash
    let patternHash = 0, textHash = 0, power = 1;
    for (let i = 0; i < m; i++) {
        patternHash = (patternHash * base + pattern.charCodeAt(i)) % mod;
        textHash = (textHash * base + text.charCodeAt(i)) % mod;
        if (i < m - 1) power = (power * base) % mod;
    }
    
    // Slide window
    for (let i = 0; i <= n - m; i++) {
        if (patternHash === textHash && text.substring(i, i + m) === pattern) {
            return i;
        }
        if (i < n - m) {
            textHash = (textHash - text.charCodeAt(i) * power % mod + mod) % mod;
            textHash = (textHash * base + text.charCodeAt(i + m)) % mod;
        }
    }
    return -1;
}
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Two Sum | Easy | [LC 1](https://leetcode.com/problems/two-sum/) | ⬜ |
| 2 | Group Anagrams | Medium | [LC 49](https://leetcode.com/problems/group-anagrams/) | ⬜ |
| 3 | Longest Consecutive Sequence | Medium | [LC 128](https://leetcode.com/problems/longest-consecutive-sequence/) | ⬜ |
| 4 | Find All Anagrams in a String | Medium | [LC 438](https://leetcode.com/problems/find-all-anagrams-in-a-string/) | ⬜ |
| 5 | LRU Cache | Medium | [LC 146](https://leetcode.com/problems/lru-cache/) | ⬜ |

---

### Day 9: String Algorithms (MISSING CONCEPT ⚠️)
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] KMP (Knuth-Morris-Pratt) algorithm
- [ ] Z-algorithm
- [ ] Rabin-Karp
- [ ] Longest Common Prefix
- [ ] String manipulation patterns

#### 📖 KMP Algorithm Implementation
```javascript
// Build failure function (partial match table)
function buildLPS(pattern) {
    const lps = [0];
    let len = 0, i = 1;
    
    while (i < pattern.length) {
        if (pattern[i] === pattern[len]) {
            len++;
            lps.push(len);
            i++;
        } else if (len > 0) {
            len = lps[len - 1];
        } else {
            lps.push(0);
            i++;
        }
    }
    return lps;
}

// KMP Search
function kmpSearch(text, pattern) {
    const lps = buildLPS(pattern);
    const result = [];
    let i = 0, j = 0; // i for text, j for pattern
    
    while (i < text.length) {
        if (text[i] === pattern[j]) {
            i++; j++;
            if (j === pattern.length) {
                result.push(i - j);
                j = lps[j - 1];
            }
        } else if (j > 0) {
            j = lps[j - 1];
        } else {
            i++;
        }
    }
    return result;
}
// Time: O(n + m), Space: O(m)

// Z-Algorithm
function zFunction(s) {
    const n = s.length;
    const z = new Array(n).fill(0);
    let l = 0, r = 0;
    
    for (let i = 1; i < n; i++) {
        if (i < r) {
            z[i] = Math.min(r - i, z[i - l]);
        }
        while (i + z[i] < n && s[z[i]] === s[i + z[i]]) {
            z[i]++;
        }
        if (i + z[i] > r) {
            l = i;
            r = i + z[i];
        }
    }
    return z;
}
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Implement strStr() | Easy | [LC 28](https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/) | ⬜ |
| 2 | Repeated Substring Pattern | Easy | [LC 459](https://leetcode.com/problems/repeated-substring-pattern/) | ⬜ |
| 3 | Longest Happy Prefix | Hard | [LC 1392](https://leetcode.com/problems/longest-happy-prefix/) | ⬜ |
| 4 | Shortest Palindrome | Hard | [LC 214](https://leetcode.com/problems/shortest-palindrome/) | ⬜ |
| 5 | Longest Duplicate Substring | Hard | [LC 1044](https://leetcode.com/problems/longest-duplicate-substring/) | ⬜ |

---

### Day 10: Binary Trees Fundamentals
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Tree traversals (Inorder, Preorder, Postorder, Level)
- [ ] Iterative traversals
- [ ] Tree construction from traversals
- [ ] Tree properties (height, diameter, balance)

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Binary Tree Inorder Traversal | Easy | [LC 94](https://leetcode.com/problems/binary-tree-inorder-traversal/) | ⬜ |
| 2 | Maximum Depth of Binary Tree | Easy | [LC 104](https://leetcode.com/problems/maximum-depth-of-binary-tree/) | ⬜ |
| 3 | Same Tree | Easy | [LC 100](https://leetcode.com/problems/same-tree/) | ⬜ |
| 4 | Construct Binary Tree from Preorder and Inorder | Medium | [LC 105](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/) | ⬜ |
| 5 | Binary Tree Level Order Traversal | Medium | [LC 102](https://leetcode.com/problems/binary-tree-level-order-traversal/) | ⬜ |
| 6 | Diameter of Binary Tree | Easy | [LC 543](https://leetcode.com/problems/diameter-of-binary-tree/) | ⬜ |

---

### Day 11: Binary Search Trees (BST)
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] BST properties and operations
- [ ] BST validation
- [ ] Inorder successor/predecessor
- [ ] BST from sorted array
- [ ] LCA in BST

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Validate Binary Search Tree | Medium | [LC 98](https://leetcode.com/problems/validate-binary-search-tree/) | ⬜ |
| 2 | Kth Smallest Element in BST | Medium | [LC 230](https://leetcode.com/problems/kth-smallest-element-in-a-bst/) | ⬜ |
| 3 | Lowest Common Ancestor of BST | Medium | [LC 235](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/) | ⬜ |
| 4 | Convert Sorted Array to BST | Easy | [LC 108](https://leetcode.com/problems/convert-sorted-array-to-binary-search-tree/) | ⬜ |
| 5 | Delete Node in a BST | Medium | [LC 450](https://leetcode.com/problems/delete-node-in-a-bst/) | ⬜ |

---

### Day 12: Advanced Trees
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] AVL Trees (rotations)
- [ ] Red-Black Trees (concepts)
- [ ] Tree serialization
- [ ] Binary tree maximum path sum
- [ ] Morris traversal

#### 📖 Morris Traversal (O(1) Space)
```javascript
// Inorder Morris Traversal
function morrisInorder(root) {
    const result = [];
    let curr = root;
    
    while (curr) {
        if (!curr.left) {
            result.push(curr.val);
            curr = curr.right;
        } else {
            // Find inorder predecessor
            let predecessor = curr.left;
            while (predecessor.right && predecessor.right !== curr) {
                predecessor = predecessor.right;
            }
            
            if (!predecessor.right) {
                // Make curr the right child of its predecessor
                predecessor.right = curr;
                curr = curr.left;
            } else {
                // Revert the changes
                predecessor.right = null;
                result.push(curr.val);
                curr = curr.right;
            }
        }
    }
    return result;
}
// Time: O(n), Space: O(1)
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Serialize and Deserialize Binary Tree | Hard | [LC 297](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/) | ⬜ |
| 2 | Binary Tree Maximum Path Sum | Hard | [LC 124](https://leetcode.com/problems/binary-tree-maximum-path-sum/) | ⬜ |
| 3 | Recover Binary Search Tree | Medium | [LC 99](https://leetcode.com/problems/recover-binary-search-tree/) | ⬜ |
| 4 | Flatten Binary Tree to Linked List | Medium | [LC 114](https://leetcode.com/problems/flatten-binary-tree-to-linked-list/) | ⬜ |

---

### Day 13: Heaps & Priority Queues
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Binary Heap implementation
- [ ] Heapify operation
- [ ] Top-K pattern
- [ ] Two-heap pattern (median)
- [ ] K-way merge

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Kth Largest Element in Array | Medium | [LC 215](https://leetcode.com/problems/kth-largest-element-in-an-array/) | ⬜ |
| 2 | Top K Frequent Elements | Medium | [LC 347](https://leetcode.com/problems/top-k-frequent-elements/) | ⬜ |
| 3 | Find Median from Data Stream | Hard | [LC 295](https://leetcode.com/problems/find-median-from-data-stream/) | ⬜ |
| 4 | Merge K Sorted Lists | Hard | [LC 23](https://leetcode.com/problems/merge-k-sorted-lists/) | ⬜ |
| 5 | Task Scheduler | Medium | [LC 621](https://leetcode.com/problems/task-scheduler/) | ⬜ |
| 6 | Reorganize String | Medium | [LC 767](https://leetcode.com/problems/reorganize-string/) | ⬜ |

---

### Day 14: Bit Manipulation (MISSING CONCEPT ⚠️)
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Bitwise operators: AND, OR, XOR, NOT, Shifts
- [ ] Common bit tricks
- [ ] Counting bits
- [ ] Power of two checks
- [ ] Bit masking

#### 📖 Essential Bit Tricks
```javascript
// Check if n is power of 2
const isPowerOfTwo = n => n > 0 && (n & (n - 1)) === 0;

// Count set bits (Brian Kernighan's)
function countBits(n) {
    let count = 0;
    while (n) {
        n &= (n - 1);
        count++;
    }
    return count;
}

// Get/Set/Clear bit at position i
const getBit = (n, i) => (n >> i) & 1;
const setBit = (n, i) => n | (1 << i);
const clearBit = (n, i) => n & ~(1 << i);
const toggleBit = (n, i) => n ^ (1 << i);

// Find single number (all others appear twice)
const singleNumber = nums => nums.reduce((a, b) => a ^ b, 0);

// Swap without temp
function swap(a, b) {
    a ^= b;  // a = a ^ b
    b ^= a;  // b = b ^ (a ^ b) = a
    a ^= b;  // a = (a ^ b) ^ a = b
    return [a, b];
}

// Get lowest set bit
const lowestSetBit = n => n & (-n);

// Check if bit is set
const isOdd = n => (n & 1) === 1;
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Single Number | Easy | [LC 136](https://leetcode.com/problems/single-number/) | ⬜ |
| 2 | Number of 1 Bits | Easy | [LC 191](https://leetcode.com/problems/number-of-1-bits/) | ⬜ |
| 3 | Counting Bits | Easy | [LC 338](https://leetcode.com/problems/counting-bits/) | ⬜ |
| 4 | Reverse Bits | Easy | [LC 190](https://leetcode.com/problems/reverse-bits/) | ⬜ |
| 5 | Single Number III | Medium | [LC 260](https://leetcode.com/problems/single-number-iii/) | ⬜ |
| 6 | Sum of Two Integers | Medium | [LC 371](https://leetcode.com/problems/sum-of-two-integers/) | ⬜ |
| 7 | Subsets (Bit Masking) | Medium | [LC 78](https://leetcode.com/problems/subsets/) | ⬜ |

---

## 🎯 Week 3: Graphs & Advanced Algorithms (Days 15-21)

### Day 15: Graph Representations & BFS
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Adjacency List vs Matrix
- [ ] BFS traversal
- [ ] BFS for shortest path (unweighted)
- [ ] Multi-source BFS
- [ ] 0-1 BFS

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Number of Islands | Medium | [LC 200](https://leetcode.com/problems/number-of-islands/) | ⬜ |
| 2 | Rotting Oranges | Medium | [LC 994](https://leetcode.com/problems/rotting-oranges/) | ⬜ |
| 3 | Word Ladder | Hard | [LC 127](https://leetcode.com/problems/word-ladder/) | ⬜ |
| 4 | 01 Matrix | Medium | [LC 542](https://leetcode.com/problems/01-matrix/) | ⬜ |
| 5 | Shortest Path in Binary Matrix | Medium | [LC 1091](https://leetcode.com/problems/shortest-path-in-binary-matrix/) | ⬜ |

---

### Day 16: Graph DFS & Cycle Detection
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] DFS traversal (iterative & recursive)
- [ ] Cycle detection in directed graphs
- [ ] Cycle detection in undirected graphs
- [ ] Connected components
- [ ] Bipartite check

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Course Schedule | Medium | [LC 207](https://leetcode.com/problems/course-schedule/) | ⬜ |
| 2 | Course Schedule II | Medium | [LC 210](https://leetcode.com/problems/course-schedule-ii/) | ⬜ |
| 3 | Is Graph Bipartite? | Medium | [LC 785](https://leetcode.com/problems/is-graph-bipartite/) | ⬜ |
| 4 | Number of Connected Components | Medium | [LC 323](https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/) | ⬜ |
| 5 | Clone Graph | Medium | [LC 133](https://leetcode.com/problems/clone-graph/) | ⬜ |

---

### Day 17: Topological Sort & Union Find
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Kahn's Algorithm (BFS)
- [ ] DFS-based topological sort
- [ ] Union Find with path compression
- [ ] Union by rank
- [ ] Applications: MST, connectivity

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Alien Dictionary | Hard | [LC 269](https://leetcode.com/problems/alien-dictionary/) | ⬜ |
| 2 | Redundant Connection | Medium | [LC 684](https://leetcode.com/problems/redundant-connection/) | ⬜ |
| 3 | Accounts Merge | Medium | [LC 721](https://leetcode.com/problems/accounts-merge/) | ⬜ |
| 4 | Number of Provinces | Medium | [LC 547](https://leetcode.com/problems/number-of-provinces/) | ⬜ |
| 5 | Graph Valid Tree | Medium | [LC 261](https://leetcode.com/problems/graph-valid-tree/) | ⬜ |

---

### Day 18: Shortest Path Algorithms
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Dijkstra's Algorithm
- [ ] Bellman-Ford Algorithm
- [ ] Floyd-Warshall Algorithm
- [ ] When to use which algorithm
- [ ] Negative cycles

#### 📖 Algorithm Selection Guide
```
| Algorithm      | Use Case                          | Complexity    |
|---------------|-----------------------------------|---------------|
| BFS           | Unweighted shortest path          | O(V + E)      |
| Dijkstra      | Non-negative weighted             | O((V+E)log V) |
| Bellman-Ford  | Negative weights, detect cycles   | O(V * E)      |
| Floyd-Warshall| All pairs shortest path           | O(V³)         |
| A*            | With heuristic (pathfinding)      | O(E)          |
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Network Delay Time | Medium | [LC 743](https://leetcode.com/problems/network-delay-time/) | ⬜ |
| 2 | Cheapest Flights Within K Stops | Medium | [LC 787](https://leetcode.com/problems/cheapest-flights-within-k-stops/) | ⬜ |
| 3 | Path with Minimum Effort | Medium | [LC 1631](https://leetcode.com/problems/path-with-minimum-effort/) | ⬜ |
| 4 | Find the City | Medium | [LC 1334](https://leetcode.com/problems/find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance/) | ⬜ |

---

### Day 19: Minimum Spanning Tree (MISSING CONCEPT ⚠️)
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Kruskal's Algorithm
- [ ] Prim's Algorithm
- [ ] MST applications
- [ ] Cut property

#### 📖 MST Implementations
```javascript
// Kruskal's Algorithm
function kruskalMST(n, edges) {
    // Sort edges by weight
    edges.sort((a, b) => a[2] - b[2]);
    
    const uf = new UnionFind(n);
    const mst = [];
    let cost = 0;
    
    for (const [u, v, weight] of edges) {
        if (uf.union(u, v)) {
            mst.push([u, v, weight]);
            cost += weight;
            if (mst.length === n - 1) break;
        }
    }
    
    return { mst, cost };
}
// Time: O(E log E)

// Prim's Algorithm
function primMST(n, graph) {
    const visited = new Set();
    const pq = new MinHeap(); // [weight, node]
    pq.push([0, 0]);
    let cost = 0;
    
    while (pq.size() && visited.size < n) {
        const [weight, node] = pq.pop();
        if (visited.has(node)) continue;
        
        visited.add(node);
        cost += weight;
        
        for (const [neighbor, edgeWeight] of graph[node]) {
            if (!visited.has(neighbor)) {
                pq.push([edgeWeight, neighbor]);
            }
        }
    }
    
    return cost;
}
// Time: O(E log V)
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Min Cost to Connect All Points | Medium | [LC 1584](https://leetcode.com/problems/min-cost-to-connect-all-points/) | ⬜ |
| 2 | Connecting Cities With Minimum Cost | Medium | [LC 1135](https://leetcode.com/problems/connecting-cities-with-minimum-cost/) | ⬜ |
| 3 | Optimize Water Distribution | Hard | [LC 1168](https://leetcode.com/problems/optimize-water-distribution-in-a-village/) | ⬜ |
| 4 | Find Critical and Pseudo-Critical Edges | Hard | [LC 1489](https://leetcode.com/problems/find-critical-and-pseudo-critical-edges-in-minimum-spanning-tree/) | ⬜ |

---

### Day 20: Dynamic Programming - 1D
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] DP problem identification
- [ ] State definition
- [ ] Transition formulas
- [ ] Space optimization
- [ ] Common 1D patterns

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Climbing Stairs | Easy | [LC 70](https://leetcode.com/problems/climbing-stairs/) | ⬜ |
| 2 | House Robber | Medium | [LC 198](https://leetcode.com/problems/house-robber/) | ⬜ |
| 3 | Word Break | Medium | [LC 139](https://leetcode.com/problems/word-break/) | ⬜ |
| 4 | Coin Change | Medium | [LC 322](https://leetcode.com/problems/coin-change/) | ⬜ |
| 5 | Longest Increasing Subsequence | Medium | [LC 300](https://leetcode.com/problems/longest-increasing-subsequence/) | ⬜ |
| 6 | Decode Ways | Medium | [LC 91](https://leetcode.com/problems/decode-ways/) | ⬜ |

---

### Day 21: Dynamic Programming - 2D
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] 2D DP patterns
- [ ] String DP (LCS, Edit Distance)
- [ ] Grid DP
- [ ] Interval DP basics
- [ ] DP optimization techniques

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Unique Paths | Medium | [LC 62](https://leetcode.com/problems/unique-paths/) | ⬜ |
| 2 | Longest Common Subsequence | Medium | [LC 1143](https://leetcode.com/problems/longest-common-subsequence/) | ⬜ |
| 3 | Edit Distance | Medium | [LC 72](https://leetcode.com/problems/edit-distance/) | ⬜ |
| 4 | 0/1 Knapsack | Medium | Custom Implementation | ⬜ |
| 5 | Longest Palindromic Substring | Medium | [LC 5](https://leetcode.com/problems/longest-palindromic-substring/) | ⬜ |
| 6 | Interleaving String | Medium | [LC 97](https://leetcode.com/problems/interleaving-string/) | ⬜ |

---

## 🎯 Week 4: Senior-Level DSA (Days 22-28)

### Day 22: Advanced DP
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] State compression DP (bitmask)
- [ ] Digit DP
- [ ] DP on trees
- [ ] DP optimization (monotonic queue, divide & conquer)

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Partition Equal Subset Sum | Medium | [LC 416](https://leetcode.com/problems/partition-equal-subset-sum/) | ⬜ |
| 2 | Burst Balloons | Hard | [LC 312](https://leetcode.com/problems/burst-balloons/) | ⬜ |
| 3 | Regular Expression Matching | Hard | [LC 10](https://leetcode.com/problems/regular-expression-matching/) | ⬜ |
| 4 | Wildcard Matching | Hard | [LC 44](https://leetcode.com/problems/wildcard-matching/) | ⬜ |
| 5 | Distinct Subsequences | Hard | [LC 115](https://leetcode.com/problems/distinct-subsequences/) | ⬜ |

---

### Day 23: Greedy Algorithms
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Greedy choice property
- [ ] Activity selection
- [ ] Interval scheduling
- [ ] Huffman coding concepts
- [ ] Greedy vs DP

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Jump Game | Medium | [LC 55](https://leetcode.com/problems/jump-game/) | ⬜ |
| 2 | Jump Game II | Medium | [LC 45](https://leetcode.com/problems/jump-game-ii/) | ⬜ |
| 3 | Non-overlapping Intervals | Medium | [LC 435](https://leetcode.com/problems/non-overlapping-intervals/) | ⬜ |
| 4 | Merge Intervals | Medium | [LC 56](https://leetcode.com/problems/merge-intervals/) | ⬜ |
| 5 | Meeting Rooms II | Medium | [LC 253](https://leetcode.com/problems/meeting-rooms-ii/) | ⬜ |
| 6 | Gas Station | Medium | [LC 134](https://leetcode.com/problems/gas-station/) | ⬜ |
| 7 | Candy | Hard | [LC 135](https://leetcode.com/problems/candy/) | ⬜ |

---

### Day 24: Backtracking
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Backtracking template
- [ ] Permutations vs Combinations
- [ ] Pruning strategies
- [ ] Constraint satisfaction

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Subsets | Medium | [LC 78](https://leetcode.com/problems/subsets/) | ⬜ |
| 2 | Permutations | Medium | [LC 46](https://leetcode.com/problems/permutations/) | ⬜ |
| 3 | Combination Sum | Medium | [LC 39](https://leetcode.com/problems/combination-sum/) | ⬜ |
| 4 | Palindrome Partitioning | Medium | [LC 131](https://leetcode.com/problems/palindrome-partitioning/) | ⬜ |
| 5 | N-Queens | Hard | [LC 51](https://leetcode.com/problems/n-queens/) | ⬜ |
| 6 | Sudoku Solver | Hard | [LC 37](https://leetcode.com/problems/sudoku-solver/) | ⬜ |
| 7 | Word Search II | Hard | [LC 212](https://leetcode.com/problems/word-search-ii/) | ⬜ |

---

### Day 25: Tries & String Structures
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Trie implementation
- [ ] Autocomplete system
- [ ] Word search in Trie
- [ ] Prefix/Suffix operations

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Implement Trie | Medium | [LC 208](https://leetcode.com/problems/implement-trie-prefix-tree/) | ⬜ |
| 2 | Design Add and Search Words | Medium | [LC 211](https://leetcode.com/problems/design-add-and-search-words-data-structure/) | ⬜ |
| 3 | Word Search II | Hard | [LC 212](https://leetcode.com/problems/word-search-ii/) | ⬜ |
| 4 | Design Search Autocomplete | Hard | [LC 642](https://leetcode.com/problems/design-search-autocomplete-system/) | ⬜ |
| 5 | Palindrome Pairs | Hard | [LC 336](https://leetcode.com/problems/palindrome-pairs/) | ⬜ |

---

### Day 26: Segment Trees & Advanced Trees
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] Segment Tree (build, update, query)
- [ ] Lazy propagation
- [ ] Binary Indexed Tree (Fenwick Tree)
- [ ] Applications: Range sum, Range min/max

#### 📖 Fenwick Tree Implementation
```javascript
class FenwickTree {
    constructor(n) {
        this.n = n;
        this.tree = new Array(n + 1).fill(0);
    }
    
    // Add delta to index i (1-indexed)
    update(i, delta) {
        while (i <= this.n) {
            this.tree[i] += delta;
            i += i & (-i); // Add lowest set bit
        }
    }
    
    // Get sum from 1 to i
    query(i) {
        let sum = 0;
        while (i > 0) {
            sum += this.tree[i];
            i -= i & (-i); // Remove lowest set bit
        }
        return sum;
    }
    
    // Get sum from l to r
    rangeQuery(l, r) {
        return this.query(r) - this.query(l - 1);
    }
}
// All operations: O(log n)
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Range Sum Query - Mutable | Medium | [LC 307](https://leetcode.com/problems/range-sum-query-mutable/) | ⬜ |
| 2 | Count of Smaller Numbers After Self | Hard | [LC 315](https://leetcode.com/problems/count-of-smaller-numbers-after-self/) | ⬜ |
| 3 | Count of Range Sum | Hard | [LC 327](https://leetcode.com/problems/count-of-range-sum/) | ⬜ |
| 4 | Reverse Pairs | Hard | [LC 493](https://leetcode.com/problems/reverse-pairs/) | ⬜ |

---

### Day 27: Math & Number Theory (MISSING CONCEPT ⚠️)
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] GCD/LCM (Euclidean algorithm)
- [ ] Prime numbers (Sieve of Eratosthenes)
- [ ] Modular arithmetic
- [ ] Fast exponentiation
- [ ] Combinatorics basics

#### 📖 Essential Math Implementations
```javascript
// GCD (Euclidean algorithm)
function gcd(a, b) {
    while (b !== 0) {
        [a, b] = [b, a % b];
    }
    return a;
}

// LCM
const lcm = (a, b) => (a * b) / gcd(a, b);

// Sieve of Eratosthenes
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
    return isPrime;
}

// Fast Exponentiation (a^n mod m)
function fastPow(a, n, mod = 1e9 + 7) {
    let result = 1;
    a = a % mod;
    
    while (n > 0) {
        if (n & 1) result = (result * a) % mod;
        n >>= 1;
        a = (a * a) % mod;
    }
    return result;
}

// Check if prime
function isPrime(n) {
    if (n < 2) return false;
    if (n === 2) return true;
    if (n % 2 === 0) return false;
    
    for (let i = 3; i * i <= n; i += 2) {
        if (n % i === 0) return false;
    }
    return true;
}

// nCr mod p (using Fermat's little theorem)
function nCr(n, r, mod = 1e9 + 7) {
    if (r > n) return 0;
    
    const fact = [1];
    for (let i = 1; i <= n; i++) {
        fact[i] = (fact[i - 1] * i) % mod;
    }
    
    const invFact = (a) => fastPow(a, mod - 2, mod);
    
    return (fact[n] * invFact(fact[r]) % mod) * invFact(fact[n - r]) % mod;
}
```

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | Count Primes | Medium | [LC 204](https://leetcode.com/problems/count-primes/) | ⬜ |
| 2 | Pow(x, n) | Medium | [LC 50](https://leetcode.com/problems/powx-n/) | ⬜ |
| 3 | Sqrt(x) | Easy | [LC 69](https://leetcode.com/problems/sqrtx/) | ⬜ |
| 4 | Happy Number | Easy | [LC 202](https://leetcode.com/problems/happy-number/) | ⬜ |
| 5 | Ugly Number II | Medium | [LC 264](https://leetcode.com/problems/ugly-number-ii/) | ⬜ |
| 6 | Greatest Common Divisor of Strings | Easy | [LC 1071](https://leetcode.com/problems/greatest-common-divisor-of-strings/) | ⬜ |

---

### Day 28: Design Problems & System Design Prep
**Time: 3 hours**

#### 📚 Topics to Study
- [ ] LRU Cache
- [ ] LFU Cache
- [ ] Design Twitter
- [ ] Rate Limiter
- [ ] In-Memory File System

#### 💻 Practice Problems
| # | Problem | Difficulty | Link | Done |
|---|---------|------------|------|------|
| 1 | LRU Cache | Medium | [LC 146](https://leetcode.com/problems/lru-cache/) | ⬜ |
| 2 | LFU Cache | Hard | [LC 460](https://leetcode.com/problems/lfu-cache/) | ⬜ |
| 3 | Design Twitter | Medium | [LC 355](https://leetcode.com/problems/design-twitter/) | ⬜ |
| 4 | Design In-Memory File System | Hard | [LC 588](https://leetcode.com/problems/design-in-memory-file-system/) | ⬜ |
| 5 | Insert Delete GetRandom O(1) | Medium | [LC 380](https://leetcode.com/problems/insert-delete-getrandom-o1/) | ⬜ |
| 6 | Design Hit Counter | Medium | [LC 362](https://leetcode.com/problems/design-hit-counter/) | ⬜ |

---

## 🎯 Week 5: Mock Interviews (Days 29-30)

### Day 29: Full Mock Interview 1
**Time: 4 hours**

#### Morning Session - Google Style (2 hours)
1. **Warm-up (20 min):** [Merge Two Sorted Lists](https://leetcode.com/problems/merge-two-sorted-lists/)
2. **Main Problem (40 min):** [Word Ladder](https://leetcode.com/problems/word-ladder/)
3. **Follow-up (30 min):** [Word Ladder II](https://leetcode.com/problems/word-ladder-ii/)
4. **System Design Discussion (30 min):** Design URL Shortener

#### Afternoon Session - Meta Style (2 hours)
1. **Behavioral (15 min):** Conflict resolution story
2. **Coding 1 (45 min):** [Minimum Window Substring](https://leetcode.com/problems/minimum-window-substring/)
3. **Coding 2 (45 min):** [Binary Tree Maximum Path Sum](https://leetcode.com/problems/binary-tree-maximum-path-sum/)
4. **Q&A (15 min)**

---

### Day 30: Full Mock Interview 2 + Review
**Time: 4 hours**

#### Morning Session - Amazon Style (2 hours)
1. **Leadership Principle (20 min):** Customer Obsession example
2. **Coding 1 (40 min):** [LRU Cache](https://leetcode.com/problems/lru-cache/)
3. **Coding 2 (40 min):** [Course Schedule II](https://leetcode.com/problems/course-schedule-ii/)
4. **Design Discussion (20 min):** Design Amazon shopping cart

#### Afternoon Session - Review & Weak Areas
- [ ] Review all marked difficult problems
- [ ] Rework 5 problems you struggled with
- [ ] Review all pattern templates
- [ ] Practice explaining solutions out loud

---

## 📋 Missing Concepts Summary (Now Added)

| Concept | Day Added | Status |
|---------|-----------|--------|
| Binary Search (Dedicated) | Day 4 | ✅ |
| Bit Manipulation | Day 14 | ✅ |
| String Algorithms (KMP, Z) | Day 9 | ✅ |
| Math/Number Theory | Day 27 | ✅ |
| MST (Prim's, Kruskal's) | Day 19 | ✅ |
| Morris Traversal | Day 12 | ✅ |
| Fenwick Tree | Day 26 | ✅ |

---

## 📊 Quick Reference Sheets

### Time Complexity Cheat Sheet
```
Array:      Access O(1), Search O(n), Insert O(n)
HashMap:    Access O(1), Search O(1), Insert O(1) *avg
BST:        Access O(log n), Search O(log n), Insert O(log n)
Heap:       Access O(1) for min/max, Insert O(log n)
Trie:       Search O(m) where m = word length
```

### Space Complexity Guide
```
Recursion:  O(height) for stack
BFS:        O(width) for queue  
DFS:        O(height) for stack
DP:         Usually O(n) or O(n²)
Graph:      O(V + E) for adjacency list
```

### Pattern Recognition
```
"Sorted array" → Binary Search / Two Pointer
"Substring/Subarray" → Sliding Window
"Permutation/Combination" → Backtracking
"Optimal substructure" → DP
"Tree traversal" → BFS/DFS
"K largest/smallest" → Heap
"Prefix matching" → Trie
"Island/Connected" → Union Find / BFS
"Shortest path" → BFS (unweighted) / Dijkstra (weighted)
```

---

## ✅ Daily Checklist Template

```markdown
## Day X: [Topic]

### Pre-Study
- [ ] Review previous day's notes
- [ ] Quick warm-up problem

### Core Learning
- [ ] Read theory (30 min)
- [ ] Implement data structure/algorithm
- [ ] Solve 3-5 problems

### Post-Study
- [ ] Write notes on key insights
- [ ] Identify weak areas
- [ ] Plan tomorrow's focus

### Metrics
- Problems attempted: __
- Problems solved independently: __
- Time per problem (avg): __ min
- Concepts to revisit: __
```

---

**Total Problems:** ~150+  
**Estimated Completion:** 90-120 hours  
**Confidence Level After Completion:** Ready for FAANG interviews

---

*Last Updated: February 2026*
