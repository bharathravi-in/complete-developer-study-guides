# Day 1: Node.js Architecture & Event Loop

## 🎯 Learning Objectives
- Understand Node.js architecture and why it was created
- Master the Event Loop and its phases
- Learn the difference between Node.js and browser JavaScript
- Understand V8 engine integration with libuv

---

## 📚 What is Node.js?

Node.js is a **JavaScript runtime** built on Chrome's V8 engine. It uses an **event-driven, non-blocking I/O model** that makes it lightweight and efficient.

### Key Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Node.js Architecture                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Your Code   │  │  Node.js     │  │   C++ Bindings   │  │
│  │  (JavaScript)│  │  Standard    │  │   (fs, http,     │  │
│  │              │  │  Library     │  │    crypto, etc)   │  │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                  │                    │            │
│  ┌──────┴──────────────────┴────────────────────┴─────────┐ │
│  │                    V8 Engine                            │ │
│  │            (JavaScript Execution)                       │ │
│  └────────────────────────┬───────────────────────────────┘ │
│                           │                                  │
│  ┌────────────────────────┴───────────────────────────────┐ │
│  │                    libuv                                │ │
│  │        (Event Loop + Async I/O + Thread Pool)          │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Why Node.js?

```javascript
// Traditional (blocking) server - PHP/Ruby style
// Each request = new thread (expensive)
// 10,000 concurrent users = 10,000 threads = RAM exhaustion

// Node.js (non-blocking) approach
// Single thread handles ALL connections via event loop
const http = require('http');

const server = http.createServer((req, res) => {
  // This callback fires for each request
  // But it's all on ONE thread via event loop
  res.writeHead(200, { 'Content-Type': 'text/plain' });
  res.end('Hello World\n');
});

server.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

---

## 🔄 The Event Loop

The Event Loop is the core of Node.js. It's what allows non-blocking I/O despite JavaScript being single-threaded.

### Event Loop Phases

```
   ┌───────────────────────────┐
┌─>│           timers          │  ← setTimeout, setInterval
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │     pending callbacks     │  ← I/O callbacks deferred
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │       idle, prepare       │  ← internal use only
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │           poll            │  ← retrieve new I/O events
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │           check           │  ← setImmediate
│  └─────────────┬─────────────┘
│  ┌─────────────┴─────────────┐
│  │      close callbacks      │  ← socket.on('close')
│  └─────────────┬─────────────┘
└─────────────────┘
```

### Understanding Each Phase

```javascript
// Phase 1: Timers
setTimeout(() => console.log('timeout'), 0);

// Phase 5: Check (setImmediate)
setImmediate(() => console.log('immediate'));

// Microtask Queue (runs between each phase)
Promise.resolve().then(() => console.log('promise'));
process.nextTick(() => console.log('nextTick'));

// Output order:
// nextTick (microtask - highest priority)
// promise  (microtask - after nextTick)
// timeout OR immediate (depends on system timing)
```

### process.nextTick vs setImmediate

```javascript
// process.nextTick - runs BEFORE the next event loop phase
// setImmediate - runs in the CHECK phase (after poll)

const fs = require('fs');

fs.readFile(__filename, () => {
  // Inside I/O callback (poll phase)
  setTimeout(() => console.log('timeout'), 0);
  setImmediate(() => console.log('immediate'));
  // Output: immediate ALWAYS before timeout (because we're in poll phase)
});

// Outside I/O - order is non-deterministic
setTimeout(() => console.log('timeout'), 0);
setImmediate(() => console.log('immediate'));
```

### The Thread Pool (libuv)

```javascript
const crypto = require('crypto');

// These run in the thread pool (default: 4 threads)
// NOT on the main event loop thread
const start = Date.now();

crypto.pbkdf2('password', 'salt', 100000, 512, 'sha512', () => {
  console.log('1:', Date.now() - start, 'ms');
});
crypto.pbkdf2('password', 'salt', 100000, 512, 'sha512', () => {
  console.log('2:', Date.now() - start, 'ms');
});
crypto.pbkdf2('password', 'salt', 100000, 512, 'sha512', () => {
  console.log('3:', Date.now() - start, 'ms');
});
crypto.pbkdf2('password', 'salt', 100000, 512, 'sha512', () => {
  console.log('4:', Date.now() - start, 'ms');
});
crypto.pbkdf2('password', 'salt', 100000, 512, 'sha512', () => {
  console.log('5:', Date.now() - start, 'ms'); // Takes ~2x as long (waiting for thread)
});

