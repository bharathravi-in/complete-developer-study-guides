# Day 11: Caching & Performance

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. Redis
- [ ] Understand Redis architecture
- [ ] Know Redis data structures

```
┌─────────────────────────────────────────────────────────────────────┐
│  Redis Architecture                                                  │
│                                                                     │
│   ┌─────────────────────────────────────────────────────────────┐   │
│   │                     Redis Server                             │   │
│   │   ┌─────────────────────────────────────────────────────┐   │   │
│   │   │           In-Memory Data Store                       │   │   │
│   │   │                                                     │   │   │
│   │   │   Key: "user:1"        → {name: "John", age: 30}   │   │   │
│   │   │   Key: "session:abc"   → {userId: 1, expires: ...} │   │   │
│   │   │   Key: "cache:posts"   → [post1, post2, ...]       │   │   │
│   │   │                                                     │   │   │
│   │   └─────────────────────────────────────────────────────┘   │   │
│   │                                                             │   │
│   │   Optional Persistence: RDB (snapshots) / AOF (log)         │   │
│   └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│   Features:                                                         │
│   • Sub-millisecond latency                                        │
│   • Pub/Sub messaging                                              │
│   • Lua scripting                                                  │
│   • Cluster mode                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

**Redis Data Structures:**

| Structure | Use Case | Example |
|-----------|----------|---------|
| **String** | Simple cache, counters | Session, page views |
| **Hash** | Objects | User profile |
| **List** | Queues, timelines | Activity feed |
| **Set** | Unique items | Tags, unique visitors |
| **Sorted Set** | Leaderboards | Game scores |
| **Stream** | Event log | Message queue |

**Common Operations:**
```redis
# String
SET user:1:name "John"
GET user:1:name
SETEX session:abc 3600 "data"    # Expires in 1 hour

# Hash
HSET user:1 name "John" age 30
HGET user:1 name
HGETALL user:1

# List
LPUSH notifications:user1 "new message"
LRANGE notifications:user1 0 10

# Sorted Set
ZADD leaderboard 100 "player1" 200 "player2"
ZRANGE leaderboard 0 10 WITHSCORES DESC
```

---

### 2. CDN (Content Delivery Network)
- [ ] Understand CDN architecture
- [ ] Know caching strategies

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CDN Architecture                                                        │
│                                                                         │
│     User (Tokyo)                           User (New York)              │
│          │                                       │                      │
│          ▼                                       ▼                      │
│   ┌──────────────┐                       ┌──────────────┐              │
│   │  Edge Node   │                       │  Edge Node   │              │
│   │   (Tokyo)    │                       │  (New York)  │              │
│   │   Cache HIT  │                       │  Cache MISS  │              │
│   └──────────────┘                       └──────┬───────┘              │
│          │                                      │                       │
│          │ Fast!                                │ Request Origin        │
│          ▼                                      ▼                       │
│   Content returned                       ┌──────────────┐              │
│   in 20ms                                │  Origin      │              │
│                                          │  Server      │              │
│                                          │ (California) │              │
│                                          └──────────────┘              │
│                                                 │                       │
│                                          Content cached                 │
│                                          at edge for                    │
│                                          next request                   │
│                                                                         │
│   CDN Providers: CloudFlare, AWS CloudFront, Akamai, Fastly           │
└─────────────────────────────────────────────────────────────────────────┘
```

**CDN Headers:**
```http
# Cache for 1 year (static assets)
Cache-Control: public, max-age=31536000, immutable

# Cache for 5 minutes (API responses)
Cache-Control: public, max-age=300, s-maxage=300

# Don't cache
Cache-Control: no-store, no-cache, must-revalidate

# Vary by headers (different cache per encoding)
Vary: Accept-Encoding
```

---

### 3. Cache Invalidation
- [ ] Understand invalidation strategies
- [ ] Know the challenges

> "There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton

**Cache Invalidation Strategies:**

