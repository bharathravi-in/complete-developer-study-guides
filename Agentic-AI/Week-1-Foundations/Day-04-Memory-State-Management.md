# Day 4: Memory & State Management

## Learning Objectives
- Understand why agents need memory (context window limits)
- Implement short-term memory (sliding window, token buffer)
- Build long-term memory (summaries, vector stores)
- Design episodic and working memory systems
- Explore MemGPT architecture

---

## 1. Why Agents Need Memory

```
Problem: LLMs have fixed context windows (4K-128K tokens)
- Long conversations overflow the window
- Past context is lost (no "native" memory)
- Relevant information from hours ago becomes inaccessible

Memory types (inspired by human cognition):
┌─────────────────────────────────────────────────┐
│ Working Memory: Current task context (scratchpad)│
├─────────────────────────────────────────────────┤
│ Short-term: Recent conversation (buffer/window)  │
├─────────────────────────────────────────────────┤
│ Long-term: Past interactions, learned facts      │
│   - Episodic: Specific past events              │
│   - Semantic: General knowledge/facts           │
└─────────────────────────────────────────────────┘
```

---

## 2. Short-Term Memory

```python
from collections import deque
import tiktoken

# Method 1: Sliding Window (keep last N messages)
class WindowMemory:
    def __init__(self, max_messages: int = 20):
        self.messages = deque(maxlen=max_messages)
        self.system_prompt = None
    
    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
    
    def get_messages(self) -> list[dict]:
        msgs = []
        if self.system_prompt:
            msgs.append({"role": "system", "content": self.system_prompt})
        msgs.extend(list(self.messages))
        return msgs

# Method 2: Token Buffer (keep messages within token budget)
class TokenBufferMemory:
    def __init__(self, max_tokens: int = 4000, model: str = "gpt-4o"):
        self.max_tokens = max_tokens
        self.messages = []
        self.encoding = tiktoken.encoding_for_model(model)
    
    def _count_tokens(self, messages: list[dict]) -> int:
        total = 0
        for msg in messages:
            total += len(self.encoding.encode(msg["content"])) + 4
        return total
    
    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        # Trim oldest messages if over budget
        while self._count_tokens(self.messages) > self.max_tokens and len(self.messages) > 2:
            self.messages.pop(0)
    
    def get_messages(self) -> list[dict]:
        return self.messages.copy()
```

---

## 3. Long-Term Memory: Summary

```python
from openai import OpenAI

client = OpenAI()

class SummaryMemory:
    """Summarize old messages to compress history."""
    
    def __init__(self, max_recent: int = 10, summary_threshold: int = 20):
        self.recent_messages = []
        self.summary = ""
        self.max_recent = max_recent
        self.summary_threshold = summary_threshold
    
    def add(self, role: str, content: str):
        self.recent_messages.append({"role": role, "content": content})
        
        # When buffer is too large, summarize older messages
        if len(self.recent_messages) > self.summary_threshold:
            self._compress()
    
    def _compress(self):
        """Summarize older messages into running summary."""
        to_summarize = self.recent_messages[:self.max_recent]
        self.recent_messages = self.recent_messages[self.max_recent:]
        
        conversation_text = "\n".join(
            f"{m['role']}: {m['content']}" for m in to_summarize
        )
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "user",
                "content": f"Summarize this conversation, preserving key facts, decisions, and user preferences:\n\nPrevious summary: {self.summary}\n\nNew conversation:\n{conversation_text}"
            }],
            temperature=0,
        )
        self.summary = response.choices[0].message.content
    
    def get_messages(self) -> list[dict]:
        messages = []
        if self.summary:
            messages.append({
                "role": "system",
                "content": f"Conversation summary so far:\n{self.summary}"
            })
        messages.extend(self.recent_messages)
        return messages
```

---

## 4. Long-Term Memory: Vector Store

