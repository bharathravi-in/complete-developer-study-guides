# Day 6: Events, Buffers & Process

## 🎯 Learning Objectives
- Master the EventEmitter pattern
- Understand Buffers and binary data handling
- Learn process management and signals
- Work with environment variables and CLI args

---

## 📚 EventEmitter

The EventEmitter is the backbone of Node.js — streams, HTTP server, and most core modules extend it.

### Basic Usage

```javascript
const { EventEmitter } = require('events');

class OrderSystem extends EventEmitter {
  placeOrder(order) {
    // Business logic
    this.emit('order:placed', order);
    
    setTimeout(() => {
      this.emit('order:shipped', { ...order, trackingId: 'TRK123' });
    }, 2000);
  }
}

const orders = new OrderSystem();

// Register listeners
orders.on('order:placed', (order) => {
  console.log(`📧 Sending confirmation for order ${order.id}`);
});

orders.on('order:placed', (order) => {
  console.log(`📊 Updating analytics for order ${order.id}`);
});

orders.on('order:shipped', (order) => {
  console.log(`🚚 Tracking: ${order.trackingId}`);
});

// One-time listener
orders.once('order:placed', () => {
  console.log('🎉 First order celebration!');
});

orders.placeOrder({ id: 1, item: 'Laptop', qty: 1 });
```

### Advanced EventEmitter Patterns

```javascript
const { EventEmitter } = require('events');

const emitter = new EventEmitter();

// Set max listeners (default 10 — warns about memory leaks)
emitter.setMaxListeners(20);

// Error handling (MUST have 'error' listener or process crashes)
emitter.on('error', (err) => {
  console.error('Error occurred:', err.message);
});

// Get listener count
console.log(emitter.listenerCount('data'));

// Remove listeners
const handler = (data) => console.log(data);
emitter.on('data', handler);
emitter.off('data', handler); // or removeListener

// Remove all listeners for an event
emitter.removeAllListeners('data');

// Prepend listener (runs first)
emitter.prependListener('data', () => console.log('I run first!'));

// Async event handling with EventEmitter
const { on } = require('events');

async function processEvents() {
  const emitter = new EventEmitter();
  
  // Start emitting
  setTimeout(() => emitter.emit('data', { value: 1 }), 100);
  setTimeout(() => emitter.emit('data', { value: 2 }), 200);
  setTimeout(() => emitter.emit('close'), 300);
  
  // Async iteration over events
  for await (const [event] of on(emitter, 'data', { signal: AbortSignal.timeout(5000) })) {
    console.log('Received:', event);
  }
}
```

### EventEmitter vs Observable Pattern

```javascript
// EventEmitter: Node.js native, simple pub/sub
// Observable (RxJS): Lazy, composable, has operators

// When to use EventEmitter:
// - Internal module communication
// - Simple event-driven patterns
// - When you don't need complex transformations

// When to use Observables:
// - Complex data transformations
// - Backpressure handling
// - Cancellation semantics
```

---

## 🧱 Buffers

Buffers handle raw binary data — essential for files, network packets, cryptography.

```javascript
// Creating Buffers
const buf1 = Buffer.alloc(10);           // 10 zero-filled bytes
const buf2 = Buffer.from('Hello');        // From string (UTF-8)
const buf3 = Buffer.from([0x48, 0x65]);   // From byte array
const buf4 = Buffer.from('SGVsbG8=', 'base64'); // From base64

// Reading/Writing
const buf = Buffer.alloc(256);
buf.write('Hello World');
console.log(buf.toString('utf-8', 0, 11)); // 'Hello World'
console.log(buf.toString('hex', 0, 5));     // '48656c6c6f'
console.log(buf.toString('base64'));        // Base64 encoding

// Binary operations
buf.writeUInt32BE(0x12345678, 0); // Write 4-byte big-endian integer
buf.readUInt32BE(0);               // Read it back: 305419896

// Comparison and search
Buffer.compare(buf1, buf2);  // -1, 0, or 1
buf.includes('Hello');       // true
buf.indexOf('World');        // byte offset

// Concatenation
const combined = Buffer.concat([buf1, buf2, buf3]);

// Slicing (shares memory!)
const slice = buf.slice(0, 5); // Modifying slice modifies buf!
const copy = Buffer.from(buf.slice(0, 5)); // Safe copy

// Buffer pooling - allocUnsafe is faster but contains old memory
const fast = Buffer.allocUnsafe(1024); // MUST fill before reading!
fast.fill(0); // Now safe
```

