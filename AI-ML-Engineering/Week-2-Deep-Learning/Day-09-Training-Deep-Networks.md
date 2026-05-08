# Day 9: Training Deep Networks

## Learning Objectives
- Compare optimizers (SGD, Adam, AdamW, LAMB)
- Implement learning rate schedules for stable training
- Apply gradient clipping, weight initialization, and mixed precision
- Debug common training issues

---

## 1. Optimizers

### SGD and Variants

```python
import torch
import torch.nn as nn
import torch.optim as optim

model = nn.Sequential(
    nn.Linear(784, 256),
    nn.ReLU(),
    nn.Linear(256, 128),
    nn.ReLU(),
    nn.Linear(128, 10),
)

# Vanilla SGD: w = w - lr * gradient
optimizer = optim.SGD(model.parameters(), lr=0.01)

# SGD + Momentum: accumulate velocity from past gradients
# v = β*v + gradient; w = w - lr*v
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

# SGD + Momentum + Nesterov: "look-ahead" gradient
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9, nesterov=True)

# SGD + Weight Decay (L2 regularization)
optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.9, weight_decay=1e-4)
```

### Adam & AdamW

```python
# Adam: Adaptive Moment Estimation
# Combines momentum (1st moment) + RMSProp (2nd moment)
# Each parameter gets its own learning rate
optimizer = optim.Adam(model.parameters(), lr=1e-3, betas=(0.9, 0.999), eps=1e-8)

# AdamW: Decoupled Weight Decay
# Adam has a subtle bug: weight decay != L2 regularization in Adam
# AdamW fixes this by decoupling weight decay from the gradient update
optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
# USE AdamW FOR TRANSFORMERS (it's the standard)

# When to use which:
# | Optimizer | Best For                           | Notes                |
# |-----------|------------------------------------|----------------------|
# | SGD+Mom   | CNNs, well-tuned setups            | Often best final acc |
# | Adam      | Quick convergence, small models     | Good default         |
# | AdamW     | Transformers, NLP                   | Standard for LLMs    |
# | LAMB      | Very large batch training           | BERT pre-training    |
```

---

## 2. Learning Rate Schedules

```python
from torch.optim.lr_scheduler import (
    StepLR, CosineAnnealingLR, OneCycleLR, 
    ReduceLROnPlateau, CosineAnnealingWarmRestarts
)

# --- Step decay: reduce every N epochs ---
scheduler = StepLR(optimizer, step_size=30, gamma=0.1)  # lr × 0.1 every 30 epochs

# --- Cosine annealing: smooth decay to 0 ---
scheduler = CosineAnnealingLR(optimizer, T_max=100, eta_min=1e-6)
# lr(t) = eta_min + 0.5*(lr_max - eta_min)*(1 + cos(π*t/T_max))

# --- OneCycleLR: warmup → peak → decay (best for CNNs) ---
scheduler = OneCycleLR(
    optimizer, max_lr=0.01, total_steps=len(train_loader) * num_epochs,
    pct_start=0.3,  # 30% warmup
    anneal_strategy='cos',
)
# Call scheduler.step() AFTER EVERY BATCH (not epoch)

# --- ReduceOnPlateau: reduce when metric stops improving ---
scheduler = ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
# Call: scheduler.step(val_loss) AFTER EVERY EPOCH

# --- Warmup + Cosine (Transformer standard) ---
from transformers import get_cosine_schedule_with_warmup
scheduler = get_cosine_schedule_with_warmup(
    optimizer,
    num_warmup_steps=1000,     # Linear warmup for first 1000 steps
    num_training_steps=50000,  # Then cosine decay
)

# Training loop with scheduler
for epoch in range(num_epochs):
    model.train()
    for batch in train_loader:
        optimizer.zero_grad()
        loss = compute_loss(model, batch)
        loss.backward()
        optimizer.step()
        scheduler.step()  # For OneCycleLR/warmup (per batch)
    
    # For ReduceOnPlateau (per epoch):
    # val_loss = validate(model, val_loader)
    # scheduler.step(val_loss)
```

---

## 3. Weight Initialization

