# Advanced Flask — Middleware, WebSockets, Background Tasks & Deployment

> Advanced patterns not covered in the basic Flask guide.

---

## 1. Application Factory Pattern (Production)

```python
# app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name: str = "production") -> Flask:
    app = Flask(__name__)
    
    # Load config
    configs = {
        "development": "app.config.DevelopmentConfig",
        "testing": "app.config.TestingConfig",
        "production": "app.config.ProductionConfig",
    }
    app.config.from_object(configs.get(config_name, configs["production"]))
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config["ALLOWED_ORIGINS"])
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.chat import chat_bp
    from app.routes.documents import docs_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(chat_bp, url_prefix="/api/v1/chat")
    app.register_blueprint(docs_bp, url_prefix="/api/v1/documents")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli(app)
    
    return app
```

### Config Classes
```python
# app/config.py
from pydantic_settings import BaseSettings

class BaseConfig(BaseSettings):
    SECRET_KEY: str = "change-me"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    REDIS_URL: str = "redis://localhost:6379/0"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    OPENAI_API_KEY: str = ""
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///dev.db"

class TestingConfig(BaseConfig):
    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"

class ProductionConfig(BaseConfig):
    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = "postgresql://..."
```

---

## 2. Custom Middleware Stack

### Request ID Middleware
```python
import uuid
from flask import g, request

@app.before_request
def add_request_id():
    """Add unique ID to every request for tracing."""
    g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    g.start_time = time.time()

@app.after_request
def add_response_headers(response):
    """Add tracing headers to response."""
    response.headers["X-Request-ID"] = g.get("request_id", "unknown")
    if hasattr(g, "start_time"):
        elapsed = (time.time() - g.start_time) * 1000
        response.headers["X-Response-Time"] = f"{elapsed:.2f}ms"
    return response
```

### Authentication Middleware (Decorator)
```python
from functools import wraps
import jwt

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify(error="Missing token"), 401
        try:
            payload = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
            g.user_id = payload["sub"]
            g.user_role = payload.get("role", "user")
            g.tenant_id = payload.get("tenant_id")
        except jwt.ExpiredSignatureError:
            return jsonify(error="Token expired"), 401
        except jwt.InvalidTokenError:
            return jsonify(error="Invalid token"), 401
        return f(*args, **kwargs)
    return decorated

def require_role(role: str):
    """Role-based access control."""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            if g.user_role != role:
                return jsonify(error="Insufficient permissions"), 403
            return f(*args, **kwargs)
        return decorated
    return decorator

# Usage
@bp.route("/admin/stats")
@require_role("admin")
def admin_stats():
    return jsonify(stats)
```

### Rate Limiting Middleware
```python
import redis
import time

redis_client = redis.Redis.from_url(app.config["REDIS_URL"])

def rate_limit(limit: int = 30, window: int = 60):
    """Decorator-based rate limiting with Redis."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            identifier = g.get("user_id", request.remote_addr)
            key = f"rate:{f.__name__}:{identifier}"
            
            pipe = redis_client.pipeline()
            now = time.time()
            pipe.zremrangebyscore(key, 0, now - window)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, window)
            _, _, count, _ = pipe.execute()
            
            if count > limit:
                return jsonify(error="Rate limit exceeded"), 429
            
            response = f(*args, **kwargs)
            return response
        return decorated
    return decorator

@bp.route("/chat", methods=["POST"])
@require_auth
@rate_limit(limit=30, window=60)  # 30 requests per minute
def chat():
    ...
```

---

## 3. Server-Sent Events (SSE) — Full Implementation

