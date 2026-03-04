# Multi-stage Dockerfile for FastAPI Application
# Optimized for production with security best practices

# ============================================
# Stage 1: Builder
# ============================================
FROM python:3.12-slim AS builder

# Set build-time variables
ARG POETRY_VERSION=1.7.0

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy dependency files
COPY requirements.txt .

# Create wheels for all dependencies
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt


# ============================================
# Stage 2: Production
# ============================================
FROM python:3.12-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid 1000 --create-home appuser

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /home/appuser/app

# Copy pre-built wheels from builder stage
COPY --from=builder /wheels /wheels

# Install dependencies as non-root user
RUN pip install --user --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Copy application code
COPY --chown=appuser:appgroup ./app .

# Switch to non-root user
USER appuser

# Add local bin to PATH for user-installed packages
ENV PATH="/home/appuser/.local/bin:$PATH"

# Expose the application port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


# ============================================
# Stage 3: Development (optional)
# ============================================
FROM production AS development

USER root

# Install development dependencies
RUN pip install --no-cache-dir pytest pytest-cov black ruff mypy

USER appuser

# Mount point for live code reloading
VOLUME ["/home/appuser/app"]

# Development command with reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
