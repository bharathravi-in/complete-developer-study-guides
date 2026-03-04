# Advanced Docker & Kubernetes Essentials

> Production deployment patterns beyond basic Docker Compose.

---

## 1. Multi-Stage Build (Optimized)

```dockerfile
# ============ Stage 1: Dependencies ============
FROM python:3.11-slim AS deps
WORKDIR /app
RUN pip install --no-cache-dir pip-tools
COPY requirements.in .
RUN pip-compile requirements.in -o requirements.txt
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ============ Stage 2: Test ============
FROM python:3.11-slim AS test
WORKDIR /app
COPY --from=deps /install /usr/local
COPY . .
RUN pytest tests/ -v --tb=short

# ============ Stage 3: Production ============
FROM python:3.11-slim AS production
WORKDIR /app

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy only dependencies (not test files)
COPY --from=deps /install /usr/local
COPY app/ ./app/
COPY gunicorn.conf.py .

# Security
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
    
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:create_app()"]
```

**Image size comparison:**
```
python:3.11         → 1.01 GB
python:3.11-slim    → 131 MB
python:3.11-alpine  → 51 MB (but has compatibility issues)
Multi-stage slim    → ~180 MB (with dependencies)
```

---

## 2. Docker Compose — Full Production Stack

```yaml
version: '3.8'

x-common: &common
  restart: unless-stopped
  logging:
    driver: json-file
    options:
      max-size: "10m"
      max-file: "3"

services:
  # ==================== API ====================
  api:
    <<: *common
    build:
      context: ./backend
      target: production
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@postgres:5432/aiplatform
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - CELERY_BROKER_URL=redis://redis:6379/1
    env_file:
      - .env  # OPENAI_API_KEY, JWT_SECRET
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: "1.0"

  # ==================== Celery Worker ====================
  worker:
    <<: *common
    build:
      context: ./backend
      target: production
    command: celery -A tasks worker --loglevel=info --concurrency=4
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/aiplatform
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_HOST=qdrant
      - CELERY_BROKER_URL=redis://redis:6379/1
    env_file:
      - .env
    depends_on:
      - redis
      - postgres
      - qdrant
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: "2.0"

  # ==================== PostgreSQL ====================
  postgres:
    <<: *common
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      POSTGRES_DB: aiplatform
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d aiplatform"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 256M

  # ==================== Qdrant ====================
  qdrant:
    <<: *common
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"  # gRPC
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      QDRANT__SERVICE__GRPC_PORT: 6334
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:6333/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          memory: 1G

  # ==================== Redis ====================
  redis:
    <<: *common
    image: redis:7-alpine
    command: redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # ==================== Nginx ====================
  nginx:
    <<: *common
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api

  # ==================== Monitoring (Optional) ====================
  prometheus:
    <<: *common
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
    profiles:
      - monitoring

  grafana:
    <<: *common
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    profiles:
      - monitoring

volumes:
  postgres_data:
  qdrant_data:
  redis_data:
```

### Dev Override
```yaml
# docker-compose.dev.yml
services:
  api:
    build:
      target: deps  # Skip production stage
    command: flask run --debug --host 0.0.0.0
    volumes:
      - ./backend:/app  # Hot reload
    environment:
      - FLASK_ENV=development

# Run: docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

## 3. Kubernetes Essentials

### When Docker Compose → Kubernetes
```
Docker Compose: 1 server, simple deploys, small team
Kubernetes: Multiple servers, auto-scaling, zero-downtime, large team

Start with Compose. Move to K8s when you need:
  - Auto-scaling based on load
  - Self-healing (auto-restart crashed containers)
  - Rolling updates with zero downtime
  - Multiple environments (staging, production)
  - Service mesh / advanced networking
```

### K8s Deployment (Flask API)
```yaml
# k8s/api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-platform-api
  labels:
    app: ai-platform
    component: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-platform
      component: api
  template:
    metadata:
      labels:
        app: ai-platform
        component: api
    spec:
      containers:
        - name: api
          image: your-registry/ai-platform-api:latest
          ports:
            - containerPort: 5000
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: ai-platform-secrets
                  key: database-url
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: ai-platform-secrets
                  key: openai-api-key
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 10
            periodSeconds: 30
          readinessProbe:
            httpGet:
              path: /health
              port: 5000
            initialDelaySeconds: 5
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: ai-platform-api
spec:
  selector:
    app: ai-platform
    component: api
  ports:
    - port: 80
      targetPort: 5000
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-platform-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-platform-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

---

## 4. CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Build and Deploy

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
        image: postgres:16-alpine
        env:
          POSTGRES_DB: test
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml
      
      - name: Lint
        run: |
          pip install ruff
          ruff check backend/

  build:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: |
          docker build -t ai-platform-api:${{ github.sha }} ./backend
      
      - name: Push to registry
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker tag ai-platform-api:${{ github.sha }} your-registry/ai-platform-api:${{ github.sha }}
          docker tag ai-platform-api:${{ github.sha }} your-registry/ai-platform-api:latest
          docker push your-registry/ai-platform-api:${{ github.sha }}
          docker push your-registry/ai-platform-api:latest
```

---

## 5. Docker Security Best Practices

```dockerfile
# 1. Non-root user
RUN adduser --disabled-password --no-create-home appuser
USER appuser

# 2. Read-only filesystem
# docker run --read-only --tmpfs /tmp myapp

# 3. No new privileges
# docker run --security-opt no-new-privileges myapp

# 4. Scan for vulnerabilities
# docker scout cves myapp:latest
# trivy image myapp:latest

# 5. Use specific tags, never :latest in production
FROM python:3.11.7-slim  # Pinned version

# 6. Don't store secrets in images
# Use environment variables or Docker secrets
```

---

## Key Takeaways
1. **Multi-stage builds** keep images small and secure
2. **Health checks** are mandatory for production Docker
3. **Resource limits** prevent runaway containers
4. **Docker Compose** for small deployments, **Kubernetes** for scale
5. **CI/CD**: Test → Build → Push → Deploy automatically
6. **Security**: Non-root user, pinned versions, vulnerability scanning
