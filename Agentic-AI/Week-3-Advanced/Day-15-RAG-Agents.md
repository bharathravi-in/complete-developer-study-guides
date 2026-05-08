# Day 15: RAG Agents

## Learning Objectives
- Build agentic RAG (agent decides when/how to retrieve)
- Implement self-RAG with reflection and correction
- Design adaptive retrieval strategies
- Build multi-step RAG with iterative refinement
- Implement Corrective RAG (CRAG) patterns

---

## 1. Traditional RAG vs Agentic RAG

```
Traditional RAG:
  Query → Retrieve → Generate (fixed pipeline, always retrieves)

Agentic RAG:
  Query → Agent DECIDES:
    - Do I need to retrieve? (maybe I already know)
    - What to search for? (reformulate query)
    - Is the retrieval good enough? (evaluate, retry)
    - Should I search multiple sources? (route)
    - Do I need to decompose the question? (multi-step)

Key difference: Agent has AGENCY over the retrieval process
```

---

## 2. Basic Agentic RAG

```python
from openai import OpenAI
from typing import Literal
from pydantic import BaseModel

client = OpenAI()

class RetrievalDecision(BaseModel):
    action: Literal["retrieve", "answer_directly", "clarify"]
    search_query: str | None = None
    reasoning: str

class AgenticRAG:
    """Agent that decides when and how to retrieve."""
    
    def __init__(self, retriever):
        self.retriever = retriever  # Vector store search function
    
    def answer(self, question: str) -> str:
        # Step 1: Decide if retrieval is needed
        decision = self._decide(question)
        
        if decision.action == "answer_directly":
            return self._generate_answer(question, context=None)
        
        if decision.action == "clarify":
            return f"I need clarification: {decision.reasoning}"
        
        # Step 2: Retrieve
        docs = self.retriever.search(decision.search_query or question, k=5)
        
        # Step 3: Evaluate retrieval quality
        if not self._is_relevant(question, docs):
            # Reformulate and retry
            new_query = self._reformulate(question, docs)
            docs = self.retriever.search(new_query, k=5)
        
        # Step 4: Generate answer
        return self._generate_answer(question, context=docs)
    
    def _decide(self, question: str) -> RetrievalDecision:
        response = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[{"role": "system", "content": """Decide if retrieval is needed.
- "retrieve": question needs external knowledge
- "answer_directly": you can answer from general knowledge
- "clarify": question is ambiguous"""
            }, {"role": "user", "content": question}],
            response_format=RetrievalDecision,
        )
        return response.choices[0].message.parsed
    
    def _is_relevant(self, question: str, docs: list[str]) -> bool:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Are these documents relevant to answer: '{question}'?\nDocs: {docs[:3]}\nAnswer YES or NO."}],
        )
        return "YES" in response.choices[0].message.content.upper()
    
    def _reformulate(self, original_query: str, failed_docs: list[str]) -> str:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"The search '{original_query}' returned irrelevant results. Reformulate as a better search query."}],
        )
        return response.choices[0].message.content
    
    def _generate_answer(self, question: str, context: list[str] | None) -> str:
        messages = [{"role": "system", "content": "Answer based on provided context. If no context, use general knowledge. Cite sources when available."}]
        if context:
            messages.append({"role": "user", "content": f"Context:\n{chr(10).join(context)}\n\nQuestion: {question}"})
        else:
            messages.append({"role": "user", "content": question})
        
        response = client.chat.completions.create(model="gpt-4o", messages=messages)
        return response.choices[0].message.content
```

---

## 3. Self-RAG (Reflection & Correction)

```python
class SelfRAG:
    """
    Self-RAG: Agent generates, then self-evaluates and corrects.
    Paper: "Self-RAG: Learning to Retrieve, Generate, and Critique"
    
    Steps:
    1. Decide if retrieval is needed
    2. Retrieve (if needed)
    3. Evaluate relevance of retrieved docs
    4. Generate response
    5. Self-evaluate: is response supported by evidence?
    6. Self-evaluate: is response useful?
    7. If not good enough, iterate
    """
    
    def __init__(self, retriever):
        self.retriever = retriever
    
    def answer(self, question: str, max_iterations: int = 3) -> str:
        for iteration in range(max_iterations):
            # Retrieve
            docs = self.retriever.search(question, k=5)
            
            # Generate with citation
            response = self._generate_with_citation(question, docs)
            
            # Self-evaluate
            eval_result = self._self_evaluate(question, response, docs)
            
            if eval_result["is_supported"] and eval_result["is_useful"]:
                return response
            
            # Correct: refine query based on what's missing
            question = self._refine_query(question, eval_result["critique"])
        
        return response  # Return best attempt
    
    def _generate_with_citation(self, question: str, docs: list[str]) -> str:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Answer the question using the provided documents. Cite specific documents [1], [2], etc."
            }, {"role": "user", "content": f"Documents:\n{self._format_docs(docs)}\n\nQuestion: {question}"}],
        )
        return response.choices[0].message.content
    
    def _self_evaluate(self, question: str, response: str, docs: list[str]) -> dict:
        eval_prompt = f"""Evaluate this response:
Question: {question}
Response: {response}
Source documents: {docs[:3]}

Evaluate:
1. Is the response SUPPORTED by the source documents? (yes/no)
2. Is the response USEFUL for answering the question? (yes/no)
3. What's missing or incorrect? (critique)

Reply as JSON: {{"is_supported": bool, "is_useful": bool, "critique": "..."}}"""
        
        response = client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": eval_prompt}],
        )
        import json
        return json.loads(response.choices[0].message.content)
    
    def _refine_query(self, original: str, critique: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Original query: {original}\nCritique of results: {critique}\nWrite a better search query to find the missing information."}],
        )
        return response.choices[0].message.content
    
    def _format_docs(self, docs: list[str]) -> str:
        return "\n".join(f"[{i+1}] {doc}" for i, doc in enumerate(docs))
```

