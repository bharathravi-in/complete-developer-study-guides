# Day 29: System Design for ML

## Learning Objectives
- Apply ML system design framework (Problem → Data → Model → Serving → Monitoring)
- Design fraud detection, recommendation, and content moderation systems
- Navigate key tradeoffs (latency vs accuracy, cost vs performance)
- Scale ML systems effectively

---

## 1. ML System Design Framework

```
Step 1: PROBLEM DEFINITION
- What metric are we optimizing? (precision vs recall, engagement vs quality)
- What are the constraints? (latency SLA, cost budget, data availability)
- What's the business impact? (quantify value of improvement)

Step 2: DATA
- What data is available? What needs to be collected?
- Labels: how are they obtained? (explicit, implicit, delayed?)
- Volume, velocity, variety
- Data quality issues and mitigations

Step 3: FEATURES & MODEL
- Feature engineering: what signals predict the target?
- Model selection: simple baseline → iterative complexity
- Online vs offline features
- Training: how often? How much data?

Step 4: SERVING
- Batch vs online vs streaming
- Latency requirements
- Throughput requirements
- Fallback strategy

Step 5: MONITORING & ITERATION
- What metrics to track in production?
- How to detect degradation?
- Retraining strategy
- A/B testing framework
```

---

## 2. Design: Fraud Detection System

```
PROBLEM:
- Detect fraudulent credit card transactions in real-time
- Constraint: <100ms latency, high precision (don't block legit users)
- Metric: Precision at 90% recall (minimize false positives while catching most fraud)
- Business: Each fraud costs $500 avg, each false block costs $20 (customer churn)

DATA:
- Transaction data: amount, merchant, location, time, device
- Historical: labeled fraud/legit (1% fraud rate — highly imbalanced)
- User history: past transactions, spending patterns
- Labels: chargebacks (delayed 30-90 days), manual review

FEATURES:
- Batch (daily): avg_spend_30d, num_transactions_7d, usual_merchants
- Real-time (streaming): transactions_last_hour, velocity, distance_from_last
- Derived: amount_vs_average (z-score), new_merchant_flag, unusual_time_flag

MODEL:
- Baseline: Rule-based (amount > 5x average → flag)
- V1: Gradient Boosted Trees (XGBoost) — fast inference, interpretable
- V2: Neural network for sequence modeling (transaction history)
- Ensemble: rules + ML (rules catch obvious fraud, ML catches subtle patterns)

SERVING:
- Online: real-time scoring per transaction (<50ms)
- Feature store: Redis for real-time features, BigQuery for batch
- Fallback: if ML fails → rule-based system (degraded but functional)
- Architecture: Kafka → Feature Enrichment → Model → Decision

MONITORING:
- Precision/recall (computed weekly with chargeback labels)
- False positive rate (immediate, from customer complaints)
- Feature drift (transaction patterns during holidays)
- Latency P95/P99
- Auto-retrain monthly (new fraud patterns emerge)
```

---

## 3. Design: Recommendation Engine

```
PROBLEM:
- Personalized product recommendations for e-commerce (10M users, 1M products)
- Metric: Click-through rate (CTR), conversion rate
- Constraint: 200ms latency for page load, fresh recommendations
- Trade-off: exploration (new items) vs exploitation (known preferences)

DATA:
- Implicit feedback: clicks, views, purchases, time on page
- User features: demographics, browse history, device
- Item features: category, price, brand, images, descriptions
- Context: time of day, season, trending items

FEATURES:
- User embedding (from interaction history)
- Item embedding (from content + collaborative filtering)
- User-item features: category affinity, price sensitivity, brand loyalty
- Context: time features, device, location

MODEL:
- Candidate Generation: retrieve 1000 candidates (fast, broad)
  → Two-tower model (user tower + item tower, dot product similarity)
- Ranking: score 1000 → top 20 (slow but precise)
  → Deep ranking model (concat user+item+context features → score)
- Re-ranking: business logic (diversity, promotions, freshness)

SERVING:
- Candidate generation: precomputed item embeddings in ANN index
- Ranking: online inference (batch the 1000 candidates)
- Cache: popular items recommendations (cache warm-up)
- Fallback: trending items / bestsellers (cold-start, model failure)

Architecture:
User Request → User Features (Redis) → Candidate Generation (ANN) 
→ Ranking Model (GPU) → Business Rules → Response

MONITORING:
- CTR, conversion rate (by position, category, user segment)
- Coverage: % of catalog recommended (avoid only showing popular items)
- Freshness: age of recommended items
- A/B test: new model vs current (2 weeks, 5% traffic)
```

