# Day 25: Reliability Engineering

## Learning Objectives
- Implement retry strategies with exponential backoff
- Build fallback chains for LLM calls
- Design timeout and circuit breaker patterns
- Ensure idempotency in agent operations
- Implement checkpointing for long-running agents
- Apply chaos testing to agent systems

---

## 1. Retry Strategies

```python
import time
import random
from typing import Callable, Any
from functools import wraps

class RetryConfig:
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_exceptions: tuple = (TimeoutError, ConnectionError)

def retry_with_backoff(config: RetryConfig = None):
    """Decorator for retry with exponential backoff."""
    config = config or RetryConfig()
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except config.retryable_exceptions as e:
                    last_exception = e
                    if attempt == config.max_retries:
                        raise
                    
                    delay = min(
                        config.base_delay * (config.exponential_base ** attempt),
                        config.max_delay,
                    )
                    if config.jitter:
                        delay *= (0.5 + random.random())
                    
                    time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator

# Usage
@retry_with_backoff(RetryConfig(max_retries=3, retryable_exceptions=(Exception,)))
def call_llm(messages: list) -> str:
    response = client.chat.completions.create(model="gpt-4o", messages=messages)
    return response.choices[0].message.content
```

---

## 2. Fallback Chains

```python
class FallbackChain:
    """Try multiple providers/models in sequence."""
    
    def __init__(self, providers: list[dict]):
        """providers: [{"name": "openai", "model": "gpt-4o", "call_fn": fn}, ...]"""
        self.providers = providers
    
    def call(self, messages: list, **kwargs) -> dict:
        """Try each provider until one succeeds."""
        errors = []
        for provider in self.providers:
            try:
                result = provider["call_fn"](messages, model=provider["model"], **kwargs)
                return {"result": result, "provider": provider["name"], "fallbacks_used": len(errors)}
            except Exception as e:
                errors.append({"provider": provider["name"], "error": str(e)})
                continue
        
        raise RuntimeError(f"All providers failed: {errors}")

# Setup
from openai import OpenAI
import anthropic

openai_client = OpenAI()
anthropic_client = anthropic.Anthropic()

def call_openai(messages, model="gpt-4o", **kwargs):
    resp = openai_client.chat.completions.create(model=model, messages=messages)
    return resp.choices[0].message.content

def call_anthropic(messages, model="claude-3-5-sonnet-20241022", **kwargs):
    # Convert message format
    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    user_msgs = [m for m in messages if m["role"] != "system"]
    resp = anthropic_client.messages.create(model=model, max_tokens=4096, system=system, messages=user_msgs)
    return resp.content[0].text

chain = FallbackChain([
    {"name": "openai-4o", "model": "gpt-4o", "call_fn": call_openai},
    {"name": "anthropic", "model": "claude-3-5-sonnet-20241022", "call_fn": call_anthropic},
    {"name": "openai-mini", "model": "gpt-4o-mini", "call_fn": call_openai},
])
```

---

## 3. Timeout & Circuit Breaker

```python
import threading
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking all calls
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """Prevent cascading failures by stopping calls to failing services."""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time: datetime | None = None
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitState.OPEN:
            if self._should_try_recovery():
                self.state = CircuitState.HALF_OPEN
            else:
                raise RuntimeError("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        self.failures = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now()
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
    
    def _should_try_recovery(self) -> bool:
        if not self.last_failure_time:
            return True
        return datetime.now() > self.last_failure_time + timedelta(seconds=self.recovery_timeout)

# Timeout wrapper
def with_timeout(seconds: float):
    """Decorator to add timeout to any function."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.start()
            thread.join(timeout=seconds)
            
            if thread.is_alive():
                raise TimeoutError(f"Function timed out after {seconds}s")
            if exception[0]:
                raise exception[0]
            return result[0]
        return wrapper
    return decorator
```

---

## 4. Idempotency

