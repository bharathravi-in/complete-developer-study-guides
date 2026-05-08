# Day 18-19: Data Structures & Algorithms in Python

## Learning Objectives
- Implement core data structures from scratch (LinkedList, Stack, Queue, Tree, Graph)
- Master common algorithms (sorting, searching, traversal)
- Analyze time/space complexity with Big O notation
- Solve interview-style problems using Python idioms
- Know when to use which built-in data structure

---

## 1. Core Data Structures (Beginner)

### Stack & Queue

```python
from collections import deque

# Stack (LIFO) — list works fine
class Stack:
    def __init__(self):
        self._items = []
    
    def push(self, item):
        self._items.append(item)  # O(1)
    
    def pop(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self._items.pop()  # O(1)
    
    def peek(self):
        return self._items[-1]
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
    
    def __len__(self):
        return len(self._items)

# Queue (FIFO) — use deque (O(1) both ends)
class Queue:
    def __init__(self):
        self._items = deque()
    
    def enqueue(self, item):
        self._items.append(item)     # O(1)
    
    def dequeue(self):
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self._items.popleft()  # O(1) — list.pop(0) is O(n)!
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
```

### Linked List

```python
class Node:
    def __init__(self, value, next=None):
        self.value = value
        self.next = next

class LinkedList:
    def __init__(self):
        self.head = None
        self._size = 0
    
    def prepend(self, value):  # O(1)
        self.head = Node(value, self.head)
        self._size += 1
    
    def append(self, value):  # O(n) without tail pointer
        if not self.head:
            self.head = Node(value)
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = Node(value)
        self._size += 1
    
    def find(self, value) -> bool:  # O(n)
        current = self.head
        while current:
            if current.value == value:
                return True
            current = current.next
        return False
    
    def delete(self, value):  # O(n)
        if not self.head:
            return
        if self.head.value == value:
            self.head = self.head.next
            self._size -= 1
            return
        current = self.head
        while current.next:
            if current.next.value == value:
                current.next = current.next.next
                self._size -= 1
                return
            current = current.next
    
    def reverse(self):  # O(n) in-place
        prev = None
        current = self.head
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        self.head = prev
    
    def __iter__(self):
        current = self.head
        while current:
            yield current.value
            current = current.next
    
    def __len__(self):
        return self._size
```

---

## 2. Trees & Hash Maps (Intermediate)

### Binary Search Tree

```python
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

class BST:
    def __init__(self):
        self.root = None
    
    def insert(self, value):  # O(log n) average, O(n) worst
        if not self.root:
            self.root = TreeNode(value)
            return
        self._insert(self.root, value)
    
    def _insert(self, node, value):
        if value < node.value:
            if node.left is None:
                node.left = TreeNode(value)
            else:
                self._insert(node.left, value)
        else:
            if node.right is None:
                node.right = TreeNode(value)
            else:
                self._insert(node.right, value)
    
    def search(self, value) -> bool:  # O(log n) average
        return self._search(self.root, value)
    
    def _search(self, node, value) -> bool:
        if not node:
            return False
        if value == node.value:
            return True
        elif value < node.value:
            return self._search(node.left, value)
        else:
            return self._search(node.right, value)
    
    # Traversals
    def inorder(self, node=None) -> list:
        """Left → Root → Right (sorted order for BST)."""
        if node is None:
            node = self.root
        result = []
        if node:
            result.extend(self.inorder(node.left))
            result.append(node.value)
            result.extend(self.inorder(node.right))
        return result
    
    def bfs(self) -> list:
        """Breadth-first (level-order) traversal."""
        if not self.root:
            return []
        result = []
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            result.append(node.value)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        return result

tree = BST()
for val in [8, 3, 10, 1, 6, 14, 4, 7]:
    tree.insert(val)
print(tree.inorder())  # [1, 3, 4, 6, 7, 8, 10, 14]
print(tree.bfs())      # [8, 3, 10, 1, 6, 14, 4, 7]
```

### Hash Map Implementation

```python
class HashMap:
    """Simple hash map with chaining for collision resolution."""
    
    def __init__(self, capacity: int = 16):
        self.capacity = capacity
        self.size = 0
        self.buckets: list[list] = [[] for _ in range(capacity)]
    
    def _hash(self, key) -> int:
        return hash(key) % self.capacity
    
    def put(self, key, value):  # O(1) average
        index = self._hash(key)
        bucket = self.buckets[index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)  # Update
                return
        
        bucket.append((key, value))  # Insert
        self.size += 1
        
        # Resize if load factor > 0.75
        if self.size / self.capacity > 0.75:
            self._resize()
    
    def get(self, key, default=None):  # O(1) average
        index = self._hash(key)
        for k, v in self.buckets[index]:
            if k == key:
                return v
        return default
    
    def _resize(self):
        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [[] for _ in range(self.capacity)]
        self.size = 0
        for bucket in old_buckets:
            for key, value in bucket:
                self.put(key, value)
```

---

## 3. Algorithms (Advanced)

### Sorting

```python
def merge_sort(arr: list) -> list:
    """O(n log n) — stable, predictable performance."""
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    # Merge two sorted arrays
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

def quick_sort(arr: list) -> list:
    """O(n log n) average, O(n²) worst. In-place variant exists."""
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)
```

### Binary Search

