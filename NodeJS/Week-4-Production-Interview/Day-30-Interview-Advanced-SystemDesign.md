# Day 30: Interview Questions — Advanced & System Design

## 🎯 Learning Objectives
- Master advanced Node.js interview topics
- Practice system design questions with Node.js
- Understand production-grade patterns
- Prepare for senior/staff-level interviews

---

## 📚 Advanced Node.js Questions

### Q1: How does V8's garbage collector work? How does it affect Node.js performance?

**Answer:**
V8 uses generational garbage collection:

- **Young Generation (Scavenge)**: Short-lived objects. Divided into semi-spaces (from/to). Objects surviving 2 scavenges get promoted.
- **Old Generation (Mark-Sweep-Compact)**: Long-lived objects. Mark reachable objects → sweep unreachable → compact memory.

Impact on Node.js:
- GC pauses block the event loop (stop-the-world)
- Young gen GC: ~1-5ms (fast, frequent)
- Old gen GC: ~50-200ms (slow, infrequent)
- `--max-old-space-size=4096` to increase heap (default ~1.5GB)
- Monitor with `--trace-gc` or `v8.getHeapStatistics()`

Optimization: avoid creating many short-lived objects in hot paths, reuse buffers, use object pools for frequent allocations.

---

### Q2: Explain backpressure in streams and how to handle it.

**Answer:**
Backpressure occurs when a writable stream can't process data as fast as it's being produced.

```javascript
const readable = fs.createReadStream('huge-file.csv');
const writable = fs.createWriteStream('output.json');

// Manual backpressure handling
readable.on('data', (chunk) => {
  const canContinue = writable.write(chunk);
  if (!canContinue) {
    readable.pause();  // Stop reading until drain
  }
});

writable.on('drain', () => {
  readable.resume();  // Safe to continue
});

// Better: pipeline handles backpressure automatically
const { pipeline } = require('stream/promises');
await pipeline(readable, transformStream, writable);
```

`pipeline` also handles cleanup (destroy streams on error). Always prefer `pipeline` over manual `.pipe()` for proper error + backpressure handling.

---

### Q3: How do Worker Threads differ from the Cluster module?

**Answer:**

| Feature | Worker Threads | Cluster |
|---------|---------------|---------|
| Type | Threads (shared memory) | Processes (separate memory) |
| Communication | SharedArrayBuffer, MessagePort | IPC (serialized) |
| Memory | Shared possible | Isolated |
| Use case | CPU-intensive tasks | Multi-core HTTP serving |
| Overhead | Lower (shared V8 isolate resources) | Higher (full process copy) |
| Fault isolation | Thread crash can affect process | Process crash isolated |

Use Worker Threads for: crypto, image processing, heavy computation.
Use Cluster for: scaling HTTP servers across CPU cores.

---

### Q4: What is the `AsyncLocalStorage` API and how is it used?

**Answer:**
`AsyncLocalStorage` provides context (like thread-local storage) that follows async call chains without explicitly passing values.

```javascript
const { AsyncLocalStorage } = require('async_hooks');
const context = new AsyncLocalStorage();

// Middleware: set request context
app.use((req, res, next) => {
  const store = { requestId: uuid(), userId: req.user?.id, startTime: Date.now() };
  context.run(store, next);
});

// Anywhere in the call chain (services, repositories, utilities):
function getRequestId() {
  return context.getStore()?.requestId;
}

// Logger automatically includes request context
const logger = {
  info(msg, data) {
    const store = context.getStore();
    console.log(JSON.stringify({ ...data, msg, requestId: store?.requestId }));
  }
};
```

Use cases: request-scoped logging, transaction management, user context propagation, multi-tenancy.

---

### Q5: How would you debug a memory leak in production?

**Answer:**
Steps:
1. **Detect**: Monitor RSS/heap with `process.memoryUsage()`, alert on upward trend
2. **Reproduce**: Load test with `autocannon` or replay production traffic
3. **Profile**: 
   - `--inspect` + Chrome DevTools → Heap Snapshots (compare 3 snapshots)
   - `--heapsnapshot-signal=SIGUSR2` → trigger snapshot in production
   - `clinic heapprofile` for flamegraph view
4. **Identify**: Look for growing retainers (objects preventing GC)
5. **Common culprits**: unbounded caches, event listeners, closures, global arrays
6. **Fix**: WeakMap/WeakSet, LRU caches, proper cleanup, `once` for listeners

```javascript
// Quick production diagnostic
setInterval(() => {
  const { heapUsed, heapTotal, rss } = process.memoryUsage();
  logger.info({ heapUsed: heapUsed / 1024 / 1024, rss: rss / 1024 / 1024 }, 'Memory');
}, 30000);
```

---

### Q6: Explain the Reactor pattern and how it relates to Node.js.

**Answer:**
The Reactor pattern is the architectural foundation of Node.js:

1. Application submits I/O operations to the demultiplexer (libuv)
2. Demultiplexer watches multiple I/O sources simultaneously
3. When I/O completes, event is placed in the event queue
4. Event loop picks events from queue and executes associated callbacks

