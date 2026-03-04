#!/usr/bin/env python3
"""Day 28 - Final Project Main Application"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from enum import Enum

# ============================================
# CONFIGURATION
# ============================================

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ============================================
# PYDANTIC MODELS
# ============================================

class UserCreate(BaseModel):
    email: str
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    role: MessageRole
    content: str


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str


class ChatResponse(BaseModel):
    conversation_id: int
    message: str
    response: str
    created_at: datetime


class DocumentCreate(BaseModel):
    title: str
    content: str


class DocumentResponse(BaseModel):
    id: int
    title: str
    chunk_count: int
    created_at: datetime


class RAGQuery(BaseModel):
    query: str
    conversation_id: Optional[int] = None


class RAGResponse(BaseModel):
    answer: str
    sources: List[str]
    conversation_id: int


# ============================================
# FAKE DATABASE (Replace with SQLAlchemy)
# ============================================

users_db = {}
conversations_db = {}
documents_db = {}
user_id_counter = 0
conv_id_counter = 0
doc_id_counter = 0


# ============================================
# AUTH UTILITIES
# ============================================

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = users_db.get(username)
    if user is None:
        raise credentials_exception
    return user


# ============================================
# SIMULATED AI SERVICE
# ============================================

class AIService:
    """Simulated AI service. Replace with actual OpenAI calls."""
    
    @staticmethod
    def chat(messages: List[dict], context: str = None) -> str:
        """Generate AI response."""
        # In production, use OpenAI:
        # from openai import OpenAI
        # client = OpenAI()
        # response = client.chat.completions.create(
        #     model="gpt-4",
        #     messages=messages
        # )
        # return response.choices[0].message.content
        
        last_message = messages[-1]["content"] if messages else ""
        
        if context:
            return f"Based on the provided documents: This is a simulated RAG response to '{last_message}'. In production, this would use OpenAI with the context: {context[:100]}..."
        
        return f"This is a simulated AI response to: '{last_message}'. In production, connect to OpenAI API."
    
    @staticmethod
    def embed(text: str) -> List[float]:
        """Generate embedding. Replace with actual embedding model."""
        # In production, use OpenAI:
        # response = client.embeddings.create(
        #     model="text-embedding-3-small",
        #     input=text
        # )
        # return response.data[0].embedding
        
        # Simulated embedding (length 10 for demo)
        import hashlib
        hash_bytes = hashlib.sha256(text.encode()).digest()
        return [b / 255.0 for b in hash_bytes[:10]]


ai_service = AIService()


# ============================================
# FASTAPI APPLICATION
# ============================================

app = FastAPI(
    title="AI Chat API",
    description="Production-ready AI-powered chat backend with RAG",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# AUTH ENDPOINTS
# ============================================

@app.post("/api/v1/auth/register", response_model=UserResponse, tags=["Auth"])
async def register(user: UserCreate):
    """Register a new user."""
    global user_id_counter
    
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_id_counter += 1
    users_db[user.username] = {
        "id": user_id_counter,
        "email": user.email,
        "username": user.username,
        "hashed_password": hash_password(user.password),
        "created_at": datetime.utcnow()
    }
    
    return UserResponse(
        id=user_id_counter,
        email=user.email,
        username=user.username,
        created_at=datetime.utcnow()
    )


@app.post("/api/v1/auth/login", response_model=Token, tags=["Auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token."""
    user = users_db.get(form_data.username)
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(access_token=access_token)


# ============================================
# CHAT ENDPOINTS
# ============================================

