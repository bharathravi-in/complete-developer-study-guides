# 30-Day Daily Timetable — Frontend Lead → AI Engineer

> **Daily time**: 4-6 hours (adjust based on availability)
> **Format**: Morning (concept study) → Afternoon (hands-on coding) → Evening (review)

---

## WEEK 1: Python + Flask Foundation (Days 1-7)

### Day 1 (Mon) — Python Syntax & Data Structures
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | Study Python syntax, comparison with JS | `week1/python-fundamentals/01-syntax-and-data-structures.md` |
| 10:30-12:00 | Practice: Lists, dicts, sets, comprehensions | Code exercises in the guide |
| 14:00-15:30 | String methods, f-strings, slicing | Same guide + Python REPL |
| 15:30-16:00 | ✅ Review: Write 10 list comprehensions from memory | — |

### Day 2 (Tue) — OOP & Classes
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | Study classes, dataclasses, ABC, Protocols | `week1/python-fundamentals/02-oop-and-classes.md` |
| 10:30-12:00 | Code: Build a Document class hierarchy | Exercises in the guide |
| 14:00-15:30 | Practice: Mixins, Enums, __dunder__ methods | Same guide |
| 15:30-16:00 | ✅ Review: Can you create a dataclass from memory? | — |

### Day 3 (Wed) — Async & Concurrency
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | Study asyncio, compare with JS async/await | `week1/python-fundamentals/03-async-and-concurrency.md` |
| 10:30-12:00 | Code: Async HTTP client, gather parallel calls | Same guide |
| 14:00-15:30 | Threading vs multiprocessing, GIL | Same guide |
| 15:30-16:00 | ✅ Review: When to use async vs threads vs multiprocessing? | — |

### Day 4 (Thu) — File Handling, Logging, Environment
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | File I/O, JSON, CSV, pathlib | `week1/python-fundamentals/04-file-handling-and-logging.md` |
| 10:30-12:00 | Logging setup, environment variables | Same guide |
| 14:00-15:30 | Virtual environments, Poetry, project setup | Same guide |
| 15:30-16:00 | ✅ Setup: Create a Python project with venv + .env | — |

### Day 5 (Fri) — Testing with pytest
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | pytest basics, fixtures, parametrize | `week1/python-fundamentals/05-testing-with-pytest.md` |
| 10:30-12:00 | Mocking: Mock, patch, AsyncMock | Same guide |
| 14:00-15:30 | Write tests for Day 1-4 code | Your practice code |
| 15:30-16:00 | ✅ Goal: 10+ tests passing with `pytest -v` | — |

### Day 6 (Sat) — Decorators & Advanced Python
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | Decorators, type hints, generics | `week1/python-fundamentals/06-decorators-and-advanced.md` |
| 10:30-12:00 | Code: timer, cache, retry decorators | Same guide |
| 14:00-15:30 | Context managers, generators | Same guide |
| 15:30-16:00 | ✅ Build: A decorator-heavy utility module | — |

### Day 7 (Sun) — Flask Complete Guide + Mini Project
| Time | Activity | Material |
|------|----------|----------|
| 9:00-11:00 | Flask routing, Blueprints, middleware | `week1/flask-api/01-flask-complete-guide.md` |
| 11:00-13:00 | JWT auth, Pydantic validation, SQLAlchemy | Same guide |
| 14:00-16:00 | Build: REST API with 5+ endpoints | `week1/projects/mini-cli-tool.py` for reference |
| 16:00-17:00 | ✅ Deploy Flask app locally with tests | — |

---

## WEEK 2: AI Foundations (Days 8-14)

### Day 8 (Mon) — LLM Fundamentals
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | Transformers, tokenization, how LLMs work | `week2/llm-basics/01-llm-fundamentals.md` |
| 10:30-12:00 | OpenAI API setup, first API calls | Same guide |
| 14:00-15:30 | Parameters: temperature, top_p, max_tokens | Same guide |
| 15:30-16:00 | ✅ Make 5 different API calls with varying params | — |

### Day 9 (Tue) — Prompt Engineering
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | System prompts, templates, few-shot | `week2/llm-basics/01-llm-fundamentals.md` (prompt section) |
| 10:30-12:00 | Chain-of-thought, output formatting | Same guide |
| 14:00-15:30 | Build: Prompt library for different tasks | Your own prompts |
| 15:30-16:00 | ✅ Create 10 reusable prompt templates | — |

