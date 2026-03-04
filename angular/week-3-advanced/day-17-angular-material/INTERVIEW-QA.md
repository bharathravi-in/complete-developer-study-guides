# Day 17: Angular Material - Interview Questions & Answers

## Basic Level

### Q1: What is Angular Material and its benefits?

**Answer:**
Angular Material is the official component library for Angular that implements Material Design specifications.

**Benefits:**
1. **Consistent Design** - Follows Material Design guidelines
2. **Accessibility** - Built-in ARIA support
3. **Responsive** - Works across devices
4. **Theming** - Easy customization
5. **Well Tested** - Production-ready components
6. **Active Maintenance** - Updated with Angular releases

```typescript
// Installation
ng add @angular/material

// Usage
@Component({
  standalone: true,
  imports: [MatButtonModule, MatCardModule],
  template: `
    <mat-card>
      <button mat-raised-button color="primary">Click</button>
    </mat-card>
  `
})
```

---

### Q2: How do you create a custom theme in Angular Material?

**Answer:**
```scss
// styles.scss
@use '@angular/material' as mat;

// 1. Define color palettes
$my-primary: mat.m2-define-palette(mat.$m2-indigo-palette, 500);
$my-accent: mat.m2-define-palette(mat.$m2-pink-palette, A200);
$my-warn: mat.m2-define-palette(mat.$m2-red-palette);

// 2. Create theme
$my-theme: mat.m2-define-light-theme((
  color: (
    primary: $my-primary,
    accent: $my-accent,
    warn: $my-warn
  ),
  typography: mat.m2-define-typography-config(),
  density: 0
));

// 3. Apply theme
@include mat.all-component-themes($my-theme);

// 4. Dark theme variant
$dark-theme: mat.m2-define-dark-theme((
  color: (
    primary: $my-primary,
    accent: $my-accent,
    warn: $my-warn
  )
));

.dark-mode {
  @include mat.all-component-colors($dark-theme);
}
```

---

### Q3: Explain the difference between mat-button variants.

**Answer:**
```typescript
@Component({
  template: `
    <!-- Basic - no elevation, minimal styling -->
    <button mat-button>Basic</button>

    <!-- Raised - elevated with shadow -->
    <button mat-raised-button>Raised</button>

    <!-- Flat - colored background, no elevation -->
    <button mat-flat-button color="primary">Flat</button>

    <!-- Stroked - outlined border -->
    <button mat-stroked-button>Stroked</button>

    <!-- Icon - circular for icons only -->
    <button mat-icon-button>
      <mat-icon>favorite</mat-icon>
    </button>

    <!-- FAB - Floating Action Button -->
    <button mat-fab color="accent">
      <mat-icon>add</mat-icon>
    </button>

    <!-- Mini FAB - smaller FAB -->
    <button mat-mini-fab>
      <mat-icon>edit</mat-icon>
    </button>
  `
})
```

| Variant | Elevation | Use Case |
|---------|-----------|----------|
| mat-button | None | Text actions, dialogs |
| mat-raised-button | Yes | Primary actions |
| mat-flat-button | None | Contained actions |
| mat-stroked-button | None | Secondary actions |
| mat-icon-button | None | Icon-only actions |
| mat-fab | Yes | Primary floating action |
| mat-mini-fab | Yes | Secondary floating action |

---

## Intermediate Level

### Q4: How do you implement a dialog with data passing?

**Answer:**
```typescript
// dialog.component.ts
@Component({
  standalone: true,
  imports: [MatDialogModule, MatButtonModule, MatFormFieldModule],
  template: `
    <h2 mat-dialog-title>{{ data.title }}</h2>
    
    <mat-dialog-content>
      <mat-form-field>
        <input matInput [(ngModel)]="data.name">
      </mat-form-field>
    </mat-dialog-content>
    
    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button mat-raised-button [mat-dialog-close]="data" color="primary">
        Save
      </button>
    </mat-dialog-actions>
  `
})
export class EditDialogComponent {
  data = inject<DialogData>(MAT_DIALOG_DATA);
}

// parent.component.ts
@Component({...})
export class ParentComponent {
  private dialog = inject(MatDialog);

  openEdit(item: Item) {
    const dialogRef = this.dialog.open(EditDialogComponent, {
      width: '400px',
      data: { title: 'Edit Item', name: item.name },
      disableClose: true,  // Prevent closing by clicking outside
      autoFocus: true,     // Focus first input
      panelClass: 'custom-dialog'  // Custom styling
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.saveItem(result);
      }
    });
  }
}
```

---

### Q5: How do you implement a data table with sorting, filtering, and pagination?

