#!/usr/bin/env python3
"""
FizzBuzz - Classic Programming Challenge

Rules:
- Print numbers 1 to 100
- If divisible by 3, print "Fizz"
- If divisible by 5, print "Buzz"
- If divisible by both, print "FizzBuzz"
"""


def fizzbuzz_classic(n: int) -> str:
    """Classic if-else implementation"""
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:
        return str(n)


def fizzbuzz_concat(n: int) -> str:
    """String concatenation approach"""
    result = ""
    if n % 3 == 0:
        result += "Fizz"
    if n % 5 == 0:
        result += "Buzz"
    return result or str(n)


def fizzbuzz_dict(n: int) -> str:
    """Dictionary-based approach (extensible)"""
    rules = {3: "Fizz", 5: "Buzz"}
    result = "".join(word for divisor, word in rules.items() if n % divisor == 0)
    return result or str(n)


def fizzbuzz_match(n: int) -> str:
    """Match-case approach (Python 3.10+)"""
    match (n % 3, n % 5):
        case (0, 0):
            return "FizzBuzz"
        case (0, _):
            return "Fizz"
        case (_, 0):
            return "Buzz"
        case _:
            return str(n)


def fizzbuzz_oneliner(n: int) -> str:
    """One-liner (not recommended for production)"""
    return "FizzBuzz" if n % 15 == 0 else "Fizz" if n % 3 == 0 else "Buzz" if n % 5 == 0 else str(n)


def main():
    print("=" * 50)
    print("FIZZBUZZ IMPLEMENTATIONS")
    print("=" * 50)
    
    # Test all implementations
    implementations = [
        ("Classic", fizzbuzz_classic),
        ("Concat", fizzbuzz_concat),
        ("Dict", fizzbuzz_dict),
        ("Match", fizzbuzz_match),
        ("Oneliner", fizzbuzz_oneliner),
    ]
    
    # Verify all produce same output
    print("\nVerifying implementations (1-20):")
    for i in range(1, 21):
        results = [impl(i) for _, impl in implementations]
        if len(set(results)) == 1:
            print(f"{i:2}: {results[0]}")
        else:
            print(f"{i:2}: MISMATCH! {results}")
    
    # Full FizzBuzz output
    print("\n" + "=" * 50)
    print("FULL FIZZBUZZ (1-100)")
    print("=" * 50)
    
    output = [fizzbuzz_classic(i) for i in range(1, 101)]
    
    # Print in rows of 10
    for i in range(0, 100, 10):
        row = output[i:i+10]
        print(" ".join(f"{x:8}" for x in row))


if __name__ == "__main__":
    main()
