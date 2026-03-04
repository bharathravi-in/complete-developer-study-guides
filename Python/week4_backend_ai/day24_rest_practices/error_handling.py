#!/usr/bin/env python3
"""Day 24 - Error Handling Patterns"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


# ============================================
# ERROR CODES
# ============================================

class ErrorCode(str, Enum):
    """Standardized error codes."""
    # Authentication
    UNAUTHORIZED = "UNAUTHORIZED"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    
    # Authorization
    FORBIDDEN = "FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    
    # Resources
    NOT_FOUND = "NOT_FOUND"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    CONFLICT = "CONFLICT"
    
    # Rate Limiting
    RATE_LIMITED = "RATE_LIMITED"
    
    # Server
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # Business Logic
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"


# ============================================
# CUSTOM EXCEPTIONS
# ============================================

class APIException(Exception):
    """Base API exception."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        status_code: int = 400,
        details: Optional[List[dict]] = None,
        headers: Optional[dict] = None
    ):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details
        self.headers = headers
        super().__init__(message)


class NotFoundError(APIException):
    """Resource not found."""
    
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=f"{resource} not found",
            status_code=404,
            details=[{"resource": resource, "identifier": str(identifier)}]
        )


class ConflictError(APIException):
    """Resource conflict (e.g., duplicate)."""
    
    def __init__(self, resource: str, field: str, value: Any):
        super().__init__(
            code=ErrorCode.ALREADY_EXISTS,
            message=f"{resource} with this {field} already exists",
            status_code=409,
            details=[{"field": field, "value": str(value)}]
        )


class ValidationError(APIException):
    """Input validation error."""
    
    def __init__(self, errors: List[dict]):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message="Input validation failed",
            status_code=422,
            details=errors
        )


class AuthenticationError(APIException):
    """Authentication failed."""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            code=ErrorCode.UNAUTHORIZED,
            message=message,
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"}
        )


class AuthorizationError(APIException):
    """Not authorized to perform action."""
    
    def __init__(self, action: str = "perform this action"):
        super().__init__(
            code=ErrorCode.FORBIDDEN,
            message=f"You are not authorized to {action}",
            status_code=403
        )


class RateLimitError(APIException):
    """Rate limit exceeded."""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            code=ErrorCode.RATE_LIMITED,
            message="Rate limit exceeded. Please try again later.",
            status_code=429,
            headers={"Retry-After": str(retry_after)}
        )


class BusinessLogicError(APIException):
    """Business rule violation."""
    
    def __init__(self, rule: str, message: str):
        super().__init__(
            code=ErrorCode.BUSINESS_RULE_VIOLATION,
            message=message,
            status_code=400,
            details=[{"rule": rule}]
        )


# ============================================
# ERROR RESPONSE MODEL
# ============================================

class FieldError(BaseModel):
    """Individual field error."""
    field: str
    message: str
    code: str


class ErrorResponse(BaseModel):
    """Standardized error response."""
    code: ErrorCode
    message: str
    status: int
    details: Optional[List[dict]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


# ============================================
# FASTAPI APP WITH ERROR HANDLERS
# ============================================

app = FastAPI(title="Error Handling Demo")


# Custom exception handler
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """Handle custom API exceptions."""
    response = ErrorResponse(
        code=exc.code,
        message=exc.message,
        status=exc.status_code,
        details=exc.details,
        request_id=request.headers.get("X-Request-ID")
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": response.model_dump()},
        headers=exc.headers
    )


# Validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Convert Pydantic validation errors to standard format."""
    details = []
    for error in exc.errors():
        details.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "code": error["type"]
        })
    
    response = ErrorResponse(
        code=ErrorCode.VALIDATION_ERROR,
        message="Input validation failed",
        status=422,
        details=details
    )
    return JSONResponse(
        status_code=422,
        content={"error": response.model_dump()}
    )


# Generic exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors."""
    response = ErrorResponse(
        code=ErrorCode.INTERNAL_ERROR,
        message="An unexpected error occurred",
        status=500,
        request_id=request.headers.get("X-Request-ID")
    )
    # Log the actual error here
    return JSONResponse(
        status_code=500,
        content={"error": response.model_dump()}
    )


# ============================================
# DEMO ENDPOINTS
# ============================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    age: int = Field(..., ge=0, le=150)


@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Demo: NotFoundError."""
    # Simulate user not found
    if user_id > 100:
        raise NotFoundError("User", user_id)
    return {"id": user_id, "name": "John Doe"}


@app.post("/users")
async def create_user(user: UserCreate):
    """Demo: ConflictError."""
    # Simulate duplicate email
    if user.email == "existing@example.com":
        raise ConflictError("User", "email", user.email)
    return {"email": user.email, "message": "Created"}


@app.get("/protected")
async def protected_resource():
    """Demo: AuthenticationError."""
    raise AuthenticationError("Invalid or missing token")


@app.delete("/admin/users/{user_id}")
async def admin_delete_user(user_id: int):
    """Demo: AuthorizationError."""
    raise AuthorizationError("delete users")


@app.get("/api/data")
async def rate_limited_endpoint():
    """Demo: RateLimitError."""
    raise RateLimitError(retry_after=120)


@app.post("/transfer")
async def transfer_funds():
    """Demo: BusinessLogicError."""
    raise BusinessLogicError(
        rule="minimum_balance",
        message="Transfer would result in balance below minimum required"
    )


# ============================================
# ERROR HANDLING UTILS
# ============================================

def handle_database_error(func):
    """Decorator to handle database errors."""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ConnectionError:
            raise APIException(
                code=ErrorCode.SERVICE_UNAVAILABLE,
                message="Database temporarily unavailable",
                status_code=503
            )
        except Exception as e:
            raise APIException(
                code=ErrorCode.INTERNAL_ERROR,
                message="Database operation failed",
                status_code=500,
                details=[{"error": str(e)}]
            )
    return wrapper


# ============================================
# DEMONSTRATION
# ============================================

if __name__ == "__main__":
    print("=" * 50)
    print("ERROR HANDLING PATTERNS")
    print("=" * 50)
    
    print("\nError Codes:")
    for code in ErrorCode:
        print(f"  {code.value}")
    
    print("\nCustom Exceptions:")
    exceptions = [
        NotFoundError("User", 123),
        ConflictError("User", "email", "test@example.com"),
        AuthenticationError(),
        AuthorizationError("delete users"),
        RateLimitError(60),
        BusinessLogicError("min_balance", "Insufficient balance"),
    ]
    
    for exc in exceptions:
        print(f"  {exc.code.value}: {exc.message} ({exc.status_code})")
    
    print("\nRun with: uvicorn error_handling:app --reload")
    print("Test endpoints to see error responses")
