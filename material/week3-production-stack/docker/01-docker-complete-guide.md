# Docker - Complete Guide for AI Engineers

## Why Docker?
- "It works on my machine" → It works everywhere
- Package Flask + Qdrant + Redis as ONE deployable unit
- Consistent development environments
- Easy scaling and deployment

---

## 1. Dockerfile for Flask App

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run with gunicorn (production server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:create_app()"]
```

### Multi-Stage Build (Smaller Image)
```dockerfile
# Stage 1: Build
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy only installed packages
COPY --from=builder /install /usr/local

# Copy application
COPY . .

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:create_app()"]
```

```bash
# Build
docker build -t ai-platform-api .

# Run
docker run -p 5000:5000 --env-file .env ai-platform-api

# Interactive (for debugging)
docker run -it --rm ai-platform-api /bin/bash
```

---

## 2. Docker Compose (The Full Stack)

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Flask API
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - REDIS_URL=redis://redis:6379
      - QDRANT_URL=http://qdrant:6333
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./app:/app/app  # Hot reload in dev
    depends_on:
      - redis
      - qdrant
    restart: unless-stopped

  # Qdrant Vector Database
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"  # REST API
      - "6334:6334"  # gRPC
    volumes:
      - qdrant_storage:/qdrant/storage
    restart: unless-stopped

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes  # Persist data
    restart: unless-stopped

  # PostgreSQL (Optional - for user data)
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: ai_platform
      POSTGRES_USER: bharath
      POSTGRES_PASSWORD: ${DB_PASSWORD:-password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  qdrant_storage:
  redis_data:
  postgres_data:
```

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Rebuild after code changes
docker-compose up -d --build api

# Stop all
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

---

## 3. Essential Docker Commands

```bash
# Images
docker images                    # List images
docker build -t myapp .          # Build image
docker pull redis:7              # Pull image
docker rmi myapp                 # Remove image

# Containers
docker ps                        # Running containers
docker ps -a                     # All containers
docker run -d -p 5000:5000 myapp # Run detached
docker stop <container_id>       # Stop
docker rm <container_id>         # Remove
docker logs <container_id>       # View logs
docker exec -it <id> /bin/bash   # Shell into container

# Volumes
docker volume ls                 # List volumes
docker volume rm <name>          # Remove volume

# Cleanup
docker system prune              # Remove unused data
docker system prune -a           # Remove everything unused
```

---

## 4. .dockerignore

```
# .dockerignore
__pycache__
*.pyc
*.pyo
.git
.gitignore
.env
.venv
venv
node_modules
*.egg-info
dist
build
.pytest_cache
.mypy_cache
*.log
docker-compose.yml
Dockerfile
README.md
docs/
tests/
```

---

## 5. Development vs Production

### Development Docker Compose
```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "5000:5000"
    volumes:
      - .:/app  # Mount entire project for hot reload
    environment:
      - FLASK_ENV=development
      - FLASK_DEBUG=1
    command: flask run --host=0.0.0.0 --reload
```

### Dockerfile.dev
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]
```

```bash
# Run dev environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

## 6. Health Checks

```yaml
services:
  api:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5
```

---

## Key Takeaways
1. **Dockerfile** = recipe for building your app image
2. **docker-compose** = define multi-service architecture
3. Use **multi-stage builds** for smaller production images
4. **Volumes** persist data across container restarts
5. **depends_on** controls startup order
6. Use **.dockerignore** to keep images small
7. Separate **dev** and **prod** configurations
8. Always add **health checks**