```python
import chromadb
from sentence_transformers import SentenceTransformer
from datetime import datetime

class VectorMemory:
    """Store and retrieve memories by semantic similarity."""
    
    def __init__(self, collection_name: str = "agent_memory"):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(collection_name)
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.memory_count = 0
    
    def store(self, content: str, metadata: dict = None):
        """Store a memory (conversation turn, fact, decision)."""
        self.memory_count += 1
        self.collection.add(
            documents=[content],
            metadatas=[{
                "timestamp": datetime.now().isoformat(),
                **(metadata or {}),
            }],
            ids=[f"mem_{self.memory_count}"],
        )
    
    def recall(self, query: str, top_k: int = 5) -> list[str]:
        """Retrieve relevant memories for a query."""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
        )
        return results["documents"][0] if results["documents"] else []
    
    def store_conversation_turn(self, user_msg: str, assistant_msg: str):
        """Store a conversation exchange as a memory."""
        memory_text = f"User asked: {user_msg}\nAssistant answered: {assistant_msg}"
        self.store(memory_text, {"type": "conversation"})

class HybridMemory:
    """Combine short-term buffer + long-term vector store."""
    
    def __init__(self):
        self.short_term = TokenBufferMemory(max_tokens=3000)
        self.long_term = VectorMemory()
    
    def add(self, role: str, content: str):
        self.short_term.add(role, content)
        if role == "user":
            # Store user messages for long-term recall
            self.long_term.store(content, {"type": "user_message"})
    
    def get_messages(self, current_query: str) -> list[dict]:
        """Get messages with relevant long-term memories injected."""
        # Recall relevant past memories
        memories = self.long_term.recall(current_query, top_k=3)
        
        messages = []
        if memories:
            memory_context = "\n".join(f"- {m}" for m in memories)
            messages.append({
                "role": "system",
                "content": f"Relevant past context:\n{memory_context}"
            })
        
        messages.extend(self.short_term.get_messages())
        return messages
```

---

## 5. Episodic Memory

```python
class EpisodicMemory:
    """Store and recall specific past episodes (task completions, interactions)."""
    
    def __init__(self):
        self.vector_store = VectorMemory("episodes")
        self.episodes = []
    
    def record_episode(self, task: str, actions: list[str], outcome: str, success: bool):
        """Record a completed task as an episode."""
        episode = {
            "task": task,
            "actions": actions,
            "outcome": outcome,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }
        self.episodes.append(episode)
        
        # Store searchable summary
        summary = f"Task: {task}. Actions: {', '.join(actions)}. Outcome: {outcome}. Success: {success}"
        self.vector_store.store(summary, {"type": "episode", "success": str(success)})
    
    def recall_similar_tasks(self, current_task: str, top_k: int = 3) -> list[str]:
        """Find similar past tasks to inform current approach."""
        return self.vector_store.recall(current_task, top_k)
    
    def get_success_patterns(self, task: str) -> list[str]:
        """Get successful approaches for similar tasks."""
        memories = self.vector_store.recall(task, top_k=5)
        return [m for m in memories if "Success: True" in m]
```

---

## 6. Working Memory (Scratchpad)

```python
class WorkingMemory:
    """Scratchpad for current task — structured state the agent maintains."""
    
    def __init__(self):
        self.current_goal: str = ""
        self.sub_tasks: list[dict] = []
        self.findings: list[str] = []
        self.decisions: list[str] = []
    
    def set_goal(self, goal: str):
        self.current_goal = goal
        self.sub_tasks = []
        self.findings = []
    
    def add_subtask(self, task: str, status: str = "pending"):
        self.sub_tasks.append({"task": task, "status": status})
    
    def complete_subtask(self, index: int, result: str):
        self.sub_tasks[index]["status"] = "done"
        self.findings.append(result)
    
    def to_context(self) -> str:
        """Render working memory as context for the LLM."""
        parts = [f"Current Goal: {self.current_goal}"]
        
        if self.sub_tasks:
            tasks_str = "\n".join(
                f"  {'✓' if t['status']=='done' else '○'} {t['task']}"
                for t in self.sub_tasks
            )
            parts.append(f"Sub-tasks:\n{tasks_str}")
        
        if self.findings:
            parts.append(f"Findings:\n" + "\n".join(f"  - {f}" for f in self.findings))
        
        return "\n\n".join(parts)
```