```python
import hashlib
import json

class IdempotencyStore:
    """Ensure operations are only executed once."""
    
    def __init__(self):
        self.results: dict[str, Any] = {}  # Use Redis in production
    
    def get_key(self, operation: str, params: dict) -> str:
        """Generate idempotency key from operation + params."""
        content = json.dumps({"op": operation, "params": params}, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def execute_once(self, key: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function only if not already executed for this key."""
        if key in self.results:
            return self.results[key]  # Return cached result
        
        result = func(*args, **kwargs)
        self.results[key] = result
        return result

class IdempotentAgent:
    """Agent with idempotent tool execution."""
    
    def __init__(self):
        self.store = IdempotencyStore()
    
    def execute_tool(self, tool_name: str, args: dict) -> str:
        """Execute tool idempotently (same args → same result, no side effects)."""
        key = self.store.get_key(tool_name, args)
        return self.store.execute_once(key, self._do_execute, tool_name, args)
    
    def _do_execute(self, tool_name: str, args: dict) -> str:
        # Actual execution
        return f"Executed {tool_name}"
```

---

## 5. Checkpointing

```python
import pickle
from pathlib import Path

class Checkpoint:
    """Save and restore agent state for long-running tasks."""
    
    def __init__(self, checkpoint_dir: str = "/tmp/agent_checkpoints"):
        self.dir = Path(checkpoint_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, agent_id: str, step: int, state: dict):
        """Save agent state at a given step."""
        path = self.dir / f"{agent_id}_step_{step}.json"
        with open(path, "w") as f:
            json.dump(state, f)
    
    def load_latest(self, agent_id: str) -> tuple[int, dict] | None:
        """Load the latest checkpoint for an agent."""
        checkpoints = sorted(self.dir.glob(f"{agent_id}_step_*.json"))
        if not checkpoints:
            return None
        
        latest = checkpoints[-1]
        step = int(latest.stem.split("_step_")[1])
        with open(latest) as f:
            state = json.load(f)
        return step, state
    
    def cleanup(self, agent_id: str, keep_last: int = 3):
        """Remove old checkpoints, keep last N."""
        checkpoints = sorted(self.dir.glob(f"{agent_id}_step_*.json"))
        for cp in checkpoints[:-keep_last]:
            cp.unlink()

class CheckpointedAgent:
    """Agent that checkpoints state and can resume."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.checkpoint = Checkpoint()
        self.state = {"messages": [], "step": 0, "results": []}
    
    def run(self, task: str, max_steps: int = 20) -> str:
        # Try to resume from checkpoint
        saved = self.checkpoint.load_latest(self.agent_id)
        if saved:
            self.state = saved[1]
            print(f"Resumed from step {saved[0]}")
        else:
            self.state["messages"] = [{"role": "user", "content": task}]
        
        for step in range(self.state["step"], max_steps):
            self.state["step"] = step
            
            # Checkpoint every 3 steps
            if step % 3 == 0:
                self.checkpoint.save(self.agent_id, step, self.state)
            
            # Execute step
            result = self._execute_step()
            self.state["results"].append(result)
            
            if self._is_done(result):
                self.checkpoint.cleanup(self.agent_id)
                return result
        
        return self.state["results"][-1] if self.state["results"] else ""
    
    def _execute_step(self) -> str:
        # Agent step logic
        return "step result"
    
    def _is_done(self, result: str) -> bool:
        return "DONE" in result
```

---

## 6. Chaos Testing

