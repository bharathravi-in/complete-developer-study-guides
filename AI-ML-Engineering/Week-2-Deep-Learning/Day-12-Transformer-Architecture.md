# Day 12: Transformer Architecture

## Overview
Transformers revolutionized AI — from NLP to vision to code generation. Understand the architecture that powers GPT, BERT, and modern LLMs.

---

## 1. Why Transformers?

### Limitations of RNNs
- **Sequential processing**: Can't parallelize across timesteps
- **Vanishing gradients**: Struggle with long-range dependencies
- **Fixed context**: Hidden state is a bottleneck

### Transformer Advantages
- **Parallel processing**: All positions computed simultaneously
- **Self-attention**: Direct connections between any two positions
- **Scalable**: More compute → better performance (scaling laws)

---

## 2. Architecture Overview

```
┌─────────────────────────────────────┐
│          TRANSFORMER                 │
│                                      │
│  ┌──────────────┐ ┌──────────────┐  │
│  │   ENCODER    │ │   DECODER    │  │
│  │              │ │              │  │
│  │  Self-Attn   │ │  Masked      │  │
│  │     ↓        │ │  Self-Attn   │  │
│  │  Add & Norm  │ │     ↓        │  │
│  │     ↓        │ │  Add & Norm  │  │
│  │  Feed-Fwd    │ │     ↓        │  │
│  │     ↓        │ │  Cross-Attn  │  │
│  │  Add & Norm  │ │     ↓        │  │
│  │              │ │  Add & Norm  │  │
│  │  (× N layers)│ │     ↓        │  │
│  │              │ │  Feed-Fwd    │  │
│  └──────────────┘ │     ↓        │  │
│                    │  Add & Norm  │  │
│                    │  (× N layers)│  │
│                    └──────────────┘  │
└─────────────────────────────────────┘

Encoder-only: BERT (classification, embeddings)
Decoder-only: GPT (text generation)
Encoder-Decoder: T5 (translation, summarization)
```

---

## 3. Self-Attention Mechanism

### Intuition
For each word, ask: "How much should I attend to every other word?"

```
"The cat sat on the mat because it was tired"
                                    ↑
            "it" attends most to "cat" (resolves the reference)
```

