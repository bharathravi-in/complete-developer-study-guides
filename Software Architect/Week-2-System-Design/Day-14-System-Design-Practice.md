# Day 14: System Design Practice

## Status: ⬜ Not Started

---

## 📚 Practice Problems

### 1. URL Shortener (Like bit.ly)

**Requirements:**
- Shorten long URLs to short codes
- Redirect short URLs to original
- Analytics (click count)
- Expiration support

**Estimated Scale:**
- 100M URLs created/month
- 10:1 read/write ratio
- 7 years storage

```
┌─────────────────────────────────────────────────────────────────────────┐
│  URL Shortener Architecture                                              │
│                                                                         │
│                           ┌─────────────────┐                           │
│    Users ────────────────►│    CDN / DNS    │                           │
│                           └────────┬────────┘                           │
│                                    │                                    │
│                           ┌────────▼────────┐                           │
│                           │  Load Balancer  │                           │
│                           └────────┬────────┘                           │
│                                    │                                    │
│              ┌─────────────────────┼─────────────────────┐              │
│              │                     │                     │              │
│              ▼                     ▼                     ▼              │
│       ┌──────────────┐      ┌──────────────┐      ┌──────────────┐     │
│       │  API Server  │      │  API Server  │      │  API Server  │     │
│       └──────┬───────┘      └──────┬───────┘      └──────┬───────┘     │
│              │                     │                     │              │
│              └─────────────────────┼─────────────────────┘              │
│                                    │                                    │
│                    ┌───────────────┼───────────────┐                    │
│                    │               │               │                    │
│                    ▼               ▼               ▼                    │
│             ┌──────────┐    ┌──────────┐    ┌──────────┐               │
│             │  Cache   │    │ Database │    │ Analytics│               │
│             │ (Redis)  │    │(Cassandra)│   │ (Kafka)  │               │
│             └──────────┘    └──────────┘    └──────────┘               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Design Decisions:**

| Component | Choice | Reason |
|-----------|--------|--------|
| **ID Generation** | Base62 encoding | Short strings, URL safe |
| **Database** | Cassandra | High write throughput, horizontal scale |
| **Cache** | Redis | Fast lookups for popular URLs |
| **Counter** | Snowflake ID | Distributed unique IDs |

**API Design:**
```
POST /api/shorten
Body: { "url": "https://example.com/very/long/url" }
Response: { "shortUrl": "https://short.ly/abc123" }

GET /{shortCode}
Response: 301 Redirect to original URL
```

---

### 2. Netflix-like Streaming System

**Requirements:**
- Video upload and storage
- Adaptive streaming
- Global delivery
- Personalized recommendations
- 200M subscribers

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Video Streaming Architecture                                            │
│                                                                         │
│        Upload Pipeline                      Streaming Pipeline          │
│                                                                         │
│  ┌─────────────┐                                     ┌──────────────┐   │
│  │   Content   │                                     │    Users     │   │
│  │   Creator   │                                     │  (Viewers)   │   │
│  └──────┬──────┘                                     └──────┬───────┘   │
│         │                                                   │           │
│         ▼                                                   ▼           │
│  ┌──────────────┐                                   ┌──────────────┐   │
│  │ Upload API   │                                   │     CDN      │   │
│  │              │                                   │   (Global)   │   │
│  └──────┬───────┘                                   └──────┬───────┘   │
│         │                                                   │           │
│         ▼                                                   │           │
│  ┌──────────────┐     ┌──────────────────────────────────┐ │           │
│  │  Raw Video   │     │        Origin Storage            │◄┘           │
│  │   Storage    │────►│   (S3 / Object Storage)         │             │
│  │   (S3)       │     │                                  │             │
│  └──────┬───────┘     └──────────────────────────────────┘             │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Video Processing Pipeline                      │  │
│  │                                                                  │  │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │  │
│  │  │Transcode│───►│ Encode  │───►│Thumbnail│───►│ Package │      │  │
│  │  │         │    │Multiple │    │Generate │    │HLS/DASH │      │  │
│  │  │         │    │Qualities│    │         │    │         │      │  │
│  │  └─────────┘    └─────────┘    └─────────┘    └─────────┘      │  │
│  │                                                                  │  │
│  │  Outputs: 240p, 480p, 720p, 1080p, 4K                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    Microservices                                  │  │
│  │                                                                  │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │  │
│  │  │  User   │ │ Content │ │ Search  │ │Recommend│ │ Billing │  │  │
│  │  │ Service │ │ Catalog │ │ Service │ │ Engine  │ │ Service │  │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘  │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Components:**

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Video Processing** | FFmpeg, AWS MediaConvert | Transcode to multiple formats |
| **Storage** | S3 | Store video chunks |
| **CDN** | CloudFront, Akamai | Global delivery |
| **Streaming** | HLS/DASH | Adaptive bitrate |
| **Recommendations** | ML/Spark | Personalization |

**Adaptive Bitrate Streaming:**
```
Client bandwidth detection:
- Low network  → 480p stream
- Medium      → 720p stream
- High        → 1080p/4K stream

