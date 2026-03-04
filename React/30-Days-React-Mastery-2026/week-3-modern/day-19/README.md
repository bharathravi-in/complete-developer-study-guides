# 📅 Day 19 – Next.js

## 🎯 Learning Goals
- Master Next.js App Router
- Understand routing and layouts
- Learn Server Actions
- Implement data fetching patterns

---

## 📚 Theory

### App Router Fundamentals

```tsx
// Next.js 14+ App Router structure
// 
// app/
// ├── layout.tsx        // Root layout
// ├── page.tsx          // Home page (/)
// ├── loading.tsx       // Loading UI
// ├── error.tsx         // Error UI
// ├── not-found.tsx     // 404 page
// ├── globals.css       // Global styles
// │
// ├── dashboard/
// │   ├── layout.tsx    // Dashboard layout
// │   ├── page.tsx      // /dashboard
// │   ├── loading.tsx   // Dashboard loading
// │   └── settings/
// │       └── page.tsx  // /dashboard/settings
// │
// ├── blog/
// │   ├── page.tsx      // /blog
// │   └── [slug]/
// │       └── page.tsx  // /blog/:slug (dynamic)
// │
// └── (marketing)/      // Route group (no URL impact)
//     ├── about/
//     │   └── page.tsx  // /about
//     └── contact/
//         └── page.tsx  // /contact

// app/layout.tsx (Root Layout - Required)
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'My App',
  description: 'Built with Next.js',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Header />
        <main>{children}</main>
        <Footer />
      </body>
    </html>
  );
}

// app/page.tsx (Home Page)
export default function HomePage() {
  return <h1>Welcome Home</h1>;
}
```

### Dynamic Routes

```tsx
// app/blog/[slug]/page.tsx
interface BlogPostParams {
  params: { slug: string };
  searchParams: { [key: string]: string | string[] | undefined };
}

export async function generateMetadata({ params }: BlogPostParams) {
  const post = await getPost(params.slug);
  return {
    title: post.title,
    description: post.excerpt,
  };
}

export default async function BlogPost({ params, searchParams }: BlogPostParams) {
  const post = await getPost(params.slug);
  
  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  );
}

// Static generation at build time
export async function generateStaticParams() {
  const posts = await getAllPosts();
  return posts.map((post) => ({
    slug: post.slug,
  }));
}

// app/shop/[...categories]/page.tsx (Catch-all)
// Matches: /shop/a, /shop/a/b, /shop/a/b/c
interface CatchAllParams {
  params: { categories: string[] };
}

export default function ShopCategory({ params }: CatchAllParams) {
  // /shop/clothes/men/shirts -> categories = ['clothes', 'men', 'shirts']
  return <div>Categories: {params.categories.join(' > ')}</div>;
}

// app/shop/[[...categories]]/page.tsx (Optional catch-all)
// Also matches: /shop (categories = undefined)
```

### Layouts and Templates

```tsx
// app/dashboard/layout.tsx
// Layouts persist across navigation (state preserved)
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="dashboard">
      <Sidebar />
      <main>{children}</main>
    </div>
  );
}

// app/dashboard/template.tsx
// Templates re-mount on navigation (state reset)
export default function DashboardTemplate({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div>
      {/* Re-mounts on each navigation */}
      {children}
    </div>
  );
}

// Parallel routes - Simultaneously render multiple pages
// app/dashboard/@analytics/page.tsx
// app/dashboard/@team/page.tsx
// app/dashboard/layout.tsx
export default function Layout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode;
  analytics: React.ReactNode;
  team: React.ReactNode;
}) {
  return (
    <div>
      {children}
      <div className="grid">
        {analytics}
        {team}
      </div>
    </div>
  );
}

// Intercepting routes - Modal pattern
// app/feed/@modal/(.)photo/[id]/page.tsx
// (.) - same level
// (..) - one level up
// (...) - root level
```

### Loading and Error Handling

```tsx
// app/dashboard/loading.tsx
// Automatic Suspense boundary
export default function Loading() {
  return (
    <div className="loading">
      <Spinner />
      <p>Loading dashboard...</p>
    </div>
  );
}

// app/dashboard/error.tsx
'use client'; // Error components must be Client Components

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="error">
      <h2>Something went wrong!</h2>
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}

// app/not-found.tsx
export default function NotFound() {
  return (
    <div>
      <h2>404 - Page Not Found</h2>
      <Link href="/">Go Home</Link>
    </div>
  );
}

// Trigger not-found programmatically
import { notFound } from 'next/navigation';

async function getPost(slug: string) {
  const post = await db.post.findUnique({ where: { slug } });
  if (!post) notFound();
  return post;
}
```

