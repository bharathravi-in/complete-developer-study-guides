# Day 23: Observability & Debugging

## Learning Objectives
- Implement distributed tracing for agent execution
- Build structured logging for multi-step workflows
- Track token usage, cost, and latency per step
- Design error recovery and replay systems
- Debug complex agent failures

---

## 1. Agent Tracing

```python
import uuid
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

@dataclass
class Span:
    """Single operation within a trace."""
    name: str
    trace_id: str
    span_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    parent_id: str | None = None
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    attributes: dict = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)
    status: str = "running"  # running, completed, error
    
    def end(self, status: str = "completed"):
        self.end_time = time.time()
        self.status = status
    
    @property
    def duration_ms(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time) * 1000
        return 0

@dataclass
class Trace:
    """Complete trace of an agent execution."""
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    spans: list[Span] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def start_span(self, name: str, parent_id: str = None, **attrs) -> Span:
        span = Span(name=name, trace_id=self.trace_id, parent_id=parent_id, attributes=attrs)
        self.spans.append(span)
        return span
    
    @property
    def total_duration_ms(self) -> float:
        if not self.spans:
            return 0
        start = min(s.start_time for s in self.spans)
        end = max(s.end_time or time.time() for s in self.spans)
        return (end - start) * 1000
    
    def summary(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "total_duration_ms": self.total_duration_ms,
            "total_spans": len(self.spans),
            "errors": sum(1 for s in self.spans if s.status == "error"),
            "spans": [{"name": s.name, "duration_ms": s.duration_ms, "status": s.status} for s in self.spans],
        }

class AgentTracer:
    """Traces agent execution for observability."""
    
    def __init__(self):
        self.traces: list[Trace] = []
        self.current_trace: Trace | None = None
    
    def start_trace(self, task: str) -> Trace:
        trace = Trace(metadata={"task": task, "started_at": datetime.now().isoformat()})
        self.current_trace = trace
        self.traces.append(trace)
        return trace
    
    def trace_llm_call(self, model: str, messages: list, response: Any, span: Span):
        """Record LLM call details."""
        usage = getattr(response, 'usage', None)
        span.attributes.update({
            "model": model,
            "input_tokens": usage.prompt_tokens if usage else 0,
            "output_tokens": usage.completion_tokens if usage else 0,
            "total_tokens": usage.total_tokens if usage else 0,
        })
    
    def trace_tool_call(self, tool_name: str, args: dict, result: str, span: Span):
        """Record tool execution."""
        span.attributes.update({
            "tool": tool_name,
            "args": str(args)[:200],
            "result_length": len(result),
        })
```

---

## 2. Structured Logging

```python
import logging
import json
from contextvars import ContextVar

# Context for request tracking
current_trace_id: ContextVar[str] = ContextVar('trace_id', default='')
current_step: ContextVar[int] = ContextVar('step', default=0)

class StructuredLogger:
    """JSON structured logging for agents."""
    
    def __init__(self, service_name: str):
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def log(self, level: str, event: str, **kwargs):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "event": event,
            "trace_id": current_trace_id.get(''),
            "step": current_step.get(0),
            **kwargs,
        }
        self.logger.log(getattr(logging, level.upper()), json.dumps(entry))
    
    def log_llm_call(self, model: str, tokens: int, latency_ms: float, cost: float):
        self.log("info", "llm_call", model=model, tokens=tokens, latency_ms=latency_ms, cost=cost)
    
    def log_tool_call(self, tool: str, success: bool, latency_ms: float):
        self.log("info", "tool_call", tool=tool, success=success, latency_ms=latency_ms)
    
    def log_error(self, error: str, step: str, recoverable: bool = True):
        self.log("error", "agent_error", error=error, step=step, recoverable=recoverable)
    
    def log_step(self, step_num: int, action: str, thought: str = ""):
        self.log("info", "agent_step", step_num=step_num, action=action, thought=thought[:200])

logger = StructuredLogger("agent-service")
```

---

## 3. Token & Cost Tracking

```python
class CostTracker:
    """Track token usage and costs across agent execution."""
    
    MODEL_COSTS = {
        "gpt-4o": {"input": 2.50, "output": 10.00},      # per 1M tokens
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    }
    
    def __init__(self):
        self.calls: list[dict] = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
    
    def record(self, model: str, input_tokens: int, output_tokens: int):
        costs = self.MODEL_COSTS.get(model, {"input": 5.0, "output": 15.0})
        cost = (input_tokens * costs["input"] + output_tokens * costs["output"]) / 1_000_000
        
        self.calls.append({"model": model, "input": input_tokens, "output": output_tokens, "cost": cost})
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += cost
    
    def summary(self) -> dict:
        return {
            "total_calls": len(self.calls),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": round(self.total_cost, 6),
            "avg_cost_per_call": round(self.total_cost / max(len(self.calls), 1), 6),
        }
    
    def check_budget(self, budget: float) -> bool:
        """Return True if within budget."""
        return self.total_cost < budget

class LatencyTracker:
    """Track latency breakdown per component."""
    
    def __init__(self):
        self.measurements: dict[str, list[float]] = {}
    
    def record(self, component: str, latency_ms: float):
        self.measurements.setdefault(component, []).append(latency_ms)
    
    def summary(self) -> dict:
        result = {}
        for component, values in self.measurements.items():
            sorted_vals = sorted(values)
            result[component] = {
                "count": len(values),
                "avg_ms": sum(values) / len(values),
                "p50_ms": sorted_vals[len(values) // 2],
                "p95_ms": sorted_vals[int(len(values) * 0.95)] if len(values) >= 20 else sorted_vals[-1],
                "total_ms": sum(values),
            }
        return result
```

