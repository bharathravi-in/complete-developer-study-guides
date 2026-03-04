# 📅 Day 24 – Accessibility (a11y)

## 🎯 Learning Goals
- Understand WCAG guidelines
- Implement accessible React components
- Learn screen reader best practices
- Master keyboard navigation

---

## 📚 Theory

### WCAG Fundamentals

```
WCAG 2.1 Principles (POUR):

1. Perceivable
   - Text alternatives for images
   - Captions for videos
   - Sufficient color contrast
   - Resizable text

2. Operable
   - Keyboard accessible
   - No time limits (or adjustable)
   - No seizure-inducing content
   - Clear navigation

3. Understandable
   - Readable content
   - Predictable behavior
   - Input assistance
   - Error prevention

4. Robust
   - Compatible with assistive tech
   - Valid HTML
   - ARIA when needed

Conformance Levels:
- Level A (minimum)
- Level AA (recommended - legal requirement in many places)
- Level AAA (highest)
```

### Semantic HTML

```tsx
// ❌ Bad: Div soup
<div onClick={handleClick}>Click me</div>
<div class="heading">Title</div>
<div class="list">
  <div>Item 1</div>
  <div>Item 2</div>
</div>

// ✅ Good: Semantic HTML
<button onClick={handleClick}>Click me</button>
<h1>Title</h1>
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
</ul>

// Page structure
<header>
  <nav aria-label="Main navigation">
    <ul>
      <li><a href="/">Home</a></li>
      <li><a href="/about">About</a></li>
    </ul>
  </nav>
</header>

<main>
  <article>
    <h1>Article Title</h1>
    <section>
      <h2>Section Heading</h2>
      <p>Content...</p>
    </section>
  </article>
  
  <aside aria-label="Related content">
    <h2>Related Articles</h2>
  </aside>
</main>

<footer>
  <p>© 2026 Company</p>
</footer>
```

### ARIA Attributes

```tsx
// ARIA roles, states, and properties
// Only use when native HTML isn't sufficient

// Role - defines element type
<div role="button" tabIndex={0}>Custom Button</div>
<div role="alert">Error message</div>
<div role="dialog" aria-modal="true">Modal content</div>

// States - current condition
<button aria-pressed="true">Toggle On</button>
<button aria-expanded="false">Accordion</button>
<input aria-invalid="true" aria-describedby="error-msg" />

// Properties - describe relationships
<input aria-labelledby="name-label" />
<div aria-describedby="help-text">Form field</div>
<button aria-controls="menu-id">Open Menu</button>

// Live regions - announce changes
<div aria-live="polite">Updated content</div>
<div aria-live="assertive">Critical alert</div>
<div role="status" aria-atomic="true">Loading... 50%</div>

// Accessible Button Component
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isLoading?: boolean;
  loadingText?: string;
}

function Button({ 
  children, 
  isLoading, 
  loadingText = 'Loading', 
  disabled,
  ...props 
}: ButtonProps) {
  return (
    <button
      {...props}
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      aria-disabled={disabled}
    >
      {isLoading ? (
        <>
          <span className="sr-only">{loadingText}</span>
          <Spinner aria-hidden="true" />
        </>
      ) : (
        children
      )}
    </button>
  );
}
```

### Keyboard Navigation

```tsx
// Focus management
function Modal({ isOpen, onClose, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocus = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Save current focus
      previousFocus.current = document.activeElement as HTMLElement;
      
      // Focus modal
      modalRef.current?.focus();
      
      // Trap focus inside modal
      const handleTab = (e: KeyboardEvent) => {
        if (e.key !== 'Tab') return;
        
        const focusable = modalRef.current?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        
        if (!focusable?.length) return;
        
        const first = focusable[0] as HTMLElement;
        const last = focusable[focusable.length - 1] as HTMLElement;
        
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first.focus();
        }
      };
      
      document.addEventListener('keydown', handleTab);
      return () => document.removeEventListener('keydown', handleTab);
    } else {
      // Restore focus
      previousFocus.current?.focus();
    }
  }, [isOpen]);

  // Close on Escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [onClose]);

  if (!isOpen) return null;

  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      tabIndex={-1}
    >
      <h2 id="modal-title">Modal Title</h2>
      {children}
      <button onClick={onClose}>Close</button>
    </div>
  );
}

// Custom keyboard interactions
function Dropdown() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const buttonRef = useRef<HTMLButtonElement>(null);
  const itemsRef = useRef<(HTMLLIElement | null)[]>([]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setActiveIndex(prev => Math.min(prev + 1, items.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setActiveIndex(prev => Math.max(prev - 1, 0));
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        if (activeIndex >= 0) selectItem(activeIndex);
        break;
      case 'Escape':
        setIsOpen(false);
        buttonRef.current?.focus();
        break;
    }
  };

  return (
    <div onKeyDown={handleKeyDown}>
      <button
        ref={buttonRef}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        onClick={() => setIsOpen(!isOpen)}
      >
        Select option
      </button>
      {isOpen && (
        <ul role="listbox" aria-activedescendant={`item-${activeIndex}`}>
          {items.map((item, index) => (
            <li
              key={item.id}
              id={`item-${index}`}
              ref={el => itemsRef.current[index] = el}
              role="option"
              aria-selected={index === activeIndex}
              onClick={() => selectItem(index)}
            >
              {item.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
```

