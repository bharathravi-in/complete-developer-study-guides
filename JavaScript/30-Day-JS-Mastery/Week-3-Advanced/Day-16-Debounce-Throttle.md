# Day 16: Debounce & Throttle

## 🎯 Learning Objectives
- Understand debounce vs throttle
- Implement both from scratch
- Learn practical use cases
- Master advanced variations

---

## ⏰ Understanding the Problem

```javascript
/*
When user types in a search box:

Without optimization:
t=0ms:   keypress 'h'  → API call
t=50ms:  keypress 'e'  → API call
t=100ms: keypress 'l'  → API call
t=150ms: keypress 'l'  → API call
t=200ms: keypress 'o'  → API call
= 5 API calls for "hello"

With DEBOUNCE (wait 300ms):
t=0ms:   keypress 'h'  → schedule call
t=50ms:  keypress 'e'  → cancel previous, reschedule
t=100ms: keypress 'l'  → cancel previous, reschedule
t=150ms: keypress 'l'  → cancel previous, reschedule
t=200ms: keypress 'o'  → cancel previous, reschedule
t=500ms: no more input → API call with "hello"
= 1 API call

With THROTTLE (max 1 call per 200ms):
t=0ms:   keypress 'h'  → API call ✓
t=50ms:  keypress 'e'  → ignored (within cooldown)
t=100ms: keypress 'l'  → ignored
t=150ms: keypress 'l'  → ignored
t=200ms: keypress 'o'  → API call ✓
= 2 API calls
*/
```

---

## 🔄 Debounce

Debounce delays function execution until after a period of inactivity.

```javascript
// Basic debounce
function debounce(func, wait) {
    let timeoutId;
    
    return function(...args) {
        clearTimeout(timeoutId);
        
        timeoutId = setTimeout(() => {
            func.apply(this, args);
        }, wait);
    };
}

// Usage
const searchAPI = (query) => console.log(`Searching: ${query}`);
const debouncedSearch = debounce(searchAPI, 300);

// In React/DOM
input.addEventListener('input', e => {
    debouncedSearch(e.target.value);
});

/*
VISUALIZATION:

Input:  h     e     l     l     o     (300ms passes)
        ↓     ↓     ↓     ↓     ↓          ↓
Timer:  |--X  |--X  |--X  |--X  |----------|
                                           ↓
                                        EXECUTE
                                     "hello" searched
*/
```

### Debounce with Leading/Trailing Options

```javascript
function debounce(func, wait, options = {}) {
    let timeoutId;
    let lastArgs;
    let lastThis;
    let result;
    let lastCallTime;
    
    const leading = options.leading ?? false;
    const trailing = options.trailing ?? true;
    
    function invokeFunc() {
        const args = lastArgs;
        const thisArg = lastThis;
        
        lastArgs = lastThis = undefined;
        result = func.apply(thisArg, args);
        return result;
    }
    
    function startTimer(wait) {
        return setTimeout(timerExpired, wait);
    }
    
    function timerExpired() {
        const time = Date.now();
        const timeSinceLastCall = time - lastCallTime;
        
        if (timeSinceLastCall < wait) {
            timeoutId = startTimer(wait - timeSinceLastCall);
        } else {
            timeoutId = undefined;
            if (trailing && lastArgs) {
                return invokeFunc();
            }
            lastArgs = lastThis = undefined;
        }
    }
    
    function debounced(...args) {
        const time = Date.now();
        const isInvoking = shouldInvoke(time);
        
        lastArgs = args;
        lastThis = this;
        lastCallTime = time;
        
        if (isInvoking) {
            if (!timeoutId) {
                // Start the timer for trailing edge
                timeoutId = startTimer(wait);
                // Invoke immediately if leading
                if (leading) {
                    return invokeFunc();
                }
            }
        }
        
        return result;
    }
    
    function shouldInvoke(time) {
        return lastCallTime === undefined || 
               (time - lastCallTime >= wait);
    }
    
    debounced.cancel = function() {
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        lastArgs = lastThis = lastCallTime = timeoutId = undefined;
    };
    
    debounced.flush = function() {
        if (timeoutId) {
            return invokeFunc();
        }
        return result;
    };
    
    return debounced;
}

// Usage examples
const debouncedSave = debounce(save, 1000);
const debouncedSaveLeading = debounce(save, 1000, { leading: true });
const debouncedSaveBoth = debounce(save, 1000, { leading: true, trailing: true });

// Cancel pending execution
debouncedSave.cancel();

// Execute immediately
debouncedSave.flush();
```

### Practical Debounce Examples

