# Day 30: Capstone — Production Agent System

## Learning Objectives
- Build a complete production-ready agent system
- Integrate: multi-agent + MCP + memory + safety + observability + eval
- Apply all 30 days of learning in one project
- Deploy with proper reliability and monitoring
- Create a portfolio-worthy capstone project

---

## 1. Capstone Project: Intelligent Research & Report Agent

```
A production agent system that:
1. Accepts research tasks from users
2. Plans research strategy (multi-step)
3. Searches multiple sources (web, docs, APIs)
4. Analyzes and synthesizes findings
5. Generates structured reports with citations
6. Self-evaluates quality before delivery
7. Full observability, safety, and reliability

Tech stack:
- LangGraph (orchestration)
- MCP (tool protocol)
- OpenAI / Anthropic (LLM)
- Redis (state, caching)
- PostgreSQL (persistence)
- FastAPI (API)
- Docker (deployment)
```

---

## 2. System Architecture

```python
"""
┌─────────────────────────────────────────────────────────┐
│                     API Layer (FastAPI)                   │
│  - Auth, rate limiting, request validation               │
└──────────┬──────────────────────────────┬───────────────┘
           │                              │
    ┌──────▼──────┐              ┌────────▼────────┐
    │   Router    │              │  Job Manager    │
    │ (classify)  │              │ (async queue)   │
    └──────┬──────┘              └────────┬────────┘
           │                              │
┌──────────▼──────────────────────────────▼───────────────┐
│              RESEARCH ORCHESTRATOR (LangGraph)            │
│                                                          │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐  │
│  │ Planner │→ │Researcher│→ │Analyzer │→ │ Writer  │  │
│  │  Agent  │  │  Agent   │  │  Agent  │  │  Agent  │  │
│  └─────────┘  └──────────┘  └─────────┘  └─────────┘  │
│       │              │             │            │        │
│  ┌────▼──────────────▼─────────────▼────────────▼───┐   │
│  │              SHARED STATE                         │   │
│  │  (findings, sources, analysis, draft, status)    │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  TOOLS (via MCP)                                  │   │
│  │  - web_search  - doc_search  - summarize         │   │
│  │  - extract     - cite        - validate          │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  SAFETY & QUALITY                                 │   │
│  │  - Input guardrails    - Output validation       │   │
│  │  - Self-evaluation     - Citation verification   │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  OBSERVABILITY                                    │   │
│  │  - Tracing     - Cost tracking   - Logging       │   │
│  │  - Metrics     - Error tracking  - Alerts        │   │
│  └──────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
"""
```

---

## 3. Core Implementation

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator
from openai import OpenAI
from datetime import datetime
import uuid
import json

client = OpenAI()

# --- State Definition ---
class ResearchState(TypedDict):
    task: str
    plan: list[str]
    findings: Annotated[list[dict], operator.add]
    analysis: str
    report: str
    quality_score: float
    status: str
    trace_id: str
    step: int
    cost: float
    errors: list[str]

# --- Agents ---
def planner(state: ResearchState) -> dict:
    """Break research task into sub-questions."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a research planner. Break the task into 3-5 specific research questions."
        }, {"role": "user", "content": state["task"]}],
    )
    plan = response.choices[0].message.content.split("\n")
    plan = [q.strip() for q in plan if q.strip() and q[0].isdigit()]
    return {"plan": plan, "step": state["step"] + 1}

def researcher(state: ResearchState) -> dict:
    """Research each question in the plan."""
    findings = []
    for question in state["plan"]:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Research this question. Provide facts with sources. Be specific and cite evidence."
            }, {"role": "user", "content": question}],
        )
        findings.append({
            "question": question,
            "content": response.choices[0].message.content,
            "source": "llm_knowledge",  # In production: actual web search
        })
    return {"findings": findings, "step": state["step"] + 1}

def analyzer(state: ResearchState) -> dict:
    """Analyze findings, identify key themes and contradictions."""
    findings_text = "\n\n".join(
        f"Q: {f['question']}\nA: {f['content']}" for f in state["findings"]
    )
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Analyze these research findings. Identify: key themes, contradictions, gaps in knowledge, and main conclusions."
        }, {"role": "user", "content": findings_text}],
    )
    return {"analysis": response.choices[0].message.content, "step": state["step"] + 1}

def writer(state: ResearchState) -> dict:
    """Write the final research report."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": """Write a structured research report with:
- Executive Summary
- Key Findings (numbered)
- Analysis
- Conclusions
- Limitations & Future Research
Use markdown formatting. Cite sources where available."""
        }, {"role": "user", "content": f"Task: {state['task']}\n\nAnalysis: {state['analysis']}\n\nFindings: {json.dumps(state['findings'][:5])}"}],
    )
    return {"report": response.choices[0].message.content, "step": state["step"] + 1}

