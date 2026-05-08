# Day 9: Communication Protocols

## Learning Objectives
- Design agent-to-agent messaging patterns
- Compare shared state vs message passing
- Implement structured message formats
- Build conversation protocols (request-reply, pub-sub)
- Understand blackboard architecture and conflict resolution

---

## 1. Agent Communication Fundamentals

```
Why agents need to communicate:
- Division of labor (specialist agents collaborate)
- Information sharing (one agent's finding helps another)
- Coordination (avoid duplicate work, resolve conflicts)
- Delegation (manager assigns tasks to workers)

Communication patterns:
┌─────────────────────────────────────────────┐
│ Direct Messaging: Agent A → Agent B         │
│ Broadcast: Agent A → All agents             │
│ Pub/Sub: Agents subscribe to topics         │
│ Shared State: All agents read/write a board │
│ Request-Reply: A asks, B responds           │
└─────────────────────────────────────────────┘
```

---

## 2. Shared State vs Message Passing

```python
# Option 1: Shared State (Blackboard pattern)
# All agents read from and write to a shared data structure

class SharedState:
    """Central state that all agents can read/write."""
    
    def __init__(self):
        self.data: dict = {}
        self.history: list = []
    
    def write(self, agent_name: str, key: str, value: any):
        self.data[key] = value
        self.history.append({"agent": agent_name, "action": "write", "key": key})
    
    def read(self, key: str) -> any:
        return self.data.get(key)
    
    def get_all(self) -> dict:
        return self.data.copy()

# Pros: Simple, all agents see full picture
# Cons: Race conditions, no clear ownership, hard to scale

# Option 2: Message Passing
# Agents communicate through explicit messages

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
import uuid

@dataclass
class Message:
    sender: str
    receiver: str
    content: Any
    message_type: str  # "request", "response", "inform", "delegate"
    correlation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

class MessageBus:
    """Central message routing between agents."""
    
    def __init__(self):
        self.queues: dict[str, list[Message]] = {}
        self.subscribers: dict[str, list[str]] = {}  # topic → agents
    
    def register_agent(self, agent_name: str):
        self.queues[agent_name] = []
    
    def send(self, message: Message):
        """Direct message to a specific agent."""
        if message.receiver in self.queues:
            self.queues[message.receiver].append(message)
    
    def publish(self, topic: str, message: Message):
        """Publish to all subscribers of a topic."""
        for agent_name in self.subscribers.get(topic, []):
            msg_copy = Message(
                sender=message.sender, receiver=agent_name,
                content=message.content, message_type="inform",
            )
            self.queues[agent_name].append(msg_copy)
    
    def subscribe(self, agent_name: str, topic: str):
        self.subscribers.setdefault(topic, []).append(agent_name)
    
    def receive(self, agent_name: str) -> list[Message]:
        messages = self.queues.get(agent_name, [])
        self.queues[agent_name] = []
        return messages

# Pros: Explicit, traceable, scalable, supports async
# Cons: More complex, messages can be lost, ordering issues
```

---

## 3. Structured Message Formats

```python
# Agents need structured messages for reliable communication

from pydantic import BaseModel
from enum import Enum

class MessageType(Enum):
    REQUEST = "request"       # Ask another agent to do something
    RESPONSE = "response"     # Reply to a request
    INFORM = "inform"         # Share information (no reply expected)
    DELEGATE = "delegate"     # Assign a task
    REPORT = "report"         # Report task completion/failure
    QUERY = "query"           # Ask a question

class TaskMessage(BaseModel):
    """Structured task delegation message."""
    task_id: str
    description: str
    requirements: list[str] = []
    deadline: str | None = None
    priority: str = "medium"  # low, medium, high, critical
    context: dict = {}

class ResultMessage(BaseModel):
    """Structured task result message."""
    task_id: str
    status: str  # "completed", "failed", "partial"
    result: str
    confidence: float = 1.0
    artifacts: list[str] = []
    error: str | None = None

# Example flow:
# Manager → Developer: TaskMessage(description="Write login endpoint")
# Developer → Manager: ResultMessage(status="completed", result="code here...")

class AgentProtocol:
    """Standard protocol for agent communication."""
    
    def __init__(self, agent_name: str, bus: MessageBus):
        self.name = agent_name
        self.bus = bus
        self.bus.register_agent(agent_name)
    
    def request(self, receiver: str, task: TaskMessage) -> str:
        """Send a task request, return correlation ID."""
        msg = Message(
            sender=self.name, receiver=receiver,
            content=task.model_dump(), message_type="request",
        )
        self.bus.send(msg)
        return msg.correlation_id
    
    def respond(self, correlation_id: str, receiver: str, result: ResultMessage):
        """Respond to a previous request."""
        msg = Message(
            sender=self.name, receiver=receiver,
            content=result.model_dump(), message_type="response",
            correlation_id=correlation_id,
        )
        self.bus.send(msg)
    
    def inform(self, receiver: str, info: dict):
        """Share information without expecting a response."""
        msg = Message(
            sender=self.name, receiver=receiver,
            content=info, message_type="inform",
        )
        self.bus.send(msg)
```