// Increase thread pool: UV_THREADPOOL_SIZE=8 node app.js
```

---

## 🆚 Node.js vs Browser JavaScript

| Feature | Browser | Node.js |
|---------|---------|---------|
| Global object | `window` | `global` / `globalThis` |
| DOM | ✅ | ❌ |
| File System | ❌ | ✅ (`fs` module) |
| Network (low-level) | Limited | Full (`net`, `dgram`) |
| Module system | ES Modules | CommonJS + ES Modules |
| `this` in global | `window` | `module.exports` |

```javascript
// Browser
console.log(this === window); // true

// Node.js (in module scope)
console.log(this === module.exports); // true
console.log(this === global); // false!

// Node.js (in REPL)
console.log(this === global); // true
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is Node.js and why is it single-threaded?**

Node.js is a JavaScript runtime built on V8 that uses an event-driven, non-blocking I/O model. It's single-threaded for the main execution but uses a thread pool (libuv) for heavy I/O operations. This design avoids thread-management overhead and context-switching costs.

**Q2: What is the difference between `process.nextTick()` and `setImmediate()`?**

`process.nextTick()` fires immediately after the current operation, before the event loop continues. `setImmediate()` fires in the check phase of the next event loop iteration. `nextTick` has higher priority and can starve the event loop if used recursively.

**Q3: What is libuv?**

libuv is a C library that provides the event loop, thread pool, and async I/O to Node.js. It abstracts OS-level async operations (epoll on Linux, kqueue on macOS, IOCP on Windows) into a consistent API.

### Intermediate

**Q4: Explain the 6 phases of the Node.js event loop.**

1. **Timers**: Execute `setTimeout`/`setInterval` callbacks
2. **Pending callbacks**: Execute deferred I/O callbacks
3. **Idle/Prepare**: Internal use
4. **Poll**: Retrieve new I/O events, execute I/O callbacks
5. **Check**: Execute `setImmediate` callbacks
6. **Close callbacks**: Execute close event callbacks (e.g., `socket.on('close')`)

Between each phase, microtasks (nextTick + promises) are processed.

**Q5: How does Node.js handle CPU-intensive tasks without blocking?**

Options: Worker Threads (`worker_threads` module), child processes (`child_process.fork()`), or offloading to external services. The thread pool handles some crypto/zlib operations, but custom CPU work needs explicit handling.

**Q6: What happens when you exceed the thread pool size?**

Default thread pool has 4 threads (configurable via `UV_THREADPOOL_SIZE`, max 1024). When all threads are busy, additional operations queue up, increasing latency. This affects `fs` operations, DNS lookups, and crypto operations.

### Advanced

**Q7: Explain backpressure in Node.js streams and how the event loop relates to it.**

Backpressure occurs when a writable stream can't consume data as fast as a readable stream produces it. The `write()` method returns `false` when the internal buffer exceeds `highWaterMark`. The readable stream should pause until the `drain` event fires. The event loop manages this via the poll phase, where I/O callbacks signal buffer availability.

**Q8: How would you diagnose an event loop delay in production?**

Use `monitorEventLoopDelay` (Node 11+), or measure with `process.hrtime()`. Tools: `clinic.js`, `0x` for flamegraphs. Check for: synchronous I/O, JSON.parse on large payloads, regex backtracking, or excessive `nextTick` recursion.

**Q9: Compare the Node.js event loop to the browser event loop.**

Both have microtask queues and macrotask processing, but differ in phases. Browser has rendering steps (requestAnimationFrame, style/layout/paint) between tasks. Node has distinct phases (timers, poll, check). Browser event loop is spec'd by HTML spec; Node's is implemented by libuv.

---

## 🛠️ Hands-on Exercise

Build a script that demonstrates event loop behavior:

```javascript
const fs = require('fs');

console.log('1. Script start');

setTimeout(() => console.log('2. setTimeout 0'), 0);
setImmediate(() => console.log('3. setImmediate'));

Promise.resolve().then(() => console.log('4. Promise'));
process.nextTick(() => console.log('5. nextTick'));

fs.readFile(__filename, () => {
  console.log('6. File read complete');
  setTimeout(() => console.log('7. setTimeout inside I/O'), 0);
  setImmediate(() => console.log('8. setImmediate inside I/O'));
  process.nextTick(() => console.log('9. nextTick inside I/O'));
});

console.log('10. Script end');

// Predict the output order, then run to verify!
```