```
1. Time-Based (TTL)
┌─────────────────────────────────────────────────────────────────────┐
│  SET key "value" EX 3600                                            │
│                                                                     │
│  ──────────────────────────────────────►                           │
│  │  Valid              │  Expired (auto-delete)                    │
│  └─────────────────────┴────────────────────────                   │
│  0                    3600 seconds                                  │
└─────────────────────────────────────────────────────────────────────┘

2. Write-Through
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Write Request                                                      │
│       │                                                            │
│       ├──────────────►  Update DB  ─────► Success                 │
│       │                                      │                     │
│       └──────────────►  Update Cache ◄──────┘                     │
│                            (atomic)                                │
│                                                                     │
│  Pro: Strong consistency                                           │
│  Con: Higher write latency                                         │
└─────────────────────────────────────────────────────────────────────┘

3. Write-Behind (Write-Back)
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Write Request                                                      │
│       │                                                            │
│       └──────────────►  Update Cache  ─────► Immediate Response    │
│                              │                                     │
│                              │ (Async, batched)                    │
│                              ▼                                     │
│                         Update DB                                  │
│                                                                     │
│  Pro: Fast writes                                                  │
│  Con: Risk of data loss if cache fails                            │
└─────────────────────────────────────────────────────────────────────┘

4. Cache-Aside (Lazy Loading)
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  Read:                          Write:                             │
│  1. Check cache                 1. Update DB                       │
│  2. If miss, read DB            2. Invalidate cache                │
│  3. Populate cache                                                 │
│                                                                     │
│  Pro: Simple, common pattern                                       │
│  Con: Cache miss penalty, stale data possible                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 4. LRU, LFU
- [ ] Understand eviction policies
- [ ] Know when to use each

**Cache Eviction Policies:**

```
LRU (Least Recently Used)
┌─────────────────────────────────────────────────────────────────────┐
│  Cache: [A, B, C, D] (max 4 items)                                 │
│                                                                     │
│  Access A → [B, C, D, A]          (A moves to end)                 │
│  Add E   → [C, D, A, E]           (B evicted, least recent)        │
│                                                                     │
│  Use: General-purpose caching                                      │
└─────────────────────────────────────────────────────────────────────┘

LFU (Least Frequently Used)
┌─────────────────────────────────────────────────────────────────────┐
│  Cache: {A: 5 hits, B: 2 hits, C: 10 hits, D: 1 hit}              │
│                                                                     │
│  Add E   → Evict D (lowest frequency)                              │
│                                                                     │
│  Use: When access patterns have clear hotspots                    │
└─────────────────────────────────────────────────────────────────────┘

Other Policies:
- FIFO: First In, First Out
- Random: Random eviction
- TTL: Time-based expiration
- LRU-K: LRU with K recent accesses considered
```

**Redis Eviction Policies:**
```redis
# In redis.conf
maxmemory 100mb
maxmemory-policy allkeys-lru  # or: volatile-lru, allkeys-lfu, volatile-ttl
```

---

## 📘 Performance Optimization

### Database Query Optimization

```sql
-- Bad: N+1 Query Problem
SELECT * FROM users;
-- Then for each user:
SELECT * FROM orders WHERE user_id = ?;

-- Good: Join
SELECT u.*, o.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;

-- Analyze queries
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';
```

### Application-Level Caching

```typescript
// Caching decorator pattern
class CacheService {
  async get<T>(key: string, fetchFn: () => Promise<T>, ttl: number): Promise<T> {
    // Try cache first
    const cached = await this.redis.get(key);
    if (cached) {
      return JSON.parse(cached);
    }

    // Fetch from source
    const data = await fetchFn();
    
    // Cache for future
    await this.redis.setex(key, ttl, JSON.stringify(data));
    
    return data;
  }
}

// Usage
const user = await cacheService.get(
  `user:${userId}`,
  () => userRepository.findById(userId),
  3600 // 1 hour TTL
);
```

### Connection Pooling

```
Without Pooling:                 With Pooling:
┌─────────┐                     ┌─────────┐
│ Request │                     │ Request │
└────┬────┘                     └────┬────┘
     │                               │
     │ Create new                    │ Get from pool
     │ connection                    │
     ▼                               ▼
┌─────────┐                     ┌───────────────┐
│   DB    │                     │ Connection    │
│         │                     │    Pool       │
└─────────┘                     │  ┌───┐ ┌───┐  │
                                │  │Con│ │Con│  │
Expensive:                      │  └───┘ └───┘  │
- TCP handshake                 └───────┬───────┘
- Auth                                  │
- SSL negotiation                       ▼
                                ┌─────────┐
                                │   DB    │
                                └─────────┘
                                Fast: Reuse existing
```

---

## 🎯 Practice Task

### Design Caching Strategy

**Instructions:**
1. Design caching for an e-commerce product catalog
2. Consider: Product details, search results, inventory
3. Define TTL for each cache type
4. Handle cache invalidation

**Template:**

```markdown
## E-Commerce Caching Strategy

### Cache Types

| Data | Cache Layer | TTL | Invalidation |
|------|-------------|-----|--------------|
| Product details | | | |
| Search results | | | |
| Inventory count | | | |
| User cart | | | |
| Category list | | | |

### Implementation
[Describe implementation approach]

### Metrics to Monitor
- Cache hit ratio
- Latency (p50, p95, p99)
- Memory usage
- Eviction rate
```

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] [Redis University](https://university.redis.com/)
- [ ] [High Scalability Blog](http://highscalability.com/)
- [ ] [Caching at Scale](https://aws.amazon.com/caching/)

---

## ✅ Completion Checklist

- [ ] Understood Redis data structures
- [ ] Know CDN caching strategies
- [ ] Mastered cache invalidation patterns
- [ ] Know LRU vs LFU
- [ ] Completed practice task

**Date Completed:** _____________
