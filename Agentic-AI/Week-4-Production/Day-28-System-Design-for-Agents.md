# Day 28: System Design for Agents

## Learning Objectives
- Design agent systems for real-world use cases
- Apply system design principles to agent architectures
- Handle scale, reliability, and cost trade-offs
- Present agent system designs in interview format
- Practice end-to-end agent system design

---

## 1. System Design Framework for Agents

```
Step 1: Requirements
  - What does the agent do? (functional)
  - Scale: QPS, users, data volume
  - Latency: acceptable response time
  - Reliability: uptime, error tolerance
  - Cost: budget per request

Step 2: High-Level Architecture
  - Agent type (single, multi-agent, pipeline)
  - Communication pattern (sync/async)
  - State management (stateless/stateful)
  - Tool ecosystem

Step 3: Deep Dive
  - LLM selection and routing
  - Tool design and safety
  - Memory and context management
  - Error handling and recovery

Step 4: Scale & Operations
  - Scaling strategy
  - Monitoring and observability
  - Cost optimization
  - Security
```

---

## 2. Design: Customer Support Agent

```python
"""
Requirements:
- Handle 10K support tickets/day
- Resolve 70% without human escalation
- Average response time < 30s
- Support multiple channels (chat, email, API)
- Access: order history, product info, policies

Architecture:
┌──────────────────────────────────────────────────┐
│                 API Gateway                        │
│         (rate limit, auth, routing)               │
└──────────┬────────────────────┬──────────────────┘
           │                    │
    ┌──────▼──────┐     ┌──────▼──────┐
    │   Router    │     │  Escalation │
    │  (classify) │     │   Queue     │
    └──────┬──────┘     └─────────────┘
           │
    ┌──────▼──────────────────────────┐
    │        SUPPORT AGENT            │
    │  ┌─────────────────────────┐    │
    │  │ Tools:                  │    │
    │  │  - Order lookup         │    │
    │  │  - Product info         │    │
    │  │  - Policy search (RAG)  │    │
    │  │  - Refund processing    │    │
    │  │  - Ticket update        │    │
    │  └─────────────────────────┘    │
    │  Memory: conversation history   │
    │  Guardrails: PII, tone, scope   │
    └─────────────────────────────────┘
"""

class CustomerSupportSystem:
    """High-level design for customer support agent."""
    
    def __init__(self):
        self.router = IntentRouter()
        self.agent = SupportAgent()
        self.escalation = EscalationManager()
    
    async def handle_request(self, message: str, user_id: str, channel: str) -> dict:
        # 1. Classify intent
        intent = await self.router.classify(message)
        
        # 2. Check if auto-resolvable
        if intent["confidence"] < 0.6 or intent["type"] in ["complaint_severe", "legal"]:
            return await self.escalation.escalate(message, user_id, intent)
        
        # 3. Run agent
        response = await self.agent.handle(message, user_id, intent)
        
        # 4. Quality check
        if response["confidence"] < 0.7:
            return await self.escalation.escalate(message, user_id, intent)
        
        return response

class IntentRouter:
    """Classify incoming messages by intent and urgency."""
    
    INTENTS = ["order_status", "refund", "product_info", "technical", 
               "complaint", "complaint_severe", "general", "legal"]
    
    async def classify(self, message: str) -> dict:
        # Fast classification with small model
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Classify intent: {message}\nOptions: {self.INTENTS}\nReply JSON: {{\"type\": \"...\", \"confidence\": 0.0-1.0, \"urgency\": \"low/medium/high\"}}"}],
        )
        return json.loads(response.choices[0].message.content)

# Key decisions:
# - Model: gpt-4o-mini for routing, gpt-4o for complex resolution
# - Scale: queue-based, auto-scale workers on queue depth
# - Memory: Redis for session, PostgreSQL for history
# - Safety: PII redaction, tone guardrails, escalation rules
# - Cost: ~$0.01-0.05 per ticket (mostly routing + 2-3 LLM calls)
```

---

## 3. Design: Coding Assistant Agent

