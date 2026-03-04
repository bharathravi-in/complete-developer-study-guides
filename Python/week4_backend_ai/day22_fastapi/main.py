#!/usr/bin/env python3
"""Day 22 - Complete FastAPI Application with JWT Auth"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta

from models import (
    UserCreate, UserResponse, ItemCreate, ItemResponse, ItemUpdate,
    Token, LoginRequest, MessageResponse, ErrorResponse
)
from auth import (
    create_access_token, verify_token, authenticate_user,
    get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, fake_users_db
)


# ============================================
# APP INITIALIZATION
# ============================================

app = FastAPI(
    title="Day 22 - FastAPI Tutorial",
    description="A complete REST API with JWT authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ============================================
# FAKE DATABASES
# ============================================

items_db: dict[int, dict] = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "owner_id": 1, "description": None, "tax": 80.0},
    2: {"id": 2, "name": "Mouse", "price": 29.99, "owner_id": 1, "description": "Wireless", "tax": 2.0},
}
next_item_id = 3


# ============================================
# DEPENDENCIES
# ============================================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Dependency to get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = verify_token(token, credentials_exception)
    user = fake_users_db.get(username)
    
    if user is None:
        raise credentials_exception
    if user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user


async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """Dependency to ensure user is active."""
    return current_user


# ============================================
# ROOT ENDPOINTS
# ============================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API info."""
    return {
        "message": "Welcome to FastAPI Tutorial",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# ============================================
# AUTHENTICATION ENDPOINTS
# ============================================

@app.post("/auth/login", response_model=Token, tags=["Auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with username and password.
    Returns JWT access token.
    """
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@app.get("/auth/me", tags=["Auth"])
async def get_me(current_user: dict = Depends(get_current_active_user)):
    """Get current user info (protected route)."""
    return {
        "username": current_user["username"],
        "email": current_user["email"],
        "full_name": current_user["full_name"]
    }


# ============================================
# ITEMS CRUD ENDPOINTS
# ============================================

@app.get("/items", response_model=List[dict], tags=["Items"])
async def get_items(
    skip: int = 0,
    limit: int = 10,
    current_user: dict = Depends(get_current_active_user)
):
    """Get all items (paginated)."""
    items = list(items_db.values())[skip:skip + limit]
    return items


@app.get("/items/{item_id}", tags=["Items"])
async def get_item(
    item_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Get a specific item by ID."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]


@app.post("/items", status_code=status.HTTP_201_CREATED, tags=["Items"])
async def create_item(
    item: ItemCreate,
    current_user: dict = Depends(get_current_active_user)
):
    """Create a new item."""
    global next_item_id
    
    new_item = {
        "id": next_item_id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "tax": item.tax,
        "owner_id": 1,  # Would be current_user.id in real app
        "created_at": datetime.utcnow().isoformat()
    }
    
    items_db[next_item_id] = new_item
    next_item_id += 1
    
    return new_item


@app.put("/items/{item_id}", tags=["Items"])
async def update_item(
    item_id: int,
    item: ItemUpdate,
    current_user: dict = Depends(get_current_active_user)
):
    """Update an existing item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    stored_item = items_db[item_id]
    update_data = item.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        stored_item[field] = value
    
    return stored_item


@app.delete("/items/{item_id}", tags=["Items"])
async def delete_item(
    item_id: int,
    current_user: dict = Depends(get_current_active_user)
):
    """Delete an item."""
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    del items_db[item_id]
    return MessageResponse(message=f"Item {item_id} deleted successfully")


# ============================================
# ERROR HANDLING
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return ErrorResponse(
        error=exc.detail,
        status_code=exc.status_code
    )


# ============================================
# RUN (for development)
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
