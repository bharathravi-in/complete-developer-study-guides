# FAANG-Level Mock Interview Scripts
## Senior Engineer (8+ Years Experience)

---

## Overview

These scripts simulate real senior-level interviews at top tech companies. Each mock includes:
- **Behavioral warm-up** (5 min)
- **Technical problem** (35-40 min)
- **Follow-up questions** (10-15 min)
- **Your questions** (5 min)

---

## Mock Interview 1: Meta/Facebook Style

### Company Context
- Focus: System design thinking + clean code
- Values: Impact, collaboration, move fast
- Interview style: Coding + design in one session

---

### Warm-up (5 minutes)

**Interviewer:** "Welcome! Before we dive into coding, tell me about a challenging technical problem you solved recently that had significant impact."

**What they're assessing:**
- Communication clarity
- Impact quantification
- Technical depth

**Ideal response structure:**
1. Context (10 sec): Team, product, scale
2. Problem (20 sec): What was broken/needed
3. Action (30 sec): Your specific contribution
4. Result (20 sec): Measurable impact

**Sample response:**
> "At my current company, our API response times degraded as we scaled to 2M daily users. I identified that our caching layer was causing N+1 query patterns. I redesigned the cache invalidation strategy using event sourcing, reducing p99 latency from 800ms to 120ms and database load by 60%."

---

### Technical Problem: Design an In-Memory Rate Limiter

**Problem Statement:**

"Design and implement a rate limiter that:
1. Limits requests per user to N requests per minute
2. Must be O(1) for checking if a request is allowed
3. Should be memory efficient for millions of users
4. Handle edge cases gracefully"

---

#### Phase 1: Clarifying Questions (5 min)

**You should ask:**

1. "What's the expected QPS and number of unique users?"
   - *Interviewer:* "1M users, 10K QPS peak"

2. "Should this be distributed across multiple servers?"
   - *Interviewer:* "Start with single server, then discuss distribution"

3. "What should happen when rate limited - return error or queue?"
   - *Interviewer:* "Return 429 with retry-after header"

4. "Any specific algorithm preference - token bucket, sliding window?"
   - *Interviewer:* "You choose, explain tradeoffs"

---

#### Phase 2: Approach Discussion (5 min)

**Your response:**

"I'll compare three approaches:

**1. Fixed Window Counter**
- Simple: count requests per minute
- Problem: burst at window boundaries (2x allowed rate)

**2. Sliding Window Log**
- Store timestamp of each request
- Accurate but O(n) space per user

**3. Sliding Window Counter (Recommended)**
- Hybrid approach
- Previous window count + current window count weighted by overlap
- O(1) time and space

Let me implement the sliding window counter as it balances accuracy and efficiency."

---

#### Phase 3: Implementation (20 min)

```javascript
class RateLimiter {
    constructor(maxRequests, windowSizeMs) {
        this.maxRequests = maxRequests;
        this.windowSize = windowSizeMs;
        this.windows = new Map(); // userId -> { prevCount, currCount, windowStart }
    }
    
    isAllowed(userId) {
        const now = Date.now();
        const currentWindow = Math.floor(now / this.windowSize);
        
        if (!this.windows.has(userId)) {
            this.windows.set(userId, {
                prevCount: 0,
                currCount: 1,
                windowStart: currentWindow
            });
            return true;
        }
        
        const user = this.windows.get(userId);
        
        // Check if we're in a new window
        if (currentWindow > user.windowStart) {
            // Slide the window
            if (currentWindow === user.windowStart + 1) {
                user.prevCount = user.currCount;
            } else {
                user.prevCount = 0; // Multiple windows passed
            }
            user.currCount = 0;
            user.windowStart = currentWindow;
        }
        
        // Calculate weighted count
        const elapsedInCurrentWindow = now - (currentWindow * this.windowSize);
        const weight = 1 - (elapsedInCurrentWindow / this.windowSize);
        const count = user.prevCount * weight + user.currCount;
        
        if (count >= this.maxRequests) {
            return false;
        }
        
        user.currCount++;
        return true;
    }
    
    // Memory cleanup for inactive users
    cleanup(inactiveThresholdMs) {
        const threshold = Date.now() - inactiveThresholdMs;
        for (const [userId, data] of this.windows) {
            if (data.windowStart * this.windowSize < threshold) {
                this.windows.delete(userId);
            }
        }
    }
}

// Express middleware usage
function rateLimiterMiddleware(limiter) {
    return (req, res, next) => {
        const userId = req.ip; // or req.user.id for authenticated users
        
        if (limiter.isAllowed(userId)) {
            next();
        } else {
            res.status(429).json({
                error: 'Rate limit exceeded',
                retryAfter: Math.ceil(limiter.windowSize / 1000)
            });
        }
    };
}
```

