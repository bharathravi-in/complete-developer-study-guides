# Day 2: Modules & Package Management

## 🎯 Learning Objectives
- Master CommonJS and ES Modules
- Understand module resolution algorithm
- Learn npm/yarn/pnpm package management
- Understand package.json, lockfiles, and semver

---

## 📚 Module Systems

### CommonJS (CJS) - The Original

```javascript
// math.js - Exporting
const add = (a, b) => a + b;
const subtract = (a, b) => a - b;

module.exports = { add, subtract };
// OR
exports.multiply = (a, b) => a * b;

// app.js - Importing
const { add, subtract } = require('./math');
const math = require('./math'); // entire module object

// How require() works internally:
// 1. Resolve path (relative, node_modules, built-in)
// 2. Load file contents
// 3. Wrap in function: (function(exports, require, module, __filename, __dirname) { ... })
// 4. Execute wrapped function
// 5. Cache the result
```

### Module Wrapper Function

```javascript
// Every module is wrapped in this:
(function(exports, require, module, __filename, __dirname) {
  // Your module code lives here
  // This is why these variables are available
  console.log(__filename); // /home/user/app/index.js
  console.log(__dirname);  // /home/user/app
});

// Proof:
console.log(require('module').wrapper);
// [ '(function (exports, require, module, __filename, __dirname) { ', '\n});' ]
```

### ES Modules (ESM) - The Standard

```javascript
// math.mjs (or .js with "type": "module" in package.json)
export const add = (a, b) => a + b;
export const subtract = (a, b) => a - b;
export default class Calculator { /* ... */ }

// app.mjs
import Calculator, { add, subtract } from './math.mjs';
import * as math from './math.mjs';

// Dynamic imports (works in both CJS and ESM)
const module = await import('./math.mjs');

// Top-level await (ESM only)
const data = await fetch('https://api.example.com/data');
```

### CJS vs ESM Comparison

| Feature | CommonJS | ES Modules |
|---------|----------|------------|
| Syntax | `require()` / `module.exports` | `import` / `export` |
| Loading | Synchronous | Asynchronous |
| Execution | At runtime | Parsed at compile time |
| Caching | After first `require()` | Singleton per URL |
| Top-level await | ❌ | ✅ |
| `__filename` | ✅ | Use `import.meta.url` |
| Circular deps | Returns partial export | Live bindings (reference) |
| Tree shaking | ❌ | ✅ |

### Module Resolution Algorithm

```javascript
require('express');
// 1. Is it a core module? (fs, path, http) → Return it
// 2. Does it start with './' or '/' ? → Load as file/directory
// 3. Look in node_modules:
//    ./node_modules/express
//    ../node_modules/express
//    ../../node_modules/express
//    ... up to root

// File resolution order:
require('./foo');
// 1. ./foo.js
// 2. ./foo.json
// 3. ./foo.node (C++ addon)
// 4. ./foo/index.js
// 5. ./foo/package.json → "main" field
```

### Circular Dependencies

```javascript
// a.js
console.log('a starting');
exports.done = false;
const b = require('./b'); // b gets partial 'a'
console.log('in a, b.done =', b.done);
exports.done = true;
console.log('a done');

// b.js
console.log('b starting');
exports.done = false;
const a = require('./a'); // gets PARTIAL a (done = false)
console.log('in b, a.done =', a.done); // false!
exports.done = true;
console.log('b done');

// main.js
const a = require('./a');
const b = require('./b'); // cached, not re-executed
// Output: a starting → b starting → in b, a.done = false → b done → in a, b.done = true → a done
```

---

## 📦 Package Management

### package.json Essential Fields

```json
{
  "name": "my-app",
  "version": "1.2.3",
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.mjs",
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs",
      "types": "./dist/index.d.ts"
    },
    "./utils": "./dist/utils.mjs"
  },
  "engines": { "node": ">=18.0.0" },
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "test": "jest",
    "build": "tsc"
  },
  "dependencies": {},
  "devDependencies": {},
  "peerDependencies": {}
}
```

### Semantic Versioning (SemVer)

```
MAJOR.MINOR.PATCH
  2  .  1  .  3

^2.1.3 → >=2.1.3 <3.0.0 (compatible changes)
~2.1.3 → >=2.1.3 <2.2.0 (patch-level changes)
2.1.3  → exactly 2.1.3
>=2.0.0 <3.0.0 → range
*      → any version
```

