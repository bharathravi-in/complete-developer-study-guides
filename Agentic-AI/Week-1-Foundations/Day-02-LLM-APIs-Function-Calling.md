# Day 2: LLM APIs & Function Calling

## Learning Objectives
- Master OpenAI Chat Completions API parameters
- Implement function calling (tools)
- Use structured outputs and JSON mode
- Handle streaming responses
- Manage tokens and costs across providers

---

## 1. OpenAI Chat Completions API

```python
from openai import OpenAI

client = OpenAI()

# Basic completion
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain recursion in one sentence."},
    ],
    temperature=0.7,      # Randomness (0=deterministic, 2=very random)
    max_tokens=150,       # Maximum output tokens
    top_p=1.0,           # Nucleus sampling (1.0 = consider all tokens)
    frequency_penalty=0,  # Penalize repeated tokens (0-2)
    presence_penalty=0,   # Penalize tokens that appeared at all (0-2)
)

print(response.choices[0].message.content)
print(f"Tokens: {response.usage.prompt_tokens} in, {response.usage.completion_tokens} out")

# Parameter guide:
# | Parameter         | Low (0)              | High (1-2)              |
# |-------------------|---------------------|-------------------------|
# | temperature       | Deterministic, factual | Creative, varied      |
# | frequency_penalty | Allow repetition     | Avoid repeating words  |
# | presence_penalty  | Normal               | Encourage new topics   |
# | top_p (0.1)      | Only top 10% tokens  | All tokens considered  |
```

---

## 2. Function Calling (Tools)

```python
import json

# Define tools that the model can call
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g., 'San Francisco, CA'",
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "Temperature unit",
                    },
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for current information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "num_results": {"type": "integer", "description": "Number of results (default 5)"},
                },
                "required": ["query"],
            },
        },
    },
]

# Send message with tools available
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Tokyo?"}],
    tools=tools,
    tool_choice="auto",  # "auto" | "none" | {"type": "function", "function": {"name": "..."}}
)

# Check if model wants to call a function
message = response.choices[0].message
if message.tool_calls:
    for tool_call in message.tool_calls:
        print(f"Function: {tool_call.function.name}")
        print(f"Arguments: {tool_call.function.arguments}")
        
        # Execute the function
        args = json.loads(tool_call.function.arguments)
        if tool_call.function.name == "get_weather":
            result = get_weather(**args)  # Your implementation
        
        # Send result back to model
        messages = [
            {"role": "user", "content": "What's the weather in Tokyo?"},
            message,  # Assistant message with tool_calls
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            },
        ]
        
        # Get final response incorporating tool results
        final_response = client.chat.completions.create(
            model="gpt-4o", messages=messages
        )
        print(final_response.choices[0].message.content)
```

---

## 3. Structured Outputs (JSON Mode)

```python
# Force model to output valid JSON
response = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": "Extract entities. Return JSON: {\"people\": [], \"places\": [], \"organizations\": []}"},
        {"role": "user", "content": "Tim Cook announced Apple will expand operations in Mumbai."},
    ],
)

import json
entities = json.loads(response.choices[0].message.content)
# {"people": ["Tim Cook"], "places": ["Mumbai"], "organizations": ["Apple"]}

# Structured Outputs with schema (more reliable)
from pydantic import BaseModel

class ExtractedEntities(BaseModel):
    people: list[str]
    places: list[str]
    organizations: list[str]

response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Extract entities from the text."},
        {"role": "user", "content": "Tim Cook announced Apple will expand in Mumbai."},
    ],
    response_format=ExtractedEntities,
)

entities = response.choices[0].message.parsed
print(entities.people)  # ["Tim Cook"]
```

---

## 4. Streaming Responses

```python
# Streaming: receive tokens as they're generated (better UX)
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a haiku about coding."}],
    stream=True,
)

full_response = ""
for chunk in stream:
    if chunk.choices[0].delta.content:
        token = chunk.choices[0].delta.content
        print(token, end="", flush=True)
        full_response += token

# Streaming with function calls
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's 2+2 and the weather in NYC?"}],
    tools=tools,
    stream=True,
)

tool_calls_buffer = {}
for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.tool_calls:
        for tc in delta.tool_calls:
            idx = tc.index
            if idx not in tool_calls_buffer:
                tool_calls_buffer[idx] = {"name": "", "arguments": ""}
            if tc.function.name:
                tool_calls_buffer[idx]["name"] = tc.function.name
            if tc.function.arguments:
                tool_calls_buffer[idx]["arguments"] += tc.function.arguments
```

---

## 5. Multi-Provider Patterns

```python
# Abstract across providers (OpenAI, Anthropic, Groq)
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    def complete(self, messages: list, **kwargs) -> str:
        pass

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-4o"):
        self.client = OpenAI()
        self.model = model
    
    def complete(self, messages: list, **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model, messages=messages, **kwargs
        )
        return response.choices[0].message.content

class AnthropicProvider(LLMProvider):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        from anthropic import Anthropic
        self.client = Anthropic()
        self.model = model
    
    def complete(self, messages: list, **kwargs) -> str:
        # Anthropic uses separate system parameter
        system = ""
        filtered_messages = []
        for m in messages:
            if m["role"] == "system":
                system = m["content"]
            else:
                filtered_messages.append(m)
        
        response = self.client.messages.create(
            model=self.model, messages=filtered_messages,
            system=system, max_tokens=kwargs.get("max_tokens", 1024),
        )
        return response.content[0].text

# Fallback pattern
class LLMWithFallback:
    def __init__(self, providers: list[LLMProvider]):
        self.providers = providers
    
    def complete(self, messages: list, **kwargs) -> str:
        for provider in self.providers:
            try:
                return provider.complete(messages, **kwargs)
            except Exception as e:
                print(f"Provider failed: {e}, trying next...")
        raise RuntimeError("All providers failed")
```

