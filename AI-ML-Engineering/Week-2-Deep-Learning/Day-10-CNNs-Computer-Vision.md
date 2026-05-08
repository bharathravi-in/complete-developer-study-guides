# Day 10: CNNs for Computer Vision

## Learning Objectives
- Understand convolution operations (kernel, stride, padding)
- Trace the evolution from LeNet to EfficientNet
- Apply transfer learning with pre-trained models
- Implement data augmentation for robust training

---

## 1. Convolution Operation

```python
import torch
import torch.nn as nn

# Convolution: Slide a kernel (filter) across the image
# Output size: (W - K + 2P) / S + 1
# W=input size, K=kernel size, P=padding, S=stride

# Example: 32x32 input, 3x3 kernel, padding=1, stride=1
# Output: (32 - 3 + 2*1) / 1 + 1 = 32x32 (same size)

conv = nn.Conv2d(
    in_channels=3,       # RGB input
    out_channels=64,     # 64 filters (learn 64 different features)
    kernel_size=3,       # 3x3 filter
    stride=1,            # Move 1 pixel at a time
    padding=1,           # Add 1 pixel border (maintain spatial size)
)

# Input: (batch, channels, height, width)
x = torch.randn(16, 3, 224, 224)  # Batch of 16 RGB 224x224 images
out = conv(x)  # Shape: (16, 64, 224, 224)

# 1x1 convolution: change channels without changing spatial dims
pointwise = nn.Conv2d(64, 128, kernel_size=1)  # (16, 64, H, W) → (16, 128, H, W)

# Depthwise separable convolution (MobileNet, EfficientNet)
# = Depthwise conv (spatial, per-channel) + Pointwise conv (channel mixing)
# Much fewer parameters: 3×3×C + C×C' vs 3×3×C×C'
depthwise = nn.Conv2d(64, 64, kernel_size=3, padding=1, groups=64)  # groups=in_channels
pointwise = nn.Conv2d(64, 128, kernel_size=1)
```

### Pooling Layers

```python
# Max Pooling: Take max value in each window (most common)
pool = nn.MaxPool2d(kernel_size=2, stride=2)  # Halves spatial dims
# (B, C, 224, 224) → (B, C, 112, 112)

# Average Pooling: Take average in each window
avg_pool = nn.AvgPool2d(kernel_size=2, stride=2)

# Global Average Pooling: Average entire feature map to single value
gap = nn.AdaptiveAvgPool2d(1)  # (B, C, H, W) → (B, C, 1, 1)
# Replaces fully connected layers at the end (fewer parameters)
```

---

## 2. Architecture Evolution

```python
# --- LeNet (1998): Pioneer CNN ---
class LeNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 6, 5), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(6, 16, 5), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Linear(16 * 5 * 5, 120), nn.ReLU(),
            nn.Linear(120, 84), nn.ReLU(),
            nn.Linear(84, 10),
        )

# --- VGG (2014): Deep but simple (3x3 convs stacked) ---
# Key insight: Multiple small 3×3 convs = one large 7×7 conv but deeper
# Problem: Very many parameters (138M for VGG-16)

# --- ResNet (2015): Skip connections solve vanishing gradients ---
class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(channels, channels, 3, padding=1),
            nn.BatchNorm2d(channels),
            nn.ReLU(),
            nn.Conv2d(channels, channels, 3, padding=1),
            nn.BatchNorm2d(channels),
        )
    
    def forward(self, x):
        return nn.functional.relu(x + self.block(x))  # Skip connection!
# Key insight: Learn residual F(x) where output = x + F(x)
# If F(x)=0, layer is identity → won't hurt. Can train 100+ layers.

# --- EfficientNet (2019): Scale width, depth, resolution together ---
# Compound scaling: if resources ×2, scale all three proportionally
# EfficientNet-B0 to B7 (increasing size)
# Much better accuracy per FLOP than ResNet/VGG

# Architecture timeline:
# LeNet (1998) → AlexNet (2012) → VGG (2014) → 
# GoogLeNet/Inception (2014) → ResNet (2015) → 
# DenseNet (2017) → EfficientNet (2019) → Vision Transformer (2020)
```