### npm vs yarn vs pnpm

```bash
# npm - comes with Node.js
npm install express           # add dependency
npm install -D jest           # add devDependency
npm ci                        # clean install from lockfile (CI/CD)
npm audit                     # security audit
npm ls --depth=0              # list top-level deps

# pnpm - fast, disk efficient (uses content-addressable store)
pnpm install                  # hard links to global store
pnpm add express
pnpm why express              # why is this installed?

# Key difference: pnpm uses a flat node_modules with symlinks
# Prevents "phantom dependencies" (using packages you didn't declare)
```

### Understanding Lockfiles

```
package-lock.json / yarn.lock / pnpm-lock.yaml

Purpose:
- Deterministic installs (same deps across all environments)
- Records exact versions resolved
- Records integrity hashes (SHA-512)
- MUST be committed to git

# Always use `npm ci` in CI/CD (uses lockfile, not package.json)
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is the difference between `require()` and `import`?**

`require()` is CommonJS (synchronous, runtime loading, returns cached copy). `import` is ES Modules (asynchronous, parsed at compile time, live bindings). CJS wraps in function; ESM is strict mode by default. Use `"type": "module"` in package.json for ESM.

**Q2: What is the purpose of `package-lock.json`?**

It locks exact dependency versions (including transitive deps) to ensure deterministic installs across environments. Without it, `^2.1.0` might resolve to different patch versions on different machines. Always commit it to version control.

**Q3: What are `dependencies` vs `devDependencies` vs `peerDependencies`?**

- `dependencies`: Required at runtime (express, lodash)
- `devDependencies`: Only for development (jest, eslint) — not installed in production with `npm install --production`
- `peerDependencies`: Expected to be provided by the consumer (e.g., React for a React component library)

### Intermediate

**Q4: Explain Node.js module caching. How can it cause issues?**

After first `require()`, the module is cached in `require.cache`. Subsequent requires return the cached exports object. Issues: (1) Singleton state shared across imports, (2) Circular deps return partial exports, (3) Memory leaks if modules accumulate state. Clear cache: `delete require.cache[require.resolve('./module')]`.

**Q5: What is the `exports` field in package.json?**

The `exports` field (Node 12+) defines the public API of a package, replacing `main`. It supports conditional exports (import/require/types), subpath exports, and blocks access to internal files. It's the modern way to create dual CJS/ESM packages.

**Q6: How does pnpm differ from npm in dependency management?**

pnpm uses a content-addressable store and hard links, so packages are stored once globally. Its `node_modules` uses symlinks, creating a strict structure that prevents accessing undeclared dependencies (phantom dependencies). This saves disk space and is faster than npm.

### Advanced

**Q7: How would you create a dual CJS/ESM package?**

Use the `exports` field with conditional exports: `"import"` for ESM entry, `"require"` for CJS entry. Build both formats (e.g., with tsup/rollup). Handle named exports carefully — CJS default export becomes `module.default` in ESM interop. Test with both `require()` and `import`.

**Q8: Explain the security implications of `npm install` and how to mitigate risks.**

Risks: supply chain attacks (typosquatting, malicious postinstall scripts), dependency confusion. Mitigate: use lockfiles + `npm ci`, run `npm audit`, use `.npmrc` with `ignore-scripts=true` for untrusted packages, pin versions, use tools like Socket.dev or Snyk, verify package provenance.

**Q9: What are Node.js module loading hooks and how do they work?**

Node 20+ provides `--loader` / `register()` for customizing module resolution and loading. Hooks: `resolve()` (customize path resolution), `load()` (customize how source is obtained), `initialize()` (setup). Used by TypeScript loaders (tsx, ts-node), instrumentation (APM tools), and custom protocols.

---

## 🛠️ Hands-on Exercise

Create a modular calculator app demonstrating both module systems:

```javascript
// Create these files:
// 1. operations/add.js (CJS export)
// 2. operations/multiply.mjs (ESM export)
// 3. calculator.js - imports both, demonstrates interop
// 4. package.json with proper "exports" field

// Bonus: Create a circular dependency scenario and fix it
```
