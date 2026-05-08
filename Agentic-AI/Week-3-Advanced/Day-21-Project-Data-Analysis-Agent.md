# Day 21: Project — Data Analysis Agent

## Learning Objectives
- Build an agent that analyzes data using SQL and Python
- Implement chart generation and visualization
- Use MCP for database and file system access
- Design multi-turn conversational data exploration
- Handle complex analytical workflows

---

## 1. Architecture

```
┌──────────────────────────────────────────────┐
│              DATA ANALYSIS AGENT              │
├──────────────────────────────────────────────┤
│ Tools:                                        │
│   • SQL Query (read-only, parameterized)     │
│   • Python Executor (pandas, matplotlib)     │
│   • Chart Generator (save to file)           │
│   • File Reader (CSV, JSON, Parquet)         │
│   • Schema Inspector (tables, columns)       │
├──────────────────────────────────────────────┤
│ Capabilities:                                 │
│   • Explore schema → understand data         │
│   • Write queries → extract insights         │
│   • Generate code → transform & visualize    │
│   • Multi-turn → iterative exploration       │
└──────────────────────────────────────────────┘
```

---

## 2. Core Tools

```python
import sqlite3
import subprocess
import tempfile
import os
import json
from openai import OpenAI
from dataclasses import dataclass

client = OpenAI()

@dataclass
class ToolResult:
    success: bool
    data: any
    error: str | None = None

class SQLTool:
    """Execute read-only SQL queries."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def execute(self, query: str) -> ToolResult:
        # Safety: block writes
        normalized = query.strip().upper()
        if any(normalized.startswith(cmd) for cmd in ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"]):
            return ToolResult(success=False, data=None, error="Only SELECT queries allowed")
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query)
            rows = [dict(row) for row in cursor.fetchmany(100)]
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            conn.close()
            return ToolResult(success=True, data={"columns": columns, "rows": rows, "count": len(rows)})
        except Exception as e:
            return ToolResult(success=False, data=None, error=str(e))
    
    def get_schema(self) -> ToolResult:
        """Get database schema."""
        query = """
        SELECT name, sql FROM sqlite_master 
        WHERE type='table' ORDER BY name
        """
        conn = sqlite3.connect(self.db_path)
        tables = conn.execute(query).fetchall()
        schema = []
        for name, sql in tables:
            columns = conn.execute(f"PRAGMA table_info({name})").fetchall()
            schema.append({
                "table": name,
                "columns": [{"name": c[1], "type": c[2], "nullable": not c[3]} for c in columns],
                "row_count": conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0],
            })
        conn.close()
        return ToolResult(success=True, data=schema)

class PythonExecutor:
    """Execute Python code for data analysis."""
    
    def __init__(self, work_dir: str = "/tmp/analysis"):
        self.work_dir = work_dir
        os.makedirs(work_dir, exist_ok=True)
    
    def execute(self, code: str) -> ToolResult:
        """Execute Python code, return stdout."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=self.work_dir, delete=False) as f:
            # Prepend common imports
            full_code = """import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import json
import os
os.chdir('/tmp/analysis')

""" + code
            f.write(full_code)
            f.flush()
            
            try:
                result = subprocess.run(
                    ["python", f.name],
                    capture_output=True, text=True, timeout=30,
                    cwd=self.work_dir,
                )
                os.unlink(f.name)
                
                if result.returncode == 0:
                    return ToolResult(success=True, data=result.stdout)
                return ToolResult(success=False, data=None, error=result.stderr[-500:])
            except subprocess.TimeoutExpired:
                os.unlink(f.name)
                return ToolResult(success=False, data=None, error="Execution timed out (30s)")

class ChartTool:
    """Generate charts and save to files."""
    
    def __init__(self, output_dir: str = "/tmp/analysis/charts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, chart_code: str, filename: str = "chart.png") -> ToolResult:
        """Execute chart generation code."""
        code = f"""import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

{chart_code}

plt.tight_layout()
plt.savefig('{self.output_dir}/{filename}', dpi=150, bbox_inches='tight')
plt.close()
print(f'Chart saved: {self.output_dir}/{filename}')
"""
        executor = PythonExecutor()
        return executor.execute(code)
```

---

## 3. Data Analysis Agent

