# Day 22: Deployment Architectures

## Learning Objectives
- Design serverless vs container-based agent deployment
- Implement queue-based async agent execution
- Handle scaling strategies for agent workloads
- Optimize cost for LLM-heavy systems
- Build multi-tenant agent platforms

---

## 1. Deployment Options

```
┌───────────────────────────────────────────────────┐
│ Option        │ Best for          │ Trade-offs     │
├───────────────────────────────────────────────────┤
│ Serverless    │ Bursty, low vol   │ Cold starts    │
│ (Lambda/CF)   │ Simple agents     │ 15min timeout  │
├───────────────────────────────────────────────────┤
│ Containers    │ Long-running      │ Always-on cost │
│ (ECS/K8s)    │ Complex agents    │ More ops       │
├───────────────────────────────────────────────────┤
│ Queue-based   │ High volume       │ Latency        │
│ (SQS+Worker) │ Background tasks  │ Complexity     │
├───────────────────────────────────────────────────┤
│ Hybrid        │ Production        │ Most complex   │
│               │ Multi-pattern     │ Best overall   │
└───────────────────────────────────────────────────┘
```

---

## 2. Serverless Agent

```python
# AWS Lambda handler for simple agents
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

def lambda_handler(event, context):
    """Serverless agent execution."""
    body = json.loads(event.get("body", "{}"))
    task = body.get("task", "")
    
    # Simple agent loop (must complete within timeout)
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": task},
    ]
    
    tools = load_tools()  # Load tool definitions
    
    max_steps = 5
    for _ in range(max_steps):
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, tools=tools,
        )
        msg = response.choices[0].message
        
        if not msg.tool_calls:
            return {"statusCode": 200, "body": json.dumps({"result": msg.content})}
        
        messages.append(msg)
        for tc in msg.tool_calls:
            result = execute_tool(tc.function.name, json.loads(tc.function.arguments))
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    
    return {"statusCode": 200, "body": json.dumps({"result": messages[-1].get("content", "")})}

# Limitations:
# - 15 min max execution time
# - No persistent connections/state
# - Cold starts add latency
# - Memory limited (10GB max)
```

---

## 3. Container-Based (Long-Running)

```python
# Dockerfile for agent service
"""
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# FastAPI agent service
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uuid

app = FastAPI()

class AgentRequest(BaseModel):
    task: str
    config: dict = {}

class AgentResponse(BaseModel):
    job_id: str
    status: str
    result: str | None = None

# In-memory job store (use Redis in production)
jobs: dict[str, dict] = {}

@app.post("/agent/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest, background_tasks: BackgroundTasks):
    """Start agent execution (async)."""
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running", "result": None}
    
    background_tasks.add_task(execute_agent, job_id, request.task, request.config)
    return AgentResponse(job_id=job_id, status="running")

@app.get("/agent/status/{job_id}", response_model=AgentResponse)
async def get_status(job_id: str):
    """Check agent job status."""
    job = jobs.get(job_id)
    if not job:
        return AgentResponse(job_id=job_id, status="not_found")
    return AgentResponse(job_id=job_id, status=job["status"], result=job["result"])

async def execute_agent(job_id: str, task: str, config: dict):
    """Long-running agent execution."""
    try:
        result = await run_agent_loop(task, config)  # Your agent logic
        jobs[job_id] = {"status": "completed", "result": result}
    except Exception as e:
        jobs[job_id] = {"status": "failed", "result": str(e)}
```

---

## 4. Queue-Based Architecture

