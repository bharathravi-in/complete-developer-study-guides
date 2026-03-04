# LLM Basics - Complete Guide for AI Engineers

## What is an LLM?

Large Language Model (LLM) = A neural network trained on massive text data that can understand and generate human language.

**Key Models:**
| Model | Provider | Use Case |
|-------|----------|----------|
| GPT-4 / GPT-4o | OpenAI | General purpose, best quality |
| GPT-3.5-turbo | OpenAI | Fast, cheap, good enough |
| Claude 3 | Anthropic | Long context, safety |
| Gemini | Google | Multimodal |
| Llama 3 | Meta | Open source, self-hosted |
| Mistral | Mistral AI | Open source, fast |

---

## 1. How Transformers Work (Simplified)

```
Input Text → Tokenization → Embeddings → Attention Layers → Output Probabilities → Generated Text
```

### Key Concepts:

**Tokenization:**
- Text is split into "tokens" (sub-words)
- "Hello world" → ["Hello", " world"] (2 tokens)
- "Embeddings" → ["Em", "bed", "dings"] (3 tokens)
- ~1 token ≈ 4 characters or 0.75 words
- GPT-4: 128K token context window

```python
# Approximate token counting
def estimate_tokens(text: str) -> int:
    """Rough estimate: 1 token ≈ 4 chars."""
    return len(text) // 4

# Exact counting with tiktoken
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

text = "Hello, I am an AI engineer learning about embeddings"
print(count_tokens(text))  # ~11 tokens
```

**Attention Mechanism:**
- Allows the model to focus on relevant parts of input
- "The cat sat on the mat because **it** was tired" → "it" attends to "cat"
- Self-attention: each token looks at all other tokens
- Multi-head attention: multiple attention patterns in parallel

**Context Window:**
- Maximum input + output tokens the model can handle
- GPT-4: 128K tokens (~100 pages)
- GPT-3.5: 16K tokens
- Claude 3: 200K tokens
- **Critical for RAG**: determines how much context you can send

---

## 2. Using the OpenAI API

```python
# pip install openai

from openai import OpenAI

client = OpenAI(api_key="sk-your-key-here")

# Basic completion
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "What is RAG in AI?"}
    ],
    temperature=0.7,
    max_tokens=500
)

answer = response.choices[0].message.content
print(answer)
```

### Key Parameters:

```python
response = client.chat.completions.create(
    model="gpt-4",           # Model to use
    messages=[...],           # Conversation history
    
    # TEMPERATURE: Controls randomness
    # 0.0 = deterministic (same input → same output) — USE FOR Q&A
    # 0.7 = balanced creativity — USE FOR GENERAL CHAT
    # 1.0 = maximum creativity — USE FOR CREATIVE WRITING
    temperature=0.7,
    
    # MAX_TOKENS: Maximum output length
    max_tokens=500,
    
    # TOP_P: Alternative to temperature (nucleus sampling)
    # 0.1 = very focused, 1.0 = consider all options
    top_p=1.0,
    
    # FREQUENCY_PENALTY: Reduce repetition of tokens
    # 0.0 = no penalty, 2.0 = strong penalty
    frequency_penalty=0.0,
    
    # PRESENCE_PENALTY: Encourage new topics
    presence_penalty=0.0,
    
    # STOP: Stop generating at these sequences
    stop=["\n\n", "END"],
)
```

### Streaming Responses (Like ChatGPT)

```python
# Streaming — get tokens as they're generated
stream = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Explain machine learning in 3 sentences."}
    ],
    stream=True  # Enable streaming
)

full_response = ""
for chunk in stream:
    delta = chunk.choices[0].delta
    if delta.content:
        print(delta.content, end="", flush=True)
        full_response += delta.content

print(f"\n\nFull response: {full_response}")
```

---

## 3. Prompt Engineering

### System Prompts (Setting AI Behavior)

```python
# System prompt defines the AI's personality and rules
messages = [
    {
        "role": "system",
        "content": """You are an expert AI engineer assistant.
        
Rules:
- Answer concisely and technically
- Include code examples when relevant
- If unsure, say "I'm not sure" instead of guessing
- Format responses in markdown
- Always consider production best practices"""
    },
    {
        "role": "user",
        "content": "How do I implement RAG?"
    }
]
```

### Prompt Templates (Critical Skill)

```python
# Template for RAG
RAG_PROMPT = """Answer the question based ONLY on the following context.
If the context doesn't contain the answer, say "I don't have enough information."

Context:
{context}

Question: {question}

Answer:"""

# Template for summarization
SUMMARY_PROMPT = """Summarize the following document in {num_sentences} sentences.
Focus on key points and actionable insights.

Document:
{document}

Summary:"""

# Template for classification
CLASSIFY_PROMPT = """Classify the following text into one of these categories:
{categories}

Text: {text}

Category:"""

# Using templates
def ask_with_context(question: str, context: str) -> str:
    prompt = RAG_PROMPT.format(context=context, question=question)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0  # Deterministic for factual Q&A
    )
    
    return response.choices[0].message.content
```

### Few-Shot Prompting

