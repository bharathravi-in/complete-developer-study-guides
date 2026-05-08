# Day 20: Tool Building

## Learning Objectives
- Design effective tool interfaces for agents
- Implement dynamic tool discovery and registration
- Build tools from OpenAPI specifications
- Create tool registries with metadata
- Handle authentication and testing for tools

---

## 1. Designing Tool Interfaces

```python
# Good tool design principles:
# 1. Clear name and description (agent must understand from text alone)
# 2. Well-defined inputs with types and descriptions
# 3. Predictable outputs (structured, consistent format)
# 4. Error messages that help the agent recover
# 5. Single responsibility (one tool = one action)

from pydantic import BaseModel, Field
from typing import Any

class ToolDefinition(BaseModel):
    """Standard tool interface."""
    name: str = Field(description="Snake_case name, verb_noun format")
    description: str = Field(description="What this tool does and WHEN to use it")
    parameters: dict = Field(description="JSON Schema for input parameters")
    returns: str = Field(description="What the tool returns")
    examples: list[dict] = Field(default=[], description="Example usage")
    
# Good example:
search_tool = ToolDefinition(
    name="search_documents",
    description="Search the internal knowledge base for documents matching a query. Use when the user asks about company policies, procedures, or internal information.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Natural language search query"},
            "max_results": {"type": "integer", "description": "Maximum results to return", "default": 5},
            "filter_type": {"type": "string", "enum": ["policy", "procedure", "faq", "all"], "default": "all"},
        },
        "required": ["query"],
    },
    returns="List of matching documents with title, snippet, and relevance score",
    examples=[{"query": "vacation policy", "max_results": 3}],
)

# Bad example (too vague):
# name="search", description="searches things", parameters={"q": "string"}
```

---

## 2. Tool Implementation Pattern

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
import json

@dataclass
class ToolResult:
    success: bool
    data: Any
    error: str | None = None
    
    def to_string(self) -> str:
        if self.success:
            return json.dumps(self.data) if isinstance(self.data, (dict, list)) else str(self.data)
        return f"Error: {self.error}"

class BaseTool(ABC):
    """Base class for all tools."""
    
    @property
    @abstractmethod
    def name(self) -> str: ...
    
    @property
    @abstractmethod
    def description(self) -> str: ...
    
    @property
    @abstractmethod
    def parameters_schema(self) -> dict: ...
    
    @abstractmethod
    def execute(self, **kwargs) -> ToolResult: ...
    
    def validate_inputs(self, kwargs: dict) -> tuple[bool, str]:
        """Validate inputs against schema."""
        required = self.parameters_schema.get("required", [])
        for field in required:
            if field not in kwargs:
                return False, f"Missing required parameter: {field}"
        return True, ""
    
    def safe_execute(self, **kwargs) -> ToolResult:
        """Execute with validation and error handling."""
        valid, error = self.validate_inputs(kwargs)
        if not valid:
            return ToolResult(success=False, data=None, error=error)
        try:
            return self.execute(**kwargs)
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))

# Example implementation
class DatabaseQueryTool(BaseTool):
    name = "query_database"
    description = "Execute a read-only SQL query against the analytics database. Use for data lookups and aggregations."
    parameters_schema = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "SQL SELECT query (read-only)"},
            "limit": {"type": "integer", "description": "Max rows to return", "default": 100},
        },
        "required": ["query"],
    }
    
    def __init__(self, connection_string: str):
        self.conn_str = connection_string
    
    def execute(self, query: str, limit: int = 100) -> ToolResult:
        # Safety: block non-SELECT queries
        if not query.strip().upper().startswith("SELECT"):
            return ToolResult(success=False, data=None, error="Only SELECT queries allowed")
        
        # Add LIMIT if not present
        if "LIMIT" not in query.upper():
            query = f"{query} LIMIT {limit}"
        
        # Execute (pseudo-code)
        # results = db.execute(query)
        results = [{"id": 1, "name": "example"}]  # Placeholder
        return ToolResult(success=True, data=results)
```

---

## 3. Dynamic Tool Discovery

```python
class ToolRegistry:
    """Registry for dynamic tool discovery and management."""
    
    def __init__(self):
        self.tools: dict[str, BaseTool] = {}
        self.metadata: dict[str, dict] = {}
    
    def register(self, tool: BaseTool, tags: list[str] = None, version: str = "1.0"):
        """Register a tool with metadata."""
        self.tools[tool.name] = tool
        self.metadata[tool.name] = {
            "tags": tags or [],
            "version": version,
            "description": tool.description,
            "parameters": tool.parameters_schema,
        }
    
    def discover(self, query: str) -> list[BaseTool]:
        """Find relevant tools based on natural language query."""
        # Simple keyword matching (in production: use embeddings)
        results = []
        query_lower = query.lower()
        for name, meta in self.metadata.items():
            score = 0
            if any(tag in query_lower for tag in meta["tags"]):
                score += 2
            if any(word in meta["description"].lower() for word in query_lower.split()):
                score += 1
            if score > 0:
                results.append((score, self.tools[name]))
        
        return [tool for _, tool in sorted(results, key=lambda x: -x[0])]
    
    def get_openai_tools(self, tool_names: list[str] = None) -> list[dict]:
        """Convert tools to OpenAI function calling format."""
        tools = tool_names or list(self.tools.keys())
        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": self.tools[name].description,
                    "parameters": self.tools[name].parameters_schema,
                },
            }
            for name in tools if name in self.tools
        ]
    
    def execute(self, tool_name: str, arguments: dict) -> ToolResult:
        """Execute a registered tool by name."""
        if tool_name not in self.tools:
            return ToolResult(success=False, data=None, error=f"Tool '{tool_name}' not found")
        return self.tools[tool_name].safe_execute(**arguments)

