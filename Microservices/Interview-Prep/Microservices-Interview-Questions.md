# Microservices Interview Questions — Senior / Staff Level

## Section 1: Fundamentals

### Q1: When should you NOT use microservices?
**Answer**: (1) Small team (<8-10 devs) — organizational overhead exceeds benefit, (2) New/uncertain domain — you don't know boundaries yet (start with monolith), (3) Simple CRUD app — microservices add unnecessary complexity, (4) No DevOps culture — you need CI/CD, containers, monitoring infrastructure, (5) Premature optimization — "we might scale" is not a reason.

### Q2: What is Conway's Law and how does it relate to microservices?
**Answer**: "Organizations design systems that mirror their communication structures." Microservices align with this — each service should be owned by one team. If 4 teams work on one monolith, you'll get 4-component architecture anyway. **Inverse Conway Maneuver**: Design your org structure to produce the architecture you want.

### Q3: What is a distributed monolith?
**Answer**: A system that has the complexity of microservices with none of the benefits. Signs: shared database, coordinated deployments required, synchronous call chains, shared business logic libraries. Fix: Enforce database-per-service, use async communication, define clear API contracts.

## Section 2: Communication

### Q4: When do you choose synchronous vs asynchronous communication?
**Answer**:
- **Synchronous (REST/gRPC)**: Need immediate response, query operations, simple CRUD. Trade-off: temporal coupling (both services must be up).
- **Asynchronous (Events/Messages)**: Fire-and-forget, long-running workflows, loose coupling, event sourcing. Trade-off: eventual consistency, harder debugging.
- **Rule of thumb**: Commands that need a response → sync. Events/notifications → async.

### Q5: Explain the difference between commands, events, and queries in microservices.
**Answer**:
- **Commands**: Imperative, one recipient. "CreateOrder", "ProcessPayment". Can fail.
- **Events**: Past tense, multiple subscribers. "OrderCreated", "PaymentProcessed". Facts that happened.
- **Queries**: Read-only, one recipient. "GetUser", "ListOrders". No side effects.
CQRS separates command and query models for optimization.

## Section 3: Data Management

### Q6: Explain database-per-service pattern. What challenges does it create?
**Answer**: Each service owns its database — no direct DB access across services.

**Challenges**:
1. **Joins across services**: Must do API calls or event-driven denormalization
2. **Distributed transactions**: Use Saga pattern instead of 2PC
3. **Data consistency**: Eventually consistent, not ACID across services
4. **Querying across services**: CQRS — build read-optimized views from events
5. **Data duplication**: Acceptable trade-off for service independence

### Q7: Explain the Saga pattern. Choreography vs Orchestration.
**Answer**: Saga = sequence of local transactions with compensating actions for rollback.

- **Choreography**: Each service publishes events, other services react. Pros: loose coupling. Cons: hard to track overall flow, debug complex chains.
- **Orchestration**: Central coordinator directs steps. Pros: clear flow visibility, easier debugging. Cons: coordinator can be bottleneck.
- **Use choreography** for simple 2-3 step sagas. **Use orchestration** for complex 4+ step workflows.

### Q8: What is Event Sourcing and when would you use it?
**Answer**: Instead of storing current state, store all **events** that led to the current state. The current state is derived by replaying events.

```
Event Store: [OrderCreated, ItemAdded, ItemAdded, PaymentCharged, OrderShipped]
Current State: Order { items: 2, status: 'shipped', paid: true }
```

**Use when**: Audit trail required (finance, healthcare), time-travel debugging, event-driven architecture. **Don't use**: Simple CRUD, when eventual consistency is unacceptable, team lacks experience.

## Section 4: Resilience

### Q9: Explain the Circuit Breaker pattern with all three states.
**Answer**:
- **Closed** (normal): Requests pass through. Track failures.
- **Open** (failing): Fail immediately without calling downstream. Triggered when failure count exceeds threshold.
- **Half-Open** (testing): After timeout, allow limited requests to test if downstream recovered. If successful → Close. If failed → Open again.

Prevents cascading failures. Always combine with fallback (cached data, default response, queue for retry).

### Q10: How do you prevent thundering herd when a circuit breaker closes?
**Answer**: (1) **Exponential backoff with jitter** — randomize retry delays, (2) **Rate-limited half-open** — only allow 1-3 test requests, not all accumulated traffic, (3) **Health check endpoint** — poll health instead of sending real traffic, (4) **Gradual ramp-up** — route 10% → 25% → 50% → 100% of traffic.

