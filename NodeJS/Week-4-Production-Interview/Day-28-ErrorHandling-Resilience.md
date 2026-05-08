# Day 28: Error Handling & Resilience Patterns

## 🎯 Learning Objectives
- Build robust error handling hierarchies
- Implement circuit breaker, bulkhead, and retry patterns
- Handle graceful shutdown and recovery
- Design for failure in distributed systems

---

## 📚 Error Handling Architecture

### Error Hierarchy

```javascript
// Base application error
class AppError extends Error {
  constructor(message, statusCode, code, isOperational = true) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
    this.isOperational = isOperational; // vs programmer error
    this.timestamp = new Date().toISOString();
    Error.captureStackTrace(this, this.constructor);
  }
}

class ValidationError extends AppError {
  constructor(errors) {
    super('Validation failed', 400, 'VALIDATION_ERROR');
    this.errors = errors; // [{ field, message }]
  }
}

class NotFoundError extends AppError {
  constructor(resource, id) {
    super(`${resource} with id ${id} not found`, 404, 'NOT_FOUND');
  }
}

class ConflictError extends AppError {
  constructor(message) { super(message, 409, 'CONFLICT'); }
}

class UnauthorizedError extends AppError {
  constructor(message = 'Authentication required') { super(message, 401, 'UNAUTHORIZED'); }
}

class ExternalServiceError extends AppError {
  constructor(service, originalError) {
    super(`${service} service failed`, 502, 'EXTERNAL_SERVICE_ERROR');
    this.service = service;
    this.originalError = originalError;
  }
}
```

### Global Error Handler

```javascript
// Express error handler (must be last middleware)
function errorHandler(err, req, res, next) {
  // Log error
  if (err.isOperational) {
    logger.warn({ err, requestId: req.id }, err.message);
  } else {
    logger.error({ err, requestId: req.id }, 'Unexpected error');
    // Alert on programmer errors
    Sentry.captureException(err);
  }

  // Send response
  const statusCode = err.statusCode || 500;
  res.status(statusCode).json({
    error: {
      code: err.code || 'INTERNAL_ERROR',
      message: err.isOperational ? err.message : 'An unexpected error occurred',
      ...(err.errors && { details: err.errors }),
      ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
    }
  });
}

// Catch unhandled rejections and exceptions
process.on('unhandledRejection', (reason) => {
  logger.fatal({ err: reason }, 'Unhandled rejection — shutting down');
  gracefulShutdown(1);
});

process.on('uncaughtException', (error) => {
  logger.fatal({ err: error }, 'Uncaught exception — shutting down');
  gracefulShutdown(1);
});
```

---

## 📚 Resilience Patterns

### Circuit Breaker

```javascript
class CircuitBreaker {
  #state = 'CLOSED'; // CLOSED → OPEN → HALF_OPEN
  #failureCount = 0;
  #successCount = 0;
  #lastFailureTime = null;

  constructor(options = {}) {
    this.failureThreshold = options.failureThreshold || 5;
    this.resetTimeout = options.resetTimeout || 30000; // 30s
    this.halfOpenMax = options.halfOpenMax || 3;
  }

  get state() { return this.#state; }

  async execute(fn) {
    if (this.#state === 'OPEN') {
      if (Date.now() - this.#lastFailureTime > this.resetTimeout) {
        this.#state = 'HALF_OPEN';
        this.#successCount = 0;
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }

    try {
      const result = await fn();
      this.#onSuccess();
      return result;
    } catch (error) {
      this.#onFailure();
      throw error;
    }
  }

  #onSuccess() {
    if (this.#state === 'HALF_OPEN') {
      this.#successCount++;
      if (this.#successCount >= this.halfOpenMax) {
        this.#state = 'CLOSED';
        this.#failureCount = 0;
      }
    }
    this.#failureCount = 0;
  }

  #onFailure() {
    this.#failureCount++;
    this.#lastFailureTime = Date.now();
    if (this.#failureCount >= this.failureThreshold) {
      this.#state = 'OPEN';
    }
  }
}

// Usage
const paymentBreaker = new CircuitBreaker({ failureThreshold: 3, resetTimeout: 60000 });

async function processPayment(order) {
  return paymentBreaker.execute(async () => {
    return await paymentGateway.charge(order.amount, order.paymentMethod);
  });
}
```

### Retry with Exponential Backoff

```javascript
async function withRetry(fn, options = {}) {
  const { maxRetries = 3, baseDelay = 1000, maxDelay = 30000, factor = 2, retryOn } = options;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn(attempt);
    } catch (error) {
      const isLastAttempt = attempt === maxRetries;
      const shouldRetry = retryOn ? retryOn(error) : true;
      
      if (isLastAttempt || !shouldRetry) throw error;

      const delay = Math.min(baseDelay * Math.pow(factor, attempt), maxDelay);
      const jitter = delay * (0.5 + Math.random() * 0.5); // Add jitter
      
      logger.warn({ attempt: attempt + 1, delay: jitter, error: error.message }, 'Retrying');
      await new Promise(resolve => setTimeout(resolve, jitter));
    }
  }
}

// Usage
const result = await withRetry(
  () => externalApi.call(params),
  {
    maxRetries: 3,
    baseDelay: 1000,
    retryOn: (err) => err.statusCode >= 500 || err.code === 'ECONNRESET'
  }
);
```

### Bulkhead Pattern (Isolation)

