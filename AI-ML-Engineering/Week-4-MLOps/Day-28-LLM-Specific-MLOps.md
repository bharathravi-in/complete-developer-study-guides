# Day 28: LLM-Specific MLOps

## Learning Objectives
- Evaluate LLMs (perplexity, human eval, LLM-as-judge)
- Version and manage prompts in production
- Monitor LLM systems (token usage, latency, quality)
- Implement guardrails and safety layers
- Optimize LLM costs (caching, routing, model selection)
- Use tools: LangSmith, Helicone, Portkey

---

## 1. LLM Evaluation

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

# --- LLM-as-Judge (automated evaluation) ---
def llm_judge(question: str, answer: str, reference: str = None) -> dict:
    """Use a strong LLM to evaluate another LLM's output."""
    
    judge_prompt = f"""Rate the following answer on a scale of 1-5 for each criterion.

Question: {question}
Answer: {answer}
{f"Reference answer: {reference}" if reference else ""}

Rate (1-5) for:
1. Correctness: Is the answer factually accurate?
2. Relevance: Does it address the question?
3. Completeness: Does it cover all important aspects?
4. Clarity: Is it well-written and easy to understand?

Return JSON: {{"correctness": N, "relevance": N, "completeness": N, "clarity": N, "explanation": "..."}}"""
    
    response = client.chat.completions.create(
        model="gpt-4o",  # Use strongest model as judge
        messages=[{"role": "user", "content": judge_prompt}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    
    import json
    return json.loads(response.choices[0].message.content)

# --- Pairwise Comparison (which output is better?) ---
def pairwise_eval(question: str, answer_a: str, answer_b: str) -> str:
    """Compare two answers, return which is better."""
    prompt = f"""Compare these two answers to the question. Which is better?

Question: {question}
Answer A: {answer_a}
Answer B: {answer_b}

Respond with ONLY "A" or "B" or "TIE" and a one-sentence explanation."""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content

# --- Evaluation Suite ---
class LLMEvaluator:
    def __init__(self, test_cases: list[dict]):
        self.test_cases = test_cases  # [{"question": ..., "reference": ...}]
    
    def evaluate_model(self, model_name: str) -> dict:
        scores = []
        for case in self.test_cases:
            # Get model's answer
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": case["question"]}],
            )
            answer = response.choices[0].message.content
            
            # Judge it
            judgment = llm_judge(case["question"], answer, case.get("reference"))
            scores.append(judgment)
        
        # Aggregate scores
        return {
            "correctness": np.mean([s["correctness"] for s in scores]),
            "relevance": np.mean([s["relevance"] for s in scores]),
            "completeness": np.mean([s["completeness"] for s in scores]),
            "clarity": np.mean([s["clarity"] for s in scores]),
        }
```

---

## 2. Prompt Versioning & Management

```python
# Prompts are code — they need versioning, testing, and deployment

import json
from datetime import datetime
from pathlib import Path

class PromptRegistry:
    """Version control for prompts with A/B testing support."""
    
    def __init__(self, registry_path: str = "prompts/"):
        self.path = Path(registry_path)
        self.path.mkdir(exist_ok=True)
    
    def register(self, name: str, template: str, version: str, metadata: dict = None):
        """Register a new prompt version."""
        prompt_data = {
            "name": name,
            "version": version,
            "template": template,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
        }
        
        prompt_file = self.path / f"{name}_v{version}.json"
        prompt_file.write_text(json.dumps(prompt_data, indent=2))
    
    def get(self, name: str, version: str = "latest") -> str:
        """Get a prompt template by name and version."""
        if version == "latest":
            versions = sorted(self.path.glob(f"{name}_v*.json"))
            if not versions:
                raise ValueError(f"No prompt found: {name}")
            prompt_file = versions[-1]
        else:
            prompt_file = self.path / f"{name}_v{version}.json"
        
        data = json.loads(prompt_file.read_text())
        return data["template"]
    
    def render(self, name: str, version: str = "latest", **kwargs) -> str:
        """Get prompt and fill in variables."""
        template = self.get(name, version)
        return template.format(**kwargs)

# Usage:
registry = PromptRegistry()
registry.register(
    name="summarize",
    version="2.1",
    template="Summarize the following text in {max_sentences} sentences:\n\n{text}",
    metadata={"model": "gpt-4o-mini", "temperature": 0, "eval_score": 4.2},
)

prompt = registry.render("summarize", version="2.1", max_sentences=3, text="...")

# Prompt testing:
def test_prompt_version(prompt_name, old_version, new_version, test_cases):
    """Compare two prompt versions on test cases."""
    old_scores, new_scores = [], []
    for case in test_cases:
        old_prompt = registry.render(prompt_name, old_version, **case["inputs"])
        new_prompt = registry.render(prompt_name, new_version, **case["inputs"])
        
        old_result = get_llm_response(old_prompt)
        new_result = get_llm_response(new_prompt)
        
        old_scores.append(llm_judge(case["question"], old_result)["correctness"])
        new_scores.append(llm_judge(case["question"], new_result)["correctness"])
    
    return {"old_avg": np.mean(old_scores), "new_avg": np.mean(new_scores)}
```

---

## 3. LLM Monitoring

```python
import time
from dataclasses import dataclass, field

@dataclass
class LLMCallMetrics:
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: float
    cost_usd: float
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error: str = None

class LLMMonitor:
    """Track LLM usage, cost, latency, and quality."""
    
    # Cost per 1M tokens (approximate)
    PRICING = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    }
    
    def __init__(self):
        self.metrics: list[LLMCallMetrics] = []
    
    def track_call(self, model: str, response) -> LLMCallMetrics:
        """Track an OpenAI API call."""
        usage = response.usage
        pricing = self.PRICING.get(model, {"input": 0, "output": 0})
        
        cost = (
            usage.prompt_tokens * pricing["input"] / 1_000_000 +
            usage.completion_tokens * pricing["output"] / 1_000_000
        )
        
        metric = LLMCallMetrics(
            model=model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            latency_ms=0,  # Set externally
            cost_usd=cost,
        )
        self.metrics.append(metric)
        return metric
    
    def summary(self, hours: int = 24) -> dict:
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [m for m in self.metrics if m.timestamp > cutoff]
        
        if not recent:
            return {"calls": 0}
        
        return {
            "calls": len(recent),
            "total_cost_usd": sum(m.cost_usd for m in recent),
            "avg_latency_ms": np.mean([m.latency_ms for m in recent]),
            "p95_latency_ms": np.percentile([m.latency_ms for m in recent], 95),
            "total_tokens": sum(m.prompt_tokens + m.completion_tokens for m in recent),
            "error_rate": sum(1 for m in recent if not m.success) / len(recent),
        }

