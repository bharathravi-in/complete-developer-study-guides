# 30-Day LeetCode Practice Plan for Senior Engineers
## Exact Problem List with Links and Difficulty

---

## Week 1: Foundations with Advanced Thinking

### Day 1-2: Time & Space Complexity

**Focus:** Understanding complexity analysis through practice

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Contains Duplicate | Easy | [LC 217](https://leetcode.com/problems/contains-duplicate/) | O(n) vs O(n²) tradeoff |
| 2 | Valid Anagram | Easy | [LC 242](https://leetcode.com/problems/valid-anagram/) | Sorting vs HashMap |
| 3 | Two Sum | Easy | [LC 1](https://leetcode.com/problems/two-sum/) | Brute force to optimal |
| 4 | 3Sum | Medium | [LC 15](https://leetcode.com/problems/3sum/) | O(n²) vs O(n³) |
| 5 | Sort Colors | Medium | [LC 75](https://leetcode.com/problems/sort-colors/) | In-place O(n) |
| 6 | Kth Largest Element in Array | Medium | [LC 215](https://leetcode.com/problems/kth-largest-element-in-an-array/) | Quickselect vs Heap |

**Complexity Practice:**
- Analyze each solution's time and space complexity
- Write multiple approaches and compare

---

### Day 3-4: Arrays & Strings (Advanced Patterns)

#### Two Pointer Problems

| # | Problem | Difficulty | Link | Pattern |
|---|---------|------------|------|---------|
| 1 | Two Sum II - Sorted Array | Medium | [LC 167](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) | Opposite pointers |
| 2 | 3Sum | Medium | [LC 15](https://leetcode.com/problems/3sum/) | Fixed + two pointer |
| 3 | Container With Most Water | Medium | [LC 11](https://leetcode.com/problems/container-with-most-water/) | Greedy two pointer |
| 4 | Trapping Rain Water | Hard | [LC 42](https://leetcode.com/problems/trapping-rain-water/) | Two pointer optimal |
| 5 | Remove Duplicates from Sorted Array II | Medium | [LC 80](https://leetcode.com/problems/remove-duplicates-from-sorted-array-ii/) | Fast/slow pointer |

#### Sliding Window Problems

| # | Problem | Difficulty | Link | Pattern |
|---|---------|------------|------|---------|
| 1 | Maximum Subarray | Medium | [LC 53](https://leetcode.com/problems/maximum-subarray/) | Kadane's algorithm |
| 2 | Longest Substring Without Repeating Characters | Medium | [LC 3](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | Variable window |
| 3 | Minimum Window Substring | Hard | [LC 76](https://leetcode.com/problems/minimum-window-substring/) | Variable window + hashmap |
| 4 | Sliding Window Maximum | Hard | [LC 239](https://leetcode.com/problems/sliding-window-maximum/) | Monotonic deque |
| 5 | Longest Repeating Character Replacement | Medium | [LC 424](https://leetcode.com/problems/longest-repeating-character-replacement/) | Window + frequency |

#### Prefix Sum Problems

| # | Problem | Difficulty | Link | Pattern |
|---|---------|------------|------|---------|
| 1 | Subarray Sum Equals K | Medium | [LC 560](https://leetcode.com/problems/subarray-sum-equals-k/) | Prefix sum + hashmap |
| 2 | Product of Array Except Self | Medium | [LC 238](https://leetcode.com/problems/product-of-array-except-self/) | Prefix/suffix products |
| 3 | Continuous Subarray Sum | Medium | [LC 523](https://leetcode.com/problems/continuous-subarray-sum/) | Prefix sum modulo |

#### Matrix Problems

| # | Problem | Difficulty | Link | Pattern |
|---|---------|------------|------|---------|
| 1 | Spiral Matrix | Medium | [LC 54](https://leetcode.com/problems/spiral-matrix/) | Boundary tracking |
| 2 | Rotate Image | Medium | [LC 48](https://leetcode.com/problems/rotate-image/) | In-place rotation |
| 3 | Set Matrix Zeroes | Medium | [LC 73](https://leetcode.com/problems/set-matrix-zeroes/) | O(1) space trick |

---

### Day 5-6: Linked Lists

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Reverse Linked List | Easy | [LC 206](https://leetcode.com/problems/reverse-linked-list/) | Iterative & recursive |
| 2 | Linked List Cycle | Easy | [LC 141](https://leetcode.com/problems/linked-list-cycle/) | Floyd's algorithm |
| 3 | Linked List Cycle II | Medium | [LC 142](https://leetcode.com/problems/linked-list-cycle-ii/) | Find cycle start |
| 4 | Middle of the Linked List | Easy | [LC 876](https://leetcode.com/problems/middle-of-the-linked-list/) | Fast/slow pointer |
| 5 | Remove Nth Node From End | Medium | [LC 19](https://leetcode.com/problems/remove-nth-node-from-end-of-list/) | Two pointer gap |
| 6 | Merge Two Sorted Lists | Easy | [LC 21](https://leetcode.com/problems/merge-two-sorted-lists/) | Merge pattern |
| 7 | Merge K Sorted Lists | Hard | [LC 23](https://leetcode.com/problems/merge-k-sorted-lists/) | Heap/divide&conquer |
| 8 | Reverse Nodes in k-Group | Hard | [LC 25](https://leetcode.com/problems/reverse-nodes-in-k-group/) | Reverse in groups |
| 9 | Copy List with Random Pointer | Medium | [LC 138](https://leetcode.com/problems/copy-list-with-random-pointer/) | HashMap cloning |
| 10 | LRU Cache | Medium | [LC 146](https://leetcode.com/problems/lru-cache/) | DLL + HashMap |

---

### Day 7: Stack & Queue

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Valid Parentheses | Easy | [LC 20](https://leetcode.com/problems/valid-parentheses/) | Stack basics |
| 2 | Min Stack | Medium | [LC 155](https://leetcode.com/problems/min-stack/) | Auxiliary stack |
| 3 | Daily Temperatures | Medium | [LC 739](https://leetcode.com/problems/daily-temperatures/) | Monotonic stack |
| 4 | Next Greater Element I | Easy | [LC 496](https://leetcode.com/problems/next-greater-element-i/) | Monotonic stack |
| 5 | Next Greater Element II | Medium | [LC 503](https://leetcode.com/problems/next-greater-element-ii/) | Circular array |
| 6 | Largest Rectangle in Histogram | Hard | [LC 84](https://leetcode.com/problems/largest-rectangle-in-histogram/) | Monotonic stack |
| 7 | Implement Queue using Stacks | Easy | [LC 232](https://leetcode.com/problems/implement-queue-using-stacks/) | Amortized O(1) |
| 8 | Implement Stack using Queues | Easy | [LC 225](https://leetcode.com/problems/implement-stack-using-queues/) | Queue manipulation |
| 9 | Basic Calculator | Hard | [LC 224](https://leetcode.com/problems/basic-calculator/) | Expression parsing |
| 10 | Evaluate Reverse Polish Notation | Medium | [LC 150](https://leetcode.com/problems/evaluate-reverse-polish-notation/) | Stack evaluation |

---

## Week 2: Core Structures

### Day 8-9: Hashing

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Two Sum | Easy | [LC 1](https://leetcode.com/problems/two-sum/) | Basic hashmap |
| 2 | Group Anagrams | Medium | [LC 49](https://leetcode.com/problems/group-anagrams/) | Custom hash key |
| 3 | Top K Frequent Elements | Medium | [LC 347](https://leetcode.com/problems/top-k-frequent-elements/) | Frequency map + heap |
| 4 | Longest Consecutive Sequence | Medium | [LC 128](https://leetcode.com/problems/longest-consecutive-sequence/) | HashSet O(n) |
| 5 | Valid Sudoku | Medium | [LC 36](https://leetcode.com/problems/valid-sudoku/) | Multiple hashsets |
| 6 | Encode and Decode TinyURL | Medium | [LC 535](https://leetcode.com/problems/encode-and-decode-tinyurl/) | Hashing design |
| 7 | Design HashMap | Easy | [LC 706](https://leetcode.com/problems/design-hashmap/) | Implement from scratch |
| 8 | Design HashSet | Easy | [LC 705](https://leetcode.com/problems/design-hashset/) | Implement from scratch |
| 9 | First Unique Character | Easy | [LC 387](https://leetcode.com/problems/first-unique-character-in-a-string/) | Frequency counting |
| 10 | Subarray Sum Equals K | Medium | [LC 560](https://leetcode.com/problems/subarray-sum-equals-k/) | Prefix sum + hashmap |

---

### Day 10-12: Trees

#### BST Fundamentals

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Validate Binary Search Tree | Medium | [LC 98](https://leetcode.com/problems/validate-binary-search-tree/) | Inorder property |
| 2 | Inorder Successor in BST | Medium | [LC 285](https://leetcode.com/problems/inorder-successor-in-bst/) | BST traversal |
| 3 | Kth Smallest Element in BST | Medium | [LC 230](https://leetcode.com/problems/kth-smallest-element-in-a-bst/) | Inorder traversal |
| 4 | Convert Sorted Array to BST | Easy | [LC 108](https://leetcode.com/problems/convert-sorted-array-to-binary-search-tree/) | Divide and conquer |
| 5 | Delete Node in BST | Medium | [LC 450](https://leetcode.com/problems/delete-node-in-a-bst/) | BST deletion |

#### Binary Tree Traversals

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Binary Tree Inorder Traversal | Easy | [LC 94](https://leetcode.com/problems/binary-tree-inorder-traversal/) | Iterative traversal |
| 2 | Binary Tree Level Order Traversal | Medium | [LC 102](https://leetcode.com/problems/binary-tree-level-order-traversal/) | BFS |
| 3 | Binary Tree Zigzag Level Order | Medium | [LC 103](https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/) | Level + direction |
| 4 | Binary Tree Right Side View | Medium | [LC 199](https://leetcode.com/problems/binary-tree-right-side-view/) | Level order rightmost |

#### Tree Properties

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Maximum Depth of Binary Tree | Easy | [LC 104](https://leetcode.com/problems/maximum-depth-of-binary-tree/) | Recursion basics |
| 2 | Same Tree | Easy | [LC 100](https://leetcode.com/problems/same-tree/) | Tree comparison |
| 3 | Symmetric Tree | Easy | [LC 101](https://leetcode.com/problems/symmetric-tree/) | Mirror check |
| 4 | Diameter of Binary Tree | Easy | [LC 543](https://leetcode.com/problems/diameter-of-binary-tree/) | Height + diameter |
| 5 | Balanced Binary Tree | Easy | [LC 110](https://leetcode.com/problems/balanced-binary-tree/) | Height balance |
| 6 | Subtree of Another Tree | Easy | [LC 572](https://leetcode.com/problems/subtree-of-another-tree/) | Subtree matching |

#### Tree Construction & Manipulation

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Construct Binary Tree from Preorder and Inorder | Medium | [LC 105](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/) | Tree construction |
| 2 | Flatten Binary Tree to Linked List | Medium | [LC 114](https://leetcode.com/problems/flatten-binary-tree-to-linked-list/) | Preorder flattening |
| 3 | Serialize and Deserialize Binary Tree | Hard | [LC 297](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/) | Tree serialization |
| 4 | Lowest Common Ancestor of BST | Medium | [LC 235](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/) | BST property |
| 5 | Lowest Common Ancestor of Binary Tree | Medium | [LC 236](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/) | General tree LCA |
| 6 | Binary Tree Maximum Path Sum | Hard | [LC 124](https://leetcode.com/problems/binary-tree-maximum-path-sum/) | Path tracking |

---

### Day 13-14: Heaps / Priority Queue

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Kth Largest Element in Array | Medium | [LC 215](https://leetcode.com/problems/kth-largest-element-in-an-array/) | Min heap of size k |
| 2 | Top K Frequent Elements | Medium | [LC 347](https://leetcode.com/problems/top-k-frequent-elements/) | Heap + frequency |
| 3 | Find Median from Data Stream | Hard | [LC 295](https://leetcode.com/problems/find-median-from-data-stream/) | Two heaps |
| 4 | Merge K Sorted Lists | Hard | [LC 23](https://leetcode.com/problems/merge-k-sorted-lists/) | Min heap merge |
| 5 | Task Scheduler | Medium | [LC 621](https://leetcode.com/problems/task-scheduler/) | Greedy + heap |
| 6 | K Closest Points to Origin | Medium | [LC 973](https://leetcode.com/problems/k-closest-points-to-origin/) | Max heap |
| 7 | Sort Characters By Frequency | Medium | [LC 451](https://leetcode.com/problems/sort-characters-by-frequency/) | Heap sorting |
| 8 | Reorganize String | Medium | [LC 767](https://leetcode.com/problems/reorganize-string/) | Greedy + heap |
| 9 | Meeting Rooms II | Medium | [LC 253](https://leetcode.com/problems/meeting-rooms-ii/) | Min heap scheduling |
| 10 | Last Stone Weight | Easy | [LC 1046](https://leetcode.com/problems/last-stone-weight/) | Max heap |

---

## Week 3: Graphs & Advanced Algorithms

### Day 15-17: Graph Theory

#### BFS/DFS Fundamentals

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Number of Islands | Medium | [LC 200](https://leetcode.com/problems/number-of-islands/) | Grid DFS/BFS |
| 2 | Clone Graph | Medium | [LC 133](https://leetcode.com/problems/clone-graph/) | Graph cloning |
| 3 | Max Area of Island | Medium | [LC 695](https://leetcode.com/problems/max-area-of-island/) | DFS counting |
| 4 | Pacific Atlantic Water Flow | Medium | [LC 417](https://leetcode.com/problems/pacific-atlantic-water-flow/) | Multi-source BFS |
| 5 | Rotting Oranges | Medium | [LC 994](https://leetcode.com/problems/rotting-oranges/) | Multi-source BFS |

#### Topological Sort

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Course Schedule | Medium | [LC 207](https://leetcode.com/problems/course-schedule/) | Cycle detection |
| 2 | Course Schedule II | Medium | [LC 210](https://leetcode.com/problems/course-schedule-ii/) | Topological order |
| 3 | Alien Dictionary | Hard | [LC 269](https://leetcode.com/problems/alien-dictionary/) | Build graph + topsort |
| 4 | Minimum Height Trees | Medium | [LC 310](https://leetcode.com/problems/minimum-height-trees/) | Tree + topsort |

#### Shortest Path

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Network Delay Time | Medium | [LC 743](https://leetcode.com/problems/network-delay-time/) | Dijkstra's |
| 2 | Cheapest Flights Within K Stops | Medium | [LC 787](https://leetcode.com/problems/cheapest-flights-within-k-stops/) | BFS/Bellman-Ford |
| 3 | Path With Minimum Effort | Medium | [LC 1631](https://leetcode.com/problems/path-with-minimum-effort/) | Binary search + BFS |
| 4 | Swim in Rising Water | Hard | [LC 778](https://leetcode.com/problems/swim-in-rising-water/) | Dijkstra variant |

#### Union Find

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Number of Provinces | Medium | [LC 547](https://leetcode.com/problems/number-of-provinces/) | Connected components |
| 2 | Redundant Connection | Medium | [LC 684](https://leetcode.com/problems/redundant-connection/) | Cycle detection |
| 3 | Accounts Merge | Medium | [LC 721](https://leetcode.com/problems/accounts-merge/) | Union find + DFS |
| 4 | Graph Valid Tree | Medium | [LC 261](https://leetcode.com/problems/graph-valid-tree/) | Tree validation |

#### Advanced Graph

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Word Ladder | Hard | [LC 127](https://leetcode.com/problems/word-ladder/) | BFS shortest path |
| 2 | Word Ladder II | Hard | [LC 126](https://leetcode.com/problems/word-ladder-ii/) | BFS + backtracking |
| 3 | Critical Connections | Hard | [LC 1192](https://leetcode.com/problems/critical-connections-in-a-network/) | Tarjan's algorithm |
| 4 | Reconstruct Itinerary | Hard | [LC 332](https://leetcode.com/problems/reconstruct-itinerary/) | Eulerian path |

---

### Day 18-19: Dynamic Programming

#### 1D DP

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Climbing Stairs | Easy | [LC 70](https://leetcode.com/problems/climbing-stairs/) | Fibonacci pattern |
| 2 | House Robber | Medium | [LC 198](https://leetcode.com/problems/house-robber/) | Include/exclude |
| 3 | House Robber II | Medium | [LC 213](https://leetcode.com/problems/house-robber-ii/) | Circular array |
| 4 | Coin Change | Medium | [LC 322](https://leetcode.com/problems/coin-change/) | Unbounded knapsack |
| 5 | Coin Change II | Medium | [LC 518](https://leetcode.com/problems/coin-change-ii/) | Counting combinations |
| 6 | Longest Increasing Subsequence | Medium | [LC 300](https://leetcode.com/problems/longest-increasing-subsequence/) | LIS pattern |
| 7 | Word Break | Medium | [LC 139](https://leetcode.com/problems/word-break/) | Prefix matching |
| 8 | Decode Ways | Medium | [LC 91](https://leetcode.com/problems/decode-ways/) | Two-choice DP |

#### 2D DP

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Unique Paths | Medium | [LC 62](https://leetcode.com/problems/unique-paths/) | Grid DP |
| 2 | Unique Paths II | Medium | [LC 63](https://leetcode.com/problems/unique-paths-ii/) | With obstacles |
| 3 | Minimum Path Sum | Medium | [LC 64](https://leetcode.com/problems/minimum-path-sum/) | Grid min path |
| 4 | Edit Distance | Hard | [LC 72](https://leetcode.com/problems/edit-distance/) | String DP classic |
| 5 | Longest Common Subsequence | Medium | [LC 1143](https://leetcode.com/problems/longest-common-subsequence/) | LCS pattern |
| 6 | Longest Palindromic Substring | Medium | [LC 5](https://leetcode.com/problems/longest-palindromic-substring/) | Expand around center |
| 7 | Palindromic Substrings | Medium | [LC 647](https://leetcode.com/problems/palindromic-substrings/) | Count palindromes |

#### Advanced DP

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Target Sum | Medium | [LC 494](https://leetcode.com/problems/target-sum/) | 0/1 Knapsack |
| 2 | Partition Equal Subset Sum | Medium | [LC 416](https://leetcode.com/problems/partition-equal-subset-sum/) | Subset sum |
| 3 | Burst Balloons | Hard | [LC 312](https://leetcode.com/problems/burst-balloons/) | Interval DP |
| 4 | Regular Expression Matching | Hard | [LC 10](https://leetcode.com/problems/regular-expression-matching/) | Pattern matching |
| 5 | Word Break II | Hard | [LC 140](https://leetcode.com/problems/word-break-ii/) | DP + backtracking |

---

### Day 20-21: Greedy & Backtracking

#### Greedy

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Jump Game | Medium | [LC 55](https://leetcode.com/problems/jump-game/) | Greedy reach |
| 2 | Jump Game II | Medium | [LC 45](https://leetcode.com/problems/jump-game-ii/) | BFS/Greedy |
| 3 | Gas Station | Medium | [LC 134](https://leetcode.com/problems/gas-station/) | Circuit sum |
| 4 | Meeting Rooms II | Medium | [LC 253](https://leetcode.com/problems/meeting-rooms-ii/) | Interval scheduling |
| 5 | Non-overlapping Intervals | Medium | [LC 435](https://leetcode.com/problems/non-overlapping-intervals/) | Activity selection |
| 6 | Merge Intervals | Medium | [LC 56](https://leetcode.com/problems/merge-intervals/) | Interval merge |
| 7 | Insert Interval | Medium | [LC 57](https://leetcode.com/problems/insert-interval/) | Interval insertion |

#### Backtracking

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Subsets | Medium | [LC 78](https://leetcode.com/problems/subsets/) | Power set |
| 2 | Subsets II | Medium | [LC 90](https://leetcode.com/problems/subsets-ii/) | Skip duplicates |
| 3 | Permutations | Medium | [LC 46](https://leetcode.com/problems/permutations/) | Permutation pattern |
| 4 | Permutations II | Medium | [LC 47](https://leetcode.com/problems/permutations-ii/) | Skip duplicates |
| 5 | Combination Sum | Medium | [LC 39](https://leetcode.com/problems/combination-sum/) | Unlimited picks |
| 6 | Combination Sum II | Medium | [LC 40](https://leetcode.com/problems/combination-sum-ii/) | Single picks |
| 7 | Letter Combinations of Phone | Medium | [LC 17](https://leetcode.com/problems/letter-combinations-of-a-phone-number/) | Digit mapping |
| 8 | N-Queens | Hard | [LC 51](https://leetcode.com/problems/n-queens/) | Constraint backtrack |
| 9 | Sudoku Solver | Hard | [LC 37](https://leetcode.com/problems/sudoku-solver/) | Cell-by-cell |
| 10 | Word Search | Medium | [LC 79](https://leetcode.com/problems/word-search/) | Grid backtracking |

---

## Week 4: Senior-Level Engineering DSA

### Day 22-23: Tries & Advanced Trees

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Implement Trie | Medium | [LC 208](https://leetcode.com/problems/implement-trie-prefix-tree/) | Trie basics |
| 2 | Design Add and Search Words | Medium | [LC 211](https://leetcode.com/problems/design-add-and-search-words-data-structure/) | Trie + wildcard |
| 3 | Word Search II | Hard | [LC 212](https://leetcode.com/problems/word-search-ii/) | Trie + backtracking |
| 4 | Design Search Autocomplete | Hard | [LC 642](https://leetcode.com/problems/design-search-autocomplete-system/) | Trie + ranking |
| 5 | Palindrome Pairs | Hard | [LC 336](https://leetcode.com/problems/palindrome-pairs/) | Trie + palindrome |
| 6 | Range Sum Query - Mutable | Medium | [LC 307](https://leetcode.com/problems/range-sum-query-mutable/) | Segment tree |
| 7 | Count of Range Sum | Hard | [LC 327](https://leetcode.com/problems/count-of-range-sum/) | Segment tree/merge sort |

---

### Day 24-25: Advanced Data Structures & Design

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | LRU Cache | Medium | [LC 146](https://leetcode.com/problems/lru-cache/) | DLL + HashMap |
| 2 | LFU Cache | Hard | [LC 460](https://leetcode.com/problems/lfu-cache/) | Multiple data structures |
| 3 | Design Twitter | Medium | [LC 355](https://leetcode.com/problems/design-twitter/) | OOP + heap |
| 4 | Design In-Memory File System | Hard | [LC 588](https://leetcode.com/problems/design-in-memory-file-system/) | Trie structure |
| 5 | All O`one Data Structure | Hard | [LC 432](https://leetcode.com/problems/all-oone-data-structure/) | DLL + HashMap |
| 6 | Insert Delete GetRandom O(1) | Medium | [LC 380](https://leetcode.com/problems/insert-delete-getrandom-o1/) | Array + HashMap |
| 7 | Time Based Key-Value Store | Medium | [LC 981](https://leetcode.com/problems/time-based-key-value-store/) | Binary search |
| 8 | Design Hit Counter | Medium | [LC 362](https://leetcode.com/problems/design-hit-counter/) | Queue/circular buffer |
| 9 | Design Leaderboard | Medium | [LC 1244](https://leetcode.com/problems/design-a-leaderboard/) | HashMap + sorting |

---

### Day 26-27: Concurrency & System Design

| # | Problem | Difficulty | Link | Key Concept |
|---|---------|------------|------|-------------|
| 1 | Design Bounded Blocking Queue | Medium | [LC 1188](https://leetcode.com/problems/design-bounded-blocking-queue/) | Producer-consumer |
| 2 | Print in Order | Easy | [LC 1114](https://leetcode.com/problems/print-in-order/) | Synchronization |
| 3 | Print FooBar Alternately | Medium | [LC 1115](https://leetcode.com/problems/print-foobar-alternately/) | Alternating sync |
| 4 | Building H2O | Medium | [LC 1117](https://leetcode.com/problems/building-h2o/) | Semaphore pattern |
| 5 | The Dining Philosophers | Medium | [LC 1226](https://leetcode.com/problems/the-dining-philosophers/) | Deadlock avoidance |
| 6 | Design Rate Limiter | - | Practice Problem | Token bucket/sliding window |
| 7 | Design Distributed Cache | - | Practice Problem | Consistent hashing |

---

### Day 28: Pattern Revision Day

**Solve 2 problems from each category:**

| Category | Problem 1 | Problem 2 |
|----------|-----------|-----------|
| Two Pointer | [LC 11](https://leetcode.com/problems/container-with-most-water/) | [LC 42](https://leetcode.com/problems/trapping-rain-water/) |
| Sliding Window | [LC 3](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | [LC 76](https://leetcode.com/problems/minimum-window-substring/) |
| Tree | [LC 236](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/) | [LC 297](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/) |
| Graph | [LC 200](https://leetcode.com/problems/number-of-islands/) | [LC 207](https://leetcode.com/problems/course-schedule/) |
| DP | [LC 322](https://leetcode.com/problems/coin-change/) | [LC 300](https://leetcode.com/problems/longest-increasing-subsequence/) |
| Heap | [LC 295](https://leetcode.com/problems/find-median-from-data-stream/) | [LC 23](https://leetcode.com/problems/merge-k-sorted-lists/) |
| Backtracking | [LC 78](https://leetcode.com/problems/subsets/) | [LC 51](https://leetcode.com/problems/n-queens/) |

---

### Day 29-30: Mock Interviews

#### Mock Interview Set 1 (Day 29)

| Time | Problem | Difficulty | Link |
|------|---------|------------|------|
| 0-20 min | LRU Cache | Medium | [LC 146](https://leetcode.com/problems/lru-cache/) |
| 20-45 min | Word Ladder | Hard | [LC 127](https://leetcode.com/problems/word-ladder/) |
| 45-90 min | Design Twitter | Medium | [LC 355](https://leetcode.com/problems/design-twitter/) |

#### Mock Interview Set 2 (Day 30)

| Time | Problem | Difficulty | Link |
|------|---------|------------|------|
| 0-20 min | Merge Intervals | Medium | [LC 56](https://leetcode.com/problems/merge-intervals/) |
| 20-45 min | Serialize/Deserialize Binary Tree | Hard | [LC 297](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/) |
| 45-90 min | Design Search Autocomplete | Hard | [LC 642](https://leetcode.com/problems/design-search-autocomplete-system/) |

---

## Summary: Problems by Pattern

### Quick Reference Card

| Pattern | Essential Problems |
|---------|-------------------|
| **Two Pointer** | 11, 15, 42, 167, 283 |
| **Sliding Window** | 3, 76, 239, 424, 567 |
| **Binary Search** | 33, 34, 74, 153, 162 |
| **BFS/DFS** | 200, 133, 207, 127, 417 |
| **Topological Sort** | 207, 210, 269, 310 |
| **Dynamic Programming** | 70, 198, 300, 322, 72 |
| **Backtracking** | 46, 78, 39, 51, 79 |
| **Heap** | 215, 295, 23, 347 |
| **Trie** | 208, 211, 212, 642 |
| **Union Find** | 200, 547, 684, 721 |
| **Stack** | 20, 155, 84, 739 |
| **Design** | 146, 460, 355, 380 |

---

## Daily Tracking Sheet

```
Day | Date | Problems Solved | Notes
----|------|-----------------|------
1   |      |                 |
2   |      |                 |
3   |      |                 |
... |      |                 |
30  |      |                 |
```

---

**Pro Tips:**
1. Solve problems without looking at solutions first
2. If stuck for 20 min, look at hints only
3. After solving, always check top solutions
4. Re-solve problems you struggled with after 3 days
5. Track patterns, not just problems

---

*Last Updated: February 2026*
