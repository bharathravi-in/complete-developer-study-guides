# Day 29: Interview Questions — Core & Intermediate

## 🎯 Learning Objectives
- Master frequently asked Node.js interview questions
- Understand answers at depth (not just surface level)
- Practice explaining concepts clearly and concisely

---

## 📚 Core Node.js Questions

### Q1: Explain the Node.js event loop and its phases.

**Answer:**
The event loop is Node.js's mechanism for handling asynchronous operations on a single thread. It has 6 phases:

1. **Timers** — Execute `setTimeout`/`setInterval` callbacks whose threshold has elapsed
2. **Pending callbacks** — Execute I/O callbacks deferred from previous iteration (e.g., TCP errors)
3. **Idle/Prepare** — Internal use only
4. **Poll** — Retrieve new I/O events, execute I/O callbacks (most code runs here). Blocks here if no timers pending
5. **Check** — Execute `setImmediate()` callbacks
6. **Close callbacks** — Execute close handlers (e.g., `socket.on('close', ...)`)

Between phases: process `nextTick` queue and microtasks (resolved Promises).

**Priority order:** process.nextTick > Promise.then > setTimeout(0) > setImmediate

**Key insight:** The event loop enables non-blocking I/O by offloading operations to the OS/libuv thread pool, then executing callbacks when results are ready.

---

### Q2: What is the difference between `process.nextTick()` and `setImmediate()`?

**Answer:**
- `process.nextTick()`: Fires between event loop phases (before any I/O). Recursive nextTick can starve I/O.
- `setImmediate()`: Fires in the **Check** phase (after Poll). Allows I/O to proceed.

```javascript
setImmediate(() => console.log('1: setImmediate'));
process.nextTick(() => console.log('2: nextTick'));
Promise.resolve().then(() => console.log('3: Promise'));
// Output: 2: nextTick → 3: Promise → 1: setImmediate
```

**When to use:** `nextTick` for critical synchronous follow-up (rare). `setImmediate` for deferring non-critical work without blocking I/O.

---

### Q3: How does Node.js handle concurrency if it's single-threaded?

**Answer:**
Node.js uses a single thread for JavaScript execution but leverages:
- **libuv thread pool** (4 threads default): DNS lookups, file system, crypto, compression
- **OS-level async I/O**: Network operations (epoll on Linux, kqueue on macOS)
- **Worker Threads**: CPU-intensive tasks in separate threads
- **Cluster module**: Multiple processes sharing a port

The event loop coordinates callbacks from all sources on the main thread. This is why blocking the main thread (CPU work > 50ms) is dangerous — it blocks all connections.

---

### Q4: Explain streams in Node.js. What are the types?

**Answer:**
Streams process data in chunks (vs loading entirely in memory). Types:

1. **Readable** — Source of data (fs.createReadStream, HTTP request)
2. **Writable** — Destination (fs.createWriteStream, HTTP response)
3. **Duplex** — Both (TCP socket, WebSocket)
4. **Transform** — Modify data in transit (zlib.createGzip, crypto.createCipher)

Key concepts: backpressure (writable signals "slow down"), pipe chains (`readable.pipe(transform).pipe(writable)`), flowing vs paused mode.

```javascript
const { pipeline } = require('stream/promises');
await pipeline(
  fs.createReadStream('huge.csv'),
  csv.parse({ columns: true }),
  async function* (source) { for await (const row of source) yield transform(row); },
  fs.createWriteStream('output.json')
);
```

---

### Q5: What is the module system in Node.js? Compare CommonJS and ESM.

**Answer:**

| Feature | CommonJS | ESM |
|---------|----------|-----|
| Syntax | `require()` / `module.exports` | `import` / `export` |
| Loading | Synchronous | Asynchronous |
| Evaluation | Dynamic (runtime) | Static (parse time) |
| Tree-shaking | No | Yes |
| Top-level await | No | Yes |
| `this` in module | `exports` | `undefined` |

Modules are cached after first load (singleton behavior). ESM is the future standard. Use `"type": "module"` in package.json for ESM.

---

### Q6: How does error handling work in Node.js?

**Answer:**
Multiple mechanisms:
1. **Sync code**: try/catch
2. **Callbacks**: Error-first pattern `(err, result) => {}`
3. **Promises**: `.catch()` or try/catch with `await`
4. **EventEmitters**: `emitter.on('error', handler)` — unhandled = crash
5. **Global**: `process.on('uncaughtException')`, `process.on('unhandledRejection')`

Best practices:
- Always catch Promise rejections
- Use custom error classes (operational vs programmer errors)
- Crash on programmer errors (let process manager restart)
- Never swallow errors silently

---

### Q7: What is middleware in Express? How does it work?

**Answer:**
Middleware functions have access to `(req, res, next)`. They execute sequentially in order registered.

Types:
- **Application-level**: `app.use(fn)` — runs on every request
- **Router-level**: `router.use(fn)` — scoped to router
- **Error-handling**: `(err, req, res, next)` — 4 parameters
- **Built-in**: `express.json()`, `express.static()`
- **Third-party**: cors, helmet, morgan

Execution: each middleware calls `next()` to pass control, or sends a response to terminate the chain. This is the Chain of Responsibility pattern.

---

### Q8: How do you prevent memory leaks in Node.js?

**Answer:**
Common sources:
1. **Global variables** accumulating data (arrays, maps never cleared)
2. **Event listeners** added but never removed
3. **Closures** holding references to large objects
4. **Unresolved Promises** keeping references alive
5. **Timers** (`setInterval` not cleared)

