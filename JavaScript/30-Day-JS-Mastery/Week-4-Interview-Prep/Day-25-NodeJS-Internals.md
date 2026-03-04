# Day 25: Node.js Internals & Concepts

## 🎯 Learning Objectives
- Understand Node.js architecture
- Master the event loop in Node.js
- Learn streams and buffers
- Understand the module system
- Know common Node.js patterns

---

## 🏗️ Node.js Architecture

```
╔════════════════════════════════════════════════════════════════════╗
║                     NODE.JS ARCHITECTURE                            ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║                    ┌──────────────────────┐                        ║
║                    │    Your JavaScript   │                        ║
║                    └──────────┬───────────┘                        ║
║                               │                                     ║
║                    ┌──────────▼───────────┐                        ║
║                    │     Node.js APIs     │                        ║
║                    │  (http, fs, crypto)  │                        ║
║                    └──────────┬───────────┘                        ║
║                               │                                     ║
║           ┌───────────────────┼───────────────────┐                ║
║           │                   │                   │                 ║
║    ┌──────▼──────┐    ┌───────▼───────┐   ┌──────▼──────┐         ║
║    │     V8      │    │    libuv      │   │  C++ Bindings│         ║
║    │  (JS Engine)│    │ (Event Loop)  │   │  (OpenSSL,  │         ║
║    │             │    │               │   │   zlib...)  │         ║
║    └─────────────┘    └───────────────┘   └─────────────┘         ║
║                               │                                     ║
║                    ┌──────────▼───────────┐                        ║
║                    │   Operating System   │                        ║
║                    └──────────────────────┘                        ║
║                                                                     ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## 🔄 Node.js Event Loop

The Node.js event loop is different from the browser's.

```javascript
/*
NODE.JS EVENT LOOP PHASES:

   ┌───────────────────────────────────────────────────────┐
┌─▶│                       TIMERS                          │
│  │            (setTimeout, setInterval)                  │
│  └───────────────────────────┬───────────────────────────┘
│                              │
│  ┌───────────────────────────▼───────────────────────────┐
│  │                  PENDING CALLBACKS                     │
│  │         (I/O callbacks deferred from previous)        │
│  └───────────────────────────┬───────────────────────────┘
│                              │
│  ┌───────────────────────────▼───────────────────────────┐
│  │                   IDLE, PREPARE                        │
│  │              (internal use only)                       │
│  └───────────────────────────┬───────────────────────────┘
│                              │
│  ┌───────────────────────────▼───────────────────────────┐
│  │                       POLL                             │
│  │          (retrieve new I/O events, execute)           │
│  └───────────────────────────┬───────────────────────────┘
│                              │
│  ┌───────────────────────────▼───────────────────────────┐
│  │                      CHECK                             │
│  │               (setImmediate callbacks)                 │
│  └───────────────────────────┬───────────────────────────┘
│                              │
│  ┌───────────────────────────▼───────────────────────────┐
│  │                  CLOSE CALLBACKS                       │
│  │            (socket.on('close', ...))                   │
│  └───────────────────────────┬───────────────────────────┘
│                              │
└──────────────────────────────┘

BETWEEN EACH PHASE:
• process.nextTick() callbacks
• Promise microtasks
*/

// Execution order demo
console.log('1: Script start');

setTimeout(() => console.log('2: setTimeout'), 0);

setImmediate(() => console.log('3: setImmediate'));

Promise.resolve().then(() => console.log('4: Promise'));

process.nextTick(() => console.log('5: nextTick'));

console.log('6: Script end');

// Output:
// 1: Script start
// 6: Script end
// 5: nextTick (between phases)
// 4: Promise (microtasks)
// 2: setTimeout OR 3: setImmediate (order can vary at top level)
// 3: setImmediate OR 2: setTimeout

// Inside I/O callback, order is guaranteed
const fs = require('fs');

fs.readFile(__filename, () => {
    setTimeout(() => console.log('timeout'), 0);
    setImmediate(() => console.log('immediate'));
});

// Output always:
// immediate
// timeout
// (setImmediate is always before setTimeout in I/O callbacks)
```

### process.nextTick vs setImmediate

```javascript
/*
process.nextTick():
• Executes BEFORE entering the next event loop phase
• Can starve I/O if used recursively
• Use for: deferring work that should happen before I/O

setImmediate():
• Executes IN the check phase of the event loop
• Allows I/O to be processed
• Use for: yielding to the event loop
*/

// nextTick can starve I/O
function recursiveNextTick() {
    process.nextTick(recursiveNextTick);
}
// This will prevent any I/O from being processed!

// setImmediate is safer
function recursiveImmediate() {
    setImmediate(recursiveImmediate);
}
// I/O can still be processed between calls

// Practical use of nextTick
class EventEmitterAsync extends require('events').EventEmitter {
    constructor() {
        super();
        // Defer emission to allow listeners to be added
        process.nextTick(() => {
            this.emit('ready');
        });
    }
}

