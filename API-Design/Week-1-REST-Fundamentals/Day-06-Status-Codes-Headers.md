# Day 6: Status Codes & Headers — Complete Reference

## HTTP Status Code Categories

| Range | Category | Meaning |
|-------|----------|---------|
| 1xx | Informational | Request received, continuing |
| 2xx | Success | Request accepted/completed |
| 3xx | Redirection | Further action needed |
| 4xx | Client Error | Bad request from client |
| 5xx | Server Error | Server failed to process |

## Essential Status Codes for APIs

### 2xx Success

```
200 OK
├── GET: Resource returned successfully
├── PUT: Resource updated, returns updated resource
├── PATCH: Resource partially updated
└── DELETE: Resource deleted (if returning deleted resource)

201 Created
├── POST: Resource created successfully
├── Must include Location header with new resource URL
└── Body should contain the created resource

202 Accepted
├── Request accepted for async processing
├── Processing not complete yet
└── Use for long-running tasks, batch operations

204 No Content
├── Success, but no body to return
├── DELETE: Resource deleted (no body)
└── PUT/PATCH: Updated, no need to return body
```

### 3xx Redirection

```
301 Moved Permanently  → Resource permanently at new URL
302 Found              → Temporary redirect
304 Not Modified       → Cached version still valid (ETag match)
307 Temporary Redirect → Like 302, but preserves HTTP method
308 Permanent Redirect → Like 301, but preserves HTTP method
```

### 4xx Client Errors

```
400 Bad Request
├── Malformed JSON, missing required fields
├── Validation errors
└── Include details in response body

401 Unauthorized
├── Authentication required
├── Missing or invalid credentials
└── Should include WWW-Authenticate header

403 Forbidden
├── Authenticated but not authorized
├── User lacks permission for this action
└── Don't reveal whether resource exists

404 Not Found
├── Resource doesn't exist
├── Also used to hide unauthorized resources
└── GET /users/999 → 404

405 Method Not Allowed
├── HTTP method not supported for this resource
├── GET /users ✅, DELETE /users ❌
└── Include Allow header with valid methods

409 Conflict
├── Request conflicts with current state
├── Duplicate entry, concurrent modification
└── PUT with outdated ETag

422 Unprocessable Entity
├── Syntactically correct but semantically invalid
├── Business rule violations
└── "Email already registered", "Age must be > 0"

429 Too Many Requests
├── Rate limit exceeded
├── Include Retry-After header
└── Include rate limit headers
```

### 5xx Server Errors

```
500 Internal Server Error  → Unexpected server failure
502 Bad Gateway           → Upstream service failure
503 Service Unavailable   → Server overloaded/maintenance (include Retry-After)
504 Gateway Timeout       → Upstream service timed out
```

## Choosing the Right Status Code

```
Is the request valid?
├── No → Is the body malformed?
│   ├── Yes → 400 Bad Request
│   └── No → Are business rules violated?
│       ├── Yes → 422 Unprocessable Entity
│       └── No → Is there a conflict?
│           └── Yes → 409 Conflict
├── Yes → Is the user authenticated?
│   ├── No → 401 Unauthorized
│   └── Yes → Is the user authorized?
│       ├── No → 403 Forbidden
│       └── Yes → Does the resource exist?
│           ├── No → 404 Not Found
│           └── Yes → Process successfully?
│               ├── No → 500 Internal Server Error
│               └── Yes → What was the operation?
│                   ├── GET → 200 OK
│                   ├── POST → 201 Created
│                   ├── PUT/PATCH → 200 OK or 204 No Content
│                   └── DELETE → 204 No Content
```

## HTTP Headers — Complete API Reference

### Request Headers

```http
# Content negotiation
Accept: application/json
Accept-Language: en-US
Accept-Encoding: gzip, deflate, br

# Authentication
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
Cookie: session=abc123

# Caching
If-None-Match: "etag-value"
If-Modified-Since: Wed, 01 Jan 2025 00:00:00 GMT

# CORS
Origin: https://example.com

# Custom
X-Request-Id: uuid-for-tracing
X-Idempotency-Key: unique-key-123
```

### Response Headers

```http
# Content
Content-Type: application/json; charset=utf-8
Content-Length: 1234

# Caching
Cache-Control: public, max-age=3600, s-maxage=7200
ETag: "abc123"
Last-Modified: Wed, 01 Jan 2025 00:00:00 GMT
Vary: Accept, Authorization

# Security
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'

# Rate Limiting
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
Retry-After: 60

# CORS
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Max-Age: 86400

# Pagination
Link: <https://api.example.com/users?page=2>; rel="next",
      <https://api.example.com/users?page=5>; rel="last"

# Resource Location
Location: /users/123
```

## Error Response Design

### Standard Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address",
        "code": "INVALID_FORMAT"
      },
      {
        "field": "age",
        "message": "Must be between 0 and 150",
        "code": "OUT_OF_RANGE",
        "metadata": { "min": 0, "max": 150 }
      }
    ],
    "requestId": "req_abc123",
    "timestamp": "2025-01-01T00:00:00Z",
    "documentation": "https://api.example.com/docs/errors#VALIDATION_ERROR"
  }
}
```

### RFC 7807 — Problem Details

```json
{
  "type": "https://api.example.com/errors/validation",
  "title": "Validation Error",
  "status": 422,
  "detail": "The email field is not a valid email address",
  "instance": "/users",
  "errors": [
    { "pointer": "/email", "detail": "Invalid format" }
  ]
}
```

## Caching Strategy for APIs

```http
# Immutable static assets
Cache-Control: public, max-age=31536000, immutable

# API responses — revalidate
Cache-Control: private, no-cache
ETag: "v1-abc123"

# Never cache (sensitive data)
Cache-Control: no-store

# Conditional request flow:
# 1. Client sends: If-None-Match: "v1-abc123"
# 2. Server checks: ETag matches?
#    Yes → 304 Not Modified (no body)
#    No  → 200 OK with new ETag
```

## Key Takeaways

1. **Use specific status codes** — 422 for validation, 409 for conflicts, 429 for rate limits
2. **Always include error details** — machine-readable codes + human-readable messages
3. **Security headers are mandatory** — HSTS, CSP, X-Content-Type-Options
4. **Caching headers reduce load** — ETag + Cache-Control = efficient APIs
5. **Rate limit headers** help clients self-throttle