@app.post("/api/v1/chat/message", response_model=ChatResponse, tags=["Chat"])
async def send_message(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send message and get AI response."""
    global conv_id_counter
    
    # Create or get conversation
    if request.conversation_id:
        conv_id = request.conversation_id
        if conv_id not in conversations_db:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conv_id_counter += 1
        conv_id = conv_id_counter
        conversations_db[conv_id] = {
            "id": conv_id,
            "user": current_user["username"],
            "messages": [],
            "created_at": datetime.utcnow()
        }
    
    # Add user message
    conversations_db[conv_id]["messages"].append({
        "role": "user",
        "content": request.message
    })
    
    # Get AI response
    response = ai_service.chat(conversations_db[conv_id]["messages"])
    
    # Add assistant message
    conversations_db[conv_id]["messages"].append({
        "role": "assistant",
        "content": response
    })
    
    return ChatResponse(
        conversation_id=conv_id,
        message=request.message,
        response=response,
        created_at=datetime.utcnow()
    )


@app.get("/api/v1/chat/conversations", tags=["Chat"])
async def list_conversations(current_user: dict = Depends(get_current_user)):
    """List user's conversations."""
    user_convs = [
        {"id": c["id"], "created_at": c["created_at"], "message_count": len(c["messages"])}
        for c in conversations_db.values()
        if c["user"] == current_user["username"]
    ]
    return {"conversations": user_convs}


# ============================================
# DOCUMENT ENDPOINTS
# ============================================

@app.post("/api/v1/documents/upload", response_model=DocumentResponse, tags=["Documents"])
async def upload_document(
    doc: DocumentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Upload and index a document for RAG."""
    global doc_id_counter
    
    doc_id_counter += 1
    
    # Simple chunking (in production, use better strategies)
    chunks = [doc.content[i:i+500] for i in range(0, len(doc.content), 500)]
    
    # Generate embeddings for each chunk
    embeddings = [ai_service.embed(chunk) for chunk in chunks]
    
    documents_db[doc_id_counter] = {
        "id": doc_id_counter,
        "user": current_user["username"],
        "title": doc.title,
        "chunks": chunks,
        "embeddings": embeddings,
        "created_at": datetime.utcnow()
    }
    
    return DocumentResponse(
        id=doc_id_counter,
        title=doc.title,
        chunk_count=len(chunks),
        created_at=datetime.utcnow()
    )


@app.get("/api/v1/documents", tags=["Documents"])
async def list_documents(current_user: dict = Depends(get_current_user)):
    """List user's documents."""
    user_docs = [
        {"id": d["id"], "title": d["title"], "chunks": len(d["chunks"])}
        for d in documents_db.values()
        if d["user"] == current_user["username"]
    ]
    return {"documents": user_docs}


# ============================================
# RAG ENDPOINTS
# ============================================

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(x ** 2 for x in b) ** 0.5
    return dot / (norm_a * norm_b) if norm_a and norm_b else 0


@app.post("/api/v1/rag/query", response_model=RAGResponse, tags=["RAG"])
async def rag_query(
    request: RAGQuery,
    current_user: dict = Depends(get_current_user)
):
    """Query documents using RAG."""
    global conv_id_counter
    
    # Embed query
    query_embedding = ai_service.embed(request.query)
    
    # Find relevant chunks
    all_chunks = []
    for doc in documents_db.values():
        if doc["user"] == current_user["username"]:
            for i, (chunk, embedding) in enumerate(zip(doc["chunks"], doc["embeddings"])):
                similarity = cosine_similarity(query_embedding, embedding)
                all_chunks.append({
                    "doc_title": doc["title"],
                    "chunk": chunk,
                    "similarity": similarity
                })
    
    # Sort by similarity and get top chunks
    all_chunks.sort(key=lambda x: x["similarity"], reverse=True)
    top_chunks = all_chunks[:3]
    
    if not top_chunks:
        context = ""
        sources = []
    else:
        context = "\n\n".join([c["chunk"] for c in top_chunks])
        sources = list(set([c["doc_title"] for c in top_chunks]))
    
    # Generate response with context
    messages = [
        {"role": "system", "content": f"Use this context to answer: {context}"},
        {"role": "user", "content": request.query}
    ]
    
    response = ai_service.chat(messages, context)
    
    # Handle conversation
    if request.conversation_id:
        conv_id = request.conversation_id
    else:
        conv_id_counter += 1
        conv_id = conv_id_counter
    
    return RAGResponse(
        answer=response,
        sources=sources,
        conversation_id=conv_id
    )


# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# ============================================
# RUN
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
