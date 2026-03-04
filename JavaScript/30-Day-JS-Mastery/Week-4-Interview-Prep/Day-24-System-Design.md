# Day 24: System Design for Frontend

## 🎯 Learning Objectives
- Understand frontend system design concepts
- Learn component architecture patterns
- Master state management strategies
- Design scalable frontend applications

---

## 🏗️ System Design Framework

```
╔════════════════════════════════════════════════════════════════════╗
║                   FRONTEND SYSTEM DESIGN STEPS                      ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  1. REQUIREMENTS CLARIFICATION                                      ║
║     • Functional requirements (what it does)                        ║
║     • Non-functional requirements (performance, scale)              ║
║     • Edge cases and constraints                                    ║
║                                                                     ║
║  2. HIGH-LEVEL DESIGN                                               ║
║     • Component breakdown                                           ║
║     • Data flow                                                     ║
║     • API design                                                    ║
║                                                                     ║
║  3. DETAILED DESIGN                                                 ║
║     • State management                                              ║
║     • Component interactions                                        ║
║     • Error handling                                                ║
║                                                                     ║
║  4. OPTIMIZATION                                                    ║
║     • Performance optimization                                      ║
║     • Caching strategies                                            ║
║     • Accessibility                                                 ║
║                                                                     ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## 📱 Design: Autocomplete/Typeahead

### Requirements
- Show suggestions as user types
- Handle keyboard navigation
- Support mouse selection
- Handle network latency
- Recent searches
- Highlight matching text

### Component Structure

```javascript
/*
┌─────────────────────────────────────────────────┐
│              AutocompleteContainer               │
├─────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────┐  │
│  │           SearchInput                      │  │
│  │  [Search...                          🔍 ] │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │           SuggestionsList                 │  │
│  │  ┌─────────────────────────────────────┐  │  │
│  │  │ • Suggestion Item (highlighted)     │  │  │
│  │  ├─────────────────────────────────────┤  │  │
│  │  │ • Suggestion Item                   │  │  │
│  │  ├─────────────────────────────────────┤  │  │
│  │  │ • Suggestion Item                   │  │  │
│  │  └─────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
*/
```

### Implementation

```javascript
class Autocomplete {
    constructor(options) {
        this.input = options.input;
        this.fetchSuggestions = options.fetchSuggestions;
        this.minChars = options.minChars || 2;
        this.debounceTime = options.debounceTime || 300;
        this.maxSuggestions = options.maxSuggestions || 10;
        
        this.state = {
            query: '',
            suggestions: [],
            selectedIndex: -1,
            isOpen: false,
            isLoading: false,
            cache: new Map()
        };
        
        this.init();
    }
    
    init() {
        this.createDropdown();
        this.bindEvents();
    }
    
    createDropdown() {
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'autocomplete-dropdown';
        this.dropdown.style.display = 'none';
        this.input.parentNode.appendChild(this.dropdown);
    }
    