# Wrapper for automatic monitoring
def monitored_completion(model: str, messages: list, monitor: LLMMonitor, **kwargs):
    start = time.time()
    try:
        response = client.chat.completions.create(model=model, messages=messages, **kwargs)
        metric = monitor.track_call(model, response)
        metric.latency_ms = (time.time() - start) * 1000
        return response
    except Exception as e:
        monitor.metrics.append(LLMCallMetrics(
            model=model, prompt_tokens=0, completion_tokens=0,
            latency_ms=(time.time() - start) * 1000, cost_usd=0,
            success=False, error=str(e),
        ))
        raise
```

---

## 4. Guardrails & Safety

```python
# Prevent harmful, off-topic, or incorrect outputs

class LLMGuardrails:
    def __init__(self):
        self.blocked_topics = ["violence", "illegal activities", "personal data"]
        self.max_output_tokens = 2000
    
    def check_input(self, user_message: str) -> tuple[bool, str]:
        """Pre-generation safety check."""
        # Length check
        if len(user_message) > 10000:
            return False, "Input too long"
        
        # Prompt injection detection (basic)
        injection_patterns = [
            "ignore previous instructions",
            "you are now",
            "system prompt:",
            "forget everything",
        ]
        lower_msg = user_message.lower()
        for pattern in injection_patterns:
            if pattern in lower_msg:
                return False, f"Potential prompt injection detected"
        
        return True, "OK"
    
    def check_output(self, output: str) -> tuple[bool, str]:
        """Post-generation safety check."""
        # PII detection (basic)
        import re
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', output):  # SSN pattern
            return False, "Output contains potential PII (SSN)"
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', output):
            return False, "Output contains email address"
        
        # Hallucination indicator (low confidence language)
        hallucination_markers = ["I think", "probably", "I'm not sure but"]
        confidence_issues = sum(1 for m in hallucination_markers if m.lower() in output.lower())
        if confidence_issues >= 2:
            return True, "WARNING: Low confidence language detected"
        
        return True, "OK"
    
    def safe_generate(self, messages: list, model: str = "gpt-4o-mini") -> dict:
        """Generate with input/output guardrails."""
        # Pre-check
        user_msg = messages[-1]["content"]
        safe, reason = self.check_input(user_msg)
        if not safe:
            return {"blocked": True, "reason": reason, "output": None}
        
        # Generate
        response = client.chat.completions.create(model=model, messages=messages)
        output = response.choices[0].message.content
        
        # Post-check
        safe, reason = self.check_output(output)
        if not safe:
            return {"blocked": True, "reason": reason, "output": None}
        
        return {"blocked": False, "output": output, "warning": reason if reason != "OK" else None}
