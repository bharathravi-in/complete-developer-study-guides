# Day 24: API Layer Design - Interview Questions & Answers

## Basic Level

### Q1: How do you structure an API layer in Angular?

**Answer:**
```
API Layer Structure:
────────────────────
Components
    ↓
Facade (simplified interface)
    ↓
API Services (domain-specific)
    ↓
Base API Service (common methods)
    ↓
Interceptors (cross-cutting)
    ↓
HttpClient → Backend
```

```typescript
// Base API Service
@Injectable({ providedIn: 'root' })
export class BaseApiService {
  protected http = inject(HttpClient);
  protected baseUrl = environment.apiUrl;

  protected get<T>(endpoint: string): Observable<T> {
    return this.http.get<T>(`${this.baseUrl}${endpoint}`);
  }

  protected post<T>(endpoint: string, data: any): Observable<T> {
    return this.http.post<T>(`${this.baseUrl}${endpoint}`, data);
  }
}

// Domain API Service
@Injectable({ providedIn: 'root' })
export class UserApiService extends BaseApiService {
  getUsers(): Observable<User[]> {
    return this.get<UserDto[]>('/users').pipe(
      map(dtos => dtos.map(this.mapToUser))
    );
  }

  private mapToUser(dto: UserDto): User {
    return {
      id: dto.id,
      name: `${dto.first_name} ${dto.last_name}`,
      email: dto.email
    };
  }
}
```

---

### Q2: What is the purpose of DTOs?

**Answer:**
**Data Transfer Objects (DTOs)** represent the API contract separately from domain models:

```typescript
// DTO - matches API response format
interface UserDto {
  id: string;
  first_name: string;
  last_name: string;
  email_address: string;
  created_at: string;
  status: 'ACTIVE' | 'INACTIVE';
}

// Domain Model - clean for application use
interface User {
  id: string;
  name: string;
  email: string;
  createdAt: Date;
  isActive: boolean;
}

// Mapping function
function mapToUser(dto: UserDto): User {
  return {
    id: dto.id,
    name: `${dto.first_name} ${dto.last_name}`,
    email: dto.email_address,
    createdAt: new Date(dto.created_at),
    isActive: dto.status === 'ACTIVE'
  };
}
```

**Benefits:**
- Decouple app from API changes
- Transform naming conventions (snake_case → camelCase)
- Convert types (string dates → Date objects)
- Simplify data structure for components

---

### Q3: How do you implement an auth interceptor?

**Answer:**
```typescript
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const token = auth.getToken();

  // Skip for public endpoints
  if (isPublicUrl(req.url)) {
    return next(req);
  }

  // Add token to request
  if (token) {
    req = req.clone({
      setHeaders: { Authorization: `Bearer ${token}` }
    });
  }

  return next(req);
};

function isPublicUrl(url: string): boolean {
  const publicPaths = ['/auth/login', '/auth/register'];
  return publicPaths.some(path => url.includes(path));
}

// Register in app.config.ts
provideHttpClient(withInterceptors([authInterceptor]))
```

---

## Intermediate Level

### Q4: How do you handle API errors globally?

**Answer:**
```typescript
export const errorInterceptor: HttpInterceptorFn = (req, next) => {
  const notification = inject(NotificationService);
  const router = inject(Router);
  const auth = inject(AuthService);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {
      // Handle specific status codes
      switch (error.status) {
        case 401:
          auth.logout();
          router.navigate(['/login']);
          notification.error('Session expired');
          break;
          
        case 403:
          notification.error('Access denied');
          break;
          
        case 404:
          notification.error('Resource not found');
          break;
          
        case 422:
          // Validation errors - pass through for form handling
          break;
          
        case 500:
          notification.error('Server error');
          break;
          
        default:
          notification.error('Something went wrong');
      }

      // Re-throw for specific handling
      return throwError(() => error);
    })
  );
};
```

---

### Q5: How do you implement request caching?

