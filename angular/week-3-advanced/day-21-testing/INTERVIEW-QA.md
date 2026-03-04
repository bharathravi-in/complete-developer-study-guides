# Day 21: Angular Testing - Interview Questions & Answers

## Basic Level

### Q1: What testing tools does Angular provide?

**Answer:**
Angular provides a comprehensive testing ecosystem:

| Tool | Purpose |
|------|---------|
| **Jasmine** | Testing framework (describe, it, expect) |
| **Karma** | Test runner (executes tests in browsers) |
| **TestBed** | Angular testing utility for configuring tests |
| **HttpTestingController** | Mock HTTP requests |
| **RouterTestingModule** | Test routing |

```typescript
// Basic test structure
describe('ComponentName', () => {
  let component: MyComponent;
  let fixture: ComponentFixture<MyComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MyComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(MyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
```

---

### Q2: How do you test a component with inputs?

**Answer:**
```typescript
@Component({
  selector: 'app-greeting',
  template: `<h1>Hello, {{ name() }}!</h1>`
})
export class GreetingComponent {
  name = input('Guest');
}

// Test
describe('GreetingComponent', () => {
  let fixture: ComponentFixture<GreetingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GreetingComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(GreetingComponent);
  });

  it('should display default name', () => {
    fixture.detectChanges();
    const h1 = fixture.nativeElement.querySelector('h1');
    expect(h1.textContent).toBe('Hello, Guest!');
  });

  it('should display provided name', () => {
    fixture.componentRef.setInput('name', 'John');
    fixture.detectChanges();
    
    const h1 = fixture.nativeElement.querySelector('h1');
    expect(h1.textContent).toBe('Hello, John!');
  });
});
```

---

### Q3: How do you test component outputs?

**Answer:**
```typescript
@Component({
  selector: 'app-button',
  template: `<button (click)="onClick()">Click me</button>`
})
export class ButtonComponent {
  clicked = output<void>();

  onClick() {
    this.clicked.emit();
  }
}

// Test
describe('ButtonComponent', () => {
  it('should emit clicked event', () => {
    const fixture = TestBed.createComponent(ButtonComponent);
    fixture.detectChanges();

    let emitted = false;
    fixture.componentInstance.clicked.subscribe(() => {
      emitted = true;
    });

    const button = fixture.nativeElement.querySelector('button');
    button.click();

    expect(emitted).toBeTrue();
  });
});
```

---

## Intermediate Level

### Q4: How do you mock a service in component tests?

**Answer:**
```typescript
@Component({
  template: `
    @for (user of users(); track user.id) {
      <div>{{ user.name }}</div>
    }
  `
})
export class UserListComponent {
  private userService = inject(UserService);
  users = signal<User[]>([]);

  ngOnInit() {
    this.userService.getUsers().subscribe(users => {
      this.users.set(users);
    });
  }
}

// Test with mock
describe('UserListComponent', () => {
  let mockUserService: jasmine.SpyObj<UserService>;

  beforeEach(async () => {
    // Create spy object
    mockUserService = jasmine.createSpyObj('UserService', ['getUsers']);
    mockUserService.getUsers.and.returnValue(of([
      { id: '1', name: 'John' },
      { id: '2', name: 'Jane' }
    ]));

    await TestBed.configureTestingModule({
      imports: [UserListComponent],
      providers: [
        { provide: UserService, useValue: mockUserService }
      ]
    }).compileComponents();
  });

  it('should display users from service', () => {
    const fixture = TestBed.createComponent(UserListComponent);
    fixture.detectChanges();

    expect(mockUserService.getUsers).toHaveBeenCalled();
    
    const items = fixture.nativeElement.querySelectorAll('div');
    expect(items.length).toBe(2);
    expect(items[0].textContent).toBe('John');
  });
});
```

---

### Q5: How do you test HTTP services?

**Answer:**
```typescript
@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);

  getProducts(): Observable<Product[]> {
    return this.http.get<Product[]>('/api/products');
  }

  createProduct(product: Product): Observable<Product> {
    return this.http.post<Product>('/api/products', product);
  }
}

// Test
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';

describe('ApiService', () => {
  let service: ApiService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });

    service = TestBed.inject(ApiService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();  // Verify no outstanding requests
  });

  it('should GET products', () => {
    const mockProducts = [{ id: '1', name: 'Product 1' }];

    service.getProducts().subscribe(products => {
      expect(products).toEqual(mockProducts);
    });

    const req = httpMock.expectOne('/api/products');
    expect(req.request.method).toBe('GET');
    req.flush(mockProducts);  // Return mock data
  });

  it('should POST new product', () => {
    const newProduct = { id: '2', name: 'Product 2' };

    service.createProduct(newProduct).subscribe(product => {
      expect(product).toEqual(newProduct);
    });

    const req = httpMock.expectOne('/api/products');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(newProduct);
    req.flush(newProduct);
  });

  it('should handle 404 error', () => {
    service.getProducts().subscribe({
      next: () => fail('Should have failed'),
      error: (error) => {
        expect(error.status).toBe(404);
      }
    });

    const req = httpMock.expectOne('/api/products');
    req.flush('Not found', { status: 404, statusText: 'Not Found' });
  });
});
```