### Q11: Explain the Bulkhead pattern.
**Answer**: Isolate resources per dependency so one failing service can't exhaust all resources. Like bulkheads in a ship — a leak in one compartment doesn't sink the whole ship. Implementation: separate thread pools, connection pools, or semaphores per downstream service. Combined with circuit breaker: Bulkhead → Circuit Breaker → Retry → Call.

## Section 5: Observability

### Q12: What are the three pillars of observability?
**Answer**:
1. **Logs**: Structured events from each service. Centralize with ELK/Loki. Correlate with trace IDs.
2. **Metrics**: Aggregated numerical data. RED method: Rate, Errors, Duration. USE method: Utilization, Saturation, Errors. Tools: Prometheus + Grafana.
3. **Traces**: End-to-end request flow across services. Distributed tracing with OpenTelemetry, Jaeger, Zipkin. Shows latency per service in the chain.

### Q13: How do you implement distributed tracing?
**Answer**: (1) Generate unique trace ID at the entry point (API gateway), (2) Propagate trace ID in headers (e.g., `X-Trace-Id`, W3C TraceContext) across all service calls, (3) Each service creates spans with timing data, (4) Spans are collected by tracing backend (Jaeger/Zipkin), (5) Visualize as waterfall diagram showing latency per service. Use OpenTelemetry SDK for auto-instrumentation.

## Section 6: Architecture

### Q14: Explain the Strangler Fig pattern for migration.
**Answer**: Incrementally replace a monolith by routing requests to new microservices one by one.

Steps: (1) Put a proxy/API gateway in front of the monolith, (2) Build new service for ONE feature, (3) Route that feature's traffic to new service, (4) Old code still handles everything else, (5) Repeat for next feature, (6) Eventually monolith is empty → decommission.

Key: Both systems run in parallel. No big-bang migration. Rollback is easy (route back to monolith).

### Q15: Design a microservices architecture for an e-commerce platform.

```
Services:
├── API Gateway (routing, auth, rate limiting)
├── User Service (auth, profiles, preferences)
├── Product Service (catalog, search, reviews)
├── Cart Service (add/remove, pricing)
├── Order Service (creation, lifecycle, history)
├── Payment Service (processing, refunds)
├── Inventory Service (stock, reservations)
├── Shipping Service (rates, tracking)
├── Notification Service (email, SMS, push)
└── Search Service (Elasticsearch, recommendations)

Communication:
- Sync: API Gateway → Services (REST/gRPC)
- Async: Kafka for events (OrderCreated, PaymentProcessed)
- Saga: Order → Inventory → Payment (orchestrated)

Data:
- PostgreSQL: User, Order, Payment (ACID required)
- MongoDB: Product catalog (flexible schema)
- Redis: Cart, sessions, caching
- Elasticsearch: Product search
- Kafka: Event bus
```

### Q16: What are microservices anti-patterns?
**Answer**:
1. **Distributed monolith**: Shared DB, coordinated deploys
2. **Nano-services**: Too many tiny services → operational overhead exceeds benefit
3. **God service**: One service does too much → "Account Service" that handles auth, billing, and profiles
4. **Sync chain**: A → B → C → D → E synchronously (latency adds up, any failure breaks chain)
5. **Shared libraries with business logic**: Changes require redeploying all services
6. **No API versioning**: Breaking changes cascade
7. **Per-service everything**: Separate DB, cache, queue cluster per service when not needed

## Rapid-Fire Summary

| Concept | One-Liner |
|---------|-----------|
| Microservices | Independent services aligned with business capabilities |
| Conway's Law | System structure mirrors org structure |
| Database per service | Each service owns its data, no shared DB |
| Saga | Distributed transactions via compensating actions |
| Circuit breaker | Fail fast when downstream is unhealthy |
| Bulkhead | Isolate failure domains with resource limits |
| Service mesh | Infrastructure layer for service-to-service communication |
| Strangler Fig | Incrementally replace monolith feature by feature |
| DDD Bounded Context | Boundary where domain model is consistent |
| Event Sourcing | Store events, derive state by replay |
| CQRS | Separate read and write models |
| Distributed tracing | Track requests across services with trace IDs |
