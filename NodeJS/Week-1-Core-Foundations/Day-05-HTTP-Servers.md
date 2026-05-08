# Day 5: HTTP Module & Building Servers from Scratch

## 🎯 Learning Objectives
- Build HTTP servers using only core `http` module
- Understand request/response lifecycle
- Handle routing, query params, and body parsing
- Learn about HTTP/2 and HTTPS in Node.js

---

## 📚 Core HTTP Module

### Basic HTTP Server

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
  // req = IncomingMessage (readable stream)
  // res = ServerResponse (writable stream)
  
  console.log(`${req.method} ${req.url}`);
  console.log('Headers:', req.headers);
  
  res.writeHead(200, { 
    'Content-Type': 'application/json',
    'X-Powered-By': 'Node.js'
  });
  res.end(JSON.stringify({ message: 'Hello World', timestamp: Date.now() }));
});

server.listen(3000, '0.0.0.0', () => {
  console.log('Server running on http://localhost:3000');
});

// Graceful shutdown
process.on('SIGTERM', () => {
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
});
```

### Request Body Parsing

```javascript
const http = require('http');

function parseBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', chunk => chunks.push(chunk));
    req.on('end', () => {
      const body = Buffer.concat(chunks).toString();
      const contentType = req.headers['content-type'] || '';
      
      if (contentType.includes('application/json')) {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(new Error('Invalid JSON'));
        }
      } else if (contentType.includes('application/x-www-form-urlencoded')) {
        resolve(Object.fromEntries(new URLSearchParams(body)));
      } else {
        resolve(body);
      }
    });
    req.on('error', reject);
  });
}

const server = http.createServer(async (req, res) => {
  if (req.method === 'POST') {
    const body = await parseBody(req);
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ received: body }));
  }
});
```

### URL & Query Parameter Parsing

```javascript
const http = require('http');
const { URL } = require('url');

const server = http.createServer((req, res) => {
  // Parse URL (use base URL for relative paths)
  const url = new URL(req.url, `http://${req.headers.host}`);
  
  console.log({
    pathname: url.pathname,      // '/api/users'
    search: url.search,          // '?page=2&limit=10'
    searchParams: Object.fromEntries(url.searchParams)  // { page: '2', limit: '10' }
  });
  
  // Route matching
  const pathParts = url.pathname.split('/').filter(Boolean);
  // '/api/users/123' → ['api', 'users', '123']
  
  res.end('OK');
});
```

---

## 🛣️ Building a Simple Router

```javascript
const http = require('http');

class Router {
  constructor() {
    this.routes = { GET: {}, POST: {}, PUT: {}, DELETE: {} };
  }
  
  get(path, handler) { this.routes.GET[path] = handler; }
  post(path, handler) { this.routes.POST[path] = handler; }
  put(path, handler) { this.routes.PUT[path] = handler; }
  delete(path, handler) { this.routes.DELETE[path] = handler; }
  
  // Simple pattern matching: '/users/:id' → { id: '123' }
  matchRoute(method, pathname) {
    const routes = this.routes[method] || {};
    
    for (const [pattern, handler] of Object.entries(routes)) {
      const patternParts = pattern.split('/');
      const pathParts = pathname.split('/');
      
      if (patternParts.length !== pathParts.length) continue;
      
      const params = {};
      let match = true;
      
      for (let i = 0; i < patternParts.length; i++) {
        if (patternParts[i].startsWith(':')) {
          params[patternParts[i].slice(1)] = pathParts[i];
        } else if (patternParts[i] !== pathParts[i]) {
          match = false;
          break;
        }
      }
      
      if (match) return { handler, params };
    }
    return null;
  }
  
  async handle(req, res) {
    const url = new URL(req.url, `http://${req.headers.host}`);
    const route = this.matchRoute(req.method, url.pathname);
    
    if (!route) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Not Found' }));
      return;
    }
    
    req.params = route.params;
    req.query = Object.fromEntries(url.searchParams);
    
    try {
      await route.handler(req, res);
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Internal Server Error' }));
    }
  }
}

// Usage
const router = new Router();
const users = [{ id: '1', name: 'Alice' }, { id: '2', name: 'Bob' }];

router.get('/api/users', (req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(users));
});

router.get('/api/users/:id', (req, res) => {
  const user = users.find(u => u.id === req.params.id);
  if (!user) {
    res.writeHead(404).end(JSON.stringify({ error: 'User not found' }));
    return;
  }
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(user));
});

const server = http.createServer((req, res) => router.handle(req, res));
server.listen(3000);
```

---

## 🔒 HTTPS & HTTP/2

```javascript
const https = require('https');
const http2 = require('http2');
const fs = require('fs');

