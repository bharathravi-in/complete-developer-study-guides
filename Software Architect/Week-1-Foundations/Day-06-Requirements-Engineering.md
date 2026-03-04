# Day 6: Requirements Engineering

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. Functional vs Non-Functional Requirements
- [ ] Understand the difference
- [ ] Know how to capture each

#### Functional Requirements (FRs)
> What the system should DO

**Examples:**
- User can register with email and password
- System sends order confirmation email
- Admin can view sales reports

#### Non-Functional Requirements (NFRs)
> HOW the system should behave

**Categories:**

| Category | Examples |
|----------|----------|
| **Performance** | Response time < 200ms, 1000 req/sec |
| **Scalability** | Handle 10M users |
| **Availability** | 99.99% uptime |
| **Security** | GDPR compliance, encryption |
| **Reliability** | MTBF > 720 hours |
| **Maintainability** | Deploy in < 30 minutes |

---

### 2. CAP Theorem
- [ ] Understand CAP theorem deeply
- [ ] Know when to choose which

```
              Consistency (C)
                   △
                  /|\
                 / | \
                /  |  \
               /   |   \
              /    |    \
             /     |     \
            /      |      \
           /   CP  |  CA   \
          /________|________\
         /         |         \
        /_____AP___|__________\
       Availability (A)    Partition
                          Tolerance (P)
```

**Definitions:**
- **Consistency:** Every read receives the most recent write
- **Availability:** Every request receives a response
- **Partition Tolerance:** System continues despite network partitions

**In distributed systems, you can only guarantee 2 of 3:**

| Choice | Description | Use Case |
|--------|-------------|----------|
| **CP** | Consistency + Partition Tolerance | Banking, financial systems |
| **AP** | Availability + Partition Tolerance | Social media, DNS |
| **CA** | Consistency + Availability | Single node (not distributed) |

**Real-world Examples:**
- MongoDB: CP (when using majority write concern)
- Cassandra: AP (tunable)
- PostgreSQL (single node): CA
- DynamoDB: AP

---

### 3. Trade-off Analysis
- [ ] Learn how to analyze trade-offs
- [ ] Document decisions clearly

**Common Trade-offs:**

| Trade-off | Option A | Option B |
|-----------|----------|----------|
| Performance vs Readability | Optimized code | Clean code |
| Cost vs Quality | Buy vs Build | |
| Time vs Features | MVP | Full product |
| Consistency vs Availability | ACID | BASE |
| Coupling vs Simplicity | Microservices | Monolith |

**Analysis Framework:**

```markdown
## Trade-off Analysis: [Decision]

### Options Considered
1. Option A: [Description]
2. Option B: [Description]

### Evaluation Criteria
| Criteria | Weight | Option A Score | Option B Score |
|----------|--------|----------------|----------------|
| Cost | 20% | | |
| Performance | 30% | | |
| Maintainability | 25% | | |
| Time to market | 25% | | |

### Weighted Score
- Option A: [Total]
- Option B: [Total]

### Recommendation
[Choice with rationale]
```

---

### 4. Architecture Decision Record (ADR)
- [ ] Learn ADR format
- [ ] Practice writing ADRs

**ADR Template:**

```markdown
# ADR-[NUMBER]: [TITLE]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[What is the issue that we're seeing that is motivating this decision?]

## Decision
[What is the change that we're proposing?]

## Consequences

### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Drawback 1]
- [Drawback 2]

### Neutral
- [Neutral impact]

## Alternatives Considered
1. [Alternative 1]
   - Pros: [...]
   - Cons: [...]

2. [Alternative 2]
   - Pros: [...]
   - Cons: [...]

## References
- [Link to relevant docs]
```

---

## 🎯 Practice Task

### Write ADR: "Why We Choose Microservices Over Monolith"

```markdown
# ADR-001: Microservices Architecture for E-Commerce Platform

## Status
Accepted

## Context
Our e-commerce platform is growing rapidly with the following challenges:
- 50+ developers working on the same codebase
- Deployment frequency limited to once per week
- Single database becoming a bottleneck
- Different modules have different scaling needs (Catalog vs Checkout)
- Teams blocked waiting for other team's changes

Current monolith metrics:
- 500K lines of code
- 2-hour build time
- 40% of deployments cause rollbacks
- Database at 80% capacity during peak

## Decision
We will migrate to a microservices architecture over 18 months using the Strangler Fig pattern.

Initial services:
1. User Service
2. Product Catalog Service
3. Order Service
4. Payment Service
5. Notification Service

Technology decisions:
- Docker + Kubernetes for orchestration
- Kafka for async communication
- REST + gRPC for sync communication
- PostgreSQL per service (database per service)

## Consequences

### Positive
- Independent deployment (multiple deploys per day per service)
- Technology flexibility per service
- Horizontal scaling of specific services
- Reduced blast radius of failures
- Team autonomy and faster development

### Negative
- Increased operational complexity
- Need for distributed tracing and monitoring
- Data consistency challenges (eventual consistency)
- Higher initial infrastructure cost
- Learning curve for teams

### Neutral
- Requires investment in DevOps and Platform team
- Changes development practices (contracts, API versioning)

## Alternatives Considered

### 1. Modular Monolith
- Pros: Simpler operations, easier transactions
- Cons: Still coupled deployment, doesn't solve scaling issues

### 2. Service-Oriented Architecture (SOA) with ESB
- Pros: Mature pattern, centralized governance
- Cons: ESB becomes bottleneck, less flexibility

### 3. Serverless
- Pros: No infrastructure management, auto-scaling
- Cons: Vendor lock-in, cold starts, not suitable for all workloads

## References
- Building Microservices - Sam Newman
- Domain-Driven Design - Eric Evans
- [Netflix Microservices Case Study]
- [Amazon's Two-Pizza Team Paper]

## Decision Date
2024-01-15

## Decision Makers
- [CTO Name]
- [Principal Architect Name]
- [Engineering Managers]
```

---

## 📘 Requirements Documentation Templates

### System Requirements Document (SRD)

```markdown
# System Requirements Document

## 1. Introduction
### 1.1 Purpose
### 1.2 Scope
### 1.3 Definitions

## 2. Overall Description
### 2.1 Product Perspective
### 2.2 Product Functions
### 2.3 User Classes
### 2.4 Operating Environment
### 2.5 Constraints

## 3. Functional Requirements
### 3.1 [Feature 1]
### 3.2 [Feature 2]

## 4. Non-Functional Requirements
### 4.1 Performance
### 4.2 Security
### 4.3 Reliability
### 4.4 Availability

## 5. External Interface Requirements
### 5.1 User Interfaces
### 5.2 Hardware Interfaces
### 5.3 Software Interfaces

## 6. Appendices
```

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] [ADR GitHub Organization](https://adr.github.io/)
- [ ] [CAP Theorem Deep Dive](https://martin.kleppmann.com/2015/05/11/please-stop-calling-databases-cp-or-ap.html)
- [ ] Software Architecture: The Hard Parts

---

## ✅ Completion Checklist

- [ ] Understand FRs vs NFRs
- [ ] Master CAP theorem
- [ ] Know trade-off analysis techniques
- [ ] Written ADR for microservices decision
- [ ] Created practice ADRs

**Date Completed:** _____________
