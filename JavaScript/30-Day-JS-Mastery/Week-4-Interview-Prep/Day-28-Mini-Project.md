# Day 28: Build a Mini Project

## 🎯 Learning Objectives
- Apply all learned concepts in a practical project
- Practice writing clean, modular code
- Implement proper error handling
- Write tests for your code
- Build something portfolio-worthy

---

## 🚀 Project Options

Choose one of these projects to build:

### Option 1: Task Management API
### Option 2: Real-time Chat Application
### Option 3: Event Emitter Library

---

## 📦 Project 1: Task Management API

A fully-featured REST API demonstrating core JavaScript concepts.

### Project Structure

```
task-api/
├── src/
│   ├── index.js
│   ├── routes/
│   │   └── tasks.js
│   ├── controllers/
│   │   └── taskController.js
│   ├── models/
│   │   └── Task.js
│   ├── middleware/
│   │   ├── auth.js
│   │   ├── errorHandler.js
│   │   └── validation.js
│   ├── utils/
│   │   ├── asyncHandler.js
│   │   └── ApiError.js
│   └── services/
│       └── taskService.js
├── tests/
│   ├── task.test.js
│   └── utils.test.js
├── package.json
└── README.md
```

### Implementation

```javascript
// src/utils/ApiError.js
class ApiError extends Error {
    constructor(statusCode, message, isOperational = true) {
        super(message);
        this.statusCode = statusCode;
        this.isOperational = isOperational;
        Error.captureStackTrace(this, this.constructor);
    }

    static badRequest(message) {
        return new ApiError(400, message);
    }

    static notFound(message = 'Resource not found') {
        return new ApiError(404, message);
    }

    static unauthorized(message = 'Unauthorized') {
        return new ApiError(401, message);
    }
}

module.exports = ApiError;

// src/utils/asyncHandler.js
const asyncHandler = (fn) => (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
};

module.exports = asyncHandler;

// src/models/Task.js
const EventEmitter = require('events');

class TaskStore extends EventEmitter {
    constructor() {
        super();
        this.tasks = new Map();
        this.nextId = 1;
    }

    create(taskData) {
        const task = {
            id: this.nextId++,
            title: taskData.title,
            description: taskData.description || '',
            completed: false,
            priority: taskData.priority || 'medium',
            createdAt: new Date(),
            updatedAt: new Date()
        };
        this.tasks.set(task.id, task);
        this.emit('task:created', task);
        return { ...task };
    }

    findAll(filters = {}) {
        let tasks = Array.from(this.tasks.values());
        
        if (filters.completed !== undefined) {
            tasks = tasks.filter(t => t.completed === filters.completed);
        }
        if (filters.priority) {
            tasks = tasks.filter(t => t.priority === filters.priority);
        }
        
        return tasks.map(t => ({ ...t }));
    }

    findById(id) {
        const task = this.tasks.get(Number(id));
        return task ? { ...task } : null;
    }

    update(id, updates) {
        const task = this.tasks.get(Number(id));
        if (!task) return null;
        
        const updatedTask = {
            ...task,
            ...updates,
            id: task.id,
            createdAt: task.createdAt,
            updatedAt: new Date()
        };
        
        this.tasks.set(task.id, updatedTask);
        this.emit('task:updated', updatedTask);
        return { ...updatedTask };
    }

    delete(id) {
        const task = this.tasks.get(Number(id));
        if (!task) return false;
        
        this.tasks.delete(Number(id));
        this.emit('task:deleted', { id: Number(id) });
        return true;
    }
}

module.exports = new TaskStore();

// src/middleware/validation.js
const ApiError = require('../utils/ApiError');

const validateTask = (req, res, next) => {
    const { title, priority } = req.body;
    
    if (!title || typeof title !== 'string' || title.trim().length < 1) {
        return next(ApiError.badRequest('Title is required'));
    }
    
    if (title.length > 100) {
        return next(ApiError.badRequest('Title must be less than 100 characters'));
    }
    
    const validPriorities = ['low', 'medium', 'high'];
    if (priority && !validPriorities.includes(priority)) {
        return next(ApiError.badRequest(`Priority must be one of: ${validPriorities.join(', ')}`));
    }
    
    req.body.title = title.trim();
    next();
};

module.exports = { validateTask };

// src/middleware/errorHandler.js
const errorHandler = (err, req, res, next) => {
    console.error(err);
    
    if (err.isOperational) {
        return res.status(err.statusCode).json({
            success: false,
            error: err.message
        });
    }
    
    // Programming error - don't leak details
    res.status(500).json({
        success: false,
        error: 'Internal server error'
    });
};

module.exports = errorHandler;

// src/services/taskService.js
const TaskStore = require('../models/Task');
const ApiError = require('../utils/ApiError');

class TaskService {
    async createTask(taskData) {
        return TaskStore.create(taskData);
    }

    async getTasks(filters) {
        // Parse boolean
        if (filters.completed !== undefined) {
            filters.completed = filters.completed === 'true';
        }
        return TaskStore.findAll(filters);
    }

    async getTaskById(id) {
        const task = TaskStore.findById(id);
        if (!task) {
            throw ApiError.notFound('Task not found');
        }
        return task;
    }

    async updateTask(id, updates) {
        const task = TaskStore.update(id, updates);
        if (!task) {
            throw ApiError.notFound('Task not found');
        }
        return task;
    }

    async deleteTask(id) {
        const deleted = TaskStore.delete(id);
        if (!deleted) {
            throw ApiError.notFound('Task not found');
        }
        return { message: 'Task deleted successfully' };
    }

    async toggleComplete(id) {
        const task = TaskStore.findById(id);
        if (!task) {
            throw ApiError.notFound('Task not found');
        }
        return TaskStore.update(id, { completed: !task.completed });
    }
}

module.exports = new TaskService();

// src/controllers/taskController.js
const taskService = require('../services/taskService');
const asyncHandler = require('../utils/asyncHandler');

exports.createTask = asyncHandler(async (req, res) => {
    const task = await taskService.createTask(req.body);
    res.status(201).json({ success: true, data: task });
});

exports.getTasks = asyncHandler(async (req, res) => {
    const tasks = await taskService.getTasks(req.query);
    res.json({ success: true, data: tasks, count: tasks.length });
});

exports.getTask = asyncHandler(async (req, res) => {
    const task = await taskService.getTaskById(req.params.id);
    res.json({ success: true, data: task });
});

exports.updateTask = asyncHandler(async (req, res) => {
    const task = await taskService.updateTask(req.params.id, req.body);
    res.json({ success: true, data: task });
});

exports.deleteTask = asyncHandler(async (req, res) => {
    const result = await taskService.deleteTask(req.params.id);
    res.json({ success: true, ...result });
});

exports.toggleComplete = asyncHandler(async (req, res) => {
    const task = await taskService.toggleComplete(req.params.id);
    res.json({ success: true, data: task });
});

// src/routes/tasks.js
const express = require('express');
const router = express.Router();
const taskController = require('../controllers/taskController');
const { validateTask } = require('../middleware/validation');

router.route('/')
    .get(taskController.getTasks)
    .post(validateTask, taskController.createTask);

router.route('/:id')
    .get(taskController.getTask)
    .put(validateTask, taskController.updateTask)
    .delete(taskController.deleteTask);

router.patch('/:id/toggle', taskController.toggleComplete);

module.exports = router;

// src/index.js
const express = require('express');
const taskRoutes = require('./routes/tasks');
const errorHandler = require('./middleware/errorHandler');

const app = express();

app.use(express.json());
app.use('/api/tasks', taskRoutes);
app.use(errorHandler);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
```