```python
from flask import Response, stream_with_context
import json
import queue
import threading

class SSEStream:
    """Server-Sent Events stream manager."""
    
    def __init__(self):
        self._queue: queue.Queue = queue.Queue()
        self._closed = False
    
    def send(self, data: dict, event: str = "message"):
        if not self._closed:
            self._queue.put(f"event: {event}\ndata: {json.dumps(data)}\n\n")
    
    def close(self):
        self._closed = True
        self._queue.put(None)
    
    def stream(self):
        while True:
            msg = self._queue.get()
            if msg is None:
                break
            yield msg

@bp.route("/chat/<chat_id>/stream", methods=["POST"])
@require_auth
def stream_chat(chat_id: str):
    data = request.get_json()
    question = data["message"]
    
    def generate():
        try:
            # Step 1: Send retrieval status
            yield f"data: {json.dumps({'type': 'status', 'message': 'Searching documents...'})}\n\n"
            
            # Step 2: Retrieve
            chunks = rag_service.retrieve(question)
            yield f"data: {json.dumps({'type': 'status', 'message': f'Found {len(chunks)} relevant chunks'})}\n\n"
            
            # Step 3: Stream LLM response
            yield f"data: {json.dumps({'type': 'status', 'message': 'Generating answer...'})}\n\n"
            
            full_response = ""
            stream = openai_client.chat.completions.create(
                model="gpt-4",
                messages=build_prompt(question, chunks),
                stream=True,
            )
            
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    full_response += delta.content
                    yield f"data: {json.dumps({'type': 'token', 'content': delta.content})}\n\n"
            
            # Step 4: Send sources and completion
            sources = [{"text": c.text[:100], "score": c.score} for c in chunks]
            yield f"data: {json.dumps({'type': 'sources', 'sources': sources})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'total_length': len(full_response)})}\n\n"
            
            # Step 5: Save to database (after streaming)
            save_message(chat_id, question, full_response, sources)
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )
```

### Frontend SSE Client
```javascript
// JavaScript client for SSE
function streamChat(chatId, message) {
    const response = await fetch(`/api/v1/chat/${chatId}/stream`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ message }),
    });

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const text = decoder.decode(value);
        const lines = text.split('\n');

        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = JSON.parse(line.slice(6));
                
                switch (data.type) {
                    case 'token':
                        appendToChat(data.content);
                        break;
                    case 'sources':
                        showSources(data.sources);
                        break;
                    case 'done':
                        finishChat();
                        break;
                    case 'error':
                        showError(data.message);
                        break;
                }
            }
        }
    }
}
```

---

## 4. Background Tasks with Celery

### Setup
```python
# tasks/__init__.py
from celery import Celery

def make_celery(app=None):
    celery = Celery(
        "tasks",
        broker="redis://localhost:6379/0",
        backend="redis://localhost:6379/1",
    )
    celery.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        task_track_started=True,
        task_time_limit=600,  # 10 min max
    )
    if app:
        celery.conf.update(app.config)
    return celery

celery_app = make_celery()
```

### Document Processing Task
```python
# tasks/document_tasks.py
from celery import shared_task

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_document(self, doc_id: str):
    """Process uploaded document: extract → chunk → embed → index."""
    try:
        # Update status
        update_doc_status(doc_id, "processing")
        
        # Extract text
        doc = get_document(doc_id)
        text = extract_text(doc.file_path, doc.file_type)
        
        # Chunk
        chunks = chunker.chunk(text, source=doc_id)
        update_doc_status(doc_id, "chunking", chunk_count=len(chunks))
        
        # Embed (batch)
        batch_size = 100
        all_vectors = []
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            vectors = embedding_service.embed([c.text for c in batch])
            all_vectors.extend(vectors)
            # Report progress
            self.update_state(
                state="PROGRESS",
                meta={"current": i + len(batch), "total": len(chunks)}
            )
        
        # Store in Qdrant
        vector_service.upsert(chunks, all_vectors)
        update_doc_status(doc_id, "indexed", chunk_count=len(chunks))
        
        return {"doc_id": doc_id, "chunks": len(chunks), "status": "indexed"}
    
    except Exception as e:
        update_doc_status(doc_id, "error", error=str(e))
        raise self.retry(exc=e)

# Trigger from route
@bp.route("/documents/upload", methods=["POST"])
@require_auth
def upload():
    file = request.files["document"]
    doc = save_document(file, g.user_id)
    task = process_document.delay(doc.id)
    return jsonify({
        "document_id": doc.id,
        "task_id": task.id,
        "status": "processing"
    }), 202

# Check progress
@bp.route("/documents/<doc_id>/status")
@require_auth
def check_status(doc_id: str):
    doc = get_document(doc_id)
    return jsonify({
        "id": doc.id,
        "status": doc.status,
        "chunk_count": doc.chunk_count,
    })
```