---

#### Phase 4: Follow-up Questions (10 min)

**Interviewer:** "How would you scale this to multiple servers?"

**Your response:**
"Three approaches:

1. **Sticky Sessions**
   - Route same user to same server
   - Simple but poor load balancing

2. **Centralized Store (Redis)**
   - Use Redis with Lua scripts for atomicity
   - Shared state, slight latency overhead

3. **Distributed Approach**
   - Each server has local limiter with fraction of limit
   - Use gossip protocol for synchronization
   - Eventually consistent but scalable

For most cases, I'd recommend Redis with the sliding window algorithm using MULTI/EXEC for atomicity."

**Interviewer:** "What about memory for millions of users?"

**Your response:**
"Each user entry is ~32 bytes. For 10M users, that's ~320MB. But most users are inactive. I'd implement:

1. LRU eviction when memory exceeds threshold
2. Background job to clean up inactive users
3. For massive scale, shard by user ID hash across Redis nodes"

---

### Evaluation Criteria (What They're Scoring)

| Criterion | Weight | Look For |
|-----------|--------|----------|
| Problem Solving | 25% | Clarifying questions, approach comparison |
| Coding | 25% | Clean code, handles edge cases |
| Communication | 20% | Explains thinking, asks for feedback |
| Technical Depth | 20% | Complexity analysis, tradeoffs |
| System Thinking | 10% | Scalability, production concerns |

---

## Mock Interview 2: Google Style

### Company Context
- Focus: Algorithm efficiency + rigorous analysis
- Values: Technical excellence, scale thinking
- Interview style: Pure algorithms with complexity analysis

---

### Warm-up (5 minutes)

**Interviewer:** "Tell me about a situation where you had to make a difficult technical decision with incomplete information."

**Sample response:**
> "We needed to choose between PostgreSQL and DynamoDB for a new service with unclear read/write patterns. With limited data, I proposed a hybrid: PostgreSQL for complex queries with event streaming to DynamoDB for high-scale reads. This let us validate assumptions before committing fully. Six months in, we had data showing 95% of queries were simple key lookups, so we migrated fully to DynamoDB, reducing costs by 40%."

---

### Technical Problem: Design Autocomplete System

**Problem Statement:**

"Design and implement an autocomplete system that:
1. Returns top K suggestions for a given prefix
2. Suggestions are ranked by frequency/relevance
3. Must handle 100M queries per day
4. System learns from new searches"

---

#### Phase 1: Clarifying Questions (5 min)

1. "How many unique terms in the corpus?"
   - *Interviewer:* "About 10 million terms"

2. "Are we ranking by frequency only, or personalization too?"
   - *Interviewer:* "Start with frequency, discuss personalization"

3. "What's acceptable latency?"
   - *Interviewer:* "p99 under 50ms"

4. "How fresh should suggestions be?"
   - *Interviewer:* "New trending terms within 1 hour"

---

#### Phase 2: High-Level Design (5 min)

**Your response:**

"I'll design this in layers:

1. **Data Layer:** Trie for prefix matching
2. **Ranking Layer:** Min-heap for top-K
3. **Caching Layer:** Precompute popular prefixes
4. **Update Layer:** Async processing of new searches

Let me implement the core Trie with top-K functionality."

---

#### Phase 3: Implementation (25 min)

