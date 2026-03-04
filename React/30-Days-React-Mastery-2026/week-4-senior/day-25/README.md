# 📅 Day 25 – Animations

## 🎯 Learning Goals
- Master Framer Motion
- Learn CSS transitions in React
- Implement page transitions
- Create gesture-based animations

---

## 📚 Theory

### Framer Motion Fundamentals

```tsx
import { motion, AnimatePresence } from 'framer-motion';

// Basic animation
function FadeIn() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      Hello World
    </motion.div>
  );
}

// Animate on mount & unmount
function Modal({ isOpen, onClose }: ModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.9 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
        >
          <ModalContent onClose={onClose} />
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// Variants for orchestrated animations
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

function List({ items }: { items: Item[] }) {
  return (
    <motion.ul
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {items.map(item => (
        <motion.li key={item.id} variants={itemVariants}>
          {item.name}
        </motion.li>
      ))}
    </motion.ul>
  );
}

// Whilte states
function InteractiveCard() {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      whileFocus={{ boxShadow: '0 0 0 2px blue' }}
      transition={{ type: 'spring', stiffness: 400 }}
    >
      Click me
    </motion.div>
  );
}
```

### Gestures

```tsx
import { motion, useDragControls, PanInfo } from 'framer-motion';

// Draggable
function DraggableCard() {
  return (
    <motion.div
      drag
      dragConstraints={{ top: -100, bottom: 100, left: -100, right: 100 }}
      dragElastic={0.2}
      dragMomentum={false}
      whileDrag={{ scale: 1.1 }}
    >
      Drag me
    </motion.div>
  );
}

// Swipe to delete
function SwipeToDelete({ onDelete }: { onDelete: () => void }) {
  const handleDragEnd = (event: MouseEvent, info: PanInfo) => {
    if (info.offset.x < -100) {
      onDelete();
    }
  };

  return (
    <motion.div
      drag="x"
      dragConstraints={{ left: 0, right: 0 }}
      onDragEnd={handleDragEnd}
      animate={{ x: 0 }}
    >
      <div className="item-content">Swipe left to delete</div>
      <div className="delete-background">Delete</div>
    </motion.div>
  );
}

// Scroll-linked animations
import { useScroll, useTransform } from 'framer-motion';

function ScrollProgress() {
  const { scrollYProgress } = useScroll();
  
  return (
    <motion.div
      style={{
        scaleX: scrollYProgress,
        transformOrigin: '0%',
      }}
      className="progress-bar"
    />
  );
}

function ParallaxImage() {
  const { scrollY } = useScroll();
  const y = useTransform(scrollY, [0, 500], [0, -150]);

  return (
    <motion.div style={{ y }}>
      <img src="/hero.jpg" alt="Hero" />
    </motion.div>
  );
}
```

### Page Transitions

```tsx
// With React Router
import { motion, AnimatePresence } from 'framer-motion';
import { useLocation, Routes, Route } from 'react-router-dom';

const pageVariants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
};

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route
          path="/"
          element={
            <motion.div
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <HomePage />
            </motion.div>
          }
        />
        <Route
          path="/about"
          element={
            <motion.div
              variants={pageVariants}
              initial="initial"
              animate="animate"
              exit="exit"
            >
              <AboutPage />
            </motion.div>
          }
        />
      </Routes>
    </AnimatePresence>
  );
}

// Shared layout animations (morph effect)
function ProductList() {
  const [selected, setSelected] = useState<Product | null>(null);

  return (
    <>
      <div className="grid">
        {products.map(product => (
          <motion.div
            key={product.id}
            layoutId={`product-${product.id}`}
            onClick={() => setSelected(product)}
          >
            <motion.img
              layoutId={`image-${product.id}`}
              src={product.image}
            />
            <motion.h3 layoutId={`title-${product.id}`}>
              {product.name}
            </motion.h3>
          </motion.div>
        ))}
      </div>

      <AnimatePresence>
        {selected && (
          <motion.div
            layoutId={`product-${selected.id}`}
            className="modal"
          >
            <motion.img
              layoutId={`image-${selected.id}`}
              src={selected.image}
            />
            <motion.h3 layoutId={`title-${selected.id}`}>
              {selected.name}
            </motion.h3>
            <p>{selected.description}</p>
            <button onClick={() => setSelected(null)}>Close</button>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
```

