#!/usr/bin/env python3
"""Day 22 - FastAPI Practice Exercises"""

from fastapi import FastAPI, HTTPException, Query, Path, Body
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

print("=" * 50)
print("FASTAPI CONCEPTS (WITHOUT RUNNING SERVER)")
print("=" * 50)


# ============================================
# 1. PATH PARAMETERS
# ============================================
print("\n--- 1. Path Parameters ---")

"""
Path parameters extract values from the URL path.

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

URL: /users/42 → user_id = 42

Key points:
- Type hints enable automatic validation
- Invalid types return 422 Unprocessable Entity
- Use Path() for additional validation
"""

# Simulating path parameter validation
def validate_user_id(user_id: int) -> dict:
    """Simulates FastAPI path parameter handling."""
    if user_id <= 0:
        raise ValueError("user_id must be positive")
    return {"user_id": user_id, "validated": True}

print(f"Valid user_id: {validate_user_id(42)}")
try:
    validate_user_id(-1)
except ValueError as e:
    print(f"Invalid user_id: {e}")


# ============================================
# 2. QUERY PARAMETERS
# ============================================
print("\n--- 2. Query Parameters ---")

"""
Query parameters come after ? in URLs.

@app.get("/items")
async def get_items(
    skip: int = 0,
    limit: int = Query(default=10, le=100),
    search: Optional[str] = None
):
    return {"skip": skip, "limit": limit, "search": search}

URL: /items?skip=5&limit=20&search=book
"""

def search_items(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None
) -> dict:
    """Simulates query parameter handling."""
    items = ["apple", "banana", "book", "bottle", "box"]
    
    if search:
        items = [i for i in items if search.lower() in i.lower()]
    
    return {
        "items": items[skip:skip + limit],
        "total": len(items),
        "skip": skip,
        "limit": limit
    }

print(f"All items: {search_items()}")
print(f"Search 'b': {search_items(search='b')}")
print(f"With pagination: {search_items(skip=1, limit=2)}")


# ============================================
# 3. REQUEST BODY WITH PYDANTIC
# ============================================
print("\n--- 3. Request Body ---")


class CreateUserRequest(BaseModel):
    """Request model for user creation."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=8)
    age: Optional[int] = Field(None, ge=0, le=150)


def create_user(data: dict) -> dict:
    """Simulates request body validation."""
    try:
        user = CreateUserRequest(**data)
        return {"success": True, "user": user.model_dump(exclude={"password"})}
    except Exception as e:
        return {"success": False, "error": str(e)}


# Valid request
valid_data = {
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepass123",
    "age": 25
}
print(f"Valid request: {create_user(valid_data)}")

# Invalid request (username too short)
invalid_data = {"username": "jo", "email": "j@e.com", "password": "pass"}
print(f"Invalid request: {create_user(invalid_data)}")


# ============================================
# 4. RESPONSE MODELS
# ============================================
print("\n--- 4. Response Models ---")


class UserResponse(BaseModel):
    """Response model - excludes sensitive data."""
    id: int
    username: str
    email: str
    is_active: bool = True


class UserInDB(BaseModel):
    """Internal model with password."""
    id: int
    username: str
    email: str
    hashed_password: str
    is_active: bool = True


def get_user_response(user_db: UserInDB) -> UserResponse:
    """Convert internal model to response model."""
    return UserResponse(
        id=user_db.id,
        username=user_db.username,
        email=user_db.email,
        is_active=user_db.is_active
    )


# Simulate database user
db_user = UserInDB(
    id=1,
    username="johndoe",
    email="john@example.com",
    hashed_password="$2b$12$hashedpasswordhere"
)

# Convert to response (no password)
response = get_user_response(db_user)
print(f"Response (no password): {response.model_dump()}")


# ============================================
# 5. DEPENDENCY INJECTION
# ============================================
print("\n--- 5. Dependency Injection ---")

"""
FastAPI's DI system allows reusable components.

async def get_db():
    db = Database()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    return user

@app.get("/items")
async def get_items(
    db = Depends(get_db),
    user = Depends(get_current_user)
):
    return db.get_items(user.id)
