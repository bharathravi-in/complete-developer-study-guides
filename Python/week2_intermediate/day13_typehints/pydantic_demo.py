#!/usr/bin/env python3
"""
Pydantic Demo - Data Validation

Pydantic provides runtime data validation using type hints.
Install: pip install pydantic
"""

# Note: This requires pydantic to be installed
# pip install pydantic

try:
    from pydantic import BaseModel, Field, validator, EmailStr, field_validator
    from pydantic import ValidationError, ConfigDict
    from typing import Optional, List
    from datetime import datetime
    from enum import Enum
    
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    print("Pydantic not installed. Run: pip install pydantic[email]")


if PYDANTIC_AVAILABLE:
    print("=" * 50)
    print("PYDANTIC DATA VALIDATION")
    print("=" * 50)
    
    # ============================================
    # 1. BASIC MODEL
    # ============================================
    print("\n--- 1. BASIC MODEL ---")
    
    class User(BaseModel):
        """Basic Pydantic model"""
        name: str
        age: int
        email: str
        active: bool = True
    
    # Create from dict
    user_data = {"name": "Alice", "age": 30, "email": "alice@example.com"}
    user = User(**user_data)
    print(f"User: {user}")
    print(f"User.name: {user.name}")
    print(f"User dict: {user.model_dump()}")
    print(f"User JSON: {user.model_dump_json()}")
    
    # Type coercion
    user2 = User(name="Bob", age="25", email="bob@test.com", active="true")
    print(f"Coerced age (str->int): {user2.age}, type: {type(user2.age)}")
    
    # ============================================
    # 2. VALIDATION
    # ============================================
    print("\n--- 2. VALIDATION ---")
    
    class Product(BaseModel):
        name: str = Field(..., min_length=1, max_length=100)
        price: float = Field(..., gt=0, description="Price must be positive")
        quantity: int = Field(default=0, ge=0)
        tags: List[str] = Field(default_factory=list)
        
        @field_validator('name')
        @classmethod
        def name_must_be_title_case(cls, v):
            return v.title()
    
    product = Product(name="laptop", price=999.99, quantity=10)
    print(f"Product: {product}")
    print(f"Name (auto title-cased): {product.name}")
    
    # Validation error
    try:
        bad_product = Product(name="", price=-10, quantity=-5)
    except ValidationError as e:
        print(f"\nValidation errors:")
        for error in e.errors():
            print(f"  {error['loc'][0]}: {error['msg']}")
    
    # ============================================
    # 3. NESTED MODELS
    # ============================================
    print("\n--- 3. NESTED MODELS ---")
    
    class Address(BaseModel):
        street: str
        city: str
        country: str = "USA"
    
    class Customer(BaseModel):
        name: str
        address: Address
        orders: List[str] = []
    
    customer_data = {
        "name": "John",
        "address": {
            "street": "123 Main St",
            "city": "NYC"
        },
        "orders": ["ORD-001", "ORD-002"]
    }
    
    customer = Customer(**customer_data)
    print(f"Customer: {customer.name}")
    print(f"City: {customer.address.city}")
    
    # ============================================
    # 4. ENUMS AND OPTIONAL
    # ============================================
    print("\n--- 4. ENUMS AND OPTIONAL ---")
    
    class Status(str, Enum):
        PENDING = "pending"
        ACTIVE = "active"
        COMPLETED = "completed"
    
    class Task(BaseModel):
        title: str
        description: Optional[str] = None
        status: Status = Status.PENDING
        due_date: Optional[datetime] = None
    
    task = Task(title="Learn Pydantic", status="active")
    print(f"Task: {task.title}, Status: {task.status.value}")
    
    # ============================================
    # 5. MODEL CONFIG
    # ============================================
    print("\n--- 5. MODEL CONFIG ---")
    
    class StrictUser(BaseModel):
        model_config = ConfigDict(
            str_strip_whitespace=True,
            validate_default=True,
            extra='forbid'  # Don't allow extra fields
        )
        
        name: str
        email: str
    
    user = StrictUser(name="  Alice  ", email="alice@test.com")
    print(f"Stripped name: '{user.name}'")
    
    try:
        bad_user = StrictUser(name="Bob", email="bob@test.com", extra_field="oops")
    except ValidationError as e:
        print(f"Extra field error: {e.errors()[0]['msg']}")
    
    # ============================================
    # 6. CUSTOM VALIDATORS
    # ============================================
    print("\n--- 6. CUSTOM VALIDATORS ---")
    
    class Registration(BaseModel):
        username: str
        password: str
        confirm_password: str
        
        @field_validator('username')
        @classmethod
        def username_alphanumeric(cls, v):
            if not v.isalnum():
                raise ValueError('must be alphanumeric')
            return v.lower()
        
        @field_validator('password')
        @classmethod
        def password_strength(cls, v):
            if len(v) < 8:
                raise ValueError('must be at least 8 characters')
            if not any(c.isupper() for c in v):
                raise ValueError('must contain uppercase')
            if not any(c.isdigit() for c in v):
                raise ValueError('must contain digit')
            return v
    
    try:
        reg = Registration(
            username="JohnDoe123",
            password="SecurePass123",
            confirm_password="SecurePass123"
        )
        print(f"Registration: {reg.username}")
    except ValidationError as e:
        print(f"Registration error: {e}")
    
    # ============================================
    # 7. SERIALIZATION
    # ============================================
    print("\n--- 7. SERIALIZATION ---")
    
    class Article(BaseModel):
        title: str
        content: str
        published: bool = False
        created_at: datetime = Field(default_factory=datetime.now)
    
    article = Article(title="Pydantic Guide", content="Learn validation...")
    
    # To dict
    print(f"Dict: {article.model_dump()}")
    
    # To JSON
    print(f"JSON: {article.model_dump_json()}")
    
    # Exclude fields
    print(f"Exclude content: {article.model_dump(exclude={'content'})}")
    
    # Include only specific fields
    print(f"Include title only: {article.model_dump(include={'title'})}")
    
    print("\n✅ Pydantic demo completed!")

else:
    print("""
To run this demo, install pydantic:
    pip install pydantic[email]

Pydantic features:
- Data validation using Python type hints
- JSON serialization/deserialization  
- Custom validators
- Nested models
- Settings management
""")
