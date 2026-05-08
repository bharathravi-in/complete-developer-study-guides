# Day 18: Performance Optimization & Monitoring

## 🎯 Learning Objectives
- Profile and optimize Node.js applications
- Implement APM and monitoring
- Understand memory leaks and how to fix them
- Master performance best practices

---

## 📚 Performance Profiling

### CPU Profiling

```javascript
// Built-in profiler
// node --prof app.js
// node --prof-process isolate-*.log > processed.txt

// V8 Inspector (Chrome DevTools)
// node --inspect app.js
// Open chrome://inspect

// Programmatic profiling
const { Session } = require('inspector');
const fs = require('fs');

function startProfiling() {
  const session = new Session();
  session.connect();
  session.post('Profiler.enable');
  session.post('Profiler.start');
  
  return () => {
    return new Promise((resolve) => {
      session.post('Profiler.stop', (err, { profile }) => {
        fs.writeFileSync('profile.cpuprofile', JSON.stringify(profile));
        session.disconnect();
        resolve();
      });
    });
  };
}

// Profile a specific route
app.get('/heavy-endpoint', async (req, res) => {
  const stop = startProfiling();
  // ... your code ...
  await stop();
  res.json({ profiled: true });
});
```

### Memory Profiling

```javascript
// Heap snapshot
const v8 = require('v8');
const fs = require('fs');

function takeHeapSnapshot() {
  const filename = `heap-${Date.now()}.heapsnapshot`;
  const stream = v8.writeHeapSnapshot(filename);
  console.log(`Heap snapshot written to ${stream}`);
}

// Detect memory leaks - track heap growth
function monitorMemory() {
  let lastHeap = 0;
  setInterval(() => {
    const { heapUsed } = process.memoryUsage();
    const growth = heapUsed - lastHeap;
    if (growth > 10 * 1024 * 1024) { // >10MB growth
      console.warn(`Possible memory leak: heap grew ${(growth / 1024 / 1024).toFixed(1)}MB`);
      takeHeapSnapshot();
    }
    lastHeap = heapUsed;
  }, 30000);
}

// Common memory leak patterns
// ❌ Leak: Growing event listener count
emitter.on('data', handler); // Without ever removing

// ❌ Leak: Closures holding references
function createLeak() {
  const hugeArray = new Array(1000000).fill('x');
  return () => hugeArray.length; // hugeArray can never be GC'd
}

// ❌ Leak: Unbounded caches
const cache = {}; // Grows forever
cache[key] = value;

// ✅ Fix: Use LRU cache with max size
const LRU = require('lru-cache');
const cache = new LRU({ max: 1000, ttl: 60000 });
```

---

## 📊 Event Loop Monitoring

```javascript
const { monitorEventLoopDelay } = require('perf_hooks');

// Monitor event loop lag
const histogram = monitorEventLoopDelay({ resolution: 20 });
histogram.enable();

setInterval(() => {
  console.log({
    min: histogram.min / 1e6,     // ms
    max: histogram.max / 1e6,
    mean: histogram.mean / 1e6,
    p99: histogram.percentile(99) / 1e6,
  });
  histogram.reset();
}, 5000);

// Simple event loop lag measurement
let lastCheck = Date.now();
setInterval(() => {
  const now = Date.now();
  const lag = now - lastCheck - 1000; // Expected 1000ms interval
  if (lag > 100) {
    console.warn(`Event loop lag: ${lag}ms`);
  }
  lastCheck = now;
}, 1000);
```

---

## ⚡ Optimization Techniques

### Response Compression

```javascript
const compression = require('compression');

app.use(compression({
  filter: (req, res) => {
    if (req.headers['x-no-compression']) return false;
    return compression.filter(req, res);
  },
  threshold: 1024, // Only compress responses > 1KB
  level: 6         // Compression level (1-9, 6 is balanced)
}));
```

### Database Query Optimization

```javascript
// ❌ N+1 problem
const users = await User.find();
for (const user of users) {
  user.posts = await Post.find({ author: user.id }); // N queries!
}

// ✅ Single query with population/join
const users = await User.find().populate('posts');
// OR
const users = await User.aggregate([
  { $lookup: { from: 'posts', localField: '_id', foreignField: 'author', as: 'posts' } }
]);

// ✅ Select only needed fields
const users = await User.find().select('name email').lean();

// ✅ Use indexes
// db.users.createIndex({ email: 1 }, { unique: true })
// db.posts.createIndex({ author: 1, createdAt: -1 })

// ✅ Pagination with cursor (not skip)
const posts = await Post.find({ _id: { $gt: lastId } }).limit(20);
```

### Streaming Large Responses

```javascript
// ❌ Load everything into memory
app.get('/export', async (req, res) => {
  const allData = await db.collection.find().toArray(); // May be GB of data!
  res.json(allData);
});

// ✅ Stream response
app.get('/export', async (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.write('[');
  
  const cursor = db.collection.find().cursor();
  let first = true;
  
  for await (const doc of cursor) {
    if (!first) res.write(',');
    res.write(JSON.stringify(doc));
    first = false;
  }
  
  res.write(']');
  res.end();
});
```

### JSON Serialization Optimization

```javascript
// fast-json-stringify (2-5x faster than JSON.stringify for known schemas)
const fastJson = require('fast-json-stringify');
const stringify = fastJson({
  type: 'object',
  properties: {
    id: { type: 'string' },
    name: { type: 'string' },
    email: { type: 'string' },
    createdAt: { type: 'string' }
  }
});

app.get('/users/:id', async (req, res) => {
  const user = await getUser(req.params.id);
  res.type('json').send(stringify(user)); // Faster serialization
});
```

