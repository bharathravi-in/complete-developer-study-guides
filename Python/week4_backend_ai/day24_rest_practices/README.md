# Day 24 - REST API Best Practices

## Topics Covered
- RESTful design principles
- API versioning strategies
- Error handling & status codes
- Pagination, filtering, sorting
- Security best practices
- API documentation (OpenAPI/Swagger)

## REST Constraints
| Principle | Description |
|-----------|-------------|
| Client-Server | Separation of concerns |
| Stateless | No session state on server |
| Cacheable | Responses can be cached |
| Uniform Interface | Consistent endpoints |
| Layered System | Client doesn't know intermediaries |
| Code on Demand | Optional executable code |

## HTTP Methods & Status Codes
```
GET    → 200 OK, 404 Not Found
POST   → 201 Created, 400 Bad Request
PUT    → 200 OK, 404 Not Found
PATCH  → 200 OK, 404 Not Found
DELETE → 204 No Content, 404 Not Found
```

## Project Structure
```
day24_rest_practices/
├── README.md
├── practice.py           # API design concepts
├── api_design.py         # Best practices demo
├── error_handling.py     # Error handling patterns
└── requirements.txt
```

## Key Concepts

### 1. Resource Naming
```
✓ GET /users              # Collection
✓ GET /users/123          # Single resource
✓ GET /users/123/posts    # Sub-resource
✓ POST /users             # Create
✓ PUT /users/123          # Full update
✓ PATCH /users/123        # Partial update
✓ DELETE /users/123       # Delete

✗ GET /getUsers           # Verb in URL
✗ POST /users/create      # Redundant
✗ GET /user               # Singular collection
```

### 2. API Versioning
```
# URL Path (Recommended)
/api/v1/users
/api/v2/users

# Query Parameter
/api/users?version=1

# Header
Accept: application/vnd.api.v1+json
```

### 3. Pagination
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "next": "/users?page=2",
    "prev": null
  }
}
```

### 4. Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {"field": "email", "message": "Invalid email format"}
    ]
  }
}
```

## Run
```bash
python practice.py
python api_design.py
```

## Practice Exercises
1. Design a RESTful API for a blog system
2. Implement comprehensive error handling
3. Add pagination, filtering, and sorting
4. Create OpenAPI documentation
5. Implement rate limiting
