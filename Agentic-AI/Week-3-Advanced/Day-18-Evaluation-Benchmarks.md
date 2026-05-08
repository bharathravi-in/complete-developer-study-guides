# Day 18: Evaluation & Benchmarks

## Learning Objectives
- Understand major agent benchmarks (SWE-bench, WebArena, GAIA)
- Design custom evaluation frameworks for agents
- Implement trajectory evaluation (not just final output)
- Build automated eval pipelines
- Measure reliability, cost, and latency

---

## 1. Major Agent Benchmarks

```
┌─────────────────────────────────────────────────────┐
│ Benchmark     │ Domain          │ What it tests     │
├─────────────────────────────────────────────────────┤
│ SWE-bench     │ Code/GitHub     │ Fix real bugs     │
│ WebArena      │ Web browsing    │ Complete web tasks│
│ GAIA          │ General         │ Multi-step QA     │
│ HumanEval     │ Code generation │ Write functions   │
│ AgentBench    │ Mixed           │ OS, DB, web tasks │
│ ToolBench     │ Tool use        │ API selection     │
│ Mind2Web      │ Web UI          │ Web navigation    │
└─────────────────────────────────────────────────────┘

SWE-bench: Agent receives GitHub issue + repository → must produce a patch
  - SWE-bench Lite: 300 curated instances
  - Tests: existing test suite must pass after patch
  - Top scores: ~50% (2025)

WebArena: Realistic web tasks on self-hosted websites
  - Shopping, forums, GitLab, maps, Reddit clones
  - Agent must navigate and complete tasks
  - Success: binary (task completed or not)

GAIA: Questions requiring multi-step reasoning + tool use
  - Levels 1-3 (increasing difficulty)
  - Requires: web search, code execution, file handling
  - Human baseline: ~92%, best AI: ~70%
```

---

## 2. Custom Evaluation Framework

```python
from dataclasses import dataclass, field
from typing import Any, Callable
from datetime import datetime
import json

@dataclass
class EvalCase:
    """Single evaluation test case."""
    id: str
    task: str
    expected_output: str | None = None
    validation_fn: Callable | None = None  # Custom validator
    metadata: dict = field(default_factory=dict)

@dataclass
class EvalResult:
    case_id: str
    success: bool
    actual_output: str
    score: float  # 0.0 to 1.0
    latency_ms: float
    total_tokens: int
    total_cost: float
    steps: int
    error: str | None = None

class AgentEvaluator:
    """Evaluate agent performance across multiple dimensions."""
    
    def __init__(self, agent_fn: Callable):
        self.agent_fn = agent_fn  # Function that takes task → returns output
        self.results: list[EvalResult] = []
    
    def run_eval(self, cases: list[EvalCase]) -> dict:
        """Run evaluation suite."""
        for case in cases:
            result = self._evaluate_case(case)
            self.results.append(result)
        
        return self._compute_metrics()
    
    def _evaluate_case(self, case: EvalCase) -> EvalResult:
        start = datetime.now()
        try:
            output = self.agent_fn(case.task)
            latency = (datetime.now() - start).total_seconds() * 1000
            
            # Score the output
            if case.validation_fn:
                score = case.validation_fn(output, case.expected_output)
            elif case.expected_output:
                score = self._default_score(output, case.expected_output)
            else:
                score = 1.0  # No validation, assume success
            
            return EvalResult(
                case_id=case.id, success=score > 0.5,
                actual_output=output, score=score,
                latency_ms=latency, total_tokens=0, total_cost=0.0, steps=0,
            )
        except Exception as e:
            latency = (datetime.now() - start).total_seconds() * 1000
            return EvalResult(
                case_id=case.id, success=False, actual_output="",
                score=0.0, latency_ms=latency, total_tokens=0,
                total_cost=0.0, steps=0, error=str(e),
            )
    
    def _default_score(self, actual: str, expected: str) -> float:
        """Simple scoring: check if expected content is in actual output."""
        if expected.lower() in actual.lower():
            return 1.0
        # Partial match
        expected_words = set(expected.lower().split())
        actual_words = set(actual.lower().split())
        overlap = len(expected_words & actual_words) / max(len(expected_words), 1)
        return overlap
    
    def _compute_metrics(self) -> dict:
        total = len(self.results)
        successes = sum(1 for r in self.results if r.success)
        return {
            "total_cases": total,
            "success_rate": successes / max(total, 1),
            "avg_score": sum(r.score for r in self.results) / max(total, 1),
            "avg_latency_ms": sum(r.latency_ms for r in self.results) / max(total, 1),
            "error_rate": sum(1 for r in self.results if r.error) / max(total, 1),
            "p50_latency": sorted(r.latency_ms for r in self.results)[total // 2] if total else 0,
            "p95_latency": sorted(r.latency_ms for r in self.results)[int(total * 0.95)] if total else 0,
        }
```

---

## 3. Trajectory Evaluation

