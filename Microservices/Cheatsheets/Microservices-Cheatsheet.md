# Microservices Cheatsheet — Quick Reference

## Core Principles
```
1. Single Responsibility (business capability per service)
2. Independently Deployable
3. Decentralized Data (database per service)
4. Smart Endpoints, Dumb Pipes
5. Design for Failure
6. Infrastructure Automation
```

## Communication Patterns
```
Synchronous:
  REST     → CRUD, public APIs, simple queries
  gRPC     → Internal service-to-service, streaming, low latency

Asynchronous:
  Events   → Loose coupling, fire-and-forget (Kafka, RabbitMQ)
  Commands → Directed, one recipient (message queue)
```

## Data Patterns
```
Database per Service   → Each service owns its data store
Saga                   → Distributed transactions (compensate on failure)
  Choreography         → Event-driven, no coordinator
  Orchestration        → Central coordinator directs steps
Event Sourcing         → Store events, derive state
CQRS                   → Separate read/write models
API Composition        → Aggregate data from multiple services
```

## Resilience Patterns
```
Circuit Breaker:  CLOSED → OPEN → HALF-OPEN → CLOSED
  Closed:    Normal; track failures
  Open:      Fail fast; don't call downstream
  Half-Open: Test recovery with limited requests

Retry:  Exponential backoff with jitter
  delay = min(base * 2^attempt + random_jitter, max_delay)

Bulkhead:  Isolate resources per dependency
  Separate thread/connection pools

Timeout:  Set on ALL external calls
  Rule: timeout < circuit breaker threshold
```

## Resilience Stack Order
```
Request → Bulkhead → Circuit Breaker → Retry → Timeout → Call
```

## Observability (Three Pillars)
```
Logs:    Structured JSON; centralize (ELK/Loki); correlate by trace ID
Metrics: RED (Rate, Errors, Duration); USE (Utilization, Saturation, Errors)
Traces:  Distributed tracing (OpenTelemetry, Jaeger); trace ID propagation
```

## Service Decomposition
```
By Business Capability:  User, Order, Payment, Shipping
By DDD Bounded Context:  Core domain, Supporting, Generic
By Data Ownership:       Who owns the data → that's the service
```

## Context Mapping
```
Shared Kernel:      Two contexts share a model (tight coupling)
Customer-Supplier:  Upstream provides, downstream consumes
Anti-Corruption Layer: Translator to protect your model
Open Host Service:   Published API for integration
Published Language:  Shared event schema (Protobuf, Avro)
```

## Deployment Strategies
```
Blue-Green:    Two identical envs; switch traffic instantly
Canary:        Route 5% → 25% → 100% gradually
Rolling:       Replace instances one by one
Feature Flags: Toggle features without deployment
```

## Migration Pattern — Strangler Fig
```
1. Add proxy/gateway in front of monolith
2. Build new service for ONE feature
3. Route that feature to new service
4. Repeat for each feature
5. Decommission empty monolith
```

## Service Mesh (Istio/Linkerd)
```
Sidecar proxy per service handles:
  ☐ mTLS (encryption)
  ☐ Load balancing
  ☐ Circuit breaking
  ☐ Retry/timeout
  ☐ Observability (metrics, tracing)
  ☐ Traffic routing (canary, A/B)
```

## Anti-Patterns
```
❌ Distributed Monolith    → Shared DB, coordinated deploys
❌ Nano-services           → Too many tiny services
❌ Sync Call Chains        → A→B→C→D (latency compounds)
❌ Shared Business Libs    → Coupling via shared code
❌ God Service             → One service does everything
❌ No API Versioning       → Breaking changes cascade
```

## Key Numbers
```
Service count sweet spot: 5-15 for mid-sized teams
Max sync call chain:      2-3 hops
Circuit breaker timeout:  30s typical
Retry max:                3-5 attempts
Health check interval:    10-30s
Saga steps:               <7 (more = too complex)
```

## Technology Stack Matrix
```
API Gateway:   Kong, AWS API GW, Nginx, Traefik
Service Mesh:  Istio, Linkerd, Consul Connect
Message Bus:   Kafka (event streaming), RabbitMQ (task queue)
Tracing:       OpenTelemetry, Jaeger, Zipkin
Metrics:       Prometheus + Grafana
Logging:       ELK Stack, Loki + Grafana
Containers:    Docker + Kubernetes
CI/CD:         GitHub Actions, ArgoCD, Jenkins
```