### Tests

```javascript
// tests/task.test.js
const TaskStore = require('../src/models/Task');
const TaskService = require('../src/services/taskService');

describe('TaskStore', () => {
    beforeEach(() => {
        TaskStore.tasks.clear();
        TaskStore.nextId = 1;
    });

    test('creates a task with default values', () => {
        const task = TaskStore.create({ title: 'Test task' });
        
        expect(task.id).toBe(1);
        expect(task.title).toBe('Test task');
        expect(task.completed).toBe(false);
        expect(task.priority).toBe('medium');
    });

    test('finds task by id', () => {
        TaskStore.create({ title: 'Task 1' });
        const task = TaskStore.findById(1);
        
        expect(task.title).toBe('Task 1');
    });

    test('updates task', () => {
        TaskStore.create({ title: 'Original' });
        const updated = TaskStore.update(1, { title: 'Updated' });
        
        expect(updated.title).toBe('Updated');
    });

    test('deletes task', () => {
        TaskStore.create({ title: 'To delete' });
        const result = TaskStore.delete(1);
        
        expect(result).toBe(true);
        expect(TaskStore.findById(1)).toBeNull();
    });

    test('filters tasks by completed status', () => {
        TaskStore.create({ title: 'Task 1' });
        TaskStore.update(1, { completed: true });
        TaskStore.create({ title: 'Task 2' });
        
        const completed = TaskStore.findAll({ completed: true });
        const pending = TaskStore.findAll({ completed: false });
        
        expect(completed).toHaveLength(1);
        expect(pending).toHaveLength(1);
    });

    test('emits events', () => {
        const listener = jest.fn();
        TaskStore.on('task:created', listener);
        
        TaskStore.create({ title: 'Test' });
        
        expect(listener).toHaveBeenCalled();
    });
});
```

