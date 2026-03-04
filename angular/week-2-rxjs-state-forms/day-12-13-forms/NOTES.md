# Day 12-13: Angular Forms - Complete Guide

## Overview

Angular provides two approaches for handling forms:
1. **Template-driven forms** - Simple, declarative, uses directives
2. **Reactive forms** - Programmatic, explicit, uses RxJS

---

## Template-Driven Forms

### Setup

```typescript
// app.config.ts (Standalone)
import { provideFormsModule } from '@angular/forms';

export const appConfig: ApplicationConfig = {
  providers: [
    provideFormsModule()
  ]
};

// Or in component
@Component({
  standalone: true,
  imports: [FormsModule],
  // ...
})
```

### Basic Template-Driven Form

```typescript
// user-form.component.ts
import { Component } from '@angular/core';
import { FormsModule, NgForm } from '@angular/forms';

@Component({
  selector: 'app-user-form',
  standalone: true,
  imports: [FormsModule],
  template: `
    <form #userForm="ngForm" (ngSubmit)="onSubmit(userForm)">
      <div class="form-group">
        <label for="name">Name</label>
        <input 
          type="text" 
          id="name"
          name="name"
          [(ngModel)]="user.name"
          required
          minlength="3"
          #name="ngModel"
        >
        <div *ngIf="name.invalid && name.touched" class="error">
          <span *ngIf="name.errors?.['required']">Name is required</span>
          <span *ngIf="name.errors?.['minlength']">
            Min length: {{ name.errors?.['minlength'].requiredLength }}
          </span>
        </div>
      </div>

      <div class="form-group">
        <label for="email">Email</label>
        <input 
          type="email" 
          id="email"
          name="email"
          [(ngModel)]="user.email"
          required
          email
          #email="ngModel"
        >
        <div *ngIf="email.invalid && email.touched" class="error">
          <span *ngIf="email.errors?.['required']">Email is required</span>
          <span *ngIf="email.errors?.['email']">Invalid email format</span>
        </div>
      </div>

      <div class="form-group">
        <label for="age">Age</label>
        <input 
          type="number" 
          id="age"
          name="age"
          [(ngModel)]="user.age"
          min="18"
          max="100"
          #age="ngModel"
        >
      </div>

      <button type="submit" [disabled]="userForm.invalid">Submit</button>
      
      <pre>Form Valid: {{ userForm.valid }}</pre>
      <pre>Form Value: {{ userForm.value | json }}</pre>
    </form>
  `
})
export class UserFormComponent {
  user = {
    name: '',
    email: '',
    age: null
  };

  onSubmit(form: NgForm) {
    if (form.valid) {
      console.log('Form submitted:', form.value);
      // Process form data
      form.reset(); // Reset form after submission
    }
  }
}
```

### NgModel States

```
┌─────────────────────────────────────────────────────────────┐
│                    NgModel Control States                    │
├─────────────────┬───────────────────────────────────────────┤
│ Property        │ Description                               │
├─────────────────┼───────────────────────────────────────────┤
│ pristine        │ True if user has NOT changed the value    │
│ dirty           │ True if user HAS changed the value        │
│ touched         │ True if control has been focused & blurred│
│ untouched       │ True if control has NOT been blurred      │
│ valid           │ True if all validators pass               │
│ invalid         │ True if any validator fails               │
│ pending         │ True if async validators are running      │
├─────────────────┼───────────────────────────────────────────┤
│ CSS Classes     │                                           │
├─────────────────┼───────────────────────────────────────────┤
│ ng-pristine     │ Applied when pristine = true              │
│ ng-dirty        │ Applied when dirty = true                 │
│ ng-touched      │ Applied when touched = true               │
│ ng-untouched    │ Applied when untouched = true             │
│ ng-valid        │ Applied when valid = true                 │
│ ng-invalid      │ Applied when invalid = true               │
│ ng-pending      │ Applied when pending = true               │
└─────────────────┴───────────────────────────────────────────┘
```

---

## Reactive Forms

### Setup

```typescript
// Component with Reactive Forms
import { Component } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';

@Component({
  standalone: true,
  imports: [ReactiveFormsModule],
  // ...
})
```

### Basic Reactive Form

