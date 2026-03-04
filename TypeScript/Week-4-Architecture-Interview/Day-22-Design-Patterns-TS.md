# Day 22: Design Patterns in TypeScript

## Creational Patterns

### Singleton (Thread-Safe)

```typescript
class DatabaseConnection {
  private static instance: DatabaseConnection | null = null;
  private constructor(private connectionString: string) {}

  static getInstance(connectionString?: string): DatabaseConnection {
    if (!DatabaseConnection.instance) {
      DatabaseConnection.instance = new DatabaseConnection(
        connectionString ?? 'default-connection'
      );
    }
    return DatabaseConnection.instance;
  }

  query(sql: string): Promise<any[]> {
    console.log(`Executing: ${sql}`);
    return Promise.resolve([]);
  }
}

// Modern alternative: Module-scoped singleton
// db.ts
let instance: DatabaseConnection | null = null;
export function getDB(): DatabaseConnection {
  if (!instance) instance = DatabaseConnection.getInstance();
  return instance;
}
```

### Factory Pattern

```typescript
interface Notification {
  send(to: string, message: string): Promise<void>;
}

class EmailNotification implements Notification {
  async send(to: string, message: string) {
    console.log(`Email to ${to}: ${message}`);
  }
}

class SMSNotification implements Notification {
  async send(to: string, message: string) {
    console.log(`SMS to ${to}: ${message}`);
  }
}

class PushNotification implements Notification {
  async send(to: string, message: string) {
    console.log(`Push to ${to}: ${message}`);
  }
}

type NotificationType = 'email' | 'sms' | 'push';

// Type-safe factory with exhaustive mapping
const notificationFactories: Record<NotificationType, () => Notification> = {
  email: () => new EmailNotification(),
  sms: () => new SMSNotification(),
  push: () => new PushNotification(),
};

function createNotification(type: NotificationType): Notification {
  return notificationFactories[type]();
}
```

### Builder Pattern (Fluent API)

```typescript
interface QueryConfig {
  table: string;
  fields: string[];
  conditions: string[];
  orderBy?: { field: string; direction: 'ASC' | 'DESC' };
  limit?: number;
  offset?: number;
}

class QueryBuilder {
  private config: QueryConfig;

  constructor(table: string) {
    this.config = { table, fields: [], conditions: [] };
  }

  select(...fields: string[]): this {
    this.config.fields = fields;
    return this;
  }

  where(condition: string): this {
    this.config.conditions.push(condition);
    return this;
  }

  orderBy(field: string, direction: 'ASC' | 'DESC' = 'ASC'): this {
    this.config.orderBy = { field, direction };
    return this;
  }

  limit(n: number): this {
    this.config.limit = n;
    return this;
  }

  offset(n: number): this {
    this.config.offset = n;
    return this;
  }

  build(): string {
    const fields = this.config.fields.length ? this.config.fields.join(', ') : '*';
    let sql = `SELECT ${fields} FROM ${this.config.table}`;
    if (this.config.conditions.length) {
      sql += ` WHERE ${this.config.conditions.join(' AND ')}`;
    }
    if (this.config.orderBy) {
      sql += ` ORDER BY ${this.config.orderBy.field} ${this.config.orderBy.direction}`;
    }
    if (this.config.limit) sql += ` LIMIT ${this.config.limit}`;
    if (this.config.offset) sql += ` OFFSET ${this.config.offset}`;
    return sql;
  }
}

// Usage
const query = new QueryBuilder('users')
  .select('name', 'email')
  .where('active = true')
  .where('role = "admin"')
  .orderBy('name', 'ASC')
  .limit(10)
  .build();
```

## Structural Patterns

### Strategy Pattern

```typescript
interface CompressionStrategy {
  compress(data: Buffer): Buffer;
  decompress(data: Buffer): Buffer;
}

class GzipStrategy implements CompressionStrategy {
  compress(data: Buffer): Buffer { /* gzip compression */ return data; }
  decompress(data: Buffer): Buffer { /* gzip decompression */ return data; }
}

class BrotliStrategy implements CompressionStrategy {
  compress(data: Buffer): Buffer { /* brotli compression */ return data; }
  decompress(data: Buffer): Buffer { /* brotli decompression */ return data; }
}

class FileProcessor {
  constructor(private strategy: CompressionStrategy) {}

  setStrategy(strategy: CompressionStrategy): void {
    this.strategy = strategy;
  }

  processFile(data: Buffer): Buffer {
    return this.strategy.compress(data);
  }
}

// Runtime strategy switching
const processor = new FileProcessor(new GzipStrategy());
processor.processFile(Buffer.from('data'));
processor.setStrategy(new BrotliStrategy());
processor.processFile(Buffer.from('data'));
```

### Observer Pattern (Type-Safe)

```typescript
type EventMap = Record<string, any>;

class TypedEventEmitter<T extends EventMap> {
  private listeners = new Map<keyof T, Set<(data: any) => void>>();

  on<K extends keyof T>(event: K, handler: (data: T[K]) => void): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(handler);

    // Return unsubscribe function
    return () => this.listeners.get(event)?.delete(handler);
  }

  emit<K extends keyof T>(event: K, data: T[K]): void {
    this.listeners.get(event)?.forEach(handler => handler(data));
  }
}

// Usage
interface AppEvents {
  userLogin: { userId: string; timestamp: Date };
  userLogout: { userId: string };
  error: { code: number; message: string };
}

const events = new TypedEventEmitter<AppEvents>();
const unsub = events.on('userLogin', ({ userId, timestamp }) => {
  console.log(`${userId} logged in at ${timestamp}`);
});

events.emit('userLogin', { userId: '123', timestamp: new Date() });
unsub(); // Unsubscribe
```

### Adapter Pattern

```typescript
// Legacy payment system
interface LegacyPayment {
  processPayment(amount: number, currency: string): boolean;
}

// New payment interface
interface ModernPayment {
  charge(request: { amount: number; currency: string; metadata?: Record<string, string> }): Promise<{ success: boolean; transactionId: string }>;
}

// Adapter
class PaymentAdapter implements ModernPayment {
  constructor(private legacy: LegacyPayment) {}

  async charge(request: { amount: number; currency: string }) {
    const success = this.legacy.processPayment(request.amount, request.currency);
    return {
      success,
      transactionId: success ? crypto.randomUUID() : '',
    };
  }
}
```

## Behavioral Patterns

### Command Pattern

```typescript
interface Command {
  execute(): void;
  undo(): void;
}

class TextEditor {
  content = '';

  append(text: string) { this.content += text; }
  removeLast(count: number) { this.content = this.content.slice(0, -count); }
}

class AppendCommand implements Command {
  constructor(private editor: TextEditor, private text: string) {}

  execute() { this.editor.append(this.text); }
  undo() { this.editor.removeLast(this.text.length); }
}

class CommandHistory {
  private history: Command[] = [];
  private current = -1;

  execute(command: Command): void {
    // Remove future history on new command
    this.history = this.history.slice(0, this.current + 1);
    command.execute();
    this.history.push(command);
    this.current++;
  }

  undo(): void {
    if (this.current >= 0) {
      this.history[this.current].undo();
      this.current--;
    }
  }

  redo(): void {
    if (this.current < this.history.length - 1) {
      this.current++;
      this.history[this.current].execute();
    }
  }
}
```

## Key Takeaways

1. **Factory** → Use when object creation logic is complex or varies by type
2. **Builder** → Use for objects with many optional parameters
3. **Strategy** → Use when algorithms need to be swappable at runtime
4. **Observer** → Use for event-driven, decoupled communication
5. **TypeScript generics** make all patterns more type-safe than in plain JS
