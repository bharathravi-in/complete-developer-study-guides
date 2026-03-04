# Day 18: Design Patterns

## 🎯 Learning Objectives
- Understand common design patterns
- Implement Singleton, Factory, Observer, Module, Pub/Sub
- Learn when to apply each pattern
- Recognize patterns in real-world code

---

## 🏭 Creational Patterns

### Singleton Pattern

Ensures only one instance of a class exists.

```javascript
// Basic Singleton
class Database {
    static instance = null;
    
    constructor(connectionString) {
        if (Database.instance) {
            return Database.instance;
        }
        
        this.connectionString = connectionString;
        this.connection = null;
        Database.instance = this;
    }
    
    connect() {
        if (!this.connection) {
            this.connection = `Connected to ${this.connectionString}`;
        }
        return this.connection;
    }
}

const db1 = new Database('mysql://localhost');
const db2 = new Database('postgres://localhost');

console.log(db1 === db2); // true
console.log(db2.connectionString); // 'mysql://localhost' (first one)

// Module-based Singleton (more idiomatic JS)
const Logger = (() => {
    let instance;
    
    function createInstance() {
        return {
            logs: [],
            log(message) {
                const entry = `[${new Date().toISOString()}] ${message}`;
                this.logs.push(entry);
                console.log(entry);
            },
            getLogs() {
                return this.logs;
            }
        };
    }
    
    return {
        getInstance() {
            if (!instance) {
                instance = createInstance();
            }
            return instance;
        }
    };
})();

const logger1 = Logger.getInstance();
const logger2 = Logger.getInstance();
console.log(logger1 === logger2); // true

// ES Module Singleton (simplest approach)
// config.js
class Config {
    constructor() {
        this.settings = {};
    }
    
    set(key, value) {
        this.settings[key] = value;
    }
    
    get(key) {
        return this.settings[key];
    }
}

// Modules are singletons by default
export default new Config();

// Usage anywhere:
import config from './config.js';
config.set('apiUrl', 'https://api.example.com');
```

### Factory Pattern

Creates objects without specifying the exact class.

```javascript
// Simple Factory
class Car {
    constructor(type) {
        this.type = type;
    }
    drive() { console.log(`Driving ${this.type}`); }
}

class Truck {
    constructor(type) {
        this.type = type;
    }
    drive() { console.log(`Driving ${this.type}`); }
}

class VehicleFactory {
    static create(type) {
        switch (type) {
            case 'car':
                return new Car(type);
            case 'truck':
                return new Truck(type);
            default:
                throw new Error(`Unknown vehicle type: ${type}`);
        }
    }
}

const car = VehicleFactory.create('car');
const truck = VehicleFactory.create('truck');

// Factory Function (more common in JS)
function createUser(type, data) {
    const base = {
        id: Date.now(),
        createdAt: new Date(),
        ...data
    };
    
    switch (type) {
        case 'admin':
            return {
                ...base,
                role: 'admin',
                permissions: ['read', 'write', 'delete', 'admin'],
                canManageUsers: true
            };
        case 'editor':
            return {
                ...base,
                role: 'editor',
                permissions: ['read', 'write'],
                canPublish: true
            };
        case 'viewer':
            return {
                ...base,
                role: 'viewer',
                permissions: ['read']
            };
        default:
            throw new Error(`Unknown user type: ${type}`);
    }
}

const admin = createUser('admin', { name: 'John' });
const editor = createUser('editor', { name: 'Jane' });

// Abstract Factory
function createUIKit(theme) {
    const themes = {
        light: {
            createButton: (text) => `<button style="bg: white">${text}</button>`,
            createInput: () => '<input style="bg: #f0f0f0">',
            createCard: (content) => `<div style="bg: white">${content}</div>`
        },
        dark: {
            createButton: (text) => `<button style="bg: #333">${text}</button>`,
            createInput: () => '<input style="bg: #444">',
            createCard: (content) => `<div style="bg: #222">${content}</div>`
        }
    };
    
    return themes[theme] || themes.light;
}

const darkUI = createUIKit('dark');
darkUI.createButton('Submit');
darkUI.createInput();
```

### Builder Pattern

Constructs complex objects step by step.

