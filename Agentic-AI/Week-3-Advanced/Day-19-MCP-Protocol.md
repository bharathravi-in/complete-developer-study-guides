# Day 19: MCP (Model Context Protocol)

## Overview
MCP is an open protocol that standardizes how AI applications connect to external tools and data sources. Build once, use with any MCP-compatible AI client.

---

## 1. What is MCP?

### The Problem MCP Solves
```
Before MCP:
├── ChatGPT → Custom plugin format
├── Claude → Custom tool format  
├── VS Code Copilot → Custom extension
├── Your App → Custom integration
└── Each AI client needs bespoke integrations! (N × M problem)

With MCP:
├── MCP Server (tool provider) → Standard protocol
├── Any MCP Client can use any MCP Server
└── Build once, work everywhere (N + M problem)
```

### Architecture
```
┌──────────────────┐         ┌──────────────────┐
│   MCP CLIENT     │  JSON   │   MCP SERVER     │
│ (AI Application) │◄───────▶│ (Tool Provider)  │
│                  │  RPC    │                  │
│  - Claude        │         │  - File System   │
│  - VS Code       │         │  - Database      │
│  - Custom App    │         │  - Web Search    │
│                  │         │  - GitHub API    │
└──────────────────┘         └──────────────────┘
```

### Key Concepts
| Concept | Description |
|---------|-------------|
| **Server** | Provides tools, resources, and prompts |
| **Client** | AI application that connects to servers |
| **Tool** | Executable function (like API endpoint) |
| **Resource** | Data source (like a file or database query) |
| **Prompt** | Pre-built prompt templates |
| **Transport** | Communication layer (stdio, HTTP/SSE) |

---

## 2. Building an MCP Server

### Basic Server (Python)
```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import json

# Create server
server = Server("my-tools-server")

# Define tools
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_weather",
            description="Get current weather for a city",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    },
                    "units": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "default": "celsius"
                    }
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="search_database",
            description="Search the product database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            }
        ),
    ]

# Handle tool execution
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_weather":
        city = arguments["city"]
        units = arguments.get("units", "celsius")
        
        # Your actual implementation
        weather_data = await fetch_weather(city, units)
        
        return [TextContent(
            type="text",
            text=json.dumps(weather_data)
        )]
    
    elif name == "search_database":
        results = await db_search(
            arguments["query"], 
            arguments.get("limit", 10)
        )
        return [TextContent(
            type="text", 
            text=json.dumps(results)
        )]
    
    raise ValueError(f"Unknown tool: {name}")

# Run server
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## 3. Resources (Data Sources)

```python
from mcp.types import Resource, TextContent

@server.list_resources()
async def list_resources():
    return [
        Resource(
            uri="db://customers/schema",
            name="Customer Database Schema",
            description="Schema definition for the customers table",
            mimeType="application/json"
        ),
        Resource(
            uri="file://docs/api-reference",
            name="API Reference Documentation",
            description="Complete API reference",
            mimeType="text/markdown"
        ),
    ]

@server.read_resource()
async def read_resource(uri: str):
    if uri == "db://customers/schema":
        schema = get_db_schema("customers")
        return TextContent(type="text", text=json.dumps(schema))
    
    elif uri == "file://docs/api-reference":
        content = read_file("docs/api-reference.md")
        return TextContent(type="text", text=content)
    
    raise ValueError(f"Unknown resource: {uri}")
```

---

## 4. Prompts (Templates)

```python
from mcp.types import Prompt, PromptArgument, PromptMessage

@server.list_prompts()
async def list_prompts():
    return [
        Prompt(
            name="analyze_code",
            description="Analyze code for bugs, performance, and best practices",
            arguments=[
                PromptArgument(
                    name="code",
                    description="The code to analyze",
                    required=True
                ),
                PromptArgument(
                    name="language",
                    description="Programming language",
                    required=True
                ),
                PromptArgument(
                    name="focus",
                    description="What to focus on (security, performance, style)",
                    required=False
                )
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict):
    if name == "analyze_code":
        focus = arguments.get("focus", "all aspects")
        return [
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text=f"""Analyze this {arguments['language']} code focusing on {focus}:

```{arguments['language']}
{arguments['code']}
```

Provide:
1. Bug identification
2. Performance issues
3. Security concerns
4. Suggested improvements"""
                )
            )
        ]
```

---

## 5. Real-World MCP Server: Database Agent

```python
"""
MCP Server that provides database query tools
"""
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, Resource
import asyncpg
import json

server = Server("database-agent")

# Connection pool
pool = None

