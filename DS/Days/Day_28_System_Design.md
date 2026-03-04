# 📚 DSA 30-Day Tutorial - Day 28

## Day 28: System Design Problems (LeetCode Style)

### 🎯 Learning Objectives
By the end of this day, you will:
- Design LRU Cache
- Design data structures for specific use cases
- Balance time/space tradeoffs

---

### 📖 LRU Cache

Least Recently Used - evict least recently accessed item when cache is full.

```javascript
class LRUCache {
    constructor(capacity) {
        this.capacity = capacity;
        this.cache = new Map();  // Map maintains insertion order
    }
    
    get(key) {
        if (!this.cache.has(key)) return -1;
        
        // Move to end (most recent)
        const value = this.cache.get(key);
        this.cache.delete(key);
        this.cache.set(key, value);
        
        return value;
    }
    
    put(key, value) {
        // If exists, delete first to update position
        if (this.cache.has(key)) {
            this.cache.delete(key);
        }
        
        this.cache.set(key, value);
        
        // Evict LRU if over capacity
        if (this.cache.size > this.capacity) {
            // Map.keys().next() gives the first (oldest) key
            const lruKey = this.cache.keys().next().value;
            this.cache.delete(lruKey);
        }
    }
}
```

**With Doubly Linked List (O(1) operations):**
```javascript
class DLLNode {
    constructor(key, val) {
        this.key = key;
        this.val = val;
        this.prev = null;
        this.next = null;
    }
}

class LRUCacheOptimal {
    constructor(capacity) {
        this.capacity = capacity;
        this.cache = new Map();  // key → node
        
        // Dummy head and tail
        this.head = new DLLNode(0, 0);
        this.tail = new DLLNode(0, 0);
        this.head.next = this.tail;
        this.tail.prev = this.head;
    }
    
    _remove(node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }
    
    _addToEnd(node) {
        node.prev = this.tail.prev;
        node.next = this.tail;
        this.tail.prev.next = node;
        this.tail.prev = node;
    }
    
    get(key) {
        if (!this.cache.has(key)) return -1;
        
        const node = this.cache.get(key);
        this._remove(node);
        this._addToEnd(node);
        
        return node.val;
    }
    
    put(key, value) {
        if (this.cache.has(key)) {
            const node = this.cache.get(key);
            node.val = value;
            this._remove(node);
            this._addToEnd(node);
        } else {
            const node = new DLLNode(key, value);
            this.cache.set(key, node);
            this._addToEnd(node);
            
            if (this.cache.size > this.capacity) {
                const lru = this.head.next;
                this._remove(lru);
                this.cache.delete(lru.key);
            }
        }
    }
}
```

---

### 📖 LFU Cache

Least Frequently Used - evict least frequently used item.

```javascript
class LFUCache {
    constructor(capacity) {
        this.capacity = capacity;
        this.cache = new Map();      // key → {value, freq}
        this.freqMap = new Map();    // freq → Set of keys (in order)
        this.minFreq = 0;
    }
    
    _updateFreq(key) {
        const { value, freq } = this.cache.get(key);
        
        // Remove from current frequency list
        this.freqMap.get(freq).delete(key);
        if (this.freqMap.get(freq).size === 0) {
            this.freqMap.delete(freq);
            if (this.minFreq === freq) this.minFreq++;
        }
        
        // Add to next frequency list
        const newFreq = freq + 1;
        if (!this.freqMap.has(newFreq)) {
            this.freqMap.set(newFreq, new Set());
        }
        this.freqMap.get(newFreq).add(key);
        
        this.cache.set(key, { value, freq: newFreq });
    }
    
    get(key) {
        if (!this.cache.has(key)) return -1;
        
        this._updateFreq(key);
        return this.cache.get(key).value;
    }
    
    put(key, value) {
        if (this.capacity === 0) return;
        
        if (this.cache.has(key)) {
            this.cache.get(key).value = value;
            this._updateFreq(key);
        } else {
            if (this.cache.size >= this.capacity) {
                // Evict LFU item
                const lfuKeys = this.freqMap.get(this.minFreq);
                const evictKey = lfuKeys.values().next().value;
                lfuKeys.delete(evictKey);
                this.cache.delete(evictKey);
            }
            
            this.cache.set(key, { value, freq: 1 });
            if (!this.freqMap.has(1)) this.freqMap.set(1, new Set());
            this.freqMap.get(1).add(key);
            this.minFreq = 1;
        }
    }
}
```

---

### 📖 Time Based Key-Value Store

```javascript
class TimeMap {
    constructor() {
        this.store = new Map();  // key → [[timestamp, value], ...]
    }
    
    set(key, value, timestamp) {
        if (!this.store.has(key)) {
            this.store.set(key, []);
        }
        this.store.get(key).push([timestamp, value]);
    }
    
    get(key, timestamp) {
        if (!this.store.has(key)) return '';
        
        const values = this.store.get(key);
        
        // Binary search for largest timestamp <= target
        let left = 0, right = values.length - 1;
        let result = '';
        
        while (left <= right) {
            const mid = Math.floor((left + right) / 2);
            if (values[mid][0] <= timestamp) {
                result = values[mid][1];
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        
        return result;
    }
}
```

---

### ✅ Day 28 Checklist
- [ ] Implement LRU Cache
- [ ] Understand LFU Cache
- [ ] Complete: Time Based Key-Value Store
- [ ] Practice: Design Twitter, Design HashSet

---

# 🗓️ WEEK 5: Mock Interviews & Review

---