```

---

## 5. Cost Optimization

```python
# LLM costs add up fast — optimize aggressively

# 1. Semantic Caching (same/similar questions → cached answer)
from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticCache:
    def __init__(self, similarity_threshold: float = 0.95):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.cache: list[tuple[np.ndarray, str, str]] = []  # (embedding, query, response)
        self.threshold = similarity_threshold
    
    def get(self, query: str) -> str | None:
        query_emb = self.embedder.encode(query)
        for cached_emb, cached_query, cached_response in self.cache:
            sim = np.dot(query_emb, cached_emb) / (
                np.linalg.norm(query_emb) * np.linalg.norm(cached_emb)
            )
            if sim > self.threshold:
                return cached_response
        return None
    
    def set(self, query: str, response: str):
        emb = self.embedder.encode(query)
        self.cache.append((emb, query, response))

# 2. Model Routing (use cheapest model that can handle the task)
class ModelRouter:
    def __init__(self):
        self.models = {
            "simple": "gpt-4o-mini",      # $0.15/1M input
            "complex": "gpt-4o",           # $2.50/1M input
        }
    
    def classify_complexity(self, query: str) -> str:
        """Route to appropriate model based on query complexity."""
        # Simple heuristics (or use a small classifier)
        if len(query) < 100 and "?" in query:
            return "simple"
        if any(word in query.lower() for word in ["analyze", "compare", "design", "explain in detail"]):
            return "complex"
        return "simple"
    
    def route(self, query: str) -> str:
        complexity = self.classify_complexity(query)
        return self.models[complexity]

# 3. Prompt compression (reduce input tokens)
def compress_context(context: str, max_tokens: int = 2000) -> str:
    """Compress long context to fit within budget."""
    # Simple: truncate
    # Better: summarize with cheap model
    if len(context.split()) < max_tokens:
        return context
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Summarize this in under {max_tokens} words, preserving key facts:\n\n{context}"}],
    )
    return response.choices[0].message.content
```

---

## 6. LangSmith / Helicone / Portkey

```python
# LangSmith: tracing, evaluation, and monitoring for LLM apps
# Helicone: LLM observability (proxy-based, minimal code change)
# Portkey: LLM gateway (routing, caching, fallbacks)

# --- LangSmith ---
# Set env vars: LANGCHAIN_API_KEY, LANGCHAIN_TRACING_V2=true
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "..."

from langsmith import Client
ls_client = Client()

# All LangChain calls automatically traced
# View traces: app.smith.langchain.com

# --- Helicone (proxy-based monitoring) ---
# Just change base URL — zero code changes
from openai import OpenAI

client = OpenAI(
    base_url="https://oai.helicone.ai/v1",
    default_headers={
        "Helicone-Auth": "Bearer sk-helicone-...",
        "Helicone-Cache-Enabled": "true",  # Auto-caching
    }
)
# All calls now monitored in Helicone dashboard
# Metrics: cost, latency, token usage, cache hit rate