---

## 4. Conversation Protocols

```python
# Request-Reply: Simple synchronous exchange
class RequestReplyProtocol:
    def __init__(self, bus: MessageBus):
        self.bus = bus
        self.pending: dict[str, Message] = {}
    
    def request_and_wait(self, sender: str, receiver: str, content: Any, timeout_steps: int = 10):
        msg = Message(sender=sender, receiver=receiver, content=content, message_type="request")
        self.bus.send(msg)
        self.pending[msg.correlation_id] = msg
        
        # Poll for response
        for _ in range(timeout_steps):
            messages = self.bus.receive(sender)
            for m in messages:
                if m.correlation_id == msg.correlation_id and m.message_type == "response":
                    return m.content
        return None  # Timeout

# Contract Net Protocol: Competitive task allocation
class ContractNet:
    """
    1. Manager announces task
    2. Workers bid (with cost/capability estimates)
    3. Manager selects best bidder
    4. Selected worker executes
    """
    
    def announce_task(self, manager: str, task: TaskMessage, workers: list[str]):
        """Broadcast task to potential workers."""
        for worker in workers:
            self.bus.send(Message(
                sender=manager, receiver=worker,
                content={"action": "call_for_proposals", "task": task.model_dump()},
                message_type="request",
            ))
    
    def submit_bid(self, worker: str, manager: str, task_id: str, 
                   estimated_cost: float, capability_score: float):
        """Worker submits a bid for the task."""
        self.bus.send(Message(
            sender=worker, receiver=manager,
            content={"action": "bid", "task_id": task_id, 
                     "cost": estimated_cost, "capability": capability_score},
            message_type="response",
        ))
    
    def award_contract(self, manager: str, winner: str, task: TaskMessage):
        """Manager awards task to best bidder."""
        self.bus.send(Message(
            sender=manager, receiver=winner,
            content={"action": "award", "task": task.model_dump()},
            message_type="delegate",
        ))
```

---

## 5. Blackboard Architecture

```python
class Blackboard:
    """
    Shared knowledge space where agents post findings.
    Agents can read all posted content and add their own contributions.
    A controller decides which agent acts next based on blackboard state.
    """
    
    def __init__(self):
        self.sections: dict[str, list[dict]] = {
            "hypotheses": [],
            "evidence": [],
            "conclusions": [],
            "questions": [],
        }
        self.control_data = {"current_phase": "gathering", "iteration": 0}
    
    def post(self, agent: str, section: str, content: str, confidence: float = 1.0):
        self.sections[section].append({
            "agent": agent, "content": content, 
            "confidence": confidence, "timestamp": datetime.now().isoformat(),
        })
    
    def read_section(self, section: str) -> list[dict]:
        return self.sections.get(section, [])
    
    def get_summary(self) -> str:
        """Summarize blackboard state for agent context."""
        parts = []
        for section, items in self.sections.items():
            if items:
                entries = "\n".join(f"  [{i['agent']}]: {i['content']}" for i in items[-5:])
                parts.append(f"{section.upper()}:\n{entries}")
        return "\n\n".join(parts)

# Usage: Research team blackboard
# Agent 1 (Searcher): posts evidence
# Agent 2 (Analyst): reads evidence, posts hypotheses
# Agent 3 (Critic): reads hypotheses, posts questions
# Controller: when enough evidence + hypotheses → ask for conclusions
```

---