```javascript
class TrieNode {
    constructor() {
        this.children = new Map();
        this.isEnd = false;
        this.frequency = 0;
        this.topSuggestions = []; // Pre-computed top K for this prefix
    }
}

class AutocompleteSystem {
    constructor(sentences, frequencies, k = 5) {
        this.root = new TrieNode();
        this.k = k;
        this.currentInput = '';
        this.currentNode = this.root;
        
        // Build trie with initial data
        for (let i = 0; i < sentences.length; i++) {
            this.addSentence(sentences[i], frequencies[i]);
        }
        
        // Pre-compute top suggestions for all prefixes
        this.precomputeTopSuggestions(this.root, '');
    }
    
    addSentence(sentence, frequency) {
        let node = this.root;
        
        for (const char of sentence) {
            if (!node.children.has(char)) {
                node.children.set(char, new TrieNode());
            }
            node = node.children.get(char);
        }
        
        node.isEnd = true;
        node.frequency += frequency;
    }
    
    precomputeTopSuggestions(node, prefix) {
        // Collect all sentences under this node
        const sentences = [];
        this.collectSentences(node, prefix, sentences);
        
        // Sort by frequency (desc) and take top K
        sentences.sort((a, b) => b.frequency - a.frequency);
        node.topSuggestions = sentences.slice(0, this.k);
        
        // Recursively precompute for children
        for (const [char, child] of node.children) {
            this.precomputeTopSuggestions(child, prefix + char);
        }
    }
    
    collectSentences(node, prefix, result) {
        if (node.isEnd) {
            result.push({ sentence: prefix, frequency: node.frequency });
        }
        
        for (const [char, child] of node.children) {
            this.collectSentences(child, prefix + char, result);
        }
    }
    
    // Called for each character input
    input(c) {
        if (c === '#') {
            // User submitted - learn from this search
            this.addSentence(this.currentInput, 1);
            this.updateTopSuggestions(this.currentInput);
            this.currentInput = '';
            this.currentNode = this.root;
            return [];
        }
        
        this.currentInput += c;
        
        // Navigate to next node
        if (this.currentNode && this.currentNode.children.has(c)) {
            this.currentNode = this.currentNode.children.get(c);
            return this.currentNode.topSuggestions.map(s => s.sentence);
        }
        
        // Prefix not found
        this.currentNode = null;
        return [];
    }
    
    updateTopSuggestions(sentence) {
        // Update path from root to sentence
        let node = this.root;
        let prefix = '';
        
        for (const char of sentence) {
            if (!node.children.has(char)) return;
            
            node = node.children.get(char);
            prefix += char;
            
            // Update top suggestions for this prefix
            this.updateNodeTopK(node, sentence);
        }
    }
    
    updateNodeTopK(node, sentence) {
        // Find the sentence node to get updated frequency
        let sentenceNode = this.root;
        for (const char of sentence) {
            sentenceNode = sentenceNode.children.get(char);
        }
        
        const newFreq = sentenceNode.frequency;
        
        // Check if sentence is already in top K
        const existingIndex = node.topSuggestions.findIndex(
            s => s.sentence === sentence
        );
        
        if (existingIndex !== -1) {
            node.topSuggestions[existingIndex].frequency = newFreq;
        } else if (node.topSuggestions.length < this.k || 
                   newFreq > node.topSuggestions[this.k - 1].frequency) {
            node.topSuggestions.push({ sentence, frequency: newFreq });
        }
        
        // Re-sort and trim to K
        node.topSuggestions.sort((a, b) => b.frequency - a.frequency);
        node.topSuggestions = node.topSuggestions.slice(0, this.k);
    }
}

// Optimized version with Min-Heap for top-K
class MinHeap {
    constructor(compareFn) {
        this.heap = [];
        this.compare = compareFn;
    }
    
    push(val) {
        this.heap.push(val);
        this.bubbleUp(this.heap.length - 1);
    }
    
    pop() {
        if (this.heap.length === 0) return null;
        const min = this.heap[0];
        const last = this.heap.pop();
        if (this.heap.length > 0) {
            this.heap[0] = last;
            this.bubbleDown(0);
        }
        return min;
    }
    
    peek() { return this.heap[0]; }
    size() { return this.heap.length; }
    
    bubbleUp(i) {
        while (i > 0) {
            const parent = Math.floor((i - 1) / 2);
            if (this.compare(this.heap[parent], this.heap[i]) <= 0) break;
            [this.heap[parent], this.heap[i]] = [this.heap[i], this.heap[parent]];
            i = parent;
        }
    }
    
    bubbleDown(i) {
        while (true) {
            let smallest = i;
            const left = 2 * i + 1, right = 2 * i + 2;
            if (left < this.heap.length && 
                this.compare(this.heap[left], this.heap[smallest]) < 0) {
                smallest = left;
            }
            if (right < this.heap.length && 
                this.compare(this.heap[right], this.heap[smallest]) < 0) {
                smallest = right;
            }
            if (smallest === i) break;
            [this.heap[smallest], this.heap[i]] = [this.heap[i], this.heap[smallest]];
            i = smallest;
        }
    }
}
```

