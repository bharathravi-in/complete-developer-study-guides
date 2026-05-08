# Day 13: Transfer Learning & Fine-Tuning (HuggingFace)

## Learning Objectives
- Use HuggingFace Transformers for NLP tasks
- Understand tokenizers (BPE, WordPiece, SentencePiece)
- Fine-tune pre-trained models for classification, NER, QA
- Choose between fine-tuning and feature extraction

---

## 1. HuggingFace Ecosystem

```python
# Install: pip install transformers datasets evaluate accelerate

from transformers import (
    AutoModel, AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer, pipeline
)
from datasets import load_dataset

# Quick inference with pipelines
classifier = pipeline("sentiment-analysis")
result = classifier("I love this product! It's amazing.")
print(result)  # [{'label': 'POSITIVE', 'score': 0.9998}]

# Named Entity Recognition
ner = pipeline("ner", aggregation_strategy="simple")
print(ner("Apple is looking at buying U.K. startup for $1 billion"))

# Question Answering
qa = pipeline("question-answering")
result = qa(question="What is the capital of France?",
            context="France is a country in Europe. Its capital is Paris.")
print(result)  # {'answer': 'Paris', 'score': 0.99, ...}

# Text Generation
generator = pipeline("text-generation", model="gpt2")
print(generator("The future of AI is", max_length=50))
```

---

## 2. Tokenizers

```python
from transformers import AutoTokenizer

# BERT tokenizer (WordPiece)
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

text = "I love machine learning and natural language processing!"
tokens = tokenizer.tokenize(text)
print(f"Tokens: {tokens}")
# ['i', 'love', 'machine', 'learning', 'and', 'natural', 'language', 'processing', '!']

# Full encoding
encoding = tokenizer(
    text,
    padding='max_length',
    truncation=True,
    max_length=128,
    return_tensors='pt',
)
print(f"input_ids shape: {encoding['input_ids'].shape}")
print(f"attention_mask shape: {encoding['attention_mask'].shape}")
# input_ids: [101, 1045, 2293, 3698, 4083, ..., 102, 0, 0, ...]
# 101 = [CLS], 102 = [SEP], 0 = [PAD]

# GPT-2 tokenizer (BPE - Byte Pair Encoding)
gpt_tokenizer = AutoTokenizer.from_pretrained("gpt2")
gpt_tokens = gpt_tokenizer.tokenize("unhappiness")
print(gpt_tokens)  # ['un', 'h', 'app', 'iness'] — subword units

# Tokenizer types:
# | Type        | Model      | How It Works                        |
# |-------------|------------|-------------------------------------|
# | WordPiece   | BERT       | Greedy longest-match from vocab     |
# | BPE         | GPT, RoBERTa | Merge frequent byte pairs        |
# | SentencePiece | T5, LLaMA | Language-agnostic, treats as bytes |
# | Unigram     | XLNet      | Probabilistic subword selection    |

# Batch tokenization
texts = ["First sentence.", "Second longer sentence here.", "Third."]
batch_encoding = tokenizer(
    texts,
    padding=True,        # Pad to longest in batch
    truncation=True,     # Truncate if > max_length
    max_length=64,
    return_tensors='pt',
)
```

---

## 3. Fine-Tuning for Classification

```python
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer,
    TrainingArguments, Trainer
)
from datasets import load_dataset
import evaluate
import numpy as np

# Load dataset
dataset = load_dataset("imdb")
print(dataset)  # train: 25000, test: 25000

# Load pre-trained model + tokenizer
model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(
    model_name, num_labels=2
)

# Tokenize dataset
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=256)

tokenized_datasets = dataset.map(tokenize_function, batched=True)
tokenized_datasets = tokenized_datasets.remove_columns(["text"])
tokenized_datasets = tokenized_datasets.rename_column("label", "labels")
tokenized_datasets.set_format("torch")

# Small subset for faster training (optional)
small_train = tokenized_datasets["train"].shuffle(seed=42).select(range(5000))
small_test = tokenized_datasets["test"].shuffle(seed=42).select(range(1000))

# Metrics
metric = evaluate.load("accuracy")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return metric.compute(predictions=predictions, references=labels)

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=64,
    learning_rate=2e-5,
    weight_decay=0.01,
    warmup_ratio=0.1,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="accuracy",
    fp16=True,  # Mixed precision
    report_to="none",
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=small_train,
    eval_dataset=small_test,
    compute_metrics=compute_metrics,
)

# Train!
trainer.train()

# Evaluate
results = trainer.evaluate()
print(f"Test accuracy: {results['eval_accuracy']:.4f}")
```