```javascript
class QueryBuilder {
    constructor() {
        this.table = '';
        this.conditions = [];
        this.columns = ['*'];
        this.orderByClause = '';
        this.limitValue = null;
    }
    
    select(...columns) {
        this.columns = columns.length ? columns : ['*'];
        return this;
    }
    
    from(table) {
        this.table = table;
        return this;
    }
    
    where(condition) {
        this.conditions.push(condition);
        return this;
    }
    
    orderBy(column, direction = 'ASC') {
        this.orderByClause = `ORDER BY ${column} ${direction}`;
        return this;
    }
    
    limit(n) {
        this.limitValue = n;
        return this;
    }
    
    build() {
        let sql = `SELECT ${this.columns.join(', ')} FROM ${this.table}`;
        
        if (this.conditions.length) {
            sql += ` WHERE ${this.conditions.join(' AND ')}`;
        }
        
        if (this.orderByClause) {
            sql += ` ${this.orderByClause}`;
        }
        
        if (this.limitValue) {
            sql += ` LIMIT ${this.limitValue}`;
        }
        
        return sql;
    }
}

const query = new QueryBuilder()
    .select('id', 'name', 'email')
    .from('users')
    .where('active = 1')
    .where("role = 'admin'")
    .orderBy('name')
    .limit(10)
    .build();

// SELECT id, name, email FROM users WHERE active = 1 AND role = 'admin' ORDER BY name ASC LIMIT 10
```

---

## 📦 Structural Patterns

### Module Pattern

Encapsulates private data and exposes a public API.

```javascript
// IIFE Module
const Calculator = (function() {
    // Private data
    let result = 0;
    
    // Private function
    function validate(n) {
        if (typeof n !== 'number') {
            throw new Error('Invalid number');
        }
    }
    
    // Public API
    return {
        add(n) {
            validate(n);
            result += n;
            return this;
        },
        subtract(n) {
            validate(n);
            result -= n;
            return this;
        },
        getResult() {
            return result;
        },
        reset() {
            result = 0;
            return this;
        }
    };
})();

Calculator.add(5).add(10).subtract(3);
console.log(Calculator.getResult()); // 12
console.log(Calculator.result);      // undefined (private)

// Revealing Module Pattern
const ShoppingCart = (function() {
    const items = [];
    let total = 0;
    
    function calculateTotal() {
        total = items.reduce((sum, item) => sum + item.price * item.qty, 0);
    }
    
    function addItem(item) {
        items.push(item);
        calculateTotal();
    }
    
    function removeItem(id) {
        const index = items.findIndex(item => item.id === id);
        if (index > -1) {
            items.splice(index, 1);
            calculateTotal();
        }
    }
    
    function getItems() {
        return [...items]; // Return copy
    }
    
    function getTotal() {
        return total;
    }
    
    // Reveal only what we want
    return {
        addItem,
        removeItem,
        getItems,
        getTotal
    };
})();

// ES Modules (modern approach)
// cart.js
const items = [];
let total = 0;

export function addItem(item) {
    items.push(item);
    total += item.price * item.qty;
}

export function getTotal() {
    return total;
}

// items is private to this module
```

### Proxy Pattern

Provides a surrogate for another object.

```javascript
// Validation Proxy
function createValidatedUser(user) {
    return new Proxy(user, {
        set(target, property, value) {
            if (property === 'age') {
                if (typeof value !== 'number') {
                    throw new TypeError('Age must be a number');
                }
                if (value < 0 || value > 150) {
                    throw new RangeError('Age must be between 0 and 150');
                }
            }
            if (property === 'email') {
                if (!value.includes('@')) {
                    throw new Error('Invalid email');
                }
            }
            target[property] = value;
            return true;
        }
    });
}

const user = createValidatedUser({});
user.age = 25;      // OK
// user.age = -5;   // RangeError
// user.email = 'bad'; // Error

// Caching Proxy
function createCachingProxy(target) {
    const cache = new Map();
    
    return new Proxy(target, {
        apply(targetFn, thisArg, args) {
            const key = JSON.stringify(args);
            
            if (cache.has(key)) {
                console.log('Cache hit');
                return cache.get(key);
            }
            
            console.log('Cache miss');
            const result = targetFn.apply(thisArg, args);
            cache.set(key, result);
            return result;
        }
    });
}

function expensiveOperation(n) {
    let result = 0;
    for (let i = 0; i < n * 1000000; i++) {
        result += i;
    }
    return result;
}

const cachedOperation = createCachingProxy(expensiveOperation);
cachedOperation(10); // Slow
cachedOperation(10); // Fast (cached)

// Logging Proxy
const loggingHandler = {
    get(target, property) {
        console.log(`Getting ${property}`);
        return target[property];
    },
    set(target, property, value) {
        console.log(`Setting ${property} = ${value}`);
        target[property] = value;
        return true;
    }
};

const trackedObject = new Proxy({}, loggingHandler);
trackedObject.name = 'John'; // Log: Setting name = John
trackedObject.name;          // Log: Getting name
```

