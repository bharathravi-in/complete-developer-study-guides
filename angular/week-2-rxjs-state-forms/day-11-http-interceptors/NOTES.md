# Day 11: HTTP & Interceptors in Angular 22+

## Table of Contents
1. [HttpClient Basics](#httpclient-basics)
2. [Functional Interceptors (HttpInterceptorFn)](#functional-interceptors)
3. [Authentication Token Injection](#authentication-token-injection)
4. [Global Error Handling](#global-error-handling)
5. [Retry Strategies with RxJS](#retry-strategies)
6. [Caching Interceptor](#caching-interceptor)
7. [Request/Response Transformation](#request-response-transformation)
8. [Timeout Handling](#timeout-handling)
9. [Loading Indicators](#loading-indicators)
10. [Quick Reference Card](#quick-reference-card)

---

## HttpClient Basics

### Setting Up HttpClient (Standalone)

```typescript
// app.config.ts
import { ApplicationConfig } from '@angular/core';
import { provideHttpClient, withInterceptors, withFetch } from '@angular/common/http';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withFetch(), // Use fetch API instead of XMLHttpRequest
      withInterceptors([/* interceptors */])
    )
  ]
};
```

### Core HTTP Methods

```typescript
// api.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface User {
  id: number;
  name: string;
  email: string;
}

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = '/api';

  // GET - Fetch data
  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(`${this.baseUrl}/users`);
  }

  // GET with query params
  getUsersWithParams(page: number, limit: number): Observable<User[]> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('limit', limit.toString());
    
    return this.http.get<User[]>(`${this.baseUrl}/users`, { params });
  }

  // GET single resource
  getUser(id: number): Observable<User> {
    return this.http.get<User>(`${this.baseUrl}/users/${id}`);
  }

  // POST - Create resource
  createUser(user: Omit<User, 'id'>): Observable<User> {
    return this.http.post<User>(`${this.baseUrl}/users`, user);
  }

  // PUT - Full update
  updateUser(id: number, user: User): Observable<User> {
    return this.http.put<User>(`${this.baseUrl}/users/${id}`, user);
  }

  // PATCH - Partial update
  patchUser(id: number, updates: Partial<User>): Observable<User> {
    return this.http.patch<User>(`${this.baseUrl}/users/${id}`, updates);
  }

  // DELETE - Remove resource
  deleteUser(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/users/${id}`);
  }
}
```

### Advanced Request Options

```typescript
// Custom headers
getWithHeaders(): Observable<User[]> {
  const headers = new HttpHeaders()
    .set('X-Custom-Header', 'value')
    .set('Accept', 'application/json');
  
  return this.http.get<User[]>(`${this.baseUrl}/users`, { headers });
}

// Observe full response (headers, status, body)
getFullResponse(): Observable<HttpResponse<User[]>> {
  return this.http.get<User[]>(`${this.baseUrl}/users`, {
    observe: 'response'
  });
}

// Get response as text
getAsText(): Observable<string> {
  return this.http.get(`${this.baseUrl}/text`, {
    responseType: 'text'
  });
}

// Get response as Blob (for file downloads)
downloadFile(): Observable<Blob> {
  return this.http.get(`${this.baseUrl}/file`, {
    responseType: 'blob'
  });
}

// Track upload/download progress
uploadWithProgress(file: File): Observable<HttpEvent<any>> {
  const formData = new FormData();
  formData.append('file', file);
  
  return this.http.post(`${this.baseUrl}/upload`, formData, {
    reportProgress: true,
    observe: 'events'
  });
}
```

### Using HttpClient in Components

```typescript
// users.component.ts
import { Component, inject, signal } from '@angular/core';
import { ApiService, User } from './api.service';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-users',
  standalone: true,
  template: `
    @if (loading()) {
      <p>Loading...</p>
    }
    @for (user of users(); track user.id) {
      <div>{{ user.name }} - {{ user.email }}</div>
    }
    @if (error()) {
      <p class="error">{{ error() }}</p>
    }
  `
})
export class UsersComponent {
  private readonly api = inject(ApiService);
  
  users = signal<User[]>([]);
  loading = signal(false);
  error = signal<string | null>(null);

  loadUsers(): void {
    this.loading.set(true);
    this.error.set(null);
    
    this.api.getUsers().subscribe({
      next: (users) => {
        this.users.set(users);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.message);
        this.loading.set(false);
      }
    });
  }
}
```

---

## Functional Interceptors (HttpInterceptorFn)

Angular 22+ uses functional interceptors instead of class-based ones. They are simpler, more composable, and tree-shakable.

### Basic Interceptor Structure

```typescript
// interceptors/logging.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';
import { tap } from 'rxjs';

export const loggingInterceptor: HttpInterceptorFn = (req, next) => {
  console.log(`[HTTP] ${req.method} ${req.url}`);
  const startTime = Date.now();
  
  return next(req).pipe(
    tap({
      next: (event) => {
        if (event.type === 4) { // HttpResponse
          console.log(`[HTTP] ${req.url} completed in ${Date.now() - startTime}ms`);
        }
      },
      error: (err) => {
        console.error(`[HTTP] ${req.url} failed:`, err);
      }
    })
  );
};
```

### Registering Interceptors

```typescript
// app.config.ts
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { loggingInterceptor } from './interceptors/logging.interceptor';
import { authInterceptor } from './interceptors/auth.interceptor';
import { errorInterceptor } from './interceptors/error.interceptor';
import { cacheInterceptor } from './interceptors/cache.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([
        // Order matters! First in array = first to process request, last to process response
        loggingInterceptor,
        authInterceptor,
        cacheInterceptor,
        errorInterceptor
      ])
    )
  ]
};
```

### Interceptor Execution Order

```
Request Flow:  logging → auth → cache → error → Server
Response Flow: Server → error → cache → auth → logging
```

---

## Authentication Token Injection

### Simple Auth Interceptor

```typescript
// interceptors/auth.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  const token = authService.getToken();
  
  // Skip auth for public endpoints
  if (req.url.includes('/public/') || req.url.includes('/auth/login')) {
    return next(req);
  }
  
  if (token) {
    const authReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });
    return next(authReq);
  }
  
  return next(req);
};
```

### Advanced Auth with Token Refresh

```typescript
// interceptors/auth-refresh.interceptor.ts
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { catchError, switchMap, throwError } from 'rxjs';

