# API Design Interview Questions — Senior / Staff Level

## Section 1: REST Fundamentals

### Q1: What are the 6 REST constraints?
**Answer**: (1) Client-Server separation, (2) Statelessness, (3) Cacheability, (4) Uniform Interface (resource identification, representations, self-descriptive messages, HATEOAS), (5) Layered System, (6) Code on Demand (optional).

### Q2: PUT vs PATCH — when to use each?
**Answer**: **PUT** replaces the entire resource (idempotent, must send all fields). **PATCH** partially updates specific fields (not necessarily idempotent). Use PUT when clients manage the complete resource state; use PATCH for field-level updates to reduce payload size.

### Q3: How do you handle API versioning?
**Answer**: Three main strategies:
- **URL path**: `/v1/users` → clearest, easiest caching, harder to maintain
- **Header**: `Accept: application/vnd.api+json;version=2` → clean URLs, harder to test
- **Query param**: `/users?version=2` → simple, pollutes cache keys

**Best practice**: URL versioning for major breaking changes. Use additive, non-breaking changes (new fields) without versioning when possible.

### Q4: How do you implement pagination?
**Answer**: Three approaches:
```
Offset: /users?page=2&limit=20
  ✅ Simple, jump to any page
  ❌ Inconsistent with inserts/deletes, slow for large offsets

Cursor: /users?cursor=eyJpZCI6MTIzfQ&limit=20
  ✅ Consistent, performant for any position
  ❌ Can't jump to arbitrary page

Keyset: /users?after_id=123&limit=20
  ✅ Most performant (uses index), consistent
  ❌ Only works with sortable unique columns
```

### Q5: Explain idempotency. Which HTTP methods are idempotent?
**Answer**: Idempotent = making the same request N times produces the same result. **GET, PUT, DELETE, HEAD, OPTIONS** are idempotent. **POST, PATCH** are NOT inherently idempotent. For non-idempotent operations (payments), use **idempotency keys**: client sends a unique key in the header; server deduplicates using that key.

## Section 2: HTTP & Status Codes

### Q6: When to use 401 vs 403?
**Answer**: **401 Unauthorized**: Authentication missing or invalid (no valid token). Client should re-authenticate. **403 Forbidden**: Authenticated but not authorized. Client's identity is known, but they lack permission. Don't use 403 if it would reveal hidden resources — use 404 instead.

### Q7: 400 vs 422 — what's the difference?
**Answer**: **400 Bad Request**: Malformed request — can't parse JSON, missing required header, wrong content type. **422 Unprocessable Entity**: Syntactically correct but semantically invalid — business rule violation (duplicate email, age out of range). Many APIs use 400 for both, but 422 is more precise for validation errors.

