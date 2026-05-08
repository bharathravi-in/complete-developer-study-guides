# Day 8: Express.js Fundamentals

## 🎯 Learning Objectives
- Set up Express.js applications properly
- Understand middleware architecture
- Master routing and request handling
- Learn error handling patterns

---

## 📚 Express.js Setup

```javascript
const express = require('express');
const app = express();

// Built-in middleware
app.use(express.json());                          // Parse JSON bodies
app.use(express.urlencoded({ extended: true }));  // Parse form data
app.use(express.static('public'));                // Serve static files

// Basic route
app.get('/', (req, res) => {
  res.json({ message: 'Hello Express!' });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

### Project Structure (Production)

```
src/
├── app.js              # Express app setup (no listen)
├── server.js           # Entry point (starts listening)
├── config/
│   ├── index.js        # Configuration management
│   └── database.js     # DB connection
├── routes/
│   ├── index.js        # Route aggregator
│   ├── users.js        # /api/users routes
│   └── posts.js        # /api/posts routes
├── controllers/
│   ├── userController.js
│   └── postController.js
├── services/
│   ├── userService.js  # Business logic
│   └── emailService.js
├── middleware/
│   ├── auth.js
│   ├── validate.js
│   └── errorHandler.js
├── models/
│   └── User.js
└── utils/
    ├── logger.js
    └── errors.js
```

---

## 🔌 Middleware

Middleware functions execute in order and have access to `req`, `res`, and `next`.

```javascript
// Application-level middleware
app.use((req, res, next) => {
  req.requestTime = Date.now();
  console.log(`${req.method} ${req.url}`);
  next(); // Pass to next middleware
});

// Router-level middleware
const router = express.Router();
router.use(authMiddleware);

// Error-handling middleware (4 params)
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.statusCode || 500).json({
    error: { message: err.message, code: err.code }
  });
});

// Middleware order matters!
app.use(cors());           // 1. CORS
app.use(helmet());         // 2. Security headers
app.use(morgan('dev'));    // 3. Logging
app.use(express.json());   // 4. Body parsing
app.use(rateLimit());      // 5. Rate limiting
app.use('/api', router);   // 6. Routes
app.use(errorHandler);     // 7. Error handling (LAST)
```

### Custom Middleware Examples

```javascript
// Request logging with timing
function requestLogger(req, res, next) {
  const start = process.hrtime.bigint();
  
  res.on('finish', () => {
    const duration = Number(process.hrtime.bigint() - start) / 1e6;
    console.log(`${req.method} ${req.url} ${res.statusCode} ${duration.toFixed(1)}ms`);
  });
  
  next();
}

// Rate limiter (simple in-memory)
function rateLimit({ windowMs = 60000, max = 100 } = {}) {
  const requests = new Map();
  
  return (req, res, next) => {
    const ip = req.ip;
    const now = Date.now();
    const windowStart = now - windowMs;
    
    const record = requests.get(ip) || { count: 0, resetAt: now + windowMs };
    
    if (now > record.resetAt) {
      record.count = 0;
      record.resetAt = now + windowMs;
    }
    
    record.count++;
    requests.set(ip, record);
    
    res.setHeader('X-RateLimit-Limit', max);
    res.setHeader('X-RateLimit-Remaining', Math.max(0, max - record.count));
    
    if (record.count > max) {
      return res.status(429).json({ error: 'Too many requests' });
    }
    
    next();
  };
}

// Async middleware wrapper (catches errors)
function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

// Usage
app.get('/users', asyncHandler(async (req, res) => {
  const users = await UserService.findAll();
  res.json(users);
}));
```

---

## 🛣️ Routing

```javascript
const express = require('express');
const router = express.Router();

// Route parameters
router.get('/users/:id', (req, res) => {
  const { id } = req.params;
  res.json({ userId: id });
});

// Multiple parameters
router.get('/users/:userId/posts/:postId', (req, res) => {
  const { userId, postId } = req.params;
  res.json({ userId, postId });
});

// Query parameters
// GET /search?q=hello&page=2&limit=10
router.get('/search', (req, res) => {
  const { q, page = 1, limit = 20 } = req.query;
  res.json({ query: q, page: Number(page), limit: Number(limit) });
});

// Route chaining
router.route('/users/:id')
  .get(getUser)
  .put(validateBody, updateUser)
  .delete(requireAdmin, deleteUser);