export const authRefreshInterceptor: HttpInterceptorFn = (req, next) => {
  const authService = inject(AuthService);
  
  return next(addToken(req, authService.getToken())).pipe(
    catchError((error: HttpErrorResponse) => {
      if (error.status === 401 && !req.url.includes('/auth/refresh')) {
        return authService.refreshToken().pipe(
          switchMap((newToken) => {
            return next(addToken(req, newToken));
          }),
          catchError((refreshError) => {
            authService.logout();
            return throwError(() => refreshError);
          })
        );
      }
      return throwError(() => error);
    })
  );
};

function addToken(req: any, token: string | null) {
  if (token) {
    return req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });
  }
  return req;
}
```

### Auth Service

```typescript
// services/auth.service.ts
import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap, BehaviorSubject } from 'rxjs';

interface TokenResponse {
  accessToken: string;
  refreshToken: string;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly tokenKey = 'auth_token';
  private readonly refreshTokenKey = 'refresh_token';
  
  private isRefreshing = false;
  private refreshSubject = new BehaviorSubject<string | null>(null);

  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  setTokens(tokens: TokenResponse): void {
    localStorage.setItem(this.tokenKey, tokens.accessToken);
    localStorage.setItem(this.refreshTokenKey, tokens.refreshToken);
  }

  refreshToken(): Observable<string> {
    const refreshToken = localStorage.getItem(this.refreshTokenKey);
    
    return this.http.post<TokenResponse>('/api/auth/refresh', { refreshToken }).pipe(
      tap((tokens) => this.setTokens(tokens)),
      switchMap((tokens) => of(tokens.accessToken))
    );
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    // Navigate to login
  }
}
```

---

## Global Error Handling

### Error Interceptor

```typescript
// interceptors/error.interceptor.ts
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { catchError, throwError } from 'rxjs';
import { NotificationService } from '../services/notification.service';
import { Router } from '@angular/router';