---

## 📈 Application Monitoring (APM)

```javascript
// Custom metrics middleware
const metrics = {
  requests: { total: 0, byStatus: {}, byRoute: {} },
  responseTime: { total: 0, count: 0 },
  errors: 0
};

app.use((req, res, next) => {
  const start = process.hrtime.bigint();
  
  res.on('finish', () => {
    const duration = Number(process.hrtime.bigint() - start) / 1e6;
    metrics.requests.total++;
    metrics.requests.byStatus[res.statusCode] = (metrics.requests.byStatus[res.statusCode] || 0) + 1;
    metrics.responseTime.total += duration;
    metrics.responseTime.count++;
    if (res.statusCode >= 500) metrics.errors++;
  });
  
  next();
});

// Health check endpoint
app.get('/health', async (req, res) => {
  const health = {
    status: 'healthy',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    eventLoopLag: getEventLoopLag(),
    db: await checkDbConnection(),
    redis: await checkRedisConnection()
  };
  res.json(health);
});

// Metrics endpoint (Prometheus format)
app.get('/metrics', (req, res) => {
  const avgResponse = metrics.responseTime.count 
    ? (metrics.responseTime.total / metrics.responseTime.count).toFixed(2) 
    : 0;
  
  res.type('text/plain').send(`
# HELP http_requests_total Total HTTP requests
http_requests_total ${metrics.requests.total}
# HELP http_response_time_avg Average response time in ms
http_response_time_avg ${avgResponse}
# HELP http_errors_total Total 5xx errors
http_errors_total ${metrics.errors}
# HELP nodejs_heap_used_bytes Heap used bytes
nodejs_heap_used_bytes ${process.memoryUsage().heapUsed}
  `.trim());
});
```

---

## 🧪 Interview Questions

### Beginner

**Q1: How do you identify performance bottlenecks in a Node.js application?**

Tools: (1) `--prof` flag for CPU profiling. (2) Chrome DevTools via `--inspect`. (3) Event loop lag monitoring. (4) Response time logging per route. (5) Database query logging (slow query log). (6) Memory monitoring (`process.memoryUsage()`). Look for: slow routes, high event loop lag, growing memory.

**Q2: What causes memory leaks in Node.js?**

Common causes: (1) Event listeners added without removal. (2) Closures holding large object references. (3) Unbounded caches/arrays. (4) Uncleared timers/intervals. (5) Circular references in closures. (6) Global variables accumulating data. Detect with heap snapshots (compare two snapshots to see what's growing).

**Q3: Why is blocking the event loop bad and how do you avoid it?**

Blocking prevents all other requests from being processed (Node is single-threaded). Avoid: no `*Sync` methods in servers, no heavy computation on main thread, no large JSON.parse/stringify. Solutions: Worker Threads for CPU work, streaming for large data, chunking long loops with setImmediate.

### Intermediate

**Q4: How does connection pooling affect performance?**

Without pooling: each query creates new TCP connection (DNS + TCP handshake + TLS + auth = 50-200ms overhead). With pooling: connections are reused (query overhead = network RTT only, ~1-5ms). Pool sizing: too small = queries queue up; too large = database overwhelmed. Optimal: monitor wait times and active connections.

**Q5: What is the difference between horizontal and vertical scaling for Node.js?**

Vertical: bigger server (more CPU/RAM) — limited ceiling, single point of failure. Horizontal: more instances behind load balancer — handles more traffic, requires stateless design (no in-memory sessions). Node.js is ideal for horizontal scaling due to stateless nature. Use PM2 cluster mode or Kubernetes for orchestration.

**Q6: How would you optimize a Node.js API that handles 10,000 requests/second?**

Stack: (1) CDN/Nginx for static content and SSL termination. (2) Response caching (Redis). (3) Connection pooling (DB, Redis). (4) Compression (gzip/brotli). (5) Cluster mode (all CPU cores). (6) Efficient serialization (fast-json-stringify). (7) Stream large responses. (8) Database: proper indexes, read replicas, query optimization.

### Advanced

**Q7: Explain how V8's garbage collector works and how it affects Node.js performance.**

V8 uses generational GC: Young generation (Scavenge, frequent, fast — most objects die young) and Old generation (Mark-Sweep/Mark-Compact, infrequent, causes pauses). GC pauses block the event loop. Mitigate: avoid creating many short-lived objects in hot paths, use object pooling, pre-allocate buffers. Monitor with `--trace-gc` flag.

**Q8: How would you implement distributed tracing in a Node.js microservices architecture?**

Use OpenTelemetry: instrument each service with trace context propagation (W3C Trace Context headers). Each request gets a trace ID; each service creates spans. Export to Jaeger/Zipkin/Datadog. Context propagation: pass trace ID in HTTP headers, message queue metadata. Use AsyncLocalStorage to maintain context across async operations within a service.

**Q9: Design a load testing strategy for a Node.js application.**

Tools: k6, Artillery, or autocannon. Strategy: (1) Baseline test (normal traffic). (2) Stress test (find breaking point). (3) Spike test (sudden traffic). (4) Soak test (sustained load for memory leaks). Metrics to track: p50/p95/p99 latency, error rate, throughput, CPU/memory, event loop lag. Test against production-like environment with realistic data volumes.

---

## 🛠️ Hands-on Exercise

Profile and optimize a slow API:
1. Set up event loop lag monitoring
2. Add response time tracking per route
3. Identify and fix an N+1 query problem
4. Implement streaming for large data exports
5. Add a /metrics endpoint (Prometheus format)
6. Write a load test script with autocannon