```javascript
// Limit concurrent requests to protect resources
class Bulkhead {
  #running = 0;
  #queue = [];

  constructor(maxConcurrent, maxQueue = 100) {
    this.maxConcurrent = maxConcurrent;
    this.maxQueue = maxQueue;
  }

  async execute(fn) {
    if (this.#running >= this.maxConcurrent) {
      if (this.#queue.length >= this.maxQueue) {
        throw new Error('Bulkhead queue full — service overloaded');
      }
      await new Promise((resolve, reject) => {
        this.#queue.push({ resolve, reject });
      });
    }

    this.#running++;
    try {
      return await fn();
    } finally {
      this.#running--;
      if (this.#queue.length > 0) {
        const { resolve } = this.#queue.shift();
        resolve();
      }
    }
  }
}

// Isolate different services
const paymentBulkhead = new Bulkhead(10);   // Max 10 concurrent payment calls
const emailBulkhead = new Bulkhead(50);     // Max 50 concurrent emails
const dbBulkhead = new Bulkhead(20);        // Max 20 concurrent DB queries
```

### Graceful Shutdown

```javascript
async function gracefulShutdown(exitCode = 0) {
  logger.info('Graceful shutdown initiated');
  const timeout = setTimeout(() => {
    logger.error('Forced shutdown — timeout exceeded');
    process.exit(1);
  }, 30000);

  try {
    // 1. Stop accepting new requests
    server.close();
    
    // 2. Finish in-flight requests (server.close waits)
    
    // 3. Close external connections
    await Promise.allSettled([
      database.disconnect(),
      redis.quit(),
      messageQueue.close(),
    ]);

    // 4. Flush logs/metrics
    await logger.flush();
    
    clearTimeout(timeout);
    logger.info('Shutdown complete');
    process.exit(exitCode);
  } catch (error) {
    logger.error({ error }, 'Error during shutdown');
    process.exit(1);
  }
}

process.on('SIGTERM', () => gracefulShutdown(0));
process.on('SIGINT', () => gracefulShutdown(0));
```

---

## 🧪 Interview Questions

### Beginner
**Q1: What's the difference between operational errors and programmer errors?**
Operational: expected failures (network timeout, invalid input, disk full) — handle gracefully. Programmer: bugs (TypeError, undefined access) — crash and restart. Operational errors: return error response. Programmer errors: log, alert, restart process. Use `isOperational` flag on custom errors.

**Q2: How do you handle async errors in Express?**
Express doesn't catch async errors automatically. Solutions: (1) Wrap routes: `asyncHandler(fn) => (req, res, next) => fn(req, res, next).catch(next)`. (2) Express 5+ handles async automatically. (3) Libraries like express-async-errors. Always have a global error handler middleware as the last middleware.

**Q3: What is a circuit breaker and why is it needed?**
Prevents cascading failures. When a dependency fails repeatedly → stop calling it (open circuit) → return fast failure. After timeout → try a few requests (half-open) → if successful, close circuit. Prevents: overwhelming failing services, cascading timeouts, resource exhaustion from retries.

### Intermediate
**Q4: How do you implement graceful shutdown in Node.js?**
On SIGTERM/SIGINT: (1) Stop accepting new connections (`server.close()`). (2) Wait for in-flight requests to complete. (3) Close database/Redis/queue connections. (4) Flush logs. (5) Exit. Set a timeout for force kill (30s). Kubernetes sends SIGTERM before SIGKILL. Don't abruptly kill connections.

**Q5: Explain the bulkhead pattern and when to use it.**
Isolate resource pools so one failing dependency doesn't exhaust all resources. Example: limit concurrent calls to payment service to 10 — even if it's slow, it can't consume all your connection pool. Like ship bulkheads: flooding one compartment doesn't sink the ship. Use for external service calls, database connections.

**Q6: How do you implement retry logic without causing thundering herd?**
Exponential backoff: increase delay between retries (1s, 2s, 4s, 8s). Add jitter: randomize delay to spread retries. Cap max delay. Limit retries (3-5). Only retry retryable errors (5xx, timeout — not 4xx). Circuit breaker on top: stop retrying if service is clearly down.

### Advanced
**Q7: Design a resilient payment processing system that handles partial failures.**
Idempotency key for every request (dedup retries). Saga pattern: reserve → charge → confirm (compensate on failure). Circuit breaker per payment provider. Fallback provider if primary down. Async confirmation (queue → worker). Reconciliation job for stuck transactions. Two-phase: write to DB first, then call provider.

**Q8: How would you handle a cascading failure across microservices?**
Prevention: circuit breakers on all inter-service calls, bulkheads (limit connections per service), timeouts (never wait forever), retry budgets (limit total retries system-wide). Detection: error rate monitoring, latency percentiles. Recovery: graceful degradation (serve cached/default data), load shedding (reject low-priority requests).

**Q9: Implement a dead letter queue strategy for failed messages in a distributed system.**
Architecture: Main Queue → Worker → on failure after N retries → DLQ. DLQ processing: (1) Alert on new DLQ messages. (2) Dashboard to inspect failed messages. (3) Manual/automatic replay after fix. (4) Categorize failures (poison messages vs transient). Retention: keep for 14 days. Monitoring: DLQ depth metric + alerting.

---

## 🛠️ Hands-on Exercise
Build a resilient service layer:
1. Custom error hierarchy (5+ error types)
2. Circuit breaker wrapping an external API
3. Retry with exponential backoff + jitter
4. Bulkhead limiting concurrent operations
5. Graceful shutdown handling
6. Combine all patterns in a payment service