```
Application → I/O Request → Demultiplexer (epoll/kqueue/IOCP)
                                    ↓ (I/O ready)
Application ← Callback ← Event Queue ← Event
```

This is why Node.js excels at I/O-bound tasks: one thread efficiently manages thousands of concurrent I/O operations through the OS-level event notification mechanism.

---

### Q7: How do you implement graceful degradation in a microservice?

**Answer:**
When a dependency fails, serve reduced functionality rather than complete failure:

```javascript
class UserService {
  constructor(userDb, cache, recommendationService) {
    this.userDb = userDb;
    this.cache = cache;
    this.recommendations = recommendationService;
  }

  async getUserProfile(userId) {
    // Primary data: must succeed
    const user = await this.userDb.findById(userId);
    if (!user) throw new NotFoundError('User', userId);

    // Enrichment: best-effort (graceful degradation)
    let recommendations = [];
    try {
      recommendations = await this.recommendations.getForUser(userId);
    } catch (error) {
      logger.warn({ userId, error }, 'Recommendations unavailable, serving without');
      // Return profile without recommendations — still useful!
    }

    return { ...user, recommendations };
  }
}
```

Patterns: fallback to cache, default values, feature flags, partial responses with degradation headers.

---

## 📚 System Design Questions

### Q8: Design a real-time notification system for 10M users.

**Answer:**

**Requirements:** Push notifications to web/mobile, support in-app + email + SMS, delivery guarantees, user preferences.

**Architecture:**
```
Event Source → Event Bus (Kafka) → Notification Service → Channel Router
                                                              ↓
                                    ┌──────────────┬──────────────┬────────────┐
                                    │ WebSocket    │ Push (FCM)   │ Email      │
                                    │ Gateway      │ Service      │ Service    │
                                    └──────────────┴──────────────┴────────────┘
```

