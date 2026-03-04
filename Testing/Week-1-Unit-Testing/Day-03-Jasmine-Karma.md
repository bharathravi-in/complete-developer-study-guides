# Day 3: Jasmine & Karma – Angular Testing Ecosystem

## 📚 Topics to Cover (3-4 hours)

---

## 1. Jasmine Overview

Jasmine is the default testing framework for Angular. It provides a BDD-style syntax for writing tests.

### Core Syntax

```typescript
describe('Calculator', () => {
  let calculator: Calculator;

  beforeEach(() => {
    calculator = new Calculator();
  });

  it('should add two numbers', () => {
    expect(calculator.add(2, 3)).toBe(5);
  });

  it('should subtract two numbers', () => {
    expect(calculator.subtract(5, 3)).toBe(2);
  });

  // Nested describe
  describe('division', () => {
    it('should divide correctly', () => {
      expect(calculator.divide(10, 2)).toBe(5);
    });

    it('should throw for division by zero', () => {
      expect(() => calculator.divide(10, 0)).toThrowError('Cannot divide by zero');
    });
  });

  // Pending/skipped tests
  xit('should handle large numbers', () => {
    // This test is skipped
  });

  // Focused test (runs only this)
  // fit('should run only this test', () => { ... });
});
```

---

## 2. Jasmine Matchers

```typescript
// Equality
expect(a).toBe(b);               // strict equality (===)
expect(a).toEqual(b);            // deep equality
expect(a).toBeTrue();
expect(a).toBeFalse();

// Truthiness
expect(a).toBeTruthy();
expect(a).toBeFalsy();
expect(a).toBeNull();
expect(a).toBeUndefined();
expect(a).toBeDefined();
expect(a).toBeNaN();

// Comparison
expect(a).toBeGreaterThan(b);
expect(a).toBeLessThan(b);
expect(a).toBeGreaterThanOrEqual(b);

// Strings
expect(str).toContain('substring');
expect(str).toMatch(/pattern/);

// Arrays
expect(arr).toContain(element);
expect(arr).toHaveSize(3);

// Objects
expect(obj).toEqual(jasmine.objectContaining({ key: 'value' }));
expect(arr).toEqual(jasmine.arrayContaining([1, 2]));

// Exceptions
expect(fn).toThrow();
expect(fn).toThrowError('message');
expect(fn).toThrowError(TypeError);

// Spy matchers
expect(spy).toHaveBeenCalled();
expect(spy).toHaveBeenCalledTimes(3);
expect(spy).toHaveBeenCalledWith('arg1', 'arg2');
expect(spy).toHaveBeenCalledOnceWith('arg');
```

---

## 3. Jasmine Spies

```typescript
describe('UserService', () => {
  let service: UserService;
  let httpClient: jasmine.SpyObj<HttpClient>;

  beforeEach(() => {
    // Create spy object with methods
    httpClient = jasmine.createSpyObj('HttpClient', ['get', 'post', 'put', 'delete']);
    service = new UserService(httpClient);
  });

  it('should call GET /users', () => {
    const mockUsers = [{ id: 1, name: 'John' }];
    httpClient.get.and.returnValue(of(mockUsers));

    service.getUsers().subscribe(users => {
      expect(users).toEqual(mockUsers);
    });

    expect(httpClient.get).toHaveBeenCalledWith('/api/users');
  });
});

// Spy on existing method
const spy = spyOn(service, 'getUser');
spy.and.returnValue(of(mockUser));    // return specific value
spy.and.callThrough();                 // call real implementation
spy.and.callFake((id) => of(mock));    // custom implementation
spy.and.throwError('error');           // throw error
```

---

## 4. Karma Test Runner

### Configuration (karma.conf.js)

```javascript
module.exports = function (config) {
  config.set({
    basePath: '',
    frameworks: ['jasmine', '@angular-devkit/build-angular'],
    plugins: [
      require('karma-jasmine'),
      require('karma-chrome-launcher'),
      require('karma-jasmine-html-reporter'),
      require('karma-coverage'),
      require('@angular-devkit/build-angular/plugins/karma')
    ],
    client: {
      jasmine: {
        random: true,            // randomize test order
        seed: '4321',            // specific seed for reproducibility
        stopOnSpecFailure: false,
        failSpecWithNoExpectations: true
      },
      clearContext: false
    },
    coverageReporter: {
      dir: require('path').join(__dirname, './coverage'),
      subdir: '.',
      reporters: [
        { type: 'html' },
        { type: 'text-summary' },
        { type: 'lcovonly' }
      ],
      check: {
        global: {
          statements: 80,
          branches: 80,
          functions: 80,
          lines: 80
        }
      }
    },
    reporters: ['progress', 'kjhtml'],
    browsers: ['Chrome'],         // or 'ChromeHeadless' for CI
    restartOnFileChange: true,
    singleRun: false              // true for CI
  });
};
```

