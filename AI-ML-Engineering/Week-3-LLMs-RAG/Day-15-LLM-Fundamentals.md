# Day 15: LLM Fundamentals

## Learning Objectives
- Understand how LLMs work (autoregressive next-token prediction)
- Compare architectures: decoder-only, encoder, encoder-decoder
- Know scaling laws and their implications
- Navigate the landscape of open vs closed models

---

## 1. How LLMs Work

### Next Token Prediction

```
Input:  "The cat sat on the ___"
Model:  P(next_token | "The cat sat on the")
Output: "mat" (p=0.15), "floor" (p=0.12), "couch" (p=0.08), ...

Training objective: Maximize P(x_t | x_1, ..., x_{t-1}) over all positions
Loss = -Σ log P(x_t | x_{1:t-1})  (cross-entropy)
```

```python
# Simplified autoregressive generation
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "gpt2"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

def generate_text(prompt, max_new_tokens=50, temperature=0.7):
    input_ids = tokenizer.encode(prompt, return_tensors='pt')
    
    for _ in range(max_new_tokens):
        with torch.no_grad():
            outputs = model(input_ids)
            next_token_logits = outputs.logits[:, -1, :]  # Last position
        
        # Temperature scaling (higher = more random)
        next_token_logits = next_token_logits / temperature
        probs = torch.softmax(next_token_logits, dim=-1)
        
        # Sample from distribution
        next_token = torch.multinomial(probs, num_samples=1)
        input_ids = torch.cat([input_ids, next_token], dim=-1)
        
        if next_token.item() == tokenizer.eos_token_id:
            break
    
    return tokenizer.decode(input_ids[0], skip_special_tokens=True)

# Decoding strategies:
# Greedy: always pick highest probability token (deterministic but repetitive)
# Top-k: sample from top-k tokens only
# Top-p (nucleus): sample from smallest set with cumulative prob >= p
# Temperature: scale logits before softmax (T<1: sharper, T>1: flatter)
```

---

## 2. Key Architectures

### Decoder-Only (GPT family)

```
Input: [tokens] → Generate next token → Append → Repeat

Architecture:
- Stack of Transformer decoder blocks
- Causal (masked) self-attention: each token only attends to previous tokens
- Used for: text generation, completion, chat

Models: GPT-4, Claude, Llama, Mistral, Gemini

Why dominant: Pre-training objective (next token) is simple and scales well
```

### Encoder-Only (BERT family)

```
Input: [CLS] The cat [MASK] on the mat [SEP]
Output: Predict [MASK] = "sat" (bidirectional context)

Architecture:
- Stack of Transformer encoder blocks
- Full self-attention: each token attends to ALL tokens (bidirectional)
- Used for: classification, NER, embeddings, understanding tasks

Models: BERT, RoBERTa, DeBERTa
```

### Encoder-Decoder (T5 family)

```
Input (encoder): "translate English to French: The cat is on the mat"
Output (decoder): "Le chat est sur le tapis"

Architecture:
- Encoder: bidirectional attention on input
- Decoder: causal attention + cross-attention to encoder
- Used for: translation, summarization, seq2seq tasks

Models: T5, BART, Flan-T5
```

### Comparison

| Aspect | Decoder-only | Encoder-only | Encoder-Decoder |
|--------|-------------|-------------|-----------------|
| Attention | Causal (left only) | Bidirectional | Both |
| Training | Next token | Masked LM | Denoising |
| Generation | ✅ Natural | ❌ Not designed for | ✅ Good |
| Understanding | Good | Best | Good |
| Examples | GPT-4, Llama | BERT, RoBERTa | T5, BART |

---

## 3. Scaling Laws

