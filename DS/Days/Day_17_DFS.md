# 📚 DSA 30-Day Tutorial - Day 17

## Day 17: DFS (Depth-First Search)

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand DFS traversal (recursive & iterative)
- Use DFS for path finding and cycle detection
- Recognize DFS vs BFS use cases

---

### 📖 DFS Templates

#### Recursive DFS
```javascript
function dfsRecursive(graph, node, visited = new Set()) {
    if (visited.has(node)) return;
    
    visited.add(node);
    console.log(node);  // Process node
    
    for (let neighbor of graph.get(node) || []) {
        dfsRecursive(graph, neighbor, visited);
    }
}
```

#### Iterative DFS (using stack)
```javascript
function dfsIterative(graph, start) {
    const visited = new Set();
    const stack = [start];
    
    while (stack.length > 0) {
        const node = stack.pop();
        
        if (visited.has(node)) continue;
        visited.add(node);
        console.log(node);  // Process node
        
        for (let neighbor of graph.get(node) || []) {
            if (!visited.has(neighbor)) {
                stack.push(neighbor);
            }
        }
    }
}
```

---

### 📖 DFS on Grid

```javascript
function dfsGrid(grid, row, col, visited) {
    const rows = grid.length;
    const cols = grid[0].length;
    
    // Boundary and visited check
    if (row < 0 || row >= rows || col < 0 || col >= cols) return;
    if (visited.has(`${row},${col}`)) return;
    if (grid[row][col] === 0) return;  // Not valid cell
    
    visited.add(`${row},${col}`);
    
    // Explore 4 directions
    dfsGrid(grid, row + 1, col, visited);  // Down
    dfsGrid(grid, row - 1, col, visited);  // Up
    dfsGrid(grid, row, col + 1, visited);  // Right
    dfsGrid(grid, row, col - 1, visited);  // Left
}
```

---

### 📖 Clone Graph

```javascript
function cloneGraph(node) {
    if (!node) return null;
    
    const visited = new Map();  // original → clone
    
    function dfs(node) {
        if (visited.has(node)) return visited.get(node);
        
        const clone = new Node(node.val);
        visited.set(node, clone);
        
        for (let neighbor of node.neighbors) {
            clone.neighbors.push(dfs(neighbor));
        }
        
        return clone;
    }
    
    return dfs(node);
}
```

---

### 📖 Cycle Detection in Directed Graph

```javascript
function hasCycle(numCourses, prerequisites) {
    const graph = new Map();
    for (let i = 0; i < numCourses; i++) graph.set(i, []);
    for (let [course, prereq] of prerequisites) {
        graph.get(prereq).push(course);
    }
    
    // 0: unvisited, 1: visiting (in current path), 2: visited
    const state = new Array(numCourses).fill(0);
    
    function dfs(node) {
        if (state[node] === 1) return true;   // Cycle found
        if (state[node] === 2) return false;  // Already processed
        
        state[node] = 1;  // Mark as visiting
        
        for (let neighbor of graph.get(node)) {
            if (dfs(neighbor)) return true;
        }
        
        state[node] = 2;  // Mark as fully visited
        return false;
    }
    
    for (let i = 0; i < numCourses; i++) {
        if (dfs(i)) return true;
    }
    
    return false;
}
```

---

### 📖 BFS vs DFS

| Aspect | BFS | DFS |
|--------|-----|-----|
| Data Structure | Queue | Stack/Recursion |
| Memory | O(width of tree) | O(height of tree) |
| Shortest Path | Yes (unweighted) | No |
| Best for | Level order, shortest path | Path finding, backtracking |
| Completeness | Always finds solution | May get stuck in deep path |

---

### ✅ Day 17 Checklist
- [ ] Implement DFS (recursive & iterative)
- [ ] Understand cycle detection
- [ ] Complete: Clone Graph, Course Schedule
- [ ] Practice: Number of Provinces, Pacific Atlantic

---

