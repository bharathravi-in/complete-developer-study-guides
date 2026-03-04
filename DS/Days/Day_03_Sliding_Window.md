# 📚 DSA 30-Day Tutorial - Day 3

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

