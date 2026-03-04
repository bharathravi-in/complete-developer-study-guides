# Day 29: Mock Interview Practice

## 🎯 Learning Objectives
- Practice common interview question formats
- Master problem-solving approach
- Learn to communicate effectively
- Handle coding under pressure
- Review key concepts quickly

---

## 📋 Interview Format Overview

```
╔════════════════════════════════════════════════════════════════════╗
║              TYPICAL JS INTERVIEW STRUCTURE                         ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  ROUND 1: Technical Screening (30-45 min)                          ║
║  • JavaScript fundamentals                                          ║
║  • Output prediction questions                                      ║
║  • Quick coding problems                                            ║
║                                                                     ║
║  ROUND 2: Coding Interview (45-60 min)                             ║
║  • Algorithm/Data structure problems                                ║
║  • Live coding with explanation                                     ║
║  • Optimization discussion                                          ║
║                                                                     ║
║  ROUND 3: System Design (45-60 min)                                ║
║  • Frontend architecture                                            ║
║  • Component design                                                 ║
║  • State management                                                 ║
║                                                                     ║
║  ROUND 4: Behavioral + Tech Deep Dive                              ║
║  • Past experience                                                  ║
║  • In-depth JS concepts                                             ║
║  • Debugging scenarios                                              ║
║                                                                     ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## 🎯 Round 1: Technical Screening Questions

### Question 1: Explain Event Loop
**Expected Answer:**
```javascript
/*
The event loop is JS's mechanism for handling async operations:

1. Call Stack - Executes synchronous code
2. Web APIs - Handle async operations (setTimeout, fetch)
3. Callback/Task Queue - Stores callbacks from Web APIs
4. Microtask Queue - Stores Promise callbacks (higher priority)
5. Event Loop - Moves callbacks to stack when empty

Order: Call Stack → Microtasks → Macrotasks
*/

console.log('1');
setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => console.log('3'));
console.log('4');
// Output: 1, 4, 3, 2
```

### Question 2: Implement Debounce
```javascript
function debounce(fn, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
}

// Follow-up: Add immediate execution option
function debounce(fn, delay, immediate = false) {
    let timeoutId;
    return function(...args) {
        const callNow = immediate && !timeoutId;
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            timeoutId = null;
            if (!immediate) fn.apply(this, args);
        }, delay);
        if (callNow) fn.apply(this, args);
    };
}
```

### Question 3: What's the difference between == and ===?
```javascript
/*
== (Loose Equality): Performs type coercion before comparison
=== (Strict Equality): No type coercion, checks value AND type
*/

console.log(1 == '1');   // true (coerces string to number)
console.log(1 === '1');  // false (different types)

console.log(null == undefined);   // true (special case)
console.log(null === undefined);  // false

console.log([] == false);   // true ([] → '' → 0, false → 0)
console.log([] === false);  // false

// Best Practice: Always use === unless you specifically need coercion
```

### Question 4: Closures - What will this output?
```javascript
for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100);
}
// Output: 3, 3, 3 (var is function-scoped)

// Fix 1: Use let
for (let i = 0; i < 3; i++) {
    setTimeout(() => console.log(i), 100);
}
// Output: 0, 1, 2

// Fix 2: IIFE
for (var i = 0; i < 3; i++) {
    ((j) => {
        setTimeout(() => console.log(j), 100);
    })(i);
}
// Output: 0, 1, 2
```

### Question 5: Implement Promise.all
```javascript
function promiseAll(promises) {
    return new Promise((resolve, reject) => {
        if (!Array.isArray(promises)) {
            return reject(new TypeError('Argument must be an array'));
        }
        
        const results = [];
        let completed = 0;
        
        if (promises.length === 0) {
            return resolve([]);
        }
        
        promises.forEach((promise, index) => {
            Promise.resolve(promise)
                .then(value => {
                    results[index] = value;
                    completed++;
                    if (completed === promises.length) {
                        resolve(results);
                    }
                })
                .catch(reject);
        });
    });
}
```

---

## 🖥️ Round 2: Coding Challenges

### Challenge 1: Flatten Array
```javascript
// Question: Implement a function to flatten nested arrays

