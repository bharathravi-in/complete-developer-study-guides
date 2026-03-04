#!/usr/bin/env python3
"""Day 23 - SQLAlchemy Models with Relationships"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional

# Import Base from database module
try:
    from database import Base
except ImportError:
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()


# ============================================
# ASSOCIATION TABLE (Many-to-Many)
# ============================================

post_tags = Table(
    'post_tags',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)


# ============================================
# USER MODEL
# ============================================

class User(Base):
    """User model with one-to-many relationship to posts."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    profile = relationship("Profile", back_populates="user", uselist=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


# ============================================
# PROFILE MODEL (One-to-One)
# ============================================

class Profile(Base):
    """User profile - one-to-one relationship with User."""
    __tablename__ = "profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    bio = Column(Text)
    avatar_url = Column(String(500))
    website = Column(String(255))
    location = Column(String(100))
    
    # Relationships
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<Profile(user_id={self.user_id})>"


# ============================================
# POST MODEL
# ============================================

class Post(Base):
    """Blog post with relationships to user, comments, and tags."""
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True)
    content = Column(Text, nullable=False)
    summary = Column(String(500))
    is_published = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime)
    
    # Relationships
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    tags = relationship("Tag", secondary=post_tags, back_populates="posts")
    
    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title[:30]}...')>"


# ============================================
# COMMENT MODEL
# ============================================

class Comment(Base):
    """Comment on a post - belongs to Post and User."""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"))  # For nested comments
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")
    
    def __repr__(self):
        return f"<Comment(id={self.id}, post_id={self.post_id})>"


# ============================================
# TAG MODEL
# ============================================

class Tag(Base):
    """Tag for posts - many-to-many relationship."""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    description = Column(String(200))
    
    # Relationships
    posts = relationship("Post", secondary=post_tags, back_populates="tags")
    
    def __repr__(self):
        return f"<Tag(name='{self.name}')>"


# ============================================
# PRODUCT MODEL (Example for E-commerce)
# ============================================

class Product(Base):
    """Product model demonstrating various column types."""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    discount_price = Column(Float)
    stock_quantity = Column(Integer, default=0)
    is_available = Column(Boolean, default=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="products")
    
    @property
    def effective_price(self) -> float:
        return self.discount_price or self.price
    
    def __repr__(self):
        return f"<Product(name='{self.name}', price={self.price})>"


class Category(Base):
    """Product category with self-referencing relationship."""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"))
    
    # Relationships
    products = relationship("Product", back_populates="category")
    parent = relationship("Category", remote_side=[id], backref="children")
    
    def __repr__(self):
        return f"<Category(name='{self.name}')>"


# ============================================
# DEMONSTRATION
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("SQLALCHEMY MODELS")
    print("=" * 50)
    
    print("\n--- Model Definitions ---")
    print(f"User table: {User.__tablename__}")
    print(f"  Columns: {[c.name for c in User.__table__.columns]}")
    
    print(f"\nPost table: {Post.__tablename__}")
    print(f"  Columns: {[c.name for c in Post.__table__.columns]}")
    
    print("\n--- Relationship Types ---")
    print("1. One-to-Many: User -> Posts")
    print("2. One-to-One: User -> Profile")
    print("3. Many-to-Many: Post <-> Tags")
    print("4. Self-referential: Comment -> Replies")
    print("5. Self-referential: Category -> Subcategories")
    
    print("\n--- Creating Tables ---")
    from database import engine, init_db
    init_db()
    
    print("\nModels loaded successfully!")
