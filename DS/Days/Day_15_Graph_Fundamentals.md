# 📚 DSA 30-Day Tutorial - Day 15

## Day 15: Graph Fundamentals

### 🎯 Learning Objectives
By the end of this day, you will:
- Understand graph terminology
- Implement adjacency list and matrix
- Know when to use which representation

---

### 📖 Graph Terminology

```
     A -------- B
     |  \      /|
     |   \    / |
     |    \  /  |
     |     \/   |
     |     /\   |
     |    /  \  |
     D--------C |
      \        /
       \------/

Vertices (Nodes): A, B, C, D
Edges: A-B, A-C, A-D, B-C, C-D, B-C
Degree of vertex: Number of edges connected (A has degree 3)
Path: Sequence of vertices (A→B→C)
Cycle: Path that starts and ends at same vertex
Connected: Path exists between all vertex pairs
```

**Directed vs Undirected:**
```
Undirected:  A --- B    (can go both ways)
Directed:    A --→ B    (one way only)
```

**Weighted vs Unweighted:**
```
Unweighted:  A --- B
Weighted:    A -5- B    (edge has weight 5)
```

---

### 📖 Graph Representations

#### 1. Adjacency List (Preferred for sparse graphs)

```javascript
// Using Map
const graph = new Map([
    ['A', ['B', 'C', 'D']],
    ['B', ['A', 'C']],
    ['C', ['A', 'B', 'D']],
    ['D', ['A', 'C']]
]);

// Using Object
const graph = {
    'A': ['B', 'C', 'D'],
    'B': ['A', 'C'],
    'C': ['A', 'B', 'D'],
    'D': ['A', 'C']
};

// For weighted graph: store [neighbor, weight]
const weightedGraph = {
    'A': [['B', 5], ['C', 3]],
    'B': [['A', 5], ['C', 2]],
    'C': [['A', 3], ['B', 2]]
};
```

**Space:** O(V + E)

#### 2. Adjacency Matrix

```javascript
//     A  B  C  D
// A [ 0, 1, 1, 1 ]
// B [ 1, 0, 1, 0 ]
// C [ 1, 1, 0, 1 ]
// D [ 1, 0, 1, 0 ]

const matrix = [
    [0, 1, 1, 1],
    [1, 0, 1, 0],
    [1, 1, 0, 1],
    [1, 0, 1, 0]
];

// Check if A-B connected: matrix[0][1] === 1
```

**Space:** O(V²)

---

### 📖 Building Graph from Edges

```javascript
function buildGraph(n, edges, directed = false) {
    const graph = new Map();
    
    // Initialize all vertices
    for (let i = 0; i < n; i++) {
        graph.set(i, []);
    }
    
    // Add edges
    for (let [u, v] of edges) {
        graph.get(u).push(v);
        if (!directed) {
            graph.get(v).push(u);
        }
    }
    
    return graph;
}

// Example: edges = [[0,1], [0,2], [1,2]]
// Undirected: {0: [1,2], 1: [0,2], 2: [0,1]}
```

---

### 📖 When to Use Which?

| Aspect | Adjacency List | Adjacency Matrix |
|--------|----------------|------------------|
| Space | O(V + E) | O(V²) |
| Check edge exists | O(degree) | O(1) |
| Find all neighbors | O(degree) | O(V) |
| Best for | Sparse graphs | Dense graphs |
| Examples | Social networks, Roads | Complete graphs |

---

### ✅ Day 15 Checklist
- [ ] Understand graph terminology
- [ ] Implement both representations
- [ ] Build graph from edge list
- [ ] Know when to use which representation

---

