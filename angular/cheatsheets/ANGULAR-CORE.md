# Angular Core Cheatsheet

## Component Syntax (Angular 22+)

```typescript
@Component({
  standalone: true,
  selector: 'app-example',
  imports: [CommonModule, MyOtherComponent],
  template: `...`,
  styleUrl: './example.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class ExampleComponent {
  // Input signals
  title = input<string>();                    // Optional
  id = input.required<number>();              // Required
  count = input(0);                           // With default
  transformed = input(0, { transform: numberAttribute });
  aliased = input('', { alias: 'externalName' });

  // Output signals  
  clicked = output<MouseEvent>();
  customEvent = output<{ id: number }>();

  // Two-way binding
  value = model('');                          // model signal

  // View queries
  child = viewChild(ChildComponent);          // Single
  children = viewChildren(ChildComponent);    // Multiple
  template = viewChild('templateRef');        // By template ref

  // Content queries
  projected = contentChild(ProjectedComponent);
  projectedAll = contentChildren(ProjectedComponent);

  // State
  count = signal(0);
  doubled = computed(() => this.count() * 2);

  // Effect
  constructor() {
    effect(() => console.log('Count:', this.count()));
  }
}
```

## Control Flow

```html
<!-- @if -->
@if (isLoggedIn) {
  <app-dashboard />
} @else if (isLoading) {
  <app-loader />
} @else {
  <app-login />
}

<!-- @for (with track required) -->
@for (item of items; track item.id; let i = $index, first = $first, last = $last) {
  <div [class.first]="first">{{ i }}: {{ item.name }}</div>
} @empty {
  <p>No items found</p>
}

<!-- @switch -->
@switch (status) {
  @case ('pending') { <span class="yellow">Pending</span> }
  @case ('active') { <span class="green">Active</span> }
  @case ('inactive') { <span class="red">Inactive</span> }
  @default { <span>Unknown</span> }
}

<!-- @defer -->
@defer (on viewport; prefetch on idle) {
  <app-heavy-component />
} @placeholder (minimum 200ms) {
  <div class="placeholder">Loading...</div>
} @loading (after 150ms; minimum 300ms) {
  <mat-spinner />
} @error {
  <p>Failed to load</p>
}
```

## Defer Triggers

| Trigger | Description |
|---------|-------------|
| `on idle` | Browser is idle |
| `on viewport` | Element enters viewport |
| `on interaction` | User clicks/focuses |
| `on hover` | Mouse hovers |
| `on immediate` | Loads immediately |
| `on timer(Xms)` | After X milliseconds |
| `when expression` | When expression is true |

## Signals

```typescript
// Create
const count = signal(0);
const user = signal<User | null>(null);

// Read
count()                        // Returns value

// Write
count.set(5);                  // Replace value
count.update(v => v + 1);      // Update based on current

// Computed (derived, read-only)
const doubled = computed(() => count() * 2);
const fullName = computed(() => `${user()?.first} ${user()?.last}`);

// Effect (side effects)
effect(() => {
  console.log('Count changed:', count());
  localStorage.setItem('count', count().toString());
});

// effect cleanup
effect((onCleanup) => {
  const timer = setInterval(() => tick(), 1000);
  onCleanup(() => clearInterval(timer));
});
```

## Lifecycle Hooks

| Hook | Purpose |
|------|---------|
| `ngOnChanges` | Input property changes |
| `ngOnInit` | Component initialized |
| `ngDoCheck` | Custom change detection |
| `ngAfterContentInit` | Content projected |
| `ngAfterContentChecked` | Content checked |
| `ngAfterViewInit` | View initialized |
| `ngAfterViewChecked` | View checked |
| `ngOnDestroy` | Before destruction |

```typescript
export class MyComponent implements OnInit, OnDestroy {
  destroyRef = inject(DestroyRef);

  ngOnInit() {
    // Use destroyRef instead of ngOnDestroy
    this.destroyRef.onDestroy(() => {
      // cleanup
    });
  }
}
```

