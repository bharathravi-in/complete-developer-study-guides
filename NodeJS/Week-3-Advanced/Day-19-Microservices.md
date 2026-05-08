# Day 19: Microservices with Node.js

## 🎯 Learning Objectives
- Design and build microservices in Node.js
- Implement inter-service communication (REST, gRPC, events)
- Handle service discovery and API gateway patterns
- Understand distributed system challenges

---

## 📚 Microservices Architecture

### Monolith vs Microservices

```
Monolith:                         Microservices:
┌─────────────────────┐           ┌──────┐  ┌──────┐  ┌──────┐
│  All Code Together  │           │ User │  │ Post │  │ Notif│
│  - Users            │    →      │ Svc  │  │ Svc  │  │ Svc  │
│  - Posts            │           └──┬───┘  └──┬───┘  └──┬───┘
│  - Notifications    │              │         │         │
│  - Payments         │           ┌──┴─────────┴─────────┴──┐
└─────────────────────┘           │     Message Broker       │
                                  └──────────────────────────┘
```

### Service Template

```javascript
// src/index.js - Microservice entry point
const express = require('express');
const { connectDB } = require('./config/database');
const { connectRedis } = require('./config/redis');
const { setupMessageBroker } = require('./config/messaging');
const routes = require('./routes');
const { errorHandler } = require('./middleware/error');
const { healthCheck } = require('./routes/health');

const app = express();

app.use(express.json());
app.get('/health', healthCheck);
app.use('/api', routes);
app.use(errorHandler);

async function start() {
  await connectDB();
  await connectRedis();
  await setupMessageBroker();
  
  const PORT = process.env.PORT || 3001;
  const server = app.listen(PORT, () => {
    console.log(`User Service running on port ${PORT}`);
  });
  
  // Graceful shutdown
  const shutdown = async () => {
    server.close();
    await disconnectDB();
    await disconnectRedis();
    process.exit(0);
  };
  
  process.on('SIGTERM', shutdown);
  process.on('SIGINT', shutdown);
}

start().catch(console.error);
```

---

## 🔗 Inter-Service Communication

### Synchronous (REST/gRPC)

```javascript
// HTTP client with retry and circuit breaker
const axios = require('axios');
const CircuitBreaker = require('opossum');

function createServiceClient(baseURL, options = {}) {
  const client = axios.create({
    baseURL,
    timeout: options.timeout || 5000,
    headers: { 'Content-Type': 'application/json' }
  });
  
  // Add correlation ID forwarding
  client.interceptors.request.use((config) => {
    const store = requestContext.getStore();
    if (store?.correlationId) {
      config.headers['X-Correlation-ID'] = store.correlationId;
    }
    return config;
  });
  
  // Wrap with circuit breaker
  const breaker = new CircuitBreaker(
    (config) => client.request(config),
    {
      timeout: 10000,
      errorThresholdPercentage: 50,
      resetTimeout: 30000
    }
  );
  
  breaker.on('open', () => console.warn(`Circuit OPEN for ${baseURL}`));
  breaker.on('halfOpen', () => console.info(`Circuit HALF-OPEN for ${baseURL}`));
  breaker.on('close', () => console.info(`Circuit CLOSED for ${baseURL}`));
  
  return {
    get: (path) => breaker.fire({ method: 'GET', url: path }),
    post: (path, data) => breaker.fire({ method: 'POST', url: path, data }),
  };
}

// Usage
const userService = createServiceClient('http://user-service:3001');
const postService = createServiceClient('http://post-service:3002');

// In a route handler
router.get('/feed', async (req, res) => {
  const [user, posts] = await Promise.all([
    userService.get(`/api/users/${req.user.id}`),
    postService.get(`/api/posts?userId=${req.user.id}`)
  ]);
  res.json({ user: user.data, posts: posts.data });
});
```

### Asynchronous (Event-Driven)

```javascript
// Event publisher (User Service)
const { publishEvent } = require('./messaging');

async function createUser(data) {
  const user = await User.create(data);
  
  // Publish event (other services react independently)
  await publishEvent('user.created', {
    userId: user.id,
    email: user.email,
    name: user.name,
    timestamp: new Date().toISOString()
  });
  
  return user;
}

// Event consumer (Notification Service)
const { subscribe } = require('./messaging');

subscribe('user.created', async (event) => {
  await sendWelcomeEmail(event.email, event.name);
  await createNotification(event.userId, 'Welcome!');
});

subscribe('order.completed', async (event) => {
  await sendOrderConfirmation(event.userId, event.orderId);
});
```

---

## 🚪 API Gateway Pattern

