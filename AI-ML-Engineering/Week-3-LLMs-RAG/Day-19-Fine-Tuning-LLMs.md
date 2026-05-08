# Day 19: Fine-Tuning LLMs — LoRA, QLoRA, PEFT

## Overview
Fine-tune large language models efficiently using parameter-efficient methods. Go from API consumer to model customizer.

---

## 1. Why Fine-Tune?

| Approach | When to Use | Cost |
|----------|-------------|------|
| Prompt Engineering | Simple tasks, quick iteration | $ (API calls) |
| RAG | Need external knowledge | $$ (embedding + retrieval) |
| Fine-Tuning | Need behavior change, custom format, domain expertise | $$$ (compute) |

### Fine-Tuning Use Cases
- Custom output format (JSON schema, specific style)
- Domain specialization (legal, medical, code)
- Instruction following improvement
- Reducing hallucinations on specific topics
- Smaller model that matches larger model on specific task

---

## 2. Full Fine-Tuning vs PEFT

### Full Fine-Tuning
```
Model: 7B parameters → Need 7B × 4 bytes = 28 GB (fp32)
Training: Need ~3× memory for gradients + optimizer states
Total: ~84 GB VRAM for 7B model 😱

Result: New model weights (full copy)
```

### Parameter-Efficient Fine-Tuning (PEFT)
```
Model: 7B parameters (frozen)
Trainable: ~0.1-1% of parameters (adapters)
Memory: 4-8 GB VRAM for 7B model ✅

Result: Small adapter weights (~10-100 MB)
```

---

## 3. LoRA (Low-Rank Adaptation)

### Concept
Instead of updating all weights, decompose the update into low-rank matrices:

$$W_{new} = W_{frozen} + \Delta W = W + BA$$

Where:
- $W$: Original weight matrix (d × k) — frozen
- $B$: Low-rank matrix (d × r) — trainable
- $A$: Low-rank matrix (r × k) — trainable
- $r$: Rank (typically 8-64, much smaller than d or k)

```python
# Original: W has d×k parameters
# LoRA: B has d×r, A has r×k → total r(d+k) parameters
# Example: d=4096, k=4096, r=16
# Original: 16.7M params per layer
# LoRA: 16*(4096+4096) = 131K params per layer (0.8%!)
```

### Implementation
```python
import torch
import torch.nn as nn

class LoRALayer(nn.Module):
    def __init__(self, original_layer, rank=16, alpha=32):
        super().__init__()
        self.original = original_layer
        self.original.weight.requires_grad = False  # Freeze
        
        d_out, d_in = original_layer.weight.shape
        
        # Low-rank matrices
        self.lora_A = nn.Parameter(torch.randn(rank, d_in) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(d_out, rank))
        
        self.scaling = alpha / rank  # Scaling factor
    
    def forward(self, x):
        # Original forward (frozen)
        original_output = self.original(x)
        
        # LoRA forward (trainable)
        lora_output = (x @ self.lora_A.T @ self.lora_B.T) * self.scaling
        
        return original_output + lora_output
```

---

## 4. QLoRA (Quantized LoRA)

Combines 4-bit quantization with LoRA for even more memory savings:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",          # NormalFloat4 quantization
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,      # Quantize the quantization constants
)

# Load model in 4-bit
model = AutoModelForCausalLM.from_pretrained(
    "mistralai/Mistral-7B-v0.1",
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)

# Prepare for training
model = prepare_model_for_kbit_training(model)

# LoRA config
lora_config = LoraConfig(
    r=16,                          # Rank
    lora_alpha=32,                 # Scaling
    target_modules=[               # Which layers to adapt
        "q_proj", "k_proj", "v_proj", "o_proj",  # Attention
        "gate_proj", "up_proj", "down_proj"       # MLP
    ],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

# Apply LoRA
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
# Output: trainable params: 13.6M || all params: 3.75B || trainable%: 0.36%
```

---

## 5. Dataset Preparation

### Instruction Format
```python
from datasets import load_dataset

# Standard instruction format (Alpaca-style)
def format_instruction(example):
    if example.get("input"):
        text = f"""### Instruction:
{example['instruction']}

### Input:
{example['input']}

### Response:
{example['output']}"""
    else:
        text = f"""### Instruction:
{example['instruction']}

### Response:
{example['output']}"""
    return {"text": text}

# ChatML format (for chat models)
def format_chat(example):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": example["question"]},
        {"role": "assistant", "content": example["answer"]}
    ]
    # Apply chat template
    text = tokenizer.apply_chat_template(messages, tokenize=False)
    return {"text": text}

# Load and format dataset
dataset = load_dataset("your_dataset")
dataset = dataset.map(format_instruction)
```

### Custom Dataset Creation
```python
import json

# Create training data (JSONL format)
training_data = [
    {
        "instruction": "Convert this SQL query to a natural language description",
        "input": "SELECT COUNT(*) FROM users WHERE created_at > '2024-01-01'",
        "output": "Count the total number of users who were created after January 1, 2024."
    },
    {
        "instruction": "Write a Python function based on this description",
        "input": "Calculate the factorial of a number recursively",
        "output": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)"
    },
    # Add 100+ examples for good results
]