// Solution 1: Recursive
function flatten(arr) {
    return arr.reduce((acc, item) => {
        return acc.concat(Array.isArray(item) ? flatten(item) : item);
    }, []);
}

// Solution 2: Iterative
function flattenIterative(arr) {
    const result = [];
    const stack = [...arr];
    
    while (stack.length) {
        const item = stack.pop();
        if (Array.isArray(item)) {
            stack.push(...item);
        } else {
            result.unshift(item);
        }
    }
    
    return result;
}

// Solution 3: Generator
function* flattenGen(arr) {
    for (const item of arr) {
        if (Array.isArray(item)) {
            yield* flattenGen(item);
        } else {
            yield item;
        }
    }
}

// Solution 4: Built-in (mention this too!)
[1, [2, [3, 4]]].flat(Infinity);

// Test
flatten([1, [2, [3, [4, 5]]]]); // [1, 2, 3, 4, 5]
```

### Challenge 2: Deep Clone
```javascript
// Question: Implement a deep clone function

function deepClone(obj, seen = new WeakMap()) {
    // Handle primitives and null
    if (obj === null || typeof obj !== 'object') {
        return obj;
    }
    
    // Handle circular references
    if (seen.has(obj)) {
        return seen.get(obj);
    }
    
    // Handle Date
    if (obj instanceof Date) {
        return new Date(obj.getTime());
    }
    
    // Handle RegExp
    if (obj instanceof RegExp) {
        return new RegExp(obj.source, obj.flags);
    }
    
    // Handle Array
    if (Array.isArray(obj)) {
        const clone = [];
        seen.set(obj, clone);
        obj.forEach((item, i) => {
            clone[i] = deepClone(item, seen);
        });
        return clone;
    }
    
    // Handle Object
    const clone = Object.create(Object.getPrototypeOf(obj));
    seen.set(obj, clone);
    
    for (const key of Reflect.ownKeys(obj)) {
        const descriptor = Object.getOwnPropertyDescriptor(obj, key);
        if (descriptor.value !== undefined) {
            descriptor.value = deepClone(descriptor.value, seen);
        }
        Object.defineProperty(clone, key, descriptor);
    }
    
    return clone;
}
```

### Challenge 3: LRU Cache
```javascript
// Question: Implement an LRU (Least Recently Used) Cache

class LRUCache {
    constructor(capacity) {
        this.capacity = capacity;
        this.cache = new Map();
    }

    get(key) {
        if (!this.cache.has(key)) {
            return -1;
        }
        
        // Move to end (most recently used)
        const value = this.cache.get(key);
        this.cache.delete(key);
        this.cache.set(key, value);
        return value;
    }

    put(key, value) {
        // If exists, delete first (to update order)
        if (this.cache.has(key)) {
            this.cache.delete(key);
        }
        
        // Add new entry
        this.cache.set(key, value);
        
        // Evict oldest if over capacity
        if (this.cache.size > this.capacity) {
            // Map.keys() returns iterator, first item is oldest
            const oldestKey = this.cache.keys().next().value;
            this.cache.delete(oldestKey);
        }
    }
}

// Test
const cache = new LRUCache(2);
cache.put(1, 'one');
cache.put(2, 'two');
cache.get(1);        // Returns 'one', moves 1 to most recent
cache.put(3, 'three'); // Evicts key 2
cache.get(2);        // Returns -1 (not found)
```

### Challenge 4: Rate Limiter
```javascript
// Question: Implement a function rate limiter

function createRateLimiter(fn, limit, interval) {
    const queue = [];
    let count = 0;
    
    // Reset count periodically
    setInterval(() => {
        count = 0;
        processQueue();
    }, interval);
    
    function processQueue() {
        while (queue.length > 0 && count < limit) {
            const { args, resolve, reject } = queue.shift();
            count++;
            try {
                const result = fn(...args);
                resolve(result);
            } catch (error) {
                reject(error);
            }
        }
    }
    
    return function(...args) {
        return new Promise((resolve, reject) => {
            if (count < limit) {
                count++;
                try {
                    resolve(fn(...args));
                } catch (error) {
                    reject(error);
                }
            } else {
                queue.push({ args, resolve, reject });
            }
        });
    };
}
```

### Challenge 5: Event Emitter
```javascript
// Question: Implement a simple EventEmitter class

