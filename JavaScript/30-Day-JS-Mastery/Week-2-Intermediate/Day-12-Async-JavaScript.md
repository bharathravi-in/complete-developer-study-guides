# Day 12: Asynchronous JavaScript

## 🎯 Learning Objectives
- Understand callbacks and callback hell
- Master Promises and chaining
- Learn async/await patterns
- Handle errors properly

---

## 📚 Callbacks

A **callback** is a function passed to another function to be executed later.

```javascript
// Basic callback
function fetchData(callback) {
    setTimeout(() => {
        const data = { id: 1, name: "John" };
        callback(data);
    }, 1000);
}

fetchData((data) => {
    console.log(data); // { id: 1, name: "John" }
});

// Error-first callback pattern (Node.js convention)
function readFile(path, callback) {
    setTimeout(() => {
        if (path === "invalid") {
            callback(new Error("File not found"), null);
        } else {
            callback(null, "File contents here");
        }
    }, 1000);
}

readFile("valid.txt", (err, data) => {
    if (err) {
        console.error("Error:", err.message);
        return;
    }
    console.log("Data:", data);
});
```

### Callback Hell

```javascript
// The dreaded pyramid of doom
getUser(userId, (err, user) => {
    if (err) return handleError(err);
    
    getOrders(user.id, (err, orders) => {
        if (err) return handleError(err);
        
        getOrderDetails(orders[0].id, (err, details) => {
            if (err) return handleError(err);
            
            getShippingInfo(details.shippingId, (err, shipping) => {
                if (err) return handleError(err);
                
                // Finally we can use the data!
                console.log(user, orders, details, shipping);
            });
        });
    });
});

// Problems:
// 1. Hard to read
// 2. Hard to maintain
// 3. Error handling is repetitive
// 4. Can't easily run operations in parallel
```

---

## 🎁 Promises

A **Promise** represents a value that may be available now, later, or never.

### Promise States
- **Pending**: Initial state, neither fulfilled nor rejected
- **Fulfilled**: Operation completed successfully
- **Rejected**: Operation failed

```javascript
// Creating a Promise
const promise = new Promise((resolve, reject) => {
    // Executor runs immediately
    const success = true;
    
    if (success) {
        resolve("Operation succeeded!");
    } else {
        reject(new Error("Operation failed!"));
    }
});

// Using a Promise
promise
    .then(value => console.log(value))
    .catch(error => console.error(error));

// Promisifying callback-based function
function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

wait(2000).then(() => console.log("2 seconds passed!"));

// Promisifying error-first callback
function readFilePromise(path) {
    return new Promise((resolve, reject) => {
        readFile(path, (err, data) => {
            if (err) reject(err);
            else resolve(data);
        });
    });
}
```

### Promise Chaining

```javascript
fetch("/api/user/1")
    .then(response => {
        if (!response.ok) throw new Error("User not found");
        return response.json();
    })
    .then(user => {
        console.log("User:", user);
        return fetch(`/api/orders/${user.id}`);
    })
    .then(response => response.json())
    .then(orders => {
        console.log("Orders:", orders);
    })
    .catch(error => {
        console.error("Error:", error);
    })
    .finally(() => {
        console.log("Cleanup operations");
    });

// Each .then() returns a NEW promise
// Returned values are wrapped in Promise.resolve()
// Thrown errors are wrapped in Promise.reject()

// Transforming values
Promise.resolve(1)
    .then(x => x + 1)      // 2
    .then(x => x * 2)      // 4
    .then(x => x.toString()) // "4"
    .then(console.log);    // logs "4"
```

### Promise Static Methods

```javascript
// Promise.all - Wait for ALL promises (fail-fast)
const promises = [
    fetch("/api/users"),
    fetch("/api/posts"),
    fetch("/api/comments")
];

Promise.all(promises)
    .then(responses => Promise.all(responses.map(r => r.json())))
    .then(([users, posts, comments]) => {
        console.log({ users, posts, comments });
    })
    .catch(error => {
        // If ANY promise rejects, catch executes
        console.error("One request failed:", error);
    });

// Promise.allSettled - Wait for ALL, never fails
Promise.allSettled(promises)
    .then(results => {
        results.forEach(result => {
            if (result.status === "fulfilled") {
                console.log("Success:", result.value);
            } else {
                console.log("Failed:", result.reason);
            }
        });
    });

// Promise.race - First to settle (resolve OR reject)
const timeout = new Promise((_, reject) => 
    setTimeout(() => reject(new Error("Timeout")), 5000)
);

Promise.race([fetch("/api/data"), timeout])
    .then(response => console.log("Got response"))
    .catch(error => console.log(error.message)); // "Timeout" if too slow

// Promise.any - First to RESOLVE (ignores rejections)
Promise.any([
    Promise.reject("Error 1"),
    Promise.resolve("Success 1"),
    Promise.resolve("Success 2")
]).then(value => console.log(value)); // "Success 1"

// Promise.any fails only if ALL reject
Promise.any([
    Promise.reject("Error 1"),
    Promise.reject("Error 2")
]).catch(error => {
    console.log(error); // AggregateError: All promises were rejected
    console.log(error.errors); // ["Error 1", "Error 2"]
});

// Promise.resolve / Promise.reject
Promise.resolve(42).then(console.log); // 42
Promise.reject("Error").catch(console.log); // "Error"
```