```python
# Chinchilla Scaling Laws (DeepMind, 2022):
# For compute-optimal training:
# Tokens ≈ 20 × Parameters
# 
# Example: 7B parameter model → optimal: 140B tokens
# Example: 70B parameter model → optimal: 1.4T tokens

# | Model     | Parameters | Training Tokens | Compute (FLOPs) |
# |-----------|-----------|-----------------|-----------------|
# | GPT-3     | 175B      | 300B            | 3.14×10²³       |
# | Chinchilla| 70B       | 1.4T            | 5.76×10²³       |
# | Llama 2   | 7-70B     | 2T              | -               |
# | Llama 3   | 8-70B     | 15T+            | -               |
# | GPT-4     | ~1.7T (rumored) | Unknown   | -               |

# Key insights:
# 1. Performance ∝ compute (smooth, predictable)
# 2. Can trade off parameters vs data (smaller model + more data can match)
# 3. Emergent abilities: some capabilities appear suddenly at scale
# 4. No sign of plateau yet (as of 2024)

# Practical implications:
# - For inference budget: smaller well-trained model > larger undertrained model
# - Llama 3 8B trained on 15T tokens → rivals older 70B models
# - Quality of data > quantity (filtering matters enormously)
```

---

## 4. Context Windows

```python
# Context window = maximum tokens the model can process at once
# History:
# GPT-3: 2K → GPT-3.5: 4K/16K → GPT-4: 8K/32K/128K
# Claude: 100K → 200K
# Llama 2: 4K → Llama 3: 8K → extended to 128K+

# Techniques for extending context:
# 1. RoPE (Rotary Position Embeddings): position info encoded in rotation
# 2. ALiBi (Attention with Linear Biases): add linear bias based on distance
# 3. Ring Attention: distribute long sequences across GPUs
# 4. Sliding Window Attention (Mistral): attend to local window + global tokens

# Practical considerations:
# - Longer context ≠ better retrieval (needle-in-haystack problem)
# - Cost grows quadratically with context (O(n²) attention)
# - "Lost in the middle" — models attend more to start/end
# - RAG often better than stuffing everything into context

# Token estimation:
# English: ~1 token ≈ 4 characters ≈ 0.75 words
# Code: ~1 token ≈ 3 characters (more verbose tokenization)
# 4K tokens ≈ 3,000 words ≈ 6 pages
# 128K tokens ≈ 96,000 words ≈ a novel
```

---

## 5. Model Landscape (2024)

```
CLOSED SOURCE (API only):
├── GPT-4 / GPT-4o (OpenAI): Best overall, multimodal, function calling
├── Claude 3.5 Sonnet (Anthropic): Best for code, long context, safety
├── Gemini 1.5 Pro (Google): 1M context, multimodal
└── Command R+ (Cohere): RAG-optimized, enterprise

OPEN SOURCE:
├── Llama 3.1 (Meta): 8B/70B/405B, strong overall
├── Mistral/Mixtral (Mistral): 7B/8x7B MoE, efficient
├── Qwen 2 (Alibaba): Strong multilingual, code
├── DeepSeek V2 (DeepSeek): MoE, very cost-efficient
└── Phi-3 (Microsoft): Small but capable (3.8B)

CHOOSING A MODEL:
- Budget unlimited, max quality: GPT-4 / Claude 3.5
- Self-hosted, full control: Llama 3.1 70B
- Edge/mobile: Phi-3, Llama 3.1 8B, Mistral 7B
- RAG/search: Command R+, or any model with good instruction following
- Code: Claude 3.5 Sonnet, DeepSeek Coder
- Cost-sensitive: GPT-4o-mini, Mixtral 8x7B, Llama 3.1 8B
```

---

## 6. Open vs Closed Source Tradeoffs

