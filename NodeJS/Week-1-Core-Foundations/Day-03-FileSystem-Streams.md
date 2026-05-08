# Day 3: File System & Path Operations

## 🎯 Learning Objectives
- Master the `fs` module (sync, callback, promise APIs)
- Understand Streams for large file handling
- Learn the `path` module for cross-platform paths
- Handle file watching and directory operations

---

## 📚 The fs Module

### Three API Styles

```javascript
const fs = require('fs');
const fsPromises = require('fs/promises'); // or fs.promises

// 1. Synchronous (blocks event loop - avoid in servers!)
try {
  const data = fs.readFileSync('file.txt', 'utf-8');
  console.log(data);
} catch (err) {
  console.error(err);
}

// 2. Callback (original async pattern)
fs.readFile('file.txt', 'utf-8', (err, data) => {
  if (err) throw err;
  console.log(data);
});

// 3. Promises (modern - preferred)
async function readFile() {
  const data = await fsPromises.readFile('file.txt', 'utf-8');
  console.log(data);
}
```

### Common File Operations

```javascript
const fs = require('fs/promises');

// Write file (creates or overwrites)
await fs.writeFile('output.txt', 'Hello World', 'utf-8');

// Append to file
await fs.appendFile('log.txt', `${new Date().toISOString()} - Event\n`);

// Copy file
await fs.copyFile('source.txt', 'dest.txt');

// Rename/Move file
await fs.rename('old.txt', 'new.txt');

// Delete file
await fs.unlink('temp.txt');

// File stats
const stats = await fs.stat('file.txt');
console.log({
  size: stats.size,           // bytes
  isFile: stats.isFile(),
  isDirectory: stats.isDirectory(),
  created: stats.birthtime,
  modified: stats.mtime,
  permissions: stats.mode
});

// Check if file exists
try {
  await fs.access('file.txt', fs.constants.F_OK);
  console.log('File exists');
} catch {
  console.log('File does not exist');
}
```

### Directory Operations

```javascript
const fs = require('fs/promises');
const path = require('path');

// Create directory (recursive)
await fs.mkdir('path/to/deep/dir', { recursive: true });

// Read directory
const entries = await fs.readdir('src', { withFileTypes: true });
for (const entry of entries) {
  if (entry.isDirectory()) {
    console.log(`📁 ${entry.name}`);
  } else {
    console.log(`📄 ${entry.name}`);
  }
}

// Remove directory (recursive)
await fs.rm('temp-dir', { recursive: true, force: true });

// Walk directory tree recursively
async function walk(dir) {
  const files = [];
  const entries = await fs.readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...await walk(fullPath));
    } else {
      files.push(fullPath);
    }
  }
  return files;
}

const allFiles = await walk('./src');
```

---

## 🔄 Streams

Streams process data in chunks — essential for large files that don't fit in memory.

```javascript
const fs = require('fs');
const { pipeline } = require('stream/promises');
const zlib = require('zlib');

// Read stream
const readable = fs.createReadStream('large-file.csv', {
  encoding: 'utf-8',
  highWaterMark: 64 * 1024 // 64KB chunks (default: 16KB)
});

readable.on('data', (chunk) => {
  console.log(`Received ${chunk.length} bytes`);
});
readable.on('end', () => console.log('Done'));
readable.on('error', (err) => console.error(err));

// Write stream
const writable = fs.createWriteStream('output.txt');
writable.write('Line 1\n');
writable.write('Line 2\n');
writable.end(); // Signal no more data

// Pipeline (recommended - handles errors & backpressure)
await pipeline(
  fs.createReadStream('input.txt'),
  zlib.createGzip(),
  fs.createWriteStream('input.txt.gz')
);

// Process CSV line by line (memory efficient)
const readline = require('readline');
const rl = readline.createInterface({
  input: fs.createReadStream('huge-data.csv'),
  crlfDelay: Infinity
});

let lineCount = 0;
for await (const line of rl) {
  lineCount++;
  // Process each line without loading entire file
}
console.log(`Processed ${lineCount} lines`);
```

### Transform Streams

```javascript
const { Transform } = require('stream');
const { pipeline } = require('stream/promises');

// Custom transform: uppercase every chunk
const upperCase = new Transform({
  transform(chunk, encoding, callback) {
    this.push(chunk.toString().toUpperCase());
    callback();
  }
});

await pipeline(
  fs.createReadStream('input.txt'),
  upperCase,
  fs.createWriteStream('output.txt')
);
```

---

## 📂 The path Module

