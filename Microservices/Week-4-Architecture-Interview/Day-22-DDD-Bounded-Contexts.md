# Day 22: DDD & Bounded Contexts for Service Decomposition

## Domain-Driven Design (DDD) and Microservices

DDD provides the **intellectual framework** for drawing service boundaries. Bounded Contexts map naturally to microservices.

## Core DDD Concepts

### Ubiquitous Language

```
In the ORDER context:
  "Customer" = person placing the order
  "Product"  = item being purchased (name, price)

In the SHIPPING context:
  "Customer" = delivery recipient (address, phone)
  "Product"  = package (weight, dimensions)

Same words, DIFFERENT meanings per context → DIFFERENT models
```

### Bounded Context

A boundary within which a particular domain model is defined and applicable.

```
┌─────────────────────────────────────────────────┐
│                E-Commerce Domain                 │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐              │
│  │   Catalog     │  │   Ordering    │             │
│  │   Context     │  │   Context     │             │
│  │               │  │               │             │
│  │ Product:      │  │ Product:      │             │
│  │  - name       │  │  - productId  │             │
│  │  - description│  │  - quantity   │             │
│  │  - images     │  │  - unitPrice  │             │
│  │  - category   │  │               │             │
│  │  - reviews    │  │ Order:        │             │
│  │               │  │  - items      │             │
│  └──────────────┘  │  - total      │             │
│                     │  - status     │             │
│  ┌──────────────┐  └──────────────┘              │
│  │   Shipping    │  ┌──────────────┐             │
│  │   Context     │  │   Payment     │             │
│  │               │  │   Context     │             │
│  │ Package:      │  │               │             │
│  │  - weight     │  │ Transaction:  │             │
│  │  - dimensions │  │  - amount     │             │
│  │  - address    │  │  - method     │             │
│  │  - tracking   │  │  - status     │             │
│  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────┘
```

### Context Mapping Patterns

```
1. Shared Kernel:
   Two contexts share a common model (tightly coupled)
   Order & Invoice share "LineItem" definition

2. Customer-Supplier:
   Upstream (supplier) provides; downstream (customer) consumes
   Product Catalog (upstream) → Order (downstream)

3. Anti-Corruption Layer (ACL):
   Translator between your model and external system
   Your Service → ACL → Legacy System

4. Open Host Service:
   Published API/protocol for integration
   User Service exposes REST API consumed by many

5. Published Language:
   Shared schema/format for events
   Protobuf schemas, Avro schemas, JSON Schema

6. Conformist:
   Downstream adopts upstream's model as-is (no translation)

7. Separate Ways:
   No integration — contexts are independent
```

## Identifying Service Boundaries

### Step 1: Event Storming

```
Workshop technique:
1. Identify DOMAIN EVENTS (past tense): "Order Placed", "Payment Received"
2. Group events into AGGREGATES: Order, Payment, Shipment
3. Identify COMMANDS: "Place Order", "Process Payment"
4. Draw BOUNDARIES around related events → Bounded Contexts
5. Map contexts to SERVICES
```

### Step 2: Test Boundaries with These Questions

```
For each proposed service boundary:

1. Can this be deployed independently?
2. Does it have its own data store?
3. Can one team own it end-to-end?
4. Does it have a well-defined API?
5. Can it fail without bringing down other services?
6. Does changing its internals require changing other services?

If ALL "yes" → good boundary
If any "no" → reconsider the split
```

### Anti-Pattern: Distributed Monolith

```
❌ Services share a database
❌ Changes require coordinated deployments
❌ Services call each other synchronously in chains
❌ Shared libraries with business logic
❌ Same team owns all services

= You have a distributed monolith (worst of both worlds)
```

## Aggregate Design

An aggregate is a cluster of domain objects treated as a single unit for data changes.

```typescript
// Order Aggregate
class Order {
  private items: OrderItem[] = [];
  private status: OrderStatus = 'draft';

  // Only modify through aggregate root
  addItem(productId: string, quantity: number, price: number): void {
    if (this.status !== 'draft') {
      throw new Error('Cannot modify confirmed order');
    }
    this.items.push(new OrderItem(productId, quantity, price));
  }

  confirm(): void {
    if (this.items.length === 0) {
      throw new Error('Cannot confirm empty order');
    }
    this.status = 'confirmed';
    // Raise domain event
    this.addDomainEvent(new OrderConfirmedEvent(this.id, this.total));
  }

  get total(): number {
    return this.items.reduce((sum, item) => sum + item.subtotal, 0);
  }
}

// Rule: Access aggregates ONLY through their root entity
// Rule: One transaction = one aggregate
// Rule: Reference other aggregates by ID, not object reference
```

## Key Takeaways

1. **Bounded Context = Service Boundary** — DDD provides the decomposition framework
2. **Same word, different meaning** across contexts → different models = different services
3. **Event Storming** is the best technique for discovering boundaries
4. **Aggregate = consistency boundary** — one transaction per aggregate
5. **Anti-Corruption Layer** protects your model from external system changes
6. **Avoid distributed monolith** — if services can't deploy independently, you split wrong
