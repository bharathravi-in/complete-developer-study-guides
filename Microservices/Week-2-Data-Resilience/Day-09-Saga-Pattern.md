# Day 9: Saga Pattern — Distributed Transactions

## The Problem: No ACID Across Services

In microservices, each service has its own database. Traditional distributed transactions (2PC) are impractical:
- **Holding locks** across services = poor performance
- **Coordinator failure** = all participants stuck
- **Not supported** by many databases (NoSQL, message brokers)

## Saga Pattern

A saga is a sequence of **local transactions**, where each step has a **compensating transaction** for rollback.

```
Order Saga:
Step 1: Create Order (pending)       ← Compensate: Cancel Order
Step 2: Reserve Inventory            ← Compensate: Release Inventory
Step 3: Charge Payment               ← Compensate: Refund Payment
Step 4: Update Order (confirmed)     ← (no compensation needed)
Step 5: Send Notification            ← (idempotent, no compensation)

If Step 3 fails:
  → Compensate Step 2: Release Inventory
  → Compensate Step 1: Cancel Order
```

## Choreography (Event-Driven)

Each service listens for events and decides what to do next. No central coordinator.

```
┌────────┐  OrderCreated   ┌──────────┐  InventoryReserved  ┌─────────┐
│ Order  │ ───────────────> │Inventory │ ──────────────────> │ Payment │
│Service │                  │ Service  │                     │ Service │
└────────┘                  └──────────┘                     └─────────┘
    ^                                                            │
    │              PaymentCharged                                 │
    └────────────────────────────────────────────────────────────┘

Failure path:
┌─────────┐  PaymentFailed   ┌──────────┐  InventoryReleased  ┌────────┐
│ Payment │ ───────────────> │Inventory │ ──────────────────> │ Order  │
│ Service │                  │ Service  │                     │Service │
└─────────┘                  └──────────┘  (compensate)       └────────┘
                                                           (mark cancelled)
```

```typescript
// Order Service — listens for payment events
class OrderEventHandler {
  @EventListener('PaymentCharged')
  async onPaymentCharged(event: PaymentChargedEvent) {
    await this.orderRepo.updateStatus(event.orderId, 'confirmed');
    await this.eventBus.publish('OrderConfirmed', {
      orderId: event.orderId,
      userId: event.userId,
    });
  }

  @EventListener('PaymentFailed')
  async onPaymentFailed(event: PaymentFailedEvent) {
    await this.orderRepo.updateStatus(event.orderId, 'cancelled');
    await this.eventBus.publish('OrderCancelled', {
      orderId: event.orderId,
      reason: event.reason,
    });
  }
}

// Inventory Service — listens for order events
class InventoryEventHandler {
  @EventListener('OrderCreated')
  async onOrderCreated(event: OrderCreatedEvent) {
    try {
      await this.inventoryRepo.reserve(event.items);
      await this.eventBus.publish('InventoryReserved', {
        orderId: event.orderId,
        items: event.items,
      });
    } catch (error) {
      await this.eventBus.publish('InventoryReservationFailed', {
        orderId: event.orderId,
        reason: error.message,
      });
    }
  }

  @EventListener('OrderCancelled')
  async onOrderCancelled(event: OrderCancelledEvent) {
    await this.inventoryRepo.release(event.orderId);
  }
}
```

**Pros**: Loose coupling, simple per-service logic
**Cons**: Hard to track overall progress, difficult to debug, no central flow visibility

### Orchestration (Central Coordinator)

A saga orchestrator directs the workflow. It sends commands and listens for responses.

```
           ┌──────────────────┐
           │ Saga Orchestrator │
           └──────┬───────────┘
                  │
    ┌─────────────┼─────────────┐
    ▼             ▼             ▼
┌────────┐  ┌──────────┐  ┌─────────┐
│ Order  │  │Inventory │  │ Payment │
│Service │  │ Service  │  │ Service │
└────────┘  └──────────┘  └─────────┘
```

