# Day 12: Orchestration Patterns

## Learning Objectives
- Implement fan-out/fan-in parallel execution
- Build pipeline and supervisor patterns
- Design debate and voting systems
- Create escalation and dynamic routing logic
- Choose the right orchestration pattern for each use case

---

## 1. Fan-Out / Fan-In (Parallel Execution)

```python
# Fan-out: Distribute work to multiple agents simultaneously
# Fan-in: Collect and synthesize results

import asyncio
from dataclasses import dataclass
from openai import AsyncOpenAI

client = AsyncOpenAI()

@dataclass
class AgentResult:
    agent_name: str
    result: str
    confidence: float

async def run_agent(name: str, system_prompt: str, task: str) -> AgentResult:
    """Run a single agent asynchronously."""
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task},
        ],
    )
    return AgentResult(agent_name=name, result=response.choices[0].message.content, confidence=0.8)

async def fan_out_fan_in(task: str) -> str:
    """Send task to multiple specialists, synthesize results."""
    agents = [
        ("Security Expert", "You analyze security implications."),
        ("Performance Expert", "You analyze performance implications."),
        ("UX Expert", "You analyze user experience implications."),
    ]
    
    # Fan-out: run all agents in parallel
    tasks = [run_agent(name, prompt, task) for name, prompt in agents]
    results: list[AgentResult] = await asyncio.gather(*tasks)
    
    # Fan-in: synthesize
    synthesis_prompt = "Synthesize these expert opinions into a unified recommendation:\n\n"
    for r in results:
        synthesis_prompt += f"**{r.agent_name}**: {r.result}\n\n"
    
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You synthesize expert opinions into clear recommendations."},
            {"role": "user", "content": synthesis_prompt},
        ],
    )
    return response.choices[0].message.content

# Usage
# result = asyncio.run(fan_out_fan_in("Should we add OAuth2 to our API?"))
```

---

## 2. Pipeline Pattern

```python
# Pipeline: Sequential processing where each stage transforms data
# Each agent specializes in one transformation step

class PipelineStage:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
    
    async def process(self, input_data: str) -> str:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": input_data},
            ],
        )
        return response.choices[0].message.content

class Pipeline:
    def __init__(self, stages: list[PipelineStage]):
        self.stages = stages
    
    async def run(self, initial_input: str) -> str:
        data = initial_input
        for stage in self.stages:
            print(f"  → Stage: {stage.name}")
            data = stage.process(data) if not asyncio.iscoroutinefunction(stage.process) else await stage.process(data)
        return data

# Example: Content creation pipeline
content_pipeline = Pipeline([
    PipelineStage("Research", "Extract key facts and data points from the topic."),
    PipelineStage("Outline", "Create a structured outline from these facts."),
    PipelineStage("Draft", "Write a full draft based on this outline."),
    PipelineStage("Edit", "Polish this draft: fix grammar, improve clarity, tighten prose."),
])

# result = asyncio.run(content_pipeline.run("AI agents in production 2025"))
```

---

## 3. Supervisor Pattern

```python
# Supervisor: One agent manages and directs worker agents
# Supervisor decides: who works next, what they work on, when to stop

class Supervisor:
    def __init__(self, workers: dict[str, str]):
        """workers: {name: system_prompt}"""
        self.workers = workers
    
    async def decide_next(self, task: str, history: list[dict]) -> dict:
        """Supervisor decides which worker should act next."""
        worker_list = ", ".join(self.workers.keys())
        history_text = "\n".join(f"[{h['worker']}]: {h['result'][:200]}" for h in history[-5:])
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": f"""You are a supervisor managing workers: {worker_list}.
Given the task and work history, decide:
1. Which worker should act next (or "DONE" if task is complete)
2. What specific instruction to give them
Reply as JSON: {{"worker": "name", "instruction": "what to do"}}"""
            }, {"role": "user", "content": f"Task: {task}\n\nHistory:\n{history_text}"}],
        )
        import json
        return json.loads(response.choices[0].message.content)
    
    async def run(self, task: str, max_rounds: int = 10) -> str:
        history = []
        for _ in range(max_rounds):
            decision = await self.decide_next(task, history)
            if decision["worker"] == "DONE":
                break
            
            worker_name = decision["worker"]
            result = await run_agent(
                worker_name, self.workers[worker_name], decision["instruction"]
            )
            history.append({"worker": worker_name, "result": result.result})
        
        return history[-1]["result"] if history else "No work done"

# Usage
supervisor = Supervisor({
    "researcher": "You research topics and find relevant information.",
    "coder": "You write clean Python code.",
    "tester": "You write unit tests.",
})
```

