# 📚 DSA 30-Day Tutorial - Day 27

## Day 27: Math & Number Theory

### 🎯 Learning Objectives
By the end of this day, you will:
- Master GCD, LCM, prime checking
- Understand modular arithmetic
- Solve common math problems

---

### 📖 GCD (Greatest Common Divisor)

```javascript
function gcd(a, b) {
    while (b !== 0) {
        [a, b] = [b, a % b];
    }
    return a;
}

// LCM using GCD
function lcm(a, b) {
    return (a * b) / gcd(a, b);
}

// GCD of array
function gcdArray(arr) {
    return arr.reduce((acc, num) => gcd(acc, num));
}
```

---

### 📖 Prime Numbers

```javascript
// Check if prime - O(√n)
function isPrime(n) {
    if (n < 2) return false;
    if (n === 2) return true;
    if (n % 2 === 0) return false;
    
    for (let i = 3; i * i <= n; i += 2) {
        if (n % i === 0) return false;
    }
    return true;
}

// Sieve of Eratosthenes - O(n log log n)
function sieve(n) {
    const isPrime = new Array(n + 1).fill(true);
    isPrime[0] = isPrime[1] = false;
    
    for (let i = 2; i * i <= n; i++) {
        if (isPrime[i]) {
            for (let j = i * i; j <= n; j += i) {
                isPrime[j] = false;
            }
        }
    }
    
    return isPrime.map((v, i) => v ? i : -1).filter(v => v > 0);
}
```

---

### 📖 Modular Arithmetic

For large numbers in competitive programming:

```javascript
const MOD = 1e9 + 7;

// (a + b) mod m
const modAdd = (a, b) => ((a % MOD) + (b % MOD)) % MOD;

// (a * b) mod m
const modMul = (a, b) => ((a % MOD) * (b % MOD)) % MOD;

// Fast exponentiation: a^b mod m - O(log b)
function modPow(base, exp, mod = MOD) {
    let result = 1n;
    base = BigInt(base) % BigInt(mod);
    exp = BigInt(exp);
    
    while (exp > 0n) {
        if (exp % 2n === 1n) {
            result = (result * base) % BigInt(mod);
        }
        base = (base * base) % BigInt(mod);
        exp = exp / 2n;
    }
    
    return Number(result);
}
```

---

### 📖 Factorial and Combinations

```javascript
// Factorial with memoization
function factorial(n, memo = {}) {
    if (n <= 1) return 1n;
    if (memo[n]) return memo[n];
    memo[n] = BigInt(n) * factorial(n - 1, memo);
    return memo[n];
}

// nCr = n! / (r! * (n-r)!)
function combinations(n, r) {
    if (r > n) return 0n;
    return factorial(n) / (factorial(r) * factorial(n - r));
}

// Pascal's Triangle for nCr
function pascalTriangle(n) {
    const dp = Array.from({ length: n + 1 }, () => new Array(n + 1).fill(0n));
    
    for (let i = 0; i <= n; i++) {
        dp[i][0] = 1n;
        for (let j = 1; j <= i; j++) {
            dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j];
        }
    }
    
    return dp;
}
```

---

### 📖 Power of Two/Three

```javascript
// Power of 2: Only one bit set
function isPowerOfTwo(n) {
    return n > 0 && (n & (n - 1)) === 0;
}

// Power of 3: No simple bit trick
function isPowerOfThree(n) {
    if (n <= 0) return false;
    
    // Largest power of 3 that fits in 32-bit int: 3^19 = 1162261467
    return 1162261467 % n === 0;
}
```

---

### ✅ Day 27 Checklist
- [ ] Implement GCD/LCM
- [ ] Generate primes with Sieve
- [ ] Complete: Count Primes, Power of Two
- [ ] Practice: Happy Number, Ugly Number

---

