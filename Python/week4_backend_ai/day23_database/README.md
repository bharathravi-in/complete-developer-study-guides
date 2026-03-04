# Day 23 - Database Integration: SQLAlchemy + Redis

## Topics Covered
- SQLAlchemy ORM fundamentals
- Database models and relationships
- Async database operations
- Connection pooling
- Redis for caching
- Database migrations with Alembic

## ORM vs Raw SQL
| Aspect | ORM (SQLAlchemy) | Raw SQL |
|--------|------------------|---------|
| Readability | ✅ Pythonic | ⚠️ SQL strings |
| Security | ✅ Auto-escaping | ⚠️ Manual escaping |
| Performance | ⚠️ Slight overhead | ✅ Optimal |
| Portability | ✅ DB agnostic | ❌ DB specific |
| Complex Queries | ⚠️ Can be verbose | ✅ Full control |

## Project Structure
```
day23_database/
├── README.md
├── practice.py          # ORM concepts  
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── crud.py              # CRUD operations
├── redis_cache.py       # Redis caching
└── requirements.txt
```

## Key Concepts

### 1. SQLAlchemy Setup
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://user:pass@localhost/db"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
```

### 2. Model Definition
```python
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    posts = relationship("Post", back_populates="author")
```

### 3. Async SQLAlchemy (2.0+)
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

engine = create_async_engine("postgresql+asyncpg://...")

async def get_user(session: AsyncSession, user_id: int):
    result = await session.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
```

### 4. Redis Caching Pattern
```python
import redis

cache = redis.Redis(host='localhost', port=6379, db=0)

def get_user_cached(user_id: int):
    # Try cache first
    cached = cache.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)
    
    # Cache miss - fetch from DB
    user = db.query(User).get(user_id)
    cache.setex(f"user:{user_id}", 3600, json.dumps(user.dict()))
    return user
```

## Run
```bash
# Install dependencies
pip install sqlalchemy psycopg2-binary redis alembic

# Run examples
python database.py
python crud.py
python redis_cache.py
```

## Practice Exercises
1. Create User, Post, Comment models with relationships
2. Implement CRUD operations with SQLAlchemy
3. Add Redis caching layer for frequently accessed data
4. Use connection pooling for production
5. Create database migrations with Alembic
