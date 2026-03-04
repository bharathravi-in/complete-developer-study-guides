# 📅 Day 28 – System Design for Frontend

## 🎯 Learning Goals
- Design scalable frontend architectures
- Handle real-world system design questions
- Understand frontend infrastructure
- Learn design trade-offs

---

## 📚 Theory

### Frontend System Design Framework

```
📋 System Design Approach (RADIO):

R - Requirements
    - Functional: What features?
    - Non-functional: Performance, scale, reliability
    - Out of scope: What we won't cover

A - Architecture
    - High-level components
    - Data flow
    - API design

D - Data Model
    - State structure
    - API contracts
    - Caching strategy

I - Interface Definition
    - Component hierarchy
    - Props/state design
    - Event handling

O - Optimizations
    - Performance
    - Accessibility
    - SEO
```

### Example: Design a News Feed (like Twitter)

```tsx
// 1. REQUIREMENTS

// Functional:
// - Display feed of posts
// - Infinite scroll
// - Create/like/share posts
// - Real-time updates

// Non-functional:
// - Handle 10k+ posts
// - <100ms interaction response
// - Offline support
// - Mobile responsive

// 2. ARCHITECTURE

/*
┌─────────────────────────────────────────────────────────┐
│                    App Shell                             │
├───────────┬─────────────────────────────┬───────────────┤
│  Sidebar  │         Feed                │   Trending    │
│           │  ┌─────────────────────┐    │               │
│  - Home   │  │ Virtualized List    │    │  - Topics     │
│  - Explore│  │  ┌─────────────────┐│    │  - Users      │
│  - Profile│  │  │  Post Card      ││    │               │
│           │  │  │  - Media        ││    │               │
│           │  │  │  - Actions      ││    │               │
│           │  │  └─────────────────┘│    │               │
│           │  └─────────────────────┘    │               │
└───────────┴─────────────────────────────┴───────────────┘
                          │
                          ▼
          ┌───────────────────────────────┐
          │      State Management         │
          │  - Feed: TanStack Query       │
          │  - UI: Zustand                │
          │  - Cache: IndexedDB           │
          └───────────────────────────────┘
                          │
                          ▼
          ┌───────────────────────────────┐
          │         API Layer             │
          │  - REST: /api/feed            │
          │  - WebSocket: updates         │
          │  - GraphQL: flexible queries  │
          └───────────────────────────────┘
*/

// 3. DATA MODEL

interface Post {
  id: string;
  author: User;
  content: string;
  media?: Media[];
  createdAt: string;
  likes: number;
  shares: number;
  comments: number;
  isLiked: boolean;
}

interface FeedState {
  posts: Post[];
  cursor: string | null;
  hasMore: boolean;
}

// API Response
interface FeedResponse {
  posts: Post[];
  nextCursor: string | null;
}

// 4. COMPONENT DESIGN

// Feed container with infinite scroll
function Feed() {
  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useInfiniteQuery({
    queryKey: ['feed'],
    queryFn: ({ pageParam }) => fetchFeed(pageParam),
    getNextPageParam: (lastPage) => lastPage.nextCursor,
  });

  const posts = data?.pages.flatMap(page => page.posts) ?? [];

  return (
    <VirtualizedList
      items={posts}
      renderItem={(post) => <PostCard key={post.id} post={post} />}
      onEndReached={() => hasNextPage && fetchNextPage()}
      isLoading={isFetchingNextPage}
    />
  );
}

// 5. OPTIMIZATIONS

// Virtualization for performance
// Optimistic updates for likes
// Image lazy loading
// Service worker for offline
// WebSocket for real-time updates
```

### Design: Real-time Collaborative Editor (like Google Docs)

```tsx
// REQUIREMENTS
// - Multiple users edit simultaneously
// - See others' cursors
// - Conflict resolution
// - Offline support
// - Version history

// ARCHITECTURE

/*
Client A                 Server                    Client B
   │                       │                          │
   │◄─────── WebSocket ────┼─────── WebSocket ───────►│
   │                       │                          │
   │    ┌──────────────────┴───────────────────┐     │
   │    │           CRDT Engine                 │     │
   │    │  (Yjs / Automerge)                   │     │
   │    └──────────────────┬───────────────────┘     │
   │                       │                          │
   ▼                       ▼                          ▼
┌───────────┐        ┌───────────┐           ┌───────────┐
│  Editor   │        │ Document  │           │  Editor   │
│  State    │        │  Store    │           │  State    │
└───────────┘        └───────────┘           └───────────┘
*/

// Data Model - CRDT-based
import * as Y from 'yjs';
import { WebsocketProvider } from 'y-websocket';

function CollaborativeEditor({ documentId }: { documentId: string }) {
  const [doc] = useState(() => new Y.Doc());
  
  useEffect(() => {
    const provider = new WebsocketProvider(
      'wss://api.example.com/collab',
      documentId,
      doc
    );

    provider.on('status', ({ status }) => {
      console.log('Connection status:', status);
    });

    return () => provider.destroy();
  }, [doc, documentId]);

  // Yjs text type for editor
  const yText = doc.getText('content');

  return (
    <Editor
      yText={yText}
      awareness={provider.awareness}
    />
  );
}

// Cursor awareness
function useAwareness(provider: WebsocketProvider) {
  const [users, setUsers] = useState<Map<number, UserState>>(new Map());

  useEffect(() => {
    const awareness = provider.awareness;
    
    const updateUsers = () => {
      setUsers(new Map(awareness.getStates()));
    };

    awareness.on('change', updateUsers);
    return () => awareness.off('change', updateUsers);
  }, [provider]);

  const updateCursor = (position: { x: number; y: number }) => {
    provider.awareness.setLocalStateField('cursor', position);
  };

  return { users, updateCursor };
}
```

