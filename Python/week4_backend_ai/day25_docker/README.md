# Day 25 - Docker & Deployment

## Topics Covered
- Docker fundamentals
- Writing Dockerfiles
- Docker Compose for multi-container apps
- Python best practices for containers
- Environment variables & secrets
- CI/CD basics

## Docker Architecture
```
┌──────────────────────────────────────────┐
│              Docker Client               │
│         (docker build, run, etc.)        │
└──────────────────┬───────────────────────┘
                   │
┌──────────────────▼───────────────────────┐
│              Docker Daemon               │
│            (dockerd)                     │
├──────────────────────────────────────────┤
│  Images  │  Containers  │   Networks    │
└──────────────────────────────────────────┘
```

## Project Structure
```
day25_docker/
├── README.md
├── practice.py           # Docker concepts
├── Dockerfile            # Single-stage
├── Dockerfile.multi      # Multi-stage
├── docker-compose.yml    # Multi-container
├── .dockerignore
└── app/
    ├── main.py
    └── requirements.txt
```

## Key Concepts

### 1. Basic Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Multi-stage Build
```dockerfile
# Build stage
FROM python:3.12 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir -r requirements.txt -w /wheels

# Production stage
FROM python:3.12-slim
COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### 3. Docker Compose
```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
  
  redis:
    image: redis:7
```

## Commands
```bash
# Build image
docker build -t myapp:latest .

# Run container
docker run -p 8000:8000 myapp:latest

# Docker Compose
docker compose up -d
docker compose logs -f
docker compose down
```

## Practice Exercises
1. Create a Dockerfile for a FastAPI app
2. Use multi-stage builds to reduce image size
3. Set up Docker Compose with PostgreSQL and Redis
4. Configure environment variables properly
5. Create a CI/CD pipeline with GitHub Actions
