# Day 7: Child Processes & Worker Threads

## 🎯 Learning Objectives
- Understand when and how to use child processes
- Master Worker Threads for CPU-intensive tasks
- Learn the Cluster module for multi-core scaling
- Compare concurrency approaches in Node.js

---

## 📚 Child Processes

### spawn, exec, execFile, fork

```javascript
const { spawn, exec, execFile, fork } = require('child_process');

// spawn - streams stdout/stderr (best for long-running processes)
const ls = spawn('ls', ['-la', '/home']);
ls.stdout.on('data', (data) => console.log(`stdout: ${data}`));
ls.stderr.on('data', (data) => console.error(`stderr: ${data}`));
ls.on('close', (code) => console.log(`Exit code: ${code}`));

// exec - buffers output (best for short commands, has shell)
exec('cat /etc/passwd | grep root', (err, stdout, stderr) => {
  if (err) throw err;
  console.log(stdout);
});
// Promise version
const { promisify } = require('util');
const execAsync = promisify(exec);
const { stdout } = await execAsync('ls -la');

// execFile - like exec but no shell (safer, faster)
execFile('node', ['--version'], (err, stdout) => {
  console.log(stdout); // v20.x.x
});

// fork - spawns new Node.js process with IPC channel
const child = fork('./worker.js');
child.send({ task: 'processData', payload: [1, 2, 3] });
child.on('message', (result) => {
  console.log('Worker result:', result);
});
```

### fork() for CPU-Intensive Work

```javascript
// main.js
const { fork } = require('child_process');

function computeInWorker(data) {
  return new Promise((resolve, reject) => {
    const worker = fork('./heavy-compute.js');
    worker.send(data);
    worker.on('message', resolve);
    worker.on('error', reject);
    worker.on('exit', (code) => {
      if (code !== 0) reject(new Error(`Worker exited with code ${code}`));
    });
  });
}

// heavy-compute.js
process.on('message', (data) => {
  // CPU-intensive work here
  const result = fibonacci(data.n);
  process.send({ result });
  process.exit(0);
});

function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}
```

---

## 🧵 Worker Threads

Worker Threads share memory (via SharedArrayBuffer) and are lighter than child processes.

```javascript
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

if (isMainThread) {
  // Main thread
  function runWorker(data) {
    return new Promise((resolve, reject) => {
      const worker = new Worker(__filename, { workerData: data });
      worker.on('message', resolve);
      worker.on('error', reject);
      worker.on('exit', (code) => {
        if (code !== 0) reject(new Error(`Worker stopped with exit code ${code}`));
      });
    });
  }
  
  async function main() {
    const results = await Promise.all([
      runWorker({ start: 0, end: 25000000 }),
      runWorker({ start: 25000000, end: 50000000 }),
      runWorker({ start: 50000000, end: 75000000 }),
      runWorker({ start: 75000000, end: 100000000 }),
    ]);
    console.log('Total:', results.reduce((a, b) => a + b, 0));
  }
  main();
  
} else {
  // Worker thread
  const { start, end } = workerData;
  let sum = 0;
  for (let i = start; i < end; i++) {
    sum += i;
  }
  parentPort.postMessage(sum);
}
```

### SharedArrayBuffer for Zero-Copy Communication

```javascript
const { Worker, isMainThread } = require('worker_threads');

if (isMainThread) {
  // Shared memory between main and worker
  const sharedBuffer = new SharedArrayBuffer(4 * 1024); // 4KB
  const sharedArray = new Int32Array(sharedBuffer);
  
  const worker = new Worker(__filename, {
    workerData: { sharedBuffer }
  });
  
  // Both threads can read/write this memory
  // Use Atomics for thread-safe operations
  Atomics.store(sharedArray, 0, 42);
  Atomics.notify(sharedArray, 0); // Wake worker waiting on this index
  
  worker.on('message', () => {
    console.log('Value from worker:', Atomics.load(sharedArray, 0));
  });
  
} else {
  const { sharedBuffer } = require('worker_threads').workerData;
  const sharedArray = new Int32Array(sharedBuffer);
  
  // Wait for main thread to write
  Atomics.wait(sharedArray, 0, 0); // Blocks until value !== 0
  
  // Modify shared memory
  Atomics.add(sharedArray, 0, 8); // Atomic add: 42 + 8 = 50
  
  parentPort.postMessage('done');
}
```

### Worker Thread Pool Pattern

```javascript
const { Worker } = require('worker_threads');
const os = require('os');

class WorkerPool {
  constructor(workerFile, poolSize = os.cpus().length) {
    this.workerFile = workerFile;
    this.poolSize = poolSize;
    this.workers = [];
    this.freeWorkers = [];
    this.taskQueue = [];
    
    for (let i = 0; i < poolSize; i++) {
      this.addNewWorker();
    }
  }
  
  addNewWorker() {
    const worker = new Worker(this.workerFile);
    worker.on('message', (result) => {
      worker.currentResolve(result);
      worker.currentResolve = null;
      this.freeWorkers.push(worker);
      this.processNext();
    });
    worker.on('error', (err) => {
      if (worker.currentReject) worker.currentReject(err);
      // Replace dead worker
      this.workers = this.workers.filter(w => w !== worker);
      this.addNewWorker();
    });
    this.workers.push(worker);
    this.freeWorkers.push(worker);
  }
  
  runTask(data) {
    return new Promise((resolve, reject) => {
      this.taskQueue.push({ data, resolve, reject });
      this.processNext();
    });
  }
  
  processNext() {
    if (this.taskQueue.length === 0 || this.freeWorkers.length === 0) return;
    const worker = this.freeWorkers.pop();
    const { data, resolve, reject } = this.taskQueue.shift();
    worker.currentResolve = resolve;
    worker.currentReject = reject;
    worker.postMessage(data);
  }
  
  destroy() {
    for (const worker of this.workers) {
      worker.terminate();
    }
  }
}

// Usage
const pool = new WorkerPool('./compute-worker.js', 4);
const results = await Promise.all([
  pool.runTask({ n: 40 }),
  pool.runTask({ n: 41 }),
  pool.runTask({ n: 42 }),
]);
pool.destroy();
```

