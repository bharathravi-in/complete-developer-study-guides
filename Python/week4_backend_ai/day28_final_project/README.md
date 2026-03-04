# Day 28 - Final Project: AI-Powered Backend

## Project: AI Chat API with RAG

Build a production-ready FastAPI backend with:
- AI chat capabilities (OpenAI integration)
- RAG (Retrieval-Augmented Generation)
- JWT authentication
- PostgreSQL database
- Redis caching
- Docker deployment

## Project Structure
```
day28_final_project/
├── README.md
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
├── alembic.ini
├── alembic/
│   └── versions/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings
│   ├── database.py          # Database setup
│   ├── dependencies.py      # Dependency injection
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py          # Auth endpoints
│   │   ├── chat.py          # Chat endpoints
│   │   └── documents.py     # Document endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── chat.py
│   │   └── document.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── chat.py
│   │   └── document.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── embedding.py
│   │   └── rag.py
│   └── utils/
│       ├── __init__.py
│       └── security.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_api.py
```

## Features
1. **User Authentication**: JWT-based auth with refresh tokens
2. **Chat API**: Conversation with AI using OpenAI
3. **RAG Pipeline**: Upload documents, query with context
4. **Caching**: Redis for session and response caching
5. **Database**: PostgreSQL with SQLAlchemy ORM
6. **Docker**: Full containerization

## API Endpoints
```
POST   /api/v1/auth/register      # Register user
POST   /api/v1/auth/login         # Login, get token
POST   /api/v1/auth/refresh       # Refresh token

GET    /api/v1/chat/conversations # List conversations
POST   /api/v1/chat/conversations # Create conversation
POST   /api/v1/chat/message       # Send message, get AI response

POST   /api/v1/documents/upload   # Upload document
GET    /api/v1/documents          # List documents
DELETE /api/v1/documents/{id}     # Delete document

POST   /api/v1/rag/query          # Query with RAG
```

## Quick Start
```bash
# Clone and setup
cp .env.example .env
# Edit .env with your OpenAI key

# Start with Docker
docker compose up -d

# Or run locally
pip install -r requirements.txt
uvicorn app.main:app --reload

# Access
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

## Learning Outcomes
- Full-stack API development
- AI/LLM integration
- Production deployment patterns
- Clean architecture