**Answer:**
```typescript
@Component({
  standalone: true,
  imports: [
    MatTableModule, 
    MatSortModule, 
    MatPaginatorModule,
    MatFormFieldModule,
    MatInputModule
  ],
  template: `
    <mat-form-field>
      <mat-label>Filter</mat-label>
      <input matInput (input)="applyFilter($event)">
    </mat-form-field>

    <table mat-table [dataSource]="dataSource" matSort>
      <ng-container matColumnDef="name">
        <th mat-header-cell *matHeaderCellDef mat-sort-header>Name</th>
        <td mat-cell *matCellDef="let row">{{ row.name }}</td>
      </ng-container>

      <ng-container matColumnDef="email">
        <th mat-header-cell *matHeaderCellDef mat-sort-header>Email</th>
        <td mat-cell *matCellDef="let row">{{ row.email }}</td>
      </ng-container>

      <tr mat-header-row *matHeaderRowDef="columns"></tr>
      <tr mat-row *matRowDef="let row; columns: columns"></tr>
    </table>

    <mat-paginator [pageSizeOptions]="[5, 10, 25]" showFirstLastButtons>
    </mat-paginator>
  `
})
export class DataTableComponent implements AfterViewInit {
  @ViewChild(MatSort) sort!: MatSort;
  @ViewChild(MatPaginator) paginator!: MatPaginator;

  columns = ['name', 'email'];
  dataSource = new MatTableDataSource<User>();

  ngAfterViewInit() {
    this.dataSource.sort = this.sort;
    this.dataSource.paginator = this.paginator;
    
    // Custom filter predicate
    this.dataSource.filterPredicate = (data, filter) => {
      return data.name.toLowerCase().includes(filter) ||
             data.email.toLowerCase().includes(filter);
    };
  }

  applyFilter(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    this.dataSource.filter = value.trim().toLowerCase();
  }

  loadData(users: User[]) {
    this.dataSource.data = users;
  }
}
```

---

### Q6: How do you handle form validation with Angular Material?

**Answer:**
```typescript
@Component({
  imports: [
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule
  ],
  template: `
    <form [formGroup]="form" (ngSubmit)="submit()">
      <mat-form-field appearance="outline">
        <mat-label>Email</mat-label>
        <input matInput formControlName="email" type="email">
        <mat-icon matSuffix>email</mat-icon>
        <mat-hint>Enter your work email</mat-hint>
        
        @if (form.get('email')?.hasError('required')) {
          <mat-error>Email is required</mat-error>
        }
        @if (form.get('email')?.hasError('email')) {
          <mat-error>Invalid email format</mat-error>
        }
      </mat-form-field>

      <mat-form-field appearance="outline">
        <mat-label>Password</mat-label>
        <input matInput 
               [type]="hidePassword ? 'password' : 'text'"
               formControlName="password">
        <button mat-icon-button matSuffix type="button"
                (click)="hidePassword = !hidePassword">
          <mat-icon>{{ hidePassword ? 'visibility_off' : 'visibility' }}</mat-icon>
        </button>
        
        @if (form.get('password')?.hasError('required')) {
          <mat-error>Password is required</mat-error>
        }
        @if (form.get('password')?.hasError('minlength')) {
          <mat-error>Minimum 8 characters</mat-error>
        }
      </mat-form-field>

      <button mat-raised-button color="primary" 
              type="submit" [disabled]="form.invalid">
        Submit
      </button>
    </form>
  `
})
export class LoginFormComponent {
  hidePassword = true;
  
  form = inject(FormBuilder).group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(8)]]
  });

  submit() {
    if (this.form.valid) {
      console.log(this.form.value);
    }
  }
}
```

---

### Q7: How do you create a reusable snackbar/notification service?

**Answer:**
```typescript
// notification.service.ts
@Injectable({ providedIn: 'root' })
export class NotificationService {
  private snackBar = inject(MatSnackBar);

  success(message: string, action = 'OK') {
    return this.show(message, action, 'success-snackbar');
  }

  error(message: string, action = 'Dismiss') {
    return this.show(message, action, 'error-snackbar', 5000);
  }

  warning(message: string, action = 'OK') {
    return this.show(message, action, 'warning-snackbar');
  }

  info(message: string, action = 'OK') {
    return this.show(message, action, 'info-snackbar');
  }

  private show(
    message: string, 
    action: string, 
    panelClass: string,
    duration = 3000
  ) {
    return this.snackBar.open(message, action, {
      duration,
      horizontalPosition: 'end',
      verticalPosition: 'top',
      panelClass: [panelClass]
    });
  }
}

// styles.scss
.success-snackbar {
  --mdc-snackbar-container-color: #4caf50;
  --mdc-snackbar-supporting-text-color: white;
}

.error-snackbar {
  --mdc-snackbar-container-color: #f44336;
  --mdc-snackbar-supporting-text-color: white;
}

// Usage
@Component({...})
export class UserComponent {
  private notify = inject(NotificationService);

  save() {
    this.userService.save().subscribe({
      next: () => this.notify.success('User saved!'),
      error: (err) => this.notify.error(err.message)
    });
  }
}
```

