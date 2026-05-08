# Day 13: Real-time Communication (WebSockets & Socket.IO)

## 🎯 Learning Objectives
- Understand WebSocket protocol vs HTTP
- Build real-time apps with Socket.IO
- Implement rooms, namespaces, and broadcasting
- Handle scaling WebSockets across instances

---

## 📚 WebSocket Fundamentals

### Native WebSocket Server

```javascript
const { WebSocketServer } = require('ws');
const http = require('http');

const server = http.createServer();
const wss = new WebSocketServer({ server });

wss.on('connection', (ws, req) => {
  const clientIp = req.socket.remoteAddress;
  console.log(`Client connected from ${clientIp}`);
  
  // Send message to client
  ws.send(JSON.stringify({ type: 'welcome', message: 'Connected!' }));
  
  // Receive messages
  ws.on('message', (data) => {
    const message = JSON.parse(data.toString());
    console.log('Received:', message);
    
    // Broadcast to all other clients
    wss.clients.forEach(client => {
      if (client !== ws && client.readyState === 1) {
        client.send(JSON.stringify(message));
      }
    });
  });
  
  // Handle disconnect
  ws.on('close', (code, reason) => {
    console.log(`Client disconnected: ${code} ${reason}`);
  });
  
  // Ping/pong for keepalive
  ws.isAlive = true;
  ws.on('pong', () => { ws.isAlive = true; });
});

// Heartbeat to detect dead connections
const interval = setInterval(() => {
  wss.clients.forEach(ws => {
    if (!ws.isAlive) return ws.terminate();
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);

wss.on('close', () => clearInterval(interval));
server.listen(3000);
```

---

## 🔌 Socket.IO

### Server Setup

```javascript
const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: process.env.FRONTEND_URL,
    credentials: true
  },
  pingInterval: 25000,
  pingTimeout: 20000
});

// Authentication middleware
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  try {
    const user = jwt.verify(token, process.env.JWT_SECRET);
    socket.user = user;
    next();
  } catch (err) {
    next(new Error('Authentication failed'));
  }
});

// Connection handler
io.on('connection', (socket) => {
  console.log(`User ${socket.user.name} connected (${socket.id})`);
  
  // Join user's personal room
  socket.join(`user:${socket.user.id}`);
  
  // Join a chat room
  socket.on('join:room', (roomId) => {
    socket.join(roomId);
    socket.to(roomId).emit('user:joined', { user: socket.user.name, roomId });
    console.log(`${socket.user.name} joined room ${roomId}`);
  });
  
  // Send message to room
  socket.on('message:send', ({ roomId, content }) => {
    const message = {
      id: Date.now().toString(),
      content,
      sender: socket.user,
      timestamp: new Date().toISOString()
    };
    
    io.to(roomId).emit('message:new', message);
    // Save to database
    saveMessage(message, roomId);
  });
  
  // Typing indicator
  socket.on('typing:start', (roomId) => {
    socket.to(roomId).emit('typing:start', { user: socket.user.name });
  });
  
  socket.on('typing:stop', (roomId) => {
    socket.to(roomId).emit('typing:stop', { user: socket.user.name });
  });
  
  // Disconnect
  socket.on('disconnect', (reason) => {
    console.log(`${socket.user.name} disconnected: ${reason}`);
    io.emit('user:offline', { userId: socket.user.id });
  });
});

httpServer.listen(3000);
```

### Namespaces

```javascript
// Separate concerns with namespaces
const chatNamespace = io.of('/chat');
const notificationNamespace = io.of('/notifications');

chatNamespace.on('connection', (socket) => {
  // Only chat-related events
  socket.on('message', (data) => { /* ... */ });
});

notificationNamespace.on('connection', (socket) => {
  // Only notification events
  socket.emit('unread', { count: 5 });
});

// Emit to specific namespace
chatNamespace.to('room-1').emit('message', { text: 'Hello' });
notificationNamespace.to(`user:${userId}`).emit('notification', data);
```

### Broadcasting Patterns

```javascript
// To all connected clients
io.emit('announcement', { message: 'Server restarting in 5 minutes' });

// To all clients in a room except sender
socket.to('room-1').emit('message', data);

// To all clients in a room including sender
io.to('room-1').emit('message', data);

// To a specific socket
io.to(socketId).emit('private', { message: 'Just for you' });

// To all clients except sender
socket.broadcast.emit('event', data);

// To multiple rooms
io.to('room-1').to('room-2').emit('message', data);

// Send to user across multiple devices (rooms as user channels)
io.to(`user:${userId}`).emit('notification', notification);
```

---

## 📡 Server-Sent Events (SSE)

For one-way real-time data (server → client):

