#!/usr/bin/env python3
"""Day 26 - OpenAI API Integration"""

print("=" * 50)
print("OPENAI API INTEGRATION")
print("=" * 50)


# ============================================
# 1. BASIC SETUP
# ============================================
print("\n--- 1. Basic Setup ---")

SETUP = """
# Install: pip install openai

from openai import OpenAI
import os

# Option 1: Set API key in environment
# export OPENAI_API_KEY='your-key'
client = OpenAI()  # Reads from OPENAI_API_KEY env var

# Option 2: Direct initialization
client = OpenAI(api_key="your-api-key")

# Option 3: Using .env file
from dotenv import load_dotenv
load_dotenv()
client = OpenAI()
"""
print(SETUP)


# ============================================
# 2. CHAT COMPLETIONS
# ============================================
print("\n--- 2. Chat Completions ---")

CHAT_COMPLETIONS = """
from openai import OpenAI
client = OpenAI()

# Basic chat completion
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"}
    ]
)

# Access the response
message = response.choices[0].message.content
print(message)

# With parameters
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Write a haiku"}],
    temperature=0.7,        # Creativity (0-2)
    max_tokens=100,         # Max response length
    top_p=1.0,              # Nucleus sampling
    frequency_penalty=0.0,  # Reduce repetition
    presence_penalty=0.0,   # Encourage new topics
)
"""
print(CHAT_COMPLETIONS)


# ============================================
# 3. STREAMING RESPONSES
# ============================================
print("\n--- 3. Streaming Responses ---")

STREAMING = """
from openai import OpenAI
client = OpenAI()

# Stream the response
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

# Process chunks as they arrive
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
"""
print(STREAMING)


# ============================================
# 4. FUNCTION CALLING
# ============================================
print("\n--- 4. Function Calling ---")

FUNCTION_CALLING = """
from openai import OpenAI
import json

client = OpenAI()

# Define available functions
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"]
                    }
                },
                "required": ["location"]
            }
        }
    }
]

# Call with tools
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in NYC?"}],
    tools=tools,
    tool_choice="auto"
)

# Check if function was called
message = response.choices[0].message
if message.tool_calls:
    tool_call = message.tool_calls[0]
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    print(f"Call {function_name} with {arguments}")
"""
print(FUNCTION_CALLING)


# ============================================
# 5. EMBEDDINGS
# ============================================
print("\n--- 5. Embeddings ---")

EMBEDDINGS = """
from openai import OpenAI
import numpy as np

client = OpenAI()

# Create embedding
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Python is a programming language"
)

embedding = response.data[0].embedding
print(f"Embedding dimension: {len(embedding)}")  # 1536

# Compare similarity
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Batch embeddings
texts = ["Python", "JavaScript", "Cooking"]
response = client.embeddings.create(
    model="text-embedding-3-small",
    input=texts
)
embeddings = [e.embedding for e in response.data]
"""
print(EMBEDDINGS)


# ============================================
# 6. VISION (GPT-4 Vision)
# ============================================
print("\n--- 6. Vision API ---")

VISION = """
from openai import OpenAI
import base64

client = OpenAI()

# From URL
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {
                    "type": "image_url",
                    "image_url": {"url": "https://example.com/image.jpg"}
                }
            ]
        }
    ]
)

# From base64
def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

base64_image = encode_image("image.jpg")
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
)
"""
print(VISION)


# ============================================
# 7. ASSISTANT API
# ============================================
print("\n--- 7. Assistants API ---")

ASSISTANTS = """
from openai import OpenAI
client = OpenAI()

# Create an assistant
assistant = client.beta.assistants.create(
    name="Python Tutor",
    instructions="You are a Python programming tutor.",
    model="gpt-4o",
    tools=[{"type": "code_interpreter"}]
)

# Create a thread
thread = client.beta.threads.create()

# Add a message
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="How do I read a CSV file in Python?"
)

# Run the assistant
run = client.beta.threads.runs.create_and_poll(
    thread_id=thread.id,
    assistant_id=assistant.id
)

# Get messages
messages = client.beta.threads.messages.list(thread_id=thread.id)
for msg in messages.data:
    print(f"{msg.role}: {msg.content[0].text.value}")
"""
print(ASSISTANTS)


# ============================================
# 8. ERROR HANDLING
# ============================================
print("\n--- 8. Error Handling ---")

ERROR_HANDLING = """
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
import time

client = OpenAI()

def chat_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            return response.choices[0].message.content
            
        except RateLimitError:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            
        except APIConnectionError:
            print("Connection error. Retrying...")
            time.sleep(1)
            
        except APIError as e:
            print(f"API error: {e}")
            raise
    
    raise Exception("Max retries exceeded")
"""
print(ERROR_HANDLING)


# ============================================
# 9. BEST PRACTICES
# ============================================
print("\n--- 9. Best Practices ---")

BEST_PRACTICES = """
Best Practices for OpenAI API:
─────────────────────────────────────────────

1. API Key Security:
   - Never hardcode API keys
   - Use environment variables
   - Use .env files with .gitignore

2. Cost Management:
   - Set usage limits in OpenAI dashboard
   - Use cheaper models for simple tasks
   - Cache responses when possible
   - Limit max_tokens appropriately

3. Error Handling:
   - Always handle rate limits
   - Implement exponential backoff
   - Log errors for debugging

4. Prompt Engineering:
   - Be specific in system prompts
   - Use few-shot examples
   - Set clear output formats

5. Performance:
   - Use streaming for long responses
   - Batch requests when possible
   - Use async for parallel calls

6. Testing:
   - Mock API calls in tests
   - Test with different temperatures
   - Validate response formats
"""
print(BEST_PRACTICES)


# ============================================
# DEMONSTRATION
# ============================================
print("\n" + "=" * 50)
print("SAMPLE INTEGRATION")
print("=" * 50)

SAMPLE_CODE = """
# Complete example: AI-powered text summarizer

from openai import OpenAI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()
client = OpenAI()

class SummarizeRequest(BaseModel):
    text: str
    max_length: int = 100

class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int

@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Cheaper model
            messages=[
                {
                    "role": "system",
                    "content": f"Summarize the following text in {request.max_length} words or less."
                },
                {"role": "user", "content": request.text}
            ],
            max_tokens=150
        )
        
        summary = response.choices[0].message.content
        
        return SummarizeResponse(
            summary=summary,
            original_length=len(request.text.split()),
            summary_length=len(summary.split())
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""
print(SAMPLE_CODE)
