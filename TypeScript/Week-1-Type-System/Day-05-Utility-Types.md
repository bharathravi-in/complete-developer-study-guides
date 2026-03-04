# Day 5: Utility Types — Mastering TypeScript's Built-in Type Transformations

## Built-in Utility Types — Complete Reference

### Partial<T> — All Properties Optional

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  age: number;
}

// All properties become optional
type PartialUser = Partial<User>;
// { id?: string; name?: string; email?: string; age?: number; }

// Real-world: Update functions
function updateUser(id: string, updates: Partial<User>): User {
  const existing = getUserById(id);
  return { ...existing, ...updates };
}

updateUser('123', { name: 'Bharath' }); // ✅ Only update name
```

### Required<T> — All Properties Required

```typescript
interface Config {
  host?: string;
  port?: number;
  debug?: boolean;
}

type RequiredConfig = Required<Config>;
// { host: string; port: number; debug: boolean; }

// Real-world: Validated config after defaults applied
function createServer(config: Required<Config>) { /* ... */ }
```

### Readonly<T> and ReadonlyArray<T>

```typescript
interface State {
  users: User[];
  loading: boolean;
}

type ImmutableState = Readonly<State>;
// { readonly users: User[]; readonly loading: boolean; }

// Deep readonly (custom)
type DeepReadonly<T> = {
  readonly [K in keyof T]: T[K] extends object
    ? T[K] extends Function
      ? T[K]
      : DeepReadonly<T[K]>
    : T[K];
};
```

### Pick<T, K> — Select Properties

```typescript
type UserPreview = Pick<User, 'id' | 'name'>;
// { id: string; name: string; }

// Real-world: API response shaping
type PublicUser = Pick<User, 'name' | 'email'>;
type AuthToken = Pick<User, 'id' | 'email'>;
```

### Omit<T, K> — Remove Properties

```typescript
type CreateUserDTO = Omit<User, 'id'>;
// { name: string; email: string; age: number; }

// Chain with Partial for flexible types
type UpdateUserDTO = Partial<Omit<User, 'id'>>;
// { name?: string; email?: string; age?: number; }
```

### Record<K, V> — Key-Value Map

```typescript
type Role = 'admin' | 'user' | 'guest';

type RolePermissions = Record<Role, string[]>;
// { admin: string[]; user: string[]; guest: string[]; }

const permissions: RolePermissions = {
  admin: ['read', 'write', 'delete'],
  user: ['read', 'write'],
  guest: ['read'],
};

// Dynamic records
type ApiEndpoints = Record<string, {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
}>;
```

### Extract<T, U> and Exclude<T, U>

```typescript
type AllEvents = 'click' | 'scroll' | 'mousemove' | 'keydown' | 'keyup';

type MouseEvents = Extract<AllEvents, 'click' | 'scroll' | 'mousemove'>;
// 'click' | 'scroll' | 'mousemove'

type KeyboardEvents = Exclude<AllEvents, 'click' | 'scroll' | 'mousemove'>;
// 'keydown' | 'keyup'

// With complex types
type NonNullable<T> = Exclude<T, null | undefined>;
// Built-in: removes null and undefined from T
```

### ReturnType<T> and Parameters<T>

```typescript
function createUser(name: string, email: string): { id: string; name: string; email: string } {
  return { id: crypto.randomUUID(), name, email };
}

type UserResult = ReturnType<typeof createUser>;
// { id: string; name: string; email: string }

type CreateUserParams = Parameters<typeof createUser>;
// [name: string, email: string]

// Useful for wrapping functions
function withLogging<T extends (...args: any[]) => any>(
  fn: T
): (...args: Parameters<T>) => ReturnType<T> {
  return (...args) => {
    console.log('Calling with:', args);
    const result = fn(...args);
    console.log('Result:', result);
    return result;
  };
}
```

### Awaited<T> — Unwrap Promise Types

```typescript
type AsyncResult = Promise<Promise<string>>;
type Resolved = Awaited<AsyncResult>; // string