```python
class ChaosMonkey:
    """Inject failures to test agent resilience."""
    
    def __init__(self, failure_rate: float = 0.1):
        self.failure_rate = failure_rate
        self.injected_failures: list[dict] = []
    
    def maybe_fail(self, operation: str):
        """Randomly inject failure."""
        if random.random() < self.failure_rate:
            failure_type = random.choice(["timeout", "error", "slow", "corrupt"])
            self.injected_failures.append({"operation": operation, "type": failure_type})
            
            if failure_type == "timeout":
                time.sleep(35)  # Exceed typical timeout
                raise TimeoutError(f"Chaos: {operation} timed out")
            elif failure_type == "error":
                raise RuntimeError(f"Chaos: {operation} failed")
            elif failure_type == "slow":
                time.sleep(random.uniform(5, 15))
            elif failure_type == "corrupt":
                return "CORRUPTED_RESPONSE_" + "x" * 1000
    
    def wrap_tool(self, tool_fn: Callable) -> Callable:
        """Wrap a tool function with chaos injection."""
        @wraps(tool_fn)
        def wrapper(*args, **kwargs):
            self.maybe_fail(tool_fn.__name__)
            return tool_fn(*args, **kwargs)
        return wrapper

# Usage: Test agent resilience
# chaos = ChaosMonkey(failure_rate=0.2)
# agent.tools["search"] = chaos.wrap_tool(agent.tools["search"])
# Run agent and verify it still completes (maybe slower, with retries)
```

---

## Interview Questions

### Beginner
1. **Why do agents need retry logic?** LLM APIs: rate limits, transient errors, timeouts. Without retry: agent fails on first hiccup. Exponential backoff prevents thundering herd. Jitter prevents synchronized retries from multiple agents. Always limit max retries to prevent infinite loops.
2. **What is a circuit breaker?** Pattern that prevents repeatedly calling a failing service. States: CLOSED (normal), OPEN (blocking calls), HALF_OPEN (testing recovery). After N failures → circuit opens → stops calls → waits → tries one call → if success, closes. Prevents cascading failures.
3. **Why is idempotency important for agents?** Agents may retry steps (error recovery, checkpointing). Without idempotency: same email sent twice, same record created twice. Idempotent operations: same input → same result regardless of how many times called. Critical for: side effects (emails, payments, writes).

### Intermediate
4. **Design a fallback strategy for a production agent.** Primary: GPT-4o (best quality). Fallback 1: Claude (different provider). Fallback 2: GPT-4o-mini (cheaper, less capable). Triggers: timeout, rate limit, 5xx error. Don't fallback on: 4xx (bad request), content filter. Track: which fallback used, frequency. Alert if primary fails >5%.
5. **How do you implement checkpointing for a 50-step agent?** Save state every N steps (e.g., every 5). State includes: messages, tool results, intermediate outputs. Store in Redis/DB (not just filesystem). Resume: load latest checkpoint, skip completed steps. Cleanup: remove old checkpoints after completion. Handle: partial step (tool called but result not saved).
6. **What chaos testing scenarios are most important for agents?** LLM timeout (common). Rate limit bursts. Tool returning errors. Tool returning garbage data. Slow responses (10x normal latency). Connection drops mid-response. Out-of-memory (long context). Concurrent execution conflicts.

### Advanced
7. **Design a reliability system for an agent handling financial transactions.** Exactly-once semantics: idempotency keys for all mutations. Saga pattern: compensating actions on failure. Circuit breaker per external service. Dead letter queue for unprocessable tasks. Manual review for high-value transactions. Audit log of all operations. Timeout + automatic reversal.
8. **How do you balance reliability with latency?** Retries add latency. Solutions: parallel retries (send to backup simultaneously, take first response). Speculative execution. Timeout budget: allocate time across steps. Fast fail: detect unfixable errors early. Cache: avoid retrying same computation. Adaptive: reduce retries when latency budget is low.
9. **How do you test that an agent system is resilient without affecting production?** Shadow mode: run chaos tests alongside real traffic (discard chaos results). Staging environment with production-like load. Synthetic tests: inject failures in test suite. Game days: scheduled chaos in production with team prepared. Gradual: start with 1% failure injection, increase. Monitor: recovery time, error propagation.

---

## Hands-On Exercise
1. Implement retry with exponential backoff and jitter
2. Build a fallback chain (OpenAI → Anthropic → local model)
3. Implement circuit breaker for tool calls
4. Add idempotency to tool execution (same args = cached result)
5. Build checkpointing system (save/resume agent state)
6. Create ChaosMonkey that randomly fails tool calls
7. Test: run agent with 20% failure rate, verify it still completes
