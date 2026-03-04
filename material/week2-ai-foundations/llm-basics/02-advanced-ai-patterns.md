# Advanced AI Engineering — Agents, Evaluation, Fine-Tuning & Production LLM Patterns

> Topics beyond basic RAG that separate senior AI engineers from juniors.

---

## 1. LLM Agents & Tool Use

### What is an Agent?
An agent is an LLM that can **decide which actions to take** to accomplish a goal. Instead of a single prompt→response, the agent enters a loop:
1. Think about what to do
2. Choose a tool/action
3. Observe the result
4. Decide if done or needs more steps

### OpenAI Function Calling (Tool Use)
```python
from openai import OpenAI

client = OpenAI()

# Define tools
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search the knowledge base for relevant information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_profile",
            "description": "Get information about a user by their ID",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email notification",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    }
]

# Implement tool handlers
def handle_tool_call(name: str, arguments: dict) -> str:
    if name == "search_documents":
        results = rag_service.search(arguments["query"], arguments.get("top_k", 5))
        return json.dumps(results)
    elif name == "get_user_profile":
        user = user_service.get(arguments["user_id"])
        return json.dumps(user)
    elif name == "send_email":
        send_email(**arguments)
        return "Email sent successfully"
    return "Unknown tool"

# Agent loop
def run_agent(user_message: str, max_iterations: int = 5) -> str:
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use tools when needed."},
        {"role": "user", "content": user_message}
    ]

    for i in range(max_iterations):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            tool_choice="auto",  # Let model decide
        )

        message = response.choices[0].message

        # If no tool calls, return the text response
        if not message.tool_calls:
            return message.content or ""

        # Process tool calls
        messages.append(message)  # Add assistant message with tool calls

        for tool_call in message.tool_calls:
            result = handle_tool_call(
                tool_call.function.name,
                json.loads(tool_call.function.arguments)
            )
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })

    return "Agent reached maximum iterations"
```

### ReAct Pattern (Reason + Act)
```python
REACT_SYSTEM_PROMPT = """You are an AI assistant that solves problems step by step.

For each step, output:
Thought: [your reasoning about what to do next]
Action: [the tool to use] with [parameters]
Observation: [result of the action - this will be filled in]

When you have the final answer:
Thought: I now have enough information
Final Answer: [your answer]

Available tools:
- search_documents(query): Search the knowledge base
- calculate(expression): Evaluate a math expression
- get_current_date(): Get today's date
"""
```

---

## 2. RAG Evaluation (RAGAS Framework)

### Key Metrics
```python
# 1. Context Precision — Are retrieved chunks relevant?
def context_precision(question: str, retrieved_chunks: list[str], ground_truth: str) -> float:
    """How many retrieved chunks are actually relevant?"""
    relevant = 0
    for chunk in retrieved_chunks:
        # Use LLM to judge relevance
        prompt = f"Is this chunk relevant to answering '{question}'?\nChunk: {chunk}\nAnswer: yes/no"
        if llm_judge(prompt) == "yes":
            relevant += 1
    return relevant / len(retrieved_chunks)

# 2. Context Recall — Did we retrieve all relevant info?
def context_recall(question: str, retrieved_chunks: list[str], ground_truth: str) -> float:
    """What fraction of the ground truth is covered by retrieved chunks?"""
    # Use LLM to check if ground truth claims are in the context
    prompt = f"""Given the question: {question}
Ground truth answer: {ground_truth}
Retrieved context: {' '.join(retrieved_chunks)}

What fraction of claims in the ground truth are supported by the context?
Return a number between 0 and 1."""
    return float(llm_judge(prompt))

# 3. Faithfulness — Does the answer stick to the context?
def faithfulness(answer: str, context: str) -> float:
    """Does the answer only contain information from the context?"""
    prompt = f"""Given the context and the answer, identify claims in the answer
that are NOT supported by the context.

Context: {context}
Answer: {answer}

List unsupported claims (or "none"):"""
    unsupported = llm_judge(prompt)
    return 0.0 if unsupported != "none" else 1.0

# 4. Answer Relevance — Does the answer address the question?
def answer_relevance(question: str, answer: str) -> float:
    """Is the answer relevant to the question asked?"""
    prompt = f"Rate from 0-1 how well this answer addresses the question.\nQ: {question}\nA: {answer}"
    return float(llm_judge(prompt))
```