export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notification = inject(NotificationService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      let errorMessage = 'An unknown error occurred';

      if (error.error instanceof ErrorEvent) {
        // Client-side error
        errorMessage = `Client Error: ${error.error.message}`;
      } else {
        // Server-side error
        switch (error.status) {
          case 400:
            errorMessage = error.error?.message || 'Bad Request';
            break;
          case 401:
            errorMessage = 'Unauthorized. Please log in again.';
            router.navigate(['/login']);
            break;
          case 403:
            errorMessage = 'Access Denied';
            break;
          case 404:
            errorMessage = 'Resource not found';
            break;
          case 422:
            errorMessage = 'Validation Error';
            // Handle validation errors specially
            if (error.error?.errors) {
              return throwError(() => ({
                ...error,
                validationErrors: error.error.errors
              }));
            }
            break;
          case 500:
            errorMessage = 'Internal Server Error';
            break;
          case 503:
            errorMessage = 'Service Unavailable. Please try again later.';
            break;
          default:
            errorMessage = `Error ${error.status}: ${error.statusText}`;
        }
      }

      notification.showError(errorMessage);
      
      return throwError(() => ({
        message: errorMessage,
        status: error.status,
        originalError: error
      }));
    })
  );
};
```

### Custom Error Types

```typescript
// models/api-error.ts
export interface ApiError {
  message: string;
  status: number;
  code?: string;
  validationErrors?: ValidationError[];
  originalError?: any;
}

export interface ValidationError {
  field: string;
  message: string;
}

// Type guard
export function isApiError(error: unknown): error is ApiError {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'status' in error
  );
}
```

---

## Retry Strategies with RxJS

### Simple Retry Interceptor

```typescript
// interceptors/retry.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';
import { retry, timer } from 'rxjs';

export const retryInterceptor: HttpInterceptorFn = (req, next) => {
  // Only retry GET requests (idempotent)
  if (req.method !== 'GET') {
    return next(req);
  }

  return next(req).pipe(
    retry({
      count: 3,
      delay: (error, retryCount) => {
        // Don't retry client errors (4xx)
        if (error.status >= 400 && error.status < 500) {
          throw error;
        }
        // Exponential backoff: 1s, 2s, 4s
        const delay = Math.pow(2, retryCount - 1) * 1000;
        console.log(`Retry attempt ${retryCount} after ${delay}ms`);
        return timer(delay);
      }
    })
  );
};
```

### Advanced Retry with Conditions

```typescript
// interceptors/advanced-retry.interceptor.ts
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { retry, timer, throwError } from 'rxjs';

interface RetryConfig {
  maxRetries: number;
  retryableStatuses: number[];
  scalingDuration: number;
  excludedUrls: string[];
}

const defaultConfig: RetryConfig = {
  maxRetries: 3,
  retryableStatuses: [408, 500, 502, 503, 504],
  scalingDuration: 1000,
  excludedUrls: ['/auth/', '/upload/']
};

export const advancedRetryInterceptor: HttpInterceptorFn = (req, next) => {
  const config = defaultConfig;
  
  // Skip non-GET and excluded URLs
  if (req.method !== 'GET' || config.excludedUrls.some(url => req.url.includes(url))) {
    return next(req);
  }

  return next(req).pipe(
    retry({
      count: config.maxRetries,
      delay: (error: HttpErrorResponse, retryCount: number) => {
        // Check if error is retryable
        if (!config.retryableStatuses.includes(error.status)) {
          return throwError(() => error);
        }
        
        // Exponential backoff with jitter
        const baseDelay = config.scalingDuration * Math.pow(2, retryCount - 1);
        const jitter = Math.random() * 1000;
        const totalDelay = baseDelay + jitter;
        
        console.log(`[Retry] ${req.url} - Attempt ${retryCount}/${config.maxRetries} in ${totalDelay}ms`);
        
        return timer(totalDelay);
      }
    })
  );
};
```

### Configurable Retry via Request Context

```typescript
// utils/retry-context.ts
import { HttpContextToken, HttpContext } from '@angular/common/http';

export const RETRY_COUNT = new HttpContextToken<number>(() => 3);
export const RETRY_DELAY = new HttpContextToken<number>(() => 1000);

