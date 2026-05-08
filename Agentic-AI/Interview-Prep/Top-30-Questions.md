# Agentic AI — Interview Prep

## Top 30 Interview Questions

### Fundamentals (1-10)

**1. What is an AI agent and how does it differ from a chain?**
An agent uses an LLM as a reasoning engine to dynamically decide actions. Unlike chains (fixed steps), agents choose tools, loop, branch, and adapt based on observations. Key components: Reasoning (LLM), Tools (actions), Memory (state), Planning (strategy).

**2. Explain the ReAct pattern.**
Reasoning + Acting. Loop: Thought (LLM reasons about what to do) → Action (execute tool) → Observation (tool result). LLM decides whether to continue or provide final answer. Foundation of most agent architectures.

**3. What is function calling and why is it important?**
LLMs output structured JSON to call functions (tools) instead of free-text parsing. Benefits: reliable tool invocation, type-safe arguments, parallel calls, schema validation. Core of production agents.

**4. How does agent memory work?**
- Short-term: Conversation messages in context window (limited by tokens)
- Working memory: Task-specific state (current plan, partial results)
- Long-term: Vector store for episodic memory, summaries of past interactions
- External: Database/file storage for persistent knowledge

**5. What is tool orchestration?**
Managing how an agent selects, sequences, and executes tools. Includes: tool selection (which tool for this step), argument construction, error handling, retry logic, parallel execution when independent.

**6. Explain the Plan-and-Execute pattern.**
1. Planner LLM decomposes task into subtasks
2. Executor LLM handles each subtask with tools
3. Re-planner adjusts plan based on results
Advantage over ReAct: Better for complex multi-step tasks. Separates planning from execution.

**7. What is a multi-agent system?**
Multiple specialized agents collaborating on a task. Patterns: Orchestrator-Worker (manager delegates), Pipeline (sequential), Debate (adversarial review), Hierarchical (team structure). Benefits: specialization, scalability, quality control.

**8. How do you handle agent failures?**
- Max iteration limits (prevent infinite loops)
- Retry with backoff on transient errors
- Fallback models (GPT-4 fails → try Claude)
- Graceful degradation (partial results > no results)
- Human escalation for critical failures
- Dead letter queue for failed tasks

**9. What is the context window limitation and how to address it?**
LLMs have fixed context (4K-200K tokens). Strategies: summarize long conversations, use RAG (retrieve relevant context only), hierarchical memory (store summaries, retrieve details on demand), sliding window with key facts.

**10. Explain prompt injection and defense strategies.**
Adversarial inputs override system instructions. Defenses: input validation (pattern matching), sandwich prompts (reinforce instructions after user input), output filtering, separate LLM calls for planning vs execution, tool output sanitization.

---

### Architecture & Design (11-20)

**11. Design an autonomous coding agent.**
```
User Task → Planner (decompose into coding steps)
         → Researcher (read relevant code/docs)
         → Coder (write implementation)
         → Tester (run tests, check output)
         → Reviewer (quality/security check)
         → Loop if tests fail (max 3 iterations)
         → Final output
```
Key: Sandboxed execution, file system tools, git integration, test runner, max iterations.

**12. How would you build a customer support agent?**
- Router: Classify intent (billing, technical, general)
- Knowledge Agent: RAG over docs/FAQs
- Action Agent: Execute actions (refund, escalate, update)
- Human handoff: Confidence threshold for escalation
- Guardrails: Can't promise unauthorized things, PII handling
- Memory: Customer history for personalized support

**13. Explain LangGraph vs other frameworks.**
- LangGraph: Explicit state machine (nodes + edges), full control, checkpointing, production-ready
- LangChain AgentExecutor: Simple loop, quick prototyping, limited customization
- CrewAI: Multi-agent with roles, good for crew-based workflows
- AutoGen: Conversational multi-agent, group chat pattern
- Choose LangGraph for production; CrewAI/AutoGen for prototyping multi-agent

**14. How do you evaluate agent performance?**
- Task completion rate (did it achieve the goal?)
- Trajectory efficiency (steps taken vs optimal)
- Tool usage accuracy (right tool, right args)
- Response quality (LLM-as-judge scoring)
- Cost per task (tokens consumed)
- Latency (time to completion)
- Failure mode analysis (where/why does it fail?)

**15. What is MCP and why does it matter?**
Model Context Protocol: standardizes how AI apps connect to tools/data. Like USB for AI tools. Server exposes tools/resources, any MCP client can use them. Build once, work with Claude/VS Code/custom apps. Reduces N×M integration problem to N+M.

**16. How do you handle state in long-running agents?**
- Checkpointing: Save state after each step (LangGraph built-in)
- Persistence: Store in Redis/PostgreSQL
- Resume: Load checkpoint and continue from last step
- Timeout handling: Save progress, resume later
- State serialization: All state must be JSON-serializable

