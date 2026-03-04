#!/usr/bin/env python3
"""Day 18 - Data Structures Implementation"""

from typing import Any, Optional, List, Generic, TypeVar
from collections import deque

T = TypeVar('T')

print("=" * 50)
print("DATA STRUCTURES")
print("=" * 50)


# ============================================
# 1. LINKED LIST
# ============================================
print("\n--- 1. LINKED LIST ---")


class ListNode:
    """Node for singly linked list"""
    def __init__(self, val: T, next: Optional['ListNode'] = None):
        self.val = val
        self.next = next


class LinkedList(Generic[T]):
    """Singly linked list implementation"""
    
    def __init__(self):
        self.head: Optional[ListNode] = None
        self._size = 0
    
    def append(self, val: T) -> None:
        """Add to end: O(n)"""
        new_node = ListNode(val)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self._size += 1
    
    def prepend(self, val: T) -> None:
        """Add to beginning: O(1)"""
        new_node = ListNode(val, self.head)
        self.head = new_node
        self._size += 1
    
    def delete(self, val: T) -> bool:
        """Delete first occurrence: O(n)"""
        if not self.head:
            return False
        
        if self.head.val == val:
            self.head = self.head.next
            self._size -= 1
            return True
        
        current = self.head
        while current.next:
            if current.next.val == val:
                current.next = current.next.next
                self._size -= 1
                return True
            current = current.next
        return False
    
    def find(self, val: T) -> Optional[ListNode]:
        """Find node by value: O(n)"""
        current = self.head
        while current:
            if current.val == val:
                return current
            current = current.next
        return None
    
    def reverse(self) -> None:
        """Reverse in place: O(n)"""
        prev = None
        current = self.head
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        self.head = prev
    
    def __len__(self) -> int:
        return self._size
    
    def __iter__(self):
        current = self.head
        while current:
            yield current.val
            current = current.next
    
    def __repr__(self) -> str:
        return " -> ".join(str(val) for val in self) + " -> None"


# Test LinkedList
ll = LinkedList()
for i in [1, 2, 3, 4, 5]:
    ll.append(i)
print(f"LinkedList: {ll}")
ll.reverse()
print(f"Reversed: {ll}")


# ============================================
# 2. STACK
# ============================================
print("\n--- 2. STACK ---")


class Stack(Generic[T]):
    """LIFO Stack implementation"""
    
    def __init__(self):
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        """Add to top: O(1)"""
        self._items.append(item)
    
    def pop(self) -> T:
        """Remove from top: O(1)"""
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self._items.pop()
    
    def peek(self) -> T:
        """View top without removing: O(1)"""
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self._items[-1]
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
    
    def __len__(self) -> int:
        return len(self._items)
    
    def __repr__(self) -> str:
        return f"Stack({self._items})"


# Stack example: Balanced parentheses
def is_balanced(s: str) -> bool:
    """Check if parentheses are balanced"""
    stack = Stack()
    pairs = {')': '(', ']': '[', '}': '{'}
    
    for char in s:
        if char in '([{':
            stack.push(char)
        elif char in ')]}':
            if stack.is_empty() or stack.pop() != pairs[char]:
                return False
    
    return stack.is_empty()


test_cases = ["(())", "([{}])", "(()", "([)]"]
for s in test_cases:
    print(f"  '{s}' is balanced: {is_balanced(s)}")


# ============================================
# 3. QUEUE
# ============================================
print("\n--- 3. QUEUE ---")


class Queue(Generic[T]):
    """FIFO Queue implementation"""
    
    def __init__(self):
        self._items: deque = deque()
    
    def enqueue(self, item: T) -> None:
        """Add to back: O(1)"""
        self._items.append(item)
    
    def dequeue(self) -> T:
        """Remove from front: O(1)"""
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self._items.popleft()
    
    def peek(self) -> T:
        """View front: O(1)"""
        if self.is_empty():
            raise IndexError("Queue is empty")
        return self._items[0]
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
    
    def __len__(self) -> int:
        return len(self._items)


# Test Queue
q = Queue()
for i in range(5):
    q.enqueue(i)
print(f"Queue: {list(q._items)}")
print(f"Dequeue: {q.dequeue()}, {q.dequeue()}")
print(f"After: {list(q._items)}")


# ============================================
# 4. HASH MAP
# ============================================
print("\n--- 4. HASH MAP ---")


