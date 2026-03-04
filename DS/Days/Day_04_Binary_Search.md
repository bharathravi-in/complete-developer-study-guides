# 📚 DSA 30-Day Tutorial - Day 4

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

