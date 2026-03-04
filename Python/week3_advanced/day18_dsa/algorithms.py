#!/usr/bin/env python3
"""Day 19 - Algorithms Implementation"""

from typing import List, Optional, TypeVar, Callable
import time
import random

T = TypeVar('T')

print("=" * 50)
print("ALGORITHMS")
print("=" * 50)


# ============================================
# 1. BINARY SEARCH
# ============================================
print("\n--- 1. BINARY SEARCH ---")


def binary_search(arr: List[T], target: T) -> int:
    """
    Binary search for sorted array.
    Time: O(log n), Space: O(1)
    Returns index or -1 if not found.
    """
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1


def binary_search_recursive(arr: List[T], target: T, left: int = 0, right: int = None) -> int:
    """Recursive binary search."""
    if right is None:
        right = len(arr) - 1
    
    if left > right:
        return -1
    
    mid = (left + right) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        return binary_search_recursive(arr, target, left, mid - 1)


# Test
arr = list(range(0, 100, 2))  # Even numbers 0-98
print(f"Array: [0, 2, 4, ..., 98]")
print(f"binary_search(50): index {binary_search(arr, 50)}")
print(f"binary_search(51): index {binary_search(arr, 51)}")


# ============================================
# 2. MERGE SORT
# ============================================
print("\n--- 2. MERGE SORT ---")


def merge_sort(arr: List[T]) -> List[T]:
    """
    Merge sort - divide and conquer.
    Time: O(n log n), Space: O(n)
    Stable sort.
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)


def merge(left: List[T], right: List[T]) -> List[T]:
    """Merge two sorted arrays."""
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result


# Test
arr = [38, 27, 43, 3, 9, 82, 10]
print(f"Original: {arr}")
print(f"Merge sorted: {merge_sort(arr)}")


# ============================================
# 3. QUICK SORT
# ============================================
print("\n--- 3. QUICK SORT ---")


def quick_sort(arr: List[T]) -> List[T]:
    """
    Quick sort - divide and conquer.
    Time: O(n log n) avg, O(n²) worst
    Space: O(log n)
    Not stable.
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)


def quick_sort_inplace(arr: List[T], low: int = 0, high: int = None) -> None:
    """In-place quick sort."""
    if high is None:
        high = len(arr) - 1
    
    if low < high:
        pivot_idx = partition(arr, low, high)
        quick_sort_inplace(arr, low, pivot_idx - 1)
        quick_sort_inplace(arr, pivot_idx + 1, high)


def partition(arr: List[T], low: int, high: int) -> int:
    """Partition array around pivot."""
    pivot = arr[high]
    i = low - 1
    
    for j in range(low, high):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


# Test
arr = [64, 34, 25, 12, 22, 11, 90]
print(f"Original: {arr}")
print(f"Quick sorted: {quick_sort(arr)}")


# ============================================
# 4. ADDITIONAL SEARCHES
# ============================================
print("\n--- 4. SEARCH ALGORITHMS ---")


def linear_search(arr: List[T], target: T) -> int:
    """Linear search: O(n)"""
    for i, val in enumerate(arr):
        if val == target:
            return i
    return -1


