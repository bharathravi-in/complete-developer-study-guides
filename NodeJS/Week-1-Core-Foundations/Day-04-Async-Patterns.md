# Day 4: Async Patterns - Callbacks, Promises, Async/Await

## 🎯 Learning Objectives
- Master all Node.js async patterns
- Understand error handling in async code
- Learn Promise combinators and patterns
- Handle async iteration and generators

---

## 📚 Evolution of Async in Node.js

### 1. Callbacks (Error-First Pattern)

```javascript
const fs = require('fs');

// Node.js convention: callback(error, result)
fs.readFile('file.txt', 'utf-8', (err, data) => {
  if (err) {
    console.error('Failed:', err.message);
    return;
  }
  console.log(data);
});

// Callback Hell (Pyramid of Doom)
fs.readFile('config.json', 'utf-8', (err, config) => {
  if (err) return handleError(err);
  const parsed = JSON.parse(config);
  db.connect(parsed.dbUrl, (err, connection) => {
    if (err) return handleError(err);
    connection.query('SELECT * FROM users', (err, users) => {
      if (err) return handleError(err);
      users.forEach(user => {
        sendEmail(user.email, (err) => {
          if (err) return handleError(err);
          // Deeply nested... hard to read and maintain
        });
      });
    });
  });
});
```

### 2. Promises

```javascript
const fs = require('fs/promises');

// Creating promises
function readConfig(path) {
  return new Promise((resolve, reject) => {
    fs.readFile(path, 'utf-8')
      .then(data => resolve(JSON.parse(data)))
      .catch(err => reject(err));
  });
}

// Chaining (flat, readable)
readConfig('config.json')
  .then(config => db.connect(config.dbUrl))
  .then(connection => connection.query('SELECT * FROM users'))
  .then(users => Promise.all(users.map(u => sendEmail(u.email))))
  .then(() => console.log('All emails sent'))
  .catch(err => console.error('Pipeline failed:', err));

// Promise states:
// - Pending: initial state
// - Fulfilled: resolved with value
// - Rejected: rejected with reason
// Once settled (fulfilled/rejected), cannot change
```

### 3. Async/Await (Modern Standard)

```javascript
const fs = require('fs/promises');

async function processUsers() {
  try {
    const config = JSON.parse(await fs.readFile('config.json', 'utf-8'));
    const connection = await db.connect(config.dbUrl);
    const users = await connection.query('SELECT * FROM users');
    
    // Sequential (one at a time)
    for (const user of users) {
      await sendEmail(user.email);
    }
    
    // Parallel (all at once)
    await Promise.all(users.map(u => sendEmail(u.email)));
    
    console.log('Done');
  } catch (err) {
    console.error('Failed:', err);
  } finally {
    await connection?.close();
  }
}
```

---

## 🔧 Promise Combinators

```javascript
const tasks = [
  fetch('/api/users'),
  fetch('/api/posts'),
  fetch('/api/comments')
];

// Promise.all - ALL must succeed (fails fast on first rejection)
const [users, posts, comments] = await Promise.all(tasks);

// Promise.allSettled - Wait for ALL, regardless of success/failure
const results = await Promise.allSettled(tasks);
results.forEach(result => {
  if (result.status === 'fulfilled') {
    console.log('Success:', result.value);
  } else {
    console.log('Failed:', result.reason);
  }
});

// Promise.race - First to settle (resolve OR reject) wins
const fastest = await Promise.race([
  fetch('/api/data'),
  new Promise((_, reject) => setTimeout(() => reject('Timeout'), 5000))
]);

// Promise.any - First to RESOLVE wins (ignores rejections)
const firstSuccess = await Promise.any([
  fetch('https://primary-api.com/data'),
  fetch('https://backup-api.com/data'),
  fetch('https://cdn-api.com/data')
]);
// Throws AggregateError only if ALL reject
```

---

## ⚠️ Error Handling Patterns

```javascript
// Pattern 1: try/catch with async/await
async function fetchData(url) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (err) {
    if (err.code === 'ECONNREFUSED') {
      throw new Error('Service unavailable');
    }
    throw err; // Re-throw unexpected errors
  }
}

// Pattern 2: Error wrapper (Go-style)
async function to(promise) {
  try {
    const result = await promise;
    return [null, result];
  } catch (err) {
    return [err, null];
  }
}

const [err, data] = await to(fetchData('/api/users'));
if (err) {
  console.error('Failed:', err);
}

// Pattern 3: Global unhandled rejection handler
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // Log to monitoring service
  // In production: graceful shutdown
});

process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
  // MUST exit - process is in undefined state
  process.exit(1);
});
```

### Common Async Pitfalls

```javascript
// ❌ Pitfall 1: forEach doesn't wait for async
const files = ['a.txt', 'b.txt', 'c.txt'];
files.forEach(async (file) => {
  const data = await fs.readFile(file); // Fires and forgets!
});
console.log('Done'); // Runs BEFORE files are read!

// ✅ Fix: use for...of for sequential
for (const file of files) {
  const data = await fs.readFile(file);
}

// ✅ Fix: use Promise.all for parallel
await Promise.all(files.map(file => fs.readFile(file)));

// ❌ Pitfall 2: Missing await
async function getUser() {
  return fetchUser(); // Returns Promise, not resolved value!
}

// ❌ Pitfall 3: Sequential when parallel is possible
const user = await getUser(id);     // Wait...
const posts = await getPosts(id);   // Then wait again...
// These are independent! Run in parallel:
const [user, posts] = await Promise.all([getUser(id), getPosts(id)]);

// ❌ Pitfall 4: Swallowing errors
async function riskyOperation() {
  doSomething().catch(() => {}); // Error silently ignored!
}
```

