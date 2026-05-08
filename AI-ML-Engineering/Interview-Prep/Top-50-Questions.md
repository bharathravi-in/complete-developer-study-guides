# AI/ML Engineering — Interview Prep

## Top 50 Interview Questions

### ML Fundamentals (Questions 1-15)

**1. Explain the bias-variance trade-off.**
- Bias: Error from wrong assumptions (underfitting). Model too simple.
- Variance: Error from sensitivity to training data (overfitting). Model too complex.
- Goal: Minimize both. Sweet spot = low bias + low variance.
- High bias fix: more features, complex model. High variance fix: more data, regularization.

**2. What is regularization? Compare L1 vs L2.**
- L1 (Lasso): Adds |w| penalty. Drives weights to exactly zero → feature selection.
- L2 (Ridge): Adds w² penalty. Shrinks weights toward zero → all features kept.
- Elastic Net: Combines both. Use when many correlated features.

**3. Explain gradient descent variants.**
- Batch GD: Use ALL training data per step. Stable but slow.
- Stochastic GD (SGD): One sample per step. Fast but noisy.
- Mini-batch GD: Batch of samples (32-256). Best of both.
- Adam: Adaptive learning rates per parameter + momentum. Default choice.

**4. How do you handle class imbalance?**
- Oversampling (SMOTE), undersampling
- Class weights in loss function
- Focal loss (down-weight easy examples)
- Threshold tuning (don't use 0.5)
- Ensemble methods (balanced random forest)
- Metric choice: Use F1/AUC-ROC, not accuracy

**5. Explain precision, recall, F1.**
- Precision: Of predicted positives, how many are correct? TP/(TP+FP)
- Recall: Of actual positives, how many did we find? TP/(TP+FN)
- F1: Harmonic mean = 2·P·R/(P+R). Balances precision and recall.
- Choose metric based on cost: Spam filter → high precision. Cancer detection → high recall.

**6. What is cross-validation and why use it?**
K-Fold: Split data into K parts, train on K-1, validate on 1, rotate. Gives reliable performance estimate. Stratified K-Fold preserves class distribution. TimeSeriesSplit for temporal data.

**7. Explain decision trees and why they overfit.**
Recursive binary splits on features to maximize information gain. Overfit because they can memorize training data (grow until pure leaves). Fix: pruning, max_depth, min_samples_split, or use ensembles.

**8. Random Forest vs XGBoost.**
- Random Forest: Parallel bagging of trees. Each tree trains on bootstrap sample + random feature subset. Reduces variance.
- XGBoost: Sequential boosting. Each tree corrects previous errors. Reduces bias. Usually better performance but needs more tuning.

**9. What is feature engineering?**
Creating new input features from raw data. Examples: log transforms, interaction features, date components, aggregations, embeddings. Often more impactful than model choice. Domain knowledge is key.

**10. Explain the curse of dimensionality.**
As features increase, data becomes sparse in high-dimensional space. Distance metrics become meaningless. Need exponentially more data. Fix: dimensionality reduction (PCA), feature selection, regularization.

**11. What is data leakage?**
When training data contains information not available at prediction time. Examples: future data leaking into features, target-derived features, fitting scaler on all data before split. Causes overoptimistic evaluation.

**12. Explain ensemble methods.**
Combine multiple models for better performance. Bagging (parallel, reduce variance): Random Forest. Boosting (sequential, reduce bias): XGBoost, LightGBM. Stacking: train meta-model on base model predictions.

**13. When would you use unsupervised learning?**
- Customer segmentation (K-means, DBSCAN)
- Anomaly detection (Isolation Forest, Autoencoder)
- Dimensionality reduction for visualization (t-SNE, UMAP)
- Feature learning (autoencoders, word2vec)
- When labels are expensive/unavailable

**14. Explain AUC-ROC curve.**
ROC plots TPR (recall) vs FPR at every threshold. AUC = area under this curve. 0.5 = random, 1.0 = perfect. Threshold-independent metric. Good for comparing models overall.

**15. How do you select features?**
- Filter: Statistical tests (chi-squared, correlation)
- Wrapper: Try subsets, evaluate (forward/backward selection)
- Embedded: Model-based (L1 regularization, tree feature importance)
- Domain knowledge: Engineer meaningful features

---

### Deep Learning (Questions 16-25)

**16. Explain backpropagation.**
Compute loss, then propagate gradients backward through layers using chain rule. Each layer computes ∂Loss/∂weights. Optimizer uses gradients to update weights. Autograd (PyTorch) does this automatically.

**17. What is batch normalization?**
Normalize layer inputs to zero mean, unit variance within each mini-batch. Benefits: faster training, higher learning rates, some regularization. Applied between linear layer and activation.

**18. Explain attention mechanism.**
Compute relevance scores between query and all keys. Weight values by these scores. Allows model to focus on relevant parts of input. Self-attention: Q=K=V=same input. Foundation of Transformers.

**19. What is transfer learning?**
Use pre-trained model (trained on large dataset) as starting point. Fine-tune on your smaller dataset. Works because early layers learn general features. Saves compute and data. Standard for CV and NLP.

**20. Explain vanishing/exploding gradients.**
- Vanishing: Gradients shrink as they propagate backward (deep networks, sigmoid). Layers don't learn.
- Exploding: Gradients grow exponentially. Training diverges.
- Fix: ReLU activation, residual connections, batch norm, gradient clipping, proper initialization.

**21. Compare CNN vs RNN vs Transformer.**
- CNN: Local patterns (convolutions). Best for images. Efficient, parallelizable.
- RNN: Sequential data, hidden state carries context. Sequential processing (slow).
- Transformer: Attention-based. Parallel, handles long-range dependencies. Dominates NLP & increasingly vision.

**22. What is dropout and why does it work?**
Randomly zero out neurons during training (e.g., 20%). Forces network to not rely on any single neuron. Acts as ensemble of sub-networks. Effectively regularizes. Disabled during inference.

**23. Explain learning rate scheduling.**
- Warmup: Start low, ramp up (stabilizes early training)
- Cosine annealing: Gradual decay following cosine curve
- Step decay: Reduce by factor at fixed epochs
- OneCycleLR: Warmup → high → anneal (fast convergence)

**24. What is a residual connection?**
Add input directly to output: y = F(x) + x. Solves vanishing gradients in deep networks. Enables training 100+ layer networks. Core of ResNet, Transformers.

**25. Explain the Transformer architecture.**
- Multi-head self-attention: Relate all positions to each other
- Feed-forward network: Process each position independently
- Residual + Layer Norm: Stable training
- Positional encoding: Inject order information
- Encoder (bidirectional) + Decoder (causal masking)

---

### LLMs & Applied AI (Questions 26-40)

**26. How does GPT generate text?**
Decoder-only Transformer. Next-token prediction (autoregressive). Given context, predict probability distribution over vocabulary. Sample from distribution. Append token. Repeat. Causal masking prevents seeing future.

**27. What is RAG and when to use it?**
Retrieval-Augmented Generation: Retrieve relevant documents from vector store, inject into prompt as context, then generate. Use when LLM needs external/current knowledge. Better than fine-tuning for factual knowledge.

**28. Explain embedding models.**
Convert text to dense vectors where semantic similarity = geometric closeness. Used for: search, clustering, RAG retrieval. Models: text-embedding-3-small (OpenAI), sentence-transformers (open-source).

**29. What is fine-tuning vs prompt engineering?**
- Prompt engineering: Craft input to guide model behavior. Fast, no training. Limited by context window.
- Fine-tuning: Update model weights on custom data. Changes behavior/knowledge. Slower, needs data.
- Fine-tune for: format/style. Prompt for: one-off tasks. RAG for: knowledge.

**30. Explain LoRA.**
Low-Rank Adaptation: Freeze base model, add small trainable matrices (rank decomposition). W_new = W_frozen + B·A. Trains <1% of parameters. Enables fine-tuning 7B models on single GPU.

**31. What is quantization?**
Reduce model precision: fp32 → fp16 → int8 → int4. Reduces memory and increases inference speed. Methods: GPTQ (post-training), QLoRA (quantized training), AWQ. 4-bit = ~4x memory reduction.

**32. How do vector databases work?**
Store embeddings with metadata. Support approximate nearest neighbor (ANN) search. Algorithms: HNSW, IVF, PQ. Tradeoff: speed vs recall. Examples: Pinecone, Qdrant, pgvector, Weaviate.

**33. Explain chunking strategies for RAG.**
- Fixed-size: Split by token count (simple but may break context)
- Semantic: Split by paragraphs/sections (preserves meaning)
- Recursive: Try paragraph → sentence → character
- Document-aware: Use headings, code blocks as boundaries
- Overlap: Include overlapping text between chunks for continuity

**34. What is prompt injection?**
Adversarial input that overrides system instructions. Direct: user says "ignore instructions." Indirect: tool output contains malicious instructions. Defense: input validation, output filtering, sandwich prompts.

**35. Explain model hallucination.**
Model generates plausible-sounding but factually incorrect content. Causes: training data gaps, overconfident prediction. Reduce: RAG (ground in facts), fine-tuning, chain-of-thought, verification agents.

**36. What is RLHF?**
Reinforcement Learning from Human Feedback. Train reward model on human preferences. Use PPO to fine-tune LLM to maximize reward. Makes models helpful, harmless, honest. Core of ChatGPT's alignment.

**37. Compare open-source vs proprietary LLMs.**
- Proprietary (GPT-4, Claude): Best quality, easy API, cost per token, data leaves your infra.
- Open-source (Llama, Mistral): Self-host, full control, customizable, no per-token cost, but need infra.
- Use proprietary for prototyping, open-source for production at scale / data-sensitive workloads.

**38. How to evaluate LLM outputs?**
- Automated: BLEU, ROUGE (for summarization), perplexity
- LLM-as-judge: Use GPT-4 to rate outputs (cost-effective)
- Human evaluation: Gold standard but expensive
- Task-specific: Accuracy for classification, pass@k for code
- Benchmark suites: MMLU, HumanEval, MT-Bench

**39. Explain model serving for LLMs.**
- vLLM: PagedAttention, continuous batching, high throughput
- TGI: HuggingFace's solution, streaming, multi-GPU
- TensorRT-LLM: NVIDIA optimized, lowest latency
- Key: KV-cache management, batching, quantization, GPU memory planning

**40. What is an AI agent vs a chain?**
- Chain: Fixed sequence of steps. Deterministic flow.
- Agent: LLM decides what to do next dynamically. Can use tools, loop, branch.
- Agent advantages: Handles novel situations, adapts strategy.
- Agent risks: Unpredictable, can loop, higher latency/cost.

---

### MLOps & System Design (Questions 41-50)

**41. Explain ML system design process.**
1. Clarify requirements (latency, scale, accuracy)
2. Define ML task (classification? ranking?)
3. Data pipeline design
4. Feature engineering
5. Model selection & training
6. Serving architecture
7. Monitoring & feedback loop

**42. What is concept drift?**
Model performance degrades because the relationship between inputs and outputs changes over time. Types: sudden (event), gradual (trends), seasonal. Detect with monitoring. Fix with retraining.

**43. How to A/B test an ML model?**
- Random traffic split (5-10% to new model)
- Define success metric (conversion, engagement)
- Run until statistical significance
- Monitor guardrail metrics (latency, errors)
- Progressive rollout: 5% → 25% → 50% → 100%

**44. Design a recommendation system.**
- Candidate generation: Collaborative filtering, content-based, embeddings
- Ranking: Neural network scoring (features: user, item, context)
- Serving: Pre-compute candidates (batch), rank in real-time
- Feedback: Log impressions + clicks → retrain

**45. Explain feature stores.**
Centralized repository for ML features. Serves both batch (training) and real-time (inference). Ensures training-serving consistency (no skew). Point-in-time correct for training. Examples: Feast, Tecton.

**46. How to handle model versioning?**
- MLflow Model Registry: Stage transitions (dev → staging → production)
- DVC for data versioning alongside code (git)
- Docker images with pinned model versions
- Feature flags for model switching
- Rollback capability always available

**47. Explain training-serving skew.**
Mismatch between how features are computed during training vs serving. Causes: different code paths, timing differences, data freshness. Fix: feature stores, shared transformation code, monitoring.

**48. Design a fraud detection system.**
- Real-time scoring (< 100ms): Feature store → lightweight model (gradient boosting)
- Batch analysis: Deep learning on historical patterns
- Rules engine: Known fraud patterns
- Human review queue for uncertain cases
- Feedback loop: analyst labels → retrain

**49. What is model explainability?**
Understanding WHY a model made a prediction. Methods: SHAP values, LIME, feature importance, attention visualization. Required for: regulated industries, debugging, building trust. Trade-off with model complexity.

**50. How do you scale ML inference?**
- Horizontal: Multiple model replicas behind load balancer
- Batching: Group requests, process together (GPU efficient)
- Caching: Store predictions for common inputs
- Quantization: Reduce model size for faster inference
- Model distillation: Train smaller model to mimic large one
- Auto-scaling: Scale replicas based on queue depth/latency
