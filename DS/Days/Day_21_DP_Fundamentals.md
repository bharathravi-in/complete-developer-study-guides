# 📚 DSA 30-Day Tutorial - Day 21

## Day 21: Dynamic Programming Fundamentals

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand DP principles
- Identify overlapping subproblems
- Apply memoization and tabulation

---

### 📖 What is Dynamic Programming?

DP = **Optimal Substructure** + **Overlapping Subproblems**

- Break problem into smaller subproblems
- Store results to avoid recomputation

**Two approaches:**
1. **Top-down (Memoization):** Recursive with caching
2. **Bottom-up (Tabulation):** Iterative, build from base cases

---

### 📖 Fibonacci - DP Example

#### Naive Recursion (Exponential)
```javascript
function fibNaive(n) {
    if (n <= 1) return n;
    return fibNaive(n - 1) + fibNaive(n - 2);
}
// Time: O(2^n) - recomputes same values
```

#### Memoization (Top-down)
```javascript
function fibMemo(n, memo = {}) {
    if (n <= 1) return n;
    if (memo[n] !== undefined) return memo[n];
    
    memo[n] = fibMemo(n - 1, memo) + fibMemo(n - 2, memo);
    return memo[n];
}
// Time: O(n), Space: O(n)
```

#### Tabulation (Bottom-up)
```javascript
function fibTab(n) {
    if (n <= 1) return n;
    
    const dp = new Array(n + 1);
    dp[0] = 0;
    dp[1] = 1;
    
    for (let i = 2; i <= n; i++) {
        dp[i] = dp[i - 1] + dp[i - 2];
    }
    
    return dp[n];
}
// Time: O(n), Space: O(n)
```

#### Space Optimized
```javascript
function fibOptimized(n) {
    if (n <= 1) return n;
    
    let prev2 = 0, prev1 = 1;
    for (let i = 2; i <= n; i++) {
        const curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    
    return prev1;
}
// Time: O(n), Space: O(1)
```

---

### 📖 Climbing Stairs

```javascript
function climbStairs(n) {
    // dp[i] = ways to reach step i
    // dp[i] = dp[i-1] + dp[i-2]
    
    if (n <= 2) return n;
    
    let prev2 = 1, prev1 = 2;
    for (let i = 3; i <= n; i++) {
        const curr = prev1 + prev2;
        prev2 = prev1;
        prev1 = curr;
    }
    
    return prev1;
}
```

---

### 📖 House Robber

```javascript
function rob(nums) {
    if (nums.length === 0) return 0;
    if (nums.length === 1) return nums[0];
    
    // dp[i] = max money robbing houses 0..i
    // dp[i] = max(dp[i-1], dp[i-2] + nums[i])
    
    let prev2 = 0, prev1 = nums[0];
    
    for (let i = 1; i < nums.length; i++) {
        const curr = Math.max(prev1, prev2 + nums[i]);
        prev2 = prev1;
        prev1 = curr;
    }
    
    return prev1;
}
```

**Walkthrough:**
```
nums = [2, 7, 9, 3, 1]

i=0: prev1 = 2         (take house 0)
i=1: curr = max(2, 0+7) = 7, prev2=2, prev1=7
i=2: curr = max(7, 2+9) = 11, prev2=7, prev1=11
i=3: curr = max(11, 7+3) = 11, prev2=11, prev1=11
i=4: curr = max(11, 11+1) = 12, prev2=11, prev1=12

Answer: 12 (houses 0, 2, 4)
```

---

### 📖 Coin Change

```javascript
function coinChange(coins, amount) {
    // dp[i] = min coins needed for amount i
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
```

---

### ✅ Day 21 Checklist
- [ ] Understand memoization vs tabulation
- [ ] Identify DP problems
- [ ] Complete: Climbing Stairs, House Robber
- [ ] Practice: Coin Change, Min Cost Climbing Stairs

---

# End of Week 3

**Week 3 Summary:**
- Day 15: Graph Fundamentals
- Day 16: BFS
- Day 17: DFS
- Day 18: Topological Sort & Union Find
- Day 19: Shortest Path (Dijkstra, Bellman-Ford)
- Day 20: Minimum Spanning Tree
- Day 21: DP Fundamentals

**Continue to Week 4 for: Advanced DP, Greedy, Backtracking, Tries, and System Design**

---

# 🗓️ WEEK 4: Advanced Algorithms

---