# Usage
registry = ToolRegistry()
registry.register(DatabaseQueryTool("postgres://..."), tags=["database", "sql", "analytics"])
```

---

## 4. Building Tools from OpenAPI Specs

```python
import yaml
import httpx

class OpenAPIToolBuilder:
    """Automatically create tools from OpenAPI/Swagger specifications."""
    
    def __init__(self, spec_url: str, base_url: str, api_key: str = None):
        self.spec = self._load_spec(spec_url)
        self.base_url = base_url
        self.api_key = api_key
    
    def _load_spec(self, url: str) -> dict:
        if url.startswith("http"):
            response = httpx.get(url)
            return yaml.safe_load(response.text)
        with open(url) as f:
            return yaml.safe_load(f)
    
    def build_tools(self) -> list[BaseTool]:
        """Generate tool classes from each endpoint."""
        tools = []
        for path, methods in self.spec.get("paths", {}).items():
            for method, details in methods.items():
                if method in ("get", "post", "put", "delete"):
                    tool = self._create_tool(path, method, details)
                    tools.append(tool)
        return tools
    
    def _create_tool(self, path: str, method: str, details: dict) -> BaseTool:
        """Create a tool from an API endpoint definition."""
        operation_id = details.get("operationId", f"{method}_{path.replace('/', '_')}")
        description = details.get("summary", details.get("description", f"{method.upper()} {path}"))
        
        # Build parameters schema from spec
        params_schema = self._build_params_schema(details)
        
        # Create dynamic tool class
        base_url = self.base_url
        api_key = self.api_key
        
        class DynamicAPITool(BaseTool):
            name = operation_id
            description = description
            parameters_schema = params_schema
            
            def execute(self, **kwargs) -> ToolResult:
                url = f"{base_url}{path}"
                # Replace path parameters
                for key, value in kwargs.items():
                    url = url.replace(f"{{{key}}}", str(value))
                
                headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
                
                try:
                    if method == "get":
                        resp = httpx.get(url, params=kwargs, headers=headers, timeout=30)
                    else:
                        resp = httpx.request(method, url, json=kwargs, headers=headers, timeout=30)
                    
                    resp.raise_for_status()
                    return ToolResult(success=True, data=resp.json())
                except Exception as e:
                    return ToolResult(success=False, data=None, error=str(e))
        
        return DynamicAPITool()
    
    def _build_params_schema(self, details: dict) -> dict:
        """Extract parameter schema from OpenAPI endpoint."""
        properties = {}
        required = []
        
        for param in details.get("parameters", []):
            properties[param["name"]] = {
                "type": param.get("schema", {}).get("type", "string"),
                "description": param.get("description", ""),
            }
            if param.get("required"):
                required.append(param["name"])
        
        # Request body
        body = details.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema", {})
        if body:
            properties.update(body.get("properties", {}))
            required.extend(body.get("required", []))
        
        return {"type": "object", "properties": properties, "required": required}
```

---

## 5. Authentication & Security

```python
from enum import Enum

class AuthType(Enum):
    NONE = "none"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC = "basic"

class SecureToolWrapper:
    """Wraps tools with authentication and security controls."""
    
    def __init__(self, tool: BaseTool, auth_type: AuthType, credentials: dict):
        self.tool = tool
        self.auth_type = auth_type
        self.credentials = credentials
        self.rate_limiter = RateLimiter(max_calls=100, period=60)
    
    def execute(self, **kwargs) -> ToolResult:
        # Rate limiting
        if not self.rate_limiter.allow():
            return ToolResult(success=False, data=None, error="Rate limit exceeded")
        
        # Input sanitization
        sanitized = self._sanitize_inputs(kwargs)
        
        # Execute with auth
        return self.tool.safe_execute(**sanitized)
    
    def _sanitize_inputs(self, kwargs: dict) -> dict:
        """Prevent injection attacks."""
        sanitized = {}
        for key, value in kwargs.items():
            if isinstance(value, str):
                # Remove potential injection patterns
                value = value.replace("\\", "\\\\")
                # Limit length
                value = value[:10000]
            sanitized[key] = value
        return sanitized

