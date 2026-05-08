# Agentic AI Cheatsheet

## Agent Patterns

### ReAct Loop
```python
while not done:
    thought = llm.think(messages)      # Reason about next step
    action = llm.choose_tool(thought)  # Select tool + args
    observation = execute(action)       # Run tool
    messages.append(observation)        # Feed back result
    if llm.is_done(messages):          # Check if goal met
        done = True
```

### Function Calling (OpenAI)
```python
tools = [{
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": "What the tool does",
        "parameters": {"type": "object", "properties": {...}, "required": [...]}
    }
}]

response = client.chat.completions.create(model="gpt-4", messages=msgs, tools=tools)
if response.choices[0].message.tool_calls:
    for call in response.choices[0].message.tool_calls:
        result = execute(call.function.name, json.loads(call.function.arguments))
        messages.append({"role": "tool", "tool_call_id": call.id, "content": result})
```

### LangGraph Template
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]

def agent(state): return {"messages": [llm.invoke(state["messages"])]}
def tools(state): return {"messages": [execute_tools(state["messages"][-1])]}
def should_continue(state): return "tools" if state["messages"][-1].tool_calls else END

graph = StateGraph(State)
graph.add_node("agent", agent)
graph.add_node("tools", tools)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")
app = graph.compile()
```

### CrewAI Template
```python
from crewai import Agent, Task, Crew, Process

agent = Agent(role="...", goal="...", backstory="...", tools=[...], llm="gpt-4")
task = Task(description="...", expected_output="...", agent=agent)
crew = Crew(agents=[...], tasks=[...], process=Process.sequential)
result = crew.kickoff(inputs={...})
```

## Multi-Agent Patterns

| Pattern | When | Example |
|---------|------|---------|
| Orchestrator-Worker | Complex tasks needing delegation | Manager + specialized workers |
| Pipeline | Sequential processing | Research → Write → Edit |
| Debate | Need quality/accuracy | Proposer + Critic + Judge |
| Hierarchical | Large teams | CEO → Managers → Workers |
| Parallel | Independent subtasks | 3 researchers in parallel |

## Memory Types

```python
# Short-term: Message list (limited by context)
messages = [{"role": "user", "content": "..."}, ...]

# Summarized: Compress old messages
summary = llm.summarize(messages[:20])
messages = [{"role": "system", "content": summary}] + messages[20:]

# Vector store (long-term)
memory_store.add(embedding, {"text": observation, "timestamp": now})
relevant = memory_store.search(query, top_k=5)

# Structured (task-specific)
state = {"plan": [...], "completed_steps": [...], "findings": {...}}
```

## Safety Checklist
- [ ] Input validation (injection patterns)
- [ ] Max iterations limit (prevent loops)
- [ ] Cost caps (token budget per run)
- [ ] Tool permissions (least privilege)
- [ ] Output validation (PII, harmful content)
- [ ] Sandboxed code execution
- [ ] Rate limiting (per user, global)
- [ ] Human-in-the-loop for critical actions
- [ ] Audit logging (all decisions)
- [ ] Graceful degradation (fallbacks)

## MCP Server Template
```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("my-server")

@server.list_tools()
async def list_tools():
    return [Tool(name="...", description="...", inputSchema={...})]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    return [TextContent(type="text", text=result)]
```

## Key Decisions

```
Simple Q&A                    → Direct LLM call
Need external knowledge       → RAG
Fixed multi-step workflow      → Chain (LangChain LCEL)
Dynamic multi-step + tools    → Single Agent (LangGraph)
Complex task, multiple skills → Multi-Agent (CrewAI / LangGraph)
Long-running, resumable       → LangGraph + Checkpointing
User approval needed          → Human-in-the-loop (interrupt)
Many tools (50+)             → Tool retrieval + dynamic binding
Production reliability        → LangGraph + guardrails + monitoring
```

## Cost Optimization

| Strategy | Savings | When |
|----------|---------|------|
| Model routing (cheap for easy) | 50-70% | Mixed complexity tasks |
| Caching tool results | 20-40% | Repeated queries |
| Prompt compression | 10-30% | Long contexts |
| Early termination | 20-50% | High-confidence answers |
| Batch related calls | 10-20% | Multiple similar tasks |
