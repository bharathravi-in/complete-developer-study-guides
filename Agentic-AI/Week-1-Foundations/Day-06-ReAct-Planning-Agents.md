# Day 6: ReAct & Planning Agents

## Learning Objectives
- Implement the ReAct (Reason + Act) pattern
- Understand planning approaches (Plan-and-Execute, ADaPT)
- Build self-reflection and error correction loops
- Design task decomposition strategies
- Implement termination conditions
- Use LangGraph for ReAct agents

---

## 1. ReAct Pattern

```python
# ReAct: Thought → Action → Observation → Thought → ... → Final Answer
# Model alternates between REASONING about what to do and ACTING with tools

from openai import OpenAI
import json

client = OpenAI()

REACT_SYSTEM = """You are a research assistant. Solve problems step-by-step.

For each step, output exactly one of:
1. Thought: [your reasoning about what to do next]
2. Action: [tool_name(param1="value1", param2="value2")]
3. Answer: [your final answer to the user]

You MUST think before acting. After each Observation, think about what it means.

Available tools:
- search(query="..."): Search the web
- calculate(expression="..."): Evaluate math
- lookup(term="..."): Look up a term in the knowledge base
"""

def react_agent(query: str, tools: dict, max_steps: int = 10) -> str:
    """ReAct loop: reason and act iteratively."""
    messages = [
        {"role": "system", "content": REACT_SYSTEM},
        {"role": "user", "content": query},
    ]
    
    for step in range(max_steps):
        response = client.chat.completions.create(
            model="gpt-4o", messages=messages, temperature=0,
        )
        output = response.choices[0].message.content
        messages.append({"role": "assistant", "content": output})
        
        # Check if we have a final answer
        if output.strip().startswith("Answer:"):
            return output.replace("Answer:", "").strip()
        
        # Parse and execute action
        if "Action:" in output:
            action_line = [l for l in output.split("\n") if l.strip().startswith("Action:")][0]
            tool_name, args = parse_action(action_line)
            
            # Execute tool
            result = tools[tool_name](**args)
            observation = f"Observation: {result}"
            messages.append({"role": "user", "content": observation})
        
    return "Max steps reached without answer"

def parse_action(action_line: str) -> tuple[str, dict]:
    """Parse 'Action: search(query=\"hello\")' into name + args."""
    # Simple parsing (production: use regex or structured output)
    content = action_line.replace("Action:", "").strip()
    name = content.split("(")[0]
    # ... parse arguments
    return name, args
```

---

## 2. Plan-and-Execute

```python
# Plan first, then execute each step
# Better for complex tasks: avoids getting lost in details

class PlanAndExecuteAgent:
    def __init__(self, tools: dict):
        self.tools = tools
        self.client = OpenAI()
    
    def plan(self, task: str) -> list[str]:
        """Create a plan (list of steps) for the task."""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"""Break this task into 3-7 concrete, actionable steps.
Each step should be specific enough to execute independently.
Return as a numbered list.

Task: {task}"""
            }],
            temperature=0,
        )
        
        steps = []
        for line in response.choices[0].message.content.split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                steps.append(line.lstrip("0123456789. "))
        return steps
    
    def execute_step(self, step: str, context: str) -> str:
        """Execute a single step using available tools."""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Execute this step. Available tools: {list(self.tools.keys())}. Context from previous steps: {context}"},
                {"role": "user", "content": step},
            ],
            tools=[...],  # tool definitions
        )
        # ... execute tools, get result
        return result
    
    def run(self, task: str) -> str:
        """Plan then execute."""
        # Step 1: Plan
        plan = self.plan(task)
        print(f"Plan: {plan}")
        
        # Step 2: Execute each step
        context = ""
        for i, step in enumerate(plan):
            print(f"Executing step {i+1}: {step}")
            result = self.execute_step(step, context)
            context += f"\nStep {i+1} result: {result}"
        
        # Step 3: Synthesize final answer
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"Task: {task}\n\nResults from execution:\n{context}\n\nProvide the final answer."
            }],
        )
        return response.choices[0].message.content
```