---

## 6. Error Handling & Retries

```python
import time
from openai import RateLimitError, APITimeoutError, APIConnectionError

def robust_completion(client, messages, max_retries=3, **kwargs):
    """Call LLM with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                messages=messages, **kwargs
            )
            return response
        except RateLimitError:
            wait = 2 ** attempt + np.random.random()
            print(f"Rate limited, waiting {wait:.1f}s...")
            time.sleep(wait)
        except APITimeoutError:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)
        except APIConnectionError:
            time.sleep(2)
    
    raise RuntimeError(f"Failed after {max_retries} retries")

# Token budget management
import tiktoken

def count_tokens(messages: list, model: str = "gpt-4o") -> int:
    """Count tokens in a message list."""
    encoding = tiktoken.encoding_for_model(model)
    total = 0
    for msg in messages:
        total += 4  # message overhead
        total += len(encoding.encode(msg["content"]))
    total += 2  # reply overhead
    return total

def trim_messages(messages: list, max_tokens: int = 8000, model: str = "gpt-4o"):
    """Trim oldest messages to fit within token budget."""
    while count_tokens(messages, model) > max_tokens and len(messages) > 2:
        messages.pop(1)  # Keep system message, remove oldest user/assistant
    return messages
```

---

## 7. Cost Tracking

```python
# Cost per 1M tokens (approximate, 2025)
PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku": {"input": 0.80, "output": 4.00},
}

class CostTracker:
    def __init__(self):
        self.total_cost = 0
        self.calls = []
    
    def track(self, model: str, usage):
        pricing = PRICING.get(model, {"input": 0, "output": 0})
        cost = (
            usage.prompt_tokens * pricing["input"] / 1_000_000 +
            usage.completion_tokens * pricing["output"] / 1_000_000
        )
        self.total_cost += cost
        self.calls.append({"model": model, "cost": cost, "tokens": usage.total_tokens})
        return cost

tracker = CostTracker()
# After each API call:
# cost = tracker.track(model, response.usage)
```

---

## Interview Questions

### Beginner
1. **What is function calling in LLMs?** The model can output structured tool calls (function name + arguments) instead of plain text. You execute the function, send results back, and the model incorporates them into its response. Enables LLMs to interact with external systems (APIs, databases, calculations).
2. **What's the difference between temperature and top_p?** Temperature scales logits before softmax (0=greedy, higher=more random). Top_p (nucleus sampling) considers only tokens whose cumulative probability reaches p. Both control randomness — typically use one or the other. Temperature=0 for factual, 0.7-1.0 for creative.
3. **Why use streaming responses?** User sees tokens as they arrive (perceived latency drops from seconds to milliseconds). Better UX for chat applications. Enables cancellation mid-generation. SSE (Server-Sent Events) for web, async iterators for backend.

### Intermediate
4. **How does the function calling loop work?** 1) Send messages + tool definitions. 2) Model returns tool_calls (not text). 3) Execute functions locally. 4) Send function results as tool messages. 5) Model generates final text response. Can loop multiple times for multi-step tool use.
5. **How do you manage token budgets for long conversations?** Count tokens with tiktoken. Strategies: sliding window (keep last N messages), summarize old messages, truncate from middle, use cheaper model for summarization. Reserve tokens for: system prompt (fixed), tools (fixed), response (max_tokens), conversation (flexible).
6. **Compare OpenAI vs Anthropic API patterns.** OpenAI: system in messages array, tool_calls in response, JSON mode. Anthropic: system as separate param, content blocks (text + tool_use), different stop reasons. Both support streaming and function calling. Abstraction layer recommended for multi-provider.

### Advanced
7. **Design a multi-provider LLM system with intelligent routing.** Route by: task complexity (simple→mini, complex→4o), cost budget, latency requirements. Implement: fallback chain (primary fails → secondary), load balancing, provider health checking. Track: per-provider latency, error rates, costs. Auto-switch on: rate limits, outages, cost thresholds.
8. **How do you handle parallel function calls?** Model may return multiple tool_calls in one response. Execute them in parallel (asyncio.gather). Return all results. Handle partial failures (some tools succeed, some fail). Model decides next step based on all results. Important for: research agents querying multiple sources.
9. **Design a cost-optimized function calling system.** Minimize tool definitions in prompt (only include relevant tools). Cache frequent function results. Use smaller model for tool selection, larger for synthesis. Batch similar tool calls. Track cost per tool (some trigger expensive downstream calls). Set per-request and daily budgets.

---

## Hands-On Exercise
1. Make 3 API calls with different temperature values — compare outputs
2. Implement a 2-tool function calling loop (weather + calculator)
3. Use structured outputs to extract data from unstructured text
4. Build a streaming chat interface (terminal-based)
5. Create a multi-provider wrapper with automatic fallback
6. Implement token counting and message trimming for long conversations
