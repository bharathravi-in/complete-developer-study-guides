# Day 14: Project — Custom Model Training

## Learning Objectives
- Build custom PyTorch Dataset and DataLoader
- Design or adapt model architecture for a real task
- Train with proper validation, early stopping, and experiment tracking
- Export model for deployment (ONNX/TorchScript)

---

## 1. Custom Dataset & DataLoader

```python
import torch
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from transformers import AutoTokenizer

class TextClassificationDataset(Dataset):
    """Custom dataset for text classification."""
    
    def __init__(self, texts, labels, tokenizer, max_length=256):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt',
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'label': torch.tensor(label, dtype=torch.long),
        }

# Create datasets
tokenizer = AutoTokenizer.from_pretrained('distilbert-base-uncased')

train_dataset = TextClassificationDataset(
    texts=train_df['text'].values,
    labels=train_df['label'].values,
    tokenizer=tokenizer,
)

val_dataset = TextClassificationDataset(
    texts=val_df['text'].values,
    labels=val_df['label'].values,
    tokenizer=tokenizer,
)

# DataLoaders with optimal settings
train_loader = DataLoader(
    train_dataset,
    batch_size=32,
    shuffle=True,
    num_workers=4,
    pin_memory=True,         # Faster GPU transfer
    drop_last=True,          # Drop incomplete last batch
)

val_loader = DataLoader(
    val_dataset,
    batch_size=64,           # Larger batch for validation (no gradients)
    shuffle=False,
    num_workers=4,
    pin_memory=True,
)
```

---

## 2. Model Architecture

```python
import torch.nn as nn
from transformers import AutoModel

class CustomClassifier(nn.Module):
    """Custom model with pre-trained backbone + classification head."""
    
    def __init__(self, model_name, num_classes, dropout=0.3):
        super().__init__()
        self.backbone = AutoModel.from_pretrained(model_name)
        hidden_size = self.backbone.config.hidden_size
        
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, 512),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(256, num_classes),
        )
        
        # Initialize classifier weights
        for module in self.classifier:
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.zeros_(module.bias)
    
    def forward(self, input_ids, attention_mask):
        outputs = self.backbone(input_ids=input_ids, attention_mask=attention_mask)
        
        # Mean pooling over all tokens (better than [CLS] alone)
        last_hidden = outputs.last_hidden_state  # (batch, seq_len, hidden)
        # Mask padding tokens before averaging
        mask_expanded = attention_mask.unsqueeze(-1).expand(last_hidden.size()).float()
        sum_hidden = torch.sum(last_hidden * mask_expanded, dim=1)
        sum_mask = torch.clamp(mask_expanded.sum(dim=1), min=1e-9)
        mean_pooled = sum_hidden / sum_mask  # (batch, hidden)
        
        logits = self.classifier(mean_pooled)
        return logits

model = CustomClassifier('distilbert-base-uncased', num_classes=5)
model = model.cuda()

# Count parameters
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"Total params: {total_params:,}")
print(f"Trainable params: {trainable_params:,}")
```

---

## 3. Training Loop with Early Stopping

```python
import time
from torch.cuda.amp import autocast, GradScaler

class EarlyStopping:
    """Stop training when validation metric stops improving."""
    
    def __init__(self, patience=5, min_delta=0.001, mode='min'):
        self.patience = patience
        self.min_delta = min_delta
        self.mode = mode
        self.counter = 0
        self.best_score = None
        self.early_stop = False
    
    def __call__(self, score):
        if self.best_score is None:
            self.best_score = score
        elif self._is_improvement(score):
            self.best_score = score
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
    
    def _is_improvement(self, score):
        if self.mode == 'min':
            return score < self.best_score - self.min_delta
        return score > self.best_score + self.min_delta

def train_epoch(model, loader, optimizer, scheduler, scaler, criterion):
    model.train()
    total_loss = 0
    correct = 0
    total = 0
    
    for batch in loader:
        input_ids = batch['input_ids'].cuda()
        attention_mask = batch['attention_mask'].cuda()
        labels = batch['label'].cuda()
        
        optimizer.zero_grad()
        
        with autocast(dtype=torch.float16):
            logits = model(input_ids, attention_mask)
            loss = criterion(logits, labels)
        
        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()
        scheduler.step()
        
        total_loss += loss.item() * labels.size(0)
        correct += (logits.argmax(1) == labels).sum().item()
        total += labels.size(0)
    
    return total_loss / total, correct / total

@torch.no_grad()
def validate(model, loader, criterion):
    model.eval()
    total_loss = 0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []
    
    for batch in loader:
        input_ids = batch['input_ids'].cuda()
        attention_mask = batch['attention_mask'].cuda()
        labels = batch['label'].cuda()
        
        with autocast(dtype=torch.float16):
            logits = model(input_ids, attention_mask)
            loss = criterion(logits, labels)
        
        total_loss += loss.item() * labels.size(0)
        preds = logits.argmax(1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
    
    return total_loss / total, correct / total, all_preds, all_labels

# Training configuration
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5, weight_decay=0.01)

num_epochs = 10
total_steps = len(train_loader) * num_epochs
scheduler = torch.optim.lr_scheduler.OneCycleLR(
    optimizer, max_lr=2e-5, total_steps=total_steps
)
scaler = GradScaler()
early_stopping = EarlyStopping(patience=3, mode='max')

# Main training loop
best_val_acc = 0
for epoch in range(num_epochs):
    start = time.time()
    
    train_loss, train_acc = train_epoch(
        model, train_loader, optimizer, scheduler, scaler, criterion
    )
    val_loss, val_acc, val_preds, val_labels = validate(model, val_loader, criterion)
    
    elapsed = time.time() - start
    print(f"Epoch {epoch+1}/{num_epochs} ({elapsed:.1f}s)")
    print(f"  Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}")
    print(f"  Val Loss:   {val_loss:.4f}, Val Acc:   {val_acc:.4f}")
    
    # Save best model
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), 'best_model.pth')
        print(f"  → Saved best model (acc={val_acc:.4f})")
    
    # Early stopping
    early_stopping(val_acc)
    if early_stopping.early_stop:
        print(f"Early stopping at epoch {epoch+1}")
        break

print(f"\nBest validation accuracy: {best_val_acc:.4f}")
```