### Running Tests

```bash
# Run tests with watch
ng test

# Run tests once (CI mode)
ng test --watch=false

# Run with code coverage
ng test --code-coverage

# Run specific test file
ng test --include='**/user.service.spec.ts'

# Run headless (CI)
ng test --watch=false --browsers=ChromeHeadless
```

---

## 5. Angular TestBed

### Component Testing

```typescript
describe('UserListComponent', () => {
  let component: UserListComponent;
  let fixture: ComponentFixture<UserListComponent>;
  let userService: jasmine.SpyObj<UserService>;

  beforeEach(async () => {
    const spy = jasmine.createSpyObj('UserService', ['getUsers']);

    await TestBed.configureTestingModule({
      declarations: [UserListComponent],
      providers: [
        { provide: UserService, useValue: spy }
      ],
      imports: [HttpClientTestingModule]
    }).compileComponents();

    fixture = TestBed.createComponent(UserListComponent);
    component = fixture.componentInstance;
    userService = TestBed.inject(UserService) as jasmine.SpyObj<UserService>;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should load users on init', () => {
    const mockUsers = [{ id: 1, name: 'John' }, { id: 2, name: 'Jane' }];
    userService.getUsers.and.returnValue(of(mockUsers));

    fixture.detectChanges(); // triggers ngOnInit

    expect(component.users).toEqual(mockUsers);
    expect(userService.getUsers).toHaveBeenCalledTimes(1);
  });

  it('should display user names in template', () => {
    const mockUsers = [{ id: 1, name: 'John' }];
    userService.getUsers.and.returnValue(of(mockUsers));

    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('.user-name')?.textContent).toContain('John');
  });
});
```

### Service Testing

```typescript
describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AuthService]
    });

    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify(); // Ensure no outstanding requests
  });

  it('should login and return token', () => {
    const mockResponse = { token: 'abc123', user: { id: 1 } };

    service.login('user@test.com', 'password').subscribe(response => {
      expect(response.token).toBe('abc123');
    });

    const req = httpMock.expectOne('/api/auth/login');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({
      email: 'user@test.com',
      password: 'password'
    });
    req.flush(mockResponse);
  });

  it('should handle login error', () => {
    service.login('bad@test.com', 'wrong').subscribe({
      error: (err) => {
        expect(err.status).toBe(401);
      }
    });

    const req = httpMock.expectOne('/api/auth/login');
    req.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
  });
});
```

---

## 6. Jasmine vs Jest Comparison

| Feature | Jasmine | Jest |
|---------|---------|------|
| Setup | `beforeEach` / `beforeAll` | Same |
| Spy creation | `jasmine.createSpyObj()` | `jest.fn()` |
| Mock return | `.and.returnValue()` | `.mockReturnValue()` |
| Mock implementation | `.and.callFake()` | `.mockImplementation()` |
| Module mocking | Manual DI | `jest.mock()` (auto-hoisted) |
| Snapshot testing | Plugin needed | Built-in |
| Code coverage | Karma + Istanbul | Built-in |
| Speed | Slower (browser-based) | Faster (Node.js) |
| Timer mocking | `jasmine.clock()` | `jest.useFakeTimers()` |
| Angular default | ✅ Yes | Possible with setup |

---

## 🎯 Interview Questions

### Q1: Why does Angular use Jasmine + Karma by default?
**A:** Jasmine provides BDD syntax natural for Angular's testing patterns. Karma runs tests in real browsers ensuring DOM compatibility. This combination provides realistic testing environments, though Angular 16+ supports Jest experimentally for faster unit testing.

### Q2: How do you test an Angular component that has @Input/@Output?
**A:** Set inputs directly on the component instance: `component.title = 'Test'`. For outputs, subscribe to the EventEmitter: `component.clicked.subscribe(val => expect(val).toBe(true))`. Trigger with `fixture.detectChanges()`.

### Q3: What is HttpTestingController and how is it used?
**A:** It's Angular's testing utility that intercepts HTTP requests. You import `HttpClientTestingModule`, inject `HttpTestingController`, then use `expectOne()` to assert requests were made, and `flush()` to provide mock responses. Always call `verify()` in afterEach.

---

## 📝 Practice Exercises

1. Write tests for an Angular `TodoService` with CRUD operations
2. Test a component with `@Input()`, `@Output()`, and async pipe
3. Test an HTTP interceptor that adds auth tokens
4. Test a reactive form with validation