### Day 10 (Wed) — Embeddings Deep Dive
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | What are embeddings, cosine similarity | `week2/embeddings/01-embeddings-complete-guide.md` |
| 10:30-12:00 | OpenAI embeddings API, sentence-transformers | Same guide |
| 14:00-15:30 | Build: Semantic search engine (10 documents) | Same guide |
| 15:30-16:00 | ✅ Search working: query returns relevant results | — |

### Day 11 (Thu) — Qdrant Vector Database
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:00 | Docker: `docker run qdrant/qdrant` | `week2/qdrant/01-qdrant-complete-guide.md` |
| 10:00-11:30 | Qdrant CRUD operations, collections | Same guide |
| 11:30-13:00 | Filtering, payload indexing | Same guide |
| 14:00-16:00 | Build: VectorDBService class (production-ready) | Same guide |
| 16:00-16:30 | ✅ Store 100+ vectors, search working | — |

### Day 12 (Fri) — RAG Pipeline
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | RAG concept: index → retrieve → generate | `week2/rag/01-rag-complete-guide.md` |
| 10:30-12:00 | Document loading, chunking strategies | Same guide |
| 14:00-16:00 | Build: Complete RAG pipeline with Flask API | Same guide |
| 16:00-16:30 | ✅ Upload document → Ask question → Get answer with sources | — |

### Day 13 (Sat) — RAG Optimization
| Time | Activity | Material |
|------|----------|----------|
| 9:00-11:00 | Advanced: hybrid search, re-ranking | `week2/rag/01-rag-complete-guide.md` (advanced) |
| 11:00-13:00 | Prompt optimization for RAG | Same guide |
| 14:00-16:00 | Improve: Add caching, better prompts, error handling | Your RAG code |
| 16:00-16:30 | ✅ RAG system handling 10+ documents accurately | — |

### Day 14 (Sun) — Week 2 Integration & Review
| Time | Activity | Material |
|------|----------|----------|
| 9:00-12:00 | Combine all: Flask + Qdrant + LLM + Embeddings | All Week 2 materials |
| 13:00-15:00 | Write tests for the RAG pipeline | pytest knowledge from Week 1 |
| 15:00-16:00 | ✅ Review: Can you explain RAG pipeline end-to-end? | — |
| 16:00-17:00 | Answer 20 interview questions (Section 2) | `week4/interview-questions/01-120-interview-questions.md` |

---

## WEEK 3: Production Stack (Days 15-21)

### Day 15 (Mon) — Redis Fundamentals
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | Redis data structures, commands | `week3/redis/01-redis-complete-guide.md` |
| 10:30-12:00 | Python redis client, basic operations | Same guide |
| 14:00-15:30 | Build: LLM cache with Redis | Same guide |
| 15:30-16:00 | ✅ Cache hit/miss working, measure latency improvement | — |

### Day 16 (Tue) — Redis Advanced
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | Rate limiting, session management | `week3/redis/01-redis-complete-guide.md` |
| 10:30-12:00 | Pub/Sub, job queues | Same guide |
| 14:00-15:30 | Integrate Redis into RAG project | Your RAG + Redis |
| 15:30-16:00 | ✅ RAG with caching: repeated queries are instant | — |

### Day 17 (Wed) — Docker Fundamentals
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | Dockerfile, multi-stage builds | `week3/docker/01-docker-complete-guide.md` |
| 10:30-12:00 | docker-compose: Flask + Qdrant + Redis | Same guide |
| 14:00-15:30 | Build: Dockerize your RAG project | Same guide |
| 15:30-16:00 | ✅ `docker-compose up` starts entire stack | — |

### Day 18 (Thu) — Docker Advanced + Architecture
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | Health checks, .dockerignore, dev vs prod | `week3/docker/01-docker-complete-guide.md` |
| 10:30-12:00 | Multi-stage builds, image optimization | Same guide |
| 14:00-16:00 | Polish Docker setup for your project | Your project |
| 16:00-16:30 | ✅ Production-ready Docker with health checks | — |

### Day 19 (Fri) — Flutter Quick Start
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:30 | Dart basics (compared to JS/TS) | `week3/flutter/01-flutter-ai-chat-app.md` |
| 10:30-12:00 | Flutter widgets, state management | Same guide |
| 14:00-16:00 | Build: AI Chat App (connect to your Flask API) | Same guide |
| 16:00-16:30 | ✅ Chat app working: send message → get AI response | — |

### Day 20 (Sat) — Flutter Polish + Integration
| Time | Activity | Material |
|------|----------|----------|
| 9:00-12:00 | Add features: conversation history, loading states | Flutter guide |
| 13:00-15:00 | Connect Flutter → Flask → Qdrant → LLM | All materials |
| 15:00-16:00 | ✅ Full stack working end-to-end | — |

