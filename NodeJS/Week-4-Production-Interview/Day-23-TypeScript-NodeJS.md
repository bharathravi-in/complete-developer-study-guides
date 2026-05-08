# Day 23: TypeScript with Node.js

## 🎯 Learning Objectives
- Set up TypeScript for Node.js projects
- Type Express routes, middleware, and services
- Use generics, utility types, and advanced patterns
- Configure tsconfig for production builds

---

## 📚 TypeScript Setup

### Configuration

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "paths": {
      "@/*": ["./src/*"],
      "@config/*": ["./src/config/*"],
      "@services/*": ["./src/services/*"]
    }
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "**/*.test.ts"]
}
```

### Typed Express Application

```typescript
import express, { Request, Response, NextFunction } from 'express';

// Extend Request type
interface AuthRequest extends Request {
  user?: {
    id: string;
    role: 'admin' | 'user' | 'moderator';
    email: string;
  };
}

// Typed route params and response
interface UserParams { id: string; }
interface UserResponse { data: User; }
interface CreateUserBody { name: string; email: string; password: string; }

const router = express.Router();

router.get('/users/:id', async (req: Request<UserParams>, res: Response<UserResponse>) => {
  const user = await userService.findById(req.params.id);
  res.json({ data: user });
});

router.post('/users', async (req: Request<{}, {}, CreateUserBody>, res: Response) => {
  const user = await userService.create(req.body);
  res.status(201).json({ data: user });
});

// Typed middleware
function authenticate(req: AuthRequest, res: Response, next: NextFunction): void {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) { res.status(401).json({ error: 'Unauthorized' }); return; }
  req.user = verifyToken(token);
  next();
}

function authorize(...roles: string[]) {
  return (req: AuthRequest, res: Response, next: NextFunction): void => {
    if (!req.user || !roles.includes(req.user.role)) {
      res.status(403).json({ error: 'Forbidden' }); return;
    }
    next();
  };
}
```

### Service Layer Types

```typescript
// types/user.ts
export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  createdAt: Date;
  updatedAt: Date;
}

export type UserRole = 'admin' | 'user' | 'moderator';

export interface CreateUserDTO {
  name: string;
  email: string;
  password: string;
  role?: UserRole;
}

export interface UpdateUserDTO {
  name?: string;
  email?: string;
}

export interface PaginatedResult<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    hasNext: boolean;
  };
}

// services/userService.ts
export class UserService {
  constructor(private readonly userRepo: IUserRepository) {}

  async findAll(page: number, limit: number): Promise<PaginatedResult<User>> {
    const [users, total] = await this.userRepo.findAndCount(page, limit);
    return {
      data: users,
      pagination: { page, limit, total, hasNext: page * limit < total }
    };
  }

  async create(dto: CreateUserDTO): Promise<User> {
    const exists = await this.userRepo.findByEmail(dto.email);
    if (exists) throw new ConflictError('Email already registered');
    return this.userRepo.create(dto);
  }
}

// Repository interface (dependency inversion)
export interface IUserRepository {
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
  findAndCount(page: number, limit: number): Promise<[User[], number]>;
  create(data: CreateUserDTO): Promise<User>;
  update(id: string, data: UpdateUserDTO): Promise<User>;
  delete(id: string): Promise<void>;
}
```

### Advanced Type Patterns

```typescript
// Branded types (prevent mixing similar types)
type UserId = string & { __brand: 'UserId' };
type PostId = string & { __brand: 'PostId' };

function createUserId(id: string): UserId { return id as UserId; }

// Result type (no exceptions)
type Result<T, E = Error> = { success: true; data: T } | { success: false; error: E };

async function safeParse<T>(promise: Promise<T>): Promise<Result<T>> {
  try {
    const data = await promise;
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error as Error };
  }
}

// Type-safe event emitter
interface Events {
  'user:created': { userId: string; email: string };
  'user:deleted': { userId: string };
  'order:placed': { orderId: string; amount: number };
}

