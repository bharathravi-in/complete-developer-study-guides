# Day 8: Scalability Basics

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. Vertical vs Horizontal Scaling
- [ ] Understand both scaling approaches
- [ ] Know when to use each

#### Vertical Scaling (Scale Up)

```
Before:                    After:
┌──────────────┐          ┌──────────────────────┐
│   Server     │          │      Server          │
│   4 CPU      │   ──►    │      16 CPU          │
│   8 GB RAM   │          │      64 GB RAM       │
│   100GB SSD  │          │      1TB SSD         │
└──────────────┘          └──────────────────────┘
```

**Pros:**
- Simple to implement
- No application changes needed
- No distributed complexity

**Cons:**
- Limited by hardware
- Single point of failure
- Expensive at scale
- Downtime during upgrade

---

#### Horizontal Scaling (Scale Out)

```
Before:                    After:
┌──────────────┐          ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Server     │          │   Server 1   │ │   Server 2   │ │   Server 3   │
│   4 CPU      │   ──►    │   4 CPU      │ │   4 CPU      │ │   4 CPU      │
│   8 GB RAM   │          │   8 GB RAM   │ │   8 GB RAM   │ │   8 GB RAM   │
└──────────────┘          └──────────────┘ └──────────────┘ └──────────────┘
                                    │             │             │
                                    └─────────────┼─────────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │  Load Balancer  │
                                         └─────────────────┘
```

**Pros:**
- Near-infinite scale
- Fault tolerance
- Cost-effective with commodity hardware
- No downtime for scaling

**Cons:**
- Application complexity
- Distributed system challenges
- Session management
- Data consistency

---

### 2. Stateless vs Stateful Architecture
- [ ] Understand state management
- [ ] Design for statelessness

#### Stateful Architecture (Avoid)

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Server A    │     │  Server B    │     │  Server C    │
│  [Session:   │     │  [Session:   │     │  [Session:   │
│   User123]   │     │   User456]   │     │   User789]   │
└──────────────┘     └──────────────┘     └──────────────┘

Problem: If Server A dies, User123's session is lost!
```

#### Stateless Architecture (Preferred)

```
                    ┌─────────────────┐
                    │  Load Balancer  │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Server A    │     │  Server B    │     │  Server C    │
│  (Stateless) │     │  (Stateless) │     │  (Stateless) │
└──────────────┘     └──────────────┘     └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Session Store  │
                    │  (Redis/DB)     │
                    └─────────────────┘

Any server can handle any request!
```

**Strategies for Statelessness:**
1. Store session in centralized store (Redis)
2. Use JWT tokens (stateless authentication)
3. Store state in database
4. Use sticky sessions (partial solution)

---

### 3. Load Balancing
- [ ] Understand load balancing algorithms
- [ ] Know different types

```
                         ┌────────────────────────┐
     Client Requests     │                        │
     ─────────────────►  │    Load Balancer       │
                         │                        │
                         │  ┌──────────────────┐  │
                         │  │ Routing Algorithm │  │
                         │  └──────────────────┘  │
                         └───────────┬────────────┘
                                     │
            ┌────────────────────────┼────────────────────────┐
            │                        │                        │
            ▼                        ▼                        ▼
     ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
     │  Server 1    │        │  Server 2    │        │  Server 3    │
     │  (Weight: 3) │        │  (Weight: 2) │        │  (Weight: 1) │
     └──────────────┘        └──────────────┘        └──────────────┘
