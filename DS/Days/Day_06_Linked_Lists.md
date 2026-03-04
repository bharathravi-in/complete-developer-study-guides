# 📚 DSA 30-Day Tutorial - Day 6

## Day 6: Linked Lists

### 🎯 Learning Objectives
By the end of this day, you will:
- Implement singly and doubly linked lists
- Master the fast/slow pointer technique
- Reverse linked lists iteratively and recursively
- Solve merge and intersection problems

---

### 📖 Linked List Basics

```javascript
// Node definition
class ListNode {
    constructor(val) {
        this.val = val;
        this.next = null;
    }
}

// Creating a linked list: 1 → 2 → 3
const head = new ListNode(1);
head.next = new ListNode(2);
head.next.next = new ListNode(3);
```

```
Visual:  [1] → [2] → [3] → null
         head
```

#### Traversal
```javascript
function printList(head) {
    let current = head;
    while (current !== null) {
        console.log(current.val);
        current = current.next;
    }
}
```

---

### 📖 Dummy Head Technique

A dummy/sentinel node simplifies edge cases (empty list, head changes).

```javascript
function insertAtBeginning(head, val) {
    const dummy = new ListNode(0);
    dummy.next = head;
    
    const newNode = new ListNode(val);
    newNode.next = dummy.next;
    dummy.next = newNode;
    
    return dummy.next;  // New head
}
```

---

### 📖 Fast & Slow Pointer (Floyd's Cycle Detection)

**Pattern:** Slow moves 1 step, fast moves 2 steps.

#### Detect Cycle
```javascript
function hasCycle(head) {
    let slow = head;
    let fast = head;
    
    while (fast !== null && fast.next !== null) {
        slow = slow.next;        // 1 step
        fast = fast.next.next;   // 2 steps
        
        if (slow === fast) {
            return true;  // Cycle detected!
        }
    }
    
    return false;  // No cycle
}
```

**Visualization:**
```
No cycle: 1 → 2 → 3 → null
          s→  s→  s
          f→→ f→→ (f=null, stop)

Cycle: 1 → 2 → 3 → 4
       ↑         ↓
       └─── 6 ← 5
       
Step 1: slow=1, fast=1
Step 2: slow=2, fast=3
Step 3: slow=3, fast=5
Step 4: slow=4, fast=3
Step 5: slow=5, fast=5 ← MEET!
```

#### Find Cycle Start
```javascript
function detectCycle(head) {
    let slow = head;
    let fast = head;
    
    // Phase 1: Detect cycle
    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
        
        if (slow === fast) {
            // Phase 2: Find start
            slow = head;
            while (slow !== fast) {
                slow = slow.next;
                fast = fast.next;  // Both move 1 step now
            }
            return slow;  // Cycle start
        }
    }
    
    return null;
}
```

**Why does this work?**
```
Let:
- L = distance from head to cycle start
- C = cycle length
- X = distance from cycle start to meeting point

When they meet:
- Slow traveled: L + X
- Fast traveled: L + X + nC (n complete cycles)

Since fast travels 2x slow:
2(L + X) = L + X + nC
L + X = nC
L = nC - X = (n-1)C + (C - X)

So if we reset one pointer to head and move both at same speed,
they'll meet at cycle start after L steps!
```

#### Find Middle of List
```javascript
function findMiddle(head) {
    let slow = head;
    let fast = head;
    
    while (fast !== null && fast.next !== null) {
        slow = slow.next;
        fast = fast.next.next;
    }
    
    return slow;  // Middle node
}
```

---

### 📖 Reverse Linked List

#### Iterative (O(1) space)
```javascript
function reverseList(head) {
    let prev = null;
    let curr = head;
    
    while (curr !== null) {
        const next = curr.next;  // Save next
        curr.next = prev;        // Reverse pointer
        prev = curr;             // Move prev forward
        curr = next;             // Move curr forward
    }
    
    return prev;  // New head
}
```

**Visualization:**
```
Initial: null   1 → 2 → 3 → null
         prev  curr

Step 1:  null ← 1   2 → 3 → null
               prev curr

Step 2:  null ← 1 ← 2   3 → null
                   prev curr

Step 3:  null ← 1 ← 2 ← 3   null
                       prev curr

Return prev = 3
```

#### Recursive
```javascript
function reverseListRecursive(head) {
    // Base case: empty or single node
    if (head === null || head.next === null) {
        return head;
    }
    
    // Recursively reverse rest of list
    const newHead = reverseListRecursive(head.next);
    
    // Reverse current connection
    head.next.next = head;
    head.next = null;
    
    return newHead;
}
```

---

### 📖 Merge Two Sorted Lists

```javascript
function mergeTwoLists(l1, l2) {
    const dummy = new ListNode(0);
    let current = dummy;
    
    while (l1 !== null && l2 !== null) {
        if (l1.val <= l2.val) {
            current.next = l1;
            l1 = l1.next;
        } else {
            current.next = l2;
            l2 = l2.next;
        }
        current = current.next;
    }
    
    // Attach remaining nodes
    current.next = l1 !== null ? l1 : l2;
    
    return dummy.next;
}
```

---

### 📖 Reverse Nodes in K-Group

```javascript
function reverseKGroup(head, k) {
    const dummy = new ListNode(0);
    dummy.next = head;
    
    let groupPrev = dummy;
    
    while (true) {
        // Check if k nodes exist
        let kthNode = getKthNode(groupPrev, k);
        if (kthNode === null) break;
        
        let groupNext = kthNode.next;
        
        // Reverse the group
        let prev = kthNode.next;
        let curr = groupPrev.next;
        
        while (curr !== groupNext) {
            const next = curr.next;
            curr.next = prev;
            prev = curr;
            curr = next;
        }
        
        // Connect with previous part
        const tmp = groupPrev.next;
        groupPrev.next = kthNode;
        groupPrev = tmp;
    }
    
    return dummy.next;
}

function getKthNode(curr, k) {
    while (curr !== null && k > 0) {
        curr = curr.next;
        k--;
    }
    return curr;
}
```

---

### ✅ Day 6 Checklist
- [ ] Implement linked list from scratch
- [ ] Master fast/slow pointer technique
- [ ] Reverse list iteratively and recursively
- [ ] Complete: Reverse Linked List, Merge Two Sorted Lists
- [ ] Practice: Linked List Cycle II, Reverse K-Group

---

