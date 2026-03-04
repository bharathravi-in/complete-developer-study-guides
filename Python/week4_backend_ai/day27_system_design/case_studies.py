#!/usr/bin/env python3
"""Day 27 - System Design Case Studies"""

print("=" * 60)
print("SYSTEM DESIGN CASE STUDIES")
print("=" * 60)


# ============================================
# CASE STUDY 1: URL SHORTENER
# ============================================
print("\n" + "=" * 60)
print("CASE STUDY 1: URL SHORTENER (like bit.ly)")
print("=" * 60)

URL_SHORTENER = """
Requirements:
─────────────
Functional:
  - Create short URL from long URL
  - Redirect short URL to original
  - Custom aliases (optional)
  - Expiration (optional)
  - Analytics (optional)

Non-functional:
  - 100M URLs created/month
  - 100:1 read/write ratio
  - URL should be as short as possible
  - Low latency redirects

Design:
───────
1. Short URL Generation
   - Base62 encoding (a-z, A-Z, 0-9)
   - 7 characters = 62^7 = 3.5 trillion combinations
   
2. Database Schema
   ┌──────────────────────────────────┐
   │ urls                             │
   ├──────────────────────────────────┤
   │ short_code: VARCHAR(7) PK        │
   │ original_url: VARCHAR(2048)      │
   │ user_id: INT (nullable)          │
   │ created_at: TIMESTAMP            │
   │ expires_at: TIMESTAMP (nullable) │
   │ click_count: INT DEFAULT 0       │
   └──────────────────────────────────┘

3. Architecture
   ┌──────────┐    ┌─────────────┐    ┌──────────┐
   │  Client  │───▶│ Load Balancer│───▶│ App Tier │
   └──────────┘    └─────────────┘    └────┬─────┘
                                           │
                 ┌─────────────────────────┼───────────┐
                 │                         │           │
            ┌────▼────┐              ┌─────▼───┐  ┌────▼────┐
            │  Cache  │              │ Counter │  │Analytics│
            │ (Redis) │              │ Service │  │  Queue  │
            └────┬────┘              └─────────┘  └─────────┘
                 │
            ┌────▼────┐
            │Database │
            │(Sharded)│
            └─────────┘

4. Key Algorithms
   
   # Base62 encoding
   CHARSET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
   
   def encode(num):
       result = []
       while num > 0:
           result.append(CHARSET[num % 62])
           num //= 62
       return ''.join(reversed(result))
   
   def decode(s):
       num = 0
       for char in s:
           num = num * 62 + CHARSET.index(char)
       return num

5. Scaling Considerations
   - Cache popular URLs in Redis
   - Database sharding by hash of short_code
   - Counter service for unique ID generation
   - CDN for global distribution
"""
print(URL_SHORTENER)


# ============================================
# CASE STUDY 2: RATE LIMITER
# ============================================
print("\n" + "=" * 60)
print("CASE STUDY 2: RATE LIMITER")
print("=" * 60)

RATE_LIMITER = """
Requirements:
─────────────
Functional:
  - Limit requests per user/IP
  - Different limits for different endpoints
  - Return appropriate error when limited

Non-functional:
  - Low latency (< 1ms)
  - Distributed across servers
  - Accurate counting

Algorithms:
───────────
1. Token Bucket
   - Bucket fills with tokens at fixed rate
   - Request consumes token
   - If no tokens, request denied
   - Pros: Allows bursts
   
2. Leaky Bucket
   - Requests enter bucket
   - Processed at fixed rate
   - Overflow is denied
   - Pros: Smooth output

3. Fixed Window Counter
   - Count requests in fixed time windows
   - Reset at window boundary
   - Cons: Edge case at boundaries

4. Sliding Window Log
   - Store timestamp of each request
   - Count requests in rolling window
   - Cons: Memory intensive

5. Sliding Window Counter
   - Combine fixed windows
   - Weighted average
   - Best balance

Implementation (Redis):
───────────────────────
import redis
import time

class RateLimiter:
    def __init__(self, redis_client, limit=100, window=60):
        self.redis = redis_client
        self.limit = limit      # requests
        self.window = window    # seconds
    
    def is_allowed(self, user_id):
        key = f"rate:{user_id}"
        current = int(time.time())
        
        pipe = self.redis.pipeline()
        
        # Remove old entries
        pipe.zremrangebyscore(key, 0, current - self.window)
        
        # Count current window
        pipe.zcard(key)
        
        # Add current request
        pipe.zadd(key, {str(current): current})
        
        # Set expiry
        pipe.expire(key, self.window)
        
        results = pipe.execute()
        request_count = results[1]
        
        return request_count < self.limit

Distributed Design:
───────────────────
        ┌─────────────┐
        │ API Gateway │
        └──────┬──────┘
               │
        ┌──────▼──────┐
        │Rate Limiter │
        │  (Redis)    │
        └──────┬──────┘
               │
     ┌─────────┼─────────┐
     │         │         │
┌────▼───┐┌────▼───┐┌────▼───┐
│Server 1││Server 2││Server 3│
└────────┘└────────┘└────────┘
"""
print(RATE_LIMITER)


# ============================================
# CASE STUDY 3: NOTIFICATION SYSTEM
# ============================================
print("\n" + "=" * 60)
print("CASE STUDY 3: NOTIFICATION SYSTEM")
print("=" * 60)