### Practical Buffer Usage

```javascript
// Parse binary protocol (e.g., custom TCP message)
function parseMessage(buf) {
  return {
    version: buf.readUInt8(0),
    type: buf.readUInt16BE(1),
    length: buf.readUInt32BE(3),
    payload: buf.slice(7, 7 + buf.readUInt32BE(3))
  };
}

// Base64 encode/decode
const encoded = Buffer.from('secret data').toString('base64');
const decoded = Buffer.from(encoded, 'base64').toString('utf-8');

// Hex operations (useful for crypto, colors)
const hash = Buffer.from('a1b2c3d4', 'hex');
console.log(hash.toString('hex')); // 'a1b2c3d4'
```

---

## ⚙️ Process Management

```javascript
// Process info
console.log(process.pid);        // Process ID
console.log(process.ppid);       // Parent process ID
console.log(process.platform);   // 'linux', 'darwin', 'win32'
console.log(process.arch);       // 'x64', 'arm64'
console.log(process.version);    // 'v20.10.0'
console.log(process.versions);   // V8, OpenSSL, libuv versions
console.log(process.uptime());   // Seconds since start

// Memory usage
const mem = process.memoryUsage();
console.log({
  rss: `${(mem.rss / 1024 / 1024).toFixed(1)} MB`,       // Resident Set Size
  heapTotal: `${(mem.heapTotal / 1024 / 1024).toFixed(1)} MB`,
  heapUsed: `${(mem.heapUsed / 1024 / 1024).toFixed(1)} MB`,
  external: `${(mem.external / 1024 / 1024).toFixed(1)} MB`
});

// CPU usage
const startUsage = process.cpuUsage();
// ... do work ...
const elapsed = process.cpuUsage(startUsage);
console.log(`User CPU: ${elapsed.user / 1000}ms, System CPU: ${elapsed.system / 1000}ms`);

// High-resolution timing
const start = process.hrtime.bigint();
// ... do work ...
const end = process.hrtime.bigint();
console.log(`Took ${Number(end - start) / 1e6}ms`);
```

### Environment Variables & CLI Args

```javascript
// Environment variables
const port = process.env.PORT || 3000;
const nodeEnv = process.env.NODE_ENV || 'development';
const dbUrl = process.env.DATABASE_URL;

// Never log sensitive env vars!
// Use .env files with dotenv for development

// CLI arguments
// node app.js --port 3000 --verbose
console.log(process.argv);
// ['/usr/bin/node', '/app/app.js', '--port', '3000', '--verbose']

// Simple arg parser
function parseArgs(args) {
  const parsed = {};
  for (let i = 2; i < args.length; i++) {
    if (args[i].startsWith('--')) {
      const key = args[i].slice(2);
      const next = args[i + 1];
      parsed[key] = (!next || next.startsWith('--')) ? true : args[++i];
    }
  }
  return parsed;
}
const opts = parseArgs(process.argv);
// { port: '3000', verbose: true }

// Node.js 18+ built-in arg parser
const { parseArgs: nodeParseArgs } = require('util');
const { values } = nodeParseArgs({
  options: {
    port: { type: 'string', short: 'p', default: '3000' },
    verbose: { type: 'boolean', short: 'v' }
  }
});
```

### Signal Handling

