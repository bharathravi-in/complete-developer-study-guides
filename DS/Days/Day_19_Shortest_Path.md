# 📚 DSA 30-Day Tutorial - Day 19

## Day 19: Shortest Path Algorithms

### 🎯 Learning Objectives
By the end of this day, you will:
- Implement Dijkstra's algorithm
- Understand Bellman-Ford for negative edges
- Know when to use each algorithm

---

### 📖 Dijkstra's Algorithm

Finds shortest path from source to all vertices. **No negative edges.**

```
       5
   A ───── B
   │ \     │
  3│  2\   │1
   │    \  │
   C ───── D
       1
```

```javascript
function dijkstra(graph, start) {
    const distances = {};
    const visited = new Set();
    
    // Initialize distances
    for (let node of graph.keys()) {
        distances[node] = Infinity;
    }
    distances[start] = 0;
    
    // Min heap: [distance, node]
    const heap = new MinHeap();
    heap.push([0, start]);
    
    while (heap.size() > 0) {
        const [dist, node] = heap.pop();
        
        if (visited.has(node)) continue;
        visited.add(node);
        
        for (let [neighbor, weight] of graph.get(node) || []) {
            const newDist = dist + weight;
            
            if (newDist < distances[neighbor]) {
                distances[neighbor] = newDist;
                heap.push([newDist, neighbor]);
            }
        }
    }
    
    return distances;
}
```

**Time:** O((V + E) log V) with min heap

---

### 📖 Network Delay Time

```javascript
function networkDelayTime(times, n, k) {
    // Build weighted graph
    const graph = new Map();
    for (let i = 1; i <= n; i++) graph.set(i, []);
    for (let [u, v, w] of times) {
        graph.get(u).push([v, w]);
    }
    
    // Dijkstra from k
    const dist = dijkstra(graph, k);
    
    // Find max distance
    let maxTime = 0;
    for (let i = 1; i <= n; i++) {
        if (dist[i] === Infinity) return -1;
        maxTime = Math.max(maxTime, dist[i]);
    }
    
    return maxTime;
}
```

---

### 📖 Bellman-Ford Algorithm

Works with negative edges. Detects negative cycles.

```javascript
function bellmanFord(n, edges, start) {
    const distances = new Array(n).fill(Infinity);
    distances[start] = 0;
    
    // Relax all edges (n-1) times
    for (let i = 0; i < n - 1; i++) {
        for (let [u, v, weight] of edges) {
            if (distances[u] !== Infinity && 
                distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight;
            }
        }
    }
    
    // Check for negative cycles (one more iteration)
    for (let [u, v, weight] of edges) {
        if (distances[u] !== Infinity && 
            distances[u] + weight < distances[v]) {
            return null;  // Negative cycle exists
        }
    }
    
    return distances;
}
```

**Time:** O(V × E)

---

### 📖 When to Use Which?

| Algorithm | Use Case | Time |
|-----------|----------|------|
| BFS | Unweighted graphs | O(V + E) |
| Dijkstra | Non-negative weights | O((V+E) log V) |
| Bellman-Ford | Negative weights allowed | O(V × E) |
| Floyd-Warshall | All pairs shortest path | O(V³) |

---

### ✅ Day 19 Checklist
- [ ] Implement Dijkstra with min heap
- [ ] Understand Bellman-Ford
- [ ] Complete: Network Delay Time
- [ ] Practice: Cheapest Flights Within K Stops

---