// Usage in service
getWithRetry(): Observable<Data> {
  return this.http.get<Data>('/api/data', {
    context: new HttpContext()
      .set(RETRY_COUNT, 5)
      .set(RETRY_DELAY, 2000)
  });
}

// Interceptor using context
export const contextAwareRetryInterceptor: HttpInterceptorFn = (req, next) => {
  const retryCount = req.context.get(RETRY_COUNT);
  const retryDelay = req.context.get(RETRY_DELAY);
  
  return next(req).pipe(
    retry({
      count: retryCount,
      delay: timer(retryDelay)
    })
  );
};
```

---

## Caching Interceptor

### In-Memory Cache Interceptor

```typescript
// interceptors/cache.interceptor.ts
import { HttpInterceptorFn, HttpResponse } from '@angular/common/http';
import { of, tap } from 'rxjs';

interface CacheEntry {
  response: HttpResponse<unknown>;
  timestamp: number;
}

const cache = new Map<string, CacheEntry>();
const DEFAULT_TTL = 5 * 60 * 1000; // 5 minutes

export const cacheInterceptor: HttpInterceptorFn = (req, next) => {
  // Only cache GET requests
  if (req.method !== 'GET') {
    // Invalidate cache on mutations
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method)) {
      invalidateRelatedCache(req.url);
    }
    return next(req);
  }

  const cacheKey = createCacheKey(req);
  const cached = cache.get(cacheKey);

  // Return cached response if valid
  if (cached && !isExpired(cached)) {
    console.log(`[Cache] HIT: ${req.url}`);
    return of(cached.response.clone());
  }

  console.log(`[Cache] MISS: ${req.url}`);
  
  return next(req).pipe(
    tap((event) => {
      if (event instanceof HttpResponse) {
        cache.set(cacheKey, {
          response: event.clone(),
          timestamp: Date.now()
        });
      }
    })
  );
};

function createCacheKey(req: any): string {
  const params = req.params.toString();
  return `${req.method}:${req.urlWithParams}`;
}

function isExpired(entry: CacheEntry): boolean {
  return Date.now() - entry.timestamp > DEFAULT_TTL;
}

function invalidateRelatedCache(url: string): void {
  const baseUrl = url.split('/').slice(0, -1).join('/');
  cache.forEach((_, key) => {
    if (key.includes(baseUrl)) {
      cache.delete(key);
    }
  });
}
```

### Cache with HTTP Context Control

```typescript
// utils/cache-context.ts
import { HttpContextToken, HttpContext } from '@angular/common/http';

export const CACHE_ENABLED = new HttpContextToken<boolean>(() => true);
export const CACHE_TTL = new HttpContextToken<number>(() => 5 * 60 * 1000);
export const SKIP_CACHE = new HttpContextToken<boolean>(() => false);

// Usage
// Skip cache for specific request
this.http.get('/api/data', {
  context: new HttpContext().set(SKIP_CACHE, true)
});

// Custom TTL
this.http.get('/api/config', {
  context: new HttpContext().set(CACHE_TTL, 60 * 60 * 1000) // 1 hour
});
```

### Advanced Cache Interceptor with Context

```typescript
// interceptors/advanced-cache.interceptor.ts
import { HttpInterceptorFn, HttpResponse, HttpContextToken } from '@angular/common/http';
import { of, tap, shareReplay } from 'rxjs';
import { CACHE_ENABLED, CACHE_TTL, SKIP_CACHE } from '../utils/cache-context';

interface CacheEntry {
  response: HttpResponse<unknown>;
  timestamp: number;
  ttl: number;
}

const cache = new Map<string, CacheEntry>();
const inFlightRequests = new Map<string, Observable<HttpEvent<unknown>>>();