---

## 🔔 Behavioral Patterns

### Observer Pattern

Defines a one-to-many dependency between objects.

```javascript
// Basic Observer
class Subject {
    constructor() {
        this.observers = [];
    }
    
    subscribe(observer) {
        this.observers.push(observer);
        return () => this.unsubscribe(observer);
    }
    
    unsubscribe(observer) {
        this.observers = this.observers.filter(obs => obs !== observer);
    }
    
    notify(data) {
        this.observers.forEach(observer => observer(data));
    }
}

const subscriber = new Subject();

const unsubscribe1 = subscriber.subscribe(data => {
    console.log('Observer 1:', data);
});

const unsubscribe2 = subscriber.subscribe(data => {
    console.log('Observer 2:', data);
});

subscriber.notify('Hello!');
// Observer 1: Hello!
// Observer 2: Hello!

unsubscribe1();
subscriber.notify('After unsubscribe');
// Observer 2: After unsubscribe

// Observable Class (more OOP style)
class EventEmitter {
    constructor() {
        this.events = {};
    }
    
    on(event, listener) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        this.events[event].push(listener);
        return this;
    }
    
    off(event, listener) {
        if (this.events[event]) {
            this.events[event] = this.events[event]
                .filter(l => l !== listener);
        }
        return this;
    }
    
    once(event, listener) {
        const wrapper = (...args) => {
            listener(...args);
            this.off(event, wrapper);
        };
        return this.on(event, wrapper);
    }
    
    emit(event, ...args) {
        if (this.events[event]) {
            this.events[event].forEach(listener => {
                listener(...args);
            });
        }
        return this;
    }
}

// Usage
class Stock extends EventEmitter {
    constructor(symbol, price) {
        super();
        this.symbol = symbol;
        this.price = price;
    }
    
    setPrice(newPrice) {
        const oldPrice = this.price;
        this.price = newPrice;
        
        if (newPrice !== oldPrice) {
            this.emit('priceChange', {
                symbol: this.symbol,
                oldPrice,
                newPrice,
                change: newPrice - oldPrice
            });
        }
    }
}

const apple = new Stock('AAPL', 150);

apple.on('priceChange', ({ symbol, oldPrice, newPrice, change }) => {
    console.log(`${symbol}: $${oldPrice} → $${newPrice} (${change > 0 ? '+' : ''}${change})`);
});

apple.setPrice(155);
// AAPL: $150 → $155 (+5)
```

### Pub/Sub Pattern

Decouples publishers and subscribers through a message broker.

```javascript
// Pub/Sub (more decoupled than Observer)
const PubSub = {
    events: {},
    
    subscribe(event, callback) {
        if (!this.events[event]) {
            this.events[event] = [];
        }
        
        const index = this.events[event].push(callback) - 1;
        
        // Return unsubscribe function
        return {
            unsubscribe: () => {
                this.events[event].splice(index, 1);
            }
        };
    },
    
    publish(event, data) {
        if (!this.events[event]) return [];
        
        return this.events[event].map(callback => callback(data));
    }
};

// Usage - components don't know about each other
// Component A (Publisher)
function saveUser(user) {
    // Save to database...
    PubSub.publish('user:saved', user);
}

// Component B (Subscriber)
const emailSubscription = PubSub.subscribe('user:saved', (user) => {
    console.log(`Sending welcome email to ${user.email}`);
});

// Component C (Subscriber)
const analyticsSubscription = PubSub.subscribe('user:saved', (user) => {
    console.log(`Tracking new user: ${user.id}`);
});

// Trigger
saveUser({ id: 1, email: 'test@test.com' });

// Type-safe Pub/Sub
class TypedPubSub {
    constructor() {
        this.subscribers = new Map();
    }
    
    subscribe(eventType, handler) {
        if (!this.subscribers.has(eventType)) {
            this.subscribers.set(eventType, new Set());
        }
        this.subscribers.get(eventType).add(handler);
        
        return () => {
            this.subscribers.get(eventType).delete(handler);
        };
    }
    
    publish(eventType, payload) {
        const handlers = this.subscribers.get(eventType);
        if (handlers) {
            handlers.forEach(handler => handler(payload));
        }
    }
}
```