---

## 💬 Project 2: Real-time Chat (Core Logic)

```javascript
// src/ChatRoom.js
const EventEmitter = require('events');

class User {
    constructor(id, name) {
        this.id = id;
        this.name = name;
        this.joinedAt = new Date();
    }
}

class Message {
    constructor(userId, content, roomId) {
        this.id = Date.now().toString(36) + Math.random().toString(36).slice(2);
        this.userId = userId;
        this.content = content;
        this.roomId = roomId;
        this.timestamp = new Date();
    }
}

class ChatRoom extends EventEmitter {
    constructor(id, name, options = {}) {
        super();
        this.id = id;
        this.name = name;
        this.users = new Map();
        this.messages = [];
        this.maxMessages = options.maxMessages || 100;
        this.createdAt = new Date();
    }

    join(userId, userName) {
        if (this.users.has(userId)) {
            throw new Error('User already in room');
        }
        
        const user = new User(userId, userName);
        this.users.set(userId, user);
        this.emit('user:joined', { user, room: this.id });
        
        return user;
    }

    leave(userId) {
        const user = this.users.get(userId);
        if (!user) {
            throw new Error('User not in room');
        }
        
        this.users.delete(userId);
        this.emit('user:left', { user, room: this.id });
        
        return user;
    }

    sendMessage(userId, content) {
        if (!this.users.has(userId)) {
            throw new Error('User must join room first');
        }
        
        if (!content || typeof content !== 'string' || content.trim().length === 0) {
            throw new Error('Message content is required');
        }
        
        const message = new Message(userId, content.trim(), this.id);
        this.messages.push(message);
        
        // Keep only recent messages
        if (this.messages.length > this.maxMessages) {
            this.messages = this.messages.slice(-this.maxMessages);
        }
        
        this.emit('message', { message, room: this.id });
        
        return message;
    }

    getMessages(limit = 50) {
        return this.messages.slice(-limit);
    }

    getUsers() {
        return Array.from(this.users.values());
    }
}

class ChatServer extends EventEmitter {
    constructor() {
        super();
        this.rooms = new Map();
        this.userRooms = new Map(); // userId -> Set of roomIds
    }

    createRoom(id, name, options) {
        if (this.rooms.has(id)) {
            throw new Error('Room already exists');
        }
        
        const room = new ChatRoom(id, name, options);
        
        // Bubble up events
        room.on('user:joined', (data) => this.emit('user:joined', data));
        room.on('user:left', (data) => this.emit('user:left', data));
        room.on('message', (data) => this.emit('message', data));
        
        this.rooms.set(id, room);
        this.emit('room:created', { room: id, name });
        
        return room;
    }

    getRoom(id) {
        return this.rooms.get(id);
    }

    joinRoom(roomId, userId, userName) {
        const room = this.rooms.get(roomId);
        if (!room) {
            throw new Error('Room not found');
        }
        
        const user = room.join(userId, userName);
        
        if (!this.userRooms.has(userId)) {
            this.userRooms.set(userId, new Set());
        }
        this.userRooms.get(userId).add(roomId);
        
        return user;
    }

    leaveRoom(roomId, userId) {
        const room = this.rooms.get(roomId);
        if (!room) {
            throw new Error('Room not found');
        }
        
        room.leave(userId);
        this.userRooms.get(userId)?.delete(roomId);
    }

    getUserRooms(userId) {
        const roomIds = this.userRooms.get(userId) || new Set();
        return Array.from(roomIds).map(id => this.rooms.get(id));
    }

    broadcast(roomId, userId, content) {
        const room = this.rooms.get(roomId);
        if (!room) {
            throw new Error('Room not found');
        }
        
        return room.sendMessage(userId, content);
    }
}

module.exports = { ChatRoom, ChatServer, User, Message };

// tests/chat.test.js
const { ChatRoom, ChatServer } = require('../src/ChatRoom');

describe('ChatRoom', () => {
    let room;

    beforeEach(() => {
        room = new ChatRoom('room1', 'General');
    });

    test('user can join room', () => {
        const user = room.join('user1', 'Alice');
        
        expect(user.name).toBe('Alice');
        expect(room.getUsers()).toHaveLength(1);
    });

    test('user cannot join twice', () => {
        room.join('user1', 'Alice');
        
        expect(() => room.join('user1', 'Alice')).toThrow();
    });

    test('user can send message', () => {
        room.join('user1', 'Alice');
        const message = room.sendMessage('user1', 'Hello!');
        
        expect(message.content).toBe('Hello!');
        expect(room.getMessages()).toHaveLength(1);
    });

    test('non-member cannot send message', () => {
        expect(() => room.sendMessage('user1', 'Hello!')).toThrow();
    });

    test('emits events on actions', () => {
        const joinListener = jest.fn();
        const messageListener = jest.fn();
        
        room.on('user:joined', joinListener);
        room.on('message', messageListener);
        
        room.join('user1', 'Alice');
        room.sendMessage('user1', 'Hello!');
        
        expect(joinListener).toHaveBeenCalled();
        expect(messageListener).toHaveBeenCalled();
    });
});

describe('ChatServer', () => {
    let server;

    beforeEach(() => {
        server = new ChatServer();
    });

    test('can create and manage rooms', () => {
        server.createRoom('room1', 'General');
        server.createRoom('room2', 'Random');
        
        expect(server.getRoom('room1')).toBeDefined();
        expect(server.getRoom('room2')).toBeDefined();
    });

    test('tracks user rooms', () => {
        server.createRoom('room1', 'General');
        server.createRoom('room2', 'Random');
        
        server.joinRoom('room1', 'user1', 'Alice');
        server.joinRoom('room2', 'user1', 'Alice');
        
        const rooms = server.getUserRooms('user1');
        expect(rooms).toHaveLength(2);
    });
});
```

