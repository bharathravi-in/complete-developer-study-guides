# Day 20: Server-Side Rendering (SSR) & Hydration

## Overview

Server-Side Rendering (SSR) renders Angular applications on the server, delivering fully rendered HTML to the browser. This improves initial load performance and SEO.

---

## Why SSR?

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CSR vs SSR                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Client-Side Rendering (CSR):                                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │ Request  │ →  │  Empty   │ →  │ Download │ →  │  Render  │      │
│  │   HTML   │    │   HTML   │    │    JS    │    │   App    │      │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘      │
│       ↓              ↓                ↓                ↓            │
│    Browser       Blank Page      Loading...      Content            │
│                                                                      │
│  Server-Side Rendering (SSR):                                        │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐      │
│  │  Server  │ →  │   Full   │ →  │ Download │ →  │ Hydrate  │      │
│  │  Render  │    │   HTML   │    │    JS    │    │   App    │      │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘      │
│       ↓              ↓                ↓                ↓            │
│     Server      Content!         Interactive      Fully             │
│     (fast)      (visible)         Loading        Interactive        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

**Benefits:**
1. **Better SEO** - Search engines see full content
2. **Faster First Contentful Paint (FCP)** - Content visible immediately
3. **Better for slow devices** - Less client-side work
4. **Social media previews** - Meta tags rendered

---

## Setting Up Angular SSR

### Installation

```bash
# Add SSR to existing project
ng add @angular/ssr

# Or create new project with SSR
ng new my-app --ssr
```

### Generated Structure

```
src/
  app/
    app.config.ts
    app.config.server.ts  # Server-specific config
    app.routes.ts
  main.ts
  main.server.ts          # Server entry point
server.ts                 # Express server
```

### Configuration Files

```typescript
// app.config.ts (Browser)
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideClientHydration } from '@angular/platform-browser';
import { provideHttpClient, withFetch } from '@angular/common/http';

import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideClientHydration(),  // Enable hydration
    provideHttpClient(withFetch())
  ]
};

// app.config.server.ts (Server)
import { mergeApplicationConfig, ApplicationConfig } from '@angular/core';
import { provideServerRendering } from '@angular/platform-server';
import { appConfig } from './app.config';

const serverConfig: ApplicationConfig = {
  providers: [
    provideServerRendering()
  ]
};

export const config = mergeApplicationConfig(appConfig, serverConfig);
```

### Server Setup

```typescript
// server.ts
import 'zone.js/node';
import { APP_BASE_HREF } from '@angular/common';
import { CommonEngine } from '@angular/ssr';
import express from 'express';
import { fileURLToPath } from 'node:url';
import { dirname, join, resolve } from 'node:path';
import bootstrap from './src/main.server';

export function app(): express.Express {
  const server = express();
  const serverDistFolder = dirname(fileURLToPath(import.meta.url));
  const browserDistFolder = resolve(serverDistFolder, '../browser');
  const indexHtml = join(serverDistFolder, 'index.server.html');

  const commonEngine = new CommonEngine();

  server.set('view engine', 'html');
  server.set('views', browserDistFolder);

  // Serve static files
  server.get('*.*', express.static(browserDistFolder, {
    maxAge: '1y'
  }));

  // All regular routes use the Angular engine
  server.get('*', (req, res, next) => {
    const { protocol, originalUrl, baseUrl, headers } = req;

    commonEngine
      .render({
        bootstrap,
        documentFilePath: indexHtml,
        url: `${protocol}://${headers.host}${originalUrl}`,
        publicPath: browserDistFolder,
        providers: [{ provide: APP_BASE_HREF, useValue: baseUrl }],
      })
      .then((html) => res.send(html))
      .catch((err) => next(err));
  });

  return server;
}

function run(): void {
  const port = process.env['PORT'] || 4000;
  const server = app();
  server.listen(port, () => {
    console.log(`Node Express server listening on http://localhost:${port}`);
  });
}

run();
```

---

## Hydration

Hydration is the process of making server-rendered HTML interactive by attaching event listeners and Angular's change detection.

### Full Hydration

```typescript
// Enable full hydration (default)
import { provideClientHydration } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration()
  ]
};
```

### Incremental Hydration (Angular 17+)

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
    <!-- Hydrate on interaction -->
    @defer (hydrate on interaction) {
      <app-comments [postId]="postId" />
    }

    <!-- Hydrate on viewport -->
    @defer (hydrate on viewport) {
      <app-related-posts />
    }

    <!-- Hydrate on idle -->
    @defer (hydrate on idle) {
      <app-footer />
    }

    <!-- Hydrate on timer -->
    @defer (hydrate on timer(5s)) {
      <app-sidebar />
    }
  `
})
```

### Event Replay

```typescript
// Enable event replay for events during hydration
import { provideClientHydration, withEventReplay } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration(withEventReplay())
  ]
};