async def get_pool():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            "postgresql://user:pass@localhost/mydb",
            min_size=2, max_size=10
        )
    return pool

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="query_database",
            description="Execute a READ-ONLY SQL query against the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL query (SELECT only)"
                    },
                    "params": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Query parameters"
                    }
                },
                "required": ["sql"]
            }
        ),
        Tool(
            name="describe_table",
            description="Get schema information for a database table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string"}
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="list_tables",
            description="List all tables in the database",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    db = await get_pool()
    
    if name == "query_database":
        sql = arguments["sql"].strip()
        
        # SECURITY: Only allow SELECT queries
        if not sql.upper().startswith("SELECT"):
            return [TextContent(
                type="text",
                text="Error: Only SELECT queries are allowed"
            )]
        
        # SECURITY: Prevent dangerous operations
        dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "EXEC"]
        if any(word in sql.upper() for word in dangerous):
            return [TextContent(
                type="text",
                text="Error: Query contains forbidden operations"
            )]
        
        try:
            rows = await db.fetch(sql, *(arguments.get("params", [])))
            result = [dict(row) for row in rows[:100]]  # Limit results
            return [TextContent(type="text", text=json.dumps(result, default=str))]
        except Exception as e:
            return [TextContent(type="text", text=f"Query error: {str(e)}")]
    
    elif name == "describe_table":
        table = arguments["table_name"]
        # Parameterized to prevent injection
        schema = await db.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = $1
            ORDER BY ordinal_position
        """, table)
        return [TextContent(type="text", text=json.dumps([dict(r) for r in schema]))]
    
    elif name == "list_tables":
        tables = await db.fetch("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        return [TextContent(
            type="text", 
            text=json.dumps([r['table_name'] for r in tables])
        )]

@server.list_resources()
async def list_resources():
    db = await get_pool()
    tables = await db.fetch(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    )
    return [
        Resource(
            uri=f"db://schema/{t['table_name']}",
            name=f"{t['table_name']} schema",
            mimeType="application/json"
        )
        for t in tables
    ]
```

---

## 6. Client Integration

### Configuration (claude_desktop_config.json)
```json
{
    "mcpServers": {
        "database": {
            "command": "python",
            "args": ["/path/to/database_server.py"],
            "env": {
                "DATABASE_URL": "postgresql://user:pass@localhost/mydb"
            }
        },
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/projects"]
        },
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {
                "GITHUB_TOKEN": "ghp_..."
            }
        }
    }
}
```

### Using MCP in Your Agent
```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def create_mcp_agent():
    """Connect to MCP server and use its tools"""
    
    server_params = StdioServerParameters(
        command="python",
        args=["database_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")
            
            # Call a tool
            result = await session.call_tool(
                "list_tables",
                arguments={}
            )
            print(f"Tables: {result.content[0].text}")
            
            # Use with LangChain
            # Convert MCP tools to LangChain tools format
            langchain_tools = mcp_to_langchain_tools(tools.tools, session)
            
            # Now use in agent
            agent = create_agent(llm, langchain_tools)
```

---

## 7. Building a Production MCP Server

### Package Structure
```
my-mcp-server/
├── pyproject.toml
├── src/
│   └── my_mcp_server/
│       ├── __init__.py
│       ├── server.py
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── database.py
│       │   └── search.py
│       └── config.py
├── tests/
│   └── test_tools.py
└── README.md
```

### pyproject.toml
```toml
[project]
name = "my-mcp-server"
version = "0.1.0"
dependencies = ["mcp>=1.0.0", "asyncpg>=0.29.0"]

[project.scripts]
my-mcp-server = "my_mcp_server.server:main"
```

### Testing MCP Tools
```python
import pytest
from my_mcp_server.server import call_tool

@pytest.mark.asyncio
async def test_list_tables():
    result = await call_tool("list_tables", {})
    assert result[0].type == "text"
    tables = json.loads(result[0].text)
    assert isinstance(tables, list)

@pytest.mark.asyncio
async def test_query_rejects_mutations():
    result = await call_tool("query_database", {"sql": "DROP TABLE users"})
    assert "Error" in result[0].text
    assert "forbidden" in result[0].text.lower()
```

---

## Key Takeaways
- MCP standardizes AI tool connections (build once, use everywhere)
- Servers expose Tools (functions), Resources (data), and Prompts (templates)
- Always validate/sanitize inputs in tool handlers (security!)
- Use stdio transport for local tools, HTTP/SSE for remote services
- Test tool implementations independently from the AI client
- MCP enables composable AI systems (mix and match capabilities)

## Tomorrow
**Day 20**: Agent Evaluation & Testing — Measuring agent performance, trajectory evaluation, and building test suites.
