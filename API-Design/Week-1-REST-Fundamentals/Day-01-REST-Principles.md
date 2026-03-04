# Day 1: REST Principles — Architectural Foundations

## What Is REST?

**REST** (Representational State Transfer) is an architectural style defined by Roy Fielding in his 2000 doctoral dissertation. It is NOT a protocol — it's a set of constraints for designing networked applications.

## The 6 REST Constraints

### 1. Client-Server Separation
- Client handles UI/UX, server handles data storage/business logic
- Separation improves portability (multiple clients) and scalability

### 2. Statelessness
- Each request contains ALL information needed to process it
- Server stores no client context between requests
- State lives in the client (tokens, session data)

```
❌ Stateful: Server stores session → "Remember user #123 is logged in"
✅ Stateless: Client sends token → "Bearer eyJhbGci..." with every request
```

### 3. Cacheability
- Responses must declare themselves cacheable or not
- Reduces client-server interactions, improves performance

```http
Cache-Control: public, max-age=3600
ETag: "abc123"
Last-Modified: Wed, 01 Jan 2025 00:00:00 GMT
```

### 4. Uniform Interface (Most Important)
Four sub-constraints:
- **Resource identification**: URLs identify resources (`/users/123`)
- **Manipulation through representations**: JSON/XML representations modify resources
- **Self-descriptive messages**: Request has all info needed (Content-Type, methods)
- **HATEOAS**: Hypermedia as the engine of application state

### 5. Layered System
- Client can't tell if connected directly to server or intermediary
- Enables load balancers, caches, security layers

### 6. Code on Demand (Optional)
- Server can send executable code (JavaScript) to the client

## REST vs RPC vs GraphQL

| Aspect | REST | RPC (gRPC) | GraphQL |
|--------|------|-----------|---------|
| **URL Design** | `/resources/{id}` | `/service.Method` | Single `/graphql` |
| **Data Fetching** | Server decides shape | Server decides | Client decides |
| **Over-fetching** | Common | Minimal | None |
| **Under-fetching** | Common (N+1) | Minimal | None |
| **Caching** | HTTP caching built-in | Complex | Complex |
| **Versioning** | URL/Header versioning | Proto versioning | Schema evolution |
| **Best For** | CRUD, public APIs | Microservices, internal | Complex UIs, mobile |

## Resource-Oriented Design

### Resources, Not Actions

```
❌ Bad (RPC-style):
POST /getUser
POST /createUser
POST /deleteUser
POST /updateUserEmail

✅ Good (Resource-oriented):
GET    /users          → List users
GET    /users/123      → Get single user
POST   /users          → Create user
PUT    /users/123      → Replace user
PATCH  /users/123      → Partial update
DELETE /users/123      → Delete user
```

### Resource Hierarchy

```
/users                         → User collection
/users/123                     → Single user
/users/123/posts               → User's posts
/users/123/posts/456           → Specific post
/users/123/posts/456/comments  → Post's comments
```

### Resource Naming Conventions

```
✅ Use nouns: /users, /products, /orders
❌ Avoid verbs: /getUsers, /createProduct
✅ Use plural: /users (not /user)
✅ Use kebab-case: /order-items (not /orderItems)
✅ Use lowercase: /users (not /Users)
❌ Avoid file extensions: /users.json
✅ Use query params for filtering: /users?role=admin
```

## HTTP Methods — Semantic Meaning

| Method | Purpose | Idempotent | Safe | Request Body |
|--------|---------|------------|------|-------------|
| GET | Read | ✅ | ✅ | No |
| POST | Create | ❌ | ❌ | Yes |
| PUT | Replace | ✅ | ❌ | Yes |
| PATCH | Partial Update | ❌* | ❌ | Yes |
| DELETE | Remove | ✅ | ❌ | Rarely |
| HEAD | Get Headers | ✅ | ✅ | No |
| OPTIONS | Get Capabilities | ✅ | ✅ | No |

*PATCH can be idempotent depending on implementation.

### PUT vs PATCH

```json
// PUT: Full replacement — must send ALL fields
PUT /users/123
{
  "name": "Bharath",
  "email": "bharath@example.com",
  "age": 30,
  "role": "admin"
}

// PATCH: Partial update — only changed fields
PATCH /users/123
{
  "role": "admin"
}

// JSON Patch (RFC 6902) — operation-based
PATCH /users/123
Content-Type: application/json-patch+json
[
  { "op": "replace", "path": "/role", "value": "admin" },
  { "op": "add", "path": "/permissions/-", "value": "write" }
]
```

## Richardson Maturity Model

| Level | Description | Example |
|-------|------------|---------|
| **Level 0** | Single endpoint, RPC | POST /api → action in body |
| **Level 1** | Resources | /users, /posts — but only POST |
| **Level 2** | HTTP Methods | GET /users, POST /users, DELETE /users/123 |
| **Level 3** | HATEOAS | Responses include navigable links |

### Level 3 (HATEOAS) Example

```json
{
  "id": 123,
  "name": "Bharath",
  "email": "bharath@example.com",
  "_links": {
    "self": { "href": "/users/123" },
    "posts": { "href": "/users/123/posts" },
    "update": { "href": "/users/123", "method": "PUT" },
    "delete": { "href": "/users/123", "method": "DELETE" }
  }
}
```

## Content Negotiation

```http
# Client requests JSON
GET /users/123
Accept: application/json

# Client requests XML
GET /users/123
Accept: application/xml

# Server responds with format
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
```

## Idempotency — Why It Matters

**Idempotent**: Making the same request N times produces the same result.

```
GET /users/123     → Always returns same user (idempotent)
PUT /users/123     → Always sets same state (idempotent)
DELETE /users/123  → First: deletes. Second: 404 (still idempotent — same end state)
POST /users        → Creates new user each time (NOT idempotent)
```

**Real-world**: Implement idempotency keys for non-idempotent operations:

```http
POST /payments
Idempotency-Key: unique-request-id-abc123
Content-Type: application/json

{ "amount": 100, "currency": "USD" }
```

## Practice Exercises

1. Design a REST API for an e-commerce platform (products, cart, orders, payments)
2. Convert these RPC endpoints to REST: `POST /getUserOrders`, `POST /cancelOrder`, `POST /searchProducts`
3. Identify REST violations in an existing API and propose fixes

## Key Takeaways

1. **REST is constraints**, not a protocol — it's about resource-oriented design
2. **Statelessness** is non-negotiable — every request is self-contained
3. **Use HTTP semantics correctly** — methods, status codes, headers have meaning
4. **Resources are nouns** — URLs identify things, methods define actions
5. **Idempotency** is critical for reliable distributed systems