const emitter = new EventEmitterAsync();
emitter.on('ready', () => console.log('Ready!'));
// Works because nextTick defers the emit
```

---

## 📚 Streams

Streams handle data piece by piece without loading everything into memory.

```javascript
const { Readable, Writable, Transform, Duplex } = require('stream');
const fs = require('fs');

/*
STREAM TYPES:
• Readable: source of data (fs.createReadStream)
• Writable: destination for data (fs.createWriteStream)
• Duplex: both readable and writable (net.Socket)
• Transform: modify data as it passes through (zlib.createGzip)
*/

// Readable stream
const readableStream = fs.createReadStream('file.txt', {
    encoding: 'utf8',
    highWaterMark: 16 * 1024 // 16KB chunks
});

readableStream.on('data', (chunk) => {
    console.log('Received chunk:', chunk.length, 'bytes');
});

readableStream.on('end', () => {
    console.log('No more data');
});

readableStream.on('error', (err) => {
    console.error('Error:', err);
});

// Writable stream
const writableStream = fs.createWriteStream('output.txt');

writableStream.write('Hello, ');
writableStream.write('World!');
writableStream.end(); // Signal we're done

writableStream.on('finish', () => {
    console.log('All data written');
});

// Piping (connecting streams)
fs.createReadStream('input.txt')
    .pipe(fs.createWriteStream('output.txt'));

// With error handling
const pipeline = require('stream').pipeline;

pipeline(
    fs.createReadStream('input.txt'),
    fs.createWriteStream('output.txt'),
    (err) => {
        if (err) {
            console.error('Pipeline failed:', err);
        } else {
            console.log('Pipeline succeeded');
        }
    }
);

// Custom Readable stream
class CounterStream extends Readable {
    constructor(max) {
        super();
        this.max = max;
        this.index = 1;
    }
    
    _read() {
        if (this.index <= this.max) {
            this.push(String(this.index++) + '\n');
        } else {
            this.push(null); // Signal end
        }
    }
}

const counter = new CounterStream(5);
counter.pipe(process.stdout); // 1, 2, 3, 4, 5

// Custom Transform stream
class UpperCaseTransform extends Transform {
    _transform(chunk, encoding, callback) {
        this.push(chunk.toString().toUpperCase());
        callback();
    }
}

fs.createReadStream('input.txt')
    .pipe(new UpperCaseTransform())
    .pipe(fs.createWriteStream('output.txt'));

// Async iteration over streams
async function processStream(stream) {
    for await (const chunk of stream) {
        console.log('Chunk:', chunk);
    }
}
```

---

## 💾 Buffers

Buffers handle binary data in Node.js.

```javascript
// Creating buffers
const buf1 = Buffer.alloc(10);           // 10 bytes, filled with zeros
const buf2 = Buffer.alloc(10, 1);        // 10 bytes, filled with 1s
const buf3 = Buffer.allocUnsafe(10);     // 10 bytes, not initialized (faster)
const buf4 = Buffer.from([1, 2, 3]);     // From array
const buf5 = Buffer.from('Hello');       // From string (UTF-8)
const buf6 = Buffer.from('48656c6c6f', 'hex'); // From hex string

// Reading/writing
const buf = Buffer.alloc(4);

buf.writeInt32BE(1234);      // Big-endian
buf.writeInt32LE(1234);      // Little-endian
buf.readInt32BE();           // Read big-endian

// Converting
buf.toString('utf8');        // To string
buf.toString('hex');         // To hex
buf.toString('base64');      // To base64
buf.toJSON();                // { type: 'Buffer', data: [...] }

// Comparing
Buffer.compare(buf1, buf2);  // -1, 0, or 1
buf1.equals(buf2);           // true/false

// Concatenating
const combined = Buffer.concat([buf1, buf2, buf3]);

// Slicing (creates view, not copy!)
const slice = buf.slice(0, 5);

// Copying
const copy = Buffer.alloc(buf.length);
buf.copy(copy);

// Filling
buf.fill(0);
buf.fill('a');

// Practical example: Reading binary file headers
function readFileHeader(filename) {
    const fd = fs.openSync(filename, 'r');
    const header = Buffer.alloc(4);
    fs.readSync(fd, header, 0, 4, 0);
    fs.closeSync(fd);
    
    // Check magic numbers
    if (header.toString('hex') === '89504e47') {
        return 'PNG';
    } else if (header.toString().startsWith('GIF')) {
        return 'GIF';
    } else if (header.readUInt16BE() === 0xffd8) {
        return 'JPEG';
    }
    return 'Unknown';
}
```

---

## 📦 Module System

### CommonJS (CJS)

```javascript
// Exporting
// math.js
const add = (a, b) => a + b;
const subtract = (a, b) => a - b;

module.exports = { add, subtract };
// or
exports.add = add;
exports.subtract = subtract;

// Importing
const math = require('./math');
const { add } = require('./math');