---

### Q6: How do you test async operations with fakeAsync?

**Answer:**
```typescript
@Component({
  template: `
    <input (input)="onSearch($event)">
    <div *ngIf="loading">Loading...</div>
    <ul>
      @for (item of results(); track item) {
        <li>{{ item }}</li>
      }
    </ul>
  `
})
export class SearchComponent {
  private searchService = inject(SearchService);
  results = signal<string[]>([]);
  loading = false;

  onSearch(event: Event) {
    const query = (event.target as HTMLInputElement).value;
    this.loading = true;
    
    // Debounced search
    timer(300).pipe(
      switchMap(() => this.searchService.search(query))
    ).subscribe(results => {
      this.results.set(results);
      this.loading = false;
    });
  }
}

// Test
describe('SearchComponent', () => {
  let mockSearchService: jasmine.SpyObj<SearchService>;

  beforeEach(async () => {
    mockSearchService = jasmine.createSpyObj('SearchService', ['search']);
    
    await TestBed.configureTestingModule({
      imports: [SearchComponent],
      providers: [
        { provide: SearchService, useValue: mockSearchService }
      ]
    }).compileComponents();
  });

  it('should debounce search', fakeAsync(() => {
    mockSearchService.search.and.returnValue(of(['Result 1', 'Result 2']));

    const fixture = TestBed.createComponent(SearchComponent);
    fixture.detectChanges();

    const input = fixture.nativeElement.querySelector('input');
    input.value = 'test';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    // Before debounce completes
    expect(fixture.nativeElement.textContent).toContain('Loading...');
    expect(mockSearchService.search).not.toHaveBeenCalled();

    // After debounce
    tick(300);
    fixture.detectChanges();

    expect(mockSearchService.search).toHaveBeenCalledWith('test');
    expect(fixture.nativeElement.querySelectorAll('li').length).toBe(2);
  }));
});
```

---

## Advanced Level

### Q7: How do you test components with routing?

**Answer:**
```typescript
@Component({
  template: `
    <a routerLink="/home">Home</a>
    <a routerLink="/about">About</a>
    <router-outlet></router-outlet>
  `
})
export class NavComponent {}

// Test
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';

describe('NavComponent', () => {
  let router: Router;
  let fixture: ComponentFixture<NavComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        NavComponent,
        RouterTestingModule.withRoutes([
          { path: 'home', component: DummyComponent },
          { path: 'about', component: DummyComponent }
        ])
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(NavComponent);
    router = TestBed.inject(Router);
    fixture.detectChanges();
  });

  it('should navigate to home', fakeAsync(() => {
    const links = fixture.debugElement.queryAll(By.css('a'));
    links[0].nativeElement.click();
    tick();
    
    expect(router.url).toBe('/home');
  }));

  it('should navigate programmatically', fakeAsync(() => {
    router.navigate(['/about']);
    tick();
    fixture.detectChanges();
    
    expect(router.url).toBe('/about');
  }));
});
```

---

### Q8: How do you test forms?

**Answer:**
```typescript
@Component({
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()">
      <input formControlName="email" type="email">
      <div *ngIf="form.get('email')?.errors?.['email']" class="error">
        Invalid email
      </div>
      <button type="submit" [disabled]="form.invalid">Submit</button>
    </form>
  `
})
export class LoginFormComponent {
  form = inject(FormBuilder).group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]]
  });

  submitted = output<{ email: string; password: string }>();

  submit() {
    if (this.form.valid) {
      this.submitted.emit(this.form.value as any);
    }
  }
}