export const advancedCacheInterceptor: HttpInterceptorFn = (req, next) => {
  if (req.method !== 'GET' || !req.context.get(CACHE_ENABLED) || req.context.get(SKIP_CACHE)) {
    return next(req);
  }

  const cacheKey = `${req.method}:${req.urlWithParams}`;
  const ttl = req.context.get(CACHE_TTL);
  const cached = cache.get(cacheKey);

  // Return cached if valid
  if (cached && Date.now() - cached.timestamp < cached.ttl) {
    return of(cached.response.clone());
  }

  // Deduplicate in-flight requests
  if (inFlightRequests.has(cacheKey)) {
    return inFlightRequests.get(cacheKey)!;
  }

  const request$ = next(req).pipe(
    tap({
      next: (event) => {
        if (event instanceof HttpResponse) {
          cache.set(cacheKey, {
            response: event.clone(),
            timestamp: Date.now(),
            ttl
          });
          inFlightRequests.delete(cacheKey);
        }
      },
      error: () => inFlightRequests.delete(cacheKey)
    }),
    shareReplay(1)
  );

  inFlightRequests.set(cacheKey, request$);
  return request$;
};
```

---

## Request/Response Transformation

### Content-Type Interceptor

```typescript
// interceptors/content-type.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';

export const contentTypeInterceptor: HttpInterceptorFn = (req, next) => {
  // Skip if content-type already set or is FormData
  if (req.headers.has('Content-Type') || req.body instanceof FormData) {
    return next(req);
  }

  // Set JSON content type for requests with body
  if (req.body) {
    const clonedReq = req.clone({
      setHeaders: {
        'Content-Type': 'application/json'
      }
    });
    return next(clonedReq);
  }

  return next(req);
};
```

### Request Transformation Interceptor

```typescript
// interceptors/transform-request.interceptor.ts
import { HttpInterceptorFn } from '@angular/common/http';

export const transformRequestInterceptor: HttpInterceptorFn = (req, next) => {
  // Add API version header
  let transformedReq = req.clone({
    setHeaders: {
      'X-API-Version': '2.0',
      'X-Client-ID': 'angular-app'
    }
  });

  // Transform snake_case body to camelCase (if needed)
  if (req.body && typeof req.body === 'object') {
    const transformedBody = transformKeys(req.body, snakeToCamel);
    transformedReq = transformedReq.clone({ body: transformedBody });
  }

  return next(transformedReq);
};

function snakeToCamel(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

function transformKeys(obj: any, transform: (key: string) => string): any {
  if (Array.isArray(obj)) {
    return obj.map(item => transformKeys(item, transform));
  }
  if (obj !== null && typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      acc[transform(key)] = transformKeys(obj[key], transform);
      return acc;
    }, {} as any);
  }
  return obj;
}
```

### Response Transformation Interceptor

```typescript
// interceptors/transform-response.interceptor.ts
import { HttpInterceptorFn, HttpResponse } from '@angular/common/http';
import { map } from 'rxjs';

export const transformResponseInterceptor: HttpInterceptorFn = (req, next) => {
  return next(req).pipe(
    map((event) => {
      if (event instanceof HttpResponse && event.body) {
        // Unwrap API envelope
        const unwrapped = unwrapApiResponse(event.body);
        
        // Transform dates
        const transformed = transformDates(unwrapped);
        
        return event.clone({ body: transformed });
      }
      return event;
    })
  );
};

function unwrapApiResponse(body: any): any {
  // If API wraps data in { data: ..., meta: ... }
  if (body && typeof body === 'object' && 'data' in body) {
    return body.data;
  }
  return body;
}

function transformDates(obj: any): any {
  if (obj === null || obj === undefined) return obj;
  
  if (typeof obj === 'string' && isISODateString(obj)) {
    return new Date(obj);
  }
  
  if (Array.isArray(obj)) {
    return obj.map(transformDates);
  }
  
  if (typeof obj === 'object') {
    return Object.keys(obj).reduce((acc, key) => {
      acc[key] = transformDates(obj[key]);
      return acc;
    }, {} as any);
  }
  
  return obj;
}

function isISODateString(str: string): boolean {
  return /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/.test(str);
}
```

---

## Timeout Handling

### Timeout Interceptor

```typescript
// interceptors/timeout.interceptor.ts
import { HttpInterceptorFn, HttpContextToken, HttpContext } from '@angular/common/http';
import { timeout, catchError, throwError } from 'rxjs';

export const REQUEST_TIMEOUT = new HttpContextToken<number>(() => 30000); // 30 seconds default