---

## 4. Fine-Tuning for NER (Named Entity Recognition)

```python
from transformers import AutoModelForTokenClassification, DataCollatorForTokenClassification

# NER labels
label_list = ["O", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
label_to_id = {l: i for i, l in enumerate(label_list)}

# Load NER dataset
dataset = load_dataset("conll2003")

# Model for token classification
model = AutoModelForTokenClassification.from_pretrained(
    "bert-base-uncased", num_labels=len(label_list)
)

# Tokenize and align labels (tricky: subword tokens need label alignment)
def tokenize_and_align_labels(examples):
    tokenized = tokenizer(examples["tokens"], truncation=True, is_split_into_words=True)
    
    labels = []
    for i, label in enumerate(examples["ner_tags"]):
        word_ids = tokenized.word_ids(batch_index=i)
        label_ids = []
        previous_word_idx = None
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100)  # Ignore [CLS], [SEP], [PAD]
            elif word_idx != previous_word_idx:
                label_ids.append(label[word_idx])
            else:
                label_ids.append(-100)  # Ignore subword tokens
            previous_word_idx = word_idx
        labels.append(label_ids)
    
    tokenized["labels"] = labels
    return tokenized

tokenized_dataset = dataset.map(tokenize_and_align_labels, batched=True)

# Data collator (handles dynamic padding)
data_collator = DataCollatorForTokenClassification(tokenizer)

# Train with Trainer (same pattern as classification)
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["validation"],
    data_collator=data_collator,
    compute_metrics=compute_ner_metrics,
)
trainer.train()
```

---

## 5. Fine-Tuning for Question Answering

```python
from transformers import AutoModelForQuestionAnswering

# QA model (extractive: find answer span in context)
model = AutoModelForQuestionAnswering.from_pretrained("distilbert-base-uncased")

# Load SQuAD dataset
dataset = load_dataset("squad")
# Each example: question, context, answer (with start position)

def preprocess_qa(examples):
    """Tokenize question + context, find answer start/end positions."""
    tokenized = tokenizer(
        examples["question"],
        examples["context"],
        truncation="only_second",  # Truncate context, not question
        max_length=384,
        stride=128,               # Sliding window for long contexts
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        padding="max_length",
    )
    
    # Find answer start/end token positions
    # (map character offsets to token positions)
    # ... (complex alignment logic)
    
    return tokenized

# After training, inference:
from transformers import pipeline
qa_pipe = pipeline("question-answering", model=model, tokenizer=tokenizer)
result = qa_pipe(
    question="What is the capital of France?",
    context="Paris is the capital and most populous city of France."
)
print(result)  # {'answer': 'Paris', 'score': 0.98, 'start': 0, 'end': 5}
```

---

## 6. When to Fine-Tune vs Feature Extraction

```python
# FEATURE EXTRACTION: Use pre-trained model as fixed feature extractor
# Only train a classifier on top of frozen representations

from transformers import AutoModel

# Freeze transformer, train only classification head
model = AutoModel.from_pretrained("bert-base-uncased")
for param in model.parameters():
    param.requires_grad = False

class BERTFeatureExtractor(nn.Module):
    def __init__(self, bert_model, num_classes):
        super().__init__()
        self.bert = bert_model
        self.classifier = nn.Sequential(
            nn.Linear(768, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes),
        )
    
    def forward(self, input_ids, attention_mask):
        with torch.no_grad():  # No gradients for BERT
            outputs = self.bert(input_ids, attention_mask)
        
        # Use [CLS] token representation
        cls_output = outputs.last_hidden_state[:, 0, :]
        return self.classifier(cls_output)

# Decision guide:
# | Scenario                     | Approach           | Why                        |
# |------------------------------|--------------------|----------------------------|
# | Small dataset (<1K)          | Feature extraction | Avoid overfitting          |
# | Medium dataset (1K-100K)     | Fine-tune last 2-3 layers | Balance         |
# | Large dataset (>100K)        | Full fine-tuning   | Enough data to learn       |
# | Domain very different        | Full fine-tuning   | Pretrained features differ |
# | Domain similar (news→reviews)| Feature extraction | Pretrained features work   |
# | Limited compute              | Feature extraction | Frozen = less memory/time  |

# Model size selection:
# | Model         | Parameters | Speed    | Quality  | Use When            |
# |---------------|-----------|----------|----------|---------------------|
# | DistilBERT    | 66M       | Fast     | Good     | Production, speed   |
# | BERT-base     | 110M      | Medium   | Better   | Standard tasks      |
# | RoBERTa-large | 355M      | Slow     | Best     | Quality-critical    |
# | DeBERTa-v3    | 300M      | Slow     | SOTA     | Competition/research|
```

