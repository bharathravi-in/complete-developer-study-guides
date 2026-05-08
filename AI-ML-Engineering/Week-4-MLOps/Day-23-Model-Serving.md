# Day 23: Model Serving

## Learning Objectives
- Compare serving architectures (batch, online, streaming)
- Build FastAPI model serving endpoints
- Use production frameworks (TorchServe, Triton)
- Optimize inference (ONNX, quantization, batching)
- Implement A/B testing and auto-scaling

---

## 1. Serving Architectures

```
Batch Serving:
- Run predictions on large datasets periodically (hourly/daily)
- Use case: recommendation pre-computation, report generation
- Tools: Spark, Airflow + model, batch inference jobs
- Pros: Simple, cost-effective (spot instances), high throughput
- Cons: Stale predictions, not real-time

Online Serving (REST/gRPC):
- Real-time predictions via API (ms-level latency)
- Use case: fraud detection, search ranking, chatbot
- Tools: FastAPI, TorchServe, Triton, SageMaker Endpoints
- Pros: Fresh predictions, user-facing
- Cons: Requires low latency, always-on infrastructure

Streaming Serving:
- Process events from stream (Kafka, Kinesis) with ML
- Use case: real-time anomaly detection, dynamic pricing
- Tools: Flink + model, Kafka Streams + model, Ray Serve
- Pros: Near real-time, handles high throughput events
- Cons: Complex infrastructure, harder to debug
```

---

## 2. FastAPI Model Serving

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import joblib
import time

app = FastAPI(title="ML Model API")

# Load model at startup (not per request!)
model = None

@app.on_event("startup")
def load_model():
    global model
    model = joblib.load("model.pkl")
    print("Model loaded successfully")

class PredictionRequest(BaseModel):
    features: list[float]
    
class PredictionResponse(BaseModel):
    prediction: float
    confidence: float
    latency_ms: float

class BatchRequest(BaseModel):
    instances: list[list[float]]

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    start = time.time()
    
    features = np.array(request.features).reshape(1, -1)
    prediction = model.predict(features)[0]
    confidence = float(model.predict_proba(features).max())
    
    latency = (time.time() - start) * 1000
    return PredictionResponse(
        prediction=float(prediction),
        confidence=confidence,
        latency_ms=round(latency, 2),
    )

@app.post("/predict/batch")
async def predict_batch(request: BatchRequest):
    """Batch prediction for multiple instances."""
    features = np.array(request.instances)
    predictions = model.predict(features).tolist()
    probabilities = model.predict_proba(features).max(axis=1).tolist()
    return {"predictions": predictions, "confidences": probabilities}

@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}

# Run: uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 3. PyTorch Model Serving

```python
import torch
import torch.nn as nn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TextClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_classes):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.fc = nn.Linear(embed_dim, num_classes)
    
    def forward(self, x):
        embedded = self.embedding(x).mean(dim=1)
        return self.fc(embedded)

# Load with TorchScript for production
model = torch.jit.load("model_scripted.pt")
model.eval()

class TextRequest(BaseModel):
    token_ids: list[int]

@app.post("/classify")
async def classify(request: TextRequest):
    with torch.no_grad():
        input_tensor = torch.tensor([request.token_ids])
        logits = model(input_tensor)
        probs = torch.softmax(logits, dim=-1)
        prediction = torch.argmax(probs, dim=-1).item()
        confidence = probs[0][prediction].item()
    
    return {"class": prediction, "confidence": round(confidence, 4)}

# Export model to TorchScript (do once):
# scripted = torch.jit.script(model)
# scripted.save("model_scripted.pt")

# Export to ONNX (faster inference):
# torch.onnx.export(model, dummy_input, "model.onnx", 
#                   input_names=["input"], output_names=["output"])
```

---

## 4. ONNX Runtime (Cross-Framework Optimization)

```python
import onnxruntime as ort
import numpy as np

# ONNX: Open Neural Network Exchange
# Convert from PyTorch/TF → ONNX → optimized inference

# Load ONNX model
session = ort.InferenceSession("model.onnx", providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])

# Get input/output names
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

def predict_onnx(features: np.ndarray) -> np.ndarray:
    """Run inference with ONNX Runtime."""
    result = session.run(
        [output_name],
        {input_name: features.astype(np.float32)}
    )
    return result[0]

# Typically 2-5x faster than native PyTorch inference
# Supports: quantization, graph optimization, multi-threading

# Quantize ONNX model (reduce size, speed up CPU inference)
from onnxruntime.quantization import quantize_dynamic, QuantType

quantize_dynamic(
    "model.onnx",
    "model_quantized.onnx",
    weight_type=QuantType.QInt8,
)
# ~4x smaller, ~2x faster on CPU, minimal accuracy loss
```

