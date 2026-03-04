# Day 17: Angular Material

## Overview

Angular Material is the official component library implementing Google's Material Design for Angular applications.

---

## Installation & Setup

```bash
# Install Angular Material
ng add @angular/material

# Or manually
npm install @angular/material @angular/cdk
```

### Configuration

```typescript
// app.config.ts
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

export const appConfig: ApplicationConfig = {
  providers: [
    provideAnimationsAsync()
  ]
};
```

---

## Theming

### Custom Theme

```scss
// styles.scss
@use '@angular/material' as mat;

// Define custom palettes
$primary: mat.m2-define-palette(mat.$m2-indigo-palette);
$accent: mat.m2-define-palette(mat.$m2-pink-palette, A200, A100, A400);
$warn: mat.m2-define-palette(mat.$m2-red-palette);

// Create theme
$theme: mat.m2-define-light-theme((
  color: (
    primary: $primary,
    accent: $accent,
    warn: $warn,
  ),
  typography: mat.m2-define-typography-config(),
  density: 0,
));

// Include theme styles
@include mat.all-component-themes($theme);

// Or include only what you need
@include mat.core();
@include mat.button-theme($theme);
@include mat.card-theme($theme);
@include mat.form-field-theme($theme);
```

### Dark Theme

```scss
// Dark theme
$dark-theme: mat.m2-define-dark-theme((
  color: (
    primary: $primary,
    accent: $accent,
    warn: $warn,
  )
));

// Apply dark theme to class
.dark-theme {
  @include mat.all-component-colors($dark-theme);
}
```

### Theme Switching Service

```typescript
@Injectable({ providedIn: 'root' })
export class ThemeService {
  private darkMode = signal(false);
  
  isDarkMode = this.darkMode.asReadonly();

  constructor() {
    // Load saved preference
    const saved = localStorage.getItem('darkMode');
    if (saved) {
      this.darkMode.set(saved === 'true');
    }
  }

  toggleTheme() {
    this.darkMode.update(dark => !dark);
    localStorage.setItem('darkMode', String(this.darkMode()));
  }
}

// App component
@Component({
  selector: 'app-root',
  template: `
    <div [class.dark-theme]="themeService.isDarkMode()">
      <router-outlet />
    </div>
  `
})
export class AppComponent {
  themeService = inject(ThemeService);
}
```

---

## Common Components

### Button

```typescript
import { MatButtonModule } from '@angular/material/button';

@Component({
  imports: [MatButtonModule],
  template: `
    <button mat-button>Basic</button>
    <button mat-raised-button>Raised</button>
    <button mat-flat-button color="primary">Flat</button>
    <button mat-stroked-button color="accent">Stroked</button>
    <button mat-icon-button>
      <mat-icon>favorite</mat-icon>
    </button>
    <button mat-fab color="warn">
      <mat-icon>add</mat-icon>
    </button>
    <button mat-mini-fab>
      <mat-icon>edit</mat-icon>
    </button>
  `
})
```

### Form Fields

```typescript
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';

@Component({
  imports: [MatFormFieldModule, MatInputModule, MatSelectModule, ReactiveFormsModule],
  template: `
    <form [formGroup]="form">
      <mat-form-field appearance="outline">
        <mat-label>Name</mat-label>
        <input matInput formControlName="name" placeholder="Enter name">
        <mat-icon matSuffix>person</mat-icon>
        <mat-hint>Your full name</mat-hint>
        @if (form.get('name')?.hasError('required')) {
          <mat-error>Name is required</mat-error>
        }
      </mat-form-field>

      <mat-form-field appearance="fill">
        <mat-label>Country</mat-label>
        <mat-select formControlName="country">
          @for (country of countries; track country.code) {
            <mat-option [value]="country.code">
              {{ country.name }}
            </mat-option>
          }
        </mat-select>
      </mat-form-field>

      <mat-form-field>
        <mat-label>Description</mat-label>
        <textarea matInput formControlName="description" rows="4"></textarea>
        <mat-hint align="end">{{ form.get('description')?.value?.length }}/500</mat-hint>
      </mat-form-field>
    </form>
  `
})
export class FormComponent {
  form = inject(FormBuilder).group({
    name: ['', Validators.required],
    country: [''],
    description: ['', Validators.maxLength(500)]
  });

  countries = [
    { code: 'US', name: 'United States' },
    { code: 'UK', name: 'United Kingdom' }
  ];
}
```