---

## Advanced Level

### Q8: How do you implement server-side pagination with MatTable?

**Answer:**
```typescript
@Component({
  template: `
    <table mat-table [dataSource]="data">
      <!-- Column definitions -->
    </table>

    <mat-paginator 
      [length]="totalItems"
      [pageSize]="pageSize"
      [pageIndex]="pageIndex"
      [pageSizeOptions]="[10, 25, 50]"
      (page)="onPageChange($event)">
    </mat-paginator>
  `
})
export class ServerPaginatedTableComponent implements OnInit {
  data: User[] = [];
  totalItems = 0;
  pageSize = 10;
  pageIndex = 0;
  loading = false;

  private userService = inject(UserService);

  ngOnInit() {
    this.loadData();
  }

  loadData() {
    this.loading = true;
    
    this.userService.getUsers({
      page: this.pageIndex,
      size: this.pageSize,
      sort: this.currentSort
    }).subscribe({
      next: (response) => {
        this.data = response.content;
        this.totalItems = response.totalElements;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
      }
    });
  }

  onPageChange(event: PageEvent) {
    this.pageIndex = event.pageIndex;
    this.pageSize = event.pageSize;
    this.loadData();
  }
}
```

---

### Q9: How do you create a custom form field component compatible with Material?

**Answer:**
```typescript
// Custom form field that works with mat-form-field
@Component({
  selector: 'app-phone-input',
  standalone: true,
  imports: [MatFormFieldModule],
  template: `
    <div class="phone-input">
      <select (change)="onCountryChange($event)">
        @for (country of countries; track country.code) {
          <option [value]="country.code">{{ country.dialCode }}</option>
        }
      </select>
      <input 
        type="tel"
        [value]="phoneNumber"
        (input)="onPhoneChange($event)"
        (blur)="onTouched()"
        [disabled]="disabled"
      >
    </div>
  `,
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => PhoneInputComponent),
      multi: true
    },
    {
      provide: MatFormFieldControl,
      useExisting: PhoneInputComponent
    }
  ]
})
export class PhoneInputComponent implements ControlValueAccessor, MatFormFieldControl<string> {
  static nextId = 0;
  
  @Input() placeholder = '';
  @Input() required = false;
  
  stateChanges = new Subject<void>();
  focused = false;
  touched = false;
  disabled = false;
  
  id = `phone-input-${PhoneInputComponent.nextId++}`;
  controlType = 'phone-input';

  phoneNumber = '';
  countryCode = 'US';

  countries = [
    { code: 'US', dialCode: '+1' },
    { code: 'UK', dialCode: '+44' }
  ];

  onChange: (value: string) => void = () => {};
  onTouched: () => void = () => {};

  get value(): string {
    const country = this.countries.find(c => c.code === this.countryCode);
    return `${country?.dialCode}${this.phoneNumber}`;
  }

  get empty(): boolean {
    return !this.phoneNumber;
  }

  get shouldLabelFloat(): boolean {
    return this.focused || !this.empty;
  }

  get errorState(): boolean {
    return this.touched && this.required && this.empty;
  }

  // ControlValueAccessor
  writeValue(value: string): void {
    // Parse and set value
    this.stateChanges.next();
  }

  registerOnChange(fn: any): void {
    this.onChange = fn;
  }

  registerOnTouched(fn: any): void {
    this.onTouched = fn;
  }

  setDisabledState(disabled: boolean): void {
    this.disabled = disabled;
    this.stateChanges.next();
  }

  // MatFormFieldControl
  setDescribedByIds(ids: string[]): void {}
  
  onContainerClick(): void {
    // Focus the input
  }

  ngOnDestroy() {
    this.stateChanges.complete();
  }
}

// Usage
<mat-form-field>
  <mat-label>Phone</mat-label>
  <app-phone-input formControlName="phone"></app-phone-input>
  <mat-error>Phone is required</mat-error>
</mat-form-field>
```

---

### Q10: How do you implement drag-and-drop with CDK?

