# Day 10: CrewAI Deep Dive

## Learning Objectives
- Understand CrewAI architecture (Agents, Tasks, Crew, Process)
- Define roles with goals and backstories
- Use sequential and hierarchical processes
- Implement task delegation and dependencies
- Add custom tools and memory

---

## 1. CrewAI Architecture

```python
# CrewAI: Framework for orchestrating role-playing AI agents
# Core concepts: Agent (who), Task (what), Crew (team), Process (how)

from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, WebsiteSearchTool

# Agent: Defined by role, goal, backstory (persona)
researcher = Agent(
    role="Senior Research Analyst",
    goal="Uncover cutting-edge developments in AI and data science",
    backstory="""You work at a leading tech think tank. Your expertise 
    lies in identifying emerging trends and translating complex research 
    into actionable insights.""",
    tools=[SerperDevTool()],
    verbose=True,
    allow_delegation=False,  # Can this agent delegate to others?
    memory=True,             # Agent remembers past interactions
)

writer = Agent(
    role="Tech Content Strategist",
    goal="Craft compelling content about tech advancements",
    backstory="""You are a renowned content strategist known for making 
    complex tech topics accessible. You transform research into engaging 
    narratives that resonate with both technical and non-technical audiences.""",
    verbose=True,
    allow_delegation=False,
)

# Task: Specific assignment with expected output
research_task = Task(
    description="""Conduct comprehensive research on the latest advancements 
    in AI agents and multi-agent systems in 2025. Focus on:
    1. Key frameworks (LangGraph, CrewAI, AutoGen)
    2. Production deployment patterns
    3. Safety and reliability approaches""",
    expected_output="A detailed report with key findings, trends, and citations",
    agent=researcher,
)

write_task = Task(
    description="""Using the research findings, write a blog post about 
    the state of AI agents in 2025. The post should be engaging, 
    informative, and about 800 words.""",
    expected_output="A polished blog post in markdown format",
    agent=writer,
    context=[research_task],  # This task depends on research_task output
)

# Crew: Team of agents working together
crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    process=Process.sequential,  # Tasks run in order
    verbose=True,
)

# Execute
result = crew.kickoff()
print(result)
```

---

## 2. Sequential vs Hierarchical Process

```python
# Sequential: Tasks executed in order, output of one feeds into next
sequential_crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, write_task, edit_task],
    process=Process.sequential,
)

# Hierarchical: Manager agent delegates tasks dynamically
manager = Agent(
    role="Project Manager",
    goal="Ensure the project is completed efficiently with high quality",
    backstory="Experienced PM who knows when to delegate and how to coordinate.",
    allow_delegation=True,
)

hierarchical_crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, write_task, edit_task],
    process=Process.hierarchical,
    manager_agent=manager,  # Manager decides who does what and when
)

# Hierarchical benefits:
# - Manager can reassign tasks based on results
# - Dynamic workflow (not fixed order)
# - Manager handles coordination and conflict
# - Better for complex, non-linear workflows
```

---

## 3. Custom Tools

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="Search query for the database")

class DatabaseSearchTool(BaseTool):
    name: str = "Database Search"
    description: str = "Search the company knowledge base for internal information"
    args_schema: type[BaseModel] = SearchInput
    
    def _run(self, query: str) -> str:
        # Your implementation
        results = search_internal_db(query)
        return f"Found {len(results)} results:\n" + "\n".join(results[:5])

class CodeExecutionTool(BaseTool):
    name: str = "Python Executor"
    description: str = "Execute Python code for data analysis. Returns stdout output."
    
    def _run(self, code: str) -> str:
        import subprocess
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True, text=True, timeout=30,
        )
        return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"

# Assign tools to agents
analyst = Agent(
    role="Data Analyst",
    goal="Analyze data and provide insights",
    backstory="Expert data analyst with Python and SQL skills",
    tools=[DatabaseSearchTool(), CodeExecutionTool()],
)
```

---

## 4. Task Dependencies & Callbacks

```python
# Task dependencies: one task uses output of another
from crewai import Task

# Context parameter: pass output of previous tasks
analysis_task = Task(
    description="Analyze the market data collected by the researcher",
    agent=analyst,
    context=[research_task],  # Gets research_task output as context
)

# Callback: execute after task completes
def save_result(output):
    """Called when task completes."""
    with open("results/latest.md", "w") as f:
        f.write(str(output))
    print(f"✅ Saved result ({len(str(output))} chars)")

task_with_callback = Task(
    description="Generate the final report",
    agent=writer,
    context=[research_task, analysis_task],
    callback=save_result,
)

# Async task execution
async_task = Task(
    description="Monitor social media mentions",
    agent=monitor_agent,
    async_execution=True,  # Runs in parallel with other tasks
)

