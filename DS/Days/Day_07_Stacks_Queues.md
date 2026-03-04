# 📚 DSA 30-Day Tutorial - Day 7

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

