# Day 5: Architectural Patterns

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. MVC / MVVM Patterns
- [ ] Understand MVC architecture
- [ ] Understand MVVM architecture
- [ ] Know when to use each

#### MVC (Model-View-Controller)

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│    ┌──────────┐      ┌──────────────┐              │
│    │   View   │◄─────│  Controller  │              │
│    │  (UI)    │      │ (Handles     │              │
│    └────┬─────┘      │  Input)      │              │
│         │            └──────┬───────┘              │
│         │                   │                       │
│         │            ┌──────▼───────┐              │
│         └───────────►│    Model     │              │
│                      │ (Data/Logic) │              │
│                      └──────────────┘              │
└─────────────────────────────────────────────────────┘
```

**Flow:**
1. User interacts with View
2. Controller handles input
3. Controller updates Model
4. Model notifies View
5. View renders updated data

#### MVVM (Model-View-ViewModel)

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│    ┌──────────┐      ┌──────────────┐              │
│    │   View   │◄────►│  ViewModel   │              │
│    │  (UI)    │ Data │ (Presentation│              │
│    └──────────┘Binding│   Logic)    │              │
│                      └──────┬───────┘              │
│                             │                       │
│                      ┌──────▼───────┐              │
│                      │    Model     │              │
│                      │ (Data/Logic) │              │
│                      └──────────────┘              │
└─────────────────────────────────────────────────────┘
```

**Key Features:**
- Two-way data binding
- ViewModel doesn't know about View
- Great for reactive frameworks (Angular, Vue)

---

### 2. Microservices Architecture
- [ ] Understand microservices principles
- [ ] Know benefits and challenges

```
┌─────────────────────────────────────────────────────────────┐
│                       API Gateway                            │
└─────────────────────────────┬───────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   User       │      │   Order      │      │   Payment    │
│   Service    │      │   Service    │      │   Service    │
│  ┌────────┐  │      │  ┌────────┐  │      │  ┌────────┐  │
│  │   DB   │  │      │  │   DB   │  │      │  │   DB   │  │
│  └────────┘  │      │  └────────┘  │      │  └────────┘  │
└──────────────┘      └──────────────┘      └──────────────┘
```

**Characteristics:**
- Single Responsibility
- Decentralized Data Management
- Independent Deployment
- Designed for Failure
- API-First Design

**Benefits:**
| Benefit | Description |
|---------|-------------|
| Scalability | Scale individual services independently |
| Flexibility | Use different technologies per service |
| Resilience | Failure isolation |
| Development | Independent team development |

**Challenges:**
| Challenge | Mitigation |
|-----------|------------|
| Distributed complexity | Use observability tools |
| Data consistency | Saga pattern, eventual consistency |
| Testing | Contract testing, integration tests |
| Operations | Kubernetes, service mesh |

---

### 3. Service-Oriented Architecture (SOA)
- [ ] Understand SOA principles
- [ ] Know difference from microservices

```
┌─────────────────────────────────────────────────────────────┐
│                    Enterprise Service Bus (ESB)              │
└──────┬──────────────────┬──────────────────┬───────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Service A  │   │   Service B  │   │   Service C  │
│  (CRM)       │   │  (Billing)   │   │  (Inventory) │
└──────────────┘   └──────────────┘   └──────────────┘
```

**SOA vs Microservices:**

| Aspect | SOA | Microservices |
|--------|-----|---------------|
| Scope | Enterprise-wide | Application level |
| Reuse | Maximum reuse | Avoid coupling |
| Data | Shared databases | Database per service |
| Communication | ESB (smart pipes) | Dumb pipes |
| Governance | Centralized | Decentralized |

---

### 4. Event-Driven Architecture
- [ ] Understand event patterns
- [ ] Know event sourcing

```
┌─────────────┐     Event      ┌─────────────────┐     Event      ┌─────────────┐
│  Producer   │ ─────────────► │   Event Store   │ ─────────────► │  Consumer   │
│  (Service)  │                │   (Kafka/etc)   │                │  (Service)  │
└─────────────┘                └─────────────────┘                └─────────────┘
                                       │
                                       ▼
                               ┌─────────────────┐
                               │   Consumer 2    │
                               │   (Analytics)   │
                               └─────────────────┘
```

**Event Types:**
1. **Event Notification** - Simple notification, minimal data
2. **Event-Carried State Transfer** - Full data in event
3. **Event Sourcing** - Events as source of truth

**Event Sourcing:**
```
Events:                              State:
┌─────────────────┐                  ┌────────────────┐
│ OrderCreated    │                  │ Current State  │
│ ItemAdded       │  ═══════════►    │ (Rebuilt from  │
│ ItemRemoved     │  Replay Events   │  all events)   │
│ OrderSubmitted  │                  │                │
└─────────────────┘                  └────────────────┘
```

---

### 5. Client-Server Architecture
- [ ] Understand client-server model
- [ ] Know variations

```
              Client Tier          Server Tier
           ┌─────────────┐      ┌─────────────┐
           │   Browser   │◄────►│   Web Server│
           │   Mobile    │      │   (API)     │
           │   Desktop   │      └──────┬──────┘
           └─────────────┘             │
                                ┌──────▼──────┐
                                │  Database   │
                                │   Server    │
                                └─────────────┘
```

