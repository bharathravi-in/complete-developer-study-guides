#!/usr/bin/env python3
"""Day 22 - JWT Authentication for FastAPI"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel


# ============================================
# CONFIGURATION
# ============================================

# In production, use environment variables!
SECRET_KEY = "your-secret-key-keep-it-safe-and-long-enough-32-chars"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ============================================
# PASSWORD HASHING
# ============================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


# ============================================
# JWT TOKEN HANDLING
# ============================================

class TokenPayload(BaseModel):
    """Token payload structure."""
    sub: str  # subject (username)
    exp: datetime
    iat: datetime
    scopes: list[str] = []


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data (must include 'sub' for subject)
        expires_delta: Token expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Token payload or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token(token: str, credentials_exception) -> str:
    """
    Verify token and extract username.
    
    Args:
        token: JWT token
        credentials_exception: Exception to raise on failure
    
    Returns:
        Username from token
    
    Raises:
        credentials_exception if token is invalid
    """
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    return username


# ============================================
# FAKE USER DATABASE (for demonstration)
# ============================================

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": get_password_hash("secret123"),
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderland",
        "email": "alice@example.com",
        "hashed_password": get_password_hash("alice123"),
        "disabled": False,
    }
}


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """
    Authenticate user with username and password.
    
    Returns:
        User dict if valid, None otherwise
    """
    user = fake_users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user


# ============================================
# DEMONSTRATION
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("JWT AUTHENTICATION DEMONSTRATION")
    print("=" * 50)
    
    # Password hashing
    print("\n--- Password Hashing ---")
    password = "mysecretpassword"
    hashed = get_password_hash(password)
    print(f"Password: {password}")
    print(f"Hashed: {hashed[:50]}...")
    print(f"Verify correct: {verify_password(password, hashed)}")
    print(f"Verify wrong: {verify_password('wrongpass', hashed)}")
    
    # Token creation
    print("\n--- Token Creation ---")
    token = create_access_token(
        data={"sub": "johndoe", "scopes": ["read", "write"]}
    )
    print(f"Token: {token[:50]}...")
    
    # Token decoding
    print("\n--- Token Decoding ---")
    payload = decode_access_token(token)
    print(f"Subject: {payload.get('sub')}")
    print(f"Expires: {datetime.fromtimestamp(payload.get('exp'))}")
    print(f"Scopes: {payload.get('scopes')}")
    
    # User authentication
    print("\n--- User Authentication ---")
    user = authenticate_user("johndoe", "secret123")
    if user:
        print(f"Authenticated: {user['full_name']} ({user['email']})")
    else:
        print("Authentication failed")
    
    # Failed auth
    failed = authenticate_user("johndoe", "wrongpassword")
    print(f"Wrong password result: {failed}")