    bindEvents() {
        // Debounced input handler
        this.input.addEventListener('input', this.debounce(
            this.handleInput.bind(this),
            this.debounceTime
        ));
        
        // Keyboard navigation
        this.input.addEventListener('keydown', this.handleKeydown.bind(this));
        
        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.dropdown.contains(e.target)) {
                this.close();
            }
        });
        
        // Focus handling
        this.input.addEventListener('focus', () => {
            if (this.state.suggestions.length > 0) {
                this.open();
            }
        });
    }
    
    async handleInput(e) {
        const query = e.target.value.trim();
        this.state.query = query;
        
        if (query.length < this.minChars) {
            this.close();
            return;
        }
        
        // Check cache first
        if (this.state.cache.has(query)) {
            this.renderSuggestions(this.state.cache.get(query));
            return;
        }
        
        this.state.isLoading = true;
        this.showLoading();
        
        try {
            const suggestions = await this.fetchSuggestions(query);
            
            // Cache the results
            this.state.cache.set(query, suggestions);
            
            // Only render if query hasn't changed
            if (this.state.query === query) {
                this.renderSuggestions(suggestions);
            }
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.state.isLoading = false;
        }
    }
    
    handleKeydown(e) {
        const { suggestions, selectedIndex, isOpen } = this.state;
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                if (!isOpen && suggestions.length) {
                    this.open();
                } else {
                    this.selectIndex(
                        Math.min(selectedIndex + 1, suggestions.length - 1)
                    );
                }
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.selectIndex(Math.max(selectedIndex - 1, 0));
                break;
                
            case 'Enter':
                if (isOpen && selectedIndex >= 0) {
                    e.preventDefault();
                    this.selectSuggestion(suggestions[selectedIndex]);
                }
                break;
                
            case 'Escape':
                this.close();
                break;
        }
    }
    
    selectIndex(index) {
        this.state.selectedIndex = index;
        this.updateSelection();
    }
    
    selectSuggestion(suggestion) {
        this.input.value = suggestion.text;
        this.close();
        this.input.dispatchEvent(new CustomEvent('suggestion-selected', {
            detail: suggestion
        }));
    }
    
    renderSuggestions(suggestions) {
        this.state.suggestions = suggestions.slice(0, this.maxSuggestions);
        this.state.selectedIndex = -1;
        
        if (suggestions.length === 0) {
            this.dropdown.innerHTML = '<div class="no-results">No results found</div>';
        } else {
            this.dropdown.innerHTML = suggestions.map((s, i) => `
                <div class="suggestion-item" data-index="${i}">
                    ${this.highlightMatch(s.text, this.state.query)}
                </div>
            `).join('');
            
            // Add click handlers
            this.dropdown.querySelectorAll('.suggestion-item').forEach(item => {
                item.addEventListener('click', () => {
                    const index = parseInt(item.dataset.index);
                    this.selectSuggestion(suggestions[index]);
                });
            });
        }
        
        this.open();
    }
    
    highlightMatch(text, query) {
        const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
    
    updateSelection() {
        const items = this.dropdown.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            item.classList.toggle('selected', index === this.state.selectedIndex);
        });
    }
    
    open() {
        this.state.isOpen = true;
        this.dropdown.style.display = 'block';
    }
    
    close() {
        this.state.isOpen = false;
        this.dropdown.style.display = 'none';
        this.state.selectedIndex = -1;
    }
    
    showLoading() {
        this.dropdown.innerHTML = '<div class="loading">Loading...</div>';
        this.open();
    }
    
    showError(message) {
        this.dropdown.innerHTML = `<div class="error">${message}</div>`;
        this.open();
    }
    
    debounce(fn, delay) {
        let timeoutId;
        return (...args) => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => fn(...args), delay);
        };
    }
}
```

---

## 📜 Design: Infinite Scroll

### Requirements
- Load more content on scroll
- Handle loading states
- Support different content types
- Virtual scrolling for large lists
- Error recovery

### Implementation

```javascript
class InfiniteScroll {
    constructor(options) {
        this.container = options.container;
        this.fetchItems = options.fetchItems;
        this.renderItem = options.renderItem;
        this.threshold = options.threshold || 200;
        this.pageSize = options.pageSize || 20;
        
        this.state = {
            items: [],
            page: 1,
            hasMore: true,
            isLoading: false,
            error: null
        };
        
        this.init();
    }
    
    init() {
        this.itemsContainer = document.createElement('div');
        this.itemsContainer.className = 'items-container';
        this.container.appendChild(this.itemsContainer);
        
        this.sentinel = document.createElement('div');
        this.sentinel.className = 'scroll-sentinel';
        this.container.appendChild(this.sentinel);
        
        this.setupIntersectionObserver();
        this.loadMore();
    }
    
    setupIntersectionObserver() {
        this.observer = new IntersectionObserver(
            (entries) => {
                if (entries[0].isIntersecting && this.state.hasMore && !this.state.isLoading) {
                    this.loadMore();
                }
            },
            {
                root: null,
                rootMargin: `${this.threshold}px`,
                threshold: 0
            }
        );
        
        this.observer.observe(this.sentinel);
    }
    
