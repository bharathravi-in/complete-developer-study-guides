# Day 11: HTTP & Interceptors - Interview Questions & Answers

## Question 1: Interceptor Execution Order

**Q: In Angular, when you have multiple HTTP interceptors, what is the order of execution for requests and responses? How would you ensure a logging interceptor always runs first?**

**A:**

Interceptors execute in a **chain pattern** - the order they're registered determines execution:

- **Request flow**: First interceptor → Last interceptor → Server
- **Response flow**: Server → Last interceptor → First interceptor

```typescript
// app.config.ts
provideHttpClient(
  withInterceptors([
    loggingInterceptor,  // 1st for request, last for response
    authInterceptor,     // 2nd for request, 2nd-to-last for response  
    cacheInterceptor,    // 3rd for request, 3rd-to-last for response
    errorInterceptor     // 4th for request, 1st for response
  ])
)
```

**Visual Flow:**
```
Request:  logging → auth → cache → error → [SERVER]
Response: [SERVER] → error → cache → auth → logging
```

To ensure logging runs first on requests and last on responses (capturing everything):

```typescript
// interceptors/logging.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';
import { tap, finalize } from 'rxjs';

export const loggingInterceptor: HttpInterceptorFn = (req, next) => {
  const startTime = performance.now();
  const requestId = crypto.randomUUID();
  
  console.log(`[${requestId}] → ${req.method} ${req.url}`);
  
  return next(req).pipe(
    tap({
      next: (event) => {
        if (event.type === 4) { // HttpResponse
          console.log(`[${requestId}] ← ${event.status} (${Math.round(performance.now() - startTime)}ms)`);
        }
      },
      error: (err) => {
        console.error(`[${requestId}] ✗ ${err.status} (${Math.round(performance.now() - startTime)}ms)`);
      }
    })
  );
};
```

**Key Point**: Place logging interceptor **first** in the array to ensure it wraps all other interceptors.

---

## Question 2: Authentication Interceptor with Token Refresh

**Q: How do you implement an authentication interceptor that automatically refreshes expired tokens without causing multiple refresh requests?**

**A:**

The challenge is preventing multiple concurrent refresh requests when several API calls fail with 401 simultaneously.

```typescript
// interceptors/auth.interceptor.ts
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, switchMap, throwError, BehaviorSubject, filter, take } from 'rxjs';
import { AuthService } from '../services/auth.service';

// Shared state for token refresh coordination
let isRefreshing = false;
const refreshTokenSubject = new BehaviorSubject<string | null>(null);

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  
  // Skip auth endpoints
  if (req.url.includes('/auth/')) {
    return next(req);
  }
  
  const token = authService.getAccessToken();
  const authReq = token ? addToken(req, token) : req;
  
  return next(authReq).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && !req.url.includes('/auth/refresh')) {
        return handleUnauthorized(req, next, authService);
      }
      return throwError(() => error);
    })
  );
};

function handleUnauthorized(req: any, next: any, authService: AuthService) {
  if (!isRefreshing) {
    isRefreshing = true;
    refreshTokenSubject.next(null);
    
    return authService.refreshToken().pipe(
      switchMap((newToken: string) => {
        isRefreshing = false;
        refreshTokenSubject.next(newToken);
        return next(addToken(req, newToken));
      }),
      catchError((err) => {
        isRefreshing = false;
        authService.logout();
        return throwError(() => err);
      })
    );
  }
  
  // Wait for the ongoing refresh to complete
  return refreshTokenSubject.pipe(
    filter((token): token is string => token !== null),
    take(1),
    switchMap((token) => next(addToken(req, token)))
  );
}

function addToken(req: any, token: string) {
  return req.clone({
    setHeaders: { Authorization: `Bearer ${token}` }
  });
}
```

**Key Mechanisms:**
1. **`isRefreshing` flag**: Prevents multiple refresh calls
2. **`BehaviorSubject`**: Queues waiting requests until new token arrives
3. **`filter` + `take(1)`**: Waiting requests resume once token is available

---

## Question 3: Retry Strategy with Exponential Backoff

**Q: Implement a retry interceptor that uses exponential backoff with jitter, only retries on specific status codes, and allows per-request configuration.**

**A:**

