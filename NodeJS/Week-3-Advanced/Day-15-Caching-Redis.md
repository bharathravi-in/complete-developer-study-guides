# Day 15: Caching Strategies (Redis, In-Memory)

## 🎯 Learning Objectives
- Implement caching with Redis
- Understand cache patterns (aside, through, back)
- Build cache invalidation strategies
- Use in-memory caching for hot data

---

## 📚 Redis Fundamentals

### Connection & Basic Operations

```javascript
const Redis = require('ioredis');

const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD,
  maxRetriesPerRequest: 3,
  retryStrategy(times) {
    return Math.min(times * 50, 2000);
  }
});

redis.on('connect', () => console.log('Redis connected'));
redis.on('error', (err) => console.error('Redis error:', err));

// Basic operations
await redis.set('user:123', JSON.stringify(user));
await redis.set('session:abc', 'data', 'EX', 3600); // Expires in 1 hour
const data = JSON.parse(await redis.get('user:123'));
await redis.del('user:123');

// Hash operations (structured data)
await redis.hset('user:123', { name: 'Alice', email: 'alice@example.com', role: 'admin' });
const user = await redis.hgetall('user:123');
await redis.hincrby('user:123', 'loginCount', 1);

// Lists (queues)
await redis.lpush('queue:emails', JSON.stringify({ to: 'user@test.com', subject: 'Hello' }));
const job = await redis.rpop('queue:emails');

// Sets (unique collections)
await redis.sadd('online:users', 'user123', 'user456');
const onlineCount = await redis.scard('online:users');
await redis.srem('online:users', 'user123');

// Sorted sets (leaderboards, rate limiting)
await redis.zadd('leaderboard', 100, 'player1', 200, 'player2');
const top10 = await redis.zrevrange('leaderboard', 0, 9, 'WITHSCORES');
```

---

## 🔄 Cache Patterns

### Cache-Aside (Lazy Loading)

```javascript
async function getUser(userId) {
  const cacheKey = `user:${userId}`;
  
  // 1. Check cache first
  const cached = await redis.get(cacheKey);
  if (cached) {
    return JSON.parse(cached);
  }
  
  // 2. Cache miss - fetch from database
  const user = await db.users.findById(userId);
  if (!user) return null;
  
  // 3. Store in cache with TTL
  await redis.set(cacheKey, JSON.stringify(user), 'EX', 3600);
  
  return user;
}

// Invalidate on update
async function updateUser(userId, data) {
  const user = await db.users.update(userId, data);
  await redis.del(`user:${userId}`); // Invalidate cache
  return user;
}
```

### Write-Through Cache

```javascript
async function createUser(data) {
  // Write to database
  const user = await db.users.create(data);
  
  // Immediately cache
  await redis.set(`user:${user.id}`, JSON.stringify(user), 'EX', 3600);
  
  return user;
}
```

### Cache with Stampede Prevention

```javascript
const locks = new Map();

async function getWithLock(key, fetchFn, ttl = 3600) {
  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);
  
  // Prevent cache stampede (many requests hitting DB simultaneously on cache miss)
  if (locks.has(key)) {
    return locks.get(key); // Return existing promise
  }
  
  const promise = (async () => {
    try {
      const data = await fetchFn();
      await redis.set(key, JSON.stringify(data), 'EX', ttl);
      return data;
    } finally {
      locks.delete(key);
    }
  })();
  
  locks.set(key, promise);
  return promise;
}
```

### Express Caching Middleware

```javascript
function cacheMiddleware(ttl = 300, keyPrefix = '') {
  return async (req, res, next) => {
    if (req.method !== 'GET') return next();
    
    const key = `${keyPrefix}:${req.originalUrl}`;
    
    try {
      const cached = await redis.get(key);
      if (cached) {
        const { data, headers } = JSON.parse(cached);
        res.set(headers);
        res.set('X-Cache', 'HIT');
        return res.json(data);
      }
    } catch (err) {
      // Cache failure shouldn't break the app
      console.error('Cache read error:', err);
    }
    
    // Override res.json to cache response
    const originalJson = res.json.bind(res);
    res.json = async (data) => {
      try {
        await redis.set(key, JSON.stringify({
          data,
          headers: { 'Content-Type': 'application/json' }
        }), 'EX', ttl);
      } catch (err) {
        console.error('Cache write error:', err);
      }
      res.set('X-Cache', 'MISS');
      return originalJson(data);
    };
    
    next();
  };
}

// Usage
router.get('/api/posts', cacheMiddleware(300, 'posts'), getPosts);
```