```javascript
router.get('/events', (req, res) => {
  res.writeHead(200, {
    'Content-Type': 'text/event-stream',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive'
  });
  
  // Send event
  function sendEvent(event, data) {
    res.write(`event: ${event}\n`);
    res.write(`data: ${JSON.stringify(data)}\n\n`);
  }
  
  sendEvent('connected', { message: 'Stream active' });
  
  // Send updates periodically
  const interval = setInterval(() => {
    sendEvent('update', { timestamp: Date.now(), value: Math.random() });
  }, 1000);
  
  // Cleanup on disconnect
  req.on('close', () => {
    clearInterval(interval);
  });
});
```

---

## 🔄 Scaling WebSockets

```javascript
// Problem: Multiple server instances don't share socket state
// Solution: Redis adapter for Socket.IO

const { createAdapter } = require('@socket.io/redis-adapter');
const { createClient } = require('redis');

async function setupSocketIO(io) {
  const pubClient = createClient({ url: process.env.REDIS_URL });
  const subClient = pubClient.duplicate();
  
  await Promise.all([pubClient.connect(), subClient.connect()]);
  
  io.adapter(createAdapter(pubClient, subClient));
  // Now events are broadcast across all instances via Redis pub/sub
}

// Sticky sessions (required for Socket.IO with HTTP long-polling fallback)
// In Nginx:
// upstream backend {
//   ip_hash;  # or use cookie-based stickiness
//   server backend1:3000;
//   server backend2:3000;
// }
```

---

## 🧪 Interview Questions

### Beginner

**Q1: What is the difference between HTTP and WebSocket?**

HTTP: request-response, client initiates, half-duplex, new connection per request (or keep-alive). WebSocket: persistent, bidirectional, full-duplex connection. WebSocket starts as HTTP upgrade request, then maintains a long-lived TCP connection. Better for real-time data (chat, live updates, gaming).

**Q2: What is Socket.IO and how does it differ from raw WebSockets?**

Socket.IO is a library built on WebSockets that adds: automatic reconnection, fallback transports (HTTP long-polling), rooms/namespaces, broadcasting, acknowledgements, and binary support. It uses its own protocol over WebSockets. Raw WS is lighter but requires manual implementation of these features.

**Q3: What are rooms in Socket.IO?**

Rooms are arbitrary channels that sockets can join/leave. Used to group sockets for targeted broadcasting (`io.to('room').emit(...)`). Common uses: chat rooms, game lobbies, user-specific channels. Sockets can be in multiple rooms. Every socket automatically has a room with its socket ID.

### Intermediate

**Q4: How do you handle authentication with WebSockets?**

Options: (1) Token in handshake query/auth (Socket.IO `handshake.auth`). (2) Authenticate on first message. (3) Cookie-based (sent with upgrade request). Validate in `io.use()` middleware. Reject with `next(new Error())`. Re-authenticate on reconnection. Never trust client-side socket.id for authorization.

**Q5: What is the difference between WebSocket and Server-Sent Events (SSE)?**

WebSocket: bidirectional, binary support, custom protocol. SSE: unidirectional (server → client only), HTTP-based, auto-reconnection, event types built-in. Use SSE for: notifications, live feeds, dashboards (server-only updates). Use WebSocket for: chat, gaming, collaborative editing (client also sends data).

**Q6: How do you handle WebSocket connection drops and reconnection?**

Socket.IO handles automatically (configurable delays, max attempts). For raw WS: implement exponential backoff reconnection, queue messages during disconnection, send last-received sequence number on reconnect to get missed messages, use heartbeat/pong to detect dead connections proactively.

### Advanced

**Q7: How do you scale WebSockets across multiple server instances?**

Use Redis adapter (pub/sub) to relay events between instances. Socket.IO: `@socket.io/redis-adapter`. Require sticky sessions for HTTP long-polling transport (Nginx ip_hash or cookie). Alternative: dedicated WebSocket service behind a load balancer with layer-4 balancing (TCP-level).

**Q8: How would you implement a real-time collaborative text editor?**

Use Operational Transform (OT) or CRDT (Conflict-free Replicated Data Types). Each keystroke generates an operation. Operations are broadcast via WebSocket, transformed against concurrent ops, and applied. Libraries: Yjs (CRDT), ShareJS (OT). Server acts as central authority for operation ordering. Handle offline edits with version vectors.

**Q9: Design a notification system that handles millions of concurrent WebSocket connections.**

Architecture: Connection tier (gateway servers, 100K connections each) → Message broker (Kafka/Redis Streams) → Business logic tier. Use horizontal scaling with Redis adapter. Implement connection draining for deployments. Binary protocol for efficiency. Client-side message deduplication. Presence tracking with Redis sorted sets.

---

## 🛠️ Hands-on Exercise

Build a real-time chat application:
1. Socket.IO server with authentication
2. Multiple chat rooms with join/leave
3. Typing indicators
4. Message history (load from DB on join)
5. Online/offline presence tracking
6. Private messaging between users
