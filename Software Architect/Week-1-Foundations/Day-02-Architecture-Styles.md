# Day 2: Architecture Styles

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. Monolith Architecture
- [ ] Understand monolithic architecture
- [ ] Know when to use monolith

```
┌────────────────────────────────────────┐
│            MONOLITH                    │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │    UI    │ │ Business │ │  Data  │ │
│  │  Layer   │ │  Logic   │ │ Access │ │
│  └──────────┘ └──────────┘ └────────┘ │
│                    │                   │
│              ┌─────┴─────┐            │
│              │  Database │            │
│              └───────────┘            │
└────────────────────────────────────────┘
```

**Pros:** Simple deployment, easy debugging, no network latency  
**Cons:** Scaling limitations, technology lock-in, deployment coupling

---

### 2. Layered Architecture
- [ ] Understand layers and their responsibilities
- [ ] Know the flow of requests

```
┌─────────────────────────────────────┐
│      Presentation Layer             │  ← UI, Controllers
├─────────────────────────────────────┤
│       Business Layer                │  ← Business Logic, Services
├─────────────────────────────────────┤
│      Persistence Layer              │  ← Repositories, DAOs
├─────────────────────────────────────┤
│       Database Layer                │  ← Database
└─────────────────────────────────────┘
```

**Rules:**
- Each layer can only access the layer directly below
- Strict layering prevents cross-layer access
- Open layers can be bypassed

---

### 3. Clean Architecture (Robert C. Martin)
- [ ] Understand dependency rule
- [ ] Know the layers and their purpose

```
        ┌─────────────────────────────────┐
        │   Frameworks & Drivers          │
        │  (UI, DB, External Services)    │
        │    ┌─────────────────────────┐  │
        │    │    Interface Adapters   │  │
        │    │  (Controllers, Gateways)│  │
        │    │   ┌─────────────────┐   │  │
        │    │   │  Application    │   │  │
        │    │   │  Business Rules │   │  │
        │    │   │  ┌───────────┐  │   │  │
        │    │   │  │ Enterprise│  │   │  │
        │    │   │  │ Business  │  │   │  │
        │    │   │  │   Rules   │  │   │  │
        │    │   │  └───────────┘  │   │  │
        │    │   └─────────────────┘   │  │
        │    └─────────────────────────┘  │
        └─────────────────────────────────┘
```

**Dependency Rule:** Source code dependencies must point inwards only.

---

### 4. Hexagonal Architecture (Ports & Adapters)
- [ ] Understand ports and adapters
- [ ] Know how to achieve technology independence

```
         ┌───────────────────────────────────────┐
         │              Adapters                  │
         │    ┌─────┐              ┌─────┐       │
         │    │ REST│              │ CLI │       │
         │    └──┬──┘              └──┬──┘       │
         │       │    ┌─────────┐    │          │
         │       └───►│  Ports  │◄───┘          │
         │            │ (Input) │               │
         │            └────┬────┘               │
         │                 │                     │
         │         ┌───────▼───────┐            │
         │         │   Application │            │
         │         │     Core      │            │
         │         └───────┬───────┘            │
         │                 │                     │
         │            ┌────▼────┐               │
         │            │  Ports  │               │
         │            │(Output) │               │
         │       ┌────┴────┬────┴────┐          │
         │    ┌──▼──┐   ┌──▼──┐   ┌──▼──┐      │
         │    │ DB  │   │ API │   │Queue│      │
         │    └─────┘   └─────┘   └─────┘      │
         └───────────────────────────────────────┘
```

**Key Concepts:**
- **Ports:** Interfaces that define how the application interacts with outside
- **Adapters:** Implementations of ports for specific technologies

---

### 5. Onion Architecture
- [ ] Understand the layers
- [ ] Know the relationship to Clean Architecture

