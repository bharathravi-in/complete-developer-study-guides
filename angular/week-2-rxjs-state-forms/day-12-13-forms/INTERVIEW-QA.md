# Day 12-13: Forms - Interview Questions & Answers

## Basic Level

### Q1: What's the difference between Template-driven and Reactive forms?

**Answer:**
```
┌──────────────────┬─────────────────────────┬─────────────────────────┐
│ Aspect           │ Template-driven         │ Reactive                │
├──────────────────┼─────────────────────────┼─────────────────────────┤
│ Setup            │ FormsModule             │ ReactiveFormsModule     │
│ Form model       │ Created by directives   │ Created in component    │
│ Data model       │ Two-way binding         │ Immutable, RxJS         │
│ Validation       │ Directives (required)   │ Functions in component  │
│ Testing          │ Template needed (harder)│ No template (easier)    │
│ Scalability      │ Simple forms            │ Complex forms           │
│ Async validation │ Harder                  │ Built-in support        │
│ Dynamic forms    │ Not practical           │ FormArray support       │
└──────────────────┴─────────────────────────┴─────────────────────────┘
```

**When to use which:**
- **Template-driven**: Simple login/signup forms, basic data entry
- **Reactive**: Complex forms, dynamic fields, heavy validation

---

### Q2: What are the states of a form control?

**Answer:**
Form controls track both user interaction and validation states:

```typescript
// Interaction states
control.pristine    // true if never changed by user
control.dirty       // true if changed by user
control.touched     // true if focused then blurred
control.untouched   // true if never focused

// Validation states
control.valid       // true if all validators pass
control.invalid     // true if any validator fails
control.pending     // true if async validators running
control.errors      // object containing validation errors

// CSS classes added automatically
.ng-pristine / .ng-dirty
.ng-touched / .ng-untouched
.ng-valid / .ng-invalid
.ng-pending
```

---

### Q3: How do you create a FormGroup with nested groups?

**Answer:**
```typescript
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({...})
export class ProfileComponent {
  private fb = inject(FormBuilder);

  profileForm = this.fb.group({
    // Basic fields
    firstName: ['', Validators.required],
    lastName: ['', Validators.required],
    
    // Nested group
    address: this.fb.group({
      street: [''],
      city: ['', Validators.required],
      state: [''],
      zip: ['', [Validators.required, Validators.pattern(/^\d{5}$/)]]
    }),
    
    // Another nested group
    contact: this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      phone: ['']
    })
  });
}
```

Template:
```html
<form [formGroup]="profileForm">
  <input formControlName="firstName">
  <input formControlName="lastName">
  
  <!-- Nested group -->
  <div formGroupName="address">
    <input formControlName="street">
    <input formControlName="city">
    <input formControlName="state">
    <input formControlName="zip">
  </div>
</form>
```

---

### Q4: What is FormArray and when would you use it?

**Answer:**
FormArray is for managing a dynamic list of form controls that can grow or shrink at runtime.

**Use cases:**
- Multiple phone numbers
- List of addresses
- Order items
- Skills/tags list
- Survey questions

```typescript
@Component({...})
export class SkillsComponent {
  private fb = inject(FormBuilder);

  form = this.fb.group({
    name: ['', Validators.required],
    skills: this.fb.array([])  // Dynamic array
  });

  get skills(): FormArray {
    return this.form.get('skills') as FormArray;
  }

  addSkill() {
    this.skills.push(this.fb.group({
      name: ['', Validators.required],
      level: ['beginner', Validators.required]
    }));
  }

  removeSkill(index: number) {
    this.skills.removeAt(index);
  }
}
```

---

## Intermediate Level

### Q5: How do you create a custom validator?

**Answer:**

**Sync Validator:**
```typescript
// As a function
export function noSpaces(control: AbstractControl): ValidationErrors | null {
  if (control.value && control.value.includes(' ')) {
    return { noSpaces: { message: 'Spaces not allowed' } };
  }
  return null;
}

// As a factory (with parameters)
export function minWords(count: number): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null => {
    const words = control.value?.trim().split(/\s+/).length || 0;
    if (words < count) {
      return { minWords: { required: count, actual: words } };
    }
    return null;
  };
}

// Usage
form = this.fb.group({
  username: ['', [Validators.required, noSpaces]],
  description: ['', [Validators.required, minWords(10)]]
});
```