```
CLOSED SOURCE (GPT-4, Claude):
✅ Best performance (most compute, data, RLHF)
✅ No infrastructure to manage
✅ Continuous improvements
✅ Safety alignment
❌ Data privacy (sent to provider)
❌ Vendor lock-in
❌ Cost at scale ($$$)
❌ No customization of weights
❌ Rate limits, downtime

OPEN SOURCE (Llama, Mistral):
✅ Full control over data (on-premise)
✅ Fine-tune for your domain
✅ No per-token cost (just compute)
✅ No vendor dependency
✅ Can inspect/modify weights
❌ Need infrastructure (GPUs)
❌ Smaller/less capable (usually)
❌ Security/safety is your responsibility
❌ Need ML expertise to run well

DECISION FRAMEWORK:
- Prototype/MVP: Closed source (fastest to start)
- Sensitive data (health, finance): Open source (self-hosted)
- High volume (millions of calls): Open source (cost)
- Needs domain expertise: Open source (fine-tune)
- Best quality at any cost: Closed source
```

---

## 7. Using LLMs via API

```python
from openai import OpenAI
import anthropic

# OpenAI API
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain transformers in 3 sentences."},
    ],
    temperature=0.7,
    max_tokens=200,
)
print(response.choices[0].message.content)

# Anthropic API
client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Explain transformers in 3 sentences."}
    ],
)
print(message.content[0].text)

# Local with Ollama
# ollama run llama3.1:8b
import requests
response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama3.1:8b",
    "prompt": "Explain transformers in 3 sentences.",
    "stream": False,
})
print(response.json()["response"])
```

---

## Interview Questions

### Beginner
1. **How does an LLM generate text?** Autoregressive next-token prediction. Given all previous tokens, predicts probability distribution over vocabulary for next token. Samples from distribution (with temperature/top-p). Appends token, repeats until stop condition.
2. **What's the difference between GPT and BERT?** GPT: decoder-only, causal attention (sees only past), trained on next-token prediction, good for generation. BERT: encoder-only, bidirectional attention (sees all), trained on masked token prediction, good for understanding.
3. **What is a context window?** Maximum number of tokens (input + output) the model can process. Includes system prompt, conversation history, and response. Longer context = more information but higher cost (O(n²) attention).

### Intermediate
4. **Explain Chinchilla scaling laws.** For fixed compute budget: optimal to train a smaller model on more data (rather than bigger model on less data). Rule of thumb: tokens ≈ 20× parameters. Led to shift toward smaller, better-trained models (Llama 3 8B on 15T tokens).
5. **Temperature, top-k, top-p: how do they affect generation?** Temperature: scales logits before softmax (T<1: deterministic, T>1: creative). Top-k: only consider k most likely tokens. Top-p: consider smallest set with cumulative probability ≥ p. For factual: T=0. For creative: T=0.7-1.0, top-p=0.9.
6. **When would you choose open-source over closed-source LLM?** Open-source when: sensitive data (compliance/privacy), high volume (cost), need fine-tuning for domain, require full control, no internet dependency. Closed-source when: need best quality, don't have GPU infrastructure, prototyping fast.

### Advanced
7. **How are LLMs trained? Walk through pre-training, SFT, RLHF.** Pre-training: next-token prediction on trillions of tokens (unsupervised). SFT (Supervised Fine-Tuning): train on curated instruction/response pairs. RLHF: train reward model on human preferences, then use PPO to optimize policy. Result: helpful, harmless, honest.
8. **What are the limitations of current LLMs?** Hallucinations (confident fabrication), knowledge cutoff (no recent info), reasoning failures (multi-step logic), context window limits, can't learn/update in real-time, expensive inference, alignment challenges.
9. **Design a strategy for evaluating LLM outputs in production.** Automated metrics: BLEU/ROUGE (similarity), perplexity (fluency). LLM-as-judge (GPT-4 evaluates outputs). Human evaluation (quality, helpfulness, safety). Domain-specific: factual accuracy checks, format compliance. A/B testing for user preference.

---

## Hands-On Exercise
1. Generate text with GPT-2 locally — vary temperature and observe
2. Compare outputs from 3 different models (GPT-4, Claude, Llama) on same prompt
3. Estimate token costs for your use case
4. Run Llama 3.1 8B locally with Ollama, measure latency
5. Experiment with decoding strategies: greedy vs top-p vs beam search
6. Build a simple chat interface using OpenAI API with conversation history
