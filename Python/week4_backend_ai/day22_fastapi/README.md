# Day 22 - FastAPI: Building Modern REST APIs

## Topics Covered
- FastAPI fundamentals & async support
- Pydantic models for request/response validation
- Path & query parameters
- Authentication with JWT
- Dependency injection
- Error handling & custom responses

## Why FastAPI?
| Feature | FastAPI | Flask | Django |
|---------|---------|-------|--------|
| Async Support | ✅ Native | ❌ Manual | ⚠️ Limited |
| Type Hints | ✅ Required | ❌ Optional | ❌ Optional |
| Auto Docs | ✅ Swagger + ReDoc | ❌ Manual | ❌ Manual |
| Validation | ✅ Pydantic | ❌ Manual | ⚠️ Forms |
| Performance | 🚀 Very Fast | Moderate | Slower |

## Project Structure
```
day22_fastapi/
├── README.md
├── practice.py          # Basic concepts
├── main.py              # Full API application
├── auth.py              # JWT authentication
├── models.py            # Pydantic models
└── requirements.txt
```

## Key Concepts

### 1. Basic Route
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### 2. Path & Query Parameters
```python
@app.get("/items/{item_id}")
async def get_item(item_id: int, q: str = None, limit: int = 10):
    return {"item_id": item_id, "query": q, "limit": limit}
```

### 3. Pydantic Models
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### 4. JWT Authentication Flow
```
1. User logs in with credentials
2. Server validates and returns JWT token
3. Client includes token in Authorization header
4. Server validates token on protected routes
```

## Run the API
```bash
# Install dependencies
pip install fastapi uvicorn pydantic python-jose[cryptography] passlib[bcrypt]

# Run development server
uvicorn main:app --reload

# Access docs
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## Practice Exercises
1. Create a CRUD API for a resource (users/products)
2. Implement JWT authentication
3. Add request validation with Pydantic
4. Create custom exception handlers
5. Implement dependency injection for database connections
