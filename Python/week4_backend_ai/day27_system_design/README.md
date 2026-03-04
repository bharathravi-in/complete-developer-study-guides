# Day 27 - System Design for Backend Engineers

## Topics Covered
- System design fundamentals
- Scalability patterns
- Database design
- Caching strategies
- Message queues
- Microservices architecture

## System Design Process
```
1. Requirements Clarification
   ├─ Functional requirements
   └─ Non-functional requirements

2. Capacity Estimation
   ├─ Traffic estimates
   ├─ Storage estimates
   └─ Bandwidth estimates

3. System Interface Design
   └─ API endpoints

4. Data Model Design
   ├─ Database schema
   └─ Data flow

5. High-Level Design
   └─ Component diagram

6. Detailed Design
   ├─ Specific components
   └─ Trade-offs

7. Bottlenecks & Solutions
   └─ Scaling strategies
```

## Project Structure
```
day27_system_design/
├── README.md
├── practice.py              # Concepts overview
├── design_patterns.py       # Common patterns
└── case_studies.py          # Example designs
```

## Key Concepts

### 1. Scaling Patterns
```
Vertical Scaling (Scale Up)
  └─ More CPU, RAM, storage

Horizontal Scaling (Scale Out)
  └─ More servers

Load Balancing
  ├─ Round Robin
  ├─ Least Connections
  └─ IP Hash

Database Scaling
  ├─ Read Replicas
  ├─ Sharding
  └─ Partitioning
```

### 2. Caching Layers
```
Client → CDN → Load Balancer → App Cache → DB Cache → Database
```

### 3. Common Architectures
```
Monolith → Service-Oriented → Microservices → Serverless
```

## Run
```bash
python practice.py
python design_patterns.py
```

## Practice Exercises
1. Design a URL shortener (like bit.ly)
2. Design a rate limiter
3. Design a notification system
4. Design a chat application
5. Design a file storage system (like Dropbox)
