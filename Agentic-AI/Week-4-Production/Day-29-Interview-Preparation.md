# Day 29: Interview Preparation

## Learning Objectives
- Master top 30 agentic AI interview questions
- Practice live coding for agent systems
- Prepare system design presentations
- Handle behavioral questions about AI agents
- Build a portfolio of agent projects

---

## 1. Top 30 Interview Questions & Answers

### Fundamentals (1-10)

**1. What is an AI agent and how does it differ from a chatbot?**
Agent: autonomous, multi-step, uses tools, maintains state, makes decisions. Chatbot: single-turn Q&A, no tools, no planning. Agent = LLM + tools + memory + planning loop. Key difference: agents take actions in the real world (APIs, code, files).

**2. Explain the ReAct pattern.**
Reasoning + Acting. Loop: Think (reason about what to do) → Act (call a tool) → Observe (read result) → repeat until done. Advantages: transparent reasoning (can debug), structured approach, works with any tools. Implementation: system prompt instructs agent to alternate Thought/Action/Observation.

**3. How does function calling work?**
LLM receives tool definitions (name, description, parameters). Model outputs structured tool calls (JSON with function name + arguments). System executes tool, returns result. Model sees result and decides next step. Key: model SELECTS which tool to use based on descriptions.

**4. What is tool use and why is it important?**
Tools extend LLM capabilities beyond text generation: search, calculate, access databases, call APIs, execute code. Without tools: LLM hallucinates answers. With tools: LLM reasons about WHAT to do, tools DO it. Principle: LLM as brain, tools as hands.

**5. Explain memory types for agents.**
Short-term: current conversation messages. Long-term: persisted across sessions (vector store, DB). Episodic: past experiences/interactions. Semantic: facts and knowledge. Working: intermediate reasoning. Buffer memory: last N messages. Summary memory: compressed history.

**6. What is LangGraph and when would you use it?**
Graph-based agent framework. Agents defined as state machines: nodes (actions) + edges (transitions) + state. Use when: complex conditional flows, human-in-the-loop, need explicit control over routing, multiple agents coordinating. Not for: simple single-agent chat.

**7. What is MCP (Model Context Protocol)?**
Standard protocol for tools. Server exposes tools via JSON-RPC. Client (agent) discovers and calls tools. Benefits: decoupled (any client + any server), composable (mix servers), discoverable (tools/list). Like REST for AI tools.

**8. How do you handle rate limits in agent systems?**
Exponential backoff with jitter. Queue requests. Use multiple API keys/providers. Circuit breaker (stop calling if consistently failing). Token budget per request. Fallback to cheaper model. Cache repeated queries.

**9. What is prompt injection and how do you defend?**
Attacker crafts input to override agent instructions. Defense: input validation, clear system/user boundaries, treat user input as data not instructions, LLM-based classifier, output validation, never reveal system prompt.

**10. Explain checkpointing for agents.**
Save agent state periodically during execution. If agent crashes/times out: resume from last checkpoint. State includes: messages, tool results, intermediate outputs. Important for: long-running agents, expensive operations, reliability.

### Architecture (11-20)

**11. When would you use multi-agent vs single agent?**
Multi-agent: complex tasks with distinct sub-roles, parallel work needed, different expertise areas. Single agent: straightforward tasks, latency-sensitive, simple tool use. Multi-agent overhead: coordination, more tokens, complexity. Start single, split when needed.

**12. Compare sequential, hierarchical, and parallel orchestration.**
Sequential: fixed order (A→B→C). Simple, predictable. Hierarchical: manager delegates to workers dynamically. Flexible, handles uncertainty. Parallel (fan-out/fan-in): multiple agents work simultaneously, results merged. Fast but needs coordination. Choose based on task dependency structure.

**13. How do you design tools for agents?**
Clear names (verb_noun). Detailed descriptions (when and why to use). Typed parameters with descriptions. Predictable output format. Error messages that help agent recover. Single responsibility. Validate inputs at boundary. Rate limit.

**14. How do you handle context window limits?**
Summarize old messages. Sliding window (keep last N). RAG for long-term info (retrieve when needed). Compress: remove verbose tool outputs. Priority: keep system prompt + recent + relevant. Multi-model: use long-context model for complex tasks.

**15. Design a RAG system for an agent.**
Agent decides IF retrieval needed. Query reformulation for better search. Evaluate retrieved docs (relevant?). Multi-step: decompose complex queries. Corrective: if bad results, try different query or web search. Self-RAG: generate → verify against sources → iterate.

**16. How do you evaluate agent quality?**
Success rate (task completion). Trajectory quality (efficient path?). Cost per task. Latency. Consistency (same result across runs). LLM-as-judge scoring. Regression testing over time. Domain-specific metrics (for support: resolution rate).

**17. Explain the supervisor pattern.**
One agent (supervisor) decides: who works next, what they work on, when to stop. Workers are specialized. Supervisor sees all results, routes dynamically. Benefits: adaptive workflow, handles unexpected situations. Used when: task decomposition isn't known upfront.

