# Day 16: Message Queues & Background Jobs (BullMQ, RabbitMQ)

## 🎯 Learning Objectives
- Understand message queue patterns
- Implement job queues with BullMQ (Redis-backed)
- Learn RabbitMQ fundamentals
- Handle retries, dead letters, and scheduling

---

## 📚 Why Message Queues?

```
Without Queue:                    With Queue:
User → API → Send Email (3s)     User → API → Queue → Response (50ms)
           → Process Image (5s)              ↓
           → Response (8s+ total)   Worker → Send Email
                                    Worker → Process Image
```

### Use Cases
- Email/notification sending
- Image/video processing
- Data imports/exports
- Scheduled tasks (cron-like)
- Webhook delivery with retries
- Decoupling microservices

---

## 🐂 BullMQ (Redis-backed Queue)

### Setup

```javascript
const { Queue, Worker, QueueScheduler } = require('bullmq');
const Redis = require('ioredis');

const connection = new Redis(process.env.REDIS_URL, { maxRetriesPerRequest: null });

// Create queue
const emailQueue = new Queue('email', { connection });
const imageQueue = new Queue('image-processing', { connection });
```

### Producing Jobs

```javascript
// Add a job
await emailQueue.add('welcome-email', {
  to: 'user@example.com',
  subject: 'Welcome!',
  template: 'welcome',
  data: { name: 'Alice' }
});

// Add with options
await emailQueue.add('password-reset', 
  { to: 'user@example.com', resetToken: 'abc123' },
  {
    priority: 1,              // Lower = higher priority
    attempts: 3,              // Retry 3 times
    backoff: { type: 'exponential', delay: 2000 }, // 2s, 4s, 8s
    removeOnComplete: 100,    // Keep last 100 completed
    removeOnFail: 500,        // Keep last 500 failed
  }
);

// Delayed job (send in 1 hour)
await emailQueue.add('reminder', data, { delay: 60 * 60 * 1000 });

// Scheduled/repeatable jobs (cron)
await emailQueue.add('daily-report', {}, {
  repeat: { cron: '0 9 * * *' } // Every day at 9 AM
});

// Bulk add
await emailQueue.addBulk([
  { name: 'welcome', data: { to: 'user1@test.com' } },
  { name: 'welcome', data: { to: 'user2@test.com' } },
  { name: 'welcome', data: { to: 'user3@test.com' } },
]);
```

### Processing Jobs (Workers)

```javascript
const worker = new Worker('email', async (job) => {
  console.log(`Processing ${job.name} (ID: ${job.id})`);
  
  switch (job.name) {
    case 'welcome-email':
      await sendEmail(job.data.to, job.data.subject, job.data.template, job.data.data);
      break;
    case 'password-reset':
      await sendPasswordResetEmail(job.data.to, job.data.resetToken);
      break;
    default:
      throw new Error(`Unknown job type: ${job.name}`);
  }
  
  // Return value stored as job result
  return { sent: true, timestamp: Date.now() };
}, {
  connection,
  concurrency: 5,           // Process 5 jobs simultaneously
  limiter: { max: 10, duration: 1000 }, // Rate limit: 10 jobs/second
});

// Event handlers
worker.on('completed', (job, result) => {
  console.log(`Job ${job.id} completed:`, result);
});

worker.on('failed', (job, err) => {
  console.error(`Job ${job.id} failed (attempt ${job.attemptsMade}):`, err.message);
  if (job.attemptsMade >= job.opts.attempts) {
    // Move to dead letter queue or alert
    alertOps(`Job ${job.id} permanently failed: ${err.message}`);
  }
});

worker.on('error', (err) => {
  console.error('Worker error:', err);
});
```

### Job Progress & Events

```javascript
// Report progress from worker
const imageWorker = new Worker('image-processing', async (job) => {
  const { imagePath, operations } = job.data;
  
  for (let i = 0; i < operations.length; i++) {
    await applyOperation(imagePath, operations[i]);
    await job.updateProgress(Math.round(((i + 1) / operations.length) * 100));
  }
  
  return { outputPath: '/processed/image.jpg' };
}, { connection });

// Monitor progress
const queueEvents = new QueueEvents('image-processing', { connection });
queueEvents.on('progress', ({ jobId, data }) => {
  console.log(`Job ${jobId}: ${data}% complete`);
  // Send progress update to client via WebSocket
  io.to(`job:${jobId}`).emit('progress', data);
});
```

---

## 🐰 RabbitMQ

### Connection & Publishing

