# Week 3: Advanced Patterns — Remaining Day Outlines

## Day 15: RAG Agents
- RAG vs Agentic RAG (agent decides when/what to retrieve)
- Self-RAG: agent evaluates retrieval quality
- Adaptive retrieval (skip retrieval for easy questions)
- Multi-step retrieval (iterative search refinement)
- RAG + tool use (retrieve, then calculate, then answer)
- Corrective RAG (CRAG): verify and re-retrieve
- LangGraph implementation of agentic RAG

## Day 16: Code Generation Agents
- Code agent architecture (plan → write → test → fix)
- Code execution sandboxes (Docker, E2B, Modal)
- Test-driven development with agents
- Multi-file code generation
- Debugging agents (read error → fix → re-run)
- Repository-level understanding (code search, AST)
- Tools: Cursor, Aider, OpenHands, SWE-Agent

## Day 17: Autonomous Web Agents
- Browser automation agents
- DOM understanding and action space
- Playwright/Selenium integration
- Visual grounding (screenshot → action)
- Navigation strategies (goal-directed browsing)
- Form filling and data extraction
- Safety: restricted URLs, action limits, sandboxing

## Day 18: Evaluation & Benchmarks
- Why agent evaluation is hard (non-deterministic, multi-step)
- Metrics: task success rate, efficiency, cost
- Benchmarks: SWE-bench, WebArena, GAIA, AgentBench
- Building custom evaluation suites
- Trajectory evaluation (quality of intermediate steps)
- Automated evaluation with LLM-as-judge
- Regression testing for agents

## Day 20: Tool Building
- Designing great tool interfaces (descriptions, schemas)
- Dynamic tool discovery (tools from OpenAPI specs)
- Tool registries and catalogs
- Rate limiting and quota management
- Tool authentication (API keys, OAuth)
- Error handling in tools (retry, fallback)
- Testing tools independently

## Day 21: Project — Advanced Agent
- Build a data analysis agent
  - Tools: SQL query, Python execution, chart generation
  - Memory: conversation + analysis results cache
  - Planning: decompose complex analytics questions
  - MCP integration for database access
- Multi-turn conversation with iterative analysis
- Export results (reports, visualizations)
- Evaluation on diverse analytical questions
