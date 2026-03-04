# 📅 Day 18 – React Server Components

## 🎯 Learning Goals
- Understand Server vs Client Components
- Learn RSC mental model
- Master data fetching patterns
- Know when to use each type

---

## 📚 Theory

### Server Components Fundamentals

```tsx
// React Server Components (RSC) - Run ONLY on the server

// 🎯 Key Concepts:
// - Default in Next.js App Router (no 'use client')
// - Zero JavaScript sent to client
// - Direct database/file access
// - Can't use hooks (useState, useEffect)
// - Can't use browser APIs

// Server Component (default)
// app/users/page.tsx
async function UsersPage() {
  // Direct database access - runs on server
  const users = await db.user.findMany();
  
  // Or fetch from API
  const res = await fetch('https://api.example.com/users', {
    cache: 'force-cache', // Default caching
  });
  const apiUsers = await res.json();

  return (
    <div>
      <h1>Users</h1>
      <UserList users={users} />
    </div>
  );
}

export default UsersPage;

// Client Component (opt-in)
// components/Counter.tsx
'use client'; // This directive makes it a Client Component

import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  
  return (
    <button onClick={() => setCount(c => c + 1)}>
      Count: {count}
    </button>
  );
}
```

### Server vs Client Components

```tsx
// ✅ Server Components - Use when:
// - Fetching data
// - Accessing backend resources
// - Large dependencies (stay on server)
// - Sensitive data (API keys, tokens)
// - SEO-critical content

// ✅ Client Components - Use when:
// - Interactivity (onClick, onChange)
// - State management (useState)
// - Effects (useEffect)
// - Browser APIs (window, localStorage)
// - Custom hooks

// Component tree example:
// 
// ServerComponent (page.tsx)
// ├── ServerComponent (Header)
// │   └── ClientComponent (SearchBar) 'use client'
// ├── ServerComponent (ProductList)
// │   └── ClientComponent (AddToCart) 'use client'
// └── ServerComponent (Footer)
```

### Data Fetching Patterns

```tsx
// Pattern 1: Sequential fetching
async function Page({ params }: { params: { id: string } }) {
  const user = await fetchUser(params.id);
  const posts = await fetchUserPosts(user.id); // Waits for user
  
  return <Profile user={user} posts={posts} />;
}

// Pattern 2: Parallel fetching (better!)
async function Page({ params }: { params: { id: string } }) {
  // Fetch in parallel
  const [user, posts] = await Promise.all([
    fetchUser(params.id),
    fetchUserPosts(params.id),
  ]);
  
  return <Profile user={user} posts={posts} />;
}

// Pattern 3: Streaming with Suspense
import { Suspense } from 'react';

async function Page({ params }: { params: { id: string } }) {
  const user = await fetchUser(params.id);
  
  return (
    <div>
      <UserInfo user={user} />
      
      {/* Stream in posts later */}
      <Suspense fallback={<PostsSkeleton />}>
        <UserPosts userId={params.id} />
      </Suspense>
    </div>
  );
}

// UserPosts is a separate async Server Component
async function UserPosts({ userId }: { userId: string }) {
  const posts = await fetchUserPosts(userId);
  return <PostList posts={posts} />;
}

// Pattern 4: Caching strategies
async function getUser(id: string) {
  const res = await fetch(`/api/users/${id}`, {
    cache: 'force-cache',     // Cache indefinitely (default)
    // cache: 'no-store',     // Never cache
    // next: { revalidate: 60 }, // Revalidate every 60s
    // next: { tags: ['user'] }, // Tag-based revalidation
  });
  return res.json();
}
```

### Composition Patterns

```tsx
// ❌ Wrong: Can't import Server into Client
'use client';
import ServerComponent from './ServerComponent'; // Error!

// ✅ Correct: Pass Server as children/props
// ServerWrapper.tsx (Server Component)
import ClientComponent from './ClientComponent';
import ServerChild from './ServerChild';

function ServerWrapper() {
  return (
    <ClientComponent>
      <ServerChild /> {/* Passed as children */}
    </ClientComponent>
  );
}

// ClientComponent.tsx
'use client';

function ClientComponent({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  
  return (
    <div>
      <button onClick={() => setIsOpen(!isOpen)}>Toggle</button>
      {isOpen && children} {/* Render server component */}
    </div>
  );
}

// ✅ Pattern: Server Component with Client interactivity
// ProductPage.tsx (Server)
async function ProductPage({ id }: { id: string }) {
  const product = await fetchProduct(id); // Server-side fetch
  
  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <ProductPrice price={product.price} /> {/* Server rendered */}
      <AddToCartButton productId={id} />      {/* Client interactive */}
    </div>
  );
}

// AddToCartButton.tsx (Client)
'use client';

function AddToCartButton({ productId }: { productId: string }) {
  const [isAdding, setIsAdding] = useState(false);
  
  const handleAdd = async () => {
    setIsAdding(true);
    await addToCart(productId);
    setIsAdding(false);
  };
  
  return (
    <button onClick={handleAdd} disabled={isAdding}>
      {isAdding ? 'Adding...' : 'Add to Cart'}
    </button>
  );
}
```

