# Day 2: Dockerfile Best Practices & Multi-Stage Builds

## 📚 Topics to Cover (3-4 hours)

---

## 1. Multi-Stage Builds

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:20-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

ENV NODE_ENV=production
USER node
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### Angular Multi-Stage

```dockerfile
# Stage 1: Build Angular app
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build -- --configuration production

# Stage 2: Serve with Nginx
FROM nginx:alpine
COPY --from=build /app/dist/my-app/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Python Multi-Stage

```dockerfile
# Stage 1: Build with full Python
FROM python:3.12 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
COPY . .

# Stage 2: Slim production
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

---

## 2. .dockerignore

```
# .dockerignore
node_modules
npm-debug.log
dist
.git
.gitignore
.env
.env.*
Dockerfile
docker-compose.yml
.dockerignore
README.md
.vscode
coverage
__pycache__
*.pyc
.pytest_cache
.angular
```

---

## 3. Security Best Practices

```dockerfile
# 1. Use specific image tags (never :latest in production)
FROM node:20.11.0-alpine3.19

# 2. Run as non-root user
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -D appuser
USER appuser

# 3. Use COPY, not ADD (unless you need tar extraction)
COPY package*.json ./

# 4. Scan for vulnerabilities
# docker scout cves myimage:latest
# trivy image myimage:latest

# 5. Read-only filesystem
# docker run --read-only --tmpfs /tmp myimage

# 6. Don't store secrets in images
# Use build args for build-time secrets
ARG NPM_TOKEN
RUN echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" > .npmrc && \
    npm ci && \
    rm -f .npmrc

# 7. Use HEALTHCHECK
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# 8. Minimize attack surface
RUN apk add --no-cache curl && \
    apk del --purge build-dependencies
```

---

## 4. Optimization Techniques

### Size Comparison

```bash
# Base image sizes (approximate)
ubuntu:22.04          ~77MB
python:3.12           ~1GB
python:3.12-slim      ~130MB
python:3.12-alpine    ~50MB
node:20               ~1.1GB
node:20-slim          ~200MB
node:20-alpine        ~130MB
nginx:latest          ~140MB
nginx:alpine          ~40MB
gcr.io/distroless/nodejs  ~120MB (no shell!)
```

### Combine & Clean RUN Commands

```dockerfile
# BAD - Each RUN creates a layer
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y git
RUN apt-get clean

# GOOD - Single layer, cleaned up
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl \
      git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### Build Arguments

```dockerfile
ARG NODE_VERSION=20
FROM node:${NODE_VERSION}-alpine

ARG BUILD_DATE
ARG VERSION
LABEL build-date=${BUILD_DATE}
LABEL version=${VERSION}

# Build: docker build --build-arg VERSION=1.2.3 .
```

---

## 5. Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        NODE_ENV: production
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
      - REDIS_URL=redis://cache:6379
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped
    networks:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - backend

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    networks:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - backend

volumes:
  pgdata:
  redis-data:

networks:
  backend:
    driver: bridge
```

### Docker Compose Commands

```bash
docker compose up -d              # Start all services
docker compose down               # Stop and remove
docker compose down -v            # Also remove volumes
docker compose logs -f app        # Follow logs
docker compose exec app sh        # Shell into service
docker compose ps                 # List services
docker compose build              # Build images
docker compose pull               # Pull latest images
docker compose restart app        # Restart service
docker compose scale app=3        # Scale service
```

---

## 6. Docker Networking

```bash
# Network types
docker network create mynet                          # bridge (default)
docker network create --driver host mynet            # host
docker network create --driver overlay mynet         # swarm overlay

# Connect containers
docker run --network mynet --name app1 myimage
docker run --network mynet --name app2 myimage
# app1 can reach app2 via hostname "app2"

# Inspect
docker network ls
docker network inspect bridge
```

---

## 🎯 Interview Questions

### Q1: What are multi-stage builds and why use them?
**A:** Multi-stage builds use multiple FROM statements. Build tools and source code stay in builder stages; only production artifacts go to the final image. Benefits: smaller images (10x reduction), no build tools in production, better security, cleaner separation.

### Q2: How do you handle secrets in Docker?
**A:** Never put secrets in Dockerfile or image layers. Use: (1) Environment variables at runtime (`-e`), (2) Docker secrets (Swarm/K8s), (3) Volume-mounted secret files, (4) Build-time secrets with `--secret` flag, (5) External secret managers (Vault, AWS Secrets Manager).

### Q3: Explain Docker networking modes
**A:** **Bridge** (default): Isolated network, containers communicate via DNS. **Host**: Container uses host network directly (no isolation). **Overlay**: Multi-host networking for Docker Swarm. **None**: No networking. **Macvlan**: Assign MAC address, appear as physical device.

---

## 📝 Practice Exercises

1. Build a multi-stage Dockerfile that reduces image size by 80%+
2. Create a docker-compose.yml for a full-stack app (API + DB + Cache + Proxy)
3. Set up Docker networking between multiple services
4. Implement health checks and dependency ordering in Compose