---

## 3. Transfer Learning

```python
import torchvision.models as models
from torchvision import transforms

# Load pre-trained model (trained on ImageNet, 1000 classes)
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)

# Strategy 1: Feature Extraction (freeze all, train only classifier)
for param in model.parameters():
    param.requires_grad = False  # Freeze all layers

# Replace final layer
num_classes = 10
model.fc = nn.Linear(model.fc.in_features, num_classes)
# Only model.fc will be trained

# Strategy 2: Fine-Tuning (unfreeze some layers)
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
# Freeze early layers (generic features: edges, textures)
for name, param in model.named_parameters():
    if 'layer4' not in name and 'fc' not in name:
        param.requires_grad = False

model.fc = nn.Linear(model.fc.in_features, num_classes)

# Strategy 3: Gradual unfreezing (best results)
# Epoch 1-5: Train only fc layer
# Epoch 6-10: Unfreeze layer4 + fc
# Epoch 11-15: Unfreeze layer3 + layer4 + fc
# Use lower learning rate for earlier layers

# Different learning rates per layer group
optimizer = optim.AdamW([
    {'params': model.layer3.parameters(), 'lr': 1e-5},
    {'params': model.layer4.parameters(), 'lr': 1e-4},
    {'params': model.fc.parameters(), 'lr': 1e-3},
])
```

---

## 4. Data Augmentation

```python
from torchvision import transforms
from torchvision.transforms import v2

# Training transforms (heavy augmentation)
train_transform = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
    transforms.RandomHorizontalFlip(p=0.5),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
    transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
    transforms.RandomErasing(p=0.1),  # Cutout
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Validation transforms (no augmentation, just resize + normalize)
val_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Advanced: RandAugment (automated augmentation policy)
train_transform_auto = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandAugment(num_ops=2, magnitude=9),  # 2 random transforms
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Mixup / CutMix (label-level augmentation)
def mixup(x, y, alpha=0.2):
    """Mix two images and their labels."""
    lam = np.random.beta(alpha, alpha)
    idx = torch.randperm(x.size(0))
    mixed_x = lam * x + (1 - lam) * x[idx]
    y_a, y_b = y, y[idx]
    return mixed_x, y_a, y_b, lam
```

---

## 5. Complete Training Pipeline

```python
import torch
from torch.utils.data import DataLoader
from torchvision import datasets
import time

# Dataset
train_dataset = datasets.CIFAR10(root='./data', train=True, transform=train_transform, download=True)
val_dataset = datasets.CIFAR10(root='./data', train=False, transform=val_transform)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True, num_workers=4, pin_memory=True)
val_loader = DataLoader(val_dataset, batch_size=128, shuffle=False, num_workers=4, pin_memory=True)

# Model
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
model.fc = nn.Linear(model.fc.in_features, 10)
model = model.cuda()

# Training setup
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=0.01)
scheduler = optim.lr_scheduler.OneCycleLR(
    optimizer, max_lr=1e-3, total_steps=len(train_loader) * 20
)

# Training loop
best_val_acc = 0
for epoch in range(20):
    model.train()
    train_loss, correct, total = 0, 0, 0
    
    for images, labels in train_loader:
        images, labels = images.cuda(), labels.cuda()
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        scheduler.step()
        
        train_loss += loss.item()
        correct += (outputs.argmax(1) == labels).sum().item()
        total += labels.size(0)
    
    # Validation
    model.eval()
    val_correct, val_total = 0, 0
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.cuda(), labels.cuda()
            outputs = model(images)
            val_correct += (outputs.argmax(1) == labels).sum().item()
            val_total += labels.size(0)
    
    train_acc = correct / total
    val_acc = val_correct / val_total
    print(f"Epoch {epoch+1}: Train Acc={train_acc:.4f}, Val Acc={val_acc:.4f}")
    
    if val_acc > best_val_acc:
        best_val_acc = val_acc
        torch.save(model.state_dict(), 'best_model.pth')
```

