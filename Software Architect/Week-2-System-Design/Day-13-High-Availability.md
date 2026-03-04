# Day 13: High Availability & Fault Tolerance

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. Replication
- [ ] Understand replication strategies
- [ ] Know leader-follower patterns

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Single-Leader Replication                                               │
│                                                                         │
│                         ┌─────────────────┐                            │
│    Writes ─────────────►│     Leader      │                            │
│                         │    (Primary)    │                            │
│                         └────────┬────────┘                            │
│                                  │                                      │
│                       Replication (sync/async)                         │
│                                  │                                      │
│           ┌──────────────────────┼──────────────────────┐              │
│           │                      │                      │              │
│           ▼                      ▼                      ▼              │
│    ┌──────────────┐       ┌──────────────┐       ┌──────────────┐     │
│    │  Follower 1  │       │  Follower 2  │       │  Follower 3  │     │
│    │   (Replica)  │       │   (Replica)  │       │   (Replica)  │     │
│    └──────────────┘       └──────────────┘       └──────────────┘     │
│           │                      │                      │              │
│           └──────────────────────┼──────────────────────┘              │
│                                  │                                      │
│    Reads ◄───────────────────────┘                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Replication Types:**

| Type | Consistency | Latency | Durability |
|------|-------------|---------|------------|
| **Synchronous** | Strong | Higher | High |
| **Asynchronous** | Eventual | Lower | Lower |
| **Semi-sync** | Balanced | Medium | Medium |

```
Multi-Leader Replication:
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   Region A                          Region B                           │
│   ┌─────────────────┐              ┌─────────────────┐                 │
│   │     Leader A    │◄────────────►│     Leader B    │                 │
│   └────────┬────────┘   Bidirect   └────────┬────────┘                 │
│            │            Replication          │                          │
│   ┌────────┴────────┐              ┌────────┴────────┐                 │
│   │    Followers    │              │    Followers    │                 │
│   └─────────────────┘              └─────────────────┘                 │
│                                                                         │
│   Challenges: Conflict resolution, eventual consistency                │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 2. Failover
- [ ] Understand failover strategies
- [ ] Know automatic vs manual failover

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Automatic Failover                                                      │
│                                                                         │
│  Normal Operation:                                                      │
│  ┌──────────────┐         ┌──────────────┐                             │
│  │    Primary   │  ◄───   │   Standby    │                             │
│  │   (Active)   │  Sync   │  (Passive)   │                             │
│  └──────────────┘         └──────────────┘                             │
│         │                                                               │
│    Traffic                                                              │
│                                                                         │
│  After Failover:                                                        │
│  ┌──────────────┐         ┌──────────────┐                             │
│  │    Primary   │         │   Standby    │                             │
│  │    (Down)    │         │  (Promoted)  │                             │
│  └──────────────┘         └──────────────┘                             │
│                                  │                                      │
│                             Traffic                                     │
│                                                                         │
│  Detection → Election → Promotion → DNS/LB Update                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Failover Strategies:**

| Strategy | Description | Recovery Time |
|----------|-------------|---------------|
| **Active-Passive** | Standby takes over | Seconds-minutes |
| **Active-Active** | Load shared | Near-instant |
| **Pilot Light** | Minimal standby | Minutes |
| **Warm Standby** | Scaled-down copy | Seconds |

---

### 3. Health Checks
- [ ] Understand health check types
- [ ] Implement proper health endpoints

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Health Check Architecture                                               │
│                                                                         │
│   ┌─────────────────┐                                                   │
│   │  Load Balancer  │                                                   │
│   │     /health     │◄───────── Check every 10s                        │
│   └────────┬────────┘                                                   │
│            │                                                            │
│     ┌──────┼──────┬──────┐                                             │
│     │      │      │      │                                             │
│     ▼      ▼      ▼      ▼                                             │
│   ┌────┐ ┌────┐ ┌────┐ ┌────┐                                         │
│   │ ✓  │ │ ✓  │ │ ✗  │ │ ✓  │                                         │
│   │200 │ │200 │ │503 │ │200 │                                         │
│   └────┘ └────┘ └────┘ └────┘                                         │
│   Server Server Server Server                                          │
│     1      2      3      4                                             │
│                    │                                                    │
│                    └─── Removed from pool                              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Health Check Types:**

```typescript
// Liveness Check - Is the app running?
app.get('/health/live', (req, res) => {
  res.status(200).json({ status: 'alive' });
});

// Readiness Check - Is the app ready to serve?
app.get('/health/ready', async (req, res) => {
  const checks = {
    database: await checkDatabase(),
    cache: await checkRedis(),
    queue: await checkKafka()
  };
  
  const allHealthy = Object.values(checks).every(v => v);
  
  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? 'ready' : 'degraded',
    checks
  });
});