### Cards

```typescript
import { MatCardModule } from '@angular/material/card';

@Component({
  imports: [MatCardModule, MatButtonModule],
  template: `
    <mat-card>
      <mat-card-header>
        <div mat-card-avatar class="avatar"></div>
        <mat-card-title>Product Name</mat-card-title>
        <mat-card-subtitle>Category</mat-card-subtitle>
      </mat-card-header>
      
      <img mat-card-image src="product.jpg" alt="Product">
      
      <mat-card-content>
        <p>Product description goes here...</p>
      </mat-card-content>
      
      <mat-card-actions align="end">
        <button mat-button>SHARE</button>
        <button mat-button color="primary">BUY</button>
      </mat-card-actions>
    </mat-card>
  `
})
```

---

## Dialog

```typescript
import { MatDialogModule, MatDialog, MAT_DIALOG_DATA } from '@angular/material/dialog';

// Dialog component
@Component({
  selector: 'app-confirm-dialog',
  standalone: true,
  imports: [MatDialogModule, MatButtonModule],
  template: `
    <h2 mat-dialog-title>{{ data.title }}</h2>
    
    <mat-dialog-content>
      <p>{{ data.message }}</p>
    </mat-dialog-content>
    
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button mat-raised-button color="warn" [mat-dialog-close]="true">
        Confirm
      </button>
    </mat-dialog-actions>
  `
})
export class ConfirmDialogComponent {
  data = inject<{ title: string; message: string }>(MAT_DIALOG_DATA);
}

// Using the dialog
@Component({
  imports: [MatButtonModule],
  template: `
    <button mat-raised-button (click)="openDialog()">Delete Item</button>
  `
})
export class ParentComponent {
  private dialog = inject(MatDialog);

  openDialog() {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      width: '400px',
      data: {
        title: 'Delete Item',
        message: 'Are you sure you want to delete this item?'
      }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.deleteItem();
      }
    });
  }
}
```

### Dialog with Form

```typescript
@Component({
  standalone: true,
  imports: [MatDialogModule, MatFormFieldModule, MatInputModule, ReactiveFormsModule],
  template: `
    <h2 mat-dialog-title>Edit User</h2>
    
    <form [formGroup]="form" (ngSubmit)="save()">
      <mat-dialog-content>
        <mat-form-field>
          <mat-label>Name</mat-label>
          <input matInput formControlName="name">
        </mat-form-field>
        
        <mat-form-field>
          <mat-label>Email</mat-label>
          <input matInput formControlName="email" type="email">
        </mat-form-field>
      </mat-dialog-content>
      
      <mat-dialog-actions align="end">
        <button mat-button type="button" mat-dialog-close>Cancel</button>
        <button mat-raised-button color="primary" type="submit" 
                [disabled]="form.invalid">
          Save
        </button>
      </mat-dialog-actions>
    </form>
  `
})
export class EditUserDialogComponent {
  private dialogRef = inject(MatDialogRef<EditUserDialogComponent>);
  private data = inject<User>(MAT_DIALOG_DATA);

  form = inject(FormBuilder).group({
    name: [this.data.name, Validators.required],
    email: [this.data.email, [Validators.required, Validators.email]]
  });

  save() {
    if (this.form.valid) {
      this.dialogRef.close(this.form.value);
    }
  }
}
```

---

## Table with Pagination & Sorting