---

## ⚡ async/await

Syntactic sugar over Promises, making async code look synchronous.

```javascript
// Before: Promise chains
function fetchUserData(userId) {
    return fetch(`/api/users/${userId}`)
        .then(res => res.json())
        .then(user => fetch(`/api/posts/${user.id}`))
        .then(res => res.json());
}

// After: async/await
async function fetchUserData(userId) {
    const userRes = await fetch(`/api/users/${userId}`);
    const user = await userRes.json();
    
    const postsRes = await fetch(`/api/posts/${user.id}`);
    const posts = await postsRes.json();
    
    return { user, posts };
}

// Calling async functions
fetchUserData(1)
    .then(data => console.log(data))
    .catch(error => console.error(error));

// Or in another async function
async function main() {
    try {
        const data = await fetchUserData(1);
        console.log(data);
    } catch (error) {
        console.error(error);
    }
}

// async functions ALWAYS return a Promise
async function getValue() {
    return 42;
}
getValue().then(console.log); // 42

async function throwError() {
    throw new Error("Oops!");
}
throwError().catch(console.error); // Error: Oops!
```

### Parallel Execution with async/await

```javascript
// SEQUENTIAL (slow) - each awaits previous
async function sequential() {
    const user = await fetchUser();     // 1 second
    const posts = await fetchPosts();   // 1 second
    const comments = await fetchComments(); // 1 second
    // Total: ~3 seconds
}

// PARALLEL (fast) - all start together
async function parallel() {
    const [user, posts, comments] = await Promise.all([
        fetchUser(),     // \
        fetchPosts(),    //  > All run simultaneously
        fetchComments()  // /
    ]);
    // Total: ~1 second (time of slowest request)
}

// PARALLEL with individual error handling
async function parallelWithErrors() {
    const results = await Promise.allSettled([
        fetchUser(),
        fetchPosts(),
        fetchComments()
    ]);
    
    const user = results[0].status === "fulfilled" ? results[0].value : null;
    const posts = results[1].status === "fulfilled" ? results[1].value : null;
    const comments = results[2].status === "fulfilled" ? results[2].value : null;
    
    return { user, posts, comments };
}
```

---

## 🚨 Error Handling

### With Promises

```javascript
// .catch() catches any error in the chain
fetchData()
    .then(process)
    .then(save)
    .catch(error => {
        // Catches errors from fetchData, process, or save
        console.error("Error:", error);
    });

// Multiple catch blocks (recovery)
fetchData()
    .then(process)
    .catch(error => {
        console.warn("Process failed, using default");
        return defaultValue; // Recovery - continues chain
    })
    .then(save)
    .catch(error => {
        console.error("Save failed");
    });

// Re-throwing errors
fetchData()
    .catch(error => {
        logError(error);
        throw error; // Re-throw to propagate
    })
    .then(doSomething)
    .catch(handleFinalError);
```

### With async/await

```javascript
// try/catch
async function fetchWithErrorHandling() {
    try {
        const response = await fetch("/api/data");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("Fetch error:", error);
        throw error; // Re-throw if needed
    } finally {
        console.log("Fetch attempt completed");
    }
}

// Error handling wrapper
function asyncHandler(fn) {
    return async (...args) => {
        try {
            return await fn(...args);
        } catch (error) {
            console.error("Error in async function:", error);
            throw error;
        }
    };
}

const safeFetch = asyncHandler(async (url) => {
    const res = await fetch(url);
    return res.json();
});

// Go-style error handling
async function fetchWithGoStyle() {
    const [error, data] = await fetch("/api/data")
        .then(res => res.json())
        .then(data => [null, data])
        .catch(error => [error, null]);
    
    if (error) {
        console.error(error);
        return;
    }
    
    console.log(data);
}
```

---

## 🔄 Converting Between Patterns

### Callback to Promise

