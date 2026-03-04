# Day 17: DOM & Events Deep Dive

## 🎯 Learning Objectives
- Understand DOM tree structure
- Master event propagation (bubbling/capturing)
- Learn event delegation
- Implement custom events
- Optimize DOM performance

---

## 🌳 DOM Tree Structure

```javascript
/*
HTML:
<html>
    <head><title>Page</title></head>
    <body>
        <div id="app">
            <h1>Hello</h1>
            <p>World</p>
        </div>
    </body>
</html>

DOM Tree:
                    document
                        │
                      <html>
                     /      \
                <head>      <body>
                  │            │
               <title>      <div#app>
                  │          /    \
                "Page"    <h1>    <p>
                           │       │
                       "Hello"  "World"
*/

// Accessing elements
document.documentElement;  // <html>
document.head;             // <head>
document.body;             // <body>

// Node types
const div = document.getElementById('app');
div.nodeType;  // 1 (Element)
div.nodeName;  // "DIV"
div.nodeValue; // null (elements don't have nodeValue)

const text = div.firstChild.firstChild;
text.nodeType;  // 3 (Text)
text.nodeName;  // "#text"
text.nodeValue; // "Hello"

/*
Node Types:
1  - Element
3  - Text
8  - Comment
9  - Document
10 - DocumentType
11 - DocumentFragment
*/
```

---

## 🔍 DOM Selection Methods

```javascript
// By ID (fastest)
document.getElementById('app');

// By Class
document.getElementsByClassName('item'); // HTMLCollection (live)

// By Tag
document.getElementsByTagName('div'); // HTMLCollection (live)

// By Query Selector (most flexible)
document.querySelector('.item');         // First match
document.querySelectorAll('.item');       // NodeList (static)

// HTMLCollection vs NodeList
const collection = document.getElementsByClassName('item'); // Live
const nodeList = document.querySelectorAll('.item');        // Static

// Adding an element with class 'item' updates collection but not nodeList

// Converting to array
const arr1 = Array.from(nodeList);
const arr2 = [...nodeList];

// Traversal
element.parentNode;
element.parentElement;
element.children;          // Only elements
element.childNodes;        // All nodes (includes text)
element.firstChild;        // First node
element.firstElementChild; // First element
element.lastChild;
element.lastElementChild;
element.nextSibling;
element.nextElementSibling;
element.previousSibling;
element.previousElementSibling;

// Closest ancestor
element.closest('.container'); // Finds nearest ancestor matching selector
```

---

## 📐 DOM Manipulation

```javascript
// Creating elements
const div = document.createElement('div');
const text = document.createTextNode('Hello');
const fragment = document.createDocumentFragment();

// Modifying content
element.textContent = 'Plain text';     // Text only (safer)
element.innerHTML = '<b>HTML</b>';       // Parses HTML (XSS risk)
element.outerHTML = '<span>New</span>';  // Replaces element entirely

// Attributes
element.getAttribute('class');
element.setAttribute('class', 'active');
element.removeAttribute('class');
element.hasAttribute('class');
element.toggleAttribute('disabled');

// Data attributes
// <div data-user-id="123" data-active="true">
element.dataset.userId;  // "123"
element.dataset.active;  // "true"

// Classes
element.className = 'one two';
element.classList.add('active');
element.classList.remove('active');
element.classList.toggle('active');
element.classList.toggle('active', condition); // Force state
element.classList.contains('active');
element.classList.replace('old', 'new');

// Styles
element.style.color = 'red';
element.style.backgroundColor = 'blue';
element.style.cssText = 'color: red; font-size: 14px;';

// Get computed style
const computed = getComputedStyle(element);
computed.color;      // Actual color
computed.getPropertyValue('color');

// Adding to DOM
parent.appendChild(child);
parent.insertBefore(newNode, referenceNode);
parent.append(child1, child2, 'text');      // Multiple items
parent.prepend(child);
element.after(sibling);
element.before(sibling);

// Removing
parent.removeChild(child);
element.remove();

// Replacing
parent.replaceChild(newChild, oldChild);
element.replaceWith(newElement);

// Cloning
const clone = element.cloneNode(false); // Shallow
const deepClone = element.cloneNode(true); // Deep (includes children)
```

---

## 🎪 Event Propagation

