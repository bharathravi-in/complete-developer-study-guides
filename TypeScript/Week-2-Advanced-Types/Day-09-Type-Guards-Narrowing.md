# Day 9: Type Guards & Narrowing — Complete Guide

## What Is Type Narrowing?

Type narrowing is TypeScript's ability to refine a broad type to a more specific one within a code block based on runtime checks.

## Built-in Type Guards

### `typeof` Guard

```typescript
function process(value: string | number | boolean) {
  if (typeof value === 'string') {
    // value: string
    return value.toUpperCase();
  }
  if (typeof value === 'number') {
    // value: number
    return value.toFixed(2);
  }
  // value: boolean
  return value ? 'yes' : 'no';
}
```

### `instanceof` Guard

```typescript
class ApiError extends Error {
  constructor(public statusCode: number, message: string) {
    super(message);
  }
}

class ValidationError extends Error {
  constructor(public fields: string[], message: string) {
    super(message);
  }
}

function handleError(error: Error) {
  if (error instanceof ApiError) {
    // error: ApiError
    console.log(`API Error ${error.statusCode}: ${error.message}`);
  } else if (error instanceof ValidationError) {
    // error: ValidationError
    console.log(`Validation: ${error.fields.join(', ')}`);
  } else {
    // error: Error
    console.log(`Unknown: ${error.message}`);
  }
}
```

### `in` Operator Guard

```typescript
interface Bird {
  fly(): void;
  layEggs(): void;
}

interface Fish {
  swim(): void;
  layEggs(): void;
}

function move(animal: Bird | Fish) {
  if ('fly' in animal) {
    animal.fly(); // animal: Bird
  } else {
    animal.swim(); // animal: Fish
  }
}
```

### Truthiness Narrowing

```typescript
function printName(name: string | null | undefined) {
  if (name) {
    // name: string (null and undefined eliminated)
    console.log(name.toUpperCase());
  }
}

// Double-bang pattern
function getLength(value: string | null): number {
  return value?.length ?? 0; // Safe with optional chaining
}
```

## Custom Type Guards (Type Predicates)

```typescript
interface Cat { meow(): void; name: string; }
interface Dog { bark(): void; name: string; }

// Type predicate: `animal is Cat`
function isCat(animal: Cat | Dog): animal is Cat {
  return 'meow' in animal;
}

function interact(animal: Cat | Dog) {
  if (isCat(animal)) {
    animal.meow(); // animal: Cat
  } else {
    animal.bark(); // animal: Dog
  }
}
```

### Advanced Type Guards for API Responses

```typescript
interface SuccessResponse<T> {
  status: 'success';
  data: T;
}

interface ErrorResponse {
  status: 'error';
  error: { code: number; message: string };
}

type ApiResponse<T> = SuccessResponse<T> | ErrorResponse;

function isSuccess<T>(response: ApiResponse<T>): response is SuccessResponse<T> {
  return response.status === 'success';
}

async function fetchUser(id: string) {
  const response: ApiResponse<User> = await api.get(`/users/${id}`);

  if (isSuccess(response)) {
    // response: SuccessResponse<User>
    console.log(response.data.name);
  } else {
    // response: ErrorResponse
    console.log(response.error.message);
  }
}
```

## Discriminated Unions (Tagged Unions)

The most powerful narrowing pattern in TypeScript:

```typescript
// Each variant has a unique literal type on a common property
type Shape =
  | { kind: 'circle'; radius: number }
  | { kind: 'rectangle'; width: number; height: number }
  | { kind: 'triangle'; base: number; height: number };

function area(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'rectangle':
      return shape.width * shape.height;
    case 'triangle':
      return 0.5 * shape.base * shape.height;
  }
}

// Exhaustive checking with never
function assertNever(value: never): never {
  throw new Error(`Unexpected value: ${value}`);
}

function areaExhaustive(shape: Shape): number {
  switch (shape.kind) {
    case 'circle': return Math.PI * shape.radius ** 2;
    case 'rectangle': return shape.width * shape.height;
    case 'triangle': return 0.5 * shape.base * shape.height;
    default: return assertNever(shape); // Compile error if case missed
  }
}
```

### Real-World: Redux Actions

```typescript
type Action =
  | { type: 'FETCH_START' }
  | { type: 'FETCH_SUCCESS'; payload: User[] }
  | { type: 'FETCH_ERROR'; error: string }
  | { type: 'SET_FILTER'; filter: string };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'FETCH_START':
      return { ...state, loading: true };
    case 'FETCH_SUCCESS':
      return { ...state, loading: false, users: action.payload };
    case 'FETCH_ERROR':
      return { ...state, loading: false, error: action.error };
    case 'SET_FILTER':
      return { ...state, filter: action.filter };
  }
}
```

## Assertion Functions

```typescript
function assertIsDefined<T>(value: T): asserts value is NonNullable<T> {
  if (value === null || value === undefined) {
    throw new Error('Value is null or undefined');
  }
}

function processUser(user: User | null) {
  assertIsDefined(user);
  // After assertion, user: User (narrowed)
  console.log(user.name);
}

// Assertion with condition
function assert(condition: unknown, message: string): asserts condition {
  if (!condition) throw new Error(message);
}

function process(value: string | number) {
  assert(typeof value === 'string', 'Expected string');
  // value: string
  value.toUpperCase();
}
```

## Narrowing Gotchas

### Gotcha 1: `typeof null === 'object'`
```typescript
function process(value: string | object | null) {
  if (typeof value === 'object') {
    // value: object | null — null is NOT eliminated!
    value?.toString(); // Need optional chaining
  }
}
```

### Gotcha 2: Callbacks Break Narrowing
```typescript
function example(value: string | null) {
  if (value !== null) {
    // value: string ✅
    setTimeout(() => {
      // value: string | null ← narrowing lost in callback!
      // TypeScript can't guarantee value hasn't changed
    }, 0);
  }
}

// Fix: capture in const
function exampleFixed(value: string | null) {
  if (value !== null) {
    const definitelyString = value; // type: string
    setTimeout(() => {
      console.log(definitelyString.toUpperCase()); // ✅
    }, 0);
  }
}
```

## Key Takeaways

1. **Discriminated unions** are the gold standard for state modeling in TypeScript
2. **Custom type guards** (`is` predicates) let you create reusable narrowing functions
3. **Assertion functions** (`asserts`) throw on failure and narrow on success
4. **`never` in default** enables exhaustive checking — compile errors when cases added
5. **Watch for gotchas**: null in typeof, callback narrowing loss