---

## 4. Multi-Step RAG (Query Decomposition)

```python
class MultiStepRAG:
    """Decompose complex questions into sub-queries, retrieve for each, synthesize."""
    
    def __init__(self, retriever):
        self.retriever = retriever
    
    def answer(self, question: str) -> str:
        # Step 1: Decompose into sub-questions
        sub_questions = self._decompose(question)
        
        # Step 2: Answer each sub-question
        sub_answers = {}
        for sq in sub_questions:
            docs = self.retriever.search(sq, k=3)
            answer = self._answer_sub(sq, docs)
            sub_answers[sq] = answer
        
        # Step 3: Synthesize final answer
        return self._synthesize(question, sub_answers)
    
    def _decompose(self, question: str) -> list[str]:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Break this complex question into 2-4 simpler sub-questions that can be independently researched."
            }, {"role": "user", "content": question}],
        )
        # Parse numbered list
        lines = response.choices[0].message.content.strip().split("\n")
        return [l.lstrip("0123456789.- ") for l in lines if l.strip()]
    
    def _answer_sub(self, question: str, docs: list[str]) -> str:
        context = "\n".join(docs)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Context: {context}\n\nAnswer briefly: {question}"}],
        )
        return response.choices[0].message.content
    
    def _synthesize(self, original_question: str, sub_answers: dict) -> str:
        parts = "\n".join(f"Q: {q}\nA: {a}" for q, a in sub_answers.items())
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Synthesize these sub-answers into a comprehensive response."
            }, {"role": "user", "content": f"Original question: {original_question}\n\nSub-answers:\n{parts}"}],
        )
        return response.choices[0].message.content
```

---

## 5. Corrective RAG (CRAG)

```python
class CorrectiveRAG:
    """
    CRAG: Corrective Retrieval Augmented Generation
    Key idea: Evaluate retrieval quality and take corrective actions
    
    Actions based on relevance score:
    - CORRECT: docs are relevant → use them
    - AMBIGUOUS: partially relevant → refine + supplement with web search
    - INCORRECT: docs irrelevant → fall back to web search entirely
    """
    
    def __init__(self, retriever, web_search):
        self.retriever = retriever
        self.web_search = web_search  # Fallback search
    
    def answer(self, question: str) -> str:
        # Retrieve from primary source
        docs = self.retriever.search(question, k=5)
        
        # Evaluate relevance of each doc
        relevance_scores = [self._score_relevance(question, doc) for doc in docs]
        avg_score = sum(relevance_scores) / max(len(relevance_scores), 1)
        
        # Take corrective action based on scores
        if avg_score > 0.7:
            # CORRECT: use retrieved docs
            context = [d for d, s in zip(docs, relevance_scores) if s > 0.5]
        elif avg_score > 0.3:
            # AMBIGUOUS: supplement with web search
            web_results = self.web_search(question)
            relevant_docs = [d for d, s in zip(docs, relevance_scores) if s > 0.5]
            context = relevant_docs + web_results
        else:
            # INCORRECT: fall back to web search entirely
            context = self.web_search(question)
        
        # Generate with knowledge refinement
        refined_context = self._refine_knowledge(question, context)
        return self._generate(question, refined_context)
    
    def _score_relevance(self, question: str, doc: str) -> float:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": f"Rate relevance of this document to the question (0.0 to 1.0).\nQuestion: {question}\nDocument: {doc[:500]}\nScore:"}],
        )
        try:
            return float(response.choices[0].message.content.strip())
        except ValueError:
            return 0.5
    
    def _refine_knowledge(self, question: str, docs: list[str]) -> str:
        """Extract only the relevant parts from documents."""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Extract ONLY information relevant to: {question}\n\nFrom these documents:\n{chr(10).join(docs[:5])}"}],
        )
        return response.choices[0].message.content
    
    def _generate(self, question: str, context: str) -> str:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Answer using the provided context."
            }, {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}],
        )
        return response.choices[0].message.content
```