---

## 5. Deployment with Gunicorn + Nginx

### Gunicorn Configuration
```python
# gunicorn.conf.py
import multiprocessing

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"  # Async workers for I/O-bound (LLM calls)
worker_connections = 1000
timeout = 120  # LLM calls can be slow

# Server
bind = "0.0.0.0:5000"
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 8190
limit_request_fields = 100

# Hooks
def on_starting(server):
    print("Starting Gunicorn server...")

def post_fork(server, worker):
    print(f"Worker {worker.pid} spawned")
```

### Nginx Configuration
```nginx
upstream flask_app {
    server 127.0.0.1:5000;
    keepalive 32;
}

server {
    listen 80;
    server_name api.yourapp.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourapp.com;
    
    ssl_certificate /etc/ssl/certs/cert.pem;
    ssl_certificate_key /etc/ssl/private/key.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Max upload size
    client_max_body_size 50M;
    
    # Proxy to Flask
    location /api/ {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Request-ID $request_id;
        
        # Timeouts for LLM calls
        proxy_read_timeout 120s;
        proxy_connect_timeout 10s;
    }
    
    # SSE streaming — disable buffering
    location /api/v1/chat/stream {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_cache off;
        chunked_transfer_encoding off;
    }
    
    # Health check
    location /health {
        proxy_pass http://flask_app;
        access_log off;
    }
}
```

### Run Commands
```bash
# Development
flask run --debug --port 5000

# Production
gunicorn -c gunicorn.conf.py "app:create_app()"

# With Celery worker
celery -A tasks worker --loglevel=info --concurrency=4

# With Celery beat (scheduled tasks)
celery -A tasks beat --loglevel=info
```

---

## 6. Flask CLI Commands

```python
import click

def register_cli(app: Flask):
    @app.cli.command("seed")
    @click.argument("count", default=10)
    def seed_data(count):
        """Seed database with test data."""
        from app.seeds import seed_users, seed_documents
        seed_users(count)
        seed_documents(count * 5)
        click.echo(f"Seeded {count} users and {count * 5} documents")

    @app.cli.command("reindex")
    @click.option("--doc-id", default=None, help="Specific document ID")
    def reindex(doc_id):
        """Re-index documents in Qdrant."""
        if doc_id:
            process_document(doc_id)
        else:
            docs = get_all_documents()
            for doc in docs:
                process_document(doc.id)
        click.echo("Reindexing complete")

    @app.cli.command("stats")
    def show_stats():
        """Show system statistics."""
        from app.services import get_system_stats
        stats = get_system_stats()
        for key, value in stats.items():
            click.echo(f"  {key}: {value}")
```

```bash
flask seed 50
flask reindex
flask reindex --doc-id abc123
flask stats
```

---

## Key Takeaways
1. **App Factory**: Always use `create_app()` for testability and configuration
2. **Middleware stack**: Request ID → Auth → Rate Limit → Route → Error Handler
3. **SSE streaming**: Disable all buffering (Gunicorn, Nginx, browser)
4. **Celery**: Background processing for document indexing (don't block the API)
5. **Gunicorn**: Use gevent workers for I/O-bound AI workloads
6. **Nginx**: Reverse proxy with special SSE config
