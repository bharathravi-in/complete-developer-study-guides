# Day 4: File Handling, Logging & Environment Management

## Why This Matters
- Reading/writing documents for RAG pipelines
- Logging API calls and errors in production
- Managing config files and environment variables
- Processing CSV, JSON, PDF files for AI training data

---

## 1. File Handling

### Basic File Operations
```python
# Writing files
with open("output.txt", "w") as f:
    f.write("Hello, AI World!\n")
    f.write("This is line 2\n")

# Reading files
with open("output.txt", "r") as f:
    content = f.read()         # Read entire file
    print(content)

# Reading line by line (memory efficient for large files)
with open("output.txt", "r") as f:
    for line in f:
        print(line.strip())    # strip() removes \n

# Reading all lines into a list
with open("output.txt", "r") as f:
    lines = f.readlines()      # ['Hello, AI World!\n', ...]

# Appending
with open("output.txt", "a") as f:
    f.write("Appended line\n")

# IMPORTANT: `with` statement auto-closes file (like try-with-resources)
# Never do: f = open("file.txt"); f.read(); f.close()  # risky!
```

### Working with JSON (Used Constantly)
```python
import json

# Python dict → JSON string
data = {
    "model": "gpt-4",
    "messages": [
        {"role": "system", "content": "You are helpful"},
        {"role": "user", "content": "What is RAG?"}
    ],
    "temperature": 0.7
}

# Write JSON file
with open("config.json", "w") as f:
    json.dump(data, f, indent=2)

# Read JSON file
with open("config.json", "r") as f:
    loaded = json.load(f)

# String conversion
json_str = json.dumps(data, indent=2)  # dict → string
parsed = json.loads(json_str)           # string → dict

# Handle custom types
from datetime import datetime

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

json.dumps({"time": datetime.now()}, cls=CustomEncoder)
```

### Working with CSV
```python
import csv

# Writing CSV
with open("users.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "role", "score"])
    writer.writeheader()
    writer.writerow({"name": "Bharath", "role": "AI Engineer", "score": 95})
    writer.writerow({"name": "Alice", "role": "ML Engineer", "score": 88})

# Reading CSV
with open("users.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['name']}: {row['score']}")
```

### Path Management (Modern Way)
```python
from pathlib import Path

# Creating paths
base = Path("/home/bharath/project")
data_dir = base / "data"          # /home/bharath/project/data
file_path = data_dir / "docs.json" # /home/bharath/project/data/docs.json

# Path operations
print(file_path.exists())         # True/False
print(file_path.is_file())        # True/False
print(file_path.is_dir())         # True/False
print(file_path.suffix)           # .json
print(file_path.stem)             # docs
print(file_path.parent)           # /home/bharath/project/data
print(file_path.name)             # docs.json

# Create directories
data_dir.mkdir(parents=True, exist_ok=True)

# List files
for f in data_dir.glob("*.json"):
    print(f)

# Recursive glob
for f in base.rglob("*.py"):     # All .py files recursively
    print(f)

# Read/write (simpler than open())
content = file_path.read_text()
file_path.write_text("new content")
```

---

## 2. Logging

### Basic Logging
```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)

# Log levels (from least to most severe)
logger.debug("Detailed debugging info")      # DEBUG
logger.info("General information")            # INFO
logger.warning("Something unexpected")        # WARNING
logger.error("Something failed")              # ERROR
logger.critical("System is broken!")           # CRITICAL

# With context
logger.info("Processing document", extra={"doc_id": 123})
logger.error("API call failed: %s", "timeout", exc_info=True)
```

### Production Logging Setup
```python
import logging
import logging.handlers
from pathlib import Path

def setup_logging(log_dir: str = "logs", level: str = "INFO"):
    """Production-grade logging setup."""
    Path(log_dir).mkdir(exist_ok=True)
    
    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s"
    )
    
    # File handler (rotates at 10MB, keeps 5 backups)
    file_handler = logging.handlers.RotatingFileHandler(
        f"{log_dir}/app.log",
        maxBytes=10_000_000,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, level))
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

# Usage
setup_logging()
logger = logging.getLogger("ai_service")
logger.info("AI service started")
logger.error("Embedding generation failed", exc_info=True)
```