```typescript
// registration.component.ts
import { Component, OnInit, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-registration',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  template: `
    <form [formGroup]="registrationForm" (ngSubmit)="onSubmit()">
      <div class="form-group">
        <label>Username</label>
        <input type="text" formControlName="username">
        <div *ngIf="username.invalid && username.touched" class="error">
          <span *ngIf="username.errors?.['required']">Required</span>
          <span *ngIf="username.errors?.['minlength']">
            Min {{ username.errors?.['minlength'].requiredLength }} characters
          </span>
        </div>
      </div>

      <div class="form-group">
        <label>Email</label>
        <input type="email" formControlName="email">
        <div *ngIf="email.invalid && email.touched" class="error">
          <span *ngIf="email.errors?.['required']">Required</span>
          <span *ngIf="email.errors?.['email']">Invalid email</span>
        </div>
      </div>

      <div formGroupName="passwordGroup">
        <div class="form-group">
          <label>Password</label>
          <input type="password" formControlName="password">
        </div>
        <div class="form-group">
          <label>Confirm Password</label>
          <input type="password" formControlName="confirmPassword">
        </div>
        <div *ngIf="passwordGroup.errors?.['passwordMismatch']" class="error">
          Passwords do not match
        </div>
      </div>

      <button type="submit" [disabled]="registrationForm.invalid">
        Register
      </button>
    </form>
  `
})
export class RegistrationComponent implements OnInit {
  private fb = inject(FormBuilder);
  registrationForm!: FormGroup;

  ngOnInit() {
    this.registrationForm = this.fb.group({
      username: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      passwordGroup: this.fb.group({
        password: ['', [Validators.required, Validators.minLength(8)]],
        confirmPassword: ['', Validators.required]
      }, { validators: this.passwordMatchValidator })
    });
  }

  // Custom Validator for password match
  passwordMatchValidator(group: FormGroup): { [key: string]: boolean } | null {
    const password = group.get('password')?.value;
    const confirmPassword = group.get('confirmPassword')?.value;
    return password === confirmPassword ? null : { passwordMismatch: true };
  }

  // Getters for easy template access
  get username() { return this.registrationForm.get('username')!; }
  get email() { return this.registrationForm.get('email')!; }
  get passwordGroup() { return this.registrationForm.get('passwordGroup')!; }

  onSubmit() {
    if (this.registrationForm.valid) {
      console.log(this.registrationForm.value);
    } else {
      this.markAllAsTouched();
    }
  }

  private markAllAsTouched() {
    Object.keys(this.registrationForm.controls).forEach(key => {
      this.registrationForm.get(key)?.markAsTouched();
    });
  }
}
```

---

## FormArray - Dynamic Forms

```typescript
// dynamic-form.component.ts
import { Component, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, FormArray, Validators } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-dynamic-form',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  template: `
    <form [formGroup]="orderForm" (ngSubmit)="onSubmit()">
      <h3>Customer Info</h3>
      <input formControlName="customerName" placeholder="Customer Name">

      <h3>Order Items</h3>
      <div formArrayName="items">
        @for (item of items.controls; track item; let i = $index) {
          <div [formGroupName]="i" class="item-row">
            <input formControlName="productName" placeholder="Product">
            <input formControlName="quantity" type="number" placeholder="Qty">
            <input formControlName="price" type="number" placeholder="Price">
            <span>Total: {{ getItemTotal(i) | currency }}</span>
            <button type="button" (click)="removeItem(i)">Remove</button>
          </div>
        }
      </div>

      <button type="button" (click)="addItem()">Add Item</button>

      <h3>Order Total: {{ getOrderTotal() | currency }}</h3>

      <button type="submit" [disabled]="orderForm.invalid">Place Order</button>
    </form>
  `
})
export class DynamicFormComponent {
  private fb = inject(FormBuilder);

  orderForm = this.fb.group({
    customerName: ['', Validators.required],
    items: this.fb.array([])
  });

  get items(): FormArray {
    return this.orderForm.get('items') as FormArray;
  }

  createItem() {
    return this.fb.group({
      productName: ['', Validators.required],
      quantity: [1, [Validators.required, Validators.min(1)]],
      price: [0, [Validators.required, Validators.min(0)]]
    });
  }

  addItem() {
    this.items.push(this.createItem());
  }

  removeItem(index: number) {
    this.items.removeAt(index);
  }

  getItemTotal(index: number): number {
    const item = this.items.at(index);
    return item.get('quantity')?.value * item.get('price')?.value || 0;
  }

  getOrderTotal(): number {
    return this.items.controls.reduce((total, item, index) => {
      return total + this.getItemTotal(index);
    }, 0);
  }

  onSubmit() {
    console.log(this.orderForm.value);
  }
}
```

---

## Custom Validators

