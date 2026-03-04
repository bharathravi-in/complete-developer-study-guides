#!/usr/bin/env python3
"""
Prime Number Checker - Multiple Implementations

Features:
- Check if a number is prime
- Find all primes in a range
- Prime factorization
"""

import math
import time
from typing import Generator


def is_prime_basic(n: int) -> bool:
    """Basic O(n) implementation"""
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True


def is_prime_sqrt(n: int) -> bool:
    """Optimized O(√n) implementation"""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def is_prime_6k(n: int) -> bool:
    """
    Optimized using 6k±1 optimization
    All primes > 3 are of form 6k±1
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def sieve_of_eratosthenes(limit: int) -> list[int]:
    """
    Find all primes up to limit using Sieve of Eratosthenes
    Time: O(n log log n), Space: O(n)
    """
    if limit < 2:
        return []
    
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(math.sqrt(limit)) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    
    return [i for i in range(limit + 1) if is_prime[i]]


def prime_generator() -> Generator[int, None, None]:
    """Infinite prime number generator"""
    yield 2
    primes = [2]
    candidate = 3
    
    while True:
        is_prime = True
        sqrt_candidate = math.sqrt(candidate)
        
        for p in primes:
            if p > sqrt_candidate:
                break
            if candidate % p == 0:
                is_prime = False
                break
        
        if is_prime:
            primes.append(candidate)
            yield candidate
        
        candidate += 2


def prime_factors(n: int) -> list[int]:
    """Return prime factorization of n"""
    factors = []
    d = 2
    
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    
    if n > 1:
        factors.append(n)
    
    return factors


def benchmark_prime_functions():
    """Compare performance of different implementations"""
    test_number = 1_000_003  # Large prime
    iterations = 100
    
    functions = [
        ("Basic O(n)", is_prime_basic),
        ("Sqrt O(√n)", is_prime_sqrt),
        ("6k±1 Optimized", is_prime_6k),
    ]
    
    print("\n" + "=" * 50)
    print(f"BENCHMARK: Testing {test_number} ({iterations} iterations)")
    print("=" * 50)
    
    for name, func in functions:
        start = time.perf_counter()
        for _ in range(iterations):
            result = func(test_number)
        elapsed = time.perf_counter() - start
        print(f"{name:20}: {elapsed*1000:.2f}ms (result: {result})")


def main():
    print("=" * 50)
    print("PRIME NUMBER CHECKER")
    print("=" * 50)
    
    # Test basic functionality
    print("\n--- Testing Prime Check ---")
    test_numbers = [1, 2, 3, 4, 17, 18, 97, 100, 101]
    
    for n in test_numbers:
        result = is_prime_6k(n)
        print(f"  {n:3} is prime: {result}")
    
    # Sieve of Eratosthenes
    print("\n--- Primes up to 100 (Sieve) ---")
    primes_100 = sieve_of_eratosthenes(100)
    print(f"  Count: {len(primes_100)}")
    print(f"  Primes: {primes_100}")
    
    # Prime generator
    print("\n--- First 20 primes (Generator) ---")
    gen = prime_generator()
    first_20 = [next(gen) for _ in range(20)]
    print(f"  {first_20}")
    
    # Prime factorization
    print("\n--- Prime Factorization ---")
    test_factorize = [12, 60, 100, 1001, 2024]
    for n in test_factorize:
        factors = prime_factors(n)
        print(f"  {n} = {' × '.join(map(str, factors))}")
    
    # Benchmark
    benchmark_prime_functions()
    
    # Interactive mode
    print("\n" + "=" * 50)
    print("INTERACTIVE MODE (Enter 'quit' to exit)")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\nEnter a number to check: ")
            if user_input.lower() in ('quit', 'q', 'exit'):
                break
            
            n = int(user_input)
            
            if is_prime_6k(n):
                print(f"✅ {n} is PRIME!")
            else:
                factors = prime_factors(n)
                print(f"❌ {n} is NOT prime")
                print(f"   Factors: {' × '.join(map(str, factors))}")
                
        except ValueError:
            print("Please enter a valid integer")
        except KeyboardInterrupt:
            break
    
    print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