**Answer:**
```typescript
import { CdkDragDrop, DragDropModule, moveItemInArray, transferArrayItem } from '@angular/cdk/drag-drop';

@Component({
  standalone: true,
  imports: [DragDropModule],
  template: `
    <div class="kanban-board">
      <div class="column"
           cdkDropList
           #todoList="cdkDropList"
           [cdkDropListData]="todo"
           [cdkDropListConnectedTo]="[doneList]"
           (cdkDropListDropped)="drop($event)">
        <h3>To Do</h3>
        @for (item of todo; track item) {
          <div class="item" cdkDrag>
            {{ item }}
            <div class="drag-placeholder" *cdkDragPlaceholder></div>
          </div>
        }
      </div>

      <div class="column"
           cdkDropList
           #doneList="cdkDropList"
           [cdkDropListData]="done"
           [cdkDropListConnectedTo]="[todoList]"
           (cdkDropListDropped)="drop($event)">
        <h3>Done</h3>
        @for (item of done; track item) {
          <div class="item" cdkDrag>{{ item }}</div>
        }
      </div>
    </div>
  `,
  styles: [`
    .kanban-board { display: flex; gap: 20px; }
    .column { 
      width: 300px; 
      min-height: 200px;
      background: #f5f5f5;
      padding: 10px;
      border-radius: 4px;
    }
    .item {
      padding: 10px;
      background: white;
      margin-bottom: 8px;
      border-radius: 4px;
      cursor: move;
    }
    .cdk-drag-preview {
      box-shadow: 0 5px 5px -3px rgba(0,0,0,.2);
    }
    .cdk-drag-placeholder {
      opacity: 0.3;
    }
    .cdk-drag-animating {
      transition: transform 250ms;
    }
  `]
})
export class KanbanBoardComponent {
  todo = ['Task 1', 'Task 2', 'Task 3'];
  done = ['Task 4'];

  drop(event: CdkDragDrop<string[]>) {
    if (event.previousContainer === event.container) {
      // Reorder within same list
      moveItemInArray(
        event.container.data,
        event.previousIndex,
        event.currentIndex
      );
    } else {
      // Transfer between lists
      transferArrayItem(
        event.previousContainer.data,
        event.container.data,
        event.previousIndex,
        event.currentIndex
      );
    }
  }
}
```

---

### Q11: How do you implement autocomplete with async data?

**Answer:**
```typescript
@Component({
  imports: [
    MatAutocompleteModule,
    MatFormFieldModule,
    MatInputModule,
    ReactiveFormsModule,
    AsyncPipe
  ],
  template: `
    <mat-form-field>
      <mat-label>User</mat-label>
      <input matInput
             [formControl]="searchControl"
             [matAutocomplete]="auto">
      
      <mat-autocomplete #auto="matAutocomplete"
                        [displayWith]="displayFn"
                        (optionSelected)="onSelect($event)">
        @if (loading()) {
          <mat-option disabled>Loading...</mat-option>
        } @else {
          @for (user of users$ | async; track user.id) {
            <mat-option [value]="user">
              <img [src]="user.avatar" class="avatar">
              <span>{{ user.name }}</span>
              <small>{{ user.email }}</small>
            </mat-option>
          } @empty {
            <mat-option disabled>No users found</mat-option>
          }
        }
      </mat-autocomplete>
    </mat-form-field>
  `
})
export class UserAutocompleteComponent {
  searchControl = new FormControl('');
  loading = signal(false);

  private userService = inject(UserService);

  users$ = this.searchControl.valueChanges.pipe(
    debounceTime(300),
    distinctUntilChanged(),
    filter(value => typeof value === 'string' && value.length >= 2),
    tap(() => this.loading.set(true)),
    switchMap(value => this.userService.search(value).pipe(
      catchError(() => of([])),
      finalize(() => this.loading.set(false))
    ))
  );

  displayFn(user: User): string {
    return user?.name || '';
  }

  onSelect(event: MatAutocompleteSelectedEvent) {
    const user = event.option.value as User;
    console.log('Selected:', user);
  }
}
```

---

## Quick Reference

```
Common Material Imports:
────────────────────────
MatButtonModule      - Buttons
MatCardModule        - Cards
MatFormFieldModule   - Form field wrapper
MatInputModule       - Input/Textarea
MatSelectModule      - Dropdowns
MatCheckboxModule    - Checkboxes
MatRadioModule       - Radio buttons
MatTableModule       - Data tables
MatPaginatorModule   - Pagination
MatSortModule        - Column sorting
MatDialogModule      - Modal dialogs
MatSnackBarModule    - Toasts/Notifications
MatAutocompleteModule - Autocomplete
MatDatepickerModule  - Date picker
MatIconModule        - Icons
MatToolbarModule     - Toolbars
MatSidenavModule     - Side navigation
MatMenuModule        - Menus
MatTabsModule        - Tabs
MatProgressSpinnerModule - Spinners
MatProgressBarModule - Progress bars

Theme Palettes:
───────────────
Primary   - Main brand color
Accent    - Secondary/highlight color
Warn      - Error/warning color

Button Colors:
──────────────
color="primary"
color="accent"
color="warn"
(default - no color attribute)
```
