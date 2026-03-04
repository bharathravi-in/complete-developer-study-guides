# 📅 Day 20 – Authentication & Security

## 🎯 Learning Goals
- Implement JWT authentication
- Learn NextAuth.js (Auth.js)
- Understand OAuth flows
- Apply security best practices

---

## 📚 Theory

### JWT Authentication

```tsx
// JWT (JSON Web Token) Flow:
// 1. User logs in with credentials
// 2. Server validates and returns JWT
// 3. Client stores JWT (httpOnly cookie preferred)
// 4. Client sends JWT with each request
// 5. Server validates JWT on protected routes

// utils/jwt.ts
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET!;
const JWT_EXPIRES_IN = '15m';
const REFRESH_TOKEN_EXPIRES_IN = '7d';

interface TokenPayload {
  userId: string;
  email: string;
  role: string;
}

export function generateAccessToken(payload: TokenPayload): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
}

export function generateRefreshToken(userId: string): string {
  return jwt.sign({ userId }, JWT_SECRET, { expiresIn: REFRESH_TOKEN_EXPIRES_IN });
}

export function verifyToken(token: string): TokenPayload {
  return jwt.verify(token, JWT_SECRET) as TokenPayload;
}

// API route - Login
// app/api/auth/login/route.ts
import { cookies } from 'next/headers';
import bcrypt from 'bcryptjs';

export async function POST(request: Request) {
  const { email, password } = await request.json();
  
  // Find user
  const user = await prisma.user.findUnique({ where: { email } });
  if (!user) {
    return Response.json({ error: 'Invalid credentials' }, { status: 401 });
  }
  
  // Verify password
  const isValid = await bcrypt.compare(password, user.passwordHash);
  if (!isValid) {
    return Response.json({ error: 'Invalid credentials' }, { status: 401 });
  }
  
  // Generate tokens
  const accessToken = generateAccessToken({
    userId: user.id,
    email: user.email,
    role: user.role,
  });
  const refreshToken = generateRefreshToken(user.id);
  
  // Store refresh token in DB
  await prisma.refreshToken.create({
    data: { token: refreshToken, userId: user.id },
  });
  
  // Set httpOnly cookie
  cookies().set('accessToken', accessToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 15 * 60, // 15 minutes
  });
  
  cookies().set('refreshToken', refreshToken, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    path: '/api/auth/refresh',
    maxAge: 7 * 24 * 60 * 60, // 7 days
  });
  
  return Response.json({ user: { id: user.id, email: user.email } });
}
```

### NextAuth.js (Auth.js)

```tsx
// Auth.js v5 (NextAuth.js)
// app/api/auth/[...nextauth]/route.ts

import NextAuth from 'next-auth';
import Google from 'next-auth/providers/google';
import GitHub from 'next-auth/providers/github';
import Credentials from 'next-auth/providers/credentials';
import { PrismaAdapter } from '@auth/prisma-adapter';
import bcrypt from 'bcryptjs';

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHub({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    }),
    Credentials({
      credentials: {
        email: { label: 'Email', type: 'email' },
        password: { label: 'Password', type: 'password' },
      },
      async authorize(credentials) {
        const user = await prisma.user.findUnique({
          where: { email: credentials.email as string },
        });
        
        if (!user || !user.passwordHash) return null;
        
        const isValid = await bcrypt.compare(
          credentials.password as string,
          user.passwordHash
        );
        
        if (!isValid) return null;
        
        return { id: user.id, email: user.email, name: user.name };
      },
    }),
  ],
  session: {
    strategy: 'jwt',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.role = user.role;
      }
      return token;
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string;
        session.user.role = token.role as string;
      }
      return session;
    },
  },
  pages: {
    signIn: '/auth/login',
    error: '/auth/error',
  },
});

export const { GET, POST } = handlers;

// middleware.ts - Protect routes
import { auth } from './auth';

export default auth((req) => {
  const isLoggedIn = !!req.auth;
  const isProtected = req.nextUrl.pathname.startsWith('/dashboard');
  
  if (isProtected && !isLoggedIn) {
    return Response.redirect(new URL('/auth/login', req.nextUrl));
  }
});

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

### Protected Components

```tsx
// Using auth in Server Components
// app/dashboard/page.tsx
import { auth } from '@/auth';
import { redirect } from 'next/navigation';

export default async function DashboardPage() {
  const session = await auth();
  
  if (!session) {
    redirect('/auth/login');
  }
  
  return (
    <div>
      <h1>Welcome, {session.user?.name}</h1>
    </div>
  );
}

// Client-side auth hook
// hooks/useSession.ts
'use client';

import { useSession, signIn, signOut } from 'next-auth/react';

