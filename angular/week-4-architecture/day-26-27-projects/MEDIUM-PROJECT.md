# Days 26-27: Medium-Level Project - Task Management App

## Project Overview

Build a complete Task Management application demonstrating:
- Angular 22 features (Signals, Standalone components)
- Reactive Forms with validation
- State management
- API integration
- Authentication
- Lazy loading

---

## Project Structure

```
src/
├── app/
│   ├── core/
│   │   ├── auth/
│   │   │   ├── auth.service.ts
│   │   │   ├── auth.guard.ts
│   │   │   └── auth.interceptor.ts
│   │   ├── api/
│   │   │   ├── base-api.service.ts
│   │   │   └── task-api.service.ts
│   │   └── services/
│   │       └── notification.service.ts
│   ├── shared/
│   │   ├── components/
│   │   │   ├── button/
│   │   │   ├── card/
│   │   │   └── modal/
│   │   ├── pipes/
│   │   │   └── relative-time.pipe.ts
│   │   └── directives/
│   │       └── click-outside.directive.ts
│   ├── features/
│   │   ├── auth/
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── dashboard/
│   │   │   └── dashboard.component.ts
│   │   └── tasks/
│   │       ├── task-list/
│   │       ├── task-detail/
│   │       ├── task-form/
│   │       └── task.store.ts
│   ├── app.component.ts
│   ├── app.config.ts
│   └── app.routes.ts
└── environments/
```

---

## Core Implementation

### App Configuration

```typescript
// app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, withViewTransitions()),
    provideHttpClient(
      withInterceptors([authInterceptor, errorInterceptor])
    ),
    provideAnimations()
  ]
};
```

### Routes

```typescript
// app.routes.ts
export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'login', loadComponent: () => import('./features/auth/login/login.component') },
  { path: 'register', loadComponent: () => import('./features/auth/register/register.component') },
  {
    path: '',
    canActivate: [authGuard],
    children: [
      {
        path: 'dashboard',
        loadComponent: () => import('./features/dashboard/dashboard.component')
      },
      {
        path: 'tasks',
        loadChildren: () => import('./features/tasks/task.routes')
      }
    ]
  },
  { path: '**', redirectTo: 'dashboard' }
];
```

---

## Auth Module

### Auth Service

```typescript
// core/auth/auth.service.ts
interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private router = inject(Router);
  
  private state = signal<AuthState>({
    user: null,
    token: localStorage.getItem('token'),
    loading: false
  });

  user = computed(() => this.state().user);
  token = computed(() => this.state().token);
  isAuthenticated = computed(() => !!this.state().token);
  loading = computed(() => this.state().loading);

  login(credentials: LoginRequest): Observable<User> {
    this.state.update(s => ({ ...s, loading: true }));
    
    return this.http.post<AuthResponse>('/api/auth/login', credentials).pipe(
      tap(response => {
        localStorage.setItem('token', response.token);
        this.state.set({
          user: response.user,
          token: response.token,
          loading: false
        });
      }),
      map(response => response.user),
      catchError(error => {
        this.state.update(s => ({ ...s, loading: false }));
        return throwError(() => error);
      })
    );
  }

  register(data: RegisterRequest): Observable<User> {
    return this.http.post<AuthResponse>('/api/auth/register', data).pipe(
      tap(response => {
        localStorage.setItem('token', response.token);
        this.state.set({
          user: response.user,
          token: response.token,
          loading: false
        });
      }),
      map(response => response.user)
    );
  }

  logout(): void {
    localStorage.removeItem('token');
    this.state.set({ user: null, token: null, loading: false });
    this.router.navigate(['/login']);
  }

  loadUser(): void {
    const token = this.token();
    if (!token) return;

    this.http.get<User>('/api/auth/me').subscribe({
      next: user => this.state.update(s => ({ ...s, user })),
      error: () => this.logout()
    });
  }
}
```

### Auth Guard

```typescript
// core/auth/auth.guard.ts
export const authGuard: CanActivateFn = (route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);

  if (auth.isAuthenticated()) {
    return true;
  }

  return router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url }
  });
};
```

### Login Component

