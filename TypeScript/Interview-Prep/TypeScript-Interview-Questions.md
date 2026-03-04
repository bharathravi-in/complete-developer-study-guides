# TypeScript Interview Questions — Senior / Staff Level

## Section 1: Type System Fundamentals

### Q1: Explain structural typing vs nominal typing. How does TypeScript handle this?
**Answer**: TypeScript uses **structural typing** (duck typing) — two types are compatible if they have the same structure, regardless of name. In nominal type systems (Java, C#), types must be explicitly declared compatible.

```typescript
interface Point { x: number; y: number; }
interface Coordinate { x: number; y: number; }
const p: Point = { x: 1, y: 2 };
const c: Coordinate = p; // ✅ Same structure = compatible

// Simulate nominal types with branded types
type USD = number & { __brand: 'USD' };
type EUR = number & { __brand: 'EUR' };
const usd = 100 as USD;
// const eur: EUR = usd; // ❌ Brands make them incompatible
```

### Q2: What's the difference between `unknown`, `any`, and `never`?
**Answer**:
- **`any`**: Disables type checking entirely. Anything goes.
- **`unknown`**: Top type — can hold any value, but must be narrowed before use. Type-safe alternative to `any`.
- **`never`**: Bottom type — no value can be assigned. Used for exhaustive checks and impossible states.

```typescript
let a: any = 'hello';     a.anything(); // No error
let u: unknown = 'hello'; // u.anything(); // ❌ Must narrow first
function fail(): never { throw new Error(); } // Never returns
```

### Q3: Explain type widening and how `as const` prevents it.
**Answer**: TypeScript widens literal types to their base types for mutable variables. `as const` prevents this by making values readonly with literal types.

```typescript
let x = 'hello';           // type: string (widened)
const y = 'hello';         // type: 'hello' (const prevents widening)
let z = 'hello' as const;  // type: 'hello'
const arr = [1, 2] as const; // type: readonly [1, 2]
```

### Q4: What is excess property checking and when does it apply?
**Answer**: TypeScript checks for extra properties only on **direct object literal assignments**. When passing via a variable, structural compatibility is used instead.

```typescript
interface Config { host: string; port: number; }
const c: Config = { host: 'x', port: 80, extra: true }; // ❌ Excess
const obj = { host: 'x', port: 80, extra: true };
const c2: Config = obj; // ✅ No excess check via variable
```

## Section 2: Generics

### Q5: Implement a type-safe `pick` function.
```typescript
function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  const result = {} as Pick<T, K>;
  for (const key of keys) {
    result[key] = obj[key];
  }
  return result;
}

const user = { name: 'Bharath', age: 30, email: 'b@e.com' };
const picked = pick(user, ['name', 'email']); // { name: string; email: string }
```

### Q6: What is generic variance? Explain covariance and contravariance.
**Answer**:
- **Covariant**: `Array<Dog>` is assignable to `Array<Animal>` (output positions — return types)
- **Contravariant**: `(animal: Animal) => void` is assignable to `(dog: Dog) => void` (input positions — parameters, under strict mode)
- **Invariant**: Neither direction works

TypeScript 4.7 added explicit variance annotations:
```typescript
interface Producer<out T> { produce(): T; }    // Covariant
interface Consumer<in T> { consume(item: T): void; } // Contravariant
interface Both<in out T> { transform(item: T): T; }  // Invariant
```

## Section 3: Conditional Types & Mapped Types

### Q7: Implement `DeepPartial<T>`.
```typescript
type DeepPartial<T> = {
  [K in keyof T]?: T[K] extends object
    ? T[K] extends Function
      ? T[K]
      : T[K] extends Array<infer U>
        ? Array<DeepPartial<U>>
        : DeepPartial<T[K]>
    : T[K];
};
```

### Q8: Implement `Flatten<T>` that recursively unwraps arrays.
```typescript
type Flatten<T> = T extends Array<infer U> ? Flatten<U> : T;

type A = Flatten<string[][]>; // string
type B = Flatten<number>;     // number
```

### Q9: What are template literal types? Give a real-world example.
```typescript
type HTTPMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';
type APIPath = '/users' | '/posts' | '/comments';
type APIRoute = `${HTTPMethod} ${APIPath}`;
// "GET /users" | "GET /posts" | ... (12 combinations)

// Extract route params
type ExtractParam<T extends string> =
  T extends `${string}:${infer P}/${infer Rest}`
    ? P | ExtractParam<`/${Rest}`>
    : T extends `${string}:${infer P}`
      ? P : never;

type Params = ExtractParam<'/users/:id/posts/:postId'>; // "id" | "postId"
```

### Q10: Explain distributive conditional types.
**Answer**: When a conditional type receives a union, it distributes over each member individually.

```typescript
type ToArray<T> = T extends any ? T[] : never;
type R1 = ToArray<string | number>; // string[] | number[]

// Prevent with tuple wrapping
type ToArrayND<T> = [T] extends [any] ? T[] : never;
type R2 = ToArrayND<string | number>; // (string | number)[]
```

## Section 4: Advanced Patterns

### Q11: What are branded types and when would you use them?
**Answer**: Branded types simulate nominal typing by adding a phantom property. Use for: currency types, IDs, validated strings.

```typescript
type Brand<T, B extends string> = T & { readonly __brand: B };
type UserId = Brand<string, 'UserId'>;
type PostId = Brand<string, 'PostId'>;

function getUser(id: UserId): User { /* ... */ }
const userId = '123' as UserId;
const postId = '456' as PostId;
getUser(userId); // ✅
// getUser(postId); // ❌ Type error — can't pass PostId as UserId
```

### Q12: How do you implement a type-safe state machine?
```typescript
type State = 'idle' | 'loading' | 'success' | 'error';

type Transitions = {
  idle: 'loading';
  loading: 'success' | 'error';
  success: 'idle';
  error: 'idle' | 'loading';
};

class StateMachine<S extends State> {
  constructor(private state: S) {}

  transition<Next extends Transitions[S]>(
    nextState: Next
  ): StateMachine<Next> {
    return new StateMachine(nextState);
  }

  getState(): S { return this.state; }
}

const machine = new StateMachine('idle' as 'idle');
const loading = machine.transition('loading');   // ✅
const success = loading.transition('success');   // ✅
// loading.transition('idle');                    // ❌ Not valid
```

### Q13: What is declaration merging? When is it useful?
**Answer**: TypeScript merges multiple declarations of the same name. Common with interfaces and modules.

```typescript
// Interface merging
interface Express {
  Request: { body: any };
}
// In @types/express-session
interface Express {
  Request: { session: Session };
}
// Merged: Request has both body and session

// Module augmentation
declare module 'express' {
  interface Request {
    user?: User; // Add custom properties
  }
}
```

### Q14: Explain `satisfies` operator (TS 4.9+).
**Answer**: `satisfies` validates that an expression matches a type without widening it. Preserves the narrow literal type.

```typescript
type Colors = Record<string, [number, number, number] | string>;

const palette = {
  red: [255, 0, 0],
  green: '#00FF00',
  blue: [0, 0, 255],
} satisfies Colors;

// palette.red is [number, number, number] — NOT string | [number, number, number]
palette.red.map(c => c * 2); // ✅ Works — type is preserved as tuple
palette.green.toUpperCase();  // ✅ Works — type is preserved as string
```

## Section 5: Practical Architecture

### Q15: How do you type a middleware pipeline?
```typescript
type Middleware<T> = (context: T, next: () => Promise<void>) => Promise<void>;

class Pipeline<T> {
  private middlewares: Middleware<T>[] = [];

  use(middleware: Middleware<T>): this {
    this.middlewares.push(middleware);
    return this;
  }

  async execute(context: T): Promise<void> {
    let index = 0;
    const next = async (): Promise<void> => {
      if (index < this.middlewares.length) {
        await this.middlewares[index++](context, next);
      }
    };
    await next();
  }
}
```

### Q16: What's the difference between `interface` and `type`?
| Feature | `interface` | `type` |
|---------|-------------|--------|
| Declaration merging | ✅ Yes | ❌ No |
| `extends` | ✅ `extends` keyword | Uses `&` intersection |
| Unions, tuples, mapped | ❌ No | ✅ Yes |
| `implements` | ✅ Yes | ✅ Yes (with limitations) |
| Computed properties | ❌ No | ✅ Yes |

**Rule of thumb**: Use `interface` for public APIs (extensible), `type` for unions/intersections/complex types.

## Section 6: TypeScript Config & Tooling

### Q17: What strict mode flags should always be enabled?
```jsonc
{
  "strict": true,                          // All strict flags
  "noUncheckedIndexedAccess": true,        // arr[0] is T | undefined
  "exactOptionalProperties": true,         // No undefined in optional
  "noImplicitReturns": true,               // All paths return
  "noFallthroughCasesInSwitch": true,      // No switch fallthrough
  "noImplicitOverride": true              // Require 'override' keyword
}
```

### Q18: What are project references and when to use them?
**Answer**: Project references (`references` in tsconfig) enable:
- Incremental builds across a monorepo
- Logical separation of concerns
- Faster compile times (only rebuild changed projects)

```jsonc
// tsconfig.json (root)
{
  "references": [
    { "path": "./packages/shared" },
    { "path": "./packages/api" },
    { "path": "./packages/web" }
  ]
}
```

## Rapid-Fire Summary

| Concept | One-Liner |
|---------|-----------|
| Structural typing | Shape matters, not name |
| `unknown` vs `any` | `unknown` is safe `any` |
| `never` | Bottom type — for impossible states, exhaustive checks |
| `as const` | Prevents widening, makes readonly literals |
| `satisfies` | Validates type without widening |
| Branded types | Nominal typing simulation with phantom properties |
| Distributive conditionals | Union members evaluated individually |
| `infer` | Pattern-match and extract types |
| Declaration merging | Multiple declarations of same interface merge |
| Variance annotations | `in`/`out` keywords for explicit covariance/contravariance |
