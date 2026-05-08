# Day 1: Agentic AI Landscape

## Overview
Understanding what AI agents are, how they differ from chains and simple LLM calls, and the design patterns that make them powerful.

---

## 1. What is an AI Agent?

An AI agent is a system that uses an LLM as its **reasoning engine** to:
1. **Perceive** its environment (read inputs, tool outputs)
2. **Reason** about what to do next
3. **Act** using tools/APIs
4. **Learn** from results and iterate

### Agent vs Chain vs RAG

| Approach | Control Flow | Decision Making | Use Case |
|----------|-------------|-----------------|----------|
| **LLM Call** | Fixed (single call) | None | Q&A, summarization |
| **Chain** | Fixed (predetermined steps) | None | Sequential processing |
| **RAG** | Fixed (retrieve → generate) | None (or minimal) | Knowledge-grounded answers |
| **Agent** | **Dynamic** (LLM decides) | **LLM chooses actions** | Complex, multi-step tasks |

```python
# Chain: Fixed sequence
def chain(question):
    context = retrieve(question)        # Always step 1
    answer = generate(context, question) # Always step 2
    return answer

# Agent: Dynamic decisions
def agent(goal):
    while not goal_achieved:
        thought = llm.think(observation)  # What should I do?
        action = llm.choose_action()       # Which tool?
        observation = execute(action)      # Get result
        # LLM decides: continue, try different approach, or stop
```

---

## 2. Agent Taxonomy

### By Architecture
```
┌─────────────────────────────────────────────┐
│           AGENT ARCHITECTURES                │
├─────────────────────────────────────────────┤
│                                              │
│  Simple ReAct       Plan-and-Execute         │
│  ┌──────────┐      ┌──────────────────┐     │
│  │Think→Act │      │ Plan → Execute    │     │
│  │   ↓      │      │  each step       │     │
│  │Observe   │      │ → Replan if needed│     │
│  │   ↓      │      └──────────────────┘     │
│  │  Loop    │                                │
│  └──────────┘      Multi-Agent               │
│                    ┌──────────────────┐      │
│  Tool-Use          │ Agent₁ ↔ Agent₂  │      │
│  ┌──────────┐      │    ↕       ↕     │      │
│  │LLM picks │      │ Agent₃ ← Agent₄  │      │
│  │tool + args│     └──────────────────┘      │
│  │executes   │                               │
│  └──────────┘      Autonomous                │
│                    ┌──────────────────┐      │
│                    │ Self-directing    │      │
│                    │ Goal decomposition│      │
│                    │ Self-evaluation   │      │
│                    └──────────────────┘      │
└─────────────────────────────────────────────┘
```

### By Autonomy Level
| Level | Description | Example |
|-------|-------------|---------|
| L1: Tool Use | LLM selects and calls tools | ChatGPT with plugins |
| L2: Iterative | Multi-step tool usage with reasoning | Research agent |
| L3: Planning | Creates and follows plans, adapts | Coding agent |
| L4: Multi-Agent | Multiple specialized agents collaborate | CrewAI teams |
| L5: Autonomous | Self-directed, long-running, self-improving | Devin-like agents |

---

## 3. The ReAct Pattern

**Re**asoning + **Act**ing — the fundamental agent loop.

```
User: "What was the GDP of India in 2023 and how does it compare to 2020?"

Agent:
  Thought: I need to find India's GDP for both 2023 and 2020. Let me search.
  Action: search("India GDP 2023")
  Observation: India's GDP in 2023 was approximately $3.73 trillion.
  
  Thought: Now I need the 2020 figure for comparison.
  Action: search("India GDP 2020")
  Observation: India's GDP in 2020 was approximately $2.66 trillion.
  
  Thought: I have both numbers. Let me calculate the growth and respond.
  Action: calculate("(3.73 - 2.66) / 2.66 * 100")
  Observation: 40.2%
  
  Thought: I can now provide a complete answer.
  Final Answer: India's GDP grew from $2.66T (2020) to $3.73T (2023), 
                a growth of approximately 40.2% over 3 years.
```

### Implementation from Scratch
```python
import openai
import json

SYSTEM_PROMPT = """You are a helpful assistant with access to tools.

When you need to use a tool, respond with:
THOUGHT: <your reasoning>
ACTION: <tool_name>
ACTION_INPUT: <input as JSON>

When you have the final answer, respond with:
THOUGHT: <your reasoning>
FINAL_ANSWER: <your answer>

Available tools:
- search: Search the web. Input: {"query": "search query"}
- calculate: Do math. Input: {"expression": "2 + 2"}
- get_weather: Get weather. Input: {"city": "New York"}
"""

def run_agent(user_query: str, max_iterations: int = 10):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]
    
    for i in range(max_iterations):
        # Get LLM response
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0
        )
        assistant_message = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_message})
        
        # Check if we have a final answer
        if "FINAL_ANSWER:" in assistant_message:
            return assistant_message.split("FINAL_ANSWER:")[-1].strip()
        
        # Parse action
        if "ACTION:" in assistant_message:
            action = parse_action(assistant_message)
            
            # Execute tool
            observation = execute_tool(action['name'], action['input'])
            
            # Feed observation back
            messages.append({
                "role": "user", 
                "content": f"OBSERVATION: {observation}"
            })
        else:
            # No action and no final answer — something went wrong
            messages.append({
                "role": "user",
                "content": "Please either use a tool or provide a final answer."
            })
    
    return "Agent reached maximum iterations without a final answer."

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Execute a tool and return the observation"""
    tools = {
        "search": lambda inp: web_search(inp["query"]),
        "calculate": lambda inp: str(eval(inp["expression"])),  # Sandbox in production!
        "get_weather": lambda inp: get_weather_api(inp["city"]),
    }
    
    if tool_name not in tools:
        return f"Error: Unknown tool '{tool_name}'"
    
    try:
        return tools[tool_name](tool_input)
    except Exception as e:
        return f"Error executing {tool_name}: {str(e)}"
```