```python
class DataAnalysisAgent:
    """Multi-turn data analysis agent."""
    
    def __init__(self, db_path: str):
        self.sql = SQLTool(db_path)
        self.python = PythonExecutor()
        self.chart = ChartTool()
        self.conversation: list[dict] = []
        self.schema_cache: dict | None = None
    
    def chat(self, user_message: str) -> str:
        """Process user message and return analysis."""
        self.conversation.append({"role": "user", "content": user_message})
        
        # Get schema on first call
        if not self.schema_cache:
            schema_result = self.sql.get_schema()
            self.schema_cache = schema_result.data
        
        # Agent decides and executes
        response = self._agent_loop(user_message)
        self.conversation.append({"role": "assistant", "content": response})
        return response
    
    def _agent_loop(self, task: str, max_steps: int = 5) -> str:
        """Agent decides which tools to use."""
        messages = [
            {"role": "system", "content": self._system_prompt()},
            *self.conversation[-10:],
        ]
        
        tools = [
            {"type": "function", "function": {
                "name": "sql_query", "description": "Execute a read-only SQL query",
                "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
            }},
            {"type": "function", "function": {
                "name": "python_execute", "description": "Execute Python code for data processing (pandas, numpy available)",
                "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]},
            }},
            {"type": "function", "function": {
                "name": "create_chart", "description": "Generate a chart (matplotlib). Include plt.figure() and data setup.",
                "parameters": {"type": "object", "properties": {
                    "code": {"type": "string", "description": "Matplotlib code"},
                    "filename": {"type": "string", "description": "Output filename"},
                }, "required": ["code", "filename"]},
            }},
        ]
        
        for step in range(max_steps):
            response = client.chat.completions.create(
                model="gpt-4o", messages=messages, tools=tools,
            )
            msg = response.choices[0].message
            
            if not msg.tool_calls:
                return msg.content
            
            messages.append(msg)
            
            for tc in msg.tool_calls:
                result = self._execute_tool(tc.function.name, json.loads(tc.function.arguments))
                messages.append({
                    "role": "tool", "tool_call_id": tc.id,
                    "content": result.data if result.success else f"Error: {result.error}",
                })
        
        return "Analysis complete. Let me know if you'd like to explore further."
    
    def _execute_tool(self, name: str, args: dict) -> ToolResult:
        if name == "sql_query":
            return self.sql.execute(args["query"])
        elif name == "python_execute":
            return self.python.execute(args["code"])
        elif name == "create_chart":
            return self.chart.generate(args["code"], args.get("filename", "chart.png"))
        return ToolResult(success=False, data=None, error=f"Unknown tool: {name}")
    
    def _system_prompt(self) -> str:
        schema_text = json.dumps(self.schema_cache, indent=2) if self.schema_cache else "No schema loaded"
        return f"""You are a data analysis assistant. You help users explore and understand their data.

Available database schema:
{schema_text}

Approach:
1. First understand the question
2. Query the database to get relevant data
3. Process/transform with Python if needed
4. Generate visualizations when helpful
5. Explain findings clearly

Always show your reasoning. When presenting numbers, provide context."""
```

---

## 4. Multi-Turn Exploration

```python
class ConversationalAnalyst:
    """Supports iterative data exploration across multiple turns."""
    
    def __init__(self, db_path: str):
        self.agent = DataAnalysisAgent(db_path)
        self.findings: list[str] = []  # Accumulate insights
        self.charts_generated: list[str] = []
    
    def explore(self, question: str) -> str:
        """User asks a question, agent explores and answers."""
        response = self.agent.chat(question)
        
        # Track findings
        if "insight" in response.lower() or "finding" in response.lower():
            self.findings.append(response[:200])
        
        return response
    
    def summarize_session(self) -> str:
        """Summarize all findings from the conversation."""
        if not self.findings:
            return "No findings recorded yet."
        
        summary_prompt = f"Summarize these data analysis findings into key insights:\n\n"
        summary_prompt += "\n---\n".join(self.findings)
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": summary_prompt}],
        )
        return response.choices[0].message.content
    
    def suggest_next_questions(self) -> list[str]:
        """Suggest follow-up questions based on conversation."""
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Based on the data analysis conversation, suggest 3 follow-up questions."},
                *self.agent.conversation[-6:],
            ],
        )
        return response.choices[0].message.content.split("\n")

# Usage example:
# analyst = ConversationalAnalyst("sales.db")
# print(analyst.explore("What are total sales by month for 2024?"))
# print(analyst.explore("Which product category grew fastest?"))
# print(analyst.explore("Create a chart showing the top 10 customers by revenue"))
# print(analyst.summarize_session())
```

---

## 5. MCP Integration

```python
# Model Context Protocol for structured tool access

class MCPDataServer:
    """MCP server exposing database tools."""
    
    def __init__(self, db_path: str):
        self.sql = SQLTool(db_path)
    
    def handle_request(self, method: str, params: dict) -> dict:
        """Handle MCP tool calls."""
        if method == "tools/list":
            return {"tools": [
                {"name": "query", "description": "Execute SQL query", 
                 "inputSchema": {"type": "object", "properties": {"sql": {"type": "string"}}}},
                {"name": "schema", "description": "Get database schema",
                 "inputSchema": {"type": "object", "properties": {}}},
                {"name": "sample", "description": "Get sample rows from a table",
                 "inputSchema": {"type": "object", "properties": {"table": {"type": "string"}, "n": {"type": "integer"}}}},
            ]}
        
        elif method == "tools/call":
            tool_name = params["name"]
            args = params.get("arguments", {})
            
            if tool_name == "query":
                result = self.sql.execute(args["sql"])
                return {"content": [{"type": "text", "text": json.dumps(result.data)}]}
            elif tool_name == "schema":
                result = self.sql.get_schema()
                return {"content": [{"type": "text", "text": json.dumps(result.data)}]}
            elif tool_name == "sample":
                result = self.sql.execute(f"SELECT * FROM {args['table']} LIMIT {args.get('n', 5)}")
                return {"content": [{"type": "text", "text": json.dumps(result.data)}]}
        
        return {"error": f"Unknown method: {method}"}
```

