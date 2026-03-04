# Day 8: Angular Component Testing

## 📚 Topics to Cover (3-4 hours)

---

## 1. TestBed Configuration

```typescript
import { ComponentFixture, TestBed, fakeAsync, tick } from '@angular/core/testing';
import { By } from '@angular/platform-browser';

describe('UserProfileComponent', () => {
  let component: UserProfileComponent;
  let fixture: ComponentFixture<UserProfileComponent>;
  let userService: jasmine.SpyObj<UserService>;

  beforeEach(async () => {
    const spy = jasmine.createSpyObj('UserService', ['getUser', 'updateUser']);

    await TestBed.configureTestingModule({
      imports: [
        ReactiveFormsModule,
        HttpClientTestingModule,
        NoopAnimationsModule,  // Disable animations in tests
      ],
      declarations: [
        UserProfileComponent,
        MockPipe('translate'),  // Mock pipes
      ],
      providers: [
        { provide: UserService, useValue: spy },
        { provide: ActivatedRoute, useValue: { params: of({ id: '123' }) } },
      ],
      schemas: [CUSTOM_ELEMENTS_SCHEMA]  // Ignore unknown elements
    }).compileComponents();

    fixture = TestBed.createComponent(UserProfileComponent);
    component = fixture.componentInstance;
    userService = TestBed.inject(UserService) as jasmine.SpyObj<UserService>;
  });
});
```

---

## 2. Testing @Input and @Output

```typescript
// Component
@Component({
  selector: 'app-counter',
  template: `
    <span data-testid="count">{{ count }}</span>
    <button (click)="increment()">+</button>
    <button (click)="decrement()">-</button>
  `
})
class CounterComponent {
  @Input() count = 0;
  @Output() countChange = new EventEmitter<number>();

  increment() { this.countChange.emit(++this.count); }
  decrement() { this.countChange.emit(--this.count); }
}

// Tests
describe('CounterComponent', () => {
  it('should display initial count', () => {
    component.count = 5;
    fixture.detectChanges();
    
    const el = fixture.debugElement.query(By.css('[data-testid="count"]'));
    expect(el.nativeElement.textContent.trim()).toBe('5');
  });

  it('should emit incremented value', () => {
    component.count = 10;
    spyOn(component.countChange, 'emit');
    
    const btn = fixture.debugElement.queryAll(By.css('button'))[0];
    btn.triggerEventHandler('click', null);
    
    expect(component.countChange.emit).toHaveBeenCalledWith(11);
  });
});
```

---

## 3. Testing Async Operations

```typescript
// fakeAsync + tick
it('should load user after init', fakeAsync(() => {
  const mockUser = { id: 1, name: 'John' };
  userService.getUser.and.returnValue(of(mockUser).pipe(delay(100)));

  fixture.detectChanges(); // triggers ngOnInit
  tick(100);               // fast-forward time
  fixture.detectChanges(); // update DOM

  expect(component.user).toEqual(mockUser);
  expect(fixture.nativeElement.querySelector('.user-name').textContent)
    .toContain('John');
}));

// waitForAsync (real async)
it('should handle async data', waitForAsync(() => {
  userService.getUser.and.returnValue(of({ id: 1, name: 'Jane' }));
  
  fixture.detectChanges();
  
  fixture.whenStable().then(() => {
    fixture.detectChanges();
    expect(component.user.name).toBe('Jane');
  });
}));

// done callback
it('should complete observable', (done) => {
  userService.getUser.and.returnValue(of({ id: 1 }));
  
  component.loadUser().subscribe(user => {
    expect(user.id).toBe(1);
    done();
  });
});
```

---

## 4. Testing Reactive Forms