def quality_checker(state: ResearchState) -> dict:
    """Self-evaluate report quality."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Evaluate this report (1-10). Check: completeness, accuracy, clarity, citations, actionability. Reply JSON: {\"score\": n, \"feedback\": \"...\"}"
        }, {"role": "user", "content": f"Task: {state['task']}\n\nReport:\n{state['report']}"}],
    )
    result = json.loads(response.choices[0].message.content)
    return {"quality_score": result["score"] / 10.0, "step": state["step"] + 1}

# --- Routing ---
def should_revise(state: ResearchState) -> str:
    if state["quality_score"] >= 0.7:
        return "done"
    if state["step"] > 10:
        return "done"  # Max iterations
    return "revise"

def reviser(state: ResearchState) -> dict:
    """Revise report based on quality feedback."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Improve this report based on the quality feedback. Make it more complete, accurate, and well-cited."
        }, {"role": "user", "content": f"Report:\n{state['report']}\n\nScore: {state['quality_score']}\n\nPlease improve."}],
    )
    return {"report": response.choices[0].message.content, "step": state["step"] + 1}

# --- Build Graph ---
graph = StateGraph(ResearchState)
graph.add_node("planner", planner)
graph.add_node("researcher", researcher)
graph.add_node("analyzer", analyzer)
graph.add_node("writer", writer)
graph.add_node("quality_check", quality_checker)
graph.add_node("reviser", reviser)

graph.set_entry_point("planner")
graph.add_edge("planner", "researcher")
graph.add_edge("researcher", "analyzer")
graph.add_edge("analyzer", "writer")
graph.add_edge("writer", "quality_check")
graph.add_conditional_edges("quality_check", should_revise, {"done": END, "revise": "reviser"})
graph.add_edge("reviser", "quality_check")

research_agent = graph.compile()
```

---

## 4. API Layer

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import uuid

app = FastAPI(title="Research Agent API")

class ResearchRequest(BaseModel):
    task: str
    max_depth: int = 3
    output_format: str = "markdown"

class ResearchResponse(BaseModel):
    job_id: str
    status: str
    report: str | None = None
    quality_score: float | None = None
    cost: float | None = None

jobs: dict[str, dict] = {}

@app.post("/research", response_model=ResearchResponse)
async def create_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    # Input validation
    if len(request.task) < 10:
        raise HTTPException(400, "Task too short")
    if len(request.task) > 2000:
        raise HTTPException(400, "Task too long")
    
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running", "report": None}
    
    background_tasks.add_task(run_research, job_id, request.task)
    return ResearchResponse(job_id=job_id, status="running")

@app.get("/research/{job_id}", response_model=ResearchResponse)
async def get_research(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return ResearchResponse(
        job_id=job_id, status=job["status"],
        report=job.get("report"), quality_score=job.get("quality_score"),
        cost=job.get("cost"),
    )

async def run_research(job_id: str, task: str):
    try:
        initial_state = {
            "task": task, "plan": [], "findings": [],
            "analysis": "", "report": "", "quality_score": 0.0,
            "status": "running", "trace_id": job_id,
            "step": 0, "cost": 0.0, "errors": [],
        }
        result = research_agent.invoke(initial_state)
        jobs[job_id] = {
            "status": "completed", "report": result["report"],
            "quality_score": result["quality_score"], "cost": result["cost"],
        }
    except Exception as e:
        jobs[job_id] = {"status": "failed", "error": str(e)}
```

---

## 5. Observability & Safety Integration

```python
# Wrap the agent with observability and safety

class ProductionResearchAgent:
    """Full production wrapper around the research agent."""
    
    def __init__(self):
        self.agent = research_agent
        self.tracer = AgentTracer()
        self.cost_tracker = CostTracker()
        self.guardrails = AgentGuardrails()
    
    def run(self, task: str, user_id: str) -> dict:
        # Input validation
        input_check = self.guardrails.validate_input(task)
        if not input_check["allowed"]:
            return {"error": input_check["reason"], "status": "blocked"}
        
        # Start trace
        trace = self.tracer.start_trace(task)
        
        try:
            # Execute agent
            result = self.agent.invoke({
                "task": task, "plan": [], "findings": [],
                "analysis": "", "report": "", "quality_score": 0.0,
                "status": "running", "trace_id": trace.trace_id,
                "step": 0, "cost": 0.0, "errors": [],
            })
            
            # Output validation
            output_check = self.guardrails.validate_output(result["report"])
            if not output_check["allowed"]:
                return {"error": "Output blocked by safety filters", "status": "blocked"}
            
            return {
                "report": output_check.get("output", result["report"]),
                "quality_score": result["quality_score"],
                "cost": self.cost_tracker.total_cost,
                "trace_id": trace.trace_id,
                "steps": result["step"],
                "status": "completed",
            }
        
        except Exception as e:
            return {"error": str(e), "status": "failed", "trace_id": trace.trace_id}
```

---

## 6. Evaluation Suite