---

## 4. Design: Real-Time Content Moderation

```
PROBLEM:
- Detect harmful content (hate speech, violence, spam) on social platform
- Constraint: <500ms (before content shown to others), high recall (catch all harmful)
- Metric: Recall at 95% precision (don't miss harmful content)
- Scale: 100K posts/minute

DATA:
- Text: post content, comments
- Images/video: uploaded media
- Context: user history, posting patterns, social graph
- Labels: human moderator decisions, user reports

MODEL:
Multi-stage pipeline:
1. Fast filter (rule-based + small model): catch obvious violations instantly
2. ML classifier (BERT-based): score content 0-1 on multiple categories
3. LLM review (for borderline cases): nuanced understanding
4. Human review (high-uncertainty): final decision

- Text: fine-tuned BERT for toxicity classification
- Images: fine-tuned CLIP/ViT for NSFW/violence detection
- Multi-modal: joint text+image model for context

SERVING:
- Streaming: Kafka → pre-filter → ML model → decision queue
- Async for non-real-time (old posts reported)
- Human-in-the-loop for uncertain cases (0.3 < score < 0.7)
- Auto-action: score > 0.9 → remove immediately

MONITORING:
- False positive rate (legitimate content removed)
- Appeal overturn rate (wrong decisions)
- Coverage (% content scored before shown)
- Latency: P99 < 500ms
- Category-specific performance (hate speech vs spam vs violence)
```

---

## 5. Design: Search Relevance System

```
PROBLEM:
- Improve search results ranking for e-commerce
- Metric: NDCG@10, revenue per search
- Constraint: <200ms total search latency
- Balance: relevance vs revenue (sponsored vs organic)

DATA:
- Queries: text, reformulations, session context
- Clicks: position-biased (correct with IPW)
- Purchases: strongest signal (sparse)
- Item data: title, description, categories, images, price, stock

FEATURES:
- Query-item: BM25 score, semantic similarity, category match
- Item quality: CTR history, conversion rate, reviews, freshness
- User personalization: past purchases, category affinity
- Context: device, location, time

MODEL:
1. Retrieval: BM25 + embedding search → 1000 candidates
2. Ranking: LambdaMART or neural ranker (query + item features → relevance score)
3. Re-ranking: diversity, business rules, personalization boost

Learning to Rank:
- Pointwise: predict relevance score per item
- Pairwise: predict which of two items is more relevant
- Listwise: optimize NDCG directly (LambdaRank)

SERVING:
Query → Query Understanding (spelling, expansion) → Retrieval (ES + ANN)
→ Feature Assembly → Ranker → Business Rules → Results

MONITORING:
- NDCG@10 (offline eval + interleaving experiments)
- No-result rate (queries returning nothing)
- Clicks at different positions
- Query→purchase funnel metrics
```

---

## 6. Key Tradeoffs

```python
# Tradeoff 1: Latency vs Accuracy
# Simple model (5ms, 85% accuracy) vs Complex model (200ms, 92% accuracy)
# Solution: cascade — fast model for easy cases, complex for hard cases

# Tradeoff 2: Cost vs Performance
# GPT-4 (expensive, high quality) vs GPT-4o-mini (cheap, good quality)
# Solution: route by complexity, cache, batch

# Tradeoff 3: Freshness vs Stability
# Retrain daily (fresh but might be noisy) vs monthly (stable but stale)
# Solution: online learning for features, periodic full retrain for model

# Tradeoff 4: Precision vs Recall
# Fraud: high precision (don't block legit users)
# Content moderation: high recall (don't miss harmful content)
# Solution: adjust threshold based on business impact

# Tradeoff 5: Exploration vs Exploitation (recommendations)
# Exploit: show what we KNOW user likes (safe, good short-term CTR)
# Explore: try new items (risky, but discovers new preferences)
# Solution: epsilon-greedy, Thompson sampling, contextual bandits

# Tradeoff 6: Model Complexity vs Operability
# Complex: ensemble of 5 models, custom features, real-time signals
# Simple: single model, batch features
# Consider: team size, debugging difficulty, maintenance cost

# Framework for tradeoff decisions:
# 1. Quantify business value of each option
# 2. Estimate engineering cost (build + maintain)
# 3. Consider: team expertise, timeline, scale requirements
# 4. Start simple, add complexity only when justified by data
```