**Cross-field Validator:**
```typescript
export function passwordMatch(group: AbstractControl): ValidationErrors | null {
  const password = group.get('password')?.value;
  const confirm = group.get('confirmPassword')?.value;
  
  if (password !== confirm) {
    return { passwordMatch: true };
  }
  return null;
}

// Apply to FormGroup
form = this.fb.group({
  password: ['', Validators.required],
  confirmPassword: ['', Validators.required]
}, { validators: passwordMatch });
```

---

### Q6: How do you create an async validator?

**Answer:**
Async validators are used for server-side validation like checking username availability:

```typescript
// As a function
export function uniqueEmail(userService: UserService): AsyncValidatorFn {
  return (control: AbstractControl): Observable<ValidationErrors | null> => {
    if (!control.value) {
      return of(null);
    }

    return timer(500).pipe(  // Debounce
      switchMap(() => userService.checkEmail(control.value)),
      map(isTaken => isTaken ? { emailTaken: true } : null),
      catchError(() => of(null))
    );
  };
}

// Usage - async validators go in third argument
form = this.fb.group({
  email: ['', 
    [Validators.required, Validators.email],  // Sync validators
    [uniqueEmail(this.userService)]           // Async validators
  ]
});
```

**Key points:**
- Async validators run AFTER sync validators pass
- They receive `Observable` or `Promise`
- Use `pending` state to show loading indicator
- Always debounce to avoid excessive API calls

---

### Q7: What is ControlValueAccessor and when do you need it?

**Answer:**
ControlValueAccessor is an interface that bridges angular forms with custom components. It allows custom components to work with `formControlName` and `ngModel`.

**When to use:**
- Custom date pickers
- Star rating components
- Rich text editors
- Custom select/autocomplete
- File upload components

```typescript
@Component({
  selector: 'app-custom-input',
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => CustomInputComponent),
      multi: true
    }
  ]
})
export class CustomInputComponent implements ControlValueAccessor {
  value: any;
  disabled = false;
  
  onChange: (value: any) => void = () => {};
  onTouched: () => void = () => {};

  // Called when form value changes programmatically
  writeValue(value: any): void {
    this.value = value;
  }

  // Register callback for value changes
  registerOnChange(fn: (value: any) => void): void {
    this.onChange = fn;
  }

  // Register callback for touch events
  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  // Handle disabled state
  setDisabledState(isDisabled: boolean): void {
    this.disabled = isDisabled;
  }

  // Call this when user changes value
  onInput(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    this.value = value;
    this.onChange(value);
  }

  onBlur() {
    this.onTouched();
  }
}
```

---

### Q8: How do you dynamically add/remove validators?

**Answer:**
```typescript
// Add validators
this.form.get('field')?.setValidators([
  Validators.required,
  Validators.minLength(5)
]);

// Add async validators
this.form.get('field')?.setAsyncValidators([
  uniqueValidator(this.service)
]);

// Remove all validators
this.form.get('field')?.clearValidators();
this.form.get('field')?.clearAsyncValidators();

// Add single validator without replacing existing
this.form.get('field')?.addValidators(Validators.max(100));

// Remove specific validator
this.form.get('field')?.removeValidators(Validators.required);

// IMPORTANT: Must call updateValueAndValidity after changing validators
this.form.get('field')?.updateValueAndValidity();

// Conditional validation example
toggleRequired(required: boolean) {
  const control = this.form.get('optionalField');
  if (required) {
    control?.addValidators(Validators.required);
  } else {
    control?.removeValidators(Validators.required);
  }
  control?.updateValueAndValidity();
}
```

---

## Advanced Level

### Q9: How would you handle form state persistence (save draft)?

