#!/usr/bin/env python3
"""Day 30 - Advanced Coding Problems"""

print("=" * 60)
print("CODING PROBLEMS - ADVANCED")
print("=" * 60)


# ============================================
# PROBLEM 1: LRU Cache
# ============================================
print("\n" + "-" * 60)
print("Problem 1: Implement LRU Cache")
print("-" * 60)
print("Least Recently Used cache with O(1) get and put")

from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]
    
    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # Remove first (least recently used)
            self.cache.popitem(last=False)

# Demo
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
print(f"get(1): {cache.get(1)}")  # 1
cache.put(3, 3)  # Evicts key 2
print(f"get(2): {cache.get(2)}")  # -1 (evicted)


# ============================================
# PROBLEM 2: Longest Substring Without Repeating
# ============================================
print("\n" + "-" * 60)
print("Problem 2: Longest Substring Without Repeating Characters")
print("-" * 60)

def length_of_longest_substring(s: str) -> int:
    """Sliding window approach - O(n)"""
    char_index = {}
    max_length = 0
    start = 0
    
    for end, char in enumerate(s):
        if char in char_index and char_index[char] >= start:
            start = char_index[char] + 1
        char_index[char] = end
        max_length = max(max_length, end - start + 1)
    
    return max_length

print(f"'abcabcbb': {length_of_longest_substring('abcabcbb')}")  # 3 ("abc")
print(f"'bbbbb': {length_of_longest_substring('bbbbb')}")  # 1 ("b")
print(f"'pwwkew': {length_of_longest_substring('pwwkew')}")  # 3 ("wke")


# ============================================
# PROBLEM 3: Merge Intervals
# ============================================
print("\n" + "-" * 60)
print("Problem 3: Merge Overlapping Intervals")
print("-" * 60)

def merge_intervals(intervals):
    """Sort by start, merge overlapping - O(n log n)"""
    if not intervals:
        return []
    
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    
    for current in intervals[1:]:
        last = merged[-1]
        if current[0] <= last[1]:  # Overlapping
            merged[-1] = [last[0], max(last[1], current[1])]
        else:
            merged.append(current)
    
    return merged

intervals = [[1,3], [2,6], [8,10], [15,18]]
print(f"Input: {intervals}")
print(f"Merged: {merge_intervals(intervals)}")  # [[1,6], [8,10], [15,18]]


# ============================================
# PROBLEM 4: Word Break
# ============================================
print("\n" + "-" * 60)
print("Problem 4: Word Break (Dynamic Programming)")
print("-" * 60)

def word_break(s: str, word_dict: list) -> bool:
    """DP: dp[i] = True if s[:i] can be segmented"""
    word_set = set(word_dict)
    dp = [False] * (len(s) + 1)
    dp[0] = True  # Empty string
    
    for i in range(1, len(s) + 1):
        for j in range(i):
            if dp[j] and s[j:i] in word_set:
                dp[i] = True
                break
    
    return dp[len(s)]

s = "leetcode"
word_dict = ["leet", "code"]
print(f"'{s}' with {word_dict}: {word_break(s, word_dict)}")  # True

s = "applepenapple"
word_dict = ["apple", "pen"]
print(f"'{s}' with {word_dict}: {word_break(s, word_dict)}")  # True


# ============================================
# PROBLEM 5: Validate BST
# ============================================
print("\n" + "-" * 60)
print("Problem 5: Validate Binary Search Tree")
print("-" * 60)

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def is_valid_bst(root, min_val=float('-inf'), max_val=float('inf')):
    """Check if tree is valid BST using range validation"""
    if not root:
        return True
    
    if root.val <= min_val or root.val >= max_val:
        return False
    
    return (is_valid_bst(root.left, min_val, root.val) and
            is_valid_bst(root.right, root.val, max_val))

# Valid BST: 2 -> 1, 3
valid_tree = TreeNode(2, TreeNode(1), TreeNode(3))
print(f"Valid BST [2,1,3]: {is_valid_bst(valid_tree)}")  # True

# Invalid BST: 5 -> 1, 4 (4 has children 3, 6)
invalid_tree = TreeNode(5, TreeNode(1), TreeNode(4, TreeNode(3), TreeNode(6)))
print(f"Invalid BST [5,1,4,null,null,3,6]: {is_valid_bst(invalid_tree)}")  # False


# ============================================
# PROBLEM 6: Top K Frequent Elements
# ============================================
print("\n" + "-" * 60)
print("Problem 6: Top K Frequent Elements")
print("-" * 60)

from collections import Counter
import heapq

def top_k_frequent(nums: list, k: int) -> list:
    """Using heap - O(n log k)"""
    count = Counter(nums)
    # Use min heap with negative freq for max behavior
    return heapq.nlargest(k, count.keys(), key=count.get)

nums = [1, 1, 1, 2, 2, 3]
k = 2
print(f"nums={nums}, k={k}")
print(f"Top {k} frequent: {top_k_frequent(nums, k)}")  # [1, 2]


