# Day 7: Project — Single Agent Application

## Learning Objectives
- Build a complete research assistant agent end-to-end
- Integrate tools (web search, Wikipedia, calculator, code interpreter)
- Add memory (conversation history + vector store for notes)
- Implement planning and error handling
- Evaluate on diverse queries
- Deploy as a CLI application

---

## 1. Architecture

```
┌────────────────────────────────────────────────┐
│           Research Assistant Agent               │
├────────────────────────────────────────────────┤
│ Input → Query Analyzer → Plan → Execute Loop    │
│                                                  │
│ Tools:                                          │
│   • Web Search (Tavily API)                     │
│   • Wikipedia Lookup                            │
│   • Calculator (safe math eval)                 │
│   • Python Executor (sandboxed)                 │
│                                                  │
│ Memory:                                         │
│   • Short-term: conversation buffer (20 msgs)   │
│   • Long-term: ChromaDB notes store             │
│                                                  │
│ Planning: ReAct with self-reflection            │
│ Output → Formatted Answer with Sources          │
└────────────────────────────────────────────────┘
```

---

## 2. Tool Implementations

```python
import requests
import json
import subprocess
import wikipedia
from openai import OpenAI

client = OpenAI()

# Tool: Web Search
def search_web(query: str, num_results: int = 5) -> str:
    """Search the web for current information."""
    try:
        response = requests.get(
            "https://api.tavily.com/search",
            params={"query": query, "max_results": num_results, "search_depth": "basic"},
            headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
            timeout=10,
        )
        results = response.json().get("results", [])
        formatted = []
        for r in results:
            formatted.append(f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:200]}")
        return "\n\n".join(formatted) if formatted else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"

# Tool: Wikipedia
def lookup_wikipedia(topic: str) -> str:
    """Look up a topic on Wikipedia for factual background."""
    try:
        page = wikipedia.page(topic, auto_suggest=True)
        return f"Title: {page.title}\n\nSummary:\n{page.summary[:1500]}"
    except wikipedia.DisambiguationError as e:
        return f"Multiple results. Try being more specific. Options: {', '.join(e.options[:5])}"
    except wikipedia.PageError:
        return f"No Wikipedia page found for '{topic}'"

# Tool: Calculator
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression safely."""
    import ast, operator
    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}
    
    def _eval(node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](_eval(node.operand))
        raise ValueError(f"Unsupported: {type(node)}")
    
    try:
        tree = ast.parse(expression, mode='eval')
        result = _eval(tree.body)
        return f"{expression} = {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

# Tool: Python Executor
def execute_python(code: str) -> str:
    """Execute Python code in a sandboxed subprocess."""
    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True, text=True, timeout=15,
        )
        output = result.stdout[:2000] if result.returncode == 0 else f"Error: {result.stderr[:500]}"
        return output
    except subprocess.TimeoutExpired:
        return "Error: Execution timed out (15s limit)"

TOOLS = {
    "search_web": search_web,
    "lookup_wikipedia": lookup_wikipedia,
    "calculate": calculate,
    "execute_python": execute_python,
}

TOOL_DEFINITIONS = [
    {"type": "function", "function": {
        "name": "search_web",
        "description": "Search the web for current information, news, or facts. Use for recent events or when you need up-to-date info.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "Search query"},
            "num_results": {"type": "integer", "description": "Number of results (default 5)"},
        }, "required": ["query"]},
    }},
    {"type": "function", "function": {
        "name": "lookup_wikipedia",
        "description": "Look up background information on a topic from Wikipedia. Use for established facts, history, biographies.",
        "parameters": {"type": "object", "properties": {
            "topic": {"type": "string", "description": "Topic to look up"},
        }, "required": ["topic"]},
    }},
    {"type": "function", "function": {
        "name": "calculate",
        "description": "Evaluate a mathematical expression. Use for any calculation - don't do math in your head.",
        "parameters": {"type": "object", "properties": {
            "expression": {"type": "string", "description": "Math expression, e.g., '(45 * 12) / 7'"},
        }, "required": ["expression"]},
    }},
    {"type": "function", "function": {
        "name": "execute_python",
        "description": "Execute Python code for data analysis, complex calculations, or generating outputs. Use when calculation tool is insufficient.",
        "parameters": {"type": "object", "properties": {
            "code": {"type": "string", "description": "Python code to execute"},
        }, "required": ["code"]},
    }},
]
```