---

## 3. Self-Reflection & Error Correction

```python
class ReflectiveAgent:
    """Agent that evaluates its own outputs and retries if unsatisfied."""
    
    def __init__(self):
        self.client = OpenAI()
    
    def generate(self, task: str) -> str:
        """Generate initial response."""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": task}],
        )
        return response.choices[0].message.content
    
    def reflect(self, task: str, output: str) -> dict:
        """Evaluate the output — is it correct and complete?"""
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": f"""Evaluate this output for the given task.

Task: {task}
Output: {output}

Rate quality (1-5) and identify specific issues.
Return JSON: {{"score": N, "issues": ["..."], "should_retry": true/false, "feedback": "..."}}"""
            }],
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    
    def run(self, task: str, max_attempts: int = 3) -> str:
        """Generate, reflect, and retry until satisfactory."""
        for attempt in range(max_attempts):
            output = self.generate(task)
            reflection = self.reflect(task, output)
            
            print(f"Attempt {attempt+1}: score={reflection['score']}")
            
            if not reflection["should_retry"] or reflection["score"] >= 4:
                return output
            
            # Retry with feedback
            task = f"{task}\n\nPrevious attempt had issues: {reflection['feedback']}\nPlease fix these issues."
        
        return output  # Return best attempt
```

---

## 4. Task Decomposition

```python
# Strategies for breaking complex tasks into manageable pieces

def decompose_task(task: str, strategy: str = "sequential") -> list[str]:
    """Decompose a complex task into sub-tasks."""
    
    prompts = {
        "sequential": f"Break this into ordered steps (each depends on previous):\n{task}",
        "parallel": f"Break this into independent sub-tasks that can run simultaneously:\n{task}",
        "hierarchical": f"Break this into main phases, each with sub-steps:\n{task}",
    }
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompts[strategy]}],
    )
    # Parse steps...
    return steps

# Adaptive decomposition: start coarse, refine if needed
class AdaptiveDecomposer:
    def decompose(self, task: str, depth: int = 0, max_depth: int = 2) -> dict:
        """Recursively decompose until atomic tasks."""
        if depth >= max_depth:
            return {"task": task, "atomic": True}
        
        # Check if task is already atomic (can be done in one step)
        is_atomic = self._is_atomic(task)
        if is_atomic:
            return {"task": task, "atomic": True}
        
        # Decompose
        subtasks = self._break_down(task)
        return {
            "task": task,
            "atomic": False,
            "subtasks": [self.decompose(st, depth+1) for st in subtasks],
        }
    
    def _is_atomic(self, task: str) -> bool:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Can this be done in a single tool call or API request? Answer YES or NO.\nTask: {task}"}],
        )
        return "YES" in response.choices[0].message.content.upper()
```

---

## 5. Termination Conditions

```python
# When should the agent STOP?

class TerminationChecker:
    def __init__(self, max_steps: int = 15, max_cost: float = 0.50):
        self.max_steps = max_steps
        self.max_cost = max_cost
        self.step_count = 0
        self.total_cost = 0
    
    def should_stop(self, agent_output: str, task_complete: bool) -> tuple[bool, str]:
        self.step_count += 1
        
        # 1. Task explicitly completed
        if task_complete:
            return True, "Task completed successfully"
        
        # 2. Max steps exceeded
        if self.step_count >= self.max_steps:
            return True, "Maximum steps reached"
        
        # 3. Cost budget exceeded
        if self.total_cost >= self.max_cost:
            return True, "Cost budget exceeded"
        
        # 4. Agent is looping (same action repeated)
        if self._detect_loop(agent_output):
            return True, "Loop detected — agent stuck"
        
        # 5. Agent explicitly says it cannot continue
        if any(phrase in agent_output.lower() for phrase in 
               ["i cannot", "i'm unable", "impossible to"]):
            return True, "Agent cannot proceed"
        
        return False, ""
    
    def _detect_loop(self, output: str) -> bool:
        # Track last N outputs, detect repetition
        # ... implementation
        pass
```