---

## 6. Running the Complete System

```python
def main():
    """Example: complete data analysis session."""
    import sqlite3
    
    # Create sample database
    conn = sqlite3.connect("/tmp/analysis/sales.db")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY, date TEXT, product TEXT,
            category TEXT, amount REAL, quantity INTEGER, region TEXT
        );
        INSERT OR IGNORE INTO sales VALUES
            (1, '2024-01-15', 'Widget A', 'Widgets', 29.99, 100, 'North'),
            (2, '2024-01-20', 'Gadget B', 'Gadgets', 49.99, 50, 'South'),
            (3, '2024-02-10', 'Widget A', 'Widgets', 29.99, 150, 'North'),
            (4, '2024-02-15', 'Gadget C', 'Gadgets', 79.99, 30, 'East'),
            (5, '2024-03-01', 'Widget B', 'Widgets', 39.99, 200, 'West');
    """)
    conn.close()
    
    # Run agent
    analyst = ConversationalAnalyst("/tmp/analysis/sales.db")
    
    questions = [
        "What tables are available and what do they contain?",
        "What are total sales by category?",
        "Show me monthly revenue trends",
        "Create a bar chart of sales by region",
    ]
    
    for q in questions:
        print(f"\n👤 {q}")
        print(f"🤖 {analyst.explore(q)}")
    
    print(f"\n📊 Session Summary:\n{analyst.summarize_session()}")

if __name__ == "__main__":
    main()
```

---

## Interview Questions

### Beginner
1. **Why use an agent for data analysis instead of fixed scripts?** Agents handle ad-hoc questions (no pre-built query needed). They can explore iteratively: ask follow-up questions, drill down, change approach based on results. Natural language interface means non-technical users can analyze data. Agent adapts to any schema.
2. **Why restrict SQL tools to SELECT only?** Agent-generated SQL could accidentally DROP tables, DELETE data, or UPDATE incorrectly. Read-only prevents data loss/corruption. Principle of least privilege. If writes needed: separate tool with approval gate. Production: use database user with read-only permissions.
3. **What's the benefit of multi-turn data exploration?** Single query rarely answers complex questions. Multi-turn: explore schema → understand data → query → refine → visualize. Each turn builds on previous findings. Agent maintains context. Like working with a data analyst who remembers the conversation.

### Intermediate
4. **How do you handle large query results?** LIMIT clauses (default 100 rows). Pagination for more. Summarize: "Query returned 10,000 rows. Top 5: ...". Aggregate: GROUP BY, COUNT rather than raw rows. Stream: process in chunks for Python analysis. Warning: alert user when results are truncated.
5. **How do you make data analysis agents safe?** Read-only DB access. Sandboxed Python execution (no network, limited filesystem). Timeout on all operations. Validate SQL before execution. No PII in responses (redact sensitive columns). Audit log of all queries. Rate limiting.
6. **How does MCP improve data agent architecture?** Standardized tool interface: any MCP client works. Separation of concerns: data server independent of agent. Multiple data sources: one MCP server per database/API. Security: MCP server handles auth. Composability: agent uses same protocol for SQL, APIs, files.

### Advanced
7. **Design a data analysis agent for enterprise (multi-tenant, multiple databases).** Routing: user's tenant → their databases. Permission: column-level access control. Connection pooling for multiple DBs. Schema caching (per tenant). Query cost estimation (block expensive queries). Audit: log all queries per user. PII: mask sensitive columns. Scale: queue queries, async execution.
8. **How do you handle agent errors in data analysis (wrong SQL, incorrect insights)?** Self-verification: agent checks results make sense (e.g., negative revenue → error). Explain reasoning: show query + logic so user can verify. Confidence signals: "I'm 90% sure" vs "This is approximate." Retry with different approach on error. Human-in-loop for important decisions.
9. **How would you evaluate a data analysis agent's quality?** Test cases: known questions with expected answers. Correctness: does the SQL return right results? Efficiency: query complexity, execution time. Communication: are explanations clear? Completeness: does it address all parts of the question? Robustness: handles ambiguous questions, missing data gracefully.

---

## Hands-On Exercise
1. Create a sample SQLite database with 3 tables and sample data
2. Implement SQLTool with schema inspection and read-only execution
3. Build PythonExecutor with pandas/matplotlib support
4. Create DataAnalysisAgent with tool-calling loop
5. Add multi-turn conversation (agent remembers context)
6. Generate 3 different charts based on the data
7. Implement session summarization (key findings from exploration)
