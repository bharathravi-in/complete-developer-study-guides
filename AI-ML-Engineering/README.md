# AI/ML Engineering — 30-Day Mastery Plan

## Goal
Build a complete AI/ML Engineering skillset: from classical ML fundamentals through deep learning to LLM fine-tuning and MLOps. Transition from API consumer to model builder.

## Prerequisites
- Python intermediate+ (NumPy, Pandas basics)
- Basic linear algebra and statistics
- Familiarity with APIs and Docker

---

## Weekly Breakdown

### Week 1: Machine Learning Fundamentals (Days 1–7)
| Day | Topic | Focus |
|-----|-------|-------|
| 1 | ML Landscape & Workflow | Types of ML, bias-variance, train/val/test, cross-validation |
| 2 | Linear Models | Linear regression, logistic regression, gradient descent, regularization |
| 3 | Tree-Based Models | Decision trees, Random Forest, XGBoost, feature importance |
| 4 | Feature Engineering | Encoding, scaling, imputation, feature selection, feature stores |
| 5 | Model Evaluation | Metrics (precision, recall, F1, AUC-ROC), confusion matrix, threshold tuning |
| 6 | Unsupervised Learning | K-means, DBSCAN, PCA, dimensionality reduction, anomaly detection |
| 7 | Project: End-to-End ML Pipeline | Scikit-learn pipeline with feature engineering, training, evaluation |

### Week 2: Deep Learning & Neural Networks (Days 8–14)
| Day | Topic | Focus |
|-----|-------|-------|
| 8 | Neural Network Foundations | Perceptrons, activation functions, backpropagation, PyTorch basics |
| 9 | Training Deep Networks | Optimizers (Adam, SGD), learning rate scheduling, batch norm, dropout |
| 10 | CNNs for Computer Vision | Convolutions, pooling, transfer learning, ResNet, image classification |
| 11 | RNNs & Sequence Models | LSTM, GRU, seq2seq, time series forecasting |
| 12 | Transformer Architecture | Self-attention, multi-head attention, positional encoding, BERT basics |
| 13 | Transfer Learning & Fine-Tuning | HuggingFace Transformers, pre-trained models, task-specific fine-tuning |
| 14 | Project: Custom Model Training | Train and deploy a PyTorch model on custom data |

### Week 3: LLMs, RAG & Advanced AI (Days 15–21)
| Day | Topic | Focus |
|-----|-------|-------|
| 15 | LLM Fundamentals | GPT architecture, tokenization, context windows, inference optimization |
| 16 | Prompt Engineering | Few-shot, chain-of-thought, structured output, system prompts |
| 17 | Embeddings & Vector Databases | Embedding models, similarity search, pgvector, Pinecone, Qdrant |
| 18 | RAG Architecture | Chunking strategies, retrieval, re-ranking, hybrid search |
| 19 | Fine-Tuning LLMs | LoRA, QLoRA, PEFT, dataset preparation, evaluation |
| 20 | HuggingFace Ecosystem | Transformers, Datasets, Tokenizers, PEFT, model hub |
| 21 | Project: Production RAG System | Build retrieval-augmented generation with evaluation |

### Week 4: MLOps & Production AI (Days 22–30)
| Day | Topic | Focus |
|-----|-------|-------|
| 22 | MLOps Fundamentals | ML lifecycle, experiment tracking, reproducibility |
| 23 | MLflow & Experiment Tracking | Logging, model registry, artifact management |
| 24 | Model Serving | FastAPI, TorchServe, TF Serving, vLLM, quantization |
| 25 | Model Monitoring | Data drift, concept drift, performance degradation, alerting |
| 26 | CI/CD for ML | Training pipelines, model validation, A/B testing, canary deployments |
| 27 | Distributed Training | Data parallelism, DeepSpeed, FSDP, multi-GPU strategies |
| 28 | AI System Design | Design: recommendation system, search engine, fraud detection |
| 29 | Interview Prep | ML system design, coding challenges, paper discussions |
| 30 | Capstone: Production AI Service | End-to-end: train → evaluate → deploy → monitor |

---

## Key Technologies
- **Frameworks**: PyTorch, scikit-learn, HuggingFace Transformers
- **LLMs**: OpenAI API, open-source models (Llama, Mistral)
- **Vector DBs**: pgvector, Qdrant, Pinecone, ChromaDB
- **MLOps**: MLflow, Weights & Biases, DVC
- **Serving**: FastAPI, vLLM, TorchServe
- **Fine-tuning**: LoRA/QLoRA, PEFT, Unsloth
- **Data**: Pandas, Polars, HuggingFace Datasets
- **Infra**: Docker, Kubernetes, GPU instances

## Study Approach
- 2–3 hours/day minimum
- Theory (30%) → Coding (50%) → Projects (20%)
- Build portfolio projects for each week
- Use free GPU: Google Colab, Kaggle Notebooks, Lightning AI