### Evaluation Pipeline
```python
class RAGEvaluator:
    """Evaluate RAG quality on a test set."""

    def __init__(self, rag_pipeline, test_cases: list[dict]):
        self.rag = rag_pipeline
        self.test_cases = test_cases  # [{question, expected_answer, relevant_doc_ids}]

    def evaluate(self) -> dict:
        scores = {"precision": [], "recall": [], "faithfulness": [], "relevance": []}

        for case in self.test_cases:
            result = self.rag.query(case["question"])

            scores["precision"].append(
                context_precision(case["question"], result["chunks"], case["expected_answer"])
            )
            scores["faithfulness"].append(
                faithfulness(result["answer"], result["context"])
            )
            scores["relevance"].append(
                answer_relevance(case["question"], result["answer"])
            )

        return {
            metric: sum(vals) / len(vals)
            for metric, vals in scores.items()
        }

# Usage
test_set = [
    {
        "question": "What is the GIL?",
        "expected_answer": "The GIL allows only one thread to execute Python bytecode at a time",
    },
    {
        "question": "How does RAG work?",
        "expected_answer": "RAG retrieves relevant documents and uses them as context for LLM generation",
    },
]

evaluator = RAGEvaluator(rag_pipeline, test_set)
results = evaluator.evaluate()
print(results)
# {'precision': 0.85, 'faithfulness': 0.92, 'relevance': 0.88}
```

---

## 3. Advanced RAG Patterns

### Multi-Query RAG
```python
def multi_query_rag(question: str, n_queries: int = 3) -> list[Chunk]:
    """Generate multiple search queries to improve retrieval."""
    # Step 1: Generate alternative queries
    prompt = f"""Generate {n_queries} different search queries for: "{question}"
    Each query should capture a different aspect or phrasing.
    Return as a JSON list of strings."""

    response = llm.generate(prompt)
    queries = json.loads(response)

    # Step 2: Retrieve for each query
    all_chunks = []
    seen_ids = set()
    for q in [question] + queries:
        results = vector_store.search(embed(q), top_k=3)
        for chunk, score in results:
            if chunk.id not in seen_ids:
                all_chunks.append((chunk, score))
                seen_ids.add(chunk.id)

    # Step 3: Re-rank by score
    all_chunks.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in all_chunks[:5]]
```

### Hypothetical Document Embedding (HyDE)
```python
def hyde_rag(question: str) -> list[Chunk]:
    """Generate a hypothetical answer, embed it, search with that."""
    # Step 1: Generate hypothetical answer
    prompt = f"Write a detailed paragraph answering: {question}"
    hypothetical = llm.generate(prompt)

    # Step 2: Embed the hypothetical answer (not the question)
    vector = embed(hypothetical)

    # Step 3: Search with enriched vector
    # The hypothetical answer is semantically closer to real answers
    # than a short question would be
    return vector_store.search(vector, top_k=5)
```

### Contextual Compression
```python
def contextual_compression(question: str, chunks: list[str]) -> list[str]:
    """Extract only the relevant parts from retrieved chunks."""
    compressed = []
    for chunk in chunks:
        prompt = f"""Extract ONLY the sentences from the following text that are relevant
to answering: "{question}"

Text: {chunk}

Relevant sentences:"""
        relevant = llm.generate(prompt)
        if relevant.strip():
            compressed.append(relevant)
    return compressed
```