**Answer:**
```typescript
@Injectable({ providedIn: 'root' })
export class CacheService {
  private cache = new Map<string, { data: any; expiry: number }>();
  private ttl = 5 * 60 * 1000; // 5 minutes

  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    if (!item) return null;
    if (Date.now() > item.expiry) {
      this.cache.delete(key);
      return null;
    }
    return item.data;
  }

  set(key: string, data: any): void {
    this.cache.set(key, {
      data,
      expiry: Date.now() + this.ttl
    });
  }

  invalidate(pattern: string): void {
    for (const key of this.cache.keys()) {
      if (key.includes(pattern)) {
        this.cache.delete(key);
      }
    }
  }
}

// Caching interceptor
export const cacheInterceptor: HttpInterceptorFn = (req, next) => {
  const cache = inject(CacheService);

  // Only cache GET requests
  if (req.method !== 'GET') {
    // Invalidate on mutations
    if (['POST', 'PUT', 'DELETE'].includes(req.method)) {
      const resource = req.url.split('/')[3];
      cache.invalidate(resource);
    }
    return next(req);
  }

  // Check cache
  const cached = cache.get(req.url);
  if (cached) {
    return of(new HttpResponse({ body: cached }));
  }

  // Fetch and cache
  return next(req).pipe(
    tap(event => {
      if (event instanceof HttpResponse) {
        cache.set(req.url, event.body);
      }
    })
  );
};
```

---

### Q6: How do you implement retry logic?

**Answer:**
```typescript
export const retryInterceptor: HttpInterceptorFn = (req, next) => {
  // Only retry idempotent operations
  if (!['GET', 'PUT', 'DELETE'].includes(req.method)) {
    return next(req);
  }

  return next(req).pipe(
    retry({
      count: 3,
      delay: (error, retryCount) => {
        // Don't retry client errors (4xx)
        if (error.status >= 400 && error.status < 500) {
          return throwError(() => error);
        }

        // Exponential backoff: 1s, 2s, 4s
        const delay = Math.pow(2, retryCount - 1) * 1000;
        console.log(`Retry ${retryCount} for ${req.url} in ${delay}ms`);
        return timer(delay);
      }
    })
  );
};
```

---

## Advanced Level

### Q7: How do you handle paginated API responses?

**Answer:**
```typescript
// Paginated response type
interface PaginatedResponse<T> {
  data: T[];
  meta: {
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
  };
}

// API Service
@Injectable({ providedIn: 'root' })
export class ProductApiService extends BaseApiService {
  
  getProducts(params: ProductQueryParams): Observable<PaginatedResponse<Product>> {
    const httpParams = new HttpParams()
      .set('page', params.page.toString())
      .set('limit', params.limit.toString())
      .set('sort', params.sort || '')
      .set('filter', params.filter || '');

    return this.get<PaginatedResponse<ProductDto>>('/products', httpParams).pipe(
      map(response => ({
        data: response.data.map(dto => this.mapToProduct(dto)),
        meta: response.meta
      }))
    );
  }
}

// Store with pagination
@Injectable()
export class ProductStore extends ComponentStore<ProductState> {
  readonly products = this.selectSignal(state => state.products);
  readonly pagination = this.selectSignal(state => state.pagination);
  readonly loading = this.selectSignal(state => state.loading);

  readonly loadProducts = this.effect((params$: Observable<ProductQueryParams>) => {
    return params$.pipe(
      tap(() => this.patchState({ loading: true })),
      switchMap(params => this.api.getProducts(params).pipe(
        tapResponse(
          response => this.patchState({
            products: response.data,
            pagination: response.meta,
            loading: false
          }),
          error => this.patchState({ error, loading: false })
        )
      ))
    );
  });
}
```

---

### Q8: How do you handle optimistic updates?

