# 📚 DSA 30-Day Tutorial - Day 18

## Day 18: Topological Sort & Union Find

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand topological ordering
- Implement Kahn's algorithm (BFS)
- Implement Union Find (Disjoint Set)

---

### 📖 Topological Sort

Linear ordering of vertices in DAG such that for every edge u→v, u comes before v.

```
Course prerequisites:
  0 → 1 → 3
       ↘   ↓
         2 → 4

Possible order: 0, 1, 2, 3, 4
```

#### Kahn's Algorithm (BFS approach)

```javascript
function topologicalSort(numCourses, prerequisites) {
    const graph = new Map();
    const inDegree = new Array(numCourses).fill(0);
    
    // Build graph and count in-degrees
    for (let i = 0; i < numCourses; i++) graph.set(i, []);
    for (let [course, prereq] of prerequisites) {
        graph.get(prereq).push(course);
        inDegree[course]++;
    }
    
    // Start with nodes having no prerequisites
    const queue = [];
    for (let i = 0; i < numCourses; i++) {
        if (inDegree[i] === 0) queue.push(i);
    }
    
    const result = [];
    while (queue.length > 0) {
        const node = queue.shift();
        result.push(node);
        
        for (let neighbor of graph.get(node)) {
            inDegree[neighbor]--;
            if (inDegree[neighbor] === 0) {
                queue.push(neighbor);
            }
        }
    }
    
    // If we processed all nodes, valid ordering exists
    return result.length === numCourses ? result : [];
}
```

---

### 📖 Union Find (Disjoint Set Union)

Tracks elements partitioned into disjoint sets. Supports:
- **Find:** Which set does element belong to?
- **Union:** Merge two sets

```javascript
class UnionFind {
    constructor(n) {
        this.parent = Array.from({ length: n }, (_, i) => i);
        this.rank = new Array(n).fill(0);
    }
    
    // Find with path compression
    find(x) {
        if (this.parent[x] !== x) {
            this.parent[x] = this.find(this.parent[x]);
        }
        return this.parent[x];
    }
    
    // Union by rank
    union(x, y) {
        const rootX = this.find(x);
        const rootY = this.find(y);
        
        if (rootX === rootY) return false;  // Already connected
        
        if (this.rank[rootX] < this.rank[rootY]) {
            this.parent[rootX] = rootY;
        } else if (this.rank[rootX] > this.rank[rootY]) {
            this.parent[rootY] = rootX;
        } else {
            this.parent[rootY] = rootX;
            this.rank[rootX]++;
        }
        
        return true;
    }
    
    connected(x, y) {
        return this.find(x) === this.find(y);
    }
}
```

**Visual:**
```
Initial: [0] [1] [2] [3] [4]  (each is its own set)

union(0, 1):
    0
    |
    1

union(2, 3):
    0       2
    |       |
    1       3

union(0, 2):
      0
     /|\
    1 2
      |
      3
```

---

### 📖 Number of Connected Components

```javascript
function countComponents(n, edges) {
    const uf = new UnionFind(n);
    let components = n;
    
    for (let [u, v] of edges) {
        if (uf.union(u, v)) {
            components--;
        }
    }
    
    return components;
}
```

---

### ✅ Day 18 Checklist
- [ ] Implement topological sort (Kahn's algorithm)
- [ ] Implement Union Find with path compression
- [ ] Complete: Course Schedule II, Number of Provinces
- [ ] Practice: Redundant Connection, Accounts Merge

---