### Self-Reflective RAG (CRAG)
```python
def corrective_rag(question: str) -> str:
    """Retrieved docs are evaluated; if low quality, try web search."""
    # Step 1: Normal retrieval
    chunks = retrieve(question, top_k=5)

    # Step 2: Grade each chunk
    relevant_chunks = []
    for chunk in chunks:
        grade = llm.generate(
            f"Is this relevant to '{question}'? Answer 'yes' or 'no'.\n{chunk.text}"
        )
        if "yes" in grade.lower():
            relevant_chunks.append(chunk)

    # Step 3: If not enough relevant chunks, fall back
    if len(relevant_chunks) < 2:
        # Option A: web search
        web_results = web_search(question)
        relevant_chunks.extend(web_results)
        # Option B: re-query with expanded terms
        # Option C: return "I don't have enough information"

    # Step 4: Generate with verified context
    return generate(question, relevant_chunks)
```

---

## 4. Fine-Tuning Guide

### When to Fine-Tune
| Use Case | RAG or Fine-Tune? |
|----------|-------------------|
| Add company knowledge | RAG ✅ |
| Change response style/format | Fine-Tune ✅ |
| Domain-specific terminology | Fine-Tune ✅ |
| Always up-to-date data | RAG ✅ |
| Consistent JSON output | Fine-Tune ✅ |
| Classification (many categories) | Fine-Tune ✅ |
| Question answering | RAG ✅ |
| Both format + knowledge | RAG + Fine-Tune ✅ |

### OpenAI Fine-Tuning
```python
# 1. Prepare training data (JSONL format)
# training_data.jsonl
# {"messages": [{"role": "system", "content": "You are a medical assistant."}, {"role": "user", "content": "What is hypertension?"}, {"role": "assistant", "content": "Hypertension is..."}]}

# 2. Upload file
from openai import OpenAI
client = OpenAI()

file = client.files.create(
    file=open("training_data.jsonl", "rb"),
    purpose="fine-tune"
)

# 3. Create fine-tuning job
job = client.fine_tuning.jobs.create(
    training_file=file.id,
    model="gpt-4o-mini-2024-07-18",
    hyperparameters={
        "n_epochs": 3,
        "learning_rate_multiplier": 1.8,
    }
)

# 4. Monitor
status = client.fine_tuning.jobs.retrieve(job.id)
print(status.status)  # "running" → "succeeded"

# 5. Use fine-tuned model
response = client.chat.completions.create(
    model=job.fine_tuned_model,  # "ft:gpt-4o-mini:org:custom:id"
    messages=[{"role": "user", "content": "What is hypertension?"}]
)
```

### Training Data Best Practices
```
Minimum: 50 examples (10+ is technically possible but low quality)
Ideal: 200-500 examples for good quality
Format: Always use system + user + assistant messages
Quality: Examples should represent the exact format/style you want
Diversity: Include edge cases and variations
Don't: Include knowledge that changes (use RAG for that)
```

---

## 5. Structured Output (JSON Mode)

### OpenAI JSON Mode
```python
# Guaranteed valid JSON output
response = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": "Return JSON with keys: answer, confidence, sources"},
        {"role": "user", "content": "What is Python?"}
    ]
)
data = json.loads(response.choices[0].message.content)
```

### Pydantic + LLM Output Parsing
```python
from pydantic import BaseModel

class RAGAnswer(BaseModel):
    answer: str
    confidence: float  # 0.0 to 1.0
    sources: list[str]
    follow_up_questions: list[str]

def structured_query(question: str) -> RAGAnswer:
    schema = RAGAnswer.model_json_schema()

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": f"Return a JSON object matching this schema: {json.dumps(schema)}"
            },
            {"role": "user", "content": question}
        ]
    )

    data = json.loads(response.choices[0].message.content)
    return RAGAnswer(**data)  # Validates with Pydantic
```

---