class HashMap:
    """Simple hash map implementation"""
    
    def __init__(self, capacity: int = 16):
        self.capacity = capacity
        self.size = 0
        self.buckets: List[List] = [[] for _ in range(capacity)]
    
    def _hash(self, key: Any) -> int:
        """Get bucket index for key"""
        return hash(key) % self.capacity
    
    def put(self, key: Any, value: Any) -> None:
        """Insert or update: O(1) average"""
        index = self._hash(key)
        bucket = self.buckets[index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        
        bucket.append((key, value))
        self.size += 1
    
    def get(self, key: Any, default: Any = None) -> Any:
        """Get value: O(1) average"""
        index = self._hash(key)
        for k, v in self.buckets[index]:
            if k == key:
                return v
        return default
    
    def remove(self, key: Any) -> bool:
        """Remove key: O(1) average"""
        index = self._hash(key)
        bucket = self.buckets[index]
        
        for i, (k, v) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self.size -= 1
                return True
        return False
    
    def __repr__(self) -> str:
        items = []
        for bucket in self.buckets:
            items.extend(bucket)
        return f"HashMap({dict(items)})"


# Test HashMap
hm = HashMap()
hm.put("name", "Alice")
hm.put("age", 30)
hm.put("city", "NYC")
print(f"HashMap: {hm}")
print(f"get('name'): {hm.get('name')}")
print(f"get('unknown', 'default'): {hm.get('unknown', 'default')}")


# ============================================
# 5. BINARY TREE
# ============================================
print("\n--- 5. BINARY TREE ---")


class TreeNode:
    """Node for binary tree"""
    def __init__(self, val: T):
        self.val = val
        self.left: Optional['TreeNode'] = None
        self.right: Optional['TreeNode'] = None


class BinarySearchTree:
    """Binary Search Tree implementation"""
    
    def __init__(self):
        self.root: Optional[TreeNode] = None
    
    def insert(self, val: T) -> None:
        """Insert value: O(log n) average"""
        if not self.root:
            self.root = TreeNode(val)
        else:
            self._insert_recursive(self.root, val)
    
    def _insert_recursive(self, node: TreeNode, val: T) -> None:
        if val < node.val:
            if node.left:
                self._insert_recursive(node.left, val)
            else:
                node.left = TreeNode(val)
        else:
            if node.right:
                self._insert_recursive(node.right, val)
            else:
                node.right = TreeNode(val)
    
    def search(self, val: T) -> bool:
        """Search for value: O(log n) average"""
        return self._search_recursive(self.root, val)
    
    def _search_recursive(self, node: Optional[TreeNode], val: T) -> bool:
        if not node:
            return False
        if val == node.val:
            return True
        elif val < node.val:
            return self._search_recursive(node.left, val)
        else:
            return self._search_recursive(node.right, val)
    
    def inorder(self) -> List[T]:
        """In-order traversal (sorted): O(n)"""
        result = []
        self._inorder_recursive(self.root, result)
        return result
    
    def _inorder_recursive(self, node: Optional[TreeNode], result: List[T]) -> None:
        if node:
            self._inorder_recursive(node.left, result)
            result.append(node.val)
            self._inorder_recursive(node.right, result)
    
    def preorder(self) -> List[T]:
        """Pre-order traversal: O(n)"""
        result = []
        self._preorder_recursive(self.root, result)
        return result
    
    def _preorder_recursive(self, node: Optional[TreeNode], result: List[T]) -> None:
        if node:
            result.append(node.val)
            self._preorder_recursive(node.left, result)
            self._preorder_recursive(node.right, result)


# Test BST
bst = BinarySearchTree()
for val in [5, 3, 7, 1, 4, 6, 8]:
    bst.insert(val)
print(f"BST in-order: {bst.inorder()}")
print(f"BST pre-order: {bst.preorder()}")
print(f"Search 4: {bst.search(4)}")
print(f"Search 10: {bst.search(10)}")


# ============================================
# 6. MIN HEAP
# ============================================
print("\n--- 6. MIN HEAP ---")


class MinHeap:
    """Min Heap implementation"""
    
    def __init__(self):
        self.heap: List[T] = []
    
    def push(self, val: T) -> None:
        """Add value: O(log n)"""
        self.heap.append(val)
        self._sift_up(len(self.heap) - 1)
    
    def pop(self) -> T:
        """Remove minimum: O(log n)"""
        if not self.heap:
            raise IndexError("Heap is empty")
        
        if len(self.heap) == 1:
            return self.heap.pop()
        
        min_val = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return min_val
    
    def peek(self) -> T:
        """View minimum: O(1)"""
        if not self.heap:
            raise IndexError("Heap is empty")
        return self.heap[0]
    
    def _sift_up(self, index: int) -> None:
        parent = (index - 1) // 2
        while index > 0 and self.heap[index] < self.heap[parent]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            index = parent
            parent = (index - 1) // 2
    
    def _sift_down(self, index: int) -> None:
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2
        
        if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
            smallest = left
        if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
            smallest = right
        
        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._sift_down(smallest)
    
    def __len__(self) -> int:
        return len(self.heap)


# Test MinHeap
heap = MinHeap()
for val in [5, 3, 8, 1, 2, 7]:
    heap.push(val)

print("Heap extract min:", end=" ")
while len(heap) > 0:
    print(heap.pop(), end=" ")
print()


print("\n✅ Data structures completed!")
