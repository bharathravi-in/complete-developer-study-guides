# AI Knowledge Platform — Full Project Blueprint

> **The capstone project** that demonstrates every skill from the 30-day plan.
> Build this incrementally throughout weeks 1-4. Show it in interviews.

---

## Project Overview

**AI Knowledge Platform** — An internal knowledge assistant where teams upload documents and ask questions. Uses RAG to provide accurate, cited answers.

### Features
- Upload documents (PDF, TXT, MD)
- Ask questions in natural language
- Get AI-generated answers with source citations
- Conversation history
- Admin dashboard (usage analytics, document management)
- Mobile chat interface (Flutter)
- Rate limiting, caching, authentication

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        CLIENTS                                │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐ │
│  │  React Admin  │  │  Flutter App │  │  API Consumers     │ │
│  │  Dashboard    │  │  Chat App    │  │  (curl, Postman)   │ │
│  └──────┬───────┘  └──────┬───────┘  └────────┬───────────┘ │
└─────────┼────────────────┼──────────────────┼────────────────┘
          │                │                   │
          ▼                ▼                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    NGINX (Reverse Proxy)                      │
│                 SSL, Load Balancing, Rate Limit               │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│              FLASK API (Gunicorn, 4 workers)                  │
│                                                               │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │
│  │  Auth   │  │ Documents │  │   Chat   │  │   Admin      │ │
│  │  Routes │  │  Routes   │  │  Routes  │  │   Routes     │ │
│  └─────────┘  └──────────┘  └──────────┘  └──────────────┘ │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │              SERVICE LAYER                            │    │
│  │  AuthService | DocumentService | RAGService | LLMSvc │    │
│  └──────────────────────────────────────────────────────┘    │
└──────┬───────────────┬───────────────┬───────────────┬──────┘
       │               │               │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐ ┌─────▼──────┐
│ PostgreSQL  │ │   Qdrant    │ │    Redis    │ │   MinIO    │
│ - Users     │ │ - Vectors   │ │ - Cache     │ │ - Documents│
│ - Documents │ │ - Embeddings│ │ - Sessions  │ │ - Uploads  │
│ - Chats     │ │ - Search    │ │ - Rate limit│ │            │
│ - Messages  │ │             │ │ - Queues    │ │            │
└─────────────┘ └─────────────┘ └─────────────┘ └────────────┘
```

---

## Repository Structure

```
ai-knowledge-platform/
├── README.md                     # Project overview, setup instructions
├── docker-compose.yml            # Full stack orchestration
├── docker-compose.dev.yml        # Dev overrides (hot reload)
├── .env.example                  # Environment variables template
├── .gitignore
│
├── backend/                      # Flask API
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── pytest.ini
│   │
│   ├── app/
│   │   ├── __init__.py           # Flask app factory
│   │   ├── config.py             # Settings (Pydantic BaseSettings)
│   │   ├── extensions.py         # DB, Redis, Qdrant initialization
│   │   │
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # POST /register, /login, /refresh
│   │   │   ├── documents.py      # CRUD /documents, POST /upload
│   │   │   ├── chat.py           # POST /chat, GET /chat/stream
│   │   │   └── admin.py          # GET /stats, /users, /documents
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py   # JWT generation, validation
│   │   │   ├── document_service.py  # Upload, process, index
│   │   │   ├── embedding_service.py # Generate embeddings
│   │   │   ├── vector_service.py    # Qdrant operations
│   │   │   ├── rag_service.py       # RAG pipeline orchestration
│   │   │   ├── llm_service.py       # OpenAI/LLM API calls
│   │   │   └── cache_service.py     # Redis caching layer
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py           # SQLAlchemy User model
│   │   │   ├── document.py       # SQLAlchemy Document model
│   │   │   ├── chat.py           # SQLAlchemy Chat + Message models
│   │   │   └── schemas.py        # Pydantic request/response schemas
│   │   │
│   │   ├── middleware/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py           # JWT middleware
│   │   │   ├── rate_limit.py     # Redis rate limiter
│   │   │   └── error_handler.py  # Global error handler
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── chunker.py        # Text chunking strategies
│   │       ├── pdf_parser.py     # PDF text extraction
│   │       └── tokens.py         # Token counting
│   │
│   └── tests/
│       ├── conftest.py           # Fixtures
│       ├── test_auth.py
│       ├── test_documents.py
│       ├── test_chat.py
│       ├── test_rag_service.py
│       └── test_embedding_service.py
│
├── mobile/                       # Flutter App
│   ├── lib/
│   │   ├── main.dart
│   │   ├── models/
│   │   │   ├── message.dart
│   │   │   ├── chat.dart
│   │   │   └── user.dart
│   │   ├── services/
│   │   │   ├── api_service.dart
│   │   │   └── auth_service.dart
│   │   ├── screens/
│   │   │   ├── login_screen.dart
│   │   │   ├── chat_screen.dart
│   │   │   └── history_screen.dart
│   │   └── widgets/
│   │       ├── message_bubble.dart
│   │       └── chat_input.dart
│   └── pubspec.yaml
│
├── nginx/
│   ├── nginx.conf                # Reverse proxy config
│   └── Dockerfile
│
└── scripts/
    ├── seed_data.py              # Seed documents for testing
    ├── benchmark.py              # Performance benchmarking
    └── migrate.py                # Database migration helper
