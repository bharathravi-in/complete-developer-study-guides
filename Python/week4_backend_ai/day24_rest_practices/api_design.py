#!/usr/bin/env python3
"""Day 24 - REST API Design Implementation with FastAPI"""

from fastapi import FastAPI, HTTPException, Query, Path, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Generic, TypeVar
from datetime import datetime
from enum import Enum
import math


# ============================================
# APP SETUP
# ============================================

app = FastAPI(
    title="REST API Best Practices Demo",
    version="1.0.0",
    description="Demonstrates RESTful API design patterns",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# GENERIC RESPONSE MODELS
# ============================================

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata."""
    page: int
    per_page: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    data: List[T]
    pagination: PaginationMeta


class FieldError(BaseModel):
    """Field-level validation error."""
    field: str
    message: str
    code: str


class ErrorResponse(BaseModel):
    """Standardized error response."""
    code: str
    message: str
    status: int
    details: Optional[List[FieldError]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Generic success response."""
    message: str
    success: bool = True


# ============================================
# DOMAIN MODELS
# ============================================

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    status: Optional[UserStatus] = None


class UserResponse(UserBase):
    id: int
    status: UserStatus
    created_at: datetime
    _links: dict = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    status: UserStatus


# ============================================
# FAKE DATABASE
# ============================================

users_db = {
    1: {
        "id": 1, "email": "john@example.com", "username": "johndoe",
        "full_name": "John Doe", "status": "active",
        "created_at": datetime(2024, 1, 1)
    },
    2: {
        "id": 2, "email": "jane@example.com", "username": "janesmith",
        "full_name": "Jane Smith", "status": "active",
        "created_at": datetime(2024, 1, 15)
    },
    3: {
        "id": 3, "email": "bob@example.com", "username": "bobwilson",
        "full_name": "Bob Wilson", "status": "inactive",
        "created_at": datetime(2024, 2, 1)
    },
}
next_id = 4


# ============================================
# HELPERS
# ============================================

def add_hateoas_links(user: dict, request: Request) -> dict:
    """Add HATEOAS links to user response."""
    user_id = user["id"]
    base_url = str(request.base_url).rstrip("/")
    
    user["_links"] = {
        "self": {"href": f"{base_url}/api/v1/users/{user_id}"},
        "posts": {"href": f"{base_url}/api/v1/users/{user_id}/posts"},
        "update": {"href": f"{base_url}/api/v1/users/{user_id}", "method": "PATCH"},
        "delete": {"href": f"{base_url}/api/v1/users/{user_id}", "method": "DELETE"},
    }
    return user


def paginate_items(
    items: list,
    page: int,
    per_page: int
) -> tuple[list, PaginationMeta]:
    """Create pagination for a list of items."""
    total = len(items)
    pages = math.ceil(total / per_page) if total > 0 else 1
    
    start = (page - 1) * per_page
    end = start + per_page
    paginated = items[start:end]
    
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )
    
    return paginated, meta


# ============================================
# EXCEPTION HANDLERS
# ============================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    error = ErrorResponse(
        code=exc.detail if isinstance(exc.detail, str) else "ERROR",
        message=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        status=exc.status_code
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": error.model_dump()}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    error = ErrorResponse(
        code="INTERNAL_ERROR",
        message="An unexpected error occurred",
        status=500
    )
    return JSONResponse(
        status_code=500,
        content={"error": error.model_dump()}
    )


# ============================================
# API v1 ENDPOINTS
# ============================================

# --- LIST USERS ---
@app.get(
    "/api/v1/users",
    response_model=PaginatedResponse[UserListResponse],
    tags=["Users"]
)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[UserStatus] = Query(None, description="Filter by status"),
    sort: str = Query("id", description="Sort field (prefix with - for desc)"),
    q: Optional[str] = Query(None, description="Search query"),
):
    """
    Get paginated list of users.
    
    Supports:
    - Pagination: page, per_page
    - Filtering: status, q (search)
    - Sorting: sort (e.g., 'username', '-created_at')
    """
    # Filter
    items = list(users_db.values())
    
    if status:
        items = [u for u in items if u["status"] == status.value]
    
    if q:
        items = [
            u for u in items 
            if q.lower() in u["username"].lower() or q.lower() in u["email"].lower()
        ]
    
    # Sort
    desc = sort.startswith("-")
    sort_field = sort.lstrip("-")
    if sort_field in ["id", "username", "email", "created_at"]:
        items.sort(key=lambda x: x.get(sort_field, ""), reverse=desc)
    
    # Paginate
    paginated, meta = paginate_items(items, page, per_page)
    
    return {"data": paginated, "pagination": meta}


# --- GET USER ---
@app.get(
    "/api/v1/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"]
)
async def get_user(
    request: Request,
    user_id: int = Path(..., ge=1, description="User ID"),
):
    """Get a single user by ID with HATEOAS links."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="USER_NOT_FOUND"
        )
    
    user = users_db[user_id].copy()
    return add_hateoas_links(user, request)


# --- CREATE USER ---
@app.post(
    "/api/v1/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Users"]
)
async def create_user(request: Request, user_in: UserCreate):
    """Create a new user."""
    global next_id
    
    # Check for duplicate email
    if any(u["email"] == user_in.email for u in users_db.values()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="EMAIL_ALREADY_EXISTS"
        )
    
    user = {
        "id": next_id,
        "email": user_in.email,
        "username": user_in.username,
        "full_name": user_in.full_name,
        "status": UserStatus.PENDING.value,
        "created_at": datetime.utcnow()
    }
    
    users_db[next_id] = user
    next_id += 1
    
    return add_hateoas_links(user.copy(), request)


# --- UPDATE USER (PATCH) ---
@app.patch(
    "/api/v1/users/{user_id}",
    response_model=UserResponse,
    tags=["Users"]
)
async def update_user(
    request: Request,
    user_id: int,
    user_in: UserUpdate
):
    """Partially update a user."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="USER_NOT_FOUND"
        )
    
    user = users_db[user_id]
    update_data = user_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if value is not None:
            user[field] = value.value if isinstance(value, Enum) else value
    
    return add_hateoas_links(user.copy(), request)


# --- DELETE USER ---
@app.delete(
    "/api/v1/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Users"]
)
async def delete_user(user_id: int):
    """Delete a user."""
    if user_id not in users_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="USER_NOT_FOUND"
        )
    
    del users_db[user_id]
    return None


# --- USER SUB-RESOURCES ---
@app.get("/api/v1/users/{user_id}/posts", tags=["Users"])
async def get_user_posts(user_id: int):
    """Get posts by user (sub-resource example)."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="USER_NOT_FOUND")
    
    return {
        "data": [
            {"id": 1, "title": "Hello World", "author_id": user_id},
            {"id": 2, "title": "REST API Guide", "author_id": user_id},
        ],
        "pagination": {"page": 1, "total": 2}
    }


# ============================================
# HEALTH & STATUS
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