```typescript
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatPaginatorModule, MatPaginator } from '@angular/material/paginator';
import { MatSortModule, MatSort } from '@angular/material/sort';

@Component({
  standalone: true,
  imports: [MatTableModule, MatPaginatorModule, MatSortModule],
  template: `
    <div class="table-container">
      <!-- Filter -->
      <mat-form-field>
        <mat-label>Search</mat-label>
        <input matInput (input)="applyFilter($event)" placeholder="Search...">
      </mat-form-field>

      <!-- Table -->
      <table mat-table [dataSource]="dataSource" matSort>
        <!-- ID Column -->
        <ng-container matColumnDef="id">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>ID</th>
          <td mat-cell *matCellDef="let row">{{ row.id }}</td>
        </ng-container>

        <!-- Name Column -->
        <ng-container matColumnDef="name">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Name</th>
          <td mat-cell *matCellDef="let row">{{ row.name }}</td>
        </ng-container>

        <!-- Email Column -->
        <ng-container matColumnDef="email">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Email</th>
          <td mat-cell *matCellDef="let row">{{ row.email }}</td>
        </ng-container>

        <!-- Actions Column -->
        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef>Actions</th>
          <td mat-cell *matCellDef="let row">
            <button mat-icon-button (click)="edit(row)">
              <mat-icon>edit</mat-icon>
            </button>
            <button mat-icon-button color="warn" (click)="delete(row)">
              <mat-icon>delete</mat-icon>
            </button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>

        <!-- No data row -->
        <tr class="mat-row" *matNoDataRow>
          <td class="mat-cell" [attr.colspan]="displayedColumns.length">
            No data found
          </td>
        </tr>
      </table>

      <!-- Paginator -->
      <mat-paginator 
        [pageSizeOptions]="[5, 10, 25, 100]"
        showFirstLastButtons
      ></mat-paginator>
    </div>
  `
})
export class UserTableComponent implements AfterViewInit {
  @ViewChild(MatPaginator) paginator!: MatPaginator;
  @ViewChild(MatSort) sort!: MatSort;

  displayedColumns = ['id', 'name', 'email', 'actions'];
  dataSource = new MatTableDataSource<User>();

  private userService = inject(UserService);

  ngOnInit() {
    this.loadData();
  }

  ngAfterViewInit() {
    this.dataSource.paginator = this.paginator;
    this.dataSource.sort = this.sort;
  }

  loadData() {
    this.userService.getUsers().subscribe(users => {
      this.dataSource.data = users;
    });
  }

  applyFilter(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    this.dataSource.filter = value.trim().toLowerCase();

    if (this.dataSource.paginator) {
      this.dataSource.paginator.firstPage();
    }
  }

  edit(user: User) {
    // Open edit dialog
  }

  delete(user: User) {
    // Confirm and delete
  }
}
```

---

## Snackbar (Toast Notifications)

```typescript
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';

@Injectable({ providedIn: 'root' })
export class NotificationService {
  private snackBar = inject(MatSnackBar);

  success(message: string) {
    this.snackBar.open(message, 'Close', {
      duration: 3000,
      horizontalPosition: 'end',
      verticalPosition: 'top',
      panelClass: ['success-snackbar']
    });
  }

  error(message: string) {
    this.snackBar.open(message, 'Close', {
      duration: 5000,
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
      panelClass: ['error-snackbar']
    });
  }

  info(message: string) {
    this.snackBar.open(message, 'Dismiss', {
      duration: 4000
    });
  }
}

// Custom snackbar component
@Component({
  selector: 'app-custom-snackbar',
  template: `
    <div class="custom-snackbar">
      <mat-icon>{{ data.icon }}</mat-icon>
      <span>{{ data.message }}</span>
      <button mat-icon-button (click)="dismiss()">
        <mat-icon>close</mat-icon>
      </button>
    </div>
  `
})
export class CustomSnackbarComponent {
  data = inject(MAT_SNACK_BAR_DATA);
  snackBarRef = inject(MatSnackBarRef);

  dismiss() {
    this.snackBarRef.dismiss();
  }
}
```

---

## Dynamic Forms with Material

```typescript
interface FormField {
  type: 'text' | 'select' | 'checkbox' | 'date';
  name: string;
  label: string;
  options?: { value: any; label: string }[];
  validators?: ValidatorFn[];
}

@Component({
  selector: 'app-dynamic-form',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatCheckboxModule,
    MatDatepickerModule,
    MatButtonModule
  ],
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()">
      @for (field of fields; track field.name) {
        @switch (field.type) {
          @case ('text') {
            <mat-form-field>
              <mat-label>{{ field.label }}</mat-label>
              <input matInput [formControlName]="field.name">
            </mat-form-field>
          }
          @case ('select') {
            <mat-form-field>
              <mat-label>{{ field.label }}</mat-label>
              <mat-select [formControlName]="field.name">
                @for (opt of field.options; track opt.value) {
                  <mat-option [value]="opt.value">{{ opt.label }}</mat-option>
                }
              </mat-select>
            </mat-form-field>
          }
          @case ('checkbox') {
            <mat-checkbox [formControlName]="field.name">
              {{ field.label }}
            </mat-checkbox>
          }
          @case ('date') {
            <mat-form-field>
              <mat-label>{{ field.label }}</mat-label>
              <input matInput [matDatepicker]="picker" [formControlName]="field.name">
              <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
              <mat-datepicker #picker></mat-datepicker>
            </mat-form-field>
          }
        }
      }
      
      <button mat-raised-button color="primary" type="submit" 
              [disabled]="form.invalid">
        Submit
      </button>
    </form>
  `
})
export class DynamicFormComponent implements OnInit {
  @Input() fields: FormField[] = [];
  @Output() formSubmit = new EventEmitter<any>();

