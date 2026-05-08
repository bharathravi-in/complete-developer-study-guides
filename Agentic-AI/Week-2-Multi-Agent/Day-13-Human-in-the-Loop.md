# Day 13: Human-in-the-Loop

## Learning Objectives
- Implement approval gates for critical actions
- Build interactive refinement workflows
- Design tool approval mechanisms
- Understand active learning patterns with agents
- Use LangGraph interrupt for human intervention

---

## 1. Why Human-in-the-Loop (HITL)

```
When agents need humans:
- High-stakes actions (send email, deploy, delete data)
- Ambiguous requests (clarify intent before proceeding)
- Quality assurance (review before publishing)
- Learning (human feedback improves agent over time)
- Safety (prevent harmful or unauthorized actions)

HITL Spectrum:
┌──────────────────────────────────────────────┐
│ Full Autonomy ←→ Full Human Control          │
│                                              │
│ Auto-approve    Notify     Ask before  Block │
│ all actions     human      acting      until │
│                                      approved│
└──────────────────────────────────────────────┘
```

---

## 2. Approval Gates

```python
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Any

class RiskLevel(Enum):
    LOW = "low"        # Auto-approve (read operations)
    MEDIUM = "medium"  # Notify human, proceed unless vetoed
    HIGH = "high"      # Wait for explicit approval
    CRITICAL = "critical"  # Require multi-person approval

@dataclass
class Action:
    name: str
    description: str
    risk_level: RiskLevel
    params: dict

class ApprovalGate:
    """Gate that blocks execution until human approves."""
    
    def __init__(self, auto_approve_levels: list[RiskLevel] = None):
        self.auto_approve = auto_approve_levels or [RiskLevel.LOW]
        self.pending: list[Action] = []
    
    def check(self, action: Action) -> bool:
        """Returns True if action can proceed, False if needs approval."""
        if action.risk_level in self.auto_approve:
            return True
        
        # In production: send to approval queue (Slack, email, UI)
        print(f"\n⚠️ APPROVAL REQUIRED [{action.risk_level.value}]")
        print(f"Action: {action.name}")
        print(f"Description: {action.description}")
        print(f"Parameters: {action.params}")
        
        response = input("Approve? (yes/no): ").strip().lower()
        return response == "yes"

# Risk classification for common tool actions
RISK_CLASSIFICATION = {
    "web_search": RiskLevel.LOW,
    "read_file": RiskLevel.LOW,
    "write_file": RiskLevel.MEDIUM,
    "send_email": RiskLevel.HIGH,
    "delete_data": RiskLevel.CRITICAL,
    "deploy": RiskLevel.CRITICAL,
    "execute_code": RiskLevel.MEDIUM,
    "api_call_read": RiskLevel.LOW,
    "api_call_write": RiskLevel.HIGH,
}

# Integration with agent tool execution
class SafeToolExecutor:
    def __init__(self, gate: ApprovalGate):
        self.gate = gate
    
    def execute(self, tool_name: str, params: dict) -> str:
        risk = RISK_CLASSIFICATION.get(tool_name, RiskLevel.HIGH)
        action = Action(name=tool_name, description=f"Execute {tool_name}", risk_level=risk, params=params)
        
        if not self.gate.check(action):
            return f"❌ Action '{tool_name}' was rejected by human."
        
        # Execute the tool
        return self._run_tool(tool_name, params)
    
    def _run_tool(self, name: str, params: dict) -> str:
        # Actual tool execution
        return f"Executed {name} with {params}"
```

---

## 3. Interactive Refinement

```python
# Human provides feedback, agent refines iteratively

from openai import OpenAI

client = OpenAI()

class InteractiveRefinement:
    """Agent generates, human provides feedback, agent refines."""
    
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.history = [{"role": "system", "content": system_prompt}]
    
    def generate(self, task: str) -> str:
        self.history.append({"role": "user", "content": task})
        response = client.chat.completions.create(
            model="gpt-4o", messages=self.history,
        )
        result = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": result})
        return result
    
    def refine(self, feedback: str) -> str:
        """Human provides feedback, agent refines."""
        self.history.append({"role": "user", "content": f"Feedback: {feedback}\nPlease revise accordingly."})
        response = client.chat.completions.create(
            model="gpt-4o", messages=self.history,
        )
        result = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": result})
        return result
    
    def run_loop(self, task: str, max_rounds: int = 5) -> str:
        result = self.generate(task)
        for _ in range(max_rounds):
            print(f"\n{'='*60}\n{result}\n{'='*60}")
            feedback = input("\nFeedback (or 'done' to accept): ").strip()
            if feedback.lower() == "done":
                return result
            result = self.refine(feedback)
        return result

# Usage:
# refiner = InteractiveRefinement("You write professional emails.")
# final = refiner.run_loop("Write an email declining a meeting politely")
```