```javascript
const path = require('path');

// Join paths (handles separators)
path.join('/users', 'john', 'docs', 'file.txt');
// → '/users/john/docs/file.txt' (Unix)
// → '\\users\\john\\docs\\file.txt' (Windows)

// Resolve to absolute path
path.resolve('src', 'utils', 'helper.js');
// → '/home/user/project/src/utils/helper.js'

// Parse path components
const parsed = path.parse('/home/user/file.txt');
// { root: '/', dir: '/home/user', base: 'file.txt', ext: '.txt', name: 'file' }

// Extract parts
path.basename('/foo/bar/baz.html');      // 'baz.html'
path.basename('/foo/bar/baz.html', '.html'); // 'baz'
path.dirname('/foo/bar/baz.html');       // '/foo/bar'
path.extname('index.coffee.md');         // '.md'

// Relative path between two paths
path.relative('/data/users', '/data/posts/today');
// → '../posts/today'

// Normalize path (resolves .., .)
path.normalize('/foo/bar//baz/asdf/quux/..');
// → '/foo/bar/baz/asdf'

// Platform-specific separator
path.sep;      // '/' on Unix, '\\' on Windows
path.delimiter; // ':' on Unix, ';' on Windows
```

---

## 👁️ File Watching

```javascript
const fs = require('fs');
const { watch } = require('fs/promises');

// Simple watch (uses OS-level watchers)
fs.watch('src', { recursive: true }, (eventType, filename) => {
  console.log(`${eventType}: ${filename}`);
});

// Async iterator (Node 18+)
async function watchDir() {
  const watcher = watch('src', { recursive: true });
  for await (const event of watcher) {
    console.log(`${event.eventType}: ${event.filename}`);
  }
}

// Debounced watcher (practical)
let timeout;
fs.watch('src', { recursive: true }, (event, filename) => {
  clearTimeout(timeout);
  timeout = setTimeout(() => {
    console.log(`Changed: ${filename}`);
    // Rebuild, restart, etc.
  }, 100);
});
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What's the difference between `fs.readFile()` and `fs.createReadStream()`?**

`readFile()` loads the entire file into memory at once — fine for small files but problematic for large ones. `createReadStream()` reads in chunks (default 16KB), processing data as it flows through, using minimal memory regardless of file size.

**Q2: Why should you avoid synchronous `fs` methods in a server?**

Synchronous methods (`readFileSync`, etc.) block the entire event loop. While blocked, no other requests can be processed. In a server handling concurrent requests, this causes all users to wait, destroying throughput. Use async methods (`fs/promises`) instead.

**Q3: What does `path.resolve()` vs `path.join()` do?**

`path.join()` concatenates path segments with the correct separator. `path.resolve()` resolves to an absolute path, processing from right to left until an absolute path is formed. `resolve('a', '/b', 'c')` → `/b/c`, while `join('a', '/b', 'c')` → `a/b/c`.

### Intermediate

**Q4: Explain backpressure in Node.js streams and how to handle it.**

Backpressure occurs when a writable stream's internal buffer fills up (exceeds `highWaterMark`). `write()` returns `false`, signaling the readable should pause. Listen for the `drain` event to resume. `pipeline()` handles this automatically. Without proper handling, memory grows unbounded.

**Q5: How would you efficiently process a 10GB log file in Node.js?**

Use `createReadStream` with `readline` for line-by-line processing, or Transform streams for custom parsing. Never use `readFile`. Consider `pipeline()` for chaining operations. For parallel processing, split the file and use Worker Threads. Memory usage stays constant regardless of file size.

**Q6: What is the difference between `fs.watch()` and `fs.watchFile()`?**

`fs.watch()` uses OS-native file watching (inotify/FSEvents/ReadDirectoryChanges), is efficient but can be unreliable across platforms. `fs.watchFile()` uses polling (stat checks at intervals), is reliable but more resource-intensive. For production, use libraries like chokidar that handle cross-platform issues.

### Advanced

**Q7: How do file descriptors work in Node.js and when would you use them?**

File descriptors (fd) are OS-level integer handles to open files. Use `fs.open()` to get an fd, then `fs.read()`/`fs.write()` for fine-grained control (random access, partial reads, multiple operations on same file). Always `fs.close()` when done to prevent leaks. Useful for databases, binary formats, or lock files.

**Q8: Explain how Node.js handles file I/O internally using the thread pool.**

File operations are offloaded to libuv's thread pool (default 4 threads). The main thread submits work, continues processing events, and receives completion callbacks when the thread finishes. This is why `UV_THREADPOOL_SIZE` affects fs performance under load — all fs operations share the pool with crypto and DNS.

**Q9: How would you implement atomic file writes in Node.js?**

Write to a temporary file first, then use `fs.rename()` (atomic on most filesystems). This prevents corruption from crashes mid-write or concurrent readers seeing partial data. Pattern: write to `.tmp`, `fsync` for durability, rename to final name. Libraries like `write-file-atomic` implement this.

---

## 🛠️ Hands-on Exercise

Build a log file analyzer that:
1. Watches a directory for new `.log` files
2. Processes each file using streams (line by line)
3. Extracts errors and warnings
4. Writes a summary report
5. Compresses processed files with gzip
