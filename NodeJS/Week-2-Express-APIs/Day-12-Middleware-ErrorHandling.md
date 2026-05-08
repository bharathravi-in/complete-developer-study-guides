# Day 12: Middleware Patterns & Error Handling

## 🎯 Learning Objectives
- Master advanced middleware patterns
- Implement comprehensive error handling
- Build reusable middleware libraries
- Understand middleware composition

---

## 📚 Advanced Middleware Patterns

### Composable Middleware

```javascript
// Middleware factory pattern
function validate(schema, source = 'body') {
  return (req, res, next) => {
    const { error, value } = schema.validate(req[source], { abortEarly: false });
    if (error) {
      return next(new ValidationError(error.details));
    }
    req[source] = value;
    next();
  };
}

// Conditional middleware
function unless(middleware, ...paths) {
  return (req, res, next) => {
    if (paths.some(p => req.path.startsWith(p))) {
      return next();
    }
    middleware(req, res, next);
  };
}

// Apply auth to all routes EXCEPT public ones
app.use(unless(authenticate, '/auth', '/public', '/health'));

// Middleware composition
function compose(...middlewares) {
  return (req, res, next) => {
    let index = 0;
    function dispatch() {
      if (index >= middlewares.length) return next();
      const middleware = middlewares[index++];
      middleware(req, res, dispatch);
    }
    dispatch();
  };
}

const secured = compose(authenticate, authorize('admin'), auditLog);
router.delete('/users/:id', secured, deleteUser);
```

### Request Context & Correlation IDs

```javascript
const { v4: uuid } = require('uuid');
const { AsyncLocalStorage } = require('async_hooks');

const requestContext = new AsyncLocalStorage();

// Attach correlation ID to every request
function correlationId(req, res, next) {
  const id = req.headers['x-correlation-id'] || uuid();
  req.correlationId = id;
  res.setHeader('X-Correlation-ID', id);
  
  // Store in async context (accessible anywhere without passing req)
  requestContext.run({ correlationId: id, userId: req.user?.id }, next);
}

// Access anywhere in the codebase
function getCorrelationId() {
  return requestContext.getStore()?.correlationId;
}

// Logger automatically includes correlation ID
function log(message, data = {}) {
  const store = requestContext.getStore();
  console.log(JSON.stringify({
    timestamp: new Date().toISOString(),
    correlationId: store?.correlationId,
    userId: store?.userId,
    message,
    ...data
  }));
}
```

### Caching Middleware

```javascript
// In-memory cache with TTL
function cache(ttlSeconds = 60) {
  const store = new Map();
  
  return (req, res, next) => {
    if (req.method !== 'GET') return next();
    
    const key = req.originalUrl;
    const cached = store.get(key);
    
    if (cached && Date.now() < cached.expiry) {
      res.setHeader('X-Cache', 'HIT');
      return res.json(cached.data);
    }
    
    // Override res.json to cache the response
    const originalJson = res.json.bind(res);
    res.json = (data) => {
      store.set(key, { data, expiry: Date.now() + ttlSeconds * 1000 });
      res.setHeader('X-Cache', 'MISS');
      return originalJson(data);
    };
    
    next();
  };
}

router.get('/api/posts', cache(300), getPosts); // Cache for 5 minutes

// Cache invalidation
function invalidateCache(pattern) {
  return (req, res, next) => {
    // Clear matching cache entries after mutation
    res.on('finish', () => {
      if (res.statusCode < 400) {
        // Clear related caches
        for (const [key] of store) {
          if (key.includes(pattern)) store.delete(key);
        }
      }
    });
    next();
  };
}
```

---

## ⚠️ Comprehensive Error Handling

### Error Hierarchy

```javascript
// Base error class
class AppError extends Error {
  constructor(message, statusCode = 500, code = 'INTERNAL_ERROR') {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = true;
    Error.captureStackTrace(this, this.constructor);
  }
}

class NotFoundError extends AppError {
  constructor(resource = 'Resource') {
    super(`${resource} not found`, 404, 'NOT_FOUND');
  }
}

class ValidationError extends AppError {
  constructor(details) {
    super('Validation failed', 400, 'VALIDATION_ERROR');
    this.details = details;
  }
}

class UnauthorizedError extends AppError {
  constructor(message = 'Authentication required') {
    super(message, 401, 'UNAUTHORIZED');
  }
}

class ForbiddenError extends AppError {
  constructor(message = 'Insufficient permissions') {
    super(message, 403, 'FORBIDDEN');
  }
}

class ConflictError extends AppError {
  constructor(message = 'Resource already exists') {
    super(message, 409, 'CONFLICT');
  }
}
```

### Global Error Handler

```javascript
function errorHandler(err, req, res, next) {
  // Default values
  let statusCode = err.statusCode || 500;
  let message = err.message || 'Internal Server Error';
  let code = err.code || 'INTERNAL_ERROR';
  let details = err.details || null;
  
  // Handle specific error types
  if (err.name === 'CastError') {
    statusCode = 400;
    message = 'Invalid ID format';
    code = 'INVALID_ID';
  }
  
  if (err.code === 11000) { // MongoDB duplicate key
    statusCode = 409;
    const field = Object.keys(err.keyValue)[0];
    message = `${field} already exists`;
    code = 'DUPLICATE';
  }
  
  if (err.name === 'JsonWebTokenError') {
    statusCode = 401;
    message = 'Invalid token';
    code = 'INVALID_TOKEN';
  }
  
  if (err.type === 'entity.too.large') {
    statusCode = 413;
    message = 'Request body too large';
    code = 'PAYLOAD_TOO_LARGE';
  }
  
  // Log error
  if (statusCode >= 500) {
    console.error('SERVER ERROR:', {
      message: err.message,
      stack: err.stack,
      url: req.originalUrl,
      method: req.method,
      correlationId: req.correlationId
    });
  }
  
  // Response
  const response = {
    error: { message, code, statusCode }
  };
  
  if (details) response.error.details = details;
  if (process.env.NODE_ENV === 'development') response.error.stack = err.stack;
  
  res.status(statusCode).json(response);
}

// Catch unhandled routes (404)
app.use('*', (req, res) => {
  res.status(404).json({
    error: { message: `Route ${req.method} ${req.originalUrl} not found`, code: 'ROUTE_NOT_FOUND' }
  });
});

// Error handler must be last
app.use(errorHandler);
```

