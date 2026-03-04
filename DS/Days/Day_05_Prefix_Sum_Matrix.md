# 📚 DSA 30-Day Tutorial - Day 5

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