// Events clicked before hydration completes are replayed after
```

---

## Platform Detection

```typescript
import { isPlatformBrowser, isPlatformServer, PLATFORM_ID } from '@angular/common';

@Component({...})
export class MyComponent implements OnInit {
  private platformId = inject(PLATFORM_ID);

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      // Browser-only code
      this.initBrowserFeatures();
    }

    if (isPlatformServer(this.platformId)) {
      // Server-only code
      this.loadServerData();
    }
  }

  private initBrowserFeatures() {
    // Access window, document, localStorage
    localStorage.setItem('visited', 'true');
    
    // Initialize browser-only libraries
    this.initAnalytics();
  }
}
```

### afterNextRender & afterRender

```typescript
import { afterNextRender, afterRender } from '@angular/core';

@Component({...})
export class ChartComponent {
  private chartContainer = viewChild<ElementRef>('chart');

  constructor() {
    // Runs once after first render (browser only)
    afterNextRender(() => {
      this.initChart();
    });

    // Runs after every render (browser only)
    afterRender(() => {
      this.updateChart();
    });
  }

  private initChart() {
    // Safe to use DOM APIs here
    const ctx = this.chartContainer().nativeElement;
    new Chart(ctx, this.chartConfig);
  }
}
```

---

## State Transfer

Transfer state from server to client to avoid duplicate API calls.

```typescript
// Enable HTTP transfer cache
import { provideClientHydration, withHttpTransferCacheOptions } from '@angular/platform-browser';

export const appConfig: ApplicationConfig = {
  providers: [
    provideClientHydration(
      withHttpTransferCacheOptions({
        includeHeaders: ['X-Custom-Header'],
        includePostRequests: true
      })
    ),
    provideHttpClient(withFetch())
  ]
};

// Usage - HTTP requests are automatically cached
@Component({...})
export class ProductComponent {
  private http = inject(HttpClient);
  
  product$ = this.http.get<Product>('/api/products/1');
  // Request made on server, response transferred to client
  // Client reuses transferred response instead of making new request
}
```

### Manual State Transfer

```typescript
import { makeStateKey, TransferState } from '@angular/core';

const USER_KEY = makeStateKey<User>('user');

@Injectable({ providedIn: 'root' })
export class UserService {
  private http = inject(HttpClient);
  private transferState = inject(TransferState);
  private platformId = inject(PLATFORM_ID);

  getUser(id: string): Observable<User> {
    // Check if state was transferred from server
    const cachedUser = this.transferState.get(USER_KEY, null);
    
    if (cachedUser) {
      this.transferState.remove(USER_KEY);
      return of(cachedUser);
    }

    return this.http.get<User>(`/api/users/${id}`).pipe(
      tap(user => {
        if (isPlatformServer(this.platformId)) {
          // Store for transfer to client
          this.transferState.set(USER_KEY, user);
        }
      })
    );
  }
}
```

---

## SEO with SSR

### Meta Tags Service

```typescript
import { Meta, Title } from '@angular/platform-browser';

@Injectable({ providedIn: 'root' })
export class SeoService {
  private meta = inject(Meta);
  private title = inject(Title);

  updatePageMeta(config: PageSeoConfig) {
    // Title
    this.title.setTitle(config.title);

    // Meta tags
    this.meta.updateTag({ name: 'description', content: config.description });
    this.meta.updateTag({ name: 'keywords', content: config.keywords?.join(', ') });

    // Open Graph
    this.meta.updateTag({ property: 'og:title', content: config.title });
    this.meta.updateTag({ property: 'og:description', content: config.description });
    this.meta.updateTag({ property: 'og:image', content: config.image });
    this.meta.updateTag({ property: 'og:url', content: config.url });
    this.meta.updateTag({ property: 'og:type', content: 'website' });

    // Twitter
    this.meta.updateTag({ name: 'twitter:card', content: 'summary_large_image' });
    this.meta.updateTag({ name: 'twitter:title', content: config.title });
    this.meta.updateTag({ name: 'twitter:description', content: config.description });
    this.meta.updateTag({ name: 'twitter:image', content: config.image });

    // Canonical URL
    this.setCanonicalUrl(config.url);
  }

  private setCanonicalUrl(url: string) {
    const link: HTMLLinkElement = document.querySelector('link[rel="canonical"]') 
      || document.createElement('link');
    link.setAttribute('rel', 'canonical');
    link.setAttribute('href', url);
    document.head.appendChild(link);
  }
}

