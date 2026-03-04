# 📚 DSA 30-Day Tutorial - Day 16

## Day 16: BFS (Breadth-First Search)

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand BFS traversal
- Use BFS for shortest path (unweighted)
- Solve level-based problems

---

### 📖 BFS Template

BFS explores level by level using a **queue**.

```javascript
function bfs(graph, start) {
    const visited = new Set([start]);
    const queue = [start];
    
    while (queue.length > 0) {
        const node = queue.shift();
        console.log(node);  // Process node
        
        for (let neighbor of graph.get(node) || []) {
            if (!visited.has(neighbor)) {
                visited.add(neighbor);
                queue.push(neighbor);
            }
        }
    }
}
```

**BFS Visualization:**
```
Graph:       BFS from A:
  A          Level 0: A
 /|\         Level 1: B, C, D
B C D        Level 2: E, F
|   |
E   F

Queue trace:
[A] → process A, add B,C,D
[B,C,D] → process B, add E
[C,D,E] → process C
[D,E] → process D, add F
[E,F] → process E
[F] → process F
```

---

### 📖 Shortest Path (Unweighted Graph)

```javascript
function shortestPath(graph, start, end) {
    const visited = new Set([start]);
    const queue = [[start, 0]];  // [node, distance]
    
    while (queue.length > 0) {
        const [node, dist] = queue.shift();
        
        if (node === end) return dist;
        
        for (let neighbor of graph.get(node) || []) {
            if (!visited.has(neighbor)) {
                visited.add(neighbor);
                queue.push([neighbor, dist + 1]);
            }
        }
    }
    
    return -1;  // No path
}
```

---

### 📖 Number of Islands

```javascript
function numIslands(grid) {
    if (!grid.length) return 0;
    
    const rows = grid.length;
    const cols = grid[0].length;
    let islands = 0;
    
    function bfs(r, c) {
        const queue = [[r, c]];
        grid[r][c] = '0';  // Mark visited
        
        const directions = [[0, 1], [0, -1], [1, 0], [-1, 0]];
        
        while (queue.length > 0) {
            const [row, col] = queue.shift();
            
            for (let [dr, dc] of directions) {
                const newR = row + dr;
                const newC = col + dc;
                
                if (newR >= 0 && newR < rows && 
                    newC >= 0 && newC < cols && 
                    grid[newR][newC] === '1') {
                    grid[newR][newC] = '0';
                    queue.push([newR, newC]);
                }
            }
        }
    }
    
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (grid[r][c] === '1') {
                bfs(r, c);
                islands++;
            }
        }
    }
    
    return islands;
}
```

---

### 📖 Rotting Oranges (Multi-source BFS)

```javascript
function orangesRotting(grid) {
    const rows = grid.length;
    const cols = grid[0].length;
    const queue = [];
    let freshCount = 0;
    
    // Find all rotten oranges and count fresh
    for (let r = 0; r < rows; r++) {
        for (let c = 0; c < cols; c++) {
            if (grid[r][c] === 2) queue.push([r, c, 0]);
            else if (grid[r][c] === 1) freshCount++;
        }
    }
    
    if (freshCount === 0) return 0;
    
    const directions = [[0, 1], [0, -1], [1, 0], [-1, 0]];
    let minutes = 0;
    
    while (queue.length > 0) {
        const [r, c, time] = queue.shift();
        
        for (let [dr, dc] of directions) {
            const newR = r + dr;
            const newC = c + dc;
            
            if (newR >= 0 && newR < rows && 
                newC >= 0 && newC < cols && 
                grid[newR][newC] === 1) {
                grid[newR][newC] = 2;
                freshCount--;
                minutes = time + 1;
                queue.push([newR, newC, time + 1]);
            }
        }
    }
    
    return freshCount === 0 ? minutes : -1;
}
```

---

### ✅ Day 16 Checklist
- [ ] Implement BFS template
- [ ] Find shortest path in unweighted graph
- [ ] Complete: Number of Islands, Rotting Oranges
- [ ] Practice: Word Ladder, Open the Lock

---