---

## 5. Triton Inference Server

```python
# NVIDIA Triton: production GPU inference server
# Features: dynamic batching, multi-model, ensemble, auto-scaling

# Model repository structure:
# model_repository/
# ├── text_classifier/
# │   ├── config.pbtxt
# │   └── 1/
# │       └── model.onnx
# └── feature_extractor/
#     ├── config.pbtxt
#     └── 1/
#         └── model.pt

# config.pbtxt:
"""
name: "text_classifier"
platform: "onnxruntime_onnx"
max_batch_size: 64
input [
  {
    name: "input"
    data_type: TYPE_INT64
    dims: [128]
  }
]
output [
  {
    name: "output"
    data_type: TYPE_FP32
    dims: [10]
  }
]
dynamic_batching {
  preferred_batch_size: [16, 32]
  max_queue_delay_microseconds: 100
}
instance_group [
  {
    count: 2
    kind: KIND_GPU
  }
]
"""

# Run Triton:
# docker run --gpus all -p 8000:8000 -p 8001:8001 \
#   -v $(pwd)/model_repository:/models \
#   nvcr.io/nvidia/tritonserver:latest tritonserver --model-repository=/models

# Client:
import tritonclient.http as httpclient

client = httpclient.InferenceServerClient(url="localhost:8000")

# Check model status
assert client.is_model_ready("text_classifier")

# Send request
input_data = np.array([[1, 2, 3, ...]], dtype=np.int64)
inputs = [httpclient.InferInput("input", input_data.shape, "INT64")]
inputs[0].set_data_from_numpy(input_data)

result = client.infer("text_classifier", inputs)
output = result.as_numpy("output")
```

---

## 6. Latency Optimization

```python
# Optimization techniques (from least to most complex):

# 1. Model Quantization
# FP32 → FP16 (GPU): 2x speedup, minimal accuracy loss
# FP32 → INT8 (CPU): 3-4x speedup, ~1% accuracy loss
model_fp16 = model.half().cuda()  # PyTorch FP16

# 2. Dynamic Batching
# Collect requests, batch them, process together
import asyncio
from collections import deque

class BatchProcessor:
    def __init__(self, model, max_batch: int = 32, max_wait_ms: int = 50):
        self.model = model
        self.max_batch = max_batch
        self.max_wait = max_wait_ms / 1000
        self.queue = deque()
    
    async def predict(self, features):
        future = asyncio.Future()
        self.queue.append((features, future))
        
        if len(self.queue) >= self.max_batch:
            await self._process_batch()
        else:
            await asyncio.sleep(self.max_wait)
            if not future.done():
                await self._process_batch()
        
        return await future
    
    async def _process_batch(self):
        batch = []
        futures = []
        while self.queue and len(batch) < self.max_batch:
            features, future = self.queue.popleft()
            batch.append(features)
            futures.append(future)
        
        # Batch inference
        results = self.model.predict(np.array(batch))
        for future, result in zip(futures, results):
            future.set_result(result)

# 3. Model Distillation (train small model to mimic large)
# Teacher: BERT-large (24 layers) → Student: BERT-tiny (4 layers)
# 10x faster, 80-95% of teacher's accuracy

# 4. Caching predictions
from functools import lru_cache
import hashlib

prediction_cache = {}

def cached_predict(features_tuple):
    key = hashlib.md5(str(features_tuple).encode()).hexdigest()
    if key not in prediction_cache:
        prediction_cache[key] = model.predict(np.array([features_tuple]))
    return prediction_cache[key]
```

---

## 7. A/B Testing & Canary Deployments