```python
def binary_search(arr: list, target) -> int:
    """O(log n) — array must be sorted."""
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1

# Python built-in
import bisect
sorted_list = [1, 3, 5, 7, 9, 11]
index = bisect.bisect_left(sorted_list, 7)  # 3
bisect.insort(sorted_list, 6)  # Inserts in sorted position
```

### Graph Algorithms

```python
from collections import defaultdict, deque

class Graph:
    def __init__(self):
        self.adjacency = defaultdict(list)
    
    def add_edge(self, u, v, directed=False):
        self.adjacency[u].append(v)
        if not directed:
            self.adjacency[v].append(u)
    
    def bfs(self, start) -> list:
        """Breadth-first search — shortest path in unweighted graph."""
        visited = set([start])
        queue = deque([start])
        order = []
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor in self.adjacency[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order
    
    def dfs(self, start) -> list:
        """Depth-first search — explore as deep as possible first."""
        visited = set()
        order = []
        
        def _dfs(node):
            visited.add(node)
            order.append(node)
            for neighbor in self.adjacency[node]:
                if neighbor not in visited:
                    _dfs(neighbor)
        
        _dfs(start)
        return order
    
    def shortest_path(self, start, end) -> list:
        """BFS shortest path."""
        queue = deque([(start, [start])])
        visited = {start}
        while queue:
            node, path = queue.popleft()
            if node == end:
                return path
            for neighbor in self.adjacency[node]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []  # No path exists
```

### Big O Complexity Reference

| Structure | Access | Search | Insert | Delete |
|-----------|--------|--------|--------|--------|
| Array/List | O(1) | O(n) | O(n) | O(n) |
| Dict/Set | - | O(1) | O(1) | O(1) |
| Deque | O(n) | O(n) | O(1) | O(1) |
| BST (balanced) | - | O(log n) | O(log n) | O(log n) |
| Heap | - | O(n) | O(log n) | O(log n) |

---

## Interview Questions

### Beginner
1. **When do you use a list vs dict vs set in Python?** List: ordered collection, need index access, allow duplicates. Dict: key-value mapping, O(1) lookup by key, need associations. Set: unique elements, O(1) membership test, set operations (union, intersection). Performance: `x in set` is O(1) vs `x in list` is O(n). Choose based on access pattern.

2. **What's the time complexity of `list.append()` vs `list.insert(0, x)`?** `append()`: O(1) amortized (occasionally O(n) when resizing). `insert(0, x)`: O(n) because all elements must shift right. This is why `collections.deque` exists — O(1) on both ends. Similarly, `list.pop()` is O(1) but `list.pop(0)` is O(n).

3. **Explain the difference between BFS and DFS.** BFS (Breadth-First): explores level by level, uses a queue, finds shortest path in unweighted graphs. DFS (Depth-First): explores as deep as possible before backtracking, uses stack/recursion, good for maze-solving, cycle detection. Memory: BFS stores entire level (can be large), DFS stores one path (depth).

### Intermediate
4. **How does Python's `dict` work internally?** Hash table with open addressing. Key is hashed → index computed → stored in array. Collisions resolved by probing (looking at next slots). Load factor kept below 2/3 (resizes at that point). Python 3.7+: insertion order preserved (implementation detail → guaranteed in 3.7). Average O(1) operations, O(n) worst case with many collisions.

5. **Implement a function to detect a cycle in a linked list.** Floyd's Tortoise & Hare: use two pointers (slow moves 1 step, fast moves 2 steps). If they meet → cycle exists. If fast reaches None → no cycle. Time: O(n), Space: O(1). To find cycle start: reset slow to head, move both at 1 step — they meet at cycle start.

6. **What is a heap and when would you use one?** A heap is a complete binary tree where parent ≤ children (min-heap). Provides O(1) access to min, O(log n) insert/extract-min. Use for: priority queues, top-K elements, merge K sorted lists, scheduling. Python: `heapq` module (min-heap only, negate for max-heap).

### Advanced
7. **Design an LRU Cache with O(1) operations.** Use: OrderedDict (or dict + doubly-linked list). `get(key)`: if exists, move to end (most recent), return value. `put(key, value)`: if full, remove first item (least recent); add to end. Python: `collections.OrderedDict` with `move_to_end()` and `popitem(last=False)`. Or use `functools.lru_cache` built-in.

8. **Explain when you'd choose different sorting algorithms.** Merge sort: stable, guaranteed O(n log n), good for linked lists, external sorting. Quick sort: fastest in practice (cache-friendly), O(n log n) average, not stable. Tim sort (Python's built-in): hybrid merge+insertion, stable, adapts to partially sorted data. Radix/counting sort: O(n) for bounded integers.

9. **Solve: Given an array, find two numbers that sum to a target. Optimize.** Brute force: O(n²) nested loops. Optimal: O(n) using a hash set. Iterate once: for each number, check if `target - number` is in the set. If yes, found pair. If no, add current number to set. One pass, O(n) time, O(n) space. This is the "Two Sum" pattern — foundational for many problems.

---

## Hands-On Exercise
1. Implement a doubly-linked list with `reverse()` and `find_middle()`
2. Build a min-heap from scratch and implement heap sort
3. Implement BFS shortest path and DFS cycle detection on a graph
4. Solve "Two Sum", "Valid Parentheses", and "Merge Intervals" in Python
5. Build an LRU Cache class that passes the LeetCode problem
