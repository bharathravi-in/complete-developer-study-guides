# Day 5: LangGraph Fundamentals

## Overview
LangGraph is the production framework for building stateful, multi-step agents as graphs. More control than LangChain agents, ideal for complex workflows.

---

## 1. Why LangGraph?

### LangChain AgentExecutor Limitations
- Black-box loop (hard to customize control flow)
- Difficult to add human-in-the-loop
- No built-in persistence/checkpointing
- Limited multi-agent support

### LangGraph Advantages
- **Explicit control flow** as a graph (nodes + edges)
- **State management** with typed state objects
- **Persistence** and checkpointing built-in
- **Human-in-the-loop** with interrupt/resume
- **Streaming** of intermediate steps
- **Subgraphs** for composition

---

## 2. Core Concepts

```
┌────────────────────────────────────────────┐
│                GRAPH                         │
│                                              │
│  ┌──────┐   edge    ┌──────┐   edge   ┌──┐ │
│  │Node A│──────────▶│Node B│─────────▶│END│ │
│  └──────┘           └──────┘          └──┘ │
│      │                                  ▲   │
│      │ conditional     ┌──────┐         │   │
│      └────────────────▶│Node C│─────────┘   │
│                        └──────┘             │
│                                              │
│  STATE: Flows through every node             │
└────────────────────────────────────────────┘
```

| Concept | Description |
|---------|-------------|
| **State** | TypedDict that flows through the graph |
| **Node** | Function that takes state, returns state updates |
| **Edge** | Connection between nodes (fixed or conditional) |
| **Graph** | Collection of nodes and edges |
| **Checkpoint** | Saved state at any point (enables resume) |

---

## 3. Your First LangGraph Agent

```python
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import operator

# 1. Define State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]  # Append-only
    next_action: str

# 2. Define Nodes
llm = ChatOpenAI(model="gpt-4", temperature=0)

def agent_node(state: AgentState) -> dict:
    """LLM decides what to do"""
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def tool_node(state: AgentState) -> dict:
    """Execute the tool call"""
    last_message = state["messages"][-1]
    # Parse and execute tool calls
    tool_results = execute_tools(last_message.tool_calls)
    return {"messages": tool_results}

# 3. Define Routing Logic
def should_continue(state: AgentState) -> str:
    """Decide: continue with tools or finish"""
    last_message = state["messages"][-1]
    
    if last_message.tool_calls:
        return "tools"  # Has tool calls → execute them
    return "end"        # No tool calls → done

# 4. Build the Graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

# Add edges
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        "end": END,
    }
)
workflow.add_edge("tools", "agent")  # After tools → back to agent

# Compile
graph = workflow.compile()

# 5. Run
result = graph.invoke({
    "messages": [HumanMessage(content="What's the weather in Tokyo?")]
})
print(result["messages"][-1].content)
```

---

## 4. State Management

### Custom State
```python
from typing import TypedDict, Optional, Annotated
import operator

class ResearchState(TypedDict):
    # Accumulator fields (append)
    messages: Annotated[list[BaseMessage], operator.add]
    sources: Annotated[list[str], operator.add]
    
    # Override fields (replace)
    query: str
    plan: Optional[list[str]]
    current_step: int
    draft: Optional[str]
    final_report: Optional[str]
    iteration_count: int

# Node returns PARTIAL state updates
def plan_node(state: ResearchState) -> dict:
    """Create a research plan"""
    plan = llm.invoke(f"Create a research plan for: {state['query']}")
    steps = parse_plan(plan.content)
    return {
        "plan": steps,
        "current_step": 0,
        "messages": [AIMessage(content=f"Plan created: {steps}")]
    }

def research_node(state: ResearchState) -> dict:
    """Execute current research step"""
    current_task = state["plan"][state["current_step"]]
    results = search_web(current_task)
    return {
        "sources": [r["url"] for r in results],
        "current_step": state["current_step"] + 1,
        "messages": [AIMessage(content=f"Researched: {current_task}")]
    }
```

### Reducers
```python
# operator.add → Appends new items to existing list
# Default → Replaces the value entirely
# Custom reducer:
def dedup_add(existing: list, new: list) -> list:
    """Add items without duplicates"""
    return list(set(existing + new))

class State(TypedDict):
    unique_items: Annotated[list[str], dedup_add]
```

---

## 5. Conditional Routing

```python
def route_after_research(state: ResearchState) -> str:
    """Determine next step based on current state"""
    # Check if all steps complete
    if state["current_step"] >= len(state["plan"]):
        return "write_draft"
    
    # Check if we have enough sources
    if len(state["sources"]) >= 10:
        return "write_draft"
    
    # Continue researching
    return "research"

# Add conditional edges
workflow.add_conditional_edges(
    "research",
    route_after_research,
    {
        "research": "research",     # Loop back
        "write_draft": "write",     # Move to writing
    }
)
```

