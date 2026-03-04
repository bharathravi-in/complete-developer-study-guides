#!/usr/bin/env python3
"""Day 26 - NumPy Fundamentals"""

# Note: Run `pip install numpy` first
# This demo shows concepts without requiring imports

print("=" * 50)
print("NUMPY FUNDAMENTALS")
print("=" * 50)


# ============================================
# 1. ARRAY CREATION
# ============================================
print("\n--- 1. Array Creation ---")

ARRAY_CREATION = """
import numpy as np

# From Python list
arr = np.array([1, 2, 3, 4, 5])

# Special arrays
zeros = np.zeros((3, 4))           # 3x4 zeros
ones = np.ones((2, 3))             # 2x3 ones
empty = np.empty((2, 2))           # Uninitialized
full = np.full((3, 3), 7)          # Filled with 7
eye = np.eye(4)                    # Identity matrix

# Ranges
arange = np.arange(0, 10, 2)       # [0, 2, 4, 6, 8]
linspace = np.linspace(0, 1, 5)    # 5 evenly spaced [0, 1]

# Random
random = np.random.rand(3, 3)      # Uniform [0, 1)
randn = np.random.randn(3, 3)      # Normal distribution
randint = np.random.randint(0, 10, (3, 3))  # Random integers
"""
print(ARRAY_CREATION)


# ============================================
# 2. ARRAY PROPERTIES
# ============================================
print("\n--- 2. Array Properties ---")

ARRAY_PROPERTIES = """
import numpy as np
arr = np.array([[1, 2, 3], [4, 5, 6]])

arr.shape      # (2, 3) - dimensions
arr.ndim       # 2 - number of dimensions
arr.size       # 6 - total elements
arr.dtype      # int64 - data type
arr.itemsize   # 8 - bytes per element
arr.nbytes     # 48 - total bytes

# Reshape
reshaped = arr.reshape(3, 2)   # Change shape
flattened = arr.flatten()      # 1D copy
raveled = arr.ravel()          # 1D view
"""
print(ARRAY_PROPERTIES)


# ============================================
# 3. INDEXING & SLICING
# ============================================
print("\n--- 3. Indexing & Slicing ---")

INDEXING = """
import numpy as np
arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])

# Basic indexing
arr[0]         # First row: [1, 2, 3]
arr[0, 1]      # Element at row 0, col 1: 2
arr[-1]        # Last row: [7, 8, 9]

# Slicing
arr[0:2]       # First 2 rows
arr[:, 1]      # Second column: [2, 5, 8]
arr[1:, :2]    # Rows 1+, first 2 columns
arr[::2]       # Every other row

# Boolean indexing
arr[arr > 5]   # Elements > 5: [6, 7, 8, 9]

# Fancy indexing
arr[[0, 2], [1, 2]]  # Elements at (0,1) and (2,2): [2, 9]
"""
print(INDEXING)


# ============================================
# 4. OPERATIONS
# ============================================
print("\n--- 4. Array Operations ---")

OPERATIONS = """
import numpy as np
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

# Element-wise operations
a + b          # [5, 7, 9]
a - b          # [-3, -3, -3]
a * b          # [4, 10, 18]
a / b          # [0.25, 0.4, 0.5]
a ** 2         # [1, 4, 9]
np.sqrt(a)     # [1, 1.414, 1.732]

# Aggregations
np.sum(a)      # 6
np.mean(a)     # 2.0
np.std(a)      # 0.816
np.min(a)      # 1
np.max(a)      # 3
np.argmax(a)   # 2 (index of max)

# Matrix operations
c = np.array([[1, 2], [3, 4]])
d = np.array([[5, 6], [7, 8]])

np.dot(c, d)       # Matrix multiplication
c @ d              # Same as np.dot
c.T                # Transpose
np.linalg.inv(c)   # Inverse
np.linalg.det(c)   # Determinant
"""
print(OPERATIONS)


# ============================================
# 5. BROADCASTING
# ============================================
print("\n--- 5. Broadcasting ---")

