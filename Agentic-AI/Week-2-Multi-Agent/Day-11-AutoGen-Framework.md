# Day 11: AutoGen Framework

## Learning Objectives
- Understand AutoGen's conversable agent architecture
- Build AssistantAgent and UserProxyAgent interactions
- Implement group chat with multiple agents
- Configure code execution safely
- Use nested conversations and custom reply functions

---

## 1. AutoGen Architecture

```python
# AutoGen: Microsoft's framework for multi-agent conversations
# Core idea: Agents converse with each other to solve problems
# Key agents: AssistantAgent (LLM), UserProxyAgent (human/code execution)

import autogen

# Configuration for LLM
config_list = [
    {"model": "gpt-4o", "api_key": "your-key"},
]

llm_config = {
    "config_list": config_list,
    "temperature": 0,
    "timeout": 120,
}

# AssistantAgent: LLM-powered, generates responses
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config=llm_config,
    system_message="""You are a helpful AI assistant. Solve tasks step by step.
    When you need to write code, write it in Python code blocks.
    When the task is done, reply with TERMINATE.""",
)

# UserProxyAgent: Executes code, can ask human for input
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",  # NEVER, ALWAYS, TERMINATE
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "coding",
        "use_docker": True,  # Safer code execution
    },
)

# Start conversation
user_proxy.initiate_chat(
    assistant,
    message="Write a Python script that fetches top HN stories and saves to CSV.",
)
```

---

## 2. Agent Types and Configuration

```python
# Different human_input_mode options:
# NEVER: Fully autonomous (agent decides everything)
# ALWAYS: Always asks human before responding
# TERMINATE: Only asks when termination condition met

# Custom AssistantAgent with specific role
coder = autogen.AssistantAgent(
    name="coder",
    llm_config=llm_config,
    system_message="""You are an expert Python programmer. Write clean, 
    efficient code. Always include error handling and type hints.
    Use code blocks for all code. End with TERMINATE when done.""",
)

reviewer = autogen.AssistantAgent(
    name="reviewer",
    llm_config=llm_config,
    system_message="""You are a code reviewer. Review code for:
    - Bugs and logic errors
    - Security vulnerabilities  
    - Performance issues
    - Style and readability
    Provide specific, actionable feedback. Say APPROVE if code is good.""",
)

# Agent with custom termination
planner = autogen.AssistantAgent(
    name="planner",
    llm_config=llm_config,
    system_message="You plan tasks. Output a numbered plan. Reply TERMINATE when plan is complete.",
    is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
)
```

---

## 3. Group Chat

```python
# GroupChat: Multiple agents discuss together
# GroupChatManager: Decides who speaks next

coder = autogen.AssistantAgent(name="Coder", llm_config=llm_config,
    system_message="You write Python code. Use code blocks.")

reviewer = autogen.AssistantAgent(name="Reviewer", llm_config=llm_config,
    system_message="You review code for bugs and improvements.")

tester = autogen.AssistantAgent(name="Tester", llm_config=llm_config,
    system_message="You write unit tests for the code.")

executor = autogen.UserProxyAgent(name="Executor",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "workspace", "use_docker": True},
)

# Create group chat
groupchat = autogen.GroupChat(
    agents=[coder, reviewer, tester, executor],
    messages=[],
    max_round=12,
    speaker_selection_method="auto",  # LLM decides who speaks next
    # Other options: "round_robin", "random", or custom function
)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config=llm_config,
)

# Start the group discussion
executor.initiate_chat(
    manager,
    message="Create a REST API endpoint for user registration with validation.",
)

# Custom speaker selection
def custom_speaker(last_speaker, groupchat):
    """Custom logic for who speaks next."""
    messages = groupchat.messages
    if last_speaker is coder:
        return reviewer  # Always review after coding
    elif last_speaker is reviewer:
        if "APPROVE" in messages[-1]["content"]:
            return tester
        return coder  # Back to coder for fixes
    elif last_speaker is tester:
        return executor  # Run the tests
    return coder

groupchat_custom = autogen.GroupChat(
    agents=[coder, reviewer, tester, executor],
    messages=[],
    max_round=12,
    speaker_selection_method=custom_speaker,
)
```

---

## 4. Code Execution

```python
# Safe code execution with Docker
executor = autogen.UserProxyAgent(
    name="executor",
    code_execution_config={
        "work_dir": "coding_workspace",
        "use_docker": "python:3.11-slim",  # Specific image
        "timeout": 60,  # Kill after 60 seconds
        "last_n_messages": 3,  # Only execute from recent messages
    },
    human_input_mode="NEVER",
)

# Without Docker (less safe, but simpler for development)
local_executor = autogen.UserProxyAgent(
    name="local_executor",
    code_execution_config={
        "work_dir": "workspace",
        "use_docker": False,
        "timeout": 30,
    },
    human_input_mode="NEVER",
)

# Code execution flow:
# 1. AssistantAgent writes code in ```python block
# 2. UserProxyAgent detects code block
# 3. Executes in Docker/local environment
# 4. Returns stdout/stderr to AssistantAgent
# 5. AssistantAgent reads output, fixes if needed
```

---

## 5. Nested Conversations

```python
# Nested conversations: Agent triggers sub-conversations as tools

