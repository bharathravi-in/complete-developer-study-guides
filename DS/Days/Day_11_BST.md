# 📚 DSA 30-Day Tutorial - Day 11

## Day 11: Binary Search Trees (BST)

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand BST properties
- Validate BST
- Implement BST operations
- Solve BST-specific problems

---

### 📖 BST Property

For every node:
- All values in left subtree < node's value
- All values in right subtree > node's value

```
Valid BST:          Invalid BST:
      8                   8
     / \                 / \
    3   10              3   10
   / \    \            / \    \
  1   6    14         1   6    4  ← 4 < 8, should be in left
     / \                 / \
    4   7               4   7
```

---

### 📖 BST Search, Insert, Delete

#### Search
```javascript
function searchBST(root, val) {
    if (root === null || root.val === val) return root;
    
    if (val < root.val) {
        return searchBST(root.left, val);
    } else {
        return searchBST(root.right, val);
    }
}
// Time: O(h) where h = height, O(log n) for balanced
```

#### Insert
```javascript
function insertIntoBST(root, val) {
    if (root === null) return new TreeNode(val);
    
    if (val < root.val) {
        root.left = insertIntoBST(root.left, val);
    } else {
        root.right = insertIntoBST(root.right, val);
    }
    
    return root;
}
```

---

### 📖 Validate Binary Search Tree

```javascript
function isValidBST(root, min = -Infinity, max = Infinity) {
    if (root === null) return true;
    
    // Check current node's value
    if (root.val <= min || root.val >= max) {
        return false;
    }
    
    // Recursively validate subtrees with updated bounds
    return isValidBST(root.left, min, root.val) 
        && isValidBST(root.right, root.val, max);
}
```

**Key Insight:** Pass down valid range for each subtree.

```
        5
       / \
      3   7
     / \
    1   4

Check 5: range (-∞, +∞) ✓
Check 3: range (-∞, 5) ✓
Check 7: range (5, +∞) ✓
Check 1: range (-∞, 3) ✓
Check 4: range (3, 5) ✓
```

---

### 📖 Kth Smallest Element in BST

**Key Insight:** Inorder traversal of BST gives sorted order!

```javascript
function kthSmallest(root, k) {
    const stack = [];
    let current = root;
    
    while (current !== null || stack.length > 0) {
        while (current !== null) {
            stack.push(current);
            current = current.left;
        }
        
        current = stack.pop();
        k--;
        
        if (k === 0) return current.val;
        
        current = current.right;
    }
    
    return -1;  // k is larger than tree size
}
```

---

### 📖 Lowest Common Ancestor in BST

```javascript
function lowestCommonAncestorBST(root, p, q) {
    while (root !== null) {
        if (p.val < root.val && q.val < root.val) {
            // Both in left subtree
            root = root.left;
        } else if (p.val > root.val && q.val > root.val) {
            // Both in right subtree
            root = root.right;
        } else {
            // Split point - this is LCA
            return root;
        }
    }
    
    return null;
}
```

---

### ✅ Day 11 Checklist
- [ ] Understand BST property
- [ ] Implement search, insert operations
- [ ] Complete: Validate BST, Kth Smallest
- [ ] Practice: LCA of BST, Convert Sorted Array to BST

---