```python
# Producer: API receives requests, puts on queue
# Consumer: Worker pulls from queue, runs agent

import redis
import json
from datetime import datetime

class AgentQueue:
    """Queue-based agent execution with Redis."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis = redis.from_url(redis_url)
        self.queue_name = "agent:tasks"
        self.results_prefix = "agent:result:"
    
    def submit(self, task: str, priority: int = 0, config: dict = None) -> str:
        """Submit task to queue, return job ID."""
        job_id = str(uuid.uuid4())
        job = {
            "id": job_id,
            "task": task,
            "config": config or {},
            "priority": priority,
            "submitted_at": datetime.now().isoformat(),
        }
        
        # Use sorted set for priority queue
        self.redis.zadd(self.queue_name, {json.dumps(job): priority})
        self.redis.set(f"{self.results_prefix}{job_id}", json.dumps({"status": "queued"}))
        return job_id
    
    def get_result(self, job_id: str) -> dict | None:
        """Check result of a job."""
        data = self.redis.get(f"{self.results_prefix}{job_id}")
        return json.loads(data) if data else None

class AgentWorker:
    """Worker that processes agent tasks from queue."""
    
    def __init__(self, queue: AgentQueue):
        self.queue = queue
        self.running = True
    
    def run(self):
        """Main worker loop."""
        while self.running:
            # Pop highest priority task
            items = self.queue.redis.zpopmax(self.queue.queue_name, count=1)
            if not items:
                import time; time.sleep(1)
                continue
            
            job = json.loads(items[0][0])
            job_id = job["id"]
            
            # Update status
            self.queue.redis.set(
                f"{self.queue.results_prefix}{job_id}",
                json.dumps({"status": "running"}),
            )
            
            # Execute agent
            try:
                result = self._execute(job["task"], job["config"])
                self.queue.redis.set(
                    f"{self.queue.results_prefix}{job_id}",
                    json.dumps({"status": "completed", "result": result}),
                )
            except Exception as e:
                self.queue.redis.set(
                    f"{self.queue.results_prefix}{job_id}",
                    json.dumps({"status": "failed", "error": str(e)}),
                )
    
    def _execute(self, task: str, config: dict) -> str:
        """Run the agent (your agent logic here)."""
        # ... agent execution ...
        return "Agent completed task"
```

---

## 5. Scaling Strategies

```python
# Auto-scaling based on queue depth and latency

class ScalingConfig:
    """Configuration for auto-scaling agent workers."""
    
    min_workers: int = 1
    max_workers: int = 20
    scale_up_threshold: int = 10     # Queue depth to trigger scale-up
    scale_down_threshold: int = 2    # Queue depth to trigger scale-down
    cooldown_seconds: int = 60       # Wait between scaling events
    
    # Cost optimization
    max_concurrent_llm_calls: int = 50  # Limit parallel LLM API calls
    prefer_spot_instances: bool = True   # Use cheap instances when possible

class CostOptimizer:
    """Optimize LLM costs for agent workloads."""
    
    def __init__(self):
        self.model_costs = {
            "gpt-4o": 0.005,       # per 1K tokens
            "gpt-4o-mini": 0.00015,
            "claude-3-haiku": 0.00025,
        }
    
    def select_model(self, task_complexity: str, budget_remaining: float) -> str:
        """Route to appropriate model based on complexity and budget."""
        if budget_remaining < 0.01:
            return "gpt-4o-mini"  # Cheapest
        
        model_map = {
            "low": "gpt-4o-mini",
            "medium": "gpt-4o-mini",
            "high": "gpt-4o",
        }
        return model_map.get(task_complexity, "gpt-4o-mini")
    
    def estimate_cost(self, task: str, model: str, estimated_steps: int = 5) -> float:
        """Estimate cost before execution."""
        avg_tokens_per_step = 2000
        total_tokens = avg_tokens_per_step * estimated_steps
        return (total_tokens / 1000) * self.model_costs.get(model, 0.005)
```

---

## 6. Multi-Tenant Architecture

