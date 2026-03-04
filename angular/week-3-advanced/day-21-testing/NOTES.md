# Day 21: Angular Testing

## Overview

Angular provides robust testing capabilities with Jasmine (test framework) and Karma (test runner), plus support for Jest and other frameworks.

---

## Testing Setup

### Default Setup (Jasmine + Karma)

```bash
# Run tests
ng test

# Run with code coverage
ng test --code-coverage

# Run single run (CI)
ng test --watch=false --browsers=ChromeHeadless
```

### Jest Setup (Alternative)

```bash
# Install Jest
npm install jest @types/jest jest-preset-angular --save-dev

# Remove Karma
npm uninstall karma karma-chrome-launcher karma-coverage karma-jasmine karma-jasmine-html-reporter
```

```javascript
// jest.config.js
module.exports = {
  preset: 'jest-preset-angular',
  setupFilesAfterEnv: ['<rootDir>/setup-jest.ts'],
  testPathIgnorePatterns: ['<rootDir>/node_modules/', '<rootDir>/dist/'],
  coverageDirectory: 'coverage',
  testMatch: ['**/+(*.)+(spec).+(ts)']
};

// setup-jest.ts
import 'jest-preset-angular/setup-jest';
```

---

## Unit Testing Components

### Basic Component Test

```typescript
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HelloComponent } from './hello.component';

describe('HelloComponent', () => {
  let component: HelloComponent;
  let fixture: ComponentFixture<HelloComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HelloComponent]  // Standalone component
    }).compileComponents();

    fixture = TestBed.createComponent(HelloComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();  // Trigger initial change detection
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display the name', () => {
    component.name = 'John';
    fixture.detectChanges();
    
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('John');
  });
});
```

### Testing Inputs and Outputs

```typescript
@Component({
  selector: 'app-counter',
  template: `
    <span>{{ count() }}</span>
    <button (click)="increment()">+</button>
  `
})
export class CounterComponent {
  count = input(0);
  countChange = output<number>();
  
  increment() {
    this.countChange.emit(this.count() + 1);
  }
}

// Test
describe('CounterComponent', () => {
  let component: CounterComponent;
  let fixture: ComponentFixture<CounterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CounterComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(CounterComponent);
    component = fixture.componentInstance;
  });

  it('should display initial count', () => {
    fixture.componentRef.setInput('count', 5);
    fixture.detectChanges();
    
    const span = fixture.nativeElement.querySelector('span');
    expect(span.textContent).toBe('5');
  });

  it('should emit countChange when increment clicked', () => {
    fixture.componentRef.setInput('count', 10);
    fixture.detectChanges();
    
    let emittedValue: number | undefined;
    component.countChange.subscribe(value => emittedValue = value);
    
    const button = fixture.nativeElement.querySelector('button');
    button.click();
    
    expect(emittedValue).toBe(11);
  });
});
```

### Testing with Signal Inputs

```typescript
@Component({
  selector: 'app-user-card',
  template: `
    <div class="card">
      <h2>{{ user().name }}</h2>
      <p>{{ user().email }}</p>
    </div>
  `
})
export class UserCardComponent {
  user = input.required<User>();
}

// Test
describe('UserCardComponent', () => {
  it('should display user information', async () => {
    await TestBed.configureTestingModule({
      imports: [UserCardComponent]
    }).compileComponents();

    const fixture = TestBed.createComponent(UserCardComponent);
    
    const testUser = { name: 'John Doe', email: 'john@example.com' };
    fixture.componentRef.setInput('user', testUser);
    fixture.detectChanges();

    const compiled = fixture.nativeElement;
    expect(compiled.querySelector('h2').textContent).toBe('John Doe');
    expect(compiled.querySelector('p').textContent).toBe('john@example.com');
  });
});
```

---

## Testing Services

### Basic Service Test

```typescript
@Injectable({ providedIn: 'root' })
export class CalculatorService {
  add(a: number, b: number): number {
    return a + b;
  }

  divide(a: number, b: number): number {
    if (b === 0) throw new Error('Cannot divide by zero');
    return a / b;
  }
}

// Test
describe('CalculatorService', () => {
  let service: CalculatorService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CalculatorService);
  });

  it('should add two numbers', () => {
    expect(service.add(2, 3)).toBe(5);
  });

  it('should throw error when dividing by zero', () => {
    expect(() => service.divide(10, 0)).toThrowError('Cannot divide by zero');
  });
});
```

### Testing Service with HTTP

```typescript
@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);
  private apiUrl = '/api/users';

  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl);
  }

  getUser(id: string): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/${id}`);
  }

  createUser(user: User): Observable<User> {
    return this.http.post<User>(this.apiUrl, user);
  }
}

// Test
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';