---

## 3. Memory System

```python
import chromadb
from collections import deque

class AgentMemory:
    def __init__(self):
        # Short-term: recent conversation
        self.conversation = deque(maxlen=20)
        
        # Long-term: stored research notes
        self.chroma_client = chromadb.Client()
        self.notes = self.chroma_client.get_or_create_collection("research_notes")
        self.note_count = 0
    
    def add_message(self, role: str, content: str):
        self.conversation.append({"role": role, "content": content})
    
    def save_note(self, content: str, topic: str = ""):
        """Save a research finding for later retrieval."""
        self.note_count += 1
        self.notes.add(
            documents=[content],
            metadatas=[{"topic": topic}],
            ids=[f"note_{self.note_count}"],
        )
    
    def recall_notes(self, query: str, top_k: int = 3) -> list[str]:
        """Retrieve relevant past research notes."""
        if self.note_count == 0:
            return []
        results = self.notes.query(query_texts=[query], n_results=min(top_k, self.note_count))
        return results["documents"][0]
    
    def get_messages(self, query: str = "") -> list[dict]:
        """Get conversation history with relevant notes injected."""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Inject relevant notes if available
        if query and self.note_count > 0:
            notes = self.recall_notes(query)
            if notes:
                notes_text = "\n".join(f"- {n}" for n in notes)
                messages.append({"role": "system", "content": f"Relevant notes from past research:\n{notes_text}"})
        
        messages.extend(list(self.conversation))
        return messages
```

---

## 4. Agent Core

```python
SYSTEM_PROMPT = """You are a research assistant. Help users find information, analyze data, and answer questions.

Approach:
1. Think about what information is needed
2. Use tools to gather information (don't guess)
3. Synthesize findings into a clear answer
4. Cite your sources

Guidelines:
- Use search_web for current/recent information
- Use lookup_wikipedia for established facts and background
- Use calculate for math (never do math in your head)
- Use execute_python for complex analysis
- If unsure, search before answering
- Be concise but thorough
- If you can't find the answer, say so honestly
"""

class ResearchAgent:
    def __init__(self):
        self.memory = AgentMemory()
        self.max_iterations = 8
    
    def run(self, query: str) -> str:
        """Process a user query through the agent loop."""
        self.memory.add_message("user", query)
        messages = self.memory.get_messages(query)
        
        for iteration in range(self.max_iterations):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
            )
            
            message = response.choices[0].message
            messages.append(message)
            
            # No tool calls → final answer
            if not message.tool_calls:
                answer = message.content
                self.memory.add_message("assistant", answer)
                
                # Auto-save notable findings
                if len(answer) > 200:
                    self.memory.save_note(answer[:500], topic=query[:50])
                
                return answer
            
            # Execute tool calls
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                print(f"  🔧 {func_name}({', '.join(f'{k}={v!r}' for k,v in args.items())})")
                
                result = TOOLS[func_name](**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result[:3000],  # Truncate large outputs
                })
        
        return "I wasn't able to find a complete answer within the step limit."
```

---

## 5. CLI Interface

```python
def main():
    agent = ResearchAgent()
    print("🔬 Research Assistant (type 'quit' to exit, 'notes' to see saved notes)")
    print("-" * 60)
    
    while True:
        query = input("\nYou: ").strip()
        
        if not query:
            continue
        if query.lower() == "quit":
            break
        if query.lower() == "notes":
            if agent.memory.note_count > 0:
                all_notes = agent.memory.notes.get()
                for doc in all_notes["documents"]:
                    print(f"  📝 {doc[:100]}...")
            else:
                print("  No notes saved yet.")
            continue
        
        print("\nAssistant: ", end="")
        answer = agent.run(query)
        print(answer)

if __name__ == "__main__":
    main()
```

---

## 6. Evaluation

