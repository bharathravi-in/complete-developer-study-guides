# Day 20: SSR & Hydration - Interview Questions & Answers

## Basic Level

### Q1: What is Server-Side Rendering (SSR)?

**Answer:**
SSR renders Angular applications on the server, sending fully populated HTML to the browser instead of an empty shell.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SSR vs CSR                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  CSR (Client-Side Rendering):                                        │
│  Server → Empty HTML → Browser downloads JS → Renders content       │
│           ↓                                                          │
│        [Blank page while JS loads]                                   │
│                                                                      │
│  SSR (Server-Side Rendering):                                        │
│  Server → Rendered HTML → Browser shows content → JS hydrates       │
│           ↓                                                          │
│        [Content visible immediately]                                 │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Benefits:**
- **SEO** - Search engines see full content
- **Fast FCP** - Content visible before JS loads
- **Social sharing** - Meta tags work properly
- **Slow devices** - Less client-side processing

---

### Q2: How do you set up SSR in Angular?

**Answer:**
```bash
# Add SSR to existing project
ng add @angular/ssr

# This creates:
# - server.ts (Express server)
# - app.config.server.ts (Server config)
# - Updates angular.json
```

```typescript
// app.config.ts
import { provideClientHydration } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideClientHydration(),  // Enable hydration
    provideHttpClient(withFetch())
  ]
};

// app.config.server.ts
import { provideServerRendering } from '@angular/platform-server';

const serverConfig: ApplicationConfig = {
  providers: [provideServerRendering()]
};

export const config = mergeApplicationConfig(appConfig, serverConfig);
```

---

### Q3: What is Hydration?

**Answer:**
Hydration is the process of making server-rendered HTML interactive by attaching event listeners and enabling Angular's change detection.

```typescript
// Enable hydration
import { provideClientHydration } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration()
  ]
};
```