```typescript
// features/auth/login/login.component.ts
@Component({
  standalone: true,
  imports: [ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatButtonModule],
  template: `
    <div class="login-container">
      <mat-card>
        <mat-card-header>
          <mat-card-title>Login</mat-card-title>
        </mat-card-header>
        
        <mat-card-content>
          <form [formGroup]="form" (ngSubmit)="submit()">
            <mat-form-field>
              <mat-label>Email</mat-label>
              <input matInput type="email" formControlName="email">
              @if (form.get('email')?.hasError('required')) {
                <mat-error>Email is required</mat-error>
              }
              @if (form.get('email')?.hasError('email')) {
                <mat-error>Invalid email format</mat-error>
              }
            </mat-form-field>

            <mat-form-field>
              <mat-label>Password</mat-label>
              <input matInput type="password" formControlName="password">
              @if (form.get('password')?.hasError('required')) {
                <mat-error>Password is required</mat-error>
              }
            </mat-form-field>

            @if (error()) {
              <mat-error class="form-error">{{ error() }}</mat-error>
            }

            <button mat-raised-button color="primary" 
                    type="submit" 
                    [disabled]="form.invalid || auth.loading()">
              @if (auth.loading()) {
                <mat-spinner diameter="20" />
              } @else {
                Login
              }
            </button>
          </form>

          <p>Don't have an account? <a routerLink="/register">Register</a></p>
        </mat-card-content>
      </mat-card>
    </div>
  `
})
export default class LoginComponent {
  auth = inject(AuthService);
  router = inject(Router);
  route = inject(ActivatedRoute);
  
  error = signal('');

  form = inject(FormBuilder).nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required]
  });

  submit() {
    if (this.form.invalid) return;

    this.error.set('');
    this.auth.login(this.form.getRawValue()).subscribe({
      next: () => {
        const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/dashboard';
        this.router.navigateByUrl(returnUrl);
      },
      error: err => this.error.set(err.message || 'Login failed')
    });
  }
}
```

---

## Task Feature

### Task Model

```typescript
// features/tasks/task.model.ts
export interface Task {
  id: string;
  title: string;
  description: string;
  status: 'todo' | 'in-progress' | 'done';
  priority: 'low' | 'medium' | 'high';
  dueDate: Date | null;
  createdAt: Date;
  updatedAt: Date;
}
```

### Task Store

```typescript
// features/tasks/task.store.ts
interface TaskState {
  tasks: Task[];
  selectedTask: Task | null;
  loading: boolean;
  error: string | null;
  filter: { status?: string; priority?: string };
}

@Injectable()
export class TaskStore extends ComponentStore<TaskState> {
  private api = inject(TaskApiService);

  constructor() {
    super({
      tasks: [],
      selectedTask: null,
      loading: false,
      error: null,
      filter: {}
    });
  }

  // Selectors
  readonly tasks = this.selectSignal(state => state.tasks);
  readonly selectedTask = this.selectSignal(state => state.selectedTask);
  readonly loading = this.selectSignal(state => state.loading);
  readonly error = this.selectSignal(state => state.error);
  
  readonly filteredTasks = this.selectSignal(state => {
    let tasks = state.tasks;
    if (state.filter.status) {
      tasks = tasks.filter(t => t.status === state.filter.status);
    }
    if (state.filter.priority) {
      tasks = tasks.filter(t => t.priority === state.filter.priority);
    }
    return tasks;
  });

  readonly tasksByStatus = this.selectSignal(state => ({
    todo: state.tasks.filter(t => t.status === 'todo'),
    'in-progress': state.tasks.filter(t => t.status === 'in-progress'),
    done: state.tasks.filter(t => t.status === 'done')
  }));

  // Effects
  readonly loadTasks = this.effect<void>(trigger$ => {
    return trigger$.pipe(
      tap(() => this.patchState({ loading: true, error: null })),
      switchMap(() => this.api.getTasks().pipe(
        tapResponse(
          tasks => this.patchState({ tasks, loading: false }),
          error => this.patchState({ error: error.message, loading: false })
        )
      ))
    );
  });

  readonly createTask = this.effect((task$: Observable<Partial<Task>>) => {
    return task$.pipe(
      switchMap(task => this.api.createTask(task).pipe(
        tapResponse(
          newTask => this.patchState(state => ({ tasks: [...state.tasks, newTask] })),
          error => this.patchState({ error: error.message })
        )
      ))
    );
  });

  readonly updateTask = this.effect((params$: Observable<{ id: string; changes: Partial<Task> }>) => {
    return params$.pipe(
      switchMap(({ id, changes }) => this.api.updateTask(id, changes).pipe(
        tapResponse(
          updated => this.patchState(state => ({
            tasks: state.tasks.map(t => t.id === id ? updated : t),
            selectedTask: state.selectedTask?.id === id ? updated : state.selectedTask
          })),
          error => this.patchState({ error: error.message })
        )
      ))
    );
  });

  readonly deleteTask = this.effect((id$: Observable<string>) => {
    return id$.pipe(
      switchMap(id => this.api.deleteTask(id).pipe(
        tapResponse(
          () => this.patchState(state => ({
            tasks: state.tasks.filter(t => t.id !== id),
            selectedTask: state.selectedTask?.id === id ? null : state.selectedTask
          })),
          error => this.patchState({ error: error.message })
        )
      ))
    );
  });

  // Updaters
  readonly selectTask = this.updater((state, task: Task | null) => ({
    ...state,
    selectedTask: task
  }));

  readonly setFilter = this.updater((state, filter: TaskState['filter']) => ({
    ...state,
    filter: { ...state.filter, ...filter }
  }));
}
```