---

## 6. Adaptive Retrieval with LangGraph

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class RAGState(TypedDict):
    question: str
    documents: list[str]
    generation: str
    relevance_score: float
    iteration: int
    max_iterations: int

def decide_retrieval(state: RAGState) -> str:
    """Route based on whether docs are good enough."""
    if state["relevance_score"] > 0.7:
        return "generate"
    elif state["iteration"] >= state["max_iterations"]:
        return "generate"  # Give up and generate with what we have
    else:
        return "refine_and_retrieve"

def retrieve(state: RAGState) -> dict:
    docs = retriever.search(state["question"], k=5)
    return {"documents": docs, "iteration": state["iteration"] + 1}

def evaluate_relevance(state: RAGState) -> dict:
    # Score how relevant retrieved docs are
    score = score_relevance(state["question"], state["documents"])
    return {"relevance_score": score}

def refine_query(state: RAGState) -> dict:
    new_query = reformulate_query(state["question"], state["documents"])
    return {"question": new_query}

def generate(state: RAGState) -> dict:
    answer = generate_answer(state["question"], state["documents"])
    return {"generation": answer}

# Build graph
graph = StateGraph(RAGState)
graph.add_node("retrieve", retrieve)
graph.add_node("evaluate", evaluate_relevance)
graph.add_node("refine", refine_query)
graph.add_node("generate", generate)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "evaluate")
graph.add_conditional_edges("evaluate", decide_retrieval, {
    "generate": "generate",
    "refine_and_retrieve": "refine",
})
graph.add_edge("refine", "retrieve")
graph.add_edge("generate", END)

app = graph.compile()
```

---

## Interview Questions

### Beginner
1. **What makes RAG "agentic"?** Traditional RAG always retrieves and generates (fixed pipeline). Agentic RAG: agent DECIDES whether to retrieve, what query to use, whether results are good enough, whether to retry. Agent has control over the retrieval strategy rather than following fixed steps.
2. **What is Self-RAG?** Agent generates a response, then self-evaluates: Is it supported by evidence? Is it useful? If not, it refines the query and tries again. Key insight: the model critiques its own output and iterates. Reduces hallucination by verifying against sources.
3. **Why decompose complex questions into sub-queries?** Complex questions often can't be answered by a single retrieval. "Compare X and Y across dimensions A, B, C" needs separate searches. Each sub-query targets specific info. Final synthesis combines all sub-answers into coherent response.

### Intermediate
4. **Explain the CRAG (Corrective RAG) approach.** Score relevance of retrieved docs. Three actions: CORRECT (high relevance → use docs), AMBIGUOUS (medium → supplement with web search), INCORRECT (low → discard, use web search only). Key improvement: don't blindly trust retrieval. Evaluate and correct before generating.
5. **How do you evaluate retrieval quality within an agent loop?** LLM-as-judge: ask model "is this doc relevant?" Score relevance 0-1. Heuristics: keyword overlap, embedding similarity. Red flags: retrieved docs don't contain query terms, docs are about different topic. Track retrieval quality metrics across runs.
6. **When would you use multi-step RAG vs single retrieval?** Multi-step: complex questions needing info from multiple topics, comparative questions, questions with sub-parts. Single: factual lookups, specific questions with direct answers. Multi-step costs more (multiple retrievals + generations) but handles complexity better.

### Advanced
7. **Design an agentic RAG system for a legal research platform.** Sources: case law, statutes, regulations (different indices). Agent: classifies question type → routes to appropriate index. Multi-step: find relevant cases → extract holdings → find contradicting cases → synthesize. Self-evaluation: verify citations are real, check currency of law. HITL: flag uncertain answers for lawyer review.
8. **How do you prevent infinite loops in self-correcting RAG?** Max iteration cap. Track: what queries have been tried (avoid repeats). Diminishing returns detection: if relevance isn't improving, stop. Fallback: after N iterations, answer with disclaimer about uncertainty. Budget: limit total tokens/cost per query.
9. **Compare agentic RAG approaches for latency-sensitive vs quality-sensitive applications.** Latency-sensitive: single retrieval, no self-evaluation, cache frequent queries, use smaller models for routing. Quality-sensitive: multi-step, self-RAG, CRAG, multiple iterations allowed. Hybrid: router decides based on query complexity — simple questions get fast path, complex get thorough path.

---

## Hands-On Exercise
1. Build basic agentic RAG that decides whether to retrieve or answer directly
2. Implement Self-RAG with generate-evaluate-refine loop
3. Build multi-step RAG with query decomposition and synthesis
4. Implement CRAG with relevance scoring and corrective actions
5. Create adaptive RAG with LangGraph (retrieval → evaluate → decide)
6. Compare quality and latency: traditional RAG vs agentic RAG on 10 questions
