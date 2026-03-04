# Day 15: Decorators (Stage 3 / TC39) — TypeScript 5+

## Decorator Overview

Decorators are functions that modify classes, methods, properties, or parameters. TypeScript 5+ supports the **TC39 Stage 3** decorator spec.

## TC39 Decorators (TypeScript 5+)

### Class Decorators

```typescript
// Simple class decorator
function sealed(target: Function, context: ClassDecoratorContext) {
  Object.seal(target);
  Object.seal(target.prototype);
}

@sealed
class User {
  name: string;
  constructor(name: string) {
    this.name = name;
  }
}

// Class decorator with metadata
function entity(tableName: string) {
  return function (target: Function, context: ClassDecoratorContext) {
    (target as any).tableName = tableName;
  };
}

@entity('users')
class User {
  id!: number;
  name!: string;
}
```

### Method Decorators

```typescript
function log(
  target: any,
  context: ClassMethodDecoratorContext
) {
  const methodName = String(context.name);

  return function (this: any, ...args: any[]) {
    console.log(`→ ${methodName}(${args.join(', ')})`);
    const result = target.call(this, ...args);
    console.log(`← ${methodName} returned:`, result);
    return result;
  };
}

class Calculator {
  @log
  add(a: number, b: number): number {
    return a + b;
  }
}

const calc = new Calculator();
calc.add(2, 3);
// → add(2, 3)
// ← add returned: 5
```

### Decorator Factories (Parameterized)

```typescript
function validateRange(min: number, max: number) {
  return function (
    target: any,
    context: ClassMethodDecoratorContext
  ) {
    return function (this: any, ...args: any[]) {
      for (const arg of args) {
        if (typeof arg === 'number' && (arg < min || arg > max)) {
          throw new RangeError(`Argument ${arg} out of range [${min}, ${max}]`);
        }
      }
      return target.call(this, ...args);
    };
  };
}

class MathService {
  @validateRange(0, 100)
  calculatePercentage(value: number): string {
    return `${value}%`;
  }
}
```

### Field Decorators

```typescript
function defaultValue<T>(value: T) {
  return function (
    _target: undefined,
    context: ClassFieldDecoratorContext
  ) {
    return function (initialValue: T): T {
      return initialValue ?? value;
    };
  };
}

class Settings {
  @defaultValue('localhost')
  host!: string;

  @defaultValue(3000)
  port!: number;

  @defaultValue(false)
  debug!: boolean;
}
```

### Accessor Decorators

```typescript
function bound(
  target: any,
  context: ClassMethodDecoratorContext
) {
  context.addInitializer(function (this: any) {
    this[context.name] = this[context.name].bind(this);
  });
}

class Button {
  label = 'Click me';

  @bound
  handleClick() {
    console.log(this.label); // Always correct 'this'
  }
}

const btn = new Button();
const handler = btn.handleClick;
handler(); // "Click me" — 'this' is bound correctly
```

## Experimental Decorators (Legacy — Angular)

Angular still uses the older experimental decorator syntax:

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true
  }
}

// Experimental decorators have different signatures
function Component(config: { selector: string; template: string }) {
  return function (constructor: Function) {
    Object.defineProperty(constructor, 'metadata', { value: config });
  };
}

@Component({
  selector: 'app-root',
  template: '<h1>Hello</h1>',
})
class AppComponent { }
```

## Real-World Decorator Patterns

### Pattern 1: Auto-Retry

```typescript
function retry(attempts: number = 3, delay: number = 1000) {
  return function (
    target: any,
    context: ClassMethodDecoratorContext
  ) {
    return async function (this: any, ...args: any[]) {
      for (let i = 0; i < attempts; i++) {
        try {
          return await target.call(this, ...args);
        } catch (error) {
          if (i === attempts - 1) throw error;
          await new Promise(r => setTimeout(r, delay * (i + 1)));
        }
      }
    };
  };
}

class ApiClient {
  @retry(3, 1000)
  async fetchData(url: string) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  }
}
```

### Pattern 2: Caching / Memoization

```typescript
function memoize(
  target: any,
  context: ClassMethodDecoratorContext
) {
  const cache = new Map<string, any>();

  return function (this: any, ...args: any[]) {
    const key = JSON.stringify(args);
    if (cache.has(key)) return cache.get(key);
    const result = target.call(this, ...args);
    cache.set(key, result);
    return result;
  };
}

class MathService {
  @memoize
  fibonacci(n: number): number {
    if (n <= 1) return n;
    return this.fibonacci(n - 1) + this.fibonacci(n - 2);
  }
}
```

### Pattern 3: Dependency Injection (Simplified)

```typescript
const container = new Map<string, any>();

function injectable(
  target: any,
  context: ClassDecoratorContext
) {
  container.set(String(context.name), new target());
}

function inject(token: string) {
  return function (
    _target: undefined,
    context: ClassFieldDecoratorContext
  ) {
    return function () {
      return container.get(token);
    };
  };
}

@injectable
class Logger {
  log(msg: string) { console.log(msg); }
}

class UserService {
  @inject('Logger')
  logger!: Logger;

  createUser(name: string) {
    this.logger.log(`Creating user: ${name}`);
  }
}
```

## Key Takeaways

1. **TC39 Stage 3 decorators** (TS 5+) are the future — different API from experimental
2. **Angular** still uses experimental decorators with `emitDecoratorMetadata`
3. **Method decorators** wrap the original method — great for cross-cutting concerns
4. **`context.addInitializer`** runs code during class instantiation
5. **Common patterns**: logging, retry, memoization, validation, DI

## Interview Quick-Fire

| Question | Answer |
|----------|--------|
| TC39 vs experimental decorators? | TC39 (Stage 3) is standard; experimental is TS-specific legacy |
| Can decorators modify class shape? | TC39: limited; Experimental: yes via metadata reflection |
| Execution order of multiple decorators? | Bottom-up (closest to declaration first) |
| What does `emitDecoratorMetadata` do? | Emits design-time type metadata for experimental decorators |
| Name 3 decorator use cases | Logging, caching/memoization, validation, DI, authorization |