**Hydration Process:**
1. Server renders HTML with data
2. Browser displays HTML immediately
3. Angular downloads and boots
4. Angular matches DOM nodes (doesn't re-create them)
5. Angular attaches event listeners
6. App becomes interactive

---

## Intermediate Level

### Q4: How do you detect if code is running on server or browser?

**Answer:**
```typescript
import { isPlatformBrowser, isPlatformServer, PLATFORM_ID } from '@angular/common';

@Component({...})
export class MyComponent {
  private platformId = inject(PLATFORM_ID);

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      // Browser-only code
      localStorage.setItem('key', 'value');
      this.initScrollListener();
    }

    if (isPlatformServer(this.platformId)) {
      // Server-only code
      console.log('Rendering on server');
    }
  }
}
```

**Better approach with afterNextRender:**
```typescript
import { afterNextRender } from '@angular/core';

@Component({...})
export class ChartComponent {
  constructor() {
    afterNextRender(() => {
      // Always runs in browser, never on server
      // Safe to use window, document, DOM APIs
      this.initChart();
    });
  }
}
```

---

### Q5: How do you handle browser-only APIs with SSR?

**Answer:**

**Problem:**
```typescript
// ❌ Breaks on server
@Component({...})
export class BadComponent {
  ngOnInit() {
    window.addEventListener('scroll', this.onScroll);  // window is undefined!
  }
}
```

**Solutions:**

```typescript
// Solution 1: Platform check
@Component({...})
export class Solution1Component {
  private platformId = inject(PLATFORM_ID);

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      window.addEventListener('scroll', this.onScroll);
    }
  }
}

// Solution 2: afterNextRender (preferred)
@Component({...})
export class Solution2Component {
  constructor() {
    afterNextRender(() => {
      window.addEventListener('scroll', this.onScroll);
    });
  }
}

// Solution 3: Dynamic import for libraries
@Component({...})
export class Solution3Component {
  constructor() {
    afterNextRender(async () => {
      const { gsap } = await import('gsap');
      gsap.to('.element', { x: 100 });
    });
  }
}
```

---

### Q6: How does TransferState work?

**Answer:**
TransferState prevents duplicate API calls by transferring data from server to client.

```typescript
// Automatic with HTTP client
import { provideClientHydration, withHttpTransferCacheOptions } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration(
      withHttpTransferCacheOptions({
        includePostRequests: true
      })
    ),
    provideHttpClient(withFetch())
  ]
};

// HTTP requests are automatically cached
@Component({...})
export class ProductComponent {
  product$ = this.http.get<Product>('/api/products/1');
  // Server makes request, transfers response
  // Client reuses transferred data
}
```

**Manual TransferState:**
```typescript
import { makeStateKey, TransferState } from '@angular/core';

const DATA_KEY = makeStateKey<Data>('data');

@Injectable({ providedIn: 'root' })
export class DataService {
  private transferState = inject(TransferState);
  private platformId = inject(PLATFORM_ID);

  getData(): Observable<Data> {
    const cached = this.transferState.get(DATA_KEY, null);
    
    if (cached) {
      this.transferState.remove(DATA_KEY);
      return of(cached);
    }

    return this.http.get<Data>('/api/data').pipe(
      tap(data => {
        if (isPlatformServer(this.platformId)) {
          this.transferState.set(DATA_KEY, data);
        }
      })
    );
  }
}
```

---

### Q7: How do you implement SEO with SSR?

**Answer:**
```typescript
import { Meta, Title } from '@angular/platform-browser';

@Injectable({ providedIn: 'root' })
export class SeoService {
  private meta = inject(Meta);
  private title = inject(Title);

  updateSeo(config: SeoConfig) {
    // Title
    this.title.setTitle(config.title);

    // Description
    this.meta.updateTag({ name: 'description', content: config.description });

    // Open Graph (Facebook, LinkedIn)
    this.meta.updateTag({ property: 'og:title', content: config.title });
    this.meta.updateTag({ property: 'og:description', content: config.description });
    this.meta.updateTag({ property: 'og:image', content: config.image });
    this.meta.updateTag({ property: 'og:url', content: config.url });

    // Twitter Card
    this.meta.updateTag({ name: 'twitter:card', content: 'summary_large_image' });
    this.meta.updateTag({ name: 'twitter:title', content: config.title });
  }
}

// Usage in component
@Component({...})
export class ProductPageComponent {
  private seo = inject(SeoService);

  product = input.required<Product>();

  constructor() {
    effect(() => {
      const p = this.product();
      this.seo.updateSeo({
        title: `${p.name} | Store`,
        description: p.description,
        image: p.imageUrl,
        url: `https://store.com/products/${p.id}`
      });
    });
  }
}
```

---

## Advanced Level

### Q8: What is Incremental Hydration?

**Answer:**
Incremental Hydration (Angular 17+) allows deferring hydration of specific components, reducing initial JavaScript execution.

```typescript
// Enable incremental hydration
import { provideClientHydration, withIncrementalHydration } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration(withIncrementalHydration())
  ]
};

