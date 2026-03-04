# 📚 DSA 30-Day Tutorial - Day 2

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