---

## 4. Tool Approval with Context

```python
# Show human WHAT the tool will do and WHY before approving

class ContextualApproval:
    """Provide rich context for approval decisions."""
    
    def request_approval(self, tool_call: dict, agent_reasoning: str) -> bool:
        """
        Show human: what tool, what args, why agent wants to use it.
        """
        print("\n" + "="*60)
        print("🔧 TOOL APPROVAL REQUEST")
        print(f"Tool: {tool_call['name']}")
        print(f"Arguments: {tool_call['arguments']}")
        print(f"\n💭 Agent's reasoning: {agent_reasoning}")
        print(f"\n⚡ Impact: {self._assess_impact(tool_call)}")
        print("="*60)
        
        choice = input("[A]pprove / [R]eject / [M]odify: ").strip().upper()
        
        if choice == "A":
            return True
        elif choice == "M":
            # Human can modify the arguments
            new_args = input("Modified arguments (JSON): ")
            import json
            tool_call["arguments"] = json.loads(new_args)
            return True
        return False
    
    def _assess_impact(self, tool_call: dict) -> str:
        impacts = {
            "send_email": "Will send an email that cannot be unsent",
            "delete_file": "Permanent data deletion",
            "deploy": "Changes production environment",
            "write_file": "Modifies file on disk",
        }
        return impacts.get(tool_call["name"], "Unknown impact")

# Batch approval: show all planned actions at once
class BatchApproval:
    def approve_plan(self, planned_actions: list[dict]) -> list[dict]:
        """Show complete plan, let human approve/reject individual steps."""
        print("\n📋 PROPOSED PLAN:")
        for i, action in enumerate(planned_actions):
            print(f"  {i+1}. [{action['risk']}] {action['name']}: {action['description']}")
        
        response = input("\nApprove all? (yes/no/select): ").strip().lower()
        if response == "yes":
            return planned_actions
        elif response == "select":
            indices = input("Enter step numbers to approve (e.g., 1,3,4): ")
            selected = [int(x.strip()) - 1 for x in indices.split(",")]
            return [planned_actions[i] for i in selected]
        return []
```

---

## 5. LangGraph Interrupt

```python
# LangGraph provides built-in interrupt for HITL
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
from langgraph.prebuilt import ToolNode
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]
    pending_approval: dict | None
    approved: bool

def agent_node(state: State) -> dict:
    """Agent decides what to do."""
    # Agent logic here - decides on an action
    action = {"tool": "send_email", "args": {"to": "boss@co.com", "body": "Request approved"}}
    return {"pending_approval": action, "approved": False}

def approval_gate(state: State) -> dict:
    """This node uses interrupt to pause for human input."""
    from langgraph.types import interrupt
    
    # Pause execution and wait for human
    human_response = interrupt({
        "question": "Approve this action?",
        "action": state["pending_approval"],
    })
    
    return {"approved": human_response == "yes"}

def execute_action(state: State) -> dict:
    """Execute the approved action."""
    if state["approved"]:
        # Run the action
        return {"messages": [f"✅ Executed: {state['pending_approval']}"]}
    return {"messages": ["❌ Action rejected by human."]}

def should_execute(state: State) -> str:
    if state.get("pending_approval"):
        return "approval"
    return END

# Build graph
graph = StateGraph(State)
graph.add_node("agent", agent_node)
graph.add_node("approval", approval_gate)
graph.add_node("execute", execute_action)

graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_execute, {"approval": "approval", END: END})
graph.add_edge("approval", "execute")
graph.add_edge("execute", END)

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

# Run until interrupt
config = {"configurable": {"thread_id": "1"}}
result = app.invoke({"messages": [], "pending_approval": None, "approved": False}, config)
# Graph pauses at approval_gate

# Resume with human input
result = app.invoke(None, config, input="yes")  # Human approves
```