### Design: E-commerce Product Page

```tsx
// REQUIREMENTS
// - Fast initial load (LCP < 2.5s)
// - SEO optimized
// - Handle flash sales (high traffic)
// - A/B testing support
// - Analytics tracking

// SERVER COMPONENT ARCHITECTURE

// app/products/[slug]/page.tsx
export default async function ProductPage({ 
  params 
}: { 
  params: { slug: string } 
}) {
  const product = await getProduct(params.slug);

  return (
    <main>
      {/* Static, SEO-critical content */}
      <ProductHeader product={product} />
      
      {/* Server-rendered, cached */}
      <Suspense fallback={<PriceSkeleton />}>
        <ProductPrice productId={product.id} />
      </Suspense>

      {/* Client-side interactivity */}
      <AddToCartButton productId={product.id} />
      
      {/* Lazy-loaded below fold */}
      <Suspense fallback={<ReviewsSkeleton />}>
        <ProductReviews productId={product.id} />
      </Suspense>

      {/* Personalized recommendations */}
      <Suspense fallback={<RecommendationsSkeleton />}>
        <Recommendations productId={product.id} />
      </Suspense>
    </main>
  );
}

// Caching strategy
async function getProduct(slug: string) {
  return fetch(`/api/products/${slug}`, {
    next: { 
      revalidate: 60,  // Revalidate every minute
      tags: ['product', slug],
    },
  }).then(r => r.json());
}

// Price with real-time inventory
async function ProductPrice({ productId }: { productId: string }) {
  const { price, inventory, discount } = await fetch(
    `/api/products/${productId}/price`,
    { cache: 'no-store' }  // Always fresh
  ).then(r => r.json());

  return (
    <div className="price-section">
      {discount && <span className="original">${price}</span>}
      <span className="current">${discount || price}</span>
      <InventoryBadge count={inventory} />
    </div>
  );
}
```

### Performance Budgets and Monitoring

```tsx
// Performance budget
const performanceBudget = {
  // Core Web Vitals
  LCP: 2500,    // ms
  INP: 200,     // ms
  CLS: 0.1,
  
  // Bundle size
  mainBundle: 100 * 1024,  // 100KB
  totalJS: 300 * 1024,     // 300KB
  
  // Network
  apiLatency: 100,  // ms (P95)
  ttfb: 600,        // ms
};

// Monitoring setup
function setupMonitoring() {
  // Web Vitals
  onLCP(metric => reportMetric('LCP', metric.value));
  onINP(metric => reportMetric('INP', metric.value));
  onCLS(metric => reportMetric('CLS', metric.value));

  // Custom metrics
  performance.mark('app-interactive');
  
  // Error tracking
  window.onerror = (msg, url, line) => {
    reportError({ msg, url, line });
  };
}

// Real User Monitoring (RUM)
function reportMetric(name: string, value: number) {
  fetch('/api/metrics', {
    method: 'POST',
    body: JSON.stringify({
      metric: name,
      value,
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: Date.now(),
    }),
  });
}
```

---

## ✅ Task: Design Exercise

Design one of these systems:
1. **Messaging App** (WhatsApp-like)
2. **Video Streaming** (YouTube-like)
3. **Calendar App** (Google Calendar-like)
4. **Kanban Board** (Trello-like)

Cover: Requirements, Architecture, Data Model, Components, Optimizations

---

## 🎯 Interview Questions & Answers

### Q1: How would you design infinite scroll?
**Answer:** Use intersection observer for detection, cursor-based pagination from API, virtualization for large lists, prefetch next page, debounce scroll events, show loading skeleton.

### Q2: How do you handle real-time updates?
**Answer:** WebSocket for bi-directional, SSE for server-push only, polling as fallback. Implement reconnection logic, optimistic updates for UX, conflict resolution strategy (last-write-wins or CRDT).

### Q3: How would you optimize a slow dashboard?
**Answer:** Identify bottleneck (Network? Rendering?). Solutions: parallel data fetching, skeleton loading, virtualization, code splitting, caching, service worker, server components for static content.

---

## ✅ Completion Checklist

- [ ] Understand design framework
- [ ] Can design scalable frontends
- [ ] Know performance strategies
- [ ] Can analyze trade-offs
- [ ] Completed design exercise

---

**Previous:** [Day 27 - AI + React](../day-27/README.md)  
**Next:** [Day 29 - Interview Questions](../day-29/README.md)