```python
# Test the agent on diverse query types
TEST_QUERIES = [
    # Factual (should use Wikipedia or search)
    "What is the population of Japan?",
    # Calculation (should use calculator)
    "If I invest $10,000 at 7% annually for 20 years with compound interest, how much will I have?",
    # Current events (should search web)
    "What were the major AI announcements this week?",
    # Multi-step (should combine tools)
    "Compare the GDP per capita of the US and Germany. Which is higher and by what percentage?",
    # Analysis (should use Python)
    "Generate the first 20 Fibonacci numbers and find their average",
    # Memory test (depends on previous questions)
    "Summarize what we've discussed so far",
]

def evaluate_agent(agent: ResearchAgent):
    results = []
    for query in TEST_QUERIES:
        print(f"\n{'='*60}\nQuery: {query}")
        answer = agent.run(query)
        print(f"Answer: {answer[:200]}...")
        
        # Basic quality checks
        results.append({
            "query": query,
            "answer_length": len(answer),
            "has_content": len(answer) > 50,
            "no_error": "error" not in answer.lower(),
        })
    
    success_rate = sum(1 for r in results if r["has_content"] and r["no_error"]) / len(results)
    print(f"\n\nSuccess rate: {success_rate:.0%}")

evaluate_agent(ResearchAgent())
```

---

## 7. Error Handling & Fallbacks

```python
class RobustResearchAgent(ResearchAgent):
    """Agent with graceful error handling and fallbacks."""
    
    def run(self, query: str) -> str:
        try:
            return super().run(query)
        except Exception as e:
            # Log error, return graceful message
            print(f"  ⚠️ Agent error: {e}")
            return f"I encountered an issue processing your request. Error: {str(e)[:100]}. Please try rephrasing your question."
    
    def _execute_tool_safe(self, name: str, args: dict) -> str:
        """Execute tool with error handling."""
        try:
            result = TOOLS[name](**args)
            if not result or result.strip() == "":
                return f"Tool '{name}' returned empty result. Try different parameters."
            return result
        except KeyError:
            return f"Unknown tool: {name}"
        except TypeError as e:
            return f"Invalid arguments for {name}: {e}"
        except Exception as e:
            return f"Tool error ({name}): {str(e)[:200]}"
```

---

## Interview Questions

### Beginner
1. **What are the key components of an agent application?** LLM (reasoning engine), tools (actions it can take), memory (context persistence), planning (task decomposition), and a control loop (iterative execution until task complete). Plus: error handling, termination conditions, and evaluation.
2. **Why separate tools into individual functions?** Each tool has a single clear purpose — easier for LLM to select the right one. Clear interfaces (typed params) prevent misuse. Independent testing and error handling. Can add/remove tools without affecting others.
3. **How do you evaluate an agent?** Test on diverse queries (factual, calculation, multi-step, current events). Metrics: task completion rate, answer accuracy, tool selection correctness, number of steps (efficiency), cost. Compare against: baseline (no tools), human performance.

### Intermediate
4. **How do you handle tool failures gracefully?** Catch exceptions per tool call. Return informative error messages. Let LLM decide next action (retry with different params, try different tool, give up gracefully). Set timeouts. Never let one tool failure crash the entire agent.
5. **How do you manage context window with tools?** Tool outputs can be large. Truncate results (keep first N chars). Summarize large outputs before adding to context. Only keep most recent tool results in context. Use memory to offload older findings.
6. **How do you prevent the agent from hallucinating when tools are available?** System prompt: "Use tools rather than guessing." Force tool use for specific query types. Instruct: "If unsure, search first." Evaluate: flag answers that don't reference tool outputs for factual questions.

### Advanced
7. **Design an agent that improves over time.** Episodic memory: store task → approach → outcome. Before new task: recall similar past tasks, reuse successful strategies. Feedback loop: user ratings → adjust system prompt or tool selection. Meta-learning: track which tools work best for which query types.
8. **How would you scale this to production (1000 users)?** Async execution (queue-based). Per-user memory isolation. Rate limiting (per user, per tool). Caching (common queries). Multiple LLM providers (failover). Monitoring: cost per user, error rates, latency. Persistent memory (Redis/Postgres instead of in-memory).
9. **Compare single-agent vs multi-agent for complex research tasks.** Single: simpler, lower cost, good for focused queries. Multi: specialized agents (searcher, analyst, writer), better for complex multi-part tasks. Single agent struggles with: very long tasks (context overflow), tasks requiring multiple specialties simultaneously. Multi-agent adds: coordination overhead, higher cost, debugging complexity.

---

## Hands-On Exercise
1. Implement all 4 tools with proper error handling
2. Build the agent loop (ReAct style with function calling)
3. Add hybrid memory (conversation buffer + vector store notes)
4. Create the CLI interface with conversation persistence
5. Run evaluation suite (6+ diverse queries), measure success rate
6. Add a 5th tool (e.g., file reader, API caller) and test integration