```javascript
/*
EVENT PHASES:

1. CAPTURE PHASE (Window → Target)
   Event travels down from window to target

2. TARGET PHASE
   Event reaches the target element

3. BUBBLE PHASE (Target → Window)
   Event bubbles up from target to window

         ┌──────────────── Window ────────────────┐
         │                    │                    │
         │    ┌─────────── document ───────────┐   │
         │    │               │                │   │
         │    │    ┌─────── body ───────┐      │   │
         │    │    │          │         │      │   │
         │    │    │   ┌── parent ──┐   │      │   │
         │    │    │   │     │      │   │      │   │
         │    │    │   │  target    │   │      │   │
         │    │    │   │     │      │   │      │   │
         │    │    │   └──── │ ─────┘   │      │   │
         │    │    │         │          │      │   │
         │    │    └──────── │ ─────────┘      │   │
         │    │              │                 │   │
         │    └────────────  │  ───────────────┘   │
         │                   │                     │
         └───────────────────│─────────────────────┘
                   CAPTURE ↓ │ ↑ BUBBLE
*/

// Event listener with capture
element.addEventListener('click', handler, true);        // Capture
element.addEventListener('click', handler, false);       // Bubble (default)
element.addEventListener('click', handler, {
    capture: true,
    once: true,     // Remove after first call
    passive: true   // Won't call preventDefault()
});

// Example: Capture vs Bubble
document.getElementById('outer').addEventListener('click', () => {
    console.log('outer bubble');
}, false);

document.getElementById('outer').addEventListener('click', () => {
    console.log('outer capture');
}, true);

document.getElementById('inner').addEventListener('click', () => {
    console.log('inner bubble');
}, false);

document.getElementById('inner').addEventListener('click', () => {
    console.log('inner capture');
}, true);

// Click on inner:
// 1. "outer capture"
// 2. "inner capture"
// 3. "inner bubble"
// 4. "outer bubble"
```

### Stopping Propagation

```javascript
element.addEventListener('click', (e) => {
    e.stopPropagation();  // Stops event from propagating
    // Other listeners on same element still fire
});

element.addEventListener('click', (e) => {
    e.stopImmediatePropagation();  // Stops completely
    // No other listeners fire, even on same element
});

// Event object properties
element.addEventListener('click', (e) => {
    e.target;          // Element that triggered event
    e.currentTarget;   // Element with the listener
    e.type;            // 'click'
    e.eventPhase;      // 1=capture, 2=target, 3=bubble
    e.bubbles;         // true/false
    e.cancelable;      // Can use preventDefault()?
    e.timeStamp;       // When event occurred
    e.isTrusted;       // true if user initiated
});
```

---

## 🎯 Event Delegation

Instead of attaching listeners to many elements, attach one to a parent.

```javascript
// ❌ Bad: Many listeners
document.querySelectorAll('.button').forEach(btn => {
    btn.addEventListener('click', handleClick);
});

// ✅ Good: One listener (delegation)
document.getElementById('buttons').addEventListener('click', (e) => {
    if (e.target.matches('.button')) {
        handleClick(e);
    }
});

// Practical example: Dynamic list
const todoList = document.getElementById('todo-list');

todoList.addEventListener('click', (e) => {
    // Handle different actions
    if (e.target.matches('.delete-btn')) {
        const item = e.target.closest('.todo-item');
        item.remove();
    }
    
    if (e.target.matches('.checkbox')) {
        const item = e.target.closest('.todo-item');
        item.classList.toggle('completed');
    }
});

// Works even for dynamically added items!
function addTodo(text) {
    const li = document.createElement('li');
    li.className = 'todo-item';
    li.innerHTML = `
        <input type="checkbox" class="checkbox">
        <span>${text}</span>
        <button class="delete-btn">Delete</button>
    `;
    todoList.appendChild(li);
}

// Delegation helper function
function delegate(parent, selector, event, handler) {
    parent.addEventListener(event, (e) => {
        const target = e.target.closest(selector);
        if (target && parent.contains(target)) {
            handler.call(target, e);
        }
    });
}

// Usage
delegate(document.body, '.button', 'click', function(e) {
    console.log('Button clicked:', this);
});
```

---

## 🎨 Custom Events

```javascript
// Creating custom events
const event = new Event('build');

// With data
const customEvent = new CustomEvent('userLogin', {
    detail: { userId: 123, username: 'john' },
    bubbles: true,
    cancelable: true
});

// Dispatching
element.dispatchEvent(event);
element.dispatchEvent(customEvent);

// Listening
element.addEventListener('userLogin', (e) => {
    console.log('User logged in:', e.detail.username);
});

// Practical example: Component communication
class NotificationSystem {
    constructor() {
        this.container = document.getElementById('notifications');
        
        // Listen for custom events
        document.addEventListener('notify', this.handleNotify.bind(this));
    }
    
    handleNotify(e) {
        const { message, type } = e.detail;
        this.show(message, type);
    }
    
    show(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        this.container.appendChild(notification);
        
        setTimeout(() => notification.remove(), 3000);
    }
}

// Anywhere in your app:
function notify(message, type) {
    document.dispatchEvent(new CustomEvent('notify', {
        detail: { message, type }
    }));
}

notify('Saved successfully!', 'success');
notify('Something went wrong', 'error');

// EventTarget class for custom objects
class EventEmitter extends EventTarget {
    emit(type, data) {
        this.dispatchEvent(new CustomEvent(type, { detail: data }));
    }
}

const emitter = new EventEmitter();
emitter.addEventListener('message', e => console.log(e.detail));
emitter.emit('message', 'Hello!');
```

---

## 🔥 Common Event Types