// HTTPS Server
const options = {
  key: fs.readFileSync('private-key.pem'),
  cert: fs.readFileSync('certificate.pem')
};

const httpsServer = https.createServer(options, (req, res) => {
  res.writeHead(200);
  res.end('Secure!');
});
httpsServer.listen(443);

// HTTP/2 Server (with TLS)
const h2Server = http2.createSecureServer(options);
h2Server.on('stream', (stream, headers) => {
  stream.respond({ ':status': 200, 'content-type': 'text/html' });
  stream.end('<h1>Hello HTTP/2</h1>');
  
  // Server Push
  stream.pushStream({ ':path': '/style.css' }, (err, pushStream) => {
    pushStream.respond({ ':status': 200, 'content-type': 'text/css' });
    pushStream.end('body { color: red; }');
  });
});
h2Server.listen(443);
```

---

## 🌐 Making HTTP Requests

```javascript
const http = require('http');
const https = require('https');

// Built-in (verbose but no dependencies)
function httpGet(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      const chunks = [];
      res.on('data', chunk => chunks.push(chunk));
      res.on('end', () => {
        const body = Buffer.concat(chunks).toString();
        resolve({ status: res.statusCode, body: JSON.parse(body) });
      });
    }).on('error', reject);
  });
}

// Node.js 18+ built-in fetch
const response = await fetch('https://api.example.com/data', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ key: 'value' }),
  signal: AbortSignal.timeout(5000) // 5s timeout
});
const data = await response.json();
```

---

## 🧪 Interview Questions

### Beginner

**Q1: How does `http.createServer()` work under the hood?**

It creates a `Server` instance that listens for TCP connections. For each connection, it parses the HTTP request (method, headers, URL), creates `IncomingMessage` and `ServerResponse` objects, and calls the request handler. The server uses the event loop to handle multiple connections on a single thread.

**Q2: What is the difference between `res.write()` and `res.end()`?**

`res.write()` sends a chunk of response body (can be called multiple times for streaming). `res.end()` signals that the response is complete — it optionally takes final data and sends the response. You MUST call `end()` or the client hangs waiting for more data.

**Q3: How do you parse query parameters from a URL in Node.js?**

Use the `URL` class: `new URL(req.url, 'http://localhost')`. Access params via `.searchParams` (a `URLSearchParams` object). Methods: `.get('key')`, `.getAll('key')`, or convert to object: `Object.fromEntries(url.searchParams)`.

### Intermediate

**Q4: How would you implement request body size limits to prevent DoS attacks?**

Track accumulated body size in the `data` event. If it exceeds a threshold (e.g., 1MB), destroy the request with a 413 status. Also set `server.maxHeadersCount` and `server.headersTimeout`. In Express: `express.json({ limit: '1mb' })`.

**Q5: Explain the difference between HTTP/1.1, HTTP/2, and HTTP/3 from a Node.js perspective.**

HTTP/1.1: text-based, one request per connection (or keep-alive). HTTP/2: binary framing, multiplexing (multiple requests on one connection), server push, header compression. Node supports both via `http` and `http2` modules. HTTP/3 uses QUIC (UDP), not yet fully native in Node.

**Q6: How does Node.js handle keep-alive connections?**

HTTP/1.1 defaults to keep-alive — the TCP connection stays open for multiple requests. `server.keepAliveTimeout` (default 5s) controls idle time before closing. This reduces latency (no TCP handshake per request) but consumes file descriptors. Monitor with `server.getConnections()`.

### Advanced

**Q7: How would you implement graceful shutdown for an HTTP server?**

Call `server.close()` — it stops accepting new connections but lets existing requests finish. Set a timeout (e.g., 30s) to force-close lingering connections. Track active connections and close idle ones. Handle SIGTERM/SIGINT signals. Drain health check endpoints first so load balancers stop routing traffic.

**Q8: How does backpressure affect HTTP response streaming?**

If you `res.write()` faster than the client can receive (slow network), the kernel buffer fills, `write()` returns `false`. You must pause your data source and wait for the `drain` event. Using `pipeline(readable, res)` handles this automatically. Without it, memory grows for slow clients (Slowloris-like effect).

**Q9: How would you implement request rate limiting using only the core `http` module?**

Use a Map with IP → { count, timestamp }. On each request, check/update the counter. Reset counts after the window expires. For distributed systems, use Redis with sliding window or token bucket algorithms. Consider: X-Forwarded-For behind proxies, exponential backoff in 429 responses.

---

## 🛠️ Hands-on Exercise

Build a REST API server using ONLY the core `http` module:
1. Router with parameter extraction (`/users/:id`)
2. JSON body parsing with size limits
3. CORS headers middleware
4. Request logging with timing
5. Graceful shutdown on SIGTERM