Seamless quality switching during playback
```

---

### 3. E-Commerce Platform

**Requirements:**
- Product catalog
- Shopping cart
- Order processing
- Payment integration
- Inventory management
- 10M daily active users

```
┌─────────────────────────────────────────────────────────────────────────┐
│  E-Commerce Architecture                                                 │
│                                                                         │
│                           ┌─────────────────┐                           │
│    Web/Mobile ───────────►│   API Gateway   │                           │
│                           └────────┬────────┘                           │
│                                    │                                    │
│       ┌────────────────────────────┼────────────────────────────┐       │
│       │                            │                            │       │
│       ▼                            ▼                            ▼       │
│ ┌───────────┐              ┌───────────┐              ┌───────────┐    │
│ │   User    │              │  Product  │              │   Order   │    │
│ │  Service  │              │  Service  │              │  Service  │    │
│ └─────┬─────┘              └─────┬─────┘              └─────┬─────┘    │
│       │                          │                          │          │
│       ▼                          ▼                          ▼          │
│ ┌───────────┐              ┌───────────┐              ┌───────────┐    │
│ │PostgreSQL │              │ MongoDB   │              │PostgreSQL │    │
│ └───────────┘              └───────────┘              └───────────┘    │
│                                                                         │
│       ┌────────────────────────────┼────────────────────────────┐       │
│       │                            │                            │       │
│       ▼                            ▼                            ▼       │
│ ┌───────────┐              ┌───────────┐              ┌───────────┐    │
│ │   Cart    │              │  Payment  │              │ Inventory │    │
│ │  Service  │              │  Service  │              │  Service  │    │
│ └─────┬─────┘              └─────┬─────┘              └─────┬─────┘    │
│       │                          │                          │          │
│       ▼                          ▼                          ▼          │
│ ┌───────────┐              ┌───────────┐              ┌───────────┐    │
│ │   Redis   │              │  Stripe   │              │PostgreSQL │    │
│ │           │              │  Gateway  │              │   +Redis  │    │
│ └───────────┘              └───────────┘              └───────────┘    │
│                                                                         │
│                    ┌─────────────────────────┐                          │
│                    │     Message Broker      │                          │
│                    │        (Kafka)          │                          │
│                    └─────────────────────────┘                          │
│                                │                                        │
│       ┌────────────────────────┼────────────────────────────┐          │
│       │                        │                            │          │
│       ▼                        ▼                            ▼          │
│ ┌───────────┐           ┌───────────┐              ┌───────────┐       │
│ │Notification│          │  Search   │              │ Analytics │       │
│ │  Service  │           │(Elastic)  │              │  Service  │       │
│ └───────────┘           └───────────┘              └───────────┘       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Order Flow:**

```
1. Add to Cart
   User → Cart Service → Redis (TTL 7 days)

2. Checkout
   Cart → Order Service → Reserve Inventory → Payment Service

3. Payment
   Payment Service → Stripe → Webhook → Update Order Status

4. Publish Events
   Order Created → Kafka → Multiple Consumers
                         ├── Inventory (decrement)
                         ├── Notification (email/SMS)
                         ├── Analytics (tracking)
                         └── Search (update availability)
```

**Key Design Decisions:**

| Aspect | Decision | Reason |
|--------|----------|--------|
| **Cart Storage** | Redis | Fast, TTL support |
| **Product Catalog** | MongoDB | Flexible schema |
| **Orders** | PostgreSQL | ACID transactions |
| **Search** | Elasticsearch | Full-text search |
| **Inventory** | Redis + DB | Fast reads, consistent writes |

---

## 🎯 Practice Template

### System Design Interview Template

```markdown
## 1. Requirements Clarification (5 min)
### Functional Requirements
- What features are must-have?
- What is the core user flow?

### Non-Functional Requirements
- Scale: How many users? DAU/MAU?
- Performance: Latency requirements?
- Availability: SLA?
- Consistency: Strong or eventual?

## 2. Back-of-Envelope Estimation (5 min)
### Traffic
- Reads/sec:
- Writes/sec:
- Peak traffic:

### Storage
- Data per record:
- Total storage (5 years):
- Bandwidth:

## 3. High-Level Design (10 min)
[Draw architecture diagram]

### Key Components
- API Layer
- Service Layer
- Data Layer
- Caching

## 4. Deep Dive (15 min)
### Database Schema
[Design tables/collections]

### API Design
[Define key endpoints]

### Core Algorithms
[Describe key algorithms]

## 5. Scale & Optimization (5 min)
### Bottlenecks
- Identify bottlenecks

### Solutions
- Caching
- Sharding
- CDN
- Async processing

## 6. Monitoring & Failure Handling
### Metrics
- Key metrics to track

### Failure Scenarios
- How to handle failures
```

---

## 🏆 Challenge Yourself

### Additional Problems to Practice:

1. **Design Twitter**
   - Timeline generation
   - Fan-out on write vs read
   - Trending topics

2. **Design WhatsApp**
   - Real-time messaging
   - Group chats
   - Read receipts

3. **Design Google Drive**
   - File storage
   - Sync across devices
   - Sharing

4. **Design Uber**
   - Real-time location
   - Matching algorithm
   - Surge pricing

---

## 📝 Notes

*Add your notes here during practice*

---

## 📖 Resources

- [ ] [System Design Primer](https://github.com/donnemartin/system-design-primer)
- [ ] [Grokking System Design](https://www.educative.io/courses/grokking-the-system-design-interview)
- [ ] [ByteByteGo Newsletter](https://blog.bytebytego.com/)

---

## ✅ Week 2 Summary

After completing Week 2, you should be able to:

- [ ] Design scalable systems
- [ ] Choose appropriate databases
- [ ] Implement caching strategies
- [ ] Design messaging systems
- [ ] Ensure high availability
- [ ] Complete system design interviews

**Date Completed:** _____________
