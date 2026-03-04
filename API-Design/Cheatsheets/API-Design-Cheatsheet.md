# API Design Cheatsheet — Quick Reference

## REST Resource Naming
```
✅ Plural nouns:     /users, /orders, /products
✅ Kebab-case:       /order-items, /user-profiles
✅ Hierarchy:        /users/123/orders/456
❌ Verbs:            /getUser, /createOrder
❌ File extensions:  /users.json
```

## HTTP Methods
```
GET     → Read (safe, idempotent, cacheable)
POST    → Create (not idempotent, not cacheable)
PUT     → Replace (idempotent)
PATCH   → Partial update
DELETE  → Remove (idempotent)
HEAD    → Headers only (like GET without body)
OPTIONS → CORS preflight / capabilities
```

## Status Codes — Must Know
```
200 OK              → Success (GET, PUT, PATCH)
201 Created         → POST success (+ Location header)
204 No Content      → DELETE success (no body)
301 Moved Perm.     → Permanent redirect
304 Not Modified    → Cache still valid
400 Bad Request     → Malformed request / syntax
401 Unauthorized    → Authentication required
403 Forbidden       → Authenticated, not authorized
404 Not Found       → Resource doesn't exist
409 Conflict        → Duplicate / concurrent edit
422 Unprocessable   → Validation / business rule
429 Too Many Reqs   → Rate limited (+ Retry-After)
500 Internal Error  → Server crash
502 Bad Gateway     → Upstream failure
503 Unavailable     → Overloaded / maintenance
```

## Pagination Patterns
```
Offset:  /users?page=2&limit=20          Simple, slow for deep pages
Cursor:  /users?cursor=abc&limit=20      Consistent, no page jumping
Keyset:  /users?after_id=123&limit=20    Fastest, index-based
```

## Filtering & Sorting
```
/users?status=active&role=admin          Filtering
/users?sort=name:asc,created_at:desc     Sorting
/users?fields=id,name,email              Sparse fieldsets
/users?search=bharath                    Full-text search
```

## Versioning
```
URL:     /v1/users, /v2/users
Header:  Accept: application/vnd.api.v2+json
Query:   /users?version=2
```

## Authentication
```
API Key:     X-API-Key: sk_live_abc123
Bearer:      Authorization: Bearer eyJ...
OAuth 2.0:   Authorization Code + PKCE (web/mobile)
             Client Credentials (service-to-service)
Session:     Set-Cookie: sid=abc; HttpOnly; Secure; SameSite=Strict
```

## JWT Structure
```
Header:    { "alg": "RS256", "typ": "JWT" }
Payload:   { "sub": "123", "exp": 1641081600, "role": "admin" }
Signature: RS256(base64(header) + "." + base64(payload), privateKey)

Access token:  15 min TTL, in memory
Refresh token: 7 day TTL, HttpOnly cookie, rotate on use
```

## Security Headers
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
```

## Rate Limiting Headers
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
Retry-After: 60
```

## Caching
```http
# Cacheable (public resources)
Cache-Control: public, max-age=3600, s-maxage=7200
ETag: "abc123"

# Revalidate every time
Cache-Control: private, no-cache
ETag: "abc123"

# Never cache (sensitive data)
Cache-Control: no-store
```

## Error Response Template
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "details": [
      { "field": "email", "message": "Invalid format" }
    ],
    "requestId": "req_abc123"
  }
}
```

## GraphQL Quick Reference
```graphql
# Query
query GetUser($id: ID!) {
  user(id: $id) { name email posts { title } }
}

# Mutation
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) { id name }
}

# Subscription
subscription OnPostCreated {
  postCreated { id title }
}
```

## API Gateway Checklist
```
☐ Request routing
☐ Authentication / Authorization
☐ Rate limiting
☐ Request/response transformation
☐ Circuit breaking
☐ Logging / monitoring
☐ CORS handling
☐ SSL termination
```

## REST vs GraphQL vs gRPC
```
REST     → CRUD, public APIs, HTTP caching
GraphQL  → Complex UIs, multiple clients, nested data
gRPC     → Microservices, streaming, low latency
```
