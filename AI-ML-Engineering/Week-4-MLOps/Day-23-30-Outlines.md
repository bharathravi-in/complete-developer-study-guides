# Week 4: MLOps — Remaining Day Outlines

## Day 23: Model Serving
- Serving architectures (batch vs online vs streaming)
- FastAPI model serving (REST endpoint)
- TorchServe and TFServing (production frameworks)
- Triton Inference Server (GPU optimization, batching)
- Model formats: ONNX, TorchScript, SavedModel
- Latency optimization (quantization, pruning, distillation)
- A/B testing and canary deployments
- Auto-scaling inference endpoints

## Day 24: Experiment Tracking & Feature Stores
- MLflow deep dive (experiments, runs, artifacts, model registry)
- Weights & Biases (dashboards, sweeps, reports)
- Comparison: MLflow vs W&B vs Neptune vs Comet
- Feature stores: Feast, Tecton
- Online vs offline feature serving
- Feature engineering pipelines
- Point-in-time correctness (avoid data leakage)

## Day 25: Data & Model Versioning
- DVC (Data Version Control): track large files, pipelines
- Git + DVC workflow
- Model versioning strategies
- Dataset versioning (Delta, LakeFS, DVC)
- Reproducibility: code + data + environment
- Docker for ML environments
- Artifact management (S3, GCS, MLflow artifacts)

## Day 26: CI/CD for ML
- ML pipeline CI/CD vs traditional software
- Testing ML code: unit tests, data tests, model tests
- GitHub Actions for ML workflows
- Automated retraining triggers (performance drift, schedule)
- Model validation gates (quality checks before deploy)
- Infrastructure as Code for ML (Terraform, Pulumi)
- Continuous training (CT) pipelines

## Day 27: Model Monitoring
- Data drift detection (KL divergence, PSI, Kolmogorov-Smirnov)
- Concept drift (model performance degradation)
- Feature drift monitoring
- Tools: Evidently AI, WhyLabs, NannyML
- Alert configuration and escalation
- Automated retraining pipelines
- Shadow mode deployment

## Day 28: LLM-Specific MLOps
- LLM evaluation (perplexity, human eval, LLM-as-judge)
- Prompt versioning and management
- LLM monitoring (token usage, latency, quality metrics)
- Guardrails and safety in production
- Cost optimization (caching, routing, model selection)
- A/B testing prompts and models
- Tools: LangSmith, Helicone, Portkey

## Day 29: System Design for ML
- Design: ML system for fraud detection
- Design: Recommendation engine at scale
- Design: Real-time content moderation
- Design: Search relevance system
- Framework: Problem → Data → Model → Serving → Monitoring
- Tradeoffs: latency vs accuracy, cost vs performance
- Scaling ML systems (horizontal, model parallel)

## Day 30: Capstone & Interview
- Full ML system implementation
- Code: data pipeline → training → serving → monitoring
- MLflow experiment tracking
- Docker containerized model serving
- Monitoring dashboard
- System design document
- Interview practice: explain your system decisions