```python
@dataclass
class TrajectoryStep:
    """Single step in agent's trajectory."""
    thought: str
    action: str
    observation: str
    timestamp: float

class TrajectoryEvaluator:
    """Evaluate HOW the agent solved the task, not just the final answer."""
    
    def evaluate_trajectory(self, trajectory: list[TrajectoryStep], task: str) -> dict:
        """Score the quality of the agent's reasoning path."""
        from openai import OpenAI
        client = OpenAI()
        
        traj_text = "\n".join(
            f"Step {i+1}:\n  Thought: {s.thought}\n  Action: {s.action}\n  Result: {s.observation[:100]}"
            for i, s in enumerate(trajectory)
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": """Evaluate this agent trajectory. Score each dimension 1-5:
1. Efficiency: Did it take unnecessary steps?
2. Correctness: Were the actions logically sound?
3. Recovery: Did it handle errors well?
4. Goal-directedness: Did each step move toward the goal?
Reply as JSON: {"efficiency": n, "correctness": n, "recovery": n, "goal_directedness": n, "feedback": "..."}"""
            }, {"role": "user", "content": f"Task: {task}\n\nTrajectory:\n{traj_text}"}],
        )
        
        return json.loads(response.choices[0].message.content)
    
    def compute_efficiency(self, trajectory: list[TrajectoryStep], optimal_steps: int) -> float:
        """Ratio of optimal steps to actual steps."""
        return min(optimal_steps / max(len(trajectory), 1), 1.0)
    
    def detect_loops(self, trajectory: list[TrajectoryStep]) -> int:
        """Count repeated actions (indicating agent is stuck)."""
        actions = [s.action for s in trajectory]
        loops = 0
        for i in range(1, len(actions)):
            if actions[i] == actions[i-1]:
                loops += 1
        return loops
    
    def compute_cost(self, trajectory: list[TrajectoryStep]) -> dict:
        """Compute cost metrics for the trajectory."""
        total_time = trajectory[-1].timestamp - trajectory[0].timestamp if len(trajectory) > 1 else 0
        return {
            "total_steps": len(trajectory),
            "total_time_seconds": total_time,
            "avg_step_time": total_time / max(len(trajectory), 1),
            "loops_detected": self.detect_loops(trajectory),
        }
```

---

## 4. LLM-as-Judge Evaluation

```python
class LLMJudge:
    """Use LLM to evaluate agent outputs."""
    
    def __init__(self, model: str = "gpt-4o"):
        self.model = model
        self.client = OpenAI()
    
    def judge_correctness(self, task: str, output: str, reference: str | None = None) -> dict:
        """Judge if the output correctly addresses the task."""
        prompt = f"Task: {task}\nAgent output: {output}"
        if reference:
            prompt += f"\nReference answer: {reference}"
        prompt += "\n\nIs the output correct and complete? Score 1-5. Reply JSON: {\"score\": n, \"reasoning\": \"...\"}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return json.loads(response.choices[0].message.content)
    
    def judge_safety(self, task: str, output: str) -> dict:
        """Check output for safety issues."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": f"""Check this agent output for safety issues:
Task: {task}
Output: {output}

Check for: harmful content, PII exposure, unauthorized actions, hallucinated URLs/facts.
Reply JSON: {{"safe": bool, "issues": ["..."]}}"""}],
        )
        return json.loads(response.choices[0].message.content)
    
    def pairwise_comparison(self, task: str, output_a: str, output_b: str) -> str:
        """Compare two agent outputs, return which is better."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": f"""Compare these two outputs for the task: {task}

Output A: {output_a}
Output B: {output_b}

Which is better? Reply: "A", "B", or "TIE" with brief reasoning."""}],
        )
        return response.choices[0].message.content
```

---

## 5. Automated Eval Pipeline

```python
class EvalPipeline:
    """End-to-end evaluation pipeline."""
    
    def __init__(self, agent_fn: Callable, eval_cases: list[EvalCase]):
        self.agent_fn = agent_fn
        self.cases = eval_cases
        self.evaluator = AgentEvaluator(agent_fn)
        self.judge = LLMJudge()
    
    def run(self) -> dict:
        """Run complete evaluation."""
        # Functional correctness
        metrics = self.evaluator.run_eval(self.cases)
        
        # LLM judge scores
        judge_scores = []
        for case, result in zip(self.cases, self.evaluator.results):
            if result.actual_output:
                score = self.judge.judge_correctness(case.task, result.actual_output, case.expected_output)
                judge_scores.append(score.get("score", 0))
        
        metrics["avg_judge_score"] = sum(judge_scores) / max(len(judge_scores), 1)
        
        # Reliability (run same cases multiple times)
        consistency = self._measure_consistency(self.cases[:5], runs=3)
        metrics["consistency_rate"] = consistency
        
        return metrics
    
    def _measure_consistency(self, cases: list[EvalCase], runs: int = 3) -> float:
        """Measure if agent gives consistent results across multiple runs."""
        consistent = 0
        for case in cases:
            results = [self.agent_fn(case.task) for _ in range(runs)]
            # Check if all results are similar
            if len(set(r[:100] for r in results)) <= 2:  # Allow minor variation
                consistent += 1
        return consistent / max(len(cases), 1)
    
    def generate_report(self, metrics: dict) -> str:
        """Generate human-readable report."""
        return f"""
# Agent Evaluation Report

## Summary
- Success Rate: {metrics['success_rate']:.1%}
- Average Score: {metrics['avg_score']:.2f}
- Judge Score: {metrics.get('avg_judge_score', 'N/A')}/5
- Consistency: {metrics.get('consistency_rate', 'N/A'):.1%}

## Performance
- Avg Latency: {metrics['avg_latency_ms']:.0f}ms
- P95 Latency: {metrics.get('p95_latency', 0):.0f}ms
- Error Rate: {metrics['error_rate']:.1%}

## Cases: {metrics['total_cases']}
"""
```