### Async Error Wrapper

```javascript
// Wraps async route handlers to catch errors
function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

// With Express 5+ this is built-in, but for Express 4:
router.get('/users/:id', asyncHandler(async (req, res) => {
  const user = await User.findById(req.params.id);
  if (!user) throw new NotFoundError('User');
  res.json({ data: user });
}));

// Alternative: express-async-errors (monkey-patches Express)
require('express-async-errors');
// Now async errors are caught automatically
```

---

## 📊 Request Logging & Monitoring

```javascript
const morgan = require('morgan');

// Custom token for response time
morgan.token('response-time-ms', (req, res) => {
  const diff = process.hrtime(req._startTime);
  return (diff[0] * 1e3 + diff[1] / 1e6).toFixed(1);
});

// Structured JSON logging (for production)
app.use((req, res, next) => {
  req._startTime = process.hrtime();
  
  res.on('finish', () => {
    const duration = process.hrtime(req._startTime);
    const ms = (duration[0] * 1e3 + duration[1] / 1e6).toFixed(1);
    
    const logEntry = {
      timestamp: new Date().toISOString(),
      method: req.method,
      url: req.originalUrl,
      status: res.statusCode,
      duration: `${ms}ms`,
      ip: req.ip,
      userAgent: req.get('user-agent'),
      correlationId: req.correlationId,
      userId: req.user?.id
    };
    
    if (res.statusCode >= 400) {
      console.error(JSON.stringify(logEntry));
    } else {
      console.log(JSON.stringify(logEntry));
    }
  });
  
  next();
});
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is the difference between application-level and router-level middleware?**

Application-level: attached to `app` instance via `app.use()` — runs for ALL requests. Router-level: attached to `express.Router()` — runs only for routes on that router. Use router-level for modular middleware (auth on specific route groups). Both work identically except scope.

**Q2: Why is middleware order important in Express?**

Middleware executes sequentially — order defines the pipeline. Body parser must come before route handlers. Auth must come before protected routes. Error handler must be last (4 params). CORS must be early. Logging should be first to capture all requests including failures.

**Q3: How do you handle async errors in Express 4?**

Express 4 doesn't automatically catch rejected promises. Solutions: (1) Wrap every async handler with try/catch and call `next(err)`. (2) Use a wrapper function: `asyncHandler(fn)` that catches rejections. (3) Use `express-async-errors` package. Express 5 handles this natively.

### Intermediate

**Q4: How would you implement request validation middleware that works for body, params, and query?**

Create a factory function that accepts a schema and source ('body', 'params', 'query'): `validate(schema, 'body')`. Validate the corresponding `req[source]` against the schema. Replace `req[source]` with sanitized value. Return 400 with structured error details on failure.

**Q5: What is the AsyncLocalStorage and how does it help with request context?**

`AsyncLocalStorage` (from `async_hooks`) provides a context that follows async operations without explicit passing. Store request-scoped data (correlation ID, user) at the start. Access it anywhere in the call chain (services, logger) without threading `req` through every function. Useful for structured logging and tracing.

**Q6: How would you implement a circuit breaker middleware?**

Track failure count for external service calls. States: CLOSED (normal), OPEN (reject immediately after threshold failures), HALF-OPEN (allow one test request after cooldown). On OPEN: return 503 instantly. On success in HALF-OPEN: close circuit. Prevents cascading failures when downstream services are down.

### Advanced

**Q7: Design an idempotency middleware for POST/PUT requests.**

Accept `Idempotency-Key` header. On first request: process normally, cache the response (key → response) with TTL. On subsequent requests with same key: return cached response without re-processing. Use Redis for distributed systems. Handle race conditions with distributed locks. Required for payment APIs.

**Q8: How would you implement request rate limiting that works across multiple instances?**

Use Redis with sliding window or token bucket algorithm. Key: `ratelimit:{ip}:{window}`. Use `MULTI/EXEC` for atomic increment + TTL. Alternatives: leaky bucket (smooth traffic), fixed window counter (simple). Return `X-RateLimit-*` headers. For API keys: per-key limits with different tiers.

**Q9: Explain how to build middleware that supports both Express and Fastify.**

Create framework-agnostic core logic that accepts normalized request/response objects. Write thin adapters for each framework. Express adapter: `(req, res, next) → normalize → core logic → denormalize`. Fastify adapter: plugin with `(request, reply) → normalize → core logic`. Publish as separate packages or with factory pattern.

---

## 🛠️ Hands-on Exercise

Build a middleware library with:
1. Request correlation ID tracking
2. Structured JSON logger (with context from AsyncLocalStorage)
3. Rate limiting (in-memory + Redis adapter)
4. Response caching with invalidation
5. Circuit breaker for external API calls
6. Comprehensive error handler with error hierarchy