```typescript
// utils/retry-config.ts
import { HttpContextToken } from '@angular/common/http';

export interface RetryConfig {
  maxRetries: number;
  initialDelay: number;
  retryStatuses: number[];
}

export const RETRY_CONFIG = new HttpContextToken<Partial<RetryConfig>>(() => ({}));

// interceptors/retry.interceptor.ts
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { retry, timer, throwError } from 'rxjs';
import { RETRY_CONFIG, RetryConfig } from '../utils/retry-config';

const DEFAULT_CONFIG: RetryConfig = {
  maxRetries: 3,
  initialDelay: 1000,
  retryStatuses: [408, 429, 500, 502, 503, 504]
};

export const retryInterceptor: HttpInterceptorFn = (req, next) => {
  // Only retry idempotent methods
  if (!['GET', 'HEAD', 'OPTIONS'].includes(req.method)) {
    return next(req);
  }
  
  const customConfig = req.context.get(RETRY_CONFIG);
  const config = { ...DEFAULT_CONFIG, ...customConfig };
  
  return next(req).pipe(
    retry({
      count: config.maxRetries,
      delay: (error: HttpErrorResponse, retryCount: number) => {
        // Don't retry if status not in retryable list
        if (!config.retryStatuses.includes(error.status)) {
          return throwError(() => error);
        }
        
        // Exponential backoff with jitter
        const exponentialDelay = config.initialDelay * Math.pow(2, retryCount - 1);
        const jitter = Math.random() * 1000;
        const totalDelay = Math.min(exponentialDelay + jitter, 30000); // Max 30s
        
        console.log(`Retry ${retryCount}/${config.maxRetries} in ${Math.round(totalDelay)}ms`);
        return timer(totalDelay);
      }
    })
  );
};

// Usage with custom config
this.http.get('/api/flaky-endpoint', {
  context: new HttpContext().set(RETRY_CONFIG, {
    maxRetries: 5,
    initialDelay: 500,
    retryStatuses: [503]
  })
});
```

**Key Concepts:**
- **Exponential Backoff**: Delay doubles each retry (1s, 2s, 4s...)
- **Jitter**: Random delay prevents thundering herd
- **Status Code Filter**: Only retry transient failures
- **Max Cap**: Prevents excessive delays
- **Idempotent Only**: Don't retry POST/PUT/DELETE

---

## Question 4: Implementing a Caching Interceptor

**Q: How would you implement an HTTP cache interceptor that supports TTL, cache invalidation on mutations, and prevents duplicate in-flight requests?**

**A:**

```typescript
// interceptors/cache.interceptor.ts
import { HttpInterceptorFn, HttpResponse, HttpContextToken } from '@angular/common/http';
import { Observable, of, tap, shareReplay, finalize } from 'rxjs';

export const CACHE_TTL = new HttpContextToken<number>(() => 5 * 60 * 1000);
export const BYPASS_CACHE = new HttpContextToken<boolean>(() => false);

interface CacheEntry {
  response: HttpResponse<unknown>;
  expiry: number;
}

const cache = new Map<string, CacheEntry>();
const inFlight = new Map<string, Observable<any>>();

export const cacheInterceptor: HttpInterceptorFn = (req, next) => {
  // Handle cache invalidation for mutations
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method)) {
    invalidateCache(req.url);
    return next(req);
  }
  
  // Only cache GET requests
  if (req.method !== 'GET' || req.context.get(BYPASS_CACHE)) {
    return next(req);
  }
  
  const cacheKey = generateCacheKey(req);
  const ttl = req.context.get(CACHE_TTL);
  
  // Return cached response if valid
  const cached = cache.get(cacheKey);
  if (cached && cached.expiry > Date.now()) {
    return of(cached.response.clone());
  }
  
  // Return in-flight request if exists (deduplication)
  if (inFlight.has(cacheKey)) {
    return inFlight.get(cacheKey)!;
  }
  
  // Make request and cache
  const request$ = next(req).pipe(
    tap((event) => {
      if (event instanceof HttpResponse) {
        cache.set(cacheKey, {
          response: event.clone(),
          expiry: Date.now() + ttl
        });
      }
    }),
    finalize(() => inFlight.delete(cacheKey)),
    shareReplay(1)
  );
  
  inFlight.set(cacheKey, request$);
  return request$;
};

function generateCacheKey(req: any): string {
  return `${req.method}:${req.urlWithParams}`;
}

function invalidateCache(url: string): void {
  // Invalidate exact URL and related collection URLs
  const baseUrl = url.replace(/\/\d+$/, ''); // Remove ID suffix
  
  cache.forEach((_, key) => {
    if (key.includes(baseUrl)) {
      cache.delete(key);
    }
  });
}
```