**Answer:**
```typescript
@Component({...})
export class DraftFormComponent implements OnInit, OnDestroy {
  private fb = inject(FormBuilder);
  private destroy$ = new Subject<void>();
  private storageKey = 'form-draft';

  form = this.fb.group({
    title: [''],
    content: ['']
  });

  ngOnInit() {
    // Load saved draft
    this.loadDraft();

    // Auto-save on changes
    this.form.valueChanges.pipe(
      debounceTime(1000),
      distinctUntilChanged((a, b) => JSON.stringify(a) === JSON.stringify(b)),
      takeUntil(this.destroy$)
    ).subscribe(value => {
      this.saveDraft(value);
    });
  }

  private saveDraft(value: any) {
    localStorage.setItem(this.storageKey, JSON.stringify({
      data: value,
      timestamp: Date.now()
    }));
  }

  private loadDraft() {
    const saved = localStorage.getItem(this.storageKey);
    if (saved) {
      const { data, timestamp } = JSON.parse(saved);
      
      // Optional: Only load if draft is recent (e.g., < 24 hours)
      if (Date.now() - timestamp < 24 * 60 * 60 * 1000) {
        this.form.patchValue(data);
      }
    }
  }

  clearDraft() {
    localStorage.removeItem(this.storageKey);
    this.form.reset();
  }

  onSubmit() {
    if (this.form.valid) {
      // Submit form
      this.clearDraft(); // Clear draft after successful submit
    }
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
```

---

### Q10: How do you implement conditional form fields?

**Answer:**
```typescript
@Component({
  template: `
    <form [formGroup]="form">
      <select formControlName="contactMethod">
        <option value="email">Email</option>
        <option value="phone">Phone</option>
      </select>

      <!-- Show based on selection -->
      @if (contactMethod === 'email') {
        <input formControlName="email" placeholder="Email">
      }
      @if (contactMethod === 'phone') {
        <input formControlName="phone" placeholder="Phone">
      }
    </form>
  `
})
export class ConditionalFormComponent implements OnInit {
  private fb = inject(FormBuilder);

  form = this.fb.group({
    contactMethod: ['email'],
    email: [''],
    phone: ['']
  });

  get contactMethod() {
    return this.form.get('contactMethod')?.value;
  }

  ngOnInit() {
    // React to changes in contact method
    this.form.get('contactMethod')?.valueChanges.subscribe(method => {
      this.updateValidation(method);
    });

    // Set initial validation
    this.updateValidation('email');
  }

  private updateValidation(method: string) {
    const emailControl = this.form.get('email');
    const phoneControl = this.form.get('phone');

    if (method === 'email') {
      emailControl?.setValidators([Validators.required, Validators.email]);
      phoneControl?.clearValidators();
    } else {
      phoneControl?.setValidators([Validators.required, Validators.pattern(/^\d{10}$/)]);
      emailControl?.clearValidators();
    }

    emailControl?.updateValueAndValidity();
    phoneControl?.updateValueAndValidity();
  }
}
```

---

### Q11: How would you build a multi-step wizard form?

**Answer:**
```typescript
@Component({
  template: `
    <div class="wizard">
      <!-- Progress indicator -->
      <div class="steps">
        @for (step of steps; track step; let i = $index) {
          <div 
            class="step" 
            [class.active]="currentStep === i"
            [class.completed]="i < currentStep"
          >
            {{ step }}
          </div>
        }
      </div>

      <form [formGroup]="form">
        <!-- Step 1: Personal Info -->
        @if (currentStep === 0) {
          <div formGroupName="personal">
            <input formControlName="firstName" placeholder="First Name">
            <input formControlName="lastName" placeholder="Last Name">
          </div>
        }

        <!-- Step 2: Contact Info -->
        @if (currentStep === 1) {
          <div formGroupName="contact">
            <input formControlName="email" placeholder="Email">
            <input formControlName="phone" placeholder="Phone">
          </div>
        }

        <!-- Step 3: Review -->
        @if (currentStep === 2) {
          <div class="review">
            <h3>Review Your Information</h3>
            <pre>{{ form.value | json }}</pre>
          </div>
        }
      </form>

      <!-- Navigation -->
      <div class="nav-buttons">
        <button 
          (click)="previousStep()" 
          [disabled]="currentStep === 0"
        >
          Previous
        </button>
        
        @if (currentStep < steps.length - 1) {
          <button 
            (click)="nextStep()" 
            [disabled]="!isCurrentStepValid()"
          >
            Next
          </button>
        } @else {
          <button 
            (click)="submit()" 
            [disabled]="form.invalid"
          >
            Submit
          </button>
        }
      </div>
    </div>
  `
})
export class WizardFormComponent {
  private fb = inject(FormBuilder);
  
  steps = ['Personal', 'Contact', 'Review'];
  currentStep = 0;

  form = this.fb.group({
    personal: this.fb.group({
      firstName: ['', Validators.required],
      lastName: ['', Validators.required]
    }),
    contact: this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      phone: ['', Validators.required]
    })
  });

  isCurrentStepValid(): boolean {
    switch (this.currentStep) {
      case 0:
        return this.form.get('personal')!.valid;
      case 1:
        return this.form.get('contact')!.valid;
      default:
        return true;
    }
  }

  nextStep() {
    if (this.isCurrentStepValid() && this.currentStep < this.steps.length - 1) {
      this.currentStep++;
    }
  }

  previousStep() {
    if (this.currentStep > 0) {
      this.currentStep--;
    }
  }

  submit() {
    if (this.form.valid) {
      console.log('Form submitted:', this.form.value);
    }
  }
}
```