```javascript
const amqp = require('amqplib');

async function setupRabbitMQ() {
  const connection = await amqp.connect(process.env.RABBITMQ_URL);
  const channel = await connection.createChannel();
  
  // Declare exchange and queues
  await channel.assertExchange('events', 'topic', { durable: true });
  await channel.assertQueue('user-events', { 
    durable: true,
    deadLetterExchange: 'dlx',
    messageTtl: 86400000 // 24 hours
  });
  await channel.bindQueue('user-events', 'events', 'user.*');
  
  return { connection, channel };
}

// Publish message
async function publishEvent(channel, routingKey, data) {
  channel.publish(
    'events',
    routingKey,
    Buffer.from(JSON.stringify(data)),
    { 
      persistent: true,           // Survive broker restart
      contentType: 'application/json',
      timestamp: Date.now(),
      headers: { version: '1.0' }
    }
  );
}

// Usage
await publishEvent(channel, 'user.created', { userId: '123', email: 'alice@test.com' });
await publishEvent(channel, 'user.updated', { userId: '123', name: 'Alice Smith' });
```

### Consuming Messages

```javascript
async function startConsumer(channel) {
  // Prefetch 10 messages at a time
  await channel.prefetch(10);
  
  channel.consume('user-events', async (msg) => {
    if (!msg) return;
    
    try {
      const data = JSON.parse(msg.content.toString());
      const routingKey = msg.fields.routingKey;
      
      console.log(`Received ${routingKey}:`, data);
      
      switch (routingKey) {
        case 'user.created':
          await handleUserCreated(data);
          break;
        case 'user.updated':
          await handleUserUpdated(data);
          break;
      }
      
      // Acknowledge successful processing
      channel.ack(msg);
    } catch (err) {
      console.error('Processing failed:', err);
      // Reject and requeue (or send to DLQ)
      channel.nack(msg, false, false); // Don't requeue, send to DLX
    }
  });
}
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is a message queue and why use it?**

A message queue decouples producers (send messages) from consumers (process messages). Benefits: async processing (faster API responses), retry handling (automatic redelivery on failure), load leveling (process at worker's pace), decoupling services. Examples: Redis/BullMQ, RabbitMQ, SQS, Kafka.

**Q2: What is the difference between a job queue and a message broker?**

Job queue (BullMQ, Sidekiq): focused on task processing with retries, scheduling, priorities, progress tracking. Each job processed once. Message broker (RabbitMQ, Kafka): focused on routing messages between services, pub/sub patterns, multiple consumers. Job queues are often built on top of message brokers.

**Q3: What happens if a worker crashes while processing a job?**

With proper acknowledgement: the job stays in the queue and is redelivered to another worker. BullMQ: marks job as "stalled" after timeout, retries it. RabbitMQ: unacknowledged messages are requeued. Without ack: job is lost (at-most-once). This is why "at-least-once" delivery requires idempotent processing.

### Intermediate

**Q4: Explain dead letter queues and when to use them.**

Dead letter queue (DLQ) stores messages that failed processing after max retries. Purpose: prevent poison messages from blocking the queue, enable manual inspection and replay. Configuration: set max retry count, on final failure route to DLQ. Monitor DLQ length as a health metric. Implement DLQ consumers for alerting.

**Q5: How do you ensure exactly-once processing with message queues?**

True exactly-once is nearly impossible in distributed systems. Approaches: (1) Idempotent consumers — processing same message twice has same effect (use idempotency key). (2) Transactional outbox — write message and DB change in same transaction. (3) Deduplication with unique message IDs. Design for "at-least-once" + idempotency.

**Q6: How do you handle job priorities and rate limiting in BullMQ?**

Priority: lower number = higher priority. BullMQ processes higher priority jobs first. Rate limiting: `limiter: { max: 10, duration: 1000 }` processes max 10 jobs per second. Group rate limiting: limit per tenant/API key. Combine with concurrency settings for fine-grained control.

### Advanced

**Q7: Compare RabbitMQ and Apache Kafka for event-driven architectures.**

RabbitMQ: traditional broker, message acknowledgement, flexible routing (direct/topic/fanout), messages deleted after consumption. Best for: task queues, request-reply patterns. Kafka: distributed log, messages retained, consumer groups, high throughput, replay capability. Best for: event sourcing, stream processing, data pipelines.

**Q8: How would you implement a reliable webhook delivery system?**

Queue webhook deliveries as jobs. Implement exponential backoff retries (1s, 2s, 4s... up to 24h). Track delivery status per webhook. Handle: timeouts (5s), non-2xx responses (retry), connection failures. After max retries: disable webhook, alert customer. Add: signature verification, deduplication headers, delivery logs.

**Q9: Design a distributed task scheduling system that handles millions of scheduled jobs.**

Architecture: API → Scheduler service (scans for due jobs) → Queue → Workers. Use Redis sorted sets (score = execution timestamp) for efficient range queries. Partition scheduled jobs across shards. Scheduler runs every second, moves due jobs to processing queue. Handle: clock drift, scheduler HA (leader election), timezone awareness.

---

## 🛠️ Hands-on Exercise

Build an async task processing system:
1. Email queue with templates and retry logic
2. Image processing queue with progress reporting
3. Scheduled job (daily report generation)
4. Dead letter queue with monitoring dashboard
5. Rate-limited webhook delivery queue
