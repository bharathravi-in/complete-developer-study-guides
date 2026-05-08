# Day 14: Project — Multi-Agent Software Development Team

## Learning Objectives
- Build a complete multi-agent system for software development
- Implement PM, Developer, Reviewer, and Tester agents
- Orchestrate with task delegation and feedback loops
- Handle iterative code review and fixing cycles
- Apply all Week 2 concepts in a real project

---

## 1. System Architecture

```
┌─────────────────────────────────────────────────────┐
│                  PROJECT MANAGER                      │
│  Breaks requirements → assigns tasks → tracks progress│
└──────────┬──────────────────┬───────────────────────┘
           │                  │
    ┌──────▼──────┐   ┌──────▼──────┐
    │  DEVELOPER  │   │   TESTER    │
    │ Writes code │   │ Writes tests│
    └──────┬──────┘   └──────┬──────┘
           │                  │
    ┌──────▼──────────────────▼──────┐
    │           REVIEWER              │
    │  Reviews code + tests quality   │
    └─────────────────────────────────┘

Flow: PM → Developer → Reviewer → (fix loop) → Tester → PM (done)
```

---

## 2. Agent Definitions

```python
from openai import OpenAI
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

client = OpenAI()

class AgentRole(Enum):
    PM = "project_manager"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    TESTER = "tester"

@dataclass
class TaskItem:
    id: str
    description: str
    status: str = "pending"  # pending, in_progress, review, testing, done
    assignee: str = ""
    code: str = ""
    tests: str = ""
    review_feedback: str = ""
    iterations: int = 0

class Agent:
    def __init__(self, role: AgentRole, system_prompt: str):
        self.role = role
        self.system_prompt = system_prompt
        self.history: list[dict] = []
    
    def act(self, message: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            *self.history[-10:],  # Keep recent context
            {"role": "user", "content": message},
        ]
        response = client.chat.completions.create(model="gpt-4o", messages=messages)
        result = response.choices[0].message.content
        self.history.append({"role": "user", "content": message})
        self.history.append({"role": "assistant", "content": result})
        return result

# Define agents
pm = Agent(AgentRole.PM, """You are a Project Manager for a software team.
Your responsibilities:
1. Break user requirements into specific, actionable tasks
2. Prioritize tasks and assign them
3. Track progress and ensure quality
4. Make decisions when there are trade-offs

Output task breakdowns as numbered lists with clear acceptance criteria.
When all tasks are complete, output: PROJECT_COMPLETE""")

developer = Agent(AgentRole.DEVELOPER, """You are a Senior Python Developer.
Your responsibilities:
1. Write clean, production-quality Python code
2. Follow best practices (type hints, error handling, docstrings)
3. Address review feedback promptly
4. Write code that is testable

Always output complete, runnable code in ```python blocks.
Include imports and all necessary functions/classes.""")

reviewer = Agent(AgentRole.REVIEWER, """You are a Code Reviewer.
Your responsibilities:
1. Check for bugs, logic errors, edge cases
2. Verify security (no injection, proper validation)
3. Assess code quality (naming, structure, DRY)
4. Check error handling and type safety

Rate code: APPROVE (ready for testing) or REQUEST_CHANGES (needs fixes).
If REQUEST_CHANGES, provide specific, actionable feedback.""")

tester = Agent(AgentRole.TESTER, """You are a QA Engineer.
Your responsibilities:
1. Write comprehensive unit tests using pytest
2. Cover happy path, edge cases, and error cases
3. Verify the code meets acceptance criteria
4. Report any bugs found

Output complete test files in ```python blocks.
Rate: PASS (all good) or FAIL (with specific issues found).""")
```

---

## 3. Orchestrator

