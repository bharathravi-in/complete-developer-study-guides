#!/usr/bin/env python3
"""Day 23 - SQLAlchemy Practice"""

from sqlalchemy import create_engine, text, select, func
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from typing import Optional
from datetime import datetime


print("=" * 50)
print("SQLALCHEMY FUNDAMENTALS")
print("=" * 50)


# ============================================
# 1. ENGINE & CONNECTION
# ============================================
print("\n--- 1. Engine & Connection ---")

# Create in-memory SQLite engine
engine = create_engine("sqlite:///:memory:", echo=False)

# Test raw SQL
with engine.connect() as conn:
    result = conn.execute(text("SELECT 1 + 1 as sum"))
    print(f"Raw SQL result: {result.fetchone()}")


# ============================================
# 2. DECLARATIVE BASE & MODELS
# ============================================
print("\n--- 2. Models ---")


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    age: Mapped[Optional[int]] = mapped_column(default=None)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}')>"


# Create tables
Base.metadata.create_all(engine)
print("Tables created!")


# ============================================
# 3. SESSION & CRUD
# ============================================
print("\n--- 3. Session & CRUD ---")

Session = sessionmaker(bind=engine)
session = Session()

# CREATE
print("\nCreate:")
users = [
    User(name="Alice", email="alice@example.com", age=30),
    User(name="Bob", email="bob@example.com", age=25),
    User(name="Charlie", email="charlie@example.com", age=35),
]
session.add_all(users)
session.commit()
print(f"Created {len(users)} users")

# READ - All
print("\nRead All:")
all_users = session.query(User).all()
for user in all_users:
    print(f"  {user}")

# READ - Filter
print("\nRead with Filter:")
young_users = session.query(User).filter(User.age < 30).all()
print(f"Users under 30: {[u.name for u in young_users]}")

# READ - Single
print("\nRead Single:")
alice = session.query(User).filter(User.name == "Alice").first()
print(f"Found: {alice}")

# UPDATE
print("\nUpdate:")
alice.age = 31
session.commit()
print(f"Alice's new age: {alice.age}")

# DELETE
print("\nDelete:")
bob = session.query(User).filter(User.name == "Bob").first()
session.delete(bob)
session.commit()
remaining = session.query(User).count()
print(f"Remaining users: {remaining}")


# ============================================
# 4. QUERY PATTERNS
# ============================================
print("\n--- 4. Query Patterns ---")

# Add more data
session.add_all([
    User(name="David", email="david@example.com", age=28),
    User(name="Eve", email="eve@example.com", age=32),
    User(name="Frank", email="frank@example.com", age=28),
])
session.commit()

# Order By
print("\nOrder by age:")
ordered = session.query(User).order_by(User.age.desc()).all()
for u in ordered:
    print(f"  {u.name}: {u.age}")

# Limit & Offset (Pagination)
print("\nPagination (page 1, 2 items):")
page1 = session.query(User).limit(2).offset(0).all()
print(f"  {[u.name for u in page1]}")

# Count
print("\nCount:")
count = session.query(func.count(User.id)).scalar()
print(f"Total users: {count}")

# Distinct
print("\nDistinct ages:")
ages = session.query(User.age).distinct().all()
print(f"  {[a[0] for a in ages]}")

# Group By
print("\nGroup by age:")
grouped = session.query(User.age, func.count(User.id)).group_by(User.age).all()
for age, count in grouped:
    print(f"  Age {age}: {count} users")

# Like
print("\nFilter with LIKE:")
matching = session.query(User).filter(User.name.like("A%")).all()
print(f"Names starting with 'A': {[u.name for u in matching]}")

# In
print("\nFilter with IN:")
selected = session.query(User).filter(User.age.in_([28, 32])).all()
print(f"Age 28 or 32: {[u.name for u in selected]}")


# ============================================
# 5. MODERN SELECT SYNTAX (SQLAlchemy 2.0)
# ============================================
print("\n--- 5. Modern Select Syntax ---")

# SQLAlchemy 2.0 style queries
stmt = select(User).where(User.age >= 30).order_by(User.name)
result = session.scalars(stmt).all()
print(f"Users 30+: {[u.name for u in result]}")

# Select specific columns
stmt = select(User.name, User.email).where(User.is_active == True)
result = session.execute(stmt).all()
print(f"Active users: {result}")


# ============================================
# 6. TRANSACTIONS
# ============================================
print("\n--- 6. Transactions ---")

try:
    # Start implicit transaction
    session.add(User(name="Test", email="test@example.com"))
    
    # Simulate error
    # session.add(User(name="Test2", email="test@example.com"))  # Duplicate!
    
    session.commit()
    print("Transaction committed")
except Exception as e:
    session.rollback()
    print(f"Transaction rolled back: {e}")


# ============================================
# 7. RAW SQL
# ============================================
print("\n--- 7. Raw SQL ---")

# Execute raw SQL
result = session.execute(
    text("SELECT name, age FROM users WHERE age > :min_age"),
    {"min_age": 28}
)
print("Raw SQL results:")
for row in result:
    print(f"  {row.name}: {row.age}")


# ============================================
# 8. BULK OPERATIONS
# ============================================
print("\n--- 8. Bulk Operations ---")

# Bulk insert
session.execute(
    User.__table__.insert(),
    [
        {"name": "User1", "email": "user1@test.com", "age": 20},
        {"name": "User2", "email": "user2@test.com", "age": 21},
    ]
)
session.commit()
print("Bulk inserted 2 users")

# Bulk update
session.query(User).filter(User.age < 25).update({"is_active": False})
session.commit()
inactive_count = session.query(User).filter(User.is_active == False).count()
print(f"Deactivated {inactive_count} young users")


# Cleanup
session.close()


# ============================================
# 9. SUMMARY
# ============================================
print("\n" + "=" * 50)
print("SQLALCHEMY CORE CONCEPTS")
print("=" * 50)
print("""
1. Engine: Database connection factory
2. Session: Unit of work, manages transactions
3. Declarative Base: Define models as classes
4. Mapped columns: Type-annotated columns (2.0 style)
5. Query patterns: filter, order_by, limit, group_by
6. Relationships: one-to-many, many-to-many
7. Transactions: commit/rollback
8. Async support: create_async_engine, AsyncSession

Best Practices:
- Use context managers for sessions
- Always handle transactions explicitly
- Use migrations (Alembic) for schema changes
- Index frequently queried columns
- Use relationship lazy loading carefully
""")