**Key decisions:**
- Kafka for durability + ordering per user (partition by userId)
- Redis for WebSocket session tracking (which server has user's connection)
- Priority queue: urgent notifications jump the queue
- Batching: aggregate low-priority notifications (digest email)
- Deduplication: idempotency key per notification
- User preferences: do-not-disturb, channel preferences stored in DB
- Delivery tracking: status per notification (sent/delivered/read)

**Scaling WebSocket connections:**
- Socket.IO with Redis adapter (cross-server broadcasting)
- Sticky sessions at load balancer (or Redis pub/sub)
- 100K connections per server → 100 servers for 10M

---

### Q9: Design a distributed task scheduler (like cron but for millions of jobs).

**Answer:**

**Requirements:** Schedule jobs at specific times, recurring schedules, exactly-once execution, scale to millions of pending jobs.

**Architecture:**
```
API → Job Store (PostgreSQL) → Scheduler Partition Leader → Worker Pool
                                       ↓
                              Timer Wheel / Sorted Set (Redis)
```

**Key components:**
1. **Job Store**: PostgreSQL with jobs table (id, schedule, payload, status, next_run_at)
2. **Scheduler**: Polls for due jobs, distributes to workers via queue
3. **Locking**: Distributed lock (Redis SETNX) prevents duplicate execution
4. **Timer Wheel**: Redis sorted set scored by execution time — O(log N) insertion, O(1) poll

```javascript
// Simplified scheduler loop
async function schedulerLoop() {
  while (true) {
    const now = Date.now();
    // Get jobs due for execution
    const dueJobs = await redis.zrangebyscore('scheduled_jobs', 0, now, 'LIMIT', 0, 100);
    
    for (const jobId of dueJobs) {
      // Try to claim the job (atomic)
      const claimed = await redis.set(`lock:job:${jobId}`, workerId, 'NX', 'EX', 300);
      if (claimed) {
        await jobQueue.publish(jobId);
        await redis.zrem('scheduled_jobs', jobId);
      }
    }
    
    await sleep(1000); // Poll every second
  }
}
```

**Recurring jobs:** After execution, calculate next run time and re-insert into sorted set. Handle missed executions (catch up or skip).

---

### Q10: Design a multi-tenant SaaS API with Node.js.

**Answer:**

**Requirements:** Data isolation between tenants, per-tenant rate limits, tenant-specific configuration, scalable.

**Isolation strategies:**
1. **Shared DB, shared schema** — tenant_id column on every table (cheapest, least isolation)
2. **Shared DB, separate schemas** — PostgreSQL schemas per tenant (moderate)
3. **Separate databases** — full isolation (expensive, best for compliance)

```javascript
// Middleware: resolve tenant
async function tenantMiddleware(req, res, next) {
  const tenantId = req.headers['x-tenant-id'] || extractFromSubdomain(req);
  const tenant = await tenantCache.get(tenantId);
  if (!tenant) return res.status(404).json({ error: 'Tenant not found' });
  
  req.tenant = tenant;
  // Set DB connection for this tenant
  req.db = await getConnectionForTenant(tenant);
  next();
}

// Connection per schema (RLS or schema-based)
async function getConnectionForTenant(tenant) {
  const pool = pools.get(tenant.id) || createPool(tenant.dbConfig);
  const conn = await pool.connect();
  await conn.query(`SET search_path TO tenant_${tenant.id}`);
  return conn;
}
```

**Per-tenant features:** config in tenant table, feature flags, custom rate limits, usage metering for billing.

---

### Q11: How would you migrate a monolith to microservices using Node.js?

**Answer:**

**Strategy (Strangler Fig pattern):**
1. Identify bounded contexts (User, Order, Payment, Inventory)
2. Extract one service at a time (start with least coupled)
3. Proxy pattern: new API gateway routes to new service OR old monolith
4. Shared database → Database per service (hardest part)
5. Events for inter-service communication

**Steps:**
```
Phase 1: Add API Gateway (route all traffic through it)
Phase 2: Extract User Service (easiest, few dependencies)
Phase 3: Extract Payment Service (clear boundary)
Phase 4: Event bus for eventual consistency between services
Phase 5: Extract Order Service (depends on others → events)
Phase 6: Decommission monolith
```

**Key challenges:** distributed transactions (saga pattern), data consistency (eventual), shared libraries (extract npm packages), testing (contract tests), deployment (CI/CD per service).

---

## 📚 Production Scenario Questions

### Q12: Your Node.js API suddenly has 10x latency. How do you diagnose?

**Answer:**
1. **Check metrics dashboard**: which endpoints? All or specific?
2. **Event loop lag**: if high → CPU-bound issue (blocked loop)
3. **Database**: slow queries? Connection pool exhausted? Run `EXPLAIN ANALYZE`
4. **External services**: circuit breaker stats, timeout increases?
5. **Memory**: GC pauses? Check heap usage trend
6. **Network**: DNS resolution? Connection limits?
7. **Load**: sudden traffic spike? Check request rate
8. **Recent deploy**: rollback and verify

Tools: `clinic doctor`, Datadog APM traces, database slow query log, `process.hrtime()` for timing, heap snapshot if memory suspected.

---

### Q13: How do you handle secrets management in Node.js applications?

**Answer:**
Never in code or environment files committed to git.

Hierarchy:
1. **Development**: `.env` file (gitignored) + `dotenv` package
2. **CI/CD**: Platform secrets (GitHub Actions secrets, GitLab CI variables)
3. **Production**: 
   - AWS: Secrets Manager / SSM Parameter Store
   - GCP: Secret Manager
   - Azure: Key Vault
   - K8s: External Secrets Operator → Kubernetes Secrets

```javascript
// Validate all secrets at startup (fail fast)
const required = ['DATABASE_URL', 'JWT_SECRET', 'STRIPE_KEY'];
for (const key of required) {
  if (!process.env[key]) {
    throw new Error(`Missing required env: ${key}`);
  }
}
```

Rotation: use SDK to fetch from secret manager (auto-rotates), never embed long-lived secrets in containers.

---

### Q14: Your application is running out of memory in production. What do you do?

**Answer:**

**Immediate:**
1. Check if it's a memory leak or legitimate growth
2. `process.memoryUsage()` → compare heapUsed vs external vs arrayBuffers
3. Take heap snapshot: `kill -USR2 <pid>` (if configured with `--heapsnapshot-signal`)

**Analysis:**
- Compare 3 heap snapshots over time (Chrome DevTools → Memory tab)
- Look for: growing object counts, large retained sizes
- Check event listener counts: `emitter.listenerCount()`
- Check timers: uncleared setIntervals

**Common fixes:**
- Add LRU eviction to caches (`lru-cache` package)
- Stream large responses instead of buffering
- Remove event listeners properly
- Fix closure references holding large objects
- Set `--max-old-space-size` if legitimately needs more memory

---

## 🧪 Behavioral / Scenario Questions

### Q15: Tell me about a time you optimized a Node.js application.

**Framework for answering (STAR):**
- **Situation**: API response time was 2s for product listing endpoint
- **Task**: Reduce to <200ms
- **Action**: Profiled with clinic.js → found N+1 queries, added Redis caching, implemented DataLoader for batch DB queries
- **Result**: p95 latency dropped from 2s to 80ms, database load reduced 70%

### Q16: How do you decide between Node.js and other technologies for a project?

**Choose Node.js when:**
- I/O bound (APIs, proxies, gateways)
- Real-time (WebSockets, chat, collaboration)
- Microservices (lightweight, fast startup)
- Full-stack JavaScript team
- Streaming data processing

**Consider alternatives when:**
- Heavy CPU computation (Go, Rust, C++)
- Data science/ML (Python)
- Enterprise with complex type system (Java, C#)
- System-level programming (Rust, C)

---

## 🛠️ Practice Strategy
1. Explain each concept in 30 seconds (elevator pitch)
2. Draw architecture diagrams on whiteboard
3. Write code snippets from memory
4. Discuss trade-offs for every decision
5. Practice with a timer (system design: 35 min)
