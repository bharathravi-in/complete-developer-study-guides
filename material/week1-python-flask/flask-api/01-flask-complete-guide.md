# Flask API Development - Complete Guide

## Flask vs Express.js (Quick Comparison)

| Feature | Express.js | Flask |
|---------|-----------|-------|
| Language | JavaScript | Python |
| Routing | `app.get('/', handler)` | `@app.route('/')` |
| Middleware | `app.use()` | Decorators / before_request |
| Templates | EJS, Pug | Jinja2 |
| ORM | Sequelize, Prisma | SQLAlchemy |
| Package | npm | pip |
| Server | Built-in | Waitress/Gunicorn |
| Ecosystem | Huge | Rich (AI/ML focus) |

---

## 1. Hello World

```python
# app.py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello():
    return {"message": "Hello, Bharath!"}

@app.route("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

```bash
# Run
pip install flask
python app.py
# Open: http://localhost:5000
```

## 2. REST API Routes

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage (will replace with DB later)
courses = []
next_id = 1

# GET all courses
@app.route("/api/courses", methods=["GET"])
def get_courses():
    return jsonify({"data": courses, "total": len(courses)})

# GET single course
@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id: int):
    course = next((c for c in courses if c["id"] == course_id), None)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    return jsonify({"data": course})

# POST create course
@app.route("/api/courses", methods=["POST"])
def create_course():
    global next_id
    data = request.get_json()
    
    # Validation
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400
    
    course = {
        "id": next_id,
        "title": data["title"],
        "description": data.get("description", ""),
        "instructor": data.get("instructor", "Unknown"),
    }
    courses.append(course)
    next_id += 1
    
    return jsonify({"data": course, "message": "Course created"}), 201

# PUT update course
@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id: int):
    course = next((c for c in courses if c["id"] == course_id), None)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    data = request.get_json()
    course.update({
        "title": data.get("title", course["title"]),
        "description": data.get("description", course["description"]),
        "instructor": data.get("instructor", course["instructor"]),
    })
    
    return jsonify({"data": course, "message": "Course updated"})

# DELETE course
@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id: int):
    global courses
    course = next((c for c in courses if c["id"] == course_id), None)
    if not course:
        return jsonify({"error": "Course not found"}), 404
    
    courses = [c for c in courses if c["id"] != course_id]
    return jsonify({"message": "Course deleted"})

# Query parameters
@app.route("/api/courses/search", methods=["GET"])
def search_courses():
    query = request.args.get("q", "")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    
    filtered = [c for c in courses if query.lower() in c["title"].lower()]
    
    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered[start:end]
    
    return jsonify({
        "data": paginated,
        "total": len(filtered),
        "page": page,
        "per_page": per_page,
    })
```

## 3. Blueprints (Like Express Router)

```python
# blueprints/courses.py
from flask import Blueprint, request, jsonify

courses_bp = Blueprint("courses", __name__, url_prefix="/api/courses")

@courses_bp.route("/", methods=["GET"])
def get_all():
    return jsonify({"data": []})

@courses_bp.route("/<int:id>", methods=["GET"])
def get_one(id: int):
    return jsonify({"data": {"id": id}})

@courses_bp.route("/", methods=["POST"])
def create():
    data = request.get_json()
    return jsonify({"data": data}), 201


# blueprints/auth.py
from flask import Blueprint, request, jsonify

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    # ... authentication logic
    return jsonify({"token": "jwt-token-here"})

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    return jsonify({"message": "User created"}), 201


# app.py - Register blueprints
from flask import Flask
from blueprints.courses import courses_bp
from blueprints.auth import auth_bp

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(courses_bp)
    app.register_blueprint(auth_bp)
    
    return app

app = create_app()
```

## 4. Middleware & Hooks

```python
from flask import Flask, request, g
import time
import uuid

app = Flask(__name__)

# Before EVERY request (like Express middleware)
@app.before_request
def before_request():
    """Runs before every request."""
    g.request_id = str(uuid.uuid4())[:8]
    g.start_time = time.time()
    print(f"[{g.request_id}] {request.method} {request.path}")

# After EVERY request
@app.after_request
def after_request(response):
    """Runs after every request."""
    elapsed = time.time() - g.start_time
    print(f"[{g.request_id}] Response: {response.status_code} ({elapsed:.2f}s)")
    response.headers["X-Request-ID"] = g.request_id
    response.headers["X-Response-Time"] = f"{elapsed:.2f}s"
    return response

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(ValueError)
def value_error(error):
    return jsonify({"error": str(error)}), 400
```

## 5. JWT Authentication

```python
# pip install PyJWT

import jwt
import datetime
from functools import wraps
from flask import Flask, request, jsonify, g

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key-change-in-production"

def generate_token(user_id: int, role: str) -> str:
    """Generate a JWT token."""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")

def require_auth(f):
    """Decorator to require JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        try:
            payload = jwt.decode(
                token, app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            g.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return decorated

def require_role(role: str):
    """Decorator to require a specific role."""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            if g.current_user.get("role") != role:
                return jsonify({"error": "Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


# Routes
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    # In real app: validate against database
    if data.get("email") == "bharath@test.com" and data.get("password") == "pass123":
        token = generate_token(user_id=1, role="admin")
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/api/profile", methods=["GET"])
@require_auth
def get_profile():
    return jsonify({"user": g.current_user})

@app.route("/api/admin/users", methods=["GET"])
@require_role("admin")
def admin_users():
    return jsonify({"users": [{"id": 1, "name": "Bharath"}]})
```

## 6. Request Validation (with Pydantic)

