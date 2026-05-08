# Day 11: RNNs & Sequence Models

## Learning Objectives
- Understand vanilla RNN and vanishing gradient problem
- Master LSTM and GRU gating mechanisms
- Implement sequence models for time series and NLP
- Know why Transformers replaced RNNs

---

## 1. Vanilla RNN

### Architecture

```
h_t = tanh(W_hh * h_{t-1} + W_xh * x_t + b)
y_t = W_hy * h_t + b_y
```

```python
import torch
import torch.nn as nn

class VanillaRNN(nn.Module):
    """Simple RNN — for understanding, not production."""
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.hidden_size = hidden_size
        self.W_xh = nn.Linear(input_size, hidden_size)
        self.W_hh = nn.Linear(hidden_size, hidden_size, bias=False)
        self.W_hy = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        # x shape: (batch, seq_len, input_size)
        batch_size, seq_len, _ = x.shape
        h = torch.zeros(batch_size, self.hidden_size, device=x.device)
        
        outputs = []
        for t in range(seq_len):
            h = torch.tanh(self.W_xh(x[:, t]) + self.W_hh(h))
            outputs.append(h)
        
        # Use last hidden state for classification
        out = self.W_hy(h)
        return out

# Problem: Vanishing Gradients
# During backpropagation through time (BPTT):
# gradient ∝ W_hh^T (multiplied T times for T timesteps)
# If |eigenvalue(W_hh)| < 1 → gradient → 0 (vanishing)
# If |eigenvalue(W_hh)| > 1 → gradient → ∞ (exploding)
# Result: Can't learn long-range dependencies (>10-20 steps)
```

---

## 2. LSTM (Long Short-Term Memory)

### Gating Mechanism

```
Forget gate:  f_t = σ(W_f * [h_{t-1}, x_t] + b_f)     → What to forget
Input gate:   i_t = σ(W_i * [h_{t-1}, x_t] + b_i)     → What to store
Candidate:    c̃_t = tanh(W_c * [h_{t-1}, x_t] + b_c)  → New candidate values
Cell state:   c_t = f_t ⊙ c_{t-1} + i_t ⊙ c̃_t        → Update cell
Output gate:  o_t = σ(W_o * [h_{t-1}, x_t] + b_o)     → What to output
Hidden state: h_t = o_t ⊙ tanh(c_t)                    → Filtered output
```

```python
# PyTorch LSTM
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,      # (batch, seq, features)
            dropout=dropout,        # Between LSTM layers
            bidirectional=False,
        )
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        # x: (batch, seq_len, input_size)
        lstm_out, (h_n, c_n) = self.lstm(x)
        # lstm_out: (batch, seq_len, hidden_size) — all timesteps
        # h_n: (num_layers, batch, hidden_size) — final hidden state
        
        # Use last timestep's output
        last_output = lstm_out[:, -1, :]  # (batch, hidden_size)
        out = self.dropout(last_output)
        out = self.fc(out)
        return out

# Why LSTM solves vanishing gradient:
# Cell state c_t flows through with only element-wise operations
# Forget gate ≈ 1 → gradient flows unchanged (like skip connection)
# Gates learned to selectively remember/forget
```

---

## 3. GRU (Gated Recurrent Unit)

```python
# GRU: Simplified LSTM (fewer parameters, often similar performance)
# Only 2 gates (vs LSTM's 3) and no separate cell state

# Reset gate: r_t = σ(W_r * [h_{t-1}, x_t])  → How much past to forget
# Update gate: z_t = σ(W_z * [h_{t-1}, x_t])  → How much to update
# Candidate: h̃_t = tanh(W * [r_t ⊙ h_{t-1}, x_t])
# Output: h_t = (1 - z_t) ⊙ h_{t-1} + z_t ⊙ h̃_t

class GRUModel(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super().__init__()
        self.gru = nn.GRU(
            input_size, hidden_size, num_layers,
            batch_first=True, dropout=0.2,
        )
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        gru_out, h_n = self.gru(x)
        out = self.fc(gru_out[:, -1, :])
        return out

# LSTM vs GRU:
# | Aspect      | LSTM           | GRU            |
# |-------------|----------------|----------------|
# | Parameters  | 4× input→hidden| 3× input→hidden|
# | Gates       | 3 (forget, input, output) | 2 (reset, update) |
# | Cell state  | Separate c_t   | Just h_t       |
# | Performance | Better for long sequences | Similar or better for short |
# | Speed       | Slower         | Faster         |
```