---

## 🎛️ Project 3: Event Emitter Library

A full-featured event emitter with advanced features.

```javascript
// src/EventEmitter.js
class EventEmitter {
    constructor(options = {}) {
        this._events = new Map();
        this._maxListeners = options.maxListeners || 10;
        this._wildcardEnabled = options.wildcard || false;
    }

    on(event, listener, options = {}) {
        if (typeof listener !== 'function') {
            throw new TypeError('Listener must be a function');
        }

        if (!this._events.has(event)) {
            this._events.set(event, []);
        }

        const listeners = this._events.get(event);
        
        if (listeners.length >= this._maxListeners) {
            console.warn(`MaxListenersExceeded: ${event} has more than ${this._maxListeners} listeners`);
        }

        const wrapper = {
            listener,
            once: options.once || false,
            priority: options.priority || 0
        };

        listeners.push(wrapper);
        
        // Sort by priority (higher first)
        listeners.sort((a, b) => b.priority - a.priority);

        return this;
    }

    once(event, listener, options = {}) {
        return this.on(event, listener, { ...options, once: true });
    }

    off(event, listener) {
        if (!this._events.has(event)) return this;

        if (!listener) {
            this._events.delete(event);
            return this;
        }

        const listeners = this._events.get(event);
        const index = listeners.findIndex(w => w.listener === listener);
        
        if (index !== -1) {
            listeners.splice(index, 1);
        }

        if (listeners.length === 0) {
            this._events.delete(event);
        }

        return this;
    }

    emit(event, ...args) {
        const listeners = this._events.get(event) || [];
        const wildcardListeners = this._wildcardEnabled 
            ? (this._events.get('*') || [])
            : [];

        const allListeners = [...listeners, ...wildcardListeners];
        
        if (allListeners.length === 0) return false;

        const toRemove = [];

        for (const wrapper of allListeners) {
            try {
                wrapper.listener.apply(this, args);
            } catch (error) {
                this.emit('error', error);
            }

            if (wrapper.once) {
                toRemove.push(wrapper);
            }
        }

        // Remove once listeners
        for (const wrapper of toRemove) {
            const eventListeners = this._events.get(event);
            if (eventListeners) {
                const index = eventListeners.indexOf(wrapper);
                if (index !== -1) {
                    eventListeners.splice(index, 1);
                }
            }
        }

        return true;
    }

    async emitAsync(event, ...args) {
        const listeners = this._events.get(event) || [];
        
        const results = await Promise.all(
            listeners.map(wrapper => 
                Promise.resolve(wrapper.listener.apply(this, args))
            )
        );

        // Remove once listeners
        const newListeners = listeners.filter(w => !w.once);
        if (newListeners.length > 0) {
            this._events.set(event, newListeners);
        } else {
            this._events.delete(event);
        }

        return results;
    }

    emitSerial(event, ...args) {
        const listeners = this._events.get(event) || [];
        
        return listeners.reduce(async (promise, wrapper) => {
            await promise;
            return wrapper.listener.apply(this, args);
        }, Promise.resolve());
    }

    listeners(event) {
        const listeners = this._events.get(event) || [];
        return listeners.map(w => w.listener);
    }

    listenerCount(event) {
        return this._events.get(event)?.length || 0;
    }

    eventNames() {
        return Array.from(this._events.keys());
    }

    setMaxListeners(n) {
        this._maxListeners = n;
        return this;
    }

    removeAllListeners(event) {
        if (event) {
            this._events.delete(event);
        } else {
            this._events.clear();
        }
        return this;
    }

    // Pipe events to another emitter
    pipe(event, target, targetEvent) {
        this.on(event, (...args) => {
            target.emit(targetEvent || event, ...args);
        });
        return this;
    }

    // Wait for an event (returns Promise)
    waitFor(event, timeout) {
        return new Promise((resolve, reject) => {
            const timer = timeout 
                ? setTimeout(() => reject(new Error('Timeout')), timeout)
                : null;

            this.once(event, (...args) => {
                if (timer) clearTimeout(timer);
                resolve(args);
            });
        });
    }
}

module.exports = EventEmitter;

// tests/EventEmitter.test.js
const EventEmitter = require('../src/EventEmitter');

describe('EventEmitter', () => {
    let emitter;

    beforeEach(() => {
        emitter = new EventEmitter();
    });

    describe('on/emit', () => {
        test('registers and triggers listeners', () => {
            const callback = jest.fn();
            emitter.on('event', callback);
            emitter.emit('event', 'arg1', 'arg2');
            
            expect(callback).toHaveBeenCalledWith('arg1', 'arg2');
        });

        test('handles multiple listeners', () => {
            const cb1 = jest.fn();
            const cb2 = jest.fn();
            
            emitter.on('event', cb1);
            emitter.on('event', cb2);
            emitter.emit('event');
            
            expect(cb1).toHaveBeenCalled();
            expect(cb2).toHaveBeenCalled();
        });
    });

    describe('once', () => {
        test('listener fires only once', () => {
            const callback = jest.fn();
            emitter.once('event', callback);
            
            emitter.emit('event');
            emitter.emit('event');
            
            expect(callback).toHaveBeenCalledTimes(1);
        });
    });

    describe('off', () => {
        test('removes specific listener', () => {
            const callback = jest.fn();
            emitter.on('event', callback);
            emitter.off('event', callback);
            emitter.emit('event');
            
            expect(callback).not.toHaveBeenCalled();
        });

        test('removes all listeners for event', () => {
            emitter.on('event', jest.fn());
            emitter.on('event', jest.fn());
            emitter.off('event');
            
            expect(emitter.listenerCount('event')).toBe(0);
        });
    });

    describe('priority', () => {
        test('higher priority listeners fire first', () => {
            const order = [];
            
            emitter.on('event', () => order.push(1), { priority: 1 });
            emitter.on('event', () => order.push(2), { priority: 2 });
            emitter.on('event', () => order.push(0), { priority: 0 });
            
            emitter.emit('event');
            
            expect(order).toEqual([2, 1, 0]);
        });
    });

    describe('emitAsync', () => {
        test('handles async listeners', async () => {
            emitter.on('event', async () => {
                return new Promise(r => setTimeout(() => r('result'), 10));
            });
            
            const results = await emitter.emitAsync('event');
            
            expect(results).toEqual(['result']);
        });
    });

    describe('waitFor', () => {
        test('resolves when event fires', async () => {
            setTimeout(() => emitter.emit('event', 'data'), 10);
            
            const [result] = await emitter.waitFor('event');
            
            expect(result).toBe('data');
        });

        test('rejects on timeout', async () => {
            await expect(
                emitter.waitFor('event', 10)
            ).rejects.toThrow('Timeout');
        });
    });
});
```

