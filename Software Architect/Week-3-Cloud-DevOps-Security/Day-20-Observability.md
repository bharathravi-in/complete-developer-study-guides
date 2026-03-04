# Day 20: Observability

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. The Three Pillars of Observability
- [ ] Understand logs, metrics, traces
- [ ] Know how they complement each other

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Three Pillars of Observability                                          │
│                                                                         │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐           │
│  │    LOGS       │    │   METRICS     │    │   TRACES      │           │
│  │               │    │               │    │               │           │
│  │  What         │    │  How          │    │  Where        │           │
│  │  happened?    │    │  is it        │    │  did it       │           │
│  │               │    │  performing?  │    │  go?          │           │
│  └───────┬───────┘    └───────┬───────┘    └───────┬───────┘           │
│          │                    │                    │                    │
│          ▼                    ▼                    ▼                    │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐           │
│  │ Discrete      │    │ Aggregated    │    │ Correlated    │           │
│  │ events        │    │ measurements  │    │ request flow  │           │
│  │               │    │ over time     │    │               │           │
│  └───────────────┘    └───────────────┘    └───────────────┘           │
│                                                                         │
│  Example Investigation:                                                │
│  1. Alert: High latency (METRICS)                                     │
│  2. Trace: Slow database call (TRACES)                                │
│  3. Logs: Query details (LOGS)                                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Logging
- [ ] Understand structured logging
- [ ] Know log aggregation

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Centralized Logging Architecture                                        │
│                                                                         │
│   Services                    Collection              Storage & Analysis│
│  ┌──────────┐                                                          │
│  │Service A │─┐                                                        │
│  │  [logs]  │ │           ┌─────────────┐         ┌─────────────────┐ │
│  └──────────┘ │           │             │         │                 │ │
│               ├──────────►│  Fluentd /  │────────►│  Elasticsearch  │ │
│  ┌──────────┐ │           │  Fluent Bit │         │       or        │ │
│  │Service B │─┤           │     or      │         │     Loki        │ │
│  │  [logs]  │ │           │  Logstash   │         │                 │ │
│  └──────────┘ │           │             │         └────────┬────────┘ │
│               │           └─────────────┘                  │          │
│  ┌──────────┐ │                                           │          │
│  │Service C │─┘                                           ▼          │
│  │  [logs]  │                                     ┌───────────────┐  │
│  └──────────┘                                     │   Kibana /    │  │
│                                                   │   Grafana     │  │
│                                                   │  (Dashboard)  │  │
│                                                   └───────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Structured Logging:**

```typescript
// ❌ Bad: Unstructured logs
console.log('User 123 placed order 456 for $99.99');

// ✅ Good: Structured JSON logs
logger.info('Order placed', {
  userId: '123',
  orderId: '456',
  amount: 99.99,
  currency: 'USD',
  timestamp: new Date().toISOString(),
  traceId: context.traceId,
  spanId: context.spanId
});

// Output:
{
  "level": "info",
  "message": "Order placed",
  "userId": "123",
  "orderId": "456",
  "amount": 99.99,
  "currency": "USD",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "traceId": "abc123",
  "spanId": "def456"
}
```

**Log Levels:**

| Level | When to Use |
|-------|-------------|
| **ERROR** | Exceptions, failures requiring attention |
| **WARN** | Potential issues, degraded functionality |
| **INFO** | Business events, state changes |
| **DEBUG** | Development diagnostics |
| **TRACE** | Detailed execution flow |

---

