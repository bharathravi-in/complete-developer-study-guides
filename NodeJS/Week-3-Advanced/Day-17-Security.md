# Day 17: Security Best Practices

## 🎯 Learning Objectives
- Prevent OWASP Top 10 vulnerabilities
- Implement security headers and CORS
- Handle input validation and sanitization
- Secure dependencies and secrets management

---

## 📚 OWASP Top 10 in Node.js

### 1. Injection (SQL/NoSQL/Command)

```javascript
// ❌ SQL Injection
const query = `SELECT * FROM users WHERE email = '${email}'`; // NEVER!

// ✅ Parameterized queries
const { rows } = await pool.query('SELECT * FROM users WHERE email = $1', [email]);

// ❌ NoSQL Injection
const user = await User.findOne({ email: req.body.email }); // If email = { $ne: "" } → returns first user!

// ✅ Sanitize input
const mongoSanitize = require('express-mongo-sanitize');
app.use(mongoSanitize()); // Strips $ and . from req.body/query/params

// ❌ Command Injection
const { exec } = require('child_process');
exec(`convert ${req.body.filename} output.png`); // filename could be "; rm -rf /"

// ✅ Use execFile (no shell) + validate input
const { execFile } = require('child_process');
const allowedPattern = /^[a-zA-Z0-9._-]+$/;
if (!allowedPattern.test(filename)) throw new Error('Invalid filename');
execFile('convert', [filename, 'output.png']);
```

### 2. Broken Authentication

```javascript
// ✅ Password hashing (never store plain text)
const bcrypt = require('bcrypt');
const SALT_ROUNDS = 12; // Minimum 10, adjust for your hardware

// ✅ Rate limit login attempts
const rateLimit = require('express-rate-limit');
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  skipSuccessfulRequests: true,
  message: { error: 'Too many login attempts' }
});

// ✅ Timing-safe comparison (prevent timing attacks)
const crypto = require('crypto');
function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  return crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));
}

// ✅ Account lockout after N failures
// ✅ Multi-factor authentication for sensitive operations
// ✅ Session invalidation on password change
```

### 3. XSS Prevention

```javascript
// ✅ Encode output (Content-Type header)
res.setHeader('Content-Type', 'application/json'); // JSON APIs are largely safe

// ✅ Sanitize HTML input (if storing/rendering user HTML)
const createDOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');
const DOMPurify = createDOMPurify(new JSDOM('').window);
const clean = DOMPurify.sanitize(userInput);

// ✅ Content Security Policy header
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", 'data:', 'https:'],
  }
}));
```

---

## 🔒 Security Headers (Helmet)

```javascript
const helmet = require('helmet');
app.use(helmet()); // Sets all recommended headers

// What helmet sets:
// X-Content-Type-Options: nosniff
// X-Frame-Options: DENY
// X-XSS-Protection: 0 (deprecated, CSP is better)
// Strict-Transport-Security: max-age=15552000; includeSubDomains
// Content-Security-Policy: ...
// Referrer-Policy: no-referrer
// X-DNS-Prefetch-Control: off
```

### CORS Configuration

```javascript
const cors = require('cors');

// ❌ Allow everything (development only)
app.use(cors());

// ✅ Production CORS
app.use(cors({
  origin: (origin, callback) => {
    const allowedOrigins = process.env.ALLOWED_ORIGINS.split(',');
    if (!origin || allowedOrigins.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error('Not allowed by CORS'));
    }
  },
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true,
  maxAge: 86400 // Cache preflight for 24 hours
}));
```

---

## 🛡️ Input Validation & Sanitization

```javascript
const Joi = require('joi');
const xss = require('xss');

// Comprehensive validation schema
const createUserSchema = Joi.object({
  name: Joi.string().min(2).max(50).pattern(/^[a-zA-Z\s'-]+$/).required(),
  email: Joi.string().email().max(254).required(),
  password: Joi.string().min(8).max(128)
    .pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])/)
    .message('Password must contain uppercase, lowercase, number, and special character')
    .required(),
  age: Joi.number().integer().min(13).max(150),
  bio: Joi.string().max(500).custom((value) => xss(value)) // Sanitize HTML
}).options({ stripUnknown: true }); // Remove unknown fields

// Request size limits
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true, limit: '1mb' }));

// File upload validation
const multer = require('multer');
const upload = multer({
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB max
  fileFilter: (req, file, cb) => {
    const allowed = ['image/jpeg', 'image/png', 'image/webp'];
    if (allowed.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type'));
    }
  }
});
```

---

## 🔑 Secrets Management

