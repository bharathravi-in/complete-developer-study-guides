# Day 13: Modules

## 🎯 Learning Objectives
- Understand CommonJS modules
- Master ES Modules (ESM)
- Learn tree shaking
- Implement dynamic imports

---

## 📚 CommonJS (CJS)

CommonJS is the module system used by Node.js.

```javascript
// math.js - Exporting
const add = (a, b) => a + b;
const subtract = (a, b) => a - b;
const PI = 3.14159;

// Named exports
module.exports.add = add;
module.exports.subtract = subtract;
module.exports.PI = PI;

// Or export an object
module.exports = {
    add,
    subtract,
    PI
};

// Or shorthand
exports.add = add;
exports.subtract = subtract;
// Note: exports = {} won't work (breaks reference)

// app.js - Importing
const math = require('./math');
console.log(math.add(2, 3)); // 5
console.log(math.PI);        // 3.14159

// Destructured import
const { add, subtract } = require('./math');
console.log(add(5, 3));      // 8

// Import JSON
const config = require('./config.json');

// Import from node_modules
const express = require('express');
```

### CommonJS Characteristics

```javascript
// 1. Synchronous loading
const fs = require('fs'); // Blocks until loaded

// 2. Runs at runtime (dynamic)
const moduleName = condition ? 'moduleA' : 'moduleB';
const mod = require(`./${moduleName}`);

// 3. Exports are COPIES
// counter.js
let count = 0;
module.exports = {
    getCount: () => count,
    increment: () => count++
};

// app.js
const counter = require('./counter');
console.log(counter.count); // undefined (not exported directly)
counter.increment();
console.log(counter.getCount()); // 1

// 4. Cached after first require
const a = require('./module');
const b = require('./module');
console.log(a === b); // true (same cached object)

// Clear cache (for testing)
delete require.cache[require.resolve('./module')];
```

---

## 📦 ES Modules (ESM)

ES Modules are the standard JavaScript module system.

```javascript
// math.js - Named exports
export const add = (a, b) => a + b;
export const subtract = (a, b) => a - b;
export const PI = 3.14159;

// Or export later
const multiply = (a, b) => a * b;
const divide = (a, b) => a / b;
export { multiply, divide };

// Default export (one per module)
export default function calculate(expr) {
    return eval(expr);
}

// app.js - Named imports
import { add, subtract, PI } from './math.js';
console.log(add(2, 3)); // 5

// Import with alias
import { add as sum } from './math.js';
console.log(sum(2, 3)); // 5

// Import all as namespace
import * as math from './math.js';
console.log(math.add(2, 3)); // 5
console.log(math.PI);        // 3.14159

// Default import
import calculate from './math.js';
console.log(calculate('2 + 3')); // 5

// Mixed imports
import calculate, { add, PI } from './math.js';

// Re-export
export { add, subtract } from './math.js';
export * from './utils.js';
export { default as math } from './math.js';
```

### ESM in HTML

```html
<!-- Type module is required -->
<script type="module" src="app.js"></script>

<!-- Inline module -->
<script type="module">
    import { greet } from './greet.js';
    greet('World');
</script>

<!-- Fallback for unsupported browsers -->
<script nomodule src="fallback.js"></script>
```

### ESM in Node.js

```javascript
// package.json
{
    "type": "module" // Treat .js as ESM
}

// Or use .mjs extension for ESM files
// file.mjs

// Import CommonJS in ESM
import pkg from 'commonjs-package';
// Note: Named imports from CJS might not work directly

// Import JSON (requires Node 18+)
import config from './config.json' assert { type: 'json' };

// Or with createRequire
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const config = require('./config.json');
```

---

## ⚖️ CommonJS vs ES Modules

```javascript
/*
═══════════════════════════════════════════════════════════════════
FEATURE               │ COMMONJS           │ ES MODULES
═══════════════════════════════════════════════════════════════════
Loading               │ Synchronous        │ Asynchronous
Evaluation time       │ Runtime            │ Parse time
Import hoisting       │ No                 │ Yes (hoisted)
Structure analysis    │ Dynamic            │ Static
Tree shaking          │ Difficult          │ Easy
Top-level await       │ No                 │ Yes
Browser support       │ No (needs bundler) │ Yes
this value            │ module.exports     │ undefined
File extension        │ .js, .cjs          │ .js, .mjs
Import style          │ require()          │ import/export
═══════════════════════════════════════════════════════════════════
*/

// Static vs Dynamic imports

// CommonJS - Dynamic (determined at runtime)
const module = require(`./${dynamicPath}`); // Works!

// ESM - Static (determined at parse time)
// import something from `./${dynamicPath}`; // Syntax Error!

// For dynamic ESM, use import()
const module = await import(`./${dynamicPath}`);
```

---

## 🌲 Tree Shaking

Tree shaking eliminates unused exports from the final bundle.

```javascript
// utils.js
export const used = () => console.log('I am used');
export const unused = () => console.log('I am not used');
export const alsoUnused = () => console.log('Neither am I');

// app.js
import { used } from './utils.js';
used();

/*
After tree shaking, only 'used' remains in the bundle.
'unused' and 'alsoUnused' are removed.

REQUIREMENTS for tree shaking:
1. Use ES Modules (static analysis possible)
2. Pure module (no side effects)
3. Mark modules as side-effect free in package.json:

{
    "sideEffects": false,
    // Or specify which files have side effects:
    "sideEffects": ["*.css", "./src/polyfills.js"]
}
*/

// Side effects prevent tree shaking
// utils-with-side-effects.js
console.log('Module loaded!'); // Side effect - runs on import

export const pure = () => 'pure';
// Even if 'pure' is unused, the module runs

// Avoiding side effects
// Instead of:
export const config = fetchConfig(); // Runs immediately

// Do this:
export const getConfig = () => fetchConfig(); // Runs when called
```

