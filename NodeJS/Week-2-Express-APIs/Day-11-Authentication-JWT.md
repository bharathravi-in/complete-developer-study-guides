# Day 11: Authentication & Authorization (JWT, OAuth)

## 🎯 Learning Objectives
- Implement JWT-based authentication
- Understand OAuth 2.0 and social login
- Build role-based access control (RBAC)
- Secure authentication best practices

---

## 📚 JWT Authentication

### How JWT Works

```
┌──────────┐     POST /login       ┌──────────┐
│  Client  │ ──────────────────▶  │  Server  │
│          │  {email, password}    │          │
│          │                       │          │
│          │  ◀────────────────── │          │
│          │  { token: "eyJ..." } │          │
│          │                       │          │
│          │  GET /api/users       │          │
│          │ ──────────────────▶  │          │
│          │  Authorization:       │          │
│          │  Bearer eyJ...        │          │
│          │                       │          │
│          │  ◀────────────────── │          │
│          │  { data: [...] }     │          │
└──────────┘                       └──────────┘

JWT Structure: header.payload.signature
- Header: { "alg": "HS256", "typ": "JWT" }
- Payload: { "userId": "123", "role": "admin", "iat": 1234567890, "exp": 1234571490 }
- Signature: HMACSHA256(base64(header) + "." + base64(payload), secret)
```

### Implementation

```javascript
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

const JWT_SECRET = process.env.JWT_SECRET; // Use strong secret (min 256 bits)
const JWT_EXPIRES_IN = '15m';
const REFRESH_TOKEN_EXPIRES = '7d';

// Generate tokens
function generateTokens(user) {
  const accessToken = jwt.sign(
    { userId: user.id, role: user.role },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES_IN }
  );
  
  const refreshToken = jwt.sign(
    { userId: user.id, tokenVersion: user.tokenVersion },
    process.env.REFRESH_SECRET,
    { expiresIn: REFRESH_TOKEN_EXPIRES }
  );
  
  return { accessToken, refreshToken };
}

// Login endpoint
router.post('/auth/login', async (req, res) => {
  const { email, password } = req.body;
  
  const user = await User.findOne({ email }).select('+password');
  if (!user || !(await bcrypt.compare(password, user.password))) {
    return res.status(401).json({ error: { message: 'Invalid credentials' } });
  }
  
  const tokens = generateTokens(user);
  
  // Set refresh token in httpOnly cookie
  res.cookie('refreshToken', tokens.refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
  });
  
  res.json({ accessToken: tokens.accessToken, user: { id: user.id, name: user.name, role: user.role } });
});

// Refresh token endpoint
router.post('/auth/refresh', async (req, res) => {
  const refreshToken = req.cookies.refreshToken;
  if (!refreshToken) return res.status(401).json({ error: { message: 'No refresh token' } });
  
  try {
    const decoded = jwt.verify(refreshToken, process.env.REFRESH_SECRET);
    const user = await User.findById(decoded.userId);
    
    // Check token version (allows invalidation on password change)
    if (!user || user.tokenVersion !== decoded.tokenVersion) {
      return res.status(401).json({ error: { message: 'Token revoked' } });
    }
    
    const tokens = generateTokens(user);
    res.cookie('refreshToken', tokens.refreshToken, { httpOnly: true, secure: true, sameSite: 'strict' });
    res.json({ accessToken: tokens.accessToken });
  } catch (err) {
    return res.status(401).json({ error: { message: 'Invalid refresh token' } });
  }
});

// Logout
router.post('/auth/logout', (req, res) => {
  res.clearCookie('refreshToken');
  res.status(204).end();
});
```

### Authentication Middleware

```javascript
function authenticate(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: { message: 'Access token required' } });
  }
  
  const token = authHeader.split(' ')[1];
  
  try {
    const decoded = jwt.verify(token, JWT_SECRET);
    req.user = decoded; // { userId, role, iat, exp }
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return res.status(401).json({ error: { message: 'Token expired', code: 'TOKEN_EXPIRED' } });
    }
    return res.status(401).json({ error: { message: 'Invalid token' } });
  }
}

// Role-based authorization
function authorize(...roles) {
  return (req, res, next) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ error: { message: 'Insufficient permissions' } });
    }
    next();
  };
}

// Usage
router.get('/admin/users', authenticate, authorize('admin'), getUsers);
router.delete('/users/:id', authenticate, authorize('admin', 'moderator'), deleteUser);
```

---

## 🔐 OAuth 2.0 (Google Login Example)