```javascript
// Simple API Gateway with Express
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const rateLimit = require('express-rate-limit');

const app = express();

// Rate limiting at gateway level
app.use(rateLimit({ windowMs: 60000, max: 100 }));

// Authentication at gateway
app.use('/api', authenticate);

// Route to services
app.use('/api/users', createProxyMiddleware({
  target: 'http://user-service:3001',
  pathRewrite: { '^/api/users': '/api/users' },
  changeOrigin: true
}));

app.use('/api/posts', createProxyMiddleware({
  target: 'http://post-service:3002',
  pathRewrite: { '^/api/posts': '/api/posts' },
  changeOrigin: true
}));

app.use('/api/orders', createProxyMiddleware({
  target: 'http://order-service:3003',
  pathRewrite: { '^/api/orders': '/api/orders' },
  changeOrigin: true
}));

app.listen(80);
```

---

## 🔍 Service Discovery & Health Checks

```javascript
// Health check endpoint (standard for orchestrators)
app.get('/health', async (req, res) => {
  const checks = {
    database: await checkDB(),
    redis: await checkRedis(),
    diskSpace: checkDisk()
  };
  
  const healthy = Object.values(checks).every(c => c.status === 'ok');
  
  res.status(healthy ? 200 : 503).json({
    status: healthy ? 'healthy' : 'unhealthy',
    version: process.env.APP_VERSION,
    uptime: process.uptime(),
    checks
  });
});

// Readiness vs Liveness (Kubernetes)
app.get('/health/live', (req, res) => res.status(200).send('OK')); // Process is running
app.get('/health/ready', async (req, res) => {
  // Can accept traffic (DB connected, warmed up)
  const ready = await isReady();
  res.status(ready ? 200 : 503).send(ready ? 'Ready' : 'Not Ready');
});
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What are microservices and when should you use them?**

Microservices are small, independently deployable services each handling one business capability. Use when: team is large (independent teams per service), different scaling needs, different tech stacks needed, need independent deployments. Don't use for: small teams, simple domains, MVPs. Start monolith, extract services when needed.

**Q2: How do microservices communicate with each other?**

Synchronous: REST (HTTP), gRPC (binary, fast, type-safe). Best for: request-response patterns, queries. Asynchronous: Message queues (RabbitMQ, Kafka), events. Best for: fire-and-forget, event-driven workflows, decoupling. Choose based on: consistency needs, latency tolerance, coupling preferences.

**Q3: What is an API Gateway?**

A single entry point for all client requests that routes to appropriate microservices. Responsibilities: request routing, authentication, rate limiting, load balancing, response aggregation, protocol translation. Examples: Kong, AWS API Gateway, Nginx, custom Express gateway. Prevents clients from knowing individual service addresses.

### Intermediate

**Q4: How do you handle distributed transactions across microservices?**

Patterns: (1) Saga pattern — sequence of local transactions with compensating actions on failure. (2) Outbox pattern — write event + data in same DB transaction, publish later. (3) Two-phase commit (rarely used — slow, locks). Avoid distributed transactions when possible. Design for eventual consistency. Example: Order saga — create order → reserve inventory → process payment → confirm (or compensate).

**Q5: What is the circuit breaker pattern and why is it important?**

Circuit breaker prevents cascading failures when a downstream service is down. States: CLOSED (normal), OPEN (reject immediately after N failures), HALF-OPEN (allow one test request after timeout). Benefits: fail fast, prevent resource exhaustion, allow recovery. Implementation: opossum library in Node.js. Configure: error threshold, timeout, reset interval.

**Q6: How do you handle data consistency between microservices?**

Each service owns its data (database per service). Consistency approaches: (1) Event-driven sync — publish events on changes, other services update their view. (2) CQRS — separate read/write models. (3) API composition — aggregate data from multiple services at read time. Accept eventual consistency for most operations.

### Advanced

**Q7: How would you implement distributed tracing across Node.js microservices?**

Use OpenTelemetry SDK: create spans at service boundaries, propagate context via HTTP headers (W3C traceparent). Each service: create child spans, add attributes (userId, orderId). Export to Jaeger/Zipkin. Use AsyncLocalStorage for in-process context propagation. Auto-instrument Express, database clients, HTTP clients with OTel plugins.

**Q8: Design a service mesh approach for Node.js microservices.**

Service mesh (Istio/Linkerd) handles cross-cutting concerns outside application code. Sidecar proxy per service handles: mTLS, retries, circuit breaking, observability. Node.js services just make plain HTTP calls. Benefits: polyglot support, consistent security, traffic management. Trade-offs: complexity, latency overhead, resource consumption.

**Q9: How do you handle versioning and backward compatibility in microservices?**

API versioning: URL path (/v1, /v2) or headers. Event versioning: schema registry, include version in events. Strategy: always backward-compatible changes (additive only), deprecation periods, consumer-driven contracts (Pact). Database: expand-and-contract migrations. Deploy new version → verify → remove old version. Never break existing consumers.

---

## 🛠️ Hands-on Exercise

Build a mini microservices system:
1. User Service (CRUD, auth)
2. Post Service (CRUD, references users)
3. Notification Service (event-driven)
4. API Gateway (routing, auth, rate limiting)
5. Event bus (Redis pub/sub or RabbitMQ)
6. Docker Compose for local development