    async loadMore() {
        if (this.state.isLoading || !this.state.hasMore) return;
        
        this.state.isLoading = true;
        this.showLoading();
        
        try {
            const newItems = await this.fetchItems(this.state.page, this.pageSize);
            
            this.state.items = [...this.state.items, ...newItems];
            this.state.hasMore = newItems.length === this.pageSize;
            this.state.page++;
            
            this.renderItems(newItems);
            this.hideLoading();
        } catch (error) {
            this.state.error = error;
            this.showError(error);
        } finally {
            this.state.isLoading = false;
        }
    }
    
    renderItems(items) {
        const fragment = document.createDocumentFragment();
        
        items.forEach(item => {
            const element = this.renderItem(item);
            fragment.appendChild(element);
        });
        
        this.itemsContainer.appendChild(fragment);
    }
    
    showLoading() {
        if (!this.loadingIndicator) {
            this.loadingIndicator = document.createElement('div');
            this.loadingIndicator.className = 'loading-indicator';
            this.loadingIndicator.textContent = 'Loading...';
        }
        this.container.insertBefore(this.loadingIndicator, this.sentinel);
    }
    
    hideLoading() {
        if (this.loadingIndicator && this.loadingIndicator.parentNode) {
            this.loadingIndicator.remove();
        }
    }
    
    showError(error) {
        const errorEl = document.createElement('div');
        errorEl.className = 'error-message';
        errorEl.innerHTML = `
            <p>Error loading items: ${error.message}</p>
            <button class="retry-btn">Retry</button>
        `;
        
        errorEl.querySelector('.retry-btn').addEventListener('click', () => {
            errorEl.remove();
            this.state.error = null;
            this.loadMore();
        });
        
        this.container.insertBefore(errorEl, this.sentinel);
    }
    
    destroy() {
        this.observer.disconnect();
        this.container.innerHTML = '';
    }
}

// Virtual scrolling for large lists
class VirtualScroll {
    constructor(options) {
        this.container = options.container;
        this.items = options.items;
        this.itemHeight = options.itemHeight;
        this.renderItem = options.renderItem;
        this.bufferSize = options.bufferSize || 5;
        
        this.init();
    }
    
    init() {
        this.viewport = document.createElement('div');
        this.viewport.className = 'virtual-viewport';
        this.viewport.style.height = '100%';
        this.viewport.style.overflow = 'auto';
        
        this.content = document.createElement('div');
        this.content.className = 'virtual-content';
        this.content.style.height = `${this.items.length * this.itemHeight}px`;
        this.content.style.position = 'relative';
        
        this.viewport.appendChild(this.content);
        this.container.appendChild(this.viewport);
        
        this.viewport.addEventListener('scroll', this.handleScroll.bind(this));
        this.render();
    }
    
    handleScroll() {
        requestAnimationFrame(() => this.render());
    }
    
    render() {
        const scrollTop = this.viewport.scrollTop;
        const viewportHeight = this.viewport.clientHeight;
        
        const startIndex = Math.max(0, Math.floor(scrollTop / this.itemHeight) - this.bufferSize);
        const endIndex = Math.min(
            this.items.length,
            Math.ceil((scrollTop + viewportHeight) / this.itemHeight) + this.bufferSize
        );
        
        const visibleItems = this.items.slice(startIndex, endIndex);
        
        this.content.innerHTML = '';
        
        visibleItems.forEach((item, i) => {
            const element = this.renderItem(item);
            element.style.position = 'absolute';
            element.style.top = `${(startIndex + i) * this.itemHeight}px`;
            element.style.height = `${this.itemHeight}px`;
            this.content.appendChild(element);
        });
    }
}
```

---

## 💬 Design: Real-time Chat

### Requirements
- Send/receive messages
- Typing indicators
- Read receipts
- Offline support
- Message history

### Architecture

```javascript
/*
┌────────────────────────────────────────────────────────────┐
│                    Chat Application                         │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   ChatList   │    │   ChatRoom   │    │  MessageBox  │  │
│  │              │    │              │    │              │  │
│  │  [User 1   ]│───►│  Messages    │    │  [Type msg  │  │
│  │  [User 2   ]│    │  ────────    │    │   and send] │  │
│  │  [User 3   ]│    │  ────────    │    │  [Send Btn] │  │
│  │             │    │  ────────    │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
├────────────────────────────────────────────────────────────┤
│                    State Management                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  { currentUser, activeChat, messages, users, ... }    │  │
│  └──────────────────────────────────────────────────────┘  │
├────────────────────────────────────────────────────────────┤
│                    Services Layer                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  WebSocket  │  │   Storage   │  │  Message Queue     │ │
│  │   Service   │  │   Service   │  │  (offline support) │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└────────────────────────────────────────────────────────────┘
*/

