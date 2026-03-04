# Day 12: Messaging Systems

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. Apache Kafka
- [ ] Understand Kafka architecture
- [ ] Know use cases

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Kafka Architecture                                                      │
│                                                                         │
│               ┌─────────────────────────────────────────────────────┐   │
│               │                   Kafka Cluster                      │   │
│               │                                                     │   │
│   Producers   │   ┌─────────────────────────────────────────────┐   │   │
│       │       │   │              Topic: orders                   │   │   │
│       │       │   │                                             │   │   │
│       │       │   │   Partition 0  ┌───┬───┬───┬───┬───┐       │   │   │
│       │       │   │                │ 0 │ 1 │ 2 │ 3 │ 4 │       │   │   │
│       └───────┼──►│                └───┴───┴───┴───┴───┘       │   │   │
│               │   │                                             │   │   │
│               │   │   Partition 1  ┌───┬───┬───┬───┐           │   │   │
│               │   │                │ 0 │ 1 │ 2 │ 3 │           │   │   │
│               │   │                └───┴───┴───┴───┘           │   │   │
│               │   │                                             │   │   │
│               │   │   Partition 2  ┌───┬───┬───┬───┬───┬───┐   │   │   │
│               │   │                │ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │   │   │   │
│               │   │                └───┴───┴───┴───┴───┴───┘   │   │   │
│               │   └─────────────────────────────────────────────┘   │   │
│               │                       │                             │   │
│               │                       ▼                             │   │
│               │   ┌─────────────────────────────────────────────┐   │   │
│               │   │           Consumer Groups                    │   │   │
│               │   │                                             │   │   │
│               │   │   Group A:  [C1] [C2] [C3]                  │   │   │
│               │   │   Group B:  [C4] [C5]                       │   │   │
│               │   └─────────────────────────────────────────────┘   │   │
│               └─────────────────────────────────────────────────────┘   │
│                                                                         │
│   Key Concepts:                                                         │
│   • Topics: Categories of messages                                     │
│   • Partitions: Parallel units within topic                           │
│   • Consumer Groups: Load balancing across consumers                  │
│   • Offset: Position in partition                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

**Kafka Use Cases:**

| Use Case | Description |
|----------|-------------|
| Event Streaming | Real-time event processing |
| Log Aggregation | Collect logs from services |
| Metrics | Time-series data collection |
| Event Sourcing | Store events as source of truth |
| Message Queue | Async communication |
| Change Data Capture | DB change events |

**Key Features:**
- High throughput (millions of messages/sec)
- Persistence on disk
- Horizontal scalability
- Replication for fault tolerance

---

### 2. RabbitMQ
- [ ] Understand RabbitMQ architecture
- [ ] Know exchange types

```
┌─────────────────────────────────────────────────────────────────────────┐
│  RabbitMQ Architecture                                                   │
│                                                                         │
│   Producer                    Exchange                  Queue           │
│       │                          │                        │             │
│       │    ┌──────────┐         │         ┌──────────┐   │             │
│       └───►│ Exchange │─────────┼────────►│  Queue   │───┼──► Consumer │
│            │          │         │         │          │   │             │
│            │  Type:   │         │         └──────────┘   │             │
│            │  - Direct│     Routing                      │             │
│            │  - Fanout│     Key/Binding                  │             │
│            │  - Topic │                                  │             │
│            │  - Headers│                                 │             │
│            └──────────┘                                  │             │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Exchange Types:**

```
1. Direct Exchange (Exact routing key match)
┌──────────┐     routing_key: "error"     ┌─────────────┐
│ Producer │ ────────────────────────────►│ Error Queue │
└──────────┘                              └─────────────┘

2. Fanout Exchange (Broadcast to all queues)
┌──────────┐                              ┌─────────────┐
│ Producer │ ──────────┬─────────────────►│  Queue 1    │
└──────────┘           │                  └─────────────┘
                       │                  ┌─────────────┐
                       └─────────────────►│  Queue 2    │
                                          └─────────────┘

