# Day 22: API Gateway Patterns

## What Is an API Gateway?

An API Gateway is a **single entry point** for all client requests. It sits between clients and backend services, handling cross-cutting concerns.

```
┌──────────┐     ┌──────────────┐     ┌─────────────┐
│  Web App  │────>│              │────>│ User Service │
├──────────┤     │              │     ├─────────────┤
│Mobile App │────>│  API Gateway │────>│ Order Service│
├──────────┤     │              │     ├─────────────┤
│ 3rd Party │────>│              │────>│ Payment Svc  │
└──────────┘     └──────────────┘     └─────────────┘
```

## Gateway Responsibilities

### 1. Request Routing
```yaml
# Kong / AWS API Gateway style
routes:
  - path: /api/v1/users/**
    service: user-service
    strip_prefix: /api/v1
  - path: /api/v1/orders/**
    service: order-service
    strip_prefix: /api/v1
  - path: /api/v1/payments/**
    service: payment-service
    strip_prefix: /api/v1
```

### 2. Authentication & Authorization
```
Client → Gateway (validates JWT) → Forwards with X-User-Id header → Service
```

### 3. Rate Limiting
```yaml
rate_limiting:
  - path: /api/**
    limits:
      - window: 1m
        max: 100
        key: client_ip
      - window: 1h
        max: 1000
        key: api_key
```

### 4. Request/Response Transformation
```typescript
// Aggregate multiple service calls
app.get('/api/dashboard', async (req, res) => {
  const [user, orders, notifications] = await Promise.all([
    userService.get(`/users/${req.userId}`),
    orderService.get(`/users/${req.userId}/orders?limit=5`),
    notificationService.get(`/users/${req.userId}/notifications`),
  ]);

  res.json({
    user: user.data,
    recentOrders: orders.data,
    notifications: notifications.data,
  });
});
```

### 5. Circuit Breaking
```
Normal → Service responds in < 500ms
Degraded → 50% of requests fail → Circuit OPEN → Return cached/default
Recovery → After 30s → Circuit HALF-OPEN → Try some requests
Restored → Success rate > 80% → Circuit CLOSED → Normal operation
```

## API Gateway Solutions

| Solution | Type | Best For |
|----------|------|----------|
| **Kong** | Self-hosted | Full control, plugins |
| **AWS API Gateway** | Managed | AWS ecosystem |
| **Apigee** | Managed | Enterprise, analytics |
| **Nginx / Envoy** | Self-hosted | High performance |
| **Traefik** | Self-hosted | Container-native |
| **Express Gateway** | Self-hosted | Node.js teams |

## BFF Pattern (Backend for Frontend)

Separate gateway per client type:

```
Web App  → Web BFF  → [ User Svc, Order Svc, ... ]
Mobile   → Mobile BFF → [ User Svc, Order Svc, ... ]
Admin    → Admin BFF  → [ User Svc, Analytics, ... ]
```

```typescript
// Web BFF — rich data for desktop
app.get('/web/dashboard', async (req, res) => {
  const data = await Promise.all([
    fetchUser(req.userId),
    fetchRecentOrders(req.userId, 20),  // More items for web
    fetchAnalytics(req.userId),          // Only web needs this
    fetchNotifications(req.userId),
  ]);
  res.json(aggregateForWeb(data));
});

// Mobile BFF — minimal data for mobile
app.get('/mobile/dashboard', async (req, res) => {
  const data = await Promise.all([
    fetchUser(req.userId),
    fetchRecentOrders(req.userId, 5),   // Fewer items for mobile
    fetchNotifications(req.userId),
  ]);
  res.json(aggregateForMobile(data));
});
```

## Gateway Anti-Patterns

### 1. God Gateway
```
❌ Business logic in gateway
❌ Data transformations beyond simple mapping
❌ Database access from gateway
✅ Keep gateway thin — routing, auth, rate-limiting only
```

### 2. Single Point of Failure
```
❌ Single gateway instance
✅ Multiple instances behind load balancer
✅ Health checks and auto-scaling
✅ Graceful degradation
```

### 3. Tight Coupling
```
❌ Gateway knows service internals
❌ Gateway does data aggregation for all use cases
✅ Use BFF pattern for client-specific aggregation
✅ Services own their data contracts
```

## Key Takeaways

1. **API Gateway = central entry point** for routing, auth, rate limiting
2. **BFF pattern** — one gateway per client type for tailored responses
3. **Keep gateway thin** — no business logic, no database access
4. **Circuit breakers** prevent cascade failures across services
5. **Use managed solutions** (AWS API Gateway, Apigee) unless you need full control