```python
# Give examples to guide the model
FEW_SHOT_PROMPT = """Extract entities from the text.

Example 1:
Text: "Apple released the iPhone 15 in Cupertino"
Entities: {"company": "Apple", "product": "iPhone 15", "location": "Cupertino"}

Example 2:
Text: "Google announced Gemini at their Mountain View headquarters"
Entities: {"company": "Google", "product": "Gemini", "location": "Mountain View"}

Now extract entities from:
Text: "{text}"
Entities:"""
```

### Chain-of-Thought Prompting

```python
COT_PROMPT = """Solve this step by step.

Question: {question}

Let's think through this step by step:
1."""

# Forces the model to reason through the problem
```

---

## 4. Fine-tuning vs RAG

### When to Use What?

| Aspect | RAG | Fine-tuning |
|--------|-----|------------|
| **Use for** | Adding knowledge | Changing behavior/style |
| **Data needed** | Documents (any amount) | 100-10000 examples |
| **Cost** | Low (just retrieval) | High (training) |
| **Freshness** | Always up-to-date | Static after training |
| **Accuracy** | High (with good retrieval) | High (for specific tasks) |
| **Hallucination** | Low (grounded in docs) | Can still hallucinate |
| **Setup time** | Hours | Days/weeks |
| **Best for** | Q&A, search, docs | Style, format, classification |

### RAG is Your Primary Tool as an AI Engineer

```
User Query → Generate Embedding → Search Vector DB → Get Relevant Docs → Send to LLM → Generate Answer
```

This is what 90% of AI applications do.

---

## 5. Reducing Hallucinations

**Interview Question: How do you reduce hallucination?**

```python
# 1. Use RAG with strict prompt
ANTI_HALLUCINATION_PROMPT = """Answer ONLY based on the provided context.
If the context doesn't contain the answer, respond with: 
"I cannot answer this based on the available information."

Do NOT use any prior knowledge.

Context: {context}
Question: {question}"""

# 2. Set temperature to 0
temperature = 0.0

# 3. Use structured outputs
response = client.chat.completions.create(
    model="gpt-4",
    messages=[...],
    response_format={"type": "json_object"},  # Force JSON output
    temperature=0.0
)

# 4. Implement source citations
CITE_PROMPT = """Answer the question and cite your sources.
Format: [Source: document_name, chunk_id]

Context chunks:
{chunks_with_ids}

Question: {question}

Answer (with citations):"""

# 5. Add confidence scoring
CONFIDENCE_PROMPT = """Rate your confidence in the answer (0-100%).
If confidence < 50%, say you're unsure.

Context: {context}
Question: {question}

Answer:
Confidence:"""
```

---

## 6. LLM Service Class (Production Pattern)

```python
from openai import OpenAI
from dataclasses import dataclass
from typing import Optional, Generator
import logging

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    content: str
    model: str
    tokens_used: int
    prompt_tokens: int
    completion_tokens: int
    cost: float

class LLMService:
    """Production-ready LLM service."""
    
    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def _calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        pricing = self.PRICING.get(model, {"input": 0.01, "output": 0.03})
        return (prompt_tokens * pricing["input"] + completion_tokens * pricing["output"]) / 1000
    
    def generate(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            usage = response.usage
            cost = self._calculate_cost(
                self.model, usage.prompt_tokens, usage.completion_tokens
            )
            
            logger.info(
                f"LLM call: {usage.total_tokens} tokens, ${cost:.4f}"
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                tokens_used=usage.total_tokens,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                cost=cost,
            )
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.7,
    ) -> Generator[str, None, None]:
        """Stream response tokens."""
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
            stream=True,
        )
        
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                yield delta.content
    
    def generate_with_context(
        self,
        question: str,
        context_chunks: list[str],
        temperature: float = 0.0,
    ) -> LLMResponse:
        """RAG-style generation with context."""
        context = "\n\n---\n\n".join(context_chunks)
        
        prompt = f"""Answer based ONLY on the following context.
If the context doesn't contain the answer, say "I don't have enough information."

Context:
{context}

Question: {question}

Answer:"""
        
        return self.generate(
            prompt=prompt,
            system_prompt="You are a precise Q&A assistant. Only use provided context.",
            temperature=temperature,
        )
```

---

## Exercises

### Exercise 1: Build a Prompt Manager
```python
# Create a class that:
# 1. Stores prompt templates
# 2. Validates required variables
# 3. Renders prompts with variables
# 4. Tracks prompt version history
# 5. Supports few-shot examples

# TODO: Implement
```

### Exercise 2: Build a Cost Tracker
```python
# Create a class that:
# 1. Tracks all LLM API calls
# 2. Calculates cost per call
# 3. Provides daily/monthly summaries
# 4. Alerts when budget exceeded
# 5. Exports usage reports

# TODO: Implement
```

---

## Key Takeaways
1. **Tokens** ≈ 4 characters; know context window limits
2. **Temperature 0** for factual, **0.7** for creative
3. **RAG > Fine-tuning** for most use cases
4. **Prompt engineering** is a critical skill — practice templates
5. Always handle **streaming** for good UX
6. Track **costs** — LLM calls are expensive
7. Use **structured prompts** to reduce hallucination