```python
# Why it matters: wrong initialization → vanishing/exploding gradients

def init_weights(module):
    """Initialize weights properly based on layer type."""
    if isinstance(module, nn.Linear):
        # He initialization (for ReLU networks)
        nn.init.kaiming_normal_(module.weight, mode='fan_in', nonlinearity='relu')
        if module.bias is not None:
            nn.init.zeros_(module.bias)
    elif isinstance(module, nn.Conv2d):
        nn.init.kaiming_normal_(module.weight, mode='fan_out', nonlinearity='relu')
    elif isinstance(module, nn.LayerNorm):
        nn.init.ones_(module.weight)
        nn.init.zeros_(module.bias)
    elif isinstance(module, nn.Embedding):
        nn.init.normal_(module.weight, mean=0, std=0.02)

model.apply(init_weights)

# Guidelines:
# | Activation | Initialization | Why |
# |------------|---------------|-----|
# | ReLU       | He/Kaiming    | Accounts for ReLU killing half the values |
# | Sigmoid/Tanh | Xavier/Glorot | Balanced variance for symmetric activations |
# | GELU       | He or small normal | Similar to ReLU |
# | None (linear) | Xavier     | General purpose |

# Xavier: var(w) = 2 / (fan_in + fan_out)
# He:     var(w) = 2 / fan_in
```

---

## 4. Gradient Clipping

```python
# Problem: Gradients can explode (especially in RNNs, Transformers)
# Solution: Clip gradient norm before optimizer.step()

# Method 1: Clip by global norm (standard, used in most papers)
max_norm = 1.0
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm)
# If ||grad|| > max_norm, scale all gradients down proportionally

# Method 2: Clip by value (less common)
torch.nn.utils.clip_grad_value_(model.parameters(), clip_value=1.0)

# Training loop with gradient clipping
for batch in train_loader:
    optimizer.zero_grad()
    loss = compute_loss(model, batch)
    loss.backward()
    
    # Clip AFTER backward, BEFORE step
    grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    
    optimizer.step()
    scheduler.step()
    
    # Monitor gradient norm (useful for debugging)
    if step % 100 == 0:
        print(f"Step {step}, Loss: {loss.item():.4f}, Grad norm: {grad_norm:.4f}")
```

---

## 5. Mixed Precision Training

```python
from torch.cuda.amp import autocast, GradScaler

# Mixed precision: Use fp16/bf16 for forward pass, fp32 for accumulation
# Benefits: 2x memory savings, 2-3x speed on modern GPUs (V100, A100, H100)

scaler = GradScaler()  # Handles loss scaling for fp16

for batch in train_loader:
    optimizer.zero_grad()
    
    # Forward pass in fp16 (faster, less memory)
    with autocast(dtype=torch.float16):
        outputs = model(batch['input_ids'], batch['attention_mask'])
        loss = criterion(outputs, batch['labels'])
    
    # Backward pass (scales loss to prevent fp16 underflow)
    scaler.scale(loss).backward()
    
    # Unscale before clipping
    scaler.unscale_(optimizer)
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    
    # Optimizer step (with scaling)
    scaler.step(optimizer)
    scaler.update()
    scheduler.step()

# bf16 (bfloat16): Same range as fp32, just less precision
# Available on A100+ GPUs, no need for GradScaler
# with autocast(dtype=torch.bfloat16):
#     ...
```

---

## 6. Gradient Accumulation

```python
# Problem: Want large batch size but GPU memory is limited
# Solution: Accumulate gradients over multiple mini-batches

accumulation_steps = 4  # Effective batch = batch_size × accumulation_steps
# If batch_size=8 and accumulation_steps=4, effective batch=32

for step, batch in enumerate(train_loader):
    with autocast(dtype=torch.float16):
        loss = model(batch) / accumulation_steps  # Scale loss
    
    scaler.scale(loss).backward()  # Gradients accumulate
    
    if (step + 1) % accumulation_steps == 0:
        # Only update weights every N steps
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()
        optimizer.zero_grad()  # Reset after update
        scheduler.step()
```

---

## 7. Debugging Training Issues

