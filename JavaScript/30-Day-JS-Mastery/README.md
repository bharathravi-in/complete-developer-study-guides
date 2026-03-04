# 🚀 30-Day JavaScript Mastery Plan

[← Back to Main](../../README.md)

A comprehensive JavaScript study plan for senior-level interview preparation.

---

## 📚 Course Structure

### Week 1: Core Foundations
| Day | Topic | File |
|-----|-------|------|
| 1 | JS Engine & Runtime | [Day-01-JS-Engine-Runtime.md](Week-1-Core-Foundations/Day-01-JS-Engine-Runtime.md) |
| 2 | Variables & Scope | [Day-02-Variables-Scope.md](Week-1-Core-Foundations/Day-02-Variables-Scope.md) |
| 3 | Data Types & Memory | [Day-03-Data-Types-Memory.md](Week-1-Core-Foundations/Day-03-Data-Types-Memory.md) |
| 4 | Type Coercion & Equality | [Day-04-Type-Coercion.md](Week-1-Core-Foundations/Day-04-Type-Coercion.md) |
| 5 | Functions Core | [Day-05-Functions-Core.md](Week-1-Core-Foundations/Day-05-Functions-Core.md) |
| 6 | this Keyword | [Day-06-this-Keyword.md](Week-1-Core-Foundations/Day-06-this-Keyword.md) |
| 7 | Closures | [Day-07-Closures.md](Week-1-Core-Foundations/Day-07-Closures.md) |

### Week 2: Intermediate Topics
| Day | Topic | File |
|-----|-------|------|
| 8 | Prototypes & Inheritance | [Day-08-Prototypes.md](Week-2-Intermediate/Day-08-Prototypes.md) |
| 9 | Objects Deep Dive | [Day-09-Objects.md](Week-2-Intermediate/Day-09-Objects.md) |
| 10 | Arrays Deep Dive | [Day-10-Arrays.md](Week-2-Intermediate/Day-10-Arrays.md) |
| 11 | Event Loop | [Day-11-Event-Loop.md](Week-2-Intermediate/Day-11-Event-Loop.md) |
| 12 | Async JavaScript | [Day-12-Async-JavaScript.md](Week-2-Intermediate/Day-12-Async-JavaScript.md) |
| 13 | Modules | [Day-13-Modules.md](Week-2-Intermediate/Day-13-Modules.md) |
| 14 | Error Handling | [Day-14-Error-Handling.md](Week-2-Intermediate/Day-14-Error-Handling.md) |

### Week 3: Advanced Topics
| Day | Topic | File |
|-----|-------|------|
| 15 | Currying & Composition | [Day-15-Currying-Composition.md](Week-3-Advanced/Day-15-Currying-Composition.md) |
| 16 | Debounce & Throttle | [Day-16-Debounce-Throttle.md](Week-3-Advanced/Day-16-Debounce-Throttle.md) |
| 17 | DOM & Events | [Day-17-DOM-Events.md](Week-3-Advanced/Day-17-DOM-Events.md) |
| 18 | Design Patterns | [Day-18-Design-Patterns.md](Week-3-Advanced/Day-18-Design-Patterns.md) |
| 19 | Memory Management | [Day-19-Memory-GC.md](Week-3-Advanced/Day-19-Memory-GC.md) |
| 20 | Proxy, Reflect, Generators | [Day-20-Proxy-Reflect-Generators.md](Week-3-Advanced/Day-20-Proxy-Reflect-Generators.md) |
| 21 | Functional Programming | [Day-21-Functional-Programming.md](Week-3-Advanced/Day-21-Functional-Programming.md) |

### Week 4: Interview Preparation
| Day | Topic | File |
|-----|-------|------|
| 22 | Polyfills & Implementations | [Day-22-Polyfills.md](Week-4-Interview-Prep/Day-22-Polyfills.md) |
| 23 | Output Prediction | [Day-23-Output-Prediction.md](Week-4-Interview-Prep/Day-23-Output-Prediction.md) |
| 24 | System Design | [Day-24-System-Design.md](Week-4-Interview-Prep/Day-24-System-Design.md) |
| 25 | Node.js Internals | [Day-25-NodeJS-Internals.md](Week-4-Interview-Prep/Day-25-NodeJS-Internals.md) |
| 26 | Security | [Day-26-Security.md](Week-4-Interview-Prep/Day-26-Security.md) |
| 27 | Testing | [Day-27-Testing.md](Week-4-Interview-Prep/Day-27-Testing.md) |
| 28 | Mini Project | [Day-28-Mini-Project.md](Week-4-Interview-Prep/Day-28-Mini-Project.md) |
| 29 | Mock Interview | [Day-29-Mock-Interview.md](Week-4-Interview-Prep/Day-29-Mock-Interview.md) |
| 30 | Final Revision | [Day-30-Final-Revision.md](Week-4-Interview-Prep/Day-30-Final-Revision.md) |

