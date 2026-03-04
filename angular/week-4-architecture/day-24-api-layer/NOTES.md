# Day 24: API Layer Design

## Overview

A well-designed API layer provides a clean abstraction between your Angular application and backend services, handling communication, error handling, caching, and data transformation.

---

## API Service Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    API Layer Architecture                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Components/Services                                                 │
│        ↓                                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    FACADE LAYER                               │   │
│  │  • Simplified API for components                              │   │
│  │  • Combines multiple API calls                                │   │
│  │  • Handles caching decisions                                  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│        ↓                                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    API SERVICES                               │   │
│  │  • Domain-specific (UserApi, ProductApi)                      │   │
│  │  • DTO to Domain mapping                                      │   │
│  │  • Business-level error handling                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│        ↓                                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    HTTP CLIENT WRAPPER                        │   │
│  │  • Centralized configuration                                  │   │
│  │  • Request/response transformation                            │   │
│  │  • Retry logic                                                │   │
│  └──────────────────────────────────────────────────────────────┘   │
│        ↓                                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    INTERCEPTORS                               │   │
│  │  • Auth tokens                                                │   │
│  │  • Logging                                                    │   │
│  │  • Error handling                                             │   │
│  └──────────────────────────────────────────────────────────────┘   │
│        ↓                                                             │
│     HttpClient → Backend API                                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Base API Service

```typescript
// Configuration
export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
}

export const API_CONFIG = new InjectionToken<ApiConfig>('API_CONFIG');

// Base API service
@Injectable({ providedIn: 'root' })
export class BaseApiService {
  protected http = inject(HttpClient);
  protected config = inject(API_CONFIG);

  protected get<T>(endpoint: string, params?: HttpParams): Observable<T> {
    return this.http.get<T>(`${this.config.baseUrl}${endpoint}`, { params }).pipe(
      timeout(this.config.timeout),
      retry(this.config.retryAttempts),
      catchError(this.handleError.bind(this))
    );
  }

  protected post<T>(endpoint: string, body: any): Observable<T> {
    return this.http.post<T>(`${this.config.baseUrl}${endpoint}`, body).pipe(
      timeout(this.config.timeout),
      catchError(this.handleError.bind(this))
    );
  }

  protected put<T>(endpoint: string, body: any): Observable<T> {
    return this.http.put<T>(`${this.config.baseUrl}${endpoint}`, body).pipe(
      timeout(this.config.timeout),
      catchError(this.handleError.bind(this))
    );
  }

  protected patch<T>(endpoint: string, body: any): Observable<T> {
    return this.http.patch<T>(`${this.config.baseUrl}${endpoint}`, body).pipe(
      timeout(this.config.timeout),
      catchError(this.handleError.bind(this))
    );
  }

  protected delete<T>(endpoint: string): Observable<T> {
    return this.http.delete<T>(`${this.config.baseUrl}${endpoint}`).pipe(
      timeout(this.config.timeout),
      catchError(this.handleError.bind(this))
    );
  }

  protected handleError(error: HttpErrorResponse): Observable<never> {
    let apiError: ApiError;

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      apiError = {
        type: 'client',
        message: error.error.message,
        status: 0
      };
    } else {
      // Server-side error
      apiError = {
        type: 'server',
        message: error.error?.message || error.statusText,
        status: error.status,
        errors: error.error?.errors
      };
    }

    return throwError(() => apiError);
  }
}
```

---

## Domain-Specific API Services