---

## 4. Error Recovery

```python
class ErrorRecovery:
    """Handle and recover from agent errors."""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.error_handlers: dict[str, callable] = {}
    
    def register_handler(self, error_type: str, handler: callable):
        self.error_handlers[error_type] = handler
    
    def handle_error(self, error: Exception, context: dict) -> dict:
        """Classify error and attempt recovery."""
        error_type = self._classify_error(error)
        
        if error_type == "rate_limit":
            return {"action": "retry", "delay_seconds": 60, "reason": "Rate limited"}
        elif error_type == "timeout":
            return {"action": "retry", "delay_seconds": 5, "reason": "Timeout, retrying"}
        elif error_type == "context_length":
            return {"action": "truncate", "reason": "Context too long, truncating history"}
        elif error_type == "invalid_tool":
            return {"action": "skip", "reason": "Tool call invalid, skipping"}
        elif error_type == "api_error":
            return {"action": "fallback_model", "reason": "API error, trying fallback"}
        else:
            return {"action": "abort", "reason": f"Unrecoverable error: {error}"}
    
    def _classify_error(self, error: Exception) -> str:
        error_str = str(error).lower()
        if "rate limit" in error_str or "429" in error_str:
            return "rate_limit"
        elif "timeout" in error_str:
            return "timeout"
        elif "context length" in error_str or "maximum" in error_str:
            return "context_length"
        elif "tool" in error_str and "not found" in error_str:
            return "invalid_tool"
        elif "500" in error_str or "502" in error_str or "503" in error_str:
            return "api_error"
        return "unknown"

class AgentWithRecovery:
    """Agent with built-in error recovery."""
    
    def __init__(self):
        self.recovery = ErrorRecovery()
        self.cost_tracker = CostTracker()
    
    def run(self, task: str, budget: float = 1.0) -> str:
        retries = 0
        while retries < 3:
            try:
                if not self.cost_tracker.check_budget(budget):
                    return "Budget exceeded. Returning best result so far."
                return self._execute(task)
            except Exception as e:
                action = self.recovery.handle_error(e, {"task": task, "retries": retries})
                
                if action["action"] == "retry":
                    import time; time.sleep(action.get("delay_seconds", 1))
                    retries += 1
                elif action["action"] == "abort":
                    raise
                elif action["action"] == "fallback_model":
                    return self._execute(task, model="gpt-4o-mini")
        
        return "Max retries exceeded"
    
    def _execute(self, task: str, model: str = "gpt-4o") -> str:
        # Agent execution logic
        return "result"
```

---

## 5. Replay & Debugging

```python
class TraceReplay:
    """Replay agent execution from saved traces for debugging."""
    
    def __init__(self, trace: Trace):
        self.trace = trace
        self.spans = trace.spans
    
    def analyze_failure(self) -> dict:
        """Analyze where the agent went wrong."""
        error_spans = [s for s in self.spans if s.status == "error"]
        slow_spans = sorted(self.spans, key=lambda s: s.duration_ms, reverse=True)[:3]
        
        return {
            "total_steps": len(self.spans),
            "errors": [{"name": s.name, "attrs": s.attributes} for s in error_spans],
            "slowest_steps": [{"name": s.name, "duration_ms": s.duration_ms} for s in slow_spans],
            "total_duration_ms": self.trace.total_duration_ms,
            "timeline": self._build_timeline(),
        }
    
    def _build_timeline(self) -> list[dict]:
        return [
            {
                "step": i,
                "name": s.name,
                "duration_ms": s.duration_ms,
                "status": s.status,
                "key_attrs": {k: v for k, v in s.attributes.items() if k in ["model", "tool", "error"]},
            }
            for i, s in enumerate(self.spans)
        ]
    
    def replay_to_step(self, step: int) -> list[Span]:
        """Get trace up to a specific step for debugging."""
        return self.spans[:step]

class DebugDashboard:
    """Aggregate metrics for debugging."""
    
    def __init__(self, traces: list[Trace]):
        self.traces = traces
    
    def overview(self) -> dict:
        total = len(self.traces)
        successful = sum(1 for t in self.traces if all(s.status != "error" for s in t.spans))
        return {
            "total_traces": total,
            "success_rate": successful / max(total, 1),
            "avg_duration_ms": sum(t.total_duration_ms for t in self.traces) / max(total, 1),
            "avg_steps": sum(len(t.spans) for t in self.traces) / max(total, 1),
            "common_errors": self._common_errors(),
        }
    
    def _common_errors(self) -> list[dict]:
        from collections import Counter
        errors = []
        for t in self.traces:
            for s in t.spans:
                if s.status == "error":
                    errors.append(s.attributes.get("error", s.name))
        return [{"error": e, "count": c} for e, c in Counter(errors).most_common(5)]
```