```python
class MultiTenantAgentPlatform:
    """Serve multiple tenants with isolated agent execution."""
    
    def __init__(self):
        self.tenant_configs: dict[str, dict] = {}
        self.rate_limiters: dict[str, RateLimiter] = {}
    
    def register_tenant(self, tenant_id: str, config: dict):
        """Register a tenant with their configuration."""
        self.tenant_configs[tenant_id] = {
            "api_key": config["api_key"],       # Their LLM API key or use ours
            "max_requests_per_minute": config.get("rpm", 60),
            "max_tokens_per_day": config.get("daily_tokens", 1_000_000),
            "allowed_tools": config.get("tools", ["search", "calculate"]),
            "model": config.get("model", "gpt-4o-mini"),
        }
        self.rate_limiters[tenant_id] = RateLimiter(
            max_calls=config.get("rpm", 60), period=60,
        )
    
    def execute(self, tenant_id: str, task: str) -> dict:
        """Execute agent for a specific tenant."""
        config = self.tenant_configs.get(tenant_id)
        if not config:
            return {"error": "Tenant not found"}
        
        # Rate limiting
        if not self.rate_limiters[tenant_id].allow():
            return {"error": "Rate limit exceeded"}
        
        # Run with tenant's configuration
        agent = create_agent(
            model=config["model"],
            tools=config["allowed_tools"],
            api_key=config["api_key"],
        )
        
        result = agent.run(task)
        
        # Track usage
        self._track_usage(tenant_id, result)
        return {"result": result}
    
    def _track_usage(self, tenant_id: str, result: dict):
        """Track token usage per tenant for billing."""
        # Log to usage tracking system
        pass
```

---

## Interview Questions

### Beginner
1. **When would you choose serverless vs containers for agents?** Serverless: simple agents, bursty traffic, low volume, cost-sensitive (pay per use). Containers: long-running agents (>15 min), persistent connections needed, complex multi-step workflows, predictable high traffic. Containers also needed for stateful agents.
2. **Why use a queue for agent execution?** Decouples request from execution. Benefits: handle traffic spikes (queue absorbs), retry failed jobs, priority ordering, rate limit LLM API calls, scale workers independently. User gets immediate response (job ID) while agent runs async.
3. **What's the main challenge of scaling agents?** LLM API rate limits: can't just add more workers indefinitely. Cost: more agents = more LLM calls = higher bills. State management: agents need context across steps. Coordination: avoid duplicate work. Solution: rate limiting + queuing + caching.

### Intermediate
4. **How do you optimize costs for an agent platform?** Model routing (cheap model for simple tasks). Caching (repeated queries → cached results). Prompt optimization (shorter prompts). Batch processing (combine similar requests). Token budgets per task. Spot/preemptible instances for workers. Monitor and alert on cost spikes.
5. **Design a queue-based system for handling 1000 agent requests/minute.** Priority queue (Redis sorted set). Worker pool (10-50 workers, auto-scale on queue depth). Rate limiter per LLM provider. Deduplication (same query → return cached result). Circuit breaker (stop sending if LLM errors). DLQ for failed jobs. Monitoring: queue depth, latency, error rate.
6. **How do you handle long-running agents (>1 hour)?** Checkpointing: save state periodically. Heartbeat: worker reports alive. Timeout: kill after max duration. Resume: if worker dies, another picks up from checkpoint. Progress tracking: report % complete. Async: user doesn't wait, gets notified on completion.

### Advanced
7. **Design a multi-tenant agent platform with isolation and billing.** Tenant isolation: separate queues or priority lanes. Resource quotas: max tokens/day, max concurrent agents. Billing: track tokens per tenant, usage-based pricing. Security: tools scoped to tenant's data. Performance: noisy neighbor prevention (one tenant can't starve others). SLAs: guaranteed latency per tier.
8. **How do you handle cold starts and latency in serverless agents?** Provisioned concurrency (keep warm instances). First response prediction (start generating while loading). Model caching (keep model client warm). Smaller runtime (Alpine, minimal deps). Connection pooling. Hybrid: frequently-used agents stay in containers, rare ones go serverless.
9. **Design a deployment architecture for a coding agent that needs Docker.** Agent runs inside a container. Spawns sibling containers for code execution (Docker-in-Docker or sidecar pattern). Kubernetes: agent pod + code sandbox pod (shared volume). Networking: sandbox has no internet. Cleanup: kill sandbox after task. Resource limits: CPU/memory per sandbox.

---

## Hands-On Exercise
1. Build a FastAPI agent service with async execution and job polling
2. Implement Redis-based priority queue for agent tasks
3. Create a worker that processes tasks from the queue
4. Add auto-scaling logic based on queue depth
5. Implement cost estimation and model routing
6. Build simple multi-tenant isolation (per-tenant rate limits and config)
