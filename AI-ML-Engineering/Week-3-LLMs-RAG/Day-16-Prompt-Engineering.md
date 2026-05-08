# Day 16: Prompt Engineering

## Learning Objectives
- Master zero-shot, few-shot, and chain-of-thought prompting
- Design effective system prompts and output formats
- Apply advanced techniques (ReAct, Tree of Thoughts, Self-Consistency)
- Avoid common prompt engineering anti-patterns

---

## 1. Basic Prompting Patterns

### Zero-Shot (No Examples)

```python
# Just describe the task — model uses pre-training knowledge
prompt = """Classify the following text as positive, negative, or neutral.

Text: "The movie was decent but the ending felt rushed."
Classification:"""
# Output: "neutral"
```

### Few-Shot (Provide Examples)

```python
# Give examples of input → output pattern
prompt = """Classify the sentiment of each text.

Text: "I absolutely loved this product!"
Sentiment: positive

Text: "Terrible quality, broke after one day."
Sentiment: negative

Text: "It works fine, nothing special."
Sentiment: neutral

Text: "The service was outstanding and exceeded all expectations."
Sentiment:"""
# Output: "positive" (model learns the pattern from examples)
```

### Chain-of-Thought (CoT)

```python
# Ask model to reason step-by-step before answering
prompt = """Solve this problem step by step.

Question: A store sells notebooks for $3 each. If you buy 5 or more, 
you get 20% off. How much do 7 notebooks cost?

Let's think step by step:
1. Base price for 7 notebooks: 7 × $3 = $21
2. Since 7 ≥ 5, the 20% discount applies
3. Discount amount: $21 × 0.20 = $4.20
4. Final price: $21 - $4.20 = $16.80

Answer: $16.80"""

# Auto CoT (just add "Let's think step by step")
prompt = """Question: If 3 machines can produce 90 widgets in 4 hours, 
how many widgets can 5 machines produce in 6 hours?

Let's think step by step:"""
```

---

## 2. System Prompts & Personas

```python
from openai import OpenAI
client = OpenAI()

# System prompt defines behavior, constraints, and format
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": """You are a senior Python code reviewer.

Rules:
- Point out bugs, security issues, and performance problems
- Suggest specific fixes with code examples
- Rate severity: critical, warning, or suggestion
- Be concise — no more than 3 issues per review
- Format as a numbered list

Never:
- Rewrite the entire code
- Suggest style-only changes
- Be condescending"""},
        {"role": "user", "content": "Review this code:\n```python\ndef get_user(id):\n    query = f'SELECT * FROM users WHERE id = {id}'\n    return db.execute(query)\n```"}
    ],
)

# Structured output with JSON mode
response = client.chat.completions.create(
    model="gpt-4o",
    response_format={"type": "json_object"},
    messages=[
        {"role": "system", "content": """Extract entities from text. 
Return JSON with format: {"people": [], "organizations": [], "locations": []}"""},
        {"role": "user", "content": "Tim Cook announced that Apple will open a new office in London."}
    ],
)
# {"people": ["Tim Cook"], "organizations": ["Apple"], "locations": ["London"]}
```

---

## 3. Advanced Techniques

### Self-Consistency (Majority Voting)

```python
# Generate multiple reasoning paths, take majority answer
def self_consistency(prompt, n=5, temperature=0.7):
    """Generate N answers, return most common one."""
    answers = []
    for _ in range(n):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        answer = extract_final_answer(response.choices[0].message.content)
        answers.append(answer)
    
    # Return majority vote
    from collections import Counter
    most_common = Counter(answers).most_common(1)[0]
    return most_common[0], most_common[1] / n  # answer, confidence
```

### ReAct (Reasoning + Acting)

```python
# Model alternates between thinking and taking actions
react_prompt = """Answer the following question using the tools available.

Tools:
- search(query): Search the web for information
- calculate(expression): Evaluate a math expression
- lookup(term): Look up a term in the knowledge base

Question: What is the population of France divided by the area of France in km²?

Thought: I need to find the population and area of France, then divide.
Action: search("population of France 2024")
Observation: The population of France is approximately 68.2 million.

Thought: Now I need the area.
Action: search("area of France in square kilometers")
Observation: France has an area of approximately 643,801 km².

Thought: Now I can calculate the population density.
Action: calculate("68200000 / 643801")
Observation: 105.93

Thought: I have the answer.
Answer: The population of France divided by its area is approximately 106 people per km²."""
```