---

#### Phase 4: Complexity Analysis

**Your explanation:**

"Let me analyze the complexities:

**Time Complexity:**
- `input(char)`: O(1) - Just traverse one edge and return precomputed list
- `addSentence`: O(L) where L = sentence length
- `precompute`: O(N * L * K log K) - done once at startup

**Space Complexity:**
- Trie: O(N * L) for N sentences of average length L
- Top-K lists: O(N * K) at most
- Total: O(N * L + N * K) = O(N * L) since typically L > K

**For 10M terms with average 20 characters:**
- ~200MB for trie structure
- Fits comfortably in memory"

---

#### Phase 5: Follow-up Questions (10 min)

**Interviewer:** "How would you handle personalization?"

**Your response:**
"I'd layer personalization on top:

1. **User Profile:** Store user's search history
2. **Blended Ranking:** 
   ```
   score = 0.7 * global_frequency + 0.3 * user_frequency
   ```
3. **Storage:** Keep user-specific top-K in Redis/cache
4. **Real-time:** Use Kafka for streaming user events"

**Interviewer:** "How to handle 100M queries/day?"

**Your response:**
"100M/day = ~1200 QPS average, ~5000 QPS peak.

1. **Caching:** Cache top 10K prefixes (covers 80% of queries)
2. **CDN:** Edge caching for common prefixes
3. **Sharding:** Shard tries by first character
4. **Read Replicas:** 3-5 replicas per shard

Architecture:
```
User → CDN → Load Balancer → Autocomplete Servers (sharded)
                                    ↓
                              Redis Cache
                                    ↓
                              Trie Replicas
```"

---

## Mock Interview 3: Amazon Style

### Company Context
- Focus: Leadership principles + scalable systems
- Values: Customer obsession, ownership, bias for action
- Interview style: Behavioral + technical + LP deep dives

---

### Warm-up: Leadership Principle Questions (10 minutes)

**Interviewer:** "Tell me about a time you had to deliver something with incomplete requirements."

**STAR Response:**

**Situation:** "Our team was tasked with building a fraud detection system for a new payment method launching in 3 weeks. Requirements were unclear because the product hadn't launched."

**Task:** "As the tech lead, I needed to deliver a working system without knowing exact fraud patterns."

**Action:** 
- "I designed a modular rule engine where rules could be added without code changes
- Created ML feature pipeline that could incorporate new signals quickly
- Set up A/B testing framework to validate rules safely
- Built dashboards for real-time monitoring"

**Result:** 
- "Launched on time with 5 basic rules
- Added 20 rules in first month based on real data
- Blocked $2M in fraudulent transactions in first quarter
- System became template for 3 other product launches"

---

### Technical Problem: Design an Order Processing System

**Problem Statement:**

"Design and implement the core logic for an order processing system that:
1. Validates orders against inventory
2. Handles concurrent orders for same item safely
3. Processes orders in priority order (Prime users first)
4. Must not oversell inventory"

---

#### Phase 1: Clarifying Questions (5 min)

1. "What's the scale - orders per second?"
   - *Interviewer:* "1000 orders/second peak"

2. "Are we handling payment, or just inventory allocation?"
   - *Interviewer:* "Just inventory allocation"

