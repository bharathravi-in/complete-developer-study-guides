# AI/ML Engineering Cheatsheet

## Scikit-learn Quick Reference

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, roc_auc_score

# Pipeline
pipe = Pipeline([
    ('preprocessor', ColumnTransformer([
        ('num', StandardScaler(), numeric_cols),
        ('cat', OneHotEncoder(handle_unknown='ignore'), cat_cols)
    ])),
    ('model', XGBClassifier())
])

# Train & Evaluate
pipe.fit(X_train, y_train)
scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring='f1')
print(classification_report(y_test, pipe.predict(X_test)))
```

## PyTorch Quick Reference

```python
# Model
class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(in, h), nn.ReLU(), nn.Linear(h, out))
    def forward(self, x): return self.layers(x)

# Training loop
model.train()
for X, y in loader:
    X, y = X.to(device), y.to(device)
    loss = criterion(model(X), y)
    optimizer.zero_grad(); loss.backward(); optimizer.step()

# Evaluation
model.eval()
with torch.no_grad():
    preds = model(X_test.to(device))
```

## HuggingFace Quick Reference

```python
from transformers import AutoModel, AutoTokenizer, pipeline

# Quick inference
pipe = pipeline("text-generation", model="mistralai/Mistral-7B-Instruct-v0.2")
result = pipe("Hello, how are you?", max_new_tokens=100)

# Fine-tuning with PEFT
from peft import LoraConfig, get_peft_model
lora_config = LoraConfig(r=16, lora_alpha=32, target_modules=["q_proj", "v_proj"])
model = get_peft_model(base_model, lora_config)
```

## LLM API Quick Reference

```python
# OpenAI
from openai import OpenAI
client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4", messages=[{"role": "user", "content": "Hello"}]
)

# With tools
response = client.chat.completions.create(
    model="gpt-4", messages=messages, tools=tools, tool_choice="auto"
)

# Embeddings
embeddings = client.embeddings.create(model="text-embedding-3-small", input=["text"])
vector = embeddings.data[0].embedding  # list of floats
```

## Key Metrics

| Task | Metrics | When |
|------|---------|------|
| Binary Classification | Precision, Recall, F1, AUC-ROC | Default |
| Multi-class | Macro/Micro F1, Confusion Matrix | Multiple classes |
| Regression | MSE, MAE, R², MAPE | Continuous output |
| Ranking | MRR, NDCG, MAP | Search, recommendations |
| Generation | BLEU, ROUGE, Perplexity | NLP generation |
| LLM | LLM-as-judge, Human eval | Open-ended |

## Model Selection Guide

```
Start here:
├── Tabular data?
│   ├── Small (<10K rows): LogisticRegression, RandomForest
│   ├── Medium: XGBoost/LightGBM (almost always wins)
│   └── Large: XGBoost with GPU, or neural network
├── Text data?
│   ├── Classification: Fine-tune BERT/DistilBERT
│   ├── Generation: GPT/Llama + prompt engineering or fine-tune
│   └── Embeddings: sentence-transformers
├── Image data?
│   ├── Classification: ResNet/EfficientNet (transfer learning)
│   └── Generation: Diffusion models
└── Time series?
    ├── Classical: Prophet, ARIMA
    └── Deep: Temporal Fusion Transformer, N-BEATS
```

## RAG Architecture

```
Query → Embedding → Vector Search → Top-K Documents
                                         ↓
                    Query + Documents → LLM → Answer

Key decisions:
- Chunk size: 256-512 tokens (experiment!)
- Overlap: 50-100 tokens
- Embedding: text-embedding-3-small (cheap) or large (better)
- Top-K: 3-5 documents usually sufficient
- Re-ranking: Cohere rerank or cross-encoder for better precision
```

## MLOps Checklist
- [ ] Experiment tracking (MLflow/W&B)
- [ ] Data versioning (DVC)
- [ ] Reproducible environment (Docker + pinned deps)
- [ ] Model registry (staging → production)
- [ ] Automated evaluation pipeline
- [ ] Monitoring (drift detection, performance)
- [ ] Rollback capability
- [ ] A/B testing framework
