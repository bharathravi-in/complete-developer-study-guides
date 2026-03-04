# Day 12 - File Handling

## Topics Covered
- Reading & writing files
- JSON handling
- CSV handling
- Context managers (`with`)
- Custom context managers

## File Modes
| Mode | Description |
|------|-------------|
| 'r' | Read (default) |
| 'w' | Write (overwrites) |
| 'a' | Append |
| 'x' | Exclusive create |
| 'b' | Binary mode |
| '+' | Read and write |

## Best Practices
```python
# Always use context manager
with open('file.txt', 'r') as f:
    content = f.read()
# File automatically closed

# Specify encoding
with open('file.txt', 'r', encoding='utf-8') as f:
    pass
```

## Run
```bash
python practice.py
```
