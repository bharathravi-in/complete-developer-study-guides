# Day 19: Angular Security

## Overview

Security in Angular applications covers multiple layers: protecting against common web vulnerabilities, secure authentication, authorization, and data protection.

---

## Common Web Vulnerabilities

### 1. Cross-Site Scripting (XSS)

XSS attacks inject malicious scripts into web pages viewed by other users.

**Angular's Built-in Protection:**

```typescript
// Angular automatically sanitizes values bound to the DOM
@Component({
  template: `
    <!-- Safe: Angular escapes HTML -->
    <div>{{ userInput }}</div>
    
    <!-- Safe: Angular sanitizes href -->
    <a [href]="userProvidedUrl">Link</a>
    
    <!-- Safe: Angular sanitizes style -->
    <div [style.background]="userColor">Styled</div>
  `
})
export class SafeComponent {
  userInput = '<script>alert("XSS")</script>';  // Rendered as text
  userProvidedUrl = 'javascript:alert("XSS")';  // Sanitized
  userColor = 'red; background-image: url(evil.com)';  // Sanitized
}
```

**When bypassing sanitization (use with caution):**
```typescript
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Component({
  template: `<div [innerHTML]="trustedHtml"></div>`
})
export class TrustedHtmlComponent {
  trustedHtml: SafeHtml;
  
  private sanitizer = inject(DomSanitizer);

  setHtml(html: string) {
    // Only use for content you control/trust
    // NEVER use for user-provided content
    this.trustedHtml = this.sanitizer.bypassSecurityTrustHtml(html);
  }
}
```

**Security Contexts:**
```typescript
// Different bypass methods for different contexts
sanitizer.bypassSecurityTrustHtml(value);      // innerHTML
sanitizer.bypassSecurityTrustStyle(value);     // [style]
sanitizer.bypassSecurityTrustScript(value);    // script (rarely needed)
sanitizer.bypassSecurityTrustUrl(value);       // href, src
sanitizer.bypassSecurityTrustResourceUrl(value); // iframe src, object data
```

---

### 2. Cross-Site Request Forgery (CSRF/XSRF)

CSRF attacks trick authenticated users into performing unwanted actions.

**Protection with HttpClient:**
```typescript
// Angular's HttpClient automatically handles XSRF tokens
// When server sets cookie named XSRF-TOKEN
// Angular reads it and sends as X-XSRF-TOKEN header

// Custom XSRF configuration
import { provideHttpClient, withXsrfConfiguration } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withXsrfConfiguration({
        cookieName: 'MY-XSRF-TOKEN',  // Custom cookie name
        headerName: 'X-MY-XSRF-TOKEN' // Custom header name
      })
    )
  ]
};
```

**Server-side setup (Express example):**
```javascript
const csrf = require('csurf');
const cookieParser = require('cookie-parser');

app.use(cookieParser());
app.use(csrf({ cookie: { key: 'XSRF-TOKEN' } }));

// Set token in cookie for Angular to read
app.use((req, res, next) => {
  res.cookie('XSRF-TOKEN', req.csrfToken());
  next();
});
```

---

### 3. Content Security Policy (CSP)

CSP prevents XSS by restricting resource loading.

```html
<!-- index.html -->
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'nonce-${NONCE}';
               style-src 'self' 'unsafe-inline';
               img-src 'self' data: https:;
               font-src 'self' https://fonts.gstatic.com;
               connect-src 'self' https://api.example.com;">
```

**Angular specific CSP considerations:**
```typescript
// For AOT compilation (recommended)
// No special CSP config needed - all scripts are bundled

// For JIT compilation (development)
// Requires 'unsafe-eval' for template compilation
// NEVER use JIT in production

// Using nonces for inline scripts
// angular.json
{
  "projects": {
    "app": {
      "architect": {
        "build": {
          "options": {
            "index": {
              "input": "src/index.html",
              "output": "index.html"
            }
          }
        }
      }
    }
  }
}
```

---

## Authentication Patterns

### JWT Authentication