### Tree Shaking Best Practices

```javascript
// ❌ Bad - imports everything
import _ from 'lodash';
_.map([1, 2, 3], x => x * 2);

// ✅ Good - only imports 'map'
import map from 'lodash/map';
// Or with lodash-es:
import { map } from 'lodash-es';

// ❌ Bad - barrel exports (index.js re-exports everything)
// utils/index.js
export * from './string';
export * from './array';
export * from './object';

// app.js
import { capitalize } from './utils'; // Might import all!

// ✅ Good - direct imports
import { capitalize } from './utils/string';
```

---

## 🔄 Dynamic Imports

Load modules on demand using `import()`.

```javascript
// Dynamic import returns a Promise
const module = await import('./heavy-module.js');
module.doSomething();

// Conditional loading
if (needsFeature) {
    const { feature } = await import('./feature.js');
    feature();
}

// User action triggered loading
button.addEventListener('click', async () => {
    const { showModal } = await import('./modal.js');
    showModal();
});

// Route-based code splitting
async function loadRoute(route) {
    const routes = {
        '/home': () => import('./pages/Home.js'),
        '/about': () => import('./pages/About.js'),
        '/contact': () => import('./pages/Contact.js')
    };
    
    const loader = routes[route];
    if (loader) {
        const module = await loader();
        return module.default;
    }
}

// Lazy loading with fallback
async function loadFeature() {
    try {
        const { feature } = await import('./feature.js');
        return feature;
    } catch (error) {
        console.error('Failed to load feature:', error);
        return fallbackFeature;
    }
}

// Preloading for performance
function preloadModule(path) {
    const link = document.createElement('link');
    link.rel = 'modulepreload';
    link.href = path;
    document.head.appendChild(link);
}

preloadModule('./heavy-module.js');
// Later: import() will be faster
```

---

## 📋 Module Patterns

### Singleton Pattern

```javascript
// database.js
let instance = null;

class Database {
    constructor(connectionString) {
        if (instance) {
            return instance;
        }
        this.connectionString = connectionString;
        instance = this;
    }
    
    query(sql) {
        console.log(`Executing: ${sql}`);
    }
}

export default Database;

// Anywhere in the app:
import Database from './database.js';
const db1 = new Database('conn1');
const db2 = new Database('conn2');
console.log(db1 === db2); // true (same instance)
```

### Facade Pattern

```javascript
// api-facade.js
import { getUserById } from './services/user-service.js';
import { getOrdersByUser } from './services/order-service.js';
import { getPaymentHistory } from './services/payment-service.js';

// Simplified API for common operations
export async function getUserDashboardData(userId) {
    const [user, orders, payments] = await Promise.all([
        getUserById(userId),
        getOrdersByUser(userId),
        getPaymentHistory(userId)
    ]);
    
    return { user, orders, payments };
}
```

### Barrel Exports (with caution)

```javascript
// components/index.js
export { Button } from './Button.js';
export { Input } from './Input.js';
export { Modal } from './Modal.js';

// Usage
import { Button, Input } from './components';

// Note: Can hurt tree shaking. Modern bundlers handle this better.
```

---

## 🧪 import.meta

ESM provides import.meta for module metadata.

```javascript
// Current module's URL
console.log(import.meta.url);
// file:///path/to/current/module.js

// Get directory name (equivalent to __dirname in CJS)
const url = new URL('.', import.meta.url);
console.log(url.pathname);

// In Node.js
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Environment-specific
if (import.meta.env?.DEV) {
    console.log('Development mode');
}

// Hot module replacement (Vite)
if (import.meta.hot) {
    import.meta.hot.accept((newModule) => {
        console.log('Module updated');
    });
}
```

---

## 🔬 Practice Problems

```javascript
// Problem 1: Create a module with named and default exports
// calculator.js
export const add = (a, b) => a + b;
export const subtract = (a, b) => a - b;
export default class Calculator {
    evaluate(expr) { return eval(expr); }
}

// Problem 2: Implement a lazy-loaded feature
async function loadChartLibrary() {
    const { Chart } = await import('chart.js');
    return Chart;
}

// Problem 3: Create a module registry for plugins
const plugins = new Map();

export function registerPlugin(name, loader) {
    plugins.set(name, loader);
}

export async function loadPlugin(name) {
    const loader = plugins.get(name);
    if (!loader) throw new Error(`Plugin ${name} not found`);
    return await loader();
}

registerPlugin('analytics', () => import('./plugins/analytics.js'));
registerPlugin('chat', () => import('./plugins/chat.js'));

// Usage
const analytics = await loadPlugin('analytics');

// Problem 4: Convert CommonJS to ESM
// Before (CJS)
const path = require('path');
const fs = require('fs');
module.exports = { readConfig };

// After (ESM)
import path from 'path';
import fs from 'fs/promises';
export { readConfig };
```

---

## ✅ Day 13 Checklist

- [ ] Understand CommonJS require/exports
- [ ] Know require caching behavior
- [ ] Master ES Modules import/export syntax
- [ ] Understand named vs default exports
- [ ] Know the differences between CJS and ESM
- [ ] Understand tree shaking requirements
- [ ] Implement dynamic imports
- [ ] Know when to use dynamic imports
- [ ] Use import.meta for module metadata
- [ ] Convert between CJS and ESM
- [ ] Complete practice problems