---

### Q12: How do you handle form arrays with complex validation?

**Answer:**
```typescript
@Component({...})
export class TeamFormComponent {
  private fb = inject(FormBuilder);

  form = this.fb.group({
    teamName: ['', Validators.required],
    members: this.fb.array([], [
      this.minMembers(2),      // Custom array validator
      this.maxMembers(10),
      this.uniqueEmails()
    ])
  });

  get members(): FormArray {
    return this.form.get('members') as FormArray;
  }

  // Custom validator: minimum members
  minMembers(min: number): ValidatorFn {
    return (array: AbstractControl): ValidationErrors | null => {
      const formArray = array as FormArray;
      if (formArray.length < min) {
        return { minMembers: { required: min, actual: formArray.length } };
      }
      return null;
    };
  }

  // Custom validator: maximum members
  maxMembers(max: number): ValidatorFn {
    return (array: AbstractControl): ValidationErrors | null => {
      const formArray = array as FormArray;
      if (formArray.length > max) {
        return { maxMembers: { allowed: max, actual: formArray.length } };
      }
      return null;
    };
  }

  // Custom validator: unique emails in array
  uniqueEmails(): ValidatorFn {
    return (array: AbstractControl): ValidationErrors | null => {
      const formArray = array as FormArray;
      const emails = formArray.controls.map(c => c.get('email')?.value);
      const duplicates = emails.filter((e, i) => emails.indexOf(e) !== i);
      
      if (duplicates.length > 0) {
        return { duplicateEmails: { emails: duplicates } };
      }
      return null;
    };
  }

  addMember() {
    this.members.push(this.fb.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      role: ['member', Validators.required]
    }));
  }
}
```

---

## Scenario-Based Questions

### Q13: How would you optimize a form with 50+ fields?

**Answer:**
1. **Split into logical sections** using nested FormGroups
2. **Lazy load form sections** - render only visible sections
3. **Use OnPush change detection** in form components
4. **Debounce value changes** for expensive operations
5. **Use updateOn: 'blur'** to reduce validation frequency

```typescript
form = this.fb.group({
  email: ['', {
    validators: [Validators.required, Validators.email],
    updateOn: 'blur'  // Validate only on blur
  }]
});

// Or for entire form
form = this.fb.group({
  field1: [''],
  field2: ['']
}, { updateOn: 'blur' });
```

---

### Q14: Form is not updating after patchValue - why?

**Answer:**
Common causes and solutions:

```typescript
// 1. Control doesn't exist - patchValue silently ignores
this.form.patchValue({ nonExistentField: 'value' }); // No error!

// Use setValue for strict matching (throws error if mismatch)
this.form.setValue({ exactFields: 'required' });

// 2. Nested objects need proper structure
this.form.patchValue({
  address: { city: 'New York' }  // Correct for nested group
});

// 3. FormArray needs special handling
const items = this.form.get('items') as FormArray;
items.clear();  // Clear existing
data.items.forEach(item => {
  items.push(this.fb.group(item));
});

// 4. Check if change detection is needed
this.form.patchValue(data);
this.cdr.detectChanges(); // Force update if using OnPush
```

---

## Quick Reference

### Form Methods Cheat Sheet
```typescript
// Value operations
form.value           // Current value
form.getRawValue()   // Value including disabled fields
form.patchValue({})  // Partial update
form.setValue({})    // Complete update (strict)
form.reset()         // Reset to initial
form.reset({})       // Reset with values

// State operations
form.markAsTouched()
form.markAllAsTouched()
form.markAsDirty()
form.markAsPristine()
form.enable()
form.disable()

// Validation
form.setValidators([])
form.clearValidators()
form.updateValueAndValidity()

// Access controls
form.get('fieldName')
form.get('nested.field')
form.controls['fieldName']
```
