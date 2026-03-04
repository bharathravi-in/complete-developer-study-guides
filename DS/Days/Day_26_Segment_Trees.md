# 📚 DSA 30-Day Tutorial - Day 26

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