```typescript
// User API service
@Injectable({ providedIn: 'root' })
export class UserApiService extends BaseApiService {
  private endpoint = '/users';

  getUsers(params?: UserQueryParams): Observable<PaginatedResponse<User>> {
    const httpParams = this.buildParams(params);
    return this.get<PaginatedResponse<UserDto>>(this.endpoint, httpParams).pipe(
      map(response => ({
        ...response,
        data: response.data.map(dto => this.mapToUser(dto))
      }))
    );
  }

  getUserById(id: string): Observable<User> {
    return this.get<UserDto>(`${this.endpoint}/${id}`).pipe(
      map(dto => this.mapToUser(dto))
    );
  }

  createUser(data: CreateUserRequest): Observable<User> {
    return this.post<UserDto>(this.endpoint, data).pipe(
      map(dto => this.mapToUser(dto))
    );
  }

  updateUser(id: string, data: UpdateUserRequest): Observable<User> {
    return this.put<UserDto>(`${this.endpoint}/${id}`, data).pipe(
      map(dto => this.mapToUser(dto))
    );
  }

  deleteUser(id: string): Observable<void> {
    return this.delete(`${this.endpoint}/${id}`);
  }

  // DTO to Domain mapping
  private mapToUser(dto: UserDto): User {
    return {
      id: dto.id,
      name: `${dto.first_name} ${dto.last_name}`,
      email: dto.email,
      role: dto.role_type,
      createdAt: new Date(dto.created_at),
      isActive: dto.status === 'active'
    };
  }

  private buildParams(params?: UserQueryParams): HttpParams {
    let httpParams = new HttpParams();
    if (params) {
      if (params.page) httpParams = httpParams.set('page', params.page.toString());
      if (params.limit) httpParams = httpParams.set('limit', params.limit.toString());
      if (params.sort) httpParams = httpParams.set('sort', params.sort);
      if (params.filter) httpParams = httpParams.set('filter', params.filter);
    }
    return httpParams;
  }
}
```

---

## HTTP Interceptors

### Auth Interceptor

```typescript
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

  return next(req);
};

function isPublicEndpoint(url: string): boolean {
  const publicPaths = ['/auth/login', '/auth/register', '/public'];
  return publicPaths.some(path => url.includes(path));
}
```

### Error Interceptor

```typescript
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notification = inject(NotificationService);
  const auth = inject(AuthService);
  const router = inject(Router);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      switch (error.status) {
        case 401:
          auth.logout();
          router.navigate(['/login']);
          notification.error('Session expired. Please login again.');
          break;
        case 403:
          notification.error('You do not have permission to perform this action.');
          break;
        case 404:
          notification.error('Resource not found.');
          break;
        case 422:
          // Validation errors - let the service handle
          break;
        case 500:
          notification.error('Server error. Please try again later.');
          break;
        default:
          notification.error('An unexpected error occurred.');
      }

      return throwError(() => error);
    })
  );
};
```

### Logging Interceptor

```typescript
export const loggingInterceptor: HttpInterceptorFn = (req, next) => {
  const logger = inject(LoggerService);
  const startTime = Date.now();

  return next(req).pipe(
    tap({
      next: (event) => {
        if (event instanceof HttpResponse) {
          const duration = Date.now() - startTime;
          logger.debug(`${req.method} ${req.url} - ${event.status} (${duration}ms)`);
        }
      },
      error: (error: HttpErrorResponse) => {
        const duration = Date.now() - startTime;
        logger.error(`${req.method} ${req.url} - ${error.status} (${duration}ms)`, error);
      }
    })
  );
};
```

### Retry Interceptor

```typescript
export const retryInterceptor: HttpInterceptorFn = (req, next) => {
  // Only retry GET requests
  if (req.method !== 'GET') {
    return next(req);
  }

  return next(req).pipe(
    retry({
      count: 3,
      delay: (error, retryCount) => {
        // Don't retry client errors (except timeout)
        if (error.status >= 400 && error.status < 500) {
          return throwError(() => error);
        }
        // Exponential backoff
        const delay = Math.pow(2, retryCount) * 1000;
        console.log(`Retrying ${req.url} in ${delay}ms (attempt ${retryCount})`);
        return timer(delay);
      }
    })
  );
};
```

### Caching Interceptor