### Q8: Design an error response format for a production API.
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      { "field": "email", "message": "Already registered", "code": "DUPLICATE" }
    ],
    "requestId": "req_abc123",
    "documentation": "https://api.example.com/docs/errors"
  }
}
```
Key principles: machine-readable error codes, human-readable messages, field-level validation details, request ID for debugging, link to documentation.

## Section 3: GraphQL

### Q9: When would you choose GraphQL over REST?
**Answer**:
- **GraphQL**: Multiple clients needing different data shapes, deeply nested relationships, rapid frontend iteration, real-time features (subscriptions)
- **REST**: Simple CRUD, heavy HTTP caching needs, file uploads, public API for external consumers
- **Both**: BFF pattern — GraphQL gateway aggregating REST microservices

### Q10: How do you solve the N+1 problem in GraphQL?
**Answer**: Use **DataLoader** — it batches and caches database queries. Instead of N individual queries for each item's related data, DataLoader collects all IDs in a single tick of the event loop and makes one batch query: `SELECT * FROM posts WHERE author_id IN (1, 2, 3, ...)`.

### Q11: How do you prevent malicious queries in GraphQL?
**Answer**: (1) **Query depth limiting** — reject queries deeper than N levels, (2) **Query complexity analysis** — assign costs to fields, reject over budget, (3) **Persistent queries** — allowlist approved query hashes, (4) **Timeout** — kill long-running resolvers, (5) **Rate limiting** — per user/IP.

## Section 4: Authentication & Security

### Q12: JWT vs Session-based auth — trade-offs?
**Answer**:
| JWT | Sessions |
|-----|----------|
| Stateless, no server storage | Stateful, needs session store |
| Hard to revoke (need blocklist) | Immediate revocation (delete session) |
| Contains claims (self-describing) | Lookup required for each request |
| Better for microservices (no shared state) | Better for monoliths |
| XSS risk if stored in JS | CSRF risk if using cookies |

**Best practice**: Short-lived access tokens (15 min JWT) + long-lived refresh tokens (7 day, stored server-side).

### Q13: How do you implement rate limiting?
**Answer**: Algorithms:
- **Fixed window**: Count requests per fixed time window (e.g., 100/min). Simple but bursty at boundaries.
- **Sliding window**: Weighted count across current and previous windows. Smoother than fixed.
- **Token bucket**: Tokens added at fixed rate, consumed per request. Allows bursts up to bucket capacity.
- **Leaky bucket**: Requests processed at fixed rate, queue excess. Smoothest output.

Implementation: Redis `INCR` + `EXPIRE` for distributed rate limiting. Return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `Retry-After` headers.

### Q14: What API security headers should every response include?
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
X-XSS-Protection: 0  # Deprecated, rely on CSP
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

## Section 5: Architecture & Design

### Q15: What is the BFF pattern and when would you use it?
**Answer**: Backend for Frontend — separate API layer per client type (web, mobile, admin). Each BFF aggregates/transforms data from microservices to match client needs. Use when: clients have significantly different data needs, you want to avoid over-fetching for mobile, or different teams own different clients.

### Q16: Design Scenario — Design a URL shortener API

```
POST /api/urls
Body: { "originalUrl": "https://...", "customAlias": "my-link" }
Response: 201 { "shortCode": "abc123", "shortUrl": "https://short.ly/abc123" }

GET  /api/urls/:code/stats → Analytics
GET  /:code → 301 Redirect to original URL
DELETE /api/urls/:code → Delete short URL

Considerations:
- Base62 encoding for short codes (a-z, A-Z, 0-9)
- Pre-generate short codes for high throughput
- Cache popular URLs in Redis
- Rate limit creation (anti-spam)
- TTL for expiring links
```

### Q17: Design Scenario — Design a payment API with idempotency

```
POST /api/payments
Headers:
  Idempotency-Key: unique-client-key-123
Body: { "amount": 9999, "currency": "USD", "recipientId": "..." }

Server flow:
1. Check if Idempotency-Key exists in cache/DB
2. If exists → return cached response (same status, body)
3. If not → process payment → store response with key
4. Key expires after 24 hours

Response: 201 Created
{
  "paymentId": "pay_abc",
  "status": "processing",
  "amount": 9999,
  "idempotencyKey": "unique-client-key-123"
}

Webhook for async completion:
POST /webhooks/payments
{ "paymentId": "pay_abc", "status": "completed", "signature": "..." }
```

## Rapid-Fire Summary

| Concept | One-Liner |
|---------|-----------|
| REST | Architectural style with 6 constraints, resource-oriented |
| Idempotency | Same request N times = same result |
| PUT vs PATCH | Full replace vs partial update |
| 401 vs 403 | Not authenticated vs not authorized |
| JWT vs Session | Stateless vs stateful auth |
| HATEOAS | Responses include navigable links |
| Rate limiting | Token bucket for bursts, sliding window for smoothness |
| BFF | Separate backend per client type |
| API Gateway | Central entry for routing, auth, rate limiting |
| GraphQL N+1 | Solve with DataLoader batching |
