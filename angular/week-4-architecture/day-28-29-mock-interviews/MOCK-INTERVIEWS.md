# Days 28-29: Mock Interview Questions

## Technical Interview Questions

### Category 1: Angular Core Concepts

#### Q1: Explain Angular's change detection and OnPush strategy.

**Expected Answer:**
- Default change detection checks entire component tree on events
- OnPush only checks when:
  - Input reference changes
  - Event fired in component/child
  - Async pipe receives value
  - Manual `markForCheck()` called
- Use signals for automatic granular updates
- Zoneless mode eliminates Zone.js overhead

**Follow-up:** How does zoneless CD work?
- Uses `provideExperimentalZonelessChangeDetection()`
- Relies on signals for reactivity
- Scheduler triggers updates only when signals change

---

#### Q2: What are standalone components and why use them?

**Expected Answer:**
```typescript
@Component({
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `...`
})
export class MyComponent {}
```

**Benefits:**
- No NgModule declarations required
- Direct imports in component
- Smaller bundle sizes (tree-shakable)
- Simpler mental model
- Better lazy loading

---

#### Q3: Explain the defer block and its triggers.

**Expected Answer:**
```typescript
@defer (on viewport) {
  <app-heavy-component />
} @placeholder {
  <div class="skeleton" />
} @loading (minimum 500ms) {
  <mat-spinner />
} @error {
  <p>Failed to load</p>
}
```

**Triggers:**
- `on viewport` - element enters viewport
- `on idle` - browser idle
- `on immediate` - immediately
- `on interaction` - user interacts
- `on timer(2s)` - after delay
- `on hover` - mouse hover
- `when condition` - expression true

---

### Category 2: RxJS

#### Q4: Explain switchMap vs mergeMap vs concatMap.

**Expected Answer:**

| Operator | Behavior | Use Case |
|----------|----------|----------|
| switchMap | Cancels previous, uses latest | Search (typeahead) |
| mergeMap | All concurrent | Parallel downloads |
| concatMap | Sequential queue | Form submissions |

```typescript
// switchMap - search
search$.pipe(
  switchMap(term => this.api.search(term))
);

// mergeMap - concurrent
files$.pipe(
  mergeMap(file => this.api.upload(file), 3) // max 3 concurrent
);

// concatMap - sequential
actions$.pipe(
  concatMap(action => this.api.process(action))
);
```

---

#### Q5: How do you handle memory leaks in RxJS?

**Expected Answer:**
```typescript
// 1. takeUntilDestroyed (best for Angular 16+)
ngOnInit() {
  this.service.data$.pipe(
    takeUntilDestroyed(this.destroyRef)
  ).subscribe();
}

// 2. Async pipe (auto-unsubscribes)
@Component({
  template: `{{ data$ | async }}`
})

// 3. takeUntil with subject
private destroy$ = new Subject<void>();
ngOnDestroy() { this.destroy$.next(); }

this.data$.pipe(takeUntil(this.destroy$)).subscribe();
```

---

### Category 3: State Management

#### Q6: Compare BehaviorSubject vs Signal for state.

**Expected Answer:**

**BehaviorSubject:**
```typescript
private state$ = new BehaviorSubject<State>(initial);
current$ = this.state$.asObservable();
update(value: State) { this.state$.next(value); }
```

**Signal:**
```typescript
state = signal<State>(initial);
update(value: State) { this.state.set(value); }
// Or: this.state.update(s => ({...s, ...changes}));
```

**Signal Advantages:**
- Synchronous reads
- No subscription management
- Automatic change detection
- Better debugging
- Granular updates via computed()

---

#### Q7: How would you design state for a large app?

**Expected Answer:**
```
State Architecture:
───────────────────
Global State (NgRx/Signal Store)
  ├── Auth state
  ├── User preferences
  └── App-wide notifications

Feature State (ComponentStore)
  ├── Product catalog
  ├── Shopping cart
  └── Order history

Local State (Signals)
  ├── Form state
  ├── UI toggles
  └── Component-specific data
```

**Principles:**
- Global for shared data across features
- Feature stores for domain logic
- Local signals for ephemeral UI state
- Facades to simplify component interaction

---

### Category 4: Performance

#### Q8: How do you optimize Angular app performance?

**Expected Answer:**

1. **Change Detection:**
   - OnPush strategy
   - Signals instead of getters
   - trackBy in @for loops

2. **Loading:**
   - Lazy load routes
   - @defer blocks
   - Preloading strategies

3. **Bundle Size:**
   - Standalone components
   - Tree-shaking
   - Analyze with source-map-explorer

4. **Runtime:**
   - Virtual scrolling
   - Memoize expensive computations
   - Debounce user inputs

5. **Network:**
   - HTTP caching
   - Compression
   - CDN for assets

---

#### Q9: How does SSR improve performance?