---

## 4. Experiment Tracking (MLflow / W&B)

```python
import mlflow
import mlflow.pytorch

# MLflow tracking
mlflow.set_experiment("text-classification")

with mlflow.start_run(run_name="distilbert-v1"):
    # Log parameters
    mlflow.log_params({
        "model": "distilbert-base-uncased",
        "learning_rate": 2e-5,
        "batch_size": 32,
        "max_length": 256,
        "epochs": num_epochs,
        "dropout": 0.3,
    })
    
    for epoch in range(num_epochs):
        train_loss, train_acc = train_epoch(...)
        val_loss, val_acc, _, _ = validate(...)
        
        # Log metrics per epoch
        mlflow.log_metrics({
            "train_loss": train_loss,
            "train_acc": train_acc,
            "val_loss": val_loss,
            "val_acc": val_acc,
        }, step=epoch)
    
    # Log final model
    mlflow.pytorch.log_model(model, "model")
    mlflow.log_metric("best_val_acc", best_val_acc)

# Weights & Biases alternative
import wandb

wandb.init(project="text-classification", name="distilbert-v1")
wandb.config.update({"lr": 2e-5, "batch_size": 32, "model": "distilbert"})

for epoch in range(num_epochs):
    train_loss, train_acc = train_epoch(...)
    val_loss, val_acc, _, _ = validate(...)
    wandb.log({"train_loss": train_loss, "val_loss": val_loss, 
               "train_acc": train_acc, "val_acc": val_acc})

wandb.finish()
```

---

## 5. Error Analysis

```python
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

# Load best model
model.load_state_dict(torch.load('best_model.pth'))
val_loss, val_acc, all_preds, all_labels = validate(model, val_loader, criterion)

# Classification report
print(classification_report(all_labels, all_preds, target_names=class_names))

# Confusion matrix
cm = confusion_matrix(all_labels, all_preds)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=class_names, yticklabels=class_names)
plt.xlabel('Predicted')
plt.ylabel('True')
plt.title('Confusion Matrix')
plt.show()

# Find misclassified examples
errors = []
model.eval()
for batch in val_loader:
    with torch.no_grad():
        logits = model(batch['input_ids'].cuda(), batch['attention_mask'].cuda())
    preds = logits.argmax(1).cpu()
    labels = batch['label']
    
    for i in range(len(labels)):
        if preds[i] != labels[i]:
            text = tokenizer.decode(batch['input_ids'][i], skip_special_tokens=True)
            errors.append({
                'text': text[:200],
                'true': class_names[labels[i]],
                'predicted': class_names[preds[i]],
                'confidence': torch.softmax(logits[i], 0).max().item(),
            })

# Analyze error patterns
error_df = pd.DataFrame(errors)
print(f"\nTotal errors: {len(error_df)}")
print(f"\nMost confused pairs:")
print(error_df.groupby(['true', 'predicted']).size().sort_values(ascending=False).head(10))
print(f"\nHigh-confidence errors (model is wrong but sure):")
print(error_df[error_df['confidence'] > 0.9].head(10))
```

---

## 6. Model Export & Deployment