```python
# LOSS NOT DECREASING:
# 1. Check: learning rate too high? → Reduce by 10x
# 2. Check: gradient norm → If NaN or very large, clip or reduce lr
# 3. Check: data loading correct? → Print batch, visualize
# 4. Check: loss function correct? → Unit test with known examples
# 5. Try: overfit on 1 batch (if can't → bug in model/loss)

# LOSS EXPLODES (NaN):
# 1. Reduce learning rate
# 2. Add gradient clipping
# 3. Check for numerical instability (log(0), div by 0)
# 4. Use mixed precision with GradScaler
# 5. Check data for NaN/Inf values

# OVERFITTING (train acc high, val acc low):
# 1. Add regularization: dropout, weight decay
# 2. Data augmentation
# 3. Early stopping
# 4. Reduce model size
# 5. Get more data

# UNDERFITTING (train acc also low):
# 1. Increase model capacity (deeper/wider)
# 2. Train longer
# 3. Reduce regularization
# 4. Better learning rate schedule
# 5. Better architecture for the task

# DEBUGGING CHECKLIST:
def sanity_check(model, train_loader, criterion):
    """Quick check: can model overfit a single batch?"""
    model.train()
    batch = next(iter(train_loader))
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    for i in range(100):
        optimizer.zero_grad()
        loss = criterion(model(batch['x']), batch['y'])
        loss.backward()
        optimizer.step()
        if i % 20 == 0:
            print(f"Step {i}: loss = {loss.item():.4f}")
    
    # Loss should approach 0 if model can fit the data
    assert loss.item() < 0.1, "Model can't overfit single batch — check architecture/loss"
```

---

## Interview Questions

### Beginner
1. **What is the difference between SGD and Adam?** SGD: one learning rate for all parameters. Adam: adaptive per-parameter learning rate based on first moment (momentum) and second moment (RMSProp). Adam converges faster but SGD often generalizes better.
2. **Why do we need learning rate warmup?** At start, model weights are random → gradients are noisy and large. High LR + noisy gradients = unstable training. Warmup: start with tiny LR, increase gradually, then decay. Especially important for Transformers.
3. **What is gradient clipping?** Limit gradient magnitude before updating weights. If gradient norm > threshold, scale all gradients down. Prevents exploding gradients (loss → NaN). Standard: clip to norm 1.0.

### Intermediate
4. **AdamW vs Adam: what's the difference and why does it matter?** Adam implements weight decay incorrectly (applies to gradient moments). AdamW decouples weight decay from gradient update. Result: better generalization, cleaner regularization. Use AdamW for Transformers.
5. **Explain mixed precision training.** Forward pass in fp16 (half precision): 2x memory savings, faster compute on tensor cores. Backward pass: GradScaler prevents fp16 underflow. Master weights in fp32 for accuracy. Result: 2-3x speedup, same model quality.
6. **How does gradient accumulation work?** Accumulate gradients over N mini-batches before optimizer.step(). Effective batch size = batch_size × N. Scale loss by 1/N to maintain correct gradient magnitude. Enables large-batch training on limited GPU memory.

### Advanced
7. **Your model's loss oscillates wildly. Diagnose and fix.** Check: LR too high (reduce), batch size too small (increase or accumulate), data issues (shuffle, check for corrupted samples), numerical instability (use fp32, add eps), momentum too high. Use loss smoothing to identify trend.
8. **Design a training recipe for a 7B parameter model.** AdamW (lr=3e-4, warmup 2000 steps, cosine decay). bf16 mixed precision. Gradient accumulation (effective batch 2M tokens). Gradient clipping (norm 1.0). FSDP/DeepSpeed for distributed training. Checkpoint every 1000 steps.
9. **When would SGD outperform Adam?** With careful tuning + cosine schedule, SGD often achieves better generalization on CNNs. Adam converges to sharper minima (worse generalization). SGD+momentum + warm restarts for image classification. But Adam is better for: Transformers, NLP, quick prototyping.

---

## Hands-On Exercise
1. Train same model with SGD, Adam, AdamW — compare convergence curves
2. Implement cosine annealing + warmup from scratch
3. Show the effect of gradient clipping on training stability
4. Enable mixed precision, measure speedup and memory savings
5. Implement gradient accumulation to simulate large batch training
6. Debug a broken training loop (intentionally broken code with 3 bugs)