### Synchronous Validators

```typescript
// validators/custom.validators.ts
import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

// Simple validator function
export function noWhitespace(control: AbstractControl): ValidationErrors | null {
  if (control.value && control.value.trim().length === 0) {
    return { whitespace: true };
  }
  return null;
}

// Validator factory (when you need parameters)
export function minAge(age: number): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    if (control.value && control.value < age) {
      return { minAge: { requiredAge: age, actualAge: control.value } };
    }
    return null;
  };
}

// Pattern-based validator
export function phoneNumber(control: AbstractControl): ValidationErrors | null {
  const phoneRegex = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
  if (control.value && !phoneRegex.test(control.value)) {
    return { invalidPhone: true };
  }
  return null;
}

// Cross-field validator (for FormGroup)
export function dateRange(startField: string, endField: string): ValidatorFn {
  return (group: AbstractControl): ValidationErrors | null => {
    const start = group.get(startField)?.value;
    const end = group.get(endField)?.value;
    
    if (start && end && new Date(start) > new Date(end)) {
      return { dateRange: { message: 'Start date must be before end date' } };
    }
    return null;
  };
}

// Usage
@Component({...})
export class FormComponent {
  form = this.fb.group({
    name: ['', [Validators.required, noWhitespace]],
    age: ['', [Validators.required, minAge(18)]],
    phone: ['', phoneNumber],
    startDate: [''],
    endDate: ['']
  }, { validators: dateRange('startDate', 'endDate') });
}
```

### Async Validators

```typescript
// validators/async.validators.ts
import { AbstractControl, AsyncValidatorFn, ValidationErrors } from '@angular/forms';
import { Observable, of, timer } from 'rxjs';
import { map, switchMap, catchError } from 'rxjs/operators';
import { inject } from '@angular/core';

// Async validator as function
export function uniqueUsername(userService: UserService): AsyncValidatorFn {
  return (control: AbstractControl): Observable<ValidationErrors | null> => {
    if (!control.value) {
      return of(null);
    }

    // Debounce to avoid too many API calls
    return timer(500).pipe(
      switchMap(() => userService.checkUsername(control.value)),
      map(exists => exists ? { usernameTaken: true } : null),
      catchError(() => of(null)) // Handle errors gracefully
    );
  };
}

// Async validator as injectable class
@Injectable({ providedIn: 'root' })
export class UniqueEmailValidator {
  private userService = inject(UserService);

  validate(): AsyncValidatorFn {
    return (control: AbstractControl): Observable<ValidationErrors | null> => {
      return timer(300).pipe(
        switchMap(() => this.userService.checkEmail(control.value)),
        map(exists => exists ? { emailTaken: true } : null),
        catchError(() => of(null))
      );
    };
  }
}

// Usage in component
@Component({...})
export class RegistrationComponent {
  private userService = inject(UserService);
  private emailValidator = inject(UniqueEmailValidator);

  form = this.fb.group({
    username: ['', 
      [Validators.required], 
      [uniqueUsername(this.userService)]  // Async validators
    ],
    email: ['',
      [Validators.required, Validators.email],
      [this.emailValidator.validate()]
    ]
  });
}
```

---

## Form Validation Patterns

### Show Errors Component (Reusable)

```typescript
// components/form-errors.component.ts
import { Component, Input } from '@angular/core';
import { AbstractControl } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-form-errors',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (control && control.invalid && (control.dirty || control.touched)) {
      <div class="error-messages">
        @if (control.errors?.['required']) {
          <span>{{ fieldName }} is required</span>
        }
        @if (control.errors?.['minlength']) {
          <span>
            Minimum {{ control.errors?.['minlength'].requiredLength }} characters
          </span>
        }
        @if (control.errors?.['maxlength']) {
          <span>
            Maximum {{ control.errors?.['maxlength'].requiredLength }} characters
          </span>
        }
        @if (control.errors?.['email']) {
          <span>Invalid email format</span>
        }
        @if (control.errors?.['pattern']) {
          <span>Invalid format</span>
        }
        @if (control.errors?.['min']) {
          <span>Minimum value: {{ control.errors?.['min'].min }}</span>
        }
        @if (control.errors?.['max']) {
          <span>Maximum value: {{ control.errors?.['max'].max }}</span>
        }
        <!-- Custom errors -->
        @if (control.errors?.['usernameTaken']) {
          <span>Username is already taken</span>
        }
        @if (control.errors?.['emailTaken']) {
          <span>Email is already registered</span>
        }
      </div>
    }
  `,
  styles: [`
    .error-messages {
      color: red;
      font-size: 12px;
      margin-top: 4px;
    }
    .error-messages span {
      display: block;
    }
  `]
})
export class FormErrorsComponent {
  @Input() control!: AbstractControl;
  @Input() fieldName = 'Field';
}
```

---

## Advanced Form Techniques

### Form with Signals (Angular 17+)

```typescript
import { Component, signal, computed } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'app-signal-form',
  standalone: true,
  imports: [ReactiveFormsModule],
  template: `
    <form [formGroup]="form">
      <input formControlName="search" placeholder="Search...">
      <p>You typed: {{ searchValue() }}</p>
      <p>Character count: {{ charCount() }}</p>
    </form>
  `
})
export class SignalFormComponent {
  private fb = inject(FormBuilder);
  
