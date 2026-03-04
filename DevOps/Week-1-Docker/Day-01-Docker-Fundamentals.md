# Day 1: Docker Fundamentals

## 📚 Topics to Cover (3-4 hours)

---

## 1. Containers vs Virtual Machines

```
Virtual Machines                    Containers
┌─────────┐ ┌─────────┐           ┌─────────┐ ┌─────────┐
│  App A   │ │  App B   │           │  App A   │ │  App B   │
├──────────┤ ├──────────┤           ├──────────┤ ├──────────┤
│ Guest OS │ │ Guest OS │           │  Bins/   │ │  Bins/   │
├──────────┤ ├──────────┤           │  Libs    │ │  Libs    │
│          Hypervisor          │    ├──────────────────────┤
├──────────────────────────────┤    │    Docker Engine      │
│        Host OS               │    ├──────────────────────┤
├──────────────────────────────┤    │      Host OS          │
│       Hardware               │    ├──────────────────────┤
└──────────────────────────────┘    │     Hardware          │
                                    └──────────────────────┘
```

| Feature | VM | Container |
|---------|-----|-----------|
| Isolation | Full OS | Process-level |
| Start time | Minutes | Seconds |
| Size | GBs | MBs |
| Performance | Near-native | Native |
| Density | 10s per host | 100s per host |
| Resource usage | High (full OS) | Low (shared kernel) |

---

## 2. Docker Architecture

```
┌─────────────────────────────────────────┐
│           Docker Client (CLI)            │
│  docker build | docker run | docker pull │
└──────────────────┬──────────────────────┘
                   │ REST API
┌──────────────────▼──────────────────────┐
│           Docker Daemon (dockerd)        │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐ │
│  │ Images   │ │Containers│ │ Networks │ │
│  └──────────┘ └─────────┘ └──────────┘ │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         Container Runtime (containerd)   │
│              + runc                      │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│           Linux Kernel                   │
│  namespaces | cgroups | union filesystems│
└─────────────────────────────────────────┘
```

### Key Concepts
- **Image**: Read-only template with application + dependencies
- **Container**: Running instance of an image
- **Registry**: Storage for images (Docker Hub, ECR, GCR)
- **Dockerfile**: Recipe for building images
- **Layer**: Each instruction creates a layer (cached)

---

## 3. Essential Commands

```bash
# Image Management
docker pull nginx:latest              # Download image
docker images                         # List images
docker build -t myapp:1.0 .          # Build from Dockerfile
docker tag myapp:1.0 registry/myapp  # Tag image
docker push registry/myapp:1.0      # Push to registry
docker rmi image_id                   # Remove image
docker image prune -a                 # Remove unused images

# Container Management
docker run -d -p 8080:80 --name web nginx    # Run detached
docker run -it ubuntu bash                    # Interactive shell
docker run --rm alpine echo "hello"           # Auto-remove
docker ps                                     # List running
docker ps -a                                  # List all
docker stop container_id                      # Stop
docker start container_id                     # Start
docker restart container_id                   # Restart
docker rm container_id                        # Remove
docker rm -f $(docker ps -aq)                 # Remove all

# Container Inspection
docker logs container_id              # View logs
docker logs -f --tail 100 container   # Follow last 100 lines
docker exec -it container bash        # Shell into container
docker inspect container_id           # Full details
docker stats                          # Resource usage
docker top container_id               # Running processes

# System
docker system df                      # Disk usage
docker system prune -a                # Clean everything
docker info                           # System info
```

---

## 4. Dockerfile Basics

```dockerfile
# Base image
FROM node:20-alpine

# Metadata
LABEL maintainer="bharath@example.com"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Copy package files (leverage cache)
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Set environment variables
ENV NODE_ENV=production
ENV PORT=3000

# Expose port (documentation)
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Start command
CMD ["node", "server.js"]
```

### Dockerfile Instructions Reference

| Instruction | Purpose |
|------------|---------|
| `FROM` | Base image |
| `WORKDIR` | Set working directory |
| `COPY` | Copy files from host |
| `ADD` | Copy + extract archives + URLs |
| `RUN` | Execute command during build |
| `CMD` | Default command (overridable) |
| `ENTRYPOINT` | Main executable (not easily overridable) |
| `ENV` | Set environment variable |
| `ARG` | Build-time variable |
| `EXPOSE` | Document ports |
| `VOLUME` | Create mount point |
| `USER` | Set runtime user |
| `HEALTHCHECK` | Container health check |
| `LABEL` | Metadata |

---

## 5. Docker Run Options

```bash
docker run \
  -d                          # Detached mode
  --name myapp                # Container name
  -p 8080:3000                # Port mapping (host:container)
  -p 127.0.0.1:8080:3000     # Bind to specific interface
  -v /host/path:/container/path  # Bind mount
  -v myvolume:/data           # Named volume
  --tmpfs /tmp                # Temp filesystem
  -e NODE_ENV=production      # Environment variable
  --env-file .env             # Load env file
  -w /app                     # Working directory
  --restart unless-stopped    # Restart policy
  --memory 512m               # Memory limit
  --cpus 0.5                  # CPU limit
  --network mynetwork         # Network
  --rm                        # Auto-remove on exit
  --read-only                 # Read-only filesystem
  --user 1000:1000            # Run as specific user
  myimage:latest
```

---

## 6. Layer Caching

```dockerfile
# BAD - Cache busted on every code change
FROM node:20-alpine
COPY . .                    # ← Any file change invalidates cache
RUN npm install
CMD ["node", "server.js"]

# GOOD - Dependencies cached separately
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./       # ← Only changes when deps change
RUN npm ci                  # ← Cached if package.json unchanged
COPY . .                    # ← Only app code layer changes
CMD ["node", "server.js"]
```

---

## 🎯 Interview Questions

### Q1: What are Docker namespaces and cgroups?
**A:** **Namespaces** provide isolation: PID (processes), NET (networking), MNT (filesystems), UTS (hostname), IPC (inter-process), USER (users). **Cgroups** limit resources: CPU, memory, I/O, network bandwidth. Together they create isolated, resource-limited environments.

### Q2: What's the difference between CMD and ENTRYPOINT?
**A:** `CMD` provides default arguments that can be overridden: `docker run image cmd`. `ENTRYPOINT` defines the main executable: `docker run image args-to-entrypoint`. Best practice: use `ENTRYPOINT` for the executable and `CMD` for default arguments.

### Q3: How do Docker layers work?
**A:** Each Dockerfile instruction creates a read-only layer. Layers are cached and shared between images. When a layer changes, all subsequent layers are rebuilt. Order instructions from least to most frequently changing for optimal caching.

### Q4: What is a Docker image vs container?
**A:** An **image** is a read-only template (class). A **container** is a running instance (object) with a writable layer on top. Multiple containers can share the same image. Images are built in layers, containers add a thin writable layer.

### Q5: How do you reduce Docker image size?
**A:** Use Alpine/slim base images, multi-stage builds, combine RUN commands, use .dockerignore, remove caches (`apt-get clean`, `npm cache clean`), minimize layers, use `--no-install-recommends`.

---

## 📝 Practice Exercises

1. Containerize a Node.js Express API
2. Create a Python Flask app with Dockerfile
3. Build an Angular app and serve with Nginx in a container
4. Compare image sizes: Ubuntu vs Alpine vs Distroless base images