class TypedEmitter<T extends Record<string, unknown>> {
  private handlers = new Map<string, Function[]>();
  
  on<K extends keyof T>(event: K, handler: (data: T[K]) => void): void {
    const list = this.handlers.get(event as string) || [];
    list.push(handler);
    this.handlers.set(event as string, list);
  }
  
  emit<K extends keyof T>(event: K, data: T[K]): void {
    this.handlers.get(event as string)?.forEach(fn => fn(data));
  }
}

const emitter = new TypedEmitter<Events>();
emitter.on('user:created', ({ userId, email }) => {}); // ✅ Type-safe
emitter.emit('user:created', { userId: '1', email: 'a@b.com' }); // ✅
```

---

## 🧪 Interview Questions

### Beginner
**Q1: Why use TypeScript with Node.js?**
TypeScript adds static types → catch errors at compile time, better IDE support (autocomplete, refactoring), self-documenting code, safer refactoring. In Node.js: typed request/response objects, typed database models, typed service interfaces. Drawback: build step required, slight learning curve.

**Q2: How do you configure TypeScript for a Node.js project?**
Install: `typescript`, `@types/node`, `@types/express`. Create `tsconfig.json` with target ES2022, module NodeNext, strict mode. Add build script: `tsc`. Dev: use `tsx` or `ts-node` for development. Production: compile to JS, deploy only `dist/`.

**Q3: What is the difference between `interface` and `type` in TypeScript?**
Both define object shapes. Interfaces: extendable (declaration merging), better for objects/classes. Types: more flexible (unions, intersections, mapped types, conditional types). Use interfaces for public APIs and class shapes. Use types for complex type operations. Performance: virtually identical.

### Intermediate
**Q4: How do you type Express middleware and request handlers?**
Use generic `Request<Params, ResBody, ReqBody, Query>`. Create custom interfaces extending `Request` for auth (`req.user`). Type middleware with `(req, res, next) => void`. Use `Response<T>` for typed responses. Create utility types: `AsyncHandler`, `TypedRouter`.

**Q5: What are generics and when do you use them in Node.js services?**
Generics are type parameters that make code reusable across types. Use for: repository pattern (`IRepository<T>`), paginated results (`PaginatedResult<T>`), API responses (`ApiResponse<T>`), service methods that work with multiple models. They provide type safety without duplicating code.

**Q6: How do you handle runtime type validation when TypeScript types don't exist at runtime?**
TypeScript types are erased at compile time. For runtime validation: use Zod (infer types from schemas), Joi (validate then cast), class-validator (decorators). Pattern: define Zod schema → infer TypeScript type → validate at API boundary → use inferred type internally. This ensures runtime safety matches compile-time types.

### Advanced
**Q7: How do you implement the repository pattern with TypeScript generics?**
Define `IRepository<T>` interface with CRUD methods typed to T. Create `BaseRepository<T>` implementing common logic. Each model gets a typed repository: `class UserRepository extends BaseRepository<User>`. Use dependency injection (constructor injection) for testability. Type the factory/container to ensure correct types.

**Q8: Explain conditional types and how they're useful in API design.**
Conditional types: `T extends U ? X : Y`. Use for: response type based on query params (`include=posts` → return User with posts), endpoint return types, API versioning types. Example: `type Response<T, Include> = Include extends 'full' ? T & { relations: ... } : T`.

**Q9: How would you design a type-safe event system for a Node.js microservice?**
Define event map interface (event names → payload types). Create generic EventBus class parameterized by the event map. `publish<K>()` and `subscribe<K>()` are generic over the event name, ensuring payload types match. Use discriminated unions for event routing. Combine with Zod for runtime validation at service boundaries.

---

## 🛠️ Hands-on Exercise
Build a fully typed Express API:
1. TypeScript project setup with path aliases
2. Typed routes, middleware, and services
3. Generic repository pattern
4. Zod validation with inferred types
5. Type-safe event emitter
6. Build configuration for production
