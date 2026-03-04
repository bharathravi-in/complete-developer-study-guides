# Day 19: Angular Security - Interview Questions & Answers

## Basic Level

### Q1: How does Angular protect against XSS attacks?

**Answer:**
Angular protects against XSS through automatic sanitization of values inserted into the DOM.

```typescript
// Angular automatically escapes dangerous values
@Component({
  template: `
    <!-- User input is escaped -->
    <div>{{ userInput }}</div>
    
    <!-- URLs are sanitized -->
    <a [href]="userUrl">Link</a>
    
    <!-- Styles are sanitized -->
    <div [style.color]="userColor">Text</div>
  `
})
export class SafeComponent {
  // These malicious values are neutralized
  userInput = '<script>alert("XSS")</script>';  // Rendered as text
  userUrl = 'javascript:alert("XSS")';  // Becomes 'unsafe:javascript:...'
  userColor = 'red; background-image: url(evil.com)';  // Style stripped
}
```

**Sanitization contexts:**
- HTML - escapes `<`, `>`, `&`
- URL - blocks `javascript:` protocol
- Style - removes dangerous properties
- Resource URLs - for `<iframe src>`, `<object data>`

---

### Q2: What is CSRF and how does Angular handle it?

**Answer:**
**CSRF (Cross-Site Request Forgery)** tricks authenticated users into making unwanted requests.

**Angular's Protection:**
```typescript
// 1. Server sets XSRF-TOKEN cookie
// 2. Angular automatically reads it
// 3. Angular sends X-XSRF-TOKEN header with requests
// 4. Server validates header matches cookie

// Configuration
import { provideHttpClient, withXsrfConfiguration } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withXsrfConfiguration({
        cookieName: 'XSRF-TOKEN',
        headerName: 'X-XSRF-TOKEN'
      })
    )
  ]
};
```

**Why it works:**
- Attackers can trigger requests but can't read cookies (same-origin policy)
- Without reading cookie, they can't set correct header
- Server rejects requests without matching header

---

### Q3: How do you implement route guards for authentication?

**Answer:**
```typescript
// auth.guard.ts
export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isAuthenticated()) {
    return true;
  }

  // Redirect to login with return URL
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url }
  });
};

// Routes
export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [authGuard]
  },
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.routes'),
    canActivate: [authGuard]
  }
];
```

---

## Intermediate Level

### Q4: When should you bypass Angular's sanitization?

**Answer:**
Only bypass sanitization when:
1. Content comes from a **trusted source** you control
2. You've **manually sanitized** the content
3. There's no other way to achieve the functionality

```typescript
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Component({
  template: `<div [innerHTML]="trustedHtml"></div>`
})
export class TrustedContentComponent {
  trustedHtml: SafeHtml;
  private sanitizer = inject(DomSanitizer);

  loadContent() {
    // Content from CMS you control
    const html = this.cmsService.getApprovedContent();
    this.trustedHtml = this.sanitizer.bypassSecurityTrustHtml(html);
  }
}
```

**Security Context Methods:**
| Method | Use Case |
|--------|----------|
| `bypassSecurityTrustHtml()` | innerHTML binding |
| `bypassSecurityTrustStyle()` | style binding |
| `bypassSecurityTrustUrl()` | href, src |
| `bypassSecurityTrustResourceUrl()` | iframe src |
| `bypassSecurityTrustScript()` | script (rare) |

⚠️ **Never bypass for user-provided content!**

---

### Q5: How do you implement JWT authentication with token refresh?

**Answer:**
```typescript
@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private accessToken: string | null = null;
  private refreshTokenTimer: any;

  login(credentials: Credentials): Observable<User> {
    return this.http.post<AuthResponse>('/api/auth/login', credentials).pipe(
      tap(response => {
        this.setTokens(response);
      }),
      map(r => r.user)
    );
  }

  private setTokens(response: AuthResponse) {
    this.accessToken = response.accessToken;
    // Refresh token is stored in httpOnly cookie by server
    
    // Schedule refresh before expiration
    const payload = this.decodeJwt(response.accessToken);
    const expiresIn = payload.exp * 1000 - Date.now();
    const refreshIn = expiresIn - 60000; // 1 minute before
    
    this.refreshTokenTimer = setTimeout(() => {
      this.refreshAccessToken().subscribe();
    }, refreshIn);
  }

  refreshAccessToken(): Observable<void> {
    return this.http.post<AuthResponse>('/api/auth/refresh', {}).pipe(
      tap(response => this.setTokens(response)),
      map(() => void 0),
      catchError(err => {
        this.logout();
        return throwError(() => err);
      })
    );
  }

  getToken(): string | null {
    return this.accessToken;
  }

  logout() {
    this.accessToken = null;
    clearTimeout(this.refreshTokenTimer);
    // Call server to invalidate refresh token
    this.http.post('/api/auth/logout', {}).subscribe();
  }
}
```

