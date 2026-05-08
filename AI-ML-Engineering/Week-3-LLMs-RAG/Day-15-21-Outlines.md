# Week 3: LLMs & RAG — Remaining Day Outlines

## Day 15: LLM Fundamentals
- How LLMs work (next token prediction, autoregressive)
- Key architectures: GPT (decoder-only), BERT (encoder), T5 (encoder-decoder)
- Scaling laws (Chinchilla, parameters vs data)
- Tokenization (BPE, SentencePiece) and vocabulary size
- Context windows (4K → 128K+ evolution)
- Key models: GPT-4, Claude, Llama, Mistral, Gemini
- Open vs closed source tradeoffs

## Day 16: Prompt Engineering
- Zero-shot, few-shot, chain-of-thought prompting
- System prompts and persona definition
- Output formatting (JSON mode, structured outputs)
- Self-consistency and majority voting
- ReAct (Reasoning + Acting) pattern
- Tree of Thoughts for complex reasoning
- Prompt optimization techniques
- Anti-patterns and common failures

## Day 17: RAG Architecture
- RAG concept (retrieval-augmented generation)
- Document loading and chunking (recursive, semantic)
- Embeddings (OpenAI, sentence-transformers, BGE)
- Vector databases (Qdrant, Pinecone, Weaviate, ChromaDB)
- Similarity search (cosine, dot product, Euclidean)
- RAG pipeline: query → embed → retrieve → augment → generate
- Evaluation metrics (faithfulness, relevance, context precision)
- LangChain and LlamaIndex for RAG

## Day 18: Advanced RAG
- Naive RAG vs Advanced RAG vs Modular RAG
- Query rewriting and HyDE (Hypothetical Document Embedding)
- Multi-query retrieval (generate multiple search queries)
- Contextual compression and re-ranking
- Hybrid search (dense + sparse / BM25 + embeddings)
- Parent-child chunking (small chunks for retrieval, big for context)
- Self-RAG (model decides when to retrieve)
- Knowledge graph + RAG

## Day 20: Embeddings Deep Dive
- What embeddings capture (semantic similarity)
- Training embedding models (contrastive learning, RLHF)
- Fine-tuning embeddings for domain-specific data
- Matryoshka embeddings (variable dimensions)
- Multi-modal embeddings (CLIP, text + image)
- Embedding quantization for efficiency
- Evaluation: MTEB benchmark
- Choosing: open source vs API embeddings

## Day 21: Project — Production RAG System
- Build RAG for technical documentation
- Multiple document types (PDF, code, markdown)
- Chunking strategy selection and comparison
- Hybrid search with re-ranking (Cohere, cross-encoder)
- Evaluation pipeline (RAGAS framework)
- Streaming responses
- Conversation memory and multi-turn
- Deploy with FastAPI + Qdrant