3. Topic Exchange (Pattern matching)
┌──────────┐     routing_key: "order.created.us"
│ Producer │ ────────────────────────────────────────────►
└──────────┘
                Binding: "order.*.us"     ┌─────────────┐
                ─────────────────────────►│ US Orders   │
                                          └─────────────┘
                Binding: "order.created.*" ┌─────────────┐
                ─────────────────────────►│ All Created │
                                          └─────────────┘
```

---

### 3. Pub/Sub Pattern
- [ ] Understand publish-subscribe
- [ ] Know implementations

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Pub/Sub Pattern                                                         │
│                                                                         │
│                    ┌────────────────────────┐                           │
│   Publishers       │     Message Broker     │       Subscribers         │
│                    │      (Topic)           │                           │
│   ┌──────────┐     │                        │     ┌──────────┐          │
│   │Publisher │────►│  ┌──────────────────┐  │────►│Subscriber│          │
│   │    A     │     │  │  Event: Order    │  │     │    1     │          │
│   └──────────┘     │  │  Created         │  │     └──────────┘          │
│                    │  └──────────────────┘  │                           │
│   ┌──────────┐     │                        │     ┌──────────┐          │
│   │Publisher │────►│                        │────►│Subscriber│          │
│   │    B     │     │                        │     │    2     │          │
│   └──────────┘     │                        │     └──────────┘          │
│                    │                        │                           │
│                    └────────────────────────┘     ┌──────────┐          │
│                                             ────►│Subscriber│          │
│                                                   │    3     │          │
│                                                   └──────────┘          │
│                                                                         │
│   Implementations: Kafka Topics, Redis Pub/Sub, AWS SNS, Google Pub/Sub│
└─────────────────────────────────────────────────────────────────────────┘
```

**Pub/Sub vs Message Queue:**

| Aspect | Pub/Sub | Message Queue |
|--------|---------|---------------|
| Delivery | All subscribers | One consumer |
| Use Case | Event notification | Task distribution |
| Example | Order created event | Process payment |

---

### 4. Event Streaming
- [ ] Understand event streaming concepts
- [ ] Know event-driven design

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Event Streaming Architecture                                            │
│                                                                         │
│   Event Producers                    Event Store                        │
│   (Services)                         (Kafka)                            │
│                                                                         │
│   ┌──────────┐                    ┌────────────────────────────────┐    │
│   │  Order   │   OrderCreated     │  Topic: domain-events           │    │
│   │ Service  │───────────────────►│                                │    │
│   └──────────┘                    │  ┌────┬────┬────┬────┐         │    │
│                                   │  │ E1 │ E2 │ E3 │ E4 │ ──────► │    │
│   ┌──────────┐                    │  └────┴────┴────┴────┘         │    │
│   │ Payment  │   PaymentProcessed │                                │    │
│   │ Service  │───────────────────►│                                │    │
│   └──────────┘                    └────────────────────────────────┘    │
│                                              │                          │
│                                              ▼                          │
│   Event Consumers                                                       │
│   (Processors)                    ┌──────────────┐                     │
│                                   │   Stream     │                     │
│   ┌──────────────┐               │  Processor   │                     │
│   │  Analytics   │◄──────────────│  (Flink/     │                     │
│   │   Service    │               │   Spark)     │                     │
│   └──────────────┘               └──────────────┘                     │
│                                                                         │
│   ┌──────────────┐                                                     │
│   │  Notification│◄─────────────────────────────────────────────────   │
│   │   Service    │                                                     │
│   └──────────────┘                                                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📘 Advanced Topics

### Idempotency
- [ ] Understand idempotent operations
- [ ] Implement idempotency

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Idempotency Pattern                                                     │
│                                                                         │
│  Problem: Message delivered twice                                       │
│                                                                         │
│  Request 1: Process $100 payment  → Balance: $900                      │
│  Request 1: Process $100 payment  → Balance: $800 ❌ (Double charge!)  │
│                                                                         │
│  Solution: Idempotency Key                                              │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  Message: {                                                      │   │
│  │    idempotencyKey: "txn-12345",                                  │   │
│  │    action: "debit",                                              │   │
│  │    amount: 100                                                   │   │
│  │  }                                                               │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Consumer:                                                              │
│  1. Check if idempotencyKey exists in processed set                    │
│  2. If exists, return cached result (no-op)                            │
│  3. If not, process and store key                                      │
│                                                                         │
│  Request 1: Process → Store "txn-12345" → Balance: $900               │
│  Request 1: Check "txn-12345" exists → Return cached → Still $900 ✓   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Exactly-Once Delivery
- [ ] Understand delivery semantics
- [ ] Know trade-offs

