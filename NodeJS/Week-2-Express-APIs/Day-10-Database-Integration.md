# Day 10: Database Integration (MongoDB & PostgreSQL)

## 🎯 Learning Objectives
- Connect Node.js to MongoDB with Mongoose
- Connect Node.js to PostgreSQL with Sequelize/Knex
- Understand ORMs vs Query Builders vs Raw SQL
- Implement connection pooling and transactions

---

## 📚 MongoDB with Mongoose

### Connection Setup

```javascript
const mongoose = require('mongoose');

async function connectDB() {
  try {
    await mongoose.connect(process.env.MONGODB_URI, {
      maxPoolSize: 10,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
    });
    console.log('MongoDB connected');
  } catch (err) {
    console.error('MongoDB connection error:', err);
    process.exit(1);
  }
}

// Connection events
mongoose.connection.on('disconnected', () => console.log('MongoDB disconnected'));
mongoose.connection.on('error', (err) => console.error('MongoDB error:', err));

// Graceful shutdown
process.on('SIGTERM', async () => {
  await mongoose.connection.close();
  process.exit(0);
});
```

### Schema & Model Definition

```javascript
const mongoose = require('mongoose');
const bcrypt = require('bcrypt');

const userSchema = new mongoose.Schema({
  name: {
    type: String,
    required: [true, 'Name is required'],
    trim: true,
    minlength: [2, 'Name must be at least 2 characters']
  },
  email: {
    type: String,
    required: true,
    unique: true,
    lowercase: true,
    match: [/^\S+@\S+\.\S+$/, 'Invalid email format']
  },
  password: {
    type: String,
    required: true,
    minlength: 8,
    select: false // Exclude from queries by default
  },
  role: {
    type: String,
    enum: ['user', 'admin', 'moderator'],
    default: 'user'
  },
  posts: [{ type: mongoose.Schema.Types.ObjectId, ref: 'Post' }],
  profile: {
    bio: { type: String, maxlength: 500 },
    avatar: String,
    socialLinks: { type: Map, of: String }
  }
}, {
  timestamps: true, // adds createdAt, updatedAt
  toJSON: { virtuals: true, transform: (_, ret) => { delete ret.__v; return ret; } }
});

// Indexes
userSchema.index({ email: 1 });
userSchema.index({ name: 'text', 'profile.bio': 'text' }); // Text search

// Virtual fields
userSchema.virtual('postCount').get(function() {
  return this.posts?.length || 0;
});

// Pre-save hook (hash password)
userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  this.password = await bcrypt.hash(this.password, 12);
  next();
});

// Instance method
userSchema.methods.comparePassword = async function(candidatePassword) {
  return bcrypt.compare(candidatePassword, this.password);
};

// Static method
userSchema.statics.findByEmail = function(email) {
  return this.findOne({ email: email.toLowerCase() });
};

const User = mongoose.model('User', userSchema);
module.exports = User;
```

### CRUD with Mongoose

```javascript
// Create
const user = await User.create({ name: 'Alice', email: 'alice@example.com', password: 'secret123' });

// Read (with filtering, pagination, population)
const users = await User.find({ role: 'user' })
  .select('name email role createdAt')
  .sort({ createdAt: -1 })
  .skip(0)
  .limit(20)
  .populate('posts', 'title createdAt')
  .lean(); // Returns plain objects (faster, no Mongoose overhead)

// Update
const updated = await User.findByIdAndUpdate(
  id,
  { $set: { name: 'Bob', 'profile.bio': 'Developer' } },
  { new: true, runValidators: true }
);

// Delete
await User.findByIdAndDelete(id);

// Aggregation pipeline
const stats = await User.aggregate([
  { $match: { role: 'user' } },
  { $group: { _id: '$role', count: { $sum: 1 }, avgPosts: { $avg: { $size: '$posts' } } } },
  { $sort: { count: -1 } }
]);
```

---

## 🐘 PostgreSQL with Knex.js

### Setup

```javascript
const knex = require('knex');

const db = knex({
  client: 'pg',
  connection: {
    host: process.env.PG_HOST,
    port: process.env.PG_PORT || 5432,
    user: process.env.PG_USER,
    password: process.env.PG_PASSWORD,
    database: process.env.PG_DATABASE,
    ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
  },
  pool: { min: 2, max: 10 },
  migrations: { directory: './migrations' }
});

module.exports = db;
```

### Migrations

```javascript
// migrations/20240101_create_users.js
exports.up = function(knex) {
  return knex.schema.createTable('users', (table) => {
    table.uuid('id').primary().defaultTo(knex.fn.uuid());
    table.string('name', 100).notNullable();
    table.string('email', 255).notNullable().unique();
    table.string('password_hash', 255).notNullable();
    table.enum('role', ['user', 'admin', 'moderator']).defaultTo('user');
    table.jsonb('profile').defaultTo('{}');
    table.timestamps(true, true); // created_at, updated_at
    
    table.index(['email']);
    table.index(['role']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('users');
};

// Run: npx knex migrate:latest
```

### Query Building

