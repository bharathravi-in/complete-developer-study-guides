# Day 26: Design Patterns in Node.js

## 🎯 Learning Objectives
- Implement creational, structural, and behavioral patterns
- Apply patterns to real Node.js problems
- Understand when to use (and not use) each pattern
- Recognize patterns in popular frameworks

---

## 📚 Creational Patterns

### Singleton (Module-level)

```javascript
// In Node.js, modules are cached — singletons by default
// database.js
class Database {
  constructor() {
    if (Database.instance) return Database.instance;
    this.connection = null;
    Database.instance = this;
  }

  async connect(url) {
    if (!this.connection) {
      this.connection = await createConnection(url);
    }
    return this.connection;
  }
}

module.exports = new Database(); // Same instance everywhere

// More idiomatic Node.js singleton:
let connection;
module.exports = {
  async getConnection() {
    if (!connection) {
      connection = await createConnection(process.env.DB_URL);
    }
    return connection;
  }
};
```

### Factory Pattern

```javascript
// Notification factory
class NotificationFactory {
  static create(type, config) {
    switch (type) {
      case 'email': return new EmailNotification(config);
      case 'sms': return new SMSNotification(config);
      case 'push': return new PushNotification(config);
      case 'slack': return new SlackNotification(config);
      default: throw new Error(`Unknown notification type: ${type}`);
    }
  }
}

// Abstract factory for database adapters
class DatabaseFactory {
  static create(engine) {
    const factories = {
      postgres: () => new PostgresAdapter(),
      mongodb: () => new MongoAdapter(),
      mysql: () => new MySQLAdapter(),
    };
    const factory = factories[engine];
    if (!factory) throw new Error(`Unsupported engine: ${engine}`);
    return factory();
  }
}

// Usage
const db = DatabaseFactory.create(process.env.DB_ENGINE);
await db.connect();
await db.query('...');
```

### Builder Pattern

```javascript
class QueryBuilder {
  #table; #conditions = []; #orderBy; #limit; #offset; #joins = [];

  from(table) { this.#table = table; return this; }
  
  where(condition, value) {
    this.#conditions.push({ condition, value });
    return this;
  }

  join(table, on) {
    this.#joins.push({ table, on });
    return this;
  }

  orderBy(field, direction = 'ASC') { this.#orderBy = { field, direction }; return this; }
  limit(n) { this.#limit = n; return this; }
  offset(n) { this.#offset = n; return this; }

  build() {
    let query = `SELECT * FROM ${this.#table}`;
    const params = [];

    this.#joins.forEach(j => { query += ` JOIN ${j.table} ON ${j.on}`; });
    
    if (this.#conditions.length) {
      const clauses = this.#conditions.map((c, i) => {
        params.push(c.value);
        return c.condition.replace('?', `$${i + 1}`);
      });
      query += ` WHERE ${clauses.join(' AND ')}`;
    }
    
    if (this.#orderBy) query += ` ORDER BY ${this.#orderBy.field} ${this.#orderBy.direction}`;
    if (this.#limit) query += ` LIMIT ${this.#limit}`;
    if (this.#offset) query += ` OFFSET ${this.#offset}`;

    return { query, params };
  }
}

// Usage
const { query, params } = new QueryBuilder()
  .from('users')
  .where('age > ?', 18)
  .where('status = ?', 'active')
  .join('orders', 'orders.user_id = users.id')
  .orderBy('created_at', 'DESC')
  .limit(10)
  .offset(20)
  .build();
```

---

## 📚 Structural Patterns

### Proxy Pattern (Caching, Logging)

```javascript
// Caching proxy
function createCachingProxy(service, ttl = 60000) {
  const cache = new Map();

  return new Proxy(service, {
    get(target, prop) {
      const original = target[prop];
      if (typeof original !== 'function') return original;

      return async function (...args) {
        const key = `${prop}:${JSON.stringify(args)}`;
        const cached = cache.get(key);
        
        if (cached && Date.now() - cached.time < ttl) {
          return cached.value;
        }

        const result = await original.apply(target, args);
        cache.set(key, { value: result, time: Date.now() });
        return result;
      };
    }
  });
}

const userService = createCachingProxy(new UserService(), 30000);
await userService.findById('123'); // Hits DB
await userService.findById('123'); // Returns cached
```

### Decorator Pattern

```javascript
// Function decorators
function withRetry(fn, maxRetries = 3, delay = 1000) {
  return async function (...args) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await fn.apply(this, args);
      } catch (error) {
        if (attempt === maxRetries) throw error;
        await new Promise(r => setTimeout(r, delay * attempt));
      }
    }
  };
}

