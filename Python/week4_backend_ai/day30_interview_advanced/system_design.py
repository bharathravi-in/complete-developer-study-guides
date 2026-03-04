#!/usr/bin/env python3
"""Day 30 - System Design Interview Questions"""

print("=" * 60)
print("SYSTEM DESIGN INTERVIEW QUESTIONS")
print("=" * 60)


# ============================================
# QUESTION 1: DESIGN URL SHORTENER
# ============================================
print("\n" + "=" * 60)
print("Q1: DESIGN URL SHORTENER (like bit.ly)")
print("=" * 60)

URL_SHORTENER = """
Requirements:
─────────────
- Shorten long URLs to short codes
- Redirect short URL to original
- Analytics (optional)
- Scale: 100M URLs/month, 100:1 read/write

API Design:
───────────
POST /shorten
  Request: { "url": "https://example.com/very/long/path" }
  Response: { "short_url": "https://short.ly/abc123" }

GET /{short_code}
  Response: 301 Redirect to original URL

High-Level Design:
──────────────────
Client → Load Balancer → App Servers → Cache (Redis) → Database

Key Decisions:
──────────────
1. Short Code Generation:
   - Base62 encoding (a-z, A-Z, 0-9)
   - 7 characters = 62^7 = 3.5 trillion unique URLs
   
2. Database:
   - NoSQL (Cassandra) for high write throughput
   - Or SQL with sharding by short_code hash

3. Unique ID Generation:
   - Twitter Snowflake (timestamp + machine ID + sequence)
   - Or counter service with distributed counters

Scaling:
────────
- Cache popular URLs (80/20 rule)
- Database sharding (range-based or hash-based)
- Read replicas for analytics queries
- CDN for global latency

Data Estimation:
────────────────
- 100M URLs/month = ~40 URLs/second
- Read: 4000 requests/second
- Storage: 100M × 500 bytes = 50 GB/month
- 5 years: 3 TB
"""
print(URL_SHORTENER)


# ============================================
# QUESTION 2: DESIGN TWITTER FEED
# ============================================
print("\n" + "=" * 60)
print("Q2: DESIGN TWITTER FEED")
print("=" * 60)

TWITTER_FEED = """
Requirements:
─────────────
- Post tweets (text, images)
- Follow/unfollow users
- View home feed (tweets from followed users)
- Scale: 500M users, 200M DAU

API Design:
───────────
POST /tweets       - Create tweet
GET  /feed         - Get home timeline
POST /follow/{id}  - Follow user
GET  /user/{id}    - Get user profile

Two Approaches:
───────────────
1. Pull Model (Fan-out on read):
   - Store tweets by user_id
   - On feed request, query all followed users' tweets
   - Merge and sort
   - Pros: Simple writes
   - Cons: Slow reads for users following many people

2. Push Model (Fan-out on write):
   - Maintain feed cache for each user
   - On new tweet, push to all followers' feeds
   - Pros: Fast reads
   - Cons: Slow writes, storage heavy for celebrities

3. Hybrid (Recommended):
   - Push for regular users
   - Pull for celebrities (>10K followers)
   - Merge at read time

Architecture:
─────────────
User → API Gateway → Tweet Service → Tweet DB (writes)
                  → Feed Service → Feed Cache (reads)
                  → Fan-out Service → Message Queue → Workers

Database Schema:
────────────────
tweets (id, user_id, content, media_urls[], created_at)
users (id, name, follower_count)
follows (follower_id, followee_id, created_at)
feed_cache (user_id, tweet_ids[], last_updated)
"""
print(TWITTER_FEED)


# ============================================
# QUESTION 3: DESIGN RATE LIMITER
# ============================================
print("\n" + "=" * 60)
print("Q3: DESIGN RATE LIMITER")
print("=" * 60)

RATE_LIMITER = """
Requirements:
─────────────
- Limit API requests per user/IP
- Different limits for different endpoints
- Distributed (multiple servers)
- Low latency

Algorithms:
───────────
1. Token Bucket:
   - Bucket holds tokens, refilled at constant rate
   - Request takes a token
   - Allows bursts

2. Sliding Window Counter:
   - Count requests in rolling time window
   - More accurate than fixed window

Implementation (Redis):
───────────────────────
def is_allowed(user_id, limit=100, window=60):
    key = f"rate:{user_id}"
    now = time.time()
    
    # Remove old entries
    redis.zremrangebyscore(key, 0, now - window)
    
    # Count current window
    count = redis.zcard(key)
    
    if count < limit:
        redis.zadd(key, {str(now): now})
        redis.expire(key, window)
        return True
    return False

Architecture:
─────────────
Client → API Gateway (check limit) → Rate Limiter (Redis) → App

Distributed:
────────────
- Centralized Redis cluster
- Each API server queries Redis
- Or local + sync (eventually consistent)

Response Headers:
─────────────────
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1609459200
"""
print(RATE_LIMITER)