  form!: FormGroup;
  private fb = inject(FormBuilder);

  ngOnInit() {
    this.form = this.buildForm();
  }

  private buildForm(): FormGroup {
    const group: { [key: string]: any } = {};
    
    this.fields.forEach(field => {
      group[field.name] = ['', field.validators || []];
    });
    
    return this.fb.group(group);
  }

  submit() {
    if (this.form.valid) {
      this.formSubmit.emit(this.form.value);
    }
  }
}

// Usage
@Component({
  template: `
    <app-dynamic-form 
      [fields]="formConfig" 
      (formSubmit)="onSubmit($event)"
    />
  `
})
export class ConfigurableFormComponent {
  formConfig: FormField[] = [
    { type: 'text', name: 'name', label: 'Full Name', validators: [Validators.required] },
    { type: 'text', name: 'email', label: 'Email', validators: [Validators.email] },
    { type: 'select', name: 'role', label: 'Role', options: [
      { value: 'admin', label: 'Administrator' },
      { value: 'user', label: 'User' }
    ]},
    { type: 'date', name: 'birthDate', label: 'Birth Date' },
    { type: 'checkbox', name: 'newsletter', label: 'Subscribe to newsletter' }
  ];
}
```

---

## Autocomplete

```typescript
import { MatAutocompleteModule } from '@angular/material/autocomplete';

@Component({
  imports: [MatAutocompleteModule, MatFormFieldModule, MatInputModule, ReactiveFormsModule],
  template: `
    <mat-form-field>
      <mat-label>Country</mat-label>
      <input matInput
             [formControl]="countryControl"
             [matAutocomplete]="auto">
      <mat-autocomplete #auto="matAutocomplete" 
                        [displayWith]="displayFn"
                        (optionSelected)="onSelected($event)">
        @for (option of filteredOptions(); track option.code) {
          <mat-option [value]="option">
            {{ option.name }}
          </mat-option>
        }
      </mat-autocomplete>
    </mat-form-field>
  `
})
export class AutocompleteComponent {
  countryControl = new FormControl('');
  
  countries = [
    { code: 'US', name: 'United States' },
    { code: 'UK', name: 'United Kingdom' },
    { code: 'CA', name: 'Canada' },
    { code: 'AU', name: 'Australia' }
  ];

  filteredOptions = toSignal(
    this.countryControl.valueChanges.pipe(
      startWith(''),
      map(value => this.filter(value || ''))
    ),
    { initialValue: this.countries }
  );

  private filter(value: string | Country): Country[] {
    const filterValue = typeof value === 'string' 
      ? value.toLowerCase() 
      : value.name.toLowerCase();
    
    return this.countries.filter(c => 
      c.name.toLowerCase().includes(filterValue)
    );
  }

  displayFn(country: Country): string {
    return country?.name || '';
  }

  onSelected(event: any) {
    console.log('Selected:', event.option.value);
  }
}
```

---

## Summary

| Component | Import | Use Case |
|-----------|--------|----------|
| MatButton | MatButtonModule | Actions, navigation |
| MatFormField | MatFormFieldModule | Input containers |
| MatTable | MatTableModule | Data display |
| MatDialog | MatDialogModule | Modal dialogs |
| MatSnackBar | MatSnackBarModule | Notifications |
| MatPaginator | MatPaginatorModule | Table pagination |
| MatSort | MatSortModule | Column sorting |
| MatAutocomplete | MatAutocompleteModule | Search suggestions |
| MatDatepicker | MatDatepickerModule | Date selection |