```python
import random
from dataclasses import dataclass

@dataclass
class ModelVersion:
    name: str
    model: object
    weight: float  # Traffic percentage

class ABTestRouter:
    def __init__(self):
        self.versions: list[ModelVersion] = []
        self.metrics: dict[str, list] = {}
    
    def add_version(self, name: str, model, weight: float):
        self.versions.append(ModelVersion(name, model, weight))
        self.metrics[name] = []
    
    def route(self, features) -> tuple[str, float]:
        """Route request to a model version based on weights."""
        rand = random.random()
        cumulative = 0
        
        for version in self.versions:
            cumulative += version.weight
            if rand <= cumulative:
                prediction = version.model.predict(features)
                return version.name, prediction
        
        # Fallback
        return self.versions[0].name, self.versions[0].model.predict(features)
    
    def record_outcome(self, version_name: str, actual: float, predicted: float):
        """Record actual outcome for analysis."""
        self.metrics[version_name].append({"actual": actual, "predicted": predicted})
    
    def compare(self) -> dict:
        """Compare model versions."""
        results = {}
        for name, outcomes in self.metrics.items():
            if outcomes:
                errors = [abs(o["actual"] - o["predicted"]) for o in outcomes]
                results[name] = {"mae": np.mean(errors), "n": len(outcomes)}
        return results

# Canary deployment: gradually shift traffic
# Day 1: new_model=5%, old_model=95%
# Day 2: new_model=25%, old_model=75% (if metrics good)
# Day 3: new_model=100% (full rollout)

router = ABTestRouter()
router.add_version("v1_baseline", model_v1, weight=0.9)
router.add_version("v2_candidate", model_v2, weight=0.1)  # 10% canary
```

---

## Interview Questions

### Beginner
1. **What's the difference between batch and online serving?** Batch: process large datasets periodically (Spark, cron jobs), high throughput, stale results. Online: real-time API predictions per request, low latency required, always-on. Choose based on: freshness requirements, latency SLA, cost constraints.
2. **Why load the model at startup instead of per request?** Model loading is expensive (disk I/O, memory allocation, GPU transfer). Loading per request adds seconds of latency. Load once at startup → store in memory → serve from memory (microseconds). Use `@app.on_event("startup")` in FastAPI.
3. **What is ONNX?** Open Neural Network Exchange — a cross-framework model format. Export from PyTorch/TensorFlow → ONNX → run with ONNX Runtime. Benefits: faster inference (graph optimizations), deploy anywhere (no framework dependency), easy quantization.

### Intermediate
4. **Explain dynamic batching.** Collect multiple inference requests, combine into one batch, run batch inference (GPU-efficient). Trade-off: wait time vs throughput. Configure: max batch size (32-128) and max wait (10-100ms). Triton does this automatically. Increases GPU utilization from ~20% to ~80%.
5. **How do you implement canary deployment for ML models?** Deploy new model alongside old one. Route small traffic percentage (5-10%) to new model. Monitor metrics (latency, accuracy, error rate). Gradually increase traffic if metrics are good. Instant rollback if metrics degrade. Use feature flags or load balancer weights.
6. **Compare model optimization techniques.** Quantization (FP32→INT8): 3-4x faster, minimal accuracy loss, easiest. Pruning (remove weights): 2-3x smaller, needs retraining. Distillation (train small model): 5-10x faster, needs data + training. ONNX optimization: 1.5-2x faster, no accuracy loss.

### Advanced
7. **Design a serving system for 10K QPS with <50ms P99 latency.** Multiple model replicas behind load balancer. GPU instances with Triton (dynamic batching). Quantized model (INT8 on GPU). Response cache (Redis) for repeated inputs. Horizontal auto-scaling on CPU/GPU utilization. Separate inference from pre/post-processing. Monitor: latency percentiles, throughput, error rate.
8. **How would you serve an ensemble of models?** Triton ensemble pipelines (model A output → model B input). Or: parallel inference + aggregation. Architecture: preprocessing model → feature extraction → multiple classifiers → voting/stacking layer. Keep ensemble logic in serving config, not application code.
9. **When would you choose streaming serving over online?** When: processing continuous event streams (IoT, logs, transactions), need to maintain state across events, volume too high for individual API calls, near-real-time sufficient (seconds not milliseconds). Architecture: Kafka → Flink/Ray with model → output topic. Example: real-time fraud scoring on transaction stream.

---

## Hands-On Exercise
1. Build a FastAPI model endpoint (load sklearn model, /predict, /health)
2. Export a PyTorch model to ONNX, compare inference speed
3. Implement dynamic batching (collect requests, batch predict)
4. Set up Triton with a simple ONNX model (Docker)
5. Build an A/B test router serving 2 model versions
6. Quantize a model (INT8) and measure speed improvement vs accuracy