class ChatService {
    constructor(userId) {
        this.userId = userId;
        this.ws = null;
        this.messageQueue = [];
        this.handlers = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        this.connect();
    }
    
    connect() {
        this.ws = new WebSocket('wss://chat.example.com');
        
        this.ws.onopen = () => {
            console.log('Connected');
            this.reconnectAttempts = 0;
            this.flushMessageQueue();
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };
        
        this.ws.onclose = () => {
            this.attemptReconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.pow(2, this.reconnectAttempts) * 1000;
            setTimeout(() => this.connect(), delay);
        }
    }
    
    send(type, payload) {
        const message = { type, payload, timestamp: Date.now() };
        
        if (this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(message));
        } else {
            this.messageQueue.push(message);
            this.saveToLocalStorage();
        }
    }
    
    flushMessageQueue() {
        while (this.messageQueue.length > 0) {
            const message = this.messageQueue.shift();
            this.ws.send(JSON.stringify(message));
        }
    }
    
    handleMessage(data) {
        const handlers = this.handlers.get(data.type) || [];
        handlers.forEach(handler => handler(data.payload));
    }
    
    on(type, handler) {
        if (!this.handlers.has(type)) {
            this.handlers.set(type, []);
        }
        this.handlers.get(type).push(handler);
    }
    
    sendMessage(chatId, text) {
        this.send('message', {
            chatId,
            text,
            senderId: this.userId,
            id: this.generateId()
        });
    }
    
    sendTyping(chatId, isTyping) {
        this.send('typing', { chatId, isTyping });
    }
    
    markAsRead(chatId, messageId) {
        this.send('read', { chatId, messageId });
    }
    
    generateId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }
    
    saveToLocalStorage() {
        localStorage.setItem('chatMessageQueue', JSON.stringify(this.messageQueue));
    }
    
    loadFromLocalStorage() {
        const saved = localStorage.getItem('chatMessageQueue');
        if (saved) {
            this.messageQueue = JSON.parse(saved);
        }
    }
}
```

---

## 📊 Design: Dashboard with Widgets

### Requirements
- Draggable/resizable widgets
- Customizable layout
- Real-time data updates
- Responsive design

### Implementation

```javascript
class Dashboard {
    constructor(container, options = {}) {
        this.container = container;
        this.columns = options.columns || 12;
        this.rowHeight = options.rowHeight || 50;
        this.widgets = new Map();
        this.layout = options.layout || [];
        
        this.init();
    }
    
    init() {
        this.grid = document.createElement('div');
        this.grid.className = 'dashboard-grid';
        this.grid.style.cssText = `
            display: grid;
            grid-template-columns: repeat(${this.columns}, 1fr);
            grid-auto-rows: ${this.rowHeight}px;
            gap: 10px;
        `;
        this.container.appendChild(this.grid);
        
        this.loadLayout();
    }
    
    addWidget(config) {
        const widget = new Widget(config, this);
        this.widgets.set(config.id, widget);
        this.grid.appendChild(widget.element);
        this.layout.push(config);
        this.saveLayout();
    }
    
    removeWidget(id) {
        const widget = this.widgets.get(id);
        if (widget) {
            widget.destroy();
            this.widgets.delete(id);
            this.layout = this.layout.filter(w => w.id !== id);
            this.saveLayout();
        }
    }
    