### 3. Metrics (Prometheus)
- [ ] Understand metric types
- [ ] Know PromQL basics

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Prometheus Architecture                                                 │
│                                                                         │
│   Targets (Scrape)           Prometheus              Visualization     │
│  ┌──────────────┐           ┌───────────────┐       ┌───────────────┐  │
│  │  Service A   │◄──────────│               │──────►│               │  │
│  │  /metrics    │   pull    │  Prometheus   │       │   Grafana     │  │
│  └──────────────┘           │    Server     │       │               │  │
│                             │               │       └───────────────┘  │
│  ┌──────────────┐           │  ┌─────────┐  │                         │
│  │  Service B   │◄──────────│  │  TSDB   │  │       ┌───────────────┐  │
│  │  /metrics    │   pull    │  │ Storage │  │──────►│  Alertmanager │  │
│  └──────────────┘           │  └─────────┘  │       │               │  │
│                             │               │       └───────────────┘  │
│  ┌──────────────┐           └───────────────┘              │          │
│  │  Node Exp.   │                                          ▼          │
│  │  /metrics    │◄─────────────────────────        ┌───────────────┐  │
│  └──────────────┘                                  │  PagerDuty    │  │
│                                                    │  Slack        │  │
│                                                    └───────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

**Metric Types:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Prometheus Metric Types                                                 │
│                                                                         │
│  1. Counter (only increases)                                           │
│     ─────────────────────                                              │
│     http_requests_total{method="GET", status="200"}                    │
│                                                                         │
│     ▲                                                                  │
│     │            ╱                                                     │
│     │          ╱                                                       │
│     │        ╱                                                         │
│     │      ╱                                                           │
│     │    ╱                                                             │
│     └───────────────────────► time                                     │
│                                                                         │
│  2. Gauge (goes up and down)                                           │
│     ────────────────────────                                           │
│     cpu_usage_percent                                                  │
│                                                                         │
│     ▲                                                                  │
│     │    ╱╲      ╱╲                                                    │
│     │   ╱  ╲    ╱  ╲   ╱                                               │
│     │  ╱    ╲  ╱    ╲ ╱                                                │
│     │ ╱      ╲╱      ╲                                                 │
│     └───────────────────────► time                                     │
│                                                                         │
│  3. Histogram (distribution)                                           │
│     ──────────────────────                                             │
│     http_request_duration_seconds_bucket{le="0.1"}                     │
│     http_request_duration_seconds_bucket{le="0.5"}                     │
│     http_request_duration_seconds_bucket{le="1.0"}                     │
│                                                                         │
│  4. Summary (percentiles)                                              │
│     ─────────────────────                                              │
│     http_request_duration_seconds{quantile="0.5"}                      │
│     http_request_duration_seconds{quantile="0.99"}                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**PromQL Examples:**

```promql
# Request rate (requests/second)
rate(http_requests_total[5m])

# Error rate percentage
sum(rate(http_requests_total{status=~"5.."}[5m])) 
/ sum(rate(http_requests_total[5m])) * 100

# 95th percentile latency
histogram_quantile(0.95, 
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le))

# Top 5 endpoints by traffic
topk(5, sum(rate(http_requests_total[5m])) by (endpoint))
```

---

### 4. Distributed Tracing
- [ ] Understand trace context
- [ ] Know tracing tools

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Distributed Trace                                                       │
│                                                                         │
│  Trace ID: abc123 (entire request journey)                             │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                                                                  │  │
│  │  API Gateway [Span A: 120ms]                                    │  │
│  │  ═══════════════════════════════════════════                    │  │
│  │      │                                                          │  │
│  │      ├──► User Service [Span B: 45ms]                          │  │
│  │      │    ════════════════                                      │  │
│  │      │        │                                                 │  │
│  │      │        └──► Auth DB [Span C: 15ms]                      │  │
│  │      │             ══════                                       │  │
│  │      │                                                          │  │
│  │      └──► Order Service [Span D: 60ms]                         │  │
│  │           ═══════════════════════                               │  │
│  │               │                                                 │  │
│  │               ├──► Inventory DB [Span E: 25ms]                 │  │
│  │               │    ═════════                                    │  │
│  │               │                                                 │  │
│  │               └──► Payment Service [Span F: 30ms]              │  │
│  │                    ═══════════                                  │  │
│  │                        │                                        │  │
│  │                        └──► Payment Gateway [Span G: 20ms]     │  │
│  │                             ══════                              │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  Trace Context Propagation:                                            │
│  Header: traceparent: 00-abc123-spanid-01                             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Tracing with OpenTelemetry:**