### Bonus Materials
| Resource | Description | File |
|----------|-------------|------|
| 200+ Q&A | Comprehensive interview questions | [JavaScript-QA-200.md](Interview-Questions/JavaScript-QA-200.md) |
| 50 Output Questions | Tricky output prediction practice | [Output-Prediction-50.md](Interview-Questions/Output-Prediction-50.md) |

---

## 📋 How to Use This Course

### Daily Study Routine (2-3 hours)
1. **Read** the day's material (45 min)
2. **Code** the examples yourself (45 min)
3. **Practice** the exercises (30 min)
4. **Review** with the interview questions (30 min)

### Study Tips
- Don't just read - **TYPE** the code yourself
- **Explain concepts** out loud (teaches you deeply)
- **Take notes** in your own words
- **Build something** that uses what you learned
- **Review** previous days regularly

---

## 🎯 Key Topics by Priority

### Must Know (Every Interview)
- Variables & Scope (var/let/const, hoisting, TDZ)
- this keyword (rules, binding, arrow functions)
- Closures (definition, use cases, loops)
- Prototypes & Inheritance
- Promises & async/await
- Event Loop (microtasks vs macrotasks)

### Frequently Asked
- Type coercion (== vs ===)
- Higher-order functions (map, filter, reduce)
- ES6+ features (destructuring, spread, modules)
- Error handling patterns
- DOM manipulation & events

### Senior Level
- System design (components, state management)
- Performance optimization
- Memory management
- Design patterns
- Security considerations
- Testing strategies

---

## 🔧 Common Implementations to Memorize

```javascript
// 1. debounce
const debounce = (fn, delay) => {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
};

// 2. throttle
const throttle = (fn, limit) => {
    let inThrottle;
    return (...args) => {
        if (!inThrottle) {
            fn(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
};

// 3. bind
Function.prototype.myBind = function(context, ...args) {
    const fn = this;
    return function(...newArgs) {
        return fn.apply(context, [...args, ...newArgs]);
    };
};

// 4. Promise.all
const promiseAll = (promises) => new Promise((resolve, reject) => {
    const results = [];
    let completed = 0;
    promises.forEach((p, i) => {
        Promise.resolve(p).then(val => {
            results[i] = val;
            if (++completed === promises.length) resolve(results);
        }).catch(reject);
    });
    if (!promises.length) resolve([]);
});

// 5. deep clone
const deepClone = (obj, seen = new WeakMap()) => {
    if (obj === null || typeof obj !== 'object') return obj;
    if (seen.has(obj)) return seen.get(obj);
    const clone = Array.isArray(obj) ? [] : {};
    seen.set(obj, clone);
    for (const key in obj) {
        if (obj.hasOwnProperty(key)) {
            clone[key] = deepClone(obj[key], seen);
        }
    }
    return clone;
};
```

---

## ✅ Interview Checklist

### Before the Interview
- [ ] Review all 30 days of notes
- [ ] Practice output prediction questions
- [ ] Implement common functions from memory
- [ ] Review system design patterns
- [ ] Prepare questions for interviewer

### During the Interview
- [ ] Think out loud
- [ ] Ask clarifying questions
- [ ] Start with brute force, then optimize
- [ ] Test code with examples
- [ ] Discuss time/space complexity

### Key Phrases
- "Let me think about the edge cases..."
- "The time complexity would be O(n) because..."
- "I could optimize this by..."
- "In a real application, I would also consider..."

---

## 📅 30-Day Schedule

| Week | Focus | Days |
|------|-------|------|
| 1 | Core JS Fundamentals | Engine, Variables, Types, Functions, this, Closures |
| 2 | Intermediate Concepts | Prototypes, Objects, Arrays, Event Loop, Async, Modules |
| 3 | Advanced Topics | Patterns, Performance, Proxy, FP, DOM |
| 4 | Interview Prep | Polyfills, Output, Design, Node, Security, Testing, Practice |

---

## 🎉 What's Next?

After completing this course:
1. **Build a project** using advanced concepts
2. **Contribute to open source** JavaScript projects
3. **Practice** LeetCode/HackerRank problems
4. **Mock interviews** with peers
5. **Stay updated** with TC39 proposals

---

Good luck with your JavaScript journey! 🚀

*Created for senior-level JavaScript interview preparation*