# Define a nested chat that an agent can trigger
def research_chat(query):
    """Sub-conversation for research."""
    researcher = autogen.AssistantAgent(
        name="researcher", llm_config=llm_config,
        system_message="Research the given topic thoroughly.",
    )
    proxy = autogen.UserProxyAgent(name="research_proxy", human_input_mode="NEVER",
        max_consecutive_auto_reply=3,
        is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""))
    
    proxy.initiate_chat(researcher, message=query)
    return proxy.last_message()["content"]

# Register nested chat with an agent
main_assistant = autogen.AssistantAgent(
    name="main_assistant", llm_config=llm_config,
)

# Register a nested chat trigger
main_assistant.register_nested_chats(
    [
        {
            "recipient": autogen.AssistantAgent(name="math_expert", llm_config=llm_config,
                system_message="You solve math problems step by step."),
            "message": lambda recipient, messages, sender, config: messages[-1]["content"],
            "max_turns": 3,
            "summary_method": "last_msg",
        }
    ],
    trigger=lambda sender: "math" in sender.last_message().get("content", "").lower(),
)
```

---

## 6. Custom Reply Functions

```python
# Register custom reply functions for fine-grained control

assistant = autogen.AssistantAgent(name="assistant", llm_config=llm_config)

# Custom function that intercepts before LLM call
def check_budget(recipient, messages, sender, config):
    """Check token budget before allowing LLM call."""
    total_tokens = sum(len(m.get("content", "")) // 4 for m in messages)
    if total_tokens > 50000:
        return True, "Budget exceeded. Summarizing and stopping. TERMINATE"
    return False, None  # Continue with normal flow

assistant.register_reply(
    trigger=autogen.Agent,  # Trigger for all senders
    reply_func=check_budget,
    position=0,  # Check before other reply methods
)

# Tool-use pattern with function calling
from typing import Annotated

def search_web(query: Annotated[str, "Search query"]) -> str:
    """Search the web for information."""
    # Implementation
    return f"Results for: {query}"

def calculate(expression: Annotated[str, "Math expression"]) -> str:
    """Evaluate a mathematical expression."""
    return str(eval(expression))  # In production: use safe eval

# Register functions as tools
autogen.register_function(
    search_web,
    caller=assistant,
    executor=user_proxy,
    description="Search the web for information",
)

autogen.register_function(
    calculate,
    caller=assistant,
    executor=user_proxy,
    description="Calculate a math expression",
)
```

---

## Interview Questions

### Beginner
1. **What are the two main agent types in AutoGen?** AssistantAgent: LLM-powered, generates responses and code. UserProxyAgent: can execute code, proxy human input, manage termination. They converse back and forth until termination condition is met.
2. **What does human_input_mode control?** NEVER: fully autonomous, no human involvement. ALWAYS: asks human before every reply. TERMINATE: asks human only when termination condition met. Determines level of human oversight in agent conversations.
3. **How does code execution work in AutoGen?** AssistantAgent writes code in markdown code blocks. UserProxyAgent detects these blocks and executes them (in Docker or locally). Output (stdout/stderr) is sent back to AssistantAgent. Agent can iterate: fix code based on errors.

### Intermediate
4. **How does GroupChat decide who speaks next?** speaker_selection_method options: "auto" (LLM decides based on context), "round_robin" (sequential), "random", or custom function. Custom function receives last_speaker and groupchat, returns next agent. Enables complex workflow patterns.
5. **When would you use nested conversations?** When an agent needs specialist help for sub-problems. Example: main agent encounters math → triggers math expert sub-chat. Keeps conversations focused. Sub-chat result summarized and returned to parent. Avoids polluting main conversation with specialist details.
6. **How do you ensure safe code execution in production?** Use Docker containers (sandboxed), set timeouts (prevent infinite loops), limit disk/network access, whitelist packages, review code before execution (human_input_mode="ALWAYS" for sensitive ops), limit last_n_messages to reduce injection risk.

### Advanced
7. **Design a multi-agent coding system with AutoGen for production.** Agents: Planner (breaks task into steps), Coder (writes code), Reviewer (checks quality), Tester (writes/runs tests), Executor (Docker sandbox). GroupChat with custom speaker selection: Planner first → Coder → Reviewer → (loop if issues) → Tester → Executor. Add: token budget check, output validation, human approval for deployment.
8. **Compare AutoGen's approach to CrewAI and LangGraph.** AutoGen: conversation-centric, agents chat freely, good for collaborative problem-solving. CrewAI: role-playing focus, structured tasks, simpler mental model. LangGraph: state machine, explicit control flow, most flexible. AutoGen best for: iterative code generation, research discussions.
9. **How do you handle failures and infinite loops in AutoGen group chats?** max_round limit on GroupChat. max_consecutive_auto_reply on agents. Termination messages ("TERMINATE", "APPROVE"). Custom reply functions to check budget/time. Monitor conversation for repetition (same content repeating). Timeout per agent turn. Fallback: if stuck, inject human guidance.

---

## Hands-On Exercise
1. Create a two-agent system (AssistantAgent + UserProxyAgent) for coding tasks
2. Set up safe code execution with Docker and timeouts
3. Build a group chat with Coder, Reviewer, and Tester agents
4. Implement custom speaker selection (always review after coding)
5. Register a function as a tool for the assistant
6. Add nested conversation for a specialist sub-task
