# Routing & Forms Cheatsheet

## Routing Configuration

```typescript
// app.routes.ts
export const routes: Routes = [
  // Redirect
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  
  // Basic route
  { path: 'home', component: HomeComponent },
  
  // Lazy load component
  { 
    path: 'products', 
    loadComponent: () => import('./products/products.component')
  },
  
  // Lazy load routes
  {
    path: 'admin',
    loadChildren: () => import('./admin/admin.routes').then(m => m.ADMIN_ROUTES)
  },
  
  // Route with parameter
  { path: 'products/:id', component: ProductDetailComponent },
  
  // Protected route
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [authGuard],
    canDeactivate: [unsavedChangesGuard]
  },
  
  // Route with resolver
  {
    path: 'user/:id',
    component: UserComponent,
    resolve: { user: userResolver }
  },
  
  // Nested routes
  {
    path: 'account',
    component: AccountLayoutComponent,
    children: [
      { path: '', redirectTo: 'profile', pathMatch: 'full' },
      { path: 'profile', component: ProfileComponent },
      { path: 'settings', component: SettingsComponent }
    ]
  },
  
  // Wildcard (404)
  { path: '**', component: NotFoundComponent }
];

// app.config.ts
provideRouter(routes,
  withViewTransitions(),          // Page transitions
  withComponentInputBinding(),    // Route params as inputs
  withPreloading(PreloadAllModules)  // Preload lazy routes
)
```

## Guards

```typescript
// Auth guard
export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  
  if (auth.isLoggedIn()) {
    return true;
  }
  
  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url }
  });
};

// Role guard
export const roleGuard: CanActivateFn = (route) => {
  const auth = inject(AuthService);
  const requiredRole = route.data['role'];
  
  return auth.hasRole(requiredRole);
};

// Unsaved changes guard
export const unsavedChangesGuard: CanDeactivateFn<HasUnsavedChanges> = (component) => {
  if (component.hasUnsavedChanges()) {
    return confirm('You have unsaved changes. Leave anyway?');
  }
  return true;
};

// Child routes guard
export const canActivateChild: CanActivateChildFn = (route, state) => {
  return inject(AuthService).isLoggedIn();
};

// Route matching guard
export const canMatchGuard: CanMatchFn = (route, segments) => {
  return inject(FeatureService).isFeatureEnabled(route.data['feature']);
};
```

## Resolvers

```typescript
// Function resolver
export const userResolver: ResolveFn<User> = (route) => {
  const id = route.params['id'];
  return inject(UserService).getUser(id);
};

// With error handling
export const productResolver: ResolveFn<Product | null> = (route) => {
  const id = route.params['id'];
  return inject(ProductService).getProduct(id).pipe(
    catchError(() => of(null))
  );
};

// Usage in component
@Component({...})
export class UserComponent {
  route = inject(ActivatedRoute);
  user = this.route.snapshot.data['user'];
  // Or reactive:
  // user$ = this.route.data.pipe(map(d => d['user']));
}
```

## Navigation

```typescript
@Component({...})
export class NavComponent {
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  // Navigate by URL
  goHome() {
    this.router.navigate(['/home']);
  }

  // Navigate with parameters
  goToProduct(id: string) {
    this.router.navigate(['/products', id]);
  }

  // Navigate with query params
  search(term: string) {
    this.router.navigate(['/search'], {
      queryParams: { q: term, page: 1 }
    });
  }

  // Navigate relative to current route
  goToChild() {
    this.router.navigate(['child'], { relativeTo: this.route });
  }

  // Navigate and replace history
  replace() {
    this.router.navigate(['/new'], { replaceUrl: true });
  }

  // Navigate preserving query params
  preserveQuery() {
    this.router.navigate(['/other'], { queryParamsHandling: 'preserve' });
  }
}
```

```html
<!-- Template navigation -->
<a routerLink="/home">Home</a>
<a [routerLink]="['/products', product.id]">{{ product.name }}</a>
<a routerLink="/search" [queryParams]="{ q: 'angular' }">Search</a>
<a routerLink="child" routerLinkActive="active">Child</a>

<!-- With active class -->
<a routerLink="/home" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">
  Home
</a>
```

## Reading Route Data

```typescript
@Component({...})
export class ProductComponent {
  route = inject(ActivatedRoute);

  // Snapshot (one-time read)
  id = this.route.snapshot.params['id'];
  query = this.route.snapshot.queryParams['filter'];
  data = this.route.snapshot.data['product'];

  // Observable (reactive to changes)
  id$ = this.route.params.pipe(map(p => p['id']));
  query$ = this.route.queryParams.pipe(map(q => q['filter']));
  
  // With component input binding (app.config)
  // Enable: withComponentInputBinding()
  id = input<string>();  // From :id param
}
```

---

# Forms

## Reactive Forms

