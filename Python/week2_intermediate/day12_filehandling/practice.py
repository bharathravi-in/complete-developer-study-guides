#!/usr/bin/env python3
"""Day 12 - File Handling Deep Dive"""

import json
import csv
import tempfile
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Any, Iterator

print("=" * 50)
print("FILE HANDLING DEEP DIVE")
print("=" * 50)

# Create temp directory for demos
TEMP_DIR = tempfile.mkdtemp()

# ============================================
# 1. BASIC FILE OPERATIONS
# ============================================
print("\n--- 1. BASIC FILE OPERATIONS ---")

# Writing text
file_path = Path(TEMP_DIR) / "sample.txt"

with open(file_path, 'w', encoding='utf-8') as f:
    f.write("Hello, World!\n")
    f.write("Python file handling.\n")
    f.writelines(["Line 3\n", "Line 4\n"])

print(f"File created: {file_path}")

# Reading methods
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
    print(f"\nread():\n{content}")

with open(file_path, 'r') as f:
    lines = f.readlines()
    print(f"readlines(): {lines}")

with open(file_path, 'r') as f:
    first_line = f.readline()
    print(f"readline(): {first_line!r}")

# Iterate lines (memory efficient)
print("\nIterate lines:")
with open(file_path, 'r') as f:
    for i, line in enumerate(f, 1):
        print(f"  {i}: {line.strip()}")


# ============================================
# 2. FILE MODES
# ============================================
print("\n--- 2. FILE MODES ---")

modes_file = Path(TEMP_DIR) / "modes.txt"

# Write mode - overwrites
with open(modes_file, 'w') as f:
    f.write("Original content\n")

# Append mode - adds to end
with open(modes_file, 'a') as f:
    f.write("Appended content\n")

# Read and write mode
with open(modes_file, 'r+') as f:
    content = f.read()
    f.write("Added at end\n")
    f.seek(0)  # Go back to start
    new_content = f.read()
    print(f"r+ mode result:\n{new_content}")


# ============================================
# 3. JSON HANDLING
# ============================================
print("\n--- 3. JSON HANDLING ---")

data = {
    "name": "Python",
    "version": 3.12,
    "features": ["easy", "powerful", "flexible"],
    "creator": {"name": "Guido", "country": "Netherlands"},
    "active": True,
    "previous": None
}

json_file = Path(TEMP_DIR) / "data.json"

# Write JSON
with open(json_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"JSON written to: {json_file}")

# Read JSON
with open(json_file, 'r') as f:
    loaded = json.load(f)

print(f"Loaded: {loaded['name']} v{loaded['version']}")
print(f"Features: {loaded['features']}")

# JSON to/from string
json_str = json.dumps(data, indent=2)
print(f"\nJSON string:\n{json_str[:100]}...")

parsed = json.loads(json_str)
print(f"Parsed from string: {parsed['name']}")


# Custom JSON encoder
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        return super().default(obj)


custom_data = {"items": {1, 2, 3}, "data": b"bytes"}
print(f"\nCustom encoder: {json.dumps(custom_data, cls=CustomEncoder)}")


# ============================================
# 4. CSV HANDLING
# ============================================
print("\n--- 4. CSV HANDLING ---")

csv_file = Path(TEMP_DIR) / "users.csv"

# Write CSV
users = [
    {"name": "Alice", "age": 30, "city": "NYC"},
    {"name": "Bob", "age": 25, "city": "LA"},
    {"name": "Charlie", "age": 35, "city": "Chicago"},
]

with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age", "city"])
    writer.writeheader()
    writer.writerows(users)

print(f"CSV written to: {csv_file}")

# Read CSV
with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    print("\nCSV contents:")
    for row in reader:
        print(f"  {row['name']}, {row['age']}, {row['city']}")