```python
# Option 1: ONNX (cross-platform, optimized inference)
import torch.onnx

model.eval()
dummy_input = {
    'input_ids': torch.randint(0, 30000, (1, 256)).cuda(),
    'attention_mask': torch.ones(1, 256, dtype=torch.long).cuda(),
}

torch.onnx.export(
    model,
    (dummy_input['input_ids'], dummy_input['attention_mask']),
    'model.onnx',
    input_names=['input_ids', 'attention_mask'],
    output_names=['logits'],
    dynamic_axes={
        'input_ids': {0: 'batch', 1: 'sequence'},
        'attention_mask': {0: 'batch', 1: 'sequence'},
        'logits': {0: 'batch'},
    },
    opset_version=14,
)

# Inference with ONNX Runtime (much faster than PyTorch)
import onnxruntime as ort

session = ort.InferenceSession('model.onnx')
inputs = {
    'input_ids': encoding['input_ids'].numpy(),
    'attention_mask': encoding['attention_mask'].numpy(),
}
logits = session.run(None, inputs)[0]

# Option 2: TorchScript (PyTorch native, mobile-friendly)
scripted = torch.jit.trace(model, (dummy_input['input_ids'], dummy_input['attention_mask']))
scripted.save('model_scripted.pt')

# Load without needing model class definition
loaded = torch.jit.load('model_scripted.pt')
output = loaded(input_ids, attention_mask)

# Option 3: HuggingFace optimum (ONNX + quantization)
# pip install optimum[onnxruntime]
from optimum.onnxruntime import ORTModelForSequenceClassification

ort_model = ORTModelForSequenceClassification.from_pretrained(
    "./my_model", export=True
)
# Automatic optimization + quantization
```

---

## 7. Complete Project Checklist

```markdown
## Project Deliverables Checklist

### Code
- [ ] Custom Dataset class with proper __getitem__
- [ ] DataLoader with num_workers, pin_memory
- [ ] Model architecture (adapted pre-trained or custom)
- [ ] Training loop with mixed precision
- [ ] Validation loop with metrics
- [ ] Early stopping
- [ ] Learning rate scheduler
- [ ] Gradient clipping
- [ ] Model checkpointing (save best)
- [ ] Experiment tracking (MLflow/W&B)

### Analysis
- [ ] EDA and data statistics
- [ ] Training/validation curves
- [ ] Classification report + confusion matrix
- [ ] Error analysis (misclassified examples)
- [ ] Ablation study (what matters most?)

### Production
- [ ] Export to ONNX
- [ ] Benchmark inference speed
- [ ] Document model card (performance, limitations)
- [ ] Simple serving code (FastAPI)

### Documentation
- [ ] README with setup instructions
- [ ] Architecture decisions explained
- [ ] Results summary
- [ ] Known limitations and future work
```

---

## Interview Questions

### Beginner
1. **What is a PyTorch Dataset vs DataLoader?** Dataset: defines how to access individual samples (__getitem__, __len__). DataLoader: batches samples, shuffles, parallelizes loading (num_workers), handles padding. Always build both.
2. **Why use mixed precision training?** Forward pass in fp16: 2x less memory, faster on tensor cores. Gradients and updates in fp32: maintain accuracy. Result: train faster, fit larger batches, same model quality.
3. **What is early stopping?** Monitor validation metric. If no improvement for N epochs (patience), stop training. Prevents overfitting. Save best model checkpoint, not the last one.

### Intermediate
4. **How do you debug a model that's not learning?** 1) Overfit single batch (confirm architecture works). 2) Check data loading (print samples). 3) Check loss function. 4) Reduce learning rate. 5) Check gradient norms. 6) Simplify model. 7) Compare with known baseline.
5. **ONNX vs TorchScript: when to use each?** ONNX: cross-platform (Python, C++, mobile, web), optimized runtimes (TensorRT, ONNX Runtime), best for production. TorchScript: PyTorch ecosystem, dynamic control flow, simpler export. ONNX for speed, TorchScript for flexibility.
6. **How do you track experiments effectively?** Log: all hyperparameters, metrics per epoch, final results, model artifacts, data version, git commit. Compare runs: visualize in dashboard. Reproducibility: seed, config files, environment lock. Tools: MLflow, W&B, Neptune.

### Advanced
7. **Design an experiment pipeline for systematic model improvement.** Baseline → ablation (one change at a time) → hyperparameter sweep → architecture search. Track everything. Statistical significance between runs. Automated: scheduled sweeps, early termination of bad runs (Optuna). Document what worked and what didn't.
8. **How do you reduce inference latency for a deployed model?** Quantization (INT8/INT4), distillation (smaller student), pruning (remove weights), ONNX+TensorRT optimization, batching requests, caching frequent inputs, hardware (GPU inference server), model parallelism for large models.
9. **You have 1 week to build an ML product. Walk me through your approach.** Day 1: Define metrics, get data, quick EDA. Day 2: Baseline model (simple features + logistic regression). Day 3: Better model (pre-trained + fine-tune). Day 4: Evaluation, error analysis, iterate. Day 5: Export, simple API, basic tests. Day 6-7: Deploy, monitor, documentation. Ship the baseline fast, iterate.

---

## Hands-On Exercise
1. Build custom Dataset + DataLoader for a Kaggle dataset
2. Design model architecture (pre-trained backbone + custom head)
3. Train with early stopping, learning rate scheduling, gradient clipping
4. Track experiments with MLflow (log params, metrics, model)
5. Perform error analysis on worst predictions
6. Export to ONNX, benchmark PyTorch vs ONNX Runtime speed
7. Create a model card documenting performance and limitations
