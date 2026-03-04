# Day 1: TypeScript Fundamentals — Beyond the Basics

## Why TypeScript Matters for Senior Engineers

TypeScript isn't just "JavaScript with types." At the senior level, TypeScript is a **design tool** that:
- Encodes business rules in the type system
- Catches entire categories of bugs at compile time
- Serves as living documentation
- Enables powerful IDE tooling and refactoring

## Core Type System Architecture

### Structural Typing (Duck Typing)

TypeScript uses **structural typing**, not nominal typing:

```typescript
interface Point {
  x: number;
  y: number;
}

interface Coordinate {
  x: number;
  y: number;
}

// These are compatible — same structure
const p: Point = { x: 1, y: 2 };
const c: Coordinate = p; // ✅ Works — structural compatibility

// Contrast with nominal typing (Java/C#) where this would fail
```

### Excess Property Checking

```typescript
interface Config {
  host: string;
  port: number;
}

// Direct object literal → excess property checking
const config: Config = {
  host: 'localhost',
  port: 3000,
  debug: true, // ❌ Error: Object literal may only specify known properties
};

// Via variable → no excess property checking
const obj = { host: 'localhost', port: 3000, debug: true };
const config2: Config = obj; // ✅ Works — structural compatibility
```

### Type Widening and Narrowing

```typescript
// Widening: TypeScript infers wider types
let x = 'hello'; // type: string (widened)
const y = 'hello'; // type: 'hello' (literal type, no widening)

// Control widening
let z = 'hello' as const; // type: 'hello'
const arr = [1, 2, 3] as const; // type: readonly [1, 2, 3]

// Narrowing: TypeScript narrows types in control flow
function process(value: string | number) {
  if (typeof value === 'string') {
    // TypeScript knows: value is string
    return value.toUpperCase();
  }
  // TypeScript knows: value is number
  return value.toFixed(2);
}
```

## Advanced Primitive Types

### Literal Types

```typescript
type Direction = 'north' | 'south' | 'east' | 'west';
type HttpStatus = 200 | 301 | 404 | 500;
type Toggle = true | false; // Same as boolean, but explicit

// Template literal types (TS 4.1+)
type EventName = `on${Capitalize<string>}`; // 'onClick', 'onHover', etc.
```

### `unknown` vs `any` vs `never`

```typescript
// any: Opt out of type checking entirely
let unsafeValue: any = 'hello';
unsafeValue.nonExistentMethod(); // No error — dangerous!

// unknown: Type-safe alternative to any
let safeValue: unknown = 'hello';
// safeValue.toUpperCase(); // ❌ Error — must narrow first
if (typeof safeValue === 'string') {
  safeValue.toUpperCase(); // ✅ After narrowing
}

// never: Impossible type — for exhaustive checks
type Shape = 'circle' | 'square';

function getArea(shape: Shape): number {
  switch (shape) {
    case 'circle': return Math.PI * 10;
    case 'square': return 100;
    default:
      const _exhaustive: never = shape; // Ensures all cases handled
      throw new Error(`Unknown shape: ${_exhaustive}`);
  }
}
```

## Function Types — Advanced Patterns

### Overloads

```typescript
// Overload signatures
function createElement(tag: 'a'): HTMLAnchorElement;
function createElement(tag: 'canvas'): HTMLCanvasElement;
function createElement(tag: 'div'): HTMLDivElement;
function createElement(tag: string): HTMLElement;

// Implementation signature
function createElement(tag: string): HTMLElement {
  return document.createElement(tag);
}

const anchor = createElement('a'); // type: HTMLAnchorElement
const div = createElement('div');   // type: HTMLDivElement
```

### `this` Parameter

```typescript
interface User {
  name: string;
  greet(this: User): string;
}

const user: User = {
  name: 'Bharath',
  greet() {
    return `Hello, ${this.name}`; // 'this' is typed as User
  },
};

const greet = user.greet;
// greet(); // ❌ Error: 'this' context of type 'void' is not assignable
```

### Assertion Functions

```typescript
function assertIsString(value: unknown): asserts value is string {
  if (typeof value !== 'string') {
    throw new Error('Not a string');
  }
}

function processInput(input: unknown) {
  assertIsString(input);
  // TypeScript now knows input is string
  console.log(input.toUpperCase());
}
```

## Enums — The Full Picture

### Const Enums (Inlined at compile time)

```typescript
const enum Direction {
  Up = 'UP',
  Down = 'DOWN',
  Left = 'LEFT',
  Right = 'RIGHT',
}

// Compiles to: const dir = "UP" (inlined, no runtime object)
const dir = Direction.Up;
```

### Enum Alternatives (Recommended)

```typescript
// Prefer union types + object maps
const DIRECTION = {
  Up: 'UP',
  Down: 'DOWN',
  Left: 'LEFT',
  Right: 'RIGHT',
} as const;

type Direction = typeof DIRECTION[keyof typeof DIRECTION];
// type Direction = "UP" | "DOWN" | "LEFT" | "RIGHT"
```

## Strict Mode — Non-Negotiable for Production

```jsonc
// tsconfig.json — strict mode flags
{
  "compilerOptions": {
    "strict": true, // Enables ALL strict flags:
    // "noImplicitAny": true,
    // "strictNullChecks": true,
    // "strictFunctionTypes": true,
    // "strictBindCallApply": true,
    // "strictPropertyInitialization": true,
    // "noImplicitThis": true,
    // "alwaysStrict": true,
    // "useUnknownInCatchVariables": true,

    // Additional strictness (not in "strict"):
    "noUncheckedIndexedAccess": true,  // array[0] is T | undefined
    "exactOptionalProperties": true,    // Can't assign undefined to optional
    "noPropertyAccessFromIndexSignature": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noImplicitOverride": true,
  }
}
```

## Practice Exercises

### Exercise 1: Type-Safe Config Builder
```typescript
// Build a configuration object with type safety
// Requirements:
// 1. Keys must be from a predefined set
// 2. Values must match the expected type for each key
// 3. All required keys must be provided

interface AppConfig {
  port: number;
  host: string;
  debug: boolean;
  logLevel: 'info' | 'warn' | 'error';
}

// Implement: createConfig that enforces all keys
```

### Exercise 2: Exhaustive Switch
```typescript
// Create a type-safe state machine for an order
type OrderStatus = 'pending' | 'processing' | 'shipped' | 'delivered' | 'cancelled';

// Implement: getNextStatus that handles ALL cases
// Adding a new status should cause a compile error
```

## Key Takeaways

1. **Structural typing** means types are compatible if their structures match
2. **`unknown` > `any`** — always prefer unknown for type-safe handling
3. **`never`** enables exhaustive checking — catch missing switch cases at compile time
4. **Strict mode** is non-negotiable — enable ALL strict flags
5. **`as const`** prevents widening and enables literal types
6. **Assertion functions** let you write custom type narrowing logic

## Interview Quick-Fire

| Question | Answer |
|----------|--------|
| Structural vs Nominal typing? | TS uses structural — shape matters, not name |
| `unknown` vs `any`? | `unknown` requires narrowing before use; `any` bypasses all checks |
| When does excess property checking apply? | Only on direct object literal assignments |
| What does `as const` do? | Prevents widening, makes values readonly literal types |
| Why use `never` in default case? | Ensures exhaustive handling — compile error if case added |