// Real-world: Get return type of async function
async function fetchUser(): Promise<User> { /* ... */ }
type FetchedUser = Awaited<ReturnType<typeof fetchUser>>; // User
```

## Implementing Utility Types from Scratch

### Understanding how they work internally:

```typescript
// Partial implementation
type MyPartial<T> = {
  [K in keyof T]?: T[K];
};

// Required implementation
type MyRequired<T> = {
  [K in keyof T]-?: T[K]; // -? removes optionality
};

// Readonly implementation
type MyReadonly<T> = {
  readonly [K in keyof T]: T[K];
};

// Pick implementation
type MyPick<T, K extends keyof T> = {
  [P in K]: T[P];
};

// Omit implementation
type MyOmit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;

// Record implementation
type MyRecord<K extends keyof any, V> = {
  [P in K]: V;
};

// Exclude implementation
type MyExclude<T, U> = T extends U ? never : T;

// Extract implementation
type MyExtract<T, U> = T extends U ? T : never;

// ReturnType implementation
type MyReturnType<T extends (...args: any) => any> = T extends (...args: any) => infer R ? R : never;

// Parameters implementation
type MyParameters<T extends (...args: any) => any> = T extends (...args: infer P) => any ? P : never;
```

## Combining Utility Types — Real Patterns

### Pattern 1: Safe API Layer

```typescript
interface User {
  id: string;
  name: string;
  email: string;
  password: string;
  createdAt: Date;
  updatedAt: Date;
}

// Different DTOs from the same base type
type CreateUserDTO = Omit<User, 'id' | 'createdAt' | 'updatedAt'>;
type UpdateUserDTO = Partial<Omit<User, 'id' | 'password' | 'createdAt' | 'updatedAt'>>;
type PublicUserDTO = Omit<User, 'password'>;
type UserListItem = Pick<User, 'id' | 'name' | 'email'>;
```

### Pattern 2: Form State Management

```typescript
type FormState<T> = {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  dirty: Partial<Record<keyof T, boolean>>;
  isValid: boolean;
  isSubmitting: boolean;
};

// Usage
type LoginForm = FormState<{ email: string; password: string }>;
```

### Pattern 3: API Response Wrapper

```typescript
type ApiResponse<T> =
  | { status: 'success'; data: T; error: null }
  | { status: 'error'; data: null; error: string }
  | { status: 'loading'; data: null; error: null };

type PaginatedResponse<T> = ApiResponse<{
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasMore: boolean;
}>;
```

## Custom Utility Types — Senior Level

```typescript
// Make specific keys required, rest stay the same
type RequireKeys<T, K extends keyof T> = T & Required<Pick<T, K>>;
// Usage: RequireKeys<User, 'email'> — email required, others unchanged

// Make specific keys optional, rest stay the same
type OptionalKeys<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
// Usage: OptionalKeys<User, 'age'> — age optional, others required

// Mutable version of a readonly type
type Mutable<T> = {
  -readonly [K in keyof T]: T[K];
};

// Get all nullable keys
type NullableKeys<T> = {
  [K in keyof T]: null extends T[K] ? K : never;
}[keyof T];

// Deep Partial
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object
    ? T[K] extends Array<infer U>
      ? Array<DeepPartial<U>>
      : DeepPartial<T[K]>
    : T[K];
};
```

## Practice Exercises

### Exercise 1: Build `StrictOmit`
```typescript
// Standard Omit allows omitting non-existent keys
// Build StrictOmit that only allows omitting actual keys
type StrictOmit<T, K extends keyof T> = ???;
```

### Exercise 2: Build `PickByType`
```typescript
// Pick only properties of a specific type
type PickByType<T, U> = ???;

interface Mixed {
  name: string;
  age: number;
  active: boolean;
  email: string;
}

type StringProps = PickByType<Mixed, string>;
// { name: string; email: string; }
```

## Key Takeaways

1. **Know all built-in utility types** — they appear in every senior TS interview
2. **Understand implementations** — `Partial`, `Pick`, `Record` use mapped types; `Extract`/`Exclude` use conditional types
3. **Compose utility types** — chain them for complex real-world DTOs
4. **`-?` removes optionality**, `+readonly` / `-readonly` control mutability
5. **Create custom utilities** for repeated patterns in your codebase