**Expected Answer:**
```typescript
// app.config.server.ts
export const config: ApplicationConfig = {
  providers: [
    provideServerRendering(),
    provideClientHydration(withEventReplay())
  ]
};
```

**Benefits:**
- Faster First Contentful Paint (FCP)
- Better SEO
- Works without JavaScript initially
- Incremental hydration defers interactivity

**Hydration:** Attaches event listeners without re-rendering DOM.

---

### Category 5: Architecture

#### Q10: Explain smart vs dumb component pattern.

**Expected Answer:**

**Smart (Container):**
```typescript
@Component({
  template: '<app-user-list [users]="store.users()" (select)="onSelect($event)" />'
})
export class UsersContainerComponent {
  store = inject(UserStore);
  onSelect(user: User) { this.store.selectUser(user); }
}
```

**Dumb (Presentational):**
```typescript
@Component({
  selector: 'app-user-list',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class UserListComponent {
  @Input() users: User[] = [];
  @Output() select = new EventEmitter<User>();
}
```

**Benefits:**
- Separation of concerns
- Reusability
- Easier testing
- Predictable data flow

---

#### Q11: How do you design a micro frontend architecture?

**Expected Answer:**
```
Shell (Host)
├── Layout/Navigation
├── Shared state
└── Routes to remotes

Remotes (Feature MFEs)
├── Product Catalog
├── Shopping Cart
└── Checkout

Shared Libraries
├── UI components
├── Auth services
└── API clients
```

**Implementation:**
- Nx workspace + Module Federation
- Shared dependencies (singletons)
- Cross-MFE state via events/store
- Independent deployment

---

### Category 6: Testing

#### Q12: How do you test a component with dependencies?

**Expected Answer:**
```typescript
describe('UserListComponent', () => {
  let component: UserListComponent;
  let userService: jasmine.SpyObj<UserService>;

  beforeEach(async () => {
    userService = jasmine.createSpyObj('UserService', ['getUsers']);
    userService.getUsers.and.returnValue(of([mockUser]));

    await TestBed.configureTestingModule({
      imports: [UserListComponent],
      providers: [
        { provide: UserService, useValue: userService }
      ]
    }).compileComponents();

    component = TestBed.createComponent(UserListComponent).componentInstance;
  });

  it('should load users on init', () => {
    component.ngOnInit();
    expect(userService.getUsers).toHaveBeenCalled();
    expect(component.users()).toEqual([mockUser]);
  });
});
```

---

## Behavioral Questions

### Q13: Describe a challenging technical problem you solved.

**Framework for Answer:**
1. **Situation:** Brief context
2. **Task:** What needed to be done
3. **Action:** Steps you took
4. **Result:** Outcome with metrics

**Example:**
"Our Angular app had severe performance issues with 10,000 items rendering. I implemented virtual scrolling using CDK, added OnPush change detection, and used trackBy. Result: render time dropped from 3s to 50ms."

---

### Q14: How do you handle disagreements on technical decisions?

**Good Answer Points:**
- Listen to understand other perspectives
- Present data/benchmarks to support position
- Focus on project goals, not personal preferences
- Prototype both approaches if time permits
- Accept team decision once made
- Document reasoning for future reference

---

### Q15: How do you stay current with Angular updates?

**Expected Answer:**
- Follow Angular blog and changelog
- Angular Discord/Twitter
- Watch ng-conf, Angular team YouTube
- Side projects to try new features
- Read RFC discussions
- Contribute to open source

---

## Scenario-Based Questions

### Q16: A page is slow. How do you diagnose and fix it?

**Answer:**

1. **Profile:** Chrome DevTools Performance tab
2. **Identify bottlenecks:**
   - Large JS bundles → lazy load
   - Many re-renders → OnPush, signals
   - Heavy computations → memoize, Web Workers
   - Long API calls → caching, pagination
3. **Measure:** Lighthouse scores before/after
4. **Monitor:** Set up performance budgets

---

### Q17: Your team is starting a new Angular project. What architecture would you recommend?

**Answer:**
```
Recommended Structure:
──────────────────────
/src
  /app
    /core        - singletons, guards, interceptors
    /shared      - reusable components, pipes, directives
    /features    - feature modules (lazy loaded)
    /layouts     - page layouts
  /libs          - if using Nx monorepo

Key Decisions:
- Standalone components (no NgModules)
- NgRx Signal Store for state
- Reactive forms
- OnPush change detection everywhere
- Enforce with ESLint rules
```

---

## Quick Tips for Interview Day

1. **Explain your thought process** - talk through problems
2. **Ask clarifying questions** - shows thoroughness
3. **Mention trade-offs** - no solution is perfect
4. **Use real examples** - from your experience
5. **Be honest** - say "I don't know" if needed
6. **Practice coding** - be comfortable typing
7. **Review fundamentals** - core concepts matter