```javascript
// 1. Search input
const searchInput = document.getElementById('search');
const debouncedSearch = debounce(async (query) => {
    const results = await fetch(`/api/search?q=${query}`);
    displayResults(await results.json());
}, 300);

searchInput.addEventListener('input', e => {
    debouncedSearch(e.target.value);
});

// 2. Window resize
const debouncedResize = debounce(() => {
    console.log('Window resized to:', window.innerWidth, window.innerHeight);
    recalculateLayout();
}, 250);

window.addEventListener('resize', debouncedResize);

// 3. Auto-save form
const form = document.getElementById('form');
const debouncedAutoSave = debounce((data) => {
    localStorage.setItem('formDraft', JSON.stringify(data));
    showSavedIndicator();
}, 1000);

form.addEventListener('input', e => {
    const formData = new FormData(form);
    debouncedAutoSave(Object.fromEntries(formData));
});

// 4. React hook
function useDebounce(value, delay) {
    const [debouncedValue, setDebouncedValue] = useState(value);
    
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedValue(value);
        }, delay);
        
        return () => clearTimeout(timer);
    }, [value, delay]);
    
    return debouncedValue;
}

// Usage in component
function Search() {
    const [query, setQuery] = useState('');
    const debouncedQuery = useDebounce(query, 300);
    
    useEffect(() => {
        if (debouncedQuery) {
            searchAPI(debouncedQuery);
        }
    }, [debouncedQuery]);
    
    return <input onChange={e => setQuery(e.target.value)} />;
}
```

---

## 🚦 Throttle

Throttle ensures a function is called at most once in a specified time period.

```javascript
// Basic throttle
function throttle(func, wait) {
    let lastTime = 0;
    
    return function(...args) {
        const now = Date.now();
        
        if (now - lastTime >= wait) {
            lastTime = now;
            return func.apply(this, args);
        }
    };
}

// Usage
const handleScroll = () => console.log('Scrolled at:', Date.now());
const throttledScroll = throttle(handleScroll, 200);

window.addEventListener('scroll', throttledScroll);

/*
VISUALIZATION:

Scroll events:  x x x x x x x x x x x x x x x x
                ↓                 ↓
Execute:        ✓ (t=0)          ✓ (t=200)      ✓ (t=400ms)
                |-------200ms-----|-------200ms-----|

Only executes first event in each 200ms window
*/
```

### Throttle with Trailing Option

```javascript
function throttle(func, wait, options = {}) {
    let lastTime = 0;
    let timeoutId = null;
    let lastArgs = null;
    let lastThis = null;
    
    const leading = options.leading ?? true;
    const trailing = options.trailing ?? true;
    
    function invokeFunc() {
        func.apply(lastThis, lastArgs);
        lastArgs = lastThis = null;
    }
    
    function throttled(...args) {
        const now = Date.now();
        const remaining = wait - (now - lastTime);
        
        lastArgs = args;
        lastThis = this;
        
        if (remaining <= 0 || remaining > wait) {
            if (timeoutId) {
                clearTimeout(timeoutId);
                timeoutId = null;
            }
            
            lastTime = now;
            if (leading) {
                invokeFunc();
            }
        } else if (!timeoutId && trailing) {
            timeoutId = setTimeout(() => {
                lastTime = Date.now();
                timeoutId = null;
                invokeFunc();
            }, remaining);
        }
    }
    
    throttled.cancel = function() {
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        lastTime = 0;
        timeoutId = lastArgs = lastThis = null;
    };
    
    return throttled;
}

// Usage
const throttledScroll = throttle(onScroll, 200);
const throttledScrollNoLeading = throttle(onScroll, 200, { leading: false });
const throttledScrollNoTrailing = throttle(onScroll, 200, { trailing: false });
```

### Practical Throttle Examples

```javascript
// 1. Scroll event handling
const throttledScrollHandler = throttle(() => {
    const scrollY = window.scrollY;
    
    // Update progress bar
    const progress = (scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
    progressBar.style.width = `${progress}%`;
    
    // Lazy load images
    lazyLoadImages();
    
    // Update sticky header state
    header.classList.toggle('sticky', scrollY > 100);
}, 100);

window.addEventListener('scroll', throttledScrollHandler);

// 2. Mouse move for drawing
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

const throttledDraw = throttle((x, y) => {
    ctx.lineTo(x, y);
    ctx.stroke();
}, 16); // ~60fps

canvas.addEventListener('mousemove', e => {
    throttledDraw(e.offsetX, e.offsetY);
});

// 3. Button click (prevent double-click)
const throttledSubmit = throttle(async () => {
    await submitForm();
    showSuccess();
}, 2000);

submitButton.addEventListener('click', throttledSubmit);

// 4. Game loop / Animation
const throttledUpdate = throttle(() => {
    updateGameState();
    render();
}, 16); // 60 FPS cap

function gameLoop() {
    throttledUpdate();
    requestAnimationFrame(gameLoop);
}

// 5. API rate limiting
const throttledAPICall = throttle(async (data) => {
    const response = await fetch('/api/track', {
        method: 'POST',
        body: JSON.stringify(data)
    });
    return response.json();
}, 1000); // Max 1 call per second

// 6. Infinite scroll
const throttledLoadMore = throttle(() => {
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
    
    if (scrollTop + clientHeight >= scrollHeight - 100) {
        loadMoreItems();
    }
}, 500);

window.addEventListener('scroll', throttledLoadMore);
```