```javascript
// SIGTERM: Graceful shutdown (from kill, Docker stop, Kubernetes)
process.on('SIGTERM', () => {
  console.log('SIGTERM received. Shutting down gracefully...');
  server.close(() => {
    db.disconnect();
    process.exit(0);
  });
  // Force exit if graceful shutdown takes too long
  setTimeout(() => process.exit(1), 10000);
});

// SIGINT: Ctrl+C in terminal
process.on('SIGINT', () => {
  console.log('\nCaught interrupt signal');
  process.exit(0);
});

// Exit handler (runs on any exit)
process.on('exit', (code) => {
  // Only synchronous code here!
  console.log(`Process exiting with code: ${code}`);
});

// beforeExit: When event loop is empty (NOT on process.exit())
process.on('beforeExit', (code) => {
  // Can schedule async work here (keeps process alive)
});
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is the EventEmitter and why is it important in Node.js?**

EventEmitter is the foundation of Node.js's event-driven architecture. It implements the observer/pub-sub pattern. Streams, HTTP server, file watchers all extend it. It allows loose coupling — emitters don't know about listeners. Core API: `on()`, `emit()`, `once()`, `off()`.

**Q2: What is a Buffer and when would you use it?**

Buffer represents fixed-size binary data (raw memory outside V8 heap). Use it for: reading files in binary mode, handling network protocols, cryptographic operations, image processing, or any binary data manipulation. It's like a typed array but with additional methods for encoding/decoding.

**Q3: How do you access environment variables in Node.js?**

Via `process.env` object. Example: `process.env.PORT`. All values are strings (parse numbers explicitly). For local development, use `.env` files with the `dotenv` package. Never commit secrets to code — use environment variables or secret management services.

### Intermediate

**Q4: What happens if you emit an 'error' event with no listener?**

The process crashes with an uncaught exception. This is by design — unhandled errors should fail loudly. Always attach an `error` listener: `emitter.on('error', handler)`. Alternatively, use `events.captureRejections = true` for async event handlers (Node 13+).

**Q5: Explain the difference between `Buffer.alloc()` and `Buffer.allocUnsafe()`.**

`alloc()` zero-fills the memory (safe, slightly slower). `allocUnsafe()` skips zeroing — the buffer may contain old data from previous allocations (potential security leak). Use `allocUnsafe()` only when you'll immediately overwrite all bytes (performance-critical code). Never send uninitialized buffers over network.

**Q6: How would you implement a pub/sub system using EventEmitter?**

Create a central EventEmitter instance (message bus). Publishers emit events with payloads. Subscribers listen for specific events. Add namespacing (`user:created`), wildcard matching, and dead letter handling. For distributed systems, replace with Redis Pub/Sub or message queues.

### Advanced

**Q7: How does Node.js handle memory for Buffers vs regular objects?**

Buffers are allocated outside V8's heap (in C++ memory). Small buffers (< 8KB) use a shared pre-allocated pool (`Buffer.poolSize = 8192`). Large buffers get their own allocation. This means Buffer memory isn't tracked by V8's GC — monitor with `process.memoryUsage().external`. Buffer pools can cause unexpected memory retention.

**Q8: Explain the performance implications of EventEmitter listener count.**

Each `emit()` iterates all listeners synchronously. Many listeners per event = linear slowdown. Memory leak warning at 11+ listeners (usually indicates missing `off()`). For high-frequency events (e.g., stream `data`), excessive listeners compound. Use `setMaxListeners()` judiciously and profile with `listenerCount()`.

**Q9: How would you design a graceful shutdown that handles in-flight requests, database connections, and message queue consumers?**

1. Stop accepting new connections (`server.close()`)
2. Signal health checks as unhealthy (load balancer drains)
3. Wait for in-flight requests (track with counter)
4. Stop consuming messages, finish current processing
5. Close database connection pools
6. Flush logs and metrics
7. Set hard timeout (30s) for force exit
8. Exit with code 0 (or 1 on timeout)

---

## 🛠️ Hands-on Exercise

Build an event-driven task queue:
1. TaskQueue extends EventEmitter
2. Emits: `task:added`, `task:started`, `task:completed`, `task:failed`
3. Processes tasks with concurrency limit
4. Tracks statistics (processed, failed, avg time)
5. Supports graceful shutdown (finish current tasks, reject new ones)