// Test
describe('LoginFormComponent', () => {
  let fixture: ComponentFixture<LoginFormComponent>;
  let component: LoginFormComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoginFormComponent, ReactiveFormsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(LoginFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should show validation error for invalid email', () => {
    const emailInput = fixture.debugElement.query(By.css('input')).nativeElement;
    
    emailInput.value = 'invalid-email';
    emailInput.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    const error = fixture.nativeElement.querySelector('.error');
    expect(error).toBeTruthy();
    expect(error.textContent).toContain('Invalid email');
  });

  it('should disable submit button when form is invalid', () => {
    const button = fixture.nativeElement.querySelector('button');
    expect(button.disabled).toBeTrue();
  });

  it('should emit submitted event with form values', () => {
    let emittedValue: any;
    component.submitted.subscribe(value => emittedValue = value);

    component.form.setValue({
      email: 'test@example.com',
      password: 'password123'
    });
    fixture.detectChanges();

    const form = fixture.debugElement.query(By.css('form'));
    form.triggerEventHandler('ngSubmit', null);

    expect(emittedValue).toEqual({
      email: 'test@example.com',
      password: 'password123'
    });
  });
});
```

---

### Q9: How do you achieve good code coverage?

**Answer:**

**1. Run coverage report:**
```bash
ng test --code-coverage
```

**2. Coverage configuration:**
```json
// angular.json
{
  "test": {
    "options": {
      "codeCoverage": true,
      "codeCoverageExclude": [
        "src/**/*.spec.ts",
        "src/test.ts",
        "src/environments/**"
      ]
    }
  }
}
```

**3. Coverage thresholds:**
```json
// karma.conf.js
coverageReporter: {
  check: {
    global: {
      statements: 80,
      branches: 80,
      functions: 80,
      lines: 80
    }
  }
}
```

**4. Writing comprehensive tests:**
```typescript
// Test all branches
describe('calculateDiscount', () => {
  it('should return 0 for amounts below threshold', () => {
    expect(service.calculateDiscount(50)).toBe(0);
  });

  it('should return 10% for amounts between 100-500', () => {
    expect(service.calculateDiscount(200)).toBe(20);
  });

  it('should return 20% for amounts above 500', () => {
    expect(service.calculateDiscount(1000)).toBe(200);
  });

  it('should handle null/undefined', () => {
    expect(service.calculateDiscount(null as any)).toBe(0);
  });
});
```

---

### Q10: What are testing best practices in Angular?

**Answer:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Angular Testing Best Practices                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  1. TEST ISOLATION                                                   │
│     • Each test should be independent                                │
│     • Use beforeEach to reset state                                  │
│     • Don't rely on test execution order                             │
│                                                                      │
│  2. MOCK DEPENDENCIES                                                │
│     • Mock services, not implementation                              │
│     • Use jasmine.createSpyObj for spy objects                       │
│     • Control external dependencies                                   │
│                                                                      │
│  3. TEST BEHAVIOR, NOT IMPLEMENTATION                                │
│     • Test what component does, not how                              │
│     • Focus on inputs/outputs                                        │
│     • Avoid testing private methods directly                         │
│                                                                      │
│  4. ASYNC TESTING                                                    │
│     • Use fakeAsync + tick for timers                               │
│     • Use waitForAsync for Promises                                  │
│     • Always handle async operations                                 │
│                                                                      │
│  5. MAINTAINABLE TESTS                                               │
│     • Keep tests simple and readable                                 │
│     • One assertion per test (when possible)                         │
│     • Use descriptive test names                                     │
│                                                                      │
│  6. COVERAGE                                                         │
│     • Aim for 80%+ coverage                                         │
│     • Test edge cases and error paths                                │
│     • Don't just test happy paths                                    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Example of good test structure:**
```typescript
describe('UserService', () => {
  // Describe the unit
  let service: UserService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    // Setup for each test
    TestBed.configureTestingModule({...});
    service = TestBed.inject(UserService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    // Cleanup
    httpMock.verify();
  });

  describe('getUser', () => {
    // Group related tests
    
    it('should return user when found', () => {...});
    it('should throw error when not found', () => {...});
    it('should handle network error', () => {...});
  });

  describe('createUser', () => {
    it('should create user successfully', () => {...});
    it('should handle validation error', () => {...});
  });
});
```

---

## Quick Reference

```
Test Commands:
──────────────
ng test                     - Run tests in watch mode
ng test --watch=false       - Single run
ng test --code-coverage     - Generate coverage
ng test --browsers=Chrome   - Specific browser

TestBed Methods:
────────────────
configureTestingModule()    - Configure test module
createComponent()           - Create component fixture
inject()                    - Get service instance
overrideComponent()         - Override component metadata

Fixture Methods:
────────────────
detectChanges()             - Trigger change detection
componentRef.setInput()     - Set input values
debugElement.query()        - Query elements
nativeElement               - Access DOM element
whenStable()                - Wait for async

Async Testing:
──────────────
fakeAsync(() => {})         - Wrap test function
tick()                      - Simulate time passage
tick(1000)                  - Advance 1000ms
flush()                     - Flush all pending async
waitForAsync(() => {})      - For promise-based async

Jasmine Matchers:
─────────────────
expect(x).toBe(y)           - Strict equality
expect(x).toEqual(y)        - Deep equality
expect(x).toBeTruthy()      - Truthy check
expect(x).toContain(y)      - Contains element
expect(fn).toThrow()        - Throws error
expect(spy).toHaveBeenCalled()
expect(spy).toHaveBeenCalledWith(arg)
```
