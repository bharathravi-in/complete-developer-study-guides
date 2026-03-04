# Day 14 - Testing & Code Quality

## Topics Covered
- unittest
- pytest
- Mocking
- Code formatters (black, ruff)
- Linters (flake8, ruff)

## pytest Features
- Simple `assert` statements
- Fixtures for setup/teardown
- Parameterized tests
- Markers and plugins

## Install Tools
```bash
pip install pytest pytest-cov black ruff mypy
```

## Commands
```bash
# Run tests
pytest tests/ -v

# With coverage
pytest --cov=src tests/

# Format code
black .
ruff format .

# Lint code
ruff check .
```

## Run
```bash
pytest test_calculator.py -v
python -m pytest test_calculator.py -v
```