**Key Features:**
1. **TTL Support**: Configurable via HttpContext
2. **In-flight Deduplication**: `shareReplay(1)` shares response among concurrent subscribers
3. **Smart Invalidation**: Mutations clear related cached entries
4. **Memory Cleanup**: `finalize` removes completed in-flight entries

---

## Question 5: Global Error Handling Strategy

**Q: Design a comprehensive error handling interceptor that handles different error types, shows user-friendly messages, and allows components to handle specific errors.**

**A:**

```typescript
// models/api-error.ts
export interface ApiError {
  message: string;
  status: number;
  code?: string;
  timestamp: Date;
  handled: boolean;
}

export const SUPPRESS_ERROR = new HttpContextToken<boolean>(() => false);

// interceptors/error.interceptor.ts
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { NotificationService } from '../services/notification.service';
import { Router } from '@angular/router';
import { SUPPRESS_ERROR, ApiError } from '../models/api-error';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notification = inject(NotificationService);
  const router = inject(Router);
  const suppressGlobalError = req.context.get(SUPPRESS_ERROR);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      const apiError = transformError(error);
      
      // Handle specific status codes
      switch (error.status) {
        case 401:
          if (!req.url.includes('/auth/')) {
            router.navigate(['/login'], { 
              queryParams: { returnUrl: router.url } 
            });
          }
          break;
          
        case 403:
          router.navigate(['/forbidden']);
          break;
          
        case 404:
          // Let components handle 404 for specific resources
          break;
          
        case 0:
          apiError.message = 'Network error. Please check your connection.';
          break;
      }
      
      // Show notification unless suppressed
      if (!suppressGlobalError && error.status >= 500) {
        notification.showError(apiError.message);
        apiError.handled = true;
      }
      
      return throwError(() => apiError);
    })
  );
};

function transformError(error: HttpErrorResponse): ApiError {
  const messages: Record<number, string> = {
    400: 'Invalid request. Please check your input.',
    401: 'Session expired. Please log in again.',
    403: 'You do not have permission for this action.',
    404: 'The requested resource was not found.',
    422: 'Validation failed. Please check your input.',
    429: 'Too many requests. Please wait and try again.',
    500: 'A server error occurred. Please try again later.',
    502: 'Service temporarily unavailable.',
    503: 'Service under maintenance. Please try again later.'
  };

  return {
    message: error.error?.message || messages[error.status] || 'An unexpected error occurred.',
    status: error.status,
    code: error.error?.code,
    timestamp: new Date(),
    handled: false
  };
}

// Usage - suppress global error to handle locally
this.http.get('/api/optional-feature', {
  context: new HttpContext().set(SUPPRESS_ERROR, true)
}).pipe(
  catchError((error: ApiError) => {
    // Handle locally
    console.log('Feature not available');
    return of(null);
  })
);
```

---

## Question 6: HttpInterceptorFn vs Class-Based Interceptors

**Q: What are the differences between functional interceptors (HttpInterceptorFn) and class-based interceptors? Why did Angular move to functional interceptors?**

**A:**

| Aspect | Class-Based (Legacy) | Functional (Angular 15+) |
|--------|---------------------|--------------------------|
| **Syntax** | Class with `intercept()` method | Simple function |
| **DI** | Constructor injection | `inject()` function |
| **Tree-shaking** | Harder to tree-shake | Fully tree-shakable |
| **Registration** | `HTTP_INTERCEPTORS` provider | `withInterceptors()` |
| **Boilerplate** | More verbose | Minimal |
| **Testing** | Mock class dependencies | Pure function testing |

**Class-Based (Legacy):**
```typescript
@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private authService: AuthService) {}
  
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.authService.getToken();
    const authReq = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });
    return next.handle(authReq);
  }
}

// Registration
providers: [
  { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
]
```

**Functional (Modern):**
```typescript
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.getToken();
  
  const authReq = req.clone({
    setHeaders: { Authorization: `Bearer ${token}` }
  });
  return next(authReq);
};

// Registration
provideHttpClient(withInterceptors([authInterceptor]))
```