---

## 7. MemGPT Architecture

```python
# MemGPT: LLM manages its own memory like an OS manages virtual memory
# Key insight: Let the LLM decide what to store/retrieve

# Architecture:
# Main Context (limited) = working memory
# Archival Memory (unlimited) = long-term storage (vector DB)
# Recall Memory = searchable conversation history

# The LLM has tools to manage its own memory:
memory_tools = [
    {
        "type": "function",
        "function": {
            "name": "core_memory_save",
            "description": "Save an important fact about the user or conversation to persistent memory. Use when you learn something worth remembering.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string", "description": "Category (e.g., 'user_preferences', 'project_details')"},
                    "value": {"type": "string", "description": "The fact to remember"},
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "archival_memory_search",
            "description": "Search your long-term memory for relevant past information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for"},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "conversation_search",
            "description": "Search past conversations for relevant context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer", "default": 5},
                },
                "required": ["query"],
            },
        },
    },
]

# System prompt for MemGPT-style agent:
memgpt_system = """You manage your own memory. You have limited context, so proactively:
- Save important facts using core_memory_save
- Search archival_memory_search when you need past context
- Search conversation_search to recall past discussions

Always check your memory before saying "I don't know" about something previously discussed."""
```

---

## Interview Questions

### Beginner
1. **Why do agents need external memory?** LLMs have fixed context windows. Long conversations overflow them, losing earlier information. Memory systems let agents: remember user preferences across sessions, recall past decisions, maintain context for long-running tasks. Without memory, every interaction starts from scratch.
2. **What's the difference between a sliding window and summary memory?** Sliding window: keeps last N messages, drops oldest (simple, may lose important early context). Summary: compresses old messages into a summary (preserves key info, but loses details). Summary is better for long conversations where early decisions matter.
3. **What is vector store memory?** Store conversation snippets/facts as embeddings in a vector database. On new query, embed it and find semantically similar past memories. Enables: recall relevant context from thousands of past interactions, not just recent ones.

### Intermediate
4. **Explain the MemGPT approach.** LLM manages its own memory like an OS manages virtual memory. Has tools: save to memory, search memory, page in/out context. Main context = limited working memory. Archival = unlimited long-term. The LLM decides what's important to remember and when to recall. Self-directed memory management.
5. **How do you combine different memory types?** Hybrid approach: token buffer (recent context) + vector store (long-term recall) + working memory (current task state). On each turn: inject recent buffer + relevant vector results + task scratchpad. Budget tokens across each component.
6. **How do you handle memory in multi-session agents?** Persist memory between sessions: vector store (persistent DB), summary (stored as text), user profile (key facts). On new session: load user profile + search relevant past sessions + start fresh buffer. Clear working memory between sessions but keep episodic memory.

### Advanced
7. **Design a memory system for a coding assistant that works across sessions.** Short-term: current file context + recent edits. Long-term: project structure, coding patterns used, user preferences (style, frameworks). Episodic: past debugging sessions (what worked). Working: current task plan, files being modified. Persistence: SQLite for structured data, ChromaDB for semantic search.
8. **How do you evaluate memory system quality?** Recall accuracy: does the system find relevant past context? Precision: are retrieved memories actually useful? Staleness: does it surface outdated info? Compression quality: does summary preserve critical facts? User test: can agent correctly answer questions about past interactions?
9. **What are the failure modes of agent memory systems?** False memories (hallucinated stored facts), stale memories (outdated info treated as current), memory overflow (too much irrelevant context injected), privacy leakage (memories from one user accessible to another in multi-tenant), summary drift (key details lost through repeated compression).

---

## Hands-On Exercise
1. Implement sliding window memory (test with 50-turn conversation)
2. Build summary memory — verify important facts survive compression
3. Create vector store memory — test semantic recall accuracy
4. Implement working memory scratchpad for a multi-step task
5. Build hybrid memory (buffer + vector) — compare with buffer-only
6. Add MemGPT-style self-managed memory tools to an agent
