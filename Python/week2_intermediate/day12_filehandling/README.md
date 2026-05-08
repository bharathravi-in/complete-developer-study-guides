# Day 12: File Handling — I/O, Serialization & Context Managers

## Learning Objectives
- Master file reading/writing with proper resource management
- Handle JSON, CSV, and binary file formats
- Build custom context managers for resource management
- Process large files efficiently without loading into memory
- Understand encoding, pathlib, and file system operations

---

## 1. File I/O Basics (Beginner)

```python
from pathlib import Path

# ALWAYS use context managers (with statement)
# Guarantees file is closed even if exception occurs

# Reading files
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()        # Entire file as string
    # OR
    # lines = f.readlines()   # List of lines
    # OR
    # for line in f:          # Memory-efficient line-by-line
    #     process(line)

# Writing files
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello, World!\n")
    f.writelines(["line 1\n", "line 2\n"])

# Appending
with open("log.txt", "a", encoding="utf-8") as f:
    f.write(f"New entry at {datetime.now()}\n")

# File modes
# 'r'  - Read (default, error if not exists)
# 'w'  - Write (creates/overwrites)
# 'a'  - Append (creates if not exists)
# 'x'  - Exclusive create (error if exists)
# 'b'  - Binary mode (add to above: 'rb', 'wb')
# '+'  - Read and write ('r+', 'w+')
```

### Pathlib — Modern File System Operations

```python
from pathlib import Path

# Path operations (OS-independent)
project = Path("/home/user/project")
config = project / "config" / "settings.json"  # Path joining with /

print(config.exists())      # True/False
print(config.is_file())     # True
print(config.suffix)        # .json
print(config.stem)          # settings
print(config.parent)        # /home/user/project/config

# Reading/writing with pathlib (Python 3.12+)
text = config.read_text(encoding="utf-8")
config.write_text('{"key": "value"}', encoding="utf-8")

# Directory operations
data_dir = Path("./data")
data_dir.mkdir(parents=True, exist_ok=True)

# Glob patterns
for py_file in project.rglob("*.py"):  # Recursive
    print(py_file)

# Iterate directory
for item in data_dir.iterdir():
    if item.is_file():
        print(f"{item.name}: {item.stat().st_size} bytes")
```

---

## 2. Structured Data Formats (Intermediate)

### JSON

```python
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

# Reading JSON
with open("config.json", "r") as f:
    config = json.load(f)  # File → dict

# Writing JSON
data = {"users": [{"name": "Alice", "age": 30}], "count": 1}
with open("output.json", "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# String conversion
json_str = json.dumps(data, indent=2)
parsed = json.loads(json_str)

# Custom serialization (handle non-JSON types)
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, Path):
            return str(obj)
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)

json.dumps({"time": datetime.now()}, cls=CustomEncoder)
```

### CSV

```python
import csv
from typing import Iterator

# Reading CSV
def read_csv(filepath: str) -> list[dict]:
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

# Writing CSV
def write_csv(filepath: str, data: list[dict]):
    if not data:
        return
    fieldnames = data[0].keys()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

# Memory-efficient CSV processing (generator)
def stream_csv(filepath: str) -> Iterator[dict]:
    """Process large CSV without loading all into memory."""
    with open(filepath, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

# Process 10GB CSV in constant memory
for row in stream_csv("huge_file.csv"):
    if float(row["amount"]) > 1000:
        process(row)
```

### Binary Files

```python
import struct
import pickle

# Binary read/write
with open("image.bin", "rb") as f:
    header = f.read(8)  # Read 8 bytes
    width, height = struct.unpack(">II", header)  # Big-endian uint32

# Pickle (Python object serialization)
# WARNING: Never unpickle untrusted data (security risk!)
data = {"key": [1, 2, 3], "set": {4, 5, 6}}
with open("data.pkl", "wb") as f:
    pickle.dump(data, f)

with open("data.pkl", "rb") as f:
    loaded = pickle.load(f)
```

---

## 3. Custom Context Managers (Advanced)

```python
from contextlib import contextmanager, ExitStack
import tempfile
import os

# Class-based context manager
class FileTransaction:
    """Write to temp file, rename on success (atomic write)."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.temp_path = filepath + ".tmp"
        self._file = None
    
    def __enter__(self):
        self._file = open(self.temp_path, "w", encoding="utf-8")
        return self._file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()
        if exc_type is None:
            # Success: atomically replace original
            os.replace(self.temp_path, self.filepath)
        else:
            # Error: remove temp file
            os.unlink(self.temp_path)
        return False  # Don't suppress exceptions

# Usage: file is only updated if no errors
with FileTransaction("config.json") as f:
    json.dump({"status": "updated"}, f)


# Generator-based context manager
@contextmanager
def temp_directory():
    """Create temp dir, clean up after."""
    dirpath = tempfile.mkdtemp()
    try:
        yield Path(dirpath)
    finally:
        import shutil
        shutil.rmtree(dirpath)

with temp_directory() as tmpdir:
    (tmpdir / "test.txt").write_text("temporary")
# Directory and contents automatically deleted


# ExitStack — dynamic context manager management
def process_multiple_files(filepaths: list[str]):
    """Open variable number of files safely."""
    with ExitStack() as stack:
        files = [
            stack.enter_context(open(fp, "r"))
            for fp in filepaths
        ]
        # All files open, all will be closed on exit
        for f in files:
            process(f.read())
```