---

## 🏭 Cluster Module

Scale across CPU cores with the cluster module:

```javascript
const cluster = require('cluster');
const http = require('http');
const os = require('os');

if (cluster.isPrimary) {
  const numCPUs = os.cpus().length;
  console.log(`Primary ${process.pid} forking ${numCPUs} workers`);
  
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  
  cluster.on('exit', (worker, code, signal) => {
    console.log(`Worker ${worker.process.pid} died (${signal || code})`);
    cluster.fork(); // Replace dead worker
  });
  
  // Graceful restart
  process.on('SIGUSR2', () => {
    const workers = Object.values(cluster.workers);
    function restartWorker(index) {
      if (index >= workers.length) return;
      const worker = workers[index];
      worker.disconnect();
      worker.on('disconnect', () => {
        const newWorker = cluster.fork();
        newWorker.on('listening', () => restartWorker(index + 1));
      });
    }
    restartWorker(0);
  });
  
} else {
  const server = http.createServer((req, res) => {
    res.writeHead(200);
    res.end(`Worker ${process.pid} handled this request\n`);
  });
  server.listen(3000);
  console.log(`Worker ${process.pid} started`);
}
```

---

## 🆚 Comparison: When to Use What

| Approach | Use Case | Overhead | Communication |
|----------|----------|----------|---------------|
| **Worker Threads** | CPU-intensive JS (crypto, image processing) | Low (shared memory) | `postMessage`, SharedArrayBuffer |
| **child_process.fork()** | Separate Node.js processes, isolation needed | Medium (IPC) | JSON messages via IPC |
| **child_process.spawn()** | Run external programs (ffmpeg, git) | Medium | stdin/stdout streams |
| **Cluster** | Scale HTTP servers across CPU cores | High (per-process) | Limited IPC |
| **Thread Pool (libuv)** | Built-in (fs, crypto, dns) | Managed by Node | Callbacks |

---

## 🧪 Interview Questions

### Beginner

**Q1: What is the difference between child processes and worker threads?**

Child processes are separate OS processes with their own memory space and V8 instance. Worker threads share the same process and can share memory (SharedArrayBuffer). Child processes have higher overhead but better isolation. Worker threads are better for CPU-intensive JS tasks.

**Q2: When would you use `spawn()` vs `exec()` vs `fork()`?**

`spawn()`: Long-running processes with large output (streaming). `exec()`: Short commands where you need shell features (pipes, wildcards) — buffers all output. `fork()`: Spawning new Node.js processes with IPC communication. Use `execFile()` for running specific executables without shell overhead.

**Q3: What is the Cluster module used for?**

Cluster creates multiple Node.js processes sharing the same port. The primary process forks workers (typically one per CPU core). Incoming connections are distributed among workers (round-robin on Linux). This utilizes all CPU cores for HTTP servers since Node.js is single-threaded.

### Intermediate

**Q4: How does SharedArrayBuffer work with Worker Threads?**

SharedArrayBuffer provides a fixed-size block of memory accessible from multiple threads simultaneously. Unlike `postMessage` (which copies data), SharedArrayBuffer has zero-copy overhead. Use `Atomics` for thread-safe operations (load, store, add, wait, notify) to prevent race conditions.

**Q5: Explain the difference between Cluster and PM2.**

Cluster is a Node.js core module — you write the clustering logic. PM2 is a process manager that handles clustering, process monitoring, log management, zero-downtime reloads, and auto-restart on crashes. PM2 wraps cluster internally but adds operational features (daemon mode, metrics, deployment).

**Q6: How do you handle errors in worker threads and child processes?**

Worker threads: listen for `error` event (uncaught exceptions) and `exit` with non-zero code. Child processes: `error` event (spawn failure), `stderr` stream (runtime errors), `exit` event (check code). Always implement restart/replacement logic and avoid orphan processes.

### Advanced

**Q7: How would you implement a job queue with worker threads that handles backpressure?**

Use a bounded task queue. When the queue is full, `runTask()` blocks (returns pending promise) until a worker frees up. Track active tasks count. Implement priority queues for different job types. Add health monitoring (dead worker detection/replacement). Use `Atomics.wait()` for efficient blocking.

**Q8: Explain the limitations of Worker Threads and when child processes are better.**

Limitations: Workers share the same process — a V8 crash or segfault kills all workers. Native addons must be thread-safe. `process.env` is shared (mutations visible to all). Each worker has its own event loop but shares the libuv thread pool. Use child processes when: isolation is critical, running untrusted code, or needing independent resource limits.

**Q9: How would you implement zero-downtime deployment with the Cluster module?**

1. Primary receives SIGUSR2 signal
2. Fork new workers one at a time
3. Wait for new worker to start listening
4. Disconnect old worker (stop accepting new connections)
5. Old worker finishes in-flight requests, then exits
6. Repeat for all workers
This is "rolling restart" — at least N-1 workers always serving traffic. Libraries: pm2, throng, or custom implementation.

---

## 🛠️ Hands-on Exercise

Build a parallel image processing pipeline:
1. Main thread watches a folder for new images
2. Worker pool (4 threads) processes images in parallel
3. Each worker: resize, apply watermark, compress
4. Use SharedArrayBuffer for progress reporting
5. Handle worker crashes with automatic restart