# ============================================
# PROBLEM 7: Course Schedule (Topological Sort)
# ============================================
print("\n" + "-" * 60)
print("Problem 7: Course Schedule (Cycle Detection)")
print("-" * 60)

from collections import defaultdict, deque

def can_finish(num_courses: int, prerequisites: list) -> bool:
    """Kahn's algorithm (BFS topological sort)"""
    graph = defaultdict(list)
    in_degree = [0] * num_courses
    
    for course, prereq in prerequisites:
        graph[prereq].append(course)
        in_degree[course] += 1
    
    # Start with courses having no prerequisites
    queue = deque([i for i in range(num_courses) if in_degree[i] == 0])
    completed = 0
    
    while queue:
        course = queue.popleft()
        completed += 1
        
        for next_course in graph[course]:
            in_degree[next_course] -= 1
            if in_degree[next_course] == 0:
                queue.append(next_course)
    
    return completed == num_courses

print(f"2 courses, [[1,0]]: {can_finish(2, [[1,0]])}")  # True
print(f"2 courses, [[1,0],[0,1]]: {can_finish(2, [[1,0],[0,1]])}")  # False (cycle)


# ============================================
# PROBLEM 8: Serialize/Deserialize Binary Tree
# ============================================
print("\n" + "-" * 60)
print("Problem 8: Serialize/Deserialize Binary Tree")
print("-" * 60)

class Codec:
    def serialize(self, root) -> str:
        """Preorder traversal with null markers"""
        if not root:
            return "N"
        return f"{root.val},{self.serialize(root.left)},{self.serialize(root.right)}"
    
    def deserialize(self, data: str):
        """Rebuild from preorder"""
        values = iter(data.split(','))
        
        def build():
            val = next(values)
            if val == "N":
                return None
            node = TreeNode(int(val))
            node.left = build()
            node.right = build()
            return node
        
        return build()

codec = Codec()
tree = TreeNode(1, TreeNode(2), TreeNode(3, TreeNode(4), TreeNode(5)))
serialized = codec.serialize(tree)
print(f"Serialized: {serialized}")
deserialized = codec.deserialize(serialized)
print(f"Deserialized root: {deserialized.val}")


# ============================================
# PROBLEM 9: Median from Data Stream
# ============================================
print("\n" + "-" * 60)
print("Problem 9: Median from Data Stream")
print("-" * 60)

class MedianFinder:
    """Two heaps: max heap for lower half, min heap for upper half"""
    def __init__(self):
        self.small = []  # Max heap (negate values)
        self.large = []  # Min heap
    
    def add_num(self, num: int) -> None:
        # Add to max heap (small)
        heapq.heappush(self.small, -num)
        
        # Balance: ensure all small <= all large
        if self.small and self.large and -self.small[0] > self.large[0]:
            heapq.heappush(self.large, -heapq.heappop(self.small))
        
        # Keep sizes balanced (small can have 1 more)
        if len(self.small) > len(self.large) + 1:
            heapq.heappush(self.large, -heapq.heappop(self.small))
        if len(self.large) > len(self.small):
            heapq.heappush(self.small, -heapq.heappop(self.large))
    
    def find_median(self) -> float:
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2

mf = MedianFinder()
for num in [1, 2, 3, 4, 5]:
    mf.add_num(num)
    print(f"After adding {num}: median = {mf.find_median()}")


# ============================================
# PROBLEM 10: Trapping Rain Water
# ============================================
print("\n" + "-" * 60)
print("Problem 10: Trapping Rain Water")
print("-" * 60)

def trap(height: list) -> int:
    """Two pointer approach - O(n) time, O(1) space"""
    if not height:
        return 0
    
    left, right = 0, len(height) - 1
    left_max, right_max = height[left], height[right]
    water = 0
    
    while left < right:
        if left_max < right_max:
            left += 1
            left_max = max(left_max, height[left])
            water += left_max - height[left]
        else:
            right -= 1
            right_max = max(right_max, height[right])
            water += right_max - height[right]
    
    return water

heights = [0,1,0,2,1,0,1,3,2,1,2,1]
print(f"heights = {heights}")
print(f"Water trapped: {trap(heights)}")  # 6


# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 60)
print("ADVANCED PATTERNS TO MASTER")
print("=" * 60)
print("""
1. Sliding Window (substring problems)
2. Two Pointers (sorted arrays, palindromes)
3. Hash Maps (frequency, seen elements)
4. Dynamic Programming (optimization, counting)
5. BFS/DFS (graphs, trees)
6. Binary Search (sorted data, search space)
7. Heaps (top K, streaming median)
8. Topological Sort (dependencies, ordering)
9. Union Find (connected components)
10. Tries (prefix matching, autocomplete)

Time Complexity Goals:
- O(1): Hash operations
- O(log n): Binary search, heap operations
- O(n): Linear scan, two pointers
- O(n log n): Sorting, heap-based solutions
- O(n²): Nested loops (try to avoid)
""")
