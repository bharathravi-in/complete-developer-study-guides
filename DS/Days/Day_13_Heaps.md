# 📚 DSA 30-Day Tutorial - Day 13

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

