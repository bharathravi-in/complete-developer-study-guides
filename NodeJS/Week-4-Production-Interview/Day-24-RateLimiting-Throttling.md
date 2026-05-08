# Day 24: Rate Limiting & API Throttling

## 🎯 Learning Objectives
- Implement rate limiting algorithms (token bucket, sliding window)
- Use Redis-backed distributed rate limiting
- Configure per-user, per-endpoint, and tiered limits
- Handle rate limit responses properly

---

## 📚 Rate Limiting Fundamentals

### Algorithms

```
┌─────────────────────────────────────────────────────────────────┐
│                  RATE LIMITING ALGORITHMS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Fixed Window:        [====|====|====]  Simple but bursty edges  │
│  Sliding Window:      [--==|==--|--==]  Smooth, more accurate    │
│  Token Bucket:        [●●●○○ refill]   Allows bursts             │
│  Leaky Bucket:        [drip...drip]    Constant rate output      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Basic Rate Limiter (express-rate-limit)

```javascript
const rateLimit = require('express-rate-limit');

// Global limiter
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,                   // 100 requests per window
  standardHeaders: true,      // Return rate limit info in RateLimit-* headers
  legacyHeaders: false,
  message: { error: 'Too many requests, please try again later' },
  keyGenerator: (req) => req.user?.id || req.ip,
  skip: (req) => req.path === '/health',
});

app.use(globalLimiter);

// Strict limiter for auth endpoints
const authLimiter = rateLimit({
  windowMs: 60 * 1000,  // 1 minute
  max: 5,               // 5 login attempts
  skipSuccessfulRequests: true,
});

app.use('/api/auth/login', authLimiter);
```

### Redis-backed Sliding Window

```javascript
const Redis = require('ioredis');
const redis = new Redis(process.env.REDIS_URL);

class SlidingWindowRateLimiter {
  constructor({ windowMs, maxRequests }) {
    this.windowMs = windowMs;
    this.maxRequests = maxRequests;
  }

  async isAllowed(key) {
    const now = Date.now();
    const windowStart = now - this.windowMs;
    const redisKey = `ratelimit:${key}`;

    const pipeline = redis.pipeline();
    pipeline.zremrangebyscore(redisKey, 0, windowStart);  // Remove old entries
    pipeline.zadd(redisKey, now, `${now}-${Math.random()}`);  // Add current
    pipeline.zcard(redisKey);  // Count in window
    pipeline.expire(redisKey, Math.ceil(this.windowMs / 1000));

    const results = await pipeline.exec();
    const count = results[2][1];

    return {
      allowed: count <= this.maxRequests,
      remaining: Math.max(0, this.maxRequests - count),
      resetAt: new Date(now + this.windowMs),
      total: this.maxRequests
    };
  }
}

// Token Bucket Algorithm
class TokenBucketLimiter {
  constructor({ capacity, refillRate, refillInterval }) {
    this.capacity = capacity;          // Max tokens
    this.refillRate = refillRate;      // Tokens per refill
    this.refillInterval = refillInterval; // ms between refills
  }

  async consume(key, tokens = 1) {
    const script = `
      local key = KEYS[1]
      local capacity = tonumber(ARGV[1])
      local refillRate = tonumber(ARGV[2])
      local refillInterval = tonumber(ARGV[3])
      local now = tonumber(ARGV[4])
      local tokens = tonumber(ARGV[5])
      
      local bucket = redis.call('HMGET', key, 'tokens', 'lastRefill')
      local currentTokens = tonumber(bucket[1]) or capacity
      local lastRefill = tonumber(bucket[2]) or now
      
      -- Refill tokens
      local elapsed = now - lastRefill
      local refills = math.floor(elapsed / refillInterval)
      currentTokens = math.min(capacity, currentTokens + (refills * refillRate))
      lastRefill = lastRefill + (refills * refillInterval)
      
      -- Try to consume
      if currentTokens >= tokens then
        currentTokens = currentTokens - tokens
        redis.call('HMSET', key, 'tokens', currentTokens, 'lastRefill', lastRefill)
        redis.call('EXPIRE', key, math.ceil(capacity / refillRate * refillInterval / 1000))
        return {1, currentTokens}
      end
      
      return {0, currentTokens}
    `;

    const [allowed, remaining] = await redis.eval(
      script, 1, `bucket:${key}`,
      this.capacity, this.refillRate, this.refillInterval, Date.now(), tokens
    );

    return { allowed: allowed === 1, remaining };
  }
}
```

### Tiered Rate Limiting

```javascript
// Different limits based on user plan
const TIER_LIMITS = {
  free:       { windowMs: 60000, max: 20 },
  basic:      { windowMs: 60000, max: 100 },
  pro:        { windowMs: 60000, max: 500 },
  enterprise: { windowMs: 60000, max: 5000 },
};

