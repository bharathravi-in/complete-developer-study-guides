# Day 22: Performance Testing Fundamentals

## 📚 Topics to Cover (3-4 hours)

---

## 1. Types of Performance Testing

| Type | Purpose | Tools |
|------|---------|-------|
| **Load Testing** | Behavior under expected load | k6, Artillery, JMeter |
| **Stress Testing** | Breaking point determination | k6, Locust |
| **Spike Testing** | Sudden traffic surge handling | k6, Gatling |
| **Endurance Testing** | Sustained load over time | k6, JMeter |
| **Scalability Testing** | How well it scales horizontally/vertically | Custom scripts |
| **Volume Testing** | Large data set handling | Custom + DB tools |

---

## 2. k6 – Modern Load Testing

```javascript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up to 20 users
    { duration: '1m', target: 20 },     // Stay at 20 users
    { duration: '10s', target: 0 },     // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],   // 95% of requests < 500ms
    http_req_failed: ['rate<0.01'],     // Less than 1% errors
    http_reqs: ['rate>100'],            // At least 100 req/s
  },
};

export default function () {
  const res = http.get('http://localhost:3000/api/users');
  
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 200ms': (r) => r.timings.duration < 200,
    'response has users': (r) => JSON.parse(r.body).length > 0,
  });

  sleep(1); // Think time between requests
}

// Run: k6 run load-test.js
```

### Stress Test Pattern

```javascript
export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp to 100
    { duration: '5m', target: 100 },   // Hold at 100
    { duration: '2m', target: 200 },   // Push to 200
    { duration: '5m', target: 200 },   // Hold at 200
    { duration: '2m', target: 300 },   // Push to 300
    { duration: '5m', target: 300 },   // Hold at 300
    { duration: '2m', target: 0 },     // Ramp down
  ],
};
```

---

## 3. Frontend Performance Testing

### Lighthouse CI

```javascript
// lighthouserc.js
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000/', 'http://localhost:3000/dashboard'],
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['warn', { minScore: 0.9 }],
        'first-contentful-paint': ['error', { maxNumericValue: 2000 }],
        'largest-contentful-paint': ['error', { maxNumericValue: 2500 }],
        'cumulative-layout-shift': ['error', { maxNumericValue: 0.1 }],
        'total-blocking-time': ['error', { maxNumericValue: 300 }],
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
```

### Core Web Vitals

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤2.5s | ≤4.0s | >4.0s |
| **FID** (First Input Delay) | ≤100ms | ≤300ms | >300ms |
| **CLS** (Cumulative Layout Shift) | ≤0.1 | ≤0.25 | >0.25 |
| **INP** (Interaction to Next Paint) | ≤200ms | ≤500ms | >500ms |
| **TTFB** (Time to First Byte) | ≤800ms | ≤1800ms | >1800ms |
| **FCP** (First Contentful Paint) | ≤1.8s | ≤3.0s | >3.0s |

---

## 4. Bundle Size Analysis

```bash
# React/Webpack
npx webpack-bundle-analyzer stats.json

# Angular
ng build --stats-json
npx webpack-bundle-analyzer dist/stats.json

# Vite
npm install --save-dev rollup-plugin-visualizer
```

### Size Budget (Angular)

```json
// angular.json
{
  "budgets": [
    {
      "type": "initial",
      "maximumWarning": "500kb",
      "maximumError": "1mb"
    },
    {
      "type": "anyComponentStyle",
      "maximumWarning": "2kb",
      "maximumError": "4kb"
    }
  ]
}
```

---

## 5. Memory Leak Detection

```javascript
// Browser DevTools
// 1. Performance tab → Record → Take Actions → Stop
// 2. Memory tab → Heap Snapshot → Compare snapshots
// 3. Look for Detached DOM nodes

// Automated memory check
describe('Memory Leak Test', () => {
  it('should not leak memory on route change', async () => {
    const initialMemory = await page.evaluate(() => 
      performance.memory.usedJSHeapSize
    );

    // Navigate back and forth 10 times
    for (let i = 0; i < 10; i++) {
      await page.goto('/page-a');
      await page.goto('/page-b');
    }

    await page.evaluate(() => {
      // Force garbage collection (Chrome only with --js-flags="--expose-gc")
      if (window.gc) window.gc();
    });

    const finalMemory = await page.evaluate(() => 
      performance.memory.usedJSHeapSize
    );

    // Memory should not grow more than 20%
    expect(finalMemory).toBeLessThan(initialMemory * 1.2);
  });
});
```

---

## 6. API Performance Testing with Python

```python
# locust_test.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)  # Weight: 3x more likely
    def get_users(self):
        self.client.get("/api/users")

    @task(1)
    def create_user(self):
        self.client.post("/api/users", json={
            "name": "Test User",
            "email": f"test_{random.randint(1,10000)}@test.com"
        })

    def on_start(self):
        # Login on start
        response = self.client.post("/api/auth/login", json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        self.token = response.json()["token"]
        self.client.headers = {"Authorization": f"Bearer {self.token}"}

# Run: locust -f locust_test.py --host=http://localhost:3000
```

---

## 🎯 Interview Questions

### Q1: How do you measure API performance?
**A:** Key metrics: response time (p50, p95, p99), throughput (req/s), error rate, and resource utilization (CPU, memory). Use tools like k6 or Artillery for load testing. Set SLA thresholds (e.g., p95 < 500ms) and monitor in production with APM tools.

### Q2: What are Core Web Vitals and why do they matter?
**A:** LCP (loading), FID/INP (interactivity), CLS (visual stability). Google uses them as ranking factors. They measure real user experience. Optimize with lazy loading, code splitting, preloading critical resources, and minimizing layout shifts.

### Q3: How do you identify and fix memory leaks?
**A:** Take heap snapshots before/after operations, compare for growing objects. Common causes: unsubscribed observables, event listeners not removed, closures holding references, detached DOM nodes. Fix: proper cleanup in ngOnDestroy/useEffect return, WeakMap/WeakRef usage.