3. "Should partially fulfilled orders be allowed?"
   - *Interviewer:* "Yes, for some product categories"

4. "What's the SLA for order confirmation?"
   - *Interviewer:* "99% under 100ms"

---

#### Phase 2: Design Discussion (5 min)

"I'll design this with:

1. **Priority Queue** for order processing
2. **Optimistic Locking** for inventory updates
3. **Saga Pattern** for distributed inventory
4. **Event Sourcing** for audit trail

Let me implement the core with proper concurrency handling."

---

#### Phase 3: Implementation (25 min)

```javascript
// Priority Queue for Order Processing
class OrderPriorityQueue {
    constructor() {
        this.heap = [];
    }
    
    enqueue(order) {
        const priority = this.calculatePriority(order);
        this.heap.push({ order, priority });
        this.bubbleUp(this.heap.length - 1);
    }
    
    calculatePriority(order) {
        // Lower number = higher priority
        let priority = 1000;
        
        if (order.isPrime) priority -= 500;
        if (order.isFreshFood) priority -= 200;  // Perishables first
        priority -= Math.min(order.orderValue / 100, 100);  // Value bonus
        priority += (Date.now() - order.timestamp) / 1000;  // Age penalty
        
        return priority;
    }
    
    dequeue() {
        if (this.heap.length === 0) return null;
        const result = this.heap[0];
        const last = this.heap.pop();
        if (this.heap.length > 0) {
            this.heap[0] = last;
            this.bubbleDown(0);
        }
        return result.order;
    }
    
    bubbleUp(i) {
        while (i > 0) {
            const parent = Math.floor((i - 1) / 2);
            if (this.heap[parent].priority <= this.heap[i].priority) break;
            [this.heap[parent], this.heap[i]] = [this.heap[i], this.heap[parent]];
            i = parent;
        }
    }
    
    bubbleDown(i) {
        while (true) {
            let smallest = i;
            const left = 2 * i + 1, right = 2 * i + 2;
            if (left < this.heap.length && 
                this.heap[left].priority < this.heap[smallest].priority) {
                smallest = left;
            }
            if (right < this.heap.length && 
                this.heap[right].priority < this.heap[smallest].priority) {
                smallest = right;
            }
            if (smallest === i) break;
            [this.heap[smallest], this.heap[i]] = [this.heap[i], this.heap[smallest]];
            i = smallest;
        }
    }
    
    isEmpty() {
        return this.heap.length === 0;
    }
}

// Inventory Manager with Optimistic Locking
class InventoryManager {
    constructor() {
        this.inventory = new Map(); // productId -> { quantity, version }
        this.reservations = new Map(); // orderId -> [{ productId, quantity }]
    }
    
    initializeProduct(productId, quantity) {
        this.inventory.set(productId, { quantity, version: 0 });
    }
    
    // Reserve inventory with optimistic locking
    async reserve(orderId, items) {
        const reserved = [];
        
        try {
            for (const item of items) {
                const success = await this.reserveItem(
                    orderId, 
                    item.productId, 
                    item.quantity
                );
                
                if (success) {
                    reserved.push(item);
                } else {
                    // Partial fulfillment or rollback based on policy
                    throw new Error(`Insufficient inventory for ${item.productId}`);
                }
            }
            
            this.reservations.set(orderId, reserved);
            return { success: true, reserved };
            
        } catch (error) {
            // Rollback reserved items
            for (const item of reserved) {
                this.releaseItem(item.productId, item.quantity);
            }
            return { success: false, error: error.message };
        }
    }
    
    reserveItem(orderId, productId, quantity, maxRetries = 3) {
        for (let retry = 0; retry < maxRetries; retry++) {
            const product = this.inventory.get(productId);
            if (!product) return false;
            
            const { quantity: available, version } = product;
            
            if (available < quantity) return false;
            
            // Optimistic locking - check version hasn't changed
            const newVersion = version + 1;
            const updated = this.compareAndSwap(
                productId, 
                version, 
                { quantity: available - quantity, version: newVersion }
            );
            
            if (updated) return true;
            
            // Retry on version conflict
        }
        return false;
    }
    
    compareAndSwap(productId, expectedVersion, newValue) {
        const current = this.inventory.get(productId);
        if (current.version !== expectedVersion) return false;
        this.inventory.set(productId, newValue);
        return true;
    }
    
    releaseItem(productId, quantity) {
        const product = this.inventory.get(productId);
        if (product) {
            product.quantity += quantity;
            product.version++;
        }
    }
    
    confirmOrder(orderId) {
        // Remove from reservations, inventory is already deducted
        this.reservations.delete(orderId);
    }
    
    cancelOrder(orderId) {
        const reserved = this.reservations.get(orderId);
        if (reserved) {
            for (const item of reserved) {
                this.releaseItem(item.productId, item.quantity);
            }
            this.reservations.delete(orderId);
        }
    }
}

// Order Processor
class OrderProcessor {
    constructor() {
        this.queue = new OrderPriorityQueue();
        this.inventory = new InventoryManager();
        this.processing = false;
        this.results = new Map(); // orderId -> status
    }
    
    submitOrder(order) {
        order.timestamp = Date.now();
        order.status = 'pending';
        this.queue.enqueue(order);
        this.results.set(order.id, { status: 'queued' });
        
        // Start processing if not already running
        this.startProcessing();
        
        return order.id;
    }
    
    async startProcessing() {
        if (this.processing) return;
        this.processing = true;
        
        while (!this.queue.isEmpty()) {
            const order = this.queue.dequeue();
            await this.processOrder(order);
        }
        
        this.processing = false;
    }
    
    async processOrder(order) {
        const result = await this.inventory.reserve(order.id, order.items);
        
        if (result.success) {
            this.results.set(order.id, {
                status: 'confirmed',
                reserved: result.reserved,
                timestamp: Date.now()
            });
            
            // Emit event for downstream processing
            this.emitEvent('order.confirmed', order);
        } else {
            this.results.set(order.id, {
                status: 'failed',
                error: result.error,
                timestamp: Date.now()
            });
            
            this.emitEvent('order.failed', order);
        }
    }
    
    getOrderStatus(orderId) {
        return this.results.get(orderId);
    }
    
    emitEvent(type, order) {
        // Hook for event sourcing / downstream systems
        console.log(`Event: ${type}`, order.id);
    }
}

// Usage Example
const processor = new OrderProcessor();

// Initialize inventory
processor.inventory.initializeProduct('SKU001', 100);
processor.inventory.initializeProduct('SKU002', 50);

// Submit orders
const order1 = {
    id: 'ORD001',
    isPrime: true,
    items: [{ productId: 'SKU001', quantity: 2 }],
    orderValue: 150
};

const order2 = {
    id: 'ORD002',
    isPrime: false,
    items: [{ productId: 'SKU001', quantity: 1 }],
    orderValue: 75
};

processor.submitOrder(order1);  // Will be processed first (Prime)
processor.submitOrder(order2);
```

