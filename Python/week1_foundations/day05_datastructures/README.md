# Day 5 - Data Structures in Python

## Topics Covered
- List operations
- Dict methods
- Set operations
- Tuple unpacking
- Comprehensions (List, Dict, Set)

## Key Operations

### List Methods
```python
lst.append(x)      # Add to end
lst.extend(iter)   # Add multiple
lst.insert(i, x)   # Insert at index
lst.pop()          # Remove & return last
lst.remove(x)      # Remove first occurrence
lst.sort()         # Sort in place
lst.reverse()      # Reverse in place
```

### Dict Methods
```python
d.get(key, default)     # Safe access
d.keys(), d.values()    # Views
d.items()               # Key-value pairs
d.update(other_dict)    # Merge
d.setdefault(key, val)  # Get or set
d.pop(key)              # Remove & return
```

### Set Operations
```python
a | b   # Union
a & b   # Intersection
a - b   # Difference
a ^ b   # Symmetric difference
```

## Practice Task
Build a Word Frequency Counter that:
1. Reads text input
2. Counts word occurrences
3. Shows top N words
4. Ignores common stop words

## Run
```bash
python practice.py
python word_frequency.py
```