---

## 6. Active Learning Pattern

```python
# Agent identifies uncertain situations and asks human for guidance
# Over time, learns from human decisions and asks less often

class ActiveLearningAgent:
    """Agent that learns from human feedback to reduce future interruptions."""
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.threshold = confidence_threshold
        self.learned_rules: list[dict] = []  # Past decisions to learn from
    
    def should_ask_human(self, action: str, confidence: float) -> bool:
        """Decide if human input is needed based on confidence."""
        # Check if we've seen similar situations before
        for rule in self.learned_rules:
            if self._similar(action, rule["action"]):
                return False  # We know what to do
        
        return confidence < self.threshold
    
    def _similar(self, action1: str, action2: str) -> bool:
        # Simplified similarity check
        return action1.split()[0] == action2.split()[0]
    
    def record_decision(self, action: str, human_decision: str):
        """Learn from human's decision for future reference."""
        self.learned_rules.append({
            "action": action,
            "decision": human_decision,
        })
    
    def act(self, action: str, confidence: float) -> str:
        if self.should_ask_human(action, confidence):
            print(f"🤔 Uncertain about: {action} (confidence: {confidence:.0%})")
            decision = input("How should I proceed? ")
            self.record_decision(action, decision)
            return decision
        
        # Find matching learned rule
        for rule in self.learned_rules:
            if self._similar(action, rule["action"]):
                return rule["decision"]
        
        return "proceed"  # Default
```

---

## Interview Questions

### Beginner
1. **Why is human-in-the-loop important for AI agents?** Safety: prevents harmful actions. Quality: human catches errors. Trust: users trust systems they can control. Compliance: many domains require human approval (finance, healthcare). Liability: human accountability for decisions.
2. **What's an approval gate?** A checkpoint where execution pauses until a human approves. Agent proposes action → gate shows human what/why → human approves/rejects/modifies → agent proceeds or stops. Classify actions by risk level to avoid over-asking.
3. **What are the different HITL modes?** Full autonomy (agent decides everything). Notify-only (human informed but not blocking). Approval-required (agent waits). Interactive (human collaborates throughout). Choice depends on: risk, user trust, domain requirements.

### Intermediate
4. **How do you balance automation with human oversight?** Classify by risk: auto-approve low-risk (reads), require approval for high-risk (writes, sends). Track accuracy over time — increase autonomy for reliable actions. Let users configure their comfort level. Log everything for audit.
5. **How does LangGraph interrupt work for HITL?** Graph execution pauses at interrupt node. State is checkpointed. Human provides input externally (API, UI). Graph resumes from checkpoint with human input injected. Enables: approval gates, clarification loops, collaborative editing within graph workflows.
6. **How do you design HITL that doesn't frustrate users?** Batch approvals (show full plan, approve at once). Smart defaults (pre-approve common patterns). Learn from past decisions (reduce future asks). Clear context (show WHY approval is needed). Quick actions (one-click approve). Async (don't block user's workflow).

### Advanced
7. **Design a HITL system for a customer-facing AI agent.** Tiers: auto-respond for simple queries (FAQ), human review for refunds > $100, require approval for account changes. Confidence-based: if agent unsure, escalate to human. Seamless handoff: human sees full context. Fallback: if no human available within SLA, inform customer.
8. **How do you implement active learning to reduce human intervention over time?** Track: (situation, human decision, outcome). Cluster similar situations. When confidence > threshold for a cluster, auto-decide. Monitor: if auto-decisions lead to bad outcomes, reduce threshold. Feedback loop: periodically validate with human that auto-decisions are still correct.
9. **Compare synchronous vs asynchronous HITL in production.** Sync: agent blocks until human responds. Simple but slow. Bad for real-time. Async: agent queues request, continues other work (or pauses gracefully). Human responds when available. Needs: state persistence, timeout handling, notification system. Production: usually async with SLA-based timeouts.

---

## Hands-On Exercise
1. Implement risk classification and approval gates for tool execution
2. Build interactive refinement loop (generate → feedback → revise)
3. Add contextual approval with impact assessment
4. Implement LangGraph interrupt for human approval mid-workflow
5. Create batch approval (show plan, approve/reject individual steps)
6. Build active learning: track human decisions, reduce asks over time