---

#### Phase 4: Follow-up Questions (10 min)

**Interviewer:** "How would you handle this across multiple warehouses?"

**Your response:**
"Distributed inventory requires:

1. **Inventory Sharding:** Shard by warehouse region
2. **Routing:** Route orders to nearest warehouse with stock
3. **Distributed Lock:** Use Redis locks or database row locks
4. **Saga Pattern:** 
   ```
   Reserve Warehouse A → Reserve Warehouse B → Confirm Both
                    ↓                     ↓
               Compensate           Compensate
   ```
5. **Eventual Consistency:** Accept slight oversell risk for better latency, handle via backorders"

**Interviewer:** "What about the audit trail for compliance?"

**Your response:**
"Event Sourcing architecture:

1. **Event Store:** Append-only log of all state changes
2. **Events:**
   - InventoryReserved
   - InventoryReleased  
   - OrderConfirmed
   - OrderCancelled
   
3. **Reconstruction:** Can rebuild state at any point
4. **Compliance:** Immutable audit trail for SOX/PCI
5. **Implementation:** Kafka or AWS EventBridge"

---

## Mock Interview 4: Apple/Netflix Style

### Company Context
- Focus: Elegant design + attention to detail
- Values: Quality over speed, user experience
- Interview style: Deep technical discussion, clean code