**18. How do you handle failures in multi-agent systems?**
Per-agent retry. Timeout per step. Fallback agents. Circuit breaker per tool. Graceful degradation (continue with partial results). Human escalation. Checkpoint before risky operations. Error classification (transient vs permanent).

**19. What is human-in-the-loop and when is it needed?**
Human reviews/approves agent actions. Needed for: high-stakes actions (payments, emails), ambiguous requests, quality assurance, learning from feedback. Implementation: approval gates, interactive refinement, LangGraph interrupt. Balance: too much HITL = slow, too little = risky.

**20. How do you deploy agents to production?**
Container-based for long-running. Queue-based for high volume. API gateway (auth, rate limit). Async execution (return job ID). Auto-scale on queue depth. Health checks. Graceful shutdown. Blue-green deployment for updates.

### Production (21-30)

**21. How do you monitor agents in production?**
Trace every execution (spans per step). Metrics: success rate, latency, cost, tokens. Logs: structured JSON with trace IDs. Alerts: degradation, cost spikes, error rate. Dashboard: real-time overview. Regression: scheduled eval suite.

**22. How do you optimize agent costs?**
Model routing (cheap for simple, expensive for complex). Caching (common queries). Shorter prompts. Fewer steps (better planning). Token budgets (stop when exceeded). Batch processing. Evaluate: cost per successful task, not just per call.

**23. What security concerns are specific to agents?**
Prompt injection. Data exfiltration via tools. Privilege escalation. Tool misuse (unintended side effects). Resource exhaustion (infinite loops). Indirect injection (poisoned documents). Defense-in-depth: input validation + tool permissions + output validation + audit.

**24. How do you handle multi-tenancy for agents?**
Tenant isolation: separate configs, data, API keys. Usage limits per tenant. Billing: track tokens per tenant. Permissions: RBAC per tenant. No cross-tenant data access. Noisy neighbor prevention (resource quotas).

**25. Explain reliability patterns for agents.**
Retry with backoff. Fallback chains (multiple providers). Circuit breaker. Timeout. Idempotency (same input = same result). Checkpointing. Graceful degradation. Chaos testing.

**26. How do you test agents?**
Unit: individual tools. Integration: tool + LLM. E2E: full task execution. Eval suite: 50+ test cases with expected outcomes. Regression: run on every change. Load: handle expected traffic. Chaos: inject failures. Quality: LLM-as-judge scoring.

**27. How do you version and rollback agents?**
Semantic versioning. A/B testing (route % to new version). Monitor quality metrics. Instant rollback if regression. Keep old version hot (ready to serve). Change log for prompt/tool changes. Separate: code deploys vs prompt updates.

**28. What is observability for multi-step agents?**
Full trace: every step with inputs/outputs/latency. Token tracking per step. Tool call logging with arguments and results. Error attribution (which step failed?). Replay: re-run from trace for debugging. Correlation: link user request to all internal operations.

**29. How do you handle data privacy with agents?**
PII detection and redaction before logging. Data minimization (don't store what you don't need). Retention policies (auto-delete). Encryption (at rest + in transit). User consent. Right to deletion (GDPR). Anonymize training data.

**30. Describe your ideal agent architecture for production.**
API gateway → router (classify intent/complexity) → agent pool (scaled via queue). Agents: LLM + tools + memory + guardrails. Infra: tracing, cost tracking, error recovery, checkpointing. Safety: input/output validation, tool permissions, audit. Scale: queue-based, auto-scale workers. Operations: dashboards, alerts, regression tests.

---

## 2. Live Coding Practice

```python
# Common live coding tasks in agent interviews:

# Task 1: Build a simple ReAct agent (20 min)
# - Function calling loop
# - 2-3 tools (search, calculate)
# - Termination condition

# Task 2: Implement a tool with safety (15 min)
# - Input validation
# - Rate limiting
# - Error handling

# Task 3: Add memory to an agent (15 min)
# - Conversation buffer
# - Summarization when too long
# - Relevant memory retrieval

# Task 4: Build a router (10 min)
# - Classify input complexity
# - Route to appropriate model/agent
# - Fallback handling

# Task 5: Implement retry with fallback (10 min)
# - Exponential backoff
# - Provider fallback chain
# - Circuit breaker
```

---

## 3. System Design Interview Template

```
Format: 45-minute system design for agent systems

Opening (5 min):
"Design an AI agent for [X]. Walk me through your approach."

Your response:
1. Ask clarifying questions (scale, latency, budget, constraints)
2. State assumptions

High-level (10 min):
- Draw architecture (API → Router → Agent → Tools)
- Explain agent type choice (single/multi, sync/async)
- Identify key tools needed
- Define success metrics

Deep dive (20 min):
- Model selection and routing strategy
- Tool interfaces and safety
- Memory/context management
- Error handling and reliability
- Security considerations

Scale & Operations (10 min):
- Scaling bottlenecks
- Cost analysis (per request)
- Monitoring approach
- Deployment strategy
```

---

## 4. Behavioral Questions