---

## 6. LangGraph ReAct Implementation

```python
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing import TypedDict, Annotated
import operator

# Define state
class AgentState(TypedDict):
    messages: Annotated[list, operator.add]

# Create model with tools
model = ChatOpenAI(model="gpt-4o")
tools = [search_tool, calculator_tool]  # LangChain tools
model_with_tools = model.bind_tools(tools)

# Define nodes
def call_model(state: AgentState):
    """Agent reasons and optionally calls tools."""
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState):
    """Decide whether to call tools or end."""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# Build graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")  # After tools, go back to agent

app = workflow.compile()

# Run
result = app.invoke({
    "messages": [HumanMessage(content="What's the population of France divided by its area?")]
})
print(result["messages"][-1].content)
```

---

## Interview Questions

### Beginner
1. **What is the ReAct pattern?** Reasoning + Acting in alternating steps. Model thinks (Thought), takes action (Action with tool), observes result (Observation), then thinks again. Repeats until it has enough info for a final Answer. Key advantage: model's reasoning is visible and traceable.
2. **What's Plan-and-Execute vs ReAct?** ReAct: interleaves thinking and acting step-by-step (reactive, adapts as it goes). Plan-and-Execute: creates full plan first, then executes each step sequentially. Plan-and-Execute better for complex tasks with many steps; ReAct better for exploratory tasks.
3. **Why are termination conditions important?** Without them, agents can: loop forever (repeating actions), burn excessive tokens/money, never converge on an answer. Common stops: max steps, max cost, task completed, loop detected, agent gives up.

### Intermediate
4. **How does self-reflection improve agent quality?** Agent generates output → separate evaluation step rates quality → if poor, retry with feedback. Catches: incorrect answers, incomplete responses, format issues. Tradeoff: more LLM calls (cost) but higher quality. Typically 1-2 retries sufficient.
5. **Compare task decomposition strategies.** Sequential: steps depend on each other (research → analyze → write). Parallel: independent sub-tasks (search topic A while searching topic B). Hierarchical: phases with sub-steps (useful for project-level tasks). Adaptive: start coarse, refine only complex sub-tasks.
6. **How do you detect and handle agent loops?** Track action history — if same action appears 3+ times, the agent is stuck. Solutions: inject a message ("You seem to be repeating. Try a different approach."), force a different tool, limit same-action repeats, return partial results with explanation.

### Advanced
7. **Design a Plan-and-Execute agent with replanning.** Plan initially → execute step → evaluate result → if unexpected (error, new info), replan remaining steps. Key: after each step, check if plan is still valid. Replan triggers: step failure, new information discovered, user input changes goal. Balance: don't replan on every step (expensive), only on meaningful changes.
8. **How would you implement a hierarchical agent system?** Top-level planner: decomposes complex goals into sub-goals. Mid-level agents: own sub-goals, decompose into tasks. Task agents: execute atomic actions with tools. Communication: structured task assignment (goal + constraints + deadline). Escalation: task agent fails → reports to mid-level → reassigns or replans.
9. **Compare ReAct-style vs function-calling-style agents.** ReAct (text-based): model generates "Action: search(...)" as text, you parse it. Flexible, works with any model, but parsing can fail. Function calling (native): model returns structured tool_calls, no parsing needed. More reliable, but requires API support. Production: prefer function calling for reliability.

---

## Hands-On Exercise
1. Implement a ReAct agent with 3 tools (search, calculate, lookup)
2. Build Plan-and-Execute: plan a research task, execute each step
3. Add self-reflection: generate → evaluate → retry if score < 4
4. Implement adaptive task decomposition (recursive until atomic)
5. Add termination conditions (max steps, loop detection, cost limit)
6. Build a LangGraph agent with tool nodes and conditional edges
