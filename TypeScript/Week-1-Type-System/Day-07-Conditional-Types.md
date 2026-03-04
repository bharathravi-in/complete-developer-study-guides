# Day 7: Conditional Types

## The Foundation: `extends` in Type Position

Conditional types follow the syntax: `T extends U ? X : Y`

```typescript
// Basic conditional type
type IsString<T> = T extends string ? true : false;

type A = IsString<'hello'>; // true
type B = IsString<42>;      // false
type C = IsString<string>;  // true
```

## Distributive Conditional Types

When a conditional type acts on a **union type**, it distributes over each member:

```typescript
type ToArray<T> = T extends any ? T[] : never;

// Distributes over union members
type Result = ToArray<string | number>;
// = (string extends any ? string[] : never) | (number extends any ? number[] : never)
// = string[] | number[]

// Prevent distribution with tuple wrapping
type ToArrayNonDist<T> = [T] extends [any] ? T[] : never;
type Result2 = ToArrayNonDist<string | number>;
// = (string | number)[]
```

## The `infer` Keyword

`infer` declares a type variable within a conditional type that TypeScript infers:

```typescript
// Extract return type of a function
type GetReturnType<T> = T extends (...args: any[]) => infer R ? R : never;

type R1 = GetReturnType<() => string>;          // string
type R2 = GetReturnType<(x: number) => boolean>; // boolean
type R3 = GetReturnType<string>;                 // never

// Extract element type of an array
type ElementType<T> = T extends (infer E)[] ? E : T;

type E1 = ElementType<string[]>;  // string
type E2 = ElementType<number>;    // number

// Extract Promise value
type UnwrapPromise<T> = T extends Promise<infer V> ? V : T;
type P1 = UnwrapPromise<Promise<string>>; // string
type P2 = UnwrapPromise<string>;          // string

// Recursive unwrap
type DeepUnwrapPromise<T> = T extends Promise<infer V>
  ? DeepUnwrapPromise<V>
  : T;
type P3 = DeepUnwrapPromise<Promise<Promise<Promise<number>>>>; // number
```

## Advanced Infer Patterns

### Infer in Template Literal Types

```typescript
// Extract parts of string types
type ExtractRouteParams<T extends string> =
  T extends `${string}:${infer Param}/${infer Rest}`
    ? Param | ExtractRouteParams<Rest>
    : T extends `${string}:${infer Param}`
      ? Param
      : never;

type Params = ExtractRouteParams<'/users/:userId/posts/:postId'>;
// 'userId' | 'postId'
```

### Infer in Tuple Types

```typescript
// First and Last element
type First<T extends any[]> = T extends [infer F, ...any[]] ? F : never;
type Last<T extends any[]> = T extends [...any[], infer L] ? L : never;

type F = First<[1, 2, 3]>; // 1
type L = Last<[1, 2, 3]>;  // 3

// Head and Tail
type Tail<T extends any[]> = T extends [any, ...infer Rest] ? Rest : never;
type T1 = Tail<[1, 2, 3]>; // [2, 3]
```

### Infer with Constraints (TS 4.7+)

```typescript
// Constrain what infer matches
type FirstString<T> = T extends [infer S extends string, ...unknown[]]
  ? S
  : never;

type FS1 = FirstString<['hello', 42]>; // 'hello'
type FS2 = FirstString<[42, 'hello']>; // never
```

## Real-World Conditional Type Patterns

### Pattern 1: Type-Safe API Route Handler

```typescript
interface RouteDefinitions {
  '/users': { GET: User[]; POST: User };
  '/users/:id': { GET: User; PUT: User; DELETE: void };
  '/posts': { GET: Post[]; POST: Post };
}

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

type RouteResponse<
  Path extends keyof RouteDefinitions,
  Method extends keyof RouteDefinitions[Path]
> = RouteDefinitions[Path][Method];

// Usage
type GetUsersResponse = RouteResponse<'/users', 'GET'>; // User[]
type CreateUserResponse = RouteResponse<'/users', 'POST'>; // User
```

### Pattern 2: Flatten Nested Types

```typescript
type Flatten<T> = T extends Array<infer U>
  ? Flatten<U>
  : T;

type F1 = Flatten<string[][]>;  // string
type F2 = Flatten<number[][][]>; // number
type F3 = Flatten<string>;       // string
```

### Pattern 3: Conditional Event Handlers

```typescript
type EventPayload<T extends string> =
  T extends 'click' ? { x: number; y: number } :
  T extends 'keypress' ? { key: string; code: number } :
  T extends 'scroll' ? { scrollTop: number; scrollLeft: number } :
  never;

function handleEvent<T extends 'click' | 'keypress' | 'scroll'>(
  type: T,
  handler: (payload: EventPayload<T>) => void
): void { /* ... */ }

handleEvent('click', ({ x, y }) => {
  // x: number, y: number — fully typed!
});
```

### Pattern 4: Recursive Type Transformations

```typescript
// Convert all string properties to number recursively
type StringToNumber<T> = {
  [K in keyof T]: T[K] extends string
    ? number
    : T[K] extends object
      ? StringToNumber<T[K]>
      : T[K];
};

interface FormValues {
  name: string;
  age: number;
  address: {
    street: string;
    city: string;
    zip: number;
  };
}

type ValidationScores = StringToNumber<FormValues>;
// { name: number; age: number; address: { street: number; city: number; zip: number } }
```

## Built-in Conditional Types

```typescript
// These are all conditional types internally:
type NonNullable<T> = T extends null | undefined ? never : T;
type Extract<T, U> = T extends U ? T : never;
type Exclude<T, U> = T extends U ? never : T;
type ReturnType<T extends (...args: any) => any> = T extends (...args: any) => infer R ? R : any;
```

## Practice Exercises

### Exercise 1: Implement `IsNever<T>`
```typescript
// Check if T is never
type IsNever<T> = ???;

type A = IsNever<never>;  // true
type B = IsNever<string>; // false
```

### Exercise 2: Implement `TupleToUnion<T>`
```typescript
type TupleToUnion<T extends any[]> = ???;

type U = TupleToUnion<[string, number, boolean]>;
// string | number | boolean
```

### Exercise 3: Type-Safe Deep Get
```typescript
// Implement a type that gets a nested property type by dot-notation path
type DeepGet<T, Path extends string> = ???;

interface Config {
  db: { host: string; port: number };
  auth: { secret: string };
}

type DBHost = DeepGet<Config, 'db.host'>; // string
```

## Key Takeaways

1. **Conditional types** are TypeScript's "if/else" for the type system
2. **Distribution** happens automatically over unions — wrap in `[T]` to prevent
3. **`infer`** is like pattern matching — extract types from structures
4. **Recursive conditional types** enable deep type transformations
5. **Most built-in utility types** are conditional types internally

## Interview Quick-Fire

| Question | Answer |
|----------|--------|
| What is a distributive conditional type? | Conditional type that distributes over union members |
| How to prevent distribution? | Wrap both sides in tuples: `[T] extends [U]` |
| What does `infer` do? | Declares a type variable within a conditional type to extract/capture |
| Can conditional types be recursive? | Yes — useful for deep transformations like DeepPartial |
| Name 3 built-in conditional utility types | `Exclude`, `Extract`, `NonNullable`, `ReturnType`, `Parameters` |