```

#### Load Balancing Algorithms

| Algorithm | Description | Best For |
|-----------|-------------|----------|
| **Round Robin** | Rotate through servers sequentially | Equal capacity servers |
| **Weighted Round Robin** | Servers with higher weights get more traffic | Different capacity servers |
| **Least Connections** | Route to server with fewest connections | Varying request duration |
| **Least Response Time** | Route to fastest responding server | Performance-critical |
| **IP Hash** | Same client IP → same server | Session affinity |
| **Random** | Random selection | Simple setups |

#### Types of Load Balancers

| Type | Layer | Examples |
|------|-------|----------|
| **Hardware** | L4/L7 | F5, Citrix |
| **Software** | L4/L7 | HAProxy, NGINX |
| **Cloud** | L4/L7 | AWS ALB/NLB, Azure LB |
| **DNS** | L3 | Route 53, Cloudflare |

---

### 4. Reverse Proxy
- [ ] Understand reverse proxy concept
- [ ] Know use cases

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│   Internet                                                          │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Reverse Proxy (NGINX)                     │   │
│  │                                                             │   │
│  │  Features:                                                  │   │
│  │  • SSL Termination                                          │   │
│  │  • Caching                                                  │   │
│  │  • Compression                                              │   │
│  │  • Load Balancing                                           │   │
│  │  • Security (WAF)                                           │   │
│  │  • Request Routing                                          │   │
│  └────────────────────────┬────────────────────────────────────┘   │
│                           │                                        │
│            ┌──────────────┼──────────────┐                        │
│            │              │              │                        │
│            ▼              ▼              ▼                        │
│       ┌─────────┐   ┌─────────┐   ┌─────────┐                    │
│       │ App 1   │   │ App 2   │   │ Static  │                    │
│       │ /api    │   │ /admin  │   │ /assets │                    │
│       └─────────┘   └─────────┘   └─────────┘                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Reverse Proxy vs Load Balancer:**

| Feature | Reverse Proxy | Load Balancer |
|---------|---------------|---------------|
| Primary role | Hide backend servers | Distribute traffic |
| SSL termination | Yes | Sometimes |
| Caching | Yes | No |
| Compression | Yes | No |
| URL rewriting | Yes | No |
| Multiple backends | Yes | Yes |

---

## 📘 Advanced Topics

### Auto Scaling

```
┌─────────────────────────────────────────────────────────────────────┐
│  Auto Scaling Group                                                  │
│                                                                     │
│  Scaling Policy:                                                    │
│  • Min: 2 instances                                                 │
│  • Max: 10 instances                                                │
│  • Target CPU: 70%                                                  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    CloudWatch Metrics                         │  │
│  │                                                              │  │
│  │  CPU > 70% for 5 min  ──►  Scale OUT (+2 instances)         │  │
│  │  CPU < 30% for 10 min ──►  Scale IN  (-1 instance)          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Current: 4 instances                                               │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                                  │
│  │ i-1 │ │ i-2 │ │ i-3 │ │ i-4 │                                  │
│  └─────┘ └─────┘ └─────┘ └─────┘                                  │
└─────────────────────────────────────────────────────────────────────┘
```

**Scaling Strategies:**
- **Target Tracking:** Maintain target metric (e.g., CPU at 70%)
- **Step Scaling:** Scale based on alarm thresholds
- **Scheduled:** Scale at specific times
- **Predictive:** ML-based scaling (AWS)

---

### Database Scaling Patterns

```
Read Scaling with Replicas:
                         ┌─────────────────┐
                         │    Primary      │
                         │   (Write)       │
                         └────────┬────────┘
                                  │ Replication
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
            ▼                     ▼                     ▼
     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
     │   Replica 1  │     │   Replica 2  │     │   Replica 3  │
     │   (Read)     │     │   (Read)     │     │   (Read)     │
     └──────────────┘     └──────────────┘     └──────────────┘


Write Scaling with Sharding:
     ┌─────────────────────────────────────────────────────┐
     │                   Shard Router                       │
     └──────────────────────┬──────────────────────────────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │   Shard 1    │ │   Shard 2    │ │   Shard 3    │
    │  Users A-H   │ │  Users I-P   │ │  Users Q-Z   │
    └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 🎯 Practice Task

### Design Scalable Architecture

**Instructions:**
1. Take a simple web application
2. Design scalable architecture
3. Show how it handles 100, 10K, 1M users

**Template:**

```markdown
## System: [Application Name]

### Current Load
- Users: 100
- Requests/sec: 10

### Architecture for 100 Users
[Diagram]

### Architecture for 10,000 Users
[Diagram + What changed]

### Architecture for 1,000,000 Users
[Diagram + What changed]

### Scaling Decisions
| Component | Strategy | Reason |
|-----------|----------|--------|
| Web servers | | |
| Database | | |
| Cache | | |
| CDN | | |
```

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [ ] [NGINX Load Balancing](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/)
- [ ] Designing Data-Intensive Applications - Ch. 1

---

## ✅ Completion Checklist

- [ ] Understood vertical vs horizontal scaling
- [ ] Know stateless architecture design
- [ ] Mastered load balancing concepts
- [ ] Understand reverse proxy
- [ ] Know auto-scaling strategies
- [ ] Completed practice task

**Date Completed:** _____________