**Why Angular Moved to Functional:**
1. **Standalone Components**: Aligns with standalone architecture
2. **Simpler Mental Model**: Just a function with `(req, next) => Observable`
3. **Better Composition**: Easy to create higher-order interceptors
4. **Reduced Bundle Size**: Tree-shaking removes unused interceptors
5. **Easier Testing**: No class instantiation needed

---

## Question 7: Request Deduplication

**Q: How do you prevent duplicate API calls when multiple components request the same data simultaneously?**

**A:**

```typescript
// services/dedupe-http.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, shareReplay, finalize } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class DedupeHttpService {
  private readonly http = inject(HttpClient);
  private readonly pending = new Map<string, Observable<any>>();

  get<T>(url: string): Observable<T> {
    if (this.pending.has(url)) {
      return this.pending.get(url) as Observable<T>;
    }

    const request$ = this.http.get<T>(url).pipe(
      shareReplay({ bufferSize: 1, refCount: true }),
      finalize(() => this.pending.delete(url))
    );

    this.pending.set(url, request$);
    return request$;
  }
}

// As an interceptor
const pendingRequests = new Map<string, Observable<any>>();

export const dedupeInterceptor: HttpInterceptorFn = (req, next) => {
  if (req.method !== 'GET') {
    return next(req);
  }

  const key = req.urlWithParams;
  
  if (pendingRequests.has(key)) {
    return pendingRequests.get(key)!;
  }

  const request$ = next(req).pipe(
    shareReplay(1),
    finalize(() => pendingRequests.delete(key))
  );

  pendingRequests.set(key, request$);
  return request$;
};
```

**Key Concepts:**
- **`shareReplay(1)`**: Multicasts response to all subscribers
- **`refCount: true`**: Auto-unsubscribe when all subscribers leave
- **`finalize`**: Cleanup map entry when request completes

---

## Question 8: Handling File Uploads with Progress

**Q: How do you implement file uploads with progress tracking in Angular?**

**A:**

```typescript
// services/upload.service.ts
import { Injectable, inject, signal } from '@angular/core';
import { HttpClient, HttpEvent, HttpEventType, HttpProgressEvent } from '@angular/common/http';
import { Observable, map, tap, catchError, throwError } from 'rxjs';

export interface UploadProgress {
  state: 'pending' | 'uploading' | 'done' | 'error';
  progress: number;
  response?: any;
  error?: string;
}

@Injectable({ providedIn: 'root' })
export class UploadService {
  private readonly http = inject(HttpClient);

  upload(file: File, url: string): Observable<UploadProgress> {
    const formData = new FormData();
    formData.append('file', file, file.name);

    return this.http.post(url, formData, {
      reportProgress: true,
      observe: 'events'
    }).pipe(
      map((event: HttpEvent<any>): UploadProgress => {
        switch (event.type) {
          case HttpEventType.Sent:
            return { state: 'pending', progress: 0 };
            
          case HttpEventType.UploadProgress:
            const progress = event.total 
              ? Math.round(100 * event.loaded / event.total)
              : 0;
            return { state: 'uploading', progress };
            
          case HttpEventType.Response:
            return { state: 'done', progress: 100, response: event.body };
            
          default:
            return { state: 'uploading', progress: 0 };
        }
      }),
      catchError((error) => throwError(() => ({
        state: 'error',
        progress: 0,
        error: error.message
      } as UploadProgress)))
    );
  }
}

// Component usage
@Component({
  template: `
    <input type="file" (change)="onFileSelected($event)">
    @if (uploadProgress(); as progress) {
      <div class="progress-bar">
        <div [style.width.%]="progress.progress"></div>
      </div>
      <span>{{ progress.state }} - {{ progress.progress }}%</span>
    }
  `
})
export class UploadComponent {
  private uploadService = inject(UploadService);
  uploadProgress = signal<UploadProgress | null>(null);

  onFileSelected(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) return;

    this.uploadService.upload(file, '/api/upload').subscribe({
      next: (progress) => this.uploadProgress.set(progress),
      error: (err) => this.uploadProgress.set(err)
    });
  }
}
```

---

## Question 9: HTTP Context Token Usage

**Q: What are HttpContext and HttpContextToken? How do they enable per-request configuration in interceptors?**

**A:**

`HttpContext` allows passing metadata to interceptors without modifying the request URL or headers.