```

---

## Database Schema

### PostgreSQL Tables

```sql
-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',  -- 'user', 'admin'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,     -- 'pdf', 'txt', 'md'
    file_size INTEGER NOT NULL,
    chunk_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'processing', 'indexed', 'error'
    storage_path VARCHAR(500),            -- MinIO/S3 path
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Chats
CREATE TABLE chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,    -- 'user', 'assistant'
    content TEXT NOT NULL,
    sources JSONB DEFAULT '[]',   -- [{doc_id, chunk_text, score}]
    tokens_used INTEGER DEFAULT 0,
    latency_ms INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## API Endpoints

### Authentication
```
POST   /api/v1/auth/register     # Create account
POST   /api/v1/auth/login        # Get JWT token
POST   /api/v1/auth/refresh      # Refresh token
GET    /api/v1/auth/me           # Current user info
```

### Documents
```
GET    /api/v1/documents         # List user's documents
POST   /api/v1/documents/upload  # Upload document
GET    /api/v1/documents/:id     # Document details
DELETE /api/v1/documents/:id     # Delete document + vectors
GET    /api/v1/documents/:id/status  # Processing status
```

### Chat
```
GET    /api/v1/chats             # List conversations
POST   /api/v1/chats             # New conversation
GET    /api/v1/chats/:id         # Conversation messages
POST   /api/v1/chats/:id/messages     # Send message
GET    /api/v1/chats/:id/stream       # Stream response (SSE)
DELETE /api/v1/chats/:id         # Delete conversation
```

### Admin
```
GET    /api/v1/admin/stats       # Usage statistics
GET    /api/v1/admin/users       # All users
GET    /api/v1/admin/documents   # All documents
GET    /api/v1/admin/usage       # Token usage, costs
```

---

## Docker Compose (Production)

```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@postgres:5432/aiplatform
      - REDIS_URL=redis://redis:6379/0
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      qdrant:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 5s
      retries: 3

  postgres:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: aiplatform
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d aiplatform"]
      interval: 10s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:6333/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  nginx:
    build: ./nginx
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api

volumes:
  postgres_data:
  qdrant_data:
  redis_data:
```

---

## Build Order (Map to 30-Day Plan)

| Week | What to Build | Files to Create |
|------|---------------|-----------------|
| 1 | Flask app skeleton, auth routes, DB models | `app/__init__.py`, `routes/auth.py`, `models/` |
| 2 | RAG pipeline, document upload, chat API | `services/rag_service.py`, `routes/documents.py`, `routes/chat.py` |
| 3 | Redis caching, Docker setup, Flutter app | `services/cache_service.py`, `Dockerfile`, `mobile/` |
| 4 | Polish, admin routes, tests, deploy | `routes/admin.py`, `tests/`, `docker-compose.yml` |

---

## Interview Talking Points

When presenting this project in interviews, highlight:
1. **Architecture**: Clean separation (routes → services → models)
2. **RAG Pipeline**: Chunking → Embedding → Qdrant → LLM with citations
3. **Caching**: Redis cache reducing LLM costs by 50-80%
4. **Production**: Docker, health checks, error handling, rate limiting
5. **Full-Stack**: Backend (Flask) + Mobile (Flutter) + Infrastructure (Docker)
6. **Testing**: pytest with mocking external services
7. **Cost**: Token counting, caching strategy, model selection
