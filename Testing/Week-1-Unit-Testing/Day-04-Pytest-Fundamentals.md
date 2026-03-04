# Day 4: Pytest Fundamentals – Python Testing Mastery

## 📚 Topics to Cover (3-4 hours)

---

## 1. Pytest Setup & Configuration

```bash
# Install
pip install pytest pytest-cov pytest-asyncio pytest-mock

# Run tests
pytest                          # discover and run all tests
pytest -v                       # verbose output
pytest -x                       # stop on first failure
pytest -k "test_login"          # run tests matching keyword
pytest tests/test_user.py       # run specific file
pytest tests/test_user.py::test_create  # run specific test
pytest --tb=short               # shorter traceback
pytest -s                       # show print statements
```

### pytest.ini / pyproject.toml

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
python_classes = "Test*"
addopts = "-v --tb=short --strict-markers"
markers = [
    "slow: marks tests as slow",
    "integration: marks integration tests",
    "unit: marks unit tests",
]
```

---

## 2. Basic Assertions

```python
# Pytest uses plain assert statements (no special methods!)
def test_addition():
    assert 2 + 2 == 4

def test_string():
    assert "hello" in "hello world"

def test_list():
    assert [1, 2, 3] == [1, 2, 3]

def test_dict():
    result = {"name": "John", "age": 30}
    assert result["name"] == "John"
    assert "age" in result

def test_exception():
    with pytest.raises(ValueError):
        int("not a number")

    with pytest.raises(ValueError, match="invalid literal"):
        int("not a number")

def test_approximate():
    assert 0.1 + 0.2 == pytest.approx(0.3)
    assert [0.1 + 0.2, 0.2 + 0.4] == pytest.approx([0.3, 0.6])
```

---

## 3. Fixtures – Pytest's Power Feature

```python
import pytest

# Basic fixture
@pytest.fixture
def user():
    return {"id": 1, "name": "John", "email": "john@test.com"}

def test_user_name(user):
    assert user["name"] == "John"

# Fixture with setup and teardown
@pytest.fixture
def db_connection():
    # Setup
    conn = create_connection("test.db")
    yield conn  # This is where the test runs
    # Teardown
    conn.close()
    os.remove("test.db")

# Fixture scopes
@pytest.fixture(scope="module")  # once per module
def expensive_resource():
    return create_expensive_thing()

@pytest.fixture(scope="session")  # once per entire test session
def database():
    db = setup_test_database()
    yield db
    teardown_test_database(db)

@pytest.fixture(scope="class")  # once per test class
def api_client():
    return TestClient(app)

# Auto-use fixture (applied to all tests)
@pytest.fixture(autouse=True)
def reset_state():
    global_state.clear()
    yield
    global_state.clear()
```

### Fixture Factories

```python
@pytest.fixture
def make_user():
    created_users = []
    
    def _make_user(name="John", email="john@test.com", role="user"):
        user = User(name=name, email=email, role=role)
        created_users.append(user)
        return user
    
    yield _make_user
    
    # Cleanup all created users
    for user in created_users:
        user.delete()

def test_admin_user(make_user):
    admin = make_user(name="Admin", role="admin")
    assert admin.role == "admin"
    assert admin.has_permission("delete")
```

### conftest.py – Shared Fixtures

```python
# conftest.py (in tests/ directory)
import pytest
from myapp import create_app

@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers():
    token = generate_test_token()
    return {"Authorization": f"Bearer {token}"}
```

---

## 4. Parametrize – Data-Driven Testing

```python
# Multiple inputs, single test function
@pytest.mark.parametrize("input,expected", [
    (1, 1),
    (2, 4),
    (3, 9),
    (4, 16),
    (-1, 1),
])
def test_square(input, expected):
    assert input ** 2 == expected

# Multiple parameters
@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add(a, b, expected):
    assert add(a, b) == expected

# Parametrize with IDs for clarity
@pytest.mark.parametrize("email,valid", [
    ("user@test.com", True),
    ("invalid-email", False),
    ("", False),
    ("user@.com", False),
], ids=["valid_email", "no_at_sign", "empty", "no_domain"])
def test_validate_email(email, valid):
    assert validate_email(email) == valid

# Parametrize with expected exceptions
@pytest.mark.parametrize("value,error", [
    (-1, ValueError),
    ("abc", TypeError),
    (None, TypeError),
])
def test_errors(value, error):
    with pytest.raises(error):
        process_value(value)
```

---

## 5. Mocking with pytest-mock

```python
# Using mocker fixture (pytest-mock)
def test_send_email(mocker):
    mock_smtp = mocker.patch('myapp.email.smtplib.SMTP')
    
    send_welcome_email("user@test.com")
    
    mock_smtp.return_value.sendmail.assert_called_once()

def test_api_call(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"users": []}
    
    mocker.patch('requests.get', return_value=mock_response)
    
    result = fetch_users()
    assert result == []

# Using unittest.mock directly
from unittest.mock import patch, MagicMock, AsyncMock

@patch('myapp.services.external_api')
def test_service(mock_api):
    mock_api.get_data.return_value = {"key": "value"}
    result = my_service.process()
    assert result["key"] == "value"

# Context manager style
def test_with_context():
    with patch('myapp.db.query') as mock_query:
        mock_query.return_value = [{"id": 1}]
        result = get_all_items()
        assert len(result) == 1
```

---

## 6. Async Testing

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await fetch_data_async()
    assert result is not None

@pytest.mark.asyncio
async def test_async_with_mock(mocker):
    mocker.patch(
        'myapp.client.make_request',
        return_value=AsyncMock(return_value={"status": "ok"})()
    )
    result = await process_async()
    assert result["status"] == "ok"

# Async fixture
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_endpoint(async_client):
    response = await async_client.get("/api/users")
    assert response.status_code == 200
```

---

## 7. Coverage

```bash
# Run with coverage
pytest --cov=myapp --cov-report=html --cov-report=term-missing

# Coverage config in pyproject.toml
[tool.coverage.run]
source = ["myapp"]
omit = ["tests/*", "*/migrations/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.",
    "if TYPE_CHECKING:",
]
```

---

## 8. Markers & Custom Markers

```python
# Skip test
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

# Skip conditionally
@pytest.mark.skipif(sys.platform == "win32", reason="Linux only")
def test_linux_feature():
    pass

# Expected failure
@pytest.mark.xfail(reason="Known bug #123")
def test_known_bug():
    assert buggy_function() == expected

# Custom markers
@pytest.mark.slow
def test_large_dataset():
    # Run with: pytest -m "not slow"
    pass

@pytest.mark.integration
def test_database_connection():
    pass
```

---

## 🎯 Interview Questions

### Q1: What makes Pytest superior to unittest?
**A:** Simpler syntax (plain `assert`), powerful fixtures with dependency injection, parametrize for data-driven tests, auto-discovery, rich plugin ecosystem, better error messages, no class inheritance needed.

### Q2: Explain pytest fixture scopes
**A:** `function` (default): per test, `class`: per class, `module`: per file, `package`: per package, `session`: per entire session. Higher scopes share state, reducing setup cost but requiring careful isolation.

### Q3: How do you test Flask/FastAPI endpoints?
**A:** Create a test client fixture (`app.test_client()` for Flask, `TestClient(app)` for FastAPI). Use it to make HTTP requests and assert responses. Use fixtures for database setup/teardown.

---

## 📝 Practice Exercises

1. Write parametrized tests for a password validator
2. Create fixtures with factory pattern for User, Order, Product
3. Test a Flask REST API with mocked database
4. Write async tests for a FastAPI endpoint