**Delivery Semantics:**

| Semantic | Description | Implementation |
|----------|-------------|----------------|
| **At-most-once** | May lose messages | Fire and forget |
| **At-least-once** | May duplicate | Ack after process |
| **Exactly-once** | No loss, no dup | Transactions + Idempotency |

```
Exactly-Once in Kafka:
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   Producer                              Broker                          │
│      │                                    │                             │
│      │ 1. Begin Transaction               │                             │
│      ├───────────────────────────────────►│                             │
│      │                                    │                             │
│      │ 2. Send Messages                   │                             │
│      ├───────────────────────────────────►│                             │
│      │                                    │                             │
│      │ 3. Commit Transaction              │                             │
│      ├───────────────────────────────────►│                             │
│      │                                    │                             │
│      │                                    │  Messages visible atomically│
│      │                                    │                             │
│                                                                         │
│   Consumer: read_committed isolation                                    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### Dead Letter Queues (DLQ)
- [ ] Understand DLQ pattern
- [ ] Know error handling

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Dead Letter Queue Pattern                                               │
│                                                                         │
│   ┌──────────┐     ┌──────────────┐     ┌──────────────┐               │
│   │ Producer │────►│  Main Queue  │────►│   Consumer   │               │
│   └──────────┘     └──────────────┘     └──────┬───────┘               │
│                                                 │                       │
│                                                 │ Process Failed        │
│                                                 │ (3 retries)           │
│                                                 ▼                       │
│                                          ┌──────────────┐               │
│                                          │  Dead Letter │               │
│                                          │    Queue     │               │
│                                          └──────┬───────┘               │
│                                                 │                       │
│                                                 │                       │
│                               ┌─────────────────┼─────────────────┐     │
│                               │                 │                 │     │
│                               ▼                 ▼                 ▼     │
│                          ┌─────────┐     ┌───────────┐     ┌─────────┐ │
│                          │ Alert   │     │  Manual   │     │  Auto   │ │
│                          │ (PagerD)│     │  Review   │     │ Retry   │ │
│                          └─────────┘     └───────────┘     └─────────┘ │
│                                                                         │
│   DLQ Contents:                                                        │
│   - Original message                                                   │
│   - Error information                                                  │
│   - Retry count                                                        │
│   - Timestamp                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Kafka vs RabbitMQ

| Feature | Kafka | RabbitMQ |
|---------|-------|----------|
| **Primary Use** | Event streaming | Message queue |
| **Message Order** | Per partition | Per queue |
| **Persistence** | Long-term | Short-term |
| **Throughput** | Very high (millions/sec) | High (10K-100K/sec) |
| **Delivery** | Pull | Push |
| **Replay** | Yes (offset seek) | No |
| **Protocol** | Binary | AMQP |
| **Best For** | Event sourcing, logs | Task queues, RPC |

---

## 🎯 Practice Task

### Design Messaging Architecture

**Instructions:**
1. Design messaging for an order processing system
2. Include: Order Service, Payment, Inventory, Notification
3. Handle failures with DLQ
4. Ensure idempotency

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] [Kafka Documentation](https://kafka.apache.org/documentation/)
- [ ] [RabbitMQ Tutorials](https://www.rabbitmq.com/getstarted.html)
- [ ] Designing Data-Intensive Applications - Ch. 11

---

## ✅ Completion Checklist

- [ ] Understood Kafka architecture
- [ ] Know RabbitMQ exchange types
- [ ] Mastered Pub/Sub pattern
- [ ] Know idempotency patterns
- [ ] Understand exactly-once delivery
- [ ] Know DLQ pattern

**Date Completed:** _____________