---

## 6. Modern Techniques

```python
# Label Smoothing: prevents overconfident predictions
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
# Instead of target [1, 0, 0], use [0.9, 0.05, 0.05]

# Test-Time Augmentation (TTA): augment at inference, average predictions
def predict_with_tta(model, image, n_augments=5):
    model.eval()
    predictions = []
    for _ in range(n_augments):
        augmented = train_transform(image)  # Random augmentation
        with torch.no_grad():
            pred = model(augmented.unsqueeze(0).cuda())
            predictions.append(torch.softmax(pred, dim=1))
    return torch.stack(predictions).mean(0)

# Knowledge Distillation: train small model to mimic large model
# teacher_model: large, accurate
# student_model: small, fast
def distillation_loss(student_logits, teacher_logits, labels, temperature=4.0, alpha=0.7):
    soft_loss = nn.KLDivLoss(reduction='batchmean')(
        torch.log_softmax(student_logits / temperature, dim=1),
        torch.softmax(teacher_logits / temperature, dim=1),
    ) * (temperature ** 2)
    hard_loss = nn.CrossEntropyLoss()(student_logits, labels)
    return alpha * soft_loss + (1 - alpha) * hard_loss
```

---

## Interview Questions

### Beginner
1. **What does a convolution layer do?** Slides a learnable kernel (filter) across the image, computing dot products. Each filter detects a specific feature (edge, texture, etc.). Multiple filters → multiple feature maps. Key parameters: kernel size, stride, padding.
2. **Why use pooling layers?** Reduce spatial dimensions (less computation, more translation invariance). Max pooling: keeps strongest activation. Global average pooling: replaces fully-connected layers (fewer parameters). Modern trend: use strided convolutions instead.
3. **What is transfer learning?** Use a model pre-trained on a large dataset (ImageNet) as starting point. Early layers learn universal features (edges, textures). Fine-tune later layers for your specific task. Works even with small datasets.

### Intermediate
4. **Explain ResNet's skip connections. Why do they work?** Skip connection: output = F(x) + x (input added to output). Gradient flows directly through the skip → no vanishing gradient. If F(x)=0, layer is identity (can't hurt). Enables training 100+ layer networks.
5. **How do you decide between feature extraction and fine-tuning?** Feature extraction: small dataset, similar domain. Fine-tuning: larger dataset or different domain. Gradual unfreezing: best results. If very different from ImageNet (medical, satellite), fine-tune more layers with lower LR.
6. **What data augmentation would you use for medical images?** Rotation, flipping (horizontal + vertical for pathology), elastic deformation, color jitter (stain variation), random crop. NOT: flipping for X-rays (anatomical orientation matters). Consider: mix of spatial and intensity transforms.

### Advanced
7. **Compare CNN vs Vision Transformer (ViT).** CNN: inductive bias (locality, translation equivariance), works with less data, faster for small models. ViT: no inductive bias, needs more data, better with large-scale pretraining, captures global context. Hybrid: CNN early + Transformer later.
8. **How do you deploy a CNN for real-time inference?** Quantization (INT8): 4x smaller, 2-3x faster. Pruning: remove low-weight connections. Knowledge distillation: smaller model. TensorRT/ONNX optimization. Batching for throughput. Hardware: GPU for batch, CPU/edge for single.
9. **Design a visual quality inspection system for manufacturing.** Data: labeled defect images (small dataset → augmentation heavy). Model: ResNet/EfficientNet + transfer learning. Training: high recall (don't miss defects), tune threshold for acceptable FP rate. Deploy: edge device (TensorRT), real-time inference. Monitor: track precision/recall, retrain on new defect types.

---

## Hands-On Exercise
1. Build a CNN from scratch for MNIST (Conv → Pool → Conv → Pool → FC)
2. Compare ResNet18 feature extraction vs fine-tuning on CIFAR-10
3. Implement data augmentation, measure impact on accuracy
4. Train with different learning rate schedules, plot learning curves
5. Apply test-time augmentation, measure improvement
6. Export model to ONNX, run inference without PyTorch