```typescript
describe('LoginFormComponent', () => {
  it('should create form with email and password', () => {
    fixture.detectChanges();
    expect(component.loginForm.contains('email')).toBeTrue();
    expect(component.loginForm.contains('password')).toBeTrue();
  });

  it('should mark email as invalid when empty', () => {
    fixture.detectChanges();
    const email = component.loginForm.get('email');
    email.setValue('');
    expect(email.valid).toBeFalse();
    expect(email.errors['required']).toBeTruthy();
  });

  it('should validate email format', () => {
    fixture.detectChanges();
    const email = component.loginForm.get('email');
    email.setValue('invalid');
    expect(email.errors['email']).toBeTruthy();
    
    email.setValue('valid@test.com');
    expect(email.valid).toBeTrue();
  });

  it('should submit form with valid data', () => {
    fixture.detectChanges();
    component.loginForm.patchValue({
      email: 'user@test.com',
      password: 'Password123!'
    });

    spyOn(component, 'onSubmit');
    
    const form = fixture.debugElement.query(By.css('form'));
    form.triggerEventHandler('ngSubmit', null);

    expect(component.onSubmit).toHaveBeenCalled();
  });
});
```

---

## 5. Testing Router Navigation

```typescript
describe('NavComponent', () => {
  let router: Router;
  let location: Location;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        RouterTestingModule.withRoutes([
          { path: 'dashboard', component: DashboardComponent },
          { path: 'profile', component: ProfileComponent },
        ])
      ],
      declarations: [NavComponent, DashboardComponent, ProfileComponent]
    }).compileComponents();

    router = TestBed.inject(Router);
    location = TestBed.inject(Location);
  });

  it('should navigate to dashboard', fakeAsync(() => {
    router.navigate(['/dashboard']);
    tick();
    expect(location.path()).toBe('/dashboard');
  }));

  it('should activate correct route', fakeAsync(() => {
    const fixture = TestBed.createComponent(NavComponent);
    router.navigate(['/profile']);
    tick();
    fixture.detectChanges();
    
    const activeLink = fixture.debugElement
      .query(By.css('.active'))
      .nativeElement.textContent;
    expect(activeLink).toContain('Profile');
  }));
});
```

---

## 6. Testing Directives & Pipes

```typescript
// Custom Pipe Test
describe('CurrencyFormatPipe', () => {
  const pipe = new CurrencyFormatPipe();

  it('should format number as currency', () => {
    expect(pipe.transform(1234.5)).toBe('$1,234.50');
  });

  it('should handle zero', () => {
    expect(pipe.transform(0)).toBe('$0.00');
  });
});

// Custom Directive Test
@Component({
  template: `<input appHighlight [highlightColor]="color">`
})
class TestHostComponent {
  color = 'yellow';
}

describe('HighlightDirective', () => {
  let fixture: ComponentFixture<TestHostComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [TestHostComponent, HighlightDirective]
    });
    fixture = TestBed.createComponent(TestHostComponent);
    fixture.detectChanges();
  });

  it('should apply background color', () => {
    const input = fixture.debugElement.query(By.directive(HighlightDirective));
    expect(input.nativeElement.style.backgroundColor).toBe('yellow');
  });
});
```

---

## 🎯 Interview Questions

### Q1: How do you test OnPush change detection components?
**A:** OnPush components only update when inputs change by reference or events fire. In tests: change @Input reference (new object, not mutation), use `fixture.detectChanges()`, or trigger events. Use `fixture.componentRef.injector.get(ChangeDetectorRef).markForCheck()` if needed.

### Q2: What's the difference between `fakeAsync`/`tick` and `waitForAsync`?
**A:** `fakeAsync` gives you control over time (synchronous simulation), ideal for testing timeouts/intervals. `waitForAsync` wraps in a test zone and waits for real async operations. `fakeAsync` is preferred for most Angular tests.

### Q3: How do you test components with complex dependencies?
**A:** Use `jasmine.createSpyObj()` for services, `HttpClientTestingModule` for HTTP, `RouterTestingModule` for routing, `NoopAnimationsModule` for animations. Create test host components for directive testing. Use `CUSTOM_ELEMENTS_SCHEMA` to ignore child components.