class EventEmitter {
    constructor() {
        this.events = {};
    }

    on(event, listener) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(listener);
        return () => this.off(event, listener);
    }

    off(event, listener) {
        if (!this.events[event]) return;
        this.events[event] = this.events[event].filter(l => l !== listener);
    }

    emit(event, ...args) {
        if (!this.events[event]) return;
        this.events[event].forEach(listener => listener(...args));
    }

    once(event, listener) {
        const wrapper = (...args) => {
            listener(...args);
            this.off(event, wrapper);
        };
        this.on(event, wrapper);
    }
}
```

---

## 🏗️ Round 3: System Design

### Design: Autocomplete Component

**Step 1: Requirements**
- Search as user types
- Debounce API calls
- Cache results
- Handle loading/error states
- Keyboard navigation
- Accessible

**Step 2: Architecture**
```javascript
class Autocomplete {
    constructor(options) {
        this.input = options.input;
        this.fetchSuggestions = options.fetchSuggestions;
        this.cache = new Map();
        this.debounceMs = options.debounceMs || 300;
        this.minChars = options.minChars || 2;
        this.maxSuggestions = options.maxSuggestions || 10;
        
        this.selectedIndex = -1;
        this.suggestions = [];
        
        this.init();
    }

    init() {
        this.createDropdown();
        this.bindEvents();
    }

    createDropdown() {
        this.dropdown = document.createElement('ul');
        this.dropdown.className = 'autocomplete-dropdown';
        this.dropdown.setAttribute('role', 'listbox');
        this.input.parentNode.appendChild(this.dropdown);
    }

    bindEvents() {
        this.input.addEventListener('input', this.debounce(
            this.handleInput.bind(this),
            this.debounceMs
        ));
        
        this.input.addEventListener('keydown', this.handleKeydown.bind(this));
        this.dropdown.addEventListener('click', this.handleSelect.bind(this));
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
                this.hide();
            }
        });
    }

    debounce(fn, delay) {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => fn(...args), delay);
        };
    }

    async handleInput() {
        const query = this.input.value.trim();
        
        if (query.length < this.minChars) {
            this.hide();
            return;
        }
        
        // Check cache
        if (this.cache.has(query)) {
            this.render(this.cache.get(query));
            return;
        }
        
        // Fetch suggestions
        try {
            this.showLoading();
            const suggestions = await this.fetchSuggestions(query);
            this.cache.set(query, suggestions);
            this.render(suggestions);
        } catch (error) {
            this.showError(error);
        }
    }

    handleKeydown(e) {
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.navigate(1);
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.navigate(-1);
                break;
            case 'Enter':
                e.preventDefault();
                this.selectCurrent();
                break;
            case 'Escape':
                this.hide();
                break;
        }
    }

    navigate(direction) {
        const items = this.dropdown.querySelectorAll('li');
        if (!items.length) return;
        
        this.selectedIndex = Math.max(
            0,
            Math.min(this.selectedIndex + direction, items.length - 1)
        );
        
        items.forEach((item, i) => {
            item.classList.toggle('selected', i === this.selectedIndex);
        });
    }

    selectCurrent() {
        if (this.selectedIndex >= 0 && this.suggestions[this.selectedIndex]) {
            this.select(this.suggestions[this.selectedIndex]);
        }
    }

    handleSelect(e) {
        const item = e.target.closest('li');
        if (item) {
            const index = parseInt(item.dataset.index);
            this.select(this.suggestions[index]);
        }
    }

    select(suggestion) {
        this.input.value = suggestion.label;
        this.hide();
        this.input.dispatchEvent(new CustomEvent('autocomplete', {
            detail: suggestion
        }));
    }

    render(suggestions) {
        this.suggestions = suggestions.slice(0, this.maxSuggestions);
        this.selectedIndex = -1;
        
        this.dropdown.innerHTML = this.suggestions
            .map((s, i) => `
                <li role="option" data-index="${i}">${this.highlight(s.label)}</li>
            `)
            .join('');
        
        this.show();
    }

    highlight(text) {
        const query = this.input.value;
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    showLoading() {
        this.dropdown.innerHTML = '<li class="loading">Loading...</li>';
        this.show();
    }

    showError(error) {
        this.dropdown.innerHTML = '<li class="error">Error loading suggestions</li>';
        this.show();
    }

    show() {
        this.dropdown.classList.add('visible');
    }

    hide() {
        this.dropdown.classList.remove('visible');
        this.selectedIndex = -1;
    }
}
```

---

## 💬 Round 4: Behavioral Questions

### Common Questions

**Q1: Tell me about a challenging JavaScript bug you fixed.**
```
STRUCTURE: STAR Method
- Situation: Describe the context
- Task: What needed to be done
- Action: What you did
- Result: Outcome and learnings

