# Day 27: System Design with Node.js

## 🎯 Learning Objectives
- Design scalable systems using Node.js
- Understand common system design patterns
- Handle high-traffic scenarios
- Make architecture decisions with trade-offs

---

## 📚 System Design Principles

### Scalability Patterns

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCALING STRATEGIES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Horizontal:  [App1] [App2] [App3] ← Load Balancer              │
│  Vertical:    [App ↑CPU ↑RAM]                                    │
│  Database:    Read replicas, Sharding, Caching                   │
│  Async:       Queue → Workers (decouple write from processing)   │
│  CDN:         Static assets closer to users                      │
│  Caching:     Redis/Memcached for hot data                       │
│                                                                   │
│  Node.js specific:                                                │
│  ├── Cluster mode (utilize all CPU cores)                        │
│  ├── Worker threads (CPU-intensive tasks)                        │
│  ├── Event-driven (high concurrent connections)                  │
│  └── Streaming (handle large payloads efficiently)               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Design: URL Shortener

```javascript
// Requirements: Shorten URLs, redirect, analytics, high availability
// Scale: 100M URLs, 1B redirects/month

// Architecture:
// Client → CDN/Cache → Load Balancer → API Servers → Database
//                                                  → Cache (Redis)
//                                                  → Analytics (Kafka → ClickHouse)

// Key decisions:
// - Short code generation: Base62 encoding of counter (or random + collision check)
// - Storage: PostgreSQL (write) + Redis (read cache for redirects)
// - Analytics: Async via Kafka (don't block redirects)

class URLShortener {
  constructor(db, cache, analytics, idGenerator) {
    this.db = db;
    this.cache = cache;
    this.analytics = analytics;
    this.idGenerator = idGenerator;
  }

  async shorten(originalUrl, userId) {
    const shortCode = await this.idGenerator.generate(); // Base62 encoded
    const url = { shortCode, originalUrl, userId, createdAt: new Date() };
    
    await this.db.insert('urls', url);
    await this.cache.set(`url:${shortCode}`, originalUrl, 86400); // Cache 24h
    
    return `https://short.ly/${shortCode}`;
  }

  async redirect(shortCode, metadata) {
    // Try cache first (hot path)
    let url = await this.cache.get(`url:${shortCode}`);
    
    if (!url) {
      const record = await this.db.findOne('urls', { shortCode });
      if (!record) throw new NotFoundError('URL not found');
      url = record.originalUrl;
      await this.cache.set(`url:${shortCode}`, url, 86400);
    }

    // Async analytics (don't block redirect)
    this.analytics.track({ shortCode, ...metadata }).catch(() => {});
    
    return url;
  }
}

// ID Generation: Distributed unique IDs
class Base62IDGenerator {
  static CHARS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
  
  async generate() {
    const id = await this.getNextId(); // Snowflake or Redis INCR
    return this.encode(id);
  }
  
  encode(num) {
    let result = '';
    while (num > 0) {
      result = Base62IDGenerator.CHARS[num % 62] + result;
      num = Math.floor(num / 62);
    }
    return result.padStart(7, '0');
  }
}
```

### Design: Real-time Chat System

```javascript
// Requirements: 1-on-1, group chat, online status, message history
// Scale: 10M users, 1M concurrent connections

// Architecture:
// Client ←WebSocket→ Gateway (Socket.IO) → Redis Pub/Sub → Other Gateways
//                                         → Message Queue → Message Service → DB
//                                         → Presence Service (Redis)

class ChatGateway {
  constructor(io, redis, messageQueue) {
    this.io = io;
    this.redis = redis;
    this.messageQueue = messageQueue;
  }

  handleConnection(socket) {
    const userId = socket.user.id;
    
    // Track presence
    this.redis.set(`presence:${userId}`, socket.id, 'EX', 300);
    this.redis.publish('presence', JSON.stringify({ userId, status: 'online' }));
    
    // Join user's rooms
    socket.join(`user:${userId}`);
    
    socket.on('message:send', async (data) => {
      const message = {
        id: uuid(),
        from: userId,
        to: data.conversationId,
        content: data.content,
        timestamp: Date.now()
      };

      // Emit to room immediately (optimistic)
      this.io.to(`conv:${data.conversationId}`).emit('message:new', message);
      
      // Persist async via queue
      await this.messageQueue.publish('messages', message);
    });

    socket.on('disconnect', () => {
      this.redis.del(`presence:${userId}`);
      this.redis.publish('presence', JSON.stringify({ userId, status: 'offline' }));
    });
  }
}

// Scaling WebSockets: Redis adapter
const { createAdapter } = require('@socket.io/redis-adapter');
const pubClient = new Redis();
const subClient = pubClient.duplicate();
io.adapter(createAdapter(pubClient, subClient));
// Now events broadcast across all Socket.IO server instances
```

### Design: Task Queue / Job Scheduler

```javascript
// Requirements: Delayed jobs, retries, priorities, rate limiting
// Think: email sending, image processing, report generation

class JobScheduler {
  constructor(queue, registry) {
    this.queue = queue;      // BullMQ
    this.registry = registry; // Job type → handler mapping
  }

