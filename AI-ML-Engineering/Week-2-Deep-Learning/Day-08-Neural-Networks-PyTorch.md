# Day 8: Neural Network Foundations & PyTorch

## Overview
Deep learning builds on neural networks — learn the core concepts and PyTorch framework to build models from scratch.

---

## 1. Neural Network Basics

### Perceptron (Single Neuron)
```
Input:  x₁, x₂, x₃
Weights: w₁, w₂, w₃
Bias:    b

Output = activation(w₁·x₁ + w₂·x₂ + w₃·x₃ + b)
       = activation(Σ wᵢxᵢ + b)
       = activation(W·X + b)
```

### Activation Functions
```python
import torch
import torch.nn.functional as F

# ReLU: max(0, x) — most common for hidden layers
relu = F.relu(x)  # Simple, fast, but "dying ReLU" problem

# Sigmoid: 1/(1+e^-x) — output [0,1], good for binary classification
sigmoid = torch.sigmoid(x)

# Tanh: (e^x - e^-x)/(e^x + e^-x) — output [-1,1]
tanh = torch.tanh(x)

# Softmax: e^xi / Σe^xj — multi-class probabilities (sums to 1)
softmax = F.softmax(x, dim=-1)

# GELU: x * Φ(x) — used in Transformers
gelu = F.gelu(x)
```

### Forward Pass
```python
import torch
import torch.nn as nn

class SimpleNet(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.layer1 = nn.Linear(input_dim, hidden_dim)   # W₁x + b₁
        self.layer2 = nn.Linear(hidden_dim, hidden_dim)  # W₂h₁ + b₂
        self.layer3 = nn.Linear(hidden_dim, output_dim)  # W₃h₂ + b₃
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, x):
        x = self.relu(self.layer1(x))      # Layer 1 + activation
        x = self.dropout(x)                 # Regularization
        x = self.relu(self.layer2(x))      # Layer 2 + activation
        x = self.layer3(x)                  # Output layer (no activation for logits)
        return x

model = SimpleNet(input_dim=10, hidden_dim=64, output_dim=2)
print(model)
print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")
```

---

## 2. Backpropagation & Gradient Descent

### Chain Rule
```
Loss = L(ŷ, y)
ŷ = f(W₃ · h₂ + b₃)
h₂ = f(W₂ · h₁ + b₂)
h₁ = f(W₁ · x + b₁)

∂Loss/∂W₁ = ∂Loss/∂ŷ · ∂ŷ/∂h₂ · ∂h₂/∂h₁ · ∂h₁/∂W₁
```

### PyTorch Autograd
```python
# PyTorch tracks operations for automatic differentiation
x = torch.tensor([2.0, 3.0], requires_grad=True)
y = x ** 2 + 3 * x + 1  # y = x² + 3x + 1

loss = y.sum()
loss.backward()  # Compute gradients

print(x.grad)  # dy/dx = 2x + 3 → [7.0, 9.0]
```

---

## 3. Training Loop

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

# Data
X_train_tensor = torch.FloatTensor(X_train)
y_train_tensor = torch.LongTensor(y_train)
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# Model, Loss, Optimizer
model = SimpleNet(input_dim=10, hidden_dim=64, output_dim=2)
criterion = nn.CrossEntropyLoss()  # Classification
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-5)

# Training loop
num_epochs = 50
for epoch in range(num_epochs):
    model.train()  # Enable dropout, batch norm training mode
    total_loss = 0
    correct = 0
    total = 0
    
    for batch_X, batch_y in train_loader:
        # Forward pass
        outputs = model(batch_X)
        loss = criterion(outputs, batch_y)
        
        # Backward pass
        optimizer.zero_grad()   # Clear previous gradients
        loss.backward()         # Compute gradients
        optimizer.step()        # Update weights
        
        # Metrics
        total_loss += loss.item()
        _, predicted = outputs.max(1)
        correct += predicted.eq(batch_y).sum().item()
        total += batch_y.size(0)
    
    # Validation
    model.eval()  # Disable dropout
    with torch.no_grad():  # No gradient computation
        val_outputs = model(X_val_tensor)
        val_loss = criterion(val_outputs, y_val_tensor).item()
        val_acc = (val_outputs.argmax(1) == y_val_tensor).float().mean().item()
    
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1}/{num_epochs}")
        print(f"  Train Loss: {total_loss/len(train_loader):.4f}, Acc: {correct/total:.4f}")
        print(f"  Val Loss: {val_loss:.4f}, Acc: {val_acc:.4f}")