## Change Detection

```typescript
// OnPush - only checks when:
// 1. Input reference changes
// 2. Event in component fires
// 3. Async pipe receives value
// 4. markForCheck() called

@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class MyComponent {
  private cdr = inject(ChangeDetectorRef);

  manualUpdate() {
    this.cdr.markForCheck();  // Mark for next CD cycle
    this.cdr.detectChanges(); // Run CD immediately
  }
}

// Zoneless (experimental)
bootstrapApplication(AppComponent, {
  providers: [provideExperimentalZonelessChangeDetection()]
});
```

## Dependency Injection

```typescript
// Service registration
@Injectable({ providedIn: 'root' })     // Singleton (tree-shakable)
@Injectable({ providedIn: 'platform' }) // Shared across apps
@Injectable()                            // Needs explicit provider

// Injection
class MyComponent {
  // Modern (preferred)
  service = inject(MyService);
  router = inject(Router);
  
  // With options
  optional = inject(MyService, { optional: true });
  self = inject(MyService, { self: true });
  skipSelf = inject(MyService, { skipSelf: true });
  host = inject(MyService, { host: true });
}

// InjectionToken
export const API_URL = new InjectionToken<string>('API_URL');

// Providers
providers: [
  MyService,                                           // Class
  { provide: MyService, useClass: MockService },       // Replace
  { provide: API_URL, useValue: 'https://api.com' },   // Value
  { provide: MyService, useExisting: OtherService },   // Alias
  { provide: MyService, useFactory: () => new MyService(), deps: [] }
]
```

## Directives

```typescript
// Attribute directive
@Directive({
  standalone: true,
  selector: '[appHighlight]'
})
export class HighlightDirective {
  color = input('yellow', { alias: 'appHighlight' });
  private el = inject(ElementRef);

  constructor() {
    effect(() => {
      this.el.nativeElement.style.backgroundColor = this.color();
    });
  }
}

// Structural directive
@Directive({
  standalone: true,
  selector: '[appIf]'
})
export class IfDirective {
  private vcr = inject(ViewContainerRef);
  private template = inject(TemplateRef);

  condition = input(false, { alias: 'appIf' });

  constructor() {
    effect(() => {
      this.vcr.clear();
      if (this.condition()) {
        this.vcr.createEmbeddedView(this.template);
      }
    });
  }
}
```

## Pipes

```typescript
@Pipe({
  standalone: true,
  name: 'truncate',
  pure: true  // default, memoized
})
export class TruncatePipe implements PipeTransform {
  transform(value: string, limit = 50): string {
    return value.length > limit ? value.slice(0, limit) + '...' : value;
  }
}

// Usage
{{ longText | truncate:100 }}

// Built-in pipes
{{ date | date:'short' }}
{{ price | currency:'USD' }}
{{ value | number:'1.2-2' }}
{{ object | json }}
{{ items | slice:0:5 }}
{{ name | uppercase }}
{{ name | lowercase }}
{{ name | titlecase }}
{{ data$ | async }}
```

## Template Reference Variables

```html
<!-- Element reference -->
<input #nameInput>
<button (click)="greet(nameInput.value)">Greet</button>

<!-- Directive reference -->
<form #myForm="ngForm">
  <input name="email" ngModel required>
  <button [disabled]="myForm.invalid">Submit</button>
</form>

<!-- Component reference -->
<app-counter #counter></app-counter>
<button (click)="counter.increment()">+</button>
```

## App Configuration

```typescript
// app.config.ts
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes, 
      withViewTransitions(),
      withComponentInputBinding()
    ),
    provideHttpClient(
      withInterceptors([authInterceptor, errorInterceptor]),
      withFetch()
    ),
    provideAnimationsAsync(),
    provideClientHydration()
  ]
};

// main.ts
bootstrapApplication(AppComponent, appConfig);
```