```typescript
class OrderSagaOrchestrator {
  async execute(orderData: CreateOrderRequest): Promise<SagaResult> {
    const saga = new SagaBuilder()
      .step('createOrder')
        .action(() => this.orderService.create(orderData))
        .compensation((ctx) => this.orderService.cancel(ctx.orderId))
      .step('reserveInventory')
        .action((ctx) => this.inventoryService.reserve(ctx.orderId, orderData.items))
        .compensation((ctx) => this.inventoryService.release(ctx.orderId))
      .step('chargePayment')
        .action((ctx) => this.paymentService.charge(ctx.orderId, orderData.amount))
        .compensation((ctx) => this.paymentService.refund(ctx.orderId))
      .step('confirmOrder')
        .action((ctx) => this.orderService.confirm(ctx.orderId))
      .step('sendNotification')
        .action((ctx) => this.notificationService.send(ctx.orderId))
      .build();

    return saga.run();
  }
}

class Saga {
  private steps: SagaStep[] = [];
  private completedSteps: SagaStep[] = [];

  async run(): Promise<SagaResult> {
    const context: Record<string, any> = {};

    for (const step of this.steps) {
      try {
        const result = await step.action(context);
        Object.assign(context, result);
        this.completedSteps.push(step);
      } catch (error) {
        // Compensate in reverse order
        await this.compensate(context);
        return { success: false, error: error.message, step: step.name };
      }
    }
    return { success: true, context };
  }

  private async compensate(context: Record<string, any>): Promise<void> {
    for (const step of this.completedSteps.reverse()) {
      try {
        await step.compensation?.(context);
      } catch (error) {
        // Log compensation failure — may need manual intervention
        console.error(`Compensation failed for ${step.name}:`, error);
      }
    }
  }
}
```

**Pros**: Central flow visibility, easier to debug, clear failure handling
**Cons**: Orchestrator can become a bottleneck, tighter coupling with orchestrator

## Choreography vs Orchestration

| Aspect | Choreography | Orchestration |
|--------|-------------|---------------|
| Coupling | Very loose | Moderate (via orchestrator) |
| Visibility | Low (trace events) | High (central coordinator) |
| Complexity | Per-service simple, overall complex | Overall clear, orchestrator complex |
| Debugging | Hard (event chain) | Easier (central state) |
| Scalability | Better (no central bottleneck) | Orchestrator can bottleneck |
| Best For | Simple sagas (2-3 steps) | Complex sagas (4+ steps) |

## Handling Saga Failures

### Compensating Transactions Must Be:

1. **Idempotent**: Can be called multiple times safely
2. **Retryable**: Must eventually succeed (use retry with backoff)
3. **Commutative**: Order shouldn't matter for concurrent compensations

### Saga State Machine

```
              ┌─────────┐
              │ STARTED  │
              └────┬─────┘
                   │ createOrder
              ┌────▼─────┐
              │  ORDER   │
              │ CREATED  │
              └────┬─────┘
                   │ reserveInventory
              ┌────▼─────┐     fail     ┌──────────┐
              │ INVENTORY│────────────>│COMPENSATING│
              │ RESERVED │             └──────────┘
              └────┬─────┘                   │
                   │ chargePayment      ┌────▼─────┐
              ┌────▼─────┐              │ CANCELLED │
              │ PAYMENT  │              └──────────┘
              │ CHARGED  │
              └────┬─────┘
                   │ confirmOrder
              ┌────▼─────┐
              │COMPLETED │
              └──────────┘
```

## Key Takeaways

1. **Saga replaces distributed transactions** — no locks, eventual consistency
2. **Choreography** for simple flows, **orchestration** for complex ones
3. **Compensating transactions** must be idempotent and retryable
4. **Track saga state** in a persistent store for recovery
5. **Design for partial failure** — some steps succeed, others fail
6. **Event deduplication** is critical — use idempotency keys