```python
"""
Requirements:
- IDE integration (VS Code extension)
- Real-time code suggestions + multi-turn chat
- Access: codebase, documentation, git history
- Latency: < 2s for completions, < 30s for complex tasks
- Support: multiple languages, test generation, debugging

Architecture:
┌─────────────────────────────────────────────┐
│           IDE Extension (Client)             │
│  - Inline completions (fast path)           │
│  - Chat panel (complex tasks)              │
│  - Context collection (files, cursor)       │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│              Agent Backend                    │
│  ┌─────────────────────────────────────┐    │
│  │  Context Manager                     │    │
│  │  - File indexing (embeddings)        │    │
│  │  - Relevant file selection           │    │
│  │  - Git history for context           │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │  Agent (multi-turn)                  │    │
│  │  Tools: file_read, file_edit,        │    │
│  │    search_codebase, run_tests,       │    │
│  │    git_diff, terminal_exec           │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
"""

# Key design decisions for coding assistant:
# 1. Context selection: Most impactful — which files to include
#    - Current file + imports + recently edited + related by embedding
#    - Budget: 100K tokens total, allocate across sources
# 2. Latency: Stream responses, speculative decoding for completions
# 3. Safety: Sandbox for code execution, no access to prod systems
# 4. Scale: Per-user sessions, stateless between sessions
# 5. Cost: Cache common patterns, use small model for completions
```

---

## 4. Design: Data Pipeline Agent

```python
"""
Requirements:
- Build and manage ETL pipelines from natural language
- Connect to: databases, APIs, file systems, warehouses
- Handle: schema changes, data quality issues, scheduling
- Scale: process GBs of data
- Reliability: retry, exactly-once, monitoring

Architecture:
┌─────────────────────────────────────────────┐
│            Pipeline Builder Agent             │
│                                              │
│  Input: "Load daily sales from MySQL,        │
│          transform dates, load to BigQuery"   │
│                                              │
│  1. Parse requirements → pipeline spec       │
│  2. Generate code (Python/SQL)               │
│  3. Validate connections                     │
│  4. Test with sample data                    │
│  5. Deploy to scheduler (Airflow/Prefect)    │
│                                              │
│  Tools:                                      │
│  - schema_inspect(source)                    │
│  - generate_transform(spec)                  │
│  - test_pipeline(code, sample_data)          │
│  - deploy_pipeline(code, schedule)           │
│  - monitor_pipeline(pipeline_id)             │
└─────────────────────────────────────────────┘

Key decisions:
- Human approval before deployment
- Sandbox testing with sample data (never prod data for testing)
- Schema validation at each stage
- Checkpointing for long-running transforms
- Cost: compute + LLM (LLM is small fraction for data-heavy pipelines)
"""
```

---

## 5. Design: Research Platform

```python
"""
Requirements:
- Multi-agent research on complex topics
- Sources: academic papers, web, internal docs
- Output: structured reports with citations
- Quality: verifiable claims, no hallucination
- Scale: 100+ concurrent research tasks

Architecture:
┌─────────────────────────────────────────────┐
│              RESEARCH ORCHESTRATOR            │
├─────────────────────────────────────────────┤
│                                              │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐   │
│  │Search│  │Read  │  │Analyze│  │Write │   │
│  │Agent │  │Agent │  │Agent  │  │Agent │   │
│  └──┬───┘  └──┬───┘  └──┬────┘  └──┬───┘   │
│     │         │         │          │        │
│  ┌──▼─────────▼─────────▼──────────▼───┐   │
│  │         Shared Knowledge Base         │   │
│  │  (findings, sources, contradictions)  │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  Quality Layer:                              │
│  - Citation verification                     │
│  - Cross-reference claims                    │
│  - Confidence scoring                        │
│  - Contradiction detection                   │
└─────────────────────────────────────────────┘

Design decisions:
1. Agents: specialized (search, read, analyze, write)
2. Knowledge base: shared state (blackboard pattern)
3. Quality: every claim must have a source citation
4. Scale: parallel search agents, sequential analysis
5. Cost: most tokens in reading/analyzing papers ($1-5 per deep research)
6. Reliability: checkpoint after each research phase
"""
```

---

## 6. Interview Presentation Template