```javascript
// ❌ Never commit secrets to code
const API_KEY = 'sk-12345'; // NEVER!

// ✅ Environment variables
const API_KEY = process.env.API_KEY;

// ✅ .env file for development (add to .gitignore!)
require('dotenv').config();

// ✅ Validate required env vars at startup
const requiredEnvVars = ['DATABASE_URL', 'JWT_SECRET', 'REDIS_URL'];
for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    console.error(`Missing required environment variable: ${envVar}`);
    process.exit(1);
  }
}

// ✅ Production: use secret managers (AWS Secrets Manager, Vault, GCP Secret Manager)
// ✅ Rotate secrets regularly
// ✅ Use different secrets per environment
```

---

## 🔍 Dependency Security

```bash
# Audit dependencies
npm audit
npm audit fix

# Check for known vulnerabilities
npx snyk test

# Keep dependencies updated
npx npm-check-updates -u

# Lock dependency versions
npm ci  # Uses lockfile exactly (for CI/CD)
```

```javascript
// Prevent prototype pollution
const safeJsonParse = (str) => {
  const obj = JSON.parse(str);
  if (obj.__proto__ || obj.constructor || obj.prototype) {
    throw new Error('Potential prototype pollution');
  }
  return obj;
};
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is SQL/NoSQL injection and how do you prevent it?**

Injection occurs when user input is treated as code/query syntax. SQL: using string concatenation in queries. NoSQL: objects with operators (`$ne`, `$gt`) in MongoDB queries. Prevention: parameterized queries (SQL), input sanitization (strip `$` operators), ORMs with built-in escaping, input validation.

**Q2: What is CORS and why is it needed?**

CORS (Cross-Origin Resource Sharing) controls which domains can make requests to your API from a browser. Browsers block cross-origin requests by default (Same-Origin Policy). CORS headers tell the browser which origins, methods, and headers are allowed. Without it, your API is only accessible from the same domain.

**Q3: What security headers should every API have?**

Essential: `Content-Type`, `Strict-Transport-Security` (force HTTPS), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy`. Use the `helmet` npm package which sets all recommended headers. Also: `Referrer-Policy`, `Permissions-Policy`.

### Intermediate

**Q4: How do you prevent brute force attacks on login endpoints?**

Multiple layers: (1) Rate limiting per IP (e.g., 5 attempts/15 min). (2) Account lockout after N failures. (3) CAPTCHA after 3 failures. (4) Exponentially increasing delays. (5) Monitor and alert on unusual patterns. (6) Use secure password hashing (bcrypt, argon2). (7) Implement MFA for sensitive accounts.

**Q5: What is prototype pollution and how do you prevent it in Node.js?**

Prototype pollution modifies `Object.prototype` through unsafe object merging (deep merge of user input). If `__proto__` or `constructor.prototype` is modified, it affects ALL objects. Prevention: freeze prototypes, use `Object.create(null)` for dictionaries, validate/strip `__proto__` from input, use Map instead of plain objects for user data.

**Q6: How do you securely store and manage API keys and secrets?**

Never in code or git. Development: `.env` files (gitignored). Production: cloud secret managers (AWS Secrets Manager, HashiCorp Vault). Principles: least privilege, rotation, audit logging, different secrets per environment, encrypt at rest. Validate all required secrets at startup.

### Advanced

**Q7: How would you implement a Content Security Policy for a Node.js application serving a SPA?**

Define allowed sources per resource type: `script-src 'self'` (no inline), `style-src 'self' 'unsafe-inline'` (CSS frameworks often need inline), `img-src 'self' data: https:`, `connect-src 'self' https://api.example.com`. Use nonces for inline scripts. Report violations with `report-uri`. Test with `Content-Security-Policy-Report-Only` first.

**Q8: Design a security audit pipeline for a Node.js CI/CD process.**

Pipeline stages: (1) Static analysis (ESLint security rules, Semgrep). (2) Dependency audit (`npm audit`, Snyk). (3) Secret scanning (git-secrets, truffleHog). (4) SAST (SonarQube). (5) Container scanning (Trivy). (6) DAST in staging (OWASP ZAP). Block deployments on critical findings. Regular penetration testing for high-value targets.

**Q9: How do you handle security in a multi-tenant Node.js application?**

Data isolation: separate schemas/databases per tenant, row-level security (RLS) in PostgreSQL. Auth: tenant-specific JWT claims, validate tenant context on every request. API: scope all queries to tenant ID (middleware). Secrets: per-tenant encryption keys. Monitoring: per-tenant rate limits, anomaly detection. Never trust client-provided tenant IDs.

---

## 🛠️ Hands-on Exercise

Security-harden an Express API:
1. Add helmet with custom CSP
2. Implement input validation + sanitization middleware
3. Add rate limiting (per IP and per user)
4. Secure authentication (bcrypt, timing-safe compare)
5. Add dependency audit to package.json scripts
6. Implement request logging for security monitoring
