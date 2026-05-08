# Week 2: Deep Learning — Remaining Day Outlines

## Day 9: Training Deep Networks
- Optimizers: SGD, SGD+Momentum, Adam, AdamW, LAMB
- Learning rate: warmup, cosine annealing, OneCycleLR, ReduceOnPlateau
- Gradient clipping (prevent exploding gradients)
- Weight initialization (Xavier, He, Kaiming)
- Debugging training (loss not decreasing? overfitting?)
- Mixed precision training (fp16/bf16 for speed)
- Gradient accumulation (larger effective batch on small GPU)

## Day 10: CNNs for Computer Vision
- Convolution operation (kernel, stride, padding)
- Pooling (max, average, global average)
- Architecture evolution: LeNet → VGG → ResNet → EfficientNet
- Transfer learning with pre-trained ImageNet models
- Fine-tuning strategies (freeze layers, gradual unfreezing)
- Data augmentation (torchvision transforms)
- Project: Image classification with transfer learning

## Day 11: RNNs & Sequence Models
- Vanilla RNN (hidden state, vanishing gradients)
- LSTM (forget gate, input gate, output gate, cell state)
- GRU (reset gate, update gate — simpler than LSTM)
- Bidirectional RNNs (context from both directions)
- Seq2Seq with attention (machine translation)
- Time series forecasting with LSTM
- Why Transformers replaced RNNs (parallelization, long-range)

## Day 13: Transfer Learning & Fine-Tuning
- HuggingFace Transformers library
- Pre-trained models: BERT, RoBERTa, DistilBERT, GPT-2
- Tokenizers (WordPiece, BPE, SentencePiece)
- Fine-tuning for classification (add classification head)
- Fine-tuning for NER, QA, summarization
- Trainer API (HuggingFace) for easy training
- When to fine-tune vs feature extraction

## Day 14: Project — Custom Model Training
- Choose a real dataset (Kaggle, HuggingFace Datasets)
- Build custom PyTorch dataset and dataloader
- Design model architecture (or adapt pre-trained)
- Training with proper validation and early stopping
- Experiment tracking with MLflow or W&B
- Model evaluation and error analysis
- Export and deploy (ONNX or TorchScript)