export function AuthButton() {
  const { data: session, status } = useSession();
  
  if (status === 'loading') {
    return <div>Loading...</div>;
  }
  
  if (session) {
    return (
      <div>
        <span>Signed in as {session.user?.email}</span>
        <button onClick={() => signOut()}>Sign out</button>
      </div>
    );
  }
  
  return (
    <div>
      <button onClick={() => signIn('google')}>Sign in with Google</button>
      <button onClick={() => signIn('github')}>Sign in with GitHub</button>
    </div>
  );
}

// Wrap app with SessionProvider
// app/providers.tsx
'use client';

import { SessionProvider } from 'next-auth/react';

export function Providers({ children }: { children: React.ReactNode }) {
  return <SessionProvider>{children}</SessionProvider>;
}
```

### Security Best Practices

```tsx
// 1. CSRF Protection
// NextAuth handles CSRF automatically
// For custom forms, use tokens

// 2. XSS Prevention
// React escapes by default
// Avoid dangerouslySetInnerHTML
// Use DOMPurify for user content
import DOMPurify from 'dompurify';

function SafeHTML({ html }: { html: string }) {
  const clean = DOMPurify.sanitize(html);
  return <div dangerouslySetInnerHTML={{ __html: clean }} />;
}

// 3. Content Security Policy
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: `
      default-src 'self';
      script-src 'self' 'unsafe-eval' 'unsafe-inline';
      style-src 'self' 'unsafe-inline';
      img-src 'self' data: https:;
    `.replace(/\n/g, ''),
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY',
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff',
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin',
  },
];

// 4. Rate Limiting
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';

const ratelimit = new Ratelimit({
  redis: Redis.fromEnv(),
  limiter: Ratelimit.slidingWindow(10, '10 s'),
});

export async function middleware(request: Request) {
  const ip = request.headers.get('x-forwarded-for') ?? '127.0.0.1';
  const { success, remaining } = await ratelimit.limit(ip);
  
  if (!success) {
    return new Response('Too many requests', { status: 429 });
  }
}

// 5. Input Validation
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

// Always validate on server
export async function login(data: unknown) {
  const validated = loginSchema.safeParse(data);
  if (!validated.success) {
    throw new Error('Invalid input');
  }
  // Proceed with validated.data
}

// 6. Secure Cookie Settings
cookies().set('token', token, {
  httpOnly: true,      // Not accessible via JS
  secure: true,        // HTTPS only
  sameSite: 'strict',  // CSRF protection
  path: '/',
  maxAge: 60 * 60,     // 1 hour
});
```

### Role-Based Access Control

```tsx
// types/next-auth.d.ts
import { DefaultSession } from 'next-auth';

declare module 'next-auth' {
  interface Session {
    user: {
      id: string;
      role: 'admin' | 'user' | 'moderator';
    } & DefaultSession['user'];
  }
}

// Middleware for role checking
export function withRole(roles: string[]) {
  return async function middleware(req: Request) {
    const session = await auth();
    
    if (!session?.user?.role || !roles.includes(session.user.role)) {
      return Response.json({ error: 'Forbidden' }, { status: 403 });
    }
  };
}

// Protected admin route
// app/admin/page.tsx
import { auth } from '@/auth';
import { redirect } from 'next/navigation';

export default async function AdminPage() {
  const session = await auth();
  
  if (!session || session.user.role !== 'admin') {
    redirect('/unauthorized');
  }
  
  return <AdminDashboard />;
}

// Component-level protection
function AdminOnly({ children }: { children: React.ReactNode }) {
  const { data: session } = useSession();
  
  if (session?.user?.role !== 'admin') {
    return null;
  }
  
  return <>{children}</>;
}
```

---

## ✅ Task: Complete Auth System

Build authentication with:
- Login/Register forms
- OAuth (Google/GitHub)
- Protected routes
- Role-based access
- Session management

---

## 🎯 Interview Questions & Answers

### Q1: JWT vs Session-based auth?
**Answer:** JWT: stateless, scalable, useful for microservices. Session: server-stored, easier to invalidate, better for traditional apps. Modern approach: JWT in httpOnly cookies with refresh tokens.

### Q2: How do you prevent XSS in React?
**Answer:** React escapes JSX by default. Avoid `dangerouslySetInnerHTML`. If needed, sanitize with DOMPurify. Use CSP headers. Store tokens in httpOnly cookies, not localStorage.

### Q3: What is CSRF and how to prevent it?
**Answer:** Cross-Site Request Forgery - attacker tricks user into making unintended requests. Prevention: CSRF tokens, SameSite cookies, verify Origin header. NextAuth handles this automatically.

---

## ✅ Completion Checklist

- [ ] Understand JWT flow
- [ ] Implement NextAuth.js
- [ ] Know OAuth integration
- [ ] Apply security best practices
- [ ] Built complete auth system

---

**Previous:** [Day 19 - Next.js](../day-19/README.md)  
**Next:** [Day 21 - Micro Frontend](../day-21/README.md)