  async schedule(jobType, data, options = {}) {
    const job = await this.queue.add(jobType, data, {
      delay: options.delay,
      priority: options.priority || 0,
      attempts: options.maxRetries || 3,
      backoff: { type: 'exponential', delay: 1000 },
      removeOnComplete: { age: 86400 },
      removeOnFail: { age: 604800 },
    });
    return job.id;
  }

  async processJobs(concurrency = 5) {
    const worker = new Worker(this.queue.name, async (job) => {
      const handler = this.registry.get(job.name);
      if (!handler) throw new Error(`No handler for: ${job.name}`);
      
      return handler.execute(job.data, {
        progress: (pct) => job.updateProgress(pct),
        attempt: job.attemptsMade + 1
      });
    }, { concurrency });

    worker.on('completed', (job) => logger.info({ jobId: job.id }, 'Job completed'));
    worker.on('failed', (job, err) => logger.error({ jobId: job.id, err }, 'Job failed'));
  }
}
```

---

## 📚 Architecture Decision Framework

```
For each design decision, evaluate:

1. REQUIREMENTS: What are the functional + non-functional requirements?
2. SCALE: How much traffic? How much data? Growth rate?
3. TRADE-OFFS:
   - Consistency vs Availability (CAP theorem)
   - Latency vs Throughput
   - Simplicity vs Flexibility
   - Cost vs Performance
4. NODE.JS FIT: 
   - ✅ I/O bound (APIs, proxies, real-time)
   - ✅ High concurrency (WebSockets, streaming)
   - ❌ CPU bound (use workers or different service)
```

---

## 🧪 Interview Questions

### Beginner
**Q1: Why is Node.js good for real-time applications?**
Event-driven, non-blocking I/O handles thousands of concurrent connections on a single thread. WebSocket support is excellent (Socket.IO, ws). Low memory per connection (no thread per client). Same language client + server. Fast event loop processes messages quickly.

**Q2: How does horizontal scaling work with Node.js?**
Deploy multiple Node.js instances behind a load balancer (Nginx, ALB). Stateless design: store sessions in Redis (not memory). Shared state: Redis for cache, PostgreSQL for persistence. Cluster module or PM2 for multi-core on single machine. Docker + Kubernetes for container orchestration.

**Q3: What is the role of a message queue in system design?**
Decouples producers from consumers. Benefits: buffer traffic spikes, retry failed operations, distribute work across workers, handle backpressure, enable async processing. Examples: order placed → queue → payment processing, email sending, inventory update. Tools: Redis/BullMQ, RabbitMQ, SQS, Kafka.

### Intermediate
**Q4: Design a notification system that sends email, SMS, and push notifications.**
Architecture: API → Notification Service → Router (by channel + user preferences) → Channel Queues (email/SMS/push) → Workers → Provider APIs. Features: template engine, scheduling, batching, rate limiting per channel, fallback (if push fails → email). Storage: notification log in DB, delivery status tracking.

**Q5: How would you design a file upload service handling large files (>1GB)?**
Direct upload to S3 via pre-signed URLs (bypass your server). Multipart upload for large files. Flow: client requests upload URL → server generates pre-signed URL → client uploads directly to S3 → S3 triggers Lambda/webhook → process file. Benefits: no server memory/bandwidth consumed, resumable uploads.

**Q6: How do you handle distributed transactions across microservices?**
Saga pattern: sequence of local transactions with compensating actions on failure. Types: Choreography (events) or Orchestration (central coordinator). Example: Order Saga: Create Order → Reserve Inventory → Process Payment → Ship. If payment fails → release inventory → cancel order. Implement with event bus or Step Functions.

### Advanced
**Q7: Design a rate-limited API with 10M requests/second across multiple regions.**
Multi-region: API Gateways in each region → local Redis clusters for rate limiting. Approximate counting (allow slight over-limit for performance). Token bucket per user replicated across regions with eventual consistency. Global limits: periodic sync between regions. Use CDN for cacheable responses. Edge compute for hot paths.

**Q8: How would you design a real-time collaborative editing system (like Google Docs)?**
Conflict resolution: OT (Operational Transformation) or CRDT (Conflict-free Replicated Data Types). Architecture: Client → WebSocket → Transform Server → Broadcast to other clients. Persistence: periodic snapshots + operation log. Node.js role: WebSocket gateway, operation processing. Yjs or Automerge for CRDT library.

**Q9: Design a system that handles 1M webhook deliveries per minute with guaranteed delivery.**
Architecture: Webhook events → Kafka (durable queue) → Consumer workers → HTTP delivery. Retry: exponential backoff (1s, 5s, 30s, 5min, 1h). DLQ after max retries. Delivery tracking: DB records per attempt. Fan-out: partition by destination URL. Circuit breaker per endpoint. Signature verification (HMAC). Idempotency keys.

---

## 🛠️ Hands-on Exercise
Design and implement (high-level):
1. URL shortener with analytics
2. Real-time notification system
3. Background job processor with BullMQ
4. Write design doc with architecture diagram
5. Identify bottlenecks and scaling strategies