---

## 4. Function Calling (Structured Tool Use)

Modern approach: LLM outputs structured JSON for tool calls.

```python
from openai import OpenAI

client = OpenAI()

# Define tools with JSON Schema
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "Get the current stock price for a given ticker symbol",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, GOOGL)"
                    },
                    "currency": {
                        "type": "string",
                        "enum": ["USD", "EUR", "GBP"],
                        "description": "Currency for the price"
                    }
                },
                "required": ["ticker"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_chart",
            "description": "Create a chart comparing multiple data points",
            "parameters": {
                "type": "object",
                "properties": {
                    "chart_type": {"type": "string", "enum": ["bar", "line", "pie"]},
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "value": {"type": "number"}
                            }
                        }
                    },
                    "title": {"type": "string"}
                },
                "required": ["chart_type", "data"]
            }
        }
    }
]

# Agent loop with function calling
def agent_with_tools(user_message: str):
    messages = [{"role": "user", "content": user_message}]
    
    while True:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice="auto"  # Let model decide
        )
        
        message = response.choices[0].message
        messages.append(message)
        
        # If no tool calls, we're done
        if not message.tool_calls:
            return message.content
        
        # Execute each tool call
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            # Execute the function
            result = execute_function(function_name, arguments)
            
            # Append tool result
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })
```

---

## 5. Agent Design Patterns

### Pattern 1: Router Agent
```python
# Routes to specialized sub-agents
def router_agent(query):
    classification = llm.classify(query, categories=[
        "code_question", "data_analysis", "web_research", "general"
    ])
    
    agents = {
        "code_question": code_agent,
        "data_analysis": data_agent,
        "web_research": research_agent,
        "general": general_agent,
    }
    
    return agents[classification](query)
```

### Pattern 2: Reflection / Self-Critique
```python
# Agent checks and improves its own output
def reflective_agent(task):
    # Generate initial response
    draft = llm.generate(task)
    
    # Self-critique
    critique = llm.evaluate(
        f"Review this response for accuracy and completeness:\n{draft}"
    )
    
    # Improve based on critique
    if "needs improvement" in critique.lower():
        improved = llm.generate(
            f"Original: {draft}\nCritique: {critique}\nImprove the response:"
        )
        return improved
    
    return draft
```

### Pattern 3: Parallel Tool Execution
```python
import asyncio

async def parallel_agent(query):
    # Determine all needed tools upfront
    plan = llm.plan(query)  # Returns list of independent tool calls
    
    # Execute independent calls in parallel
    tasks = [execute_tool_async(tool) for tool in plan.independent_steps]
    results = await asyncio.gather(*tasks)
    
    # Synthesize results
    return llm.synthesize(query, results)
```

---

## 6. When to Use Agents

### Good Fit ✅
- Multi-step research and synthesis
- Dynamic decision-making based on intermediate results
- Tasks requiring multiple tools in variable order
- Code generation with testing and iteration
- Data analysis with exploration

### Bad Fit ❌
- Simple Q&A (just use LLM directly)
- Fixed workflows (use chains)
- Latency-sensitive applications (agents are slow)
- Tasks requiring perfect reliability (agents can loop/fail)
- When a deterministic algorithm exists

---

## 7. Hands-On: Build Your First Agent

```python
"""
Research Agent: Given a topic, search the web, 
extract key information, and write a summary.
"""
class ResearchAgent:
    def __init__(self):
        self.client = OpenAI()
        self.tools = self._define_tools()
        self.max_iterations = 8
    
    def _define_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web for current information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_url",
                    "description": "Read and extract content from a URL",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"},
                            "focus": {"type": "string", "description": "What to focus on"}
                        },
                        "required": ["url"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_report",
                    "description": "Write the final research report",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "sections": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "heading": {"type": "string"},
                                        "content": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "required": ["title", "sections"]
                    }
                }
            }
        ]
    
    def research(self, topic: str) -> str:
        messages = [
            {"role": "system", "content": """You are a research agent. 
            Search for information, read relevant sources, then write a comprehensive report.
            Always cite your sources."""},
            {"role": "user", "content": f"Research this topic: {topic}"}
        ]
        
        for _ in range(self.max_iterations):
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            messages.append(message)
            
            if not message.tool_calls:
                return message.content
            
            for tool_call in message.tool_calls:
                result = self._execute(tool_call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        
        return "Research incomplete — reached max iterations"
    
    def _execute(self, tool_call):
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        if name == "web_search":
            return self._web_search(args["query"])
        elif name == "read_url":
            return self._read_url(args["url"], args.get("focus"))
        elif name == "write_report":
            return json.dumps({"status": "report_written", "title": args["title"]})
        
        return f"Unknown tool: {name}"

# Usage
agent = ResearchAgent()
report = agent.research("Latest advances in quantum computing 2024")
print(report)
```

---

## Key Takeaways
- Agents = LLMs that can reason + act + observe in a loop
- ReAct pattern is the foundation: Thought → Action → Observation
- Function calling gives structured, reliable tool use
- Start simple (single agent + few tools) before multi-agent systems
- Agents trade latency/cost for capability — use only when needed
- Always set maximum iterations and implement graceful stopping

## Tomorrow
**Day 2**: Function Calling & Tool Use Deep Dive — Building robust tool schemas, handling errors, and parallel tool execution.