    moveWidget(id, newPosition) {
        const config = this.layout.find(w => w.id === id);
        if (config) {
            Object.assign(config, newPosition);
            const widget = this.widgets.get(id);
            widget.updatePosition(newPosition);
            this.saveLayout();
        }
    }
    
    saveLayout() {
        localStorage.setItem('dashboardLayout', JSON.stringify(this.layout));
    }
    
    loadLayout() {
        const saved = localStorage.getItem('dashboardLayout');
        if (saved) {
            const layout = JSON.parse(saved);
            layout.forEach(config => this.addWidget(config));
        }
    }
}

class Widget {
    constructor(config, dashboard) {
        this.id = config.id;
        this.config = config;
        this.dashboard = dashboard;
        
        this.createElement();
        this.setupDragAndDrop();
        this.loadData();
    }
    
    createElement() {
        this.element = document.createElement('div');
        this.element.className = 'widget';
        this.element.id = this.id;
        this.element.style.cssText = `
            grid-column: ${this.config.col} / span ${this.config.width};
            grid-row: ${this.config.row} / span ${this.config.height};
        `;
        
        this.element.innerHTML = `
            <div class="widget-header">
                <h3>${this.config.title}</h3>
                <div class="widget-actions">
                    <button class="refresh-btn">↻</button>
                    <button class="remove-btn">×</button>
                </div>
            </div>
            <div class="widget-content"></div>
        `;
        
        this.content = this.element.querySelector('.widget-content');
        
        this.element.querySelector('.remove-btn').addEventListener('click', () => {
            this.dashboard.removeWidget(this.id);
        });
        
        this.element.querySelector('.refresh-btn').addEventListener('click', () => {
            this.loadData();
        });
    }
    
    setupDragAndDrop() {
        this.element.draggable = true;
        
        this.element.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', this.id);
            this.element.classList.add('dragging');
        });
        
        this.element.addEventListener('dragend', () => {
            this.element.classList.remove('dragging');
        });
    }
    
    async loadData() {
        this.content.innerHTML = '<div class="loading">Loading...</div>';
        
        try {
            const data = await this.config.fetchData();
            this.render(data);
        } catch (error) {
            this.content.innerHTML = `<div class="error">${error.message}</div>`;
        }
    }
    
    render(data) {
        this.config.render(this.content, data);
    }
    
    updatePosition(position) {
        this.element.style.gridColumn = `${position.col} / span ${position.width}`;
        this.element.style.gridRow = `${position.row} / span ${position.height}`;
    }
    
    destroy() {
        this.element.remove();
    }
}
```

---

## 🔑 Key Design Patterns

### State Management

```javascript
// Simple state management
class Store {
    constructor(initialState = {}) {
        this.state = initialState;
        this.listeners = [];
    }
    
    getState() {
        return this.state;
    }
    
    setState(newState) {
        this.state = { ...this.state, ...newState };
        this.notify();
    }
    
    subscribe(listener) {
        this.listeners.push(listener);
        return () => {
            this.listeners = this.listeners.filter(l => l !== listener);
        };
    }
    
    notify() {
        this.listeners.forEach(listener => listener(this.state));
    }
}

// Redux-like pattern
function createStore(reducer, initialState) {
    let state = initialState;
    const listeners = [];
    
    return {
        getState: () => state,
        dispatch: (action) => {
            state = reducer(state, action);
            listeners.forEach(l => l());
        },
        subscribe: (listener) => {
            listeners.push(listener);
            return () => listeners.splice(listeners.indexOf(listener), 1);
        }
    };
}
```

---

## ✅ Day 24 Checklist

- [ ] Understand FE system design framework
- [ ] Design autocomplete component
- [ ] Implement infinite scroll
- [ ] Design real-time chat architecture
- [ ] Create dashboard widget system
- [ ] Implement virtual scrolling
- [ ] Handle offline support
- [ ] Design state management
- [ ] Consider accessibility
- [ ] Handle error states
