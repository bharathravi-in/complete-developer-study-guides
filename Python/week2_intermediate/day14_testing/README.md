# Day 14: Testing & Code Quality — pytest, Mocking & TDD

## Learning Objectives
- Write effective tests with pytest (fixtures, parametrize, markers)
- Mock external dependencies for isolated unit tests
- Measure and improve code coverage
- Apply TDD (Test-Driven Development) workflow
- Set up code quality tooling (ruff, black, mypy)

---

## 1. pytest Fundamentals (Beginner)

```python
# tests/test_calculator.py
import pytest
from src.calculator import Calculator

class TestCalculator:
    """Group related tests in a class."""
    
    def setup_method(self):
        """Runs before each test method."""
        self.calc = Calculator()
    
    def test_add(self):
        assert self.calc.add(2, 3) == 5
    
    def test_add_negative(self):
        assert self.calc.add(-1, -1) == -2
    
    def test_divide(self):
        assert self.calc.divide(10, 2) == 5.0
    
    def test_divide_by_zero_raises(self):
        with pytest.raises(ZeroDivisionError, match="Cannot divide by zero"):
            self.calc.divide(10, 0)
    
    def test_float_precision(self):
        # Use approx for floating point
        assert self.calc.divide(1, 3) == pytest.approx(0.333, rel=1e-2)


# Parametrized tests — run same test with multiple inputs
@pytest.mark.parametrize("a, b, expected", [
    (1, 1, 2),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
    (1.5, 2.5, 4.0),
])
def test_add_parametrized(a, b, expected):
    calc = Calculator()
    assert calc.add(a, b) == expected
```

### Fixtures

```python
import pytest
from pathlib import Path
import json

@pytest.fixture
def sample_user():
    """Provides test user data."""
    return {"name": "Alice", "email": "alice@test.com", "age": 30}

@pytest.fixture
def tmp_config(tmp_path):
    """Create a temporary config file."""
    config = {"database": "test.db", "debug": True}
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps(config))
    return config_file

@pytest.fixture
def db_connection():
    """Setup and teardown pattern."""
    conn = create_test_database()
    yield conn  # Test runs here
    conn.close()
    cleanup_test_database()

# Using fixtures
def test_user_creation(sample_user, db_connection):
    user = User.create(sample_user, db=db_connection)
    assert user.name == "Alice"
    assert user.id is not None
```

---

## 2. Mocking & Test Doubles (Intermediate)

```python
from unittest.mock import Mock, patch, MagicMock, AsyncMock
import pytest

# The service we're testing
class UserService:
    def __init__(self, db, email_client):
        self.db = db
        self.email_client = email_client
    
    def register(self, name: str, email: str) -> dict:
        if self.db.find_by_email(email):
            raise ValueError("Email already exists")
        user = self.db.create({"name": name, "email": email})
        self.email_client.send_welcome(email)
        return user


class TestUserService:
    def setup_method(self):
        self.mock_db = Mock()
        self.mock_email = Mock()
        self.service = UserService(self.mock_db, self.mock_email)
    
    def test_register_success(self):
        # Configure mock behavior
        self.mock_db.find_by_email.return_value = None
        self.mock_db.create.return_value = {"id": 1, "name": "Bob", "email": "bob@test.com"}
        
        result = self.service.register("Bob", "bob@test.com")
        
        # Assert behavior
        assert result["id"] == 1
        self.mock_db.create.assert_called_once_with({"name": "Bob", "email": "bob@test.com"})
        self.mock_email.send_welcome.assert_called_once_with("bob@test.com")
    
    def test_register_duplicate_email(self):
        self.mock_db.find_by_email.return_value = {"id": 1}
        
        with pytest.raises(ValueError, match="already exists"):
            self.service.register("Bob", "bob@test.com")
        
        # Email should NOT have been sent
        self.mock_email.send_welcome.assert_not_called()


# Patching external modules
@patch("src.service.requests.get")
def test_fetch_data(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"data": "test"}
    
    result = fetch_data("http://api.example.com/data")
    assert result == {"data": "test"}
    mock_get.assert_called_once_with("http://api.example.com/data", timeout=30)


# Async mocking
@pytest.mark.asyncio
async def test_async_operation():
    mock_client = AsyncMock()
    mock_client.fetch.return_value = {"status": "ok"}
    
    result = await process_async(mock_client)
    assert result["status"] == "ok"
```

### Testing Exceptions & Edge Cases

```python
@pytest.mark.parametrize("invalid_input,expected_error", [
    ("", ValueError),
    (None, TypeError),
    (-1, ValueError),
    ("x" * 1000, ValueError),
])
def test_invalid_inputs(invalid_input, expected_error):
    with pytest.raises(expected_error):
        validate_input(invalid_input)

# Testing that specific warnings are raised
def test_deprecation_warning():
    with pytest.warns(DeprecationWarning, match="old_function"):
        old_function()

# Testing logging output
def test_logs_error(caplog):
    import logging
    with caplog.at_level(logging.ERROR):
        process_bad_data(None)
    assert "Invalid data" in caplog.text
```

---

## 3. Advanced Testing Patterns (Advanced)

### Test-Driven Development (TDD)