---

### Technical Problem: Design an LRU Cache with TTL

**Problem Statement:**

"Implement an LRU Cache that:
1. Has O(1) get and put operations
2. Supports TTL (time-to-live) for entries
3. Has efficient memory management
4. Handles concurrent access safely (bonus)"

---

#### Implementation

```javascript
class LRUCacheWithTTL {
    constructor(capacity, defaultTTL = Infinity) {
        this.capacity = capacity;
        this.defaultTTL = defaultTTL;
        this.cache = new Map();
        
        // Doubly linked list
        this.head = { key: null, prev: null, next: null };
        this.tail = { key: null, prev: null, next: null };
        this.head.next = this.tail;
        this.tail.prev = this.head;
        
        // Start cleanup timer
        this.startCleanup();
    }
    
    get(key) {
        if (!this.cache.has(key)) return -1;
        
        const node = this.cache.get(key);
        
        // Check if expired
        if (this.isExpired(node)) {
            this.remove(node);
            this.cache.delete(key);
            return -1;
        }
        
        // Move to front (most recently used)
        this.remove(node);
        this.addToFront(node);
        
        return node.value;
    }
    
    put(key, value, ttl = this.defaultTTL) {
        // If key exists, update it
        if (this.cache.has(key)) {
            const node = this.cache.get(key);
            node.value = value;
            node.expiresAt = Date.now() + ttl;
            this.remove(node);
            this.addToFront(node);
            return;
        }
        
        // If at capacity, evict LRU
        if (this.cache.size >= this.capacity) {
            this.evictLRU();
        }
        
        // Add new node
        const node = {
            key,
            value,
            expiresAt: Date.now() + ttl,
            prev: null,
            next: null
        };
        
        this.cache.set(key, node);
        this.addToFront(node);
    }
    
    isExpired(node) {
        return node.expiresAt !== Infinity && Date.now() > node.expiresAt;
    }
    
    remove(node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }
    
    addToFront(node) {
        node.next = this.head.next;
        node.prev = this.head;
        this.head.next.prev = node;
        this.head.next = node;
    }
    
    evictLRU() {
        const lru = this.tail.prev;
        if (lru !== this.head) {
            this.remove(lru);
            this.cache.delete(lru.key);
        }
    }
    
    // Lazy cleanup of expired entries
    startCleanup() {
        setInterval(() => {
            for (const [key, node] of this.cache) {
                if (this.isExpired(node)) {
                    this.remove(node);
                    this.cache.delete(key);
                }
            }
        }, 60000); // Clean every minute
    }
    
    // Active expiration during idle
    cleanupExpired() {
        const now = Date.now();
        for (const [key, node] of this.cache) {
            if (node.expiresAt !== Infinity && node.expiresAt <= now) {
                this.remove(node);
                this.cache.delete(key);
            }
        }
    }
    
    size() {
        return this.cache.size;
    }
    
    clear() {
        this.cache.clear();
        this.head.next = this.tail;
        this.tail.prev = this.head;
    }
}

// Thread-safe version (using locks pattern)
class ThreadSafeLRUCache extends LRUCacheWithTTL {
    constructor(capacity, defaultTTL) {
        super(capacity, defaultTTL);
        this.lock = false;
        this.queue = [];
    }
    
    async acquireLock() {
        return new Promise(resolve => {
            const tryAcquire = () => {
                if (!this.lock) {
                    this.lock = true;
                    resolve();
                } else {
                    this.queue.push(tryAcquire);
                }
            };
            tryAcquire();
        });
    }
    
    releaseLock() {
        this.lock = false;
        if (this.queue.length > 0) {
            const next = this.queue.shift();
            next();
        }
    }
    
    async get(key) {
        await this.acquireLock();
        try {
            return super.get(key);
        } finally {
            this.releaseLock();
        }
    }
    
    async put(key, value, ttl) {
        await this.acquireLock();
        try {
            super.put(key, value, ttl);
        } finally {
            this.releaseLock();
        }
    }
}
```

---

