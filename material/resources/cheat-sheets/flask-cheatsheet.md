# Flask Cheat Sheet

## App Setup
```python
from flask import Flask, request, jsonify
app = Flask(__name__)

# With factory pattern
def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    register_routes(app)
    return app
```

## Routes
```python
@app.route("/")
def index():
    return jsonify({"status": "ok"})

@app.route("/items", methods=["GET"])
def list_items():
    page = request.args.get("page", 1, type=int)
    return jsonify(items)

@app.route("/items", methods=["POST"])
def create_item():
    data = request.get_json()
    return jsonify(item), 201

@app.route("/items/<int:id>", methods=["PUT"])
def update_item(id):
    data = request.get_json()
    return jsonify(updated)

@app.route("/items/<int:id>", methods=["DELETE"])
def delete_item(id):
    return "", 204
```

## Blueprints (like Express Router)
```python
from flask import Blueprint
bp = Blueprint("items", __name__, url_prefix="/api/items")

@bp.route("/", methods=["GET"])
def list_items():
    return jsonify([])

# Register
app.register_blueprint(bp)
```

## Request Data
```python
request.get_json()           # JSON body
request.args.get("key")      # Query param
request.form.get("key")      # Form data
request.files["file"]        # File upload
request.headers.get("Auth")  # Headers
request.method               # GET, POST, etc.
```

## Responses
```python
return jsonify(data)                    # JSON
return jsonify(data), 201               # With status
return jsonify(error="msg"), 400        # Error
return "", 204                          # No content
return Response(gen(), mimetype="text/event-stream")  # SSE
```

## Middleware
```python
@app.before_request
def before():
    # Auth check, logging
    pass

@app.after_request
def after(response):
    response.headers["X-Request-Id"] = str(uuid4())
    return response

@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Not found"), 404

@app.errorhandler(Exception)
def handle_error(e):
    return jsonify(error=str(e)), 500
```

## JWT Auth Pattern
```python
import jwt
from functools import wraps

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET, algorithms=["HS256"])
            request.user_id = payload["user_id"]
        except jwt.InvalidTokenError:
            return jsonify(error="Unauthorized"), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/protected")
@require_auth
def protected():
    return jsonify(user_id=request.user_id)
```

## SSE Streaming
```python
@app.route("/stream")
def stream():
    def generate():
        for token in llm_stream():
            yield f"data: {json.dumps({'token': token})}\n\n"
        yield f"data: {json.dumps({'done': True})}\n\n"
    
    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache",
                             "X-Accel-Buffering": "no"})
```

## Testing
```python
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200

def test_create(client):
    r = client.post("/items", json={"name": "test"})
    assert r.status_code == 201
```

## Run
```bash
flask run --debug          # Development
gunicorn -w 4 "app:create_app()"  # Production
```