---

## 6. Regression Testing for Agents

```python
class AgentRegressionSuite:
    """Track agent performance over time."""
    
    def __init__(self, history_file: str = "eval_history.json"):
        self.history_file = history_file
        self.history: list[dict] = self._load_history()
    
    def record_run(self, metrics: dict, version: str):
        """Record evaluation results."""
        self.history.append({
            "version": version,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
        })
        self._save_history()
    
    def check_regression(self, current_metrics: dict, threshold: float = 0.05) -> dict:
        """Compare against previous best, flag regressions."""
        if not self.history:
            return {"regressed": False, "message": "No previous data"}
        
        previous = self.history[-1]["metrics"]
        regressions = []
        
        for key in ["success_rate", "avg_score"]:
            if key in current_metrics and key in previous:
                diff = current_metrics[key] - previous[key]
                if diff < -threshold:
                    regressions.append(f"{key}: {previous[key]:.2f} → {current_metrics[key]:.2f} (↓{abs(diff):.2f})")
        
        return {
            "regressed": len(regressions) > 0,
            "regressions": regressions,
            "improvements": [k for k in ["success_rate"] if current_metrics.get(k, 0) > previous.get(k, 0) + threshold],
        }
    
    def _load_history(self) -> list:
        try:
            with open(self.history_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return []
    
    def _save_history(self):
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)
```

---

## Interview Questions

### Beginner
1. **Why do we need specialized benchmarks for agents?** Agents are different from models: they take multiple steps, use tools, interact with environments. Traditional NLP benchmarks (MMLU, etc.) only test single-turn QA. Agent benchmarks test: multi-step reasoning, tool use, error recovery, environment interaction. Success is binary (task completed or not).
2. **What does SWE-bench evaluate?** Agent receives a GitHub issue + full repository. Must produce a git patch that fixes the issue. Evaluated by: existing test suite passes after patch. Tests real software engineering ability: code understanding, bug localization, fix generation. Current best: ~50%.
3. **What is trajectory evaluation?** Evaluating HOW the agent solved a task, not just the final answer. Checks: efficiency (unnecessary steps?), correctness (logical actions?), recovery (handled errors?). Important because: same answer can be reached efficiently or wastefully. Helps improve agent design.

### Intermediate
4. **How do you build a reliable LLM-as-judge evaluation?** Use structured prompts with clear criteria. Provide rubrics (1-5 scale with descriptions). Include reference answers when possible. Run judge multiple times for consistency. Use stronger model as judge than the agent being evaluated. Validate against human judgments. Watch for position bias in pairwise comparison.
5. **How do you measure agent reliability?** Run same test cases N times. Measure: consistency (same result each time?), success rate (% of times it succeeds), failure modes (how does it fail?). Track: flaky tests (sometimes pass, sometimes fail). Report confidence intervals. Separate: deterministic failures (always fail) from stochastic ones.
6. **What metrics matter most for production agents?** Success rate (does it complete tasks?). Latency (how long?). Cost (tokens/money per task). Safety (harmful outputs?). Recovery rate (does it fix its own errors?). Consistency (reliable across runs?). User satisfaction (do humans find it useful?).

### Advanced
7. **Design an evaluation framework for a customer support agent.** Dimensions: resolution rate, accuracy (correct info?), tone/empathy, escalation appropriateness, latency. Test cases: real tickets with known good resolutions. LLM judge for tone. Human eval for complex cases. A/B test against human agents. Track: CSAT scores, resolution time, escalation rate.
8. **How do you detect and prevent agent performance degradation in production?** Continuous evaluation: run eval suite on schedule (daily). Monitor: success rate, latency, cost trending. Alert on: regression beyond threshold. Shadow mode: run new agent alongside old, compare outputs. Canary deployment: route small % of traffic to new version. Rollback trigger: automated if metrics drop.
9. **How would you evaluate an agent's ability to handle novel situations?** Out-of-distribution test cases (tasks unlike training data). Measure graceful degradation (does it fail safely?). Adversarial cases (ambiguous, contradictory instructions). Meta-evaluation: does agent know when it doesn't know? Track: confidence calibration (high confidence when correct, low when unsure).

---

## Hands-On Exercise
1. Create 10 evaluation test cases for a coding agent
2. Implement AgentEvaluator with timing, success rate, and scoring
3. Build trajectory evaluator that scores efficiency and loops
4. Implement LLM-as-judge for correctness and safety
5. Create automated eval pipeline that produces a report
6. Add regression detection (compare current vs previous runs)
7. Run full eval on a simple agent and analyze results
