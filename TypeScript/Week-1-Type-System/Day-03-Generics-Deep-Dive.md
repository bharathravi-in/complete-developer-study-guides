# Day 3: Generics Deep Dive

## Why Generics Matter

Generics let you write **reusable, type-safe code** that works with any type while preserving type information. They are the foundation of every advanced TypeScript pattern.

## Generic Functions

### Basic Generic Functions

```typescript
// Without generics — loses type information
function identity(value: any): any {
  return value;
}

// With generics — preserves type
function identity<T>(value: T): T {
  return value;
}

const str = identity('hello');    // type: string
const num = identity(42);         // type: number
const obj = identity({ x: 1 });   // type: { x: number }
```

### Multiple Type Parameters

```typescript
function pair<T, U>(first: T, second: U): [T, U] {
  return [first, second];
}

const p = pair('hello', 42); // type: [string, number]

// Swap function
function swap<T, U>(tuple: [T, U]): [U, T] {
  return [tuple[1], tuple[0]];
}

const swapped = swap(['hello', 42]); // type: [number, string]
```

### Generic Arrow Functions (JSX Gotcha)

```typescript
// In .ts files — works fine
const identity = <T>(value: T): T => value;

// In .tsx files — <T> looks like JSX
// Fix 1: Extend constraint
const identity = <T extends unknown>(value: T): T => value;

// Fix 2: Trailing comma (less common)
const identity = <T,>(value: T): T => value;
```

## Generic Constraints

### `extends` Keyword

```typescript
// Constrain T to have a 'length' property
function logLength<T extends { length: number }>(value: T): T {
  console.log(value.length);
  return value;
}

logLength('hello');       // ✅ string has length
logLength([1, 2, 3]);    // ✅ array has length
logLength({ length: 5 }); // ✅ has length property
// logLength(42);         // ❌ number has no length
```

### `keyof` Constraint

```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const person = { name: 'Bharath', age: 30, role: 'Tech Lead' };

const name = getProperty(person, 'name'); // type: string
const age = getProperty(person, 'age');    // type: number
// getProperty(person, 'email');            // ❌ Error: not a key of person
```

### Multiple Constraints

```typescript
interface Serializable {
  serialize(): string;
}

interface Loggable {
  log(): void;
}

// T must satisfy BOTH interfaces
function process<T extends Serializable & Loggable>(item: T): string {
  item.log();
  return item.serialize();
}
```

## Generic Interfaces and Types

```typescript
// Generic interface
interface Repository<T> {
  findById(id: string): Promise<T | null>;
  findAll(): Promise<T[]>;
  create(item: Omit<T, 'id'>): Promise<T>;
  update(id: string, item: Partial<T>): Promise<T>;
  delete(id: string): Promise<boolean>;
}

// Usage
interface User {
  id: string;
  name: string;
  email: string;
}

class UserRepository implements Repository<User> {
  async findById(id: string): Promise<User | null> { /* ... */ }
  async findAll(): Promise<User[]> { /* ... */ }
  async create(item: Omit<User, 'id'>): Promise<User> { /* ... */ }
  async update(id: string, item: Partial<User>): Promise<User> { /* ... */ }
  async delete(id: string): Promise<boolean> { /* ... */ }
}
```

## Generic Classes

```typescript
class Stack<T> {
  private items: T[] = [];

  push(item: T): void {
    this.items.push(item);
  }

  pop(): T | undefined {
    return this.items.pop();
  }

  peek(): T | undefined {
    return this.items[this.items.length - 1];
  }

  get size(): number {
    return this.items.length;
  }
}

const numberStack = new Stack<number>();
numberStack.push(1);
numberStack.push(2);
const val = numberStack.pop(); // type: number | undefined

// With constraint
class SortableCollection<T extends { compareTo(other: T): number }> {
  private items: T[] = [];

  add(item: T): void {
    this.items.push(item);
  }

  sort(): T[] {
    return [...this.items].sort((a, b) => a.compareTo(b));
  }
}
```

## Real-World Generic Patterns

### Pattern 1: Type-Safe Event Emitter

```typescript
type EventMap = {
  userLogin: { userId: string; timestamp: Date };
  userLogout: { userId: string };
  error: { message: string; code: number };
};

class TypedEventEmitter<T extends Record<string, any>> {
  private listeners = new Map<keyof T, Set<Function>>();

  on<K extends keyof T>(event: K, handler: (payload: T[K]) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(handler);
  }

  emit<K extends keyof T>(event: K, payload: T[K]): void {
    this.listeners.get(event)?.forEach(handler => handler(payload));
  }

  off<K extends keyof T>(event: K, handler: (payload: T[K]) => void): void {
    this.listeners.get(event)?.delete(handler);
  }
}

const emitter = new TypedEventEmitter<EventMap>();
emitter.on('userLogin', ({ userId, timestamp }) => {
  // userId: string, timestamp: Date — fully typed!
  console.log(`${userId} logged in at ${timestamp}`);
});

emitter.emit('userLogin', { userId: '123', timestamp: new Date() }); // ✅
// emitter.emit('userLogin', { userId: 123 }); // ❌ Error
```

