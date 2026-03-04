#!/usr/bin/env python3
"""Day 23 - CRUD Operations with SQLAlchemy"""

from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func, and_, or_
from typing import List, Optional, TypeVar, Generic, Type
from datetime import datetime

from database import get_db_context, init_db
from models import User, Post, Comment, Tag, Profile


# ============================================
# GENERIC CRUD BASE CLASS
# ============================================

T = TypeVar("T")


class CRUDBase(Generic[T]):
    """Base class for CRUD operations."""
    
    def __init__(self, model: Type[T]):
        self.model = model
    
    def get(self, db: Session, id: int) -> Optional[T]:
        """Get single record by ID."""
        return db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[T]:
        """Get all records with pagination."""
        return db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, db: Session, **kwargs) -> T:
        """Create new record."""
        obj = self.model(**kwargs)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
    
    def update(self, db: Session, id: int, **kwargs) -> Optional[T]:
        """Update existing record."""
        obj = self.get(db, id)
        if obj:
            for key, value in kwargs.items():
                setattr(obj, key, value)
            db.commit()
            db.refresh(obj)
        return obj
    
    def delete(self, db: Session, id: int) -> bool:
        """Delete record by ID."""
        obj = self.get(db, id)
        if obj:
            db.delete(obj)
            db.commit()
            return True
        return False
    
    def count(self, db: Session) -> int:
        """Count total records."""
        return db.query(func.count(self.model.id)).scalar()


# ============================================
# USER CRUD
# ============================================

class UserCRUD(CRUDBase[User]):
    """CRUD operations for User model."""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    def get_active_users(self, db: Session) -> List[User]:
        """Get all active users."""
        return db.query(User).filter(User.is_active == True).all()
    
    def create_with_profile(
        self, 
        db: Session,
        email: str,
        username: str,
        password: str,
        bio: str = None
    ) -> User:
        """Create user with profile."""
        user = User(
            email=email,
            username=username,
            hashed_password=password  # Should be hashed!
        )
        db.add(user)
        db.flush()  # Get user.id without committing
        
        if bio:
            profile = Profile(user_id=user.id, bio=bio)
            db.add(profile)
        
        db.commit()
        db.refresh(user)
        return user
    
    def search(self, db: Session, query: str) -> List[User]:
        """Search users by username or email."""
        return db.query(User).filter(
            or_(
                User.username.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            )
        ).all()


# ============================================
# POST CRUD
# ============================================

class PostCRUD(CRUDBase[Post]):
    """CRUD operations for Post model."""
    
    def __init__(self):
        super().__init__(Post)
    
    def get_by_slug(self, db: Session, slug: str) -> Optional[Post]:
        """Get post by slug."""
        return db.query(Post).filter(Post.slug == slug).first()
    
    def get_published(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[Post]:
        """Get published posts."""
        return db.query(Post)\
            .filter(Post.is_published == True)\
            .order_by(Post.published_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def get_by_author(self, db: Session, author_id: int) -> List[Post]:
        """Get all posts by author."""
        return db.query(Post).filter(Post.author_id == author_id).all()
    
    def get_with_tags(self, db: Session, tag_names: List[str]) -> List[Post]:
        """Get posts with specific tags."""
        return db.query(Post)\
            .join(Post.tags)\
            .filter(Tag.name.in_(tag_names))\
            .distinct()\
            .all()
    
    def publish(self, db: Session, post_id: int) -> Optional[Post]:
        """Publish a post."""
        post = self.get(db, post_id)
        if post:
            post.is_published = True
            post.published_at = datetime.utcnow()
            db.commit()
            db.refresh(post)
        return post
    
    def increment_views(self, db: Session, post_id: int) -> None:
        """Increment view count."""
        db.query(Post).filter(Post.id == post_id).update(
            {Post.view_count: Post.view_count + 1}
        )
        db.commit()


# ============================================
# ADVANCED QUERIES
# ============================================

def advanced_query_examples(db: Session):
    """Examples of advanced SQLAlchemy queries."""
    
    # 1. Join query with filter
    posts_with_authors = db.query(Post, User)\
        .join(User, Post.author_id == User.id)\
        .filter(Post.is_published == True)\
        .all()
    
    # 2. Aggregate query
    post_counts = db.query(
        User.username,
        func.count(Post.id).label('post_count')
    ).join(Post, User.id == Post.author_id)\
     .group_by(User.username)\
     .all()
    
    # 3. Subquery
    subquery = db.query(
        func.max(Post.created_at)
    ).filter(Post.author_id == User.id).scalar_subquery()
    
    users_with_latest = db.query(User, subquery.label('latest_post')).all()
    
    # 4. Complex filter
    filtered = db.query(Post).filter(
        and_(
            Post.is_published == True,
            Post.view_count > 100,
            or_(
                Post.title.ilike("%python%"),
                Post.title.ilike("%fastapi%")
            )
        )
    ).all()
    
    # 5. Eager loading (avoid N+1)
    from sqlalchemy.orm import joinedload
    posts = db.query(Post)\
        .options(joinedload(Post.author))\
        .options(joinedload(Post.tags))\
        .all()
    
    return {
        "posts_with_authors": len(posts_with_authors),
        "post_counts": post_counts,
        "filtered": len(filtered)
    }


# ============================================
# CRUD INSTANCES
# ============================================

user_crud = UserCRUD()
post_crud = PostCRUD()


# ============================================
# DEMONSTRATION
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("CRUD OPERATIONS DEMONSTRATION")
    print("=" * 50)
    
    # Initialize database
    init_db()
    
    with get_db_context() as db:
        # Create user
        print("\n--- Create User ---")
        user = user_crud.get_by_username(db, "johndoe")
        if not user:
            user = user_crud.create(
                db,
                email="john@example.com",
                username="johndoe",
                hashed_password="hashed_secret",
                full_name="John Doe"
            )
            print(f"Created: {user}")
        else:
            print(f"Existing: {user}")
        
        # Create post
        print("\n--- Create Post ---")
        post = post_crud.get_by_slug(db, "hello-world")
        if not post:
            post = post_crud.create(
                db,
                title="Hello World",
                slug="hello-world",
                content="This is my first post!",
                author_id=user.id
            )
            print(f"Created: {post}")
        else:
            print(f"Existing: {post}")
        
        # Read operations
        print("\n--- Read Operations ---")
        all_users = user_crud.get_all(db, limit=5)
        print(f"All users: {len(all_users)}")
        print(f"Total users: {user_crud.count(db)}")
        
        # Update
        print("\n--- Update ---")
        updated_user = user_crud.update(db, user.id, full_name="John Updated Doe")
        print(f"Updated: {updated_user.full_name}")
        
        # Publish post
        print("\n--- Publish Post ---")
        published = post_crud.publish(db, post.id)
        print(f"Published: {published.is_published} at {published.published_at}")
        
        # Increment views
        print("\n--- Increment Views ---")
        post_crud.increment_views(db, post.id)
        refreshed_post = post_crud.get(db, post.id)
        print(f"View count: {refreshed_post.view_count}")
        
        print("\nCRUD operations completed!")