---

## 🗑️ Cache Invalidation Strategies

```javascript
// Pattern-based invalidation
async function invalidatePattern(pattern) {
  const keys = await redis.keys(pattern); // e.g., 'user:123:*'
  if (keys.length > 0) {
    await redis.del(...keys);
  }
}

// Tag-based invalidation
async function setWithTags(key, value, ttl, tags) {
  const pipeline = redis.pipeline();
  pipeline.set(key, JSON.stringify(value), 'EX', ttl);
  for (const tag of tags) {
    pipeline.sadd(`tag:${tag}`, key);
  }
  await pipeline.exec();
}

async function invalidateByTag(tag) {
  const keys = await redis.smembers(`tag:${tag}`);
  if (keys.length > 0) {
    await redis.del(...keys, `tag:${tag}`);
  }
}

// Usage
await setWithTags('post:123', postData, 3600, ['posts', 'user:456:posts']);
await invalidateByTag('user:456:posts'); // Clears all posts by user 456
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is caching and why is it important?**

Caching stores frequently accessed data in fast storage (memory/Redis) to reduce database load and improve response times. Benefits: lower latency (Redis: ~1ms vs DB: ~10-50ms), reduced database load, handles traffic spikes. Trade-off: data freshness (stale data risk) and added complexity.

**Q2: What is the difference between Redis and in-memory caching?**

In-memory (e.g., Map/LRU cache): per-process, lost on restart, no sharing between instances. Redis: separate service, persistent, shared across all app instances, supports data structures (lists, sets, sorted sets), built-in TTL, pub/sub. Use in-memory for single-instance hot data; Redis for distributed apps.

**Q3: What is TTL (Time To Live) in caching?**

TTL is the duration a cached entry remains valid before automatic expiration. `redis.set(key, value, 'EX', 3600)` = expires after 1 hour. Choose TTL based on: data change frequency, acceptable staleness, and business requirements. Short TTL = fresher data but more DB hits.

### Intermediate

**Q4: Explain cache-aside vs write-through vs write-behind patterns.**

Cache-aside: app manages cache explicitly (read: check cache → miss → fetch DB → write cache). Write-through: write to cache AND database synchronously (consistent but slower writes). Write-behind: write to cache immediately, async write to DB later (fast writes but risk of data loss).

**Q5: What is a cache stampede and how do you prevent it?**

Cache stampede: when a popular cache entry expires, many concurrent requests hit the database simultaneously. Prevention: (1) Lock/mutex — only one request fetches, others wait. (2) Stale-while-revalidate — serve stale data while refreshing. (3) Pre-warming — refresh before expiry. (4) Probabilistic early expiration.

**Q6: How do you handle cache invalidation in a microservices architecture?**

Options: (1) Event-driven — publish events on data change, subscribers invalidate. (2) TTL-based — accept eventual consistency. (3) Cache tags — invalidate groups of related keys. (4) CDC (Change Data Capture) — database triggers invalidation. Most common: events + short TTL as safety net.

### Advanced

**Q7: Design a multi-tier caching strategy for a high-traffic API.**

L1: In-process LRU cache (10ms response, hot data). L2: Redis cluster (sub-ms network, shared state). L3: CDN for static/semi-static responses. Strategy: check L1 → L2 → Database. Write-through from DB to L2, stale-while-revalidate for L1. CDN with short TTL + Cache-Control headers. Monitor hit ratios per tier.

**Q8: How would you implement distributed rate limiting with Redis?**

Sliding window algorithm: Use sorted set with timestamps. On each request: remove entries outside window (`ZREMRANGEBYSCORE`), count remaining (`ZCARD`), add new entry if under limit. Atomic with `MULTI/EXEC`. Alternative: Token bucket — Redis key with counter, refill with Lua script. Handle Redis failures with local fallback.

**Q9: Compare Redis Cluster vs Redis Sentinel for high availability.**

Sentinel: automatic failover for master-replica setup, doesn't shard data. Cluster: shards data across multiple nodes (16384 hash slots), built-in failover per shard. Choose Sentinel: dataset fits one node, simpler ops. Choose Cluster: large datasets, high throughput needs. Both provide HA but with different trade-offs.

---

## 🛠️ Hands-on Exercise

Build a caching layer for an API:
1. Redis cache-aside for user/post queries
2. Cache invalidation on writes (tag-based)
3. Stampede prevention with locks
4. In-memory LRU for ultra-hot data
5. Cache hit/miss metrics endpoint
6. Graceful degradation when Redis is down
