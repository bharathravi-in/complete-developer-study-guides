# 📚 DSA 30-Day Tutorial - Day 22

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