### Pattern 2: Builder Pattern with Generics

```typescript
class QueryBuilder<T> {
  private conditions: string[] = [];
  private selectedFields: (keyof T)[] = [];
  private orderByField?: keyof T;

  select<K extends keyof T>(...fields: K[]): QueryBuilder<Pick<T, K>> {
    this.selectedFields = fields as any;
    return this as any;
  }

  where<K extends keyof T>(field: K, value: T[K]): this {
    this.conditions.push(`${String(field)} = ${value}`);
    return this;
  }

  orderBy(field: keyof T, direction: 'ASC' | 'DESC' = 'ASC'): this {
    this.orderByField = field;
    return this;
  }

  build(): string {
    const fields = this.selectedFields.length
      ? this.selectedFields.join(', ')
      : '*';
    let query = `SELECT ${fields} FROM table`;
    if (this.conditions.length) {
      query += ` WHERE ${this.conditions.join(' AND ')}`;
    }
    return query;
  }
}

interface Product {
  id: number;
  name: string;
  price: number;
  category: string;
}

const query = new QueryBuilder<Product>()
  .select('name', 'price')
  .where('category', 'electronics')
  .build();
```

### Pattern 3: Factory with Generic Return Types

```typescript
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
  timestamp: Date;
}

function createSuccessResponse<T>(data: T): ApiResponse<T> {
  return {
    data,
    status: 200,
    message: 'Success',
    timestamp: new Date(),
  };
}

function createErrorResponse<T = never>(
  status: number,
  message: string
): ApiResponse<T> {
  return {
    data: undefined as T,
    status,
    message,
    timestamp: new Date(),
  };
}

// Type is automatically inferred
const response = createSuccessResponse({ users: ['Alice', 'Bob'] });
// ApiResponse<{ users: string[] }>
```

### Pattern 4: Generic Higher-Order Functions

```typescript
// Memoize any function
function memoize<Args extends unknown[], Result>(
  fn: (...args: Args) => Result
): (...args: Args) => Result {
  const cache = new Map<string, Result>();

  return (...args: Args): Result => {
    const key = JSON.stringify(args);
    if (cache.has(key)) {
      return cache.get(key)!;
    }
    const result = fn(...args);
    cache.set(key, result);
    return result;
  };
}

const expensiveCalc = (x: number, y: number): number => {
  console.log('Computing...');
  return x * y;
};

const memoized = memoize(expensiveCalc);
memoized(2, 3); // "Computing..." → 6
memoized(2, 3); // 6 (cached, no log)
```

## Generic Default Types

```typescript
interface PaginatedResponse<T, Meta = { total: number; page: number }> {
  items: T[];
  meta: Meta;
}

// Uses default Meta
const response: PaginatedResponse<User> = {
  items: [],
  meta: { total: 0, page: 1 },
};

// Custom Meta
const customResponse: PaginatedResponse<User, { cursor: string }> = {
  items: [],
  meta: { cursor: 'abc123' },
};
```

## Practice Exercises

### Exercise 1: Implement `ObjectKeys<T>`
```typescript
// Create a type that extracts all keys of T as a union of string literals
type ObjectKeys<T> = ???;

interface User { name: string; age: number; email: string; }
type UserKeys = ObjectKeys<User>; // "name" | "age" | "email"
```

### Exercise 2: Type-Safe Dictionary
```typescript
// Implement a Dictionary class that:
// 1. Maps string keys to values of type T
// 2. Has get/set/has/delete methods
// 3. Has a map method that transforms values
// dictionary.map<U>(fn: (value: T) => U): Dictionary<U>
```

### Exercise 3: Generic Pipe Function
```typescript
// Implement a pipe function that chains transformations
// pipe(5, double, addOne, toString) → "11"
// Each function's input type must match the previous function's output type
```

## Key Takeaways

1. **Generics preserve type information** through function calls and data transformations
2. **Constraints (`extends`)** limit what types can be used while maintaining type safety
3. **`keyof` + generics** = type-safe property access
4. **Generic defaults** reduce boilerplate for common use cases
5. **Real-world patterns**: Event emitters, builders, factories, HOFs all benefit from generics

## Interview Quick-Fire

| Question | Answer |
|----------|--------|
| What problem do generics solve? | Reusable code that preserves type information |
| `T extends U` meaning? | T must be assignable to U (constraint) |
| Generic vs `any`? | Generics preserve type info; `any` loses it |
| Can you have generic arrow functions in TSX? | Yes, use `<T extends unknown>` or `<T,>` |
| Generic default type? | `<T = DefaultType>` — used when T not specified |