---

## 4. Bidirectional RNN

```python
# Bidirectional: Process sequence left→right AND right→left
# Gets context from both directions (useful for NLP)

class BiLSTMClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_size, num_classes):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(
            embed_dim, hidden_size, num_layers=2,
            batch_first=True, bidirectional=True, dropout=0.3,
        )
        # hidden_size * 2 because bidirectional concatenates both directions
        self.fc = nn.Linear(hidden_size * 2, num_classes)
    
    def forward(self, x):
        embedded = self.embedding(x)  # (batch, seq, embed_dim)
        lstm_out, _ = self.lstm(embedded)  # (batch, seq, hidden*2)
        
        # Pool over sequence (mean of all timesteps)
        pooled = lstm_out.mean(dim=1)  # (batch, hidden*2)
        return self.fc(pooled)

# Use case: Text classification, NER, POS tagging
# (any task where you can see the full sequence at once)
# NOT for: autoregressive generation (can't see future tokens)
```

---

## 5. Seq2Seq with Attention

```python
# Seq2Seq: Encoder processes input → Decoder generates output
# Used for: Machine translation, summarization, chatbots

class Attention(nn.Module):
    """Bahdanau (additive) attention."""
    def __init__(self, hidden_size):
        super().__init__()
        self.W = nn.Linear(hidden_size * 2, hidden_size)
        self.v = nn.Linear(hidden_size, 1, bias=False)
    
    def forward(self, decoder_hidden, encoder_outputs):
        # decoder_hidden: (batch, hidden)
        # encoder_outputs: (batch, src_len, hidden)
        src_len = encoder_outputs.size(1)
        
        # Repeat decoder hidden for each source position
        decoder_hidden = decoder_hidden.unsqueeze(1).repeat(1, src_len, 1)
        
        # Score each encoder output
        energy = torch.tanh(self.W(torch.cat([decoder_hidden, encoder_outputs], dim=2)))
        scores = self.v(energy).squeeze(2)  # (batch, src_len)
        
        # Softmax to get attention weights
        weights = torch.softmax(scores, dim=1)  # (batch, src_len)
        
        # Weighted sum of encoder outputs
        context = torch.bmm(weights.unsqueeze(1), encoder_outputs).squeeze(1)
        return context, weights

# This was the precursor to Transformer's self-attention
# Key insight: Instead of compressing entire input into one vector,
# attend to relevant parts of the input at each decoding step
```

---

## 6. Time Series Forecasting with LSTM

```python
import numpy as np
from torch.utils.data import Dataset, DataLoader

class TimeSeriesDataset(Dataset):
    """Create sequences for time series prediction."""
    def __init__(self, data, seq_length, forecast_horizon=1):
        self.data = torch.FloatTensor(data)
        self.seq_length = seq_length
        self.forecast_horizon = forecast_horizon
    
    def __len__(self):
        return len(self.data) - self.seq_length - self.forecast_horizon + 1
    
    def __getitem__(self, idx):
        x = self.data[idx:idx + self.seq_length]
        y = self.data[idx + self.seq_length:idx + self.seq_length + self.forecast_horizon]
        return x, y

class LSTMForecaster(nn.Module):
    def __init__(self, n_features, hidden_size, num_layers, forecast_horizon):
        super().__init__()
        self.lstm = nn.LSTM(n_features, hidden_size, num_layers, 
                           batch_first=True, dropout=0.2)
        self.fc = nn.Linear(hidden_size, forecast_horizon)
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        return self.fc(lstm_out[:, -1, :])  # Predict from last timestep

# Training
seq_length = 30  # Use 30 days to predict
forecast_horizon = 7  # Predict next 7 days

# Normalize data
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data.reshape(-1, 1))

# Create datasets
train_dataset = TimeSeriesDataset(data_scaled[:train_split], seq_length, forecast_horizon)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

model = LSTMForecaster(n_features=1, hidden_size=64, num_layers=2, forecast_horizon=7)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.MSELoss()

for epoch in range(50):
    model.train()
    total_loss = 0
    for x_batch, y_batch in train_loader:
        optimizer.zero_grad()
        pred = model(x_batch.unsqueeze(-1))  # Add feature dim
        loss = criterion(pred, y_batch.squeeze(-1))
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    
    if epoch % 10 == 0:
        print(f"Epoch {epoch}: Loss = {total_loss/len(train_loader):.6f}")
```

