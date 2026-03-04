# 📅 Day 1 – React Fundamentals

## 🎯 Learning Goals
- Understand what React is and why it exists
- Master Virtual DOM vs Real DOM concepts
- Understand Reconciliation
- Learn SPA vs MPA differences
- Understand rendering strategies (CSR, SSR, SSG)
- Set up development environment with Vite
- Learn 2026 folder structure best practices

---

## 📚 Theory

### What is React?
React is a JavaScript library for building user interfaces, developed by Facebook (Meta). It's component-based, declarative, and uses a virtual DOM for efficient updates.

**Key Characteristics:**
- **Declarative:** You describe what the UI should look like, React handles the how
- **Component-Based:** Build encapsulated components that manage their own state
- **Learn Once, Write Anywhere:** Works with web, mobile (React Native), desktop

### Virtual DOM vs Real DOM

```
Real DOM:
- Browser's actual document structure
- Expensive to manipulate
- Direct manipulation triggers reflow/repaint
- Synchronous updates

Virtual DOM:
- Lightweight JavaScript representation
- Cheap to manipulate
- Batches multiple changes
- Computes minimal DOM operations needed
```

**How it works:**
1. State changes in component
2. New Virtual DOM is created
3. Diffing: Compare new vs old Virtual DOM
4. Reconciliation: Calculate minimal changes
5. Commit: Apply only necessary changes to Real DOM

### Reconciliation

Reconciliation is React's algorithm for determining which parts of the UI need to be updated.

**Key Concepts:**
- **Diffing Algorithm:** O(n) complexity using heuristics
- **Two assumptions:**
  1. Different element types produce different trees
  2. Keys hint which children are stable across renders

```jsx
// Without key - React rebuilds entire list
{items.map(item => <ListItem {...item} />)}

// With key - React can identify and reuse elements
{items.map(item => <ListItem key={item.id} {...item} />)}
```

### SPA vs MPA

| Feature | SPA (Single Page App) | MPA (Multi Page App) |
|---------|----------------------|---------------------|
| Navigation | Client-side routing | Server requests |
| Initial Load | Slower (downloads app) | Faster (single page) |
| Subsequent Load | Instant | Full page reload |
| SEO | Challenging | Better by default |
| User Experience | App-like, smooth | Traditional web |
| Examples | Gmail, Trello | Wikipedia, Amazon |

### CSR vs SSR vs SSG

```
CSR (Client-Side Rendering):
├── Server sends empty HTML + JS bundle
├── Browser downloads and executes JS
├── React renders UI in browser
└── Best for: Dashboard, admin panels

SSR (Server-Side Rendering):
├── Server renders HTML for each request
├── Sends fully rendered HTML
├── JS hydrates for interactivity
└── Best for: Dynamic content, personalization

SSG (Static Site Generation):
├── HTML generated at build time
├── Pre-rendered pages served from CDN
├── Fastest first contentful paint
└── Best for: Blogs, docs, marketing sites

ISR (Incremental Static Regeneration):
├── SSG + ability to update at runtime
├── Revalidate pages after specified time
└── Best for: E-commerce, news sites
```

---

## 💻 Setting Up with Vite

### Why Vite in 2026?
- **Fast cold start:** Native ES modules
- **Instant HMR:** Sub-second updates
- **Optimized build:** Rollup under the hood
- **Out-of-box TypeScript support**

### Installation

```bash
# Create new project
npm create vite@latest my-react-app -- --template react-ts

# Navigate and install
cd my-react-app
npm install

# Start development server
npm run dev
```

### Project Structure

```
my-react-app/
├── public/                 # Static assets
│   └── vite.svg
├── src/
│   ├── assets/            # Images, fonts, etc.
│   ├── components/        # Reusable components
│   │   └── ui/           # UI component library
│   ├── features/          # Feature-based modules
│   ├── hooks/             # Custom hooks
│   ├── lib/               # Utility functions
│   ├── pages/             # Page components
│   ├── services/          # API services
│   ├── store/             # State management
│   ├── types/             # TypeScript types
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## ✅ Tasks

### Task 1: Create Vite + React Project

```bash
npm create vite@latest day-01-counter -- --template react-ts
cd day-01-counter
npm install
npm run dev
```

### Task 2: Build Simple Counter

Create `src/components/Counter.tsx`:

```tsx
import { useState } from 'react';

