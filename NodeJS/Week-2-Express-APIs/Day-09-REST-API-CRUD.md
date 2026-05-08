# Day 9: REST API Design & CRUD Operations

## 🎯 Learning Objectives
- Design RESTful APIs following best practices
- Implement full CRUD with proper HTTP semantics
- Handle pagination, filtering, and sorting
- Implement input validation

---

## 📚 REST API Design Principles

### Resource Naming Conventions

```
✅ Good:
GET    /api/users              → List users
GET    /api/users/123          → Get user 123
POST   /api/users              → Create user
PUT    /api/users/123          → Replace user 123
PATCH  /api/users/123          → Partial update user 123
DELETE /api/users/123          → Delete user 123

GET    /api/users/123/posts    → Get posts by user 123
POST   /api/users/123/posts    → Create post for user 123

❌ Bad:
GET    /api/getUsers
POST   /api/createUser
GET    /api/user/delete/123
POST   /api/users/update
```

### HTTP Status Codes

```javascript
// 2xx Success
200 // OK - GET, PUT, PATCH success
201 // Created - POST success (include Location header)
204 // No Content - DELETE success

// 4xx Client Error
400 // Bad Request - validation error
401 // Unauthorized - no/invalid authentication
403 // Forbidden - authenticated but not authorized
404 // Not Found - resource doesn't exist
409 // Conflict - duplicate resource
422 // Unprocessable Entity - semantic validation failure
429 // Too Many Requests - rate limited

// 5xx Server Error
500 // Internal Server Error
502 // Bad Gateway - upstream service failed
503 // Service Unavailable - maintenance/overload
```

---

## 🔧 Full CRUD Implementation

```javascript
const express = require('express');
const router = express.Router();
const { v4: uuid } = require('uuid');

// In-memory store (replace with database)
let users = [];

// GET /api/users - List with pagination, filtering, sorting
router.get('/users', (req, res) => {
  let result = [...users];
  
  // Filtering
  const { role, status, search } = req.query;
  if (role) result = result.filter(u => u.role === role);
  if (status) result = result.filter(u => u.status === status);
  if (search) {
    const q = search.toLowerCase();
    result = result.filter(u => 
      u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    );
  }
  
  // Sorting
  const { sort = 'createdAt', order = 'desc' } = req.query;
  result.sort((a, b) => {
    const modifier = order === 'asc' ? 1 : -1;
    return a[sort] > b[sort] ? modifier : -modifier;
  });
  
  // Pagination
  const page = Math.max(1, parseInt(req.query.page) || 1);
  const limit = Math.min(100, Math.max(1, parseInt(req.query.limit) || 20));
  const startIndex = (page - 1) * limit;
  const total = result.length;
  const paginatedUsers = result.slice(startIndex, startIndex + limit);
  
  res.json({
    data: paginatedUsers,
    pagination: {
      page,
      limit,
      total,
      totalPages: Math.ceil(total / limit),
      hasNext: startIndex + limit < total,
      hasPrev: page > 1
    }
  });
});

// GET /api/users/:id - Get single user
router.get('/users/:id', (req, res) => {
  const user = users.find(u => u.id === req.params.id);
  if (!user) {
    return res.status(404).json({ error: { message: 'User not found', code: 'NOT_FOUND' } });
  }
  res.json({ data: user });
});

// POST /api/users - Create user
router.post('/users', validateUser, (req, res) => {
  const user = {
    id: uuid(),
    ...req.body,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  users.push(user);
  
  res.status(201)
    .setHeader('Location', `/api/users/${user.id}`)
    .json({ data: user });
});

// PUT /api/users/:id - Full replacement
router.put('/users/:id', validateUser, (req, res) => {
  const index = users.findIndex(u => u.id === req.params.id);
  if (index === -1) {
    return res.status(404).json({ error: { message: 'User not found' } });
  }
  
  users[index] = {
    id: req.params.id,
    ...req.body,
    createdAt: users[index].createdAt,
    updatedAt: new Date().toISOString()
  };
  
  res.json({ data: users[index] });
});

// PATCH /api/users/:id - Partial update
router.patch('/users/:id', (req, res) => {
  const index = users.findIndex(u => u.id === req.params.id);
  if (index === -1) {
    return res.status(404).json({ error: { message: 'User not found' } });
  }
  
  users[index] = {
    ...users[index],
    ...req.body,
    id: req.params.id, // Prevent ID override
    updatedAt: new Date().toISOString()
  };
  
  res.json({ data: users[index] });
});

// DELETE /api/users/:id
router.delete('/users/:id', (req, res) => {
  const index = users.findIndex(u => u.id === req.params.id);
  if (index === -1) {
    return res.status(404).json({ error: { message: 'User not found' } });
  }
  
  users.splice(index, 1);
  res.status(204).end();
});
```

---

## ✅ Input Validation