```python
class SoftwareTeamOrchestrator:
    """Orchestrates the multi-agent software development workflow."""
    
    def __init__(self):
        self.pm = pm
        self.developer = developer
        self.reviewer = reviewer
        self.tester = tester
        self.tasks: list[TaskItem] = []
        self.max_review_iterations = 3
    
    def run(self, requirements: str) -> dict:
        """Execute full development workflow."""
        print("📋 Phase 1: Planning")
        tasks = self._plan(requirements)
        
        results = {}
        for task in tasks:
            print(f"\n💻 Phase 2: Developing — {task.id}")
            code = self._develop(task)
            
            print(f"\n🔍 Phase 3: Reviewing — {task.id}")
            code = self._review_loop(task, code)
            
            print(f"\n🧪 Phase 4: Testing — {task.id}")
            tests = self._test(task, code)
            
            results[task.id] = {"code": code, "tests": tests}
        
        print("\n✅ PROJECT_COMPLETE")
        return results
    
    def _plan(self, requirements: str) -> list[TaskItem]:
        """PM breaks requirements into tasks."""
        plan = self.pm.act(f"""Break these requirements into development tasks.
For each task provide:
- ID (task_1, task_2, etc.)
- Description
- Acceptance criteria

Requirements:
{requirements}""")
        
        # Parse tasks from PM output
        tasks = []
        for i, line in enumerate(plan.split("\n")):
            if line.strip().startswith(f"{i+1}.") or "task_" in line.lower():
                tasks.append(TaskItem(id=f"task_{len(tasks)+1}", description=line.strip()))
        
        # Fallback: if parsing fails, create single task
        if not tasks:
            tasks = [TaskItem(id="task_1", description=requirements)]
        
        self.tasks = tasks
        return tasks
    
    def _develop(self, task: TaskItem) -> str:
        """Developer writes code for the task."""
        context = f"Task: {task.description}"
        if task.review_feedback:
            context += f"\n\nPrevious review feedback to address:\n{task.review_feedback}"
        
        result = self.developer.act(context)
        task.code = result
        task.status = "review"
        return result
    
    def _review_loop(self, task: TaskItem, code: str) -> str:
        """Reviewer checks code, loops with developer if changes needed."""
        for iteration in range(self.max_review_iterations):
            review = self.reviewer.act(f"""Review this code for task: {task.description}

Code:
{code}

Check for: bugs, security issues, code quality, error handling.""")
            
            if "APPROVE" in review:
                print(f"  ✅ Approved on iteration {iteration + 1}")
                task.status = "testing"
                return code
            
            # Request changes — developer fixes
            print(f"  🔄 Changes requested (iteration {iteration + 1})")
            task.review_feedback = review
            code = self.developer.act(f"""Fix your code based on this review feedback:

{review}

Original code:
{code}

Rewrite the complete corrected code.""")
            task.code = code
        
        # Max iterations reached, proceed anyway
        print(f"  ⚠️ Max review iterations reached, proceeding")
        return code
    
    def _test(self, task: TaskItem, code: str) -> str:
        """Tester writes and evaluates tests."""
        tests = self.tester.act(f"""Write comprehensive pytest tests for this code:

Task: {task.description}

Code:
{code}

Write tests covering:
1. Happy path (normal usage)
2. Edge cases (empty input, boundaries)
3. Error cases (invalid input, exceptions)""")
        
        task.tests = tests
        task.status = "done"
        return tests
```

---

## 4. Enhanced Orchestrator with Message Bus

```python
from collections import deque
from datetime import datetime

@dataclass
class TeamMessage:
    sender: AgentRole
    receiver: AgentRole
    content: str
    msg_type: str  # "task", "code", "review", "tests", "feedback"
    timestamp: datetime = field(default_factory=datetime.now)

class MessageDrivenTeam:
    """Event-driven orchestration using message passing."""
    
    def __init__(self):
        self.message_log: list[TeamMessage] = []
        self.queue: deque[TeamMessage] = deque()
        self.agents = {
            AgentRole.PM: pm,
            AgentRole.DEVELOPER: developer,
            AgentRole.REVIEWER: reviewer,
            AgentRole.TESTER: tester,
        }
    
    def send(self, msg: TeamMessage):
        self.queue.append(msg)
        self.message_log.append(msg)
    
    def process(self, requirements: str):
        """Process messages until done."""
        # Kick off with PM
        self.send(TeamMessage(
            sender=AgentRole.PM, receiver=AgentRole.PM,
            content=requirements, msg_type="task",
        ))
        
        max_messages = 20
        for _ in range(max_messages):
            if not self.queue:
                break
            
            msg = self.queue.popleft()
            self._handle_message(msg)
    
    def _handle_message(self, msg: TeamMessage):
        agent = self.agents[msg.receiver]
        
        if msg.msg_type == "task" and msg.receiver == AgentRole.PM:
            result = agent.act(f"Plan this: {msg.content}")
            self.send(TeamMessage(AgentRole.PM, AgentRole.DEVELOPER, result, "task"))
        
        elif msg.msg_type == "task" and msg.receiver == AgentRole.DEVELOPER:
            result = agent.act(f"Implement: {msg.content}")
            self.send(TeamMessage(AgentRole.DEVELOPER, AgentRole.REVIEWER, result, "code"))
        
        elif msg.msg_type == "code" and msg.receiver == AgentRole.REVIEWER:
            result = agent.act(f"Review: {msg.content}")
            if "APPROVE" in result:
                self.send(TeamMessage(AgentRole.REVIEWER, AgentRole.TESTER, msg.content, "code"))
            else:
                self.send(TeamMessage(AgentRole.REVIEWER, AgentRole.DEVELOPER, result, "feedback"))
        
        elif msg.msg_type == "feedback" and msg.receiver == AgentRole.DEVELOPER:
            result = agent.act(f"Fix based on feedback: {msg.content}")
            self.send(TeamMessage(AgentRole.DEVELOPER, AgentRole.REVIEWER, result, "code"))
        
        elif msg.msg_type == "code" and msg.receiver == AgentRole.TESTER:
            result = agent.act(f"Test this code: {msg.content}")
            print(f"🧪 Testing complete: {result[:100]}...")
```