// Usage in component
@Component({...})
export class ProductDetailComponent implements OnInit {
  private seo = inject(SeoService);
  private route = inject(ActivatedRoute);

  product = toSignal(
    this.route.data.pipe(
      map(data => data['product'] as Product)
    )
  );

  ngOnInit() {
    const product = this.product();
    if (product) {
      this.seo.updatePageMeta({
        title: `${product.name} | My Store`,
        description: product.description,
        image: product.imageUrl,
        url: `https://mystore.com/products/${product.id}`
      });
    }
  }
}
```

### Route Data for SEO

```typescript
// Routes with SEO data
export const routes: Routes = [
  {
    path: 'products/:id',
    component: ProductDetailComponent,
    resolve: { product: productResolver },
    data: {
      seo: {
        titleTemplate: '${product.name} | My Store'
      }
    }
  }
];

// Global SEO handler
@Injectable({ providedIn: 'root' })
export class GlobalSeoService {
  private router = inject(Router);
  private seo = inject(SeoService);

  init() {
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd),
      map(() => this.router.routerState.root),
      map(route => {
        while (route.firstChild) route = route.firstChild;
        return route;
      }),
      filter(route => route.outlet === 'primary')
    ).subscribe(route => {
      const data = route.snapshot.data;
      if (data['seo']) {
        this.seo.updatePageMeta(data['seo']);
      }
    });
  }
}
```

---

## Prerendering (Static Site Generation)

```typescript
// angular.json
{
  "projects": {
    "my-app": {
      "architect": {
        "prerender": {
          "builder": "@angular/build:prerender",
          "options": {
            "routes": [
              "/",
              "/about",
              "/products",
              "/products/1",
              "/products/2"
            ]
          }
        }
      }
    }
  }
}
```

### Dynamic Route Discovery

```typescript
// prerender-routes.ts
import { PrerenderRoute } from '@angular/prerender';

export async function getRoutes(): Promise<PrerenderRoute[]> {
  // Fetch dynamic routes
  const products = await fetch('https://api.example.com/products')
    .then(r => r.json());

  return [
    { route: '/' },
    { route: '/about' },
    ...products.map(p => ({ route: `/products/${p.id}` }))
  ];
}
```

---

## Common SSR Issues & Solutions

### 1. Browser API Access

```typescript
// ❌ Problem: Accessing window on server
@Component({...})
export class BadComponent {
  width = window.innerWidth;  // Error: window is not defined
}

// ✅ Solution: Platform check
@Component({...})
export class GoodComponent {
  private platformId = inject(PLATFORM_ID);
  width = 0;

  ngOnInit() {
    if (isPlatformBrowser(this.platformId)) {
      this.width = window.innerWidth;
    }
  }
}

// ✅ Better: afterNextRender
@Component({...})
export class BetterComponent {
  width = signal(0);

  constructor() {
    afterNextRender(() => {
      this.width.set(window.innerWidth);
    });
  }
}
```

### 2. Third-party Libraries

```typescript
// Some libraries aren't SSR-compatible
// Use dynamic imports with platform check

@Component({...})
export class ChartComponent {
  chart: any;

  constructor() {
    afterNextRender(async () => {
      const { Chart } = await import('chart.js');
      this.chart = new Chart(/* ... */);
    });
  }
}
```

### 3. Long-running Operations

```typescript
// ❌ Problem: Subscription never completes on server
@Component({...})
export class BadComponent {
  data$ = interval(1000).pipe(
    map(() => new Date())
  );
}

// ✅ Solution: Complete on server
@Component({...})
export class GoodComponent {
  private platformId = inject(PLATFORM_ID);
  
  data$ = isPlatformServer(this.platformId)
    ? of(new Date())  // Single value on server
    : interval(1000).pipe(map(() => new Date()));
}
```

---

## Build & Deployment

```bash
# Build SSR application
ng build

# Output structure
dist/
  my-app/
    browser/    # Client-side assets
    server/     # Server bundle

# Run SSR server
node dist/my-app/server/server.mjs

# Or use production server (PM2)
pm2 start dist/my-app/server/server.mjs
```

---

## Summary

| Feature | Description |
|---------|-------------|
| SSR | Renders on server, sends HTML |
| Hydration | Makes server HTML interactive |
| Incremental Hydration | Deferred component hydration |
| Event Replay | Replays events during hydration |
| Transfer State | Passes server data to client |
| Prerendering | Static HTML at build time |
| Platform Detection | `isPlatformBrowser/Server` |
| afterNextRender | Browser-only lifecycle hook |
