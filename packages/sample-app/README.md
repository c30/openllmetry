# sample-app

Sample applications demonstrating OpenLLMetry instrumentation with various AI frameworks and tools.

## Overview

This package contains example applications that showcase how to use OpenLLMetry (OpenTelemetry for LLM applications) with different AI frameworks, libraries, and protocols.

## Examples

### LangChain MCP Adapters Demo

**File:** `sample_app/langchain_mcp_adapters_demo.py`

Demonstrates integration of LangChain with Model Context Protocol (MCP) servers using the `langchain-mcp-adapters` package, with full OpenTelemetry tracing support.

**Features:**
- Connects to MCP servers (e.g., Google Maps MCP server)
- Creates LangChain tools from MCP server capabilities
- Uses LangChain agents to interact with MCP tools
- Automatically traces all interactions via:
  - `opentelemetry-instrumentation-langchain` - Traces LangChain operations
  - `opentelemetry-instrumentation-mcp` - Traces MCP protocol calls

**Requirements:**
- OpenAI API key (set `OPENAI_API_KEY` environment variable)
- Node.js and npx (for running MCP server)

**Usage:**
```bash
python sample_app/langchain_mcp_adapters_demo.py
```

**What it does:**
1. Initializes Traceloop SDK for OpenTelemetry instrumentation
2. Connects to a Google Maps MCP server using langchain-mcp-adapters
3. Creates a LangChain agent with tools from the MCP server
4. Executes example queries through the agent
5. All operations are automatically traced and can be sent to an OpenTelemetry collector

## Installation

Install dependencies using Poetry:

```bash
poetry install
```

## Running Examples

Set up your environment variables in a `.env` file:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

Then run any example:

```bash
poetry run python sample_app/langchain_mcp_adapters_demo.py
```

## OpenTelemetry Configuration

All examples initialize Traceloop SDK which automatically:
- Instruments supported frameworks (LangChain, MCP, OpenAI, etc.)
- Sets up OpenTelemetry tracing
- Exports traces to configured backends

Configure the OpenTelemetry endpoint via environment variables:

```bash
export TRACELOOP_API_KEY=your_api_key
# or use a custom OTLP endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
```