BROADCASTING = """
import numpy as np

# Broadcasting: operations on different-shaped arrays
arr = np.array([[1, 2, 3], [4, 5, 6]])  # Shape: (2, 3)
scalar = 10

arr + scalar    # Add scalar to all elements
# [[11, 12, 13],
#  [14, 15, 16]]

row = np.array([1, 2, 3])  # Shape: (3,)
arr + row       # Add row to each row
# [[2, 4, 6],
#  [5, 7, 9]]

col = np.array([[10], [20]])  # Shape: (2, 1)
arr + col       # Add column to each column
# [[11, 12, 13],
#  [24, 25, 26]]

Broadcasting rules:
1. Arrays with smaller ndim are padded with 1s on left
2. Arrays with size 1 along dimension are stretched
3. Incompatible sizes raise an error
"""
print(BROADCASTING)


# ============================================
# 6. UNIVERSAL FUNCTIONS (ufuncs)
# ============================================
print("\n--- 6. Universal Functions ---")

UFUNCS = """
import numpy as np
arr = np.array([0, np.pi/4, np.pi/2, np.pi])

# Trigonometric
np.sin(arr)
np.cos(arr)
np.tan(arr)

# Exponential & logarithmic
np.exp(arr)         # e^x
np.log(arr)         # Natural log
np.log10(arr)       # Base 10 log

# Comparison
np.greater(a, b)    # a > b element-wise
np.equal(a, b)      # a == b element-wise
np.logical_and(a > 0, b < 5)

# Rounding
np.floor(arr)
np.ceil(arr)
np.round(arr, decimals=2)

# Aggregation along axis
arr2d = np.array([[1, 2, 3], [4, 5, 6]])
np.sum(arr2d, axis=0)   # Sum columns: [5, 7, 9]
np.sum(arr2d, axis=1)   # Sum rows: [6, 15]
"""
print(UFUNCS)


# ============================================
# 7. COMMON USE CASES
# ============================================
print("\n--- 7. Common Use Cases ---")

USE_CASES = """
# 1. Data normalization
data = np.random.rand(100, 10)
normalized = (data - data.mean(axis=0)) / data.std(axis=0)

# 2. One-hot encoding
labels = np.array([0, 1, 2, 1, 0])
num_classes = 3
one_hot = np.eye(num_classes)[labels]
# [[1, 0, 0],
#  [0, 1, 0],
#  [0, 0, 1],
#  [0, 1, 0],
#  [1, 0, 0]]

# 3. Cosine similarity
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# 4. Batch matrix operations
# Shape: (batch_size, m, n) @ (batch_size, n, p) -> (batch_size, m, p)
batch1 = np.random.rand(32, 10, 20)
batch2 = np.random.rand(32, 20, 5)
result = batch1 @ batch2  # Shape: (32, 10, 5)

# 5. Image manipulation (treating as array)
# image shape: (height, width, channels)
# grayscale = image.mean(axis=2)
# flipped = image[::-1, :, :]
"""
print(USE_CASES)


# ============================================
# DEMONSTRATION WITH ACTUAL CODE
# ============================================
print("\n" + "=" * 50)
print("LIVE DEMONSTRATION")
print("=" * 50)

try:
    import numpy as np
    
    # Create sample data
    print("\n--- Creating Arrays ---")
    arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    print(f"Array:\n{arr}")
    print(f"Shape: {arr.shape}, Dtype: {arr.dtype}")
    
    # Operations
    print("\n--- Operations ---")
    print(f"Sum: {np.sum(arr)}")
    print(f"Mean: {np.mean(arr):.2f}")
    print(f"Max: {np.max(arr)} at index {np.argmax(arr)}")
    print(f"Sum per column: {np.sum(arr, axis=0)}")
    print(f"Sum per row: {np.sum(arr, axis=1)}")
    
    # Transformation
    print("\n--- Transformations ---")
    print(f"Transposed:\n{arr.T}")
    print(f"Flattened: {arr.flatten()}")
    
    # Boolean operations
    print("\n--- Boolean Indexing ---")
    print(f"Elements > 5: {arr[arr > 5]}")
    
    # Random
    print("\n--- Random ---")
    random_arr = np.random.rand(3, 3)
    print(f"Random 3x3:\n{random_arr.round(2)}")

except ImportError:
    print("\nNumPy not installed. Run: pip install numpy")
    print("The concepts above are still valid!")