**17. Explain agentic RAG.**
Agent decides WHEN and HOW to retrieve. Unlike static RAG (always retrieve), agentic RAG: decides if retrieval needed, formulates queries dynamically, evaluates relevance, reformulates if results are poor, synthesizes from multiple retrievals.

**18. How do you implement human-in-the-loop?**
- Interrupt points: Pause before critical actions
- Approval queue: Human reviews and approves/rejects
- Feedback injection: Human can modify agent state
- Escalation rules: Confidence-based routing to human
- LangGraph: interrupt_before/after + checkpoint resume

**19. Design a data analysis agent.**
```
Query → Intent Classification
      → If SQL needed: Text-to-SQL Agent → Execute → Validate
      → If visualization: Chart generation
      → If statistical: Python execution (sandboxed)
      → Summarize findings in natural language
```
Tools: SQL executor (read-only!), Python sandbox, chart library. Safety: only SELECT, resource limits.

**20. How do you manage costs in production agents?**
- Token budgets per task (hard limit)
- Model routing: Use cheap model (GPT-3.5) for simple steps, expensive (GPT-4) for reasoning
- Caching: Cache tool results and common LLM responses
- Prompt optimization: Shorter prompts, fewer examples
- Early termination: Stop when confidence is high
- Batching: Group related tasks

---

### Production & Advanced (21-30)

**21. How do you deploy agents at scale?**
- Queue-based: Task queue (Redis/SQS) → Worker pool → Results store
- Async execution: Don't block on LLM calls
- Horizontal scaling: Stateless workers + shared state store
- Rate limiting: Per-user and global API limits
- Graceful shutdown: Checkpoint before stopping

**22. Explain observability for agents.**
- Tracing: Full trajectory (every thought, action, observation)
- Tools: LangSmith, Phoenix (Arize), custom logging
- Metrics: Latency, token usage, success rate, error rate
- Replay: Ability to replay a failed run with same inputs
- Debugging: Step through agent decisions

**23. What are guardrails for agents?**
Safety boundaries: input validation (reject malicious prompts), output validation (check for PII/harmful content), tool permissions (least privilege), rate limits, cost caps, max iterations, sandboxed execution.

**24. How do you test agents?**
- Unit tests: Individual tools work correctly
- Integration tests: Agent can use tools end-to-end
- Trajectory tests: Expected path through tools/reasoning
- Adversarial tests: Prompt injection, edge cases
- Regression tests: Known-good inputs still produce correct output
- Load tests: Performance under concurrent usage

**25. Explain the difference between sync and async agent execution.**
- Sync: User waits for completion. Good for fast tasks (< 30s). Simple architecture.
- Async: Submit task, get task_id, poll for results. Good for long tasks (minutes/hours). Requires queue + workers + results store + webhooks/polling.

**26. How do you handle multi-turn conversations with agents?**
- Message history: Append all messages (limited by context window)
- Summarization: Periodically summarize old messages
- Slot filling: Track what information has been collected
- State machine: Track conversation stage (greeting → info gathering → action → confirm)
- Session management: Thread ID → persistent state

**27. What is tool selection optimization?**
When an agent has many tools (50+), LLM struggles to select the right one. Solutions: tool descriptions as RAG (retrieve relevant tools), hierarchical tools (categories → specific), dynamic tool sets (only show relevant tools per step), few-shot examples of tool use.

**28. Explain autonomous vs semi-autonomous agents.**
- Autonomous: Full self-direction, minimal human intervention. Risky but powerful. (Devin, AutoGPT)
- Semi-autonomous: Human approves critical steps, agent handles routine work. Safer. (Copilot-style)
- Production reality: Most deployed agents are semi-autonomous with guardrails.

**29. How do you handle conflicting tool outputs?**
- Confidence scoring: Rank sources by reliability
- Majority voting: Multiple sources agree → higher confidence
- Recency: Prefer newer information
- Source authority: Prefer authoritative sources
- Ask for clarification: Route to human if conflict is critical
- Explicit uncertainty: Report conflicting information to user

**30. Design a production agent platform (system design).**
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   API/UI    │────▶│  Task Queue  │────▶│  Workers    │
│  (FastAPI)  │     │  (Redis/SQS) │     │  (Agents)   │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                 │
                    ┌──────────────┐     ┌───────▼──────┐
                    │  State Store │◀────│  Tool Router │
                    │ (PostgreSQL) │     │  (MCP/REST)  │
                    └──────────────┘     └──────────────┘
                    
Components:
- Auth + rate limiting (API gateway)
- Task queue (Redis) for async execution
- Worker pool (K8s pods) for agent execution
- State store (PostgreSQL) for checkpoints
- Tool registry (MCP servers) for extensibility
- Observability (LangSmith + Prometheus)
- Safety layer (guardrails middleware)
```
