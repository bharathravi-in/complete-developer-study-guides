# Testing Cheatsheet

## TestBed Setup

```typescript
import { TestBed, ComponentFixture } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';

describe('MyComponent', () => {
  let component: MyComponent;
  let fixture: ComponentFixture<MyComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MyComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        { provide: MyService, useValue: mockService }
      ]
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

## Component Testing

```typescript
describe('UserListComponent', () => {
  let component: UserListComponent;
  let fixture: ComponentFixture<UserListComponent>;
  let userService: jasmine.SpyObj<UserService>;

  beforeEach(async () => {
    userService = jasmine.createSpyObj('UserService', ['getUsers', 'deleteUser']);
    userService.getUsers.and.returnValue(of([mockUser]));

    await TestBed.configureTestingModule({
      imports: [UserListComponent],
      providers: [{ provide: UserService, useValue: userService }]
    }).compileComponents();

    fixture = TestBed.createComponent(UserListComponent);
    component = fixture.componentInstance;
  });

  it('should load users on init', () => {
    fixture.detectChanges();
    expect(userService.getUsers).toHaveBeenCalled();
    expect(component.users()).toEqual([mockUser]);
  });

  it('should display users in template', () => {
    fixture.detectChanges();
    const userElements = fixture.nativeElement.querySelectorAll('.user-item');
    expect(userElements.length).toBe(1);
    expect(userElements[0].textContent).toContain(mockUser.name);
  });

  it('should delete user when delete clicked', () => {
    userService.deleteUser.and.returnValue(of(void 0));
    fixture.detectChanges();

    const deleteBtn = fixture.nativeElement.querySelector('.delete-btn');
    deleteBtn.click();

    expect(userService.deleteUser).toHaveBeenCalledWith(mockUser.id);
  });
});
```

## Testing with Inputs/Outputs

```typescript
describe('UserCardComponent', () => {
  let component: UserCardComponent;
  let fixture: ComponentFixture<UserCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserCardComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(UserCardComponent);
    component = fixture.componentInstance;
  });

  it('should display user name from input', () => {
    // Using setInput for signal inputs (Angular 17.1+)
    fixture.componentRef.setInput('user', mockUser);
    fixture.detectChanges();

    const nameEl = fixture.nativeElement.querySelector('.name');
    expect(nameEl.textContent).toContain(mockUser.name);
  });

  it('should emit when edit clicked', () => {
    fixture.componentRef.setInput('user', mockUser);
    fixture.detectChanges();

    const editSpy = jasmine.createSpy('editSpy');
    component.edit.subscribe(editSpy);

    const editBtn = fixture.nativeElement.querySelector('.edit-btn');
    editBtn.click();

    expect(editSpy).toHaveBeenCalledWith(mockUser);
  });
});
```

## Testing Services

```typescript
describe('UserService', () => {
  let service: UserService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [
        UserService,
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

  it('should get users', () => {
    const mockUsers = [{ id: '1', name: 'John' }];

    service.getUsers().subscribe(users => {
      expect(users).toEqual(mockUsers);
    });

    const req = httpMock.expectOne('/api/users');
    expect(req.request.method).toBe('GET');
    req.flush(mockUsers);
  });

  it('should create user', () => {
    const newUser = { name: 'Jane', email: 'jane@test.com' };
    const createdUser = { id: '2', ...newUser };

    service.createUser(newUser).subscribe(user => {
      expect(user).toEqual(createdUser);
    });

    const req = httpMock.expectOne('/api/users');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual(newUser);
    req.flush(createdUser);
  });

  it('should handle error', () => {
    service.getUsers().subscribe({
      error: err => {
        expect(err.status).toBe(500);
      }
    });

    const req = httpMock.expectOne('/api/users');
    req.flush('Server Error', { status: 500, statusText: 'Server Error' });
  });
});
```

## Testing Async Code

```typescript
describe('AsyncComponent', () => {
  // fakeAsync + tick
  it('should update after debounce', fakeAsync(() => {
    component.search('test');
    tick(300);  // Advance time by 300ms
    fixture.detectChanges();
    expect(component.results().length).toBeGreaterThan(0);
  }));

  // fakeAsync with flush
  it('should complete all async operations', fakeAsync(() => {
    component.loadData();
    flush();  // Flush all pending async
    fixture.detectChanges();
    expect(component.data()).toBeTruthy();
  }));

  // waitForAsync
  it('should load data', waitForAsync(() => {
    component.loadData();
    fixture.whenStable().then(() => {
      expect(component.data()).toBeTruthy();
    });
  }));

  // done callback
  it('should complete observable', (done) => {
    component.data$.subscribe(data => {
      expect(data).toBeTruthy();
      done();
    });
    component.loadData();
  });
});
```

## Testing Forms

```typescript
describe('LoginFormComponent', () => {
  let component: LoginFormComponent;
  let fixture: ComponentFixture<LoginFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoginFormComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(LoginFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should be invalid when empty', () => {
    expect(component.form.valid).toBeFalse();
  });

  it('should be valid with correct values', () => {
    component.form.patchValue({
      email: 'test@test.com',
      password: 'password123'
    });
    expect(component.form.valid).toBeTrue();
  });

  it('should show email error when invalid', () => {
    const emailCtrl = component.form.get('email')!;
    emailCtrl.setValue('invalid');
    emailCtrl.markAsTouched();
    fixture.detectChanges();

    const errorEl = fixture.nativeElement.querySelector('.email-error');
    expect(errorEl).toBeTruthy();
  });

  it('should call submit when form is valid', () => {
    const submitSpy = spyOn(component, 'onSubmit');
    
    component.form.patchValue({
      email: 'test@test.com',
      password: 'password123'
    });
    fixture.detectChanges();

    const form = fixture.nativeElement.querySelector('form');
    form.dispatchEvent(new Event('submit'));

    expect(submitSpy).toHaveBeenCalled();
  });
});
```

## Testing Signals

```typescript
describe('CounterComponent with Signals', () => {
  let component: CounterComponent;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [CounterComponent]
    });
    const fixture = TestBed.createComponent(CounterComponent);
    component = fixture.componentInstance;
  });

  it('should increment count', () => {
    expect(component.count()).toBe(0);
    
    component.increment();
    expect(component.count()).toBe(1);
  });

  it('should compute doubled value', () => {
    component.count.set(5);
    expect(component.doubled()).toBe(10);
  });

  it('should run effect', () => {
    const consoleSpy = spyOn(console, 'log');
    
    TestBed.runInInjectionContext(() => {
      effect(() => {
        console.log(component.count());
      });
    });

    TestBed.flushEffects();
    component.count.set(5);
    TestBed.flushEffects();

    expect(consoleSpy).toHaveBeenCalledWith(5);
  });
});
```

## Testing Routing

```typescript
describe('AppComponent routing', () => {
  let router: Router;
  let location: Location;
  let fixture: ComponentFixture<AppComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [
        provideRouter([
          { path: '', component: HomeComponent },
          { path: 'about', component: AboutComponent }
        ])
      ]
    }).compileComponents();

    router = TestBed.inject(Router);
    location = TestBed.inject(Location);
    fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
  });

  it('should navigate to about', fakeAsync(() => {
    router.navigate(['/about']);
    tick();
    expect(location.path()).toBe('/about');
  }));

  it('should display about component', fakeAsync(() => {
    router.navigate(['/about']);
    tick();
    fixture.detectChanges();

    const aboutEl = fixture.nativeElement.querySelector('app-about');
    expect(aboutEl).toBeTruthy();
  }));
});
```

## Mocking Techniques

```typescript
// Spy object
const userService = jasmine.createSpyObj('UserService', ['getUsers', 'deleteUser']);
userService.getUsers.and.returnValue(of(mockUsers));

// Partial mock
const partialMock: Partial<UserService> = {
  getUsers: () => of(mockUsers)
};

// Jest mock (if using Jest)
const mockService = {
  getUsers: jest.fn().mockReturnValue(of(mockUsers))
};

// Mock class
class MockUserService {
  getUsers() { return of(mockUsers); }
}
{ provide: UserService, useClass: MockUserService }

// Mock value
{ provide: UserService, useValue: mockService }

// Spying on method
spyOn(component, 'submit').and.callThrough();
```

## Common Matchers

```typescript
// Jasmine matchers
expect(value).toBe(expected);           // ===
expect(value).toEqual(expected);        // Deep equality
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toContain(item);
expect(value).toBeGreaterThan(3);
expect(array).toHaveSize(3);
expect(spy).toHaveBeenCalled();
expect(spy).toHaveBeenCalledWith(arg);
expect(spy).toHaveBeenCalledTimes(2);
expect(fn).toThrow();
expect(fn).toThrowError('message');
```

## Running Tests

```bash
# Run all tests
ng test

# Run with coverage
ng test --code-coverage

# Run specific file
ng test --include=**/user.service.spec.ts

# Watch mode off
ng test --watch=false

# Run in CI
ng test --watch=false --browsers=ChromeHeadless
```