---

### Q6: How do you implement role-based access control?

**Answer:**
```typescript
// 1. Role Guard
export const roleGuard = (allowedRoles: string[]): CanActivateFn => {
  return () => {
    const auth = inject(AuthService);
    const router = inject(Router);
    
    const user = auth.currentUser();
    if (!user) {
      return router.createUrlTree(['/login']);
    }

    const hasRole = user.roles.some(r => allowedRoles.includes(r));
    return hasRole || router.createUrlTree(['/unauthorized']);
  };
};

// 2. Has Role Directive
@Directive({
  selector: '[appHasRole]',
  standalone: true
})
export class HasRoleDirective implements OnInit {
  @Input('appHasRole') roles!: string | string[];
  
  private templateRef = inject(TemplateRef<any>);
  private viewContainer = inject(ViewContainerRef);
  private auth = inject(AuthService);

  ngOnInit() {
    const requiredRoles = Array.isArray(this.roles) ? this.roles : [this.roles];
    const userRoles = this.auth.currentUser()?.roles || [];
    
    const hasRole = requiredRoles.some(r => userRoles.includes(r));
    
    if (hasRole) {
      this.viewContainer.createEmbeddedView(this.templateRef);
    }
  }
}

// Usage
@Component({
  template: `
    <button *appHasRole="'ADMIN'" (click)="deleteUser()">Delete</button>
    <button *appHasRole="['ADMIN', 'MANAGER']" (click)="editUser()">Edit</button>
  `
})
```

---

### Q7: How do you secure sensitive data in an Angular application?

**Answer:**

**1. Never store secrets in code:**
```typescript
// ❌ BAD - Secrets in code
const apiKey = 'sk_live_abc123';

// ✅ GOOD - Use environment or server-side
// Environment variables (still visible in bundle!)
const apiUrl = environment.apiUrl;

// Best - Keep secrets server-side
// Client only receives tokens from server
```

**2. Secure token storage:**
```typescript
// ❌ BAD - localStorage (accessible via XSS)
localStorage.setItem('token', token);

// ⚠️ OK - sessionStorage (clears on tab close)
sessionStorage.setItem('token', token);

// ✅ BEST - Memory (for access tokens)
@Injectable({ providedIn: 'root' })
export class TokenService {
  private accessToken: string | null = null;
  
  setToken(token: string) { this.accessToken = token; }
  getToken() { return this.accessToken; }
  clearToken() { this.accessToken = null; }
}

// ✅ BEST - httpOnly cookie (for refresh tokens)
// Server sets: Set-Cookie: refreshToken=xyz; HttpOnly; Secure; SameSite=Strict
```

**3. Clear sensitive data:**
```typescript
logout() {
  // Clear all sensitive data
  this.tokenService.clearToken();
  sessionStorage.clear();
  this.userSignal.set(null);
  
  // Navigate away
  this.router.navigate(['/login']);
}
```

---

## Advanced Level

### Q8: How do you implement Content Security Policy with Angular?

**Answer:**
```html
<!-- index.html -->
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  font-src 'self' https://fonts.gstatic.com;
  img-src 'self' data: https:;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
">
```

**Angular-specific considerations:**

```typescript
// 1. Use AOT compilation (default in production)
// - No eval() needed
// - No Function() needed
// - No 'unsafe-eval' required

// 2. Inline styles issue
// Angular may inject inline styles
// Solution: Use 'unsafe-inline' for styles OR nonces

// 3. For strict CSP with nonces:
// Server generates nonce per request
// index.html template: <script nonce="${NONCE}">

// 4. angular.json configuration for stricter builds
{
  "build": {
    "options": {
      "optimization": {
        "scripts": true,
        "styles": {
          "minify": true,
          "inlineCritical": false  // Avoid inline styles
        }
      }
    }
  }
}
```