---

## 4. Debate Pattern

```python
# Debate: Agents argue different positions, then a judge decides
# Good for: decision-making, exploring trade-offs, finding flaws

async def debate(topic: str, rounds: int = 3) -> str:
    """Two agents debate, judge decides."""
    
    pro_messages = [{"role": "system", "content": "You argue IN FAVOR of the proposal. Be persuasive but honest."}]
    con_messages = [{"role": "system", "content": "You argue AGAINST the proposal. Find weaknesses and risks."}]
    
    debate_history = []
    
    for round_num in range(rounds):
        # Pro argues
        pro_messages.append({"role": "user", "content": f"Round {round_num+1}. Topic: {topic}\nPrevious debate: {debate_history[-2:] if debate_history else 'None'}"})
        pro_response = await client.chat.completions.create(model="gpt-4o", messages=pro_messages)
        pro_arg = pro_response.choices[0].message.content
        debate_history.append(f"PRO: {pro_arg}")
        
        # Con argues
        con_messages.append({"role": "user", "content": f"Round {round_num+1}. Pro's argument: {pro_arg}\nRespond with counter-arguments."})
        con_response = await client.chat.completions.create(model="gpt-4o", messages=con_messages)
        con_arg = con_response.choices[0].message.content
        debate_history.append(f"CON: {con_arg}")
    
    # Judge decides
    judge_response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are an impartial judge. Evaluate both sides and give a reasoned verdict."
        }, {"role": "user", "content": f"Topic: {topic}\n\nDebate:\n" + "\n\n".join(debate_history)}],
    )
    return judge_response.choices[0].message.content
```

---

## 5. Voting Pattern

```python
# Voting: Multiple agents independently answer, majority wins
# Good for: factual questions, reducing hallucination

async def voting(question: str, num_voters: int = 5) -> str:
    """Multiple agents answer independently, aggregate results."""
    
    tasks = []
    for i in range(num_voters):
        tasks.append(client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": f"Answer concisely. Voter {i}."
            }, {"role": "user", "content": question}],
            temperature=0.7,  # Some variation
        ))
    
    responses = await asyncio.gather(*tasks)
    answers = [r.choices[0].message.content for r in responses]
    
    # Aggregate (use LLM to find consensus since answers may be worded differently)
    agg_response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Find the consensus answer from these responses. Return the most common/agreed-upon answer."
        }, {"role": "user", "content": "\n\n".join(f"Voter {i}: {a}" for i, a in enumerate(answers))}],
    )
    return agg_response.choices[0].message.content
```

---

## 6. Escalation & Dynamic Routing

