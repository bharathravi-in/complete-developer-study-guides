#!/usr/bin/env python3
"""Day 25 - Docker Concepts for Python Developers"""

print("=" * 50)
print("DOCKER FOR PYTHON DEVELOPERS")
print("=" * 50)


# ============================================
# 1. DOCKERFILE BASICS
# ============================================
print("\n--- 1. Dockerfile Instructions ---")

DOCKERFILE_BASICS = """
Common Dockerfile Instructions:
─────────────────────────────────────────────
FROM        Base image (python:3.12-slim)
WORKDIR     Set working directory
COPY        Copy files from host to image
RUN         Execute commands (build time)
ENV         Set environment variables
EXPOSE      Document exposed ports
CMD         Default command (run time)
ENTRYPOINT  Fixed command prefix
ARG         Build-time variables
VOLUME      Create mount point
USER        Set non-root user
HEALTHCHECK Container health check
"""
print(DOCKERFILE_BASICS)


# ============================================
# 2. DOCKERFILE EXAMPLES
# ============================================
print("\n--- 2. Dockerfile Examples ---")

SIMPLE_DOCKERFILE = '''
# Dockerfile (Simple)
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''

MULTISTAGE_DOCKERFILE = '''
# Dockerfile.multi (Multi-stage)
# Stage 1: Build
FROM python:3.12 AS builder

WORKDIR /build

# Install build dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

# Stage 2: Production
FROM python:3.12-slim

# Security: Run as non-root user
RUN useradd --create-home appuser
USER appuser
WORKDIR /home/appuser/app