## Mock Interview 5: System Design + Coding Hybrid

### Technical Problem: Word Dictionary with Wildcards

**Problem Statement:**

"Design a word dictionary that supports:
1. Adding words
2. Searching with '.' wildcard (matches any single character)
3. Efficient prefix search
4. Memory efficient for large dictionaries"

---

#### Implementation

```javascript
class WordDictionary {
    constructor() {
        this.root = new Map();
    }
    
    addWord(word) {
        let node = this.root;
        for (const char of word) {
            if (!node.has(char)) {
                node.set(char, new Map());
            }
            node = node.get(char);
        }
        node.set('$', true); // End marker
    }
    
    search(word) {
        return this.searchHelper(word, 0, this.root);
    }
    
    searchHelper(word, index, node) {
        if (index === word.length) {
            return node.has('$');
        }
        
        const char = word[index];
        
        if (char === '.') {
            // Wildcard - try all children
            for (const [key, child] of node) {
                if (key !== '$' && this.searchHelper(word, index + 1, child)) {
                    return true;
                }
            }
            return false;
        }
        
        if (!node.has(char)) {
            return false;
        }
        
        return this.searchHelper(word, index + 1, node.get(char));
    }
    
    // Bonus: Get all words matching pattern
    getAllMatches(pattern) {
        const results = [];
        this.collectMatches(pattern, 0, this.root, '', results);
        return results;
    }
    
    collectMatches(pattern, index, node, current, results) {
        if (index === pattern.length) {
            if (node.has('$')) {
                results.push(current);
            }
            return;
        }
        
        const char = pattern[index];
        
        if (char === '.') {
            for (const [key, child] of node) {
                if (key !== '$') {
                    this.collectMatches(pattern, index + 1, child, current + key, results);
                }
            }
        } else if (node.has(char)) {
            this.collectMatches(pattern, index + 1, node.get(char), current + char, results);
        }
    }
    
    // Bonus: Autocomplete
    autocomplete(prefix, limit = 10) {
        let node = this.root;
        
        // Navigate to prefix end
        for (const char of prefix) {
            if (!node.has(char)) return [];
            node = node.get(char);
        }
        
        // Collect all words from here
        const results = [];
        this.collectAll(node, prefix, results, limit);
        return results;
    }
    
    collectAll(node, prefix, results, limit) {
        if (results.length >= limit) return;
        
        if (node.has('$')) {
            results.push(prefix);
        }
        
        for (const [key, child] of node) {
            if (key !== '$') {
                this.collectAll(child, prefix + key, results, limit);
            }
        }
    }
}

// Complexity Analysis:
// - addWord: O(L) where L = word length
// - search without wildcard: O(L)
// - search with wildcards: O(26^W * L) worst case, W = wildcards
// - Space: O(N * L) for N words
```

---

## Scoring Rubric

### Technical Assessment (60%)

| Level | Score | Description |
|-------|-------|-------------|
| **Strong Hire** | 4 | Optimal solution, clean code, excellent analysis |
| **Hire** | 3 | Working solution, good code, solid analysis |
| **Lean Hire** | 2 | Solution with minor issues, decent analysis |
| **Lean No Hire** | 1 | Significant gaps but shows potential |
| **No Hire** | 0 | Unable to solve, poor communication |

### Behavioral Assessment (40%)

| Competency | What to Demonstrate |
|------------|---------------------|
| **Problem Solving** | Structured approach, considers alternatives |
| **Communication** | Clear explanation, seeks feedback |
| **Ownership** | Takes initiative, acknowledges gaps |
| **Impact** | Quantifies results, shows scale |
| **Growth** | Learns from feedback, improves |

---

## Final Tips for Mock Interviews

1. **Think out loud** - Share your reasoning process
2. **Start with brute force** - Show you can get something working
3. **Optimize explicitly** - Explain why each optimization matters
4. **Test your code** - Walk through examples
5. **Ask clarifying questions** - Shows thoroughness
6. **Discuss tradeoffs** - Shows senior thinking
7. **Be time-aware** - Don't spend 20 min on clarifications

---

*Last Updated: February 2026*