---

## 📝 Project Checklist

```
╔════════════════════════════════════════════════════════════════════╗
║                    PROJECT COMPLETION CHECKLIST                     ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                     ║
║  STRUCTURE:                                                         ║
║  □ Clear folder organization                                        ║
║  □ Separation of concerns                                           ║
║  □ Modular code with single responsibility                          ║
║                                                                     ║
║  CODE QUALITY:                                                      ║
║  □ ES6+ features used appropriately                                 ║
║  □ Proper error handling                                            ║
║  □ No code duplication                                              ║
║  □ Clear naming conventions                                         ║
║                                                                     ║
║  FUNCTIONALITY:                                                     ║
║  □ Core features working                                            ║
║  □ Edge cases handled                                               ║
║  □ Input validation                                                 ║
║                                                                     ║
║  TESTING:                                                           ║
║  □ Unit tests for core functions                                    ║
║  □ Edge cases tested                                                ║
║  □ Good test coverage (>80%)                                        ║
║                                                                     ║
║  DOCUMENTATION:                                                     ║
║  □ README with usage examples                                       ║
║  □ Code comments for complex logic                                  ║
║  □ API documentation                                                ║
║                                                                     ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## ✅ Day 28 Checklist

- [ ] Choose a project to build
- [ ] Plan the architecture
- [ ] Implement core functionality
- [ ] Add proper error handling
- [ ] Write unit tests
- [ ] Handle edge cases
- [ ] Document your code
- [ ] Refactor for clean code
