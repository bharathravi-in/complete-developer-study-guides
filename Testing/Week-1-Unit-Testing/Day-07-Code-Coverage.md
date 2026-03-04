# Day 7: Code Coverage Strategies & Best Practices

## 📚 Topics to Cover (3-4 hours)

---

## 1. Types of Code Coverage

| Type | What It Measures | Example |
|------|-----------------|---------|
| **Line Coverage** | % of lines executed | Each line at least once |
| **Branch Coverage** | % of branches taken | Both if/else paths |
| **Function Coverage** | % of functions called | Each function at least once |
| **Statement Coverage** | % of statements executed | Similar to line but more granular |
| **Condition Coverage** | Each boolean sub-expression | `(a && b)` → test a=T,b=F etc. |
| **Path Coverage** | All possible execution paths | Exponential, rarely achievable |

### Branch Coverage Example

```javascript
function getDiscount(user) {
  if (user.isPremium) {       // Branch 1
    if (user.age > 60) {      // Branch 2
      return 0.3;
    }
    return 0.2;
  }
  return 0;
}

// 100% Line coverage but NOT 100% branch:
test('premium user', () => {
  expect(getDiscount({ isPremium: true, age: 65 })).toBe(0.3);
});
test('non-premium user', () => {
  expect(getDiscount({ isPremium: false })).toBe(0);
});

// Missing branch: premium user under 60
test('premium user under 60', () => {
  expect(getDiscount({ isPremium: true, age: 30 })).toBe(0.2);
});
// Now 100% branch coverage ✅
```

---

## 2. Coverage Tools Setup

### Jest (JavaScript/TypeScript)

```json
// package.json
{
  "jest": {
    "collectCoverage": true,
    "coverageDirectory": "coverage",
    "collectCoverageFrom": [
      "src/**/*.{ts,tsx}",
      "!src/**/*.d.ts",
      "!src/**/*.test.ts",
      "!src/**/index.ts",
      "!src/**/__mocks__/**"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      },
      "src/services/": {
        "branches": 90,
        "functions": 90,
        "lines": 90
      }
    },
    "coverageReporters": ["text", "lcov", "html", "json-summary"]
  }
}
```

```bash
# Generate coverage
jest --coverage

# View HTML report
open coverage/lcov-report/index.html
```

### Pytest (Python)

```bash
pip install pytest-cov

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# With branch coverage
pytest --cov=src --cov-branch
```

### Angular (Karma + Istanbul)

```bash
ng test --code-coverage
# Opens coverage/index.html
```

---

## 3. Coverage Best Practices

### The 80% Rule

```
┌──────────────────────────────────────────────┐
│  80% coverage = Good baseline                 │
│  90%+ coverage = Excellent for critical code  │
│  100% coverage ≠ Bug-free code               │
└──────────────────────────────────────────────┘
```

### What to Cover (Priority Order)

1. **Critical business logic** — Payment, auth, data processing
2. **Edge cases** — Null, undefined, empty, boundary values
3. **Error handling** — Exception paths, error messages
4. **Public API surface** — All exported functions/methods
5. **Complex conditionals** — Nested if/else, switch statements

### What NOT to Cover

```javascript
// Don't waste time testing:
// 1. Framework-generated code
// 2. Simple getters/setters
// 3. Configuration files
// 4. Type definitions
// 5. Third-party library internals

// Exclude from coverage:
/* istanbul ignore next */
if (process.env.DEBUG) {
  console.log('debug info');
}
```

---

## 4. Coverage in CI/CD

### GitHub Actions Coverage Gate

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm test -- --coverage --ci
      - name: Check coverage threshold
        run: |
          COVERAGE=$(cat coverage/coverage-summary.json | jq '.total.lines.pct')
          if (( $(echo "$COVERAGE < 80" | bc -l) )); then
            echo "Coverage ${COVERAGE}% is below 80% threshold"
            exit 1
          fi
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info
```

### Coverage Badge

```markdown
<!-- In README.md -->
[![codecov](https://codecov.io/gh/user/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/user/repo)
```

---

## 5. Mutation Testing

Mutation testing verifies that your tests actually catch bugs by introducing small changes (mutations) to your code and checking if tests fail.

### Stryker (JavaScript/TypeScript)

```bash
npm install --save-dev @stryker-mutator/core @stryker-mutator/jest-runner

# stryker.conf.json
{
  "mutate": ["src/**/*.ts", "!src/**/*.test.ts"],
  "testRunner": "jest",
  "reporters": ["html", "clear-text", "progress"],
  "coverageAnalysis": "perTest"
}

npx stryker run
```

### Mutation Types

```javascript
// Original
function isAdult(age) {
  return age >= 18;
}

// Mutations Stryker creates:
return age > 18;     // Boundary mutation
return age <= 18;    // Negation mutation
return age >= 19;    // Increment mutation
return true;         // Constant mutation
return false;        // Constant mutation
// If your tests still pass with any mutation → TEST IS WEAK
```

---

## 6. Coverage Anti-Patterns

### ❌ Writing tests just for coverage

```javascript
// BAD - Tests implementation, not behavior
it('should call the function', () => {
  const spy = jest.spyOn(service, 'process');
  service.process();
  expect(spy).toHaveBeenCalled(); // Meaningless!
});

// GOOD - Tests behavior
it('should return processed result', () => {
  const result = service.process({ data: [1, 2, 3] });
  expect(result).toEqual({ sum: 6, count: 3, average: 2 });
});
```

### ❌ Chasing 100% coverage

```javascript
// Don't test trivial code just for coverage numbers
class User {
  constructor(public name: string, public email: string) {}
  
  // Testing this getter adds coverage but zero value
  getName() { return this.name; }
}
```

---

## 🎯 Interview Questions

### Q1: Is 100% code coverage a good goal?
**A:** No. 100% coverage doesn't mean bug-free code. It can lead to brittle, low-value tests. Aim for 80%+ overall, 90%+ for critical paths. Focus on meaningful tests that verify behavior, not just execute lines.

### Q2: What is mutation testing?
**A:** Mutation testing modifies your source code (mutations) and checks if tests detect the changes. If a test passes with mutated code, the test is weak. It measures test quality, not just coverage quantity. Tools: Stryker (JS), mutmut (Python).

### Q3: How do you improve coverage without writing meaningless tests?
**A:** Focus on untested business scenarios, not uncovered lines. Write tests for edge cases, error paths, and boundary conditions. Use parametrized tests for multiple inputs. Review coverage reports to find critical untested branches.

---

## 📝 Practice Exercises

1. Set up Jest coverage for a Node.js project with 80% threshold
2. Find and fix coverage gaps using the HTML report
3. Run Stryker mutation testing and fix surviving mutations
4. Configure coverage gates in a GitHub Actions workflow
