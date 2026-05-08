# Day 8: Multi-Agent Architectures

## Overview
When single agents hit their limits, multi-agent systems unlock complex problem-solving through specialization and collaboration.

---

## 1. Why Multi-Agent?

### Single Agent Limitations
- Context window exhaustion on complex tasks
- One model can't be expert at everything
- No separation of concerns
- Hard to debug single monolithic agent

### Multi-Agent Benefits
- **Specialization**: Each agent excels at one thing
- **Modularity**: Add/remove agents without rewriting
- **Scalability**: Parallel execution of independent tasks
- **Reliability**: Agents can check each other's work

---

## 2. Architecture Patterns

### Pattern 1: Orchestrator-Worker
```
┌──────────────────┐
│   ORCHESTRATOR   │  (Plans, delegates, synthesizes)
│   (Manager LLM)  │
└────────┬─────────┘
         │ delegates tasks
    ┌────┼────────┬──────────┐
    ▼    ▼        ▼          ▼
┌──────┐┌──────┐┌──────┐┌──────┐
│Researcher││Writer││Coder ││Reviewer│
└──────┘└──────┘└──────┘└──────┘
         │ return results
    └────┼────────┴──────────┘
         ▼
┌──────────────────┐
│   ORCHESTRATOR   │  (Synthesizes final output)
└──────────────────┘
```

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class MultiAgentState(TypedDict):
    messages: Annotated[list, operator.add]
    task: str
    plan: list[dict]
    results: Annotated[list[dict], operator.add]
    final_output: str

# Orchestrator decides what to do
def orchestrator(state: MultiAgentState) -> dict:
    """Plan and delegate tasks"""
    plan = llm.invoke(f"""
    Task: {state['task']}
    
    Break this into subtasks and assign to available agents:
    - researcher: Find information
    - writer: Write content  
    - coder: Write code
    - reviewer: Check quality
    
    Return JSON: [{{"agent": "...", "subtask": "..."}}]
    """)
    return {"plan": parse_json(plan.content)}

# Worker agents
def researcher(state: MultiAgentState) -> dict:
    current_task = get_my_task(state, "researcher")
    result = research_llm.invoke(current_task)
    return {"results": [{"agent": "researcher", "output": result.content}]}

def writer(state: MultiAgentState) -> dict:
    current_task = get_my_task(state, "writer")
    context = get_research_results(state)
    result = writer_llm.invoke(f"{current_task}\n\nContext: {context}")
    return {"results": [{"agent": "writer", "output": result.content}]}

def reviewer(state: MultiAgentState) -> dict:
    """Review and provide feedback"""
    outputs = state["results"]
    review = review_llm.invoke(f"Review this work:\n{outputs}")
    return {"results": [{"agent": "reviewer", "output": review.content}]}
```

### Pattern 2: Sequential Pipeline
```
Agent 1 → Agent 2 → Agent 3 → Agent 4
(Research)  (Draft)   (Edit)    (Format)
```

### Pattern 3: Debate / Adversarial
```
┌─────────┐         ┌─────────┐
│ Agent A  │◄───────▶│ Agent B  │
│(Proposer)│ debate  │(Critic)  │
└────┬─────┘         └────┬─────┘
     │                    │
     └────────┬───────────┘
              ▼
       ┌──────────┐
       │  Judge   │  (Decides winner / synthesizes)
       └──────────┘
```

### Pattern 4: Hierarchical
```
           CEO Agent
          /    |    \
    Manager1  Manager2  Manager3
    /    \      |      /    \
Worker Worker Worker Worker Worker
```

---

## 3. CrewAI Framework

```python
from crewai import Agent, Task, Crew, Process

# Define specialized agents
researcher = Agent(
    role="Senior Research Analyst",
    goal="Find and analyze the latest information on the given topic",
    backstory="""You are an expert researcher with 15 years of experience 
    in technology analysis. You excel at finding accurate, up-to-date information.""",
    tools=[search_tool, web_reader_tool],
    llm="gpt-4",
    verbose=True,
    allow_delegation=True  # Can ask other agents for help
)

writer = Agent(
    role="Technical Content Writer",
    goal="Write compelling, accurate technical content",
    backstory="""You are a skilled technical writer who transforms complex 
    research into clear, engaging articles.""",
    tools=[],
    llm="gpt-4",
    verbose=True,
)

editor = Agent(
    role="Senior Editor",
    goal="Ensure content is polished, accurate, and well-structured",
    backstory="""You are a meticulous editor with an eye for detail. 
    You ensure factual accuracy and clear communication.""",
    tools=[],
    llm="gpt-4",
    verbose=True,
)

# Define tasks
research_task = Task(
    description="""Research the topic: {topic}
    Find at least 5 credible sources.
    Identify key trends, statistics, and expert opinions.""",
    expected_output="Comprehensive research report with cited sources",
    agent=researcher,
)

writing_task = Task(
    description="""Write a 1500-word article based on the research.
    Include introduction, 3-4 main sections, and conclusion.
    Use clear language accessible to technical professionals.""",
    expected_output="Complete article draft in markdown format",
    agent=writer,
    context=[research_task]  # Gets output of research_task
)

editing_task = Task(
    description="""Edit the article for:
    - Factual accuracy (cross-reference with research)
    - Grammar and style
    - Logical flow
    - Technical accuracy""",
    expected_output="Final polished article ready for publication",
    agent=editor,
    context=[research_task, writing_task]
)

