# TypeScript Cheatsheet — Quick Reference

## Type Basics
```typescript
// Primitives
let s: string = 'hello';
let n: number = 42;
let b: boolean = true;
let u: undefined = undefined;
let nl: null = null;
let sym: symbol = Symbol('id');
let big: bigint = 100n;

// Special types
let any_: any;           // Opt-out of type checking
let unknown_: unknown;   // Must narrow before use
function fail(): never { throw new Error(); } // Never returns

// Literal types
type Dir = 'up' | 'down';
type Status = 200 | 404 | 500;
```

## Object Types
```typescript
// Interface
interface User {
  readonly id: string;    // immutable
  name: string;
  email?: string;         // optional
  [key: string]: unknown; // index signature
}

// Type alias
type Point = { x: number; y: number };

// Intersection
type Admin = User & { role: 'admin' };

// Union
type Result = Success | Error;
```

## Function Types
```typescript
// Arrow functions
type Fn = (x: number, y: number) => number;

// Overloads
function parse(input: string): number;
function parse(input: number): string;
function parse(input: string | number): number | string { /* ... */ }

// Generic function
function identity<T>(value: T): T { return value; }

// Assertion function
function assert(val: unknown): asserts val is string { }
```

## Generics
```typescript
// Constraint
function getLength<T extends { length: number }>(item: T): number {
  return item.length;
}

// keyof constraint
function getVal<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

// Default
interface Box<T = string> { value: T; }

// Multiple params
function merge<T, U>(a: T, b: U): T & U { return { ...a, ...b }; }
```

## Utility Types
```typescript
Partial<T>           // All props optional
Required<T>          // All props required
Readonly<T>          // All props readonly
Pick<T, K>           // Select props K from T
Omit<T, K>           // Remove props K from T
Record<K, V>         // Map keys K to values V
Extract<T, U>        // Members of T assignable to U
Exclude<T, U>        // Members of T NOT assignable to U
NonNullable<T>       // Remove null/undefined
ReturnType<F>        // Return type of function F
Parameters<F>        // Parameter types as tuple
Awaited<T>           // Unwrap Promise<T>
```

## Mapped Types
```typescript
// Basic mapped type
type Flags<T> = { [K in keyof T]: boolean };

// With modifiers
type Mutable<T> = { -readonly [K in keyof T]: T[K] };
type Concrete<T> = { [K in keyof T]-?: T[K] };

// Key remapping (TS 4.1+)
type Getters<T> = {
  [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K];
};
```

## Conditional Types
```typescript
// Basic
type IsString<T> = T extends string ? true : false;

// Infer
type UnwrapPromise<T> = T extends Promise<infer V> ? V : T;
type RetType<T> = T extends (...args: any[]) => infer R ? R : never;

// Distributive (over unions)
type ToArr<T> = T extends any ? T[] : never;
type R = ToArr<string | number>; // string[] | number[]

// Non-distributive
type ToArrND<T> = [T] extends [any] ? T[] : never;
```

## Type Guards
```typescript
typeof x === 'string'           // typeof
x instanceof Date               // instanceof
'property' in obj               // in operator
function isFish(x: any): x is Fish { } // Custom predicate
function assert(x: unknown): asserts x is string { } // Assertion
```

## Template Literal Types
```typescript
type Method = 'GET' | 'POST';
type Path = '/users' | '/posts';
type Route = `${Method} ${Path}`; // "GET /users" | "GET /posts" | ...

// String manipulation
Uppercase<S>    Lowercase<S>    Capitalize<S>    Uncapitalize<S>
```

## Discriminated Unions
```typescript
type Result<T> =
  | { status: 'ok'; data: T }
  | { status: 'error'; error: string };

function handle<T>(result: Result<T>) {
  if (result.status === 'ok') {
    result.data;  // ✅ narrowed
  } else {
    result.error; // ✅ narrowed
  }
}
```

## Branded Types (Nominal)
```typescript
type Brand<T, B> = T & { __brand: B };
type UserId = Brand<string, 'UserId'>;
type PostId = Brand<string, 'PostId'>;
```

## Key Operators
```typescript
keyof T              // Union of keys of T
T[K]                 // Indexed access type
typeof variable      // Type of JS value
T extends U ? X : Y  // Conditional type
infer R              // Type variable in conditional
as const             // Readonly literal (no widening)
satisfies Type       // Validate without widening (TS 4.9+)
```

## tsconfig.json Essentials
```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalProperties": true,
    "noImplicitReturns": true,
    "noImplicitOverride": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "declaration": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src"
  }
}
```