```typescript
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';

@Component({
  imports: [ReactiveFormsModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()">
      <input formControlName="name">
      @if (form.get('name')?.errors?.['required'] && form.get('name')?.touched) {
        <span class="error">Name is required</span>
      }
      
      <input formControlName="email" type="email">
      
      <div formGroupName="address">
        <input formControlName="street">
        <input formControlName="city">
      </div>
      
      <button [disabled]="form.invalid">Submit</button>
    </form>
  `
})
export class MyFormComponent {
  private fb = inject(FormBuilder);
  
  form = this.fb.nonNullable.group({
    name: ['', [Validators.required, Validators.minLength(2)]],
    email: ['', [Validators.required, Validators.email]],
    address: this.fb.group({
      street: [''],
      city: ['', Validators.required]
    })
  });

  submit() {
    if (this.form.valid) {
      console.log(this.form.getRawValue());
    }
  }
}
```

## Form Arrays

```typescript
@Component({
  template: `
    <form [formGroup]="form">
      <div formArrayName="phones">
        @for (phone of phones.controls; track $index; let i = $index) {
          <div [formGroupName]="i">
            <input formControlName="type">
            <input formControlName="number">
            <button type="button" (click)="removePhone(i)">Remove</button>
          </div>
        }
      </div>
      <button type="button" (click)="addPhone()">Add Phone</button>
    </form>
  `
})
export class PhoneFormComponent {
  private fb = inject(FormBuilder);
  
  form = this.fb.group({
    phones: this.fb.array([])
  });

  get phones() {
    return this.form.get('phones') as FormArray;
  }

  addPhone() {
    this.phones.push(this.fb.group({
      type: ['mobile'],
      number: ['', Validators.required]
    }));
  }

  removePhone(index: number) {
    this.phones.removeAt(index);
  }
}
```

## Custom Validators

```typescript
// Sync validator
export function noWhitespace(control: AbstractControl): ValidationErrors | null {
  const hasWhitespace = control.value?.includes(' ');
  return hasWhitespace ? { whitespace: true } : null;
}

// Async validator
export function uniqueUsername(userService: UserService): AsyncValidatorFn {
  return (control: AbstractControl): Observable<ValidationErrors | null> => {
    return userService.checkUsername(control.value).pipe(
      map(exists => exists ? { usernameTaken: true } : null),
      catchError(() => of(null))
    );
  };
}

// Cross-field validator
export function passwordMatch(control: AbstractControl): ValidationErrors | null {
  const password = control.get('password')?.value;
  const confirm = control.get('confirmPassword')?.value;
  return password === confirm ? null : { passwordMismatch: true };
}

// Usage
form = this.fb.group({
  username: ['', [Validators.required, noWhitespace], [uniqueUsername(this.userService)]],
  password: ['', Validators.required],
  confirmPassword: ['']
}, { validators: passwordMatch });
```

## Template-Driven Forms

```typescript
@Component({
  imports: [FormsModule],
  template: `
    <form #myForm="ngForm" (ngSubmit)="submit(myForm)">
      <input name="name" [(ngModel)]="user.name" required minlength="2" #name="ngModel">
      @if (name.invalid && name.touched) {
        <span class="error">Name is required (min 2 chars)</span>
      }
      
      <input name="email" [(ngModel)]="user.email" required email>
      
      <button [disabled]="myForm.invalid">Submit</button>
    </form>
  `
})
export class TemplateFormComponent {
  user = { name: '', email: '' };

  submit(form: NgForm) {
    if (form.valid) {
      console.log(form.value);
    }
  }
}
```

## Form Control States

```typescript
// Access control
const name = this.form.get('name');

// States
name.valid        // Passes all validators
name.invalid      // Fails validation
name.pending      // Async validation in progress
name.disabled     // Control is disabled
name.enabled      // Control is enabled
name.pristine     // Value not changed by user
name.dirty        // Value changed by user
name.touched      // Control has been focused
name.untouched    // Control has not been focused

// Errors
name.errors       // { required: true, minlength: { requiredLength: 2 } }
name.hasError('required')
name.getError('minlength')?.requiredLength

// Programmatic updates
name.setValue('John');
this.form.patchValue({ name: 'John' });
this.form.reset();
this.form.markAllAsTouched();
name.enable();
name.disable();
```

## Form Error Messages

```html
<input formControlName="email">
@if (form.get('email')?.touched) {
  @if (form.get('email')?.hasError('required')) {
    <span class="error">Email is required</span>
  } @else if (form.get('email')?.hasError('email')) {
    <span class="error">Invalid email format</span>
  }
}

<!-- Or with helper -->
<span class="error">{{ getErrorMessage('email') }}</span>
```

```typescript
getErrorMessage(field: string): string {
  const control = this.form.get(field);
  if (!control?.errors) return '';
  
  const errors: Record<string, string> = {
    required: 'This field is required',
    email: 'Invalid email format',
    minlength: `Minimum ${control.errors['minlength']?.requiredLength} characters`,
    pattern: 'Invalid format'
  };
  
  const errorKey = Object.keys(control.errors)[0];
  return errors[errorKey] || 'Invalid value';
}
```