```markdown
## Presenting Agent System Design in Interviews

### Structure (45 minutes):
1. **Clarify Requirements** (5 min)
   - Functional: what does the agent do?
   - Non-functional: scale, latency, cost, reliability
   - Constraints: existing systems, compliance

2. **High-Level Design** (10 min)
   - Draw architecture diagram
   - Identify agent type and communication pattern
   - Define tool ecosystem
   - Explain data flow

3. **Deep Dive** (20 min)
   - LLM selection rationale
   - Tool design (interfaces, safety, auth)
   - Memory/state management
   - Error handling strategy
   - Security considerations

4. **Scale & Operations** (10 min)
   - Scaling bottlenecks and solutions
   - Monitoring (what to measure)
   - Cost analysis
   - Deployment strategy

### Key Metrics to Discuss:
- Tokens per request (cost)
- Steps per task (efficiency)
- Success rate (reliability)
- P95 latency (performance)
- Cost per completed task (economics)
```

---

## Interview Questions

### Beginner
1. **What makes agent system design different from traditional system design?** Non-determinism (same input → different paths). LLM as bottleneck (rate limits, latency, cost). Tool management. Multi-step execution (state between steps). Safety (agents can take harmful actions). Cost is per-token (usage-based). Need observability at step level.
2. **What are the key components of any agent system?** LLM (reasoning engine). Tools (actions agent can take). Memory (context and history). Orchestration (how steps are coordinated). Safety (guardrails). Observability (tracing and monitoring). These exist regardless of use case.
3. **How do you estimate cost for an agent system?** Count: avg tokens per step × avg steps per task × cost per token. Add: tool execution costs (API calls, compute). Factor: retries (add 20-30%). Example: 5 steps × 3000 tokens × $0.005/1K = $0.075 per task. Multiply by daily volume for monthly cost.

### Intermediate
4. **How do you handle the trade-off between agent quality and latency?** Fast path: simple queries → single LLM call (< 2s). Standard: 3-5 tool calls (10-30s). Deep: complex multi-step (30s-5min, async). Route based on complexity. Stream responses. Use cheaper/faster models for intermediate steps.
5. **Design an agent system that handles 1M requests per day.** Queue-based: requests → priority queue → worker pool. Workers: 100+ containers, auto-scale. Caching: common queries → cached results (hit rate ~30%). Rate limiting: per user and per LLM provider. Dedup: identical requests → return same result. Cost: ~$50K-100K/month at $0.05/request.
6. **How do you design for graceful degradation in agent systems?** Tiers: full agent → simpler agent → cached response → static fallback. On LLM outage: fallback provider. On tool failure: skip non-critical tools, continue with available info. On overload: queue with priorities, shed low-priority. Always return something useful.

### Advanced
7. **Design a multi-agent system for automated software development that handles a team of 50 engineers.** Requirements: PR reviews, bug fixes, feature planning, documentation. Architecture: specialized agents per task type. Scale: queue per task type, priority based on urgency. Integration: GitHub webhooks → agent → PR comments. Safety: no auto-merge, human approval required. Cost: $0.50-2 per PR review, $5-20 per bug fix. Team: shared codebase knowledge via RAG.
8. **How would you migrate a traditional microservice to an agent-based architecture?** Identify: which services benefit from LLM reasoning (support, content, analysis). Start: add agent as new service alongside existing. Gradual: route % of traffic to agent, compare quality. Hybrid: agent handles complex cases, rules handle simple. Avoid: replacing working deterministic logic with non-deterministic agents. Measure: quality, cost, latency before full migration.
9. **Design an agent platform that serves multiple products (email, search, chat, analytics).** Shared: LLM gateway (routing, caching, rate limiting), tool registry, observability. Per-product: agent configuration, tools, prompts. Platform team: owns infra, gateway, shared tools. Product teams: own agent logic, product-specific tools. Versioning: independent per product. Cost allocation: per-product token tracking.

---

## Hands-On Exercise
1. Design a customer support agent system (full architecture diagram)
2. Calculate cost and latency for the support agent (per ticket)
3. Design a coding assistant with context management strategy
4. Design a data pipeline agent with deployment workflow
5. Design a research platform with quality verification
6. Practice presenting one design in 15 minutes (simulate interview)
7. Identify scaling bottlenecks and propose solutions for each design