```javascript
const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;

passport.use(new GoogleStrategy({
  clientID: process.env.GOOGLE_CLIENT_ID,
  clientSecret: process.env.GOOGLE_CLIENT_SECRET,
  callbackURL: '/api/auth/google/callback'
}, async (accessToken, refreshToken, profile, done) => {
  try {
    let user = await User.findOne({ googleId: profile.id });
    
    if (!user) {
      user = await User.create({
        googleId: profile.id,
        name: profile.displayName,
        email: profile.emails[0].value,
        avatar: profile.photos[0].value
      });
    }
    
    done(null, user);
  } catch (err) {
    done(err, null);
  }
}));

// Routes
router.get('/auth/google', passport.authenticate('google', { scope: ['profile', 'email'] }));

router.get('/auth/google/callback', 
  passport.authenticate('google', { session: false }),
  (req, res) => {
    const tokens = generateTokens(req.user);
    // Redirect to frontend with token
    res.redirect(`${process.env.FRONTEND_URL}/auth/callback?token=${tokens.accessToken}`);
  }
);
```

---

## 🛡️ Security Best Practices

```javascript
// 1. Password hashing (never store plain text)
const SALT_ROUNDS = 12;
const hash = await bcrypt.hash(password, SALT_ROUNDS);

// 2. Rate limit login attempts
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts
  message: { error: { message: 'Too many login attempts, try again in 15 minutes' } }
});
router.post('/auth/login', loginLimiter, loginHandler);

// 3. Helmet for security headers
const helmet = require('helmet');
app.use(helmet());

// 4. CORS configuration
const cors = require('cors');
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS?.split(','),
  credentials: true
}));

// 5. Input sanitization (prevent NoSQL injection)
const mongoSanitize = require('express-mongo-sanitize');
app.use(mongoSanitize());
```

---

## 🧪 Interview Questions

### Beginner

**Q1: How does JWT authentication work?**

Client sends credentials → Server verifies and returns a signed token → Client includes token in Authorization header for subsequent requests → Server verifies signature without database lookup. JWTs are stateless — the server doesn't store sessions. Token contains encoded user data (claims).

**Q2: What is the difference between authentication and authorization?**

Authentication: verifying identity (who you are) — login with credentials. Authorization: verifying permissions (what you can do) — checking roles/permissions after authentication. Authentication comes first; authorization depends on it.

**Q3: Where should you store JWT tokens on the client?**

Access tokens: in memory (JavaScript variable) — safest from XSS but lost on refresh. Refresh tokens: in httpOnly, secure, sameSite cookies — protected from JavaScript access. Never in localStorage (vulnerable to XSS). The httpOnly cookie approach is most secure.

### Intermediate

**Q4: What are the security risks of JWT and how to mitigate them?**

Risks: (1) No revocation (mitigate: short expiry + refresh tokens). (2) Token theft (mitigate: httpOnly cookies, short TTL). (3) Algorithm confusion attacks (mitigate: specify algorithm explicitly in verify). (4) Sensitive data in payload (it's base64, not encrypted). (5) Large token size (overhead per request).

**Q5: Explain the OAuth 2.0 authorization code flow.**

1. User clicks "Login with Google" → redirect to Google's auth page
2. User grants permission → Google redirects back with authorization code
3. Server exchanges code for access token (server-to-server, secure)
4. Server uses access token to fetch user profile from Google
5. Server creates session/JWT for the user
The code exchange prevents tokens from appearing in browser URL.

**Q6: How do you implement token refresh rotation?**

On refresh: issue both new access token AND new refresh token. Invalidate the old refresh token. If an old refresh token is used (replay attack), invalidate ALL tokens for that user (token family). Store refresh token hash in database with family ID for detection.

### Advanced

**Q7: Design a permission system that handles both RBAC and ABAC.**

RBAC: roles (admin, editor) with fixed permissions. ABAC: attribute-based (user.department === resource.department). Combine: assign roles for broad access, add policies for fine-grained rules. Implementation: permission middleware checks role first, then evaluates policy functions against request context and resource attributes.

**Q8: How would you implement secure password reset?**

1. User requests reset → generate cryptographically random token
2. Hash token and store with expiry (30 min) in database
3. Send unhashed token in email link (HTTPS only)
4. On reset: verify token hash matches, check expiry
5. Update password, invalidate token and all sessions
6. Rate limit reset requests, log attempts
Never: expose whether email exists, use predictable tokens, skip rate limiting.

**Q9: How do you handle authentication in a microservices architecture?**

Options: (1) API Gateway validates JWT, passes user context downstream. (2) Each service validates tokens independently (shared secret/public key). (3) Service mesh with mTLS for service-to-service auth. JWT is ideal — stateless, each service can verify without calling auth service. Use short-lived tokens with scopes per service.

---

## 🛠️ Hands-on Exercise

Build a complete auth system:
1. Registration with email verification
2. Login with JWT (access + refresh tokens)
3. Google OAuth social login
4. Role-based access control (admin, user, moderator)
5. Password reset flow
6. Token refresh rotation
7. Rate limiting on auth endpoints