```python
# pip install pydantic

from pydantic import BaseModel, Field, validator
from flask import Flask, request, jsonify
from typing import Optional

app = Flask(__name__)

# Pydantic models for validation (like Zod/Joi in JS)
class CreateCourseRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    instructor: str = Field(..., min_length=2)
    duration_hours: int = Field(..., ge=1, le=100)
    tags: list[str] = Field(default_factory=list)
    
    @validator("title")
    def title_must_be_capitalized(cls, v):
        if not v[0].isupper():
            raise ValueError("Title must start with uppercase")
        return v

class UpdateCourseRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    instructor: Optional[str] = None

# Validation decorator
def validate_body(model_class):
    """Decorator to validate request body with Pydantic."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                data = request.get_json()
                validated = model_class(**data)
                g.validated_data = validated
            except Exception as e:
                return jsonify({"error": "Validation failed", "details": str(e)}), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator

@app.route("/api/courses", methods=["POST"])
@validate_body(CreateCourseRequest)
def create_course():
    data = g.validated_data
    # data is now validated and typed!
    return jsonify({
        "data": {
            "title": data.title,
            "description": data.description,
            "instructor": data.instructor,
            "duration_hours": data.duration_hours,
            "tags": data.tags,
        }
    }), 201
```

## 7. SQLAlchemy ORM

```python
# pip install flask-sqlalchemy

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///courses.db"
# For PostgreSQL: "postgresql://user:password@localhost:5432/dbname"

db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default="viewer")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    courses = db.relationship("Course", backref="instructor_user", lazy=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }

class Course(db.Model):
    __tablename__ = "courses"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    duration_hours = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "instructor_id": self.instructor_id,
            "duration_hours": self.duration_hours,
        }


# CRUD Operations
@app.route("/api/courses", methods=["GET"])
def get_courses():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    
    pagination = Course.query.paginate(page=page, per_page=per_page)
    return jsonify({
        "data": [c.to_dict() for c in pagination.items],
        "total": pagination.total,
        "page": pagination.page,
        "pages": pagination.pages,
    })

@app.route("/api/courses", methods=["POST"])
def create_course():
    data = request.get_json()
    course = Course(
        title=data["title"],
        description=data.get("description"),
        instructor_id=data.get("instructor_id"),
        duration_hours=data.get("duration_hours"),
    )
    db.session.add(course)
    db.session.commit()
    return jsonify({"data": course.to_dict()}), 201

@app.route("/api/courses/<int:id>", methods=["PUT"])
def update_course(id):
    course = Course.query.get_or_404(id)
    data = request.get_json()
    
    course.title = data.get("title", course.title)
    course.description = data.get("description", course.description)
    db.session.commit()
    
    return jsonify({"data": course.to_dict()})

@app.route("/api/courses/<int:id>", methods=["DELETE"])
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    return jsonify({"message": "Course deleted"})

# Initialize DB
with app.app_context():
    db.create_all()
```

## 8. Error Handling (Production Grade)

```python
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

class APIError(Exception):
    """Base API error class."""
    def __init__(self, message: str, status_code: int = 400, details=None):
        self.message = message
        self.status_code = status_code
        self.details = details

class NotFoundError(APIError):
    def __init__(self, resource: str, id: int):
        super().__init__(f"{resource} with id {id} not found", 404)

class ValidationError(APIError):
    def __init__(self, errors: list):
        super().__init__("Validation failed", 400, details=errors)

class UnauthorizedError(APIError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)

# Register error handlers
def register_error_handlers(app: Flask):
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = {
            "error": error.message,
            "status_code": error.status_code,
        }
        if error.details:
            response["details"] = error.details
        return jsonify(response), error.status_code
    
    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return jsonify({
            "error": error.description,
            "status_code": error.code,
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        # Log the actual error
        app.logger.error(f"Unhandled error: {error}", exc_info=True)
        return jsonify({
            "error": "Internal server error",
            "status_code": 500,
        }), 500

# Usage in routes
@app.route("/api/courses/<int:id>")
def get_course(id):
    course = Course.query.get(id)
    if not course:
        raise NotFoundError("Course", id)
    return jsonify({"data": course.to_dict()})
```

## 9. CORS Setup

```python
# pip install flask-cors

from flask_cors import CORS

app = Flask(__name__)

# Allow all origins (development)
CORS(app)

# Production: specific origins
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "https://yourdomain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
    }
})
```

## 10. Full Project Structure

```
course-management-api/
├── app/
│   ├── __init__.py              # create_app() factory
│   ├── config.py                # Settings
│   ├── extensions.py            # db, jwt, cors instances
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── course.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── courses.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   └── course_service.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth.py
│   └── utils/
│       ├── __init__.py
│       ├── errors.py
│       └── validators.py
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_courses.py
├── .env
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Build Project: Course Management API

Follow these steps to build the complete API:

### Step 1: Setup
```bash
mkdir course-api && cd course-api
python -m venv venv
source venv/bin/activate
pip install flask flask-sqlalchemy flask-cors pyjwt python-dotenv pydantic
```

### Step 2: Build in this order:
1. Config & app factory
2. User model + auth routes
3. Course model + CRUD routes
4. JWT middleware
5. Validation with Pydantic
6. Error handling
7. Tests

This gives you a **production-ready Flask API** to show in interviews.

---

## Key Takeaways
1. Flask is minimal like Express.js — you add what you need
2. **Blueprints** = Express Router
3. **Decorators** = middleware
4. **SQLAlchemy** = Sequelize/Prisma equivalent
5. **Pydantic** = Zod/Joi equivalent
6. Use **app factory pattern** (create_app) for testing
7. Always add **CORS**, **error handling**, and **auth** from the start