**Answer:**
```typescript
@Injectable()
export class TodoFacade {
  private api = inject(TodoApiService);
  private store = inject(TodoStore);

  deleteTodo(id: string): Observable<void> {
    // 1. Save current state for rollback
    const previousTodos = this.store.todos();

    // 2. Optimistically remove from UI
    this.store.removeTodo(id);

    // 3. Make API call
    return this.api.deleteTodo(id).pipe(
      catchError(error => {
        // 4. Rollback on error
        this.store.setTodos(previousTodos);
        this.notification.error('Failed to delete. Changes reverted.');
        return throwError(() => error);
      })
    );
  }

  updateTodo(id: string, changes: Partial<Todo>): Observable<Todo> {
    const previousTodo = this.store.getTodoById(id);

    // Optimistic update
    this.store.updateTodo(id, changes);

    return this.api.updateTodo(id, changes).pipe(
      catchError(error => {
        // Rollback
        if (previousTodo) {
          this.store.updateTodo(id, previousTodo);
        }
        return throwError(() => error);
      })
    );
  }
}
```

---

### Q9: How do you implement API versioning in the client?

**Answer:**
```typescript
// Configuration-based versioning
export interface ApiConfig {
  baseUrl: string;
  version: string;
}

export const API_CONFIG = new InjectionToken<ApiConfig>('API_CONFIG');

@Injectable({ providedIn: 'root' })
export class BaseApiService {
  private config = inject(API_CONFIG);

  protected get baseUrl(): string {
    return `${this.config.baseUrl}/${this.config.version}`;
  }
}

// Provider setup
providers: [
  {
    provide: API_CONFIG,
    useValue: {
      baseUrl: 'https://api.example.com',
      version: 'v2'
    }
  }
]

// Or header-based versioning
export const apiVersionInterceptor: HttpInterceptorFn = (req, next) => {
  const config = inject(API_CONFIG);
  
  req = req.clone({
    setHeaders: {
      'Accept-Version': config.version,
      'X-API-Version': config.version
    }
  });
  
  return next(req);
};
```

---

### Q10: How do you handle file uploads?

**Answer:**
```typescript
@Injectable({ providedIn: 'root' })
export class FileUploadService {
  private http = inject(HttpClient);
  private baseUrl = environment.apiUrl;

  uploadFile(file: File): Observable<UploadProgress> {
    const formData = new FormData();
    formData.append('file', file, file.name);

    return this.http.post(`${this.baseUrl}/upload`, formData, {
      reportProgress: true,
      observe: 'events'
    }).pipe(
      map(event => {
        switch (event.type) {
          case HttpEventType.UploadProgress:
            const progress = event.total
              ? Math.round(100 * event.loaded / event.total)
              : 0;
            return { status: 'uploading', progress };
          
          case HttpEventType.Response:
            return { status: 'complete', response: event.body };
          
          default:
            return { status: 'pending', progress: 0 };
        }
      })
    );
  }

  uploadMultiple(files: File[]): Observable<UploadProgress[]> {
    return forkJoin(files.map(file => this.uploadFile(file)));
  }
}

// Usage in component
@Component({
  template: `
    <input type="file" (change)="onFileSelected($event)">
    @if (uploading()) {
      <progress [value]="progress()" max="100"></progress>
    }
  `
})
export class FileUploadComponent {
  private uploadService = inject(FileUploadService);
  uploading = signal(false);
  progress = signal(0);

  onFileSelected(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) return;

    this.uploading.set(true);
    this.uploadService.uploadFile(file).subscribe({
      next: result => {
        if (result.status === 'uploading') {
          this.progress.set(result.progress);
        } else if (result.status === 'complete') {
          this.uploading.set(false);
        }
      }
    });
  }
}
```

---

## Quick Reference

```
Interceptor Order:
──────────────────
Request:  logging → auth → cache → next
Response: next → cache → error → logging

Common Interceptors:
────────────────────
Auth          - Add tokens
Error         - Global error handling
Logging       - Request/response logging
Retry         - Automatic retry
Cache         - Response caching
Loading       - Show/hide spinner

HTTP Methods:
─────────────
GET     - Read, safe, cacheable
POST    - Create, not idempotent
PUT     - Replace, idempotent
PATCH   - Partial update
DELETE  - Remove, idempotent

Error Handling:
───────────────
401 → Logout, redirect to login
403 → Access denied message
404 → Not found message
422 → Validation errors (form)
500 → Server error message

Caching Strategy:
─────────────────
Cache GET requests only
Invalidate on mutations
Use TTL (time-to-live)
Clear on logout
```
