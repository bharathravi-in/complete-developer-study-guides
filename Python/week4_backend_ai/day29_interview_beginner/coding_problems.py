#!/usr/bin/env python3
"""Day 29 - Common Coding Problems (Beginner Level)"""

print("=" * 60)
print("CODING PROBLEMS - BEGINNER")
print("=" * 60)


# ============================================
# PROBLEM 1: FizzBuzz
# ============================================
print("\n" + "-" * 60)
print("Problem 1: FizzBuzz")
print("-" * 60)
print("""
Print 1-100:
- Divisible by 3: "Fizz"
- Divisible by 5: "Buzz"
- Divisible by both: "FizzBuzz"
""")

def fizzbuzz(n):
    for i in range(1, n + 1):
        if i % 3 == 0 and i % 5 == 0:
            print("FizzBuzz", end=" ")
        elif i % 3 == 0:
            print("Fizz", end=" ")
        elif i % 5 == 0:
            print("Buzz", end=" ")
        else:
            print(i, end=" ")
    print()

print("Output (1-20):")
fizzbuzz(20)


# ============================================
# PROBLEM 2: Reverse a String
# ============================================
print("\n" + "-" * 60)
print("Problem 2: Reverse a String")
print("-" * 60)

def reverse_string(s):
    """Multiple ways to reverse."""
    # Method 1: Slicing (Pythonic)
    return s[::-1]
    
    # Method 2: reversed()
    # return ''.join(reversed(s))
    
    # Method 3: Loop
    # result = ''
    # for char in s:
    #     result = char + result
    # return result

print(f"reverse_string('Python') = '{reverse_string('Python')}'")


# ============================================
# PROBLEM 3: Check Palindrome
# ============================================
print("\n" + "-" * 60)
print("Problem 3: Check Palindrome")
print("-" * 60)

def is_palindrome(s):
    """Check if string is palindrome (ignoring case/spaces)."""
    s = s.lower().replace(" ", "")
    return s == s[::-1]

print(f"is_palindrome('racecar') = {is_palindrome('racecar')}")
print(f"is_palindrome('A man a plan a canal Panama') = {is_palindrome('A man a plan a canal Panama')}")
print(f"is_palindrome('hello') = {is_palindrome('hello')}")


# ============================================
# PROBLEM 4: Find Maximum/Minimum
# ============================================
print("\n" + "-" * 60)
print("Problem 4: Find Max/Min without built-ins")
print("-" * 60)

def find_max(lst):
    """Find maximum without max()."""
    if not lst:
        return None
    maximum = lst[0]
    for num in lst[1:]:
        if num > maximum:
            maximum = num
    return maximum

nums = [3, 1, 4, 1, 5, 9, 2, 6]
print(f"find_max({nums}) = {find_max(nums)}")


# ============================================
# PROBLEM 5: Factorial
# ============================================
print("\n" + "-" * 60)
print("Problem 5: Factorial")
print("-" * 60)

def factorial_iterative(n):
    """Iterative factorial."""
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result

def factorial_recursive(n):
    """Recursive factorial."""
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)

print(f"factorial_iterative(5) = {factorial_iterative(5)}")
print(f"factorial_recursive(5) = {factorial_recursive(5)}")


# ============================================
# PROBLEM 6: Fibonacci
# ============================================
print("\n" + "-" * 60)
print("Problem 6: Fibonacci Sequence")
print("-" * 60)

def fibonacci(n):
    """Return first n Fibonacci numbers."""
    if n <= 0:
        return []
    if n == 1:
        return [0]
    
    fib = [0, 1]
    while len(fib) < n:
        fib.append(fib[-1] + fib[-2])
    return fib

print(f"fibonacci(10) = {fibonacci(10)}")


# ============================================
# PROBLEM 7: Two Sum
# ============================================
print("\n" + "-" * 60)
print("Problem 7: Two Sum")
print("-" * 60)
print("Find indices of two numbers that add up to target")

def two_sum(nums, target):
    """O(n) solution using hash map."""
    seen = {}  # value -> index
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []

nums = [2, 7, 11, 15]
target = 9
print(f"nums={nums}, target={target}")
print(f"two_sum result: {two_sum(nums, target)}")


# ============================================
# PROBLEM 8: Count Character Frequency
# ============================================
print("\n" + "-" * 60)
print("Problem 8: Character Frequency")
print("-" * 60)

def char_frequency(s):
    """Count frequency of each character."""
    freq = {}
    for char in s:
        freq[char] = freq.get(char, 0) + 1
    return freq

# Using collections.Counter is more Pythonic
from collections import Counter
print(f"char_frequency('hello') = {char_frequency('hello')}")
print(f"Counter('hello') = {dict(Counter('hello'))}")


