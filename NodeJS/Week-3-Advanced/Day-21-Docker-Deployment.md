# Day 21: Docker & Deployment

## 🎯 Learning Objectives
- Containerize Node.js applications with Docker
- Write production-ready Dockerfiles
- Implement CI/CD pipelines
- Deploy to cloud platforms (AWS, GCP, Railway)

---

## 📚 Docker for Node.js

### Production Dockerfile

```dockerfile
# Multi-stage build for smaller images
# Stage 1: Install dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Stage 2: Build (if needed, e.g., TypeScript)
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Production image
FROM node:20-alpine AS runner
WORKDIR /app

# Security: non-root user
RUN addgroup --system nodejs && adduser --system nodeuser
USER nodeuser

# Copy only what's needed
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY package.json ./

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

EXPOSE 3000
ENV NODE_ENV=production

CMD ["node", "dist/index.js"]
```

### Docker Compose for Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
      - "9229:9229"  # Debugger
    volumes:
      - .:/app
      - /app/node_modules  # Don't override node_modules
    environment:
      - NODE_ENV=development
      - DATABASE_URL=postgres://postgres:password@db:5432/myapp
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: npm run dev

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongodata:/data/db

volumes:
  pgdata:
  mongodata:
```

### .dockerignore

```
node_modules
npm-debug.log
.git
.env
.env.*
coverage
dist
*.md
.vscode
.idea
```

---

## 🚀 CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        ports: [5432:5432]
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
      
      redis:
        image: redis:7
        ports: [6379:6379]
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'
      
      - run: npm ci
      - run: npm run lint
      - run: npm run test:coverage
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
      
      - uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build & Push Docker image
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to production
        run: |
          # Deploy to your platform (Railway, Fly.io, AWS ECS, etc.)
          echo "Deploying..."
```

---

## ☁️ Cloud Deployment Options

### PM2 (Process Manager)

```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'api',
    script: 'dist/index.js',
    instances: 'max',     // Use all CPU cores
    exec_mode: 'cluster',
    max_memory_restart: '500M',
    env_production: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    // Graceful shutdown
    kill_timeout: 10000,
    listen_timeout: 5000,
    // Logging
    error_file: '/var/log/api/error.log',
    out_file: '/var/log/api/out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss'
  }]
};

// Commands:
// pm2 start ecosystem.config.js --env production
// pm2 reload api  (zero-downtime restart)
// pm2 monit       (monitor)
// pm2 logs        (view logs)
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: ghcr.io/myorg/api:latest
          ports:
            - containerPort: 3000
          env:
            - name: NODE_ENV
              value: "production"
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: database-url
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health/live
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 3000
  type: ClusterIP
```

---

## 🧪 Interview Questions

### Beginner

**Q1: Why use Docker for Node.js applications?**

Docker ensures consistency across environments (dev/staging/prod). Benefits: reproducible builds, isolation, easy scaling, simplified deployment, version pinning (Node version, OS). Eliminates "works on my machine" issues. Multi-stage builds create small production images. Docker Compose simplifies local development with dependencies.

**Q2: What is a multi-stage Docker build?**

A Dockerfile with multiple FROM statements. Each stage can copy artifacts from previous stages. Purpose: separate build environment (dev dependencies, build tools) from production image (only runtime deps). Result: smaller, more secure images. Example: install all deps → build TypeScript → copy only compiled output + prod deps to final image.

**Q3: What is PM2 and why use it?**

PM2 is a Node.js process manager for production. Features: cluster mode (utilize all CPUs), auto-restart on crashes, zero-downtime reloads, log management, monitoring dashboard. Use it when deploying directly to VMs (not containers). With containers/Kubernetes, PM2 is less needed since the orchestrator handles restarts.

### Intermediate

**Q4: How do you implement zero-downtime deployments for Node.js?**

Strategies: (1) Rolling updates (Kubernetes) — replace pods one at a time. (2) Blue-green — deploy new version alongside old, switch traffic. (3) Canary — route small % of traffic to new version. Requirements: health checks, graceful shutdown (finish in-flight requests), backward-compatible API changes. PM2: `pm2 reload` does rolling restart.

**Q5: How do you handle environment-specific configuration in deployments?**

Hierarchy: (1) Default config in code. (2) Environment-specific files (config/production.json). (3) Environment variables (override everything). In Docker: env vars via docker-compose, K8s ConfigMaps/Secrets. Never bake secrets into images. Validate all required config at startup. Use libraries like `convict` or `config` for typed configuration.

**Q6: What should a production Node.js health check endpoint return?**

Return: overall status, dependency health (DB, Redis, queues), version, uptime. Separate endpoints: `/health/live` (process running — for liveness probe), `/health/ready` (can serve traffic — for readiness probe). Return 200 if healthy, 503 if not. Include response time. Don't expose internal details in public-facing endpoints.

### Advanced

**Q7: Design a deployment pipeline for a Node.js microservices application.**

Pipeline: PR → lint + unit tests → build Docker image → integration tests (docker-compose) → push to registry → deploy to staging → smoke tests → manual approval → canary deploy (5% traffic) → monitor metrics → full rollout. Per-service pipelines with shared CI templates. Rollback: revert to previous image tag automatically on error rate spike.

**Q8: How do you handle database migrations in containerized deployments?**

Options: (1) Init container (K8s) — runs migration before app starts. (2) Startup script — check and run pending migrations on boot. (3) Separate migration job — CI/CD runs migration before deploying new image. Rules: migrations must be backward-compatible (old code + new schema works). Never drop columns immediately — deploy code first, then remove column.

**Q9: How would you implement auto-scaling for a Node.js application?**

Kubernetes HPA: scale on CPU, memory, or custom metrics (request queue depth, event loop lag). Configure: min/max replicas, target utilization (70% CPU). Proactive: scale up fast, scale down slowly (cooldown period). Custom metrics: export to Prometheus, HPA queries them. Consider: connection limits, warm-up time, statelessness requirements.

---

## 🛠️ Hands-on Exercise

Containerize and deploy a Node.js API:
1. Multi-stage Dockerfile (dev + production)
2. Docker Compose with PostgreSQL + Redis
3. Health check endpoints (live + ready)
4. GitHub Actions CI/CD pipeline
5. PM2 cluster configuration
6. Kubernetes manifests (deployment + service + HPA)