---

## 5. Running the System

```python
# Example usage
if __name__ == "__main__":
    orchestrator = SoftwareTeamOrchestrator()
    
    requirements = """
    Build a URL shortener service with:
    1. POST /shorten - accepts a URL, returns a short code
    2. GET /{code} - redirects to original URL
    3. GET /stats/{code} - returns click count
    
    Requirements:
    - Validate URLs (must be valid http/https)
    - Handle duplicate URLs (return same short code)
    - Thread-safe for concurrent access
    - Short codes should be 6 characters (alphanumeric)
    """
    
    results = orchestrator.run(requirements)
    
    # Save outputs
    for task_id, output in results.items():
        print(f"\n{'='*60}")
        print(f"Task: {task_id}")
        print(f"Code:\n{output['code'][:500]}...")
        print(f"Tests:\n{output['tests'][:500]}...")
```

---

## 6. Monitoring & Improvements

```python
class TeamMetrics:
    """Track team performance."""
    
    def __init__(self):
        self.review_iterations: list[int] = []
        self.task_times: list[float] = []
        self.approval_rate: float = 0.0
    
    def report(self) -> str:
        avg_iterations = sum(self.review_iterations) / max(len(self.review_iterations), 1)
        first_pass_rate = self.review_iterations.count(1) / max(len(self.review_iterations), 1)
        
        return f"""Team Metrics:
- Avg review iterations: {avg_iterations:.1f}
- First-pass approval rate: {first_pass_rate:.0%}
- Tasks completed: {len(self.review_iterations)}
"""

# Improvements to add:
# 1. Persistent memory — developer learns from past review feedback
# 2. Parallel tasks — developer and tester work on different tasks simultaneously
# 3. Escalation — if stuck after N iterations, ask human for help
# 4. Code execution — actually run tests and feed results back
# 5. Context sharing — agents can reference code from other tasks
```

---

## Interview Questions

### Beginner
1. **What agents would you include in a software development team?** PM (breaks requirements into tasks), Developer (writes code), Reviewer (checks quality), Tester (writes tests). Optional: Architect (design decisions), DevOps (deployment), Security (security review). Each has clear role and responsibilities.
2. **Why use iterative review loops?** First code attempt often has issues. Reviewer catches bugs/style problems → Developer fixes → Reviewer re-checks. Mimics real PR workflow. Limit iterations (3-5) to prevent infinite loops. Track iterations as quality metric.
3. **How do you handle task dependencies in multi-agent development?** PM identifies dependencies during planning. Orchestrator ensures dependent tasks wait. Use task graph (DAG) for parallel execution of independent tasks. Developer can reference code from completed tasks via shared context.

### Intermediate
4. **How do you prevent infinite review loops?** Max iteration cap. Track what feedback was given — don't repeat same issues. If same feedback appears twice, escalate to PM/human. Acceptance criteria: be specific about what "good enough" means. Reviewer should APPROVE if non-critical issues remain.
5. **Compare message-passing vs direct orchestration for agent teams.** Direct: orchestrator explicitly calls agents in order. Simple, predictable, easy to debug. Message-passing: agents react to messages. More flexible, easier to add agents, supports async. Direct for simple flows; messages for complex, dynamic collaboration.
6. **How do you share context between agents effectively?** Pass relevant prior outputs (not everything). Summarize long conversations. Use structured formats (code blocks, JSON). Share acceptance criteria to all agents. Reviewer needs: task description + code. Tester needs: task description + code + acceptance criteria.

### Advanced
7. **Design this system for production with 100+ concurrent projects.** Queue-based: tasks in Redis/SQS. Workers (agent instances) pull from queue. State in database (task status, code, reviews). Async execution. Rate limiting per LLM. Caching similar tasks. Priority queue for urgent work. Monitoring: stuck tasks, high iteration counts, token costs.
8. **How would you evaluate the quality of agent-generated code?** Static analysis (linting, type checking). Actually execute tests (not just generate them). Compare against reference implementation. Human evaluation sample. Metrics: bugs found in review, test pass rate, code complexity scores. Track improvement over time.
9. **How would you add learning/improvement to this system?** Log: (task type, developer output, review feedback, iterations needed). Fine-tune developer prompt with common feedback patterns. Cache: similar tasks → reuse approaches. RAG: developer searches past successful code for similar tasks. Team-level: adjust reviewer strictness based on downstream bug rates.

---

## Hands-On Exercise
1. Implement the 4-agent team (PM, Developer, Reviewer, Tester)
2. Build the review loop with max iterations and tracking
3. Add message-bus orchestration as an alternative
4. Run the system on 3 different requirements (URL shortener, calculator API, TODO app)
5. Add metrics tracking (iterations, approval rate)
6. Implement parallel task execution for independent tasks
7. Add human escalation when review loop exceeds max iterations