### Task List Component

```typescript
// features/tasks/task-list/task-list.component.ts
@Component({
  standalone: true,
  imports: [TaskCardComponent, TaskFilterComponent, MatButtonModule],
  providers: [TaskStore],
  template: `
    <div class="task-list-container">
      <header>
        <h1>My Tasks</h1>
        <button mat-raised-button color="primary" (click)="openCreateDialog()">
          <mat-icon>add</mat-icon> New Task
        </button>
      </header>

      <app-task-filter (filterChange)="store.setFilter($event)" />

      @if (store.loading()) {
        <mat-progress-bar mode="indeterminate" />
      }

      @if (store.error()) {
        <mat-error>{{ store.error() }}</mat-error>
      }

      <div class="kanban-board">
        @for (column of columns; track column.status) {
          <div class="column">
            <h2>{{ column.label }} ({{ getTaskCount(column.status) }})</h2>
            
            <div class="task-cards"
                 cdkDropList
                 [cdkDropListData]="getTasksByStatus(column.status)"
                 (cdkDropListDropped)="onDrop($event, column.status)">
              @for (task of getTasksByStatus(column.status); track task.id) {
                <app-task-card 
                  [task]="task"
                  cdkDrag
                  (click)="openDetailDialog(task)"
                  (delete)="store.deleteTask(task.id)" />
              } @empty {
                <p class="empty">No tasks</p>
              }
            </div>
          </div>
        }
      </div>
    </div>
  `
})
export default class TaskListComponent implements OnInit {
  store = inject(TaskStore);
  dialog = inject(MatDialog);

  columns = [
    { status: 'todo', label: 'To Do' },
    { status: 'in-progress', label: 'In Progress' },
    { status: 'done', label: 'Done' }
  ];

  ngOnInit() {
    this.store.loadTasks();
  }

  getTasksByStatus(status: string): Task[] {
    return this.store.tasksByStatus()[status as keyof ReturnType<typeof this.store.tasksByStatus>];
  }

  getTaskCount(status: string): number {
    return this.getTasksByStatus(status).length;
  }

  onDrop(event: CdkDragDrop<Task[]>, newStatus: string) {
    if (event.previousContainer === event.container) return;
    
    const task = event.previousContainer.data[event.previousIndex];
    this.store.updateTask({ id: task.id, changes: { status: newStatus as Task['status'] } });
  }

  openCreateDialog() {
    const dialogRef = this.dialog.open(TaskFormComponent, { width: '500px' });
    dialogRef.afterClosed().subscribe(result => {
      if (result) this.store.createTask(result);
    });
  }

  openDetailDialog(task: Task) {
    this.dialog.open(TaskDetailComponent, { data: task, width: '600px' });
  }
}
```

### Task Form Component

