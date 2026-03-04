# Day 30: Final Revision & Quick Reference

## Angular 22 Core Concepts Summary

### Component Basics

```typescript
@Component({
  standalone: true,
  selector: 'app-example',
  imports: [CommonModule],
  template: `<h1>{{ title }}</h1>`,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ExampleComponent {
  title = input.required<string>();     // Required input
  count = input(0);                      // Optional with default
  
  click = output<void>();                // Output signal
  
  doubled = computed(() => this.count() * 2);
}
```

### Modern Angular Features

| Feature | Angular 22 Way |
|---------|---------------|
| Input | `input()`, `input.required()` |
| Output | `output()` |
| ViewChild | `viewChild()`, `viewChildren()` |
| ContentChild | `contentChild()`, `contentChildren()` |
| Model | `model()` (two-way binding) |

---

## Control Flow (@-syntax)

```html
<!-- Conditionals -->
@if (condition) {
  <div>True</div>
} @else if (other) {
  <div>Other</div>
} @else {
  <div>False</div>
}

<!-- Loops -->
@for (item of items; track item.id; let i = $index) {
  <div>{{ i }}: {{ item.name }}</div>
} @empty {
  <div>No items</div>
}

<!-- Switch -->
@switch (status) {
  @case ('active') { <span class="active">Active</span> }
  @case ('inactive') { <span class="inactive">Inactive</span> }
  @default { <span>Unknown</span> }
}

<!-- Defer -->
@defer (on viewport) {
  <app-heavy />
} @placeholder {
  <div>Loading...</div>
} @loading (minimum 1s) {
  <mat-spinner />
}
```

---

## Signals Cheat Sheet

```typescript
// Create
const count = signal(0);

// Read
console.log(count());

// Write
count.set(5);
count.update(v => v + 1);

// Computed
const doubled = computed(() => count() * 2);

// Effect
effect(() => console.log('Count:', count()));

// In component
class MyComponent {
  count = signal(0);
  doubled = computed(() => this.count() * 2);
  
  increment() { this.count.update(v => v + 1); }
}
```

---

## RxJS Operators

```
Transformation:
  map, switchMap, mergeMap, concatMap, exhaustMap

Filtering:
  filter, distinctUntilChanged, debounceTime, throttleTime, take, first

Combination:
  combineLatest, forkJoin, merge, concat, withLatestFrom

Error Handling:
  catchError, retry, retryWhen

Utility:
  tap, finalize, delay, timeout

Creation:
  of, from, interval, timer, fromEvent
```

### Common Patterns

```typescript
// Search with debounce
searchControl.valueChanges.pipe(
  debounceTime(300),
  distinctUntilChanged(),
  switchMap(term => this.api.search(term))
);

// Retry with backoff
http.get(url).pipe(
  retry({ count: 3, delay: (_, i) => timer(i * 1000) })
);

// Cleanup
data$.pipe(
  takeUntilDestroyed(this.destroyRef)
).subscribe();
```

---

## Dependency Injection

```typescript
// Service registration
@Injectable({ providedIn: 'root' })  // Singleton
@Injectable()                         // Requires provider

// Injection
class MyComponent {
  service = inject(MyService);
  
  constructor(private alt: MyService) {}  // Alternative
}

// Tokens
const API_URL = new InjectionToken<string>('API_URL');
providers: [{ provide: API_URL, useValue: 'https://api.example.com' }]

// Factory
{ provide: MyService, useFactory: (http: HttpClient) => new MyService(http), deps: [HttpClient] }
```

---

## Routing

```typescript
// Routes
const routes: Routes = [
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  { path: 'home', component: HomeComponent },
  { 
    path: 'products', 
    loadComponent: () => import('./products/products.component'),
    canActivate: [authGuard]
  },
  { path: 'products/:id', component: ProductDetailComponent },
  { path: '**', component: NotFoundComponent }
];

// Guards
export const authGuard: CanActivateFn = () => {
  return inject(AuthService).isLoggedIn() || inject(Router).createUrlTree(['/login']);
};

// Resolvers
export const userResolver: ResolveFn<User> = (route) => {
  return inject(UserService).getUser(route.params['id']);
};

// Navigate
router.navigate(['/products', id]);
router.navigate(['/products'], { queryParams: { page: 1 } });
```

---

## Forms

### Reactive Forms

```typescript
// Build form
form = this.fb.nonNullable.group({
  name: ['', [Validators.required, Validators.minLength(2)]],
  email: ['', [Validators.required, Validators.email]],
  addresses: this.fb.array([])
});

// Access
this.form.get('name')?.value;
this.form.get('name')?.errors;
this.form.valid;
this.form.getRawValue();

// Update
this.form.patchValue({ name: 'John' });
this.form.get('name')?.setValue('John');
this.form.reset();
```

### Template-Driven

```html
<form #myForm="ngForm" (ngSubmit)="submit(myForm)">
  <input name="email" [(ngModel)]="user.email" required email>
  <button [disabled]="myForm.invalid">Submit</button>
</form>
```

---

## HTTP

```typescript
// Configuration
provideHttpClient(withInterceptors([authInterceptor]))

// Service
@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  
  getItems(): Observable<Item[]> {
    return this.http.get<Item[]>('/api/items');
  }
  
  createItem(item: Item): Observable<Item> {
    return this.http.post<Item>('/api/items', item);
  }
}

// Interceptor
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const token = inject(AuthService).token();
  if (token) {
    req = req.clone({ setHeaders: { Authorization: `Bearer ${token}` }});
  }
  return next(req);
};
```

---

## Testing

```typescript
// Component test
describe('MyComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MyComponent],
      providers: [{ provide: MyService, useValue: mockService }]
    }).compileComponents();
  });

  it('should create', () => {
    const fixture = TestBed.createComponent(MyComponent);
    expect(fixture.componentInstance).toBeTruthy();
  });
});

// Service test
describe('MyService', () => {
  let service: MyService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()]
    });
    service = TestBed.inject(MyService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  it('should fetch data', () => {
    service.getData().subscribe(data => expect(data).toEqual(mockData));
    httpMock.expectOne('/api/data').flush(mockData);
  });
});
```

---

## Performance Optimization Checklist

- [ ] Use `OnPush` change detection
- [ ] Use signals instead of getters
- [ ] Use `trackBy` (track in @for)
- [ ] Lazy load routes
- [ ] Use `@defer` for heavy components
- [ ] Virtual scrolling for long lists
- [ ] Debounce user inputs
- [ ] Cache HTTP responses
- [ ] Enable SSR for public pages
- [ ] Analyze bundles (`ng build --stats-json`)

---

## Interview Day Checklist

1. **Before:**
   - [ ] Review this cheat sheet
   - [ ] Practice coding problems
   - [ ] Prepare questions to ask
   - [ ] Test equipment (camera, mic)

2. **During:**
   - [ ] Explain thought process
   - [ ] Ask clarifying questions
   - [ ] Mention trade-offs
   - [ ] Be honest about unknowns

3. **Key Topics:**
   - [ ] Signals vs RxJS
   - [ ] Change detection
   - [ ] Performance optimization
   - [ ] State management patterns
   - [ ] Testing strategies

---

## Quick Commands

```bash
# Create app
ng new my-app --standalone --routing --style=scss

# Generate
ng g c components/button --standalone
ng g s services/api
ng g guard guards/auth --functional

# Build & Serve
ng serve
ng build --configuration=production

# Test
ng test
ng test --code-coverage

# Analyze
ng build --stats-json
npx webpack-bundle-analyzer dist/stats.json
```

---

**Good luck with your interview!**