// Module wrapper (what Node.js actually does)
(function(exports, require, module, __filename, __dirname) {
    // Your code here
    module.exports = yourExports;
});

// Module caching
const a = require('./module'); // Loads and caches
const b = require('./module'); // Returns cached
console.log(a === b);          // true

// Clear cache
delete require.cache[require.resolve('./module')];

// Circular dependencies
// a.js
exports.loaded = false;
const b = require('./b');
exports.loaded = true;

// b.js
const a = require('./a');
console.log(a.loaded);  // false (a is not fully loaded yet)
```

### ES Modules (ESM)

```javascript
// package.json
{ "type": "module" }

// Or use .mjs extension

// Exporting
export const add = (a, b) => a + b;
export default function main() {}

// Importing
import main, { add } from './math.js';
import * as math from './math.js';

// Dynamic import
const module = await import('./module.js');

// Import JSON (Node 18+)
import data from './data.json' assert { type: 'json' };

// import.meta
console.log(import.meta.url);  // file:///path/to/module.js

// Create require in ESM
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const json = require('./data.json');
```

---

## 🔧 Common Patterns

### Async Patterns

```javascript
// Callback pattern
function readFileCallback(path, callback) {
    fs.readFile(path, 'utf8', (err, data) => {
        if (err) return callback(err);
        callback(null, data);
    });
}

// Promise wrapper
function readFilePromise(path) {
    return new Promise((resolve, reject) => {
        fs.readFile(path, 'utf8', (err, data) => {
            if (err) reject(err);
            else resolve(data);
        });
    });
}

// util.promisify
const { promisify } = require('util');
const readFile = promisify(fs.readFile);

// fs/promises (built-in)
const fsPromises = require('fs/promises');
// or
const { readFile } = require('fs/promises');

// Async/await
async function processFiles() {
    try {
        const data = await readFile('file.txt', 'utf8');
        return process(data);
    } catch (err) {
        console.error(err);
    }
}
```

### Worker Threads

```javascript
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

if (isMainThread) {
    // Main thread
    const worker = new Worker(__filename, {
        workerData: { num: 42 }
    });
    
    worker.on('message', (result) => {
        console.log('Result:', result);
    });
    
    worker.on('error', (err) => {
        console.error('Worker error:', err);
    });
    
    worker.on('exit', (code) => {
        console.log('Worker exited with code:', code);
    });
} else {
    // Worker thread
    const num = workerData.num;
    const result = heavyComputation(num);
    parentPort.postMessage(result);
}

// Worker pool pattern
class WorkerPool {
    constructor(workerPath, poolSize) {
        this.workers = [];
        this.queue = [];
        
        for (let i = 0; i < poolSize; i++) {
            this.workers.push({
                worker: new Worker(workerPath),
                busy: false
            });
        }
    }
    
    execute(data) {
        return new Promise((resolve, reject) => {
            const available = this.workers.find(w => !w.busy);
            
            if (available) {
                this.runTask(available, data, resolve, reject);
            } else {
                this.queue.push({ data, resolve, reject });
            }
        });
    }
    
    runTask(workerInfo, data, resolve, reject) {
        workerInfo.busy = true;
        workerInfo.worker.postMessage(data);
        
        workerInfo.worker.once('message', (result) => {
            workerInfo.busy = false;
            resolve(result);
            this.processQueue();
        });
        
        workerInfo.worker.once('error', (err) => {
            workerInfo.busy = false;
            reject(err);
            this.processQueue();
        });
    }
    
    processQueue() {
        if (this.queue.length > 0) {
            const available = this.workers.find(w => !w.busy);
            if (available) {
                const { data, resolve, reject } = this.queue.shift();
                this.runTask(available, data, resolve, reject);
            }
        }
    }
}
```

### Cluster Module

```javascript
const cluster = require('cluster');
const http = require('http');
const numCPUs = require('os').cpus().length;

if (cluster.isPrimary) {
    console.log(`Primary ${process.pid} is running`);
    
    // Fork workers
    for (let i = 0; i < numCPUs; i++) {
        cluster.fork();
    }
    
    cluster.on('exit', (worker, code, signal) => {
        console.log(`Worker ${worker.process.pid} died`);
        // Restart worker
        cluster.fork();
    });
} else {
    // Workers share the same port
    http.createServer((req, res) => {
        res.writeHead(200);
        res.end(`Hello from worker ${process.pid}`);
    }).listen(8000);
    
    console.log(`Worker ${process.pid} started`);
}
```

---

## ✅ Day 25 Checklist

- [ ] Understand Node.js architecture
- [ ] Know V8 and libuv roles
- [ ] Master event loop phases
- [ ] Know nextTick vs setImmediate
- [ ] Work with streams (Readable, Writable, Transform)
- [ ] Handle buffers for binary data
- [ ] Understand CJS vs ESM modules
- [ ] Use util.promisify
- [ ] Implement worker threads
- [ ] Use cluster for multi-core