### Form Accessibility

```tsx
function AccessibleForm() {
  const [errors, setErrors] = useState<Record<string, string>>({});

  return (
    <form aria-describedby="form-instructions">
      <p id="form-instructions">
        Required fields are marked with an asterisk (*).
      </p>

      {/* Text input */}
      <div>
        <label htmlFor="name">
          Name <span aria-hidden="true">*</span>
          <span className="sr-only">(required)</span>
        </label>
        <input
          id="name"
          type="text"
          required
          aria-required="true"
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? 'name-error' : undefined}
        />
        {errors.name && (
          <span id="name-error" role="alert" className="error">
            {errors.name}
          </span>
        )}
      </div>

      {/* Radio group */}
      <fieldset>
        <legend>Notification preferences</legend>
        <div>
          <input type="radio" id="email-pref" name="notification" value="email" />
          <label htmlFor="email-pref">Email</label>
        </div>
        <div>
          <input type="radio" id="sms-pref" name="notification" value="sms" />
          <label htmlFor="sms-pref">SMS</label>
        </div>
      </fieldset>

      {/* Checkbox */}
      <div>
        <input type="checkbox" id="terms" required />
        <label htmlFor="terms">
          I agree to the <a href="/terms">Terms of Service</a>
        </label>
      </div>

      <button type="submit">Submit</button>
    </form>
  );
}

// Screen reader only class (Tailwind)
// .sr-only {
//   position: absolute;
//   width: 1px;
//   height: 1px;
//   padding: 0;
//   margin: -1px;
//   overflow: hidden;
//   clip: rect(0, 0, 0, 0);
//   border: 0;
// }
```

### Testing Accessibility

```tsx
// Jest + Testing Library
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Button', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<Button>Click me</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('should be keyboard accessible', () => {
    render(<Button onClick={jest.fn()}>Click</Button>);
    const button = screen.getByRole('button');
    button.focus();
    expect(document.activeElement).toBe(button);
  });
});

// Storybook a11y addon
// .storybook/main.ts
export default {
  addons: ['@storybook/addon-a11y'],
};

// ESLint plugin
// .eslintrc
{
  "extends": ["plugin:jsx-a11y/recommended"]
}
```

---

## ✅ Task: Build Accessible Component Library

Create these accessible components:
- Button (with loading, disabled states)
- Modal (focus trap, escape to close)
- Dropdown/Select (keyboard navigation)
- Form with validation
- Tabs component

---

## 🎯 Interview Questions & Answers

### Q1: What is ARIA and when should you use it?
**Answer:** ARIA (Accessible Rich Internet Applications) provides attributes for accessibility. Use when native HTML isn't sufficient (custom widgets). First rule: prefer native HTML. ARIA doesn't add behavior, only semantics for assistive tech.

### Q2: How do you test for accessibility?
**Answer:** Automated: axe-core, jest-axe, Lighthouse, eslint-plugin-jsx-a11y. Manual: keyboard navigation, screen reader testing (NVDA, VoiceOver). Real user testing with assistive tech users.

### Q3: What is focus trapping and when is it needed?
**Answer:** Keeping keyboard focus within a component (modal, dropdown). Needed for modals, dialogs, and other overlays to prevent users from tabbing into background content. Implement with tab key interception.

---

## ✅ Completion Checklist

- [ ] Understand WCAG guidelines
- [ ] Use semantic HTML properly
- [ ] Implement ARIA correctly
- [ ] Handle keyboard navigation
- [ ] Built accessible components

---

**Previous:** [Day 23 - Performance](../day-23/README.md)  
**Next:** [Day 25 - Animations](../day-25/README.md)