```

---

## 4. Loss Functions

```python
# Binary Classification
criterion = nn.BCEWithLogitsLoss()  # Sigmoid + BCE (numerically stable)

# Multi-class Classification
criterion = nn.CrossEntropyLoss()   # Softmax + NLL (most common)

# Regression
criterion = nn.MSELoss()            # Mean Squared Error
criterion = nn.L1Loss()             # Mean Absolute Error
criterion = nn.SmoothL1Loss()       # Huber loss (robust to outliers)

# Custom loss
class FocalLoss(nn.Module):
    """For imbalanced classification"""
    def __init__(self, alpha=0.25, gamma=2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
    
    def forward(self, inputs, targets):
        bce_loss = F.binary_cross_entropy_with_logits(inputs, targets, reduction='none')
        pt = torch.exp(-bce_loss)
        focal_loss = self.alpha * (1 - pt) ** self.gamma * bce_loss
        return focal_loss.mean()
```

---

## 5. Key PyTorch Patterns

### Device Management (GPU)
```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using: {device}")

model = model.to(device)

for batch_X, batch_y in train_loader:
    batch_X = batch_X.to(device)
    batch_y = batch_y.to(device)
    outputs = model(batch_X)
```

### Save & Load Models
```python
# Save
torch.save({
    'epoch': epoch,
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'loss': loss,
}, 'checkpoint.pth')

# Load
checkpoint = torch.load('checkpoint.pth')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
```

### Custom Dataset
```python
from torch.utils.data import Dataset

class CustomDataset(Dataset):
    def __init__(self, dataframe, target_col, transform=None):
        self.features = dataframe.drop(target_col, axis=1).values
        self.targets = dataframe[target_col].values
        self.transform = transform
    
    def __len__(self):
        return len(self.targets)
    
    def __getitem__(self, idx):
        x = torch.FloatTensor(self.features[idx])
        y = torch.LongTensor([self.targets[idx]])
        if self.transform:
            x = self.transform(x)
        return x, y.squeeze()
```

---

## 6. Regularization Techniques

```python
class RegularizedNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(100, 256),
            nn.BatchNorm1d(256),        # Batch Normalization
            nn.ReLU(),
            nn.Dropout(0.3),            # Dropout (30% neurons zeroed)
            nn.Linear(256, 128),
            nn.BatchNorm1d(128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 10)
        )
    
    def forward(self, x):
        return self.layers(x)

# Weight Decay (L2 regularization) in optimizer
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)

# Early Stopping
best_val_loss = float('inf')
patience = 10
patience_counter = 0

for epoch in range(max_epochs):
    train(model, train_loader)
    val_loss = evaluate(model, val_loader)
    
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        patience_counter = 0
        torch.save(model.state_dict(), 'best_model.pth')
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"Early stopping at epoch {epoch}")
            break
```

---

## 7. Hands-On: Build a Neural Network Classifier

```python
"""
Complete example: Classify handwritten digits (MNIST-like)
"""
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# Data loading with transforms
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.1307,), (0.3081,))
])

train_data = datasets.MNIST('./data', train=True, download=True, transform=transform)
test_data = datasets.MNIST('./data', train=False, transform=transform)

train_loader = DataLoader(train_data, batch_size=64, shuffle=True)
test_loader = DataLoader(test_data, batch_size=1000)

# Model
class DigitClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.network = nn.Sequential(
            nn.Linear(28*28, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 10)
        )
    
    def forward(self, x):
        x = self.flatten(x)
        return self.network(x)

# Train
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = DigitClassifier().to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()

for epoch in range(10):
    model.train()
    for batch_X, batch_y in train_loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)
        
        optimizer.zero_grad()
        output = model(batch_X)
        loss = criterion(output, batch_y)
        loss.backward()
        optimizer.step()
    
    # Test accuracy
    model.eval()
    correct = 0
    with torch.no_grad():
        for X, y in test_loader:
            X, y = X.to(device), y.to(device)
            correct += (model(X).argmax(1) == y).sum().item()
    
    print(f"Epoch {epoch+1}: Test Accuracy = {correct/len(test_data)*100:.2f}%")
```

---

## Key Takeaways
- Neural networks: layers of linear transformations + non-linear activations
- Backprop computes gradients via chain rule; optimizer updates weights
- Training loop: forward → loss → backward → step
- Regularization prevents overfitting: dropout, batch norm, weight decay, early stopping
- PyTorch: define model (`nn.Module`), use autograd, write explicit training loop
- Always move data and model to the same device (CPU/GPU)

## Tomorrow
**Day 9**: Training Deep Networks — Optimizers, learning rate scheduling, gradient clipping, and debugging training.