### Tree of Thoughts

```python
# Explore multiple reasoning paths, evaluate each, backtrack if needed
tree_of_thoughts_prompt = """Solve this puzzle. Consider multiple approaches, 
evaluate each, and choose the best.

Puzzle: Arrange the digits 1-9 in a 3x3 grid so each row, column, 
and diagonal sums to 15.

Approach 1: Start with center
- Center must be 5 (appears in all 4 lines through center)
- Each line through center: pair must sum to 10
- Pairs: (1,9), (2,8), (3,7), (4,6)
- Evaluation: Promising, center=5 is correct.

Approach 2: Start with corners
- Corners appear in 3 lines each (row, column, diagonal)
- Even numbers in corners: 2,4,6,8
- Evaluation: Also valid, but Approach 1 gives clearer constraints.

Continuing Approach 1:
- Place 5 in center
- Opposite pairs on each line through center: 2-8, 4-6, 1-9, 3-7
- [continues to solution...]"""
```

---

## 4. Output Formatting

```python
# JSON output (structured, parseable)
prompt = """Analyze this customer review and return a JSON object.

Review: "Great product but shipping took forever. Would buy again though."

Return JSON:
{
  "sentiment": "positive|negative|mixed",
  "aspects": [{"aspect": "...", "sentiment": "..."}],
  "recommendation_likely": true/false,
  "confidence": 0.0-1.0
}"""

# Markdown table output
prompt = """Compare Python, JavaScript, and Go for backend development.
Format as a markdown table with columns: Language, Speed, Ecosystem, Learning Curve, Best For."""

# XML tags for structured sections (especially useful with Claude)
prompt = """<task>Summarize the following article</task>

<article>
{article_text}
</article>

<constraints>
- Maximum 3 sentences
- Include the main conclusion
- Use simple language
</constraints>

<output_format>
Summary: [your summary]
Key takeaway: [one sentence]
</output_format>"""
```

---

## 5. Prompt Optimization Techniques

```python
# 1. Be specific about what you want
# BAD: "Write something about climate change"
# GOOD: "Write a 200-word explanation of the greenhouse effect for a 12-year-old"

# 2. Use delimiters for clear input separation
prompt = f"""Summarize the text delimited by triple backticks.

```{article_text}```

Summary:"""

# 3. Specify output length/format explicitly
# "Respond in exactly 3 bullet points"
# "Give a one-word answer: yes or no"
# "Return only the JSON, no explanation"

# 4. Give the model a role/expertise
# "You are an expert data scientist with 10 years of experience..."

# 5. Break complex tasks into steps
prompt = """Analyze this dataset description in 3 steps:
Step 1: Identify the key variables
Step 2: Suggest potential relationships
Step 3: Recommend visualization types

Dataset: [description]"""

# 6. Use negative examples (show what NOT to do)
prompt = """Write a professional email.
DO: Be concise, include clear ask, provide deadline
DON'T: Use slang, include unnecessary details, be passive-aggressive"""

# 7. Provide context and constraints
prompt = """Context: You're helping a startup with limited engineering resources.
Constraint: Solution must be implementable in 1 week with 2 engineers.
Question: How should we implement user authentication?"""
```

---

## 6. Anti-Patterns & Common Failures

```python
# ❌ ANTI-PATTERN 1: Vague instructions
# Bad: "Help me with my code"
# Good: "Find the bug in this Python function that causes IndexError on empty lists"

# ❌ ANTI-PATTERN 2: Too many instructions at once
# Bad: 500-word system prompt with 20 rules
# Good: Focus on 3-5 most important rules, add examples

# ❌ ANTI-PATTERN 3: Conflicting instructions
# Bad: "Be concise" + "Explain thoroughly"
# Good: "Explain in 2-3 sentences, then provide a code example"

# ❌ ANTI-PATTERN 4: Relying on model for real-time facts
# Bad: "What's the current stock price of Apple?"
# Good: Use tools/APIs for real-time data, model for reasoning

# ❌ ANTI-PATTERN 5: No validation of output
# Bad: Trust model output blindly
# Good: Parse JSON with try/except, validate format, check constraints

# ❌ ANTI-PATTERN 6: Prompt injection vulnerability
# Bad: Directly inserting user input into system prompt
# Good: Clear delimiters, input validation, separate user input from instructions

# Handling failures gracefully:
def robust_llm_call(prompt, retries=3):
    for attempt in range(retries):
        response = get_llm_response(prompt)
        parsed = try_parse(response)
        if parsed and validate(parsed):
            return parsed
        # Retry with more specific instructions
        prompt += "\n\nIMPORTANT: Return ONLY valid JSON. No explanation."
    return None  # Fallback
```