describe('UserService', () => {
  let service: UserService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    });

    service = TestBed.inject(UserService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();  // Ensure no outstanding requests
  });

  it('should fetch users', () => {
    const mockUsers: User[] = [
      { id: '1', name: 'John', email: 'john@example.com' },
      { id: '2', name: 'Jane', email: 'jane@example.com' }
    ];

    service.getUsers().subscribe(users => {
      expect(users.length).toBe(2);
      expect(users).toEqual(mockUsers);
    });

    const req = httpMock.expectOne('/api/users');
    expect(req.request.method).toBe('GET');
    req.flush(mockUsers);
  });

  it('should create user', () => {
    const newUser: User = { id: '3', name: 'Bob', email: 'bob@example.com' };

    service.createUser(newUser).subscribe(user => {
      expect(user).toEqual(newUser);
    });

    const req = httpMock.expectOne('/api/users');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(newUser);
    req.flush(newUser);
  });

  it('should handle error', () => {
    service.getUser('999').subscribe({
      next: () => fail('Should have failed'),
      error: (error) => {
        expect(error.status).toBe(404);
      }
    });

    const req = httpMock.expectOne('/api/users/999');
    req.flush('User not found', { status: 404, statusText: 'Not Found' });
  });
});
```

---

## Mocking Dependencies

### Using Spies

```typescript
@Component({
  template: `<button (click)="save()">Save</button>`
})
export class FormComponent {
  private service = inject(DataService);
  private router = inject(Router);

  save() {
    this.service.save({ name: 'Test' }).subscribe(() => {
      this.router.navigate(['/success']);
    });
  }
}

// Test with spies
describe('FormComponent', () => {
  let component: FormComponent;
  let fixture: ComponentFixture<FormComponent>;
  let mockService: jasmine.SpyObj<DataService>;
  let mockRouter: jasmine.SpyObj<Router>;

  beforeEach(async () => {
    mockService = jasmine.createSpyObj('DataService', ['save']);
    mockRouter = jasmine.createSpyObj('Router', ['navigate']);

    await TestBed.configureTestingModule({
      imports: [FormComponent],
      providers: [
        { provide: DataService, useValue: mockService },
        { provide: Router, useValue: mockRouter }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(FormComponent);
    component = fixture.componentInstance;
  });

  it('should navigate on successful save', fakeAsync(() => {
    mockService.save.and.returnValue(of({ id: '1', name: 'Test' }));

    const button = fixture.nativeElement.querySelector('button');
    button.click();
    tick();

    expect(mockService.save).toHaveBeenCalled();
    expect(mockRouter.navigate).toHaveBeenCalledWith(['/success']);
  }));
});
```

### Mock Service Class

```typescript
// Create mock class
class MockUserService {
  users = [
    { id: '1', name: 'John' },
    { id: '2', name: 'Jane' }
  ];

  getUsers() {
    return of(this.users);
  }

  getUser(id: string) {
    const user = this.users.find(u => u.id === id);
    return user ? of(user) : throwError(() => new Error('Not found'));
  }
}

// Test
describe('UserListComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserListComponent],
      providers: [
        { provide: UserService, useClass: MockUserService }
      ]
    }).compileComponents();
  });

  it('should display users', () => {
    const fixture = TestBed.createComponent(UserListComponent);
    fixture.detectChanges();

    const items = fixture.nativeElement.querySelectorAll('li');
    expect(items.length).toBe(2);
  });
});
```

---

## Testing Async Operations

### fakeAsync and tick

```typescript
@Component({
  template: `
    <input (input)="search($event)">
    <ul>
      @for (result of results(); track result.id) {
        <li>{{ result.name }}</li>
      }
    </ul>
  `
})
export class SearchComponent {
  private searchService = inject(SearchService);
  results = signal<Result[]>([]);

  search(event: Event) {
    const query = (event.target as HTMLInputElement).value;
    
    // Debounced search
    this.searchService.search(query)
      .pipe(debounceTime(300))
      .subscribe(results => this.results.set(results));
  }
}

