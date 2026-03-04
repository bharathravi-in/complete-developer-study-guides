#!/usr/bin/env python3
"""Day 22 - Pydantic Models for FastAPI"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ============================================
# 1. BASIC MODELS
# ============================================

class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    """Model for user creation (includes password)."""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v


class UserResponse(UserBase):
    """Model for user response (excludes password)."""
    id: int
    created_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True  # Pydantic v2 (formerly orm_mode)


class UserInDB(UserResponse):
    """User model with hashed password (for internal use)."""
    hashed_password: str


# ============================================
# 2. ITEM/PRODUCT MODELS
# ============================================

class ItemBase(BaseModel):
    """Base item model."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    tax: Optional[float] = Field(None, ge=0)


class ItemCreate(ItemBase):
    """Model for item creation."""
    pass


class ItemUpdate(BaseModel):
    """Model for item update (all optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    tax: Optional[float] = Field(None, ge=0)


class ItemResponse(ItemBase):
    """Model for item response."""
    id: int
    owner_id: int
    created_at: datetime
    
    @property
    def price_with_tax(self) -> float:
        return self.price + (self.tax or 0)
    
    class Config:
        from_attributes = True


# ============================================
# 3. AUTH MODELS
# ============================================

class Token(BaseModel):
    """JWT Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class TokenData(BaseModel):
    """Data extracted from JWT token."""
    username: Optional[str] = None
    scopes: List[str] = []


class LoginRequest(BaseModel):
    """Login request model."""
    username: str
    password: str


# ============================================
# 4. API RESPONSE MODELS
# ============================================

class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    success: bool = True


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[dict]
    total: int
    page: int
    per_page: int
    pages: int


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    status_code: int


# ============================================
# DEMONSTRATION
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("PYDANTIC MODELS DEMONSTRATION")
    print("=" * 50)
    
    # Create user
    print("\n--- User Validation ---")
    try:
        user = UserCreate(
            email="john@example.com",
            username="johndoe",
            password="SecurePass123",
            full_name="John Doe"
        )
        print(f"Valid user: {user.username}")
    except Exception as e:
        print(f"Validation error: {e}")
    
    # Invalid password
    try:
        bad_user = UserCreate(
            email="jane@example.com",
            username="janedoe",
            password="weakpass"  # No uppercase or digit
        )
    except ValueError as e:
        print(f"Password validation failed: {e}")
    
    # Item with price
    print("\n--- Item Model ---")
    item = ItemCreate(
        name="Python Book",
        description="Learn Python in 30 days",
        price=29.99,
        tax=2.50
    )
    print(f"Item: {item.name}, Price: ${item.price}")
    print(f"JSON: {item.model_dump_json()}")
    
    # Paginated response
    print("\n--- Paginated Response ---")
    paginated = PaginatedResponse(
        items=[{"id": 1}, {"id": 2}],
        total=100,
        page=1,
        per_page=10,
        pages=10
    )
    print(f"Page {paginated.page} of {paginated.pages}")
