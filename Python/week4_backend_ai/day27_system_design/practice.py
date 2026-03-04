#!/usr/bin/env python3
"""Day 27 - System Design Fundamentals"""

print("=" * 60)
print("SYSTEM DESIGN FUNDAMENTALS")
print("=" * 60)


# ============================================
# 1. SCALABILITY CONCEPTS
# ============================================
print("\n--- 1. Scalability Concepts ---")

SCALABILITY = """
Vertical Scaling (Scale Up)
───────────────────────────
├─ Add more CPU/RAM/Storage to existing server
├─ Pros: Simple, no code changes
├─ Cons: Hardware limits, single point of failure
└─ Use case: Databases, legacy apps

Horizontal Scaling (Scale Out)
──────────────────────────────
├─ Add more servers
├─ Pros: Virtually unlimited, fault tolerant
├─ Cons: Complexity, data consistency
└─ Use case: Web servers, stateless services

Key Metrics:
─────────────
├─ Throughput: Requests per second (RPS)
├─ Latency: Response time (p50, p95, p99)
├─ Availability: Uptime percentage (99.9% = 8.76 hours/year downtime)
└─ Consistency: Data accuracy across replicas
"""
print(SCALABILITY)


# ============================================
# 2. LOAD BALANCING
# ============================================
print("\n--- 2. Load Balancing ---")

LOAD_BALANCING = """
Load Balancer Algorithms:
─────────────────────────
1. Round Robin
   - Requests distributed sequentially
   - Simple but doesn't consider server load

2. Weighted Round Robin
   - Servers assigned weights
   - More powerful servers get more requests

3. Least Connections
   - Route to server with fewest connections
   - Good for varying request durations

4. IP Hash
   - Route based on client IP
   - Ensures session persistence

5. Least Response Time
   - Route to fastest responding server
   - Requires health checks

Architecture:
─────────────
              ┌─────────────┐
              │   Client    │
              └─────┬───────┘
                    │
              ┌─────▼───────┐
              │Load Balancer │
              └─────┬───────┘
        ┌───────────┼───────────┐
        │           │           │
   ┌────▼────┐ ┌────▼────┐ ┌────▼────┐
   │ Server1 │ │ Server2 │ │ Server3 │
   └─────────┘ └─────────┘ └─────────┘
"""
print(LOAD_BALANCING)


# ============================================
# 3. CACHING STRATEGIES
# ============================================
print("\n--- 3. Caching Strategies ---")

CACHING = """
Cache Layers:
─────────────
1. Browser Cache (Client-side)
2. CDN Cache (Edge servers)
3. Application Cache (Redis/Memcached)
4. Database Cache (Query cache)

Caching Patterns:
─────────────────
1. Cache-Aside (Lazy Loading)
   ┌─ App checks cache first
   ├─ If miss, load from DB
   └─ Store in cache for next time

2. Read-Through
   ┌─ Cache sits between app and DB
   └─ Cache handles loading from DB

3. Write-Through
   ┌─ Write to cache and DB simultaneously
   └─ Strong consistency, slower writes

4. Write-Behind (Write-Back)
   ┌─ Write to cache only
   ├─ Async write to DB later
   └─ Faster writes, risk of data loss

5. Refresh-Ahead
   ┌─ Proactively refresh before expiry
   └─ Reduces cache misses

Cache Eviction Policies:
────────────────────────
├─ LRU: Least Recently Used
├─ LFU: Least Frequently Used
├─ FIFO: First In, First Out
└─ TTL: Time To Live
"""
print(CACHING)


# ============================================
# 4. DATABASE DESIGN
# ============================================
print("\n--- 4. Database Design ---")