### Advanced: File Watcher

```python
import time
from pathlib import Path
from typing import Callable

class FileWatcher:
    """Watch files for changes and trigger callbacks."""
    
    def __init__(self, path: str, callback: Callable):
        self.path = Path(path)
        self.callback = callback
        self._last_modified = {}
    
    def check(self):
        for filepath in self.path.rglob("*"):
            if filepath.is_file():
                mtime = filepath.stat().st_mtime
                if filepath not in self._last_modified:
                    self._last_modified[filepath] = mtime
                elif mtime > self._last_modified[filepath]:
                    self._last_modified[filepath] = mtime
                    self.callback(filepath, "modified")
    
    def watch(self, interval: float = 1.0):
        """Blocking watch loop."""
        print(f"Watching {self.path}...")
        while True:
            self.check()
            time.sleep(interval)
```

---

## Interview Questions

### Beginner
1. **Why use `with` statement for file operations?** `with` implements the context manager protocol, guaranteeing `__exit__` (cleanup/close) runs even if exceptions occur. Without `with`, you risk resource leaks (open file handles), which can exhaust OS limits. It's equivalent to try/finally but cleaner and less error-prone.

2. **What's the difference between `read()`, `readline()`, and `readlines()`?** `read()`: entire file as one string (loads all into memory). `readline()`: one line at a time (memory-efficient, manual loop). `readlines()`: all lines as a list (all in memory). Best practice: iterate the file object directly (`for line in f`) — it's lazy and memory-efficient.

3. **When should you specify encoding?** Always! Default encoding varies by OS (Windows: cp1252, Linux: utf-8). Explicitly set `encoding='utf-8'` for portability. Common bugs: opening UTF-8 files without specifying encoding on Windows gives `UnicodeDecodeError`. Use `errors='replace'` or `errors='ignore'` for damaged files.

### Intermediate
4. **How do you handle very large files (larger than RAM)?** Read line-by-line (generator pattern): `for line in f`. Use chunked reading: `while chunk := f.read(8192)`. For CSV: `csv.reader` with iteration. For binary: `iter(lambda: f.read(4096), b'')`. Key: never call `f.read()` or `f.readlines()` on large files.

5. **Explain the context manager protocol (`__enter__`/`__exit__`).** `__enter__` is called when entering `with` block, returns the value for `as` variable. `__exit__(exc_type, exc_val, tb)` is called when leaving (success or exception). Returns `True` to suppress exception, `False` to propagate. Use for: resource management (files, locks, connections, transactions).

6. **How do you safely write files (avoid corruption on crash)?** Atomic write pattern: write to temp file → fsync → rename/replace over original. `os.replace()` is atomic on POSIX. Libraries: `tempfile.NamedTemporaryFile` + `os.replace()`. For critical data: also keep backup of previous version before replacing.

### Advanced
7. **Compare `json.dump` vs `pickle.dump` — security implications?** JSON: text format, safe to load from untrusted sources, limited types (no datetime, set, custom objects). Pickle: binary, can serialize ANY Python object, but **NEVER load untrusted pickle** — it can execute arbitrary code during deserialization (remote code execution vulnerability). Use JSON for external data, pickle only for internal cache/state.

8. **How would you implement a file-based database with ACID guarantees?** Write-Ahead Log (WAL): log changes before applying. Atomic writes via temp+rename. Use `os.fsync()` to ensure data reaches disk. Implement locking (`fcntl.flock`) for concurrent access. Recovery: replay WAL on startup. This is how SQLite works internally.

9. **Explain `ExitStack` and when to use it.** `ExitStack` manages a dynamic number of context managers. Use when: number of resources is determined at runtime (variable file count), resources acquired conditionally, building complex resource management. Also useful for exception handling: `stack.callback()` registers cleanup functions.

---

## Hands-On Exercise
1. Build a `FileTransaction` class for atomic JSON config updates
2. Write a CSV processor that handles 1GB files in constant memory
3. Implement a custom `@contextmanager` for database connection pooling
4. Create a file watcher that detects changes and triggers callbacks
5. Build a log rotation system (max size → archive → new file)
