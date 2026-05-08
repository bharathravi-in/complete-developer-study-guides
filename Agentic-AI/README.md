# Agentic AI — 30-Day Mastery Plan

## Goal
Master the design and implementation of autonomous AI agents — from single-tool agents to multi-agent orchestration systems. Build production-grade agentic applications.

## Prerequisites
- Python intermediate+
- LLM fundamentals (API usage, prompt engineering)
- Basic understanding of RAG (see `../AI-ML-Engineering/` or `../material/`)

---

## Weekly Breakdown

### Week 1: Foundations — Tool Use & Single Agents (Days 1–7)
| Day | Topic | Focus |
|-----|-------|-------|
| 1 | Agentic AI Landscape | What are agents, taxonomy, ReAct pattern, agent vs chain vs RAG |
| 2 | Function Calling & Tool Use | OpenAI/Anthropic function calling, tool schemas, structured outputs |
| 3 | Building a ReAct Agent from Scratch | Thought-Action-Observation loop in Python, no framework |
| 4 | LangChain Agents | AgentExecutor, tool binding, memory, output parsers |
| 5 | LangGraph Fundamentals | State machines, nodes, edges, conditional routing |
| 6 | Agent Memory Systems | Short-term, long-term, episodic memory, vector store memory |
| 7 | Project: Personal Research Agent | Agent that searches web, reads docs, synthesizes answers |

### Week 2: Multi-Agent Systems & Frameworks (Days 8–14)
| Day | Topic | Focus |
|-----|-------|-------|
| 8 | Multi-Agent Architectures | Orchestrator-worker, debate, delegation, hierarchy patterns |
| 9 | CrewAI Framework | Agents, tasks, crews, process types, delegation |
| 10 | AutoGen / AG2 | Conversable agents, group chat, code execution |
| 11 | OpenAI Assistants API | Threads, runs, file search, code interpreter |
| 12 | Agent Communication Patterns | Message passing, shared state, event-driven, blackboard |
| 13 | Human-in-the-Loop | Approval flows, escalation, feedback loops, guardrails |
| 14 | Project: Multi-Agent Content Pipeline | Research → Write → Edit → Publish crew |

### Week 3: Advanced Patterns & Production (Days 15–21)
| Day | Topic | Focus |
|-----|-------|-------|
| 15 | Planning & Reasoning | Tree-of-Thought, plan-and-execute, task decomposition |
| 16 | Advanced LangGraph | Subgraphs, parallel execution, dynamic routing, checkpointing |
| 17 | RAG-Augmented Agents | Agents with retrieval tools, adaptive RAG, agentic RAG |
| 18 | Code Generation Agents | Code writing, execution sandboxing, self-debugging, testing |
| 19 | MCP (Model Context Protocol) | MCP servers, tools, resources, building MCP integrations |
| 20 | Agent Evaluation & Testing | Benchmarks, trajectory evaluation, success metrics |
| 21 | Project: Autonomous Coding Agent | Agent that reads repos, writes code, runs tests, iterates |

### Week 4: Production, Safety & Interview Prep (Days 22–30)
| Day | Topic | Focus |
|-----|-------|-------|
| 22 | Production Architecture | Deployment, scaling, async execution, queue-based agents |
| 23 | Reliability & Error Handling | Retry strategies, fallbacks, circuit breakers, graceful degradation |
| 24 | Safety & Guardrails | Prompt injection defense, output validation, sandboxing, rate limits |
| 25 | Cost Optimization | Token management, caching, model routing, batching |
| 26 | Observability & Debugging | LangSmith, tracing, logging agent decisions, replay |
| 27 | Advanced Orchestration | Workflow engines, event-driven agents, long-running tasks |
| 28 | AI Agent System Design | Design: customer support, data analyst, DevOps agent |
| 29 | Interview Prep | Agentic AI interview questions, system design, whiteboard |
| 30 | Capstone: Production Agent Platform | Multi-agent system with memory, tools, safety, monitoring |

---

## Key Technologies
- **Frameworks**: LangChain, LangGraph, CrewAI, AutoGen, Semantic Kernel
- **LLM Providers**: OpenAI, Anthropic, open-source (Llama, Mistral)
- **Tools**: Web search, code execution, file I/O, APIs, databases
- **Memory**: Vector stores (ChromaDB, Qdrant), Redis, conversation buffers
- **Protocols**: MCP (Model Context Protocol), OpenAI function calling
- **Observability**: LangSmith, Phoenix, Weights & Biases
- **Infra**: FastAPI, Docker, Redis queues, WebSockets

## Study Approach
- 2–3 hours/day minimum
- Theory (20%) → Build agents (60%) → Evaluate & iterate (20%)
- Every day should produce a working agent or component
- Focus on reliability over cleverness — production agents must be predictable