```typescript
// Define context tokens
import { HttpContextToken, HttpContext } from '@angular/common/http';

// Token with default value
export const SKIP_AUTH = new HttpContextToken<boolean>(() => false);
export const CACHE_TTL = new HttpContextToken<number>(() => 60000);
export const RETRY_COUNT = new HttpContextToken<number>(() => 3);
export const SHOW_LOADER = new HttpContextToken<boolean>(() => true);

// Using in service
@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);

  // Normal request - uses all defaults
  getUsers(): Observable<User[]> {
    return this.http.get<User[]>('/api/users');
  }

  // Skip auth and caching
  getPublicData(): Observable<Data> {
    return this.http.get<Data>('/api/public', {
      context: new HttpContext()
        .set(SKIP_AUTH, true)
        .set(CACHE_TTL, 0)
    });
  }

  // Silent background sync
  backgroundSync(): Observable<void> {
    return this.http.post<void>('/api/sync', {}, {
      context: new HttpContext()
        .set(SHOW_LOADER, false)
        .set(RETRY_COUNT, 5)
    });
  }
}

// Reading in interceptors
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  if (req.context.get(SKIP_AUTH)) {
    return next(req);
  }
  // Add auth header...
};

export const cacheInterceptor: HttpInterceptorFn = (req, next) => {
  const ttl = req.context.get(CACHE_TTL);
  if (ttl === 0) {
    return next(req); // Skip cache
  }
  // Use ttl for caching...
};
```

**Benefits:**
- Type-safe with generics
- Default values via factory function
- Interceptors remain decoupled
- Clean API at call site

---

## Question 10: Testing HTTP Interceptors

**Q: How do you unit test a functional HTTP interceptor?**

**A:**

```typescript
// auth.interceptor.spec.ts
import { TestBed } from '@angular/core/testing';
import { HttpClient, provideHttpClient, withInterceptors } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { authInterceptor } from './auth.interceptor';
import { AuthService } from '../services/auth.service';

describe('AuthInterceptor', () => {
  let httpClient: HttpClient;
  let httpMock: HttpTestingController;
  let authServiceSpy: jasmine.SpyObj<AuthService>;

  beforeEach(() => {
    authServiceSpy = jasmine.createSpyObj('AuthService', ['getToken']);
    
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(withInterceptors([authInterceptor])),
        provideHttpClientTesting(),
        { provide: AuthService, useValue: authServiceSpy }
      ]
    });

    httpClient = TestBed.inject(HttpClient);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify(); // Verify no outstanding requests
  });

  it('should add Authorization header when token exists', () => {
    authServiceSpy.getToken.and.returnValue('test-token');

    httpClient.get('/api/users').subscribe();

    const req = httpMock.expectOne('/api/users');
    expect(req.request.headers.get('Authorization')).toBe('Bearer test-token');
    req.flush([]);
  });

  it('should not add header when token is null', () => {
    authServiceSpy.getToken.and.returnValue(null);

    httpClient.get('/api/users').subscribe();

    const req = httpMock.expectOne('/api/users');
    expect(req.request.headers.has('Authorization')).toBeFalse();
    req.flush([]);
  });

  it('should skip auth for public endpoints', () => {
    authServiceSpy.getToken.and.returnValue('token');

    httpClient.get('/api/public/data').subscribe();

    const req = httpMock.expectOne('/api/public/data');
    expect(req.request.headers.has('Authorization')).toBeFalse();
    req.flush({});
  });

  it('should handle 401 errors', () => {
    authServiceSpy.getToken.and.returnValue('expired-token');
    let errorResponse: any;

    httpClient.get('/api/protected').subscribe({
      error: (err) => errorResponse = err
    });

    const req = httpMock.expectOne('/api/protected');
    req.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });

    expect(errorResponse.status).toBe(401);
  });
});
```

---

## Question 11: withFetch() vs XMLHttpRequest

**Q: What is `withFetch()` in `provideHttpClient()` and when should you use it?**

**A:**

`withFetch()` switches HttpClient from `XMLHttpRequest` to the native **Fetch API**.

```typescript
// Using Fetch API
provideHttpClient(withFetch())

// Using XMLHttpRequest (default)
provideHttpClient()
```

**Comparison:**

| Feature | XMLHttpRequest | Fetch API |
|---------|----------------|-----------|
| **Progress Events** | ✅ Full support | ⚠️ Upload only, no download progress |
| **Request Cancellation** | Via XMLHttpRequest.abort() | Via AbortController |
| **Streaming** | ❌ No | ✅ Yes (ReadableStream) |
| **SSR Compatibility** | ⚠️ Requires polyfill | ✅ Native in Node 18+ |
| **CORS** | Full support | Full support |
| **Timeout** | Built-in | Manual (AbortController + setTimeout) |

