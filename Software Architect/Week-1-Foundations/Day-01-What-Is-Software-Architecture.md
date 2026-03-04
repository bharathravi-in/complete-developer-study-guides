# Day 1: What is Software Architecture?

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. Architecture vs Design
- [ ] Understand the difference between architecture and design
- [ ] Learn when to focus on architecture vs implementation details

| Aspect | Architecture | Design |
|--------|-------------|--------|
| **Scope** | System-wide, high-level | Component-level, detailed |
| **Focus** | Structure, quality attributes | Implementation details |
| **Change Cost** | Expensive to change | Easier to modify |
| **Examples** | Microservices, Event-driven | Class structure, algorithms |

### 2. Role of Software Architect
- [ ] Technical leadership responsibilities
- [ ] Decision-making authority
- [ ] Cross-team coordination

**Key Responsibilities:**
- Define system structure and technology stack
- Make high-impact technical decisions
- Ensure quality attributes (performance, security, scalability)
- Guide and mentor development teams
- Communicate with stakeholders

### 3. Architect vs Technical Lead

| Aspect | Software Architect | Technical Lead |
|--------|-------------------|----------------|
| **Scope** | Cross-project/system | Single project/team |
| **Focus** | Long-term vision | Short-term delivery |
| **Coding** | Less hands-on | More hands-on |
| **Decisions** | System-wide | Team/module level |

### 4. Quality Attributes (NFRs)
- [ ] Understand key quality attributes

| Attribute | Description | Measurement |
|-----------|-------------|-------------|
| **Scalability** | Handle increased load | Users, requests/sec |
| **Availability** | System uptime | 99.9%, 99.99% (SLA) |
| **Reliability** | Consistent correct behavior | MTBF, error rates |
| **Security** | Protection from threats | Vulnerabilities, compliance |
| **Performance** | Response time, throughput | Latency (p50, p95, p99) |
| **Maintainability** | Ease of modification | Time to implement changes |

---

## 📘 Deep Dive Topics

### 4+1 View Model (Philippe Kruchten)

```
                    ┌─────────────────┐
                    │   Scenarios     │
                    │  (Use Cases)    │
                    └────────┬────────┘
                             │
    ┌────────────────────────┼────────────────────────┐
    │                        │                        │
    ▼                        ▼                        ▼
┌─────────┐           ┌─────────┐           ┌─────────┐
│ Logical │           │ Process │           │ Physical│
│  View   │           │  View   │           │  View   │
└─────────┘           └─────────┘           └─────────┘
    │                                            │
    └──────────────┬─────────────────────────────┘
                   │
                   ▼
            ┌─────────────┐
            │ Development │
            │    View     │
            └─────────────┘
```

| View | Focus | Stakeholders |
|------|-------|--------------|
| **Logical** | Functionality, objects, classes | End users, analysts |
| **Process** | Concurrency, threads, processes | System integrators |
| **Physical** | Hardware, deployment | Operations, infra team |
| **Development** | Code organization, modules | Developers |
| **Scenarios** | Use cases connecting all views | All stakeholders |

### ISO/IEC 25010 Quality Model

```
Quality Characteristics:
├── Functional Suitability
│   ├── Completeness
│   ├── Correctness
│   └── Appropriateness
├── Performance Efficiency
│   ├── Time behavior
│   ├── Resource utilization
│   └── Capacity
├── Compatibility
│   ├── Co-existence
│   └── Interoperability
├── Usability
│   ├── Appropriateness recognizability
│   ├── Learnability
│   ├── Operability
│   └── User error protection
├── Reliability
│   ├── Maturity
│   ├── Availability
│   ├── Fault tolerance
│   └── Recoverability
├── Security
│   ├── Confidentiality
│   ├── Integrity
│   ├── Non-repudiation
│   ├── Accountability
│   └── Authenticity
├── Maintainability
│   ├── Modularity
│   ├── Reusability
│   ├── Analyzability
│   ├── Modifiability
│   └── Testability
└── Portability
    ├── Adaptability
    ├── Installability
    └── Replaceability
```

### Architectural Characteristics

**Operational Characteristics:**
- Availability, Continuity, Performance, Recoverability, Reliability, Scalability

**Structural Characteristics:**
- Configurability, Extensibility, Maintainability, Portability, Supportability

**Cross-cutting Characteristics:**
- Accessibility, Security, Privacy, Legal compliance

---

## 🎯 Practice Task

### Redesign Your Past Angular Project

**Instructions:**
1. Pick one of your Angular projects
2. Document the current architecture
3. Identify architectural decisions (explicit or implicit)
4. List quality attributes you need to consider
5. Create a high-level architecture diagram

**Template:**

```markdown
## Project: [Your Project Name]

### Current State
- Architecture Style: [Monolith/Modular/etc.]
- Key Components: [List main modules]
- Technology Stack: [Angular, Backend, DB, etc.]

### Quality Attributes Analysis
| Attribute | Current State | Target State | Gap |
|-----------|---------------|--------------|-----|
| Scalability | | | |
| Performance | | | |
| Security | | | |
| Maintainability | | | |

### Architectural Decisions
1. Decision: [What]
   - Rationale: [Why]
   - Consequences: [Trade-offs]

### High-Level Diagram
[Create using draw.io or excalidraw]

### Improvement Opportunities
1. [Area 1]
2. [Area 2]
```

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] [Fundamentals of Software Architecture - Ch.1](https://www.oreilly.com/library/view/fundamentals-of-software/9781492043447/)
- [ ] [4+1 View Model Paper](https://www.cs.ubc.ca/~gregor/teaching/papers/4+1view-architecture.pdf)
- [ ] [ISO 25010 Overview](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010)

---

## ✅ Completion Checklist

- [ ] Understood Architecture vs Design
- [ ] Know the role of Software Architect
- [ ] Learned 4+1 View Model
- [ ] Understand ISO 25010 Quality Model
- [ ] Completed practice task
- [ ] Made personal notes

**Date Completed:** _____________