DATABASE = """
SQL vs NoSQL:
─────────────
SQL (Relational)
├─ ACID transactions
├─ Complex queries, joins
├─ Structured data
├─ Examples: PostgreSQL, MySQL
└─ Use: Banking, e-commerce

NoSQL (Non-relational)
├─ Document: MongoDB, CouchDB
├─ Key-Value: Redis, DynamoDB
├─ Column: Cassandra, HBase
├─ Graph: Neo4j, Neptune
└─ Use: Flexible schemas, high scale

Database Scaling:
─────────────────
1. Read Replicas
   ├─ Master handles writes
   └─ Replicas handle reads

2. Sharding (Horizontal Partitioning)
   ├─ Split data across servers
   ├─ By key range or hash
   └─ Complexity in joins

3. Vertical Partitioning
   ├─ Split tables by columns
   └─ Reduces row size

4. Denormalization
   ├─ Duplicate data for faster reads
   └─ Trade consistency for performance
"""
print(DATABASE)


# ============================================
# 5. MESSAGE QUEUES
# ============================================
print("\n--- 5. Message Queues ---")

QUEUES = """
Use Cases:
──────────
├─ Async processing: Send email, process image
├─ Decoupling: Independent scaling
├─ Load leveling: Handle traffic spikes
└─ Event sourcing: Audit trail

Message Queue Patterns:
───────────────────────
1. Point-to-Point (Queue)
   Producer → Queue → Consumer
   - One consumer processes each message
   
2. Pub/Sub (Topic)
   Publisher → Topic → Multiple Subscribers
   - All subscribers receive all messages

3. Request-Reply
   Request Queue ←→ Reply Queue
   - Async request-response

Popular Solutions:
──────────────────
├─ RabbitMQ: Feature-rich, AMQP
├─ Apache Kafka: High throughput, event streaming
├─ Redis Pub/Sub: Simple, fast
├─ AWS SQS: Managed, serverless
└─ Celery: Python task queue

Architecture:
─────────────
┌─────────┐    ┌─────────┐    ┌──────────┐
│ API     │───▶│  Queue  │───▶│ Worker   │
│ Server  │    │ (Redis) │    │ (Celery) │
└─────────┘    └─────────┘    └──────────┘
"""
print(QUEUES)


# ============================================
# 6. MICROSERVICES
# ============================================
print("\n--- 6. Microservices Architecture ---")

MICROSERVICES = """
Monolith vs Microservices:
──────────────────────────
Monolith:
├─ Single codebase
├─ Simple deployment
├─ Hard to scale parts
└─ Tech stack locked

Microservices:
├─ Independent services
├─ Independent deployment
├─ Scale individually
├─ Polyglot (different languages)
└─ Complexity overhead

Key Components:
───────────────
1. API Gateway
   - Single entry point
   - Routing, auth, rate limiting

2. Service Discovery
   - Find service instances
   - Consul, Kubernetes DNS

3. Load Balancer
   - Distribute traffic
   - Health checks

4. Circuit Breaker
   - Prevent cascade failures
   - Fallback behavior

5. Config Server
   - Centralized configuration
   - Environment-specific

Architecture:
─────────────
           ┌─────────────┐
           │ API Gateway │
           └──────┬──────┘
      ┌───────────┼───────────┐
      │           │           │
┌─────▼─────┐┌────▼────┐┌─────▼─────┐
│   User    ││  Order  ││  Payment  │
│  Service  ││ Service ││  Service  │
└───────────┘└─────────┘└───────────┘
      │           │           │
      └───────────┴───────────┘
              │
         ┌────▼────┐
         │  Event  │
         │   Bus   │
         └─────────┘
"""
print(MICROSERVICES)


# ============================================
# 7. CAP THEOREM
# ============================================
print("\n--- 7. CAP Theorem ---")

CAP = """
CAP Theorem: Pick 2 of 3
────────────────────────

     Consistency
         /\\
        /  \\
       /    \\
      /      \\
     /   CP   \\
    /          \\
   Availability─Partition Tolerance
          AP

Consistency: All nodes see same data
Availability: Every request gets a response
Partition Tolerance: System works despite network failures

Trade-offs:
───────────
CA (Consistency + Availability)
├─ Single node systems
└─ Not suitable for distributed systems

CP (Consistency + Partition Tolerance)
├─ Examples: MongoDB, HBase
└─ May reject requests during partitions

AP (Availability + Partition Tolerance)
├─ Examples: Cassandra, DynamoDB
└─ May return stale data

In Practice:
────────────
Most distributed systems must handle partitions,
so choose between CP and AP based on requirements.
"""
print(CAP)