---

## ⚖️ Debounce vs Throttle Comparison

```javascript
/*
╔══════════════════════════════════════════════════════════════════════╗
║                    DEBOUNCE vs THROTTLE                               ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                       ║
║  DEBOUNCE:                         THROTTLE:                          ║
║  "Wait until activity stops"       "Limit rate of execution"          ║
║                                                                       ║
║  Events: x x x x x                 Events: x x x x x                  ║
║          └─────┘                           ↓   ↓   ↓                  ║
║              ↓                             ✓   ✓   ✓                  ║
║          (one call after pause)     (one call per interval)           ║
║                                                                       ║
║  USE WHEN:                         USE WHEN:                          ║
║  • Search input                    • Scroll handlers                  ║
║  • Auto-save                       • Resize handlers                  ║
║  • Form validation                 • Mouse move tracking              ║
║  • Window resize                   • Rate limiting                    ║
║  • API suggestions                 • Game loops                       ║
║                                                                       ║
║  GUARANTEES:                       GUARANTEES:                        ║
║  • Final value processed           • Regular interval calls           ║
║  • Min delay between calls         • Max call frequency               ║
║                                                                       ║
╚══════════════════════════════════════════════════════════════════════╝
*/

// Same events, different behavior

const events = ['a', 'b', 'c', 'd', 'e'];
const wait = 100;

// Debounce: Only 'e' is processed (after 100ms of no activity)
// Throttle: 'a' is processed immediately, then one every 100ms
```

---

## 🔧 RequestAnimationFrame Throttle

```javascript
// Throttle to animation frame (smooth 60fps)
function throttleRAF(func) {
    let rafId = null;
    
    return function(...args) {
        if (rafId) return;
        
        rafId = requestAnimationFrame(() => {
            func.apply(this, args);
            rafId = null;
        });
    };
}

// Usage - smoother than time-based throttle
const smoothScroll = throttleRAF(() => {
    updateScrollPosition();
});

window.addEventListener('scroll', smoothScroll);

// Throttle with cancelation
function throttleRAFWithCancel(func) {
    let rafId = null;
    
    function throttled(...args) {
        if (rafId) return;
        
        rafId = requestAnimationFrame(() => {
            func.apply(this, args);
            rafId = null;
        });
    }
    
    throttled.cancel = () => {
        if (rafId) {
            cancelAnimationFrame(rafId);
            rafId = null;
        }
    };
    
    return throttled;
}
```

---

## 🎯 Interview Implementation

```javascript
// DEBOUNCE - Write from scratch
function debounce(fn, delay) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => fn.apply(this, args), delay);
    };
}

// THROTTLE - Write from scratch
function throttle(fn, limit) {
    let inThrottle = false;
    return function(...args) {
        if (!inThrottle) {
            fn.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// THROTTLE with trailing call
function throttleWithTrailing(fn, limit) {
    let lastArgs = null;
    let inThrottle = false;
    
    return function(...args) {
        if (!inThrottle) {
            fn.apply(this, args);
            inThrottle = true;
            
            setTimeout(() => {
                inThrottle = false;
                if (lastArgs) {
                    fn.apply(this, lastArgs);
                    lastArgs = null;
                }
            }, limit);
        } else {
            lastArgs = args;
        }
    };
}

// Test
function log(x) {
    console.log(x, Date.now());
}

const debouncedLog = debounce(log, 200);
const throttledLog = throttle(log, 200);

// Simulate rapid calls
for (let i = 0; i < 5; i++) {
    setTimeout(() => {
        debouncedLog('debounce', i);
        throttledLog('throttle', i);
    }, i * 50);
}

// Debounce: Only logs once (last call) after 200ms of no activity
// Throttle: Logs immediately, then could log again after 200ms
```

---

## ✅ Day 16 Checklist

- [ ] Understand when to use debounce
- [ ] Understand when to use throttle
- [ ] Implement basic debounce
- [ ] Implement basic throttle
- [ ] Handle leading/trailing options
- [ ] Implement cancel and flush methods
- [ ] Use requestAnimationFrame for animations
- [ ] Apply in React hooks
- [ ] Complete practical examples
- [ ] Write both from scratch for interviews