---

## 🔄 Async Iteration

```javascript
const { Readable } = require('stream');

// Async generators
async function* fetchPages(url) {
  let page = 1;
  while (true) {
    const response = await fetch(`${url}?page=${page}`);
    const data = await response.json();
    if (data.length === 0) break;
    yield data;
    page++;
  }
}

// Consuming async iterables
for await (const pageData of fetchPages('/api/items')) {
  console.log(`Got ${pageData.length} items`);
}

// Async generator for retry logic
async function* retryable(fn, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      yield await fn();
      return;
    } catch (err) {
      if (attempt === maxRetries) throw err;
      await new Promise(r => setTimeout(r, 1000 * attempt)); // Exponential backoff
      yield { retry: attempt, error: err.message };
    }
  }
}
```

---

## 🔒 Concurrency Control

```javascript
// Limit concurrent operations (e.g., max 5 parallel requests)
async function parallelLimit(tasks, limit) {
  const results = [];
  const executing = new Set();
  
  for (const [index, task] of tasks.entries()) {
    const promise = task().then(result => {
      executing.delete(promise);
      return result;
    });
    executing.add(promise);
    results[index] = promise;
    
    if (executing.size >= limit) {
      await Promise.race(executing);
    }
  }
  
  return Promise.all(results);
}

// Usage
const urls = Array.from({ length: 100 }, (_, i) => `https://api.com/item/${i}`);
const tasks = urls.map(url => () => fetch(url).then(r => r.json()));
const results = await parallelLimit(tasks, 5); // Max 5 concurrent fetches
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is the difference between `Promise.all()` and `Promise.allSettled()`?**

`Promise.all()` short-circuits on the first rejection — if any promise rejects, the whole thing rejects immediately. `Promise.allSettled()` waits for ALL promises to complete and returns an array of `{status, value/reason}` objects, regardless of success or failure.

**Q2: Why can't you use `await` at the top level in CommonJS?**

`await` is only valid inside `async` functions or in ES Modules (which support top-level await). CommonJS modules are wrapped in a synchronous function, so `await` would be a syntax error. Workaround: wrap in an async IIFE: `(async () => { await ... })()`.

**Q3: What happens if you don't `await` a promise in an `async` function?**

The promise executes but its result is not captured — it becomes a "fire and forget" operation. If it rejects, you'll get an `unhandledRejection` event. The function continues without waiting for completion, potentially causing race conditions.

### Intermediate

**Q4: How do you implement a timeout for a promise?**

Use `Promise.race()` with a timeout promise: `Promise.race([actualPromise, new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 5000))])`. For AbortController-compatible APIs, pass `signal` to abort the actual operation on timeout.

**Q5: Explain the difference between sequential and concurrent async execution. When would you choose each?**

Sequential (`for...of` + `await`): When order matters or operations depend on each other (database transactions, rate-limited APIs). Concurrent (`Promise.all`): When operations are independent (fetching multiple resources). Use concurrency limiters when you need parallelism but want to control resource usage.

**Q6: What is an `unhandledRejection` and how should you handle it in production?**

It fires when a promise rejects and no `.catch()` or try/catch handles it. In production: log the error with context, send to monitoring (Sentry/Datadog), and decide whether to continue or gracefully shutdown. Node.js will eventually make these terminate the process by default.

### Advanced

**Q7: How would you implement a retry mechanism with exponential backoff?**

```javascript
async function withRetry(fn, { maxRetries = 3, baseDelay = 1000, maxDelay = 30000 } = {}) {
  for (let i = 0; i <= maxRetries; i++) {
    try { return await fn(); } 
    catch (err) {
      if (i === maxRetries) throw err;
      const delay = Math.min(baseDelay * 2 ** i + Math.random() * 1000, maxDelay);
      await new Promise(r => setTimeout(r, delay));
    }
  }
}
```
Add jitter to prevent thundering herd. Consider circuit breaker pattern for cascading failures.

**Q8: How does `AbortController` work with async operations in Node.js?**

`AbortController` creates a signal that can cancel async operations. Pass `signal` to `fetch()`, `fs` operations (Node 16+), `setTimeout` (Node 16+). On `abort()`, operations throw `AbortError`. Use in HTTP request timeouts, user cancellation, and cleanup on shutdown.

**Q9: Explain the microtask queue and its relationship to async/await.**

When `await` pauses, the rest of the async function is scheduled as a microtask continuation. Microtasks (Promise.then, queueMicrotask, process.nextTick) run between each macrotask and between event loop phases. Excessive microtasks can starve I/O — `nextTick` recursion can prevent the event loop from reaching the poll phase.

---

## 🛠️ Hands-on Exercise

Build an API data aggregator:
1. Fetch data from 3 different endpoints concurrently
2. Implement retry with exponential backoff
3. Add a 5-second timeout per request
4. Use `AbortController` for cancellation
5. Handle partial failures gracefully with `Promise.allSettled`