interface CounterProps {
  initialValue?: number;
  step?: number;
}

export function Counter({ initialValue = 0, step = 1 }: CounterProps) {
  const [count, setCount] = useState(initialValue);

  const increment = () => setCount(prev => prev + step);
  const decrement = () => setCount(prev => prev - step);
  const reset = () => setCount(initialValue);

  return (
    <div className="counter">
      <h2>Counter: {count}</h2>
      <div className="counter-buttons">
        <button onClick={decrement}>- {step}</button>
        <button onClick={reset}>Reset</button>
        <button onClick={increment}>+ {step}</button>
      </div>
    </div>
  );
}
```

Update `src/App.tsx`:

```tsx
import { Counter } from './components/Counter';
import './App.css';

function App() {
  return (
    <div className="app">
      <h1>Day 1: React Fundamentals</h1>
      <Counter />
      <Counter initialValue={10} step={5} />
    </div>
  );
}

export default App;
```

---

## 🎯 Interview Questions & Answers

### Q1: What is Virtual DOM?
**Answer:** The Virtual DOM is a lightweight JavaScript representation of the actual DOM. React maintains this virtual tree in memory and uses it to compute the minimal set of changes needed when state updates occur. This process involves:
1. Creating a new Virtual DOM tree on state change
2. Diffing the new tree with the previous one
3. Computing the minimal "patch" needed
4. Applying only those changes to the real DOM

This makes DOM updates efficient because:
- JavaScript operations are fast
- Batches multiple changes together
- Minimizes expensive DOM operations

### Q2: How does reconciliation work?
**Answer:** Reconciliation is React's diffing algorithm that determines what changed between renders:

1. **Element Type Check:** If root elements have different types, React tears down old tree and builds new one
2. **Same DOM Element:** React looks at attributes and updates only changed ones
3. **Same Component Element:** Instance stays same, props updated, lifecycle methods called
4. **Recursing on Children:** React iterates over both lists of children simultaneously

**Key optimizations:**
- Uses keys to identify elements in lists
- Assumes elements at same position correlate
- Stops when elements differ in type

### Q3: Why are keys important?
**Answer:** Keys help React identify which items have changed, been added, or removed in lists:

```jsx
// BAD: Using index as key
{items.map((item, index) => <Item key={index} {...item} />)}
// Problems: Reordering breaks state, poor performance

// GOOD: Using unique ID
{items.map(item => <Item key={item.id} {...item} />)}
// Benefits: Correct identity, efficient updates
```

**Why unique keys matter:**
- React uses keys to match children between renders
- Stable keys preserve component state
- Help React make minimal DOM operations
- Index as key causes bugs when list is reordered

### Q4: Explain CSR vs SSR vs SSG
**Answer:**
- **CSR:** JavaScript renders UI in browser. Good for SPAs, dashboards. SEO challenges.
- **SSR:** Server renders HTML per request. Good for dynamic, personalized content. Better SEO.
- **SSG:** HTML generated at build time. Fastest, best for static content. Limited dynamism.

### Q5: Why Vite over Create React App?
**Answer:** 
- CRA is deprecated/unmaintained
- Vite uses native ES modules (no bundling in dev)
- 10-100x faster cold start
- Instant HMR
- Better TypeScript support
- Optimized production builds

---

## 📝 Notes

```
Personal notes space - add your learnings here:

_______________________________________________

_______________________________________________

_______________________________________________
```

---

## ✅ Completion Checklist

- [ ] Understood Virtual DOM concept
- [ ] Can explain reconciliation
- [ ] Know differences between SPA/MPA
- [ ] Understand CSR/SSR/SSG
- [ ] Created Vite project
- [ ] Built counter component
- [ ] Can answer all interview questions

---

**Next:** [Day 2 - JSX & Rendering](../day-02/README.md)