# ============================================
# PROBLEM 9: Remove Duplicates
# ============================================
print("\n" + "-" * 60)
print("Problem 9: Remove Duplicates (Preserve Order)")
print("-" * 60)

def remove_duplicates(lst):
    """Remove duplicates while preserving order."""
    seen = set()
    result = []
    for item in lst:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

nums = [1, 2, 2, 3, 4, 3, 5]
print(f"remove_duplicates({nums}) = {remove_duplicates(nums)}")


# ============================================
# PROBLEM 10: Check Anagram
# ============================================
print("\n" + "-" * 60)
print("Problem 10: Check Anagram")
print("-" * 60)

def is_anagram(s1, s2):
    """Check if two strings are anagrams."""
    # Remove spaces and lowercase
    s1 = s1.replace(" ", "").lower()
    s2 = s2.replace(" ", "").lower()
    
    # Method 1: Sort and compare
    return sorted(s1) == sorted(s2)
    
    # Method 2: Counter
    # return Counter(s1) == Counter(s2)

print(f"is_anagram('listen', 'silent') = {is_anagram('listen', 'silent')}")
print(f"is_anagram('hello', 'world') = {is_anagram('hello', 'world')}")


# ============================================
# PROBLEM 11: Find Missing Number
# ============================================
print("\n" + "-" * 60)
print("Problem 11: Find Missing Number")
print("-" * 60)
print("Array contains n-1 numbers from 1 to n, find missing")

def find_missing(nums, n):
    """Find missing number using math."""
    expected_sum = n * (n + 1) // 2
    actual_sum = sum(nums)
    return expected_sum - actual_sum

nums = [1, 2, 4, 5, 6]  # Missing 3
print(f"nums={nums}, n=6")
print(f"find_missing result: {find_missing(nums, 6)}")


# ============================================
# PROBLEM 12: Prime Number Check
# ============================================
print("\n" + "-" * 60)
print("Problem 12: Check Prime Number")
print("-" * 60)

def is_prime(n):
    """Check if n is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

for num in [2, 3, 4, 17, 18, 97]:
    print(f"is_prime({num}) = {is_prime(num)}")


# ============================================
# PROBLEM 13: Merge Two Sorted Lists
# ============================================
print("\n" + "-" * 60)
print("Problem 13: Merge Two Sorted Lists")
print("-" * 60)

def merge_sorted(lst1, lst2):
    """Merge two sorted lists into one sorted list."""
    result = []
    i = j = 0
    
    while i < len(lst1) and j < len(lst2):
        if lst1[i] <= lst2[j]:
            result.append(lst1[i])
            i += 1
        else:
            result.append(lst2[j])
            j += 1
    
    # Add remaining elements
    result.extend(lst1[i:])
    result.extend(lst2[j:])
    return result

a = [1, 3, 5, 7]
b = [2, 4, 6, 8]
print(f"merge_sorted({a}, {b}) = {merge_sorted(a, b)}")


# ============================================
# PROBLEM 14: Valid Parentheses
# ============================================
print("\n" + "-" * 60)
print("Problem 14: Valid Parentheses")
print("-" * 60)

def is_valid_parentheses(s):
    """Check if parentheses are balanced."""
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:  # Closing bracket
            if not stack or stack[-1] != mapping[char]:
                return False
            stack.pop()
        else:  # Opening bracket
            stack.append(char)
    
    return len(stack) == 0

print(f"is_valid_parentheses('()[]{{}}') = {is_valid_parentheses('()[]{}')}")
print(f"is_valid_parentheses('([)]') = {is_valid_parentheses('([)]')}")
print(f"is_valid_parentheses('{{[]}}') = {is_valid_parentheses('{[]}')}")


# ============================================
# PROBLEM 15: Rotate Array
# ============================================
print("\n" + "-" * 60)
print("Problem 15: Rotate Array")
print("-" * 60)

def rotate_array(nums, k):
    """Rotate array to the right by k steps."""
    k = k % len(nums)  # Handle k > len(nums)
    return nums[-k:] + nums[:-k]

nums = [1, 2, 3, 4, 5]
k = 2
print(f"rotate_array({nums}, {k}) = {rotate_array(nums, k)}")


# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 60)
print("PRACTICE TIPS")
print("=" * 60)
print("""
1. Always clarify the problem first
2. Think about edge cases (empty, single element, etc.)
3. Start with brute force, then optimize
4. Know time/space complexity of your solution
5. Test with examples before coding
6. Practice these patterns:
   - Two pointers
   - Hash maps for O(1) lookup
   - Sliding window
   - Stack for matching pairs
""")