```
        ┌─────────────────────────────────────┐
        │           Infrastructure            │
        │    ┌─────────────────────────┐      │
        │    │      Application        │      │
        │    │   ┌─────────────────┐   │      │
        │    │   │  Domain Services│   │      │
        │    │   │   ┌─────────┐   │   │      │
        │    │   │   │ Domain  │   │   │      │
        │    │   │   │  Model  │   │   │      │
        │    │   │   └─────────┘   │   │      │
        │    │   └─────────────────┘   │      │
        │    └─────────────────────────┘      │
        └─────────────────────────────────────┘
```

**Layers:**
1. **Domain Model** - Entities, Value Objects
2. **Domain Services** - Business logic
3. **Application Services** - Use cases, orchestration
4. **Infrastructure** - External concerns (DB, UI, etc.)

---

### 6. Microkernel Architecture
- [ ] Understand plugin-based architecture
- [ ] Know use cases

```
┌─────────────────────────────────────────────────┐
│                  Plugins                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │ Plugin  │  │ Plugin  │  │ Plugin  │         │
│  │    A    │  │    B    │  │    C    │         │
│  └────┬────┘  └────┬────┘  └────┬────┘         │
│       │            │            │               │
│       └────────────┼────────────┘               │
│                    │                            │
│            ┌───────▼───────┐                   │
│            │   Core System │                   │
│            │  (Microkernel)│                   │
│            └───────────────┘                   │
└─────────────────────────────────────────────────┘
```

**Examples:** IDEs, Browsers, VS Code, Eclipse  
**Pros:** Extensibility, independent plugin development  
**Cons:** Plugin API design complexity

---

### 7. Event-Driven Architecture
- [ ] Understand event producers and consumers
- [ ] Know event patterns

```
┌────────────┐     ┌─────────────────┐     ┌────────────┐
│  Producer  │────►│   Event Broker  │────►│  Consumer  │
│  Service   │     │  (Kafka/Queue)  │     │  Service   │
└────────────┘     └─────────────────┘     └────────────┘
       │                   │                      │
       │                   │                      │
       ▼                   ▼                      ▼
   Event: OrderCreated  │  Topic: orders     │  Process Order
```

**Patterns:**
- **Event Notification** - Fire and forget
- **Event-Carried State Transfer** - Event contains full data
- **Event Sourcing** - Store events as source of truth
- **CQRS** - Separate read/write models

---

## 🎯 Practice Task

### Convert a Monolith App into Clean Architecture Diagram

**Instructions:**
1. Take any monolith application you know
2. Identify the different concerns
3. Map components to Clean Architecture layers
4. Create a diagram showing the transformation

**Template:**

```markdown
## Application: [Name]

### Current Monolith Structure
[Describe current architecture]

### Mapping to Clean Architecture

| Current Component | Clean Architecture Layer |
|-------------------|--------------------------|
| Controllers | Interface Adapters |
| Services | Application Business Rules |
| Models/Entities | Enterprise Business Rules |
| Database Access | Interface Adapters |
| External APIs | Frameworks & Drivers |

### Clean Architecture Diagram
[Create diagram]

### Migration Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Benefits After Migration
- [ ] Benefit 1
- [ ] Benefit 2
```

---

## 📊 Comparison Table

| Style | Best For | Complexity | Scalability |
|-------|----------|------------|-------------|
| Monolith | Small apps, startups | Low | Low |
| Layered | Traditional enterprise | Medium | Medium |
| Clean | Domain-focused apps | Medium-High | High |
| Hexagonal | Testable, adaptable apps | Medium-High | High |
| Microkernel | Extensible products | Medium | Medium |
| Event-Driven | Async, decoupled systems | High | High |

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] Clean Architecture Book - Robert C. Martin
- [ ] [Hexagonal Architecture Explained](https://alistair.cockburn.us/hexagonal-architecture/)
- [ ] [Event-Driven Architecture Pattern](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/)

---

## ✅ Completion Checklist

- [ ] Understood all architecture styles
- [ ] Know differences between Clean, Hexagonal, Onion
- [ ] Completed monolith to clean architecture task
- [ ] Made personal notes

**Date Completed:** _____________