```javascript
// Manual validation middleware
function validateUser(req, res, next) {
  const errors = [];
  const { name, email, role } = req.body;
  
  if (!name || typeof name !== 'string' || name.trim().length < 2) {
    errors.push({ field: 'name', message: 'Name must be at least 2 characters' });
  }
  
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.push({ field: 'email', message: 'Valid email is required' });
  }
  
  if (role && !['admin', 'user', 'moderator'].includes(role)) {
    errors.push({ field: 'role', message: 'Invalid role' });
  }
  
  if (errors.length > 0) {
    return res.status(400).json({ error: { message: 'Validation failed', details: errors } });
  }
  
  // Sanitize - only allow known fields
  req.body = { name: name.trim(), email: email.toLowerCase().trim(), role: role || 'user' };
  next();
}

// Using Joi (popular validation library)
const Joi = require('joi');

const userSchema = Joi.object({
  name: Joi.string().min(2).max(50).required(),
  email: Joi.string().email().required(),
  role: Joi.string().valid('admin', 'user', 'moderator').default('user'),
  age: Joi.number().integer().min(13).max(150)
});

function validate(schema) {
  return (req, res, next) => {
    const { error, value } = schema.validate(req.body, { abortEarly: false, stripUnknown: true });
    if (error) {
      const details = error.details.map(d => ({ field: d.path.join('.'), message: d.message }));
      return res.status(400).json({ error: { message: 'Validation failed', details } });
    }
    req.body = value; // Use validated & sanitized data
    next();
  };
}

router.post('/users', validate(userSchema), createUser);
```

---

## 📄 Response Formatting

```javascript
// Consistent response envelope
function sendSuccess(res, data, statusCode = 200, meta = {}) {
  const response = { success: true, data };
  if (Object.keys(meta).length) response.meta = meta;
  return res.status(statusCode).json(response);
}

function sendError(res, message, statusCode = 500, details = null) {
  const response = { success: false, error: { message, statusCode } };
  if (details) response.error.details = details;
  return res.status(statusCode).json(response);
}

// HATEOAS links (Level 3 REST)
router.get('/users/:id', (req, res) => {
  const user = users.find(u => u.id === req.params.id);
  res.json({
    data: user,
    links: {
      self: `/api/users/${user.id}`,
      posts: `/api/users/${user.id}/posts`,
      update: `/api/users/${user.id}`,
      delete: `/api/users/${user.id}`
    }
  });
});
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is REST and what makes an API RESTful?**

REST (Representational State Transfer) is an architectural style. Principles: stateless communication, resource-based URLs (nouns, not verbs), standard HTTP methods (GET/POST/PUT/DELETE), proper status codes, and uniform interface. RESTful APIs treat everything as a resource with CRUD operations.

**Q2: What is the difference between PUT and PATCH?**

PUT replaces the entire resource (must send complete object). PATCH applies partial modifications (send only changed fields). PUT is idempotent — sending the same request twice has the same effect. Both are used for updates, but PATCH is more common for partial updates in practice.

**Q3: How do you implement pagination in a REST API?**

Common patterns: (1) Offset/limit: `?page=2&limit=20` — simple but skip-count is expensive for large datasets. (2) Cursor-based: `?cursor=abc123&limit=20` — efficient, uses last item's ID/timestamp as cursor. Return pagination metadata (total, hasNext, nextCursor) in response.

### Intermediate

**Q4: How do you handle API versioning?**

Strategies: (1) URL path `/api/v1/users` — explicit, cacheable. (2) Header `Accept: application/vnd.api.v2+json` — cleaner URLs. (3) Query param `?version=2` — easy to test. Best practice: URL versioning for major changes, maintain backward compatibility, deprecation headers for old versions.

**Q5: What is idempotency and which HTTP methods are idempotent?**

An operation is idempotent if performing it multiple times has the same effect as performing it once. Idempotent: GET, PUT, DELETE, HEAD, OPTIONS. Not idempotent: POST (creates new resource each time). PATCH can be idempotent depending on implementation. Important for retry logic and network reliability.

**Q6: How would you design a search/filter API for complex queries?**

Use query parameters: `?status=active&role=admin&sort=-createdAt&fields=name,email`. For complex filters: (1) JSON in query: `?filter={"age":{"$gt":18}}`. (2) Dedicated search endpoint: `POST /api/users/search`. (3) Query language like OData or GraphQL. Always validate and sanitize filter inputs.

### Advanced

**Q7: How do you handle concurrent updates (optimistic locking) in REST APIs?**

Use ETag header or version field. Client sends `If-Match: "etag-value"` on update. Server checks if resource has changed — returns 412 Precondition Failed if it has. Alternative: version number in body — reject if submitted version doesn't match current. Prevents lost updates in concurrent editing.

**Q8: Design a REST API that handles bulk operations efficiently.**

Options: (1) Batch endpoint: `POST /api/users/batch` with array body. (2) JSON Patch for bulk updates: `PATCH /api/users` with operations array. Return per-item results (207 Multi-Status). Implement transaction semantics (all-or-nothing vs partial success). Set size limits and use async processing for large batches.

**Q9: How would you implement cursor-based pagination for real-time data?**

Encode cursor as opaque token (base64 of `{id, timestamp}`). Query: `WHERE (created_at, id) > (cursor_timestamp, cursor_id) ORDER BY created_at, id LIMIT N+1`. Fetch N+1 to determine `hasNext`. Cursor pagination is stable under insertions/deletions unlike offset pagination. Use indexed columns for cursor fields.

---

## 🛠️ Hands-on Exercise

Build a complete REST API for a blog platform:
1. Users CRUD with role-based access
2. Posts CRUD with author relationship
3. Comments nested under posts
4. Pagination, filtering, and sorting
5. Input validation with Joi
6. Consistent error responses
