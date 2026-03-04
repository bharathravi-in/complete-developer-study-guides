# Day 15: Authentication Patterns for APIs

## Authentication vs Authorization

| Concept | Question | Example |
|---------|----------|---------|
| **Authentication** (AuthN) | "Who are you?" | Login with username/password |
| **Authorization** (AuthZ) | "What can you do?" | Admin can delete; user can only read |

## Authentication Methods

### 1. API Keys

```http
# Header-based
GET /api/data
X-API-Key: sk_live_abc123def456

# Query parameter (less secure — shows in logs)
GET /api/data?api_key=sk_live_abc123def456
```

**Pros**: Simple, good for service-to-service
**Cons**: No user context, hard to rotate, can leak in URLs/logs

### 2. Bearer Token (JWT)

```http
GET /api/users/me
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

```typescript
// JWT structure: header.payload.signature
// Header
{ "alg": "RS256", "typ": "JWT" }

// Payload
{
  "sub": "user-123",
  "email": "bharath@example.com",
  "role": "admin",
  "iat": 1640995200,
  "exp": 1641081600,
  "iss": "auth.example.com",
  "aud": "api.example.com"
}

// Verification (Node.js)
import jwt from 'jsonwebtoken';

function verifyToken(token: string): JWTPayload {
  try {
    return jwt.verify(token, publicKey, {
      algorithms: ['RS256'],
      issuer: 'auth.example.com',
      audience: 'api.example.com',
    }) as JWTPayload;
  } catch (error) {
    if (error instanceof jwt.TokenExpiredError) {
      throw new AuthError('Token expired', 401);
    }
    throw new AuthError('Invalid token', 401);
  }
}
```

### 3. OAuth 2.0 Flows

```
Authorization Code Flow (Web apps — most secure):
┌──────┐    ┌────────────┐    ┌──────────┐
│Client│    │Auth Server  │    │API Server│
└──┬───┘    └──────┬─────┘    └────┬─────┘
   │  1. Redirect  │               │
   │──────────────>│               │
   │  2. Login     │               │
   │  3. Auth Code │               │
   │<──────────────│               │
   │  4. Code→Token│               │
   │──────────────>│               │
   │  5. Access Token              │
   │<──────────────│               │
   │  6. API Request + Token       │
   │──────────────────────────────>│
   │  7. Response                  │
   │<──────────────────────────────│

Client Credentials Flow (Machine-to-machine):
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=service-a
&client_secret=secret123
&scope=read:users
```

### 4. Session-Based Authentication

```typescript
// Server-side session
app.post('/login', async (req, res) => {
  const user = await authenticate(req.body);
  req.session.userId = user.id;
  req.session.role = user.role;
  res.json({ message: 'Logged in' });
});

// Session cookie sent automatically
// Set-Cookie: connect.sid=s%3Aabc123; HttpOnly; Secure; SameSite=Strict
```

| Aspect | Session | JWT |
|--------|---------|-----|
| State | Server-side | Stateless (client) |
| Revocation | Immediate (delete session) | Hard (need blocklist) |
| Scalability | Needs shared session store | Scales independently |
| CSRF Risk | Yes (cookie-based) | No (header-based) |
| XSS Risk | Lower (HttpOnly cookie) | Higher (stored in JS) |

## Access Token + Refresh Token Pattern

```typescript
// Token lifecycle
const ACCESS_TOKEN_TTL = '15m';  // Short-lived
const REFRESH_TOKEN_TTL = '7d';  // Long-lived

// Login → issue both tokens
app.post('/auth/login', async (req, res) => {
  const user = await authenticate(req.body);

  const accessToken = jwt.sign(
    { sub: user.id, role: user.role },
    privateKey,
    { expiresIn: ACCESS_TOKEN_TTL, algorithm: 'RS256' }
  );

  const refreshToken = crypto.randomUUID();
  await redis.set(
    `refresh:${refreshToken}`,
    JSON.stringify({ userId: user.id }),
    'EX', 7 * 24 * 3600
  );

  res.json({ accessToken, refreshToken });
});

// Refresh → issue new access token
app.post('/auth/refresh', async (req, res) => {
  const { refreshToken } = req.body;
  const data = await redis.get(`refresh:${refreshToken}`);

  if (!data) return res.status(401).json({ error: 'Invalid refresh token' });

  const { userId } = JSON.parse(data);
  const user = await db.users.findById(userId);

  // Rotate refresh token (one-time use)
  await redis.del(`refresh:${refreshToken}`);
  const newRefreshToken = crypto.randomUUID();
  await redis.set(`refresh:${newRefreshToken}`, data, 'EX', 7 * 24 * 3600);

  const accessToken = jwt.sign(
    { sub: user.id, role: user.role },
    privateKey,
    { expiresIn: ACCESS_TOKEN_TTL, algorithm: 'RS256' }
  );

  res.json({ accessToken, refreshToken: newRefreshToken });
});
```

## RBAC (Role-Based Access Control)

```typescript
type Role = 'admin' | 'editor' | 'viewer';
type Permission = 'users:read' | 'users:write' | 'users:delete' |
                  'posts:read' | 'posts:write' | 'posts:delete';

const rolePermissions: Record<Role, Permission[]> = {
  admin: ['users:read', 'users:write', 'users:delete', 'posts:read', 'posts:write', 'posts:delete'],
  editor: ['users:read', 'posts:read', 'posts:write'],
  viewer: ['users:read', 'posts:read'],
};

// Middleware
function requirePermission(...permissions: Permission[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    const userRole = req.user.role as Role;
    const userPerms = rolePermissions[userRole];
    const hasAll = permissions.every(p => userPerms.includes(p));

    if (!hasAll) {
      return res.status(403).json({
        error: 'Forbidden',
        required: permissions,
      });
    }
    next();
  };
}

// Usage
app.delete('/users/:id', requirePermission('users:delete'), deleteUser);
app.get('/users', requirePermission('users:read'), listUsers);
```

## Security Best Practices

```
1. Always use HTTPS
2. Store tokens securely:
   - Access tokens: Memory only (not localStorage)
   - Refresh tokens: HttpOnly, Secure, SameSite cookies
3. Use RS256 (asymmetric) over HS256 for JWT
4. Set short expiration for access tokens (15 min)
5. Rotate refresh tokens on use (one-time use)
6. Implement token revocation (blocklist in Redis)
7. Rate-limit auth endpoints aggressively
8. Use PKCE for OAuth public clients (SPA, mobile)
9. Never log tokens or send in URL parameters
10. Validate ALL JWT claims (iss, aud, exp, nbf)
```

## Key Takeaways

1. **JWT = stateless auth** — great for microservices, hard to revoke
2. **Session = stateful auth** — easy to revoke, needs shared store
3. **Access + Refresh token pattern** — best of both worlds
4. **OAuth 2.0 Authorization Code + PKCE** — standard for web/mobile
5. **RBAC/ABAC** — always authorize at the API layer, not just UI