```javascript
// Mouse Events
element.addEventListener('click', handler);
element.addEventListener('dblclick', handler);
element.addEventListener('mousedown', handler);
element.addEventListener('mouseup', handler);
element.addEventListener('mousemove', (e) => {
    console.log(e.clientX, e.clientY); // Viewport coords
    console.log(e.pageX, e.pageY);     // Document coords
    console.log(e.offsetX, e.offsetY); // Element coords
});
element.addEventListener('mouseenter', handler); // No bubble
element.addEventListener('mouseleave', handler); // No bubble
element.addEventListener('mouseover', handler);  // Bubbles
element.addEventListener('mouseout', handler);   // Bubbles

// Keyboard Events
element.addEventListener('keydown', (e) => {
    console.log(e.key);      // 'a', 'Enter', 'Escape'
    console.log(e.code);     // 'KeyA', 'Enter', 'Escape'
    console.log(e.ctrlKey);  // true/false
    console.log(e.shiftKey);
    console.log(e.altKey);
    console.log(e.metaKey);  // Command on Mac
});
element.addEventListener('keyup', handler);
element.addEventListener('keypress', handler); // Deprecated

// Form Events
form.addEventListener('submit', (e) => {
    e.preventDefault();
    const data = new FormData(form);
});
input.addEventListener('input', handler);     // Every change
input.addEventListener('change', handler);    // On blur
input.addEventListener('focus', handler);
input.addEventListener('blur', handler);
input.addEventListener('invalid', handler);

// Focus Events (bubble)
element.addEventListener('focusin', handler);
element.addEventListener('focusout', handler);

// Drag Events
element.addEventListener('drag', handler);
element.addEventListener('dragstart', (e) => {
    e.dataTransfer.setData('text/plain', 'data');
});
element.addEventListener('dragend', handler);
element.addEventListener('dragenter', handler);
element.addEventListener('dragleave', handler);
element.addEventListener('dragover', (e) => {
    e.preventDefault(); // Required to allow drop
});
element.addEventListener('drop', (e) => {
    const data = e.dataTransfer.getData('text/plain');
});

// Scroll Events
element.addEventListener('scroll', (e) => {
    console.log(element.scrollTop, element.scrollLeft);
});

// Touch Events (mobile)
element.addEventListener('touchstart', (e) => {
    const touch = e.touches[0];
    console.log(touch.clientX, touch.clientY);
});
element.addEventListener('touchmove', handler);
element.addEventListener('touchend', handler);
element.addEventListener('touchcancel', handler);
```

---

## ⚡ DOM Performance

```javascript
// 1. Batch DOM operations
// ❌ Bad: Multiple reflows
const list = document.getElementById('list');
for (let i = 0; i < 100; i++) {
    list.innerHTML += `<li>Item ${i}</li>`; // Causes reflow each time
}

// ✅ Good: DocumentFragment
const fragment = document.createDocumentFragment();
for (let i = 0; i < 100; i++) {
    const li = document.createElement('li');
    li.textContent = `Item ${i}`;
    fragment.appendChild(li);
}
list.appendChild(fragment); // Single reflow

// ✅ Also Good: Build string first
let html = '';
for (let i = 0; i < 100; i++) {
    html += `<li>Item ${i}</li>`;
}
list.innerHTML = html; // Single reflow

// 2. Avoid layout thrashing
// ❌ Bad: Interleaved read/write
elements.forEach(el => {
    const width = el.offsetWidth;  // Read (forces layout)
    el.style.width = width + 10 + 'px';  // Write
});

// ✅ Good: Batch reads, then writes
const widths = elements.map(el => el.offsetWidth); // All reads
elements.forEach((el, i) => {
    el.style.width = widths[i] + 10 + 'px';  // All writes
});

// 3. Use requestAnimationFrame for visual changes
function animate() {
    element.style.transform = `translateX(${x}px)`;
    x += 1;
    if (x < 100) {
        requestAnimationFrame(animate);
    }
}
requestAnimationFrame(animate);

// 4. Avoid expensive selectors
// ❌ Complex selectors
document.querySelectorAll('div.container > ul li:nth-child(odd) span');

// ✅ Simple selectors + traversal
const items = document.querySelectorAll('.item');

// 5. Cache DOM references
// ❌ Multiple lookups
function update() {
    document.getElementById('count').textContent = count;
    document.getElementById('count').style.color = 'red';
}

// ✅ Cache reference
const countEl = document.getElementById('count');
function update() {
    countEl.textContent = count;
    countEl.style.color = 'red';
}

// 6. Use passive event listeners for scroll/touch
element.addEventListener('scroll', handler, { passive: true });
element.addEventListener('touchstart', handler, { passive: true });
```

---

## ✅ Day 17 Checklist

- [ ] Understand DOM tree structure
- [ ] Know all element selection methods
- [ ] Know HTMLCollection vs NodeList
- [ ] Master element traversal
- [ ] Understand event phases
- [ ] Implement event delegation
- [ ] Create and dispatch custom events
- [ ] Know common event types and properties
- [ ] Stop propagation vs stopImmediatePropagation
- [ ] Optimize DOM performance
- [ ] Use DocumentFragment
- [ ] Avoid layout thrashing
