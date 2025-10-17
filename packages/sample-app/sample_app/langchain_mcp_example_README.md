# LangChain MCP Integration Demo with OpenTelemetry

This demo showcases how to integrate LangChain with Model Context Protocol (MCP) servers while leveraging OpenTelemetry instrumentation for comprehensive observability.

## Overview

The demo demonstrates:

- **LangChain + MCP Integration**: Use `langchain-mcp` to connect LangChain agents to MCP servers
- **OpenTelemetry Tracing**: Automatic instrumentation of MCP operations via `opentelemetry-instrumentation-mcp`
- **Tool Calling**: LangChain agents using MCP tools (filesystem operations in this example)
- **End-to-End Observability**: Complete trace of requests from user query through agent reasoning to MCP tool execution

## Architecture

```
User Query
    ↓
LangChain Agent (with OpenAI)
    ↓
MCPToolkit → MCP Client Session
    ↓
MCP Server (Filesystem Server)
    ↓
[All operations traced by OpenTelemetry]
```

## Prerequisites

1. **Python 3.10+**
2. **OpenAI API Key**: Set as environment variable
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```
3. **Node.js/npx**: Required to run MCP servers (for the filesystem server)

## Installation

From the `sample-app` directory:

```bash
poetry install
```

This will install:
- `langchain-mcp`: LangChain integration for MCP
- `opentelemetry-instrumentation-mcp`: OpenTelemetry instrumentation
- `traceloop-sdk`: Traceloop SDK for easy OpenTelemetry setup
- All other required dependencies

## Usage

### Demo Mode (Default)

Runs a series of predefined queries:

```bash
cd /home/runner/work/openllmetry/openllmetry/packages/sample-app
poetry run python sample_app/langchain_mcp_example.py
```

### Interactive Mode

Enter your own queries interactively:

```bash
poetry run python sample_app/langchain_mcp_example.py --interactive
```

Type your questions and press Enter. Type 'quit' or 'exit' to stop.

## How It Works

### 1. OpenTelemetry Initialization

The demo initializes Traceloop SDK which automatically configures OpenTelemetry:

```python
from traceloop.sdk import Traceloop

Traceloop.init(app_name="langchain_mcp_demo")
```

This automatically:
- Instruments MCP operations (via `opentelemetry-instrumentation-mcp`)
- Instruments LangChain operations
- Instruments OpenAI API calls
- Collects and exports traces

### 2. MCP Server Connection

Connects to an MCP server using stdio transport:

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@modelcontextprotocol/server-filesystem", os.getcwd()]
)
stdio_transport = await stdio_client(server_params)
session = ClientSession(read_stream, write_stream)
await session.initialize()
```

### 3. LangChain Agent Setup

Creates a LangChain agent with MCP tools:

```python
from langchain_mcp import MCPToolkit

toolkit = MCPToolkit(session=session)
await toolkit.initialize()
tools = toolkit.get_tools()

agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)
```

### 4. Query Processing

Process queries with automatic tracing:

```python
@workflow(name="process_query_with_mcp")
async def process_query(self, query: str) -> str:
    result = await self.agent_executor.ainvoke({"input": query})
    return result["output"]
```

## Traces and Metrics

When you run the demo, OpenTelemetry will collect:

- **MCP Operations**: Tool calls, server requests/responses
- **LangChain Execution**: Agent reasoning, tool selection
- **LLM Calls**: OpenAI API requests and responses
- **Complete Flow**: End-to-end request traces

### Viewing Traces

Traces are exported to your configured OpenTelemetry backend. By default, Traceloop SDK may export to:
- Console (for debugging)
- Traceloop cloud (if configured)
- Any OTLP-compatible backend (Jaeger, Tempo, etc.)

Configure the export endpoint:
```bash
export TRACELOOP_BASE_URL=<your-traceloop-url>
# or
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```

## Example Queries

The demo includes these example queries:

1. "List all files in the current directory"
2. "What is the content of README.md file?"
3. "Tell me about the LICENSE file in this directory"

You can modify these or use interactive mode to test your own queries.

## Trace Hierarchy

A typical trace will show:

```
process_query_with_mcp (workflow)
├── AgentExecutor
│   ├── OpenAI Chat Completion
│   ├── MCP Tool Call: read_file
│   │   └── MCP Server Request/Response
│   └── OpenAI Chat Completion (final response)
```

## MCP Servers

This demo uses the official MCP filesystem server, but you can connect to any MCP server:

```python
await demo.connect_to_mcp_server(
    server_command="npx",
    server_args=["-y", "@modelcontextprotocol/server-<name>", ...args]
)
```

Available MCP servers include:
- `@modelcontextprotocol/server-filesystem`: File system operations
- `@modelcontextprotocol/server-postgres`: PostgreSQL database
- `@modelcontextprotocol/server-slack`: Slack integration
- `@modelcontextprotocol/server-google-maps`: Google Maps API
- Many more on npm

## Troubleshooting

### Missing OpenAI API Key
```
Error: OPENAI_API_KEY environment variable is required
```
Solution: Set your OpenAI API key as shown in Prerequisites

### npx not found
```
Error: npx command not found
```
Solution: Install Node.js which includes npx

### Connection to MCP Server Failed
- Check that npx can run the MCP server
- Verify the server package name is correct
- Check for port conflicts if using SSE/HTTP transport

## Key Files

- `langchain_mcp_example.py`: Main demo implementation
- `pyproject.toml`: Dependencies including `langchain-mcp` and `opentelemetry-instrumentation-mcp`

## Learn More

- [LangChain MCP Documentation](https://github.com/rectalogic/langchain-mcp)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [OpenLLMetry Documentation](https://traceloop.com/docs/openllmetry/introduction)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
