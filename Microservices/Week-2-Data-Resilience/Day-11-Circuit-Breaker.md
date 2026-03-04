# Day 11: Circuit Breaker Pattern

## The Problem: Cascading Failures

```
Service A → Service B → Service C (DOWN)
                  ↓
         B times out waiting for C
                  ↓
         A times out waiting for B
                  ↓
         All services overwhelmed with waiting threads
                  ↓
         SYSTEM-WIDE OUTAGE 💀
```

## Circuit Breaker States

```
     ┌──────────┐
     │  CLOSED   │  ─── Normal operation; requests pass through
     │ (Normal)  │
     └────┬─────┘
          │ Failure threshold exceeded
     ┌────▼──────┐
     │   OPEN    │  ─── Fail fast; no requests sent to downstream
     │ (Failing) │
     └────┬─────┘
          │ Timeout expires (cool-down)
     ┌────▼──────┐
     │ HALF-OPEN │  ─── Allow limited requests to test recovery
     │ (Testing) │
     └────┬─────┘
          │
     ┌────┴────────────────┐
     │                      │
  Success               Failure
     │                      │
     ▼                      ▼
  CLOSED                  OPEN
```

## Implementation

```typescript
enum CircuitState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN',
}

interface CircuitBreakerConfig {
  failureThreshold: number;    // Failures before opening (e.g., 5)
  successThreshold: number;    // Successes in half-open to close (e.g., 3)
  timeout: number;             // ms before trying half-open (e.g., 30000)
  monitorWindow: number;       // ms window for counting failures (e.g., 60000)
}

class CircuitBreaker {
  private state = CircuitState.CLOSED;
  private failureCount = 0;
  private successCount = 0;
  private lastFailureTime = 0;
  private nextAttemptTime = 0;

  constructor(private config: CircuitBreakerConfig) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === CircuitState.OPEN) {
      if (Date.now() < this.nextAttemptTime) {
        throw new CircuitOpenError('Circuit is OPEN — failing fast');
      }
      this.state = CircuitState.HALF_OPEN;
      console.log('Circuit → HALF_OPEN');
    }

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private onSuccess(): void {
    if (this.state === CircuitState.HALF_OPEN) {
      this.successCount++;
      if (this.successCount >= this.config.successThreshold) {
        this.state = CircuitState.CLOSED;
        this.failureCount = 0;
        this.successCount = 0;
        console.log('Circuit → CLOSED (recovered)');
      }
    } else {
      this.failureCount = 0; // Reset on success in closed state
    }
  }

  private onFailure(): void {
    this.failureCount++;
    this.lastFailureTime = Date.now();

    if (this.state === CircuitState.HALF_OPEN) {
      this.state = CircuitState.OPEN;
      this.nextAttemptTime = Date.now() + this.config.timeout;
      this.successCount = 0;
      console.log('Circuit → OPEN (half-open test failed)');
    } else if (this.failureCount >= this.config.failureThreshold) {
      this.state = CircuitState.OPEN;
      this.nextAttemptTime = Date.now() + this.config.timeout;
      console.log('Circuit → OPEN (threshold exceeded)');
    }
  }

  getState(): CircuitState { return this.state; }
}

// Usage
const breaker = new CircuitBreaker({
  failureThreshold: 5,
  successThreshold: 3,
  timeout: 30_000,
  monitorWindow: 60_000,
});

async function callPaymentService(orderId: string) {
  try {
    return await breaker.execute(() =>
      fetch(`http://payment-service/charge/${orderId}`)
    );
  } catch (error) {
    if (error instanceof CircuitOpenError) {
      // Fallback: return cached response, queue for retry, etc.
      return { status: 'pending', message: 'Payment service temporarily unavailable' };
    }
    throw error;
  }
}
```

## Retry Pattern

```typescript
interface RetryConfig {
  maxRetries: number;
  baseDelay: number;       // ms
  maxDelay: number;        // ms
  backoffMultiplier: number;
  retryableErrors: string[];
}

async function withRetry<T>(
  fn: () => Promise<T>,
  config: RetryConfig
): Promise<T> {
  let lastError: Error;

  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      if (attempt === config.maxRetries) break;
      if (!isRetryable(error, config.retryableErrors)) break;

      // Exponential backoff with jitter
      const delay = Math.min(
        config.baseDelay * Math.pow(config.backoffMultiplier, attempt),
        config.maxDelay
      );
      const jitter = delay * 0.5 * Math.random();
      await sleep(delay + jitter);

      console.log(`Retry ${attempt + 1}/${config.maxRetries} after ${delay}ms`);
    }
  }
  throw lastError!;
}

// Usage with circuit breaker
async function resilientCall(orderId: string) {
  return breaker.execute(() =>
    withRetry(
      () => fetch(`http://payment-service/charge/${orderId}`),
      { maxRetries: 3, baseDelay: 500, maxDelay: 5000, backoffMultiplier: 2, retryableErrors: ['ECONNREFUSED', 'ETIMEDOUT'] }
    )
  );
}
```

## Bulkhead Pattern

Isolate failures by limiting resources per dependency:

```typescript
class Bulkhead {
  private active = 0;
  private queue: Array<() => void> = [];

  constructor(
    private maxConcurrent: number,  // Max simultaneous calls
    private maxQueue: number         // Max waiting requests
  ) {}

  async execute<T>(fn: () => Promise<T>): Promise<T> {
    if (this.active >= this.maxConcurrent) {
      if (this.queue.length >= this.maxQueue) {
        throw new Error('Bulkhead full — request rejected');
      }
      await new Promise<void>(resolve => this.queue.push(resolve));
    }

    this.active++;
    try {
      return await fn();
    } finally {
      this.active--;
      if (this.queue.length > 0) {
        const next = this.queue.shift()!;
        next();
      }
    }
  }
}

// Separate bulkheads per dependency
const paymentBulkhead = new Bulkhead(10, 20);
const inventoryBulkhead = new Bulkhead(15, 30);

// Payment service down doesn't exhaust connections for inventory
await paymentBulkhead.execute(() => callPaymentService(orderId));
await inventoryBulkhead.execute(() => callInventoryService(orderId));
```

## Key Takeaways

1. **Circuit breaker prevents cascading failures** — fail fast, don't wait
2. **Three states**: Closed (normal) → Open (failing fast) → Half-Open (testing)
3. **Retry with exponential backoff + jitter** — avoid thundering herd
4. **Bulkhead** isolates failure domains — one slow service can't starve others
5. **Combine all three**: Bulkhead → Circuit Breaker → Retry → Call
6. **Always have a fallback** — cached data, default response, queue for later