### Scaled Dot-Product Attention

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Q, K, V: (batch, seq_len, d_k)
    Returns: attention output and weights
    """
    d_k = Q.size(-1)
    
    # 1. Compute attention scores
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
    # scores shape: (batch, seq_len, seq_len)
    
    # 2. Apply mask (for causal/padding)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))
    
    # 3. Softmax to get attention weights
    attention_weights = F.softmax(scores, dim=-1)
    
    # 4. Weighted sum of values
    output = torch.matmul(attention_weights, V)
    
    return output, attention_weights
```

### Step-by-Step Example
```python
# Input: 3 tokens, each with embedding dim 4
# "The" = [1,0,1,0], "cat" = [0,1,0,1], "sat" = [1,1,0,0]
X = torch.tensor([[1.,0,1,0], [0,1,0,1], [1,1,0,0]])  # (3, 4)

# Learned projection matrices
d_model = 4
d_k = 3  # typically d_model / num_heads

W_Q = nn.Linear(d_model, d_k, bias=False)
W_K = nn.Linear(d_model, d_k, bias=False)
W_V = nn.Linear(d_model, d_k, bias=False)

# Project to Q, K, V
Q = W_Q(X)  # (3, 3) - Queries: "What am I looking for?"
K = W_K(X)  # (3, 3) - Keys: "What do I contain?"
V = W_V(X)  # (3, 3) - Values: "What info do I provide?"

# Compute attention
output, weights = scaled_dot_product_attention(Q, K, V)
# output: (3, 3) - contextualized representations
# weights: (3, 3) - attention matrix (who attends to whom)
```

---

## 4. Multi-Head Attention

Multiple attention heads capture different relationship types:

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model=512, num_heads=8):
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.W_Q = nn.Linear(d_model, d_model)
        self.W_K = nn.Linear(d_model, d_model)
        self.W_V = nn.Linear(d_model, d_model)
        self.W_O = nn.Linear(d_model, d_model)  # Output projection
    
    def forward(self, Q, K, V, mask=None):
        batch_size = Q.size(0)
        
        # Linear projections and reshape for multi-head
        # (batch, seq, d_model) → (batch, num_heads, seq, d_k)
        Q = self.W_Q(Q).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_K(K).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_V(V).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Scaled dot-product attention for each head
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        attention = F.softmax(scores, dim=-1)
        context = torch.matmul(attention, V)
        
        # Concatenate heads and project
        # (batch, num_heads, seq, d_k) → (batch, seq, d_model)
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        output = self.W_O(context)
        
        return output
```

---

## 5. Positional Encoding

Transformers have no notion of order — we must inject position information:

```python
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)  # Even indices
        pe[:, 1::2] = torch.cos(position * div_term)  # Odd indices
        
        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        # x: (batch, seq_len, d_model)
        return x + self.pe[:, :x.size(1), :]
```

### Alternative: Rotary Position Embeddings (RoPE)
Used in modern LLMs (LLaMA, Mistral) — encodes relative positions through rotation:
```python
# RoPE applies rotation to Q and K based on position
# Advantage: captures RELATIVE position, extrapolates to longer sequences
```

---

## 6. Complete Transformer Block

```python
class TransformerBlock(nn.Module):
    def __init__(self, d_model=512, num_heads=8, d_ff=2048, dropout=0.1):
        super().__init__()
        
        # Multi-head attention
        self.attention = MultiHeadAttention(d_model, num_heads)
        self.norm1 = nn.LayerNorm(d_model)
        
        # Feed-forward network
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),                    # Modern: GELU instead of ReLU
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout),
        )
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        # Self-attention with residual connection + layer norm
        attn_output = self.attention(x, x, x, mask)  # Q=K=V=x (self-attention)
        x = self.norm1(x + self.dropout(attn_output))  # Residual + Norm
        
        # Feed-forward with residual connection + layer norm
        ff_output = self.feed_forward(x)
        x = self.norm2(x + ff_output)  # Residual + Norm
        
        return x


class GPTModel(nn.Module):
    """Decoder-only Transformer (like GPT)"""
    def __init__(self, vocab_size, d_model=512, num_heads=8, num_layers=6, max_len=2048):
        super().__init__()
        
        self.token_embedding = nn.Embedding(vocab_size, d_model)
        self.position_encoding = PositionalEncoding(d_model, max_len)
        
        self.blocks = nn.ModuleList([
            TransformerBlock(d_model, num_heads) for _ in range(num_layers)
        ])
        
        self.norm = nn.LayerNorm(d_model)
        self.output_head = nn.Linear(d_model, vocab_size)  # Predict next token
    
    def forward(self, tokens):
        # tokens: (batch, seq_len)
        seq_len = tokens.size(1)
        
        # Causal mask: prevent attending to future tokens
        mask = torch.tril(torch.ones(seq_len, seq_len)).unsqueeze(0).unsqueeze(0)
        
        # Embed tokens + positions
        x = self.token_embedding(tokens)
        x = self.position_encoding(x)
        
        # Pass through transformer blocks
        for block in self.blocks:
            x = block(x, mask)
        
        x = self.norm(x)
        logits = self.output_head(x)  # (batch, seq_len, vocab_size)
        
        return logits
```

---

## 7. Key Concepts in Modern LLMs

### KV Cache (Inference Optimization)
```python
# During generation, cache Key and Value to avoid recomputation
# Without cache: O(n²) per new token
# With cache: O(n) per new token

class CachedAttention:
    def __init__(self):
        self.k_cache = None
        self.v_cache = None
    
    def forward(self, q, k, v):
        # Append new k, v to cache
        if self.k_cache is not None:
            k = torch.cat([self.k_cache, k], dim=1)
            v = torch.cat([self.v_cache, v], dim=1)
        self.k_cache = k
        self.v_cache = v
        
        # Attention only on new query
        return scaled_dot_product_attention(q, k, v)
```

### Model Scale
| Model | Parameters | Layers | d_model | Heads |
|-------|-----------|--------|---------|-------|
| GPT-2 Small | 117M | 12 | 768 | 12 |
| BERT-Base | 110M | 12 | 768 | 12 |
| GPT-3 | 175B | 96 | 12288 | 96 |
| LLaMA-2 70B | 70B | 80 | 8192 | 64 |

---

## 8. Hands-On: Build a Mini GPT

```python
"""
Train a character-level GPT on Shakespeare text
"""
# Tokenize at character level
text = open('shakespeare.txt').read()
chars = sorted(set(text))
vocab_size = len(chars)
char_to_idx = {c: i for i, c in enumerate(chars)}
idx_to_char = {i: c for i, c in enumerate(chars)}

# Encode/decode
encode = lambda s: [char_to_idx[c] for c in s]
decode = lambda l: ''.join([idx_to_char[i] for i in l])

# Create training data
data = torch.tensor(encode(text))
block_size = 64  # Context length

def get_batch(data, batch_size=32):
    ix = torch.randint(len(data) - block_size, (batch_size,))
    x = torch.stack([data[i:i+block_size] for i in ix])
    y = torch.stack([data[i+1:i+block_size+1] for i in ix])
    return x, y

# Train
model = GPTModel(vocab_size=vocab_size, d_model=128, num_heads=4, num_layers=4, max_len=block_size)
optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)

for step in range(5000):
    x, y = get_batch(data)
    logits = model(x)
    loss = F.cross_entropy(logits.view(-1, vocab_size), y.view(-1))
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    if step % 500 == 0:
        print(f"Step {step}: Loss = {loss.item():.4f}")

# Generate
model.eval()
context = torch.zeros((1, 1), dtype=torch.long)
for _ in range(200):
    logits = model(context[:, -block_size:])
    probs = F.softmax(logits[:, -1, :], dim=-1)
    next_token = torch.multinomial(probs, 1)
    context = torch.cat([context, next_token], dim=1)
print(decode(context[0].tolist()))
```

---

## Key Takeaways
- Self-attention computes relationships between ALL positions in parallel
- Multi-head attention captures diverse relationship types
- Positional encoding injects order information
- Residual connections + Layer Norm enable deep networks
- Causal masking (decoder) prevents seeing future tokens
- KV cache makes autoregressive generation efficient
- The same architecture scales from 100M to 1T+ parameters

## Tomorrow
**Day 13**: Transfer Learning & Fine-Tuning — Using HuggingFace Transformers with pre-trained models.