```javascript
// Original callback-based function
function delay(ms, callback) {
    setTimeout(() => callback(null, "Done!"), ms);
}

// Promisified version
function delayPromise(ms) {
    return new Promise((resolve, reject) => {
        delay(ms, (err, result) => {
            if (err) reject(err);
            else resolve(result);
        });
    });
}

// Generic promisify function
function promisify(fn) {
    return function(...args) {
        return new Promise((resolve, reject) => {
            fn(...args, (err, result) => {
                if (err) reject(err);
                else resolve(result);
            });
        });
    };
}

const delayAsync = promisify(delay);
```

### Promise to async/await

```javascript
// Original promise chain
function getUserPosts(userId) {
    return fetch(`/api/users/${userId}`)
        .then(res => res.json())
        .then(user => fetch(`/api/posts?author=${user.name}`))
        .then(res => res.json());
}

// Converted to async/await
async function getUserPostsAsync(userId) {
    const userRes = await fetch(`/api/users/${userId}`);
    const user = await userRes.json();
    
    const postsRes = await fetch(`/api/posts?author=${user.name}`);
    return postsRes.json();
}
```

---

## 💡 Practical Patterns

### Retry Pattern

```javascript
async function fetchWithRetry(url, retries = 3, delay = 1000) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await fetch(url);
            if (response.ok) return response.json();
            throw new Error(`HTTP ${response.status}`);
        } catch (error) {
            if (i === retries - 1) throw error;
            console.log(`Retry ${i + 1}/${retries} after ${delay}ms`);
            await new Promise(r => setTimeout(r, delay));
            delay *= 2; // Exponential backoff
        }
    }
}
```

### Timeout Pattern

```javascript
function withTimeout(promise, ms) {
    const timeout = new Promise((_, reject) => 
        setTimeout(() => reject(new Error("Timeout")), ms)
    );
    return Promise.race([promise, timeout]);
}

// Usage
try {
    const data = await withTimeout(fetch("/api/data"), 5000);
} catch (error) {
    if (error.message === "Timeout") {
        console.log("Request took too long");
    }
}
```

### Queue Pattern

```javascript
class AsyncQueue {
    constructor(concurrency = 1) {
        this.concurrency = concurrency;
        this.running = 0;
        this.queue = [];
    }
    
    async add(fn) {
        return new Promise((resolve, reject) => {
            this.queue.push({ fn, resolve, reject });
            this.process();
        });
    }
    
    async process() {
        if (this.running >= this.concurrency || this.queue.length === 0) {
            return;
        }
        
        this.running++;
        const { fn, resolve, reject } = this.queue.shift();
        
        try {
            resolve(await fn());
        } catch (error) {
            reject(error);
        } finally {
            this.running--;
            this.process();
        }
    }
}

// Process 3 tasks at a time
const queue = new AsyncQueue(3);
urls.forEach(url => queue.add(() => fetch(url)));
```

---

## 🔬 Practice Problems

```javascript
// Problem 1: Implement Promise.all
function myPromiseAll(promises) {
    return new Promise((resolve, reject) => {
        const results = [];
        let completed = 0;
        
        promises.forEach((promise, index) => {
            Promise.resolve(promise)
                .then(value => {
                    results[index] = value;
                    completed++;
                    if (completed === promises.length) {
                        resolve(results);
                    }
                })
                .catch(reject);
        });
        
        if (promises.length === 0) resolve([]);
    });
}

// Problem 2: Implement Promise.race
function myPromiseRace(promises) {
    return new Promise((resolve, reject) => {
        promises.forEach(promise => {
            Promise.resolve(promise)
                .then(resolve)
                .catch(reject);
        });
    });
}

// Problem 3: Sequential execution with reduce
async function runSequentially(tasks) {
    return tasks.reduce(
        (promise, task) => promise.then(task),
        Promise.resolve()
    );
}

// Problem 4: Fetch with cache
const cache = new Map();

async function fetchWithCache(url) {
    if (cache.has(url)) {
        return cache.get(url);
    }
    
    const response = await fetch(url);
    const data = await response.json();
    cache.set(url, data);
    return data;
}
```

---

## ✅ Day 12 Checklist

- [ ] Understand callbacks and error-first pattern
- [ ] Know the problems with callback hell
- [ ] Create and use Promises
- [ ] Master Promise chaining
- [ ] Use Promise.all, allSettled, race, any
- [ ] Write async/await code
- [ ] Handle errors with try/catch
- [ ] Convert callbacks to Promises
- [ ] Implement parallel execution
- [ ] Know retry and timeout patterns
- [ ] Complete practice problems