// Deep Health Check - Detailed status
app.get('/health/deep', async (req, res) => {
  res.json({
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    database: {
      connected: true,
      latency: '5ms'
    },
    dependencies: [...]
  });
});
```

---

### 4. Circuit Breaker
- [ ] Master circuit breaker pattern
- [ ] Know state transitions

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Circuit Breaker States                                                  │
│                                                                         │
│         ┌─────────────────────────────────────────────────────────────┐│
│         │                                                             ││
│         │              ┌───────────────┐                              ││
│         │   Success    │    CLOSED     │◄──── Requests flow normally  ││
│         │   (below     │               │                              ││
│         │   threshold) └───────┬───────┘                              ││
│         │                      │                                      ││
│         │              Failures exceed                                ││
│         │              threshold (e.g., 5)                            ││
│         │                      │                                      ││
│         │                      ▼                                      ││
│         │              ┌───────────────┐                              ││
│         └──────────────│     OPEN      │◄──── Requests fail fast      ││
│                        │               │      (no remote calls)       ││
│                        └───────┬───────┘                              ││
│                                │                                      ││
│                         Timeout expires                               ││
│                         (e.g., 30 seconds)                            ││
│                                │                                      ││
│                                ▼                                      ││
│                        ┌───────────────┐                              ││
│                        │  HALF-OPEN    │◄──── Allow limited requests  ││
│                        │               │      to test recovery        ││
│                        └───────┬───────┘                              ││
│                                │                                      ││
│              ┌─────────────────┴─────────────────┐                    ││
│              │                                   │                    ││
│         Success                             Failure                   ││
│              │                                   │                    ││
│              ▼                                   ▼                    ││
│       Back to CLOSED                      Back to OPEN               ││
│                                                                       ││
└─────────────────────────────────────────────────────────────────────────┘
```

**Circuit Breaker Implementation:**

```typescript
class CircuitBreaker {
  private state: 'CLOSED' | 'OPEN' | 'HALF_OPEN' = 'CLOSED';
  private failures = 0;
  private lastFailure: Date | null = null;
  
  constructor(
    private threshold: number = 5,
    private timeout: number = 30000,
    private halfOpenAttempts: number = 3
  ) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailure!.getTime() > this.timeout) {
        this.state = 'HALF_OPEN';
      } else {
        throw new Error('Circuit is OPEN');
      }
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess() {
    this.failures = 0;
    this.state = 'CLOSED';
  }

  private onFailure() {
    this.failures++;
    this.lastFailure = new Date();
    if (this.failures >= this.threshold) {
      this.state = 'OPEN';
    }
  }
}
```

---

## 📘 High Availability Patterns

### N+1 Redundancy

```
┌─────────────────────────────────────────────────────────────────────────┐
│  N+1 Redundancy                                                          │
│                                                                         │
│  If you need N servers to handle load, deploy N+1                      │
│                                                                         │
│  Example: Need 3 servers at 100% capacity                              │
│                                                                         │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐                               │
│  │ S1   │  │ S2   │  │ S3   │  │ S4   │                               │
│  │ 75%  │  │ 75%  │  │ 75%  │  │ Spare│                               │
│  └──────┘  └──────┘  └──────┘  └──────┘                               │
│                                                                         │
│  If S1 fails → S2, S3, S4 each handle 100% (still capacity)           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Multi-Zone Deployment

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Multi-AZ Architecture                                                   │
│                                                                         │
│  Region: us-east-1                                                      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │  ┌───────────────────┐    ┌───────────────────┐                │   │
│  │  │      AZ-1a        │    │      AZ-1b        │                │   │
│  │  │                   │    │                   │                │   │
│  │  │  ┌─────┐ ┌─────┐  │    │  ┌─────┐ ┌─────┐  │                │   │
│  │  │  │ App │ │ App │  │    │  │ App │ │ App │  │                │   │
│  │  │  └─────┘ └─────┘  │    │  └─────┘ └─────┘  │                │   │
│  │  │                   │    │                   │                │   │
│  │  │  ┌─────────────┐  │    │  ┌─────────────┐  │                │   │
│  │  │  │ DB Primary  │◄─┼────┼─►│ DB Standby  │  │                │   │
│  │  │  └─────────────┘  │    │  └─────────────┘  │                │   │
│  │  │                   │    │                   │                │   │
│  │  └───────────────────┘    └───────────────────┘                │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Benefits: Survive AZ failure, low-latency replication                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Availability Calculation

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Availability Targets                                                    │
│                                                                         │
│  Availability    Downtime/Year    Downtime/Month   Downtime/Day        │
│  ─────────────────────────────────────────────────────────────────     │
│  99%             3.65 days        7.2 hours        14.4 min            │
│  99.9%           8.76 hours       43.8 min         1.44 min            │
│  99.99%          52.6 min         4.38 min         8.64 sec            │
│  99.999%         5.26 min         26.3 sec         0.86 sec            │
│                                                                         │
│  Serial Components: A_total = A1 × A2 × A3                             │
│  Example: 99.9% × 99.9% × 99.9% = 99.7%                                │
│                                                                         │
│  Parallel Components: A_total = 1 - (1-A1) × (1-A2)                    │
│  Example: 1 - (0.001 × 0.001) = 99.9999%                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Practice Task

### Design High Availability Architecture

**Instructions:**
1. Design HA architecture for a payment system
2. Target: 99.99% availability
3. Include: Failover, health checks, circuit breakers
4. Multi-region setup

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] [AWS Well-Architected: Reliability](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
- [ ] [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [ ] Site Reliability Engineering (Google SRE Book)

---

## ✅ Completion Checklist

- [ ] Understood replication strategies
- [ ] Know failover patterns
- [ ] Can implement health checks
- [ ] Mastered circuit breaker
- [ ] Completed practice task

**Date Completed:** _____________
