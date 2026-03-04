# 📚 DSA 30-Day Tutorial - Day 24

## Day 24: Backtracking

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand backtracking template
- Generate permutations and combinations
- Solve constraint satisfaction problems

---

### 📖 Backtracking Template

```javascript
function backtrack(candidates, path, result) {
    // Base case: valid solution found
    if (isValid(path)) {
        result.push([...path]);
        return;
    }
    
    for (let candidate of candidates) {
        // Check if candidate is valid choice
        if (isValidChoice(candidate)) {
            // Make choice
            path.push(candidate);
            
            // Recurse
            backtrack(remainingCandidates, path, result);
            
            // Undo choice (backtrack)
            path.pop();
        }
    }
}
```

---

### 📖 Subsets

```javascript
function subsets(nums) {
    const result = [];
    
    function backtrack(start, path) {
        result.push([...path]);  // Every path is a valid subset
        
        for (let i = start; i < nums.length; i++) {
            path.push(nums[i]);
            backtrack(i + 1, path);  // Start from i+1 to avoid duplicates
            path.pop();
        }
    }
    
    backtrack(0, []);
    return result;
}
```

**Decision tree:**
```
                    []
           /        |        \
         [1]       [2]       [3]
        / \         |
     [1,2] [1,3]  [2,3]
       |
    [1,2,3]
```

---

### 📖 Permutations

```javascript
function permute(nums) {
    const result = [];
    
    function backtrack(path, used) {
        if (path.length === nums.length) {
            result.push([...path]);
            return;
        }
        
        for (let i = 0; i < nums.length; i++) {
            if (used[i]) continue;
            
            path.push(nums[i]);
            used[i] = true;
            
            backtrack(path, used);
            
            path.pop();
            used[i] = false;
        }
    }
    
    backtrack([], new Array(nums.length).fill(false));
    return result;
}
```

---

### 📖 Combination Sum

```javascript
function combinationSum(candidates, target) {
    const result = [];
    
    function backtrack(start, path, remaining) {
        if (remaining === 0) {
            result.push([...path]);
            return;
        }
        if (remaining < 0) return;
        
        for (let i = start; i < candidates.length; i++) {
            path.push(candidates[i]);
            backtrack(i, path, remaining - candidates[i]);  // i, not i+1 (reuse allowed)
            path.pop();
        }
    }
    
    backtrack(0, [], target);
    return result;
}
```

---

### 📖 N-Queens

```javascript
function solveNQueens(n) {
    const result = [];
    const board = Array.from({ length: n }, () => '.'.repeat(n));
    
    // Track attacked columns and diagonals
    const cols = new Set();
    const diag1 = new Set();  // row - col
    const diag2 = new Set();  // row + col
    
    function backtrack(row) {
        if (row === n) {
            result.push([...board]);
            return;
        }
        
        for (let col = 0; col < n; col++) {
            if (cols.has(col) || diag1.has(row - col) || diag2.has(row + col)) {
                continue;
            }
            
            // Place queen
            board[row] = board[row].substring(0, col) + 'Q' + board[row].substring(col + 1);
            cols.add(col);
            diag1.add(row - col);
            diag2.add(row + col);
            
            backtrack(row + 1);
            
            // Remove queen
            board[row] = board[row].substring(0, col) + '.' + board[row].substring(col + 1);
            cols.delete(col);
            diag1.delete(row - col);
            diag2.delete(row + col);
        }
    }
    
    backtrack(0);
    return result;
}
```

---

### ✅ Day 24 Checklist
- [ ] Master backtracking template
- [ ] Complete: Subsets, Permutations
- [ ] Practice: Combination Sum, N-Queens
- [ ] Understand pruning strategies

---

