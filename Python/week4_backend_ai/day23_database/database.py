#!/usr/bin/env python3
"""Day 23 - Database Configuration with SQLAlchemy"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
from typing import Generator
import os


# ============================================
# DATABASE CONFIGURATION
# ============================================

# Database URLs for different databases
DATABASE_URLS = {
    "sqlite": "sqlite:///./app.db",
    "postgresql": "postgresql://user:password@localhost:5432/dbname",
    "mysql": "mysql+pymysql://user:password@localhost:3306/dbname",
    "async_postgresql": "postgresql+asyncpg://user:password@localhost:5432/dbname",
}

# Use SQLite for demonstration (no external DB needed)
DATABASE_URL = os.getenv("DATABASE_URL", DATABASE_URLS["sqlite"])


# ============================================
# ENGINE CONFIGURATION
# ============================================

def create_db_engine(url: str = DATABASE_URL):
    """
    Create database engine with connection pooling.
    
    Pool settings:
    - pool_size: Number of permanent connections
    - max_overflow: Additional connections allowed
    - pool_pre_ping: Check connection health before use
    - pool_recycle: Recycle connections after N seconds
    """
    # SQLite doesn't support connection pooling
    if "sqlite" in url:
        engine = create_engine(
            url,
            connect_args={"check_same_thread": False},  # Required for SQLite
            echo=False  # Set True to log SQL queries
        )
    else:
        engine = create_engine(
            url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
    
    return engine


# Create engine and session factory
engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()


# ============================================
# SESSION MANAGEMENT
# ============================================

def get_db() -> Generator:
    """
    Dependency that provides database session.
    Used with FastAPI's Depends().
    
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database operations.
    
    Usage:
        with get_db_context() as db:
            user = db.query(User).first()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ============================================
# DATABASE EVENTS (Hooks)
# ============================================

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign keys for SQLite."""
    if "sqlite" in DATABASE_URL:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_connection, connection_record, connection_proxy):
    """Log when connection is checked out from pool."""
    pass  # Add logging here if needed


# ============================================
# DATABASE INITIALIZATION
# ============================================

def init_db():
    """
    Initialize database - create all tables.
    Call this on application startup.
    """
    # Import models here to register them with Base
    from models import User, Post, Comment  # noqa
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def drop_db():
    """Drop all tables (use with caution!)."""
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped!")


# ============================================
# ASYNC DATABASE (SQLAlchemy 2.0+)
# ============================================

"""
For async operations, use this setup:

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

ASYNC_DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=5,
    max_overflow=10
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_db():
    async with AsyncSessionLocal() as session:
        yield session
"""


# ============================================
# DEMONSTRATION
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("DATABASE CONFIGURATION")
    print("=" * 50)
    
    print(f"\nDatabase URL: {DATABASE_URL}")
    print(f"Engine: {engine}")
    
    # Test connection
    print("\n--- Testing Connection ---")
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1" if "sqlite" not in DATABASE_URL else "SELECT 1")
            print(f"Connection successful! Result: {result.fetchone()}")
    except Exception as e:
        print(f"Connection test: Using SQLite (no external DB needed)")
    
    # Initialize database
    print("\n--- Initializing Database ---")
    init_db()
    
    # Test session
    print("\n--- Testing Session ---")
    with get_db_context() as db:
        print(f"Session created: {db}")
        print("Session will auto-commit on successful exit")
    
    print("\nDatabase configuration complete!")