# ============================================
# 8. DESIGN PROCESS
# ============================================
print("\n--- 8. System Design Process ---")

PROCESS = """
Step 1: Clarify Requirements (5 min)
────────────────────────────────────
├─ Functional: What should it do?
├─ Non-functional: Scale, latency, availability?
├─ Users: Who uses it? How many?
└─ Constraints: Budget, timeline, tech?

Step 2: Estimate Scale (5 min)
──────────────────────────────
├─ DAU/MAU (Daily/Monthly Active Users)
├─ Read/Write ratio
├─ Data size and growth
├─ Traffic patterns (peaks?)
└─ Storage requirements

Step 3: Design API (5 min)
──────────────────────────
├─ Define endpoints
├─ Request/Response format
└─ Rate limits

Step 4: High-Level Design (10 min)
──────────────────────────────────
├─ Draw main components
├─ Data flow
├─ API → Service → Database
└─ External services

Step 5: Deep Dive (15 min)
──────────────────────────
├─ Database schema
├─ Algorithms
├─ Specific challenges
└─ Trade-offs

Step 6: Identify Bottlenecks (5 min)
────────────────────────────────────
├─ Single points of failure
├─ Potential hotspots
└─ Scaling solutions
"""
print(PROCESS)


# ============================================
# 9. CAPACITY ESTIMATION
# ============================================
print("\n--- 9. Capacity Estimation ---")

def estimate_capacity():
    """Example capacity estimation."""
    print("Example: URL Shortener")
    print("-" * 40)
    
    # Assumptions
    new_urls_per_month = 500_000_000  # 500M
    read_write_ratio = 100  # 100:1
    avg_url_length = 100  # bytes
    hash_length = 7  # bytes
    
    # Write calculations
    writes_per_second = new_urls_per_month / (30 * 24 * 3600)
    reads_per_second = writes_per_second * read_write_ratio
    
    print(f"New URLs/month: {new_urls_per_month:,}")
    print(f"Writes/second: {writes_per_second:.0f}")
    print(f"Reads/second: {reads_per_second:,.0f}")
    
    # Storage calculations
    record_size = avg_url_length + hash_length + 50  # metadata
    storage_per_month = new_urls_per_month * record_size
    storage_5_years = storage_per_month * 60
    
    print(f"\nStorage/month: {storage_per_month / 1e9:.1f} GB")
    print(f"Storage (5 years): {storage_5_years / 1e12:.1f} TB")
    
    # Bandwidth
    write_bandwidth = writes_per_second * record_size
    read_bandwidth = reads_per_second * hash_length
    
    print(f"\nWrite bandwidth: {write_bandwidth / 1e6:.2f} MB/s")
    print(f"Read bandwidth: {read_bandwidth / 1e6:.2f} MB/s")

estimate_capacity()


# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 60)
print("SYSTEM DESIGN CHECKLIST")
print("=" * 60)
print("""
Requirements:
  □ Functional requirements
  □ Non-functional requirements (scale, latency)
  □ Capacity estimation

High-Level Components:
  □ Load balancer
  □ Web/App servers
  □ Database (SQL/NoSQL)
  □ Cache layer
  □ Message queue
  □ CDN

Data Design:
  □ Database schema
  □ Indexing strategy
  □ Sharding approach
  □ Replication

Reliability:
  □ Redundancy (no SPOF)
  □ Health checks
  □ Graceful degradation
  □ Monitoring & alerting

Security:
  □ Authentication/Authorization
  □ Encryption (transit/rest)
  □ Rate limiting
  □ Input validation
""")
