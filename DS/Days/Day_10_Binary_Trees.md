# 📚 DSA 30-Day Tutorial - Day 10

## Day 10: Binary Trees Fundamentals

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand tree terminology
- Implement all tree traversals (recursive & iterative)
- Solve common tree problems

---

### 📖 Tree Terminology

```
        1          ← Root
       / \
      2   3        ← Level 1 (depth 1)
     / \   \
    4   5   6      ← Leaves (no children)
    
Terminology:
- Root: Node with no parent (1)
- Leaf: Node with no children (4, 5, 6)
- Parent of 4: 2
- Children of 2: 4, 5
- Siblings of 5: 4
- Height: Longest path from root to leaf (2)
- Depth of node 5: Distance from root (2)
```

```javascript
class TreeNode {
    constructor(val) {
        this.val = val;
        this.left = null;
        this.right = null;
    }
}
```

---

### 📖 Tree Traversals

#### Inorder (Left → Root → Right)
```
    1
   / \
  2   3
 / \
4   5

Inorder: 4, 2, 5, 1, 3
```

```javascript
// Recursive
function inorderRecursive(root, result = []) {
    if (root === null) return result;
    
    inorderRecursive(root.left, result);
    result.push(root.val);
    inorderRecursive(root.right, result);
    
    return result;
}

// Iterative (using stack)
function inorderIterative(root) {
    const result = [];
    const stack = [];
    let current = root;
    
    while (current !== null || stack.length > 0) {
        // Go to leftmost node
        while (current !== null) {
            stack.push(current);
            current = current.left;
        }
        
        // Process node
        current = stack.pop();
        result.push(current.val);
        
        // Go to right subtree
        current = current.right;
    }
    
    return result;
}
```

#### Preorder (Root → Left → Right)
```javascript
// Recursive
function preorderRecursive(root, result = []) {
    if (root === null) return result;
    
    result.push(root.val);
    preorderRecursive(root.left, result);
    preorderRecursive(root.right, result);
    
    return result;
}

// Iterative
function preorderIterative(root) {
    if (!root) return [];
    
    const result = [];
    const stack = [root];
    
    while (stack.length > 0) {
        const node = stack.pop();
        result.push(node.val);
        
        // Push right first (so left is processed first)
        if (node.right) stack.push(node.right);
        if (node.left) stack.push(node.left);
    }
    
    return result;
}
```

#### Postorder (Left → Right → Root)
```javascript
// Recursive
function postorderRecursive(root, result = []) {
    if (root === null) return result;
    
    postorderRecursive(root.left, result);
    postorderRecursive(root.right, result);
    result.push(root.val);
    
    return result;
}

// Iterative (reverse of modified preorder)
function postorderIterative(root) {
    if (!root) return [];
    
    const result = [];
    const stack = [root];
    
    while (stack.length > 0) {
        const node = stack.pop();
        result.unshift(node.val);  // Add to front
        
        if (node.left) stack.push(node.left);
        if (node.right) stack.push(node.right);
    }
    
    return result;
}
```

#### Level Order (BFS)
```javascript
function levelOrder(root) {
    if (!root) return [];
    
    const result = [];
    const queue = [root];
    
    while (queue.length > 0) {
        const levelSize = queue.length;
        const currentLevel = [];
        
        for (let i = 0; i < levelSize; i++) {
            const node = queue.shift();
            currentLevel.push(node.val);
            
            if (node.left) queue.push(node.left);
            if (node.right) queue.push(node.right);
        }
        
        result.push(currentLevel);
    }
    
    return result;
}
```

---

### 📖 Common Tree Problems

#### Maximum Depth
```javascript
function maxDepth(root) {
    if (root === null) return 0;
    
    return 1 + Math.max(maxDepth(root.left), maxDepth(root.right));
}
```

#### Same Tree
```javascript
function isSameTree(p, q) {
    if (p === null && q === null) return true;
    if (p === null || q === null) return false;
    
    return p.val === q.val 
        && isSameTree(p.left, q.left) 
        && isSameTree(p.right, q.right);
}
```

#### Invert Binary Tree
```javascript
function invertTree(root) {
    if (root === null) return null;
    
    // Swap children
    [root.left, root.right] = [root.right, root.left];
    
    invertTree(root.left);
    invertTree(root.right);
    
    return root;
}
```

#### Diameter of Binary Tree
```javascript
function diameterOfBinaryTree(root) {
    let diameter = 0;
    
    function height(node) {
        if (node === null) return 0;
        
        const leftHeight = height(node.left);
        const rightHeight = height(node.right);
        
        // Update diameter (path through this node)
        diameter = Math.max(diameter, leftHeight + rightHeight);
        
        return 1 + Math.max(leftHeight, rightHeight);
    }
    
    height(root);
    return diameter;
}
```

---

### ✅ Day 10 Checklist
- [ ] Understand tree terminology
- [ ] Implement all 4 traversals (recursive & iterative)
- [ ] Complete: Max Depth, Same Tree, Invert Tree
- [ ] Practice: Diameter, Level Order Traversal

---