# Assemble crew
crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.sequential,  # or Process.hierarchical
    verbose=True,
    memory=True,  # Enable crew memory
)

# Run
result = crew.kickoff(inputs={"topic": "AI Agents in Production 2024"})
print(result)
```

---

## 4. Multi-Agent with LangGraph

```python
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

# Specialized LLMs
research_llm = ChatOpenAI(model="gpt-4", temperature=0.2)
code_llm = ChatOpenAI(model="gpt-4", temperature=0)
review_llm = ChatOpenAI(model="gpt-4", temperature=0.1)

class TeamState(TypedDict):
    messages: Annotated[list, operator.add]
    task: str
    research: str
    code: str
    review: str
    approved: bool
    iterations: int

def research_agent(state: TeamState) -> dict:
    """Research agent: gathers information"""
    result = research_llm.invoke([
        {"role": "system", "content": "You are a research specialist."},
        {"role": "user", "content": f"Research for this task: {state['task']}"}
    ])
    return {"research": result.content}

def coding_agent(state: TeamState) -> dict:
    """Coding agent: writes implementation"""
    result = code_llm.invoke([
        {"role": "system", "content": "You are an expert programmer."},
        {"role": "user", "content": f"""
        Task: {state['task']}
        Research: {state['research']}
        {"Previous feedback: " + state['review'] if state.get('review') else ""}
        
        Write the implementation.
        """}
    ])
    return {"code": result.content}

def review_agent(state: TeamState) -> dict:
    """Review agent: evaluates code quality"""
    result = review_llm.invoke([
        {"role": "system", "content": """You are a senior code reviewer. 
        Evaluate code for correctness, performance, and best practices.
        Respond with APPROVED if code is ready, or provide specific feedback."""},
        {"role": "user", "content": f"Review this code:\n{state['code']}"}
    ])
    approved = "APPROVED" in result.content.upper()
    return {
        "review": result.content,
        "approved": approved,
        "iterations": state.get("iterations", 0) + 1
    }

def route_after_review(state: TeamState) -> str:
    if state["approved"] or state["iterations"] >= 3:
        return END
    return "coding_agent"  # Send back for revision

# Build graph
builder = StateGraph(TeamState)
builder.add_node("research_agent", research_agent)
builder.add_node("coding_agent", coding_agent)
builder.add_node("review_agent", review_agent)

builder.set_entry_point("research_agent")
builder.add_edge("research_agent", "coding_agent")
builder.add_edge("coding_agent", "review_agent")
builder.add_conditional_edges("review_agent", route_after_review)

graph = builder.compile()

# Run the multi-agent team
result = graph.invoke({"task": "Build a rate limiter in Python using Redis"})
print(f"Approved: {result['approved']}")
print(f"Iterations: {result['iterations']}")
print(f"Code:\n{result['code']}")
```

---

## 5. Communication Patterns

### Shared State (LangGraph default)
```python
# All agents read/write to the same state
class SharedState(TypedDict):
    blackboard: dict    # Shared knowledge base
    messages: list      # Communication log
    task_queue: list    # Pending work
```

### Message Passing
```python
# Agents communicate via messages
class Message:
    sender: str
    receiver: str
    content: str
    message_type: str  # "request", "response", "broadcast"

def agent_mailbox(state):
    my_messages = [m for m in state["messages"] if m.receiver == MY_NAME]
    # Process messages and respond
```

### Event-Driven
```python
# Agents react to events
class Event:
    type: str           # "task_complete", "error", "approval_needed"
    source: str
    data: dict

# Agents subscribe to event types they care about
subscriptions = {
    "researcher": ["new_task", "clarification_needed"],
    "writer": ["research_complete"],
    "editor": ["draft_complete"],
}
```

---

## 6. Error Handling in Multi-Agent Systems

```python
def resilient_agent_node(state):
    """Agent with retry and fallback"""
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            result = agent_function(state)
            
            # Validate output
            if not validate_output(result):
                raise ValueError("Invalid agent output")
            
            return result
            
        except RateLimitError:
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except (ValidationError, ValueError) as e:
            # Ask agent to fix its output
            state["messages"].append(
                HumanMessage(content=f"Error: {e}. Please fix and retry.")
            )
            
        except Exception as e:
            # Fallback to simpler model
            if attempt == max_retries - 1:
                return fallback_response(state, error=str(e))
    
    return {"error": "Agent failed after max retries"}
```

---

## 7. Design Guidelines

### When to Split into Multiple Agents
- Task requires >2 distinct skills (research + coding + review)
- Context window would overflow with all context in one agent
- You need quality control (writer + reviewer)
- Tasks can be parallelized (3 research topics simultaneously)

### Agent Design Principles
1. **Single Responsibility**: Each agent does ONE thing well
2. **Clear Interface**: Define inputs/outputs explicitly
3. **Fail Gracefully**: Every agent handles errors
4. **Limit Scope**: Cap iterations, tokens, and tools per agent
5. **Observe Everything**: Log all agent decisions and tool calls

---

## Key Takeaways
- Multi-agent = specialization + collaboration
- Orchestrator-Worker is the most common production pattern
- CrewAI for quick prototyping; LangGraph for production control
- Always implement review/validation agents for quality
- Cap iterations to prevent infinite loops
- Communication pattern (shared state vs messages) depends on complexity

## Tomorrow
**Day 9**: CrewAI Deep Dive — Advanced crew configuration, hierarchical processes, and building production crews.
