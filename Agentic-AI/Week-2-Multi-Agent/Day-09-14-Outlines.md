# Week 2: Multi-Agent Systems — Remaining Day Outlines

## Day 9: Communication Protocols
- Agent-to-agent messaging patterns
- Shared state vs message passing
- Structured message formats (JSON, function calls)
- Conversation protocols (request-reply, publish-subscribe)
- Blackboard architecture (shared knowledge base)
- Negotiation and consensus between agents
- Conflict resolution strategies

## Day 10: CrewAI Deep Dive
- CrewAI architecture (Agents, Tasks, Crew, Process)
- Role definition and goal setting
- Sequential vs hierarchical process
- Task delegation and dependencies
- Custom tools for CrewAI agents
- Memory and caching in CrewAI
- Production patterns and deployment

## Day 11: AutoGen Framework
- AutoGen architecture (AssistantAgent, UserProxyAgent)
- Group chat: dynamic multi-agent conversations
- Code execution in AutoGen (Docker sandbox)
- Custom agent types
- Nested conversations (sub-groups)
- Human-in-the-loop patterns
- AutoGen Studio (no-code agent building)

## Day 12: Agent Orchestration Patterns
- Fan-out / fan-in (parallel subtasks → merge)
- Pipeline (sequential processing stages)
- Supervisor pattern (manager delegates to specialists)
- Debate pattern (agents argue, judge decides)
- Voting / consensus (multiple agents propose, vote)
- Escalation (agent recognizes limits → escalates)
- Dynamic routing (choose agent based on input)

## Day 13: Human-in-the-Loop
- When to involve humans (high stakes, ambiguity, learning)
- Approval gates (pause and wait for confirmation)
- Interactive refinement (human feedback → agent adjusts)
- Tool use approval (approve dangerous actions)
- Active learning (agent asks for labels/guidance)
- UI patterns for human-agent collaboration
- LangGraph interrupt and resume patterns

## Day 14: Project — Multi-Agent System
- Build a software development team
  - PM Agent: requirements analysis, task breakdown
  - Developer Agent: code generation
  - Reviewer Agent: code review and suggestions
  - Tester Agent: write and run tests
- Orchestration: hierarchical with PM as manager
- Communication: structured task handoffs
- Quality gates between stages
- Evaluation on real coding tasks
