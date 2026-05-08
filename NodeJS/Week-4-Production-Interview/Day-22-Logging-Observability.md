# Day 22: Logging, Error Tracking & Observability

## 🎯 Learning Objectives
- Implement structured logging with Winston/Pino
- Set up error tracking (Sentry)
- Understand the three pillars of observability
- Build dashboards and alerting

---

## 📚 Structured Logging

### Pino (Fastest Node.js Logger)

```javascript
const pino = require('pino');

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'development' 
    ? { target: 'pino-pretty', options: { colorize: true } }
    : undefined,
  base: { service: 'user-api', version: process.env.APP_VERSION },
  redact: ['req.headers.authorization', 'password', 'req.body.password'],
  serializers: {
    req: pino.stdSerializers.req,
    res: pino.stdSerializers.res,
    err: pino.stdSerializers.err,
  }
});

// Usage
logger.info({ userId: '123', action: 'login' }, 'User logged in');
logger.warn({ queueDepth: 1500, threshold: 1000 }, 'Queue depth exceeds threshold');
logger.error({ err, orderId: '456' }, 'Payment processing failed');

// Express middleware
const expressPino = require('pino-http');
app.use(expressPino({ logger, autoLogging: { ignore: (req) => req.url === '/health' } }));
```

### Log Levels & Best Practices

```javascript
// Log levels: fatal > error > warn > info > debug > trace
logger.fatal('Unrecoverable error, process shutting down');
logger.error({ err }, 'Operation failed, will retry');
logger.warn('Approaching rate limit');
logger.info({ duration: 150 }, 'Request completed');
logger.debug({ query, params }, 'Database query executed');
logger.trace({ body: req.body }, 'Raw request body');

// ✅ Good logging practices
logger.info({ orderId, userId, amount }, 'Order placed');

// ❌ Bad practices
console.log('User logged in');                    // No structure
logger.info(`User ${userId} did ${action}`);      // String interpolation (not searchable)
logger.info({ password: user.password });         // Logging secrets!
logger.info({ data: entireDatabaseResult });      // Too much data
```

### Correlation & Request Context

```javascript
const { AsyncLocalStorage } = require('async_hooks');
const context = new AsyncLocalStorage();

// Middleware: create request context
app.use((req, res, next) => {
  const requestId = req.headers['x-request-id'] || uuid();
  const childLogger = logger.child({ requestId, userId: req.user?.id });
  
  context.run({ logger: childLogger, requestId }, next);
});

// Access logger anywhere
function getLogger() {
  return context.getStore()?.logger || logger;
}

// In services (no need to pass logger around)
class OrderService {
  async createOrder(data) {
    const log = getLogger();
    log.info({ data }, 'Creating order');
    // ...
    log.info({ orderId: order.id }, 'Order created');
  }
}
```

---

## 🐛 Error Tracking (Sentry)

```javascript
const Sentry = require('@sentry/node');

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  release: process.env.APP_VERSION,
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,
  integrations: [
    new Sentry.Integrations.Http({ tracing: true }),
    new Sentry.Integrations.Express({ app }),
  ],
});

// Request handler (must be first middleware)
app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.tracingHandler());

// Routes...

// Error handler (must be before your error handler)
app.use(Sentry.Handlers.errorHandler());

// Manual error reporting
try {
  await processPayment(order);
} catch (err) {
  Sentry.captureException(err, {
    extra: { orderId: order.id, amount: order.total },
    user: { id: req.user.id, email: req.user.email },
    tags: { service: 'payment', severity: 'critical' }
  });
  throw err;
}
```

---

## 📈 Three Pillars of Observability

```
1. LOGS    → What happened (structured events)
2. METRICS → How the system is performing (numbers over time)  
3. TRACES  → How a request flows through services
```

### Metrics (Prometheus)