NOTIFICATION = """
Requirements:
─────────────
Functional:
  - Push notifications (mobile)
  - Email notifications
  - SMS notifications
  - In-app notifications
  - User preferences

Non-functional:
  - 10M notifications/day
  - Near real-time delivery
  - Retry failed deliveries
  - Analytics

Architecture:
─────────────
┌──────────────┐
│   Services   │ (Order, User, Payment, etc.)
└──────┬───────┘
       │ Events
┌──────▼───────┐
│ Message Queue │ (Kafka/RabbitMQ)
└──────┬───────┘
       │
┌──────▼───────────────────────────────────────┐
│            Notification Service              │
├──────────────────────────────────────────────┤
│  ┌─────────┐  ┌────────┐  ┌──────────────┐  │
│  │Priority │  │Template│  │ Preference   │  │
│  │ Router  │  │ Engine │  │   Manager    │  │
│  └────┬────┘  └───┬────┘  └──────────────┘  │
│       │           │                          │
│  ┌────▼───────────▼───────────────────────┐ │
│  │           Worker Pool                   │ │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────────┐  │ │
│  │  │Push │ │Email│ │ SMS │ │ In-App  │  │ │
│  │  └──┬──┘ └──┬──┘ └──┬──┘ └────┬────┘  │ │
│  └─────┼───────┼───────┼─────────┼───────┘ │
└────────┼───────┼───────┼─────────┼─────────┘
         │       │       │         │
    ┌────▼──┐┌───▼───┐┌──▼───┐┌────▼───┐
    │ APNs  ││Sendgrid││Twilio││ Redis  │
    │ FCM   ││  SES   ││      ││(WebSocket)│
    └───────┘└───────┘└──────┘└────────┘

Database Schema:
────────────────
┌───────────────────────────┐
│ notifications             │
├───────────────────────────┤
│ id: UUID PK               │
│ user_id: UUID FK          │
│ type: ENUM                │
│ channel: ENUM             │
│ title: VARCHAR            │
│ body: TEXT                │
│ data: JSONB               │
│ status: ENUM              │
│ retry_count: INT          │
│ scheduled_at: TIMESTAMP   │
│ sent_at: TIMESTAMP        │
│ created_at: TIMESTAMP     │
└───────────────────────────┘

┌───────────────────────────┐
│ user_preferences          │
├───────────────────────────┤
│ user_id: UUID PK          │
│ push_enabled: BOOLEAN     │
│ email_enabled: BOOLEAN    │
│ sms_enabled: BOOLEAN      │
│ quiet_hours_start: TIME   │
│ quiet_hours_end: TIME     │
│ frequency: ENUM           │
└───────────────────────────┘

Key Features:
─────────────
1. Priority Queue: Urgent vs batch
2. Template Engine: Personalization
3. Rate Limiting: Per user/channel
4. Retry with Backoff: Handle failures
5. Analytics: Open rates, click rates
"""
print(NOTIFICATION)


# ============================================
# CASE STUDY 4: CHAT APPLICATION
# ============================================
print("\n" + "=" * 60)
print("CASE STUDY 4: CHAT APPLICATION")
print("=" * 60)

CHAT_APP = """
Requirements:
─────────────
Functional:
  - 1:1 messaging
  - Group chats
  - Read receipts
  - Online status
  - Media sharing
  - Message history

Non-functional:
  - Real-time delivery (< 100ms)
  - 100M DAU
  - Offline support
  - End-to-end encryption

Architecture:
─────────────
┌───────────┐    ┌──────────────────┐
│  Client   │◀──▶│  WebSocket       │
│  (App)    │    │  Gateway         │
└───────────┘    └────────┬─────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
┌───────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
│    Chat       │ │   Presence    │ │    Media      │
│   Service     │ │   Service     │ │   Service     │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
┌───────▼───────┐ ┌───────▼───────┐ ┌───────▼───────┐
│  Message DB   │ │    Redis      │ │     S3        │
│ (Cassandra)   │ │  (Status)     │ │   (Media)     │
└───────────────┘ └───────────────┘ └───────────────┘

Message Flow:
─────────────
1. User A sends message
2. WebSocket server receives
3. Store in message DB
4. Find User B's WebSocket server
5. Send to User B (or queue if offline)
6. User B acknowledges
7. Update delivery status

Database Design:
────────────────
# Messages (Cassandra - time-series optimized)
messages (
    chat_id: UUID,           # Partition key
    message_id: TIMEUUID,    # Clustering key
    sender_id: UUID,
    content: TEXT,
    type: TEXT,
    created_at: TIMESTAMP
) PRIMARY KEY (chat_id, message_id)
  WITH CLUSTERING ORDER BY (message_id DESC)

# User chats (for inbox)
user_chats (
    user_id: UUID,
    chat_id: UUID,
    last_message_at: TIMESTAMP,
    unread_count: INT
) PRIMARY KEY (user_id, last_message_at)

Scaling Strategies:
───────────────────
1. WebSocket: Sticky sessions with consistent hashing
2. Message DB: Partition by chat_id
3. Presence: Redis cluster for online status
4. Media: CDN for image/video delivery
"""
print(CHAT_APP)


# ============================================
# DESIGN PATTERNS SUMMARY
# ============================================
print("\n" + "=" * 60)
print("COMMON DESIGN PATTERNS")
print("=" * 60)
print("""
1. Sharding
   └─ Distribute data across multiple databases
   
2. Replication
   └─ Master-slave for read scaling

3. Caching
   └─ Reduce database load

4. Message Queues
   └─ Async processing, decoupling

5. Load Balancing
   └─ Distribute traffic

6. Circuit Breaker
   └─ Prevent cascade failures

7. Event Sourcing
   └─ Store state as events

8. CQRS
   └─ Separate read/write models

9. Saga Pattern
   └─ Distributed transactions

10. API Gateway
    └─ Single entry point
""")