# CSV with custom delimiter
tsv_file = Path(TEMP_DIR) / "data.tsv"
with open(tsv_file, 'w', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(["Name", "Score"])
    writer.writerow(["Alice", 95])
    writer.writerow(["Bob", 87])


# ============================================
# 5. PATHLIB
# ============================================
print("\n--- 5. PATHLIB ---")

# Create Path objects
p = Path(TEMP_DIR) / "subdir" / "file.txt"

# Path operations
print(f"path: {p}")
print(f"parent: {p.parent}")
print(f"name: {p.name}")
print(f"stem: {p.stem}")
print(f"suffix: {p.suffix}")
print(f"exists: {p.exists()}")

# Create directories
p.parent.mkdir(parents=True, exist_ok=True)

# Write/read with pathlib
p.write_text("Hello from pathlib!")
content = p.read_text()
print(f"Content: {content}")

# Glob patterns
print("\nFiles in temp dir:")
for file in Path(TEMP_DIR).glob("**/*"):
    if file.is_file():
        print(f"  {file.name}")


# ============================================
# 6. CONTEXT MANAGERS
# ============================================
print("\n--- 6. CONTEXT MANAGERS ---")


# Class-based context manager
class FileManager:
    """Custom context manager for file operations"""
    
    def __init__(self, filename: str, mode: str = 'r'):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        print(f"  Opening {self.filename}")
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print(f"  Closing {self.filename}")
        if self.file:
            self.file.close()
        if exc_type is not None:
            print(f"  Exception occurred: {exc_val}")
        return False  # Don't suppress exceptions


# Using class-based context manager
test_file = Path(TEMP_DIR) / "context_test.txt"
with FileManager(str(test_file), 'w') as f:
    f.write("Test content")


# ============================================
# 7. CUSTOM CONTEXT MANAGER WITH DECORATOR
# ============================================
print("\n--- 7. @CONTEXTMANAGER DECORATOR ---")


@contextmanager
def timer(name: str):
    """Context manager that times a block"""
    import time
    print(f"  Starting {name}")
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"  {name} took {elapsed*1000:.2f}ms")


with timer("file operation"):
    # Simulate work
    import time
    time.sleep(0.1)


@contextmanager
def temporary_file(content: str = "") -> Iterator[Path]:
    """Create a temporary file that's deleted after use"""
    path = Path(tempfile.mktemp(suffix='.txt'))
    try:
        path.write_text(content)
        print(f"  Created temp file: {path.name}")
        yield path
    finally:
        if path.exists():
            path.unlink()
            print(f"  Deleted temp file: {path.name}")


print("\nTemporary file context manager:")
with temporary_file("Hello, temp!") as tmp:
    print(f"  Content: {tmp.read_text()}")
print("  File no longer exists")


# ============================================
# 8. BINARY FILES
# ============================================
print("\n--- 8. BINARY FILES ---")

binary_file = Path(TEMP_DIR) / "data.bin"

# Write binary
data = bytes([0x48, 0x65, 0x6c, 0x6c, 0x6f])  # "Hello"
with open(binary_file, 'wb') as f:
    f.write(data)

# Read binary
with open(binary_file, 'rb') as f:
    content = f.read()
    print(f"Binary: {content}")
    print(f"As string: {content.decode('utf-8')}")


# ============================================
# 9. FILE UTILITIES
# ============================================
print("\n--- 9. FILE UTILITIES ---")

import shutil

# Copy file
src = file_path
dst = Path(TEMP_DIR) / "sample_copy.txt"
shutil.copy(src, dst)
print(f"Copied: {src.name} -> {dst.name}")

# File info
stat = file_path.stat()
print(f"\nFile info for {file_path.name}:")
print(f"  Size: {stat.st_size} bytes")
print(f"  Modified: {stat.st_mtime}")


# ============================================
# 10. CLEANUP
# ============================================
print("\n--- 10. CLEANUP ---")

# Remove temp directory
shutil.rmtree(TEMP_DIR)
print(f"Cleaned up temp directory: {TEMP_DIR}")


print("\n✅ Day 12 completed!")