```typescript
// features/tasks/task-form/task-form.component.ts
@Component({
  standalone: true,
  imports: [ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatSelectModule, MatDatepickerModule, MatButtonModule],
  template: `
    <h2 mat-dialog-title>{{ data ? 'Edit Task' : 'New Task' }}</h2>
    
    <mat-dialog-content>
      <form [formGroup]="form">
        <mat-form-field>
          <mat-label>Title</mat-label>
          <input matInput formControlName="title">
          @if (form.get('title')?.hasError('required')) {
            <mat-error>Title is required</mat-error>
          }
        </mat-form-field>

        <mat-form-field>
          <mat-label>Description</mat-label>
          <textarea matInput formControlName="description" rows="4"></textarea>
        </mat-form-field>

        <mat-form-field>
          <mat-label>Status</mat-label>
          <mat-select formControlName="status">
            <mat-option value="todo">To Do</mat-option>
            <mat-option value="in-progress">In Progress</mat-option>
            <mat-option value="done">Done</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field>
          <mat-label>Priority</mat-label>
          <mat-select formControlName="priority">
            <mat-option value="low">Low</mat-option>
            <mat-option value="medium">Medium</mat-option>
            <mat-option value="high">High</mat-option>
          </mat-select>
        </mat-form-field>

        <mat-form-field>
          <mat-label>Due Date</mat-label>
          <input matInput [matDatepicker]="picker" formControlName="dueDate">
          <mat-datepicker-toggle matSuffix [for]="picker" />
          <mat-datepicker #picker />
        </mat-form-field>
      </form>
    </mat-dialog-content>

    <mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button mat-raised-button color="primary" 
              [disabled]="form.invalid"
              (click)="save()">
        Save
      </button>
    </mat-dialog-actions>
  `
})
export class TaskFormComponent {
  dialogRef = inject(MatDialogRef);
  data = inject(MAT_DIALOG_DATA, { optional: true }) as Task | null;

  form = inject(FormBuilder).nonNullable.group({
    title: [this.data?.title ?? '', Validators.required],
    description: [this.data?.description ?? ''],
    status: [this.data?.status ?? 'todo'],
    priority: [this.data?.priority ?? 'medium'],
    dueDate: [this.data?.dueDate ?? null]
  });

  save() {
    if (this.form.valid) {
      this.dialogRef.close(this.form.getRawValue());
    }
  }
}
```

---

## Shared Components

### Task Card Component

```typescript
// shared/components/task-card/task-card.component.ts
@Component({
  standalone: true,
  selector: 'app-task-card',
  imports: [MatCardModule, MatIconModule, MatChipModule],
  template: `
    <mat-card [class]="'priority-' + task.priority">
      <mat-card-header>
        <mat-card-title>{{ task.title }}</mat-card-title>
        <button mat-icon-button (click)="onDelete($event)">
          <mat-icon>delete</mat-icon>
        </button>
      </mat-card-header>
      
      <mat-card-content>
        <p>{{ task.description | slice:0:100 }}{{ task.description.length > 100 ? '...' : '' }}</p>
      </mat-card-content>
      
      <mat-card-footer>
        <mat-chip [color]="priorityColor">{{ task.priority }}</mat-chip>
        @if (task.dueDate) {
          <span class="due-date">
            <mat-icon>event</mat-icon>
            {{ task.dueDate | date:'shortDate' }}
          </span>
        }
      </mat-card-footer>
    </mat-card>
  `
})
export class TaskCardComponent {
  @Input({ required: true }) task!: Task;
  @Output() delete = new EventEmitter<void>();

  get priorityColor(): string {
    return { high: 'warn', medium: 'accent', low: 'primary' }[this.task.priority];
  }

  onDelete(event: Event) {
    event.stopPropagation();
    this.delete.emit();
  }
}
```

---

## Running the Project

```bash
# Create new Angular app
ng new task-manager --standalone --routing --style=scss

# Add Angular Material
ng add @angular/material

# Add CDK for drag-drop
ng add @angular/cdk

# Generate components
ng g c features/auth/login --standalone
ng g c features/tasks/task-list --standalone
ng g c features/tasks/task-form --standalone

# Serve
ng serve
```

---

## Key Takeaways

| Concept | Implementation |
|---------|---------------|
| State Management | ComponentStore with signals |
| Forms | Reactive forms with validation |
| Auth | JWT with guards and interceptors |
| Lazy Loading | Route-based code splitting |
| UI | Angular Material components |
| Drag & Drop | CDK DragDrop module |
