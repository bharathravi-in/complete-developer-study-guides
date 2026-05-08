# Week 4: Production & Safety — Remaining Day Outlines

## Day 22: Deployment Architectures
- Serverless agents (AWS Lambda, Cloud Functions)
- Container-based (Docker, Kubernetes)
- Queue-based architecture (Celery, Bull, SQS)
- Scaling strategies (horizontal, model routing)
- Latency optimization (streaming, caching, parallel tools)
- Cost management (model selection, token budgets)
- Multi-tenant agent systems

## Day 23: Observability & Debugging
- Tracing agent execution (LangSmith, Phoenix, Helicone)
- Structured logging for multi-step agents
- Token usage tracking and cost attribution
- Latency breakdown (LLM time vs tool time)
- Error classification and recovery patterns
- Replay and debugging failed trajectories
- Dashboards and alerting

## Day 25: Reliability Engineering
- Retry strategies (exponential backoff, jitter)
- Fallback chains (primary model → secondary → graceful degradation)
- Timeout management (per-tool, per-step, total)
- Idempotency in agent actions
- Checkpointing for long-running agents
- Recovery from partial failures
- Chaos testing for agents

## Day 26: Agent Security Deep Dive
- Threat model for AI agents
- Prompt injection (direct, indirect, tool-mediated)
- Data exfiltration via tools
- Privilege escalation attacks
- Defense: input validation, output filtering, sandboxing
- Principle of least privilege for tools
- Red teaming agents

## Day 27: Enterprise Patterns
- Multi-tenant agent platforms
- Role-based access control for agents
- Audit logging and compliance
- Data residency and privacy (PII handling)
- Agent marketplace and sharing
- Version management (agent versions, prompt versions)
- SLAs for agent systems

## Day 28: System Design for Agents
- Design: Customer support agent system
- Design: Autonomous coding assistant
- Design: Data pipeline monitoring agent
- Design: Multi-agent research platform
- Framework: Requirements → Architecture → Safety → Scaling
- Trade-offs: autonomy vs control, cost vs quality

## Day 29: Interview Preparation
- Top 30 questions review (see Interview-Prep/)
- Live coding: build an agent in 45 minutes
- System design: whiteboard an agent architecture
- Behavioral: explain production agent decisions
- Portfolio presentation (show your projects)
- Research awareness (latest papers, trends)

## Day 30: Capstone — Production Agent
- Full production agent system
  - Multi-agent architecture (specialist agents + orchestrator)
  - MCP integration (database, file system, API tools)
  - Memory: short-term + long-term + episodic
  - Safety: guardrails, sandboxing, rate limiting
  - Observability: tracing, metrics, dashboards
  - Evaluation: automated test suite
- Documentation: architecture, decisions, trade-offs
- Demo-ready deployment
