# Day 16: Code Generation Agents

## Learning Objectives
- Build agents that plan, write, test, and fix code
- Implement safe sandboxed code execution
- Design TDD-driven code generation workflows
- Create debugging agents that analyze and fix errors
- Understand iterative code improvement patterns

---

## 1. Code Generation Pipeline

```
Plan → Write → Test → Fix (iterate)

┌─────────┐    ┌─────────┐    ┌──────────┐    ┌────────┐
│  Plan   │ →  │  Write  │ →  │   Test   │ →  │  Fix   │
│ (spec)  │    │ (code)  │    │ (execute)│    │ (debug)│
└─────────┘    └─────────┘    └──────────┘    └────┬───┘
                                                    │
                                    ↑───────────────┘
                                    (loop until tests pass)
```

---

## 2. Planning Agent

```python
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI()

class CodePlan(BaseModel):
    """Structured plan for code generation."""
    description: str
    functions: list[dict]  # {"name": ..., "purpose": ..., "inputs": ..., "outputs": ...}
    data_structures: list[dict]  # {"name": ..., "fields": ...}
    test_cases: list[dict]  # {"description": ..., "input": ..., "expected": ...}
    dependencies: list[str]  # Required packages

class PlanningAgent:
    """Creates detailed implementation plan before coding."""
    
    def plan(self, requirements: str) -> CodePlan:
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[{"role": "system", "content": """You are a software architect.
Create a detailed implementation plan. Include:
- Functions with inputs/outputs
- Data structures needed
- Test cases (happy path + edge cases)
- External dependencies"""
            }, {"role": "user", "content": requirements}],
            response_format=CodePlan,
        )
        return response.choices[0].message.parsed

# Example:
# plan = PlanningAgent().plan("Build a rate limiter using token bucket algorithm")
```

---

## 3. Code Writing Agent

```python
class CodingAgent:
    """Writes code based on a plan."""
    
    def write(self, plan: CodePlan) -> str:
        plan_text = f"""Implementation Plan:
Description: {plan.description}
Functions: {plan.functions}
Data Structures: {plan.data_structures}
Test Cases: {plan.test_cases}
"""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": """You are an expert Python developer.
Write complete, production-quality code based on the plan.
Requirements:
- Include type hints on all functions
- Add docstrings
- Handle errors gracefully
- Make code testable (no global state)
- Output ONLY the Python code, no explanations."""
            }, {"role": "user", "content": plan_text}],
        )
        return self._extract_code(response.choices[0].message.content)
    
    def fix(self, code: str, error: str, test_results: str = "") -> str:
        """Fix code based on error output."""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Fix the code bug. Output ONLY the corrected complete code."
            }, {"role": "user", "content": f"Code:\n```python\n{code}\n```\n\nError:\n{error}\n\nTest results:\n{test_results}"}],
        )
        return self._extract_code(response.choices[0].message.content)
    
    def _extract_code(self, content: str) -> str:
        """Extract Python code from markdown blocks."""
        if "```python" in content:
            return content.split("```python")[1].split("```")[0].strip()
        if "```" in content:
            return content.split("```")[1].split("```")[0].strip()
        return content.strip()
```

---

## 4. Sandboxed Execution

```python
import subprocess
import tempfile
import os
from dataclasses import dataclass

@dataclass
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    return_code: int
    timeout: bool = False