export const timeoutInterceptor: HttpInterceptorFn = (req, next) => {
  const timeoutMs = req.context.get(REQUEST_TIMEOUT);
  
  return next(req).pipe(
    timeout(timeoutMs),
    catchError((error) => {
      if (error.name === 'TimeoutError') {
        return throwError(() => ({
          message: `Request timed out after ${timeoutMs}ms`,
          status: 408,
          url: req.url,
          isTimeout: true
        }));
      }
      return throwError(() => error);
    })
  );
};

// Usage with custom timeout
this.http.get('/api/slow-endpoint', {
  context: new HttpContext().set(REQUEST_TIMEOUT, 60000) // 60 seconds
});
```

### Abort Controller for Cancellation

```typescript
// services/cancelable-http.service.ts
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject, takeUntil } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class CancelableHttpService {
  private readonly http = inject(HttpClient);
  private cancelSubject = new Subject<void>();

  get<T>(url: string): Observable<T> {
    return this.http.get<T>(url).pipe(
      takeUntil(this.cancelSubject)
    );
  }

  cancelAllRequests(): void {
    this.cancelSubject.next();
    this.cancelSubject.complete();
    this.cancelSubject = new Subject<void>();
  }
}
```

---

## Loading Indicators

### Loading State Service

```typescript
// services/loading.service.ts
import { Injectable, signal, computed } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class LoadingService {
  private activeRequests = signal(0);
  
  readonly isLoading = computed(() => this.activeRequests() > 0);
  readonly loadingCount = this.activeRequests.asReadonly();

  show(): void {
    this.activeRequests.update(count => count + 1);
  }

  hide(): void {
    this.activeRequests.update(count => Math.max(0, count - 1));
  }

  reset(): void {
    this.activeRequests.set(0);
  }
}
```

### Loading Interceptor

```typescript
// interceptors/loading.interceptor.ts
import { HttpInterceptorFn, HttpContextToken } from '@angular/common/http';
import { inject } from '@angular/core';
import { finalize } from 'rxjs';
import { LoadingService } from '../services/loading.service';

export const SKIP_LOADING = new HttpContextToken<boolean>(() => false);

export const loadingInterceptor: HttpInterceptorFn = (req, next) => {
  const loadingService = inject(LoadingService);
  
  // Skip loading indicator for specific requests
  if (req.context.get(SKIP_LOADING)) {
    return next(req);
  }

  loadingService.show();
  
  return next(req).pipe(
    finalize(() => loadingService.hide())
  );
};

// Usage - skip loading for background sync
this.http.get('/api/sync', {
  context: new HttpContext().set(SKIP_LOADING, true)
});
```

### Global Loading Component

```typescript
// components/global-loader.component.ts
import { Component, inject } from '@angular/core';
import { LoadingService } from '../services/loading.service';

@Component({
  selector: 'app-global-loader',
  standalone: true,
  template: `
    @if (loadingService.isLoading()) {
      <div class="global-loader-overlay">
        <div class="spinner"></div>
      </div>
    }
  `,
  styles: [`
    .global-loader-overlay {
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0, 0, 0, 0.3);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 9999;
    }
    .spinner {
      width: 50px;
      height: 50px;
      border: 3px solid #f3f3f3;
      border-top: 3px solid #3498db;
      border-radius: 50%;
      animation: spin 1s linear infinite;
    }
    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `]
})
export class GlobalLoaderComponent {
  loadingService = inject(LoadingService);
}
```

### Per-Request Loading with RxJS

```typescript
// Pattern for component-level loading
import { Component, signal } from '@angular/core';
import { finalize } from 'rxjs';

@Component({...})
export class DataComponent {
  loading = signal(false);
  data = signal<Data | null>(null);

  loadData(): void {
    this.loading.set(true);
    
    this.api.getData().pipe(
      finalize(() => this.loading.set(false))
    ).subscribe({
      next: (data) => this.data.set(data),
      error: (err) => console.error(err)
    });
  }
}
```

---

## Complete Interceptor Configuration

```typescript
// app.config.ts - Production-ready setup
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors, withFetch } from '@angular/common/http';

