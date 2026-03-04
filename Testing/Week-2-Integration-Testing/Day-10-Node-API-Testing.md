# Day 10: Node.js API Testing

## 📚 Topics to Cover (3-4 hours)

---

## 1. Supertest for Express API Testing

```typescript
import request from 'supertest';
import app from '../app';

describe('Users API', () => {
  describe('GET /api/users', () => {
    it('should return all users', async () => {
      const response = await request(app)
        .get('/api/users')
        .set('Authorization', 'Bearer test-token')
        .expect('Content-Type', /json/)
        .expect(200);

      expect(response.body).toHaveLength(3);
      expect(response.body[0]).toHaveProperty('name');
    });

    it('should paginate results', async () => {
      const response = await request(app)
        .get('/api/users?page=1&limit=10')
        .expect(200);

      expect(response.body.data).toHaveLength(10);
      expect(response.body.pagination).toEqual({
        page: 1, limit: 10, total: 50, pages: 5
      });
    });

    it('should filter by role', async () => {
      const response = await request(app)
        .get('/api/users?role=admin')
        .expect(200);

      response.body.forEach(user => {
        expect(user.role).toBe('admin');
      });
    });
  });

  describe('POST /api/users', () => {
    it('should create a new user', async () => {
      const newUser = { name: 'John', email: 'john@test.com', role: 'user' };

      const response = await request(app)
        .post('/api/users')
        .send(newUser)
        .expect(201);

      expect(response.body.id).toBeDefined();
      expect(response.body.name).toBe('John');
    });

    it('should validate required fields', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({}) // missing required fields
        .expect(400);

      expect(response.body.errors).toContainEqual(
        expect.objectContaining({ field: 'name', message: 'Name is required' })
      );
    });

    it('should reject duplicate email', async () => {
      await request(app)
        .post('/api/users')
        .send({ name: 'A', email: 'dup@test.com' })
        .expect(201);

      const response = await request(app)
        .post('/api/users')
        .send({ name: 'B', email: 'dup@test.com' })
        .expect(409);

      expect(response.body.message).toContain('already exists');
    });
  });

  describe('PUT /api/users/:id', () => {
    it('should update user', async () => {
      const response = await request(app)
        .put('/api/users/1')
        .send({ name: 'Updated Name' })
        .expect(200);

      expect(response.body.name).toBe('Updated Name');
    });

    it('should return 404 for non-existent user', async () => {
      await request(app)
        .put('/api/users/99999')
        .send({ name: 'Test' })
        .expect(404);
    });
  });

  describe('DELETE /api/users/:id', () => {
    it('should delete user', async () => {
      await request(app).delete('/api/users/1').expect(204);
      await request(app).get('/api/users/1').expect(404);
    });
  });
});
```

---

## 2. Testing Middleware

```typescript
describe('Auth Middleware', () => {
  it('should allow request with valid token', async () => {
    const token = generateTestToken({ userId: 1, role: 'admin' });

    await request(app)
      .get('/api/protected')
      .set('Authorization', `Bearer ${token}`)
      .expect(200);
  });

  it('should reject request without token', async () => {
    await request(app)
      .get('/api/protected')
      .expect(401);
  });

  it('should reject expired token', async () => {
    const token = generateTestToken({ userId: 1 }, { expiresIn: '-1h' });

    const response = await request(app)
      .get('/api/protected')
      .set('Authorization', `Bearer ${token}`)
      .expect(401);

    expect(response.body.message).toContain('expired');
  });
});

describe('Rate Limiter Middleware', () => {
  it('should allow requests within limit', async () => {
    for (let i = 0; i < 10; i++) {
      await request(app).get('/api/data').expect(200);
    }
  });

  it('should block requests exceeding limit', async () => {
    for (let i = 0; i < 100; i++) {
      await request(app).get('/api/data');
    }
    await request(app).get('/api/data').expect(429);
  });
});

describe('Error Handler Middleware', () => {
  it('should return 500 for unhandled errors', async () => {
    const response = await request(app)
      .get('/api/trigger-error')
      .expect(500);

    expect(response.body).toEqual({
      error: 'Internal Server Error',
      message: expect.any(String),
    });
  });
});
```

---

## 3. Database Integration Testing

```typescript
import { setupTestDB, teardownTestDB, clearDB } from '../test-helpers/db';

describe('User Repository', () => {
  beforeAll(async () => {
    await setupTestDB(); // Create test database
  });

  beforeEach(async () => {
    await clearDB(); // Clean all tables
    await seedTestData(); // Insert test data
  });

  afterAll(async () => {
    await teardownTestDB();
  });

  it('should find user by email', async () => {
    const user = await userRepo.findByEmail('john@test.com');
    expect(user).toBeDefined();
    expect(user.name).toBe('John');
  });

  it('should create user with hashed password', async () => {
    const user = await userRepo.create({
      name: 'Jane',
      email: 'jane@test.com',
      password: 'plaintext123'
    });

    expect(user.password).not.toBe('plaintext123');
    expect(await bcrypt.compare('plaintext123', user.password)).toBe(true);
  });

  it('should handle transactions', async () => {
    const result = await userRepo.transferCredits(1, 2, 100);

    const sender = await userRepo.findById(1);
    const receiver = await userRepo.findById(2);

    expect(sender.credits).toBe(900);   // was 1000
    expect(receiver.credits).toBe(1100); // was 1000
  });
});
```

---

## 4. FastAPI Testing (Python)

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestUsersAPI:
    def test_create_user(self):
        response = client.post("/api/users", json={
            "name": "John",
            "email": "john@test.com"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "John"
        assert "id" in data

    def test_get_users(self):
        response = client.get("/api/users")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_authentication_required(self):
        response = client.get("/api/protected")
        assert response.status_code == 401

    def test_with_auth(self):
        token = create_test_token()
        response = client.get(
            "/api/protected",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
```

---

## 🎯 Interview Questions

### Q1: How do you test APIs without hitting a real database?
**A:** Three approaches: (1) Mock the database layer (unit tests), (2) Use test database with setup/teardown (integration), (3) Use in-memory databases like SQLite. For Node.js, mock Prisma/TypeORM. For Python, use test fixtures with database transactions that rollback.

### Q2: How do you test file upload endpoints?
**A:** Use Supertest's `.attach()` for Node.js or TestClient with `UploadFile` for FastAPI. Create test files in fixtures, send multipart form data, verify the file was processed correctly, and clean up in afterEach.

### Q3: How do you handle test data isolation?
**A:** Use transactions that rollback after each test, or truncate tables in beforeEach. Use factories (factory-bot pattern) for creating test data. Never rely on shared mutable state between tests.