# ============================================
# QUESTION 4: DESIGN CHAT SYSTEM
# ============================================
print("\n" + "=" * 60)
print("Q4: DESIGN CHAT SYSTEM (like WhatsApp)")
print("=" * 60)

CHAT_SYSTEM = """
Requirements:
─────────────
- 1:1 messaging
- Group chat (up to 500 members)
- Online/offline status
- Read receipts
- Message history
- Scale: 100M+ messages/day

Protocol:
─────────
- WebSocket for real-time messaging
- HTTP fallback
- Long polling as backup

Architecture:
─────────────
Clients ←WebSocket→ Chat Servers ←→ Message Queue ←→ DB

Message Flow:
─────────────
1. User A sends message via WebSocket
2. Chat server validates, assigns message ID
3. Store in message queue (Kafka)
4. Worker stores in database
5. If User B online: push via WebSocket
6. If offline: push notification

Database Design:
────────────────
# Messages (Cassandra - partitioned by chat_id)
messages (
    chat_id,        # Partition key
    message_id,     # Clustering key (time-based UUID)
    sender_id,
    content,
    type,
    created_at
)

# User chats (for inbox)
user_chats (
    user_id,
    chat_id,
    last_message_at,
    unread_count
)

Presence System:
────────────────
- Heartbeat to Redis every 30 seconds
- Subscribe to presence updates via pub/sub
- Handle disconnect (timeout after 2x heartbeat)

Scaling:
────────
- WebSocket servers: Horizontal with sticky sessions
- Message DB: Partition by chat_id
- Hot chats: Cache recent messages
"""
print(CHAT_SYSTEM)


# ============================================
# QUESTION 5: DESIGN NOTIFICATION SYSTEM
# ============================================
print("\n" + "=" * 60)
print("Q5: DESIGN NOTIFICATION SYSTEM")
print("=" * 60)

NOTIFICATION = """
Requirements:
─────────────
- Push notifications (iOS, Android)
- Email notifications
- SMS notifications
- In-app notifications
- User preferences
- Scheduled notifications

Architecture:
─────────────
Services → Event Bus → Notification Service → Providers

Components:
───────────
1. API Gateway: Receive notification requests
2. Validation Service: Check user preferences
3. Template Service: Render messages
4. Priority Queue: Urgent vs batch
5. Rate Limiter: Prevent spam
6. Workers: Send to providers
7. Retry Queue: Handle failures

Database:
─────────
notifications (
    id, user_id, type, channel,
    title, body, data,
    status, retry_count,
    scheduled_at, sent_at
)

user_preferences (
    user_id, channel, enabled,
    quiet_hours_start, quiet_hours_end
)

Reliability:
────────────
- Exactly-once delivery (idempotency keys)
- Retry with exponential backoff
- Dead letter queue for failures
- Monitoring and alerting
"""
print(NOTIFICATION)


# ============================================
# INTERVIEW FRAMEWORK
# ============================================
print("\n" + "=" * 60)
print("SYSTEM DESIGN INTERVIEW FRAMEWORK")
print("=" * 60)
print("""
Step 1: Clarify Requirements (3-5 min)
──────────────────────────────────────
- Functional: What features?
- Non-functional: Scale, latency, availability?
- Constraints: Budget, timeline?

Step 2: Estimate Scale (3-5 min)
────────────────────────────────
- Users (DAU/MAU)
- Read/Write ratio
- Data size
- QPS (queries per second)

Step 3: High-Level Design (10-15 min)
─────────────────────────────────────
- Draw main components
- Data flow
- API design

Step 4: Deep Dive (15-20 min)
─────────────────────────────
- Pick 2-3 components
- Database schema
- Algorithms
- Trade-offs

Step 5: Wrap Up (3-5 min)
─────────────────────────
- Bottlenecks
- Future improvements
- Error handling
- Monitoring

Key Principles:
───────────────
- No single point of failure
- Horizontal scalability
- Cache aggressively
- Async when possible
- Monitor everything
""")
