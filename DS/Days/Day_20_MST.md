# 📚 DSA 30-Day Tutorial - Day 20

## Day 20: Minimum Spanning Tree

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand MST concept
- Implement Kruskal's algorithm
- Implement Prim's algorithm

---

### 📖 What is MST?

Minimum Spanning Tree connects all vertices with minimum total edge weight, using exactly V-1 edges.

```
       4      
   A ───── B
   │\     /│
  1│ 2   3 │6
   │  \ /  │
   C ───── D
       5
       
MST (weight = 1 + 2 + 3 = 6):
   A       B
   │\     /
  1│ 2   3
   │  \ /
   C     D
```

---

### 📖 Kruskal's Algorithm

1. Sort edges by weight
2. Add edges one by one (skip if creates cycle)
3. Use Union Find to detect cycles

```javascript
function kruskal(n, edges) {
    // Sort edges by weight
    edges.sort((a, b) => a[2] - b[2]);
    
    const uf = new UnionFind(n);
    const mst = [];
    let totalWeight = 0;
    
    for (let [u, v, weight] of edges) {
        // Add edge if doesn't create cycle
        if (uf.union(u, v)) {
            mst.push([u, v, weight]);
            totalWeight += weight;
            
            // MST complete when we have n-1 edges
            if (mst.length === n - 1) break;
        }
    }
    
    return { mst, totalWeight };
}
```

---

### 📖 Prim's Algorithm

Start from any vertex, always add the minimum weight edge that connects visited to unvisited.

```javascript
function prim(graph, n) {
    const visited = new Set();
    const mst = [];
    let totalWeight = 0;
    
    // Min heap: [weight, from, to]
    const heap = new MinHeap();
    heap.push([0, -1, 0]);  // Start from vertex 0
    
    while (visited.size < n && heap.size() > 0) {
        const [weight, from, to] = heap.pop();
        
        if (visited.has(to)) continue;
        visited.add(to);
        
        if (from !== -1) {
            mst.push([from, to, weight]);
            totalWeight += weight;
        }
        
        for (let [neighbor, edgeWeight] of graph.get(to) || []) {
            if (!visited.has(neighbor)) {
                heap.push([edgeWeight, to, neighbor]);
            }
        }
    }
    
    return { mst, totalWeight };
}
```

---

### 📖 Min Cost to Connect All Points

```javascript
function minCostConnectPoints(points) {
    const n = points.length;
    
    // Build complete graph with Manhattan distances
    const edges = [];
    for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
            const dist = Math.abs(points[i][0] - points[j][0]) + 
                        Math.abs(points[i][1] - points[j][1]);
            edges.push([i, j, dist]);
        }
    }
    
    // Kruskal's algorithm
    const { totalWeight } = kruskal(n, edges);
    return totalWeight;
}
```

---

### ✅ Day 20 Checklist
- [ ] Understand MST concept
- [ ] Implement Kruskal's with Union Find
- [ ] Implement Prim's with min heap
- [ ] Complete: Min Cost to Connect Points

---