# --- Portkey (LLM gateway) ---
from portkey_ai import Portkey

portkey = Portkey(
    api_key="...",
    config={
        "strategy": {"mode": "fallback"},  # Auto-fallback on failure
        "targets": [
            {"provider": "openai", "model": "gpt-4o"},
            {"provider": "anthropic", "model": "claude-3-5-sonnet"},
        ],
        "cache": {"mode": "semantic", "max_age": 3600},
    }
)
# Automatic: fallback, caching, load balancing, monitoring
```

---

## Interview Questions

### Beginner
1. **How do you evaluate LLM outputs?** LLM-as-judge (GPT-4 rates outputs 1-5 on criteria). Human evaluation (gold standard, expensive). Automated metrics: BLEU/ROUGE (for translation/summarization), exact match. Pairwise comparison (which of two outputs is better). Evaluation datasets with reference answers.
2. **Why version prompts?** Prompts are code — changes affect output quality. Need to: track which prompt version produced which results, rollback if quality drops, A/B test prompt variants, reproduce past behavior. Store in registry with metadata (model, temperature, eval scores).
3. **What LLM metrics should you monitor?** Token usage (cost tracking), latency (P50/P95/P99), error rate (API failures, timeouts), quality scores (from judges or user feedback), cache hit rate, cost per request. Alert on: latency spikes, cost anomalies, quality degradation.

### Intermediate
4. **How does LLM-as-judge work and what are its limitations?** Strong model (GPT-4) evaluates outputs on criteria (correctness, relevance, etc.). Limitations: position bias (prefers first option), verbosity bias (prefers longer answers), self-bias (prefers its own style), may not catch subtle errors in specialized domains. Mitigate: randomize order, use multiple judges, calibrate on human labels.
5. **How do you implement guardrails for production LLMs?** Input: prompt injection detection, topic filtering, length limits. Output: PII detection, factuality checking, toxicity filtering. Structural: output format validation (JSON schema). Operational: rate limiting, cost caps. Tools: NeMo Guardrails, Guardrails AI, custom classifiers.
6. **Explain semantic caching for LLMs.** Cache responses keyed by semantic similarity (not exact match). Embed queries, if new query similar to cached query (cosine > 0.95), return cached response. Benefits: reduce API calls 30-60%, lower latency. Tradeoffs: stale answers for dynamic topics, cache invalidation complexity.

### Advanced
7. **Design a cost-optimized LLM serving system for 1M requests/day.** Model routing: classify complexity → route 80% to cheap model (4o-mini), 20% to expensive (4o). Semantic cache: 40% hit rate = 400K saved calls. Prompt compression: reduce tokens 30%. Batch similar requests. Budget: set daily limits with alerts. Expected: 60-70% cost reduction vs naive approach.
8. **How do you A/B test prompts in production?** Traffic split: 90% control (current prompt), 10% variant. Metrics: task success rate, user satisfaction, latency, cost. Duration: 1-2 weeks for statistical significance. Guardrails: auto-rollback if variant quality drops. Analysis: per-segment (user type, query complexity). Use LangSmith or custom logging.
9. **Design an LLM observability stack.** Layers: 1) Tracing (LangSmith) — every chain/tool call traced. 2) Metrics (Helicone/Portkey) — cost, latency, token usage aggregated. 3) Quality (LLM-as-judge on sample) — nightly eval on 100 random outputs. 4) Alerts (PagerDuty) — error rate, cost spike, quality drop. 5) Dashboard (Grafana) — real-time overview. Log everything, sample for expensive analysis.

---

## Hands-On Exercise
1. Implement LLM-as-judge evaluation on 5 test cases (score 1-5)
2. Build a prompt registry with versioning and rendering
3. Create an LLM monitor tracking cost, latency, and token usage
4. Implement input/output guardrails (injection detection, PII filter)
5. Build a semantic cache and measure cache hit rate on 20 queries
6. Implement model routing (simple→mini, complex→4o) and compare costs