  form = this.fb.group({
    search: ['']
  });

  // Convert form value to signal
  searchValue = toSignal(
    this.form.controls.search.valueChanges,
    { initialValue: '' }
  );

  // Computed signal based on form value
  charCount = computed(() => this.searchValue()?.length || 0);
}
```

### ControlValueAccessor - Custom Form Control

```typescript
// components/star-rating.component.ts
import { Component, forwardRef, Input } from '@angular/core';
import { ControlValueAccessor, NG_VALUE_ACCESSOR } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-star-rating',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="star-rating" [class.disabled]="disabled">
      @for (star of stars; track star) {
        <span 
          class="star"
          [class.filled]="star <= value"
          (click)="!disabled && setRating(star)"
          (mouseenter)="!disabled && hover = star"
          (mouseleave)="!disabled && hover = 0"
          [class.hovered]="star <= hover"
        >
          ★
        </span>
      }
    </div>
    <span class="rating-text">{{ value }} / {{ maxStars }}</span>
  `,
  styles: [`
    .star-rating { display: inline-flex; cursor: pointer; }
    .star { font-size: 24px; color: #ddd; transition: 0.2s; }
    .star.filled, .star.hovered { color: gold; }
    .disabled { cursor: not-allowed; opacity: 0.5; }
  `],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => StarRatingComponent),
      multi: true
    }
  ]
})
export class StarRatingComponent implements ControlValueAccessor {
  @Input() maxStars = 5;
  
  value = 0;
  hover = 0;
  disabled = false;
  
  stars: number[] = [];

  private onChange: (value: number) => void = () => {};
  private onTouched: () => void = () => {};

  ngOnInit() {
    this.stars = Array.from({ length: this.maxStars }, (_, i) => i + 1);
  }

  setRating(rating: number) {
    this.value = rating;
    this.onChange(this.value);
    this.onTouched();
  }

  // ControlValueAccessor implementation
  writeValue(value: number): void {
    this.value = value || 0;
  }

  registerOnChange(fn: (value: number) => void): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }
}

// Usage in a form
@Component({
  template: `
    <form [formGroup]="form">
      <app-star-rating formControlName="rating"></app-star-rating>
    </form>
  `
})
export class ProductReviewComponent {
  form = this.fb.group({
    rating: [0, [Validators.required, Validators.min(1)]]
  });
}
```

---

## Form Patterns Summary

```
┌────────────────────────────────────────────────────────────────────┐
│                     Form Pattern Decision Tree                      │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Simple form? ────► Yes ────► Template-driven forms                │
│       │                                                             │
│       No                                                            │
│       │                                                             │
│       ▼                                                             │
│  Complex validation? ────► Yes ────► Reactive forms                │
│       │                              + Custom validators            │
│       No                                                            │
│       │                                                             │
│       ▼                                                             │
│  Dynamic fields? ────► Yes ────► Reactive forms + FormArray        │
│       │                                                             │
│       No                                                            │
│       │                                                             │
│       ▼                                                             │
│  Async validation? ────► Yes ────► Reactive forms                  │
│       │                            + AsyncValidatorFn               │
│       No                                                            │
│       │                                                             │
│       ▼                                                             │
│  Cross-field validation? ────► Reactive forms                      │
│                                + FormGroup validators               │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Key Takeaways for Interviews

1. **Template-driven**: Uses `ngModel`, good for simple forms
2. **Reactive**: Uses `FormGroup/FormControl`, better for complex forms
3. **FormArray**: For dynamic lists of controls
4. **Custom validators**: Sync and async
5. **ControlValueAccessor**: For custom form controls
6. **Always validate server-side** - client validation is for UX only