class Sandbox:
    """Safe code execution environment."""
    
    def __init__(self, timeout: int = 30, use_docker: bool = True):
        self.timeout = timeout
        self.use_docker = use_docker
    
    def execute(self, code: str) -> ExecutionResult:
        if self.use_docker:
            return self._execute_docker(code)
        return self._execute_local(code)
    
    def _execute_local(self, code: str) -> ExecutionResult:
        """Execute in subprocess with timeout (less safe)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            try:
                result = subprocess.run(
                    ["python", f.name],
                    capture_output=True, text=True, timeout=self.timeout,
                    env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                )
                return ExecutionResult(
                    success=result.returncode == 0,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    return_code=result.returncode,
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(success=False, stdout="", stderr="Timeout", return_code=-1, timeout=True)
            finally:
                os.unlink(f.name)
    
    def _execute_docker(self, code: str) -> ExecutionResult:
        """Execute in Docker container (safer)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            
            try:
                result = subprocess.run(
                    ["docker", "run", "--rm", "--network=none",
                     "--memory=256m", "--cpus=1",
                     "-v", f"{f.name}:/app/code.py:ro",
                     "python:3.11-slim", "python", "/app/code.py"],
                    capture_output=True, text=True, timeout=self.timeout,
                )
                return ExecutionResult(
                    success=result.returncode == 0,
                    stdout=result.stdout, stderr=result.stderr,
                    return_code=result.returncode,
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(success=False, stdout="", stderr="Timeout", return_code=-1, timeout=True)
            finally:
                os.unlink(f.name)
    
    def run_tests(self, code: str, tests: str) -> ExecutionResult:
        """Run code + tests together."""
        combined = f"{code}\n\n{tests}\n"
        # Add pytest runner
        combined += "\nimport sys; sys.exit(0 if all_tests_pass() else 1)"
        return self.execute(combined)
```

---

## 5. TDD Agent (Test-Driven Development)

```python
class TDDAgent:
    """Generates tests first, then writes code to pass them."""
    
    def __init__(self):
        self.coder = CodingAgent()
        self.sandbox = Sandbox(use_docker=False)
    
    def develop(self, requirements: str, max_iterations: int = 5) -> dict:
        # Step 1: Generate tests first
        tests = self._generate_tests(requirements)
        print(f"📝 Generated tests:\n{tests[:200]}...")
        
        # Step 2: Write code to pass tests
        code = self._write_code_for_tests(requirements, tests)
        
        # Step 3: Iterate until tests pass
        for i in range(max_iterations):
            # Combine and run
            combined = f"{code}\n\n{tests}"
            result = self.sandbox.execute(combined)
            
            if result.success:
                print(f"✅ All tests pass (iteration {i+1})")
                return {"code": code, "tests": tests, "iterations": i+1}
            
            # Fix code based on test failures
            print(f"❌ Tests failed (iteration {i+1}): {result.stderr[:100]}")
            code = self.coder.fix(code, result.stderr, result.stdout)
        
        return {"code": code, "tests": tests, "iterations": max_iterations, "status": "max_iterations_reached"}
    
    def _generate_tests(self, requirements: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": """Write pytest test cases for these requirements.
Include: happy path, edge cases, error cases. Use descriptive test names.
Output ONLY the test code with imports."""
            }, {"role": "user", "content": requirements}],
        )
        return self._extract_code(response.choices[0].message.content)
    
    def _write_code_for_tests(self, requirements: str, tests: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Write implementation code that passes these tests. Output ONLY the code."
            }, {"role": "user", "content": f"Requirements: {requirements}\n\nTests to pass:\n{tests}"}],
        )
        return self._extract_code(response.choices[0].message.content)
    
    def _extract_code(self, content: str) -> str:
        if "```python" in content:
            return content.split("```python")[1].split("```")[0].strip()
        return content.strip()
```

---

## 6. Debugging Agent

```python
class DebuggingAgent:
    """Analyzes errors and fixes code."""
    
    def debug(self, code: str, error: str) -> dict:
        # Step 1: Analyze the error
        analysis = self._analyze_error(code, error)
        
        # Step 2: Identify root cause
        root_cause = self._find_root_cause(code, error, analysis)
        
        # Step 3: Generate fix
        fixed_code = self._generate_fix(code, root_cause)
        
        return {
            "analysis": analysis,
            "root_cause": root_cause,
            "fixed_code": fixed_code,
        }
    
    def _analyze_error(self, code: str, error: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Analyze this error. What type of error is it? What line caused it? What's the immediate issue?"
            }, {"role": "user", "content": f"Code:\n{code}\n\nError:\n{error}"}],
        )
        return response.choices[0].message.content
    
    def _find_root_cause(self, code: str, error: str, analysis: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Given the error analysis, what is the ROOT CAUSE? Look beyond the immediate error to the underlying issue."
            }, {"role": "user", "content": f"Code:\n{code}\nError:\n{error}\nAnalysis:\n{analysis}"}],
        )
        return response.choices[0].message.content
    
    def _generate_fix(self, code: str, root_cause: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Fix the code based on the root cause. Output ONLY the complete corrected code."
            }, {"role": "user", "content": f"Code:\n{code}\n\nRoot cause:\n{root_cause}"}],
        )
        content = response.choices[0].message.content
        if "```python" in content:
            return content.split("```python")[1].split("```")[0].strip()
        return content

# Full pipeline
class CodeGenerationPipeline:
    def __init__(self):
        self.planner = PlanningAgent()
        self.coder = CodingAgent()
        self.debugger = DebuggingAgent()
        self.sandbox = Sandbox(use_docker=False)
    
    def generate(self, requirements: str, max_fix_attempts: int = 3) -> str:
        # Plan
        plan = self.planner.plan(requirements)
        
        # Write
        code = self.coder.write(plan)
        
        # Test and fix loop
        for attempt in range(max_fix_attempts):
            result = self.sandbox.execute(code)
            if result.success:
                return code
            
            # Debug and fix
            debug_result = self.debugger.debug(code, result.stderr)
            code = debug_result["fixed_code"]
        
        return code  # Return best attempt
```

---

## Interview Questions

### Beginner
1. **Why do code generation agents need planning before writing?** Without planning: agent writes code that misses requirements, has poor structure, hard to test. Planning defines: functions, data structures, test cases upfront. Like an architect drawing blueprints before construction. Reduces iterations needed to get correct code.
2. **Why sandbox code execution?** Agent-generated code could: infinite loop (crash system), access filesystem (data loss), make network calls (data exfiltration), consume resources (denial of service). Sandbox provides: timeout, network isolation, memory limits, read-only filesystem. Docker is most common approach.
3. **What is TDD in the context of code agents?** Test-Driven Development: generate tests FIRST from requirements, then write code to pass tests. Benefits: clear success criteria, catches regressions, forces testable design. Agent iterates: run tests → fail → fix code → run tests → pass.

### Intermediate
4. **How do you handle non-determinism in code generation?** Same prompt may generate different code each run. Solutions: temperature=0 (more deterministic), test-driven (any code that passes is correct), structured output (plan constrains implementation), multiple attempts with voting (generate 3 versions, pick best).
5. **Design the fix loop to avoid infinite iterations.** Max attempts cap. Track what was tried (don't repeat same fix). If same error persists after 2 fixes: different strategy (rewrite from scratch). Escalate: after N failures, ask human or try different model. Budget: limit total tokens spent on fixing.
6. **How do you ensure generated code is secure?** Static analysis (bandit, semgrep) on generated code. Disallow: eval, exec, os.system, subprocess without sanitization. Check for: SQL injection, path traversal, hardcoded secrets. Sandbox execution prevents runtime damage. Review tool: automated security scan before deploying.

### Advanced
7. **Design a production code generation system.** Pipeline: requirements → plan → code → lint → type-check → test → security scan → human review. Sandboxed execution (Docker, network isolated). Caching: similar requirements → reuse past code. Multi-model: cheap model for simple code, expensive for complex. Monitoring: track pass rates, iteration counts, security issues found.
8. **How would you build an agent that fixes bugs in existing codebases?** Input: bug report + codebase. Steps: 1) Localize (find relevant files via search/embeddings). 2) Reproduce (write test that fails). 3) Analyze (trace code flow to find root cause). 4) Fix (minimal change). 5) Verify (test passes, no regressions). Challenges: large codebases, dependencies, side effects.
9. **Compare plan-then-code vs iterative code generation.** Plan-then-code: structured, fewer iterations, better for complex systems, higher upfront cost. Iterative: start coding immediately, fix as you go, faster for simple tasks, may miss big-picture design. Hybrid: light plan for structure, then iterate on implementation details. Best approach depends on task complexity.

---

## Hands-On Exercise
1. Build PlanningAgent that creates structured implementation plans
2. Implement CodingAgent that generates code from plans
3. Create Sandbox with timeout and Docker execution
4. Build TDD workflow: generate tests → write code → iterate until passing
5. Implement DebuggingAgent that analyzes errors and fixes code
6. Create full pipeline: plan → write → test → fix loop (max 5 iterations)
7. Test on: "Build a LRU cache with TTL" requirement