```javascript
const promClient = require('prom-client');

// Default metrics (CPU, memory, event loop)
promClient.collectDefaultMetrics({ prefix: 'node_' });

// Custom metrics
const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 5]
});

const activeConnections = new promClient.Gauge({
  name: 'http_active_connections',
  help: 'Number of active HTTP connections'
});

// Middleware
app.use((req, res, next) => {
  activeConnections.inc();
  const end = httpRequestDuration.startTimer();
  
  res.on('finish', () => {
    activeConnections.dec();
    end({ method: req.method, route: req.route?.path || req.path, status_code: res.statusCode });
  });
  next();
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', promClient.register.contentType);
  res.send(await promClient.register.metrics());
});
```

---

## 🧪 Interview Questions

### Beginner
**Q1: Why use structured logging instead of console.log?**
Structured logs (JSON) are machine-parseable, searchable, and can be aggregated. They include context (requestId, userId), enable log levels, support redaction of sensitive data, and work with log management tools (ELK, Datadog). `console.log` produces unstructured text that's hard to query at scale.

**Q2: What are the three pillars of observability?**
Logs (discrete events), Metrics (aggregated measurements over time), Traces (request flow across services). Together they provide complete visibility: metrics alert you to problems, logs explain what happened, traces show where in the system it occurred.

**Q3: What is a correlation/request ID?**
A unique identifier attached to a request at the entry point and propagated through all services. Enables tracing a single request across logs from multiple services. Generated at API gateway/first service, passed via HTTP headers (X-Request-ID, X-Correlation-ID). Essential for debugging in distributed systems.

### Intermediate
**Q4: How do you prevent sensitive data from appearing in logs?**
(1) Redaction rules (Pino/Winston can mask specified paths). (2) Never log full request bodies (whitelist fields). (3) Strip auth headers. (4) Mask PII (email → a***@example.com). (5) Different log levels per environment (debug only in dev). (6) Audit log access controls. (7) Log rotation and retention policies.

**Q5: How do you set up effective alerting without alert fatigue?**
Define SLOs (Service Level Objectives). Alert on: error rate > threshold, p99 latency > X, queue depth growing, disk/memory approaching limits. Use severity levels (critical → page, warning → ticket). Group related alerts. Include runbook links. Regularly review and tune thresholds. Use anomaly detection for dynamic thresholds.

**Q6: Compare Winston, Pino, and Bunyan for Node.js logging.**
Pino: fastest (5x Winston), JSON-first, minimal overhead in production. Winston: most popular, transport system (file, console, HTTP), more features. Bunyan: JSON-native, child loggers, streams. Recommendation: Pino for performance-critical APIs, Winston for feature-rich needs. All support structured logging.

### Advanced
**Q7: Design a logging and monitoring strategy for a microservices system.**
Architecture: Each service → Pino JSON logs → Fluentd/Vector (collection) → Elasticsearch (storage) → Kibana (visualization). Metrics: Prometheus scraping /metrics → Grafana dashboards. Traces: OpenTelemetry → Jaeger. Correlation IDs propagated via headers. Centralized alerting with PagerDuty/OpsGenie. Log retention policies by severity.

**Q8: How would you implement distributed tracing with OpenTelemetry in Node.js?**
Install `@opentelemetry/sdk-node`, configure auto-instrumentation (HTTP, Express, DB clients). Create custom spans for business logic. Propagate context via W3C traceparent header. Export to Jaeger/Zipkin/OTLP endpoint. Each span has: traceId, spanId, parentSpanId, attributes. Use AsyncLocalStorage internally.

**Q9: How do you handle log volume at scale (millions of requests/day)?**
Sampling: log 100% of errors, 10% of success. Buffered writes (don't flush per log). Async transports (don't block event loop). Log levels: INFO in prod, DEBUG only when debugging. Structured logs compress well. Retention policies: 7 days hot, 30 days warm, archive cold. Cost optimization: aggregate metrics from logs, drop verbose logs.

---

## 🛠️ Hands-on Exercise
Build an observability stack:
1. Pino structured logging with request context
2. Prometheus metrics (custom + default)
3. Health check with dependency status
4. Error tracking with Sentry integration
5. Grafana dashboard (docker-compose setup)