```typescript
@Injectable({ providedIn: 'root' })
export class CacheService {
  private cache = new Map<string, { data: any; timestamp: number }>();
  private ttl = 5 * 60 * 1000; // 5 minutes

  get<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (!cached) return null;
    
    if (Date.now() - cached.timestamp > this.ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return cached.data as T;
  }

  set(key: string, data: any): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  clear(pattern?: string): void {
    if (pattern) {
      for (const key of this.cache.keys()) {
        if (key.includes(pattern)) {
          this.cache.delete(key);
        }
      }
    } else {
      this.cache.clear();
    }
  }
}

export const cacheInterceptor: HttpInterceptorFn = (req, next) => {
  const cache = inject(CacheService);

  // Only cache GET requests
  if (req.method !== 'GET') {
    // Invalidate cache for mutations
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(req.method)) {
      cache.clear(req.url.split('/')[3]); // Clear related resource cache
    }
    return next(req);
  }

  // Check cache
  const cached = cache.get<HttpResponse<any>>(req.url);
  if (cached) {
    return of(cached.clone());
  }

  return next(req).pipe(
    tap(event => {
      if (event instanceof HttpResponse) {
        cache.set(req.url, event);
      }
    })
  );
};
```

---

## Request/Response DTOs

```typescript
// Request DTOs
interface CreateUserRequest {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  roleId: number;
}

interface UpdateUserRequest {
  firstName?: string;
  lastName?: string;
  email?: string;
  roleId?: number;
}

interface UserQueryParams {
  page?: number;
  limit?: number;
  sort?: string;
  filter?: string;
  search?: string;
}

// Response DTOs (matching API format)
interface UserDto {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  role_type: string;
  status: 'active' | 'inactive';
  created_at: string;
  updated_at: string;
}

interface PaginatedResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}

interface ApiErrorResponse {
  message: string;
  errors?: Record<string, string[]>;
  code?: string;
}

// Domain models (used in app)
interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  createdAt: Date;
  isActive: boolean;
}
```

---

## API Facade

```typescript
@Injectable({ providedIn: 'root' })
export class UserFacade {
  private api = inject(UserApiService);
  private store = inject(UserStore);
  private notification = inject(NotificationService);

  // State exposure
  users = this.store.users;
  selectedUser = this.store.selectedUser;
  loading = this.store.loading;
  error = this.store.error;

  loadUsers(params?: UserQueryParams): void {
    this.store.setLoading(true);
    
    this.api.getUsers(params).subscribe({
      next: response => {
        this.store.setUsers(response.data);
        this.store.setPagination(response.meta);
      },
      error: error => {
        this.store.setError(error.message);
        this.notification.error('Failed to load users');
      },
      complete: () => this.store.setLoading(false)
    });
  }

  createUser(data: CreateUserRequest): Observable<User> {
    return this.api.createUser(data).pipe(
      tap(user => {
        this.store.addUser(user);
        this.notification.success('User created successfully');
      }),
      catchError(error => {
        this.notification.error(error.message);
        return throwError(() => error);
      })
    );
  }

  updateUser(id: string, data: UpdateUserRequest): Observable<User> {
    return this.api.updateUser(id, data).pipe(
      tap(user => {
        this.store.updateUser(user);
        this.notification.success('User updated successfully');
      }),
      catchError(error => {
        this.notification.error(error.message);
        return throwError(() => error);
      })
    );
  }

  deleteUser(id: string): Observable<void> {
    return this.api.deleteUser(id).pipe(
      tap(() => {
        this.store.removeUser(id);
        this.notification.success('User deleted successfully');
      }),
      catchError(error => {
        this.notification.error(error.message);
        return throwError(() => error);
      })
    );
  }
}
```

---

## Provider Configuration

```typescript
// app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withInterceptors([
        loggingInterceptor,
        authInterceptor,
        cacheInterceptor,
        retryInterceptor,
        errorInterceptor
      ])
    ),
    {
      provide: API_CONFIG,
      useValue: {
        baseUrl: environment.apiUrl,
        timeout: 30000,
        retryAttempts: 3
      }
    }
  ]
};
```

---

## Summary

| Layer | Responsibility |
|-------|---------------|
| Interceptors | Cross-cutting: auth, logging, errors |
| Base API | Common HTTP operations |
| Domain APIs | Resource-specific endpoints |
| DTOs | Data transformation |
| Facade | Simplified interface for components |
| Cache | Improve performance |