---

## 7. Why Transformers Replaced RNNs

```
RNN Limitations:
1. SEQUENTIAL: Must process tokens one by one → can't parallelize
   Transformer: All tokens processed simultaneously → 10-100x faster training

2. LONG-RANGE: Even LSTM struggles beyond ~500 tokens
   Transformer: Self-attention connects any two positions directly

3. MEMORY: Fixed-size hidden state is a bottleneck
   Transformer: Attends to all positions (grows with sequence length)

4. TRAINING: Gradient flow still degraded over very long sequences
   Transformer: Residual connections + attention = stable gradients

RNNs Still Useful For:
- Streaming/online processing (one token at a time)
- Very long sequences where O(n²) attention is too expensive
- Edge devices with limited memory
- Simple sequence tasks where Transformer is overkill

The Evolution:
RNN (1990s) → LSTM (1997) → Seq2Seq+Attention (2014) 
→ Transformer (2017) → BERT/GPT (2018-19) → LLMs (2020+)
```

---

## Interview Questions

### Beginner
1. **What is the vanishing gradient problem in RNNs?** During backpropagation through time, gradients are multiplied by weight matrix at each step. If weights < 1, gradient shrinks exponentially → early timesteps get zero gradient → can't learn long dependencies.
2. **How does LSTM solve vanishing gradients?** Cell state flows through with only element-wise operations (multiply + add). Forget gate near 1 → gradient passes unchanged (like a highway). Gates are differentiable → network learns what to remember/forget.
3. **LSTM vs GRU: when to use which?** GRU: fewer parameters (faster training), works well for short-medium sequences. LSTM: better for very long sequences (separate cell state), default choice for complex tasks. In practice: try both, difference is usually small.

### Intermediate
4. **Explain the attention mechanism in Seq2Seq.** Instead of encoding entire input into one vector, decoder can "look back" at all encoder states. At each decoding step: compute relevance score for each input position → softmax → weighted sum. Solves information bottleneck of fixed-size encoding.
5. **Why is bidirectional LSTM useful for NLP tasks?** Many NLP tasks benefit from both left and right context. "The bank by the river" — meaning of "bank" depends on "river" which comes after. BiLSTM processes both directions and concatenates. NOT usable for generation (no future access).
6. **How do you handle variable-length sequences in batching?** Padding: pad shorter sequences to max length + create attention mask. Pack sequences: `pack_padded_sequence` (skips padding in computation). Sort by length in batch for efficiency. Collate function handles this.

### Advanced
7. **Why did Transformers replace RNNs for most NLP tasks?** Parallelization: all positions computed simultaneously (GPU-friendly). Long-range: direct connection between any two positions (O(1) path length). Scalability: scales to billions of parameters. Pretraining: self-supervised pretraining works better with Transformers.
8. **When might you still use an RNN over a Transformer?** Streaming (process one token at a time without full sequence). Very long sequences where O(n²) attention is prohibitive. Resource-constrained environments. Real-time applications with strict latency. Simple tasks where Transformer is overkill.
9. **Design a sequence model for real-time anomaly detection in IoT sensor data.** LSTM or GRU (streaming-friendly). Input: sliding window of sensor readings. Predict next value → anomaly = large deviation from prediction. Online learning: update model periodically. Edge deployment: quantized GRU. Alert with confidence threshold.

---

## Hands-On Exercise
1. Implement vanilla RNN from scratch, observe vanishing gradients
2. Build LSTM for sentiment classification (IMDB dataset)
3. Compare LSTM vs GRU on same task (accuracy, speed)
4. Implement bidirectional LSTM for text classification
5. Build LSTM time series forecaster for stock/weather data
6. Implement simple attention mechanism on Seq2Seq