```
Q: "Tell me about a time you built something with AI agents."
Framework: STAR (Situation, Task, Action, Result)
- What was the problem?
- What agent approach did you choose and why?
- What challenges did you face?
- What was the outcome (metrics)?

Q: "How do you handle uncertainty in agent outputs?"
- Confidence scoring
- Human-in-the-loop for low confidence
- Verification steps
- Graceful degradation
- Clear communication to users about limitations

Q: "How do you decide between using an agent vs traditional code?"
- Agents: unstructured input, need reasoning, can't predefine all paths
- Traditional: structured input, deterministic logic, well-defined rules
- Hybrid: route simple cases to code, complex to agent
- Cost/reliability trade-off

Q: "How do you keep up with the rapidly evolving agent landscape?"
- Follow key papers (Self-RAG, CRAG, ReAct)
- Experiment with new frameworks (LangGraph, CrewAI, AutoGen)
- Build prototypes to understand trade-offs
- Focus on fundamentals (prompt engineering, tool design, evaluation)
```

---

## 5. Portfolio Projects

```
Strong portfolio for agent engineering roles:

1. Multi-Agent Development Team
   - PM, Developer, Reviewer, Tester
   - Iterative code review loops
   - Shows: orchestration, communication, quality control

2. RAG Agent with Self-Correction
   - Agentic retrieval (decide when/how to search)
   - Self-evaluation and query refinement
   - Shows: reliability, evaluation, iterative improvement

3. Production-Ready Agent with Observability
   - Full tracing and cost tracking
   - Error recovery and retry logic
   - Shows: production mindset, operations, reliability

4. Web Automation Agent
   - Browser control with Playwright
   - Multi-step task completion
   - Shows: tool building, error handling, real-world application

5. Secure Agent with Guardrails
   - Input validation, prompt injection defense
   - Output filtering, audit logging
   - Shows: security awareness, enterprise readiness
```

---

## Interview Questions

### Beginner
1. **How do you explain AI agents to a non-technical stakeholder?** "An AI agent is like a smart assistant that can not only answer questions but also take actions — search databases, call APIs, write code, send emails. You give it a task, and it figures out the steps, uses tools, and delivers results. Unlike simple chatbots, it can handle multi-step complex tasks autonomously."
2. **What's the most important skill for agent engineering?** Prompt engineering + systems thinking. You need to: design clear tool interfaces (agent must understand them), write effective system prompts, think about failure modes and edge cases, design for observability. It's software engineering with an LLM as a core component.
3. **How do you stay updated on agent developments?** Follow: LangChain/LangGraph updates, Anthropic and OpenAI blogs, key papers (agent benchmarks, new architectures). Practice: build prototypes with new frameworks. Community: GitHub discussions, Twitter/X AI community. Focus: fundamentals over hype (evaluation, reliability, safety).

### Intermediate
4. **Walk through how you'd debug a failing agent.** 1) Check trace: which step failed? 2) Examine: what was the input to the LLM at that step? 3) Tool call: was the tool call valid? Did the tool return expected result? 4) Context: was relevant info available? 5) Replay: run again with same inputs — reproducible? 6) Fix: adjust prompt, tool description, or add guardrails.
5. **How do you balance agent autonomy with safety?** Risk-based: auto-approve low-risk (reads), require approval for high-risk (writes, sends). Confidence-based: high confidence → auto, low → ask human. Scope: limit tools to minimum needed. Monitor: alert on unusual patterns. Start restrictive, gradually increase autonomy as trust builds.
6. **What would you improve about current agent frameworks?** Better evaluation tooling (standard benchmarks + custom). More reliable structured output. Native observability (trace by default). Better long-term memory. Cost optimization built-in. More secure defaults (sandboxed by default). Easier testing.

### Advanced
7. **If you had to build an agent platform from scratch, what would you prioritize?** Week 1: Core agent loop + tool calling + basic tracing. Week 2: Error handling + retry + fallback. Week 3: Evaluation framework + regression tests. Week 4: Security (guardrails, permissions, audit). Then: multi-tenant, scaling, advanced observability. Principle: reliability > features.
8. **What's the hardest production agent problem you'd expect to face?** Reliability at scale. Non-deterministic behavior makes testing hard. Cascading failures across tools. Cost control when agents take unexpected paths. Detecting degradation before users notice. Root-causing failures in multi-step, multi-agent systems. Balancing latency with quality.
9. **Where do you see agentic AI in 3 years?** More autonomous (less HITL needed). Specialized agents > general agents. Agent-to-agent protocols standardized (like APIs). Better evaluation and certification. Enterprise: agents as team members with clear roles and permissions. Cost: 10x cheaper. Safety: better solved problems.

---

## Hands-On Exercise
1. Answer all 30 questions in writing (practice articulating clearly)
2. Time yourself: explain ReAct pattern in 2 minutes
3. Live code: build a 3-tool agent in 20 minutes
4. System design: present customer support agent in 15 minutes
5. Mock interview: have someone ask 5 random questions from this list
6. Portfolio: ensure you have 3+ agent projects on GitHub with READMEs