```javascript
// Insert
const [user] = await db('users')
  .insert({ name: 'Alice', email: 'alice@example.com', password_hash: hash })
  .returning('*');

// Select with joins
const posts = await db('posts')
  .join('users', 'posts.author_id', 'users.id')
  .select('posts.*', 'users.name as author_name')
  .where('posts.status', 'published')
  .orderBy('posts.created_at', 'desc')
  .limit(20)
  .offset(0);

// Transactions
const trx = await db.transaction();
try {
  const [order] = await trx('orders').insert({ user_id: userId, total: 99.99 }).returning('*');
  await trx('order_items').insert(items.map(i => ({ ...i, order_id: order.id })));
  await trx('inventory').where('product_id', productId).decrement('quantity', 1);
  await trx.commit();
} catch (err) {
  await trx.rollback();
  throw err;
}

// Raw SQL when needed
const result = await db.raw(`
  SELECT u.name, COUNT(p.id) as post_count
  FROM users u
  LEFT JOIN posts p ON p.author_id = u.id
  WHERE u.created_at > ?
  GROUP BY u.id
  HAVING COUNT(p.id) > ?
  ORDER BY post_count DESC
`, [startDate, minPosts]);
```

---

## 🔄 Connection Pooling

```javascript
// Why pooling matters:
// Without pool: Each query = new TCP connection (expensive: DNS + TCP + TLS + auth)
// With pool: Reuse existing connections from a pool

// PostgreSQL with pg-pool
const { Pool } = require('pg');
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 20,                    // Max connections in pool
  idleTimeoutMillis: 30000,   // Close idle connections after 30s
  connectionTimeoutMillis: 2000, // Error if can't connect in 2s
});

// Monitor pool
pool.on('connect', () => console.log('New connection created'));
pool.on('error', (err) => console.error('Pool error:', err));

// Use pool
const { rows } = await pool.query('SELECT * FROM users WHERE id = $1', [userId]);

// Check pool status
console.log({
  total: pool.totalCount,
  idle: pool.idleCount,
  waiting: pool.waitingCount
});
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is an ORM and what are its pros and cons?**

ORM (Object-Relational Mapping) maps database tables to code objects (Mongoose, Sequelize, Prisma). Pros: type safety, easier migrations, database-agnostic, less SQL to write. Cons: N+1 queries, inefficient complex queries, learning curve, abstracts away performance tuning. Use query builders (Knex) for more control.

**Q2: What is connection pooling and why is it important?**

A connection pool maintains a set of reusable database connections. Instead of creating/destroying connections per query (expensive), queries grab from the pool and return when done. This reduces latency, limits database connections, and handles concurrent requests efficiently.

**Q3: What is the difference between SQL and NoSQL databases?**

SQL (PostgreSQL, MySQL): structured schemas, ACID transactions, joins, strong consistency. NoSQL (MongoDB, Redis): flexible schemas, horizontal scaling, eventual consistency, document/key-value/graph models. Choose based on data relationships, consistency needs, and scaling requirements.

### Intermediate

**Q4: How do you prevent N+1 query problems?**

N+1: loading 100 users then 100 separate queries for their posts. Solutions: (1) Mongoose: `.populate()` or `$lookup` aggregation. (2) SQL: JOIN queries or batch loading (`WHERE id IN (...)`). (3) DataLoader pattern (batches and deduplicates). Always monitor query counts in development.

**Q5: Explain database transactions and when to use them.**

Transactions group multiple operations into an atomic unit — all succeed or all rollback. Use for: transferring money, creating orders with items, any multi-step operation where partial completion is invalid. ACID properties: Atomicity, Consistency, Isolation, Durability. Be aware of isolation levels and deadlocks.

**Q6: How do you handle database migrations in production?**

Use migration tools (Knex, Prisma Migrate, db-migrate). Rules: migrations are sequential, never modify existing migrations, test rollback. For zero-downtime: (1) backward-compatible schema changes only, (2) multi-phase migrations (add column → deploy code → remove old column), (3) run migrations before deploying new code.

### Advanced

**Q7: How would you implement read replicas with Node.js?**

Create separate connection pools for primary (writes) and replicas (reads). Route queries based on operation type. Handle replication lag (reads immediately after writes may hit stale replica). Options: manual routing, middleware that detects read/write, or ORMs with built-in replica support (Sequelize). Use sticky sessions when consistency is critical.

**Q8: How do you handle database connection failures gracefully?**

Implement: (1) Retry logic with exponential backoff on initial connection. (2) Circuit breaker for repeated failures. (3) Health check endpoint that verifies DB connectivity. (4) Queue writes during outages (if applicable). (5) Graceful degradation (serve cached data). (6) Connection pool error events with alerting.

**Q9: Compare Prisma, Sequelize, and Knex for a production Node.js application.**

Prisma: type-safe, excellent DX, schema-first, auto-generated client. Limitation: less flexible for raw queries. Sequelize: full ORM, mature, associations. Limitation: complex API, performance overhead. Knex: query builder only, full SQL control, lightweight. Choose: Prisma for new TypeScript projects, Knex for complex queries, Sequelize for existing projects.

---

## 🛠️ Hands-on Exercise

Build a user management system with:
1. MongoDB for user profiles (flexible schema)
2. PostgreSQL for transactions/orders (ACID)
3. Connection pooling for both
4. Migrations for PostgreSQL schema
5. Transaction example (create order + update inventory)
