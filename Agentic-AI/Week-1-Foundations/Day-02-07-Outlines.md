# Week 1: Foundations & Tool Use — Remaining Day Outlines

## Day 2: LLM APIs & Function Calling
- OpenAI API deep dive (chat completions, parameters)
- Temperature, top_p, frequency_penalty tuning
- Function calling (tools parameter)
- Structured outputs with JSON mode
- Streaming responses (SSE)
- Token management and cost tracking
- Multi-provider patterns (OpenAI, Anthropic, Groq)
- Error handling and retries

## Day 3: Tool Use & Integration
- Tool design principles (clear descriptions, typed params)
- Building tools: web search, calculator, code execution
- Tool selection strategies (how LLM picks tools)
- Parallel tool execution
- Tool result formatting and error handling
- Composing tools (output of one → input of another)
- Security: never trust tool outputs blindly

## Day 4: Memory & State Management
- Why agents need memory (context limits)
- Short-term: conversation buffer (sliding window)
- Long-term: summary memory, vector store memory
- Episodic memory (past interactions indexed by similarity)
- Working memory (scratchpad for current task)
- Memory architectures: MemGPT, buffer + summary
- Implementation with LangChain memory classes

## Day 6: ReAct & Planning Agents
- ReAct pattern (Reason → Act → Observe loop)
- Planning approaches: Plan-and-Execute, ADaPT
- Self-reflection and error correction
- Task decomposition strategies
- Iterative refinement
- When to stop (termination conditions)
- LangGraph implementation of ReAct agent

## Day 7: Project — Single Agent Application
- Build a research assistant agent
- Tools: web search, Wikipedia, calculator, code interpreter
- Memory: conversation history + vector store for notes
- Planning: break complex queries into sub-tasks
- Error handling and graceful fallbacks
- Evaluation: test on diverse queries
- Deploy as CLI or simple web interface