---

## 6. Persistence & Checkpointing

```python
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.postgres import PostgresSaver

# SQLite for development
memory = SqliteSaver.from_conn_string(":memory:")

# PostgreSQL for production
# memory = PostgresSaver.from_conn_string("postgresql://user:pass@host/db")

# Compile with checkpointer
graph = workflow.compile(checkpointer=memory)

# Run with thread_id (enables resume)
config = {"configurable": {"thread_id": "research-123"}}

# First invocation
result1 = graph.invoke(
    {"messages": [HumanMessage(content="Research quantum computing")]},
    config=config
)

# Resume from where we left off (same thread_id)
result2 = graph.invoke(
    {"messages": [HumanMessage(content="Now focus on recent breakthroughs")]},
    config=config
)

# Get state at any point
state = graph.get_state(config)
print(state.values)

# Get state history
for state in graph.get_state_history(config):
    print(state.values["current_step"])
```

---

## 7. Human-in-the-Loop

```python
from langgraph.graph import StateGraph, END

# Interrupt BEFORE a node
graph = workflow.compile(
    checkpointer=memory,
    interrupt_before=["execute_action"]  # Pause before this node
)

# Run until interrupt
config = {"configurable": {"thread_id": "approval-flow"}}
result = graph.invoke(initial_state, config)
# → Pauses before "execute_action"

# Check what's about to happen
state = graph.get_state(config)
pending_action = state.values["pending_action"]
print(f"Agent wants to: {pending_action}")

# Human approves → Resume
if human_approves(pending_action):
    result = graph.invoke(None, config)  # Continue from checkpoint
else:
    # Modify state and resume
    graph.update_state(config, {"pending_action": None, "messages": [
        HumanMessage(content="Don't do that. Try a different approach.")
    ]})
    result = graph.invoke(None, config)
```

---

## 8. Streaming

```python
# Stream events as they happen
async for event in graph.astream_events(
    {"messages": [HumanMessage(content="Analyze this data")]},
    config=config,
    version="v2"
):
    kind = event["event"]
    
    if kind == "on_chat_model_stream":
        # Stream LLM tokens
        print(event["data"]["chunk"].content, end="", flush=True)
    
    elif kind == "on_tool_start":
        print(f"\n🔧 Using tool: {event['name']}")
    
    elif kind == "on_tool_end":
        print(f"   Result: {event['data']['output'][:100]}")

# Stream node outputs
for chunk in graph.stream(initial_state, config, stream_mode="values"):
    print(f"Step: {chunk.get('current_step')}")
    if chunk.get("messages"):
        print(f"Latest: {chunk['messages'][-1].content[:100]}")
```

---

## 9. Complete Example: Research Agent

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults
from langchain_core.messages import HumanMessage

# Tools
search_tool = TavilySearchResults(max_results=3)
tools = [search_tool]

# LLM with tools bound
llm = ChatOpenAI(model="gpt-4", temperature=0).bind_tools(tools)

# State
class State(TypedDict):
    messages: Annotated[list, operator.add]

# Nodes
def call_model(state: State):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

tool_node = ToolNode(tools)

# Router
def should_continue(state: State):
    last_msg = state["messages"][-1]
    if last_msg.tool_calls:
        return "tools"
    return END

# Graph
builder = StateGraph(State)
builder.add_node("agent", call_model)
builder.add_node("tools", tool_node)
builder.set_entry_point("agent")
builder.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
builder.add_edge("tools", "agent")

graph = builder.compile()

# Run
result = graph.invoke({
    "messages": [HumanMessage(content="What are the latest developments in fusion energy?")]
})

for msg in result["messages"]:
    print(f"{msg.type}: {msg.content[:200]}")
```

---

## 10. LangGraph vs LangChain Agents

| Feature | LangChain Agent | LangGraph |
|---------|----------------|-----------|
| Control flow | Implicit (loop) | Explicit (graph) |
| Customization | Limited | Full control |
| State | Messages only | Custom typed state |
| Persistence | Manual | Built-in checkpointing |
| Human-in-loop | Callbacks | interrupt_before/after |
| Multi-agent | Difficult | Subgraphs |
| Streaming | Basic | Rich event stream |
| **Use when** | Simple agents | Production agents |

---

## Key Takeaways
- LangGraph = state machines for agents (nodes + edges + state)
- State flows through every node; nodes return partial updates
- Conditional edges let the LLM (or logic) determine the path
- Checkpointing enables persistence, resume, and time-travel debugging
- Human-in-the-loop with interrupt_before + state modification
- Use LangGraph for production; LangChain agents for prototyping

## Tomorrow
**Day 6**: Agent Memory Systems — Short-term, long-term, episodic memory patterns for persistent agents.