### Day 21 (Sun) — Week 3 Review & Project Integration
| Time | Activity | Material |
|------|----------|----------|
| 9:00-12:00 | Full project: Flask API + Qdrant + Redis + Docker | All Week 3 materials |
| 13:00-15:00 | Test everything, fix bugs, add error handling | Your project |
| 15:00-16:00 | ✅ Complete stack running in Docker | — |
| 16:00-17:00 | Answer 20 interview questions (Sections 1 & 3) | Interview questions |

---

## WEEK 4: System Design & Interview Prep (Days 22-30)

### Day 22 (Mon) — System Design: AI Chat
| Time | Activity | Material |
|------|----------|----------|
| 9:00-11:00 | Study: Design an AI Chat System | `week4/system-design/01-ai-system-design.md` |
| 11:00-12:00 | Practice drawing architecture diagrams | Paper/whiteboard |
| 14:00-16:00 | Practice: Explain the design out loud (30 min timer) | — |

### Day 23 (Tue) — System Design: Scalable RAG
| Time | Activity | Material |
|------|----------|----------|
| 9:00-11:00 | Study: Scalable RAG System, capacity estimation | System design guide |
| 11:00-12:00 | Calculate costs for different scales | Same guide |
| 14:00-16:00 | Practice: Whiteboard the RAG architecture | — |

### Day 24 (Wed) — System Design: Multi-Tenant SaaS
| Time | Activity | Material |
|------|----------|----------|
| 9:00-11:00 | Study: Multi-tenant design, data isolation | System design guide |
| 11:00-12:00 | Compare isolation approaches | Same guide |
| 14:00-16:00 | Practice: Design a multi-tenant AI SaaS from scratch | — |

### Day 25 (Thu) — Interview Questions Deep Dive (Part 1)
| Time | Activity | Material |
|------|----------|----------|
| 9:00-12:00 | Study + practice Q1-40 (Python + AI basics) | `week4/interview-questions/01-120-interview-questions.md` |
| 14:00-16:00 | Code the answers: implement caching, rate limiting | Your code |
| 16:00-16:30 | ✅ Can answer any Q1-40 confidently | — |

### Day 26 (Fri) — Interview Questions Deep Dive (Part 2)
| Time | Activity | Material |
|------|----------|----------|
| 9:00-12:00 | Study + practice Q41-80 (AI advanced + Redis) | Interview questions |
| 14:00-16:00 | Code: RAG evaluation, prompt engineering examples | Your code |
| 16:00-16:30 | ✅ Can answer any Q41-80 confidently | — |

### Day 27 (Sat) — Interview Questions Deep Dive (Part 3)
| Time | Activity | Material |
|------|----------|----------|
| 9:00-12:00 | Study + practice Q81-120 (System design + Architecture) | Interview questions |
| 14:00-16:00 | Mock interview: answer 10 random questions aloud | — |
| 16:00-16:30 | ✅ Can answer any Q81-120 confidently | — |

### Day 28 (Sun) — Full Project Polish
| Time | Activity | Material |
|------|----------|----------|
| 9:00-13:00 | Polish the AI Knowledge Platform project | `week4/full-project/` |
| 14:00-16:00 | Write README, add screenshots, clean code | — |
| 16:00-17:00 | ✅ Project ready to show in interviews | — |

### Day 29 (Mon) — Mock Interviews
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:00 | Mock: System design (30 min) | Timer + whiteboard |
| 10:00-11:00 | Mock: Technical questions (30 min) | Random questions |
| 11:00-12:00 | Mock: Tell me about yourself + project (30 min) | Resume |
| 14:00-16:00 | Review weak areas, study gaps | All materials |
| 16:00-17:00 | ✅ Update resume with latest experience | `resources/resume/` |

### Day 30 (Tue) — Final Review & Confidence Check
| Time | Activity | Material |
|------|----------|----------|
| 9:00-10:00 | Quick review: cheat sheets | `resources/cheat-sheets/` |
| 10:00-11:00 | Quick review: system design (sketch 3 designs) | System design guide |
| 11:00-12:00 | Quick review: 20 hardest questions | Interview questions |
| 14:00-15:00 | Final mock interview (full simulation) | — |
| 15:00-16:00 | ✅ Confidence check: I'm ready! | — |

---

## Daily Habits (Every Day)
- [ ] 30 min morning: Review yesterday's material
- [ ] Code at least 1 hour hands-on
- [ ] Answer 5 interview questions out loud
- [ ] Push code to GitHub (build your profile)
- [ ] 15 min evening: Write what you learned today