```python
# TDD Cycle: RED → GREEN → REFACTOR

# Step 1 (RED): Write a failing test
def test_password_strength():
    assert is_strong_password("Abc123!@") == True
    assert is_strong_password("weak") == False
    assert is_strong_password("NoSpecial123") == False
    assert is_strong_password("no_upper_123!") == False

# Step 2 (GREEN): Minimal implementation to pass
def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*" for c in password)
    return all([has_upper, has_lower, has_digit, has_special])

# Step 3 (REFACTOR): Improve without changing behavior
import re
def is_strong_password(password: str) -> bool:
    checks = [
        len(password) >= 8,
        re.search(r'[A-Z]', password),
        re.search(r'[a-z]', password),
        re.search(r'\d', password),
        re.search(r'[!@#$%^&*]', password),
    ]
    return all(checks)
```

### Fixtures with Factories & Conftest

```python
# conftest.py — shared fixtures across all tests
import pytest
from faker import Faker

fake = Faker()

@pytest.fixture
def user_factory():
    """Factory fixture — create users with custom overrides."""
    def _create_user(**overrides):
        defaults = {
            "name": fake.name(),
            "email": fake.email(),
            "age": fake.random_int(18, 80),
            "active": True,
        }
        defaults.update(overrides)
        return User(**defaults)
    return _create_user

@pytest.fixture(autouse=True)
def reset_database(db):
    """Automatically clean DB before each test."""
    db.truncate_all()
    yield
    db.truncate_all()

# Usage in tests
def test_deactivate_user(user_factory, db):
    user = user_factory(active=True)
    db.save(user)
    
    deactivate(user.id)
    
    updated = db.find(user.id)
    assert updated.active == False
```

### Coverage & CI Integration

```bash
# Run with coverage
pytest --cov=src --cov-report=html --cov-branch tests/

# Fail if coverage drops below threshold
pytest --cov=src --cov-fail-under=80 tests/

# Generate XML for CI
pytest --cov=src --cov-report=xml tests/
```

```ini
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (deselect with '-m not slow')",
    "integration: integration tests requiring external services",
]
addopts = "-v --tb=short --strict-markers"

[tool.coverage.run]
branch = true
source = ["src"]
omit = ["*/tests/*", "*/__pycache__/*"]

[tool.coverage.report]
fail_under = 80
show_missing = true
```

---

## Interview Questions

### Beginner
1. **What's the difference between `unittest` and `pytest`?** pytest: simpler (plain `assert`), auto-discovery, powerful fixtures, parametrize, better output, rich plugin ecosystem. unittest: built-in (no install), class-based (`self.assertEqual`), more verbose, Java-inspired. Industry standard: pytest. Use unittest only when: no external dependencies allowed, or existing codebase uses it.

2. **What is a test fixture?** A fixture provides a known state for tests: test data, database connections, mock objects, temp files. In pytest: `@pytest.fixture` functions that inject dependencies into tests. Can have setup AND teardown (`yield`). Scopes: function (default), class, module, session. Fixtures make tests independent and repeatable.

3. **What does `pytest.raises` do?** It's a context manager that asserts an exception is raised. `with pytest.raises(ValueError, match="invalid"):` — verifies both the exception type and optionally the message (regex match). If no exception or wrong type: test fails. It's the pytest equivalent of `self.assertRaises` in unittest.

### Intermediate
4. **Explain mocking — when and why to mock?** Mocking replaces real dependencies with controlled fakes. Mock when: external services (APIs, DB), slow operations, non-deterministic behavior (time, random), side effects (emails, payments). DON'T mock: the thing under test, simple value objects. Rule: mock at boundaries, test behavior not implementation.

5. **What's the difference between `Mock`, `MagicMock`, and `patch`?** `Mock`: basic mock object, configurable return values and assertions. `MagicMock`: extends Mock with all magic methods pre-configured (`__len__`, `__iter__`, etc.). `patch`: decorator/context manager that replaces objects in a specific module namespace during test. Use `patch` for module-level replacements, `Mock/MagicMock` for injected dependencies.

6. **How do you test async code with pytest?** Install `pytest-asyncio`. Mark tests with `@pytest.mark.asyncio`. Use `AsyncMock` for mocking async functions. Fixture for async setup: `@pytest_asyncio.fixture`. For testing streams/generators: `async for` in tests. Key: event loop management is handled by the plugin.

### Advanced
7. **How do you design tests for non-deterministic systems (AI, random)?** Seed random generators for reproducibility. Test statistical properties (output within expected distribution over N runs). Snapshot testing (save known-good output, detect changes). Property-based testing (Hypothesis): define invariants, framework generates inputs. For AI: test format/structure, not exact content.

8. **Explain property-based testing with Hypothesis.** Instead of specific examples, define PROPERTIES that must hold for ALL inputs. Hypothesis generates random inputs trying to find counterexamples. Example: `@given(st.lists(st.integers()))` def test_sort_preserves_length(lst): assert len(sorted(lst)) == len(lst). Finds edge cases you'd never think of (empty lists, huge numbers, unicode).

9. **How do you structure tests for a large application?** Mirror source structure: `src/auth/service.py` → `tests/auth/test_service.py`. Layers: unit (fast, isolated, most) → integration (real DB, fewer) → e2e (full stack, fewest). Shared fixtures in `conftest.py` at appropriate levels. Markers for slow/integration tests. CI: run unit on every push, integration on merge.

---

## Hands-On Exercise
1. Write tests for a `UserService` with mocked DB and email dependencies
2. Use `@pytest.mark.parametrize` to test 10+ edge cases for a validator
3. Set up coverage reporting and achieve 90%+ on a small module
4. Practice TDD: write tests FIRST for a shopping cart, then implement
5. Configure `pyproject.toml` with pytest, coverage, ruff, and mypy settings