function tieredRateLimiter() {
  const limiters = {};

  return async (req, res, next) => {
    const tier = req.user?.plan || 'free';
    const key = req.user?.id || req.ip;
    const config = TIER_LIMITS[tier];

    if (!limiters[tier]) {
      limiters[tier] = new SlidingWindowRateLimiter(config);
    }

    const result = await limiters[tier].isAllowed(key);

    // Set standard headers
    res.set('RateLimit-Limit', config.max);
    res.set('RateLimit-Remaining', result.remaining);
    res.set('RateLimit-Reset', Math.ceil(result.resetAt.getTime() / 1000));

    if (!result.allowed) {
      res.set('Retry-After', Math.ceil(config.windowMs / 1000));
      return res.status(429).json({
        error: 'Rate limit exceeded',
        retryAfter: Math.ceil(config.windowMs / 1000),
        limit: config.max,
        upgrade: tier === 'free' ? 'Upgrade to Basic for higher limits' : undefined
      });
    }

    next();
  };
}
```

---

## 🧪 Interview Questions

### Beginner
**Q1: What is rate limiting and why is it needed?**
Rate limiting restricts the number of requests a client can make in a time window. Needed for: preventing abuse/DDoS, protecting backend resources, fair usage among users, cost control (API calls to third parties), preventing brute-force attacks. Common: 100 requests/minute per user.

**Q2: What HTTP status code and headers should a rate-limited response include?**
Status: 429 Too Many Requests. Headers: `RateLimit-Limit` (max requests), `RateLimit-Remaining` (remaining), `RateLimit-Reset` (when window resets), `Retry-After` (seconds to wait). Body: error message + retry information. Clients should implement exponential backoff.

**Q3: What's the difference between rate limiting and throttling?**
Rate limiting: rejects requests exceeding the limit (hard cutoff). Throttling: slows down processing (queues or delays). Rate limiting protects the server; throttling smooths traffic. Example: rate limit = 429 response; throttle = add 100ms delay per excess request.

### Intermediate
**Q4: Compare fixed window vs sliding window rate limiting.**
Fixed window: simple counters reset at interval boundaries. Problem: burst at window edges (2x traffic). Sliding window: considers requests across a rolling window. More accurate, prevents edge bursts. Implementation: sorted set in Redis (timestamp → score). Sliding window uses more memory but is fairer.

**Q5: How do you implement distributed rate limiting across multiple server instances?**
Use shared state: Redis (most common), Memcached. Each request checks/increments a counter in Redis. Use Lua scripts for atomicity (check + increment in single operation). Consider: Redis latency overhead, what happens if Redis is down (fail open vs fail closed).

**Q6: How do you handle rate limiting for authenticated vs unauthenticated users?**
Key by user ID for authenticated, IP for anonymous. Authenticated users get higher limits. Apply multiple layers: global per-IP (DDoS protection), per-user (fair usage), per-endpoint (expensive operations). Allow burst but limit sustained rate.

### Advanced
**Q7: Design a rate limiting system for an API gateway serving multiple microservices.**
Architecture: API gateway → Redis cluster for global limits. Per-service limits (quotas). Per-user per-service limits. Hierarchical: global → service → user. Use token bucket for burst tolerance. Sync across gateway instances via Redis. Circuit breaker if Redis fails. Metrics: track limit hits for capacity planning.

**Q8: How would you implement adaptive rate limiting that adjusts based on system load?**
Monitor: CPU usage, event loop lag, response times, error rates. When load high → decrease limits dynamically. Feedback loop: (1) Collect metrics. (2) Score system health 0-1. (3) Multiply limits by health score. (4) Gradually restore when load decreases. Priority queues: reduce free-tier first, enterprise last.

**Q9: Explain the token bucket algorithm and when to prefer it over sliding window.**
Token bucket: bucket holds N tokens, refills at rate R. Each request consumes a token. If empty → reject. Advantages: allows bursts (bucket can be full), constant refill rate, configurable burst size separate from sustained rate. Prefer over sliding window when: you want to allow short bursts, need configurable burst/sustain independently.

---

## 🛠️ Hands-on Exercise
Build a production rate limiting system:
1. Sliding window rate limiter with Redis
2. Token bucket for burst handling
3. Tiered limits (free/pro/enterprise)
4. Per-endpoint limits (strict for auth)
5. Standard rate limit response headers
6. Graceful degradation when Redis is down