function withTimeout(fn, ms) {
  return async function (...args) {
    const result = fn.apply(this, args);
    const timeout = new Promise((_, reject) =>
      setTimeout(() => reject(new Error(`Timeout after ${ms}ms`)), ms)
    );
    return Promise.race([result, timeout]);
  };
}

function withLogging(fn, logger) {
  return async function (...args) {
    const start = Date.now();
    logger.info({ method: fn.name, args }, 'Calling');
    try {
      const result = await fn.apply(this, args);
      logger.info({ method: fn.name, duration: Date.now() - start }, 'Completed');
      return result;
    } catch (error) {
      logger.error({ method: fn.name, error, duration: Date.now() - start }, 'Failed');
      throw error;
    }
  };
}

// Compose decorators
const resilientFetch = withLogging(withRetry(withTimeout(fetch, 5000)), logger);
```

---

## 📚 Behavioral Patterns

### Strategy Pattern

```javascript
// Payment processing strategies
const paymentStrategies = {
  stripe: {
    async charge(amount, token) {
      return stripe.charges.create({ amount, currency: 'usd', source: token });
    }
  },
  paypal: {
    async charge(amount, token) {
      return paypal.payment.create({ amount, token });
    }
  },
  crypto: {
    async charge(amount, address) {
      return cryptoGateway.createPayment({ amount, address });
    }
  }
};

class PaymentService {
  constructor(strategy) { this.strategy = strategy; }
  setStrategy(strategy) { this.strategy = strategy; }
  async processPayment(amount, details) {
    return this.strategy.charge(amount, details);
  }
}

const payment = new PaymentService(paymentStrategies[user.preferredMethod]);
await payment.processPayment(9999, token);
```

### Observer/EventEmitter Pattern

```javascript
// Domain events with typed observer
class DomainEventBus {
  #handlers = new Map();

  subscribe(event, handler) {
    const handlers = this.#handlers.get(event) || [];
    handlers.push(handler);
    this.#handlers.set(event, handlers);
    return () => { // Unsubscribe function
      const idx = handlers.indexOf(handler);
      if (idx > -1) handlers.splice(idx, 1);
    };
  }

  async publish(event, data) {
    const handlers = this.#handlers.get(event) || [];
    await Promise.allSettled(handlers.map(h => h(data)));
  }
}

// Usage
const events = new DomainEventBus();
events.subscribe('order:created', async (order) => sendConfirmationEmail(order));
events.subscribe('order:created', async (order) => updateInventory(order));
events.subscribe('order:created', async (order) => notifyWarehouse(order));

await events.publish('order:created', { id: '123', items: [...] });
```

### Chain of Responsibility (Middleware)

```javascript
// Express middleware IS chain of responsibility
// Custom implementation:
class Pipeline {
  #middlewares = [];

  use(middleware) {
    this.#middlewares.push(middleware);
    return this;
  }

  async execute(context) {
    let index = 0;
    const next = async () => {
      if (index < this.#middlewares.length) {
        const middleware = this.#middlewares[index++];
        await middleware(context, next);
      }
    };
    await next();
    return context;
  }
}