```typescript
// auth.service.ts
@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  
  private currentUser = signal<User | null>(null);
  private tokenExpiration = signal<Date | null>(null);
  
  isAuthenticated = computed(() => {
    const exp = this.tokenExpiration();
    return exp ? new Date() < exp : false;
  });

  login(credentials: LoginCredentials): Observable<AuthResponse> {
    return this.http.post<AuthResponse>('/api/auth/login', credentials).pipe(
      tap(response => {
        this.storeToken(response.accessToken);
        this.storeRefreshToken(response.refreshToken);
        this.currentUser.set(response.user);
        this.scheduleTokenRefresh();
      })
    );
  }

  private storeToken(token: string) {
    // Use memory for access token (more secure)
    const payload = this.decodeToken(token);
    this.tokenExpiration.set(new Date(payload.exp * 1000));
    
    // Store in memory only - NOT localStorage for access tokens
    this.accessToken = token;
  }

  private storeRefreshToken(token: string) {
    // Refresh token in httpOnly cookie (set by server)
    // Or if must use client storage, use secure methods
  }

  private decodeToken(token: string): JwtPayload {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(atob(base64));
  }

  refreshToken(): Observable<AuthResponse> {
    return this.http.post<AuthResponse>('/api/auth/refresh', {}).pipe(
      tap(response => {
        this.storeToken(response.accessToken);
        this.scheduleTokenRefresh();
      }),
      catchError(error => {
        this.logout();
        return throwError(() => error);
      })
    );
  }

  private scheduleTokenRefresh() {
    const exp = this.tokenExpiration();
    if (!exp) return;

    // Refresh 5 minutes before expiration
    const refreshTime = exp.getTime() - Date.now() - 5 * 60 * 1000;
    
    timer(refreshTime).pipe(
      switchMap(() => this.refreshToken())
    ).subscribe();
  }

  logout() {
    this.accessToken = null;
    this.currentUser.set(null);
    this.tokenExpiration.set(null);
    this.router.navigate(['/login']);
  }
}
```

### Auth Interceptor

```typescript
// auth.interceptor.ts
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const token = auth.getAccessToken();

  // Skip auth for public endpoints
  if (isPublicEndpoint(req.url)) {
    return next(req);
  }

  if (token) {
    req = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
  }

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401) {
        // Try to refresh token
        return auth.refreshToken().pipe(
          switchMap(() => {
            const newToken = auth.getAccessToken();
            const retryReq = req.clone({
              setHeaders: { Authorization: `Bearer ${newToken}` }
            });
            return next(retryReq);
          }),
          catchError(() => {
            auth.logout();
            return throwError(() => error);
          })
        );
      }
      return throwError(() => error);
    })
  );
};

function isPublicEndpoint(url: string): boolean {
  const publicUrls = ['/api/auth/login', '/api/auth/register', '/api/public'];
  return publicUrls.some(public => url.includes(public));
}
```

---

## Authorization & Route Guards

### Functional Guards

```typescript
// auth.guard.ts
export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isAuthenticated()) {
    return true;
  }

  // Store attempted URL for redirect after login
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url }
  });
};

// role.guard.ts
export const roleGuard = (allowedRoles: string[]): CanActivateFn => {
  return (route, state) => {
    const auth = inject(AuthService);
    const router = inject(Router);
    
    const user = auth.currentUser();
    
    if (!user) {
      return router.createUrlTree(['/login']);
    }

    const hasRole = user.roles.some(role => allowedRoles.includes(role));
    
    if (hasRole) {
      return true;
    }

    return router.createUrlTree(['/unauthorized']);
  };
};

// permission.guard.ts
export const permissionGuard = (permission: string): CanActivateFn => {
  return () => {
    const permissionService = inject(PermissionService);
    return permissionService.hasPermission(permission);
  };
};

// Routes configuration
export const routes: Routes = [
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [authGuard]
  },
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.routes'),
    canActivate: [authGuard, roleGuard(['ADMIN'])]
  },
  {
    path: 'reports',
    component: ReportsComponent,
    canActivate: [authGuard, permissionGuard('VIEW_REPORTS')]
  }
];
```

### Directive-based Authorization

```typescript
// has-permission.directive.ts
@Directive({
  selector: '[appHasPermission]',
  standalone: true
})
export class HasPermissionDirective implements OnInit {
  @Input('appHasPermission') permission!: string;
  
  private templateRef = inject(TemplateRef<any>);
  private viewContainer = inject(ViewContainerRef);
  private permissionService = inject(PermissionService);
  
  private hasView = false;

  ngOnInit() {
    const hasPermission = this.permissionService.hasPermission(this.permission);
    
    if (hasPermission && !this.hasView) {
      this.viewContainer.createEmbeddedView(this.templateRef);
      this.hasView = true;
    } else if (!hasPermission && this.hasView) {
      this.viewContainer.clear();
      this.hasView = false;
    }
  }
}

// Usage
@Component({
  template: `
    <button *appHasPermission="'DELETE_USER'" (click)="deleteUser()">
      Delete User
    </button>

    <div *appHasPermission="'VIEW_ANALYTICS'">
      <app-analytics-dashboard />
    </div>
  `
})
```

---

## Secure Data Handling

### Sensitive Data in Memory

```typescript
// Secure service for handling sensitive data
@Injectable({ providedIn: 'root' })
export class SecureDataService {
  // Don't expose sensitive data in signals/observables that persist
  private sensitiveData: Map<string, any> = new Map();

  storeSensitiveData(key: string, data: any) {
    this.sensitiveData.set(key, data);
  }

  getSensitiveData(key: string): any {
    return this.sensitiveData.get(key);
  }

  clearSensitiveData(key: string) {
    this.sensitiveData.delete(key);
  }

  clearAll() {
    this.sensitiveData.clear();
  }
}

// Clear on logout
@Injectable({ providedIn: 'root' })
export class AuthService {
  private secureData = inject(SecureDataService);

  logout() {
    this.secureData.clearAll();
    // Clear other sensitive state
    sessionStorage.clear();
    // Navigate to login
  }
}
```