// Test
describe('SearchComponent', () => {
  let mockService: jasmine.SpyObj<SearchService>;

  beforeEach(async () => {
    mockService = jasmine.createSpyObj('SearchService', ['search']);
    
    await TestBed.configureTestingModule({
      imports: [SearchComponent],
      providers: [{ provide: SearchService, useValue: mockService }]
    }).compileComponents();
  });

  it('should debounce search', fakeAsync(() => {
    mockService.search.and.returnValue(of([{ id: '1', name: 'Result' }]));

    const fixture = TestBed.createComponent(SearchComponent);
    fixture.detectChanges();

    const input = fixture.nativeElement.querySelector('input');
    input.value = 'test';
    input.dispatchEvent(new Event('input'));

    // Before debounce time
    expect(mockService.search).not.toHaveBeenCalled();

    // After debounce
    tick(300);
    fixture.detectChanges();

    expect(mockService.search).toHaveBeenCalledWith('test');
    expect(fixture.nativeElement.querySelectorAll('li').length).toBe(1);
  }));
});
```

### waitForAsync

```typescript
it('should load data asynchronously', waitForAsync(() => {
  const fixture = TestBed.createComponent(AsyncComponent);
  fixture.detectChanges();

  fixture.whenStable().then(() => {
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('p').textContent).toBe('Loaded');
  });
}));
```

---

## Testing DOM Interaction

### Click Events

```typescript
it('should handle click', () => {
  const fixture = TestBed.createComponent(ButtonComponent);
  fixture.detectChanges();

  const button = fixture.debugElement.query(By.css('button'));
  button.triggerEventHandler('click', null);
  fixture.detectChanges();

  expect(fixture.componentInstance.clicked).toBeTrue();
});
```

### Form Inputs

```typescript
it('should update form value', () => {
  const fixture = TestBed.createComponent(FormComponent);
  fixture.detectChanges();

  const input = fixture.debugElement.query(By.css('input')).nativeElement;
  input.value = 'test value';
  input.dispatchEvent(new Event('input'));
  fixture.detectChanges();

  expect(fixture.componentInstance.form.get('name')?.value).toBe('test value');
});
```

---

## Testing Pipes

```typescript
@Pipe({ name: 'truncate', standalone: true })
export class TruncatePipe implements PipeTransform {
  transform(value: string, length = 50): string {
    if (!value) return '';
    if (value.length <= length) return value;
    return value.substring(0, length) + '...';
  }
}

// Test
describe('TruncatePipe', () => {
  let pipe: TruncatePipe;

  beforeEach(() => {
    pipe = new TruncatePipe();
  });

  it('should return empty string for null', () => {
    expect(pipe.transform(null as any)).toBe('');
  });

  it('should not truncate short strings', () => {
    expect(pipe.transform('Hello', 10)).toBe('Hello');
  });

  it('should truncate long strings', () => {
    expect(pipe.transform('Hello World', 5)).toBe('Hello...');
  });

  it('should use default length', () => {
    const longString = 'a'.repeat(60);
    const result = pipe.transform(longString);
    expect(result.length).toBe(53);  // 50 + '...'
  });
});
```

---

## Testing Directives

```typescript
@Directive({
  selector: '[appHighlight]',
  standalone: true
})
export class HighlightDirective {
  @Input('appHighlight') color = 'yellow';
  
  private el = inject(ElementRef);

  @HostListener('mouseenter')
  onMouseEnter() {
    this.el.nativeElement.style.backgroundColor = this.color;
  }

  @HostListener('mouseleave')
  onMouseLeave() {
    this.el.nativeElement.style.backgroundColor = '';
  }
}

// Test
@Component({
  template: `<p appHighlight="blue">Test</p>`,
  imports: [HighlightDirective]
})
class TestHostComponent {}

describe('HighlightDirective', () => {
  it('should highlight on mouseenter', () => {
    const fixture = TestBed.createComponent(TestHostComponent);
    fixture.detectChanges();

    const p = fixture.debugElement.query(By.css('p'));
    
    p.triggerEventHandler('mouseenter', null);
    expect(p.nativeElement.style.backgroundColor).toBe('blue');

    p.triggerEventHandler('mouseleave', null);
    expect(p.nativeElement.style.backgroundColor).toBe('');
  });
});
```

---

## Testing with RouterTestingModule

```typescript
import { RouterTestingModule } from '@angular/router/testing';
import { Router } from '@angular/router';

describe('NavigationComponent', () => {
  let router: Router;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        NavigationComponent,
        RouterTestingModule.withRoutes([
          { path: 'home', component: DummyComponent },
          { path: 'about', component: DummyComponent }
        ])
      ]
    }).compileComponents();

    router = TestBed.inject(Router);
  });

  it('should navigate to about', fakeAsync(() => {
    const fixture = TestBed.createComponent(NavigationComponent);
    fixture.detectChanges();

    router.navigate(['/about']);
    tick();
    fixture.detectChanges();

    expect(router.url).toBe('/about');
  }));
});
```

---

## Code Coverage

```bash
# Generate coverage report
ng test --code-coverage

# View in browser
open coverage/index.html
```

```json
// angular.json - coverage configuration
{
  "test": {
    "options": {
      "codeCoverage": true,
      "codeCoverageExclude": [
        "src/**/*.spec.ts",
        "src/test.ts"
      ]
    }
  }
}
```

---

## Summary

| Test Type | Tools | Purpose |
|-----------|-------|---------|
| Unit Tests | Jasmine/Jest | Test isolated units |
| Component Tests | TestBed | Test component behavior |
| Service Tests | HttpTestingController | Test services with HTTP |
| Integration Tests | RouterTestingModule | Test component interactions |
| E2E Tests | Cypress/Playwright | Test full application |

```
Testing Utilities:
──────────────────
TestBed                    - Configure testing module
ComponentFixture           - Component test wrapper
fakeAsync + tick           - Test async code
waitForAsync               - Alternative async testing
By.css/By.directive        - Query elements
HttpTestingController      - Mock HTTP requests
RouterTestingModule        - Test routing
```