```python
class CapstoneEval:
    """Evaluation suite for the capstone project."""
    
    TEST_CASES = [
        {"task": "Research the current state of quantum computing", "min_score": 0.6},
        {"task": "Compare React vs Angular for enterprise applications", "min_score": 0.6},
        {"task": "Explain the latest developments in AI safety research", "min_score": 0.6},
        {"task": "Research best practices for microservices architecture", "min_score": 0.6},
        {"task": "Analyze the impact of remote work on software team productivity", "min_score": 0.6},
    ]
    
    def run_eval(self) -> dict:
        agent = ProductionResearchAgent()
        results = []
        
        for case in self.TEST_CASES:
            result = agent.run(case["task"], user_id="eval")
            results.append({
                "task": case["task"],
                "status": result["status"],
                "quality_score": result.get("quality_score", 0),
                "cost": result.get("cost", 0),
                "steps": result.get("steps", 0),
                "passed": result.get("quality_score", 0) >= case["min_score"],
            })
        
        passed = sum(1 for r in results if r["passed"])
        return {
            "total": len(results),
            "passed": passed,
            "pass_rate": passed / len(results),
            "avg_quality": sum(r["quality_score"] for r in results) / len(results),
            "avg_cost": sum(r["cost"] for r in results) / len(results),
            "avg_steps": sum(r["steps"] for r in results) / len(results),
            "details": results,
        }
```

---

## Interview Questions

### Beginner
1. **What components does a production agent system need?** LLM (reasoning), tools (actions), memory (context), orchestration (flow control), safety (guardrails), observability (tracing + metrics), reliability (retry + fallback), API layer (auth + rate limiting), evaluation (quality checks). All work together — missing any creates production risk.
2. **Why is self-evaluation important in agent systems?** Agent output is non-deterministic — quality varies. Self-eval catches: hallucinations, incomplete answers, low-quality output. Enables: automatic retry/revision if quality is low. Provides: confidence score to user. Alternative: always ship to human reviewer (expensive, slow).
3. **What's the minimum viable production agent?** Core loop (LLM + tools), basic retry logic, input validation, output validation, structured logging, health check endpoint. Not needed for MVP: multi-agent, advanced memory, full observability suite. Add complexity as needed, not upfront.

### Intermediate
4. **How do you decide on the graph structure for a LangGraph agent?** Map the workflow: what steps are always sequential? Where are decision points? Where can work be parallel? Start with happy path (linear). Add: conditional edges for quality gates, loops for revision, branches for escalation. Keep it simple — complex graphs are hard to debug.
5. **How do you balance quality self-evaluation with cost/latency?** Quick checks are cheap (GPT-4o-mini, single call). Deep evaluation is expensive. Strategy: fast check first → if borderline, do deep check. Skip self-eval for simple tasks. Budget: self-eval should be <20% of total cost. Alternative: sample-based eval (evaluate 10% of outputs deeply).
6. **What's your deployment checklist for a production agent?** ✅ Input validation. ✅ Output validation. ✅ Rate limiting. ✅ Error handling + retry. ✅ Timeout on all external calls. ✅ Structured logging. ✅ Cost tracking + budget. ✅ Health check endpoint. ✅ Graceful shutdown. ✅ Eval suite passing. ✅ Load tested. ✅ Security review.

### Advanced
7. **How would you scale this capstone system to handle 100K research tasks/day?** Queue-based: requests → Redis priority queue → worker pool (50-100 containers). Caching: similar tasks → return cached report (embedding similarity). Parallel research: fan-out sub-questions to multiple workers. Cost: model routing (mini for planning, 4o for writing). Monitoring: real-time dashboard, auto-scale on queue depth.
8. **How do you ensure the research agent produces accurate, non-hallucinated reports?** Multi-source verification (cross-reference findings). Citation requirement (every claim → source). Retrieval-augmented (ground in actual documents). Self-RAG (verify against sources before including). Confidence scoring per claim. Human review for high-stakes reports. Evaluation: compare against known-good references.
9. **If you had to build this system for a real company, what would you change?** Add real web search (Tavily, Serper). Real document retrieval (company knowledge base). User management (auth, permissions, history). Streaming responses (show progress). Collaboration (share/edit reports). Templates (recurring research types). Feedback loop (user ratings improve quality). Cost: charge per report based on complexity.

---

## Hands-On Exercise (Full Capstone)
1. Build the LangGraph orchestration (planner → researcher → analyzer → writer → quality)
2. Add self-evaluation loop (revise if quality < 0.7)
3. Wrap with FastAPI (async execution, job polling)
4. Add input/output guardrails
5. Implement tracing and cost tracking
6. Build evaluation suite (5 test cases)
7. Run full eval and report metrics
8. Deploy with Docker (Dockerfile + docker-compose)
9. Write README documenting architecture, setup, and usage
10. Record a 5-minute demo video for your portfolio