def interpolation_search(arr: List[int], target: int) -> int:
    """
    Interpolation search for uniformly distributed data.
    Time: O(log log n) avg, O(n) worst
    """
    low, high = 0, len(arr) - 1
    
    while low <= high and arr[low] <= target <= arr[high]:
        if low == high:
            if arr[low] == target:
                return low
            return -1
        
        # Estimate position
        pos = low + ((target - arr[low]) * (high - low) // (arr[high] - arr[low]))
        
        if arr[pos] == target:
            return pos
        elif arr[pos] < target:
            low = pos + 1
        else:
            high = pos - 1
    
    return -1


# Test
arr = list(range(0, 1000, 10))  # 0, 10, 20, ..., 990
print(f"interpolation_search(500): {interpolation_search(arr, 500)}")


# ============================================
# 5. SORTING COMPARISONS
# ============================================
print("\n--- 5. SORTING COMPARISONS ---")


def bubble_sort(arr: List[T]) -> List[T]:
    """Bubble sort: O(n²)"""
    arr = arr.copy()
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:
            break
    return arr


def insertion_sort(arr: List[T]) -> List[T]:
    """Insertion sort: O(n²)"""
    arr = arr.copy()
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr


def selection_sort(arr: List[T]) -> List[T]:
    """Selection sort: O(n²)"""
    arr = arr.copy()
    for i in range(len(arr)):
        min_idx = i
        for j in range(i + 1, len(arr)):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr


# Benchmark
def benchmark_sort(sort_func: Callable, arr: List[int], name: str) -> float:
    start = time.perf_counter()
    sort_func(arr)
    elapsed = time.perf_counter() - start
    return elapsed


sizes = [100, 500, 1000]
print(f"\n{'Algorithm':<20} | " + " | ".join(f"n={s}" for s in sizes))
print("-" * 60)

for name, func in [
    ("Bubble Sort", bubble_sort),
    ("Insertion Sort", insertion_sort),
    ("Selection Sort", selection_sort),
    ("Merge Sort", merge_sort),
    ("Quick Sort", quick_sort),
    ("Python sorted()", sorted),
]:
    times = []
    for size in sizes:
        arr = [random.randint(0, 1000) for _ in range(size)]
        elapsed = benchmark_sort(func, arr, name)
        times.append(f"{elapsed*1000:.2f}ms")
    print(f"{name:<20} | " + " | ".join(f"{t:>8}" for t in times))


# ============================================
# 6. COMPLEXITY REFERENCE
# ============================================
print("\n--- 6. COMPLEXITY REFERENCE ---")

print("""
╔═══════════════════════════════════════════════════════════════╗
║                    TIME COMPLEXITY                             ║
╠══════════════════╦════════════════════════════════════════════╣
║ Algorithm        ║ Best      │ Average   │ Worst    │ Space   ║
╠══════════════════╬═══════════╪═══════════╪══════════╪═════════╣
║ Binary Search    ║ O(1)      │ O(log n)  │ O(log n) │ O(1)    ║
║ Linear Search    ║ O(1)      │ O(n)      │ O(n)     │ O(1)    ║
╠══════════════════╬═══════════╪═══════════╪══════════╪═════════╣
║ Bubble Sort      ║ O(n)      │ O(n²)     │ O(n²)    │ O(1)    ║
║ Insertion Sort   ║ O(n)      │ O(n²)     │ O(n²)    │ O(1)    ║
║ Selection Sort   ║ O(n²)     │ O(n²)     │ O(n²)    │ O(1)    ║
║ Merge Sort       ║ O(n log n)│ O(n log n)│O(n log n)│ O(n)    ║
║ Quick Sort       ║ O(n log n)│ O(n log n)│ O(n²)    │O(log n) ║
║ Heap Sort        ║ O(n log n)│ O(n log n)│O(n log n)│ O(1)    ║
║ Tim Sort         ║ O(n)      │ O(n log n)│O(n log n)│ O(n)    ║
╠══════════════════╬═══════════╧═══════════╧══════════╧═════════╣
║ Data Structure   ║     Access │ Search │ Insert │ Delete      ║
╠══════════════════╬════════════╪════════╪════════╪═════════════╣
║ Array            ║     O(1)   │ O(n)   │ O(n)   │ O(n)        ║
║ Linked List      ║     O(n)   │ O(n)   │ O(1)   │ O(1)        ║
║ Hash Table       ║     N/A    │ O(1)   │ O(1)   │ O(1)        ║
║ BST (balanced)   ║  O(log n)  │O(log n)│O(log n)│ O(log n)    ║
║ Heap             ║     N/A    │ O(n)   │O(log n)│ O(log n)    ║
╚══════════════════╩════════════╧════════╧════════╧═════════════╝
""")


print("\n✅ Algorithms completed!")