### Strategy Pattern

Defines a family of algorithms and makes them interchangeable.

```javascript
// Payment strategies
const paymentStrategies = {
    creditCard: (amount, details) => {
        console.log(`Paying $${amount} with credit card ${details.cardNumber}`);
        return { success: true, method: 'creditCard' };
    },
    
    paypal: (amount, details) => {
        console.log(`Paying $${amount} with PayPal account ${details.email}`);
        return { success: true, method: 'paypal' };
    },
    
    crypto: (amount, details) => {
        console.log(`Paying $${amount} with crypto wallet ${details.wallet}`);
        return { success: true, method: 'crypto' };
    }
};

class PaymentProcessor {
    constructor(strategy) {
        this.strategy = strategy;
    }
    
    setStrategy(strategy) {
        this.strategy = strategy;
    }
    
    pay(amount, details) {
        return this.strategy(amount, details);
    }
}

const processor = new PaymentProcessor(paymentStrategies.creditCard);
processor.pay(100, { cardNumber: '1234-5678' });

processor.setStrategy(paymentStrategies.paypal);
processor.pay(50, { email: 'user@example.com' });

// Validation strategies
const validators = {
    required: (value) => value !== '' && value != null,
    email: (value) => /\S+@\S+\.\S+/.test(value),
    minLength: (min) => (value) => value.length >= min,
    maxLength: (max) => (value) => value.length <= max,
    pattern: (regex) => (value) => regex.test(value)
};

function validate(value, strategies) {
    for (const strategy of strategies) {
        if (!strategy(value)) {
            return false;
        }
    }
    return true;
}

const isValidPassword = validate('abc123', [
    validators.required,
    validators.minLength(6),
    validators.pattern(/[0-9]/)
]);
```

---

## 🎯 Patterns Comparison

```javascript
/*
╔═══════════════════════════════════════════════════════════════════╗
║                   OBSERVER vs PUB/SUB                              ║
╠═══════════════════════════════════════════════════════════════════╣
║  OBSERVER:                        PUB/SUB:                         ║
║  • Subject knows observers        • Publishers don't know subs     ║
║  • Direct communication           • Indirect via broker            ║
║  • Tightly coupled               • Loosely coupled                 ║
║  • Simpler setup                  • More scalable                  ║
║                                                                    ║
║  Use Observer when:               Use Pub/Sub when:                ║
║  • Direct notifications needed    • Components are decoupled       ║
║  • Few observers                  • Many subscribers               ║
║  • Same module/class              • Cross-module communication     ║
╚═══════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════╗
║               SINGLETON vs MODULE PATTERN                          ║
╠═══════════════════════════════════════════════════════════════════╣
║  SINGLETON:                       MODULE:                          ║
║  • Class-based instance           • Closure-based encapsulation    ║
║  • Can be subclassed             • Cannot be extended              ║
║  • Explicit getInstance()         • Direct access                  ║
║                                                                    ║
║  ES Modules ARE singletons by default!                             ║
╚═══════════════════════════════════════════════════════════════════╝
*/
```

---

## ✅ Day 18 Checklist

- [ ] Implement Singleton pattern
- [ ] Understand Factory vs Abstract Factory
- [ ] Use Builder for complex objects
- [ ] Implement Module pattern with IIFE
- [ ] Create validation Proxy
- [ ] Implement Observer pattern
- [ ] Implement Pub/Sub pattern
- [ ] Understand Observer vs Pub/Sub
- [ ] Use Strategy pattern
- [ ] Apply patterns to real scenarios
- [ ] Recognize patterns in existing code