class RateLimiter:
    def __init__(self, max_calls: int, period: int):
        self.max_calls = max_calls
        self.period = period
        self.calls: list[float] = []
    
    def allow(self) -> bool:
        import time
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.period]
        if len(self.calls) >= self.max_calls:
            return False
        self.calls.append(now)
        return True
```

---

## 6. Tool Testing

```python
import pytest

class ToolTester:
    """Automated testing for tools."""
    
    def test_tool(self, tool: BaseTool) -> dict:
        """Run standard tests on a tool."""
        results = {
            "schema_valid": self._test_schema(tool),
            "handles_missing_params": self._test_missing_params(tool),
            "handles_invalid_types": self._test_invalid_types(tool),
            "returns_tool_result": self._test_return_type(tool),
            "description_quality": self._test_description(tool),
        }
        results["all_pass"] = all(results.values())
        return results
    
    def _test_schema(self, tool: BaseTool) -> bool:
        schema = tool.parameters_schema
        return "type" in schema and "properties" in schema
    
    def _test_missing_params(self, tool: BaseTool) -> bool:
        result = tool.safe_execute()  # No params
        # Should either work (no required) or return error gracefully
        return isinstance(result, ToolResult)
    
    def _test_invalid_types(self, tool: BaseTool) -> bool:
        result = tool.safe_execute(invalid_param="test")
        return isinstance(result, ToolResult)
    
    def _test_return_type(self, tool: BaseTool) -> bool:
        # Minimal valid call
        return True  # Would need valid inputs
    
    def _test_description(self, tool: BaseTool) -> bool:
        desc = tool.description
        return len(desc) > 20 and len(desc) < 500

# Integration test example
def test_database_tool():
    tool = DatabaseQueryTool("sqlite:///test.db")
    
    # Valid query
    result = tool.safe_execute(query="SELECT 1")
    assert result.success
    
    # Blocked write
    result = tool.safe_execute(query="DELETE FROM users")
    assert not result.success
    assert "SELECT" in result.error
```

---

## Interview Questions

### Beginner
1. **What makes a good tool interface for an agent?** Clear name (verb_noun). Detailed description of WHAT it does and WHEN to use it. Well-typed parameters with descriptions. Consistent output format. Helpful error messages. Single responsibility. Agent selects tools from descriptions alone — clarity is critical.
2. **Why use a tool registry?** Centralized management of all available tools. Dynamic discovery: agent can find relevant tools at runtime. Version control. Metadata (tags, docs, permissions). Easy to add/remove tools without changing agent code. Enables tool composition.
3. **Why do tools need input validation?** Agents can generate invalid inputs (wrong types, missing fields, injection attempts). Validation prevents: crashes, security issues, unexpected behavior. Better: return clear error so agent can fix the input and retry. Always validate at the tool boundary.

### Intermediate
4. **How do you build tools from OpenAPI specifications?** Parse the spec (YAML/JSON). For each endpoint: extract name (operationId), description (summary), parameters (path/query/body), auth requirements. Generate tool class with execute method that makes the HTTP call. Advantage: instant tool library from any documented API.
5. **How do you handle rate limiting and auth for tools?** Wrapper pattern: tool wrapped with auth + rate limiting layer. Token bucket or sliding window for rate limiting. Auth: inject API key/token per request. Per-tool limits (some APIs are stricter). Queue requests when rate limited. Cache responses for repeated calls.
6. **How do you decide which tools to expose to an agent?** Relevance: only tools the agent might need. Security: minimize access (least privilege). Context window: fewer tools = better selection. Dynamic: discover tools based on task type. Too many tools → agent confused, wrong selection. Start small, add tools as needed.

### Advanced
7. **Design a tool system that supports 100+ tools without overwhelming the agent.** Hierarchical: top-level categories → specific tools. Dynamic selection: based on task, load only relevant subset (5-10 tools). Tool router: lightweight model picks which tools are relevant. Caching: remember which tools worked for similar tasks. Pagination: agent can request "more tools like X."
8. **How do you test tools for reliability in production?** Unit tests: each tool with valid/invalid inputs. Integration tests: actual API calls (staging environment). Chaos testing: simulate timeouts, errors, rate limits. Monitor: success rate, latency p50/p95, error types. Contract testing: verify API hasn't changed. Canary: new tool version gets small traffic first.
9. **How would you build a tool marketplace for agents?** Registry with: metadata, docs, ratings, usage stats. Versioning: semantic versioning, backward compatibility. Sandboxing: tools run in isolation. Auth: tool-level permissions. Discovery: search by capability, recommendations. Quality: automated testing before listing. Billing: per-call pricing for premium tools.

---

## Hands-On Exercise
1. Define 5 tools with proper schemas (search, calculate, file_read, http_get, db_query)
2. Implement BaseTool pattern with validation and error handling
3. Build a ToolRegistry with registration and discovery
4. Create tools from a sample OpenAPI spec (e.g., JSONPlaceholder API)
5. Add authentication wrapper and rate limiting
6. Write automated tests for all tools using ToolTester
7. Integrate with OpenAI function calling (convert registry to tools format)