---

## 7. Practical Tips

```python
# 1. Learning rate: 2e-5 to 5e-5 for fine-tuning (much lower than training from scratch)
# 2. Epochs: 2-4 usually sufficient (more → overfitting)
# 3. Batch size: 16-32 (limited by GPU memory)
# 4. Warmup: 6-10% of total steps
# 5. Weight decay: 0.01 (AdamW standard)
# 6. Max sequence length: as short as possible (memory/speed)

# Save and load fine-tuned model
trainer.save_model("./my_fine_tuned_model")
# or
model.save_pretrained("./my_fine_tuned_model")
tokenizer.save_pretrained("./my_fine_tuned_model")

# Load later
from transformers import AutoModelForSequenceClassification
model = AutoModelForSequenceClassification.from_pretrained("./my_fine_tuned_model")
tokenizer = AutoTokenizer.from_pretrained("./my_fine_tuned_model")

# Push to HuggingFace Hub
model.push_to_hub("my-username/my-fine-tuned-model")
tokenizer.push_to_hub("my-username/my-fine-tuned-model")
```

---

## Interview Questions

### Beginner
1. **What is transfer learning in NLP?** Pre-train a large model on massive text corpus (unsupervised: predict masked words). Then fine-tune on your specific task (classification, NER) with small labeled dataset. Transfers language understanding to new tasks.
2. **What is a tokenizer and why are subword tokenizers used?** Tokenizer converts text to numerical IDs. Subword tokenizers (BPE, WordPiece): split rare words into known subwords. Handles any word (no OOV), fixed vocabulary size, shares information between related words ("unhappy" → "un" + "happy").
3. **BERT vs GPT: what's the difference?** BERT: bidirectional, masked language model, best for understanding tasks (classification, NER, QA). GPT: autoregressive (left-to-right), best for generation. BERT sees full context; GPT generates one token at a time.

### Intermediate
4. **How does fine-tuning work mechanically?** Start with pre-trained weights. Add task-specific head (linear layer). Train all parameters with very small learning rate (2e-5). Pretrained layers change slightly; head learns from scratch. Early stopping when val metric stops improving.
5. **What is the [CLS] token and how is it used?** BERT prepends [CLS] at position 0. After processing, [CLS] representation aggregates information from all tokens (via self-attention). Used as sentence-level representation for classification. Alternative: mean-pool all token representations.
6. **How do you handle class imbalance when fine-tuning?** Weighted loss (higher weight for rare classes), oversampling rare classes in training, focal loss, stratified batching. For extreme imbalance: few-shot learning with prompt engineering.

### Advanced
7. **LoRA vs full fine-tuning: tradeoffs.** Full fine-tuning: updates all parameters (best quality, most memory). LoRA: adds small trainable matrices (rank decomposition), freezes original weights. 10-100x fewer trainable params, nearly same quality. Use LoRA for: large models on limited GPU, multiple task adapters, quick experiments.
8. **How do you fine-tune a model for a language/domain not in pretraining data?** Continued pretraining: run MLM on domain text (medical, legal, code). Then fine-tune on task. Alternatively: vocabulary expansion (add domain terms to tokenizer). For new language: multilingual model or train tokenizer from scratch + continued pretraining.
9. **Design a production NLP system with multiple tasks.** Shared backbone (one fine-tuned BERT/RoBERTa). Multiple task heads (classification, NER, etc.). Options: multi-task training (shared encoder), or separate fine-tuned models. Serve with ONNX/TensorRT. Monitor per-task performance.

---

## Hands-On Exercise
1. Use HuggingFace pipeline for 3 different tasks (sentiment, NER, QA)
2. Fine-tune DistilBERT on a custom classification dataset
3. Compare learning rates (1e-3 vs 2e-5 vs 1e-6) for fine-tuning
4. Fine-tune for NER with proper label alignment
5. Compare feature extraction vs full fine-tuning (accuracy, speed)
6. Push a fine-tuned model to HuggingFace Hub