Prevention:
- Use WeakMap/WeakSet for caches (GC-friendly)
- Always remove event listeners (`removeListener`, `once`)
- Bound cache sizes (LRU eviction)
- Monitor with `process.memoryUsage()` and `--inspect` heap snapshots
- Use `clinic.js` or `--heapsnapshot-signal` for profiling

---

### Q9: Explain the difference between `spawn`, `exec`, and `fork`.

**Answer:**
All create child processes:

| Method | Use Case | Output | Shell |
|--------|----------|--------|-------|
| `spawn` | Long-running, streaming output | Stream | No |
| `exec` | Short commands, need full output | Buffer (200KB limit) | Yes |
| `fork` | Node.js processes with IPC | Stream + messages | No |

```javascript
const { spawn, exec, fork } = require('child_process');

spawn('ls', ['-la']);           // Streaming, no shell
exec('ls -la | grep txt');     // Shell, buffered
fork('./worker.js');           // Node process with IPC channel
```

`fork` enables `process.send()` / `process.on('message')` communication.

---

## 📚 Express & API Questions

### Q10: How do you handle authentication in a Node.js API?

**Answer:**
Common strategies:
1. **JWT (stateless)**: Sign token on login → client sends in Authorization header → verify on each request
2. **Session (stateful)**: Store session in Redis → send session ID as cookie
3. **OAuth 2.0**: Delegate to identity provider (Google, GitHub)

JWT flow:
```javascript
// Login: validate credentials → sign token
const token = jwt.sign({ userId, role }, secret, { expiresIn: '15m' });
const refreshToken = jwt.sign({ userId }, refreshSecret, { expiresIn: '7d' });

// Protected route: verify token
const decoded = jwt.verify(token, secret); // throws if expired/invalid
```

Security: short-lived access tokens (15min), refresh tokens (7 days, stored in DB, revocable), httpOnly cookies for tokens, HTTPS only.

---

### Q11: What is CORS and how do you configure it?

**Answer:**
Cross-Origin Resource Sharing: browser security mechanism that restricts cross-origin HTTP requests. Server must explicitly allow origins.

```javascript
const cors = require('cors');
app.use(cors({
  origin: ['https://myapp.com', 'https://admin.myapp.com'],
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  credentials: true,           // Allow cookies
  maxAge: 86400               // Preflight cache (24h)
}));
```

Preflight: browser sends OPTIONS request for non-simple requests (custom headers, PUT/DELETE). Server responds with allowed origins/methods. If mismatch → browser blocks request.

---

### Q12: How do you validate request input in Express?

**Answer:**
Never trust client input. Validate at API boundary:

```javascript
const { z } = require('zod');

const createUserSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
  age: z.number().int().min(13).max(120).optional(),
  role: z.enum(['user', 'admin']).default('user')
});

// Middleware
function validate(schema) {
  return (req, res, next) => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({ errors: result.error.flatten() });
    }
    req.body = result.data; // Use parsed/sanitized data
    next();
  };
}

app.post('/users', validate(createUserSchema), createUser);
```

---

## 📚 Database Questions

### Q13: How do you handle database connection pooling?

**Answer:**
Opening a new connection per request is expensive. Pool maintains reusable connections:

```javascript
const { Pool } = require('pg');
const pool = new Pool({
  max: 20,                    // Max connections in pool
  idleTimeoutMillis: 30000,   // Close idle connections after 30s
  connectionTimeoutMillis: 5000 // Fail if can't connect in 5s
});

// Connections automatically returned to pool after query
const result = await pool.query('SELECT * FROM users WHERE id = $1', [userId]);
```

Sizing: `pool size = (core_count * 2) + effective_spindle_count`. For Node.js: 10-30 connections typical (single process). Too large pool → database overwhelmed. Too small → requests queued.

---

### Q14: Explain database transactions and when to use them.

**Answer:**
Transaction: group of operations that either ALL succeed or ALL rollback. ACID guarantees.

```javascript
const client = await pool.connect();
try {
  await client.query('BEGIN');
  await client.query('UPDATE accounts SET balance = balance - $1 WHERE id = $2', [100, fromId]);
  await client.query('UPDATE accounts SET balance = balance + $1 WHERE id = $2', [100, toId]);
  await client.query('COMMIT');
} catch (error) {
  await client.query('ROLLBACK');
  throw error;
} finally {
  client.release();
}
```

Use when: money transfers, inventory operations, any multi-step operation where partial completion is invalid.

---

## 🧪 Quick-Fire Round

| Question | Key Answer |
|----------|------------|
| What is `package-lock.json`? | Locks exact dependency versions for reproducible installs |
| Difference between `dependencies` and `devDependencies`? | devDeps only needed for development (tests, linters), not in production |
| What is event-driven architecture? | System components communicate via events rather than direct calls |
| How to handle file uploads? | multer middleware, stream to S3, limit file size |
| What is clustering? | Running multiple Node.js processes sharing same port for multi-core utilization |
| How to debug Node.js? | `--inspect` flag + Chrome DevTools, VS Code debugger, `console.time` |
| What is `Buffer`? | Fixed-size memory allocation for binary data outside V8 heap |
| What does `npm audit` do? | Scans dependencies for known security vulnerabilities |

---

## 🛠️ Practice
For each question:
1. Explain the concept (30 seconds)
2. Give a real-world example
3. Discuss trade-offs or caveats
4. Write code if applicable
