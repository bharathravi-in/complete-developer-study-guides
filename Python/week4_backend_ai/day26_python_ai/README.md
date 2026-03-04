# Day 26 - Python for AI: NumPy, Pandas & OpenAI

## Topics Covered
- NumPy fundamentals
- Pandas data manipulation
- OpenAI API integration
- LangChain basics
- Building AI-powered features

## AI/ML Python Stack
```
┌─────────────────────────────────────────────┐
│           Application Layer                 │
│    (FastAPI, LangChain, Custom Code)        │
├─────────────────────────────────────────────┤
│           AI/ML Libraries                   │
│  (OpenAI, HuggingFace, LangChain)          │
├─────────────────────────────────────────────┤
│           Data Processing                   │
│       (Pandas, NumPy, Polars)              │
├─────────────────────────────────────────────┤
│           Python Runtime                    │
└─────────────────────────────────────────────┘
```

## Project Structure
```
day26_python_ai/
├── README.md
├── practice.py           # NumPy & Pandas basics
├── numpy_demo.py         # NumPy operations
├── pandas_demo.py        # Pandas data analysis
├── openai_demo.py        # OpenAI API usage
├── langchain_demo.py     # LangChain basics
└── requirements.txt
```

## Key Concepts

### 1. NumPy Arrays
```python
import numpy as np

arr = np.array([1, 2, 3, 4, 5])
matrix = np.zeros((3, 3))
random = np.random.rand(100)

# Vectorized operations
result = arr * 2 + 1
```

### 2. Pandas DataFrames
```python
import pandas as pd

df = pd.DataFrame({
    "name": ["Alice", "Bob"],
    "age": [25, 30]
})

# Operations
filtered = df[df["age"] > 25]
grouped = df.groupby("name").mean()
```

### 3. OpenAI API
```python
from openai import OpenAI

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### 4. LangChain
```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-4")
prompt = ChatPromptTemplate.from_template("Explain {topic}")
chain = prompt | llm
```

## Run
```bash
pip install numpy pandas openai langchain langchain-openai

python practice.py
python numpy_demo.py
python pandas_demo.py
```

## Practice Exercises
1. Analyze a dataset with Pandas
2. Build an AI chatbot with OpenAI
3. Create a RAG pipeline with LangChain
4. Process embeddings with NumPy
5. Build a text summarization API