# Human input: pause for human approval
review_task = Task(
    description="Review the generated content for accuracy",
    agent=editor,
    human_input=True,  # Will pause and ask for human feedback
)
```

---

## 5. Memory & Caching

```python
# CrewAI supports multiple memory types:

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    memory=True,              # Enable memory system
    cache=True,               # Cache tool results
    embedder={                # Custom embedder for memory
        "provider": "openai",
        "config": {"model": "text-embedding-3-small"},
    },
)

# Memory types in CrewAI:
# Short-term: Recent interactions within current execution
# Long-term: Persists across executions (learns from past)
# Entity memory: Tracks info about entities mentioned

# With long-term memory, agents can:
# - Remember successful approaches from past runs
# - Avoid repeating failed strategies
# - Build up domain knowledge over time
```

---

## 6. Production Patterns

```python
# Pattern 1: Multi-crew pipeline
research_crew = Crew(agents=[researcher], tasks=[research_task])
writing_crew = Crew(agents=[writer, editor], tasks=[write_task, edit_task])

# Run sequentially
research_result = research_crew.kickoff()
writing_crew.kickoff(inputs={"research": str(research_result)})

# Pattern 2: Dynamic task creation
class DynamicCrew:
    def run(self, topic: str):
        # Create tasks dynamically based on topic
        tasks = []
        if "code" in topic.lower():
            tasks.append(Task(description=f"Write code for: {topic}", agent=developer))
            tasks.append(Task(description="Review the code", agent=reviewer, context=[tasks[-1]]))
        
        tasks.append(Task(description=f"Write documentation for: {topic}", agent=writer, context=tasks))
        
        crew = Crew(agents=[developer, reviewer, writer], tasks=tasks, process=Process.sequential)
        return crew.kickoff()

# Pattern 3: Error handling
from crewai import Crew

try:
    result = crew.kickoff()
except Exception as e:
    print(f"Crew failed: {e}")
    # Retry with simpler configuration or fallback
    fallback_crew = Crew(agents=[writer], tasks=[simplified_task])
    result = fallback_crew.kickoff()
```

---

## Interview Questions

### Beginner
1. **What are the core components of CrewAI?** Agent (role + goal + backstory + tools), Task (description + expected output + assigned agent), Crew (team of agents + tasks + process type), Process (sequential or hierarchical execution). Agents have personas that guide their behavior.
2. **What's the difference between sequential and hierarchical process?** Sequential: tasks run in fixed order, output chains automatically. Hierarchical: a manager agent dynamically delegates and coordinates. Use sequential for simple pipelines, hierarchical for complex tasks where order isn't predetermined.
3. **Why give agents backstories?** Backstories provide context for HOW the agent should approach tasks. "10-year security expert" acts differently than "junior developer." Backstories improve output quality by giving the LLM a consistent persona and expertise level to role-play.

### Intermediate
4. **How do task dependencies work in CrewAI?** Use `context=[previous_task]` parameter. The output of context tasks is automatically included when executing the dependent task. Enables information flow without manual wiring. Multiple context tasks combine their outputs.
5. **When would you use multiple crews vs one large crew?** Multiple crews: different stages with different agent configurations, separation of concerns, error isolation (one crew failing doesn't affect others). One crew: agents need to interact directly, shared memory needed, dynamic task reallocation.
6. **How does CrewAI memory improve over multiple runs?** Long-term memory persists across executions. Agent remembers: what worked before, common pitfalls, user preferences. Entity memory tracks: facts about people/companies mentioned. Cache avoids redundant tool calls. Result: faster, more accurate over time.

### Advanced
7. **Design a CrewAI system for automated code review.** Agents: Analyzer (find issues), Security Expert (security scan), Performance Expert (bottlenecks), Writer (summary report). Process: hierarchical (Analyzer triages, delegates to specialists). Tools: code search, linter, SAST scanner. Tasks: analyze → specialist reviews → synthesize findings → write PR comment.
8. **How do you handle failures and retries in production CrewAI?** Task-level: max retries per task, fallback agents. Crew-level: try/except with fallback crew. Tool-level: timeout + retry within tools. Monitoring: log each agent's actions, track token usage. Quality: validate outputs before proceeding to next task.
9. **Compare CrewAI vs LangGraph for multi-agent systems.** CrewAI: higher-level abstraction, role-playing focus, easier setup, less control over flow. LangGraph: graph-based (explicit state machine), fine-grained control, more flexible routing, steeper learning curve. Use CrewAI: quick prototypes, well-defined roles. Use LangGraph: complex conditional flows, custom state management.

---

## Hands-On Exercise
1. Create a 3-agent crew (researcher, writer, editor) with sequential process
2. Add custom tools (web search, file reader) to agents
3. Implement hierarchical process with a manager agent
4. Set up task dependencies (research → write → review)
5. Enable memory and run the crew twice — observe improvement
6. Build a dynamic crew that adapts tasks based on user input