# Install pre-built wheels
COPY --from=builder /wheels /wheels
RUN pip install --user --no-cache /wheels/* && rm -rf /wheels

# Copy application
COPY --chown=appuser:appuser . .

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
'''

print("Simple Dockerfile:")
print(SIMPLE_DOCKERFILE)

print("\nMulti-stage Dockerfile:")
print(MULTISTAGE_DOCKERFILE)


# ============================================
# 3. DOCKER COMPOSE
# ============================================
print("\n--- 3. Docker Compose ---")

DOCKER_COMPOSE = '''
# docker-compose.yml
version: "3.9"

services:
  # FastAPI Application
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mydb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    volumes:
      - ./app:/app  # Development mount
    restart: unless-stopped

  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d mydb"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  # Nginx Reverse Proxy (Production)
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - web

volumes:
  postgres_data:
  redis_data:
'''

print(DOCKER_COMPOSE)


# ============================================
# 4. DOCKER COMMANDS
# ============================================
print("\n--- 4. Essential Docker Commands ---")

DOCKER_COMMANDS = """
Building:
  docker build -t myapp:latest .
  docker build -f Dockerfile.prod -t myapp:prod .
  docker build --no-cache -t myapp:latest .

Running:
  docker run -p 8000:8000 myapp:latest
  docker run -d --name myapp myapp:latest
  docker run -it --rm myapp:latest /bin/bash
  docker run -e DATABASE_URL=... myapp:latest
  docker run -v $(pwd):/app myapp:latest

Managing:
  docker ps                          # List running
  docker ps -a                       # List all
  docker logs -f <container>         # Follow logs
  docker exec -it <container> bash   # Shell access
  docker stop <container>            # Stop
  docker rm <container>              # Remove

Images:
  docker images                      # List images
  docker rmi <image>                 # Remove image
  docker image prune                 # Clean unused

Docker Compose:
  docker compose up                  # Start services
  docker compose up -d               # Start detached
  docker compose up --build          # Rebuild
  docker compose down                # Stop & remove
  docker compose logs -f             # Follow logs
  docker compose exec web bash       # Shell into service
  docker compose ps                  # List services
"""

print(DOCKER_COMMANDS)


# ============================================
# 5. ENVIRONMENT VARIABLES
# ============================================
print("\n--- 5. Environment Variables ---")

ENV_HANDLING = """
Methods to pass env variables:
──────────────────────────────

1. Dockerfile ENV:
   ENV DATABASE_URL=postgresql://...
   (Not recommended for secrets!)

2. docker run -e:
   docker run -e DATABASE_URL=... myapp

3. env_file in docker-compose:
   services:
     web:
       env_file:
         - .env
         - .env.local

4. Docker Secrets (Swarm/Production):
   secrets:
     db_password:
       file: ./db_password.txt
   services:
     web:
       secrets:
         - db_password

5. Docker Config:
   configs:
     app_config:
       file: ./config.json
"""

print(ENV_HANDLING)


# ============================================
# 6. PYTHON-SPECIFIC BEST PRACTICES
# ============================================
print("\n--- 6. Python Docker Best Practices ---")

PYTHON_BEST_PRACTICES = """
1. Use official slim images:
   ✓ python:3.12-slim
   ✗ python:3.12 (larger)

2. Set Python environment variables:
   ENV PYTHONDONTWRITEBYTECODE=1
   ENV PYTHONUNBUFFERED=1

3. Install only production dependencies:
   RUN pip install --no-cache-dir -r requirements.txt

4. Use non-root user:
   RUN useradd --create-home appuser
   USER appuser

5. Multi-stage builds for smaller images:
   FROM python:3.12 AS builder
   ...
   FROM python:3.12-slim
   COPY --from=builder ...

6. Use .dockerignore:
   __pycache__
   *.pyc
   .git
   .env
   .venv
   tests/

7. Order COPY commands (cache optimization):
   COPY requirements.txt .       # Changes rarely
   RUN pip install -r requirements.txt
   COPY . .                      # Changes often

8. Health checks:
   HEALTHCHECK --interval=30s --timeout=3s \\
     CMD curl -f http://localhost:8000/health || exit 1
"""

print(PYTHON_BEST_PRACTICES)


# ============================================
# 7. .DOCKERIGNORE
# ============================================
print("\n--- 7. .dockerignore ---")

DOCKERIGNORE = """
# .dockerignore
__pycache__
*.pyc
*.pyo
*.pyd
.Python

# Virtual environments
.venv
venv
env

# Git
.git
.gitignore

# IDE
.vscode
.idea
*.swp

# Testing
.pytest_cache
.coverage
htmlcov
tests/

# Docker
Dockerfile*
docker-compose*
.dockerignore

# Environment files
.env
.env.*
!.env.example

# Docs
*.md
docs/
"""

print(DOCKERIGNORE)


# ============================================
# 8. CI/CD PIPELINE
# ============================================
print("\n--- 8. GitHub Actions CI/CD ---")

GITHUB_ACTIONS = '''
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
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run tests
        run: pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Login to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: myuser/myapp:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to server
        run: |
          ssh ${{ secrets.SERVER_HOST }} "
            docker pull myuser/myapp:latest
            docker compose up -d
          "
'''

print(GITHUB_ACTIONS)


# ============================================
# 9. DEBUGGING CONTAINERS
# ============================================
print("\n--- 9. Debugging Tips ---")

DEBUGGING = """
Debugging Docker Containers:
──────────────────────────────

1. Check logs:
   docker logs <container> -f --tail 100

2. Shell access:
   docker exec -it <container> /bin/bash
   docker exec -it <container> /bin/sh  # Alpine

3. Inspect container:
   docker inspect <container>
   docker inspect --format='{{.State.Health}}' <container>

4. Check resource usage:
   docker stats <container>

5. View filesystem:
   docker diff <container>

6. Copy files out:
   docker cp <container>:/app/logs ./logs

7. Run with interactive shell:
   docker run -it --entrypoint /bin/bash myapp

8. Override command:
   docker run myapp python -c "print('debug')"
"""

print(DEBUGGING)


# ============================================
# 10. SUMMARY
# ============================================
print("\n" + "=" * 50)
print("DOCKER DEPLOYMENT CHECKLIST")
print("=" * 50)
print("""
Development:
  □ Create Dockerfile (multi-stage)
  □ Create .dockerignore
  □ Create docker-compose.yml
  □ Test locally with docker compose

Security:
  □ Use non-root user
  □ No secrets in Dockerfile
  □ Use .env files or secrets
  □ Scan images for vulnerabilities

Optimization:
  □ Use slim base images
  □ Order COPY for cache efficiency
  □ Install only production deps
  □ Multi-stage builds

Production:
  □ Add health checks
  □ Configure logging
  □ Set restart policy
  □ Resource limits
  □ CI/CD pipeline
""")