---

## 6. Production Monitoring

```python
# Key metrics to monitor:

class AgentMetrics:
    """Production metrics for agent monitoring."""
    
    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "latencies": [],
        }
    
    def record_request(self, success: bool, latency_ms: float, tokens: int, cost: float):
        self.metrics["requests_total"] += 1
        if success:
            self.metrics["requests_success"] += 1
        else:
            self.metrics["requests_failed"] += 1
        self.metrics["total_tokens"] += tokens
        self.metrics["total_cost"] += cost
        self.metrics["latencies"].append(latency_ms)
    
    def get_dashboard(self) -> dict:
        latencies = sorted(self.metrics["latencies"]) if self.metrics["latencies"] else [0]
        n = len(latencies)
        return {
            "success_rate": self.metrics["requests_success"] / max(self.metrics["requests_total"], 1),
            "error_rate": self.metrics["requests_failed"] / max(self.metrics["requests_total"], 1),
            "avg_latency_ms": sum(latencies) / max(n, 1),
            "p50_latency_ms": latencies[n // 2],
            "p95_latency_ms": latencies[int(n * 0.95)],
            "total_cost_usd": self.metrics["total_cost"],
            "avg_tokens_per_request": self.metrics["total_tokens"] / max(self.metrics["requests_total"], 1),
        }

# Alerts:
# - Success rate < 95% → page on-call
# - P95 latency > 30s → investigate
# - Cost spike > 2x daily average → alert
# - Error rate > 10% → circuit breaker
```

---

## Interview Questions

### Beginner
1. **Why is observability important for agents?** Agents are non-deterministic: same input → different paths. Without observability: can't debug failures, track costs, or understand behavior. Need: traces (what happened), metrics (how well), logs (details). Critical for production trust.
2. **What should you log for each agent step?** Step number, action taken (tool call or generate), input/output summary, tokens used, latency, success/failure. For tool calls: tool name, arguments, result. For LLM: model, tokens, cost. Trace ID to correlate steps within one execution.
3. **What is a trace in the context of agents?** A trace is the complete record of one agent execution: all steps from start to finish. Contains spans (individual operations). Shows: what tools were called, in what order, how long each took, where errors occurred. Like a stack trace but for multi-step agent workflows.

### Intermediate
4. **How do you track and control costs in production agents?** Per-request cost tracking (model × tokens). Budget limits per request, per user, per day. Cost estimation before execution (predict tokens needed). Alerts on anomalies. Model routing (cheap model for simple tasks). Caching repeated calls. Token budgets that stop execution early.
5. **Design an error recovery strategy for production agents.** Classify errors: transient (retry), permanent (abort), recoverable (fallback). Rate limits: exponential backoff. Timeouts: retry with shorter context. Context length: truncate history. API errors: failover to alternate provider. Always: log error, track frequency, alert on patterns.
6. **How do you debug a failing agent when you can't reproduce the issue?** Replay from trace: saved state at each step, re-execute from failure point. Check: what was the context? What tool calls were made? Were responses unexpected? Compare: successful vs failed traces for same task type. Look for: non-determinism, timing issues, API changes.

### Advanced
7. **Design an observability system for a multi-agent platform handling 10K requests/day.** Distributed tracing (OpenTelemetry compatible). Time-series metrics (Prometheus). Structured logs (shipped to ELK/Datadog). Custom dashboards: success rate, cost, latency by agent type. Alerting: PagerDuty for critical failures. Sampling: trace 100% of errors, 10% of successes. Retention: 7 days full traces, 90 days metrics.
8. **How do you detect agent degradation before users notice?** Canary metrics: compare current hour vs same hour last week. Quality scoring on random samples (LLM-as-judge). Latency trending (gradual increase = degradation). Token usage trending (increasing = prompts getting longer). A/B monitoring: new version vs baseline. Synthetic tests: run known tasks on schedule.
9. **How do you build a replay system for debugging production agents?** Store: full trace (all messages, tool calls, results) per execution. Replay mode: feed stored inputs to agent, compare outputs with stored outputs. Divergence detection: where did replay differ from original? Partial replay: start from step N with stored state. Privacy: redact PII before storing. Retention: keep failed traces longer.

---

## Hands-On Exercise
1. Implement Trace and Span classes for agent execution tracking
2. Add structured logging (JSON) with trace correlation
3. Build CostTracker that monitors token usage and costs per call
4. Implement ErrorRecovery with classification and retry/fallback logic
5. Create TraceReplay for debugging from saved traces
6. Build a simple dashboard that aggregates metrics across traces
7. Add budget limits that stop agent execution when exceeded