// Component with deferred hydration
@Component({
  template: `
    <!-- Hydrate when user interacts -->
    @defer (hydrate on interaction) {
      <app-comments [postId]="postId" />
    }

    <!-- Hydrate when visible in viewport -->
    @defer (hydrate on viewport) {
      <app-related-products />
    }

    <!-- Hydrate when browser is idle -->
    @defer (hydrate on idle) {
      <app-newsletter-signup />
    }

    <!-- Hydrate after delay -->
    @defer (hydrate on timer(3s)) {
      <app-recommendations />
    }

    <!-- Never hydrate (static content) -->
    @defer (hydrate never) {
      <app-static-footer />
    }
  `
})
```

**Benefits:**
- Faster Time to Interactive (TTI)
- Reduced main thread work
- Progressive enhancement

---

### Q9: How do you handle event replay during hydration?

**Answer:**
Event replay captures user interactions during hydration and replays them after the app is interactive.

```typescript
// Enable event replay
import { provideClientHydration, withEventReplay } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration(withEventReplay())
  ]
};
```

**How it works:**
```
Timeline:
─────────────────────────────────────────────────────────────────────
1. Server HTML rendered        [Content visible]
2. User clicks button          [Event captured but app not ready]
3. JavaScript loads            [Hydration begins]
4. Hydration completes         [Event replayed → handler executes]
─────────────────────────────────────────────────────────────────────
```

**Without event replay:**
- Click happens during hydration → Lost
- User must click again

**With event replay:**
- Click captured during hydration
- Replayed once app is interactive
- Better UX

---

### Q10: What is Prerendering vs SSR?

**Answer:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Prerendering vs SSR                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Prerendering (Static Site Generation):                              │
│  • HTML generated at BUILD time                                      │
│  • Static files served by CDN                                        │
│  • No Node.js server required                                        │
│  • Best for: Static content, marketing pages                         │
│                                                                      │
│  SSR (Server-Side Rendering):                                        │
│  • HTML generated at REQUEST time                                    │
│  • Requires Node.js server                                           │
│  • Dynamic content per request                                       │
│  • Best for: User-specific content, real-time data                   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Prerender configuration:**
```json
// angular.json
{
  "prerender": {
    "builder": "@angular/build:prerender",
    "options": {
      "routes": [
        "/",
        "/about",
        "/products/1",
        "/products/2"
      ]
    }
  }
}
```

**When to use each:**
| Use Prerendering | Use SSR |
|-----------------|---------|
| Marketing pages | User dashboards |
| Blog posts | Personalized content |
| Documentation | Real-time data |
| Product pages (static) | Search results |

---

### Q11: How do you troubleshoot SSR issues?

**Answer:**

**Common issues and solutions:**

```typescript
// Issue 1: "window is not defined"
// Solution: Use afterNextRender or platform check
afterNextRender(() => {
  window.scrollTo(0, 0);
});

// Issue 2: Hydration mismatch
// Cause: Server and client render different content
// Solution: Ensure deterministic rendering
@Component({
  template: `
    <!-- ❌ Different on server vs client -->
    <p>Time: {{ new Date() }}</p>
    
    <!-- ✅ Consistent rendering -->
    <p>Time: {{ fixedTime }}</p>
  `
})
export class TimeComponent {
  fixedTime = new Date().toISOString();
}

// Issue 3: Memory leaks on server
// Solution: Complete observables
@Component({...})
export class DataComponent implements OnDestroy {
  private destroy$ = new Subject<void>();

  data$ = this.http.get('/api/data').pipe(
    takeUntil(this.destroy$)
  );

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}

// Issue 4: Third-party library not SSR-compatible
// Solution: Dynamic import with afterNextRender
constructor() {
  afterNextRender(async () => {
    const { Chart } = await import('chart.js');
    // Use Chart...
  });
}
```

---

## Quick Reference

```
SSR Lifecycle:
──────────────
1. Request hits server
2. Angular renders on server (CommonEngine)
3. Server sends HTML + serialized state
4. Browser displays HTML (FCP)
5. Browser downloads JS
6. Angular hydrates (matches DOM, attaches listeners)
7. App is interactive (TTI)

Key Providers:
──────────────
provideClientHydration()           - Enable hydration
withIncrementalHydration()         - Deferred hydration
withEventReplay()                  - Capture events during hydration  
withHttpTransferCacheOptions()     - HTTP state transfer
provideServerRendering()           - Server-side provider

Platform Detection:
───────────────────
isPlatformBrowser(platformId)      - Check if browser
isPlatformServer(platformId)       - Check if server
afterNextRender(() => {})          - Browser-only code
afterRender(() => {})              - After each render

@defer Hydration Triggers:
──────────────────────────
hydrate on interaction             - User click/focus
hydrate on viewport                - Element visible
hydrate on idle                    - Browser idle
hydrate on timer(Xs)               - After X seconds
hydrate never                      - Never hydrate

Build Commands:
───────────────
ng build                           - Build with SSR
ng serve --ssr                     - Dev server with SSR
node dist/app/server/server.mjs    - Run production
```
