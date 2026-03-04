# Day 1: Microservices Principles

## What Are Microservices?

Microservices are an architectural style where an application is built as a collection of **small, independently deployable services**, each running in its own process, communicating via lightweight mechanisms (HTTP/REST, gRPC, messaging).

## Core Principles

### 1. Single Responsibility (Business Capability)
Each service owns ONE business capability end-to-end.

```
✅ User Service    → Registration, authentication, profile management
✅ Order Service   → Order creation, order lifecycle, order history
✅ Payment Service → Payment processing, refunds, billing

❌ "Backend Service" → Does everything
```

### 2. Independently Deployable
Each service can be built, tested, and deployed without affecting others.

```
Deploy Order Service v2.1 → User Service stays at v3.0
No coordinated releases → Faster iteration
```

### 3. Decentralized Data Management
Each service owns its data. No shared databases.

```
User Service  → users_db (PostgreSQL)
Order Service → orders_db (PostgreSQL)
Search Service → search_index (Elasticsearch)
Cache Service → cache (Redis)

❌ Shared database → tight coupling, schema changes break everything
```

### 4. Smart Endpoints, Dumb Pipes
Business logic lives in services (smart endpoints). Communication infrastructure is simple (dumb pipes — HTTP, message queues).

```
✅ Services contain business logic
✅ HTTP REST / gRPC for sync communication
✅ Kafka / RabbitMQ for async communication

❌ ESB (Enterprise Service Bus) with routing logic in the bus
```

### 5. Design for Failure
Assume any service can fail at any time.

```
✅ Circuit breakers (stop cascading failures)
✅ Retry with exponential backoff
✅ Bulkheads (isolate failure impact)
✅ Timeouts on all external calls
✅ Graceful degradation (show cached data when service down)
```

### 6. Infrastructure Automation
Automate everything — build, test, deploy, monitor.

```
✅ CI/CD pipelines per service
✅ Containerization (Docker)
✅ Orchestration (Kubernetes)
✅ Infrastructure as Code (Terraform)
✅ Automated testing at all levels
```

## Monolith vs Microservices

```
Monolith:
┌────────────────────────────┐
│     Single Application      │
│  ┌──────┐ ┌──────┐ ┌────┐ │
│  │Users │ │Orders│ │Pay │ │
│  └──────┘ └──────┘ └────┘ │
│        Shared Database      │
└────────────────────────────┘

Microservices:
┌──────┐   ┌──────┐   ┌────┐
│Users │   │Orders│   │Pay │
│Svc   │   │Svc   │   │Svc │
└──┬───┘   └──┬───┘   └─┬──┘
   │          │          │
 users_db   orders_db  pay_db
```

| Aspect | Monolith | Microservices |
|--------|----------|---------------|
| Deployment | All-or-nothing | Independent per service |
| Scaling | Vertical (scale up) | Horizontal (scale per service) |
| Tech Stack | Single | Polyglot (per service) |
| Data | Shared database | Database per service |
| Complexity | In-process calls | Network calls + distributed systems |
| Testing | Simple (all in process) | Complex (integration, contracts) |
| Team Size | Works for small teams | Scales with large teams |
| Latency | In-process (fast) | Network hops (slower) |
| Debugging | Stack trace | Distributed tracing |
| Transactions | ACID (simple) | Saga (complex) |

### When NOT to Use Microservices

```
❌ Small team (< 8-10 developers)
❌ New/uncertain domain (don't know the boundaries yet)
❌ Simple CRUD application
❌ Premature optimization ("we might need to scale")
❌ No DevOps culture/infrastructure
```

## Service Decomposition Strategies

### By Business Capability

```
E-commerce:
├── Product Catalog Service (browse, search)
├── Shopping Cart Service (add, remove, checkout)
├── Order Service (create, track, history)
├── Payment Service (charge, refund)
├── Shipping Service (estimate, track)
├── User Service (auth, profile)
└── Notification Service (email, SMS, push)
```

### By Subdomain (DDD Bounded Contexts)

```
Domain: E-commerce
├── Core Domain: Order Management (competitive advantage)
├── Supporting: Inventory Management (important but not differentiating)
├── Supporting: Shipping Integration (necessary infrastructure)
└── Generic: User Authentication (commodity, use existing solution)
```

### By Data Ownership

```
Who owns the data? → That's the service boundary.

User data → User Service
Order data → Order Service
Product data → Product Service

❌ Order Service reading user table directly
✅ Order Service calls User Service API
```

## Communication Patterns

### Synchronous (Request-Response)

```
REST / gRPC:
Order Service → HTTP GET /users/123 → User Service → { name: "Bharath" }

When to use:
✅ Need immediate response
✅ Simple CRUD operations
✅ Query data from another service
```

### Asynchronous (Event-Driven)

```
Event Bus (Kafka/RabbitMQ):
Order Service → publishes "OrderCreated" event
   ├── Payment Service subscribes → charges payment
   ├── Inventory Service subscribes → reserves stock
   └── Notification Service subscribes → sends email

When to use:
✅ Fire-and-forget operations
✅ Loose coupling between services
✅ Long-running workflows
✅ Event sourcing patterns
```

## Service Communication Comparison

| Pattern | Protocol | Coupling | Speed | Use Case |
|---------|----------|----------|-------|----------|
| REST | HTTP/JSON | Low | Medium | CRUD, public APIs |
| gRPC | HTTP/2+Protobuf | Medium | Fast | Internal service-to-service |
| Message Queue | AMQP/Kafka | Very Low | Async | Events, workflows |
| GraphQL | HTTP/JSON | Low | Medium | BFF, aggregation |

## The Fallacies of Distributed Computing

Every microservices developer must understand these:

```
1. The network is reliable           → Implement retries, circuit breakers
2. Latency is zero                   → Add timeouts, async where possible
3. Bandwidth is infinite             → Minimize payload sizes
4. The network is secure             → mTLS, auth on every call
5. Topology doesn't change           → Service discovery
6. There is one administrator        → Decentralized ownership
7. Transport cost is zero            → Batch requests, cache
8. The network is homogeneous        → Protocol negotiation
```

## Key Takeaways

1. **Microservices = organizational pattern** — align services with teams (Conway's Law)
2. **Start with a monolith**, decompose when you understand domain boundaries
3. **Database per service** is non-negotiable — shared DB = distributed monolith
4. **Design for failure** — circuit breakers, retries, timeouts everywhere
5. **Async communication** reduces coupling — prefer events over synchronous calls
6. **Don't adopt microservices for small teams** — the complexity tax isn't worth it
