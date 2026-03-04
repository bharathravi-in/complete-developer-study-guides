#!/usr/bin/env python3
"""Day 24 - REST API Best Practices"""

print("=" * 50)
print("REST API DESIGN PRINCIPLES")
print("=" * 50)


# ============================================
# 1. RESOURCE NAMING CONVENTIONS
# ============================================
print("\n--- 1. Resource Naming ---")

GOOD_ENDPOINTS = """
✓ GET    /api/v1/users              # Get all users
✓ GET    /api/v1/users/123          # Get user by ID
✓ POST   /api/v1/users              # Create user
✓ PUT    /api/v1/users/123          # Replace user
✓ PATCH  /api/v1/users/123          # Partial update
✓ DELETE /api/v1/users/123          # Delete user

✓ GET    /api/v1/users/123/posts    # User's posts (sub-resource)
✓ GET    /api/v1/posts?author=123   # Filter posts
✓ GET    /api/v1/posts?status=published&sort=-created_at
"""

BAD_ENDPOINTS = """
✗ GET    /getUsers                  # Verb in URL
✗ POST   /users/create              # Redundant action
✗ GET    /user                      # Singular for collection
✗ POST   /users/123/delete          # Should use DELETE method
✗ GET    /getUserById/123           # Not RESTful
"""

print("Good Endpoints:")
print(GOOD_ENDPOINTS)
print("Bad Endpoints:")
print(BAD_ENDPOINTS)


# ============================================
# 2. HTTP STATUS CODES
# ============================================
print("\n--- 2. HTTP Status Codes ---")

STATUS_CODES = {
    # 2xx Success
    200: ("OK", "Request succeeded"),
    201: ("Created", "Resource created (POST)"),
    204: ("No Content", "Success, no body (DELETE)"),
    
    # 3xx Redirection
    301: ("Moved Permanently", "Resource moved"),
    304: ("Not Modified", "Cached version valid"),
    
    # 4xx Client Errors
    400: ("Bad Request", "Invalid syntax/validation"),
    401: ("Unauthorized", "Authentication required"),
    403: ("Forbidden", "Authenticated but not allowed"),
    404: ("Not Found", "Resource doesn't exist"),
    405: ("Method Not Allowed", "HTTP method not supported"),
    409: ("Conflict", "Resource conflict"),
    422: ("Unprocessable Entity", "Validation failed"),
    429: ("Too Many Requests", "Rate limited"),
    
    # 5xx Server Errors
    500: ("Internal Server Error", "Server error"),
    502: ("Bad Gateway", "Invalid upstream response"),
    503: ("Service Unavailable", "Server overloaded/maintenance"),
}

print("Common Status Codes:")
for code, (name, desc) in STATUS_CODES.items():
    print(f"  {code} {name}: {desc}")


# ============================================
# 3. ERROR RESPONSE FORMAT
# ============================================
print("\n--- 3. Error Response Format ---")

from dataclasses import dataclass, asdict
from typing import List, Optional
import json


@dataclass
class FieldError:
    """Individual field validation error."""
    field: str
    message: str
    code: str


@dataclass
class APIError:
    """Standardized API error response."""
    code: str
    message: str
    status: int
    details: Optional[List[FieldError]] = None
    
    def to_dict(self) -> dict:
        result = {"error": asdict(self)}
        if self.details is None:
            del result["error"]["details"]
        return result


# Examples
validation_error = APIError(
    code="VALIDATION_ERROR",
    message="Input validation failed",
    status=422,
    details=[
        FieldError("email", "Invalid email format", "invalid_format"),
        FieldError("password", "Must be at least 8 characters", "min_length"),
    ]
)

auth_error = APIError(
    code="UNAUTHORIZED",
    message="Invalid or expired token",
    status=401
)

print("Validation Error Response:")
print(json.dumps(validation_error.to_dict(), indent=2))

print("\nAuth Error Response:")
print(json.dumps(auth_error.to_dict(), indent=2))


# ============================================
# 4. PAGINATION
# ============================================
print("\n--- 4. Pagination ---")


@dataclass
class PaginationMeta:
    """Pagination metadata."""
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool
    next_url: Optional[str] = None
    prev_url: Optional[str] = None


def paginate(items: list, page: int, per_page: int, base_url: str) -> dict:
    """Create paginated response."""
    total = len(items)
    pages = (total + per_page - 1) // per_page
    
    start = (page - 1) * per_page
    end = start + per_page
    page_items = items[start:end]
    
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
        next_url=f"{base_url}?page={page + 1}" if page < pages else None,
        prev_url=f"{base_url}?page={page - 1}" if page > 1 else None,
    )
    
    return {
        "data": page_items,
        "pagination": asdict(meta)
    }