"""


class FakeDB:
    """Simulated database dependency."""
    def __init__(self):
        self.connected = True
        print("  DB: Connected")
    
    def query(self, sql: str) -> list:
        return [{"id": 1, "name": "Item 1"}]
    
    def close(self):
        self.connected = False
        print("  DB: Disconnected")


def with_db_connection(func):
    """Simulates Depends(get_db)."""
    def wrapper(*args, **kwargs):
        db = FakeDB()
        try:
            result = func(db, *args, **kwargs)
            return result
        finally:
            db.close()
    return wrapper


@with_db_connection
def fetch_items(db: FakeDB) -> list:
    """Simulates endpoint with DB dependency."""
    return db.query("SELECT * FROM items")


print("Calling endpoint with DB dependency:")
items = fetch_items()
print(f"  Result: {items}")


# ============================================
# 6. ERROR HANDLING
# ============================================
print("\n--- 6. Error Handling ---")

"""
FastAPI uses HTTPException for errors.

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "Item lookup failed"}
        )
    return items_db[item_id]
"""


class APIError(Exception):
    """Custom API error."""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


def get_item(item_id: int) -> dict:
    """Simulates item retrieval with error handling."""
    items = {1: "Apple", 2: "Banana"}
    
    if item_id <= 0:
        raise APIError(400, "Invalid item ID")
    
    if item_id not in items:
        raise APIError(404, "Item not found")
    
    return {"id": item_id, "name": items[item_id]}


for test_id in [1, 3, -1]:
    try:
        result = get_item(test_id)
        print(f"Item {test_id}: {result}")
    except APIError as e:
        print(f"Item {test_id}: Error {e.status_code} - {e.detail}")


# ============================================
# 7. ASYNC/AWAIT IN FASTAPI
# ============================================
print("\n--- 7. Async Operations ---")

"""
FastAPI supports both sync and async endpoints.

# Async (I/O bound operations)
@app.get("/async-items")
async def get_items_async():
    items = await fetch_from_database()  # Non-blocking
    return items

# Sync (CPU bound or simple operations)
@app.get("/sync-items")
def get_items_sync():
    return {"items": [1, 2, 3]}

Rules:
- Use async for I/O: database, HTTP requests, file I/O
- Use sync for CPU-bound or simple operations
- Don't use sync blocking calls inside async functions
"""

import asyncio

async def async_db_query(query: str) -> list:
    """Simulates async database query."""
    await asyncio.sleep(0.01)  # Simulate I/O
    return [{"id": 1}, {"id": 2}]

async def async_endpoint():
    """Simulates async endpoint."""
    results = await async_db_query("SELECT * FROM items")
    return {"items": results}

# Run async code
result = asyncio.run(async_endpoint())
print(f"Async result: {result}")


# ============================================
# 8. MIDDLEWARE
# ============================================
print("\n--- 8. Middleware Concept ---")

"""
Middleware processes requests before/after routes.

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

Common middleware uses:
- Logging
- Authentication
- CORS
- Rate limiting
- Request timing
"""

import time

def timing_middleware(func):
    """Simulates timing middleware."""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  Request processed in {elapsed:.4f}s")
        return result
    return wrapper


@timing_middleware
def process_request():
    """Simulates request processing."""
    time.sleep(0.01)  # Simulate work
    return {"status": "ok"}


print("Processing request with timing middleware:")
process_request()


# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 50)
print("KEY FASTAPI CONCEPTS")
print("=" * 50)
print("""
1. Path Parameters: /users/{user_id} → user_id: int
2. Query Parameters: ?skip=0&limit=10 → skip: int = 0
3. Request Body: Pydantic models for validation
4. Response Models: Control what data is returned
5. Dependencies: Reusable components with Depends()
6. Error Handling: HTTPException for API errors
7. Async/Await: Native async support for I/O
8. Middleware: Process requests globally

Next steps:
- Run main.py with: uvicorn main:app --reload
- Explore docs at: http://localhost:8000/docs
- Test authentication flow with JWT
""")