### Server Actions

```tsx
// Server Actions - Functions that run on server, called from client

// app/actions.ts
'use server';

import { revalidatePath, revalidateTag } from 'next/cache';

export async function createPost(formData: FormData) {
  const title = formData.get('title') as string;
  const content = formData.get('content') as string;
  
  // Direct database access
  await db.post.create({ data: { title, content } });
  
  // Revalidate cache
  revalidatePath('/posts');
  // or revalidateTag('posts');
}

export async function deletePost(id: string) {
  await db.post.delete({ where: { id } });
  revalidatePath('/posts');
}

// Using in form (Progressive Enhancement)
function CreatePostForm() {
  return (
    <form action={createPost}>
      <input name="title" placeholder="Title" />
      <textarea name="content" placeholder="Content" />
      <button type="submit">Create</button>
    </form>
  );
}

// Using with client state
'use client';

import { createPost } from './actions';
import { useTransition } from 'react';

function CreatePostClient() {
  const [isPending, startTransition] = useTransition();
  
  const handleSubmit = (formData: FormData) => {
    startTransition(async () => {
      await createPost(formData);
    });
  };
  
  return (
    <form action={handleSubmit}>
      <input name="title" />
      <button disabled={isPending}>
        {isPending ? 'Creating...' : 'Create'}
      </button>
    </form>
  );
}

// Using useFormStatus for pending state
'use client';

import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending } = useFormStatus();
  
  return (
    <button disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  );
}
```

---

## ✅ Task: Build RSC-Based Dashboard

```tsx
// app/dashboard/page.tsx
import { Suspense } from 'react';
import { StatsCards, StatsSkeleton } from './stats';
import { RecentOrders, OrdersSkeleton } from './orders';
import { DashboardChart, ChartSkeleton } from './chart';

export default async function DashboardPage() {
  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      
      {/* Parallel streaming */}
      <div className="grid">
        <Suspense fallback={<StatsSkeleton />}>
          <StatsCards />
        </Suspense>
        
        <Suspense fallback={<ChartSkeleton />}>
          <DashboardChart />
        </Suspense>
        
        <Suspense fallback={<OrdersSkeleton />}>
          <RecentOrders />
        </Suspense>
      </div>
    </div>
  );
}

// app/dashboard/stats.tsx
async function StatsCards() {
  const stats = await fetchDashboardStats();
  
  return (
    <div className="stats-grid">
      {stats.map(stat => (
        <StatCard key={stat.id} {...stat} />
      ))}
    </div>
  );
}

// app/dashboard/orders.tsx
async function RecentOrders() {
  const orders = await fetchRecentOrders();
  
  return (
    <div className="orders">
      <h2>Recent Orders</h2>
      <OrdersTable orders={orders} />
      <RefreshButton /> {/* Client component for interactivity */}
    </div>
  );
}

// components/RefreshButton.tsx
'use client';

import { useRouter } from 'next/navigation';

export function RefreshButton() {
  const router = useRouter();
  
  return (
    <button onClick={() => router.refresh()}>
      Refresh Data
    </button>
  );
}
```

---

## 🎯 Interview Questions & Answers

### Q1: What are React Server Components?
**Answer:** Components that render ONLY on the server. Zero JS sent to client, direct backend access, can't use hooks/browser APIs. Default in Next.js App Router. Use 'use client' directive to opt into Client Components.

### Q2: When should you use Client Components?
**Answer:** When you need: interactivity (event handlers), React hooks (useState, useEffect), browser APIs (window, localStorage), or third-party libraries that use these features.

### Q3: How do you share data between Server and Client Components?
**Answer:** Pass data as props from Server to Client Components. Server Components can fetch data and pass it down. Can't import Server Components into Client Components directly - use children pattern instead.

---

## ✅ Completion Checklist

- [ ] Understand Server vs Client Components
- [ ] Know when to use each type
- [ ] Can implement streaming with Suspense
- [ ] Understand Server Actions
- [ ] Built RSC-based page

---

**Previous:** [Day 17 - API Layer](../day-17/README.md)  
**Next:** [Day 19 - Next.js](../day-19/README.md)