### Server Actions

```tsx
// app/actions.ts
'use server';

import { revalidatePath, revalidateTag } from 'next/cache';
import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';
import { z } from 'zod';

const createPostSchema = z.object({
  title: z.string().min(1).max(100),
  content: z.string().min(1),
});

export async function createPost(formData: FormData) {
  // Validate
  const validated = createPostSchema.safeParse({
    title: formData.get('title'),
    content: formData.get('content'),
  });

  if (!validated.success) {
    return { error: validated.error.flatten() };
  }

  // Create
  const post = await db.post.create({
    data: validated.data,
  });

  // Revalidate and redirect
  revalidatePath('/posts');
  redirect(`/posts/${post.slug}`);
}

export async function deletePost(id: string) {
  await db.post.delete({ where: { id } });
  revalidatePath('/posts');
}

export async function updateTheme(theme: 'light' | 'dark') {
  cookies().set('theme', theme);
}

// app/posts/new/page.tsx
import { createPost } from '../actions';

export default function NewPostPage() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" required />
      <textarea name="content" placeholder="Content" required />
      <SubmitButton />
    </form>
  );
}

// components/SubmitButton.tsx
'use client';

import { useFormStatus } from 'react-dom';

export function SubmitButton() {
  const { pending } = useFormStatus();
  
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Creating...' : 'Create Post'}
    </button>
  );
}
```

### Data Fetching Patterns

```tsx
// Caching and revalidation options
async function getData() {
  // Default: cached forever (static)
  const staticData = await fetch('https://api.example.com/data');
  
  // No caching (dynamic)
  const dynamicData = await fetch('https://api.example.com/data', {
    cache: 'no-store',
  });
  
  // Time-based revalidation
  const revalidatedData = await fetch('https://api.example.com/data', {
    next: { revalidate: 3600 }, // Revalidate every hour
  });
  
  // Tag-based revalidation
  const taggedData = await fetch('https://api.example.com/data', {
    next: { tags: ['posts'] },
  });
  
  return { staticData, dynamicData, revalidatedData, taggedData };
}

// Route segment config
export const dynamic = 'force-dynamic'; // Always dynamic
export const revalidate = 60; // Page-level revalidation

// Parallel data fetching
async function DashboardPage() {
  // Fetch in parallel
  const [user, posts, analytics] = await Promise.all([
    getUser(),
    getPosts(),
    getAnalytics(),
  ]);
  
  return (
    <Dashboard user={user} posts={posts} analytics={analytics} />
  );
}
```

---

## ✅ Task: Build Full Next.js App

```
app/
├── layout.tsx
├── page.tsx
├── loading.tsx
├── error.tsx
├── not-found.tsx
├── actions.ts
│
├── auth/
│   ├── login/page.tsx
│   └── register/page.tsx
│
├── dashboard/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── loading.tsx
│   └── settings/page.tsx
│
├── posts/
│   ├── page.tsx
│   ├── new/page.tsx
│   └── [slug]/
│       ├── page.tsx
│       └── edit/page.tsx
│
└── api/
    └── posts/route.ts
```

---

## 🎯 Interview Questions & Answers

### Q1: Layout vs Template?
**Answer:** Layout persists across navigations (state preserved, no re-mount). Template re-mounts on every navigation (state reset). Use layouts for persistent UI (nav, sidebar), templates when you need fresh state.

### Q2: What is ISR (Incremental Static Regeneration)?
**Answer:** Pages are statically generated at build time but can be revalidated after deployment. Use `revalidate` option to specify seconds. Combines static performance with dynamic freshness.

### Q3: Server Actions vs API Routes?
**Answer:** Server Actions are colocated functions called directly from components (forms). API Routes are traditional REST endpoints. Server Actions: simpler, type-safe, progressive enhancement. API Routes: when you need REST API or webhooks.

---

## ✅ Completion Checklist

- [ ] Understand App Router structure
- [ ] Can create dynamic routes
- [ ] Know layouts and templates
- [ ] Implement Server Actions
- [ ] Built full Next.js app

---

**Previous:** [Day 18 - React Server Components](../day-18/README.md)  
**Next:** [Day 20 - Authentication](../day-20/README.md)