// Usage
const pipeline = new Pipeline()
  .use(async (ctx, next) => { ctx.startTime = Date.now(); await next(); })
  .use(async (ctx, next) => { ctx.user = await authenticate(ctx.token); await next(); })
  .use(async (ctx, next) => { ctx.result = await processRequest(ctx); await next(); })
  .use(async (ctx, next) => { ctx.duration = Date.now() - ctx.startTime; });

await pipeline.execute({ token: 'abc', body: {} });
```

---

## 🧪 Interview Questions

### Beginner
**Q1: What is the Singleton pattern and how does Node.js handle it?**
Singleton ensures one instance exists. Node.js modules are cached after first `require()`, so `module.exports = new MyClass()` is inherently singleton. Useful for: database connections, config objects, loggers. Caveat: doesn't work across different `node_modules` copies.

**Q2: What is the Factory pattern? Give a Node.js example.**
Factory creates objects without specifying exact class. Caller says "I need a notification sender" and factory returns Email/SMS/Push instance based on config. Benefits: loose coupling, easy to add new types, centralizes creation logic. In Node.js: database adapters, transport layers, strategy selection.

**Q3: How is Express middleware an example of a design pattern?**
Chain of Responsibility: request passes through ordered middleware chain. Each middleware can: (1) process and call next(), (2) short-circuit (send response), (3) modify request/response. Also Decorator pattern: each middleware decorates the request object (add user, parse body, add headers).

### Intermediate
**Q4: When would you use the Strategy pattern in a Node.js application?**
When behavior needs to be interchangeable at runtime. Examples: payment gateways (Stripe/PayPal), file storage (S3/local/GCS), notification channels (email/SMS/push), sorting algorithms, authentication strategies (JWT/OAuth/API-key). Avoids large if/else chains, follows Open/Closed principle.

**Q5: Explain the Observer pattern and its relationship to EventEmitter.**
Observer: subjects notify observers of state changes. EventEmitter IS the Observer pattern in Node.js. Subject = emitter, observers = listeners. Decouples producers from consumers. Used everywhere: streams (data events), HTTP (request events), DOM (click events). Enables event-driven architecture.

**Q6: How would you implement the Repository pattern in Node.js?**
Repository abstracts data access behind an interface. Define interface (findById, create, update, delete). Implement for each database (PostgresUserRepo, MongoUserRepo). Service depends on interface, not implementation. Benefits: swap databases, easier testing (mock repo), single responsibility.

### Advanced
**Q7: How do you combine multiple patterns to build a resilient service layer?**
Combine: Factory (create services), Strategy (interchangeable implementations), Decorator (add retry/timeout/logging), Repository (data access), Observer (events). Example: `withRetry(withCircuitBreaker(withLogging(new PaymentService(stripeStrategy))))`. Each layer adds resilience without modifying core logic.

**Q8: How does the CQRS pattern apply to Node.js applications?**
CQRS: separate read and write models. Write: Command handlers → validate → update → emit event. Read: Event listeners → update read-optimized projections. In Node.js: different Express routes for commands (POST/PUT/DELETE) vs queries (GET). Different databases: write to PostgreSQL, read from Redis/Elasticsearch.

**Q9: Implement a plugin system using design patterns.**
Use Strategy + Observer + Factory. Plugin interface defines hooks (lifecycle methods). Plugin registry (factory) loads/instantiates plugins. Event bus (observer) notifies plugins of lifecycle events. Example: `app.use(plugin)` registers hooks. Pipeline (chain of responsibility) executes plugin hooks in order.

---

## 🛠️ Hands-on Exercise
Build a notification system using design patterns:
1. Factory: create notification channels (email/SMS/push/slack)
2. Strategy: select channel based on user preference
3. Observer: listen for domain events
4. Decorator: add retry, logging, rate limiting
5. Builder: construct complex notification payloads
6. Chain of Responsibility: validation pipeline