**Types:**
- **2-Tier:** Client ↔ Server
- **3-Tier:** Client ↔ Application Server ↔ Database
- **N-Tier:** Multiple layers of servers

---

### 6. Serverless Architecture
- [ ] Understand serverless concepts
- [ ] Know FaaS patterns

```
┌─────────────────────────────────────────────────────────────┐
│                      Cloud Provider                          │
│                                                             │
│   ┌─────────┐     ┌─────────┐     ┌─────────┐              │
│   │ API     │────►│ Function │────►│ Database│              │
│   │ Gateway │     │ (Lambda) │     │ (DynamoDB)             │
│   └─────────┘     └─────────┘     └─────────┘              │
│                         │                                   │
│                   ┌─────▼─────┐                            │
│                   │  Storage  │                            │
│                   │  (S3)     │                            │
│                   └───────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

**Benefits:**
- No server management
- Automatic scaling
- Pay per execution
- Built-in high availability

**Challenges:**
- Cold starts
- Vendor lock-in
- Debugging complexity
- Execution time limits

---

## 📘 Advanced Architectural Patterns

### BFF Pattern (Backend for Frontend)

```
┌─────────┐   ┌─────────┐   ┌─────────┐
│   Web   │   │  Mobile │   │   TV    │
│   App   │   │   App   │   │   App   │
└────┬────┘   └────┬────┘   └────┬────┘
     │             │             │
┌────▼────┐   ┌────▼────┐   ┌────▼────┐
│ Web BFF │   │Mobile   │   │ TV BFF  │
│         │   │  BFF    │   │         │
└────┬────┘   └────┬────┘   └────┬────┘
     │             │             │
     └─────────────┼─────────────┘
                   │
           ┌───────▼───────┐
           │  Microservices │
           └───────────────┘
```

**Use When:**
- Different clients need different data shapes
- Want to optimize per platform
- Need client-specific logic

---

### API Gateway Pattern

```
                    ┌─────────────────┐
                    │   API Gateway   │
                    │  ┌───────────┐  │
     Request ──────►│  │ Auth      │  │
                    │  │ Rate Limit│  │
                    │  │ Routing   │  │
                    │  │ Transform │  │
                    │  └───────────┘  │
                    └────────┬────────┘
               ┌─────────────┼─────────────┐
               │             │             │
               ▼             ▼             ▼
         ┌─────────┐   ┌─────────┐   ┌─────────┐
         │Service A│   │Service B│   │Service C│
         └─────────┘   └─────────┘   └─────────┘
```

**Responsibilities:**
- Authentication/Authorization
- Rate limiting
- Request routing
- Protocol translation
- Response caching

---

### Strangler Fig Pattern

```
Phase 1: Identify                Phase 2: Strangle

┌───────────────────┐            ┌───────────────────┐
│     Monolith      │            │   Façade/Proxy    │
│  ┌─────┐ ┌─────┐  │            └─────────┬─────────┘
│  │  A  │ │  B  │  │                      │
│  ├─────┤ ├─────┤  │         ┌────────────┼────────────┐
│  │  C  │ │  D  │  │         │            │            │
│  └─────┘ └─────┘  │         ▼            ▼            ▼
└───────────────────┘    ┌─────────┐  ┌─────────┐  ┌─────────┐
                         │Service A│  │Monolith │  │Service B│
                         │ (New)   │  │ (C,D)   │  │ (New)   │
                         └─────────┘  └─────────┘  └─────────┘

Phase 3: Complete

┌───────────────────┐
│   Façade/Proxy    │
└─────────┬─────────┘
          │
    ┌─────┼─────┬─────┐
    │     │     │     │
    ▼     ▼     ▼     ▼
┌─────┐┌─────┐┌─────┐┌─────┐
│  A  ││  B  ││  C  ││  D  │
└─────┘└─────┘└─────┘└─────┘
```

**Steps:**
1. Put a façade in front of the monolith
2. Extract services gradually
3. Route traffic to new services
4. Eventually decommission monolith

---

## 🎯 Practice Task

### Compare and Choose Patterns

**Instructions:**
1. Given a scenario, choose the appropriate architectural pattern
2. Justify your choice with trade-offs

**Scenarios:**

| Scenario | Pattern Choice | Why |
|----------|----------------|-----|
| Startup MVP | | |
| Enterprise banking | | |
| Real-time analytics | | |
| E-commerce platform | | |
| Social media app | | |

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] Building Microservices - Sam Newman
- [ ] [Microsoft Azure Architecture Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/)
- [ ] [Martin Fowler's Blog](https://martinfowler.com/architecture/)

---

## ✅ Completion Checklist

- [ ] Understood MVC/MVVM
- [ ] Mastered microservices concepts
- [ ] Know SOA vs Microservices
- [ ] Understood event-driven architecture
- [ ] Learned serverless patterns
- [ ] Know BFF, API Gateway, Strangler Fig

**Date Completed:** _____________