# Example
all_items = list(range(1, 101))  # 100 items
result = paginate(all_items, page=2, per_page=20, base_url="/api/v1/items")
print("Paginated Response:")
print(f"  Data: {result['data'][:5]}... ({len(result['data'])} items)")
print(f"  Pagination: page {result['pagination']['page']}/{result['pagination']['pages']}")
print(f"  Next: {result['pagination']['next_url']}")


# ============================================
# 5. FILTERING & SORTING
# ============================================
print("\n--- 5. Filtering & Sorting ---")

"""
Filtering Patterns:
  /users?status=active                     # Simple filter
  /users?age_gte=18&age_lte=65             # Range filter
  /users?name__contains=john               # Contains
  /users?role__in=admin,moderator          # Multiple values
  /posts?created_at__gt=2024-01-01         # Date comparison

Sorting Patterns:
  /users?sort=name                         # Ascending
  /users?sort=-name                        # Descending
  /users?sort=status,-created_at           # Multiple fields
  /users?order_by=name&order=asc           # Alternative
"""


@dataclass
class FilterParams:
    """Query parameters for filtering."""
    status: Optional[str] = None
    name_contains: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    

@dataclass
class SortParams:
    """Query parameters for sorting."""
    sort_by: str = "id"
    sort_order: str = "asc"  # asc or desc


def parse_sort_param(sort_string: str) -> SortParams:
    """Parse sort parameter like '-created_at'."""
    if sort_string.startswith("-"):
        return SortParams(sort_by=sort_string[1:], sort_order="desc")
    return SortParams(sort_by=sort_string, sort_order="asc")


# Example
sort = parse_sort_param("-created_at")
print(f"Sort param '-created_at': {sort}")


# ============================================
# 6. HATEOAS (Hypermedia Links)
# ============================================
print("\n--- 6. HATEOAS Links ---")

"""
HATEOAS = Hypermedia as the Engine of Application State

Response includes links to related resources and actions.
"""

user_response = {
    "id": 123,
    "name": "John Doe",
    "email": "john@example.com",
    "_links": {
        "self": {"href": "/api/v1/users/123"},
        "posts": {"href": "/api/v1/users/123/posts"},
        "followers": {"href": "/api/v1/users/123/followers"},
        "update": {"href": "/api/v1/users/123", "method": "PATCH"},
        "delete": {"href": "/api/v1/users/123", "method": "DELETE"},
    }
}

print("User Response with HATEOAS:")
print(json.dumps(user_response, indent=2))


# ============================================
# 7. API VERSIONING
# ============================================
print("\n--- 7. API Versioning ---")

VERSIONING_STRATEGIES = """
1. URL Path (Recommended)
   /api/v1/users
   /api/v2/users
   
   Pros: Clear, easy to implement, cacheable
   Cons: Not truly RESTful (version in URL)

2. Query Parameter
   /api/users?version=1
   
   Pros: Optional versioning
   Cons: Can be missed, caching issues

3. Header
   Accept: application/vnd.api.v1+json
   X-API-Version: 1
   
   Pros: Clean URLs, truly RESTful
   Cons: Harder to test, less visible

4. Content Negotiation
   Accept: application/vnd.myapi+json; version=1
   
   Pros: HTTP standard compliant
   Cons: Complex to implement
"""

print(VERSIONING_STRATEGIES)


# ============================================
# 8. RATE LIMITING HEADERS
# ============================================
print("\n--- 8. Rate Limiting ---")

rate_limit_headers = {
    "X-RateLimit-Limit": "100",        # Max requests per window
    "X-RateLimit-Remaining": "95",     # Remaining requests
    "X-RateLimit-Reset": "1640995200", # Unix timestamp when limit resets
    "Retry-After": "60",               # Seconds to wait (when 429)
}

print("Rate Limit Headers:")
for header, value in rate_limit_headers.items():
    print(f"  {header}: {value}")


# ============================================
# 9. SECURITY HEADERS
# ============================================
print("\n--- 9. Security Headers ---")

security_headers = {
    "Content-Security-Policy": "default-src 'self'",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Cache-Control": "no-store",  # For sensitive data
}

print("Security Headers:")
for header, value in security_headers.items():
    print(f"  {header}: {value}")


# ============================================
# 10. SUMMARY
# ============================================
print("\n" + "=" * 50)
print("REST API BEST PRACTICES SUMMARY")
print("=" * 50)
print("""
Design:
  ✓ Use nouns for resources, not verbs
  ✓ Use plural resource names (/users, not /user)
  ✓ Use proper HTTP methods
  ✓ Return appropriate status codes

Responses:
  ✓ Consistent error format
  ✓ Include pagination metadata
  ✓ Support filtering and sorting
  ✓ Consider HATEOAS links

Security:
  ✓ Use HTTPS always
  ✓ Implement rate limiting
  ✓ Add security headers
  ✓ Validate all inputs

Documentation:
  ✓ Use OpenAPI/Swagger
  ✓ Document all endpoints
  ✓ Provide examples
  ✓ Version your API
""")