---

## 7. Evaluation and Iteration

```python
# Track prompt performance
class PromptEvaluator:
    def __init__(self):
        self.test_cases = [
            {"input": "I love this!", "expected": "positive"},
            {"input": "Terrible product.", "expected": "negative"},
            {"input": "It's okay.", "expected": "neutral"},
        ]
    
    def evaluate_prompt(self, prompt_template: str) -> dict:
        correct = 0
        results = []
        
        for case in self.test_cases:
            prompt = prompt_template.format(text=case["input"])
            output = get_llm_response(prompt)
            is_correct = case["expected"].lower() in output.lower()
            correct += is_correct
            results.append({
                "input": case["input"],
                "expected": case["expected"],
                "got": output,
                "correct": is_correct,
            })
        
        return {
            "accuracy": correct / len(self.test_cases),
            "results": results,
        }

# A/B test prompts
# Version A: "Classify sentiment as positive/negative/neutral"
# Version B: "Rate the emotional tone: positive (happy/excited), negative (angry/sad), neutral (factual/indifferent)"
# Measure: accuracy on test set, consistency, edge case handling
```

---

## Interview Questions

### Beginner
1. **What is few-shot prompting?** Provide 2-5 examples of the desired input→output pattern in the prompt. Model learns the task from examples without any fine-tuning. More effective than zero-shot for specific formats or edge cases.
2. **What is chain-of-thought prompting?** Ask the model to show its reasoning step-by-step before giving the final answer. Significantly improves math, logic, and multi-step reasoning. Simple version: add "Let's think step by step."
3. **Why is temperature important?** Controls randomness. Temperature=0: deterministic, best for factual/coding tasks. Temperature=0.7-1.0: creative, varied outputs. Higher temperature = more diverse but potentially less accurate.

### Intermediate
4. **Explain the ReAct pattern.** Model alternates between Thought (reasoning about what to do) and Action (calling a tool). After observing the result, it reasons about next step. Enables multi-step problem solving with tool use. Foundation for AI agents.
5. **How do you prevent prompt injection?** Separate user input from instructions (delimiters), validate/sanitize input, use system messages (harder to override), monitor for injection patterns, limit model capabilities, never trust LLM output for security decisions.
6. **How do you evaluate prompt quality systematically?** Create test suite (20+ examples with expected outputs). Measure: accuracy, consistency (same input → same output), format compliance, edge case handling. A/B test variants. Track metrics over time.

### Advanced
7. **How do you optimize prompts for production?** Start with clarity and examples. Benchmark against test suite. Reduce token count (shorter prompts = faster + cheaper). Cache common responses. Use structured outputs for reliable parsing. Version control prompts. Monitor production accuracy.
8. **Design a prompt for complex multi-step data analysis.** Break into stages: 1) Understand the data (schema analysis prompt), 2) Generate hypotheses (exploration prompt), 3) Write analysis code (code gen prompt with schema context), 4) Interpret results (explanation prompt). Chain outputs between stages.
9. **When should you fine-tune vs optimize prompts?** Prompt engineering first (faster, cheaper, no data needed). Fine-tune when: consistent format needed at scale (cheaper per-call), domain-specific knowledge, need to reduce prompt size (cost), specific style/behavior hard to describe.

---

## Hands-On Exercise
1. Write zero-shot, few-shot, and CoT prompts for a math problem — compare accuracy
2. Design a system prompt for a code review assistant
3. Implement self-consistency (5 samples, majority vote) — measure improvement
4. Build a ReAct loop with 2-3 mock tools
5. Create a prompt evaluation test suite (10+ cases)
6. Find and fix 3 prompt injection vulnerabilities in example prompts