### Structured Logging (JSON Logs for Production)
```python
import json
import logging
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON (for Elasticsearch/Datadog/etc.)."""
    
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        
        return json.dumps(log_entry)

# Usage
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger("api")
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("Request received", extra={"request_id": "abc-123"})
# Output: {"timestamp": "2024-...", "level": "INFO", "message": "Request received", "request_id": "abc-123"}
```

---

## 3. Environment Variables & Configuration

### Using os.environ
```python
import os

# Get environment variable
api_key = os.environ.get("OPENAI_API_KEY", "not-set")
debug = os.environ.get("DEBUG", "false").lower() == "true"

# Required env var (raises error if missing)
api_key = os.environ["OPENAI_API_KEY"]  # KeyError if not set
```

### Using python-dotenv (Like dotenv in Node.js)
```python
# pip install python-dotenv

# .env file:
# OPENAI_API_KEY=sk-xxx
# QDRANT_URL=http://localhost:6333
# REDIS_URL=redis://localhost:6379
# DEBUG=true
# MODEL_NAME=gpt-4

from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Now access like normal env vars
api_key = os.getenv("OPENAI_API_KEY")
qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
```

### Pydantic Settings (Best Practice for Production)
```python
# pip install pydantic-settings

from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    """Type-safe configuration with validation.
    Like a TypeScript interface for env vars!
    """
    
    # Required
    openai_api_key: str = Field(..., description="OpenAI API key")
    
    # With defaults
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096
    
    # With env var name mapping
    qdrant_url: str = Field(
        default="http://localhost:6333",
        env="QDRANT_URL"  # Maps to QDRANT_URL env var
    )
    redis_url: str = "redis://localhost:6379"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Usage
settings = Settings()
print(settings.openai_api_key)
print(settings.model_name)
print(settings.debug)
```

---

## 4. Virtual Environments

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install packages
pip install flask redis qdrant-client openai

# Save dependencies (like package.json)
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# Deactivate
deactivate
```

### Poetry (Better Package Manager - Like npm)
```bash
# Install poetry
pip install poetry

# Initialize project
poetry init

# Add dependencies
poetry add flask redis qdrant-client openai
poetry add --dev pytest black mypy

# Install all dependencies
poetry install

# Run in virtual env
poetry run python app.py
poetry run pytest
```

### pyproject.toml (Modern Python Project Config)
```toml
[tool.poetry]
name = "ai-platform"
version = "0.1.0"
description = "AI Knowledge Assistant"

[tool.poetry.dependencies]
python = "^3.11"
flask = "^3.0"
redis = "^5.0"
qdrant-client = "^1.7"
openai = "^1.0"

[tool.poetry.dev-dependencies]
pytest = "^7.0"
black = "^23.0"
mypy = "^1.0"
```

---

## Exercises

### Exercise 1: Document File Processor
```python
# Build a function that:
# 1. Reads all .txt files from a directory
# 2. Cleans and processes text
# 3. Splits into chunks of N characters
# 4. Saves as JSON with metadata (filename, chunk_index, text)
# This is exactly what you'll do in RAG pipelines!

# TODO: Implement
```

### Exercise 2: Application Logger
```python
# Build a logging utility class that:
# 1. Supports both file and console logging
# 2. Rotates log files
# 3. Adds request_id to all log entries
# 4. Has convenience methods: log_api_call(), log_error(), log_embedding()

# TODO: Implement
```

### Exercise 3: Config Manager
```python
# Build a config system that:
# 1. Reads from .env file
# 2. Validates required keys
# 3. Has type conversion (str → int, bool, float)
# 4. Supports profiles (dev, staging, prod)
# 5. Provides a singleton access pattern

# TODO: Implement
```

---

## Key Takeaways for Day 4
1. Always use `with` statement for files (auto-closes)
2. Use **pathlib.Path** for file paths (modern Python)
3. **json** module for API data — learn it well
4. Set up **proper logging** from day 1 in any project
5. Use **python-dotenv** or **pydantic-settings** for config
6. Always use **virtual environments** (never install globally)
7. Consider **Poetry** as your package manager