---

### Q9: How do you handle auth interceptor with token refresh?

**Answer:**
```typescript
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const tokenService = inject(TokenService);
  
  // Skip auth for public endpoints
  if (isPublicUrl(req.url)) {
    return next(req);
  }

  // Add token if available
  const token = tokenService.getToken();
  if (token) {
    req = addToken(req, token);
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && !req.url.includes('/refresh')) {
        // Try to refresh token
        return handleTokenRefresh(req, next, auth, tokenService);
      }
      return throwError(() => error);
    })
  );
};

// Prevent multiple refresh calls
let isRefreshing = false;
let refreshSubject = new BehaviorSubject<string | null>(null);

function handleTokenRefresh(
  req: HttpRequest<any>, 
  next: HttpHandlerFn,
  auth: AuthService,
  tokenService: TokenService
): Observable<HttpEvent<any>> {
  if (isRefreshing) {
    // Wait for refresh to complete
    return refreshSubject.pipe(
      filter(token => token !== null),
      take(1),
      switchMap(token => next(addToken(req, token!)))
    );
  }

  isRefreshing = true;
  refreshSubject.next(null);

  return auth.refreshAccessToken().pipe(
    switchMap(() => {
      const newToken = tokenService.getToken()!;
      isRefreshing = false;
      refreshSubject.next(newToken);
      return next(addToken(req, newToken));
    }),
    catchError(err => {
      isRefreshing = false;
      auth.logout();
      return throwError(() => err);
    })
  );
}

function addToken(req: HttpRequest<any>, token: string): HttpRequest<any> {
  return req.clone({
    setHeaders: { Authorization: `Bearer ${token}` }
  });
}
```

---

### Q10: What are security best practices for Angular applications?

**Answer:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Security Best Practices                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. XSS PREVENTION                                                   │
│     • Never use innerHTML with user content                          │
│     • Never bypass sanitization for untrusted data                   │
│     • Use AOT compilation in production                              │
│     • Implement Content Security Policy                              │
│                                                                      │
│  2. AUTHENTICATION                                                   │
│     • Use short-lived access tokens (15-30 min)                     │
│     • Store refresh tokens in httpOnly cookies                       │
│     • Implement automatic token refresh                              │
│     • Clear all tokens on logout                                     │
│                                                                      │
│  3. AUTHORIZATION                                                    │
│     • Implement guards for all protected routes                      │
│     • Never trust client-side checks alone                           │
│     • Always validate permissions on server                          │
│     • Use least privilege principle                                  │
│                                                                      │
│  4. DATA PROTECTION                                                  │
│     • Use HTTPS everywhere                                           │
│     • Don't store secrets in frontend code                           │
│     • Validate all inputs client AND server side                     │
│     • Sanitize data before display                                   │
│                                                                      │
│  5. DEPENDENCIES                                                     │
│     • Run npm audit regularly                                        │
│     • Keep Angular and dependencies updated                          │
│     • Remove unused packages                                         │
│     • Review third-party code                                        │
│                                                                      │
│  6. HEADERS & COOKIES                                                │
│     • Set security headers (X-Frame-Options, etc.)                  │
│     • Use Secure and HttpOnly for sensitive cookies                  │
│     • Enable SameSite cookie attribute                               │
│     • Implement CORS properly                                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

```
Security Headers (Server-side):
───────────────────────────────
X-Frame-Options: DENY
X-Content-Type-Options: nosniff  
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
Referrer-Policy: strict-origin-when-cross-origin

Angular Security Functions:
───────────────────────────
DomSanitizer.bypassSecurityTrustHtml()
DomSanitizer.bypassSecurityTrustStyle()
DomSanitizer.bypassSecurityTrustUrl()
DomSanitizer.bypassSecurityTrustResourceUrl()

Guard Types:
────────────
CanActivate     - Can route be activated?
CanActivateChild - Can child routes be activated?
CanDeactivate   - Can leave current route?
CanMatch        - Can route be matched?
Resolve         - Pre-fetch data before activation

Token Storage Security:
───────────────────────
Access Token  → Memory (or short-lived sessionStorage)
Refresh Token → httpOnly cookie (server-set)
```