```typescript
import { trace, context } from '@opentelemetry/api';

const tracer = trace.getTracer('order-service');

async function processOrder(orderId: string) {
  return tracer.startActiveSpan('processOrder', async (span) => {
    try {
      span.setAttribute('order.id', orderId);
      
      // Child span for database
      const order = await tracer.startActiveSpan('fetchOrder', async (childSpan) => {
        const result = await db.orders.findById(orderId);
        childSpan.setAttribute('db.statement', 'SELECT * FROM orders WHERE id = ?');
        childSpan.end();
        return result;
      });
      
      // Child span for payment
      await tracer.startActiveSpan('processPayment', async (childSpan) => {
        await paymentService.charge(order);
        childSpan.end();
      });
      
      span.setStatus({ code: SpanStatusCode.OK });
    } catch (error) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
      span.recordException(error);
      throw error;
    } finally {
      span.end();
    }
  });
}
```

---

### 5. Grafana Dashboards
- [ ] Design effective dashboards
- [ ] Know visualization best practices

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Service Dashboard Layout                                                │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Request Rate          Error Rate          P95 Latency           │  │
│  │  ┌──────────┐         ┌──────────┐         ┌──────────┐         │  │
│  │  │   1.2K   │         │   0.1%   │         │  120ms   │         │  │
│  │  │ req/sec  │         │          │         │          │         │  │
│  │  └──────────┘         └──────────┘         └──────────┘         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  HTTP Request Rate by Status                                     │  │
│  │  ▲                                                               │  │
│  │  │ ████████████████████████████████████████ 200                 │  │
│  │  │ ████ 500                                                     │  │
│  │  │ ██ 404                                                       │  │
│  │  └─────────────────────────────────────────────────► time       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Latency Distribution                                            │  │
│  │  ▲                                                               │  │
│  │  │      ╱╲                                                       │  │
│  │  │     ╱  ╲     p50: 50ms                                       │  │
│  │  │    ╱    ╲    p95: 120ms                                      │  │
│  │  │   ╱      ╲   p99: 250ms                                      │  │
│  │  │  ╱        ╲                                                   │  │
│  │  └─────────────────────────────────────────────────► latency    │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📘 Alerting Best Practices

### Alert on Symptoms, Not Causes

```yaml
# Good: Alert on user-facing symptoms
- alert: HighErrorRate
  expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.01
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "High error rate ({{ $value | humanizePercentage }})"
    description: "More than 1% of requests are failing"

# Avoid: Alerting on causes (CPU, memory) unless critical
```

### SLO-Based Alerting

```
┌─────────────────────────────────────────────────────────────────────────┐
│  SLI/SLO/SLA/Error Budget                                                │
│                                                                         │
│  SLI (Service Level Indicator):                                        │
│  └─► Measurement: "99.5% of requests complete in < 200ms"             │
│                                                                         │
│  SLO (Service Level Objective):                                        │
│  └─► Target: "99.9% availability over 30 days"                        │
│                                                                         │
│  SLA (Service Level Agreement):                                        │
│  └─► Contract: "Refund credits if below 99.5%"                        │
│                                                                         │
│  Error Budget:                                                         │
│  └─► Allowance: 0.1% of requests can fail (43.2 min/month)           │
│                                                                         │
│  Error Budget Remaining: ██████████░░░░ 70%                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Practice Task

### Set Up Observability Stack

**Instructions:**
1. Deploy Prometheus + Grafana
2. Add metrics to a sample app
3. Create dashboard with RED metrics
4. Set up alerting

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] [Prometheus Documentation](https://prometheus.io/docs/)
- [ ] [Grafana Documentation](https://grafana.com/docs/)
- [ ] [OpenTelemetry](https://opentelemetry.io/)
- [ ] Google SRE Book - Monitoring Chapter

---

## ✅ Completion Checklist

- [ ] Understand logs, metrics, traces
- [ ] Can set up structured logging
- [ ] Know Prometheus and PromQL
- [ ] Understand distributed tracing
- [ ] Can create Grafana dashboards

**Date Completed:** _____________
