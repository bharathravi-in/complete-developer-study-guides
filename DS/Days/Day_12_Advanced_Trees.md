# 📚 DSA 30-Day Tutorial - Day 12

## Day 12: Advanced Trees

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand balanced trees (AVL)
- Serialize and deserialize trees
- Solve path sum problems

---

### 📖 AVL Tree Concepts

AVL is a self-balancing BST where heights of left and right subtrees differ by at most 1.

**Balance Factor = height(left) - height(right)**
- Must be -1, 0, or 1 for every node

#### Rotations

**Right Rotation (LL Imbalance):**
```
    z                y
   / \             /   \
  y   T4   →      x     z
 / \             / \   / \
x   T3          T1 T2 T3 T4
```

**Left Rotation (RR Imbalance):**
```
  z                    y
 / \                 /   \
T1  y     →         z     x
   / \             / \   / \
  T2  x           T1 T2 T3 T4
```

---

### 📖 Serialize and Deserialize Binary Tree

Convert tree to string and back.

```javascript
class Codec {
    serialize(root) {
        if (root === null) return 'null';
        
        return `${root.val},${this.serialize(root.left)},${this.serialize(root.right)}`;
    }
    
    deserialize(data) {
        const values = data.split(',');
        let index = 0;
        
        function build() {
            if (values[index] === 'null') {
                index++;
                return null;
            }
            
            const node = new TreeNode(parseInt(values[index++]));
            node.left = build();
            node.right = build();
            return node;
        }
        
        return build();
    }
}
```

**Example:**
```
Tree:       Serialized:
    1       "1,2,null,null,3,4,null,null,5,null,null"
   / \
  2   3
     / \
    4   5
```

---

### 📖 Binary Tree Maximum Path Sum

```javascript
function maxPathSum(root) {
    let maxSum = -Infinity;
    
    function maxGain(node) {
        if (node === null) return 0;
        
        // Max gain from left and right (ignore negative)
        const leftGain = Math.max(0, maxGain(node.left));
        const rightGain = Math.max(0, maxGain(node.right));
        
        // Path through this node
        const pathSum = node.val + leftGain + rightGain;
        maxSum = Math.max(maxSum, pathSum);
        
        // Return max gain for parent (can only use one branch)
        return node.val + Math.max(leftGain, rightGain);
    }
    
    maxGain(root);
    return maxSum;
}
```

---

### 📖 Construct Tree from Traversals

**From Preorder and Inorder:**
```javascript
function buildTree(preorder, inorder) {
    const inorderMap = new Map();
    for (let i = 0; i < inorder.length; i++) {
        inorderMap.set(inorder[i], i);
    }
    
    let preorderIdx = 0;
    
    function build(left, right) {
        if (left > right) return null;
        
        const rootVal = preorder[preorderIdx++];
        const root = new TreeNode(rootVal);
        
        const mid = inorderMap.get(rootVal);
        
        root.left = build(left, mid - 1);
        root.right = build(mid + 1, right);
        
        return root;
    }
    
    return build(0, inorder.length - 1);
}
```

---

### ✅ Day 12 Checklist
- [ ] Understand AVL rotations conceptually
- [ ] Implement serialize/deserialize
- [ ] Complete: Max Path Sum, Construct from Traversals
- [ ] Practice: Flatten to Linked List

---