## 6. Streaming with Token Counting

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens for a text string."""
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(text))

async def stream_with_metrics(prompt: str) -> dict:
    """Stream response and track metrics."""
    start = time.time()
    input_tokens = count_tokens(prompt)
    output_tokens = 0
    full_response = ""

    stream = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in stream:
        if chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            full_response += token
            output_tokens += 1
            yield token  # Stream to client

    latency = time.time() - start

    # Cost calculation
    input_cost = input_tokens * 0.03 / 1000   # GPT-4 input
    output_cost = output_tokens * 0.06 / 1000  # GPT-4 output

    metrics = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "latency_seconds": round(latency, 2),
        "input_cost": round(input_cost, 4),
        "output_cost": round(output_cost, 4),
        "total_cost": round(input_cost + output_cost, 4),
        "tokens_per_second": round(output_tokens / latency, 1),
    }
    # Log metrics for monitoring
    logger.info("LLM stream completed", extra={"extra": metrics})
```

---

## 7. Local LLMs (Ollama, vLLM)

### Ollama (Easiest local LLM)
```bash
# Install
curl -fsSL https://ollama.ai/install.sh | sh

# Run a model
ollama run llama3.1      # Chat in terminal
ollama run mistral       # Smaller, faster
ollama run codellama     # Code-focused

# API (OpenAI-compatible!)
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1",
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

### Using Ollama from Python (same as OpenAI!)
```python
from openai import OpenAI

# Point to Ollama instead of OpenAI
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # Required but unused
)

response = client.chat.completions.create(
    model="llama3.1",
    messages=[{"role": "user", "content": "What is RAG?"}],
    temperature=0,
)
print(response.choices[0].message.content)

# Same code works with OpenAI or Ollama — just change base_url!
```

### When to Use Local vs Cloud
```
Local (Ollama/vLLM):
  ✅ Development & testing (no API costs)
  ✅ Privacy-sensitive data
  ✅ Unlimited requests
  ✅ Offline capability
  ❌ Lower quality than GPT-4
  ❌ Requires GPU for good performance

Cloud (OpenAI/Claude):
  ✅ Best quality (GPT-4, Claude 3.5)
  ✅ No infrastructure to manage
  ✅ Always latest models
  ❌ API costs
  ❌ Rate limits
  ❌ Data leaves your network
```

---

## 8. LLM Guardrails & Safety

```python
class LLMGuardrails:
    """Production safety layer for LLM outputs."""

    def __init__(self):
        self.blocked_patterns = [
            r"(?i)(api[_\s]?key|secret|password)\s*[:=]\s*\S+",  # Credentials
            r"(?i)(ignore|forget)\s+(all\s+)?(previous|above)\s+instructions",  # Injection
        ]

    def check_input(self, text: str) -> tuple[bool, str]:
        """Check user input before sending to LLM."""
        if len(text) > 10000:
            return False, "Input too long (max 10,000 characters)"
        for pattern in self.blocked_patterns:
            if re.search(pattern, text):
                return False, "Input contains blocked pattern"
        return True, "ok"

    def check_output(self, output: str, system_prompt: str) -> tuple[bool, str]:
        """Check LLM output before returning to user."""
        # Check for system prompt leakage
        if system_prompt[:50].lower() in output.lower():
            return False, "Output may contain system prompt"
        # Check for credential patterns
        for pattern in self.blocked_patterns[:1]:
            if re.search(pattern, output):
                return False, "Output may contain credentials"
        return True, "ok"

# Usage in pipeline
guardrails = LLMGuardrails()

safe, reason = guardrails.check_input(user_message)
if not safe:
    return {"error": reason}

response = llm.generate(user_message)

safe, reason = guardrails.check_output(response, system_prompt)
if not safe:
    return {"error": "Response filtered for safety"}

return {"answer": response}
```

---

## Key Takeaways
1. **Agents**: LLMs that use tools in a loop — the future of AI applications
2. **Evaluation**: Use RAGAS metrics (precision, recall, faithfulness, relevance) — test your RAG like you test code
3. **Advanced RAG**: Multi-query, HyDE, contextual compression, CRAG improve quality significantly
4. **Fine-tuning**: For format/style, NOT for knowledge. Start with 200+ examples.
5. **Structured Output**: JSON mode + Pydantic = reliable LLM outputs
6. **Local LLMs**: Ollama for dev, cloud for prod. Same OpenAI API interface.
7. **Guardrails**: Always validate inputs and outputs in production