### Input Validation

```typescript
// Validation service
@Injectable({ providedIn: 'root' })
export class ValidationService {
  
  sanitizeInput(input: string): string {
    // Remove potentially dangerous characters
    return input
      .replace(/[<>]/g, '')  // Remove angle brackets
      .replace(/javascript:/gi, '')  // Remove javascript: protocol
      .trim();
  }

  validateEmail(email: string): boolean {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  }

  validateUrl(url: string): boolean {
    try {
      const parsed = new URL(url);
      return ['http:', 'https:'].includes(parsed.protocol);
    } catch {
      return false;
    }
  }
}

// Form validation with sanitization
@Component({
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()">
      <input formControlName="name" (blur)="sanitizeField('name')">
      <input formControlName="website" type="url">
    </form>
  `
})
export class SecureFormComponent {
  private validation = inject(ValidationService);
  
  form = inject(FormBuilder).group({
    name: ['', [Validators.required, Validators.maxLength(100)]],
    website: ['', [this.urlValidator()]]
  });

  urlValidator(): ValidatorFn {
    return (control: AbstractControl) => {
      if (!control.value) return null;
      return this.validation.validateUrl(control.value) 
        ? null 
        : { invalidUrl: true };
    };
  }

  sanitizeField(fieldName: string) {
    const control = this.form.get(fieldName);
    if (control?.value) {
      control.setValue(this.validation.sanitizeInput(control.value));
    }
  }
}
```

---

## HTTP Security Headers

```typescript
// Security headers (implemented on server/proxy)
const securityHeaders = {
  // Prevent clickjacking
  'X-Frame-Options': 'DENY',
  
  // Prevent MIME type sniffing
  'X-Content-Type-Options': 'nosniff',
  
  // Enable XSS filter
  'X-XSS-Protection': '1; mode=block',
  
  // Control referrer information
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  
  // Content Security Policy
  'Content-Security-Policy': "default-src 'self'",
  
  // HTTP Strict Transport Security
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  
  // Permissions Policy
  'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
};
```

---

## Secure Communication

### HTTPS Enforcement

```typescript
// Redirect HTTP to HTTPS (server-side)
// Express example
app.use((req, res, next) => {
  if (req.headers['x-forwarded-proto'] !== 'https') {
    return res.redirect(`https://${req.headers.host}${req.url}`);
  }
  next();
});

// Angular service worker for HTTPS
// ngsw-config.json
{
  "assetGroups": [...],
  "dataGroups": [
    {
      "name": "api",
      "urls": ["https://api.example.com/**"],
      "cacheConfig": {
        "maxSize": 100,
        "maxAge": "1h",
        "strategy": "freshness"
      }
    }
  ]
}
```

### Secure API Communication

```typescript
// API service with security best practices
@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private baseUrl = environment.apiUrl;

  // All requests go through HTTPS
  private request<T>(method: string, endpoint: string, body?: any): Observable<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const options = {
      headers: new HttpHeaders({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }),
      withCredentials: true  // Include cookies for CSRF
    };

    switch (method) {
      case 'GET':
        return this.http.get<T>(url, options);
      case 'POST':
        return this.http.post<T>(url, body, options);
      case 'PUT':
        return this.http.put<T>(url, body, options);
      case 'DELETE':
        return this.http.delete<T>(url, options);
      default:
        throw new Error(`Unsupported method: ${method}`);
    }
  }
}
```

---

## Security Checklist

```
✅ XSS Prevention
   - Don't use innerHTML with user data
   - Never bypass sanitization for untrusted content
   - Use AOT compilation in production

✅ CSRF Protection
   - Enable XSRF token handling
   - Use same-site cookies
   - Validate origin header on server

✅ Authentication
   - Use short-lived access tokens
   - Implement token refresh
   - Store tokens securely (httpOnly cookies preferred)
   - Clear tokens on logout

✅ Authorization
   - Implement route guards
   - Use server-side authorization
   - Don't trust client-side checks alone

✅ Secure Communication
   - Use HTTPS everywhere
   - Implement proper CORS
   - Set security headers

✅ Input Validation
   - Validate on client AND server
   - Sanitize all user input
   - Use Content-Type headers

✅ Dependency Security
   - Keep dependencies updated
   - Audit with npm audit
   - Remove unused packages
```

---

## Summary

| Security Concern | Angular Solution |
|-----------------|------------------|
| XSS | Built-in sanitization, AOT |
| CSRF | HttpClient XSRF configuration |
| Authentication | JWT + Interceptors |
| Authorization | Route guards, directives |
| Secure Storage | Memory, httpOnly cookies |
| CSP | Meta tags, server headers |