### CSS Transitions with React

```tsx
// CSS Modules approach
// styles.module.css
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.fadeEnter {
  opacity: 0;
}

.fadeEnterActive {
  opacity: 1;
  transition: opacity 300ms ease-in;
}

.fadeExit {
  opacity: 1;
}

.fadeExitActive {
  opacity: 0;
  transition: opacity 300ms ease-out;
}

// With react-transition-group
import { CSSTransition, TransitionGroup } from 'react-transition-group';
import styles from './styles.module.css';

function FadeList({ items }: { items: Item[] }) {
  return (
    <TransitionGroup component="ul">
      {items.map(item => (
        <CSSTransition
          key={item.id}
          timeout={300}
          classNames={{
            enter: styles.fadeEnter,
            enterActive: styles.fadeEnterActive,
            exit: styles.fadeExit,
            exitActive: styles.fadeExitActive,
          }}
        >
          <li>{item.name}</li>
        </CSSTransition>
      ))}
    </TransitionGroup>
  );
}

// Tailwind CSS animations
function TailwindAnimations() {
  return (
    <>
      <div className="animate-spin">Loading...</div>
      <div className="animate-pulse">Skeleton</div>
      <div className="animate-bounce">Attention</div>
      
      {/* Custom with motion-safe */}
      <div className="motion-safe:animate-fade-in motion-reduce:opacity-100">
        Respects reduced motion preference
      </div>
    </>
  );
}
```

### Performance & Accessibility

```tsx
// Use transform and opacity (GPU accelerated)
// ✅ Good
<motion.div animate={{ x: 100, opacity: 0.5 }} />

// ❌ Avoid (triggers layout)
<motion.div animate={{ left: 100, width: 200 }} />

// Respect reduced motion
import { useReducedMotion } from 'framer-motion';

function AccessibleAnimation() {
  const shouldReduceMotion = useReducedMotion();

  const variants = {
    initial: shouldReduceMotion 
      ? { opacity: 0 } 
      : { opacity: 0, y: 50 },
    animate: shouldReduceMotion 
      ? { opacity: 1 } 
      : { opacity: 1, y: 0 },
  };

  return (
    <motion.div
      variants={variants}
      initial="initial"
      animate="animate"
      transition={{ duration: shouldReduceMotion ? 0.01 : 0.5 }}
    >
      Content
    </motion.div>
  );
}

// CSS approach
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## ✅ Task: Build Animated App

Create:
- Animated list with stagger effect
- Modal with enter/exit animation
- Page transition system
- Drag-to-reorder list
- Scroll-linked parallax effect

---

## 🎯 Interview Questions & Answers

### Q1: Why use Framer Motion over CSS?
**Answer:** Framer Motion offers: exit animations (AnimatePresence), gesture support, layout animations, orchestration (variants), React integration. Use CSS for simple hover effects, Framer for complex interactions.

### Q2: How do you ensure animation performance?
**Answer:** Animate only `transform` and `opacity` (GPU accelerated). Avoid animating layout properties (width, height, top, left). Use `will-change` sparingly. Profile with DevTools Performance tab.

### Q3: How do you handle reduced motion preferences?
**Answer:** Use `useReducedMotion()` hook or `prefers-reduced-motion` media query. Provide instant or minimal animations for users who need them. Never completely disable - use opacity fades instead.

---

## ✅ Completion Checklist

- [ ] Master Framer Motion basics
- [ ] Implement gesture animations
- [ ] Create page transitions
- [ ] Handle reduced motion
- [ ] Built animated application

---

**Previous:** [Day 24 - Accessibility](../day-24/README.md)  
**Next:** [Day 26 - React Native](../day-26/README.md)