## 6. Conflict Resolution

```python
class ConflictResolver:
    """Handle disagreements between agents."""
    
    def __init__(self, strategy: str = "voting"):
        self.strategy = strategy
    
    def resolve(self, proposals: list[dict]) -> dict:
        """
        Resolve conflicting proposals from multiple agents.
        Each proposal: {"agent": ..., "content": ..., "confidence": ...}
        """
        if self.strategy == "voting":
            return self._majority_vote(proposals)
        elif self.strategy == "confidence":
            return self._highest_confidence(proposals)
        elif self.strategy == "judge":
            return self._judge_decides(proposals)
    
    def _majority_vote(self, proposals):
        """Most common answer wins."""
        from collections import Counter
        answers = [p["content"] for p in proposals]
        most_common = Counter(answers).most_common(1)[0][0]
        return {"content": most_common, "method": "majority_vote"}
    
    def _highest_confidence(self, proposals):
        """Highest confidence agent wins."""
        best = max(proposals, key=lambda p: p["confidence"])
        return {"content": best["content"], "method": "highest_confidence", "agent": best["agent"]}
    
    def _judge_decides(self, proposals):
        """Use an LLM judge to evaluate proposals."""
        proposals_text = "\n".join(
            f"Agent {p['agent']} (confidence {p['confidence']}): {p['content']}"
            for p in proposals
        )
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"These agents disagree. Which answer is best and why?\n\n{proposals_text}"}],
        )
        return {"content": response.choices[0].message.content, "method": "judge"}
```

---

## Interview Questions

### Beginner
1. **Why do multi-agent systems need communication protocols?** Agents must coordinate: share findings, delegate tasks, avoid duplicate work, resolve conflicts. Without protocols: chaos, lost messages, unclear responsibilities. Protocols define: message format, who talks to whom, expected responses.
2. **What's the difference between shared state and message passing?** Shared state: all agents read/write a common data structure (simple but race conditions). Message passing: explicit messages between agents (more complex but traceable, scalable). Choose based on: team size, concurrency needs, debugging requirements.
3. **What is a blackboard architecture?** Shared knowledge space where agents post findings. No direct agent-to-agent communication. A controller decides which agent acts based on current board state. Good for: collaborative problem-solving where agents contribute different expertise.

### Intermediate
4. **How do you handle message ordering and delivery in multi-agent systems?** Problems: messages arrive out of order, agents process at different speeds. Solutions: sequence numbers, timestamps, correlation IDs for request-reply pairs, message queues with ordering guarantees, acknowledgment mechanisms.
5. **Explain the Contract Net Protocol.** Manager announces task → workers bid (cost + capability) → manager awards to best bidder → winner executes → reports result. Enables dynamic task allocation based on capability. Good for: heterogeneous agents with different strengths.
6. **How do you resolve conflicts between agents?** Voting (majority wins), confidence-weighted (most confident wins), judge (separate LLM evaluates proposals), hierarchy (senior agent overrides), consensus (iterate until agreement). Choice depends on: stakes, number of agents, domain.

### Advanced
7. **Design a communication system for 10+ agents working on a complex task.** Hierarchical: team leads coordinate sub-teams. Message bus with topics (agents subscribe to relevant topics). Structured messages (Pydantic models). Async processing (agents work independently, post results). Controller: monitors progress, resolves blockers, reallocates resources.
8. **How do you debug communication issues in multi-agent systems?** Full message logging (sender, receiver, content, timestamp). Trace correlation IDs through the system. Visualize message flow (sequence diagrams). Monitor: message latency, queue depths, unprocessed messages. Replay: re-run from message log for debugging.
9. **Compare synchronous vs asynchronous agent communication.** Sync (request-reply): simple mental model, agent waits for response. Blocks progress. Async (fire-and-forget + callbacks): agents work independently, higher throughput. Complex: need to handle responses arriving out of order. Production: usually async with timeouts.

---

## Hands-On Exercise
1. Implement a MessageBus with direct messaging and pub/sub
2. Create structured message types (TaskMessage, ResultMessage)
3. Build request-reply protocol between two agents
4. Implement a blackboard system with 3 agents collaborating
5. Add conflict resolution (voting between 3 agent proposals)
6. Trace message flow through a 3-agent system (log and visualize)