import { loggingInterceptor } from './interceptors/logging.interceptor';
import { authInterceptor } from './interceptors/auth.interceptor';
import { errorInterceptor } from './interceptors/error.interceptor';
import { retryInterceptor } from './interceptors/retry.interceptor';
import { cacheInterceptor } from './interceptors/cache.interceptor';
import { timeoutInterceptor } from './interceptors/timeout.interceptor';
import { loadingInterceptor } from './interceptors/loading.interceptor';
import { transformResponseInterceptor } from './interceptors/transform-response.interceptor';

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(
      withFetch(),
      withInterceptors([
        // Order: outer → inner for requests, inner → outer for responses
        loggingInterceptor,      // 1. Log all requests
        loadingInterceptor,      // 2. Show loading indicator
        authInterceptor,         // 3. Add auth token
        cacheInterceptor,        // 4. Check cache
        retryInterceptor,        // 5. Retry on failure
        timeoutInterceptor,      // 6. Enforce timeout
        transformResponseInterceptor, // 7. Transform response
        errorInterceptor         // 8. Handle errors (innermost)
      ])
    )
  ]
};
```

---

## Quick Reference Card

### HttpClient Methods Cheatsheet

| Method | Purpose | Return Type |
|--------|---------|-------------|
| `get<T>(url)` | Fetch data | `Observable<T>` |
| `post<T>(url, body)` | Create resource | `Observable<T>` |
| `put<T>(url, body)` | Full update | `Observable<T>` |
| `patch<T>(url, body)` | Partial update | `Observable<T>` |
| `delete<T>(url)` | Remove resource | `Observable<T>` |

### Request Options

```typescript
{
  headers: HttpHeaders,        // Custom headers
  params: HttpParams,          // Query parameters
  observe: 'body' | 'response' | 'events',  // What to observe
  responseType: 'json' | 'text' | 'blob' | 'arraybuffer',
  reportProgress: boolean,     // Track upload/download progress
  context: HttpContext,        // Pass data to interceptors
  withCredentials: boolean     // Include cookies in CORS
}
```

### Functional Interceptor Signature

```typescript
export const myInterceptor: HttpInterceptorFn = (req, next) => {
  // Modify request
  const modifiedReq = req.clone({ /* changes */ });
  
  // Pass to next handler and process response
  return next(modifiedReq).pipe(
    // RxJS operators for response
  );
};
```

### HttpContext Tokens

```typescript
// Define token
export const MY_TOKEN = new HttpContextToken<Type>(() => defaultValue);

// Use in request
http.get(url, {
  context: new HttpContext().set(MY_TOKEN, value)
});

// Read in interceptor
const value = req.context.get(MY_TOKEN);
```

### Common Interceptor Patterns

| Pattern | Purpose |
|---------|---------|
| Auth | Add Authorization header |
| Error | Global error handling |
| Retry | Automatic retry with backoff |
| Cache | Response caching |
| Loading | Show/hide loading indicator |
| Timeout | Request timeout |
| Transform | Modify request/response data |
| Logging | Debug and monitoring |

### provideHttpClient Options

```typescript
provideHttpClient(
  withFetch(),              // Use Fetch API
  withInterceptors([...]),  // Functional interceptors
  withInterceptorsFromDi(), // Class-based interceptors (legacy)
  withXsrfConfiguration({   // XSRF/CSRF protection
    cookieName: 'XSRF-TOKEN',
    headerName: 'X-XSRF-TOKEN'
  }),
  withNoXsrfProtection(),   // Disable XSRF
  withJsonpSupport(),       // JSONP support
  withRequestsMadeViaParent() // Use parent injector's HttpClient
)
```

### Error Types Quick Reference

| Status | Meaning | Action |
|--------|---------|--------|
| 400 | Bad Request | Show validation errors |
| 401 | Unauthorized | Redirect to login/refresh token |
| 403 | Forbidden | Show access denied |
| 404 | Not Found | Show not found message |
| 408 | Timeout | Retry or show timeout message |
| 422 | Validation Error | Display field errors |
| 500+ | Server Error | Show generic error, retry |

### RxJS Operators for HTTP

```typescript
import {
  retry,      // Retry failed requests
  timeout,    // Set request timeout
  catchError, // Handle errors
  tap,        // Side effects (logging)
  map,        // Transform response
  finalize,   // Cleanup (loading indicators)
  shareReplay,// Share response among subscribers
  switchMap,  // Cancel previous, use latest
  takeUntil   // Cancel on signal
} from 'rxjs';
```