EXAMPLE:
"In our team's dashboard, users reported intermittent data inconsistencies.
After investigation, I discovered a race condition where multiple async
API calls were updating shared state. I implemented a mutex pattern
with a request queue that serialized conflicting operations. This
eliminated the bug and improved reliability from 95% to 99.9%."
```

**Q2: How do you stay updated with JavaScript?**
```
- Follow TC39 proposals
- Read MDN, JavaScript Weekly
- Experiment with new features
- Contribute to open source
- Attend conferences/meetups
```

**Q3: Describe a time you disagreed with a technical decision.**
```
- Acknowledge different perspectives
- Focus on facts, not emotions
- Explain your reasoning process
- Show you can compromise or accept decisions
- Emphasize team collaboration
```

---

## ✅ Interview Tips

```
╔════════════════════════════════════════════════════════════════════╗
║                    INTERVIEW SUCCESS TIPS                           ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  BEFORE:                                                            ║
║  □ Review fundamentals (this, closures, promises)                   ║
║  □ Practice coding problems out loud                                ║
║  □ Prepare questions for interviewer                                ║
║  □ Test your setup (camera, mic, IDE)                               ║
║                                                                     ║
║  DURING:                                                            ║
║  □ Think out loud - explain your approach                           ║
║  □ Ask clarifying questions first                                   ║
║  □ Start with brute force, then optimize                            ║
║  □ Test your code with examples                                     ║
║  □ Handle edge cases                                                ║
║  □ Discuss time/space complexity                                    ║
║                                                                     ║
║  IF STUCK:                                                          ║
║  □ Break down the problem                                           ║
║  □ Think about simpler versions                                     ║
║  □ Ask for hints (it's okay!)                                       ║
║  □ Walk through an example manually                                 ║
║                                                                     ║
║  COMMUNICATION:                                                     ║
║  □ Be concise but thorough                                          ║
║  □ Admit when you don't know something                              ║
║  □ Show enthusiasm and curiosity                                    ║
║  □ Ask about trade-offs                                             ║
║                                                                     ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## 📝 Mock Interview Scenarios

### Scenario 1: Output Prediction (5 min)
```javascript
// What's the output?
const arr = [1, 2, 3];
arr[10] = 11;
console.log(arr.length);
console.log(arr.filter(x => x === undefined).length);

// Answer: 11, 0 (sparse array, filter skips empty slots)
```

### Scenario 2: Debug This (10 min)
```javascript
// Bug: "this" is undefined in callback
class Counter {
    constructor() {
        this.count = 0;
    }
    
    increment() {
        ['a', 'b', 'c'].forEach(function(item) {
            this.count++; // Error!
        });
    }
}

// Fix 1: Arrow function
['a', 'b', 'c'].forEach((item) => {
    this.count++;
});

// Fix 2: Bind
['a', 'b', 'c'].forEach(function(item) {
    this.count++;
}.bind(this));

// Fix 3: thisArg
['a', 'b', 'c'].forEach(function(item) {
    this.count++;
}, this);
```

### Scenario 3: Implement (15 min)
```javascript
// Implement a retry function with exponential backoff
async function retry(fn, maxRetries = 3, baseDelay = 1000) {
    let lastError;
    
    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error;
            const delay = baseDelay * Math.pow(2, attempt);
            await new Promise(resolve => setTimeout(resolve, delay));
        }
    }
    
    throw lastError;
}
```

---

## ✅ Day 29 Checklist

- [ ] Review all core concepts
- [ ] Practice output prediction questions
- [ ] Solve coding challenges with explanation
- [ ] Practice system design questions
- [ ] Prepare behavioral answers
- [ ] Do a timed mock interview
- [ ] Review and improve weak areas