**When to Use withFetch():**
- Server-Side Rendering (Angular Universal)
- Modern browsers only
- Need streaming responses
- Don't need download progress

**When to Stick with XMLHttpRequest:**
- Need download progress tracking
- Supporting older browsers
- Need built-in timeout

```typescript
// SSR-ready configuration
export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withFetch(),        // Better SSR support
      withInterceptors([...])
    )
  ]
};
```

---

## Question 12: Implementing Request Timeout and Cancellation

**Q: How do you implement request timeout with automatic cancellation in Angular?**

**A:**

```typescript
// interceptors/timeout.interceptor.ts
import { HttpInterceptorFn, HttpContextToken } from '@angular/common/http';
import { timeout, catchError, throwError, race, timer, EMPTY } from 'rxjs';

export const REQUEST_TIMEOUT = new HttpContextToken<number>(() => 30000);
export const CANCEL_ON_NAVIGATION = new HttpContextToken<boolean>(() => false);

export const timeoutInterceptor: HttpInterceptorFn = (req, next) => {
  const timeoutMs = req.context.get(REQUEST_TIMEOUT);
  
  return next(req).pipe(
    timeout({
      each: timeoutMs,
      with: () => throwError(() => ({
        name: 'TimeoutError',
        message: `Request exceeded ${timeoutMs}ms timeout`,
        status: 408,
        url: req.url
      }))
    })
  );
};

// Service with manual cancellation
import { Injectable, inject, DestroyRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subject, takeUntil } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class CancellableApiService {
  private readonly http = inject(HttpClient);
  private readonly destroyRef = inject(DestroyRef);
  private cancelSubject = new Subject<void>();

  getData<T>(url: string): Observable<T> {
    return this.http.get<T>(url).pipe(
      takeUntil(this.cancelSubject),
      takeUntilDestroyed(this.destroyRef) // Auto-cancel on service destroy
    );
  }

  cancelAllRequests(): void {
    this.cancelSubject.next();
  }
}

// Component with auto-cancellation on destroy
@Component({...})
export class DataComponent {
  private destroyRef = inject(DestroyRef);
  private api = inject(ApiService);

  loadData(): void {
    this.api.getData('/api/data').pipe(
      takeUntilDestroyed(this.destroyRef) // Cancels when component destroys
    ).subscribe(data => {
      // Handle data
    });
  }
}

// Using AbortController directly (with withFetch())
async loadWithAbort(): Promise<void> {
  const controller = new AbortController();
  
  // Cancel after 5 seconds
  setTimeout(() => controller.abort(), 5000);
  
  try {
    const response = await fetch('/api/data', {
      signal: controller.signal
    });
    const data = await response.json();
  } catch (error) {
    if (error.name === 'AbortError') {
      console.log('Request was cancelled');
    }
  }
}
```

**Key Patterns:**
1. **`timeout()` operator**: RxJS-based timeout handling
2. **`takeUntilDestroyed()`**: Angular 16+ automatic cleanup
3. **`Subject` cancellation**: Manual cancel control
4. **`AbortController`**: Native Fetch cancellation

---

## Quick Reference: Interview Tips

### Key Points to Remember

1. **Interceptor Order**: First registered = first for request, last for response
2. **Functional > Class**: Prefer `HttpInterceptorFn` over class-based
3. **HttpContext**: Use for per-request configuration
4. **Error Handling**: Centralize but allow local override
5. **Retry**: Only idempotent requests, with exponential backoff
6. **Caching**: Invalidate on mutations, dedupe in-flight
7. **Token Refresh**: Prevent multiple refresh calls with BehaviorSubject

### Common Mistakes to Avoid

❌ Retrying POST/PUT/DELETE requests
❌ Forgetting to clone requests before modification
❌ Not handling token refresh race conditions
❌ Ignoring error status codes in retry logic
❌ Memory leaks from uncached in-flight requests
❌ Blocking UI without loading indicators

### Best Practices

✅ Use `inject()` for dependencies in functional interceptors
✅ Clone requests when modifying (`req.clone()`)
✅ Use HttpContext for interceptor configuration
✅ Implement proper error types and type guards
✅ Add jitter to retry delays
✅ Test interceptors with `HttpTestingController`