// Mount router
app.use('/api/v1', router);
// Routes become: /api/v1/users/:id
```

---

## ⚠️ Error Handling

```javascript
// Custom error classes
class AppError extends Error {
  constructor(message, statusCode, code) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = true;
  }
}

class NotFoundError extends AppError {
  constructor(resource = 'Resource') {
    super(`${resource} not found`, 404, 'NOT_FOUND');
  }
}

class ValidationError extends AppError {
  constructor(errors) {
    super('Validation failed', 400, 'VALIDATION_ERROR');
    this.errors = errors;
  }
}

// Controller with error handling
router.get('/users/:id', asyncHandler(async (req, res) => {
  const user = await User.findById(req.params.id);
  if (!user) throw new NotFoundError('User');
  res.json(user);
}));

// Global error handler
app.use((err, req, res, next) => {
  // Log error
  if (!err.isOperational) {
    console.error('UNEXPECTED ERROR:', err);
  }
  
  const statusCode = err.statusCode || 500;
  const response = {
    error: {
      message: err.isOperational ? err.message : 'Internal Server Error',
      code: err.code || 'INTERNAL_ERROR',
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    }
  };
  
  if (err.errors) response.error.details = err.errors;
  
  res.status(statusCode).json(response);
});

// 404 handler (after all routes)
app.use((req, res) => {
  res.status(404).json({ error: { message: 'Route not found', code: 'NOT_FOUND' } });
});
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is middleware in Express.js?**

Middleware are functions that execute during the request-response cycle with access to `req`, `res`, and `next()`. They can modify request/response objects, end the cycle, or pass control to the next middleware. Express itself is a series of middleware calls.

**Q2: What is the difference between `app.use()` and `app.get()`?**

`app.use()` matches ALL HTTP methods and partial paths (prefix matching). `app.get()` matches only GET requests to the exact path. `app.use('/api')` matches `/api`, `/api/users`, `/api/anything`; `app.get('/api')` only matches `/api`.

**Q3: How do you handle errors in Express?**

Use error-handling middleware (4 parameters: `err, req, res, next`). Throw errors in route handlers — they propagate to the error middleware. For async routes, wrap handlers with a function that catches rejected promises and calls `next(err)`.

### Intermediate

**Q4: Explain the Express.js request lifecycle.**

1. Request arrives → 2. Middleware execute in order (logging, auth, parsing) → 3. Route matching → 4. Route handler executes → 5. Response sent OR `next()` → 6. Error handler (if error thrown) → 7. Response finalized. If no route matches, 404 handler fires.

**Q5: How would you implement API versioning in Express?**

Options: (1) URL path: `/api/v1/users`, `/api/v2/users` with separate routers. (2) Header: `Accept: application/vnd.api.v2+json`. (3) Query param: `?version=2`. URL path is most common and explicit. Mount versioned routers: `app.use('/api/v1', v1Router)`.

**Q6: What is `express.Router()` and why use it?**

Router is a mini-application with its own middleware and routes. It modularizes code — each resource gets its own router file. Routers can be mounted at specific paths. They support all routing methods and can have their own middleware stack, enabling clean separation of concerns.

### Advanced

**Q7: How would you handle graceful shutdown in Express?**

```javascript
const server = app.listen(3000);
process.on('SIGTERM', () => {
  server.close(() => {
    // Close DB connections, flush logs
    process.exit(0);
  });
  setTimeout(() => process.exit(1), 30000); // Force after 30s
});
```
Also: stop health checks first (let LB drain), track in-flight requests, close keep-alive connections.

**Q8: How do you prevent Express performance issues at scale?**

Disable `x-powered-by`, use compression middleware, implement response caching (ETags, Cache-Control), use connection pooling, avoid synchronous code, set proper timeouts (`server.timeout`, `server.keepAliveTimeout`), use reverse proxy (Nginx) for static files, implement request size limits.

**Q9: Compare Express.js with Fastify and Koa.**

Express: mature, huge ecosystem, middleware-based, callback-style. Koa: lightweight, async/await native, no built-in middleware, better error handling with `ctx`. Fastify: fastest (schema-based serialization), built-in validation, plugin architecture, TypeScript-first. For new projects: Fastify for performance, Express for ecosystem.

---

## 🛠️ Hands-on Exercise

Build a production-ready Express API boilerplate:
1. Project structure with separate concerns
2. Custom error handling with operational vs programming errors
3. Request validation middleware
4. Rate limiting per IP
5. Request logging with response time
6. Graceful shutdown