---

## 7. Scaling ML Systems

```python
# Horizontal scaling patterns:

# Data parallelism: split data across workers
# - Training: distributed gradient descent (PyTorch DDP, Horovod)
# - Inference: multiple model replicas behind load balancer
# - Feature computation: Spark/Dask across cluster

# Model parallelism: split model across devices
# - Large models that don't fit on one GPU
# - Pipeline parallelism: layers on different GPUs
# - Tensor parallelism: single layer split across GPUs

# Feature store scaling:
# - Offline: partition by entity + time (BigQuery, Delta Lake)
# - Online: shard by entity ID across Redis cluster

# Inference scaling:
# - Auto-scale on QPS/latency (Kubernetes HPA)
# - GPU sharing (Triton multi-model, MIG)
# - Batch requests (Triton dynamic batching)
# - Cache popular predictions

# Data pipeline scaling:
# - Backfill: Spark batch (cost-effective, high throughput)
# - Real-time: Flink/Kafka Streams (low latency, complex)
# - Hybrid: batch for historical + streaming for fresh
```

---

## Interview Questions

### Beginner
1. **What's the ML system design framework?** Problem definition (metrics, constraints) → Data (sources, labels, quality) → Features & Model (engineering, selection) → Serving (batch/online, latency) → Monitoring (drift, performance, retraining). Always start with problem understanding and constraints.
2. **Why start with a simple baseline?** Establishes performance floor. Quick to implement and validate data pipeline. Helps understand data issues. Complex model improvement measured against it. Sometimes simple is good enough. Rules/heuristics → logistic regression → trees → deep learning.
3. **What's the difference between candidate generation and ranking?** Candidate generation: fast, broad retrieval (1000 items from millions) using embeddings/rules. Ranking: slow, precise scoring of candidates using rich features. Two-stage because: scoring all items is too expensive, but we need rich features for quality.

### Intermediate
4. **How do you handle imbalanced classes in fraud detection?** Data level: SMOTE, undersampling majority. Model level: class weights, focal loss. Threshold: optimize decision threshold on precision-recall curve. Evaluation: use PR-AUC (not ROC-AUC), precision@recall. Operational: separate models for different fraud types.
5. **How do you handle position bias in search ranking?** Clicks are biased toward higher positions. Solutions: Inverse Propensity Weighting (IPW), unbiased learning to rank, interleaving experiments (randomize top results), use purchase signals (less position-biased). Data correction: estimate position effect, debias click labels.
6. **Design a cold-start strategy for recommendations.** New users: popular items → content-based (from browse history) → collaborative after 5+ interactions. New items: content features (description, category, images) → boost exploration → transition to behavior-based. Explicit preferences on signup help.

### Advanced
7. **Design a real-time ML system at 1M events/sec.** Architecture: Kafka (ingest) → Flink (feature enrichment + model inference) → output topic. Features: online store (Redis cluster, sharded) + stream aggregations. Model: ONNX quantized, deployed in Flink UDF. Scaling: partition by entity, scale Flink workers. Fallback: rule-based if model latency exceeds budget.
8. **How do you design an ML system for multi-region deployment?** Model: same model globally or region-specific? Data residency: features must stay in region (GDPR). Architecture: global model registry, regional feature stores, local inference. Sync: federated learning or periodic global retraining. Monitoring: per-region performance (culture-specific patterns).
9. **Compare end-to-end neural approaches vs modular ML systems.** End-to-end (one model): simpler deployment, auto-learns features, needs more data, less interpretable. Modular (pipeline of models): interpretable, easier to debug, can improve components independently, more engineering. Trend: start modular, replace bottleneck components with neural as data grows.

---

## Hands-On Exercise
1. Design a fraud detection system (write system design doc: 2 pages)
2. Design a recommendation system for a news app (cold-start focus)
3. Draw architecture diagrams for both (components, data flow, latency)
4. Identify top 3 tradeoffs in each system, justify your choices
5. Estimate infrastructure costs for serving 100K QPS
6. Plan a 4-week roadmap: baseline → v1 → monitoring → iteration
