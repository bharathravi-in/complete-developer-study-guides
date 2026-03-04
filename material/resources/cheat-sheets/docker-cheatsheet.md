# Docker Cheat Sheet

## Image Commands
```bash
docker build -t myapp .              # Build image
docker build -t myapp:v1 .           # Build with tag
docker images                        # List images
docker rmi myapp                     # Remove image
docker pull python:3.11-slim         # Pull image
```

## Container Commands
```bash
docker run -p 5000:5000 myapp        # Run container
docker run -d -p 5000:5000 myapp     # Run detached
docker run --rm myapp                # Remove after exit
docker run -e API_KEY=xxx myapp      # With env var
docker run -v ./data:/app/data myapp # Mount volume

docker ps                            # Running containers
docker ps -a                         # All containers
docker stop <id>                     # Stop
docker rm <id>                       # Remove
docker logs <id>                     # View logs
docker logs -f <id>                  # Follow logs
docker exec -it <id> bash            # Shell into container
```

## Docker Compose
```bash
docker-compose up                    # Start all services
docker-compose up -d                 # Detached
docker-compose up --build            # Rebuild
docker-compose down                  # Stop + remove
docker-compose down -v               # + remove volumes
docker-compose logs api              # Service logs
docker-compose exec api bash         # Shell into service
docker-compose ps                    # Status
```

## Dockerfile Template (Python)
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Dependencies first (cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Then code
COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

## Multi-Stage Build
```dockerfile
# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

## Docker Compose Template (AI Stack)
```yaml
version: '3.8'
services:
  api:
    build: .
    ports: ["5000:5000"]
    env_file: .env
    depends_on: [qdrant, redis, postgres]

  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333"]
    volumes: [qdrant_data:/qdrant/storage]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: app
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes: [pg_data:/var/lib/postgresql/data]

volumes:
  qdrant_data:
  pg_data:
```

## .dockerignore
```
__pycache__
*.pyc
.env
.git
.venv
node_modules
*.md
tests/
```

## Common Patterns
```bash
# Rebuild single service
docker-compose up --build api

# View resource usage
docker stats

# Clean everything
docker system prune -a

# Copy file from container
docker cp <id>:/app/data.json ./data.json
```
