#!/usr/bin/env python3
"""
Custom Exceptions Demo

Learn how to create and use custom exceptions for domain-specific errors.
"""

from dataclasses import dataclass
from typing import Optional


# ============================================
# 1. BASIC CUSTOM EXCEPTION
# ============================================

class ValidationError(Exception):
    """Base exception for validation errors"""
    pass


class InvalidEmailError(ValidationError):
    """Raised when email format is invalid"""
    def __init__(self, email: str, message: str = None):
        self.email = email
        self.message = message or f"Invalid email format: {email}"
        super().__init__(self.message)


class InvalidAgeError(ValidationError):
    """Raised when age is out of valid range"""
    def __init__(self, age: int, min_age: int = 0, max_age: int = 150):
        self.age = age
        self.min_age = min_age
        self.max_age = max_age
        message = f"Age {age} is out of valid range ({min_age}-{max_age})"
        super().__init__(message)


# ============================================
# 2. EXCEPTION HIERARCHY
# ============================================

class AppError(Exception):
    """Base exception for application errors"""
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)
    
    def __str__(self):
        return f"[{self.code}] {self.message}"


class DatabaseError(AppError):
    """Database-related errors"""
    def __init__(self, message: str, query: str = None):
        super().__init__(message, code="DB_ERROR")
        self.query = query


class ConnectionError(DatabaseError):
    """Database connection errors"""
    def __init__(self, host: str, port: int):
        message = f"Cannot connect to database at {host}:{port}"
        super().__init__(message)
        self.host = host
        self.port = port
        self.code = "DB_CONNECTION_ERROR"


class QueryError(DatabaseError):
    """Query execution errors"""
    def __init__(self, message: str, query: str):
        super().__init__(message, query)
        self.code = "DB_QUERY_ERROR"


class APIError(AppError):
    """API-related errors"""
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message, code="API_ERROR")
        self.status_code = status_code


class NotFoundError(APIError):
    """Resource not found"""
    def __init__(self, resource: str, resource_id: str):
        message = f"{resource} with id '{resource_id}' not found"
        super().__init__(message, status_code=404)
        self.code = "NOT_FOUND"
        self.resource = resource
        self.resource_id = resource_id


class AuthenticationError(APIError):
    """Authentication failures"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)
        self.code = "AUTH_ERROR"


class AuthorizationError(APIError):
    """Authorization failures"""
    def __init__(self, action: str, resource: str):
        message = f"Not authorized to {action} {resource}"
        super().__init__(message, status_code=403)
        self.code = "FORBIDDEN"


# ============================================
# 3. PRACTICAL USAGE
# ============================================

@dataclass
class User:
    email: str
    age: int
    name: str


def validate_email(email: str) -> bool:
    """Simple email validation"""
    if "@" not in email or "." not in email.split("@")[-1]:
        raise InvalidEmailError(email)
    return True


def validate_age(age: int) -> bool:
    """Age validation"""
    if not isinstance(age, int):
        raise TypeError(f"Age must be int, got {type(age).__name__}")
    if age < 0 or age > 150:
        raise InvalidAgeError(age)
    return True


def create_user(name: str, email: str, age: int) -> User:
    """Create and validate a user"""
    validate_email(email)
    validate_age(age)
    return User(email=email, age=age, name=name)


def get_user_from_db(user_id: str) -> User:
    """Simulate fetching user from database"""
    # Simulate connection error
    if user_id == "timeout":
        raise ConnectionError("localhost", 5432)
    
    # Simulate not found
    if user_id == "unknown":
        raise NotFoundError("User", user_id)
    
    # Simulate success
    return User(email="user@example.com", age=30, name="Test User")


def authenticate(token: str) -> bool:
    """Simulate authentication"""
    if not token:
        raise AuthenticationError("No token provided")
    if token != "valid_token":
        raise AuthenticationError("Invalid token")
    return True


def authorize(user: User, action: str, resource: str) -> bool:
    """Simulate authorization check"""
    if action == "delete" and resource == "admin":
        raise AuthorizationError(action, resource)
    return True


# ============================================
# 4. DEMO
# ============================================

def main():
    print("=" * 60)
    print("CUSTOM EXCEPTIONS DEMO")
    print("=" * 60)
    
    # Test validation errors
    print("\n--- Validation Errors ---")
    
    test_users = [
        ("Alice", "alice@example.com", 25),
        ("Bob", "invalid-email", 30),
        ("Charlie", "charlie@test.com", -5),
        ("Diana", "diana@test.com", 200),
    ]
    
    for name, email, age in test_users:
        try:
            user = create_user(name, email, age)
            print(f"✅ Created user: {user}")
        except InvalidEmailError as e:
            print(f"❌ Email error: {e.message}")
        except InvalidAgeError as e:
            print(f"❌ Age error: {e}")
    
    # Test database errors
    print("\n--- Database Errors ---")
    
    for user_id in ["123", "timeout", "unknown"]:
        try:
            user = get_user_from_db(user_id)
            print(f"✅ Found user: {user.name}")
        except ConnectionError as e:
            print(f"❌ Connection failed: {e}")
        except NotFoundError as e:
            print(f"❌ Not found: {e}")
    
    # Test auth errors
    print("\n--- Authentication/Authorization Errors ---")
    
    tokens = ["valid_token", "invalid_token", ""]
    for token in tokens:
        try:
            authenticate(token)
            print(f"✅ Authenticated with token: '{token[:10]}...'")
        except AuthenticationError as e:
            print(f"❌ Auth failed: {e}")
    
    # Authorization
    try:
        user = User("admin@test.com", 30, "Admin")
        authorize(user, "delete", "admin")
        print("✅ Authorized to delete admin")
    except AuthorizationError as e:
        print(f"❌ Authorization failed: {e}")
    
    # Test exception hierarchy
    print("\n--- Exception Hierarchy ---")
    
    try:
        raise NotFoundError("Product", "xyz123")
    except AppError as e:
        print(f"Caught as AppError: {e}")
        print(f"  Code: {e.code}")
        if isinstance(e, APIError):
            print(f"  Status: {e.status_code}")
    
    # Show inheritance
    print("\n--- Inheritance Check ---")
    errors = [
        NotFoundError("X", "1"),
        QueryError("Query failed", "SELECT *"),
        AuthenticationError(),
    ]
    
    for error in errors:
        checks = [
            ("Exception", isinstance(error, Exception)),
            ("AppError", isinstance(error, AppError)),
            ("APIError", isinstance(error, APIError)),
            ("DatabaseError", isinstance(error, DatabaseError)),
        ]
        true_checks = [name for name, result in checks if result]
        print(f"{type(error).__name__} is: {' → '.join(true_checks)}")


if __name__ == "__main__":
    main()