# Save as JSONL
with open("training_data.jsonl", "w") as f:
    for item in training_data:
        f.write(json.dumps(item) + "\n")
```

---

## 6. Training with HuggingFace TRL

```python
from transformers import TrainingArguments
from trl import SFTTrainer

# Training arguments
training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,      # Effective batch = 4 * 4 = 16
    learning_rate=2e-4,
    weight_decay=0.01,
    warmup_ratio=0.03,
    lr_scheduler_type="cosine",
    logging_steps=10,
    save_strategy="steps",
    save_steps=100,
    evaluation_strategy="steps",
    eval_steps=100,
    bf16=True,                          # Use bfloat16
    optim="paged_adamw_8bit",           # Memory-efficient optimizer
    gradient_checkpointing=True,         # Trade compute for memory
    max_grad_norm=0.3,
    group_by_length=True,               # Batch similar lengths together
    report_to="wandb",                  # Log to Weights & Biases
)

# SFT Trainer
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    tokenizer=tokenizer,
    args=training_args,
    dataset_text_field="text",
    max_seq_length=2048,
    packing=True,                       # Pack multiple examples per sequence
)

# Train!
trainer.train()

# Save adapter weights
trainer.save_model("./final_model")
# Only saves LoRA weights (~50-100 MB, not 14 GB!)
```

---

## 7. Merging & Deployment

```python
from peft import PeftModel

# Load base model + adapter
base_model = AutoModelForCausalLM.from_pretrained("mistralai/Mistral-7B-v0.1")
model = PeftModel.from_pretrained(base_model, "./final_model")

# Merge LoRA weights into base model (for faster inference)
merged_model = model.merge_and_unload()

# Save merged model
merged_model.save_pretrained("./merged_model")
tokenizer.save_pretrained("./merged_model")

# Push to HuggingFace Hub
merged_model.push_to_hub("your-username/your-fine-tuned-model")
tokenizer.push_to_hub("your-username/your-fine-tuned-model")
```

---

## 8. Evaluation

```python
from evaluate import load

# Perplexity
def compute_perplexity(model, tokenizer, texts):
    encodings = tokenizer(texts, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**encodings, labels=encodings["input_ids"])
    return torch.exp(outputs.loss).item()

# Task-specific evaluation
def evaluate_instruction_following(model, tokenizer, test_set):
    results = []
    for example in test_set:
        prompt = format_instruction_prompt(example["instruction"], example.get("input"))
        
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.1)
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        predicted = extract_response(response)
        
        # Compare with expected
        results.append({
            "instruction": example["instruction"],
            "expected": example["output"],
            "predicted": predicted,
            "match": predicted.strip() == example["output"].strip()
        })
    
    accuracy = sum(r["match"] for r in results) / len(results)
    return accuracy, results

# LLM-as-judge evaluation
def llm_judge(predictions, references):
    """Use GPT-4 to evaluate quality"""
    judge_prompt = """Rate the following response on a scale of 1-5:
    Instruction: {instruction}
    Expected: {reference}
    Actual: {prediction}
    
    Score (1-5) and brief explanation:"""
    # Call OpenAI API with judge_prompt
```

---

## 9. Best Practices

### Hyperparameter Guidelines
| Parameter | Recommended | Notes |
|-----------|-------------|-------|
| Rank (r) | 16-64 | Higher = more capacity, more memory |
| Alpha | 2× rank | Scaling factor |
| Target modules | All attention + MLP | More modules = better but slower |
| Learning rate | 1e-4 to 3e-4 | Lower than full fine-tuning |
| Epochs | 1-3 | More = overfitting risk |
| Batch size | 4-8 (with grad accum) | Effective 16-32 |

### Common Mistakes
```python
# ❌ Too few examples (< 50)
# ✅ Minimum 100-500 high-quality examples

# ❌ Training too long (high epochs with small data)
# ✅ 1-3 epochs, monitor val loss

# ❌ Wrong format (model expects ChatML, you give Alpaca)
# ✅ Match the base model's expected format

# ❌ Not evaluating on held-out set
# ✅ Always keep 10-20% for evaluation

# ❌ Fine-tuning for general knowledge (use RAG instead)
# ✅ Fine-tune for behavior/format/style changes
```

---

## 10. When NOT to Fine-Tune

| Scenario | Better Approach |
|----------|----------------|
| Need factual knowledge | RAG (retrieval) |
| Need current information | RAG + web search |
| Simple format changes | Prompt engineering |
| One-off task | Few-shot prompting |
| Need explainability | Prompt + structured output |

---

## Key Takeaways
- LoRA makes fine-tuning accessible (single GPU for 7B models)
- QLoRA (4-bit + LoRA) enables 7B fine-tuning on 8GB VRAM
- Quality of training data > quantity (100 great examples > 10K mediocre ones)
- Fine-tune for behavior/format changes; use RAG for knowledge
- Always evaluate on held-out data and compare to base model
- Merge adapters for production inference speed

## Tomorrow
**Day 20**: HuggingFace Ecosystem — Transformers, Datasets, PEFT, model hub, and building a training workflow.