```python
# Escalation: Route to more capable/expensive agent when needed
# Dynamic routing: Choose agent based on task characteristics

class Router:
    """Route tasks to appropriate agents based on complexity and type."""
    
    async def classify(self, task: str) -> dict:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Cheap model for routing
            messages=[{"role": "system", "content": """Classify this task.
Return JSON: {"type": "code|research|creative|analysis", "complexity": "low|medium|high"}"""
            }, {"role": "user", "content": task}],
        )
        import json
        return json.loads(response.choices[0].message.content)
    
    async def route(self, task: str) -> str:
        classification = await self.classify(task)
        
        # Route based on type
        agent_map = {
            "code": "Expert Python developer.",
            "research": "Research analyst with web access.",
            "creative": "Creative writer.",
            "analysis": "Data analyst.",
        }
        
        # Escalation based on complexity
        model = {
            "low": "gpt-4o-mini",
            "medium": "gpt-4o",
            "high": "gpt-4o",  # Could use o1 for highest complexity
        }[classification["complexity"]]
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": agent_map[classification["type"]]},
                {"role": "user", "content": task},
            ],
        )
        return response.choices[0].message.content

# Escalation pattern: try cheap first, escalate if quality is low
async def escalation(task: str) -> str:
    # Try with cheap model first
    response = await client.chat.completions.create(
        model="gpt-4o-mini", messages=[{"role": "user", "content": task}]
    )
    result = response.choices[0].message.content
    
    # Quality check
    check = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Is this answer complete and accurate? Reply YES or NO.\nQuestion: {task}\nAnswer: {result}"}],
    )
    
    if "NO" in check.choices[0].message.content.upper():
        # Escalate to stronger model
        response = await client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": task}]
        )
        return response.choices[0].message.content
    
    return result
```

---

## Interview Questions

### Beginner
1. **What is the fan-out/fan-in pattern?** Fan-out: distribute same task to multiple agents in parallel (e.g., 3 experts analyze a PR). Fan-in: collect all results and synthesize into unified output. Benefits: faster (parallel), diverse perspectives, covers multiple angles.
2. **When would you use a pipeline pattern?** When work is naturally sequential: each stage transforms output for the next. Examples: research → outline → draft → edit; parse → analyze → visualize. Each agent specializes in one step. Clear data flow.
3. **What's the supervisor pattern?** One manager agent decides: which worker acts next, what instruction to give, when work is done. Like a project manager. Benefits: dynamic workflow (not fixed), can adapt based on intermediate results, handles unexpected situations.

### Intermediate
4. **How does the debate pattern improve decision quality?** Forces exploration of both sides. Pro agent finds benefits; con agent finds risks. Neither alone sees full picture. Judge synthesizes balanced view. Reduces: confirmation bias, blind spots, overconfidence. Best for: consequential decisions with trade-offs.
5. **Compare voting vs debate for quality improvement.** Voting: same question asked independently, majority wins. Reduces random errors. Best for factual questions. Debate: structured argumentation, explores trade-offs. Best for subjective decisions. Voting is cheaper (parallel, no interaction). Debate is deeper (iterative refinement).
6. **How do you implement escalation without wasting tokens?** Start with cheapest model. Add quality gate (fast check: is answer complete?). Only escalate if quality is insufficient. Track escalation rates — if >50%, just use the better model. Use routing to avoid obvious mismatches (complex task → strong model directly).

### Advanced
7. **Design an orchestration system that combines multiple patterns.** Router classifies incoming task → routes to appropriate pattern. Simple tasks: single agent. Multi-perspective: fan-out/fan-in. Sequential work: pipeline. Complex decisions: debate. Uncertain: voting. Supervisor oversees, can switch patterns mid-task if results are poor.
8. **How do you handle failures in parallel fan-out execution?** Set timeouts per agent. If one agent fails: proceed with remaining results (graceful degradation). Retry with backoff for transient failures. Track which agents fail often. Minimum quorum: need at least N results to synthesize. Fallback: sequential execution if parallel fails.
9. **Design a dynamic routing system that learns from past results.** Log: task → route taken → quality score. Train classifier on successful routes. A/B test: try different routes for similar tasks. Track: cost, latency, quality per route. Over time: routing improves, fewer escalations. Use embeddings to find similar past tasks and their best routes.

---

## Hands-On Exercise
1. Implement fan-out/fan-in with 3 specialist agents analyzing a codebase
2. Build a 4-stage pipeline (research → outline → draft → edit)
3. Create a supervisor that dynamically assigns work to 3 workers
4. Implement a debate between pro/con agents with a judge
5. Build a router that classifies tasks and routes to appropriate agents
6. Add escalation: try cheap model first, escalate if quality check fails
